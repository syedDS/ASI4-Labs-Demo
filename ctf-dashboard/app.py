"""
ASI04 Lab - CTF Dashboard
Track progress and view captured flags
"""

from flask import Flask, jsonify, render_template_string
import os
import json
import requests

app = Flask(__name__)

ATTACKER_SERVER = os.getenv("ATTACKER_SERVER", "http://attacker-server:8666")

# Challenge definitions — Labs 1, 2, 3, 5 (pre + post mitigation)
CHALLENGES = {
    "ASI04-01": {
        "name": "Typosquatting",
        "points": 100,
        "description": "Install a typosquatted package and trigger exfiltration",
        "flag": "ASI04_FLAG{typ0squ4t_g0t_y0u}",
        "mitigation": "Guardrail: Package Name Similarity Check",
        "hints": [
            "Look at the fake PyPI server packages",
            "Compare package names to legitimate ones",
            "langchaln vs langchain"
        ]
    },
    "ASI04-02": {
        "name": "Malicious MCP Server",
        "points": 250,
        "description": "Identify and exploit the malicious MCP server",
        "flag": "ASI04_FLAG{mcp_tr0j4n_d3t3ct3d}",
        "mitigation": "Guardrail: MCP Tool Source Validation",
        "hints": [
            "Examine MCP tool responses",
            "Look for hidden exfiltration endpoints",
            "Enable the guardrail toggle to see the mitigation block the attack"
        ]
    },
    "ASI04-03": {
        "name": "Dependency Confusion",
        "points": 250,
        "description": "Exploit dependency confusion with high-version packages",
        "flag": "ASI04_FLAG{d3p_c0nfus10n_pwn3d}",
        "mitigation": "Guardrail: Package Registry Allowlist",
        "hints": [
            "Internal packages have low versions",
            "Public PyPI might have higher versions",
            "Enable the guardrail toggle to block unapproved registry installs"
        ]
    },
    "ASI04-05": {
        "name": "RAG Poisoning — Poison the Brain",
        "points": 500,
        "description": "Upload a poisoned document and trigger hidden instruction retrieval",
        "flag": "ASI04_FLAG{r4g_p01s0n3d}",
        "mitigation": "Guardrail: RAG Instruction Injection Filter (input + output rails)",
        "hints": [
            "Upload a document containing RUN_MAINTENANCE",
            "Ask the agent about system health/status",
            "Enable the guardrail toggle to see it sanitise the injected context"
        ]
    }
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ASI04 CTF Dashboard</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
            color: #00ff00;
            margin: 0;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 {
            color: #ff0000;
            text-align: center;
            text-shadow: 0 0 10px #ff0000;
        }
        .scoreboard {
            background: #111;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .score-row {
            display: flex;
            justify-content: space-around;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        .score-block { text-align: center; }
        .score-label {
            font-size: 14px;
            color: #888;
            margin-bottom: 5px;
        }
        .total-score {
            font-size: 48px;
            text-align: center;
            color: #00ff00;
            text-shadow: 0 0 20px #00ff00;
        }
        .challenges {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        .challenge {
            background: #111;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s;
        }
        .challenge:hover {
            border-color: #00ff00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
        }
        .challenge.solved {
            border-color: #00ff00;
            background: rgba(0, 255, 0, 0.1);
        }
        .challenge h3 {
            margin-top: 0;
            color: #ff6600;
        }
        .points {
            float: right;
            background: #222;
            padding: 5px 15px;
            border-radius: 5px;
            color: #ffff00;
        }
        .solved .points {
            background: #00ff00;
            color: #000;
        }
        .mitigation {
            font-size: 12px;
            color: #00bfff;
            margin-top: 6px;
            padding: 6px 10px;
            background: #001a2a;
            border-left: 3px solid #00bfff;
            border-radius: 3px;
        }
        .hints {
            font-size: 12px;
            color: #666;
            margin-top: 10px;
            padding: 10px;
            background: #0a0a0a;
            border-radius: 5px;
        }
        .flag {
            background: #000;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            border-left: 3px solid #00ff00;
            margin-top: 10px;
            word-break: break-all;
        }
        .status {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 3px;
            font-size: 12px;
        }
        .status.captured { background: #00ff00; color: #000; }
        .status.pending { background: #666; }
        .refresh-btn {
            background: #00ff00;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-family: monospace;
            font-weight: bold;
        }
        .refresh-btn:hover { background: #00cc00; }
        .header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .section-header {
            color: #ff6600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 1px solid #333;
        }
        .links-bar {
            text-align: center;
            padding: 10px;
            background: #111;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .links-bar a { color: #00ff88; margin: 0 10px; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ASI04 SUPPLY CHAIN CTF</h1>

        <div class="scoreboard">
            <div class="header-row">
                <h2>Scoreboard</h2>
                <button class="refresh-btn" onclick="loadProgress()">Refresh</button>
            </div>
            <div class="score-row">
                <div class="score-block">
                    <div class="score-label">Score</div>
                    <div class="total-score" id="core-score">0 / 1100</div>
                </div>
            </div>
        </div>

        <div class="links-bar">
            <a href="http://localhost:5050" target="_blank">Vulnerable Agent :5050</a>
            <a href="http://localhost:8666/dashboard" target="_blank">Attacker Dashboard :8666</a>
        </div>

        <div class="section-header">Supply Chain Attack Labs — 1100 pts (Labs 1, 2, 3, 5)</div>
        <div class="challenges" id="core-challenges">
            Loading challenges...
        </div>
    </div>

    <script>
        const challenges = ''' + json.dumps(CHALLENGES) + ''';

        function renderChallenges(containerId, challengeData, solvedData) {
            let html = '';
            for (const [id, challenge] of Object.entries(challengeData)) {
                const solved = solvedData[id] || false;
                html += `
                    <div class="challenge ${solved ? 'solved' : ''}">
                        <span class="points">${challenge.points} pts</span>
                        <h3>${id}: ${challenge.name}</h3>
                        <p>${challenge.description}</p>
                        <p>
                            <span class="status ${solved ? 'captured' : 'pending'}">
                                ${solved ? 'CAPTURED' : 'PENDING'}
                            </span>
                        </p>
                        ${solved ? `<div class="flag">${challenge.flag}</div>` : ''}
                        <div class="mitigation">🛡️ Mitigation: ${challenge.mitigation}</div>
                        <div class="hints">
                            <strong>Hints:</strong>
                            <ul>
                                ${challenge.hints.map(h => `<li>${h}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                `;
            }
            document.getElementById(containerId).innerHTML = html;
        }

        async function loadProgress() {
            try {
                const resp = await fetch('/api/progress');
                const data = await resp.json();

                let score = 0, max = 0;
                for (const [id, challenge] of Object.entries(challenges)) {
                    max += challenge.points;
                    if (data.solved[id]) score += challenge.points;
                }

                renderChallenges('core-challenges', challenges, data.solved);
                document.getElementById('core-score').textContent = `${score} / ${max}`;

            } catch (e) {
                console.error('Failed to load progress:', e);
            }
        }

        loadProgress();
        setInterval(loadProgress, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/progress')
def get_progress():
    """Check which flags have been captured"""
    try:
        response = requests.get(f"{ATTACKER_SERVER}/api/log", timeout=5)
        if response.status_code == 200:
            data = response.json()
            entries = data.get("entries", [])

            # Convert to string for searching
            all_data = str(entries)

            solved = {
                id: CHALLENGES[id]["flag"] in all_data
                for id in CHALLENGES
            }

            return jsonify({
                "solved": solved,
                "total_entries": len(entries)
            })
    except Exception as e:
        print(f"Error checking progress: {e}")

    return jsonify({
        "solved": {k: False for k in CHALLENGES},
        "total_entries": 0
    })

@app.route('/api/challenges')
def get_challenges():
    return jsonify(CHALLENGES)

if __name__ == '__main__':
    print("""
    ======================================================
         ASI04 CTF DASHBOARD
         Port: 3000
         Tracks Labs 1, 2, 3, 5 (pre + post mitigation)
    ======================================================
    """)
    app.run(host='0.0.0.0', port=3000, debug=True)
