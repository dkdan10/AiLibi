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

**ABANDON. The adopting record does not start.**

Five live 9p2i seeds recorded at the full Phase-20 slate for $0. The recording half is clean: the
validity gate PASSED on all ten checks, the substrate stamp equals the declared slate on all five
games, no opening defaulted, no guard tripped during the run, and the recorder absorbed no retry.
**The measuring half is not.** `scripts/measure_baseline.py --honesty` — the phase's primary
instrument, the one that computes the cells every ratified bar is read on — **raises and folds
nothing** over these bytes:

```
eval.evidence_honesty.EvidenceHonestyReconstructionError: headless-seed-13: meeting at tick 8
carries an alibi_vs_sighting flag whose events
'turn:headless-seed-13:meeting-0:turn-4:obs:1' / 'turn:headless-seed-13:meeting-0:turn-6:claim:0'
do not resolve to one spoken sighting and one alibi — the flag would vanish from I-4, I-6 and I-7
while still counting in the I-3 class census
```

**A record whose primary instrument cannot read its bytes must not be spent.** The defect, its
mechanism, its blast radius and its routing slot are §11. §12 states the criterion this was ruled
against, and states plainly that no §9 criterion names this class verbatim — the report invents
none.

## 1. What this is, and what it is not

The standing cadence rule is smoke before full-record. Phase 20 buys one measurement with roughly
23 h of operator wall across four sets, and this is the cheap proof — five seeds, 44 minutes, $0 —
that the whole stack is live and coherent before the expensive event starts: the lever slate, the v4
prompt set, the recorder's real worker path, the substrate stamp, the validity gate, and the honesty
instruments reading a freshly recorded set rather than committed bytes. **The last clause is the one
that failed, and it is the one no cheaper instrument could have tested.**

It is **not** a measurement. No pre-registered bar is declared met or missed on five seeds, and this
report says so in those words wherever a cell appears. The counterfactual memo already fixed that
rule for the smoke (§9 item 6: a directional bar that merely misses on five smoke seeds is
explicitly NOT an abandon — it is recorded and carried forward, never acted on here).

## 2. The recorded configuration

The whole environment was exported in one block before any worker process started; every lever is
read at runner construction, never mid-run. The operator's `FEATHERLESS_API_KEY` is not reproduced
here or anywhere in this record.

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
Using Featherless API key prefix: <redacted — the recorder prints 8 characters; this record keeps none>
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

The census is re-derived at HEAD from the committed baseline-6 bytes, not quoted (the command is in
§14):

```
seeds 50 meetings 165 {'vent_sighting': 96, 'alibi_vs_physical': 6,
                       'alibi_vs_sighting': 76, 'alibi_conflict': 8}
alibi_vs_sighting seeds 33
alibi_conflict seeds [12, 21, 28, 31, 40, 47]
reasons {'CREWMATE_EJECT': 31, 'IMPOSTOR_PARITY': 15, 'CREWMATE_TASKS': 4}
```

**The slate is seeds 7, 12, 13, 31 and 40.**

| seed | baseline-6 meetings | ejections | vent_sighting | alibi_vs_sighting | alibi_conflict | ended by | why it is on the slate |
|---|---|---|---|---|---|---|---|
| 7 | 4 | 2 | 2 | 3 | 0 | CREWMATE_TASKS | the task-completion ending, a multi-ejection game |
| 12 | 2 | 1 | 0 | 2 | 1 | IMPOSTOR_PARITY | the counterfactual memo's own §5.1 fixture (b) anchor (9p2i seed 12, M0) |
| 13 | 3 | 2 | 1 | **8** | 0 | IMPOSTOR_PARITY | one of the two `alibi_vs_sighting`-densest baseline-6 games |
| 31 | 5 | 3 | 3 | **8** | 1 | IMPOSTOR_PARITY | the other densest game, and a 5-meeting / 3-ejection game |
| 40 | 3 | 2 | 0 | 4 | **3** | IMPOSTOR_PARITY | the `alibi_conflict`-densest game |

