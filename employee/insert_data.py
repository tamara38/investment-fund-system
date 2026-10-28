import json
from pymongo import MongoClient

client = MongoClient(
    host="localhost",
    port=27017,
    username="root",
    password="example",
    authSource="admin"
)

database = client["investment_fond"]
collection = database["assets"]

with open("assets.json", "r", encoding="utf-8") as f:
    data = json.load(f)

collection.insert_many(data)

print("Done!")