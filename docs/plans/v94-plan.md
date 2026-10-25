# dev-setup-chromebook v94 plan

Oct 24, 2026 · moved into the repo Oct 25, 2026

## Scope and priority

Lazarus is v94's top priority. After v94, running setup with `install-lazarus` on a clean Chromebook
should end exactly where the hand-configured machine stood on Oct 24, 2026: a Qt5 IDE whose dialogs
work, light and dark profiles, docked and floating layouts, and a `lazmode` command to switch layouts.
Nothing else needs setting up.

- **Base:** v93, the published initial release.
- **One flag:** everything rides on the existing `install-lazarus`, so `install-editors` and
  `install-all` get it too. There is no new flag.
- **Built during setup:** all four IDE binaries (2 profiles × 2 layouts) are built during setup, so the
  first launch or switch never waits on a build.
- **Other v94 items:** the housekeeping fixes below, plus anything v93 testing turns up.

## Where v93 stands

v93's `install-lazarus` already installs the right base: the SourceForge 4.8 debs. v94 adds to that
block rather than replacing it.

| Script | What v93 does with Lazarus | v94 change |
| --- | --- | --- |
| setup | Downloads `fpc-laz`, `fpc-src`, `lazarus-project` 4.8.0 to `assets/downloads` (`wget -c`, `dpkg-deb --info` check), installs them in order, deletes the debs. Pulled in by `install-editors` → `install-all`. | Qt5 steps added after the install |
| test | "Lazarus / Free Pascal" section: `fpc -iV`, `lazbuild --version`, `fpc-src` present, hello-world compile, installers cleaned up | New checks in the same section |
| test (disk report) | `dapt editors "Lazarus + Free Pascal"` counts only the three debs | Count `~/.lazarus*` binaries and units too |
| init | Flag expansion only | Short configured/skipped report |
| dev-demo | `demo_lazarus` copies `/usr/share/lazarus/<ver>/examples` and opens the chosen `.lpi` with `startlazarus` | Optional light/dark choice |

The v93 download URL hardcodes `Lazarus%204.8`. v94's new steps read the installed version from
`dpkg-query -W -f='${Version}' lazarus-project`, so their paths keep working after a Lazarus upgrade.

The Firebird/InterBase SQLdb checks and demos use `fpc` only, not the IDE, so the rebuild doesn't
affect them.

## Setup: install-lazarus additions

The new steps run right after v93's deb install, inside the same `install-lazarus` block. Each one is
guarded, so a rerun skips what's already done, and a hand-configured machine like the one set up on
Oct 24 is simply brought into line.

1. **Detect the version:** set `LAZ_VER` from `dpkg-query` and `LAZ_DIR=/usr/share/lazarus/$LAZ_VER`.
   Stop with a clear message if `lazarus-project` isn't installed.
2. **apt:** `libqt5pas-dev qt5ct`.
3. **Build folder:** `sudo install -d -o $USER -g $USER $LAZ_DIR/units/x86_64-linux/qt5`. Without it,
   the read-only SourceForge tree fails the IDE's final make step with "mkdir: Permission denied".
4. **Profiles:** light = `~/.lazarus`, dark = `~/.lazarus-dark` (created by `--pcp`). The dark profile
   is seeded from light only if it doesn't exist yet.
5. **Four builds, always `--ws=qt5`:** for each profile, build floating first, then docked. The first
   build per profile compiles every package and takes minutes. The second mostly relinks, about 30 s on
   the Oct 24 run.
6. **Active binary:** copy `lazarus-docked` to `bin/lazarus`. `startlazarus` launches
   `<profile>/bin/lazarus`, so docked is the default.
7. **Dark launcher:** write `~/.local/share/applications/lazarus-dark.desktop` from the system
   `lazarus.desktop`, with `Name=Lazarus (Dark)` and
   `Exec=env QT_QPA_PLATFORMTHEME=qt5ct startlazarus --pcp=<expanded $HOME>/.lazarus-dark %f`. The stock
   launcher stays as the light one.
8. **qt5ct:** pre-seed `~/.config/qt5ct/qt5ct.conf` with Fusion style and the darker palette, so there
   is no first-run dialog. Confirm the key names against Trixie's qt5ct while building. Leave an
   existing config alone.
9. **`lazmode`:** install to `~/.local/bin/lazmode`.

