# URL routes
from flask import Blueprint, render_template

# Create a blueprint named "auth"
# The name is used for URL building (url_for("auth.login"))
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET"])
def login():
    # When user visits /login, Flask renders login.html
    # render_template looks inside app/templates/
    return render_template("login.html")