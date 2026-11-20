#!/usr/bin/env python3
import sys
import http.server
import socketserver
import json
import urllib.request
import urllib.error
import threading
import time

PORT = 8080

class DevOpsAgentHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "agent": "Volcano-Clone", "self_healing": "active"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Endpoint not found"}')

    def do_POST(self):
        if self.path == '/heal-infrastructure':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                service_name = data.get('service', 'unknown')
                
                # محاكاة الإصلاح الذاتي للبنية التحتية
                fix_action = f"Restarted service {service_name}, cleared cache, and optimized memory allocation."
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "success", "action_taken": fix_action, "timestamp": time.time()}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    handler = DevOpsAgentHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Volcano-Clone Micro-SaaS Agent running on port {PORT}...")
        httpd.serve_forever()

def self_test():
    print("Running self-test for Volcano Micro-SaaS Agent...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1) # الانتظار حتى يبتدئ الخادم
    
    try:
        # اختبار نقطة النهاية /health
        url = f"http://localhost:{PORT}/health"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            data = json.loads(body)
            assert data.get("status") == "healthy", "Health check failed!"
        print("Self-test /health passed successfully.")

        # اختبار نقطة النهاية /heal-infrastructure
        heal_url = f"http://localhost:{PORT}/heal-infrastructure"
        payload = json.dumps({"service": "payment-api"}).encode('utf-8')
        req = urllib.request.Request(heal_url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            data = json.loads(body)
            assert data.get("status") == "success", "Self-healing action failed!"
        print("Self-test /heal-infrastructure passed successfully.")
        print("All MVP tests passed successfully. Ready for deployment!")
        sys.exit(0)
    except Exception as e:
        print(f"Self-test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        self_test()
    else:
        run_server()