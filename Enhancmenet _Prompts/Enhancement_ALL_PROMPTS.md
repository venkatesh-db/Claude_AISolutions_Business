# International Smile — All 10 Prompts (compiled)

Chronological record of every prompt used this session, in the order
they were run. Status is marked per prompt — some are executed with real
proof on disk, some are still drafted/unexecuted. Don't assume execution
from presence in this file alone; check the linked REVIEW file.

---

## Prompt1 — Initial requirement framing

**Status: informational, no code.**

```
Role- Principal architect,
Task role -full stack engineer,
domain -travel,
Feature - Login - Order success,
UI/ux- Refer .zip file,
domainknowledge- learn from goibio, makemytrip, skytravel

Techstack-python Layer
Technology
API
FastAPI, Pydantic v2
Domain
Plain Python service layer
Data
PostgreSQL, SQLAlchemy 2.x, Alembic
Cache and locks
Redis
Async work
Celery workers
Events
Kafka (Redpanda locally)
Analytics
pandas / Polars ETL
Testing
pytest, pytest-asyncio, hypothesis, testcontainers, locust
Quality gates
ruff, mypy --strict, bandit, pip-audit
Ops
Docker Compose, GitHub Actions, OpenTelemetry

Question to you- domain knowledge of the product scenario are u well versed
Task1- i need you understand this requirement clearly with domain expert 10 years and
role - full stack engineer (dont need prompt but confirmation)
```

---

## Prompt2 — Focus scope

**Status: informational, no code.**

```
first learn for zip file and focus on only travel domain requirement
```

---

## Prompt3 — Generic vertical-slice template

**Status: template, reused as the basis for Prompts 4, 6, 8, 9, 10.**
Saved separately as [SLICE_PROMPT_TEMPLATE.md](SLICE_PROMPT_TEMPLATE.md).

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit.

We work in single verified vertical slices, never big-bang generation.
Methodology for this slice, follow it exactly, in order:

1. REFERENCE CHECK (5 min max): before writing any contract, verify the
   real field/behavior for <SLICE_NAME> against a live reference product
   (IndiGo at goindigo.in, or MakeMyTrip/Goibibo if IndiGo doesn't cover
   it). Use the browser tool. Do not rely on memorized/trained knowledge
   of these products — observe the live page directly.

2. DOMAIN_KNOWLEDGE.md: write or extend the domain doc for this slice.
   Every field/rule must be tagged with its evidence source:
   - [Observed] — captured live from a real product this session, cite
     the exact element/text seen.
   - [Stitch] — from our UI mockup (stitch_modern_irctc_redesign/), cite
     file:line.
   - [Inferred] — standard domain pattern, not verified live. Must be
     labeled, never presented as fact.
   If the reference product's behavior conflicts with the Stitch mock,
   log it as an open conflict, do not silently pick one.

3. TEST FIRST (RED): write the pytest test file for <SLICE_NAME> before
   any implementation exists. Run it. Confirm it fails
   (ModuleNotFoundError or equivalent). Show me the actual failing output.

4. IMPLEMENT (GREEN): write the minimal Pydantic v2 model / FastAPI route
   / service function needed to make the tests in step 3 pass. Nothing
   more — no speculative fields, no unused abstractions. Run the tests
   again, show me the actual passing output.

5. GATES: run ruff, mypy --strict (and bandit if the slice touches
   auth/payment/PII). Fix every real finding — do not suppress or ignore.
   Show me the actual command output, before and after any fix.

6. REVIEW.md: write/append a review log for this slice with the real
   RED output, real GREEN output, real gate output, and an explicit list
   of what this slice does NOT cover yet (don't let one slice get
   reported as "the feature is done").

Stop after step 6. Do not start the next slice, do not touch other
screens/endpoints, until I say go.

