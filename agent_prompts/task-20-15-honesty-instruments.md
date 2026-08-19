# Agent Prompt — 20.15 The evidence-honesty instrument set: the review's numbers become committed pins

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.15 — The evidence-honesty instrument set: the review's numbers become committed pins, anchored to audits/review-2026-08-19/A/verdicts.md G-1 (false crew self-placement 148/723), G-2 (the 830-row flag census; sole-flag precision 12 right / 70 wrong; the 63.5% ungrounded sighting side; the 25.3% base rate), G-3 (fabricated completions + the +1 render calibration), G-4, G-5 (venting participants 69/707; reporters killed within 3 ticks 111/707), G-9 (movement-origin flags 38/313), G-12 (ghost-top 303/2461; 0 mismatches over 10,335 reconstructed decisions), G-25 (markers 53/971 turns, 246/1956 prompts; singular persona 1956/1956); audits/review-2026-08-19/B/verdicts.md C-3 (free zero-witness kills declined 190/415; the hash-verified reconstruction harness); audits/review-2026-08-19/A/ideas-multi-agent-researcher.md (adjacent-room STRONG 148/234); audits/review-2026-08-19/D/FINAL-synthesis.md §4 (the wave-2 pre-registration rule + the primary bars); audits/audit-phase-20-preregistration.md §2 rows I-2…I-11, §3, §4 bars 3-7; audits/audit-phase-20-planning.md §4 item 4 (the review's session scripts are NOT committed). Anchors re-verified at HEAD: eval/deduction_metrics.py:14-20 + :852 + :2629-2654; eval/replay_walk.py:231 + :353; eval/funnel.py:236-248 + :376-401; observation/service.py:219 + :605-612; agents/perception.py:90; agents/memory/store.py:1010 + :1028 + :1163 + :1194 + :1451; meetings/transcript.py:561 + :666 + :759 + :2170 + :2380; meetings/schemas.py:57-64 + :183-199 + :298-323 + :423-459; meetings/manager.py:381-383 + :3908-3912; orchestrator/replay.py:120-149 + :164-194; orchestrator/game.py:1029-1031; agents/tactical/impostor_policy.py:185 + :261 + :766 + :813 + :937 + :1008; agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:79 + :136, accusation_round_roll_call.j2:76 + :133, crewmate_report.j2:58, impostor_report.j2:59, impostor_report_roll_call.j2:69, vote_ballot.j2:74 + :100; engine/maps/canonical_1.yaml:179-207; api/replay_loader.py:1485; pyproject.toml:74-79. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-honesty-instruments`
**Depends on:** 20.14 — the solvability instrument lands the shared `scripts/measure_baseline.py` emitter slot and its CLI test first, and sets the Wilson-cell convention both instruments report through; a serialization edge on two files plus one convention, not a semantic prerequisite
**Section refs:** audits/review-2026-08-19/A/verdicts.md G-1 (false crew self-placement 148/723), G-2 (the 830-row flag census; sole-flag precision 12 right / 70 wrong; the 63.5% ungrounded sighting side; the 25.3% base rate), G-3 (fabricated completions + the +1 render calibration), G-4, G-5 (venting participants 69/707; reporters killed within 3 ticks 111/707), G-9 (movement-origin flags 38/313), G-12 (ghost-top 303/2461; 0 mismatches over 10,335 reconstructed decisions), G-25 (markers 53/971 turns, 246/1956 prompts; singular persona 1956/1956); audits/review-2026-08-19/B/verdicts.md C-3 (free zero-witness kills declined 190/415; the hash-verified reconstruction harness); audits/review-2026-08-19/A/ideas-multi-agent-researcher.md (adjacent-room STRONG 148/234); audits/review-2026-08-19/D/FINAL-synthesis.md §4 (the wave-2 pre-registration rule + the primary bars); audits/audit-phase-20-preregistration.md §2 rows I-2…I-11, §3, §4 bars 3-7; audits/audit-phase-20-planning.md §4 item 4 (the review's session scripts are NOT committed). Anchors re-verified at HEAD: eval/deduction_metrics.py:14-20 + :852 + :2629-2654; eval/replay_walk.py:231 + :353; eval/funnel.py:236-248 + :376-401; observation/service.py:219 + :605-612; agents/perception.py:90; agents/memory/store.py:1010 + :1028 + :1163 + :1194 + :1451; meetings/transcript.py:561 + :666 + :759 + :2170 + :2380; meetings/schemas.py:57-64 + :183-199 + :298-323 + :423-459; meetings/manager.py:381-383 + :3908-3912; orchestrator/replay.py:120-149 + :164-194; orchestrator/game.py:1029-1031; agents/tactical/impostor_policy.py:185 + :261 + :766 + :813 + :937 + :1008; agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:79 + :136, accusation_round_roll_call.j2:76 + :133, crewmate_report.j2:58, impostor_report.j2:59, impostor_report_roll_call.j2:69, vote_ballot.j2:74 + :100; engine/maps/canonical_1.yaml:179-207; api/replay_loader.py:1485; pyproject.toml:74-79
**Complexity:** Integration
**Record impact:** none — the module only reads committed bytes; no rendered-prompt byte and no detector output moves, and the OFF-path pins stay green unchanged.
**Measurement:** `uv run pytest tests/eval/test_evidence_honesty.py -q` green; `uv run python scripts/measure_baseline.py --honesty replays/samples/9p2i` prints all ten cell families in under 2 minutes with the pinned values (false whereabouts 148/723, sole-flag precision 12 right / 70 wrong, grounded sighting side, fabricated completions 53/529, adjacent-room STRONG 148/234, markers 53/971 turns and 246/1956 prompts, singular persona 1956/1956, venting participants 16/165, free kills declined 190/415, ghost-top 303/2461) — output pasted into the PR Summary.

The Phase-20 pre-registration is a falsifiability contract, and a contract whose
numbers cannot be re-run is not one. Ten of the thirteen instrument rows in
`audits/audit-phase-20-preregistration.md` §2 are today [REVIEW-DERIVED]: they were
measured by the 2026-08-19 review's session scripts over the committed baseline-6
bytes, and those scripts are deliberately NOT committed
(`audits/audit-phase-20-planning.md` §4 item 4 — the Markdown is the record, the
instrument is the deliverable). Until this task lands, bars 3 through 7 of the
pre-registration name a "before" that nobody can recompute, which is exactly the
failure mode this phase exists to stop repeating. This contract turns those ten
rows into one typed module, four committed sets of pins, and one command.

The cells, with the review's values as the expected pins. I-2 false crew
self-placement — a spoken `whereabouts` whose room matches the speaker's true room
at NEITHER agent-tick N nor N−1 — 148/723 = 20.5% (samples/9p2i), 402/2038 = 19.7%
(ml_corpus/9p2i), 7/78 = 9.0% (samples/4p1i), 11/79 = 13.9% (ml_corpus/4p1i)
[A/verdicts.md G-1]. I-3 sole-`alibi_vs_sighting` convicting precision, 12 right /
70 wrong = 14.6%, and the STRONG-class impostor share 33/192 = 17.2% against a
25.3% living-voter base rate — a class that is anti-informative, below chance at
one-sided p=0.0048 [G-2]. I-4 grounded sighting side, 36.5% of 170 resolvable
sides supported by the speaker's own perception, 28.8% not supported even at ±2
ticks [G-2]. I-5 fabricated `You completed` lines, 53/529 = 10.0%, 140/1528 = 9.2%,
15/65 = 23.1%, 14/64 = 21.9% [G-3, corroborated independently by B/verdicts.md
C-2]. I-6 adjacent-room STRONG share 148/234 = 63.2%
[A/ideas-multi-agent-researcher.md]. I-7 movement-origin flags 7/76, 30/233, 0/3,
1/1 — 38/313 pooled, and 38/38 of them memory-truthful and spoken-false [G-9]. I-8
dev-marker contamination, 53/971 turns and 246/1956 prompts (samples/9p2i),
139/2726 and 671/5502 (ml_corpus/9p2i), zero on both 4p1i sets [G-25]. I-9
singular-persona prompts 1956/1956 and 5502/5502 [G-25(b)]. I-10 the two context
cells: meetings with a participant inside a vent 16/165, 50/463, 1/39, 2/40 (69/707
pooled) and reporters killed within 3 ticks of their own meeting 27/165, 75/463,
5/39, 4/40 (111/707 pooled) [G-5]. I-11 the two co-intervention cells that price
Task 20.32's comparator repair: free zero-witness kills declined 190/415 = 45.8%
[B/verdicts.md C-3] and ghost-top impostor decisions 303/2461 = 12.3%, 555/6663,
0/632, 0/579 [G-12].

Three definitional collisions sit inside those numbers, and adjudicating them IS
the work — a bar measured on a definition nobody wrote down is a bar anyone can
move. First, I-3's 14.6% and its 84.4%-crewmate companion come from two different
conventions: "12 right / 70 wrong" is per-VICTIM (the only STRONG flag naming the
ejected player, denominator 82) while "77 ejections, 65 of them crewmates" is
per-MEETING (the meeting's only STRONG flag). Second, I-4's tolerance: the review
measured at-tick and at ±2, `audits/audit-phase-20-preregistration.md` §2 writes
"±1 agent tick", and production's exculpatory vouch channel uses
`SIGHTING_GROUNDING_TICK_TOLERANCE = 2` (meetings/transcript.py:666) — three
different tolerances for one cell. Third, the review disagrees with itself on the
samples-pooled fabricated-completion count: A/verdicts.md G-3's per-set table sums
to 68/594 while D/FINAL-synthesis.md §4 item 2.1 quotes 65/594. All three are
resolved here, in code, with the losing reading named in the test comment; this
task emits every reading, and Task 20.22 then names the ONE convention each of
bars 4 and 5 gates on when it restates those pre-registration rows.

Underneath every cell is one clock. The agent memory frame runs exactly +1 against
the engine/replay frame — the review proved it on 18,936/18,936 discriminating
sightings, and G-7's headline statistic was a two-clock artefact that inflated
three of Track A's own numbers by one tick. The module therefore does not assume
the offset; it asserts it on committed bytes before counting anything, so a future
clock change (roadmap item 2.14, deferred) fails here first instead of silently
re-pricing every bar.

Nothing in production moves. This is an instrument over recorded bytes: the
meeting rows already carry the transcript, the detector's `ContradictionRef` flags
and the verbatim `LLMCallRecord.prompt` text
(orchestrator/replay.py:164-194, :120-149), and everything else is reconstructed by
the hash-verifying `eval/replay_walk.py` walk. Record impact is none and prompt
templates are untouchable here — the single Phase-20 prompt-set bump is Task
20.31's alone. Downstream, `compute_evidence_honesty` is the ONLY home of these
definitions: Task 20.22 pins the pre-registration from it, Task 20.34 runs it under
the lever-ON slate for the offline counterfactual, and Task 20.36 reads it cell by
cell on the baseline-7 bytes. If a cell is re-implemented anywhere else, the
before and the after stop being comparable, which is the one failure this phase
cannot survive.

**Files in scope:**
- eval/evidence_honesty.py; (NEW — the instrument module: one frozen typed cell family per metric above, computed from committed bytes via the replay walker and the recorded transcripts/prompts; Wilson intervals imported from `eval.deduction_metrics`)
- tests/eval/test_evidence_honesty.py; (NEW — hand-built fixture tests per cell plus the four committed sets' pins, with every difference from the review's value explained in a comment)
- eval/deduction_metrics.py; (ONLY if a shared helper genuinely must be exported — prefer importing `_wilson_interval` / `WilsonRateCell` as `tests/eval/test_deception_instruments.py` already does; a third copy of the Wilson helper is forbidden)
- scripts/measure_baseline.py; (the `--honesty` emitter, following the `--vj` / `--funnel` shape at :471-508 and :540-556)
- tests/scripts/test_measure_baseline_cli.py
- agents/tactical/impostor_policy.py; (NO behaviour change — only if a pure read-only accessor must be exposed to reconstruct target rankings; prefer reconstructing via the public `decide()` on rebuilt memory as the review's C-3 harness did)
- tests/agents/test_impostor_policy.py; (the free-kill-declined pin over samples/9p2i, 190/415 — read-only reconstruction, the policy untouched)

**Files NOT in scope:**
- meetings/, agents/memory/, observation/, orchestrator/ (no behaviour change anywhere; the instrument reads recorded bytes and re-runs the engine, it does not edit either)
- agents/strategic/prompts/ (prompt templates are editable in Task 20.31 only, the single prompt-set bump; the singular-persona and marker cells COUNT the current bytes, they do not fix them)
- replays/ (bytes never move; no recording of any kind)
- audits/audit-phase-20-preregistration.md (Task 20.22 pins it from this task's cells; this task supplies numbers, not the memo)
- eval/solvability.py (the sibling instrument is Task 20.14's; import it if a cell needs it, never edit it)
- tests/conftest.py (out of scope — cache the per-set report in a module-scoped fixture inside the new test file instead of adding a session fixture beside `committed_9p2i_report`)
- orchestrator/replay.py (no lever, no stamp key; Task 20.33 owns substrate-stamp registration for the whole phase)

**Definition of done:**
- [ ] `eval/evidence_honesty.py` exposes exactly the ten cell families I-2…I-11 of `audits/audit-phase-20-preregistration.md` §2 as frozen typed dataclasses hung off one `EvidenceHonestyReport`, each carrying a docstring that states its numerator, its denominator, the clock convention it uses and what it does NOT measure — the `eval/deduction_metrics.py:14-20` definitions-before-counting discipline; `tests/eval/test_evidence_honesty.py` asserts each definition sentence is present verbatim so the string 20.22 copies into the memo cannot drift from the code that computes it.
- [ ] The +1 agent-clock alignment is ASSERTED, not assumed: the module resolves every recorded observation tick to the engine frame as `obs.tick − 1`, and a test reproduces the review's proof on committed bytes (for discriminating sightings — subject changed room between T−1 and T — the spoken room matches the walker's room at `obs.tick − 1` with zero exceptions). A perturbed offset makes the assertion fail (craft rule 2).
- [ ] I-2 is pinned per set with the "matches at NEITHER agent-tick N nor N−1" rule and crew/impostor split: 148/723, 402/2038, 7/78, 11/79 — or the re-derived values, each difference explained by cause in the test comment.
- [ ] I-3 ships BOTH conventions, named and separately pinned — per-victim (the only STRONG `alibi_vs_sighting` naming the ejected player: 12 right / 70 wrong = 12/82 = 14.6%) and per-meeting (the meeting's only STRONG flag: 77 ejections, 65 crewmates) — and the module states which one the pre-registration's bar 4 is measured on. The class impostor share is deduped by subject (33/192 = 17.2%) and compared against the same meetings' living-voter impostor base rate (25.3%), both reported with Wilson intervals.
- [ ] I-4 takes the tick tolerance as an explicit parameter and reports the ±0, ±1 and ±2 cells side by side (the review: 36.5% grounded at-tick, 71.2% within ±2, over 170 resolvable sides), with the resolvable / unresolvable split quoted so the denominator is never silently the full 234, and with `meetings/transcript.py:666`'s production value named in the docstring as a distinct thing from this instrument's parameter.
- [ ] I-5 is pinned per set (53/529, 140/1528, 15/65, 14/64) with the +1 render offset calibrated in-module against `task_completed` events, and the review's internal disagreement resolved in the test comment: A/verdicts.md G-3's per-set table sums to 68/594 over the two samples sets while D/FINAL-synthesis.md §4 item 2.1 quotes 65/594 — the instrument's value is authoritative and the comment says which reading was wrong and why.
- [ ] I-6 computes adjacency from `engine/maps/canonical_1.yaml`'s doorway list (never a hard-coded room table) with the tick-gap rule stated, pinned at 148/234 pooled plus per-set cells; I-7 is pinned at 7/76, 30/233, 0/3, 1/1 (38/313 pooled) with the origin-vs-destination test derived from the speaker's own `saw_player_move` render line.
- [ ] I-8 is pinned on BOTH denominators (turns 53/971 and 139/2726; prompts 246/1956 and 671/5502; zero on both 4p1i sets) reading the recorded `LLMCallRecord.prompt` bytes and `MeetingTurn.free_text`, with the marker set derived from the `meetings/manager.py` constants rather than re-typed literals; I-9 is pinned at 1956/1956 and 5502/5502, and the 4p1i sets report NOT-APPLICABLE (one impostor makes the singular persona true) rather than a zero that would read as "clean".
- [ ] I-10 is pinned per set — venting participants 16/165, 50/463, 1/39, 2/40 and reporters killed within 3 ticks 27/165, 75/463, 5/39, 4/40 — with the "within 3 ticks" window defined inclusively and the body-triggered restriction stated.
- [ ] I-11 refuses to count until the reconstruction is faithful: rebuilding each impostor's memory tick-by-tick and calling `ImpostorPolicy.decide` reproduces the recorded action stream with ZERO mismatches for every set (the review: 0 over 10,335 decisions), asserted as a hard precondition before any cell is emitted; free zero-witness kills declined pins at 190/415 with the miss-reason breakdown (168 ranking / 15 fellow-defer / 7 cover) and ghost-top decisions pin at 303/2461, 555/6663, 0/632, 0/579. A planted mismatch makes the precondition fire.
- [ ] `uv run python scripts/measure_baseline.py --honesty <set-dir>` prints every cell for one set with denominators and Wilson intervals in under 2 minutes on the author's machine (timed in the PR), and `--honesty --json` emits the machine-readable rows 20.34 consumes; `tests/scripts/test_measure_baseline_cli.py` covers both the human and JSON paths and the missing-directory exit code.
- [ ] The module is the only home of these definitions: the PR quotes a repo grep showing no second implementation of any cell, and states that 20.22, 20.34 and 20.36 consume `compute_evidence_honesty` rather than re-deriving.
- [ ] No production behaviour changes: `tests/meetings/test_prompt_byte_golden.py` and `bash scripts/verify_samples.sh` stay green, `git diff --stat` shows zero changed lines under `meetings/`, `agents/memory/`, `observation/` and `orchestrator/`, and any `agents/tactical/impostor_policy.py` diff is a pure read-only accessor with no change to an existing call site (quoted in the PR).
- [ ] Three further cells are defined in the module and pinned: the movement-origin flag cell (alibi_vs_sighting whose sighting is the origin half of a move line in the speaker's memory — 7/76, 30/233, 0/3, 1/1 review-derived), the self-placement coverage cell (share of crew whereabouts claims a rendered self-location line could have been copied from), and the two render-budget cells (mean rendered lines per snapshot; reported-testimony rows kept, by candidate-count bucket) — so the lever tasks and the counterfactual print them from one place.
- [ ] The policy-reconstruction cells (free kills declined; ghost-top decisions) live in tests/agents/test_impostor_policy.py — the file the mover-repair task owns — never in tests/eval/test_evidence_honesty.py, so the repair updates one pin set.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — read `eval/deduction_metrics.py`'s module docstring before writing a line. Its
"every metric is defined below — numerator, denominator, and what it does NOT measure —
before it is counted" rule is the house style this module extends, and the C5 lesson it
records (two audits' counts differed ONLY by definition) is the exact hazard I-3, I-4 and
I-5 carry. Write all ten definitions first, in prose, then count.

Step 2 — one walk per game serves all ten cells. Do NOT walk four times. Build a
`ReplayWalkConfig` profile in the shape of `eval/funnel.py:236-248` (verify tick hashes,
verify meeting pre/post hashes, fail loud on a missing meeting row) and drive
`eval.replay_walk.walk_replay`. Two passes keep the runtime honest: pass A reads the
meeting rows only (no engine) and indexes exactly which `(agent, tick)` perceptions the
sighting-grounding cell needs plus which impostors are alive per tick; pass B walks once
and builds `ObservationService.build_packet` packets only for those pairs, plus every
impostor tick for the policy reconstruction. Building packets for all nine agents at every
tick is the obvious way and it is the slow one.

Step 3 — the recorded bytes already carry more than you may expect. `MeetingReplayEntry`
holds `transcript` (turns, observations, claims, `free_text`), `contradictions` (the
detector's own flags, so no re-detection is needed for I-3/I-6/I-7) and `llm_calls`, whose
`prompt` field is the verbatim rendered prompt — that is where the rendered-memory lines,
the spliced dev markers and the singular-persona strings live. Read the marker prefixes
from the `meetings/manager.py` constants and the persona strings from the templates rather
than re-typing literals, so a Task-20.31 template edit shows up as a changed cell instead
of a silently stale one. STRONG vs weak is `meetings.transcript.is_weak_contradiction`,
never a substring check on the description.

Step 4 — the impostor reconstruction is the C-3 harness verbatim: rebuild each impostor's
`MemoryStore` tick-by-tick with `ObservationService.build_packet` +
`agents.perception.ingest_packet`, then call the public `ImpostorPolicy.decide(memory,
public_map)`. Derive the "free zero-witness kill" predicate from the ENGINE rules
(`engine/rules.py` legality: alive impostor, not vented, cooldown 0, an alive crewmate
co-located, zero other living non-vented non-fellow players) and not from the policy's own
`_kill_available_now`, which inherits the same `targets[0]`-only defect the cell measures.
Assert 0 mismatches against the recorded action stream BEFORE emitting; a reconstruction
that drifts must fail loudly rather than quietly re-price the co-intervention. Ghost-top is
"the top-ranked target is a player the meeting record already ejected, or one whose death
the impostor never saw" — state the two sub-populations separately (the review: 222
ejected / 81 unseen on samples/9p2i).

Step 5 — resolve the three definition collisions explicitly and cheaply. I-3: emit both
conventions as separate typed cells and let 20.22 pick; do not average them. I-4: make the
tolerance a parameter with ±0/±1/±2 emitted; the pre-registration says ±1, the review
measured at-tick, and production's vouch tolerance is 2 — three numbers, one parameter.
I-5: recount and say which of 65 or 68 was right. Every difference from a review value goes
in a test comment as a sentence with a cause, never as a silent re-pin.

Step 6 — pins live in the test file, values quoted with denominators, and the four sets get
a module-scoped cached fixture inside `tests/eval/test_evidence_honesty.py` (tests/conftest.py
is out of scope). Mark the four-set pins `slow` for tiering annotation — it carries no
default filter, so they still run in the default gate (pyproject.toml:77). Hand-built
fixtures come first for each cell's logic; the committed-set pins are the second layer, not
the only one.

Step 7 — the `--honesty` emitter mirrors `--vj`: a boolean flag, a `_render_*_human`
function, an `_emit_*_json` function, an early return in `main()`. Keep the JSON row shape
stable and documented — Task 20.34 diffs OFF against ON through it, and Task 20.36 reads it
on the baseline-7 bytes.

## Public types this task introduces
- `eval.evidence_honesty.EvidenceHonestyReport`
- `eval.evidence_honesty.compute_evidence_honesty`
- `eval.evidence_honesty.FalseWhereaboutsCells`
- `eval.evidence_honesty.SoleFlagPrecisionCells`
- `eval.evidence_honesty.GroundedSightingCells`
- `eval.evidence_honesty.FabricatedCompletionCells`
- `eval.evidence_honesty.AdjacentRoomFlagCells`
- `eval.evidence_honesty.MovementOriginFlagCells`
- `eval.evidence_honesty.MarkerContaminationCells`
- `eval.evidence_honesty.SingularPersonaCells`
- `eval.evidence_honesty.MeetingPhysicalityCells`
- `eval.evidence_honesty.ImpostorTargetingCells`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Ten cells, four sets, one module: the risk is silently disagreeing definitions between this
module and the pre-registration text, or a cell whose reconstruction drifts from the
recorded bytes. Mitigation, in this order. Every cell's definition sentence is ONE string,
present verbatim in the module docstring and asserted by the test that 20.22 will copy into
the memo — if the memo and the module ever disagree, the test is what fails. The FSM
reconstruction asserts zero mismatches against the recorded action stream before any I-11
cell is emitted, and the hash-verifying walk profile means a drifted engine reconstruction
raises rather than counts. Every pin quotes its denominator, so a denominator change reads
as a diff and not as a moved bar.

Two second-order risks. Runtime: the honest budget is one walk per game with targeted
packet construction; if the two-pass design is skipped the emitter will not meet the
2-minute bar and the pressure will be to drop cells rather than to fix the walk — resist
that and fix the walk. Scope creep toward repair: this task MEASURES eight defects that
later tasks FIX, and every one of them is tempting to fix while you are standing in the
file. The instrument must read baseline-6 behaviour exactly as it is, including the bugs;
a cell computed against a quietly repaired code path would make the phase's before/after
comparison meaningless. If a cell cannot be computed without touching production, stop and
report rather than widening scope (craft rule 6).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.solvability"`

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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-honesty-instruments` with a title like `task 20.15: the evidence-honesty instrument set: the review's numbers become committed pins`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/A/verdicts.md G-1 (false crew self-placement 148/723), G-2 (the 830-row flag census; sole-flag precision 12 right / 70 wrong; the 63.5% ungrounded sighting side; the 25.3% base rate), G-3 (fabricated completions + the +1 render calibration), G-4, G-5 (venting participants 69/707; reporters killed within 3 ticks 111/707), G-9 (movement-origin flags 38/313), G-12 (ghost-top 303/2461; 0 mismatches over 10,335 reconstructed decisions), G-25 (markers 53/971 turns, 246/1956 prompts; singular persona 1956/1956); audits/review-2026-08-19/B/verdicts.md C-3 (free zero-witness kills declined 190/415; the hash-verified reconstruction harness); audits/review-2026-08-19/A/ideas-multi-agent-researcher.md (adjacent-room STRONG 148/234); audits/review-2026-08-19/D/FINAL-synthesis.md §4 (the wave-2 pre-registration rule + the primary bars); audits/audit-phase-20-preregistration.md §2 rows I-2…I-11, §3, §4 bars 3-7; audits/audit-phase-20-planning.md §4 item 4 (the review's session scripts are NOT committed). Anchors re-verified at HEAD: eval/deduction_metrics.py:14-20 + :852 + :2629-2654; eval/replay_walk.py:231 + :353; eval/funnel.py:236-248 + :376-401; observation/service.py:219 + :605-612; agents/perception.py:90; agents/memory/store.py:1010 + :1028 + :1163 + :1194 + :1451; meetings/transcript.py:561 + :666 + :759 + :2170 + :2380; meetings/schemas.py:57-64 + :183-199 + :298-323 + :423-459; meetings/manager.py:381-383 + :3908-3912; orchestrator/replay.py:120-149 + :164-194; orchestrator/game.py:1029-1031; agents/tactical/impostor_policy.py:185 + :261 + :766 + :813 + :937 + :1008; agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:79 + :136, accusation_round_roll_call.j2:76 + :133, crewmate_report.j2:58, impostor_report.j2:59, impostor_report_roll_call.j2:69, vote_ballot.j2:74 + :100; engine/maps/canonical_1.yaml:179-207; api/replay_loader.py:1485; pyproject.toml:74-79), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
