# dev-setup-chromebook v102 plan

Nov 9, 2026 · **FINAL — owner approved Nov 9, 2026 after review of `0db00e1`; merge before build**

**Read-only-checked:** baseline is released `v101`, commit
`68113ff633e19005707394b375f25dd505cfccee`, the merge of PR #17. After fetching,
`origin/main` and `v101^{commit}` matched; the initial live origin query found neither
`plan/v102` nor `release/v102`. This plan branch started at that commit and is now PR #18.

Evidence labels apply throughout, including the companion:

- **Owner-reported:** instructions/decisions in the Nov 9 request or findings attributed
  to the owner in the v101 release history; not independently reproduced here.
- **Read-only-checked:** repository source/history or linked primary documentation actually
  read during planning. A documented capability is not a successful lab run.
- **Hypothesis:** proposed design, recommendation, budget, expected behavior or unverified
  compatibility. Future-tense implementation/validation instructions retain this label unless
  explicitly recorded as an owner decision. Approval of a design does not prove it works or
  authorize its execution during this planning task.

**Owner-reported scope:** five items only. This PR changes plan documents; implementation,
version bumps, real script runs, guest changes and media-content inspection are excluded.
The v101 plan documents remain unchanged release history. Detailed F0/F1 design is in
[v102-delphi-f0-f1.md](v102-delphi-f0-f1.md).

## Items at a glance

**Hypothesis — proposed deliverables, all NOT RUN:**

| # | Item | v102 deliverable / gate |
|---|---|---|
| 1 | Released-v101 six-flag baseline | Early owner-run init → setup → init → test, saved logs, disk preflight and a fix ledger |
| 2 | Guest network matrix | Settled endpoints/origins; owner-recorded HTTP/DNS/local-link results, sanitized summary |
| 3 | F0 prerequisites | Backup → NT SP6a → Delphi 7 Wine install or Windows fallback → DCOM preparation; preserved docs |
| 4 | F1 DCOM go/no-go | No-TLB IDispatch probe, Wine build first, local then NT → 2000 activation, real-configuration timings, GO/NO-GO |
| 5 | Evidence-driven fixes | Initially empty; only reproducible findings from items 1 and 2 |

## Recorded owner decisions and implementation evidence still needed

**Owner-reported — settled scope; do not reopen:**

- The six flags are `install-all install-db-server install-lan-share install-models
  install-ollama-containers install-retro`. Run the released-v101 baseline before
  v102 script changes. The owner runs commands in his terminal; Codex reads saved assets logs.
- Protect the existing guest lab's disk headroom: use the approved separate regression laptop.
  Keep actual machine identities in private run notes. Its item 1 baseline runs in parallel
  with the owner's guest-lab F0 backup/SP6a steps; both precede item 2, whose NT rows run on SP6a.
- v101 acceptance was targeted: PASS 159, FAIL 0, WARN 0, SKIP 0 for
  `install-retro install-agentic install-node`. LAN adapter identity, ping/domain,
  first-NIC internet and scaffold menu hand checks passed. This did not run the
  guest network matrix or full six-flag regression.
- F0 order is backup → NT 4.0 SP6a → Delphi 7 Enterprise under Wine (or Windows 2000
  fallback) → DCOM preparation on both guests. Delphi 7 has not been installed under Wine
  on any owner's machine. Preflight guest-lab free space and bound the installer attempt.
  Windows 2000 SP4/NT without a service pack remain historical state, not a new check.
- F1 is a minimal Delphi 7 object/client, no database or MIDAS provider. Local Windows
  2000 activation precedes NT client → Windows 2000 server on the managed second NIC.
- Primary F1 uses `TComObject`/`TComObjectFactory` with hand-written `IDispatch` and no type
  library; original per-machine .reg/undo files supply AppID/CLSID links/RemoteServerName.
  Build first with `delphi 7 build` under Wine on the guest-lab host. During the later build
  Codex may execute each approved build command and iterate on compiler errors. Registration,
  activation and DCOM tests occur only in Windows guests, never Wine.
- If Wine install/build fails, install Delphi 7 Enterprise in Windows 2000 within F0 and build
  there, preferring command-prompt dcc32 (IDE equivalent). Record why. The IDE/TAutoObject/TLB
  route is a documented second fallback and F2 note. F2 expects the Windows 2000 IDE/debugger
  regardless; v102 requires that installation only if the Wine route fails.
