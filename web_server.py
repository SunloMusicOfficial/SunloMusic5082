from flask import Flask, request, jsonify, render_template_string
import asyncio
from database.cookies import add_cookie, get_all_cookies, delete_cookie, json_to_netscape
import json

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Sunlo Cookies Dashboard</title>
    <style>
        body { background: #0f172a; color: #e2e8f0; font-family: Arial; padding: 30px; }
        .card { background: #1e293b; padding: 25px; border-radius: 12px; max-width: 600px; margin: auto; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; text-align: center; }
        input, button { width: 100%; padding: 12px; margin-top: 10px; border-radius: 6px; border: none; font-size: 16px; }
        input { background: #0f172a; color: white; border: 1px solid #334155; }
        button { background: #10b981; color: white; font-weight: bold; cursor: pointer; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #334155; }
        .green { color: #10b981; } .red { color: #ef4444; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🍪 Sunlo Cookie Manager</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="text" name="name" placeholder="Account Name (e.g., acc1)" required>
            <input type="file" name="file" accept=".txt,.json" required>
            <button type="submit">Upload & Encrypt</button>
        </form>
        <table>
            <tr><th>Account</th><th>Status</th><th>Success</th><th>Fails</th></tr>
            {% for c in cookies %}
            <tr>
                <td>{{ c.name }}</td>
                <td class="{{ 'green' if c.status == 'active' else 'red' }}">{{ c.status.capitalize() }}</td>
                <td>{{ c.success }}</td>
                <td>{{ c.fails }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return "Bot is online!"

@app.route('/cookies', methods=['GET', 'POST'])
def cookies_ui():
    if request.method == 'POST':
        # Handle file upload
        name = request.form.get('name')
        file = request.files.get('file')
        if file and name:
            content = file.read().decode('utf-8')
            if file.filename.endswith('.json'):
                try:
                    json_data = json.loads(content)
                    content = json_to_netscape(json_data)
                except: pass
            asyncio.run(add_cookie(name, content))
    
    # Show dashboard
    cookies = asyncio.run(get_all_cookies())
    return render_template_string(HTML, cookies=cookies)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
