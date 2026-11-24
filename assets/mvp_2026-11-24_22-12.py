#!/usr/bin/env python3
import sys
import json
import http.server
import urllib.request
import urllib.error
import socket
from datetime import datetime

# Simple Micro-SaaS Core: AI Agent Security & Config Scanner MVP

def scan_agent_config(config_data):
    """
    يفحص إعدادات وكيل الذكاء الاصطناعي بحثاً عن ثغرات شائعة
    مثل تفعيل التنفيذ الديناميكي أو غياب المصادقة.
    """
    issues = []
    risk_score = 0
    
    # التحقق من التنفيذ الديناميكي (خطير جداً في الـ Agents)
    if config_data.get("allow_dynamic_eval", False):
        issues.append("CRITICAL: Dynamic code evaluation (eval/exec) is enabled.")
        risk_score += 5
        
    # التحقق من وجود مفتاح API أو غيابه
    if not config_data.get("api_key"):
        issues.append("HIGH: Missing API authentication key.")
        risk_score += 3
        
    # التحقق من وضع التصحيح
    if config_data.get("debug_mode", False):
        issues.append("MEDIUM: Debug mode is enabled in production environment.")
        risk_score += 2
        
    status = "SECURE" if risk_score == 0 else ("VULNERABLE" if risk_score < 5 else "CRITICAL")
    
    return {
        "status": status,
        "risk_score": risk_score,
        "issues_found": issues,
        "timestamp": datetime.utcnow().isoformat()
    }

class MVPHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/scan":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                result = scan_agent_config(data)
                response = json.dumps(result).encode('utf-8')
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response)
            except Exception as e:
                error_response = json.dumps({"error": str.upper(str(e))}).encode('utf-8')
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(error_response)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Endpoint not found. Use POST /api/scan")

def run_self_test():
    print("[*] Running MVP Self-Test...")
    test_config = {
        "agent_name": "TestAgent",
        "allow_dynamic_eval": True,
        "api_key": "",
        "debug_mode": True
    }
    
    result = scan_agent_config(test_config)
    print(f"[+] Test Scan Result: {json.dumps(result, indent=2)}")
    
    if result["risk_score"] > 0 and len(result["issues_found"]) > 0:
        print("[+] Self-Test PASSED Successfully!")
        sys.exit(0)
    else:
        print("[-] Self-Test FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        run_self_test()
    else:
        port = 8080
        server = http.server.HTTPServer(('0.0.0.0', port), MVPHandler)
        print(f"[*] Starting Micro-SaaS Security Scanner MVP on port {port}...")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[!] Server stopped by user.")
            server.server_close()