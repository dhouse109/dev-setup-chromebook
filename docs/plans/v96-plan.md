# dev-setup-chromebook v96 plan

Oct 26, 2026 · item 1 chosen Oct 26 (all choices) · item 2 added Oct 26, back end, flag and rendering chosen Oct 26 · item 3 added and chosen Oct 26, revised Oct 26 (memory; launcher goes through `/usr/bin/devin-desktop`) · item 4 added and chosen Oct 26, DDEV ports settled Oct 26 · items 6 and 7 added Oct 26 · **plan final Oct 26** · item 5 added and chosen Oct 26 · items 5 and 2 amended Oct 27 after the build (decisions from the v96 PR)

## Scope

v96 follows v95. Base: v95 (`release/v95`, merged into `main` as PR #4). Anything v95's release
run turns up and doesn't go into v95 itself can join this plan.

1. **Thread support for Free Pascal programs:** setup defines `UseCThreads` for every compile, in
   `~/.fpc.cfg` (found Oct 26 2026 with a Lazarus example).
2. **Headless Drupal + Astro demo:** a new dev-demo, `drupal/drupal-astro`, that builds Umami's recipes
   into a static Astro site from core's JSON:API, next to `drupal/drupal-nuxt` for a "one Drupal, two
   front ends" comparison. Nothing is installed for Astro itself.
3. **Devin Desktop (formerly Windsurf) under X11:** install-windsurf starts Devin Desktop with
   `--ozone-platform=x11` from its own launcher entry and a terminal wrapper (it froze or closed on
   Wayland, Oct 26 2026); the later freezes were memory, documented as a Crostini gotcha.
4. **Links from Linux open in ChromeOS's browser:** setup registers ChromeOS's browser as Linux's
   handler for web links, instead of the Linux Google Chrome the base install registers.
5. **Lazarus and Delphi projects in VS Code, Cursor and Devin:** `lazmode vscode` writes a project's build
   (`lazbuild`) and gdb debug setup; `delphi N vscode` writes build (`dcc32` under Wine) and run tasks.
6. **How long a new login shell takes:** dev-test times `bash -i -l` and warns before VS Code-based editors'
   10 s limit, naming the slow lines.
7. **A memory report, `devmem`:** what's using Linux's memory, how much ChromeOS has taken back, and what to
   close.

Items 1, 3, 4, 5, 6 and 7 change scripts, so the bundle goes to v96: all four scripts bumped, CHANGELOG entries under all
four sections ("version bump only" where nothing changed). Item 2 changes dev-demo only.

Each item lists the choices that were offered; the decision is marked. All choices are settled (Oct 26);
the plan is final and the build can start.

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

**Decided Oct 27 2026, after the build** (found while testing umami-headless): with drush 13.8,
`vendor/bin/drush` is a shell script, so `php vendor/bin/drush` only prints it and exits 0, and every drush step
(Umami's install among them) silently did nothing. Every call through `php` in the bundle now uses
`vendor/bin/drush.php`: umami-headless, web/drupal-umami and drupal/drupal-graphql (the only ones; a v96 comment
records the finding at each). The `-x vendor/bin/drush` existence check in drupal-umami stays.

## 3. Devin Desktop (formerly Windsurf) under X11 (install-windsurf)

**Found Oct 26 2026** (installed Oct 24, worked at first, then wouldn't sign in or stay open). Windsurf is
now **Devin Desktop** (1.126.0): the apt package is `devin-desktop`, and `windsurf` is a transitional
package that pulls it in. Its window either froze ("The window is not responding") or vanished ("The
window terminated unexpectedly (reason: 'clean-exit', code: '0')"). Two separate causes:

**Cause 1, the Wayland path** (the sign-in freeze):

- Not the extensions: `devin-desktop --disable-extensions --verbose` froze the same way.
- Not the shell: the launcher-started run logged "Unable to resolve your shell environment in a
  reasonable time", but a terminal-started run skips that step (`resolveShellEnv(): skipped`) and failed
  the same way.
- Not the keyring: the stored `windsurf_auth.sessions` secret was found and decrypted.
- Electron ran on ChromeOS's Wayland (`ozone/platform/wayland`). Right after `devin.login`, the log went
  silent for 62 s, a child process died, then `Fatal Wayland communication error: Broken pipe` and
  `FATAL ... Failed to shutdown`.
- **Fix:** `devin-desktop --ozone-platform=x11` (XWayland). Sign-in then completed and the window stayed
  up. Same family as Android Studio's Wayland dimming (v70).
- **The launcher ignored an edited copy.** A copy of `devin-desktop.desktop` in
  `~/.local/share/applications` with the flag added was **not** used by the ChromeOS launcher, even after
  shutting Linux down: the icon still started it on Wayland and it crashed. A **separately named** entry
  (`devin-desktop-x11.desktop`, "Devin (X11)") worked.
- **The launcher must go through `/usr/bin/devin-desktop`, not the Electron binary.** Later the same day,
  with everything else settled, Devin started from the terminal stayed up (all extensions on, CodeLLDB
  included), while the "Devin (X11)" icon crashed within 5 s every time. The difference: the stock entry
  runs `/usr/share/devin-desktop/devin-desktop` (Electron) directly, with ChromeOS's bare environment, so
  Devin resolves the shell environment itself by running `bash -i -l` at startup (the step that had
  logged "Unable to resolve your shell environment in a reasonable time" that morning). The terminal's
  `devin-desktop` is `/usr/bin/devin-desktop`, the CLI launcher script, which sets `VSCODE_CLI` so that
  step is skipped (`resolveShellEnv(): skipped (VSCODE_CLI is set)`). Pointing the icon's `Exec` at a
  script that runs `/usr/bin/devin-desktop --ozone-platform=x11` fixed it. Icon launches never had the
  shell environment anyway (the resolve had timed out), so nothing is lost.

**Cause 2, memory** (the freezes that came back on X11):

- With X11 in place, the window still froze or closed at random: once ~35 s in, once 11 s in, once
  after a Linux restart. Each time some extension happened to be starting (Gemini Code Assist in two
  runs, CodeLLDB in others), so each looked guilty in turn. They weren't: the extension host's exits all
  read "renderer closed the MessagePort", i.e. it lost the frozen window. Switching groups of extensions
  off gave contradictory results (fewer extensions froze, more didn't); no extensions at all held up.
- Watching the live log, each freeze followed a burst of hundreds of renderer messages from Devin's own
  Devin Cloud Session panel (`devin-webapp-host`, "Rendering was performed in a subtree hidden by
  content-visibility"), and one startup took 66 s to reach Devin's cloud (`acpCloudConnectedMs=66561`).
- **The snapshot settled it:** Linux had 6.4 GB, **no swap**, 1.2 GB available. All processes together
  held 2.2 GB (Devin Desktop 1.65 GB of it, its window process at 91% CPU), Linux's own slab and shmem
  ~0.2 GB, yet 4.9 GB showed as used: ChromeOS had reclaimed ~2.5 GB from the Linux VM for itself. A
  copy of **Google Chrome inside Linux** (from the bundle's base install) was also running, ~0.3 GB once
  shared pages are counted, with one process at 91% CPU: Devin's Login had opened the sign-in page there,
  because Linux Chrome was registered as the default browser (item 4).
- So Devin plus its agent extensions needs ~2 GB of headroom, and when ChromeOS takes memory back, Linux
  has nowhere to put the overflow. **Fixes are operational:** keep ChromeOS's own tabs and Android apps
  light while Devin is open (Search + Esc shows them), keep Linux Chrome closed (item 4 stops sign-ins
  opening it), and keep Devin lean. Heavy Devin use belongs on the 16–32 GB Windows laptops.
- Three imported extensions were removed along the way and stay removed by choice, not because they
  caused this: Gemini Code Assist (Google supports it in VS Code and JetBrains, and Devin has its own
  agent), `coenraads.bracket-pair-colorizer-2` and `s-nlf-fh.glassit` (both fail on every start: a
  missing `vscode-textmate` module, and `pgrep 'code'`).

**Two Devin details found on the way** (docs only):

- **CodeLLDB** (`vadimcn.vscode-lldb`): Open VSX serves the universal package, which downloads its Linux
  add-on through `workbench.extensions.command.installFromVSIX`. Devin Desktop doesn't have that command
  ("Platform package installation failed ... command not found"). The fix is to install
  `codelldb-linux-x64.vsix` from its GitHub release with `devin-desktop --profile <name>
  --install-extension <file>`.
- **Devin's profile isn't the built-in Default.** Onboarding's VS Code import created a profile *named*
  "default" at `~/.config/Devin/User/profiles/-164eb798`, tied to Devin's workspace (`userDataProfiles`
  and `profileAssociations` in `~/.config/Devin/User/globalStorage/storage.json`). Command-line
  `--install-extension`, `--uninstall-extension` and `--list-extensions` act on the built-in Default
  unless given `--profile <name>`.

**Setup** (under `install-windsurf`; the flag keeps its name, chosen Oct 26):

- **Package:** install `devin-desktop` directly from the same apt source (fall back to `windsurf` if the
  source doesn't offer it yet). The existing `windsurf.list` and key stay.
- **Launcher entry "Devin (X11)"** (chosen: A): generated from the installed
  `/usr/share/applications/devin-desktop.desktop` at every run (not a frozen copy, so vendor changes to
  `Icon`, `StartupWMClass` or `MimeType` carry over): `Name=` gets " (X11)" and every `Exec=` program is
  replaced by the terminal wrapper below, by absolute path (`$HOME/.local/bin/devin-desktop`; the launcher
  has no `~/.local/bin` on PATH), keeping the stock arguments (`%F`, `--new-window %F`). So the icon and
  the terminal start Devin the same way: through `/usr/bin/devin-desktop` with `--ozone-platform=x11`.
  Written to `~/.local/share/applications/devin-desktop-x11.desktop`.
- **Stock entry hidden** (chosen: A): `~/.local/share/applications/devin-desktop.desktop` is the stock
  file plus `NoDisplay=true`, also regenerated each run. If the launcher ignores that as it ignored the
  `Exec` change, the stock icon simply stays; the hand check below tells.
- **URL handler:** `devin-desktop-url-handler.desktop` copied with `--ozone-platform=x11` added after its
  stock program (it keeps the Electron binary and `--open-url %U`; going through the CLI script there is
  untested). Inside Linux, `xdg-open` follows the user-directory override, so a `devin://` link starts it
  on X11 too.
- **Terminal wrapper** (chosen: A): `~/.local/bin/devin-desktop` (and `~/.local/bin/windsurf` when
  `/usr/bin/windsurf` exists) runs the system `/usr/bin/devin-desktop --ozone-platform=x11 "$@"`, by
  absolute path so it can't call itself. `~/.local/bin` is ahead of `/usr/bin` on PATH. CLI-only
  calls (`--install-extension`, `--list-extensions`, `--version`) ignore the flag.
- **Extensions are left alone** (revised Oct 26): setup installs no extension into Devin (no CodeLLDB)
  and removes none you imported.
- **Idempotent:** each run regenerates the three entries and the wrapper; a hand-made
  `devin-desktop-x11.desktop` (the Oct 26 one) is replaced by the generated one, which differs only in
  following the installed stock file.

**Test** (Windsurf section, renamed "Devin Desktop / Windsurf (install-windsurf)"):

- `devin-desktop --version` (check), via the wrapper.
- Apt source present (check, as now).
- `devin-desktop-x11.desktop`: every `Exec=` runs `$HOME/.local/bin/devin-desktop` (the wrapper), and
  it has no `NoDisplay` (check). The wrapper exists, runs `/usr/bin/devin-desktop`, and passes
  `--ozone-platform=x11` (check).
- Stock entry overridden with `NoDisplay=true` (warn: cosmetic).
- `command -v devin-desktop` is the wrapper, and the wrapper passes the flag (check).
- Disk report: measure `devin-desktop` (the transitional `windsurf` package is a few KB).

No GUI launch in the test; that's the hand check.

**Init:** version bump only. Sign-in is a browser step.

**Docs:**

- `docs/crostini-gotchas.md`:
  - Graphics: "Devin Desktop (Windsurf) freezes or closes under Wayland", and that the ChromeOS launcher
    ignores an override with the same file name, so the fix is a separate entry.
  - Memory and disk: "ChromeOS takes memory back from Linux": the VM's "used" includes memory ChromeOS
    reclaimed (2.5 GB of 4.9 GB on Oct 26), there is no swap, so a 2 GB Electron IDE freezes when it
    runs out; how to tell (`ps` total vs `free`), and what helps.
- `docs/init-checklist.md`, the editors line: open **Devin (X11)**; click Login once and give it
  20–30 s; keep ChromeOS's tabs light while it's open. Command-line extension changes need
  `--profile <name>` (the name is in `storage.json`); CodeLLDB's Linux add-on is a manual install with
  that flag. Machines set up before v96: rerun setup with install-windsurf, then shut Linux down once so
  the launcher picks up the new entry.
- README: the gotchas list gets a Devin line next to Android Studio's, and a memory line; flag table
  text "Windsurf (now Devin Desktop)".
- CHANGELOG (all four sections).

**To verify on the Chromebook:** on the machine fixed by hand on Oct 26, setup replaces the hand-made
entry and the wrapper without breaking either; after a Linux restart the launcher shows **Devin (X11)**
(and, if `NoDisplay` is honoured, not the stock icon); opened from it, `pgrep -af devin-desktop` shows
`--ozone-platform=x11`, and its parent was `/usr/bin/devin-desktop` (`VSCODE_CLI` set, no shell-environment
timeout in the log); Login completes in ChromeOS's browser (item 4). `devin-desktop` from a terminal
also gets the flag. Devin stays up through several launches from the icon, including one after a Linux
restart, with ChromeOS's tabs kept light.

## 4. Links from Linux open in ChromeOS's browser (setup base)

**Found Oct 26 2026** (with item 3): the base install's Google Chrome registered itself in Linux as the
handler for web links (`com.google.Chrome.desktop` for `x-scheme-handler/http(s)` and `text/html`).
So every link a Linux app opens (sign-in pages, `--open` dev servers, docs) starts a Linux copy of
Chrome inside the VM's memory, separate from your ChromeOS browser and its sign-ins. Devin's Login did
that, and the Linux Chrome left running added to the memory squeeze in item 3.

`xdg-settings set default-web-browser` refuses ("$BROWSER is set"): ChromeOS's Linux sets
`BROWSER=/usr/bin/garcon-url-handler` itself, and `xdg-open` checks the MIME registration before
`$BROWSER` anyway. What worked:

```
xdg-mime default garcon_host_browser.desktop x-scheme-handler/https x-scheme-handler/http text/html
```

**Tested Oct 26** (all through `xdg-open`, landing in ChromeOS's browser):

| Link | Result |
| --- | --- |
| `https://example.com` | Opened in ChromeOS's browser. |
| `http://localhost:8765` (a Linux server bound to 127.0.0.1) | Opened, served from Linux: ChromeOS still passes `localhost` to Linux in the full-VM mode. |
| `http://127.0.0.1:8765` | Opened, served from Linux. |
| `~/xdg-test.html` | Opened from the Linux files share (`file:///media/fuse/crostini_…`). |
| A DDEV site, default router (`https://ddev-test.ddev.site`, ports 80/443) | **Refused** (`ERR_CONNECTION_REFUSED`). ChromeOS passes high ports through to Linux, not 80 and 443. |
| The same site on its direct port (`http://127.0.0.1:32772`, from `ddev describe`) | Opened ("hello from DDEV"). |
| The same site with DDEV's router on 8080/8443 (`https://ddev-test.ddev.site:8443`) | Opened, with Chrome's "Not secure" (the mkcert CA is trusted in Linux only). |

So Playwright, Selenium, Cypress and Puppeteer are unaffected (they start their own browser), Linux
Chrome stays installed and launchable, and command-line sign-ins with a localhost callback (`gh`,
`gcloud`, `az`, `wrangler`, `vercel`, Hugging Face) should complete in ChromeOS's browser, since
`localhost` and `127.0.0.1` both pass through.

| Choice | |
| --- | --- |
| A | ChromeOS's browser for every link (the `xdg-mime` line above). |
| B | A small router as the default handler (`~/.local/bin/open-url` plus a `.desktop` entry): `*.ddev.site` and other local HTTPS names stay in Linux Chrome, where the mkcert CA is trusted; everything else goes to ChromeOS's browser. |
| A now, B if DDEV fails (chosen first) | Build A; the DDEV check decides. |
| **A, with DDEV's router on 8080/8443 (chosen Oct 26, after the DDEV check)** | Every link to ChromeOS's browser; DDEV's router moves to high ports, which ChromeOS does pass through. B (the router script) is dropped. |

**The DDEV check, Oct 26** (a throwaway `php` project, `~/ddev-test`, on dragonair's 38 GB disk): the first
two tries ran the disk out of space while pulling `ddev-webserver`, and the full disk left
`~/.ddev/.state.yaml` and `~/.ddev/.update` at 0 bytes, after which every `ddev start` panicked
("assignment to entry in nil map" in `remoteconfig`); moving the two empty files aside fixed it (DDEV
rewrote them). Freeing ~5 GB of caches (npm 2.3 GB, Docker build cache 2.7 GB, uv, Go, Composer, Linux
Chrome's cache) let it start. Then the table above. `ddev config global --router-http-port=8080
--router-https-port=8443` then `ddev poweroff && ddev start` made `ddev launch` open
`https://ddev-test.ddev.site:8443` in ChromeOS's browser. Ports 8080/8443 match what install-lan-share
already uses for DDEV between laptops (LAN 8080/8443 → the router, read by `ddev_router_port`), so a site
is `:8443` on its own laptop and from the others.

**Setup** (base, after the Google Chrome install, so Chrome's own registration comes first and this
overrides it):

- When `/usr/share/applications/garcon_host_browser.desktop` exists (ChromeOS only), run the `xdg-mime
  default` line above; it writes `~/.config/mimeapps.list`. Rerun-safe. Not on ChromeOS: a NOTICE, and
  nothing changes.
- **DDEV's router on 8080/8443** (base, where setup already runs `ddev config global
  --instrumentation-opt-in=false`): `ddev config global --router-http-port=8080 --router-https-port=8443`
  on ChromeOS, unless `router_http_port` / `router_https_port` are already set to something else in
  `~/.ddev/global_config.yaml` (yours wins; a NOTICE says which ports DDEV sites are on). A router already
  running keeps its old ports until `ddev poweroff`; setup says so. The LAN share keeps working:
  `ddev_router_port` reads the new ports, LAN 8080/8443 now pass to local 8080/8443; the build confirms
  that the relay (it listens on the Linux network address, the router on 127.0.0.1) and `tailscale serve`
  coexist with the router on the same port numbers.
- **Two demos move off 8080**, since DDEV's router holds it while any DDEV project runs: the Docker
  voting app to **8090** (vote) and **8091** (results), through a generated copy of its compose file with
  those host ports (an override file would add ports, not replace them); Spring PetClinic to **8092**
  (`--server.port=8092`). Their launchers, notes and `docs/dev-demo.md` follow.
- **DDEV's certificates:** print once, after the mkcert step, how to trust the mkcert CA in ChromeOS
  (Settings → Privacy and security → Security → Manage certificates → Authorities → Import the
  `rootCA.pem` from `mkcert -CAROOT`, "Trust this certificate for identifying websites"), so `*.ddev.site`
  opens without a warning. ChromeOS's certificate store isn't reachable from Linux, so this stays a
  manual step.
- **Opting out:** `xdg-mime default com.google.Chrome.desktop x-scheme-handler/https
  x-scheme-handler/http text/html` puts Linux Chrome back (in the checklist).

**Test** (base section):

- DDEV's router ports in `~/.ddev/global_config.yaml` are 8080 and 8443, or values you set (check when
  absent, warn when changed by you).
- The two moved demos' ports (8090, 8091, 8092) appear in their generated launchers (dev-demo isn't in
  the test loop; this is the build's own check).
- `xdg-mime query default x-scheme-handler/https` (and `http`, `text/html`) is
  `garcon_host_browser.desktop` (warn, since it's your setting to change; hint: Linux Chrome may have
  taken it back if you accepted its "make Chrome your default browser" prompt; rerun setup or the
  `xdg-mime` line).
- No live open in the test (it would open browser tabs).

**Init:** version bump only.

**Docs:**

- `docs/crostini-gotchas.md`, a new section or Network: "Links from Linux open in Linux Chrome": why,
  the `xdg-mime` fix, why `xdg-settings` refuses, and that localhost passes through.
- `docs/init-checklist.md`: DDEV sites are `https://<site>.ddev.site:8443` (and why); the ChromeOS CA
  import for DDEV, step by step (`cp "$(mkcert -CAROOT)/rootCA.pem" ~/ddev-rootCA.pem`, Settings →
  Privacy and security → Security → Manage certificates → Authorities → Import, trust for websites,
  then delete the copy); how to switch back to Linux Chrome.
- `docs/crostini-gotchas.md`: "ChromeOS doesn't pass ports 80 and 443 to Linux" (DDEV's router moved
  to 8080/8443); and under Memory and disk, "A full disk can leave DDEV unable to start": 0-byte
  `~/.ddev/.state.yaml` / `.update` make `ddev start` panic; move them aside; DDEV's images want ~3 GB.
- README: one line in the gotchas list.
- CHANGELOG (all four sections).

**To verify on the Chromebook:** on a clean machine after setup, `xdg-open https://example.com` opens in
ChromeOS's browser; `gh auth login --web` (or init's GitHub step) completes there; a demo's dev server
opens with `--open`; `ddev launch` on a DDEV site opens `https://<site>.ddev.site:8443` in ChromeOS's
browser, first with a certificate warning and, after the CA import, without one; from another laptop
over install-lan-share, the same site on `:8443`. The voting app and PetClinic demos open on their new
ports while a DDEV project is running.

## 5. Build and debug Lazarus (and build Delphi) projects in VS Code, Cursor and Devin

**Asked Oct 26 2026:** whether projects meant for the Lazarus or Delphi IDE can be built, run and
debugged from VS Code, Windsurf/Devin or Cursor, using the settings the IDEs already keep. Yes, because
neither IDE is needed to build:

- **Lazarus / Free Pascal: build, run and debug.** `lazbuild` reads the project's `.lpi` (compiler
  options, build modes, unit paths, package dependencies), as the IDE does, plus `~/.fpc.cfg` (item 1).
  Packages installed from the IDE live in its profile, so `lazbuild` takes the same `--pcp` as the IDE
  (`~/.lazarus` or `~/.lazarus-dark`). Free Pascal writes DWARF, which **gdb** reads, and gdb knows
  Pascal; the editors drive it through **Native Debug** (`webfreak.debug`). CodeLLDB also works but
  lldb doesn't know Pascal, so values display worse. Lazarus 4's own debugger is FpDebug, so gdb isn't
  there unless install-cpp put it there.
- **Delphi 3–7 (Wine): build and run, no debugging.** `dcc32.exe` runs under Wine and reads the
  project's `.dpr` plus the `.cfg` the IDE writes next to it (search paths, defines), so it builds what
  the IDE would. Delphi writes Borland's own debug format, which gdb and lldb can't read, and Wine's
  debugger is minimal: debugging stays in the Delphi IDE (Wine, or the real Windows guests). A Delphi
  project converted by Lazarus (Tools → Delphi Conversion; Free Pascal's `{$mode delphi}`) becomes a
  Lazarus project with the full build-and-debug path.

**Confirmed by hand Oct 26** (before any v96 code), in Devin on TDaemon with hand-written `tasks.json` and
`launch.json`: gdb wasn't installed (no install-cpp on that machine; `apt install gdb` brought gdb 16.3),
Devin offered Native Debug from Open VSX on the first F5, `lazbuild` built the Debug mode into
`x86_64-linux/Debug/TestDaemon`, and gdb stopped at a breakpoint in `daemonworkerthread.pas` on the worker
thread, switching between threads. The Debug Console takes gdb commands (`p <expr>`), not bare variable
names: typing `FDaemonWorkerThread` there gives "Undefined command". Two more from the same session:
`string` locals (`aMessage`, `LogFilePath`) and a `Text` file variable showed as `<unknown>` / "unknown
type" in Variables. The project was already on **Dwarf 3 (beta) (`-gw3`)**: that format is aimed at Lazarus's
own FpDebug and describes strings and file types in a way gdb can't read. For gdb, Lazarus's choice is
**Dwarf 2 with sets (`-gw2 -godwarfsets`)**, where an AnsiString is a plain pointer to chars that gdb
prints as text (FpDebug reads it too). The project also had "Use external debug symbols file (`-Xg`)" on;
gdb found the `.dbg` file through its debug link, so breakpoints worked.

**Where gdb + Native Debug tops out** (same session, after switching to Dwarf 2 with sets): breakpoints,
stepping, threads and the call stack work, and the Debug Console prints strings (`p LOGFILEPATH` gave
`'/home/…/x86_64-linux/Debug/20261026.log'`, `p AMESSAGE` gave `'Daemon worker thread running'`). Two
things don't: expanding a string in Variables or Watch ("A syntax error in expression, near
`*LOGFILEPATH`": Native Debug builds C-style expressions, gdb is in Pascal mode), and `F: Text` stays
`<unknown>` (Free Pascal doesn't describe file records for gdb). `set language c` didn't help (C-syntax
expressions still failed), so the generated `launch.json` gets no `autorun`. The generated files and the
checklist say so plainly: use the editor to build, run, step and print with `p`; open the project in the
Lazarus IDE (FpDebug) to inspect records, objects and file variables. And Self appears to gdb as
`this` (`Execute (this=0x…)`), so fields are watched as `this.<Field>` from a method's frame.

**FpDebug in VS Code** (same day): **Free Pascal (fpc) Debugger**, `CNOC.fpdebug` (Joost van der Sluis's
FPDServer, a Debug Adapter Protocol server around Lazarus's FpDebug, embedded for 64-bit Linux; ~76,600
installs; Microsoft's marketplace only, not found on Open VSX, and Microsoft's terms keep its extensions to
Microsoft's editors, so VS Code only). It needs DWARF 3 (`-gw3`) and doesn't build. With TDaemon's Debug
mode back on `-gw3` and a clean `lazbuild -B`, launched with `"type": "fpDebug"`, `program`
`${workspaceFolder}/x86_64-linux/Debug/TestDaemon`, `parameters` `["-r"]`, `preLaunchTask` the
lazbuild task: it stopped at the breakpoint in `LogToFile` on the worker thread, listed all three threads,
showed Arguments and Locals separately with their real case, and **showed strings as text**
(`aMessage = 'Daemon worker thread running'`, `LogFilePath = '/home/…'`). Watches use Pascal (`Self`, not
`this`). `f: Text` stays `Unknown type`, and casts to `TextRec`, `TTextRec` or `PLongInt` say "Identifier
not found": those types are in the RTL, which ships without debug info. Workaround for your own code:
`fView: TextRec absolute f;` beside `f` puts `TextRec`'s layout into the unit's debug info, and a `fView`
watch then expands (Name, Mode, Handle); in the checklist as a tip, not generated.

Then, with `fView: TextRec absolute f;` added: `fView` expanded in Locals, and `TextRec(f)` worked as a
watch too, since the unit's debug info now has `TextRec`. Stopped *on* `AssignFile` (before it runs), every
field read `$5555…` (pointers `Pointer($5555555555555555)`, `bufpos` 6148914691236517205 = `$5555555555555555`,
`UserData` bytes 85 = `$55`, `name` chars shown as '啕'): that is the project's "Trash variables (`-gt`)"
option filling uninitialized locals with `$55` on purpose, so it looks like noise until `AssignFile` runs.

So the two debuggers want opposite debug info: FpDebug needs DWARF 3, gdb reads strings only with DWARF 2
with sets, and a build mode has one type.

| Choice: two debuggers, one project | |
| --- | --- |
| **B (chosen)** | `lazmode vscode` adds a second build mode, **Debug-gdb**, to the `.lpi`: a copy of Debug set to Dwarf 2 with sets. VS Code builds Debug and debugs it with FpDebug; Devin and Cursor build Debug-gdb and debug it with gdb. Each editor gets its best debugger; the project file gains one build mode (visible, and removable, in Lazarus). |
| A | DWARF 3 everywhere, both launch configurations, no `.lpi` change; gdb in Devin/Cursor then reads strings only through console commands (`x/s *(char**)&NAME`). |
| C | Dwarf 2 with sets everywhere, gdb only; FpDebug left out. |

| Choice: the command | |
| --- | --- |
| **A (chosen)** | Subcommands on the commands you already use: `lazmode vscode [dir]` and `delphi N vscode [dir]`. |
| B | One new command, `pas-vscode [dir]`, detecting `.lpi` or `.dpr` itself. |

| Choice: the extensions | |
| --- | --- |
| **A (chosen)** | Recommended per project: the generated `.vscode/extensions.json` lists `alefragnani.pascal`, `webfreak.debug` and `CNOC.fpdebug`, so each editor offers what its store has when the folder opens (VS Code all three; Devin and Cursor won't find `CNOC.fpdebug` on Open VSX, which is expected). No editor CLIs, no Devin `--profile` handling. |
| B | Setup installs both into every installed editor, each Devin profile included. |

| Choice: dev-demo | |
| --- | --- |
| **A (chosen)** | A new `editor` item in the Lazarus examples launcher: pick a project, generate its `.vscode`, open it in VS Code, Cursor or Devin (whichever are installed). |
| B | Pre-generate `.vscode` in every example project when the demo installs. |
| C | TDaemon only, as the worked example. |

| Choice: Delphi | |
| --- | --- |
| **A (chosen)** | Included: build and run tasks (`delphi N build`, `delphi N run`), no launch configuration. |
| B | Lazarus only. |

**Setup** (under `install-lazarus`, plus `install-retro` for the Delphi part):

- **gdb** joins install-lazarus's apt packages (it's only in install-cpp today).
- **GNU Global** (`global`, which provides `gtags` and `global`) joins them too (asked Oct 26): the Pascal
  extension (`alefragnani.pascal`) uses it for Go to Definition and Find References, and without it shows
  "The "global" command is not available. Make sure it is on PATH" (seen Oct 26 in VS Code).
- **`lazmode vscode [dir] [--profile light|dark] [--force]`** (dir defaults to the current folder):
  - Finds the project's `.lpi` (one in the folder, or asks which when there are several; `dir` may also
    be the `.lpi` itself).
  - The executable's path is **asked of `lazbuild`, not read from the `.lpi`**: TDaemon's target is
    `x86_64-linux/Debug/TestDaemon`, built from macros (`$(TargetCPU)-$(TargetOS)/$(BuildModeName)`),
    which a plain read of `Target/Filename` gets wrong (found Oct 26: the hand-written `launch.json`
    pointed at `./TestDaemon`). First choice `lazbuild --pcp=<profile> [--bm=Debug]
    --get-expand-text='$(TargetFile)' <project>.lpi`; if that option isn't there, one build and the path
    from its `Linking <path>` line. The build confirms which works with Lazarus 4.8.
  - Profile: dark when `~/.lazarus-dark` exists, unless `--profile light` (you work in the dark one).
  - **Adds the Debug-gdb build mode** (choice B) to the `.lpi`, unless one by that name exists: a copy
    of the Debug mode (or, with no Debug mode, of the default one with debug info turned on) whose debug
    info type is Dwarf 2 with sets (`-gw2 -godwarfsets`). The `.lpi` is XML; the edit is done with python3
    on a parsed copy, the original kept as `<project>.lpi.bak` the first time, and the result checked by
    `lazbuild --bm=Debug-gdb` before it replaces the original. Nothing else in the `.lpi` changes. If the
    Debug mode itself isn't on DWARF 3, it says that FpDebug needs `-gw3` and how to set it; it doesn't
    change Debug. If either mode has no debug info at all (`GenerateDebugInfo` false), it says so (gdb
    and FpDebug then can't stop at breakpoints). The build confirms the exact `.lpi` keys.
  - The target path is asked of `lazbuild` once per mode (above), since a project's output path usually
    includes `$(BuildModeName)` (TDaemon's does), so the two builds don't overwrite each other. A project
    whose path doesn't vary by mode gets a NOTICE: the two builds then share one file, and each launch's
    build step rebuilds it for its debugger.
  - Writes `.vscode/tasks.json`: `lazbuild (Debug)` (the default build task, Ctrl+Shift+B) and
    `lazbuild (Debug-gdb)`, each `lazbuild --pcp=<profile> --bm=<mode> <project>.lpi`, plus a clean
    (`-B`) variant of each, all with a problem matcher for Free Pascal's
    `file(line,col) Error|Fatal|Warning|Note|Hint: message`, so errors land in Problems and click through.
  - Writes `.vscode/launch.json` with two configurations: `<project> (FpDebug)`, `"type": "fpDebug"`,
    `program` the Debug target, `workingdirectory` the project folder, `preLaunchTask` `lazbuild (Debug)`
    (for VS Code), and `<project> (gdb)`, Native Debug `"type": "gdb"`, `target` the Debug-gdb target,
    `cwd` the project folder, `preLaunchTask` `lazbuild (Debug-gdb)` (for Devin and Cursor). No `autorun`.
    Each configuration's name says which editor it's for.
  - Writes `.vscode/extensions.json` (recommendations above).
  - Writes `.vscode/settings.json` pointing the Pascal extension's code navigation at GNU Global (gtags)
    and letting it generate the tags itself; the build confirms the setting names against the
    extension's current documentation. `GTAGS`, `GRTAGS` and `GPATH` land in the project folder; the
    generated settings exclude them from the Explorer and search.
  - Existing files are kept unless `--force` (a NOTICE names them), so your own edits survive.
- **`delphi N build PROJECT.dpr`** (new): runs that version's `dcc32.exe` (found under the prefix's
  `Delphi*/Bin`, as `delphi_bin` finds Delphi 1's) in the prefix, console only (no virtual desktop),
  from the project folder so it reads the `.cfg`. Output keeps dcc32's `file(line) Error: …` form.
- **`delphi N vscode [dir] [--force]`**: finds the `.dpr`, writes `.vscode/tasks.json` with a default
  build task (`delphi N build`, a problem matcher for dcc32's messages, paths mapped from Wine's
  `C:\` / `Z:\` back to Linux where dcc32 prints them) and a run task (`delphi N run <Project>.exe`,
  the existing subcommand with its desktop and fonts), plus `extensions.json` (Pascal only). No
  `launch.json`; the generated file says why in a comment.
- Both write only into the project's `.vscode/`; nothing in `~`.

**Test:**

- Lazarus section: gdb present (check); `global --version` and `gtags` on the scratch example writes
  `GTAGS` (check). `lazmode vscode` on a copy of a small Lazarus example in the
  test's scratch folder adds the Debug-gdb mode (its `.lpi` parses and `lazbuild --bm=Debug-gdb` builds,
  check), and writes three files that parse as JSON, `launch.json` holding one `fpDebug` and one `gdb`
  configuration (check); both build tasks' commands, run as written, build (check); the Debug binary
  (or its `.dbg`) has DWARF version 3 and the Debug-gdb one version 2 (`readelf --debug-dump=info`,
  check); `gdb -batch -ex run` runs the Debug-gdb binary to exit (check). FpDebug isn't run in the test
  (it needs VS Code).
- Retro section (when a Delphi 3–7 prefix with `dcc32.exe` exists): `delphi N build` compiles a
  one-line console `.dpr` and `wine` runs the result (check); otherwise SKIP.
- `delphi N vscode` writes JSON that parses (check), when that prefix exists.

**Init:** version bump only.

**Demo** (`lazarus examples` launcher, choice A): a new item, `editor`: pick a project (same menu as
now), run `lazmode vscode` on it with the light/dark choice the launcher already asks, then open the
project folder in VS Code, Cursor or Devin (a menu of those installed; Devin through its X11 wrapper,
item 3). The launcher's note says: F5 builds and debugs; for TDaemon, `-r` is already the argument in
`launch.json`, and the item 1 note applies.

**Docs:**

- `docs/init-checklist.md`, Lazarus section: `lazmode vscode`, the Debug-gdb mode it adds and why,
  which configuration to pick in which editor, the extensions each editor will offer, `--profile`; what
  each debugger shows (FpDebug: strings and objects in Variables, `Self`; gdb: stepping, `p NAME` in the
  Debug Console with names in capitals); the `fView: TextRec absolute f;` tip for file variables, and that
  stopping before `AssignFile` shows the `-gt` trash pattern (`$55…`) rather than real values; GNU Global
  and what it adds (Ctrl+click navigation); retro section: `delphi N build` / `delphi N vscode` and why there's no
  debugging.
- `docs/dev-demo.md`: the `editor` item.
- README: one line each under install-lazarus and install-retro.
- CHANGELOG (all four sections).

**To verify on the Chromebook:** `lazmode vscode` in `~/dev-demo/lazarus/examples/TDaemon`, open the
folder in Devin and in VS Code, accept the recommended extensions; Ctrl+Shift+B builds and an error
introduced on purpose shows in Problems at the right line; F5 stops at a breakpoint in
`DaemonWorkerThread` with variables readable, the target being `x86_64-linux/Debug/TestDaemon`. In Devin,
the editor offers Native Debug (`webfreak.debug`, on Open VSX) when F5 first meets the `gdb` type, and the
`(gdb)` configuration builds Debug-gdb. In VS Code, the `(FpDebug)` configuration stops at the same breakpoint
with strings readable in Variables. The `.lpi` change shows in Lazarus as a Debug-gdb build mode, and the
project still builds and debugs in the Lazarus IDE. The dark-profile packages are found (`--pcp`). For Delphi
(once a Delphi 3–7 is installed): `delphi 7 vscode` in a project folder, Ctrl+Shift+B builds it, the run
task starts it in the Delphi desktop.

**Decided Oct 27 2026, after the build** (the build's findings, then the owner's answers in the v96 PR):

- **Go to Definition, machine-wide.** gtags' built-in parsers don't read Pascal: the tags it wrote for TDaemon were
  empty, and the Pascal extension's README says Global needs a plug-in parser. Setup (install-lazarus) installs
  `universal-ctags` (when `apt-cache policy` shows a candidate; otherwise a NOTICE and the Pascal part is skipped,
  setup doesn't fail) and writes `~/.globalrc` as a marked block: Pascal files (`.pas .pp .lpr .inc .dpr`) go to
  Universal Ctags, everything else keeps Global's built-in parsers (taken from the system `gtags.conf` by reference).
  `lazmode vscode` writes no `gtags.conf`. Test: `gtags` on a scratch copy of TDaemon, then `global -x LogToFile`
  finds it. The checklist's manual step is replaced.
- **Debug-gdb gets its own folders, only when needed.** TDaemon's 4.8 `.lpi` writes
  `$(TargetCPU)-$(TargetOS)\Debug\TestDaemon` with a literal `Debug`, so the premise above ("TDaemon's does" vary
  by mode) doesn't hold, and Lazarus's macro is `$(BuildMode)` (or `$(BuildModeCaption)`), not `$(BuildModeName)`
  (`ide/buildmanager.pas`). When the target or unit output path doesn't vary by build mode, Debug-gdb gets its own
  target and unit folders (`Debug` -> `Debug-gdb` in the path), Debug unchanged; the NOTICE becomes "gave Debug-gdb
  its own folders". On TDaemon both binaries now sit side by side (`x86_64-linux/Debug`, `x86_64-linux/Debug-gdb`)
  with DWARF 3 and 2.
- **Accepted as built:** the DDEV ports in the laravel, symfony and drupal-graphql notes (item 4), and devmem's swap
  line ("Memory looks fine." with the missing swap noted, item 7).

## 6. How long a new login shell takes (dev-test, base)

**Found Oct 26 2026** (with item 3): Devin's first launcher-started log said "Unable to resolve your shell
environment in a reasonable time. Please review your shell configuration and restart." VS Code-based
editors started from a launcher icon run the login shell (`$SHELL -i -l`) to read its environment, and
give up after 10 s; when they do, the editor, its terminal tasks and its extensions run without the PATH
entries `~/.bashrc` adds (`~/.local/bin`, Homebrew last, nvm's Node, `~/.gems/bin`, `~/.cargo/bin` and the
rest), with nothing telling you why. Devin avoids the step since item 3 (its launcher goes through
`/usr/bin/devin-desktop`, which sets `VSCODE_CLI`); **VS Code's and Cursor's launcher icons still run it**.
The test already checks that a new shell starts *without errors* (v74), not how *fast*.

**Test** (base, next to "a new interactive shell starts without errors"):

- **"a new login shell starts in under 5 s"**: times `bash -i -l -c true` under the same harness as the
  v74 check (`setsid -w env -i HOME USER LOGNAME SHELL TERM PATH=<system PATH>`, stdin from
  `/dev/null`, `timeout 30`), three runs, the median reported in the line (`2.1 s`). **WARN** at 5 s or
  more, **FAIL** at 10 s or more (VS Code's limit: an icon-started VS Code or Cursor then runs without
  your PATH).
- On WARN or FAIL, the hint names the slow part: the same shell run once more with `PS4='+ $EPOCHREALTIME '`
  and `-x` into the test's scratch folder, and the five slowest lines (time to the next trace line) printed
  with their source text. A shell that hangs past 30 s says so and prints the last traced line.
- The median goes into the run's log line (not the disk TSV), so runs can be compared.

**Setup, init, demo:** version bump only. No change to `~/.bashrc` from this item: what to speed up is
decided once a measured run shows what's slow.

**Docs:**

- `docs/crostini-gotchas.md`, Packages and PATH: "An editor started from its icon can miss your PATH":
  the 10 s limit, the message, which editors, and the test that measures it.
- `docs/init-checklist.md`: what the new check means and how to read its hint.
- CHANGELOG (all four sections).

**To verify on the Chromebook:** the check reports a time on the machine from Oct 26 (dragonair), and the
first run's figure goes into this plan's notes; a deliberately slow line (`sleep 6` at the end of
`~/.bashrc`) gives a WARN whose hint points at it; removing it brings the check back to PASS.

## 7. A memory report: `devmem` (setup base)

**Found Oct 26 2026** (with item 3): Linux showed 6.4 GB total, 4.9 GB used, 1.5 GB available, **no swap**,
while its processes held only 2.2 GB (Devin Desktop 1.65 GB of it) and slab plus shmem ~0.2 GB: ChromeOS
had reclaimed ~2.5 GB from the Linux VM. Seeing that took several commands and some arithmetic. With no
swap, a reclaim at the wrong moment freezes a large app instead of slowing it.

**Setup** (base): a command, `~/.local/bin/devmem`, with no dependencies beyond procps, `awk` and (when
there) `docker` and `ollama`. It prints:

- **Memory:** total, used, available, swap (with "none" called out), from `/proc/meminfo`.
- **Where "used" is:** Linux processes (sum of PSS from `/proc/*/smaps_rollup`, which counts shared pages
  once, falling back to RSS where a process can't be read; the line says which), kernel (Slab +
  KernelStack + PageTables), shared memory (Shmem), and the rest as **"taken back by ChromeOS (estimate)"**.
- **Top programs by memory**, processes grouped by program name (all of Devin Desktop's, all of
  Chrome's), the top 10.
- **Bundle services running:** Docker containers that belong to the bundle (`devsvc-*`, `devdb-*`,
  DDEV's), each with its memory from `docker stats --no-stream`; Ollama's loaded models (`ollama ps`).
- **A verdict**, one line per finding that applies: ChromeOS has reclaimed more than 1.5 GB ("close
  ChromeOS tabs or Android apps: Search + Esc shows them"); less than 1 GB available; Linux's Google Chrome
  is running ("links open in ChromeOS's browser since v96, so it can usually be closed"); a heavy `devsvc`
  engine or database server is running (named, with its stop command); no swap ("a large app freezes
  instead of slowing down when memory runs out"). None: "Memory looks fine."
- **Options:** `devmem --watch [seconds]` (default 5) refreshes in place until Ctrl-C, for watching while
  something misbehaves; `devmem --brief` prints the memory line and the verdict only.

**Test** (base): `devmem` runs and exits 0, and its output has the Memory, Where, Top programs and verdict
sections (check); `devmem --brief` prints at most a few lines (check); the "taken back by ChromeOS" figure
is a number between 0 and the total (check).

**Init, demo:** version bump only.

**Docs:**

- `docs/crostini-gotchas.md`, Memory and disk: the item 3 memory entry points at `devmem`.
- `docs/init-checklist.md`, "After it finishes": `devmem`, and when to reach for it (a freeze, a slow
  machine, before starting a heavy engine).
- README: one line in the commands list.
- CHANGELOG (all four sections).

**To verify on the Chromebook:** with Devin Desktop open and a few ChromeOS tabs, `devmem` shows Devin
Desktop at the top and a "taken back by ChromeOS" figure close to what the Oct 26 arithmetic gave; opening
heavy ChromeOS tabs makes that figure grow under `devmem --watch`; starting a `devsvc` heavy engine adds it
to the services and the verdict; with Linux's Chrome open the verdict names it.

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
- [x] Item 2, Oct 27 (after the build): drush through `vendor/bin/drush.php` everywhere in the bundle (drush 13.8)
- [x] Item 3: Devin Desktop under X11, under install-windsurf
- [x] Item 3, launcher: A (a separate "Devin (X11)" entry, stock entry hidden with `NoDisplay`)
- [x] Item 3, terminal: A (`~/.local/bin/devin-desktop` wrapper adds the flag)
- [x] Item 3, flag name: A (keep `install-windsurf`; it installs `devin-desktop`)
- [x] Item 3, revised Oct 26: the later freezes were memory (gotcha doc); setup installs and removes no
      Devin extensions (CodeLLDB and Gemini dropped from setup and test; CodeLLDB's profile fix in the docs)
- [x] Item 3, launcher (found Oct 26): every `Exec=` runs the wrapper, i.e. `/usr/bin/devin-desktop`, not the
      Electron binary
- [x] Item 4: ChromeOS's browser for Linux links: A, with DDEV's router on 8080/8443 (DDEV check passed
      Oct 26; router script B dropped); voting app to 8090/8091, PetClinic to 8092
- [x] Item 5: `lazmode vscode` and `delphi N vscode` subcommands (A); extensions recommended per project
      (A); dev-demo `editor` launcher item (A); Delphi build + run included (A)
- [x] Item 5, two debuggers: B (a Debug-gdb build mode on Dwarf 2 with sets for gdb; Debug on DWARF 3 for
      VS Code's FpDebug, `CNOC.fpdebug`)
- [x] Item 5, added Oct 26: GNU Global under install-lazarus, and `lazmode vscode` writes
      `.vscode/settings.json` for the Pascal extension's gtags navigation
- [x] Item 5, Oct 27 (after the build): Universal Ctags and a `~/.globalrc` block for Pascal (machine-wide, no
      `gtags.conf` per project); Debug-gdb gets its own target and unit folders when Debug's paths don't vary by mode
- [x] Item 6: dev-test times a new login shell (WARN 5 s, FAIL 10 s, slowest lines in the hint)
- [x] Item 7: `devmem` memory report (with `--watch` and `--brief`)
- [x] Anything else for v96: nothing further (Oct 26); plan final
