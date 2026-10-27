# dev-setup-chromebook v97 plan

Oct 26, 2026 · started Oct 26 (item 1, from the v96 hand checks) · **draft: choices open**

## Scope

v97 follows v96. Base: v96 (`release/v96`, PR #6), confirmed on a Chromebook Oct 26 (dev-test PASS 114,
FAIL 0) and being released now. Anything the v96 hand checks turn up that doesn't go into v96 itself can
join this plan.

1. **More ways to free and find disk space:** `devclean` learns the three biggest things it missed on
   Oct 26 (editors' cached extension downloads, extension versions left behind, Linux Chrome's caches),
   says what each step actually freed, and gains a "where is the space" view of the checks that were run
   by hand.

Each item lists the choices offered; the decision is marked when made. The build starts once "anything
else for v97" is settled.

## 1. More ways to free and find disk space (setup base, `devclean`)

**Found Oct 26 2026** (the v96 hand checks, on a 30 GB Linux disk set up from v96 with
`install-editors install-web`). The v96 test ended with 16.6 GB free; three hours later there was
4.6 GB. `devclean` (v96) reported about 3.2 GB to free; `devclean --run` freed 1.9 GB (4.6 → 6.5 GB). Then a
look by hand found more than it had, and clearing it freed another 3.2 GB (6.5 → 9.7 GB).

**How the space was found, by hand** (these are the checks to build in):

```
du -xsh ~/.[!.]* ~/* 2>/dev/null | sort -h | tail -10
sudo du -xsh /var/lib/docker /var/lib/containerd 2>/dev/null
du -sh ~/.vscode/extensions/<publisher.name>-* 2>/dev/null
du -sh ~/.config/* 2>/dev/null | sort -h | tail -6
du -sh ~/.config/Code/* | sort -h | tail -5
docker system df
```

**What they showed:**

| Where | Size | What it was |
| --- | --- | --- |
| `~/.vscode` | 4.2 GB | VS Code's 63 extensions, including **two Codex versions**: 26.1021.22027 (1.2 GB, the one whose panel never loaded) and 26.1007.21434 (977 MB, rolled back to). A rollback leaves the newer version on disk |
| `~/.config/Code/CachedExtensionVSIXs` | **1.7 GB** | VS Code's copies of every extension package it downloaded; installed extensions don't need them |
| `~/.config/google-chrome` | 1.1 GB | Linux Chrome's profile, mostly caches from the morning's sign-in tabs (links go to ChromeOS's browser since v96) |
| `/var/lib/containerd` | 3.3 GB | Docker's image store: Docker 29 keeps images in containerd, so `/var/lib/docker` showed only 952 KB. Mostly DDEV's six images |
| Docker's build cache | 2.7 GB | `devclean --run` emptied it (0 B after), but it freed less than its size: the cache shared layers with the DDEV images just built |
| `~/.config/nvm` | 835 MB | Node installs; kept |

**Cleared by hand** (6.5 → 9.7 GB), all with the program closed first:

```
rm -rf ~/.config/Code/CachedExtensionVSIXs/*                              # 1.7 GB
rm -rf ~/.vscode/extensions/openai.chatgpt-26.1021.22027-linux-x64        # 1.2 GB, not the version in use
pkill -f /opt/google/chrome
rm -rf ~/.config/google-chrome/Default/{Cache,"Code Cache",GPUCache,"Service Worker"}
```

Nothing in use broke: VS Code, its extensions and sign-ins, DDEV's images (all six still listed by
`docker images` after `devclean --run`) and Linux Chrome's profile itself were untouched.

**Proposed changes to `devclean`:**

- **Editors' cached extension downloads:** `CachedExtensionVSIXs` under `~/.config/Code`,
  `~/.config/Cursor` and `~/.config/Devin` (and any other VS Code-based editor's config folder that has
  one), cleared with `--run`. Measured in the report.
- **Extension versions left behind:** in `~/.vscode/extensions`, `~/.cursor/extensions` and
  `~/.devin/extensions`, a folder for an extension of which a different version is the one installed
  (per that folder's `extensions.json`, and the editor's `.obsolete` list). Devin's profiles (v96: Devin's
  "default" profile isn't the built-in Default) all share `~/.devin/extensions`, so a version any profile
  still uses is kept.
