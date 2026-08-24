# International Smile — Remaining Screens, Filled-In Prompts

Five filled-in prompts, one per remaining screen, each built from
`MASTER_PROMPT.md`'s 9-step engine. Run them **one at a time, in order**
— each depends on state the previous one creates (a fare snapshot needs
to exist before a seat can lock against it; a seat lock needs to exist
before checkout can reference it). Do not run two in parallel.

Copy one block at a time, paste to Claude, let it run to completion
(through step 8, or step 9 if you want the self-review), before starting
the next.

---

## Screen 1: Select Flight (fare-snapshot lock)

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit, pip-audit.

We work in single verified vertical slices, never big-bang generation.
One slice per pass. Do not touch screens/endpoints outside the named
scope. Do not claim a step is done without showing the real command
output that proves it.

1. READ FIRST. Read Day4/backend/app/api/routes_search.py and
   Day4/backend/app/schemas/search.py (the existing FlightOption shape
   this slice extends) and stitch_modern_irctc_redesign/select_flight/
   code.html in full. State what you found: the 3 fare-tier tiles
   (Economy/Flex/Premium in the mock; SAVER/FLEXI PLUS/SUPER 6E already
   used in Search results), the conflicting progress-stepper labels
   noted in DOMAIN_KNOWLEDGE.md §2.3.

2. REFERENCE CHECK (5 min max). Not required this pass — fare-tier
   naming and pricing shape were already [Observed] on IndiGo during the
   Search Flights slice. Skip re-verification unless something here
   looks materially different from what Search already confirmed.

3. DOMAIN_KNOWLEDGE.md: extend with the fare-lock contract. Every new
   field tagged [Observed]/[Stitch]/[Inferred] as usual. Specifically:
   - Request: which flight_number + fare_tier the user selected
   - Response: a `fare_snapshot_id` (UUID) + `locked_until` timestamp
   - The lock itself lives in Redis, TTL matches
     `inventory_lock_ttl_seconds` from the original requirement doc §5
     (10 min) — implement this now, it's the first slice that needs it
   - Price-drift rule: if the same flight/fare is re-selected after the
     snapshot's price would differ from a fresh Search result, that's a
     FUTURE checkout-time concern (§2.2 in the original requirement doc,
     "fare changed on payment") — NOT this slice's job to detect, just
     don't let this slice's design make that detection harder later

4. TEST FIRST (RED). Write tests for a `POST /flights/{flight_number}/lock`
   route: request body = fare_tier, response = fare_snapshot_id +
   locked_until. Also test that a second lock request for the same
   flight+tier by a different (simulated) caller does NOT fail — multiple
   users can independently snapshot the same public fare, this is not a
   scarce-resource lock like a seat. Run tests, confirm real failure.

5. IMPLEMENT (GREEN). Redis-backed snapshot: key `fare_snapshot:{uuid}`,
   value = flight_number + fare_tier + price + locked_until, TTL 600s.
   Minimal FastAPI route. Re-run tests, show real passing output.

6. GATES: ruff, mypy --strict, pip-audit if new deps added. Show output.

7. LIVE RUN: reuse the running Postgres/Redis containers (confirm with
   `docker ps` first). Real browser: navigate select_flight (built this
   pass, adapted from the Stitch mock, rebranded International Smile),
   click a fare tile, confirm the real network request, confirm the
   fare_snapshot key actually exists in Redis via `redis-cli` (not just
   the UI response).

8. REVIEW.md: real RED/GREEN/gate/live output, explicit "what this does
   NOT cover" — no price-drift detection yet (that's Checkout's job), no
   multi-passenger fare splitting.

Stop after step 8.

