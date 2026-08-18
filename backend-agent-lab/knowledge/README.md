# Knowledge base — status

What's real, what's derived, what's an honest gap. Any agent reading
these folders should trust this file over assuming a folder is complete
just because it exists.

| Folder | Status | Source |
|---|---|---|
| `api/` | **Real** | `openapi.json` generated directly from `taskflow-ops`'s FastAPI app — not hand-written, regenerate any time the code changes |
| `architecture/` | **Real, one entry** | One ADR, formalizing a real decision already made (and its real cause) during `taskflow-ops`'s build |
| `experiments/` | **Real, one entry** | The actual `safe-release` run log from `taskflow-ops`, copied here |
| `incidents/` | **Real, one entry** | Not a production incident — a real near-miss caught *during* the safe-release run (a wrong test target led to a wrong conclusion, caught before it shipped). Recorded because "we almost got this wrong" is exactly what this folder is for |
| `objectives/` | **GAP — intentionally empty** | No SLO/SLI has ever been defined for `taskflow-ops`. See `objectives/GAP.md` |
| `product/` | **Real** | Task lifecycle and status transitions, derived directly from `domain.py`'s `TaskStatus` enum and the tests that assert its behavior |
| `test-data/` | **Real** | The actual fixtures used in `taskflow-ops`'s test suite |
| `traffic/` | **GAP — intentionally empty** | `taskflow-ops` has never run in production; there is no real traffic shape to record. See `traffic/GAP.md` |

**Two gaps, not fabricated.** `risk-workload` and `performance-analyst`
(the two agents that consume `objectives/` and `traffic/`) must report
these gaps explicitly rather than inventing plausible numbers — see each
agent's `AGENT.md`.
