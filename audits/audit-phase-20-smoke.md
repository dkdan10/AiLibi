# Audit — Phase 20 smoke record: the live seeds before the record

**Date:** 2026-08-24
**Task:** 20.35 — the smoke record (operator), STOP-and-report, with the abandon branch
**Source state:** `2be19f56` (origin/main), inside the freeze the ratified pre-registration §9
declared at the 20.33 merge (`fc5cf719`). This smoke ran inside the window; it did not open it.
**Instruments, in order:** `scripts/refresh_samples.sh` (real provider) → `scripts/validity_gate.py`
→ `scripts/verify_samples.sh` → `scripts/measure_baseline.py --honesty`.
**Reads against:** `audits/audit-phase-20-preregistration.md` (the ratified bars, the decision rule,
the freeze) and `audits/audit-phase-20-counterfactual.md` (the predicted cells and the abandon
criteria). Where this smoke and a memo disagree, the memo wins and the disagreement is the finding.

## 0. The verdict, in one line

**GO.** Two live 9p2i seeds recorded at the full Phase-20 slate in 16 m 38 s for $0, the validity
gate PASSED on all ten checks, the recorded substrate stamp equals the declared slate on both games,
no opening defaulted, no guard tripped, and both cells the counterfactual memo predicts to reach
exactly zero reached it. None of the five ratified STOP conditions fired.

**Read the GO narrowly.** It says the stack is coherent, not that the record will separate. The
smoke's two games minted **zero `alibi_vs_sighting` flags across five meetings**, so three of the
eight levers — `grounded_prosecution`, `map_aware_arbitration`, `movement_claim_shape` — were never
exercised at all, and the bars that ride that class (4, 5, 7) have no reading here. That is recorded
and carried forward to the record audit under counterfactual §9 item 6, never acted on at this n.

## 1. What this is, and what it is not

The standing cadence rule is smoke before full-record. Phase 20 buys one measurement with roughly
23 h of operator wall across four sets, and this is the cheap proof — a handful of seeds, minutes,
$0 — that the whole stack is live and coherent before the expensive event starts: the lever slate,
the v4 prompt set, the recorder's real worker path, the substrate stamp, the validity gate, and the
honesty instruments reading a freshly recorded set rather than committed bytes.

It is **not** a measurement. No pre-registered bar is declared met or missed on this many seeds, and
this report says so in those words wherever a cell appears. The counterfactual memo already fixed
that rule for the smoke (§9 item 6: a directional bar that merely misses on the smoke seeds is
explicitly NOT an abandon — it is recorded and carried forward, never acted on here). What the smoke
CAN decide is mechanical: does the declared slate reach the recorded bytes, does the gate pass, does
an opening default, does a guard trip, and does a cell predicted to reach exactly zero reach it.

## 2. The recorded configuration

The whole environment was exported in one block before any worker process started; every lever is
read at runner construction, never mid-run. The operator's `FEATHERLESS_API_KEY` is not reproduced
here or anywhere in this record — the recorder prints its 8-character prefix only.

```
AILIBI_LLM_PROVIDER=featherless
AILIBI_PROMPT_SET=qwen3_6_27b
AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B
AILIBI_NUM_PLAYERS=9  AILIBI_NUM_IMPOSTORS=2  AILIBI_TASKS_PER_CREWMATE=2
AILIBI_SAMPLE_DIR=<scratch>/tasks/20.35/smoke/9p2i        # absolute, OUTSIDE the repo
AILIBI_TASK_COMPLETION_FROM_EVENTS=1  AILIBI_SELF_LOCATION_TRAIL=1
AILIBI_MOVEMENT_CLAIM_SHAPE=1         AILIBI_GROUNDED_PROSECUTION=1
AILIBI_MAP_AWARE_ARBITRATION=1        AILIBI_STRUCTURED_TURN_MARKERS=1
AILIBI_MEETING_OUTCOME_MEMORY=1       AILIBI_COALESCED_MEMORY_RENDER=1
```

`AILIBI_MANIFEST` needs no export: it defaults under the sample dir. The sample dir is out of tree
for two verified reasons — a bare `bash scripts/verify_samples.sh` walks EVERY set under the samples
root, so a scratch set parked under `replays/samples/` would silently join the committed gate; and
the per-refresh stage is created under `dirname "$SAMPLE_DIR"`, so an out-of-tree sample dir keeps
the staging out of tree too.

