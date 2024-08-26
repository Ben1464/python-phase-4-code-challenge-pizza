#!/usr/bin/env python3
from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)

# Helper function to return JSON responses
def json_response(data, status_code=200):
    return make_response(jsonify(data), status_code)

class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return json_response([restaurant.to_dict() for restaurant in restaurants])

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant is None:
            return json_response({"error": "Restaurant not found"}, 404)
        return json_response(restaurant.to_dict())

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant is None:
            return json_response({"error": "Restaurant not found"}, 404)
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return json_response([pizza.to_dict() for pizza in pizzas])

class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.json
        try:
            price = data['price']
            restaurant_id = data['restaurant_id']
            pizza_id = data['pizza_id']
            
            if not (1 <= price <= 30):
                return json_response({"error": "Price must be between 1 and 30"}, 400)

            restaurant = Restaurant.query.get(restaurant_id)
            pizza = Pizza.query.get(pizza_id)
            if restaurant is None or pizza is None:
                return json_response({"error": "Restaurant or Pizza not found"}, 404)

            restaurant_pizza = RestaurantPizza(price=price, restaurant_id=restaurant_id, pizza_id=pizza_id)
            db.session.add(restaurant_pizza)
            db.session.commit()
            return json_response(restaurant_pizza.to_dict(), 201)
        except KeyError as e:
            return json_response({"error": f"Missing key: {str(e)}"}, 400)

# Add resource routes
api.add_resource(RestaurantListResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzaListResource, '/pizzas')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
