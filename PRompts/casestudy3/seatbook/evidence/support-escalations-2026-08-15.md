# Support escalations — seat allocation
**Queue:** L2 Bookings · **Compiled:** 2026-08-15 · **Compiled by:** Support Ops

Escalated to engineering. Ten cases in eleven days, all the same shape:
more than one passenger holding a valid ticket for the same seat on the
same trip. Every affected passenger has a confirmed booking reference
and a successful payment.

Operators are resolving these at the boarding point. Two passengers
have been refused travel.

---

### ESC-88214 · 2026-08-04 · Orange Travels · TRIP-BLR-HYD-2140 · seat L4

Two passengers boarded with confirmed tickets for L4. Conductor asked
the second to stand. Passenger refused travel and demanded a refund at
the boarding point. Refund issued, goodwill voucher issued.

Booking refs: BK7A2E19C044, BK03D1FF8B7E
Both created 2026-08-04, timestamps within the same second.

---

### ESC-88301 · 2026-08-06 · VRL · TRIP-BLR-PNQ-2115 · seat U9

Three confirmed bookings for one upper berth. Two passengers
accommodated in a later service. One did not travel.

Booking refs: BKB81C7D2A55, BK4E9033FC17, BK1D77A0E8B2
All three created within two seconds of each other.

---

### ESC-88355 · 2026-08-07 · SRS · TRIP-HYD-BLR-2230 · seat L11

Two bookings. Operator noticed at manifest print, before boarding.
Second passenger moved to L14 without customer contact.

Booking refs: BK52C1AA0396, BKE07B4D1188

---

### ESC-88402 · 2026-08-09 · Orange Travels · TRIP-BLR-HYD-2140 · seat L4

Same trip and seat as ESC-88214. Two bookings again.

Booking refs: BK9F30E27C6A, BK22B58D01E4

---

## Pattern noted by Support Ops

Support has no access to application logs, but from the booking
records alone:

- Every case is on a **high-demand evening departure** (21:00–22:30)
- The duplicate booking references are always created **within a few
  seconds of each other**
- Affected trips are consistently ones that **sold out within minutes**
- No case has been reproduced by a support agent booking manually
- Between 2 and 3 duplicates per affected seat

Support cannot reproduce this on demand and has no further diagnostic
access. Handing to engineering.

## What engineering has been asked for

1. Whether the duplicate bookings can be prevented at source
2. Whether existing duplicate rows can be identified across all trips
3. Whether refunds already issued were correct

Contact: #bookings-oncall
