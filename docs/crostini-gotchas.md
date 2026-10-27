# Crostini gotchas

These are things that went wrong while building this bundle on ChromeOS's Linux (Debian 13, 8 GB
Chromebooks), and what fixed each one. Every fix is in the scripts. Search them for the flag in brackets
to see it in context; the comment above each fix usually tells the story.

## Graphics

- **Windowed OpenGL falls back to software rendering** (setup base). Crostini hands Linux a virgl GPU as
  `/dev/dri/renderD128`, which belongs to the `render` group. The default user is only in `video`, so Godot,
  Flutter desktop, Android Studio's previews and Chrome's WebGL silently use llvmpipe.
  **Fix:** `usermod -aG video,render $USER`, then shut Linux down and reopen it.
- **There is no Vulkan** (`install-godot`). Only OpenGL comes through. Godot's Forward+ and Mobile renderers
  need Vulkan, so the `godot` launchers default to `--rendering-driver opengl3`.
  **Fix:** pick the Compatibility renderer for new projects.
- **Android Studio's window dims while it has focus** (`install-android-native`). This happens under
  ChromeOS's Wayland, with the IDE's JetBrains runtime.
  **Fix:** `-Dawt.toolkit.name=XToolkit` in its VM options.
- **Devin Desktop (Windsurf) freezes or closes under Wayland** (`install-windsurf`, v96). On ChromeOS's Wayland
  its window froze at sign-in (62 s of silence, then `Fatal Wayland communication error: Broken pipe`) or
  vanished ("clean-exit"), with or without extensions (Oct 26 2026). **Fix:** `--ozone-platform=x11`
  (XWayland), through a wrapper, `~/.local/bin/devin-desktop`, and its own launcher entry, "Devin (X11)".
  Two launcher traps: the ChromeOS launcher ignored an edited copy of `devin-desktop.desktop` with the same
  file name in `~/.local/share/applications` (the icon still started it on Wayland), so the fix is a
  separately named entry; and the entry must run `/usr/bin/devin-desktop` (the CLI script, which sets
  `VSCODE_CLI`), not the Electron binary the stock entry runs, which resolved the shell environment itself
  and crashed within 5 s every time. The freezes that came back on X11 were memory (see Memory and disk).
- **GTK2 dialogs in Lazarus draw blank and freeze** (`install-lazarus`, v94). The SourceForge IDE is built on
  GTK2. Under Crostini some of its modal dialogs (Run Parameters, New Project) drew blank until resized and
  never took keyboard focus, while Tools → Options worked. Removing `gtk2-engines-pixbuf` didn't help, and
  GTK2 theming (`gnome-themes-extra`, Adwaita-dark gtkrc) doesn't touch the cause.
  **Fix:** setup rebuilds the IDE with `lazbuild --build-ide= --ws=qt5` (needs `libqt5pas-dev`, and a
  user-owned `/usr/share/lazarus/<ver>/units/x86_64-linux/qt5`, or the final make step stops with "mkdir:
  Permission denied"). `lazbuild --add-package` also saves the packages to the profile's install list
  (`StaticAutoInstallPackages` in `miscellaneousoptions.xml`), and every later `--build-ide` builds them in;
  the IDE installs packages the same way, rebuilding itself from that list. So the floating build runs with
  the docking packages out of it, and since v95 the list names them exactly while docked is active, so the
  IDE's own rebuild (Package → Install/Uninstall Packages, or a project's install prompt) keeps its layout
  and `lazmode` adopts the result. On Oct 25 2026 that rebuild stayed on Qt5; should one come out GTK2,
  `lazmode` keeps it aside and puts the Qt5 layout back.
  **The IDE's own rebuild came out GTK2 on a fresh profile** (v96). On Oct 27 2026 the dark docked IDE,
  set up by v96, installed lazdaemon for TDaemon, rebuilt itself and came back light with a blank white
  dialog. The IDE's own rebuild uses the widgetset of its build profile (Tools → Configure Build Lazarus,
  `LCLPlatform` under `BuildLazarusOptions/Profiles` in `miscellaneousoptions.xml`). lazbuild's `--ws=qt5`
  sets that only in memory, and its `--add-package` saves the profiles with Lazarus's defaults: gtk2 in
  all four, on Linux. **Fix:** `lazmode` changes gtk2 to qt5 in every build profile after its builds and
  in `lazmode status`, which setup runs for both profiles. A widgetset you chose yourself is left alone,
  and nothing is changed while Lazarus runs, because the IDE saves its options on exit. The dark look comes from qt5ct
  (`QT_QPA_PLATFORMTHEME=qt5ct`); ChromeOS draws the title bars, so no Linux theme changes them.
  `startlazarus` buffers its output, so `--debug-log` and `tee` logs are cut off when a hung IDE is killed
  and don't help diagnose a hang.

## Network

- **Downloads hang on IPv6** (setup base). A Linux VM can get IPv6 addresses with no route out. `wget` then
  waits on one IPv6 address after another, while the ChromeOS browser works because it races IPv4 against
  IPv6. **Fix:** setup detects this and adds `precedence ::ffff:0:0/96 100` to `/etc/gai.conf`, plus
  `Acquire::ForceIPv4` for apt. Every wget and curl also gets a 20-second connect timeout.
