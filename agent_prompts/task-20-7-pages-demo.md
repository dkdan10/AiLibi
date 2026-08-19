# Agent Prompt — 20.7 The hosted demo: a GitHub Pages workflow for the static bundle + the owner's About checklist

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.7 — The hosted demo: a GitHub Pages workflow for the static bundle + the owner's About checklist, anchored to audits/review-2026-08-19/C/collated-portfolio.md §A3 (host the bundle; the two warts to fix first) and §A4 (About/topics/homepage — description `""`, topics none, homepage `null`, `has_pages: false`, verified via `gh` by four personas); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-0 rows 0.1 and 0.8; audits/review-2026-08-19/C/p3-frontend-product-engineer.md (the built bundle drove in a browser: 8.8 MB, 7 featured games, 204 JSON files, 5.2 s warm — and the Tournament tab's raw `<!DOCTYPE HTML PUBLIC …>` dump, plus the bundle README's baked `/Users/danielkeinan/…` path); audits/review-2026-08-19/C/x1-front-door-reproduction.md (the reproduction table's bundle row: 4.3 s, served and played; the same absolute-path wart); audits/audit-phase-20-planning.md §6 (the owner's About checklist text, verbatim); scripts/build_demo_bundle.py:410 (`samples_dir=samples_dir.resolve()`) and :580 (the generated README's "baked from" line interpolating that resolved path), :339-343 (the standing absence-is-a-404 precedent for the unscored set), :510-533 (`_assert_static_mode_compiled_in`, the compiled-in-marker pattern); tests/scripts/test_build_demo_bundle.py:537 and :548 (the two asserts that currently PIN the absolute path); frontend/src/components/TournamentDashboard.tsx:1045-1058 (the no-report panel; :1057 renders the raw transport string); frontend/src/api/client.ts:65 (`ApiError` folds the response body into its message) and frontend/src/store/tournamentStore.ts:32-33 (the store flattens it to `error.message`); docs/deployment.md:12-14 and :58 (the ONLY-sanctioned-artifact rule) and :84-85 (the "first-class 'no report' state" claim the review contradicts); .github/workflows/ci.yml:12-13 (least privilege) and :29-34 (the full-SHA pin convention and its worked example); .github/workflows/campaign-tier.yml:10-15 (why a separate workflow file rather than a job in ci.yml); frontend/e2e/bundle.spec.ts:15-22 (zero `/api` proven twice) and :167 (`AILIBI_DEMO_BUNDLE_DIR` reuses a prebuilt bundle); frontend/vitest.config.ts:24-26 (`environment: "node"` — no renderer, so a component render test is not available here). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-pages-demo`
**Depends on:** 20.2 (the spectator copy pass lands first — this task rewrites the same dashboard component's no-report panel, and the replacement wording has to be written in the cleaned product voice instead of re-introducing the audit dialect the copy pass just removed)
**Section refs:** audits/review-2026-08-19/C/collated-portfolio.md §A3 (host the bundle; the two warts to fix first) and §A4 (About/topics/homepage — description `""`, topics none, homepage `null`, `has_pages: false`, verified via `gh` by four personas); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-0 rows 0.1 and 0.8; audits/review-2026-08-19/C/p3-frontend-product-engineer.md (the built bundle drove in a browser: 8.8 MB, 7 featured games, 204 JSON files, 5.2 s warm — and the Tournament tab's raw `<!DOCTYPE HTML PUBLIC …>` dump, plus the bundle README's baked `/Users/danielkeinan/…` path); audits/review-2026-08-19/C/x1-front-door-reproduction.md (the reproduction table's bundle row: 4.3 s, served and played; the same absolute-path wart); audits/audit-phase-20-planning.md §6 (the owner's About checklist text, verbatim); scripts/build_demo_bundle.py:410 (`samples_dir=samples_dir.resolve()`) and :580 (the generated README's "baked from" line interpolating that resolved path), :339-343 (the standing absence-is-a-404 precedent for the unscored set), :510-533 (`_assert_static_mode_compiled_in`, the compiled-in-marker pattern); tests/scripts/test_build_demo_bundle.py:537 and :548 (the two asserts that currently PIN the absolute path); frontend/src/components/TournamentDashboard.tsx:1045-1058 (the no-report panel; :1057 renders the raw transport string); frontend/src/api/client.ts:65 (`ApiError` folds the response body into its message) and frontend/src/store/tournamentStore.ts:32-33 (the store flattens it to `error.message`); docs/deployment.md:12-14 and :58 (the ONLY-sanctioned-artifact rule) and :84-85 (the "first-class 'no report' state" claim the review contradicts); .github/workflows/ci.yml:12-13 (least privilege) and :29-34 (the full-SHA pin convention and its worked example); .github/workflows/campaign-tier.yml:10-15 (why a separate workflow file rather than a job in ci.yml); frontend/e2e/bundle.spec.ts:15-22 (zero `/api` proven twice) and :167 (`AILIBI_DEMO_BUNDLE_DIR` reuses a prebuilt bundle); frontend/vitest.config.ts:24-26 (`environment: "node"` — no renderer, so a component render test is not available here)
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run pytest tests/scripts/test_build_demo_bundle.py -q` green, including the out-of-repo bake (the generated README carries no absolute host path) and the planted leg where stripping the empty-state fragment from a synthesized `assets/*.js` makes the builder's compiled-in check RAISE; `cd frontend && AILIBI_DEMO_BUNDLE_DIR=<the built dir> npx playwright test e2e/bundle.spec.ts` green against the exact directory the workflow uploads; after the owner enables Pages, the workflow's own post-deploy step reports HTTP 200 for the deployment's `page_url` and the PR quotes it.