### 2.1 The preflight refuses a slate nobody declared — proven, not asserted

The wrapper's substrate-lever preflight runs on the DRY-RUN path as well as the real one, and it
defaults to the bare slate. Under this phase's exports a bare `--dry-run` therefore exits 1 and names
all eight levers. That is the gate proving it bites, run first and quoted here:

```
Error: the live substrate-lever slate does not match --expect-levers.
       Expected ON: (none — the bare slate: every live toggle OFF)
       Mismatch: task_completion_from_events must be OFF but the live slate reads ON
       (AILIBI_TASK_COMPLETION_FROM_EVENTS); self_location_trail must be OFF ... ;
       movement_claim_shape ... ; grounded_prosecution ... ; map_aware_arbitration ... ;
       structured_turn_markers ... ; meeting_outcome_memory ... ; coalesced_memory_render
       must be OFF but the live slate reads ON (AILIBI_COALESCED_MEMORY_RENDER)
       Export exactly the levers you named and unset every other AILIBI_*
       lever export, then re-run. Nothing was staged.
```

The dry run still wrote nothing. With the slate declared, the same command previews the plan and the
preflight passes:

```
[dry-run] mode: seeds
[dry-run] seeds: 7,12
[dry-run] roster: num_players=9 num_impostors=2 tasks_per_crewmate=2
[dry-run] provider: featherless
[dry-run] meeting model: Qwen/Qwen3.6-27B
[dry-run] prompt set: qwen3_6_27b
[dry-run] substrate flags: expected levers ON = task_completion_from_events,self_location_trail,
          movement_claim_shape,grounded_prosecution,map_aware_arbitration,structured_turn_markers,
          meeting_outcome_memory,coalesced_memory_render; every other live toggle OFF; the
          graduated levers unconditional ON
[dry-run] seed workers: 2 parallel (each records one seed, then pulls the next available seed from
          the queue; Featherless: 2 units per 32B request → 4-unit cap)
[dry-run] seed crash-retry: up to 4 attempt(s) per seed on a transport/crash error (recorded parse
          failures are non-fatal)
[dry-run] no API calls made; no files written.
Substrate slate OK: expected levers ON = <the eight>; every other live toggle OFF; the graduated
levers unconditional ON.
```

The real run's own preflight block, before any seed staged:

```
Using Featherless API key prefix: rc_79456
Locked substrate OK: AILIBI_PROMPT_SET=qwen3_6_27b.
Model-set coupling OK: qwen3_6_27b on Qwen/Qwen3.6-27B.
Model registry OK: Qwen/Qwen3.6-27B is registered in the production client.
Substrate slate OK: expected levers ON = <the eight>; every other live toggle OFF; the graduated
levers unconditional ON.
wrote roster descriptor: <scratch>/tasks/20.35/smoke/9p2i/roster.json
```

## 3. The seed slate, and why these seeds

The slate is a coverage decision, not a convenience one, and this project has already paid for the
lesson: the phase-10 smoke ran 5 seeds green, fired zero emergency meetings, and the full run then
crashed on that uncovered path. The shopping list is the contract's: several `alibi_vs_sighting`
rows, at least one `vent_sighting`, at least one `alibi_conflict`, at least one multi-ejection game,
and a game that ends by task completion rather than ejection — with the counterfactual memo's own
enumerated fixtures drawn from first.

The census below is **re-derived at HEAD from the committed baseline-6 bytes**, not quoted:

a per-seed fold over `replays/samples/9p2i` (the command is in §13, and it also prints the two rows
of the table below):

```
seeds 50 meetings 165 {'vent_sighting': 96, 'alibi_vs_physical': 6,
                       'alibi_vs_sighting': 76, 'alibi_conflict': 8}
alibi_vs_sighting seeds 33
alibi_conflict seeds [12, 21, 28, 31, 40, 47]
reasons {'CREWMATE_EJECT': 31, 'IMPOSTOR_PARITY': 15, 'CREWMATE_TASKS': 4}
seed 7 meetings 4 ejections 2 {'vent_sighting': 2, 'alibi_vs_sighting': 3} CREWMATE_TASKS
seed 12 meetings 2 ejections 1 {'alibi_conflict': 1, 'alibi_vs_sighting': 2} IMPOSTOR_PARITY
```

