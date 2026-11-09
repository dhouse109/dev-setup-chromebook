# v102 Delphi F0/F1 detail

Nov 9, 2026 · **DRAFT — owner decisions recorded; companion to [v102 items 3/4](v102-plan.md)**

Evidence labels follow the main plan. Recorded owner decisions settle the design; **Hypothesis**
still applies to unverified Delphi compatibility, implementation details and expected results.
No code, guest changes, compiler runs, media listings or licensed-content inspections are
part of this planning PR.

## F0 lab and prerequisite record

### Recovery and media

**Owner-reported:** NT 4.0 SP6a and Delphi 7 Enterprise media are available; the historical
Windows 2000 installation is SP4. This is availability/version evidence, not a content check,
an installed Delphi 7 claim or proof of runtime compatibility. Delphi 7 has not yet been installed
under Wine on any owner's machine. Installation problems must be expected, not assumed away.

**Owner-reported — Nov 9 order:** backup → SP6a on NT → Delphi 7 Enterprise under Wine
(or the Windows 2000 fallback) → DCOM preparation on both guests. Owner backup/SP6a runs in
parallel with item 1 on the separate regression host; both finish before the item 2 matrix.
The matrix's NT rows run once on SP6a. Continue with Delphi installation/DCOM preparation
before F1; a later Wine build failure returns to F0 for the Windows install fallback.

**Hypothesis:** before SP6a or registration, owner shuts down both guests and keeps recoverable
copies of system disks, guest configs, exchange data, app-CD selection and required account/
domain recovery information. Confirm how to restore and reserve space for recovery growth.
Keep credentials outside repo/logs. Prefer a stopped-guest disk snapshot where supported plus
separate config/exchange backup; a raw disk needs an owner-selected recoverable backup instead.
Do not convert disks just to get snapshots. Backups outside the scaffold survive demo-clean.

**Read-only-checked:** setup's generated `snapshot_cmd` supports qcow2 system-disk snapshots,
not a complete config/exchange backup. `nt_cmd` dispatches snapshot operations. **Hypothesis:**
these are optional existing tools for an owner-approved recovery procedure, not commands to run
in planning. The owner applies SP6a from supplied media inside Windows, confirms `winver`,
reboots as required, and rechecks login/domain, unchanged adapters/IP/WINS and both network
paths. Stop before F1 on an unrecoverable backup, wrong SP level or broken lab link.

### Delphi 7 installation and guest-lab disk preflight

**Read-only-checked:** setup's `delphi_n_cmd` dispatches `delphi 7 setup` to `dn_setup`
inside `DEVRETRO_EOF`. This is the actual install subcommand. `dn_setup` selects the supplied
installer/media through `dn_cdroot`/`dn_installer`, prepares the Wine prefix and invokes the
installer; it accepts an explicit installer argument if one is later owner-selected. It can
unpack supplied ISO media and is not a read-only status operation. No helper/media was run here.

**Owner-reported — explicit F0 owner step:** install Delphi 7 Enterprise under Wine on the
privately designated guest-lab host through **`delphi 7 setup`**, after backup/SP6a and a
free-space check. The owner runs/controls the installer. No Wine install is authorized now.

**Hypothesis — preflight and bounded attempt:** use `df -B1` on the guest-lab filesystems
holding the Wine prefix, media staging and assets; use allocated-size `du` on existing prefix/
guest data without listing media contents. Budget prefix installation, possible ISO extraction,
compiler outputs/logs and recoverable backups while retaining the agreed recovery/headroom
reserve; do not use the regression host's free space as evidence for the guest lab. Stop for
owner sizing if the estimate does not fit. Recheck after installation and before compilation.
Allow one installer session, suggested ceiling **60 minutes**, then record success/failure
and the observed blocker. This is an owner-managed budget, not a timeout guaranteed by the
helper; the owner stops a stalled attempt at the limit and proceeds to the fallback. No
unbounded reinstall loops, guest deletion or cache/media pruning.
Installer keys are entered privately; diagnostics retain no keys, credentials or raw registry.

