import json
from flask import Flask, Response, request, url_for
from mealplan import api

ERROR_PROFILE="/api/profiles/errors/"
MASON="/api/application/vnd.mason+json"
REC_PROFILE="/api/profiles/recipes/"
ING_PROFILE="/api/profiles/ingredients/"
STEPS_PROFILE = "/api/profiles/steps/"
USER_PROFILE = "/api/profiles/users/"
SHOPLIST_PROFILE= "/api/profiles/shoppinglists/"
LINK_RELATIONS_URL = "/api/profiles/link-relations/"

class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


class RecipeBuilder(MasonBuilder):      # Recipebuilder is based on the inventorybuilder that was in the course examples

    def create_error_response(status_code, title, message=None):
        resource_url = request.path
        body = MasonBuilder(resource_url=resource_url)
        body.add_error(title, message)
        body.add_control("profile", href=ERROR_PROFILE)
        return Response(json.dumps(body), status_code, mimetype=MASON)

    @staticmethod
    def user_schema():
        schema = {
            "type": "object",
            "required": ["username"]
        }
        props = schema["properties"] = {}
        props["username"] = {
            "description": "User's unique name",
            "type": "string"
        }
        return schema

    @staticmethod
    def recipe_schema():
        schema = {
            "type": "object",
            "required": ["name", "description", "recipeyield", "cooktime", "category", "author"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Recipe's name",
            "type": "string"
        }
        props["description"] = {
            "description": "A short description about the recipe",
            "type": "string"
        }
        props["recipeyield"] = {
            "description": "Number of portions the recipe will yield",
            "type": "string"
        }
        props["cooktime"] = {
            "description": "The time it takes to prepare the food",
            "type": "string"
        }
        props["category"] = {
            "description": "The category the recipe belongs to",
            "type": "string"
        }
        props["author"] = {
            "description": "Username of the author of the recipe",
            "type": "string"
        }
        return schema

    @staticmethod
    def step_schema():
        schema = {
            "type": "object",
            "required": ["step", "text"]
        }
        props = schema["properties"] = {}
        props["step"] = {
            "description": "The number of the step",
            "type": "integer"
        }
        props["text"] = {
            "description": "The instruction of the step",
            "type": "string"
        }
        return schema

    @staticmethod
    def shoppinglist_schema():
        schema = {
            "type": "object"
        }
        props = schema["properties"] = {}
        props["notes"] = {
            "description": "The shopping list note like foodstuff",
            "type": "string"
        }
        return schema

    @staticmethod
    def ingredient_schema():
        schema = {
            "type": "object",
            "required": ["name", "description", "amount", "unit"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "The name of the ingredient",
            "type": "string"
        }
        props["description"] = {
            "description": "The description of the ingredient",
            "type": "string"
        }
        props["amount"] = {
            "description": "The amount of foodstuff needed",
            "type": "integer"
        }
        props["unit"] = {
            "description": "grams, litres etc",
            "type": "string"
        }
        return schema

    @staticmethod
    def shoppinglistingredient_schema():
        schema = {
            "type": "object",
            "required": ["amount", "unit"]
        }
        props = schema["properties"] = {}
        props["amount"] = {
            "description": "The amount of foodstuff needed",
            "type": "integer"
        }
        props["unit"] = {
            "description": "grams, litres etc",
            "type": "string"
        }
        return schema

    #RECIPE METHODS

    def add_control_all_recipes(self):
        self.add_control(
            "profile:recipes-all",
            "/api/recipes/",
            method="GET",
            title="Get all recipes"
        )

    def add_control_add_recipe(self):
        self.add_control(
            "profile:add-recipe",
            "/api/recipes/",
            method="POST",
            encoding="json",
            title="Add a new recipe",
            schema=self.recipe_schema()
        )

    def add_control_edit_recipe(self, recipe_id):
        self.add_control(
            "profile:edit-recipe",
            href=url_for("api.recipeitem", recipe_id=recipe_id),
            method="PUT",
            encoding="json",
            title="Edit an existing recipe",
            schema=self.recipe_schema()
        )

    def add_control_delete_recipe(self, recipe_id):
        self.add_control(
            "profile:delete",
            href=url_for("api.recipeitem", recipe_id=recipe_id),
            method="DELETE",
            title="Delete this resource"
        )

    # USER METHODS

    def add_control_all_users(self):
        self.add_control(
            "profile:users-all",
            "/api/users/",
            method="GET",
            title="Get all users"
        )

    def add_control_add_user(self):
        self.add_control(
            "profile:add-user",
            "/api/users/",
            method="POST",
            encoding="json",
            title="Add a new user",
            schema=self.user_schema()
        )

    def add_control_edit_user(self, username):
        self.add_control(
            "profile:edit-user",
            href=url_for("api.users", username=username),
            method="PUT",
            encoding="json",
            title="Edit an existing user",
            schema=self.user_schema()
        )

    def add_control_delete_user(self, username):
        self.add_control(
            "profile:delete",
            href=url_for("api.users", username=username),
            method="DELETE",
            title="Delete this resource"
        )

    #recipeIngredient controls

    def add_control_all_recipe_ingredients(self, recipe_id):
        self.add_control(
            "profile:ingredients-all",
            href=url_for("api.ingredientcollection", recipe_id=recipe_id),
            method="GET",
            title="Get all ingredients of recipe"
        )

    def add_control_add_recipe_ingredient(self, recipe_id):
        self.add_control(
            "profile:add-ingredient",
            href=url_for("api.ingredientcollection", recipe_id=recipe_id),
            method="POST",
            encoding="json",
            title="Add a new ingredient to recipe",
            schema=self.ingredient_schema()
        )

    def add_control_edit_recipe_ingredient(self, recipe_id, ingredient_id):
        self.add_control(
            "profile:edit-ingredient",
            href=url_for("api.ingredient", recipe_id=recipe_id,ingredient_id=ingredient_id),
            method="PUT",
            encoding="json",
            title="Edit an existing ingredient",
            schema=self.ingredient_schema()
        )

    def add_control_delete_recipe_ingredient(self, recipe_id, ingredient_id):
        self.add_control(
            "profile:delete",
            href=url_for("api.ingredient", recipe_id=recipe_id, ingredient_id=ingredient_id),
            method="DELETE",
            title="Delete this resource"
        )
#Shoppinglist Ingredient controls

    def add_control_all_shoplist_ingredients(self, username, list_id):
        self.add_control(
            "profile:ingredients-all",
            href=url_for("api.ingredientcollection", username=username, list_id=list_id),
            method="GET",
            title="Get all ingredients of recipe"
        )

    def add_control_add_shoplist_ingredient(self, username, list_id):
        self.add_control(
            "profile:add-ingredient",
            href=url_for("api.ingredientcollection", username=username, list_id=list_id),
            method="POST",
            encoding="json",
            title="Add a new ingredient to recipe",
            schema=self.ingredient_schema()
        )

    def add_control_edit_shoplist_ingredient(self, username, list_id, ingredient_id):
        self.add_control(
            "profile:edit-user",
            href=url_for("api.ingredient", username=username, list_id=list_id, ingredient_id=ingredient_id),
            method="PUT",
            encoding="json",
            title="Edit an existing ingredient",
            schema=self.ingredient_schema()
        )

    def add_control_delete_shoplist_ingredient(self, username, list_id, ingredient_id):
        self.add_control(
            "profile:delete",
            href=url_for("api.ingredient", username=username, list_id=list_id, ingredient_id=ingredient_id),
            method="DELETE",
            title="Delete this resource"
        )


# Step controls

    def add_control_all_steps(self, recipe_id):
        self.add_control(
            "profile:steps-all",
            href=url_for("api.stepcollection", recipe_id=recipe_id),
            method="GET",
            title="Get all steps of recipe"
        )

    def add_control_add_step(self, recipe_id):
        self.add_control(
            "profile:add-step",
            href=url_for("api.stepcollection", recipe_id=recipe_id),
            method="POST",
            encoding="json",
            title="Add a new step to recipe",
            schema=self.step_schema()
        )

    def add_control_edit_step(self, recipe_id, step_id):
        self.add_control(
            "profile:edit-step",
            href=url_for("api.step", recipe_id=recipe_id,step_id=step_id),
            method="PUT",
            encoding="json",
            title="Edit an existing step",
            schema=self.step_schema()
        )

    def add_control_delete_step(self, recipe_id, step_id):
        self.add_control(
            "profile:delete",
            href=url_for("api.step", recipe_id=recipe_id, step_id=step_id),
            method="DELETE",
            title="Delete this resource"
        )

# Shoppinglist controls

    def add_control_all_shoppinglists(self, username):
        self.add_control(
            "profile:shoppinglists-all",
            href=url_for("api.shoppinglistcollection", username=username),
            method="GET",
            title="Get all shoppinglists of user"
        )

    def add_control_add_shoppinglist(self, username):
        self.add_control(
            "profile:add-shoppinglist",
            href=url_for("api.shoppinglistcollection", username=username),
            method="POST",
            encoding="json",
            title="Create new shoppinglist",
            schema=self.shoppinglist_schema()
        )

    def add_control_edit_shoppinglist(self, username, list_id):
        self.add_control(
            "profile:edit-step",
            href=url_for("api.shoppinglist", username=username, list_id=list_id),
            method="PUT",
            encoding="json",
            title="Edit an existing shoppinglist",
            schema=self.shoppinglist_schema()
        )

    def add_control_delete_shoppinglist(self, username, list_id):
        self.add_control(
            "profile:delete",
            href=url_for("api.shoppinglist", username=username, list_id=list_id),
            method="DELETE",
            title="Delete this resource"
        )