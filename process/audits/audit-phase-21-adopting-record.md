# Phase-21 adopting record — the injustice record at the Wave-2 slate: four legs, read by the pre-registered rule (Task 21.24)

**Verdict: FINDING.** Bars 1, 2 and 3 are MET on the recorded bytes and **bar 4 is MISSED**
(0.5500 against a target of < 0.40). `audits/audit-phase-21-preregistration.md` §6's rule is
conjunctive and names its subset exactly, so three of four is FINDING, not adoption. The three
Wave-2 levers stay live toggles, the ladder tip does not move, and the four canonical replay sets
under `replays/samples/` and `replays/ml_corpus/` are UNTOUCHED and keep their baseline-8 bytes.

The lever-ON recording — 300 games, all four sets, every gate green — is preserved as named,
non-canonical evidence rather than discarded. **The bytes live in a class-(c) orphan evidence
commit whose tip sha is pinned in-tree and fetched by that sha**, deliberately outside
`replays/samples/` (which the bare gate walks in full) and outside the declared corpus sets (which
`scripts/verify_ml_evidence.py` walks), so no gate reaches bytes it cannot reconstruct. That
landing mechanism is **PROVISIONAL**: prerequisite (G8) is an owner decision that was still open at
dispatch, and this record executed the orchestrator's recommendation. §6 states what changes if the
owner rules the other way.

A record that missed one of its own pre-registered bars is the most valuable artifact this phase can
produce, and it is published as a miss. Nothing here re-prices a bar.

## 0. Source state, prerequisites, configuration and the pre-committed projection

### 0.1 The window-open sha and the source-state certification

The record is taken at source state **`44f0a28c`**. That sha is the certificate PR #426's two-seed
post-#424 re-smoke published as `audits/audit-phase-21-smoke-wave2.md` §18 with verdict **GO** — not
#425's earlier GO over `14854a06`, which #424's edits to `meetings/{corroboration,manager,transcript}.py`
and `vote_ballot.j2` retired.

The certification holds only while no later merge touches `agents/`, `meetings/`, `observation/`,
`orchestrator/` or `agents/strategic/prompts/`. Re-run at every resume of this record, and again
after the last leg:

```
$ git diff --name-only 44f0a28c..HEAD -- agents meetings observation orchestrator
(no output — 0 files)
```

The branch carries only staging bytes, this audit and the coordination commits above them, so the
window stayed open for the whole record.

### 0.2 The prerequisite block, item by item

| item | state |
|---|---|
| (i) the re-smoke, merged | **DISCHARGED** — PR #426 merged by the owner 2026-09-03, squash `e0c2adde`; it touched `audits/README.md`, `audits/audit-phase-21-smoke-wave2.md` and `docs/artifacts.md` only, so the window stays open at `44f0a28c`'s substrate |
| (a) the freeze-guard reconciliation | **DISCHARGED** — landed in PR #427 (`608ae1f6`): a non-opening `deadline_default` row RE-RECORDS the seed at freeze and does not abandon the run, with the re-record allowance priced outside §12.2's bracket, and routing (e) putting the samples legs' scan in the operator's hand. **It was exercised: SEVEN re-record rounds over five seeds — six on leg 2 and one on leg 1 — every one a non-opening slot (§2.5)** |
| (c) the T4-equality disclosure row | **DISCHARGED** — PR #427 (`608ae1f6`); equality PASSES as a population fact under §8.1, an OFF reading ABOVE ON is the STOP. T-6 read ON 100% on every leg, so the clause was not the deciding one anywhere |
| (d) §9.2 bullet 4's executor named | **DISCHARGED** — PR #427 (`608ae1f6`); `scripts/counterfactual_phase21.py::assert_recording_declares` executed it over each leg's own bytes, exit 0 on all four |
| (R-4) the §5.1 row retired as discharged | **DISCHARGED** — PR #427 (`608ae1f6`); `P-1k` / `P-1ka` are the committed reader and are published in §3 as registered secondaries |
| (f)+(g) the two dated errata | **DISCHARGED** — PR #427 (`608ae1f6`); the §5 pointer reads E.1 and E.2, and the smoke report's §8.2 carries its erratum |
| (h) the un-bumped ballot stamp | **DISCHARGED** — PR #427 (`608ae1f6`); accepted with an erratum and NO version bump. Every leg's `git_sha` values are quoted beside its stamp in §2, which is the only thing that separates this record's ballot body from the certified smoke's |
| (b) the husk `free_text` wording | **DEFERRED past the record** to the close ledger; `meetings/` is frozen and a merge there would reopen the window a third time. **Zero husks survive in any adopted leg** — every `deadline_default` row that appeared was re-recorded away, and the final scan reads 0 under either shape on all four legs — so the list this item asks for is empty. Their triggers are published in §2.5 anyway, because the *cause* is the item's real content |
| (j) the seed-13 featured card | **EXECUTED on the FINDING branch** — no `OWNER RULING` line exists in `tasks/phase-21.md` on `origin/main`, so the contract's default copy is used and shipped with its machine check (§6.3) |
| (G8) the FINDING-branch landing mechanism | **UNRULED at dispatch** — no `(G8) OWNER DECISION, RULED` line exists in `tasks/phase-21.md` on `origin/main`. The record landed by the orchestrator's recommendation (the class-(c) orphan evidence commit) and is marked **PROVISIONAL** (§6.1) |
| (G3) the corpus recorder preflighted at the window-open sha | **DISCHARGED** — §0.4 |

### 0.3 The successor baseline id, DERIVED

Read with the committed helper before the first heading of the read, never from memory:

```
$ uv run python -c "... check_doc_facts.recorded_ladder_tip(Path('.'), errors) ..."
_LADDER_TIP_AUDIT = audits/audit-phase-21-rerecord.md
recorded_ladder_tip = 8
errors = []
```

The tip reads **baseline 8**, which is the expected reading. On ADOPTED the successor would have been
baseline 9. The rule selected FINDING, so no successor is minted:
**the ladder tip stands at baseline 8**.

### 0.4 The recorded configuration, and the corpus recorder's preflight

