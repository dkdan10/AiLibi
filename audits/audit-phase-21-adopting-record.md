# Phase-21 adopting record — the injustice record at the Wave-2 slate: four legs, read by the pre-registered rule (Task 21.24)

**Status: IN PROGRESS — the record is being taken. No verdict is stated until every leg's bytes
exist and the whole read table is written; §5 is deliberately empty until then.**

This audit records a live re-recording of all four committed replay sets on Featherless
`Qwen/Qwen3.6-27B` at the three-lever Wave-2 slate, and reads it against the bars that
`audits/audit-phase-21-preregistration.md` ratified **before these bytes existed**. It decides
nothing of its own: §4 applies that memo's §6 rule verbatim, and where a reading and the memo
disagree the memo wins and the disagreement is the finding.

## 0. Source state, prerequisites, configuration and the pre-committed projection

### 0.1 The window-open sha and the source-state certification

The record is taken at source state **`44f0a28c`**. That sha is the certificate PR #426's
two-seed post-#424 re-smoke published as `audits/audit-phase-21-smoke-wave2.md` §18 with verdict
**GO** — not #425's earlier GO over `14854a06`, which #424's edits to
`meetings/{corroboration,manager,transcript}.py` and `vote_ballot.j2` retired.

The certification holds only while no later merge touches `agents/`, `meetings/`, `observation/`,
`orchestrator/` or `agents/strategic/prompts/`. Re-run at every resume of this record:

```
$ git diff --name-only 44f0a28c..HEAD -- agents meetings observation orchestrator
(no output — 0 files)
```

The branch carries only staging bytes, this audit and the coordination commits above them, so the
window is open.

### 0.2 The prerequisite block, item by item

| item | state |
|---|---|
| (i) the re-smoke, merged | **DISCHARGED** — PR #426 merged by the owner 2026-09-03, squash `e0c2adde`; it touched `audits/README.md`, `audits/audit-phase-21-smoke-wave2.md` and `docs/artifacts.md` only, so the window stays open at `44f0a28c`'s substrate |
| (a) the freeze-guard reconciliation | **DISCHARGED** — landed in PR #427 (`608ae1f6`): a non-opening `deadline_default` row RE-RECORDS the seed at freeze and does not abandon the run, with the re-record allowance priced outside §12.2's bracket, and routing (e) putting the samples legs' scan in the operator's hand |
| (c) the T4-equality disclosure row | **DISCHARGED** — PR #427 (`608ae1f6`); equality PASSES as a population fact under §8.1, an OFF reading ABOVE ON is the STOP |
| (d) §9.2 bullet 4's executor named | **DISCHARGED** — PR #427 (`608ae1f6`); `scripts/counterfactual_phase21.py::assert_recording_declares` executes it over the record's own bytes |
| (R-4) the §5.1 row retired as discharged | **DISCHARGED** — PR #427 (`608ae1f6`); `P-1k` / `P-1ka` are the committed reader |
| (f)+(g) the two dated errata | **DISCHARGED** — PR #427 (`608ae1f6`); the §5 pointer reads E.1 and E.2, and the smoke report's §8.2 carries its erratum |
| (h) the un-bumped ballot stamp | **DISCHARGED** — PR #427 (`608ae1f6`); accepted with an erratum and NO version bump, and this audit quotes each leg's `git_sha` beside its stamp (§2) |
| (b) the husk `free_text` wording | **DEFERRED past the record** to the close ledger; `meetings/` is frozen and a merge there would reopen the window a third time. Every husk surviving in a leg is listed in §2 with its trigger |
| (j) the seed-13 featured card | **CARRIED** — the card is false on the served baseline-8 bytes; §6 executes the branch the verdict selects. No owner ruling line exists in `tasks/phase-21.md` on `origin/main`, so the contract's default copy is used on FINDING |
| (G8) the FINDING-branch landing mechanism | **UNRULED at dispatch** — no `(G8) OWNER DECISION, RULED` line exists in `tasks/phase-21.md` on `origin/main`. On FINDING the record lands by the orchestrator's recommendation (the class-(c) orphan evidence commit, its tip sha pinned in an in-tree class-(b) manifest) and is marked **PROVISIONAL** pending the owner's ruling |
| (G3) the corpus recorder preflighted at the window-open sha | **DISCHARGED** — §0.4 |

### 0.3 The successor baseline id, DERIVED

Read with the committed helper before the first heading of the read, never from memory:

