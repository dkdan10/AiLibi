# Agent Prompt — 20.34 THE OFFLINE COUNTERFACTUAL: the new detector and render rules over the 300 committed games, published before the record

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.34 — THE OFFLINE COUNTERFACTUAL: the new detector and render rules over the 300 committed games, published before the record, anchored to audits/audit-phase-20-preregistration.md §8 (the offline-counterfactual protocol this task executes verbatim), §2 (the I-1…I-13 instrument list), §3 (the baseline cells and their denominators), §4 (the eight primary bars), §5 (the secondary observed-not-gated cells), §6 (the decision rule — partial adoption graduates nothing; this memo's per-lever predictions inform the record audit's narrative, not a graduation subset), §9 (the record order the abandon criteria guard), §10 (THE RATIFIED DECISION — its two named exceptions BIND this task by name: I-3 is `sole_flag_precision.per_victim_precision`, the kind-sole cell reading 12/82 pooled, NOT the exactly-one-flag `per_victim_single_flag_precision`'s 8/58; I-6 is `adjacent_room_flags.adjacent` — one doorway apart AND the sighting within ≤ 1 tick of the alibi window — with the un-gated `adjacent_any_gap` reported BESIDE it, never in place of it), §11 (the amendment log: the 2026-08-20 I-11 erratum — the ratified I-11 cells are frozen constants in `eval.evidence_honesty.RATIFIED_I11_CELLS`, no ratified bar rides I-11, so this script neither recomputes nor gates on them); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 preamble (the "$0 offline counterfactual … how many of the 79 innocent ejections would no longer be minted … a falsifiable prediction made before the measurement, and it de-risks a 23 h event"), §4 wave-2 row 2.5 ("run as the offline counterfactual first"), §4 wave-1 row 1.13 (the two byte-identical speed-ups exist to cut "every offline counterfactual wave 2 depends on"), §5 ruling R3 (with the mover repair declared as a co-intervention, "the offline counterfactual (frozen bytes, detector-only)" is the clean attribution instrument); audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §R1 (148/234 = 63.2% adjacent-room STRONG, and the review's own single-lever offline prediction: "78 of the 126 were adjacent-room flags, and 68 of those 78 (87.2%) ejected an innocent"), Part 1 D1 (the zero-LLM solvability oracle: containment 581/626 = 92.8%, singleton 109/626 correct 103/109, 61/354 ejections on an already-cleared player); audits/review-2026-08-19/A/verdicts.md G-2 (sole-`alibi_vs_sighting` precision 12 right / 70 wrong = 14.6%; 63.5% of resolvable sighting sides never perceived by the speaker; 70 of 79 wrongful ejections ride one), G-3 (fabricated completion lines 53/529 = 10.0% on samples/9p2i, 15/65 = 23.1% on samples/4p1i), G-9 (movement-origin flags 38/313 pooled, 38/38 memory-truthful and spoken-false, 10 meetings ejected the innocent they framed), G-25 (dev markers in turn `free_text` 53/971 = 5.5% and in 246/1956 prompts = 12.6%; singular-persona prompts 1956/1956); audits/review-2026-08-19/A/verdicts.md G-12:260 (the offline reconstruction-fidelity standard, quoted from where it actually lives: "300 games / 10,335 impostor decisions: 0 mismatches vs the recorded action stream" — that held for the PRE-20.32 policy; since the mover repair merged (`09dab356`) the live-policy fold no longer reproduces the recorded action stream, `compute_evidence_honesty(..., assert_recorded_action_fidelity=True)` RAISES, and the ratified I-11 cells are the frozen `eval.evidence_honesty.RATIFIED_I11_CELLS` — so this script must never assert recorded-action fidelity); audits/review-2026-08-19/B/verdicts.md C-3 (the state-hash-verified `eval.replay_walk.walk_replay` harness style the DoD's fidelity bullet means); tests/eval/test_deduction_metrics.py:179-182 (samples/9p2i non-direct 10/33 → 23 innocent), :257 (ml_corpus/9p2i 35/89 → 54), :296-297 (samples/4p1i 1/3 → 2), :310-311 (ml_corpus/4p1i 0/0 → 0) — the committed 19.14 pins that sum to the 79; orchestrator/replay.py:587-609 (`_TOGGLEABLE_LEVER_RESOLVERS` and `TOGGLEABLE_SUBSTRATE_FLAG_KEYS` — 20.33 MERGED (`fc5cf719`), so the table now holds NINE registered keys: the eight Phase-20 levers at :591-598, each bound BY IDENTITY to its home-module resolver, beside the pre-existing `impostor_roll_call` at :590), :620-643 (`substrate_flag_snapshot`'s threaded `env`, the no-`os.environ`-mutation seam), :646 (`env_var_for_lever`, the registry-key → `AILIBI_*` derivation), :714 (`fold_meeting_outcome_into_memories`, 20.33's shared lever-7 fold that the replay-loader walk, the prompt byte-golden walk and the evidence-honesty walk all route through — reuse it, never re-derive the meeting fold); meetings/transcript.py:1515, :1542 (the 13.5 `*_enabled(env: Mapping[str, str] | None = None) -> bool` resolver signature every Phase-20 lever follows), :1576 / :1612 / :1652 (the three merged detector-lever resolvers `movement_claim_shape_enabled`, `grounded_prosecution_enabled`, `map_aware_arbitration_enabled`), :1683-1693 (`detect_contradictions`, whose `env` keyword IS the ON-slate seam); eval/replay_walk.py:366 (`walk_replay`, the 19.25 typed per-tick consumer pattern); api/replay_loader.py:697 (`ReplayLoader`, the reconstruction entry point); eval/deduction_metrics.py:852 (`_wilson_interval`); scripts/measure_baseline.py:656 (`main`, the CLI + `--json` emitter pattern this script copies; its `--solvability` :716 and `--honesty` :726 flags are the committed readers the pre-registration §12 names). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-offline-counterfactual`
**Depends on:** 20.22 (the ratified pre-registration is the input: it fixes the cell list, the bars, the decision rule's partial-adoption clause and the abandon vocabulary this memo predicts against — a counterfactual cannot pre-register a prediction against bars the owner has not yet ratified), 20.33 (all eight lever resolvers must exist and be registered in the substrate stamp before one command can toggle the whole slate through their `env` parameters and prove the ambient process stayed OFF)
**Section refs:** audits/audit-phase-20-preregistration.md §8 (the offline-counterfactual protocol this task executes verbatim), §2 (the I-1…I-13 instrument list), §3 (the baseline cells and their denominators), §4 (the eight primary bars), §5 (the secondary observed-not-gated cells), §6 (the decision rule — partial adoption graduates nothing; this memo's per-lever predictions inform the record audit's narrative, not a graduation subset), §9 (the record order the abandon criteria guard), §10 (THE RATIFIED DECISION — its two named exceptions BIND this task by name: I-3 is `sole_flag_precision.per_victim_precision`, the kind-sole cell reading 12/82 pooled, NOT the exactly-one-flag `per_victim_single_flag_precision`'s 8/58; I-6 is `adjacent_room_flags.adjacent` — one doorway apart AND the sighting within ≤ 1 tick of the alibi window — with the un-gated `adjacent_any_gap` reported BESIDE it, never in place of it), §11 (the amendment log: the 2026-08-20 I-11 erratum — the ratified I-11 cells are frozen constants in `eval.evidence_honesty.RATIFIED_I11_CELLS`, no ratified bar rides I-11, so this script neither recomputes nor gates on them); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 preamble (the "$0 offline counterfactual … how many of the 79 innocent ejections would no longer be minted … a falsifiable prediction made before the measurement, and it de-risks a 23 h event"), §4 wave-2 row 2.5 ("run as the offline counterfactual first"), §4 wave-1 row 1.13 (the two byte-identical speed-ups exist to cut "every offline counterfactual wave 2 depends on"), §5 ruling R3 (with the mover repair declared as a co-intervention, "the offline counterfactual (frozen bytes, detector-only)" is the clean attribution instrument); audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §R1 (148/234 = 63.2% adjacent-room STRONG, and the review's own single-lever offline prediction: "78 of the 126 were adjacent-room flags, and 68 of those 78 (87.2%) ejected an innocent"), Part 1 D1 (the zero-LLM solvability oracle: containment 581/626 = 92.8%, singleton 109/626 correct 103/109, 61/354 ejections on an already-cleared player); audits/review-2026-08-19/A/verdicts.md G-2 (sole-`alibi_vs_sighting` precision 12 right / 70 wrong = 14.6%; 63.5% of resolvable sighting sides never perceived by the speaker; 70 of 79 wrongful ejections ride one), G-3 (fabricated completion lines 53/529 = 10.0% on samples/9p2i, 15/65 = 23.1% on samples/4p1i), G-9 (movement-origin flags 38/313 pooled, 38/38 memory-truthful and spoken-false, 10 meetings ejected the innocent they framed), G-25 (dev markers in turn `free_text` 53/971 = 5.5% and in 246/1956 prompts = 12.6%; singular-persona prompts 1956/1956); audits/review-2026-08-19/A/verdicts.md G-12:260 (the offline reconstruction-fidelity standard, quoted from where it actually lives: "300 games / 10,335 impostor decisions: 0 mismatches vs the recorded action stream" — that held for the PRE-20.32 policy; since the mover repair merged (`09dab356`) the live-policy fold no longer reproduces the recorded action stream, `compute_evidence_honesty(..., assert_recorded_action_fidelity=True)` RAISES, and the ratified I-11 cells are the frozen `eval.evidence_honesty.RATIFIED_I11_CELLS` — so this script must never assert recorded-action fidelity); audits/review-2026-08-19/B/verdicts.md C-3 (the state-hash-verified `eval.replay_walk.walk_replay` harness style the DoD's fidelity bullet means); tests/eval/test_deduction_metrics.py:179-182 (samples/9p2i non-direct 10/33 → 23 innocent), :257 (ml_corpus/9p2i 35/89 → 54), :296-297 (samples/4p1i 1/3 → 2), :310-311 (ml_corpus/4p1i 0/0 → 0) — the committed 19.14 pins that sum to the 79; orchestrator/replay.py:587-609 (`_TOGGLEABLE_LEVER_RESOLVERS` and `TOGGLEABLE_SUBSTRATE_FLAG_KEYS` — 20.33 MERGED (`fc5cf719`), so the table now holds NINE registered keys: the eight Phase-20 levers at :591-598, each bound BY IDENTITY to its home-module resolver, beside the pre-existing `impostor_roll_call` at :590), :620-643 (`substrate_flag_snapshot`'s threaded `env`, the no-`os.environ`-mutation seam), :646 (`env_var_for_lever`, the registry-key → `AILIBI_*` derivation), :714 (`fold_meeting_outcome_into_memories`, 20.33's shared lever-7 fold that the replay-loader walk, the prompt byte-golden walk and the evidence-honesty walk all route through — reuse it, never re-derive the meeting fold); meetings/transcript.py:1515, :1542 (the 13.5 `*_enabled(env: Mapping[str, str] | None = None) -> bool` resolver signature every Phase-20 lever follows), :1576 / :1612 / :1652 (the three merged detector-lever resolvers `movement_claim_shape_enabled`, `grounded_prosecution_enabled`, `map_aware_arbitration_enabled`), :1683-1693 (`detect_contradictions`, whose `env` keyword IS the ON-slate seam); eval/replay_walk.py:366 (`walk_replay`, the 19.25 typed per-tick consumer pattern); api/replay_loader.py:697 (`ReplayLoader`, the reconstruction entry point); eval/deduction_metrics.py:852 (`_wilson_interval`); scripts/measure_baseline.py:656 (`main`, the CLI + `--json` emitter pattern this script copies; its `--solvability` :716 and `--honesty` :726 flags are the committed readers the pre-registration §12 names)
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run python scripts/counterfactual_phase20.py --sets all` completes in < 10 min offline at $0 over the 300 committed games and prints an OFF/ON table whose every cell equals the corresponding table row in `audits/audit-phase-20-counterfactual.md`; the OFF column equals the committed 20.15 / 20.14 / 19.14 pins cell for cell (the 79-meeting enumeration reproducing 23 / 54 / 2 / 0); `uv run pytest tests/scripts/test_counterfactual_phase20.py -q` green.

The record is a one-shot, ~23-hour, $0-but-irreplaceable operator event, and a bar without a
prediction is still a post-hoc read. The pre-registration fixes what will be measured; this task
fixes what is *expected*, in advance, for every cell an instrument can compute without spending the
record. The synthesis states the protocol as the thing that de-risks the event: re-run the new
detector rules over the existing 300 committed games and publish, before recording, how many of the
79 innocent ejections would no longer be minted
(audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 preamble). The 79 is not a review figure —
it is the sum of the committed 19.14 non-direct innocent cells (33 − 10 = 23 on samples/9p2i,
89 − 35 = 54 on ml_corpus/9p2i, 3 − 1 = 2 on samples/4p1i, 0 on ml_corpus/4p1i;
tests/eval/test_deduction_metrics.py:179-182, :257, :296-297, :310-311), against 435 ejections in
total. That is the population this memo walks.

Attribution is the second reason, and it is the one the phase's own doctrine forces. Ruling R3
(audits/review-2026-08-19/D/FINAL-synthesis.md §5) admits the scripted-mover repair into the same
record as a declared co-intervention because publishing a before/after against a knowingly hobbled
comparator is precisely the failure this project's thesis forbids — and then names the price: the
record alone can no longer attribute a delta to the honesty levers. The frozen-bytes counterfactual
is the instrument that pays it. It holds the model, the mover, the seeds and the recorded bytes
constant and moves only the detector and render rules, so whatever it predicts is caused by the
levers and nothing else. Detector-only is not a limitation of the method here; it is the method.

Each lever task already pinned its own single-lever counterfactual beside the honesty instrument's
tests, and that is exactly why this task exists: nobody has yet run them as ONE slate. The levers
interact and their per-lever censuses double-count. Grounding the prosecution removes flags the
map-aware arbitration would also have removed; the movement-claim shape removes a third overlapping
set; the review's own single-lever
estimate for the adjacency rule alone — 78 of 126 flag-driven ejections vetoed, 68 of them wrongful
(audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §R1) — cannot simply be added to G-2's
70-of-79 sole-flag census (audits/review-2026-08-19/A/verdicts.md G-2) or to G-9's 38/313 origin-half
class (same file, G-9). One command, one shipping slate, one table, with denominators.

The memo's other half is the half a weaker memo would omit: what the instrument *cannot* see.
Everything downstream of new model behaviour is unpredictable offline — the non-direct conviction
accuracy (a bar about how agents vote once the substrate changes), the false crew self-placement rate
once a self-location trail exists to copy from, the model-dependent halves of the four injustice
fixtures, and the win split. A flag that stops being minted is not a vote that changes; asserting
otherwise would be the exact overreach the phase is built to demonstrate against. The memo states
each of those by name, with its reason, and then converts the whole thing into an operational
artefact: the abandon criteria the smoke and the record read as written STOP conditions, and the
per-lever predictions the record audit reads against (the ratified §6 rules out subset graduation)
(audits/audit-phase-20-preregistration.md §6), which that rule explicitly defers to this task.

Nothing here changes production behaviour: the script reads committed bytes, toggles resolvers
through their `env` parameters, writes no replay, and mutates no process environment.

**Files in scope:**
- scripts/counterfactual_phase20.py; (new — runs the 20.15 and 20.14 instruments over all four committed sets under a chosen lever slate, OFF as the baseline and ON as all eight, and emits the before/after table plus `--json`)
- tests/scripts/test_counterfactual_phase20.py; (new — the CLI contract, the OFF-equals-committed-pins property, the environment-purity assertion, and the memo-matches-the-script doc-fact check)
- audits/audit-phase-20-counterfactual.md; (new — the memo: the table, the predicted direction of each pre-registered bar, the cells that CANNOT be predicted offline with their reasons, the per-lever prediction table, and the abandon criteria for the record)

Recorded at merge (PR #385, orchestrator-ratified): eval/evidence_honesty.py edited under a scope amendment (14 lines — the _MEETING_FRAME pattern widening so the census counts lever-7's [meeting N] frame; OFF-neutrality proven, §11 erratum dated 2026-08-24; no bar rides the render census). The full eight-lever census is the §4.1 headline (39.0349 rows/snapshot, testimony retention 18.0% → 44.6%), the seven-lever reading kept beside it as the lever-7 decomposition. audits/README.md + docs/artifacts.md index lines accepted. scripts/counterfactual_phase20.py gained --withhold LEVER for single-lever ablations (20.36 may want it). The memo's predicted verdict is FINDING (bars 4, 5, 7 predicted MISS under the ratified readings; nothing re-priced). Prose records, not scope entries.

**Files NOT in scope:**
- agents/memory/store.py, meetings/transcript.py, meetings/manager.py, agents/perception.py and every other lever home module (read-only here — the mechanisms froze at the stamp registration; this task toggles them, never edits them, and a defect found here routes to a named fix task rather than being patched inside the counterfactual)
- orchestrator/replay.py (the stamp registration and the `--expect-levers` preflight are not this task's; the registry is imported and read)
- eval/evidence_honesty.py, eval/solvability.py, eval/deduction_metrics.py (the instruments are IMPORTED, never re-implemented — no cell definition may be born in this script; a cell this script needs and the instruments lack is a finding to route, not a local reimplementation). Verified at HEAD: `compute_evidence_honesty(sample_dir, *, impostor_policy, assert_recorded_action_fidelity)` (eval/evidence_honesty.py:850) and `compute_solvability_report(sample_dir)` (eval/solvability.py:395) take a DIRECTORY and expose NO lever-slate parameter — the deliberate §8 declination, restated in code at tests/eval/test_evidence_honesty.py:1044-1047 ("this instrument exposes no lever slate by design ... the ON census over the committed sets belongs to the offline counterfactual"). So the OFF column calls them as-is under the bare ambient environment, and the ON column is THIS script's own reconstruction re-evaluated through the resolvers' `env` seam. That asymmetry is exactly why the RECORDED-OFF / RECONSTRUCTED-OFF split below exists; it is NOT a defect to route
- every `.j2` prompt template (template edits belong to the single prompt-set bump; this task re-renders under whatever set is default at HEAD and never authors one)
- replays/ (nothing records and no byte moves; the committed bytes are the frozen substrate the whole method depends on holding still)
- audits/audit-phase-20-preregistration.md (ratified at merge; this memo reads against it and may only add dated errata — it never re-prices a bar)
- scripts/check.sh (the full run is a manual pre-record command, not a gate leg; the fast pins run under pytest)

**Definition of done:**
- [ ] `uv run python scripts/counterfactual_phase20.py --sets all` prints, for the OFF slate and the ON slate, every pre-registered cell the instruments can compute offline, per set and pooled, each with its numerator and denominator: the STRONG `alibi_vs_sighting` class size, its impostor share against the roster base rate and the sole-flag precision proxy; the grounded sighting side; the adjacent-room STRONG share; fabricated completion lines; origin-spoken movement flags; dev-marker contamination in turns and in prompts; singular-persona prompts; rendered lines per snapshot and reported-testimony retention; the solvability cells (containment, singleton rate and correctness, ejections on an already-cleared player); and the surviving-STRONG-flag census over the 79 innocent-ejection meetings.
- [ ] The OFF column is proven to BE the committed baseline before any ON number is believed: every OFF cell equals its committed 20.15 / 20.14 pin and the 79-meeting enumeration reproduces the 19.14 non-direct innocent split 23 / 54 / 2 / 0 — with I-11 excluded by the pre-registration's §11 erratum (its ratified cells are the frozen `RATIFIED_I11_CELLS`, not a recomputation, because the 20.32 mover repair deleted the policy that produced them; a live-policy fold reports `impostor_targeting.reconstruction_mismatches > 0` by construction) (asserted in `tests/scripts/test_counterfactual_phase20.py`, not eyeballed in the memo). A disagreement is a defect in this script, not a finding about the bytes, and the script says so in its failure message.
- [ ] Reconstruction fidelity is asserted, not assumed, in the C-3 harness style: the script separates RECORDED-OFF (an instrument reading committed bytes) from RECONSTRUCTED-OFF (the same instrument over re-derived inputs with all eight levers OFF) and refuses to print an ON column for any cell whose two OFF readings disagree. Cells that cannot agree by construction because the default prompt set moved at the prompt-set bump are printed with their RECORDED value and labelled prompt-set-coupled, with the reason in the memo.
- [ ] The slate is toggled ONLY through each resolver's `env` parameter: the script never assigns to `os.environ`, never writes a replay, and never calls an LLM. A test asserts the process environment is identical before and after a full run and that `substrate_flag_snapshot()` read from the ambient process still reports all eight Phase-20 keys False after the run completes.
- [ ] Lever interaction is reported rather than summed: the ON column is one shipping slate (all eight ON), and for each cell the memo states either the leave-one-out attribution the script computed or an explicit declination with its reason. Where the review published a single-lever estimate — the adjacency rule's 78-of-126 / 68-wrongful veto census — the memo quotes it beside the slate figure and explains the difference.
- [ ] `audits/audit-phase-20-counterfactual.md` states, for each of the eight primary bars, the predicted direction and, where the instrument computes it offline, the predicted value with its denominator; and names every cell it CANNOT predict offline with the reason — at minimum the non-direct conviction accuracy, the false crew self-placement rate once the trail exists to copy from, the model-dependent halves of the four injustice fixtures, and the win split — stating in one sentence that a flag that stops being minted is not a vote that changes.
- [ ] The memo states, per lever, the offline-predictable delta and which levers no offline instrument can support (with the reason) — the record audit's per-lever narrative under either verdict; it does NOT propose a graduation subset (the ratified §6 rules partial adoption graduates nothing).
- [ ] The abandon criteria are written as operator-applicable STOP conditions requiring no judgment call, covering at minimum: a validity-gate FAIL; a seed whose opening defaults; a substrate stamp that does not equal the intended slate; a guard trip; and a cell-level tripwire — a cell this memo predicts to reach exactly 0 that is non-zero on the smoke seeds is an ABANDON at any n, while a directional bar that merely misses on five seeds is explicitly NOT (sampling noise, recorded and carried forward).
- [ ] The run is bounded and reproducible: `--sets all` completes in under 10 minutes over the 300 committed games from a fresh clone (the wall time recorded in the PR Summary), needs no network and no `AILIBI_*` export from the operator, and `--json` emits the same table machine-readably for the record audit to consume.
- [ ] `tests/scripts/test_counterfactual_phase20.py` pins the CLI contract on a small committed slice (fast enough for the default tier, with the whole-corpus run marked `slow` if it is kept as a test at all), and asserts the memo's table equals the script's output so the document cannot drift from the instrument.
- [ ] The memo is committed before the smoke record starts — the DAG enforces the order — and the PR Summary carries the headline prediction in one sentence so the smoke report can be read directly against it.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — Read `audits/audit-phase-20-preregistration.md` §2, §3, §6 and §8 first and build the cell
list from it directly. §8 is the specification; anything this script prints that §8 does not name is
scope creep, and anything §8 names that the script cannot compute is a line in the "cannot predict
offline" section, not a silent omission.

Step 2 — One walk, two slates. Reconstruct each game ONCE (`eval.replay_walk.walk_replay` for the
typed per-tick events, `api.replay_loader.ReplayLoader` for the served meeting views), then evaluate
both slates from the same reconstruction. Reconstructing twice doubles the runtime for no signal and
invites the two passes to diverge. The detector levers are pure functions of the reconstructed
meeting inputs plus each speaker's own record, so the ON evaluation is a second call to
`detect_contradictions` with a lever-ON mapping (its `env` keyword, meetings/transcript.py:1693); the
render levers are a second render of the same rebuilt memory. Fold each meeting's outcome into those
rebuilt memories through 20.33's shared helper
`orchestrator.replay.fold_meeting_outcome_into_memories` (orchestrator/replay.py:714) — the same
helper the replay-loader walk, the prompt byte-golden walk and the evidence-honesty walk already use,
so lever 7 (`meeting_outcome_memory`) reconstructs identically in all four places.

Step 3 — Toggle by argument, never by environment. Build one frozen mapping per slate, e.g.
`{"AILIBI_GROUNDED_PROSECUTION": "1", ...}` for ON and `{}` for OFF, and thread it into the
resolvers' `env` parameter the way `orchestrator.replay.substrate_flag_snapshot` already threads it
(the 13.5 signature at meetings/transcript.py:1515). Assert the ambient snapshot is all-False at
process start and again at exit; a monkeypatched `os.environ` would make the whole memo
unreproducible for anyone who runs the command with a stale export.

Step 4 — The 79-meeting census is a join, not a new metric. Take the innocent ejections from the
committed `EjecteeProofCrossTab` partition (eval/deduction_metrics.py), key each one by
`(set, game, meeting)`, then for each recompute the ON-slate flag set and report three things: how
many still carry ANY STRONG flag naming the ejectee, how many lose the sole STRONG flag they
convicted on, and the residue grouped by which lever removed it. Cross-check the enumeration's total
against the committed pins before reporting anything — 23 / 54 / 2 / 0 — and fail loud on a mismatch.

Step 5 — Runtime. The wave-1 speed-ups (the memoized Jinja environment and the bisecting episodic
scan) exist partly for this command; use them rather than re-deriving. If `--sets all` still runs
long, parallelize per game with a process pool over immutable per-game inputs — never by sharing a
mutable renderer — and keep a `--sets <dir>` single-set path for iteration. Report the wall time in
the PR; a command nobody can afford to re-run is a command nobody re-runs.

Step 6 — Write the memo as a falsifiable prediction, not as a summary. Predicted value, denominator,
and the bar it is predicted against, in one row each; a separate short section for the cells that are
not predictable offline with one clause of reason apiece; then the per-lever prediction table and
the abandon criteria. Copy the pre-registration's evidence-label key rather than inventing one, and
state at the top that this memo is detector-and-render only by construction — the declared
co-intervention to the scripted mover is deliberately absent, which is exactly why the table is a
clean attribution instrument.

Step 7 — Keep the definitions in one place. If a cell needs a definition the instruments do not
already own, do not write it here: the instrument module is the single home for cell definitions, and
a second definition of the same cell in a script is how a memo and a record end up disagreeing about
what was measured.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import check_doc_facts"`
- `uv run python -c "import eval.leak_scan"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
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
Open a PR from branch `phase-20-offline-counterfactual` with a title like `task 20.34: the offline counterfactual: the new detector and render rules over the 300 committed games, published before the record`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-20-preregistration.md §8 (the offline-counterfactual protocol this task executes verbatim), §2 (the I-1…I-13 instrument list), §3 (the baseline cells and their denominators), §4 (the eight primary bars), §5 (the secondary observed-not-gated cells), §6 (the decision rule — partial adoption graduates nothing; this memo's per-lever predictions inform the record audit's narrative, not a graduation subset), §9 (the record order the abandon criteria guard), §10 (THE RATIFIED DECISION — its two named exceptions BIND this task by name: I-3 is `sole_flag_precision.per_victim_precision`, the kind-sole cell reading 12/82 pooled, NOT the exactly-one-flag `per_victim_single_flag_precision`'s 8/58; I-6 is `adjacent_room_flags.adjacent` — one doorway apart AND the sighting within ≤ 1 tick of the alibi window — with the un-gated `adjacent_any_gap` reported BESIDE it, never in place of it), §11 (the amendment log: the 2026-08-20 I-11 erratum — the ratified I-11 cells are frozen constants in `eval.evidence_honesty.RATIFIED_I11_CELLS`, no ratified bar rides I-11, so this script neither recomputes nor gates on them); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 preamble (the "$0 offline counterfactual … how many of the 79 innocent ejections would no longer be minted … a falsifiable prediction made before the measurement, and it de-risks a 23 h event"), §4 wave-2 row 2.5 ("run as the offline counterfactual first"), §4 wave-1 row 1.13 (the two byte-identical speed-ups exist to cut "every offline counterfactual wave 2 depends on"), §5 ruling R3 (with the mover repair declared as a co-intervention, "the offline counterfactual (frozen bytes, detector-only)" is the clean attribution instrument); audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §R1 (148/234 = 63.2% adjacent-room STRONG, and the review's own single-lever offline prediction: "78 of the 126 were adjacent-room flags, and 68 of those 78 (87.2%) ejected an innocent"), Part 1 D1 (the zero-LLM solvability oracle: containment 581/626 = 92.8%, singleton 109/626 correct 103/109, 61/354 ejections on an already-cleared player); audits/review-2026-08-19/A/verdicts.md G-2 (sole-`alibi_vs_sighting` precision 12 right / 70 wrong = 14.6%; 63.5% of resolvable sighting sides never perceived by the speaker; 70 of 79 wrongful ejections ride one), G-3 (fabricated completion lines 53/529 = 10.0% on samples/9p2i, 15/65 = 23.1% on samples/4p1i), G-9 (movement-origin flags 38/313 pooled, 38/38 memory-truthful and spoken-false, 10 meetings ejected the innocent they framed), G-25 (dev markers in turn `free_text` 53/971 = 5.5% and in 246/1956 prompts = 12.6%; singular-persona prompts 1956/1956); audits/review-2026-08-19/A/verdicts.md G-12:260 (the offline reconstruction-fidelity standard, quoted from where it actually lives: "300 games / 10,335 impostor decisions: 0 mismatches vs the recorded action stream" — that held for the PRE-20.32 policy; since the mover repair merged (`09dab356`) the live-policy fold no longer reproduces the recorded action stream, `compute_evidence_honesty(..., assert_recorded_action_fidelity=True)` RAISES, and the ratified I-11 cells are the frozen `eval.evidence_honesty.RATIFIED_I11_CELLS` — so this script must never assert recorded-action fidelity); audits/review-2026-08-19/B/verdicts.md C-3 (the state-hash-verified `eval.replay_walk.walk_replay` harness style the DoD's fidelity bullet means); tests/eval/test_deduction_metrics.py:179-182 (samples/9p2i non-direct 10/33 → 23 innocent), :257 (ml_corpus/9p2i 35/89 → 54), :296-297 (samples/4p1i 1/3 → 2), :310-311 (ml_corpus/4p1i 0/0 → 0) — the committed 19.14 pins that sum to the 79; orchestrator/replay.py:587-609 (`_TOGGLEABLE_LEVER_RESOLVERS` and `TOGGLEABLE_SUBSTRATE_FLAG_KEYS` — 20.33 MERGED (`fc5cf719`), so the table now holds NINE registered keys: the eight Phase-20 levers at :591-598, each bound BY IDENTITY to its home-module resolver, beside the pre-existing `impostor_roll_call` at :590), :620-643 (`substrate_flag_snapshot`'s threaded `env`, the no-`os.environ`-mutation seam), :646 (`env_var_for_lever`, the registry-key → `AILIBI_*` derivation), :714 (`fold_meeting_outcome_into_memories`, 20.33's shared lever-7 fold that the replay-loader walk, the prompt byte-golden walk and the evidence-honesty walk all route through — reuse it, never re-derive the meeting fold); meetings/transcript.py:1515, :1542 (the 13.5 `*_enabled(env: Mapping[str, str] | None = None) -> bool` resolver signature every Phase-20 lever follows), :1576 / :1612 / :1652 (the three merged detector-lever resolvers `movement_claim_shape_enabled`, `grounded_prosecution_enabled`, `map_aware_arbitration_enabled`), :1683-1693 (`detect_contradictions`, whose `env` keyword IS the ON-slate seam); eval/replay_walk.py:366 (`walk_replay`, the 19.25 typed per-tick consumer pattern); api/replay_loader.py:697 (`ReplayLoader`, the reconstruction entry point); eval/deduction_metrics.py:852 (`_wilson_interval`); scripts/measure_baseline.py:656 (`main`, the CLI + `--json` emitter pattern this script copies; its `--solvability` :716 and `--honesty` :726 flags are the committed readers the pre-registration §12 names)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
