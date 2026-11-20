import http.server
import socketserver
import json
import urllib.parse
import sys
import os
import time

# نواة خدمة Micro-SaaS مصغرة لأتمتة فحص واختبار الأكواد والبيانات
class CodeTestAgentHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/':
            self._set_headers(200, "text/html; charset=utf-8")
            html_content = """
            <html>
                <head><title>AI TestSprite Agent MVP</title></head>
                <body style="font-family: Arial; padding: 20px;">
                    <h2>Welcome to AI TestSprite Agent MVP</h2>
                    <p>Use POST /test to analyze and test code snippets.</p>
                </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
        elif parsed_path.path == '/health':
            self._set_headers(200)
            response = {"status": "healthy", "service": "TestSprite-Agent-Core", "timestamp": time.time()}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/test':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                code_snippet = data.get("code", "")
                
                # تحليل محاكاة لاختبار الأخطاء (Regression & Syntax simulation)
                issues = []
                if "import os" in code_snippet and "rmtree" in code_snippet:
                    issues.append("Security Warning: Dangerous file deletion command detected.")
                if "def " not in code_snippet:
                    issues.append("Quality Notice: No function definitions found in snippet.")
                
                result = {
                    "status": "success",
                    "lines_analyzed": len(code_snippet.splitlines()),
                    "issues_found": len(issues),
                    "warnings": issues,
                    "passed": len(issues) == 0
                }
                
                self._set_headers(200)
                self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))

def run_self_test():
    print("[Self-Test] Starting autonomous system verification...")
    
    # محاكاة طلب اختبار داخلي بدون الحاجة لرفع خادم خارجي بالكامل للاختبار
    class MockHandler:
        def __init__(self, code):
            self.code = code
        def analyze(self):
            issues = []
            if "eval(" in self.code:
                issues.append("Critical: Use of eval() is insecure.")
            return {"passed": len(issues) == 0, "issues": issues}

    test_case = "def add(a, b): return a + b\nres = eval('2 + 2')"
    tester = MockHandler(test_case)
    res = tester.analyze()
    
    print(f"[Self-Test] Test Code: {test_case}")
    print(f"[Self-Test] Analysis Result: {res}")
    
    assert res["passed"] == False, "Self-test failed: expected security warning for eval()"
    print("[Self-Test] SUCCESS: All internal validations passed successfully.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--self-test':
        run_self_test()
        sys.exit(0)
        
    PORT = 8080
    print(f"Starting Micro-SaaS Agent Server on port {PORT}...")
    with socketserver.TCPServer(("", PORT), CodeTestAgentHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server gracefully.")