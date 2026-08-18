# Safe-Release Skill — Live Run Log

**Change under review:** add `GZipMiddleware` (compress responses ≥500 bytes)
to `taskflow-ops`. One named variable, per Skill stage 6.

## What actually ran, stage by stage

| Stage | Action | Result |
|---|---|---|
| 1. Proposal | Scope: response compression only. Risk: low (standard, well-tested Starlette middleware). Rollback: `docker run taskflow-ops:baseline` (image kept, verified present). | Approved |
| 2. Contract | `/healthz` → `{"status":"ok"}`, `/tasks` POST → 201 `queued`, `/metrics` shape unchanged. | Written before stage 3 |
| 3. Smoke test | `smoke_test.py` against `taskflow-ops:baseline` container | **PASSED** |
| 4. Concurrency | `concurrency_check.py --count 10` against baseline | **PASSED** — 10 distinct IDs, queued=10 |
| 5. Baseline | `capture_baseline.py` → `baseline.json` | Captured: `{"uptime_seconds": 34.95, "requests_total": 17, "tasks_by_status": {"queued": 10}}` |
| 6. Named change | GZip compression, `minimum_size=500` | One variable, stated |
| 7. Build | `docker build -t taskflow-ops:release-candidate .` | Succeeded; baseline image confirmed still present (`docker images` showed both tags) |
| 8. Repeat & compare | Stages 3–4 re-run against candidate; `compare_baseline.py` | Smoke **PASSED**, concurrency **PASSED** (10/10, queued=10). Compression **verified directly**: `curl -H "Accept-Encoding: gzip" /openapi.json` returned `content-encoding: gzip` on the candidate and no such header on the baseline for the identical request. |
| 9. Decision | See below | **ACCEPT** |

## A real miss, caught and corrected mid-run

The first attempt to verify stage 6's effect checked `/metrics` for a
`Content-Encoding` header and found none — on *both* baseline and
candidate. Before writing that up as "the change had no effect," the
response size was checked: `/metrics` is 75 bytes, well under the
500-byte compression threshold. The test target was wrong, not the
change. Re-tested against `/openapi.json` (3,219 bytes) and the header
appeared exactly where expected. Recorded here because "the change
looks like it had no effect" and "the change had no effect" are
different claims, and only checking the response size distinguished
them.

A second issue: `compare_baseline.py`'s uptime comment assumed a
sequential replace (candidate uptime lower than baseline's). This run
deployed both containers side by side, so the candidate's uptime was
*higher* by the time it was checked — correct, but the script's fixed
comment claimed the opposite direction was "expected." Fixed to state
the actual invariant (uptime alone isn't a pass/fail signal, in either
direction) rather than a comment that was right in one deployment
pattern and wrong in another.

## Stage 9 — independent review and decision

**Contract (stage 2):** held — no response shape changed except the new
`Content-Encoding` header on responses ≥500 bytes, which was not part of
the frozen contract (the contract only specified body shapes).

**Named change (stage 6):** had exactly its expected effect, verified
directly against two different endpoints with two different payload
sizes, not inferred from one ambiguous test.

**Unexplained regressions:** none found.

**Decision: ACCEPT.**

## Cleanup

Both containers stopped and removed after this run; `taskflow-ops:baseline`
and `taskflow-ops:release-candidate` images retained locally as the
rollback pair per stage 1's rollback plan.