**The slate is seeds 7 and 12**, and between them they cover the whole list:

| seed | baseline-6 meetings | ejections | vent_sighting | alibi_vs_sighting | alibi_conflict | ended by | why it is on the slate |
|---|---|---|---|---|---|---|---|
| 7 | 4 | 2 | 2 | 3 | 0 | CREWMATE_TASKS | the task-completion ending, a multi-ejection game, vent and sighting flags |
| 12 | 2 | 1 | 0 | 2 | 1 | IMPOSTOR_PARITY | the counterfactual memo's own §5.1 fixture (b) anchor (9p2i seed 12, M0), and one of the six `alibi_conflict` seeds |

Seeds 0–4 were rejected on the contract's own reasoning: they carry 0, 2, 0, 0 and 0
`alibi_vs_sighting` rows, so four of five would exercise the phase's centrepiece lever — grounded
prosecution — zero times.

**Baseline-6 coverage is only a proxy.** The corrected substrate moves trajectories, so the slate is
chosen from it and coverage is then reported as OBSERVED on the smoke bytes (§7), with any lever the
slate never exercised named as untested rather than implied green.

### 3.1 Two seeds, not five — stated plainly

The contract's Definition of done asks for five seeds; this smoke recorded **two**, on the
dispatching orchestrator's re-scope of the task (2026-08-24). The deviation is recorded here rather
than absorbed, and it costs coverage in exactly one place worth naming: fewer games means fewer
chances for the `alibi_vs_sighting` class to appear, and §7 shows it did not appear at all. Every
number in this report is a two-game number and is labelled as one.

## 4. Per-seed outcome

| seed | wall | ticks | meetings | ejections | LLM calls | tokens in / out | cost | winner / reason | `failed_call` rows | recorded flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 7 | 998 s | 30 | 4 | 2 | 42 | 170,687 / 9,221 | $0.0000 | IMPOSTORS / IMPOSTOR_PARITY | 0 | 1 × `vent_sighting` |
| 12 | 352 s | 13 | 1 | 1 | 14 | 44,944 / 3,472 | $0.0000 | IMPOSTORS / IMPOSTOR_PARITY | 0 | none |

Both trajectories moved away from their baseline-6 shapes, which is the expected consequence of a
corrected substrate and the reason §3 calls baseline-6 coverage a proxy: seed 7 ended by impostor
parity rather than task completion, and seed 12 reached one meeting where it had reached two.

The recorder's own summary line, over both seeds:

```
Refresh complete in 16m38s: 2/2 seeds reached a meeting (~100%; authoritative meeting_rate is in
the eval report).
Total spend: $0.0000
... meeting_rate 1.00 (5 meetings) | ejection_accuracy 0.3333 (1/3) | conversion 0.3333 (1/3)
  | lost_openings 0 (defaults 0) | vote_defaults 0 (must_vote 0) | ballot_redirects 0 (eject 0)
```

## 5. The validity gate

`uv run python scripts/validity_gate.py "$SMOKE_DIR" --expected-model Qwen/Qwen3.6-27B
--require-zero-cost`, run under the recorded slate (§12 item 1):

```
Validity gate over <scratch>/tasks/20.35/smoke/9p2i (2 games):
  [PASS] all_games_reach_game_over: 2/2 games reached a reconstructed game_over with a consistent win condition
  [PASS] meeting_rate_and_resolution: meeting_rate 1.0 (floor 0.60); 5 resolved meetings; 0 unresolved
  [PASS] no_duplicate_meeting_rows: 0 duplicate meeting rows over 5 (want 0)
  [PASS] no_tick_1_kills: 0 kills at tick <= 1 (want 0)
  [PASS] no_friendly_fire_kills: 0 impostor-on-impostor kills (want 0)
  [PASS] no_betrayal_ballots_or_accusations: 0 teammate-betrayal ballots/accusations over 28 multi-impostor ballots (want 0)
  [PASS] no_railroaded_crew_ejections: 0 railroaded crew rows over 74 rendered crew suspicions (want 0)
  [PASS] no_dangling_primary_reason_id: 0 dangling primary_reason_id over 28 ballots (want 0)
  [PASS] cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact on 2 games
  [PASS] byte_identical_reconstruction: 0 samples drifted from byte-identical reconstruction (want 0)
Validity gate PASSED (all checks green).
```

