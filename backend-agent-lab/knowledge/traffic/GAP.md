# Gap: no real production traffic shape for taskflow-ops

`taskflow-ops` has never been deployed anywhere real traffic could hit
it. There are no access logs, no request-rate history, no payload-size
distribution to draw from.

**Consequence for agents:** `risk-workload` and `load-test-engineer`
cannot build a load profile from real traffic. Synthetic load tests run
against this service test an assumed shape, not a validated one — this
must be stated in every `experiments/` entry produced against
`taskflow-ops` until real traffic exists (e.g. "workload is synthetic:
N concurrent users, uniform arrival — not derived from production data").

**To close this gap:** once `taskflow-ops` has any real usage, export
request-rate-by-hour and payload-size distribution here before the next
tuning cycle.
