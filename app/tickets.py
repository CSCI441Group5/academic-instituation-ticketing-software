"""
Handles ticket creation/management.
"""
from datetime import datetime
import app.database


def submit_ticket(category, description, attachment=None):
    """
    Create a ticket.
    """


def auto_route_ticket(ticket_id):
    """
    Route ticket to department.
    """


def view_ticket(ticket_id):
    """
    Retrieve ticket data.
    """


def update_ticket_status(ticket_id: int, status: str, notes: str):
    """
    Update ticket status.
    """

    ticket = app.database.update_ticket(status, ticket_id)
    return ticket


def search_tickets(tickets, filters):
    """
    Search tickets by date, description, etc.
    """
    status_filter = filters[0]
    category_filter = filters[1]
    before_date = filters[2]
    after_date = filters[3]
    filtered = tickets

    if status_filter != "":
        filtered = [t for t in filtered if t["status"] == status_filter]
    else:
        print(f"Status Filter: {status_filter}")

    if category_filter != "":
        filtered = [t for t in filtered if t["category"]
                    == category_filter]
    else:
        print(f"Category Filter: {category_filter}")

    if before_date != "":
        cutoff = datetime.strptime(before_date, "%Y-%m-%d").date()
        filtered = [t for t in filtered
                    if datetime.strptime(t["created_at"], "%Y-%m-%d %H:%M:%S").date() < cutoff]

    if after_date != "":
        cutoff = datetime.strptime(after_date, "%Y-%m-%d").date()
        filtered = [t for t in filtered
                    if datetime.strptime(t["created_at"], "%Y-%m-%d %H:%M:%S").date() > cutoff]

    return filtered
