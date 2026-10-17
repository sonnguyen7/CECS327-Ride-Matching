# CECS 327 - Distributed Ride-Matching System  
**1. Required Software**   
  * Python 3.14+  
  * Visual Studio Code (or any code editor)  

**2. Dependencies**   
  * None (Standard Library Only): This project relies solely on built-in Python modules (such as http.server, urllib, json, socket, and threading). No external pip installations are required.  

**3. How to Start Each Service:** Open separate terminal windows and execute the commands in the following order:  
  * **Terminal 1: Event Broker (TCP Socket Server on Port 9200)**  
      * `python3 event_broker.py`  
  * **Terminal 2: Matching Service & Web Console (Port 9000)**  
      * `python3 matching_service.py`   
  * **Terminal 3: Audit Subscriber (Pub-Sub Node)**  
      * `python3 subscriber.py audit`  
  * **Terminal 4: Monitor Subscriber (Pub-Sub Node)**  
      * `python3 subscriber.py monitor`  
  * **Terminal 5-8: Driver Services (Ports 9101-9104, Group: `drivers.local`)**  
      * Terminal 5: `python3 driver_service.py D1 9101 37.770 -122.410 drivers.local`  
      * Terminal 6: `python3 driver_service.py D2 9102 37.790 -122.420 drivers.local`  
      * Terminal 7: `python3 driver_service.py D3 9103 37.760 -122.400 drivers.local`  
      * Terminal 8: `python3 driver_service.py D4 9104 37.780 -122.430 drivers.local`  
  * **Terminal 9: Interactive Runner (Marshalling & Group Client)**  
      * Used for running demo scripts on demand.

**4. Demo: (seen in the demo video)**  
* **Step 1:** Start services in Terminals 1-8 as shown above. Open your web browser to `http://localhost:9000/`.  
* **Step 2 (Marshalling):** In Terminal 9, run `python3 demo_marshall.py` to display the native Python dictionary before marshalling, the raw UTF-8 JSON bytes sent over the wire, and the unmarshalled object. 
* **Step 3 (Request-Reply & Dynamic Matching):** From the web UI at `http://localhost:9000`, submit requests for 4 riders at coordinates (37.7749, -122.4194):  
      * John matches Driver D1 (`ride-John-D1`).  
      * Click Retry Same (Duplicate) to demonstrate idempotency caching without re-booking.  
      * Elizabeth matches Driver D4 (`ride-Elizabeth-D4`).  
      * Kevin matches Driver D2 (`ride-Kevin-D2`).
      * Emma matches Driver D3 (`ride-Emma-D3`).
* **Step 4 (Publish-Subscribe Notification):** Check Terminals 3 and 4 (`subscriber.py audit` and `subscriber.py monitor`). Both display all 4 `ride.assigned` event envelopes with message IDs and timestamps.
* **Step 5 (Group Communication):** In terminal 9, run: `python3 group_client.py drivers.local "High demand in your area"`. All four driver terminals receive and log the broadcast notice simultaneously.  

**5. Test cases**  
  * **Test Case 1 (Nearest Driver Matching):** Run all 4 drivers on ports 9101-9104. Request rider John at (37.7749, -122.4194). Expected output: D1 is closest and assigned (`ride-John-D1`), updating D1 to busy.  
  * **Test Case 2 (Duplicate / Idempotency Handling):** Resend John's request with the same `request_id`. Expected output: `matching_service.py` returns the cached response, logs `IDEMPOTENCY: duplicate request`, and does not publish a duplicate event to the broker.  
  * **Test Case 3 (All Drivers Busy / Pool Exhaustion):** Book all four drivers (John -> D1, Elizabeth -> D4, Kevin -> D2, Emma -> D3). After, submit a 5th request. Expected output: The matching service returns HTTP 503 `no_drivers_available` without crashing. 
  * **Test Case 4 (Group Multicast):** Run `python3 group_client.py drivers.local "High demand in your area"`. Expected output: All 4 active driver group logs record the message at the exact same timestamp.  
    

