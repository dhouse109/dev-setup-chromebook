# dev-setup-chromebook v101 plan

Nov 8, 2026 · **draft: scope only; owner choices pending**

v101 starts from v100 (released Nov 8, 2026, tag `v100`). This file records the items carried
forward from v100 and the owner's new request (item 1). Each item gives the finding, what is
already known and what the detailed plan must settle. Owner choices are recorded here before the
build starts, as for v100.

## Items at a glance

| # | Item | Kind |
|---|---|---|
| 1 | Release archives must extract in ChromeOS's Files app (the `CLAUDE.md` symlink) | fix (owner priority) |
| 2 | Inspector offline cache coherence (v100 item 1) | fix (investigate first) |
| 3 | Windows 2000 on nested KVM, and working Windows 2000 sound | investigate, then fix |
| 4 | Diagnostics for dev-test's intermittent "QEMU starts a blank disk headless" timeout | test fix |
| 5 | winnt40: first install and v100 item 8's fresh-install acceptance | acceptance |
| 6 | DOSBox-X full-screen profile and the renderer-preference WARN | default/docs |
| 7 | win95: OLEnterprise's Object Agent needs DOSBox-X's normal core | docs, maybe a setting |
| 8 | Guest network test plan | test plan |
| 9 | Delphi DCOM / multi-tier database demo | demo (largest; may be staged across versions) |

Items 8 and 9 depend on `install-lan-share` and `install-db-server`; their v100 write-ups (end of
`docs/plans/v100-plan.md`) are the starting point and are summarized here.

## 1. Release archives must extract in ChromeOS's Files app

