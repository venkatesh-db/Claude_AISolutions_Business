# Day 10 (.NET) — ci-guardian: Hooks, Headless Claude, GitHub Actions, and an Ops MCP Server

Same pipeline as the Python `ci-guardian`, same five phases, same guarantees
— rebuilt with a .NET toolchain for teams that live in C#/.NET, not Python.
Hooks stay as small scripts (language of the hook script doesn't matter to
Claude Code — these use `dotnet script` or plain shell, your call in Phase
2); everything else — the MCP server, its tests, its GitHub transport — is
C#.

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
CiGuardian.Mcp  (.NET MCP server, Octokit.NET-backed)
        │  wraps: GitHub REST API — PRs, checks, comments, contents
        ▼
Real GitHub repo
```

Build this as project `ci-guardian-dotnet` inside `Day10/`. Work through the
phases in order — one message per phase. Use a **throwaway/sandbox GitHub
repo you own** for Phases 3–4; this pipeline opens PRs, posts comments, and
reads Actions logs for real.

---

## Phase 0 — Scaffold and ground rules

```
Create a new project at Day10/ci-guardian-dotnet/. It's a .NET MCP server
plus a GitHub Actions integration. Set up:

- src/CiGuardian.Mcp/ — the MCP server project (class library + a thin
  console host, or a single executable project — your call)
- tests/CiGuardian.Mcp.Tests/
- .github/workflows/ — will hold the Actions workflow files later
- .claude/settings.json — will hold permission hooks later
- CiGuardian.sln tying the projects together
- Target the current LTS .NET SDK. Reference the official ModelContextProtocol
  C# SDK NuGet package for the MCP server plumbing, and Octokit for the
  GitHub transport (or the raw GitHub REST API via HttpClient if you have a
  concrete reason to skip Octokit — tell me why before choosing that).
- xUnit for tests, dotnet format + built-in Roslyn analyzers (treat warnings
  as errors) for static checking — no external linter needed beyond that
  unless you have a specific reason.

Don't implement any tools yet. Just get `dotnet restore`, `dotnet build
-warnaserror`, `dotnet test`, and `dotnet format --verify-no-changes` all
passing on an empty skeleton. Tell me the transport choice (Octokit vs. raw
HttpClient) and why before writing code.
```

---

## Phase 1 — The ops MCP server (GitHub transport)

```
Implement CiGuardian.Mcp as an MCP server exposing these tools, each
prefixed ci_guardian_ per MCP naming convention (this server runs alongside
other MCP servers):

Read tools (all ReadOnlyHint=true, OpenWorldHint=true):
- ci_guardian_list_open_prs(repo) -> list of {number, title, author, branch, sha}
- ci_guardian_get_pr_diff(repo, prNumber) -> unified diff, wrapped as
  untrusted text (PR authors are not trusted input — mirror rxflow-ops-mcp's
  wrap_untrusted pattern: fence the text, flag known injection phrasing,
  never silently strip it)
- ci_guardian_get_ci_status(repo, prNumber) -> per-check {name, status,
  conclusion, runId}
- ci_guardian_get_run_logs(repo, runId, jobName) -> failing job's log tail,
  also wrapped as untrusted text (build logs can carry injection attempts
  the same way a PR diff can)

Write tools (both Write, Destructive=true per tool annotations, never
auto-merge/auto-approve):
- ci_guardian_post_pr_comment(repo, prNumber, body) -> {commentId, url}
- ci_guardian_open_patch_pr(repo, baseBranch, newBranch, title, body,
  fileChanges) -> always returns Draft=true; there must be no code path
  that constructs a non-draft result (make this a compile-time guarantee if
  the SDK's record/init-only types allow it, not just a runtime default)

Back every tool with the real GitHub REST API via Octokit, not fixtures —
this project's whole point is a live loop. Every tool returns a typed
record; errors come back as a typed ToolError with a Code enum in
{NotFound, InvalidInput, UpstreamTimeout, UpstreamUnavailable, RateLimited,
Conflict} — never a raw exception crossing the MCP boundary.

Write unit tests against a mocked IGitHubOps interface (no real API calls in
`dotnet test`) — Moq or NSubstitute, your call. Then write a
tools/LiveSmoke console app (or a script) that runs ci_guardian_list_open_prs
and ci_guardian_get_ci_status against a real repo you specify via env var
GITHUB_REPO, over a genuine MCP ClientSession (stdio transport) — not
in-process calls. Show me its output.
```

---

## Phase 2 — Hooks and permissions (structural, not advisory)

