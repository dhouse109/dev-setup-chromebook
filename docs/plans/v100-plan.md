# dev-setup-chromebook v100 plan

Nov 1, 2026 · **draft for owner review; planning only**

## Scope and baseline

The owner accepted v99 in [PR #13](https://github.com/dhouse109/dev-setup-chromebook/pull/13)
with two known non-credential WARNs: offline Inspector cache availability and environmental disk
headroom below the model reserve. The final test returned to the prompt without Ctrl+C.
Inspector ENOTCACHED pre-existed v99 and is not classified as a v99 regression.

This plan starts on `plan/v100`; implementation belongs on `release/v100` after the owner approves
the plan and v99 is merged. The draft PR targets `main` and contains only this plan. It does not
implement a fix, bump script versions, authorize running setup/init/test/demo, or authorize merging
either PR. Disk reserve changes, cache purges and unrelated stack changes are outside item 1.

## 1. Inspector offline cache coherence

### Evidence

Repo-relative local evidence (raw logs remain local):

- `assets/logs/dev-setup-20261101-115925.output`: setup reaches all 79 selected stages.
- `assets/logs/inspector-cache-20261101-115925.log`: real online and offline tools/call both exit 0
  and return result 5 during setup's warm-up.
- `assets/logs/dev-test-20261101-130201.log`: global Inspector's real call passes, but the real
  `npx --offline` call exits 1 with ENOTCACHED for the package's registry response.
- The completed full test reports PASS 594, FAIL 0, WARN 11, SKIP 1. This issue is one of the two
  non-credential WARNs explicitly accepted for v99.

An installed global executable and an immediately successful warm-up do not establish that a
later npx invocation can resolve the same package from the same cache without registry access.
No cache deletion, Node version mismatch or registry change has yet been proven as the cause.

### Setup versus dev-test comparison

| Input | Setup warm-up in v99 | Dev-test in v99 | Finding / missing evidence |
| --- | --- | --- | --- |
| Node | Node stage selects installed LTS; run log reports v26.13.0 | Managed nvm default activation; run log reports v26.13.0 | Recorded versions match. Capture the executable identity at each actual probe before excluding a shim/PATH difference. |
| npm / npx | Run log reports npm 11.20.0; npx follows selected Node | Run log reports npm 11.20.0; npx follows activated default Node | Recorded npm versions match. Probe-level executable/config identities are not recorded. |
| Global Inspector | `npm install -g @modelcontextprotocol/inspector@latest` | Global version check reports 2.13.0, then a successful global tool call | Global installation and npx's execution cache are separate checks. |
| Online package spec | `npx --yes @modelcontextprotocol/inspector ...` | No online acquisition in the offline assertion | Global install uses explicit `@latest`; the warm-up uses the bare package. |
| Offline package spec | `npx --offline @modelcontextprotocol/inspector ...` | Same bare package, same real tools/call operation | Both use the bare spec, not explicit `@latest` or an exact version. Test each form; do not assume identical resolution/cache identity. |
| Registry | Inherited effective npm configuration; no effective registry snapshot | Error names the public npm registry; effective configuration not captured | The error's URL does not prove warm-up used identical configuration. Compare registry origin and scoped-registry selection without reading or publishing credentials. |
| Cache path | Inherited effective npm cache; not recorded at warm-up | Inherited effective npm cache; not recorded at the assertion | Compare canonical cache paths locally. Do not infer the cache path from npm's debug-log path. Public reports contain only matching/different results or repo-relative paths. |
| Working directory | Caller directory; no managed Inspector cwd | Test scratch directory | npm project configuration and local dependencies can differ. Capture this context and normalize bundle-owned probes. |

Code reviewed: Inspector block in `dev-setup-chromebook.sh`; environment activation and Inspector
assertion in `dev-test-chromebook.sh`; `tests/warm-inspector-cache.py`. The installed FastMCP CLI
builds a bare Inspector spec by default and appends an explicit version when its Inspector-version
option is supplied. Verify that supported option again against the installed CLI before building
any launcher; do not assume a different invocation uses the same npm cache.

### Investigation before implementation

1. At setup warm-up and immediately before the offline assertion, compare Node/npm/npx executable
   identity and versions, exact package spec, effective registry/scoped registry, effective cache
   path and working-directory category. Use allowlisted individual properties, not config dumps,
   credential files, environment dumps or verbose request headers. Keep any absolute path comparison
   local; publish only equality/results and repo-relative evidence paths.
2. In isolated bundle-owned test caches, compare the bare spec, explicit `@latest` and one exact
   installed version. For each, run the real online tools/call once, then the identical invocation
   with strict `--offline`, both immediately and from the later test context. Record producer status
   and result 5, not only a package listing or a no-op command.
3. Repeat the successful pair after the intervening full workflow and a new terminal/Linux session.
   Inspect cache existence/identity without deleting the user's cache. Correlate any difference with
   the recorded context before attributing the failure to npm eviction, version drift or a bug.

These real commands require individual owner approval. This draft performs no new warm-up,
installation, cache mutation or service start.

### Recommended change, pending owner approval

Use an exact Inspector release and an explicit, bundle-owned execution-cache context for the
bundle's offline contract. Keep the general global CLI available separately.

1. After a successful global install/update, read its installed Inspector version once. Record that
   exact version for the warm-up and dev-test; do not resolve mutable `latest` during dev-test.
2. Warm `@modelcontextprotocol/inspector@<recorded-version>` through the real npx tools/call using
   an explicit cache under `assets/tools/mcp-inspector/npm-cache` and a stable bundle-owned cwd.
   Verify the identical strict-offline call before publishing a new successful record. Retain the
   previous usable record on acquisition or verification failure.
3. Make dev-test use that same spec/cache context with `--offline`, preserving full producer output,
   status and the result-5 assertion. Missing/mismatched cache remains an honest WARN; the assertion
   must never download or repair its own prerequisites. `--prefer-offline` is not sufficient.
4. Preserve the FastMCP use case: provide a small generated launcher or documented invocation that
   passes the same cache and recorded Inspector version using FastMCP's supported version option.
   Set npm cache/offline options only for that command and its children. Do not rewrite user/global
   npm configuration or claim an unqualified default FastMCP invocation shares the managed cache.
5. Record only safe version/spec/result metadata under `assets/tools/mcp-inspector`; keep diagnostics
   under `assets/logs`. Include the managed cache in the agentic disk-report line and document its
   offline contract. Avoid duplicate downloads where npm can safely reuse content.

This is the recommended design, not a root-cause claim or an approved implementation. If the
investigation shows a smaller explicit spec/context correction reliably fixes the original default
cache path, present that evidence before adding a managed cache or launcher. Do not replace the npx
test with the passing global executable and call cache coherence fixed.

### Validation and completion criteria

- An isolated cold cache produces an honest offline failure; online warm-up followed by strict
  offline real tools/call returns 5 with status 0 from both managed contexts.
- Bare, explicit `@latest` and exact-version comparisons identify which context/spec is actually
  used. A deliberate cache/context mismatch is diagnosed without a test-time download.
- Repeat setup reuses the recorded release/cache when current; a failed update preserves the last
  usable record and never prints a success claim for a failed warm-up.
- A new terminal/Linux session and the full intervening workflow retain the offline result. Verify
  the documented FastMCP invocation separately; UI/global CLI success alone is insufficient.
- Keep all flags/expansion logic identical across the four scripts. At implementation time bump all
  four to v100 and update CHANGELOG, README, init checklist and disk-report/docs as appropriate.
- Before each push run all-four Bash syntax and error-level ShellCheck plus secret checks. Use
  focused regressions for spec/context/status propagation and owner-approved targeted real runs,
  followed by the owner-approved full acceptance route.
- Public PR comments contain counts, results and repo-relative paths only; no PIDs, hardware or
  kernel details, auth status, home-directory paths or raw logs.

### Primary references

- [npm exec: package resolution and strict offline caching](https://docs.npmjs.com/cli/v11/commands/npm-exec/)
- [npm package specifications](https://docs.npmjs.com/cli/v11/using-npm/package-spec/)
- [npm configuration precedence](https://docs.npmjs.com/cli/v11/using-npm/config/)

npm documents that npx uses npm exec's cache and strict offline mode fails when required cached
data is missing; configuration can vary by command context. Those contracts motivate the
comparison above, but do not establish which input caused the recorded ENOTCACHED.
