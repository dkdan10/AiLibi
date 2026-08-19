# Agent Prompt — 20.26 Grounding the prosecution: every spoken sighting is checked against the speaker's own record; STRONG needs two sources

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.26 — Grounding the prosecution: every spoken sighting is checked against the speaker's own record; STRONG needs two sources, anchored to audits/review-2026-08-19/A/collated-findings.md §G-2 + audits/review-2026-08-19/A/verdicts.md (the G-2 verdict: CONFIRMED-DESIGN-CHOICE, twice ratified, P0/corrob-9); audits/review-2026-08-19/B/collated-findings.md §C-11 + audits/review-2026-08-19/B/verdicts.md (the C-11 verdict: CONFIRMED, severity corrected to P1); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 item 2.4 ("the centrepiece") + §2 claim 6 + §1 RC2; meetings/transcript.py:1414-1421 (`detect_contradictions` takes `vent_witness_records` and NO `sighting_records`), :2170-2179 (`_iter_sightings` yields every spoken `SawPlayerObservation` unfiltered), :2380-2494 (`_detect_alibi_vs_sightings` never inspects the sighter's record), :2411-2414 (the Task 18.9 interior exemption) + :2415-2419 (the 13.14 LONE-STRONG comment), :160-181 + :2721-2747 + :2749-2856 (the Task 16.7 grounding chokepoint, wired only to the −0.05 vouch), :105 ("A STRONG flag naming a CREWMATE is a false positive"), :541 + :559-566 + :641 + :666 (the weak-marker literal, the reason literals, `PHYSICAL_CONTRADICTION_MIN_VOICES`, `SIGHTING_GROUNDING_TICK_TOLERANCE`), :3339-3399 (`_apply_proxy_intra_turn_guard`, the post-pass precedent); meetings/manager.py:1060-1064 (the per-speaker vent mapping) + :1114, :1146, :1188, :1229 (the four detector call sites) + :1235-1246 (the 16.7 "deliberately NOT threaded" note); meetings/schemas.py:183-199 ("NEVER a contradiction flag"); orchestrator/game.py:1081 + :2774-2816 (`sighting_records` already built per participant on the live path); agents/memory/beliefs.py:104 + :108 + :636 (0.30 / 0.08 / −0.05); tasks/phase-13.md:700 (the 2026-06-22 LONE-STRONG owner ruling); tasks/phase-18.md Task 18.9 (the default-OFF lever + committed-bytes counterfactual precedent); tests/meetings/test_contradictions.py:2071-2228 (the committed-bytes re-derivation harness this task extends). Every anchor re-verified at HEAD by the planning session; two corrections to the harness's own comments are folded into this task's scope (below).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-grounded-prosecution`
**Depends on:** 20.24 (the self-location trail lands first — this lever judges a spoken sighting against the same first-hand record the memory now renders, so an agent can copy from the record it is prosecuted by; grounding a channel the speaker cannot read would move the injustice rather than close it), 20.25 (movement resolution lands first — it rewrites an origin-half re-speak into a destination placement inside the same sighting index this lever then grounds, and both edit the same detector function, so the order is a semantic prerequisite AND a file-collision edge)
**Section refs:** audits/review-2026-08-19/A/collated-findings.md §G-2 + audits/review-2026-08-19/A/verdicts.md (the G-2 verdict: CONFIRMED-DESIGN-CHOICE, twice ratified, P0/corrob-9); audits/review-2026-08-19/B/collated-findings.md §C-11 + audits/review-2026-08-19/B/verdicts.md (the C-11 verdict: CONFIRMED, severity corrected to P1); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 item 2.4 ("the centrepiece") + §2 claim 6 + §1 RC2; meetings/transcript.py:1414-1421 (`detect_contradictions` takes `vent_witness_records` and NO `sighting_records`), :2170-2179 (`_iter_sightings` yields every spoken `SawPlayerObservation` unfiltered), :2380-2494 (`_detect_alibi_vs_sightings` never inspects the sighter's record), :2411-2414 (the Task 18.9 interior exemption) + :2415-2419 (the 13.14 LONE-STRONG comment), :160-181 + :2721-2747 + :2749-2856 (the Task 16.7 grounding chokepoint, wired only to the −0.05 vouch), :105 ("A STRONG flag naming a CREWMATE is a false positive"), :541 + :559-566 + :641 + :666 (the weak-marker literal, the reason literals, `PHYSICAL_CONTRADICTION_MIN_VOICES`, `SIGHTING_GROUNDING_TICK_TOLERANCE`), :3339-3399 (`_apply_proxy_intra_turn_guard`, the post-pass precedent); meetings/manager.py:1060-1064 (the per-speaker vent mapping) + :1114, :1146, :1188, :1229 (the four detector call sites) + :1235-1246 (the 16.7 "deliberately NOT threaded" note); meetings/schemas.py:183-199 ("NEVER a contradiction flag"); orchestrator/game.py:1081 + :2774-2816 (`sighting_records` already built per participant on the live path); agents/memory/beliefs.py:104 + :108 + :636 (0.30 / 0.08 / −0.05); tasks/phase-13.md:700 (the 2026-06-22 LONE-STRONG owner ruling); tasks/phase-18.md Task 18.9 (the default-OFF lever + committed-bytes counterfactual precedent); tests/meetings/test_contradictions.py:2071-2228 (the committed-bytes re-derivation harness this task extends). Every anchor re-verified at HEAD by the planning session; two corrections to the harness's own comments are folded into this task's scope (below).
**Complexity:** Integration
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/meetings tests/api/test_evidence_mechanisms.py tests/eval/test_evidence_honesty.py -q` green; the counterfactual cells quoted in the PR Summary — STRONG `alibi_vs_sighting` 234 → after, grounded share of surviving sighting sides 100%, impostor share of surviving STRONG subjects against the 25.3% base (quoted, not gated), and how many of the 70 sole-flag wrongful-ejection meetings still carry a STRONG flag on the innocent; sole-flag PRECISION cannot be measured until the record, so the pre-record proxies are the impostor share and the grounded share.

