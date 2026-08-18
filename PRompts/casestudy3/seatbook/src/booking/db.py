"""SQLite access for the seat inventory service.

Each request opens its own connection, matching how the service runs
behind the WSGI worker pool in production.
"""

import os
import sqlite3

DB_PATH = os.environ.get("SEATBOOK_DB", "seatbook.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS bookings (
    booking_ref  TEXT PRIMARY KEY,
    trip_id      TEXT NOT NULL,
    seat_no      TEXT NOT NULL,
    passenger    TEXT NOT NULL,
    fare         REAL NOT NULL,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trips (
    trip_id      TEXT PRIMARY KEY,
    operator     TEXT NOT NULL,
    route        TEXT NOT NULL,
    total_seats  INTEGER NOT NULL
);
"""


def connect():
    """Open a connection for one request."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path=None):
    """Create the schema and seed one trip."""
    global DB_PATH
    if path:
        DB_PATH = path

    conn = connect()
    conn.executescript(SCHEMA)
    conn.execute(
        "INSERT OR REPLACE INTO trips VALUES (?, ?, ?, ?)",
        ("TRIP-BLR-HYD-2140", "Orange Travels", "Bengaluru - Hyderabad", 36),
    )
    conn.commit()
    conn.close()


def reset():
    """Clear all bookings. Used by tests and the fixture generator."""
    conn = connect()
    conn.execute("DELETE FROM bookings")
    conn.commit()
    conn.close()
