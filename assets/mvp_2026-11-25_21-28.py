#!/usr/bin/env python3
"""
Eluna Core MVP: Couples Cycle & Behavioral Insights Engine
Author: Autonomous Agent
Usage: python3 eluna_mvp.py [--self-test]
"""

import sys
import json
import http.server
import socketserver
from datetime import datetime, timedelta

class CycleAnalyzer:
    """محرك تحليل الدورة الشهرية وتقديم رؤى سلوكية للأزواج"""
    
    @staticmethod
    def calculate_phase(cycle_day: int) -> dict:
        if 1 <= cycle_day <= 5:
            return {"phase": "Menstrual", "behavioral_tip": "منح مساحة للراحة وتقديم دعم عاطفي إضافي."}
        elif 6 <= cycle_day <= 13:
            return {"phase": "Follicular", "behavioral_tip":ارات طاقة عالية، وقت ممتاز للتخطيط لأنشطة مشتركة."}
        elif 14 <= cycle_day <= 16:
            return {"phase": "Ovulation", "behavioral_tip": "ذروة التواصل الاجتماعي، المزاج غالباً إيجابي ومشرق."}
        else:
            return {"phase": "Luteal", "behavioral_tip": "احتمالية تقلبات مزاجية، الصبر وتجنب النقاشات الحادة مطلوب."}

    @classmethod
    def get_couple_insight(cls, last_period_str: str, current_date_str: str) -> dict:
        last_date = datetime.strptime(last_period_str, "%Y-%m-%d")
        curr_date = datetime.strptime(current_date_str, "%Y-%m-%d")
        day_diff = (curr_date - last_date).days
        cycle_day = (day_diff % 28) + 1  # افتراض دورة نموذجية 28 يوم
        
        phase_info = cls.calculate_phase(cycle_day)
        return {
            "cycle_day": cycle_day,
            "phase": phase_info["phase"],
            "partner_guidance": phase_info["behavioral_tip"],
            "timestamp": datetime.now().isoformat()
        }

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/insight"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            # مثال تجريبي لطلب افتراضي
            result = CycleAnalyzer.get_couple_insight("2023-10-01", datetime.now().strftime("%Y-%m-%d"))
            response = json.dumps({"status": "success", "data": result}, ensure_ascii=False)
            self.wfile.write(response.encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = "<h3>Eluna Micro-SaaS API is Running. Use /api/insight</h3>"
            self.wfile.write(html.encode("utf-8"))
            
    def log_message(self, format, *args):
        # تعطيل السجلات الافتراضية لتقليل الإزعاج أثناء الاختبار
        return

def run_self_test():
    print("[*] بدء الاختبار الذاتي لنواة Eluna MVP...")
    
    # اختبار حساب المراحل السلوكية
    test_day_1 = CycleAnalyzer.calculate_phase(3)
    assert test_day_1["phase"] == "Menstrual", "خطأ في حساب مرحلة الطمث"
    
    test_day_2 = CycleAnalyzer.calculate_phase(14)
    assert test_day_2["phase"] == "Ovulation", "خطأ في حساب مرحلة الإباضة"
    
    # اختبار تحليل الأزواج الشامل
    today = datetime.now().strftime("%Y-%m-%d")
    insight = CycleAnalyzer.get_couple_insight(today, today)
    assert "partner_guidance" in insight, "التوجيه السلوكي مفقود"
    assert "cycle_day" in insight, "يوم الدورة مفقود"
    
    print("[✓] نجح الاختبار الذاتي بنجاح تام! الكود جاهز للإنتاج التجريبي.")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        success = run_self_test()
        sys.exit(0 if success else 1)
    else:
        PORT = 8080
        with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
            print(f"[*] خادم Eluna يعمل الآن على المنفذ {PORT}...")
            print(f"[*] جرب زيارة: http://localhost:{PORT}/api/insight")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[*] إيقاف الخادم بأمان.")