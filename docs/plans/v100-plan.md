# dev-setup-chromebook v100 plan

Nov 1, 2026 (item 1) · Nov 6, 2026 (items 2–16 added; owner choices recorded) · **final: approved for the build on `release/v100`**

## Items at a glance

Item 1 was drafted Nov 1. Items 2–16 are the owner-confirmed scope from hands-on install-retro testing
on a long-term Chromebook with `/dev/kvm` (Nov 5–6, 2026); each records the finding, the owner's
decision and the requested change. The detailed proposals below verify v99 code locations, describe migration and validation, and
list owner choices. They are recommendations for review, not build approval.

| # | Item | Kind |
|---|---|---|
| 1 | Inspector offline cache coherence | fix (investigate first) |
| 2 | NuGet steps hang where IPv6 to api.nuget.org fails | fix |
| 3 | win95 hangs on its first boot after Setup (`mount x` becomes an IDE disk) | fix |
| 4 | Stale-frame flicker in a maximized win95 window: `output=surface` | default change |
| 5 | Windows 2000 crawls/hangs at "Starting up…" on nested KVM: default to TCG | default change |
| 6 | QEMU tablet pointer misaligned: `zoom-to-fit=off` for win2000 | default change |
| 7 | win2000 sound: default `SOUND=none` | default change |
| 8 | Exchange disk takes C: (and loses its letter) during NT/2000 Setup | fix |
| 9 | Misleading accel message when `ACCEL=tcg` is configured | fix |
| 10 | Failed `winetricks corefonts tahoma` is silent; `win31 fonts` then finds nothing | fix |
| 11 | Loose-file media for real guests: `genisoimage` + docs | feature |
| 12 | Wine color schemes with built-in Breeze Dark: `delphi N colors` | feature |
| 13 | DOSBox-X host key `ctrlshift` by default | default change |
| 14 | `win95 net on\|off` | feature |
| 15 | Delphi under Wine: documentation findings | docs |
| 16 | DOSBox-X and QEMU guests: documentation findings | docs |

Deferred to v101 (recorded at the end): the Delphi DCOM/multi-tier database demo and the guest
network test plan.

## Owner decisions (Nov 6, 2026)

The owner approved this plan for the build with these choices:

| Item | Choice |
|---|---|
| 2 | **2A:** command-scoped IPv4 (`DOTNET_SYSTEM_NET_DISABLEIPV6=1`) for the bundle's NuGet/Gallery acquisition and restore-capable build/runner paths; no IPv6 probe. |
| 3 | **3A:** remove the win95 guest-boot folder mount; keep the standalone IMGMAKE and win31 mounts. |
| 4 | **4A (Nov 6 follow-up):** win95 `output=surface`; add absent settings and upgrade exact v99 `output=opengl` lines; preserve edited lines and duplicates. |
| 5 | **5A (Nov 6 follow-up):** win2000 defaults to TCG; upgrade its untouched v99 ACCEL line; preserve owner edits; winnt40 stays `auto`. |
| 6 | **6A (Nov 6 follow-up):** win2000 defaults to `zoom-to-fit=off`, including its untouched v99 DISPLAY_OPTS line; preserve owner edits. |
| 7 | **7A (Nov 6 follow-up):** win2000 defaults to `SOUND=none`, including its untouched v99 SOUND line; preserve owner edits; winnt40 unchanged. |
| 8 | **8A:** exchange disk withheld during every `setup` and until `<guest> exchange enable`; existing installs need a one-time enable. |
| 9 | **9A:** report the selected acceleration and its reason consistently in helper, setup, init and test. |
| 10 | **10A:** one automatic font retry, saved diagnostics, a prominent non-fatal result, status and a prefix-qualified repair command. |
| 11 | **11A:** install `genisoimage` and document ISO creation; `cd` stays ISO-only (`cd FOLDER` not in v100). |
| 12 | **12B:** ship the `delphi1 colors` / `delphi N colors` switcher with the `default` scheme and support for validated owner-supplied `.reg` schemes; **do not bundle breeze-dark** (no license grant observed). The owner keeps his Breeze Dark file locally as a user scheme. Preserve existing themes until an explicit switch. The values table in item 12 stays as the record of the owner's local scheme, not shipped data. |
| 13 | **13A:** `hostkey=ctrlshift` under `[dosbox]`; preserve existing choices; report a misplaced `hostkey` rather than moving it. |
| 14 | **14A:** keep IRQ 3; add `[serial] serial2=disabled` only when absent; refuse custom conflicts; manage only helper-owned blocks. |
| 15 | **15A:** publish the qualified Delphi 1/3 observations, including the limited OCX finding. |
| 16 | **16A:** publish the qualified manual procedures; verify shortcuts during acceptance. |

**Acceptance scope for item 8:** no separate fresh win2000 reinstall workspace. Item 8's fresh-install
behaviour (Setup installs to C:, resumed boots stay detached, then `exchange enable`) is accepted on
the owner's first winnt40 install, which is a fresh install anyway. The existing win2000 guest is
checked as an existing install: one-time `win2000 exchange enable`, then the exchange drive works.

Item 1 is **paused by the owner (Nov 6)**. Resume on a machine with `install-agentic`, using the
bundle's own setup and its investigation-first gate with approval for each real command. Do not
create an Inspector environment under `assets/tools`; a hand-built environment would not reproduce
the bundle context. Stages 1–7 are built; Chromebook acceptance remains pending.

## Scope and baseline

