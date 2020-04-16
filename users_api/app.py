from flask import Flask, request
import pymongo
import bcrypt
from flasgger import Swagger

from constants import API_HOST, API_PORT
from token_zmq import sign_token

app = Flask(__name__)
Swagger(app, template_file="apidocs.yml")

dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = dbclient.cybersafe


@app.route("/register", methods=["POST"])
async def register():
    req = request.json
    if type(req) is not dict:
        return {"error": "Incorrect payload"}, 400
    if "username" not in req:
        return {"error": "Missing username parameter"}, 400
    if "password" not in req:
        return {"error": "Missing password parameter"}, 400
    if len(req["username"]) < 3:
        return {"error": "Username too short"}, 400
    if len(req["password"]) < 3:
        return {"error": "Password too short"}, 400

    user = db.users.find_one({"username": req["username"]})
    if user is not None:
        return {"error": "Username already taken"}, 409

    password_hash = bcrypt.hashpw(req["password"].encode("utf-8"), bcrypt.gensalt())
    db.users.insert_one({
        "username": req["username"],
        "password_hash": password_hash
    })

    token = await sign_token(req["username"])
    res = {"token": token}
    return res, 201


@app.route("/login", methods=["POST"])
async def login():
    req = request.json
    if type(req) is not dict:
        return {"error": "Incorrect payload"}, 400
    if "username" not in req:
        return {"error": "Missing username parameter"}, 400
    if "password" not in req:
        return {"error": "Missing password parameter"}, 400

    user = db.users.find_one({"username": req["username"]})
    if user is None:
        return {"error": "User not found"}, 404

    if not bcrypt.checkpw(req["password"].encode("utf-8"), user["password_hash"]):
        return {"error": "Incorrect username/password"}, 401

    token = await sign_token(req["username"])
    res = {"token": token}
    return res, 200


if __name__ == "__main__":
    app.run(host=API_HOST, port=API_PORT)
