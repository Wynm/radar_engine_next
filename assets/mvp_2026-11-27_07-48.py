#!/usr/bin/env python3
"""
Micro-Game Generator MVP (Aligned with nexu-io/opengame concept)
Standard Python libraries only. No external pip packages required.
Supports --self-test execution.
"""

import sys
import json
import http.server
import socketserver
import urllib.parse
import threading
import time

class GameGenerator:
    """Core logic to generate mini-game boilerplates for Telegram/TikTok platforms."""
    templates = {
        "telegram": {"platform": "Telegram Mini App", "format": "HTML5/JS Canvas", "monetization": "Ads/Stars"},
        "tiktok": {"platform": "TikTok Effect House", "format": "Interactive WebGL", "monetization": "In-app Coins"}
    }

    def generate(self, game_name: str, target_platform: str) -> dict:
        platform_info = self.templates.get(target_platform.lower(), self.templates["telegram"])
        code_snippet = f"""
        // Generated Mini-Game: {game_name} for {platform_info['platform']}
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        let score = 0;
        function update() {{
            ctx.fillStyle = '#111';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0ff';
            ctx.font = '20px Arial';
            ctx.fillText('Score: ' + score, 20, 40);
        }}
        setInterval(update, 1000 / 30);
        """
        return {
            "status": "success",
            "game_name": game_name,
            "platform": platform_info['platform'],
            "format": platform_info['format'],
            "monetization": platform_info['monetization'],
            "code": code_snippet.strip()
        }

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    generator = GameGenerator()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            response = {
                "service": "Micro-Game AI Generator MVP",
                "usage": "/generate?name=GameName&platform=telegram"
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        elif parsed_path.path == '/generate':
            query_params = urllib.parse.parse_qs(parsed_path.query)
            game_name = query_params.get('name', ['DefaultGame'])[0]
            platform = query_params.get('platform', ['telegram'])[0]
            
            result = self.generator.generate(game_name, platform)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')

    def log_message(self, format, *args):
        # Suppress HTTP server logs for clean stdout during tests
        return

def run_self_test():
    print("[-] Running MVP Self-Test...")
    gen = GameGenerator()
    
    # Test generation logic
    res = gen.generate("CyberRunner", "telegram")
    assert res["status"] == "success", "Generation failed status"
    assert res["game_name"] == "CyberRunner", "Game name mismatch"
    assert "Canvas" in res["format"], "Format mismatch"
    print("[+] GameGenerator logic test passed successfully.")
    
    # Test HTTP Server in a background thread
    port = 8085
    server = socketserver.TCPServer(("127.0.0.1", port), SimpleHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(0.5)
    
    # Make a test HTTP request
    import urllib.request
    try:
        url = f"http://127.0.0.1:{port}/generate?name=TestQuest&platform=tiktok"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            assert data["game_name"] == "TestQuest"
            assert data["platform"] == "TikTok Effect House"
            print("[+] HTTP Micro-SaaS endpoint test passed successfully.")
    finally:
        server.shutdown()
        server.server_close()
        
    print("[SUCCESS] All self-tests passed cleanly without external dependencies!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--self-test':
        run_self_test()
    else:
        print("Starting Micro-Game Generator MVP Server on port 8080...")
        print("Run with --self-test to execute automated tests.")
        with socketserver.TCPServer(("", 8080), SimpleHandler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")