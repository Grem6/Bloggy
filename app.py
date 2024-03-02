import datetime
import os
from flask import Flask, redirect, render_template, request, url_for, session
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = MongoClient(os.environ.get("MONGODB_URI"))
app.db = client.bloggy
app.secret_key = os.environ.get("SECRET_KEY")

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


@app.route("/", methods=["GET", "POST"])
def home():
    logged_in = session.get("logged_in")
    print(logged_in)
    if request.method == "POST" and session.get("logged_in"):
        post_content = request.form.get("content")
        post_time = datetime.datetime.today().strftime("%Y-%m-%d")
        app.db.posts.insert_one({"post": post_content, "date": post_time})
        return redirect(url_for("home"))
    posts_with_date = [
        (
            post["post"],
            post["date"],
            datetime.datetime.strptime(post["date"], "%Y-%m-%d").strftime("%b %d"),
        )
        for post in app.db.posts.find({})
    ]
    return render_template("index.html", posts=posts_with_date, logged_in=logged_in)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            return render_template("index.html")
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("home"))


def login_required(func):
    def wrapper(*args, **kwargs):
        if session.get("logged_in"):
            return func(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return wrapper


@app.route("/delete/<int:index>", methods=["POST"])
def delete_post(index):
    post_to_delete = list(app.db.posts.find({}))[index - 1]
    app.db.posts.delete_one({"_id": post_to_delete["_id"]})
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