- **Linux port forwarding is gone** (`install-lan`). On these Chromebooks, new Linux installs since ChromeOS
  147 run as a full VM, with no port forwarding from ChromeOS. Other laptops can't reach a service in
  Linux. **Fix:** Tailscale.
- **Tailscale starts in userspace mode** (`install-lan`). In this VM `tailscaled` picked userspace
  networking by itself, so there was no `tailscale0` interface and Linux tools couldn't reach the 100.x
  addresses. **Fix:** `FLAGS="--tun=tailscale0"` in `/etc/default/tailscaled`.
- **Links from Linux open in Linux Chrome** (setup base, v96). The base install's Google Chrome registers
  itself as Linux's handler for web links, so a sign-in page or a dev server's `--open` started a second
  Chrome inside the VM's memory, without your ChromeOS sign-ins (Devin Desktop's Login did, Oct 26 2026).
  `xdg-settings set default-web-browser` refuses ("$BROWSER is set": ChromeOS sets
  `BROWSER=/usr/bin/garcon-url-handler`), and `xdg-open` checks the MIME registration first anyway.
  **Fix:** `xdg-mime default garcon_host_browser.desktop x-scheme-handler/https x-scheme-handler/http
  text/html`. `localhost` and `127.0.0.1` still reach Linux from ChromeOS's browser, so dev servers and
  localhost sign-in callbacks work.
- **ChromeOS doesn't pass ports 80 and 443 to Linux** (setup base, v96). High ports reach Linux from
  ChromeOS's browser, 80 and 443 don't: a DDEV site on the default router ports gave
  `ERR_CONNECTION_REFUSED`, while its direct port and the router on 8080/8443 opened (Oct 26 2026).
  **Fix:** `ddev config global --router-http-port=8080 --router-https-port=8443`, then `ddev poweroff`;
  sites are `https://<site>.ddev.site:8443`. mkcert's CA is trusted in Linux only, so ChromeOS's browser
  warns until the CA is imported there by hand (the init checklist has the steps).
- **Ollama answers 403 to a plain hostname** (`install-lan`). Ollama refuses a `Host:` it doesn't
  recognise. **Fix:** the address book also writes `NAME.internal` names, which it accepts.
- **The GitHub API rate-limits anonymous calls** (many flags). It allows 60 calls an hour per IP, then
  returns 403 in the middle of a run. **Fix:** release tags come from the `releases/latest` redirect, which
  isn't rate-limited.

## Memory and disk

- **Linux sees about 6.4 GB of an 8 GB Chromebook.** SQL Server and Oracle hold about 2 GB each while
  running, and Solr, OpenSearch, Elasticsearch, Milvus and Atlas Local hold 1–3 GB. **Fix:** setup creates
  them stopped. `mssql up`, `oracle up` and `devsvc up` stop the other heavy engines first and check a
  memory budget (`DEVSVC_RAM_MB`).
- **ChromeOS takes memory back from Linux** (setup base, v96). The Linux VM's "used" memory includes what
  ChromeOS has reclaimed from it for itself: on Oct 26 2026 Linux showed 4.9 GB of 6.4 GB used, but its
  processes held only 2.2 GB (Devin Desktop 1.65 GB of it) and slab plus shmem about 0.2 GB, so ChromeOS had
  taken about 2.5 GB. There is no swap, so when a 2 GB Electron IDE runs out it freezes or closes instead of
  slowing down. To tell: add up the processes (`ps`, or better PSS from `/proc/*/smaps_rollup`) and compare
  with `free`. **Fix:** `devmem` does that arithmetic ("taken back by ChromeOS (estimate)"), names the top
  programs and the bundle's running containers, and says what to close; `devmem --watch` follows it while
  something misbehaves. What helps: keep ChromeOS's tabs and Android apps light while a heavy Linux app is
  open (Search + Esc shows them), close Linux's Google Chrome, run one heavy engine at a time.
- **`vm.max_map_count` can't be raised from inside the container** (`install-search`). OpenSearch and
  Elasticsearch normally insist on it. **Fix:** `node.store.allow_mmap=false`, so they don't need it, and
  their disk watermarks are off, so a nearly full disk doesn't turn an index read-only.
