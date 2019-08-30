import click
from flask.cli import with_appcontext
from mealplan import db

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()

class NutritionInformation(db.Model):
    # db.Model defaults to nutrition_information
    __tablename__ = "nutrition_information"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    recipe = db.relationship('Recipe', cascade="save-update, merge")
    ingredient = db.relationship('Ingredient', cascade="save-update, merge")

    def __repr__(self):
        return "{}".format(self.id)


class Ingredient(db.Model):
    __tablename__ = "ingredient"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    nutrition_information_id = db.Column(db.Integer, db.ForeignKey("nutrition_information.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=True)
    nutrition_information = db.relationship("NutritionInformation", uselist=False, cascade="save-update, merge")
    recipe_ingredients = db.relationship('RecipeIngredient', cascade="delete")
    ingredients = db.relationship('ShoppingListIngredient', cascade="delete")


class Recipe(db.Model):
    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    recipeYield = db.Column(db.String(255), nullable=False)
    cookTime = db.Column(db.String(255), nullable=False)
    recipeCategory = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    datePublished = db.Column(db.DateTime, nullable=False)
    nutritionInformation_id = db.Column(db.Integer, db.ForeignKey("nutrition_information.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=True)
    nutrition_information = db.relationship("NutritionInformation", uselist=False, cascade="save-update, merge")
    ingredients = db.relationship('RecipeIngredient', cascade="delete")
    steps = db.relationship('RecipeInstructionStep', cascade="delete")


class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredient"
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id", onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True)
    recipe = db.relationship('Recipe', cascade="save-update, merge")
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id", onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True)
    ingredient = db.relationship('Ingredient', cascade="save-update, merge, delete")
    amount = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(10), nullable=False)


class RecipeInstructionStep(db.Model):
    __tablename__ = "recipe_instruction_step"
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id", onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True)
    recipe = db.relationship('Recipe', cascade="save-update, merge")
    step = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)


class ShoppingList(db.Model):
    __tablename__ = "shopping_list"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notes = db.Column(db.String(255), nullable=True)
    owner = db.relationship('User', cascade="save-update, merge")
    owner_name = db.Column(db.String, db.ForeignKey("user.username", onupdate="CASCADE", ondelete="RESTRICT"))
    ingredients = db.relationship('ShoppingListIngredient', cascade="delete")

class ShoppingListIngredient(db.Model):
    __tablename__ = "shoplistingredient"
    shopping_list_id = db.Column(db.Integer, db.ForeignKey("shopping_list.id", onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True)
    shopping_list = db.relationship('ShoppingList', cascade="save-update, merge")
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id", onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True)
    ingredient = db.relationship('Ingredient', cascade="save-update, merge, delete")
    amount = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(10), nullable=False)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    shoppinglists = db.relationship('ShoppingList', cascade="delete")

