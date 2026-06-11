# Phase 10 — Conviction-engine repair (Wave 0) + crew evidence economy (Wave 1) + impostor gameplay (Wave 2)

Goal: make the crew's conviction engine HONEST, give the crew an evidence economy that can
actually recruit a plurality, then arm the impostor side — in that order, because deception is
unmeasurable against a conviction engine that is 93% artifact noise.

Anchor: audits/audit-2026-06-10-1820-gameplay-data.md (the post-Wave-1 close audit). Its
decomposition re-posed the Phase-9 fork: the missed-conversion mass is NOT mostly detector-shape
(weak-sub-gate = 6) nor mostly game-length (true-absence + one-meeting-short = 14) but
witness-over-gate-without-plurality = 27 — a witness renders >= 0.60 on the impostor, votes for
them (22/27), and cannot recruit a plurality because spoken testimony never enters listeners'
beliefs. Below that sits a detector whose flags are 93% artifacts (compound room labels 34,
placeholders 11, endpoint-tick fuzz 31), whose strong path fired on 5 wrong ejections and 0
correct ones, and whose old 0.629 "accuracy" was artifact railroads (14/22 artifact-only) at the
accusation base rate. The repairs come first so every later number means something.

Locked decisions (2026-06-10):
- Three waves, three combined re-records — attribution beats operator time (owner decision; the
  Phase-9 lesson was measuring on a broken instrument). Wave 0 repairs the instrument; Wave 1
  changes the crew evidence economy; Wave 2 arms impostors. One re-record per wave, never
  per-task.
- Tie ballots STAY SKIPPED (gp-8 parked, owner 2026-06-10): seed 26 m0's 4-4 eject-vs-skip tie
  resolving SKIPPED is the current rule working as written. Revisit only after Wave 1 grows
  eject blocs past tie territory. No tie-break or accused-self-vote change lands in Phase 10
  without a new owner decision.
- FROZEN throughout the phase: the §4.6 gate render + threshold (0 inversions across 506
  ballots — it works), the tally/abstain design (refuted Phase 9), the 2048 turn cap, the 9.8
  accumulator constants (+0.05 / -0.05 / 25% decay — byte-verified correct; Wave 1 may ADD
  channels, never re-tune these mid-measurement).
- Gates: the win split is EXCLUDED from every gate (constant ~90/10, zero ejection-driven wins).
  Progress is gated on genuine-class conversion and the accumulator/testimony channels — NEVER
  on raw ejection_accuracy parity with the artifact-era 0.63 (that number was railroads; parity
  with it is not a target, it is a regression).
