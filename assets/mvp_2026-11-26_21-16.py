#!/usr/bin/env python3
"""
Data Broker Opt-Out Automation MVP (Core Engine)
Supports --self-test for immediate validation without external dependencies.
"""

import sys
import json
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# قائمة ببعض وسطاء البيانات الوهمية أو الحقيقية لاختبار إرسال الطلبات
BROKERS_DATABASE = [
    {"name": "DataBrokerA", "opt_out_url": "https://httpbin.org/post", "method": "POST"},
    {"name": "InfoSellerB", "opt_out_url": "https://httpbin.org/post", "method": "POST"}
]

def generate_opt_out_payload(user_email: str, user_name: str) -> dict:
    return {
        "request_type": "CCPA/GDPR Data Deletion Request",
        "name": user_name,
        "email": user_email,
        "statement": "I hereby request the permanent deletion of all my personal data."
    }

def send_removal_request(broker: dict, payload: dict) -> bool:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        broker["opt_out_url"], 
        data=data, 
        headers={'Content-Type': 'application/json', 'User-Agent': 'PrivacyBot/1.0'}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except Exception:
        return False

class PrivacyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
            email = data.get("email", "test@example.com")
            name = data.get("name", "John Doe")
            
            results = []
            payload = generate_opt_out_payload(email, name)
            for broker in BROKERS_DATABASE:
                success = send_removal_request(broker, payload)
                results.append({"broker": broker["name"], "success": success})
            
            response = {"status": "success", "results": results}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

def run_self_test():
    print("Running self-test for Data Broker Opt-Out MVP...")
    payload = generate_opt_out_payload("privacy_test@example.com", "Test User")
    
    success_count = 0
    for broker in BROKERS_DATABASE:
        res = send_removal_request(broker, payload)
        if res:
            success_count += 1
            print(f"[PASS] Successfully simulated request to {broker['name']}")
        else:
            print(f"[FAIL] Could not reach {broker['name']}")
            
    if success_count > 0:
        print("\n[SELF-TEST RESULT]: SUCCESS (Core engine is operational)")
        sys.exit(0)
    else:
        print("\n[SELF-TEST RESULT]: FAILED (Network or endpoint issue)")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        run_self_test()
    else:
        server_address = ('', 8080)
        httpd = HTTPServer(server_address, PrivacyHandler)
        print("Starting Privacy SaaS Micro-Server on port 8080...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass