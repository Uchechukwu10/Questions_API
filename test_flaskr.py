import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Question, Category
from dotenv import load_dotenv

load_dotenv()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            os.getenv("DATABASE_USER"),
            os.getenv("DATABASE_USER_PASSWORD"),
            "localhost:5432",
            self.database_name
        )

        setup_db(self.app, self.database_path)

        self.new_question = {
            "answer": "Water",
            "question": "What is H2O?",
            "difficulty": 5,
            "category": 1
        }
        self.quiz_start = {"quiz_category": 2, "previous_questions": [16, 17]}
        self.quiz_fail = {"quiz_category": 12, "previous_questions": [16, 17]}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful
    operation and for expected errors.
    """

    """Test For Get Categories"""

    def test_get_available_categories(self):
        """Test Success"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue('categories')

    def test_404_not_found_categories(self):

        res = self.client().get('/categories/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    """Test for Get Questions"""

    def test_get_questions(self):

        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        questions = Question.query.order_by(Question.id).all()
        current_page = questions[10:20]
        formatted_questions = [question.format() for question in current_page]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'], formatted_questions)
        self.assertEqual(data['total_questions'], len(questions))
        self.assertTrue('categories')

    def test_404_questions_not_found(self):

        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    """Test delete question"""

    def test_delete_book(self):

        res = self.client().delete('/questions/24')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 24).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 24)
        self.assertTrue(len(data['questions']))
        self.assertFalse(question)

    def test_404_question_does_not_exist(self):

        res = self.client().delete('/questions/400')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    """Test post new question"""

    def test_post_new_question(self):

        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_405_if_creation_not_allowed(self):

        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "method not allowed")

        """Test search questions"""

    def test_question_search_with_results(self):

        res = self.client().post(
            '/questions/search',
            json={'searchTerm': "what"}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 10)

    def test_questions_search_without_results(self):

        res = self.client().post('/questions/search', json={'searchTerm': "Uches"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)

    """Test get questions by category"""
    def test_get_questions_by_category(self):

        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], 3)

    def test_422_if_unprocessable(self):

        res = self.client().get('/categories/9/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

    """Test quiz game"""
    def test_quiz_game(self):

        res = self.client().post('/quizzes', json=self.quiz_start)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotIn(data['question']['id'], [16, 17])

    def test_422_unsuccessful_quiz_game(self):

        res = self.client().post('/quizzes', json=self.quiz_fail)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

# Make the tests conveniently executable


if __name__ == "__main__":
    unittest.main()
