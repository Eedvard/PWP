import json
import flask
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Response, request
from flask_restful import Resource
from mealplan import utils, db, models


class RecipeItem(Resource):

    def get(self, recipe_id):
        db_recipe = models.Recipe.query.filter_by(id=recipe_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(recipe_id))

    def put(self, user):
        pass

    def delete(self, user):
        pass

class RecipeCollection(Resource):

    def get(self):
        db_recipe = db.session.query(models.Recipe).all()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username")
    def post(self):
        pass

