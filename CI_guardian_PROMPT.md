# Day 10 — ci-guardian: Hooks, Headless Claude, GitHub Actions, and an Ops MCP Server (one project)

Day 9's prompts (`sub-agents-hooks-ci-prompts.md`) taught each concept in isolation,
on toy commands. Day 10 wires the same four concepts into **one real pipeline**
so you can see how they actually compose in production:

```
GitHub PR opened / CI run fails
        │
        ▼
GitHub Actions workflow (.github/workflows/*.yml)
        │  runs `claude -p "..." --output-format json`  ← headless Claude
        ▼
Claude Code session, permission-limited by .claude/settings.json hooks
        │  calls MCP tools instead of raw `gh`/`git` commands
        ▼
ci-guardian-mcp  (Python MCP server, github plugin backend)
        │  wraps: gh api, gh pr diff, gh run view --log, gh pr comment
        ▼
Real GitHub repo
```

Build this as project `ci-guardian` inside `Day10/`. Work through the phases
in order — each phase produces something the next phase depends on. Give each
phase to Claude as its own message; don't paste the whole file at once.

Use a **throwaway/sandbox GitHub repo you own** for the live-fire phases
(3 and 4) — this pipeline opens PRs, posts comments, and reads Actions logs
for real. Do not point it at a repo you don't control or a shared team repo
on your first run.

---

## Phase 0 — Scaffold and ground rules

```
Create a new project at Day10/ci-guardian/. It's a Python MCP server plus a
GitHub Actions integration. Set up:

- src/ci_guardian_mcp/ — the MCP server package
- tests/
- .github/workflows/ — will hold the Actions workflow files later
- .claude/settings.json — will hold permission hooks later
- pyproject.toml with the mcp Python SDK, PyGithub or the gh CLI as the
  GitHub transport (your call — tell me which and why), pytest, ruff, mypy

Don't implement any tools yet. Just get `pip install -e ".[dev]"`,
`pytest -q`, `ruff check .`, and `mypy --strict src/` all passing on an
empty skeleton. Tell me the tool-transport choice and why before writing
code.
```

---

## Phase 1 — The ops MCP server (github plugin)

```
Implement ci_guardian_mcp as an MCP server exposing these tools, each
prefixed ci_guardian_ per MCP naming convention (this server runs alongside
other MCP servers):

Read tools (all readOnlyHint=True, openWorldHint=True):
- ci_guardian_list_open_prs(repo) -> list of {number, title, author, branch, sha}
- ci_guardian_get_pr_diff(repo, pr_number) -> unified diff, wrapped as
  untrusted text (PR authors are not trusted input — see rxflow-ops-mcp's
  security.wrap_untrusted pattern for why and how)
- ci_guardian_get_ci_status(repo, pr_number) -> per-check {name, status,
  conclusion, run_id}
- ci_guardian_get_run_logs(repo, run_id, job_name) -> failing job's log tail,
  also wrapped as untrusted text (build logs can contain injection attempts
  the same way ticket text can)

Write tools (both write, destructive=True per ToolAnnotations, never
auto-merge/auto-approve):
- ci_guardian_post_pr_comment(repo, pr_number, body) -> {comment_id, url}
- ci_guardian_open_patch_pr(repo, base_branch, new_branch, title, body,
  file_changes) -> always returns draft=True; never opens a non-draft PR

Back every tool with the real GitHub REST/GraphQL API (via the transport
chosen in Phase 0), not fixtures — this project's whole point is a live
loop, unlike the fixture-backed rxflow-ops-mcp. Every tool returns a typed
Pydantic model; errors come back as a typed ToolError with code in
{not_found, invalid_input, upstream_timeout, upstream_unavailable,
rate_limited, conflict} — never a raw exception.

Write unit tests against a mocked GitHub client (no real API calls in
`pytest -q`). Then write scripts/live_smoke.py that runs
ci_guardian_list_open_prs and ci_guardian_get_ci_status against a real repo
you specify via env var GITHUB_REPO, over a genuine mcp.ClientSession
(stdio transport) — not in-process calls. Show me its output.
```

---

## Phase 2 — Hooks and permissions (structural, not advisory)

