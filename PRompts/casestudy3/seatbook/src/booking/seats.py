"""Seat availability and booking.

A seat is available when no booking row exists for that trip and seat
number. Booking creates the row and returns the booking reference.
"""

import uuid
from datetime import datetime

from src.booking.db import connect
from src.booking.fares import fare_for


class SeatUnavailable(Exception):
    """Raised when the requested seat is already booked."""


def is_available(trip_id, seat_no):
    """Return True if the seat has no booking on this trip."""
    conn = connect()
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM bookings WHERE trip_id = ? AND seat_no = ?",
        (trip_id, seat_no),
    ).fetchone()
    conn.close()
    return row["n"] == 0


def book_seat(trip_id, seat_no, passenger):
    """Book one seat for one passenger.

    Args:
        trip_id: the trip being booked
        seat_no: seat number, e.g. "L4" or "U11"
        passenger: passenger name on the ticket

    Returns:
        The booking reference.

    Raises:
        SeatUnavailable: if the seat is already booked.
    """
    if not is_available(trip_id, seat_no):
        raise SeatUnavailable(f"seat {seat_no} is already booked on {trip_id}")

    fare = fare_for(trip_id, seat_no)

    booking_ref = "BK" + uuid.uuid4().hex[:10].upper()

    conn = connect()
    conn.execute(
        "INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?)",
        (
            booking_ref,
            trip_id,
            seat_no,
            passenger,
            fare,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()

    return booking_ref


def bookings_for_seat(trip_id, seat_no):
    """Return every booking row for one seat. Used by support tooling."""
    conn = connect()
    rows = conn.execute(
        "SELECT * FROM bookings WHERE trip_id = ? AND seat_no = ? "
        "ORDER BY created_at",
        (trip_id, seat_no),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
