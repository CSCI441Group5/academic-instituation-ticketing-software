# Academic Institution Ticketing Software (2026S_CSCI441_VB Group 5)

## Project Overview

This project is a prototype ticketing system for an academic institution.
Students can submit support tickets, staff can manage tickets routed to their
department, and managers can oversee tickets across departments.

The system is being developed via an agile-based design.

## Quick Start

First-time setup (or when dependencies change):

- macOS / Linux: `./setup.sh`
- Windows (PowerShell): `.\setup.ps1`

Run the app:

- macOS / Linux: `./run.sh`
- Windows (PowerShell): `.\run.ps1`

## Current Features

- University account login for student, staff, and manager roles
- Student dashboard for viewing active submitted tickets
- Staff dashboard for viewing active tickets in the staff member's department
- Manager dashboard for viewing tickets across all departments
- Ticket submission with title, category, description, and optional image attachment
- Category-based routing, where submitted tickets appear in the matching department queue
- Ticket claiming and ticket status updates for support staff
- Manager ticket assignment controls
- Archive page for closed tickets
- Dashboard and archive filtering by status, category, and date
- Ticket detail page with ticket history/activity log
- Notification panel showing recent ticket updates
- Theme and font-size controls

## Technology

- Frontend: HTML, CSS, JavaScript, Jinja templates
- Backend: Python, Flask
- Database: SQLite
- Testing: pytest

## How to run the project

### 1. Clone the repository

```
git clone https://github.com/CSCI441Group5/academic-institution-ticketing-software.git
cd academic-institution-ticketing-software
```

### 2. Run setup script

**macOS / Linux**

```
./setup.sh
```

**Windows (PowerShell)**

```
.\setup.ps1
```

This creates `.venv` (if missing) and installs dependencies.

### 3. Run the application

**macOS / Linux**

```
./run.sh
```

**Windows (PowerShell)**

```
.\run.ps1
```

### 4. Open in your browser

```
http://127.0.0.1:5000
```

## Manual setup (alternative)

### 1. Create and activate a virtual environment

**macOS / Linux**

```
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```
python -m venv .venv
.venv\Scripts\Activate
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Run the application

```
python run.py
```

If outside the virtual environment:

```
python3 run.py
```

### 4. Open in your browser

```
http://127.0.0.1:5000
```

## Running Tests

After setup, run the automated test suite with:

**macOS / Linux**

```
./test.sh -q
```

Or run pytest directly from the virtual environment:

```
.venv/bin/python -m pytest -q
```

## Troubleshooting

**“command not found: run.sh”**

```
./run.sh
```

**“command not found: python”**

```
./setup.sh
```

**Flask not found**

```
source .venv/bin/activate
```
