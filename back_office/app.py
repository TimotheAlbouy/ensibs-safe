from flask import Flask, render_template, session, request, redirect
import requests

from constants import USERS_API, SAFE_API, SECRET_KEY, BO_PORT

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/apidocs")
def apidocs():
    return render_template("apidocs.html", users_api=USERS_API, safe_api=SAFE_API)


@app.route("/resources")
def list_resources():
    res = requests.get(SAFE_API + "/resources", headers={
        "Authorization": "Bearer " + session.get("token")
    })
    if res.status_code != 200:
        return redirect("/login")
    return render_template("list_resources.html", resources=res.json()["resources"])


@app.route("/resources/<string:id>")
def show_resource(id):
    res = requests.get(SAFE_API + "/resources/" + id, headers={
        "Authorization": "Bearer " + session.get("token")
    })
    if res.status_code != 200:
        return redirect("/login")
    return render_template("show_resource.html", id=id, content=res.json()["content"])


@app.route("/create-resource", methods=["GET"])
def create_resource_form():
    return render_template("create_resource.html")


@app.route("/create-resource", methods=["POST"])
def create_resource():
    res = requests.post(SAFE_API + "/resources", headers={
        "Authorization": "Bearer " + session.get("token")
    }, json={
        "content": request.form.get("content")
    })
    if res.status_code != 201:
        return render_template("create_resource.html", error=res.json()["error"])
    return redirect("/resources")


@app.route("/register", methods=["GET"])
def register_form():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    res = requests.post(USERS_API + "/register", json={
        "username": username,
        "password": password
    })
    if res.status_code != 201:
        return render_template("register.html", error=res.json()["error"])
    session["token"] = res.json()["token"]
    session["username"] = username
    return redirect("/resources")


@app.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    res = requests.post(USERS_API + "/login", json={
        "username": username,
        "password": password
    })
    if res.status_code != 200:
        return render_template("login.html", error=res.json()["error"])
    session["token"] = res.json()["token"]
    session["username"] = username
    return redirect("/resources")


@app.route("/logout")
def logout():
    session["token"] = None
    session["username"] = None
    return redirect("/")


if __name__ == "__main__":
    app.run(port=BO_PORT)
