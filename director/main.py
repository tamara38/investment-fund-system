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

def find_order(uuid):
    orders = None
    with Redis(host = Configuration.REDIS_HOST) as redis:
        orders = redis.lrange(Configuration.REDIS_ORDER_LIST, 0, -1);

    for order in orders:
        curr = json.loads(order)

        if curr["uuid"] == uuid:
            return curr

    return None


@application.route("/pending_orders", methods=["GET"])
@role_check("director")
def get_pending_orders( ):

    with Redis(host = Configuration.REDIS_HOST) as redis:
        orders = redis.lrange(Configuration.REDIS_ORDER_LIST, 0, -1);

        orders = [json.loads(order) for order in orders];

        return jsonify({"orders" : orders}), 200;

@application.route("/decision", methods=["POST"])
@role_check("director")
def decision( ):
    data = request.get_json();

    uuid_request = data.get("uuid");
    approved = data.get("approved");

    if uuid_request is None:
        return jsonify(message = "Field uuid is missing."), 400;

    if isinstance(uuid_request, str) and len(uuid_request) == 0:
        return jsonify(message = "Field uuid is missing."), 400;

    if not isinstance(uuid_request, str):
        return jsonify(message="Invalid uuid."), 400;


    try:
        uuid.UUID(uuid_request)
    except ValueError:
        return jsonify(message = "Invalid uuid."), 400

    order = find_order(uuid_request);

    if order is None:
        return jsonify(message="Invalid uuid."), 400;

    if approved is None:
        return jsonify(message = "Field approved is missing."), 400;


    if not isinstance(approved, bool):
        return jsonify({"message": "Invalid decision."}), 400;

    if approved:
        now = datetime.now(timezone.utc);
        if (order["order_type"] == "BUY"):
            asset = {
                "name": order["name"],
                "categories": order["categories"],
                "buying_price": order["buying_price"],
                "buying_date": now,
                "info": order["info"]
            };

            collection.insert_one(asset);

        if (order["order_type"] == "SELL"):
            query = { "_id" : ObjectId(order["id"]) };
            operation = {"$set": {
                "selling_price": order["selling_price"], "selling_date": now
                }
            };
            collection.update_one(query, operation);

    with Redis(host = Configuration.REDIS_HOST) as redis:
        redis.lrem(Configuration.REDIS_ORDER_LIST, 1, json.dumps(order));

    return Response(status = 200);

@application.route("/report", methods=["GET"])
@role_check("director")
def report( ):

    pipeline = [
        {
            "$unwind": "$categories",
        },

        {
            "$group": {
                "_id": "$categories",
                "spent": {"$sum": "$buying_price"},
                "earned": {
                    "$sum": {
                        "$ifNull": [
                            "$selling_price",
                            0
                        ]
                    }
                }
            }
        },

        {
            "$sort": {
                "earned": -1,
                "spent": 1,
                "_id" : 1
            }
        },

        {
            "$project": {
                "_id" : 0,
                "category" : "$_id",
                "spent" : "$spent",
                "earned" : "$earned"
            }
        }

    ];

    statistics = list(collection.aggregate(pipeline));


    return jsonify({"statistics" : statistics}),200;

if __name__ == "__main__":
    application.run ( debug = True, host="0.0.0.0", port=5002 )