Slice for this pass: Flight selection + fare-snapshot lock
Scope: POST /flights/{flight_number}/lock route, Redis fare_snapshot key,
select_flight.html frontend
Folder: Day4/
Prior findings to close first: none outstanding
```

---

## Screen 2: Select Seat (seat lock — highest concurrency risk)

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit, pip-audit.

We work in single verified vertical slices, never big-bang generation.
One slice per pass. Do not touch screens/endpoints outside the named
scope. Do not claim a step is done without showing the real command
output that proves it.

1. READ FIRST. Read stitch_modern_irctc_redesign/select_seat/code.html
   in full (seat map states: premium/extra-legroom/standard/occupied,
   the "Confirm Seat 12A" CTA that hardcodes the seat number as static
   text — DOMAIN_KNOWLEDGE.md §3.4). Read whatever fare-snapshot code
   exists from the previous slice — a seat lock must reference a real
   `fare_snapshot_id`, not float free.

2. REFERENCE CHECK: not required — seat-map UX pattern already covered
   by the Stitch mock reading. Skip.

3. DOMAIN_KNOWLEDGE.md: this is the highest concurrency-risk slice built
   so far — TWO users tapping the same seat within the same second is a
   real, expected scenario, not an edge case. Document the lock contract:
   - `POST /flights/{flight_number}/seats/{seat}/lock` — request includes
     the `fare_snapshot_id` from Screen 1
   - Redis key `seat_lock:{flight_number}:{seat}`, TTL 600s
     (inventory_lock_ttl_seconds, matches the original requirement §5)
   - MUST be an atomic Redis SET...NX (set-if-not-exists), not a
     GET-then-SET pattern — a GET-then-SET here is the exact same
     check-then-act race class already found and fixed in the user-
     creation bug (Prompt8). Do not repeat that mistake with a seat
     instead of a phone number.

4. TEST FIRST (RED). Write a test that runs two concurrent lock requests
   for the SAME seat (via asyncio.gather against the real route, same
   pattern as test_auth_service_race.py) and asserts exactly ONE succeeds
   (200) and the other gets a real 409 Conflict — not both succeeding,
   not both failing. Run it, confirm real failure output against the
   not-yet-implemented route.

5. IMPLEMENT (GREEN). Use Redis `SET key value NX EX 600` — atomic by
   construction, no separate check step. Return 409 if the SET returns
   falsy (key already existed). Re-run the concurrency test, show real
   passing output — this is the proof that matters most for this slice.

6. GATES: ruff, mypy --strict, bandit, pip-audit. Show output.

7. LIVE RUN: real browser, real seat-map click, confirm via `redis-cli`
   that the lock key actually exists with the right TTL. Then, in a
   second real browser tab/session, try to lock the SAME seat and
   confirm a real 409 is returned and shown to the user — not silently
   swallowed.

8. REVIEW.md: real output including the concurrency test result. State
   explicitly what happens when the lock expires mid-checkout (should
   this slice handle expiry gracefully in the UI, or is that Checkout's
   job? — answer this, don't leave it implicit).

Stop after step 8.

Slice for this pass: Seat selection + atomic seat lock
Scope: POST /flights/{flight_number}/seats/{seat}/lock route, Redis
seat_lock key (SET NX EX only, no check-then-act), select_seat.html
frontend
Folder: Day4/
Prior findings to close first: none outstanding
```

---

## Screen 3: Add-ons

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit, pip-audit.

We work in single verified vertical slices, never big-bang generation.
One slice per pass. Do not touch screens/endpoints outside the named
scope. Do not claim a step is done without showing the real command
output that proves it.

1. READ FIRST. Read stitch_modern_irctc_redesign/add_ons/code.html in
   full. Note the DOMAIN_KNOWLEDGE.md §3.5/§5 flag: the mock has
   INCONSISTENT CTA patterns across its three sections (meals use
   "Add to Trip" buttons, baggage uses a `+` quantity stepper, perks use
   a mix) — pick ONE consistent interaction pattern for this build
   (recommend: all items are toggle-add, baggage additionally supports
   quantity 1-3), state which you picked and why, don't silently carry
   the mock's inconsistency forward.

2. REFERENCE CHECK: not required — this is the lowest domain-risk
   remaining screen, no real-product ambiguity to resolve. Skip.

3. DOMAIN_KNOWLEDGE.md: document the add-on contract:
   - `PATCH /bookings/{fare_snapshot_id}/addons` — idempotent: sending
     the same add-on selection twice must not double-add or double-charge
   - Each add-on: sku, name, price — a small fixed catalog is fine for
     this slice (meals, checked bag, lounge, priority boarding), no live
     inventory system needed
   - Running total must be computed server-side and returned in the
     response — the Stitch mock's sidebar total is static and does NOT
     react to clicks (a confirmed defect, §3.5) — do not repeat that,
     the frontend must re-render the total from the real server response
     after every add/remove, not compute it client-side

4. TEST FIRST (RED). Test the PATCH route: adding an add-on returns the
   updated total; adding the same add-on twice (idempotency key or
   natural idempotent PATCH semantics — your choice, state which) does
   not double the price; removing a non-added item is a no-op, not an
   error. Run tests, confirm real failure output.

5. IMPLEMENT (GREEN). Minimal route + in-memory-per-fare-snapshot (Redis
   hash keyed off fare_snapshot_id, same TTL family as the fare lock) add-
   on state. Re-run tests, show real passing output.

6. GATES: ruff, mypy --strict, pip-audit. Show output.

