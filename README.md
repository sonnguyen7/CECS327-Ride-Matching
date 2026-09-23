# CECS 327 - Distributed Ride-Matching System  
**1. Required Software**  
  * Python 3.14+  
  * Visual Studio Code (or any code editor)

**2. Dependencies**
  * None (Standard Library Only): This project relies solely on built-in Python modules (such as http.server, urllib, json, socket, and threading). No external pip installations are required.

**3. How to Start Each Service:** Open three separate terminal windows and execute the commands in the following order:  
  * **Terminal 1: Matching Service (Coordinator)**
    * Start the central matching engine first so it can begin listening for incoming registrations and ride requests:
      * `python3 matching_service.py`  
  * **Terminal 2: Driver Service (Driver Node)**  
    * Launch the driver application. This process automatically registers with the Matching Service and begins listening for incoming ride assignments:  
      * `python3 driver_service.py`  
  * **Terminal 3: Rider Client**
    * Run the client script to simulate a rider requesting a pickup:
      * `python3 rider_client.py`  

**4. Demo:**  
  * Run in this order, and each in different terminals:  
    * `python3 matching_service.py`  
    * `python3 driver_service.py <driver_id> <port> <latitude> <longitude>`  
    * `python3 rider_client.py <rider_id> <latitude> <longitude>`  
  * Example:  
    * `python3 matching_service.py`  
    * `python3 driver_service.py D1 9101 37.77 -122.41`  
    * `python3 rider_client.py R1 37.775 -122.415`  
  * The output:  
    * The driver-D1.log should look like this:  
```text
[2026-09-13 19:30:19.485] [driver-D1] registering with matching service at localhost:9000  
[2026-09-13 19:30:21.601] [driver-D1] registered, now listening for assignments on port 9101  
[2026-09-13 19:30:29.792] [driver-D1] ASSIGNED ride ride-R1-D1 for rider R1  
```
> **Note:** Complete runtime logs for all 3 active services are located in the logs directory.  

**5. Test cases**  
  * **Select** the nearest driver to the client:  
    * Set up:  
      * Terminal 1: `python3 matching_service.py`  
      * Terminal 2 (closer driver): `python3 driver_service.py D1 9101 37.77 -122.41`  
      * Terminal 3 (further driver): `python3 driver_service.py D2 9102 37.90 -122.60`  
    * Action:  
      * Terminal 4 (Rider near D1): `python3 rider_client.py R1 37.775 -122.415`  
    * Expected output:  
      * The rider (R1) is matched with D1, and D1 receives the assignment on port 9101 (also marked unavailable).  
  * **Driver** availability locking to avoid double booking  
    * Set up:  
      * Keep the current state from test case 1 where D1 is already booked (available: False)  
    * Action:  
      * Terminal 4 (New rider): `python3 rider_client.py R2 37.775 -122.415`  
    * Expected output:  
      * Although D1 is closer to the new driver, the service matches D2 to R2, as it is the only remaining available driver.  
  * **No** driver available (Error Handling):  
    * Set up:  
      * Start `python3 matching_service.py`, but this time, with no active `driver_service.py` instances running.  
    * Action:  
      * `python3 rider_client.py R3 37.775 -122.415`  
    * Expected output:  
      * The rider client logs the failure without crashing, and the matching service lets the user know that there are no available drivers.  

