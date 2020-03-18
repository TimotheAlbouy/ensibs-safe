from flask import Flask, request
from flask_pymongo import PyMongo
from flask_restplus import Api, Resource

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)
api = Api(app=app, version='0.1', title='Safe Api', description='REST Safe API', validate=True)


@api.route('/resources/<int:id>')
class SafeResource(Resource):
    def get(self):
        return 'Hello World!'

    def post(self):
        return


if __name__ == '__main__':
    app.run()
