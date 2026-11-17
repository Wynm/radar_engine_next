#!/usr/bin/env python3
"""
Cal-MicroSaaS Core MVP (Python Standard Library Only)
Supports HTTP server and --self-test mode for instant deployment.
"""

import http.server
import json
import socketserver
import sys
import urllib.parse
import urllib.request

PORT = 8080
BOOKINGS_DB = []

class SaaSHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {
                "service": "Cal-MicroSaaS Wrapper",
                "status": "active",
                "endpoints": ["/book (POST)", "/bookings (GET)"]
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            
        elif parsed_path.path == '/bookings':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(BOOKINGS_DB).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/book':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                # Validate minimal required fields
                if not all(k in data for k in ("client_name", "date", "time")):
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"error": "Missing fields: client_name, date, time"}')
                    return
                
                booking_id = len(BOOKINGS_DB) + 1
                new_booking = {
                    "id": booking_id,
                    "client_name": data["client_name"],
                    "date": data["date"],
                    "time": data["time"],
                    "status": "confirmed"
                }
                BOOKINGS_DB.append(new_booking)
                
                self.send_response(201)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "booking": new_booking}).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_self_test():
    """Executes a complete self-test of the Micro-SaaS endpoints."""
    import threading
    import time
    
    print("[*] Starting Self-Test for Cal-MicroSaaS MVP...")
    
    # Start server in background thread
    handler = SaaSHandler
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(0.5) # Give server time to bind
    
    base_url = f"http://127.0.0.1:{PORT}"
    
    try:
        # 1. Test Root Endpoint
        req = urllib.request.urlopen(base_url + "/")
        assert req.status == 200, "Root endpoint failed"
        print("[+] Root endpoint: OK")
        
        # 2. Test Booking Creation (POST)
        booking_payload = json.dumps({
            "client_name": "John Doe",
            "date": "2023-12-01",
            "time": "14:00"
        }).encode("utf-8")
        
        req = urllib.request.Request(base_url + "/book", data=booking_payload, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req) as response:
            assert response.status == 201, "Booking creation failed"
            res_data = json.loads(response.read().decode('utf-8'))
            assert res_data["success"] is True, "Booking success flag missing"
        print("[+] Booking creation: OK")
        
        # 3. Test Retrieve Bookings (GET)
        req = urllib.request.urlopen(base_url + "/bookings")
        assert req.status == 200, "Retrieve bookings failed"
        bookings = json.loads(req.read().decode('utf-8'))
        assert len(bookings) == 1, "Bookings count mismatch"
        print("[+] Retrieve bookings: OK")
        
        print("\n[SUCCESS] ALL SELF-TESTS PASSED PERFECTLY!")
        success = True
    except Exception as e:
        print(f"\n[FAILURE] Self-test failed: {e}")
        success = False
    finally:
        httpd.shutdown()
        httpd.server_close()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        run_self_test()
    else:
        print(f"[*] Starting Cal-MicroSaaS Server on port {PORT}...")
        with socketserver.TCPServer(("", PORT), SaaSHandler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[*] Server stopped.")