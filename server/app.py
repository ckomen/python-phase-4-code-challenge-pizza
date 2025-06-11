#!/usr/bin/env python3

import os
from flask import Flask, request, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from models import db, Restaurant, RestaurantPizza, Pizza

# Setup DB path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Enable CORS
CORS(app, origins=["http://localhost:3000"])  # Allow only frontend origin

# Set up DB and migration
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = [
        restaurant.to_dict(only=('id', 'name', 'address'))
        for restaurant in Restaurant.query.all()
    ]
    return make_response(restaurants, 200)

@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()

    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)

    if request.method == 'GET':
        return make_response(restaurant.to_dict(), 200)

    elif request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()
        return make_response({}, 204)

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = [
        pizza.to_dict(only=('id', 'name', 'ingredients'))
        for pizza in Pizza.query.all()
    ]
    return make_response(pizzas, 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    try:
        data = request.get_json()

        if not data:
            raise ValueError("No JSON data provided")

        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        if price is None or pizza_id is None or restaurant_id is None:
            raise ValueError("Missing required fields")

        # Ensure price is a number and within valid range
        try:
            price = float(price)
            if price < 1 or price > 30:
                raise ValueError("Price must be between 1 and 30")
        except Exception:
            raise ValueError("Price must be between 1 and 30")

        pizza = db.session.get(Pizza, pizza_id)
        restaurant = db.session.get(Restaurant, restaurant_id)

        if not pizza or not restaurant:
            raise ValueError("Invalid pizza or restaurant ID")

        new_rp = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )

        db.session.add(new_rp)
        db.session.commit()

        return make_response(pizza.to_dict(), 201)

    except ValueError as ve:
        return make_response({"errors": ["validation errors"]}, 400)

    except Exception as e:
        # Generic error catch, useful for debugging
        return make_response({"errors": ["An unexpected error occurred"]}, 500)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
