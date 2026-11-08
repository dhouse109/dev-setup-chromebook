# dev-setup-chromebook v101 plan

Nov 8, 2026 · **detailed draft for owner review; recommendations are not build approval**

Baseline: released `v100` (`3de837e`, Nov 8). The scripts on `plan/v101` are still v100.
This expands the scope notes at `5eb3b35`, following the v100 plan: findings, approach, affected
code, migration, dev-test coverage, documentation and owner choices. This commit changes plans
only. No bundle run, guest start, installation or implementation is authorized.

## Items at a glance

| # | Item | Proposed v101 deliverable |
|---|---|---|
| 1 | Release zip fails in ChromeOS Files because of `CLAUDE.md` | Regular import file, archive/CI checks, owner extraction check |
| 2 | Inspector offline npx ENOTCACHED | Investigate matching execution contexts, then implement the evidenced correction |
| 3 | Windows 2000 KVM stalls and sound | Bounded investigation; native PipeWire selection; conservative defaults unless proven |
| 4 | QEMU blank-disk test timeout | Persistent diagnostics, correct QMP exchange and bounded process cleanup |
| 5 | NT 4.0 installation, CPU and pointer | Record completed exchange acceptance; Pentium default/migration; driver and pointer docs |
| 6 | DOSBox-X full screen and renderer WARN | Document profiles; report valid owner renderer choices as information |
| 7 | OLEnterprise Object Agent crashes the dynamic core | Normal-core recovery and persistent config instructions |
| 8 | Guest network test plan | Reproducible protocol/results matrix; Delphi HTTPGET specification for follow-up |
| 9 | Delphi multi-tier foundation | Supported second-NIC command, `advanced-demo` scaffolding and docs only |

Item 9's Delphi projects, seed SQL, database adapters, COM registration, transport bridges and live
database-swap demonstration belong to a **staged follow-up after v101**, described in
[the companion plan](v101-dcom-demo.md). Completing that application is not a v101 release gate.
Item 8 does not bring Delphi source generation back into this version.

## Recorded owner decisions and choices still needed

Already settled by the owner; do not reopen these as unanswered questions:

- ChromeOS Files extraction is a priority (Nov 8).
- NT 4.0 fresh Setup withheld exchange and created C: successfully (Nov 8).
- The local UDP second-PCnet link worked, including Windows 2000 joining NT's HADAMIN domain
  (Nov 8). Explicit, different MAC addresses were essential; multicast remains unproven.
- The eventual demo belongs in dev-demo at `~/dev-demo/retro/delphi/advanced-demo` (Nov 8).
- Delphi 3–7 C/S or Enterprise editions are available, including Delphi 7 Enterprise. The
  version/database mapping in the companion is agreed: InterBase and SQL Server 6.5/2000;
  Oracle is later. NT SP6a is available and is to precede application/database work.
- **Current instruction:** v101 plans the bundle foundation only; Delphi demo code is a staged
  follow-up. This narrows the earlier companion's full-application wording.

These remaining choices are recommendations, not decisions already made:

| Choice | Recommendation | Owner decision still needed |
|---|---|---|
| 1A | Regular `CLAUDE.md` containing `@AGENTS.md`; reject tracked symlinks in CI | Approve replacement of the symlink rule; confirm Claude context and ChromeOS extraction |
| 2A | Diagnose first; exact Inspector spec/context if needed, preserving strict offline testing | Approve real investigation commands individually; choose evidenced small fix or managed cache |
| 3A | Time-box KVM research; retain win2000 TCG/no-sound defaults unless repeatably clean | Choose experiment budget and any evidence-backed default change |
| 3B | `AUDIO_BACKEND=auto`: PipeWire, then PulseAudio, then silent | Approve policy for both QEMU guests and explicit-override behavior |
| 4A | Keep smoke-test errors as FAIL; capture before waits and bound cleanup | Approve diagnostic-only TCG comparison after KVM failure |
| 5A | NT Pentium default; independent once-only v101 migration; PS/2 docs | Approve migration; record NT KVM/TCG result before any acceleration-default change |
| 6A | Document windowed/full-screen profiles; valid renderers are informational | Approve WARN policy; defer display switcher |
| 7A | Existing `--core normal` plus `boot.conf` instructions | Approve docs-only scope; defer another core-setting command |
| 8A | Manual matrix now; one bounded Delphi 3 HTTPGET in follow-up | Choose controlled endpoints, peer/name forms and acceptance machines |
| 9A | Per-guest `lan status\|on\|off`, local defaults, explicit Tailscale endpoints | Approve command/config ownership and manual adoption of existing NIC arguments |
| 9B | Nested docs/status/results/pack scaffold, no application code | Approve index/path extension, scaffold contents and optional remote transport check |

Each item below gives alternatives and the evidence needed to settle its choices. Plan approval
does not substitute for the separate approvals required for real commands on the owner's machine.

## Shared implementation and validation contract

- Build after approval on `release/v101`; plans stay on `plan/v101`. The first script change
  bumps **all four** to 101, including headers, banners, completion lines and demo `VERSION`.
  Update README's current version and all four CHANGELOG sections together; later stages refine
  those entries. No script/version/changelog implementation belongs in this planning commit.
- Recommend **no new install flag**. Retro helpers/scaffold use `install-retro`; Inspector uses
  `install-agentic` with Node. Keep flag expansion identical across all four scripts. Local guest
  linking needs only retro. Cross-laptop work additionally needs configured normal-mode Tailscale
  (`install-lan`/`install-lan-share`). `install-db-server` is optional for later Linux-server
  comparisons, not a prerequisite that installs Docker databases for the licensed guest lab.
- Setup stays unattended/idempotent. Preserve owner configs and guest disks. Use atomic,
  mode-preserving writes; defer changes while the relevant guest runs. Keep v100's once-only
  migration record intact. Dev-test observes real configs and tests mutations in isolated homes.
