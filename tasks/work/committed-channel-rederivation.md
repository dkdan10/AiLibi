# Re-derive the committed meetings through their true private channels

**Status:** ready

## Outcome

Six default-tier tests have been red on `main` since the baseline-9 re-record merged
(`acf6c604`), and none of them has found a defect in the recorded bytes. Three (T1, T2, T5)
read the recording through a records-free re-derivation. That harness inverts the sighting
channel out of recorded verdicts, rebuilds vents from recorded flags, passes no movement channel
at all, and says in its docstrings that the movement channel "is not recoverable". The channel
is recoverable: the evidence-honesty censuses already rebuild all three private channels from
the replay walk, and with the arguments production passes, that rebuild reproduces every
committed meeting. T3 and T4 are measured consequences of the route claim: a Phase-20 ratio
floor, met on earlier bytes, and an ordering whose comparand was deleted when its lever
graduated. The adjacency guard restates the detector's tick rule against the stay instead of
the route's outer ends, and its 0-as-unset sentinel can hide the very zero it exists to catch.

This card changes tests, plus one stale docstring. It gives the three private channels one
home in `tests/_helpers/committed.py`, matched field for field to the live accessors, and gates
that home: with all three channels, the re-derivation equals the recorded flags on every
committed meeting. On that ground it re-scopes T1 and T2, labelled as re-scopes rather than
repairs. It re-anchors T3, T4, T5 and the adjacency guard at the strength the design actually
holds, and it deletes the records-free stand-ins that only imitated the recording. The six ids
leave the red list, no id joins it, and no recorded byte, prompt byte, detector output or served
payload moves.

The records did surface one real rule question: a one-tick fuzz at an interior, declared stay
boundary, whose production instance is `ml_corpus/9p2i` seed 1041 meeting 1. It is routed as
S-1 and this card leaves it alone.

## Evidence

Every `file:line` in this card is at `95fb894b`, the base the three sibling cards were planned on;
re-verify at dispatch. A measured count comes from one of two places:
- the tree, with the command given in Validation;
- the orchestrator's 2026-09-23 decision memo, or its `signals.md` and `bugs_other.md`
  investigation memos. These are notes outside the tree, in
  `tasks/investigations-2026-09-23/`.

Re-measure every memo count at dispatch, and pin what you measure, not the memo's figure.

**The ruling.** Q5 of [the re-ground card](ml-reground-baseline-9.md), answered by the owner on
2026-09-23, verbatim: "Look into why the tests would still fail, if they are necessary at all,
or a separate potential path forward. Go with the recommended idea from that."

The recommended path for these six is set out in the decision memo:
- section 4 (the signals);
- section 5, item 2 (the adjacency guard);
- section 6, card B.

The record left all six red and reported them in
[the record audit](../../audits/audit-2026-09-22-process-rerecord.md) §6.4.

**The six red ids, reproduced at `95fb894b`.** Command:
`uv run pytest -p no:cacheprovider -q <ids>`. Result: 6 failed, in about 13 s on a Darwin-arm64
host.

| # | id | fails with |
|---|---|---|
| T1 | `tests/meetings/test_contradictions.py::TestGroundedProsecutionCommittedCensus::test_the_fully_grounded_leg_drops_the_whole_class` (`:4133`) | `(8, 113) == (0, 120)` |
| T2 | `tests/meetings/test_contradictions.py::TestGroundedProsecutionInjusticeShapes::test_no_committed_ejection_rides_a_strong_sighting_flag` (`:4174`) | 5 names against `[]`, the first `samples/9p2i seed 7 headless-seed-7:meeting-0` |
| T3 | `tests/agents/test_reported_testimony.py::test_reported_rows_survive_in_every_candidate_bucket` (`:930`) | `>150: kept 5927 of 7539`, under `_SURVIVAL_FLOOR = 0.80` (`:791`) |
| T4 | `tests/eval/test_evidence_honesty.py::test_the_band_change_not_the_fold_is_what_costs_first_hand_coverage` (`:4185`) | `32123 < 32037` (`:4208`) |
| T5 | `tests/meetings/test_transcript.py::TestCommittedBytesArtifactCollapse::test_rederivation_diverges_only_at_the_repaired_sites` (`:1930`) | an unclassified addition in `samples/9p2i` seed 7 meeting 0 |
| guard | `tests/eval/test_evidence_honesty.py::test_the_instrument_and_the_detector_read_one_adjacency_rule` (`:3816`) | `assert 0 >= (1 + 1)` |

**The recording, count-only.** The probe reads `entry.contradictions` over every committed
meeting; its command is in Validation.

| measure | value |
|---|---|
| meetings | 676: 145 in `samples/9p2i`, 39 in `samples/4p1i`, 449 in `ml_corpus/9p2i`, 43 in `ml_corpus/4p1i` |
| `alibi_vs_sighting` flags | 1 STRONG, 45 weak |
| committed ejections whose ejectee carries a STRONG `alibi_vs_sighting` flag | exactly {`ml_corpus/9p2i` seed 1041 `headless-seed-1041:meeting-1`} |

