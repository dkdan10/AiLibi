# Agent Prompt — 20.37 Retire means delete: the post-record graduation sweep and the old accept-and-ignore residue

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.37 — Retire means delete: the post-record graduation sweep and the old accept-and-ignore residue, anchored to C-64 and C-104 in `audits/review-2026-08-19/B/collated-findings.md` §4 and §5; RC6 in `audits/review-2026-08-19/D/FINAL-synthesis.md` §1 ("the render-version stamp, plus one deletion pass"); the per-area sources `audits/review-2026-08-19/B/repo-health-architecture.md` §2 F6, `audits/review-2026-08-19/B/agents-memory.md` §2 F4, `audits/review-2026-08-19/B/meetings-transcript-voting.md` §2 F5, `audits/review-2026-08-19/B/meetings-manager.md` §2 P1-3, `audits/review-2026-08-19/B/orchestrator.md` §2 (the `suspicion_graph_for_meeting` dead-kwarg leg). Anchors RE-VERIFIED at HEAD: the seventeen accept-and-ignore resolvers `agents/memory/store.py:242,273,315,340,369`, `agents/memory/beliefs.py:190,224,292,407`, `meetings/constants.py:54`, `meetings/transcript.py:1515,1542,1575,1600,1628`, `meetings/manager.py:887,929` (332 source lines in total, each ending `del env  # retired: the lever is unconditional, no environment is consulted`); their seventeen `ENV_*` constants `agents/memory/store.py:239,270,294,335,362`, `agents/memory/beliefs.py:187,221,289,404`, `meetings/constants.py:51`, `meetings/manager.py:884,926`, `meetings/transcript.py:1507,1512,1572,1597,1625` and the seventeen matching `__all__` entries; the twenty-two production read sites `agents/memory/store.py:563,566,568,571,574,836,2357` (paired guards `:602`, `:2377`), `agents/memory/beliefs.py:1463,1826,1835,1841` (paired guards `:1465`, `:1502`), `meetings/manager.py:1323,1514,1941,2201,2631`, `meetings/transcript.py:1841,1842,1844,1849,1852`, `orchestrator/game.py:2795` — the original thirteen for the nine older levers plus nine more for the eight Phase-20 levers; the dead private-helper parameters `meetings/transcript.py:2924-2932` — `_detect_alibi_vs_sightings` now takes THREE lever booleans (`whereabouts_interior_flags`, `grounded_prosecution`, `map_aware_arbitration`), of which only `grounded_prosecution` stays live-shaped because `detect_contradictions:1849` ANDs the resolver with `bool(sighting_records)` — with the "survives only for direct callers" comment at `:2953-2956` and the `interior_exempt` expression at `:2963-2965`; the stamp registry `orchestrator/replay.py:524-546` (`_RETIRED_ALWAYS_ON_LEVERS`, TWENTY-ONE keys since the baseline-7 record) and `:568-570` (`_TOGGLEABLE_LEVER_RESOLVERS`, still one live entry); the rule this task amends, `AGENTS.md:62-75` (Graduation sweeps) beside craft rule 3 at `AGENTS.md:91-94`; `.env.example:88-118` (the graduated always-ON note, ALREADY rewritten to twenty-one levers with their adopting records by the baseline-7 record — verify rather than re-author); the test residue `tests/agents/test_absence_prior.py:166-216`, `tests/agents/test_beliefs_hard_evidence_gate.py:86-115`, `tests/agents/test_beliefs.py:2735-2761`, `tests/agents/test_episodic_ids.py:391-467`, `tests/meetings/test_citation_gate.py:127-158`, `tests/meetings/test_manager.py:494-529` and `:791` (`TestRollCallOffPath`, whose docstring says the round is skipped while its test asserts the round fires), `tests/meetings/test_contradictions.py:1581-1667` (TWO resolver classes: `TestWhereaboutsInteriorFlagsResolver:1581` and `TestVentPlacementContradictionsResolver:1621`); and the Phase-20 residue this task inherits — `tests/eval/test_evidence_honesty.py` ON-slates `_TRAIL_ON:1632`, `_MOVEMENT_ON:2002`, `_GROUNDED_ON:2583`, `_MAP_AWARE_ON:3137`, `_COALESCE_ON:3456` plus resolver tautologies at `:1417` and `:1920-1922`, `tests/agents/test_memory_rendering.py`, `tests/agents/test_reported_testimony.py`, `tests/agents/test_memory_meeting_history.py`, `tests/observation/test_leak_property.py`, `tests/orchestrator/test_meeting_integration.py`. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-graduation-sweep`
**Depends on:** 20.36 — the adopting record is the ruling that says which levers graduated, and a lever may only be deleted after its verdict exists; the record's own graduation flips are the commit this sweep deletes on top of, so it cannot run in parallel with them
**Section refs:** C-64 and C-104 in `audits/review-2026-08-19/B/collated-findings.md` §4 and §5; RC6 in `audits/review-2026-08-19/D/FINAL-synthesis.md` §1 ("the render-version stamp, plus one deletion pass"); the per-area sources `audits/review-2026-08-19/B/repo-health-architecture.md` §2 F6, `audits/review-2026-08-19/B/agents-memory.md` §2 F4, `audits/review-2026-08-19/B/meetings-transcript-voting.md` §2 F5, `audits/review-2026-08-19/B/meetings-manager.md` §2 P1-3, `audits/review-2026-08-19/B/orchestrator.md` §2 (the `suspicion_graph_for_meeting` dead-kwarg leg). Anchors RE-VERIFIED at HEAD: the seventeen accept-and-ignore resolvers `agents/memory/store.py:242,273,315,340,369`, `agents/memory/beliefs.py:190,224,292,407`, `meetings/constants.py:54`, `meetings/transcript.py:1515,1542,1575,1600,1628`, `meetings/manager.py:887,929` (332 source lines in total, each ending `del env  # retired: the lever is unconditional, no environment is consulted`); their seventeen `ENV_*` constants `agents/memory/store.py:239,270,294,335,362`, `agents/memory/beliefs.py:187,221,289,404`, `meetings/constants.py:51`, `meetings/manager.py:884,926`, `meetings/transcript.py:1507,1512,1572,1597,1625` and the seventeen matching `__all__` entries; the twenty-two production read sites `agents/memory/store.py:563,566,568,571,574,836,2357` (paired guards `:602`, `:2377`), `agents/memory/beliefs.py:1463,1826,1835,1841` (paired guards `:1465`, `:1502`), `meetings/manager.py:1323,1514,1941,2201,2631`, `meetings/transcript.py:1841,1842,1844,1849,1852`, `orchestrator/game.py:2795` — the original thirteen for the nine older levers plus nine more for the eight Phase-20 levers; the dead private-helper parameters `meetings/transcript.py:2924-2932` — `_detect_alibi_vs_sightings` now takes THREE lever booleans (`whereabouts_interior_flags`, `grounded_prosecution`, `map_aware_arbitration`), of which only `grounded_prosecution` stays live-shaped because `detect_contradictions:1849` ANDs the resolver with `bool(sighting_records)` — with the "survives only for direct callers" comment at `:2953-2956` and the `interior_exempt` expression at `:2963-2965`; the stamp registry `orchestrator/replay.py:524-546` (`_RETIRED_ALWAYS_ON_LEVERS`, TWENTY-ONE keys since the baseline-7 record) and `:568-570` (`_TOGGLEABLE_LEVER_RESOLVERS`, still one live entry); the rule this task amends, `AGENTS.md:62-75` (Graduation sweeps) beside craft rule 3 at `AGENTS.md:91-94`; `.env.example:88-118` (the graduated always-ON note, ALREADY rewritten to twenty-one levers with their adopting records by the baseline-7 record — verify rather than re-author); the test residue `tests/agents/test_absence_prior.py:166-216`, `tests/agents/test_beliefs_hard_evidence_gate.py:86-115`, `tests/agents/test_beliefs.py:2735-2761`, `tests/agents/test_episodic_ids.py:391-467`, `tests/meetings/test_citation_gate.py:127-158`, `tests/meetings/test_manager.py:494-529` and `:791` (`TestRollCallOffPath`, whose docstring says the round is skipped while its test asserts the round fires), `tests/meetings/test_contradictions.py:1581-1667` (TWO resolver classes: `TestWhereaboutsInteriorFlagsResolver:1581` and `TestVentPlacementContradictionsResolver:1621`); and the Phase-20 residue this task inherits — `tests/eval/test_evidence_honesty.py` ON-slates `_TRAIL_ON:1632`, `_MOVEMENT_ON:2002`, `_GROUNDED_ON:2583`, `_MAP_AWARE_ON:3137`, `_COALESCE_ON:3456` plus resolver tautologies at `:1417` and `:1920-1922`, `tests/agents/test_memory_rendering.py`, `tests/agents/test_reported_testimony.py`, `tests/agents/test_memory_meeting_history.py`, `tests/observation/test_leak_property.py`, `tests/orchestrator/test_meeting_integration.py`
**Complexity:** Integration
**Record impact:** post-record
**Measurement:** `grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator | wc -l` reads 19 at HEAD (seventeen dead plus two live) and must read 2 — the baseline-7 record adopted ALL EIGHT Phase-20 levers, so the only survivors are the live 18.10 pair; `grep -rnE 'ENV_(ROLL_CALL_ROUND|WHEREABOUTS_INTERIOR_FLAGS|VENT_PLACEMENT_CONTRADICTIONS|ABSENCE_PRIOR|CITATION_GATE|HARD_EVIDENCE_GATE|OBSERVATION_ID_RENDERING|EVIDENCE_QUALITY_LIFT|REPORTER_EXCULPATION|TASK_COMPLETION_FROM_EVENTS|SELF_LOCATION_TRAIL|MEETING_OUTCOME_MEMORY|COALESCED_MEMORY_RENDER|MOVEMENT_CLAIM_SHAPE|GROUNDED_PROSECUTION|MAP_AWARE_ARBITRATION|STRUCTURED_TURN_MARKERS)' tests/ | wc -l` reads 227 at HEAD across 14 files and must read 0 (the nine-name alternation alone reads 144); `grep -rnE "accepted and ignored|no longer read|now always True" --include="*.py" agents meetings orchestrator | wc -l` reads 50 at HEAD (store.py 15, transcript.py 14, beliefs.py 13, manager.py 5, constants.py 3) and must read 0; `bash scripts/verify_samples.sh` stays 100/100 and `bash scripts/check.sh` is green.

