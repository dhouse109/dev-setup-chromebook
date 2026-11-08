# Delphi multi-tier demo across Delphi 3–7: plan

Nov 8, 2026 · **v101 foundation planned; application code deferred to a staged follow-up**
· companion to [v101 plan item 9](v101-plan.md#9-bundle-foundation-for-the-later-delphi-demo)

## Version boundary and approval status

The owner has now limited **v101** to the bundle's supported guest-network command, the
`advanced-demo` scaffolding in dev-demo, and documentation. The application described below is the
**follow-up target**, not code to write in v101 and not a v101 release gate. This instruction
supersedes earlier wording that called the whole application a v101 demo.

The agreed code location, service-pack prerequisite and version/database mapping remain agreed.
Implementation mechanisms and the remaining choices below are recommendations awaiting approval.
This planning commit changes neither scripts nor installed tools/guests. Real commands still need
individual owner approval; licensed media is supplied by the owner, never downloaded by the bundle.

### What v101 supplies

- Per-guest `winnt40 lan` / `win2000 lan` status/on/off with a default-off managed second PCnet
  adapter, the proven local UDP preset, validation and manual adoption of existing EXTRA_ARGS.
  Explicit Tailscale endpoint mode is recommended but still an owner choice; a local-only first
  release is the alternative. Exact grammar, paths, guards and fixtures are in main-plan item 9A.
- Foundation docs, version matrix, initially empty results template and owner work directory at
  `~/dev-demo/retro/delphi/advanced-demo`, with a nested launcher offering steps/status/results and
  optional explicit documentation-only CD packaging. Main-plan item 9B defines index/lifecycle
  compatibility and preservation behavior. Existing `retro/matrix` stays available.
- Network/IP/driver/SP6a/media instructions, the item 8 test protocol and clear labels for evidence
  already collected versus checks still pending. No automatic VM boot, service-pack/database
  installation, domain/DCOM configuration or application success claim.

**Not generated in v101:** Delphi projects/forms/type libraries, HTTPGET source, per-dialect seed
SQL, compiled programs, transport bridges, registration scripts or a runnable database-swap demo.
The optional v101 ISO contains allowlisted foundation docs only, not placeholder application code.

### Foundation files, checks and documentation

- **Setup:** generated `DEVRETRO_EOF` helper's help/main dispatch, QEMU launch/config integration
  and proposed LAN config/status/argv functions. JSON lives under `~/.config/dev-retro`, defaults
  off; never source it as shell or silently replace the owner's manual NIC arguments.
- **Dev-demo:** proposed `demo_retro_advanced`, install-retro dispatch, `begin`/`write_run`/
  `done_demo`/`write_index` relative-path metadata and clean handling. Use a flat index key with
  nested directory/launcher paths; do not put a slash into STACK/index filenames. Preserve future
  owner code and results on rerun/demo-refresh; ordinary bundle docs may refresh.
- **Dev-test:** fake-QEMU argument/config fixtures for local/remote pairs, unique MACs, reciprocal
  ports, on/off/stopped guards, custom networking conflicts, corrupt/symlink state, no-write status,
  first-NIC preservation and setup exchange withholding. Scaffold fixtures verify nested index,
  launcher syntax, honest pending-stage labels, refresh/clean and the pack allowlist. Missing
  manually installed Delphi/databases or an ungenerated live demo is never a retro FAIL.
- **Disk report:** existing "Retro helper and config" row already measures the new LAN config's
  parent; clarify its label rather than count it twice. Add retained ISO/results under assets once;
  existing NT/2000 rows cover guest disks/media. Source/docs are small; measure scaffold/
  ISO after generation rather than add an unmeasured database-size claim to the demo total.
- **Docs:** README, init checklist, dev-demo footprint, Crostini network/MAC/TCG notes, proposed
  `docs/guest-network-tests.md`, generated STEPS and all four CHANGELOG sections at build time.
  All four script versions/flags remain synchronized, with no new install flag recommended.

**v101 acceptance:** static checks/isolated fixtures, owner local-link ping/domain/first-NIC checks,
safe on/off adoption, scaffold lifecycle/menu/optional ISO verification, and clean approved bundle
test. Remote UDP is separate evidence if tested; DCOM/database results are follow-up acceptance.

## Goal

One small Delphi application, built in each of Delphi 3, 4, 5, 6 and 7 (all Client/Server or
Enterprise editions), shows the multi-tier pattern of its era:

- an **application server** exposes `GetCustomers` (and `GetBackendInfo`) over a database;
- a **client** on a *different* operating system calls it over the network and shows the rows;
- the demo **swaps the database** behind the server (to another database of the same era) while the
  client stays exactly the same.

Two settings, in order:

1. **One laptop (joxer):** two operating systems as two QEMU guests (NT 4.0 and Windows 2000) on the
   guest network proven on Nov 8. This must work completely before step 2.
2. **Two laptops:** joxer runs the servers and databases; yaviks runs the clients.

**Database scope (owner decision, Nov 8):** the follow-up demo uses **InterBase and SQL Server
only**, to keep the unknowns down. Oracle (8.0.5 and 8i media on hand) is a still later step; see
"Later: Oracle". Neither database integration is implemented in v101's foundation.

## What each Delphi version brings

| Delphi | Year | Multi-tier framework | Client connections | Database access |
|---|---|---|---|---|
| 3 C/S | 1997 | MIDAS 1: Remote Data Module, provider, `TClientDataSet` | DCOM; OLEnterprise | BDE + SQL Links |
| 4 C/S | 1998 | MIDAS 2 | DCOM; **sockets** (`scktsrvr`); OLEnterprise; CORBA | BDE + SQL Links |
| 5 Ent | 1999 | MIDAS 3 (stateless providers, `TWebConnection`) | DCOM; sockets; **HTTP** (`httpsrvr.dll`) | BDE; **ADO** (ADOExpress); **IBX** |
| 6 Ent | 2001 | DataSnap | DCOM; sockets; HTTP; **SOAP** | **dbExpress**; ADO; IBX; BDE |
| 7 Ent | 2002 | DataSnap | DCOM; sockets; HTTP; SOAP | dbExpress (adds an MSSQL driver); ADO (dbGo); IBX; BDE |

The framework names, connection history and edition drivers are inherited working hypotheses, not
newly verified compatibility claims. Confirm each against the owner's exact help and demos in the
follow-up before choosing units, component names, runtime DLLs or providers. This planning pass
did not inspect licensed media or run a compiler.

## Era-specific databases and the swap

SQL Server from the owner's media; InterBase from the Delphi CDs (each Client/Server or Enterprise
CD carries an InterBase of its year).

