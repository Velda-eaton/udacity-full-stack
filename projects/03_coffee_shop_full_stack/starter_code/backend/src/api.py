import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES


# Public endpoint, continaing drink.short()
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.order_by('id').all()
    prettyDrinks = [drink.short() for drink in drinks]
    if len(prettyDrinks) == 0:
        abort(404)
    else:
        return jsonify(
            {
                "success": True,
                "drinks": prettyDrinks,
            }
        )


# restricted endpoint, returns drink.long()
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.order_by('id').all()
    prettyDrinks = [drink.long() for drink in drinks]
    if len(prettyDrinks) == 0:
        abort(404)
    else:
        return jsonify(
            {
                "success": True,
                "drinks": prettyDrinks,
            }
        )


# restricted endpoint, insert a drink and return it's long formatt
@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    newDrink = body.get("title", None)
    recipe = body.get("recipe", None)
    if newDrink is None or newDrink == "" or recipe is None:
        abort(400)
    try:
        drink = Drink(title=newDrink, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify(
            {
                "success": True,
                "drinks": drink.long(),
            }
        )
    except:
        print(sys.exc_info())
        abort(422)


# restricted endpoint, update a drink given the id
@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    body = request.get_json()
    newTitle = body.get("title", None)
    recipe = body.get("recipe", None)
    if (newTitle is None or newTitle == "") and \
        (recipe is None or recipe == ""):
            abort(400)
    try:
        drink = Drink.query.get_or_404(drink_id)
        if newTitle is not None or newTitle != "":
            drink.title = newTitle
        if recipe is not None or recipe != "":
            drink.recipe = json.dumps(recipe)
        drink.update()

        return jsonify(
            {
                "success": True,
                "drinks": [drink.long()],
            }
        )
    except:
        print(sys.exc_info())
        abort(422)


# restricted endpoint.  DELETE drink using a given ID.
@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_question(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()

        return jsonify(
            {
                "success": True,
                "delete": drink_id,
            }
            )
    except:
        abort(422)


# error handlers
@app.errorhandler(400)
def bad_request(err):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(AuthError)
def auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


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
