from flask import Blueprint
from flask_restful import Resource, Api

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# this import must be placed after we create api to avoid issues with
# circular imports

from mealplan.resources.users import Users, UserCollection
from mealplan.resources.recipes import RecipeItem, RecipeCollection
from mealplan.resources.steps import Step, StepCollection
from mealplan.resources.ingredients import  Ingredient, IngredientCollection
from mealplan.resources.shoppinglists import  Shoppinglist, ShoppingListCollection

api.add_resource(Users, "/users/<username>/")
api.add_resource(UserCollection, "/users/")
api.add_resource(RecipeCollection, "/recipes/")
api.add_resource(RecipeItem, "/recipes/<recipe_id>/")
api.add_resource(Step, "/recipes/<recipe_id>/steps/<step_id>/")
api.add_resource(StepCollection, "/recipes/<recipe_id>/steps/")

api.add_resource(Ingredient, "/recipes/<recipe_id>/ingredients/<ingredient_id>/")
api.add_resource(IngredientCollection, "/recipes/<recipe_id>/ingredients/")

api.add_resource(Shoppinglist, "/users/<username>/shoppinglist/<list_id>/")
api.add_resource(ShoppingListCollection, "/users/<username>/shoppinglist/")
@api_bp.route("/")
def index():
    return "paska"