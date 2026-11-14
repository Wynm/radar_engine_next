import sys
import json
import re

class STE80HumanizerMVP:
    """
    نواة برمجية مصغرة تحاكي معيار ASD-STE100 لإزالة بصمات الذكاء الاصطناعي 
    وتبسيط النصوص التقنية بدون الحاجة لأي مكتبات خارجية.
    """
    def __init__(self):
        # قائمة بالكلمات النمطية الشائعة للذكاء الاصطناعي لاستبدالها بأخرى مباشرة
        self.ai_tells = {
            r"\bdelve into\b": "explore",
            r"\bin order to\b": "to",
            r"\butilize\b": "use",
            r"\bmoreover\b": "also",
            r"\bit is important to note that\b": "",
            r"\bfoster\b": "support",
            r"\bparadigm\b": "model"
        }

    def process_text(self, text: str) -> dict:
        original_length = len(text.split())
        cleaned_text = text

        # تطبيق القواعد النمطية للتبسيط
        for pattern, replacement in self.ai_tells.items():
            cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.IGNORECASE)

        # تنظيف المسافات الزائدة الناتجة عن الحذف
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        new_length = len(cleaned_text.split())
        
        return {
            "status": "success",
            "original_words": original_length,
            "optimized_words": new_length,
            "result": cleaned_text
        }

def run_self_test():
    print("[*] بدء الاختبار الذاتي (Self-Test) لأداة STE80 Humanizer...")
    sample_input = "In order to delve into the new paradigm, it is important to note that we must utilize better tools."
    
    humanizer = STE80HumanizerMVP()
    output = humanizer.process_text(sample_input)
    
    print(f"[*] النص الأصلي: {sample_input}")
    print(f"[*] النتيجة المعالجة: {output['result']}")
    
    # التحقق من نجاح الاختبار
    assert "delve into" not in output['result'], "فشل الاختبار: لا تزال كلمة delve موجودة"
    assert "utilize" not in output['result'], "فشل الاختبار: لا تزال كلمة utilize موجودة"
    
    print("[+] نجح الاختبار الذاتي بنجاح تام! النظام جاهز للتشغيل.")
    return True

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        run_self_test()
    else:
        # مثال تشغيل سريع مباشر إذا لم يُستخدَم الوسيط
        sample = "In order to utilize this system, we must delve into the data."
        app = STE80HumanizerMVP()
        print(json.dumps(app.process_text(sample), indent=2, ensure_ascii=False))