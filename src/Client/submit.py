import json
import requests
import PySimpleGUI as sg


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



# valitaan haluttu resepti jos löytyy samalla nimellä useita

def prompt_recipe_choice(name, hits):

    print("The following recipes were found with '{}'".format(name))
    items = []
    for i, recipe in enumerate(hits, 1):
        print("{i}: {name} ({description},{recipeyield},{cookTime},{recipeCategory},{author},{datePublished}}".format(i=i, **recipe))
    choice = int(input("Choose artist by typing a number: "))
    return items[choice - 1]

# Find functions to search the database for specific items and locations

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


# Functions to send different requests to server.


def submit_data(s, ctrl, data): # POST/PUT

    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers = {"Content-type": "application/json"}
    )
    return resp

def delete(s, ctrl): # DEL

    delctrl = ctrl["profile:delete"]
    resp = s.request(
        delctrl["method"],
        API_URL + delctrl["href"],
        headers={"Content-type": "application/json"}
    )
    return resp

# Functions to use the submit_data and delete functions correctly
# Every resource has create function for post and modify for put

def create_user(s, username, ctrl):

    body = {}
    ctrl = ctrl["profile:add-user"]
    schema = ctrl["schema"]
    for field in schema["required"]:
        if field == "username":
            body[field] = username
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)

def change_user(s, username, ctrl):

    body = {}
    ctrl = ctrl["profile:edit-user"]
    schema = ctrl["schema"]
    for field in schema["required"]:
        if field == "username":
            body[field] = username
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

    optional = ["calories", "carbohydratecontent", "cholesterolcontent", "fatcontent", "fibercontent",
                "proteincontent", "saturatedfatcontent", "sodiumcontent", "sugarcontent", "transfatcontent",
                "unsaturatedfatcontent"]
    i = 4
    for field in optional:
        if(ingrargs[i]!=""):
            body[field] = ingrargs[i]
        i += 1
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)

def modify_ingredient(s, ingrargs, ctrl):
    body = {}
    ctrl = ctrl["profile:edit-ingredient"]
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

    optional = ["calories", "carbohydratecontent", "cholesterolcontent", "fatcontent", "fibercontent",
                "proteincontent", "saturatedfatcontent", "sodiumcontent", "sugarcontent", "transfatcontent",
                "unsaturatedfatcontent"]
    i = 4
    for field in optional:
        if(ingrargs[i]!=""):
            body[field] = ingrargs[i]
        i += 1
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)

def create_step(s, stepargs, ctrl):

    body = {}
    ctrl = ctrl["profile:add-step"]
    schema = ctrl["schema"]
    for field in schema["required"]:
        if field == "step":
            body[field] = stepargs[0]
        elif field == "text":
            body[field] = stepargs[1]
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)

def modify_step(s, stepargs, ctrl):

    body = {}
    ctrl = ctrl["profile:edit-step"]
    schema = ctrl["schema"]
    for field in schema["required"]:
        if field == "step":
            body[field] = int(stepargs[0])
        elif field == "text":
            body[field] = stepargs[1]
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)


def create_shoppinglist(s, ingrargs, ctrl):
    body = {}
    ctrl = ctrl["profile:add-shoppinglist"]
    schema = ctrl["schema"]
    optional = ["notes"]
    for field in optional:
        if field == "notes":
            body[field] = ingrargs[0]
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)


def modify_shoppinglist(s, ingrargs, ctrl):
    body = {}
    ctrl = ctrl["profile:edit-shoppinglist"]
    schema = ctrl["schema"]
    optional = ["notes"]
    for field in optional:
        if field == "notes":
            body[field] = ingrargs[0]
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)

# Get functions for every resource
# Sends get request to server and parses results

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


# Client is a simple state machine where every state is a new screen

