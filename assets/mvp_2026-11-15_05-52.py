import sys
import json
import urllib.request
import urllib.error

class PolymarketEdgeAnalyzer:
    """
    محلل فجوات احتمالية مبسط لمنصة Polymarket (MVP)
    يقوم بحساب الفجوة بين الاحتمال المتوقع والسعر المعروض في السوق لاكتشاف فرص المراجحة.
    """
    def __init__(self, markets_data=None):
        self.markets_data = markets_data or [
            {"id": "market-1", "question": "Will BTC exceed $100k?", "yes_price": 0.45, "true_probability": 0.55},
            {"id": "market-2", "question": "Will ETH upgrade succeed?", "yes_price": 0.80, "true_probability": 0.75},
            {"id": "market-3", "question": "Will AI regulation pass in 2025?", "yes_price": 0.30, "true_probability": 0.42}
        ]

    def scan_for_edges(self, min_edge=0.05):
        """يكشف عن الفجوات التي تتجاوز الحد الأدنى المطلوب للاستثمار"""
        opportunities = []
        for market in self.markets_data:
            price = market["yes_price"]
            true_prob = market["true_probability"]
            edge = true_prob - price
            
            if abs(edge) >= min_edge:
                recommendation = "BUY YES" if edge > 0 else "BUY NO"
                opportunities.append({
                    "id": market["id"],
                    "question": market["question"],
                    "market_price": price,
                    "true_probability": true_prob,
                    "edge": round(edge, 4),
                    "recommendation": recommendation
                })
        return opportunities

    def run_self_test(self):
        """تنفيذ اختبار ذاتي للتحقق من سلامة خوارزمية كشف الفجوات"""
        print("[*] Running Polymarket Analyzer Self-Test...")
        results = self.scan_for_edges(min_edge=0.05)
        
        assert isinstance(results, list), "Error: Output must be a list."
        # نتوقع العثور على السوق 1 و 3 بناءً على البيانات الافتراضية
        assert len(results) >= 2, "Error: Expected at least 2 trading opportunities."
        
        print("[+] Self-Test Passed Successfully!")
        print(f"[+] Detected {len(results)} profitable edges.")
        for opp in results:
            print(f"    - Market: {opp['question']} | Action: {opp['recommendation']} | Edge: {opp['edge']}")
        return True

if __name__ == "__main__":
    analyzer = PolymarketEdgeAnalyzer()
    
    if "--self-test" in sys.argv:
        success = analyzer.run_self_test()
        sys.exit(0 if success else 1)
    else:
        print("[*] Running standard scan...")
        ops = analyzer.scan_for_edges()
        print(json.dumps(ops, indent=2))