The two checks the contract asks to be quoted verbatim are the last two rows above:
`cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact on
2 games` and `byte_identical_reconstruction: 0 samples drifted from byte-identical reconstruction
(want 0)`.

**Reproducibility, as it can actually be proven.** A hosted 27B model is not a deterministic
function of the seed — that is precisely why the engine records the model's responses and replays
from them. So the repeat is the RECONSTRUCTION, not a second spend:
`bash scripts/verify_samples.sh "$SMOKE_DIR"` was run twice and reported `All 2 samples verified
clean.` both times, and the gate's `byte_identical_reconstruction` row is the same property under
the gate's own harness.

## 6. The recorded substrate stamp

Read out of the two `game_over` rows, not out of a live snapshot. Each carries all 22
`SUBSTRATE_FLAG_KEYS`: the thirteen retired levers `True`, the eight Phase-20 levers `True`, and
`impostor_roll_call` `False` — the declared slate exactly, on both games.

```
seed 7  stamp keys=22  eight_ON=True  impostor_roll_call=False  OFF keys=['impostor_roll_call']
seed 12 stamp keys=22  eight_ON=True  impostor_roll_call=False  OFF keys=['impostor_roll_call']
```

The wrapper's preflight read the same slate from the environment before spending, through the one
comparison both recorders and this report use rather than re-deriving:
`orchestrator.replay.substrate_slate_mismatches(<the eight>)` returned `[]`. The MANIFEST `flags`
cell the recorder wrote lists the same 21 ON keys per row, with `impostor_roll_call` absent.
**The two reads agree; there is no disagreement to report as a defect.**

## 7. Lever coverage, OBSERVED on the smoke bytes

Each marker below is discriminating: it counts **0** across all 1,956 recorded prompts and 971 turns
of the committed baseline-6 `replays/samples/9p2i` (the OFF control), so a non-zero count here is the
lever on the live path. Counts are over the smoke's 56 recorded prompts / 28 turns / 5 meetings.

| lever | observed | count | how it was read |
|---|---|---|---|
| `self_location_trail` | **FIRED** | 56/56 prompts | `## Where you were:` and a `Your route (t = tick): …` line in every recorded prompt |
| `meeting_outcome_memory` | **FIRED** | 26 prompts, 794 tagged rows | `## Meetings so far:` block plus `[meeting N]`-tagged testimony frames (seed 7 only — seed 12 held one meeting, so nothing had concluded before it) |
| `coalesced_memory_render` | **FIRED, in part** | 50 prompts | the opening whole-roster summary line (`You saw every other player in CAFETERIA: …`). **The run-folding half is UNTESTED**: zero multi-tick sighting spans were rendered |
| `task_completion_from_events` | **FIRED** | 10 distinct completion rows, 0 fabricated | the registered I-5 cell, `0/10` (baseline-6: 19/458). The rendered completion LINE is byte-identical on both paths, so no marker scan can discriminate this lever — the cell can |
| `structured_turn_markers` | **UNTESTED** | 0 of 28 turns | no meeting guard fired on any of the 28 turns, so the lever had no input to move. I-8 turn contamination reads `0/28`, which is consistent with the lever working AND with nothing having happened; on baseline-6 the OFF path prepended 53 `[invalid accusation target …]` markers over 971 turns |
| `grounded_prosecution` | **UNTESTED** | 0 flags of its class | the smoke minted **zero `alibi_vs_sighting` flags** across five meetings; the lever's entire input class is empty |
| `map_aware_arbitration` | **UNTESTED** | 0 flags of its class | as above — it re-bands `alibi_vs_sighting` and there were none |
| `movement_claim_shape` | **UNTESTED** | I-7 `0/0` | no `alibi_vs_sighting` flag resolvable to a spoken sighting, so the movement-origin cell has no denominator |

Five of eight levers are therefore **named as untested rather than implied green**, and the three of
them that share one cause — an empty `alibi_vs_sighting` class — are the phase's detector centrepiece.
The whole recorded flag census over the smoke is a single row:

```
p-6 witnessed p-7 vent in ADMIN at tick 13; venting is impostor-only, and the spoken observation
matches the witness's own record.
```