7. LIVE RUN: real browser, add 2 add-ons, confirm the total updates from
   the real server response (not a client-side guess), refresh the page
   and confirm the selections persist (read from the Redis hash, not
   lost on reload).

8. REVIEW.md: real output, explicit note on which CTA pattern was chosen
   and why, and confirm the "sidebar total goes stale" defect from the
   Stitch mock was NOT carried forward.

Stop after step 8.

Slice for this pass: Add-ons selection with server-computed running total
Scope: PATCH /bookings/{fare_snapshot_id}/addons route, Redis add-on
state, add_ons.html frontend
Folder: Day4/
Prior findings to close first: none outstanding
```

---

## Screen 4: Checkout / Payment

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit, pip-audit.

We work in single verified vertical slices, never big-bang generation.
One slice per pass. Do not touch screens/endpoints outside the named
scope. Do not claim a step is done without showing the real command
output that proves it.

1. READ FIRST. Read stitch_modern_irctc_redesign/checkout/code.html in
   full — the boarding-pass-style summary card, the fare breakdown, the
   payment-method radio (Apple Pay pre-selected, Credit Card has NO
   entry fields in the mock — DOMAIN_KNOWLEDGE.md §3.6), and the hidden
   `id="success-message"` stub (§3.6/§4) that is the only design
   precedent for Order Success. Read the fare-snapshot, seat-lock, and
   add-on state from the previous 3 slices — this route reads all of it.

2. REFERENCE CHECK: CANNOT be completed live this pass. Browser-driving a
   real payment flow on goindigo.in or any live OTA is not ethical or
   practical (would require real payment credentials / a real
   transaction). State this explicitly rather than skipping silently.
   Rely on [Inferred] patterns already documented in the ORIGINAL domain
   requirement doc §2.2 (payment state machine: PAYMENT_PENDING →
   CONFIRMED / PAYMENT_FAILED / RECONCILING) — these are standard
   industry patterns, not verified live, and must stay tagged [Inferred].

3. DOMAIN_KNOWLEDGE.md: document the checkout contract:
   - `POST /checkout/{fare_snapshot_id}/initiate` — re-validates the fare
     snapshot and seat lock haven't expired (real check against Redis TTL,
     not assumed), returns a mock `payment_intent` (client_secret-style
     placeholder — NO real payment gateway integration in this slice,
     state this as an explicit scope boundary)
   - `POST /webhooks/payment` — simulated webhook endpoint for this slice
     (you will call it yourself in the live-run step to simulate a
     gateway callback, since there's no real gateway) — MUST be
     idempotent: the same webhook payload (same gateway_txn_id) processed
     twice must not double-confirm or double-write
   - CRITICAL: the fare/seat lock TTLs from Screens 1-2 might have
     expired by the time checkout is initiated — this slice MUST check
     that explicitly and return a real 410 Gone if so, not silently
     proceed with stale state

4. TEST FIRST (RED). Tests for: successful initiate + webhook confirm →
   booking state CONFIRMED; expired fare snapshot at initiate time → 410;
   duplicate webhook delivery (same gateway_txn_id twice) → second call
   is a no-op, not a double-write (check this at the DB level in the
   test, not just the HTTP response). Run tests, confirm real failure.

5. IMPLEMENT (GREEN). Minimal route + webhook handler with an
   idempotency-key unique constraint on the payment record (DB-level,
   not just application-level — same lesson as the phone-uniqueness fix
   in Prompt8). Re-run tests, show real passing output.

6. GATES: ruff, mypy --strict, bandit (mandatory — payment-adjacent),
   pip-audit. Show output.

7. LIVE RUN: real browser through checkout.html (built this pass,
   rebranded, reusing the boarding-pass card styling), click Confirm &
   Pay, then YOU manually call the webhook endpoint via curl to simulate
   the gateway callback (state clearly that this is a simulated callback,
   not a real gateway), confirm the booking's real DB row transitions to
   CONFIRMED. Then curl the SAME webhook payload a second time and prove
   via a DB query that nothing double-wrote.

8. REVIEW.md: real output. Explicit, prominent "what this does NOT
   cover": no real payment gateway, no real card handling (correctly, per
   the original requirement doc's PCI-DSS note — card data must never
   touch this backend directly, only a tokenization reference would in a
   real integration), the RECONCILING/refund path from the original state
   machine is NOT implemented this pass, only documented as a future gap.

Stop after step 8. Do not implement Order Success in this pass even
though it's tempting — that's Screen 5.

Slice for this pass: Checkout initiate + simulated payment webhook
(idempotent)
Scope: POST /checkout/{fare_snapshot_id}/initiate, POST /webhooks/payment
(simulated), checkout.html frontend
Folder: Day4/
Prior findings to close first: none outstanding
```

