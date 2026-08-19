# Agent Prompt — 20.9 Import-linter covers the whole tree; the firewall test plants in a temp tree

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.9 — Import-linter covers the whole tree; the firewall test plants in a temp tree, anchored to C-32 + C-34 + C-125 [D-VERIFIED] — audits/review-2026-08-19/B/observation-firewall.md §2 F2; audits/review-2026-08-19/B/tests-ci-tooling.md §2 P1-1 + §2 P2-15 + §6 recommendations 1 and 8; audits/review-2026-08-19/B/verdicts.md (the C-32 verdict, "Analyzed 90 files … Contracts: 4 kept, 0 broken", and the C-34 verdict, "2/12 false BROKEN"); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 rows 1.2 + 1.3 and §3 claim-table row 3 ("agents cannot import engine directly or transitively (import-linter enforced)" — UNDERMINED); anchors re-verified at HEAD `b809b19c` by the drafting session: `.importlinter:2-8` (six root packages; `orchestrator`/`api`/`eval`/`scripts`/`experiments` absent, `include_external_packages` unset), `tests/test_firewall.py:21-23`, `:41-47`, `:142-144`, `:213-215` (five fixed plant paths written into the live checkout, each removed in a bare `finally` at `:36-37`, `:60-62`, `:156-157`, `:224-225`), `:90` (the repo-wide `agents/` AST scan bans `numpy`/`torch` only), `:160-169` (the in-code comment that names the invisible `agents -> orchestrator -> engine` chain and fixes it for one subpackage), `:172-174` (the learned-only rglob), `agents/tactical/learned/__init__.py:19-21` (the same posture claim), `.gitignore:1-43` (no `_firewall*` pattern; `git check-ignore -v agents/_firewall_bad_import.py` exits 1), `CONTRIBUTING.md:60-62` ("it runs the same checks CI runs") and `:79-80` (the transitive-firewall invariant) against `.github/workflows/ci.yml:90-160` (the `frontend-e2e` Playwright job) and `scripts/check.sh:30-35` (why the journey is deliberately excluded), `.github/workflows/campaign-tier.yml:23-28` (the weekly campaign tier), `eval/validity.py:95` (`from api import replay_loader`), `eval/leak_test.py:60` + `eval/determinism_test.py:14` (`from tests._helpers.world_state import …`), `README.md:74` (the claim 20.12 restates). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-import-contracts-coverage`
**Depends on:** none (root)
**Section refs:** C-32 + C-34 + C-125 [D-VERIFIED] — audits/review-2026-08-19/B/observation-firewall.md §2 F2; audits/review-2026-08-19/B/tests-ci-tooling.md §2 P1-1 + §2 P2-15 + §6 recommendations 1 and 8; audits/review-2026-08-19/B/verdicts.md (the C-32 verdict, "Analyzed 90 files … Contracts: 4 kept, 0 broken", and the C-34 verdict, "2/12 false BROKEN"); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 rows 1.2 + 1.3 and §3 claim-table row 3 ("agents cannot import engine directly or transitively (import-linter enforced)" — UNDERMINED); anchors re-verified at HEAD `b809b19c` by the drafting session: `.importlinter:2-8` (six root packages; `orchestrator`/`api`/`eval`/`scripts`/`experiments` absent, `include_external_packages` unset), `tests/test_firewall.py:21-23`, `:41-47`, `:142-144`, `:213-215` (five fixed plant paths written into the live checkout, each removed in a bare `finally` at `:36-37`, `:60-62`, `:156-157`, `:224-225`), `:90` (the repo-wide `agents/` AST scan bans `numpy`/`torch` only), `:160-169` (the in-code comment that names the invisible `agents -> orchestrator -> engine` chain and fixes it for one subpackage), `:172-174` (the learned-only rglob), `agents/tactical/learned/__init__.py:19-21` (the same posture claim), `.gitignore:1-43` (no `_firewall*` pattern; `git check-ignore -v agents/_firewall_bad_import.py` exits 1), `CONTRIBUTING.md:60-62` ("it runs the same checks CI runs") and `:79-80` (the transitive-firewall invariant) against `.github/workflows/ci.yml:90-160` (the `frontend-e2e` Playwright job) and `scripts/check.sh:30-35` (why the journey is deliberately excluded), `.github/workflows/campaign-tier.yml:23-28` (the weekly campaign tier), `eval/validity.py:95` (`from api import replay_loader`), `eval/leak_test.py:60` + `eval/determinism_test.py:14` (`from tests._helpers.world_state import …`), `README.md:74` (the claim 20.12 restates)
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run lint-imports` prints `Analyzed 149 files, 741 dependencies` (HEAD prints `Analyzed 89 files, 379 dependencies`) with `Contracts: 4 kept, 0 broken`, both lines quoted in the PR; the three planted probes each print `Contracts: 2 kept, 2 broken` naming the chain; `uv run pytest tests/test_firewall.py -q` green with `git status --porcelain` empty afterwards; and `uv run pytest tests/test_firewall.py -q & for i in $(seq 12); do uv run lint-imports --no-cache; done` prints zero BROKEN (review-measured 2/12 false BROKEN at HEAD).

