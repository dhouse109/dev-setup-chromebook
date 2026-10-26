# dev-setup-chromebook v96 plan

Oct 26, 2026 · item 1 chosen Oct 26

## Scope

v96 follows v95. Base: v95, built on `release/v95` (PR #4), being released now. Anything v95's release
run turns up and doesn't go into v95 itself can join this plan.

1. **Thread support for Free Pascal programs:** setup defines `UseCThreads` for every compile, in
   `~/.fpc.cfg` (found Oct 26 2026 with a Lazarus example).

Item 1 changes scripts, so the bundle goes to v96: all four scripts bumped, CHANGELOG entries under all
four sections ("version bump only" where nothing changed).

Each item lists the choices that were offered; the decision is marked. The build starts once "anything
else for v96" is settled.

## 1. Thread support for Free Pascal programs (install-lazarus)

**Found Oct 26 2026:** Lazarus's own `examples/TDaemon`, copied by dev-demo to
`~/dev-demo/lazarus/examples/TDaemon`, built and installed (`sudo ./TestDaemon -i` wrote
`/lib/systemd/system/TestDaemon.service`), but running it failed:

```
$ sudo ./TestDaemon -r
This binary has no thread support compiled in.
Recompile the application with a thread-driver in the program uses clause before other units using thread.
Runtime error 232 at $000000000041A62D
```

The IDE's debugger stopped at the same place: `RunError(232)`, "Threads not supported".

**Why:** on Linux, Free Pascal's RTL has no thread manager until the `cthreads` unit is loaded, and it
has to be the first unit in the program's `uses`. Lazarus's project templates and many of its examples
(TDaemon among them) load it only behind a define nobody sets by default:

```pascal
Uses
{$IFDEF UNIX}{$IFDEF UseCThreads}
  CThreads,
{$ENDIF}{$ENDIF}
  DaemonApp, lazdaemonapp, ...
```

TDaemon's `.lpi` doesn't define `UseCThreads`, so `CThreads` was skipped. `-i` doesn't start a thread, so
it worked; `-r` starts the daemon's worker thread and stops with error 232. This is a Linux and Free
Pascal default, not a Crostini difference: the same project fails the same way on any Linux.

| Choice | Where `UseCThreads` gets defined |
| --- | --- |
| A | Per project: Project Options → Compiler Options → Custom Options → `-dUseCThreads`. The bundle changes nothing; the checklist and the demo explain it. |
| B | Per project, in the source: drop the `{$IFDEF UseCThreads}` guard so `CThreads` is always used. |
| **C (chosen)** | For every compile on the machine: `-dUseCThreads` in `~/.fpc.cfg`, which `fpc`, `lazbuild` and both IDE profiles all read. Every Lazarus example and new project with the guard gets thread support with no per-project change. |

**Setup** (under `install-lazarus`, after the debs are installed and before the Qt5 IDE builds):

- **Which file fpc reads.** On Linux fpc uses the *first* config file it finds: `./fpc.cfg`, then
  `~/.fpc.cfg`, then `<fpc's dir>/../etc/fpc.cfg`, then `/etc/fpc.cfg`. A `~/.fpc.cfg` therefore
  replaces the system file. It has to start with `#INCLUDE <system file>`, or fpc loses the unit paths
  the system file sets and nothing compiles.
- **The system file** is found, not assumed: the first that exists of `$(dirname $(readlink -f $(command -v fpc)))/../etc/fpc.cfg`
  and `/etc/fpc.cfg` (the SourceForge `fpc-laz` deb writes `/etc/fpc.cfg`). None found: a NOTICE, and
  `~/.fpc.cfg` is not written.
- **No `~/.fpc.cfg` yet:** setup creates it with the `#INCLUDE` line, then a marked block:
  ```
  #INCLUDE /etc/fpc.cfg
  # >>> dev-setup lazarus >>>
  # v96: thread support for programs whose uses clause has {$IFDEF UseCThreads} CThreads (Lazarus's
  # templates and examples). Without it they stop with runtime error 232 when they start a thread.
  -dUseCThreads
  # <<< dev-setup lazarus <<<
  ```
- **`~/.fpc.cfg` already there** (yours, from Oct 26): `-dUseCThreads` anywhere in it is left alone
  and reported as already set; otherwise the block is appended. A file that neither `#INCLUDE`s a
  system config nor has its own `-Fu` lines can't compile anything, so it gets a NOTICE naming the
  missing line, and setup doesn't change it.
- **Rewritten in place** on every run (like the `~/.bashrc` blocks), never duplicated.
- **The IDE builds are unaffected:** the Lazarus IDE already uses `cthreads` (its own guard is
  `DisableCThreads`), so `lazmode`'s builds and the IDE's own rebuilds come out the same.

| Choice: a way to turn it off | |
| --- | --- |
| **A (recommended)** | None. A define that only switches `CThreads` on in programs that ask for it costs nothing. Deleting the block by hand lasts until the next setup run. |
| B | `FPC_USE_CTHREADS=0` in secrets.env: setup removes the block instead of writing it. |

**Test** (Lazarus section, next to "fpc compiles and runs a program"):

- `~/.fpc.cfg` defines `UseCThreads`, and includes the system config or has its own unit paths (check).
- A program with the TDaemon-style guard that starts and waits for a `TThread` compiles and prints
  from the thread (check: this is the Oct 26 failure; FAIL means error 232 is back).
- The existing hello-world check also proves that `~/.fpc.cfg` didn't cut fpc off from its units.

**Init:** version bump only (nothing to log in to).

**Demo** (`lazarus examples`):

| Choice | What changes |
| --- | --- |
| **A (recommended)** | A note in the launcher's output and in `docs/dev-demo.md` for TDaemon: it needs `sudo` for `-i` and `-u`, `-i` writes a systemd unit that runs the binary from its build folder (so rebuild before `systemctl start`), how to watch its daily log, and how to remove it (`systemctl stop`, then `sudo ./TestDaemon -u`). |
| B | No demo change. |

**Docs:**

- `docs/init-checklist.md`, Lazarus section: what `~/.fpc.cfg` does, and that a project built before
  v96 needs **Run → Clean up and Build** once.
- `docs/crostini-gotchas.md`: one line under Lazarus: not Crostini-specific, but where it bit.
- CHANGELOG (all four sections).

**To verify on the Chromebook:** on the machine set up by hand on Oct 26, setup reports
`UseCThreads` as already set and leaves `~/.fpc.cfg` as it is. On a clean machine, `~/.fpc.cfg` is
created with the right `#INCLUDE`. TDaemon (Clean up and Build), `sudo ./TestDaemon -i`,
`sudo systemctl daemon-reload`, `sudo systemctl start TestDaemon`: the log shows "Daemon received
start signal". `lazmode rebuild` still works with the new file in place.

## Carried forward

**From v95** (its own on-hardware checks, in the v95 plan): `lazmode`'s install-list handling and
adoption of the IDE's own build (item 4), and herdr in ChromeOS's Terminal (item 5). Fixes they need
go into v95 if you keep them there, otherwise here.

**From the v93 plan, on-hardware checks still open:**

- [ ] Windows 95 reads a 1 GB exchange disk in DOSBox-X (255 heads since v93's review)
- [ ] win95 sees the app CD as F: with the Windows CD as E:
- [ ] Delphi 7 installs and starts under Wine (`delphi 7 setup`); the integrated debugger stops at a
      breakpoint
- [ ] the same for Delphi 6, 4 and 3, in that order, as the discs are tried
- [ ] Delphi 3 or 4 in win95: debugger on the dynamic core, or only `--core normal`?
- [ ] BDE in each native guest: any "insufficient disk space" error on the larger disks?

**Open question:** why dragonair → eldrid goes through a DERP relay instead of connecting directly.
`tailscale netcheck` on both laptops is the first step.

**Not built here:** the Windows (WSL) bundle, in its own repo, `dev-setup-windows`.

## Choices to make

- [x] Item 1: C (`-dUseCThreads` in `~/.fpc.cfg`, written by setup under install-lazarus)
- [ ] Item 1, off switch: A (none) or B (`FPC_USE_CTHREADS=0`)
- [ ] Item 1, demo: A (TDaemon note) or B (no change)
- [ ] Anything else for v96