That is a grounded `vent_sighting` — a proof-class flag, and one produced by an already-graduated
lever, not by any of the eight.

**Live proof that the v4 set rendered**, read out of a recorded prompt rather than inferred from the
version string (the phrase "one-tick doorways" that reads like the obvious marker lives in the
template's Jinja comment header and never renders, so three RENDERED v4-only strings are used
instead; all three count 0 on the baseline-6 control):

```
<map>
Rooms and doors. Every door below is ONE tick of walking, so two players in rooms that share a door
can be one tick apart:
- ADMIN: EAST_HALL, UPPER_HALL, WEST_HALL
...
## Meetings so far:
- Meeting 1 (tick 11): no ejection (4 skip). 2 impostors remain.

## Where you were:
- Your route (t = tick): CAFETERIA t0 -> EAST_HALL t1 -> ENGINEERING t2-11 -> EAST_HALL t12 -> ADMIN t13
```

`prompt_v4_map_card` 56/56, `prompt_v4_vent_exemption` 25, `prompt_v4_saw_move_shape` 25; the v3-only
sentence `Each flag below is VERIFIED evidence` counts **0** here and 619 on baseline-6. The recorded
`prompt_versions` stamp agrees: `*.qwen3_6_27b.v4` on all four templates, both games.

## 8. The honesty cells on the smoke seeds — DIRECTIONAL ONLY

**No pre-registered bar is declared met or missed on these seeds.** Every row below is a two-game
reading printed beside the counterfactual memo's predicted direction, and nothing in this section
decides anything. Counterfactual §9 item 6 fixes that rule: a directional bar that merely misses on
the smoke seeds is explicitly NOT an abandon — it is recorded here and carried forward to the record
audit.

| cell | baseline-6 samples/9p2i (recorded) | smoke (2 games) | memo's predicted direction | directional reading at this n |
|---|---|---|---|---|
| I-2 false crew self-placement | 152/723 = 21.0% | 0/20 = 0.0% | NOT PREDICTABLE OFFLINE (bar 3) | down; n = 20 claims |
| I-3 sole-flag precision (per victim) | 2/21 | 0/0 — no denominator | ON 1/4 pooled | the class did not occur |
| I-4 grounded sighting side (at tick) | 31/58 = 53.5% | 0/0 — no denominator | ON 10/12 pooled, 1/1 on this set | the class did not occur |
| I-5 fabricated completion lines | 19/458 = 4.1% | **0/10 = 0** | 0 on every set | reaches zero — the §9 tripwire did NOT trip |
| I-6 adjacent-room STRONG share | 38/58 = 65.5% | 0/0 — no denominator | ON 0/1 on this set | the class did not occur |
| I-7 movement-origin flags | 7/76 = 9.2% | 0/0 — no denominator | ON grows, 88/363 pooled | the class did not occur |
| I-8 marker contamination (turns) | 53/971 = 5.5% | **0/28 = 0** | 0/3934 | reaches zero — the second §9 tripwire did NOT trip; coverage is vacuous (§7) |
| I-8 marker contamination (prompts) | 246/1956 = 12.6% | 0/56 = 0.0% | PROMPT-SET-COUPLED, no ON | down |
| I-9 singular-persona prompts | 1956/1956 = 100% | **0/56 = 0.0%** | PROMPT-SET-COUPLED, no ON | the v4 impostor-count parameterisation, live: the prompt now says "2 impostors remain" |
| I-10 meetings with a venting participant | 16/165 = 9.7% | 1/5 = 20% | no bar | up; n = 5 meetings |
| render: rows per snapshot (mean) | 99,959/1,956 = 51.10 | 1,974/56 = 35.25 | ON 40.77 on this set | down, past the predicted value |
| render: reported-testimony retained | 18,319/99,959 = 18.3% | 794/1,974 = 40.2% | ON 47.9% on this set | up sharply, short of the predicted value |

Solvability, for completeness (also two games): killer in the candidate set 5/5; one candidate 0/5;
at most two candidates 1/5; ejected an already-cleared player 1/3.

