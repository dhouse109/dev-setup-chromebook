# Delphi multi-tier demo across Delphi 3–7: plan

Nov 8, 2026 · **draft for owner review** · companion to `docs/plans/v101-plan.md` item 9

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

## What each Delphi version brings

| Delphi | Year | Multi-tier framework | Client connections | Database access |
|---|---|---|---|---|
| 3 C/S | 1997 | MIDAS 1: Remote Data Module, provider, `TClientDataSet` | DCOM; OLEnterprise | BDE + SQL Links |
| 4 C/S | 1998 | MIDAS 2 | DCOM; **sockets** (`scktsrvr`); OLEnterprise; CORBA | BDE + SQL Links |
| 5 Ent | 1999 | MIDAS 3 (stateless providers, `TWebConnection`) | DCOM; sockets; **HTTP** (`httpsrvr.dll`) | BDE; **ADO** (ADOExpress) |
| 6 Ent | 2001 | DataSnap | DCOM; sockets; HTTP; **SOAP** | **dbExpress**; ADO; BDE |
| 7 Ent | 2002 | DataSnap | DCOM; sockets; HTTP; SOAP | dbExpress; ADO (dbGo); BDE |

The framework names and the year each connection type arrived are from memory of the products;
each one is confirmed against that version's own help and demos during the build.

## Era-specific databases and the swap

Databases from the owner's media, plus the InterBase shipped on the Delphi CDs:

| Delphi | Server guest | Primary database | Swap to | Access (primary / swap) |
|---|---|---|---|---|
| 3 | NT 4.0 | SQL Server 6.5 | InterBase (from the Delphi 3 C/S CD) | BDE SQL Links MSSQL / InterBase |
| 4 | NT 4.0 | Oracle 8.0.5 | SQL Server 6.5 | BDE SQL Links Oracle / MSSQL |
| 5 | Windows 2000 | Oracle 8i | SQL Server 2000 | ADO (or BDE) / ADO |
| 6 | Windows 2000 | SQL Server 2000 | Oracle 8i | dbExpress / dbExpress |
| 7 | Windows 2000 | SQL Server 2000 (Northwind) | Oracle 8i (or InterBase) | dbGo ADO or dbExpress / dbExpress |

- **Era logic:** NT 4.0 hosts the 1996–98 databases, Windows 2000 the 1999–2002 ones. Each Delphi
  version's server runs where its databases are; its client runs on the other OS.
- **How the swap is shown:** the server registers one server object per database (for example
  `CustomerSrv.SQLServer` and `CustomerSrv.Oracle`, or one object with a `Backend` setting). The
  client picks the server object from a list. Its code, form and data handling stay the same, and
  `GetBackendInfo` displays which database answered. That makes "the client doesn't know or care"
  visible.
