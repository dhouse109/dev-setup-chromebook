# dev-setup-chromebook v95 plan

Oct 25, 2026 · all choices made Oct 25

## Scope

v95 is a small follow-up to v94, from what the v94 review and release turned up. Base: v94, the first
tagged release (`v94` on `main`, Oct 25 2026).

1. **Branch names** that can't collide with release tags (repo process; no script change).
2. **The qt5ct check** stops warning about a palette you chose yourself.
3. ~~Floating launchers~~ for Lazarus: **not doing** (decided Oct 25; two launchers plus `lazmode dock` stay).
4. **Packages installed from inside the IDE** survive `lazmode dock on|off` (found Oct 25 in use).

Items 2 and 4 change scripts, so the bundle goes to v95: all four scripts bumped, CHANGELOG entries under
all four sections ("version bump only" where nothing changed). Anything v94 use turns up can join.

Each item below lists the choices that were offered; the decision is marked. The build starts once
"anything else for v95" is settled.

## 1. Branch names (in this plan's PR, not in v95's build)

**Why:** CLAUDE.md says "one branch per version (`vNN`)", and the release step tags `vNN`. v94 had a
branch and a tag with the same name, so `git checkout v94` was ambiguous until the branch was deleted.

**Change** (made in CLAUDE.md in this PR, so the v95 build session follows it from the start):

- Version branches are `release/vNN` (v95 is built on `release/v95`).
- Plan PRs use `plan/vNN` (this one is `plan/v95`).
- The tag stays `vNN`, as in v94.
- Release step: delete the merged branch after merging (it no longer clashes, but it is spent).

**Repo settings, yours to flip** (not something a commit can do):

- [ ] Settings → General → **Automatically delete head branches**, so merged branches disappear on
      their own.
- [ ] Delete the leftover `claude-md-v94-plan` branch from PR #1.

## 2. qt5ct check (test)

**Why:** v94's test has `warn "qt5ct: Fusion style with the darker palette"`. On Oct 25 your config used
the **waves** palette, which you picked in `lazmode theme`, and the test warned about it. A warning you
are meant to ignore hides real ones, and the "clean run" rule (FAIL 0, WARNs only for optional
credentials) can't be met while it fires.

What actually matters is that the **Lazarus (Dark)** launcher looks dark: qt5ct is configured, it uses a
custom palette, and that palette file exists.

| Choice | What dev-test does |
| --- | --- |
| **A (chosen)** | PASS naming the style and palette ("Fusion, palette waves") whenever `custom_palette=true` and `color_scheme_path` names a file that exists. WARN only when the palette file is missing or `custom_palette=false` (the dark launcher would then show the style's light palette), with `lazmode theme` as the fix. |
| B | Always an INFO line with the style and palette; never PASS, WARN or FAIL. |
| C | Keep v94's WARN for anything other than darker. |

Setup is unchanged either way: it seeds darker only when no `qt5ct.conf` exists, and leaves yours alone.
`lazmode status` already prints the style and palette.

**Also:** `docs/init-checklist.md`'s Lazarus section says any palette is fine, and how to pick one.

## 3. Floating launchers (optional)

**Why:** after v94 there are two launchers, **Lazarus** and **Lazarus (Dark)**. Each opens whichever
layout `lazmode dock on|off` made active. You asked whether there should be four.

| Choice | What it adds |
| --- | --- |
| **A (chosen)** | Nothing: two launchers, layouts switched with `lazmode dock`. v94 as it is. |
| B | Two more launchers, **Lazarus (Floating)** and **Lazarus (Dark, Floating)**, that open the floating build for that session only. The default stays whatever `lazmode dock` set, so the stock launchers keep their meaning. |
| C | Four launchers that each switch the profile's default (`lazmode dock on/off`) and then start it, so the last one used becomes the default. |

**Not built.** Kept for the record, in case it comes back. **How B would work:** a new `lazmode open [--profile light|dark] [--layout docked|floating] [FILE]`
starts `<profile>/bin/lazarus-<layout>` with the profile's `--pcp` (and `QT_QPA_PLATFORMTHEME=qt5ct` for
dark). The new launchers' `Exec=` lines call it, so the launch logic stays in one place, like the builds.
Things the build has to handle:

- **Process names:** `lazmode`'s "is Lazarus running" check uses `pgrep -x` on `lazarus`,
  `startlazarus`, `lazarus-ide` and `lazbuild`. A build started directly runs as `lazarus-docked` or
  `lazarus-floatin` (Linux keeps 15 characters), so the check needs those names, or `lazmode rebuild`
  could replace a build that is running.
- **No `startlazarus`:** opening a build directly skips `startlazarus`, which only matters for restarting
  the IDE after its own Tools → Build Lazarus. The docs already steer package installs to `lazmode
  rebuild` instead.
- **One IDE per profile:** a floating and a docked IDE on the same profile at once would share and
  overwrite each other's settings. `lazmode open` refuses when that profile's IDE is already running.
- **To verify on the Chromebook:** the floating build started directly finds its Lazarus directory and
  packages the same way as through `startlazarus`.

Test (B or C): the new launchers exist with the right `Exec=` and `Name=`; `lazmode open --help` exits 0.
Init: the "configured" line names four launchers. Docs: checklist, README's `lazmode` mention, CHANGELOG.

## 4. Packages installed from inside the IDE (lazmode)

