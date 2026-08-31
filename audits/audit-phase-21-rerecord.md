# Phase-21 maintenance record — baseline 8: four sets on the corrected substrate (Task 21.15)

**Date:** 2026-08-30
**Task:** 21.15 — THE COMBINED RE-RECORD (operator, `$0`): four sets, the record audit, the re-pins
**Branch:** `phase-21-rerecord`, opened from `origin/main` `3b156fee`
**Window opens at:** `4ea88689` — this branch's graduation commit, which IS the substrate this
record captures (§0.6)
**Smoke this record runs on:** [`audits/audit-phase-21-smoke.md`](audit-phase-21-smoke.md) — **GO**,
five seeds, no STOP criterion met, all six corrected behaviours OBSERVED on freshly recorded bytes

---

## What this record is, and what it decides

**Nothing.** This is a maintenance-of-record: it re-records the four committed sets on repaired
bytes at the bumped prompt set, publishes every instrument cell before and after, and declares no
verdict. There is no pre-registration, there are no bars, and no cell below carries one. Every cell
this record publishes is a **published cell**, never a bar, and a cell that moves in a flattering
direction is still only a published cell.

**Baseline 7 is canon by explicit owner override of a FINDING verdict.** The pre-registered rule
returned FINDING because bars 1 and 2 were MISSED
([`audits/audit-phase-20-baseline-7.md`](audit-phase-20-baseline-7.md) §6, §6.1). That read is
immutable and nothing on this branch states or implies that those bars passed.

**And this record supersedes it as the reference recording.** A numbered reference recording is
"one recording of the sample sets under a stated set of behavioural settings" and the ladder tip is
"the newest reference recording" ([`docs/glossary.md`](../docs/glossary.md)), so bytes recorded
under corrected code and a bumped prompt set are a new one. From this merge the ladder tip is
**baseline 8**. Baseline 7 keeps its whole history — the FINDING, the two missed bars, the override
that adopted it anyway — and loses only its claim to be the current recording. Those two paragraphs
are not in tension: the constraint this phase inherited is about the BARS story, not about the tip's
succession, and a document still calling baseline 7 the tip after these bytes land would be the
second source of truth this phase opened against.

**Attribution is impossible by construction.** Every behavioural repair Wave 1a landed, plus the
prompt-set bump, arrives in ONE recording window, so no cell's movement below is attributable to any
single one of them. That is the correct trade — none of these changes is a lever, nothing is decided
on the cells, and buying a 20-hour window per unconditional bug fix would be an expensive answer to
a question nobody needs. The Wave-2 levers get their own record precisely because those DO decide
something. The full co-intervention list is §0.5.

---

## 0. The pre-record projection, the STOP rule, and the actual against them

Everything in §0.1 through §0.6 was written and **committed before the first seed staged**. A
prediction made after the numbers are in is not a prediction.

### 0.1 The projection, re-derived rather than inherited

The smoke states its projection method precisely so this record re-runs it
([`audits/audit-phase-21-smoke.md`](audit-phase-21-smoke.md) §11). Re-run here, from the smoke's
measured figures, it reproduces the smoke's bracket to the second.

**The method, and the inputs it takes.**

| input | value | where it comes from |
|---|---|---|
| per-seed SERIAL wall, 9p2i, two workers | 392 s (min), 632.8 s (mean), 791 s (max) | MEASURED, smoke §11, five seeds |
| 9p2i games this record runs | 200 (`samples/9p2i` 50 + `ml_corpus/9p2i` 150) | `git ls-files`, counted below |
| 4p1i games this record runs | 100 (`samples/4p1i` 50 + `ml_corpus/4p1i` 50) | same |
| phase-20's MEASURED wall for both 4p1i legs | 1h29m31s = 5,371 s | `audits/audit-phase-20-baseline-7.md` §0.3 |
| like-for-like inflation | ×1.1961 | MEASURED, smoke §11, same five seeds |
| overhead | ×1.0009 | phase 20's own realized window-over-legs factor |

The 9p2i legs are the roster the smoke actually ran, so they are projected from its own measured
serial seconds-per-seed at two workers: `games × s_per_seed / 2`. The 4p1i legs were **not smoked**,
so they are projected from the wall phase 20 MEASURED for those same legs scaled by the inflation
above — **an inference, labelled one**, and one the total is insensitive to because the 4p1i legs
were 6.4% of the last record's wall.

```
9p2i  low     200 × 392   / 2 = 39,200 s   = 10h53m20s
9p2i  centre  200 × 632.8 / 2 = 63,280 s   = 17h34m40s
9p2i  high    200 × 791   / 2 = 79,100 s   = 21h58m20s
4p1i  (all)   5,371 × 1.1961  =  6,424.2 s =  1h47m04s
total low     (39,200 + 6,424.2) × 1.0009 = 45,665.2 s = 12h41m05s
total centre  (63,280 + 6,424.2) × 1.0009 = 69,766.9 s = 19h22m47s
total high    (79,100 + 6,424.2) × 1.0009 = 85,601.2 s = 23h46m41s
```

**THE BRACKET, COMMITTED IN ADVANCE: 12h41m05s – 23h46m41s, centred 19h22m47s**, against phase 20's
realized **23h25m42s** for the same 300 games. The re-derivation equals the smoke's own answer, so
this record ADOPTS that bracket having re-derived it rather than having inherited it.

Per leg, so each actual has something to be read against:

| leg | games | low | centre | high |
|---|---|---|---|---|
| 1. `samples/9p2i` | 50 | 2h43m20s | 4h23m40s | 5h29m35s |
| 2. `ml_corpus/9p2i` | 150 | 8h10m00s | 13h11m00s | 16h28m45s |
| 3. `samples/4p1i` | 50 | 53m32s | 53m32s | 53m32s |
| 4. `ml_corpus/4p1i` | 50 | 53m32s | 53m32s | 53m32s |

The 4p1i rows carry ONE figure across all three columns on purpose: their projection is an inference
from a single measured phase-20 wall, not a measured spread, and inventing a bracket around it would
dress an inference as a measurement.

**The bracket is wide by construction.** At `$0` flat-rate billing the wall is hosted-provider
latency, which five seeds measure coarsely and which varies hour to hour. The two measured drivers
of the inflation, both from the smoke and both re-stated here as facts rather than as one surprise:

| | same-five committed | smoke | factor |
|---|---|---|---|
| calls per meeting | 11.20 | 11.50 | ×1.0268 (+2.7%) — a trajectory effect at n=16, **not a repair** |
| tokens per call | 4,407.3 | 4,813.0 | ×1.0921 (+9.2%) — the A-17 render paying its way |
| **tokens per meeting** | **49,361.6** | **55,349.5** | **×1.1213** |

and `1.0268 × 1.0921 = 1.1213` exactly: roughly three-quarters of the per-meeting increase is larger
prompts, roughly one-quarter a higher call rate.

### 0.2 The recording protocol, committed in advance

1. **Order.** `samples/9p2i` → `ml_corpus/9p2i` → `samples/4p1i` → `ml_corpus/4p1i` — the value
   order the baseline-7 record fixed, with the corpus 9p2i leg ahead of both 4p1i legs because that
   is where the conviction cell's denominator is.
2. **Slate.** `--expect-levers ""` on EVERY leg including the `--dry-run` preview. The empty slate is
   correct **only because the graduation commit precedes the first seed**: the smoke recorded its
   bytes under `AILIBI_LAST_SEEN_FROM_SIGHTINGS=1 AILIBI_VENT_SINGLE_MINT=1`, and after the sweep
   those exports must NOT be set, because the repaired render is now the default and those two keys
   no longer exist.