- **Same data everywhere:** one `CUSTOMERS` table (ID, company, contact, city, country; seeded from
  Northwind's Customers) is created in every database by a per-dialect seed script, so every swap
  returns the same rows.
- **Not available:** SQL Server 7.0 (Delphi 5's exact era) isn't in the owner's media; SQL Server
  2000 stands in.

## Topology on one laptop

```
 winnt40 guest (NT 4.0, DC "HADAMIN")         win2000 guest (Windows 2000, joined)
 192.168.50.10                                 192.168.50.20
 SQL Server 6.5, Oracle 8.0.5                  SQL Server 2000, Oracle 8i
 Delphi 3/4 servers  <-- DCOM / sockets -->    Delphi 3/4 clients
 Delphi 5/6/7 clients <-- DCOM / sockets -->   Delphi 5/6/7 servers
            \___ point-to-point UDP socket link (second PCnet NIC) ___/
```

- **Domain accounts** (HADAMIN) make DCOM security much simpler than matching local accounts: the
  client's user is known to the server machine.
- **Memory:** NT 4.0 at 256 MB (SQL Server 6.5 + Oracle 8.0.5), Windows 2000 at 768 MB (SQL Server
  2000 + Oracle 8i). About 1 GB of the Chromebook's ~6.4 GB, but run one database per guest at a
  time where possible. Both guests on TCG use two CPU cores.
- **IDEs:** Delphi 3 and 4 installed in NT 4.0, Delphi 5–7 in Windows 2000 (their eras; Borland's
  debugger works there). Wine builds (`delphi N`) stay optional.
- **Deploying a client to the other guest:** the client `.exe`, `midas.dll` (Delphi 3/4: `dbclient.dll`)
  registered with `regsvr32`, and the server's registration on the client machine (the type library
  or the registry entries the server's `/regserver` writes, with `RemoteServerName` set to the server's
  address). No database software on the client side.

## Phases

**A. Foundation (one laptop, no Delphi code yet)**
- Guest network (done by hand on Nov 8; v101 item 9 makes it a supported command), snapshots of both
  guests, memory raised as above.
- DCOM baseline in both guests: `dcomcnfg` with Default Properties > Enable DCOM, Connect /
  Identify, and access/launch permissions for HADAMIN accounts. Test with a trivial out-of-process
  server first.

**B. Vertical slice (go/no-go): Delphi 7 + SQL Server 2000**
- SQL Server 2000 (Mixed Mode, Northwind) and Delphi 7 in Windows 2000.
- Server and client both in Windows 2000 first; then the client on NT 4.0 over DCOM. If DCOM fails
  here, the plan falls back to sockets (`scktsrvr`) before going further.

**C. The swap in Delphi 7:** Oracle 8i in Windows 2000, the second server object, the client
choosing between them. Then InterBase as an optional third.

**D. Back-porting, newest to oldest:** Delphi 6 (dbExpress), 5 (ADO; first HTTP option), 4 (NT 4.0
server, Oracle 8.0.5 / SQL Server 6.5, sockets as well as DCOM), 3 (NT 4.0 server, SQL Server 6.5 /
InterBase, DCOM only). The client of each version runs on the other OS.

**E. Bridges:** Socket Server for clients that can't do DCOM: win95 (DOSBox-X) and Wine reach a
guest's socket server through QEMU port forwarding on its user-mode NIC
(`hostfwd=tcp::211-:211`, Socket Server's default port), via `10.0.2.2:211` or `127.0.0.1:211`. SOAP
(Delphi 6/7) for a Lazarus client on Linux. OLEnterprise (Delphi 3/4) as a period alternative for
win95 (it needs DOSBox-X's normal core).

**F. Two laptops: joxer (servers) and yaviks (clients)**
- yaviks needs install-retro and its own NT 4.0 / Windows 2000 guests (owner's media).
- The guest network's UDP link spans the laptops over Tailscale: joxer's server guest sends to
  yaviks' Tailscale address and listens on all interfaces (`udp=<yaviks>:10001,localaddr=0.0.0.0:10002`),
  and the reverse on yaviks. The 192.168.50.x network, the domain and DCOM then work unchanged.
  Socket and HTTP clients can instead use Tailscale TCP plus QEMU port forwarding.
- Show each Delphi version's client on yaviks against its server on joxer, with the database swap.

## Risks and checks to do early

- **Oracle 8i's Java installer** fails on newer CPUs (the old JIT); the guests' Pentium-class CPU
  model may avoid it, otherwise a known workaround exists. Check before planning around 8i.
- **NT 4.0 service pack:** SQL Server 2000 clients, Delphi 5–7 programs and later MDAC need NT 4.0
  SP6a; SQL Server 6.5 is happiest with its own SP. Confirm what the owner has.
- **BDE SQL Links with Oracle 8:** as far as known, Delphi 3's BDE predates Oracle 8's client
  (Oracle 8 support arrived with Delphi 4's BDE); hence Oracle is Delphi 4's database, not Delphi 3's.
  Confirm against Delphi 3's SQL Links driver list.
- **DCOM through Tailscale:** DCOM hands out dynamic ports; within the bridged 192.168.50.x network
  that's fine, but it's the first thing to check in phase F.
- **TCG speed:** two databases and two IDEs on software emulation will be slow; phase B measures it.

## Where the demo's code lives (owner decision)

The Delphi projects and SQL seed scripts are new, publishable source. Options:
- **A:** a dev-demo item in this bundle (`dev-demo/retro/dcom`), which installs the sources and
  scripts into `~/dev-demo` for the guests;
- **B:** a separate repository (for example a "Delphi multi-tier lab"), as a portfolio piece for the
  legacy-migration practice, with this bundle only providing the guests, network and tools.

## Owner inputs still needed

1. Where the code lives (A or B above).
2. NT 4.0 service packs available (SP6a?), and Windows 2000's service pack level.
3. What is in the Oracle `9` folder, if anything (Oracle 9i would be Delphi 7's exact era).
4. Agree the version-to-database mapping above, or adjust it.
