#!/usr/bin/env python3
"""
Micro-SaaS MVP: CurvDelta Safe-Data & Unlearning Filter Core
Applies basic low-curvature logic principles (weight/data masking) for safe data removal.
Supports --self-test execution.
"""

import sys
import json
import http.server
import socketserver
import urllib.parse

PORT = 8080

class SafeUnlearningEngine:
    def __init__(self):
        # محاكاة قاعدة بيانات أو أوزان نموذج للعملاء
        self.knowledge_base = {
            "model_v1": {"capabilities": ["math", "coding"], "sensitive_data": ["user_passwords_xyz", "credit_cards_123"]}
        }

    def unlearn_and_sanitize(self, model_name: str, target_data: str) -> dict:
        """محاكاة عملية الـ Unlearning للحفاظ على القدرات وحذف البيانات الحساسة"""
        if model_name not in self.knowledge_base:
            return {"status": "error", "message": "Model not found"}
        
        current_data = self.knowledge_base[model_name]["sensitive_data"]
        sanitized = [item for item in current_data if target_data not in item]
        
        removed_count = len(current_data) - len(sanitized)
        self.knowledge_base[model_name]["sensitive_data"] = sanitized
        
        return {
            "status": "success",
            "model": model_name,
            "removed_items": removed_count,
            "capabilities_preserved": self.knowledge_base[model_name]["capabilities"]
        }

engine = SafeUnlearningEngine()

class SimpleHTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/unlearn':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                model = data.get("model", "model_v1")
                target = data.get("target", "user_passwords_xyz")
                
                result = engine.unlearn_and_sanitize(model, target)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "CurvDelta-MicroSaaS"}).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h3>CurvDelta Safe Unlearning MVP Service Running</h3><p>Use POST /api/unlearn or GET /health</p>")

def run_self_test():
    print("[-] Running CurvDelta MVP Self-Test...")
    # اختبار محاكاة الحذف الآمن
    res = engine.unlearn_and_sanitize("model_v1", "user_passwords_xyz")
    print(f"[-] Test Result: {res}")
    assert res["status"] == "success", "Self-test failed!"
    assert res["removed_items"] > 0, "No items removed!"
    print("[+] Self-Test Passed Successfully!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--self-test':
        run_self_test()
        sys.exit(0)
    
    print(f"[-] Starting Micro-SaaS Server on port {PORT}...")
    with socketserver.TCPServer(("", PORT), SimpleHTTPHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[-] Server stopped by user.")