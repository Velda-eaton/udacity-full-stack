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

        self.new_question={
            "question":'In what movie does the line, “My name is Inigo Montoya. You killed my father. Prepare to die.”, come from?', 
            "answer":"The Princess Bride", 
            "difficulty": 3, 
            "category": 5
        }
        
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_404_when_url(self):        
        res = self.client().delete('/invalid/url')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], "resource not Found")

    def test_get_questions_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
    
    def test_get_pagation_questions(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], "")

    def test_get_pagation_questions_past_valid(self):
        res = self.client().get('/questions?page=200')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], "resource not Found")

    def test_delete_question(self):        
        res = self.client().delete('/questions/6')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 6).one_or_none()
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],6)
        self.assertEqual(question,None)

    def test_422_when_no_resource_to_delete(self):        
        res = self.client().delete('/questions/200')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], "unprocessable")

    def test_insert_question(self):        
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['created'])


    def test_400_insert_without_question(self):    
        noQuestion={
            "question":'', 
            "answer":"1790", 
            "difficulty": 5, 
            "category": 4
        }    
        res = self.client().post('/questions', json=noQuestion)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], "bad request")
        
    def test_400_insert_without_answer(self):  
        
        noAnswer={
            "question":'When was the first sewing machine invented?', 
            "answer":"", 
            "difficulty": 5, 
            "category": 4
        }      
        res = self.client().post('/questions', json=noAnswer)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], "bad request")

    def test_405_if_question_creation_not_allowed(self):        
        res = self.client().post("/questions/45", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], "method not allowed")

    def test_get_questions_in_categories(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], 4)

    
    def test_category_search_without_results(self):        
        res = self.client().get("/categories/400/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(len(data['questions']),0)
        self.assertEqual(data['total_questions'],0)
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'], 400)

    def test_question_search_with_results(self):        
        res = self.client().post('/questions', json={'searchTerm': 'Artist'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(len(data['questions']),2)
        self.assertEqual(data['total_questions'],2)

    def test_question_search_without_results(self):        
        res = self.client().post("/questions", json={'searchTerm': 'No search results'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(len(data['questions']),0)
        self.assertEqual(data['total_questions'],0)
    
    def test_next_random_question_with_category(self):         
        res = self.client().post('/quizzes', json={"previous_questions": [13], "quiz_category": {"type": "Geography", "id": "3"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])

    def test_no_more_random_questions_with_category(self):      
        res = self.client().post('/quizzes', json={"previous_questions": [13, 14, 15], "quiz_category": {"type": "Geography", "id": "3"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['question'],None)

    def test_next_random_question_without_category(self):        
        res = self.client().post('/quizzes', json={"previous_questions": [2, 20, 5], "quiz_category": {"type": "click", "id": "0"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()