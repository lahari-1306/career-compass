import unittest
import json
from app import app

class CareerCompassTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CAREER COMPASS', response.data)
        self.assertIn(b'FIND YOUR TRUE NORTH', response.data)

    def test_active_notifications_ticker(self):
        response = self.app.get('/api/notifications')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_active', data)
        self.assertIn('notifications', data)
        # Verify that active notifications have dynamic_status
        for notif in data['notifications']:
            self.assertTrue(notif['is_active_for_ticker'])
            self.assertIn(notif['dynamic_status'], ['OPEN', 'LIVE', 'CLOSING_SOON', 'RESULT'])

    def test_all_notifications(self):
        response = self.app.get('/api/notifications/all')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(data['total'], 0)

    def test_career_paths(self):
        response = self.app.get('/api/career-paths')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('10th', data)
        self.assertIn('intermediate', data)
        self.assertIn('diploma', data)
        self.assertIn('degree', data)
        self.assertIn('btech', data)
        self.assertIn('postgraduate', data)
        self.assertIn('other', data)

    def test_defence_entries(self):
        response = self.app.get('/api/defence-entries')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)
        nda = next((d for d in data if d['id'] == 'def-nda'), None)
        self.assertIsNotNone(nda)
        self.assertIn('UPSC', nda['organization'])

    def test_govt_engineering(self):
        response = self.app.get('/api/govt-engineering-jobs')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)
        gate = next((g for g in data if g['id'] == 'govt-gate'), None)
        self.assertIsNotNone(gate)

    def test_entrance_exams(self):
        response = self.app.get('/api/entrance-exams')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

    def test_colleges_and_cutoffs(self):
        response = self.app.get('/api/colleges')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

        response_cutoffs = self.app.get('/api/cutoffs')
        self.assertEqual(response_cutoffs.status_code, 200)
        cutoffs_data = json.loads(response_cutoffs.data)
        self.assertIn('disclaimer', cutoffs_data)
        self.assertIn('Previous-year cutoffs are for reference only', cutoffs_data['disclaimer'])

    def test_scholarships(self):
        response = self.app.get('/api/scholarships')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

    def test_digital_library(self):
        response = self.app.get('/api/digital-library')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

    def test_official_links(self):
        response = self.app.get('/api/official-links')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

    def test_ai_fallback_chat(self):
        # 1. 10th Query
        res1 = self.app.post('/api/ai/chat', json={'message': 'What can I do after 10th?', 'profile': {'qualification': '10th'}})
        self.assertEqual(res1.status_code, 200)
        d1 = json.loads(res1.data)
        self.assertEqual(d1['status'], 'success')
        self.assertIn('roadmap', d1['data'])

        # 2. Defence Query
        res2 = self.app.post('/api/ai/chat', json={'message': 'I want to join Defence. Which exams can I write?', 'profile': {}})
        self.assertEqual(res2.status_code, 200)
        d2 = json.loads(res2.data)
        self.assertIn('Armed Forces', d2['data']['title'])

        # 3. Diploma Query
        res3 = self.app.post('/api/ai/chat', json={'message': 'What can I do after Diploma?', 'profile': {'qualification': 'Diploma'}})
        self.assertEqual(res3.status_code, 200)
        d3 = json.loads(res3.data)
        self.assertIn('Diploma', d3['data']['title'])

        # 4. B.Tech Query
        res4 = self.app.post('/api/ai/chat', json={'message': 'B.Tech CSE career options', 'profile': {'qualification': 'B.Tech', 'branch': 'CSE'}})
        self.assertEqual(res4.status_code, 200)
        d4 = json.loads(res4.data)
        self.assertIn('Engineers', d4['data']['title'])

if __name__ == '__main__':
    unittest.main()

