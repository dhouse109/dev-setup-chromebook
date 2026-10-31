# dev-setup-chromebook v98 plan

Oct 31, 2026 · started Oct 27 (items 1-3, from the v97 Chromebook runs) · items 4-6 added Oct 30 · all choices made; fresh-instance finding recorded Oct 31 · **final**

## Scope

v98 follows v97. Base: v97 (tag `v97`, PR #8 merged Oct 27 2026 as 7424727), confirmed on a Chromebook
Oct 27 (dev-test PASS 126, FAIL 0, WARN 0 with `install-editors install-web`; setup ran to its summary;
every hand check passed). The owner has closed the scope at items 1-6; nothing else joins v98.

1. **Setup stops downloading Cursor on every run** (install-cursor): the same fix v97 made for the Lazarus
   debs and Chrome's .deb.
2. **What fills Linux Chrome's profile** (base, `devclean`): the old profile was about 1 GB (5.5 MB in
   the existing cleanup folders); it has since been cleaned. Report the largest parts and add only
   documented shader caches to cleanup; the fresh instance has no size breakdown of the old profile.
3. **Images left by DDEV projects that are gone** (base, `devclean`): the images DDEV builds per project
   stay after the project is deleted.
4. **One instruction file for every coding agent** (repo only, no script change): `CLAUDE.md` becomes
   `AGENTS.md`, with `CLAUDE.md` a symlink to it, so Codex CLI reads the same rules as Claude Code; a new
   section says what an agent may do when it runs locally on a Chromebook. **Done in this plan's PR.**
5. **DuckDB failed to install** (install-lakehouse): diagnosed locally Oct 30; an obsolete CLI asset URL
   returns 404. Pin CLI, Python and ODBC to DuckDB 1.5.6 pending downstream support for 2.0.
6. **Executable script modes** (repo only): the four scripts are committed as 100644; running
   `chmod +x` locally leaves mode changes at every checkout.

Each item lists the choices offered and the owner's decision. All are made, and nothing else joins
v98, so the plan is final. This is the approved plan, not an implemented or Chromebook-tested v98.

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

**Decision (owner, Oct 30 2026): A.** Record the installed download URL/version under `assets/`.

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

**Read-only follow-up (Oct 30 2026):** the requested
`du -sh ~/.config/google-chrome/* ~/.config/google-chrome/Default/* | sort -h | tail -20`
now reports only `4.0K ~/.config/google-chrome/Crash Reports`, with
`du: cannot access '/home/dhouse109/.config/google-chrome/Default/*': No such file or directory`.
`du -sh ~/.config/google-chrome` also reports 4.0K. **Owner clarification (Oct 31):** the old profile
was cleaned; this is a fresh instance. The old 997 MB's contents cannot be reconstructed from this
measurement, so do not attribute it to models, components or shaders without evidence. The new
cleanup list below is based on Chromium's documented cache paths, not the old profile's sizes.

**Proposed (A):**

- `devclean --where` shows the user-data directory's and each profile's largest parts. Missing
  profiles on a fresh instance are normal; report what exists without launching Chrome.