The project built the right thing once, on the wrong half. A spoken `saw_vent`
is checked against the speaker's own typed record before it can mint a flag
(the 15.4 chokepoint), and a spoken `saw_player` is checked against the
speaker's own record before it can earn its subject the −0.05 vouch (the 16.7
chokepoint at `meetings/transcript.py:2749-2856`). The PROSECUTORIAL half was
never wired: `_iter_sightings` (`:2170-2179`) yields every spoken
`SawPlayerObservation` unfiltered, `_detect_alibi_vs_sightings` (`:2380-2494`)
never reads `sighting.speaker` except for the proxy re-target, and
`detect_contradictions` (`:1414-1421`) has no `sighting_records` parameter at
all — it structurally cannot ground this kind. `meetings/schemas.py:194` states
the asymmetry as doctrine: grounding a sighting feeds the vouch channel,
"NEVER a contradiction flag". The live path already HOLDS the missing input:
`orchestrator/game.py:1081` puts each participant's
`sighting_records_for_meeting()` on `MeetingParticipant`, and
`meetings/manager.py:1235-1246` records in prose that the mapping is
"deliberately NOT threaded" because threading it would move committed bytes.
This task threads it, behind a lever, so the bytes move only at the record.

The cost of the asymmetry is the largest single defect the review found, and
both tracks found it independently. Review-measured over the committed
baseline-6 bytes (A/verdicts.md §G-2): resolving the 170 resolvable sighting
sides against the sighter's own per-tick visibility, **63.5% were never
perceived by that speaker at that tick** (28.8% not even within ±2 ticks); the
STRONG `alibi_vs_sighting` class names an impostor **33/192 = 17.2%** against a
25.3% random baseline of living voters — *below chance*, binomial one-sided
p=**0.0048**; as the SOLE convicting evidence it is **12 right / 70 wrong =
14.6% precise**, against `vent_sighting`'s 310/316; **70 of the 79 wrongful
ejections carry one, and in all 70 it is the only strong flag on the victim**;
82 meetings whose only strong flag is this kind eject 77 times (93.9%) versus
42/306 (13.7%) with no strong flag. B/verdicts.md §C-11 re-derives the same
shape from engine role-truth on 96 games: 60 STRONG flags, **53 naming a
crewmate (88.3%)**, 17 of them minted off an impostor-authored sighting, while
the grounded sibling reads `vent_sighting` 107/107 impostor; ejections whose
only strong flag was this kind split IMP 3 / CREW 20, i.e. **80% of that
corpus's wrongful ejections**. Re-derived at HEAD by the planning session over
all four committed sets (707 meetings, 435 ejections): the recorded census
reproduces the review's table exactly — `alibi_vs_sighting` 234 STRONG / 79
weak, `vent_sighting` 440 STRONG, `alibi_vs_physical` 37 STRONG / 5 weak,
`alibi_conflict` 35 weak — and **187 of the 234 STRONG flags (79.9%) rest on a
single-tick alibi window with the sighting on that same tick**.

