# dev-setup-chromebook v96 plan

Oct 26, 2026 · item 1 chosen Oct 26 · item 2 added Oct 26, back end, flag and rendering chosen Oct 26

## Scope

v96 follows v95. Base: v95, built on `release/v95` (PR #4), being released now. Anything v95's release
run turns up and doesn't go into v95 itself can join this plan.

1. **Thread support for Free Pascal programs:** setup defines `UseCThreads` for every compile, in
   `~/.fpc.cfg` (found Oct 26 2026 with a Lazarus example).
2. **Headless Drupal + Astro demo:** a new dev-demo, `drupal/drupal-astro`, that builds Umami's recipes
   into a static Astro site from core's JSON:API, next to `drupal/drupal-nuxt` for a "one Drupal, two
   front ends" comparison. Nothing is installed for Astro itself.

Item 1 changes scripts, so the bundle goes to v96: all four scripts bumped, CHANGELOG entries under all
four sections ("version bump only" where nothing changed). Item 2 changes dev-demo only.

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

## 2. Headless Drupal + Astro demo (dev-demo, `drupal/drupal-astro`)

**Asked Oct 26 2026:** whether Astro belongs in the bundle. Astro is not a CMS: it is a JavaScript
framework for content sites (static by default, no JavaScript shipped unless a component asks for it),
with no admin UI or content store of its own. Its content comes from Markdown or from a CMS, and headless
Drupal is a common source. Cloudflare acquired the company in January 2026; the framework stays MIT
and open source. Astro 7 is the current major (June 2026).

**Setup, test, init: nothing.** Astro follows the bundle's rule that frameworks stay per-project: it has
no global CLI (`npm create astro@latest` scaffolds a project, which pins its own version), and Node,
Composer and wrangler are already there. So Astro gets a demo, not a flag.

**The demo** mirrors `drupal/drupal-nuxt` (v91) so the two read side by side: the same Umami recipes
from the same JSON:API, rendered two ways. Astro's pages are static, with one live part (a server
island) to show that Astro mixes the two per component.

| | drupal-nuxt (v91) | drupal-astro (v96) |
| --- | --- | --- |
| Rendering | On the server, per request (Nuxt 4 SSR) | Ahead of time: `astro build` writes one HTML file per recipe; one server island on each page renders per request |
| Drupal needed | While the site runs | While it builds; at run time only for the island (the rest of the page works without it) |
| Change a recipe in Drupal | Shows on the next page load | In the island on the next page load; in the page itself after the next build |
| JavaScript in the browser | Nuxt's runtime (hydration) | Only Astro's small inline script that fetches the island |
| Ports | Nuxt dev :3020, production :3021 | Astro dev :4321, the built site's Node server :4322 |

**What it generates** (in `~/dev-demo/drupal/drupal-astro`):

- `astro/` with `package.json` (`astro` `^7`, `@astrojs/node` in standalone mode, no UI framework),
  `astro.config.mjs`, and a content
  collection whose loader reads `node/recipe` from JSON:API at build time (following `links.next`, only
  the fields it shows) and validates them with `astro/zod`. Drupal's address is config, overridable
  with `DRUPAL_URL`.
- `src/pages/index.astro` (the recipe list) and `src/pages/recipes/[slug].astro` (one static page per
  recipe from `getStaticPaths`), with the same titles and difficulty labels as the Nuxt version.
- `src/components/LatestFromDrupal.astro`, used with `server:defer` on every page: the most recently
  changed recipe and when it changed, read live from JSON:API (`sort=-changed`, one item). Its
  `fallback` slot says what it is waiting for, and stays in place when Drupal or the server is not
  there.
- Images go through Astro's `<Image>` with Drupal's host in `image.domains`, so the build downloads and
  resizes them into `dist/`. The built site then stands alone: no links back to `127.0.0.1:8891`.
- A launcher (`run`), checking `demo_need php`, `composer install-web` and `npm install-node` the way
  drupal-nuxt's does.

**Launcher items:**

