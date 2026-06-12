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
- [ ] Smoke first (3-5 seeds @ 9p/2i): think:false guard holds; every smoke seed reaches game_over with zero ballot/turn truncation; opening-retry telemetry sane (no retry loops, retries counted); the per-seed wall-time projection ACCOUNTS for the 10.3 opening-retry adding roughly one extra meeting call per validation-failing opening — narration-only OR guard-emptied (the 10.3 validation runs on post-guard claims), ~5-10 per 50 games at baseline — so the full-run estimate does not under-shoot; STOP for operator go (or the documented autonomous-go protocol from 9.11 if unattended).
- [ ] Both sets re-recorded in ONE PR on qwen3.5:9b; reports + MANIFESTs + fixtures regenerated; version rows carry v5/v4/v7.
- [ ] Validity gate (HARD, the standing v3 set): friendly-fire 0; every game reaches game_over; betrayal 0; leak suite green; meeting_rate >= 0.60 with >= 30 resolved meetings; byte-identical reconstruction; zero tick-1 kills; zero dangling primary_reason_id; zero thinking trips; model rows correct.
- [ ] Repair assertions (the Wave-0 additions, reported with numbers): total contradiction volume collapses vs the 83/93%-artifact era (derive the artifact share with the audit extractor offline — compound-label and placeholder classes ~0; the endpoint class survives ONLY as weak-banded flags per the 10.1 weak-band decision, never full-weight); no innocent reaches suspicion 1.0 by flag stacking (the 10.1 per-subject cap is 0.3 — one strong flag's worth); Rule-3 fired count > 0 (the corroboration channel is alive — both the claim-stated and the detector-derived containment paths); CANON_INTERIOR impostor flags present and their conversion reported via 10.4's genuine_class_conversion (NOTE: these flags are weak self-stated by construction — a fabricated alibi is self-stated — so assert presence under 10.4's re-derived definition, not marker-strength); invalid-subject drop markers present where the model hallucinated; lost-opening-accusation count vs the 5-baseline.
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

## Wave 1 — Crew evidence economy (testimony conversion + meeting supply)

Anchor: audits/audit-2026-06-11-2218-gameplay-data.md (the post-Wave-0 close audit;
SIGNIFICANT_ISSUES, baseline VALID). What it established: the testimony class stays dominant
(b1 = 53 impostor-meeting pairs over 50 meetings, up from 27), but the binding constraint
MOVED — crew vote discipline is now 100% (zero crew over-gate skips; all 28 missed-skips are
impostor voters), so the loss point is the strict SKIP-plurality bloc (1-3 over-gate voters
losing to 4-7 mandatory sub-gate skips). Wave 1's job is to grow the over-gate POPULATION,
not to fix follow-through. Three instrument cracks must close first because they sit inside
the measurement: the VARYING_ROOMS placeholder leak (22/87 flags = 25% of set volume, all on
one innocent), the proxy-alibi strong-band gap (3/3 strong flags third-party, 1 TP / 2 FP),
and Rule-3 credulity (52% of impostor accusation flow cancels in-meeting on spawn-window and
kill-scene vouches).

Owner decisions (2026-06-12) locked into these contracts:
- Proxy alibis: SUBJECT-ACCOUNT-CONSISTENCY (option b) — when the subject's own account agrees
  with the conflicting sighting, the proxy flag is suppressed and re-targeted (weak) at the
  proxy speaker. Keeps the seed-24 true positive, kills the seed-28 false positive.
- Fold timing: PRE-VOTE with a TWO-WITNESS independence requirement; accuse-capable opt-in
  corroborations count as the second voice; corroborations move at the same phase as
  accusations. The audit's simulation (report §4.2) is the spec: single-witness pre-vote
  (+14 impostor meetings / 9 innocent meetings) is REJECTED as an owner-principle violation.
- The testimony channel reuses the +0.05 accusation unit (no new magnitude; the simulation
  showed two-witness yield identical at +0.05 vs +0.08). A pre-vote fold REPLACES the
  post-vote accused-bump for that subject-meeting — the per-meeting total never doubles.
- Committed replays do NOT change under 10.6-10.8 (recording-side semantics only;
  reconstruction replays recorded results). The Wave-1 A/B baseline is the 10.6-re-derived
  corrected W0 table, NOT PR #143's numbers (flag volume is ~25% inflated until the
  placeholder fix lands).

Sequencing (cadence doctrine walk): 10.6 is the measurement root and lands first; 10.8 is
file-disjoint and may dispatch in parallel with it; 10.7 follows 10.6 (shared
transcript/beliefs/manager seams + it consumes 10.6's relevance predicate); ONE combined
re-record (10.9) after all three — never per-task. Freeze-during-measurement holds: §4.6
render/threshold, tally, token caps, and the 9.8 constants stay untouched; the testimony
channel adds a rule, not a re-tune, and its shape freezes once 10.9 records. Track with
`python3 scripts/compute_next_task.py --phase 10`.

### Task 10.6 — Wave-1 instrument integrity and gate spec
**Branch:** `phase-10-instrument-integrity`
**Depends on:** none (wave root)
**Section refs:** DESIGN.md §5.4, §6.3; audits/audit-2026-06-11-2218-gameplay-data.md gp-1 (C-C-5, C-C-4), C-C-3, gp-5 (H-H-1, H-H-2), gp-6 (H-H-4), gp-7 (C-C-6)
**Complexity:** Integration

The Wave-0 close audit found the honest instrument has two remaining detector cracks, one
rule-credulity hole, and a fail-soft gap — all offline-repairable against committed bytes, no
re-record. This task closes them and ships the Wave-1 A/B gate metrics, then re-derives the
corrected W0 baseline that 10.9 measures against. True-positive load was measured before
removal per doctrine: all 22 placeholder-leak flags were false positives on one innocent
(zero TP loss), and the proxy-alibi repair is the TP-preserving option (b) by owner decision.

**Files in scope:**
- meetings/transcript.py (placeholder fix as a frozen canonical-room ALLOWLIST — a data constant of the map's canonical rooms; any claim room whose canonical form is not in the set is non-spatial and mints NO flag and NO corroboration, replacing the placeholder-label denylist, with a test asserting the allowlist equals the engine map's room set so a future map change re-triggers review; proxy-alibi subject-account-consistency — when alibi.speaker differs from subject AND the subject's own claims this meeting are consistent with the conflicting sighting, suppress the flag against the subject and mint a re-targeted WEAK flag against the proxy speaker, new weak-reason constant, no ContradictionRef schema change; the subject-account lookup MUST run on canonical claims BEFORE echo-dedup discards the subject's copy, else the subject's own account is invisible exactly when the proxy spoke first; Rule-3 relevance predicate — a supporting sighting corroborates ONLY if outside the spawn window, tick 2 or later, AND not a kill-scene sighting placing the subject in the meeting's triggering-body room within the corroborated alibi window; the predicate is a named pure function because 10.7 reuses it for accusation-side observation backing)
- agents/memory/beliefs.py (apply the relevance gate at the Rule-3 ingestion seam so claim-stated and detector-derived corroborations both pass through it; no constant changes)
- meetings/manager.py (retry feedback — the single opening retry prompt states the failure reason, naming the dropped dead target and demanding a LIVING target or unsure; unsure-degrade — a twice-failed opening records as an unsure opening with no accusation instead of a full default, so opt-ins and votes still run; telemetry distinguishes cap-default vs validation-degrade; bound the quoted-original in INVALID_ALIBI_SUBJECT_MARKER and sibling markers to 60 chars plus ellipsis)
- eval/vote_correctness.py + eval/meeting_quality.py + scripts/build_sample_report.py (gp-7: multi_signal_conversion — an impostor ejection counts when its rendered pre-vote lift decomposes into 2+ distinct design channels over the quantized rule lattice: contradiction-flag, body-proximity, vent-witness, prior-meeting carry; supply gauges: zero-contradiction meeting share, genuine-subject share, over-gate listeners per accused-impostor meeting, flag-subject role split; the published report labels win split non-gate)
- tests/meetings/test_transcript.py + tests/agents/test_beliefs.py + tests/meetings/test_manager.py + tests/eval/* (the pins below; offline against committed bytes)

**Files NOT in scope:**
- agents/strategic/prompts/** (§4.6 render frozen; 10.8 owns the emergency opening branch)
- the 9.8 accumulator constants (frozen)
- replays/samples/** (no re-record; committed tournament-eval-report.json is NOT regenerated — the corrected baseline lives in the PR body + a tests/fixtures JSON, keeping the committed sample dir single-era)
- meetings/manager.py fold/vote phases beyond the items named (10.7 owns the fold restructure)

**Definition of done:**
- [ ] Allowlist pins: seed 13 m1 mints 0 flags from VARYING_ROOMS (currently 22); seed 6 m1 HALLS mints 0; the canonical-set-equals-map test exists; no genuine CANON flag is lost (re-derive and compare the genuine supply before/after — expected unchanged).
- [ ] Proxy pins: seed 28 m1 has NO strong flag on p-9 and a weak re-target on p-7, with p-9's re-derived max below 0.60; seed 24 m0's strong flag on p-4 SURVIVES (the subject echoed the false alibi — no suppression). Both walked offline against committed bytes.
- [ ] Relevance-gate pins: seed 6 m1 — the accuser's ADMIN tick-16 sighting produces NO corroboration for p-6, and p-6's re-derived cross-meeting trajectory rises instead of rendering flat; spawn-window-sourced corroborations count 0 set-wide; total re-derived Rule-3 events remain above 0 (the channel is gated, not killed).
- [ ] Fail-soft pins: a guard-emptied opening's retry prompt contains the failure reason; a twice-failed opening records as unsure (no accusation) and the meeting still reaches opt-ins and ballots; a 3499-char invalid subject yields a bounded marker (unit test); telemetry splits cap-default vs validation-degrade.
- [ ] gp-7 pins: the 5 W0 impostor ejections decompose exactly as the audit found — seeds 8, 11, 26, 39 multi-signal and seed 24 flag-only; the gauges publish in the report builder.
- [ ] CORRECTED W0 BASELINE: re-run the 10.4 re-deriver + the new metrics over the committed W0 bytes; record the corrected table (total flags, weak/strong split, genuine supply + conversion, multi-signal conversion, gauge values) in the PR body and pin it at `tests/fixtures/phase10/corrected_w0_baseline.json` — the exact file 10.9 reads as its A/B baseline (one home: the fixture is the artifact, the PR-body copy is narrative).
- [ ] Determinism: detector, predicate, and metrics are pure; re-runs are byte-identical.
- [ ] `uv run mypy .`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run lint-imports`, `uv run python scripts/generate_prompts.py --check`, `uv run python scripts/validate_task_docs.py`, `uv run pytest`, and `bash scripts/check.sh` all pass.

**Public types introduced:**
- CANONICAL_ROOMS
- WEAK_REASON_RETARGETED_PROXY
- MultiSignalConversionReport

**Implementation hint:**

One-home discipline throughout: the allowlist, the relevance predicate, and the proxy
consistency check live in meetings/transcript.py beside the existing classifier; beliefs.py
and eval consume them by import, never re-derive. The audit extractor
(audits/workflows/extract_gameplay_facts.py) shows the offline replay-walk pattern for every
pin. The echo-dedup ordering item is the subtle one: the seed-24 conviction currently exists
only because the impostor's proxy copy happened to be kept — under option (b) the subject's
own account must be consulted from the pre-dedup claim set so the outcome stops depending on
turn order.

**Integration risk:**

Over-suppression is the failure mode that matters: the W0 lesson is that 100% silence is as
bad as 93% artifacts. The seed-24 survival pin and the Rule-3-events-above-zero pin are the
tripwires. The re-target changes who gets lifted — it can only point at a speaker whose claim
conflicts with both the sighting and the subject's own account, and it lands weak, so it
cannot eject alone. Recording-side only; committed reconstruction unaffected.

**Ready-to-paste prompt:** `agent_prompts/task-10-6-wave-1-instrument-integrity-and-gate-spec.md`

### Task 10.7 — Testimony ingestion (pre-vote, two-witness)
**Branch:** `phase-10-testimony-ingestion`
**Depends on:** 10.6
**Section refs:** DESIGN.md §5.2, §6.3, §4.6; audits/audit-2026-06-11-2218-gameplay-data.md gp-2 (C-C-1, C-C-2, C-C-3, D-D-3, C-C-6); the corroborate-within-round owner principle
**Complexity:** Integration

The b1 lever. Spoken testimony currently never enters listeners' beliefs: 38/53 testimony
pairs already had an over-gate eyewitness and 30/53 had witness ballot follow-through, yet
47/50 such meetings SKIPPED because listeners parked at 0.58 and the SKIP bloc won. This task
folds qualifying testimony into every living listener's PERSISTENT belief BEFORE ballots, so
an eyewitness can recruit a plurality within the round — under the independence gate that
keeps bare verbal pile-ons powerless.

**Files in scope:**
- meetings/transcript.py (a pure helper deriving the INDEPENDENT VOICES for each accused subject from the transcript: a voice is a chain/opening turn accusing the subject that carries at least one first-hand observation claim about the subject which passes the 10.6 relevance predicate, or an opt-in corroboration supporting an accuser of the subject that itself carries such an observation; voices must be distinct speakers, never the subject; bare verbal accusations carry no voice)
- agents/memory/beliefs.py (the two-witness rule: subjects with 2+ independent voices take the +0.05 accused-bump PRE-VOTE, applied to every living listener, deduped once per meeting per subject, written to the persistent store; subjects below the bar keep today's post-vote path; the pre-vote fold REPLACES the post-vote accused-bump for that subject-meeting — a folded subject is marked so the post-vote half skips it; the impostor teammate guard applies to this channel)
- meetings/manager.py (restructure the meeting fold into two deterministic halves that ALWAYS run: pre-vote half = two-witness testimony bumps + this meeting's relevance-gated corroborations, both directions symmetric; post-vote half = single-voice accused-bumps + Rule-5 decay, exactly as today; vote prompts render AFTER the pre-vote half so the §4.6 verdict reads post-fold values — the gate computation itself is untouched)
- tests/meetings/test_transcript.py + tests/agents/test_beliefs.py + tests/meetings/test_manager.py

**Files NOT in scope:**
- agents/strategic/prompts/** (the §4.6 render and all templates frozen; no prompt knows about the fold — listeners see updated numbers, nothing else)
- eval/** (10.6 shipped the gauges; this task changes no metric)
- the 9.8 constants (the +0.05 unit is reused, not re-tuned; decay untouched)
- engine/**, orchestrator/** (meeting-layer only)
- tests/fixtures/prompt_regression/** (10.8 owns the v6 baseline regeneration; this task changes no template, and the regression fixture renders from fixed inputs unaffected by fold timing)
- replays/samples/**

**Definition of done:**
- [ ] Single-voice regression: a meeting with one accuser (or any number of bare verbal accusers) produces a persistent post-meeting state byte-identical to pre-change behavior — the channel is invisible until independence is met.
- [ ] Two-voice fold: two observation-backed accusers (or one plus a qualifying opt-in corroboration) move every living listener's view of the subject by exactly +0.05 pre-vote, once, persisted; the post-vote half demonstrably skips the accused-bump for that subject (the double-fold test is mandatory — the per-meeting total for a folded subject equals the unfolded total).
- [ ] Pile-on pin (the owner-principle tripwire): replaying the rule offline over seed 30 m1 produces NO pre-vote fold for p-7 (3 accusers, none with qualifying observation backing). If the implementation finds a qualifying second voice there, STOP and escalate — do not ship a rule that converts that meeting.
- [ ] Yield pins: the offline replay reproduces the audit's two-witness simulation rows — seeds 2 m1 and 5 m1 each lift at least one additional listener to 0.60 or above pre-vote.
- [ ] Same-phase symmetry: a relevance-gated corroboration in the same meeting folds pre-vote alongside the bumps (a defended subject is cleared before ballots, not a meeting late — the seed-28 shape).
- [ ] Render-after-fold consistency: when a listener's view of a folded subject crosses 0.60 pre-vote, the rendered vote prompt shows the post-fold value AND the in-prompt §4.6 verdict reads MUST vote for that listener — graph and verdict computed from ONE post-fold state source; a stale pre-fold graph anywhere in the render path is the bug this pin catches. Unit-pinned: render a vote prompt after a two-voice fold and assert both the value and the verdict line. (A model skip against a freshly-folded MUST-vote render would be a NEW inversion class; 10.9's 0-inversion line plus its fold-crossed spot-walk cover the recorded side.)
- [ ] Teammate guard holds on the new channel; rendered values stay on the quantized lattice; determinism (same transcript, byte-identical fold).
- [ ] `uv run mypy .`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run lint-imports`, `uv run python scripts/generate_prompts.py --check`, `uv run python scripts/validate_task_docs.py`, `uv run pytest`, and `bash scripts/check.sh` all pass.

**Implementation hint:**

Split the existing fold by moving invocation points, not duplicating logic — one fold
function with a phase argument, called twice per meeting. The voices helper is pure and lives
beside the classifier; it reuses the 10.6 relevance predicate verbatim (one home). The
audit's §4.2 simulation is the executable spec for the yield pins; its per-voter rendered
graphs are in the audit facts. Mark folded subjects on the meeting context, not in the
belief store (the store should never know about phases).

**Integration risk:**

Cascade is the risk this design exists to prevent; the three guards are observation backing,
the relevance predicate, and the two-voice bar — the seed-30 STOP pin is the tripwire wired
to the owner principle. The double-fold hazard is the one bug class that silently doubles
the constant; its test is non-negotiable. Vote prompts now render mid-meeting-updated
values: the §4.6 inversion count must stay 0 on the 10.9 re-record (gate stacks).

**Ready-to-paste prompt:** `agent_prompts/task-10-7-testimony-ingestion.md`

### Task 10.8 — Crew emergency meeting and pacing
**Branch:** `phase-10-emergency-pacing`
**Depends on:** none (file-disjoint from the wave root; functionally independent)
**Section refs:** DESIGN.md §3.2, §5.2; audits/audit-2026-06-11-2218-gameplay-data.md gp-3 (B-B-1 through B-B-9)
**Complexity:** Integration

Meeting supply is starved and impostor-controlled: 78/78 meetings are body reports, 0
emergency meetings ever fired (the intent exists but is gated behind witnessing a kill in
your own room — 53% of kills are unwitnessed — plus a button-room walk), median 1.56
meetings/game, and only 44% of games reach the accumulator's 2-meeting floor. This task makes
the emergency channel reachable for crew, breaking the kill-cadence monopoly and creating the
runway 10.7's conversions and the 9.8 accumulator need. Pacing is currently INVERTED (every
3-or-fewer-meeting game is a crew win, 3 of 4 four-meeting games are impostor wins), so the
anti-railroad gate in 10.9 is the hard condition, not the meeting count.

**Files in scope:**
- agents/tactical/crewmate_policy.py (add a suspicion-accumulation trigger beside the witnessed-kill trigger: a living crewmate whose private max suspicion over living players reaches the §4.6 threshold 0.60, with no meeting held since that belief crossed, sets EmergencyMeetingIntent and walks to the button as today — the walk stays, it is the counterplay cost; eligibility: at most ONE emergency call per player per game, plus a global cooldown of EMERGENCY_COOLDOWN_TICKS since the last meeting ended, a named constant anchored to the mean kill interval (~6 ticks on the W0 set) and reported in the PR — the anchor reasoning, recorded for future re-tunes: emergency supply should roughly match and never exceed organic body-report supply, so meetings cannot spawn faster than evidence accrues; the anchor shifts when kill cadence changes, and Wave 2's kill-intent gating will change it — re-derive there; the missing-player trigger is explicitly OUT — revisit only if supply is still starved after this wave; impostor policy untouched — impostors gain no button behavior until Wave 2 decides it)
- orchestrator/game.py (verify the EmergencyMeetingIntent path end-to-end into a meeting with trigger EMERGENCY; bump crewmate_report to v6 in DEFAULT_PROMPT_VERSIONS)
- agents/strategic/prompts/crewmate_report.j2 (an emergency-opening branch ONLY: when the meeting trigger is EMERGENCY the opener is the caller and the prompt frames the meeting as called-on-suspicion — state who you suspect and the first-hand basis, or unsure; the body-report branch is byte-unchanged; version v5 to v6)
- tests/agents/test_strategic_prompts.py + tests/agents/test_crewmate_policy.py + tests/orchestrator/* (pins below) + tests/fixtures/prompt_regression/ (regenerate the baseline for v6 per the established pattern)

**Files NOT in scope:**
- agents/tactical/impostor_policy.py (Wave 2)
- meetings/transcript.py, agents/memory/beliefs.py, meetings/manager.py vote/fold logic (10.6 and 10.7 own those seams; the meeting layer already accepts a trigger field)
- engine/** (the emergency action exists; no rule changes)
- vote_ballot.j2 and the §4.6 render (frozen); the 9.8 decay constants (the decay-vs-cadence question is ACCOUNTED in 10.9's report, not re-tuned here)
- replays/samples/**

**Definition of done:**
- [ ] Trigger unit pins: the intent fires when private max suspicion crosses 0.60 with no meeting since the cross; it does not fire below threshold, during cooldown, after the player's one call is spent, or for impostors (asserted against impostor policy output).
- [ ] End-to-end scenario: an unwitnessed kill followed by accumulated suspicion produces an EMERGENCY-triggered meeting with the caller as opener, opt-ins and ballots running normally, and the §5.2 chain rules unchanged.
- [ ] The emergency opening renders the called-on-suspicion frame; the body-report branch renders byte-identically to v5 for body meetings (golden-pin both branches); DEFAULT_PROMPT_VERSIONS and the version test pins read v6 — lineage confirmed at branch time: this builds on the v5 merged in Wave 0 and recorded by 10.5, no Wave-1 task touches the template in parallel (10.7 is prompts-frozen), so the lineage is v5 to v6 and this task is the sole owner of the prompt-regression baseline regeneration.
- [ ] A body-less meeting carries no found_body observation and nothing downstream assumes one (transcript, ballots, eval readers run clean on an EMERGENCY meeting fixture).
- [ ] Determinism: trigger evaluation is a pure function of the agent's observation/belief state; cooldown bookkeeping replays identically.
- [ ] `uv run mypy .`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run lint-imports`, `uv run python scripts/generate_prompts.py --check`, `uv run python scripts/validate_task_docs.py`, `uv run pytest`, and `bash scripts/check.sh` all pass.

**Public types introduced:**
- EMERGENCY_COOLDOWN_TICKS

**Implementation hint:**

The witnessed-kill path at crewmate_policy.py:105 and the button-walk at :203-218 are the
existing machinery — the new trigger is a second producer of the same intent, not a new
pipeline. Threshold one-home: read the §4.6 gate constant, do not restate 0.60. The
crewmate_report branch should follow the template's existing conditional style; keep the
emergency branch additive so the v5 body path stays byte-stable (the golden pin enforces it).

**Integration risk:**

Meeting spam is capped by once-per-player plus the global cooldown; the real risk is the
pacing inversion — more meetings currently correlate with MORE wrong ejections, which is why
this ships in the same re-record as 10.7's conversion fix and why 10.9 hard-gates on
wrong-ejection games not rising. The stopwatch coupling (13 margin-1 wins, 8 photo-finishes)
is reported in 10.9, never tuned here.

**Ready-to-paste prompt:** `agent_prompts/task-10-8-crew-emergency-meeting-and-pacing.md`

### Task 10.9 — Wave-1 combined re-record and gate
**Branch:** `phase-10-wave1-rerecord`
**Depends on:** 10.6, 10.7, 10.8
**Section refs:** DESIGN.md §9, §11.4; tasks/phase-9.md 9.5 protocol; audits/audit-2026-06-11-2218-gameplay-data.md gp-7
**Complexity:** Integration

Operator task, local session, after 10.6-10.8 merge. ONE combined re-record of BOTH sets
(flat 4p/1i + 9p2i) on qwen3.5:9b via scripts/refresh_samples.sh, smoke-first with
STOP-for-go, then the stacked gate. The A/B baseline is the 10.6-re-derived corrected W0
table read from `tests/fixtures/phase10/corrected_w0_baseline.json` — the one home 10.6
committed; never PR #143's raw numbers, never a re-derivation inside this task.

**Files in scope:**
- replays/samples/** (both sets re-recorded; MANIFEST provenance per the rev-parse-HEAD convention)
- tests/fixtures/** (era pins that legitimately move; each move named in the PR Decisions)
- tasks/phase-10.md (check off; record the gate table)

**Files NOT in scope:**
- everything else — any source change discovered mid-record is a STOP-and-escalate, recorded on a smoke-abandon branch per doctrine; no papering edits

**Definition of done:**
- [ ] Smoke (5 seeds, 9p2i) green, then STOP for explicit owner go before the full run.
- [ ] HARD validity gate (stacked, all green): friendly-fire 0; game_over 50/50 both sets; betrayal ballots/accusations 0; byte-identical reconstruction; threshold inversions 0; thinking-leak trips 0; dangling reason ids 0; meeting_rate at or above the 0.60 floor.
- [ ] Wave-1 gates: emergency_meetings above 0 set-wide; meetings/game median at or above 2 (report the share of games with 2+ meetings beside it); genuine_class_conversion at or above the corrected baseline; multi_signal_conversion UP vs the corrected baseline; over-gate listeners per accused-impostor meeting UP; ANTI-RAILROAD HARD: games with a wrong ejection NOT above the W0 count of 7, innocents-at-1.0 still 0.
- [ ] Channel telemetry: every pre-vote fold event lists its voices with observation backing (spot-walk 3 from the bytes, and at least one spot-walk must be a ballot whose voter crossed 0.60 BY the pre-vote fold — verify the rendered verdict read MUST-vote and the ballot complied; that is the new render seam where a fresh inversion class would appear); VARYING_ROOMS-class flags 0; retry/unsure-degrade telemetry present; no seed-30-class conversion (a bare-pile-on ejection anywhere fails the gate).
- [ ] The funnel table in the PR: supply gauges (zero-contradiction share, genuine-subject share, over-gate listeners), conversion metrics vs corrected baseline, meetings histogram, emergency usage, win split REPORTED and labelled non-gate, decay/carry survival accounting (the decay-vs-cadence question is answered with data here, decided in a later wave if at all).
- [ ] Provenance tuple (sample dir + commit + model) in the PR; `bash scripts/check.sh` green; any truncation runaway is a STOP (the cap stays frozen).

**Implementation hint:**

Mirror the 10.5 operator rhythm exactly (smoke, go, both sets, gate, funnel). Expect total
meeting count UP (emergency channel) and contradiction volume DOWN vs PR #143 (the
placeholder fix) — the corrected baseline makes that legible. If any HARD line goes red,
stop, push the smoke-abandon branch, and report; do not iterate prompts or constants inside
this task.

**Integration risk:**

This is the wave's only measurement; everything frozen stays frozen during it. The two
known tensions to watch in the funnel: added meetings vs the pacing inversion (the
anti-railroad gate is the arbiter) and the testimony channel vs §4.6 inversions (must stay
0 — the gate reads post-fold values but its rule is untouched).

**Ready-to-paste prompt:** `agent_prompts/task-10-9-wave-1-combined-re-record-and-gate.md`

## Merge Criteria (Phase 10 Wave 1 — crew evidence economy)
- Instrument closed (10.6): allowlist kills the placeholder class with zero TP loss; proxy flags subject-account-gated with the seed-24 TP preserved; Rule-3 relevance-gated but alive; fail-softs degrade instead of dying; gp-7 metrics + corrected W0 baseline shipped.
- Testimony converts (10.7): pre-vote two-witness fold live with the seed-30 pile-on pin green; single-voice behavior byte-identical; no double-fold.
- Supply unblocked (10.8): emergency channel reachable with caps; v6 opening branch; body path byte-stable.
- Measured once (10.9): one combined re-record; HARD + Wave-1 gates green; anti-railroad holds; funnel published against the corrected baseline.
- THE PAUSE: Wave 1 ends at 10.9's merge. The design thread re-runs the close audit on the new baseline; Wave-2 contracts are authored only after that audit AND the 10.10 deception probe.

## Wave 2 — Impostor gameplay (SKETCH — contracts authored after the Wave-1 gate + deception probe)

Updated inputs from the 2026-06-11 close audit (gp-4): the fake-task path is structurally
unreachable today (impostor_policy.py:570-595 falls to wait because pending_task_id is never
populated — 0 do_task / 0 report across 50 games, 53.3% wait vs crew 10.4%); accused-impostor
survival is 93% but only 28/53 survivals involved ACTIVE deflection (25 were passive crew
under-conversion) — any toolkit A/B gates on the active subcount with 10.7 frozen during
measurement; impostor ballot-push was the decisive margin in 2/7 wrong ejections; 19/50 games
ran on one active killer, so toolkit activation shifts the supply/stopwatch numbers and B-2,
B-5, B-8 get re-derived.

- 10.10 Deception probe (the pre-contract gate, model-probe harness): before any toolkit
  contract is written, extend experiments/model_probe to measure whether qwen3.5:9b can
  (a) emit a plausible fake-task pattern, (b) deflect an accusation without boomeranging onto
  itself, (c) self-report a kill with a pre-built alibi that survives the repaired detector.
  Cheap, offline, $0 — the same pre-validation pattern that de-risked the conversion prompts.
  If the 9B cannot play the villain, the toolkit contract changes shape (or the model question
  reopens) BEFORE a wave is spent on it.
- 10.11 Impostor toolkit (gp-4): fake do_task (consumes the tick, renders as do_task, no
  progress — ships only WITH a crew-side checkability counter) + an idle budget tuned toward
  the crew wait-rate (~10%); a report action with an occasional self-report-own-kill policy;
  kill-intent gating on same-room co-presence at intent time (eliminates the ~20 cross-room
  MECH-B-1 refusals, ~15% of kill intents; this shifts the kill cadence that anchors
  EMERGENCY_COOLDOWN_TICKS — re-derive that anchor at the 10.13 gate). The 7.12/9.3 firewalls
  and betrayal==0 stay inviolate.
- 10.12 Indistinguishability metrics (gp-4 gate): impostor wait-rate vs crew, task-emission
  overlap, top-2-idler overlap (the fingerprint to erase), impostor-reporter share,
  kill-success rate; deception metrics conversion-controlled per 10.4, and the
  deflection-effectiveness gate reads the ACTIVE subcount, never raw accused-survival.
- 10.13 Wave-2 combined re-record + the phase-close audit.

Parked / explicit non-goals for the phase: tie-break + accused-self-vote semantics (gp-8,
owner-parked — ties stay SKIPPED); §4.6 gate or threshold changes; tally/abstain redesign
(refuted); turn/vote token caps; accumulator constant re-tuning; the MANIFEST provenance
convention (affirmed).
