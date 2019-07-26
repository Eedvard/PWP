import os
import pytest
import tempfile
import time
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm.attributes import flag_modified

from mealplan import create_app, db
from mealplan.models import NutritionInformation, Ingredient, Recipe, RecipeIngredient, RecipeInstructionStep, ShoppingList, ShoppingListIngredient, User

def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


#based on http://flask.pocoo.org/docs/1.0/testing/
@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()
    yield app

    os.close(db_fd)
    os.unlink(db_fname)

def _get_NutritionInformation():
    return NutritionInformation(
        servingSize = 9,
        servingSizeUnit = "g",
        calories = 299,
        carbohydrateContent = 7,
        cholesterolContent = 8,
        fatContent = 32,
        fiberContent = 92,
        proteinContent = 58,
        saturatedFatContent = 84,
        sodiumContent = 70,
        sugarContent = 88,
        transFatContent = 14,
        unsaturatedFatContent = 87
    )
def _get_Ingredient():
    return Ingredient(
        name="potato",
        description = "potato is a potato"
    )
def _get_Recipe():
    return Recipe(
        name = "chickensoup",
        description = "nice soup",
        recipeYield = "9 servings",
        cookTime = "5 hours",
        recipeCategory = "soup",
        author = "Ville",
        datePublished = datetime(2019, 1, 1, 0, 0, 1)
    )
def _get_RecipeIngredient():
    return RecipeIngredient(
        amount=5,
        unit="kg"
    )
def _get_RecipeInstructionStep():
    return RecipeInstructionStep(
        step = 5,
        text = "boil the potatoes"
    )
def _get_ShoppingList():
    return ShoppingList(
        notes = "buy some cheese"
    )
def _get_ShoppingListIngredient():
    return ShoppingListIngredient(
        amount = 5,
        unit = "dl"
    )
def _get_User():
    return User(
        username = "rille"
    )


def createdb():
    nutri = _get_NutritionInformation()
    ingredient = _get_Ingredient()
    recipe = _get_Recipe()
    recipei = _get_RecipeIngredient()
    recipestep = _get_RecipeInstructionStep()
    shoplist = _get_ShoppingList()
    shoplisti = _get_ShoppingListIngredient()
    user = _get_User()

    ingredient.nutrition_information = nutri
    recipe.nutrition_information = nutri
    recipei.recipe = recipe
    recipei.ingredient = ingredient
    recipestep.recipe = recipe
    shoplisti.shopping_list = shoplist
    shoplisti.ingredient = ingredient
    shoplist.owner = user

    return nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user

def test_create_instances(app):  # testing the creation of the database and that the relations are working properly. Making sure that the information can retrieved from the database

    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user = createdb()
    with app.app_context():

        db.session.add(nutri)
        db.session.add(ingredient)
        db.session.add(recipe)
        db.session.add(recipei)
        db.session.add(recipestep)
        db.session.add(shoplist)
        db.session.add(shoplisti)
        db.session.add(user)
        db.session.commit()

        assert NutritionInformation.query.count() == 1
        assert Ingredient.query.count() == 1
        assert Recipe.query.count() == 1
        assert RecipeIngredient.query.count() == 1
        assert RecipeInstructionStep.query.count() == 1

        assert ingredient.nutrition_information == NutritionInformation.query.first()
        assert ingredient.nutrition_information_id == NutritionInformation.query.first().id
        assert recipe.nutrition_information == NutritionInformation.query.first()
        assert recipe.nutritionInformation_id == NutritionInformation.query.first().id
        assert recipei.recipe == Recipe.query.first()
        assert recipei.recipe_id == Recipe.query.first().id
        assert recipei.ingredient == Ingredient.query.first()
        assert recipei.ingredient_id == Ingredient.query.first().id
        assert recipestep.recipe == Recipe.query.first()
        assert recipestep.recipe_id == Recipe.query.first().id

        assert shoplisti.shopping_list == ShoppingList.query.first()
        assert shoplisti.ingredient == Ingredient.query.first()


