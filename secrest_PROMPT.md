# Lab 8 — Secrets & Auth in Automation, Claude in GitHub Actions, and a Slash Command You'll Actually Reach For

Three things that only click once you've built them together: how a piece of
automation is allowed to prove who it is without a human typing a password
into it, what Claude does with that identity once it has it (reviewing a
PR, triaging why CI went red, proposing a patch), and how you turn "the
thing I type into Claude every single day" into a one-word command with a
result worth looking at.

This builds on [ci-guardian](../ci-guardian) — its MCP server and hooks
already exist; this lab is what makes it run *unattended*, on your real repo,
and adds a slash command that's yours specifically. Work through the phases
in order.

---

## Phase 0 — Secret management and authentication, done right

```
Before ci-guardian can act on venkatesh-db/Claude_AISolutions_Business
without a human present, it needs credentials it can prove and I need to
never see the secret itself. Do the following, in order:

1. Explain the three auth options for a GitHub automation — a classic PAT,
   a fine-grained PAT, and a GitHub App installation token — and recommend
   one for this repo specifically (public, single-owner, low-traffic).
   State the exact scopes/permissions needed for: reading PRs and CI runs,
   posting PR comments, opening draft PRs. Nothing broader.
2. Show me where that credential is allowed to live: a local .env (gitignored,
   never committed — verify .gitignore actually excludes it), GitHub Actions'
   own Secrets store for the workflow itself, and nowhere else. Grep the repo
   for anything that looks like a hardcoded token pattern before we go
   further, and report clean or not.
3. Add a pre-commit-style guard (extend ci-guardian's existing
   .claude/hooks/pre_bash_guard.py or add a sibling hook) that blocks any
   Bash command or file write containing something that looks like a GitHub
   token (ghp_, github_pat_, gho_ prefixes) — defense in depth against a
   credential accidentally landing in a commit.
4. Tell me exactly what to click to create the credential myself (I will not
   ask you to generate or handle the raw secret) and how to add it as a
   repo secret named CI_GUARDIAN_TOKEN in GitHub Actions settings.

Do not proceed to Phase 1 until a real credential exists as a GitHub Actions
secret — confirm its presence via the GitHub API (secret names are visible
via the API even though values never are), not by asking me to paste it
anywhere.
```

---

## Phase 1 — Claude in GitHub Actions, running for real

```
Write .github/workflows/ci-guardian.yml in
venkatesh-db/Claude_AISolutions_Business (or in ci-guardian's own repo if
that's the deploy target — confirm which with me first) wiring three jobs,
each a headless `claude -p ... --output-format json` call using
CI_GUARDIAN_TOKEN from GitHub Actions secrets, never echoed to logs:

1. PR review — on: pull_request [opened, synchronize]. Calls
   ci_guardian_get_pr_diff, reviews for correctness + missing test coverage
   only, posts findings via ci_guardian_post_pr_comment.
2. CI-failure triage — on: workflow_run [completed], if: conclusion ==
   'failure'. Calls ci_guardian_get_ci_status + ci_guardian_get_run_logs,
   diagnoses real regression vs. flaky vs. infra, posts a triage comment
   with evidence quoted from the log.
3. Patch proposal — manually triggered (workflow_dispatch) only, never
   automatic. Runs the mechanical-change loop from ci-guardian's Phase 5,
   opens a draft PR via ci_guardian_open_patch_pr. Requires a human to have
   clicked "Run workflow" — never fires from a PR event.

Push this workflow via a real PR (small, on a branch, reviewed like any
other change — don't push straight to main). Then trigger it for real:
open a tiny throwaway PR to fire job 1, and show me the actual bot comment
that lands, with a link.
```

---

## Phase 2 — the slash command: something you type most days

```
Ask me, in one short question, what I type into Claude most days — a
recurring instruction, a repeated multi-step ritual, whatever it is. Do not
guess or invent one.

Once I answer, build it as a real custom slash command:

1. Create the command file under .claude/commands/ (project-level) — a
   single, well-scoped prompt template with $ARGUMENTS where the command
   needs my input, following the same discipline as this project's other
   prompts: concrete, no vague "do the needful," explicit about what's read
   vs. written vs. asked-for-confirmation.
2. If the command's natural output is something worth looking at rather
   than reading as terminal text — a status board, a before/after diff, a
   small dashboard — design that as a proper artifact (load the
   artifact-design skill first, the same discipline used for ci-guardian's
   console) rather than dumping raw text. Match the visual treatment to
   what the command actually does; don't force a UI onto something that's
   genuinely just an answer.
3. Run the command for real, on real input, at least twice — show me both
   runs. The second run should look different from the first because the
   input was different, proving it's a live command and not a canned reply.
4. Write one line in the command file's own header comment explaining what
   it does and when to reach for it — this is the thing that makes you
   actually use it again next week instead of forgetting it exists.
```

---

## What "wow" means here, specifically

Not decoration — recognition. The slash command should feel like it was
built for the exact thing you do, not a generic template with your words
swapped in: real data, a UI treatment that matches the actual shape of the
output (a table if it's tabular, a diff if it's a diff, plain confirmation
text if that's genuinely all there is), and fast enough that reaching for it
beats typing the longhand version out again. If Phase 2 produces something
generic, that's the signal to stop and ask what's specific about how you
actually do this task, not to add more visual polish on top.
