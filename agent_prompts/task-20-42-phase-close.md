# Agent Prompt — 20.42 THE PHASE CLOSE (owner): the close audit, the gate rerun, the ledger, the next decision

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.42 — THE PHASE CLOSE (owner): the close audit, the gate rerun, the ledger, the next decision, anchored to [L] the prior close's pattern, reprised — audits/audit-phase-19-close.md §1 (the whole gate re-run at close HEAD by the verifiers' actual paths, and its close-found F1: the documented restore and the documented gate are mutually exclusive at two legs), §2 (every contract verified-or-deviation-recorded, none silent), §3 (the before/after story in generated numbers only), §4 (the routed decision, recommendation first, the committed cells doing the arguing), §6 (provenance + the frontier), §7 (the reproduction block); audits/review-2026-08-19/D/FINAL-synthesis.md §4 (the roadmap this phase implements; the wave-2 close-gate list; the pre-registered primary bar), §4 "Later, or never" (the balance-lever ruling: a separate chartered wave with its own record), §6 (the owner's decision framing and the four-week collapse plan), §8 (the re-record ledger); audits/review-2026-08-19/A/collated-findings.md G-5, G-8, G-13, G-15, G-22, G-40 (the six excluded balance levers and their measured evidence); audits/audit-phase-20-preregistration.md (the bars and the decision rule this close reads back); AGENTS.md:76-110 (the seven craft rules every ledger row is audited against); scripts/check.sh:15-21 (the default gate's seven legs); pyproject.toml:74-76 (`addopts = "--strict-markers -m 'not campaign'"` and the registered `campaign` marker — the opt-in tier); .github/workflows/ci.yml + .github/workflows/campaign-tier.yml (the two standing jobs; the Pages workflow is added earlier this phase); docs/artifacts.md:95 (the counted `audits/` registry row, stated as 4.8 MB / 98 files, matching `git ls-files audits | wc -l` = 98 at HEAD); tests/scripts/test_verify_ml_evidence.py:1400 (`test_every_counted_registry_row_matches_the_index`, unmarked and therefore in the DEFAULT tier) via scripts/verify_ml_evidence.py:2162 (`"audits/": (("audits",), ())`) and :2174-2201 (`inventory_problems` — the document's stated count against the git index); scripts/compute_next_task.py:94 (`compute_frontier`, the frontier cross-check); README.md:82-84 and :107 (the two living project-status/roadmap sentences — re-locate by the `## Project status` heading, since the front-door rework and the results pass both restructure this section before the close); tasks/phase-19.md:3 (the STATUS-banner exemplar). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-phase-close`
**Depends on:** 20.6 (the front-door fact check must already be green on the vote-correctness truth-up before the close can quote it as a passing leg), 20.10 (the corpus acceptance gate must reject a truncated replay before the close re-runs the validity legs over the recorded sets), 20.11 (the in-vent legality guards are the last engine-rule change, so the close's byte-identity leg runs after them), 20.17 (the close runs the documented restore and the documented gate in one session — the pair the prior phase close recorded as mutually exclusive; the hermeticity fix is what makes this close's rerun quotable at all), 20.18 (the parallel default tier is the invocation the close quotes, and its wall clock is a before/after row), 20.37 (the graduation sweep is the last change to production bytes, so the close verifies the tree it leaves behind), 20.39 (the hero media is a ledger row the close re-verifies against the deployed bundle), 20.40 (the curated review index publishes the finding-to-outcome map the close's ledger mirrors), 20.41 (the tail-truth pass is the last documentation change — bannering a front door that still carried an uncheckable claim would close the phase on the defect class it opened against)
**Section refs:** [L] the prior close's pattern, reprised — audits/audit-phase-19-close.md §1 (the whole gate re-run at close HEAD by the verifiers' actual paths, and its close-found F1: the documented restore and the documented gate are mutually exclusive at two legs), §2 (every contract verified-or-deviation-recorded, none silent), §3 (the before/after story in generated numbers only), §4 (the routed decision, recommendation first, the committed cells doing the arguing), §6 (provenance + the frontier), §7 (the reproduction block); audits/review-2026-08-19/D/FINAL-synthesis.md §4 (the roadmap this phase implements; the wave-2 close-gate list; the pre-registered primary bar), §4 "Later, or never" (the balance-lever ruling: a separate chartered wave with its own record), §6 (the owner's decision framing and the four-week collapse plan), §8 (the re-record ledger); audits/review-2026-08-19/A/collated-findings.md G-5, G-8, G-13, G-15, G-22, G-40 (the six excluded balance levers and their measured evidence); audits/audit-phase-20-preregistration.md (the bars and the decision rule this close reads back); AGENTS.md:76-110 (the seven craft rules every ledger row is audited against); scripts/check.sh:15-21 (the default gate's seven legs); pyproject.toml:74-76 (`addopts = "--strict-markers -m 'not campaign'"` and the registered `campaign` marker — the opt-in tier); .github/workflows/ci.yml + .github/workflows/campaign-tier.yml (the two standing jobs; the Pages workflow is added earlier this phase); docs/artifacts.md:95 (the counted `audits/` registry row, stated as 4.8 MB / 98 files, matching `git ls-files audits | wc -l` = 98 at HEAD); tests/scripts/test_verify_ml_evidence.py:1400 (`test_every_counted_registry_row_matches_the_index`, unmarked and therefore in the DEFAULT tier) via scripts/verify_ml_evidence.py:2162 (`"audits/": (("audits",), ())`) and :2174-2201 (`inventory_problems` — the document's stated count against the git index); scripts/compute_next_task.py:94 (`compute_frontier`, the frontier cross-check); README.md:82-84 and :107 (the two living project-status/roadmap sentences — re-locate by the `## Project status` heading, since the front-door rework and the results pass both restructure this section before the close); tasks/phase-19.md:3 (the STATUS-banner exemplar)
**Complexity:** Small
**Record impact:** post-record — the close verifies and banners the tree the adopting record left; it moves no rendered prompt byte, no detector output and no replay byte.
**Measurement:** `bash scripts/check.sh` green at close HEAD in a clean worktree, quoted leg by leg, plus `uv run pytest -m campaign`, `bash scripts/fetch_evidence.sh` followed by `uv run python scripts/verify_ml_evidence.py --complete`, `bash scripts/verify_samples.sh`, `uv run python scripts/check_doc_facts.py` and the Pages deploy job on the close commit — every leg green or recorded as a named finding; every number in the close audit's before/after table equals a committed pin or a command reproduced in its own method section.

Phase 20 dispatched 41 contracts; this is the 42nd and it is the only one whose job is to
distrust the other 41. The convention the prior two closes established is that a merge is not a
verification: the phase-18 close found real defects inside otherwise-green merges, and the
phase-19 close's own first `bash scripts/check.sh` run at close HEAD exited 1 and then found a
second facet under `mypy` — the F1 recorded at `audits/audit-phase-19-close.md` §1, where the
documented `fetch_evidence.sh` restore and the documented gate turned out to be mutually
exclusive. That finding is this phase's Task 20.17, which means the close is now re-running the
exact pairing that was broken the last time anyone tried it. Re-running is the point.

The gate this close re-runs is not the gate the phase started with. The default tier became
parallel and lost most of its wall clock; the env surface became hermetic; import-linter's
contracts were widened past the six root packages that left `agents/_probe_orch.py` importing
`orchestrator.game` at `4 kept, 0 broken` (C-32, [D-VERIFIED] in
`audits/review-2026-08-19/D/FINAL-synthesis.md` §2 row 3); the leak scanner started checking
entitlement rather than shape, so mutation M6 — every undiscovered body visible to everyone —
can no longer survive all four suites (C-31, the same table row 4); the corpus acceptance gate
started reading truncation as truncation rather than as a legitimate `TICK_BUDGET` (C-6); and a
Pages deploy became a standing job. The close is the first moment all of those run together at
one HEAD, in a clean worktree, with the evidence payload restored and then cleaned. A close that
quotes only the default tier would be quoting the smallest of the phase's own gates.

The ledger is a two-owner surface and the close owns only half of it. The record's ruling belongs
to the adopting-record contract and to its own merge: whether the pre-registered decision rule
produced ADOPTED (baseline 7, the levers graduate, the ladder tip moves) or FINDING (the levers
stay toggles, the record is committed as the finding record, the tip stays at baseline 6 — the
18.12 tip that has stood since 2026-08-01). This close does not re-open that ruling and does not
improve it. It verifies that the ruling was APPLIED — the graduation flips present or absent as
the rule required, the lever slate stamped in the recorded bytes, the floors re-pinned, the
archived prompt-version set retired or kept — and it publishes the numbers either way. A close
that quietly upgrades a FINDING to an ADOPTED is the single failure this phase's whole
pre-registration apparatus exists to make impossible, and the close audit says so in its own
words.

The before/after table reads the pre-registration back, bar by bar, and does not recompute. Every
baseline-6 figure it carries was review-measured over the committed baseline-6 bytes and re-pinned
by the honesty-instrument contract — false crew `whereabouts` 148/723 = 20.5% on `samples/9p2i`;
sole-`alibi_vs_sighting` convicting precision 12/70 = 14.6%; grounded sighting side 36.5%;
fabricated `You completed` lines 53/529 = 10.0% on `samples/9p2i` and 15/65 = 23.1% on
`samples/4p1i`; adjacent-room STRONG share 148/234 = 63.2%; dev markers in spoken `free_text`
53/971 = 5.5%; singular-persona prompts 1,956/1,956; 79 crewmate ejections corpus-wide
(`audits/review-2026-08-19/A/verdicts.md`); non-direct-cell conviction accuracy 46/125 = 0.368
against direct-proof 310/310 (`audits/review-2026-08-19/D/FINAL-synthesis.md` §7). Beside each
sits its baseline-7 value or the stated reason there is none, and the verdict the decision rule
produced. The RR-free half gets the same treatment against measurements that need no record at
all: phantom body frames 1,182/1,769 = 66.8% of committed frames in 50/50 games (C-7) against the
post-fix count, and the default tier's serial 320–338 s against its parallel wall clock. Then the
map: every review finding id this phase acted on resolves to exactly one outcome — fixed,
lever-ON-and-graduated, recorded-as-finding, or triaged backlog — and the backlog is named as a
backlog with its size, which is the synthesis's own instruction ("a triaged backlog reads better
than a half-done sweep").

Finally the close routes. The next decision is the balance wave: the levers this phase excluded
by charter so that one measured delta would have one cause. They are well evidenced and several
are large — no post-meeting position or cooldown reset, so 89 reporters are killed within three
ticks of their own meeting and 69 of 707 meetings carry a participant speaking from inside a vent
(G-5); a witnessed kill that reaches peers only as a +0.08 belief nudge because the turn schema
has no kill shape, at 0.02% of all rendered memory lines (G-8); blind vent exits that produce the
56.5% emerge-sighting rate carrying 310/435 ejections (G-13); finished crewmates standing still,
one for 36 consecutive ticks, across the 48.6% of 9p2i ticks in which nothing happens at all
(G-15); the roll-call asymmetry that makes P(impostor | turn has no whereabouts) 97.7–100% and
leaves `impostor_report.qwen3_6_27b.v3` at 0 calls out of 7,932 (G-22); and sabotage as a walk
simulator, 32 set-wide and 0 in 100 committed 4p1i games (G-40). The synthesis's ruling is that
they belong to a separate chartered wave with its own record, because shipping any of them
alongside the honesty wave destroys the attribution of the delta this phase bought with roughly
23 hours of operator wall clock. The close states the recommendation first, prices each lever
against a second record, and leaves the ruling to the owner.

**Files in scope:**
- audits/audit-phase-20-close.md (new); (the close audit — the section shape below)
- tasks/phase-20.md; (the STATUS line only — CLOSED, the date, the outcome in one sentence, the close audit's path)
- README.md; (the status line only — the two living project-status/roadmap sentences under `## Project status`, flipped from "under way" to the close's outcome; no other README content moves)
- docs/artifacts.md; (the audits/ registry row count only)
- audits/review-2026-08-19/README.md; (the last two rows of the finding→task→PR map)

**Files NOT in scope:**
- every production package, `eval/`, `scripts/`, `tests/`, `frontend/` (the close verifies; it does not fix — a close-found defect is recorded as a finding and routed to the next phase's inputs, exactly as F1 was at the prior close)
- replays/ (the record is done and its bytes are canonical; the close reads them)
- audits/audit-phase-20-preregistration.md, audits/audit-phase-20-counterfactual.md, audits/audit-phase-20-smoke.md, audits/audit-phase-20-baseline-7.md (records — the close quotes them; a correction is an additive dated erratum in the owning document, never a rewrite)
- docs/history.md, docs/reading-guide.md, docs/ml-program.md, docs/lessons.md (the results pass and the lessons pass own them and land before this close)
- docs/artifacts.md; (BLOCKING COORDINATION ITEM — landing the close audit adds one file under `audits/`, and `docs/artifacts.md:95` states a counted `98 files` that `tests/scripts/test_verify_ml_evidence.py:1400` compares against the git index in the DEFAULT tier, so this PR's own `uv run pytest` goes red without the one-token bump. The prior close carried exactly this bump for exactly this reason. Do NOT widen scope silently — craft rule 6: stop and report the blast radius, and ask the owner to admit the file)

**Definition of done:**
- [ ] `audits/audit-phase-20-close.md` re-runs the WHOLE gate at close HEAD by the verifiers' actual invocation paths, each output quoted verbatim with its wall clock: `bash scripts/check.sh` (the default tier, parallel), `uv run pytest -m campaign` (the opt-in tier registered at `pyproject.toml:74-76`), `bash scripts/fetch_evidence.sh` followed by `uv run python scripts/verify_ml_evidence.py --complete`, `bash scripts/verify_samples.sh` in a bare environment, `uv run python scripts/check_doc_facts.py`, and the Pages deploy job's status on the close commit — with the restore-then-gate pair executed in ONE session and its result recorded (green, or a named finding in the F1 shape).
- [ ] Each of the 41 dispatched contracts has a ledger row carrying a fresh contract-specific command, its quoted output, and a verdict of VERIFIED or DEVIATION-RECORDED; no row is silent, no row's verdict rests on the merge alone, and the boilerplate tail is verified once by the gate rerun rather than re-quoted per row.
- [ ] The before/after table states every pre-registered bar from `audits/audit-phase-20-preregistration.md` with its baseline-6 value, its baseline-7 value (or the stated reason there is none), and the verdict the pre-registered decision rule produced — quoted from the record audit and the committed pins, never recomputed in the close; the RR-free rows (phantom body frames, default-tier wall clock, import-contract coverage, the leak scanner's M6 result) sit in the same table with their own sources.
- [ ] The close records that the record's ruling is the record contract's, not the close's: the audit states whether the applied outcome is ADOPTED or FINDING, verifies that the graduation flips, the stamped lever slate, the re-pinned floors and the archived prompt-version set match that outcome, and asserts in words that the close did not re-rule it.
- [ ] Every review finding id this phase acted on maps to exactly one outcome — fixed / lever-ON-and-graduated / recorded-as-finding / triaged backlog — and the untouched remainder is stated as a triaged backlog with its size; the map is consistent row-for-row with the curated review index published earlier this phase.
- [ ] The routed next decision is the balance wave, framed with a costed recommendation: the six excluded levers named with their measured evidence (post-meeting reset, finished-crew jobs, vent peek, `saw_kill`, symmetric roll-call, sabotage — the synthesis's list also carries the 4p1i second act), the attribution argument for a separate record, the operator cost of a second record, and no unilateral ruling; the owner's ruling is recorded in the audit when given.
- [ ] The phase-complete frontier is cross-checked with `scripts/compute_next_task.py::compute_frontier` against a git-log title index PINNED to close HEAD, and the provenance section records close HEAD, the phase's merged-PR range, the coordination commits, the evidence pin and any observed remote tags.
- [ ] `tasks/phase-20.md`'s STATUS line and README's two `## Project status` sentences state the close, its date, its outcome and the close audit's path; a reader who opens either surface after the merge cannot conclude the phase is still under way.
- [ ] docs/artifacts.md's audits/ row count equals the git index at close HEAD; the finding→task→PR map under audits/review-2026-08-19/README.md is complete for every Phase-20 task.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import check_doc_facts"`
- `uv run python -c "import eval.leak_scan"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
- `uv run python -c "import tests._helpers.committed"`
- `uv run python -c "import eval.validity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-20-phase-close` with a title like `task 20.42: the phase close (owner): the close audit, the gate rerun, the ledger, the next decision`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing [L] the prior close's pattern, reprised — audits/audit-phase-19-close.md §1 (the whole gate re-run at close HEAD by the verifiers' actual paths, and its close-found F1: the documented restore and the documented gate are mutually exclusive at two legs), §2 (every contract verified-or-deviation-recorded, none silent), §3 (the before/after story in generated numbers only), §4 (the routed decision, recommendation first, the committed cells doing the arguing), §6 (provenance + the frontier), §7 (the reproduction block); audits/review-2026-08-19/D/FINAL-synthesis.md §4 (the roadmap this phase implements; the wave-2 close-gate list; the pre-registered primary bar), §4 "Later, or never" (the balance-lever ruling: a separate chartered wave with its own record), §6 (the owner's decision framing and the four-week collapse plan), §8 (the re-record ledger); audits/review-2026-08-19/A/collated-findings.md G-5, G-8, G-13, G-15, G-22, G-40 (the six excluded balance levers and their measured evidence); audits/audit-phase-20-preregistration.md (the bars and the decision rule this close reads back); AGENTS.md:76-110 (the seven craft rules every ledger row is audited against); scripts/check.sh:15-21 (the default gate's seven legs); pyproject.toml:74-76 (`addopts = "--strict-markers -m 'not campaign'"` and the registered `campaign` marker — the opt-in tier); .github/workflows/ci.yml + .github/workflows/campaign-tier.yml (the two standing jobs; the Pages workflow is added earlier this phase); docs/artifacts.md:95 (the counted `audits/` registry row, stated as 4.8 MB / 98 files, matching `git ls-files audits | wc -l` = 98 at HEAD); tests/scripts/test_verify_ml_evidence.py:1400 (`test_every_counted_registry_row_matches_the_index`, unmarked and therefore in the DEFAULT tier) via scripts/verify_ml_evidence.py:2162 (`"audits/": (("audits",), ())`) and :2174-2201 (`inventory_problems` — the document's stated count against the git index); scripts/compute_next_task.py:94 (`compute_frontier`, the frontier cross-check); README.md:82-84 and :107 (the two living project-status/roadmap sentences — re-locate by the `## Project status` heading, since the front-door rework and the results pass both restructure this section before the close); tasks/phase-19.md:3 (the STATUS-banner exemplar)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
