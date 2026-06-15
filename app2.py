from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from passlib.hash import sha256_crypt #password hashing
from base64 import b64encode

app = Flask(
    __name__,
    template_folder="template-2",
    static_folder="static-2"
)
app.secret_key = "fdjhiofhfjdg9h349hidfshg98e934ej983"

conn = sqlite3.connect("db2.db", check_same_thread=False) # povezava na bazo
cur = conn.cursor() # "cursor" baze
cur.execute(
    "CREATE TABLE IF NOT EXISTS users"
    "(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)"
)
cur.execute(
    "CREATE TABLE IF NOT EXISTS posts"
    "(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, title TEXT, content TEXT, image MEDIUMBLOB, FOREIGN KEY (user_id) REFERENCES users(id))"
)

@app.route("/")
def index():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if cur.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone():
            return "Uporabnik že obstaja."

        password_hash = sha256_crypt.encrypt(password)

        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        print(user)

        if user and sha256_crypt.verify(password, user[2]):
            session["user"] = username
            return redirect("/dashboard")
        return "napacno uporabnisko ime ali geslo"

    return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return {"status": "success"}, 200


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    posts = cur.execute("SELECT posts.id, posts.title, posts.username, posts.user_id, posts.content, posts.image FROM posts").fetchall()
    posts = [{"id": post[0], "title": post[1], "username": post[2], "user_id": post[3], "content": post[4], "image": b64encode(post[5]).decode('utf-8') if post[5] else None} for post in posts]

    return render_template("dashboard.html", user=session["user"], posts=posts)


@app.route("/newPost", methods=["GET", "POST"])
def newPost():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        data = request.form
        cur.execute("SELECT id FROM users WHERE username=?", (session["user"],))
        slika = request.files.get('image', '')
        user_id = cur.fetchone()[0]
        cur.execute("INSERT INTO posts (user_id, username, title, content, image) VALUES (?, ?, ?, ?, ?)", (user_id, session["user"], data["title"], data["content"], slika.read() if slika else None))
        conn.commit()

        return redirect("/dashboard")
    return render_template("newPost.html")


@app.route("/deletePost", methods=["POST"])
def deletePost():
    if request.method == "POST":
        data = request.form
        cur.execute("DELETE FROM posts WHERE id=?", (int(data["id"]),))
        conn.commit()

        return jsonify({"status": "deleted"}), 200


app.run(debug=True)