# PWP SPRING 2019
# Don't Starve - Meal planner API
# Group information
* Student 1. Eetu Haapamäki <eetu.haapamaki@gmail.com>
* Student 2. Samuli Helttunen <samuli.helttunen@gmail.com>

Following commands will create the database and fill it with example data. All the necessary files are found on the requirements.txt file.
```python
from app import db

from app import NutritionInformation, Ingredient, Recipe, RecipeIngredient, RecipeInstructionStep, ShoppingList, ShoppingListIngredient, User, WeeklyPlan, Meal, MealRecipe, Like, MealPlan
from datetime import datetime
db.create_all()

#create example models

nutri = NutritionInformation(
servingSize = 9,
servingSizeUnit = "g",
calories = 299,
carbohydrateContent = 7,
cholesterolContent = 8,
fatContent = 32,
fiberContent = 92,
proteinContent = 58,
saturatedFatContent = 84,
sodiumContent = 70,
sugarContent = 88,
transFatContent = 14,
unsaturatedFatContent = 87
)

ingredient = Ingredient(
name="potato",
description = "potato is a potato"
)

recipe = Recipe(
name = "chickensoup",
description = "nice soup",
recipeYield = "9 servings",
cookTime = "5 hours",
recipeCategory = "soup",
author = "Ville",
datePublished = datetime(2019, 1, 1, 0, 0, 1)
)

recipei = RecipeIngredient(
amount = 5,
unit = "kg")

recipestep = RecipeInstructionStep(
step = 5,
text = "boil the potatoes")

shoplist = ShoppingList(
notes = "buy some cheese"
)
shoplisti = ShoppingListIngredient(
amount = 5,
unit = "dl"
)
user = User(
username = "rille"
)
weekplan = WeeklyPlan(
week= 8,
notes = "tjasj"
)

mealplan = MealPlan(
weekday = "friday",
type = "emt"
)

meal = Meal(
name = "meatballs and mashed potatoes",
description = "jeejee",
author = "masa",
type = "maindish",
datePublished = datetime(2020, 1, 1, 0, 0, 0)
)

mealrecipe = MealRecipe(
type = "kja"
)

like = Like(
stars ="3"
)


#create relationships between models

ingredient.nutrition_information = nutri
recipe.nutrition_information = nutri
recipei.recipe = recipe
recipei.ingredient = ingredient
recipestep.recipe = recipe
shoplist.meal_plan = mealplan
shoplisti.shopping_list = shoplist
shoplisti.ingredient = ingredient
weekplan.user = user
mealplan.plan = weekplan
mealplan.meal = meal
mealrecipe.meal = meal
mealrecipe.recipe = recipe
like.meal = meal
like.user = user

#create database 

db.session.add(nutri)
db.session.add(ingredient)
db.session.add(recipe)
db.session.add(recipei)
db.session.add(recipestep)
db.session.add(shoplist)
db.session.add(shoplisti)
db.session.add(user)
db.session.add(weekplan)
db.session.add(meal)
db.session.add(mealrecipe)
db.session.add(like)

db.session.commit()
```
The testing is done with pytest. db_test.py file is put into the same folder as the database app and ran by typing pytest into the terminal. The test will create the database and check that the relationships work properly. Then it will test that editing models will work properly with foreign keys. Then it will test the same but with removing the models.
