# dev-setup-chromebook v100 plan

Nov 1, 2026 (item 1) · Nov 6, 2026 (items 2–16 added) · **draft for owner review; planning only**

## Items at a glance

Item 1 was drafted Nov 1. Items 2–16 are the owner-confirmed scope from hands-on install-retro testing
on a long-term Chromebook with `/dev/kvm` (Nov 5–6, 2026); each records the finding, the owner's
decision and the requested change. They still need a detailed design (code locations, tests, docs)
before the build starts. See "Items 2–16" below.

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
- Line numbers below refer to v99 (`main` at 5c1a3b8) and are starting points only.

### 2. NuGet steps hang where IPv6 to api.nuget.org fails

- **Finding (Nov 2):** with the six-flag v99 install, dev-demo's NuGet-based steps
  (`dotnet/vb-spectre`, `pwsh/spectre-demo`) hung. On that Chromebook IPv6 connections to
  api.nuget.org failed while IPv4 worked; rerunning dev-demo with `DOTNET_SYSTEM_NET_DISABLEIPV6=1`
  completed every demo.
- **Decision:** in v100.
- **Plan should settle:** which steps need it (dev-demo only, or setup/test steps that restore NuGet
  packages or install .NET tools too); applying the variable to those commands only versus detecting
  a failing IPv6 path first; a dev-test check or warning that makes the condition visible; a
  `docs/crostini-gotchas.md` entry.

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
- **Plan should settle:** every place the X: mount reaches a `boot c:` (setup's second-part run as
  well as `win95` / `win95 run`), keeping the separate IMGMAKE use at line 10606, which needs it; a
  regression check that the generated helper's boot arguments contain no folder mount; whether win31
  is affected (it boots DOS, not `boot c:`, so probably not).

### 4. Stale-frame flicker in a maximized win95 window

- **Finding (Nov 5):** with DOSBox-X's window maximized, the area around the guest picture flickers
  with stale frames under `output=opengl`. `output=surface` in `~/win95/boot.conf` fixed it.
  Separately, switching the output mode from the Video menu while Windows 95 ran blanked the window
  and left it unusable; toggling the same options in win31 (which runs `output=opengl`) worked.
- **Decision:** `output=surface` for win95's `setup.conf` and `boot.conf` (the `base` template at
  setup line 10528). win31 and `dos.conf` keep their current output. No other video default changes.
- **Plan should settle:** whether setup changes an existing win95 config's `output=opengl` to
  `surface` (only when the line still has the old default) or leaves existing machines to the docs;
  the docs note that output modes are changed in the config file with the guest off, not live (see 16).

### 5. Windows 2000 crawls or hangs at "Starting up…" on nested KVM

- **Finding (Nov 5):** `win2000 setup`'s first graphical boot sat at "Starting up…" for over five
  minutes, the splash painting slowly top to bottom with QEMU above 100% CPU. HPET off, a PS/2 mouse
  and `SOUND=none` did not help; `ACCEL=tcg` got through, and Setup completed under TCG. ChromeOS's
  `/dev/kvm` is nested, so the many VGA and IDE port exits of an old guest's boot are expensive.
- **Decision:** default win2000 to TCG always, until a KVM boot of an installed system is shown to
  be faster.
- **Plan should settle:** the default in `qemu_config` (line ~10693) and in the config file setup
  writes (lines ~11780–11797, with a comment explaining why); whether existing `~/win2000/config`
  files with `ACCEL=auto` change (the owner's machines already have `ACCEL=tcg` by hand); the winnt40
  default (NT 4.0 is not yet installed or tested on these machines: propose keeping it unchanged and
  documenting the TCG fallback, unless there is evidence); docs.

### 6. QEMU tablet pointer misaligned

- **Finding (Nov 5):** with the USB tablet, Windows' pointer did not line up with the host pointer.
  Unticking View > Zoom To Fit fixed it (the README already suggests `zoom-to-fit=off` for a sharper
  picture, setup line 11518).
- **Decision:** `DISPLAY_OPTS="gtk,zoom-to-fit=off"` as the win2000 default. winnt40 uses a PS/2
  mouse; the plan proposes whether it changes too.
- **Plan should settle:** where the default lives (line 10695 sets it for both guests; the config
  template at 11798); the docs advice to raise the guest's screen area since the window no longer
  scales.

### 7. win2000 sound: default `SOUND=none`

- **Finding (Nov 5):** with the AC97 card, the terminal fills with repeated
  `pulseaudio: set_sink_input_volume() failed … Invalid argument` lines during boot. Turning the card
  off did not fix item 5, so the errors were not its cause, but they serve no purpose for the
  development use of the guest.
- **Decision:** default `SOUND=none` for win2000; investigating working guest audio is a later item.
- **Plan should settle:** the defaults (lines 10693, 11782); whether winnt40's sb16 shows the same
  errors (unknown; leave unchanged without evidence); docs on turning sound back on.

### 8. Exchange disk takes C: (and loses its letter) during NT/2000 Setup

- **Finding (Nov 5–6):** `qemu_launch` always attaches `exchange.img` as the primary slave (line
  10763). The exchange disk is partitioned and formatted before Setup runs while the new system disk
  is blank, so Windows 2000 Setup assigned **C:** to the exchange disk and installed Windows to F:.
  The workaround was: create the system partition, quit Setup with F3, boot the CD again, so the
  system partition is enumerated first and becomes C:. During those attempts the exchange disk's
  partition was deleted, so it later appeared in Disk Management as unallocated with no letter;
  `win2000 exchange recreate` with the guest off restored it, and `put` / `get` worked again.
- **Decision:** don't attach the exchange disk until the guest's Windows is installed.
- **Plan should settle:** the "installed" test that decides attachment (`installed "$GUEST"` or the
  disk holding a Windows install) and the message shown when it is left out; that setup's later runs
  (the second, resumed `setup`) still work; the same for winnt40; docs covering the F3 workaround and
  `exchange recreate` for guests installed with earlier versions, and that the exchange disk is
  formatted only from Linux, never in Windows (`put` / `get` use mtools and need its FAT layout).

### 9. Misleading accel message when `ACCEL=tcg` is configured

- **Finding (Nov 5):** with `ACCEL=tcg` in `~/win2000/config` on a Chromebook that has a usable
  `/dev/kvm`, the launch line said "software emulation (TCG; no /dev/kvm on this Chromebook:
  slower)" (`pick_accel`, line 10712).