- Code locations below were checked against v100. Retro functions mostly live **inside setup's
  quoted `DEVRETRO_EOF` heredoc**, which generates `~/.local/lib/dev-retro/dev-retro`. Re-find
  symbols before editing. Outer `bash -n` does not parse that helper: extract and validate it too.
- Keep existing dated/versioned comments and add v101 explanations. Retained generated artifacts
  and diagnostics go under `$ASSETS`, commands under `~/.local/bin`, new helper config under
  `~/.config/dev-retro`. Guest workspaces/dev-demo remain the established homes for their data.
- Every stack change updates README, `docs/init-checklist.md`, all four CHANGELOG sections and
  its dev-test/disk-report coverage. Each item adds specific docs below. Do not count a new file
  again if a recursive existing disk row already measures it.
- Required installed capabilities and isolated regressions use `check` (FAIL). User-changeable,
  optional/environment-dependent settings use `warn` or information. Optional licensed media,
  guest installations, manual UI checks and the unbuilt application are not required installs.
- Before every push: all-four `bash -n`, `shellcheck -S error dev-*-chromebook*.sh`, whitespace,
  version/flag parity and secret checks (gitleaks in CI). Proposed `tests/test_v101.py` covers
  changed behavior using fake engines, isolated HOME/config and no network. Retain v100 regressions.
  `tests/warm-inspector-cache.py` and `tests/refresh-retro-helper.py` mutate the live installation;
  they are not static checks. The existing untracked `tests/inspect-inspector-context.py` is
  untouched by this commit; review/authorize it separately before adopting or running it.
- Real setup/init/test/demo, Inspector experiments and guest launches require individual owner
  approval. Read saved assets `.output`/`.log` files afterward. No credential/config dumps, cache
  purges, host-guard bypasses or unapproved heavy-service starts. Public reports contain counts,
  results and repo-relative paths, not raw local machine details.

## 1. ChromeOS-compatible release archives

### Finding and approach

The owner reports that v100's source zip stops partway through ChromeOS Files extraction; Linux
unzip completes and reports `CLAUDE.md -> AGENTS.md`. The index confirms mode 120000 for that file.
Treat the symlink as the working diagnosis; final ChromeOS extraction must prove the fix.

**Recommend 1A:** replace it in the approved build with an ordinary UTF-8 `CLAUDE.md` containing
the operative line `@AGENTS.md`, optionally with a short instruction to edit AGENTS.md. Shared
rules remain in AGENTS.md. Update its "never replace the symlink" instruction in the same change,
and explain the v101 change in `docs/how-its-built.md` without rewriting the v98 history.