```
$ uv run python -c "... check_doc_facts.recorded_ladder_tip(Path('.'), errors) ..."
_LADDER_TIP_AUDIT = audits/audit-phase-21-rerecord.md
recorded_ladder_tip = 8
errors = []
```

The tip reads **baseline 8**, which is the expected reading, so the expected successor on ADOPTED is
**baseline 9**. On FINDING the tip does not move and stays at 8. The id is not asserted here; §5
states which branch the rule selected and §6 executes it.

### 0.4 The recorded configuration, and the corpus recorder's preflight

Every recording, gate and instrument shell for a leg carries the same block (the smoke report's §2
block, with the staging paths of this record's DoD). `FEATHERLESS_API_KEY` is sourced from the
untracked `.env` at the main checkout and appears in no log, report or PR — the recorders print an
eight-character prefix and nothing here keeps it.

```
AILIBI_LLM_PROVIDER=featherless
AILIBI_PROMPT_SET=qwen3_6_27b
AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B
AILIBI_REFRESH_WORKERS=2
AILIBI_SEED_MAX_ATTEMPTS=8
AILIBI_REPORTER_REASONING=1
AILIBI_CORROBORATION_DISCIPLINE=1
AILIBI_TESTIMONY_SHAPES=1
# AILIBI_IMPOSTOR_ROLL_CALL — unset, in this and in every gate/instrument shell
# samples legs:  AILIBI_SAMPLE_DIR=<staging>/samples/<set>, AILIBI_MANIFEST=$AILIBI_SAMPLE_DIR/MANIFEST.md
#                AILIBI_NUM_PLAYERS / AILIBI_NUM_IMPOSTORS / AILIBI_TASKS_PER_CREWMATE per leg
# corpus legs:   AILIBI_ML_CORPUS_ROOT=<staging>/ml_corpus  (the recorder appends the set name)
```

`AILIBI_SEED_MAX_ATTEMPTS=8` is an override — both recorders default the crash-retry budget to 4 —
and the corpus recorder's own preview line `seed crash-retry: up to 8 attempt(s) per seed` is the
proof it took.

The corpus recorder's dry run under the full slate, at the window-open sha, before any corpus spend
(prerequisite (G3)). Its derived map and its acceptance line are quoted verbatim because the record's
validity gates take that line's value rather than a retyped one:

```
[dry-run] prompt versions: the declared slate resolves to
  [accusation_round.qwen3_6_27b.v5.reporter_reasoning+accusation_round.qwen3_6_27b.v5.testimony_shapes,
   crewmate_report.qwen3_6_27b.v5.reporter_reasoning+crewmate_report.qwen3_6_27b.v5.testimony_shapes,
   impostor_report.qwen3_6_27b.v5,
   vote_ballot.qwen3_6_27b.v5.corroboration_discipline+vote_ballot.qwen3_6_27b.v5.testimony_shapes]
[dry-run] acceptance (per set, before merge): scripts/validity_gate.py <set>
  --expected-model Qwen/Qwen3.6-27B --require-zero-cost --expected-prompt-versions
  accusation_round=accusation_round.qwen3_6_27b.v5.reporter_reasoning+accusation_round.qwen3_6_27b.v5.testimony_shapes,
  crewmate_report=crewmate_report.qwen3_6_27b.v5.reporter_reasoning+crewmate_report.qwen3_6_27b.v5.testimony_shapes,
  impostor_report=impostor_report.qwen3_6_27b.v5,
  vote_ballot=vote_ballot.qwen3_6_27b.v5.corroboration_discipline+vote_ballot.qwen3_6_27b.v5.testimony_shapes
Substrate slate OK: expected levers ON = reporter_reasoning,corroboration_discipline,testimony_shapes;
  every other live toggle OFF; the graduated levers unconditional ON.
```

`check_slate_bodies_carry_their_stamps` passed (it refuses a slate whose stamp outpaces its bodies;
the three-key slate passes and adding `impostor_roll_call` is refused), and
`derive_required_prompt_versions` filled the freeze map from `--expect-levers` rather than from a
hand-edited literal.

### 0.5 The pre-committed projection

Copied here from `audits/audit-phase-21-smoke-wave2.md` §12.2 **before** the actual is read, so the
actual is read against a number someone else committed to in advance:

| | scaling factor | four-leg total |
|---|---|---|
| low (all-games cross-check ratio) | ×1.0725 | **12h46m50s** |
| **centre (like-for-like ratio, primary)** | **×1.1703** | **13h56m45s** |
| high (like-for-like × the latency allowance) | ×1.3465 | **16h02m42s** |

The bracket is **12h47m – 16h03m, centred at 13h57m**, against 21.15's realized 11h54m28s for 299
games and the phase-20 record's 23h25m42s for 300. Any re-recorded seed is priced OUTSIDE the
bracket as its own line item, per prerequisite (a).

### 0.6 The before column

The before column is **baseline 8** — 21.15's maintenance re-record on the corrected substrate — and
it is re-derived from the committed bytes here rather than quoted from the memo:

```
$ uv run python -m eval.reporter_justice \
    replays/samples/9p2i replays/ml_corpus/9p2i replays/samples/4p1i replays/ml_corpus/4p1i --pooled
reporter justice — pooled (300 games, 672 meetings)
  meetings: body report 620, emergency 52
  reporter role: CREWMATE 620, IMPOSTOR 0
  ejections (all meetings): 429 total, 46 innocent, 383 impostor; 34 reporter
    (34 of them innocent, 73.9% of the innocent total)
  per-slot ejection: reporter 34/620 = 5.48%, innocent non-reporter 12/1859 = 0.65%,
    impostor 331/856 = 38.67% (relative risk 8.50x)
```

and the twin, per set, from `scripts/measure_baseline.py --funnel --json`:

| set | `killer_self_reported` | `reporter_ejected` | `reporter_ejected_innocent` |
|---|---|---|---|
| `samples/9p2i` | 0 | 7 | 7 |
| `ml_corpus/9p2i` | 0 | 23 | 23 |
| `samples/4p1i` | 0 | 4 | 4 |
| `ml_corpus/4p1i` | 0 | 0 | 0 |
| **pooled** | **0** | **34** | **34** |

which agrees with `eval.reporter_justice` set for set and pooled — the §4.3 I-3 provenance, on the
before column, before the record moves it.

The Wave-0 register's headline figures (42 pooled innocent ejections, 30 of them the reporter, 0
impostor reporters in 618 of 668 body-report meetings) are **baseline-7 history** and are quoted in
this audit only as history. A-4's three verifier corrections travel with them wherever they appear:
the reporter's ejectability is a recorded design decision (`agents/memory/beliefs.py:182-190`,
chartered at `tasks/phase-15.md:561-565`), not a defect; the invariant half is already published as
one of the balance wave's chartered seven (`audits/audit-phase-20-close.md:445`); and the channel is
SHRINKING across baselines — 22/106 = 20.8% of report-meeting ejections at baseline 2 against
30/379 = 7.9% at baseline 7.

