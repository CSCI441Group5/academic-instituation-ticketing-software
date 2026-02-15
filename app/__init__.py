# Initializes the Flask application
# Registers blueprints and shared configuration

# used to read environmental variables
import os
from flask import Flask

def create_app():
    # Creates and configures the Flask app, then registers blueprints
    app = Flask(__name__)

     # Set Flask SECRET_KEY from environment variable
     # If it’s not set, it can cause issues, so use a temporary fallback
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "replace_later")

    @app.get("/")
    def index():
        return {"status": "ok"}

    return app