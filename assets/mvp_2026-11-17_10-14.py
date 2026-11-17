#!/usr/bin/env python3
import sys
import json
import urllib.request
import http.server
import socketserver
import threading
import time

class IncidentAnalyzerHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode('utf-8'))
            patch_logs = data.get("logs", "")
            
            # تحليل مبدئي لأخطاء التحديثات والبنية التحتية
            risk_score = 0
            warnings = []
            
            if "july fix" in patch_logs.lower() or "defect" in patch_logs.lower():
                risk_score += 8
                warnings.append("Critical Software Defect Indicator Detected (Similar to Microsoft July Fix Outage)")
            if "timeout" in patch_logs.lower() or "crash" in patch_logs.lower():
                risk_score += 5
                warnings.append("Performance degradation or crash risk identified")

            status = "SAFE" if risk_score < 5 else "HIGH_RISK_REJECT_DEPLOYMENT"
            
            response = {
                "status": status,
                "risk_score": risk_score,
                "warnings": warnings,
                "action": "Hold deployment and review root cause" if status != "SAFE" else "Proceed with caution"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def log_message(self, format, *args):
        # Suppress server logs for clean self-test output
        pass

def run_self_test():
    print("Running MVP Self-Test...")
    port = 8998
    server = socketserver.TCPServer(("127.0.0.1", port), IncidentAnalyzerHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(0.5)
    
    # Test payload simulating the Microsoft bug report context
    payload = json.dumps({
        "logs": "Deploying July fix update, software defect introduced causing monster email outage."
    }).encode('utf-8')
    
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/",
        data=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print("Self-Test Response Received:")
            print(json.dumps(res_data, indent=2))
            assert res_data["status"] == "HIGH_RISK_REJECT_DEPLOYMENT", "Self-test validation failed!"
            print("SUCCESS: Self-Test passed cleanly using standard libraries only.")
    except Exception as e:
        print(f"Self-Test Failed: {e}")
        sys.exit(1)
    finally:
        server.shutdown()
        server.server_close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        run_self_test()
    else:
        print("Usage: python3 script.py --self-test")