Seeds 0–4 were rejected on the contract's own reasoning: they carry 0, 2, 0, 0 and 0
`alibi_vs_sighting` rows, so four of five would exercise the phase's centrepiece lever — grounded
prosecution — zero times.

**Baseline-6 coverage is only a proxy.** The corrected substrate moves trajectories, so the slate is
chosen from it and coverage is then reported as OBSERVED on the smoke bytes (§8).

### 3.1 The slate was recorded in two batches, and why

Seeds 7 and 12 were recorded first (16 m 38 s), and seeds 13, 31 and 40 followed (27 m 26 s) after
an automated review of this PR pointed out — correctly — that a five-seed smoke is required by BOTH
committed sources of truth: the task contract's Definition of done, and the ratified pre-registration
§9 ("Smoke (20.35): 5 seeds of 9p2i into a scratch directory"). The three added seeds were chosen to
attack the gap the two-seed set exposed: its games minted **zero** `alibi_vs_sighting` flags, so the
detector levers had no input at all. They did their job — the five-seed set carries six flags of that
class, and two of them are the ones that broke the instrument. **Every number in this report is a
five-game number, re-derived on the whole set; nothing is carried over from the two-seed pass.**

## 4. Per-seed outcome

| seed | wall | ticks | meetings | ejections | LLM calls | tokens in / out | cost | winner / reason | `failed_call` rows | recorded flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 7 | 998 s | 30 | 4 | 2 | 42 | 170,687 / 9,221 | $0.0000 | IMPOSTORS / IMPOSTOR_PARITY | 0 | 1 `vent_sighting` |
| 12 | 352 s | 13 | 1 | 1 | 14 | 44,944 / 3,472 | $0.0000 | IMPOSTORS / IMPOSTOR_PARITY | 0 | none |
| 13 | 872 s | 31 | 4 | 2 | 40 | 167,533 / 9,542 | $0.0000 | IMPOSTORS / IMPOSTOR_PARITY | 0 | 2 `alibi_vs_sighting`, 1 `alibi_conflict`, 1 `vent_sighting` |
| 31 | 808 s | 21 | 3 | 2 | 36 | 137,080 / 7,905 | $0.0000 | CREWMATES / CREWMATE_EJECT | 0 | 2 `vent_sighting` |
| 40 | 837 s | 16 | 3 | 2 | 38 | 153,925 / 7,673 | $0.0000 | CREWMATES / CREWMATE_EJECT | 0 | 4 `alibi_vs_sighting`, 3 `alibi_conflict`, 1 `vent_sighting` |

Totals: 15 meetings, 9 ejections, 170 LLM calls, 674,169 in / 37,813 out = 711,982 tokens, $0.0000.
Flag census: 6 `alibi_vs_sighting`, 5 `vent_sighting`, 4 `alibi_conflict`.

Trajectories moved away from their baseline-6 shapes, which is the expected consequence of a
corrected substrate and the reason §3 calls baseline-6 coverage a proxy — seed 7 ended by impostor
parity rather than task completion, and seed 31 by crew ejection rather than parity.

## 5. The validity gate — PASSED

`uv run python scripts/validity_gate.py "$SMOKE_DIR" --expected-model Qwen/Qwen3.6-27B
--require-zero-cost`, run under the recorded slate (§13 item 1):

```
Validity gate over <scratch>/tasks/20.35/smoke/9p2i (5 games):
  [PASS] all_games_reach_game_over: 5/5 games reached a reconstructed game_over with a consistent win condition
  [PASS] meeting_rate_and_resolution: meeting_rate 1.0 (floor 0.60); 15 resolved meetings; 0 unresolved
  [PASS] no_duplicate_meeting_rows: 0 duplicate meeting rows over 15 (want 0)
  [PASS] no_tick_1_kills: 0 kills at tick <= 1 (want 0)
  [PASS] no_friendly_fire_kills: 0 impostor-on-impostor kills (want 0)
  [PASS] no_betrayal_ballots_or_accusations: 0 teammate-betrayal ballots/accusations over 85 multi-impostor ballots (want 0)
  [PASS] no_railroaded_crew_ejections: 0 railroaded crew rows over 280 rendered crew suspicions (want 0)
  [PASS] no_dangling_primary_reason_id: 0 dangling primary_reason_id over 85 ballots (want 0)
  [PASS] cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact on 5 games
  [PASS] byte_identical_reconstruction: 0 samples drifted from byte-identical reconstruction (want 0)
Validity gate PASSED (all checks green).
```

