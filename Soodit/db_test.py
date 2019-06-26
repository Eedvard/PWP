import os
import pytest
import tempfile
import time
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError
import app
from app import db
from app import NutritionInformation, Ingredient, Recipe, RecipeIngredient, RecipeInstructionStep, ShoppingList, ShoppingListIngredient, User, Like


def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True

    with app.app.app_context():
        app.db.create_all()

    yield app.db

    os.close(db_fd)

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
        datePublished = datetime(2019, 1, 1, 0, 0, 1),
        number_of_likes = 10
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
def _get_Likes():
    return Like(
        likes = True
    )

def createdb(db_handle):
    nutri = _get_NutritionInformation()
    ingredient = _get_Ingredient()
    recipe = _get_Recipe()
    recipei = _get_RecipeIngredient()
    recipestep = _get_RecipeInstructionStep()
    shoplist = _get_ShoppingList()
    shoplisti = _get_ShoppingListIngredient()
    user = _get_User()
    likes = _get_Likes()

    ingredient.nutrition_information = nutri
    recipe.nutrition_information = nutri
    recipei.recipe = recipe
    recipei.ingredient = ingredient
    recipestep.recipe = recipe
    shoplisti.shopping_list = shoplist
    shoplisti.ingredient = ingredient
    likes.recipe = recipe
    likes.user = user

    return nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user, likes

def test_create_instances(db_handle):  # testing the creation of the database and that the relations are working properly. Making sure that the information can retrieved from the database

    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user, likes = createdb(db_handle)

    db_handle.session.add(nutri)
    db_handle.session.add(ingredient)
    db_handle.session.add(recipe)
    db_handle.session.add(recipei)
    db_handle.session.add(recipestep)
    db_handle.session.add(shoplist)
    db_handle.session.add(shoplisti)
    db_handle.session.add(user)
    db_handle.session.add(likes)


    db_handle.session.commit()

    assert NutritionInformation.query.count() == 1
    assert Ingredient.query.count() == 1
    assert Recipe.query.count() == 1
    assert RecipeIngredient.query.count() == 1
    assert RecipeInstructionStep.query.count() == 1

    assert ingredient.nutrition_information == NutritionInformation.query.first()
    assert ingredient.nutrition_nformation_id == NutritionInformation.query.first().id
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
def test_edit_nutri(db_handle): 


    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user, likes = createdb(db_handle)
    db_handle.session.add(nutri)
    db_handle.session.add(ingredient)
    db_handle.session.add(recipe)
    db_handle.session.add(recipei)
    db_handle.session.add(recipestep)
    db_handle.session.add(shoplist)
    db_handle.session.add(shoplisti)
    db_handle.session.add(user)
    db_handle.session.add(likes)

    db_handle.session.commit()

    test = NutritionInformation.query.first()
    test.id = 2
    db_handle.session.commit()
    assert NutritionInformation.query.first().id == 2
    #assert Ingredient.query.first().nutrition_nformation_id == 2
    #assert Recipe.query.first().nutritionInformation_id == 2

    test2 = Ingredient.query.first()
    test2.id = 3
    db_handle.session.commit()
    assert Ingredient.query.first().id == 3
    #assert RecipeIngredient.query.first().ingredient_id == 3
    #assert ShoppingListIngredient.query.first().ingredient_id == 3

    test3 = Recipe.query.first()
    test3.id = 4
    db_handle.session.commit()
    assert Recipe.query.first().id == 4
    #assert RecipeInstructionStep.query.first().recipe_id == 4
    #assert RecipeIngredient.query.first().recipe_id == 4
    #assert MealRecipe.query.first().recipe_id == 4


    test5 = ShoppingList.query.first()
    test5.id = 6
    db_handle.session.commit()
    assert ShoppingList.query.first().id == 6
    #assert ShoppingListIngredient.query.first().shopping_list_id == 5

    test6 = User.query.first()
    test6.id = 7
    db_handle.session.commit()
    assert User.query.first().id == 7
    #assert WeeklyPlan.query.first().user_id == 7
    #assert Like.query.first().user_id == 7



#Following testcases are testing that the removal of existing model is handled properly by foreign keys

def test_measurement_ondelete_nutri(db_handle):

    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user, likes = createdb(db_handle)


    db_handle.session.add(nutri)
    db_handle.session.add(ingredient)
    db_handle.session.add(recipe)
    db_handle.session.add(recipei)
    db_handle.session.add(recipestep)
    db_handle.session.add(user)
    db_handle.session.commit()
    db_handle.session.delete(nutri)
    db_handle.session.commit()


    assert recipe.nutrition_information is None
    assert recipe.nutrition_information is None

def test_measurement_ondelete_ingredient(db_handle):

    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user, likes = createdb(db_handle)

    db_handle.session.add(nutri)
    db_handle.session.add(ingredient)
    db_handle.session.add(recipe)
    db_handle.session.add(recipei)
    db_handle.session.add(recipestep)
    db_handle.session.add(shoplist)
    db_handle.session.add(shoplisti)
    db_handle.session.add(user)
    db_handle.session.add(likes)


    db_handle.session.commit()

    db_handle.session.delete(ingredient)
    db_handle.session.commit()

    assert recipei.ingredient is None
    assert shoplisti.ingredient is None

def test_measurement_ondelete_recipe(db_handle):

    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user, likes = createdb(db_handle)


    db_handle.session.add(nutri)
    db_handle.session.add(ingredient)
    db_handle.session.add(recipe)
    db_handle.session.add(recipei)
    db_handle.session.add(recipestep)
    db_handle.session.add(shoplist)
    db_handle.session.add(shoplisti)
    db_handle.session.add(user)
    db_handle.session.add(likes)

    db_handle.session.commit()

    db_handle.session.delete(recipe)
    db_handle.session.commit()

    assert recipei.recipe is None
    assert recipestep.recipe is None


def test_measurement_ondelete_shoplist(db_handle):


    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user, likes = createdb(db_handle)
    db_handle.session.add(nutri)
    db_handle.session.add(ingredient)
    db_handle.session.add(recipe)
    db_handle.session.add(recipei)
    db_handle.session.add(recipestep)
    db_handle.session.add(shoplist)
    db_handle.session.add(shoplisti)
    db_handle.session.add(user)
    db_handle.session.add(likes)


    db_handle.session.commit()

    db_handle.session.delete(shoplist)
    db_handle.session.commit()

    assert shoplisti.shopping_list is None



def test_measurement_ondelete_user(db_handle):


    nutri, ingredient, recipe, recipei, recipestep, shoplist, shoplisti, user, likes = createdb(db_handle)
    db_handle.session.add(nutri)
    db_handle.session.add(ingredient)
    db_handle.session.add(recipe)
    db_handle.session.add(recipei)
    db_handle.session.add(recipestep)
    db_handle.session.add(shoplist)
    db_handle.session.add(shoplisti)
    db_handle.session.add(user)
    db_handle.session.add(likes)


    db_handle.session.commit()

    db_handle.session.delete(user)
    db_handle.session.commit()
    #assert user.id is None