The repository's loudest architectural claim is enforced over 89 of its 383 tracked
`.py` files. `.importlinter:2-8` lists six root packages — `agents`, `engine`, `llm`,
`meetings`, `observation`, `training` — and grimp builds no nodes for anything else, so
the traversal dies at the first hop into a package it does not know. The review planted
`agents/_probe_orch.py` containing `import orchestrator.game` and got `Contracts: 4 kept,
0 broken` with `scripts/check.sh` fully green
(audits/review-2026-08-19/B/verdicts.md, the C-32 verdict; the same evidence in
audits/review-2026-08-19/B/observation-firewall.md §2 F2). The drafting session reproduced
it exactly at HEAD in a scratch copy: `Analyzed 90 files, 379 dependencies. Contracts: 4
kept, 0 broken`. `orchestrator/game.py:71-81` imports seven `engine` modules,
`eval/leak_scan.py:38-47` and `api/replay_loader.py` likewise, so `agents -> orchestrator
-> engine`, `agents -> api -> engine` and `agents -> eval -> engine` are all live
back-channels that no gate in this repo can see. The blind spot is known and written down
in-repo (`tests/test_firewall.py:160-169`) and was closed for exactly one subpackage —
`agents/tactical/learned/` — by a source scan; the top-level `agents/` scan at `:90` bans
only `numpy` and `torch`. Meanwhile `README.md:74`, `CONTRIBUTING.md:79-80`,
`docs/architecture.md:106` and `docs/reading-guide.md:30` all state the transitive
guarantee uncaveated, and the front-door rewrite is about to amplify it.

The fix is four lines of config and it makes the claim TRUE rather than softening it. The
drafting session measured the widened configuration against unmodified sources at HEAD:
`Analyzed 149 files, 741 dependencies. Contracts: 4 kept, 0 broken` — no existing import
breaks, and the run costs ~0.17 s against ~0.19 s today, so the gate pays nothing. The 149
reconciles exactly: 148 tracked non-test `.py` files under the ten roots (agents 22,
engine 10, llm 9, meetings 7, observation 6, training 35, orchestrator 8, api 8, eval 25,
scripts 18) plus one synthetic node grimp mints for `scripts`, which carries no
`__init__.py` and is therefore a namespace package (confirmed by a two-root control:
`api` + `engine` analyses exactly 18 files, `scripts` + `engine` analyses 29 for 28
files). With the roots widened, the planted probe becomes loud: `import orchestrator.game`
under `agents/` prints `Contracts: 2 kept, 2 broken` with the chain spelled out —
`agents._probe_orch -> orchestrator.game (l.1)` then `orchestrator.game -> engine.world
(l.81)` — and `import api.main` and `import eval.leak_scan` break the same two contracts
through their own chains. What stays outside the graph after this task is small, nameable
and closed by the second layer below: `experiments/` (49 tracked `.py`, the frozen
investigation tier that imports the inner packages by design —
`experiments/__init__.py:6-8`), `tests/` (184), and two loose generators
(`audits/workflows/extract_gameplay_facts.py`, `design/phase-12/gen_map_reference.py`).