**The shared cause of T1, T2 and T5** (signals memo §3).

The records-free harness is `_rederive` (`tests/meetings/test_contradictions.py:3428-3440`) and
its twin (`tests/meetings/test_transcript.py:1708-1713`). They re-run the detector with:
- the sighting channel inverted from recorded verdicts (`tests/_helpers/committed.py:147-191`);
- vents rebuilt from recorded flags (the twin passes none);
- no movement channel.

The walk rebuilds the channels instead:
- It runs `eval.replay_walk.walk_replay` (`eval/replay_walk.py:455`) with the perception fold
  (`eval/evidence_honesty.py:1323-1382`).
- It projects each channel as the live accessors do (`orchestrator/game.py:3833`, `:3889`,
  `:3980`).
- It threads them as the manager does (`meetings/manager.py:1310-1354`, `:1557-1567`).

The walk-rebuilt channels reproduced 676 of 676 meetings at baseline 9, and 672 of 672 at
baseline 8.

The harness was already blind at baseline 8. The recording then held two STRONG flags in
`samples/9p2i` seed 41 meeting 2, while T1 and T2 read zero and passed.

Two controls (memo figures; re-measure them):
- Dropping the movement channel makes 68 meetings diverge. All 68 are inside the 69 that
  `_MOVEMENT_CHANNEL_DIVERGING_MEETINGS` (`tests/meetings/test_contradictions.py:3446`) pins
  today, and 17 of those 69 are `samples/9p2i`.
- Dropping the sighting channel makes 31 diverge.

The one pinned name that is not movement is `ml_corpus/9p2i` seed 1134 meeting 3, and it is the
harness's own artifact: its inversion returned an empty mapping, and
`grounded_prosecution = bool(sighting_records)` (`meetings/transcript.py:1836`) then fell back
to the pre-grounding rules.

**The existing builders drift from the live accessors** (decision memo, fact row 11).

The live move accessor drops the holder's own rows (`orchestrator/game.py:4024`), and all three
live accessors carry `observation_id`. In `tests/eval/test_evidence_honesty.py`, the move builder
(`_move_witness_records`, `:2417`) keeps the holder's own rows, and none of the three builders
(the others are `_vent_witness_records`, `:2463`, and `_sighting_witness_records`, `:3008`)
carries `observation_id`.

The censuses also pass different arguments from production:

| argument | censuses | production |
|---|---|---|
| roster | the ballot voters | the living participants (`meetings/manager.py:1310`) |
| `trigger_kind` | none | passed (`:1557-1567`) |

A refuter read 675 of 676 meetings with the builders as they stand, with one extra
`alibi_vs_sighting` flag; this was not re-measured. Keeping the holder's own rows diverges at
`ml_corpus/9p2i` seed 1035 meeting 3 (decision memo §6).

**Per test.** Signals memo §4 and decision memo §4; every figure is re-measured at dispatch.

- **T1 is a measured pin, not a design invariant.** Rule (b) keeps a STRONG sighting flag when
  two carriers stand behind it (`GROUNDED_PROSECUTION_MIN_SOURCES = 2`,
  `meetings/constants.py:46`).

  On the true movement and vent channels the census reads:

  | leg | STRONG | weak |
  |---|---|---|
  | off | 19 | 27 |
  | ungrounded | 0 | 46 |
  | fully grounded | 2 (both in 1041 meeting 1) | 44 |

  The other kinds are identical on all three legs: conflict 3 weak, physical 18 STRONG and 7
  weak, vent 455. The class docstring's bracket (`tests/meetings/test_contradictions.py:3965-3972`)
  then holds: 0 ≤ 1 recorded ≤ 2.
  Without the movement channel, the fully grounded leg reproduces today's `(8, 113)`.
- **T2's "empty" was a records-free reading.** The recorded class is the one meeting above. Its
  ejectee's only STRONG flag is the sighting flag, which is false at its own tick and true one
  tick later:
  - the witness spoke a one-tick interior stay one tick early;
  - grounding accepted it within `SIGHTING_GROUNDING_TICK_TOLERANCE = 2`;
  - the map band did not fire, because by design it measures from the route's outer ends
    (`meetings/transcript.py:3357-3387`).

  An ejectee holding a STRONG sighting flag plus a STRONG flag of another kind is inside T2 but
  outside I-3's sole-flag cell (`test_i3_sole_flag_precision_pins`,
  `tests/eval/test_evidence_honesty.py:1628`; per-victim cell at `:1638`).
- **T3 fails on a ratio; the band order it protects still holds.** The >150 bucket reads 5,927 of
  7,539 = 0.786. The route claim offers more testimony than a saturated 6,000-character render
  can hold.

  The design invariant is the salience band. Testimony sits at 60 (`agents/memory/store.py:97`),
  and a strict prefix applies the band: it stops at the first row that does not fit (`:3118-3124`).
  That invariant holds. In the 232 renders that shed a testimony row, 0 rows ranked below
  testimony survive. Renders that shed none keep 20,178 such rows.

  Planted: re-banding testimony to 25 lets 6,319 lower rows survive in the >150 renders that
  shed, and >150 survival collapses to 169 of 7,539.

  The test itself (`tests/agents/test_reported_testimony.py:956-958`) already says that kept can
  exceed offered.
