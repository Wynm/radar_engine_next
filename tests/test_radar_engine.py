import tempfile
import unittest
from pathlib import Path

import radar_engine
from radar.security import review


class RadarTests(unittest.TestCase):
    def test_stable_ids(self):
        self.assertEqual(radar_engine.stable_id("ph", "url"), radar_engine.stable_id("ph", "url"))

    def test_noise_filter(self):
        self.assertTrue(radar_engine.is_noise("ROBLOX project"))
        self.assertFalse(radar_engine.is_noise("workflow automation"))

    def test_security_result_is_not_a_certification(self):
        self.assertIn("eval", radar_engine.security_review("eval(user_input)"))
        self.assertIn("not a safety guarantee", radar_engine.security_review("normal text"))
        self.assertIn("not a safety guarantee", review("normal text"))

    def test_legacy_memory_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.json"
            path.write_text('["hn_12"]', encoding="utf-8")
            memory = radar_engine.load_memory(path)
            self.assertIn("hn_12", memory)
            radar_engine.save_memory(memory, path)
            self.assertIsInstance(radar_engine.load_memory(path), dict)

    def test_telegram_html_escaping(self):
        self.assertEqual(radar_engine.html.escape("<b>x</b>"), "&lt;b&gt;x&lt;/b&gt;")


if __name__ == "__main__":
    unittest.main()
