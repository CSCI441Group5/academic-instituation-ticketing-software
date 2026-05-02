# This file prepares the app before each test runs

import pytest

from app import create_app
import app.database as database

# fixture is a function that prepares something your test needs

@pytest.fixture()
def app(tmp_path, monkeypatch):
    # Tests should not touch the real app database, so create new temporary database
    test_db_path = tmp_path / "tickets.db"
    # temporarily change the app’s database path
    monkeypatch.setattr(database, "DB_PATH", test_db_path)

    # create the app and put it into test mode
    flask_app = create_app()
    # Tests should save uploaded files in a temporary folder
    flask_app.config.update(
        TESTING=True,
        UPLOAD_FOLDER=tmp_path / "uploads",
    )

    return flask_app


# client is like a fake browser that lets us make GET and POST requests without
# starting the web server with ./run.sh
@pytest.fixture()
def client(app):
    return app.test_client()


# Helper used by ticket tests that need a signed-in user
# It posts to the same login route that the real form uses
@pytest.fixture()
def login(client):
    def _login(email, password="password"):
        return client.post(
            "/auth/login_submit",
            data={"email": email, "password": password},
            follow_redirects=False,
        )

    return _login


# Helper used by tests that need a seeded account ID
# Tickets are linked to requester_account_id, so test tickets need this value
@pytest.fixture()
def account_id():
    def _account_id(email):
        account = database.get_university_account_by_email(email)
        assert account is not None
        return account["id"]

    return _account_id


# Helper used by dashboard and ticket tests that need database tickets
# It creates rows directly so tests can focus on the behavior they are checking
@pytest.fixture()
def create_ticket(account_id):
    def _create_ticket(
        title,
        category,
        description,
        requester_email,
        status="Pending",
        claimed_by="",
        created_at=None,
    ):
        ticket_id = database.save_ticket(
            {
                "title": title,
                "category": category,
                "description": description,
                "attachment": None,
                "requester_account_id": account_id(requester_email),
                "status": status,
                "claimed_by": claimed_by,
            }
        )

        # Some filter tests need stable dates, so update created_at after insert
        # when a specific timestamp is provided
        if created_at is not None:
            connection = database.connect_db()
            try:
                connection.execute(
                    "UPDATE tickets SET created_at = ? WHERE id = ?",
                    (created_at, ticket_id),
                )
                connection.commit()
            finally:
                connection.close()

        return ticket_id

    return _create_ticket