The two checks the contract asks to be quoted verbatim are the last two rows above:
`cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact on
5 games` and `byte_identical_reconstruction: 0 samples drifted from byte-identical reconstruction
(want 0)`.

**That the gate passes while the instrument raises is itself the finding.** The gate checks the
recording; it does not fold the flag class. A record can be perfectly valid and still be unmeasurable.

**Reproducibility, as it can actually be proven.** A hosted 27B model is not a deterministic function
of the seed — that is precisely why the engine records the model's responses and replays from them.
So the repeat is the RECONSTRUCTION, not a second spend: `bash scripts/verify_samples.sh "$SMOKE_DIR"`
was run twice and reported `All 5 samples verified clean.` both times.

## 6. The recorded substrate stamp

Read out of the five `game_over` rows, not out of a live snapshot. Each carries all 22
`SUBSTRATE_FLAG_KEYS`: the thirteen retired levers `True`, the eight Phase-20 levers `True`, and
`impostor_roll_call` `False` — the declared slate exactly, on every game.

```
seeds 7, 12, 13, 31, 40 — stamp keys=22  eight_ON=True  OFF keys=['impostor_roll_call']
```

The wrapper's preflight read the same slate from the environment before spending, through the one
comparison both recorders and this report use rather than re-deriving:
`orchestrator.replay.substrate_slate_mismatches(<the eight>)` returned `[]`. The MANIFEST `flags`
cell lists the same 21 ON keys on every row, with `impostor_roll_call` absent.
**The two reads agree; there is no stamp disagreement to report.**

## 7. The prompt set that rendered

Proven from recorded prompt bytes, not inferred from the version string. The phrase "one-tick
doorways" that reads like the obvious marker lives inside the template's Jinja comment header and
never renders, so three RENDERED v4-only strings are used instead — each counts **0** across all
1,956 committed baseline-6 prompts (the OFF control) and non-zero here.

| marker | smoke (170 prompts) | baseline-6 (1,956 prompts) |
|---|---|---|
| the `<map>` card's own sentence | 170 | 0 |
| the vent-first exemption clause | 75 | 0 |
| the `saw_move` observation shape | **75** | **0** |
| v3's `Each flag below is VERIFIED evidence` | 0 | 619 |

The recorded `prompt_versions` stamp agrees: `*.qwen3_6_27b.v4` on all four templates, all five games.
**The third row is the one that matters for §11**: the v4 set is what first tells an agent it may
speak `{"type": "saw_move", …}`, and 75 of the 170 recorded prompts carry that instruction.

## 8. Lever coverage, OBSERVED on the smoke bytes

Every RENDER marker below is discriminating: it counts **0** across all 1,956 recorded prompts and
971 turns of the committed baseline-6 `replays/samples/9p2i` (the OFF control), so a non-zero count
here is the lever on the live path. Counts are over the smoke's 170 prompts / 85 turns / 15 meetings.

| lever | observed | count | how it was read |
|---|---|---|---|
| `self_location_trail` | **FIRED** | 170/170 prompts | `## Where you were:` and a `Your route (t = tick): …` line in every recorded prompt |
| `meeting_outcome_memory` | **FIRED** | 98 prompts, 2,542 tagged rows | the `## Meetings so far:` block plus `[meeting N]`-tagged testimony frames |
| `movement_claim_shape` | **FIRED** | 2 flags | two `alibi_vs_sighting` flags whose sighting side is a spoken `saw_move` — a shape that exists only because this lever reads a spoken movement report as a placement. **These are the two flags that break the instrument (§11)** |
| `map_aware_arbitration` | **FIRED** | 4 flags re-banded | the `adjacent room one tick away` weak reason on 4 recorded flag descriptions |
| `coalesced_memory_render` | **FIRED, in part** | 156 prompts | the opening whole-roster summary line (`You saw every other player in …`). **The run-folding half is UNTESTED**: zero multi-tick sighting spans were rendered |
| `grounded_prosecution` | **UNTESTED** | 0 | neither of its two bands (`ungrounded sighting`, `single grounded source`) appears on any recorded flag; the six flags of its class were all banded by other rules |
| `structured_turn_markers` | **UNTESTED** | 0 of 85 turns | no meeting guard fired on any of the 85 turns, so the lever had no input to move. On baseline-6 the OFF path prepended 53 `[invalid accusation target …]` markers over 971 turns |
| `task_completion_from_events` | **UNMEASURABLE** | — | its registered cell is I-5, and the instrument that computes I-5 raises before emitting anything (§11). 130 completion lines rendered, but the rendered LINE is byte-identical on both paths, so no marker scan can discriminate the lever |