```
Add .claude/settings.json hooks to ci-guardian so the agent CANNOT bypass
the MCP server's own guardrails by dropping to raw shell:

- PreToolUse (matcher Bash): block `git push` to any branch matching
  main|master directly (only pushes to branches matching patch/* or
  ci-fix/* are allowed), block `gh pr merge`, block `gh pr edit --add-label
  auto-merge`, block any `--force`/`-f` push.
- PreToolUse (matcher mcp__ci_guardian.*): block direct calls to
  ci_guardian_open_patch_pr unless a prior ci_guardian_get_pr_diff or
  ci_guardian_get_run_logs call already happened this session (i.e. no
  blind patches — the agent must have actually looked at the diff/logs
  first). Implement this via a small state file the hook reads/writes.
- PostToolUse (matcher *): audit_log.py appending one JSON line per tool
  call (actor, tool, target, timestamp) to audit.log — this is what a human
  reviews after an autonomous run, so it must never itself be able to block
  the action it's logging.

Prove each hook with the same block-then-fix pattern as rxflow-ops-mcp:
show the blocked call (exit code + message), then the compliant version of
the same intent succeeding. Capture both as tests in tests/test_hooks.py.
```

---

## Phase 3 — Headless Claude: PR review and CI-failure triage

```
Write two headless entry points, each a single `claude -p "..."
--output-format json` invocation with no human in the loop:

1. scripts/review_pr.sh <repo> <pr_number> — prompts Claude to call
   ci_guardian_get_pr_diff, review it for correctness bugs and missing test
   coverage only (reuse the review-scope discipline from Day 9's sub-agent
   prompt — no style nitpicks), then call ci_guardian_post_pr_comment with
   the findings. Must run non-interactively start to finish.

2. scripts/triage_ci_failure.sh <repo> <run_id> — prompts Claude to call
   ci_guardian_get_ci_status and ci_guardian_get_run_logs, diagnose the
   failure (flaky test vs. real regression vs. infra issue), and post a
   triage comment on the associated PR explaining which, with evidence
   quoted from the log.

Run both against a real open PR and a real failing run in your sandbox
repo. Show me the raw JSON output of each invocation and the actual comment
that landed on the PR. This is the "no human present" property from Day
9's headless prompt, but now doing something with real consequences instead
of running a test script.
```

---

## Phase 4 — GitHub Actions: the loop closes itself

```
Write .github/workflows/ci-guardian.yml with two triggers:

- on: pull_request (opened, synchronize) -> runs scripts/review_pr.sh
  against the triggering PR
- on: workflow_run (completed, for your existing CI workflow) where
  conclusion == 'failure' -> runs scripts/triage_ci_failure.sh against the
  failed run

Both jobs authenticate with a scoped GITHUB_TOKEN (repo-pr-write only, not
admin), install ci-guardian-mcp, and invoke Claude headlessly exactly as in
Phase 3 — same scripts, now triggered by GitHub's event system instead of
your terminal.

Open a real PR against your sandbox repo (a trivial change is fine) and
show me review_pr.sh's comment appear automatically in the Actions run,
with no one running anything by hand. Then deliberately break a test on a
branch, push it, and show triage_ci_failure.sh's diagnosis land as a
comment once CI fails.
```

---

## Phase 5 — Large mechanical change, proposed as a draft PR (the capstone)

```
Pick one real, mechanical, repo-wide change in your sandbox repo — e.g.
"replace every `requests.get(...)` call with the retrying wrapper in
utils/http.py" or "add a return-type annotation to every public function in
src/". Write scripts/propose_mechanical_change.sh that runs Claude headless
to:

1. Find every occurrence (via MCP or plain grep — your call).
2. Apply the change file-by-file.
3. Run the test suite after each file's edit — hooks from Phase 2 must
   allow this loop to keep going through many files without a human typing
   "next" (this is the "Large Mechanical Change" pattern: same edit,
   applied N times, verified after each one, not one giant unreviewed diff).
4. Call ci_guardian_open_patch_pr with the full diff — draft=True, always,
   per Phase 1's guardrail.

Run it for real. Show me: the number of files changed, the test result
after each one, and the resulting draft PR URL. Then explain in your own
words why step 3's hook-enforced "no blind patches" hard-stop from Phase 2
matters more here than anywhere else in the project.
```

---

## What "real value" looks like when you're done

You should be able to point at:
- one MCP server that is the *only* path to GitHub write actions,
- hooks that make that boundary structural rather than a suggestion in a
  prompt,
- two headless Claude invocations that GitHub Actions itself triggers with
  no human present,
- and one large mechanical change that got proposed, verified file-by-file,
  and opened as a draft PR — never merged without you.

That last property — drafts and `pending_approval`-style gates everywhere a
write could cause real damage — is the throughline from `rxflow-ops-mcp`
carried into a pipeline that touches a real GitHub repo instead of fixtures.
