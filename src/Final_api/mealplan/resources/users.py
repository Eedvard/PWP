import json
import flask
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Response, request
from flask_restful import Resource
from mealplan import utils, db, models, api
import datetime


class Users(Resource):

    def get(self, username):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "Wrong method", "GET method required")
        db_user = models.User.query.filter_by(username=username).first()
        if db_user is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(username))

        body = utils.RecipeBuilder(
            username=db_user.username
        )
        body.add_namespace("users", utils.LINK_RELATIONS_URL)
        body.add_control("self", api.api.url_for(Users, username=username))
        body.add_control("profile", utils.USER_PROFILE)
        body.add_control("collection", "/api/users/")
        body.add_control_delete_user(username)
        body.add_control_edit_user(username)
        body.add_control("storage:users-all", api.api.url_for(Users, username=username))
        body.add_control_add_shoppinglist(username)
        body.add_control_all_shoppinglists(username)
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

    def put(self, username):
        if request.method != "PUT":
            return utils.RecipeBuilder.create_error_response(405, "Wrong method", "PUT method required")
        db_user = models.User.query.filter_by(username=username).first()
        if db_user is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(username))
        try:
            newusername = str(request.json["username"])
        except KeyError:
            return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
        except ValueError:
            return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Username must be a string")
        except TypeError:
            return utils.RecipeBuilder.create_error_response(415, "Invalid content", "Request content must be JSON")
        if (models.User.query.filter_by(username=newusername).first() is not None) and username!=newusername:
            return utils.RecipeBuilder.create_error_response(409, "Duplicate content", "User already exists")

        body = utils.RecipeBuilder(
            username=db_user.username
        )

        db_user.username = newusername
        db.session.commit()
        url = api.api.url_for(Users, username=newusername)
        return Response(headers={
            "Location": url
        },
            status=204
        )

    def delete(self, username):
        if request.method != "DELETE":
            return utils.RecipeBuilder.create_error_response(405, "Wrong method", "DELETE method required")
        db_user = models.User.query.filter_by(username=username).first()
        print(db_user)
        if db_user is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(username))

        body = utils.RecipeBuilder(
            username=db_user.username
        )

        db.session.delete(db_user)
        db.session.commit()
        return Response(json.dumps(body), 204, mimetype=utils.MASON)


class UserCollection (Resource):

    def get(self):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "Wrong method", "GET method required")
        users = db.session.query(models.User).all()
        body = utils.RecipeBuilder(users=[])
        for user in users:
            useritem = utils.RecipeBuilder(
                username=user.username
            )
            useritem.add_control("self", "/api/users/{}/".format(user.username))
            useritem.add_control("profile", utils.USER_PROFILE)
            body["users"].append(useritem)
        body.add_control_all_users()
        body.add_control_add_user()
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

    def post(self):
        if request.method != "POST":
            return utils.RecipeBuilder.create_error_response(405, "Wrong method", "POST method required")
        try:
            username = str(request.json["username"])
        except KeyError:
            return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
        except ValueError:
            return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Username must be a string")
        except TypeError:
            return utils.RecipeBuilder.create_error_response(415, "Invalid content", "Request content must be JSON")

        db_user = models.User.query.filter_by(username=username).first()
        if db_user is not None:
            return utils.RecipeBuilder.create_error_response(409, "Duplicate content", "User already exists")

        user = models.User(
            username=username
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

        url = api.api.url_for(Users, username=username)
        return Response(headers={
            "Location": url
        },
            status=204
        )
