# dev-setup-chromebook v99 plan

Oct 31, 2026 · investigation of the v98 full setup run · **draft; owner choices pending**

## Scope

v99 follows the v98 release on `main` (6eb42ce, PR #11). This is an investigation and plan only:
no bundle script has been edited or executed, no package installed or downloaded, and no service
started for this investigation. The plan branch is `plan/v99`; implementation, after approval, belongs
on `release/v99`. The scripts and README remain at v98 in this PR.

Evidence is `assets/logs/dev-setup-20261031-194457.output`: 82,453 lines, approximately 10.8 MB.
All **L** references below refer to that local output file, not to source-code lines. Only searches,
counts and selected ranges were read; the full log is not committed. The owner ran:

```bash
./dev-setup-chromebook.sh install-all install-db-server install-lan-share install-models install-ollama-containers install-retro
```

The run stopped in install-agentic. Proposed work:

1. Bounded retries and timeouts for network operations across the bundle.
2. Continue independent optional stages after failure, record outcomes and return an honest status.
3. Contain apt's delayed-item warning flood without hiding failures.
4. Remove Playwright's misleading project-dependencies warning through a managed installer context.
5. Replace random-data pipelines that produce broken-pipe messages.
6. Make model examples reflect installed models and correct the Gemma secrets hint.
7. Let apt's sandbox read verified local .debs; use apt-get in unattended package operations.
8. Verify Antigravity's PATH behaviour; avoid speculative shell-profile surgery.
9. Keep other upstream notices classified, with functional checks instead of warning suppression.

Every item offers options, a recommended default and verification. **No choice below is approved yet.**
Disk/RAM guards, optional credentials, verification before replacement and Homebrew after Debian stay
requirements. This plan does not claim a successful full v98 run or any built/tested v99.

## Evidence and triage

Source references are to `dev-setup-chromebook.sh` at v98 unless another script is named. Most stacks
are top-level conditional blocks, not functions; the table says so explicitly.

| Finding / log lines | Root cause and evidence | Severity | Script / function or block | Proposed disposition |
| --- | --- | --- | --- | --- |
| Agentic pip failure, L82416–82453 | Temporal CLI and pip upgrade succeed. Pip resumes temporalio metadata once, then resets while fetching langgraph metadata. Unguarded pip returns nonzero under `set -e`; no stage boundary handles it. | **Fatal** | setup: `install-agentic`, source 7550–7591; `make_venv` | Items 1–2: bounded native and whole-command retries; failed stage recorded, later independent stages continue. |
| 64,364 delayed-item warnings, L13607–77970 | Font fetch goes Get → Ign → Get at L13530–13542; package config succeeds at L13593. Apt 3.0.3 emits its delayed acquisition queue warning repeatedly. Matches Debian #1111554. Browser downloads then succeed, L77971–77986. | **Upstream bug; real log-flood problem, nonfatal here** | setup: `install-playwright` → `npx ... install --with-deps` (6620) → sudo apt-get; upstream `pkgAcquire::Run` | Item 3: own dependency step with retries and narrow counted deduplication; preserve exit status and all other diagnostics. |
| Playwright warning box, L13354–13373 | `npx -y playwright@latest` runs outside a project with a Playwright dependency. This is the bundle's machine-level browser provisioning, not a failed project install. | **Cosmetic noise / bundle invocation issue** | setup: `install-playwright`, 6616–6635 | Item 4: small managed tools context under assets, resolve one release and use its CLI for both dependency and browser installs. |
| Broken pipes, L13163–13164, L13191–13192, L13203–13206 | `head -c` closes while `tr` still writes filtered `/dev/urandom`. SQL Server, Oracle and devsvc creation continue; no evidence of bad passwords. Pipeline status is fragile under pipefail and can also be hidden by outer printf/assignment. | **Real robustness bug; cosmetic in this run** | setup: `db_new_password` (4552), devsvc key loop (5550); same latent pattern in `ldap_random` / `ldap_new_password` (5055–5057), LDAP not selected | Item 5: finite, checked Python `secrets` generation, preserve formats and existing values. |
| Qwen skipped but recommended, L82196–82198, L82407–82413 | Guard estimates **9 GB remaining after the proposed pull**, below 10 GB; this is not a measurement of only 9 GB currently free. Model list correctly contains only two installed curated models, but closing examples are hardcoded. | **Real hint bug; disk skip is intended** | setup: `install-models`, `model_bytes`, `have_model`, 7473–7539 | Item 6: choose present generation-capable models; omit unavailable hints and keep reason for skip. Do not lower the guard automatically. |
| Symfony / Redis Insight unsandboxed notices, L785, L13277 | Verified .debs are inside `mktemp -d` directories (normally 0700), so `_apt` cannot traverse them; apt falls back to root. Both packages install. | **Real packaging-permissions issue; nonfatal notice** | setup: `install-symfony` (1867–1882), `install-redis` / Redis Insight block (5696–5713) | Item 7: private staging, validate first, then expose only the verified package through an apt-readable directory; retain `_apt` sandbox. |
| Antigravity “ERROR” information lines, L12759–12766 | The installer's Google logger is used before initialization; `I1031` messages describe successful operations and CLI installation succeeds. | **Upstream cosmetic noise** | setup: `install-antigravity`, vendor `curl ... \| bash` (3748) | Item 8: retain diagnostics and verify `agy`; item 1 checks download before execution. No blanket ERROR filtering. |
| Antigravity profile exports, L12760–12764 | Installer prepends `~/.local/bin` in both profiles. It does not prepend Homebrew or reverse Debian/Homebrew order. Targeted read confirms marked brew block in `.bashrc` 118–137, local-bin prepend at 177 and `.profile` 35. Duplicated PATH entries exist. | **Cosmetic duplication; no observed ordering conflict** | setup: `install-antigravity`; `brew_after_system` and marked Homebrew block (422–482) | Item 8: preserve current ordering, verify fresh-shell lookup and repeat-run behaviour; only use a documented vendor no-profile option if confirmed. |
| sdkmanager deprecation, L12787–12789 | SDK tooling advertises replacement Android CLI, after accepting licences/installing components. Not an installation failure. | **Upstream; ignore for v99 behaviour** | setup: Android common block (3857 onward), `sdkmanager` calls | Item 9: retain warning, existing SDK/build checks; migration is separate scope unless owner selects it. |
| npm deprecated packages, L12796–12804 | Transitive packages of global `eas-cli` installation (React Native / Expo mobile path), followed by “added 527 packages” at L12806. | **Upstream; track, no bundle dependency overrides** | setup: Android/mobile `install-mobile` / `install-rn` path | Item 9: keep package-manager diagnostics and Expo/EAS version checks; no claim of a security audit. |
| Brew Landlock warning, L1768, L12864, L78007, L82422 | Kernel exposes ABI 3; brew wants ABI 10 for network isolation of its build sandbox. Bottles install. It does not mean network connectivity failed. | **Upstream/platform limitation; ignore for install success** | setup: Java/Android, GitLab and agentic brew calls | Item 9: retain notice, no sandbox bypass or kernel change. |
| rdoc encoding notice, L5942; completion L5956 | RDoc scans a bundled http-parser test fixture whose contents resemble an invalid encoding name. Gem documentation continues and completes. | **Upstream cosmetic noise; ignore** | setup: `install-ruby`, `gem install jekyll bundler ...` (2155) | Item 9: retain gem/runtime checks. Optional `--no-document` only if owner wants to give up local RI docs. |
| apt's unstable CLI warning, L13317, L13321, L13325 | `devsvc_deb` redirects stdout while calling interactive-oriented `apt install`; stderr warns. mongosh, Database Tools and Compass install. | **Cosmetic noise / real script-interface cleanup** | setup: `devsvc_deb` (5849), `install-mongodb` | Item 7: use apt-get and consistent noninteractive/retry options; preserve installation errors. |
| No JRE during certificate configuration, L1352; triggers L1365 onward | ca-certificates-java configures before the JRE dependency, then reruns its trigger after Java arrives; certificate additions follow. | **Upstream package-order notice; ignore if checks pass** | setup: `install-java` → `install_jdk_and_java_home` (1428) | Item 9: existing Debian JDK checks plus Java trust-store check; no manual certificate reset. |
| CPU-only Ollama, L78140 | Ollama detects no NVIDIA/AMD GPU in ChromeOS Linux. This environment deliberately uses CPU inference. | **Expected upstream/platform notice; ignore** | setup: `install-ollama`, vendor installer (7056) | Item 9: retain existing API/model checks; do not promise GPU support. |
| Gemma asks for key in `.bashrc`, L81666–81667 | Old completion text bypasses the documented secrets.env → dev-init flow. No key is printed by this hint. | **Real documentation bug** | setup: `install-gemma` completion text (7423–7424) | Item 6: point to optional GEMINI_API_KEY in secrets.env and dev-init; do not require a key for local use. |
| HF skill / credential-helper hints, L81655–81662 | Upstream login succeeds. Optional skill and Git credential-helper integration are suggestions, not missing bundle components. | **Upstream; ignore** | setup: `install-gemma`, `hf auth login` (7414) | Item 9: retain optional-login semantics; no automatic skill install or Git credential change. |
| No final summary, log ends L82453 | Exit occurs before final `unlink_brew_openjdk`, package cleanup and closing hints. Existing DL_FAILED only tracks some downloads and cannot summarize an unhandled abort. | **Real reporting gap caused by fatal exit** | setup: finalization 11425 onward, screen recorder 29–78 | Item 2: stage ledger, incomplete-run summary and preserved exit code, including unexpected fatal exits. |

Routine skips are not defects: L1176 AArch64, L13199 LDAP, L13295 Elasticsearch, L13314 Milvus,
L13332 Atlas Local, L77998 Cypress, L78023 GitLab Runner, L78030–78031 Puppet/Chef were not requested
by these flags. Brew's “already installed and up-to-date” warnings (L113–L122), Debian t64 package
aliases and the mkcert CA import reminder (L129) are also expected. No independent OOM, ENOSPC,
checksum failure or other fatal error was found in the targeted diagnostic searches.

## Exact exit path and work not reached

Flag expansion at setup source 119–123 adds `install-agentic` from `install-all`. The script reaches
the top-level agentic block at 7550 after Ollama, Gemma and curated model pulls. `brew install temporal`
and `make_venv "$HOME/.agentic-env"` run, and the pip upgrade at 7573 succeeds (L82445, pip 26.2.2).
The separate, unguarded multi-package `pip install -U` at 7581–7587 then fails (L82453).

`set -e` is enabled at source 82. There is **no global `set -o pipefail`**: occurrences elsewhere are
inside generated helper heredocs or isolated subshells (e.g. the DuckDB downloader). The failing pip
command is a simple command, not a pipeline; pipefail is unnecessary for this exit. It is not an
`if` condition or protected with a status handler. There is no outer agentic failure collector or
finalization trap. The screen recorder preserves the child status (`script -e`, or PIPESTATUS[0]) and
does not resume the installer. The recorded output excludes its own parent's final notification.

Do not say “pip had no retries/timeouts”: the command supplies **no explicit** policy, but pip has
defaults and L82448–82450 proves one resume attempt for temporalio metadata. Its subsequent
langgraph metadata reset escapes to an OSError without a successful recovery. There is no traceback
or packet trace proving which peer reset the connection (server, intermediary, Wi-Fi, etc.). v93's
20-second curl/wget connection configuration (source 93–103) neither applies to pip nor bounds a
stalled response body. A larger pip retry number alone is insufficient for all such failures.

These selected stages were not reached **in this run**; this does not prove they were absent before it:

| Order | Remaining stage / flags | Work still needed | v98 setup source |
| --- | --- | --- | --- |
| 1 | `install-agentic` (partial) | Finish Python packages and import smoke; aliases `agentic` / `tsdb`; Langfuse compose and example config; FastMCP uv tool and MCP Inspector/cache. Temporal CLI and pip upgrade already ran. | 7581–7693 |
| 2 | `install-cloud` → `install-aws install-azure install-gcp install-vercel install-cloudflare` | AWS, Azure, Google Cloud, Vercel, wrangler installations/configuration. | 7704–7777 |
| 3 | `install-jev` | TypeSafe Claude Code plugin setup and instructions. | 7815–7841 |
| 4 | `install-iac` | HashiCorp Terraform, tflint/checksums and Bicep if Azure CLI is present. | 7848–7877 |
| 5 | `install-ansible-full` (expanded by `install-iac`) | pipx Ansible core + full community package, lint, Molecule, Docker SDK and collection handling. | 7898–7939 |
| 6 | `install-k8s` | kubectl, Helm, kind, k9s and shell completions. | 7953–7974 |
| 7 | `install-lan-share` → `install-lan` | Tailscale apt setup/tun mode, `lan` helper, address-book application, relay artifacts and sharing application. Tailnet login still belongs to init. | 8033–9215 (sharing from 8852) |
| 8 | `install-com` (expanded by `install-retro`) | Wine 64/32-bit, mingw-w64, widl, winetricks, COM prefix and configuration. | 9242–9324 |
| 9 | `install-retro` | DOSBox-X, QEMU, Open Watcom and guest/media helpers, including Delphi launchers; licensed media remain bring-your-own. | 9379–11287 |
| 10 | `install-herdr` (expanded by `install-all`) | Install/verify herdr if absent. | 11300–11328 |
| 11 | Finalization (base) | Final Homebrew JDK unlink, apt autoremove, closing summary and next steps. Earlier Java/Android unlink calls did run. | 11425 onward |

**Correction to the starting expectation:** `install-ollama-containers` already ran, within the Ollama
block **before** agentic. Source 7099–7107 writes the binding drop-in; L78143 explicitly reports
`/etc/systemd/system/ollama.service.d/dev-setup-containers.conf` and the container URL. Its network
behaviour still needs dev-test verification; do not list it as never run. `install-db-server`'s
InterBase/SQL Server/Oracle stages also preceded the failure. Later source blocks for
`install-cloudflared`, `install-hermes` and `install-openclaw` are not selected, so they are not missing
work for this invocation. `install-ansible-core` is not a separately requested stage; full contains core.

## 1. Bounded network retries across the bundle

**Found Oct 31 2026:** the agentic pip reset (L82448–82453); previous fixes already cover selected
downloads (`fetch_tgz`, DuckDB's verified downloader, some curl calls). The policy is inconsistent.

| Choice: reach of the retry change | |
| --- | --- |
| A (recommended) | Audit every network boundary in all four scripts and their generated launchers. Use small equivalent local helpers in the standalone scripts, package-manager native settings and bounded whole-command retries where needed. No fifth runtime file to fetch/source. |
| B | Patch only agentic pip, leaving the same failure mode in Gemma, lakehouse, pipx, brew, apt and demos. Smaller change; incomplete resilience. |
| C | Add a shared external shell library and make the four scripts depend on it. Less duplicated helper code, but changes the four-script distribution contract. |

**Proposed default for A:**

- One explicit attempt budget (three whole-command attempts, backoff 2 then 5 seconds, with the native
  retry counts documented so they do not multiply accidentally). Retry only safe/idempotent acquisition
  and install operations after transient transport failures. Never retry logins, key uploads, destructive
  database operations or remote writes blindly; init authentication keeps its current semantics.
- Pip: explicit `--retries 5 --timeout 60`, and `--resume-retries 5` when that pip supports it. Cover
  venv pip, pipx/runpip and subprocess pip via invocation-scoped settings. A bounded whole-pip-command
  retry covers resets escaping its native handling. Dependency conflicts, unsupported Python, invalid
  credentials, disk exhaustion and checksum failures are classified rather than endlessly retried.
- Apt: install one managed `/etc/apt/apt.conf.d/` policy early in setup with `Acquire::Retries "3";`
  and HTTP/HTTPS timeouts of 60 seconds; root apt and Playwright's sudo child must see it. Account for
  apt's existing internal retries (the font fetch already retried). Use apt-get's strict update error
  mode where a fresh index is required; don't mistake an update that kept stale indices for success.
  Keep the existing IPv4 workaround; retries do not replace it.
- curl/wget: connection timeout 20 seconds plus bounded retries and an idle/read timeout (60 seconds),
  with finite metadata request limits. Large artifacts get an appropriate transfer budget instead of
  a tiny overall timeout. Download into a fresh `.part`/temporary path in assets, validate archive/deb
  and checksum, then promote atomically. Never retry into a pipe that is already executing an installer.
  Fetch vendor scripts completely and check transport/status before running them. Check both sides of
  necessary pipelines explicitly or use pipefail locally after auditing those pipelines.
- Audit brew, npm/npx, uv, git clones, Composer, gems, Rust/Go fetches, SDK managers, Docker/Ollama pulls
  and Ansible Galaxy too. Prefer their supported retry/timeout knobs, with bounded retries around safe
  operations where those knobs do not cover failure. Document exceptions and use item 2's outcomes.
  Never kill dpkg midway as a generic timeout strategy or retry an entire setup/install stage blindly.
- Demo: cover `fetch_repo`, `fetch_subdir`, `fetch_file`, `apt_need` and generated launchers, preserving
  edited projects and failed downloads for diagnosis. Test: use the policy for acquisition in scratch
  projects, but **never retry failed assertions** into a pass. Keep existing test deadlines and counts.
  Init: bounded read-only API probes; rejected credentials remain skip/todo under existing rules.
- Helpers print a safe operation label and attempt number, not expanded commands, tokens, authorization
  headers or signed URLs. User curl/wget/proxy configuration remains respected. TLS checks stay on.

**Decision:** pending (recommend A).

**Test / dev-test proof:** fault-injection fixtures for the actual helpers: transient metadata/reset
failure then success; exhausted attempts; HTTP 404/auth failure; corrupt archive/checksum; stalled
response; old binary retained on failure. Assert finite attempts, correct status and no credentials
in output. dev-test checks the managed apt policy and existing selected tool/import checks, including
`pip check` for agentic. Exercise representative pip/apt/download/demo paths against a local fault
server, with no real credentials or system install. Verify generated launchers use the same policy.

**To verify on the Chromebook:** owner-approved rerun; loss/recovery during a controlled acquisition
must recover or produce one actionable failure. Large valid downloads must finish without arbitrary
size-based timeouts. No live network-disruption exercise is authorized by this plan PR.

## 2. Stage outcomes and the exit status

**Today:** an unguarded optional install kills the entire run, while several guarded installs only
print a NOTICE and can leave the final “complete” message optimistic. DL_FAILED covers only a subset.

| Choice: an optional, selected stage still fails after retries | |
| --- | --- |
| A (recommended) | Record failure, skip only dependent work, continue independent stages, print a final report, and exit nonzero if a requested installation failed. |
| B | Stop at the first selected-stage failure, but write an incomplete-run report naming work not reached. |
| C | Continue and return zero with notices only. Easy to overlook failures; not recommended. |

**Proposed:** track requested leaf stages as not-started/running/succeeded/failed/skipped, with safe
reason labels and exact rerun flags. Store a per-run TSV under `assets/logs`, using DEV_RUN_STAMP,
plus a readable closing summary. Missing optional credentials and deliberate disk/media/disabled
skips remain distinct from a failed download; report their reasons. They do not turn into fabricated
installation success. Do not depend on manually sourcing this TSV as shell code.

Keep fail-fast behaviour for failed base prerequisites, unsafe package state and invalid invariants;
still report the current stage and selected work not reached. On optional failures stop that stage's
dependent setup (e.g. no “agentic installed” message after pip/import failure), then continue cloud,
LAN, retro, etc. Preserve existing data and installed versions. Do not blindly run unsafe cleanup
after a foundational failure. Preserve signal exits (130/143), the original fatal status and the
screen recorder's status. Normal completed-with-failures summary must differ from clean completion.

Explicitly check/propagate each fallible operation. Bash disables errexit through a function invoked
as an `if`/`!`/`||` condition; wrapping existing bodies in `if stage_function` is not sufficient. Do
not implement a global `set +e`, an ERR trap that returns success, or automatic replay of side effects.

**Decision:** pending (recommend A, including nonzero final status).

**Test / dev-test proof:** offline stage harness injects failed agentic acquisition/imports, verifies
subsequent independent stages execute once, dependent actions do not execute and summary/status are
correct. Inject fatal base failure, interruption and reporting failure; original exit status survives.
On recovery a new run records success and does not keep stale failures. dev-test reports selected
stage failures as FAIL (not optional-credential WARN), quotes safe reasons for deliberate skips, and
continues checking tool functionality even when the last setup was incomplete. Historical failed
runs do not override newer successful outcomes. The ledger is supplementary evidence, not a substitute
for actual import, CLI or service checks. Include its disk footprint in the base disk report.

## 3. Apt's 64,364-warning flood

**Diagnosis:** L13531's Ign and L13542's second Get show a delayed/retried font fetch. L13593 confirms
configuration succeeded; L13607–77970 is one exact repeated warning. Current read-only dpkg metadata
reports apt/libapt-pkg7.0 3.0.3 and the font package installed. The log itself does not print apt's
version; current metadata corroborates, rather than proves, its version at the earlier run.

[Debian #1111554](https://bugs.debian.org/1111554) records this flood in apt 3.0.3, with the warning
moved to debug output in 3.1.8. [Apt 3.0.3's acquisition loop](https://sources.debian.org/src/apt/3.0.3/apt-pkg/acquire.cc/)
warns when an eligible delayed item stays idle after cycling its queue. The exact queue stall/network
trigger here is not logged; do not call this a broken font or claim that Acquire::Retries fixes it.

| Choice: contain the flood on supported Debian 13 | |
| --- | --- |
| A (recommended) | Separate browser dependency installation, keep apt retries, and stream-deduplicate only this known warning with a count. Apply the narrow filter to bundle-owned apt output and the Playwright dependency child. |
| B | Keep `--with-deps`; apply the same narrow filter to that command and other apt calls. Less control over apt options and dependency-step status. |
| C | Depend on a fixed apt from Debian's supported channels once available. Do not add testing/unstable sources or rebuild apt merely to silence this warning. Until then the flood remains. |

For A use the selected Playwright version's Debian 13 dependency definitions (item 4), including
fonts/xvfb; do not guess a partial list. Preinstalling just fonts may avoid this instance but cannot
prove other delayed items will not flood. Filter by the specific warning prefix and exact repeated
line, preserve the first occurrence and emit a repeat count; bound memory and stream other output.
Never pipe to `head`, drop every `W:`/stderr, or use a pipeline's filter exit status as apt's status.
Filter before terminal/screen recording so the warning cannot fill either output. A separate complete
unfiltered 64,364-line copy is not needed. This contains output volume; it does not repair apt's queue
or bound a CPU-side stall. Prefer a fixed apt if Debian provides it through the supported channels.
Abort/filter errors must not turn a failed install into success. Document the upstream diagnosis in
crostini-gotchas, identifying it as a Debian issue.

**Decision:** pending (recommend A).

**Test / dev-test proof:** feed a synthetic 64,364-repeat fixture plus unrelated warnings/errors
through the actual filter: one first line, repeat total, all unrelated lines and original command
status survive. With an unprivileged fake apt producer returning nonzero, setup records failure and
continues per item 2. dev-test checks font/xvfb package presence and launches Chromium/Firefox/WebKit;
package presence alone is insufficient. Owner checks the next setup output for bounded warning volume.

## 4. Playwright installation context and release identity

| Choice: avoid the project-dependencies warning | |
| --- | --- |
| A (recommended) | A minimal bundle-owned tools package under `assets/tools/playwright`, containing the installer dependency and lockfile; use its local CLI for OS deps and browsers. Projects continue to own their test-framework dependencies. |
| B | Keep npx's temporary package and document the warning as harmless. No extra tools package, but the warning remains. |

For A, resolve/update one Playwright version per setup run, record the version only after successful
installation, and keep the prior usable record on failure. Use supported dependency installation
and item 3's apt handling. Keep machine-wide browser caches in `~/.cache/ms-playwright`. Do not install
a test framework into the repository root or the user's projects to silence the warning. No system
global SDK is added for project application code. Browser downloads run as the user, not root, with
a bounded idle/download retry policy (e.g. PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT=60000).

Update dev-test's current `npx ... playwright@latest` lookup (2730) to use that recorded installer
release. A mutable `latest` lookup during a later test is not proof that its browsers match setup's.
Scratch test projects still install their own matching `@playwright/test`; MCP remains independently
managed. Keep old builds required by other projects; no `uninstall --all` cleanup.

**Decision:** pending (recommend A).

**Test / dev-test proof:** recorded release, installer CLI and scratch package agree; all three
bundled browsers and system Chrome run the links spec and Chromium writes a trace. A synthetic later
upstream release cannot change dev-test's selected version. Interrupted tools-package update keeps a
usable previous installation/record; failed browser provisioning never writes success. Two setup runs
must avoid the warning box and reuse already installed matching browsers. Include tools-package bytes
in Playwright's disk-report line and document the extra assets path.

## 5. Finite password generation, safe with pipefail

**Today:** DB/LDAP helpers put filtered infinite random input through head; devsvc interpolates it
inside `Dev_...9`. Without pipefail, head's success hides tr's failure. With pipefail, a direct
`ldap_random` assignment can fail, but outer printf or surrounding assignments can mask another
substitution's status. These pipelines therefore are not a reliable success contract in either mode.

| Choice: generate the same allowed password shapes | |
| --- | --- |
| A (recommended) | Use Debian Python's `secrets.choice` for an exact finite length; check generator status and validate shape/length before storing or passing the value. |
| B | Read bounded random batches and filter until enough allowed characters exist, checking each read. More shell code and edge cases. |

Use A for `db_new_password`, `ldap_random`, `ldap_new_password` and devsvc generated keys. Preserve
upper/lower/digit/symbol requirements and the current permitted alphabets, lengths and prefixes.
Do not print real generated secrets, rotate existing passwords or read credential files during
development verification. A CSPRNG failure must stop that credential-dependent operation explicitly.
Suppressing tr's stderr or adding `|| true` would hide errors instead of fixing the generator.

**Decision:** pending (recommend A).

**Test / dev-test proof:** isolated generation/validation fixtures under `set -e -o pipefail`, with
fake persisted values and a failing random provider; assert length/character classes, successful
status and empty stderr without printing generated strings. Rerun keeps configured values. Existing
DB/devsvc/LDAP authentication tests prove stored credentials still work on owner-approved runs;
they must never expose the values. LDAP gets coverage even though it was not selected in this log.

## 6. Honest model examples and the optional Google key

| Choice: model recommendations after a disk/network skip | |
| --- | --- |
| A (recommended) | Pick a generation-capable model confirmed present, preferring qwen3.5 only if available; otherwise use deepseek or installed Gemma, or omit generation examples. Embedding-only availability gets embedding examples. |
| B | Print all examples with an explicit “requires this missing model; not downloaded” label. Less helpful, but no implied availability. |

Do not silently pull qwen through a suggested command immediately after the disk guard skipped it.
Check capability as well as presence; qwen3-embedding is not a chat fallback. Keep the curated-model
record exact and preserve it if Ollama is unreachable. Use one confirmed snapshot/capability result
for the recorded model list and hints. Avoid stale fallback examples if every pull failed. Fix
Gemma's completion hint (L81666–81667) to direct optional GEMINI_API_KEY to
`~/.config/dev-init/secrets.env`, then dev-init; it must not tell users to put keys directly in
`.bashrc`. Init may still export settings through its existing managed flow.

**Decision:** pending (recommend A; secrets hint correction included).

**Test / dev-test proof:** fixture cases qwen absent/present, only embeddings, no model, server down,
Gemma present and qwen skipped for disk. Every suggested generation model is confirmed present and
has generation capability; no advice triggers a hidden download. Keep existing recorded-model and
model API checks. Verify the effective disk margin matches setup's configured/default policy instead
of inventing a lower margin. A text regression check confirms completion guidance uses secrets.env
and never requires credentials for local inference. Update checklist/examples accordingly.

## 7. Verified local .debs and apt's scripting interface

| Choice: let `_apt` read verified package files | |
| --- | --- |
| A (recommended) | Private download/verification first; stage only the verified .deb in a traversable dedicated directory (0755 directory, 0644 file) for apt-get, then clean up. Ensure parent paths are traversable too. |
| B | Keep root fallback and document the notice. No install failure, but avoids fixing the permission problem. |

A may expose the existing random temp directory only after validation, or use a controlled apt-readable
staging directory under assets if all its parents are accessible. Do not broaden `$HOME`, repository
or config permissions or disable `APT::Sandbox::User`. Check checksums where published and
`dpkg-deb --info` before staging; a partial/corrupt download never replaces the installed package.
Audit other local .deb paths as part of this work, including `devsvc_deb`. Switch bundle-owned
unattended apt operations to apt-get with noninteractive options and item 1's retry policy. Do not
suppress stderr as a way of removing the unstable-interface warning.

**Decision:** pending (recommend A).

**Test / dev-test proof:** mode/traversal and corrupt-package fixtures; nonzero apt status still
reaches the failure report. On an owner-approved machine run, Symfony, Redis Insight and MongoDB
clients install without `_apt` fallback/unstable-CLI notices. Keep `symfony version` and requirements,
Redis Insight package/launcher checks and MongoDB client checks; missing requested components are
FAIL, while explicitly disabled GUI components follow their existing skip policy. No need to reinstall
current .debs on every rerun merely to produce a quiet log. Disk reporting keeps package bytes in
their original stack; retained assets are reported separately.

## 8. Antigravity PATH and misleading error prefixes

The prepend observed at L12760 and L12762 moves only local-bin. It leaves Debian/Homebrew relative
order intact; there is no evidence it moves Homebrew ahead. The duplicate local-bin entries are
cosmetic. Subsequent Android/Flutter PATH additions also exist, so “brew after Debian” is the lookup
invariant to verify, not an assumption that these installer lines caused every PATH detail.

| Choice: profile ownership | |
| --- | --- |
| A (recommended) | Keep vendor profile behaviour unless a documented no-profile-update option is confirmed; verify idempotence and lookup order, retaining the marked in-place Homebrew block. Leave the upstream logger prefix visible. |
| B | Replace the vendor CLI installation path with bundle-owned verified binary installation and one managed PATH block. More maintenance; requires upstream asset/checksum and supported install-contract investigation first. |

Network policy still replaces unverified streaming execution at this call site with complete checked
fetch-before-run. Do not delete arbitrary PATH exports or rewrite `.profile` based only on matching
`~/.local/bin`. If a vendor no-profile switch is available, prefer it plus the bundle's already
configured local-bin; confirm support rather than inventing an environment variable. No global
ERROR/warning text filter: future real installer failures must remain visible and recorded.

**Decision:** pending (recommend A).

**Test / dev-test proof:** `agy --version`/existing CLI check; synthetic clean/repeated profile fixtures
prove Debian python/sqlite/java/binutils resolve ahead of Homebrew and `agy` remains discoverable.
Owner-approved fresh login and interactive-shell checks preserve their timing limits and current
tool-resolution tests; a hand-selected user override is WARN, missing installed CLI is FAIL. Second
setup run must not grow equivalent PATH lines indefinitely. Do not execute the owner's shell startup
files as part of this investigation or overwrite unrelated profile edits.

## 9. Upstream notices: retain evidence and check the installed tools

| Choice: sdkmanager, npm, brew, RDoc and other expected notices | |
| --- | --- |
| A (recommended) | Keep the notices and existing functional checks; document their meaning. No dependency overrides, new Android migration, kernel/sandbox bypass, automatic HF skill or credential-helper changes in v99. |
| B | Add Android CLI migration and/or remove Ruby local documentation (`gem --no-document`) as separate owner-approved scope. Verify compatibility and user tradeoffs first. |

The table above records each notice and its originating block. Add only useful guidance to docs;
do not match arbitrary English warning text as installation failure. A successful package-manager
exit is acquisition evidence, not proof every tool works. For Java's early certificate notice,
verify the resulting trust store; the later trigger is why no ordering fix is proposed. For npm's
deprecated transitives, track the parent release without forcing incompatible nested versions.

**Decision:** pending (recommend A).

**Test / dev-test proof:** retain Java version/compiler and trust-store checks, SDK package/build
checks, Expo/EAS CLI checks, Ruby/Jekyll smoke and Ollama API/model checks. No test should require
Landlock ABI 10 or treat CPU-only Ollama as FAIL. An optional missing HF skill remains informational.
If B is selected, add Android CLI licence/package parity and Ruby runtime checks appropriate to the
specific change; do not claim these migrations were tested by this log.

## Implementation and Chromebook acceptance (after owner approval)

- Create `release/v99` from the approved baseline; targeted edits only. Any script change bumps all
  four scripts and every version string to 99, README's current version to v99, and adds all four
  CHANGELOG entries (version bump only where appropriate). Retain dated/tagged design comments.
- Flags and expansions stay identical. Update dev-test checks and disk-report lines, init-checklist
  run order/network policy/secrets hints, README behaviour and assets paths, dev-demo docs if generated
  launchers/acquisition change, and crostini-gotchas for the apt/transport findings.
- Use focused fault-injection tests for transport/status handling; do not run real installers on a
  non-Chromebook or force the host guard. Before every push: bash -n all four scripts, shellcheck
  -S error and secret checks (CI gitleaks; local only if already available).
- After implementation, ask the owner before any setup/init/test/demo run or heavy-service test.
  For a targeted recovery, the selected work not reached can be covered by:

  ```bash
  ./dev-setup-chromebook.sh install-agentic install-cloud install-jev install-iac install-k8s install-lan-share install-retro install-herdr
  ```

  This still executes base setup and installs/changes services; it is a proposed future command,
  **not executed or approved for execution by this planning PR**. It does not retry the disk-skipped
  qwen model. Keep the disk guard unless the owner explicitly chooses otherwise.
- Full acceptance uses the original six flags on setup, then init, then dev-test with the same flags
  (initial init already precedes setup for secrets-template creation). Include ollama-containers in
  verification even though its setup step ran. Read new `.output`/`.log` files by path. Confirm the
  summary is reached, failures are visible, reruns are idempotent and dev-test FAIL is 0; only optional
  credential WARNs are acceptable. Never call the version confirmed before that Chromebook run.

## Open questions for the owner

1. Approve item 1 A's bundle-wide acquisition audit and local helper approach, or limit it to agentic?
2. Approve item 2 A: continue independent optional stages, then return nonzero for failed requested
   installs (with deliberate disk/media/credential skips reported separately)?
3. Approve items 3–4 A: own apt dependency step, narrowly counted warning deduplication and a minimal
   assets-based Playwright installer context/recorded release? Alternative keeps npx and its warning.
4. Approve items 5–7 A: finite random generation, present-model hints/secrets guidance and apt-readable
   verified .debs plus apt-get cleanup?
5. Approve items 8–9 A: retain Antigravity's profile behaviour after verification and defer Android
   CLI/RDoc changes, or select the broader alternatives?
6. After implementation, prefer targeted recovery first or a full rerun with the original flags?
   Qwen still needs more room or a separately chosen override; no automatic guard reduction is proposed.

## Primary references checked for the plan

- [pip options](https://pip.pypa.io/en/stable/cli/pip/): HTTP connection retries, socket timeout and
  incomplete-download resume retries are distinct controls.
- [apt.conf on Debian trixie](https://manpages.debian.org/trixie/apt/apt.conf.5.en.html): Acquire policy
  and config scope, including settings seen by root apt.
- [Debian apt flood report](https://bugs.debian.org/1111554) and
  [apt 3.0.3 acquisition source](https://sources.debian.org/src/apt/3.0.3/apt-pkg/acquire.cc/): upstream
  match and warning placement; no claim that retries repair the queue.
- [Playwright browsers](https://playwright.dev/docs/browsers): dependency and browser installation,
  per-release browsers and download timeout. Use the actual installed version's CLI/source for its
  dependency contract when implementing, not a guessed list or a mutable newer CLI.

Future plan changes: commit with `Co-authored-by: Codex <noreply@openai.com>`, push, and add a PR comment
describing the change so the GitHub discussion remains self-contained.
