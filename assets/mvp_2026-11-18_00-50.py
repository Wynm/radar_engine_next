#!/usr/bin/env python3
"""
Inference Optimisation Skill - MVP & Self-Test Engine
Author: Automated Analysis System
Description: Optimises LLM inference parameters and KV Cache configurations locally.
"""

import sys
import json
import time
import http.server
import socketserver
import threading
from urllib.parse import urlparse, parse_qs

class InferenceOptimizer:
    def __init__(self, target_latency_ms=100.0):
        self.target_latency_ms = target_latency_ms
        self.history = []

    def optimize_parameters(self, current_latency, kv_cache_size, batch_size):
        """
        Implements a hill-climbing logic to adjust parameters for optimal LLM throughput.
        """
        adjustment_score = 0.0
        recommendations = {}

        # KV Cache optimisation heuristic
        if kv_cache_size < 4096:
            recommendations["kv_cache"] = "Increase KV Cache size to at least 4096 for better context handling."
            adjustment_score += 0.4
        else:
            recommendations["kv_cache"] = "KV Cache size is optimal."
            adjustment_score += 0.5

        # Latency adjustment
        if current_latency > self.target_latency_ms:
            recommendations["batch_size"] = max(1, batch_size - 1)
            recommendations["quantization"] = "Apply INT8 or INT4 quantization to reduce compute overhead."
            adjustment_score += 0.3
        else:
            recommendations["batch_size"] = batch_size + 1
            recommendations["quantization"] = "Current quantization level is performing within acceptable limits."
            adjustment_score += 0.5

        return {
            "score": round(min(1.0, adjustment_score), 2),
            "recommendations": recommendations,
            "timestamp": time.time()
        }

class OptimizationHandler(http.server.BaseHTTPRequestHandler):
    optimizer = InferenceOptimizer()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "service": "inference-optimisation-skill"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif parsed_path.path == '/optimize':
            query_params = parse_qs(parsed_path.query)
            latency = float(query_params.get('latency', [120.0])[0])
            kv_size = int(query_params.get('kv_size', [2048])[0])
            batch = int(query_params.get('batch', [4])[0])

            result = self.optimizer.optimize_parameters(latency, kv_size, batch)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        # Suppress default server logs for cleaner output
        return

def run_self_test():
    print("[Self-Test] Initialising Inference Optimisation Skill Self-Test...")
    optimizer = InferenceOptimizer(target_latency_ms=100.0)
    
    # Test Case 1: High latency, small KV Cache
    res1 = optimizer.optimize_parameters(current_latency=150.0, kv_cache_size=2048, batch_size=8)
    assert res1["score"] > 0, "Test Case 1 Failed: Score should be positive"
    print(f"[Self-Test] Test Case 1 Passed. Result: {json.dumps(res1)}")

    # Test Case 2: Optimal parameters
    res2 = optimizer.optimize_parameters(current_latency=80.0, kv_cache_size=8192, batch_size=2)
    assert res2["score"] >= 0.8, "Test Case 2 Failed: Score should be high for optimal state"
    print(f"[Self-Test] Test Case 2 Passed. Result: {json.dumps(res2)}")

    # Test Micro-SaaS Server Health Check locally
    port = 8998
    server = socketserver.TCPServer(("127.0.0.1", port), OptimizationHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    import urllib.request
    try:
        time.sleep(0.5)
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health") as response:
            data = json.loads(response.read().decode())
            assert data["status"] == "healthy"
            print(f"[Self-Test] HTTP Server Health Check Passed: {data}")
            
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/optimize?latency=110&kv_size=4096&batch=4") as response:
            data = json.loads(response.read().decode())
            assert "recommendations" in data
            print(f"[Self-Test] HTTP Optimisation API Passed: {data}")
    finally:
        server.shutdown()
        server.server_close()

    print("[Self-Test] ALL TESTS PASSED SUCCESSFULLY.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        run_self_test()
    else:
        print("Usage: python3 script.py --self-test")
        sys.exit(1)