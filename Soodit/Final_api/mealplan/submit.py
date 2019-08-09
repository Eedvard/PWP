from flask import Flask
import json
import os
import re
import requests
import sys
import time
from dataclasses import dataclass
from tinytag import TinyTag, TinyTagException

import PySimpleGUI as sg

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
    items = []
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

def find_ingredient_href(name, collection):
    name = name.lower()
    for item in collection:
        if item["name"].lower()== name:
            return item["@controls"]["self"]["href"]
    return None

# Etsii collectionista käyttäjän

def find_user_href(username, collection):
    username = username.lower()
    for item in collection:
        if item["username"].lower() == username:
            return item["@controls"]["self"]["href"]
    return None

def find_user_item(username, collection):
    username = username
    hits = []
    for item in collection:
        if item["username"] == username:
            hits.append(item)
    if len(hits) == 1:
        return hits[0]
    else:
        return None

def find_recipe_item(tag, collection):
    name = tag["name"].lower()
    hits = []
    for item in collection:
        if item["name"].lower() == name:
            hits.append(item)
    if len(hits) == 1:
        return hits[0]
    elif len(hits) >= 2:
        author_n = tag["author"] or 1
        date_n = tag["datePublished"]
        for item in hits:
            if item["author"] == author_n and item["datePublished"] == date_n:
                return item
        return None
    else:
        author_n = tag["author"] or 1
        date_n = tag["datePublished"]
        for item in collection:
            if item["datePublished"] == date_n and item["author"] == author_n:
                return item
        return None


def create_with_mapping(s, tag, ctrl, mapping):
    """
    create_with_mapping(s, tag, ctrl, mapping) -> string

    Creates an album or track dictionary for submitting a resource to the API.
    The data is constructed by using the *ctrl* object's schema as a template and
    reading corresponding values from *tag* by using the *mapping* dictionary.
    Values are converted to types and format required by the schema. If creation
    is successful, the new resource's URI is returned. Otherwiser APIError is
    raised.
    """

    body = {}
    schema = ctrl["schema"]
    for name, props in schema["properties"].items():
        local_name = mapping[name]
        value = getattr(tag, local_name)
        if value is not None:
            value = convert_value(value, props)
            body[name] = value

    resp = submit_data(s, ctrl, body)
    if resp.status_code == 201:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)

def sendreq(s, ctrl):

    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        headers = {"Content-type": "application/json"}
    )
    return resp


def submit_data(s, ctrl, data):

    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers = {"Content-type": "application/json"}
    )
    return resp


def create_user(s, username, ctrl):

    body = {}
    ctrl = ctrl["profile:add-user"]
    schema = ctrl["schema"]
    for field in schema["required"]:
        if field == "username":
            body[field] = username
        else:
            print("Unknown required field '{}'".format(field))
            body[field] = input("Provide value: ")
    print(body)
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)


def create_recipe(s, recipeargs, ctrl):
    body = {}
    ctrl = ctrl["profile:add-recipe"]
    schema = ctrl["schema"]
    for field in schema["required"]:
        if field == "name":
            body[field] = recipeargs[0]
        elif field == "description":
            body[field] = recipeargs[1]
        elif field == "recipeyield":
            body[field] = recipeargs[2]
        elif field == "cooktime":
            body[field] = recipeargs[3]
        elif field == "category":
            body[field] = recipeargs[4]
        elif field == "author":
            body[field] = recipeargs[5]
    print(body)
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)



def create_ingredient(s, ingrargs, ctrl):
    body = {}
    ctrl = ctrl["profile:add-ingredient"]
    schema = ctrl["schema"]
    for field in schema["required"]:
        if field == "name":
            body[field] = ingrargs[0]
        elif field == "description":
            body[field] = ingrargs[1]
        elif field == "amount":
            body[field] = ingrargs[2]
        elif field == "unit":
            body[field] = ingrargs[3]
        elif field == "servingsize":
            body[field] = ingrargs[4]
        elif field == "servingsizeunit":
            body[field] = ingrargs[5]
    print(body)
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)

def get_users(s, ctrl):

    href = ctrl["profile:users-all"]["href"]
    resp = s.get(API_URL + href)
    body = resp.json()
    return body["users"]

