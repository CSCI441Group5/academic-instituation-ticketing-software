import app.database as database

# Test naming convention: test_<method_or_route>_<starting_state>_<expected_result>
# Covers TC-11 and the ticket history part of TC-13

# Some TC's show up more than once because one report test case can have different situations to check

# Helper function for loading a ticket row created through the route under test
def ticket_by_title(title):
    connection = database.connect_db()
    try:
        return connection.execute(
            "SELECT * FROM tickets WHERE title = ?",
            (title,),
        ).fetchone()
    finally:
        connection.close()


# TC-11: Ticket History Logging
# Verifies that creating a ticket records an initial history entry
def test_post_new_ticket_valid_student_request_logs_created_history(client, login):
    # Sign in as a student because ticket history should record who created it
    login("student1@parkfield.edu")

    # Submit a valid ticket through the same route used by the real form
    response = client.post(
        "/tickets/new",
        data={
            "title": "History create check",
            "category": "IT",
            "description": "Ticket used to check creation history.",
            "attachment": "",
        },
        follow_redirects=False,
    )

    # After saving the ticket, load its history from the database
    assert response.status_code == 302
    ticket = ticket_by_title("History create check")
    history = database.get_ticket_history(ticket["id"])

    # The first history row should record ticket creation by the requester
    assert len(history) == 1
    assert history[0]["change_type"] == "created"
    assert history[0]["new_value"] == "Pending"
    assert history[0]["actor_name"] == "Amy"


# TC-11: Ticket History Logging
# Verifies that a staff status update records the old and new status
def test_post_update_ticket_claimed_ticket_logs_status_history(client, login, create_ticket):
    # Create a ticket already claimed by Carl so he can update its status
    ticket_id = create_ticket(
        "History status update check",
        "IT",
        "Ticket used to check status update history.",
        "student1@parkfield.edu",
        status="Pending",
        claimed_by="Carl",
    )

    # Sign in as Carl and update the ticket status
    login("staff1@parkfield.edu")
    response = client.post(
        f"/tickets/{ticket_id}/update",
        data={"status": "In Progress", "claimed_by": "Carl"},
        follow_redirects=False,
    )

    history = database.get_ticket_history(ticket_id)
    status_entries = [entry for entry in history if entry["change_type"] == "status_updated"]

    # The status history should show the transition from Pending to In Progress
    assert response.status_code == 302
    assert len(status_entries) == 1
    assert status_entries[0]["old_value"] == "Pending"
    assert status_entries[0]["new_value"] == "In Progress"
    assert status_entries[0]["actor_name"] == "Carl"


# TC-11: Ticket History Logging
# Verifies that claiming an unclaimed ticket records the ownership change
def test_post_claim_ticket_unclaimed_ticket_logs_claim_history(client, login, create_ticket):
    # Create an unclaimed ticket that staff can claim
    ticket_id = create_ticket(
        "History claim check",
        "IT",
        "Ticket used to check claim history.",
        "student1@parkfield.edu",
    )

    # Sign in as Carl and claim the ticket
    login("staff1@parkfield.edu")
    response = client.post(
        f"/tickets/{ticket_id}/claim",
        data={"user_name": "Carl"},
        follow_redirects=False,
    )

    history = database.get_ticket_history(ticket_id)
    claim_entries = [entry for entry in history if entry["change_type"] == "claimed"]

    # The claim history should show that Carl claimed the unassigned ticket
    assert response.status_code == 302
    assert len(claim_entries) == 1
    assert claim_entries[0]["old_value"] == "Unclaimed"
    assert claim_entries[0]["new_value"] == "Carl"
    assert claim_entries[0]["actor_name"] == "Carl"


# TC-13: Retrieval of Requester Tickets and Ticket History
# Verifies that an authorized requester can view their ticket history page
def test_get_ticket_detail_own_ticket_shows_history(client, login, create_ticket):
    # Create a ticket for student1, which also creates the first history row
    ticket_id = create_ticket(
        "History detail check",
        "IT",
        "Ticket used to check the detail page history.",
        "student1@parkfield.edu",
    )

    # Sign in as student1 and open the ticket detail page
    login("student1@parkfield.edu")
    response = client.get(f"/tickets/{ticket_id}")
    text = response.get_data(as_text=True)

    # The detail page should show the ticket and its history entries
    assert response.status_code == 200
    assert "History detail check" in text
    assert "Ticket History" in text
    assert "created" in text
    assert "Amy" in text


# TC-13: Retrieval of Requester Tickets and Ticket History
# Verifies that one requester cannot view another requester's ticket history
def test_get_ticket_detail_other_student_ticket_returns_forbidden(client, login, create_ticket):
    # Create a ticket owned by student1
    ticket_id = create_ticket(
        "History forbidden check",
        "IT",
        "Ticket used to check history access control.",
        "student1@parkfield.edu",
    )

    # Sign in as student2 and try to open student1's ticket detail page
    login("student2@parkfield.edu")
    response = client.get(f"/tickets/{ticket_id}")

    # A requester should only be able to view their own ticket history
    assert response.status_code == 403