The [official Claude documentation](https://code.claude.com/docs/en/memory#share-one-file-with-other-coding-tools)
supports this adjacent-file import. Both files are at the root, so the relative target is clear.
This verifies the documented design; **runtime loading here remains an acceptance check**, not
a result claimed by this planning session. Only CLI version help was inspected. Do not start a
paid/model session or write its state just to claim import success during planning. After the
change the owner opens a normal session here, uses `/context all` (and `/memory` where available)
and confirms the imported file and a distinctive existing rule; repeat in an extracted copy.
Codex's input remains the unchanged root AGENTS.md; verify its rules in a fresh Codex session
too. Neither tool should depend on a second copy of the rules.

**Alternative 1B:** retain the link and set `CLAUDE.md export-ignore` in `.gitattributes`.
[Git archive](https://git-scm.com/docs/git-archive#ATTRIBUTES) supports exclusion, but extracted
bundles lose the explicit Claude entrypoint, and whole-tree no-symlink CI would need an exception.
Prefer 1A.

### Files, checks, docs and decision

- **Files:** `CLAUDE.md` (100644), AGENTS.md introduction, `.github/workflows/lint.yml` and
  proposed `tests/check_release_archive.py`. No bundle function changes for this item.
- **CI:** parse `git ls-files -s -z`, reject every mode 120000 entry and print relative names.
  Use a synthetic symlink tree to prove failure. The tracked link is expected to remain until
  implementation; this draft must not claim the proposed guard passes today.
- **Archive:** from the candidate committed tree, run `git archive --format=zip` with prefix
  `dev-setup-chromebook-v101/`, keeping output under `assets/releases/`. Check zip integrity,
  entry modes, the import file and tree manifest, including all four scripts/docs; account for
  deliberately export-ignored files. Do not package loose working files/untracked artifacts.
- **Dev-test:** source layout is a CI/package check, not an installed-stack FAIL. Owner extracts
  the candidate in ChromeOS Files, checks completeness/final files and repeats with the actual
  GitHub-generated release source zip. Linux extraction alone is insufficient. Disk report has
  no installed-content change.
- **Docs:** AGENTS.md, `docs/how-its-built.md`, README download/extraction instructions and release
  notes; record results here. No new runtime Crostini workaround or secret/manual init step.
- **Decision:** approve **1A (recommended)** and the no-tracked-symlink policy, or **1B** with a
  revised CI policy. Real import/Files verification remains open until performed.

## 2. Inspector offline cache coherence

### Evidence and investigation before implementation

Carry forward v99's accepted ENOTCACHED issue retained in v100 item 1. Setup's real online and
immediate offline tools/call returned 5; later dev-test offline npx failed while the global CLI
worked. Matching headline Node/npm versions did not establish matching executable/config/cache/
cwd/spec inputs. No cache deletion, eviction or version mismatch is a proven cause.

1. Use a machine configured by the bundle's own `install-agentic install-node`; do not hand-build
   Inspector in assets. At actual setup/test probes compare allowlisted executable identities and
   versions, exact spec, canonical cache identity, cwd category and registry/scoped-registry
   equality. Keep paths local; redact URL userinfo/query strings, publish safe origins/equality.
   Never read npm credentials or dump config/environment.
2. With separately approved commands, compare bare spec, explicit `@latest` and the exact global
   release in isolated diagnostic caches. Capture real producer status, full local diagnostics
   and result 5 for online, immediate strict offline and later test-context calls. Include
   project npm-config/cwd influence in the comparison.
3. Repeat a successful pair after the intervening workflow and a fresh terminal/Linux session.
   No cache purge, test-time download/repair or substitution of the already-passing global CLI.
   Present evidence before choosing whether a smaller explicit spec/context fix is sufficient.

### Recommended correction, conditional on findings

**2A:** prefer the smallest evidenced correction. If a managed cache is needed, read the installed
global release after successful setup acquisition, warm that exact spec under
`$ASSETS/tools/mcp-inspector/npm-cache` in a stable bundle-owned cwd, then atomically publish the
successful version/context record only after both online and strict offline calls return 5.
Preserve the prior usable record/cache on update failure; use candidate state/cache where needed
so a failed refresh cannot break the old one. Do not hardcode an unverified release or resolve
mutable latest in dev-test.

Test consumes the same spec/cache/cwd with strict `--offline`. Cache unavailability stays an honest
WARN with status/evidence/repair hint. Global installation/call remains a separate required check.
If needed, generate `~/.local/bin/dev-mcp-inspector` using the record, command-scoped npm cache/
offline options and FastMCP's supported `--inspector-version`. Preserve the caller's project context
or normalize the server path so managed cwd does not break relative imports. Verify the option
against installed FastMCP; [upstream documents it](https://github.com/PrefectHQ/fastmcp/blob/main/docs/cli/running.mdx).
Do not promise offline uv/Python dependencies merely because npm is warm.

### Files, dev-test, docs and decisions

- **Setup:** install-agentic Inspector block and `inspector_cache_call` (v100 8180–8216), generated
  `cache-check.py`, record/launcher and honest stage reporting. **Test:** `mcp_server.py`, global/
  offline assertions around 4566–4587 and agentic disk row. **Demo:** `demo_fastmcp`'s inspector
  menu uses the chosen invocation. **Init:** hints if needed and shared metadata. Review the
  mutating `tests/warm-inspector-cache.py` only as an approved investigation aid.
- **Dev-test/fixtures:** cold cache fails honestly; online/offline result/status; nonzero producer
  with misleading result text; missing/malformed/mismatched record; context mismatch; failed update
  preserves old record/cache; rerun reuse; no environment leakage. A required shipped launcher
  missing is FAIL; optional cache availability WARN. Real fresh-session/FastMCP success requires
  owner verification. Existing agentic `dpaths` recursively covers the tools directory; adjust its
  label/diagnostics accounting without counting managed cache twice or global Node content again.
- **Docs:** common README/checklist/CHANGELOG updates, `docs/dev-demo.md` and generated FastMCP
  instructions. State the online warm-up/strict-offline contract. Add a Crostini gotcha only for an
  evidenced host-specific cause, not an assumed npm defect.
- **Decisions:** approve real research command by command, then choose **2A (recommended)** small
  fix when proven or managed exact-version cache/launcher when necessary. **2B:** explicitly defer
  with the accepted WARN; do not call it fixed. The implementation design remains evidence-gated.

## 3. Windows 2000 nested KVM and sound

### Investigation and defaults

Nov 5–7 owner evidence: KVM stalls both Setup and installed Windows 2000; TCG boots. PulseAudio
volume errors stop with native PipeWire/sb16. Windows 2000's SB16-compatible WDM driver plays sound
but stutters under TCG; output latency 100000 did not help. A built-in AC97 driver is not established.
Keep boot, backend errors and audible quality as separate findings.

**Recommend 3A:** agree a small budget (one session, at most six single-change variants). Start
with guest off and an owner-approved recoverable disk/config backup. Use the installed system
before reinstall experiments. Record elapsed boot, display progress, selected accelerator, CPU
use and audio separately. Stop unsuccessful variants at an agreed limit (suggest three minutes),
restoring baseline before the next.

Suggested order, after read-only installed help checks: TCG baseline; KVM baseline/sound off;
standard VGA instead of Cirrus; one supported alternate CPU; `kernel-irqchip=off`; a supported
split-irqchip or versioned i440fx variant if warranted. No combined speculative options, q35 switch,
blind HAL change or host kernel/KVM reconfiguration. Machine/CPU changes may affect hardware
detection; owner controls recovery. `qemu_launch` appends `,hpet=...` to MACHINE: avoid duplicate
properties. Research does not promise a KVM fix.

Retain win2000 TCG, `SOUND=none` and unscaled-tablet defaults unless repeatable cold boots, owner
normal use and audio checks support a new choice. Return to the owner with evidence and the exact
migration/marker policy before changing defaults. Never reset v100's review marker.

### Audio policy

**Recommend 3B:** `AUDIO_BACKEND=auto|pipewire|pa|none`, with helper fallback auto when absent.
SOUND=none adds no card/backend. Otherwise auto selects supported native PipeWire when the user's
runtime socket exists, then supported/reachable PulseAudio, then explicit silent backend with a
note. Explicit unavailable requests fail before guest launch with a clear override/repair hint.
Do not restart a guest automatically if audio initialization fails after launch.

Read-only planning inspection confirmed native pipewire/pa/none in installed QEMU audio help;
this is capability evidence, not playback evidence. Apply policy to NT's sb16 as well. Win2000
sb16 stays opt-in until clean. Document its owner's working WDM SB16/AWE32-compatible selection:
I/O 220, IRQ 5, DMA 1, 16-bit DMA 5; verify resources inside Windows. Correct generated STEPS that
currently suggest a suitable AC97 driver necessarily exists on the Windows CD.

### Files, dev-test, docs and decisions

- **Setup/helper:** `qemu_config`, `pick_accel`, `audio_args`, `qemu_launch`, `accel_status`,
  `qemu_preferences`, `EOF_RCFG` and help. Use an array for audio argv instead of current word-split
  command output; preserve card choices. Existing configs can inherit auto without being rewritten.
  **Init:** retro messages. **Demo:** `demo_retro` STEPS-winnt/Delphi. **Test:** QEMU/audio fixtures.
- **Dev-test:** required fixtures for no card, native, PulseAudio fallback, silent fallback,
  explicit unavailable backend, no duplicate IDs and launch/status agreement. Detect capabilities
  without starting services. Optional unavailable audio warns; selected settings are information.
  No automated real guest boot or speaker test. Keep accelerator regressions and item 4's separate
  smoke check. Existing QEMU/config rows cover installed bytes; account for retained experiment
  logs under retro diagnostics once. No new guest memory/disk default.
- **Docs:** common docs, Crostini Retro findings/recovery, `docs/dev-demo.md`, generated STEPS.
  Explain backend errors disappearing separately from stutter being solved.
- **Decisions:** **3A (recommended)** bounded research, or defer KVM and do backend/docs only.
  **3B (recommended)** native-first auto/explicit overrides, or opt-in PipeWire only. Any sound/
  acceleration default change is a later evidence-dependent choice within the approved build.

## 4. QEMU blank-disk test diagnostics

### Finding and implementation

The v99/v100 `slow "QEMU starts a blank disk headless (accelerator, QMP answers)"` starts QEMU in
scratch, runs a Python QMP exchange and unconditionally `wait $q` before printing status/stderr.
If QMP fails before quit, wait can consume the outer 120-second timeout; scratch logs disappear
on exit. One of three acceptance runs timed out and a Linux restart preceded a pass: cause unknown.

**Recommend 4A:** a generated Python supervisor, still a `slow` FAIL check. Use only its dedicated
blank qcow2, no networking/audio/display or owner disk. Open persistent
`$ASSETS/logs/retro-qemu-<run-stamp>/` diagnostics **before spawn**. Flush argv, QEMU version,
selected KVM/TCG/reason, monotonic phase times, stderr/process state and QMP traffic as produced.

Bound startup/connect/greeting/capabilities/query-status; correlate response IDs and skip events.
Distinguish timeout, protocol error and child exit. Pass requires an actual running reply and
bounded teardown. On success/failure/signal: QMP quit, short wait, terminate owned child, kill if
necessary, reap. Internal deadlines/cleanup must fit below outer timeout; TERM flushes evidence
and cleans up before its five-second kill grace. Use owned process handles/group, never a broad
`pkill qemu` or old guest pid file. Do not block indefinitely in finally/wait.

Optional bounded TCG comparison after KVM failure can localize the problem but cannot turn the
original FAIL into PASS. Fit it in the budget or propose a separate owner-approved command.
No silent retries, WARN downgrade or forced-TCG substitution for the KVM assertion.

### Files, dev-test, docs and decision

- **Test:** replace inline smoke block at v100 5982ff; review `_run`, `slow`, `test_exit`/outer
  timeout interaction without unnecessary global changes. Generate supervisor under WORK;
  keep diagnostics under assets. Fake QEMU/QMP fixtures cover events, startup exit, absent socket,
  broken greeting, timeout, ignored quit/TERM, parent TERM and cleanup failure.
- **Dev-test:** print selected accelerator/failure phase and persistent path even on timeout.
  Assert producer status and no leftover owned child/socket. `quick` skips the real smoke test;
  portable fixtures can still run. Add persistent diagnostics to retro disk report, using allocated
  bytes, without adding automatic retention/deletion policy. A real repeat needs owner dev-test.
- **Other scripts:** metadata only. **Docs:** checklist evidence path/troubleshooting, Crostini
  Retro known issue, CHANGELOG and plan results. README points to them. No root-cause claim until
  supported by captured evidence.
- **Decision:** **4A (recommended)** diagnostics/cleanup plus optional diagnostic TCG comparison,
  or capture/cleanup alone. Original accelerator failure must always remain visible.

## 5. NT 4.0 CPU, installation acceptance and usability

### Evidence and approach

**Completed Nov 8 (owner-reported):** fresh `winnt40 setup` withheld exchange; text-mode Setup saw
only the 4095 MB system disk and made C:. This supplies v100 item 8's delegated fresh-install
acceptance. No reinstall is needed and v100's historical record should not be rewritten. Continued
boot gating and later exchange enable remain fixture/hand checks; the note alone does not prove
every post-install step was completed.

Three NT Server ISOs stopped with 0x1E/0xC0000005 in hal.dll on Pentium III; CPU=pentium allowed
Setup to detect MPS Uniprocessor PC. Drawing is slow and PS/2 drifts with scaling on or off. Reduced
NT mouse speed helped the owner; a USB tablet is not NT's built-in path. These are specific findings,
not a guarantee for all NT media or proof that win2000's KVM stall applies identically to NT.

**Recommend 5A:** new NT configs and helper fallback use Pentium; win2000 CPU remains unchanged.
Extend `qemu_defaults`/`config_defaults` to review NT with an independent
`# v101: NT CPU reviewed` marker. Current qemu_defaults only handles win2000; the existing v100
marker must neither suppress the NT change nor be reset to rerun Windows 2000 migrations.

For stopped existing NT configs replace only the single untouched v100 line
`CPU=pentium3            # pentium if setup blue-screens on this model` (trailing spaces allowed),
or add CPU=pentium if absent in a simple unreviewed config. Preserve edited values/comments,
duplicates, symlinks and complex shell; ambiguous regular files can be marked reviewed with a
manual note, as in v100. Atomic byte/mode/CRLF preservation; new files start marked. Later restored
Pentium III/deleted CPU stays untouched. Running defers without marking. Exact spelling is only a
proxy for untouched defaults; an owner deliberately keeping it can edit/comment it or decline
migration. Do not pretend that spelling proves intent.

Keep NT ACCEL=auto until owner compares installed-system KVM/TCG. Document View > Grab On Hover/
click capture, Ctrl+Alt+G release, reduced Control Panel > Mouse > Motion speed and the guest's
Cirrus driver rather than 16-color VGA. Registry thresholds are a backed-up manual fallback, not
automated. Defer VMware absolute mouse support until compatible owner-supplied driver/media and
a separately chosen experiment exist.

### Files, dev-test, docs and decisions

- **Setup/helper:** `qemu_config`, `qemu_defaults`, `config_defaults`, `nt_cmd`, preferences/help,
  `EOF_RCFG`. Use a per-guest CPU template variable instead of changing the common hardcoded line
  for both. **Test:** extend QEMU defaults/argv fixtures and retain exchange identity/Setup cases.
  **Init/demo:** hints where needed and `STEPS-winnt.md`.
- **Dev-test:** required fixtures for NT fallback/new template versus unchanged 2000, exact line,
  absent CPU, owner edits, duplicate/complex/symlink config, running deferral, atomic marker, mode/
  CRLF and restored/deleted values on later setup/launch. A real retained known-problem CPU is
  an owner-setting WARN, never automatically rewritten by test. Owner records KVM/TCG, pointer,
  driver, login keys and exchange results. No licensed media/installed NT requirement; existing
  NT workspace disk row suffices, no resizing/reservation change.
- **Docs:** common docs, Crostini NT CPU/pointer/driver findings, `docs/dev-demo.md`/STEPS;
  checklist records C: success and SP6a prerequisite for later apps. No driver/SP downloads.
- **Decision:** **5A (recommended)** once-only exact-template migration/PS2 docs; **5B** new
  installs/docs only with manual existing CPU fix. NT acceleration awaits actual owner results.
  Recommend deferring VMware mouse support.

## 6. DOSBox-X full screen and renderer preference WARN

### Approach and migration

Owner uses OpenGL with `[sdl] fullresolution=desktop` and `[render] aspect=false` for stretching.
Surface fixed maximized stale-frame redraw in v100 but does not provide that stretching. Current
`dosbox_config_status` returns nonzero for every non-surface win95 output, so test warns about an
intentional choice even after v100 defaults review.

**Recommend 6A:** document manual stopped-guest profiles. Windowed win95 keeps surface as the
new-install default; full-screen stretching uses the owner's OpenGL/desktop/aspect=false settings,
explaining distortion, possible windowed flicker and focus recovery. For win31 explain its existing
OpenGL baseline and verify the equivalent full-screen settings with the owner before claiming
success. DOS retains ttf; all v100 migrations stay once-only.

Separate renderer information from invalid-config diagnostics. A unique valid installed-build
renderer is information with tradeoffs; missing/duplicate/unsupported output remains WARN. A v100
review marker means migration ran, not proof of a deliberate preference, so it must not suppress
structural warnings. Keep hostkey/folder-mount warnings independent. No recurring config rewrite,
fullscreen=true default or implicit display switcher.

### Files, dev-test, docs and decision

- **Setup/helper:** `dosbox_config_status`, `ini_setting read`, `retro config-status`, help;
  keep `dosbox_defaults`, `win95_confs` and win31 creation defaults. **Test:** separate current
  combined preference warning/information and update DOSBox fixtures. **Demo:** generated Delphi1/
  Delphi display notes. **Init:** metadata unless a stale hint needs updating.
- **Dev-test:** required fixtures for reviewed/unreviewed surface/OpenGL, invalid/duplicate/missing
  values despite marker, hostkey/mount warning retention, no writes and preservation of later
  restored/deleted settings. No WARN solely for a valid renderer. Owner validates fullscreen,
  shortcuts and recovery; parsing config proves no visual behavior. Existing disk rows suffice.
- **Docs:** common docs, Crostini Graphics/Retro tradeoffs, `docs/dev-demo.md`, generated STEPS;
  retain dated v100 finding alongside profile rationale.
- **Decision:** **6A (recommended)** documentation/warning policy. **6B:** add display switcher,
  requiring additional transactional edits/conflict/migration design; defer unless owner chooses it.

## 7. OLEnterprise Object Agent and normal core

### Approach

Nov 7 owner finding: Delphi 3 OLEnterprise's Object Agent started at win95 login; dynamic core hung
and DOSBox-X segfaulted. Normal-core `win95 setup` booted. This establishes a workaround for that
installation, not all RPC/network software.

**Recommend 7A:** existing `win95 --core normal` recovers; with guest off, set `[cpu] core=normal`
in `~/win95/boot.conf` for persistence. Keep normal setup and general dynamic boot defaults. Explain
disabling Object Agent automatic startup if unused: inspect Startup/vendor configuration first,
remove only the identified startup action. Do not invent a registry key or delete the installation.
If Run/RunServices is used, document the actual owner-confirmed entry and export it before editing.
Do not recommend routine `setup` launches just to select normal core.

### Files, dev-test, docs and decision

- **Setup/helper:** existing `win95_cmd`, `win95_confs` comments/help only as needed.
  **Demo:** `demo_retro` STEPS-delphi and advanced scaffold cross-link. **Test:** focused fake-engine
  argv checks for `--core normal` overriding config, normal setup and persistent edit preservation.
  **Init:** version metadata only.
- **Dev-test:** no add-on requirement or real crash/guest reproduction. Owner verifies normal-core
  login and identifies startup control; missing licensed OLEnterprise is not FAIL. Existing disk
  rows cover content; no new downloads/config migration.
- **Docs:** common docs, Crostini Retro crash/workaround, `docs/dev-demo.md` and generated STEPS;
  broader RPC software is a troubleshooting suggestion, not an established finding.
- **Decision:** **7A (recommended)** existing commands/docs. **7B:** another persistent core
  switcher, deferred unless owner wants command-managed config edits.

## 8. Guest network test plan

### v101 procedure and follow-up probe

**Recommend 8A:** publish repeatable manual protocol/results now with item 9's command. Specify the
eventual Delphi 3 Winsock HTTPGET, but write/compile it in the staged code follow-up. Contract: one
plain-HTTP URL, bounded DNS/connect/read, Host header, status/body, nonzero failure; HTTP/1.0 with
connection close suits period Winsock. Build once and copy identical binary under Wine/win95/NT/
2000, recording its checksum/version. No TLS emulation or browser installer.

For v101 use existing guest browser/tools and an owner-started controlled Python HTTP server on
Linux serving only a fixed marker. Label browser results as browser evidence, never as HTTPGET
results. Choose a free high port (example 8765), stop the listener afterward; prefer specific
reachable interface binding. A wildcard bind for NAT/Tailscale requires an explicit documented
reachability choice, not a persistent service or ChromeOS port-forward recipe.

| Origin | Target | Expected path / observation |
|---|---|---|
| Wine | Same Linux host | `http://127.0.0.1:8765/`, fixed marker |
| win95/NT/2000 user-mode NIC | Linux host | `http://10.0.2.2:8765/`; verify installed DOSBox-X slirp alias |
| All four | Other laptop Tailscale IPv4 | Controlled marker, separating reachability from HTTP |
| All four | Peer short and full tailnet names | Record DNS separately; guest DNS need not inherit MagicDNS |
| All four | Chosen plain-HTTP internet endpoint | Record redirect/status; HTTPS redirect is not HTTP transport failure |
| Period browsers | HTTP / HTTPS comparison | HTTP marker expected; legacy TLS may fail, record actual result |
| NT ↔ 2000 second NIC | 192.168.50.10 / .20 | Bidirectional ping and existing domain behavior |

Template columns: date, bundle/engine versions, origin, transport, target category, IP/name form,
DNS/connect/HTTP result, elapsed time, evidence reference. Raw results remain under assets; public
reports are sanitized. Distinguish NOT RUN, unsupported and FAIL; never pre-fill success.

### Files, dev-test, docs and decision

- Proposed `docs/guest-network-tests.md`, README/checklist links, generated advanced STEPS/results
  template. **Demo:** explain controlled host-server command, no unattended listener/download/
  Delphi generation. **Setup/init:** help/hints only, no new DNS setting, dependency or credential.
- **Dev-test:** retain existing LAN protocol probes; required item 9 argument fixtures/template
  consistency tests. No second laptop/internet HTTP/real guest/absent HTTPGET requirement for retro.
  Manual results do not become automated PASS counts. Disk report accounts for tiny scaffold and
  retained assets results once; no database stack content is added.
- **Docs:** common docs, Crostini NAT/DNS/inbound limits, `docs/dev-demo.md` explaining scaffold
  versus later binary/VM/database footprint.
- **Decision:** **8A (recommended)** procedure now/probe later. Select controlled peer/listener,
  external HTTP endpoint, short/FQDN names and test machines before real checks. Win31 networking
  and guest inbound hostfwd are follow-ups; install-db-server is not a basic-network prerequisite.

## 9. Bundle foundation for the later Delphi demo

### Boundary and proven baseline

v101 builds a supported guest-network command, dev-demo scaffolding and documentation. **No Delphi
`.pas`/`.dpr`/forms, seed SQL, binaries, COM/DCOM registration or live database integrations** in
v101. The menu labels application stages pending; they are not a v101 completion criterion.

Owner-proven Nov 8 link, retaining each guest's first user-mode NIC:

```text
NT:   -nic socket,model=pcnet,mac=52:54:00:50:00:10,udp=127.0.0.1:10002,localaddr=127.0.0.1:10001
2000: -nic socket,model=pcnet,mac=52:54:00:50:00:20,udp=127.0.0.1:10001,localaddr=127.0.0.1:10002
```

Windows second NICs: 192.168.50.10/.20, mask 255.255.255.0, **no gateway**; 2000 WINS=.10 in the
existing HADAMIN lab. Guest IPs are distinct from host UDP endpoints and set manually in Windows.
First NIC keeps internet/default route. NT NWLink requested a nonzero internal network number with
two adapters; record that observation, not a requirement to add NWLink/IPX. Multicast attempt with
duplicate default MACs got no replies; multicast itself remains untested.

### 9A. Supported command and config ownership

Recommend existing per-guest style, separate from DOSBox-X's `win95 net`:

```text
winnt40 lan [status|on|off]
win2000 lan [status|on|off]
<guest> lan on [--peer IPV4 --bind IPV4 --local-port N --peer-port N --mac MAC]
```

- Status defaults, reads only and never migrates/boots. Missing state means off. `on` without
  options explicitly selects the local preset above by guest; custom mode requires all five
  endpoint/MAC options. `off` disables managed NIC only and retains parameters for inspection.
  Changes require that guest stopped; no hot-plug or automatic domain/IP configuration.
  Dispatch read-only LAN status before today's eager STATE/workspace `mkdir` calls; create
  directories lazily only for mutations/launches so a first status on a fresh home writes nothing.
- Record versioned JSON under `~/.config/dev-retro/<guest>-lan.json`; allowlist/schema parsing,
  no shell source/eval. Validate then atomically replace regular files preserving mode. Refuse
  symlink, unknown schema or corrupt state without clobbering it. Missing state preserves existing
  launches. Corrupt state needs manual repair, not guessed recovery writes.
- Local preset uses PCnet, reciprocal loopback UDP ports, distinct locally administered unicast
  MACs. Validate IPv4, ports (recommend 1024–65535), unicast MAC, nonidentical local endpoints;
  reject unsafe wildcard binds, unspecified/multicast/broadcast peers, duplicates and injection.
  Remote mode requires numeric Tailscale IPv4 peer, **specific local Tailscale IPv4 bind**, explicit
  ports and lab-unique MAC. Confirm bind address is local at launch without reading credentials.
- Supported topology is **one point-to-point pair**: NT↔2000 locally, or one selected QEMU guest
  per laptop. Four simultaneous endpoints require a later hub/switch design. Remote examples name
  both endpoint/guest IP/MAC identities. No multicast, TAP/bridge, sudo, host reconfiguration,
  broad 0.0.0.0 bind or ChromeOS port forwarding.
- Append one validated `-nic socket,...` in `qemu_launch`, preserving existing user-mode NIC
  policy, exchange gate and CDs. Valid enabled link applies to normal/run/explicit setup launches
  (including domain-controller installation); setup still withholds exchange. Off changes no
  Windows settings or disks. Status does not ping peers or launch QEMU.
- Existing hand-written second-NIC EXTRA_ARGS must not gain a duplicate. Managed off leaves those
  untouched. Before on, inspect `-nic`, `-net`, `-netdev` and network-device overrides and refuse
  ambiguous custom networking. Owner adoption with guests off: back up config, remove only known
  manual link args, run on. Never auto-delete owner text; preserve unrelated args. Revalidate on
  launch against later edits, failing before opening disks on conflict.
- Reject known local managed-pair MAC/bind-port collisions; report other-process port ownership
  without killing anything. QEMU bind failure is an error, no silent alternate port/topology.
  Cannot prove remote MAC uniqueness/reciprocity locally: status prints expected reciprocal values
  and docs require checking the peer. No rewrite of tailnet access policy; owner permits UDP ports
  in existing normal-mode Tailscale configuration.

Local link/domain join is proven; remote UDP/domain/DCOM are distinct unproven stages. Check
socket syntax against installed Debian QEMU, using the
[upstream network reference](https://www.qemu.org/docs/master/system/invocation.html#network-options)
as design guidance, not a substitute for installed support.

### 9B. dev-demo scaffold and lifecycle

Add separate `demo_retro_advanced` under install-retro, independent of `demo_retro`'s Watcom guard.
Keep retro/matrix; generate the agreed nested home:

```text
retro/delphi/advanced-demo/
  README.md              foundation status, prerequisites, follow-up links
  STEPS.md               network commands, guest IPs, drivers/SP6a/media/recovery
  VERSIONS.md            agreed mapping; unverified media details labelled
  results-template.tsv   manual columns, initially NOT RUN
  work/README.md         owner workspace; application sources arrive later
retro/delphi/run-advanced-demo.sh
```

Menu: `steps`, `status` (read-only helper status), `results` (copy-template guidance) and explicit
`pack`. No action boots a guest, installs software, configures DCOM or pretends to run application
stages. Pack uses existing genisoimage to create a **documentation-only foundation CD**; validate
before atomic publication to `$ASSETS/retro/advanced-demo/ADVDEMO.iso`, then print the owner's
explicit `<guest> cd FILE.iso` command. Allowlist docs only; exclude work/results/media/config. Later
code work can extend packaging. Nothing compiles or builds an ISO during this planning task.

Existing index assumes `<stack>/<name>` and validates `run-<name>.sh` before reading its record.
Do not pass `retro/delphi` as STACK: slash-containing `.index` names break discovery/cleanup.
Recommend optional relative demo/launcher paths in `begin`, retaining all existing defaults:
STACK=retro, NAME=advanced-demo, relative directory `delphi/advanced-demo`, launcher
`delphi/run-advanced-demo.sh`, flat key `retro--advanced-demo`. `write_run`, `done_demo` and
`write_index` consume recorded relative launcher; index reads it before existence validation.
Reject traversal/absolute paths and keep old TSV records compatible.

Bundle README/STEPS/version docs and launcher refresh as retro STEPS do today. Owner workspace/
template is create-if-missing; never replace future code/results, even on demo-refresh. Existing
demo-clean confirmation lists the target and removes correct directory/launcher/index, not guest
workspaces or assets ISO/results. Both retro demos remain indexed/workspace-discoverable. Ready
means scaffold available, not application accepted.

### Files and functions affected

- **Setup/helper:** header/help, `help_cmd`, main dispatch, `nt_cmd`, `qemu_launch`, `qemu_config`/
  EXTRA_ARGS integration, where/status notes; proposed `qemu_lan_status`, `qemu_lan_config`,
  `qemu_lan_args`. New feature defaults off, no automatic adoption/enabling.
- **Test:** QEMU argv/isolated-home helper fixtures under retro; proposed `tests/test_v101.py`.
  Existing "Retro helper and config" row already covers `~/.config/dev-retro`; clarify its label
  for LAN state rather than add the directory again. Add assets ISO/results once and retain guest
  workspace rows. Add a demo scaffold row only if not already covered by a demo total. Scaffold
  checks are portable fixtures, not requirements that the owner already ran dev-demo.
- **Demo:** new `demo_retro_advanced`, bottom dispatch, `begin`, `write_run`, `done_demo`,
  `write_index` and clean/path metadata. `gen_file`/`present`/`stash_old` must not replace future
  work on refresh. Cross-link matrix menu/STEPS-delphi/STEPS-winnt to new launcher/docs.
- **Init:** informational prerequisites only; no required credentials, SQL/SP install or VM start.
  All four share flags/version metadata.

### Dev-test and owner acceptance

- Required fake-engine fixtures: off/missing preserves argv; exact local presets/reciprocity/MACs;
  remote explicit pair; on/off/rerun; schema/input/bind rejection; running guards; EXTRA_ARGS
  refusal/adoption; malformed/symlink state; collisions; status no writes/network/engine; first
  NIC preserved; second NIC boot/run/setup and exchange withheld in setup. Isolated HOME/config.
- Scaffold fixtures: nested paths, old/new index compatibility, launcher syntax, honest menu,
  no application/seed/binary generation, refresh preservation, correct clean target, pack doc
  allowlist. Real ISO inspection in a portable fixture when genisoimage available; missing pack
  tool yields a useful message, never installs it from the menu. Owner work/results stay intact.
- Owner after backup/adoption runs each guest's lan on/status, boots explicitly, sets/verifies
  PCnet/IPs, pings both directions, confirms existing domain and first-NIC internet. Shut down,
  off, confirm second adapter absent without data loss; on again retains identity. Windows may
  need driver rebinding when NICs change: document recovery; owner handles domain credentials.
- Network-only acceptance starts at current NT 128 MB/2000 256 MB. Future SQL lab may use NT
  128–256 MB/2000 512 MB, one database workload at a time. No global memory/SMP change: TCG
  multi-thread mode is not two guest vCPUs; helper currently uses `-smp 1`. Measure responsiveness
  before requiring two simultaneous guests. No models/Docker databases for this transport test.
- Optional remote v101 evidence: one endpoint per laptop, explicit Tailscale binds, reciprocal
  ports, ping and disable/restore. If not run label remote mode unconfirmed; no DCOM claim. Later
  application work completes one-laptop behavior before cross-laptop demonstrations.

### Docs and decisions

Common docs; `docs/dev-demo.md` scaffold/ISO versus VM/database footprint; Crostini link/MAC/TCG
notes; proposed guest-network procedure; generated STEPS; companion plan. Document own-media
SP6a/SQL/InterBase/Delphi without implying installers are included. Preserve qualified domain/
multicast observations and licensed-media boundaries.

**9A (recommended):** approve command grammar/JSON ownership, local preset, explicit remote mode
and manual EXTRA_ARGS adoption. Alternative: local-only command in v101, remote support later to
reduce acceptance surface. **9B (recommended):** nested docs/status/results/pack scaffold with
compatible index extension. Alternative: defer pack until sources arrive. Location, mapping,
SP6a and Delphi-code deferral are settled and do not need deciding again.

## Proposed build stages after owner approval

1. **Archive (1):** import/rules/history, CI and candidate archive checks; owner context/extraction.
   No script bump needed until first script stage.
2. **Diagnostics/research (4, research for 2/3):** bounded supervisor/fake peers, then separately
   approved observations. First script commit bumps all four/README/CHANGELOG to v101. Record
   evidence before cache/default choices.
3. **Retro defaults/reporting (3, 5–7):** NT migration, backend selection, renderer warning policy
   and docs/STEP updates with preservation regressions; keep unproven defaults conservative.
4. **Inspector (2):** owner-approved evidenced correction, fixtures, strict-offline real checks and
   FastMCP/demo docs. Investigation can determine this stage's final design.
5. **Supported link (9A):** config/argv/status/adoption/collision fixtures, docs/disk rows, owner
   local transport and first-NIC validation.
6. **Procedure/scaffold (8, 9B):** nested lifecycle/index, docs/results/menu, optional foundation CD.
   No Delphi/SQL source. Check refresh/clean ownership and final command cross-references.
7. **Acceptance record:** settle pending choices/results, static checks and owner Chromebook route.
   Every stage commit has Codex co-author trailer; no merge/release implied by a plan/build commit.

## Proposed owner acceptance route

Commands below are for the later approved build, **not permission to execute now**.

1. Settle 1A–9B, including explicit deferral/claim narrowing if research or remote mode stays
   unconfirmed. Validate Claude import and archive extraction separately.
2. Guests/heavy workloads stopped; targeted init → setup → init → test, then optional demo:

   ```bash
   ./dev-init-chromebook.sh install-retro install-agentic install-node
   ./dev-setup-chromebook.sh install-retro install-agentic install-node
   ./dev-init-chromebook.sh install-retro install-agentic install-node
   ./dev-test-chromebook.sh install-retro install-agentic install-node
   ./dev-demo-chromebook.sh install-retro
   ```

   First init on fresh machines only creates template. Approve/run each separately and inspect
   assets output/stage coverage. Demo remains outside test checklist; verify scaffold menu/status/
   pack without treating the deferred application as installed.
3. Separately approved Inspector strict-offline checks after workflow/new session; bounded KVM/
   audio experiments within budget; NT preservation/CPU/usability; DOSBox profiles/core recovery.
   Preserve existing guests: no repeat fresh install needed for recorded C: acceptance.
4. Local managed-link hand checks and available-tool HTTP/DNS matrix. NOT RUN for deferred
   HTTPGET/DCOM/database stages. Stop temporary listeners/guests, read persistent diagnostics and
   confirm failed smoke probes left no process behind.
5. Broader regression, only if requested: repeat init → setup → init → test with established
   `install-all install-db-server install-lan-share install-models install-ollama-containers
   install-retro`. Separate approvals and existing heavy-workload guards still apply; mentioning
   this route does not authorize it or make it mandatory for a planning-only change.
6. Release gate: real clean Chromebook test (FAIL 0; WARNs only optional credentials), selected
   stages complete, normal prompt return, required archive/hand checks recorded. Any known
   non-credential exception or unconfirmed advertised capability needs explicit owner acceptance/
   narrowed claims before release. Until real validation, a built version is **built, not yet
   confirmed run on a Chromebook**; this version is currently only **planned**. Merge/tag/release
   follow acceptance and owner authorization. Scaffold readiness is not Delphi app acceptance.

## References and evidence limits

Primary references checked: Claude import and Git archive docs (1),
[npm exec](https://docs.npmjs.com/cli/v11/commands/npm-exec/) and
[npm config](https://docs.npmjs.com/cli/v11/using-npm/config/) plus FastMCP CLI (2), and
[QEMU audio/network invocation](https://www.qemu.org/docs/master/system/invocation.html) (3/9).
[QMP specification](https://www.qemu.org/docs/master/interop/qmp-spec.html) is the protocol
reference for implementation (4). Live docs may describe newer versions: installed help and real
owner tests remain authoritative for supported behavior.

Planning inspection was read-only: source/fixtures/docs, tracked mode, CLI version/capability help.
No Inspector probe, guest boot, media inspection, playback, Claude import session or ChromeOS
extraction occurred. Owner findings stay labelled as such. The companion's historical Delphi/
transport/database details still require matching help/media verification in the follow-up.
