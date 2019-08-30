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
            if not models.Recipe.query.filter_by(id=recipe_id).all():
                return utils.RecipeBuilder.create_error_response(404,"Not found","No recipe was found with id {}".format(recipe_id))
            db_recipe = models.RecipeIngredient.query.filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found", "No ingredient was found with id {}".format(ingredient_id))

            body = utils.RecipeBuilder(
                name=db_recipe.ingredient.name,
                description=db_recipe.ingredient.description,
                amount=db_recipe.amount,
                unit=db_recipe.unit,
                calories=db_recipe.ingredient.nutrition_information.calories,
                carbohydrateContent=db_recipe.ingredient.nutrition_information.carbohydrateContent,
                cholesterolContent=db_recipe.ingredient.nutrition_information.cholesterolContent,
                fatContent=db_recipe.ingredient.nutrition_information.fatContent,
                fiberContent=db_recipe.ingredient.nutrition_information.fiberContent,
                proteinContent=db_recipe.ingredient.nutrition_information.proteinContent,
                saturatedFatContent=db_recipe.ingredient.nutrition_information.saturatedFatContent,
                sodiumContent=db_recipe.ingredient.nutrition_information.sodiumContent,
                sugarContent=db_recipe.ingredient.nutrition_information.sugarContent,
                transFatContent=db_recipe.ingredient.nutrition_information.transFatContent,
                unsaturatedFatContent=db_recipe.ingredient.nutrition_information.unsaturatedFatContent
            )
            body.add_namespace("recipe_ingredients", utils.LINK_RELATIONS_URL)
            body.add_control("self", api.api.url_for(Ingredient, recipe_id=recipe_id, ingredient_id=ingredient_id))
            body.add_control("profile", utils.ING_PROFILE)
            body.add_control("collection", api.api.url_for(IngredientCollection, recipe_id=recipe_id))
            body.add_control_delete_recipe_ingredient(recipe_id, ingredient_id)
            body.add_control_edit_recipe_ingredient(recipe_id, ingredient_id)
        elif list_id and username is not None:
            if not models.User.query.filter_by(username=username).all():
                return utils.RecipeBuilder.create_error_response(404, "Not found","No user was found with the username {}".format(username))
            db_list = models.ShoppingList.query.filter_by(owner_name=username, id=list_id).first()
            if db_list is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found",
                                                                 "No shopping list with id {} was found with the username {}".format(
                                                                     list_id,
                                                                     username))
            db_recipe = models.ShoppingListIngredient.query.filter_by(shopping_list=db_list, ingredient_id=ingredient_id, ).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found", "No ingredient was found with id {}".format(ingredient_id))

            body = utils.RecipeBuilder(
                name=db_recipe.ingredient.name,
                description=db_recipe.ingredient.description,
                amount=db_recipe.amount,
                unit=db_recipe.unit,
                calories=db_recipe.ingredient.nutrition_information.calories,
                carbohydrateContent=db_recipe.ingredient.nutrition_information.carbohydrateContent,
                cholesterolContent=db_recipe.ingredient.nutrition_information.cholesterolContent,
                fatContent=db_recipe.ingredient.nutrition_information.fatContent,
                fiberContent=db_recipe.ingredient.nutrition_information.fiberContent,
                proteinContent=db_recipe.ingredient.nutrition_information.proteinContent,
                saturatedFatContent=db_recipe.ingredient.nutrition_information.saturatedFatContent,
                sodiumContent=db_recipe.ingredient.nutrition_information.sodiumContent,
                sugarContent=db_recipe.ingredient.nutrition_information.sugarContent,
                transFatContent=db_recipe.ingredient.nutrition_information.transFatContent,
                unsaturatedFatContent=db_recipe.ingredient.nutrition_information.unsaturatedFatContent
            )
            body.add_namespace("list_ingredients", utils.LINK_RELATIONS_URL)
            body.add_control("self", api.api.url_for(Ingredient, username=username, list_id=list_id, ingredient_id=ingredient_id))
            body.add_control("profile", utils.ING_PROFILE)
            body.add_control("collection", api.api.url_for(IngredientCollection, username=username, list_id=list_id))
            body.add_control_delete_shoplist_ingredient(username, list_id, ingredient_id)
            body.add_control_edit_shoplist_ingredient(username, list_id, ingredient_id)
            body.add_control("storage:recipe_ingredients-all",
                             api.api.url_for(IngredientCollection, username=username, list_id=list_id))
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

    def put(self, ingredient_id, recipe_id=None, list_id=None, username=None):
        if request.method != "PUT":
            return utils.RecipeBuilder.create_error_response(405, "wrong method", "PUT method required")
        if recipe_id is not None:
            if not models.Recipe.query.filter_by(id=recipe_id).all():
                return utils.RecipeBuilder.create_error_response(404,"Not found","No recipe was found with id {}".format(recipe_id))
            db_recipe = models.RecipeIngredient.query.filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found", "No ingredient was found with id {}".format(ingredient_id))
            try:
                name = str(request.json["name"])
                description = str(request.json["description"])
                amount = int(request.json["amount"])
                unit = str(request.json["unit"])

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
                calories=db_recipe.ingredient.nutrition_information.calories,
                carbohydrateContent=db_recipe.ingredient.nutrition_information.carbohydrateContent,
                cholesterolContent=db_recipe.ingredient.nutrition_information.cholesterolContent,
                fatContent=db_recipe.ingredient.nutrition_information.fatContent,
                fiberContent=db_recipe.ingredient.nutrition_information.fiberContent,
                proteinContent=db_recipe.ingredient.nutrition_information.proteinContent,
                saturatedFatContent=db_recipe.ingredient.nutrition_information.saturatedFatContent,
                sodiumContent=db_recipe.ingredient.nutrition_information.sodiumContent,
                sugarContent=db_recipe.ingredient.nutrition_information.sugarContent,
                transFatContent=db_recipe.ingredient.nutrition_information.transFatContent,
                unsaturatedFatContent=db_recipe.ingredient.nutrition_information.unsaturatedFatContent
            )
            optional = ["calories", "carbohydratecontent", "cholesterolcontent", "fatcontent", "fibercontent",
                        "proteincontent", "saturatedfatcontent", "sodiumcontent", "sugarcontent", "transfatcontent",
                        "unsaturatedfatcontent"]
            values = []
            for jsonname in optional:
                try:
                    values.append(int(request.json[jsonname]))
                except KeyError:
                    values.append(None)
                    pass
                except ValueError:
                    return utils.RecipeBuilder.create_error_response(400, "Invalid input",
                                                                     "Weight and price must be numbers")
                except TypeError:
                    return utils.RecipeBuilder.create_error_response(415, "Invalid content",

                                                                     "request content type must be JSON")

            db_recipe.ingredient.name=name
            db_recipe.ingredient.description=description
            db_recipe.amount=amount
            db_recipe.unit=unit
            def None_sum(a, b, c):
                if a and b and c is None:
                    return None
                elif b and c is None:
                    return a
                elif c is None:
                    return a
                else:
                    return (a+b-c)
            if db_recipe.ingredient.nutrition_information is None:
                pass
            else:
                nutrition = db_recipe.ingredient.nutrition_information
                nutrition.calories = None_sum(nutrition.calories, values[0], db_recipe.ingredient.nutrition_information.calories)
                nutrition.carbohydrateContent = None_sum(nutrition.carbohydrateContent, values[1], db_recipe.ingredient.nutrition_information.carbohydrateContent)
                nutrition.cholesterolContent = None_sum(nutrition.cholesterolContent, values[2], db_recipe.ingredient.nutrition_information.cholesterolContent)
                nutrition.fatContent = None_sum(nutrition.fatContent, values[3], db_recipe.ingredient.nutrition_information.fatContent)
                nutrition.fiberContent = None_sum(nutrition.fiberContent, values[4], db_recipe.ingredient.nutrition_information.fiberContent)
                nutrition.proteinContent = None_sum(nutrition.proteinContent, values[5], db_recipe.ingredient.nutrition_information.proteinContent)
                nutrition.saturatedFatContent = None_sum(nutrition.saturatedFatContent, values[6], db_recipe.ingredient.nutrition_information.saturatedFatContent)
                nutrition.sodiumContent = None_sum(nutrition.sodiumContent, values[7], db_recipe.ingredient.nutrition_information.sodiumContent)
                nutrition.sugarContent = None_sum(nutrition.sugarContent, values[8], db_recipe.ingredient.nutrition_information.sugarContent)
                nutrition.transFatContent = None_sum(nutrition.transFatContent, values[9], db_recipe.ingredient.nutrition_information.transFatContent)
                nutrition.unsaturatedFatContent = None_sum(nutrition.unsaturatedFatContent, values[10], db_recipe.ingredient.nutrition_information.unsaturatedFatContent)
            db.session.commit()
            url = api.api.url_for(Ingredient, recipe_id=recipe_id, ingredient_id=ingredient_id)
        elif list_id and username is not None:
            db_list = models.ShoppingList.query.filter_by(owner_name=username, id=list_id).first()
            if db_list is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found",
                                                                 "No shopping list with id {} was found with the username {}".format(
                                                                     list_id,
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
            )

            db_recipe.ingredient.name = name
            db_recipe.ingredient.description = description
            db_recipe.amount = amount
            db_recipe.unit = unit
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
            if not models.Recipe.query.filter_by(id=recipe_id).all():
                return utils.RecipeBuilder.create_error_response(404,"Not found","No recipe was found with id {}".format(recipe_id))
            db_recipe = models.RecipeIngredient.query.filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found","No ingredient was found with id {}".format(ingredient_id))
            body = utils.RecipeBuilder(
                name=db_recipe.ingredient.name,
                description=db_recipe.ingredient.description,
                amount=db_recipe.amount,
                unit=db_recipe.unit,
                calories=db_recipe.ingredient.nutrition_information.calories,
                carbohydrateContent=db_recipe.ingredient.nutrition_information.carbohydrateContent,
                cholesterolContent=db_recipe.ingredient.nutrition_information.cholesterolContent,
                fatContent=db_recipe.ingredient.nutrition_information.fatContent,
                fiberContent=db_recipe.ingredient.nutrition_information.fiberContent,
                proteinContent=db_recipe.ingredient.nutrition_information.proteinContent,
                saturatedFatContent=db_recipe.ingredient.nutrition_information.saturatedFatContent,
                sodiumContent=db_recipe.ingredient.nutrition_information.sodiumContent,
                sugarContent=db_recipe.ingredient.nutrition_information.sugarContent,
                transFatContent=db_recipe.ingredient.nutrition_information.transFatContent,
                unsaturatedFatContent=db_recipe.ingredient.nutrition_information.unsaturatedFatContent
            )
            def None_sum(a, b):
                if a and b is None:
                    return None
                elif b is None:
                    return a
                else:
                    return a-b
            if db_recipe.ingredient.nutrition_information is None:
                pass
            else:
                nutrition = db_recipe.ingredient.nutrition_information
                nutrition.calories = None_sum(nutrition.calories, db_recipe.ingredient.nutrition_information.calories)
                nutrition.carbohydrateContent = None_sum(nutrition.carbohydrateContent, db_recipe.ingredient.nutrition_information.carbohydrateContent)
                nutrition.cholesterolContent = None_sum(nutrition.cholesterolContent, db_recipe.ingredient.nutrition_information.cholesterolContent)
                nutrition.fatContent = None_sum(nutrition.fatContent, db_recipe.ingredient.nutrition_information.fatContent)
                nutrition.fiberContent = None_sum(nutrition.fiberContent, db_recipe.ingredient.nutrition_information.fiberContent)
                nutrition.proteinContent = None_sum(nutrition.proteinContent, db_recipe.ingredient.nutrition_information.proteinContent)
                nutrition.saturatedFatContent = None_sum(nutrition.saturatedFatContent, db_recipe.ingredient.nutrition_information.saturatedFatContent)
                nutrition.sodiumContent = None_sum(nutrition.sodiumContent, db_recipe.ingredient.nutrition_information.sodiumContent)
                nutrition.sugarContent = None_sum(nutrition.sugarContent, db_recipe.ingredient.nutrition_information.sugarContent)
                nutrition.transFatContent = None_sum(nutrition.transFatContent, db_recipe.ingredient.nutrition_information.transFatContent)
                nutrition.unsaturatedFatContent = None_sum(nutrition.unsaturatedFatContent, db_recipe.ingredient.nutrition_information.unsaturatedFatContent)
        elif list_id and username is not None:

            db_list = models.ShoppingList.query.filter_by(owner_name=username, id=list_id).first()
            if db_list is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found",
                                                                 "No shopping list with id {} was found with the username {}".format(
                                                                     list_id,
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
            )
        db.session.delete(db_recipe)
        db.session.commit()
        return Response(json.dumps(body), 204, mimetype=utils.MASON)

