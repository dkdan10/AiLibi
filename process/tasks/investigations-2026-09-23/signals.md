# Signals: the five SIGNAL-classed red tests at 95fb894b

Investigator memo, 2026-09-23. Read-only at `95fb894b` (baseline 9 on `main`), with a
`git archive 39a568c6` export (baseline 8) in scratch for before/after. No tracked file
edited, no commit, no provider call, no recorder, no held-out band, no `--complete`, no
rendered prompt printed. Every census below is count-only. Role-correctness is reported
where the question asks for it and is never proposed as a gate.

Owner rulings this memo serves: Q5 of the re-ground card (2026-09-23), "Look into why the
tests would still fail, if they are necessary at all, or a separate potential path forward.
Go with the recommended idea from that."

Name note: the brief calls the fifth test `test_rederivation_diverges_only_at_the_allowed_weak_kinds`;
at `95fb894b` it is `tests/meetings/test_transcript.py::TestCommittedBytesArtifactCollapse::test_rederivation_diverges_only_at_the_repaired_sites` (`:1930`).

## 1. Verdict in one paragraph

None of the five is a design invariant that the record broke through a substrate defect in
the way the test states it. Three of them (T1, T2, T5) are read through a **records-free
re-derivation** that cannot see the speakers' private movement channel, and that harness,
not the bytes, is what fails: rebuilding the three private channels (vent, movement,
sighting) from the replay walk through the real perception path reproduces **676 of 676**
committed meetings byte-for-byte at baseline 9 and **672 of 672** at baseline 8, in about
9 s. The same harness was already blind at baseline 8: the recording then held two STRONG
`alibi_vs_sighting` flags on the crewmate p-9 (samples/9p2i seed 41 meeting 2, the
direction memo's lead defect) that convicted him, while T1 and T2 read zero and stayed
green. T3 and T4 are measured consequences of the route claim (more testimony rows per
render; a comparand deleted at graduation). One real substrate question does surface, in
T2: the only recorded ejection riding a STRONG sighting flag at baseline 9
(ml_corpus/9p2i seed 1041 meeting 1) rests on a contradiction that is false at its own
tick. Recommendation: fix all five by test changes now (one test-only card for T1, T2, T5
plus two small edits for T3, T4), and route the 1041 question to the owner as a separate
substrate card that would land only at the next combined re-record.

## 2. What was run

All five fail at `95fb894b` (`uv run pytest -p no:cacheprovider <id>`; the two contradiction
tests take 2.3 s, the other three 10 s together), and all five pass on the baseline-8 export
(the three contradiction/transcript tests re-run there: 5 passed in 1.7 s).

Probes (scratch, outside the tree; run with `PYTHONPATH=<tree> uv run --frozen --no-sync python <probe>`):

- `probe_contra.py`: each grounded-leg STRONG survivor and each strong-sighting ejection:
  subject role, recorded band of the same id, re-derived band, carrier composition
  (grounded sighting speakers / vent anchors / physical anchors), movement-divergence
  membership.
- `probe_reconstructed.py`: walks every committed game with `eval.replay_walk.walk_replay`
  plus `eval.evidence_honesty._perceive_tick` / `_fold_meeting_into_memories`
  (`eval/evidence_honesty.py:1323-1382`), projects each living participant's episodic
  store into `VentWitnessRecord` / `SightingRecord` / `MoveWitnessRecord` exactly as the
  live accessors do (`orchestrator/game.py:3833-3887`, `:3889-3978`, `:3980-4045`),
  threads them as `meetings/manager.py:1311-1354` does (participants with no rows
  omitted; the sighting mapping and the move accessor drop fellow impostors), passes the
  trigger kind as `meetings/manager.py:1557-1567` does, and compares
  `detect_contradictions(...)` against `entry.contradictions` by full model equality.
  Negative controls: drop the movement channel; drop the sighting channel.
- `probe_truth.py` / `probe_1041.py`: engine truth (booleans and tick deltas only) of both
  sides of each recorded STRONG sighting flag, via `eval.process_scorecard.walk_routes`
  and `AGENT_CLOCK_OFFSET` (`eval/process_scorecard.py:192`, `:791-831`).
- `probe_survival.py`: the T3 census per render, with a planted re-band.

## 3. The shared root cause of T1, T2, T5: a lossy harness, provably

`_rederive` (`tests/meetings/test_contradictions.py:3428-3440`) and its twin
(`tests/meetings/test_transcript.py:1708-1713`) re-run the detector with the sighting channel
inverted from recorded verdicts (`tests/_helpers/committed.py:147-191`), vents rebuilt from
recorded flags (transcript twin: no vents at all), and **no movement channel**. The helper's
docstring states the movement channel "is not recoverable at all" (`tests/_helpers/committed.py:161-165`,
echoed at `tests/meetings/test_contradictions.py:3255-3261` and `test_transcript.py:1698-1703`).
It is recoverable from the replay walk, which the evidence-honesty instrument already runs.

| measurement | baseline 9 (95fb894b) | baseline 8 (39a568c6) |
|---|---|---|
| committed meetings re-derived byte-exact with walk-rebuilt channels | 676 / 676 | 672 / 672 |
| meetings whose rebuilt sighting mapping was empty | 0 | 0 |
| rebuilt channel rows at meeting open (move / sighting / vent) | 24,898 / 95,386 / 857 | 24,792 / 95,824 / 854 |
| drop only the movement channel: meetings that diverge | 68, all inside the pinned 69 | not run |
| recorded STRONG `alibi_vs_sighting` flags | 1 (impostor subject) | 2 (both crewmate p-9) |
| same, records-free `_rederive` | 8 (7 impostor, 1 crewmate) | 0 |

The one pinned "movement-channel divergence" that is not movement is ml_corpus/9p2i seed
1134 meeting 3: every spoken sighting there was recorded ungrounded, so the inversion
returns `{}`, and `grounded_prosecution = bool(sighting_records)` (`meetings/transcript.py:1836`)
drops the detector into the pre-grounding rules; `_rederive` then mints a STRONG flag on a
crewmate that the recording banded `ungrounded sighting`. The green attribution test
(`tests/meetings/test_contradictions.py:3553-3584`) accepts it because its predicate is
"a planted move channel could move this meeting", not "movement did".

## 4. Per test

### T1. `test_contradictions.py::TestGroundedProsecutionCommittedCensus::test_the_fully_grounded_leg_drops_the_whole_class` (`:4133-4154`)

- **Property asserted.** Grounding every spoken sighting (the planted channel,
  `:3387-3406`) leaves zero STRONG `alibi_vs_sighting` flags: "nothing in the class
  convicts". Pinned `(0, 120)`; measured `(8, 113)`.
- **Origin.** Created in Task 20.36, the baseline-7 record (`efcd43b8`), pinned `(0, 105)`;
  the census it belongs to is Task 20.26's counterfactual (`tasks/phase-20.md:4032-4140`).
- **Classification: a measured pin, not a design invariant.** Task 20.26's rule (b) was
  designed to let a STRONG sighting flag survive when two carriers stand behind it
  (`tasks/phase-20.md` 20.26 rule (b); `meetings/transcript.py:4416-4526`; constant
  `GROUNDED_PROSECUTION_MIN_SOURCES = 2`, `meetings/constants.py:46`), and its measurement
  line quotes the impostor share of surviving STRONG subjects "quoted, not gated". The
  class docstring's bracket claim (`:3965-3972`, "two PLANTED channels that bracket the
  truth") is false without the movement channel: at baseline 8 this leg read 0 STRONG while
  the recording carried 2.
- **What the 8 rest on (count-only).** Carriers (sighting speakers / vent anchors /
  physical anchors): 1041 m1 x2 = 3/0/1; 1005 m0, 1021 m0, 1026 m0 = 1/2/0; 1100 m0 = 1/1/0;
  samples seed 7 m0 = 1/0/2; 1010 m1 = 1/0/1. So 4 ride one grounded witness plus vent
  anchors, 2 ride one witness plus physical anchors, 2 are multi-witness. Against the
  recording: 6 of 8 are pairings the recording never carried, 1 is recorded
  `ungrounded sighting` (the planted channel grounds what the real record did not), 1 is
  recorded STRONG. All 8 subjects are impostors (reported only). With the movement channel
  removed from the walk-rebuilt run, the generous leg reproduces `(8, 113)` exactly; with
  it present, it reads **(2, 44)**, both in 1041 m1.
- **Recommendation: re-anchor as a measured pin on the walk-rebuilt movement and vent
  channels.** Walk-rebuilt census, all 676 meetings: off leg `alibi_vs_sighting` 19 strong /
  27 weak; ungrounded leg 0 / 46; generous leg **2 / 44**; the untouched kinds identical on
  all three legs (conflict 3 weak, physical 18 strong / 7 weak, vent 455), so the scope
  firewall still holds and the bracket becomes true (0 <= recorded 1 <= 2). Rename (for
  example `test_the_fully_grounded_leg_keeps_two_strong_on_these_bytes`) and restate the
  comment. The whole census class moves onto the rebuilt channels together, and its
  sibling pins re-derive as MEASURED. **Test change.** Fallback if the card is not taken:
  re-pin `(8, 113)` on the records-free leg and correct both docstrings to say the leg is
  neither a bound on nor a reproduction of the recording.

### T2. `test_contradictions.py::TestGroundedProsecutionInjusticeShapes::test_no_committed_ejection_rides_a_strong_sighting_flag` (`:4174-4189`)

- **Property asserted.** No committed ejection's ejectee carries a STRONG
  `alibi_vs_sighting` flag in the re-derivation; "That is the cell bar 4 reads at 0/0."
- **Origin.** Task 20.36 (`efcd43b8`), reading bar 4 of the baseline-7 record
  (`audits/audit-phase-20-baseline-7.md:262-283`): bar 4 (precision at least 50%) was
  MISSED with an empty class, and the §6 class-closed waiver (pooled denominator below 20)
  was satisfied (`:470-495`). The empty class was the waiver's reading of baseline-7
  bytes.
- **Classification: an invariant the design superseded, measured on the wrong
  population.** The design since 20.26 admits STRONG sighting convictions carried by two
  sources; the 2026-06-22 LONE-STRONG relaxation (`tasks/phase-13.md:700`) is superseded by
  rule (b) (`meetings/transcript.py:280-286`), which is the memory principle's current form
  (innocents ejectable, not at random; corroborate within the round). And the test reads
  `_rederive`, not the recording: at baseline 8 the recorded class had one member, samples
  seed 41 m2 (crewmate, two recorded STRONG flags, 4 eject ballots all citing a flag side
  turn), the production instrument pinned it (`tests/eval/test_evidence_honesty.py:1639`
  was `(0, 1)` on samples/9p2i at `39a568c6`), and this test read empty and passed.
- **What the 5 ejections rest on (count-only).** 4 are re-derivation-only pairings; in the
  recording those ejectees carried 2 STRONG `vent_sighting` flags each (1005, 1021, 1026)
  or 2 STRONG `alibi_vs_physical` (samples seed 7 m0). The recorded class is 1: 1041 m1,
  where the ejectee's only STRONG flag is the sighting flag (recorded carriers 2 sighting
  speakers plus 1 physical anchor) and 6 of 6 eject ballots cite a turn on one of its
  sides. All 5 ejectees are impostors (reported only). The walk-rebuilt run gives exactly
  this recorded class.
