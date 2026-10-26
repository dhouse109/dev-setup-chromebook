# dev-setup-chromebook v95 plan

Oct 25, 2026 · draft, choices not yet made

## Scope

v95 is a small follow-up to v94, from what the v94 review and release turned up. Base: v94, the first
tagged release (`v94` on `main`, Oct 25 2026).

1. **Branch names** that can't collide with release tags (repo process; no script change).
2. **The qt5ct check** stops warning about a palette you chose yourself.
3. **Floating launchers** for Lazarus (optional; your call).

Items 2 and 3 change scripts, so the bundle goes to v95: all four scripts bumped, CHANGELOG entries under
all four sections ("version bump only" where nothing changed). Anything v94 use turns up can join.

Each item below lists its choices, with a recommendation. Strike or change any of them; the build starts
once they are settled.

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
| **A (recommended)** | PASS naming the style and palette ("Fusion, palette waves") whenever `custom_palette=true` and `color_scheme_path` names a file that exists. WARN only when the palette file is missing or `custom_palette=false` (the dark launcher would then show the style's light palette), with `lazmode theme` as the fix. |
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
| **A** | Nothing: two launchers, layouts switched with `lazmode dock`. v94 as it is. |
| **B (recommended, if you want four)** | Two more launchers, **Lazarus (Floating)** and **Lazarus (Dark, Floating)**, that open the floating build for that session only. The default stays whatever `lazmode dock` set, so the stock launchers keep their meaning. |
| C | Four launchers that each switch the profile's default (`lazmode dock on/off`) and then start it, so the last one used becomes the default. |

**How B would work:** a new `lazmode open [--profile light|dark] [--layout docked|floating] [FILE]`
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

- [ ] Item 2: A, B or C (recommended: A)
- [ ] Item 3: A, B or C (recommended: B if you want four launchers, else A)
- [ ] Anything else for v95