**Four levers fired, one half-fired, two are untested, and one is unmeasurable.** The recorded
weak-signal bands over the whole set: `endpoint-tick sighting` 6, `self-stated alibi pair` 4,
`narrow alibi window` 4, `endpoint-tick overlap` 4, `adjacent room one tick away` 4.

## 9. The honesty cells — NOT COMPUTED

**No pre-registered bar is declared met or missed on these seeds.** The point is stronger here than
the usual caution: the cells **do not exist**. `scripts/measure_baseline.py --honesty "$SMOKE_DIR"`
exits 1 with the reconstruction error quoted in §0 and emits no report at all, so I-2, I-3, I-4, I-5,
I-6, I-7, I-8, I-9, I-10, I-11 and the render census have no value on this set.

The one instrument that does run is the solvability ceiling, which reads the engine's kill and
visibility record and the recorded ballots rather than the flag class:

```
Solvability ceiling over <scratch>/tasks/20.35/smoke/9p2i (5 games, 15 body meetings, 9 ejections):
  killer in candidate set: 0.9333  (14/15)
  one candidate: 0.0  (0/15)
  at most two candidates: 0.2  (3/15)   ... containing the killer: 1.0 (3/3)
  ejected a player the crew had already cleared: 0.2222  (2/9)
  killer in candidate set, last-kill anchor: 1.0  (15/15)
```

