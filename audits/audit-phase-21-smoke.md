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

**Three review findings were taken after this reading was first written, and §16 records what each
moved.** Two cells and the projection bracket changed; **none of them is a cell the GO rests on**, and
the corrections make the reading stronger rather than weaker — the B-8 marker now reads 0 over a
denominator 2.3× larger, and the oracle net now runs wider than A-6's published one with an
over-broad floor bounding the false negative. The GO stands unchanged on re-derivation.

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

**The marker pass is a command, not an assertion.** It supplies the evidence for STOP criterion 6 and
therefore for the GO, so it ships here in full rather than being described. It is stdlib-only and
imports nothing from the repo, so an owner or a later re-measure reproduces both columns from the
preserved smoke bytes and the committed record alone. §7.3 carries the script; the two invocations
that produced the table are:

```bash
# the committed reference column — a BARE shell (the committed stamps predate both repair keys)
uv run python /tmp/marker_pass.py replays/samples/9p2i

# the smoke column — the SAME shell discipline as the recording
AILIBI_LAST_SEEN_FROM_SIGHTINGS=1 AILIBI_VENT_SINGLE_MINT=1 \
  uv run python /tmp/marker_pass.py /Users/danielkeinan/ailibi-smoke-21-14/9p2i
```

**And it is calibrated against the register before it is trusted.** Applied unchanged to the four
committed sets it reproduces the published cells exactly: A-6's leak partition **45/326 flag-present
and 0/342 flag-absent** and its **11,727**-utterance denominator; A-17's **3,350** vote prompts with
**0** current-meeting claim lines; A-14's **35,350** recorded actions over **5,960** tick rows; A-3's
**3,602** ballots with **120** carrying the redirect marker; A-31's **1,505** double-minted rows,
**27** distinct heard-only rows and **0** witnessed-only. The same code then produced the smoke column.

