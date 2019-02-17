from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class NutritionInformation(db.Model):
    # db.Model defaults to nutrition_information
    __tablename__ = "nutrition_information"
    id = db.Column(db.Integer, primary_key=True)
    servingSize = db.Column(db.Integer, nullable=False)
    servingSizeUnit = db.Column(db.String(255), nullable=False)
    calories = db.Column(db.Integer, nullable=True)
    carbohydrateContent = db.Column(db.Integer, nullable=True)
    cholesterolContent = db.Column(db.Integer, nullable=True)
    fatContent = db.Column(db.Integer, nullable=True)
    fiberContent = db.Column(db.Integer, nullable=True)
    proteinContent = db.Column(db.Integer, nullable=True)
    saturatedFatContent = db.Column(db.Integer, nullable=True)
    sodiumContent = db.Column(db.Integer, nullable=True)
    sugarContent = db.Column(db.Integer, nullable=True)
    transFatContent = db.Column(db.Integer, nullable=True)
    unsaturatedFatContent = db.Column(db.Integer, nullable=True)


class Ingredient(db.Model):
    __tablename__ = "ingredient"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    nutrition_nformation_id = db.Column(db.Integer, db.ForeignKey("nutrition_information.id"), nullable=True)
    nutrition_information = db.relationship("NutritionInformation", uselist=False)


class Recipe(db.Model):
    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    recipeYield = db.Column(db.String(255), nullable=False)
    cookTime = db.Column(db.String(255), nullable=False)
    recipeCategory = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    datePublished = db.Column(db.DateTime, nullable=False)
    nutritionInformation_id = db.Column(db.Integer, db.ForeignKey("nutrition_information.id"), nullable=True)
    nutrition_information = db.relationship("NutritionInformation", uselist=False)


class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredient"
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), primary_key=True)
    recipe = db.relationship('Recipe')
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), primary_key=True)
    ingredient = db.relationship('Ingredient')
    amount = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(10), nullable=False)


class RecipeInstructionStep(db.Model):
    __tablename__ = "recipe_instruction_step"
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), primary_key=True)
    recipe = db.relationship('Recipe')
    step = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)


class ShoppingList(db.Model):
    __tablename__ = "shopping_list"
    id = db.Column(db.Integer, primary_key=True)
    meal_plan_id = db.Column(db.Integer, db.ForeignKey("meal_plan.plan_id"))
    meal_plan = db.relationship('MealPlan')
    notes = db.Column(db.String(255), nullable=True)


class ShoppingListIngredient(db.Model):
    __tablename__ = "shoplistingredient"
    shopping_list_id = db.Column(db.Integer, db.ForeignKey("shopping_list.id"), primary_key=True)
    shopping_list = db.relationship('ShoppingList')
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), primary_key=True)
    ingredient = db.relationship('Ingredient')
    amount = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(10), nullable=False)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)


class WeeklyPlan(db.Model):
    __tablename__ = "weekly_plan"
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship('User')


class MealPlan(db.Model):
    plan_id = db.Column(db.Integer, db.ForeignKey("weekly_plan.id"), primary_key=True)
    plan = db.relationship('WeeklyPlan')
    meal_id = db.Column(db.Integer, db.ForeignKey("meal.id"), primary_key=True)
    meal = db.relationship('Meal')
    weekday = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)


class Meal(db.Model):
    __tablename__ = "meal"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    datePublished = db.Column(db.DateTime, nullable=False)


class MealRecipe(db.Model):
    meal_id = db.Column(db.Integer, db.ForeignKey("meal.id"), primary_key=True)
    meal = db.relationship('Meal')
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), primary_key=True)
    recipe = db.relationship('Recipe')
    type = db.Column(db.String(255), nullable=False)


class Like(db.Model):
    meal_id = db.Column(db.Integer, db.ForeignKey("meal.id"), primary_key=True)
    meal = db.relationship('Meal')
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    user = db.relationship('User')
    stars = db.Column(db.Integer, nullable=False)
