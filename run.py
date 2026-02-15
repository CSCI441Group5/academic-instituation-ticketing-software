# Entry point for running the Flask application locally
# Creates the app instance and starts the development server

from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True for local dev
    # change later
    app.run(debug=True)