Directional only at n = 5, against baseline-6 `samples/9p2i` (containment 544/626 pooled at the
corpus level; this set's own cells are in the committed 20.15 pins). Nothing here decides anything.

## 10. Operating data, and the ~23 h projection re-derived

| measurement | value |
|---|---|
| operator wall, both batches | 998 s + 1,646 s = **2,644 s = 44 m 04 s** |
| per-seed wall | 7 → 998 s; 12 → 352 s; 13 → 872 s; 31 → 808 s; 40 → 837 s; **mean 773 s** |
| worker occupancy | 3,867 busy worker-seconds of 5,288 available = **73.1%** (the idle is the two tails; with 200 seeds queued the pool stays saturated until the last round) |
| LLM calls | 170, all `call_kind=meeting` |
| tokens | 674,169 in + 37,813 out = 711,982; **mean 4,188 per call** |
| tokens per meeting | mean **47,465** over 15 meetings |
| throughput | **184.1 tokens per worker-second** (368.2 aggregate at 2 workers) |
| retries / transport blips absorbed | **0** — no `WARN … retrying` line in either run log, no attempt beyond the first for any seed |
| cost | $0.0000 (flat-rate provider; every per-call `cost_usd` row is 0.0) |

**The projection, two ways, both from measured tokens.** The record is 300 games: `samples/9p2i` 50,
`ml_corpus/9p2i` 150, `samples/4p1i` 50, `ml_corpus/4p1i` 50.

* **At the smoke's own game lengths** (142,396 tokens per 9p2i game) with the committed 4p1i:9p2i
  tokens-per-game ratio of 0.066: 29.4 M tokens ÷ 368.2 tokens/s = **22.2 h**.
* **At baseline-6 game lengths** (176,267 tokens per `samples/9p2i` game): 34.9 M tokens ÷ 368.2
  tokens/s = **26.3 h**.

The review's "~23 h operator wall, $0 flat-rate" is confirmed by measurement rather than assumed: the
smoke's own lengths put it at 22.2 h. **No re-plan of the wall clock is required** — what is required
is the §11 fix before any of it is spent. The lever that moves the estimate most is worker count,
capped by the provider's concurrency (2 units per 32B request against a 4-unit cap), not by the
recorder.

## 11. THE DEFECT — symptom, seed, suspected file, reproduction, routing

**Symptom.** `uv run python scripts/measure_baseline.py --honesty "$SMOKE_DIR"` exits 1 with
`eval.evidence_honesty.EvidenceHonestyReconstructionError`, raised at `eval/evidence_honesty.py:2043`
inside `_fold_flags`. No cell is emitted — the fold aborts on the first offending flag, so the whole
five-game set is unmeasurable, not partially measurable.

**Seeds and meetings.** Two flags, in two different games, both at their game's first meeting:

| seed | meeting | tick | flag events | sighting-side type |
|---|---|---|---|---|
| 13 | `headless-seed-13:meeting-0` | 8 | `turn-4:obs:1` / `turn-6:claim:0` | `saw_move` |
| 40 | `headless-seed-40:meeting-0` | 8 | `turn-3:obs:2` / `turn-5:claim:0` | `saw_move` |

Of the six `alibi_vs_sighting` flags the smoke recorded, **four resolve (`alibi` + `saw_player`) and
two do not (`alibi` + `saw_move`)**.

**Suspected file, and the mechanism.** `eval/evidence_honesty.py::_resolve_flag` (:2083-2131) reads
the flag's two event ids and requires **exactly one** side to be a `SawPlayerObservation`:

```python
sightings = [
    (speaker, artifact)
    for event_id, (speaker, artifact) in sides
    if isinstance(artifact, SawPlayerObservation)
    and ":whereabouts:" not in event_id
]
...
if len(sightings) != 1 or len(alibis) != 1:
    return None
```

A spoken `{"type": "saw_move", "subject": …, "from_room": …, "to_room": …, "tick": …}` is a
different artifact type, so `sightings` is empty, `_resolve_flag` returns `None`, and `_fold_flags`
raises by design — its guard exists precisely so an unresolvable flag cannot silently vanish from
I-4/I-6/I-7 while still counting in the I-3 class census. **The guard is correct. What is missing is
the resolver's knowledge of the movement-report side.** The flag itself is well-formed; its recorded
description reads

```
Alibi places p-9 in LABS (ticks 3-8); sighting reports p-9 in MEDBAY at tick 8.
[weak signal: endpoint-tick sighting; adjacent room one tick away]
```

— the detector read the movement's DESTINATION as the placement, which is exactly what
`movement_claim_shape` (Task 20.23) is specified to do.

**Why no offline instrument could have caught this, and why the smoke is where it had to surface.**
The spoken `saw_move` observation shape is **new in the v4 prompt set** (Task 20.31): the v3 templates
never told an agent it could speak a movement, so no committed baseline-6 transcript contains one
(§7: 0 of 1,956 v3-era prompts carry the shape; 75 of 170 v4 prompts do). The 20.34 offline
counterfactual re-runs the ON detector over the RECORDED spoken inputs — which are all v3-era — so
its ON leg could never mint a `saw_move`-sided flag and never exercised this path. **The
prompt-set bump and the detector lever only meet in a live recording.** That is the whole argument
for a smoke, and it is the argument this smoke just proved.

**Reproduction, exact.**

```bash
# the §2 environment block, then:
bash scripts/refresh_samples.sh --seeds 13 --expect-levers <the eight>
uv run python scripts/measure_baseline.py --honesty "$AILIBI_SAMPLE_DIR"   # exits 1
```

A cheaper deterministic reproduction for the follow-up's test: hand-build a meeting whose
`alibi_vs_sighting` flag names a `saw_move` observation on one side and an `alibi` claim on the
other, and assert `_resolve_flag` returns a resolved flag rather than `None`. The five recorded
replays in the scratch set are the live fixture.

**Blast radius.** Every bar read on the flag class — bars 4 (I-3), 5 (I-4), 7 (I-6) — plus the
secondary I-7 movement-origin cell, and, because the fold aborts wholesale, **every other honesty
cell too**: I-2 (bar 3), I-5 (bar 6), I-8, I-9, I-10, I-11 and the render census. Bars 1 and 2 read
`eval/deduction`, which is a separate instrument and unaffected. Note the ugly corollary: I-5 and
I-8 are the two cells the counterfactual §9 item 5 names as ABANDON tripwires, and **neither can be
evaluated**, so the tripwire itself is inoperable on these bytes.

**The routing slot for the owner to land.** One `eval/` follow-up contract, before the record:

* teach `eval/evidence_honesty.py::_resolve_flag` the movement-report sighting side — resolve a
  spoken `saw_move` to the placement the detector actually used (the destination room at that tick),
  so I-4's grounding, I-6's geometry and I-7's movement-origin cell all read the same side the flag
  was minted from;
* ship it with a planted case proving the gate still bites for a genuinely unresolvable pair, per
  AGENTS.md craft rule 2, and with a fixture built from the two recorded meetings above;
* re-check whether the same blindness reaches `scripts/counterfactual_phase20.py`'s ON leg — it
  shares `_fold_flags`, and it will meet a `saw_move` side the moment its inputs are v4 bytes;
* then the smoke runs again. **The contract's rule is that a routed fix reopens the window and the
  smoke re-runs from zero with every number re-derived.** One observation for the owner, offered
  rather than decided: this fix lands in `eval/`, which is outside the frozen trees (`agents/`,
  `meetings/`, `observation/`, `orchestrator/`, the prompt set), and it changes no recorded byte —
  so the five replays in the scratch set could in principle be re-MEASURED rather than re-RECORDED.
  Whether that satisfies "from zero" is the owner's call, not this report's.

**The adopting record does not start.**

## 12. The verdict, against the ratified abandon criteria

The criteria are `audits/audit-phase-20-counterfactual.md` §9, quoted verbatim; nothing is invented
here.

| # | criterion, verbatim | reading |
|---|---|---|
| 1 | "A `scripts/validity_gate.py` FAIL on any leg. STOP." | **NOT MET** — PASSED, all ten checks green (§5) |
| 2 | "A seed whose opening defaults — the `(deadline_default)` watch item on the opening turn. STOP." | **NOT MET** — zero `failed_call` rows of any `error_type` in all five replays; the recorder's own summary reads `lost_openings 0 (defaults 0)` and `vote_defaults 0 (must_vote 0)` |
| 3 | "A substrate stamp that does not equal the intended slate… a non-empty result STOPS the record" | **NOT MET** — `substrate_slate_mismatches` returned `[]`, and all five recorded stamps carry the eight True with `impostor_roll_call` False (§6) |
| 4 | "A guard trip — any firewall or leak guard raising during the run. STOP." | **NOT MET as written** — no firewall or leak guard raised during the run. A guard DID raise, but it is an instrument guard raising during MEASUREMENT (§11), which this criterion's wording does not reach |
| 5 | "a cell this memo predicts to reach exactly 0 that is non-zero on the smoke seeds is an ABANDON at any n" | **CANNOT BE EVALUATED** — the two cells it names (I-5 fabricated completion lines, I-8 marker contamination in turns) are not computed at all, because the instrument that computes them raises first |
| 6 | "NOT an abandon, explicitly: a directional bar that merely misses on five smoke seeds." | applied — and it does not reach this case: no bar MISSED here, no bar has a value |
| 7 | "Also NOT an abandon: bars 5 and 7 missing at the record." | not reached |

**No §9 criterion names this class verbatim, and this report invents none.** What it applies instead
is the task contract's own Verification checklist — *"a Measurement that cannot be run is reported
under `## Questions`, never asserted"* — and the contract's framing of the fork: GO means the record
starts; **ABANDON means the defect is described concretely enough to author a follow-up contract, the
routing is named, and the record does not start.** All three hold, so the verdict is recorded as
**ABANDON**.

The stronger statement, for the owner: criterion 5 is not merely unmet, it is **inoperable** on these
bytes. A record taken now would spend ~22 h to produce a set whose ratified tripwire cannot fire and
whose primary bars have no reading. **The go/no-go on restarting is the owner's**; this report stops
here.

## 13. Operating notes the record must carry

1. **The gate and the instruments must run under the recorded slate.**
   `api/replay_loader.py::_assert_substrate_matches` refuses a cross-substrate reconstruction, so
   `validity_gate.py`, `verify_samples.sh` and `measure_baseline.py` pointed at these bytes must run
   in a shell carrying the same eight `AILIBI_*` exports; the bare committed-set gate must run
   without them. Both were run that way here. This is the mechanism the pre-registration §6 already
   names when it explains why no subset of levers may graduate — not new, but an operator who drops
   the exports between the record and the gate will read a refusal, not a result.
2. **`--expect-levers` is required on the dry run too.** Since Task 20.33 the preflight runs on the
   preview path, so a bare `--dry-run` under a Phase-20 shell exits 1. That is the guard working.
3. **The validity gate is not a measurement gate.** It passed cleanly on a set the honesty instrument
   cannot fold. Any future record protocol should run the honesty instrument on the FIRST completed
   seed, not after the whole set — the smoke is what caught this at 44 minutes instead of 22 hours,
   and a per-seed instrument check would catch it at 15.

## 14. Reproduction

```bash
# the environment block of §2, exported first, then:
bash scripts/refresh_samples.sh --seeds 7,12 --expect-levers \
  task_completion_from_events,self_location_trail,movement_claim_shape,grounded_prosecution,\
map_aware_arbitration,structured_turn_markers,meeting_outcome_memory,coalesced_memory_render \
  --dry-run                      # preview; writes nothing
bash scripts/refresh_samples.sh --seeds 7,12 --expect-levers <the same eight>
bash scripts/refresh_samples.sh --seeds 13,31,40 --expect-levers <the same eight>

# gate, then measure, in that order — under the same exports
uv run python scripts/validity_gate.py "$AILIBI_SAMPLE_DIR" \
  --expected-model Qwen/Qwen3.6-27B --require-zero-cost      # PASS
bash scripts/verify_samples.sh "$AILIBI_SAMPLE_DIR"          # clean, twice
uv run python scripts/measure_baseline.py --honesty "$AILIBI_SAMPLE_DIR"      # EXITS 1 — §11
uv run python scripts/measure_baseline.py --solvability "$AILIBI_SAMPLE_DIR"  # runs

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
PY
```

## §14 — Post-fix re-measure and the restart ruling (addendum, 2026-08-25)

Task 20.43 (PR #387, merged acf71f14) landed the movement-sided resolver arm and the
instrument-side flag dedup this report's §11 routed. Per that contract's Step 5, the
orchestrator ran the re-measure on the PRESERVED smoke bytes (the same five replays this
report recorded; no re-record, no new spend), at origin/main 28599ec3, with the eight
Phase-20 lever exports matching the recorded slate:

`uv run python scripts/measure_baseline.py --honesty <preserved smoke dir>` — exit 0:

```
Evidence-honesty instruments over /private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/tasks/20.35/smoke/9p2i (5 games, 15 meetings; +1 agent clock proved on 252 discriminating sightings):
  I-2 false crew self-placement: 0.0  (0/63)  95% CI [0.0, 0.0575]  (rare count — read the interval)
    ... agent-frame reading: 0.0  (0/63)  95% CI [0.0, 0.0575]  (rare count — read the interval)
    ... impostor claims: 0.0  (0/13)  95% CI [0.0, 0.2281]  (rare count — read the interval)
    ... copyable from a rendered self-location line: 0.0952  (6/63)  95% CI [0.0444, 0.1926]  (rare count — read the interval)
  I-3 sole-flag precision (per victim): None  (0/0)  95% CI undefined  (rare count — read the interval)
    ... per meeting: crewmates ejected: None  (0/0)  95% CI undefined  (rare count — read the interval)  [0 sole-flag meetings]
    ... class impostor share: None  (0/0)  95% CI undefined  (rare count — read the interval)
    ... living-voter base rate: None  (0/0)  95% CI undefined  (rare count — read the interval)
  I-4 grounded sighting side (+-0): None  (0/0)  95% CI undefined  (rare count — read the interval)
    ... (+-1): None  (0/0)  95% CI undefined  (rare count — read the interval)
    ... (+-2): None  (0/0)  95% CI undefined  (rare count — read the interval)  [0 of 0 sides unresolvable]
  I-5 fabricated completion lines: 0.0  (0/32)  95% CI [0.0, 0.1072]  (rare count — read the interval)  [+1 render offset 32/32; 0 games hit]
  I-6 adjacent-room STRONG share: None  (0/0)  95% CI undefined  (rare count — read the interval)  [distance 2: 0; >=3: 0; single-tick window: 0]
    ... adjacency alone, any tick gap: None  (0/0)  95% CI undefined  (rare count — read the interval)
  I-7 movement-origin flags: 0.0  (0/5)  95% CI [0.0, 0.4345]  (rare count — read the interval)  [move-backed 2; destination 2; STRONG 0; memory-truthful 0]
  I-8 marker contamination (turns): 0.0  (0/85)  95% CI [0.0, 0.0432]  (rare count — read the interval)
    ... (prompts): 0.0  (0/170)  95% CI [0.0, 0.0221]  (rare count — read the interval)  [0 meetings, 0 games]
  I-9 singular-persona prompts: 0.0  (0/170)  95% CI [0.0, 0.0221]  (rare count — read the interval)
  I-10 meetings with a venting participant: 0.2  (3/15)  95% CI [0.0705, 0.4519]  (rare count — read the interval)
    ... reporter killed within 3 ticks: 0.2  (3/15)  95% CI [0.0705, 0.4519]  (rare count — read the interval)  [15 body-triggered]
  I-11 [live-policy-fold] free zero-witness kills declined: 0.04  (1/25)  95% CI [0.0071, 0.1954]  (rare count — read the interval)  [ranking 0; fellow-defer 1; cover 0; other 0]
    ... ghost-top decisions: 0.0  (0/173)  95% CI [0.0, 0.0217]  (rare count — read the interval)  [0 ejected / 0 unseen death; 0 mismatches over 173 decisions]
  render budget: mean rendered lines/snapshot 35.69 over 170 snapshots; reported-testimony rows 2542 {'5-6': 1252, '<=4': 1026, '>=7': 264}
```

`uv run python scripts/measure_baseline.py --solvability <preserved smoke dir>` — exit 0:

```
Solvability ceiling over /private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/tasks/20.35/smoke/9p2i (5 games, 15 body meetings, 9 ejections at them):
  killer in candidate set: 0.9333  (14/15)  95% CI [0.7018, 0.9881]
  one candidate: 0.0  (0/15)  95% CI [0.0, 0.2039]  (rare count — read the interval)
    ... and it is the killer: None  (0/0)  95% CI undefined  (rare count — read the interval)
  at most two candidates: 0.2  (3/15)  95% CI [0.0705, 0.4519]  (rare count — read the interval)
    ... containing the killer: 1.0  (3/3)  95% CI [0.4385, 1.0]  (rare count — read the interval)
  ejected a player the crew had already cleared: 0.2222  (2/9)  95% CI [0.0632, 0.5474]  (rare count — read the interval)
  killer in candidate set, last-kill anchor: 1.0  (15/15)  95% CI [0.7961, 1.0]
```

Every cell family folds; the §11 defect is lifted. Read against the bars (n = 5 games,
every interval advisory): I-2 0/63, I-5 0/32, I-7 origin 0/5, I-8 0/85 + 0/170 and
I-9 0/170 all read at their targets; I-3, I-4 and I-6 are empty-denominator cells — the
sole-flag and STRONG alibi_vs_sighting classes did not occur on these bytes — and take
their real read at the record. The recording half was already clean (§§5–8).

RULING: the owner's restart go was given 2026-08-25 (recorded by the orchestrator; the
owner also directed two parallel Featherless workers and an ETA re-derivation at the
first leg). The §12 ABANDON is LIFTED TO GO for Task 20.36 on the corrected instrument.
The §13 operating notes carry unchanged, including note 3: the record runs the honesty
instrument after the FIRST completed seed of each leg, not only at the end.
