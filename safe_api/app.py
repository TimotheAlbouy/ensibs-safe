from flask import Flask, request
import pymongo
from bson.objectid import ObjectId
from flasgger import Swagger

from safe_api_constants import API_HOST, API_PORT
from token_verification import verify_token, verify_token_errors

app = Flask(__name__)
Swagger(app, template_file="apidocs.yml")

dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = dbclient.cybersafe


@app.route("/resources/<string:id>", methods=["GET"])
def get_resource(id):
    status = verify_token()
    if status != 200:
        return {"error": verify_token_errors[status]}, status

    resource = db.resources.find_one({"_id": ObjectId(id)})
    if resource is None:
        return {"error": "Resource not found"}, 404

    res = {"content": resource["content"]}
    return res, 200


@app.route("/resources", methods=["POST"])
def create_resource():
    status = verify_token()
    if status != 200:
        return {"error": verify_token_errors[status]}, status

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
    status = verify_token()
    if status != 200:
        return {"error": verify_token_errors[status]}, status

    resources = [{"id": str(r["_id"])} for r in db.resources.find({}, {"content": 0})]
    res = {"resources": resources}
    return res, 200


if __name__ == "__main__":
    app.run(host=API_HOST, port=API_PORT)