| Profile | Floating build | Docked build (active) |
| --- | --- | --- |
| light `~/.lazarus` | `lazbuild --build-ide= --ws=qt5` → `bin/lazarus-floating` | same + `--add-package` docking → `bin/lazarus-docked` → `bin/lazarus` |
| dark `~/.lazarus-dark` | same with `--pcp=$HOME/.lazarus-dark` | same with `--pcp` |

Docking packages: `$LAZ_DIR/components/anchordocking/design/anchordockingdsgn.lpk` (docked main window)
and `$LAZ_DIR/components/dockedformeditor/dockedformeditor.lpk` (form designer as an editor tab).

Build output goes to an `assets` log. Only the `tail` goes to the console, since a single build prints
thousands of hints.

## lazmode command

`lazmode` switches between the binaries that setup already built, so a switch is a file copy that takes
seconds. It refuses to switch or rebuild while Lazarus is running (`pgrep -f lazarus`). `--profile`
defaults to `both`.

| Command | What it does |
| --- | --- |
| `lazmode status` | Per profile: active layout (docked/floating), whether both builds exist, the widget set reported by `ldd`, the dark launcher's `Exec=` line, and the qt5ct style and palette |
| `lazmode dock on [--profile light\|dark\|both]` | Copies `bin/lazarus-docked` over `bin/lazarus` |
| `lazmode dock off [--profile …]` | Copies `bin/lazarus-floating` over `bin/lazarus` |
| `lazmode rebuild [--profile …] [--add-package <lpk>…]` | Rebuilds both layouts with `--ws=qt5` and keeps the active layout. This is the supported way to install IDE packages or recover after a Lazarus upgrade |
| `lazmode theme` | Opens qt5ct with `QT_QPA_PLATFORMTHEME=qt5ct` |

The light/dark choice stays with the two launchers rather than `lazmode`. You pick it when you open the
IDE, there's no state file, and both can run side by side.

If `lazmode rebuild` gets extra packages, it records them in `<profile>/lazmode-packages` so later
rebuilds include them.

## Test, init, disk report, dev-demo

**Test** (added to the existing "Lazarus / Free Pascal (install-lazarus)" section, every item a
`check` = FAIL if missing):

- `lazarus-floating`, `lazarus-docked` and `bin/lazarus` exist in both profiles, and each links
  `libQt5Pas` (`ldd`)
- `bin/lazarus` matches one of the two builds (`cmp`), with the result reported as docked or floating
- `$LAZ_DIR/units/x86_64-linux/qt5` exists and is owned by the user
- the dark launcher exists, and its `Exec=` contains `QT_QPA_PLATFORMTHEME=qt5ct` and
  `--pcp=$HOME/.lazarus-dark`
- `~/.config/qt5ct/qt5ct.conf` exists with Fusion and the dark palette (`warn` if the user changed them)
- `lazmode status` exits 0
- `lazbuild --version` still passes with `--pcp=$HOME/.lazarus-dark`

**Init:** a Lazarus line reports "configured" (four builds plus the launcher are present) or "skip" when
the flag isn't installed. There are no credentials or prompts.

**Disk report:** the editors line adds `~/.lazarus/bin`, `~/.lazarus/units`, `~/.lazarus-dark/bin` and
`~/.lazarus-dark/units` to the three debs, so the TSV measures the real footprint.

**dev-demo (optional):** `demo_lazarus` asks light or dark before opening an `.lpi`. The dark choice
runs `env QT_QPA_PLATFORMTHEME=qt5ct startlazarus --pcp=$HOME/.lazarus-dark`. dev-demo stays outside the
test/checklist loop.

## Housekeeping found while moving to the repo

Proposed additions; strike any you don't want.

- **dev-demo version string:** `dev-demo-chromebook.sh` sets `VERSION=92` while its header says 93, so
  the demo's summary line and the `.dev-demo-source` files it writes report v92. The v94 bump sets it to
  94 with the other version strings.
- **Unversioned file names:** dev-demo writes `dev-demo-chromebook-v$VERSION.sh` into two generated files
  (lines ~530 and ~3757). In the repo the scripts are unversioned, so these should name
  `dev-demo-chromebook.sh` (keeping "v$VERSION" as a separate version mention).
- **Version-consistency check (optional):** a CI step that fails when the version strings across the
  four scripts don't all match, so a missed bump can't ship again.

## Docs, housekeeping and cost

**Cost:** expect roughly 10–20 extra minutes and several hundred MB over a plain Lazarus install on a
clean machine. The first v94 disk report replaces these estimates with measured numbers.

**`docs/init-checklist.md`** — new Lazarus entry:

- the two launchers: **Lazarus** (light) and **Lazarus (Dark)**
- `lazmode` usage (see above)
- manual steps that stay manual: the editor color scheme per profile (Tools → Options → Editor →
  Display → Colors; e.g. Twilight for dark, Default for light) and Object Inspector colors in the dark
  profile (Tools → Options → Environment → Object Inspector)
- warning: install IDE packages with `lazmode rebuild --add-package`, not Package → Install/Uninstall
  Packages. The IDE's own rebuild can fall back to GTK2, and GTK2 dialogs draw blank and freeze under
  Crostini.

**`docs/dev-demo.md`:** the Lazarus demo's light/dark choice and its updated disk footprint.

**`docs/crostini-gotchas.md`:** GTK2 modal dialogs drawing blank under Crostini, and the Qt5 fix.

**`README.md`:** "Current version: v94"; the `install-editors` row can mention Qt5 light/dark Lazarus.

**`CHANGELOG.md`:** a v94 section per script (setup, test, init, demo).

**Versioning:** all four scripts bump to v94, including any with no code change.

## Reference: what worked by hand on Oct 24

These commands, run on the Chromebook (Debian 13 trixie, `lazarus-project` 4.8.0), took the IDE from
frozen GTK2 dialogs to working Qt5 light/dark with docking. Setup automates them.

```
sudo apt install libqt5pas-dev qt5ct
sudo install -d -o "$USER" -g "$USER" /usr/share/lazarus/4.8.0/units/x86_64-linux/qt5
cp -r ~/.lazarus ~/.lazarus-dark
L=/usr/share/lazarus/4.8.0
lazbuild --build-ide= --ws=qt5 --add-package \
  $L/components/anchordocking/design/anchordockingdsgn.lpk \
  $L/components/dockedformeditor/dockedformeditor.lpk
lazbuild --pcp=$HOME/.lazarus-dark --build-ide= --ws=qt5 --add-package \
  $L/components/anchordocking/design/anchordockingdsgn.lpk \
  $L/components/dockedformeditor/dockedformeditor.lpk
QT_QPA_PLATFORMTHEME=qt5ct qt5ct        # Fusion + darker palette, Apply
# ~/.local/share/applications/lazarus-dark.desktop:
#   Name=Lazarus (Dark)
#   Exec=env QT_QPA_PLATFORMTHEME=qt5ct startlazarus --pcp=<your $HOME>/.lazarus-dark %f
```

**Findings that shaped the plan:**

- GTK2 Lazarus under Crostini: some modal dialogs (Run Parameters, New Project) drew blank until resized
  and never took keyboard focus. Tools → Options worked. Removing `gtk2-engines-pixbuf` didn't help. Qt5
  fixed it.
- A plain `--build-ide=` rebuild drops the docking packages, which is why the IDE came back floating.
- `startlazarus` buffers its output, so `--debug-log` and `tee` logs get cut off when Lazarus is killed.
  They're not useful for diagnosing hangs.
- ChromeOS draws the title bars, so no Linux theme changes them.

**Dropped from the first attempt:** `gnome-themes-extra`, `gtk2-engines-pixbuf`,
`GTK2_RC_FILES=…/Adwaita-dark/gtk-2.0/gtkrc` and `~/.gtkrc-2.0`. These were all GTK2 theming, which Qt5
replaced. Setup doesn't install them.

## Carried forward from older plans

The v89, v90, v92 and v93 plans are all built into v93, including install-graphql, the retro guests,
Delphi 3–7, the v93 database fixes and LAN over Tailscale. These are the only items they left open:

**On-hardware checks from the v93 plan** (any fixes they need become v94 items):

- [ ] Windows 95 reads a 1 GB exchange disk (2080 cylinders) in DOSBox-X; else 255 heads
- [ ] win95 sees the app CD as F: with the Windows CD as E:
- [ ] Delphi 7 installs and starts under Wine (`delphi 7 setup`); the integrated debugger stops at a
      breakpoint
- [ ] the same for Delphi 6, 4 and 3, in that order, as the discs are tried
- [ ] Delphi 3 or 4 in win95: debugger on the dynamic core, or only `--core normal`?
- [ ] BDE in each native guest: any "insufficient disk space" error on the larger disks?

**Open question:** why dragonair → eldrid goes through a DERP relay instead of connecting directly
(probably the VM's NAT behind the home router). Running `tailscale netcheck` on both laptops is the
first step.

**Not built here:** the Windows (WSL) bundle, which lives in its own repo, `dev-setup-windows`.