- **`/tmp` is RAM-backed.** Large downloads and the test script's scratch space live on disk instead
  (`./assets`, and the test's own work folder).
- **Disk: caches fill it, and a full disk breaks DDEV** (setup base, v96). On Oct 26 2026 DDEV's image pull ran
  dragonair's 38 GB disk out of space twice. The full disk left `~/.ddev/.state.yaml` and `~/.ddev/.update` at
  0 bytes, and every later `ddev start` panicked ("assignment to entry in nil map" in `remoteconfig`) until the two
  files were moved aside (DDEV rewrites them). What had filled the disk was mostly caches: npm 2.3 GB, Docker's
  build cache 2.7 GB (which `docker system df` called only 16 kB reclaimable; `docker builder prune -af` freed
  it), uv 641 MB, Homebrew 264 MB, Linux Chrome's cache 189 MB, pnpm 172 MB, Go's build cache 133 MB, Composer
  61 MB, plus apt. DDEV's images want about 3 GB free. **Fix:** `devclean` reports what each cache would free and
  changes nothing; `devclean --run` clears them and moves 0-byte DDEV state files aside; `--images` also removes
  Docker images no container uses. Never `docker system prune`: the bundle's services are containers created
  stopped, and it deletes them.
- **kind works in Crostini's Docker** (`install-k8s`). A cluster takes about 2 GB, so the test unloads
  Ollama's models first.

## Packages and PATH

- **Homebrew shadows Debian** (setup base). Formula dependencies bring their own python3, sqlite3, `as`,
  `ld` and openjdk, and Homebrew's `shellenv` puts them ahead of Debian's. **Fix:** a marked `~/.bashrc`
  block moves Homebrew's directories to the end of PATH. `brew unlink openjdk` keeps `java` on Debian's JDK.
- **A PATH block moved below the lines that need it** (v74). Rewriting a `~/.bashrc` block by deleting it
  and appending it again put it below a `kubectl` completion line, and every new terminal said
  `kubectl: command not found`. **Fix:** marked blocks are rewritten in place.
- **aider needs Python ≤ 3.12, trixie has 3.13** (`install-node`).
  **Fix:** `uv tool install --python 3.12 aider-chat`, which fetches a managed 3.12.
- **npm 12 blocks dependency install scripts** (`install-node` and others). Global CLIs with native
  modules then install broken. **Fix:** `npm install -g --allow-scripts=<names>`, with the names listed per
  package.
- **Debian trixie renamed `libaio.so.1` to `libaio.so.1t64`** (`install-oracle`). Oracle Instant Client
  links against the old name. **Fix:** one compatibility link in the system library directory.
- **Firebird's embedded lock directory** (`install-db`). If another user created `/tmp/firebird` first,
  every embedded open fails. **Fix:** setup probes once and, only if needed, sets a private
  `FIREBIRD_LOCK`.
- **An editor started from its icon can miss your PATH** (dev-test base, v96). VS Code-based editors
  started from a launcher icon run your login shell (`bash -i -l`) to read its environment and give up
  after 10 s, with "Unable to resolve your shell environment in a reasonable time" in the log (Devin
  Desktop, Oct 26 2026). The editor, its terminal tasks and extensions then run without what `~/.bashrc`
  adds to PATH (`~/.local/bin`, nvm's Node, `~/.cargo/bin` and the rest), and nothing says why. VS Code
  and Cursor still do this from their icons; Devin's icon goes through `/usr/bin/devin-desktop` since v96,
  which skips the step. **Fix:** keep a new login shell fast. dev-test times it (median of three runs,
  WARN from 5 s, FAIL from 10 s) and on a WARN or FAIL lists the five slowest lines of a traced run.
- **The docker group isn't active in the run that adds you to it.** Group changes apply to new logins, so
  setup's own Docker calls go through `sudo`, and the helper commands fall back to `sudo -n docker`.

## Android

- **The Android emulator doesn't run in Crostini** (`install-android-native`).
  **Fix:** deploy to the Chromebook's own Android runtime. Turn on ADB debugging in ChromeOS's Linux
  settings, then `adb connect arc`.

## Databases

- **Oracle Free's Lite image ignored `ORACLE_PWD`** (`install-oracle`). Every login failed with ORA-01017.
  **Fix:** the first `oracle up` of a new data volume runs the image's own `setPassword.sh`.
- **InterBase's installer leaves `ibmgr` root-only** (`install-interbase`). Checks run as the user then see
  no server manager. **Fix:** setup gives `bin/` tools the execute bit for everyone. A related trap: the
  unregistered Developer Edition server spins at 100% CPU without ever listening, so setup no longer
  starts it before registration.
- **InterBase's `isql -q` exits 1 even when `CREATE DATABASE` worked** (`install-interbase`).
  **Fix:** the test drops `-q`.

## Lazarus and Free Pascal

- **"This binary has no thread support compiled in", runtime error 232** (`install-lazarus`, v96). Not
  Crostini-specific (any Linux does it), but this is where it bit: Lazarus's TDaemon example stopped on
  `sudo ./TestDaemon -r` (Oct 26 2026). On Linux the RTL has no thread manager until `cthreads` is the first
  unit loaded, and Lazarus's templates and examples load it only behind `{$IFDEF UseCThreads}`.
  **Fix:** `-dUseCThreads` in `~/.fpc.cfg`, which must `#INCLUDE` the system `fpc.cfg` (fpc reads only the
  first config it finds); rebuild an older project once with Run → Clean up and Build.

## Retro

- **Delphi 1's IDE crashes in a shared Wine prefix** (`install-retro`). It fails with a `winevdm.exe` page
  fault. **Fix:** give it its own 32-bit prefix inside a Wine virtual desktop, with integrated debugging
  turned off.
- **Some Chromebooks have no `/dev/kvm`.** Windows NT 4.0 and 2000 under QEMU then run in software
  emulation, which works but is slow. Windows 3.1 and 95 run in DOSBox-X, which doesn't need KVM.
