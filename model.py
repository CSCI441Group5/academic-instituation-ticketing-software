"""
System models.
"""

class User:
    def __init__(self, email, role):
        self.email = email
        self.role = role

class Ticket:
    def __init__(self, ticket_id, category, description, status):
        self.ticket_id = ticket_id
        self.category = category
        self.description = description
        self.status = status
