#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants')
def restaurants():
    restaurants=[restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in Restaurant.query.all()]

    response = make_response(
        restaurants,
        200
    )
    return response

@app.route('/restaurants/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def restaurant_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id==id).first()
    
    if restaurant is None:
        return make_response({"error": "Restaurant not found"}, 404)
    
    else:
        if request.method=='GET':
            restaurant_dict=restaurant.to_dict()

            response = make_response(
                restaurant_dict,
                200
                )

            return response
    
        elif request.method=='DELETE':
            db.session.delete(restaurant)
            db.session.commit()

            response_body={
                "delete_successful": True,
                "messge": "Review deleted."
            }

            response= make_response(
                response_body,
                204
            )
            return response

@app.route('/pizzas')
def get_pizzas():
    pizzas=[pizza.to_dict(only=('id','name', 'ingredients')) for pizza in Pizza.query.all()]
    response=make_response(
        pizzas,
        200
    )
    return response

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data=request.get_json()

    price=data.get("price")
    pizza_id=data.get("pizza_id")
    restaurant_id=data.get("restaurant_id")

    if not all([price, pizza_id, restaurant_id]) or not (1 <= int(price) <= 30):
        return make_response(
            {"errors": ["validation errors"]},
            400
        )
    pizza=Pizza.query.get(pizza_id)
    restaurant=Restaurant.query.get(restaurant_id)

    if not pizza or not restaurant:
        return make_response({
            "errors" :["validation errors"]},
            400)
    new_restaurant_pizza=RestaurantPizza(
        price=price,
        pizza_id=pizza_id,
        restaurant_id=restaurant_id
    )
    db.session.add(new_restaurant_pizza)
    db.session.commit()

    response_data = {
        "id": new_restaurant_pizza.id,
        "pizza": pizza.to_dict(),
        "pizza_id": pizza_id,
        "price": price,
        "restaurant": restaurant.to_dict(),
        "restaurant_id": restaurant_id
    }

    response = make_response(
        response_data,
        201
        )

    return response
   
    



if __name__ == "__main__":
    app.run(port=5555, debug=True)