class Client():

    def __init__(self):
        self.button = 0
        self.endloop = False
        self.window = None

    def openingView(self):

        layout = [
            [sg.Button("Create new user"), sg.Button("Login"), sg.Button("Exit")],
        ]
        window1 = sg.Window('Dont starve').Layout(layout)
        if(self.window is not None):
            self.window.Close()
        self.window = window1
        button, values = self.window.Read()
        if button is None or button == 'Exit':
            self.endloop = True
        elif (button == "Login"):
            self.loginScreen()
        elif (button == "Create new user"):
            self.userCreateScreen()

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
            self.openingView()
        elif (button == "Login"):
            try:
                users = get_users(s, body["@controls"])
                user = find_user_item(values[0], users)
                if (user == None or values[0] == None):
                    raise Input_error
                elif (button == None):
                    self.endloop=True
            except Input_error:
                sg.Popup('User not found')
            else:
                self.userloc = API_URL + find_user_href(values[0], users)
                self.username = user["username"]
                self.userScreen()


    def userCreateScreen(self):

        layout = [
            [sg.Text('Please enter your username')],
            [sg.Text('Name', size=(15, 1)), sg.InputText('name')],
            [sg.Button("Create user"), sg.Button("Back")]
        ]
        window1 = sg.Window('Dont starve').Layout(layout)
        self.window.Close()
        self.window = window1


        while True:
            try:
                button, values = self.window.Read()
                if (button == "Back"):
                    self.window.Close()
                    self.openingView()
                elif (button == "Create user"):
                    self.userloc = create_user(s, values[0], body["@controls"])

                elif (button == None):
                        self.endloop=True
            except APIError as ae:
                sg.Popup(str(ae.error["@error"]["@messages"]))
            else:
                self.username = values[0]
                self.userScreen()
                break

    def userScreen(self):

        resp = s.get(self.userloc)
        userbody = resp.json()
        layout = [
            [sg.Text('Please enter your username')],
            [sg.Button("Recipes"), sg.Button("Shoppinglists"), sg.Button("Back")],
            [sg.Button("Delete your user"), sg.Button("Change username")]
        ]
        window1 = sg.Window(self.username).Layout(layout)
        self.window.Close()
        self.window = window1
        button, values = self.window.Read()
        if (button == "Recipes"):
            self.recipeScreen()
        elif(button == "Shoppinglists"):
            self.shoppingListScreen(userbody)
        elif(button == "Delete your user"):
            delete(s, userbody["@controls"])
            self.openingView()
        elif(button == "Change username"):
            layout = [
                [sg.Text('Please enter your new')],
                [sg.Text('Name', size=(15, 1)), sg.InputText(self.username)],
                [sg.Button("Change username"), sg.Button("Back")]
            ]
            window1 = sg.Window('Dont starve').Layout(layout)
            self.window.Close()
            self.window = window1

            while True:
                try:
                    button, values = self.window.Read()
                    if (button == "Back"):
                        self.window.Close()
                        self.openingView()
                    elif (button == "Change username"):
                        self.userloc = change_user(s, values[0], userbody["@controls"])
                    elif (button == None):
                        self.endloop = True
                        break
                except APIError as ae:
                    sg.Popup(str(ae.error["@error"]["@messages"]))
                else:
                    self.username = values[0]
                    self.userScreen()
                    break

    def shoppingListScreen(self, userbody):
        lists = get_shoppinglists(s, userbody["@controls"])
        listlist = []
        k = 1
        for shoppinglist in lists:
            lnotes = (str(k) + " :  " + shoppinglist["notes"])
            listlist.append(lnotes)
        layout = [
            [sg.Listbox(values=listlist, size=(30,6))],
            [sg.Button("Pick a list"), sg.Button("Create new list"), sg.Button("Back")]
        ]
        window1 = sg.Window(self.username).Layout(layout).Finalize()
        self.window.Close()
        window = window1
        while True:
            button, values = window.Read()
            print(button)
            if(button == "Pick a list"):
                if(values[0]!= []):
                    notes = values[0][0].split(" ")
                    picked_list = lists[int(notes[0]) - 1]
                    resp = s.get(API_URL + picked_list["@controls"]["self"]["href"])
                    listbody = resp.json()
                    self.singleList(listbody, userbody)

            elif (button == "Create new list"):
                layout = [
                    [sg.Text('Please input the fields')],
                    [sg.Text('New List', size=(15, 1)), sg.InputText()],
                    [sg.Button("Create list"), sg.Button("Back")]
                ]
                window1 = sg.Window(self.username).Layout(layout).Finalize()
                window.Close()
                window = window1
                while True:
                    try:
                        button, values = window.Read()
                        values[5] = self.username
                        self.listloc = create_shoppinglist(s, values, userbody["@controls"])
                    except APIError as ae:
                        sg.Popup(str(ae.error["@error"]["@messages"]))
                    else:
                        break
            elif (button == "Back"):
                self.userScreen()

    def singleList(self, listbody, userbody):
        window1 = None
        while True:
            tab1_layout = [
                [sg.Text('Notes' + " : " + listbody["notes"])]
            ]
            ingredients = get_ingredients(s, listbody["@controls"])
            tab2_layout = [[sg.Listbox(values=ingredients, size=(50, 6))]]

            tab3_layout = [[sg.Listbox(values=ingredients, size=(50, 6))],
                           [sg.Button("Add ingredient"), sg.Button("Modify ingredient"),
                            sg.Button("Delete ingredient")]]
            layout = [[sg.TabGroup([[sg.Tab('List information', tab1_layout), sg.Tab('Ingredients', tab3_layout)]])],
                      [sg.Button("Back")]]
            if (window1 is not None):
                window1.Close()
            window1 = sg.Window(self.username).Layout(layout).Finalize()

            button, values = window1.Read()
            if (button == "Add ingredient"):
                self.addListIngredient(listbody)
            elif (button == "Modify ingredient"):
                if(values[0]!=[]):
                    resp = s.get(API_URL + values[0][0]["@controls"]["self"]["href"])
                    ingredientbody = resp.json()
                    self.editIngredient(ingredientbody)
            elif(button == "Delete ingredient"):
                if(values[0]!=[]):
                    resp = s.get(API_URL + values[0][0]["@controls"]["self"]["href"])
                    ingredientbody = resp.json()
                    delete(s, ingredientbody["@controls"])
            elif(button == "Back"):
                window1.Close()
                self.shoppingListScreen(userbody)

    def addListIngredient(self, listbody):

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
            popwindow = sg.Window(self.username).Layout(layout).Finalize()
            while True:
                try:
                    button, values = popwindow.Read()
                    if(button=="Back"):
                        break
                    elif(button=="Submit"):
                        self.ingredientloc = create_ingredient(s, values, listbody["@controls"])
                    else:
                        break
                except APIError as ae:
                    sg.Popup(str(ae.error["@error"]["@messages"]))
                else:
                    popwindow.Close()
                    break



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
        while True:
            button, values = window.Read()
            if (button == "Pick recipe"):
                if(values[0]!=[]):
                    name = values[0][0].split(" ")
                    picked_recipe = recipes[int(name[0]) - 1]
                    resp = s.get(API_URL + picked_recipe["@controls"]["self"]["href"])
                    recipebody = resp.json()
                    self.singleRecipe(recipebody)

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
                while True:
                    try:
                        button, values = window.Read()
                        values[5] = self.username
                        self.recipeloc = create_recipe(s, values, body["@controls"])
                    except APIError as ae:
                        sg.Popup(str(ae.error["@error"]["@messages"]))
                    else:
                        break
            elif (button == "Back"):
                self.userScreen()

    def singleRecipe(self, recipebody):

        #window.Close()
        #window = window1
        window1=None
        while True:
            tab1_layout = [
                [sg.Text('Name' + " : " + recipebody["name"])],
                [sg.Text('Description' + " : " + recipebody["description"])],
                [sg.Text('RecipeYield' + " : " + recipebody["recipeYield"])],
                [sg.Text('Cooktime' + " : " + recipebody["cookTime"])],
                [sg.Text('Recipe category' + " : " + recipebody["recipeCategory"])],
                [sg.Text('Author' + " : " + recipebody["author"])],
                [sg.Text('Date published' + " : " + recipebody["datePublished"])]
            ]
            ingredients = get_ingredients(s, recipebody["@controls"])
            steps = get_steps(s, recipebody["@controls"])
            tab2_layout = [
                [sg.Text('Calories' + " : " + str(recipebody["calories"]))],
                [sg.Text('Carbonhydrate content' + " : " + str(recipebody["carbohydrateContent"]))],
                [sg.Text('Cholesterol content' + " : " + str(recipebody["cholesterolContent"]))],
                [sg.Text('Fat content' + " : " + str(recipebody["fatContent"]))],
                [sg.Text('Fiber content' + " : " + str(recipebody["fiberContent"]))],
                [sg.Text('Protein content' + " : " + str(recipebody["proteinContent"]))],
                [sg.Text('Saturated fat content' + " : " + str(recipebody["saturatedFatContent"]))],
                [sg.Text('Sodium content' + " : " + str(recipebody["sodiumContent"]))],
                [sg.Text('Sugar content' + " : " + str(recipebody["sugarContent"]))],
                [sg.Text('Trans fat content' + " : " + str(recipebody["transFatContent"]))],
                [sg.Text('Unsaturated fat content' + " : " + str(recipebody["unsaturatedFatContent"]))]

            ]
            tab3_layout = [[sg.Listbox(values=ingredients, size=(50, 6))],
                           [sg.Button("Add ingredient"), sg.Button("Modify ingredient"),
                            sg.Button("Delete ingredient")]]
            tab4_layout = [[sg.Listbox(values=steps, size=(30, 6))],
                           [sg.Button("Add step"), sg.Button("Modify step"), sg.Button("Delete step")]]
            layout = [[sg.TabGroup([[sg.Tab('Recipe information', tab1_layout), sg.Tab('Nutrition information', tab2_layout), sg.Tab('Ingredients', tab3_layout),
                                     sg.Tab('Steps', tab4_layout)]])],
                      [sg.Button("Back")]]
            if(window1 is not None):
                window1.Close()

            window1 = sg.Window(self.username).Layout(layout).Finalize()

            button, values = window1.Read()
            if (button == "Add ingredient"):
                self.addIngredient(recipebody)
            elif (button == "Modify ingredient"):
                if(values[0]!=[]):
                    resp = s.get(API_URL + values[0][0]["@controls"]["self"]["href"])
                    ingredientbody = resp.json()
                    self.editIngredient(ingredientbody)
            elif(button == "Delete ingredient"):
                if(values[0]!=[]):
                    resp = s.get(API_URL + values[0][0]["@controls"]["self"]["href"])
                    ingredientbody = resp.json()
                    delete(s, ingredientbody["@controls"])
            elif (button == "Add step"):
                self.addStep(recipebody)
            elif (button == "Modify step"):
                if(values[1]!=[]):
                    resp = s.get(API_URL + values[1][0]["@controls"]["self"]["href"])
                    stepbody = resp.json()
                    self.editStep(stepbody)
            elif(button == "Delete step"):
                if(values[1]!=[]):
                    resp = s.get(API_URL + values[1][0]["@controls"]["self"]["href"])
                    stepbody = resp.json()
                    delete(s, stepbody["@controls"])
            elif(button == "Back"):
                window1.Close()
                self.recipeScreen()

    def addIngredient(self, recipebody):

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
            popwindow = sg.Window(self.username).Layout(layout).Finalize()
            while True:
                try:
                    button, values = popwindow.Read()
                    if(button=="Back"):
                        break
                    elif(button=="Submit"):
                        self.ingredientloc = create_ingredient(s, values, recipebody["@controls"])
                    else:
                        break
                except APIError as ae:
                    sg.Popup(str(ae.error["@error"]["@messages"]))
                else:
                    popwindow.Close()
                    break

    def editIngredient(self, ingredientbody):

            layout = [
                [sg.Text('Required fields')],
                [sg.Text('Name', size=(15, 1)), sg.InputText(ingredientbody["name"])],
                [sg.Text("Description", size=(15, 1)), sg.InputText(ingredientbody["description"])],
                [sg.Text("Amount", size=(15, 1)), sg.InputText(ingredientbody["amount"])],
                [sg.Text('Unit', size=(15, 1)), sg.InputText(ingredientbody["unit"])],
                [sg.Text('Optional fields')],
                [sg.Text('Calories', size=(15, 1)), sg.InputText(ingredientbody["calories"])],
                [sg.Text('Carbonhydrate content', size=(15, 1)), sg.InputText(ingredientbody["carbohydrateContent"])],
                [sg.Text('Cholesterol content', size=(15, 1)), sg.InputText(ingredientbody["cholesterolContent"])],
                [sg.Text('Fat content', size=(15, 1)), sg.InputText(ingredientbody["fatContent"])],
                [sg.Text('Fiber content', size=(15, 1)), sg.InputText(ingredientbody["fiberContent"])],
                [sg.Text('Protein content', size=(15, 1)), sg.InputText(ingredientbody["proteinContent"])],
                [sg.Text('Saturated fat content', size=(15, 1)), sg.InputText(ingredientbody["saturatedFatContent"])],
                [sg.Text('Sodium content', size=(15, 1)), sg.InputText(ingredientbody["sodiumContent"])],
                [sg.Text('Sugar content', size=(15, 1)), sg.InputText(ingredientbody["sugarContent"])],
                [sg.Text('Transfat content', size=(15, 1)), sg.InputText(ingredientbody["transFatContent"])],
                [sg.Text('Unsaturated fat content', size=(15, 1)), sg.InputText(ingredientbody["unsaturatedFatContent"])],
                [sg.Button("Submit"), sg.Button("Back")]
            ]
            popwindow = sg.Window(self.username).Layout(layout).Finalize()
            while True:
                try:
                    button, values = popwindow.Read()
                    if(button=="Back"):
                        break
                    elif(button=="Submit"):
                        self.ingredientloc = modify_ingredient(s, values, ingredientbody["@controls"])
                    else:
                        break
                except APIError as ae:
                    sg.Popup(str(ae.error["@error"]["@messages"]))
                else:
                    popwindow.Close()
                    break

    def addStep(self, recipebody):

            layout = [
                [sg.Text('Required fields')],
                [sg.Text('Step', size=(15, 1)), sg.InputText()],
                [sg.Text("Text", size=(15, 1)), sg.InputText()]
            ]
            popwindow = sg.Window(self.username).Layout(layout).Finalize()
            while True:
                try:
                    button, values = popwindow.Read()
                    if(button=="Back"):
                        break
                    elif(button=="Submit"):
                        self.ingredientloc = create_step(s, values, recipebody["@controls"])
                    else:
                        break
                except APIError as ae:
                    sg.Popup(str(ae.error["@error"]["@messages"]))
                else:
                    popwindow.Close()
                    break

    def editStep(self, stepbody):

            layout = [
                [sg.Text('Required fields')],
                [sg.Text('Step', size=(15, 1)), sg.InputText(stepbody["step"])],
                [sg.Text("Text", size=(15, 1)), sg.InputText(stepbody["text"])],
                [sg.Button("Submit"), sg.Button("Back")]
            ]
            popwindow = sg.Window(self.username).Layout(layout).Finalize()
            while True:
                try:
                    button, values = popwindow.Read()
                    if(button=="Back"):
                        break
                    elif(button=="Submit"):
                        self.ingredientloc = modify_step(s, values, stepbody["@controls"])
                    else:
                        break
                except APIError as ae:
                    sg.Popup(str(ae.error["@error"]["@messages"]))
                else:
                    popwindow.Close()
                    break

if __name__ == "__main__":
    API_URL = "http://localhost:5000"
    with requests.Session() as s:
        resp = s.get(API_URL + "/api/") # Send get request to entrypoint
        body = resp.json()
        client = Client()
        client.openingView()    # Client starts at the openingview