**One inherited claim, and its wording is fixed:** baseline 7 is canon **by explicit owner override
of a FINDING verdict** (`audits/audit-phase-20-baseline-7.md` §6.1). Bars 1 and 2 were MISSED as
measured (61/103 = 0.5922 against ≥ 0.60; 42 against < 35). No line of this audit, its PR body, its
code comments or its README edits states or implies otherwise.

## 1. What this record does not decide

The verdict is `audits/audit-phase-21-preregistration.md` §6's conjunctive rule, applied to the four
bars its §4.1 table fixes, on these bytes, with §4.3's premise read before either reporter bar and a
VOID published as a VOID. Eligibility (§6's per-lever RENDER test) is published as a per-lever line
and graduates nothing. The seven §8.1 tripwires are STOP conditions, and for T1 and T5 never-worse
bars; none of them can carry an ADOPTED verdict. No bar is re-priced. "Adopt anyway" is the single
outcome this record must not produce, and the phase-20 override is not a precedent for re-pricing.

## 2. The legs

Each leg records into `replays/records/phase-21-wave2-staging/<kind>/<set>/`, a path walked by no
gate, and each completed seed range is checkpoint-pushed to `phase-21-adopting-record` before the
next begins.

### 2.1 Leg 1 — `samples/9p2i`, 50 games, COMPLETE

| | |
|---|---|
| wall | **3h03m29s** (09:37:39Z – 12:41:08Z), including one killed run's lost tail and the seed-3 re-record |
| games | 50 of 50 |
| re-records | **1** (seed 3) — priced outside §12.2's bracket per prerequisite (a) |
| validity gate | **PASS**, all ten checks named individually |
| tripwire reader | **exit 0**, `stopped_cells` empty, all nine gated cells PASS |
| `deadline_default` | **0 under either shape**; `lost_openings` 0, `defaults` 0, `vote_defaults` 0 |
| `failed_call` rows | **0 of any error_type** |
| `git_sha` values stamped | `c8c2c13c`, `196f3ccb`, `d859e58b`, `2cbeff5e`, `9248043b`, `b102add6` |
| reconciliation | every sha: `git diff --name-only 44f0a28c..<sha> -- agents meetings observation orchestrator` → **0 files** |

The leg was recorded in checkpoint batches, so it stamps six shas rather than one; the contract's
per-leg reconciliation is therefore run per sha, and all six touch no frozen directory.

```
$ uv run python scripts/validity_gate.py <leg 1 dir> --expected-model Qwen/Qwen3.6-27B \
    --expected-prompt-versions <the derived map, verbatim> --require-zero-cost
Validity gate over .../phase-21-wave2-staging/samples/9p2i (50 games):
  [PASS] all_games_reach_game_over: 50/50 games reached a reconstructed game_over with a consistent win condition
  [PASS] meeting_rate_and_resolution: meeting_rate 1.0 (floor 0.60); 168 resolved meetings; 0 unresolved
  [PASS] no_duplicate_meeting_rows: 0 duplicate meeting rows over 168 (want 0)
  [PASS] no_tick_1_kills: 0 kills at tick <= 1 (want 0)
  [PASS] no_friendly_fire_kills: 0 impostor-on-impostor kills (want 0)
  [PASS] no_betrayal_ballots_or_accusations: 0 teammate-betrayal ballots/accusations over 944 multi-impostor ballots (want 0)
  [PASS] no_railroaded_crew_ejections: 0 railroaded crew rows over 3436 rendered crew suspicions (want 0)
  [PASS] no_dangling_primary_reason_id: 0 dangling primary_reason_id over 944 ballots (want 0)
  [PASS] cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact on 50 games
  [PASS] byte_identical_reconstruction: 0 samples drifted from byte-identical reconstruction (want 0)
Validity gate PASSED (all checks green).
```

The lever-ON tripwire reader over the leg's own bytes, run in the leg's own shell
(`--recorded-slate on --json`, exit 0, `stopped_cells: []`); population totals and the nine gated
cells:

```
games 50 | meetings 168 | body_report_meetings 158 | ejections 89
reporter_openings 158 | reporter_openings_by_an_impostor 0

T-7   T1  PASS  spoken vent accounts naming a player who never vented
R-13  T2  PASS  reporter openings gaining the discovery-account block
R-14  T2  PASS  non-reporter speech turns gaining the base-rate block
R-15  T3  PASS  ballots gaining a reporter block
T-6   T4  PASS  location accounts that reach the alibi map
T-9a  T5  PASS  CREW speech turns gaining the witnessed-kill elicitation block
T-9b  T5  PASS  IMPOSTOR speech turns gaining the witnessed-kill elicitation block
C-9   T6  PASS  ballots gaining the source-count block
B-1m1 T7  PASS  rendered memory rows per prompt snapshot, FIRST meeting only
stopped_cells: []
```

Leg 1's own token ratio, re-derived from its own bytes against the committed baseline-8
`replays/samples/9p2i` (the smoke's §16 item 5 discipline — the seed slate is not a representative
token sample, so the per-leg ratio is re-derived rather than inherited):

| | leg 1 (ON) | baseline 8 (OFF) | ratio |
|---|---|---|---|
| games | 50 | 50 | — |
| meetings | 168 | 151 | ×1.1126 |
| calls | 1,891 | 1,740 | ×1.0868 |
| tokens | 9,717,705 | 8,134,860 | ×1.1946 |
| tokens / meeting | 57,843.5 | 53,873.2 | **×1.0737** |
| tokens / call | 5,138.9 | 4,675.2 | ×1.0992 |

The smoke projected ×1.1703 like-for-like and ×1.0725 all-games; leg 1 measures **×1.0737 per
meeting** — at the smoke's own low end — while the all-games total moves ×1.1946 because the leg
holds 17 more meetings than the set it replaces. The wall bears that out: 3h03m29s against 21.15's
3h07m00s for the same leg.

### 2.2 Leg 2 — `ml_corpus/9p2i`, 150 games, IN PROGRESS

Recording. The honesty probe passed on the first completed seed (1000: 2 meetings,
`measure_baseline --honesty` exit 0), so the leg is not vacuous and the rest queued behind it.

## 3. Secondary cells — observed, reported, never gated

*(written after the legs)*

## 4. The pre-registered read

*(written after the legs)*

## 5. The verdict

*(written after the read, and not before)*
