import requests

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):


    def escape(s):

        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def inr(value):
    print(value)  # Add this line
    if value is None:
        return "₹0.00"
    return f"₹{value:,.2f}"