- **Linux Chrome's caches:** `Cache`, `Code Cache`, `GPUCache` and `Service Worker` in each profile under
  `~/.config/google-chrome`, only when Linux Chrome isn't running (as v96 already does for
  `~/.cache/google-chrome`). The profile itself (bookmarks, sign-ins, settings) is never touched.
- **What each step freed:** `--run` prints the free space gained per step (df before and after each), so a
  gap between the report's estimate and the result is visible. The report's Docker build-cache line says
  "up to" and why (layers shared with images in use stay).
- **"Where is the space"** (the hand checks above, built in): the largest folders in the home folder
  (including dot folders), Docker's real image store (`/var/lib/containerd` as well as
  `/var/lib/docker`, read with `sudo -n` when allowed), and for the largest editor folders their biggest
  parts. Report only; it never deletes.
- **Never touched**, added to `--help`'s list with the reason: an extension version still in use; editors'
  `User` and `globalStorage` folders (settings and extension sign-ins); browser profiles other than their
  cache folders; `~/.config/nvm` (Node installs).

| Choice: when editors' items are cleaned | |
| --- | --- |
| A (recommended) | Only when that editor isn't running (checked per editor); otherwise the line says "left: VS Code is open". Same rule as Linux Chrome's cache. |
| B | Always; editors cope with a missing download cache, but removing an extension version a running window may still load is riskier. |

| Choice: extension versions left behind | |
| --- | --- |
| A (recommended) | Removed by `--run`, with the editor closed, when another version of the same extension is the installed one. |
| B | Report only; `--run` names them and the command to remove each. |

| Choice: the "where is the space" view | |
| --- | --- |
| A (recommended) | `devclean --where`, a separate option, so the default report stays short. |
| B | Always at the end of the plain `devclean` report. |
| C | A separate command, `devdisk`, next to `devmem`. |

**Test** (base, with the v96 `devclean` checks): the report still changes nothing (now including a
scratch editor folder with a cached VSIX, an old extension version and a Chrome `Cache` folder); `--run`
against those scratch folders removes the cache and the old version and keeps the installed version, the
`User` folder and the profile; `--where` (or the chosen form) runs and names the largest folders.

**Init, demo:** version bump only.

**Docs:**

- `docs/crostini-gotchas.md`, Disk: editors keep a copy of every extension download, and a rollback
  leaves the newer version on disk (Oct 26: 1.7 GB and 1.2 GB); Docker 29 keeps images under
  `/var/lib/containerd`, not `/var/lib/docker`; Docker's build cache can't be freed in full while built
  images share its layers.
- `docs/init-checklist.md`: the new `devclean` lines, the "where is the space" checks (the commands above,
  for doing it by hand), and the never-touch additions.
- CHANGELOG (all four sections).

**To verify on the Chromebook:** on a machine with VS Code, Cursor and Devin installed and used, `devclean`
lists each editor's cached downloads and any old extension versions with sizes; with the editors closed,
`--run` frees roughly what the report said, step by step; every editor still opens with its extensions
and sign-ins; Linux Chrome still opens with its profile; DDEV's images and the bundle's service containers
are still there.

## Carried forward

**From v96:** its own hand checks (in PR #6), and two fixes found during them that went to v96 itself:
DDEV's usage-statistics opt-out moves to the base install (a first `ddev start` asked, on a machine set up
without install-drupal), and `devclean --run`'s per-step figures (if not built in v96, item 1 here covers
them).

**Not bundle work, noted:** Codex's VS Code extension 26.1021.22027 (Oct 23) never loaded its panel on the
Chromebook ("Webview renderer did not become ready", 30 s timeout, twice, after a reload too); rolling back to
26.1007.21434 fixed it, with Auto Update off. Claude Code's panel loaded fine in the same window.

## Choices to make

- [ ] Item 1: when editors' items are cleaned (A: only with the editor closed, recommended)
- [ ] Item 1: extension versions left behind (A: removed by `--run`, recommended)
- [ ] Item 1: the "where is the space" view (A: `devclean --where`, recommended)
- [ ] Anything else for v97
