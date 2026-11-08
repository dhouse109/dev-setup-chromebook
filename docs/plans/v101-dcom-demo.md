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

The owner approved **9A local-only** and **9B without pack** in the review of `936737b`. v101 will
provide `winnt40 lan` and `win2000 lan` status/on/off for the proven local second-PCnet pair. The
feature will default off and require explicit adoption of existing manual EXTRA_ARGS. Main-plan
item 9A compares a separate JSON file with LAN keys in the existing guest config and recommends
the latter; that new recommendation remains for final review.

The approved scaffold will live at `~/dev-demo/retro/delphi/advanced-demo`. Its nested launcher
will offer steps, read-only status and results guidance. It will include foundation instructions,
the agreed version matrix, a results template initially marked NOT RUN and an owner work directory.
Main-plan item 9B describes compatible index/lifecycle changes and preservation on rerun/refresh.
Existing retro/matrix will remain available.

There will be no pack action or generated ISO in v101. Delphi projects, HTTPGET source, seed SQL,
compiled programs, COM registration, transport bridges and database integration all belong to the
follow-up. The scaffold will not boot VMs, install software, configure a domain/DCOM or claim that
an application stage passed. Cross-laptop mode and packaging will wait until their later stages.

### Foundation files, checks and documentation

Setup's generated helper will gain local LAN dispatch, status, conservative config editing and
validated QEMU arguments. With the recommended LAN keys, the existing per-guest config remains
the single settings location. Read-only status and editing will not execute shell config.

Dev-demo will gain `demo_retro_advanced` and compatible relative-path handling in `begin`,
`write_run`, `done_demo`, `write_index` and clean logic. The flat index key will refer to nested
paths. Refresh will update bundle documentation while preserving future owner code and results.

Dev-test will use isolated fake-QEMU fixtures for the local link, config preservation, conflicts,
collisions, no-write status, first-NIC preservation and setup exchange withholding. Scaffold
fixtures will check paths/indexes, launcher syntax, refresh/clean and absence of pack or application
outputs. They will not require proprietary tools, installed guest databases or a live Delphi demo.

Existing guest-workspace disk rows cover LAN settings in those config files. Retained results under
assets and generated scaffold content will be measured once; there is no v101 application ISO to
count. Update README, the checklist, demo footprint, Crostini notes, guest-network procedure,
generated STEPS and the four CHANGELOG sections during implementation. All four versions/flags
remain synchronized, with no new install flag.

The v101 acceptance checks are static/isolated tests, an owner-run local link and first-NIC check,
safe on/off adoption, scaffold lifecycle/menu checks and the approved clean bundle test. Remote
transport, MTU behavior, DCOM and database swaps use the F0–F6 follow-up scheme below and are not
v101 acceptance gates.

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
  against a newer InterBase server are checked in F4; fall back to each version's own InterBase,
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
  tests in F6. Local ping/domain success alone does not establish remote DCOM.
- **TCG speed:** two guests on software emulation will be slow; F2 measures it.

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
5. Review of `936737b`: the managed link is local-only, remote mode moves to F6, and pack waits
   until application sources exist. The main plan records all other approved choices.

## Follow-up work packages F0–F6 and acceptance gates

F0–F6 are the only application staging scheme. The former prose phases A–F have been removed;
all their prerequisites, transport work and acceptance gates are assigned below. These packages
are a roadmap for a later approved version/stage, not build instructions for v101.
Use a new approved plan and version branch before writing application code. Keep each package
small enough for one reviewable commit and an owner-run result. Proposed source paths below are
inside `advanced-demo`; the follow-up decides whether their growth warrants a separate repository.