- **T4's rows ordering lost its comparand.** The comparand was the lever-OFF, uncoalesced render,
  and it was deleted when the lever graduated. Since then the ordering has compared two coalesced
  renders at one character budget: margins of −137 at baseline 7, −95 at baseline 8 and +86 now.
  The coverage half holds: 28,359 covered ticks against 20,629, and 18,100 sighting rows against
  12,771 (both read from the failure at `95fb894b`).
- **T5 is a design invariant (replay determinism) measured by a lossy harness.**
  - With the true channels, all 145 `samples/9p2i` meetings re-derive byte-exactly, every kind
    included, and recorded total = re-derived total = 107.
  - Its four unexplained additions (seed 7 meeting 0 twice, seed 32 meeting 0, seed 38 meeting 1)
    are absent from the recording.
  - `_NAMED_UNCLASSIFIED_DIVERGENCES` (`tests/meetings/test_transcript.py:1871-1876`) still names
    a baseline-8 flag of seed 41 meeting 2. That meeting carries no flag on these bytes
    (`tests/meetings/test_contradictions.py:4643-4646`).
- **The adjacency guard** (bugs_other memo §2; decision memo §5, item 2, and fact row 18).
  - **The tick term.** `_endpoint_gap` (`tests/eval/test_evidence_honesty.py:3566-3578`) measures
    the sighting against the STAY. The detector measures it against the ROUTE's outer ends
    (`meetings/transcript.py:3357-3387`, commit `301993f7`). The census keeps 29 adjacent flags
    STRONG, all on multi-stay routes. For those 29 the stay gap reads 0 (26 flags), 3 (1) and 4
    (2); the route gap has a minimum of 2.
  - **The sentinel.** `min_gap = 0` (`:3641`, `:3677`) lets any later non-zero gap overwrite a
    genuine 0.
  - **Direction 1** (`:3822-3824`) is vacuous. The census's off and on legs are identical calls
    (`:3649-3658`), so `demoted` is 0 by construction.
  - **The population.** The census passes no sighting mapping, so its STRONG population is a
    pre-grounding counterfactual. Of its 29 adjacent kept-STRONG flags, the recording holds 1
    STRONG (1041 meeting 1, stay gap 0) and 5 weak; the other 23 were never minted. The record
    audit reads 26 of the 29 as within one tick of an interior stay boundary (§6.4).

**Cost** (signals memo §5). The four sets walk in about 7-9 s on the Mac, once per worker per
file under `--dist loadfile` (`scripts/check.sh:41`). The spend is `$0`.

## Acceptance

- [ ] **One home for the three private channels, matched to the live accessors.**
  - **Move.** The move, vent and sighting builders move into `tests/_helpers/committed.py`,
    together with the walk that feeds them, cached per set.
  - **Yield.** For each committed meeting the helper yields its set, seed, entry, living roster,
    trigger kind and three channel mappings. A participant with no rows is omitted, as in
    `meetings/manager.py:1311-1354`.
  - **Match.** Each builder matches its accessor field for field, `observation_id` included.
    The move builder drops the holder's own rows (`orchestrator/game.py:4024`). The
    fellow-impostor guards stay. The trigger kind is derived as `meetings/manager.py:1557-1567`
    derives it.
  - **No second copy.** No test file keeps a second copy of a builder. A census that needs more
    than the channels builds its channels with these builders.

  Mechanism: the single-home scanner in `tests/_helpers/test_committed_single_home.py` registers
  the channel walk, and its immutability walk covers the cached value (only `Mapping`, `Sequence`
  and frozen records).

  Planted proofs:
  - the scanner flags a planted module that calls the channel walk on a committed set outside
    the cache;
  - a planted memory holding the holder's own move row and another subject's row keeps only the
    other subject's;
  - the three guard tests (`tests/eval/test_evidence_honesty.py:2783`, `:3365`, `:3391`) run
    against the helper's builders.
- [ ] **The gate: with all three channels, the re-derivation equals the recording on 676 of 676
  committed meetings.**
  - **Comparison.** Full model equality (every field, descriptions included), with the living
    roster, the trigger kind and every channel as production threads them.
  - **A meeting that still diverges** after the self-row and argument fixes is named in an
    explicit set, with its mechanism in the docstring, and Results says why. No count-only
    allowance.
  - **What it replaces.** It replaces every records-free "the OFF leg is the recorded substrate"
    comparison: `_REDERIVED_MEETINGS` (`tests/eval/test_evidence_honesty.py:2862`) where it is
    read at `:2879`, `:3434` and `:3789`, and
    `test_re_derivation_equals_recorded_on_every_committed_meeting`
    (`tests/meetings/test_contradictions.py:3533`).

  Mechanism: the gate test.

  Planted proofs (memo figures; each re-measured, and pinned at what is measured):
  - dropping the movement channel diverges 68 meetings;
  - dropping the sighting channel diverges 31;
  - keeping the holder's own move rows diverges at `ml_corpus/9p2i` seed 1035 meeting 3.

  The drop-movement plant is a committed test: dropping a channel reuses the cached channels,
  so it needs no second walk (craft rule 2). The other two are committed tests too when they
  need no second walk; otherwise each is quoted in Results with its command, and Results lists
  it as a limitation.
