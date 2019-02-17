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
from app import NutritionInformation, Ingredient, Recipe, RecipeIngredient, RecipeInstructionStep


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
    )
def _get_Ingredient():
    return Ingredient(
        name="potato"
    )
def _get_Recipe():
    return Recipe(
        name = "chickensoup"
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

def test_create_instances(db_handle):

    nutri = _get_NutritionInformation()
    ingredient = _get_Ingredient()
    recipe = _get_Recipe()
    recipei = _get_RecipeIngredient()
    recipestep = _get_RecipeInstructionStep()

    ingredient.nutrition_information = nutri
    recipe.nutrition_information = nutri
    recipei.recipe = recipe
    recipei.ingredient = ingredient
    recipestep.recipe = recipe

    db.session.add(nutri)
    db.session.add(ingredient)
    db.session.add(recipe)
    db.session.add(recipei)
    db.session.add(recipestep)
    db.session.commit()

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