- Keep the existing `~/.cache/google-chrome` cleanup and per-profile `Cache`, `Code Cache`, `GPUCache`
  and `Service Worker`. Add only `ShaderCache`, `GrShaderCache` and `GraphiteDawnCache` directly under
  `~/.config/google-chrome`, when present and only while Linux Chrome is closed. Chromium's
  [browser path definitions](https://chromium.googlesource.com/chromium/src/+/e156ccff5dc879607ca48817e638e361406e4170/chrome/browser/chrome_content_browser_client.cc)
  identify these as shader disk caches in the user-data directory; its
  [GPU cache implementation](https://chromium.googlesource.com/chromium/src/+/HEAD/gpu/ipc/host/gpu_disk_cache.cc)
  initializes a shader cache backend, and its
  [tests](https://chromium.googlesource.com/chromium/src/+/HEAD/gpu/ipc/host/gpu_disk_cache_unittest.cc)
  cover creating and clearing it. They can be rebuilt on use; no size saving is promised on this
  fresh instance, where they are absent.
- Use these exact paths, not a recursive `*Cache*` match. Downloaded components/models and all other
  unexplained folders stay report-only in v98. Never touch bookmarks, sign-ins, history, settings,
  extensions or the profile itself.

| Choice: what to clear | |
| --- | --- |
| A (recommended) | Add the three documented shader caches above to the existing Chrome cleanup, only while Chrome is closed; report all other profile space. |
| B | Report only (`--where`); clearing stays by hand. |

**Decision (owner, Oct 30 2026): A.** Clear only folders Chrome rebuilds, while Chrome is closed.

**Test:** a stand-in Chrome directory contains the exact allowed cache paths and unrelated profile
data: only the allowed paths are reported as clearable and removed; absent caches are harmless;
while Chrome is running, cleanup is skipped. The size report still lists unexplained folders.

**To verify on the Chromebook:** `devclean --where` lists the profile's largest parts; with Linux Chrome
closed `devclean --run` frees roughly what the report said; Linux Chrome still opens with its profile, and
dev-test's Puppeteer check passes. After normal graphics use, Chrome can recreate the shader caches
it uses; an unused backend's cache need not reappear. On the fresh instance, absent caches mean 0 B
to clear, not a failed check.

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

**Decision (owner, Oct 30 2026): A.** `devclean --run` removes a gone project's built images.

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
HTTP 200. The [release metadata](https://api.github.com/repos/duckdb/duckdb/releases/tags/v2.0.0) carries
GitHub's SHA-256 asset digest; DuckDB publishes no checksum file among this release's assets.
`command -v duckdb` finds nothing, `duckdb --version` reports `command not found`, and
`~/.lakehouse-env/bin/python` is absent. Python import and extension compatibility remain untested;
`INSTALL delta` was not run (no CLI, and INSTALL writes to the extension cache). No bundle script,
sudo command, or install was run for this diagnosis.

**Downstream evidence (read-only checks, Oct 30 2026):** artifact availability and dependency metadata
can be checked without installing anything. They do not prove that queries, extension loads or dbt
models run; those checks are still required on the Chromebook.

- **Extensions:** HEAD requests (`curl -sSIL`, following redirects) to
  `https://extensions.duckdb.org/v2.0.0/linux_amd64/<name>.duckdb_extension.gz` returned:

  | Extension artifact name | Final HTTP status |
  | --- | --- |
  | iceberg | 200 |
  | ducklake | 200 |
  | delta | 200 |
  | httpfs | 200 |
  | sqlite_scanner | 200 |
  | postgres_scanner | 200 |

  These are the published artifacts for all six setup INSTALLs (`sqlite` and `postgres` resolve to
  the scanner names). Availability is confirmed, not LOAD/runtime compatibility.
- **Python package:** [PyPI's DuckDB 2.0.0 metadata](https://pypi.org/pypi/duckdb/2.0.0/json) reports
  `requires_python: >=3.11.0` and a non-yanked wheel named
  `duckdb-2.0.0-cp312-abi3-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl`.
  The CPython stable ABI (`cp312-abi3`) covers both cp312 and standard cp313; a separate cp313-named
  wheel is not needed. Free-threaded Python is excluded by the
  [Python migration guide](https://duckdb.org/docs/2.0/clients/python/migration). Thus a wheel exists
  for the bundle's Debian Python 3.13 as well as 3.12; no pip installation was performed.
- **dbt Core adapter:** [PyPI's latest dbt-duckdb metadata](https://pypi.org/pypi/dbt-duckdb/json) reports
  version `1.11.1`, with `duckdb>=1.0.0`, `dbt-core>=1.8.0`, `dbt-adapters<2,>=1` and
  `dbt-common<2,>=1`. The optional `md` extra has `duckdb==1.5.5`; setup does not request that extra.
  The normal requirement permits 2.0, but this is not a claim that the adapter has been tested on it.
  DuckDB 2.0's Python migration guide lists removed result/relation methods and changed result handling;
  the adapter's smoke test must pass. Keep classic `dbt-core<2` explicit when implementing the fix.
- **Delta writer:** [PyPI's latest deltalake metadata](https://pypi.org/pypi/deltalake/json) reports
  `1.6.6` and `requires_dist: arro3-core>=0.5.0, deprecated>=1.2.18`, plus optional pandas and pyarrow
  extras. There is no DuckDB requirement: delta-rs is a separate engine, not a DuckDB binding.
  That removes a package-version constraint, but DuckDB's `delta` extension must still read the
  Delta tables it writes, and the existing read/append/time-travel tests remain necessary.
- **dbt Fusion (dbt v2):** no explicit DuckDB 2.0 support statement was found in the checked
  [dbt changelog](https://github.com/dbt-labs/dbt/blob/main/CHANGELOG.md) or
  [connection docs](https://docs.getdbt.com/docs/local/connect-data-platform/duckdb-setup).
  The changelog's engine-specific evidence says "via duckdb 1.5.4"; dbt's own v2 version number
  does not establish DuckDB 2.0 support. DuckDB's
  [Fusion article](https://duckdb.org/2026/09/22/dbt-fusion) says it ships a "pinned DuckDB version".
  The connection docs also say the bundled driver "does not support loading DuckDB extensions" and
  describe a separate `dbc` driver for that. Fusion uses its own driver, not setup's CLI or Python
  package. Its shared-file interoperability and extension/catalog behaviour are unconfirmed; do not
  silently add `dbc` or replace its driver as part of this download fix.
- **ODBC (separate flag):** [latest release metadata](https://api.github.com/repos/duckdb/duckdb-odbc/releases/latest)
  identifies `v2.0.0.0`. Its
  [tagged version source](https://github.com/duckdb/duckdb-odbc/blob/v2.0.0.0/src/duckdb/src/function/table/version/pragma_version.cpp)
  says `#define DUCKDB_VERSION "v2.0.0"` and `DUCKDB_SOURCE_ID "d54cbbe3df"`.
  HEAD on setup's existing `releases/latest/download/duckdb_odbc-linux-amd64.zip` returns 200.
  This driver embeds a separate DuckDB engine; it is not the CLI failure. The bundle's CSV DSN is
  in-memory, but sharing a new 2.0-format file with a pinned 1.x CLI/Python would be incompatible.
  A matching older release also exists: the
  [v1.5.6.0 metadata](https://api.github.com/repos/duckdb/duckdb-odbc/releases/tags/v1.5.6.0) reports
  tag `v1.5.6.0`, asset `duckdb_odbc-linux-amd64.zip`, and a populated `digest` field with
  `sha256:` followed by 64 hex digits. HEAD on
  `https://github.com/duckdb/duckdb-odbc/releases/download/v1.5.6.0/duckdb_odbc-linux-amd64.zip`
  returns HTTP 200. Its
  [tagged version source](https://github.com/duckdb/duckdb-odbc/blob/v1.5.6.0/src/duckdb/src/function/table/version/pragma_version.cpp)
  says `#define DUCKDB_VERSION "v1.5.6"` and `DUCKDB_SOURCE_ID "069cc9f9b5"`.

**Recommendation:** hold the CLI and Python on the last stable 1.x release until the remaining
downstream behaviour is confirmed. This is a conservative inference from the incomplete Fusion/dbt
evidence, not a demonstrated failure of all downstream tools on 2.0. The
[DuckDB migration guide](https://duckdb.org/docs/2.0/operations_manual/migration) confirms that new
2.0-format files cannot be read by older engines; existing older-format files retain their format.
[PyPI](https://pypi.org/pypi/duckdb/json) currently lists `1.5.6` as the highest non-yanked stable 1.x.
Its [CLI release](https://github.com/duckdb/duckdb/releases/tag/v1.5.6) still publishes
`duckdb_cli-linux-amd64.zip` (HEAD 200), and its
[Python release](https://pypi.org/pypi/duckdb/1.5.6/json) has cp312 and cp313 manylinux x86_64 wheels.
The same six extension HEAD requests under `v1.5.6/linux_amd64` all return 200.

**Proposed, whichever choice:** setup defines one exact DuckDB version (without the tag's leading `v`),
uses `v${version}` for the CLI release and installs `duckdb==${version}` in `~/.lakehouse-env` in the
same pip transaction as dbt-core, dbt-duckdb and the other lakehouse packages. Keep that exact constraint
on reruns/upgrades; a resolver conflict is an error, never permission to drift. Compare the staged CLI's
reported version and Python's `duckdb.__version__` with the selected version before declaring success.
Use the archive name/format published for that tag: the old zip for 1.5.6, the new tar.gz for 2.0.0.

Before any CLI download, ask `~/.local/bin/duckdb --version` for its installed version. If it reports
the selected version, print that DuckDB CLI is current and skip the download, metadata lookup and
replacement; otherwise download and validate the selected release. Continue the remaining lakehouse
steps in either case. The exact pip `duckdb==${version}` requirement is already a no-op when satisfied.
This follows item 1 and v97's Lazarus/Chrome fix: the second setup run downloads no CLI archive.

Apply rule 9: read **GitHub's asset digest** at run time from
`repos/duckdb/duckdb/releases/tags/v${version}` release metadata. Use `gh api` when gh is logged in,
with an unauthenticated `curl` fallback; never print credentials or make a GitHub login/token required.
Select the exact asset's `digest` field and require a valid `sha256:` value. DuckDB publishes no checksum
file for these releases; never hardcode a digest, including for a pinned version. Stage the download
and extraction in a temporary directory under `assets/`, removed on success and on failure by a
cleanup trap (preserve any existing traps), so no staging files remain beside the logs. Compare its
SHA-256, then run `unzip -t` or `gzip -t` as appropriate,
inspect archive members before extracting, and run the staged binary's `--version` and in-memory
`SELECT 1` before replacing `~/.local/bin/duckdb`. Use the same tag for the asset and digest. A missing
digest, rate limit, failed lookup, bad archive or failed binary check stops with a useful error and
leaves any installed CLI intact; no unchecked fallback.

| Choice: DuckDB version for the lakehouse stack | |
| --- | --- |
| A (recommended) | Pin the CLI and pip duckdb to the last 1.x release (`1.5.6` at this check) until the downstream pieces support 2.0 and the shared-file checks pass. One exact version drives both installs; read GitHub's digest at run time. This fixes the download without introducing the major-version migration. |
| B | Adopt `2.0.0` for both CLI and pip duckdb, using the new tar.gz and run-time GitHub digest. The six extensions and Python wheel exist and the normal adapter requirement permits it, but accept only after dbt Core, Delta, and Fusion/shared-file checks pass; establish Fusion's actual driver compatibility or an explicit older storage-format policy before sharing files. No independent floating `latest`/pip upgrade. |

**Decision (owner, Oct 30 2026): A.** Pin CLI and Python to `1.5.6` using one version variable.

| Choice: ODBC driver while CLI/Python are pinned to 1.x | |
| --- | --- |
| A (recommended) | Pin the driver to the same DuckDB version: `v1.5.6.0`, asset `duckdb_odbc-linux-amd64.zip`. Use the shared version variable to derive the ODBC tag (`v${version}.0` for this release), so the bundle's CLI, Python and ODBC use DuckDB 1.5.6. Verify the exact asset's GitHub digest at run time with the same gh/curl policy. |
| B | Leave ODBC on latest (currently built on DuckDB 2.0). Document in `docs/init-checklist.md` that files it writes in the new 2.0 format cannot be opened by the 1.x CLI or Python; the existing CSV DSN remains in-memory. |

**Decision (owner, Oct 30 2026): ODBC A.** The matching release exists, so pin it to DuckDB 1.5.6.
Define the shared version before either flag's block, so `install-db-extra` works on its own without
enabling `install-lakehouse`. Stage and verify the ODBC zip, validate its archive and expected driver
before replacement, and clean up on success/failure as for the CLI. Skip the driver download and print
that it is current when an in-memory ODBC version probe reports the selected engine; otherwise
install the pinned driver. Record the engine version with
an in-memory ODBC `SELECT version()` check in dev-test; keep registration and CSV-query checks and
the existing `/opt/duckdb-odbc` disk-report line. Document the shared pin in `docs/init-checklist.md`.

**Test:** stand-in downloads/metadata: a valid archive installs; 404, missing digest, checksum mismatch,
truncated archive, unexpected tar members and a binary that fails validation all stop before replacing
an existing CLI. Cover zip and tar.gz; logged-in `gh api`, unauthenticated curl fallback and rate limits;
never accept metadata for a different tag/asset. A conflicting pip requirement must fail rather than
install a different DuckDB. Check reruns keep the exact version in both installs. First run with no
CLI: one download; second run with the selected CLI installed: no download or digest lookup and an
explicit current/skip message; a different version or a failed version probe downloads and validates
the selected release. Confirm the staging directory is removed after success and each failure path.
For ODBC A, check the tag/asset derives from the shared version, digest verification precedes driver
replacement, a second run skips the matching driver download, and a standalone `install-db-extra`
selects the same engine without installing lakehouse.
In dev-test, keep the existing CLI/Python extension loads and DuckLake/Delta/dbt smoke checks; strengthen
the CLI check to print its version and run an in-memory query, and print Python's DuckDB version in the
import check so mismatches are visible. Add a FAIL check that normalizes the leading `v` from the
CLI version and compares it with `~/.lakehouse-env`'s `duckdb.__version__`; report both values and
FAIL on a missing command/import or a mismatch. Exercise matching, mismatched and missing versions.
The lakehouse disk-report line already includes the CLI, venv
and extension cache; no new retained path is needed. Update `docs/init-checklist.md` with the verified
CLI download, shared ODBC pin and failure guidance, and CHANGELOG under all four scripts when built.
No new flag or Crostini workaround to document.

**To verify on the Chromebook — A (chosen):** setup with `install-lakehouse` twice (also
`install-db-extra`, since ODBC A is chosen); both reach the summary, and the second run downloads no
DuckDB CLI or ODBC archive and prints that they are current. Then dev-test with `install-lakehouse install-db-extra`:
FAIL 0, including CLI/Python version equality and the pinned ODBC engine/CSV checks. Read the new
`.output` files. No bundle install/test run has been done as part of this plan diagnosis.

**To verify on the Chromebook — B (not chosen):** the same two-run and FAIL 0 checks with 2.0,
plus Fusion's actual `SELECT version()` through a model and a scratch database written/read across
CLI, Python and Fusion in both directions under `assets/`. A Fusion WARN does not confirm 2.0
interoperability; establish its driver compatibility or an explicit older storage-format policy.

## 6. Executable script modes (repo only)

**Found Oct 30 2026:** `git ls-files -s` records all four bundle scripts as `100644`. The owner runs
them with `chmod +x`, so `git diff --summary` shows `100644 => 100755` for setup, init, test and demo
after a checkout. Those local mode changes are present during this plan work and remain uncommitted.

**Proposed:** record that the scripts are executable in Git, so a normal checkout is ready to run and
the owner's executable bits agree with the index. No script contents change for this item.

| Choice: executable modes | |
| --- | --- |
| A (recommended) | Commit all four scripts as `100755` when this choice is approved and built. Checkouts preserve the executable bits and stop showing these local mode changes. |
| B | Leave the repository at `100644`; the owner sets `git config --local core.fileMode false` in this checkout. Git ignores local executable-bit differences, but fresh clones still need `chmod +x`. |

**Decision (owner, Oct 30 2026): A.** Commit all four scripts as `100755` during the build.

**Test:** for A, `git ls-files -s` shows `100755` for exactly the four scripts and the diff contains
only their mode changes for this item. For B, confirm the local setting; no repository mode change.

**To verify on the Chromebook:** after the chosen change, checkout/pull no longer shows the four
scripts modified solely because they are executable. No modes or Git configuration are changed by
this plan-only update.

## Init, demo

Version bump only.

## Docs

`docs/init-checklist.md` (the `devclean` lines and shared DuckDB pin/download verification),
`docs/crostini-gotchas.md` only if a Chrome-on-Crostini difference is found, CHANGELOG (all four sections).

## Not bundle work, noted

- `~/##dev-setup-chromebook` (488 MB, Oct 27): an old copy of the repo in the home folder.
- `ddev-test`: the throwaway site from the v96 router check, still there Oct 27
  (`ddev delete -Oy ddev-test && rm -rf ~/ddev-test` frees its images as well).
- The DuckDB pin is one variable; revisit adopting 2.0 when dbt Fusion states DuckDB 2.0 support.

## Choices made — final

All choices are settled; item 2 records the fresh-instance finding and its bounded cleanup list.

- [x] Item 1: A — record the installed Cursor download URL/version
- [x] Item 2: A — clear only folders Chrome rebuilds, while Chrome is closed
- [x] Item 3: A — `--run` removes a gone DDEV project's built images
- [x] Item 4: one instruction file for every agent (`AGENTS.md`, `CLAUDE.md` symlink) — done in this PR
- [x] Item 5: A — pin CLI/Python to 1.5.6; ODBC A — matching v1.5.6.0 release exists, pin it too
- [x] Item 6: A — commit all four scripts as 100755 during the build
- [x] Nothing else joins v98 — scope closed by the owner
