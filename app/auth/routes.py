# URL routes
from flask import Blueprint, redirect, render_template, request, url_for

# Create a blueprint named "auth"
# The name is used for URL building (url_for("auth.login"))
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # On submit (POST), skip auth checks (for now) and send the user to dashboard
    if request.method == "POST":
        return redirect(url_for("auth.dashboard"))

    # When user visits /login, Flask renders login.html
    # render_template looks inside app/templates/
    return render_template("login.html")

@auth_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")