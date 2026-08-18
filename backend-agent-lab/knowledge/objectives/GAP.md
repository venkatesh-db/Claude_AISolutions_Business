# Gap: no SLO/SLI defined for taskflow-ops

No one has stated a target P95 latency, an error-rate budget, or a
throughput requirement for this service. It has never run in
production, so there's no historical basis to derive one from either.

**Consequence for agents:** `risk-workload` cannot state a real P95
target or error-rate limit. It must say so explicitly and either (a)
request one from a human before proceeding, or (b) proceed with an
**explicitly labeled placeholder** (e.g. "no SLO defined — using P95 <
200ms as an unvalidated placeholder for this test run only") — never a
silent default presented as if it were a real requirement.

**To close this gap:** define at minimum a P95 latency target and an
acceptable error rate for `/tasks` before running a real tuning
exercise against this service.