---

## Screen 5: Order Success

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit, pip-audit.

We work in single verified vertical slices, never big-bang generation.
One slice per pass. Do not touch screens/endpoints outside the named
scope. Do not claim a step is done without showing the real command
output that proves it.

1. READ FIRST. There is almost nothing to read here — this is the one
   screen with NO real design precedent. The only artifact evidence is
   the hidden `id="success-message"` stub in checkout/code.html
   (DOMAIN_KNOWLEDGE.md §4): an icon + "Your journey with {brand}
   begins." on the SAME page as checkout, not a separate screen. State
   explicitly that this slice is closer to greenfield design than any
   prior slice, and that the brand-corrected copy is "International
   Smile," not the stub's original "Avia Luxe."

2. REFERENCE CHECK: skip — no live product comparison adds value for a
   confirmation/polling screen; the pattern (poll while issuing, then
   show PNR/ticket) is standard and already specified in the ORIGINAL
   requirement doc §3.10 (GET /bookings/{id}/order).

3. DOMAIN_KNOWLEDGE.md: document:
   - `GET /bookings/{fare_snapshot_id}/order` — while the (simulated,
     from Screen 4) issuance is still pending, returns 202 with
     `{"state": "ISSUING", "poll_after_ms": 2000}`; once issued, returns
     200 with PNR, flight summary, travelers, total paid
   - For this slice, "issuing" can be simulated with a short fixed delay
     (e.g. a Celery task that flips state after 3 seconds) rather than a
     real supplier integration — state this as an explicit scope boundary
   - The frontend MUST implement real polling (setTimeout loop honoring
     poll_after_ms), not a fixed single fetch — this is the one new UI
     interaction pattern this slice introduces that no prior slice needed

4. TEST FIRST (RED). Test: immediately after checkout confirms, GET
   /order returns 202 ISSUING; after the simulated delay, GET /order
   returns 200 with a real PNR (format: 6 alphanumeric chars, matching
   the IndiGo PNR pattern already [Observed] and logged in the earlier
   sample-data pass of this session). Run tests, confirm real failure.

5. IMPLEMENT (GREEN). Minimal route + Celery task (or a simple
   time-based check against a stored "confirmed_at + 3s" if Celery adds
   too much setup cost for this slice — state which you chose and why).
   Re-run tests, show real passing output.

6. GATES: ruff, mypy --strict, pip-audit. Show output.

7. LIVE RUN: real browser through the full funnel — login, search, select
   flight, select seat, add-ons, checkout, confirm — land on Order
   Success while it's still polling (screenshot the ISSUING state, don't
   skip past it), then screenshot the final PNR state once polling
   resolves. This is the first slice where the FULL funnel gets run
   start to finish in one live pass — treat that as the actual milestone
   it is.

8. REVIEW.md: real output including both polling states screenshotted.
   Explicit "what this does NOT cover": no real e-ticket/invoice PDF
   generation, no real email/SMS notification dispatch (Kafka event
   `order.order.issued` from the original requirement doc §4.4 is not
   wired to a real consumer in this pass), no RECONCILING/refund path.

Stop after step 8. This completes the full Login → Order Success funnel
at the "thin slice, mocked integrations" level — say so explicitly, and
say explicitly what would be needed to take it from here to production
(real GDS, real payment gateway, real notification dispatch).

Slice for this pass: Order Success with real issuance polling
Scope: GET /bookings/{fare_snapshot_id}/order route, simulated async
issuance, order_success.html frontend
Folder: Day4/
Prior findings to close first: none outstanding
```

---

## Notes for whoever runs these

- **Run in order.** Each slice's live-run step reads real state a prior
  slice created (fare snapshot → seat lock → add-ons → checkout →
  order). Running out of order means faking upstream state, which
  defeats the "real, not simulated" principle this whole process is
  built on.
- **Update `MASTER_PROMPT.md`'s step 9 checklist after each of these
  runs**, per the standing guidance already given: the seat-lock slice
  will likely surface a new defect class (lock-expiry-mid-request), the
  checkout slice will likely surface webhook-idempotency lessons beyond
  what's already anticipated here. Fold each one forward, don't let the
  checklist go stale.
- **Screen 4 (Checkout) and Screen 5 (Order Success) both explicitly cap
  or skip the live reference-check step**, unlike Login/Search — this is
  a deliberate, stated deviation from the earlier pattern, not an
  oversight. Real payment flows and real issuance/notification systems
  are out of ethical/practical reach for a live browser check in this
  environment.