- [ ] **T1 is re-scoped under the owner's 2026-09-23 ruling (Q5), not repaired.**
  - **Channels.** The census (`_grounded_prosecution_census`,
    `tests/meetings/test_contradictions.py:3993`) reads the helper's vent and movement channels,
    living roster and trigger kind on all three legs. It keeps its two
    planted grounding channels (`_planted_sighting_channel`, `_ungroundable_sighting_channel`).
  - **The fully grounded leg** is re-pinned at its measured value (memo: 2 STRONG, 44 weak). The
    test is renamed to what it asserts, for example
    `test_the_fully_grounded_leg_keeps_two_strong_on_these_bytes`. Its comment says that rule (b)
    keeps a flag two carriers stand behind.
  - **The bracket.** The class docstring's bracket (`:3965-3972`) is corrected and becomes an
    assertion: ungrounded STRONG ≤ recorded STRONG (read from `entry.contradictions`) ≤ fully
    grounded STRONG.
  - **Siblings.** The sibling pins re-derive MEASURED:
    `test_the_committed_class_and_the_untouched_kinds` and
    `test_the_ungrounded_leg_convicts_on_nothing`. The scope firewall,
    `test_only_the_sighting_kind_moves`, is kept unchanged.
  - **History.** One history line: the records-free leg read (0, 120) at baseline 8, while the
    recording held 2 STRONG.

  Mechanism: the pin and the bracket assertion. Perturbed proof: the census run without the
  movement channel reads (8, 113) again, and the pin fails.
- [ ] **T2 is re-scoped under the same ruling, to the recorded set.**
  - **Source.** It reads `entry.contradictions`, which the gate proves equal to production.
  - **Assertion.** The committed ejections whose ejectee carries a STRONG `alibi_vs_sighting`
    flag are exactly {`ml_corpus/9p2i` seed 1041 meeting 1}. Adding or losing a member fails,
    after the `_STATEMENT_PAIR_CONVICTIONS` precedent (`tests/api/test_evidence_mechanisms.py:306`).
    No role is read or asserted.
  - **Naming.** The name says what the test asserts.
  - **Docstring.** It names:
    - the baseline-8 member (`samples/9p2i` seed 41 meeting 2);
    - the mechanism behind the 1041 flag, from Evidence;
    - the difference from I-3's sole-flag cell.
  - **History.** One history line records the retired claim that the class is empty.

  Mechanism: the named-set equality. Planted proof: `test_the_search_finds_a_planted_conviction`
  (`tests/meetings/test_contradictions.py:4191`) stays unchanged and green, so the predicate is
  shown to fire.
- [ ] **T5 returns to pure exactness.**
  - **Assertion.** The class walk reads the helper's channels for `samples/9p2i` and asserts no
    removed and no added flag on 145 of 145 meetings, every kind included. Recorded total equals
    re-derived total (memo: 107).
  - **Naming.** The test is renamed to that claim, and the class docstring is restated.
  - **Deleted, each with one history line:**
    - `_REPAIRED_SITES` (`tests/meetings/test_transcript.py:1928`);
    - `_NAMED_UNCLASSIFIED_DIVERGENCES` (`:1871`), including its stale baseline-8 seed-41 entry;
    - the addition allowlist;
    - the vent-kind exclusion.
  - **Helpers.** `_classify_removed_flag`, `_is_promoted_self_stated_divergence` and
    `_vent_observation_event_ids` are deleted too, once no consumer is left. At `95fb894b` only
    this test reads them.

  Mechanism: the exactness assertion. Perturbed proof: dropping the movement channel diverges
  exactly at the `samples/9p2i` meetings the helper names. By the memo's arithmetic that is 17;
  re-measure it.