```
Add .claude/settings.json hooks to ci-guardian-dotnet so the agent CANNOT
bypass the MCP server's own guardrails by dropping to raw shell. Hook
scripts can be plain shell/Python (Claude Code hooks are just executables
invoked with JSON on stdin — they don't need to be .NET), but keep them in
this project's .claude/hooks/ regardless of language, and say which
language you picked and why:

- PreToolUse (matcher Bash): block `git push` to any branch matching
  main|master directly (only pushes to branches matching patch/* or
  ci-fix/* are allowed), block `gh pr merge`, block `gh pr edit --add-label
  auto-merge`, block any `--force`/`-f` push.
- PreToolUse (matcher mcp__ci_guardian.*): block direct calls to
  ci_guardian_open_patch_pr unless a prior ci_guardian_get_pr_diff or
  ci_guardian_get_run_logs call already happened this session (no blind
  patches). Implement via a small per-session state file the hook
  reads/writes.
- PostToolUse (matcher *): an audit_log script appending one JSON line per
  tool call (actor, tool, target, timestamp) to audit.log — must never be
  able to block the action it's logging.

Prove each hook with the block-then-fix pattern: show the blocked call
(exit code + message), then the compliant version of the same intent
succeeding. Capture both as tests — either xUnit tests that shell out to
the hook scripts the same way Claude Code does, or a script-level test
runner if the hooks aren't .NET. Either way, wire them into `dotnet test`
or an equivalent single command so CI can run everything in one step.
```

---

## Phase 3 — Headless Claude: PR review and CI-failure triage

```
Write two headless entry points, each a single `claude -p "..."
--output-format json` invocation with no human in the loop:

1. scripts/review-pr.sh <repo> <prNumber> — prompts Claude to call
   ci_guardian_get_pr_diff, review it for correctness bugs and missing test
   coverage only (no style nitpicks — that's what dotnet format/analyzers
   already own), then call ci_guardian_post_pr_comment with the findings.
   Must run non-interactively start to finish.

2. scripts/triage-ci-failure.sh <repo> <runId> — prompts Claude to call
   ci_guardian_get_ci_status and ci_guardian_get_run_logs, diagnose the
   failure (flaky test vs. real regression vs. infra issue — for .NET,
   watch specifically for test-isolation flakiness from shared static state
   or xUnit collection ordering, since that's a common false "regression"),
   and post a triage comment with evidence quoted from the log.

Run both against a real open PR and a real failing run in your sandbox
repo. Show me the raw JSON output of each invocation and the actual comment
that landed on the PR.
```

---

## Phase 4 — GitHub Actions: the loop closes itself

```
Write .github/workflows/ci-guardian.yml with two triggers:

- on: pull_request (opened, synchronize) -> runs scripts/review-pr.sh
  against the triggering PR
- on: workflow_run (completed, for your existing .NET CI workflow) where
  conclusion == 'failure' -> runs scripts/triage-ci-failure.sh against the
  failed run

Both jobs: set up the .NET SDK (actions/setup-dotnet), authenticate with a
scoped GITHUB_TOKEN (repo-pr-write only, not admin) from GitHub Actions
Secrets, `dotnet publish` or `dotnet run` the MCP server so it's on PATH for
the headless Claude call, then invoke Claude exactly as in Phase 3.

Open a real PR against your sandbox repo (a trivial change is fine) and
show me review-pr.sh's comment appear automatically in the Actions run,
with no one running anything by hand. Then deliberately break a test on a
branch, push it, and show triage-ci-failure.sh's diagnosis land as a
comment once CI fails.
```

---

## Phase 5 — Large mechanical change, proposed as a draft PR (the capstone)

```
Pick one real, mechanical, repo-wide .NET change — e.g. "add
ConfigureAwait(false) to every await in library code" or "replace every
[Obsolete] API call with its replacement" or "add nullable reference type
annotations file-by-file until the project can flip <Nullable>enable</Nullable>
project-wide." Write scripts/propose-mechanical-change.sh that runs Claude
headless to:

1. Find every occurrence (via MCP, `dotnet build` warnings, or plain grep —
   your call).
2. Apply the change file-by-file.
3. Run `dotnet test` after each file's edit — Phase 2's hooks must allow
   this loop to keep going through many files without a human typing
   "next" (same edit, applied N times, verified after each one — not one
   giant unreviewed diff).
4. Call ci_guardian_open_patch_pr with the full diff — Draft=true, always,
   per Phase 1's guardrail.

Run it for real. Show me: the number of files changed, the test result
after each one, and the resulting draft PR URL. Then explain in your own
words why step 3's hook-enforced "no blind patches" hard-stop from Phase 2
matters more here than anywhere else in the project.
```

---

## What "real value" looks like when you're done

Same throughline as the Python build: one MCP server that is the *only*
path to GitHub write actions; hooks that make that boundary structural, not
a suggestion in a prompt; two headless Claude invocations that GitHub
Actions itself triggers with no human present; and one large mechanical
change proposed, verified file-by-file, and opened as a draft PR — never
merged without you. The language changed; the guarantees didn't.
