from flask import Blueprint
from flask_restful import Resource, Api

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# this import must be placed after we create api to avoid issues with
# circular imports

from mealplan.resources.users import Users
from mealplan.resources.recipes import RecipeItem, RecipeCollection
from mealplan.resources.steps import Step

api.add_resource(Users, "/users/<user_id>/")
api.add_resource(RecipeCollection, "/recipes/")
api.add_resource(RecipeItem, "/recipes/<recipe_id>/")
api.add_resource(Step, "/recipes/<recipe_id>/steps/step_id/")

#api.add_resource(SensorItem, "/sensors/<sensor>/")

@api_bp.route("/")
def index():
    return "paska"