- Time the real configuration: NT uses its configured accelerator, Windows 2000 uses TCG;
  record each actual selection. No temporary NT TCG override or NT accelerator comparison.
- A recorded F1 decision is the release requirement; DCOM success is not. One bounded
  diagnosis is allowed after NO-GO; sockets fallback is a v103 decision.
- Keep the agreed advanced-demo home. F2–F6 and the other deferrals below are outside v102.

**Read-only-checked:** the historical evidence and carried-forward limits are recorded in
[v101 owner acceptance](v101-plan.md#owner-acceptance--nov-9-2026-targeted-run),
[the F0–F6 roadmap](v101-dcom-demo.md#follow-up-work-packages-f0f6-and-acceptance-gates),
the v101 entries in all four CHANGELOG sections and
[the network procedure](../guest-network-tests.md). The v101 KVM investigation exhausted
its budget without a Windows 2000 fix; audio was not retested. Those are recorded owner
findings, not new measurements. No F0/F1 pass is inherited from scaffold readiness.

**Owner-reported — Nov 9 decisions:** choices 1, 2, 4, 5, 6, 9 and 10 are approved as
recommended, subject to the revised stage order and real-configuration timing below. Choice 3
selects `http://neverssl.com`, recording redirects separately; no owner-hosted internet marker.
Choices 7/8 adopt the no-TLB Wine-first build, original heredocs and stopped-guest exchange path
specified in item 4 and the companion. These choices are settled; exact peer identifiers and
individual run approvals remain operational inputs, not reopened design decisions.

## Shared implementation and validation contract

**Hypothesis — proposed build contract:**

- Merge the approved plan first, then build on `release/v102`. The **first script change**
  bumps all four scripts to 102, every header/banner/completion/demo VERSION occurrence,
  README's current version and all four CHANGELOG sections. Unchanged scripts get
  “version bump only”. No such changes in this planning PR.
- No new install flag unless evidence justifies one and the owner approves it. Use existing
  `install-retro`; keep all-four flag expansion identical. Project-specific probe code belongs
  in the demo, not a new system SDK stack. No database dependency for F0/F1.
- Setup remains unattended/idempotent. No automatic guest boot, DCOM configuration, domain
  changes, service-pack application or registration from Linux. Every real script, guest,
  listener, compiler or transfer run requires owner approval. Prior v101 approvals are not
  permission for new v102 experiments. The later Codex Wine-build scope still requires
  per-command approval; it authorizes no Wine registration/activation/DCOM testing. No sudo,
  heavy service starts or host-guard bypasses during planning.
- Licensed media, vendor DLLs, seed data and credentials never enter the repo or public
  artifacts. Do not open media contents in this task. Before any later names-only inventory
  of install-media folders, ask once for that inventory scope; publish only edition/version
  facts, not folder listings, keys, paths or labels. Owner verifies content in Windows.
- Required installed behavior/portable regressions use `check` (FAIL); user-changeable or
  optional environmental settings use `warn`/information. Dev-test must not require a
  proprietary compiler, installed guests, domain accounts or live DCOM. Demo acceptance
  stays separate from dev-test PASS counts.
- Preserve dated/versioned design comments. Re-find functions before edits. The helper is
  generated inside setup's **`DEVRETRO_EOF`** heredoc; the scaffold is dev-demo's
  **`demo_retro_advanced`**. Outer `bash -n` alone does not validate generated helper syntax.
- Keep new F0 docs and F1 editable sources **create-if-missing on rerun and refresh**.
  Preserve owner work/results; use explicit backed-up replacement for a later revision.
  Reject/skip symlink targets and unexpected file types without following them. Keep the
  existing confirmed-clean scope clear: work inside the scaffold is included. Recovery
  backups and completed raw results belong outside it, under approved assets locations.
- Disk accounting: existing guest workspace rows cover disk/exchange/app-CD/config growth;
  the existing recursive dev-demo total covers generated docs, sources and owner work once.
  Existing guest-network evidence row covers item 2. Add only an otherwise-unmeasured
  `assets/logs/delphi-probe/` evidence row for F0/F1; do not double count scaffold or guests.
- Each changed stack updates README, `docs/init-checklist.md`, all-four CHANGELOG entries,
  dev-test/disk coverage and relevant `docs/dev-demo.md`/generated instructions. Add a
  Crostini gotcha only for an evidenced ChromeOS-specific issue. Leave both v101 plans alone.
- Before every push: all-four `bash -n`, `shellcheck -S error dev-*-chromebook*.sh`, whitespace
  and secret review; CI gitleaks remains required. Build checks additionally validate the
  extracted generated helper, version/flag parity and affected isolated regressions.
  Every agent commit ends with `Co-authored-by: Codex <noreply@openai.com>`.
- Read saved `.output`/test `.log` files after owner runs; do not open secret files or dump
  config/environment. Public docs/PR text contain sanitized results/counts and repo-relative
  evidence references, without actual machine/user identities, addresses or runtime details.
  Literal lab topology values already documented are examples, not evidence of a new run.

## 1. Full six-flag regression on released v101

### Finding

**Read-only-checked:** v101's acceptance section explicitly marks this regression NOT RUN.
**Owner-reported:** run it early on the designated regression laptop, keeping the guest lab
available for F0/F1. Use the regression host selected in the Nov 9 request rather than the
guest lab; keep that private machine mapping out of public run reports. These are scheduling
choices, not host inspection results.

### Approach

**Hypothesis:** verify tag/commit before running; use a separate released-v101 checkout if the
working build has advanced. Never downgrade the build tree over owner work. With guests and
heavy workloads stopped by the owner, preflight allocated/free disk using `df -B1`, `du` on
existing stacks/guest workspaces/assets/model stores, the last disk TSV and `docker system df`.
Do not enumerate licensed-media contents. Estimate missing downloads, unpacking/build space,
model/container growth and retained logs; do not treat `install-all` alone as these six flags.
Require remaining free space **at least estimated peak additional allocation + 10 GiB reserve**
before starting under approved choice 1. This is a run budget, not proof the full stack fits
or a new installer threshold. If estimates are unknown or space insufficient, stop for owner sizing; no pruning,
guest moves, cache deletion or silent host substitution. Recheck after setup and before test.

**Hypothesis — commands for later individual owner approval, not execution now:**

```bash
./dev-init-chromebook.sh install-all install-db-server install-lan-share install-models install-ollama-containers install-retro
./dev-setup-chromebook.sh install-all install-db-server install-lan-share install-models install-ollama-containers install-retro
./dev-init-chromebook.sh install-all install-db-server install-lan-share install-models install-ollama-containers install-retro
./dev-test-chromebook.sh install-all install-db-server install-lan-share install-models install-ollama-containers install-retro
```

**Read-only-checked:** setup/test have assets screen-output capture; test also saves its detailed
log and disk report. **Hypothesis:** retain matching timestamps/commit/flags, exit status and
normal prompt return. Read existing saved captures, never secrets; if init has no saved capture,
agree an assets-only capture command before its run. First init on a new machine only writes
the template; the owner fills it privately. Inventory missing log evidence honestly.

**Hypothesis:** turn each FAIL, unexpected WARN, timeout or coverage gap into item 5 evidence,
not an automatic fix. Preserve the v101 result; fixes belong to v102 and do not rewrite history.

### Files/functions, dev-test coverage and docs

**Read-only-checked:** `dev-test-chromebook.sh` owns per-stack checks and `_disk_report`/`dpaths`.
**Hypothesis:** item 1 alone changes no runtime function. Record a sanitized baseline summary
here during the build; raw logs remain in `assets/logs/`. Verify every selected stack ran or
has an explained SKIP, not merely the final FAIL count. No new stack-specific test until a
finding exists. Keep demo outside the four-command regression.

### Owner choices

**Owner-reported — choice 1 approved Nov 9:** early released-v101 baseline on the privately
selected separate regression host with the peak-space budget/reserve above. Run it in parallel
with owner F0 backup/SP6a on the guest lab; both finish before the matrix. No run starts now.

## 2. Execute the guest network matrix

### Finding

**Read-only-checked:** `docs/guest-network-tests.md` supplies a bounded fixed-marker listener;
`demo_retro_advanced` generates 27 initially NOT RUN rows. Twenty-four cover four origins and
six HTTP/browser categories, two cover the local second-NIC link, one is deferred HTTPGET.
The historical ping/domain acceptance is not an HTTP/DNS matrix result.

### Approach and endpoint choices

**Owner-reported — choice 2 approved Nov 9:** retain TCP **8765**, `/marker`, and the v101
marker body for direct comparison. Check port availability first; if occupied, stop and select another port explicitly,
updating all private run URLs. Same-host bind is `127.0.0.1`: Wine uses loopback; NT/2000 use
the existing user-NIC host alias, and win95's installed slirp alias must be verified. If alias
reachability fails, record it; do not silently switch to `0.0.0.0`. Peer marker binds only the
peer's specific Tailscale IPv4. No persistent listener or ChromeOS port forwarding. Stop each
listener and confirm the port is free when finished.

**Owner-reported — choice 3 settled Nov 9:** use **`http://neverssl.com`** for the internet
category, recording any redirect separately. No owner-hosted marker site. **Hypothesis:**
observe status/body/redirect from Linux immediately before/after guest checks; availability and
legacy-client compatibility remain untested here. The peer tailnet marker stays a separate
controlled target and is not the internet result.

**Owner-reported — choice 4 approved Nov 9:** use one available peer laptop with normal tun-mode
Tailscale and the temporary marker. Owner records its IPv4, short name and full tailnet name privately before
running. Test all three against the same peer/port/path. Public docs use target categories and
resolution results; actual names/addresses stay in assets. Guest DNS may fail while IPv4 passes.
This is first/user-NIC HTTP to a peer, not a remote guest second-NIC transport.

**Owner-reported — choice 5 approved Nov 9:** schedule Wine, win95, NT and 2000 using only
their already available HTTP tools/browsers. For each origin run same-host, peer IPv4, peer short/full name, internet HTTP
and a bounded HTTPS comparison. Mark an origin/category **unsupported with reason** only if
the required existing tool/capability is absent; install no browser/tool just for the matrix.
An available path that fails is FAIL, not unsupported. No time to run is NOT RUN. Keep Win31
outside the matrix and HTTPGET's placeholder NOT RUN/deferred. The owner confirms this origin
inventory before starting; unsupported cells must be explicitly accepted at release.

**Owner-reported — stage order:** complete the item 1 baseline and guest-lab backup/SP6a before
the matrix; run the NT rows once on SP6a, not an initial pre-SP6a matrix followed by a routine
post-SP6a repeat. **Hypothesis:** copy the template to a named assets results file; record actual
tool/engine, DNS, connect, HTTP status/body/redirect, elapsed time, outcome and evidence separately. Do not
invent TCP observations a browser cannot expose; use “not observed”. HTTPS results describe
legacy TLS only, not an HTTP failure. Recheck local second-NIC ping/domain and adapter settings
without re-adoption; new hardware/lost settings stops the run for recovery. Owner records raw
results; Codex prepares only a sanitized summary. Gaps and failures feed item 5.

### Files/functions, dev-test coverage, docs and owner choices

**Read-only-checked:** procedure text is also embedded in `demo_retro_advanced`'s STEPS heredoc.
**Hypothesis:** update that copy and `docs/guest-network-tests.md` together to reflect settled choices;
extend results guidance without replacing existing owner templates/results. Reconcile all 27
rows with observations or explicit unsupported/deferred dispositions. Update demo/checklist links
at build time. Retain isolated LAN/scaffold checks; dev-test never requires a peer, public
endpoint, browser, guest or live network matrix. Disk row is already present. Choices 2–5 are
settled; record the actual peer/name forms and existing-tool inventory privately before a run.

## 3. F0 lab prerequisites

### Finding and approach

**Owner-reported:** NT SP6a is supplied and should precede application work; Windows 2000 SP4 is
the recorded baseline. **Read-only-checked:** v101 provides foundation docs, not completed F0.
**Owner-reported — F0 order:** owner-controlled backup → SP6a on NT → Delphi 7 Enterprise
Wine install (or Windows 2000 fallback) → DCOM preparation on both guests. The first two
steps run in parallel with item 1, before the item 2 matrix. **Read-only-checked:** the
existing install command is `delphi 7 setup`, dispatched by `delphi_n_cmd` to `dn_setup`
inside `DEVRETRO_EOF`. **Hypothesis:** check guest-lab free space
for Wine prefix, possible media staging, compiler outputs, logs and retained recovery reserve;
attempt the installation within a bounded session, then take the recorded Windows fallback
if installation or compilation fails. Confirm version/domain/local NIC health after SP6a.
A system-disk snapshot alone is insufficient. Document DCOM preparation on both systems: Enable
DCOM, authentication/impersonation, and HADAMIN account launch/access permissions; owner applies
it only in Windows. [Companion F0](v102-delphi-f0-f1.md#f0-lab-and-prerequisite-record) gives the
backup boundary, settings, media table and stop conditions.

### Files/functions, dev-test coverage and docs

**Hypothesis:** extend `demo_retro_advanced` with create-if-missing
`advanced-demo/docs/media-matrix.md` and `docs/prerequisites.md`, with explicit status fields.
Preserve owner edits during normal generation and demo-refresh. Update generated STEPS,
`docs/dev-demo.md` and checklist at build time. No live guest modification in setup/init/test/demo.
Add isolated preservation/symlink/partial-tree fixtures; dev-test checks generator contracts in
scratch even when no actual demo/guest/media exists. Keep normal disk accounting as above.

### Owner choices

**Owner-reported — choice 6 approved Nov 9:** recovery scope and Windows-only DCOM preparation,
starting with Connect authentication/Identify impersonation and per-application HADAMIN account grants,
with no blanket anonymous/Everyone access. Exact account and recovery location stay private.
F0 completion requires owner confirmation; a generated document is not its completion.
The later owner install step is explicitly `delphi 7 setup`, after free-space review; no
installation or media-content inspection occurs during this planning revision.

## 4. F1 DCOM go/no-go

### Finding and approach

**Read-only-checked:** no application sources exist in the v101 scaffold; `dn_build` in setup's
helper invokes `dcc32.exe` under Wine from the project directory, passing extra compiler options
and preserving producer status. It has no explicit type-library generation or guest-registration
step. **Owner-reported — revised design:** an out-of-process Delphi 7 `TComObject`, registered
through `TComObjectFactory`, implements `IDispatch` by hand without a type library.
`GetTypeInfoCount` returns 0; `GetIDsOfNames` maps one name to one DISPID; `Invoke` returns
the fixed marker plus server computer name/process account. The client calls late-bound through
its own `CoCreateInstance(Ex)`: local mode uses `CLSCTX_LOCAL_SERVER`, remote mode uses
`CLSCTX_REMOTE_SERVER`. `CreateOleObject` is not the selected activation path. These are approved
design choices; Delphi 7/ComServ compatibility remains a hypothesis until verified and confirmed.

**Owner-reported — build/source/transfer:** primary build is `delphi 7 build` under Wine on
the privately designated guest-lab host, with per-command approval for Codex builds/compiler-error
iterations during the build stage. Original quoted heredocs in `demo_retro_advanced` generate
create-if-missing text in `advanced-demo/delphi7/probe`; experiments belong in `work/`.
Put server EXE/server .reg and undo files into Windows 2000, and client EXE/client .reg and undo
files into NT via exchange with each guest stopped; record source revision/output checksums.
Also stage the client EXE in Windows 2000 for the required local activation test.
If Wine install/build fails, install D7 Enterprise in Windows 2000 within F0 and prefer dcc32
there (IDE equivalent), recording why; add the Windows 2000 → Linux → NT transfer hop.
The IDE/TAutoObject/type-library route is a documented second fallback and F2 note, not the
primary probe. No database/provider/MIDAS requirement, new flag or F5 packaging.

**Owner-reported — registration:** original per-machine .reg files and matching undo files write
the AppID, its CLSID link and client RemoteServerName. No type library is registered on either
machine in the primary probe. All registration, activation and DCOM testing occur in Windows.
**Hypothesis:** verify against D7 source/help, then obtain owner confirmation: ComServ operation
without a TLB resource, exact `TComObjectFactory` `/regserver` writes, and whether it supplies an
AppID or the separate file must do so. Distinguish configured RemoteServerName activation from
an explicit target override; no local fallback. Record GO/NO-GO and responsiveness with NT on
its configured accelerator and Windows 2000 on TCG, naming each actual accelerator privately. The
[companion F1](v102-delphi-f0-f1.md#f1-object-build-and-deployment-choices) specifies alternatives,
registration boundaries, timing and one bounded diagnosis.

### Files/functions, dev-test coverage and docs

**Hypothesis:** `demo_retro_advanced` gains original source generation plus build/registration/
results instructions. Prefer quoted source heredocs in that function, following the existing
bundle pattern; no compiled `.exe`/`.tlb`/`.dcu` or vendor source/DLLs are committed. Keep edits
safe on refresh. No helper change expected for F1; `dn_build`, `nt_cmd`, `exch_put`, `app_cd`
and `snapshot_cmd` are existing read-only-checked integration points, not new API promises.
Extend portable lifecycle/source-manifest fixtures and the existing installed dev-test wrapper;
do not compile Delphi or activate COM in dev-test. Docs/checklist explain optional licensed
build tools, transfer approval, per-machine registration and evidence limits. Disk accounting
includes local probe evidence once and guest/demo content in existing rows.

### Owner choices

**Owner-reported — choices 7/8 revised and settled Nov 9:** no-TLB manual IDispatch, Wine-first
build, Windows dcc32/IDE build fallback, IDE/TAutoObject/TLB second fallback, preserved heredocs
and stopped-guest exchange transfers as above. **Choice 9 approved:** Windows-only per-machine
registration, Connect/Identify and recorded server identity, using original .reg/undo files for
the revised design. **Choice 10 approved:** GO/NO-GO evidence and usability judgment, with one
diagnostic session of at most 60 minutes/three single-variable trials after initial NO-GO;
sockets waits for v103. Timing now measures the real NT-configured/Windows-2000-TCG setup.

## 5. Fixes from items 1 and 2

### Finding and approach

**Read-only-checked:** this planning session has no new regression or matrix run evidence.
**Hypothesis:** keep this ledger empty until the owner provides saved evidence from items 1/2.
Do not infer bugs from historical NOT RUN cells or add speculative cleanups/features.

| Entry | Source / evidence | Reproduction and affected stack | Approved fix / files / regression / rerun |
|---|---|---|---|
| None yet | Items 1 and 2 NOT RUN | Not established | Not authorized by a finding |

### Files/functions, dev-test coverage, docs and owner choices

**Hypothesis:** each later entry records sanitized symptom, repo-relative evidence reference,
version/flags, owner-vs-read-only evidence label, root-cause confidence, affected functions,
bounded fix, meaningful regression coverage, disk/doc impacts and owner-run closure. Maintain
original failing evidence alongside the passing rerun. Use required checks for required
capabilities; do not downgrade a failure to WARN to meet the gate. Changes beyond evidenced
scope return as explicit proposals for approval. F1 implementation corrections remain item 4;
item 5 is reserved for item 1/2 findings. No files/functions or extra owner choices are assigned
to an empty placeholder.

## Deferred work and reasons

**Owner-reported scope; hypothesis about future implementation, no additional v102 proposals:**

| Deferred | Reason |
|---|---|
| F2–F4 (Delphi 7 database slice/swap, back-ports) | Wait for F1 decision; F2 expects the Windows 2000 Delphi 7 IDE/debugger regardless of v102 Wine success; IDE/TAutoObject/TLB is also a second-fallback note |
| F5 packaging and transport bridges | Source/runtime manifest and core application must exist first; manual F1 transfer is not a packaging feature |
| F6 remote second NIC / Tailscale MTU | Separate topology, endpoint identity and size-sensitive transport proof required |
| Delphi HTTPGET | Separate compiler/deployment/protocol work; item 2 uses available tools only |
| Oracle | Outside the agreed initial database scope and F0/F1 prerequisites |
| Windows 2000 audio retest | Unrun, separate experiment; preserve TCG/no-sound baseline |
| NT ACCEL comparison | Separate controlled experiment; F1 timings do not reopen acceleration defaults |
| Sockets fallback decision | Explicitly v103 after the bounded v102 DCOM decision |

**Read-only-checked:** v101's companion records the F6 MTU risk as an inference, not a lab
failure. **Hypothesis:** guest Ethernet encapsulated in UDP can exceed the Tailscale path MTU;
small pings do not prove large transfers/DCOM. Future F6 must verify current path MTU,
bidirectional size-sensitive transfers, fragmentation/PMTU, endpoint names and a proven owner-
controlled mitigation. No MTU registry edits, remote link or TCP-MSS “fix” in v102.

## Build stages after the owner merges the approved plan

**Hypothesis — one reviewable commit per stage, with Codex trailer:**

1. **Parallel prerequisites (1/3):** owner runs the released-v101 preflight/baseline on the
   approved regression host while owner backup → NT SP6a proceeds on the guest lab. Both complete before item 2;
   no v102 script changes before the baseline. Keep the two evidence sets separate.
2. **Matrix and triage (2/5):** run NT rows once on SP6a under the settled choices, recording
   actual peer/name forms privately; collect sanitized results and only evidenced fix entries.
   Continue F0 in order with the free-space-checked, bounded `delphi 7 setup` Wine install
   (or Windows 2000 fallback), then Windows-only DCOM preparation. Obtain substantive fix scope.
3. **F0 scaffold (3):** first script change bumps all-four/README/CHANGELOG to 102. Add preserved
   prerequisites/media docs, portable lifecycle checks, docs and disk-row accounting. Owner
   records the ordered recovery/SP6a/Delphi install/DCOM work before F1; stop for missing prerequisites.
4. **F1 probe (4):** original source/build/registration instructions and preservation fixtures;
   Codex may run individually approved Wine builds and iterate compiler errors. If Wine fails,
   complete the Windows 2000 installation/build fallback within F0 and record why. Owner handles
   all guest registration, local then remote activation, real-configuration measurements and
   GO/NO-GO. One bounded diagnosis if needed; no transition into F2 or sockets.
5. **Evidenced fixes (5):** targeted changes and regressions, or record no fixes if no findings.
   A blocking baseline defect can be fixed earlier after its evidence/approval, with the same
   first-script version-bump rule. Revalidate any affected earlier evidence.
6. **Acceptance record:** final static checks, owner regression/targeted reruns and disposition
   of every matrix cell/F0/F1 gate. No automatic merge, tag or release.

## Proposed owner acceptance route

**Hypothesis — proposed release gate, separate from planning approval:**

1. Use settled choices 1–10; merge the plan and authorize individual real runs. Run item 1 at
   released v101 in parallel with the owner's guest-lab backup/SP6a. After both finish, execute
   item 2 with NT rows once on SP6a. Save logs before fixing anything. Complete the remaining
   F0 order: Delphi Wine install/free-space check or Windows fallback, then DCOM preparation.
2. Build on `release/v102`, preserve edits/results and pass static/portable checks. A build
   without owner runtime evidence is **built, not yet confirmed run on a Chromebook**.
3. Complete the ordered F0 recovery/SP6a/Delphi install/settings record; check the no-TLB D7
   hypotheses against installed source/help, retaining hypothesis labels until owner confirmation.
   Build primarily under Wine with per-command approval;
   record any fallback and transfer hop. Execute F1 registration/local then remote tests only
   inside Windows. Measure NT's configured accelerator with Windows 2000 TCG, without overrides. Record
   GO or NO-GO, artifacts/identifiers, HRESULT/failure phase, timings and bounded diagnosis.
   Record owner confirmation of the Delphi behavior against the source/help and Windows evidence.
   Success is not required; missing prerequisites are not silently called a tested NO-GO.
4. On the candidate v102 repeat the full six-flag init → setup → init → test sequence on the
   regression host after renewed preflight/approval. Gate is **FAIL 0**, normal prompt return,
   WARNs only optional credentials or individually documented owner-accepted exceptions;
   explain SKIPs and verify expected selected-stack coverage.
5. Targeted release reruns: always `install-retro` on the guest lab for changed scaffold/helper
   contracts; include `install-agentic install-node` if Inspector/Node/shared harness paths
   change. Each item 5 entry adds its affected flags, e.g. `install-db-server`,
   `install-lan-share`, `install-models` or `install-ollama-containers`, plus dependencies. A
   shared flags/init/setup/test change requires the full six-flag rerun, not a narrow substitute.
   Run the applicable init → setup → init → test sequence for changed installed behavior;
   owner-run dev-demo install-retro separately checks create/refresh preservation and menu.
6. SP6a precedes the initial matrix; no routine second matrix is required merely for SP6a.
   After relevant later fixes/changes, re-run failed/affected matrix paths plus same-host HTTP,
   local ping/domain and first-NIC health. Re-run F1 if later changes affect its sources/registration/
   transport. Record every required matrix row as observed or owner-accepted unsupported;
   only deliberately deferred Win31/HTTPGET work stays outside acceptance.
7. Release requires clean regression, matrix recorded, **F0 done**, and **F1 decision recorded**.
   Publish sanitized summaries with evidence references; never raw local captures or licensed
   outputs. Owner separately authorizes merge/branch deletion/tag/release after acceptance.

## Planning evidence limits

**Read-only-checked:** repo rules, requested v101 plans/procedure/demo/CHANGELOG sections and
current function definitions were read at the baseline above. Public technical references and
their modern-documentation limits are linked in the companion. No media inventory was needed;
no install-media folder listing or contents inspection took place. No setup/init/test/demo,
guest, compiler, listener or transfer was run during planning. The document remains DRAFT with
the Nov 9 choices settled; technical hypotheses and real-run evidence remain unconfirmed.
