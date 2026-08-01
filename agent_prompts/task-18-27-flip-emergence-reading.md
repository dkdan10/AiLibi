# Agent Prompt — 18.27 THE FLIP + EMERGENCE READING (owner) + conditional productization

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.27 — THE FLIP + EMERGENCE READING (owner) + conditional productization, anchored to audits/audit-phase-17-close.md §1.3 (the flip bar, verbatim); audits/audit-phase-18-emergence-preregistration.md (the ratified second axis); tasks/phase-17.md 17.16 (the evidence-gated flip shape, both branches); the 18.26 evidence tables. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-flip-emergence-reading`
**Depends on:** 18.4, 18.18, 18.26
**Section refs:** audits/audit-phase-17-close.md §1.3 (the flip bar, verbatim); audits/audit-phase-18-emergence-preregistration.md (the ratified second axis); tasks/phase-17.md 17.16 (the evidence-gated flip shape, both branches); the 18.26 evidence tables
**Complexity:** Integration

The phase's owner reading, two axes in one memo. **Axis 1 — the flip:** the champion
candidate read against the standing bar (referee PASS at the adopted baseline's floors AND
win ≥ the same-seed FSM comparator); PASS ⇒ productize the ARTIFACT surface (the champion
weights/stamp under `agents/tactical/learned/` swap to the ruled candidate) and pre-author
the selector flip — the DEFAULT-SELECTOR surfaces (`orchestrator/game.py::
build_default_agent_factory`, the `scripts/run_tournament.py` default path) flip at
18.28's adopting record, not here (adoption-at-record: a default graduates at the baseline
that adopts it); FAIL ⇒ the champion stays opt-in, the finding recorded, 18.28 closes
NO-FLIP. **Axis 2 — emergence:** every pre-registered instrument read against the
18.4 memo's four-part discipline (significance, split-reproducibility, ablation,
selected-for), each claim ruled EMERGENT / NOT-DEMONSTRATED with the evidence quoted. A
crew-adoption question, if the crew evidence supports one, is put to the owner here as its
own slot — never folded silently into either axis.

Inherited from the 18.24 merge (quote committed artifacts; report §12 Errata names the
prose defects): (a) **the F13 ruling is THIS reading's** — 18.26's pre-registered
champions-vs-runner-ups cell measures it, and this memo rules which hypothesis stands; if
the runner-up effect is real (the ES trading evidence-supply for wins), that is a
Phase-18-level finding about the selection rule whose FIX is a routed next-campaign/
Phase-19 contract, never a retrofit into this phase. (b) **F6 bounds attribution**: the
run-01 same-seed `conviction=None` twin reproduced the impostor champion lineage
sha-for-sha, so no axis-2 emergence claim may attribute an impostor-side selection effect
to the conviction term on that lineage (the term's demonstrated selection effect is
crew-side). (c) **F11 is a measurement, not a ruling**: encoder v3 trained 3.8× worse
than its v2 ablation twin at the 12-generation budget — input to the reading, with the
disposition routed to the close's hand-off ledger. (d) The named non-finalist exhibit
`27f852fe…` (v3 gen-9 hall champion) stands ready if the off-menu instrument's
claim-grade denominators are wanted. (e) Any UNRESOLVABLE gauge verdict from 18.26 reads
exactly that in axis 1 — the bar stays as ratified, unresolvability is reported, and
re-pricing the bar remains an owner decision outside this memo. (f) From the 18.25
merge: the conviction-term emergence claim arrives NOT-DEMONSTRATED with its limb states
recorded (limb (a) unsatisfiable at n=3; limb (c) PARTIAL — the recede recording
deliberately withheld under the F12 stop); F6 is EXTENDED, not contradicted — the term's
selection locus is crew-side on BOTH bases with a base-dependent channel (direct
selection reordering where meetings are scarce, exploiter-novelty where meetings are
rich) — and no impostor-side attribution is permitted on the `ea4bc955…`-seeded
lineages either. The cycling-detector inputs: Red-Queen signature PRESENT on the
general-base impostor (flat anchor + oscillating co-matchup), owned-task crew reads
progress, its impostor plateaus. Any crew-adoption slot rests on 18.26 evidence alone —
18.25 supplies none that clears a bar.

The 18.26 evidence map (merged 384effc, verified — the memo quotes THESE rows and cells,
never report prose): rows `p18-imp-{ea4bc955,bfd145cb,6d327dcb,7f73929d}`,
`p18-fsm-comparator`, `p18-crew-{c1-gen9,c1-gen0,c2-gen9,c2-gen0}` in
`training/reports/results-finalist-eval.jsonl`; persisted cells
`f13_intersection_gauges`, `instruments.kill_craft_rider_intersection`,
`instruments.conversion_paired_49_seed`, `instruments.intersection_49_seed_for_7f73929d`,
`instruments.registered_nested_cells`, `instruments.seed_mod5_splits`,
`instruments.kill_craft_co_present_departure`. Axis-1 mechanics the ruling must carry:
`witnessed_event_rate` is UNRESOLVABLE on ALL NINE arms (structural — the rare-event
floor's 25% noise ceiling is unclearable at n=50), so the ratified three-gauge referee is
EFFECTIVELY TWO GAUGES, and on `bfd145cb…` (whose flags cell is also UNRESOLVABLE at a 7%
overshoot) the axis-1 FAIL rests on conversion alone; `7f73929d…` reads against the
49-seed intersection comparator 12/49 = 0.24490, never 0.26 (its n=49 seed-35 exclusion
is owner-sanctioned and annotated everywhere); the comparator-pairing map is full-50 for
the three full arms, the 49-seed block for `7f73929d…`, nothing for crew arms. The
measured axis-1 material: every learned arm beats the comparator on wins (+0.12 to
+0.30) and every one fails the referee supply gauges — NO candidate satisfies the §1.3
conjunction as measured. F13 under §11.2's either-side noise rule: all three pooled
runner-up-minus-champion margins NEGATIVE and noise-barred from supporting hypothesis A
(the hypothesis-B shape; one residual within-lineage conversion cell survives —
"A unsupported" ≠ "B demonstrated", the ruling is this memo's). Axis-2 scoping: ablation
clause (c) is complete on ZERO of the five campaign runs as recorded — inspect per cell;
crew axis-2 columns are NOT-DEMONSTRABLE for want of an opponent-matched comparator
(owner 2026-07-31: label, do not record), with a scripted-crew-vs-`ea4bc955…` comparator
arm ROUTED as an owner-optional follow-up if this memo wants crew claims;
roll-call is CONTEXT, not a ratified instrument; both action-entropy rulings arrive
NOT-DEMONSTRATED (the variance field never landed). Two post-hoc-criterion questions are
put to this memo explicitly rather than answered below it: the equivalence margin
("gen-9 ≈ gen-0" was never operationalized) on both the rider and conversion pairs, and
nothing else — every other cell reads through pre-registered semantics.

**Files in scope:**
- audits/audit-phase-18-flip-emergence.md (new: the two-axis memo + rulings)
- agents/tactical/learned/; (PASS branch only: the artifact-surface productization swap — the default-selector files flip at 18.28's record)
- tests/scripts/test_champion_flip_ruling.py; (the ruling pins, either branch)
- tasks/phase-18.md; (the ruling's banner note)

**Files NOT in scope:**
- eval/ + training/ (evidence is read, never regenerated here)
- replays/ (no record at the reading — 18.28 records)

**Definition of done:**
- [ ] The memo reads axis 1 against the bar with every floor cell + win edge quoted from the 18.26 committed rows, the ruling recorded verbatim, and the ruled branch implemented + pinned (PASS: the artifact surface swapped and the 18.28 selector flip pre-authored, with the default provably NOT yet moved — adoption-at-record; FAIL: the default provably unmoved).
- [ ] Axis 2 rules every pre-registered claim with its four-part evidence quoted (including the ablation runs' provenance), and any crew-adoption slot is put and recorded explicitly.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The 17.16 both-branches-pre-authored pattern: write the FAIL branch first (it is the
historical base rate), then the PASS branch's swap surface. The ablation evidence for axis
2 comes from the campaign reports — if an ablation was not run for a claimed behavior, the
claim reads NOT-DEMONSTRATED, honestly.

## Integration risk

Two owner rulings in one PR risks a stalled merge if one axis's evidence is contested —
keep the memo's axes separable so the owner can rule one and hold the other (the PR stays
open on the held axis, the 17.14 PENDING pattern).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.coevo.hall_of_fame"`
- `uv run python -c "import training.conviction.serving"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.conviction.model"`
- `uv run python -c "import training.conviction.dataset"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`
- `uv run python -c "import agents.tactical.features"`
- `uv run python -c "import training.coevo.factory"`
- `uv run python -c "import training.coevo.rollout"`
- `uv run python -c "import training.coevo.driver"`
- `uv run python -c "import training.bakeoff.map_elites"`
- `uv run python -c "import training.realpath"`
- `uv run python -c "import training.anchor_study"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-18-flip-emergence-reading` with a title like `task 18.27: the flip + emergence reading (owner) + conditional productization`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-17-close.md §1.3 (the flip bar, verbatim); audits/audit-phase-18-emergence-preregistration.md (the ratified second axis); tasks/phase-17.md 17.16 (the evidence-gated flip shape, both branches); the 18.26 evidence tables), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
