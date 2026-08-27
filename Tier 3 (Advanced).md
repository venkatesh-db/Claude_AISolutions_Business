# Tier 3 — Advanced
## MCP Operations Server, Hook-Enforced (Modules 9 & 10)

A real connector into operational systems, with human approval structurally enforced before any external write — plus hooks that block unsafe commands rather than merely advise against them. The assessment: trigger a hook block, then bring the change into compliance.

---

## Python · RxFlow — Ops MCP server + guardrail hooks

Server: FastMCP · Hooks: PreToolUse / PostToolUse

```
Build an MCP server in Python (FastMCP or the official SDK) exposing:
get_ticket, search_incidents, get_service_owner, get_runbook,
get_lab_health, create_change_request, and update_ticket_status. Each
tool: narrow single responsibility, typed Pydantic input/output
models, read-only tools annotated as such, create_change_request and
update_ticket_status annotated destructive/non-idempotent, pagination
on search_incidents, explicit timeouts on every backing call, and a
typed error contract (never a bare stack trace back to the model).
Treat every tool response as untrusted — no tool result may contain
instructions the agent then blindly executes; document how you guard
against tool-response prompt injection.

Wire it to a mock backend (JSON fixtures are fine) representing
RxFlow's ticketing, incident, and ownership systems.

Then run the full operational loop: retrieve a defect via get_ticket,
search_incidents for prior occurrences, read the relevant runbook,
check service ownership, investigate the RxFlow repo, produce a patch,
prepare a change request via create_change_request — then stop and
request my explicit approval before calling anything that writes
externally — and only call update_ticket_status after the fix is
verified by tests.

Separately, add hooks at .claude/settings.json: a PreToolUse hook that
blocks any Bash command touching production database credentials, any
`git push --force`, and any read of files matching *.env or *secret*;
a PostToolUse hook that auto-runs ruff + mypy --strict on every edited
.py file and fails loudly (not silently) if either fails; and a hook
that appends an audit-log line (actor=claude, tool, target, timestamp)
for every AI-generated change. Keep every hook fast and deterministic
— no network calls inside a hook.

Finally, give me one command that a hook correctly blocks, let me see
the block, then bring the exact same intent into compliance so it
passes.

Stack
Layer
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


```

**Outcome:** a working ops connector with human approval enforced before any external write, and guardrails proven structural, not advisory.

---

## Java · LensForge — Ops MCP server + guardrail hooks

Server: Spring AI MCP or official Java SDK · Hooks: PreToolUse / PostToolUse

```
Build an MCP server in Java (Spring AI's MCP server support or the
official Java SDK) exposing: getTicket, searchIncidents,
getServiceOwner, getRunbook, getLabHealth, createChangeRequest, and
updateTicketStatus. Each tool: narrow responsibility, typed
request/response DTOs with Bean Validation, read-only tools clearly
annotated, createChangeRequest/updateTicketStatus annotated
destructive and non-idempotent unless an idempotency key is supplied,
pagination on searchIncidents, explicit timeouts on every downstream
call (RestClient/WebClient with a configured Duration), and a typed
error contract — no raw stack traces surfaced to the model. Document
explicitly how tool responses are treated as untrusted input, guarding
against prompt injection smuggled through a ticket description or
runbook body.

Back it with mock fixtures standing in for LensForge's ticketing,
incident, and service-ownership systems.

Then run the full operational loop: getTicket for a defect,
searchIncidents for prior occurrences, getRunbook for the affected
service, getServiceOwner, investigate the LensForge repo, produce a
patch, call createChangeRequest — then stop and require my explicit
approval before anything that writes externally — and call
updateTicketStatus only once the fix is verified by tests.

Add hooks at .claude/settings.json: a PreToolUse hook blocking any Bash
command touching prod DB credentials or Kubernetes prod context, any
`git push --force`, and any read of application-prod.yml or files
matching *secret*; a PostToolUse hook auto-running
`./mvnw spotless:check checkstyle:check` on every edited .java file,
failing loudly on violation; a hook logging every AI-generated change
(actor, tool, target, timestamp) to an audit file. Hooks must be fast,
deterministic, no network calls.

Then trigger one hook block on purpose, show me the block, and bring
the change into compliance.



Stack
Layer
Technology
API
Springboot
Domain
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


```

**Outcome:** a connector into Essilor's operational systems with approval-before-write structurally enforced, proven with a real block-and-fix cycle.

---

## .NET · OrderGateway — Ops MCP server + guardrail hooks

Server: ModelContextProtocol C# SDK · Hooks: PreToolUse / PostToolUse

```
Build an MCP server in C# using the official ModelContextProtocol .NET
SDK, exposing: GetTicket, SearchIncidents, GetServiceOwner, GetRunbook,
GetLabHealth, CreateChangeRequest, and UpdateTicketStatus. Each tool:
single narrow responsibility, typed request/response records with
data-annotation validation, read-only tools clearly annotated,
CreateChangeRequest/UpdateTicketStatus annotated destructive and
non-idempotent (require an idempotency key), pagination on
SearchIncidents, explicit HttpClient timeouts (with Polly) on every
downstream call, and a typed error contract — never an unhandled
exception surfaced raw to the model. Document explicitly how you treat
every tool response as untrusted, since a ticket description or
runbook body is an attacker-controlled channel into an agent with
terminal access.

Back it with mock JSON fixtures for OrderGateway's ticketing, incident,
and ownership systems.

Then run the full operational loop: GetTicket for a defect,
SearchIncidents for prior occurrences, GetRunbook for the affected
service, GetServiceOwner, investigate the OrderGateway repo, produce a
patch, call CreateChangeRequest — then stop and require my explicit
approval before anything that writes externally — and call
UpdateTicketStatus only after the fix is verified by xUnit tests.

Add hooks at .claude/settings.json: a PreToolUse hook blocking any Bash
command touching prod connection strings, any `git push --force`, and
any read of appsettings.Production.json or files matching *secret*; a
PostToolUse hook auto-running `dotnet format --verify-no-changes` and
the affected xUnit tests on every edited .cs file, failing loudly on
violation; a hook appending an audit-log line (actor, tool, target,
timestamp) for every AI-generated change. Hooks stay fast and
deterministic, no network calls.

Then deliberately trigger one hook block, show me exactly what fired
and why, and bring the change into compliance.
```

**Outcome:** a working .NET ops connector with approval-before-write enforced structurally, and a guardrail proven to actually stop something.