Slice for this pass: <SLICE_NAME>
Scope: <ONE ENDPOINT / ONE MODEL / ONE SCREEN'S INPUT CONTRACT — name it>
Folder: <e.g. Day5/, or the real project path>
```

**Fill-in guide, why it exists, and a worked example** are documented in
the standalone file — see [SLICE_PROMPT_TEMPLATE.md](SLICE_PROMPT_TEMPLATE.md).

---

## Prompt4 — Login frontend-backend integration (design pass)

**Status: superseded by Prompt6's live execution.** This is the design/
contract pass; Prompt6 is what actually ran it live.
Saved separately as [PROMPT_login_frontend_backend.md](PROMPT_login_frontend_backend.md).

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit.

We work in single verified vertical slices, never big-bang generation.
Methodology for this slice, follow it exactly, in order:

1. READ BOTH SIDES FIRST. Read the existing frontend markup at
   stitch_modern_irctc_redesign/login/code.html in full before touching
   anything. Confirm what actually exists: the Apple/Google buttons
   (currently no handler), the mobile-number input with a hardcoded "+1"
   prefix, the "Send One-Time Code" button (currently type="button", no
   JS wired, no OTP-entry step exists at all). Read the existing backend
   login/OTP code that's already been built. Do not assume either side's
   shape — confirm both by reading, and tell me what you found before
   proceeding.

2. REFERENCE CHECK (5 min max): verify live on goindigo.in (or
   MakeMyTrip/Goibibo) how a real OTA actually wires this: what the
   request/response looks like for "send OTP," what happens on wrong
   OTP, what the resend-timer behavior is. Use the browser tool, observe
   live, don't rely on memorized knowledge.

3. DOMAIN_KNOWLEDGE.md: extend it with the exact contract between this
   frontend and backend — every field tagged [Observed] / [Stitch] /
   [Inferred] as usual. Specifically pin down:
   - Request shape frontend sends on "Send One-Time Code" click
     (mobile number + country code — note the mock hardcodes "+1", flag
     that as a defect to fix, add a real country selector)
   - Response shape backend returns (session_id, expiry)
   - The OTP-entry UI does not exist yet in the mock — design it fresh,
     matching the existing glassmorphic style (see login/code.html's
     .glass-panel, .input-glow, .btn-gradient classes — reuse them,
     don't invent a new visual language)
   - Request/response shape for OTP verify
   - Every error state the UI must show: wrong OTP, expired OTP, OTP
     locked after 3 attempts, network failure, rate-limited — none of
     these exist in the current mock, they must be designed net-new

4. TEST FIRST (RED): write tests for the API client / request-building
   logic and for the backend endpoint contract before wiring the actual
   button handlers. Run them, confirm they fail, show me real output.

5. IMPLEMENT (GREEN):
   - Backend: confirm the existing OTP endpoints match the contract from
     step 3 (adjust if the reference check in step 2 surfaced a gap)
   - Frontend: replace the dead type="button" handlers with real fetch
     calls to the backend, wire loading/disabled states on the buttons
     while a request is in flight, wire every error state from step 3
     to actual UI feedback (not silent failure)
   - Build the missing OTP-entry screen/step now, reusing the login
     screen's existing visual components
   Run tests again, show me real passing output.

6. GATES: ruff, mypy --strict, bandit (this slice touches auth — bandit
   is mandatory, not optional). Fix every real finding, show before/after
   output.

7. REVIEW.md: append the real RED/GREEN/gate output for this slice, plus
   an explicit list of what's still not covered (e.g. if social login
   OAuth wiring isn't done in this pass, say so, don't imply it's done).

Stop after step 7. Do not touch search/seat/checkout screens in this pass.

Slice for this pass: Login frontend-backend integration (OTP request +
verify + missing OTP-entry screen)
Scope: login/code.html wiring only — the send-OTP button, the new
OTP-entry step, and the two backend endpoints they call
Folder: Day4/ (or wherever the real login backend currently lives — tell
me the path if it's not in Day4/)
```

---

## Prompt5 — Note (not a paste-able prompt)

**Status: descriptive commentary, not an instruction template.** Included
here only for chronological completeness — this was a message summarizing
[PROMPT_connect_and_run_live.md](PROMPT_connect_and_run_live.md) (the file
below), not itself something to paste to Claude.

> Saved: `Day4/PROMPT_connect_and_run_live.md` — captures exactly what
> happened, generalized so it's repeatable for any slice: (1) read before
> building, (2) stand up real infra, don't mock it, (3) drive it like a
> real user in the browser, (4) fix real bugs with real proof, (5) verify
> at the data layer, not just the UI, (6) write the review log.