- [ ] **T3 is re-anchored on the band order.**
  - **Deleted.** The flat `_SURVIVAL_FLOOR = 0.80` (`tests/agents/test_reported_testimony.py:791`)
    and its loop (`:970-976`) go, with one history line. The floor was a Phase-20 acceptance
    target, met on the baseline-7 and baseline-8 bytes; these bytes read 0.786 in the >150
    bucket.
  - **The new assertion runs per render.** A render that offered a reported-testimony row and did
    not keep it keeps no row of a class the store bands below testimony.
  - **The source.** The kept rows are read from the selector's kept list
    (`_select_within_budget`, `agents/memory/store.py:3061`), not parsed from rendered text.
  - **The lower classes are fixed by their own constants:**
    - `_SALIENCE_SAW_PLAYER_ACTIVE`, `_SALIENCE_SAW_PLAYER_MOVE`, `_SALIENCE_SAW_PLAYER`;
    - `_SALIENCE_TRANSITION`, `_SALIENCE_COMPLETED_TASK`;
    - `_SALIENCE_OWN_ROUTINE`, `_SALIENCE_COOLDOWN_STATUS`;
    - `_SALIENCE_EVIDENCE_TRAVEL` (45), `_SALIENCE_EVIDENCE_ACCOUNT_NOTICE` (16) and
      `_SALIENCE_EVIDENCE_ACCOUNT_UNCERTAINTY` (15), the evidence-context rows, which
      `_evidence_context_salience` maps (`:418-426`) and `_select_within_budget` orders in the
      same list.

    These constants are defined at `agents/memory/store.py:75-146`. The set is read once,
    before any monkeypatch, and is never derived by comparison with
    `_SALIENCE_REPORTED_TESTIMONY`, so a re-banding of testimony can fail it. The memo's
    lower-row counts (20,178 and 6,319) are re-measured over all ten classes and pinned at
    what is measured.
  - **Non-vacuity pins.** One pin counts the renders that shed (memo: 232). Another counts the
    lower rows kept in renders that shed none (memo: 20,178).
  - **Kept.** The exact offered and kept pins stay. The test is renamed to the band-order claim.

  Mechanism: the per-render assertion. Planted proof: re-banding testimony to 25 by monkeypatch,
  as T4 already does, fails it (memo: 6,319 lower rows survive).
- [ ] **T4's retired ordering is deleted.**
  - **The ordering.** `fold_only.rows_on < render_budget.rows_off`
    (`tests/eval/test_evidence_honesty.py:4208`) goes, with one history line. Its comparand was
    the lever-OFF, uncoalesced render (49,590 rows at baseline 6), and it was deleted when the
    coalesced render graduated. Rows are budget-capped (`:4145-4175`).
  - **Kept.** The pins stay (rows 32,123; covered 28,359), and so does the coverage inequality
    (28,359 > 20,629).
  - **Added.** The sighting-row inequality (18,100 > 12,771), which is the mechanism of the
    coverage gain.
  - **Naming.** The test is renamed to what it still measures.

  Mechanism: the kept pins and the two inequalities. Perturbed proof: the same census without the
  band patch is the recorded census itself, so both strict inequalities fail. This is shown once
  in Results with its command, not committed, because committing it would repeat the walk;
  Results records that as a limitation.
- [ ] **The adjacency guard reads the detector's rule, and reports the class instead of blessing
  it.**
  - **The tick term.** `_endpoint_gap` (`tests/eval/test_evidence_honesty.py:3566-3578`) measures
    from the route's outer ends through `maximal_stays`:
    - an `AlibiClaim` uses its first stay's `from_tick` and its last stay's `to_tick`;
    - a whereabouts claim uses its tick;
    - any other shape raises an `AssertionError`.

    The synthetic caller at `:3754` passes a route window. The stale baseline-6 comment
    (`:3825-3828`) is restated.
  - **The sentinel.** The minimum starts unset as `None`, so the census field becomes
    `int | None`. The assertion runs over the non-`None` gaps and requires at least one.
  - **Deleted under craft rule 3:**
    - direction 1 (`:3822-3824`);
    - the census's duplicate ON leg (`:3649-3658`);
    - the fields that read only that leg: `strong_on`, `adjacent_on`, `demoted`,
      `demoted_but_not_adjacent`;
    - the ON half of `test_i6_adjacent_room_strong_share_off_and_on` (`:3795`);
    - `test_the_ejections_that_lose_their_only_strong_flag` (`:3842`), whose ON-leg reading is 0
      by construction.

    Confirm each is vacuous before deleting it.
  - **The OFF-leg test.** `test_the_corridor_off_leg_is_the_recorded_substrate` (`:3780`) gives
    its `_REDERIVED_MEETINGS` comparison over to the gate.
  - **The new class pin** is count-only and MEASURED. It reports the kept-STRONG adjacent flags
    whose sighting sits within `MAP_ARBITRATION_MAX_TICK_GAP` (1, `meetings/constants.py:63`) of
    an interior stay boundary. The record audit reads 26 of 29.
  - **The docstring states both readings:**
    - by design, the census is a records-free, pre-grounding population: 29 kept-STRONG adjacent
      flags;
    - the recording holds 1 of those 29 as STRONG (`ml_corpus/9p2i` seed 1041 meeting 1, stay
      gap 0, the member T2 names) and 5 as weak; 23 were never minted.

    The rule question is S-1's, not this test's.

  Mechanism: the route-window restatement and the class pin.

  Perturbed proofs:
  - pointing `_endpoint_gap` back at the stay window turns the guard red again;
  - a unit case feeds the minimum fold a 0 gap after a non-zero gap, and it reads 0 (the old
    sentinel read the non-zero gap);
  - a synthetic flag one tick from an interior boundary is counted by the class pin, and one two
    ticks from every boundary is not.
- [ ] **The records-free stand-ins are retired under craft rule 3.** Each gets one history line
  and is deleted only once its last consumer has been dispositioned.

  Retired:
  - `_MOVEMENT_CHANNEL_DIVERGING_MEETINGS` (`tests/meetings/test_contradictions.py:3446`),
    `_MOVEMENT_CHANNEL_DIVERGENCES` (`:3261`), and the identity pin that reads them
    (`:3550-3551`);
  - the 451 sensitivity test (`:3553-3585`);
  - `test_the_planted_movement_channel_is_live` (`:3587`) and `_planted_move_channel` (`:3354`);
  - `_REDERIVED_MEETINGS` and its three comparisons;
  - T5's classifier machinery.

  Dispositioned by the same rule:
  - the records-free recoverable-meeting pins `_SAMPLES_9P2I_REDERIVED` and
    `_SAMPLES_4P1I_REDERIVED` (`:3855-3856`, read at `:3922-3923`);
  - the map-aware census's `off_matches_recorded` pin (`:4547`).

  `sighting_records_from_recorded_flags` (`tests/_helpers/committed.py:147`) is deleted if no
  consumer is left. The frozen baseline-8 exhibit tests
  (`tests/meetings/test_contradictions.py:4725`, `:4743`, `:5156`) read a
  meeting line with no tick rows, which no walk can rebuild. If they keep it, its docstring says
  it serves frozen exhibits only.

  Every `_rederive` consumer is dispositioned by the memo's rule; there are 21 call lines across
  the two files at `95fb894b`:
  - an assertion that claims to describe the recording moves to the helper;
  - an assertion of a transcript-level property keeps `_rederive`, with a one-line "records-free
    by design" docstring. The properties that qualify are determinism, a kind with no private
    channel, and a frozen exhibit.

  The same rule governs the vent inversions (`_vent_records_from_recorded_flags`, `_vent_channel`)
  and the structural-only vent comparison (`_VENT_STRUCT`, `_flags_match`). Results lists every
  consumer and its disposition.

  Mechanism: the `_rederive` grep in Validation, re-run at the head, lists only dispositioned
  sites. Proof: at `95fb894b` it lists 21 lines.
- [ ] **No comment still says a private channel cannot be rebuilt from the replay.**
  - **Scope.** Every such statement is corrected; the decision memo's list is the floor, not the
    ceiling.
  - **The 15 lines the Validation grep finds at `95fb894b`:**
    - `tests/_helpers/committed.py:163`;
    - `tests/meetings/test_transcript.py:1702`, `:1766`, `:1916`;
    - `tests/meetings/test_contradictions.py:3244`, `:3255`, `:3258`, `:3327`, `:3529`, `:3566`,
      `:3717`, `:4542`, `:4704`;
    - `tests/eval/test_evidence_honesty.py:2857`, `:2859`.
  - **What may survive.** A line survives only where it is true: a frozen exhibit carries no
    tick rows, and a records-free-by-design consumer says that it is one.

  Mechanism: the grep, re-run at the head, with each surviving hit explained in Results. Proof:
  the 15 hits at `95fb894b`.
- [ ] **The stale "one segment" docstring in `eval/evidence_honesty.py` is restated, and no
  other production byte moves.**
  - **The claim.** `eval/evidence_honesty.py:2295-2297` says that every committed recording
    carries a one-stay account.
  - **Why it is stale.** Baseline 9 is the first recording with multi-stay routes; all 29
    kept-STRONG adjacent flags sit on one.
  - **The change.** It is restated, docstring lines only. Its new text carries no task id.
  - **Not here.** The same sentence in the `AlibiSegment` docstring
    (`meetings/schemas.py:406-408`) reaches the provider schema, so it is routed as S-4
    (Constraints) and not edited.

  Mechanism:
  - the Validation AST check: the module's AST, with docstrings stripped, is identical to the
    merge base's;
  - `git diff --stat` against the merge base names no production file but this one.

  Perturbed proof: run on a scratch copy that carries a one-token code edit, the AST check
  names the file.
- [ ] **The six ids leave the red list, and none joins it.** Run `bash scripts/check.sh` whole,
  in a clean worktree at the head:
  - the six ids, or their renamed successors, pass. Results maps each old id to its new one.
  - no failing id falls outside the re-ground card's ML list and card C's three ids;
  - the new walk's wall cost per worker file is quoted (memo: about 9 s).

  Mechanism: `check.sh`, with the PR's CI `project-checks` job as the second reading. Proof: at
  `95fb894b` the six fail (the Evidence table).

## Constraints

**Ruling relied on.** Q5, quoted verbatim in Evidence. T1 and T2 are re-scopes under that
ruling, not repairs, and they are labelled so in their docstrings. Each retired property gets
one history line: craft rule 1 allows provenance at most one trailing line.

**Tests only.**
- No production code changes except the one docstring span in `eval/evidence_honesty.py`.
- No substrate change and no re-record.
- None of these moves: recorded bytes, prompt bytes, detector output, served payloads, fixtures,
  registry rows.

The card asks for no user-facing copy, so no task or audit id can reach any.

**Measured, never weakened silently.**
- Every pin that the self-row fix, the living roster or the trigger kind moves is re-derived
  from the helper, including the movement and grounded censuses in
  `tests/eval/test_evidence_honesty.py`.
- Results lists each moved pin old → new, marked MEASURED, with its command. The file's
  `# was` convention keeps the old value.
- The only deletions are the ones named in Acceptance, each with its history line.

