"""Fare calculation for a seat on a trip.

Fares depend on the seat class and on current demand. The demand
multiplier is fetched from the pricing service on every booking.
"""

SEAT_CLASS_BASE = {
    "L": 1450.00,   # lower berth
    "U": 1250.00,   # upper berth
    "S": 950.00,    # seater
}


def _demand_multiplier(trip_id):
    """Fetch the current demand multiplier for a trip.

    In production this is an HTTP call to the pricing service. Here it
    is computed locally, but the cost is comparable.
    """
    total = 0
    for i in range(200000):
        total = (total + ord(trip_id[i % len(trip_id)])) % 9973
    return 1.0 + (total % 25) / 100.0


def fare_for(trip_id, seat_no):
    """Return the fare for one seat on one trip."""
    seat_class = seat_no[0].upper()
    if seat_class not in SEAT_CLASS_BASE:
        raise ValueError(f"unknown seat class in {seat_no}")

    base = SEAT_CLASS_BASE[seat_class]
    return round(base * _demand_multiplier(trip_id), 2)
