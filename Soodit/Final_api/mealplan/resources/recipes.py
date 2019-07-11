import json
import flask
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Response, request
from flask_restful import Resource
from mealplan import utils, db, models
import datetime



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
        recipes = db.session.query(models.Recipe).all()
        body = utils.RecipeBuilder(items=[])
        for recipe in recipes:
            item = utils.RecipeBuilder(
                name = recipe.name
            )
            body["items"].append(item)

            print("ribale")
            print(recipe)
        return Response(json.dumps(body), 200, mimetype=utils.MASON)
    def post(recipe):
        if request.method != "POST":
            return "POST method required", 405
        try:
            name = str(request.json["name"])
            description = str(request.json["description"])
            recipeYield = str(request.json["recipeyield"])
            cookTime = str(request.json["cooktime"])
            recipeCategory = str(request.json["category"])
            author = str(request.json["author"])
            datePublished = datetime.datetime.now()
            #servingSize = int(request.json["servingsize"])
            #servingSizeUnit = str(request.json["servingsizeunit"])
            #weight = float(request.json["weight"])
            #price = float(request.json["price"])
        except KeyError:
            return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
        except ValueError:
            return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Weight and price must be numbers")
        except TypeError:
            return utils.RecipeBuilder.create_error_response(415, "Invalid content", "request content type must be JSON")

            # Database stuff
        recipe = models.Recipe.query.filter_by(name=name).first()
        if recipe is not None:
            return utils.RecipeBuilder.create_error_response(409, "Duplicate content", "Handle already exists")
        recipe = models.Recipe(
            name=name,
            description= description,
            recipeYield = recipeYield,
            cookTime = cookTime,
            recipeCategory = recipeCategory,
            author = author,
            datePublished = datePublished
        )
        #url = api.url_for(RecipeItem, name=name)
        db.session.add(recipe)
        db.session.commit()
        return ""

