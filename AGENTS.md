# AGENTS.md — dev-setup-chromebook

Guidance for coding agents working in this repository (Claude Code, Codex, or any other). Read this first,
then the plan for the version you are building (`docs/plans/vNN-plan.md`).

`CLAUDE.md` is a symlink to this file, so Claude Code and Codex read the same rules. Edit `AGENTS.md`;
never replace the symlink with a copy (v98: the bundle is now also worked on with Codex CLI, locally).

## What this repo is

A four-script bash bundle that turns the Linux environment on a Chromebook into a development machine.
It is a personal lab, published as is: kitchen sink, but tested. The owner decides what goes in and runs
every version on real Chromebooks; the coding agent drafts, reviews and fixes the bash.

| Script | Role |
|---|---|
| `dev-setup-chromebook.sh` | Installer. Unattended, idempotent, safe to rerun. |
| `dev-init-chromebook.sh` | Logins, API keys and config, read from `~/.config/dev-init/secrets.env`. |
| `dev-test-chromebook.sh` | Verifies every installed component works (PASS/FAIL/WARN/SKIP) and writes a per-stack disk report. |
| `dev-demo-chromebook.sh` | Optional. Installs runnable demos into `~/dev-demo`. Outside the test/checklist loop. |

All four take the **same flags** with the **same flag-expansion logic** (the `FLAG EXPANSION` block near
the top of each script: `install-all` → groups → members → dependencies). A flag added to one script is
added to all four, even if some only expand it.

Run order on a machine: **init → setup → init → test** (first init only writes the secrets template).

## Target environment

- ChromeOS Linux (Crostini container or the newer full Linux VM), **Debian 13 (trixie)**, x86-64.
- Chromebooks with 8 GB RAM; Linux sees about 6.4 GB. Heavy services run one at a time.
- Long-term machines (80 GB Linux disk, `/dev/kvm` present): tigerlake (board eldrid), yaviks, joxer.
- Quick-test machine (35 GB, no `/dev/kvm`, wiped often): dragonair; dragonair109 has about 10 GB less.
- No ChromeOS port forwarding any more: laptops reach each other over Tailscale (`install-lan`,
  `install-lan-share`), with `tailscaled` in normal (tun) mode, not userspace.
- Known Crostini differences and their fixes: `docs/crostini-gotchas.md`. Check it before "fixing"
  something that looks odd; it is often deliberate.

## Where you are running

Check this before running anything. The host guard at the top of every script exits on anything that
isn't ChromeOS + Debian, and **`DEV_BUNDLE_ANY_HOST=1` is never used to force it**, in either case below.

**In a cloud sandbox** (Claude Code on the web, Codex cloud, CI): this is not one of the Chromebooks. Do
not run setup, init, test or demo. Real runs happen on the Chromebooks; the owner pastes the end of a
`dev-test` run back into the session.

**Locally on one of the Chromebooks** (an agent started in the owner's terminal, such as Codex CLI or
Claude Code; the host guard's checks pass: `/dev/.cros_milestone` or `/opt/google/cros-containers`
exists, and `/etc/os-release` says Debian):

- Go ahead without asking: read anything in the repo, including `assets/logs/` (git-ignored, so read it
  by path; setup and test save their screen output there since v97 as `<script>-<date-time>.output`, and
  test writes a `.log` with the same date-time); `bash -n`, `shellcheck -S error`; read-only inspection (`<tool> --version`,
  `dpkg-query`, `command -v`, `du`, `docker ps`, `docker system df`).
- Ask the owner first: running `dev-setup`, `dev-init`, `dev-test` or `dev-demo` (they install, use
  `sudo`, start services, and take a long time), any other `sudo` command, and anything that writes
  outside the repo. When the owner runs a script, give the exact command and flags, and read its
  `.output` file afterwards instead of asking for a paste.
- If your sandbox blocks network or `sudo`, say so and hand the owner the command; don't look for a
  way around the sandbox.
- **Never open, print or copy credentials**: `~/.config/dev-init/secrets.env`, `~/.codex/auth.json`,
  `~/.claude/`, `gh`'s `hosts.yml`, `~/.ssh/`, cloud CLIs' config. To check a key is set, the scripts
  already report that without showing it.
- The machine is the owner's working machine with 8 GB RAM: don't start heavy services (Ollama models,
  database containers, Android emulator) to test something without asking.

## Rules that never change

1. **One version number for the bundle.** Any change to any script bumps **all four** to the same
   version, including scripts with no code change ("version bump only" in the changelog). The version
   string appears in several places; update every one:
   - line 2 of each script: `# dev-<name>-chromebook - Version NN`
   - setup: the "Starting comprehensive … (Version NN)" and "Setup Version NN complete!" lines
   - test: the "Testing … (Version NN)" and "Test Version NN complete" lines
   - init: the "Init Version NN complete" lines
   - demo: `VERSION=NN`
   After bumping, `grep -n 'Version [0-9]\+\|^VERSION=' dev-*.sh` must show only the new number.
