from flask import Blueprint, send_from_directory, Response, request
from flask_restful import Resource, Api

api_bp = Blueprint("api", __name__, url_prefix="/api", static_folder='static')
api = Api(api_bp)

# this import must be placed after we create api to avoid issues with
# circular imports

from mealplan.resources.users import Users, UserCollection
from mealplan.resources.recipes import RecipeItem, RecipeCollection
from mealplan.resources.steps import Step, StepCollection
from mealplan.resources.ingredients import  Ingredient, IngredientCollection
from mealplan.resources.shoppinglists import  Shoppinglist, ShoppingListCollection
from mealplan import utils
import json

api.add_resource(Users, "/users/<username>/")
api.add_resource(UserCollection, "/users/")
api.add_resource(RecipeCollection, "/recipes/")
api.add_resource(RecipeItem, "/recipes/<recipe_id>/")
api.add_resource(Step, "/recipes/<recipe_id>/steps/<step_id>/")
api.add_resource(StepCollection, "/recipes/<recipe_id>/steps/")

api.add_resource(Ingredient, "/recipes/<recipe_id>/ingredients/<ingredient_id>/", "/users/<username>/shoppinglist/<list_id>/ingredients/<ingredient_id>/")
api.add_resource(IngredientCollection, "/recipes/<recipe_id>/ingredients/", "/users/<username>/shoppinglist/<list_id>/ingredients/")

api.add_resource(Shoppinglist, "/users/<username>/shoppinglist/<list_id>/")
api.add_resource(ShoppingListCollection, "/users/<username>/shoppinglist/")

@api_bp.route("/")
def index():
    body = utils.RecipeBuilder()
    body.add_control_all_recipes()
    body.add_control_add_recipe()
    body.add_control_all_users()
    body.add_control_add_user()
    return Response(json.dumps(body), 200, mimetype=utils.MASON)


@api_bp.route("/profiles/<resource>/")
def send_profile_html(resource):
    print(api_bp.static_folder+"profiles")
    return send_from_directory(api_bp.static_folder+"/profiles", "{}.html".format(resource))


@api_bp.route("/profiles/link-relations/")
def send_link_relations_html():
    return send_from_directory(api_bp.static_folder+"/profiles", "links-relations.html")