---

## Prompt6 — Connect frontend + backend, run it live (generic template)

**Status: template.** The filled-in version that actually executed is
Prompt6b below. Saved separately as
[PROMPT_connect_and_run_live.md](PROMPT_connect_and_run_live.md).

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit.

Task: connect the frontend to the backend for <SLICE_NAME> and RUN IT LIVE —
not a code review, not a plan, an actual working system I can click through
in a browser with real data in the real database at the end.

Follow this exact sequence, in order. Do not skip steps, do not claim a
step is done without showing the real command output that proves it.

1. READ BEFORE BUILDING. Read the actual frontend markup and the actual
   backend code that currently exist for this slice, in full, before
   changing anything. State what you found — don't assume either side's
   shape. If a directory or file you expect is missing, STOP and say so
   explicitly before reconstructing anything — do not silently rebuild
   from memory without flagging that the source was missing and why that
   matters.

2. STAND UP REAL INFRA, DON'T MOCK IT. If the stack needs Postgres/Redis/
   Kafka, bring up the real services (Docker Compose or equivalent) — do
   not substitute an in-memory fake for "speed." Check for and resolve
   port conflicts explicitly:
   - Before binding any port, check what's already listening on it
     (`lsof -nP -iTCP:<port> -sTCP:LISTEN`).
   - If something else already owns it — a native service, an unrelated
     process from another project — do NOT kill it blindly. Remap our
     service to a free port instead (compose override file, or an env
     var), and say what you found and why you remapped rather than reused
     the default.
   - Run real migrations against the real instance. Confirm schema exists
     before moving on (`\dt` or equivalent), don't assume the migration
     succeeded from exit code alone.

3. START BOTH SIDES, CONFIRM HEALTH. Start the backend, curl its health
   endpoint and confirm a real 200. Serve the frontend statically. Confirm
   both are reachable before touching the browser.

4. DRIVE IT LIKE A REAL USER, IN THE BROWSER. Use the browser tool to
   actually click through the flow — type the input a real user would
   type, click the real buttons, read the real network requests. Do not
   fabricate what the screen would show — take real screenshots. If an
   automation quirk stops literal typed keystrokes from landing correctly
   (common with auto-advancing per-character inputs), fix it by setting
   the DOM value directly and dispatching a real `input` event — but only
   as an input-delivery workaround, never to fake a result. Every request
   that matters (e.g. "send OTP", "verify OTP") must be confirmed via the
   network tab or the server log, not assumed from the UI alone.

5. WHEN SOMETHING BREAKS, FIX IT FOR REAL, SHOW THE PROOF. A live run
   surfaces real bugs static review won't (missing transitive deps,
   silent port shadowing, partial-failure states). When you hit one:
   - Show the actual error (curl output, server log, stack trace)
   - Fix it
   - Re-run and show the actual passing result
   - If the bug reveals a deeper gap (e.g. a state that can't recover from
     a partial failure), log it explicitly as a known gap, don't quietly
     patch around it and move on as if it never happened

6. VERIFY THE END STATE AT THE DATA LAYER, NOT JUST THE UI. A success
   screen is not proof. Query the real database directly (psql or
   equivalent) and show the actual row(s) that resulted from the actual
   user action. If nothing changed at the data layer, the slice isn't
   actually working, no matter what the screen shows.

7. WRITE THE REVIEW LOG. Create/append a review doc for this live run
   covering: what infra was stood up and any conflicts resolved, what
   broke and how it was fixed (with real output), the end-to-end proof
   (browser steps + real DB query result), and an explicit "what this
   does NOT cover" section — missing tests, missing gate runs, features
   not rebuilt, known gaps not fixed in this pass.

Never report a live-run task as complete based on "the code should work" —
only based on what you actually ran and actually observed.

