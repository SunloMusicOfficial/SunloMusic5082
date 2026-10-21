from flask import Flask, jsonify, render_template_string
import psutil, time, asyncio
from database.users import get_total_users
import core.calls as calls_module

app = Flask(__name__)
START_TIME = time.time()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sunlo Music - Dashboard</title>
    <style>
        body { background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 40px; display: flex; flex-direction: column; align-items: center; }
        .container { background: #1e293b; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); width: 100%; max-width: 600px; text-align: center; }
        h1 { color: #38bdf8; margin-bottom: 5px; }
        p.subtitle { color: #94a3b8; margin-top: 0; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #334155; }
        .card h3 { margin: 0; color: #94a3b8; font-size: 14px; text-transform: uppercase; }
        .card p { margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: #10b981; }
        .status-online { color: #10b981; display: inline-block; width: 10px; height: 10px; background: #10b981; border-radius: 50%; margin-right: 8px; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); } 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); } }
        .footer { margin-top: 30px; color: #64748b; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Sunlo Music</h1>
        <p class="subtitle">Premium Bot Dashboard</p>
        
        <div class="grid">
            <div class="card">
                <h3>Status</h3>
                <p><span class="status-online"></span>Online</p>
            </div>
            <div class="card">
                <h3>Total Users</h3>
                <p>{{ users }}</p>
            </div>
            <div class="card">
                <h3>Active VCs</h3>
                <p>{{ vcs }}</p>
            </div>
            <div class="card">
                <h3>CPU Usage</h3>
                <p>{{ cpu }}%</p>
            </div>
            <div class="card">
                <h3>RAM Usage</h3>
                <p>{{ ram }}%</p>
            </div>
            <div class="card">
                <h3>Uptime</h3>
                <p>{{ uptime }}</p>
            </div>
        </div>
        <div class="footer">© 2024 SunloMusicOfficial</div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    try:
        users = asyncio.run(get_total_users())
        active_vcs = len(asyncio.run(calls_module.calls.calls)) if calls_module.calls else 0
    except:
        users, active_vcs = 0, 0
        
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    uptime_sec = int(time.time() - START_TIME)
    uptime_str = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime_sec))
    
    return render_template_string(HTML_TEMPLATE, users=users, vcs=active_vcs, cpu=cpu, ram=ram, uptime=uptime_str)

@app.route('/api/stats')
def api_stats():
    try:
        users = asyncio.run(get_total_users())
    except:
        users = 0
    return jsonify({"status": "online", "total_users": users})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
