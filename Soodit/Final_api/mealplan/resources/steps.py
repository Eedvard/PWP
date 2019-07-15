import json
import flask
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Response, request
from flask_restful import Resource
from mealplan import utils, db, models, api
import datetime

class Step(Resource):
    def get(self, recipe_id, step_id):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "wrong method", "GET method required")
        db_recipe = models.RecipeInstructionStep.query.filter_by(recipe_id=recipe_id, step=step_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(recipe_id))

        body = utils.RecipeBuilder(
            recipe_id=db_recipe.recipe_id,
            step=db_recipe.step,
            text=db_recipe.text
        )
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

    def put(self, recipe_id, step_id):
        if request.method != "PUT":
            return utils.RecipeBuilder.create_error_response(405, "wrong method", "PUT method required")
        db_recipe = models.RecipeInstructionStep.query.filter_by(recipe_id=recipe_id, step=step_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not found", "No recipe was found with the name {}".format(recipe_id))
        try:
            text = str(request.json["text"])
        except KeyError:
            return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
        except ValueError:
            return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Weight and price must be numbers")
        except TypeError:
            return utils.RecipeBuilder.create_error_response(415, "Invalid content", "request content type must be JSON")

        body = utils.RecipeBuilder(
            recipe_id=db_recipe.recipe_id,
            recipe=db_recipe.recipe,
            step=db_recipe.step,
            text=db_recipe.text
        )

        db_recipe.text=text

        db.session.commit()
        url = api.api.url_for(Step, recipe_id=db_recipe.recipe_id, step_id=db_recipe.step)
        return Response(headers={
            "Location": url
        },
            status=204
        )

    def delete(self, recipe_id, step_id):
        if request.method != "DELETE":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "DELETE method required")
        db_recipe = models.RecipeInstructionStep.query.filter_by(recipe_id=recipe_id, step=step_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not Found", "No user was found with the username {}".format(recipe_id))

        body = utils.RecipeBuilder(
            recipe_id=db_recipe.recipe_id,
            step=db_recipe.step,
            text=db_recipe.text
        )

        db.session.delete(db_recipe)
        db.session.commit()
        return Response(json.dumps(body), 200, mimetype=utils.MASON)

class StepCollection(Resource):
    def get(self, recipe_id):
        if request.method != "GET":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "GET method required")
        steps = models.RecipeInstructionStep.query.filter_by(recipe_id=recipe_id).all()
        body = utils.RecipeBuilder(steps=[])
        for step in steps:

            item = utils.RecipeBuilder(
                step=step.step,
                text=step.text
            )
            body["steps"].append(item)

        return Response(json.dumps(body), 200, mimetype=utils.MASON)
    def post(recipe, recipe_id):
        if request.method != "POST":
            return utils.RecipeBuilder.create_error_response(405, "Invalid method", "POST method required")
        try:
            stepnum = int(request.json["step"])
            text = str(request.json["text"])
        except KeyError:
            return utils.RecipeBuilder.create_error_response(400, "Missing fields", "Incomplete request - missing fields")
        except ValueError:
            return utils.RecipeBuilder.create_error_response(400, "Invalid input", "Weight and price must be numbers")
        except TypeError:
            return utils.RecipeBuilder.create_error_response(415, "Invalid content", "request content type must be JSON")

        db_recipe = models.Recipe.query.filter_by(id=recipe_id).first()
        if db_recipe is None:
            return utils.RecipeBuilder.create_error_response(404, "Not found",
                                                             "No recipe was found with the name {}".format(recipe_id))
        step = models.RecipeInstructionStep(
            recipe=db_recipe,
            step=stepnum,
            text=text
        )
        db.session.add(step)
        db.session.commit()
        db.session.refresh(step)
        id = db_recipe.id
        stepid = step.step
        url = api.api.url_for(Step, recipe_id=id, step_id=stepid)
        return Response(headers={
            "Location": url
        },
            status=204
        )