Slice for this pass: <SLICE_NAME>
Frontend entry point: <path to the html/page>
Backend entry point: <path to the FastAPI app / router>
Folder: <e.g. Day5/, or the real project path>
```

---

## Prompt6b — Login, run it live (filled-in, EXECUTED)

**Status: EXECUTED.** Real proof in
[REVIEW_login_live.md](REVIEW_login_live.md). Saved separately as
[PROMPT_login_run_live_FILLED.md](PROMPT_login_run_live_FILLED.md).

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit.

Task: connect the frontend to the backend for Login (OTP request → verify)
and RUN IT LIVE — not a code review, not a plan, an actual working system
I can click through in a browser with real data in the real database at
the end.

Follow this exact sequence, in order. Do not skip steps, do not claim a
step is done without showing the real command output that proves it.

1. READ BEFORE BUILDING. Read the actual frontend markup and the actual
   backend code that currently exist for this slice, in full, before
   changing anything. State what you found — don't assume either side's
   shape. If a directory or file you expect is missing, STOP and say so
   explicitly before reconstructing anything.

2. STAND UP REAL INFRA, DON'T MOCK IT. Bring up real Postgres + Redis
   (Docker Compose). Check for port conflicts before binding
   (`lsof -nP -iTCP:<port> -sTCP:LISTEN`) — if something else already
   owns the default port, remap to a free one rather than killing an
   unrelated process. Run real Alembic migrations, confirm schema exists
   (`\dt`) before moving on.

3. START BOTH SIDES, CONFIRM HEALTH. Start the FastAPI backend, curl
   `/health`, confirm a real 200. Serve the frontend statically. Confirm
   both reachable before touching the browser.

4. DRIVE IT LIKE A REAL USER, IN THE BROWSER. Enter a real phone number,
   click Send OTP for real, read the real network request. Read the real
   OTP from the backend log (this demo logs it instead of sending SMS —
   never fabricate the code). Enter it in the OTP boxes, click Verify for
   real.

5. WHEN SOMETHING BREAKS, FIX IT FOR REAL, SHOW THE PROOF. If verify
   fails, show the actual curl/server-log error, fix the real cause
   (e.g. a missing dependency), restart, and re-run for real. If the bug
   reveals a deeper state-machine gap, log it explicitly — don't quietly
   patch and move on as if it never happened.

6. VERIFY THE END STATE AT THE DATA LAYER. Query Postgres directly
   (`psql`) and show the actual `users` / `refresh_tokens` rows created by
   the actual click-through. A success screen alone is not proof.

7. WRITE THE REVIEW LOG. What infra was stood up, what conflicts were
   resolved, what broke and how it was fixed (with real output), the
   end-to-end proof, and an explicit "what this does NOT cover" section.

Slice for this pass: Login OTP request → verify
Frontend entry point: Day4/frontend/login.html
Backend entry point: Day4/backend/app/main.py (auth router:
Day4/backend/app/api/routes_auth.py)
Folder: Day4/
```

---

## Prompt7 — Rate and review the code (template)

**Status: EXECUTED against the Login slice** (inline in conversation,
findings: hardcoded JWT secret default, unhandled race on user creation —
both later closed by Prompt8). Saved separately as
[PROMPT_rate_and_review_code.md](PROMPT_rate_and_review_code.md).

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit.

Task: rate and review the code for <SLICE_NAME>. Do not summarize what the
code does — I can read it. Find what's actually wrong with it, cite exact
locations, and give a justified rating. No vague praise, no "looks good
overall" without evidence.

Follow this exact process:

1. READ THE ACTUAL FILES. List every file in scope for this slice. Read
   each one in full before writing any finding — don't review from memory
   of having written it earlier in the conversation.

2. FIND REAL DEFECTS, EACH WITH:
   - Exact file:line citation
   - Severity: CRITICAL (data loss / security breach / silent corruption)
     / HIGH (real bug that will trigger in production, or a real security
     default that's wrong) / MEDIUM (a real gap, lower likelihood or
     impact) / LOW (style/maintainability, not a functional bug)
   - The concrete failure scenario: what real input or timing triggers it,
     not a hypothetical
   - What the fix should be, in one sentence — not the full fix unless
     asked

   Check specifically for, don't skip these categories:
   - Hardcoded secrets or insecure defaults (a secret with a fallback
     value instead of a required env var is a finding, even if it's
     labeled "dev-only")
   - Check-then-act races (a SELECT followed by an INSERT/UPDATE with no
     transaction/locking/upsert between them — this is the single most
     common defect class in this codebase's history, per
     DOMAIN_KNOWLEDGE.md and the cartsvc reference doc; look for it
     explicitly in every service function that reads then writes)
   - PII or secrets (OTP codes, tokens, phone numbers, card data) logged
     in plaintext, even behind a "demo-only" comment
   - Unhandled exceptions that would surface as a raw 500 instead of a
     domain-meaningful error
   - Client-side-only validation with no server-side re-validation, or
     the reverse (server validation with client validation duplicated and
     able to drift)
   - Money/currency handled as float instead of int minor-units or Decimal
   - Missing idempotency on any mutating endpoint that a client could
     plausibly retry (double-tap, network retry)

