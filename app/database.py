"""
Database access.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

# Build the full path to the database file.
DB_PATH = Path(__file__).resolve().parent.parent / "instance" / "tickets.db"


def _ensure_schema(connection: sqlite3.Connection) -> None:
    """Create the tickets table if it does not already exist"""

    connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,               -- unique ticket ID
                title TEXT NOT NULL,                                -- short ticket summary
                category TEXT NOT NULL,                             -- type of issue
                description TEXT NOT NULL,                          -- details about the problem
                attachment TEXT,                                    -- file path or attachment reference
                requester_account_id INTEGER,                       -- linked university account
                status TEXT NOT NULL DEFAULT 'Open',                -- ticket state
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, -- auto timestamp
                claimed_by TEXT                                     -- name of staff who claimed the ticket if there exists one
            )
            """
)

    # Create university accounts table if it does not already exist
    connection.execute(
      """
        CREATE TABLE IF NOT EXISTS UniversityAccount (
            id INTEGER PRIMARY KEY AUTOINCREMENT,      -- unique account ID
            email TEXT NOT NULL UNIQUE,                -- university email
            password_hash TEXT NOT NULL,               -- password hashed
            full_name TEXT NOT NULL,                   -- name of account owner
            role TEXT NOT NULL,                        -- student staff or manager
            department TEXT NOT NULL DEFAULT ''        -- IT Facilities or Academic Support
        )
       """
    )

    # Create ticket history table if it doesn't exist already
    # Each row records one visible ticket change for the detail page
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS ticket_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,                 -- unique history ID
            ticket_id INTEGER NOT NULL,                           -- ticket this event belongs to
            actor_account_id INTEGER,                             -- account that made the change
            change_type TEXT NOT NULL,                            -- created status_updated claimed etc
            old_value TEXT,                                       -- previous value when there is one
            new_value TEXT,                                       -- new value when there is one
            notes TEXT,                                           -- plain English description
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP    -- auto timestamp
        )
        """
    )

    # Add missing department column to UniversityAccount if it doesn't exist
    cursor = connection.execute("PRAGMA table_info(UniversityAccount)")
    columns = [row[1] for row in cursor.fetchall()]
    if "department" not in columns:
        connection.execute(
            "ALTER TABLE UniversityAccount ADD COLUMN department TEXT NOT NULL DEFAULT ''"
        )

    # Add missing claimed_by column to tickets if it doesn't exist
    cursor = connection.execute("PRAGMA table_info(tickets)")
    columns = [row[1] for row in cursor.fetchall()]
    if "claimed_by" not in columns:
        connection.execute(
            "ALTER TABLE tickets ADD COLUMN claimed_by TEXT DEFAULT ''"
        )

    connection.commit()


def connect_db():
    """Establish connection."""

    # Make sure the folder for the database exists. If it doesn't, create it
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)

    # This lets us access row values by column name instead of index.
    # Example: row["category"] instead of row[1]
    connection.row_factory = sqlite3.Row

    # Ensure the table exists before using the database
    _ensure_schema(connection)

    return connection


def save_ticket(ticket_data):
    """Save ticket."""

    # Open database connection
    connection = connect_db()

    try:
        # Insert ticket data into the database
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                title,
                category,
                description,
                attachment,
                requester_account_id,
                status,
                claimed_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_data["title"],                  # required
                ticket_data["category"],               # required
                ticket_data["description"],            # required
                ticket_data.get("attachment"),         # optional
                ticket_data.get("requester_account_id"),
                ticket_data.get("status", "Open"),  # default if missing
                ticket_data.get("claimed_by", "")
            ),
        )

        # Save the new ticket ID so the first history row can reference it
        ticket_id = cursor.lastrowid

        # Add the initial history row for ticket creation
        _insert_ticket_history(
            connection,
            ticket_id=ticket_id,
            actor_account_id=ticket_data.get("requester_account_id"),
            change_type="created",
            new_value=ticket_data.get("status", "Open"),
            notes="Ticket created.",
        )

        # Save changes
        connection.commit()

        # Return ID of the newly created ticket
        return ticket_id
    finally:
        # Always close database connection
        connection.close()


def update_ticket_attachment(ticket_id, attachment_ref):
    """Store the saved attachment reference for an existing ticket."""

    # Open database connection
    connection = connect_db()

    try:
        # Save the server-side attachment reference on the ticket row
        connection.execute(
            "UPDATE tickets SET attachment = ? WHERE id = ?",
            (attachment_ref, ticket_id),
        )
        # Save changes
        connection.commit()
    finally:
        # Always close database connection
        connection.close()


def get_ticket_count():
    """Return the current number of ticket rows."""

    connection = connect_db()

    try:
        cursor = connection.execute("SELECT COUNT(*) AS count FROM tickets")
        row = cursor.fetchone()
        return row["count"]
    finally:
        connection.close()


def get_university_account_by_email(email):
    """Retrieve university account by email address."""

    connection = connect_db()

    try:
        # Match email case-insensitively so submitted form values are flexible
        cursor = connection.execute(
            """
            SELECT id, email, password_hash, full_name, role, department
            FROM UniversityAccount
            WHERE lower(email) = lower(?)
            """,
            (email.strip(),),
        )

        return cursor.fetchone()
    finally:
        connection.close()


def get_university_account_by_id(account_id):
    """Retrieve university account by account ID."""

    connection = connect_db()

    try:
        cursor = connection.execute(
            """
            SELECT id, email, password_hash, full_name, role, department
            FROM UniversityAccount
            WHERE id = ?
            """,
            (account_id,),
        )
        return cursor.fetchone()
    finally:
        connection.close()

def get_staff_accounts_by_department(department):
    connection = connect_db()
    query = """
                SELECT full_name
                FROM UniversityAccount
                WHERE role == "staff"
                AND department = ?
            """

    params = (department,)
    accounts = connection.execute(query, params).fetchall()
    connection.close()

    return accounts

def save_university_account(account_data):
    """Save university account if it does not already exist."""

    connection = connect_db()
    query = """
            INSERT OR IGNORE INTO UniversityAccount
            (email, password_hash, full_name, role, department)
            VALUES (?, ?, ?, ?, ?)
            """
    
    params = [account_data["email"],
                account_data["password_hash"],
                account_data["full_name"],
                account_data["role"],
                account_data["department"]]
    try:
        # Insert account only when the email does not already exist
        # Using IGNORE for safer startup seeding
        connection.execute(query, params)

        query = """
                SELECT * FROM UniversityAccount
                """
        
        params = []

        accounts = connection.execute(query, params)
        for account in accounts:
            print(account["email"])
            print(account["password_hash"])

        connection.commit()


    finally:
        connection.close()


def update_ticket(ticket_id, status, claimed_by="", actor_account_id=None):
    """Update ticket."""
    try:
        connection = connect_db()

        # Load the current values before updating so history can show what changed
        ticket = connection.execute(
            "SELECT status, claimed_by FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()

        cursor = connection.execute("UPDATE tickets SET status = ?, claimed_by = ? WHERE id = ?",
                                    (status, claimed_by, ticket_id)
                                    )

        # Only create history rows for fields that actually changed
        if ticket is not None:
            if ticket["status"] != status:
                _insert_ticket_history(
                    connection,
                    ticket_id=ticket_id,
                    actor_account_id=actor_account_id,
                    change_type="status_updated",
                    old_value=ticket["status"],
                    new_value=status,
                    notes="Ticket status updated.",
                )
            if (ticket["claimed_by"] or "") != (claimed_by or ""):
                _insert_ticket_history(
                    connection,
                    ticket_id=ticket_id,
                    actor_account_id=actor_account_id,
                    change_type="assignment_updated",
                    old_value=ticket["claimed_by"] or "Unclaimed",
                    new_value=claimed_by or "Unclaimed",
                    notes="Ticket assignment updated.",
                )

        connection.commit()

        return cursor.fetchone()
    finally:
        connection.close()

def claim_ticket(ticket_id, staff_name, actor_account_id=None)-> None:
    """Claim Ticket"""
    print("Ticket ID: ", ticket_id)
    print("Staff Name: ", staff_name)
    try:
        connection = connect_db()

        # Load the previous owner so the claim history can show the change
        ticket = connection.execute(
            "SELECT claimed_by FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()

        cursor = connection.execute("UPDATE tickets SET claimed_by = ? WHERE id = ?", (staff_name, ticket_id))
        print(cursor.rowcount)

        # Record a claim only when the owner value is actually changing
        if ticket is not None and (ticket["claimed_by"] or "") != staff_name:
            _insert_ticket_history(
                connection,
                ticket_id=ticket_id,
                actor_account_id=actor_account_id,
                change_type="claimed",
                old_value=ticket["claimed_by"] or "Unclaimed",
                new_value=staff_name,
                notes="Ticket claimed.",
            )

        connection.commit()

    finally:
        connection.close()


def get_ticket(ticket_id,):
    """Retrieve ticket data."""

    try:
        connection = connect_db()

        cursor = connection.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,)
        )

        return cursor.fetchone()
    finally:
        connection.close()


def _insert_ticket_history(
    connection,
    ticket_id,
    actor_account_id,
    change_type,
    old_value=None,
    new_value=None,
    notes=None,
):
    # Internal helper that adds a history row using an existing database connection
    # Used when ticket changes and history logging should commit together
    connection.execute(
        """
        INSERT INTO ticket_history (
            ticket_id,
            actor_account_id,
            change_type,
            old_value,
            new_value,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (ticket_id, actor_account_id, change_type, old_value, new_value, notes),
    )


