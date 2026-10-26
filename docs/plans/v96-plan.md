# dev-setup-chromebook v96 plan

Oct 26, 2026 · item 1 chosen Oct 26 (all choices) · item 2 added Oct 26, back end, flag and rendering chosen Oct 26 · item 3 added and chosen Oct 26

## Scope

v96 follows v95. Base: v95 (`release/v95`, merged into `main` as PR #4). Anything v95's release
run turns up and doesn't go into v95 itself can join this plan.

1. **Thread support for Free Pascal programs:** setup defines `UseCThreads` for every compile, in
   `~/.fpc.cfg` (found Oct 26 2026 with a Lazarus example).
2. **Headless Drupal + Astro demo:** a new dev-demo, `drupal/drupal-astro`, that builds Umami's recipes
   into a static Astro site from core's JSON:API, next to `drupal/drupal-nuxt` for a "one Drupal, two
   front ends" comparison. Nothing is installed for Astro itself.
3. **Devin Desktop (formerly Windsurf) under X11, and CodeLLDB:** install-windsurf starts Devin Desktop
   with `--ozone-platform=x11` from its own launcher entry and a terminal wrapper (it froze or closed
   on Wayland, Oct 26 2026), and installs CodeLLDB's Linux add-on, which can't install itself there.

Items 1 and 3 change scripts, so the bundle goes to v96: all four scripts bumped, CHANGELOG entries under all
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
| **A (chosen)** | None. A define that only switches `CThreads` on in programs that ask for it costs nothing. Deleting the block by hand lasts until the next setup run. |
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
| **A (chosen)** | A note in the launcher's output and in `docs/dev-demo.md` for TDaemon: it needs `sudo` for `-i` and `-u`, `-i` writes a systemd unit that runs the binary from its build folder (so rebuild before `systemctl start`), how to watch its daily log, and how to remove it (`systemctl stop`, then `sudo ./TestDaemon -u`). |
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

## 3. Devin Desktop (formerly Windsurf) under X11, and CodeLLDB (install-windsurf)

**Found Oct 26 2026** (installed Oct 24, worked at first, then wouldn't sign in or stay open). Windsurf is
now **Devin Desktop** (1.126.0): the apt package is `devin-desktop`, and `windsurf` is a transitional
package that pulls it in. Its window either froze ("The window is not responding") or vanished ("The
window terminated unexpectedly (reason: 'clean-exit', code: '0')"), about 30 s after launch or when
**Login** was clicked. What the logs ruled out and what fixed it:

- Not the extensions: `devin-desktop --disable-extensions --verbose` froze the same way.
- Not the shell: the launcher-started run logged "Unable to resolve your shell environment in a
  reasonable time", but a terminal-started run skips that step (`resolveShellEnv(): skipped`) and failed
  the same way.
- Not the keyring: the stored `windsurf_auth.sessions` secret was found and decrypted.
- **The Wayland path.** Electron ran on ChromeOS's Wayland (`ozone/platform/wayland`). Right after
  `devin.login`, the log went silent for 62 s, a child process died, then `Fatal Wayland communication
  error: Broken pipe` and `FATAL ... Failed to shutdown`.
- **Fix:** `devin-desktop --ozone-platform=x11` (XWayland). Sign-in through ChromeOS's browser then
  worked, all extensions loaded, and it stayed up. No `--disable-gpu` needed.
- **The launcher ignored an edited copy.** A copy of `devin-desktop.desktop` in
  `~/.local/share/applications` with the flag added was **not** used by the ChromeOS launcher, even after
  shutting Linux down: the icon still started it on Wayland and it crashed. A **separately named** entry
  (`devin-desktop-x11.desktop`, "Devin (X11)") worked. Same family as Android Studio's Wayland dimming
  (v70).

**CodeLLDB** (`vadimcn.vscode-lldb`, imported from VS Code): Open VSX serves the universal package,
which downloads its Linux add-on on first start through `workbench.extensions.command.installFromVSIX`.
Devin Desktop doesn't have that command: "Platform package installation failed ... command not found".
Installing the platform `.vsix` with `devin-desktop --install-extension` fixed it.

**Setup** (under `install-windsurf`; the flag keeps its name, chosen Oct 26):

- **Package:** install `devin-desktop` directly from the same apt source (fall back to `windsurf` if the
  source doesn't offer it yet). The existing `windsurf.list` and key stay.
- **Launcher entry "Devin (X11)"** (chosen: A): generated from the installed
  `/usr/share/applications/devin-desktop.desktop` at every run (not a frozen copy, so vendor changes to
  `Exec`, `Icon`, `StartupWMClass` or `MimeType` carry over): `Name=` gets " (X11)" and every `Exec=`
  gets `--ozone-platform=x11` after the program path. Written to
  `~/.local/share/applications/devin-desktop-x11.desktop`.
- **Stock entry hidden** (chosen: A): `~/.local/share/applications/devin-desktop.desktop` is the stock
  file plus `NoDisplay=true`, also regenerated each run. If the launcher ignores that as it ignored the
  `Exec` change, the stock icon simply stays; the hand check below tells.
- **URL handler:** `devin-desktop-url-handler.desktop` copied the same way with the flag. Inside Linux,
  `xdg-open` follows the user-directory override, so a `devin://` link starts it on X11 too.
- **Terminal wrapper** (chosen: A): `~/.local/bin/devin-desktop` (and `~/.local/bin/windsurf` when
  `/usr/bin/windsurf` exists) runs the system `/usr/bin/devin-desktop --ozone-platform=x11 "$@"`, by
  absolute path so it can't call itself. `~/.local/bin` is ahead of `/usr/bin` on PATH. CLI-only
  calls (`--install-extension`, `--list-extensions`, `--version`) ignore the flag.
- **CodeLLDB** (chosen: always, under install-windsurf): the latest `codelldb-linux-x64.vsix` (tag from
  the `releases/latest` redirect, not the API; GitHub publishes no checksum for it, so it is validated
  with `unzip -t` before installing) goes in with `devin-desktop --install-extension`, so it's in place
  before onboarding imports VS Code's extensions. Skipped when that version or newer is already
  installed. Download in `$ASSETS/downloads`, removed after.
- **Idempotent:** each run regenerates the three entries and the wrapper; a hand-made
  `devin-desktop-x11.desktop` (the Oct 26 one) is replaced by the generated one, which differs only in
  following the installed stock file.

**Test** (Windsurf section, renamed "Devin Desktop / Windsurf (install-windsurf)"):

- `devin-desktop --version` (check), via the wrapper.
- Apt source present (check, as now).
- `devin-desktop-x11.desktop`: every `Exec=` has `--ozone-platform=x11`, its program is the stock
  entry's program, and it has no `NoDisplay` (check).
- Stock entry overridden with `NoDisplay=true` (warn: cosmetic).
- `command -v devin-desktop` is the wrapper, and the wrapper passes the flag (check).
- CodeLLDB's platform add-on is in Devin's extensions folder: the native adapter present and executable
  (check; the build confirms the exact path from the `.vsix`).
- Disk report: measure `devin-desktop` (the transitional `windsurf` package is a few KB).

No GUI launch in the test; that's the hand check.

**Init:** version bump only. Sign-in is a browser step.

**Docs:**

- `docs/crostini-gotchas.md`, Graphics: "Devin Desktop (Windsurf) freezes or closes under Wayland", and
  that the ChromeOS launcher ignores an override with the same file name, so the fix is a separate entry.
- `docs/init-checklist.md`: the editors line: open **Devin (X11)**; click Login once and give it 20–30 s
  (each extra click opens another browser tab); finishing sign-in in ChromeOS's browser returns to the
  app. Machines set up before v96: rerun setup with install-windsurf, then shut Linux down once so the
  launcher picks up the new entry.
- README: the gotchas list gets a Devin line next to Android Studio's; flag table text "Windsurf (now
  Devin Desktop)".
- CHANGELOG (all four sections).

**To verify on the Chromebook:** on the machine fixed by hand on Oct 26, setup replaces the hand-made
entry and the wrapper without breaking either; after a Linux restart the launcher shows **Devin (X11)**
(and, if `NoDisplay` is honoured, not the stock icon); opened from it, `pgrep -af devin-desktop` shows
`--ozone-platform=x11`; it stays up past 60 s, and Login completes. `devin-desktop` from a terminal also
gets the flag. A CodeLLDB debug session (Rust or C) stops at a breakpoint with no platform-package
error. On a clean machine: install-windsurf, then onboarding's VS Code import doesn't replace the
platform CodeLLDB with the universal one.

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
- [x] Item 1, off switch: A (none)
- [x] Item 1, demo: A (TDaemon note in the launcher and `docs/dev-demo.md`)
- [x] Item 2: an Astro + Drupal demo (dev-demo only; no setup flag for Astro)
- [x] Item 2, back end: A (shared `drupal/umami-headless`)
- [x] Item 2, flag: A (`install-web`)
- [x] Item 2, rendering: C (static pages plus a server island, `@astrojs/node`)
- [x] Item 3: Devin Desktop under X11 and CodeLLDB, under install-windsurf
- [x] Item 3, launcher: A (a separate "Devin (X11)" entry, stock entry hidden with `NoDisplay`)
- [x] Item 3, terminal: A (`~/.local/bin/devin-desktop` wrapper adds the flag)
- [x] Item 3, CodeLLDB: A (always installed under install-windsurf)
- [x] Item 3, flag name: A (keep `install-windsurf`; it installs `devin-desktop`)
- [ ] Anything else for v96
