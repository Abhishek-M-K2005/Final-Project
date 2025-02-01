import os

import sqlite3
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from extension import apology, login_required, inr

app = Flask(__name__)


if __name__ == "__main__":
    app.run(debug=True)

app.jinja_env.filters["inr"] = inr

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///logs.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

SPORTS = ["Cricket", "Kabaddi", "Football", "Volleyball", "Handball", "Hockey"]

@app.route("/")
def main_page():
    if "id" not in session:
        return render_template("main_page.html")
    elif session["id"]:
        data3= db.execute("SELECT * FROM users JOIN reg1 ON users.id = user_id")
        if data3 is None:
            return render_template("main_page.html")
        return render_template("main_page.html", data3=data3)

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.form.get("username") is None:
        return apology("Please Provide Username", 400)
    data = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
    if len(data) != 1:
        return apology("Username not found", 400)
    if request.form.get("password") is None:
        return apology("Please Provide Password", 400)
    if not check_password_hash(data[0]["hash"], request.form.get("password")) :
        return apology("Enter correct Password", 400)
    session["id"] = data[0]["id"]
    return redirect("/")

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        if request.form.get("username") is None:
            return apology("Please Enter valid Username", 400)
        if request.form.get("password") is None:
            return apology("Can't proceed without Password")
        data = db.execute("SELECT * FROM users WHERE username=?", request.form.get("username"))
        if len(data) != 0:
            return apology("User Has Registered Once!", 400)
        db.execute("INSERT INTO users (username, hash, age, mail) VALUES(?, ?, ?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")), request.form.get("age"), request.form.get("mail"))

        return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/sport_register")
@login_required
def sport_reg():
    return render_template("sport_register.html")

@app.route("/form", methods=["GET", "POST"])
@login_required
def reg():
    if request.method == "GET":
        return render_template("form.html", sports=SPORTS)
    else:
        if request.form.get("JERSEY_NAME") is None:
            return apology("Please Enter The Nickname for the Jersey.", 400)
        if request.form.get("sport") is None:
            return apology ("Please Enter the sport you want to participate in.", 400)
        if request.form.get("Jersey Number") is None:
            flash("invalid Jersey Number", "error")
            return render_template("/form.html")
        if request.form.get("password") is None:
            return apology ("Please enter your password to confirm that it is you.", 400)
        data1 = db.execute("SELECT * FROM reg1 WHERE jersey_name=? AND sports=?", request.form.get("JERSEY_NAME"), request.form.get("sport"))
        data2=db.execute("SELECT * FROM reg1 WHERE user_id=? AND sports=?",session["id"], request.form.get("sport"))
        data3 = db.execute("SELECT * FROM users WHERE id=?", session["id"])
        if not check_password_hash(data3[0]["hash"], request.form.get("password")):
            return apology("Oops! Please enter Password Correctly", 404)
        if data1 is not None:
            for data in data1:
                if data["jersey_name"]== request.form.get("JERSEY_NAME") and data["sports"]==request.form.get("sport"):
                    return apology ("Jersey Name has been taken by someone already.", 400)
        if data2 is not None:
            for data in data2:
                if data["sports"] == request.form.get("sport"):
                    return apology ("You have already applied for this Sports", 400)
        db.execute("INSERT INTO reg1 (jersey_name, jersey_num, paid, user_id, sports) VALUES(?, ?, ?, ? , ?)",
                    request.form.get("JERSEY_NAME"), request.form.get("Jersey Number"), 1,session["id"], request.form.get("sport"))
        return redirect("/")

@app.route("/cricket")
def cricket():
    return render_template("cricket.html")

@app.route("/change_pass", methods=["GET", "POST"])
@login_required
def change():
    if request.method == "GET":
        return render_template("change_pass.html")
    else:
        if not (request.form.get("old_pass") and request.form.get("new_pass") and request.form.get("conf_pass")):
            return apology("Please fill out all the details", 400)
        data = db.execute("SELECT * FROM users WHERE id = ?", session["id"])[0]
        if not check_password_hash(data["hash"], request.form.get("old_pass")):
            return apology("Wrong Bro! Incorrect password.", 400)
        if request.form.get("conf_pass") != request.form.get("new_pass"):
            return apology("The new password and the confirm Password are not matching", 400)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(request.form.get("new_pass")), session["id"])
        flash("Password Changed!")
        return redirect("/")

@app.route("/mysp", methods=["GET", "POST"])
@login_required
def mysp():
    if "id" not in session:
        return redirect("/")
    if request.method == "GET":
        data = db.execute("SELECT sports FROM reg1 WHERE user_id = ?", session["id"])
        if data is None:
            return render_template("mysports.html")
        return render_template("mysports.html", data = data)
    else:
        sp = request.form.get("sports")
        db.execute("DELETE FROM reg1 WHERE sports = ? AND user_id = ?", sp, session["id"])
        return redirect("/")

@app.route("/profile")
@login_required
def profile():
    if "id" not in session:
        return redirect("/")
    data = db.execute("SELECT * FROM users WHERE id = ?", session["id"])[0]
    if data is None:
        return redirect("/")
    return render_template("profile.html", data = data)

@app.route("/features")
def features():
    return render_template("features.html")
