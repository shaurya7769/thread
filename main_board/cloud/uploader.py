import requests
import threading
import os
import glob
import socket
import csv
import json

def is_reachable(host, port, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

def upload_latest_csv(endpoint="https://rail-inspect-api.onrender.com/api/survey"):
    """
    Finds the most recent CSV, converts it to JSON, and sends it to Render.
    Run this in a separate thread.
    """
    def _run():
        try:
            # 1. Parse host and port for connectivity check
            url_part = endpoint.split("//")[1]
            host = url_part.split("/")[0]
            port = 443 if endpoint.startswith("https") else 80
            if ":" in host:
                host, port_str = host.split(":")
                port = int(port_str)
            
            if not is_reachable(host, port):
                print(f"[CLOUD] Render host {host} unreachable. Skipping JSON sync.")
                return

            # 2. Find the latest CSV
            survey_dir = os.path.expanduser("~/surveys")
            csv_files = glob.glob(os.path.join(survey_dir, "*.csv"))
            if not csv_files:
                print("[CLOUD] No survey data found to sync.")
                return

            latest_file = max(csv_files, key=os.path.getctime)
            print(f"[CLOUD] Converting {os.path.basename(latest_file)} to JSON...")

            # 3. Convert CSV to JSON
            payload = {
                "filename": os.path.basename(latest_file),
                "data": []
            }
            with open(latest_file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Optional: Convert types if needed, but DictReader provides strings
                    payload["data"].append(row)

            # 4. Synchronous background POST
            print(f"[CLOUD] Syncing with Render: {endpoint}...")
            response = requests.post(endpoint, json=payload, timeout=20)
            
            if response.status_code in [200, 201]:
                print("[CLOUD] Render JSON Sync Successful.")
            else:
                print(f"[CLOUD] Sync Failed. Status: {response.status_code}")
                
        except Exception as e:
            print(f"[CLOUD] Sync Interrupted: {e}")

    thread = threading.Thread(target=_run, daemon=False)
    thread.start()
    return thread