**Owner-reported — first fallback:** if the Wine installation or later Wine build fails,
record why, return to the F0 toolchain step and install Delphi 7 Enterprise in Windows 2000.
Prefer dcc32 from a Windows command prompt; the IDE is an equivalent build alternative. Recheck
DCOM/link settings affected by that install before resuming F1. Windows 2000 Delphi 7 is not
required in v102 when the Wine route works; F2 expects its IDE/debugger regardless. The
IDE/TAutoObject/type-library probe route is a documented second fallback and F2 note, not an
automatic change to the primary no-TLB contract. Record the chosen route and all fallback reasons.

**Hypothesis — generated create-if-missing docs:**

| Scaffold path | Initial record / ownership |
|---|---|
| `advanced-demo/docs/media-matrix.md` | Edition/version, intended role, owner verification date, required/unused, status; owner edits preserved |
| `advanced-demo/docs/prerequisites.md` | Recovery confirmation, SP levels, LAN/domain/DCOM preparation, tool/build-route decision, headroom and F0 sign-off |

**Hypothesis — media-matrix initial entries:** NT 4.0 + SP6a (client/DC), Windows 2000 SP4
(server/first local client), Delphi 7 Enterprise under Wine (primary build; Windows 2000 install
only as fallback in v102), existing system OLE/Automation
support (owner-verifies). InterBase/SQL Server/other Delphi editions are future F2–F4 inventory
only, **not required for F0/F1**; no seed data is needed. Mark exact compiler/runtime tool versions
unknown until the owner verifies them. A later names-only folder inventory needs one explicit
permission request; names cannot establish edition, service-pack installation or DLL capability.
No media mount, extraction, checksum or content inspection is authorized by that inventory.
Public summaries record edition/version facts only; private media paths stay private.

### DCOM preparation on NT 4.0 and Windows 2000

