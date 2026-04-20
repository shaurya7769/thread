import requests
import threading
import os
import glob

def upload_latest_csv(endpoint="http://10.18.31.129:5000/api/savetfd"):
    """
    Finds the most recent CSV in the surveys folder and uploads it.
    Run this in a separate thread.
    """
    def _run():
        try:
            # Find the latest CSV (assuming standard naming convention)
            survey_dir = os.path.expanduser("~/surveys")
            csv_files = glob.glob(os.path.join(survey_dir, "*.csv"))
            if not csv_files:
                print("[CLOUD] No CSV files found to upload.")
                return

            latest_file = max(csv_files, key=os.path.getctime)
            print(f"[CLOUD] Uploading {os.path.basename(latest_file)} to {endpoint}...")

            with open(latest_file, 'rb') as f:
                files = {'file': f}
                response = requests.post(endpoint, files=files, timeout=15)
                
                if response.status_code == 200:
                    print("[CLOUD] Upload Successful.")
                else:
                    print(f"[CLOUD] Upload Failed. Status: {response.status_code}")
        except Exception as e:
            print(f"[CLOUD] Error during upload: {e}")

    thread = threading.Thread(target=_run, daemon=False)
    thread.start()
    return thread