- `serve`: start Drupal (installing Umami the first time) and Astro's dev server on :4321.
- `build`: `astro build` (static pages in `dist/client`, the island's server in `dist/server`), then
  that server on :4322.
- `api`: one raw JSON:API request, the data the loader turns into pages (same as drupal-nuxt's).
- `source`: show the recipe titles in the files under `dist/client`, then stop Drupal and show the
  pages are still served, with the island showing its fallback: what is static and what is live.
- `compare`: open Nuxt (:3020) and Astro (:4321) together; edit a recipe title in Drupal and reload:
  Nuxt and Astro's island show the new title, Astro's page heading only after `build`. Only when
  drupal-nuxt is installed.
- `drupal`: open Drupal (admin / admin).
- `deploy`: with wrangler (install-cloudflare), deploy `dist/` as static assets on Cloudflare after
  asking, with `CLOUDFLARE_API_TOKEN` or `wrangler login`, as the cloudflare demo's `deploy` does.
  Drupal stays on the Chromebook; only `dist/client` goes up, so the deployed pages show the island's
  fallback (the launcher says so before deploying).
- `stop` and `reset`, as in drupal-nuxt.

| Choice: where the Drupal back end comes from | |
| --- | --- |
| **A (chosen)** | One shared site. Umami moves to `drupal/umami-headless` (PHP's built-in server + SQLite, :8891) with a small launcher of its own (`up`, `stop`, `reset`), and both drupal-nuxt and drupal-astro use it. An existing `drupal-nuxt/drupal` is moved there on the first run, not reinstalled. The comparison is on literally the same content, and the second copy's \~250 MB isn't spent. drupal-nuxt's launcher changes to call it. |
| B | Its own site: drupal-astro installs a second Umami on :8892. Self-contained, drupal-nuxt untouched, but \~250 MB more and the two sites' content can drift, so `compare` edits one site only. |

| Choice: which flag brings the demo | |
| --- | --- |
| **A (chosen)** | `install-web` (Composer, Drupal's PHP extensions; in install-all), next to the `demo_web` and `demo_drupal` demos. Astro has nothing to do with Vue. |
| B | `install-vue`, next to drupal-nuxt, so the pair always arrive together. |

| Choice: rendering modes shown | |
| --- | --- |
| A | Static only, Astro's default, which is what sets it apart from Nuxt here. |
| B | Static plus one page rendered on demand (the `@astrojs/node` adapter and a live content collection), to show Astro can do both. Adds an adapter and a server process. |
| **C (chosen)** | Static pages plus one **server island** (`server:defer`, same `@astrojs/node` adapter): the recipe pages stay static, and one small part of them ("latest from Drupal", read live) renders on the server when the page loads. Shows Astro's own per-component mix, which drupal-nuxt can't. |

Under C (as it would under B): `build` produces a static part (`dist/client`) and a Node server (`dist/server`), and `build` runs that server on :4322 instead of `astro preview`. `deploy` ships only the static part, since the live part would need Drupal reachable from Cloudflare; the deployed site shows the static fallback where the live part would be. The launcher says so.

**Docs:**

- `docs/dev-demo.md`: a paragraph for `drupal/drupal-astro` after drupal-nuxt's (static pages, the
  server island, and why the deployed copy shows the fallback), the footprint rows
  (generated sources under 1 MB; `node_modules` on first serve, measured during the build), and, under
  choice A, `drupal/umami-headless` replacing drupal-nuxt's own Drupal row.
- README's demo list. CHANGELOG, dev-demo section.

**To verify on the Chromebook:** `dev-demo-chromebook.sh install-web` (with install-node) creates
`drupal/drupal-astro`; `serve` shows the recipes on :4321; `build` then `source` lists the titles from
`dist/client` and the :4322 server still serves them with Drupal stopped, the island showing its
fallback; with Drupal up, the island shows the latest recipe; images load from `dist/`, not :8891.
Under choice A, a machine that already has drupal-nuxt's site keeps its content after the move, and
drupal-nuxt's `serve` still works. `compare` shows Nuxt and the island picking up an edit that Astro's
page shows only after `build`. `deploy` is a hand check once wrangler is logged in (pages up, island
on its fallback).

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
- [x] Item 2: an Astro + Drupal demo (dev-demo only; no setup flag for Astro)
- [x] Item 2, back end: A (shared `drupal/umami-headless`)
- [x] Item 2, flag: A (`install-web`)
- [x] Item 2, rendering: C (static pages plus a server island, `@astrojs/node`)
- [ ] Anything else for v96