**The one observation the record audit must carry forward.** The memo predicted the STRONG
`alibi_vs_sighting` class would shrink 234 → 12 pooled on frozen bytes; live, on this slate, the
class did not appear at all across five meetings. Bars 4, 5 and 7 are all read on that class. Two
games cannot establish a rate, but a record whose primary bars land on empty denominators is a
readable outcome the pre-registration should be prepared for, and the SUPPRESSED-NOT-FIXED label
§4.1 registers for the count bars is the language it already has for it. Recorded, not acted on.

## 9. The watch items, scanned by hand

1. **The `(deadline_default)` phantom.** The gate's `cost_and_provenance_exact` has a known blindness
   around the synthetic marker, so the recorded failed-call rows were scanned directly rather than
   trusted to the gate. **Both replays carry zero `failed_call` records of any `error_type`** — there
   is no `deadline_default` row, and therefore no defaulted opening, reply or ballot. The recorder's
   own summary agrees independently: `lost_openings 0 (defaults 0)`, `vote_defaults 0 (must_vote 0)`.
2. **The prompt set actually rendered.** Proven from recorded prompt bytes, not from the version
   string — §7.

## 10. Operating data, and the ~23 h projection re-derived

| measurement | value |
|---|---|
| pool wall (2 workers, 2 seeds) | 998 s = 16 m 38 s |
| per-seed wall | seed 7 998 s; seed 12 352 s; mean 675 s |
| worker occupancy | 1,350 busy worker-seconds of 1,996 available = **67.6%** (worker 2 idled 646 s after finishing the shorter seed — a two-seed artifact, not a pool defect: with 200 seeds queued the pool stays saturated until the tail) |
| LLM calls | 56 (42 + 14), all `call_kind=meeting` |
| tokens | 215,631 in + 12,693 out = 228,324; **mean 4,077 per call** |
| tokens per meeting | mean 45,665; range 28,880 (seed 7 M3, 6 calls) to 59,402 (seed 7 M0, 16 calls) |
| throughput | **169.1 tokens per worker-second** (338.2 aggregate at 2 workers) |
| retries / transport blips absorbed | **0** — no `WARN … retrying` line in the run log, no attempt beyond the first for either seed |
| cost | $0.0000 (flat-rate provider; every per-call `cost_usd` row is 0.0) |

**The projection, two ways, both from measured tokens.** The record is 300 games: `samples/9p2i` 50,
`ml_corpus/9p2i` 150, `samples/4p1i` 50, `ml_corpus/4p1i` 50.

* **At the smoke's own game lengths** (114,162 tokens per 9p2i game) and the committed 4p1i:9p2i
  tokens-per-game ratio of 0.066: 23.6 M tokens ÷ 338.2 tokens/s = **19.4 h**.
* **At baseline-6 game lengths** — the honest upper bound, because both smoke games ended early by
  impostor parity while baseline-6 averages 176,267 tokens per `samples/9p2i` game: 34.9 M tokens
  ÷ 338.2 tokens/s = **28.6 h**.

The review's "~23 h operator wall, $0 flat-rate" sits inside that bracket. **The projection holds;
no re-plan is required**, and the record's own checkpoint-per-seed-range push is what covers the
spread. The lever that moves the estimate most is worker count, which is capped by the provider's
concurrency (2 units per 32B request against a 4-unit cap), not by the recorder.

## 11. The verdict, against the ratified abandon criteria

The criteria are `audits/audit-phase-20-counterfactual.md` §9, quoted verbatim; nothing is invented
here. Each is a mechanical check, and each is answered from the evidence above.

| # | criterion, verbatim | reading |
|---|---|---|
| 1 | "A `scripts/validity_gate.py` FAIL on any leg. STOP." | **NOT MET** — PASSED, all ten checks green (§5) |
| 2 | "A seed whose opening defaults — the `(deadline_default)` watch item on the opening turn. STOP." | **NOT MET** — zero `failed_call` rows of any kind in either replay (§9) |
| 3 | "A substrate stamp that does not equal the intended slate… a non-empty result STOPS the record" | **NOT MET** — `substrate_slate_mismatches` returned `[]`, and both recorded stamps carry the eight True with `impostor_roll_call` False (§6) |
| 4 | "A guard trip — any firewall or leak guard raising during the run. STOP." | **NOT MET** — the run exited 0 with no guard exception, and the gate's guard rows (friendly fire, betrayal ballots, railroaded ejections, dangling reason ids, tick-1 kills) are all 0 |
| 5 | "a cell this memo predicts to reach exactly 0 that is non-zero on the smoke seeds is an ABANDON at any n" | **NOT MET** — the two such cells are I-5 fabricated completion lines (`0/10`) and I-8 marker contamination in turns (`0/28`); both read zero (§8) |
| 6 | "NOT an abandon, explicitly: a directional bar that merely misses on five smoke seeds." | applied — every §8 row is recorded and carried forward, none acted on |
| 7 | "Also NOT an abandon: bars 5 and 7 missing at the record." | not reached — neither bar has a reading on these seeds |