The lever installs three rules on this ONE kind. (a) GROUNDING: a spoken
sighting is GROUNDED iff its speaker holds at least one own `SightingRecord`
matching it — same subject, canonically intersecting room, tick within
`SIGHTING_GROUNDING_TICK_TOLERANCE` — reusing `_sighting_observation_matches_record`
verbatim, the same predicate the vouch channel uses; an ungrounded sighting can
still mint a flag (flags are information, §5.4) but never a STRONG one. (b) TWO
SOURCES: a surviving STRONG `alibi_vs_sighting` needs
`GROUNDED_PROSECUTION_MIN_SOURCES` distinct grounded speakers contradicting the
same subject over the same claim, OR one grounded source plus a physical anchor
— a `vent_sighting` or `alibi_vs_physical` flag naming that subject in this same
meeting, the two channels that are grounded by construction. (c) SINGLE-TICK
ENDPOINT: the degenerate `from_tick == to_tick` self-placement stops being
adjudicated as its own interior, so it keeps the pre-18.9 narrow-window /
endpoint band. Rules (b) and (c) knowingly SUPERSEDE two owner rulings for the
post-20 substrate: the 2026-06-22 LONE-STRONG relaxation
(`tasks/phase-13.md:700`, "a single-witness `alibi_vs_sighting` contradiction
MAY cross the gate") and the Task 18.9 endpoint-band exemption that promoted
roll-call whereabouts answers to STRONG. Both were adopted on evidence and are
being reversed on more of it; the module docstring records each in one
history line and the phase doc carries the ruling.

The scope firewall is deliberate and narrow. `vent_sighting` (440/440 impostor)
and `alibi_vs_physical` (37 STRONG, already two-voice-gated) are UNTOUCHED —
their counts over the committed sets are pinned unchanged under the lever, and
`alibi_conflict` has no sighting side to ground. The lever is inert twice over:
OFF by default, and a NO-OP when the caller supplies no per-speaker mapping —
one predicate gates all three rules, so the record-free re-derivers (eval,
audit workflows) keep the pre-20.26 rules rather than silently reading every
sighting as fabricated. Before the record, the honest price is published: the
counterfactual re-runs the detector under the lever over the 300 committed
games' reconstructed inputs and quotes what the class becomes, in both
directions — the pre-registration's falsifiable prediction, made before the
23 h event that would test it.

**Files in scope:**
- meetings/transcript.py; (the lever: `detect_contradictions` receives the per-speaker SightingRecords; a spoken sighting not grounded in the speaker's own record cannot mint a STRONG flag (weak at most, labelled ungrounded); a STRONG alibi_vs_sighting requires two independent grounded sources OR one grounded source plus a physical/vent anchor; single-tick endpoint windows are suppressed; OFF-path byte-identical)
- meetings/manager.py; (pass the sighting records it already builds for vouching into detection — call-site only)
- meetings/constants.py; (the lever's thresholds as named constants)
- tests/meetings/test_contradictions.py; (OFF byte-identity; ON fixtures for each rule; the seed-17 m0 / seed-23 m1 / seed-8 m4 injustice shapes do not mint STRONG)
- tests/meetings/test_manager.py; (the wiring)
- tests/api/test_evidence_mechanisms.py; (the four 19.11 injustice fixtures read under the lever: each records its new outcome)
- tests/eval/test_evidence_honesty.py; (counterfactual: STRONG alibi_vs_sighting count, grounded share, impostor share under the lever over the 300 committed games)

**Files NOT in scope:**
- agents/strategic/prompts/ (the "VERIFIED evidence" wording is the single prompt-set bump, Task 20.31 — no template byte moves here, and no other task in this phase may touch a `.j2`)
- agents/memory/ (the records are built by the manager from memory; memory is not edited)
- eval/deduction_metrics.py (reads flags; unchanged)
- eval/evidence_honesty.py (the instrument module is Task 20.15's; this task CONSUMES its cells and must not redefine one — if a needed cell is missing, say so in the PR rather than re-implementing it here)
- eval/meeting_quality.py, eval/vote_correctness.py, eval/watchability.py, audits/workflows/extract_gameplay_facts.py (record-free re-derivers; the lever is a structural no-op for them — see Integration risk)
- meetings/voting.py, agents/memory/beliefs.py (the §4.6 gate and the 0.30 / 0.08 / −0.05 deltas are untouched: this task changes CLASSIFICATION only, the 13.14 precedent)
- orchestrator/replay.py (Task 20.33 registers every Phase-20 lever in the substrate stamp at once; this task registers nothing and adds no `SUBSTRATE_FLAG_KEYS` entry)
- replays/ (no committed byte moves; the counterfactual reads them and writes nothing)

**Definition of done:**
- [ ] `meetings.transcript.grounded_prosecution_enabled(env)` follows the 13.5 resolver signature, defaults OFF on an unset/empty/unrecognised value, accepts `1/true/yes/on` case-insensitively, and is read ONCE in `detect_contradictions`, which threads the boolean down (the 18.9 one-read convention).
- [ ] OFF-path byte identity: `detect_contradictions` re-derives the recorded flags over ALL 707 committed meetings in the four sets (`tests/meetings/test_contradictions.py`), with `env` absent and `env={}` agreeing, and with the sighting mapping supplied but the lever OFF also agreeing. The harness's samples-only restriction and its "195-meeting" comment are stale at HEAD (all 503 ml_corpus meetings re-derive byte-identically since the corpus re-record) — extend the walk and correct the comment.
- [ ] `bash scripts/verify_samples.sh` stays 100/100 and `tests/meetings/test_prompt_byte_golden.py` stays green (204 committed meetings), with the lever unset — the standing OFF-path proof that no rendered or recorded byte moved.
- [ ] Rule (a) is fixture-pinned in `tests/meetings/test_contradictions.py`: a speaker with no matching record mints an `alibi_vs_sighting` carrying the ungrounded weak reason and never a STRONG one; the perturbation — give that speaker a matching record — restores STRONG on the identical transcript.
- [ ] Rule (b) is fixture-pinned: one grounded source alone bands weak; two grounded sources from DISTINCT speakers band STRONG; the SAME speaker grounding twice (two records, or two sightings in one turn) stays weak (the double-count guard); one grounded source plus a `vent_sighting` or `alibi_vs_physical` anchor naming the same subject bands STRONG.
- [ ] Rule (c) is fixture-pinned: a `from_tick == to_tick` self-placement contradicted at that tick bands weak under the lever (the pre-18.9 narrow-window/endpoint reasons, unchanged literals); the perturbation — widen the claim to a multi-tick window with an interior sighting — mints STRONG.
- [ ] Non-interference is pinned over the committed sets under the lever ON with reconstructed inputs: `vent_sighting` 440 STRONG, `alibi_vs_physical` 37 STRONG / 5 weak, `alibi_conflict` 35 weak — all unchanged; only `alibi_vs_sighting` moves, and no flag's `contradiction_id`, `kind`, `event_a_id`, `event_b_id` or `subjects` changes (a demotion rewrites the description only, so the detector's sort and every citation id are stable).
- [ ] The three named injustice shapes are pinned by name in `tests/meetings/test_contradictions.py`: samples/9p2i seed 17 m0, seed 23 m1 and seed 8 m4 mint no STRONG `alibi_vs_sighting` on the ejected crewmate under the lever, each case naming which rule bit.
- [ ] `tests/api/test_evidence_mechanisms.py` keeps its frozen-pipeline assertions over the served DTOs unchanged (the lever is OFF for the served bytes) and ADDS one lever-ON counterfactual read per mechanism, recording each fixture's new outcome explicitly — `provenance_impossible_sighting`, `content_vs_own_memory_miss`, `one_tick_interval_artifact`, `equal_weight_conflict` — as asserted values, never as a loosened assertion.
- [ ] `meetings/manager.py` passes the per-speaker `sighting_records` mapping (built from `MeetingParticipant.sighting_records`, participants with no records omitted) into ALL FOUR `detect_contradictions` call sites, so a mid-chain turn prompt and the final recorded flag set read one grounding source (the 15.4 threading convention); `tests/meetings/test_manager.py` pins the wiring and pins that the mid-chain and final derivations agree.
- [ ] The counterfactual pins in `tests/eval/test_evidence_honesty.py`, over the four committed sets under the lever ON with per-speaker records reconstructed from the replay: STRONG `alibi_vs_sighting` 234 → after; the grounded share of surviving sighting sides = 100%; the impostor share of surviving STRONG subjects against the 25.3% base (quoted, not gated); and, over the meetings behind the 70 sole-flag wrongful ejections, how many still carry a STRONG flag on the innocent (quoted).
- [ ] The module docstring records the two supersessions in one history line each (the LONE-STRONG relaxation and the endpoint-band exemption, each naming the ruling it supersedes and that it applies only with the lever ON) — history, not narration; the phase-doc ruling is the assembler's, not this task's.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — the input seam. Widen `detect_contradictions` with a keyword-only
`sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]] | None = None`,
exactly mirroring `vent_witness_records`. Gate all three rules on ONE predicate
computed once at the top: the resolver is ON AND the mapping is non-empty. A
caller with no mapping keeps the pre-20.26 rules by construction — that is what
makes the record-free re-derivers safe and what makes the OFF-path pin trivially
true. Say so in the docstring the way the 16.7 chokepoint states its own
record/replay boundary.

Step 2 — rule (c) rides an existing branch. `_detect_alibi_vs_sightings` already
takes `whereabouts_interior_flags: bool` and its `False` branch is the
byte-identical pre-18.9 path (`meetings/transcript.py:2411-2414` and the comment
above it). Thread the new boolean in and make `interior_exempt` require it to be
OFF; nothing else in that function changes, and the weak-reason literals stay
untouched.

Step 3 — rules (a) and (b) are a post-pass, the `_apply_proxy_intra_turn_guard`
shape (`:3339-3399`). Build two indexes once: `event_id -> speaker` for sighting
events (the guard already builds a speaker index — reuse the pattern), and
`event_id -> grounded?` from `_sighting_observation_matches_record` over the
speaker's own rows. Run the pass AFTER the 10.10 guard and AFTER the vent flags
are joined, so the physical-anchor set is complete. Touch only
`kind == "alibi_vs_sighting"` flags that are not already weak (an existing weak
marker means the flag is already banded — never double-mark), and rebuild a
demoted flag through the same description builder with the reasons appended in
one fixed order (ungrounded first, then lone-source) so the output is
deterministic. `_build_contradiction` derives `contradiction_id` from the kind
and the sorted event-id pair, so a re-description leaves ids, sort order and
ballot citations byte-stable.

Step 4 — independence means DISTINCT SPEAKER IDS. Collect the grounded
contradicting sightings for a given (subject, claim) as a set of speaker ids,
excluding the subject itself and the alibi's own speaker; one speaker with two
records or two sightings is ONE source. The physical anchor is a
`vent_sighting` or `alibi_vs_physical` flag naming the same subject in this
meeting's flag set — both are grounded channels, so the anchor never
re-introduces ungrounded speech.

Step 5 — the constant. `GROUNDED_PROSECUTION_MIN_SOURCES = 2` is homed in
`meetings/constants.py` (stdlib-only leaf, the 15.6 constant-homing convention)
so the pre-registration memo can cite it without importing the 3-KLoC detector;
the tick tolerance is the existing `SIGHTING_GROUNDING_TICK_TOLERANCE`, reused,
never re-declared. The weak-reason string literals stay beside their siblings in
`meetings/transcript.py`.

Step 6 — the counterfactual reconstructs, it does not peek. Per-speaker
`SightingRecord`s come from rebuilding each participant's own memory from the
replayed packets and reading the accessor's projection (the instrument module's
reconstruction, the same one the review's harness used) — never from omniscient
state, and never by parsing a description. Toggle the lever through the `env`
parameter of the resolver, never by mutating `os.environ`. Quote the cells in
the PR Summary in both directions: what stops being minted AND what the class
looks like after.

## Public types this task introduces
- `meetings.transcript.grounded_prosecution_enabled`
- `meetings.transcript.ENV_GROUNDED_PROSECUTION`
- `meetings.transcript.WEAK_REASON_UNGROUNDED_SIGHTING`
- `meetings.transcript.WEAK_REASON_LONE_GROUNDED_SOURCE`
- `meetings.constants.GROUNDED_PROSECUTION_MIN_SOURCES`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This is the phase's centrepiece and the widest `meetings/transcript.py` change
since the 13.14 reversal: three rules, one lever, the vouch path untouched.

Risk 1 — over-suppression. The vent channel must not move: `vent_sighting` flags
are grounded by construction and must keep 440/440 over the committed sets, and
`alibi_vs_physical` (37 STRONG) is already two-voice-gated, so neither is
re-banded here. The pass filters on `kind == "alibi_vs_sighting"` and on the
absence of an existing weak marker; the census pin above is what proves it.

Risk 2 — a second-source definition that counts the same speaker twice. One
speaker holding two matching records, or emitting two sightings in one turn, is
ONE source; the subject and the alibi's own speaker are never sources. The
double-count case has its own fixture, and it is the shape most likely to pass a
casual review while restoring exactly the lone-witness conviction this lever
exists to remove.

Risk 3 — the 19.11 fixtures change MEANING under the lever. Their frozen
assertions describe the served committed bytes and must stay exactly as they
are; the lever-ON reading is an ADDITIONAL recorded outcome per mechanism.
Loosening an assertion to make both readings pass would delete the exhibit's
evidentiary value, which is the one thing Task 19.11 built it for.

Risk 4 — the record-free re-derivers. `eval/meeting_quality.py`,
`eval/vote_correctness.py`, `eval/watchability.py` and
`audits/workflows/extract_gameplay_facts.py` call `detect_contradictions`
without any typed records, so they already lose the whole grounded vent channel
relative to the recorded flags; after the Phase-20 record their
`alibi_vs_sighting` re-derivation will diverge too. This task does NOT change
them — the "mapping absent means pre-20.26 rules" gate keeps them exactly where
they are — but the phase's own instruments must read RECORDED flags or
reconstruct the records, never the record-free re-derivation, or they will
measure the old substrate on new bytes. State this explicitly in the PR.

Risk 5 — owner-ruling supersession. Two ratified rulings are reversed for the
post-20 substrate. They are reversed behind a default-OFF lever, with the
counterfactual published before the record, and each is recorded in one
docstring line; nothing about the pre-record substrate changes, so a reader of
the committed bytes still sees the rulings that produced them.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import eval.evidence_honesty"`
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

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-grounded-prosecution` with a title like `task 20.26: grounding the prosecution: every spoken sighting is checked against the speaker's own record; strong needs two sources`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/A/collated-findings.md §G-2 + audits/review-2026-08-19/A/verdicts.md (the G-2 verdict: CONFIRMED-DESIGN-CHOICE, twice ratified, P0/corrob-9); audits/review-2026-08-19/B/collated-findings.md §C-11 + audits/review-2026-08-19/B/verdicts.md (the C-11 verdict: CONFIRMED, severity corrected to P1); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 item 2.4 ("the centrepiece") + §2 claim 6 + §1 RC2; meetings/transcript.py:1414-1421 (`detect_contradictions` takes `vent_witness_records` and NO `sighting_records`), :2170-2179 (`_iter_sightings` yields every spoken `SawPlayerObservation` unfiltered), :2380-2494 (`_detect_alibi_vs_sightings` never inspects the sighter's record), :2411-2414 (the Task 18.9 interior exemption) + :2415-2419 (the 13.14 LONE-STRONG comment), :160-181 + :2721-2747 + :2749-2856 (the Task 16.7 grounding chokepoint, wired only to the −0.05 vouch), :105 ("A STRONG flag naming a CREWMATE is a false positive"), :541 + :559-566 + :641 + :666 (the weak-marker literal, the reason literals, `PHYSICAL_CONTRADICTION_MIN_VOICES`, `SIGHTING_GROUNDING_TICK_TOLERANCE`), :3339-3399 (`_apply_proxy_intra_turn_guard`, the post-pass precedent); meetings/manager.py:1060-1064 (the per-speaker vent mapping) + :1114, :1146, :1188, :1229 (the four detector call sites) + :1235-1246 (the 16.7 "deliberately NOT threaded" note); meetings/schemas.py:183-199 ("NEVER a contradiction flag"); orchestrator/game.py:1081 + :2774-2816 (`sighting_records` already built per participant on the live path); agents/memory/beliefs.py:104 + :108 + :636 (0.30 / 0.08 / −0.05); tasks/phase-13.md:700 (the 2026-06-22 LONE-STRONG owner ruling); tasks/phase-18.md Task 18.9 (the default-OFF lever + committed-bytes counterfactual precedent); tests/meetings/test_contradictions.py:2071-2228 (the committed-bytes re-derivation harness this task extends). Every anchor re-verified at HEAD by the planning session; two corrections to the harness's own comments are folded into this task's scope (below).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