class IngredientCollection(Resource):
    def get(self, recipe_id=None, username=None, list_id=None):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "GET method required")
        body = utils.RecipeBuilder(ingredients=[])
        if recipe_id is not None:
            if not models.Recipe.query.filter_by(id=recipe_id).all():
                return utils.RecipeBuilder.create_error_response(404,"Not found","No recipe was found with id {}".format(recipe_id))
            ingredients = models.RecipeIngredient.query.filter_by(recipe_id=recipe_id).all()
            for ingredient in ingredients:
                item = utils.RecipeBuilder(
                    name=ingredient.ingredient.name,
                    description=ingredient.ingredient.description,
                    amount=ingredient.amount,
                    unit=ingredient.unit
                )
                item.add_control("self", "/api/recipes/{}/ingredients/{}/".format(recipe_id, ingredient.ingredient_id))
                item.add_control("profile", utils.ING_PROFILE)
                body["ingredients"].append(item)
            body.add_control_all_recipe_ingredients(recipe_id)
            body.add_control_add_recipe_ingredient(recipe_id)
        elif username and list_id is not None:
            db_list = models.ShoppingList.query.filter_by(owner_name=username, id=list_id).first()
            if db_list is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found",
                                                                 "No shopping list with id {} was found with the username {}".format(
                                                                     list_id,
                                                                     username))
            ingredients = models.ShoppingListIngredient.query.filter_by(shopping_list_id=list_id).all()
            for ingredient in ingredients:
                item = utils.RecipeBuilder(
                    name=ingredient.ingredient.name,
                    description=ingredient.ingredient.description,
                    amount=ingredient.amount,
                    unit=ingredient.unit
                )
                item.add_control("self", "/api/users/{}/shoppinglist/{}/ingredients/{}/".format(username, list_id, ingredient.ingredient_id))
                item.add_control("profile", utils.ING_PROFILE)
                body["ingredients"].append(item)
            body.add_control_all_shoplist_ingredients(username, list_id)
            body.add_control_add_shoplist_ingredient(username, list_id)
        return Response(json.dumps(body), 200, mimetype=utils.MASON)
    def post(recipe, recipe_id=None, username=None, list_id=None):
        if request.method != "POST":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "POST method required")
        if recipe_id is not None:
            if not models.Recipe.query.filter_by(id=recipe_id).all():
                return utils.RecipeBuilder.create_error_response(404,"Not found","No recipe was found with id {}".format(recipe_id))
            try:
                name = str(request.json["name"])
                description = str(request.json["description"])
                amount = int(request.json["amount"])
                unit = str(request.json["unit"])
            except KeyError:
                return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
            except ValueError:
                return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Weight and price must be numbers")
            except TypeError:
                return utils.RecipeBuilder.create_error_response(415, "Invalid content", "request content type must be JSON")

            db_recipe = models.Recipe.query.filter_by(id=recipe_id).first()
            if db_recipe is None:
                return utils.RecipeBuilder.create_error_response(404, "Not found","No recipe was found with the name {}".format(recipe_id))
            optional = ["calories", "carbohydratecontent", "cholesterolcontent", "fatcontent", "fibercontent", "proteincontent", "saturatedfatcontent", "sodiumcontent", "sugarcontent", "transfatcontent", "unsaturatedfatcontent"]
            values = []
            for jsonname in optional:
                try:
                    values.append(int(request.json[jsonname]))
                except KeyError:
                    values.append(None)
                    pass
                except ValueError:
                    return utils.RecipeBuilder.create_error_response(400, "Invalid input",
                                                                     "Weight and price must be numbers")
                except TypeError:
                    return utils.RecipeBuilder.create_error_response(415, "Invalid content",

                                                                     "request content type must be JSON")
            nutrition_information = models.NutritionInformation(
                calories=values[0],
                carbohydrateContent=values[1],
                cholesterolContent=values[2],
                fatContent=values[3],
                fiberContent=values[4],
                proteinContent=values[5],
                saturatedFatContent=values[6],
                sodiumContent=values[7],
                sugarContent=values[8],
                transFatContent=values[9],
                unsaturatedFatContent=values[10]
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

            def None_sum(*args):
                args = [a for a in args if not a is None]
                return sum(args) if args else None
            if db_recipe.nutrition_information is None:
                db_recipe.nutrition_information = nutrition_information
            else:
                nutrition = db_recipe.nutrition_information
                nutrition.calories = None_sum(nutrition.calories, values[0])
                nutrition.carbohydrateContent = None_sum(nutrition.carbohydrateContent, values[1])
                nutrition.cholesterolContent = None_sum(nutrition.cholesterolContent, values[2])
                nutrition.fatContent = None_sum(nutrition.fatContent, values[3])
                nutrition.fiberContent = None_sum(nutrition.fiberContent, values[4])
                nutrition.proteinContent = None_sum(nutrition.proteinContent, values[5])
                nutrition.saturatedFatContent = None_sum(nutrition.saturatedFatContent, values[6])
                nutrition.sodiumContent = None_sum(nutrition.sodiumContent, values[7])
                nutrition.sugarContent = None_sum(nutrition.sugarContent, values[8])
                nutrition.transFatContent = None_sum(nutrition.transFatContent, values[9])
                nutrition.unsaturatedFatContent = None_sum(nutrition.unsaturatedFatContent, values[10])
            db.session.add(ingredient)
            db.session.add(recipeingredient)
            db.session.commit()
            db.session.refresh(recipeingredient)
            id = db_recipe.id
            ingid = recipeingredient.ingredient_id
            url = api.api.url_for(Ingredient, recipe_id=id, ingredient_id=ingid)

        elif username and list_id is not None:
            db_list = models.ShoppingList.query.filter_by(owner_name=username, id=list_id).first()
            if db_list is None:
                return utils.RecipeBuilder.create_error_response(404, "Not Found",
                                                                 "No shopping list with id {} was found with the username {}".format(
                                                                     list_id,
                                                                     username))
            try:
                name = str(request.json["name"])
                description = str(request.json["description"])
                amount = int(request.json["amount"])
                unit = str(request.json["unit"])

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
            optional = ["calories", "carbohydratecontent", "cholesterolcontent", "fatcontent", "fibercontent",
                        "proteincontent", "saturatedfatcontent", "sodiumcontent", "sugarcontent", "transfatcontent",
                        "unsaturatedfatcontent"]
            values = []
            for jsonname in optional:
                try:
                    values.append(int(request.json[jsonname]))
                except KeyError:
                    values.append(None)
                    pass
                except ValueError:
                    return utils.RecipeBuilder.create_error_response(400, "Invalid input",
                                                                     "Weight and price must be numbers")
                except TypeError:
                    return utils.RecipeBuilder.create_error_response(415, "Invalid content",

                                                                     "request content type must be JSON")
            nutrition_information = models.NutritionInformation(
                calories=values[0],
                carbohydrateContent=values[1],
                cholesterolContent=values[2],
                fatContent=values[3],
                fiberContent=values[4],
                proteinContent=values[5],
                saturatedFatContent=values[6],
                sodiumContent=values[7],
                sugarContent=values[8],
                transFatContent=values[9],
                unsaturatedFatContent=values[10]
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