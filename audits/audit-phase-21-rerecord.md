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

