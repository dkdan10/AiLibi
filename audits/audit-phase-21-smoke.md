# Audit — Phase 21 smoke: five seeds on the corrected substrate

**Date:** 2026-08-28
**Task:** 21.14 — the smoke (operator), STOP-and-report, with the abandon branch
**Source state:** `b6648899` (origin/main), branch `phase-21-smoke`. This report FIXES the source
state it certifies: a merge into `agents/`, `meetings/`, `observation/`, `orchestrator/`,
`engine/`, `api/replay_loader.py` or the prompt set between this report and the record reopens the
window, and the smoke runs again from zero on the changed source with every number re-derived.
**Instruments, in order:** `scripts/refresh_samples.sh` (real provider) → `scripts/validity_gate.py`
→ `scripts/verify_samples.sh` → `scripts/measure_baseline.py --honesty` / `--solvability`, plus a
marker pass built directly off the recorded bytes and the recorded observation packets.
**Reads against:** the Wave-0 register (`audits/review-2026-08-26/A/`, `.../B/`) for the six
repairs' committed reference values, and `audits/audit-phase-20-smoke.md` for the operating rules
this smoke inherits.

## 0. The verdict, in one line

**GO. The recording window opens on `b6648899`.** No STOP criterion was met: the validity gate
passed all ten checks, byte-identity reproduced twice, the recorded substrate stamp equals the
declared corrected slate on all five games, no opening defaulted and no `failed_call` row of any
kind was recorded, **both instruments folded every cell family — at the first completed seed and
over the set** (the class the last smoke ABANDONed on), the locked prompt-version map equals the
live registry, and **all six of the contract's corrected behaviours are OBSERVED on freshly recorded
bytes**, each against its committed reference value. The seventh repair — the win-ordering fix
(A-1 / 21.6) — went unexercised at this n and is recorded **UNTESTED** in §7.1 rather than implied
green, exactly as the contract predicted.

Five seeds, 16 meetings, **$0.0000**, 33m03s of operator wall. One residual observation and one
operator note are routed in §15; neither is a criterion and neither is stretched into one.

## 1. What this is, and what it is not

The standing cadence rule is smoke before record. The next record is **maintenance-of-record**: it
re-records the committed sets on repaired bytes, publishes every instrument cell before and after,
and declares no verdict. Nothing here is a bar, met or missed. The standing canon is that
**baseline 7 is canon by explicit owner override of a FINDING verdict**, bars 1 and 2 missed
(`audits/audit-phase-20-baseline-7.md` §6.1), so bar language would describe a decision procedure
this phase does not have.

It is not a measurement either. Five seeds carry no power, and every cell below that could be read
directionally is labelled directional.

What it IS: the cheap proof that the whole stack is live and coherent before ~20 h of operator wall
is spent — the lever slate, the v5 prompt set, the recorder's real worker path, the substrate stamp,
the validity gate, and **the instruments reading a freshly recorded set rather than committed
bytes.** That last clause is the one the Phase-20 smoke failed on (`audits/audit-phase-20-smoke.md`
§0: the validity gate passed all ten checks and the honesty instrument raised on the same bytes),
which is why the ordering rule in §8 is a contract item rather than advice.

## 2. The recorded configuration

The whole environment was exported in one block before any worker process started; every lever is
read at runner construction, never mid-run. The operator's `FEATHERLESS_API_KEY` is sourced from the
gitignored repo-root `.env` and is **not reproduced here, in the PR, or in any log excerpt in this
record** — the wrapper prints an eight-character prefix at `scripts/refresh_samples.sh`:551 and this
report keeps none of it.

```
AILIBI_LLM_PROVIDER=featherless
AILIBI_PROMPT_SET=qwen3_6_27b
AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B
AILIBI_NUM_PLAYERS=9  AILIBI_NUM_IMPOSTORS=2  AILIBI_TASKS_PER_CREWMATE=2
AILIBI_SAMPLE_DIR=/Users/danielkeinan/ailibi-smoke-21-14/9p2i     # absolute, OUTSIDE the repo
AILIBI_REFRESH_WORKERS=2
AILIBI_SEED_MAX_ATTEMPTS=8
AILIBI_LAST_SEEN_FROM_SIGHTINGS=1
AILIBI_VENT_SINGLE_MINT=1
# AILIBI_IMPOSTOR_ROLL_CALL — unset, in this and in every later gate/instrument shell
```

**Why two `AILIBI_*` exports ride a maintenance-of-record smoke, in one line:**
`last_seen_from_sightings` (21.4) and `vent_single_mint` (21.5) are not levers — they are Wave-1a
REPAIR gates registered default-OFF only because no byte-identity seam existed for a memory render,
they hold that seam until Task 21.15 flips them unconditional and DELETES them outright, and nothing
is decided on them.

The two env names were read out of the live registry rather than typed from the contract:
`orchestrator/replay.py`:141 `ENV_LAST_SEEN_FROM_SIGHTINGS` and :167 `ENV_VENT_SINGLE_MINT`,
documented at `.env.example`:169 and :196. `_TOGGLEABLE_LEVER_RESOLVERS` carries exactly THREE live
toggles at this HEAD, so no third repair gate was registered before dispatch and none is missing from
the block. `AILIBI_MANIFEST` needs no export: it defaults under the sample dir
(`scripts/refresh_samples.sh`:37).

`$SMOKE_DIR` is outside the repository for three reasons the contract names and this run confirms: a
bare `bash scripts/verify_samples.sh` walks EVERY set under the samples root
(`scripts/verify_samples.sh`:16-23), so a scratch set under `replays/samples/` would silently join
the committed gate; the per-refresh stage is created under `dirname "$SAMPLE_DIR"` (:737), so an
out-of-tree sample dir keeps the staging out of tree too; and §12 preserves these bytes, so a
directory a reboot reclaims would defeat the $0 re-measure.

### 2.1 The preflight refuses in BOTH directions — proven, not asserted

