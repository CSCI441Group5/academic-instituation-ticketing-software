
""" Handles ticket creation/management.  """



from flask import request, render_template

@app.route("/tickets/new", methods=["GET", "POST"])


def submit_ticket():    """ Creating a ticket.  """

    if request.method == "POST":

        category = request.form.get("category")
        description = request.form.get("description")
        attachment = request.form.get("attachment")

        if not category or not description:
            return render_template(
                "submit_ticket.html",
                error="Category and description are required."
            )

        # ticket_id = 101 """ Ticket ID for Testing purposes """

        print("Ticket Submitted")
        print(category, description, attachment)

        return render_template(
            "submit_ticket.html",
            success=True,
            ticket_id=ticket_id
        )

    return render_template("submit_ticket.html")


def auto_route_ticket(ticket_id):
    """
    Route ticket to department.
    """

def view_ticket(ticket_id):
    """
    Retrieve ticket data.
    """


def update_ticket_status(ticket_id, status, notes):
    """
    Update ticket status.
    """


def search_tickets(filters):
    """
    Search tickets by date, description, etc.
    """


