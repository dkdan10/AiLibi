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
| (a) the freeze-guard reconciliation | **DISCHARGED** — landed in PR #427 (`608ae1f6`): a non-opening `deadline_default` row RE-RECORDS the seed at freeze and does not abandon the run, with the re-record allowance priced outside §12.2's bracket, and routing (e) putting the samples legs' scan in the operator's hand. **It was exercised: five re-record rounds over four seeds, all on leg 2, every one a non-opening slot (§2.5)** |
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
baseline 9. The rule selected FINDING, so no successor is minted and **the ladder tip stands at
baseline 8**.

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
reason is legible rather than lucky: the smoke's like-for-like ratio was measured on five seeds, and
each leg's own ratio re-derived from its own bytes reads **×1.07 per meeting**, not ×1.17 (§2.6).
The smoke's own §16 item 5 says exactly this — the seed slate is not a representative token sample,
which is why the projection's low end is the all-games cross-check. Re-records are priced outside
the bracket per prerequisite (a): five rounds at 244–460 s each, ≈ 28 minutes in total.

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
| 1 | `samples/9p2i` | 50/50 | **PASS**, ten checks | exit 0, `stopped_cells` empty, 9/9 PASS | 0 under either shape | 1 (seed 3) |
| 2 | `ml_corpus/9p2i` | 150/150 | **PASS**, ten checks | exit 0, `stopped_cells` empty, 9/9 PASS | 0 under either shape | 5 rounds over 4 seeds |
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

### 2.5 The `deadline_default` hand scan, and the five re-record rounds

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
re-recorded at freeze under §9.2 as amended by PR #427, never abandoned. All five rounds fell on
leg 2:

| seed | slot | trigger | rounds |
|---|---|---|---|
| 1034 | `opt_in` turn 4 | validation — `Input tag 'corroboration' … does not match any of the expected tags` | 1 |
| 1061 | `opt_in` turns 3 and 5 | validation — same tag class | 2 |
| 1078 | `vote` | validation — `1 validation error for ModelAuthoredVoteBallot` | 1 |
| 1087 | `opt_in` turn 3 | validation — `Input tag 'alibi' … does not match any of the expected tags` | 2 |

**Every one of the five is a schema-VALIDATION failure, not a wall-clock miss**, which is precisely
the (b) legibility item the close ledger carries: `meetings/manager.py:209`'s
`DEFAULT_TURN_FREE_TEXT = "(missed deadline; no turn submitted)"` is minted for a validation failure
too, so the husk asserts a deadline miss that did not happen. The recurring trigger has a shape worth
naming for whoever fixes it: the model emits an observation whose `type` is a word from the domain
(`corroboration`, `alibi`) that is not a member of the `MeetingTurn` observation union. No husk
survives in any leg here, so the list this item asks for is empty — but the cause is recorded.

The corpus re-record flow was followed as written rather than improvised, because a present replay
carrying such a row refuses the WHOLE re-run at the pre-spend skip-scan: DELETE the replay and its
MANIFEST row → `--seeds N` → the finalizing run. 21.15 did this five times by hand over 250 completed
games; this record did it five times over 300.

### 2.6 Duration, per leg, against the projection — and each leg's own token ratio

| leg | 21.15's actual | this record | note |
|---|---|---|---|
| 1 `samples/9p2i` | 3h07m00s | **3h03m29s** | includes one killed run's lost tail and the seed-3 re-record |
| 2 `ml_corpus/9p2i` | 7h59m32s | **≈ 8h21m** recording wall | 12h03m55s elapsed across two operator sessions, less ≈ 3h21m dead after the first operator's provider-side HTTP 529 kill and ≈ 22m dead after a reaped background task |
| 3 `samples/4p1i` | 23m15s | **20m21s** | |
| 4 `ml_corpus/4p1i` | 24m41s (incomplete) | **20m30s** | complete |
| **four legs** | 11h54m28s (299 games) | **≈ 12h05m (300 games)** | against the bracket 12h47m – 16h03m |

The per-leg token ratio, re-derived from each leg's OWN bytes against the committed baseline-8 set it
would have replaced (smoke §16 item 5 — the seed slate is not a representative token sample):

