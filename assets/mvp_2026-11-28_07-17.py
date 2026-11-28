import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class ChickyTutorCore:
    """نواة خدمة تخصيص تعلم اللغات بناءً على اهتمامات المستخدم وسياقه اليومي."""
    def __init__(self):
        self.user_profiles = {}

    def create_profile(self, user_id, target_lang, interests):
        self.user_profiles[user_id] = {
            "lang": target_lang,
            "interests": interests,
            "lessons_generated": 0
        }
        return {"status": "success", "message": f"Profile created for {user_id}"}

    def generate_lesson(self, user_id):
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {"error": "User profile not found"}
        
        profile["lessons_generated"] += 1
        lang = profile["lang"]
        interest = profile["interests"][0] if profile["interests"] else "general"
        
        # محاكاة لتوليد محتوى مخصص بناءً على اهتمامات المستخدم
        lesson = {
            "lesson_id": profile["lessons_generated"],
            "language": lang,
            "context": f"Learning {lang} through your interest in {interest}",
            "content": f"Sample dynamic sentence in {lang} about {interest}."
        }
        return lesson

# خادم مصغر لتقديم الخدمة عبر HTTP
tutor_engine = ChickyTutorCore()

class SimpleSaaSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        if path == "/api/profile":
            user_id = query.get("user_id", ["default_user"])[0]
            lang = query.get("lang", ["Spanish"])[0]
            interests = query.get("interests", ["tech,travel"])[0].split(",")
            
            result = tutor_engine.create_profile(user_id, lang, interests)
            self._send_json(result)
            
        elif path == "/api/lesson":
            user_id = query.get("user_id", ["default_user"])[0]
            if user_id not in tutor_engine.user_profiles:
                tutor_engine.create_profile(user_id, "Spanish", ["coding"])
                
            result = tutor_engine.generate_lesson(user_id)
            self._send_json(result)
        else:
            self._send_json({"error": "Endpoint not found. Use /api/profile or /api/lesson"}, 404)

    def _send_json(self, data, status=200):
        response = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        # تعطيل طباعة السجلات لتبسيط مخرجات الاختبار الذاتي
        pass

def run_self_test():
    print("Running ChickyTutor Micro-SaaS Self-Test...")
    engine = ChickyTutorCore()
    
    # اختبار إنشاء الملف الشخصي
    res_profile = engine.create_profile("tester_1", "French", ["cooking", "music"])
    assert res_profile["status"] == "success", "Profile creation failed"
    
    # اختبار توليد الدرس المخصص
    lesson = engine.generate_lesson("tester_1")
    assert lesson["language"] == "French", "Language mismatch"
    assert "cooking" in lesson["context"], "Context personalization failed"
    
    print("[SUCCESS] All self-tests passed successfully!")

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        run_self_test()
    else:
        server_address = ('', 8080)
        httpd = HTTPServer(server_address, SimpleSaaSHandler)
        print("ChickyTutor Micro-SaaS running on port 8080...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass