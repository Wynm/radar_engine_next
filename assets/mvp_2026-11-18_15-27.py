#!/usr/bin/env python3
"""
Video Stream Intelligence & Event Logger (Micro-SaaS Core MVP)
Compatible with standard Python libraries only (no external pip dependencies).
Supports --self-test for instant validation.
"""

import sys
import json
import time
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# --- Core Business Logic: Video Event Analyzer ---
class StreamAnalyzer:
    """Simulates real-time AI video stream analysis and event triggering."""
    
    def __init__(self, sensitivity_threshold=0.75):
        self.threshold = sensitivity_threshold

    def analyze_frame_metadata(self, frame_data: dict) -> dict:
        """Analyzes frame telemetry to detect proactive interaction triggers."""
        motion_score = frame_data.get("motion_score", 0.0)
        audio_level = frame_data.get("audio_level", 0.0)
        
        # Combined anomaly or trigger score
        interaction_score = (motion_score * 0.6) + (audio_level * 0.4)
        trigger_action = interaction_score >= self.threshold
        
        return {
            "timestamp": time.time(),
            "interaction_score": round(interaction_score, 4),
            "trigger_action": trigger_action,
            "status": "ALERT_DISPATCHED" if trigger_action else "MONITORING"
        }

# --- HTTP Micro-Service Handler ---
class SimpleAPIHandler(BaseHTTPRequestHandler):
    analyzer = StreamAnalyzer()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/api/v1/analyze":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body.decode('utf-8'))
                result = self.analyzer.analyze_frame_metadata(data)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Endpoint not found. Use POST /api/v1/analyze")

    def log_message(self, format, *args):
        # Suppress default server logs for clean test outputs
        return

# --- Self-Test Routine ---
def run_self_test():
    """Executes a complete integration self-test without external dependencies."""
    print("[-] Starting Self-Test for StreamAnalyzer MVP...")
    
    # 1. Test Internal Logic
    analyzer = StreamAnalyzer(sensitivity_threshold=0.5)
    
    normal_frame = {"motion_score": 0.2, "audio_level": 0.1}
    res_normal = analyzer.analyze_frame_metadata(normal_frame)
    assert res_normal["trigger_action"] is False, "Self-test failed on normal frame logic."

    active_frame = {"motion_score": 0.9, "audio_level": 0.8}
    res_active = analyzer.analyze_frame_metadata(active_frame)
    assert res_active["trigger_action"] is True, "Self-test failed on active frame logic."
    print("[+] Core Logic Tests Passed.")

    # 2. Test HTTP Server Integration
    port = 8085
    server = HTTPServer(('127.0.0.1', port), SimpleAPIHandler)
    
    import threading
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(0.2) # Allow server to spin up
    
    try:
        url = f"http://127.0.0.1:{port}/api/v1/analyze"
        payload = json.dumps({"motion_score": 0.85, "audio_level": 0.9}).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_data = json.loads(response.read().decode('utf-8'))
            
            assert status_code == 200, f"Expected HTTP 200, got {status_code}"
            assert response_data["trigger_action"] is True, "HTTP endpoint did not trigger expected action."
            print("[+] HTTP API Integration Tests Passed.")
            
    finally:
        server.shutdown()
        server.server_close()
        
    print("[SUCCESS] All Self-Tests Passed Successfully!")

# --- Entry Point ---
if __name__ == "__main__":
    if "--self-test" in sys.argv:
        run_self_test()
    else:
        print("Usage: python script.py --self-test")
        print("Running default standalone analyzer demo...")
        analyzer = StreamAnalyzer()
        print(analyzer.analyze_frame_metadata({"motion_score": 0.8, "audio_level": 0.7}))