**No role assertion; nothing pushes an agent toward the correct answer.**
- No test this card adds or re-anchors reads or asserts a role. Role splits already pinned are
  re-derived as counts and never promoted to a gate. Role-correctness gates nothing.
- These tests read committed bytes. None changes what an agent perceives, renders or is told.
- T2 names the recorded conviction without a role, and asserts nothing about whether it was
  right.
- The 1041 flag stays STRONG, in the recording and in every pin.

**Out of scope: routed, not scheduled.** None of these four is touched here.
- **S-1: the one-tick fuzz at an interior, declared stay boundary.**
  - Its production instance is `ml_corpus/9p2i` seed 1041 meeting 1; about 25-26 of the 29
    records-free flags share the class.
  - The candidate is a labelling variant, shipped default-OFF behind an experimental gate until
    an adopting record (craft rule 7).
  - It collides with the direction's stop on adding levers, so it is the owner's call (decision
    memo, OPEN 1).
- **S-2: the empty sighting-mapping fall-back** (`meetings/transcript.py:1836`,
  `meetings/manager.py:1345-1354`).
  - It is latent: 0 of 676 meetings are affected.
  - The records-free-by-design consumers rely on it.
  - A fail-loud change would be a detector-path change (OPEN 6).
- **S-3: a render budget for reported testimony.** Not recommended: it would be a prompt-byte
  change, and the band order already holds.
- **S-4: the stale one-segment sentence in the `AlibiSegment` docstring**
  (`meetings/schemas.py:406-408`).
  - The docstring reaches the provider. `MeetingTurn.model_json_schema()` carries it as the
    `AlibiSegment` description, the manager passes `schema=MeetingTurn`
    (`meetings/manager.py:1748`), and the Ollama client sends that schema as its `format`
    payload (`llm/ollama_client.py:176`; `tests/meetings/test_manager.py:7309-7316`).
  - The file is also in the version-two derivation closure (`training/provenance.py:108-157`).
  - Restating the sentence therefore moves a provider-schema byte. It belongs to a card that
    declares that change under Record impact, and its new text carries no task id.

**Spend.** `$0`. Fake provider only: no provider call, no `.env`, no recorder, no `--complete`,
no held-out band.

**Wall time.** About 9 s per worker file (memo). Follow each file's convention on `slow`: the
marker carries no default filter, so a marked test still runs in the gate (`pyproject.toml:94`).

**One writer per file.** This card is the only writer of the six test files in Expected scope
and of the docstring span `eval/evidence_honesty.py:2295-2297`. The other writers:

| owner | files |
|---|---|
| card A ([the re-ground](ml-reground-baseline-9.md)) | `training/` (the four training reports included), `tests/training/`, `tests/scripts/test_verify_ml_evidence.py`, `tests/eval/test_balance_eval_meeting_runner.py`, `tests/experiments/test_torch_probe_excluded.py`, `replays/ml_corpus/README.md`, `docs/artifacts.md` rows 103-104, `training/README.md`, `docs/ml-program.md`, the `docs/glossary.md` lines its new prose needs, and `scripts/verify_ml_evidence.py` only when a constraint pin moves |
| card C (`tasks/work/report-fog-and-counterfactual-freeze.md`) | `api/replay_loader.py`, `tests/api/test_view_model.py`, `tests/scripts/test_counterfactual_phase21.py`, `audits/audit-phase-21-counterfactual.md`, `docs/artifacts.md` row 109 |
| the orchestrator | `tasks/README.md` |

Inside `tests/eval/`, `tests/meetings/` and `tests/agents/`, this card writes only its named
files. It does not touch `tests/eval/test_balance_eval_meeting_runner.py`, which card A's scope
names. Card A's freeze checks run from `git merge-base origin/main HEAD`, so this
docstring-only edit cannot trip them after A merges `main`.

**Base.** `main` after the orchestrator's planning commit that lands this card.

**Status and the task index.** `tasks/README.md` is the orchestrator's.
`scripts/validate_task_docs.py` derives its inventory sentence from every card's
`**Status:**`, so any Status flip here would redden `check.sh`. The worker therefore fills
Results and leaves the Status line to the orchestrator, who flips it together with the
sentence in one commit.

**Merge order and done (identical in the three baseline-9 cards).** Card A is
`tasks/work/ml-reground-baseline-9.md`, card B is `tasks/work/committed-channel-rederivation.md`
and card C is `tasks/work/report-fog-and-counterfactual-freeze.md`. Merge order: B, then C,
then A last, after merging `main` into its branch. If A is ready first, it may merge first.
Whichever pull request merges last merges `main` into its branch first and shows
`bash scripts/check.sh` fully green on `main`. A card is done when every acceptance item has
evidence and every id still failing at its gate belongs to one of the other two cards.

This card is card B. Its done rule rests on Q5; for it, the other two cards' ids are the
re-ground card's ML list and card C's three.

## Expected scope

**Tests:**
- `tests/_helpers/committed.py`
- `tests/_helpers/test_committed_single_home.py`
- `tests/meetings/test_contradictions.py`
- `tests/meetings/test_transcript.py`
- `tests/eval/test_evidence_honesty.py`
- `tests/agents/test_reported_testimony.py`

