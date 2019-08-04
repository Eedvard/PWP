from flask import Flask
import json
import os
import re
import requests
import sys
import time
from dataclasses import dataclass
from tinytag import TinyTag, TinyTagexception

API_URL = "http://private-47b898-pwpkesa.apiary-mock.com"
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

# valitaan haluttu resepti jos löytyy samalla nimellä useita

def prompt_recipe_choice(name, hits):

    print("The following recipes were found with '{}'".format(name))
    for i, recipe in enumerate(hits, 1):
        print("{i}: {name} ({description},{recipeyield},{cookTime},{recipeCategory},{author},{datePublished}}".format(i=i, **recipe))
    choice = int(input("Choose artist by typing a number: "))
    return items[choice - 1]

# etsii collectionista reseptin. Jos samannimisiä reseptejä, niin tulostaa ne ja pyörittää prompt_recipe_choice()

def find_recipe_href(name, collection):
    name = name.lower()
    hits = []
    for item in collection:
        if item["name"].lower() == name:
            hits.append(item)
    if len(hits) == 1:
        return hits[0]["@controls"]["self"]["href"]
    elif len(hits) >= 2:
        return prompt_recipe_choice(name, hits)["@controls"]["self"]["href"]
    else:
        return None

# etsii collectionista ruoka-aineen

def find_ingredient_href(name, collection)
    name = name.lower()
    for item in collection:
        if item["name"].lower()== name:
            return item["@controls"]["self"]["href"]
    return None

# Etsii collectionista käyttäjän

def find_user_href(username, collection)
    username = username.lower()
    for item in collection:
        if item["username"].lower() == username:
            return item["@controls"]["self"]["href"]
    return None



def find_recipe_item(tag, collection):
    name = tag.name.lower()
    hits = []
    for item in collection:
        if item["name"].lower() == name:
            hits.append(item)
    if len(hits) == 1:
        return hits[0]
    elif len(hits) >= 2:
        author_n = tag.author or 1
        date_n = tag.date
        for item in hits:
            if item["author"] == author_n and item["datePublished"] == date_n:
                return item
        return None
    else:
        author_n = tag.author or 1
        date_n = tag.date
        for item in collection:
            if item["datePublished"] == date_n and item["author"] == author_n:
                return item
        return None

def submit_data(s, ctrl, data):

    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers = {"Content-type": "application/json"}
    )
    return resp