- Provenance convention AFFIRMED (the audit's gp-1 demoted on design-thread review): MANIFEST
  git_sha records the source state the recording ran at (rev-parse HEAD at refresh time), per
  the fb3cfa5 precedent; byte-identical reconstruction is the falsifier. No re-stamp.

Parallelism: 10.1 is the sole root — the detector classifier is the wave's one-home dependency
(10.4 imports it; a parallel interim classifier was considered and rejected as the drift the
9.6 shared-parse rule exists to prevent). After 10.1 merges, 10.4 dispatches in parallel with
the 10.2 -> 10.3 chain (disjoint file scopes: eval/ vs meetings/agents). 10.5 is the
operator-run Wave-0 gate after all four. Track with
`python3 scripts/compute_next_task.py --phase 10`.

## Wave 0 — Honest instrument (detector + claim hygiene + gate metrics)

### Task 10.1 — Detector correctness repairs
**Branch:** `phase-10-detector-correctness`
**Depends on:** none (repair root)
**Section refs:** DESIGN.md §5.4, §6.3; audits/audit-2026-06-10-1820-gameplay-data.md gp-2 (C-C-1, C-C-2, C-C-3, D-D-3)
**Complexity:** Integration

The contradiction detector is the crew's sole structured-evidence engine and 93% of what it
emits is artifact: 34 compound-room-label mismatches (a sighting room like "CAFETERIA/EAST_HALL"
string-compared against an alibi room), 11 placeholder-room comparisons, 31 endpoint-tick-only
window mismatches, and a flag-stacking defect that let 19 near-duplicate flags lift one innocent
to suspicion 1.0 (seed 9 m1). The alibi_conflict path never received the 9.7 weak
classification at all (9.7 covered alibi_vs_sighting only), so self-pairs and adversarial
testimony still carry full +0.3 deltas. Net effect measured on this set: the strong path fired
on 5 wrong ejections and 0 correct ones, and every one of the 11 wrong ejections rode this
engine. Repair the artifact classes, weak-classify the conflict path, and cap stacked lifts —
while keeping the 4 genuine CANON_INTERIOR impostor flags alive (the only genuinely diagnostic
signal the set produced).

**Files in scope:**
- meetings/transcript.py (canonicalize rooms at claim-parse before any comparison: split compound labels, treat placeholder/unknown rooms as no-room (no flag), containment reads as CONSISTENT and feeds the corroboration path instead of a conflict — a third-party sighting whose room sits inside the subject's stated alibi is corroboration-class evidence, magnitude at most the Rule-3 delta and capped once per (subject, claim); PREFER weak-banding endpoint-tick-only window mismatches over excluding them — an endpoint mismatch can still be a real signal under corroboration; exclude only with a documented reason, and either way the handling must stay deterministic; give _detect_alibi_conflicts the 9.7 weak classification — a self-pair (both claims by the subject) is weak, adversarial accuser-stated testimony about the subject is capped weak, a defense-echo (the subject restating their own alibi after an accusation) dedupes to the original claim instead of minting a new flag)
- agents/memory/beliefs.py (cap the contradiction lift at ONE weak delta per (subject, alibi-claim) pair and add a per-subject per-meeting transient cap so near-duplicate flags cannot stack to 1.0; strong flags keep their existing single-flag weight)
- tests/meetings/test_transcript.py + tests/agents/test_beliefs.py + tests/meetings/test_manager.py (the acceptance shapes below, as offline reconstructions against the committed bytes — replays do not change until 10.5)

**Files NOT in scope:**
- agents/strategic/prompts/** (10.3 owns prompt changes; the §4.6 render is FROZEN)
- meetings/manager.py claim-target validation (10.2 owns the roster-validation extension)
- the 9.8 accumulator constants in agents/memory/beliefs.py (frozen — this task touches the contradiction-lift path only)
- replays/samples/**, eval/** (re-record is 10.5; gate metrics are 10.4)

**Definition of done:**
- [ ] Room canonicalization: compound labels, placeholders, and containment no longer mint alibi_vs_sighting or alibi_conflict flags; containment-consistent pairs feed corroboration. Pinned against the committed bytes: the 34 compound-label and 11 placeholder artifact flags from the audit's facts no longer reproduce under the new detector.
- [ ] Endpoint-tick-only mismatches no longer carry full weight — weak-banded by preference (excluded only with a documented reason; deterministic either way). The 31 endpoint-fuzz flags from the audit collapse accordingly.
- [ ] The corroboration fold demonstrably ACCEPTS a detector-derived containment-consistent pair, not only a claim-stated CorroborationClaim — integration-pinned. The audit proved Rule 3 never fired, so detector-sourced corroboration is likely the second never-exercised ingestion path; a containment-consistent pair that silently no-ops would make the canonicalization half-inert.
- [ ] alibi_conflict is weak-classified: self-pairs weak, adversarial accuser-stated testimony capped weak, defense-echoes deduped to the original claim. Seeds 11 m2 and 17 m0 self-pairs land in the weak band; seed 9 m1 renders p-8 at 0.58 (19 flags collapse to 1 effective lift), not 1.0.
- [ ] Per-(subject, claim) lift dedup + per-subject per-meeting cap: no innocent reaches 1.0 from flag volume. Seed 26 m1: innocent p-6 no longer outscores impostor p-3.
- [ ] The genuine channel SURVIVES: the 4 CANON_INTERIOR impostor flags (seeds 3, 30, 42, 45) still fire as strong under the repaired detector — pinned individually. Killing artifacts must not kill detection.
- [ ] Determinism: the detector + lift math remain pure functions; re-running on the same transcript yields byte-identical flags.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Canonicalize ONCE at claim-parse so the detector, the corroboration path, and the renderer all
see the same canonical rooms — do not scatter normalization across comparison sites. The weak
classification helpers from 9.7 already exist in meetings/transcript.py; the conflict path
should call the same logic, not a parallel implementation. Acceptance pins run offline against
the committed replays via the replay-loader walk (the audit extractor shows the pattern), so
every number above is checkable for $0 before any re-record.

**Integration risk:**

This is the highest-leverage seam in the crew pipeline — every belief, render, and ballot
downstream reads it. The hard line is the CANON_INTERIOR survival pin: an over-aggressive
repair that silences the genuine channel converts "93% artifacts" into "100% silence" and
Wave 1 measures nothing. Recording-side only; committed reconstruction unaffected until 10.5.

**Ready-to-paste prompt:** `agent_prompts/task-10-1-detector-correctness-repairs.md`

### Task 10.2 — Claim roster validation
**Branch:** `phase-10-claim-roster-validation`
**Depends on:** 10.1 (shares the belief-fold seam)
**Section refs:** DESIGN.md §5.2, §6.3; audits/audit-2026-06-10-1820-gameplay-data.md gp-6 (C-C-8, H-H-6)
**Complexity:** Medium

The fb3cfa5 guard validates accusation targets and ballot targets against the living roster, but
alibi.subject and corroboration.supports are unvalidated: the 9B emitted subjects like
"headless-seed-9" (a game id as a player), and 15 corroboration claims with invalid supports
were silent no-ops — which is why belief Rule 3 (corroboration lowers suspicion) has NEVER fired
in any recorded set. Garbage subject rows also leak into the §6.6 suspicion-graph render (seed
12 m2 renders "headless-seed-12:meeting-0:turn-0" as a player row at suspicion 0.46). Extend the
DROP + marker pattern to every subject-bearing claim field and filter the belief fold + graph
render to roster ids.

**Files in scope:**
- meetings/manager.py (extend the fb3cfa5 _drop_invalid_accusation_targets pattern to alibi.subject and corroboration.supports — invalid values DROP the claim and record the original on free_text via the existing marker convention)
- agents/memory/store.py + agents/memory/beliefs.py (filter the post-meeting evidence fold and the rendered suspicion graph to roster player ids — no garbage rows in beliefs or prompts)
- tests/meetings/test_manager.py + tests/agents/test_memory_store.py + tests/agents/test_beliefs.py (the acceptance shapes below)

**Files NOT in scope:**
- meetings/schemas.py (no schema shape change — DROP + marker, like fb3cfa5)
- agents/strategic/prompts/** (10.3 owns prompts)
- replays/samples/**, eval/** (re-record is 10.5)

**Definition of done:**
- [ ] An alibi whose subject is not a roster player, and a corroboration whose supports is not a roster player, are dropped at the meeting layer with the original preserved on free_text via the marker convention. The seed-9 m1 turns 2-3 shape ("headless-seed-9" as subject/supports) reproduces the drop in a test.
- [ ] The corroboration channel demonstrably FIRES end-to-end: a valid corroboration claim lowers the supported player's suspicion by the Rule-3 delta through the post-meeting fold — pinned in a game-loop integration test (the first live Rule-3 path; today it is structurally dead).
- [ ] The suspicion-graph render and the belief fold carry roster ids only: the seed-12 m2 garbage-row shape cannot render into any vote prompt.
- [ ] A corroboration naming a DEAD roster player is dropped (the seed-40 "p-2 dead" shape) — same rule as accusations.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Mirror fb3cfa5 exactly — one validation chokepoint in the manager, DROP + marker, no schema
change. Ordering is load-bearing relative to 10.1: the chokepoint validation runs BEFORE
detection and before the post-meeting fold, so a dropped garbage subject never mints a
contradiction flag, never consumes any 10.1 cap accounting, and never materializes a belief
row — assert that ordering in a test rather than assuming it. The graph-render and fold
filters are the defense-in-depth backstop: even if a garbage subject slips a future claim
type, the prompt surface and belief store stay clean. Rule 3's first firing is the contract's
real deliverable; the integration test proving suspicion moves -0.05 through a real meeting is
the hard line.

**Integration risk:**

Touches the same fold seam as 10.1 (hence sequential). Dropping claims changes recorded
transcripts only at the next re-record; committed reconstruction unaffected until 10.5.

**Ready-to-paste prompt:** `agent_prompts/task-10-2-claim-roster-validation.md`

### Task 10.3 — Prompt nudges
**Branch:** `phase-10-prompt-nudges`
**Depends on:** 10.2 (shares meetings/manager.py)
**Section refs:** DESIGN.md §5.1, §5.2; audits/audit-2026-06-10-1820-gameplay-data.md gp-9 (H-H-1, H-H-2, H-H-3, D-D-8)
**Complexity:** Medium

Three residual 9B artifacts, prompt-and-validation layer (the 2048 cap stays frozen; the roster
render is byte-verified correct, so these are model-side mitigations): (1) five openings
narrated without making any accusation claim, killing the chain on turn 0 (seeds 23, 39, 44, 13
m0, 38 m1 — distinct from the 2 cap-defaults); (2) the remaining defaults are structured-array
repetition loops (a sighting repeated ~5x until the cap), no longer prose relocation; (3) id
hallucination shifted shape — 17/18 invalid targets are now DEAD real players (12 impostor-
spoken), not invented ids, and the living-roster block does not say who is dead.

**Files in scope:**
- meetings/manager.py (opening validation: an opening turn whose claims carry neither an accusation nor an explicit unsure marker triggers the existing parse-retry path once before fail-soft — reuse the retry machinery, no new channel)
- agents/strategic/prompts/crewmate_report.j2 + agents/strategic/prompts/impostor_report.j2 (openings: require an accusation claim OR an explicit "unsure" statement in free_text; add the anti-repetition line "list each sighting once"; render the DEAD players as an explicit do-not-accuse line under the living roster)
- agents/strategic/prompts/accusation_round.j2 (anti-repetition line + the DEAD line; reply/opt-in unchanged otherwise)
- orchestrator/game.py (DEFAULT_PROMPT_VERSIONS bumps: crewmate_report v4 -> v5, impostor_report v3 -> v4, accusation_round v6 -> v7)
- tests/agents/test_strategic_prompts.py + tests/meetings/test_manager.py + tests/orchestrator/test_replay_meetings.py (version pins on fresh replays; the opening-retry shape; DEAD-line renders; committed-fixture pins left for 10.5)

**Files NOT in scope:**
- meetings/manager.py turn/vote token caps (FROZEN at 2048/1024)
- agents/strategic/prompts/vote_ballot.j2 (the §4.6 render is FROZEN)
- meetings/schemas.py (no MeetingTurn shape change — the unsure marker is free_text-level, validated manager-side)
- replays/samples/** (re-record is 10.5)

**Definition of done:**
- [ ] A narration-only opening (no accusation claim, no unsure marker) triggers exactly one retry through the existing parse-retry path, then fail-softs as today — pinned with a stub that returns narration-only once then a valid opening.
- [ ] Both opening templates instruct accuse-or-declare-unsure; all three turn templates carry the list-each-sighting-once line; the roster block renders DEAD players explicitly as non-targets. Render tests pin each.
- [ ] Version markers bump end-to-end (crewmate_report.v5, impostor_report_v4, accusation_round.v7) in a fresh replay entry; committed-byte fixture pins untouched until 10.5.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The opening-retry reuses the machinery 7.10/8.9 built — wire the validation into the existing
single-retry path rather than inventing a second loop. The DEAD line is the negative list the
model is missing: 17/18 hallucinations were dead-real ids, so naming the dead explicitly attacks
the observed failure, not a guessed one. Keep all three nudges terse — the free_text discipline
medians (~230 chars) prove the model follows short imperatives.

**Integration risk:**

Prompt-version bump + a retry-path change in the manager. The retry must not loop (one retry,
then the standing fail-soft) or recording wall-time degrades. Fresh-vs-committed test pin split
exactly as 9.9/PR #131 did.

**Ready-to-paste prompt:** `agent_prompts/task-10-3-prompt-nudges.md`

### Task 10.4 — Gate metrics
**Branch:** `phase-10-gate-metrics`
**Depends on:** 10.1 (the genuine-class definition IMPORTS the repaired detector's classifier — one home, two importers, per the 9.6 shared-parse rule; dispatches in parallel with the roster-validation chain, whose files are disjoint)
**Section refs:** DESIGN.md §11.3; audits/audit-2026-06-10-1820-gameplay-data.md gp-7 (B-B-1, C-C-6, D-D-2, H-H-5, H-H-7)
**Complexity:** Medium

The Phase-10 A/B ruler, offline (reads committed replays; no re-record). The audit specified the
gate surface: win split excluded (constant ~90/10, zero ejection-driven wins); deception metrics
conversion-controlled; progress gated on genuine-class conversion, never on raw
ejection_accuracy parity with the artifact-era 0.63. Ship the missing counters so 10.5 and every
later wave reads them off the report instead of deriving them operator-inline.

**Files in scope:**
- eval/vote_correctness.py + eval/meeting_quality.py + scripts/build_sample_report.py (ship: genuine-class conversion — ejections where a CANON-class strong contradiction named the ejected impostor, with its supplied/converted denominator pair; lost-opening-accusation count — openings carrying zero accusation claims, counted separately from cap-defaults; impostor-survival conditioned on rendered-max < 0.60 — the deception-vs-under-conversion split; the existing leads stay)
- eval/report_schema.py (wrapper-level additions only; CURRENT_FORMAT_VERSION stays 2 per the §11.4 policy unless the inner shape changes)
- replays/samples/tournament-eval-report.json + replays/samples/9p2i/tournament-eval-report.json (regenerated offline; bytes + MANIFESTs untouched)
- tests/eval/* + tests/fixtures/prompt_regression/baseline.json (pins on the current committed set: genuine-class 0 converted / 4 supplied; lost-opening 5; defaults 2; conditioned survival n=1 of 45; baseline regenerated)

**Files NOT in scope:**
- engine/, meetings/, agents/ source (offline metric layer only)
- replays/samples/**/replay-seed-*.jsonl + MANIFESTs (no re-record)

**Definition of done:**
- [ ] genuine_class_conversion ships with both numerator and denominator (this set: 0/4) and is documented as the phase's PRIMARY progress gate; the report carries an explicit note that raw ejection_accuracy comparisons against pre-repair eras are invalid (the 0.63 was artifact-built).
- [ ] lost_opening_accusations (5 on this set, seeds 23/39/44/13m0/38m1) ships separately from cap-defaults (2); impostor survival conditioned on rendered < 0.60 ships (n=1/45 here) so Wave-2 deception claims are conversion-controlled from day one.
- [ ] The 9p/2i report regenerates to the audited values as regression pins; these pin the e750b40 set and 10.5 updates them — stated in the test docstrings.
- [ ] prompt-regression baseline regenerated; CI exact-match holds.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The audit extractor (audits/workflows/extract_gameplay_facts.py) already derives every one of
these — port its derivations to the eval layer rather than re-inventing them, reusing
eval/_suspicion_parse.py for anything reading rendered suspicion. CANON-class detection IMPORTS
the 10.1 classification helpers from meetings/transcript.py — never a parallel implementation,
even a temporary one; a drifted copy here poisons every later gate, which is precisely why this
task waits for 10.1.

**Integration risk:**

Offline only; the hard line is committed bytes + MANIFESTs untouched. The genuine-class
definition is an import of 10.1's classifier, never a copy — the one-home rule is the whole
reason this task sequences behind the detector repair instead of dispatching as a root.

**Ready-to-paste prompt:** `agent_prompts/task-10-4-gate-metrics.md`

### Task 10.5 — Wave-0 combined re-record and gate
**Branch:** `phase-10-wave0-rerecord`
**Depends on:** 9.11, 10.1, 10.2, 10.3, 10.4
**Section refs:** DESIGN.md §11.4, §3.5; audits/audit-2026-06-10-1820-gameplay-data.md (the Wave-0 set)
**Complexity:** Integration

The Wave-0 gate, the 9.5/9.11 operator shape: with the repairs merged, smoke first, then
re-record BOTH committed sets on qwen3.5:9b (think:false) in ONE PR, regenerate both reports +
MANIFESTs + the prompt-regression fixtures and baseline, and run the validity gate plus the
repair-specific assertions. This re-record establishes the HONEST conversion baseline — the
first one whose numbers are not artifact-dominated. The wave pauses at this merge: the design
thread re-runs the close audit and authors the Wave-1 (testimony + pacing) contracts from it.

**Files in scope:**
- replays/samples/*.jsonl + tournament-eval-report.json + MANIFEST.md (flat 4p/1i re-recorded; git_sha updates per the affirmed convention)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded; roster {9,2,2} unchanged)
- tests/fixtures/prompt_regression/{v_a,v_b}/*.jsonl + baseline.json (regenerated — detector + prompts changed)
- the committed-bytes test pins (prompt-version rows crewmate_report.v5 / impostor_report_v4 / accusation_round.v7, git_sha, model, cost 0; re-scope zero-denominator skips per the 8.18/9.5/9.11 precedent)

**Files NOT in scope:**
- engine/, meetings/, agents/, llm/, eval/ source (all behavior landed in 10.1-10.4; this task records + regenerates only). The §4.6 render, tally, accumulator constants, and token caps stay FROZEN.
- audits/workflows/** (the close-audit re-run is the design thread's step after merge)

**Definition of done:**
- [ ] Smoke first (3-5 seeds @ 9p/2i): think:false guard holds; every smoke seed reaches game_over with zero ballot/turn truncation; opening-retry telemetry sane (no retry loops, retries counted); the per-seed wall-time projection ACCOUNTS for the 10.3 opening-retry adding roughly one extra meeting call per narration-only opening (~5 per 50 games at baseline) so the full-run estimate does not under-shoot; STOP for operator go (or the documented autonomous-go protocol from 9.11 if unattended).
- [ ] Both sets re-recorded in ONE PR on qwen3.5:9b; reports + MANIFESTs + fixtures regenerated; version rows carry v5/v4/v7.
- [ ] Validity gate (HARD, the standing v3 set): friendly-fire 0; every game reaches game_over; betrayal 0; leak suite green; meeting_rate >= 0.60 with >= 30 resolved meetings; byte-identical reconstruction; zero tick-1 kills; zero dangling primary_reason_id; zero thinking trips; model rows correct.
- [ ] Repair assertions (the Wave-0 additions, reported with numbers): total contradiction volume collapses vs the 83/93%-artifact era (derive the artifact share with the audit extractor offline — compound-label, placeholder, and endpoint classes ~0); no innocent reaches suspicion 1.0 by flag stacking; Rule-3 fired count > 0 (the corroboration channel is alive); CANON_INTERIOR impostor flags present and their conversion reported (the genuine-class numbers 10.4 shipped); invalid-subject drop markers present where the model hallucinated; lost-opening-accusation count vs the 5-baseline.
- [ ] Conversion re-baseline reported with the explicit framing: these are the first honest numbers; comparisons to 0.629 (artifact era) and 0.476 (mixed era) are provenance-noted, not gates.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Operator-run local session, identical mechanics to 9.11: AILIBI_LLM_PROVIDER=ollama, model from
the client constant, one atomic commit of bytes + reports + fixtures + pins. Expect contradiction
counts to DROP hard — that is the repair working, not a regression; the report framing in the PR
body should lead with the artifact-share collapse and the genuine-class numbers, not the raw
ejection count.

**Integration risk:**

The wave converges here and PAUSES at this merge for the close-audit re-run — do not author or
implement Wave-1 work (testimony ingestion, emergency meeting) in this task. If the floor fails,
STOP and fix upstream; nothing frozen gets touched to chase a number.

**Ready-to-paste prompt:** `agent_prompts/task-10-5-wave-0-combined-re-record-and-gate.md`

## Merge Criteria (Phase 10 Wave 0 — honest instrument)
- Detector honest (10.1): artifact classes repaired at the source; flag stacking capped; conflict path weak-classified; the genuine CANON_INTERIOR channel demonstrably preserved (the 4 flags survive).
- Claims validated (10.2): every subject-bearing claim field roster-validated with DROP + marker; Rule 3 fires for the first time; prompt surfaces carry roster ids only.
- Residual artifacts nudged (10.3): accuse-or-unsure openings with single retry; anti-repetition; explicit DEAD line; versions v5/v4/v7.
- Ruler shipped (10.4): genuine-class conversion is the published primary gate; lost-opening + conditioned-survival counters live; artifact-era comparisons documented invalid.
- Honest baseline recorded (10.5): one combined re-record, HARD validity gate + repair assertions green, re-baseline framed correctly.
- THE PAUSE: Wave 0 ends at 10.5's merge. The design thread re-runs the close audit on the honest baseline; Wave-1 contracts (testimony ingestion + emergency meeting/pacing) are authored from its findings, and Wave-2 contracts only after the Wave-1 gate plus the deception probe.

## Wave 1 — Crew evidence economy (SKETCH — contracts authored after the Wave-0 close audit)

Planned scope, anchored to the audit's b1/b2/c buckets; numbers re-derived on the honest
baseline before contracts are written. Wave-1 authoring is blocked on TWO inputs, not one:
the Wave-0 close-audit data AND the owner's fold-timing decision on 10.6 (pre-vote vs
post-vote — THE Phase-10 design decision); neither alone unblocks the contracts.

- 10.6 Testimony-ingestion belief rule (gp-3, the 27-meeting lever): a first-hand
  saw_player/body-proximity observation SPOKEN in a meeting adds a small quantized delta
  (below the 0.2 body-proximity weight) to listeners' suspicion of the subject, decaying like
  other meeting evidence. Owner design questions to settle at contract time: pre-vote vs
  post-vote fold (pre-vote is what converts the b1 bucket — the witness recruits a plurality
  in-meeting — but it must stay observation-gated to honor the no-verbal-cascade principle:
  first-hand observation claims only, never accusations, capped per meeting); credibility
  gating; interaction with the 9.8 fold (additive channel, constants frozen).
- 10.7 Crew-callable emergency meeting + pacing accounting (gp-4): an emergency action with
  eligibility/cooldown so meeting supply decouples from impostor kill cadence (all 76 meetings
  are body-report-triggered today; 7/50 games have zero meetings; only 21/50 reach the
  accumulator's 2-meeting floor). Targets from the audit: >= 2-meeting share above 42%,
  meetings/game above 1.52. Balance accounting (margin-1 kill counts, the §3.5 kill/denominator
  coupling) is reported, not tuned — account-don't-rule-change.
- 10.8 Wave-1 combined re-record + gate, then the close-audit re-run that authors Wave 2.

## Wave 2 — Impostor gameplay (SKETCH — contracts authored after the Wave-1 gate + deception probe)

- 10.9 Deception probe (the pre-contract gate, model-probe harness): before any toolkit
  contract is written, extend experiments/model_probe to measure whether qwen3.5:9b can
  (a) emit a plausible fake-task pattern, (b) deflect an accusation without boomeranging onto
  itself, (c) self-report a kill with a pre-built alibi that survives the repaired detector.
  Cheap, offline, $0 — the same pre-validation pattern that de-risked the conversion prompts.
  If the 9B cannot play the villain, the toolkit contract changes shape (or the model question
  reopens) BEFORE a wave is spent on it.
- 10.10 Impostor toolkit (gp-5): fake do_task (consumes the tick, renders as do_task, no
  progress) + an idle budget tuned toward the crew wait-rate (~10%); a report action with an
  occasional self-report-own-kill policy; kill-intent gating on same-room co-presence at intent
  time (eliminates the 21 same-tick MECH-B-1 refusals). The 7.12/9.3 firewalls and betrayal==0
  stay inviolate.
- 10.11 Indistinguishability metrics (gp-5 gate): impostor wait-rate vs crew, task-emission
  overlap, top-2-idler overlap (92/100 today — the fingerprint to erase), impostor-reporter
  share, kill-success rate; deception metrics conversion-controlled per 10.4.
- 10.12 Wave-2 combined re-record + the phase-close audit.

Parked / explicit non-goals for the phase: tie-break + accused-self-vote semantics (gp-8,
owner-parked — ties stay SKIPPED); §4.6 gate or threshold changes; tally/abstain redesign
(refuted); turn/vote token caps; accumulator constant re-tuning; the MANIFEST provenance
convention (affirmed).