2. **CHANGELOG.md** has one section per script (setup, test, init, demo), newest version first. Every
   version gets an entry under all four; a script with no change gets "version bump only".
3. **Code comments carry the why**, tagged with the version that added them and, for fixes, the dated
   finding (`# v94: … (Oct 24 2026: …)`). Keep existing tagged comments; they are the design record.
4. **Nothing loose in `$HOME`.** Files the scripts create for the user to keep (logs, downloads,
   generated helpers, disk-report TSVs) go in `./assets` next to the scripts (`$ASSETS`). Commands go in
   `~/.local/bin`; config in `~/.config/...`.
5. **Secrets only in `~/.config/dev-init/secrets.env`** (mode 600). Never in the scripts, never in the
   repo. `*_ONCE` values are used once and never exported.
6. **Every hosting-platform or cloud token is optional.** Installing never forces getting a key; init
   reports an unconfigured platform as a skip, not a todo.
7. **Setup is unattended and idempotent.** No interactive prompts in setup. Each step is guarded so a
   rerun skips what is done and a hand-configured machine is brought into line, not clobbered.
8. **Homebrew goes last on PATH** so its dependencies (python3, sqlite3, openjdk, binutils) never shadow
   Debian's.
9. **Downloads are verified** where the vendor publishes a checksum, and validated (`gzip -t`,
   `dpkg-deb --info`, a test run) before they replace anything. Prefer reading installed versions
   (`dpkg-query`) over hardcoding them in paths.
10. **Scope:** CLIs and system-level tools belong here behind flags. SDKs and frameworks used by one
    project stay per-project and out of the bundle. Windows is a separate repo (`dev-setup-windows`);
    don't make these scripts platform-aware.
11. **Bring your own media.** Never add downloads of Windows, DOS, Delphi, InterBase or other licensed
    media; the scripts install only from files the user places in the named folders.

## When you change a flag or a stack

Update, in the same change:
- all four scripts (flag expansion at minimum)
- `dev-test`: checks for the new behaviour (`check` = FAIL if missing, `warn` for user-changeable
  settings), and the disk report's line for that stack
- `docs/init-checklist.md`: run order, flags, secrets variables, manual steps
- `docs/dev-demo.md` if the demo changed (what it does, downloads, disk footprint)
- `README.md`: the flag tables, and "Current version: vNN"
- `docs/crostini-gotchas.md` if the change works around a ChromeOS difference
- `CHANGELOG.md` (all four sections)

## Workflow

- **Plans first.** Each version is planned in `docs/plans/vNN-plan.md` before it is built. The owner
  approves plan choices; if the plan doesn't settle something, ask rather than guess.
- **One branch per version** (`release/vNN`), PR into `main`. Plans go in on their own branch
  (`plan/vNN`). Never name a branch plain `vNN`: that is the release tag, and a branch with the same name
  makes `git checkout vNN` ambiguous (it happened with v94). Large versions can be built in stages, one
  commit per stage.
- **Every commit an agent makes says which agent made it**, with a co-author trailer at the end of
  the message, after a blank line. A local agent commits under the owner's git name and email, so
  without the trailer its work looks like the owner's own (v98: Codex's commits had none; they are
  listed in `docs/how-its-built.md`).
  - Claude Code: `Co-Authored-By: Claude <model> <noreply@anthropic.com>`, plus the `Claude-Session:`
    line its session asks for.
  - Codex: `Co-authored-by: Codex <noreply@openai.com>` (Codex's own default trailer, set by
    `commit_attribution` in `~/.codex/config.toml`). Add it yourself even when that setting is on, since
    Codex applies it through the prompt, not a git hook.
  - Any other agent: `Co-Authored-By: <agent name> <its vendor's noreply address>`.
  - Commits the owner makes by hand get no trailer. Never rewrite pushed commits to add one.
- **Checks before every push** (CI runs the same in `.github/workflows/lint.yml`):
  - `bash -n` on each script
  - `shellcheck -S error dev-*-chromebook*.sh` (warnings are left for comments to explain)
  - no secrets (gitleaks runs in CI; `.gitleaks.toml` has the two known false positives)
- **A version isn't done until its `dev-test` run on a Chromebook is clean** (FAIL 0; WARNs only for
  optional credentials). Until then, describe it as "built, not yet confirmed run on a Chromebook".
- **Release:** after a clean run, merge, delete the merged branch, tag `vNN`, and publish a GitHub
  Release with the changelog entry. Fixes found during a version's own testing can be kept in that version if the owner says so.
- The scripts are large (setup ~9,100 lines, demo ~10,700). Make targeted edits; never regenerate a
  whole script.

## Known open items

None.
