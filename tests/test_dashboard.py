# Covers TC-13, TC-16 - TC-19

# TC-13: Retrieval of Requester Tickets
# Verifies that requesters can retrieve only their own active tickets
def test_get_dashboard_student_user_shows_only_own_active_tickets(client, login, create_ticket):
    # Create one active ticket for each student
    create_ticket(
        "Student one dashboard check",
        "IT",
        "Unique active ticket for student one dashboard.",
        "student1@parkfield.edu",
    )
    create_ticket(
        "Student two dashboard check",
        "IT",
        "Unique active ticket for student two dashboard.",
        "student2@parkfield.edu",
    )
    # Sign in as student1 and load the active requester dashboard
    login("student1@parkfield.edu")
    response = client.get("/dashboard")

    text = response.get_data(as_text=True)

    # Student1 should see their own ticket, but not another requester's ticket
    assert response.status_code == 200
    assert "Unique active ticket for student one dashboard." in text
    assert "Unique active ticket for student two dashboard." not in text


# TC-16: Staff and Manager Dashboard Visibility
# Verifies that staff dashboards only show tickets from the staff user's department
def test_get_staff_dashboard_staff_user_shows_only_department_tickets(client, login, create_ticket):
    # Create active tickets in two departments
    create_ticket(
        "Dashboard IT route check",
        "IT",
        "Unique IT ticket visible to IT staff.",
        "student1@parkfield.edu",
    )
    create_ticket(
        "Dashboard facilities route check",
        "Facilities",
        "Unique facilities ticket hidden from IT staff.",
        "student1@parkfield.edu",
    )

    # Sign in as staff1, whose department is IT
    login("staff1@parkfield.edu")
    response = client.get("/staff_dashboard")

    # Turn the response into normal text so it is easier to read and check
    text = response.get_data(as_text=True)

    # IT staff should see the IT department ticket, but not the Facilities ticket
    assert response.status_code == 200
    assert "Unique IT ticket visible to IT staff." in text
    assert "Unique facilities ticket hidden from IT staff." not in text


# TC-16: Staff and Manager Dashboard Visibility
# Verifies that managers can view active tickets across departments
def test_get_staff_dashboard_manager_user_shows_all_department_tickets(client, login, create_ticket):
    # Create active tickets in multiple departments
    create_ticket(
        "Manager IT visibility check",
        "IT",
        "Unique IT ticket visible to managers.",
        "student1@parkfield.edu",
    )
    create_ticket(
        "Manager facilities visibility check",
        "Facilities",
        "Unique facilities ticket visible to managers.",
        "student1@parkfield.edu",
    )

    # Sign in as a manager, who should not be limited to one department
    login("manager1@parkfield.edu")
    response = client.get("/staff_dashboard")

    text = response.get_data(as_text=True)

    # Managers should see both active tickets
    assert response.status_code == 200
    assert "Unique IT ticket visible to managers." in text
    assert "Unique facilities ticket visible to managers." in text


# TC-17: Active Dashboard and Archive Separation
# Verifies that staff active dashboards hide closed tickets routed to their department
def test_get_staff_dashboard_staff_user_hides_closed_department_tickets(client, login, create_ticket):
    # Create one active IT ticket and one closed IT ticket
    create_ticket(
        "Staff active dashboard ticket",
        "IT",
        "Unique active IT ticket visible on staff dashboard.",
        "student1@parkfield.edu",
        status="Pending",
    )
    create_ticket(
        "Staff closed dashboard ticket",
        "IT",
        "Unique closed IT ticket hidden from active staff dashboard.",
        "student1@parkfield.edu",
        status="Closed",
    )

    # Sign in as IT staff and load the active staff dashboard
    login("staff1@parkfield.edu")
    response = client.get("/staff_dashboard")

    text = response.get_data(as_text=True)

    # The active dashboard should exclude closed tickets
    assert response.status_code == 200
    assert "Unique active IT ticket visible on staff dashboard." in text
    assert "Unique closed IT ticket hidden from active staff dashboard." not in text


