import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def paginate_books(request, selection):
  page = request.args.get("page", 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  
  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add(
      "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
      "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    )
    return response

  # Handle GET requests for all available categories.
  @app.route("/categories", methods=["GET"])
  # @cross_origin
  def get_categories():
    categories = Category.query.order_by('id').all()
    categoriesMap = dict((category.id, category.type) for category in categories)
    if len(categoriesMap) ==0:
      abort(404)
    else:
      return jsonify(
        {
          "success": True,
          "categories":categoriesMap,
        }
      )

  # Handle GET requests for all available questions.
  @app.route("/questions", methods=["GET"])
  # @cross_origin
  def get_questions():
    questions = Question.query.order_by('id').all()
    current_questions = paginate_books(request, questions)
    categories = Category.query.order_by('id').all()
    categoriesMap = dict((category.id, category.type) for category in categories)
    if len(current_questions) ==0:
      abort(404)
    else:
      return jsonify(
        {
          "success": True,
          "questions": current_questions,
          "total_questions": len(questions),
          "categories":categoriesMap,
          "current_category":"",
        }
      )

  # DELETE question using a question ID.      
  @app.route("/questions/<int:question_id>", methods=["DELETE"])
  # @cross_origin
  def delete_question(question_id):  
    try:      
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
          abort(404)
    
      question.delete()
      questions = Question.query.order_by('id').all()
      current_questions = paginate_books(request, questions)
      categories = Category.query.order_by('id').all()
      categoriesMap = dict((category.id, category.type) for category in categories)
      return jsonify(
        {
          "success": True,
          "deleted": question_id,
          "questions": current_questions,
          "total_questions": len(questions),
          "categories":categoriesMap,
          "current_category":"",
        }
      )
    except:
      abort(422)
    finally:
      db.session.close()

  @app.route("/questions", methods=["POST"])
  # POST a new question, seach for a string
  def create_question():
    body = request.get_json()
    
    new_question = body.get("question",None)
    answer = body.get("answer", None)
    difficulty = body.get("difficulty", None)
    category = body.get("category", None)
    searchStr = body.get("searchTerm", None)


    if searchStr == None and (new_question == "" or answer == "") : 
      print("in here")
      abort(400)

    try:
      if searchStr:     
        questions = Question.query.filter(Question.question.ilike('%'+searchStr+'%')).all()
        current_questions = paginate_books(request, questions)
        return jsonify(
          {
            "success": True,
            "questions": current_questions,
            "total_questions": len(questions),
          }
        )
      else:
        added_question = Question( question = new_question, answer = answer, difficulty = difficulty, category = category )
        added_question.insert()

        return jsonify(
          {
            "success": True,
            'created': added_question.id, 
          }
        )
    except:
        abort(422)     
    finally:
      db.session.close()   

  # Get questions based on category. 
  @app.route("/categories/<int:category_id>/questions", methods=["GET"])
  # @cross_origin
  def get_questions_in_category(category_id):
    questions = Question.query.filter(Question.category == category_id).order_by('id').all()
    current_questions = paginate_books(request, questions)
    categories = Category.query.order_by('id').all()
    categoriesMap = dict((category.id, category.type) for category in categories)    
    return jsonify(
      {
        "success": True,
        "questions": current_questions,
        "total_questions": len(questions),
        "categories":categoriesMap,
        "current_category":category_id,
      }
    )



  @app.route("/quizzes", methods=["POST"])
  # get questions to play the quiz.
  def next_question_in_quiz():
    body = request.get_json()
    
    previous_questions  = body.get("previous_questions",[])
    category = body.get("quiz_category", None)
    if category['id'] == '0':
      questions = Question.query.order_by('id').filter(Question.id.notin_((previous_questions))).all()
    else:
      questions = Question.query.filter(
        Question.category == category['id'], 
        Question.id.notin_((previous_questions))).all()


    print(len(questions))
    newQuestion = None
    if len(questions) == 1:
      newQuestion = questions[0].format()
    elif len(questions) > 1:
      randomIndex=random.randint(0, len(questions)-1)
      newQuestion = questions[randomIndex].format()
      
    return jsonify(
      {
        "success": True,
        "question": newQuestion,
      }
    )

  #error handlers 
  @app.errorhandler(400)
  def bad_request(err):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }), 400
  
  @app.errorhandler(404)
  def not_found(err):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not Found"
    }), 404

  @app.errorhandler(405)
  def not_allowed(err):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
    }), 405
      
  @app.errorhandler(422)
  def unprocessable(err):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
    }), 422

  return app

    