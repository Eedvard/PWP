import json
from flask import Flask, Response, request

ERROR_PROFILE="/profiles/errors/"
MASON="application/vnd.mason+json"

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


class RecipeBuilder(MasonBuilder):
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
            "required": ["name", "description", "recipeYield", "cookTime", "recipeCategory", "author", "datePublished"]
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
        props["recipeYield"] = {
            "description": "Number of portions the recipe will yield",
            "type": "string"
        }
        props["cookTime"] = {
            "description": "The time it takes to prepare the food",
            "type": "string"
        }
        props["recipeCategory"] = {
            "description": "The category the recipe belongs to",
            "type": "string"
        }
        props["author"] = {
            "description": "Username of the author of the recipe",
            "type": "string"
        }
        props["datePublished"] = {
            "description": "The date the recipe was published",
            "type": "dateTime"
        }
        return schema

    @staticmethod
    def step_schema():
        schema = {
            "type": "object",
            "required": ["text"]
        }
        props = schema["properties"] = {}
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

    #RECIPE METHODS

    def add_control_add_recipe(self):
        self.add_control(
            "profile:add-recipe",
            "/api/recipes/",
            method="POST",
            encoding="json",
            title="Add a new recipe",
            schema=self.recipe_schema()
        )

    def add_control_edit_recipe(self):
        self.add_control(
            "profile:edit-recipe",
            "api/recipes/{id}",
            method="PUT",
            encoding="json",
            title="Edit an existing recipe",
            schema=self.recipe_schema()
        )

    # USER METHODS

    def add_control_add_user(self):
        self.add_control(
            "profile:add-user",
            "/api/users/",
            method="POST",
            encoding="json",
            title="Add a new user",
            schema=self.user_schema()
        )

    def add_control_edit_user(self):
        self.add_control(
            "profile:edit-user",
            "/api/users/{id}",
            method="PUT",
            encoding="json",
            title="Edit an existing user",
            schema=self.user_schema()
        )

    def add_control_delete(self, href):
        self.add_control(
            "profile:delete",
            hreh=href,
            method="DELETE",
            title="Delete this resource"
        )
