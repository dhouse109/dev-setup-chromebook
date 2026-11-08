# Delphi multi-tier demo across Delphi 3–7: plan

Nov 8, 2026 · **scope agreed; detailed build plan next** · companion to `docs/plans/v101-plan.md` item 9

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

**Scope (owner decision, Nov 8):** v101 uses **InterBase and SQL Server only**, to keep the unknowns
down. Oracle (8.0.5 and 8i media on hand) is a later step; see "Later: Oracle" at the end.

## What each Delphi version brings

| Delphi | Year | Multi-tier framework | Client connections | Database access |
|---|---|---|---|---|
| 3 C/S | 1997 | MIDAS 1: Remote Data Module, provider, `TClientDataSet` | DCOM; OLEnterprise | BDE + SQL Links |
| 4 C/S | 1998 | MIDAS 2 | DCOM; **sockets** (`scktsrvr`); OLEnterprise; CORBA | BDE + SQL Links |
| 5 Ent | 1999 | MIDAS 3 (stateless providers, `TWebConnection`) | DCOM; sockets; **HTTP** (`httpsrvr.dll`) | BDE; **ADO** (ADOExpress); **IBX** |
| 6 Ent | 2001 | DataSnap | DCOM; sockets; HTTP; **SOAP** | **dbExpress**; ADO; IBX; BDE |
| 7 Ent | 2002 | DataSnap | DCOM; sockets; HTTP; SOAP | dbExpress (adds an MSSQL driver); ADO (dbGo); IBX; BDE |

The framework names, the year each connection type arrived and which database drivers each edition
includes are from memory of the products; each one is confirmed against that version's own help and
demos during the build.

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
- **Memory:** NT 4.0 at 128–256 MB (128 MB today) (SQL Server 6.5 + InterBase), Windows 2000 at 512 MB (SQL Server
  2000 + InterBase); both are light next to Oracle. Both guests on TCG use two CPU cores.
- **IDEs:** Delphi 3 and 4 installed in NT 4.0, Delphi 5–7 in Windows 2000 (their eras; Borland's
  debugger works there). Wine builds (`delphi N`) stay optional.
- **Deploying a client to the other guest:** the client `.exe`, the client DLL (`dbclient.dll` for
  Delphi 3/4, `midas.dll` from Delphi 5) registered with `regsvr32`, and the server's registration on
  the client machine (the type library or the registry entries the server's `/regserver` writes, with
  `RemoteServerName` set to the server's address). No database software on the client side.

## Phases

**A. Foundation (one laptop, no Delphi code yet)**
- Guest network (done by hand on Nov 8; v101 item 9 makes it a supported command), snapshots of both
  guests, memory as above.
- DCOM baseline in both guests: `dcomcnfg` with Default Properties > Enable DCOM, Connect /
  Identify, and access/launch permissions for HADAMIN accounts. Test with a trivial out-of-process
  server first.

**B. Vertical slice (go/no-go): Delphi 7 + SQL Server 2000**
- SQL Server 2000 (Mixed Mode, Northwind) and Delphi 7 in Windows 2000.
- Server and client both in Windows 2000 first; then the client on NT 4.0 over DCOM. If DCOM fails
  here, the plan falls back to sockets (`scktsrvr`) before going further.

**C. The swap in Delphi 7:** InterBase from the Delphi 7 CD in Windows 2000, the second server
object, the client choosing between them.

**D. Back-porting, newest to oldest:** Delphi 6 (InterBase over dbExpress first), 5 (ADO and IBX;
first HTTP option), 4 (NT 4.0 server, InterBase / SQL Server 6.5, sockets as well as DCOM), 3 (NT 4.0
server, SQL Server 6.5 / InterBase, DCOM only). The client of each version runs on the other OS.

**E. Bridges:** Socket Server for clients that can't do DCOM: win95 (DOSBox-X) and Wine reach a
guest's socket server through QEMU port forwarding on its user-mode NIC
(`hostfwd=tcp::211-:211`, Socket Server's default port), via `10.0.2.2:211` or `127.0.0.1:211`. SOAP
(Delphi 6/7) for a Lazarus client on Linux. OLEnterprise (Delphi 3/4) as a period alternative for
win95 (it needs DOSBox-X's normal core).

**F. Two laptops: joxer (servers) and yaviks (clients)**
- yaviks needs install-retro and its own NT 4.0 / Windows 2000 guests (owner's media). As clients
  they need no database software.
- The guest network's UDP link spans the laptops over Tailscale: joxer's server guest sends to
  yaviks' Tailscale address and listens on all interfaces (`udp=<yaviks>:10001,localaddr=0.0.0.0:10002`),
  and the reverse on yaviks. The 192.168.50.x network, the domain and DCOM then work unchanged.
  Socket and HTTP clients can instead use Tailscale TCP plus QEMU port forwarding.
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
- **DCOM through Tailscale:** DCOM hands out dynamic ports; within the bridged 192.168.50.x network
  that's fine, but it's the first thing to check in phase F.
- **TCG speed:** two guests on software emulation will be slow; phase B measures it.

## Where the demo's code lives (owner decision, Nov 8)

- **In dev-demo, in a Delphi folder of its own called `advanced-demo`:** proposed path
  `~/dev-demo/retro/delphi/advanced-demo`, next to the existing `retro/matrix`. dev-demo generates
  the sources (Delphi projects per version, the per-dialect seed scripts, a STEPS file) and, with
  install-retro's genisoimage, an app CD so a guest can take them through `<guest> cd`.
- **When it is ready for release** it may move to its own repository, depending on its size.
- **Source design proposal (for the detailed plan):** forms built in code rather than `.dfm` files,
  so one source compiles unchanged in Delphi 3–7 (text `.dfm` is the default only from Delphi 5);
  version differences behind `{$IFDEF VER100}`…`{$IFDEF VER150}` where a feature (sockets, IBX,
  dbExpress, SOAP) doesn't exist in older versions.

## Owner decisions recorded (Nov 8)

1. Code location: dev-demo, `advanced-demo` (above).
2. Service packs: available; winnt40 gets SP6a first (above).
3. The version-to-database mapping above is agreed.

## Later: Oracle (not in v101)

Owner has Oracle 8.0.5 for NT and Oracle 8i media (and a `9` folder, contents unknown). When added:
Oracle 8.0.5 on NT 4.0 as Delphi 4's era database (BDE SQL Links Oracle), Oracle 8i on Windows 2000
for Delphi 5–7 (ADO/dbExpress), as a third swap target behind the same client. Known risks to check
then: Oracle 8i's Java installer failing on newer CPUs (the guests' Pentium-class CPU model may
avoid it), Oracle's memory needs (Windows 2000 at 768 MB+), and Net8 client configuration on each
application server. Whether Delphi 3's SQL Links support Oracle 8 is to be checked.
