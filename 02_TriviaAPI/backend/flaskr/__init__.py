import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    # Take the request's arguments to get the page number
    page = request.args.get('page', 1, type=int)
    # Set the start and end based on the 'QUESTIONS_PER_PAGE'
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    # Use list slicing to select current questions
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
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        """ Get endpoint to get all the categories """
        categories = Category.query.all()
        return jsonify({
            'success': True,
            'categories': {x.id: x.type for x in categories}
        })

    @app.route('/questions', methods=['GET'])
    def get_questions():
        """ Get paginated response for questions """
        questions = Question.query.order_by(Question.id).all()
        # Get paginated data using page number as query params
        current_questions = paginate_questions(request, questions)
        # Get all the categories from db
        # categories = [x.format() for x in Category.query.all()]
        categories = Category.query.all()
        # Check if any questions present on the page
        if not len(current_questions):
            abort(404)

        # Return jsonify data
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'categories': {x.id: x.type for x in categories},
            'current_category': None
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """ Delete a question using question id """
        # Get the question by id
        question = Question.query.get(question_id)
        if question is None:
            abort(404)
        question.delete()
        return jsonify({
            'success': True,
            'deleted': question.id
        })

    @app.route('/questions', methods=['POST'])
    def post_question():
        """ Post method to add a question """
        # Get the request body
        body = request.get_json()
        # Get data from request body
        question = body.get('question')
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        category = body.get('category')
        # Check if all the required data to create the question is provided in the request
        if question is None or answer is None or difficulty is None or category is None:
            abort(400)

        category = int(category)

        try:
            # Create a question instance
            question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty
            )
            question.insert()
            return jsonify({
                'success': True,
                'created': question.id
            })
        except:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        """ Search question by search term """
        # Get the request body
        body = request.get_json()
        search_term = body.get('searchTerm')
        if search_term is None:
            abort(422)
        results = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()
        # Return json response
        return jsonify({
            'success': True,
            'questions': [question.format() for question in results],
            'total_questions': len(results),
            'current_category': None
        })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        category = Category.query.get(category_id)
        if category is None:
            abort(404)

        questions = [
            x.format()
            for x in Question.query.filter(Question.category == category_id).all()
        ]
        # Return json response
        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(questions),
            'current_category': category_id
        })

    @app.route('/quizzes', methods=['POST'])
    def play():
        # Get request body
        body = request.get_json()

        # Keys are taken from QuizView.js
        category = body.get('quiz_category')
        previous_questions = body.get('previous_questions')     # This is a list
        if not category:
            abort(422)

        # import pdb; pdb.set_trace()
        # Figure out using debug
        # category is a dict with type and id. For ALL, type is click
        if category['type'] == 'click':
            questions = Question.query.all()
        else:
            questions = Question.query.filter(Question.category == category['id']).all()

        new_questions = [x for x in questions if x.id not in previous_questions]
        next_question = random.choice(new_questions).format() if new_questions else None
        # Return JSON response
        return jsonify({
            'success': True,
            'question': next_question
        })

    # Error Handler for (404 - Not Found)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource Not Found'
        }), 404

    # Error Handler for (422 - Unprocessable)
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Not Processable'
        }), 422

    # Error Handler for (400 - Bad Request)
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
        }), 400

    # Error Handler for (500 - Internal Server Error)
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500

    # Error Handler for (405 - Method Not Allowed)
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method Not Allowed'
        }), 405

    return app