3. DO NOT FLAG what's actually fine just to pad the list. If the state
   machine, layering, or HTTP status code choices are correct, say so
   briefly and move on — don't invent nitpicks to seem thorough.

4. GIVE A NUMERIC RATING (out of 10) with a one-paragraph justification
   that explicitly ties the number to the findings above — e.g. "solid
   shape, dragged down by N real security/concurrency findings that the
   project's own gates (ruff/mypy --strict/bandit) would have caught had
   they been run." The rating must be defensible from the findings list,
   not a separate vibe.

5. END WITH ONE QUESTION: which finding(s), if any, should be fixed right
   now before moving to the next slice, versus logged and deferred.

Do not use the ReportFindings tool unless explicitly told to — respond in
plain text unless a code-review skill/command says otherwise.

Slice for this pass: <SLICE_NAME>
Files in scope: <list exact paths — do not let scope silently expand to
the whole codebase>
```

---

## Prompt8 — Close the two findings from Prompt7

**Status: EXECUTED.** Real proof in
[REVIEW_prompt8_findings_closed.md](REVIEW_prompt8_findings_closed.md).
Saved separately as [PROMPT8_fix_findings.md](PROMPT8_fix_findings.md).

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit.

Task: close two known findings from the Login slice review
(Day4/REVIEW_login_live.md and the code review that followed it) before any
new slice starts. Do not touch other screens/endpoints.

Findings to close:

1. HIGH — hardcoded default JWT secret
   File: Day4/backend/app/config.py:11
   `jwt_secret: str = "dev-secret-change-in-production"`
   Fix: require JWT_SECRET from the environment with no silent fallback —
   raise at startup if unset, instead of defaulting to a value that could
   ship unnoticed.

2. HIGH — unhandled race condition on user creation
   File: Day4/backend/app/services/auth_service.py:96-101
   SELECT-then-INSERT with no handling for the concurrent-insert case; the
   DB unique constraint on `phone` will raise IntegrityError on a race,
   currently unhandled, surfaces as a raw 500.
   Fix: catch the IntegrityError and re-fetch the existing user, or use an
   upsert (INSERT ... ON CONFLICT) instead of check-then-insert.

Follow this sequence:

1. RED: write a test that reproduces each finding before fixing it.
   - For finding 1: a test asserting the app fails to start / raises when
     JWT_SECRET is unset (don't just assert the default string is gone —
     prove the unsafe path is actually blocked).
   - For finding 2: a test that simulates two concurrent `verify_otp`
     calls for the same new phone number and asserts both return the same
     user with no unhandled exception.
   Run both, confirm they fail against the current code, show real output.

2. GREEN: implement the minimal fix for each. Re-run the same tests, show
   real passing output.

3. GATES: ruff, mypy --strict, bandit — bandit is mandatory here since
   both findings are security-adjacent. Show before/after output if
   anything is flagged.

4. LIVE RE-VERIFY: re-run the actual login flow live (per
   Day4/PROMPT_login_run_live_FILLED.md steps 3-6) to confirm the fix
   didn't break the working happy path. Real browser click-through, real
   DB row check, not just the unit tests.

5. REVIEW.md: append to Day4/REVIEW_login_live.md — what was fixed, the
   real RED/GREEN/gate output, and confirmation the live flow still works
   post-fix.

Do not start Search Flights or any other slice until this is done and
confirmed.
```

---

## Prompt9 — Search Flights slice (route + frontend, run it live)