# TC-17: Active Dashboard and Archive Separation
# Verifies that staff archives only show closed tickets from the staff user's department
def test_get_archive_staff_user_shows_only_department_closed_tickets(client, login, create_ticket):
    # Create closed tickets in two departments and an active ticket in IT
    create_ticket(
        "Staff archive IT ticket",
        "IT",
        "Unique closed IT ticket visible to IT staff archive.",
        "student1@parkfield.edu",
        status="Closed",
    )
    create_ticket(
        "Staff archive facilities ticket",
        "Facilities",
        "Unique closed facilities ticket hidden from IT staff archive.",
        "student1@parkfield.edu",
        status="Closed",
    )
    create_ticket(
        "Staff archive active IT ticket",
        "IT",
        "Unique active IT ticket hidden from staff archive.",
        "student1@parkfield.edu",
        status="Pending",
    )

    # Sign in as IT staff and load the archive
    login("staff1@parkfield.edu")
    response = client.get("/archive")

    text = response.get_data(as_text=True)

    # IT staff archives should show only closed IT tickets
    assert response.status_code == 200
    assert "Unique closed IT ticket visible to IT staff archive." in text
    assert "Unique closed facilities ticket hidden from IT staff archive." not in text
    assert "Unique active IT ticket hidden from staff archive." not in text


# TC-17: Active Dashboard and Archive Separation
# Verifies that managers can view closed archive tickets across departments
def test_get_archive_manager_user_shows_all_department_closed_tickets(client, login, create_ticket):
    # Create closed tickets in multiple departments
    create_ticket(
        "Manager archive IT ticket",
        "IT",
        "Unique closed IT ticket visible to manager archive.",
        "student1@parkfield.edu",
        status="Closed",
    )
    create_ticket(
        "Manager archive facilities ticket",
        "Facilities",
        "Unique closed facilities ticket visible to manager archive.",
        "student1@parkfield.edu",
        status="Closed",
    )

    # Sign in as manager and load the archive
    login("manager1@parkfield.edu")
    response = client.get("/archive")

    text = response.get_data(as_text=True)

    # Managers should see closed tickets from both departments
    assert response.status_code == 200
    assert "Unique closed IT ticket visible to manager archive." in text
    assert "Unique closed facilities ticket visible to manager archive." in text


# TC-18: Dashboard Filtering
# Verifies that status and category filters narrow the requester dashboard
def test_get_dashboard_filters_by_status_and_category(client, login, create_ticket):
    # Create active tickets that differ by status and category
    create_ticket(
        "Filtered pending IT ticket",
        "IT",
        "Unique pending IT ticket for dashboard filters.",
        "student1@parkfield.edu",
        status="Pending",
    )
    create_ticket(
        "Filtered resolved IT ticket",
        "IT",
        "Unique resolved IT ticket hidden by pending filter.",
        "student1@parkfield.edu",
        status="Resolved",
    )
    create_ticket(
        "Filtered pending facilities ticket",
        "Facilities",
        "Unique pending facilities ticket hidden by IT filter.",
        "student1@parkfield.edu",
        status="Pending",
    )

    # Sign in as student1 and apply both status and category filters
    login("student1@parkfield.edu")
    response = client.get(
        "/dashboard?status_filter=Pending&category_filter=IT"
    )

    text = response.get_data(as_text=True)

    # Only the ticket matching both filter values should appear
    assert response.status_code == 200
    assert "Unique pending IT ticket for dashboard filters." in text
    assert "Unique resolved IT ticket hidden by pending filter." not in text
    assert "Unique pending facilities ticket hidden by IT filter." not in text


# TC-18: Dashboard Filtering
# Verifies that archive date filters narrow closed ticket results
def test_get_archive_filters_closed_tickets_by_date(client, login, create_ticket):
    # Create two closed tickets with stable timestamps
    create_ticket(
        "Old closed archive ticket",
        "IT",
        "Unique old closed ticket hidden by archive date filter.",
        "student1@parkfield.edu",
        status="Closed",
        created_at="2026-04-01 12:00:00",
    )
    create_ticket(
        "New closed archive ticket",
        "IT",
        "Unique new closed ticket visible through archive date filter.",
        "student1@parkfield.edu",
        status="Closed",
        created_at="2026-04-20 12:00:00",
    )

    # Sign in as student1 and filter for archive tickets after April 10
    login("student1@parkfield.edu")
    response = client.get("/archive?date_after=2026-04-10")

    text = response.get_data(as_text=True)

    # Only the newer closed ticket should remain after filtering
    assert response.status_code == 200
    assert "Unique old closed ticket hidden by archive date filter." not in text
    assert "Unique new closed ticket visible through archive date filter." in text


