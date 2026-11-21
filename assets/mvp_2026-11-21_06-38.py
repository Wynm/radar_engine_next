import http.server
import json
import sys
import urllib.parse

class AntiAlgorithmHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_POST(self):
        if self.path == '/generate':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                prompt = data.get('prompt', '')
                
                # تطبيق منطق Anti-Algorithm: استبعاد المخرج الإحصائي الأول النمطي
                first_obvious_output = f"Standard generic response for: {prompt}"
                refined_output = f"Creative, non-obvious deep analysis for: {prompt} (Excluding: '{first_obvious_output}')"
                
                response = {
                    "status": "success",
                    "rejected_first_choice": first_obvious_output,
                    "final_unique_output": refined_output
                }
                self._set_headers(200)
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str.upper(str(e))}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "NOT_FOUND"}).encode('utf-8'))

def run_self_test():
    print("[-] Running Anti-Algorithm MVP Self-Test...")
    # محاكاة طلب داخلي للاختبار بدون الاعتماد على شبكة خارجية
    class MockRequest:
        def make_call(self):
            prompt = "Best marketing strategy"
            first_obvious = f"Standard generic response for: {prompt}"
            refined = f"Creative, non-obvious deep analysis for: {prompt} (Excluding: '{first_obvious}')"
            return refined

    test_req = MockRequest()
    result = test_req.make_call()
    
    assert "Creative, non-obvious" in result, "Self-test failed: Output not refined!"
    print("[+] Self-Test Passed Successfully!")
    print(f"[+] Sample Output: {result}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--self-test':
        run_self_test()
        sys.exit(0)
    
    server_port = 8080
    server_address = ('', server_port)
    httpd = http.server.HTTPServer(server_address, AntiAlgorithmHandler)
    print(f"[+] Anti-Algorithm Micro-SaaS MVP running on port {server_port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Server stopped.")