#This test will make sure that editing model will also have effect with the foreign keys
def test_edit_nutri(app):
    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user = createdb()

    with app.app_context():

        db.session.add(nutri)
        db.session.add(ingredient)
        db.session.add(recipe)
        db.session.add(recipei)
        db.session.add(recipestep)
        db.session.add(shoplist)
        db.session.add(shoplisti)
        db.session.add(user)

        db.session.commit()

        test = NutritionInformation.query.first()
        test.servingSize = 5
        db.session.merge(test)
        flag_modified(test, "servingSize")
        db.session.commit()
        assert NutritionInformation.query.first().servingSize == 5
        assert Ingredient.query.first().nutrition_information.servingSize == 5
        assert Recipe.query.first().nutrition_information.servingSize == 5

        test2 = Ingredient.query.first()
        test2.id = 3
        db.session.merge(test2)
        db.session.commit()
        assert Ingredient.query.first().id == 3
        #assert RecipeIngredient.query.first().ingredient_id == 3
        #assert ShoppingListIngredient.query.first().ingredient_id == 3

        test3 = Recipe.query.first()
        test3.id = 4
        db.session.merge(test3)
        db.session.commit()
        assert Recipe.query.first().id == 4
        #assert RecipeInstructionStep.query.first().recipe_id == 4
        #assert RecipeIngredient.query.first().recipe_id == 4
        #assert MealRecipe.query.first().recipe_id == 4

        test5 = ShoppingList.query.first()
        test5.id = 6
        db.session.merge(test5)
        db.session.commit()
        assert ShoppingList.query.first().id == 6
        #assert ShoppingListIngredient.query.first().shopping_list_id == 5

        test6 = User.query.first()
        test6.id = 7
        db.session.merge(test6)
        db.session.commit()
        assert User.query.first().id == 7
        #assert WeeklyPlan.query.first().user_id == 7



##Following testcases are testing that the removal of existing model is handled properly by foreign keys
#
def test_measurement_ondelete_nutri(app):

    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user = createdb()

    with app.app_context():

        db.session.add(nutri)
        db.session.add(ingredient)
        db.session.add(recipe)
        db.session.add(recipei)
        db.session.add(recipestep)
        db.session.add(user)
        db.session.commit()

        db.session.delete(nutri)
        db.session.commit()

        assert Recipe.query.first().nutrition_information is None
        assert Ingredient.query.first().nutrition_information is None
        assert NutritionInformation.query.first() is None

def test_measurement_ondelete_ingredient(app):

    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user = createdb()

    with app.app_context():

        db.session.add(nutri)
        db.session.add(ingredient)
        db.session.add(recipe)
        db.session.add(recipei)
        db.session.add(recipestep)
        db.session.add(shoplist)
        db.session.add(shoplisti)
        db.session.add(user)

        db.session.commit()

        db.session.delete(ingredient)
        db.session.commit()

        assert RecipeIngredient.query.first() is None
        assert ShoppingListIngredient.query.first() is None
        assert Ingredient.query.first() is None

def test_measurement_ondelete_recipe(app):

    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user = createdb()


    with app.app_context():

        db.session.add(nutri)
        db.session.add(ingredient)
        db.session.add(recipe)
        db.session.add(recipei)
        db.session.add(recipestep)
        db.session.add(shoplist)
        db.session.add(shoplisti)
        db.session.add(user)

        db.session.commit()
        db.session.delete(recipe)
        db.session.commit()

        assert Recipe.query.first() is None
        assert RecipeIngredient.query.first() is None
        assert RecipeInstructionStep.query.first() is None


def test_measurement_ondelete_shoplist(app):


    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user = createdb()

    with app.app_context():

        db.session.add(nutri)
        db.session.add(ingredient)
        db.session.add(recipe)
        db.session.add(recipei)
        db.session.add(recipestep)
        db.session.add(shoplist)
        db.session.add(shoplisti)
        db.session.add(user)


        db.session.commit()

        db.session.delete(shoplist)
        db.session.commit()

        assert ShoppingList.query.first() is None
        assert ShoppingListIngredient.query.first() is None
        assert Ingredient.query.first() is None


def test_measurement_ondelete_user(app):


    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user = createdb()

    with app.app_context():

        db.session.add(nutri)
        db.session.add(ingredient)
        db.session.add(recipe)
        db.session.add(recipei)
        db.session.add(recipestep)
        db.session.add(shoplist)
        db.session.add(shoplisti)
        db.session.add(user)

        db.session.commit()

        db.session.delete(user)
        db.session.commit()

        assert User.query.first() is None
        assert ShoppingList.query.first() is None