**Found Oct 25 2026, using the dark profile:** a project that needs packages makes the IDE offer to
install them. Accepting rebuilds the IDE, which restarts **floating**. `lazmode dock on` then brings back
the docked layout **without** those packages, the project asks again, and the loop repeats. In
floating mode everything works.

**Why:** the IDE installs packages by rebuilding itself from the profile's install list
(`StaticAutoInstallPackages` in `miscellaneousoptions.xml`) and writing the result to `bin/lazarus`,
which `startlazarus` restarts. v94 keeps the docking packages *out* of that list (so the floating
build stays floating), so the IDE's own rebuild comes out floating. `lazmode dock on|off` then copies
`lazarus-docked` or `lazarus-floating` over `bin/lazarus`; both were built before the new packages, so
the IDE's build and its packages are thrown away.

**Evidence (Oct 25, 21:35):** `lazmode status --profile dark` showed `active layout: other (matches
neither build)` with `bin/lazarus` on Qt5 (so the IDE's own rebuild stayed on Qt5), while both lazmode
builds dated from 02:08. The light profile, not used for this, was as v94 left it: `bin/lazarus` equal
to the docked build, and a list of DBFLaz and SynEditDsgn (`Count="4"` with two items: v94's scrub
removes the docking entries and leaves the count, which Lazarus tolerates).

**Dark profile, confirmed (Oct 25, 21:50, after the workaround below):**

- The IDE's own build, kept as `bin/lazarus.ide-built`, is 140,605,952 bytes: byte for byte the size of
  the floating build `lazmode rebuild` made a minute later from the same list. So the IDE's rebuild was
  a floating build with the new packages.
- The IDE saved the install list **without** the docking packages: `Printer4Lazarus`, `TurboPowerIPro`,
  `SQLDBLaz`, `SynEditDsgn`, `DBFLaz`, `DesignBaseClassDemoPkg` (`Count="6"`). So the docked IDE
  rebuilds from the list as saved, not from the packages compiled into it: a list that names the
  docking packages while docked is active should be enough to keep the layout (to verify on the
  Chromebook, below).
- `lazmode rebuild --profile dark` with that list took about 11 s per layout (a relink) and left docked
  active (143,048,264 bytes, the new packages in both layouts).

**Workaround until v95:** after the IDE installs packages, close Lazarus and run
`lazmode rebuild --profile <light|dark>`. The list now names the new packages, so both layouts get
them, and docked becomes active again (`lazmode rebuild` treats "matches neither" as docked).

**Fix (recommended design):**

- **The install list follows the active layout.** While docked is active, the list names the docking
  packages; `lazmode dock off` takes them out and `dock on` puts them back (same safe edit as v94's
  scrub, a copy of the old file kept in `assets/logs`). The IDE's own rebuild then keeps the layout it
  was started in. `lazmode rebuild` still builds the floating layout with them out (v94's save and
  restore around the build) and leaves the list matching the active layout afterwards.
- **lazmode adopts the IDE's build instead of overwriting it.** When `bin/lazarus` matches neither build
  and is newer than both, every `lazmode` command first adopts it: if it links Qt5, it becomes
  `lazarus-docked` or `lazarus-floating` (docked when it contains `TAnchorDockMaster`), and the old one
  is kept as `.bak`. If it is not Qt5 (the IDE fell back to GTK2), it is not adopted: `lazmode` says
  so, keeps it aside, and points to `lazmode rebuild`.
- **Each build records the list it was built from** (the package names, docking ones left out, next to
  the version in `bin/.lazmode-built`, one line per layout). A build whose list differs from the
  profile's current list is **stale**, and `lazmode status` says so.
- **Switching to a stale layout** (see the choice below).
- **Setup:** a profile counts as done only when neither layout is stale, so a setup rerun brings both
  up to date.
- **Test:** per profile, both builds were built from the current install list (FAIL, with
  `lazmode rebuild --profile X` as the fix); the active `bin/lazarus` is one of the two builds (as in
  v94); the list names the docking packages exactly when docked is active.
- **Init:** the "configured" line also requires that neither layout is stale.
- **Docs:** `docs/init-checklist.md` and `docs/crostini-gotchas.md` drop "install packages with `lazmode
  rebuild --add-package`, never from the IDE's Package menu": installing from the IDE (or when a project
  asks) becomes the normal way, and `lazmode rebuild --add-package` stays for scripted installs.

| Choice: switching to a stale layout | What `lazmode dock on|off` does |
| --- | --- |
| **A (chosen)** | Rebuilds that layout first (minutes, with the build log as in `rebuild`), then switches. A switch is a file copy again once both are current. |
| B | Refuses, naming the packages the layout lacks, and says to run `lazmode rebuild`. |

**To verify on the Chromebook:** with the docking packages in the list, the docked IDE's own rebuild
(Package → Install/Uninstall Packages, or a project's install prompt) comes out docked and on Qt5;
`lazmode status` afterwards shows the adopted build and the floating layout as stale; `dock off` (A:
rebuilds it) gives a floating IDE that opens the project without asking.

## Carried forward

**From the v93 plan, on-hardware checks still open** (fixes they need become v95 items):

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

- [x] Item 2: A (PASS for any working palette; WARN only when the dark launcher wouldn't look dark)
- [x] Item 3: A (no extra launchers)
- [x] Item 4: A (a switch to a stale layout rebuilds it first); cause confirmed from the dark profile
- [ ] Anything else for v95
