import json
import flask
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Response, request
from flask_restful import Resource
from mealplan import utils, db, models, api
import datetime

class Ingredient(Resource):
    def get(self, ingredient_id, recipe_id=None, list_id=None, username=None):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "wrong method", "GET method required")
        if recipe_id is not None:
            db_recipe = models.RecipeIngredient.query.filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(username))

            body = utils.RecipeBuilder(
                name=db_recipe.ingredient.name,
                description=db_recipe.ingredient.description,
                amount=db_recipe.amount,
                unit=db_recipe.unit,
                servingsize=db_recipe.ingredient.nutrition_information.servingSize,
                servingsizeunit=db_recipe.ingredient.nutrition_information.servingSizeUnit
            )
        elif list_id and username is not None:
            db_list = models.ShoppingList.query.filter_by(owner_name=username).first()
            if db_list is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found","No shopping list with that id was found with the username {}".format(username))
            db_recipe = models.ShoppingListIngredient.query.filter_by(shopping_list_id=list_id, ingredient_id=ingredient_id, ).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found","No user was found with the username {}".format(username))

            body = utils.RecipeBuilder(
                name=db_recipe.ingredient.name,
                description=db_recipe.ingredient.description,
                amount=db_recipe.amount,
                unit=db_recipe.unit,
                servingsize=db_recipe.ingredient.nutrition_information.servingSize,
                servingsizeunit=db_recipe.ingredient.nutrition_information.servingSizeUnit
            )
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

    def put(self, ingredient_id, recipe_id=None, list_id=None, username=None):
        if request.method != "PUT":
            return utils.RecipeBuilder.create_error_response(405, "wrong method", "PUT method required")
        if recipe_id is not None:
            db_recipe = models.RecipeIngredient.query.filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not found", "No recipe was found with the name {}".format(recipe_id))
            try:
                name = str(request.json["name"])
                description = str(request.json["description"])
                amount = int(request.json["amount"])
                unit = str(request.json["unit"])

                servingsize = int(request.json["servingsize"])
                servingsizeunit = str(request.json["servingsizeunit"])
            except KeyError:
                return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
            except ValueError:
                return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Weight and price must be numbers")
            except TypeError:
                return utils.RecipeBuilder.create_error_response(415, "Invalid content", "request content type must be JSON")

            body = utils.RecipeBuilder(
                name=db_recipe.ingredient.name,
                description=db_recipe.ingredient.description,
                amount=db_recipe.amount,
                unit=db_recipe.unit,
                servingsize=db_recipe.ingredient.nutrition_information.servingSize,
                servingsizeunit=db_recipe.ingredient.nutrition_information.servingSizeUnit
            )

            db_recipe.ingredient.name=name
            db_recipe.ingredient.description=description
            db_recipe.amount=amount
            db_recipe.unit=unit
            db_recipe.ingredient.nutrition_information.servingSize=servingsize
            db_recipe.ingredient.nutrition_information.servingSizeUnit=servingsizeunit
            db.session.commit()

            url = api.api.url_for(Ingredient, recipe_id=recipe_id, ingredient_id=ingredient_id)
        elif list_id and username is not None:
            db_list = models.ShoppingList.query.filter_by(owner_name=username).first()
            if db_list is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found",
                                                                 "No shopping list with that id was found with the username {}".format(
                                                                     username))
            db_recipe = models.ShoppingListIngredient.query.filter_by(shopping_list_id=list_id,
                                                                      ingredient_id=ingredient_id, ).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found",
                                                                 "No user was found with the username {}".format(
                                                                     recipe_id))
            try:
                name = str(request.json["name"])
                description = str(request.json["description"])
                amount = int(request.json["amount"])
                unit = str(request.json["unit"])

                servingsize = int(request.json["servingsize"])
                servingsizeunit = str(request.json["servingsizeunit"])
            except KeyError:
                return utils.RecipeBuilder.create_error_response(400, "Missing fields",
                                                                 "Incomplete request - missing fields")
            except ValueError:
                return utils.RecipeBuilder.create_error_response(400, "Invalid input",
                                                                 "Weight and price must be numbers")
            except TypeError:
                return utils.RecipeBuilder.create_error_response(415, "Invalid content",
                                                                 "request content type must be JSON")

            body = utils.RecipeBuilder(
                name=db_recipe.ingredient.name,
                description=db_recipe.ingredient.description,
                amount=db_recipe.amount,
                unit=db_recipe.unit,
                servingsize=db_recipe.ingredient.nutrition_information.servingSize,
                servingsizeunit=db_recipe.ingredient.nutrition_information.servingSizeUnit
            )

            db_recipe.ingredient.name = name
            db_recipe.ingredient.description = description
            db_recipe.amount = amount
            db_recipe.unit = unit
            db_recipe.ingredient.nutrition_information.servingSize = servingsize
            db_recipe.ingredient.nutrition_information.servingSizeUnit = servingsizeunit
            db.session.commit()
            url = api.api.url_for(Ingredient, username=username, list_id=list_id, ingredient_id=ingredient_id)
        return Response(headers={
            "Location": url
        },
            status=204
        )

    def delete(self, ingredient_id, recipe_id=None, list_id=None, username=None):
        if request.method != "DELETE":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "DELETE method required")

        if recipe_id is not None:
            db_recipe = models.RecipeIngredient.query.filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(recipe_id))

            body = utils.RecipeBuilder(
                name=db_recipe.ingredient.name,
                description=db_recipe.ingredient.description,
                amount=db_recipe.amount,
                unit=db_recipe.unit,
                servingsize=db_recipe.ingredient.nutrition_information.servingSize,
                servingsizeunit=db_recipe.ingredient.nutrition_information.servingSizeUnit
            )
        elif list_id and username is not None:

            db_list = models.ShoppingList.query.filter_by(owner_name=username).first()
            if db_list is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found",
                                                                 "No shopping list with that id was found with the username {}".format(
                                                                     username))
            db_recipe = models.ShoppingListIngredient.query.filter_by(shopping_list_id=list_id,
                                                                      ingredient_id=ingredient_id, ).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found",
                                                                 "No user was found with the username {}".format(
                                                                     recipe_id))



            body = utils.RecipeBuilder(
                name=db_recipe.ingredient.name,
                description=db_recipe.ingredient.description,
                amount=db_recipe.amount,
                unit=db_recipe.unit,
                servingsize=db_recipe.ingredient.nutrition_information.servingSize,
                servingsizeunit=db_recipe.ingredient.nutrition_information.servingSizeUnit
            )
        db.session.delete(db_recipe)
        db.session.commit()
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

