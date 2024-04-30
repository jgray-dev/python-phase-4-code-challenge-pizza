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


# Get list of all restaurants, excluding individual pizzas
@app.route('/restaurants', methods=['GET'])
def restaurants():
    if request.method == 'GET':
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in restaurants]


# Get singular restaurant, including individual pizzas
# Delete singular restaurant
@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurant(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    if restaurant:
        if request.method == 'GET':
            return restaurant.to_dict()
        if request.method == 'DELETE':
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204
    else:
        return {"error": "Restaurant not found"}, 404


# Get list of all pizzas, excluding restaurants serving that pizzas
@app.route('/pizzas', methods=['GET'])
def pizzas():
    pizzas = Pizza.query.all()
    return [pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in pizzas]


# Add new link between a restaurant and a pizza by including a price
@app.route('/restaurant_pizzas', methods=['POST'])
def restaurant_pizzas():
    try:
        newrp = RestaurantPizza(price=request.json['price'], pizza_id=request.json['pizza_id'],
                                restaurant_id=request.json['restaurant_id'])
        db.session.add(newrp)
        db.session.commit()
        return newrp.to_dict(), 201
    except Exception as e:
        print(e)
        return {"errors": ["validation errors"]}, 400


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
