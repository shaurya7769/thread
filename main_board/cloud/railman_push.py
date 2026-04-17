import requests
import json
import threading
import queue
import time

class CloudPusher(threading.Thread):
    def __init__(self, api_url="http://api.rail-inspect.com/v1/push"):
        super().__init__(daemon=True)
        self.api_url = api_url
        self.data_queue = queue.Queue(maxsize=1000)
        self.running = True

    def push_data(self, data):
        try:
            self.data_queue.put_nowait(data)
        except queue.Full:
            pass

    def run(self):
        print(f"[CLOUD] Pusher started, destination: {self.api_url}")
        batch = []
        while self.running:
            try:
                # Collect data for 5 seconds or until batch is 50 items
                while len(batch) < 50:
                    try:
                        item = self.data_queue.get(timeout=5)
                        batch.append(item)
                    except queue.Empty:
                        break
                
                if batch:
                    # Mimicking the project post structure
                    payload = {
                        "device_id": "BBB_RAIL_01",
                        "timestamp": int(time.time()),
                        "data": batch
                    }
                    # SIMULATED POST
                    # r = requests.post(self.api_url, json=payload, timeout=2)
                    # print(f"[CLOUD] Pushed {len(batch)} items. Status: {r.status_code}")
                    print(f"[CLOUD] (Sim) Pushed {len(batch)} data points to {self.api_url}")
                    batch = []
                    
            except Exception as e:
                print(f"[CLOUD] Error: {e}")
                time.sleep(5)

    def stop(self):
        self.running = False