**GO.** No STOP condition fired, so the recording window may open and the adopting record may start
on frozen source. The go/no-go is the owner's; this report stops here, and 20.36 is a separate
contract.

Because this is a GO, the ABANDON branch has nothing to state: there is no defect to describe, no
seed to name, no reproduction to write, and no follow-up contract to route. The one thing that DOES
travel forward is §8's carried observation about the empty `alibi_vs_sighting` class — an
expectation for the record audit, not a defect and not a routing slot.



## 12. Operating notes the record must carry

1. **The gate and the instruments must run under the recorded slate.**
   `api/replay_loader.py::_assert_substrate_matches` refuses a cross-substrate reconstruction, so
   `validity_gate.py`, `verify_samples.sh` and `measure_baseline.py` pointed at these bytes must run
   in a shell carrying the same eight `AILIBI_*` exports; the bare committed-set gate must run
   without them. Both were run that way here. This is the mechanism the pre-registration §6 already
   names when it explains why no subset of levers may graduate — it is not new, but an operator who
   drops the exports between the record and the gate will read a refusal, not a result.
2. **`--expect-levers` is required on the dry run too.** Since Task 20.33 the preflight runs on the
   preview path, so a bare `--dry-run` under a phase-20 shell exits 1. That is the guard working.

## 13. Reproduction

```bash
# the environment block of §2, exported first, then:
bash scripts/refresh_samples.sh --seeds 7,12 --expect-levers \
  task_completion_from_events,self_location_trail,movement_claim_shape,grounded_prosecution,\
map_aware_arbitration,structured_turn_markers,meeting_outcome_memory,coalesced_memory_render \
  --dry-run                      # preview; writes nothing
bash scripts/refresh_samples.sh --seeds 7,12 --expect-levers <the same eight>   # the record

# gate, then measure, in that order — under the same exports
uv run python scripts/validity_gate.py "$AILIBI_SAMPLE_DIR" \
  --expected-model Qwen/Qwen3.6-27B --require-zero-cost
bash scripts/verify_samples.sh "$AILIBI_SAMPLE_DIR"
uv run python scripts/measure_baseline.py --honesty "$AILIBI_SAMPLE_DIR"

# the committed sets, in a shell with NO lever exports
bash scripts/verify_samples.sh
git status --porcelain replays/
```

The §3 census, re-derived from the committed bytes rather than quoted:

```bash
uv run python - <<'PY'
import collections, json, pathlib
rows, kinds = [], collections.Counter()
for p in sorted(pathlib.Path("replays/samples/9p2i").glob("replay-seed-*.jsonl"),
                key=lambda q: int(q.stem.split("-")[-1])):
    meetings = ejections = 0
    per = collections.Counter()
    reason = None
    for line in p.open():
        d = json.loads(line)
        if "ballots" in d:
            meetings += 1
            ejections += bool(d.get("ejected_player_id"))
            for c in d.get("contradictions") or []:
                per[c["kind"]] += 1
                kinds[c["kind"]] += 1
        reason = d.get("reason", reason)
    rows.append((int(p.stem.split("-")[-1]), meetings, ejections, per, reason))
print("seeds", len(rows), "meetings", sum(r[1] for r in rows), dict(kinds))
print("alibi_vs_sighting seeds", sum(1 for r in rows if r[3]["alibi_vs_sighting"]))
print("alibi_conflict seeds", [r[0] for r in rows if r[3]["alibi_conflict"]])
print("reasons", dict(collections.Counter(r[4] for r in rows)))
for r in rows:
    if r[0] in (7, 12):
        print("seed", r[0], "meetings", r[1], "ejections", r[2], dict(r[3]), r[4])
PY
```
