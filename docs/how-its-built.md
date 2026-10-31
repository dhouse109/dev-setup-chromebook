# How it's built: the agent workflows, v94 to v98

Since v94 the bundle lives on GitHub, and every version goes through the same steps: a plan, a build, a
run on a real Chromebook, and a release. Two different teams of people and agents have done that work so
far. This page records who did what in each, so the history shows more than the code.

- **v94 to v97:** me, a Claude chat session, and **Claude Code in the cloud**.
- **v98:** me, a Claude chat session, and **Codex CLI running locally on the Chromebook**.

The README's [How it was built](../README.md#how-it-was-built) covers the longer history (the
Gemini-era script, then the move to Claude). The version-by-version notes are in
[CHANGELOG.md](../CHANGELOG.md).

## What both workflows share

- **The loop.** Plan (`docs/plans/vNN-plan.md`, on a `plan/vNN` branch with its own PR), build (on
  `release/vNN`, a PR into `main`), run on a Chromebook until `dev-test` shows FAIL 0, then merge, tag
  `vNN` and publish a GitHub Release.
- **Who decides.** I choose what goes into each version and make every plan choice. The agents diagnose,
  propose the choices (with one marked recommended), build, test, and review.
- **The rules.** One instruction file holds the repo's rules for whichever agent is working:
  `CLAUDE.md` through v97, then `AGENTS.md` from v98, with `CLAUDE.md` a symlink to it.
- **The referee.** `dev-test` on a real Chromebook. CI (`bash -n`, ShellCheck, gitleaks, the one-version
  check) catches the rest on every push.

## Who did what

| | v94 to v97: Claude Code in the cloud | v98: Codex locally |
| --- | --- | --- |
| **Coding agent** | Claude Code sessions in Anthropic's cloud, connected to the GitHub repo | Codex CLI in the Chromebook's Linux terminal (GPT-6.1 Sol, high reasoning), in a clone of the repo |
| **Claude chat session** | Planning and decisions in the claude.ai Project; worked out what to prompt Claude Code with | Wrote each Codex prompt and reviewed every plan round and the build diff from GitHub. Also did item 4 (`AGENTS.md`) itself and opened PRs #9 to #11 |
| **Me** | Made the plan choices, ran setup and `dev-test` on the Chromebooks, pasted the results back, reviewed and merged the PRs | Made the plan choices, relayed prompts between the chat session and Codex, approved each command Codex ran outside its sandbox, merged the PRs |
| **Diagnosis** | From what I pasted (the end of a run, error lines), the code and upstream checks | Codex read the run's saved screen output (`assets/logs/*.output`) itself and inspected the installed system read-only (`--version`, `command -v`, `du`) |
| **Testing during the build** | `bash -n`, ShellCheck, and stand-in or scratch-home tests in the cloud sandbox. The scripts' host guard stops them anywhere but ChromeOS, so the real runs were mine | The same checks, plus the real setup and `dev-test` runs: Codex ran them on the Chromebook after my approval of each command, read the output, and would have fixed and rerun on a failure |
| **Where commits come from** | Claude Code, with `Co-Authored-By` and `Claude-Session` trailers | Plan and build commits from Codex carry my local git identity and no agent trailer. They are listed below. From v98 on, `AGENTS.md` requires every agent commit to end with a co-author trailer naming the agent (`Co-authored-by: Codex <noreply@openai.com>` for Codex) |
| **Paid from** | Claude Code cloud usage credits (used up during v97) | The Codex allowance on my ChatGPT Pro plan |

## v94 to v97: Claude Code in the cloud

Each version was planned in a chat session, written into the repo as a plan PR, and built by a Claude Code
cloud session on its own branch:

| Version | Plan | Build | Run on a Chromebook |
| --- | --- | --- | --- |
| v94 | PR #1 (with the first `CLAUDE.md`) | PR #2 | `install-lazarus`: PASS 57, FAIL 0, WARN 1 (my qt5ct palette), IDE hand checks passed |
| v95 | PR #3 | PR #4 | clean run, then released |
| v96 | PR #5 | PR #6 | `install-editors install-web`: PASS 120, FAIL 0, WARN 0; fixes from the hand checks kept in v96 |
| v97 | PR #7 | PR #8 | four runs with fixes between them, the last PASS 126, FAIL 0, WARN 0 |

The cloud session couldn't run the scripts: the host guard at the top of each one exits on anything that
isn't ChromeOS. So every real run was mine. I ran it, pasted the end of `dev-test` (or the failing lines)
into the session, and the session diagnosed, fixed, pushed and asked for the next run. v97 made that
easier by saving each run's screen output to `assets/logs/<script>-<date-time>.output`.

