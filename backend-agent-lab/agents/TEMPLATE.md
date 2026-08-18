# Agent instruction template

Every agent in this system uses this exact structure. Consistency here
is what makes the orchestrator able to treat all 9 uniformly — it reads
each agent's `Reads from` / `Writes to` sections to wire the pipeline,
rather than special-casing each agent's I/O.

```markdown
# Agent: <name>

## Role
One sentence: what this agent decides that no other agent decides.

## Reads from
- knowledge/<folder>/ — what it needs from the knowledge base
- evidence/<prior-agent-output>.json — what it needs from earlier agents

## Writes to
- evidence/<this-agent>.json — structured, so the next agent (and the
  orchestrator) can consume it without re-parsing prose

## Gate condition
What must be true for this agent's output to be considered complete —
not "looks reasonable," a checkable condition.

## Prohibited
What this agent must never do, stated explicitly — usually: don't
invent data the knowledge base doesn't have; don't perform an action
another agent owns.

## On missing evidence
What happens when this agent can't produce its output because an input
is missing — must never be "proceed with a plausible guess."
```
