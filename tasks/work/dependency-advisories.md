# Update affected dependencies with verified use and build behavior

**Status:** done

## Outcome

Resolve current dependency advisories with targeted compatible updates and
verify the application's build and browser journey on the resulting lockfiles.

## Evidence

On 2026-09-05, `npm audit --json` reports five affected transitive packages:
`@xmldom/xmldom`, `brace-expansion`, `browserslist`, `nanoid`, and `postcss`.
The dependency tree places xmldom under Pixi, brace expansion under ESLint,
Browserslist under Babel, and PostCSS/nanoid under Vite. Inspect Python's locked
runtime and development dependencies against the current advisory service too.

## Acceptance

- [x] Record advisory sources, installed use, and deliberate update decisions.
- [x] Resolve fixable advisories without broad unrelated dependency upgrades.
- [x] Locked installation, frontend build and browser journey work; full project
  gate passes and any remaining advisory is explicitly dispositioned.

## Constraints

Work on `codex/cleanup`; follow `docs/architecture.md` Packages. No changes to
gameplay, prompt bytes, recorded evidence, or live-provider calls. Keep the exact
Playwright/browser pin unless an advisory actually requires changing it.

## Expected scope

`frontend/package-lock.json`, `frontend/package.json` if necessary, `uv.lock` and
`pyproject.toml` if the Python audit finds affected dependencies, this card, and
directly necessary compatibility fixes after consumer inspection. Root owns this
batch; other agents own application implementation.

## Record impact

None. Dependency maintenance must preserve recorded gameplay semantics.

## Validation

Run `npm audit --json`, `npm ls` for affected packages, and a pinned `pip-audit`
tool over `uv export --locked` output. Install from the updated lock, run the
frontend checks and `npm run e2e`, then `bash scripts/check.sh` at the combined
batch gate. Compare before/after audit responses; do not add a network-dependent
test to the offline gate.

## Results

The current audit on 2026-09-05 found five npm package findings and six Python
advisories across two packages. Targeted compatible updates now produce zero
known findings from `npm audit --json` and `pip-audit==2.9.0` over the locked
runtime and dev export. This is a dated database result, not a guarantee that
dependencies have no undiscovered defects.

| Package | Locked change | Use / advisory |
| --- | --- | --- |
| xmldom | 0.8.13 → 0.8.15 | Pixi dependency; application code does not create XML entity references. [Advisory](https://github.com/advisories/GHSA-6gmq-8vp8-gcm6) |
| brace-expansion | 5.0.6 → 5.0.9 | ESLint glob processing. [Advisory](https://github.com/advisories/GHSA-rgw5-rvv9-x895) |
| Browserslist | 4.28.2 → 4.28.9 | Babel build targets; bundled browser datasets updated as required by its dependency ranges. [Advisory](https://github.com/advisories/GHSA-c83g-rgw3-j3cx) |
| nanoid | 3.3.12 → 3.3.18 | Vite/PostCSS dependency; no application generator calls. [Advisory](https://github.com/advisories/GHSA-2v37-7h3g-55p8) |
| PostCSS | 8.5.15 → 8.5.28 | Builds local CSS; the application does not accept uploaded CSS. [Advisory](https://github.com/advisories/GHSA-fxqj-rqcc-2cmp) |
| idna | 3.13 → 3.15 | HTTP client domain handling; provider addresses are operator configuration. [Advisory](https://github.com/advisories/GHSA-65pc-fj4g-8rjx) |
| Starlette | 1.0.0 → 1.3.1 | FastAPI foundation; application has no direct form parser, HTTPEndpoint, StaticFiles, or reconstructed-URL authorization use. [Form limits](https://github.com/advisories/GHSA-82w8-qh3p-5jfq), [URL validation](https://github.com/advisories/GHSA-86qp-5c8j-p5mr) |

No direct npm versions or Playwright/browser pin changed. Python minimum
constraints keep the two transitive fixes through future resolution; FastAPI
and every other Python version remained pinned. `uv lock` and locked sync
passed. The portfolio agent's fresh source copy completed setup with these
locks and fresh isolated caches, then reproduced the documented fake game and
verified all 100 canonical replays offline. Build and browser verification passed; the combined project gate is recorded below.

The clean copy also built and served the static demo, and its browser journey
passed 11 tests with three opt-in media captures skipped. The subsequent audit
gate repair explicitly declares the already-locked `markdown-it-py==4.0.0` as a
dev dependency; that declaration changes no installed package version.

Reproduce the Python audit with `uv export --locked --no-hashes --format
requirements.txt --output-file /tmp/ailibi-requirements.txt`, then
`uvx pip-audit==2.9.0 -r /tmp/ailibi-requirements.txt --no-deps --disable-pip`.
The exported lock contains the transitive runtime/dev dependencies already;
the audit tool is isolated, not added as an application dependency.

### Combined verification and review

The final `bash scripts/check.sh` run passed: 6,409 Python tests (20 optional
skips, three expected failures), 455 frontend tests, strict typing, lint,
formatting, import boundaries, 390 historical contracts/prompts, and the build.
`bash scripts/verify_samples.sh` verified all 100 canonical recordings. No
canonical recording or historical report bytes changed. Logs: `/tmp/ailibi-cleanup-batch2-check-final.log` and `/tmp/ailibi-cleanup-batch2-samples.log`.

Independent review: Code-review agent; dependency graph, fixed advisory ranges, and clean-install/browser evidence checked.
Implemented and verified for cleanup; the owner's final Claude review and merge
remain pending. This work does not adopt an experimental behavior.
