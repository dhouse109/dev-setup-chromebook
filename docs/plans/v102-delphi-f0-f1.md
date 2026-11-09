# v102 Delphi F0/F1 detail

Nov 9, 2026 · **DRAFT — companion to [v102 items 3/4](v102-plan.md)**

Evidence labels follow the main plan. **Hypothesis** applies to every proposed procedure,
candidate file/API/tool and expected result below. No code, guest changes, compiler runs,
media listings or licensed-content inspections are part of this planning PR.

## F0 lab and prerequisite record

### Recovery and media

**Owner-reported:** NT 4.0 SP6a and Delphi 7 Enterprise media are available; the historical
Windows 2000 installation is SP4. This is availability/version evidence, not a content check,
an installed Delphi 7 claim or proof of runtime compatibility.

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

**Hypothesis — generated create-if-missing docs:**

| Scaffold path | Initial record / ownership |
|---|---|
| `advanced-demo/docs/media-matrix.md` | Edition/version, intended role, owner verification date, required/unused, status; owner edits preserved |
| `advanced-demo/docs/prerequisites.md` | Recovery confirmation, SP levels, LAN/domain/DCOM preparation, tool/build-route decision, headroom and F0 sign-off |

**Hypothesis — media-matrix initial entries:** NT 4.0 + SP6a (client/DC), Windows 2000 SP4
(server/first local client), Delphi 7 Enterprise (author/build), existing system OLE/Automation
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

**Hypothesis — owner applies and records in Windows, separately on both machines:**

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
required Delphi route/media available, DCOM enable/default/account preparation recorded, and
headroom accepted. Application-specific grants can be finalized only when F1 registers the
real class; record that dependency explicitly, not a fictitious pre-code AppID acceptance.

## F1 object, build and deployment choices

### Smallest contract and source home

**Hypothesis:** use an out-of-process 32-bit Delphi 7 Automation server and a tiny client,
with one Automation-compatible method, e.g. `Probe: WideString` (`safecall`). The returned string
contains fixed marker `dev-bundle-dcom-probe-v102` plus server computer name and server process
account identity, obtained with APIs verified for NT/2000. It reports the server execution
identity, not an unverified claim about the caller. Exact names remain local; public evidence
says “expected remote server/identity matched”. No customer data, provider or MIDAS dependency.

**Hypothesis:** assign one stable original CLSID/AppID/LIBID/IID/ProgID set and document its
mapping before registration. Prefer Automation marshaling and simple BSTR-compatible data;
verify the actual type-library/interface registration required on each OS rather than adding a
custom proxy DLL or assuming type-library registration alone creates a remote server entry.
No callbacks/events, database units, service installation or transport selector for this probe.

**Hypothesis — recommended repo representation:** original quoted source/document heredocs
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
    ProbeContract.pas          # original interface/identifier declarations
    BUILD.md                   # exact verified TLB/resource/build steps
    REGISTER.md                # separate server/client Windows steps, undo
    results-template.tsv       # NOT RUN, copied to assets before use
  work/                        # owner experiments, preserved
