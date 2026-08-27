# Tier 2 — Intermediate
## A Release-Readiness Skill, Run in Parallel (Modules 7 & 8)

Turn one senior engineer's release checklist into a Skill with progressive context loading, then fan it out into five bounded, read-only sub-agents whose findings the primary agent consolidates, de-duplicates, and turns into one release decision.

---

## Python · RxFlow — Release-readiness Skill + 5-way review

Skill fires on: "prep this for release" / "is this ready to ship"

```
Build a release-readiness Skill for RxFlow at
.claude/skills/release-readiness/SKILL.md. It must: identify which
services changed since the last tagged release (git diff against the
last tag), find the tests those changes affect, run focused validation
(not the whole suite blind), diff the current OpenAPI schema against
the previous tagged version and flag breaking changes, review any new
Alembic revisions for a working downgrade(), check that new/changed
error paths actually handle failure (no bare except, no swallowed
exceptions), verify structured logs and metrics exist for new code
paths, do a lightweight security pass (secrets, injection, auth checks
on new endpoints), and emit a structured release report (markdown,
with a clear GO / NO-GO and cited evidence per finding — no unverified
claims). Keep SKILL.md itself short; put the checklist detail and any
templates in bundled reference files loaded on demand, not inlined.

Once the Skill exists, don't run it yourself. Instead fan it out:
launch five bounded, read-only sub-agents against the current
uncommitted diff — correctness, test coverage, security, performance,
API compatibility — each restricted to read-only tools, each producing
findings with file:line evidence, no speculation presented as fact. As
the primary agent, consolidate: de-duplicate overlapping findings,
reject anything a sub-agent couldn't back with evidence, order by
severity, and issue one release decision with clear ownership per
finding (who fixes what before merge).

Then run the whole thing on a change I did NOT write — I'll hand you a
diff — so I can check the checklist works on unfamiliar code, not just
the code you already understand.
```

**Outcome:** one release decision, five traceable findings, zero speculation — reproducible by any engineer on the team.

---

## Java · LensForge — Release-readiness Skill + 5-way review

Skill fires on: "prep this for release" / "is this ready to ship"

```
Build a release-readiness Skill for LensForge at
.claude/skills/release-readiness/SKILL.md. It must: identify which
Maven modules changed since the last release tag, find the JUnit tests
those changes affect and run only those (not a blind full
`mvnw verify`), diff the current OpenAPI/Springdoc schema against the
previous tagged version and flag breaking changes to consumers, review
any new Flyway migrations for a checked-in rollback script, check
new/changed exception handling (no swallowed exceptions, no generic
`catch (Exception e) {}`), verify new endpoints have @Valid input
validation and structured logging via the shared logging aspect, do a
lightweight security pass (hardcoded secrets, missing @PreAuthorize on
new endpoints, SQL built by string concatenation), and emit a
structured markdown release report with a GO / NO-GO and cited
evidence. SKILL.md stays short; push checklist detail and templates
into bundled reference files loaded on demand.

Then fan it out: don't run the Skill yourself — launch five bounded,
read-only sub-agents against the current diff (correctness, test
coverage, security, performance, API compatibility), each read-only-
restricted, each citing file:line evidence, no speculation. As primary
agent, consolidate: de-duplicate, reject unsupported claims, order by
severity, produce one release decision with named ownership per
finding.

Run it on a diff I hand you that I did not write — confirm the
checklist generalizes past code you already know.
```

**Outcome:** a senior reviewer's checklist becomes a repeatable, evidence-based gate any Spring Boot engineer runs the same way.

---

## .NET · OrderGateway — Release-readiness Skill + 5-way review

Skill fires on: "prep this for release" / "is this ready to ship"

```
Build a release-readiness Skill for OrderGateway at
.claude/skills/release-readiness/SKILL.md. It must: identify which
projects in the .sln changed since the last release tag, find the
xUnit tests affected and run only those, diff the current
Swagger/OpenAPI export against the previous tagged version and flag
breaking changes for partner labs consuming the API, review any new
EF Core migrations for a tested Down(), check new/changed error
handling (no empty catch blocks, Polly policies present on new
outbound calls), verify new endpoints log via the shared Serilog
enrichers with correlation IDs and never log raw EDI/PII, do a
lightweight security pass (secrets in appsettings, missing [Authorize]
on new controllers, unparameterized SQL), and emit a structured
markdown release report with GO / NO-GO and cited evidence. Keep
SKILL.md itself short, bundle checklist detail and report templates as
reference files loaded on demand.

Then fan it out instead of running it yourself: launch five bounded,
read-only sub-agents over the current diff — correctness, test
coverage, security, performance, API compatibility — each read-only,
each citing file:line evidence, no unverified speculation. As primary
agent, consolidate the five reports: de-duplicate, reject claims
without evidence, order by severity, issue one release decision with
named ownership per finding.

Then run it on a diff I hand you that I didn't write, to prove the
checklist works on code you haven't already internalized.
```

**Outcome:** a multi-agent review with traceable ownership — and a documented decision on when a single agent would've been enough.