| Delphi | Server guest | Primary database | Swap to | Access (primary / swap) |
|---|---|---|---|---|
| 3 | NT 4.0 | SQL Server 6.5 | InterBase | BDE SQL Links MSSQL / BDE SQL Links InterBase |
| 4 | NT 4.0 | InterBase | SQL Server 6.5 | BDE SQL Links InterBase / MSSQL |
| 5 | Windows 2000 | SQL Server 2000 | InterBase | ADO (SQLOLEDB) / IBX |
| 6 | Windows 2000 | InterBase | SQL Server 2000 | dbExpress / ADO (Delphi 6's dbExpress has no MSSQL driver, as far as known) |
| 7 | Windows 2000 | SQL Server 2000 (Northwind) | InterBase | dbExpress MSSQL or dbGo ADO / dbExpress |

- **Era logic:** NT 4.0 hosts SQL Server 6.5 (1996), Windows 2000 hosts SQL Server 2000. Each Delphi
  version's server runs where its databases are; its client runs on the other OS.
- **Primary database alternates** between SQL Server and InterBase so the versions don't all look
  alike, and each shows a different access layer of its time (BDE, ADO, IBX, dbExpress).
- **One InterBase per guest:** InterBase servers of different versions can't run side by side on one
  machine (one service, port 3050). Proposal: NT 4.0 gets the InterBase from the Delphi 4 CD (used by
  Delphi 3 and 4), Windows 2000 the one from the Delphi 7 CD (used by Delphi 5–7). Older clients
  against a newer InterBase server are checked in phase D; fall back to each version's own InterBase,
  installed one at a time, if they don't work.
- **How the swap is shown:** the server registers one server object per database (for example
  `CustomerSrv.SQLServer` and `CustomerSrv.InterBase`, or one object with a `Backend` setting). The
  client picks the server object from a list. Its code, form and data handling stay the same, and
  `GetBackendInfo` displays which database answered. That makes "the client doesn't know or care"
  visible.
- **Same data everywhere:** one `CUSTOMERS` table (ID, company, contact, city, country; seeded from
  Northwind's Customers) is created in every database by a per-dialect seed script, so every swap
  returns the same rows. (SQL Server 6.5 ships `pubs`, not Northwind, so the seed script supplies the
  rows there.)
- **Not available:** SQL Server 7.0 (Delphi 4–5's exact era) isn't in the owner's media; SQL Server
  2000 stands in.

## Topology on one laptop

```
 winnt40 guest (NT 4.0, DC "HADAMIN")         win2000 guest (Windows 2000, joined)
 192.168.50.10                                 192.168.50.20
 SQL Server 6.5, InterBase (Delphi 4 CD)       SQL Server 2000, InterBase (Delphi 7 CD)
 Delphi 3/4 servers  <-- DCOM / sockets -->    Delphi 3/4 clients
 Delphi 5/6/7 clients <-- DCOM / sockets -->   Delphi 5/6/7 servers
            \___ point-to-point UDP socket link (second PCnet NIC) ___/
```

- **Domain accounts** (HADAMIN) make DCOM security much simpler than matching local accounts: the
  client's user is known to the server machine.
- **Memory proposal:** NT 4.0 at 128–256 MB (128 MB today), Windows 2000 at 512 MB for its later
  SQL workload (256 MB today). Start network-only v101 checks at current allocations. Run one
  database workload at a time; measure real headroom before requiring simultaneous workloads.
  The helper currently uses `-smp 1`; TCG's multi-thread setting is not two guest vCPUs. No global
  memory/SMP change is proposed for v101.
- **IDEs:** Delphi 3 and 4 installed in NT 4.0, Delphi 5–7 in Windows 2000 (their eras; Borland's
  debugger works there). Wine builds (`delphi N`) stay optional.
- **Deployment hypothesis to verify per version:** the client `.exe`, the client DLL (`dbclient.dll` for
  Delphi 3/4, `midas.dll` from Delphi 5) registered with `regsvr32`, and the server's registration on
  the client machine (the type library or the registry entries the server's `/regserver` writes, with
  `RemoteServerName` set to the server's address). Target: no database client software on the thin
  client. Verify actual COM registration/AppID/type-library and runtime dependencies; do not turn
  these remembered details into untested registration scripts.

## Application phases — staged follow-up, not v101 implementation

**A. Foundation boundary (one laptop)**

- v101 makes the hand-proven guest link supported and supplies docs/scaffolding only. Guest
  snapshots remain explicit owner actions; keep configs/exchange data with backups because an
  internal system-disk snapshot is not a backup of the entire lab.
- Follow-up begins with owner SP6a/media preparation, workload sizing and DCOM baseline:
  `dcomcnfg`, Enable DCOM, proposed Connect/Identify and specific HADAMIN account access/launch
  permissions. Verify the settings against installed versions, then use a trivial out-of-process
  object. This object is the **first later code**, not a v101 scaffold feature. Do not blanket-disable
  authentication or rewrite domain permissions from Linux.

**B. Follow-up vertical slice (go/no-go): Delphi 7 + SQL Server 2000**

- SQL Server 2000 (Mixed Mode, Northwind) and Delphi 7 in Windows 2000.
- Server and client both in Windows 2000 first; then the client on NT 4.0 over DCOM. If DCOM fails,
  stop for bounded diagnosis and an owner choice of socket fallback (`scktsrvr`) before proceeding.

**C. Follow-up swap in Delphi 7:** InterBase from the Delphi 7 CD in Windows 2000, the second server
object, the client choosing between them.

**D. Follow-up back-porting, newest to oldest:** Delphi 6 (InterBase over dbExpress first), 5 (ADO and IBX;
first HTTP option), 4 (NT 4.0 server, InterBase / SQL Server 6.5, sockets as well as DCOM), 3 (NT 4.0
server, SQL Server 6.5 / InterBase, DCOM only). The client of each version runs on the other OS.

**E. Follow-up bridges:** Socket Server for win95/Wine; SOAP (Delphi 6/7) for Lazarus/Linux;
OLEnterprise (Delphi 3/4) as a period alternative with DOSBox-X normal core (main-plan item 7).
Confirm Socket Server port/runtime against the matching media. Guest inbound serving requires a
separately planned user-NIC hostfwd feature: map a high host TCP port to the guest service rather
than require root to bind host port 211. Wine uses host loopback, win95 uses its host alias and
cross-laptop clients use the host's Tailscale address. No hostfwd/bridge implementation in v101.

**F. Follow-up two laptops: joxer (servers) and yaviks (clients)**

- yaviks needs install-retro and its own NT 4.0 / Windows 2000 guests (owner's media). As clients
  they need no database software.
- A point-to-point pair spans Tailscale using explicit numeric peer and **specific local Tailscale
  binds**, reciprocal ports, distinct MACs and unique guest addresses. Test one server/client
  guest pair at a time. Two guests on each laptop simultaneously need an additional hub/switch
  topology; one UDP pair does not provide a four-guest LAN. Prove reachability/domain identity and
  DCOM separately; they are not guaranteed by the local Nov 8 success. Socket/HTTP may later use
  Tailscale TCP plus the separately designed hostfwd path.
- Show each Delphi version's client on yaviks against its server on joxer, with the database swap.

## Guest state and service packs (owner, Nov 8)

- **win2000 guest:** Windows 2000 5.00.2195 **Service Pack 4** already installed; 256 MB RAM today
  (raise to 512 MB for SQL Server 2000); Pentium III-class CPU; two LAN adapters enabled.
- **winnt40 guest:** NT 4.0 4.00.1381 with **no service pack** yet; 128 MB RAM; Pentium CPU
  (`CPU=pentium`, item 5).
- **Owner-supplied service packs available:** NT 4.0 SP1–SP6a and Windows 2000 SP1–SP4 (bring your
  own media; nothing in the bundle downloads them).
- **Plan:** snapshot winnt40, then install NT 4.0 **SP6a** before SQL Server 6.5, InterBase or any
  Delphi client (Delphi 5–7 programs and later MDAC want SP6a; reapply SP6a if a later install
  replaces system files). SQL Server 6.5's own service pack (SP5a was its last) is checked when SQL
  Server 6.5 goes in; not blocking.

## Risks and checks to do early

- **InterBase versions:** older BDE SQL Links and IBX against a newer InterBase server (see "One
  InterBase per guest"); InterBase 6+ dialect 1 vs 3 for the seed script.
- **DCOM through Tailscale:** DCOM uses dynamic ports and endpoint identities. A raw guest link
  avoids per-RPC NAT mappings, but naming, advertised endpoints and permissions still need separate
  tests in phase F. Local ping/domain success alone does not establish remote DCOM.
- **TCG speed:** two guests on software emulation will be slow; phase B measures it.

## Where the demo's code lives (owner decision, Nov 8)

- **In dev-demo, in a Delphi folder of its own called `advanced-demo`:** agreed path
  `~/dev-demo/retro/delphi/advanced-demo`, next to the existing `retro/matrix`. dev-demo generates
  foundation docs in v101. **The follow-up** extends it with Delphi projects, per-dialect seed
  scripts and an application CD through genisoimage/`<guest> cd`. No application sources now.
- **When it is ready for release** it may move to its own repository, depending on its size.
- **Follow-up source proposal:** code-built forms avoid incompatible DFM formats; share the small
  customer contract/data presentation where practical, with version-specific projects/adapters
  for provider/transport/runtime differences. Verify Delphi's compiler symbols from its help;
  VER100/120/130/140/150 are candidate guards. Do not promise one unchanged source or binary
  transport ABI across all five releases before compiling/testing them. No such files in v101.

## Owner decisions recorded (Nov 8)

1. Code location: dev-demo, `advanced-demo` (above).
2. Service packs: available; winnt40 gets SP6a first (above).
3. The version-to-database mapping above is agreed.
4. Current task: v101 stops at supported network/scaffold/docs; code is staged afterward.

## Follow-up work packages and acceptance gates

These are a roadmap for a later approved version/stage, not build instructions for this v101 plan.
Use a new approved plan and version branch before writing application code. Keep each package
small enough for one reviewable commit and an owner-run result. Proposed source paths below are
inside `advanced-demo`; the follow-up decides whether their growth warrants a separate repository.

| Stage | Approach / proposed files | Verification and stop condition |
|---|---|---|
| F0: media/runtime inventory | Verify edition help, InterBase/runtime versions and licensing; write `docs/media-matrix.md` and `docs/prerequisites.md`; owner snapshots/SP6a | Exact component/driver names and owned media paths recorded; stop before code if core components are absent |
| F1: local DCOM object | Small Delphi 7 object/client, proposed `delphi7/probe/`; explicit per-machine registration instructions | Local activation/call first, then NT client ↔ 2000 server; confirm credentials/bitness/runtime before database work |
| F2: Delphi 7 vertical slice | `delphi7/server/`, `delphi7/client/`, SQL Server adapter, agreed GetCustomers/GetBackendInfo contract | Known rows locally and on other OS, clear backend ID, bounded failure on server loss; if remote DCOM fails investigate then decide socket fallback |
| F3: Delphi 7 database swap | InterBase adapter, dialect-specific `seed/` scripts and same client contract | Same rows/order/fields from both databases, backend identity changes; stop if runtime/data contract differs |
| F4: back-port 6 → 5 → 4 → 3 | Per-version project/adapter/runtime docs; share proven presentation/contract only | Each compiles with its own compiler, runs client on other OS and swaps agreed databases; record each transport/version explicitly |
| F5: optional bridges | Separate sockets/HTTP/SOAP/OLEnterprise projects and hostfwd plan, only after prerequisites verified | Wine/win95/Lazarus routes measured independently; unsupported transport is explicit, never replaced by an unlabelled local call |
| F6: second laptop | Reuse proven pair and application artifacts; docs/results update, no hidden topology expansion | One-laptop stages pass first; then cross-laptop calls and swap per version, credentials/DNS/port failures distinguished |

For every later application stage, dev-demo generation/refresh and ISO packing must preserve owner
edits/results. Keep sources create-if-missing or versioned; make replacement explicit with backup.
No licensed DLL/CD/database content goes into the repo or a public artifact. Guest credentials are
entered in Windows; any later host-side secret must follow `secrets.env` rules, never templates/logs.

**Testing boundary:** portable tests can validate generated trees, source manifests, safe launchers
and packaging. The existing dev-test may verify installed toolchain/helper capabilities, but it
must not require proprietary compilers, Windows guests, SQL databases, domain accounts or a live
DCOM connection on every install-retro machine. Application acceptance is an owner-run matrix
by compiler, OS, transport and backend, with raw results retained under assets and sanitized
summaries in the plan. Update README/checklist/dev-demo/CHANGELOG at each eventual bundle stage;
revisit disk rows for application sources/CD and distinguish guest disk growth already counted.

### Follow-up owner choices and recommendations

These do not block committing the v101 foundation plan. Settle them in the staged follow-up:

- **First access layer:** recommend Delphi 7 dbGo/ADO with SQLOLEDB for the initial SQL Server 2000
  slice, because it separates the DCOM go/no-go from dbExpress-driver uncertainty. Later demonstrate
  the agreed era driver once the exact media confirms it. Alternative: dbExpress first if supplied
  and working. The agreed era mapping stays intact; this selects the first slice, not new scope.
- **Swap control:** recommend one stable version-specific server class/contract with a server-side
  Backend setting, displayed through GetBackendInfo. Alternative: separate ProgIDs selected by
  the same client. Decide runtime reactivation/reconnect behavior before promising a live switch.
- **InterBase:** recommend one server per guest as proposed (Delphi 4-era on NT, Delphi 7-era on
  2000), but only after client/dialect compatibility tests. Alternative: sequential per-version
  installs with backups; do not assume unlike servers can share service/port or database files.
- **Seed data:** recommend a small owner-created/licensed customer fixture with a documented schema,
  or local seed extraction from the owner's Northwind installation. Do not redistribute Northwind
  rows until their redistribution terms are verified. Decide field types/encoding/dialect and
  whether every backend must return the exact same ordered subset.
- **Failure policy:** recommend one bounded DCOM investigation after F1/F2 failure, then ask whether
  to take the sockets route. Label that change explicitly; do not call a sockets result DCOM.
- **Bridges/topology:** recommend F5/F6 only after the core one-laptop swap. Confirm which optional
  transports matter and whether a four-guest hub is needed; otherwise keep one pair at a time.
- **Code home:** retain the agreed dev-demo home initially; decide a separate repository only when
  actual source/fixture size and review burden justify moving it.

## Later: Oracle (outside v101 and the first application follow-up)

Owner has Oracle 8.0.5 for NT and Oracle 8i media (and a `9` folder, contents unknown). When added:
Oracle 8.0.5 on NT 4.0 as Delphi 4's era database (BDE SQL Links Oracle), Oracle 8i on Windows 2000
for Delphi 5–7 (ADO/dbExpress), as a third swap target behind the same client. Known risks to check
then: Oracle 8i's Java installer failing on newer CPUs (the guests' Pentium-class CPU model may
avoid it), Oracle's memory needs (Windows 2000 at 768 MB+), and Net8 client configuration on each
application server. Whether Delphi 3's SQL Links support Oracle 8 is to be checked.