```

**Hypothesis:** source files and these new editable docs are create-if-missing even during
demo-refresh. A later source revision uses a separate candidate/version or explicit owner
replacement with backup, never silently overwrites a modified project. Reject unexpected
symlinks/types and cover partial trees. Existing bundle README/STEPS/VERSIONS refresh policy
can stay; point them to the preserved F0/F1 records. Generated readiness never implies build
success. No compile/register/transfer action is added to setup, dev-test or the menu.

**Hypothesis — alternatives:** owner-only `work/` reduces initial bundle scope but leaves the
probe unreproducible in the release; recommend repo-tracked original text. Separate tracked
source files under a new repo directory could improve review, but would need an archive-safe
copy path and installed-dev-test fixtures independent of repository-only assets. Prefer the
existing heredoc pattern for this small probe; revisit a separate repository only with growth.
Any owner-authored IDE changes returned to the repo must be original editable text, reviewed
for credentials/paths/vendor material. Compiled EXE/TLB/DCU/RES and DLLs remain local artifacts.

### IDE versus Wine compiler, and the type-library boundary

**Read-only-checked:** setup's `dn_build` locates installed `dcc32.exe`, changes to the project
directory, passes options and `.dpr`, and returns the compiler's pipeline status. Invocation is
`delphi 7 build PROJECT.dpr [dcc32 options]`; it does not explicitly generate/register a TLB.
This source check proves the wrapper's behavior, not an installed Delphi 7 toolchain.

**Read-only-checked:** modern Embarcadero
[type-library documentation](https://docwiki.embarcadero.com/RADStudio/Sydney/en/Type_Libraries)
distinguishes TLB creation from Pascal compilation and TLB import, and describes IDE generation
and IDL compilers. Its RIDL/GenTLB tooling is modern; this is **not proof of Delphi 7 tools or
switches**. The owner must verify exact legacy help/tool availability later.

**Hypothesis — recommendation:** first author the original object/interface and create its type
library in the Delphi 7 IDE inside Windows 2000, then build server/client there and prove local
activation. Record compiler version, options, identifiers, resource inclusion and original
editable contract. Leave IDE-generated binary TLB/RES local; the build instructions must allow
the owner to regenerate them from the documented original interface. Do not copy licensed
sample projects or vendor units into the repo.

**Hypothesis — command-line alternative:** once the necessary original Pascal, compiler config
and locally generated TLB/resource inputs exist, test the same project with `delphi 7 build`
under Wine, then run the result in Windows. Rebuilding an EXE from an existing TLB is distinct
from creating that TLB without an IDE. `tlibimp` imports an existing library; registration tools
register it. Neither is evidence that `dcc32` produces it from Pascal.

**Hypothesis — fully IDE-free alternative:** investigate an owner-supplied compatible IDL
compiler or an original small Pascal tool using `CreateTypeLib`/`ICreateTypeLib`, compiled with
the licensed D7 command-line compiler. Prove it produces the intended library and marshaling
metadata on these OSes before adoption. Neither tool availability nor implementation is
established here. Do not add a new SDK download or silently copy a TLB from vendor media.
If this route needs material extra work, retain the IDE route; return to the owner if neither
route can reproduce the library within F1 scope.

**Hypothesis — answer to the no-IDE question:** registration need not use an IDE; a Delphi COM
EXE can provide a `/regserver` route, subject to verifying this exact D7 project. TLB creation
without an IDE is technically a separate route to investigate, **not a proven capability of
the existing Wine wrapper**. Do not promise a clean no-IDE build until its TLB/resource steps
are tested. No compiler is invoked in this planning task.

### Transfer without F5 packaging

**Read-only-checked:** the helper already has `exch_put`, app-CD support and guest-stopped
guards; `nt_cmd run` can transfer and launch, so it is not a harmless file-copy/status action.
**Hypothesis:** prefer existing stopped-guest **put/get exchange** operations under explicit
owner approval, with the real exchange drive letter confirmed in Windows. Never mount/write
system disks from Linux or write exchange while a guest is running. Transfer only original
source plus the required local build outputs; record source revision and output checksums.

**Hypothesis — alternative:** a manually created app CD through existing tooling, with an
allowlisted folder containing only original probe source/local probe builds. Store staging and
the local ISO under established assets/guest-workspace locations; `<guest> cd` takes an ISO,
not a folder. Do not sweep install-media directories, DLL collections or database fixtures into
it. No automatic pack command/menu, ISO generator feature, runtime bundling, installer or F5
release kit. Proprietary components stay owner-supplied and out of public artifacts.

### Per-machine registration and activation sequence

**Hypothesis — Windows-only procedure to verify against actual generated project/help:**

1. On **Windows 2000**, place the server in a stable owner-selected local directory. Record
   identifiers and backing files; register the server there (candidate `ProbeServer.exe
   /regserver`, with matching unregister instructions). Verify the actual ProgID → CLSID →
   AppID association, LocalServer32 path and interface/type-library entries. Apply F0's
   per-application launch/access/location/identity settings to this real application.
2. Still on **Windows 2000**, run client local mode, allowing only local-server activation.
   Stop a prior interactive server to distinguish activation from attachment to an existing
   instance. Record activation, method result and server identity; repeat once after shutdown
   of that probe server. No remote configuration is used to manufacture a local pass.
3. On **NT 4.0 SP6a**, supply only the client and verified registration/type information it
   needs. Register the actual interfaces/type library and class/AppID association separately
   from the remote EXE's location. A candidate owner-run registration-only invocation of the
   server on NT is acceptable only if verified to exit without launching the application;
   prefer minimal documented client-side entries to installing an active server there.
   Never use `regsvr32` on an EXE or treat TLB registration as full server registration.
4. On NT's matching AppID set **RemoteServerName** to the Windows 2000 server's managed-link
   identity. Prefer the documented second-NIC IPv4 for the first test, then its verified
   Windows name if needed. Record name resolution and actual endpoint; ensure the first-NIC
   route cannot be mistaken for the intended managed-link result. If RPC advertises another
   interface and changes the path, record/investigate it within budget, not call it a pass.
5. Client remote mode should request **remote-server activation only** and use that AppID
   configuration without an explicit machine override. Verify the remote marker/identity and
   that no local server instance satisfies the call. As a separate diagnostic alternative,
   use explicit remote activation (e.g. `CreateRemoteComObject`/`CoCreateInstanceEx`) with
   the same target; label it distinctly and never infer that it validates RemoteServerName.
6. Document undo: unregister only the probe, restore its backed-up application settings,
   retain domain/other COM registrations and original raw evidence. Registration performed
   in Wine affects Wine, not either Windows guest. Credentials are entered only in Windows.

**Read-only-checked:** Microsoft's
[RemoteServerName reference](https://learn.microsoft.com/en-us/windows/win32/com/remoteservername)
places the setting under the client's AppID; an explicit `COSERVERINFO` target overrides it.
**Hypothesis:** therefore a successful explicit-target call alone cannot verify this registry
route. Actual D7 registration switches, marshaling dependencies and NT execution remain
unverified; BUILD/REGISTER instructions must be corrected from owner evidence before a GO.

### TCG measurements, outcome and bounded diagnosis

**Owner-reported:** v101 found no Windows 2000 KVM fix; keep its TCG/no-sound baseline.
**Hypothesis:** start at existing guest allocations. For the required two-guest TCG timing,
recommend a separately approved temporary NT TCG override if its current selection is different;
restore the original config afterward. This is one workload measurement, not an NT accelerator
comparison or default change. No memory/SMP tuning or audio retest. Record the actual accelerator
for each guest; an NT-auto/KVM run cannot fill the both-TCG evidence cell. If the required run
is not approved or cannot be completed, record the gap and leave the timing gate pending.

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

**Hypothesis — one bounded diagnosis after initial NO-GO:** one owner-approved session, at
most **60 minutes and three single-variable trials**. Work from the observed phase: local COM
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

**Hypothesis:** fake fixtures establish lifecycle/ownership boundaries, not Delphi compilation,
COM ABI or DCOM security. Real owner F0/F1 results stay under `assets/logs/delphi-probe/`, with
summary fields for stage, source revision, compiler/OS version, activation route, marker/identity
match, duration, HRESULT/outcome and evidence reference. Publish only sanitized counts/results
and edition/version facts. The v102 gate is a recorded decision after actual tests, not an
automated dev-test requirement for proprietary software.
