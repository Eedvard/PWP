import json
import sys
import os
import pytest
import tempfile
import time
from datetime import datetime
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError
from flask_restful import Resource, Api

from mealplan import db, create_app
from mealplan.models import NutritionInformation, Ingredient, Recipe, RecipeIngredient, RecipeInstructionStep, ShoppingList, ShoppingListIngredient, User

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    app = create_app(config)

    with app.app_context():
        db.create_all()
        _populate_db()

    yield app.test_client()

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)


# TESTING THE USER DB


def _populate_db():
    for i in range(1, 4):
        us = User(
            username="user-{}".format(i)
        )
        re = Recipe(
            name="name-{}".format(i),
            description = "description-{}".format(i),
            recipeYield = "yield-{}".format(i),
            cookTime ="cooktime-{}".format(i),
            recipeCategory = "category-{}".format(i),
            author ="user-{}".format(i),
            datePublished =datetime(2019, i, i, i, i, i)
        )
        db.session.add(us)
        db.session.add(re)
        for j in range(1, 4):
            sl = ShoppingList(
                notes="notes-{}".format(j),
                owner=us
            )
            db.session.add(sl)
            ni = NutritionInformation(
            )
            db.session.add(ni)
            ing = Ingredient(
                name="ingredient-{}".format(j),
                description = "ingredient_description-{}".format(j),
                nutrition_information = ni
            )
            db.session.add(ing)
            ri = RecipeIngredient (
                recipe=re,
                ingredient=ing,
                amount = j,
                unit = "unit-{}".format(j),
            )
            db.session.add(ri)
            ris = RecipeInstructionStep (
                recipe = re,
                step = j,
                text = "text-{}".format(j),
            )
            db.session.add(ris)

    db.session.commit()


def _get_user_json(number=1):
    """
    Creates a valid user JSON object to be used for PUT and POST tests.
    """
    return {"username": "extra-user-{}".format(number)}

def _get_recipe_json(number=1):
    """
    Creates a valid user JSON object to be used for PUT and POST tests.
    """
    return {"name": "extra-name-{}".format(number),"description": "extra-description-{}".format(number),"recipeyield": "extra-yield-{}".format(number),
            "cooktime": "extra-cooktime-{}".format(number),"category": "extra-category-{}".format(number),"author": "extra-user-{}".format(number)
            }

def _get_shoppinglist_json(number=1):
    """
    Creates a valid user JSON object to be used for PUT and POST tests.
    """
    return {"notes": "extra-notes-{}".format(number)}

def _get_recipesteps_json(number=1):
    """
    Creates a valid user JSON object to be used for PUT and POST tests.
    """
    return {"step": 5, "text": "extra-text-{}".format(number)}

def _get_ingredient_json(number=1):
    """
    Creates a valid user JSON object to be used for PUT and POST tests.
    """
    return {"name": "extra-name-{}".format(number), "description": "extra-description-{}".format(number),
            "amount": number,"unit": "extra-unit-{}".format(number)
            }