def get_shoppinglists(s, ctrl):

    href = ctrl["profile:shoppinglists-all"]["href"]
    resp = s.get(API_URL + href)
    body = resp.json()
    return body["shoppinglists"]

def get_recipes(s, ctrl):

    href = ctrl["profile:recipes-all"]["href"]
    resp = s.get(API_URL + href)
    body = resp.json()
    return body["recipes"]

def get_ingredients(s, ctrl):

    href = ctrl["profile:ingredients-all"]["href"]
    resp = s.get(API_URL + href)
    body = resp.json()
    return body["ingredients"]

def get_steps(s, ctrl):

    href = ctrl["profile:steps-all"]["href"]
    resp = s.get(API_URL + href)
    body = resp.json()
    return body["steps"]

class Input_error(BaseException):
    pass

class Client():

    def __init__(self):
        self.clientstate = 0
        self.button = 0
        self.endloop = False
        self.window = None

    def openingView(self):

        layout = [
            [sg.Button("Create new user"), sg.Button("Login"), sg.Button("Exit")]
        ]
        self.window = sg.Window('Dont starve').Layout(layout)
        button, values = self.window.Read()
        if button is None or button == 'Exit':
            self.endloop = True
        elif (button == "Login"):
            self.clientstate = 1
        elif (button == "Create new user"):
            self.clientstate = 2

    def loginScreen(self):

        layout = [
            [sg.Text('Please enter your username')],
            [sg.Text('Name', size=(15, 1)), sg.InputText('name')],
            [sg.Button("Login"), sg.Button("Back")]
        ]
        window1 = sg.Window('Dont starve').Layout(layout)
        self.window.Close()
        self.window = window1
        button, values = self.window.Read()
        if (button == "Back"):
            self.window.Close()
            self.clientstate = 0
        elif (button == "Login"):
            try:
                users = get_users(s, body["@controls"])
                user = find_user_item(values[0], users)
                print(user)
                if (user == None or values[0] == None):
                    raise Input_error
                elif (button == None):
                    self.endloop=True
            except Input_error:
                sg.Popup('User not found')
            else:
                self.userloc = find_user_href(values[0], users)
                self.username = user["username"]
                self.clientstate = 3


    def userCreateScreen(self):

        layout = [
            [sg.Text('Please enter your username')],
            [sg.Text('Name', size=(15, 1)), sg.InputText('name')],
            [sg.Button("Create user"), sg.Button("Back")]
        ]
        window1 = sg.Window('Dont starve').Layout(layout)
        self.window.Close()
        self.window = window1
        button, values = self.window.Read()
        if (button == "Back"):
            self.window.Close()
            self.clientstate = 0
        elif (button == "Create user"):
            try:
                users = get_users(s, body["@controls"])
                user = find_user_item(values[0], users)
                if (user != None or values[0] == None):
                    raise Input_error
                elif (button == None):
                    self.endloop=True
            except Input_error:
                sg.Popup('User with that name already exists')
            else:
                userloc = create_user(s, values[0], body["@controls"])
                username = values[0]
                self.clientstate = 3

    def userScreen(self):

        resp = s.get(API_URL + self.userloc)
        userbody = resp.json()
        print(userbody)
        layout = [
            [sg.Text('Please enter your username')],
            [sg.Button("Recipes"), sg.Button("Shoppinglists"), sg.Button("Back")]
        ]
        window1 = sg.Window(self.username).Layout(layout)
        self.window.Close()
        self.window = window1
        button, values = self.window.Read()
        if (button == "Recipes"):
            self.clientstate = 4

    def recipeScreen(self):

        recipes = get_recipes(s, body["@controls"])
        recipenames = []
        k = 1
        for recipe in recipes:
            rname = (str(k) + " : " + recipe["name"])
            recipenames.append(rname)
            k += 1
        layout = [
            [sg.Listbox(values=recipenames, size=(30, 6))],
            [sg.Button("Pick recipe"), sg.Button("Create new recipe"), sg.Button("Back")]
        ]
        window1 = sg.Window(self.username).Layout(layout).Finalize()
        self.window.Close()
        window = window1
        button, values = window.Read()
        if (button == "Pick recipe"):
            name = values[0][0].split(" ")
            picked_recipe = recipes[int(name[0]) - 1]
            resp = s.get(API_URL + picked_recipe["@controls"]["self"]["href"])
            recipebody = resp.json()
            print(recipes[int(name[0]) - 1])
            print(recipebody)
            tab1_layout = [
                [sg.Text('Name' + " : " + picked_recipe["name"])],
                [sg.Text('Description' + " : " + picked_recipe["description"])],
                [sg.Text('RecipeYield' + " : " + picked_recipe["recipeYield"])],
                [sg.Text('Cooktime' + " : " + picked_recipe["cookTime"])],
                [sg.Text('Recipe category' + " : " + picked_recipe["recipeCategory"])],
                [sg.Text('Author' + " : " + picked_recipe["author"])],
                [sg.Text('Date published' + " : " + picked_recipe["datePublished"])]
            ]
            ingredients = get_ingredients(s, recipebody["@controls"])
            steps = get_steps(s, recipebody["@controls"])
            tab2_layout = [[sg.Listbox(values=ingredients, size=(30, 6))],
                           [sg.Button("Add ingredient"), sg.Button("Modify ingredient"),
                            sg.Button("Delete ingredient")]]
            tab3_layout = [[sg.Listbox(values=steps, size=(30, 6))],
                           [sg.Button("Add step"), sg.Button("Modify step"), sg.Button("Delete step")]]
            layout = [[sg.TabGroup([[sg.Tab('Recipe information', tab1_layout), sg.Tab('Ingredients', tab2_layout),
                                     sg.Tab('Steps', tab3_layout)]])],
                      [sg.Button("Back")]]
            window1 = sg.Window(self.username).Layout(layout).Finalize()
            window.Close()
            window = window1
            button, values = window.Read()
            if (button == "Add ingredient"):
                self.addingredient()

        elif (button == "Create new recipe"):
            layout = [
                [sg.Text('Please input the required fields')],
                [sg.Text('Name', size=(15, 1)), sg.InputText()],
                [sg.Text("Description", size=(15, 1)), sg.InputText()],
                [sg.Text('Recipe Yield', size=(15, 1)), sg.InputText()],
                [sg.Text('Cooktime', size=(15, 1)), sg.InputText()],
                [sg.Text('Category', size=(15, 1)), sg.InputText()],
                [sg.Button("Create user"), sg.Button("Back")]
            ]
            window1 = sg.Window(self.username).Layout(layout).Finalize()
            window.Close()
            window = window1
            button, values = window.Read()
            values[5] = self.username
            self.recipeloc = create_recipe(s, values, body["@controls"])

    def addingredient(self):

        layout = [
            [sg.Text('Required fields')],
            [sg.Text('Name', size=(15, 1)), sg.InputText()],
            [sg.Text("Description", size=(15, 1)), sg.InputText()],
            [sg.Text("Amount", size=(15, 1)), sg.InputText()],
            [sg.Text('Unit', size=(15, 1)), sg.InputText()],
            [sg.Text('Optional fields')],
            [sg.Text('Calories', size=(15, 1)), sg.InputText()],
            [sg.Text('Carbonhydrate content', size=(15, 1)), sg.InputText()],
            [sg.Text('Cholesterol content', size=(15, 1)), sg.InputText()],
            [sg.Text('Fat content', size=(15, 1)), sg.InputText()],
            [sg.Text('Fiber content', size=(15, 1)), sg.InputText()],
            [sg.Text('Protein content', size=(15, 1)), sg.InputText()],
            [sg.Text('Saturated fat content', size=(15, 1)), sg.InputText()],
            [sg.Text('Sodium content', size=(15, 1)), sg.InputText()],
            [sg.Text('Sugar content', size=(15, 1)), sg.InputText()],
            [sg.Text('Transfat content', size=(15, 1)), sg.InputText()],
            [sg.Text('Unsaturated fat content', size=(15, 1)), sg.InputText()],
            [sg.Button("Submit"), sg.Button("Back")]
        ]

        window1 = sg.Window(self.username).Layout(layout).Finalize()
        self.window.Close()
        self.window = window1
        button, values = self.window.Read()
        self.ingredientloc = create_recipe(s, values, body["@controls"])

    def run(self):

        while True:
            if(self.endloop==True):
                break
            if(self.clientstate==0):
                self.openingView()
            elif(self.clientstate==1):
                self.loginScreen()
            elif(self.clientstate==2):
                self.userCreateScreen()
            elif(self.clientstate==3):
                self.userScreen()
            elif (self.clientstate == 4):
                self.recipeScreen()

            elif (self.clientstate == 5):
                print("paska")


