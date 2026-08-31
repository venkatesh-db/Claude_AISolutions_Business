# Hands-on Lab 7 — RxFlow Ops MCP Server + a Live, Interactive UI

The MCP server this lab describes already exists at
[`rxflow-ops-mcp/`](../../rxflow-ops-mcp) — 7 tools (`get_ticket`,
`search_incidents`, `get_service_owner`, `get_runbook`, `get_lab_health`,
`create_change_request`, `update_ticket_status`), fixture-backed, hook-guarded,
tested. What's missing is a **UI that watches and drives the real server
live** — not a mockup of what the loop looks like, an actual browser page
wired to the actual running MCP process over the actual protocol, so you can
click through ticket → incident → runbook → owner → patch → change request →
approval → verified status update and watch every step really happen.

Build this as `Day10/lab7-rxflow-console/`. Work through the phases below in
order, one message per phase. Each phase produces something the next one
needs.

```
Browser UI (your click)
      │  fetch()
      ▼
Local HTTP bridge (FastAPI)  ── spawns / holds open ──▶  rxflow_ops_mcp server
      │  SSE stream of every tool call + result               (real subprocess,
      ▼                                                         real fixtures,
Browser UI (live update)                                       real hooks)
```

---

## Phase 0 — Confirm the server the lab actually asks for

```
Read rxflow-ops-mcp/README.md and rxflow-ops-mcp/src/rxflow_ops_mcp/server.py.
Confirm all 7 tools the lab spec names (get_ticket, search_incidents,
get_service_owner, get_runbook, get_lab_health, create_change_request,
update_ticket_status) exist, are MCP-visible under their rxflow_-prefixed
names, and that pytest -q / ruff check . / mypy --strict src/ all still pass
in that project's .venv. Don't change anything yet — just report pass/fail
per tool and per check. If anything's missing or broken, fix only that,
minimally, before moving on.
```

---

## Phase 1 — A bridge that makes the real server driveable from a browser

```
Build Day10/lab7-rxflow-console/bridge/ as a small FastAPI app that:

1. On startup, spawns rxflow-ops-mcp's server as a real subprocess and holds
   open a genuine mcp.ClientSession over stdio for the lifetime of the
   bridge process — one persistent session, not one-per-request.
2. Exposes one REST endpoint per MCP tool, e.g. POST /tools/get_ticket,
   POST /tools/create_change_request — each just forwards to
   session.call_tool(...) and returns the real JSON result, unmodified.
3. Exposes GET /events as a Server-Sent-Events stream that emits one event
   per tool call made through step 2 — {tool, args, result, timestamp} — so
   a browser tab can watch every call happen in real time, including ones
   triggered by something other than that tab (e.g. a headless Claude run
   in Phase 4).
4. Adds no new business logic — no tool-sequencing rules, no approval
   gating. Those already live in rxflow-ops-mcp's hooks and store; the
   bridge is a dumb, faithful pipe to the real server.

Prove it without a browser first: curl -X POST localhost:8000/tools/get_ticket
-d '{"ticket_id":"RXF-4821"}' and show the real ticket coming back, then
curl the /events stream in a second terminal and show that same call show up
there.
```

---

## Phase 2 — The interactive console: the 9-step loop, for real

```
Build Day10/lab7-rxflow-console/ui/index.html (or a small Vite/React app if
you'd rather — your call, tell me which and why) as a single page that:

1. Walks the 9 steps from the lab spec as a visible pipeline, each step a
   real action, not a canned narrative:
   1. Retrieve the defect  → calls /tools/get_ticket for RXF-4821
   2. Search prior incidents → /tools/search_incidents("pricing-engine")
   3. Read the runbook → /tools/get_runbook("pricing-engine")
   4. Check service ownership → /tools/get_service_owner("pricing-engine")
   5. Investigate the repo → not an MCP call; a text area where you paste
      what you found, kept as local UI state feeding step 6
   6. Produce a patch → not an MCP call; a diff viewer showing the
      characterization-test-first patch you write against
      rxflow-order-pricing-simple, referenced but not modified by this UI
   7. Prepare a change request → calls /tools/create_change_request — the UI
      must show the response's status is pending_approval, never anything
      else, and must not let you skip to step 9 without step 8
   8. Request approval → a real modal/gate: a human must click "Approve"
      in the UI before the flow continues. No auto-advance, no timeout that
      bypasses it.
   9. Update status, only after verification → calls
      /tools/update_ticket_status with verified_by_tests=True and an
      idempotency_key generated client-side; the UI must refuse to enable
      this control until step 8's approval happened AND a "tests passed"
      checkbox is ticked
2. Subscribes to the bridge's /events SSE stream and renders a live activity
   log alongside the pipeline — every real tool call, as it happens,
   including the untrusted-text fencing on get_ticket/get_runbook shown
   visibly (not stripped) so the injection-guarding from
   rxflow-ops-mcp/security.py is something you can actually see fire.
3. Is genuinely interactive: each step is a real button that makes a real
   call and can fail for a real reason (ticket not found, incident search
   empty, approval not yet granted) — surface those errors in the UI rather
   than hiding them.

Run it against the bridge from Phase 1, click through all 9 steps yourself,
and show me a screenshot or the live event log proving steps 7→8→9 actually
gate on each other rather than just looking like they do.
```

---

## Phase 3 — Headless Claude drives the loop, UI just watches

```
Write scripts/run_loop_headless.sh: a single `claude -p "..." --output-format
json` invocation (no human present) that, using the bridge's REST endpoints
(or the MCP server directly), walks steps 1-4 and 7 of the loop against
RXF-4821 — retrieve the ticket, search incidents, read the runbook, check
ownership, then file the change request — and stops there, because step 8
(human approval) is not something headless Claude is allowed to do for
itself.

While that script runs, keep the Phase 2 UI open in a browser pointed at the
same bridge. Show me the UI's live activity log filling in in real time from
a process you didn't click anything in — that's the actual proof the bridge
in Phase 1 is a shared real state, not per-tab mock data.
```

---

## Phase 4 — The approval gate, closed by a human, in the same UI

```
With the change request from Phase 3 sitting at pending_approval, open the
Phase 2 UI, find that same change request (it should already be visible from
the live event log), and click Approve yourself. Then tick "tests passed"
and click the update_ticket_status control.

Show me: the ToolError the UI would have surfaced if you'd tried
update_ticket_status before approving or before ticking verified_by_tests,
and then the successful call afterward with its idempotency_key. Replay the
exact same click a second time and show the response comes back
replayed=true instead of writing again — that's rxflow-ops-mcp's existing
idempotency guarantee, now something you can trigger by clicking a button
twice instead of reading about it.
```

---

## What "real" means here, explicitly

Nothing in this lab is allowed to be a static mockup once Phase 1 exists:
- The UI never hardcodes a tool's response — every card, table, and log line
  it renders came from an actual `/tools/*` call in that session.
- The approval gate is UI state a human actually set, not a timer or a
  pre-filled "approved: true".
- The activity log is driven by the bridge's SSE stream, not by the UI
  re-simulating what it thinks should have happened.

If a step can't be made real without credentials or infrastructure you don't
have (there shouldn't be any here — this lab is entirely fixture-backed and
local), stop and say so explicitly rather than faking that step's output.