Graduating a lever in this repo has so far meant deleting the env *read* and keeping the
*shape*. SEVENTEEN resolvers of the form `def x_enabled(env: Mapping[str, str] | None = None)
-> bool: del env; return True` survive at HEAD — 332 source lines, each carrying a
9-to-30-line docstring explaining a switch that no longer exists — with seventeen `ENV_*`
constants "retained for naming provenance", seventeen `__all__` exports, and twenty-two
production read sites that still spell an unconditional behaviour as `if always_true():`. The
review reproduced the tax three ways; all three numbers have GROWN since, because the
baseline-7 record graduated the Phase-20 slate on top of the review's nine: 50 comment lines
in `agents/`, `meetings/` and `orchestrator/` say "accepted and ignored" / "no longer read" /
"now always True", and 227 lines of the test suite set environment variables that no
production code reads (`audits/review-2026-08-19/B/repo-health-architecture.md` §2 F6 — the
review's own grep, widened by this contract to the whole graduated slate). Of those 227, 102
live in `tests/orchestrator/test_replay.py` and 62 inside a single 549-line test class
(`:321-869`) whose job is to assert that constants are constant.

One correction to the register, made at HEAD and to be carried into the phase file: C-64
counts **ten** accept-and-ignore resolvers, listing `agents/strategic/prompts/loader.py:264`
and `orchestrator/replay.py:110` among them. Both are LIVE — they read
`AILIBI_IMPOSTOR_ROLL_CALL` and return its parsed value; the 18.10 impostor-answer arm is
still default-OFF because the CREW-ONLY ruling did not ship it. The true count of
accept-and-ignore resolvers was **nine** when C-64 was written and is **seventeen** at HEAD;
the nineteen-hit `def *_enabled(` grep is seventeen dead plus the same two live (now
`agents/strategic/prompts/loader.py:330` and `orchestrator/replay.py:117`). Likewise C-64's
"13 `ENV_*` constants" was the size of `_RETIRED_ALWAYS_ON_LEVERS` at review time (twenty-one
at HEAD), not the constant count: the four Phase-13.5 levers were swept
properly at Task 14.9 and left nothing behind, which is the existence proof that this sweep
is achievable.

The class HAS doubled. Task 20.36 (merged efcd43b8) recorded baseline 7 and, by owner
override of a FINDING verdict (`audits/audit-phase-20-baseline-7.md` §6.1), graduated all
eight Phase-20 levers built default-OFF in wave 2: their bodies now hard-return `True` and
their keys sit in `_RETIRED_ALWAYS_ON_LEVERS` — by construction exactly the same residue, in
exactly the same three modules, and it is already on disk to be swept. This task is the
first execution of craft rule 3 (`AGENTS.md:91-94`, "Retire means delete"), applied to both
generations at once, and it closes the loop by amending the older Graduation-sweeps rule at
`AGENTS.md:62-75`, which today demands only a *prose* sweep and explicitly blesses keeping
the function: *"the lever stays in the substrate stamp for provenance"*. That sentence is
true of the stamp KEY and false of everything else, and it is why nine dead functions
accumulated across five graduations.

Nothing observable moves. Every deleted branch is the branch production already takes, so the
committed bytes are the invariant and the gate is `verify_samples.sh` at 100/100 plus the
prompt byte-golden: if either moves, a deletion was not equivalent. The substrate stamp is
untouched — the keys stay in `_RETIRED_ALWAYS_ON_LEVERS`, `substrate_flag_snapshot()` keeps
stamping every one of them `True`, and a legacy replay stamped OFF keeps failing loud. What
goes is the resolver, its `env` parameter where nothing else reads one, the dead `if`, the
`ENV_*` constant, and the tests that pin a parameter — including the test class whose
docstring at `tests/meetings/test_manager.py:772` states the opposite of what its body
asserts (C-104's flagship example).

**Files in scope:**
- agents/memory/beliefs.py; (delete `evidence_quality_lift_enabled`, `reporter_exculpation_enabled`, `hard_evidence_gate_enabled`, `absence_prior_enabled`, their `ENV_*` constants and `__all__` entries, and collapse the read sites at :1463-1465, :1502, :1826, :1835, :1841; one history line per deleted lever)
- agents/memory/store.py; (same for `observation_id_rendering_enabled` and the `hard_evidence_gate_enabled` import; collapse `ids_on` at :280-286 and `gate_on` at :1632-1652; plus every Phase-20 store lever the record adopted)
- meetings/transcript.py; (same for `whereabouts_interior_flags_enabled` and `vent_placement_contradictions_enabled`; collapse :1554-1555 and delete the `whereabouts_interior_flags` parameter and its dead `False` branch at :2380-2410; plus every Phase-20 transcript lever the record adopted)
- meetings/manager.py; (same for `roll_call_round_enabled`; collapse :1185, :1759, :2018, :2448 and drop the `env` plumbing that only fed them; plus every Phase-20 manager lever the record adopted)
- meetings/constants.py; (delete `citation_gate_enabled`, `ENV_CITATION_GATE` and their `__all__` entries; every threshold constant STAYS — `DEFAULT_SKIP_CONFIDENCE_THRESHOLD:36`, and the Phase-20 additions `GROUNDED_PROSECUTION_MIN_SOURCES:84`, `MAP_ARBITRATION_MAX_HOPS:100`, `MAP_ARBITRATION_MAX_TICK_GAP:101`, whose levers graduated but whose thresholds are live policy; `UNCITED_ZERO_FLAG_EJECT_MARKER` is homed at `meetings/manager.py:369`, NOT here, and also stays)
- agents/strategic/prompts/loader.py; (the live 18.10 resolver STAYS, now at :330 — only its dangling `:func:` cross-references to deleted siblings at :319, :335, :337 are rewritten)
- orchestrator/replay.py; (the keys stay in `_RETIRED_ALWAYS_ON_LEVERS`; the resolver imports and any identity bindings for graduated levers go)
- tests/agents/; (the resolver-only classes and the tautology halves deleted; behaviour tests kept)
- tests/meetings/; (same, plus the new deletion-guard pin and its planted counter-case)
- AGENTS.md; (the Graduation-sweeps rule amended to "delete the mechanism, keep the stamp key and one history line", naming this task as its precedent)
- .env.example; (the newly graduated keys join the always-ON note; no lever gains a variable)
- orchestrator/game.py; (the `hard_evidence_gate_enabled` import at :45 and the `gate_on` read-site at :2795; the stale narration at :2791-2794 beside it)
- tests/orchestrator/test_replay.py; (the graduated resolver/constant imports and parameter pins)
- meetings/render_contract.py; (one dangling resolver reference)
- eval/meeting_quality.py; (one dangling resolver reference)
- tests/eval/test_meeting_quality.py; (same)
- tests/eval/test_evidence_honesty.py; (the graduated-lever ON slates and resolver tautologies listed in Section refs go, and its eight `detect_contradictions(env=…)` / `render_for_prompt(env=…)` sites follow the signature ruling; every CENSUS assertion is a keeper — this file holds the ratified §10/§11 instrument cells the baseline-7 record was read against, so no cell VALUE may move)
- tests/observation/test_leak_property.py and tests/orchestrator/test_meeting_integration.py; (three and two graduated `ENV_*` lines respectively, plus one `render_for_prompt(env=…)` at test_meeting_integration.py:3129)
- scripts/counterfactual_phase20.py; (the `env=` call sites at :538, :772, :942; `orchestrator/replay.py::env_var_for_lever:617` is a pure `f"AILIBI_{key.upper()}"` derivation, so the slate builders at :172-234 do NOT depend on the deleted `ENV_*` constants, and the memo's already-committed "the OFF column can no longer be produced" note at :140-143 stands)
- eval/funnel.py and eval/vj_instruments.py; (`agent.suspicion_graph_for_meeting(env={})` at funnel.py:1226 and `_suspicion_graph_with_contradictions(env={})` at vj_instruments.py:380, with the `env={}` narration at vj_instruments.py:78 and :358)
- audits/workflows/extract_gameplay_facts.py; (imports `ENV_WHEREABOUTS_INTERIOR_FLAGS` / `ENV_VENT_PLACEMENT_CONTRADICTIONS` at :127-128 and both resolvers at :141-142; builds a detector env from the stamp at :544-550; calls the resolvers at :2227-2234 inside an ambient-vs-stamp mismatch guard the graduation has made vacuous; and passes `detect_contradictions(env=…)` at :385, :591. `audits/` is NOT in the mypy/ruff exclude list, so this file BREAKS on the deletion)

Coordination note (routed from PR #384), RE-MEASURED at HEAD: seven of the eight comment-only forward references were already swept by the baseline-7 record. Exactly ONE survives, at meetings/transcript.py:1567-1569, and it is now doubly false — it still reads 'The movement-claim lever -- DEFAULT-OFF, live. Not registered in ``orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS``: Task 20.33 wires the whole Phase-20 slate…' when 20.33 DID register it and the baseline-7 record then graduated it. Sweep it here with the other residue; `grep -rn 'Not registered in' --include='*.py' agents meetings orchestrator` must read 0.

Orchestrator rulings (2026-08-26, pre-dispatch): (1) the WIDENED scope is adopted in ONE PR — both generations swept together (17 resolvers / 332 lines / 227 test env-lines), the seven newly-named consumer files included; Complexity re-rated Integration. (2) The 131-site mechanical `env=` call-site pass RIDES in this PR, audits/workflows/extract_gameplay_facts.py included — retire-means-delete does not leave the tree half-swept. (3) Deleting the ON-slate plumbing in tests/eval/test_evidence_honesty.py is ACCEPTED with the conservative bullet as written: no census assertion VALUE may move — 20.38/20.40/20.41 read those cells. (4) The grounded_prosecution parameter of _detect_alibi_vs_sightings is DATA-gated (`and bool(sighting_records)`), not lever-gated — folding it to True kills the 18.9 interior exemption; the reverifier's edit stands.

Recorded deviation at merge (PR #391, orchestrator-ratified): three prose-only comment fixes outside scope (meetings/schemas.py:165/:173, observation/service.py:68, tests/api/test_evidence_mechanisms.py:22-23) — stale references to deleted resolvers, mandated by the Graduation-sweeps rule this PR amends. Routed to 20.42's ledger: eval/replay_walk.py performs no substrate check (compute_pooling_funnel / VJ instruments would reconstruct always-on rules over earlier-substrate bytes); one-line fix via the now-public orchestrator.replay.retired_levers_stamped_off. A prose record, not scope entries.

**Files NOT in scope:**
- any lever the record did NOT adopt (it stays a live env-gated toggle with its resolver, parameter, tests and `.env.example` entry intact — the 18.10 impostor arm is the standing example)
- replays/ (the committed bytes are the pin, not an edit target; `verify_samples.sh` green is the invariant this task must not move)
- orchestrator/replay.py's `_TOGGLEABLE_LEVER_RESOLVERS` semantics and `substrate_flag_snapshot` behaviour (registration is not re-litigated here; only imports of deleted symbols change)
- the prompt templates under agents/strategic/prompts/qwen3_6_27b/ (no task except the single prompt-set bump may edit template bytes)
- tasks/ and agent_prompts/ (historical contracts record what was true when they were written and are never retro-edited)

**Definition of done:**
- [ ] Zero accept-and-ignore resolvers remain for graduated levers: a new AST-walking pin in `tests/meetings/test_lever_registry.py` parses every module under `agents/`, `meetings/` and `orchestrator/` and fails on any function whose name ends `_enabled` and whose body neither reads its `env` argument nor returns anything but a bare `True`; the pin ships with a planted counter-case (a fixture module written into `tmp_path` carrying exactly that shape) proving it bites.
- [ ] No `if <graduated>_enabled():` branch survives: each of the twenty-two verified read sites is replaced by its always-taken side. From the older nine: `ids_on`, `gate_on`, `lift_enabled`, `render_reporter` and the `absence_prior` disjunct in `meetings/manager.py:2631`. From the Phase-20 eight: the threaded booleans `completion_from_events`, `trail_on`, `meetings_on`, `coalesce_on` into `agents/memory/store.py::_build_observations`, `vents_are_content` at `agents/memory/store.py:836`, `structured_turn_markers` at `meetings/manager.py:1514`, and `movement_claim_shape` / `map_aware_arbitration` in `meetings/transcript.py::detect_contradictions`. `meetings/transcript.py::_detect_alibi_vs_sightings` loses its `whereabouts_interior_flags` and `map_aware_arbitration` parameters along with the `False` branch its own comment describes as reachable only by direct callers; its `grounded_prosecution` parameter STAYS, because `detect_contradictions:1849` ANDs the resolver with `bool(sighting_records)` and the caller-data half of that gate is live — the PR must show `interior_exempt` still evaluating both ways after the fold.
- [ ] The seventeen graduated `ENV_*` constants and their `__all__` entries are deleted; all twenty-one snake_case keys remain in `orchestrator/replay.py::_RETIRED_ALWAYS_ON_LEVERS` in graduation order, `SUBSTRATE_FLAG_KEYS` is unchanged in content and order (twenty-one retired + `impostor_roll_call`), and `substrate_flag_snapshot()` in a bare environment still stamps every retired key `True` — pinned by one consolidated test that replaces the per-lever repeats. `orchestrator/replay.py::env_var_for_lever:617` stays: it is the string derivation the recorder preflight and `scripts/counterfactual_phase20.py` read, and it depends on no deleted constant.
- [ ] An `env` parameter survives on a public function only where a LIVE resolver still reads it: `render_for_prompt`, `detect_contradictions`, `apply_contradiction_rule`, `apply_meeting_evidence_rules`, `_build_belief_lines`, `_suspicion_graph_with_contradictions`, `agents/memory/store.py::absorb_reported_testimony:762` (added with the Phase-20 meeting-outcome lever) and `TacticalAgent.suspicion_graph_for_meeting` each either keep `env` with a named live reader or lose it, and the PR states which and why for each. NOTE: after the baseline-7 record NO live resolver is reachable from any of these chains — the one live lever (`impostor_roll_call`) is read only in `agents/strategic/prompts/loader.py` — so the honest answer is that all of them lose `env`, which invalidates roughly 130 `env=` call sites across `scripts/`, `eval/`, `audits/` and `tests/`. The PR must land that as one mechanical pass, not leave a parameter nothing reads.
- [ ] The test residue is gone and the keepers survive: the eight resolver-only classes named in Section refs are deleted (`TestAbsencePriorResolver`, `TestHardEvidenceGateResolver`, `TestEvidenceQualityLiftResolver`, `TestObservationIdRenderLever`, `TestCitationGateLever`, `TestRollCallResolver`, `TestWhereaboutsInteriorFlagsResolver`, `TestVentPlacementContradictionsResolver`), `TestRollCallOffPath` at `tests/meetings/test_manager.py:791` is deleted or renamed so no test name or docstring describes an OFF path that cannot exist, `test_marker_literal_pinned_exactly` and the behaviour halves of `TestObservationIdRenderLever` are preserved verbatim, and the three ON-path assertions in `tests/agents/test_impostor_answer_arm.py` are untouched because that lever is live.
- [ ] The three Measurement greps read their target values and the PR Summary pastes all three with before/after; the default pytest tier is smaller by the deleted line count, which the PR quotes from `git diff --stat`.
- [ ] `bash scripts/verify_samples.sh` reports 100/100 and `tests/meetings/test_prompt_byte_golden.py` is green over every committed meeting; the golden still fails on a one-byte perturbation of a template body, demonstrated in the PR, so the no-behaviour-moved claim rests on a gate that can fail.
- [ ] `AGENTS.md`'s Graduation-sweeps section states the amended rule — delete the resolver, its parameter, the dead branch and the parameter-pinning tests; keep the stamp key and one history line; the prose sweep remains the smaller half — and names this task as the precedent, with craft rule 3 cross-referencing it instead of restating it.
- [ ] `.env.example` lists every graduated lever in the always-ON note with its adopting record, documents no variable for any of them, and still documents exactly the live toggles read from `orchestrator/replay.py::_TOGGLEABLE_LEVER_RESOLVERS`; the existing registry-cross-check test stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Do this one lever at a time, never as a bulk regex pass, and commit per lever so a bisect
lands on a single symbol. The 19.19 deletion pattern applies verbatim.

Step 1 — read the record's verdict first. Open the record audit written by the adopting task
and list, explicitly, which Phase-20 levers graduated. `_RETIRED_ALWAYS_ON_LEVERS` after that
commit is the authoritative list; anything still in `_TOGGLEABLE_LEVER_RESOLVERS` is LIVE and
this task must not touch its resolver, its parameter, its tests or its `.env.example` entry.
Write that list at the top of the PR description before editing anything.

Step 2 — per symbol, grep the consumers before deleting. For each resolver name and its
`ENV_*` constant run the blast-radius grep over the whole tree, not just the files in scope,
and read every hit. Expect hits in three shapes: real read sites (collapse them), `__all__`
entries (delete), and prose `:func:` cross-references in modules that are not in scope
(rewrite where the module is in scope, and report the rest rather than widening scope
silently). SEVEN consumer files sit outside the original contract's list and are now
named in Files in scope: `tests/eval/test_evidence_honesty.py`,
`tests/observation/test_leak_property.py`, `tests/orchestrator/test_meeting_integration.py`,
`scripts/counterfactual_phase20.py`, `eval/funnel.py`, `eval/vj_instruments.py` and
`audits/workflows/extract_gameplay_facts.py`. If an EIGHTH appears, stop and ask.

Step 3 — collapse, do not comment out. `ids_on = observation_id_rendering_enabled(env)`
followed by `if ids_on:` becomes the body of the `if`, dedented, with the guard gone. A
disjunct like `or (evidence.absent and absence_prior_enabled(env))` becomes `or
evidence.absent`. A ternary like `reporter_id if reporter_exculpation_enabled() else None`
becomes `reporter_id`. After each collapse run the module's own test file plus
`tests/meetings/test_prompt_byte_golden.py` before moving on — a wrong collapse shows up as a
prompt-byte diff immediately, and finding it one lever at a time costs minutes instead of a
bisect.

Step 4 — the parameter is the subtle part. `env` is threaded through several public
signatures purely to reach these resolvers. Delete it only where the grep proves no live
resolver is reached from that call chain; where a Phase-20 lever survived the record, `env`
survives with it. Leaving a parameter that nothing reads is the exact defect this task
exists to remove, and deleting one a live lever needs breaks the toggle silently, so record
the decision per signature in the PR.

Step 5 — the tests. Delete whole classes where the class exists only to assert a constant;
inside mixed classes delete only the tautology methods and keep the behaviour ones. Replace
the nine per-lever stamp repeats with one test that asserts the full retired tuple stamps
`True` under a bare mapping, an explicit "0", a junk value and the ambient process
environment — one test, four cases, the whole registry. The new AST guard belongs beside it;
give it a planted bad module in `tmp_path` so it is a gate rather than prose.

Step 6 — the docstrings that survive. Each lever's mechanism keeps one trailing provenance
line naming its adopting record, and nothing more; the 12-to-31-line narrations go with the
functions. Do not migrate the narration into the surviving mechanism docstring — that
converts a deletion into a move and the reader is no better off.

## Integration risk

The sweep touches five production modules and fourteen test files at once, and its failure mode is silent behavior change dressed as deletion — a data-gated parameter folded to a constant (the grounded_prosecution trap), a census value drifting under the plumbing rewrite, or a consumer script left importing a deleted symbol; every deletion must be proven behavior-neutral by the untouched census values and a green full gate, and the 131-site env pass must be purely mechanical (signature-following, no logic edits).

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
Open a PR from branch `phase-20-graduation-sweep` with a title like `task 20.37: retire means delete: the post-record graduation sweep and the old accept-and-ignore residue`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C-64 and C-104 in `audits/review-2026-08-19/B/collated-findings.md` §4 and §5; RC6 in `audits/review-2026-08-19/D/FINAL-synthesis.md` §1 ("the render-version stamp, plus one deletion pass"); the per-area sources `audits/review-2026-08-19/B/repo-health-architecture.md` §2 F6, `audits/review-2026-08-19/B/agents-memory.md` §2 F4, `audits/review-2026-08-19/B/meetings-transcript-voting.md` §2 F5, `audits/review-2026-08-19/B/meetings-manager.md` §2 P1-3, `audits/review-2026-08-19/B/orchestrator.md` §2 (the `suspicion_graph_for_meeting` dead-kwarg leg). Anchors RE-VERIFIED at HEAD: the seventeen accept-and-ignore resolvers `agents/memory/store.py:242,273,315,340,369`, `agents/memory/beliefs.py:190,224,292,407`, `meetings/constants.py:54`, `meetings/transcript.py:1515,1542,1575,1600,1628`, `meetings/manager.py:887,929` (332 source lines in total, each ending `del env  # retired: the lever is unconditional, no environment is consulted`); their seventeen `ENV_*` constants `agents/memory/store.py:239,270,294,335,362`, `agents/memory/beliefs.py:187,221,289,404`, `meetings/constants.py:51`, `meetings/manager.py:884,926`, `meetings/transcript.py:1507,1512,1572,1597,1625` and the seventeen matching `__all__` entries; the twenty-two production read sites `agents/memory/store.py:563,566,568,571,574,836,2357` (paired guards `:602`, `:2377`), `agents/memory/beliefs.py:1463,1826,1835,1841` (paired guards `:1465`, `:1502`), `meetings/manager.py:1323,1514,1941,2201,2631`, `meetings/transcript.py:1841,1842,1844,1849,1852`, `orchestrator/game.py:2795` — the original thirteen for the nine older levers plus nine more for the eight Phase-20 levers; the dead private-helper parameters `meetings/transcript.py:2924-2932` — `_detect_alibi_vs_sightings` now takes THREE lever booleans (`whereabouts_interior_flags`, `grounded_prosecution`, `map_aware_arbitration`), of which only `grounded_prosecution` stays live-shaped because `detect_contradictions:1849` ANDs the resolver with `bool(sighting_records)` — with the "survives only for direct callers" comment at `:2953-2956` and the `interior_exempt` expression at `:2963-2965`; the stamp registry `orchestrator/replay.py:524-546` (`_RETIRED_ALWAYS_ON_LEVERS`, TWENTY-ONE keys since the baseline-7 record) and `:568-570` (`_TOGGLEABLE_LEVER_RESOLVERS`, still one live entry); the rule this task amends, `AGENTS.md:62-75` (Graduation sweeps) beside craft rule 3 at `AGENTS.md:91-94`; `.env.example:88-118` (the graduated always-ON note, ALREADY rewritten to twenty-one levers with their adopting records by the baseline-7 record — verify rather than re-author); the test residue `tests/agents/test_absence_prior.py:166-216`, `tests/agents/test_beliefs_hard_evidence_gate.py:86-115`, `tests/agents/test_beliefs.py:2735-2761`, `tests/agents/test_episodic_ids.py:391-467`, `tests/meetings/test_citation_gate.py:127-158`, `tests/meetings/test_manager.py:494-529` and `:791` (`TestRollCallOffPath`, whose docstring says the round is skipped while its test asserts the round fires), `tests/meetings/test_contradictions.py:1581-1667` (TWO resolver classes: `TestWhereaboutsInteriorFlagsResolver:1581` and `TestVentPlacementContradictionsResolver:1621`); and the Phase-20 residue this task inherits — `tests/eval/test_evidence_honesty.py` ON-slates `_TRAIL_ON:1632`, `_MOVEMENT_ON:2002`, `_GROUNDED_ON:2583`, `_MAP_AWARE_ON:3137`, `_COALESCE_ON:3456` plus resolver tautologies at `:1417` and `:1920-1922`, `tests/agents/test_memory_rendering.py`, `tests/agents/test_reported_testimony.py`, `tests/agents/test_memory_meeting_history.py`, `tests/observation/test_leak_property.py`, `tests/orchestrator/test_meeting_integration.py`), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
