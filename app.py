from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Basic landing page to verify the service is alive
@app.route('/')
def index():
    return "Rail Inspection Cloud Backend - ACTIVE"

# The endpoint where the BeagleBone sends JSON data
@app.route('/api/survey', methods=['POST'])
def receive_survey():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No JSON payload"}), 400
            
        filename = data.get('filename', 'unknown_survey.json')
        payload = data.get('data', [])
        
        print(f"[CLOUD] Received survey: {filename} ({len(payload)} rows)")
        
        # In a production environment, you would save this to a database or cloud storage (S3/MongoDB)
        # For now, we confirm receipt successfully.
        return jsonify({
            "status": "success", 
            "received_file": filename,
            "row_count": len(payload)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Logic Failure: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

# Health check for Render monitoring
@app.route('/healthz')
def health():
    return "OK", 200

if __name__ == "__main__":
    # Use environment port for Render compatibility
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