**Comment-only** (docstring lines only): `eval/evidence_honesty.py:2295-2297`.

**This card,** for its Results.

**Nothing else.** In particular, none of these:
- `meetings/transcript.py`, `meetings/manager.py`, `meetings/schemas.py` (S-4),
  `orchestrator/`, `agents/`, `engine/`, `observation/`, `llm/`, or any template;
- `replays/`, `tests/fixtures/`, `docs/`, `audits/`, `tasks/README.md`, `training/`, `api/`,
  `frontend/`;
- the vent-inversion clone in `tests/agents/test_absence_prior.py`.

**Delivery.**
- **Branch and PR.** Branch `work/committed-channel-rederivation`, delivered as one pull request
  into `main` that populates `.github/pull_request_template.md`. Merge or fast-forward; never
  squash.
- **Commit bodies.** Each carries `Card: tasks/work/committed-channel-rederivation.md`.
- **Suggested commit order:**
  1. the helper and the gate;
  2. T5, T1 and T2;
  3. the adjacency guard;
  4. T3 and T4;
  5. the retirements and comments;
  6. the docstring;
  7. Results.

## Record impact

None.

**What stays put.**
- No recording, derived view, `docs/artifacts.md` row, fixture, rendered prompt byte, detector
  output or served payload moves.
- Gameplay, replay determinism and every replay stamp are unchanged.
- No experiment verdict is touched.

**The one byte change in production.**
- The docstring-only edit changes the bytes of `eval/evidence_honesty.py`, a function
  docstring that reaches no prompt, provider schema or served payload.
- That file is outside the 109 files the version-two derivation closure binds
  (`training/provenance.py:108-157`).
- `meetings/schemas.py`, which is in the closure and whose `AlibiSegment` docstring reaches
  the provider schema, is not edited (S-4).

**What changes for later work.**
- **Drift fails loud.** Any drift between the live accessors and the tests' re-derivation now
  fails loud at one gate, instead of being absorbed by a pinned divergence list.
- **The next re-record** re-measures these pins through production's own channels, not through
  a stand-in.

## Validation

```
uv run pytest -p no:cacheprovider -q tests/_helpers tests/meetings/test_contradictions.py tests/meetings/test_transcript.py tests/eval/test_evidence_honesty.py tests/agents/test_reported_testimony.py
uv run mypy . && uv run ruff check . && uv run ruff format --check . && uv run lint-imports
uv run python scripts/validate_task_docs.py && uv run python scripts/check_doc_facts.py

# the recording, count-only: prints 676 1 45 and the one named meeting at 95fb894b
uv run python -c "from pathlib import Path; from orchestrator.replay import MeetingReplayEntry as M, read_all_entries as r; from meetings.transcript import is_weak_contradiction as w; S=('samples/9p2i','samples/4p1i','ml_corpus/9p2i','ml_corpus/4p1i'); E=[(s,p,e) for s in S for p in sorted(Path('replays',s).glob('replay-seed-*.jsonl')) for e in r(p) if isinstance(e,M)]; F=[f for _,_,e in E for f in e.contradictions if f.kind=='alibi_vs_sighting']; print(len(E), sum(not w(f) for f in F), sum(w(f) for f in F), [(s,p.stem,e.meeting_id) for s,p,e in E if e.ejected_player_id and any(f.kind=='alibi_vs_sighting' and e.ejected_player_id in f.subjects and not w(f) for f in e.contradictions)])"

# the records-free consumers: 21 lines at 95fb894b; each survivor dispositioned in Results
grep -n "_rederive(" tests/meetings/test_contradictions.py tests/meetings/test_transcript.py | grep -v "def _rederive"

# the "cannot be rebuilt" statements: 15 lines at 95fb894b; each survivor explained in Results
grep -n -i -E "not recoverable|cannot be inverted|channel cannot be|unrecoverable|not persisted|unpersisted|cannot persist|cannot rebuild|cannot reproduce" tests/_helpers/committed.py tests/meetings/test_contradictions.py tests/meetings/test_transcript.py tests/eval/test_evidence_honesty.py tests/agents/test_reported_testimony.py

# production bytes: only the one docstring file, and docstring lines only
git diff --stat "$(git merge-base origin/main HEAD)" HEAD -- . ':(exclude)tests' ':(exclude)tasks/work/committed-channel-rederivation.md'
uv run python -c "
import ast, subprocess
def bare(src):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        body = getattr(node, 'body', None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            body.pop(0)
    return ast.dump(tree)
base = subprocess.run(['git', 'merge-base', 'origin/main', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
for path in ('eval/evidence_honesty.py',):
    old = subprocess.run(['git', 'show', f'{base}:{path}'], capture_output=True, text=True, check=True).stdout
    assert bare(old) == bare(open(path).read()), path
print('docstring-only')
"

bash scripts/check.sh   # whole, in a clean worktree
```

Results quotes these commands, plus the command behind every MEASURED pin and every planted
control, and the per-worker wall cost of the new walk.

## Results

Not started.
