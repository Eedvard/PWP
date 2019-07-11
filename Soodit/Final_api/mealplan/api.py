from flask import Blueprint
from flask_restful import Resource, Api

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# this import must be placed after we create api to avoid issues with
# circular imports

from mealplan.resources.users import Users
from mealplan.resources.recipes import RecipeItem, RecipeCollection

api.add_resource(Users, "/users/<user_id>/")
api.add_resource(RecipeCollection, "/recipes/")
#api.add_resource(SensorItem, "/sensors/<sensor>/")

@api_bp.route("/")
def index():
    return "paska"