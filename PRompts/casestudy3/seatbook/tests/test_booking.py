"""Tests for seat availability and booking."""

import pytest

from src.booking.db import init_db, reset
from src.booking.fares import fare_for
from src.booking.seats import (
    SeatUnavailable,
    book_seat,
    bookings_for_seat,
    is_available,
)

TRIP = "TRIP-BLR-HYD-2140"


@pytest.fixture(autouse=True)
def clean_db(tmp_path):
    init_db(str(tmp_path / "test.db"))
    reset()
    yield
    reset()


def test_new_seat_is_available():
    assert is_available(TRIP, "L1") is True


def test_booking_returns_a_reference():
    ref = book_seat(TRIP, "L1", "Anita R")
    assert ref.startswith("BK")
    assert len(ref) == 12


def test_seat_is_unavailable_after_booking():
    book_seat(TRIP, "L2", "Anita R")
    assert is_available(TRIP, "L2") is False


def test_double_booking_is_rejected():
    book_seat(TRIP, "L3", "Anita R")
    with pytest.raises(SeatUnavailable):
        book_seat(TRIP, "L3", "Vikram S")


def test_different_seats_can_both_be_booked():
    book_seat(TRIP, "L5", "Anita R")
    book_seat(TRIP, "L6", "Vikram S")
    assert is_available(TRIP, "L5") is False
    assert is_available(TRIP, "L6") is False


def test_same_seat_on_another_trip_is_free():
    book_seat(TRIP, "L7", "Anita R")
    assert is_available("TRIP-BLR-CHN-2200", "L7") is True


def test_booking_row_records_the_passenger():
    book_seat(TRIP, "U1", "Meera K")
    rows = bookings_for_seat(TRIP, "U1")
    assert rows[0]["passenger"] == "Meera K"


def test_lower_berth_costs_more_than_seater():
    assert fare_for(TRIP, "L1") > fare_for(TRIP, "S1")


def test_unknown_seat_class_raises():
    with pytest.raises(ValueError):
        fare_for(TRIP, "X9")


def test_fare_is_recorded_on_the_booking():
    book_seat(TRIP, "U2", "Meera K")
    rows = bookings_for_seat(TRIP, "U2")
    assert rows[0]["fare"] > 0