## v98: Codex locally

v97 used up the Claude Code cloud credits, and setup had just failed to install DuckDB. That made v98 a
test: could a different coding agent, run locally, pick the work up from the repo alone?

**Getting ready (PR #9).** The chat session renamed `CLAUDE.md` to `AGENTS.md`, the file Codex reads,
and left `CLAUDE.md` as a symlink so both agents read the same rules. It added a section, "Where you are
running", that says what an agent may do when it runs on a Chromebook:

- Without asking, it can read the repo and `assets/logs/`, lint, and inspect the system read-only.
- It asks first before running any of the four scripts, using `sudo`, writing outside the repo, or
  starting heavy services.
- It never opens credential files, and never forces the host guard.

Codex ran in its own sandbox (`workspace-write`, approvals on request), so the sandbox enforces those
boundaries, not only the instructions.

**Plan rounds.** Each round was a prompt from the chat session, pasted into Codex by me. Codex then
committed and pushed to `plan/v98`, and the chat session reviewed the result from GitHub:

1. Diagnose (commit a1295b5). Codex read the failing run's output, found that the DuckDB CLI download
   returned 404, and traced it to DuckDB v2.0.0 renaming its release asset. The chat session had
   confirmed the same 404 and the renamed asset independently.
2. Widen the question (104bb76). Did the rest of the lakehouse stack (extensions, the Python wheel,
   dbt-duckdb, delta-rs, dbt Fusion, the ODBC driver) support DuckDB 2.0? Codex checked each read-only,
   recommended pinning to 1.5.6 until dbt Fusion states 2.0 support, and added item 6 (executable
   script modes).
3. Review fixes and decisions (ac1d691). Downloads skipped on reruns, the ODBC driver pinned to the
   same engine, staging cleaned up by trap, verification split by choice. I made every choice (all A)
   and the plan went final (PR #10).

**Build (PR #11).** A fresh Codex conversation built the plan in six commits, one per stage: 1152b0f
(DuckDB), 5d7087e (Cursor), b1bdd8b (DDEV images), 686f57d (Chrome shader caches), f2d45fd (docs),
b5ee0ef (script modes). It tested each stage with stand-ins or a scratch home in a temporary folder.
Then, with my approval for each command, it ran setup twice and `dev-test` with
`install-lakehouse install-db-extra`. The second setup run skipped both DuckDB downloads, and `dev-test`
passed: PASS 81, FAIL 0, WARN 0, SKIP 0, with no fixes needed (64dca52 records the run). The chat session
reviewed the full diff against the plan and `AGENTS.md` before the merge.

## What differed in practice

- **Who closes the run loop.** In the cloud, I was the courier: I ran the scripts and pasted the results
  back. Locally, the agent ran them, read the full output and could fix and rerun on its own. I approved
  each run, but no longer copied anything.
- **What the agent can see.** Locally, Codex read the actual system: the failing log, what was installed,
  which version answered. In the cloud, diagnosis depended on what I pasted.
- **Where the safety comes from.** The cloud sandbox is a separate machine, so nothing it does touches the
  Chromebook. Locally, the agent works on the machine that holds my logins, with passwordless `sudo`.
  There the safety comes from Codex's sandbox, my per-command approval of each setup run, and the
  `AGENTS.md` rules. Full-access or "bypass approvals" modes were deliberately not used.
- **Starting cold.** Codex had none of the v94 to v97 conversations. It worked from `AGENTS.md`, the plan,
  `docs/crostini-gotchas.md` and the changelog, which showed those files carry enough context on their
  own.
- **A second reviewer.** Splitting the work between two agents from different vendors meant the plan and
  the build were each reviewed by an agent that hadn't written them.
- **One data point.** v98 was small and well specified. That says Codex locally works for this repo; it
  doesn't yet say how the two compare on a large version.

## Repeating it

- Codex: start it in the repo with the top model at high reasoning (`model_reasoning_effort = "high"`),
  `sandbox_mode = "workspace-write"` and `approval_policy = "on-request"`. Approve setup and `dev-test`
  one command at a time, never "always".
- Give each version a fresh conversation for the build, after the plan rounds. The plan carries the
  context.
- Have the agent push to `plan/vNN` or `release/vNN` after each round, so the reviewing session reads it
  from GitHub instead of from screenshots.
- Check the first commit of a session ends with the agent's co-author trailer (`AGENTS.md`, Workflow).
  Codex adds its trailer by instruction, not by a git hook, so a missing one is worth catching early.
