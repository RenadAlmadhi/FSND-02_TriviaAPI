import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        """ Test GET request to categories """
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)

    def test_post_categories(self):
        """ Test POST request to categories """
        response = self.client().post('/categories')
        self.assertEqual(response.status_code, 405)

    def test_get_no_questions(self):
        """ Test GET request to questions """
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)

    def test_get_questions(self):
        """ Test GET request to get questions """
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)

    def test_delete_question(self):
        """ Test delete question """
        with self.app.app_context():
            question = Question(
                question="What is your name",
                answer="Renad",
                category=1,
                difficulty=1
            )
            self.db.session.add(question)
            self.db.session.commit()
            response = self.client().delete(f'/questions/{question.id}')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        expected_data = {
            'success': True,
            'deleted': question.id
        }
        self.assertEqual(data, expected_data)

    def test_delete_invalid_question(self):
        """ Test delete invalid question """
        response = self.client().delete('/questions/100')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

    def test_post_question_valid(self):
        """ Test post question """
        with self.app.app_context():
            category = Category(type='General')
            self.db.session.add(category)
            self.db.session.commit()
            response = self.client().post('/questions', json={
                'question': 'Whats your name',
                'answer': 'Renad',
                'difficulty': 1,
                'category': 1
            })
        self.assertEqual(response.status_code, 200)

    def test_post_question_invalid(self):
        """ Test post invalid question """
        with self.app.app_context():
            category = Category(type='General')
            self.db.session.add(category)
            self.db.session.commit()
            response = self.client().post('/questions', json={
                'question': 'Whats your name',
                'category': 1
            })
        self.assertEqual(response.status_code, 400)

    def test_search_questions(self):
        """ Test search questions """
        response = self.client().post('/questions/search', json={'searchTerm': 'autobiography'})
        data = json.loads(response.data)
        expected_data = {
            'current_category': None,
            'questions': [
                {'answer': 'Maya Angelou', 'category': 4, 'difficulty': 2, 'id': 5,
                 'question': "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"}
            ],
            'success': True,
            'total_questions': 1
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, expected_data)

    def test_search_questions_invalid(self):
        """ Test search questions """
        response = self.client().post('/questions/search', json={'other_filed': 'value'})
        self.assertEqual(response.status_code, 422)

    def test_get_category_questions(self):
        """ Test Get category questions """
        response = self.client().get('/categories/1/questions')
        self.assertEqual(response.status_code, 200)

    def test_get_category_questions_no_category(self):
        """ Test Get category questions """
        response = self.client().get('/categories/1000/questions')
        self.assertEqual(response.status_code, 404)

    def test_play_quize(self):
        """ Test play quiz """
        response = self.client().post('/quizzes', json={
            'quiz_category': {'type': 'General', 'id': '1'},
            'previous_questions': []
        })
        self.assertEqual(response.status_code, 200)

    def test_play_quize_failed(self):
        """ Test play quiz failed"""
        response = self.client().post('/quizzes', json={
            'previous_questions': []
        })
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
