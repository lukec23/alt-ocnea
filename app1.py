from flask import Flask, render_template, request, redirect, session
from tinydb import TinyDB, Query
from markupsafe import escape # Uporablja se za user input, npr: f"Uporabik je vsedsel: {escape(text)}"

app = Flask(
    __name__,
    template_folder="template1",
    static_folder="static"
)
app.secret_key = "4438015b65c442f9a8b5296d974bd60d47f9ce0816366b873f27ec6b0668c927"

db = TinyDB("db.json")
users = db.table("users")
notes = db.table("notes")

User = Query()
Notes = Query()

@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.get(User.username == username)
        if user and user["password"] == password:
            session["user"] = username
            return redirect("/dashboard")
        return "Napačno uporabniško ime ali geslo."

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.search(User.username == username):
            return "Uporabnik že obstaja."
        
        users.insert({"username" : username, "password": password, "note" : ""})
        return redirect("/login")
    
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    

    userNotes = notes.search(Notes.username == session["user"])

    return render_template("dashboard.html", user=session["user"], notes=userNotes)


@app.route("/saveNote", methods=["POST"])
def saveNote():
    if request.method == "POST":
        data = request.form
        print(data)

        notes.insert({'username': session["user"], 'title': data["title"], 'content': data["content"]})

        return {"status": 200}


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()

    return {"status": 200}


app.run(debug=True)