import http.server
import socketserver
import json
import urllib.parse
import threading
import os
import sqlite3
from crawler.indexer import PlumIndexer
from search_engine.searcher import PlumSearchEngine

PORT = 8000
DB_PATH = 'plumcrawl.db'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PlumCrawl - AI Multi-Agent Search</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #e6e6fa; margin: 0; padding: 20px; }
        .container { width: 95%; max-width: 1400px; margin: auto; background: #2d2d2d; padding: 30px; border-radius: 15px; border: 1px solid #8e4585; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #8e4585; text-align: center; font-size: 2.5em; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #b19cd9; margin-bottom: 30px; }
        
        .grid-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 900px) { .grid-container { grid-template-columns: 1fr; } }
        
        .section { background: #333; padding: 20px; border-radius: 10px; border-left: 5px solid #8e4585; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #b19cd9; }
        input[type="text"], input[type="number"] { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 5px; border: 1px solid #444; background: #1e1e1e; color: white; box-sizing: border-box; }
        button { background: #8e4585; color: white; border: none; padding: 12px 25px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: 0.3s; width: 100%; }
        button:hover { background: #b19cd9; }
        
        .history-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 15px; }
        .history-tag { background: #1e1e1e; color: #b19cd9; padding: 5px 10px; border-radius: 15px; font-size: 0.85em; border: 1px solid #8e4585; cursor: pointer; }
        .history-tag:hover { background: #8e4585; color: white; }
        
        .stats { display: flex; justify-content: space-around; background: #1e1e1e; padding: 15px; border-radius: 8px; margin-top: 20px; }
        .stat-item { text-align: center; }
        .stat-value { font-size: 1.8em; color: #8e4585; font-weight: bold; }
        
        #results { margin-top: 20px; }
        .result-card { background: #3d3d3d; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-bottom: 2px solid #8e4585; word-wrap: break-word; }
        .result-url { color: #b19cd9; text-decoration: none; font-weight: bold; font-size: 1.1em; }
        .result-url:hover { text-decoration: underline; }
        .result-meta { font-size: 0.85em; color: #aaa; margin-top: 8px; display: flex; justify-content: space-between; }
    </style>
</head>
<body>
    <div class="container">
        <h1>PlumCrawl</h1>
        <p class="subtitle">Multi-Agent AI Indexer & Search Engine</p>

        <div class="grid-container">
            <div class="section">
                <label>Start New Indexing</label>
                <input type="text" id="origin" placeholder="e.g., https://en.wikipedia.org/wiki/History">
                <label>Depth (0-3)</label>
                <input type="number" id="depth" value="2" min="0" max="3">
                <button onclick="startIndex()">Start Indexing</button>
                <div id="indexMsg" style="margin-top:15px; font-size:0.9em; text-align: center;"></div>
                
                <button onclick="resetSystem()" style="background: #d9534f; margin-top: 20px;">🚨 Reset Entire Database</button>

                <hr style="border: 0; border-top: 1px solid #444; margin: 20px 0;">
                <label>Indexing History (Click to re-index)</label>
                <div class="history-tags" id="history-container"></div>
            </div>

            <div class="section">
                <label>Search Indexed Pages</label>
                <input type="text" id="query" placeholder="Enter keywords (e.g., ancient, war, science)..." onkeypress="if(event.key === 'Enter') runSearch()">
                <button onclick="runSearch()">Search</button>
                <div class="stats" id="telemetry">
                    <div class="stat-item"><div>Indexed</div><div class="stat-value" id="stat-indexed">0</div></div>
                    <div class="stat-item"><div>Queue</div><div class="stat-value" id="stat-queue">0</div></div>
                    <div class="stat-item"><div>Failed (Blocked)</div><div class="stat-value" id="stat-failed" style="color:#d9534f;">0</div></div>
                </div>
            </div>
        </div>

        <div id="results"></div>
    </div>

    <script>
        function updateUI() {
            fetch('/stats').then(r => r.json()).then(data => {
                document.getElementById('stat-indexed').innerText = data.indexed;
                document.getElementById('stat-queue').innerText = data.queue;
                document.getElementById('stat-failed').innerText = data.failed;
            });
            fetch('/history').then(r => r.json()).then(data => {
                const histDiv = document.getElementById('history-container');
                histDiv.innerHTML = '';
                if(data.length === 0) histDiv.innerHTML = '<span style="color:#777; font-size:0.8em;">No history yet.</span>';
                data.forEach(url => {
                    histDiv.innerHTML += `<div class="history-tag" onclick="document.getElementById('origin').value='${url}'">${url}</div>`;
                });
            });
        }
        setInterval(updateUI, 1500);
        updateUI();

        function startIndex() {
            const origin = document.getElementById('origin').value;
            const depth = document.getElementById('depth').value;
            if(!origin) return;
            
            document.getElementById('indexMsg').innerHTML = 
                `<span style="color:#b19cd9;">Indexing initiated for:</span> <br><b>${origin}</b> (Depth: ${depth})`;
                
            fetch(`/index?origin=${encodeURIComponent(origin)}&k=${depth}`)
                .then(r => r.json());
        }

        function runSearch() {
            const query = document.getElementById('query').value;
            if(!query) return;
            fetch(`/search?q=${encodeURIComponent(query)}`)
                .then(r => r.json())
                .then(data => {
                    const resDiv = document.getElementById('results');
                    resDiv.innerHTML = `<h3 style="color:#8e4585;">Search Results for "${query}"</h3>`;
                    if(data.length === 0) resDiv.innerHTML += '<p style="color:#aaa;">No relevant results found in the local index.</p>';
                    data.forEach(item => {
                        resDiv.innerHTML += `
                            <div class="result-card">
                                <a class="result-url" href="${item[0]}" target="_blank">${item[0]}</a>
                                <div class="result-meta">
                                    <span><b>Origin:</b> ${item[1]}</span>
                                    <span><b>Depth:</b> ${item[2]}</span>
                                </div>
                            </div>
                        `;
                    });
                });
        }

        
        function resetSystem() {
            if(confirm("Are you sure you want to clear all indexed pages and history?")) {
                fetch('/reset').then(() => {
                    alert("Database reset successful! You can now crawl the same link again.");
                    updateUI();
                });
            }
        }
    </script>
</body>
</html>
"""

class PlumWebHandler(http.server.BaseHTTPRequestHandler):
    searcher = PlumSearchEngine()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())

        elif parsed_path.path == '/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
            cursor = conn.cursor()
            try:
                indexed = cursor.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
                queue = cursor.execute("SELECT COUNT(*) FROM crawl_queue WHERE status = 0").fetchone()[0]
                failed = cursor.execute("SELECT COUNT(*) FROM crawl_queue WHERE status = 3").fetchone()[0]
            except:
                indexed, queue, failed = 0, 0, 0
            conn.close()
            self.wfile.write(json.dumps({"indexed": indexed, "queue": queue, "failed": failed}).encode())
            
        elif parsed_path.path == '/history':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
            cursor = conn.cursor()
            try:
                origins = [row[0] for row in cursor.execute("SELECT DISTINCT origin_url FROM pages WHERE origin_url != 'START' LIMIT 10").fetchall()]
            except:
                origins = []
            conn.close()
            self.wfile.write(json.dumps(origins).encode())

        
        elif parsed_path.path == '/reset':
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM pages")
                cursor.execute("DELETE FROM crawl_queue")
                cursor.execute("DELETE FROM word_index")
                conn.commit()
            except sqlite3.OperationalError:
                pass
            conn.close()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "reset"}).encode())

        elif parsed_path.path == '/search':
            query = urllib.parse.parse_qs(parsed_path.query).get('q', [''])[0]
            results = self.searcher.search(query)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode())

        elif parsed_path.path == '/index':
            params = urllib.parse.parse_qs(parsed_path.query)
            origin = params.get('origin', [''])[0]
            k = int(params.get('k', [0])[0])
            
            def run_indexer():
                indexer = PlumIndexer(max_queue_depth=500, rate_limit_sec=0.5, max_threads=5)
                indexer.index(origin, k)
            
            threading.Thread(target=run_indexer, daemon=True).start()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "started"}).encode())

        else:
            self.send_error(404)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), PlumWebHandler) as httpd:
        print(f"PlumCrawl Web UI running at http://localhost:{PORT}")
        httpd.serve_forever()