The one artifact in this repository that a stranger could actually look at is built, tested,
and unpublished. `scripts/build_demo_bundle.py` produces an 8.8 MB static directory — 7
featured games, 204 baked JSON files, a relative asset base — in about 4–5 seconds; two
reviewers served it and played it in a browser, and `frontend/e2e/bundle.spec.ts` drives the
BUILT output with every `/api` request aborted at the network layer
(audits/review-2026-08-19/C/p3-frontend-product-engineer.md; audits/review-2026-08-19/C/x1-front-door-reproduction.md).
Against that: `has_pages: false`, homepage `null`, description empty, no topics
(audits/review-2026-08-19/C/collated-portfolio.md §A4, verified through `gh` by four
personas). Every reader must clone ~256 MiB and install two toolchains to see anything move.
The frontend persona's sentence is the whole finding: for this audience the URL *is* the
project. This task publishes the artifact and hands the owner the five-minute checklist for
the repository card.

Hosting now is not work done twice. Pages rebuilds on push, so a future re-record refreshes
the demo for free (audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 0.8) — which is also
why the workflow belongs on `main` pushes and manual dispatch and nowhere else: a
`pull_request` trigger would hand a fork's head commit a deployment of the project's public
face.

Two warts have to go before the artifact is public. The first is the Tournament tab. The
bundle deliberately bakes no tournament report — the 9p2i one is the corpus, not a demo — so
the client 404s, exactly as it already does for the unscored set's missing rubric
(scripts/build_demo_bundle.py:339-343). But `ApiError` concatenates the RESPONSE BODY into
its message (frontend/src/api/client.ts:65), the store flattens that message to a string
(frontend/src/store/tournamentStore.ts:32-33), and the panel prints the string verbatim
(frontend/src/components/TournamentDashboard.tsx:1057) — so the reviewer's browser showed
`<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"…` inside the card. The designer ruling
here is that the absence signal STAYS a 404 and no payload gets baked to dodge it: GitHub
Pages answers a missing file with its own HTML page too, so a builder-side payload could not
have fixed the deployed case at all. The defect is that a card renders a server-supplied
document; the fix is that it never does. `docs/deployment.md:84-85` currently asserts the
Dashboard renders a "first-class 'no report' state" — after this task that sentence is true.