| # | repair | marker | committed reference | **smoke (5 seeds / 16 meetings)** | reading |
|---|---|---|---|---|---|
| 1 | A-6 (21.1) | the taught oracle line inside a rendered proof block | 3,186 of 7,211 prompts across the four sets carry `The engine certified` — one in every prompt that renders the block; leak **45/326 = 13.8%** where the block renders, **0/342** where it does not | **0 of 184** prompts carry it, while **51 prompts DO render a `Proof.` block**; banned render vocabulary (`the engine`, `the system`, `the detector`, `certif`, `flag`) **absent from every rendered line** | **OBSERVED** |
| 1b | A-6, spoken | the oracle net over `free_text`, ballot rationales and claim reasons (§7.4 states the net and why it is wider than A-6's prose) | **20 hits / 2,813 utterances** on `samples/9p2i` — exactly A-6's published per-set 20; **80 across the four sets** against A-6's 78, exact on three of the four; leak **45/326** flag-present, **0/342** flag-absent | **0 hits over 306 utterances**; leak **0/6** flag-present, **0/10** flag-absent. The over-broad FLOOR net fires **106 times on these same bytes**, so the scan demonstrably reaches these surfaces — the zero is absence of the register, not a blind detector | **OBSERVED**, directional at this n — the render-side row above carries the weight |
| 2 | A-17 (21.2) | structured testimony rows in the vote-ballot prompts | **0 of 3,350** 9p2i vote prompts carry a `saw:` / `claims:` / `said:` block — the flat render dropped ≥1 field on 3,593 of 3,602 turns | **92 of 92** vote prompts carry ALL THREE, over 546 rendered turn heads | **OBSERVED** |
| 3 | A-14 (21.3) | every recorded action row carries an explicit disposition; queued-behind-trigger actions marked discarded | **0 of 5,960** committed tick rows carry `action_dispositions`; the register re-derived 2,166 of 35,350 = **6.13%** as submitted-with-no-consequence | **101 of 101** tick rows carry it; **56 of 684 = 8.19%** `discarded_by_meeting` across **15** meeting-trigger ticks — `do_task` 23, `move` 23, `wait` 4, `report` 2, **`kill` 2**, `vent` 1, **`emergency` 1** | **OBSERVED** |
| 4 | A-3 (21.3) | guard-redirected ballots carry a machine-readable provenance field | **0 of 3,602** ballots carry `guard_rewrite_reason`; 120 are detectable only by regex over the bracketed display marker | **8 of 92** ballots carry `guard_rewrite_reason` (`under_gate_redirect` 6, `invalid_target` 1, `teammate_coerced` 1); **0** non-`parse_default` rows are missing `guard_redirected_from` | **OBSERVED** |
| 5 | B-8 (21.4) | the belief line's last-seen agrees with the agent's own sightings | `samples/9p2i` **907/2,809 = 32.3%** carry a strictly later sighting, **518/2,809 = 18.4%** stale AND wrong room — against B-8's published 34.4% / 19.6% over the corpus sets | **0 of 602 stale (0.0%)**, **0 of 602 stale-and-wrong-room (0.0%)**; and at the packet layer **520 of 520** belief rows match the observer's OWN packet at that tick, exactly, room and all | **OBSERVED** |
| 6 | A-31 (21.5) | exactly one memory row per witnessed vent; no audible copy past the teammate firewall | **1,505** double-minted rows across the four sets; every distinct witnessed vent double-minted (90/90, 297/297, 20/20, 28/28 = **100%**); 27 distinct heard-only rows, 27/27 impostors | **40 witnessed-vent rows, 0 heard-vent rows, 0 double-minted**; at the PACKET layer **0 `vent_use_heard` events over 517 packet rows**, with 9 witnessed vents each delivered ONCE as the visible action | **OBSERVED** |

Two of the six were additionally cross-checked at a layer below the render.
`observation/service.py::_audible_events` is where the A-31 repair lives, so the observation packets
settle it at the source: **zero `vent_use_heard` events emitted at all**, which makes the 27-row
teammate-firewall residue class *unreachable* rather than merely filtered — the outcome 21.5
specified. And for B-8 the packets are the ground truth for "the agent's own sightings":
**520/520 rendered last-seen rows are something that observer actually perceived at that tick**,
reading BOTH perception channels (`visible_players` and `moved_players`, whose destination is the
placement the render uses).

**The scope and the reproducibility of that cross-check, stated plainly.** It ran over **four of the
five seeds** — 13, 30, 39 and 43, the ones whose packet logs were captured; seed 4's stage had already
been cleaned when the copying began. And those logs are **not preserved**: the wrapper writes each
seed's `<stem>.audit.jsonl` into its DISCARDED stage tree (which is why no set dir carries one), and
that tree is removed when the run finalizes. **So the packet cross-check is recorded here as run, with
its numbers, and it is NOT re-runnable from the preserved bytes.** The primary evidence for every row
of the table above is the byte-level marker pass in §7.3, which IS re-runnable at $0 against the
preserved smoke bytes and the committed record — and it agrees with the packet cross-check on both
rows.

### 7.1 The one repair the five seeds could not exercise

**A-1 / 21.6, the win-ordering repair: UNTESTED**, exactly as the contract predicted at this n. The
repair makes the win check run when the game is decided, meeting-trigger tick or not; no smoke game
reached a state where the ordering could differ. The verifier's note is restated rather than papered
over: the finding is SPECIFIED and test-pinned, and **both realized cases in the committed record
recorded the correct winner** — a latent-correctness repair with zero realized exposure. Its coverage
is `tests/`, not these bytes.

### 7.2 One residual observation, named rather than absorbed

Sixteen of 602 rendered belief rows (2.7%) carry a last-seen tick LATER than any sighting row
**surviving in the same rendered memory block** — e.g. `replay-seed-4` p-3: `p-2: suspicion 0.45 (last
seen in ENGINEERING at tick 17)` while that prompt's own observation rows stop at a tick-13 move.

This is **the opposite direction from B-8** and is not the defect 21.4 repaired. The packet check
settles what it is: the rows are own-eyes and correct — p-2's own recorded trajectory puts it in
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

### 7.3 The marker pass, in full

Stdlib only; imports nothing from the repo. Save as `/tmp/marker_pass.py` and run the two invocations
at the head of §7. Every count in the table above, in both columns, comes out of this one script.

```python
"""The six-behaviour marker pass — stdlib only, no repo import."""
from __future__ import annotations
import collections, json, pathlib, re, sys

TAUGHT = "The engine certified"
BANNED = ("the engine", "the system", "the detector", "certif", "flag")
# A-6's net with the determiner made optional — see §7.4 for why.
NET = (
    re.compile(r"\bengine(?!\s+(?:room|output))\b.{0,200}?(?:certif|flag|proof|say|confirm|seal)", re.I),
    re.compile(r"engine[- ]certif", re.I),
    re.compile(r"\bsystem\b.{0,200}?(?:flag|certif|say)", re.I),
    re.compile(r"\bdetector", re.I),
)
# A deliberately over-broad floor: it cannot false-negative, only over-count.
FLOOR = (re.compile(r"\bengine|\bsystem|\bdetector|certif|\bflag", re.I),)

MEM = re.compile(r"<memory>(.*?)</memory>", re.S)
BELIEF = re.compile(
    r"^- (?P<pid>p-\d+): (?:suspicion [\d.]+ \()?last seen in (?P<room>[A-Z_]+) at tick (?P<tick>\d+)", re.M)
S_IN = re.compile(r"\[tick (\d+)\] You saw (p-\d+) (?:task )?in ([A-Z_]+)")
S_SPAN = re.compile(r"You saw (p-\d+) (?:task )?in ([A-Z_]+)[^\n]*? ticks \d+-(\d+)")
S_MOVE = re.compile(r"\[tick (\d+)\] You saw (p-\d+) move from ([A-Z_]+) to ([A-Z_]+)")
S_VENT = re.compile(r"\[tick (\d+)\] You witnessed (p-\d+) vent in ([A-Z_]+)")
S_KILL = re.compile(r"\[tick (\d+)\] You witnessed (p-\d+) kill in ([A-Z_]+)")
S_SPAWN = re.compile(r"\[tick (\d+)\] You saw every other player in ([A-Z_]+): ([^\n.]+)")
HEARD = re.compile(r"\[tick (\d+)\] You heard a vent use(?: in ([A-Z_]+))?")
TURN_HEAD = re.compile(r"^- \[[^\]]+\] turn \d+ \(", re.M)

def latest_sightings(block):
    out = {}
    def offer(p, t, r):
        if p not in out or t >= out[p][0]: out[p] = (t, r)
    for t, p, r in S_IN.findall(block): offer(p, int(t), r)
    for p, r, e in S_SPAN.findall(block): offer(p, int(e), r)
    for t, p, _s, d in S_MOVE.findall(block): offer(p, int(t), d)
    for t, p, r in S_VENT.findall(block): offer(p, int(t), r)
    for t, p, r in S_KILL.findall(block): offer(p, int(t), r)
    for t, r, mem in S_SPAWN.findall(block):
        for p in re.findall(r"p-\d+", mem): offer(p, int(t), r)
    return out

def between(text, a, b):
    i = text.find(a)
    if i < 0: return ""
    j = text.find(b, i)
    return text[i + len(a): j if j > 0 else len(text)]

def analyse(root):
    seeds = sorted(root.glob("replay-seed-*.jsonl"), key=lambda p: int(p.stem.rsplit("-", 1)[1]))
    prompts = proof = taught = utt = net_hits = floor_hits = 0
    banned = collections.Counter(); net_surf = collections.Counter()
    mf = mu = lf = lu = 0
    votes = v_saw = v_claims = v_said = v_heads = 0
    ticks = ticks_disp = actions = trigger_ticks = 0
    disp = collections.Counter(); disc_kind = collections.Counter()
    ballots = b_marker = b_machine = b_missing = 0; reasons = collections.Counter()
    b_rows = b_check = b_stale = b_stale_room = 0
    w_rows = h_rows = double = 0
    d_w, d_h, d_d = set(), set(), set()
    meetings = ejections = 0; endings = collections.Counter()
    for path in seeds:
        for line in path.open():
            row = json.loads(line); kind = row["kind"]
            if kind == "tick":
                ticks += 1; actions += len(row["actions"])
                d = row.get("action_dispositions")
                if d is not None:
                    ticks_disp += 1
                    for x in d: disp[x] += 1
                    if "discarded_by_meeting" in d: trigger_ticks += 1
                    for a, x in zip(row["actions"], d):
                        if x == "discarded_by_meeting": disc_kind[a.get("type", "?")] += 1
                continue
            if kind == "game_over":
                endings[row.get("reason") or "?"] += 1; continue
            if kind != "meeting": continue
            meetings += 1
            if row.get("ejected_player_id"): ejections += 1
            has_vent = any((f.get("kind") if isinstance(f, dict) else str(f)) == "vent_sighting"
                           for f in row.get("contradictions") or [])
            leaked = False; items = []
            for turn in (row.get("transcript") or {}).get("turns") or []:
                items.append((turn.get("free_text") or "", "free_text"))
                for c in turn.get("claims") or []:
                    r = c.get("reason")
                    if isinstance(r, str): items.append((r, "claim_reason"))  # alibi claims have none
            for b in row.get("ballots") or []:
                ballots += 1; rt = b.get("rationale_text") or ""
                items.append((rt, "ballot_rationale"))
                if "redirected]" in rt or "coerced]" in rt or "normalized]" in rt: b_marker += 1
                reason = b.get("guard_rewrite_reason")
                if reason is not None:
                    b_machine += 1; reasons[reason] += 1
                    if reason != "parse_default" and not b.get("guard_redirected_from"): b_missing += 1
            for text, surface in items:
                utt += 1
                if any(p.search(text) for p in NET):
                    net_hits += 1; net_surf[surface] += 1; leaked = True
                if any(p.search(text) for p in FLOOR): floor_hits += 1
            if has_vent: mf += 1; lf += 1 if leaked else 0
            else: mu += 1; lu += 1 if leaked else 0
            for call in row.get("llm_calls") or []:
                pr = call["prompt"]; prompts += 1
                if "\nProof." in pr or pr.startswith("Proof."): proof += 1
                if TAUGHT in pr: taught += 1
                for w in BANNED:
                    if w in pr: banned[w] += 1
                if "rationale_text" in pr:
                    votes += 1; tx = between(pr, "<transcript>", "</transcript>")
                    if tx:
                        v_heads += len(TURN_HEAD.findall(tx))
                        v_saw += "\n  saw:" in tx; v_claims += "\n  claims:" in tx
                        v_said += '\n  said: "' in tx
                m = MEM.search(pr)
                if not m: continue
                block = m.group(1); seen = latest_sightings(block)
                for bm in BELIEF.finditer(block):
                    b_rows += 1
                    pid, room, tick = bm.group("pid"), bm.group("room"), int(bm.group("tick"))
                    if pid not in seen: continue
                    b_check += 1; ot, orm = seen[pid]
                    if ot > tick:
                        b_stale += 1
                        if orm != room: b_stale_room += 1
                obs = call.get("agent_id") or "?"
                w = {(int(t), p, r) for t, p, r in S_VENT.findall(block)}
                h = set(HEARD.findall(block))
                w_rows += len(w); h_rows += len(h)
                for wt, _wp, wr in w: d_w.add((path.stem, obs, wt, wr))
                for t, r in h:
                    tick = int(t); key = (path.stem, obs, tick, r or ""); d_h.add(key)
                    if any(wt == tick and (not r or wr == r) for wt, _wp, wr in w):
                        double += 1; d_d.add(key)
    pc = lambda a, b: f"{100.0 * a / b:.1f}%" if b else "n/a"
    print(f"\n{root}: seeds {len(seeds)} | meetings {meetings} | ejections {ejections} | {dict(endings)}")
    print(f"  stray *.audit.jsonl: {len(sorted(root.glob('*.audit.jsonl')))}")
    print(f"M1 prompts {prompts}; 'Proof.' blocks {proof}; taught line {taught}; banned {dict(banned)}")
    print(f"   utterances {utt}; net {net_hits} {dict(net_surf)}; FLOOR {floor_hits}")
    print(f"   leak flagged {lf}/{mf}; unflagged {lu}/{mu}")
    print(f"M2 vote prompts {votes} (heads {v_heads}); saw {v_saw}; claims {v_claims}; said {v_said}")
    print(f"M3 tick rows {ticks}; with dispositions {ticks_disp}; actions {actions}; {dict(disp)}")
    print(f"   discarded {disp.get('discarded_by_meeting', 0)}/{actions}"
          f" = {pc(disp.get('discarded_by_meeting', 0), actions)} over {trigger_ticks} trigger ticks {dict(disc_kind)}")
    print(f"M4 ballots {ballots}; display {b_marker}; machine {b_machine} {dict(reasons)}; missing {b_missing}")
    print(f"M5 belief rows {b_rows}; checkable {b_check}; stale {b_stale} = {pc(b_stale, b_check)};"
          f" stale+wrong-room {b_stale_room} = {pc(b_stale_room, b_check)}")
    print(f"M6 witnessed {w_rows}; heard {h_rows}; double {double}; distinct w{len(d_w)} h{len(d_h)}"
          f" d{len(d_d)} heard-only {len(d_h) - len(d_d)}")

for arg in sys.argv[1:]:
    analyse(pathlib.Path(arg))
```

### 7.4 The spoken-oracle net, and why it is wider than A-6's prose

A-6 states its net as `the engine …`, `the system … flag|certif|say`, `the detector`. Transcribed
that literally it finds **72** utterances across the four committed sets against A-6's published
**78** — and the shortfall is entirely in `claim_reason` (39 ballot and 28 free_text hits match A-6
exactly, as does its count of 44 distinct games). Inspecting the misses shows why: A-6's own published
hits include `Engine flags confirm p-2 vented`, `confirmed by system flag` and `corroborated by
engine flags` — determiner-less. **Its prose says "the engine"; its detector plainly did not require
the article.** Dropping the article gives **80** across the four sets against A-6's 78, and per set
**20 / 52 / 3 / 5** against A-6's published **20 / 50 / 3 / 5** — exact on three of the four. That is
the net §7 carries, and it is the wider of the two, so it cannot under-report relative to A-6.

Two further points close Codex's false-negative concern properly, because "my net matches theirs" is
not by itself an argument that a zero is real:

1. **The denominator now matches A-6 exactly.** Counting only claims that CARRY a `reason` (alibi
   claims have no such key) gives 3,602 + 4,523 + 3,602 = **11,727** utterances — A-6's figure to the
   digit. The earlier 12,728 counted 1,001 absent alibi reasons as empty utterances.
2. **The FLOOR net bounds the false negative directly.** A deliberately over-broad pattern — any of
   `engine|system|detector|certif|flag` anywhere, with no context requirement — fires **106 times on
   the smoke bytes** and 827 on committed `samples/9p2i`. So the scan demonstrably reads these
   surfaces and matches on them; the oracle net's zero is the absence of the *register*, not a blind
   detector. Those 106 are the in-fiction and evidence-jargon uses A-6 classes as false positives and
   TIER2 (`the engine room`, `a red flag`, `the task flag`) and which the repair never claimed to
   remove.

Both nets, and the floor, are in the §7.3 script, so all three columns re-run from one command.

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

The inflation is measured **like-for-like on the same five seeds the smoke re-recorded** — seeds
4/13/30/39/43 of `replays/samples/9p2i` carry **740,424** committed tokens over 15 meetings against
the smoke's **885,592** over 16:

| denominator | committed tokens/game | inflation |
|---|---|---|
| **the SAME FIVE seeds** (the like-for-like, and the one this report carries) | 148,084.8 | **×1.1961 (+19.6%)** |
| all 50 committed `samples/9p2i` games | 148,135.8 | ×1.1956 (+19.6%) |
| both 9p2i legs, 200 games | 142,844.1 | ×1.2399 (+24.0%) |

The first two agree to 0.1%, which is the check that the five drawn seeds are not a freak sample.
Per meeting: **55,349.5 smoke vs 49,361.6 on the same five committed — ×1.1213 (+12.1%)**; calls per
meeting are unchanged at 11.5. That is the A-17 repair paying its way: the vote-ballot prompt now
renders each turn's full observation and claim body instead of one line, which is the whole point of
the repair and the dominant new input-token term. **Worth carrying into the record's plan as a
measured fact rather than a surprise.**

**Retries, transport blips, worker diagnostics: none.** Both run logs were scanned for `WARN`,
`ERROR`, `Traceback`, lock, dead-owner and claim diagnostics — **zero matches in either**. No seed
consumed a second attempt of its budget of 8.

**The four-leg projection, re-derived from these measured figures.** Method, stated so 21.15 re-runs
it rather than inherits it: the two 9p2i legs (`samples` 50 + `ml_corpus` 150 = 200 games) are the
roster this smoke actually ran, so they are projected from its own measured SERIAL seconds-per-seed at
two workers, with the bracket's ends the fastest and slowest measured seed rather than a guess; the
two 4p1i legs (100 games, **not smoked**) are projected from the wall the phase-20 record MEASURED for
those same legs (1h29m31s, §0.3) scaled by the ×1.1961 like-for-like inflation above — an inference,
labelled one, and one the projection is insensitive to because the 4p1i legs are 6.4% of the last
record's wall; overhead is carried as the phase-20 record's own realized factor (its window wall over
the sum of its four leg walls, ×1.0009).

| | 9p2i legs (200 games) | 4p1i legs (100 games) | **four-leg total** |
|---|---|---|---|
| low (fastest measured seed, 392 s) | 10h53m20s | 1h47m04s | **12h41m05s** |
| centre (measured mean, 633 s) | 17h34m40s | 1h47m04s | **19h22m47s** |
| high (slowest measured seed, 791 s) | 21h58m20s | 1h47m04s | **23h46m41s** |

**The bracket is 12h41m – 23h47m, centred at 19h23m**, against the phase-20 record's realized
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

## 16. Review round 1 — what each finding moved

Three findings on PR #411, all against this report rather than a code path. Every re-derivation ran
at **$0** against the PRESERVED smoke bytes and the committed record, in the shell discipline §2
records — recording-shell exports for smoke-byte reads, a bare shell for committed-set reads. **No
seed was re-recorded and no preserved byte was touched.**

| finding | disposition | what moved | does the GO rest on it? |
|---|---|---|---|
| **P1 — the marker command is not in the report** | **Taken in full.** §7 now opens with the two invocations and §7.3 ships the whole stdlib-only script. Shipping it also surfaced that the original belief-row pattern required a `suspicion N.NN (` prefix and so skipped rows that render a last-seen without a suspicion scalar. The shipped pattern makes the prefix optional and the row set grows accordingly. | M5's denominators, both columns: committed **401/1,051 → 907/2,809 (38.2% → 32.3%)** stale and **225/1,051 → 518/2,809 (21.4% → 18.4%)** stale-and-wrong-room — the latter now closer to B-8's published 19.6%; smoke **0/263 → 0/602**. §7.2's residual **6/263 → 16/602 (2.3% → 2.7%)**. | **No — and the marker got stronger.** The smoke numerator is still **0**, now over 2.3× the rows. |
| **P1 — re-run the spoken-oracle cell with the registered net** | **Taken, and bounded further than asked.** §7.4 shows A-6's prose says `the engine` while its own published hits are determiner-less, so the net drops the article: **80** hits across the four sets against A-6's 78, exact on three of four sets, and the denominator now reproduces A-6's **11,727** to the digit. A FLOOR net was added to bound the false negative directly. | M1b's committed reference **18 → 20** on `samples/9p2i` (now exactly A-6's published 20) and **72 → 80** across four sets; the smoke utterance denominator **329 → 306**. | **No.** The smoke cell reads **0 under both nets**, and the FLOOR net fires **106 times on the same bytes**, so the zero is absence of the register rather than a blind scan. The leak partition is unchanged at 45/326 and 0/342 committed, 0/6 and 0/10 smoke. |
| **P2 — recompute the projection with the measured inflation** | **Taken in full; the finding was correct.** §11 quoted `samples/9p2i`'s totals in its sentence but derived the multiplier from BOTH 9p2i legs. It is now measured like-for-like on the same five seeds, with all three denominators tabulated so the one in force is unambiguous. | Inflation **×1.240 → ×1.1961**; per-game **+24.0% → +19.6%**; per-meeting **+13.6% → +12.1%**; the 4p1i leg **1h51m00s → 1h47m04s**; the bracket **12h45m–23h51m → 12h41m–23h47m**, centre **19h27m → 19h23m**. | **No.** The projection is operating data for 21.15's plan; no STOP criterion reads it. |

**The verdict is re-derived, not restated: GO, unchanged.** Criteria 1–5 and 7 are untouched by all
three findings. Criterion 6 is the only one any of them reaches, and both cells it reaches — the
oracle marker and the B-8 marker — still read the repaired shape, each now on a wider net or a larger
denominator than before.

One reproducibility limit is recorded rather than papered over: the packet-layer cross-check in §7
(0 `vent_use_heard` over 517 packets; 520/520 belief rows matching their observer's own packet) read
the wrapper's discarded-stage `*.audit.jsonl` logs, which the run removes when it finalizes. Those
numbers stand as recorded but **cannot be re-run from the preserved bytes**. The byte-level marker
pass in §7.3 can, it covers every row of the table, and it agrees with the cross-check on both.
