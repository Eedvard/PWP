import json
import flask
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Response, request
from flask_restful import Resource
from mealplan import utils, db, models, api
import datetime

class Shoppinglist(Resource):
    def get(self, username, list_id):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "wrong method", "GET method required")
        if not models.User.query.filter_by(username=username).all():
            return utils.RecipeBuilder.create_error_response(404, "Not found", "No user was found with the username {}".format(username))

        db_recipe = models.ShoppingList.query.filter_by(owner_name=username, id=list_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not found", "User {} has no shoppinglist with id {}".format(username, list_id))

        body = utils.RecipeBuilder(
            notes=db_recipe.notes,
            owner=db_recipe.owner_name
        )
        body.add_namespace("shoppinglists", utils.LINK_RELATIONS_URL)
        body.add_control("self", api.api.url_for(Shoppinglist, username=username, list_id=list_id))
        body.add_control("profile", utils.SHOPLIST_PROFILE)
        body.add_control("collection", api.api.url_for(ShoppingListCollection, username=username))
        body.add_control_delete_shoppinglist(username, list_id)
        body.add_control_edit_shoppinglist(username, list_id)
        body.add_control("storage:shoppinglists-all", api.api.url_for(ShoppingListCollection, username=username))
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

    def put(self, username, list_id):
        if request.method != "PUT":
            return utils.RecipeBuilder.create_error_response(405, "wrong method", "PUT method required")
        if not models.User.query.filter_by(username=username).all():
            return utils.RecipeBuilder.create_error_response(404, "Not found", "No user was found with the username {}".format(username))

        db_recipe = models.ShoppingList.query.filter_by(owner_name=username, id=list_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not found", "User {} has no shoppinglist with id {}".format(username, list_id))
        try:
            notes = str(request.json["notes"])
        except KeyError:
            return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
        except ValueError:
            return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Weight and price must be numbers")
        except TypeError:
            return utils.RecipeBuilder.create_error_response(415, "Invalid content", "request content type must be JSON")

        body = utils.RecipeBuilder(
            notes=db_recipe.notes,
            owner=db_recipe.owner_name
        )

        db_recipe.notes=notes
        db.session.commit()

        url = api.api.url_for(Shoppinglist, username=username, list_id=id)
        return Response(headers={
            "Location": url
        },
            status=204
        )

    def delete(self, username, list_id):
        if request.method != "DELETE":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "DELETE method required")
        if not models.User.query.filter_by(username=username).all():
            return utils.RecipeBuilder.create_error_response(404, "Not found", "No user was found with the username {}".format(username))
        db_recipe = models.ShoppingList.query.filter_by(owner_name=username, id=list_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not found", "User {} has no shoppinglist with id {}".format(username, list_id))

        body = utils.RecipeBuilder(
            notes=db_recipe.notes,
            owner=db_recipe.owner_name
        )

        db.session.delete(db_recipe)
        db.session.commit()
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

class ShoppingListCollection(Resource):
    def get(self, username):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "GET method required")
        body = utils.RecipeBuilder(shoppinglists=[])

        shoppinglists = models.ShoppingList.query.filter_by(owner_name=username).all()
        if not models.User.query.filter_by(username=username).all():
            return utils.RecipeBuilder.create_error_response(404, "Not found", "No user was found with the username {}".format(username))

        for shoppinglist in shoppinglists:
            item = utils.RecipeBuilder(
                notes=shoppinglist.notes
            )
            item.add_control("self", "/api/users/{}/shoppinglist/{}/".format(username, shoppinglist.id))
            item.add_control("profile", utils.SHOPLIST_PROFILE)
            body["shoppinglists"].append(item)
        body.add_control_all_shoppinglists(username)
        body.add_control_add_shoppinglist(username)
        return Response(json.dumps(body), 200, mimetype=utils.MASON)
    def post(shoppinglist, username):
        if request.method != "POST":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "POST method required")
        if not models.User.query.filter_by(username=username).all():
            return utils.RecipeBuilder.create_error_response(404, "Not found", "No user was found with the username {}".format(username))
        try:
            notes = str(request.json["notes"])
        except KeyError:
            return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
        except ValueError:
            return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Weight and price must be numbers")
        except TypeError:
            return utils.RecipeBuilder.create_error_response(415, "Invalid content", "request content type must be JSON")

        db_recipe = models.User.query.filter_by(username=username).first()

        shoppinglist = models.ShoppingList(
            notes = notes,
            owner = db_recipe
        )
        db.session.add(shoppinglist)
        db.session.commit()
        db.session.refresh(shoppinglist)
        id = shoppinglist.id
        url = api.api.url_for(Shoppinglist, username=username, list_id=id)
        return Response(headers={
            "Location": url
        },
            status=204
        )