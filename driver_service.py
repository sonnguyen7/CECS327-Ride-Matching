import datetime
import json
import os
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

Matching_Host = "localhost"
Matching_Port = 9000

Log_Dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(Log_Dir, exist_ok=True)


def log(service_name, message):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    line = f"[{ts}] [{service_name}] {message}"
    print(line, flush=True)
    with open(os.path.join(Log_Dir, f"{service_name}.log"), "a") as f:
        f.write(line + "\n")

def post(path, payload):
    url = f"http://{Matching_Host}:{Matching_Port}{path}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=3) as resp:
        return json.loads(resp.read())

def make_handler(service_name, driver_id):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def do_POST(self):
            if self.path == "/assign":
                length = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(length))
                log(service_name, f"ASSIGNED ride {data['ride_id']} "f"for rider {data['rider_id']}")
                body = json.dumps({"status": "accepted"}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()
    return Handler

if __name__ == "__main__":
    driver_id = sys.argv[1] if len (sys.argv) > 1 else "D1"
    my_port = int(sys.argv[2]) if len(sys.argv) > 2 else 9101
    lat = float(sys.argv[3]) if len(sys.argv) > 3 else 37.77
    lon = float(sys.argv[4]) if len(sys.argv) > 4 else -122.41

    service_name = f"driver-{driver_id}"
    log(service_name, f"registering with matching service at {Matching_Host}:{Matching_Port}")

    post("/driver/register", {"driver_id": driver_id, "host": "localhost", "port": my_port, "lat": lat, "lon": lon,})

    log(service_name, f"registered, now listening for assignments on port {my_port}")

    HTTPServer(("0.0.0.0", my_port), make_handler(service_name, driver_id)).serve_forever()