| | leg 1 ON | baseline-8 `samples/9p2i` | ratio |
|---|---|---|---|
| meetings | 168 | 151 | ×1.1126 |
| calls | 1,891 | 1,740 | ×1.0868 |
| tokens | 9,717,705 | 8,134,860 | ×1.1946 |
| **tokens / meeting** | **57,843.5** | **53,873.2** | **×1.0737** |
| tokens / call | 5,138.9 | 4,675.2 | ×1.0992 |

Leg 2 reads 25,543,458 tokens over 4,996 calls and 435 meetings — **58,720.6 tokens/meeting**, within
1.5% of leg 1's — and legs 3 and 4 read 18,698.5 and 18,781.1 tokens/meeting on the far smaller 4p1i
roster. **The measured like-for-like ratio is ×1.07, not the smoke's ×1.17**, which is the whole of
the difference between the projection and the actual. The all-games total moved more (×1.19 on leg 1)
because the ON legs hold MORE meetings than the sets they would have replaced, not because a meeting
costs more.

### 2.7 The `git_sha` reconciliation

Each recorder stamps one sha at the start of its own run, and this record was taken in checkpoint
batches, so the legs carry more than one sha each: **6 / 14 / 6 / 5**, thirty-one in total. For every
one of them:

```
$ git diff --name-only 44f0a28c..<sha> -- agents meetings observation orchestrator
(no output — 0 files)
```

Every stamped sha touches **0 frozen-directory files** against the window-open sha. The full list is
in the PR body.

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
* **30 of 30 accounts were TRUE** — every named player really was an impostor. Not one fabricated
  kill account appears anywhere in 300 games.
* **16 of 30 CONVERTED** — the named player was ejected at that meeting.

Stated as counts and never as a rate, per §5's discipline. The full per-row table — speaker with
role and whether they were that meeting's reporter, the named killer with the killer's true role, the
ballot tally, the outcome, and whether any engine contradiction named anyone — is reproduced by the
reader in §9.

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

| leg | ejections | flagged ejections → impostor / innocent | unflagged ejections → impostor / innocent |
|---|---|---|---|
| 1 `samples/9p2i` | 89 | 75 → 74 / **1** | 14 → 10 / 4 |
| 2 `ml_corpus/9p2i` | 277 | 226 → 226 / 0 | 51 → 36 / 15 |
| 3 `samples/4p1i` | 19 | 19 → 19 / 0 | 0 → 0 / 0 |
| 4 `ml_corpus/4p1i` | 26 | 26 → 26 / 0 | 0 → 0 / 0 |
| **pooled** | **411** | **346 → 345 / 1** | **65 → 46 / 19** |

**One of 346 flagged ejections across 300 games took an innocent** — on leg 1 — and the other
nineteen of bar 2's twenty sit in the unflagged cell. Flagged-meeting ejection accuracy is therefore
345/346 = 0.9971 pooled. The flagged/unflagged split is a different partition from bar 1's
proof-present/non-direct split and the two are not interchangeable: proof-present reads 345 ejections
and non-direct 66, against flagged 346 and unflagged 65.

### 3.5 The corroboration cells and the render census

| cell | leg 1 | leg 2 | leg 3 | leg 4 | pooled |
|---|---|---|---|---|---|
| C-1 accused subjects with NO first-hand source | 146/396 | 372/1006 | 29/78 | 38/88 | 585/1568 |
| C-2 ejected subjects with NO first-hand source | 8/89 | 8/275 | 0/19 | 0/26 | 16/409 |
| C-3 ejections whose charge ANSWERED the ejectee's own | 4/89 | 8/277 | 0/19 | 0/26 | 12/411 |
| C-4 ejected subjects with a map-satisfied placement pair | 9/89 | 38/277 | 0/19 | 1/26 | 48/411 |

The render budget reads 39.4 / 38.2 / 10.9 / 11.5 mean rendered lines per snapshot, over 1,891 /
4,996 / 234 / 258 snapshots. `fabricated_vent_rows` is **0 on every leg**.

### 3.6 The evidence-supply floors, scored against baseline 8's block

The committed referee reads this record against the **baseline-8** floors, which were pinned from
baseline 8's own bytes, and three of the four legs FAIL them:

| leg | referee | the floors that failed |
|---|---|---|
| 1 `samples/9p2i` | FAIL (supply floors FAIL, integrity OK) | `flags_per_meeting` 0.857 < 0.974; `testimony_backed_conversion` 0.605 < 0.719; `transcript_flags_per_meeting` 0.268 < 0.377; `persisted_vent_flags_per_meeting` 0.589 < 0.596 |
| 2 `ml_corpus/9p2i` | FAIL | `transcript_flags_per_meeting` 0.303 < 0.377 (the other four PASS) |
| 3 `samples/4p1i` | FAIL | `witnessed_event_rate` 0.0152 < 0.0161; `testimony_backed_conversion` 0.559 < 0.577 |
| 4 `ml_corpus/4p1i` | PASS | — |

**This is a supply reading and not a criterion**: §9.2's abandon list does not name the referee, and
no bar reads it. It says something worth stating plainly — **the Wave-2 slate convicts more
accurately on FEWER flags.** On ADOPTED a successor floor block would have been pinned from this
record's own bytes and the comparison would have moved with it; on FINDING the canonical bytes do not
move, so `_BASELINE_SUPPLY_FLOORS` and `_DEFAULT_BASELINE_ID` are untouched (§6.2) and this table is
published as the observation it is.

### 3.7 Tokens per call, per leg

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

**MISSED.** 0.5500 is not < 0.40. The share fell by 18.9 points and stopped 15 points above the bar.

The arithmetic of the miss is worth stating because it is not a failure of the reporter channel: bar
4 is a SHARE, and its denominator is bar 2, which the same record cut from 46 to 20. The reporter's
absolute count fell faster than the bar demanded (34 → 11, bar 3 MET with a point to spare) while the
*other* wrongful-ejection routes closed faster still, so the reporter's share of a much smaller total
stayed high. That is exactly the mechanism A-4's verifier correction already named on the baseline
axis — *the headline share is high because the other routes closed, not because this one grew* — now
observed inside a single record. **It is an explanation and not a re-pricing.** The memo set 0.40
before these bytes existed, the reading is 0.5500, and the bar is MISSED.

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
before these bytes existed are met, several of them comfortably; the fourth is a share bar whose
denominator the same record more than halved. Whether that is grounds for an owner override is an
owner's question and not this audit's — and if one is made, it is recorded as an override of a
FINDING verdict, in the shape `audits/audit-phase-20-baseline-7.md` §6.1 set, and **never as a bar
that passed**.

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
already sets for raw per-seed recordings "read only when someone audits a specific claim". The four
sets weigh ~224 MB, and no test opens a finding record, so class (a) does not apply. **This is
PROVISIONAL.** If the owner rules for the in-tree class-(a)+(b) mechanism instead, the bytes move
into `replays/records/phase-21-wave2-finding/` in a follow-up, one `docs/artifacts.md` row is added
for the path, and the same path is added to `scripts/verify_ml_evidence.py`'s `_IN_TREE_PROBES` and
`_IN_TREE_INVENTORY` mappings with its planted case — nothing in this audit's read changes either
way.

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
| `scripts/verify_ml_evidence.py` | UNCHANGED | nothing re-records the corpus, no grounding gap is re-declared, and `grep -c STALE scripts/verify_ml_evidence.py` still reads **0** exactly as 21.17 left it |
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
* **Any judgment about whether bar 4's target was the right target.** The memo owns the bars. A bar
  that turned out to be a share over a denominator the same intervention improves is a fact about
  this pre-registration, and it belongs in the close ledger as an observation for the NEXT
  pre-registration to weigh — never as a retroactive edit to this one.

## 8. Provenance and co-interventions

**Provenance tuple.** Model `Qwen/Qwen3.6-27B` (Task 16.2 lock) on Featherless at the pinned
endpoint, prompt set `qwen3_6_27b`, the composite lever-ON prompt-version stamp quoted in §0.4,
tactical policy `fsm-default` on every game, `$0.0000` on every MANIFEST row, source state
`44f0a28c`, thirty-one stamped `git_sha` values all reconciled to 0 frozen-directory files, recorded
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
