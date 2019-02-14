import json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    desciption = db.Column(db.String(255), db.ForeignKey("product.id"))
    image_url = db.Column(db.String(255), nullable=False)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    servings = db.Column(db.Float, nullable=False)
    cooking_time = db.relationship("StorageItem", back_populates="product")

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)

class Meal_Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Integer, nullable=False)
    end = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(255), nullable=False)

@app.route('/products/add/', methods=["POST"])
def add_product():
    if request.method != "POST":
        return "POST method required", 405
    try:
        handle = str(request.json["handle"])
        weight = float(request.json["weight"])
        price = float(request.json["price"])
    except KeyError:
        return "Incomplete request - missing fields", 400
    except ValueError:
        return "Weight and price must be numbers", 400
    except TypeError:
        return "request content type must be JSON", 415

    # Database stuff
    product = Product.query.filter_by(handle=handle).first()
    if product is not None:
        return "Handle already exists", 409
    product = Product(
        handle=handle,
        weight=weight,
        price=price
    )
    db.session.add(product)
    db.session.commit()
    return "", 201

@app.route('/storage/<product>/add/', methods=["POST"])
def add_to_storage(product):
    if request.method != "POST":
        return "POST method required", 405
    # Check json data format
    if not request.is_json:
        return "request content type must be JSON", 415
    try:
        location = request.json["location"]
        qty = int(request.json["qty"])
    except KeyError:
        return "Incomplete request - missing fields", 400
    except ValueError:
        return "Qty must be an integer", 400

    # Database stuff
    product = Product.query.filter_by(handle=product).first()
    if product is None:
        return "Product not found", 404
    storage = StorageItem(
        qty=qty,
        location=location,
        product=product
    )
    db.session.add(storage)
    db.session.commit()
    return "", 201


@app.route('/storage/')
def get_inventory():
    if request.method != "GET":
        return "GET method required", 405
    products = db.session.query(Product).all()
    result = []
    for product in products:
        result.append({
            "handle":product.handle,
            "weight":product.weight,
            "price":product.price,
            "inventory":[]
        })
        storages = StorageItem.query.filter_by(product=product).all()
        for storage in storages:
            result[-1]["inventory"].append([storage.location, storage.qty])

    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )
    return response