from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query
import requests

app = Flask(__name__,
            template_folder="templates-3",
            static_folder="static-3")
app.secret_key = "sahdfwheihfdihdidwhiofhe"


db = TinyDB("db3.json")
users_table = db.table("users")
activities_table = db.table("activities")
User = Query()
Activity = Query()

API_URL = "https://bored-api.appbrewery.com/random"

def get_random_activity():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            return {"activity": "Napaka.", "type": "Napaka", "participants": 0, "price": 0}
        return {
            "activity": data.get("activity", ""),
            "type": data.get("type", ""),
            "participants": data.get("participants", 0),
            "price": data.get("price", 0)
        }



@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users_table.search(User.username == username):
            return "Uporabnik že obstaja."
        users_table.insert({"username": username, "password": password})
        return redirect("/login")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users_table.get((User.username == username) & (User.password == password))
        if user:
            session["user"] = username
            return redirect("/dashboard")
        return "Napačno uporabniško ime ali geslo."
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    initial_activity = get_random_activity()
    user_activities = activities_table.search(Activity.username == session["user"])
    favorites = [{"id": a.doc_id, "activity": a["activity"], "type": a["type"],
                  "participants": a["participants"], "price": a["price"]} for a in user_activities]
    return render_template("dashboard.html",
                           user=session["user"],
                           activity=initial_activity,
                           favorites=favorites)


@app.route("/get_new_activity")
def get_new_activity():
    activity = get_random_activity()
    return jsonify(activity)

@app.route("/save_activity", methods=["POST"])
def save_activity():
    """Shrani aktivnost v bazo za prijavljenega uporabnika"""
    if "user" not in session:
        return jsonify({"status": "error", "message": "Niste prijavljeni"}), 401

    data = request.get_json()
    activity_text = data.get("activity")
    activity_type = data.get("type")
    participants = data.get("participants")
    price = data.get("price")

    if not activity_text:
        return jsonify({"status": "error", "message": "Aktivnost ne sme biti prazna"}), 400

    existing = activities_table.search(
        (Activity.username == session["user"]) & (Activity.activity == activity_text)
    )
    if existing:
        return jsonify({"status": "error", "message": "Aktivnost je že shranjena!"}), 400

    activities_table.insert({
        "username": session["user"],
        "activity": activity_text,
        "type": activity_type,
        "participants": participants,
        "price": price
    })
    return jsonify({"status": "success", "message": "Aktivnost shranjena!"})


@app.route("/get_favorites")
def get_favorites():
    if "user" not in session:
        return jsonify([])
    user_activities = activities_table.search(Activity.username == session["user"])
    result = [{"id": a.doc_id, "activity": a["activity"], "type": a["type"], "participants": a["participants"], "price": a["price"]} for a in user_activities]
    return jsonify(result)


@app.route("/delete_activity", methods=["POST"])
def delete_activity():
    if "user" not in session:
        return jsonify({"status": "error", "message": "Niste prijavljeni"}), 401

    data = request.get_json()
    activity_id = data.get("id")
    if not activity_id:
        return jsonify({"status": "error", "message": "ID aktivnosti ni podan"}), 400

    activity = activities_table.get(doc_id=int(activity_id))
    if activity and activity["username"] == session["user"]:
        activities_table.remove(doc_ids=[int(activity_id)])
        return jsonify({"status": "success", "message": "Aktivnost izbrisana!"})
    return jsonify({"status": "error", "message": "Aktivnost ni bila najdena ali nimate dovoljenja"}), 403

if __name__ == "__main__":
    app.run(debug=True)