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
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No recipe was found with id {}".format(recipe_id))

        if db_recipe.nutrition_information is not None:
            body = utils.RecipeBuilder(
                name=db_recipe.name,
                description=db_recipe.description,
                recipeYield=db_recipe.recipeYield,
                cookTime=db_recipe.cookTime,
                recipeCategory=db_recipe.recipeCategory,
                author=db_recipe.author,
                datePublished=str(db_recipe.datePublished),
                calories=db_recipe.nutrition_information.calories,
                carbohydrateContent=db_recipe.nutrition_information.carbohydrateContent,
                cholesterolContent=db_recipe.nutrition_information.cholesterolContent,
                fatContent=db_recipe.nutrition_information.fatContent,
                fiberContent=db_recipe.nutrition_information.fiberContent,
                proteinContent=db_recipe.nutrition_information.proteinContent,
                saturatedFatContent=db_recipe.nutrition_information.saturatedFatContent,
                sodiumContent=db_recipe.nutrition_information.sodiumContent,
                sugarContent=db_recipe.nutrition_information.sugarContent,
                transFatContent=db_recipe.nutrition_information.transFatContent,
                unsaturatedFatContent=db_recipe.nutrition_information.unsaturatedFatContent,
                steps=[],
                ingredients=[]
            )
        else:
            body = utils.RecipeBuilder(
                name=db_recipe.name,
                description=db_recipe.description,
                recipeYield=db_recipe.recipeYield,
                cookTime=db_recipe.cookTime,
                recipeCategory=db_recipe.recipeCategory,
                author=db_recipe.author,
                datePublished=str(db_recipe.datePublished),
                steps=[],
                ingredients=[]
            )
        steps = models.RecipeInstructionStep.query.filter_by(recipe_id=recipe_id).all()
        for step in steps:
            item = utils.RecipeBuilder(
                step=step.step,
                text=step.text
            )
            body["steps"].append(item)
        ingredients = models.RecipeIngredient.query.filter_by(recipe_id=recipe_id).all()
        for ingredient in ingredients:
            item = utils.RecipeBuilder(
                name=ingredient.ingredient.name,
                description=ingredient.ingredient.description,
                amount=ingredient.amount,
                unit=ingredient.unit
            )
            body["ingredients"].append(item)

        body.add_namespace("recipes", utils.LINK_RELATIONS_URL)
        body.add_control("self", api.api.url_for(RecipeItem, recipe_id=recipe_id))
        body.add_control("profile", utils.REC_PROFILE)
        body.add_control("collection", "/api/products/")
        body.add_control_delete_recipe(recipe_id)
        body.add_control_edit_recipe(recipe_id)
        body.add_control("storage:recipes-all", api.api.url_for(RecipeItem, recipe_id=recipe_id))
        body.add_control_add_recipe_ingredient(recipe_id)
        body.add_control_all_recipe_ingredients(recipe_id)
        body.add_control_add_step(recipe_id)
        body.add_control_all_steps(recipe_id)
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

    def put(self, recipe_id):
        if request.method != "PUT":
            return utils.RecipeBuilder.create_error_response(405, "wrong method", "PUT method required")
        db_recipe = models.Recipe.query.filter_by(id=recipe_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No recipe was found with id {}".format(recipe_id))
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

        body = utils.RecipeBuilder(
            name=db_recipe.name,
            description=db_recipe.description,
            recipeYield=db_recipe.recipeYield,
            cookTime=db_recipe.cookTime,
            recipeCategory=db_recipe.recipeCategory,
            author=db_recipe.author,
            datePublished=str(db_recipe.datePublished)
        )

        db_recipe.name = name
        db_recipe.description = description
        db_recipe.recipeYield = name
        db_recipe.cookTime = name
        db_recipe.recipeCategory = name
        db_recipe.author = author
        db_recipe.datePublished = datePublished

        db.session.commit()
        url = api.api.url_for(RecipeItem, recipe_id=recipe_id)
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
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No recipe was found with id {}".format(recipe_id))


        body = utils.RecipeBuilder(
            name=db_recipe.name,
            description=db_recipe.description,
            recipeYield=db_recipe.recipeYield,
            cookTime=db_recipe.cookTime,
            recipeCategory=db_recipe.recipeCategory,
            author=db_recipe.author,
            datePublished=str(db_recipe.datePublished),
        )

        db.session.delete(db_recipe)
        db.session.commit()
        return Response(json.dumps(body), 204, mimetype=utils.MASON)

class RecipeCollection(Resource):

    def get(self):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "GET method required")
        recipes = db.session.query(models.Recipe).all()
        body = utils.RecipeBuilder(recipes=[])
        for recipe in recipes:


            item = utils.RecipeBuilder(
                name = recipe.name,
                description = recipe.description,
                recipeYield = recipe.recipeYield,
                cookTime = recipe.cookTime,
                recipeCategory = recipe.recipeCategory,
                author = recipe.author,
                datePublished = str(recipe.datePublished)
            )
            item.add_control("self", "/api/recipes/{}/".format(recipe.id))
            item.add_control("profile", utils.REC_PROFILE)
            body["recipes"].append(item)
        body.add_control_all_recipes()
        body.add_control_add_recipe()
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
        except KeyError:
            return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
        except ValueError:
            return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Weight and price must be numbers")
        except TypeError:
            return utils.RecipeBuilder.create_error_response(415, "Invalid content", "request content type must be JSON")

        recipe = models.Recipe(
            name=name,
            description= description,
            recipeYield = recipeYield,
            cookTime = cookTime,
            recipeCategory = recipeCategory,
            author = author,
            datePublished = datePublished
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