- **Decision:** fix the message.
- **Plan should settle:** wording for each case (TCG chosen in the config, no `/dev/kvm`, `/dev/kvm`
  present but not usable yet), keeping the existing group-membership hint.

### 10. Failed `winetricks corefonts tahoma` is silent

- **Finding (Nov 5):** `win31 fonts` failed with "No fonts found" (line 11531) because
  `winetricks -q corefonts tahoma` had failed during `delphi1 setup`, which printed only a NOTE
  (line 10950; the same in `delphi N setup`, line 11197). Running
  `WINEPREFIX=~/.local/share/wine/delphi1 winetricks corefonts tahoma` by hand fixed it, and
  `win31 fonts` then worked.
- **Decision:** make the failure visible and actionable.
- **Plan should settle:** how to surface it (one retry, a prominent end-of-setup line, `delphi1
  status` showing font state), and the exact command `win31 fonts` prints when the prefix has none.

### 11. Loose-file media for real guests

- **Finding (Nov 5):** most of the owner's Delphi media is loose CD files, which `delphi N setup`
  (Wine) handles, but the real guests' app CD drive only mounts an `.iso`. Building one with
  `genisoimage -o ~/win95/install/apps/delphi3.iso -J -r -V DELPHI3 ~/delphi/install/3` worked and
  Delphi 3 installed from it in Windows 95.
- **Decision:** install-retro installs `genisoimage` (next to `libarchive-tools`, line 9960) and the
  docs show building an `.iso` from a folder.
- **Plan should settle:** package choice (`genisoimage` vs `xorriso`), the docs location, and whether
  a `<guest> cd FOLDER` convenience that builds the ISO belongs in v100 (propose; the owner decides).

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
- **Plan should settle:** subcommand shape (`list`, `use NAME`, `save NAME`); how "(No Theme)" is
  set non-interactively (the winecfg Theme setting's registry location); `dn_settings` and the
  delphi1 equivalent currently set `Background` to black on every setup (lines 10943, 11190): the
  plan proposes how a chosen scheme survives a setup rerun; the gist's license (none seen) before
  shipping its values in a public repo; dev-test checks (scheme files written, `use` changes the
  registry values).

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
- **Decision:** `hostkey=ctrlshift` under `[sdl]` in every DOSBox-X config install-retro writes:
  `~/win31/dosbox-x.conf` (line 10028), win95's two configs (the `base` template), and
  `~/.config/dev-retro/dos.conf` (line 11682). Existing configs get the line only if they have no
  `hostkey=` line (never overriding the owner's choice).
- **Plan should settle:** confirming the setting name and value against the installed DOSBox-X
  (`dosbox-x -printconf` or its docs); the README/STEPS key references (they mention F12 combinations
  such as Ctrl+F10 and the host-key shortcuts).

### 14. `win95 net on|off`

- **Finding (Nov 5):** win95's configs carry a comment on how to enable NE2000 networking through
  slirp (line 10565), but nothing turns it on. The owner wants guest networking to reach services on
  his other machines (over Tailscale) and, with old-browser limits understood, the internet.
- **Decision:** a `win95 net on|off` subcommand that adds or removes the `[ne2000]` block
  (`ne2000=true`, `backend=slirp`, `nicbase=300`, `nicirq=3`) in `boot.conf`, with the guest off.
- **Plan should settle:** whether Debian's DOSBox-X build includes the slirp backend (check before
  building; if not, report and stop); `net` status output; the docs for the Windows 95 side (NE2000
  Compatible at I/O 300 / IRQ 3, TCP/IP via DHCP, `winipcfg`, `10.0.2.2` as the Linux host); a dev-test
  check of the generated block. Not in scope: port forwarding into guests, win31 networking.

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
