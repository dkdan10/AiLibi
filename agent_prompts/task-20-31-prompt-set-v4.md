# Agent Prompt — 20.31 The prompt-set bump v3 → v4: proof vs conflicting accounts, the impostor count, no threshold talk, no dead-subject vent mandate, the map card

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.31 — The prompt-set bump v3 → v4: proof vs conflicting accounts, the impostor count, no threshold talk, no dead-subject vent mandate, the map card, anchored to review register ids — G-2 prompt, G-23, G-27, G-29 and R12 in audits/review-2026-08-19/A/collated-findings.md §A (G-2, lines 33-49), §C (G-23, lines 307-318), §D (G-27, lines 354-366; G-29, lines 378-386) and audits/review-2026-08-19/A/ideas-multi-agent-researcher.md R12; the adversarial verdicts in audits/review-2026-08-19/A/verdicts.md claim 2 (CONFIRMED-DESIGN-CHOICE: the "VERIFIED evidence" framing verbatim in 2,543/2,543 recorded ballot prompts; the class is 14.6% precise as sole convicting evidence) and claim 11 (b) (CONFIRMED: all six templates hard-code a singular impostor; 1,956/1,956 and 5,502/5,502 prompts; the stated win condition is arithmetically wrong for two impostors); C-129 in audits/review-2026-08-19/B/collated-findings.md line 194 ("the render contract carries no impostor count, so the templates *cannot* say it right") and F9/F12 in audits/review-2026-08-19/B/llm-and-prompts.md; the roadmap items in audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 rows 2.6, 2.7, 2.9 and the R1+R12 half of row 2.5, with the wave's own ordering ruling "2.6+2.7+2.9 batched into ONE prompt-version bump". Anchors re-verified at HEAD: the singular persona at agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:58, impostor_report.j2:59, accusation_round.j2:79, vote_ballot.j2:74 and the two variant siblings accusation_round_roll_call.j2:76, impostor_report_roll_call.j2:69; the "VERIFIED evidence" block at vote_ballot.j2:100 (and its echo "whose account a verified flag broke" at :144); the turn-phase framing "Evidence, not verdicts:" at accusation_round.j2:145; the threshold arithmetic at vote_ballot.j2:139-144; the vent-first mandate with no dead-subject exemption at crewmate_report.j2:95, accusation_round.j2:186 and :189; the version markers at each template's line 3; the registry at orchestrator/game.py:350-384 (`PROMPT_VERSION_SETS`) and :404-410 (`IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`); the archive seam at tests/meetings/test_prompt_byte_golden.py:167-181 (empty since the 16.17 retirement), its resolution at :432-449, its renderer binding at :828-841 and the perturbation leg at :1134-1181; the registry pin at tests/agents/test_bespoke_prompt_sets.py:517-533; the evidence taxonomy at api/schemas.py:704-762 (`EvidenceCategory` at :704, `ROLE_PROOF_KINDS` at :755, `CROSS_STATEMENT_KINDS` at :760-762) and :775-834 (`classify_evidence`); the weak predicate at meetings/transcript.py:633 (`WEAK_CONTRADICTION_MARKER_PREFIX`) and :912-931 (`is_weak_contradiction`); the ballot scrape at eval/_suspicion_parse.py:34-56, whose two offline consumers are eval/meeting_quality.py and eval/vj_instruments.py; the public topology at observation/public_map.py:14-32; the ten walkable rooms and eleven one-tick edges at engine/maps/canonical_1.yaml:69-175 and :176-203; the DETECTOR's own frozen copy of that same graph at meetings/transcript.py:839-852 (`CANONICAL_ROOM_NEIGHBORS`, landed by the 20.27 dependency, pinned equal to `engine.world.load_canonical_map().room_neighbors` with every edge at one tick) — the table the rendered card must agree with, since it is what makes "one adjacency graph" true rather than asserted; the render Protocols at meetings/render_contract.py:134-147, :199-215, :257-271; the renderer construction seam at agents/strategic/prompts/loader.py:694-773 and orchestrator/game.py:895-977 (`build_default_meeting_runner`); and the per-game seam that already carries a render-only roster from world state into the renderers at orchestrator/game.py:840-864 (`DefaultMeetingRunner.run_meeting`, the Task-10.3 `dead_ids` derivation) through `MeetingManager.run` at meetings/manager.py:1091-1098.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-prompt-set-v4`
**Depends on:** 20.19, 20.27, 20.29, 20.30 — the cached Jinja environment lands first so the new per-game render inputs bind per call instead of being baked into a memoized environment, and it edits the same loader file; the map-aware flag arbitration lands first so the detector and the agents read ONE adjacency graph, never a prompt promising a reconciliation rule the detector does not apply; the meetings-record memory block lands first so an agent's memory can say who is already ejected before the prompt tells it to leave a closed case alone, and it edits the same orchestrator file; the memory-render budget rework lands first so the lines this bump adds are not the first thing the budget sheds.
**Section refs:** review register ids — G-2 prompt, G-23, G-27, G-29 and R12 in audits/review-2026-08-19/A/collated-findings.md §A (G-2, lines 33-49), §C (G-23, lines 307-318), §D (G-27, lines 354-366; G-29, lines 378-386) and audits/review-2026-08-19/A/ideas-multi-agent-researcher.md R12; the adversarial verdicts in audits/review-2026-08-19/A/verdicts.md claim 2 (CONFIRMED-DESIGN-CHOICE: the "VERIFIED evidence" framing verbatim in 2,543/2,543 recorded ballot prompts; the class is 14.6% precise as sole convicting evidence) and claim 11 (b) (CONFIRMED: all six templates hard-code a singular impostor; 1,956/1,956 and 5,502/5,502 prompts; the stated win condition is arithmetically wrong for two impostors); C-129 in audits/review-2026-08-19/B/collated-findings.md line 194 ("the render contract carries no impostor count, so the templates *cannot* say it right") and F9/F12 in audits/review-2026-08-19/B/llm-and-prompts.md; the roadmap items in audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 rows 2.6, 2.7, 2.9 and the R1+R12 half of row 2.5, with the wave's own ordering ruling "2.6+2.7+2.9 batched into ONE prompt-version bump". Anchors re-verified at HEAD: the singular persona at agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:58, impostor_report.j2:59, accusation_round.j2:79, vote_ballot.j2:74 and the two variant siblings accusation_round_roll_call.j2:76, impostor_report_roll_call.j2:69; the "VERIFIED evidence" block at vote_ballot.j2:100 (and its echo "whose account a verified flag broke" at :144); the turn-phase framing "Evidence, not verdicts:" at accusation_round.j2:145; the threshold arithmetic at vote_ballot.j2:139-144; the vent-first mandate with no dead-subject exemption at crewmate_report.j2:95, accusation_round.j2:186 and :189; the version markers at each template's line 3; the registry at orchestrator/game.py:350-384 (`PROMPT_VERSION_SETS`) and :404-410 (`IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`); the archive seam at tests/meetings/test_prompt_byte_golden.py:167-181 (empty since the 16.17 retirement), its resolution at :432-449, its renderer binding at :828-841 and the perturbation leg at :1134-1181; the registry pin at tests/agents/test_bespoke_prompt_sets.py:517-533; the evidence taxonomy at api/schemas.py:704-762 (`EvidenceCategory` at :704, `ROLE_PROOF_KINDS` at :755, `CROSS_STATEMENT_KINDS` at :760-762) and :775-834 (`classify_evidence`); the weak predicate at meetings/transcript.py:633 (`WEAK_CONTRADICTION_MARKER_PREFIX`) and :912-931 (`is_weak_contradiction`); the ballot scrape at eval/_suspicion_parse.py:34-56, whose two offline consumers are eval/meeting_quality.py and eval/vj_instruments.py; the public topology at observation/public_map.py:14-32; the ten walkable rooms and eleven one-tick edges at engine/maps/canonical_1.yaml:69-175 and :176-203; the DETECTOR's own frozen copy of that same graph at meetings/transcript.py:839-852 (`CANONICAL_ROOM_NEIGHBORS`, landed by the 20.27 dependency, pinned equal to `engine.world.load_canonical_map().room_neighbors` with every edge at one tick) — the table the rendered card must agree with, since it is what makes "one adjacency graph" true rather than asserted; the render Protocols at meetings/render_contract.py:134-147, :199-215, :257-271; the renderer construction seam at agents/strategic/prompts/loader.py:694-773 and orchestrator/game.py:895-977 (`build_default_meeting_runner`); and the per-game seam that already carries a render-only roster from world state into the renderers at orchestrator/game.py:840-864 (`DefaultMeetingRunner.run_meeting`, the Task-10.3 `dead_ids` derivation) through `MeetingManager.run` at meetings/manager.py:1091-1098.
**Complexity:** Integration
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/meetings/test_prompt_byte_golden.py tests/agents tests/orchestrator tests/meetings -q` green; `grep -c "VERIFIED evidence" agents/strategic/prompts/qwen3_6_27b/*.j2` reads 0 on every file; `uv run python scripts/measure_baseline.py --honesty` over a fresh fake-provider 9p2i tournament reads the singular-persona cell 0/N where the committed baseline-6 bytes read 1,956/1,956; `bash scripts/verify_samples.sh` stays 100/100 and the prompt byte-golden still fails on a one-byte perturbation of the ARCHIVED v3 body (both runs quoted in the PR Summary).

The ballot prompt tells every voter that a bookkeeping artifact is proof.
`vote_ballot.j2:100` reads "Each flag below is VERIFIED evidence, not a verdict … never
side with [an unverified counter-accusation] over a verified flag", and the review found
that sentence in 2,543 of 2,543 recorded ballot prompts
(audits/review-2026-08-19/A/verdicts.md claim 2, review-measured over the committed
baseline-6 bytes; the phrase COUNT itself is not a committed cell — 20.15 shipped rows
I-2…I-11 and pinned the CLASS instead: sole-flag precision 12/82 as I-3 and the singular
persona 1,956/1,956 as I-9, both in tests/eval/test_evidence_honesty.py). The
flags that sentence dignifies are not one class: a grounded `vent_sighting` is
engine-certified and names an impostor 440 times out of 440, while `alibi_vs_sighting`
compares one spoken alibi against one spoken sighting and, as the sole convicting evidence
in a meeting, is right 12 times and wrong 70 — 14.6% precision against a 25.3% base rate.
The product already knows the difference: `api/schemas.py:704-762` defines
`EvidenceCategory` as `role_proof` / `cross_statement` / `weak_signal` and the spectator
renders the three apart. The agents have never been told. This task makes the prompt speak
the taxonomy the code already holds, and deletes the word that converts an artifact into a
conviction. It does NOT widen the taxonomy: `alibi_vs_physical` stays `cross_statement` on
both surfaces, because api/schemas.py:721-737 records that widening it is one decision
taken once, in two cross-pinned places.

Three more prompt defects ride the same bump, because the wave's own ordering ruling
batches them into one version layer (audits/review-2026-08-19/D/FINAL-synthesis.md §4,
"2.6+2.7+2.9 batched into ONE prompt-version bump"). Every template hard-codes a singular
hidden impostor and a parity sentence that is arithmetically wrong for two — present in
1,956/1,956 and 5,502/5,502 recorded prompts, and self-contradicting inside one prompt
where a crewmate persona line sits ninety lines above "Your fellow saboteurs: p-8"
(verdicts claim 11 (b)). C-129 names the mechanism exactly: the render contract carries no
impostor count, so the templates cannot say it right. The vent-first mandate at
crewmate_report.j2:95 and accusation_round.j2:186 orders a witness to re-speak a held vent
"even if you already said it at an earlier meeting" with no exemption for a subject who is
already dead or ejected — 232 `saw_vent` observations in the corpus name a corpse and
5.0-5.5% of turns lose their accusation to one (G-23). And the ballot's §4.6 bookkeeping
block is recited back in the characters' voices, "the 0.60 threshold" quoted 208 times
corpus-wide (G-29).

The one thing the prompts do not contain is the map. R12 measured 0 of 7,458 prompts
carrying any room list, adjacency or travel time, while 148 of 234 STRONG
`alibi_vs_sighting` flags name rooms one doorway apart — a single tick of walking
reconciles both statements. The arbitration half of that finding is the map-aware detector
lever this task depends on; this is its agent-side half, so the detector and the agents
reason over the same graph instead of the agents guessing at a geometry only the engine
can see. The canonical map is small enough to publish honestly: ten walkable rooms, eleven
edges, every one of them one tick (engine/maps/canonical_1.yaml:176-203).

This is the ONE prompt-template edit Phase 20 allows; no other task in the phase may touch
a `.j2` body, and this task touches only the locked `qwen3_6_27b` set. It is "default-OFF"
in the phase's sense without introducing any `AILIBI_*` lever: the loader's default set is
the frozen `qwen3_5_9b` reference set (agents/strategic/prompts/loader.py:133), so a bare
environment renders zero v4 bytes, and the 300 committed games keep resolving their
recorded `*.qwen3_6_27b.v3` stamps through the bump-in-flight archive that Task 16.15
built and the 16.17 re-record retired empty. That means this task introduces no
`*_enabled` resolver and registers nothing in the substrate stamp — it is the one Phase-20
wave-2 change whose gate is the existing `AILIBI_PROMPT_SET` selector plus the archive
seam, and the adopting record is what retires the archive again.

**Files in scope:**
- agents/strategic/prompts/qwen3_6_27b/*.j2; (the four default templates → v4, the two `*_roll_call` variant bodies byte-untouched on their v1 lineage: the flag block split into 'Proof' (engine-certified: vent_sighting) and 'Conflicting accounts' (alibi_conflict, alibi_vs_sighting, alibi_vs_physical — the committed `CROSS_STATEMENT_KINDS`, not widened here) with honest wording and no 'VERIFIED evidence' phrasing for the latter; persona parameterised by impostor count with the correct parity sentence; the vent-first mandate exempts dead/ejected subjects; no threshold arithmetic in the agent's voice; a compact adjacency card ('Rooms and doors: …') rendered from the public map view; the saw_move observation shape listed)
- agents/strategic/prompts/loader.py; (the impostor-count and map-card render inputs)
- meetings/render_contract.py; (the v4 contract)
- orchestrator/game.py; (PROMPT_VERSION_SETS qwen3_6_27b → v4; IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS stays v1 for the variant templates; the render inputs threaded)
- tests/fixtures/prompt_archive/qwen3_6_27b_v3/; (new: byte-copies of the six v3 bodies)
- tests/meetings/test_prompt_byte_golden.py; (ARCHIVED_PROMPT_VERSION_SETS gains the v3 entry; the committed meetings still golden through the archive)
- tests/orchestrator/test_replay_meetings.py; (VERIFY-ONLY — re-checked at HEAD: it pins the FROZEN DEFAULT-set stamps `accusation_round.v9` / `crewmate_report.v8` / `impostor_report_v6` at :443-445, names neither `qwen3_6_27b` nor `AILIBI_PROMPT_SET`, and therefore must NOT move; if it goes red the bump has leaked out of the locked set into the default path)
- tests/orchestrator/test_meeting_integration.py; (same — its one live pin is the default-set `crewmate_report.v8` at :2542; verify-only, no edit)
- tests/agents/test_strategic_prompts.py; (v4 render pins: plural persona in a 2i game, singular in a 1i game; the proof/conflict split; no 'VERIFIED evidence' string; dead-subject exemption text; the map card)
- tests/agents/test_bespoke_prompt_sets.py; (same)
- tests/meetings/test_persona_render.py
- tests/eval/test_evidence_honesty.py; (the singular-persona cell reads 0/N under v4 on a fake tournament)
- meetings/manager.py; (render-input threading only — the impostor count and the map card reach the renderer; optional kwargs with defaults so non-test callers need no change)
- scripts/record_ml_corpus.sh; (the REQUIRED_PROMPT_VERSIONS re-lock — the recorder's version pin moves WITH the registry)
- tests/scripts/test_record_ml_corpus.py; (the registry-equality pin)
- tests/agents/test_impostor_answer_arm.py; (the variant registry's inherited keys follow the set to v4)
- tests/meetings/test_elicitation_fixtures.py; (the two removed threshold-block phrases)

**Files NOT in scope:**
- every other prompt set directory (frozen references; untouched — in particular the DEFAULT `qwen3_5_9b` set, whose crewmate_report.j2:72 carries the "do NOT emit a `found_body` observation" string two integration suites assert; those assertions stay green precisely because the frozen set does not move)
- replays/ (committed bytes resolve through the archive; nothing moves, no re-record happens here)
- orchestrator/replay.py and the substrate stamp (this bump introduces no lever key at all — there is nothing for the stamp-registration task to register; the gate is the existing prompt-set selector plus the archive)
- api/schemas.py and eval/deduction_metrics.py (the evidence taxonomy is consumed and cross-pinned, never widened — moving `alibi_vs_physical` out of `cross_statement` is a separate two-place decision)
- eval/_suspicion_parse.py (its regex is a constraint on the v4 render, not an edit target)

**Definition of done:**
- [ ] The ballot and turn flag blocks render the committed taxonomy: flags are grouped "Proof" (`role_proof`) and "Conflicting accounts", with the detector's weak stamp shown as its own subordinate group; the grouping is computed in Python from `ContradictionRef.kind` plus `meetings.transcript.is_weak_contradiction`, never re-derived in Jinja; `grep -c "VERIFIED evidence"` over the set reads 0 and vote_ballot.j2's "whose account a verified flag broke" echo is gone. Pinned in `tests/meetings/test_persona_render.py`.
- [ ] The render-side split is cross-pinned against `api.schemas.classify_evidence` over every flag in both committed sample sets (identical per-category counts), so the agents' view and the spectator's view cannot drift; `alibi_vs_physical` classifies `cross_statement` on both sides and the test says why. Pinned in `tests/meetings/test_persona_render.py`.
- [ ] The persona sentence and the win condition are parameterised by the game's impostor count: a two-impostor render says two hidden impostors and states the parity condition correctly, a one-impostor render keeps the singular wording, and the teammate line's grammar is correct for one and for many. Pinned in `tests/agents/test_bespoke_prompt_sets.py`; the fresh-tournament cell in `tests/eval/test_evidence_honesty.py` reads 0 singular-persona strings where the committed bytes read 1,956/1,956.
- [ ] The vent-first mandate carries a dead/ejected-subject exemption in every branch that states it (crewmate_report.j2:95 and BOTH branches of accusation_round.j2, :186 and :189), while "speak it FIRST" and "already said it at an earlier meeting" survive verbatim for the branches that still hold an open case. Pinned per branch in `tests/meetings/test_persona_render.py`.
- [ ] Threshold arithmetic leaves the agent's voice: no template asks the model to reason in threshold arithmetic or to name a numeric cutoff in prose it will parrot, and the ballot explicitly forbids quoting bookkeeping numbers in `rationale_text`. The rendered clause "maximum suspicion among the living ejection targets is **X**" survives byte-shaped — a test asserts `eval._suspicion_parse.VOTE_MAX_SUSPICION_RE` still matches a freshly rendered v4 ballot and captures the same value, because that line is the only per-ballot gate input that survives into a replay and two offline consumers read it on the new record.
- [ ] The map card renders in every meeting template this bump edits (the four defaults; the two `*_roll_call.j2` siblings stay byte-untouched) as at most twelve lines from `PublicMapView.room_neighbors` over the ten walkable rooms, stating the one-tick doorway fact once; `vent_graph` and `vent_rooms` never render — a negative assertion names each vent id and fails if any appears. Pinned in `tests/agents/test_bespoke_prompt_sets.py`.
- [ ] The movement observation shape introduced upstream is listed in the schema block of the turn templates, so an agent can speak the claim the detector now reads.
- [ ] The bump-in-flight seam is exact: all six pre-PR bodies are byte-copied to `tests/fixtures/prompt_archive/qwen3_6_27b_v3/` (the four default templates because the recorded stamps resolve through them, the two untouched variant siblings so the archived directory is a complete loadable set), `ARCHIVED_PROMPT_VERSION_SETS` gains the v3 entry keyed to the four recorded stamps, and the golden still re-renders every meeting of both committed sample sets byte-identically through the archive. The PR quotes a byte-level diff of each archived copy against its pre-PR body (a one-byte difference silently voids 204 goldens).
- [ ] The perturbation leg still proves the golden can fail, re-targeted at the ARCHIVED v3 body — perturbing the live v4 set is a no-op for the golden during the window, and the test's docstring says so; the v4 bodies are guarded instead by the render pins above, which the PR demonstrates by quoting one deliberately perturbed run of each.
- [ ] `PROMPT_VERSION_SETS['qwen3_6_27b']` resolves to four `*.qwen3_6_27b.v4` stamps, no value contains `.v1`, `.v2` or `.v3`, and the renamed pin in `tests/agents/test_bespoke_prompt_sets.py` asserts it; the roll-call variant registry still resolves and its two variant-file stamps keep their own lineage; the two `*_roll_call.j2` bodies are byte-untouched and the PR records their unfixed singular persona as a deliberate deferral, with the reason (an unrecorded, default-OFF arm) for the phase-close ledger.
- [ ] The frozen default path is unmoved: with `AILIBI_PROMPT_SET` unset every render is byte-identical to HEAD, `bash scripts/verify_samples.sh` stays 100/100, and `uv run python scripts/regen_test_goldens.py --check` is clean (its two targets derive from ML evidence bytes and are unaffected by construction — the PR says so rather than implying the check validates the bump).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — inventory before you edit. Run `git grep -n 'assert "'
tests/meetings/test_elicitation_fixtures.py tests/meetings/test_persona_render.py
tests/agents/test_bespoke_prompt_sets.py tests/agents/test_impostor_answer_arm.py` and
write down every rendered phrase those suites assert on the locked set. Most must survive
verbatim ("speak it FIRST", "one room, one tick", "Every EJECT names its evidence", "SKIP
is the sound call", the seven-key output contract, the worked `[obs p-2:12:0]` example).
Exactly three should break, and they are the point of the task: the two threshold-block
phrases the elicitation suite asserts, and the persona/flag strings. A phrase you break by
accident is a silent behaviour change riding a wording change.

Step 2 — the render inputs. Add one frozen dataclass to meetings/render_contract.py
carrying the game's impostor count and the pre-rendered map card, and one additive
defaulted keyword on the three render Protocols; a default of None keeps every existing
call site valid and every existing render byte-identical. Bind the inputs onto the four
renderer callables — never into the Jinja Environment, whose memo `_environment_for_set`
(loader.py:245-255) is keyed on set and root and nothing else, so per-game values must not
enter it. Split the two inputs by their lifetime, because only one of them is bindable at
construction. The MAP CARD is a constant of the canonical map: build it in the loader and
bind it onto the four renderer callables at construction (`functools.partial`, the same
discipline the roll-call lever already uses — resolved once at construction at
loader.py:741, bound at :760-772). The IMPOSTOR COUNT is per-game and CANNOT be bound
there: `build_prompt_renderers` is only reached through `build_default_meeting_runner`,
and every caller that knows a roster — eval/balance_eval.py:359, scripts/run_game.py:91,
eval/benchmark.py:124, eval/leak_scan.py:938 and the training harnesses — is out of scope
and passes none. Thread it the way `dead_ids` already travels: derive it in
`DefaultMeetingRunner.run_meeting` from the `WorldState` that seam already reads
(orchestrator/game.py:840-864) and pass it through `MeetingManager.run`
(meetings/manager.py:1091-1098) to the renderers — both files are in scope and no
out-of-scope call site moves. The card itself is built
in the loader from the public map view: agents may import observation, and rendering the
room list plus its one-tick doorways keeps the meetings leaf free of any topology import;
cross-pin the rendered adjacency against `meetings.transcript.CANONICAL_ROOM_NEIGHBORS` so
the card and the 20.27 detector cannot disagree.

Step 3 — the flag split. Classify each `ContradictionRef` in Python with the api table's
rules, sourced from what the meetings layer already exports: role proof when the kind is
`vent_sighting` or the two event ids are the same artifact, weak when
`meetings.transcript.is_weak_contradiction` is true, cross-statement otherwise. Pass the
three groups into the template context so Jinja only loops. Then cross-pin the result
against `api.schemas.classify_evidence` on the committed flags — the test may import both;
the production code must not, which is exactly why the cross-pin is the evidence.

Step 4 — the wording. Write the "Conflicting accounts" preamble so it states what is true
and nothing more: two accounts cannot both be true, nothing here says which one is wrong,
and a flag is a question to test against the transcript. The proof preamble keeps the
strength the vent channel has earned. For the persona, say the count in words rather than
a bare integer and derive the parity sentence from it, so a one-impostor render is the
sentence the four-player roster has always had. For the vent mandate, add the exemption
without touching the priority clause. For the threshold, keep the rendered maximum, drop
the numeric cutoff from the prose, and add one line telling the model the bookkeeping is
for its decision, not for its rationale.

Step 5 — the seam, in this order. Copy the four default v3 bodies into the archive
directory BEFORE editing them (`git show HEAD:<path>` into the new file is the safest
copy), register the archive entry, then edit the live bodies, then bump the version
markers on line 3 of each edited template, then the registry, then re-target the
perturbation victim. Run the golden after each of the first two steps: it must be green
after the archive lands and still green after the live bodies move.

Step 6 — the cascade. A registry bump has a known fan-out (the version-bump cascade in the
project's standing notes): the template line-3 markers, the registry entry, the variant
registry's inherited keys, the registry pin test, the recorder's locked-version constant
and the test that asserts the two agree. Walk all of them and quote the grep in the PR;
the manifest columns read as-recorded and do not move.

Step 7 — the cells. Run a small fake-provider 9p2i tournament with the set exported and
read the singular-persona cell; it must be zero. Quote the before/after beside the
committed 1,956/1,956 in the PR Summary, since the counterfactual task and the
pre-registration both consume this number.

## Public types this task introduces
- `meetings.render_contract.PromptRenderInputs`
- `agents.strategic.prompts.loader.render_map_card`
- `agents.strategic.prompts.loader.classify_flag_for_prompt`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

The widest prompt change since the persona-voice layer, and the only prompt edit this
phase allows. Three hazards, in order of how quietly they fail.

First, the blocking cascade item — verified present in Files-in-scope at HEAD (both `scripts/record_ml_corpus.sh` and `tests/scripts/test_record_ml_corpus.py` are listed), and it stays blocking:
`tests/scripts/test_record_ml_corpus.py:524`
(`test_prompt_version_registry_matches_locked_script_constant`) asserts that
`PROMPT_VERSION_SETS['qwen3_6_27b']` still equals the shell constant
`REQUIRED_PROMPT_VERSIONS` at `scripts/record_ml_corpus.sh:155`, and the recorder itself
re-asserts it at preflight. The moment the registry reads v4 that test goes red and the
full suite cannot pass, so the re-lock must ride this PR exactly as the baseline-6
record's contract required. Confirm the scope line covers it before starting; if it does
not, stop and raise it rather than shipping a red suite or a recorder that refuses to
start on the eve of a 23-hour record.

Second, byte-exactness in both directions. Every load-bearing rendered phrase the
locked-set suites assert must survive verbatim so that only the version string and the
intended lines break; and the archived v3 copies must be exact — a single trailing newline
difference leaves 204 committed meetings "golden" against bodies they never rendered,
which is worse than a red gate. Verify the copies with a byte diff, not by eye. Note also
that during the window the golden's teeth move: the live v4 templates are exercised by no
committed byte, so the perturbation leg must attack the archive or it silently stops
proving anything.

Third, the two things the change must not leak or lose. The impostor COUNT is a public
game setting — the roster preset and its impostor count are stated in the design and in
every set's name — so rendering it to crewmates leaks nothing; say that in the render
input's docstring so a later reader does not "fix" it back. And the map card must render
walkable-room adjacency only: vent topology is impostor-only knowledge that the same
public view happens to carry, and publishing it to the table would convert a legibility
fix into a firewall breach.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.leak_scan"`
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
Open a PR from branch `phase-20-prompt-set-v4` with a title like `task 20.31: the prompt-set bump v3 → v4: proof vs conflicting accounts, the impostor count, no threshold talk, no dead-subject vent mandate, the map card`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing review register ids — G-2 prompt, G-23, G-27, G-29 and R12 in audits/review-2026-08-19/A/collated-findings.md §A (G-2, lines 33-49), §C (G-23, lines 307-318), §D (G-27, lines 354-366; G-29, lines 378-386) and audits/review-2026-08-19/A/ideas-multi-agent-researcher.md R12; the adversarial verdicts in audits/review-2026-08-19/A/verdicts.md claim 2 (CONFIRMED-DESIGN-CHOICE: the "VERIFIED evidence" framing verbatim in 2,543/2,543 recorded ballot prompts; the class is 14.6% precise as sole convicting evidence) and claim 11 (b) (CONFIRMED: all six templates hard-code a singular impostor; 1,956/1,956 and 5,502/5,502 prompts; the stated win condition is arithmetically wrong for two impostors); C-129 in audits/review-2026-08-19/B/collated-findings.md line 194 ("the render contract carries no impostor count, so the templates *cannot* say it right") and F9/F12 in audits/review-2026-08-19/B/llm-and-prompts.md; the roadmap items in audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 rows 2.6, 2.7, 2.9 and the R1+R12 half of row 2.5, with the wave's own ordering ruling "2.6+2.7+2.9 batched into ONE prompt-version bump". Anchors re-verified at HEAD: the singular persona at agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:58, impostor_report.j2:59, accusation_round.j2:79, vote_ballot.j2:74 and the two variant siblings accusation_round_roll_call.j2:76, impostor_report_roll_call.j2:69; the "VERIFIED evidence" block at vote_ballot.j2:100 (and its echo "whose account a verified flag broke" at :144); the turn-phase framing "Evidence, not verdicts:" at accusation_round.j2:145; the threshold arithmetic at vote_ballot.j2:139-144; the vent-first mandate with no dead-subject exemption at crewmate_report.j2:95, accusation_round.j2:186 and :189; the version markers at each template's line 3; the registry at orchestrator/game.py:350-384 (`PROMPT_VERSION_SETS`) and :404-410 (`IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`); the archive seam at tests/meetings/test_prompt_byte_golden.py:167-181 (empty since the 16.17 retirement), its resolution at :432-449, its renderer binding at :828-841 and the perturbation leg at :1134-1181; the registry pin at tests/agents/test_bespoke_prompt_sets.py:517-533; the evidence taxonomy at api/schemas.py:704-762 (`EvidenceCategory` at :704, `ROLE_PROOF_KINDS` at :755, `CROSS_STATEMENT_KINDS` at :760-762) and :775-834 (`classify_evidence`); the weak predicate at meetings/transcript.py:633 (`WEAK_CONTRADICTION_MARKER_PREFIX`) and :912-931 (`is_weak_contradiction`); the ballot scrape at eval/_suspicion_parse.py:34-56, whose two offline consumers are eval/meeting_quality.py and eval/vj_instruments.py; the public topology at observation/public_map.py:14-32; the ten walkable rooms and eleven one-tick edges at engine/maps/canonical_1.yaml:69-175 and :176-203; the DETECTOR's own frozen copy of that same graph at meetings/transcript.py:839-852 (`CANONICAL_ROOM_NEIGHBORS`, landed by the 20.27 dependency, pinned equal to `engine.world.load_canonical_map().room_neighbors` with every edge at one tick) — the table the rendered card must agree with, since it is what makes "one adjacency graph" true rather than asserted; the render Protocols at meetings/render_contract.py:134-147, :199-215, :257-271; the renderer construction seam at agents/strategic/prompts/loader.py:694-773 and orchestrator/game.py:895-977 (`build_default_meeting_runner`); and the per-game seam that already carries a render-only roster from world state into the renderers at orchestrator/game.py:840-864 (`DefaultMeetingRunner.run_meeting`, the Task-10.3 `dead_ids` derivation) through `MeetingManager.run` at meetings/manager.py:1091-1098.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