def add_ticket_history(ticket_id, actor_account_id, change_type, old_value=None, new_value=None, notes=None):
    # Public helper for adding a standalone ticket history row
    # Opens and commits its own database connection
    
    connection = connect_db()

    try:
        _insert_ticket_history(
            connection,
            ticket_id,
            actor_account_id,
            change_type,
            old_value,
            new_value,
            notes,
        )
        connection.commit()
    finally:
        connection.close()


def get_ticket_history(ticket_id):
    """Retrieve history rows for a ticket."""
    connection = connect_db()

    try:
        # Join to UniversityAccount so the page can show who made each change
        cursor = connection.execute(
            """
            SELECT
                ticket_history.id,
                ticket_history.ticket_id,
                ticket_history.actor_account_id,
                ticket_history.change_type,
                ticket_history.old_value,
                ticket_history.new_value,
                ticket_history.notes,
                ticket_history.created_at,
                UniversityAccount.full_name AS actor_name,
                UniversityAccount.email AS actor_email
            FROM ticket_history
            LEFT JOIN UniversityAccount
                ON ticket_history.actor_account_id = UniversityAccount.id
            WHERE ticket_history.ticket_id = ?
            ORDER BY ticket_history.id ASC
            """,
            (ticket_id,)
        )
        return cursor.fetchall()
    finally:
        connection.close()


def log_event(event_data):
    """Log system errors."""