# TC-18: Dashboard Filtering
# Verifies that staff dashboard filters work within the staff user's department
def test_get_staff_dashboard_filters_by_status_category_and_date(client, login, create_ticket):
    # Create department tickets that differ by status, category, and date
    create_ticket(
        "Staff filtered visible ticket",
        "IT",
        "Unique IT ticket matching all staff dashboard filters.",
        "student1@parkfield.edu",
        status="Pending",
        created_at="2026-04-20 12:00:00",
    )
    create_ticket(
        "Staff filtered resolved ticket",
        "IT",
        "Unique IT ticket hidden by pending status filter.",
        "student1@parkfield.edu",
        status="Resolved",
        created_at="2026-04-20 12:00:00",
    )
    create_ticket(
        "Staff filtered old ticket",
        "IT",
        "Unique IT ticket hidden by date filter.",
        "student1@parkfield.edu",
        status="Pending",
        created_at="2026-04-01 12:00:00",
    )
    create_ticket(
        "Staff filtered facilities ticket",
        "Facilities",
        "Unique facilities ticket hidden from IT staff filter.",
        "student1@parkfield.edu",
        status="Pending",
        created_at="2026-04-20 12:00:00",
    )

    # Sign in as IT staff and apply filters
    login("staff1@parkfield.edu")
    response = client.get(
        "/staff_dashboard?status_filter=Pending&category_filter=IT&date_after=2026-04-10"
    )

    text = response.get_data(as_text=True)

    # Only the IT ticket matching every filter should appear
    assert response.status_code == 200
    assert "Unique IT ticket matching all staff dashboard filters." in text
    assert "Unique IT ticket hidden by pending status filter." not in text
    assert "Unique IT ticket hidden by date filter." not in text
    assert "Unique facilities ticket hidden from IT staff filter." not in text


# TC-19: Staff Dashboard Action Controls
# Unclaimed tickets show Claim. Claimed tickets show Edit for the owner. Managers can assign department staff.
def test_get_staff_dashboard_unclaimed_ticket_shows_claim_action(client, login, create_ticket):
    # Create an unclaimed IT ticket
    ticket_id = create_ticket(
        "Unclaimed dashboard action ticket",
        "IT",
        "Unique unclaimed ticket that should show a claim action.",
        "student1@parkfield.edu",
        status="Pending",
        claimed_by="",
    )

    # Sign in as IT staff and load the staff dashboard
    login("staff1@parkfield.edu")
    response = client.get("/staff_dashboard")

    text = response.get_data(as_text=True)

    # Unclaimed tickets should show ownership state and post to the claim route
    assert response.status_code == 200
    assert "Unique unclaimed ticket that should show a claim action." in text
    assert "Unclaimed" in text
    assert f"/tickets/{ticket_id}/claim" in text
    assert "Claim" in text


# TC-19: Staff Dashboard Action Controls
# Verifies that staff can open the edit form for tickets they claimed
def test_get_staff_dashboard_claimed_ticket_shows_edit_action_for_owner(client, login, create_ticket):
    # Create a ticket already claimed by the seeded IT staff user Carl
    ticket_id = create_ticket(
        "Claimed dashboard edit ticket",
        "IT",
        "Unique claimed ticket that should show edit action to owner.",
        "student1@parkfield.edu",
        status="Pending",
        claimed_by="Carl",
    )

    # Sign in as Carl from the IT department
    login("staff1@parkfield.edu")
    response = client.get("/staff_dashboard")

    text = response.get_data(as_text=True)

    # The owning staff member should see the edit link for their claimed ticket
    assert response.status_code == 200
    assert "Unique claimed ticket that should show edit action to owner." in text
    assert "Claimed By: Carl" in text
    assert f"?edit={ticket_id}" in text


# TC-19: Staff Dashboard Action Controls
# Verifies that manager edit mode exposes reassignment choices for the ticket department
def test_get_staff_dashboard_manager_edit_mode_shows_department_staff_choices(client, login, create_ticket):
    # Create an IT ticket for manager reassignment testing
    ticket_id = create_ticket(
        "Manager edit assignment ticket",
        "IT",
        "Unique manager edit ticket for assignment choices.",
        "student1@parkfield.edu",
        status="Pending",
    )

    # Sign in as manager and open the ticket in edit mode
    login("manager1@parkfield.edu")
    response = client.get(f"/staff_dashboard?edit={ticket_id}")

    text = response.get_data(as_text=True)

    # Manager edit mode should include a claimed_by select for IT staff only
    assert response.status_code == 200
    assert "Unique manager edit ticket for assignment choices." in text
    assert 'select name="claimed_by"' in text
    assert "Carl" in text
    assert "Dana" not in text