def _check_namespace(client, response):
    """
     Checks that the "profile" namespace is found from the response body, and
     that its "name" attribute is a URL that can be accessed.
     """
    ns_href = response["@namespaces"]["profile"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200


def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200


def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the control's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204


def _check_control_put_method(ctrl, client, obj):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = _get_user_json()
    body["username"] = obj["username"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204


def _check_control_post_method(ctrl, client, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    if (ctrl == "profile:add-user"):
        body = _get_user_json()
    elif (ctrl == "profile:add-recipe"):
        body = _get_recipe_json()
    elif (ctrl == "profile:add-shoppinglist"):
        body = _get_shoppinglist_json()
    elif (ctrl == "profile:add-step"):
        body = _get_recipesteps_json()
    elif (ctrl == "profile:add-ingredient"):
        body = _get_ingredient_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 204


class TestUserCollection(object):

    RESOURCE_URL = "/api/users/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB population are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        #_check_namespace(client, body)
        _check_control_post_method("profile:add-user", client, body)
        print(body["users"])
        assert len(body["users"]) == 3
        for item in body["users"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "username" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        """

        valid = _get_user_json()

        #test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        #test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["username"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["username"] == "extra-user-1"

        #send same data again for 409
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

class TestUser(object):

    RESOURCE_URL = "/api/users/user-1/"
    INVALID_URL = "/api/users/non-user-x/"
    MODIFIED_URL = "/api/users/extra-user-1/"

    def test_get(self, client):

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["username"] == "user-1"
        #_check_namespace(client, body)
        _check_control_get_method("profile", client, body)
       # _check_control_get_method()
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):

        valid = _get_user_json()

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        #test with another user's name
        valid["username"] = "user-2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # Test with the same users name
        valid["username"] = "user-1"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # remove field for 400
        valid.pop("username")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        valid = _get_user_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["username"] == valid["username"]

    def test_delete(self, client):

       resp = client.delete(self.RESOURCE_URL)
       assert resp.status_code == 204
       resp = client.get(self.RESOURCE_URL)
       assert resp.status_code == 404
       resp = client.delete(self.INVALID_URL)
       assert resp.status_code == 404

class TestRecipeCollection(object):

    RESOURCE_URL = "/api/recipes/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB population are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        #_check_namespace(client, body)
        _check_control_post_method("profile:add-recipe", client, body)
        assert len(body["recipes"]) == 3
        for item in body["recipes"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "name" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        """

        valid = _get_recipe_json()

        #test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        #test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + "4" + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "extra-name-1" and body["description"] == "extra-description-1" and body["cookTime"] == "extra-cooktime-1" and body["recipeCategory"] == "extra-category-1" and body["author"] == "extra-user-1"

        #Sending same data again results in 204 because there are no unique restrictions!
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

class TestRecipe(object):

    RESOURCE_URL = "/api/recipes/1/"
    INVALID_URL = "/api/recipes/0/"

    def test_get(self, client):

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "name-1" and body["description"] == "description-1" and body["cookTime"] == "cooktime-1" and body["recipeCategory"] == "category-1" and body["author"] == "user-1"
        #_check_namespace(client, body)
        _check_control_get_method("profile", client, body)
       # _check_control_get_method()
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):

        valid = _get_recipe_json()

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

    def test_delete(self, client):

       resp = client.delete(self.RESOURCE_URL)
       assert resp.status_code == 204
       resp = client.get(self.RESOURCE_URL)
       assert resp.status_code == 404
       resp = client.delete(self.INVALID_URL)
       assert resp.status_code == 404



class TestShoppingListCollection(object):

    RESOURCE_URL = "/api/users/user-1/shoppinglist/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB population are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        #_check_namespace(client, body)
        _check_control_post_method("profile:add-shoppinglist", client, body)
        assert len(body["shoppinglists"]) == 3
        for item in body["shoppinglists"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "notes" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        """

        valid = _get_shoppinglist_json()

        #test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        #test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + "10" + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        print(body)
        assert body["notes"] == "extra-notes-1" and body["owner"] == "user-1"

        #Sending same data again results in 204 because there are no unique restrictions!
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

class TestShoppinglist(object):

    RESOURCE_URL = "/api/users/user-1/shoppinglist/1/"
    INVALID_URL = "/api/users/not_user-1/shoppinglist/1/"
    INVALID_URL_2 = "/api/users/user-1/shoppinglist/0/"

    def test_get(self, client):

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        print(body)
        assert body["notes"] == "notes-1" and body["owner"] == "user-1"
        #_check_namespace(client, body)
        _check_control_get_method("profile", client, body)
       # _check_control_get_method()
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

        resp = client.get(self.INVALID_URL_2)
        assert resp.status_code == 404

    def test_put(self, client):

        valid = _get_shoppinglist_json()

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        resp = client.put(self.INVALID_URL_2, json=valid)
        assert resp.status_code == 404

    def test_delete(self, client):

       resp = client.delete(self.RESOURCE_URL)
       assert resp.status_code == 204

       resp = client.get(self.RESOURCE_URL)
       assert resp.status_code == 404

       resp = client.delete(self.INVALID_URL)
       assert resp.status_code == 404

       resp = client.delete(self.INVALID_URL_2)
       assert resp.status_code == 404

class TestStepCollection(object):

    RESOURCE_URL = "/api/recipes/1/steps/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB population are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        #_check_namespace(client, body)
        _check_control_post_method("profile:add-step", client, body)
        assert len(body["steps"]) == 3
        for item in body["steps"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "step" in item and "text" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        """

        valid = _get_recipesteps_json()

        #test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        #test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + "5" + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        print(body)
        assert body["text"] == "extra-text-1" and body["step"] == 5

        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

class TestStep(object):

    RESOURCE_URL = "/api/recipes/1/steps/1/"
    INVALID_URL = "/api/recipes/0/steps/1/"
    INVALID_URL_2 = "/api/recipes/1/steps/0/"

    def test_get(self, client):

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        print(body)
        assert body["step"] == 1 and body["text"] == "text-1"
        #_check_namespace(client, body)
        _check_control_get_method("profile", client, body)
       # _check_control_get_method()
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

        resp = client.get(self.INVALID_URL_2)
        assert resp.status_code == 404

    def test_put(self, client):

        valid = _get_shoppinglist_json()

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        resp = client.put(self.INVALID_URL_2, json=valid)
        assert resp.status_code == 404

    def test_delete(self, client):

       resp = client.delete(self.RESOURCE_URL)
       assert resp.status_code == 204

       resp = client.get(self.RESOURCE_URL)
       assert resp.status_code == 404

       resp = client.delete(self.INVALID_URL)
       assert resp.status_code == 404

       resp = client.delete(self.INVALID_URL_2)
       assert resp.status_code == 404

class TestRecipeIngredientCollection(object):

    RESOURCE_URL = "/api/recipes/1/ingredients/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB population are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        #_check_namespace(client, body)
        _check_control_post_method("profile:add-ingredient", client, body)
        assert len(body["ingredients"]) == 3
        for item in body["ingredients"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "amount" and "name" and "unit" and "description" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        """

        valid = _get_ingredient_json()

        #test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        #test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + "10" + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        print(body)
        assert body["name"] == "extra-name-1" and body["description"] == "extra-description-1" and body["unit"] == "extra-unit-1" and body["amount"] == 1

        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

class TestIngredient(object):

    RESOURCE_URL = "/api/recipes/1/ingredients/1/"
    INVALID_URL = "/api/recipes/1/ingredients/0/"
    INVALID_URL_2 = "/api/recipes/0/ingredients/1/"

    def test_get(self, client):

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "ingredient-1" and body["description"] == "ingredient_description-1" and body["unit"] == "unit-1" and body["amount"] == 1
        #_check_namespace(client, body)
        _check_control_get_method("profile", client, body)
       # _check_control_get_method()
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

        resp = client.get(self.INVALID_URL_2)
        assert resp.status_code == 404

    def test_put(self, client):

        valid = _get_shoppinglist_json()

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        resp = client.put(self.INVALID_URL_2, json=valid)
        assert resp.status_code == 404

    def test_delete(self, client):

       resp = client.delete(self.RESOURCE_URL)
       assert resp.status_code == 204

       resp = client.get(self.RESOURCE_URL)
       assert resp.status_code == 404

       resp = client.delete(self.INVALID_URL)
       assert resp.status_code == 404

       resp = client.delete(self.INVALID_URL_2)
       assert resp.status_code == 404
