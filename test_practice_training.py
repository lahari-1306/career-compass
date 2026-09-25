import unittest
import json
import urllib.parse
from app import app
from db_repository import PracticeTrainingRepository, LearningResourceRepository

class TestPracticeTraining(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.repo = PracticeTrainingRepository()
        self.resource_repo = LearningResourceRepository()

    def test_categories_endpoint(self):
        """Verify categories endpoint returns structured categories with counts."""
        res = self.client.get('/api/practice-training/categories?qualification=B.Tech')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get('success'))
        categories = data.get('categories', [])
        self.assertGreater(len(categories), 5)
        
        cat_names = [c['name'] for c in categories]
        # Must include all requested categories
        expected = [
            'Coding and CS Fundamentals',
            'Placement Preparation',
            'Aptitude',
            'Reasoning',
            'Interview Preparation',
            'Engineering Preparation',
            'Skill Development',
            'Web Development',
            'AI and Data Science'
        ]
        normalized_cat_names = [c.replace(' & ', ' and ') for c in cat_names]
        for exp in expected:
            self.assertIn(exp.replace(' & ', ' and '), normalized_cat_names, f"Expected category '{exp}' in categories list")

    def test_qualification_adaptive_categories(self):
        """Verify categories adapt to qualification level."""
        # 10th Standard
        res_10th = self.client.get('/api/practice-training/categories?qualification=10th+Standard')
        data_10th = json.loads(res_10th.data)
        names_10th = [c['name'] for c in data_10th.get('categories', [])]
        self.assertIn('School & Foundation Learning', names_10th)

        # Intermediate
        res_inter = self.client.get('/api/practice-training/categories?qualification=Intermediate+%2F+12th')
        data_inter = json.loads(res_inter.data)
        names_inter = [c['name'] for c in data_inter.get('categories', [])]
        self.assertIn('Entrance Exams', names_inter)

        # Diploma
        res_diploma = self.client.get('/api/practice-training/categories?qualification=Diploma')
        data_diploma = json.loads(res_diploma.data)
        names_diploma = [c['name'] for c in data_diploma.get('categories', [])]
        self.assertIn('Lateral Entry (ECET)', names_diploma)

    def test_all_core_categories_have_functional_content(self):
        """Verify all 9 requested categories have topics, cheat sheets, notes, verified links, and MCQs."""
        core_categories = [
            'Coding and CS Fundamentals',
            'Placement Preparation',
            'Aptitude',
            'Reasoning',
            'Interview Preparation',
            'Engineering Preparation',
            'Skill Development',
            'Web Development',
            'AI and Data Science'
        ]

        total_topics = 0
        total_questions = 0

        for cat in core_categories:
            encoded_cat = urllib.parse.quote(cat)
            res = self.client.get(f'/api/practice-training/topics?category={encoded_cat}')
            self.assertEqual(res.status_code, 200, f"Failed for category: {cat}")
            data = json.loads(res.data)
            self.assertTrue(data.get('success'), f"Response success false for {cat}")
            topics = data.get('topics', [])
            self.assertGreater(len(topics), 0, f"Category '{cat}' has 0 topics! Must NOT be empty.")
            
            for t in topics:
                total_topics += 1
                self.assertTrue(t.get('title'), f"Topic missing title in {cat}")
                self.assertTrue(t.get('short_description'), f"Topic {t.get('title')} missing short description")
                self.assertTrue(t.get('level'), f"Topic {t.get('title')} missing level")
                
                # Check Key Concepts / Cheat sheet formulas
                concepts = t.get('key_concepts', [])
                self.assertIsInstance(concepts, list)
                self.assertGreater(len(concepts), 0, f"Topic {t.get('title')} has empty key concepts")
                
                # Check Study notes
                notes = t.get('study_notes', '')
                self.assertGreater(len(notes.strip()), 20, f"Topic {t.get('title')} has insufficient study notes")
                
                # Check Learning materials (verified tutorials)
                materials = t.get('learning_materials', [])
                self.assertIsInstance(materials, list)
                self.assertGreater(len(materials), 0, f"Topic {t.get('title')} has no verified tutorials")
                for m in materials:
                    self.assertTrue(m.get('url', '').startswith('https://'), f"Material URL not https: {m.get('url')}")
                    self.assertTrue(m.get('title'), f"Material missing title: {m}")

                # Check Practice questions / MCQs
                questions = t.get('practice_questions', [])
                self.assertIsInstance(questions, list)
                self.assertGreater(len(questions), 0, f"Topic {t.get('title')} has no practice questions")
                for q in questions:
                    total_questions += 1
                    self.assertTrue(q.get('id'), "Question missing ID")
                    self.assertTrue(q.get('question'), "Question missing question prompt")
                    self.assertEqual(len(q.get('options', [])), 4, f"Question {q.get('id')} must have 4 options")
                    self.assertIn(q.get('correct_index'), [0, 1, 2, 3], f"Invalid correct_index for question {q.get('id')}")
                    self.assertTrue(q.get('explanation'), f"Question {q.get('id')} missing explanation")

        print(f"\n[VERIFIED] Verified {len(core_categories)} core categories with {total_topics} topics and {total_questions} MCQs.")

    def test_quiz_endpoint(self):
        """Verify /api/practice-training/quiz returns questions."""
        res = self.client.get('/api/practice-training/quiz?category=Aptitude')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get('success'))
        self.assertGreater(len(data.get('questions', [])), 0)

    def test_submit_quiz_endpoint(self):
        """Verify submitting quiz updates progress successfully."""
        res = self.client.post('/api/practice-training/submit-quiz',
            data=json.dumps({
                'topic_id': 'apt-quant-pct',
                'score': 4,
                'total': 5,
                'practice_minutes': 15
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get('success'))

    def test_learning_resources_category_matching(self):
        """Verify learning resources are available for each category without returning 0."""
        core_categories = [
            'Coding and CS Fundamentals',
            'Placement Preparation',
            'Aptitude',
            'Reasoning',
            'Interview Preparation',
            'Engineering Preparation',
            'Skill Development',
            'Web Development',
            'AI and Data Science'
        ]
        all_resources = self.resource_repo.get_all(verification_status=None)
        self.assertGreaterEqual(len(all_resources), 31)

        # Check that verified platforms exist for each domain
        for cat in core_categories:
            matched = self.resource_repo.get_personalized(category=cat)
            self.assertGreater(len(matched), 0, f"Expected at least 1 verified learning platform for category '{cat}'")

if __name__ == '__main__':
    unittest.main()
