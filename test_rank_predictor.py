import unittest
import json
import os
from app import app

class TestRankPredictor(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_intermediate_career_paths_has_eamcet_and_rank_predictor(self):
        """Verify Intermediate career pathways contain EAMCET and Rank Predictor card."""
        res = self.client.get('/api/career-paths')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('intermediate', data)
        inter = data['intermediate']
        paths = inter.get('paths', [])
        
        # Check EAMCET pathway exists
        eamcet_path = next((p for p in paths if p.get('id') == 'inter-eamcet'), None)
        self.assertIsNotNone(eamcet_path, "inter-eamcet pathway missing in intermediate")
        self.assertIn("EAMCET", eamcet_path.get('category'))
        
        # Check Rank Predictor card exists
        predictor_path = next((p for p in paths if p.get('id') == 'inter-eamcet-rank-predictor'), None)
        self.assertIsNotNone(predictor_path, "Rank Predictor card missing under EAMCET in intermediate")
        
        self.assertEqual(predictor_path.get('title'), 'Rank Predictor')
        self.assertIn('Predict your EAMCET rank', predictor_path.get('details', ''))
        self.assertEqual(predictor_path.get('official_url'), 'https://aptsrank.in/')
        self.assertEqual(predictor_path.get('button_text'), 'Open Rank Predictor')
        self.assertIn('Rank and college predictions are estimates', predictor_path.get('disclaimer', ''))

    def test_entrance_exams_has_rank_predictor(self):
        """Verify State EAPCET / EAMCET in entrance exams has rank predictor metadata."""
        res = self.client.get('/api/entrance-exams')
        self.assertEqual(res.status_code, 200)
        exams = json.loads(res.data)
        
        eapcet = next((e for e in exams if e.get('id') == 'exam-eapcet'), None)
        self.assertIsNotNone(eapcet, "exam-eapcet missing in entrance exams")
        self.assertIn('rank_predictor', eapcet)
        rp = eapcet['rank_predictor']
        self.assertEqual(rp.get('url'), 'https://aptsrank.in/')
        self.assertEqual(rp.get('button_text'), 'Open Rank Predictor')
        self.assertIn('historical cutoff data', rp.get('disclaimer', ''))

if __name__ == '__main__':
    unittest.main()