if __name__ == "__main__":
    API_URL = "http://localhost:5000"
    with requests.Session() as s:

        #resp = s.get(API_URL + "/api/users/")
        #body = resp.json()
        #data = {"username":"ok"}
        #submit_data(s, body["@controls"]["profile:add-user"], data)

        #resp = s.get(API_URL + "/api/recipes/")
        #body = resp.json()
        #data = {
        #      "name": "saatana",
        #      "description": "hoii",
        #      "recipeyield": "tyoo",
        #      "cooktime": "kakka",
        #      "category": "perkele",
        #      "author": "ville"
        #    }
        #submit_data(s, body["@controls"]["profile:add-recipe"], data)

        #resp = s.get(API_URL + "/api/users/")
        resp = s.get(API_URL + "/api/")
        body = resp.json()
        print(body)
        #recipeargs = ["paska", "vittu", "saatana", "asdasasd", "perkele", "ahahahahahhaha"]
        #asd = create_recipe(s, recipeargs, body["@controls"])
        """
        print(body)
        print(body["@controls"]["profile:recipes-all"])
        href2 = body["@controls"]["profile:recipes-all"]["href"]
        resp2 = s.get(API_URL + href2)
        body2 = resp2.json()
        print(body2["@controls"])
        href3 = body["@controls"]["profile:users-all"]["href"]
        resp3 = s.get(API_URL + href3)
        body3 = resp3.json()
        print(body3["users"][0]["@controls"]["self"]["href"])
        href4 = body3["users"][0]["@controls"]["self"]["href"]
        resp4 = s.get(API_URL + href4)
        body4 = resp4.json()
        print(body4["@controls"]["profile:add-shoppinglist"]["href"])
        href5 = body4["@controls"]["profile:add-shoppinglist"]["href"]
        resp5 = s.get(API_URL + href5)
        body5 = resp5.json()
        print(body5)
        print(body2["recipes"][0]["@controls"]["self"]["href"])
        href6 = body2["recipes"][0]["@controls"]["self"]["href"]
        resp6 = s.get(API_URL + href6)
        body6 = resp6.json()
        print(body6["@controls"]["profile:ingredients-all"])
        print(body6["@controls"]["profile:steps-all"])
        print(body6["@controls"]["profile:add-ingredient"])
        print(body6["@controls"]["profile:add-step"])
        users = body3["users"]
        print(users)
        print("paska")
        for user in users:
            print(user["username"])
        """
        clientstate = 0
        button = 0
        endloop = False
        client = Client()
        client.run()

            #print(user)

        """
        layout = [
            [sg.Text('Please enter your Name, Address, Phone')],
            [sg.Text('Name', size=(15, 1)), sg.InputText('name')],
            [sg.Text('Address', size=(15, 1)), sg.InputText('address')],
            [sg.Text('Phone', size=(15, 1)), sg.InputText('phone')],
            [sg.Submit(), sg.Cancel()]
        ]
users = get_users(s, body["@controls"])
        window = sg.Window('Dont starve').Layout(layout)
        button, values = window.Read()

        print(button, values[0], values[1], values[2])
        """
        #asd = create_user(s, -1, body["@controls"]["profile:add-user"])
        #print(body)
        #API_TAG_RECIPE_MAPPING["name"] = "sawatana"
        #print(API_TAG_RECIPE_MAPPING)
        #asd = create_with_mapping(s, )
        #asd = find_recipe_href("saatana", body["recipes"])
        #print(asd)

        #resp = s.get(API_URL + "/api/users/")
        #body = resp.json()
        #data = "ok"
        #asd = find_user_item(data, body["users"])
        #print(asd)