The second wart is that the generated bundle README bakes the builder's absolute home path
(`baked from /Users/danielkeinan/projects/AiLibi/replays/samples`) into the file
docs/deployment.md calls the only sanctioned public artifact — scripts/build_demo_bundle.py:410
resolves the directory and :580 prints it. The note's doctrine is right and stays: it names
the SOURCE and makes no claim about whether those bytes are public, because the script cannot
establish that. Only the rendering changes — a repo-relative path when the recordings live
inside the checkout, and no filesystem path at all when they do not — and a builder-side check
makes the class impossible to reintroduce in any text file the builder authors.

**Files in scope:**
- .github/workflows/pages.yml; (new: build the bundle on push to main, deploy to GitHub Pages)
- scripts/build_demo_bundle.py; (the relative-path README; a baked empty-state payload for the Tournament tab so the bundle never shows raw 404 HTML)
- tests/scripts/test_build_demo_bundle.py
- docs/deployment.md; (the Pages path as the sanctioned public artifact; the owner's one-time checklist: enable Pages, set About/description/topics/homepage — with the exact text from the planning audit)
- frontend/src/components/TournamentDashboard.tsx; (the bundle empty state when no report is served — a friendly card, not raw HTML)
- frontend/src/lib/copy.ts; (20.2 moved this surface's prose into the copy tree — the empty state's replacement strings are values here, not literals in the .tsx)

**Files NOT in scope:**
- README.md (20.12 adds the demo URL and the badges; this task adds no README text and no badge)
- frontend/e2e/bundle.spec.ts (it already proves zero `/api` requests against the built artifact — unchanged; reuse it via `AILIBI_DEMO_BUNDLE_DIR`, do not edit it)
- frontend/src/api/client.ts and frontend/src/store/tournamentStore.ts (the client seam and the store's error flattening are 20.16's region; this task sanitizes what the card renders, it does not retype the error)
- .github/workflows/ci.yml and campaign-tier.yml (read for convention only — the new workflow is its own file, per the reason campaign-tier.yml:10-15 records)
- docs/deployment.md's dangling `audit C-C-1/2/4` anchor line at :7 (a later docs-errata task owns it — leave it alone)
- docs/media/ and the hero capture re-record (a separate later task in this phase)
- any replay, report, or manifest bytes

**Definition of done:**
- [ ] `.github/workflows/pages.yml` builds `frontend/dist/demo-bundle` with `bash scripts/setup_env.sh` followed by `uv run python scripts/build_demo_bundle.py`, and deploys it with `actions/configure-pages` + `actions/upload-pages-artifact` + `actions/deploy-pages`; every action is pinned to a full commit SHA with the tag it resolved from in a trailing comment (the convention stated at .github/workflows/ci.yml:29-34); the workflow's top-level `permissions` is `contents: read` with `pages: write` and `id-token: write` granted ONLY to the deploy job; `concurrency` is set to a `pages` group with `cancel-in-progress: false`; the triggers are exactly `push` on `main` plus `workflow_dispatch`, and there is no `pull_request` trigger.
- [ ] The workflow gates on the artifact before it publishes it — a step running `uv run pytest tests/scripts/test_build_demo_bundle.py -q` ahead of the upload — and verifies it after: a final step that requests the deployment's `page_url` and fails on any non-200.
- [ ] The dashboard's no-report card renders NO server-supplied text: with `report === null`, `isLoading === false` and a non-null error, the panel shows only app-authored copy, and a repo grep confirms the transport string at TournamentDashboard.tsx:1057 no longer reaches the DOM. In a static build the guidance names the demo bundle (the featured games ship, the eval dashboard needs a tournament report, the repository has it), gated on `import.meta.env.VITE_AILIBI_STATIC_DATA` with a comment naming client.ts's sibling reader.
- [ ] That bundle-only sentence is proven to have survived dead-code elimination: `scripts/build_demo_bundle.py` asserts a short, stable fragment of it is present in the emitted `assets/*.js`, in the same place and shape as the existing `./data` marker check (scripts/build_demo_bundle.py:510-533), so a regression that deletes the designed empty state fails the BUILD instead of shipping. `tests/scripts/test_build_demo_bundle.py` pins both legs against a synthesized build directory: absent fragment raises, present fragment passes.
- [ ] The generated bundle README names its source as a repository-relative path when the recordings are inside the checkout, and names no filesystem path at all when they are not; the "does not judge whether they are public" sentence and the surrounding no-claim doctrine survive word for word. tests/scripts/test_build_demo_bundle.py's two asserts at :537 and :548 are REPLACED by assertions of the new rendering (not deleted), and the out-of-repo bake asserts the resolved absolute path is absent from the note.
- [ ] No text file the builder authors (the generated `README.md`, the ownership marker) contains an absolute host path: a builder-side check fails the build when one appears, and its perturbation leg is pinned in tests/scripts/test_build_demo_bundle.py.
- [ ] `docs/deployment.md` documents the Pages deployment as the sanctioned public route for the bundle (the live API's loopback posture and the :12-14 / :58 rules untouched and still true), corrects the :84-85 claim to state what the Dashboard tab now renders, carries the owner's one-time checklist copied verbatim from `audits/audit-phase-20-planning.md` §6 (enable Pages with the workflow as source; the ≤350-character description; the twelve topics; homepage = the Pages URL), and states how to re-verify a deployment — the `page_url` request, and re-running the bundle browser spec against the built directory with `AILIBI_DEMO_BUNDLE_DIR`, noting plainly that that spec serves a directory and does not drive a remote URL.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-pages-demo` with a title like `task 20.7: the hosted demo: a github pages workflow for the static bundle + the owner's about checklist`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/C/collated-portfolio.md §A3 (host the bundle; the two warts to fix first) and §A4 (About/topics/homepage — description `""`, topics none, homepage `null`, `has_pages: false`, verified via `gh` by four personas); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-0 rows 0.1 and 0.8; audits/review-2026-08-19/C/p3-frontend-product-engineer.md (the built bundle drove in a browser: 8.8 MB, 7 featured games, 204 JSON files, 5.2 s warm — and the Tournament tab's raw `<!DOCTYPE HTML PUBLIC …>` dump, plus the bundle README's baked `/Users/danielkeinan/…` path); audits/review-2026-08-19/C/x1-front-door-reproduction.md (the reproduction table's bundle row: 4.3 s, served and played; the same absolute-path wart); audits/audit-phase-20-planning.md §6 (the owner's About checklist text, verbatim); scripts/build_demo_bundle.py:410 (`samples_dir=samples_dir.resolve()`) and :580 (the generated README's "baked from" line interpolating that resolved path), :339-343 (the standing absence-is-a-404 precedent for the unscored set), :510-533 (`_assert_static_mode_compiled_in`, the compiled-in-marker pattern); tests/scripts/test_build_demo_bundle.py:537 and :548 (the two asserts that currently PIN the absolute path); frontend/src/components/TournamentDashboard.tsx:1045-1058 (the no-report panel; :1057 renders the raw transport string); frontend/src/api/client.ts:65 (`ApiError` folds the response body into its message) and frontend/src/store/tournamentStore.ts:32-33 (the store flattens it to `error.message`); docs/deployment.md:12-14 and :58 (the ONLY-sanctioned-artifact rule) and :84-85 (the "first-class 'no report' state" claim the review contradicts); .github/workflows/ci.yml:12-13 (least privilege) and :29-34 (the full-SHA pin convention and its worked example); .github/workflows/campaign-tier.yml:10-15 (why a separate workflow file rather than a job in ci.yml); frontend/e2e/bundle.spec.ts:15-22 (zero `/api` proven twice) and :167 (`AILIBI_DEMO_BUNDLE_DIR` reuses a prebuilt bundle); frontend/vitest.config.ts:24-26 (`environment: "node"` — no renderer, so a component render test is not available here)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
