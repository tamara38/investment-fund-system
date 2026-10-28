import json
import uuid

from bson import ObjectId
from flask import Flask, jsonify, request, Response;
from flask_jwt_extended import jwt_required, JWTManager
from pymongo import MongoClient;
from redis import Redis;
from datetime import datetime, timezone;

from configuration import Configuration
from decorators import role_check

application = Flask ( __name__ )
application.config.from_object(Configuration);

jwt = JWTManager(application);

client = MongoClient (
    host       = Configuration.MONGO_HOST,
    port       = Configuration.MONGO_PORT,
    username   = Configuration.MONGO_USERNAME,
    password   = Configuration.MONGO_PASSWORD,
    authSource = "admin"
)

database = client["investment_fond"];
collection = database["assets"];


@application.route("/search", methods=["POST"])
@role_check("employee")
def search( ):

    data = request.get_json();

    name = data.get("name");
    category = data.get("category");
    buying_date = data.get("buying_date");
    selling_date = data.get("selling_date");
    info_filters = data.get("info_filters", []);

    query = {};

    if name:
        query["name"] = {
            "$regex": name,
            "$options": "i"
        };

    if category:
        query["categories"] = category;

    if buying_date:
        query["buying_date"] = {
            "$gt": datetime.fromisoformat(
                buying_date.replace("Z", "+00:00")
            )
        };

    if selling_date:
        query["selling_date"] = {
            "$lt": datetime.fromisoformat(
                selling_date.replace("Z", "+00:00")
            )
        };

    for f in info_filters:
        field = "info." + f["field"];

        operator = f["operator"];

        value = f["value"];

        query[field] = {
            "$" + operator : value
        };

    assets = list(collection.find(query));

    result = []

    for asset in assets:
        obj = {
            "id": str(asset["_id"]),
            "name": asset["name"],
            "categories": asset["categories"],
            "buying_date": asset["buying_date"].strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "buying_price": asset["buying_price"],
            "info": asset["info"]
        }

        if "selling_date" in asset:
            obj["selling_date"] = asset["selling_date"].strftime("%Y-%m-%dT%H:%M:%S.000Z")

        if "selling_price" in asset:
            obj["selling_price"] = asset["selling_price"]

        result.append(obj);

    return jsonify({"assets": result}), 200;

@application.route("/create_buy_order", methods=["POST"])
@role_check("employee")
def create_buy_order( ):
    data = request.get_json();

    name = data.get("name");
    categories = data.get("categories");
    buying_price = data.get("buying_price");
    info = data.get("info");

    if (not name):
        return jsonify(message = "Field name is missing."), 400;

    if categories is None:
        return jsonify(message="Field categories is missing."), 400;

    if (len(categories) == 0):
        return jsonify(message = "Categories list is empty."), 400;

    if buying_price is None:
        return jsonify(message = "Field buying_price is missing."), 400;

    if not isinstance(buying_price, (int, float)) or (buying_price <= 0):
        return jsonify(message = "Invalid buying price."), 400;

    if (not info):
        return jsonify(message = "Field info is missing."), 400;



    order = {
        "uuid": str(uuid.uuid4()),
        "order_type": "BUY",
        "name": name,
        "categories": categories,
        "info": info,
        "buying_price": buying_price
    };

    with Redis(host = Configuration.REDIS_HOST, port=Configuration.REDIS_PORT) as redis:
        redis.rpush(Configuration.REDIS_ORDER_LIST, json.dumps(order));

    return Response(status = 200);

@application.route("/create_sell_order", methods=["POST"])
@role_check("employee")
def create_sell_order( ):
    data = request.get_json();

    id = data.get("id");
    selling_price = data.get("selling_price");

    if (not id):
        return jsonify(message = "Field id is missing."), 400;

    if selling_price is None:
        return jsonify(message = "Field selling_price is missing."), 400;

    if not ObjectId.is_valid(id):
        return jsonify(message = "Invalid id."), 400;

    asset = collection.find_one({"_id": ObjectId(id)});

    if asset is None:
        return jsonify(message = "Invalid id."), 400;

    if not isinstance(selling_price, (int, float)) or (selling_price <= 0):
        return jsonify(message = "Invalid selling price."), 400;

    order = {
        "uuid": str(uuid.uuid4()),
        "order_type": "SELL",
        "id": id,
        "selling_price": selling_price
    };

    with Redis(host = Configuration.REDIS_HOST, port=Configuration.REDIS_PORT) as redis:
        redis.rpush(Configuration.REDIS_ORDER_LIST, json.dumps(order));

    return Response(status = 200);


if __name__ == "__main__":
    application.run ( debug = True, host="0.0.0.0", port=5001 )