**Status: EXECUTED.** Real proof in
[REVIEW_prompt9_search_flights.md](REVIEW_prompt9_search_flights.md).
Saved separately as
[PROMPT9_search_flights_slice.md](PROMPT9_search_flights_slice.md).

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit.

We work in single verified vertical slices, never big-bang generation.
This slice already has a tested contract — Day4/src/international_smile/
flight_search.py (FlightSearchRequest, 11 passing tests, gates clean, see
Day4/REVIEW.md). This pass wires that contract into a real FastAPI route,
a minimal search response, and a real frontend screen, then runs it live —
following the same process as the Login slice.

Follow this exact sequence, in order. Do not skip steps, do not claim a
step is done without showing real command output.

1. READ FIRST. Read Day4/src/international_smile/flight_search.py and
   Day4/DOMAIN_KNOWLEDGE.md §1-2 in full before writing the route. Confirm
   the 4 open conflicts logged there (Multi City in scope? special-fare
   programs? pay-with-points? promo-code placement?) — if still
   unresolved, ask before assuming an answer; do not silently pick one.

2. REFERENCE CHECK (5 min max): re-verify on goindigo.in what a real
   search RESPONSE looks like — result list shape, fields per flight,
   price display — since only the search REQUEST was verified so far, not
   the results page. Tag new findings [Observed] in DOMAIN_KNOWLEDGE.md.