**Read-only-checked:** Microsoft distinguishes authentication from launch/access permissions in
[DCOMCNFG security](https://learn.microsoft.com/en-us/windows/win32/com/enabling-com-security-using-dcomcnfg).
[Per-application settings](https://learn.microsoft.com/en-us/windows/win32/com/setting-processwide-security-using-dcomcnfg)
include execution identity; programmatic security can override registry defaults. These are
documentation checks, not verification of this lab's dialogs or current settings.

**Owner-reported — choices 6/9 approved:** owner applies and records preparation in Windows on
both guests after the toolchain step. **Hypothesis — exact Windows controls/effective behavior:**

1. Record the current settings and a recovery method before editing. Run the installed
   `dcomcnfg`; confirm **Enable Distributed COM on this computer**. Use the controls present
   in NT/2000, not instructions assuming newer Windows “remote activation” checkboxes.
2. Record default authentication and impersonation. Start with **Connect / Identify** as the
   candidate probe baseline; do not lower an existing stronger working setting automatically.
   The probe neither impersonates the caller nor accesses databases/files on its behalf.
   Any need for Impersonate is a new evidence-driven choice, not a blanket preparation step.
3. On Windows 2000, after the probe's registration creates its application entry, choose
   application-specific launch/access permissions for the intended `HADAMIN` user or narrow
   lab group. Preserve required SYSTEM/administrative access and existing unrelated entries.
   NT, as caller, must have DCOM enabled and an authenticated intended HADAMIN logon; record
   its defaults too. Do not grant server-launch rights to the client executable unnecessarily.
4. Record application identity separately from client identity. Prefer **interactive user**
   for the first visible, owner-attended server probe, with that intended HADAMIN user logged
   into Windows 2000. Alternative: a specific lab account entered in Windows DCOMCNFG if
   interactive identity proves unsuitable. No password in source, command line, template or log.
   This initial choice proves an attended lab configuration, not unattended service deployment.
5. Configure the server location locally on Windows 2000; defer NT's RemoteServerName until
   F1 has the actual AppID. Avoid blanket Everyone/anonymous grants, authentication None,
   domain policy rewrites or Linux registry edits. Stop on domain-account lookup failures.
6. Record the effective process security used by the built probe. If generated COM code calls
   `CoInitializeSecurity` or sets proxy security, reconcile it with the Windows settings before
   interpreting a permissions failure. Do not claim that changing the GUI overrides code.

**Hypothesis:** F0 is done only with owner-confirmed recovery, SP6a and baseline link health,
Delphi 7 installed through the selected Wine or Windows fallback route, the bounded attempt/
fallback evidence, DCOM enable/default/account preparation recorded, and
headroom accepted. Application-specific grants can be finalized only when F1 registers the
real class; record that dependency explicitly, not a fictitious pre-code AppID acceptance.

## F1 object, build and deployment choices

### Smallest contract and source home

**Owner-reported — choices 7/8 revised Nov 9:** primary server is an out-of-process Delphi 7
`TComObject`, registered through `TComObjectFactory`, implementing `IDispatch` by hand:

- `GetTypeInfoCount` returns 0; the primary probe has **no type library** or type-library resource.
- `GetIDsOfNames` maps one method name to one DISPID; `Invoke` returns the fixed marker plus
  the server computer name and process account. The client calls late-bound through IDispatch.
- The client supplies its own `CoCreateInstance(Ex)` activation: `CLSCTX_LOCAL_SERVER` for
  local mode and `CLSCTX_REMOTE_SERVER` for remote mode. Do not use `CreateOleObject`, which
  does not request the selected remote activation.
- Original per-machine .reg files with matching undo files write AppID, its CLSID link and
  RemoteServerName. **No type library is registered on either machine** for the primary probe.

**Hypothesis:** choose the one name/DISPID and a stable original CLSID/AppID/ProgID set before
implementation. Use the system IDispatch interface rather than a custom typed interface; verify
the applicable system marshaling without inventing a TLB/custom-proxy requirement. Proposed
method name is `Probe`, returning marker `dev-bundle-dcom-probe-v102` and identity in a BSTR
VARIANT. Validate unknown-name/unsupported-invocation errors and required IDispatch behavior
against D7 help. Actual ComServ/factory compatibility remains unconfirmed, as listed below.
Server identity means computer/process account, not the caller's identity; exact names stay
private, with a public “expected remote server/identity matched” result. No callbacks/events,
database units, provider, MIDAS, service installation or transport selector for this probe.

**Owner-reported — source home:** original quoted source/document heredocs
inside `demo_retro_advanced` (the existing bundle distribution pattern), generated into:

```text
advanced-demo/
  docs/media-matrix.md          # create-if-missing; owner fills
  docs/prerequisites.md         # create-if-missing; owner fills
  delphi7/probe/
    README.md                  # contract and build prerequisites
    ProbeServer.dpr            # original project text
    ProbeObject.pas            # original method/factory implementation
    ProbeClient.dpr            # explicit local/remote modes, result/HRESULT
    ProbeContract.pas          # original name/DISPID/CLSID/AppID/ProgID constants
    win2000-server.reg         # original server AppID/CLSID association
    win2000-server-undo.reg    # matching scoped undo
    nt-client.reg              # original client AppID/CLSID link/RemoteServerName
    nt-client-undo.reg         # matching scoped undo
    BUILD.md                   # Wine-first no-TLB build, Windows fallback reasons
    REGISTER.md                # server/client Windows-only import/undo steps
    results-template.tsv       # NOT RUN, copied to assets before use
  work/                        # owner experiments, preserved
```

**Hypothesis:** source files and these new editable docs are create-if-missing even during
demo-refresh. A later source revision uses a separate candidate/version or explicit owner
replacement with backup, never silently overwrites a modified project. Reject unexpected
symlinks/types and cover partial trees. Existing bundle README/STEPS/VERSIONS refresh policy
can stay; point them to the preserved F0/F1 records. Generated readiness never implies build
success. No compile/register/transfer action is added to setup, dev-test or the menu.

**Owner-reported:** keep `work/` for experiments; original sources remain repo-tracked heredocs,
not owner-only work or separate source files. **Hypothesis:** any owner-authored changes
returned to the repo must be original editable text, reviewed
for credentials/paths/vendor material. Compiled EXE/TLB/DCU/RES and DLLs remain local artifacts.

### Wine-first build, Windows fallback and unverified Delphi 7 behavior

**Read-only-checked:** setup's `dn_build` locates installed `dcc32.exe`, changes to the project
directory, passes options and `.dpr`, and returns the compiler's pipeline status. Invocation is
`delphi 7 build PROJECT.dpr [dcc32 options]`; it does not explicitly generate/register a TLB.
This source check proves the wrapper's behavior, not an installed Delphi 7 toolchain.

**Owner-reported — primary build:** use `delphi 7 build` under Wine on the privately designated
guest-lab host. During the later build stage Codex may run each build command with per-command
approval and iterate on compiler errors, preserving original source revisions and diagnostics.
Example later commands are `delphi 7 build ProbeServer.dpr` and `delphi 7 build ProbeClient.dpr`
from the generated probe directory. Compiling under Wine does not include running either EXE,
`/regserver`, registry imports or activation there. All probe registration/activation/DCOM tests
take place in Windows guests. No TLB generator, registration or resource is part of this route.

**Owner-reported — first fallback:** if the Wine install/build fails, install Delphi 7
Enterprise in Windows 2000 within F0 and prefer dcc32 from a Windows command prompt, using the
same original no-TLB sources/configuration. The IDE is an equivalent way to build. Record
failure phase, why fallback was taken, compiler/version/options and source/output checksums.
The probe's local activation still occurs on Windows 2000 before remote NT tests.

**Owner-reported — second fallback/F2 note:** document the IDE/`TAutoObject`/type-library
route as the second fallback, not the primary F1 design. If needed, record a separate route,
its reason and any changed registration/runtime requirements before owner testing; never
label its result as proof of the no-TLB route. No type library is registered for the primary
probe on either machine. In F2 the Windows 2000 Delphi 7 IDE/debugger is expected regardless;
it is not a v102 installation requirement unless Wine install/build fails. Modern
[type-library documentation](https://docwiki.embarcadero.com/RADStudio/Sydney/en/Type_Libraries)
is background for that fallback, not evidence about D7's exact tools/ComServ behavior.

**Hypothesis — required D7 source/help verification, each pending owner confirmation:**

| Point | Later verification / evidence; currently hypothesis |
|---|---|
| ComServ can host this EXE without a TLB resource | Read exact D7 ComServ initialization/type-library access and matching help; identify any mandatory TLB lookup and prove the original EXE's local startup/activation without adding a hidden resource |
| `TComObjectFactory` registration behavior | Read exact factory/ComServ `/regserver` path and help; record its ProgID/CLSID/LocalServer32 and other writes, including whether it attempts type-library work; verify only inside Windows |
| Separate AppID registration | Determine whether that D7 factory writes an AppID and its CLSID link; reconcile with the original per-machine .reg files, writing the required AppID/link explicitly without contradictory duplicate ownership |

**Hypothesis:** keep all three points labelled hypotheses until the owner confirms the
matching source/help and Windows evidence; successful compilation alone does not settle them.
This task performs no licensed source/help or media-content inspection. During the later build,
use owner-provided installed D7 source/help for that verification; do not copy vendor units/help
into the repo or substitute modern RAD Studio behavior. Keep original registration/undo files
consistent with observed factory writes and preserve unrelated application/system keys.

### Transfer without F5 packaging

**Read-only-checked:** the helper already has `exch_put`, app-CD support and guest-stopped
guards; `nt_cmd run` can transfer and launch, so it is not a harmless file-copy/status action.
**Owner-reported — transfer path:** through exchange, with each guest stopped, put the server
EXE and its original server .reg/undo files into Windows 2000; put the client EXE and its
original client .reg/undo files into NT. Record source revision and output checksums. No
vendor DLL/media or type library travels with the primary probe.
Also stage the client EXE in Windows 2000 to perform the required local activation before
testing it remotely from NT; it needs no remote-client .reg settings for that local mode.

**Owner-reported — Windows build fallback:** deliver the original source/configuration and
registration files to Windows 2000 through stopped-guest exchange, build there, then take the
Windows 2000 → Linux → NT hop for the client EXE/registration files. Shut down the source guest
before extraction and the destination guest before insertion. Preserve the same source/output
checksum record across that hop. Registration/activation remains inside the Windows guests.

**Hypothesis:** confirm the real exchange drive letter and exact per-machine destinations in
Windows. Never mount/write system disks from Linux or write exchange while a guest is running.
Use existing put/get operations only after approval. No app-CD path is selected for F1; F5
packaging remains deferred. Do not add pack/menu/ISO generation, runtime bundling or an installer.
Proprietary components stay owner-supplied and out of public artifacts.

### Per-machine registration and activation sequence

**Owner-reported:** original per-machine .reg files and matching undo supply AppID, CLSID link
and RemoteServerName; no type library is registered in the primary probe. All steps below are
Windows-only. **Hypothesis — verify exact behavior against D7 source/help and owner evidence:**

1. On **Windows 2000**, place the server in a stable owner-selected local directory. Record
   identifiers and backing files; register the server there (candidate `ProbeServer.exe
   /regserver`, with matching unregister instructions). Verify the actual ProgID → CLSID →
   AppID association and LocalServer32 path against the factory's observed writes. Import the
   original server .reg file to establish/reconcile its AppID and CLSID link; preserve the
   matching undo and baseline. Confirm no type library was registered. Apply F0's
   per-application launch/access/location/identity settings to this real application.
2. Still on **Windows 2000**, run client local mode, allowing only local-server activation.
   Stop a prior interactive server to distinguish activation from attachment to an existing
   instance. Record activation, method result and server identity; repeat once after shutdown
   of that probe server. No remote configuration is used to manufacture a local pass.
3. On **NT 4.0 SP6a**, supply the client EXE and original client .reg/undo files. Import only
   its class/AppID association and remote activation settings; do not put/register a server
   EXE, custom interface or type library there. System IDispatch support is the candidate
   marshaling path to verify. Never use `regsvr32` on an EXE.
4. The original NT .reg file sets **RemoteServerName** under the matching AppID to Windows
   2000's managed-link identity. Prefer the documented second-NIC IPv4 first, then its verified
   Windows name if needed. Record name resolution and actual endpoint; ensure the first-NIC
   route cannot be mistaken for the intended managed-link result. If RPC advertises another
   interface and changes the path, record/investigate it within budget, not call it a pass.
5. Client remote mode calls its own `CoCreateInstance(Ex)` with **`CLSCTX_REMOTE_SERVER`**
   and IID_IDispatch, then GetIDsOfNames/Invoke. Use the AppID configuration without an explicit
   machine override first, verifying RemoteServerName, the remote marker/identity and absence
   of local fallback. Local mode uses **`CLSCTX_LOCAL_SERVER`**. `CreateOleObject` is excluded.
   A separate `CoCreateInstanceEx` diagnostic with explicit COSERVERINFO target is labelled
   distinctly and cannot validate RemoteServerName. Neither route consults/registers a TLB.
6. Document undo: use each matching original per-machine undo file for the probe-owned keys,
   unregister only the probe's factory entries where applicable, restore backed-up application settings,
   retain domain/other COM registrations and original raw evidence. Registration performed
   in Wine affects Wine, not either Windows guest. Credentials are entered only in Windows.

**Read-only-checked:** Microsoft's
[RemoteServerName reference](https://learn.microsoft.com/en-us/windows/win32/com/remoteservername)
places the setting under the client's AppID; an explicit `COSERVERINFO` target overrides it.
**Hypothesis:** therefore a successful explicit-target call alone cannot verify this registry
route. Actual D7 factory/ComServ behavior, registration switches, system IDispatch marshaling
and NT execution remain hypotheses until source/help verification and owner confirmation;
BUILD/REGISTER and matching .reg/undo files must reflect that evidence before a GO.

### TCG measurements, outcome and bounded diagnosis

**Owner-reported:** v101 found no Windows 2000 KVM fix; keep its TCG/no-sound baseline.
**Owner-reported — revised timing:** measure the demo's **real configuration**: NT uses its
configured accelerator and Windows 2000 uses TCG. Record each guest's actual accelerator in
private evidence. No temporary NT TCG override, accelerator comparison or default change.
**Hypothesis:** start at existing allocations; no memory/SMP tuning or audio retest. If a
measurement cannot be completed, record the gap rather than inventing a timing result.

**Hypothesis — measurement protocol:** with heavy models/databases stopped by the owner,
record Windows 2000 alone and then both guests running: time to usable desktop/logon, one
ordinary UI action, first activation/call, and five subsequent calls. Record elapsed values,
min/median/max call time, freezes/timeouts, host headroom and owner usability judgment privately.
Keep source/binary revision and all comparison settings fixed. Suggest a 180-second observation
limit for a single activation/call, after which the owner stops the client deliberately and
records timeout; do not claim a killed client cancelled server RPC. Use an external stopwatch
if no reliable in-guest timer exists; do not add timing software. The owner decides whether
observed responsiveness is acceptable rather than inventing a universal TCG SLA.

**Hypothesis — decision record:** GO requires local activation/call and remote NT → 2000 call
on the intended link, matching marker/remote identity, recorded registration/security route
and accepted responsiveness. NO-GO records exactly which phase failed, HRESULT/error, route,
versions, attempted settings, timeout/timings and repo-relative evidence reference. A successful
explicit-target call with an unresolved configured route is a qualified finding, not an
unqualified GO. A missing prerequisite stops F1 before the test and leaves its gate pending.

**Owner-reported — choice 10 approved:** one bounded diagnosis after initial NO-GO, at
most **60 minutes and three single-variable trials**. **Hypothesis:** work from the observed phase: local COM
registration, remote naming/endpoint reachability, authenticated permissions/identity or actual
runtime dependency. Restore the baseline between trials, retain the original failure and record
each result. Stop earlier for lost NIC settings, unsafe recovery, low headroom or scope growth.
At the limit write final GO/NO-GO with evidence; an unexplained failure is an honest NO-GO,
not a reason for unlimited experiments. **Sockets fallback is a v103 decision**, not a fourth
trial, automatic transport change or v102 database milestone.

### Portable validation and owner evidence

**Hypothesis:** extend the scaffold fixtures invoked by dev-test and portable test entrypoints
for new-doc/source creation, partial trees, repeated generation, refresh preserving edited
sources/docs/results, symlink refusal, unchanged launcher actions and confirmed-clean targets.
Validate source/output allowlists and that generation/steps/status/results never invokes a
compiler, guest engine, listener, transfer or registration tool. Retain v101's LAN identity/
status/argv coverage; account for evidence bytes without double counting guests/demo content.
Check the generated primary manifest contains original per-machine .reg/undo files and no
type-library resource dependency or vendor binaries. Portable checks do not claim that ComServ works
without a TLB, factory registration is correct, or a live IDispatch call succeeds.

**Hypothesis:** fake fixtures establish lifecycle/ownership boundaries, not Delphi compilation,
COM ABI or DCOM security. Real owner F0/F1 results stay under `assets/logs/delphi-probe/`, with
summary fields for stage, source revision, compiler/OS version, activation route, marker/identity
match, duration, HRESULT/outcome and evidence reference. Publish only sanitized counts/results
and edition/version facts. The v102 gate is a recorded decision after actual tests, not an
automated dev-test requirement for proprietary software.
