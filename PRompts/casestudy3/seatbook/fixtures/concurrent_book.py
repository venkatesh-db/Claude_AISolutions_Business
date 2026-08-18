"""Reproduce the double booking by sending concurrent requests.

Usage:
    python3 fixtures/concurrent_book.py
    python3 fixtures/concurrent_book.py 20
"""

import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.booking.db import init_db, reset  # noqa: E402
from src.booking.seats import (  # noqa: E402
    SeatUnavailable,
    book_seat,
    bookings_for_seat,
)

TRIP = "TRIP-BLR-HYD-2140"
SEAT = "L4"


def main():
    threads_count = int(sys.argv[1]) if len(sys.argv) > 1 else 12

    init_db()
    reset()

    results = []
    lock = threading.Lock()

    def attempt(n):
        try:
            ref = book_seat(TRIP, SEAT, f"passenger-{n}")
            with lock:
                results.append(("booked", ref))
        except SeatUnavailable:
            with lock:
                results.append(("rejected", None))

    threads = [threading.Thread(target=attempt, args=(i,))
               for i in range(threads_count)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    booked = [r for r in results if r[0] == "booked"]
    rejected = [r for r in results if r[0] == "rejected"]
    rows = bookings_for_seat(TRIP, SEAT)

    print(f"trip                 : {TRIP}")
    print(f"seat                 : {SEAT}")
    print(f"concurrent requests  : {threads_count}")
    print(f"accepted by the API  : {len(booked)}")
    print(f"rejected by the API  : {len(rejected)}")
    print(f"rows in bookings     : {len(rows)}")
    print()

    for r in rows:
        print(f"  {r['booking_ref']}  {r['seat_no']}  {r['passenger']:<14} "
              f"{r['fare']:>9.2f}")

    print()
    if len(rows) > 1:
        print(f"FAIL - one seat sold {len(rows)} times")
    else:
        print("PASS - one seat, one booking")


if __name__ == "__main__":
    main()
