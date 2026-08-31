# Day 10 (Java) — ci-guardian: Hooks, Headless Claude, GitHub Actions, and an Ops MCP Server

Same pipeline, same five phases, same guarantees as the Python `ci-guardian`
— rebuilt with a Java toolchain for teams that live in Java/Spring, not
Python. Hooks stay as small scripts (Claude Code hooks are just executables
invoked with JSON on stdin — they don't need to be JVM code); everything
else — the MCP server, its tests, its GitHub transport — is Java.

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
ci-guardian-mcp  (Java MCP server, GitHub API-backed)
        │  wraps: GitHub REST API — PRs, checks, comments, contents
        ▼
Real GitHub repo
```

Build this as project `ci-guardian-java` inside `Day10/`. Work through the
phases in order — one message per phase. Use a **throwaway/sandbox GitHub
repo you own** for Phases 3–4; this pipeline opens PRs, posts comments, and
reads Actions logs for real.

---

## Phase 0 — Scaffold and ground rules

```
Create a new project at Day10/ci-guardian-java/. It's a Java MCP server
plus a GitHub Actions integration. Set up:

- src/main/java/com/ciguardian/mcp/ — the MCP server package
- src/test/java/com/ciguardian/mcp/
- .github/workflows/ — will hold the Actions workflow files later
- .claude/settings.json — will hold permission hooks later
- Maven (pom.xml) or Gradle (build.gradle.kts) — your call, tell me which
  and why for a small single-module server like this.
- Target a current LTS JDK (21). Reference the official Java MCP SDK
  (io.modelcontextprotocol.sdk:mcp) for the server plumbing, and either the
  hub4j `github-api` client or a plain java.net.http.HttpClient wrapper for
  GitHub's REST API — your call, tell me why.
- JUnit 5 for tests, Checkstyle or Spotless for formatting, and
  SpotBugs/Error Prone for static analysis — pick a minimal set that
  actually catches something, don't cargo-cult every tool.

Don't implement any tools yet. Just get the build (`mvn verify` or `gradle
build`), the test run, and the static-analysis/format checks all passing on
an empty skeleton. Tell me the build tool and GitHub-transport choice and
why before writing code.
```

---

## Phase 1 — The ops MCP server (GitHub transport)

```
Implement ci-guardian-mcp as an MCP server exposing these tools, each
prefixed ci_guardian_ per MCP naming convention (this server runs alongside
other MCP servers):

Read tools (all readOnlyHint=true, openWorldHint=true):
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

Write tools (both write, destructive=true per tool annotations, never
auto-merge/auto-approve):
- ci_guardian_post_pr_comment(repo, prNumber, body) -> {commentId, url}
- ci_guardian_open_patch_pr(repo, baseBranch, newBranch, title, body,
  fileChanges) -> always returns draft=true. Model the result type so a
  non-draft result cannot be constructed at all — a sealed interface /
  record with `draft` fixed to `true` rather than a mutable boolean field
  someone could flip.

Back every tool with the real GitHub REST API, not fixtures — this
project's whole point is a live loop. Every tool returns a typed record;
errors come back as a typed ToolError with a Code enum in {NOT_FOUND,
INVALID_INPUT, UPSTREAM_TIMEOUT, UPSTREAM_UNAVAILABLE, RATE_LIMITED,
CONFLICT} — never a raw exception crossing the MCP boundary.

Write unit tests against a mocked GitHubOps interface (Mockito; no real API
calls in the normal test run). Then write a small LiveSmoke main class (or
script) that runs ci_guardian_list_open_prs and ci_guardian_get_ci_status
against a real repo you specify via env var GITHUB_REPO, over a genuine MCP
client session (stdio transport) — not in-process calls. Show me its
output.
```

---

## Phase 2 — Hooks and permissions (structural, not advisory)

```
Add .claude/settings.json hooks to ci-guardian-java so the agent CANNOT
bypass the MCP server's own guardrails by dropping to raw shell. Hook
scripts can be plain shell/Python (they don't need to be JVM code), but
keep them in this project's .claude/hooks/ regardless of language, and say
which language you picked and why:

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
succeeding. Capture both as JUnit tests that shell out to the hook scripts
the same way Claude Code does (ProcessBuilder, same stdin/exit-code
contract), wired into the normal build so `mvn verify`/`gradle build` runs
everything in one step.
```

---

## Phase 3 — Headless Claude: PR review and CI-failure triage

```
Write two headless entry points, each a single `claude -p "..."
--output-format json` invocation with no human in the loop:

1. scripts/review-pr.sh <repo> <prNumber> — prompts Claude to call
   ci_guardian_get_pr_diff, review it for correctness bugs and missing test
   coverage only (no style nitpicks — that's what Checkstyle/Spotless
   already own), then call ci_guardian_post_pr_comment with the findings.
   Must run non-interactively start to finish.

2. scripts/triage-ci-failure.sh <repo> <runId> — prompts Claude to call
   ci_guardian_get_ci_status and ci_guardian_get_run_logs, diagnose the
   failure (flaky test vs. real regression vs. infra issue — for Java,
   watch specifically for classpath/dependency-resolution failures and
   test-order flakiness from shared static state, since those commonly get
   misdiagnosed as "the code is broken"), and post a triage comment with
   evidence quoted from the log.

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
- on: workflow_run (completed, for your existing Java CI workflow) where
  conclusion == 'failure' -> runs scripts/triage-ci-failure.sh against the
  failed run

Both jobs: set up the JDK (actions/setup-java), authenticate with a scoped
GITHUB_TOKEN (repo-pr-write only, not admin) from GitHub Actions Secrets,
build/package the MCP server (a fat/shaded jar is simplest) so it's runnable
for the headless Claude call, then invoke Claude exactly as in Phase 3.

Open a real PR against your sandbox repo (a trivial change is fine) and
show me review-pr.sh's comment appear automatically in the Actions run,
with no one running anything by hand. Then deliberately break a test on a
branch, push it, and show triage-ci-failure.sh's diagnosis land as a
comment once CI fails.
```

---

## Phase 5 — Large mechanical change, proposed as a draft PR (the capstone)

```
Pick one real, mechanical, repo-wide Java change — e.g. "replace every raw
RestTemplate.getForObject call with the retrying client in http/RetryingHttpClient"
or "add @NonNull/@Nullable annotations file-by-file" or "migrate every
JUnit4 @Test to JUnit5." Write scripts/propose-mechanical-change.sh that
runs Claude headless to:

1. Find every occurrence (via MCP, a build-tool report, or plain grep —
   your call).
2. Apply the change file-by-file.
3. Run the test suite (`mvn test` / `gradle test`) after each file's edit —
   Phase 2's hooks must allow this loop to keep going through many files
   without a human typing "next" (same edit, applied N times, verified
   after each one — not one giant unreviewed diff).
4. Call ci_guardian_open_patch_pr with the full diff — draft=true, always,
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
