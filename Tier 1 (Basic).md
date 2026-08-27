# Tier 1 — Basic
## The Engineering Constitution (Module 6)

Build a nested CLAUDE.md hierarchy — root, then per-service — with referenced docs instead of inlined theory. Prove closest-file precedence by requesting the identical change in three directories and showing the guidance actually differs.

---

## Python · RxFlow — Prescription routing & pricing constitution

Repo shape: `order_api/ routing/ pricing/ workers/ infra/`
Verified with: `uv run pytest`, `ruff`, `mypy --strict`

```
I'm setting up durable repository guidance for RxFlow, a Python
prescription-lens routing and pricing service. The repo has order_api/,
routing/, pricing/, workers/, and infra/, plus docs/architecture.md and
docs/code-review.md (create stub versions of both — 1 page each, real
content, no filler).

Build a nested CLAUDE.md hierarchy:
- Root CLAUDE.md: verified build/test/lint commands (run them yourself
  first, paste exact output and timing), the non-negotiables (never log
  prescription values or patient identifiers — use order_ref; every
  Alembic revision needs a working downgrade(); new outbound calls need
  explicit timeout + retry policy; every defect fix ships with a
  failing-first test), and a required end-of-task report format.
  Reference docs/architecture.md and docs/code-review.md rather than
  inlining them.
- pricing/CLAUDE.md: pricing changes require characterization tests
  FIRST, before any refactor — state why (pricing bugs are
  revenue-silent and customer-invisible until an invoice dispute).
- workers/CLAUDE.md: async job idempotency rules — every worker must be
  safe to run twice on the same message.
- routing/CLAUDE.md: lens-lab routing decisions must be explainable —
  log the decision factors, never just the outcome.

Every rule must be an operational, verifiable instruction — no theory,
no unverified commands, nothing that could conflict with a rule higher
in the tree.

Then prove closest-file precedence: ask me to add a small feature three
times — once phrased identically for order_api/, once for pricing/,
once for workers/ — and show me, side by side, how your approach
differs each time because of which CLAUDE.md applied. Call out exactly
which file drove which behavior change.
```

**Outcome:** a tested hierarchy where the same request produces provably different, correct behavior per directory.

---

## Java · LensForge — Optical manufacturing catalog constitution

Repo shape: `catalog-service/ inventory-service/ pricing-engine/ order-workers/ infra/`
Verified with: `./mvnw verify`, `checkstyle`, `jacoco`

```
I'm setting up durable repository guidance for LensForge, a Spring Boot
monorepo for an optical lens manufacturer: catalog-service/,
inventory-service/, pricing-engine/, order-workers/, infra/, plus
docs/architecture.md and docs/code-review.md (create real 1-page stubs
of both).

Build a nested CLAUDE.md hierarchy:
- Root CLAUDE.md: run and paste verified output for `./mvnw -q verify`,
  `./mvnw checkstyle:check`, and coverage via jacoco — include exact
  timing. Non-negotiables: no lombok @Data on JPA entities
  (equals/hashCode break lazy proxies — state why), every Flyway
  migration needs a corresponding rollback script checked in alongside
  it, every REST controller method has an explicit @Valid DTO (no raw
  Map<String,Object> bodies), every defect fix ships with a red-then-
  green JUnit test. Reference the two docs, don't inline them.
- pricing-engine/CLAUDE.md: pricing changes require characterization
  tests FIRST — pricing regressions here mean a lab either over-bills
  or under-bills a practice, and neither is caught by CI, only by a
  customer complaint weeks later.
- inventory-service/CLAUDE.md: all stock-decrement operations must be
  transactional and idempotent under retry (use an idempotency key
  column), because Kafka delivery here is at-least-once.
- order-workers/CLAUDE.md: every consumer must log which message
  offset it processed and be safe to replay.

Every rule operational and verifiable, nothing that conflicts with the
root file.

Then prove closest-file precedence: give me the same feature request
phrased identically in catalog-service/, pricing-engine/, and
order-workers/, and show side by side how the applicable CLAUDE.md
changed your approach each time, naming the exact rule that fired.
```

**Outcome:** a tested hierarchy the team can fork into every Spring Boot repo, with proof it changes behavior, not just vibes.

---

## .NET · OrderGateway — Lab order & EDI integration constitution

Repo shape: `OrderApi/ EdiIntegration/ Pricing/ Workers/ Infra/`
Verified with: `dotnet test`, `dotnet format --verify-no-changes`

```
I'm setting up durable repository guidance for OrderGateway, an
ASP.NET Core solution that receives lab orders over EDI/X12 and routes
them to manufacturing: OrderApi/, EdiIntegration/, Pricing/, Workers/,
Infra/, plus docs/architecture.md and docs/code-review.md (write real
1-page stubs).

Build a nested CLAUDE.md hierarchy:
- Root CLAUDE.md: run and paste verified output for `dotnet build`,
  `dotnet test --filter Category!=Integration`, and
  `dotnet format --verify-no-changes`, with exact timing.
  Non-negotiables: never log raw EDI payloads or patient names — log
  the interchange control number only; every EF Core migration needs a
  tested Down(); every outbound HTTP call to the manufacturing partner
  needs Polly timeout + retry + circuit breaker; every defect fix ships
  with a failing-first xUnit test. Reference the two docs rather than
  inlining them.
- EdiIntegration/CLAUDE.md: malformed EDI segments must be quarantined,
  never thrown away — every rejected message needs an auditable reason
  code, because a silently dropped order is a lost patient
  prescription.
- Pricing/CLAUDE.md: pricing changes require characterization tests
  FIRST, same rationale as elsewhere — revenue-silent bugs.
- Workers/CLAUDE.md: background jobs (IHostedService) must be safe to
  run twice on the same message — dedupe on interchange control number.

Every rule operational and verifiable, no conflicts with the root file.

Then prove closest-file precedence: ask for the identical small feature
in OrderApi/, EdiIntegration/, and Pricing/, and show side by side
exactly how the guidance — and therefore your implementation choices —
differed each time, citing the rule that applied.
```

**Outcome:** a hierarchy Essilor can copy into every .NET service, with three transcripts as proof it isn't decoration.
