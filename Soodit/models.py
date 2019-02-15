from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class NutritionInformation(db.Model):
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

    ingredient_r = db.relationship("Ingredient", back_populates="nutritioninformation_r", uselist=False)
    recipe_r = db.relationship("Recipe", back_populates="nutritioninformation_r", uselist=False)


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    nutritionInformation = db.Column(db.Integer, db.ForeignKey("nutritioninformation.id"), nullable=True)

    nutritionInformation_r = db.relationship("NutritionInformation", back_populates="ingredient_r")
    recipeingredient_r = db.relationship("RecipeIngredient", back_populates="ingredient_r")


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    recipeYield = db.Column(db.String(255), nullable=False)
    cookTime = db.Column(db.String(255), nullable=False)
    recipeCategory = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    datePublished = db.Column(db.DateTime, nullable=False)
    nutritionInformation = db.Column(db.Integer, db.ForeignKey("nutritioninformation.id"), nullable=True)

    instructionstep_r = db.relationship("RecipeInstructionStep", back_populates="recipe_r")
    recipeingredient_r = db.relationship("RecipeIngredient", back_populates="recipe_r")
    nutritionInformation_r = db.relationship("NutritionInformation", back_populates="recipe_r")


class RecipeIngredient(db.Model):
    recipe = db.Column(db.Integer, db.ForeignKey("recipe.id"), primary_key=True)
    ingredient = db.Column(db.Integer, db.ForeignKey("ingredient.id"), primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(255), nullable=True)

    ingredient_r = db.relationship("Ingredient", back_populates="recipeingredient_r", uselist=False)
    recipe_r = db.relationship("Recipe", back_populates="recipeingredient_r", uselist=False)


class RecipeInstructionStep(db.Model):
    id = db.Column(db.Integer, db.ForeignKey("recipe.id"), primary_key=True)
    step = db.Column(db.Integer, primary_key=True)
    text = description = db.Column(db.String(255), nullable=False)

    recipe_r = db.relationship("Recipe", back_populates="instructionstep_r")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    weeklyplan_r = db.relationship("WeeklyPlan", back_populates="user_r")


class WeeklyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(255), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey("user.id"))

    user_r = db.relationship("User", back_populates="weeklyplan_r")


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    datePublished = db.Column(db.DateTime, nullable=False)
