from flask import Flask
import json
import os
import re
import requests
import sys
import time
from dataclasses import dataclass
from tinytag import TinyTag, TinyTagexception

API_URL =
ISO_DATE = "%Y-%m-%d"
ISO_TIME = "%H:%M:%S"
DATE_FORMATS = ["%Y", ISO_DATE]

API_TAG_RECIPE_MAPPING = {
    "name" : "recipename",
    "description" : "recipedesc",
    "recipeYield" : "yield",
    "cookTime": "time",
    "author" : "authorname",
    "datePublished" : "date"
}

API_TAG_INGREDIENT_MAPPING = {
    "name" : "ingredient",
    "description" : "ingredientdesc"
}

API_TAG_USER_MAPPING = {
    "username" : "user"
}

API_TAG_SHOPLIST_TAGGING = {
    "notes" : "note"
}

API_TAG_RECIPESTEP_MAPPING = {
    "step" : "step",
    "text" : "instruction"
}

class APIError(Exception):
    """
    used when API responds with an error code
    """
    def __init__(self, code, error):

        self.error = json.loads(error)
        self.code = code

    def __str__(self):

        return "Error {code} while accessing {uri}\nDetails:\n{msgs}".format(
            code=self.code,
            uri=self.error["resource_url"],
            msg=self.error["@error"]["@messages"],
            msgs="\n".join(self.error["@error"]["@messages"])
        )

def make_iso_format_date(value):

    for form in DATE_FORMATS:
        try:
            date = time.strptime(value, form)
            value = time.strftime(ISO_DATE, date)
            break
        except ValueError:
            pass
    else:
        value = input("Type ISO format date that matches {}".format(value))
    return value

def make_iso_format_time(value):

    return time.strftime(ISO_TIME, time.gmtime(value))

def prompt_recipe_choice(name, hits):

    print("The following recipes were found with '{}'".format(name))
    for i, recipe in enumerate(hits, 1):
        print("{i}: {name} ({description},{recipeyield},{cookTime},{recipeCategory},{author},{datePublished}}".format(i=i, **recipe))
    choice = int(input("Choose artist by typing a number: "))
    return items[choice - 1]