| Stage | Approach / proposed files | Verification and stop condition |
|---|---|---|
| F0: lab and media prerequisites | Verify the local foundation, edition help, InterBase/runtime versions and media; write `docs/media-matrix.md` and `docs/prerequisites.md`; take owner-controlled backups/snapshots and apply SP6a | Record exact components, permitted media, workload headroom and DCOM account/settings preparation; stop before code if prerequisites are missing |
| F1: DCOM go/no-go | Write the first small Delphi 7 object/client in `delphi7/probe/`; document per-machine registration and specific account permissions | Prove local activation/call, then NT client ↔ 2000 server; resolve identity/runtime/permissions before database work |
| F2: Delphi 7 vertical slice | `delphi7/server/`, `delphi7/client/`, SQL Server adapter, agreed GetCustomers/GetBackendInfo contract | Known rows locally and on other OS, clear backend ID, bounded failure on server loss; if remote DCOM fails investigate then decide socket fallback |
| F3: Delphi 7 database swap | InterBase adapter, dialect-specific `seed/` scripts and same client contract | Same rows/order/fields from both databases, backend identity changes; stop if runtime/data contract differs |
| F4: back-port 6 → 5 → 4 → 3 | Per-version project/adapter/runtime docs; share proven presentation/contract only | Each compiles with its own compiler, runs client on other OS and swaps agreed databases; record each transport/version explicitly |
| F5: optional bridges and packaging | Add verified sockets/HTTP/SOAP/OLEnterprise projects and a high-host-port hostfwd design; design source/application CD packaging now that sources exist | Measure Wine/win95/Lazarus routes independently, validate CD allowlists and preserve owner edits; label unsupported routes explicitly |
| F6: cross-laptop transport and application | Design the remote link over Tailscale, including MTU, endpoint binds and unique identities; reuse the proven application and update docs/results | Pass size-sensitive transport tests before domain/DCOM calls and database swaps; distinguish credentials/DNS/port/MTU failures and avoid hidden topology expansion |

F0 includes the preparation previously described as foundation work. System-disk snapshots do
not back up guest configs or exchange data, so keep those with the owner's recoverable backup.
Confirm the installed DCOM settings before use: Enable DCOM, proposed Connect/Identify and access/
launch permission for the intended domain accounts. Do not disable authentication broadly or
rewrite domain permissions from Linux. Only F1 writes the trivial object; v101 supplies no object.

F2 uses Delphi 7 with SQL Server 2000 locally before the NT client calls it. It measures performance
with the intended workload. If DCOM fails, stop for bounded diagnosis and an owner choice about
socket fallback. F3 proves the same client contract and ordered customer data against InterBase
before F4 back-ports the agreed adapters newest to oldest: Delphi 6, 5, 4, then 3. Record actual
compiler/runtime compatibility and the two guest roles per version rather than assume transport
ABI compatibility between releases.

F5 verifies each transport against matching help/media. Wine and win95 can use the Socket Server;
Delphi 6/7 SOAP can serve Lazarus/Linux; OLEnterprise remains a period alternative for Delphi 3/4
and uses the normal DOSBox-X core. A hostfwd design must use a high host TCP port instead of
requiring root to bind a low service port. Wine reaches host loopback, win95 uses its host alias
and later cross-laptop clients use the host Tailscale address. Source packaging is deliberately
absent from v101 and is planned here only after the source tree is real.

F6 must finish transport design before advertising remote support. Use a single server/client
pair at a time with specific local Tailscale binds, reciprocal endpoints and unique MAC/guest IPs.
Two guests on each laptop simultaneously require a separate hub/switch topology. Prove domain
identity and dynamic DCOM endpoints separately from ping, and show the same database swap only
after the one-laptop application passes.

**F6 MTU risk:** [Tailscale documents a 1280-byte MTU](https://tailscale.com/docs/reference/troubleshooting/network-configuration/tcp-connection-two-devices).
An ordinary Ethernet frame carrying a 1500-byte guest IP packet, plus outer UDP/IP headers, can
exceed that path MTU. This is a risk inferred from the encapsulation sizes, not a measured failure
of this lab. A small ping may pass while larger transfers fragment, fail or stall. F6 must test a
range of payload sizes and sustained bidirectional transfers before domain/DCOM acceptance, and
inspect fragmentation/PMTU behavior on the actual path. It must then choose and document a proven
mitigation, such as an appropriate guest MTU or a different transport, with the owner controlling
any legacy driver/registry changes and recovery. Do not assume TCP MSS adjustment fixes every
encapsulated Ethernet frame. No remote UDP feature or host-wide MTU workaround is built in v101.

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