3. **Preview then record.** `--dry-run` first, its resolved-configuration block pasted into §2; then
   the same command without `--dry-run`. A preflight refusal is the guard working: it is reported and
   the run restarted, never worked around.
4. **Aside, not over.** Each set's prior bytes are moved ASIDE before its leg and PRESERVED for the
   duration — both recorders' skip scans treat a present in-range replay as already recorded, and the
   corpus recorder's freeze guard judges every replay against the declared template map, so a
   leftover replay at the old template versions either skips a seed or refuses the freeze at the end
   of a multi-hour leg.
5. **Probe before queueing.** `scripts/measure_baseline.py --honesty` runs on the FIRST completed
   seed of EVERY leg, before the rest of that leg queues. A raise or an unfoldable cell family is a
   STOP. A probe that folds a game with no meetings in it is recorded VACUOUS and re-run, never
   counted as a pass. This is the whole lesson of the previous phase's smoke compressed into an
   ordering rule.
6. **Gate, then push, then next.** After each leg: the validity gate with `--expected-model`,
   `--require-zero-cost` and `--expected-prompt-versions` pinned to v5, all ten checks named
   individually; byte-identical reconstruction under a BARE environment; the recorded substrate
   snapshot diffed against the intended slate key by key; then the completed seed range is
   checkpoint-pushed before the next leg begins. **A partial record is not a baseline** — if the
   window closes mid-run this record stops at a set boundary and says which legs exist.
7. **Every `(deadline_default)` row is a FAILED recording** and its seed re-records, with the cause
   logged AS IT HAPPENS.
8. **`FEATHERLESS_API_KEY`** is sourced from the gitignored repo-root `.env` and never reaches a log,
   a report or the PR beyond the wrapper's own eight-character prefix, which this record keeps none
   of.

### 0.3 The STOP rule, pre-committed

**Expected to MOVE, with direction.** These are the cells the Wave-1a repairs and the v5 prompt set
touch. A move in the stated direction is the record working; a move in the OPPOSITE direction is a
STOP-and-report to the owner before the next leg.

| # | cell | committed reference | expected direction |
|---|---|---|---|
| 1 | prompts carrying the taught oracle line `The engine certified` | 3,186 of 7,211 across the four sets | → **0** (A-6 / 21.1) |
| 2 | spoken-oracle register hits over `free_text` / rationales / claim reasons | 80 across the four sets | → **0 or near it** |
| 3 | vote-ballot prompts carrying a structured testimony row | 0 of 3,350 (`9p2i`) | → **all of them** (A-17 / 21.2) |
| 4 | recorded tick rows carrying `action_dispositions` | 0 of 5,960 | → **all of them** (A-14 / 21.3) |
| 5 | actions recorded as submitted with no consequence | 2,166 of 35,350 = 6.13%, silently | → **marked `discarded_by_meeting`, and countable** |
| 6 | guard-redirected ballots carrying `guard_rewrite_reason` | 0 of 3,602, so all 120 rewrites lacked provenance | → **every rewrite carries it** (A-3 / 21.3) |
| 7 | belief rows whose last-seen is staler than a sighting the same prompt shows | 907 of 2,809 = 32.3% (`samples/9p2i`) | → **0** (B-8 / 21.4) |
| 8 | … stale AND in the wrong room | 518 of 2,809 = 18.4% | → **0** |
| 9 | double-minted witnessed-vent memory rows | 1,505 across the four sets (100% of witnessed vents) | → **0** (A-31 / 21.5) |
| 10 | heard-without-witnessed rows past the teammate firewall | 27, all 27 impostors | → **0, and unreachable rather than filtered** |

**PRE-DECLARED, so a corrected instrument cannot read as a surprise.** Two movements are declared
HERE, before the first seed, precisely so the STOP rule below does not fire on an instrument that got
better rather than a behaviour that got worse.

* **(a) The wait-share cells FALL**, because the action tally stops counting actions the engine
  discarded behind a meeting trigger: crew `0.1046` → approximately `0.0990`, impostor `0.1000` →
  approximately `0.0982` on the committed reference. The declaration is **directional and
  approximate ON PURPOSE** — the exact landing point is a property of the new bytes. Only a movement
  in the OPPOSITE direction, or one materially past the declared magnitude, is a STOP.
* **(b) The `last_seen`-argmax agreement cell reads RED BY CONSTRUCTION on the committed bytes.**
  The old belief line contradicted the same prompt's own sighting rows, so the cell had no honest
  "before" — the corrected render is what makes it readable at all. **It is a repaired INSTRUMENT
  READING, not a behavioural gain**, and §5's before/after table publishes it with that fact IN the
  cell, its denominator stated, and the before column labelled RED-BY-CONSTRUCTION. It is never left
  blank and never back-filled.

**Expected NOT to move.** A named-not-to-move cell that moves further than the smoke's own reading
of it is a **STOP-and-report to the owner before the next leg**, with the recording PAUSED rather
than continued under a note.

| cell | committed reference | smoke, 5 games | tolerance before it is a STOP |
|---|---|---|---|
| I-5 fabricated completion lines | 0.0 (0/308) | 0.0 (0/25) | any non-zero numerator |
| I-8 marker contamination (turns) | 0.0 (0/871) | 0.0 (0/92) | any non-zero numerator |
| I-8 marker contamination (prompts) | 0.0 (0/1,746) | 0.0 (0/184) | any non-zero numerator |
| I-9 singular-persona prompts | 0.0 (0/1,746) | 0.0 (0/184) | any non-zero numerator |
| I-7 movement-origin flags | 0.0 (0/27) | 0.0 (0/4) | any non-zero numerator |
| gate check `no_friendly_fire_kills` | 0 | 0 | any non-zero count |
| gate check `no_betrayal_ballots_or_accusations` | 0 | 0 over 92 ballots | any non-zero count |
| gate check `no_tick_1_kills` | 0 | 0 | any non-zero count |
| gate check `no_railroaded_crew_ejections` | 0 | 0 | any non-zero count |
| recorded cost, every leg | `$0.0000` | `$0.0000` | any non-zero cost |
| the MANIFEST `flags` cell | the twenty-one-key string | — | any difference at all (§4) |
| `impostor_roll_call` in every `game_over` stamp | False | False | any True |

Six of these are zero-numerator cells whose committed reference is exactly zero, so the tolerance is
stated as **any non-zero numerator** rather than as an interval: an interval around zero would be a
tolerance nobody can breach, and a gate nobody can fail is prose.

**Explicitly NOT a STOP**, so nothing below gets stretched into one:

* A directional cell moving the unwelcome way. Nothing is pre-registered here and no cell carries a
  verdict; an unflattering move is published unchanged and routed.
* A repair these bytes never exercise, which is recorded UNTESTED rather than implied green.
* Byte-level difference from the committed record. That is what a corrected substrate MEANS.
* The suite's byte-coupled tests failing between the graduation commit and the record landing —
  §0.6 states why that is structural.

### 0.4 The freeze, and what it permits

From the smoke's GO until this PR merges, nothing may merge into `engine/`, `agents/`, `meetings/`,
`observation/`, `orchestrator/` or the prompt set. The window's start is **the graduation commit**,
because that commit IS the substrate this record captures. §9 lists, from `git log` over the window,
every commit that landed in those trees; the expected list holds **exactly one entry**, and anything
else means the window reopened and the record restarts from the smoke.

Three carve-outs, all sequenced OUTSIDE the window and all stated with their order:

1. **BEFORE the window:** the Wave-1a graduation sweep (§0.6). That commit IS the substrate.
2. **AFTER the last seed:** the win-ordering expiry. `engine.tick.superseded_meeting_tick` and its
   seven call sites are a replay-only inverse that exists to read PRE-repair bytes, so deleting them
   changes no recorded behaviour.
3. **AFTER the last seed:** the `.audit`-stem guard — a read-side parser fix that touches no
   recorded behaviour.

### 0.5 The co-intervention, named in full

Everything below lands in ONE recording window. **No cell's movement in this record is attributable
to any single one of them, and this record does not attempt an attribution.**

| # | change | register entry |
|---|---|---|
| 1 | The oracle voice leaves the templates; prompt set bumped `qwen3_6_27b.v4` → `.v5` (all four templates) | A-6 (21.1) |
| 2 | Structured testimony survives to the vote surface; the redaction stops writing a blank | A-17 (21.2) |
| 3 | The replay stops recording fiction: discarded actions marked, redirected ballots carry provenance | A-14, A-3 (21.3) |
| 4 | The belief line reads every sighting the agent has | B-8 (21.4) |
| 5 | One vent, one record: the double mint and the audible copy past the teammate firewall | A-31 (21.5) |
| 6 | The win check runs when the game is decided, meeting or no meeting | A-1 (21.6) |
| 7 | The two Wave-1a repair gates graduate: flipped unconditional and DELETED (§0.6) | this record |

Item 6 went UNEXERCISED at the smoke's n and is carried as **UNTESTED** there
([`audits/audit-phase-21-smoke.md`](audit-phase-21-smoke.md) §7.1); §7 below reports whether these
300 games reached it.

### 0.6 The graduation commit — what opened the window

`4ea88689`, this branch's opening commit, before any seed staged.

The gate list was **READ from `orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS` at implementation
time**, never copied from a contract, and quoted here. At `3b156fee` the registry held THREE entries;
the comment block that separated them is the source of truth:

| key | kind | disposition |
|---|---|---|
| `impostor_roll_call` | **LEVER** (18.10's impostor-answer template arm) | **STAYS.** Graduating it would flip an unrecorded template arm ON and change every recorded game. |
| `last_seen_from_sightings` | REPAIR gate (21.4) | **GRADUATED — deleted outright.** |
| `vent_single_mint` | REPAIR gate (21.5) | **GRADUATED — deleted outright.** |

Each graduated gate was **deleted OUTRIGHT and promoted nowhere**, which deviates from
[`AGENTS.md`](../AGENTS.md) "Graduation sweeps" on exactly one clause — that the snake_case key stays
in `_RETIRED_ALWAYS_ON_LEVERS`. The deviation is the point: a repair is not a lever, no committed
record ever ran one ON, and deleting rather than retiring is what leaves the stamp keys byte-identical
across the flip. Stated so it is checkable:

```
SUBSTRATE_FLAG_KEYS  before the sweep: 24 keys (21 retired + impostor_roll_call
                                       + last_seen_from_sightings + vent_single_mint)
SUBSTRATE_FLAG_KEYS  after  the sweep: 22 keys (21 retired + impostor_roll_call)
the twenty-one retired keys, and therefore the MANIFEST `flags` cell derived from
them:                                  BYTE-IDENTICAL
```

That equality is the cheapest available proof that the substrate did not move while the bytes did,
and §4 quotes the new `flags` cell against the committed one to close it.

What the sweep deleted, per gate: the local mirror resolver in `orchestrator/replay.py`, the owning
module's `ENV_*` constant, `_*_FLAG_TRUE` frozenset and `*_enabled()` resolver, every
`if <gate>_enabled():` guard collapsed to its always-taken side, the `_TOGGLEABLE_LEVER_RESOLVERS`
entry, the `.env.example` block, the OFF-arm two-arm tests, and the prose in `docs/architecture.md`,
`docs/glossary.md` and `scripts/record_ml_corpus.sh`'s pin block. Two now-dead pieces of plumbing went
with them: `observation.service._ObservedAction.audible_room` (write-only once the audible copy was
gone) and `_audible_events`' `observed_actions` parameter. Every count in the swept prose was
re-derived from the registry rather than hand-typed: **one** live toggle, **twenty-two** stamp keys.

Two goldens a gate had left pinned to the OFF render were re-derived on the flipped one, each moving
exactly the one line the (now retired) diff tests pinned — the old value beside the new:

```
tests/fixtures/memory_rendering/self_location_trail.expected.md
-  - p-4: suspicion 0.60
+  - p-4: suspicion 0.60 (last seen in ADMIN at tick 9)

tests/fixtures/memory_rendering/coalesced_memory_render.expected.md
-  - p-4: suspicion 0.60
+  - p-4: suspicion 0.60 (last seen in ADMIN at tick 10)
```

**Gates run on the sweep commit alone:**

```
uv run pytest tests/meetings/test_lever_registry.py     7 passed
    (the structural gate that fails on any *_enabled collapsed to a bare `return True`,
     so a green run PROVES the sweep was a deletion and not a stub)
uv run python scripts/check_doc_facts.py               exit 0
    "... .env.example agree with 2 sample manifests ... and the 22-lever substrate registry"
    (the registry-versus-.env.example check, which fails on either half surviving alone)
uv run mypy .                 Success: no issues found in 372 source files
uv run ruff check .           All checks passed!
uv run ruff format --check .  401 files already formatted
uv run lint-imports           Contracts: 4 kept, 0 broken.
```

**And one deviation from the contract's own DoD, reported rather than papered over.** That DoD asks
for `bash scripts/check.sh` GREEN on the sweep commit before the first seed. **It cannot be, and the
reason is the disease this record exists to cure.** On the sweep commit `uv run pytest` reads:

```
5,620 passed, 20 skipped, 3 xfailed, 9 failed, 36 errors
```

and every single red is one class: a test that **re-renders the COMMITTED (pre-repair) replay
bytes** — `tests/meetings/test_prompt_byte_golden.py`'s reconstruction walk and the seven
committed-bytes census suites that ride it. Those bytes were recorded under the OFF render, which
this build can no longer produce; `.env.example` said so in as many words before the sweep deleted
the block ("a re-render under the gate diverges from their recorded bytes"). The suite returns to
green when the NEW bytes land, and it cannot return to green before then. The reds are enumerated in
§10 and re-run in §8 once the record is complete. The same nine failures and thirty-six errors all
PASS at `3b156fee`, verified by running them there, so the class is the graduation and nothing else.

---

## 1. THE VERDICT: the record is COMPLETE at 300 of 300 games, and it mints baseline 8

**All four sets are recorded, gated and FROZEN. The ladder tip is baseline 8.**

The record did not get there in one pass, and §1.1 narrates the interruption as the history it is
rather than smoothing it away. The sequence, dated:

| when (UTC) | what |
|---|---|
| 2026-08-30 18:07 | leg 1 opens — `samples/9p2i`, first seed recorded alone for the honesty probe |
| 2026-08-30 21:17 | leg 1 complete and gated |
| 2026-08-30 21:26 → 2026-08-31 05:31 | leg 2 — `ml_corpus/9p2i`, 150 games, FROZEN |
| 2026-08-31 05:33 → 05:58 | leg 3 — `samples/4p1i`, complete and gated |
| 2026-08-31 05:59 → 06:26 | leg 4 reaches 49 of 50 seeds, then **STOPS** on a provider refusal (§1.1) |
| 2026-08-31 06:26 | the record is reported INCOMPLETE and the branch is checkpointed at 299/300 |
| 2026-08-31 06:40 | the owner clears the account; the leg resumes on the ONE missing seed |
| 2026-08-31 06:45 | leg 4 complete and FROZEN — **300 of 300** |

**The MANIFEST dates straddle midnight, and that is chronology rather than inconsistency.**
`samples/9p2i` records `2026-08-30`; `samples/4p1i` and `ml_corpus/4p1i` record `2026-08-31`; and
`ml_corpus/9p2i` carries BOTH, because its 150 seeds ran across the boundary. A four-leg record that
takes twelve hours cannot share one date unless it starts after midday.

### 1.1 The STOP that interrupted leg 4, as it happened

Seed 1049 exhausted its whole retry budget on a hard `HTTP 402` from Featherless:

```
Featherless chat-completions POST failed: HTTP 402 (model='Qwen/Qwen3.6-27B'):
  {"error":{"message":"Insufficient credits. Available balance is -0.001503532 USD.
   Add credits to continue.","type":"invalid_request_error","code":"insufficient_credits"}}
```

**8 attempts with escalating backoff (60 s, 75 s, 90 s, 105 s …), every one the same 402** — not a
transient, and the message named its own remedy. The remedy was an account action, which the operator
does not take, so the recording stopped, the 49 recorded seeds were checkpointed as an explicitly
UNFROZEN partial, and the reading was reported to the owner with the branch left at 299/300.

**Once the owner cleared the account the resume cost ONE seed, not a leg**, because the recorder's
skip-scan re-proves each present replay's provenance before trusting it: 49 verified, seed 1049
recorded in the same pass, then the finalize — the 50-game eval report, `splits.json` at 30/10/10,
and the FROZEN line. Seed 1049 hit no 402 on the retry.

**What the `$0.0000` claim does and does not cover.** Every recorded game on all four sets carries
`cost_usd 0.0`, and the MANIFEST rows read `0.0000` throughout — the flat-rate substrate held exactly
as declared. The 402 was an **account-balance** refusal (a balance of **-0.0015 USD**), not a
per-token charge against this record. Both facts are true and this audit states both rather than
letting the zero-cost claim imply the account was in good standing throughout.

## 2. The legs, as recorded, against the projection committed in §0.1

| leg | set | games | ACTUAL | low | centre | high | reading |
|---|---|---|---|---|---|---|---|
| 1 | `samples/9p2i` | 50/50 | **3h07m00s** | 2h43m20s | 4h23m40s | 5h29m35s | inside, near the LOW end |
| 2 | `ml_corpus/9p2i` | 150/150 | **7h59m32s** | 8h10m00s | 13h11m00s | 16h28m45s | just BELOW the low end |
| 3 | `samples/4p1i` | 50/50 | **23m15s** | 53m32s | 53m32s | 53m32s | well below (an INFERENCE, not a measurement) |
| 4 | `ml_corpus/4p1i` | **49/50** | 24m41s (incomplete) | 53m32s | 53m32s | 53m32s | ABANDONED on the provider refusal |
| | **total** | **299/300** | **11h54m28s** | 12h41m05s | 19h22m47s | 23h46m41s | **below the low end** |

**The projection was too slow, and the reason is nameable.** The bracket was built from the smoke's
five measured seeds (392 / 632.8 / 791 s serial). Over 200 real 9p2i games the per-seed serial wall
ran faster and tighter than that five-seed sample suggested — observed seeds landed at 215–644 s with
most between 230 and 450. Five seeds measure hosted-provider latency coarsely, which §0.1 said in
advance; this is that coarseness resolving in the favourable direction, and it is recorded as
operating data rather than as a finding.

The two 4p1i rows carry one figure across all three columns because their projection was an
**inference** (phase 20's measured 4p1i wall scaled by the smoke's like-for-like inflation), never a
measurement — labelled as such in §0.1 before the first seed, and the total was insensitive to it
exactly as predicted.

## 3. The gates, per leg

`scripts/refresh_samples.sh` invokes the validity gate nowhere and prints no acceptance block, so the
samples legs were gated by the operator by hand; the corpus recorder prints its own.

| check | leg 1 `samples/9p2i` | leg 2 `ml_corpus/9p2i` | leg 3 `samples/4p1i` | leg 4 |
|---|---|---|---|---|
| `all_games_reach_game_over` | PASS 50/50 | PASS 150/150 | PASS 50/50 | not gated |
| `meeting_rate_and_resolution` | PASS 1.0; 151 resolved, 0 unresolved | PASS 1.0; 439 resolved, 0 unresolved | PASS 0.78; 39 resolved, 0 unresolved | not gated |
| `no_duplicate_meeting_rows` | PASS 0 of 151 | PASS 0 of 439 | PASS 0 of 39 | not gated |
| `no_tick_1_kills` | PASS 0 | PASS 0 | PASS 0 | not gated |
| `no_friendly_fire_kills` | PASS 0 | PASS 0 | PASS 0 | not gated |
| `no_betrayal_ballots_or_accusations` | PASS 0 over 869 | PASS 0 over 2,516 | PASS 0 over 0 | not gated |
| `no_railroaded_crew_ejections` | PASS 0 over 2,771 | PASS 0 over 7,656 | PASS 0 over 67 | not gated |
| `no_dangling_primary_reason_id` | PASS 0 over 869 | PASS 0 over 2,516 | PASS 0 over 117 | not gated |
| `cost_and_provenance_exact` | PASS, 4 prompt versions, 50 games | PASS, 4 prompt versions, 150 games | PASS, 4 prompt versions, 50 games | not gated |
| `byte_identical_reconstruction` | PASS 0 drifted | PASS 0 drifted | PASS 0 drifted | not gated |
| **gate exit** | **0** | **0** | **0** | — |
| BARE-shell `verify_samples.sh` | clean | `All 150 samples verified clean` | clean | not run |
| `*.audit.jsonl` in the set dir | 0 | 0 | 0 | 0 |

Every gate ran with `--expected-model Qwen/Qwen3.6-27B --require-zero-cost` and the 21.10 CLI pin
`--expected-prompt-versions` naming all four templates at **v5**. Reconstruction was verified in a
**BARE** shell with no `AILIBI_*` lever export, which is what the recorded stamps agree with.

Leg 2's freeze wrote its FROZEN line at `git_sha fed22c25` with the split rule unchanged
(`seed mod 5: {0,1,2}=train, {3}=val, {4}=test`) and `splits.json` at **90 train / 30 val / 30 test**.

## 4. The recorded substrate stamp — read out of the `game_over` rows, not the launching shell

| set | games | distinct stamps | keys | ON | OFF | `substrate_slate_mismatches` |
|---|---|---|---|---|---|---|
| `samples/9p2i` | 50 | 1 | 22 | the twenty-one retired levers | `impostor_roll_call` | `[]` |
| `ml_corpus/9p2i` | 150 | 1 | 22 | the twenty-one retired levers | `impostor_roll_call` | `[]` |
| `samples/4p1i` | 50 | 1 | 22 | the twenty-one retired levers | `impostor_roll_call` | `[]` |
| `ml_corpus/4p1i` | 49 | 1 | 22 | the twenty-one retired levers | `impostor_roll_call` | `[]` |

**The `flags` cell of every new MANIFEST row is BYTE-IDENTICAL to the committed twenty-one-key
string**, verified against the preserved baseline-7 bytes, which stamp the same 22 keys with the same
one False. That equality is the cheapest available proof that **the substrate did not move while the
bytes did** — the graduation deleted its two repair keys outright rather than retiring them into
`_RETIRED_ALWAYS_ON_LEVERS`, so the retired half never grew.

## 5. The re-record log, with causes, as they happened

| # | leg | seed | cause | repair |
|---|---|---|---|---|
| 1 | 1 | 8 | `deadline_default` at tick 8, meeting-0 — the vote ballot validated short (`primary_reason_observation_id` returned where `primary_reason_id` is required); p-1's ballot defaulted | re-recorded, 345 s |
| 2 | 2 | 1072 | `deadline_default` failed-call row — the turn was DEFAULTED, so the transcript carried a fallback husk rather than model output | re-recorded, 347 s |
| 3 | 2 | 1079 | same | re-recorded, 439 s |
| 4 | 2 | 1144 | same, **plus** the `(deadline_default)` sentinel recorded as a non-baseline model | re-recorded, 422 s |
| 5 | 3 | 32 | `deadline_default` at tick 8, meeting-0 — the same ballot shape as #1 | re-recorded, 50 s |

**Five re-records over 250 completed games**, against the baseline-7 record's 2 of 150 and the
baseline-6 record's 10 of 150. Every one was found by a guard rather than by inspection: legs 1 and 3
by the operator's `deadline_default` watch (the validity gate has no check for it), leg 2 by
`check_replay_provenance` refusing the freeze at the end of a multi-hour leg — *presence alone must
never make it a corpus game*, in the guard's own words.

**Three of the five are ONE model-output shape**, named here rather than left as five unrelated
incidents: against the v5 `vote_ballot` schema this model recurrently emits
`primary_reason_observation_id` where `primary_reason_id` is required, the ballot fails validation,
and the vote defaults. It costs a re-record each time and never reaches committed bytes. **Routed,
not fixed here** — the prompt set is frozen for the recording window.

**Two `failed_call` rows SURVIVE in the committed bytes, published rather than swept.**
`ml_corpus/9p2i` seeds 1012 and 1093 each carry one `error_type=ValidationError` row: a malformed
`MeetingTurn` the model emitted, recorded at the baseline model with `$0` cost and retried inside the
turn. These are **not** `deadline_default` — the recorder declares recorded parse failures non-fatal
and `check_replay_provenance` accepts them. The standing re-record rule names the defaulted class,
and this is not it, so re-recording them would be widening a rule rather than following it.

## 5.2 An operating note: the abandoned staging directory, and the recorder bug behind it

**What was found.** After the record completed, `replays/ml_corpus/9p2i/` still held
`.ailibi-corpus-stage-DMASrP/` — the corpus recorder's own `mktemp` staging directory from this
record's leg 2. It is **gitignored**, so `git status` is blind to it and it would have ridden the
merge invisibly. It surfaced only because `tests/scripts/test_record_ml_corpus.py::
test_preflight_refuses_fake_provider_at_the_committed_corpus_tree` globs the committed set dir and
failed on it.

**What it was, verified before anything was removed.** Deleting inside `replays/` is not something to
do on inference, so the directory was audited first:

```
tracked files in the stage                    0   (gitignored: git status --porcelain --ignored -> !!)
replay-seed-*.jsonl anywhere inside it        0
contents                                      .next_idx, .state/completed, .state/meetings
.state/completed                            150   (the full leg-2 slate)
.state/meetings                             150
.next_idx                                   150
.failed                                   ABSENT   (the leg did not fail)
total size                                  12K
committed replays in the set                150   (all promoted; the set is whole and FROZEN)
```

Every replay had been promoted out; what remained was three counter files. Removing it lost nothing,
and `find replays -type d -name '.ailibi-*stage*'` now returns none. The test is green.

**The bug, ROUTED rather than fixed here.** `scripts/record_ml_corpus.sh` creates the stage at
`:1296` and arms `trap "rm -rf '$stage_dir'" RETURN` at `:1301` — so a stage dir surviving a
**successful** promotion means that trap does not fire on at least one exit path. The recorder is
frozen for this record's window and is out of this task's scope, so the defect is recorded here for
the close ledger rather than patched:

> **Routed:** the corpus recorder can leave its `mktemp` staging directory behind after a successful
> record (`scripts/record_ml_corpus.sh:1296` / the `RETURN` trap at `:1301`). Because the path is
> gitignored, neither `git status` nor a review sees it; the only thing that catches it is a
> committed-tree test globbing the set dir. Either the trap needs to cover every exit path, or the
> finalize needs an explicit sweep.

## 5.1 The published cells

**These are PUBLISHED CELLS, not bars.** This record pre-registered nothing, so nothing below carries
a verdict, a target, or a pass/fail. They are published in the shape the front door's fact checker
reads precisely so the front door quotes a committed source rather than a remembered one.

**And the ladder tip stands at baseline 8.**

### Published cell 1 — non-direct conviction accuracy

The ejections the crew reached WITHOUT engine-certified proof of the ejectee's role. Baseline 7's
pre-registered bar 1 was measured on this cell and **MISSED** it; that read is immutable and this
record does not re-price it.

| set | before | after |
|---|---|---|
| `samples/9p2i` | 16/30 = 0.5333 | **14/27 = 0.5185** [0.3399, 0.6926] |
| `ml_corpus/9p2i` | 42/68 = 0.6176 | **32/61 = 0.5246** [0.4016, 0.6447] |
| `samples/4p1i` | 1/2 = 0.5000 | **1/5 = 0.2000** [0.0362, 0.6245] — ADVISORY |
| `ml_corpus/4p1i` | 2/3 = 0.6667 | **3/3 = 1.0000** [0.4385, 1.0] — ADVISORY |
| **pooled** | **61/103 = 0.5922** | **50/96 = 0.5208** [0.4224, 0.6178] |

**The cell FELL, and it is published unchanged.** 0.5922 → 0.5208 pooled. That is the unflattering
direction, on the very cell baseline 7's missed bar 1 was about. Three things are true at once and
the record states all three: nothing was pre-registered here so nothing is missed; the fall is inside
overlapping intervals and this record has no power to call it real; and a maintenance record does not
get to route an unwelcome number away. **It is the Wave-2 record's to rule on, not this one's.**

The direct-proof cell stays perfect and grew: **333/333 = 1.0000** pooled (68 + 220 + 19 + 26),
against 326/326 before.

### Published cell 2 — innocent ejections

| set | before | after |
|---|---|---|
| `samples/9p2i` | 14 | **13** |
| `ml_corpus/9p2i` | 26 | **29** |
| `samples/4p1i` | 1 | **4** |
| `ml_corpus/4p1i` | 1 | **0** |
| **pooled** | **42** | **46** |

**The count ROSE, 42 → 46, and it is published unchanged** — the same reading as cell 1, on the cell
baseline 7's missed bar 2 was about. Every innocent ejection still sits inside the non-direct cell:
the proof-present cell is innocent-free on both records, 0 of 333 here and 0 of 326 before.

### The win split

| set | baseline-7 impostor rate | baseline-8 impostor rate |
|---|---|---|
| `samples/9p2i` | 24% (12/50) | **30% (15/50)** |
| `samples/4p1i` | 36% (18/50) | **36% (18/50)** |
| `ml_corpus/9p2i` | 24% (36/150) | **24% (36/150)** |
| `ml_corpus/4p1i` | 26% (13/50) | **26% (13/50)** |

Three of four sets are unchanged to the game. Only `samples/9p2i` moved, by three games.

### What moved that §0 did NOT pre-declare, named rather than buried

§0.3 pre-declared ten cells expected to move and twelve expected not to. **All twelve
named-not-to-move cells HELD.** The cells below moved that §0 named in neither list, and this
record's honest position is that they are un-pre-declared movements on a maintenance record whose §0
says in as many words that "a directional cell that moves the unwelcome way" is explicitly NOT a
STOP. They are reported to the owner here, in the record, before the merge that ratifies it, rather
than being discovered downstream.

### 5.1.1 The sole-flag wrongful-conviction class RE-OPENED — 0 → 4

**This is the finding on this page that most deserves the owner's attention, because it re-prices a
stated ground of the baseline-7 adoption.** That record's §6.1 rested partly on the reading that the
class which convicted seventy innocents *no longer existed on those bytes*. On baseline 8 it is back:

| cell | before | after |
|---|---|---|
| sole-flag wrongful-conviction victims | **0** | **4** — all four CREWMATES |
| … still carrying a STRONG flag under the full slate | **0** | **1** |

Four is a small number and this record has no power to call it a trend. But "the class is extinct"
and "the class has four victims" are different claims, and only one of them is now true. **It joins
the accuracy fall and the innocent-ejection rise as Wave-2 input, and no surface may keep asserting
the extinction.**

### 5.1.1a TWO FINDINGS, and what was done with each

**FINDING 1 — `samples/9p2i` seed 41, meeting 2: a CREWMATE convicted on STRONG statement-pair
evidence.** It ejects **p-9, a crewmate**, on five flags, **two of them STRONG `alibi_vs_sighting`**.

`tests/api/test_evidence_mechanisms.py` asserted `found == []`: that NO committed meeting convicts on
a STRONG statement-pair flag naming the ejected player. It now finds one meeting carrying two such
flags. Re-pinning `found` to a bare two-element list would have gutted the property, so the test was
**converted to a named tripwire on GROWTH** instead, in the shape the repo already uses for
classified divergences: a frozenset naming `headless-seed-41:meeting-2`, where a meeting **outside**
the set fails and one **leaving** it fails too. The loss is asserted rather than tolerated — the test
pins that the ejectee is a CREWMATE and that both flags are `alibi_vs_sighting` — and the planted
case still proves the predicate fires. **The property survives; what changed is that it now has a
victim to name.**

**This class held at ZERO on baseline 7 and re-opened at one meeting on baseline 8.** It is the same
family as §5.1.1's sole-flag re-opening (0 → 4): the corrected substrate convicts innocents in ways
the previous record described as closed. **Wave-2 rules on both; no surface may keep asserting the
closure.**

Two of the four audit exhibits move with it, and they moved in opposite directions:

* **seed 23 M1 — still FLIPPED.** The mechanism's flag is DEMOTED rather than absent: two survive,
  both weak-banded, and the table still skips. The conviction the exhibit is about does not happen.
* **seed 12 M0 — PARTLY FLIPPED, and the exhibit now says so.** Its evidence half held (the fatal
  STRONG flag is still gone, both survivors weak-banded) but its outcome half regressed: the meeting
  **ejects the crewmate p-5**, where the previous recording skipped. The exhibit's original claim,
  "no longer ejects an innocent", is FALSE on these bytes. Its status moved `FLIPPED` →
  `PARTLY FLIPPED`, its test was renamed to pin the regression rather than the claim, and the
  status-set check now enumerates the allowed values so a status nobody defined still fails.

### 5.1.1c THE CURATED FEATURED HEAD NO LONGER SHOWS WHAT ITS CARD PROMISES

**The first card a visitor clicks is now falsified by these bytes, in both halves of its blurb.**
`FEATURED_GAMES[0]` is `9p2i` seed 2, and its curated label reads:

> "One meeting decides the whole game, and every contradiction on the table is stamped a weak
> signal. Watch a room reason with nothing solid in front of it."

| | baseline 7 | baseline 8 |
|---|---|---|
| meetings | 1 | 1 |
| contradictions | **3, all `weak_signal`** | **0** |
| outcome | EJECTED p-5 | **SKIPPED — nobody ejected** |

"One meeting **decides** the whole game" is false: the meeting now skips and decides nothing. "every
contradiction on the table is stamped a weak signal" is false: there are no contradictions on the
table. Seed 2 is the ONLY zero-flag game in `samples/9p2i`, and it is the one the strip leads with.

**This is caught by a real gate, not by reading.** `frontend/e2e/journey.spec.ts:449` walks the
featured head as a spectator and asserts the evidence surface is non-vacuous, with the reason written
into the test: *"the count is read rather than pinned, because a re-record can move it, but it may
not fall to zero."* It fell to zero, so the CI journey fails.

**Not fixed here, and deliberately not worked around.** The contract routes the curated strip
explicitly — it is "re-watched, not re-curated: a blurb this record falsifies is named in the audit
and routed to the post-record results task, because Wave 2 replaces these bytes again". Re-curating
is out of scope; weakening the e2e non-vacuity check to reach green would delete a guard that is
doing exactly its job. So the finding is escalated with the record rather than absorbed by it.

**OWNER RULING (2026-08-31, orchestration thread): OPTION 2 — rewrite the card, keep the selection.**
The head stays `9p2i` seed 2; its copy is repaired to the truth. This is a description repair, not a
re-curation: the game is still a good exhibit, and on the corrected substrate it is arguably a better
one — a room with nothing in front of it, where the old substrate would have railroaded. As shipped:

> "The only meeting of the game, and nothing on the table: not one account that contradicts another.
> Watch a room work out what to do with no evidence at all."

**Two constraints this edit had to clear, both recorded rather than assumed.**

1. **`ReplayPicker.tsx` carries a standing prohibition** — 19.10's contract "explicitly forbids copy
   changes in this file". The owner ruling is an explicit supersession of it, and the file's own
   comment now says so. The distinction that makes the supersession coherent: a label that has become
   FALSE is not the copy-churn that rule exists to stop — the same failure the file already records
   against the blurbs before it.
2. **The BINDING spoiler rule survives untouched.** Each label must name the setup and the question,
   "never its answer: no winner, no ejection, no vote tally". A first draft ended "and send nobody out
   the airlock", which states the meeting's outcome and would have breached it. The shipped line ends
   on the question instead.

**The guard moved with the exhibit rather than dying with it.** `journey.spec.ts` had pinned
`declaredTotal > 0`, which encoded the OLD head. It now reads the head card's own promise and holds
the render to it **in both directions**: a card promising nothing on the table must open onto zero
evidence, and a card promising anything else must open onto evidence that is actually there. A
mismatch either way is red. Two further assertions keep it non-vacuous — the transcript's turn cards
must have rendered, so "no evidence" cannot be satisfied by a dialog that rendered nothing.

**The perturbation was run, not merely written.** Rewriting the card to claim "three accounts that
cannot all be true" over the same unchanged bytes turns the journey RED; restoring the truthful copy
turns it green. A sibling test constructs both mismatch directions against the real rendered meeting
so the property is pinned in the suite rather than only in this paragraph.

### 5.1.1b THE I-13 INJUSTICE FIXTURES: 4/4 FLIPPED becomes 3/4 flipped + 1 partial

**This is the fourth movement against the justice cells, and it lands on a stated ground of the
baseline-7 adoption.** That record's **Bar 8** read the four I-13 injustice fixtures as **4/4
FLIPPED** and its §4 walked them one by one. On these bytes:

| fixture | baseline 7 | baseline 8 |
|---|---|---|
| (a) provenance-impossible sighting — `9p2i` seed 23 M1 | FLIPPED | **FLIPPED** (flags demoted to weak; table still skips) |
| (b) content-vs-own-memory miss — `9p2i` seed 12 M0 | FLIPPED | **PARTLY FLIPPED** — evidence half held, outcome half regressed: **ejects the crewmate p-5** |
| (c) one-tick interval artifact — `4p1i` seeds 49 + 41 M0 | FLIPPED | **FLIPPED** |
| (d) equal-weight conflict — `4p1i` seed 41 M0 | FLIPPED | **FLIPPED** |
| | **4/4** | **3/4 flipped + 1 partial** |

**Read together, the justice picture this record hands forward is one improvement and four
regressions**, and they should be priced as a set rather than one at a time:

1. non-direct conviction accuracy **fell** 0.5922 → 0.5208 (§5.1);
2. innocent ejections **rose** 42 → 46 (§5.1);
3. the sole-flag wrongful-conviction class **re-opened** 0 → 4 (§5.1.1);
4. the STRONG statement-pair conviction class **re-opened** 0 → 1 meeting, ejecting a crewmate
   (§5.1.1a);
5. and against those, the oracle-register leak class went to **ZERO** on all four sets (§5.1.2c) —
   the one unambiguously good movement.

Nothing here is a bar and nothing is decided. But the four regressions are on the cells the Wave-2
pre-registration will be written against, and a pre-registration priced on "these classes are
closed" would be priced on a reading these bytes no longer support.

The seventh-adjacent failure is the same meeting seen from the classifier's side:
`test_rederivation_diverges_only_at_the_repaired_sites` finds one unnamed divergence class, at seed
41 M2, where a recorded `alibi_vs_sighting` flag re-derives identically **except** that it gains
`[weak signal: single grounded source]`. The cause is a knock-on of the movement channel — the
sibling pairing cannot be re-derived, so the alibi falls from two grounded sources to one — and the
classifier misses it because its helper scans only the flag's own turns while the `saw_move` lives in
turn 0. Widening that helper is a test-logic change and was not made under a record.

**This finding is the same family as §5.1.1's re-opened sole-flag class.** Both say the corrected
substrate convicts innocents in ways the previous record had described as closed. **It is Wave-2's to
rule on, and no surface may keep asserting the closure.**

**FINDING 2 — the watchability geomean reads 0.0 because ONE extractor self-check fails.**
`test_historical_15_2_geomean_parity_frozen_pin_on_9p2i` fails against a committed artifact reading
mean 0.0, median 0.0, **all 50 games floored**. That artifact is NOT corrupt: re-running the
documented rubric path reproduces it exactly, and the copy committed at leg 1 is byte-identical to a
fresh regeneration. The floor is real and its cause is precise:

```
re-derived genuine-class == shipped compute_genuine_class_conversion
  (supplied 1/0, converted 0/0): FAIL
```

`experiments/lab/rubric_score.py::_facts_integrity_ok` floors EVERY game on any self-check FAIL, and
exactly one fails — a one-row disagreement between the extractor's re-derivation of the genuine-class
conversion and the shipped instrument's (supplied 1 versus 0). So a single disagreeing row zeroes the
whole watchability geomean.

**The production instrument disagrees with the lab scorer on the same bytes**: `eval/watchability.py`
reads `samples/9p2i` at geomean mean **48.57** / median **55.85** and its referee PASSES. Three
derivations, one outlier.

**It is NOT a stale pin, which is what decides the disposition.** Both sides of the failing check are
computed at runtime from the current bytes — `genuine_supplied_rederived` against
`shipped_genuine.supplied` — so there is no frozen expectation to re-derive. The extractor's
mechanism and the shipped instrument's mechanism disagree about what the genuine class contains on
these bytes. Re-pinning is not available; reconciling two live derivations is a code change in
`audits/workflows/extract_gameplay_facts.py` or `eval/vote_correctness.py`, and neither is in this
record's scope.

**So the rubric refresh is declared INCOMPLETE**, by the mechanism the recorder itself declares for
exactly this (`scripts/refresh_samples.sh:1048-1074`: a rubric that cannot be regenerated cleanly
makes the refresh incomplete and uncommittable). Concretely: **the three rubric artifacts are NOT
shipped at their 0.0 reading.** `experiments/lab/results-rubric-score.json`,
`experiments/lab/results-rubric-geomean.json` and `replays/samples/9p2i/results-rubric-score.json`
are left at their previous content, which makes the served rubric read STALE against the new
MANIFEST — the honest signal, and the one the freshness banner exists to give. A mean of 0.0 that a
sibling instrument reads at 48.57 is a scorer artifact, not a fact about the bytes, and publishing it
as a served measurement would be the defect this phase opened against.

**Two routed items, not one:**

> **Routed (a):** reconcile the genuine-class derivation — the extractor's re-derivation and
> `compute_genuine_class_conversion` disagree by one supplied row on the baseline-8 bytes. Until they
> agree, the 9p2i rubric cannot be regenerated and the served rubric stays stale.

> **Routed (b), independent of (a):** the robustness defect. `_facts_integrity_ok` floors EVERY
> game's score to zero on ANY single self-check FAIL, so one disagreeing row zeroes a whole
> recording's watchability geomean with no partial signal and no named cause in the artifact. That
> is a scorer bug in its own right and outlives whichever way (a) is resolved.

### 5.1.2 The other five movements, with their direction stated

| # | cell | before | after | reading |
|---|---|---|---|---|
| b | STRONG `alibi_vs_sighting` prosecution class | 11 OFF / 12 with the movement lever | **21 / 27** | grew; more prosecutions ride this class |
| c | oracle-register leak class, all four sets | non-zero | **ZERO** | **the one unambiguously good movement** — the A-6 dialect fix working. Denominators kept beside the zeroes so the cell cannot read as an empty scan |
| d | impostor false-whereabouts arm | commented as ~twice the crew rate | **0/106 impostor vs 6/660 crew** | **INVERTED.** The old comment was backwards and is corrected, not re-explained |
| e | `weak_flag_only_impostor` on `samples` | 0 | **1** | "every weak conviction was innocent" now holds only on the corpus set |
| f | `_COALESCED_ROW_PIN` | 37.05 | **36.59** | **MARGIN WATCH.** The falsification floor is 36.0, so the margin fell 1.05 → 0.59. Another re-record of similar size could flip what that test means. Ledgered, not adjusted |

Item (c) is the only movement in this record that is unambiguously an improvement, and it is stated
as one cell rather than allowed to colour the rest.

## 6. What this record does NOT discharge

The post-record tail this task owned IS discharged: the byte-coupled re-pin sweep (the census
re-derived at **46** files under `tests/` and **97** repo-wide — the repo-wide grep emits paths with
no leading `./`, so the exclusions filter on the bare prefix or they silently miss and report 101),
both frontend fixtures and their census tests, the `baseline-8` floor block and
`_DEFAULT_BASELINE_ID`, the ladder-tip move, the record-read parser widening with its perturbation
cases, the declared grounding gap's corpus digest, the corpus README's whole Capability-disclosures
section and leg table, the win-ordering expiry, the `.audit`-stem guards,
`verify_action_dispositions`' adoption, the prompt-archive retirement, and the before/after
instrument cells.

What this record deliberately does NOT discharge:

1. **The ML re-ground and the campaign tier.** The committed fits were made on a corpus this record
   replaced; the declared grounding gap now names the new pair of digests, and 12 rows report STALE
   by design. Task 21.17 owns the re-fit that deletes the amnesty.
2. **The Wave-2 lever record.** Every cell here is published, none is a bar; the decisions belong to
   that record.
3. **The narrative half of the front door.** Only the cells the doc-fact gates force were moved.
4. **The corpus recorder's header duration note**, and the recorder's leftover-stage-dir bug (§5.2).
5. **The mixed-vintage before-column in the results tables.** README and the reading guide carry a
   history column headed "At baseline 6" whose rows are now a mix of vintages. Fixing it properly
   means moving `_BEFORE_COLUMN_HEADER`, `_PROOF_PARTITION_AUDIT` and the parser in ONE commit — the
   contract already routes it (`tasks/phase-21.md:6613`, `:6645`), and splitting it across two tasks
   would leave the checker reading one vintage against another.
6. **`README.md:29`'s phases-0-19 / 20-open contradiction** — pre-existing, unrelated to these bytes,
   named here so the ledger carries it rather than absorbed into a record that did not cause it.
6a. **README word headroom is down to 13** (3,537 against a 3,550 ceiling). Two perturbation tests in
   `tests/scripts/test_check_doc_facts.py` already had to be written word-frugally to stay inside it,
   because a perturbation that appends prose now trips the budget check instead of the drift under
   test. The next few words added to README will start breaking that suite in places unrelated to
   what is being tested. Either the page gets trimmed or the ceiling gets raised in an owner-ratified
   contract; this record did neither, having only moved cells the gates forced.
7. **Surrogate verdict staleness → 21.17**, beside the conviction and composed staleness it joins.
   `training/artifacts/surrogate/verdict.json` was fitted on the corpus that was on disk when it was
   written; this record re-recorded that corpus underneath it, so 16 of its 31 fields no longer
   re-derive and its row now reports STALE like its two siblings.

   **Re-stamping it inside this PR was refused, and the reason is structural rather than procedural.**
   Doing so would take a verdict on the new corpus *inside the record that creates the new corpus* —
   the same-PR coupling of an ML baseline to a substrate baseline that the phase-20 contract
   structure exists to forbid. Task 21.17 depends on this record, has not yet run, and is the named
   discharger of exactly this staleness.

   What the two affected tests assert instead is the honest state: STALE where production already
   said STALE, and the equality converted into the two properties that must survive a declared gap —
   the consequence mapping is stable (a NO-GO stays a NO-GO, because the verdict is keyed to the
   weights, not to the corpus population) and the disagreement is a strict SUBSET of fields, so the
   artifact is stale rather than corrupt. The amnesty stays at exactly one pair of digests.
8. **The prior-generation docstring drift** the re-pin sweep deliberately left standing: the `19_8`
   disclosure, the 850-quotations line, the `55/2,726` figure, the `10/31` Wilson cell, the
   12-ejections 4p prose, and the origin-spoken-flags comments. These are stale against a recording
   OLDER than the one this record replaced, so they belong to the 21.11-class prose sweep, not to a
   re-pin. Also `test_the_crew_omniscient_control_is_one_on_each_9p2i_set`, whose docstring was
   corrected but whose NAME now mismatches its content — kept because audits cite test ids, and
   flagged for the close rather than renamed under a record.

## 7. What IS banked, and reproducible at `$0`

* **299 recorded games** on the corrected substrate at prompt set v5, three sets complete and gated.
* **The BEFORE column, measured on the preserved baseline-7 bytes** at
  `/Users/danielkeinan/ailibi-baseline7-preserved/` — honesty, solvability, core R-gate, funnel, V&J
  and watchability, all four sets, every instrument exit 0. It reproduces the smoke's committed
  reference column exactly (e.g. `samples/9p2i` I-2 `0.0046 (3/659)`, I-10 `0.1711 (26/152)`,
  solvability killer-in-candidate-set `0.875 (126/144)`, and the live 9p2i supply split **92 vent +
  52 transcript = 144/152 = 0.9473684210526315** — NOT B-10's pre-correction 134/152).
* **The leg-4 partial**, preserved out of tree at `/Users/danielkeinan/ailibi-baseline8-leg4-partial/`
  (49 replays), so resuming costs ONE seed rather than a leg.
* **The graduation sweep**, complete and green on its own gates (§0.6).

## 8. The freeze, shown rather than asserted

`git log` over the window — from the graduation commit to this PR — shows commits touching `engine/`,
`agents/`, `meetings/`, `observation/`, `orchestrator/` or the prompt set: **exactly one**, this
branch's opening graduation commit `4ea88689`, named in §0.6 with the gates it flipped. The window
did not reopen and the record did not have to restart from the smoke.

## 9. Decisions

1. **The DoD's `check.sh`-green-on-the-sweep line cannot hold**, and §0.6 reports the reading rather
   than papering it. The graduation makes the repaired render the only one this build can produce, so
   every test that re-renders the COMMITTED pre-repair bytes goes red — 9 failures and 36 errors, one
   class, all passing at `3b156fee`. The suite returns to green when the new bytes land.
2. **`tests/observation/test_service.py` was swept** though the contract's file list does not name it.
   Deleting `vent_single_mint_enabled` makes its OFF-arm two-arm tests unimportable; the edit is
   mechanically forced by the DoD's own "delete the mechanism", not a silent scope widening.
3. **Two now-dead pieces of plumbing went with the gate** — `_ObservedAction.audible_room` (write-only
   once the audible copy was gone) and `_audible_events`' `observed_actions` parameter — under
   AGENTS.md craft rule 3, "retire means delete".
4. **No loader-mediated smoke-byte re-measure was needed**, so the §0 ordering rule is discharged
   vacuously: §0's projection and named-not-to-move list are copied from the smoke REPORT's committed
   prose, which requires no byte re-read at all. After the graduation the preserved smoke bytes stamp
   two keys `SUBSTRATE_FLAG_KEYS` no longer holds and both the loader and the validity gate refuse
   them — INTENDED, and never exercised here.
5. **A straggler replay was dropped rather than canonicalized.** `ml_corpus/9p2i` seed 1001 appeared
   on disk written 12 s BEFORE the probe seed: a worker from a leg-2 launch that was stopped had
   completed its staging move after the post-stop check came back clean. The file looked complete; a
   replay whose recording process was signalled mid-flight is not something to put in a baseline. It
   was deleted and re-recorded by the leg.
6. **Leg 3's first probe was VACUOUS and re-ran.** Seed 0 of 4p1i reached an impostor win with zero
   meetings in 1 s, making no LLM call. The committed 4p1i census shows the vacuity is a property of
   the small roster and not a defect — 40 meetings over 50 games with TEN zero-meeting games, seed 0
   among them there too — so the probe re-ran on a meeting-bearing seed rather than counting as a pass.
7. **A gate that had silently lost its teeth was repaired, not just re-pinned.**
   `test_set_fingerprints_compare_by_exact_equality` builds malformed provenance keys to prove the
   comparison refuses them. It derived those variants from the REAL committed key — and once this
   record gave every set a single recording sha, that key became a bare 8-character string, so the
   "truncated digest" case truncated 8 characters to 11 and compared the value against itself. It had
   stopped testing anything. The variants now come from a synthetic well-formed fingerprint and are
   checked against the real key in both directions. Craft rule 2 applied to a gate nobody was
   watching.
8. **The 49-seed leg-4 partial is committed as a CHECKPOINT, not as a set.** It carries no FROZEN
   line (the recorder refused to write one), no regenerated `splits.json`, no 50-game eval report and
   no validity-gate claim. Committing it preserves the spend for the resume; the PR states in its
   title and body that it must not be read as a baseline.

## 10. The resume, for whoever picks this up

1. Add credits to the Featherless account (the owner's action; the balance was **-0.0015 USD**).
2. `bash scripts/record_ml_corpus.sh --set 4p1i --expect-levers ""` from the repo root with the
   recording environment exported. The recorder's resume skip-scan re-proves each of the 49 present
   replays' provenance before trusting it, records **only** seed 1049, then finalizes: the 50-game
   eval report, `splits.json`, and the FROZEN line.
3. Gate it exactly as §3 gates the other three, then run the operator's `deadline_default` watch —
   the validity gate still has no check for it.
4. Then, and only then, the whole post-record half of the contract in §6 becomes runnable.

