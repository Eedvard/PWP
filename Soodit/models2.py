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


class Ingredient(db.Model):
    __tablename__ = "ingredient"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    nutrition_nformation_id = db.Column(db.Integer, db.ForeignKey("nutrition_information.id"), nullable=True)
    nutrition_information = db.relationship("NutritionInformation", uselist=False)


class Recipe(db.Model):
    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
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
