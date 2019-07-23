import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from mealplan import app

USER_PROFILE = "/profiles/users/"
INGREDIENT_PROFILE = "/profiles/ingredients/"
RECIPE_PROFILE = "/profiles/recipes/"
SHOPLIST_PROFILE = "/profiles/shoppinglists/"
STEPS_PROFILE = "/profiles/steps/"

LINK_RELATIONS_URL = "/profile/link_relations/"


@app.route("/profiles/<resource>")
def send_profile_html(resource):
    return send_from_directory(app.static_folder, "{}.html".format(resource))


@app.route("/profile/link-relations/")
def send_link_relations_html():
    return send_from_directory(app.static_folder, "{}.html")
