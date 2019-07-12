import json
import flask
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Response, request
from flask_restful import Resource
from mealplan import utils, db, models, api
import datetime



class RecipeItem(Resource):

    def get(self, recipe_id):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "wrong method", "GET method required")
        db_recipe = models.Recipe.query.filter_by(id=recipe_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(recipe_id))
        if db_recipe.nutrition_information is None:
            servingSize = None
            servingSizeUnit = None
        else:
            servingSize = db_recipe.nutrition_information.servingSize
            servingSizeUnit = db_recipe.nutrition_information.servingSizeUnit

        body = utils.RecipeBuilder(
            name=db_recipe.name,
            description=db_recipe.description,
            recipeYield=db_recipe.recipeYield,
            cookTime=db_recipe.cookTime,
            recipeCategory=db_recipe.recipeCategory,
            author=db_recipe.author,
            datePublished=str(db_recipe.datePublished),
            number_of_likes = db_recipe.number_of_likes,
            servingSize=servingSize,
            servingSizeUnit=servingSizeUnit
        )
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

    def put(self, recipe_id):
        if request.method != "PUT":
            return utils.RecipeBuilder.create_error_response(405, "wrong method", "POST method required")
        db_recipe = models.Recipe.query.filter_by(id=recipe_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not found", "No recipe was found with the name {}".format(recipe_id))
        try:
            name = str(request.json["name"])
            description = str(request.json["description"])
            recipeYield = str(request.json["recipeyield"])
            cookTime = str(request.json["cooktime"])
            recipeCategory = str(request.json["category"])
            author = str(request.json["author"])
            datePublished = datetime.datetime.now()
        except KeyError:
            return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
        except ValueError:
            return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Weight and price must be numbers")
        except TypeError:
            return utils.RecipeBuilder.create_error_response(415, "Invalid content", "request content type must be JSON")
        if db_recipe.nutrition_information is None:
            servingSize = None
            servingSizeUnit = None
        else:
            servingSize = db_recipe.nutrition_information.servingSize
            servingSizeUnit = db_recipe.nutrition_information.servingSizeUnit

        body = utils.RecipeBuilder(
            name=db_recipe.name,
            description=db_recipe.description,
            recipeYield=db_recipe.recipeYield,
            cookTime=db_recipe.cookTime,
            recipeCategory=db_recipe.recipeCategory,
            author=db_recipe.author,
            datePublished=str(db_recipe.datePublished),
            number_of_likes=db_recipe.number_of_likes,
            servingSize=servingSize,
            servingSizeUnit=servingSizeUnit
        )

        db_recipe.name = name
        db_recipe.description = description
        db_recipe.recipeYield = name
        db_recipe.cookTime = name
        db_recipe.recipeCategory = name
        db_recipe.author = author
        db_recipe.datePublished = datePublished

        db.session.commit()
        url = api.api.url_for(RecipeItem, id=db_recipe.id)
        return Response(headers={
            "Location": url
        },
            status=204
        )

    def delete(self, recipe_id):
        if request.method != "DELETE":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "DELETE method required")
        db_recipe = models.Recipe.query.filter_by(id=recipe_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(recipe_id))
        if db_recipe.nutrition_information is None:
            servingSize = None
            servingSizeUnit = None
        else:
            servingSize = db_recipe.nutrition_information.servingSize
            servingSizeUnit = db_recipe.nutrition_information.servingSizeUnit

        body = utils.RecipeBuilder(
            name=db_recipe.name,
            description=db_recipe.description,
            recipeYield=db_recipe.recipeYield,
            cookTime=db_recipe.cookTime,
            recipeCategory=db_recipe.recipeCategory,
            author=db_recipe.author,
            datePublished=str(db_recipe.datePublished),
            number_of_likes=db_recipe.number_of_likes,
            servingSize=servingSize,
            servingSizeUnit=servingSizeUnit
        )

        db.session.delete(db_recipe)
        db.session.commit()
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

class RecipeCollection(Resource):

    def get(self):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "GET method required")
        recipes = db.session.query(models.Recipe).all()
        body = utils.RecipeBuilder(recipes=[])
        for recipe in recipes:
            if recipe.nutrition_information is None:
                servingSize = None
                servingSizeUnit = None
            else:
                servingSize = recipe.nutrition_information.servingSize
                servingSizeUnit = recipe.nutrition_information.servingSizeUnit

            item = utils.RecipeBuilder(
                name = recipe.name,
                description = recipe.description,
                recipeYield = recipe.recipeYield,
                cookTime = recipe.cookTime,
                recipeCategory = recipe.recipeCategory,
                author = recipe.author,
                datePublished = str(recipe.datePublished),
                number_of_likes = recipe.number_of_likes,
                servingSize = servingSize,
                servingSizeUnit = servingSizeUnit
            )
            body["recipes"].append(item)

        return Response(json.dumps(body), 200, mimetype=utils.MASON)
    def post(recipe):
        if request.method != "POST":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "POST method required")
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
        nutrition=None
        try:
            servingSize = int(request.json["servingsize"])
            servingSizeUnit = str(request.json["servingsizeunit"])
        except KeyError:
            pass
        except ValueError:
            return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Weight and price must be numbers")
        except TypeError:
            return utils.RecipeBuilder.create_error_response(415, "Invalid content", "request content type must be JSON")
        else:
            nutrition = models.NutritionInformation(
                servingSize=servingSize,
                servingSizeUnit=servingSizeUnit
            )

        recipe = models.Recipe(
            name=name,
            description= description,
            recipeYield = recipeYield,
            cookTime = cookTime,
            recipeCategory = recipeCategory,
            author = author,
            datePublished = datePublished,
            number_of_likes = 0, # Number of likes is always 0 for a new recipe
            nutrition_information = nutrition
        )
        db.session.add(recipe)
        db.session.commit()
        db.session.refresh(recipe)
        id = recipe.id
        url = api.api.url_for(RecipeItem, recipe_id=recipe.id)
        return Response(headers={
            "Location": url
        },
            status=204
        )

