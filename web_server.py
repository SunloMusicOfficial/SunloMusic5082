from flask import Flask, jsonify
import time

app = Flask(__name__)
START_TIME = time.time()

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "bot": "Sunlo Music",
        "uptime": int(time.time() - START_TIME)
    })

@app.route('/api/stats')
def api_stats():
    return jsonify({"status": "online"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
