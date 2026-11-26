#!/usr/bin/env python3
"""
Micro-SaaS Market Data & Trading Signal Analyzer (MVP)
Domain: Data Analysis & Trading
Supports `--self-test` for instant verification without external dependencies.
"""

import http.server
import json
import urllib.parse
import sys
import unittest

class TradingAnalyzer:
    """Core engine for processing price series and generating technical indicators."""
    @staticmethod
    def simple_moving_average(prices, period):
        if len(prices) < period:
            return []
        sma = []
        for i in range(len(prices) - period + 1):
            window = prices[i:i + period]
            sma.append(sum(window) / period)
        return sma

    @staticmethod
    def generate_signals(prices, short_period=3, long_period=5):
        if len(prices) < long_period:
            return {"error": "Not enough data points for the given periods."}
        
        short_sma = TradingAnalyzer.simple_moving_average(prices, short_period)
        long_sma = TradingAnalyzer.simple_moving_average(prices, long_period)
        
        # Align lengths
        offset = long_period - short_period
        short_aligned = short_sma[offset:]
        
        signals = []
        for i in range(1, len(long_sma)):
            prev_diff = short_aligned[i-1] - long_sma[i-1]
            curr_diff = short_aligned[i] - long_sma[i]
            
            timestamp_index = (long_period - 1) + i
            if prev_diff <= 0 and curr_diff > 0:
                signals.append({"index": timestamp_index, "signal": "BUY", "price": prices[timestamp_index]})
            elif prev_diff >= 0 and curr_diff < 0:
                signals.append({"index": timestamp_index, "signal": "SELL", "price": prices[timestamp_index]})
                
        return {
            "data_points": len(prices),
            "short_sma": short_aligned,
            "long_sma": long_sma,
            "signals": signals
        }


class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)

        if path == "/api/analyze":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            # Default mock price series if none provided
            prices = [100, 102, 101, 105, 107, 106, 110, 115, 112, 118]
            if "prices" in query:
                try:
                    prices = [float(p) for p in query["prices"][0].split(",")]
                except ValueError:
                    pass
            
            result = TradingAnalyzer.generate_signals(prices)
            self.wfile.write(json.dumps(result, indent=2).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found. Use /api/analyze?prices=100,102,101,..."}).encode("utf-8"))

    def log_message(self, format, *args):
        # Suppress server logs during normal operation for cleaner output
        return


class TestTradingAnalyzer(unittest.TestCase):
    def test_sma(self):
        prices = [10, 20, 30, 40, 50]
        sma = TradingAnalyzer.simple_moving_average(prices, 3)
        self.assertEqual(sma, [20.0, 30.0, 40.0])

    def test_signals(self):
        prices = [10, 11, 12, 11, 10, 9, 10, 12, 15]
        result = TradingAnalyzer.generate_signals(prices, short_period=2, long_period=4)
        self.assertIn("signals", result)
        self.assertIsInstance(result["signals"], list)


def run_self_test():
    print("Running automated self-tests...")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTradingAnalyzer)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("SELF-TEST PASSED SUCCESSFULLY.")
        sys.exit(0)
    else:
        print("SELF-TEST FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        run_self_test()
    else:
        port = 8080
        server_address = ("", port)
        httpd = http.server.HTTPServer(server_address, SimpleHTTPRequestHandler)
        print(f"Starting Micro-SaaS Trading Analyzer on http://localhost:{port}")
        print("Test endpoint: http://localhost:8080/api/analyze?prices=10,12,11,14,13,16,18")
        print("Run with '--self-test' to execute automated verification.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server gracefully.")
            httpd.server_close()