3. TEST FIRST (RED): write a test for a new `SearchResult` /
   `FlightOption` Pydantic model and for the `POST /search/flights` route
   (using FastAPI's TestClient), before either exists. Run it, confirm it
   fails, show real output.

4. IMPLEMENT (GREEN):
   - Backend: add the route wrapping FlightSearchRequest, returning a
     small set of realistic mock flight options (no live GDS integration
     in this slice — flag that explicitly as a scope boundary, not
     implied as done)
   - Frontend: build search_flights.html adapted from
     stitch_modern_irctc_redesign/search_flights/code.html, rebranded
     International Smile, wired to the real endpoint (replace the dead
     "Search Flights" button with a real fetch call)
   Run tests again, show real passing output.

5. GATES: ruff, mypy --strict on the new code. Show output.

6. LIVE RUN: stand up backend + frontend together (reuse the running
   Postgres/Redis containers if still up, confirm with `docker ps` first
   rather than assuming), drive a real search in the browser (Delhi →
   Mumbai or similar), confirm the real network request/response, screenshot
   the rendered results.

7. REVIEW.md: append the real RED/GREEN/gate/live output, plus an
   explicit "what this does NOT cover" section — no live fare data, no
   persistence of search history, no pagination, whatever else is out of
   scope for this pass.

Stop after step 7. Do not touch select_flight/select_seat/checkout in
this pass.

Slice for this pass: Search Flights (request already contracted, this
pass adds the route + response + live-wired frontend)
Folder: Day4/
```

---

## Prompt10 — Integrate Login and Search (optional-auth passthrough)

**Status: DRAFTED, NOT YET EXECUTED.** Waiting on confirmation of the
gate-timing default it states explicitly (guest search allowed, login
required only later at checkout — per IndiGo's observed live pattern).
Saved separately as
[PROMPT10_integrate_login_search.md](PROMPT10_integrate_login_search.md).

```
Role: Principal architect + full-stack engineer, travel domain.
Project: International Smile (flight booking). Stack: FastAPI, Pydantic v2,
PostgreSQL/SQLAlchemy 2.x/Alembic, Redis, Celery, Kafka, pytest, ruff,
mypy --strict, bandit.

Task: integrate Login and Search Flights — right now they are two
disconnected features that happen to coexist in the same browser session.
Close that gap for real, not by assumption.

Context you must read first (do not skip): DOMAIN_KNOWLEDGE.md §2.6 left
this open as an unresolved product decision — does login gate the whole
funnel at entry (classic pattern), or is it deferred to checkout while
search/browse stays guest-accessible (the pattern actually [Observed] live
on goindigo.in this session — IndiGo's search widget requires no login)?
This has NOT been answered by the user as of this prompt. Default to the
observed IndiGo pattern (guest search allowed, login required only when
proceeding past search) UNLESS the user has since told you otherwise —
state this assumption explicitly before writing code, don't bury it.

Follow this exact sequence, in order. Real output only, no claims.

1. READ FIRST. Read the current state of both slices in full:
   Day4/backend/app/api/routes_search.py, Day4/backend/app/api/
   routes_auth.py, Day4/backend/app/core/security.py (token creation —
   there is currently no token verification/dependency anywhere),
   Day4/frontend/login.html, Day4/frontend/search_flights.html. Confirm:
   search has zero auth awareness today (no header sent, no check made).

2. DESIGN THE ACTUAL INTEGRATION CONTRACT, per the guest-search decision
   above:
   - Add a reusable `get_current_user_optional` FastAPI dependency
     (Authorization: Bearer <token>, decodes via the existing JWT secret/
     algorithm in app/core/security.py, returns the user if a valid token
     is present, returns None if absent — does NOT reject an absent
     token, since search is guest-accessible)
   - Add a separate `get_current_user_required` dependency (same decode,
     but raises 401 if missing/invalid) — build it now even though no
     route uses it yet, since checkout/booking will need it in a future
     slice. Do not wire it to /search/flights.
   - Wire `get_current_user_optional` into POST /search/flights. If a
     user is present, the response should reflect that (e.g. echo
     `searched_by_user_id` in SearchResponse) — this is the actual,
     observable proof of integration, not just "the dependency exists."
   - Frontend: search_flights.html reads `access_token` from localStorage
     if present and sends it as `Authorization: Bearer <token>` on the
     search request. If absent, search still works exactly as today.

3. TEST FIRST (RED). Write tests before implementing:
   - A logged-in search (valid token attached) returns
     `searched_by_user_id` matching the token's subject
   - A guest search (no token) still succeeds, `searched_by_user_id` is
     null
   - An invalid/expired token on search does NOT reject the request
     (guest-fallback behavior, not a 401) — assert this explicitly, don't
     leave it untested
   - `get_current_user_required` (once wired to nothing yet) raises 401
     when no token is present, standalone unit test
   Run them, confirm real failure output.

4. IMPLEMENT (GREEN). Minimal code per step 2. Re-run tests, show real
   passing output.

5. GATES: ruff, mypy --strict, bandit (mandatory — this touches auth
   token handling). Show output.

6. LIVE RUN: real login → real search in the same browser session,
   confirm via the actual network request that the Authorization header
   is now present and the response actually contains the matching
   `searched_by_user_id` — then repeat as a guest (clear localStorage
   first) and confirm search still works with no user id. Two real runs,
   not one assumed to cover both.

7. REVIEW.md: real RED/GREEN/gate/live output for both the logged-in and
   guest paths, plus explicit note that `get_current_user_required`
   exists but is not yet enforced anywhere — that's for the checkout
   slice, not this one.

Stop after step 7. Do not add the required-auth gate to any route in this
pass — that's scope creep past what "integrate Login and Search" means
today.

Slice for this pass: Login + Search integration (optional-auth passthrough)
Folder: Day4/
```

---

## Status summary

| # | Prompt | Status |
|---|---|---|
| 1 | Initial requirement framing | Informational |
| 2 | Focus scope | Informational |
| 3 | Generic slice template | Template (reused by 4/6/8/9/10) |
| 4 | Login frontend-backend (design) | Superseded by 6b |
| 5 | Note about the connect-and-run-live file | Not a prompt |
| 6 | Connect + run live (generic template) | Template (filled by 6b) |
| 6b | Login, run it live | **EXECUTED** — REVIEW_login_live.md |
| 7 | Rate and review (template) | **EXECUTED** against Login |
| 8 | Close 2 findings | **EXECUTED** — REVIEW_prompt8_findings_closed.md |
| 9 | Search Flights slice | **EXECUTED** — REVIEW_prompt9_search_flights.md |
| 10 | Integrate Login + Search | **DRAFTED, NOT EXECUTED** |

There is also a consolidated single-prompt replacement for 3/6/7 combined
— see [MASTER_PROMPT.md](MASTER_PROMPT.md) — intended as the standing
template to use going forward instead of chaining individual numbered
prompts.
