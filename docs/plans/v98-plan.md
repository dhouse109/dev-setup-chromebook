# dev-setup-chromebook v98 plan

Oct 30, 2026 · started Oct 27 (items 1-3, from the v97 Chromebook runs) · items 4-5 added Oct 30 · **draft: choices open**

## Scope

v98 follows v97. Base: v97 (tag `v97`, PR #8 merged Oct 27 2026 as 7424727), confirmed on a Chromebook
Oct 27 (dev-test PASS 126, FAIL 0, WARN 0 with `install-editors install-web`; setup ran to its summary;
every hand check passed). Anything found in use before the build starts can join this plan.

1. **Setup stops downloading Cursor on every run** (install-cursor): the same fix v97 made for the Lazarus
   debs and Chrome's .deb.
2. **What fills Linux Chrome's profile** (base, `devclean`): about 1 GB, of which `devclean` clears only
   the cache folders (5.5 MB on Oct 27).
3. **Images left by DDEV projects that are gone** (base, `devclean`): the images DDEV builds per project
   stay after the project is deleted.
4. **One instruction file for every coding agent** (repo only, no script change): `CLAUDE.md` becomes
   `AGENTS.md`, with `CLAUDE.md` a symlink to it, so Codex CLI reads the same rules as Claude Code; a new
   section says what an agent may do when it runs locally on a Chromebook. **Done in this plan's PR.**
5. **DuckDB failed to install** (install-lakehouse or install-db-extra): found Oct 30 on a Chromebook;
   cause not yet diagnosed. To be diagnosed and planned with Codex CLI running locally (the first version
   worked on that way).

Each item lists the choices offered; the decision is marked when made. The build starts once all are
made and "anything else for v98" is settled.

## 1. Setup stops downloading Cursor on every run (install-cursor)

**Found Oct 27 2026** in the v97 run-4 setup output: "Downloading Cursor AppImage..." on a machine where
Cursor was already installed and current. The AppImage is ~310 MB (dev-test's disk report). v97 stopped the
same kind of re-download for the Lazarus debs (215 MB) and Chrome's .deb (138 MB).

**Today:** setup asks `https://www.cursor.com/api/download?platform=linux-x64&releaseTrack=stable` for
JSON with a `downloadUrl` (v51), downloads it to a temp file and moves it over `~/.local/bin/cursor`,
whatever is installed.

**Proposed:** remember what was installed and download only when the answer from cursor.com names a
different build. Check at build time what else the JSON carries (a version field would be the natural key;
the URL itself names the build). A failed lookup keeps the installed AppImage, as now.

| Choice: how setup knows the installed build | |
| --- | --- |
| A (recommended) | Record the `downloadUrl` (and version, if the JSON has one) of the last install in a small state file under `assets/` (nothing loose in `$HOME`); skip when cursor.com answers the same. A missing record downloads once and writes it. |
| B | Ask the installed AppImage (`cursor --version`) and compare with the JSON's version. No state file, but it starts Cursor's binary on every setup run, and depends on the JSON having a version. |

**Test:** a stand-in cursor.com answer equal to the record: no download; a different one: one download and
the record updated; no record: one download; a failed lookup: the AppImage kept. Existing Cursor checks
unchanged.

**To verify on the Chromebook:** two setup runs in a row with `install-editors`: the second prints that
Cursor is current and downloads nothing; Cursor still opens from the launcher.

## 2. What fills Linux Chrome's profile (base, `devclean`)

**Found Oct 27 2026** with `devclean --where` (v97): `~/.config/google-chrome` was 997 MB, while the four
cache folders `devclean` clears (`Cache`, `Code Cache`, `GPUCache`, `Service Worker`) held 5.5 MB. Since v96,
links from Linux open in ChromeOS's browser, so Linux Chrome is used mostly by test tools (Puppeteer,
Playwright, Selenium, which use their own temporary profiles).

**Proposed:** find out at build time what the rest is (on the Chromebook: `du -sh ~/.config/google-chrome/*
~/.config/google-chrome/Default/* | sort -h | tail -20`), then:

- `devclean --where` shows the profile's largest parts.
- Folders Chrome rebuilds by itself (for example shader caches and downloaded components or models, if
  that is what they are) join the Chrome line, only while Linux Chrome is closed, as now.
- Never touched, as now: bookmarks, sign-ins, history, settings, extensions.

| Choice: what to clear | |
| --- | --- |
| A (recommended) | Only folders Chrome documents or demonstrably rebuilds (checked on the Chromebook before the build), added to the existing Chrome line. |
| B | Report only (`--where`); clearing stays by hand. |

**To verify on the Chromebook:** `devclean --where` lists the profile's largest parts; with Linux Chrome
closed `devclean --run` frees roughly what the report said; Linux Chrome still opens with its profile, and
dev-test's Puppeteer check passes.

## 3. Images left by DDEV projects that are gone (base, `devclean`)

**Found Oct 27 2026:** `docker system df` showed 7 images, 2 in use, 2.9 GB reclaimable. Two of them were
built for the throwaway `ddev-test` project (`ddev-webserver:v1.25.5-ddev-test-built`, 1.85 GB, and
`ddev-dbserver-mariadb-11.8:v1.25.5-ddev-test-built`, 915 MB, sharing most layers with DDEV's own images).
`devclean --images` (v96) already removes every image no container uses, but those include DDEV's own
images, which download again on the next `ddev start`.

**Proposed:** a `*-<project>-built` image whose project DDEV no longer knows (`ddev list`) is listed on its
own line, with its size ("up to": layers shared with DDEV's images stay), and removed by `--run`. DDEV's own
images and those of projects that still exist are left to `--images`, as now.

| Choice: removing a gone project's images | |
| --- | --- |
| A (recommended) | `devclean --run` removes them (they can't be used again; a new project of that name builds its own). |
| B | Report only; `--images` removes them with the rest. |

**Test:** stand-in `docker` and `ddev`: an image for a project `ddev list` knows is kept; one for a gone
project is reported and removed by `--run`; DDEV's own images untouched.

**To verify on the Chromebook:** with a DDEV project deleted (`ddev delete -Oy ddev-test`), `devclean`
lists its built images and `--run` removes them; another DDEV project still starts without rebuilding
from scratch.

## 4. One instruction file for every coding agent (repo only)

**Why (Oct 30 2026):** the owner wants to try Codex CLI, run locally on a Chromebook, for some of the
bundle work (starting with item 5), alongside Claude Code in cloud sessions. Codex reads `AGENTS.md`, not
`CLAUDE.md`, so it would start without the bundle's rules. `CLAUDE.md` also said "this cloud environment
is not that machine", which is wrong for an agent running on the Chromebook itself.

**Change** (made in this PR, so item 5's work follows it from the start):

- `CLAUDE.md` renamed to `AGENTS.md`; `CLAUDE.md` is now a symlink to it (Claude Code reads it as before).
  Wording made agent-neutral.
- New section "Where you are running": in a cloud sandbox, nothing changes. Locally on a Chromebook, an
  agent may read the repo and `assets/logs/` (the v97 `.output` files), lint, and run read-only
  inspection; it asks the owner before running any of the four scripts, `sudo`, writes outside the repo,
  or heavy services; it never opens credential files; it never forces the host guard.

No script change, so no version bump and no CHANGELOG entry for this item on its own.

## 5. DuckDB failed to install (install-lakehouse)

**Found Oct 30 2026** by the owner on a Chromebook; details in the newest `assets/logs/dev-setup-*.output`
on that machine. Diagnosed locally Oct 30: the CLI download returns 404, before extensions or Python.

**Where DuckDB is installed today:**

- `install-lakehouse` (setup, "Local lakehouse stack"): the CLI from `releases/latest` (no checksum, no
  validation before `install`, unlike rule 9), then `duckdb -c "INSTALL iceberg; INSTALL ducklake;
  INSTALL delta; …"` from extensions.duckdb.org, then `pip install -U duckdb …` in `~/.lakehouse-env` and
  the same extensions from Python. Setup runs under `set -e`, so a failure in any of these stops the run.
- `install-db-extra` (setup, "Extra ODBC drivers"): the DuckDB ODBC driver zip from `releases/latest`
  into `/opt/duckdb-odbc`.

**Found (local diagnosis, Oct 30 2026):** the newest output,
`assets/logs/dev-setup-20261030-224131.output`, ends at lines 193-197:

```text
=================================================================
Installing Local Lakehouse Stack (DuckDB, Iceberg, DuckLake, Delta Lake, dbt)...
=================================================================
Installing DuckDB CLI...
curl: (22) The requested URL returned error: 404
```

The failed command is setup's CLI download (line 6775). `install-db-extra` was skipped (log line 165);
neither the CLI extension INSTALLs nor the pip install in `~/.lakehouse-env` was reached. This is an
upstream release asset name/format change, with no evidence of a Crostini-specific failure.

**Evidence:** a read-only `curl -sSIL` of the exact CLI URL reproduces the redirect to
`https://github.com/duckdb/duckdb/releases/download/v2.0.0/duckdb_cli-linux-amd64.zip`, then HTTP 404.
The [v2.0.0 release assets](https://github.com/duckdb/duckdb/releases/expanded_assets/v2.0.0) instead list
`duckdb-cli-linux-amd64.tar.gz` (hyphens and a tar.gz); a HEAD request to that versioned asset returns
HTTP 200. The [release metadata](https://api.github.com/repos/duckdb/duckdb/releases/tags/v2.0.0) publishes
its SHA-256 as `c6507206baf7793c6013dbd82368469a45f20dc0e17a6f92f204602f652ed2bc`.
`command -v duckdb` finds nothing, `duckdb --version` reports `command not found`, and
`~/.lakehouse-env/bin/python` is absent. Python import and extension compatibility remain untested;
`INSTALL delta` was not run (no CLI, and INSTALL writes to the extension cache). No bundle script,
sudo command, or install was run for this diagnosis.

**Proposed:** replace the obsolete zip URL and unzip step with the published Linux amd64 tar.gz.
Apply rule 9: stage the download and extraction under `assets/`, verify the archive against the
published SHA-256 for that exact release, run `gzip -t`, inspect the tar members before extracting,
and run the staged binary's `--version` and an in-memory `SELECT 1` before replacing
`~/.local/bin/duckdb`. Resolve one release tag and use it for both the asset and digest, so a new
`latest` cannot mix releases. A missing digest, failed lookup, bad archive or failed binary check
stops with a useful error and leaves any installed CLI intact; no unchecked fallback. Use the release
redirect for the tag, as elsewhere; if digest metadata is rate-limited, report that explicitly.

| Choice: which DuckDB CLI release setup installs | |
| --- | --- |
| A (recommended) | Keep following the latest stable release, using the current tar.gz asset name and the verification above. Preserves the bundle's current update policy; extension compatibility must pass the Chromebook checks before release. |
| B | Pin a reviewed release tag and its published SHA-256 in setup, with the same archive and binary validation. Updates become deliberate bundle changes; an older pin needs its own extension and Python compatibility checks. |

**Test:** stand-in downloads/metadata: a valid archive installs; 404, missing digest, checksum mismatch,
truncated archive, unexpected tar members and a binary that fails validation all stop before replacing
an existing CLI. Check a changing `latest` cannot mix the archive and digest from different tags.
In dev-test, keep the existing CLI/Python extension loads and DuckLake/Delta/dbt smoke checks; strengthen
the CLI check to print its version and run an in-memory query, and print Python's DuckDB version in the
import check so mismatches are visible. The lakehouse disk-report line already includes the CLI, venv
and extension cache; no new retained path is needed. Update `docs/init-checklist.md` with the verified
CLI download and failure guidance, and CHANGELOG under all four scripts when built. No new flag or
ODBC change; no Crostini workaround to document.

**To verify on the Chromebook:** after the chosen fix is built, the owner runs setup with
`install-lakehouse` twice: both reach the final summary, with no 404 and a validated CLI installed.
Read the new `.output` files; check `duckdb --version`, an in-memory query, CLI extension INSTALL/LOAD
for iceberg, ducklake, delta, httpfs, sqlite and postgres, and Python's DuckDB version and extension
loads in `~/.lakehouse-env`. Then run dev-test with `install-lakehouse`: FAIL 0, including DuckLake,
Delta reads and dbt Core; inspect any optional-feature WARNs. These install/test runs need the owner's
approval and have not been done as part of this plan diagnosis.

## Init, demo

Version bump only.

## Docs

`docs/init-checklist.md` (the `devclean` lines), `docs/crostini-gotchas.md` if item 2 turns up something
Chrome-on-Crostini specific, CHANGELOG (all four sections).

## Not bundle work, noted

- `~/##dev-setup-chromebook` (488 MB, Oct 27): an old copy of the repo in the home folder.
- `ddev-test`: the throwaway site from the v96 router check, still there Oct 27
  (`ddev delete -Oy ddev-test && rm -rf ~/ddev-test` frees its images as well).

## Choices to make

- [ ] Item 1: how setup knows the installed Cursor build (A: a recorded download URL/version, recommended)
- [ ] Item 2: what to clear in Linux Chrome's profile (A: only folders Chrome rebuilds, recommended)
- [ ] Item 3: a gone DDEV project's images (A: removed by `--run`, recommended)
- [x] Item 4: one instruction file for every agent (`AGENTS.md`, `CLAUDE.md` symlink) — done in this PR
- [ ] Item 5: DuckDB install failure — diagnosis, then the fix's choices
- [ ] Anything else for v98
