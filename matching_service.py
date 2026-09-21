import datetime
import json
import os
import math
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

SERVICE = "matching-service"
Port = 9000

Log_Dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(Log_Dir, exist_ok=True)

def log(service_name, message):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    line = f"[{ts}] [{service_name}] {message}"
    print(line, flush=True)
    with open(os.path.join(Log_Dir, f"{service_name}.log"), "a") as f:
        f.write(line + "\n")

drivers = {} #driver_id: host, port, lat, lon, available

def distance(lat1, lon1, lat2, lon2):
    return math.dist((lat1,lon1), (lat2, lon2))

def push_assignment(driver, rider_id, ride_id):
    url = f"http://{driver['host']}:{driver['port']}/assign"
    payload = json.dumps({"ride_id": ride_id, "rider_id": rider_id}).encode()
    req = urllib.request.Request(url, data=payload, method="POST", headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read())
    except Exception as e:
        log(SERVICE, f"WARN could not reach driver for assignment: {e}")
        return None

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length) or b"{}")

    def _respond(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path == "/driver/register":
            data = self._read_json()
            drivers[data["driver_id"]] = {
                "host": data["host"], "port": data ["port"],
                "lat": data["lat"], "lon": data["lon"], "available": True,}
            log(SERVICE, f"driver registered: {data['driver_id']} at" f"({data['lat']}, {data['lon']})")
            self._respond(200, {"status": "registered"})

        elif self.path == "/driver/location":
            data = self._read_json()
            d = drivers.get(data["driver_id"])
            if d:
                d["lat"], d["lon"] = data["lat"], data["lon"]
                log(SERVICE, f"location update from {data['driver_id']}: " f"({data['lat']}, {data['lon']})")
                self._respond(200, {"status": "unknown driver"})
            else:
                self._respond(404, {"status": "unknown driver"})   

        elif self.path == "/ride/request":
            data = self._read_json()
            rider_id, lat, lon = data["rider_id"], data["lat"], data["lon"]
            log(SERVICE, f"ride request from {rider_id} at ({lat}, {lon})")

            candidates = [(did, d) for did, d in drivers.items() if d["available"]]
            if not candidates:
                log(SERVICE, f"no available drivers for {rider_id}")
                self._respond(503, {"status": "no_drivers_available"})
                return

            best_id, best = min(candidates, key=lambda kv: distance(lat, lon, kv[1]["lat"], kv[1]["lon"]))
            best["available"] = False
            ride_id = f"ride-{rider_id}-{best_id}"

            log(SERVICE, f"matched {rider_id} -> {best_id} (ride_id={ride_id}); " f"pushing assignment")
            ack = push_assignment(best, rider_id, ride_id)

            if ack is None:
                best["available"] = True # roll back on failed link
                log(SERVICE, f"assignment push failed, driver freed again")
                self._respond(502, {"status": "driver_unreachable"})
            else:
                log(SERVICE, f"driver {best_id} acknowledged ride {ride_id}")
                self._respond(200, {"status": "matched", "ride_id": ride_id, "driver_id": best_id,})

if __name__ == "__main__":
    log(SERVICE, f"starting on port {Port}")
    HTTPServer(("0.0.0.0", Port), Handler).serve_forever()
