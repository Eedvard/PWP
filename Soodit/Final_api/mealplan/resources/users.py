import json
import flask
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Response, request
from flask_restful import Resource
from mealplan import utils, db, models, api
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)


class Users(Resource):

    def get(self, user_id):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "Wrong method", "GET method required")
        db_user = models.User.query.filter_by(id=user_id).first()
        if db_user is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(user_id))

        body = utils.RecipeBuilder(
            username=db_user.username
        )
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

    def put(self, user_id):
        if request.method != "PUT":
            return utils.RecipeBuilder.create_error_response(405, "Wrong method", "PUT method required")
        db_user = models.User.query.filter_by(id=user_id).first()
        if db_user is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(user_id))
        try:
            username = str(request.json["username"])
        except KeyError:
            return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
        except ValueError:
            return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Username must be a string")
        except TypeError:
            return utils.RecipeBuilder.create_error_response(415, "Invalid content", "Request content must be JSON")

        body = utils.RecipeBuilder(
            username=db_user.username
        )

        db_user.username = username

        db.session.commit()
        url = api.api.url_for(User, user_id=user_id)
        return Response(headers={
            "Location": url
        },
            status=204
        )

    def delete(self, user):
        pass

    def post(self):
        pass

