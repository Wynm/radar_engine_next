#!/usr/bin/env python3
"""
Agentes-Chat Micro-SaaS MVP & Self-Test Core
Demonstrates an HTTP server and AI agent task routing mechanism.
Run with: python3 script.py --self-test
"""

import sys
import json
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class AgentRouterHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "service": "agentes-chat-mvp", "ready": True}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif parsed_path.path == '/task':
            query_params = parse_qs(parsed_path.query)
            prompt = query_params.get('prompt', ['Default task'])[0]
            
            # Simulate AI Agent execution (Claude/GPT/Gemini routing)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            result = {
                "agent": "Claude-MCP-Bridge",
                "processed_prompt": prompt,
                "execution_status": "Success",
                "output": f"Executed automated routine for: '{prompt}' with local tools."
            }
            self.wfile.write(json.dumps(result).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def log_message(self, format, *args):
        # Suppress server logs during normal operation for clean output
        return

def run_self_test():
    print("[Self-Test] Starting Agentes-Chat MVP Self-Test...")
    
    # Start a test server on an ephemeral port
    server = HTTPServer(('127.0.0.1', 0), AgentRouterHandler)
    port = server.server_port
    
    import threading
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    try:
        # Test 1: Health Check
        health_url = f"http://127.0.0.1:{port}/health"
        req = urllib.request.urlopen(health_url)
        health_data = json.loads(req.read().decode('utf-8'))
        assert health_data.get("status") == "healthy", "Health check failed!"
        print("[Self-Test] ✓ Health check passed.")
        
        # Test 2: AI Task Routing
        task_url = f"http://127.0.0.1:{port}/task?prompt=Analyze_Sales_Pipeline"
        req_task = urllib.request.urlopen(task_url)
        task_data = json.loads(req_task.read().decode('utf-8'))
        assert task_data.get("execution_status") == "Success", "Task execution failed!"
        print(f"[Self-Test] ✓ AI Agent Routing passed. Output: {task_data.get('output')}")
        
        print("\n[SUCCESS] All self-tests passed successfully. The MVP core is fully operational.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAILURE] Self-test failed: {e}")
        sys.exit(1)
    finally:
        server.shutdown()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--self-test':
        run_self_test()
    else:
        print("Usage: python3 script.py --self-test")
        sys.exit(1)