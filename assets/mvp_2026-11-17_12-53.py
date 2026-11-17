import sys
import json
import urllib.request
import urllib.error
import http.server
import socketserver
import threading

# وكيل ذكاء اصطناعي وهمي ومحاكي للنقاش المالي (MVP Simulation)
class MultiAgentStockAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol.upper()

    def fetch_market_data(self):
        # محاكاة لجلب البيانات المالية (بدون الحاجة لـ pip، استخدام مكتبة القياسية)
        # في بيئة الإنتاج يتم ربطها بـ Alpha Vantage API
        return {
            "symbol": self.symbol,
            "price": 150.25,
            "pe_ratio": 24.5,
            "market_trend": "Bullish"
        }

    def agent_fundamentalist(self, data):
        if data["pe_ratio"] < 30:
            return "مقيم بأقل من قيمته الحقيقية (شراء)."
        return "سعره مرتفع (حذر)."

    def agent_technician(self, data):
        if data["market_trend"] == "Bullish":
            return "المؤشرات الفنية تدعم الاتجاه الصعودي."
        return "المؤشرات الفنية ضعيفة."

    def synthesize_decision(self):
        data = self.fetch_market_data()
        fund_opinion = self.agent_fundamentalist(data)
        tech_opinion = self.agent_technician(data)
        
        recommendation = "احتفاظ أو شراء بحذر"
        if "شراء" in fund_opinion and "صعودي" in tech_opinion:
            recommendation = "شراء قوي (Strong Buy)"

        return {
            "symbol": self.symbol,
            "data": data,
            "agents": {
                "fundamental_agent": fund_opinion,
                "technical_agent": tech_opinion
            },
            "final_recommendation": recommendation
        }

# خادم HTTP مصغر لتقديم الخدمة (Micro-SaaS Backend)
class SaaSHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/analyze?symbol="):
            symbol = self.path.split("=")[1]
            analyzer = MultiAgentStockAnalyzer(symbol)
            result = analyzer.synthesize_decision()
            
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>Trading Agents SaaS MVP</h1><p>Use /analyze?symbol=AAPL</p>")

def run_self_test():
    print("[-] بدء الاختبار الذاتي (Self-Test)...")
    analyzer = MultiAgentStockAnalyzer("AAPL")
    res = analyzer.synthesize_decision()
    print(f"[-] نتيجة تحليل السهم {res['symbol']}: {res['final_recommendation']}")
    print("[-] آراء الوكلاء:", json.dumps(res['agents'], ensure_ascii=False))
    assert "final_recommendation" in res, "فشل الاختبار الذاتي: لا يوجد توصية نهائية!"
    print("[+] نجح الاختبار الذاتي بنجاح تام!")

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        run_self_test()
    else:
        PORT = 8080
        handler = SaaSHandler
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"[+] خادم Micro-SaaS يعمل على المنطاق http://localhost:{PORT}")
            print("[+] لتنفيذ الاختبار الذاتي شغل السكربت هكذا: python script.py --self-test")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[!] إيقاف الخادم.")