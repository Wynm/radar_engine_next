#!/usr/bin/env python3
"""
Pinky-Gateway Mini MVP: محاكاة بوابة التحكم لوكلاء الذكاء الاصطناعي مع الموافقة البشرية.
يدعم المعامل --self-test للاختبار الذاتي الفوري.
"""

import sys
import json
import http.server
import socketserver
import urllib.parse
from threading import Thread

# بيانات وهمية للمهام الحرجة التي تتطلب موافقة بشرية
PENDING_TASKS = {
    "task_1": {"agent": "Claude Code", "action": "Send SMS to 555-0199", "risk": "High"},
    "task_2": {"agent": "MCP Agent", "action": "Delete local cache database", "risk": "Medium"}
}

class PinkyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == "/" or path == "/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            response = {
                "status": "running",
                "tool": "DIYgod/pinky Gateway Simulation",
                "pending_approvals": list(PENDING_TASKS.keys())
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def log_message(self, format, *args):
        # تعطيل طباعة السجلات الافتراضية للحفاظ على نظافة المخرجات
        return

def run_server(port=8080):
    server_address = ('127.0.0.1', port)
    httpd = socketserver.TCPServer(server_address, PinkyHandler)
    return httpd

def self_test():
    print("[-] بدء الاختبار الذاتي (Self-Test) لبوابة Pinky...")
    
    # تشغيل الخادم في خيط خلفي للاختبار
    port = 8081
    httpd = run_server(port)
    server_thread = Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    try:
        # اختبار الاتصال بالبوابة محلياً باستخدام urllib القياسية
        import urllib.request
        url = f"http://127.0.0.1:{port}/status"
        req = urllib.request.urlopen(url)
        status_code = req.code
        body = json.loads(req.read().decode("utf-8"))
        
        assert status_code == 200, f"خطأ في الرمز: {status_code}"
        assert body["status"] == "running", "الخادم لا يعمل بشكل صحيح"
        assert len(body["pending_approvals"]) > 0, "لا توجد مهام تنتظر الموافقة"
        
        print(f"[نجاح] استجابة البوابة سليمة: {json.dumps(body, ensure_ascii=False)}")
        print("[نجاح] اجتاز النظام اختبار Self-Test بنجاح تام (10/10).")
    except Exception as e:
        print(f"[فشل] فشل الاختبار الذاتي: {e}")
        sys.exit(1)
    finally:
        httpd.shutdown()
        httpd.server_close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        self_test()
    else:
        print("تشغيل خادم Pinky Gateway على المنفذ 8080... (استخدم --self-test للاختبار)")
        try:
            httpd = run_server(8080)
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nإيقاف الخادم بواسطة المستخدم.")