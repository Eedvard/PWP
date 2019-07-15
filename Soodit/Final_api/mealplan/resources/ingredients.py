import json
import flask
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Response, request
from flask_restful import Resource
from mealplan import utils, db, models, api
import datetime

class Ingredient(Resource):
    def get(self, recipe_id, ingredient_id):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "wrong method", "GET method required")
        db_recipe = models.RecipeIngredient.query.filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(recipe_id))

        body = utils.RecipeBuilder(
            name=db_recipe.ingredient.name,
            description=db_recipe.ingredient.description,
            amount=db_recipe.amount,
            unit=db_recipe.unit
        )
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

    def put(self, recipe_id, ingredient_id):
        if request.method != "PUT":
            return utils.RecipeBuilder.create_error_response(405, "wrong method", "PUT method required")
        db_recipe = models.RecipeInstructionStep.query.filter_by(recipe_id=recipe_id, step=ingredient_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not found", "No recipe was found with the name {}".format(recipe_id))
        try:
            name = str(request.json["name"])
            description = str(request.json["description"])
        except KeyError:
            return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
        except ValueError:
            return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Weight and price must be numbers")
        except TypeError:
            return utils.RecipeBuilder.create_error_response(415, "Invalid content", "request content type must be JSON")

        body = utils.RecipeBuilder(
            id=db_recipe.id,
            name=db_recipe.name,
            descrption=db_recipe.description,
            nutrition_information_id=db_recipe.nutrition_information_id,
            nutrition_information=db_recipe.nutrition_information
        )
        db_recipe.name=name
        db_recipe.description=description
        db.session.commit()
        url = api.api.url_for(Ingredient, recipe_id=db_recipe.recipe_id, step_id=db_recipe.step)
        return Response(headers={
            "Location": url
        },
            status=204
        )

    def delete(self, recipe_id, ingredient_id):
        if request.method != "DELETE":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "DELETE method required")
        db_recipe = models.RecipeInstructionStep.query.filter_by(recipe_id=recipe_id, step=ingredient_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(recipe_id))

        body = utils.RecipeBuilder(
            name=db_recipe.name,
            description=db_recipe.description
        )

        db.session.delete(db_recipe)
        db.session.commit()
        return Response(json.dumps(body), 200, mimetype=utils.MASON)
