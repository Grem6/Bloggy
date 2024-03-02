import datetime
import os
from flask import Flask, redirect, render_template, request, url_for
from pymongo import MongoClient
from dotenv import load_dotenv

app = Flask(__name__)
client = MongoClient(os.environ.get("MONGODB_URI"))
app.db = client.bloggy


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
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
    return render_template("index.html", posts=posts_with_date)


@app.route("/delete/<int:index>", methods=["POST"])
def delete_post(index):
    post_to_delete = list(app.db.posts.find({}))[index - 1]
    app.db.posts.delete_one({"_id": post_to_delete["_id"]})
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
