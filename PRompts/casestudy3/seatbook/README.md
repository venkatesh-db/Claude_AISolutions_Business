# seat-inventory

Seat availability and booking for intercity bus trips.

## What it does

Holds the seat inventory for every trip. A seat is available when no
booking row exists for that trip and seat number. Booking creates the
row, prices the seat against the pricing service, and returns a booking
reference to the payment flow.

Runs behind the WSGI worker pool. Each request opens its own database
connection.

## Layout

```
src/booking/seats.py          availability and booking
src/booking/fares.py          seat pricing
src/booking/db.py             connections and schema
tests/test_booking.py         unit tests
fixtures/concurrent_book.py   sends parallel booking requests
evidence/                     support escalations
```

## Running

```bash
python3 -m pytest -q
python3 fixtures/concurrent_book.py
```

## Open escalation

Support has raised ten cases since 4 August where more than one
passenger holds a confirmed ticket for the same seat. All on evening
departures that sold out quickly. Support cannot reproduce it manually.

See `evidence/support-escalations-2026-08-15.md`.

## Contacts

Owner: Inventory Engineering
Escalation: #bookings-oncall
