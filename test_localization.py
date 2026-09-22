import unittest
import json
import re
from app import app

class LocalizationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('static/locales/en.json', 'r', encoding='utf-8') as f:
            cls.en = json.load(f)
        with open('static/locales/te.json', 'r', encoding='utf-8') as f:
            cls.te = json.load(f)
        with open('static/locales/hi.json', 'r', encoding='utf-8') as f:
            cls.hi = json.load(f)

    def _get_all_keys(self, d, prefix=""):
        keys = set()
        for k, v in d.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.update(self._get_all_keys(v, full_key))
            else:
                keys.add(full_key)
        return keys

    def test_key_parity(self):
        en_keys = self._get_all_keys(self.en)
        te_keys = self._get_all_keys(self.te)
        hi_keys = self._get_all_keys(self.hi)

        self.assertGreater(len(en_keys), 250, "Expected at least 250 localization keys")
        missing_in_te = en_keys - te_keys
        missing_in_hi = en_keys - hi_keys
        extra_in_te = te_keys - en_keys
        extra_in_hi = hi_keys - en_keys

        self.assertEqual(len(missing_in_te), 0, f"Keys missing in Telugu: {missing_in_te}")
        self.assertEqual(len(missing_in_hi), 0, f"Keys missing in Hindi: {missing_in_hi}")
        self.assertEqual(len(extra_in_te), 0, f"Extra keys in Telugu: {extra_in_te}")
        self.assertEqual(len(extra_in_hi), 0, f"Extra keys in Hindi: {extra_in_hi}")

    def test_telugu_characters_present(self):
        # Verify Telugu strings contain Telugu Unicode range \u0C00-\u0C7F
        telugu_regex = re.compile(r'[\u0C00-\u0C7F]')
        found_telugu = False
        for section, content in self.te.items():
            if isinstance(content, dict):
                for k, v in content.items():
                    if isinstance(v, str) and telugu_regex.search(v):
                        found_telugu = True
                        break
        self.assertTrue(found_telugu, "Telugu localization must contain Telugu script characters")

    def test_hindi_characters_present(self):
        # Verify Hindi strings contain Devanagari Unicode range \u0900-\u097F
        hindi_regex = re.compile(r'[\u0900-\u097F]')
        found_hindi = False
        for section, content in self.hi.items():
            if isinstance(content, dict):
                for k, v in content.items():
                    if isinstance(v, str) and hindi_regex.search(v):
                        found_hindi = True
                        break
        self.assertTrue(found_hindi, "Hindi localization must contain Devanagari script characters")

    def test_ai_chat_multilingual_fallback(self):
        client = app.test_client()
        client.testing = True

        # Test English AI chat response
        res_en = client.post('/api/ai/chat',
                             data=json.dumps({"message": "Tell me about defence career options", "language": "en"}),
                             content_type='application/json')
        self.assertEqual(res_en.status_code, 200)
        data_en = json.loads(res_en.data)
        self.assertEqual(data_en.get("language"), "en")

        # Test Telugu AI chat response
        res_te = client.post('/api/ai/chat',
                             data=json.dumps({"message": "Tell me about defence career options", "language": "te"}),
                             content_type='application/json')
        self.assertEqual(res_te.status_code, 200)
        data_te = json.loads(res_te.data)
        self.assertEqual(data_te.get("language"), "te")
        # Check that Telugu characters are in response title or summary
        title_or_text = str(data_te)
        self.assertTrue(bool(re.search(r'[\u0C00-\u0C7F]', title_or_text)), "Telugu response must contain Telugu characters")

        # Test Hindi AI chat response
        res_hi = client.post('/api/ai/chat',
                             data=json.dumps({"message": "Tell me about defence career options", "language": "hi"}),
                             content_type='application/json')
        self.assertEqual(res_hi.status_code, 200)
        data_hi = json.loads(res_hi.data)
        self.assertEqual(data_hi.get("language"), "hi")
        title_or_text_hi = str(data_hi)
        self.assertTrue(bool(re.search(r'[\u0900-\u097F]', title_or_text_hi)), "Hindi response must contain Devanagari characters")

if __name__ == '__main__':
    unittest.main()
