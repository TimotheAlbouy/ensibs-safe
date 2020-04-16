from flask import Flask, request
import pymongo
from bson.objectid import ObjectId
from flasgger import Swagger

from constants import API_HOST, API_PORT
from token_zmq import verify_token

app = Flask(__name__)
Swagger(app, template_file="apidocs.yml")

dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = dbclient.cybersafe


@app.route("/resources/<string:id>", methods=["GET"])
def get_resource(id):
    valid_token = verify_token()
    if not valid_token:
        return {"error": "Authentication failed"}, 401

    resource = db.resources.find_one({"_id": ObjectId(id)})
    if resource is None:
        return {"error": "Resource not found"}, 404

    res = {"content": resource["content"]}
    return res, 200


@app.route("/resources", methods=["POST"])
def create_resource():
    valid_token = verify_token()
    if not valid_token:
        return {"error": "Authentication failed"}, 401

    req = request.json
    if type(req) is not dict:
        return {"error": "Incorrect payload"}, 400

    if "content" not in req:
        return {"error": "Missing content parameter"}, 400

    resource = db.resources.insert_one({"content": req["content"]})
    res = {"id": str(resource.inserted_id)}
    return res, 201


@app.route("/resources", methods=["GET"])
def get_resources():
    valid_token = verify_token()
    if not valid_token:
        return {"error": "Authentication failed"}, 401

    resources = [{"id": str(r["_id"])} for r in db.resources.find({}, {"content": 0})]
    res = {"resources": resources}
    return res, 200


if __name__ == "__main__":
    app.run(host=API_HOST, port=API_PORT)