The wrapper's substrate-lever preflight (`scripts/refresh_samples.sh`:303, delegating the comparison
to `orchestrator.replay.substrate_slate_mismatches`) runs on the DRY-RUN path (:524) as well as the
real one (:650). Both refusals were run first, and both wrote nothing.

**(a) an export nobody declared** — the corrected slate exported, `--expect-levers` omitted:

```
Error: the live substrate-lever slate does not match --expect-levers.
       Expected ON: (none — the bare slate: every live toggle OFF)
       Mismatch: last_seen_from_sightings must be OFF but the live slate reads ON
       (AILIBI_LAST_SEEN_FROM_SIGHTINGS); vent_single_mint must be OFF but the live slate
       reads ON (AILIBI_VENT_SINGLE_MINT)
       Export exactly the levers you named and unset every other AILIBI_*
       lever export, then re-run. Nothing was staged.
```

**(b) a declared gate left unexported** — the direction the contract insists is equally fatal:

```
Error: the live substrate-lever slate does not match --expect-levers.
       Expected ON: last_seen_from_sightings,vent_single_mint
       Mismatch: last_seen_from_sightings must be ON but the live slate reads OFF
       (AILIBI_LAST_SEEN_FROM_SIGHTINGS); vent_single_mint must be ON but the live slate
       reads OFF (AILIBI_VENT_SINGLE_MINT)
```

**(c) exported AND declared** — the sanctioned preview, which is the recorded configuration:

```
[dry-run] mode: seeds
[dry-run] seeds: 4,13,30,39,43
[dry-run] roster: num_players=9 num_impostors=2 tasks_per_crewmate=2
[dry-run] sample dir: /Users/danielkeinan/ailibi-smoke-21-14/9p2i
[dry-run] provider: featherless
[dry-run] meeting model: Qwen/Qwen3.6-27B
[dry-run] prompt set: qwen3_6_27b
[dry-run] substrate flags: expected levers ON = last_seen_from_sightings,vent_single_mint;
          every other live toggle OFF; the graduated levers unconditional ON
[dry-run] seed workers: 2 parallel (each records one seed, then pulls the next available seed
          from the queue; Featherless: 2 units per 32B request → 4-unit cap)
[dry-run] seed crash-retry: up to 8 attempt(s) per seed on a transport/crash error
[dry-run] no API calls made; no files written.
Substrate slate OK: expected levers ON = last_seen_from_sightings,vent_single_mint; every other
live toggle OFF; the graduated levers unconditional ON.
```

`/Users/danielkeinan/ailibi-smoke-21-14` did not exist after any of the three. The real run's own
preflight block, before any seed staged:

```
Using Featherless API key prefix: <redacted — the wrapper prints 8 characters; this record keeps none>
Locked substrate OK: AILIBI_PROMPT_SET=qwen3_6_27b.
Model-set coupling OK: qwen3_6_27b on Qwen/Qwen3.6-27B.
Model registry OK: Qwen/Qwen3.6-27B is registered in the production client.
Substrate slate OK: expected levers ON = last_seen_from_sightings,vent_single_mint; every other
live toggle OFF; the graduated levers unconditional ON.
```

## 3. The seed slate, and the census it was drawn from

The census was **re-derived at this HEAD** rather than quoted, and every figure the contract's Step 2
states reproduces exactly. Over the committed `replays/samples/9p2i`:

```
seeds=50  meetings=152  ejections=99
contradiction rows: vent_sighting 92, alibi_vs_sighting 29, alibi_conflict 21, alibi_vs_physical 2
vent_sighting appears in 45 of 50 seeds; alibi_vs_sighting in 16; alibi_conflict in 14
every seed but one (seed 2) carries at least two meetings
densest alibi_vs_sighting: 4 (five), then 30 and 39 (four), then 40 (three)
densest vent_sighting: 43 (five), then 20 and 28 (four)
endings: CREWMATE_EJECT 38, IMPOSTOR_PARITY 12
```

The drawn slate is **4, 13, 30, 39, 43**, verified per seed against the five coverage requirements:

| seed | meetings | ejections | ending | contradiction rows |
|---|---|---|---|---|
| 4 | 2 | 1 | IMPOSTOR_PARITY | alibi_vs_sighting 5, alibi_conflict 1 |
| 13 | 5 | 1 | IMPOSTOR_PARITY | one of each kind |
| 30 | 4 | 2 | CREWMATE_EJECT | alibi_vs_sighting 4, alibi_conflict 2, vent_sighting 2 |
| 39 | 2 | 2 | CREWMATE_EJECT | alibi_vs_sighting 4, alibi_conflict 2, vent_sighting 2 |
| 43 | 2 | 2 | CREWMATE_EJECT | vent_sighting 5 |

Several `alibi_vs_sighting` rows, `vent_sighting` present (without it the oracle-dialect check is
vacuous), `alibi_conflict` present, multi-ejection games present, a five-meeting game to exercise the
ballot render repeatedly, and the five split across both recorded ending reasons.

**Two honest limits.** The committed census records only `CREWMATE_EJECT` (38) and
`IMPOSTOR_PARITY` (12), so no seed could be drawn for a task-completion ending; **none occurred, and
that path is UNTESTED.** And **the census is a PROXY**: six behavioural repairs move trajectories, so
coverage is reported as OBSERVED in §4 rather than assumed from it.

## 4. The per-seed table, as recorded

| seed | wall (serial) | meetings | ejections | ending | winner | calls | tokens | cost |
|---|---|---|---|---|---|---|---|---|
| 4 | 594 s | 3 | 0 | IMPOSTOR_PARITY | IMPOSTORS | 36 | 175,859 | $0.0000 |
| 13 | 791 s | 4 | 2 | CREWMATE_EJECT | CREWMATES | 44 | 216,080 | $0.0000 |
| 30 | 640 s | 3 | 2 | CREWMATE_EJECT | CREWMATES | 36 | 169,194 | $0.0000 |
| 39 | 747 s | 4 | 2 | CREWMATE_EJECT | CREWMATES | 44 | 217,255 | $0.0000 |
| 43 | 392 s | 2 | 2 | CREWMATE_EJECT | CREWMATES | 24 | 107,204 | $0.0000 |
| **all** | **33m03s wall** | **16** | **8** | — | CREW 4 / IMP 1 | **184** | **885,592** | **$0.0000** |

