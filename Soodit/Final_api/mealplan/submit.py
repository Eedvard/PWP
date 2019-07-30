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