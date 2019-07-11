import json
import flask
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Response, request
from flask_restful import Resource
from mealplan import utils

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
        db_user = User.query.filter_by(id=user_id).first()
        if db_user is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(user))

    def put(self, user):
        pass

    def delete(self, user):
        pass

    def post(self):
        pass