The owner accepted v99 in [PR #13](https://github.com/dhouse109/dev-setup-chromebook/pull/13)
with two known non-credential WARNs: offline Inspector cache availability and environmental disk
headroom below the model reserve. The final test returned to the prompt without Ctrl+C.
Inspector ENOTCACHED pre-existed v99 and is not classified as a v99 regression.

This plan starts on `plan/v100`; implementation belongs on `release/v100` after the owner approves
the plan (v99 was merged into `main` on Nov 1). The draft PR targets `main` and contains only this plan. It does not
implement a fix, bump script versions, authorize running setup/init/test/demo, or authorize merging
either PR. Disk reserve changes, cache purges and unrelated stack changes are outside item 1.

## 1. Inspector offline cache coherence

### Evidence

Repo-relative local evidence (raw logs remain local):

- `assets/logs/dev-setup-20261101-115925.output`: setup reaches all 79 selected stages.
- `assets/logs/inspector-cache-20261101-115925.log`: real online and offline tools/call both exit 0
  and return result 5 during setup's warm-up.
- `assets/logs/dev-test-20261101-130201.log`: global Inspector's real call passes, but the real
  `npx --offline` call exits 1 with ENOTCACHED for the package's registry response.
- The completed full test reports PASS 594, FAIL 0, WARN 11, SKIP 1. This issue is one of the two
  non-credential WARNs explicitly accepted for v99.

An installed global executable and an immediately successful warm-up do not establish that a
later npx invocation can resolve the same package from the same cache without registry access.
No cache deletion, Node version mismatch or registry change has yet been proven as the cause.

### Setup versus dev-test comparison

| Input | Setup warm-up in v99 | Dev-test in v99 | Finding / missing evidence |
| --- | --- | --- | --- |
| Node | Node stage selects installed LTS; run log reports v26.13.0 | Managed nvm default activation; run log reports v26.13.0 | Recorded versions match. Capture the executable identity at each actual probe before excluding a shim/PATH difference. |
| npm / npx | Run log reports npm 11.20.0; npx follows selected Node | Run log reports npm 11.20.0; npx follows activated default Node | Recorded npm versions match. Probe-level executable/config identities are not recorded. |
| Global Inspector | `npm install -g @modelcontextprotocol/inspector@latest` | Global version check reports 2.13.0, then a successful global tool call | Global installation and npx's execution cache are separate checks. |
| Online package spec | `npx --yes @modelcontextprotocol/inspector ...` | No online acquisition in the offline assertion | Global install uses explicit `@latest`; the warm-up uses the bare package. |
| Offline package spec | `npx --offline @modelcontextprotocol/inspector ...` | Same bare package, same real tools/call operation | Both use the bare spec, not explicit `@latest` or an exact version. Test each form; do not assume identical resolution/cache identity. |
| Registry | Inherited effective npm configuration; no effective registry snapshot | Error names the public npm registry; effective configuration not captured | The error's URL does not prove warm-up used identical configuration. Compare registry origin and scoped-registry selection without reading or publishing credentials. |
| Cache path | Inherited effective npm cache; not recorded at warm-up | Inherited effective npm cache; not recorded at the assertion | Compare canonical cache paths locally. Do not infer the cache path from npm's debug-log path. Public reports contain only matching/different results or repo-relative paths. |
| Working directory | Caller directory; no managed Inspector cwd | Test scratch directory | npm project configuration and local dependencies can differ. Capture this context and normalize bundle-owned probes. |

Code reviewed: Inspector block in `dev-setup-chromebook.sh`; environment activation and Inspector
assertion in `dev-test-chromebook.sh`; `tests/warm-inspector-cache.py`. The installed FastMCP CLI
builds a bare Inspector spec by default and appends an explicit version when its Inspector-version
option is supplied. Verify that supported option again against the installed CLI before building
any launcher; do not assume a different invocation uses the same npm cache.

### Investigation before implementation

1. At setup warm-up and immediately before the offline assertion, compare Node/npm/npx executable
   identity and versions, exact package spec, effective registry/scoped registry, effective cache
   path and working-directory category. Use allowlisted individual properties, not config dumps,
   credential files, environment dumps or verbose request headers. Keep any absolute path comparison
   local; publish only equality/results and repo-relative evidence paths.
2. In isolated bundle-owned test caches, compare the bare spec, explicit `@latest` and one exact
   installed version. For each, run the real online tools/call once, then the identical invocation
   with strict `--offline`, both immediately and from the later test context. Record producer status
   and result 5, not only a package listing or a no-op command.
3. Repeat the successful pair after the intervening full workflow and a new terminal/Linux session.
   Inspect cache existence/identity without deleting the user's cache. Correlate any difference with
   the recorded context before attributing the failure to npm eviction, version drift or a bug.

These real commands require individual owner approval. This draft performs no new warm-up,
installation, cache mutation or service start.

### Recommended change, pending owner approval

Use an exact Inspector release and an explicit, bundle-owned execution-cache context for the
bundle's offline contract. Keep the general global CLI available separately.

1. After a successful global install/update, read its installed Inspector version once. Record that
   exact version for the warm-up and dev-test; do not resolve mutable `latest` during dev-test.
2. Warm `@modelcontextprotocol/inspector@<recorded-version>` through the real npx tools/call using
   an explicit cache under `assets/tools/mcp-inspector/npm-cache` and a stable bundle-owned cwd.
   Verify the identical strict-offline call before publishing a new successful record. Retain the
   previous usable record on acquisition or verification failure.
3. Make dev-test use that same spec/cache context with `--offline`, preserving full producer output,
   status and the result-5 assertion. Missing/mismatched cache remains an honest WARN; the assertion
   must never download or repair its own prerequisites. `--prefer-offline` is not sufficient.
4. Preserve the FastMCP use case: provide a small generated launcher or documented invocation that
   passes the same cache and recorded Inspector version using FastMCP's supported version option.
   Set npm cache/offline options only for that command and its children. Do not rewrite user/global
   npm configuration or claim an unqualified default FastMCP invocation shares the managed cache.
5. Record only safe version/spec/result metadata under `assets/tools/mcp-inspector`; keep diagnostics
   under `assets/logs`. Include the managed cache in the agentic disk-report line and document its
   offline contract. Avoid duplicate downloads where npm can safely reuse content.

This is the recommended design, not a root-cause claim or an approved implementation. If the
investigation shows a smaller explicit spec/context correction reliably fixes the original default
cache path, present that evidence before adding a managed cache or launcher. Do not replace the npx
test with the passing global executable and call cache coherence fixed.

### Validation and completion criteria

- An isolated cold cache produces an honest offline failure; online warm-up followed by strict
  offline real tools/call returns 5 with status 0 from both managed contexts.
- Bare, explicit `@latest` and exact-version comparisons identify which context/spec is actually
  used. A deliberate cache/context mismatch is diagnosed without a test-time download.
- Repeat setup reuses the recorded release/cache when current; a failed update preserves the last
  usable record and never prints a success claim for a failed warm-up.
- A new terminal/Linux session and the full intervening workflow retain the offline result. Verify
  the documented FastMCP invocation separately; UI/global CLI success alone is insufficient.
- Keep all flags/expansion logic identical across the four scripts. At implementation time bump all
  four to v100 and update CHANGELOG, README, init checklist and disk-report/docs as appropriate.
- Before each push run all-four Bash syntax and error-level ShellCheck plus secret checks. Use
  focused regressions for spec/context/status propagation and owner-approved targeted real runs,
  followed by the owner-approved full acceptance route.
- Public PR comments contain counts, results and repo-relative paths only; no PIDs, hardware or
  kernel details, auth status, home-directory paths or raw logs.

### Primary references

- [npm exec: package resolution and strict offline caching](https://docs.npmjs.com/cli/v11/commands/npm-exec/)
- [npm package specifications](https://docs.npmjs.com/cli/v11/using-npm/package-spec/)
- [npm configuration precedence](https://docs.npmjs.com/cli/v11/using-npm/config/)

npm documents that npx uses npm exec's cache and strict offline mode fails when required cached
data is missing; configuration can vary by command context. Those contracts motivate the
comparison above, but do not establish which input caused the recorded ENOTCACHED.

## Items 2–16: owner-confirmed scope (Nov 6, 2026)

These items come from hands-on testing of v99's `install-retro` (and, for item 2, v99's dev-demo) on
long-term Chromebooks, worked through with a Claude chat session. Each item gives the finding, the
owner's decision and the requested change. The planning agent turns each into a concrete design: code
locations, the exact change, dev-test checks, doc updates and how the owner verifies it. Where an item
leaves a design question open, the plan proposes an answer for the owner to approve rather than guessing.

General constraints for all of them:

- The guest config files (`~/win31/dosbox-x.conf`, `~/win95/setup.conf` and `boot.conf`,
  `~/<guest>/config`, `~/.config/dev-retro/dos.conf`) are written once and never overwritten, by
  design. A new default reaches new installs automatically; for existing machines, each item says
  whether setup should add a missing line (only when the setting is absent, never overriding a value
  the owner set) or only document the change.
- Owner-run checks of real guests need the owner's licensed media and happen on the owner's
  Chromebooks; dev-test can verify generated files and helper behaviour, not a Windows install.
- All source locations below were read against v99, `main` at `5c1a3b8`; the four scripts on
  `plan/v100` are identical to that baseline. Ranges include the relevant branch/function, not just
  the old starting-point line. Re-find symbols before editing after earlier stages move lines.
- **Heredoc boundary:** setup lines 10051–11764 write the shared `dev-retro` helper using
  `DEVRETRO_EOF`. Functions called out inside that range are generated helper code, not setup-time
  commands. Win31's config (10023–10047), packages (9946–9961), and QEMU config generation
  (11777–11801) are outside it. `win95_confs` and `dos_conf` run lazily in the helper; setup does
  not currently create their files.
- **Migration rule (owner amendment, Nov 6):** add absent keys and preserve owner edits. For
  items 4–7 only, also upgrade a line byte-identical to the v99 template, including its value,
  spacing and trailing comment; allow extra ASCII spaces at the end. This is an owner-authorized
  exception to the earlier absent-only rule. Any other change (value, comment, case, indentation,
  spacing or trailing tab) remains untouched. Duplicate target assignments require manual review
  and stay unchanged; a duplicate target in win2000/config defers migration of that entire file. Match win95 output only under `[sdl]`. Retain line endings,
  final-newline presence and modes. Add absent keys in the correct section without duplicates. Ignore
  commented-out assignments when deciding absence; recognize whitespace and case for DOSBox-X INI
  keys. For sourced shell configs recognize assignments with optional `export` and spaces around
  the line, and avoid appending a competing assignment when syntax is ambiguous. Report it for
  owner review. Never evaluate an existing config merely to migrate it. Skip writes while the
  affected guest runs and report the deferred update. Config updates use a same-directory temporary
  file and atomic replacement, retaining file permissions. Apply default migration from setup
  for files already present, and from helper config creation/launch for lazy files.
- **Validation boundary:** `check`/`slow` means FAIL for bundle-owned behaviour; `warn`/`slowwarn`
  means a user-changeable preference or optional font availability. Use isolated HOME/workspace
  fixtures and fake engine executables to capture argument arrays without starting guests. Never
  point mutation tests at real guest configs, disks or Wine prefixes. No licensed media is needed
  for these regressions. Guest installation, rendering, pointer and application behaviour remain
  owner acceptance checks. Test-time repair/downloads of guest settings are forbidden.
- **Build-time docs contract (applies to every item):** update `README.md` (current version and
  affected flag descriptions), `docs/init-checklist.md` (init → setup → init → test and manual
  guest steps), all four `CHANGELOG.md` sections, and all four version strings only when building
  v100. No new flags are proposed; keep flag expansion identical. Each item lists its additional
  docs/STEP targets below; a stated “none” means no extra change beyond this shared contract.
  Generated STEPS sources are the heredocs in dev-demo, never an edit to an installed copy.
- **Disk accounting:** extend retro's existing lines in dev-test 6045–6063: include helper/config
  storage (`.local/lib/dev-retro`, `.config/dev-retro`), new font logs in assets, and item 11's
  package. Guest workspaces already count exchange disks and app ISOs; don't add them twice.
  Items changing only defaults, arguments or prose add no separate disk allocation.
- **Questions:** each item ends with A/B choices, recommended first. `2A`, for example, means
  item 2 choice A. Nothing here authorizes a script run or guest start.

### 2. NuGet steps hang where IPv6 to api.nuget.org fails

- **Finding (Nov 2):** with the six-flag v99 install, dev-demo's NuGet-based steps
  (`dotnet/vb-spectre`, `pwsh/spectre-demo`) hung. On that Chromebook IPv6 connections to
  api.nuget.org failed while IPv4 worked; rerunning dev-demo with `DOTNET_SYSTEM_NET_DISABLEIPV6=1`
  completed every demo.
- **Decision:** in v100.
- **Verified locations:** dev-demo 748–831 (`demo_dotnet`: C# generated runner at 758,
  VB creation/add-package at 772–773 and runner at 829); 834–861 (`demo_pwsh`: Save-PSResource
  with Save-Module fallback at 841–843, generated runner at 854–858). The generated BDD runner's
  Reqnroll path is 9093–9106 (new/add/build/test). Setup's only NuGet acquisition commands are
  Reqnroll template update/install at 7133–7140; SDK apt installation at 2419–2444 is not NuGet.
  Dev-test restores/builds at 1694–1697 (C#/VB/mixed), 2260 (Godot .NET, including its
  `godot-mono` parent process), and 3081–3124 (Reqnroll). Init 2202–2219 only checks SDK/certs;
  init 2028–2033 lists templates, so neither needs a network workaround.
- **Proposed change:** set `DOTNET_SYSTEM_NET_DISABLEIPV6=1` on the acquisition/build process
  or a tightly scoped subshell encompassing the relevant sequence. Include child processes of
  `godot-mono`, PowerShell's Gallery acquisition, and generated C#/VB/Reqnroll runners because
  their build/run can restore implicitly. Keep the producer's exit status and existing timeout/
  error reporting. Do not export it script-wide, in bashrc, or in NuGet/global network settings.
  Use the deterministic workaround rather than a preliminary IPv6 probe: one probe's success
  says little about a later CDN endpoint. Runtime-only `--no-build` calls need no new setting.
  Microsoft's [.NET variable documentation](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-environment-variables#dotnet_system_net_disableipv6)
  confirms the name and value. There is no `dotnet tool install` in v99 to patch.
- **Existing machines:** no guest config migration. Dev-demo rewrites its bundle-owned runners;
  rerun it without refresh to update runners while keeping existing projects/modules. Scope the
  build env in these regenerated runners too; no wrapper around the owner's general dotnet/pwsh.
- **Dev-test:** retain the real C#/VB/Godot/Reqnroll build checks as FAILs; add one bounded NuGet
  service-index reachability `warn`: a tiny package-free C# HttpClient GET of
  `https://api.nuget.org/v3/index.json`, 10-second client timeout and 20-second process timeout,
  with the same .NET setting and a network/DNS hint on failure,
  rather than claiming a hang proves IPv6 is broken. At build time use process stubs to confirm
  all restore-capable paths inherit the variable and unrelated commands do not. No guest/media
  verification needed. Owner confirms VB demo acquisition and PowerShell Gallery download complete
  without manually exporting the variable; cached success alone is insufficient evidence.
- **Docs:** shared contract; `docs/crostini-gotchas.md` Network, `docs/dev-demo.md` .NET/PowerShell
  and BDD notes. No retro STEPS change or new cache disk row; existing .NET cache rows stay.
- **Owner choice:** **2A (recommended):** command-scoped IPv4 for these bundle operations.
  **2B:** detect IPv6 failure first, accepting extra probe latency and incomplete coverage.

### 3. win95 hangs on its first boot after Setup

- **Finding (Nov 5):** after a complete Windows 95 OSR2 Setup (both parts), every `win95` boot
  stopped at a blank screen after the logo. DOSBox-X's log ended with
  `C/H/S 0/0/1 out of bounds 0/16/63` and `IDE abort dh=0xb0 with error on 0x170`. `win95_cmd`
  passes `-c "mount x \"$WS\""` (setup line 10599); on `boot c:` DOSBox-X converts that folder drive
  to a temporary FAT disk on the secondary IDE slave, and Windows 95's protected-mode IDE driver hangs
  probing it. Booting with only `hdd.img` and the CD reached the desktop; removing the `mount x`
  from the installed helper by hand fixed `win95` with the exchange disk and app CD attached. The
  exchange disk was ruled out (500 MB and 255-head disks both still hung with X: present).
- **Decision:** remove the folder mount from guest boots.
- **Verified locations:** inside setup's generated helper, `win95_cmd` 10568–10638;
  shared `args` initialization is 10599, standalone IMGMAKE 10606–10607, guest image/CD mounts
  10613–10618, and `boot c:` 10632. This shared array reaches `boot`, `run`, and resumed `setup`.
  `win31_cmd` 10475–10522 starts `win` on folder-mounted DOS drives and never calls `boot c:`.
- **Proposed change:** change only shared initialization to `args=(-conf "$conf")`. Keep the X:
  mount and `x:` in the isolated IMGMAKE invocation, which exits before any guest boot. Preserve
  hdd, exchange and both ISO image mounts. No X: mount is needed for the first setup session either.
  Read-only comparison with the installed helper found exactly this one-line change and no other
  differences from v99's heredoc; this corroborates the owner's successful hand fix. Setup replaces
  that helper each run, so the fix must live in the heredoc. Leave win31's required folder mounts.
- **Existing machines:** replacing the generated helper fixes all launches without touching config
  files or disk contents. If an owner has added folder mounts to `[autoexec]`, warn and document
  removing those before `boot c:`; do not delete custom commands automatically.
- **Dev-test:** extend the isolated win95 harness at 5614–5642 with a fake DOSBox-X capturing NUL-
  separated arguments for boot, run and both setup phases. FAIL on any guest-boot `mount` folder
  command, require `boot c:` in the applicable phases and keep IMGMAKE's X: command in its separate
  invocation. A source grep alone would wrongly reject IMGMAKE. Owner alone verifies completed OSR2
  setup reaches the desktop, then boot/run with exchange disk and app CD still work.
- **Docs:** shared contract; `docs/crostini-gotchas.md` Retro, `docs/dev-demo.md` matrix and
  generated `STEPS-delphi.md` (4360–4440) win95 setup/troubleshooting. No new storage.
- **Owner choice:** **3A (recommended):** the one-line shared-array fix, preserving IMGMAKE and win31.
  **3B:** additionally remove owner-added config mounts manually after reviewing them.

### 4. Stale-frame flicker in a maximized win95 window

- **Finding (Nov 5):** with DOSBox-X's window maximized, the area around the guest picture flickers
  with stale frames under `output=opengl`. `output=surface` in `~/win95/boot.conf` fixed it.
  Separately, switching the output mode from the Video menu while Windows 95 ran blanked the window
  and left it unusable; toggling the same options in win31 (which runs `output=opengl`) worked.
- **Decision:** `output=surface` for win95's `setup.conf` and `boot.conf` (the `base` template at
  setup line 10528). win31 and `dos.conf` keep their current output. No other video default changes.
- **Verified locations:** generated helper `win95_confs` 10528–10567, `base` output at
  10532 feeds both setup.conf and boot.conf. Win31 output at 10030 and `dos_conf` output at 11683
  are separate templates and remain as they are.
- **Proposed change / existing machines (Nov 6 follow-up):** set only win95 base `output=surface`.
  Add absent `output` under `[sdl]` in existing setup.conf and boot.conf. Also replace exactly
  `output=opengl` (optionally followed by ASCII spaces), the v99 template line, with
  `output=surface`. Keep every edited value/comment/spacing/case and duplicate assignment.
  Defer the whole guest while running. Preserve CRLF, modes and final-newline presence; repeat
  runs are stable. win31/DOS are unchanged. Never change the live renderer via the menu.
- **Dev-test:** FAIL fresh-config fixtures unless both win95 configs say surface. Verify missing-
  key migration, exact-v99 upgrades in both files, repeat-run stability, running-guest deferral,
  and preservation of edited values/comments/duplicates. On real
  configs `warn` for an output other than surface, naming the recommendation, not a failed install.
  Owner checks maximized redraw and cold startup with his Windows 95 media; no automated UI claim.
- **Docs:** shared contract; `docs/crostini-gotchas.md` rendering finding, `docs/dev-demo.md`,
  `STEPS-delphi.md` and item 16's shutdown-first guidance. No new disk usage.
- **Owner choice:** **4A (approved, amended Nov 6):** upgrade untouched v99 lines and fill absent
  output; preserve owner edits/duplicates. **4B:** manual-only migration (superseded by the amendment).

### 5. Windows 2000 crawls or hangs at "Starting up…" on nested KVM

- **Finding (Nov 5):** `win2000 setup`'s first graphical boot sat at "Starting up…" for over five
  minutes, the splash painting slowly top to bottom with QEMU above 100% CPU. HPET off, a PS/2 mouse
  and `SOUND=none` did not help; `ACCEL=tcg` got through, and Setup completed under TCG. ChromeOS's
  `/dev/kvm` is nested, so the many VGA and IDE port exits of an old guest's boot are expensive.
- **Decision:** default win2000 to TCG always, until a KVM boot of an installed system is shown to
  be faster.
- **Verified locations:** generated helper `qemu_config` 10690–10702 currently sets
  `ACCEL=auto` in the shared assignment at 10695; `pick_accel` is 10703–10717. Outside the heredoc,
  setup's write-once QEMU config loop is 11777–11801, ACCEL line 11797. Setup's KVM announcement
  9966–9974 and dev-test 5578–5584 currently imply both guests will always use available KVM.
- **Proposed change:** put ACCEL in guest-specific defaults: win2000 tcg, winnt40 auto; remove the
  shared assignment which would override them. Give the config-generation loop matching R_ACCEL
  values and a v100 comment linking win2000's TCG default to the Nov 5 nested-KVM finding. Keep
  explicit auto/kvm supported. Replace “close to native” promises with capability/selection wording
  (item 9), including setup, init's retro note at 2261–2315, and test information.
- **Existing machines (Nov 6 follow-up):** add absent `ACCEL=tcg`; also replace the exact v99
  line `ACCEL=auto              # auto (KVM when /dev/kvm is usable), kvm or tcg`
  with `ACCEL=tcg              # auto (KVM when usable), kvm or tcg; explicit owner values stay`.
  Only optional trailing ASCII spaces may differ. Preserve edited values/comments/spacing and
  duplicates; defer a running guest. v99 wrote this explicit line on every retro install, so
  absent-only migration missed existing machines. NT configs stay unchanged; no NT KVM performance
  claim. Use the shared conservative parser and atomic replacement, without sourcing the config.
- **Dev-test:** FAIL fixture defaults/config templates that disagree; test explicit overrides and
  missing-key and untouched-v99 migration (full v99 config fixture), CRLF/modes, repeat runs, edited
  values/comments/spacing, duplicates and running deferral. Real win2000 non-tcg selection is a
  `warn` explaining the fallback; do not
  FAIL for usable KVM or benchmark it automatically. Owner verifies install, graphical reboot,
  login, idle and installed-system boot under TCG. NT installation remains owner-media verification.
- **Docs:** shared contract; `docs/crostini-gotchas.md` Retro, `docs/dev-demo.md`, `STEPS-winnt.md`
  4441–4486 and `STEPS-delphi.md`: distinguish NT auto from 2000 tcg, and describe the optional NT
  fallback without claiming it was tested. No disk increase.
- **Owner choice:** **5A (approved, amended Nov 6):** win2000 tcg, NT auto; upgrade untouched v99
  lines and preserve edits/duplicates.
  **5B:** also default NT to tcg, requiring NT-specific evidence before adopting that extra change.

### 6. QEMU tablet pointer misaligned

- **Finding (Nov 5):** with the USB tablet, Windows' pointer did not line up with the host pointer.
  Unticking View > Zoom To Fit fixed it (the README already suggests `zoom-to-fit=off` for a sharper
  picture, setup line 11518).
- **Decision:** `DISPLAY_OPTS="gtk,zoom-to-fit=off"` as the win2000 default. winnt40 uses a PS/2
  mouse; the plan proposes whether it changes too.
- **Verified locations:** generated helper shared `DISPLAY_OPTS` at 10695, QEMU use
  at 10760, existing `fonts_readme` sharp-picture advice at 11513–11520. Outside the heredoc, the
  config template sets it at 11798. Dev-demo STEPS-winnt sharp-pixel advice is at 4474–4477.
- **Proposed change:** make display default guest-specific alongside item 5: win2000
  `gtk,zoom-to-fit=off`, NT `gtk,zoom-to-fit=on` (PS/2 unchanged). Use matching R_DISPLAY in the
  written config. Explain the smaller unscaled picture and raising screen area in Windows Display
  Properties; do not force a guest resolution or change MOUSE.
- **Existing machines (Nov 6 follow-up):** add absent DISPLAY_OPTS; replace only exact
  `DISPLAY_OPTS=gtk,zoom-to-fit=on` (optional trailing ASCII spaces) with
  `DISPLAY_OPTS="gtk,zoom-to-fit=off"`, matching the new template. Preserve edited values,
  comments, quoting, spacing and extra GTK options; duplicates stay unchanged, running guests defer.
- **Dev-test:** FAIL mismatched fresh defaults and QEMU captured `-display` arguments; preserve
  custom options, edited comments and duplicates in fixtures. The shared full-v99 fixture upgrades
  display alongside items 5/7 and checks running deferral/repeat runs. Real win2000 zoom on is a
  `warn`, NT on is expected. Owner verifies
  tablet alignment at several picture positions and a larger guest resolution after cold launch.
- **Docs:** shared contract; `docs/crostini-gotchas.md` pointer finding, `docs/dev-demo.md`,
  `STEPS-winnt.md`, `STEPS-delphi.md`, and helper-generated fonts README sharp-picture paragraph.
- **Owner choice:** **6A (approved, amended Nov 6):** change only win2000, including untouched
  v99 lines while preserving edits/duplicates. **6B:** also unscale NT despite no
  matching pointer finding (a separate preference, requiring owner confirmation).

### 7. win2000 sound: default `SOUND=none`

- **Finding (Nov 5):** with the AC97 card, the terminal fills with repeated
  `pulseaudio: set_sink_input_volume() failed … Invalid argument` lines during boot. Turning the card
  off did not fix item 5, so the errors were not its cause, but they serve no purpose for the
  development use of the guest.
- **Decision:** default `SOUND=none` for win2000; investigating working guest audio is a later item.
- **Verified locations:** helper win2000 `SOUND=AC97` at 10693; `audio_args`
  10718–10726; QEMU audio array append at 10784–10785. Setup R_SOUND at 11782 and config SOUND
  at 11795 are outside the helper. NT remains sb16 at 10692/11780.
- **Proposed change:** win2000 SOUND=none in both defaults; keep the early return in audio_args
  so none adds no emulated sound card or audio backend. Document opting back into AC97 with the
  guest stopped, driver installation from the owner's CD, and possible PulseAudio errors. Preserve
  the historical finding that disabling audio did not solve the boot slowdown.
- **Existing machines (Nov 6 follow-up):** add absent SOUND; replace only exact
  `SOUND=AC97             # sb16, AC97 or none (drivers on the install CDs)` with
  `SOUND=none             # sb16, AC97 or none (drivers on the install CDs)`. Optional trailing
  ASCII spaces are allowed. Preserve edited values/comments/spacing and duplicates; running guests
  defer. A bare owner `SOUND=AC97` remains an override. NT sb16 stays unchanged.
- **Dev-test:** FAIL fresh/default fixture mismatch; captured win2000 launch must omit `-audiodev`
  and sound `-device` when none. The full-v99 fixture upgrades all three settings; edited values,
  comments, duplicates, modes/CRLF and running deferral are tested. Assert explicit AC97 override
  still reaches audio_args. A real
  enabled win2000 card is `warn` with the quiet default recommendation, not a bundle failure.
  Owner confirms quiet boot and application use; working guest audio is deferred.
- **Docs:** shared contract; `docs/crostini-gotchas.md` audio finding, `docs/dev-demo.md`,
  `STEPS-winnt.md` (remove automatic AC97 assumption for 2000), `STEPS-delphi.md` if referring to
  audio. No new disk row.
- **Owner choice:** **7A (approved, amended Nov 6):** silence win2000 only; upgrade untouched
  v99 lines and preserve owner edits/duplicates.
  **7B:** additionally silence NT, pending separate NT audio evidence.

### 8. Exchange disk takes C: (and loses its letter) during NT/2000 Setup

- **Finding (Nov 5–6):** `qemu_launch` always attaches `exchange.img` as the primary slave (line
  10763). The exchange disk is partitioned and formatted before Setup runs while the new system disk
  is blank, so Windows 2000 Setup assigned **C:** to the exchange disk and installed Windows to F:.
  The workaround was: create the system partition, quit Setup with F3, boot the CD again, so the
  system partition is enumerated first and becomes C:. During those attempts the exchange disk's
  partition was deleted, so it later appeared in Disk Management as unallocated with no letter;
  `win2000 exchange recreate` with the guest off restored it, and `put` / `get` worked again.
- **Decision:** don't attach the exchange disk until the guest's Windows is installed.
- **Verified locations:** helper `installed` 10219–10232 returns true for NT/2000
  merely when disk.qcow2 or disk.img exists; it cannot prove Windows is installed. `qemu_launch`
  10757–10794 attaches exchange unconditionally at 10763. `nt_cmd` 10796–10858 creates/attaches
  during initial setup, resumed setup, normal boot and run. Exchange operations are 10315–10378;
  common dispatch 11752–11753; status reports “disk created” at 11606. Reading a qcow2's host
  file bytes with mtools would not establish guest installation and NTFS is outside mtools.
- **Proposed change:** require an explicit completion acknowledgement, `<guest> exchange enable`,
  after the owner reaches the installed Windows desktop and shuts down. `exchange disable` clears
  it; `exchange info` and status show enabled, deferred or stale. Store the enabled system disk's
  canonical path and file device/inode in a small `exchange-enabled` config record under the guest
  workspace (already counted). Write it only with the guest stopped and a system disk present.
  Match it to the currently selected disk; a missing/replaced disk requires enable again. Normal
  boot/run attach index=1 only with a matching record; otherwise print “Exchange disk withheld
  until Windows installation is complete; after shutdown run '<guest> exchange enable'.”
- **Setup rule:** every `setup`, including resumed disk boot and `--from-cd`/`--raw`, withholds
  exchange regardless of record. Starting a setup command clears the old acknowledgement so a
  reinstall cannot silently reuse it. Setup-time exchange image creation may stay (it is harmless
  while detached); leave its FAT layout/data alone. Both CD drives keep their IDE indexes, but
  drive letters during installation are provisional; E:/F: describe the final layout after exchange
  is enabled and Windows assigns letters. `put`/`fonts` may prepare an exchange disk before enable,
  but print that it is withheld; they never acknowledge installation. `run` must fail before copying
  or launching if exchange is withheld, giving the enable command, rather than promising D: access.
  This is more reliable than trying to recognize complete Windows from boot files halfway through
  setup. It adds one manual step but works for FAT/NTFS, qcow2/raw and all resumed setup paths.
- **Existing machines:** no automatic inference from an existing disk or exchange image. Existing
  installed NT/2000 guests need a one-time `exchange enable` after confirming their desktop. No
  config assignment is overwritten, and no disk partition is changed. A snapshot restore normally
  keeps the disk inode; an externally replaced disk safely invalidates the record. Restoring a
  pre-install snapshot requires `exchange disable` before resuming Setup; document this explicitly.
  Do not try to rename an already installed Windows system from F: to C: automatically.
- **Dev-test:** FAIL isolated argument captures for either guest if index=1 appears during initial,
  resumed, CD/floppy/raw setup or unacknowledged boot; require it for acknowledged boot/run. Test
  enable/disable, missing/replaced disk, setup clearing the record, stopped guard, pending put/fonts,
  and run rejection. Exchange round-trip check at 5600–5612 remains independent of attachment.
  Real absence of enable is info/SKIP for uninstalled guests, `warn` for an owner expecting exchange;
  never call disk existence “installed”. Owner alone verifies fresh NT/2000 text/graphical setup
  installs to C:, all resumed boots stay detached, then enabling supplies a usable FAT exchange drive.
- **Docs:** shared contract; `docs/dev-demo.md`, `STEPS-winnt.md`, `STEPS-delphi.md`,
  `docs/crostini-gotchas.md` Retro. Include the enable step; old-version F3/reboot workaround only
  before installing Windows; Disk Management letter assignment; back up with `get` before
  `exchange recreate`; format/recreate only from Linux because mtools expects this FAT layout.
  Recreate cannot recover files from a partition the owner deleted; stop rather than promise recovery.
- **Owner choice:** **8A (recommended):** explicit completion/enable step with setup always detached.
  **8B:** withhold only during `setup`, attach on ordinary boot; simpler but an accidental normal
  boot mid-install can still take C:, so it does not fully enforce the requested protection.

### 9. Misleading accel message when `ACCEL=tcg` is configured

- **Finding (Nov 5):** with `ACCEL=tcg` in `~/win2000/config` on a Chromebook that has a usable
  `/dev/kvm`, the launch line said "software emulation (TCG; no /dev/kvm on this Chromebook:
  slower)" (`pick_accel`, line 10712).
- **Decision:** fix the message.
- **Verified locations:** helper `pick_accel` 10703–10717 and QEMU launch report at
  10788. Capability claims also occur in setup 9966–9974, `retro_cmd` 11700, dev-test 5578–5584
  and init's install-retro block 2261–2315. Selection comes from qemu_config plus the owner's config.
- **Proposed change:** test explicit tcg first: “software emulation (TCG; selected by ACCEL=tcg)”.
  Otherwise select KVM only for readable/writable character device: “KVM (selected by ACCEL=auto)”
  or “KVM (selected by ACCEL=kvm)”. No character device: “software emulation (TCG; /dev/kvm
  unavailable)”. Present but inaccessible: retain the group-membership/reopen-Linux hint and say
  “software emulation (TCG; /dev/kvm present but not usable)”. Preserve explicit-kvm fallback NOTE,
  but do not show that hint for intentional tcg. Remove unconditional speed claims. Capability
  summaries must say availability is separate from each guest's configured choice.
- **Existing machines:** no config migration; truthful messages follow current values immediately
  when the helper is replaced. Keep KVM detection/fallback semantics unchanged.
- **Dev-test:** FAIL a fixture matrix over auto/kvm/tcg and usable/absent/inaccessible KVM, testing
  both ACCEL_ARGS and reason text, with mocked predicates/stat (no permission changes to devices).
  Add helper diagnostic output usable by dev-test without launching QEMU. Real chosen preference
  is information, not a FAIL. Owner sees the selected-tcg reason on win2000 launch; no media needed
  to validate message construction itself.
- **Docs:** shared contract; `docs/crostini-gotchas.md` and `docs/dev-demo.md`/`STEPS-winnt.md`
  replace “KVM present means both run with KVM” with selection-aware explanations. No disk change.
- **Owner choice:** **9A (recommended):** selection/reason wording above across all summaries.
  **9B:** patch only pick_accel, leaving conflicting setup/test summaries (not recommended).

### 10. Failed `winetricks corefonts tahoma` is silent

- **Finding (Nov 5):** `win31 fonts` failed with "No fonts found" (line 11531) because
  `winetricks -q corefonts tahoma` had failed during `delphi1 setup`, which printed only a NOTE
  (line 10950; the same in `delphi N setup`, line 11197). Running
  `WINEPREFIX=~/.local/share/wine/delphi1 winetricks corefonts tahoma` by hand fixed it, and
  `win31 fonts` then worked.
- **Decision:** make the failure visible and actionable.
- **Verified locations:** helper `delphi_setup` 10917–10963 (suppressed winetricks at
  10949–10952), `dn_settings` 11188–11207 (11196–11199); `fonts_collect` 11446–11460 currently
  searches only Delphi 1/COM prefixes and download cache, not Delphi 3–7; `fonts_cmd` 11523–11544
  has an unqualified repair command at 11531. Status is 11599–11614; both Delphi command dispatches
  are 11078–11104 / 11387–11427. Dev-test's installed-prefix section is 5691–5738.
- **Proposed change:** factor prefix-specific corefonts/tahoma installation into one helper; check
  real expected `.ttf` files case-insensitively (Arial, Courier New and Tahoma plus bold Tahoma),
  not only winetricks exit status or its verb registry. Retry once only after nonzero/incomplete
  result. **Nov 6 follow-up:** bound each attempt with `timeout -k 10 300` (five minutes plus
  ten-second kill grace); retry once after timeout too. Retain both attempts' output, timeout
  notices and producer statuses (124/137 included) in `assets/logs/retro-fonts-<prefix>-<timestamp>.log`.
  Pass the bundle assets location into the generated helper at build time; do not derive it from cwd.
  On failure print a prominent “INCOMPLETE: fonts missing” final summary with a log path and the exact
  prefix-qualified repair command. Font failure remains nonfatal to an otherwise usable Delphi IDE.
  Add a read-only font-state line to delphi1/delphi N status (no Wine process, just files).
- **Collection and repair:** include all existing Delphi 3–7 Fonts directories in fonts_collect,
  deduplicating by existing font names, before cache extraction. On empty collection print
  `WINEPREFIX="$HOME/.local/share/wine/delphi1" winetricks corefonts tahoma`, then rerun
  `win31 fonts` (or the requesting guest's fonts command). Explain that plain winetricks repairs
  a different default prefix. Do not auto-create prefixes or download from fonts/status/dev-test.
- **Existing machines:** next explicit Delphi setup retries missing fonts; existing font files,
  registry choices and guest config remain intact. No automatic fonts install on bundle setup;
  fontsmooth handling keeps its diagnostic too. Repeated status is strictly observational.
- **Dev-test:** FAIL stub regressions for first-success/no retry, retry recovery, exhausted failures,
  missing winetricks, zero-status but absent font files, simulated timeout/kill (124/137, exactly two
  attempts with the configured bound), prefix-specific repair text and collection
  from a Delphi 3-only fixture. `warn` incomplete fonts in actual existing prefixes; absent optional
  prefixes are info/SKIP. No network font acquisition or mutation of real prefixes in tests. Owner
  checks the repaired prefix supplies `win31 fonts`, then installs/uses fonts inside his guest.
- **Docs:** shared contract; `docs/init-checklist.md` repair steps, `docs/dev-demo.md`, generated
  `STEPS-delphi1.md`, `STEPS-delphi.md`, `STEPS-winnt.md` and helper fonts README. No new Crostini
  workaround (network/font availability is not specific to ChromeOS); count logs in assets/retro row.
- **Owner choice:** **10A (recommended):** one retry, saved diagnostics, prominent nonfatal summary
  and status. **10B:** no automatic retry, same diagnostics and manual prefix-qualified repair.

### 11. Loose-file media for real guests

- **Finding (Nov 5):** most of the owner's Delphi media is loose CD files, which `delphi N setup`
  (Wine) handles, but the real guests' app CD drive only mounts an `.iso`. Building one with
  `genisoimage -o ~/win95/install/apps/delphi3.iso -J -r -V DELPHI3 ~/delphi/install/3` worked and
  Delphi 3 installed from it in Windows 95.
- **Decision:** install-retro installs `genisoimage` (next to `libarchive-tools`, line 9960) and the
  docs show building an `.iso` from a folder.
- **Verified locations:** setup package block 9959–9961 installs libarchive-tools;
  helper `app_resolve` 10411–10416 and `cd_cmd` 10417–10457 accept ISO files, not directories;
  `dn_cdroot`/`dn_installer` 11127–11167 already accept loose files for Wine. Dev-test's win95
  harness 5614–5620 currently skips ISO construction if neither ISO builder is available. Disk
  package row is 6046–6048; demo media instructions are 4407–4428 and 4443–4448.
- **Proposed change:** install Debian `genisoimage` beside libarchive-tools with its own actionable
  failure notice. Recommend the owner's proven `-J -r` recipe rather than xorriso: only ISO/Joliet
  CD authoring is needed, and genisoimage is already understood by the existing harness. Do not add
  `cd FOLDER` in v100: file creation/naming/collision/cache semantics would broaden this small item.
  Document, for example:
  `genisoimage -o "$HOME/win95/install/apps/delphi3.iso" -J -r -V DELPHI3 "$HOME/delphi/install/3"`,
  then `win95 cd delphi3`. Check the destination does not already exist first; output must be outside
  the source tree. Validate/list the resulting ISO with bsdtar and inspect guest filenames. This
  creates an **app data CD**, not automatically a bootable Windows installation CD.
- **Existing machines:** no guest config rewrite or automatic conversion. Setup adds the package;
  owners choose which folders become ISOs and keep existing ISO selection. For other guests change
  the destination workspace accordingly. Keep original media unchanged; only owner-supplied files.
- **Dev-test:** `check` package/command presence; make ISO construction required rather than SKIP
  for missing builders after install-retro. Use a tiny fixture with a spaced/long filename, list
  it through bsdtar, then retain existing ISO/app selection checks. Owner alone validates actual
  Delphi/Windows-era media filenames and installer access to F:. Include genisoimage in retro dapt;
  existing workspace disk rows count resulting ISOs, which duplicate source data roughly in full.
- **Docs:** shared contract; `docs/dev-demo.md` footprint and media, `STEPS-delphi.md`,
  `STEPS-winnt.md`, `STEPS-delphi1.md` cross-reference. No new Crostini-specific gotcha.
- **Owner choice:** **11A (recommended):** genisoimage plus documented recipe, ISO-only cd command.
  **11B:** add `cd FOLDER` convenience, requiring a further design for destination/name/overwrite rules.

### 12. Wine color schemes with built-in Breeze Dark

- **Finding (Nov 5):** the owner wants a dark Wine color scheme he can switch to in each Delphi
  prefix. A registry color scheme worked in the delphi1 prefix after winecfg's Theme was set to
  "(No Theme)"; copied into the delphi3 prefix it stayed light, apparently because a new prefix
  defaults to the Light theme, which overrides `HKCU\Control Panel\Colors`. A hand-made switcher
  (list / save / use, schemes as `.reg` files in `~/.config/dev-retro/colors`) was sketched in chat
  but not tested.
- **Decision:** a `delphi1 colors` / `delphi N colors` subcommand with two built-in schemes:
  `default` (Wine's colors) and `breeze-dark`, using the values below unchanged (including the red
  `ButtonAlternativeFace`), credited in a code comment to Zeinok's Breeze Dark gist
  (<https://gist.github.com/Zeinok/ceaf6ff204792dde0ae31e0199d89398>). Setup selects "(No Theme)" in
  each prefix so registry colors take effect.
- **Verified locations:** helper `delphi_setup` Background write 10943 and `dn_settings`
  Background write 11190 reset color every run; prefix creation is 10921–10927 / `dn_prefix`
  11178–11187. `delphi_reg` 10916 and `dn_reg` 11124 wrap registry writes. Command routing is
  11078–11104 / 11387–11427. Dev-test 5700 and 5716 hardcode black Background; that assertion must
  change when schemes are supported (both Delphi 1 and Delphi N). All these setup locations are
  within the generated helper.
- **Verified theme setting:** Wine 10's [winecfg theme.c](https://github.com/wine-mirror/wine/blob/wine-10.0/programs/winecfg/theme.c)
  `do_apply_theme` calls `ApplyTheme(NULL, ...)` for No Theme. Its
  [uxtheme system.c](https://github.com/wine-mirror/wine/blob/wine-10.0/dlls/uxtheme/system.c)
  `UXTHEME_SetActiveTheme` writes `HKCU\Software\Microsoft\Windows\CurrentVersion\ThemeManager`,
  `ThemeActive` as **REG_SZ `0`**, and removes ColorName, SizeName, DllName, LoadedBefore on
  deactivation. This is separate from Themes\Personalize's AppsUseLightTheme DWORD. For the
  noninteractive, closed-prefix path, set ThemeActive REG_SZ 0, then import colors; the next Wine
  session reads it. A full winecfg-equivalent cleanup of the four inactive style values belongs
  only to an explicit `colors use`, with a theme backup, never an automatic migration.
- **License finding (Nov 6):** the [Zeinok gist](https://gist.github.com/Zeinok/ceaf6ff204792dde0ae31e0199d89398)
  was reachable and showed three files (instructions, palette, reset); no license file or license
  grant was visible. The API endpoint was inaccessible through the web tool, so this is a report
  of no observed license, not a claim to know the author's intentions. The instructions credit a
  prior paste. Attribution alone does not settle redistribution. **Do not build the bundled palette
  until permission/license covering the supplied values is established, or the owner approves a
  scope change below.** Keep the already supplied table here unchanged as review evidence.
- **Proposed command contract:** `delphi1 colors [list|use NAME|save NAME]` and
  `delphi N colors [list|use NAME|save NAME]`. Bare colors lists names and current selection;
  list requires no prefix/Wine start. Built-ins are immutable files under the helper's installed
  data directory; user schemes are in `.config/dev-retro/colors`. Reserve default/breeze-dark;
  names must match `[A-Za-z0-9][A-Za-z0-9._-]*`, without path components. Save refuses an existing
  name, records only allowlisted REG_SZ RGB triplets (0–255) from Control Panel\Colors, and
  does not export other registry data. Require an existing idle prefix for save/use, serialize
  scheme operations, and never kill Wine to obtain it. Do not trust only the helper .pid: Wine
  tools started outside it must also be considered; if uncertain, refuse and ask the owner to close
  that prefix's Wine apps. No `wineboot` or licensed install just to list a palette.
- **Use/default:** validate the entire scheme before writes; back up only the affected Colors and
  ThemeManager keys to config (not a full registry), check every reg command, and record per-prefix
  selection only after success. Roll back partial failure. `default` removes just the allowlisted
  color overrides to let Wine supply defaults, rather than shipping the gist's reset file; leave
  unrelated/custom registry values. After use, restart the prefix's apps to observe colors. Subject
  to permission, breeze-dark uses the table verbatim, including red ButtonAlternativeFace, with
  Zeinok credit/link and license in a tagged code comment/data notice. No downloaded theme engine.
- **Existing machines:** remove both unconditional black-background writes. Newly created prefixes
  get ThemeActive=0 as part of their initial settings and otherwise Wine/default colors. Existing
  prefixes keep ThemeActive and all colors; add ThemeActive=0 only if absent, with no deletion of
  style keys. Existing active Light theme produces a warning explaining `colors use NAME` or the
  manual No Theme selection. Explicit use is the owner's instruction to switch theme/colors;
  setup reruns neither force it nor reapply a recorded palette over later manual changes. A saved
  selection is a label, not authority to overwrite registry edits. No changes to the COM prefix.
- **Dev-test:** `check` installed built-in files/command validation and fixture round-trips,
  prefix separation, default deletion scope, invalid RGB/name, existing-name rejection, stopped
  guard, rollback, repeated setup preserving a choice, and chosen scheme import via stubbed Wine.
  Add an isolated disposable Wine-prefix integration check of use/save/default with registry
  readback when test is owner-approved; never change a real Delphi prefix during dev-test.
  Use `warn` for actual theme/selection drift and font/TEMP preferences; replace the mandatory black
  assumption in the existing settings warning. Absent Delphi media/prefix is not a failure.
  Owner checks winecfg displays No Theme and the Delphi 1/3 IDEs render chosen colors after restart;
  only owner-media tests can establish IDE appearance. No default promise that editor colors follow.
- **Docs:** shared contract; `docs/dev-demo.md`, `STEPS-delphi1.md`, `STEPS-delphi.md`,
  init checklist color commands and license/attribution notice at build time. No Crostini-specific
  workaround. Count installed data and user schemes in the shared retro disk-report additions.
- **Owner choice:** **12A (recommended):** resolve redistribution permission/license first, then
  build the requested two built-ins without changing the table. **12B:** approve a scope change:
  ship default plus validated owner-supplied `.reg` schemes and defer bundled breeze-dark; owner
  may supply the gist locally. In both choices preserve existing themes until an explicit switch.

Breeze Dark values (`HKEY_CURRENT_USER\Control Panel\Colors`, "R G B"):

| Value | RGB | Value | RGB |
|---|---|---|---|
| ActiveBorder | 49 54 58 | Hilight | 119 126 140 |
| ActiveTitle | 49 54 58 | HilightText | 255 255 255 |
| AppWorkSpace | 60 64 72 | InactiveBorder | 49 54 58 |
| Background | 49 54 58 | InactiveTitle | 49 54 58 |
| ButtonAlternativeFace | 200 0 0 | InactiveTitleText | 219 220 222 |
| ButtonDkShadow | 154 154 154 | InfoText | 159 167 180 |
| ButtonFace | 49 54 58 | InfoWindow | 49 54 58 |
| ButtonHilight | 119 126 140 | Menu | 49 54 58 |
| ButtonLight | 60 64 72 | MenuBar | 49 54 58 |
| ButtonShadow | 60 64 72 | MenuHilight | 119 126 140 |
| ButtonText | 219 220 222 | MenuText | 219 220 222 |
| GradientActiveTitle | 49 54 58 | Scrollbar | 73 78 88 |
| GradientInactiveTitle | 49 54 58 | TitleText | 219 220 222 |
| GrayText | 155 155 155 | Window | 35 38 41 |
| WindowFrame | 49 54 58 | WindowText | 219 220 222 |

### 13. DOSBox-X host key `ctrlshift` by default

- **Finding (Nov 5):** DOSBox-X's host key defaults to F12, which a Chromebook keyboard lacks (F11
  and F12 exist only as remapped key combinations). The owner switches it to Ctrl+Shift by hand every
  time (Main > Select host key) and uses Ctrl+Shift+F for full screen.
- **Decision (placement corrected by installed documentation below):** `hostkey=ctrlshift` under
  `[dosbox]` in every DOSBox-X config install-retro writes:
  `~/win31/dosbox-x.conf` (line 10028), win95's two configs (the `base` template), and
  `~/.config/dev-retro/dos.conf` (line 11682). Existing configs get the line only if they have no
  `hostkey=` line (never overriding the owner's choice).
- **Verified locations:** setup win31 config at 10023–10047, helper win95 base at
  10528–10567 and lazy `dos_conf` at 11672–11692. The first template is outside DEVRETRO_EOF;
  the latter two are inside it. Existing guest output modes must stay unchanged except item 4.
- **Installed documentation result:** dosbox-x/dosbox-x-data `2025.02.01+dfsg-3` ships
  `/usr/share/dosbox-x/dosbox-x.reference.full.conf`: `[dosbox]` starts at 192, hostkey
  documentation at 239–242, assignment at 473; next section starts at 547. It explicitly lists
  ctrlshift among accepted values. Thus **hostkey is in `[dosbox]`, not `[sdl]`**. The binary
  strings also contain the hostkey handlers. No DOSBox-X execution or `-printconf` was needed.
- **Proposed change:** add `hostkey=ctrlshift` to `[dosbox]` in all four generated configs,
  creating `[dosbox]` in dos.conf (which currently has only sdl/ttf). Use the shared missing-key
  migration rule for existing files. Keep mapper files untouched. If a hostkey assignment exists
  in a wrong section, report the placement and leave it for manual review rather than silently
  relocating an owner's line or appending a competing setting. Ensure setup handles existing lazy
  files too, even before a subsequent guest launch.
- **Dev-test:** FAIL fresh-config and missing-key migration fixtures unless all four use the
  correct section; verify repeat runs and preservation of explicit mapper/ctrlalt choices. Real
  absent/different/incorrectly sectioned hostkey is `warn` with repair advice. Owner checks
  Ctrl+Shift+F full-screen and configured release shortcuts in DOS, win31 and win95; keyboard
  event delivery/focus under ChromeOS cannot be proved by a text check. DOS does not need media;
  Windows checks need the owner's installed guests.
- **Docs:** shared contract; `docs/init-checklist.md` keys, `docs/dev-demo.md`, generated
  `STEPS-delphi1.md`, `STEPS-delphi.md`, `STEPS-winnt.md` distinguish DOSBox-X shortcuts from
  QEMU's Ctrl+Alt+G. `docs/crostini-gotchas.md` focus/key section coordinated with item 16.
  Don't blindly replace Ctrl+F10 with a host shortcut: describe mapper-based release separately
  and verify the installed mapping with owner acceptance. No new disk allocation.
- **Owner choice:** **13A (recommended):** accept the documentation-verified `[dosbox]` correction
  and preserve existing choices. **13B:** defer the host-key default pending a separate GUI check.

### 14. `win95 net on|off`

- **Finding (Nov 5):** win95's configs carry a comment on how to enable NE2000 networking through
  slirp (line 10565), but nothing turns it on. The owner wants guest networking to reach services on
  his other machines (over Tailscale) and, with old-browser limits understood, the internet.
- **Decision:** a `win95 net on|off` subcommand that adds or removes the `[ne2000]` block
  (`ne2000=true`, `backend=slirp`, `nicbase=300`, `nicirq=3`) in `boot.conf`, with the guest off.
- **Verified locations:** helper win95 networking comment 10565, `win95_confs`
  10528–10567, `win95_cmd` stopped guard 10578; common dispatch 11742–11754 needs the new
  win95-only branch before boot handling. `status_cmd` 11599–11614 can append network state;
  help is the helper header at 10052–10132. No existing net subcommand or NE2000 block exists.
- **Read-only backend finding (Nov 6):** installed Debian dosbox-x `2025.02.01+dfsg-3` has
  a libslirp0 dependency; `readelf -d /usr/bin/dosbox-x` has NEEDED `libslirp.so.0`; `strings`
  includes `slirp_new`, `SlirpEthernetConnection`, the backend-selection message and “SLIRP:
  Successfully initialized”. The bundled full reference config 2502–2521 documents NE2000/slirp
  and the requested base/IRQ. [Upstream networking documentation](https://dosbox-x.com/wiki/Guide:Setting-up-networking-in-DOSBox%E2%80%90X)
  identifies shared-library linkage as its binary-support check. Together these confirm this
  installed build includes the slirp backend; a runtime launch is not needed to establish compile
  support. Guest DHCP/connectivity is still unverified. No DOSBox-X process was started.
- **Proposed change:** `win95 net`/`win95 net status` reports effective config on/off, backend,
  base, IRQ and next-boot semantics (not network reachability). `net on|off` requires the guest
  stopped, and edits only boot.conf atomically. On adds the decision's exact four-key `[ne2000]`
  block, bracketed by v100 managed comments. Off removes only an intact bundle-owned block; never
  delete a user-created section. Repeated on/off is a no-op when already in the requested state.
  Preserve unrelated settings/comments. If an unmanaged ne2000 section/key exists, or the managed
  block has been hand-edited, display its effective state and explain manual changes are required;
  do not overwrite/remove it. Refuse ambiguous duplicate sections/keys before any partial edit.
  An unmanaged already-off configuration can return “already off” without mutation.
- **Support/IRQ:** `net on` checks the installed binary/package for slirp evidence and fails
  actionably if unsupported (do not install an alternate DOSBox-X). Preserve IRQ3 as decided.
  Upstream notes IRQ3 conflicts with COM2: add `[serial] serial2=disabled` only if no serial2
  setting exists, label the inserted line as bundle-owned, and remove that unchanged managed line
  on off. Preserve any owner serial2 value; on must refuse an enabled/conflicting COM2 with an
  instruction to resolve it manually (or choose the owner's alternative below). Prevalidate both
  edits and commit together. Existing disabled COM2 is reused and never removed by off. setup.conf
  remains unchanged: network hardware becomes visible on the subsequent normal win95 boot.
- **Existing machines:** setup leaves network off/unconfigured; no automatic block adoption or
  guest driver installation. Explicit net on creates only absent managed settings; net off removes
  only its own unchanged additions. The old instructional comment becomes subcommand guidance.
  Preserve manually working networking and report it as custom. No owner keys or tokens involved.
- **Dev-test:** `check` binary slirp support and stub/fixture command round-trips, repeat calls,
  running refusal, custom block preservation, duplicate detection, COM2 conflict and unsupported
  build failure. Require the exact four values only for the managed on fixture; real networking
  off is normal info, custom settings produce `warn` only if inconsistent/conflicting. No guest
  launch or downloads to test config logic. Disk rows already count configs; no new service.
- **Owner media checks/docs:** add NE2000 Compatible manually in Windows 95, I/O 0300 / IRQ3,
  ensure no COM2 conflict, add TCP/IP, obtain address by DHCP, reboot and inspect `winipcfg`.
  Explain Linux host at 10.0.2.2; use explicit Tailscale IPv4 addresses first for other machines,
  with plain HTTP/period-browser TLS limits. Do not promise MagicDNS, ping behaviour, inbound
  access or DCOM through slirp. Broad network matrix stays v101. Shared docs contract plus
  `docs/crostini-gotchas.md` key/network constraints, `docs/dev-demo.md`, `STEPS-delphi.md` win95
  networking; cross-reference from `STEPS-delphi1.md`. No win31 networking or port forwarding.
- **Owner choice:** **14A (recommended):** retain IRQ3, disable COM2 only when absent, refuse custom
  conflicts, and manage only helper-owned blocks. **14B:** change the planned NIC IRQ to 10 to avoid
  COM2 altogether; the Windows driver instructions/block and acceptance values must change together.

### 15. Delphi under Wine: documentation findings (docs only)

- Delphi 3 Client/Server installed under Wine from loose CD files in `~/delphi/install/3` (first real
  disc test of `delphi N`); `delphi 3 setup ~/delphi/install/3/INSTALL.EXE` reruns the CD menu after
  Delphi is installed (for Local InterBase, InstallShield Express); reruns reset the prefix's desktop
  color (until item 12).
- During that install, "There was an error registering …HTTPCT.OCX;…POPCT.OCX;…SMTPCT.OCX;…WINSCK.OCX"
  (the Internet Solutions Pack ActiveX controls) is harmless: click OK; Delphi installs and runs.
- Delphi 1 and Delphi 3 IDEs ignore the mouse wheel under Wine (Notepad in the same prefix scrolls),
  because the IDEs predate wheel support; use the keyboard (Ctrl+Up/Down, Page Up/Down).
- Media layout: Delphi 1's files go in `~/win31/install/apps`, in a folder whose name contains
  "delphi"; Delphi 3–7 in `~/delphi/install/N` (an `.iso` or the CD's files); `delphi N` launcher
  icons appear only after `delphi N setup`; the bare "DOSBox-X" launcher is Debian's own entry.

- **Verified locations:** generated helper media discovery `delphi_media` 10910–10915,
  `dn_installer` 11151–11167, explicit-installer path `dn_setup` 11208–11242, launcher generation
  11035–11076 / 11243–11273, and rerun settings at 10942–10950 / 11188–11207. This is all
  DEVRETRO_EOF code. Dev-demo source STEPS-delphi1 at 4306–4358 and STEPS-delphi at 4360–4440
  contain the Wine/guest procedures; init checklist retro text is 614–620, README flag at 161.
- **Proposed documentation:** record Delphi 3 Client/Server as owner-tested, without extending
  that claim to 4–7 or to every component. Show the explicit `delphi 3 setup` installer path for
  rerunning the CD menu after installation; explain why plain setup only reapplies settings when
  already installed. Describe the four named OCX registration errors as observed non-blocking for
  this install, not a general rule to ignore installer errors. Say those optional controls may
  still be unavailable. Include IDE wheel limitations/key alternatives and the exact separate
  media layouts; distinguish Debian's DOSBox-X icon from bundle guest/Delphi launchers.
- **Existing machines:** no new writes/config migration. Replace the “rerun resets black desktop”
  observation with a historical v99 note and item 12's preserve/switch behaviour when that is built.
  Item 10's font repair is prefix-qualified. Generated STEPS files are rewritten on demo reruns;
  projects, source and guest data remain untouched.
- **Dev-test/owner boundary:** no new engine or UI test for a docs-only item. Existing prefix/IDE
  checks 5706–5738 remain; do not make missing optional Delphi media/OCXs a FAIL. A focused docs
  review checks paths/commands against dispatch and ensures no “all versions tested” claim. Owner
  alone verifies Delphi 3 install/menu, IDE start, sample compile/run and wheel/key behaviour with
  his media; optional add-ons get their own observations, not automatic success claims.
- **Docs:** shared contract; `docs/dev-demo.md`, both Delphi STEPS, checklist manual retro steps.
  No new Crostini workaround: keep existing Wine limits and link to item 12; no new disk content.
- **Owner choice:** **15A (recommended):** publish the limited Delphi 1/3 observations with the
  qualifications above. **15B:** defer the OCX note until optional-control functionality is tested.

### 16. DOSBox-X and QEMU guests: documentation findings (docs only)

- DOSBox-X full screen loses keyboard focus after switching windows on ChromeOS; recovery: click the
  picture, Ctrl+F10 (or the configured host key) to release the mouse, Alt+Enter. No `maximize=true`
  default.
- Don't change the output mode or scaler from the Video menu while a guest runs, especially during
  Setup (a Video-menu change ended one Windows 95 Setup run with an unbootable disk); edit the config
  with the guest off. Blind safe shutdown when the picture is lost: Ctrl+Esc, U, Enter.
- Windows 3.1 from floppy images: all `.IMG` files are queued on A:, DOS > Swap floppy advances them;
  choose "Return to MS-DOS" at the end.
- Chromebook keys: F11/F12 come from Settings > Device > Keyboard and inputs > Customize keyboard keys.
  NT/2000 login: `<guest> keys ctrl-alt-del`.
- QEMU guests: move files with `put` / `get` through the exchange disk; why writing to C: from Linux
  is avoided (qcow2, the guest must be off); in Windows 2000 Setup "FAT" means FAT32 above 2 GB, and
  `convert C: /fs:ntfs` changes it later; adding a drive letter in Disk Management.
- Windows 2000 has no built-in ZIP support: unzip on Linux and `put` the folder.

- **Verified locations:** helper `win31_cmd` 10475–10522 queues floppy images at 10495–10498;
  `nt_cmd` keys at 10850–10853 sends ctrl-alt-delete through the monitor; QEMU pointer note at
  10789; exchange layout/create/put/get 10243–10378. Font README sharp-picture text 11513–11520
  and demo STEPS-delphi1 4348–4355, STEPS-delphi 4428–4434, STEPS-winnt 4441–4486 carry current
  guest instructions. Helper locations are all inside DEVRETRO_EOF. Existing Crostini Retro notes
  mention missing KVM but do not describe these focus/recovery findings.
- **Proposed documentation:** put the owner's focus loss/recovery sequence in the DOSBox-X
  notes, label Ctrl+F10 as the current mapper release shortcut pending the host-key acceptance
  check (item 13), and describe host+F for the new full-screen setting. Verify Alt+Enter on the
  installed mapping rather than calling every shortcut a host-key combination. With a lost picture,
  attempt Start-menu shutdown via Ctrl+Esc, U, Enter only for the Windows guest/version where the
  owner confirmed it; it is not a DOS/win31 universal recovery. Guest-off config edits are the normal
  renderer/scaler route (item 4), and no maximize=true default is added. Document floppy queue/order,
  DOS > Swap floppy and Return to MS-DOS; key remapping in ChromeOS and helper login keys.
- **QEMU procedures:** explain exchange FAT/put/get with the guest stopped and item 8's completion
  enable step, why host mtools must not write qcow2/NTFS C:, Windows 2000 FAT choice above 2 GB as
  FAT32, optional in-guest `convert C: /fs:ntfs` only after backup, and assigning the exchange letter
  in Disk Management without formatting. State exchange letters may differ on old installations;
  do not promise D: when C:/F: were assigned during v99 Setup. Unzip on Linux before put since 2000
  lacks Explorer ZIP support. No zip-tool or licensed-media downloads are introduced.
- **Existing machines:** docs only; no config migration, disk conversion, partition repair or
  automated shutdown. Owners choose manual changes with guests off. STEPS refresh is intentional
  bundle documentation replacement, separate from write-once guest config.
- **Dev-test/owner boundary:** no new UI acceptance automated; keep engine/exchange fixtures and
  item 3/8/13 tests. No FAIL for absent media or an owner-selected output/mapping. Owner checks
  focus/full-screen recovery in DOS/win31/win95, floppy swap with his media, NT/2000 login keys,
  file round-trip and letter assignment. Disk conversion is optional and never run by dev-test.
- **Docs:** shared contract; `docs/crostini-gotchas.md` Retro/focus, `docs/dev-demo.md`, all three
  generated STEPS, checklist guest steps; README keeps a concise pointer to them. No disk increase.
- **Owner choice:** **16A (recommended):** record these as qualified manual procedures and verify
  shortcuts during acceptance. **16B:** omit the blind shutdown shortcut until rechecked per guest.

## Proposed build stages (after owner approval; one commit per stage)

1. **NuGet scope (2):** command/runner changes and relevant dev-test/docs. Bump all four scripts
   together to v100 in this first implementation commit, update every version string/README, and
   create entries under all four CHANGELOG sections (version bump only where appropriate).
2. **DOSBox-X boot/defaults/keys (3, 4, 13):** helper argument fix, correct-section host key,
   missing-key/exact-v99 migration and owner-edit preservation fixtures. Keep win31/DOS renderer choices. Refresh
   corresponding docs/STEP prose and CHANGELOG descriptions in this commit.
3. **QEMU defaults, attachment and reporting (5–9):** combine guest-specific defaults, exchange
   completion record/commands and truthful messages because launch argument tests cover them
   together. Include existing-install migration docs, init/test capability wording, disk rows and
   the fixture matrix. Validate setup continuation and safe attachment before any owner installation.
4. **Media/fonts (10, 11):** package, collection/retry/status/log handling and fixture ISO/font
   regressions, docs/STEP repairs, disk accounting and CHANGELOG entries.
5. **Colors (12), owner choice 12B:** the switcher with the `default` scheme and validated
   owner-supplied `.reg` schemes; no bundled breeze-dark data. Prefix-preserving settings, commands
   and isolated registry tests, docs/STEP and disk-report changes. Do not substitute a different
   palette or describe Breeze Dark as shipped.
6. **Win95 networking (14):** managed config transaction, support/IRQ guard, off/on fixtures and
   guest instructions. Recheck installed build support read-only at implementation time. No guest
   startup implicit in setup.
7. **Documentation consolidation (15, 16):** add remaining findings, review every README/checklist/
   gotcha/STEP cross-reference against the final helpers, and correct stale KVM/black-desktop/F:
   assumptions. Earlier stages already carry docs for behaviour they change; this is not deferred
   documentation for those changes.
8. **Inspector (1):** retain its investigation-first design and approval boundaries exactly as
   above. It is independent of retro; follow its recorded decision gate. Keep its managed npm cache
   separate from item 2's .NET workaround, add both new storage categories without double-counting,
   and combine final all-four validation/acceptance. It can move earlier after its investigation;
   no retro fix is evidence about npm cache coherence.

Every commit carries the Codex co-author trailer; use `release/v100` only after this plan is
approved. Every push needs all-four syntax, error-level ShellCheck and secret checks. Build tests
exercise the generated helper extracted from the heredoc, including its own `bash -n`/ShellCheck;
checking only the outer setup shell does not parse quoted heredoc code. Never run the targeted
refresh script merely as a read-only test: it writes the installed helper. No implementation,
version bump, release branch, merge or real script execution is part of this planning update.

## Proposed owner acceptance route (commands for later approval, not executed)

1. Review choices **2A/2B through 16A/16B** under each item, especially 8's extra enable step,
   12's license gate, 13's corrected section and 14's IRQ/COM2 handling. Approve the plan/build separately. Start with
   all real guests/Wine apps closed; preserve configs/disks before any fresh-install experiment.
   Never delete an existing Windows disk just to test this version; arrange a separate owner-approved
   workspace/backup for fresh media acceptance. Fixture tests cover destructive cases synthetically.
2. Targeted bundle workflow (first init only creates a template on a new machine):

   ```bash
   ./dev-init-chromebook.sh install-retro install-dotnet install-pwsh install-bdd install-godot
   ./dev-setup-chromebook.sh install-retro install-dotnet install-pwsh install-bdd install-godot
   ./dev-init-chromebook.sh install-retro install-dotnet install-pwsh install-bdd install-godot
   ./dev-test-chromebook.sh install-retro install-dotnet install-pwsh install-bdd install-godot
   ./dev-demo-chromebook.sh install-retro install-dotnet install-pwsh install-bdd
   ```

   These are proposed flags, not permission to run. BDD pulls its browser dependencies; use the
   targeted NuGet/demo subset first if their disk/network cost is undesirable. Inspect the saved
   setup/test `.output` files under `assets/logs/` after each owner run; investigate FAILs and retain
   producer diagnostics. Read the refreshed retro STEPS and run VB/C# Spectre/PowerShell demos;
   prove an acquisition succeeds without a manual environment export, not only a cached run.
3. Guest hand checks (one guest at a time, explicit owner-started commands):

   | Environment | Owner action and expected result |
   | --- | --- |
   | DOS | `retro run --in dos FILE` with a local DOS sample; Ctrl+Shift+F/full-screen and focus/release shortcuts work; dos.conf renderer stays ttf. |
   | win31 | `win31 setup` only in the agreed test workspace if installation is needed; queue/swap floppy images and Return to MS-DOS. `win31` reaches Program Manager; renderer remains owner-selected. After font repair, `win31 fonts` supplies C:\FONTS; install fonts in Windows, check focus and Delphi 1 run/debug using owner's media. |
   | win95 | `win95 setup` first and resumed phases, then `win95`: desktop loads with no X: folder IDE drive. Check maximized surface redraw, app CD and put/get/run; never change Video menu during Setup. `win95 snapshot save pre-net` while off; `win95 net on`, install NE2000/TCP-IP in Windows, confirm resource values and DHCP via winipcfg; reach a known owner service by IPv4. Shut down, `win95 net off`, cold boot shows network disabled; app CD and normal boot still work. |
   | win2000 | Existing install (owner decision: no fresh reinstall workspace): after the upgrade, normal boot is detached until shutdown and `win2000 exchange enable`, then boot; the exchange drive appears (assign a letter in Disk Management if needed, without formatting); off-guest put/get round-trip. TCG is the default; untouched v99 ACCEL/SOUND/DISPLAY_OPTS lines upgrade, owner edits stay. Verify unscaled tablet alignment, larger screen area, quiet boot, `win2000 keys ctrl-alt-del`, Delphi install from generated app ISO and sample compile/run. Existing installs adopt untouched-template/absent defaults, preserve edits and explicitly enable exchange. |
   | winnt40 | Item 8's fresh-install acceptance (owner's first NT install): `winnt40 setup` and resumed setup run without the exchange disk attached; Windows installs to C:; normal boot stays detached until shutdown and `winnt40 exchange enable`, then the exchange drive works; with own NT media; keep auto acceleration, PS/2, sb16 and scaled display. Test login keys, pointer release, exchange round-trip and app CD. If KVM is slow, document an owner-selected TCG fallback; no claim of NT acceptance without the run. |
   | Delphi Wine | `delphi1 setup`, `delphi 3 setup` with own files; verify final font summary/status and prefix-qualified repair if needed. Item 12 (12B): add the owner's local Breeze Dark `.reg` as a user scheme, then list/save/use default and it in each existing idle prefix; restart IDE, verify No Theme, colors and per-prefix separation. Rerun setup: manual colors survive. Rerun Delphi 3 CD menu explicitly; qualify OCX observations, check IDE keys and compile/run. Other versions only if owner has media. |

   `exchange recreate`, restoring snapshots, and `convert C:` are optional recovery/maintenance
   actions requiring separate owner intent, not routine acceptance commands. To inspect repaired
   existing exchange media, start with `exchange info`/`get`; never format it in Windows.
4. Item 1 is paused until a machine has `install-agentic` from the bundle's setup. Then resume its
   cold/online/offline/new-session/full-workflow gate with individual command approvals. Do not
   hand-build an environment under `assets/tools` or clear the owner's npm cache.
5. After focused checks, proposed full acceptance repeats **init → setup → init → test** with the
   established six flags on each script:

   ```text
   install-all install-db-server install-lan-share install-models install-ollama-containers install-retro
   ```

   Obtain approval for each script run; do not start the six-flag route automatically. Disk-heavy
   services/models follow existing one-at-a-time guards. Required result: FAIL 0, no unexplained
   non-credential WARNs, all selected stages complete, prompt returns normally, and guest hand checks
   recorded. Explicit owner preferences (old outputs/acceleration/theme) may yield documented WARNs;
   the owner must choose the recommendation or explicitly accept those exceptions before release.
   Until these runs exist, no claim of a confirmed Chromebook build; this PR remains a draft plan.

## Deferred to v101

These depend on `install-lan-share` and `install-db-server` and are recorded here so the overall
assessment is in one place. They are not part of v100.

### Delphi DCOM / multi-tier database demo

A Delphi server exposing a method such as `GetCustomers` that queries a local database and returns the
result to clients on other guests and machines; a showcase of the DCOM → MIDAS/socket → SOAP/HTTP arc.

- **Stage 1:** server and client in one win2000 guest: a Delphi 5/6/7 Remote Data Module or Automation
  object over InterBase, Paradox, or SQL Server 7/2000 in the guest.
- **Stage 2 (go/no-go):** real DCOM between winnt40 and win2000 on one Chromebook, on a shared QEMU
  socket network with static addresses (no NAT between guests), configured with `dcomcnfg`.
- **Stage 3:** the same across two Chromebooks, QEMU's UDP socket link carried over Tailscale.
- **Stage 4:** bridges: Borland Socket Server (Delphi 4+) for win95 and Wine clients; a SOAP/HTTP front
  (Delphi 6/7) for a Lazarus client on Linux.
- **Known limits:** no DCOM in win31; win95 needs the DCOM95 add-on; remote DCOM under Wine is unlikely
  to work; Lazarus has no DCOM, so it joins through stage 4.
- **Unknowns to test early:** whether 1999-era SQL Server client libraries can log in to SQL Server
  on Linux (`install-db-server`); the shared QEMU socket network inside Crostini.
- **Owner inputs needed:** Delphi 4–7 editions (multi-tier pieces need Client/Server or Enterprise);
  SQL Server version.

### Guest network test plan

One Winsock test program (a small Delphi 3 console `HTTPGET`), run unchanged under Wine, win95 (after
item 14), winnt40 and win2000, against: the Linux host (`127.0.0.1` from Wine, `10.0.2.2` from guests),
another laptop by Tailscale IP and by name, and the internet over plain HTTP; plus browser checks
(plain HTTP expected to work, HTTPS expected to fail in period browsers). Results table per
environment. Stretch: serving from a guest (QEMU `hostfwd`), win31 networking.