- **Finding (Nov 8):** the v100 release's source zip fails in ChromeOS's Files app ("Extract
  operation failed. An error occurred.") after extracting only part of the tree. `unzip` in Linux
  extracts everything, reporting `linking: CLAUDE.md -> AGENTS.md`. `CLAUDE.md` is a symlink to
  `AGENTS.md` since v98 and is the only symlink in the repository; ChromeOS's extractor doesn't
  handle it.
- **Owner request:** the release zip must extract in ChromeOS's Files app without errors. The owner
  had wanted this fixed earlier and it was not in the v100 plan.
- **Options for the plan to compare:**
  - **A:** replace the symlink with a regular `CLAUDE.md` whose content imports the shared rules
    (Claude Code's `@AGENTS.md` import), so Claude Code and Codex still read one set of rules and
    every archive format and OS sees an ordinary file. Update AGENTS.md's "never replace the symlink"
    rule and `docs/how-its-built.md`.
  - **B:** keep the symlink and exclude it from release archives (`.gitattributes`:
    `CLAUDE.md export-ignore`); archives then contain no `CLAUDE.md` at all.
  - The plan should verify, before recommending, that Claude Code loads `AGENTS.md` through the
    import in this repo, and that Codex is unaffected.
- **Also settle:** a CI check that fails when the tree contains a symlink (mode `120000` in
  `git ls-files -s`), so this cannot come back; how to verify (an archive built with
  `git archive --format=zip`, extracted in ChromeOS's Files app by the owner).

## 2. Inspector offline cache coherence (from v100 item 1)

Carry forward v99's accepted known issue: the offline npx Inspector cache can return ENOTCACHED at
test time despite a successful warm-up. The retained investigation design is in v100's item 1. It
needs a machine set up with the bundle's own `install-agentic`; v100 found that a hand-built
environment would not reproduce the bundle's context. Every real command needs the owner's approval.

## 3. Windows 2000 on nested KVM, and working sound

- **Findings (Nov 5–7):** under ChromeOS's nested `/dev/kvm`, Windows 2000 stalls at
  "Starting up…" with QEMU above 100% CPU, the splash painting slowly. This happens during Setup's
  first graphical boot **and on the installed system**; TCG works. v100 therefore defaults win2000
  to TCG.
- **Sound (Nov 7):** QEMU's `pa` backend floods the terminal with
  `set_sink_input_volume() failed … Invalid argument` (PipeWire's pulse server). The installed QEMU
  offers a native `pipewire` audiodev. With `-audiodev pipewire,id=snd1 -device sb16,audiodev=snd1`
  the errors stop, and Windows 2000's own "Sound Blaster 16 or AWE32 or compatible (WDM)" driver
  plays sound, but it stutters and lags under TCG. `out.latency=100000` didn't help. As far as
  known, Windows 2000 has no built-in driver for QEMU's AC97 card.
- **Plan should settle:** a one-change-at-a-time investigation of the KVM stall (standard VGA
  instead of Cirrus, CPU models, `kernel-irqchip`, other machine options), with per-command owner
  approval; if KVM works, retest sound under it. Separately: prefer the `pipewire` audiodev when
  QEMU offers it (falling back to `pa`/`none`), for winnt40's sb16 too; whether `SOUND=sb16` becomes
  win2000's default (only if clean) or a documented option; the docs for adding the Sound Blaster
  in Windows 2000 (I/O 220, IRQ 5, DMA 1, 16-bit DMA 5).

## 4. dev-test's intermittent QEMU blank-disk timeout

The check "QEMU starts a blank disk headless" (unchanged since v99) timed out once in three v100
acceptance runs under nested KVM and passed after a Linux restart. It waits before saving any
diagnostics, so the timeout hid the cause. Plan: capture QEMU's state and stderr before waiting,
bounded cleanup, and clear reporting of KVM vs TCG; no root cause is claimed yet.

## 5. winnt40: first install and v100 item 8's acceptance

v100 moved item 8's fresh-install acceptance (NT/2000 Setup runs without the exchange disk, Windows
installs to C:, the disk attaches only after `exchange enable`) to the owner's first winnt40
install. It has not happened yet. Expect the win2000 findings (item 3) to apply to NT 4.0 as well;
record what NT 4.0 does on KVM and TCG.

## 6. DOSBox-X full-screen profile and the renderer-preference WARN

- The owner runs win95 with `output=opengl` for full-screen stretching (`fullresolution=desktop`
  under `[sdl]`, `aspect=false` under `[render]`); `surface` (v100's default, against a maximized
  window's stale-frame flicker) never scales.
- v100's dev-test reports a WARN whenever win95's renderer isn't `surface`, which now flags a
  deliberate owner choice (the config carries `# v100: defaults reviewed`).
- **Plan should settle:** a documented full-screen profile (or a `win95 display` switch) for win31
  and win95; whether a reviewed config's deliberate renderer choice should still WARN.

## 7. win95: OLEnterprise needs DOSBox-X's normal core

- **Finding (Nov 7):** after installing OLEnterprise from the Delphi 3 CD, every `win95` boot
  (dynamic core) hung once its Object Agent started at login, with DOSBox-X ending in a segmentation
  fault. `win95 setup`, which runs the normal core, booted fine.
- **Plan should settle:** docs (normal core for OLEnterprise and similar 32-bit RPC/networking
  software; how to stop the agent starting automatically in Windows 95); whether a persistent
  per-guest core setting is worth adding beyond `win95 --core normal` and editing `boot.conf`.

## 8. Guest network test plan

From v100 (deferred section): one small Delphi 3 Winsock console program (`HTTPGET`), run unchanged
under Wine, win95 (with v100's `win95 net on`), winnt40 and win2000, against the Linux host
(`127.0.0.1` from Wine, `10.0.2.2` from guests), another laptop by Tailscale IP and by name, and the
internet over plain HTTP; plus period-browser checks (plain HTTP expected to work, HTTPS to fail).
Results table per environment. Stretch: serving from a guest (QEMU `hostfwd`), win31 networking.

## 9. Delphi DCOM / multi-tier database demo

From v100 (deferred section): a Delphi server method such as `GetCustomers` over a local database,
called from clients on other guests and machines: DCOM, then MIDAS/socket, then SOAP/HTTP.

- Stage 1: server and client in one win2000 guest. Stage 2 (go/no-go): real DCOM between winnt40 and
  win2000 on a shared QEMU socket network. Stage 3: across two Chromebooks over Tailscale. Stage 4:
  bridges (Borland Socket Server for win95 and Wine; SOAP/HTTP for a Lazarus client on Linux).
- **New (Nov 7):** OLEnterprise (Delphi 3 Client/Server) is a candidate win95 transport besides the
  Socket Server, since Windows 95 lacks DCOM without the DCOM95 add-on; it needs the normal core
  (item 7) and win95 networking.
- Owner inputs still needed: Delphi 4–7 editions; SQL Server version. Unknowns to test early: 1999-era
  SQL Server client libraries against SQL Server on Linux; the shared QEMU socket network in Crostini.
- Item 3's outcome (KVM or TCG) affects how practical two running QEMU guests are on an 8 GB
  Chromebook; the plan should size this before committing to stage 2.