Wall clock: seed 4 alone 9m55s (recorded first, for the §8 probe), then 13/30/39/43 on two workers in
23m08s. Total operator wall **33m03s**.

**Coverage as OBSERVED on the smoke bytes**, not assumed from the census that selected the slate:

```
seeds=5  meetings=16  ejections=8
contradiction rows: vent_sighting 10, alibi_vs_sighting 4, alibi_conflict 3
vent_sighting in 4 of 5 seeds; alibi_vs_sighting in 2; alibi_conflict in 2
endings: CREWMATE_EJECT 4, IMPOSTOR_PARITY 1
every seed carries at least two meetings
```

Every one of the five requirements is met on the recorded bytes: `vent_sighting` present in six
meetings (so §7's oracle check is NOT vacuous), `alibi_vs_sighting` present, `alibi_conflict`
present, four multi-ejection games, two four-meeting games, both endings.

**The proxy moved, exactly as the contract warned.** Seed 4 recorded 3 meetings and 0 ejections where
the committed census carries 2 and 1; seed 13 recorded 4 meetings and 2 ejections against 5 and 1;
seed 43 held its five `vent_sighting` rows exactly. **`alibi_vs_physical` was not exercised** — the
census puts it in 2 of 50 seeds and no slate seed carried it — and is recorded UNTESTED.

## 5. The gate

### 5.1 `scripts/validity_gate.py` — all ten checks, named individually

Run in the SAME shell as the recording, carrying both repair-gate exports: `eval/validity.py`:931
derives `cost_and_provenance_exact`'s comparison snapshot from the gate process's own environment,
and `byte_identical_reconstruction` reaches `api/replay_loader.py`:653 through `verify_samples`, so a
bare gate shell would report a substrate refusal rather than a result.

```
uv run python scripts/validity_gate.py "$SMOKE_DIR" --expected-model Qwen/Qwen3.6-27B --require-zero-cost

Validity gate over /Users/danielkeinan/ailibi-smoke-21-14/9p2i (5 games):
  [PASS] all_games_reach_game_over: 5/5 games reached a reconstructed game_over with a consistent win condition
  [PASS] meeting_rate_and_resolution: meeting_rate 1.0 (floor 0.60); 16 resolved meetings; 0 unresolved
  [PASS] no_duplicate_meeting_rows: 0 duplicate meeting rows over 16 (want 0)
  [PASS] no_tick_1_kills: 0 kills at tick <= 1 (want 0)
  [PASS] no_friendly_fire_kills: 0 impostor-on-impostor kills (want 0)
  [PASS] no_betrayal_ballots_or_accusations: 0 teammate-betrayal ballots/accusations over 92 multi-impostor ballots (want 0)
  [PASS] no_railroaded_crew_ejections: 0 railroaded crew rows over 346 rendered crew suspicions (want 0)
  [PASS] no_dangling_primary_reason_id: 0 dangling primary_reason_id over 92 ballots (want 0)
  [PASS] cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact on 5 games
  [PASS] byte_identical_reconstruction: 0 samples drifted from byte-identical reconstruction (want 0)
Validity gate PASSED (all checks green).
```

The two the contract asks be quoted verbatim are the last two above:
`cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact on
5 games` and `byte_identical_reconstruction: 0 samples drifted from byte-identical reconstruction
(want 0)`.

The gate was then re-run with the version provenance **pinned exactly** rather than merely checked
for coherence, using the recorder's own `REQUIRED_PROMPT_VERSIONS_CLI` rendering — the same pin the
recorder's acceptance line prescribes:

```
--expected-prompt-versions accusation_round=accusation_round.qwen3_6_27b.v5,\
crewmate_report=crewmate_report.qwen3_6_27b.v5,\
impostor_report=impostor_report.qwen3_6_27b.v5,\
vote_ballot=vote_ballot.qwen3_6_27b.v5
```

All ten checks PASS again, identically. Both invocations exit 0.

Byte-identity, run **twice** under the same environment:

```
bash scripts/verify_samples.sh "$SMOKE_DIR"   ->  All 5 samples verified clean.   (run 1)
bash scripts/verify_samples.sh "$SMOKE_DIR"   ->  All 5 samples verified clean.   (run 2)
```

### 5.2 The prompt-set version, read three ways (never inferred from the registry)

**Out of the recorded meeting rows' own `prompt_versions` stamp**, over all 16 meetings:

```
accusation_round: accusation_round.qwen3_6_27b.v5
crewmate_report : crewmate_report.qwen3_6_27b.v5
impostor_report : impostor_report.qwen3_6_27b.v5
vote_ballot     : vote_ballot.qwen3_6_27b.v5
```

**Out of the recorded MANIFEST rows**, all five identical: `accusation_round.qwen3_6_27b.v5,
crewmate_report.qwen3_6_27b.v5, impostor_report.qwen3_6_27b.v5, vote_ballot.qwen3_6_27b.v5`, each row
`git_sha b6648899`, `cost_usd 0.0000`.

**The expected read is v5 and the read is v5**, against the committed 9p2i MANIFEST's v4 rows. A v4
read on fresh bytes would have been a STOP; it did not occur.

**Criterion 7 — the corpus recorder's lock against the live registry**, both sides quoted verbatim.
`scripts/record_ml_corpus.sh` `REQUIRED_PROMPT_VERSIONS` (:167), echoed by its own dry run under this
same shell:

```
[dry-run] prompt versions: locked to [accusation_round.qwen3_6_27b.v5, crewmate_report.qwen3_6_27b.v5,
          impostor_report.qwen3_6_27b.v5, vote_ballot.qwen3_6_27b.v5]
```

The live `orchestrator.game.PROMPT_VERSION_SETS["qwen3_6_27b"]`:

```
{"accusation_round": "accusation_round.qwen3_6_27b.v5", "crewmate_report": "crewmate_report.qwen3_6_27b.v5",
 "impostor_report": "impostor_report.qwen3_6_27b.v5", "vote_ballot": "vote_ballot.qwen3_6_27b.v5"}
```

**They AGREE, on all four templates.** This is the check the corpus recorder performs on the REAL
path only (`check_prompt_version_registry`, called at :1177); its dry run merely ECHOES the lock and
exits, so a disagreement would have aborted legs two and four of the record hours in, after the
samples legs had already been spent. The corpus recorder's dry run also passed its substrate-lever
preflight under this shell, so the corrected slate is one both wrappers accept.

## 6. The recorded substrate stamp

Read out of the five `game_over` rows, not off a live snapshot:

| seed | keys | missing | extra | retired stamped OFF | `last_seen_from_sightings` | `vent_single_mint` | `impostor_roll_call` |
|---|---|---|---|---|---|---|---|
| 4 | 24 | none | none | none | True | True | False |
| 13 | 24 | none | none | none | True | True | False |
| 30 | 24 | none | none | none | True | True | False |
| 39 | 24 | none | none | none | True | True | False |
| 43 | 24 | none | none | none | True | True | False |

All **TWENTY-FOUR** canonical keys present on every game, the twenty-one retired keys all True, both
repair gates True, the one lever False. And the comparison the contract insists all three readers use
rather than re-derive:

```
orchestrator.replay.substrate_slate_mismatches(["last_seen_from_sightings", "vent_single_mint"]) == []
```

**Empty.** The wrapper's preflight (which delegates to the same function) and the recorded stamps
agree; nothing was reconciled by hand.

**The MANIFEST `flags` cell, read beside it: TWENTY-THREE ON keys on every row** — the twenty-one
retired plus `last_seen_from_sightings` and `vent_single_mint`, sorted — against the committed
record's twenty-one. **That difference IS the corrected substrate rendering correctly, not a defect**,
and Step 1 criterion 3 names it as explicitly NOT a stop. Stated here in the row rather than left to
be discovered.

## 7. The six corrected behaviours, read off the recorded bytes

Built directly from the recorded prompts, the recorded action rows, the recorded ballots and the
recorded observation packets — **not from any instrument's fold**, so a marker cannot be silently
satisfied by an instrument looking elsewhere.

**The marker code is calibrated against the register.** Applied unchanged to the four committed sets
it reproduces the published cells exactly: A-6's leak partition **45/326 flag-present and 0/342
flag-absent**; A-17's **3,350** vote prompts with **0** current-meeting claim lines; A-14's **35,350**
recorded actions over **5,960** tick rows; A-3's **3,602** ballots with **120** carrying the redirect
marker; A-31's **1,505** double-minted rows, **27** distinct heard-only rows and **0** witnessed-only.
The same code then produced the smoke column.

| # | repair | marker | committed reference | **smoke (5 seeds / 16 meetings)** | reading |
|---|---|---|---|---|---|
| 1 | A-6 (21.1) | the taught oracle line inside a rendered proof block | 3,186 of 7,211 prompts across the four sets carry `The engine certified` — one in every prompt that renders the block; leak **45/326 = 13.8%** where the block renders, **0/342** where it does not | **0 of 184** prompts carry it, while **51 prompts DO render a `Proof.` block**; banned render vocabulary (`the engine`, `the system`, `the detector`, `certif`, `flag`) **absent from every rendered line** | **OBSERVED** |
| 1b | A-6, spoken | the oracle net over `free_text`, ballot rationales and claim reasons | 18 hits / 3,083 utterances on `samples/9p2i`; 72 across the four sets. At the committed 13.8% flag-present leak rate, 6 flag-bearing meetings would be expected to yield **~0.8** leaking meetings — so a zero here is consistent with the repair AND weak on its own | **0 hits over 329 utterances**; leak **0/6** flag-present, **0/10** flag-absent | **OBSERVED**, directional at this n — the render-side row above carries the weight |
| 2 | A-17 (21.2) | structured testimony rows in the vote-ballot prompts | **0 of 3,350** 9p2i vote prompts carry a `saw:` / `claims:` / `said:` block — the flat render dropped ≥1 field on 3,593 of 3,602 turns | **92 of 92** vote prompts carry ALL THREE, over 546 rendered turn heads | **OBSERVED** |
| 3 | A-14 (21.3) | every recorded action row carries an explicit disposition; queued-behind-trigger actions marked discarded | **0 of 5,960** committed tick rows carry `action_dispositions`; the register re-derived 2,166 of 35,350 = **6.13%** as submitted-with-no-consequence | **101 of 101** tick rows carry it; **56 of 684 = 8.19%** `discarded_by_meeting` across **15** meeting-trigger ticks — `do_task` 23, `move` 23, `wait` 4, `report` 2, **`kill` 2**, `vent` 1, **`emergency` 1** | **OBSERVED** |
| 4 | A-3 (21.3) | guard-redirected ballots carry a machine-readable provenance field | **0 of 3,602** ballots carry `guard_rewrite_reason`; 120 are detectable only by regex over the bracketed display marker | **8 of 92** ballots carry `guard_rewrite_reason` (`under_gate_redirect` 6, `invalid_target` 1, `teammate_coerced` 1); **0** non-`parse_default` rows are missing `guard_redirected_from` | **OBSERVED** |
| 5 | B-8 (21.4) | the belief line's last-seen agrees with the agent's own sightings | `samples/9p2i` **401/1,051 = 38.2%** carry a strictly later sighting, **225/1,051 = 21.4%** stale AND wrong room (B-8 published 34.4% / 19.6% over the corpus sets) | **0 of 263 stale (0.0%)**, **0 of 263 stale-and-wrong-room (0.0%)**; and at the packet layer **520 of 520** belief rows match the observer's OWN packet at that tick, exactly, room and all | **OBSERVED** |
| 6 | A-31 (21.5) | exactly one memory row per witnessed vent; no audible copy past the teammate firewall | **1,505** double-minted rows across the four sets; every distinct witnessed vent double-minted (90/90, 297/297, 20/20, 28/28 = **100%**); 27 distinct heard-only rows, 27/27 impostors | **40 witnessed-vent rows, 0 heard-vent rows, 0 double-minted**; at the PACKET layer **0 `vent_use_heard` events over 517 packet rows**, with 9 witnessed vents each delivered ONCE as the visible action | **OBSERVED** |

Two of the six are verified at a second, stronger layer than the render. `observation/service.py::_audible_events`
is where the A-31 repair lives, so the preserved observation packets settle it at the source: **zero
`vent_use_heard` events were emitted at all**, which makes the 27-row teammate-firewall residue class
*unreachable* rather than merely filtered — the outcome 21.5 specified. And for B-8 the packets are
the ground truth for "the agent's own sightings": **520/520 rendered last-seen rows are something that
observer actually perceived at that tick**, reading BOTH perception channels (`visible_players` and
`moved_players`, whose destination is the placement the render uses).

### 7.1 The one repair the five seeds could not exercise

**A-1 / 21.6, the win-ordering repair: UNTESTED**, exactly as the contract predicted at this n. The
repair makes the win check run when the game is decided, meeting-trigger tick or not; no smoke game
reached a state where the ordering could differ. The verifier's note is restated rather than papered
over: the finding is SPECIFIED and test-pinned, and **both realized cases in the committed record
recorded the correct winner** — a latent-correctness repair with zero realized exposure. Its coverage
is `tests/`, not these bytes.

### 7.2 One residual observation, named rather than absorbed

Six of 263 rendered belief rows (2.3%) carry a last-seen tick LATER than any sighting row **surviving
in the same rendered memory block** — e.g. `replay-seed-4` p-3: `p-2: suspicion 0.45 (last seen in
ENGINEERING at tick 17)` while that prompt's own observation rows stop at a tick-13 move.

This is **the opposite direction from B-8** and is not the defect 21.4 repaired. The packet check
settles what it is: all six rows are own-eyes and correct — p-2's own recorded trajectory puts it in
ENGINEERING at tick 17, and 520/520 belief rows match their observer's packet. What is missing is the
supporting observation ROW in the render, shed by the elastic memory budget: the belief block is the
NON-elastic carve-out (`agents/memory/store.py`:2296-2302 puts `beliefs_block` in
`non_elastic_blocks`; :2314-2330 charges it first and sheds the trail then the observations against
the remainder). B-8 itself named this structure — it worried about the budget leaving only a FALSE
statement; here it leaves a TRUE statement without its visible support.

**It is not a STOP.** Step 1 criterion 6 enumerates its cases and this is not among them, and the
criterion's subject is a merged repair contradicted by the bytes — this repair is confirmed by them.
It is a **legibility** item: a model reading that prompt cannot see why the belief line says what it
says. §15 routes it.

## 8. The honesty and solvability cells

**The ordering rule, executed.** `measure_baseline.py --honesty` was run on the FIRST completed seed
ALONE — seed 4, recorded by itself in 9m55s — **before the remaining four seeds queued**. This is the
whole lesson of the last smoke compressed into an ordering rule
(`audits/audit-phase-20-smoke.md` §13 note 3), and it is the class Step 1 criterion 5 now names.

**The first-seed probe: EXIT 0, and NOT vacuous** — seed 4 carried 3 meetings, so no re-probe on a
meeting-bearing seed was needed:

```
Evidence-honesty instruments over .../9p2i (1 games, 3 meetings; +1 agent clock proved on 67 discriminating sightings):
  I-2 false crew self-placement: 0.0 (0/12) ... impostor claims: 0.0 (0/3) ... copyable: 0.0 (0/12)
  I-3 sole-flag precision: None (0/0) [0 sole-flag meetings]     I-4 grounded sighting side: None (0/0)
  I-5 fabricated completion lines: 0.0 (0/6) [+1 render offset 6/6]   I-6 adjacent-room STRONG share: None (0/0)
  I-7 movement-origin flags: 0.0 (0/2) [move-backed 1; destination 1]  I-8 marker contamination: 0.0 (0/18 turns, 0/36 prompts)
  I-9 singular-persona prompts: 0.0 (0/36)   I-10 venting participant: 0.0 (0/3) ... reporter killed within 3: 0.6667 (2/3)
  I-11 free zero-witness kills declined: 0.1667 (1/6) ... ghost-top: 0.0 (0/52)
  render budget: mean rendered lines/snapshot 40.11 over 36 snapshots
HONESTY_FIRST_SEED_EXIT=0     (--solvability on the same seed: EXIT 0)
```

**Over the whole set: EXIT 0**, every cell family folded with denominators. Beside the committed
`replays/samples/9p2i` reference (50 games / 152 meetings), **every row directional at this n**:

| row | committed `samples/9p2i` | **smoke (5 games, 16 meetings)** |
|---|---|---|
| I-2 false crew self-placement | 0.0046 (3/659) | **0.0 (0/66)** [0.0, 0.055] |
| … agent-frame reading | 0.003 (2/659) | **0.0 (0/66)** |
| … impostor claims | 0.0096 (1/104) | **0.0 (0/13)** |
| … copyable from a rendered self-location line | 0.0637 (42/659) | **0.0303 (2/66)** |
| I-3 sole-flag precision (per victim) | None (0/0) | **None (0/0)** [0 sole-flag meetings] |
| I-4 grounded sighting side (±0/±1/±2) | None (0/0) | **None (0/0)** |
| I-5 fabricated completion lines | 0.0 (0/308) | **0.0 (0/25)** [+1 render offset 25/25] |
| I-6 adjacent-room STRONG share | None (0/0) | **None (0/0)** |
| I-7 movement-origin flags | 0.0 (0/27) | **0.0 (0/4)** [move-backed 2; destination 2] |
| I-8 marker contamination (turns) | 0.0 (0/871) | **0.0 (0/92)** |
| … (prompts) | 0.0 (0/1,746) | **0.0 (0/184)** |
| I-9 singular-persona prompts | 0.0 (0/1,746) | **0.0 (0/184)** |
| I-10 meetings with a venting participant | 0.1711 (26/152) | **0.125 (2/16)** |
| … reporter killed within 3 ticks | 0.1118 (17/152) | **0.3125 (5/16)** |
| I-11 free zero-witness kills declined | 0.0351 (8/228) | **0.0435 (1/23)** [fellow-defer 1] |
| … ghost-top decisions | 0.0029 (5/1,750) | **0.0 (0/176)** [0 mismatches over 176] |
| render budget | 37.03 lines/snapshot over 1,746 | **39.16 over 184**; testimony rows 3,318 |

Solvability, same two columns:

| row | committed `samples/9p2i` | **smoke** |
|---|---|---|
| killer in candidate set | 0.875 (126/144) | **1.0 (16/16)** [0.8064, 1.0] |
| one candidate | 0.1389 (20/144) | **0.0625 (1/16)** |
| … and it is the killer | 0.7 (14/20) | **1.0 (1/1)** |
| at most two candidates | 0.3194 (46/144) | **0.125 (2/16)** |
| … containing the killer | 0.8043 (37/46) | **1.0 (2/2)** |
| ejected a player the crew had already cleared | 0.2088 (19/91) | **0.0 (0/8)** |
| killer in candidate set, last-kill anchor | 0.9375 (135/144) | **1.0 (16/16)** |

Both instruments were run on committed bytes in a bare shell too, before the smoke, and both exit 0
there — so the smoke's exit 0 is not an artifact of a broken instrument passing everything.

## 9. Backward compatibility on the committed bytes, at $0

Run in a shell with **both repair-gate exports UNSET** — which is the point of the check, not an
oversight. The committed stamps predate both keys entirely, and the missing-key-reads-OFF rule makes
them agree only with a bare snapshot; under the recording shell's exports every committed game would
report a substrate mismatch and this check would fail for a reason that is not a regression.
`AILIBI_IMPOSTOR_ROLL_CALL` is unset here too.

```
AILIBI_* in this shell:
(none)

=== bare scripts/verify_samples.sh: EVERY committed set under the samples root ===
=== verifying .../replays/samples/4p1i/ ===   All 50 samples verified clean.
=== verifying .../replays/samples/9p2i/ ===   All 50 samples verified clean.
BARE_VERIFY_EXIT=0

=== git status --porcelain replays/ ===   (empty)
```

**The conclusion, stated rather than implied: all 100 committed samples still reconstruct
byte-identically under this build, which carries both new stamp keys and the record-fidelity fields
the committed bytes do not have.** The additive-field policy holds and no committed byte moved.

## 10. The watch item, scanned by hand

Not delegated to the gate — the validity gate has no `deadline_default` check at all
(`scripts/record_ml_corpus.sh`:796-797 says so in as many words).

**No recorded `failed_call` row of any kind exists in the five seeds** — the counter is zero, so the
question of `error_type == "deadline_default"` is answered under both shapes at once. The sentinel
model shape `"(deadline_default)"` is likewise absent from every row.

```
failed_call rows by error_type: {} (none recorded)
deadline_default rows (EITHER shape): 0
```

The recorder's own summary counters, quoted from the post-record eval-report rebuild:

```
lost_openings 0 (defaults 0) | vote_defaults 0 (must_vote 0) | ballot_redirects 6 (eject 6)
missed_skip 13 | ejection_accuracy 1.0000 (8/8) | meeting_rate 1.00 (16 meetings)
```

**Zero lost openings, zero defaults, zero vote defaults.** The freeze guard `check_replay_provenance`
refused two seeds for exactly this at the last record (`audits/audit-phase-20-baseline-7.md` §0.4,
re-recorded in 12m33s); nothing here would trip it.

## 11. Operating data, and the re-derived projection

Measured, not inherited.

```
16 meetings | 184 LLM calls | 843,511 input + 42,081 output = 885,592 tokens | $0.0000
tokens/call    4,813.0
calls/meeting     11.50
tokens/meeting 55,349.5
per-seed serial wall: 594, 791, 640, 747, 392 s  (mean 632.8, min 392, max 791)
```

Against the committed `samples/9p2i` (1,746 calls over 152 meetings, 7,406,792 tokens): **11.5 vs
11.5 calls per meeting, and 55,350 vs 48,729 tokens per meeting — the corrected substrate costs
+13.6% per meeting and +24.0% per game.** That is the A-17 repair paying its way: the vote-ballot
prompt now renders each turn's full observation and claim body instead of one line, which is the
whole point of the repair and the dominant new input-token term. **Worth carrying into the record's
plan as a measured fact rather than a surprise.**

**Retries, transport blips, worker diagnostics: none.** Both run logs were scanned for `WARN`,
`ERROR`, `Traceback`, lock, dead-owner and claim diagnostics — **zero matches in either**. No seed
consumed a second attempt of its budget of 8.

**The four-leg projection, re-derived from these measured figures.** Method, stated so 21.15 re-runs
it rather than inherits it: the two 9p2i legs (`samples` 50 + `ml_corpus` 150 = 200 games) are the
roster this smoke actually ran, so they are projected from its own measured SERIAL seconds-per-seed at
two workers, with the bracket's ends the fastest and slowest measured seed rather than a guess; the
two 4p1i legs (100 games, **not smoked**) are projected from the wall the phase-20 record MEASURED for
those same legs (1h29m31s, §0.3) scaled by the corrected substrate's measured ×1.240 token inflation
— an inference, labelled one, and one the projection is insensitive to because the 4p1i legs are 6.4%
of the last record's wall; overhead is carried as the phase-20 record's own realized factor (its
window wall over the sum of its four leg walls, ×1.0009).

| | 9p2i legs (200 games) | 4p1i legs (100 games) | **four-leg total** |
|---|---|---|---|
| low (fastest measured seed, 392 s) | 10h53m20s | 1h51m00s | **12h45m01s** |
| centre (measured mean, 633 s) | 17h34m40s | 1h51m00s | **19h26m43s** |
| high (slowest measured seed, 791 s) | 21h58m20s | 1h51m00s | **23h50m37s** |

**The bracket is 12h45m – 23h51m, centred at 19h27m**, against the phase-20 record's realized
**23h25m42s** for the same 300 games. The bracket is wide by construction: with $0 flat-rate billing
the wall is dominated by hosted-provider latency, which a five-seed sample measures coarsely and
which varies hour to hour. The phase-20 realized figure sits just inside the high end, which is the
right shape for a projection that must not under-promise a 20-hour window.

## 12. The hardened worker path, as exercised

**Two parallel workers did claim seeds from the shared queue**, twice over, and the log shows the
queue model working rather than a static split:

```
Recording 4 seeds with 2 parallel workers (each records one seed, then pulls the next available seed from the queue).
--- [worker 2] recording seed 13 ---
--- [worker 1] recording seed 30 ---
    seed 30 done in 640s | ... | done 1/4
--- [worker 1] recording seed 39 ---          <- worker 1 pulled the next unclaimed seed
    seed 13 done in 791s | ... | done 2/4
--- [worker 2] recording seed 43 ---          <- worker 2 pulled the next unclaimed seed
    seed 43 done in 392s | ... | done 3/4
    seed 39 done in 747s | ... | done 4/4
Refresh complete in 23m8s: 4/4 seeds reached a meeting
```

**Worker occupancy:** 2,570 s of serial seed work across 1,388 s of wall on two workers = **92.6%
occupancy**; the 7.4% idle is the tail after seed 43 finished while seed 39 ran on. **No lock,
dead-owner or claim diagnostic appeared, and no spurious abort occurred** — so nothing here had to be
cleared by re-running, which the contract forbids.

**One honest limit, and it belongs in this section rather than §13's footnotes.** The B-18 back-port's
ten-poll dead-owner streak **could not have been exercised on this machine at all.** `bash --version`
is **GNU bash 3.2.57(1)-release (arm64-apple-darwin24)**, macOS's stock shell, which predates
`$BASHPID`; both wrappers fall back to `$$`, every worker then shares the main shell's pid, and
dead-owner detection **degrades to a documented no-op** (`scripts/refresh_samples.sh`:768-776,
`scripts/record_ml_corpus.sh`:1314-1320; ledgered at `audits/audit-phase-18-close.md` §7 row 5 and
`training/README.md` §6 row 5). The mkdir mutex and its release still serialize correctly — which is
what this run exercised, and no MANIFEST row was lost across two concurrent writers. The streak
itself is carried by `tests/scripts/test_record_ml_corpus.py`
(`test_lock_fails_loud_when_a_dead_owner_stays_the_owner`,
`test_lock_tolerates_a_release_racing_the_dead_owner_probe`). **Installing a newer bash before the
record would restore the safety net**; that is an operator note for the owner, not a finding against
this run.

## 13. What this smoke does NOT cover

Named rather than left to be discovered.

1. **One wrapper, one roster.** The smoke drives `scripts/refresh_samples.sh` on 9p2i only. Legs 2
   and 4 of the record (`samples/4p1i`, `ml_corpus/4p1i`) are exercised here **only through their
   dry-run preflights** (§5.2) and through the hermetic recorder coverage Task 21.10 shipped. That is
   a deliberate choice, not a wrapper limitation: since 21.10 the corpus recorder DOES have a seed
   subset flag (`--seeds N,N,N`, validated pre-stage against each selected set's locked range, with a
   subset run finalizing nothing — no eval report, no `splits.json`, no FROZEN line), and this smoke
   simply does not spend on it.
2. **The 4p1i roster is not live-smoked.** Its contribution to §11's projection is an inference from
   the phase-20 record's measured legs, and is labelled one there.
3. **The dead-owner streak back-port is proven by its own tests, not by this run** — and on this
   machine no run could have proven it. §12 carries the mechanism and the operator note.
4. **B-21's own remedy is a test result, not a smoke result.** The corpus recorder's engine now
   executes in tests (`tests/scripts/test_record_ml_corpus.py` is **88** tests at this HEAD, up from
   the 54 B-21 measured, including `test_two_workers_lose_no_manifest_row`, which stages four real
   seeds through the recording engine under a fake provider). This run exercises the SIBLING
   wrapper's engine live; it does not exercise the corpus recorder's.
5. **`alibi_vs_physical` and the task-completion ending are UNTESTED** (§4), and the win-ordering
   repair is UNTESTED (§7.1).
6. **No measurement.** Five seeds. Every directional cell says so where it appears.

## 14. The STOP criteria, quoted verbatim and read one by one

The criteria are the ones `tasks/phase-21.md` Task 21.14 Step 1 states, and no others. No ratified
memo owns them in this wave — the pre-registration belongs to the lever wave downstream — so this
report rules against these and invents none.

> 1. A `scripts/validity_gate.py` FAIL on any of the ten checks. STOP.

**NOT MET.** All ten PASS, twice (once with `--expected-prompt-versions` pinned). §5.1.

> 2. A seed whose opening defaults — any recorded `failed_call` row with
> `error_type == "deadline_default"`, or a non-zero lost-openings counter. STOP.

**NOT MET.** Zero `failed_call` rows of any kind; `lost_openings 0 (defaults 0)`;
`vote_defaults 0 (must_vote 0)`. §10.

> 3. A recorded substrate stamp that is not the declared CORRECTED slate:
> `substrate_slate_mismatches` non-empty against
> `["last_seen_from_sightings", "vent_single_mint"]`, any of the twenty-one retired keys stamped
> False, either repair gate stamped False, or `impostor_roll_call` True. STOP. Explicitly NOT a stop:
> the MANIFEST `flags` cell differing from the committed record's by exactly the two repair-gate
> keys, which is the declared slate rendering correctly.

**NOT MET.** `substrate_slate_mismatches` returns `[]`; 24 keys on all five games; no retired key
False; both gates True; the lever False. The MANIFEST `flags` cell reads 23 ON keys against the
committed 21 — **the case the criterion explicitly exempts**, and §6 says so in the row. §6.

> 4. A firewall or leak guard raising during the run. STOP.

**NOT MET.** No guard raised: every game ran to `game_over`, no seed consumed a retry, and both run
logs are free of any `WARN`, `ERROR`, `Traceback`, firewall or leak diagnostic. The gate's own
firewall row is independent corroboration: `no_betrayal_ballots_or_accusations: 0 teammate-betrayal
ballots/accusations over 92 multi-impostor ballots`. §10, §12.

> 5. An INSTRUMENT raising over the smoke bytes — `measure_baseline.py --honesty` or
> `--solvability` exiting non-zero at the first-seed probe or over the set. STOP. This is the class
> the last smoke had to rule on without a criterion; it has one now.

**NOT MET, and this is the criterion that mattered most.** `--honesty` exits 0 at the first-seed
probe (3 meetings — not vacuous) and 0 over the set; `--solvability` exits 0 in both places. Every
cell family folds with denominators. **The Phase-20 defect class does not recur on these bytes.** §8.

> 6. A merged repair contradicted by the recorded bytes: an oracle line still rendering inside a
> proof block, a vote-ballot prompt with no structured testimony row, a queued-behind-trigger action
> recorded with no disposition, a redirected ballot with no provenance field, or a witnessed vent
> minted twice. STOP.

**NOT MET, on all five enumerated cases.** 0 of 184 prompts carry an oracle line while 51 render a
proof block; 0 of 92 vote prompts lack a structured testimony row; 0 of 101 tick rows lack
dispositions and 56 queued-behind-trigger actions ARE marked discarded; 0 redirected ballots lack
provenance; 0 witnessed vents minted twice, at the render AND at the packet. §7.

The six last-seen rows in §7.2 are **not** one of the enumerated cases and are not stretched into
one: the criterion's subject is a merged repair CONTRADICTED by the bytes, and the packet check shows
these bytes confirm it (520/520). Recorded as a legibility item and routed, not as a criterion.

> 7. The corpus recorder's locked prompt-version map disagreeing with the live registry. STOP.

**NOT MET.** Both sides quoted verbatim in §5.2: identical, all four templates at
`*.qwen3_6_27b.v5`.

> 8. NOT a stop, explicitly: a directional cell that moves the unwelcome way at five seeds; a repair
> the five seeds never exercise, which is recorded as UNTESTED; and byte-level difference from the
> committed record, which is the expected consequence of a corrected substrate and not a finding.

**Read as written, and it reached three observed cases.** (i) I-10's "reporter killed within 3 ticks"
moved 0.1118 → 0.3125 and solvability's "one candidate" moved 0.1389 → 0.0625 — both directional at
n=16 meetings, both recorded and neither acted on. (ii) The win-ordering repair, `alibi_vs_physical`
and the task-completion ending are recorded UNTESTED (§4, §7.1) rather than implied green. (iii)
Every smoke byte differs from the committed record — that is what a corrected substrate means, and
this report treats it as the expected consequence rather than a finding.

## 15. The verdict, and what happens next

**GO**, ruled against Step 1 criteria 1–7, none of which was met, with criterion 8 read as written on
the three cases it reached. **The recording window opens on `b6648899`.**

The go/no-go is the owner's; this PR merges to ratify the reading, and the record is a separate
contract (21.15) that starts only after it does.

**Two items are routed rather than fixed here** — this task edits no code path, and papering a fix
inside a recording session is exactly what the contract forbids.

1. **The validity gate crashes on an `<stem>.audit.jsonl` sidecar.** `eval/validity.py`:282-290's
   `seeds_on_disk` globs `replay-seed-*.jsonl` and parses `int(path.stem.rsplit("-", 1)[1])`, which
   raises `ValueError` on an `<n>.audit` stem — the gate crashes rather than reporting. Both wrappers
   close it procedurally today by moving only `replay-seed-$seed.jsonl` out of the stage and leaving
   the sidecar in the discarded tree, and this run confirms the discipline holds: **no `*.audit.jsonl`
   exists under `$SMOKE_DIR`** (verified after every seed). Every seed here — the first-seed probe
   included — was recorded through `bash scripts/refresh_samples.sh --seeds ...`, never through a bare
   `run_tournament.py`. The one-line guard (skip or reject a non-integer stem) is **a routing slot for
   21.15's contract**, where the record's gating needs it permanently rather than procedurally.
2. **The belief line can outlive its supporting observation row in the render** (§7.2): 6 of 263 rows,
   all true, all own-eyes, none stale. Mechanism: the belief block is non-elastic and the observation
   rows are shed against the remaining budget. This is a **legibility** item — a reader of that prompt
   cannot see why the line says what it says — and a routing slot for the owner to place, not a
   blocker. Reproduction: `replay-seed-4`, `headless-seed-4:meeting-2`, agent p-3, subject p-2.

**One operator note before the record:** install a newer bash (`brew install bash`) to restore
dead-owner detection across the ~20-hour window (§12). The mutex is correct without it; the safety
net is not armed with it.

**The smoke bytes are PRESERVED**, not deleted at the end of the session, so a routed repair can be
re-measured on the same bytes at $0 without re-recording a seed — the §14 addendum precedent from the
last window, where the re-measure ran on preserved bytes and no seed was re-recorded.

```
path : /Users/danielkeinan/ailibi-smoke-21-14/9p2i        (absolute, outside the repository)
bytes: 5.9 MB — 5 replays (375,531 / 571,738 / 599,802 / 730,389 / 732,306 B),
       MANIFEST.md, roster.json, tournament-eval-report.json
sidecars in the set dir: none
```

`git status --porcelain` shows no replay bytes and no staging directory; the only tracked changes on
this branch are this report and the two standing index amendments.