- **The defect 1041 m1 exposes (the record did not name it).** Engine truth, count-only:
  the accused's own 7-stay route is TRUE at the sighting tick and the sighting is FALSE
  there. The sighting falls on a one-tick interior stay; the sighted room is 1 hop from the
  claimed one; the engine and the witness's own first-hand record both place the subject in
  the sighted room one tick LATER, and that t+1 row was present in the witness's rebuilt
  render. The witness (a crewmate) spoke it one tick early; grounding accepts it within
  `SIGHTING_GROUNDING_TICK_TOLERANCE = 2` (`meetings/transcript.py:775`); the map-aware
  band does not fire because it measures the gap from the route's OUTER ends (8 and 4
  ticks), by design (`meetings/transcript.py:3357-3386`, the alibi-as-route ruling that an
  interior boundary is a declared transition). Under the direction's §7 test
  (`tasks/direction-2026-09-19-process-over-outcome.md:234-261`) this is a contradiction
  that is not one: role-correct, but not "a genuine contradiction in what the target said".
  Row 3 of the scorecard cannot see it (`eval/process_scorecard.py:1014-1045` refuses
  multi-stay claims; record audit §7.1 third follow-up). Baseline 8's member was the mirror
  image: claim false at the tick, sighting true (the span envelope).
- **Recommendation: restate on the recorded flags as a named-set tripwire.** Read
  `entry.contradictions` (now proven equal to production with the true channels), assert
  the class equals `{ml_corpus/9p2i seed 1041 meeting-1}` (the
  `_STATEMENT_PAIR_CONVICTIONS` precedent: any new member fails), keep the planted case
  (`:4191-4203`), assert no role, and name both the baseline-8 member and this member's
  mechanism in the docstring. **Test change.** Separately, route to the owner a
  **substrate card** (not now): re-read a grounded sighting at the tick its matching record
  holds before pairing (the movement chokepoint's shape), or apply the one-tick adjacency
  band where the witness's own record sits across an interior stay boundary. It changes
  flags, so it lands only at the next combined re-record; with the per-stay row-3 card it
  would count and then remove this class. Not keep-red: the test's "empty" was never the
  design, and holding `check.sh` red until a re-record buys nothing.

### T3. `tests/agents/test_reported_testimony.py::test_reported_rows_survive_in_every_candidate_bucket` (`:930-977`)

- **Property asserted.** In every candidate bucket, reported testimony rows kept / offered
  >= `_SURVIVAL_FLOOR = 0.80` (`:791`, loop `:972-976`). The >150 bucket reads
  5,927 / 7,539 = 0.786.
- **Origin.** Task 20.30 (`d231fe13`), DoD "reported rows are kept in >= 80% of renders in
  EVERY candidate bucket" against a pre-lever 0 of 4,150 (`tasks/phase-20.md:4798-4900`).
- **Classification: a measured pin (an acceptance target met on baseline-7/8 bytes), not a
  design invariant.** The design invariant is the salience band: testimony (60,
  `agents/memory/store.py:97`) above bare co-presence, applied as a strict prefix that stops
  at the first row that does not fit (`agents/memory/store.py:3118-3124`). The wave's own
  ruling points the other way from growing testimony's share: "reported testimony must not
  take the render from the agent's own memory" (`tasks/work/alibi-as-route.md:139-142`).
- **Why it moved (>150 bucket, baseline 8 -> 9).** Renders 74 -> 122; testimony offered per
  render 45.15 -> 61.80; kept per render 43.43 -> 48.58 (kept went UP); renders shedding
  any row 20 -> 76; mean testimony line 78.8 -> 81.0 chars; mean render 5,873 -> 5,876 of a
  6,000-char budget (`DEFAULT_TOKEN_BUDGET = 1500` x 4). The route claim files one statement
  per maximal stay (`tasks/work/alibi-as-route.md:218`), so large renders are offered more
  testimony than the saturated budget holds. Band order holds: in the 232 renders that shed
  a testimony row, 0 rows ranked below testimony survive, against 20,178 such rows kept in
  renders that shed none. Planted: re-band testimony to 25 (`_PRE_COALESCE_REPORTED_BAND`,
  `tests/eval/test_evidence_honesty.py:2066`) and 6,319 lower rows survive in shedding >150
  renders while >150 survival collapses to 169 / 7,539.
- **Recommendation: restate at the strength the design holds.** Delete the flat 0.80 ratio
  floor (a met Phase-20 target, recorded in 20.30's merge note); assert per render that a
  render which sheds a reported row keeps no bare sighting, move, transition or task row;
  keep the exact offered / kept pins already re-derived; add the planted re-band case.
  **Test change.** A budget increase would be a behaviour change (prompt bytes, new card,
  re-record) that nothing here justifies.

### T4. `tests/eval/test_evidence_honesty.py::test_the_band_change_not_the_fold_is_what_costs_first_hand_coverage` (`:4185-4208`)

- **Property asserted.** With the reported band patched back to 25, the fold-only render
  has fewer rows than the recorded render (32,123 vs 32,037: fails) and more first-hand
  coverage (28,359 vs 20,629: holds).
- **Origin.** Task 20.30 (`d231fe13`, `:3319-3339` there): `render_budget.rows_off` was
  then the lever-OFF, uncoalesced render (49,590 rows at baseline 6), so "fewer rows" meant
  compression against the uncoalesced render.
- **Classification: an invariant superseded by graduation.** When the lever graduated
  (`efcd43b8`, `e3cc4282`) the OFF leg became the coalesced, band-raised render, and the
  assertion silently turned into a comparison of two coalesced renders at one character
  budget. Margins since: -137 (b7: 32,135 vs 32,272), -95 (b8: 31,702 vs 31,797), +86 (b9);
  characters at b9 3,160,257 vs 3,162,472 (0.07% apart). Row count is budget-capped, as the
  neighbouring docstring says (`:4145-4175`).
- **Recommendation: retire the rows ordering, keep the rest.** Remove
  `fold_only.rows_on < render_budget.rows_off` with that reason; keep the measured pins
  (rows 32,123; covered 28,359) and the coverage inequality, which carries "the band raise
  spends first-hand coverage"; optionally add sighting rows 18,100 > 12,771, the mechanism
  of the coverage gain. **Test change.**

### T5. `tests/meetings/test_transcript.py::TestCommittedBytesArtifactCollapse::test_rederivation_diverges_only_at_the_repaired_sites` (`:1930-2049`)

- **Property asserted.** Re-derivation reproduces the recorded flags except at classified
  repair sites; every ADDED pairing is a weak proxy re-target or the adjacency band
  (`:2023-2029`). Four additions are not: samples seed 7 m0 (STRONG on impostor p-2, and a
  weak `single grounded source` on a crewmate), seed 32 m0, seed 38 m1 (both weak
  `single grounded source`, crewmate subjects).
- **Origin.** Task 10.6 (`3f9e6a30`), exactness guard of the detector repairs; widened for
  the movement channel at baseline 7.
- **Classification: a design invariant (replay determinism, AGENTS load-bearing rule 1;
  the class docstring's "Re-derivation reproduces the recorded bytes EXACTLY"), measured
  by a lossy harness. No substrate defect.** With walk-rebuilt channels all 145 samples/9p2i
  meetings re-derive byte-exactly, every kind included (107 recorded flags). All four
  additions are absent from the recording; 2 of 4 have no spoken `saw_move` by the witness,
  so no transcript-only classifier can explain them (the resolution arm reads the private
  record, `meetings/transcript.py:2649-2757`). The classifier's `containment` label is also
  stale for routes: it unions every segment's rooms (`:1716-1726`, `:1784-1828`).
- **Recommendation: restore pure exactness on walk-rebuilt channels.** Re-derive with the
  rebuilt vent, movement and sighting channels; assert no removed and no added site and
  recorded total equal to re-derived total including the vent kinds; retire
  `_REPAIRED_SITES`, `_NAMED_UNCLASSIFIED_DIVERGENCES` and the addition allowlist in this
  class. Planted proof: drop the movement channel and the walk diverges at exactly the
  samples/9p2i meetings the movement walk names. **Test change.**

## 5. The recommended path

1. **One test-only card, "rebuild the private channels from the replay walk"** (`tests/`
   only; no `meetings/`, `agents/`, `eval/` or byte change):
   - add a cached helper in `tests/_helpers/committed.py` that yields, per committed
     meeting, the rebuilt vent / movement / sighting mappings and trigger kind;
   - gate it: 676 / 676 byte-exact, with planted failures (drop movement: 68 meetings
     diverge; drop sightings: 31);
   - re-point T5 (exactness), T2 (recorded class as named set), and the T1 census (all legs)
     onto it;
   - correct the false "not recoverable" docstrings (`tests/_helpers/committed.py:161-165`
     and the two mirrors).
   Follow-through it may take, or leave to the owner: the 69-meeting identity pin and its
   "could movement move it" predicate (`tests/meetings/test_contradictions.py:3446-3584`)
   become redundant; retiring them is the retire-means-delete rule.
2. **T3 and T4 edits** as in §4, in the same card or on their own.
3. **Route to the owner, not now:** the 1041 m1 substrate question (§4 T2), batched to the
   next combined re-record by the cadence doctrine, with audit §7.1's per-stay row-3 card
   as its instrument.

Cost: about 9 s of added test wall for the walk (the four sets walk in 7-9 s on this Mac),
$0, no re-record. All five red ids turn green by measurement. The nine-test list shrinks
to the four owned elsewhere (the adjacency-rule instrument test, the report-tick fog viewer
gap, and the two counterfactual-memo tests).

## 6. Side findings

- The latent fail-open behind the 1134 m3 artifact exists in production too:
  `meetings/manager.py:1345-1354` omits participants with no rows, so a meeting where no one
  holds a sighting record would pass `{}` and fall back to the pre-grounding rules
  (`meetings/transcript.py:1836`). Never exercised: 0 of 676 committed meetings had an
  empty mapping (spawn co-presence gives everyone rows). No action proposed.
- The other non-ML red test (`test_the_instrument_and_the_detector_read_one_adjacency_rule`)
  is the same geometry as 1041 m1: adjacent STRONG flags sitting on multi-leg routes near an
  inner boundary (record audit §6.4). It belongs to another investigator; the 1041 m1 case
  is its one recorded instance.
- Scratch hygiene: I first extracted `git archive 39a568c6` into the shared scratchpad's
  existing `b8/` directory before moving to my own `signals/b8tree`. That directory already
  held a `b8.tar` whose replay files match `39a568c6` byte-for-byte, so it was very likely
  the same commit. If another agent uses `scratchpad/b8/` for a different commit, it should
  re-extract.

## 7. Could not establish

- Whether the physical anchor that makes 1041 m1's flag two-carried is itself true at its
  tick (not probed).
- Why the witness spoke the tick one early although the correct t+1 row was in its render
  (would need the rendered prompt, which this investigation does not print).
- The exact re-pinned values the implementer's helper will produce for the T1 census if it
  keeps the ballot-voter roster and omits the trigger kind (my run used the living roster
  and trigger kind, the production arguments, and reproduced the recording exactly).
- Whether the baseline-7 recorded class was also non-empty for the any-strong reading
  (only the kind-sole bar-4 cell, 0/0, is on record).