Every recording, gate and instrument shell for a leg carried the same block (the smoke report's §2
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
#                leg 1 exports 9/2/2; leg 3 RE-EXPORTS 4/1/1 rather than inheriting
# corpus legs:   AILIBI_ML_CORPUS_ROOT=<staging>/ml_corpus  (the recorder APPENDS the set name)
```

Two operating notes on that block, both of which cost something to learn:

* `AILIBI_SEED_MAX_ATTEMPTS=8` is an override — both recorders default the crash-retry budget to 4 —
  and the corpus recorder's own preview line `seed crash-retry: up to 8 attempt(s) per seed` is the
  proof it took.
* The corpus root is `<staging>/ml_corpus`, not the contract's literal `<staging>`, because the
  recorder appends the set name; the literal would have put the corpus set beside the samples
  subtree instead of mirroring the canonical `replays/{samples,ml_corpus}/<set>` shape. The staged
  layout is the one leg 2's first committed bytes already carried, and continuing it is what let the
  resumed session's recorder find and skip them.

The corpus recorder's dry run under the full slate, at the window-open sha, before any corpus spend
(prerequisite (G3)). Its derived map and its acceptance line are quoted verbatim because every
validity gate in this record took that line's value rather than a retyped one:

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

### 0.5 The pre-committed projection, and the actual

Copied from `audits/audit-phase-21-smoke-wave2.md` §12.2 **before** the actual was read, so the
actual is read against a number someone else committed to in advance:

| | scaling factor | four-leg total |
|---|---|---|
| low (all-games cross-check ratio) | ×1.0725 | **12h46m50s** |
| **centre (like-for-like ratio, primary)** | **×1.1703** | **13h56m45s** |
| high (like-for-like × the latency allowance) | ×1.3465 | **16h02m42s** |

**The actual is ≈ 12h05m of recording wall** (§2.6), just under the bracket's low end, and the
reason is legible rather than lucky: the smoke's like-for-like ratio was measured on five seeds,
while each leg's own ratio re-derived from its own bytes reads **×1.074 to ×1.087 per meeting** —
never the projected ×1.1703 (§2.6).
The smoke's own §16 item 5 says exactly this — the seed slate is not a representative token sample,
which is why the projection's low end is the all-games cross-check. Re-records are priced outside
the bracket per prerequisite (a): seven rounds over five seeds, leg 2's six measured at 198–418 s each for 1,749 s = **29m09s**, leg 1's one absorbed inside its batch wall.

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
before column, before the record moves it. Bars 1 and 2's before cells reproduce the memo exactly:
**50/96 = 0.5208** pooled non-direct accuracy and **46** innocent ejections.

The Wave-0 register's headline figures (42 pooled innocent ejections, 30 of them the reporter, 0
impostor reporters in 618 of 668 body-report meetings) are **baseline-7 history** and appear in this
audit only as history. A-4's three verifier corrections travel with them wherever they appear: the
reporter's ejectability is a recorded design decision (`agents/memory/beliefs.py:182-190`, chartered
at `tasks/phase-15.md:561-565`), not a defect; the invariant half is already published as one of the
balance wave's chartered seven (`audits/audit-phase-20-close.md:445`); and the channel is SHRINKING
across baselines — 22/106 = 20.8% of report-meeting ejections at baseline 2 against 30/379 = 7.9% at
baseline 7.

**One inherited claim, and its wording is fixed:** baseline 7 is canon **by explicit owner override
of a FINDING verdict** (`audits/audit-phase-20-baseline-7.md` §6.1). Bars 1 and 2 were MISSED as
measured (61/103 = 0.5922 against ≥ 0.60; 42 against < 35). No line of this audit, its PR body, its
code comments or its edits states or implies otherwise.

## 1. What this record does not decide

The verdict is `audits/audit-phase-21-preregistration.md` §6's conjunctive rule, applied to the four
bars its §4.1 table fixes, on these bytes, with §4.3's premise read before either reporter bar and a
VOID published as a VOID. Eligibility (§6's per-lever RENDER test) is published as a per-lever line
and graduates nothing. The seven §8.1 tripwires are STOP conditions, and for T1 and T5 never-worse
bars; none of them can carry an ADOPTED verdict, and none of them fired. No bar is re-priced.
"Adopt anyway" is the single outcome this record must not produce, and the phase-20 override is not
a precedent for re-pricing.

## 2. The legs

Every leg recorded into `replays/records/phase-21-wave2-staging/<kind>/<set>/`, a path walked by no
gate, and every completed seed range was checkpoint-pushed to `phase-21-adopting-record` before the
next began. The staging root is EMPTY in the final commit: §6 moved the bytes out.

### 2.1 The four legs, in the pre-registered order

| leg | set | games | gate | tripwire reader | `deadline_default` | re-records |
|---|---|---|---|---|---|---|
| 1 | `samples/9p2i` | 50/50 | **PASS**, ten checks | exit 0, `stopped_cells` empty, 9/9 PASS | 0 under either shape | 1 round, 1 seed (3) |
| 2 | `ml_corpus/9p2i` | 150/150 | **PASS**, ten checks | exit 0, `stopped_cells` empty, 9/9 PASS | 0 under either shape | 6 rounds over 4 seeds |
| 3 | `samples/4p1i` | 50/50 | **PASS**, ten checks | exit 0, `stopped_cells` empty, 9/9 PASS | 0 under either shape | 0 |
| 4 | `ml_corpus/4p1i` | 50/50 | **PASS**, ten checks | exit 0, `stopped_cells` empty, 9/9 PASS | 0 under either shape | 0 |

Each gate ran in that leg's own lever-ON shell with the derived map as
`--expected-prompt-versions` and `--require-zero-cost`; without that third flag the gate checks only
internal coherence, and a set recorded homogeneously at the WRONG map still passes. Leg 2's gate,
verbatim and representative of all four:

```
Validity gate over .../phase-21-wave2-staging/ml_corpus/9p2i (150 games):
  [PASS] all_games_reach_game_over: 150/150 games reached a reconstructed game_over with a consistent win condition
  [PASS] meeting_rate_and_resolution: meeting_rate 1.0 (floor 0.60); 435 resolved meetings; 0 unresolved
  [PASS] no_duplicate_meeting_rows: 0 duplicate meeting rows over 435 (want 0)
  [PASS] no_tick_1_kills: 0 kills at tick <= 1 (want 0)
  [PASS] no_friendly_fire_kills: 0 impostor-on-impostor kills (want 0)
  [PASS] no_betrayal_ballots_or_accusations: 0 teammate-betrayal ballots/accusations over 2495 multi-impostor ballots (want 0)
  [PASS] no_railroaded_crew_ejections: 0 railroaded crew rows over 8517 rendered crew suspicions (want 0)
  [PASS] no_dangling_primary_reason_id: 0 dangling primary_reason_id over 2495 ballots (want 0)
  [PASS] cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact on 150 games
  [PASS] byte_identical_reconstruction: 0 samples drifted from byte-identical reconstruction (want 0)
Validity gate PASSED (all checks green).
```

**The validity gate is not a measurement gate.** It passed all ten checks on a Phase-20 smoke set the
honesty instrument could not fold at all. That is why the honesty probe (§2.3) and the lever-ON
tripwire reader (§2.4) run beside it on every leg.

### 2.2 Populations

| | leg 1 | leg 2 | leg 3 | leg 4 | pooled |
|---|---|---|---|---|---|
| games | 50 | 150 | 50 | 50 | 300 |
| meetings | 168 | 435 | 39 | 43 | 685 |
| body-report meetings | 158 | 396 | 36 | 36 | 626 |
| ejections | 89 | 277 | 19 | 26 | 411 |
| reporter openings | 158 | 396 | 36 | 36 | 626 |
| **reporter openings BY AN IMPOSTOR** | **0** | **0** | **0** | **0** | **0** |

### 2.3 The honesty probe, per leg

The probe ran on the FIRST completed **meeting-bearing** seed of every leg, before the rest of that
leg queued, with a raise defined as a STOP. No leg raised.

* Leg 1 — seed 0, probe passed.
* Leg 2 — seed 1000 (2 meetings), `measure_baseline --honesty` exit 0.
* Leg 3 — **seed 0 reached NO meeting and is recorded as VACUOUS, not as passed**, exactly as
  21.15's 4p1i first seed was (`audits/audit-phase-21-rerecord.md:911-914`). Seed 1 was recorded
  next, carried 1 meeting, and the probe ran there and passed.
* Leg 4 — seed 1000 (1 meeting), probe passed.

The probe flow differed by recorder and the difference is a spend trap that was respected: on a
corpus leg the probe is `--seeds <first>` followed by the full run, whose resume skips the seed
already on disk; on a samples leg it is `--seeds 0` and then `--seeds 1,…,49`, and **`--full` was
never used afterwards** — it would re-record seed 0 with `--force`, double-spending and replacing the
probed bytes.

### 2.4 The lever-ON tripwire reader, per leg

`scripts/counterfactual_phase21.py --recording <leg dir> --recorded-slate on --json`, run in the
leg's own lever-ON shell after that leg's validity gate. **All four legs exit 0 with `stopped_cells`
empty**, and all nine gated cells PASS on all four. The ON/OFF pairs, per leg:

| cell | tripwire | predicate | leg 1 | leg 2 | leg 3 | leg 4 |
|---|---|---|---|---|---|---|
| T-7 | T1 | the count is 0, whatever the denominator | 0/113 | 0/354 | 0/20 | 0/28 |
| R-13 | T2 | every observed body-report opening gains the block | 158/158 | 396/396 | 36/36 | 36/36 |
| R-14 | T2 | every observed non-reporter speech turn gains it | 723/723 | 1867/1867 | 72/72 | 72/72 |
| R-15 | T3 | the count is 0, whatever the ballot denominator | 0/944 | 0/2495 | 0/117 | 0/129 |
| T-6 | T4 | 100% of location accounts reach the map under ON | 1114/1114 | 2851/2851 | 106/106 | 112/112 |
| T-9a | T5 | every observed CREW speech turn gains the block | 535/535 | 1435/1435 | 39/39 | 43/43 |
| T-9b | T5 | the IMPOSTOR count is 0, whatever the denominators | 0/241 | 0/625 | 0/39 | 0/43 |
| C-9 | T6 | the observed share is ≥ 99% of ballots | 943/944 | 2495/2495 | 117/117 | 129/129 |
| B-1m1 | T7 | meeting-1 row count identical between OFF and ON | 15088/724 = 15088/724 | 47690/2152 = 47690/2152 | 2552/234 = 2552/234 | 2958/258 = 2958/258 |

T-6's OFF column reads 251 / 618 / 24 / 23 against those ON denominators, so T4's ordering clause was
strictly satisfied rather than decided at equality on any leg — the (c) disclosure row's equality
case was never reached. A pooled run over all four leg directories is informational and did not
substitute for the four per-leg runs.

**T2 has a THIRD clause, and it has its own population.** R-13 and R-14 above count body-report
openings and body-report speech turns; the memo's T2 row also requires that **no emergency-meeting
prompt gains either block** (`audits/audit-phase-21-preregistration.md:736`). Emergency meetings are
not in either denominator, so the clause is read over the recorded prompts directly — every prompt
rendered at a meeting the tick's action stream shows was an emergency, checked for the reporter
block's own marker text:

| leg | emergency meetings | prompts rendered at them | prompts carrying a reporter-block marker |
|---|---|---|---|
| 1 `samples/9p2i` | 10 | 127 | **0** |
| 2 `ml_corpus/9p2i` | 39 | 466 | **0** |
| 3 `samples/4p1i` | 3 | 18 | **0** |
| 4 `ml_corpus/4p1i` | 7 | 42 | **0** |
| **pooled** | **59** | **653** | **0** |

**MET on every leg.** The 59 emergency meetings are the same 59 `eval.reporter_justice` counts
(§0.6's pooled block reads `body report 626, emergency 59`), so the population is the whole of it
and not a sample.

### 2.5 The `deadline_default` hand scan, and the seven re-record rounds

Scanned per leg under BOTH shapes (`error_type == "deadline_default"` and the model sentinel
`(deadline_default)`), by hand on the samples legs — `scripts/refresh_samples.sh` and
`eval/validity.py` contain no such check — and by `check_replay_provenance` on the corpus legs.
**Final state: 0 rows on every leg under either shape.** The recorders' own counters, from each
leg's eval report:

| leg | `lost_openings` | `defaults` | `vote_defaults` |
|---|---|---|---|
| 1 `samples/9p2i` | 0 | 0 | 0 |
| 2 `ml_corpus/9p2i` | **1** | **0** | 0 |
| 3 `samples/4p1i` | 0 | 0 | 0 |
| 4 `ml_corpus/4p1i` | 0 | 0 | 0 |

**Leg 2's `lost_openings 1` is NOT an opening default and does not touch §9.2's abandon criterion,
and the two names are close enough that the distinction is worth stating in full.**
`lost_opening_accusations` counts *meetings whose opening turn carries zero accusation claims* — the
chain dying on turn 0 — and `eval/meeting_quality.py:1588-1600` says outright that it is counted
SEPARATELY from `cap_defaulted_turns` because they have "different causes, same chain-killing
symptom". `cap_defaulted_turns` is the defaulted-turn counter, and it reads **0**. So the one row is
a meeting that opened without an accusation, not a turn that defaulted, and §9.2's criterion — whose
subject is an OPENING DEFAULT — is not reached.

Every `deadline_default` row that DID appear during recording was on a non-opening slot and was
re-recorded at freeze under §9.2 as amended by PR #427, never abandoned. **Seven rounds over five
seeds**, six of them on leg 2 and one on leg 1:

| leg | seed | slot | trigger | rounds | wall |
|---|---|---|---|---|---|
| 1 | 3 | `opt_in` turn 3 | validation — a `MeetingTurn` schema error | 1 | (inside leg 1's batch wall) |
| 2 | 1034 | `opt_in` turn 4 | validation — `Input tag 'corroboration' … does not match any of the expected tags` | 1 | 244 s |
| 2 | 1061 | `opt_in` turns 3 and 5 | validation — same tag class | 2 | 337 s + 327 s |
| 2 | 1078 | `vote` | validation — `1 validation error for ModelAuthoredVoteBallot` | 1 | 225 s |
| 2 | 1087 | `opt_in` turn 3 | validation — `Input tag 'alibi' … does not match any of the expected tags` | 2 | 198 s + 418 s |
| **total** | | | | **7 rounds over 5 seeds** | **1,749 s on leg 2 = 29m09s** |

Two seeds needed a SECOND round because the re-recording produced a fresh `deadline_default` row of
the same class; the driver rescans after every re-record for exactly that reason and stops rather
than looping (its cap is three rounds per batch, never reached).

**Every one of the seven is a schema-VALIDATION failure, not a wall-clock miss**, which is precisely
the (b) legibility item the close ledger carries: `meetings/manager.py:209`'s
`DEFAULT_TURN_FREE_TEXT = "(missed deadline; no turn submitted)"` is minted for a validation failure
too, so the husk asserts a deadline miss that did not happen. The recurring trigger has a shape worth
naming for whoever fixes it: the model emits an observation whose `type` is a word from the domain
(`corroboration`, `alibi`) that is not a member of the `MeetingTurn` observation union. No husk
survives in any leg here, so the list this item asks for is empty — but the cause is recorded.

The corpus re-record flow was followed as written rather than improvised, because a present replay
carrying such a row refuses the WHOLE re-run at the pre-spend skip-scan: DELETE the replay and its
MANIFEST row → `--seeds N` → the finalizing run. 21.15 did this five times by hand over 250 completed
games; this record took **seven rounds over five seeds** across 300.

### 2.6 Duration, per leg, against the projection — and every leg's own token ratio

**The four-leg total is on a MIXED basis and is reported as one rather than presented as a clean
number.** Leg 1's figure is inclusive of a killed run's lost tail; leg 2's is exclusive of its dead
time; legs 3 and 4 are clean. Both totals are given so a reader can choose:

| leg | 21.15's actual | recording wall | elapsed | note |
|---|---|---|---|---|
| 1 `samples/9p2i` | 3h07m00s | **3h03m29s** | 3h03m29s | INCLUSIVE of a killed background task's lost tail (§below) and of the seed-3 re-record |
| 2 `ml_corpus/9p2i` | 7h59m32s | **≈ 8h21m** | 12h03m55s | EXCLUSIVE of ≈ 3h43m dead — ≈ 3h21m after the first operator's provider-side HTTP 529 kill, ≈ 22m after a reaped background task |
| 3 `samples/4p1i` | 23m15s | **20m21s** | 20m21s | |
| 4 `ml_corpus/4p1i` | 24m41s (incomplete) | **20m30s** | 20m30s | complete |
| **four legs** | 11h54m28s (299 games) | **≈ 12h05m** | **≈ 15h48m** | recording wall against the bracket 12h47m – 16h03m |

**The HTTP 529 kill's lost tail, quantified.** The first operator's leg-2 session was killed by a
provider-side 529 after the seeds-1001-1012 batch had written its replays and MANIFEST rows; the
resumed session's recorder re-ran with `--seeds` from 1013, and the corpus recorder's own resume
skips any seed already on disk. Leg 1 carries a second, smaller instance of the same shape: one batch
was cut by a background-task wall at ~60 minutes with seeds 19 and 20 in flight, **neither of which
promoted**, so no partial seed reached the set directory (`d859e58b`). **No seed was recorded twice
into the committed bytes**, and the check is mechanical rather than asserted: every leg's MANIFEST
carries exactly one row per seed — 50 / 150 / 50 / 50 rows for 50 / 150 / 50 / 50 replays — and the
recorders refuse to freeze a set whose row set and file set disagree. The lost tails cost wall, not
bytes.

**Every leg's like-for-like ratio, re-derived from its OWN bytes** against the committed baseline-8
set it would have replaced (smoke §16 item 5 — the seed slate is not a representative token sample,
so no leg's ratio is generalised from another's):

| leg | ON meetings | ON tokens | ON tok/mtg | OFF meetings | OFF tokens | OFF tok/mtg | **ratio** |
|---|---|---|---|---|---|---|---|
| 1 `samples/9p2i` | 168 | 9,717,705 | 57,843.5 | 151 | 8,134,860 | 53,873.2 | **×1.0737** |
| 2 `ml_corpus/9p2i` | 435 | 25,543,458 | 58,720.6 | 439 | 23,804,796 | 54,225.0 | **×1.0829** |
| 3 `samples/4p1i` | 39 | 729,240 | 18,698.5 | 39 | 671,145 | 17,208.8 | **×1.0866** |
| 4 `ml_corpus/4p1i` | 43 | 807,588 | 18,781.1 | 43 | 743,786 | 17,297.3 | **×1.0858** |

**The four ratios span 1.29 percentage points — ×1.0737 to ×1.0866 — and none of them is the
smoke's ×1.1703.** Legs 2-4 read ×1.0829, ×1.0866 and ×1.0858; leg 1 reads ×1.0737 and is the
lowest of the four, so quoting it alone would understate the other three. That gap — measured
×1.074-×1.087 against a projected ×1.1703 — is the whole of the difference between the projection
and the actual.

**The token basis, stated because two are available and they differ.** Every figure above is on the
`llm_calls` basis: the tokens recorded against each meeting's own completed calls. The eval report's
`cost_dashboard` totals the same calls PLUS the burned generations recorded in the `failed_call`
channel, so the two agree exactly on legs 1, 3 and 4 (9,717,705 / 729,240 / 807,588) and differ on
leg 2 by **3,562 tokens** — 25,547,020 against 25,543,458 — which is the single `ValidationError`
`failed_call` row that leg carries (§2.5). Cost is `0.0000` on every row of every MANIFEST and
`total_cost_usd` 0.0 in all four dashboards.

### 2.7 The `git_sha` reconciliation

Each recorder stamps one sha at the start of its own run, and this record was taken in checkpoint
batches, so the legs carry more than one sha each. The MANIFESTs carry **33** stamped shas in all,
and the count needs its two halves named or it does not reconcile: **31** appear in per-seed ROWS
(6 / 14 / 6 / 5 by leg) and **2 more** appear only in the corpus legs' **FROZEN lines** — `0747ce2d`
on leg 2 and `3fdd1193` on leg 4 — which are the finalizing runs' own HEADs, stamped when the set was
frozen rather than when a seed was recorded. The samples legs have no FROZEN line, so they contribute
none. For every one of the 33:

```
$ git diff --name-only 44f0a28c..<sha> -- agents meetings observation orchestrator
(no output — 0 files)
```

Every stamped sha touches **0 frozen-directory files** against the window-open sha, and every one of
them is a staging-bytes commit on this record's own branch:

| leg | stamped `git_sha` values |
|---|---|
| 1 `samples/9p2i` | `c8c2c13c` `196f3ccb` `d859e58b` `2cbeff5e` `9248043b` `b102add6` |
| 2 `ml_corpus/9p2i` | `78750e8d` `a8cb6f33` `035bf197` `c54cd96d` `931b80ad` `088f9e58` `e0792146` `e25e6008` `aab13b08` `853cccf6` `c60fc246` `9b975281` `c9291539` `6893c2c6` |
| 3 `samples/4p1i` | `5608556d` `e1f69a08` `5ea966b1` `a1d9d384` `b65cad28` `c9c6b891` |
| 4 `ml_corpus/4p1i` | `a1048b2d` `9f40ff6d` `c93fad1d` `6edf947b` `8da83101` |
| 2 + 4, FROZEN lines | `0747ce2d` (leg 2) `3fdd1193` (leg 4) |

The batching is why there are thirty-three rather than four, and it is the same discipline that made
the record survive two operator kills: a lost machine cost a batch, never a leg.

### 2.8 §9.2's abandon criteria, walked one by one

The memo's STOP list in its own amended words, each read against what the record actually did. **None
was met, so the record was never a candidate for abandonment** — which is a different statement from
"nothing happened", and the third row is why.

| §9.2 criterion (amended) | reading on this record | |
|---|---|---|
| "a `scripts/validity_gate.py` FAIL on any leg" | four legs, four PASSes, all ten checks named individually on each (§2.1) | **NOT MET** |
| "a seed whose opening defaults (the `(deadline_default)` watch item). **The criterion's subject is an OPENING default and nothing else.**" | zero openings defaulted anywhere: `cap_defaulted_turns` reads 0 on all four legs, and the seven `deadline_default` rows that did appear were all on `opt_in` or `vote` slots (§2.5). Leg 2's `lost_openings 1` is a meeting whose opening carried no accusation — a different counter, and the memo's subject is the default | **NOT MET** |
| "a guard trip" | the corpus freeze guard `check_replay_provenance` TRIPPED — on seeds 1034, 1061, 1078 and 1087, refusing to freeze a set holding a `deadline_default` row. Under prerequisite (a) as PR #427 amended it, a trip on a NON-OPENING row re-records that seed and does not abandon: the guard is stricter than §9.2 by design, and the amendment is what reconciles them. Every trip was resolved by re-recording, every re-record was logged with its cause as it happened, and the final scan reads 0 rows under either shape | **MET-AND-RESOLVED, not an abandon** |
| "a lever-stamp mismatch between the recorded snapshot and the declared slate" | `assert_recording_declares` exits 0 on all four legs, and the gate's `cost_and_provenance_exact` check reads "substrate stamped exact" on 50 / 150 / 50 / 50 games | **NOT MET** |
| "any of the seven §8.1 tripwires failing **its predicate**" | all seven hold on all four legs — nine gated cells PASS per leg, `stopped_cells` empty per leg, and T2's third clause read over its own population (§2.4) | **NOT MET** |

The third row is the one worth stating plainly rather than folding into a green column: **a guard did
trip, four times, and the amendment is the only reason that is not an abandoned record.** It is also
the reason prerequisite (a) had to merge before the first seed.

## 3. Secondary cells — observed, reported, never gated

**No bar, tripwire or §9.2 criterion names anything in this section, and it decides nothing.** It is
the pre-registration's §5 class, published because a record that reports only its bars is not a
record.

### 3.1 The win split (memo §5's ±15-point band)

| set | baseline-8 impostor rate | this record | move |
|---|---|---|---|
| `samples/9p2i` | 15/50 = 30.0% | 12/50 = 24.0% | −6.0 pts |
| `ml_corpus/9p2i` | 36/150 = 24.0% | 28/150 = 18.7% | −5.3 pts |
| `samples/4p1i` | 18/50 = 36.0% | 18/50 = 36.0% | 0.0 pts |
| `ml_corpus/4p1i` | 13/50 = 26.0% | 14/50 = 28.0% | +2.0 pts |

**Every set sits inside the ±15-point band.** The band is a registered secondary and not a bar; it is
reported so a reader can see that the accuracy gains in §4 did not come from a collapsed win split.

### 3.2 The spoken kills, one row per account

Baseline 8 carried **zero** spoken `saw_kill` accounts pooled — bar 1's split by a spoken kill was
`0/96`, and the smoke saw two over five seeds. **This record carries 30.** Roles come from the
committed `eval.validity.roles_by_seed` re-seeding, never from the replay, so "the account was TRUE"
is checked against ground truth rather than against the transcript that made the claim.

* **30 spoken `saw_kill` rows** across the four legs.
* **30 of 30 accounts named a real impostor**, and — on the stronger joined reading below —
  **30 of 30 also join the engine's own kill event on killer and room**, each witnessed by the
  speaker. The no-fabrication conclusion rests on the join, not on the role check.
* **16 of 30 CONVERTED** — the named player was ejected at that meeting.

Stated as counts and never as a rate, per §5's discipline.

**Two different questions, and only one of them can carry the word "fabrication".** The reader above
checks the account's SUBJECT against ground truth — was the named player really an impostor — and
that is a role check, not a truth check. A-22 already found rows that named a real impostor and still
got the event wrong, so the role check alone cannot support "no fabrication occurred". A spoken
`saw_kill` carries a killer, a ROOM and a TICK, so the honest check joins all three against the
engine's own `KilledEvent`, reconstructed by `eval.replay_walk.walk_replay` under a referee-grade
profile — A-22's own recipe.

| reading | definition | this record |
|---|---|---|
| named a real impostor | the account's subject is an IMPOSTOR by the committed re-seeding | **30 / 30** |
| joins the kill event on killer + room | an engine `KilledEvent` exists with that actor in that room | **30 / 30** |
| ...on the exact tick as well | the same event's tick equals the claimed tick | **0 / 30** |
| ...at a uniform +1 tick | claimed tick = kill tick + 1, on every row | **30 / 30** |
| the speaker was a recorded WITNESS of that kill | the speaker is in the event's own `witnesses` | **30 / 30** |

**Every one of the thirty accounts joins a real kill, by the killer it names, in the room it names,
which the speaker actually witnessed — so no fabricated kill account appears anywhere in 300 games.**
That sentence rests on the JOIN, not on the role check.

**The tick is off by exactly one on all thirty, and it is a labelling convention rather than a wrong
claim.** The offset is `+1` on every single row — not scattered, not occasionally — which is the
already-recorded tick-semantics item A-22's merge note carries as its own finding ("its secondary
+1-tick observation is carried as its own item (legibility / tick semantics)"). A uniform offset on
30 of 30 rows is a frame convention between the memory line and the event stream; a fabrication would
not be uniform. It is reported here rather than smoothed over, and it changes no count above.

**The thirty rows, in the smoke report's §8.5 columns, with the join as its own column.** Roles are
ground truth from the committed re-seeding; "converted" means the named player was the one ejected at
that meeting.

| # | set | seed / meeting | speaker (role) | reporter? | names (true role) | named a real impostor | joins the kill event (killer + room) | victim | speaker witnessed it | ballot tally | outcome / ejected (role) | converted | contradictions |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `9p2i` | 17 / meeting-3 | p-1 (CREWMATE) | YES | p-4 (IMPOSTOR) | YES | YES (tick +1) | p-6 | YES | `{'p-4': 2, 'p-1': 1}` | EJECTED / p-4 (IMPOSTOR) | YES | 0 |
| 2 | `9p2i` | 19 / meeting-3 | p-1 (CREWMATE) | YES | p-9 (IMPOSTOR) | YES | YES (tick +1) | p-7 | YES | `{'p-9': 1, 'p-1': 4}` | EJECTED / p-1 (CREWMATE) | no | 0 |
| 3 | `9p2i` | 26 / meeting-0 | p-1 (CREWMATE) | YES | p-3 (IMPOSTOR) | YES | YES (tick +1) | p-8 | YES | `{'p-3': 1, 'p-9': 3, 'SKIP': 3, 'p-1': 1}` | SKIPPED / None (-) | no | 0 |
| 4 | `9p2i` | 26 / meeting-1 | p-1 (CREWMATE) | YES | p-3 (IMPOSTOR) | YES | YES (tick +1) | p-8 | YES | `{'p-2': 5, 'SKIP': 2}` | EJECTED / p-2 (IMPOSTOR) | no | 1 |
| 5 | `9p2i` | 37 / meeting-4 | p-7 (CREWMATE) | YES | p-9 (IMPOSTOR) | YES | YES (tick +1) | p-6 | YES | `{'p-9': 2, 'SKIP': 1}` | EJECTED / p-9 (IMPOSTOR) | YES | 0 |
| 6 | `9p2i` | 37 / meeting-4 | p-8 (CREWMATE) | no | p-9 (IMPOSTOR) | YES | YES (tick +1) | p-6 | YES | `{'p-9': 2, 'SKIP': 1}` | EJECTED / p-9 (IMPOSTOR) | YES | 0 |
| 7 | `9p2i` | 44 / meeting-4 | p-3 (CREWMATE) | YES | p-5 (IMPOSTOR) | YES | YES (tick +1) | p-1 | YES | `{'p-5': 2, 'SKIP': 1}` | EJECTED / p-5 (IMPOSTOR) | YES | 0 |
| 8 | `9p2i` | 1000 / meeting-0 | p-2 (CREWMATE) | YES | p-8 (IMPOSTOR) | YES | YES (tick +1) | p-3 | YES | `{'p-8': 6, 'SKIP': 2}` | EJECTED / p-8 (IMPOSTOR) | YES | 9 |
| 9 | `9p2i` | 1012 / meeting-3 | p-7 (CREWMATE) | YES | p-9 (IMPOSTOR) | YES | YES (tick +1) | p-6 | YES | `{'SKIP': 2, 'p-7': 1, 'p-9': 1}` | SKIPPED / None (-) | no | 0 |
| 10 | `9p2i` | 1012 / meeting-4 | p-7 (CREWMATE) | no | p-9 (IMPOSTOR) | YES | YES (tick +1) | p-6 | YES | `{'p-9': 2, 'SKIP': 1}` | EJECTED / p-9 (IMPOSTOR) | YES | 1 |
| 11 | `9p2i` | 1021 / meeting-2 | p-2 (CREWMATE) | YES | p-6 (IMPOSTOR) | YES | YES (tick +1) | p-4 | YES | `{'p-6': 2, 'SKIP': 1}` | EJECTED / p-6 (IMPOSTOR) | YES | 2 |
| 12 | `9p2i` | 1023 / meeting-3 | p-2 (CREWMATE) | YES | p-5 (IMPOSTOR) | YES | YES (tick +1) | p-1 | YES | `{'p-5': 2, 'SKIP': 3}` | SKIPPED / None (-) | no | 0 |
| 13 | `9p2i` | 1030 / meeting-1 | p-5 (CREWMATE) | YES | p-9 (IMPOSTOR) | YES | YES (tick +1) | p-4 | YES | `{'p-9': 5, 'SKIP': 1}` | EJECTED / p-9 (IMPOSTOR) | YES | 0 |
| 14 | `9p2i` | 1045 / meeting-1 | p-1 (CREWMATE) | YES | p-3 (IMPOSTOR) | YES | YES (tick +1) | p-8 | YES | `{'p-3': 1, 'SKIP': 3, 'p-1': 1}` | SKIPPED / None (-) | no | 0 |
| 15 | `9p2i` | 1045 / meeting-2 | p-1 (CREWMATE) | YES | p-3 (IMPOSTOR) | YES | YES (tick +1) | p-8 | YES | `{'p-3': 1, 'p-1': 4}` | EJECTED / p-1 (CREWMATE) | no | 0 |
| 16 | `9p2i` | 1049 / meeting-0 | p-1 (CREWMATE) | YES | p-7 (IMPOSTOR) | YES | YES (tick +1) | p-6 | YES | `{'p-7': 5, 'SKIP': 2}` | EJECTED / p-7 (IMPOSTOR) | YES | 0 |
| 17 | `9p2i` | 1050 / meeting-1 | p-1 (CREWMATE) | YES | p-9 (IMPOSTOR) | YES | YES (tick +1) | p-4 | YES | `{'p-9': 1, 'SKIP': 3, 'p-1': 1}` | SKIPPED / None (-) | no | 0 |
| 18 | `9p2i` | 1050 / meeting-2 | p-1 (CREWMATE) | YES | p-9 (IMPOSTOR) | YES | YES (tick +1) | p-4 | YES | `{'p-9': 1, 'p-1': 4}` | EJECTED / p-1 (CREWMATE) | no | 0 |
| 19 | `9p2i` | 1052 / meeting-2 | p-3 (CREWMATE) | YES | p-6 (IMPOSTOR) | YES | YES (tick +1) | p-1 | YES | `{'p-6': 3, 'SKIP': 1}` | EJECTED / p-6 (IMPOSTOR) | YES | 1 |
| 20 | `9p2i` | 1062 / meeting-2 | p-1 (CREWMATE) | YES | p-9 (IMPOSTOR) | YES | YES (tick +1) | p-3 | YES | `{'p-9': 4, 'SKIP': 1}` | EJECTED / p-9 (IMPOSTOR) | YES | 0 |
| 21 | `9p2i` | 1076 / meeting-0 | p-1 (CREWMATE) | YES | p-2 (IMPOSTOR) | YES | YES (tick +1) | p-4 | YES | `{'p-2': 1, 'p-7': 5, 'p-1': 1, 'SKIP': 1}` | EJECTED / p-7 (CREWMATE) | no | 2 |
| 22 | `9p2i` | 1101 / meeting-1 | p-6 (CREWMATE) | YES | p-8 (IMPOSTOR) | YES | YES (tick +1) | p-3 | YES | `{'p-8': 5, 'SKIP': 1}` | EJECTED / p-8 (IMPOSTOR) | YES | 0 |
| 23 | `9p2i` | 1102 / meeting-0 | p-3 (CREWMATE) | YES | p-8 (IMPOSTOR) | YES | YES (tick +1) | p-5 | YES | `{'SKIP': 2, 'p-1': 5}` | EJECTED / p-1 (IMPOSTOR) | no | 2 |
| 24 | `9p2i` | 1102 / meeting-1 | p-3 (CREWMATE) | YES | p-8 (IMPOSTOR) | YES | YES (tick +1) | p-9 | YES | `{'p-8': 3, 'SKIP': 1}` | EJECTED / p-8 (IMPOSTOR) | YES | 0 |
| 25 | `9p2i` | 1102 / meeting-1 | p-6 (CREWMATE) | no | p-8 (IMPOSTOR) | YES | YES (tick +1) | p-9 | YES | `{'p-8': 3, 'SKIP': 1}` | EJECTED / p-8 (IMPOSTOR) | YES | 0 |
| 26 | `9p2i` | 1117 / meeting-1 | p-1 (CREWMATE) | YES | p-9 (IMPOSTOR) | YES | YES (tick +1) | p-3 | YES | `{'p-9': 4, 'SKIP': 1}` | EJECTED / p-9 (IMPOSTOR) | YES | 1 |
| 27 | `9p2i` | 1125 / meeting-0 | p-1 (CREWMATE) | YES | p-2 (IMPOSTOR) | YES | YES (tick +1) | p-7 | YES | `{'p-2': 1, 'p-1': 1, 'SKIP': 3}` | SKIPPED / None (-) | no | 0 |
| 28 | `9p2i` | 1125 / meeting-1 | p-1 (CREWMATE) | YES | p-2 (IMPOSTOR) | YES | YES (tick +1) | p-7 | YES | `{'p-2': 2, 'SKIP': 3}` | SKIPPED / None (-) | no | 0 |
| 29 | `9p2i` | 1136 / meeting-0 | p-1 (CREWMATE) | YES | p-8 (IMPOSTOR) | YES | YES (tick +1) | p-3 | YES | `{'p-8': 4, 'SKIP': 2}` | EJECTED / p-8 (IMPOSTOR) | YES | 0 |
| 30 | `4p1i` | 22 / meeting-0 | p-3 (CREWMATE) | YES | p-4 (IMPOSTOR) | YES | YES (tick +1) | p-1 | YES | `{'SKIP': 2, 'p-4': 1}` | SKIPPED / None (-) | no | 0 |

Three things in that table are worth naming, none of them a criterion:

* **Row 2 is the case this record exists to be able to see.** On `9p2i` seed 19 the meeting's own
  reporter spoke a kill account that JOINS the engine event — right killer, right room, a kill he
  was a recorded witness to — and the table ejected **the speaker**, 4 ballots to 1. A
  truthful eyewitness was convicted for testifying. It is one row and it prices nothing; it is also
  exactly the injustice shape the Wave-0 register named, still reachable at this slate.
* **Not one of the thirty accounts was fabricated**, on the joined definition above — the question
  T1 exists to ask, answered on a population instead of on a smoke's two rows.
* **Sixteen of thirty converted**, and fourteen did not. A spoken kill is heard and is not decisive.

The `[ADV]`-marked rows in the `P-1k` table below and these thirty rows are the same population read
two ways: the table above is every spoken account, `P-1k` is the subset whose meeting ended in a
non-direct conviction of the named player.

Bar 1's own cell split by a spoken kill, from the committed ON-recording reader (`P-1k` / `P-1ka`,
merged in #421):

| leg | `P-1k` non-direct convictions whose ejectee a spoken kill named | `P-1ka` of those, convicted an IMPOSTOR |
|---|---|---|
| 1 `samples/9p2i` | 3/15 | 3/3 |
| 2 `ml_corpus/9p2i` | 7/51 | 7/7 |
| 3 `samples/4p1i` | 0/0 `[ADV]` | 0/0 `[ADV]` |
| 4 `ml_corpus/4p1i` | 0/0 `[ADV]` | 0/0 `[ADV]` |
| **pooled** | **10/66** | **10/10** |

against baseline 8's `0/96` and the smoke's `0/3`. Ten of bar 1's sixty-six non-direct convictions
were reached with a spoken kill account naming the ejectee, and **all ten convicted an impostor**.
The two 4p1i legs have an empty denominator and are marked `[ADV]` rather than read.

### 3.3 The realized cross-lever interaction, measured rather than derived

Errata E.1 registered the ballot's cross-lever interaction and predicted it in as many words: *"the
FIRST spoken kill at 21.23 or 21.24 will move the joint ballot by more than the two arms alone."*
Here it is at scale rather than at n=2. The testimony census, pooled over the four legs, shows the
`saw_kill` statement class present under ON and absent under the reconstructed OFF (30 rows), and
`saw_move` and `whereabouts` classes that exist only under ON (1,446 and 3,267 rows). The alibi map
goes from partial to total on every leg: `alibi_map_off` → `alibi_map_on` reads 251→1114, 618→2851,
24→106 and 23→112. Episodic rows rise from 47,988 under OFF to 71,423 under ON. This record does not
decompose that delta between the public-transcript row and the adopted-clause fork and does not
re-price E.1's per-row arithmetic; that is pinned on a synthetic kill meeting by
`tests/meetings/test_corroboration.py::TestAdoptedClauseWording`.

### 3.4 Decisiveness, beside bar 2

**The registered cell first.** Memo §5 registers decisiveness as **body-report ejections over
body-report meetings, plus the SKIP share**, read from I-3's `report_ejections` twin
(`eval/funnel.py`). It is printed beside bar 2 for one reason, which the memo states outright: *a
bar-2 pass that came from deciding LESS reads as such.* Bar 2 counts wrongful ejections, and a record
that lowers it by skipping more meetings rather than by convicting better moves this cell too.

| set | baseline 8 (ejected / body-report meetings) | this record | skipped, this record |
|---|---|---|---|
| `samples/9p2i` | 85/141 = 60.3% | **79/158 = 50.00%** | 79/158 = 50.00% |
| `ml_corpus/9p2i` | 249/407 = 61.2% | **238/396 = 60.10%** | 158/396 = 39.90% |
| `samples/4p1i` | 21/36 = 58.3% | **16/36 = 44.44%** | 20/36 = 55.56% |
| `ml_corpus/4p1i` | 22/36 = 61.1% | **19/36 = 52.78%** | 17/36 = 47.22% |
| **pooled** | **377/620 = 60.8%** | **352/626 = 56.23%** | **274/626 = 43.77%** |

**The record decided LESS on every leg, and pooled — 60.8% → 56.23%, a fall of 4.6 points — so part
of bar 2's fall is a decisiveness fall and this audit says so rather than leaving it to be found.**
The cell is observed and never gated; it decides nothing, and it does not change bar 2's verdict.
What it does is bound the reading: the wrongful-ejection total fell 46 → 20 (−56.5%) while the
ejection RATE fell 60.8% → 56.2% (−7.5% relative), so the great majority of bar 2's movement is not
accounted for by deciding less. The same point from the other side: ejection ACCURACY rose from
383/429 = 89.3% to 391/411 = 95.1%.

**A second partition, published because §3.4 carried it before the registered cell was added.** This
is the flagged/unflagged split of every ejection — a different question from the one above, and not
interchangeable with it:

| leg | ejections | flagged ejections → impostor / innocent | unflagged ejections → impostor / innocent |
|---|---|---|---|
| 1 `samples/9p2i` | 89 | 75 → 74 / **1** | 14 → 10 / 4 |
| 2 `ml_corpus/9p2i` | 277 | 226 → 226 / 0 | 51 → 36 / 15 |
| 3 `samples/4p1i` | 19 | 19 → 19 / 0 | 0 → 0 / 0 |
| 4 `ml_corpus/4p1i` | 26 | 26 → 26 / 0 | 0 → 0 / 0 |
| **pooled** | **411** | **346 → 345 / 1** | **65 → 46 / 19** |

**One of 346 flagged ejections across 300 games took an innocent** — on leg 1 — and the other
nineteen of bar 2's twenty sit in the unflagged cell. Flagged-meeting ejection accuracy is therefore
345/346 = 0.9971 pooled. This split is a different partition from bar 1's proof-present/non-direct
one and the two are not interchangeable: proof-present reads 345 ejections and non-direct 66, against
flagged 346 and unflagged 65.

### 3.5 The corroboration cells and the render census

| cell | leg 1 | leg 2 | leg 3 | leg 4 | pooled |
|---|---|---|---|---|---|
| C-1 accused subjects with NO first-hand source | 146/396 | 372/1006 | 29/78 | 38/88 | 585/1568 |
| C-2 ejected subjects with NO first-hand source | 8/89 | 8/275 | 0/19 | 0/26 | 16/409 |
| C-3 ejections whose charge ANSWERED the ejectee's own | 4/89 | 8/277 | 0/19 | 0/26 | 12/411 |
| C-4 ejected subjects with a map-satisfied placement pair | 9/89 | 38/277 | 0/19 | 1/26 | 48/411 |

**The render census, per bucket.** Memo §5 requires it *"reported per bucket and never as one
blended number"*, so the blended mean sits in its own column beside the buckets rather than standing
in for them (`eval.evidence_honesty.RenderBudgetCells`; baseline 8 on `samples/9p2i` reads 1,740
snapshots, 63,624 rendered rows, mean 36.5655, 25,628 testimony rows in buckets ≤4: 6,882; 5-6:
17,340; ≥7: 1,406):

| leg | snapshots | rendered rows | mean | testimony rows | ≤4 | 5-6 | ≥7 |
|---|---|---|---|---|---|---|---|
| 1 `samples/9p2i` | 1,891 | 74,515 | 39.4051 | 43,755 | 13,364 | 27,441 | 2,950 |
| 2 `ml_corpus/9p2i` | 4,996 | 190,601 | 38.1507 | 97,915 | 28,449 | 63,988 | 5,478 |
| 3 `samples/4p1i` | 234 | 2,552 | 10.9060 | 0 | 0 | 0 | 0 |
| 4 `ml_corpus/4p1i` | 258 | 2,958 | 11.4651 | 0 | 0 | 0 | 0 |
| **pooled** | **7,379** | **270,626** | **36.6752** | **141,670** | **41,813** | **91,429** | **8,428** |

The two 4p1i legs carry **zero** testimony rows in every bucket, which is a property of the roster
rather than of the levers: a four-player table rarely has a second living witness to report. Pooling
those zeroes into one blended mean is exactly what the memo's "never as one blended number" rule
exists to prevent — the pooled 36.6752 is dominated by the 9p2i legs and describes neither shape.
`fabricated_vent_rows` is **0 on every leg**.

### 3.6 The evidence-supply floors, scored against baseline 8's block

The committed referee reads this record against the **baseline-8** floors, which were pinned from
baseline 8's own bytes. One treatment throughout, stated in the column header rather than applied
case by case: **a gauge whose baseline numerator was 0 or 1 is ADVISORY under the standing rare-event
rule and can never fail the referee** — a floor no sample could miss is not a floor — and every other
gauge binds.

| leg | referee | gauges BELOW their floor (binding) | advisory gauges |
|---|---|---|---|
| 1 `samples/9p2i` | **FAIL** (supply floors FAIL, integrity OK) | `flags_per_meeting` 0.857 < 0.974; `testimony_backed_conversion` 0.605 < 0.719; `transcript_flags_per_meeting` 0.268 < 0.377; `persisted_vent_flags_per_meeting` 0.589 < 0.596 | — |
| 2 `ml_corpus/9p2i` | **FAIL** | `transcript_flags_per_meeting` 0.303 < 0.377 | — (the other four PASS: `witnessed_event_rate` 0.0344, `flags_per_meeting` 1.0322, `testimony_backed_conversion` 0.7041, `persisted_vent_flags_per_meeting` 0.7287) |
| 3 `samples/4p1i` | **FAIL** | `testimony_backed_conversion` 0.559 < 0.577 | `witnessed_event_rate` 0.0152 < 0.0161 — reported, not referee-failing |
| 4 `ml_corpus/4p1i` | **PASS** | none | `witnessed_event_rate` 0.0 < 0.0161 — reported, not referee-failing |

**Leg 4's row says PASS while one of its gauges reads below its floor, and that is the advisory rule
working rather than an inconsistency.** The reader prints
`referee: PASS (supply floors PASS, integrity OK)` for that leg with
`witnessed_event_rate: measured 0.0 >= floor 0.016129032258064516 -> FAIL` inside it: the gauge is
advisory, so the referee does not fail on it, and this table shows both halves rather than picking
whichever reads cleaner. Leg 3's `witnessed_event_rate` is the same gauge and the same treatment; its
FAIL comes from `testimony_backed_conversion`, which binds.

**This is a supply reading and not a criterion**: §9.2's abandon list does not name the referee, and
no bar reads it. It says something worth stating plainly — **the Wave-2 slate convicts more
accurately on FEWER flags** (§3.4: accuracy 89.3% → 95.1% while `flags_per_meeting` falls below
baseline 8's floor on the leg that serves the demo). On ADOPTED a successor floor block would have
been pinned from this record's own bytes and the comparison would have moved with it; on FINDING the
canonical bytes do not move, so `_BASELINE_SUPPLY_FLOORS` and `_DEFAULT_BASELINE_ID` are untouched
(§6.2) and this table is published as the observation it is.

### 3.7 The three registered §5 secondaries: solvability, zero-flag convictions, co-discovery

Registered in memo §5 and not published anywhere else in this audit, so they are published here —
per leg and pooled, beside the baseline-8 figures the memo itself states.

**I-5, the solvability ceiling** (`eval/solvability.py`, `--solvability`). Baseline 8: containment
557/620 pooled, and ejections landing on an already-cleared player 63/377 pooled.

| leg | containment (`killer_in_set`) | singleton rate | singleton correctness | ejections onto an already-CLEARED player |
|---|---|---|---|---|
| 1 `samples/9p2i` | 142/158 = 0.8987 | 30/158 = 0.1899 | 24/30 = 0.8000 | 10/79 = 0.1266 |
| 2 `ml_corpus/9p2i` | 349/396 = 0.8813 | 53/396 = 0.1338 | 51/53 = 0.9623 | 41/238 = 0.1723 |
| 3 `samples/4p1i` | 36/36 = 1.0000 | 5/36 `[ADV]` | 5/5 `[ADV]` | 0/16 `[ADV]` |
| 4 `ml_corpus/4p1i` | 36/36 = 1.0000 | 4/36 `[ADV]` | 4/4 `[ADV]` | 0/19 `[ADV]` |
| **pooled** | **563/626 = 0.8994** | **92/626 = 0.1470** | **84/92 = 0.9130** | **51/352 = 0.1449** |

Containment holds at 0.8994 pooled against baseline 8's 557/620 = 0.8984 — flat. The
already-cleared cell reads **51/352 = 14.5%** against baseline 8's 63/377 = 16.7%. `[ADV]` marks the
reader's own advisory flag on a rare-event denominator.

**I-6, the zero-flag conviction cells** (`eval/vj_instruments.py:312-327`, `--vj`). Baseline 8: 86 of
429 convictions carry no flag, 37 of them CREW and 49 IMPOSTOR — so 37 of the 46 innocent ejections
were flagless.

| leg | zero-flag convictions | CREW | IMPOSTOR |
|---|---|---|---|
| 1 `samples/9p2i` | 14 | 4 | 10 |
| 2 `ml_corpus/9p2i` | 49 | 13 | 36 |
| 3 `samples/4p1i` | 0 | 0 | 0 |
| 4 `ml_corpus/4p1i` | 0 | 0 | 0 |
| **pooled** | **63 of 411** | **17** | **46** |

The flagless conviction channel narrowed from 86/429 = 20.0% to **63/411 = 15.3%**, and its CREW half
— the one that matters for bar 2 — from 37 to **17**. Seventeen of the record's twenty wrongful
ejections are flagless, against 37 of 46 at baseline 8.

**The `at_body` / co-discoverer recipient read** (memo §5, `eval.reporter_justice`). A-38's proposed
widening — extending exculpatory framing to non-reporter co-discoverers — was REJECTED on
measurement, and this is the cell that keeps that decision honest: the co-discoverer seats are close
to half impostor, so framing them exculpatory would have handed an impostor the same shelter half the
time. Baseline 8 pooled: 118/620 meetings carry a co-discovery, slots 74 CREWMATE / 71 IMPOSTOR =
49.0% impostor.

| leg | meetings carrying a co-discovery | CREWMATE slots | IMPOSTOR slots | impostor share |
|---|---|---|---|---|
| 1 `samples/9p2i` | 36/158 | 23 | 22 | 48.9% |
| 2 `ml_corpus/9p2i` | 91/396 | 58 | 54 | 48.2% |
| 3 `samples/4p1i` | 0/36 | 0 | 0 | n/a |
| 4 `ml_corpus/4p1i` | 0/36 | 0 | 0 | n/a |
| **pooled** | **127/626** | **81** | **76** | **48.4%** |

**48.4% against baseline 8's 49.0% — the seat is still a coin flip, and the rejection still holds on
these bytes.** Both 4p1i legs carry no co-discovery at all, for the roster reason §3.5 gives.

### 3.8 Tokens per call, per leg

5,138.9 / 5,112.8 / 3,116.4 / 3,130.2, over 1,891 / 4,996 / 234 / 258 recorded calls, at
`$0.0000` on every row of every MANIFEST.

## 4. The pre-registered read

Every bar is quoted from the instrument that owns it and no other, on the new bytes, beside its
baseline-8 value and its denominator, in the memo's own order. **No bar is re-priced.**

### 4.0 §4.3's premise, read FIRST and per leg

Bars 3 and 4 read as INJUSTICE cells only because the reporter is innocent by construction, and the
memo requires all four premise conditions checked BEFORE either bar, with a VOID published as a VOID.

| condition | leg 1 | leg 2 | leg 3 | leg 4 | pooled |
|---|---|---|---|---|---|
| `killer_self_reported == 0` | 0 ✓ | 0 ✓ | 0 ✓ | 0 ✓ | 0 ✓ |
| `reporter_ejected == reporter_ejected_innocent` | 3 = 3 ✓ | 8 = 8 ✓ | 0 = 0 ✓ | 0 = 0 ✓ | 11 = 11 ✓ |
| `reporter_impostor_meetings == 0` | 0 ✓ | 0 ✓ | 0 ✓ | 0 ✓ | 0 of 626 ✓ |
| the TWIN AGREES (funnel vs `eval.reporter_justice`) | 3 = 3 ✓ | 8 = 8 ✓ | 0 = 0 ✓ | 0 = 0 ✓ | 11 = 11 ✓ |

**The premise HOLDS on every leg and pooled. Bars 3 and 4 are READ, not VOID.** The twin's agreement
is bar 3's strongest provenance and it is printed here whether it agreed or not; it agreed.

### Bar 1 — `EjecteeProofCrossTab.non_direct_accuracy`, pooled: **MET**

Target **≥ 0.60 pooled**, with no adequately powered set below 0.50, where the per-set clause is the
inherited literal `n ≥ 30` (§4, bar 1) and **NOT** §4.2's granularity test.

| set | before | after |
|---|---|---|
| `samples/9p2i` | 14/27 = 0.5185 | 10/15 = 0.6667 (n = 15, not powered) |
| `ml_corpus/9p2i` | 32/61 = 0.5246 | 36/51 = 0.7059 (n = 51, **POWERED**) |
| `samples/4p1i` | 1/5 = 0.2000 | 0/0 = n/a (empty) |
| `ml_corpus/4p1i` | 3/3 = 1.0000 | 0/0 = n/a (empty) |
| pooled | 50/96 = 0.5208 | **46/66 = 0.6970** |

**MET.** 0.6970 ≥ 0.60, and the one adequately powered set on this record's own denominators is
`ml_corpus/9p2i` at 0.7059 ≥ 0.50, so the per-set clause holds. The two 4p1i legs have an EMPTY
non-direct cell — every ejection there was direct-proof — so they enter the pooled numerator and
denominator as zeroes and bind no floor.

The direct-proof cell reads **345/345 = 1.0000** pooled, against 333/333 = 1.0000 on baseline 8: the
proof channel remains perfect and every wrongful ejection in this record sits in the no-proof cell,
which is the same shape the front door already publishes.

### Bar 2 — `MeetingFlagCrossTab` innocent-ejection total, pooled: **MET**

Target **< 35 pooled** (flagged + unflagged).

| set | before | after |
|---|---|---|
| `samples/9p2i` | 13 | 5 |
| `ml_corpus/9p2i` | 29 | 15 |
| `samples/4p1i` | 4 | 0 |
| `ml_corpus/4p1i` | 0 | 0 |
| pooled | 46 | **20** |

**MET.** 20 < 35. The wrongful-ejection total fell by 56.5% against baseline 8 on the same
instrument and the same four sets, and nineteen of the twenty sit in the unflagged cell (§3.4).

### Bar 3 — `ReporterJusticeCells.reporter_innocent_ejections`, pooled: **MET**

Target **≤ 12 pooled**, read through `pool_reporter_justice`.

| set | before | after |
|---|---|---|
| `samples/9p2i` | 7 | 3 |
| `ml_corpus/9p2i` | 23 | 8 |
| `samples/4p1i` | 4 | 0 |
| `ml_corpus/4p1i` | 0 | 0 |
| pooled | 34 | **11** |

**MET.** 11 ≤ 12. The absolute count of the injustice this phase was built against fell by 67.6%.
The per-slot reading moved with it: reporter **11/626 = 1.76%** against innocent non-reporter
**8/1875 = 0.43%**, a relative risk of **4.12x**, against baseline 8's 5.48% / 0.65% and RR 8.50x.

### Bar 4 — `ReporterJusticeCells.reporter_share_of_innocent_ejections`, pooled: **MISSED**

Target **< 0.40 pooled**.

| set | before | after |
|---|---|---|
| `samples/9p2i` | 7/13 = 0.5385 | 3/5 = 0.6000 |
| `ml_corpus/9p2i` | 23/29 = 0.7931 | 8/15 = 0.5333 |
| `samples/4p1i` | 4/4 = 1.0000 | 0/0 = n/a |
| `ml_corpus/4p1i` | 0/0 = n/a | 0/0 = n/a |
| pooled | 34/46 = 0.7391 | **11/20 = 0.5500** |

**MISSED.** 0.5500 is not < 0.40. The Wilson interval from the memo's only interval producer
(`eval/deduction_metrics.py::_wilson_interval`) is **[0.3421, 0.7418]**, against baseline 8's
34/46 = 0.7391 [0.5974, 0.8440]. **That interval CONTAINS the 0.40 target.** It is reported as
context, not as a test: every bar in this memo is a POINT-ESTIMATE bar (§4.2's reading convention),
and "the interval contains the threshold" is explicitly NOT the advisory test — applied as one it
would make every bar here advisory. The point estimate is 0.5500 and the bar is MISSED.

**What bar 4 is FOR, in the memo's own words, written before these bytes existed:**

> Bar 4 bites in the case bars 2 and 3 cannot see — a record that fixes the reporter class in
> ABSOLUTE terms and fixes the rest of the ledger too, leaving the reporter still dominant in what
> remains: **`R = 10`, `I = 20` passes bars 2 and 3 and fails bar 4 at 50%.** That is the outcome
> this phase would most want to mistake for success, and it is the only thing bar 4 is for.
> — `audits/audit-phase-21-preregistration.md:365-372`

**This record read `R = 11`, `I = 20` — one event away from the configuration the memo names, and on
the wrong side of it.** The memo did not describe a hypothetical; it described this record, a phase
in advance. Bar 4 fired exactly where it was aimed, and the honest reading of the miss is that the
pre-registration anticipated it and the record produced it.

**The composition, from this record's own cells.** Split bar 2's total both ways:

| wrongful ejections | baseline 8 | this record | move |
|---|---|---|---|
| reporter | 34 | 11 | **−67.6%** |
| non-reporter | 12 | 9 | −25.0% |
| **total (bar 2)** | **46** | **20** | −56.5% |

and the same ordering holds per slot: the reporter's own ejection risk fell **5.48% → 1.76%
(−68.0%)** while the innocent non-reporter's fell **0.65% → 0.43% (−33.9%)**. The reporter channel
closed FASTER than every other route; the share stayed high because the reporter DOMINATED the
starting composition — 34 of 46 — and a share is invariant to a cut applied evenly. Had the other
routes fallen at the reporter's own rate the share would read 0.7391, exactly where it started.
**This is the mechanism, not a mitigation: it is precisely the `R` fixed in absolute terms with the
rest of the ledger fixed too that the memo said bar 4 was built to catch.**

#### The structural null beside bar 4 (the hardening's required reading)

`audits/audit-phase-21-hardening.md:266-271` requires the record audit to print the per-row uniform
null beside bar 4, because the hardening feared the null would RISE toward 0.50 as bar 2 succeeded —
shrinkage strips the large-roster rows first, and at three living players an innocent ejection is a
choice between two innocents. A share bar read against a rising null would get harder to pass exactly
as the record got better.

**The method, so it can be re-run rather than believed.** For each wrongful ejection at a body-report
meeting, let `I` be the number of living INNOCENT players at that meeting; a process that ejects an
innocent at random hits the meeting's reporter with probability `1/I`. The per-row null is `1/I` and
the pooled null is its mean. Living players are the meeting's ballot casters; roles come from the
committed `eval.validity.roles_by_seed` re-seeding, never from the role-firewalled replay. The proxy
reproduces the hardening's own baseline-8 figures: pooled null **0.3152** at n = 46 (the hardening
states 0.32), **12** three-living rows of the 46 (the hardening states 12), and those rows' null
exactly **0.50** (the hardening states 50%).

| | baseline 8 | this record |
|---|---|---|
| wrongful ejections at a body-report meeting | 46 | 19 |
| pooled per-row uniform null | **0.3152** | **0.2553** |
| observed reporter share on those rows | 34/46 = 0.7391 | 11/19 = 0.5789 |
| three-living rows | 12 of 46 (null 0.50, observed 12/12) | **1** of 19 (null 0.50, observed 0/1) |
| exact Poisson-binomial P(X ≥ observed \| the row nulls) | 1.27 × 10⁻⁹ | **0.0024** |

**The null FELL, 0.3152 → 0.2553. It did not rise toward 0.50, and the hardening's fear did not
materialise** — because the two 4p1i legs, which supplied 4 of baseline 8's three-living rows and all
of its `samples/4p1i` wrongful ejections, produced **zero** wrongful ejections on this record. The
three-living stratum went from 12 rows to 1.

**So 0.40 was reachable on these bytes.** The structural floor a blind process would produce is
0.2553, well below the target; the bar was not asking for something the roster made impossible. And
the observed 0.5789 sits above that null by more than chance comfortably explains, so the reporter
channel is still a real channel and not an artifact of who happened to be alive.

**The tail is exact rather than approximate, because the rows are not exchangeable.** Each row's null
is `1/I` for that meeting's own living-innocent count, and on this record those take five distinct
values — 0.1667, 0.2, 0.25, 0.3333 and 0.5 — so `Binomial(n, mean p)` is the wrong distribution for
the sum. The tail below is the **Poisson binomial**: the exact distribution of a sum of independent
non-identical Bernoulli draws, computed by the standard O(n²) convolution over the individual row
probabilities. On this record it gives **P(X ≥ 11) = 0.0024** against the identical-p binomial's
0.0027; on baseline 8, **1.27 × 10⁻⁹**.

```python
def poisson_binomial_pmf(ps):          # P(sum = k) for independent Bernoulli(p_i)
    pmf = [1.0]
    for p in ps:
        nxt = [0.0] * (len(pmf) + 1)
        for k, v in enumerate(pmf):
            nxt[k] += v * (1.0 - p)
            nxt[k + 1] += v * p
        pmf = nxt
    return pmf
# tail = sum(poisson_binomial_pmf(row_nulls)[observed_hits:])
```

**The caveat, stated rather than buried: the rows are not fully independent.** The 19 rows come from
18 distinct games, so one game contributes two of them, and wrongful ejections within a game share a
roster and a run of play; the Poisson binomial assumes independence across rows and that assumption
is only approximately true here. **This is an OFFLINE READING, published under memo §5's
observed-never-gated rule.** No bar, tripwire or §9.2 criterion reads it, it did not enter the
verdict, and it is not a significance test the record relies on — it is a sanity check on whether the
reporter share could plausibly be an artifact of who happened to be alive, and it says not.

(Bar 4's own registered reading is 11/20 = 0.5500 over ALL wrongful ejections. The null is computed
over the 19 of those 20 that occurred at a body-report meeting, because only there does a "body
reporter" exist to be the null's target; the twentieth was at an emergency meeting. All 11 reporter
ejections are in the 19.)

#### The flip cost, in the record's own units

| operation | what it would take |
|---|---|
| reclassify reporter → non-reporter (bar 2's total held at 20) | **4** reclassifications: `R = 7`, 7/20 = 0.3500 passes; `R = 8` reads exactly 0.40 and does not |
| vanish reporter ejections outright (non-reporter held at 9) | **6** vanished: `R = 5`, 5/14 = 0.3571 passes |
| hold `R = 11` and grow the wrongful total | **+8** more wrongful ejections, to 28 — a worse record on bar 2 |

**No set passes bar 4 on its own**: `samples/9p2i` 3/5 = 0.6000, `ml_corpus/9p2i` 8/15 = 0.5333, and
the two 4p1i legs have an empty cell. The bar is pooled and has no per-set clause, so this is
context; it also means the miss is not one leg's.

#### The hardening's §4.1 reading notes, beside the reporter cells

Required by the DoD, each as one line, with this record's own reading where the note names a cell
this record re-reads. None of them moves a bar.

| note | the hardening's reading (baseline 8) | on this record |
|---|---|---|
| **H-26** | the reporter lever adds ZERO bytes to the ballot, and 102 of 102 ballots that ejected a reporter already carried the exculpation paragraph | R-15 reads **0 ballots gaining a reporter block** on all four legs (§2.4) — the lever's ballot footprint is still exactly zero |
| **H-21** | the exculpation forbids only the naked report-accusation — 17–24 of the 1,041 accusations naming a reporter; the charges that convict cite a sighting or a transit | unchanged in kind: the record's convictions still run through sightings and transits, and C-9 shows 100% of ballots carrying the source-count block (§2.4) |
| **H-20** | the source-count block credits an "account" for any record-matched sighting, so on 37 of the 43 wrongful convictions with a row it prints ≥1 account, and on 13 accounts == voices | the record's wrongful convictions fell to 20, of which **16 have no first-hand source at all** (C-2, §3.5 — 16/409 ejections pooled) |
| **H-23** | an impostor speaker is credited as an account 190 times, 119 of them against the meeting's own reporter, and in 17 of the 46 innocent ejections | the channel is open at this slate too — the co-discoverer seat is **48.4% impostor** (§3.7), so an impostor is still credited as an account about half the time it can be |
| **H-24** | the first-hand/adopted split publishes a record-match verdict on every spoken sighting to every voter, impostors included — the same disclosure a `vent_sighting` flag already makes | unchanged: T-6 reads **100% of location accounts reaching the alibi map** on every leg (§2.4), so the disclosure is total by construction |
| **H-25** | the block has no row for the ejectee in the three guard-REDIRECT innocent ejections | the record carries **72 redirected ballots** on leg 2 and 21 on leg 1, all eject-directed; the ejectee-row gap is a property of the block and is unchanged by this record |
| **H-28** | a living impostor's ballot is pivotal in 16 of the 46 innocent ejections, and 24 of the 46 flip on removing ANY one ejecting ballot — thin margins, not a single adversary | the margins are still thin: leg 1's ejecting-ballot census shows **5 pile-driver rows with follower counts of 1-2**, and leg 2's 60 ejecting ballots carry 36 hearsay citations (§3.5's ballot census) |
| **R2-belief-1, -2** | the belief line is silent on the ejectee in 90 of the 150 ballots that convict an innocent (83 read `this meeting +0.00`, 7 carry no row) against 17 of 1,558 on the guilty side, and **the levers add nothing to that channel** | unchanged by construction — none of the three Wave-2 levers writes the belief line, and B-1m1 reads the meeting-1 render budget **identical between the run's own OFF and ON columns** on all four legs (§2.4) |
| **R2-fourp-1, -2** (three-living) | 127 of 672 meetings run at exactly three living players; the uniform null there is 50% against 30% elsewhere, and the pooled null RISES as bar 2 succeeds | measured above: the pooled null **FELL** 0.3152 → 0.2553 and the three-living stratum fell from 12 wrongful-ejection rows to **1**, so the predicted rise did not occur on these bytes |

### 4.5 Eligibility, per lever — published, graduating nothing

§6's eligibility test asks, conjunctively, whether a lever's own RENDER predictions held on the
recorded bytes, whether any of the seven §8.1 tripwires fired against it, and whether it is
independently stampable. The render predictions are executed by the committed reader whose cells
#422 and #423 merged for exactly this purpose (§2.4), so they are read from it rather than re-derived.

| lever | its render cells | held on all four legs? | any tripwire against it? | stampable? | **ELIGIBLE** |
|---|---|---|---|---|---|
| `reporter_reasoning` | R-13, R-14 (T2), R-15 (T3) | yes — 100% of openings and non-reporter speech turns gained their block; 0 ballots gained a reporter block | none fired | yes (one resolver, one key) | **yes** |
| `corroboration_discipline` | C-9 (T6) | yes — 943/944, 2495/2495, 117/117, 129/129, every leg ≥ 99% | none fired | yes | **yes** |
| `testimony_shapes` | T-6 (T4), T-7 (T1), T-9a/T-9b (T5), B-1m1 (T7) | yes — the alibi map reaches 100% on every leg, 0 vent accounts name a non-venter, 0 impostor prompts gained the elicitation block, and the meeting-1 render budget is identical OFF and ON | none fired, **including T1 and T5, the two NEVER-WORSE bars** | yes | **yes** |

**All three levers are ELIGIBLE and none of them graduates.** Eligibility decides nothing about the
bars; it records that each lever rendered what it was predicted to render and that nothing got worse
where it touched. An eligible lever keeps its default-OFF gate and graduates at the next record made
at its own slate. The reason is mechanical rather than stylistic: graduating a SUBSET would break
both records, because `api/replay_loader.py::_assert_substrate_matches` compares a recording's
stamped slate against `substrate_flag_snapshot()` across every `SUBSTRATE_FLAG_KEYS` entry and fails
loud on any difference.

## 5. The verdict

| bar | cell | target | baseline 8 | this record | verdict |
|---|---|---|---|---|---|
| 1 | `EjecteeProofCrossTab.non_direct_accuracy` pooled | ≥ 0.60, no powered set < 0.50 | 50/96 = 0.5208 | 46/66 = 0.6970 | **MET** |
| 2 | `MeetingFlagCrossTab` innocent ejections pooled | < 35 | 46 | 20 | **MET** |
| 3 | `reporter_innocent_ejections` pooled | ≤ 12 | 34 | 11 | **MET** |
| 4 | `reporter_share_of_innocent_ejections` pooled | < 0.40 | 34/46 = 0.7391 | 11/20 = 0.5500 | **MISSED** |

§6's rule is **ADOPTED iff all four of bars 1, 2, 3 and 4 are met, FINDING otherwise**. It is
conjunctive, it names its subset exactly, and it has no "and/or", no waiver and no substitute. Bar 4
is missed.

**VERDICT: FINDING.**

The three Wave-2 levers stay live toggles. `orchestrator/replay.py`'s registry is unchanged — twenty-one
retired always-on levers and four live toggles. The ladder tip does not move and stands at baseline 8.
The canonical sets keep their baseline-8 bytes. No subset graduates under any verdict.

This record was taken to find out, and it found out. Three of the four bars the pre-registration set
before these bytes existed are met, several of them comfortably. **The fourth is the one the memo
said it was building for, and it fired exactly where it was aimed:**

> a record that fixes the reporter class in ABSOLUTE terms and fixes the rest of the ledger too,
> leaving the reporter still dominant in what remains: **`R = 10`, `I = 20` passes bars 2 and 3 and
> fails bar 4 at 50%.** That is the outcome this phase would most want to mistake for success, and it
> is the only thing bar 4 is for.
> — `audits/audit-phase-21-preregistration.md:365-372`

This record read **`R = 11`, `I = 20`** — one event from that configuration, described a phase before
the bytes existed. The reporter channel did close faster than every other route (34 → 11 against
12 → 9; 1.76% against 0.43% per slot), and the structural null it is read against FELL rather than
rose (0.3152 → 0.2553), so 0.40 was reachable and the miss is not an artifact of who was alive
(§4, bar 4). That is what "the outcome this phase would most want to mistake for success" looks like
from the inside, and it is why the bar was written.

Whether that is grounds for an owner override is an owner's question and not this audit's — and if
one is made, it is recorded as an override of a FINDING verdict, in the shape
`audits/audit-phase-20-baseline-7.md` §6.1 set, and **never as a bar that passed**.

## 6. Where the bytes landed, and what did NOT move

### 6.1 The recording, preserved as non-canonical evidence (PROVISIONAL)

Every game this record produced is stamped with the three Wave-2 keys `True`. On the FINDING branch
those keys stay live toggles that resolve `False` in a bare shell, so an ON-stamped recording under a
default-OFF slate CANNOT reconstruct in a bare environment:
`api/replay_loader.py:655`'s `_assert_substrate_matches` compares the recorded `True` against a live
`False` and REFUSES the game. Overwriting the canonical sets would therefore break the bare
`bash scripts/verify_samples.sh` leg, the served frontend and the phase close's own gate rerun — the
§10.1 mechanism arriving as a self-inflicted wound. So the canonical sets stayed exactly where they
are, and the recording is preserved at a named path outside them.

**Prerequisite (G8) was UNRULED at dispatch**, so this record executed the orchestrator's
recommendation: **a class-(c) orphan evidence commit**, its tip sha pinned in an in-tree class-(b)
manifest and fetched by that sha, never in the working tree — the rule `docs/artifacts.md:51-58`
already sets for raw per-seed recordings "read only when someone audits a specific claim". No test
opens a finding record, so class (a) does not apply. As executed:

| | |
|---|---|
| pinned commit | `evidence/phase-21-wave2-finding` @ `29af85d5457caeba4f8ba8ba77610c6a0ab2213a`, parentless |
| what is on it | **316 files, 260,116,543 bytes** — the four set directories with their MANIFESTs, eval reports, `splits.json`, rosters, the operator's resume state, and a README whose first line states the reconstruct rule |
| what is in the tree | 2 files — `replays/records/phase-21-wave2-finding/{EVIDENCE-MANIFEST.md,README.md}`, 40 KiB, holding the pin, the per-file `sha256` digests and the restore command |
| registration | TWO `docs/artifacts.md` rows — a class-(b) row for the in-tree wrapper (added to `scripts/verify_ml_evidence.py`'s `_IN_TREE_PROBES` **and** `_IN_TREE_INVENTORY`) and a class-(c) `pinned sha` row for the payload (added to `_EVIDENCE_PREFIXES` and the manifest parser) — with planted cases proving a stated count that disagrees with `git ls-files` fails and that a restored byte which does not match its digest fails |
| composes in both directions | `bash scripts/check.sh` is green with the recording RESTORED and green after `--clean` — 6,039 passed either way. Getting there fixed a real defect this landing surfaced: `tests/orchestrator/test_replay.py::_committed_substrate_stamps` globbed `replays/**` and so walked the restored bytes, whose stamp differs from a bare build ON PURPOSE, making a gate result depend on whether an operator had run the restore. It now reads the git INDEX, which is what "committed" meant all along |
| verified, not described | `scripts/fetch_evidence.sh` fetches both pins, refuses a parented commit, restores untracked behind a generated `.gitignore` and re-hashes everything: **3269/3269 files match**. `--complete` reads `FAIL 0 / ABSENT 0` restored against `ABSENT 7` bare. The manifest DECLARES the lever slate, and the reconstruction leg reconstructs all four restored sets under it — **50/50, 150/150, 50/50, 50/50** — with the ambient slate unset, so the recording is READ and not merely hashed |

The pin is a SHA and not a branch name, which is the immutability guarantee: restored bytes are the
bytes the manifest hashed or the digest check fails, and they are untracked by design and never
committed back.

The payload is registered as class-(c) evidence through the same machinery Phase 18 uses, generalised
to a second family rather than described in prose: `scripts/verify_ml_evidence.py` parses this
manifest's digest block, carries a `wave2-finding/` class-(c) registry row, and reports the recording
**ABSENT** on any checkout that has not fetched it — so `--complete` cannot be satisfied by a tree
that merely holds the sidecars. `scripts/fetch_evidence.sh` fetches by sha, asserts the commit is a
parentless orphan, restores the bytes untracked behind a generated `.gitignore`, and hash-verifies
them; `--clean` removes exactly what it placed. The cycle is exercised in this PR: **3269/3269 files
match** — the 1,384 + 1,569 + 316 digest rows the three manifests carry, with each commit's own
README excluded from the restore and then verified independently out of its own pin — and
`--complete` reads `FAIL 0 | ABSENT 0` restored against `FAIL 0 | ABSENT 7` bare.

**This is PROVISIONAL.** If the owner rules for the in-tree class-(a)+(b) mechanism, the bytes move
into `replays/records/phase-21-wave2-finding/` itself and the row's class and size cells change with
them; the probes, the inventory scope, the manifest parser and the planted cases are already in place
and carry over. Nothing in the read changes either way.

**(G8) is decided AT THE GATE, and this PR is the gate.** The contract's prerequisite block makes the
landing mechanism an owner decision at dispatch with the orchestrator's recommendation as the
provisional fallback; this PR is owner-gated and stops open, so the owner's merge — or a ruling
before it — IS that decision, taken with the mechanism working and its cost visible rather than
described.

### 6.2 The FINDING no-ops, each one a checked no-op rather than a silence

The canonical cells did not move, so the consumers that read them did not move either. Each is
recorded with the reason rather than passed over:

| surface | state | why |
|---|---|---|
| `replays/samples/**`, `replays/ml_corpus/**` | UNTOUCHED | `git diff --stat` shows no byte moved under either root; `bash scripts/verify_samples.sh` bare still reports 100/100 on them |
| the byte-coupled re-pin sweep (54 test files + 4 frontend files) | NO-OP | the bytes those pins read did not move; `tests/meetings/test_contradictions.py:3242`'s `_COMMITTED_MEETINGS = 672` and every census that sums to it still describe the canonical sets |
| `frontend/src/lib/bodies.test.ts`, `contradictions.test.ts` `corpusSha256` | NO-OP | both digests are computed over `replays/samples`, which is unchanged |
| `eval/watchability.py::_BASELINE_SUPPLY_FLOORS`, `_DEFAULT_BASELINE_ID` | NO-OP | no successor baseline is minted; the referee still reads baseline-8 floors over baseline-8 bytes |
| `training/bakeoff/harness.py:186` `BAKEOFF_BASELINE_ID` | NO-OP by design | it moves only at an ML re-ground, and `training/` is out of scope |
| each set's `tournament-eval-report.json`, `results-rubric-score.json` | UNCHANGED | the served set is still baseline 8's, so no recipe was re-run over bytes that did not move |
| `scripts/check_doc_facts.py` `_LADDER_TIP_AUDIT`, `_WIN_SPLIT_HEADER` | UNCHANGED | they stay on `audits/audit-phase-21-rerecord.md` and `baseline-7 impostor rate`; `check_conviction_partition` and `check_verdict_figures` parse the named audit's bars against README's live figures, and pointing them at a lever-ON audit whose bytes are not canonical would either fail the checker or re-pin the front door to evidence this record did not adopt |
| `README.md`, `docs/reading-guide.md` | UNCHANGED | no front-door cell moved |
| `.env.example` | UNCHANGED | all three Wave-2 keys stay documented as live toggles in the `# AILIBI_*=0` shape `check_lever_registry` requires |
| `scripts/verify_ml_evidence.py` — the grounding-gap / STALE mechanism | UNCHANGED | nothing re-records the corpus, so no gap is re-declared and `grep -c STALE scripts/verify_ml_evidence.py` still reads **0** exactly as 21.17 left it |
| `scripts/verify_ml_evidence.py` — the evidence registry | **CHANGED** | the FINDING record's in-tree wrapper and its class-(c) payload are registered (`_IN_TREE_PROBES`, `_IN_TREE_INVENTORY`, `_EVIDENCE_PREFIXES` and the manifest parser), which is what makes the new `docs/artifacts.md` rows legal and what makes `--complete` report the recording ABSENT on a checkout that has not fetched it |
| `scripts/fetch_evidence.sh` | **CHANGED** | taught the second evidence family, so the pinned bytes are fetched by sha, restored untracked and hash-verified rather than described in prose |
| `orchestrator/replay.py`, `meetings/{manager,corroboration,constants}.py`, `orchestrator/game.py`, `agents/strategic/prompts/loader.py` | UNCHANGED | no resolver is deleted, because no lever graduated |

### 6.3 The one thing that DID move: the seed-13 featured card

The card is FALSE on the served baseline-8 bytes today — it claims five meetings where the served
game has three, of 7, 6 and 5 spoken turns (`audits/audit-phase-21-rerecord.md` §5.1.1c) — and a
FINDING record may not leave it standing by silence. No `OWNER RULING` line exists in
`tasks/phase-21.md` on `origin/main`, so the contract's default copy is used, with a machine check
beside it in `tests/api/test_sets.py` reading the three meetings' spoken-turn counts through the set
loader and asserting `(7, 6, 5)`. The blurb stays spoiler-free under the binding rule at
`ReplayPicker.tsx:108-113`. Cards [1] and [3] carry copy that is misattributed rather than false
(H-34/H-39) and are repaired with the strip's re-curation at whichever record adopts.

## 7. What this record does NOT discharge

* **The graduation sweep (21.25).** No lever graduated, so nothing was swept. The sweep's own scope —
  the lever parameters threaded through call sites, the dead OFF-path branches, the tests that
  exercise the OFF arm, the `.env.example` entries and the prose — is untouched and unowed.
* **The ML grounding state.** It is exactly as 21.17 left it: the fits are grounded against the
  baseline-8 corpus, which this record did not replace. No STALE amnesty is re-declared, no digest
  pair is named, and the second re-fit is not scheduled. If a later record adopts, the re-declaration
  this contract specifies becomes due at that record and not before.
* **The narrative reading of the results table.** 21.25 owns the before/after prose. This record
  moved no front-door cell.
* **The husk `free_text` wording (item (b)).** Deferred to the close ledger with its trigger class
  now named from live bytes (§2.5).
* **Any judgment about whether bar 4's target was the right target.** The memo owns the bars, and on
  this record bar 4 did its stated job (§4, §5) rather than misfiring. One structural observation is
  routed to the close ledger for the NEXT pre-registration to weigh, and it is an observation and not
  a complaint: a SHARE bar and a COUNT bar registered on the same cell can pull against each other,
  and here they did — at the record's 9 non-reporter wrongful ejections bar 4 needed `R ≤ 7` (holding
  the total) while bar 3 asked for `R ≤ 12` and got 11. That is a fact about how the two were
  parameterised together, not about these bytes, and it is never a retroactive edit to this memo.

## 8. Provenance and co-interventions

**Provenance tuple.** Model `Qwen/Qwen3.6-27B` (Task 16.2 lock) on Featherless at the pinned
endpoint, prompt set `qwen3_6_27b`, the composite lever-ON prompt-version stamp quoted in §0.4,
tactical policy `fsm-default` on every game, `$0.0000` on every MANIFEST row, source state
`44f0a28c`, **33 stamped `git_sha` values — 31 in per-seed rows plus the two corpus FROZEN-line
stamps (`0747ce2d`, `3fdd1193`) — all reconciled to 0 frozen-directory files** (§2.7), recorded
2026-09-03 – 2026-09-04.

**Co-interventions, by name, with their attribution consequence.**

1. **PR #424's un-bumped ballot body** (prerequisite (h)). One line inside the lever-guarded
   `<testimony_sources>` block of `vote_ballot.j2` changed without a version bump, so the composite
   stamp names two lever-ON ballot bodies — the certified smoke's (source state `14854a06`) and this
   record's (`44f0a28c`) — separable only by the MANIFEST's `git_sha`. **Consequence:** this
   record's cells are not byte-comparable with the smoke's ballot cells except through that sha, and
   every leg's shas are published in §2.7. The OFF bytes are untouched, so the before column is
   unaffected.
2. **The before column is itself a fresh record** (21.15's maintenance re-record), not Phase 20's
   baseline 7. **Consequence:** a cell that moved here moved against a substrate whose fidelity
   defects — the discarded-action manifest, the double-minted vent, the ballot-time testimony render,
   the last-seen feed — were already repaired, so the movement is attributable to the Wave-2 slate
   rather than to those repairs.
3. **The three Wave-2 levers moved together, all-or-none by construction.** **Consequence:** no bar
   may be attributed to a lever, and none is. §4.5's eligibility lines are RENDER statements, not
   attribution.
4. **Two operator sessions and one reaped background task on leg 2.** **Consequence:** leg 2's wall
   is reported as recording wall with the dead time named (§2.6); no byte is affected, and the
   checkpoint discipline means every recorded seed was pushed to the branch before the next began.

## 9. Method — every derived figure reproduced offline at $0

All of the following read committed or staged bytes and make no provider call. The lever-ON shell is
the block in §0.4; the bare shell has no `AILIBI_*` export.

```bash
# per leg: the validity gate with the DERIVED map (never a retyped one)
uv run python scripts/validity_gate.py <leg dir> --expected-model Qwen/Qwen3.6-27B \
  --expected-prompt-versions "$(the corpus recorder's REQUIRED_PROMPT_VERSIONS_CLI line)" \
  --require-zero-cost

# per leg: the lever-ON tripwire reader — exit 0 with stopped_cells empty is the requirement
uv run python scripts/counterfactual_phase21.py --recording <leg dir> --recorded-slate on --json

# bars 3 and 4, and §4.3's premise twin
uv run python -m eval.reporter_justice <leg 1> <leg 2> <leg 3> <leg 4> --pooled
uv run python scripts/measure_baseline.py --funnel --json <leg dir>

# bars 1 and 2, from each leg's own tournament-eval-report.json
#   bar 1 = deduction.ejectee_proof_cross_tab.non_direct_impostor / .non_direct_ejections, summed
#   bar 2 = deduction.meeting_flag_cross_tab.{flagged,unflagged}_ejections_innocent, summed
#   direct proof = .proof_present_impostor / .proof_present_ejections, summed

# the instruments the Measurement line names
uv run python scripts/measure_baseline.py --honesty      <leg dir>
uv run python scripts/measure_baseline.py --vj           <leg dir>
uv run python scripts/measure_baseline.py --solvability  <leg dir>
uv run python scripts/measure_baseline.py --watchability <leg dir>

# the (deadline_default) hand scan, BOTH shapes — the smoke report's §17.4 reader
# the spoken-kill outcome read — the smoke report's §17.7 reader, widened to §8.5's columns,
#   with roles from eval.validity.roles_by_seed and never from the replay
```

The win split is re-derived by counting `winner` over each set's `tournament-eval-report.json`
`report.games`. The per-leg token ratio is re-derived by the §17.4 reader over the leg's own bytes
against the committed baseline-8 set it would have replaced. The `git_sha` reconciliation is
`git diff --name-only 44f0a28c..<sha> -- agents meetings observation orchestrator` for every distinct
sha in each leg's MANIFEST.