class IngredientCollection(Resource):
    def get(self, recipe_id=None, username=None, list_id=None):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "GET method required")
        body = utils.RecipeBuilder(ingredients=[])
        db_list = models.ShoppingList.query.filter_by(id=list_id).first()
        if db_list.owner != username:
            return utils.RecipeBuilder.create_error_response(404, "Not Found",
                                                             "No shopping list with that id was found with the username {}".format(
                                                                 recipe_id))
        if recipe_id is not None:

            ingredients = models.RecipeIngredient.query.filter_by(recipe_id=recipe_id).all()
            for ingredient in ingredients:
                item = utils.RecipeBuilder(
                    name=ingredient.ingredient.name,
                    description=ingredient.ingredient.description,
                    amount=ingredient.amount,
                    unit=ingredient.unit
                )
                body["ingredients"].append(item)
        elif username and list_id is not None:
            ingredients = models.ShoppingListIngredient.query.filter_by(shopping_list_id=list_id).all()
            for ingredient in ingredients:
                item = utils.RecipeBuilder(
                    name=ingredient.ingredient.name,
                    description=ingredient.ingredient.description,
                    amount=ingredient.amount,
                    unit=ingredient.unit
                )
                body["ingredients"].append(item)
        return Response(json.dumps(body), 200, mimetype=utils.MASON)
    def post(recipe, recipe_id=None, username=None, list_id=None):
        if request.method != "POST":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "POST method required")
        if recipe_id is not None:
            try:
                name = str(request.json["name"])
                description = str(request.json["description"])
                amount = int(request.json["amount"])
                unit = str(request.json["unit"])

                servingsize = int(request.json["servingsize"])
                servingsizeunit = str(request.json["servingsizeunit"])
            except KeyError:
                return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
            except ValueError:
                return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Weight and price must be numbers")
            except TypeError:
                return utils.RecipeBuilder.create_error_response(415, "Invalid content", "request content type must be JSON")

            db_recipe = models.Recipe.query.filter_by(id=recipe_id).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not found","No recipe was found with the name {}".format(recipe_id))

            nutrition_information = models.NutritionInformation(
                servingSize=servingsize,
                servingSizeUnit=servingsizeunit
            )
            ingredient = models.Ingredient(
                name=name,
                description=description,
                nutrition_information=nutrition_information
            )
            recipeingredient = models.RecipeIngredient(
                recipe=db_recipe,
                ingredient=ingredient,
                amount=amount,
                unit=unit
            )
            db.session.add(ingredient)
            db.session.add(recipeingredient)
            db.session.commit()
            db.session.refresh(recipeingredient)
            id = db_recipe.id
            ingid = recipeingredient.ingredient_id
            url = api.api.url_for(Ingredient, recipe_id=id, ingredient_id=ingid)

        elif username and list_id is not None:
            try:
                name = str(request.json["name"])
                description = str(request.json["description"])
                amount = int(request.json["amount"])
                unit = str(request.json["unit"])

                servingsize = int(request.json["servingsize"])
                servingsizeunit = str(request.json["servingsizeunit"])
            except KeyError:
                return utils.RecipeBuilder.create_error_response(400, "Missing fields",
                                                                 "Incomplete request - missing fields")
            except ValueError:
                return utils.RecipeBuilder.create_error_response(400, "Invalid input",
                                                                 "Weight and price must be numbers")
            except TypeError:
                return utils.RecipeBuilder.create_error_response(415, "Invalid content",
                                                                 "request content type must be JSON")

            db_recipe = models.ShoppingList.query.filter_by(owner_name=username, id=list_id).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not found","No shoppinglist was found with the name {}".format(list_id))

            nutrition_information = models.NutritionInformation(
                servingSize=servingsize,
                servingSizeUnit=servingsizeunit
            )
            ingredient = models.Ingredient(
                name=name,
                description=description,
                nutrition_information=nutrition_information
            )
            shoplistingredient = models.ShoppingListIngredient(
                shopping_list=db_recipe,
                ingredient=ingredient,
                amount=amount,
                unit=unit
            )
            db.session.add(ingredient)
            db.session.add(shoplistingredient)
            db.session.commit()
            db.session.refresh(shoplistingredient)
            id = db_recipe.id
            ingid = shoplistingredient.ingredient_id
            url = api.api.url_for(Ingredient, username=username, list_id=list_id, ingredient_id=ingid)

        return Response(headers={
            "Location": url
        },
            status=204
        )