The same file carries a second defect, and it is the one that costs time today.
`tests/test_firewall.py` plants five files at fixed paths INSIDE the live checkout
(`:21-23`, `:41-47`, `:142-144`, `:213-215`), each cleaned up in a bare `finally` rather
than a fixture. Any second process touching the checkout during those few seconds sees the
repository's most alarming possible output: the review measured 2 of 12 concurrent
`lint-imports` runs printing `Agents must not import engine BROKEN` against modules that
do not exist (audits/review-2026-08-19/B/tests-ci-tooling.md §2 P1-1; the same 2/12 in
audits/review-2026-08-19/B/verdicts.md's C-34 verdict). Worse, a SIGKILL or Ctrl-C during
the subprocess leaves the plant behind, and `.gitignore` has no `_firewall*` pattern
(`git check-ignore -v agents/_firewall_bad_import.py` exits 1 at HEAD), so `git add -A`
commits a file containing `import engine` and turns a flake into a permanently red
architectural gate. It also caps the cheapest available speed-up: the parallel-suite task
later in this phase cannot run `pytest -n auto` while five process-independent plants
collide worker-to-worker. The plant-detect-cleanup SHAPE is right and is kept —
"a gate that cannot fail is not a gate" (`tests/test_firewall.py:138-139`); only the location
moves.

Scope discipline: no source import moves in this task. If the widened roots surface a real
violation, that is a finding for the PR's Questions, not a silent fix — the candidate
edges the drafting session already looked at are `eval/validity.py:95`
(`from api import replay_loader`, legal: `eval` and `api` are both consumer-layer) and
`eval/leak_test.py:60` / `eval/determinism_test.py:14` importing `tests._helpers`
(invisible to grimp, since `tests` is not a root). `README.md` is 20.12's file; that task
restates the front-door claim in the wording this PR's measured output records. No prompt
template moves anywhere in this phase outside the single prompt-set bump, and this task
records nothing: it is a $0, committed-bytes-untouched config-and-test change.

**Files in scope:**
- .importlinter; (add orchestrator, api, eval, scripts to root_packages; contracts unchanged in intent)
- tests/test_firewall.py; (plant into a tmp_path copy with a generated linter config; the repo-wide AST scan covers agents/ at top level for orchestrator/api/eval imports)
- .gitignore; (the `_firewall*` plant pattern as a belt-and-braces guard)
- CONTRIBUTING.md; (the 'same checks CI runs' sentence made true: check.sh + the Playwright job)
- tests/experiments/test_torch_probe_excluded.py; (the second live-tree plant moves to tmp_path)

**Files NOT in scope:**
- README.md (20.12 restates the claim in verifiable shape, using the wording this task's PR records)
- agents/, orchestrator/, api/, eval/ source (no import moves; if widening the roots surfaces a real violation, STOP and report it under Questions)
- eval/leak_scan.py + eval/leak_test.py (the entitlement-scanner task owns the dynamic firewall; this task is the static one)
- docs/architecture.md + docs/reading-guide.md (the enforcement paragraphs are restated by their owning tasks from this PR's recorded wording)
- .github/workflows/ci.yml + scripts/check.sh (the job set is described in CONTRIBUTING, not changed; the parallel-suite task owns the pytest invocation)
- experiments/ (stays out of root_packages: 49 files of frozen investigation code that imports the inner packages by design; it is covered by the agents-side source scan instead)

**Definition of done:**
- [ ] Verify-then-fix, before any other edit: the widened root list is run once against unmodified sources (a scratch config plus `lint-imports --config`, so the repo is not edited yet) and the verdict recorded in the PR. The drafting session measured `4 kept, 0 broken`; if a real violation appears instead, STOP and report it under Questions rather than moving any import.
- [ ] `.importlinter` `root_packages` gains `orchestrator`, `api`, `eval`, `scripts`; the four contract sections are unchanged; `uv run lint-imports` analyses 149 modules (148 tracked non-test `.py` under the ten roots plus the synthetic node for the `__init__.py`-less `scripts` namespace package) against 89 at HEAD, and all four contracts still read KEPT. Both `Analyzed …` lines and both `Contracts: …` lines are quoted in the PR.
- [ ] A planted `agents/_probe_orch.py` containing `import orchestrator.game` — and, separately, `import api.main` and `import eval.leak_scan` — is reported BROKEN by `lint-imports`, with the transitive chain named; demonstrated in the PR and pinned as a parameterized planted leg in `tests/test_firewall.py` that runs against the temp copy, so a future narrowing of `root_packages` fails the suite instead of passing it silently.
- [ ] `tests/test_firewall.py` writes NOTHING under the checkout: all five plant sites move into a `tmp_path` copy of the source tree with the linter run there, cleanup happens in a `yield` fixture rather than a bare `finally`, and no path built from the repo root is passed to `write_text` anywhere in the file (assert by reading the diff; `git status --porcelain` is empty immediately after `uv run pytest tests/test_firewall.py`).
- [ ] The copy's linter config is DERIVED from the committed `.importlinter` — parsed, with only `root_packages` rewritten to the packages present in the copy — never a second hand-written copy of the contract sections, so a fifth contract added later is exercised by the planted legs automatically. The PR states which mechanism invokes the linter from the temp cwd.
- [ ] Concurrency pin, recorded in the PR: `uv run pytest tests/test_firewall.py -q` running while 12 serial `uv run lint-imports --no-cache` invocations poll prints zero BROKEN (the review measured 2/12 false BROKEN at HEAD). The rewritten legs are also worker-independent, so the later parallel-suite task inherits no fixed-path collision.
- [ ] The top-level `agents/` AST scan (`tests/test_firewall.py:90`) widens from `{numpy, torch}` to also ban `orchestrator`, `api`, `eval`, `scripts`, `experiments`, `audits`, `design` and `tests` — the second, grimp-independent layer — and a covering assertion pins the pair: every top-level directory holding at least one tracked `.py` file is either a `root_packages` entry read from the committed `.importlinter` or a member of the ban set, so a new top-level package must join one of the two lists to land. Both the widened scan and the covering assertion are green at HEAD (verified: no file under `agents/` imports any banned name today) and both have a planted-failure leg.
- [ ] `.gitignore` carries a `_firewall*` pattern with a one-line comment saying it is residue insurance from older checkouts, not a licence to plant in-tree; `git check-ignore -v agents/_firewall_bad_import.py` now exits 0.
- [ ] `CONTRIBUTING.md:60-62` states exactly what CI runs beyond `check.sh`: the `frontend-e2e` Playwright journey (`.github/workflows/ci.yml`, deliberately excluded from the script per `scripts/check.sh:30-35`, runnable locally with `cd frontend && npm run e2e`), and one clause noting the campaign tier is in neither — it runs weekly on `main` from `.github/workflows/campaign-tier.yml`. The invariant bullet at `:79-80` is left as written, and the PR records why it is now true as written.
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
Open a PR from branch `phase-20-import-contracts-coverage` with a title like `task 20.9: import-linter covers the whole tree; the firewall test plants in a temp tree`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C-32 + C-34 + C-125 [D-VERIFIED] — audits/review-2026-08-19/B/observation-firewall.md §2 F2; audits/review-2026-08-19/B/tests-ci-tooling.md §2 P1-1 + §2 P2-15 + §6 recommendations 1 and 8; audits/review-2026-08-19/B/verdicts.md (the C-32 verdict, "Analyzed 90 files … Contracts: 4 kept, 0 broken", and the C-34 verdict, "2/12 false BROKEN"); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 rows 1.2 + 1.3 and §3 claim-table row 3 ("agents cannot import engine directly or transitively (import-linter enforced)" — UNDERMINED); anchors re-verified at HEAD `b809b19c` by the drafting session: `.importlinter:2-8` (six root packages; `orchestrator`/`api`/`eval`/`scripts`/`experiments` absent, `include_external_packages` unset), `tests/test_firewall.py:21-23`, `:41-47`, `:142-144`, `:213-215` (five fixed plant paths written into the live checkout, each removed in a bare `finally` at `:36-37`, `:60-62`, `:156-157`, `:224-225`), `:90` (the repo-wide `agents/` AST scan bans `numpy`/`torch` only), `:160-169` (the in-code comment that names the invisible `agents -> orchestrator -> engine` chain and fixes it for one subpackage), `:172-174` (the learned-only rglob), `agents/tactical/learned/__init__.py:19-21` (the same posture claim), `.gitignore:1-43` (no `_firewall*` pattern; `git check-ignore -v agents/_firewall_bad_import.py` exits 1), `CONTRIBUTING.md:60-62` ("it runs the same checks CI runs") and `:79-80` (the transitive-firewall invariant) against `.github/workflows/ci.yml:90-160` (the `frontend-e2e` Playwright job) and `scripts/check.sh:30-35` (why the journey is deliberately excluded), `.github/workflows/campaign-tier.yml:23-28` (the weekly campaign tier), `eval/validity.py:95` (`from api import replay_loader`), `eval/leak_test.py:60` + `eval/determinism_test.py:14` (`from tests._helpers.world_state import …`), `README.md:74` (the claim 20.12 restates)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
