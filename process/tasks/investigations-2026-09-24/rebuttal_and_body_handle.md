# Stage B, cards B3 and B4: the opener's reply and the kill-tick leak

Investigator memo, 2026-09-24. Read-only at `e886b663` (baseline 9). No live provider call, no
recorder run, no held-out band, no prompt or speech text printed. Every census below is count-only,
keyed by (set, meeting), over the four committed sets. Set names: `s9` = samples/9p2i, `c9` =
ml_corpus/9p2i, `s4` = samples/4p1i, `c4` = ml_corpus/4p1i. Citations are `path:line` at `e886b663`.

## 0. Recommendation in five lines

1. **B3.** Record the 50-seed assessment with `AILIBI_BOUNDED_REBUTTAL=1` and nothing else from that
   registry. `reporter_reasoning` stays unset. No template changes, so no committed prompt byte
   moves. Version 1 is already built. Its missing pieces are follow-through, not behaviour: replay-side
   structure checks, the golden harness, a recorder preflight for the switch, and census cells.
2. **B4.** Add one narrow, default-OFF arm that substitutes only the public handle in the trigger
   text (option b). Do **not** record with the whole `temporal_observations` lever ON (option a).
   (a) closes the leak but changes every prompt and some tactical trajectories. That confounds the
   B1/B2 assessment the 50 seeds exist for. Record the arm as the wave's dated exception to the
   direction's no-new-levers stop. It is deleted when temporal v2 graduates or when the arm itself
   is adopted, whichever comes first.
3. **Exception to (2).** If the B2 investigator rules that `evidence_reasoning_version=2` must ride
   along to make the hub regroup legible, drop the narrow arm and let B4 fold into that package.
   Evidence v2 requires temporal v2, and temporal v2 closes the leak by itself.
4. **The partial-record hypothesis holds for the other three sets but fails for s9 itself** if the
   record overwrites `replays/samples/9p2i` (section 5). Record seeds 0-49 at the 9p2i roster into
   an assessment directory outside `replays/samples`, following the Phase-21 precedent. Otherwise,
   extend eight instruments first and treat the push as a publication decision.
5. The census gate for B3 is a process count: accusations against the opener that the opener then
   answered. Today that is 0 of 561 pooled and 0 of 125 on s9. Reporter ejections are reported and
   never gate anything.

---

## 1. B3: what `bounded_rebuttal_version=1` does, exactly

**Selector** (`meetings/rebuttal.py:17-55`), a pure function of the recorded transcript:

- It walks turns in order.
- A turn's `AccusationClaim` against target T is **new** when its key has not been seen before.
  - The key is (T, speaker, sorted observations about T) when the turn carries observations about T.
  - Otherwise the key is (T, "", ()), so repeated bare prose is not new (`:38-49`).
- A new charge opens a pending opportunity for T when three things hold (`:50-53`):
  1. T has already spoken;
  2. T is living;
  3. T is not the speaker.
- A later turn by T consumes the opportunity (`:34`).
- It returns the **earliest** pending opportunity (`:55`).

**Placement** (`meetings/manager.py:1508-1539`):

- The rebuttal runs after the whole meeting has spoken:
  1. opening (`:1356-1377`);
  2. reply chain (`:1380-1430`);
  3. opt-in (`:1432-1467`);
  4. roll call (`:1469-1506`).
- It then appends **one** turn:
  - `turn_kind="reply"`, with `reply_to` and `prior_turn` set to the accusing turn;
  - rendered through the ordinary statement renderer;
  - collected with the default `retries=0` (`meetings/manager.py:1678`), so there is no retry;
  - never re-selected (`meetings/rebuttal.py:27`).
- Contradictions and ballots then read the full transcript (`:1540` onward).
- It is the last speech before the vote, and nobody can answer it.

**Who gets it.** The target of the earliest unanswered new charge, which is role-blind and
position-blind. At turn 1, the only player who has spoken other than the speaker is the opener. So
**an opener accused at turn 1 always gets the turn.** Projected on the committed transcripts
(section 3), 548 of 673 slots go to the opener, but not all of them.

**Calls and budget.**

- At most one extra call per meeting: `test_actual_manager_adds_at_most_one_reply`
  (`tests/meetings/test_reasoning_evidence.py:106-114`).
- A timed-out rebuttal defaults without retrying (`:117-121`).
- Cancellation propagates (`:124-138`).
- The call goes through the same `BudgetedLLMClient` as every turn (`orchestrator/game.py:1213-1217`),
  so `GameBudget` (`llm/budget.py:94-133`) charges it.
- The per-game 9-player caps are 1,750,000 input and 350,000 output tokens
  (`eval/balance_eval.py:136-153`, `:193-198`).
- Tournament ceilings come from `--max-total-*` (`scripts/run_tournament.py:1432-1455`). There is
  no call-count ceiling flag.

**Format.**

- It is legal at `format_version` 1 (`orchestrator/experiment_config.py:34`, `:43`, `:65-94`).
  Only evidence v2, accounts and testimony need format 2, and only investigation and contextual
  self-report need format 3.
- Probe (fake provider, 9p2i roster, seed 12): the stamp reads `format_version 1,
  bounded_rebuttal_version 1` on the tick rows.
- The plain-shell `ReplayLoader` verifies it (`outcome_verified True`).

**Prompt: no new body, no moved byte.**

- The rebuttal reuses the reply body of `accusation_round.j2` (qwen3_6_27b, stamp v6) unchanged:
  - the header;
  - the case block (`:215-222`), which says "Answer it, then redirect";
  - the crew-reply rules (alibi, whereabouts, redirect).
- No template file changes, so the `prompt_versions` stamp does not move.
- The prompt-byte golden stays green: 25 passed at `e886b663` (`tests/meetings/test_prompt_byte_golden.py`).
- Two wording imprecisions in the reused body are accepted as known limitations for this assessment:
  - `accusation_round.j2:129` says the accuser "just accused you", though the charge is usually
    turn 1 and the whole roll call has spoken since;
  - `:254`, `:275` and `:291` say "the chain follows whoever you accuse", but a rebuttal never
    extends the chain.
- If the census shows rebuttals fail to answer the charge, a guarded rebuttal frame could follow
  later. It would use the existing arm-stamp pattern (`orchestrator/game.py:511-521`), not a file
  edit.

**`reporter_reasoning` is independent and can stay OFF.**

- The rebuttal resolves from `AILIBI_BOUNDED_REBUTTAL` into `MeetingEvidenceProfile`
  (`meetings/evidence_profile.py:15`, `:61-64`, `:91-104`).
- `reporter_reasoning` resolves from the substrate snapshot (`orchestrator/game.py:1438`,
  `:1224-1233`).
- The manager builds `render_reporter_id` only under `reporter_reasoning` (`meetings/manager.py:1284`)
  and passes it to every turn, including the rebuttal. With the lever OFF there is no
  `<who_reported>` block.
- The only cross-constraint is accounts versus legacy overlays (`meetings/manager.py:1299-1302`),
  which does not involve the rebuttal.
- The harness runs the rebuttal with `reporter_reasoning=False` (`eval/reasoning_evidence.py:258-300`).
- **Gap.** The recorder's slate preflight covers substrate levers only
  (`orchestrator/replay.py:1220-1265`; `scripts/refresh_samples.sh:288-322`). A missing
  `AILIBI_BOUNDED_REBUTTAL` export would record OFF silently.

**Never run under a real model.**

- Git history:
  - introduced at `ee46d114` (2026-09-05);
  - last changed at `e12b6180` (2026-09-06).
- Every run that used it was scripted:
  - `audits/deduction-candidate/2026-09-06-mechanisms.json`: provider `scripted-deduction-control`,
    verdict `MECHANICS_ONLY`, arm `combined_with_reply`;
  - `audits/deduction-candidate/gameplay-review.md:119-124` records that the extra reporter turn
    there "repeats the same" text;
  - `audits/investigation-candidate/*.json` is scripted too, with status `NOT_AUTHORIZED`.
- The only live runs had it off:
  - the run in `audits/deduction-candidate/run-2026-09-16` stamps `bounded_rebuttal_version: null`;
  - calibration 3 set `AILIBI_BOUNDED_REBUTTAL` to `"0"`.
- No committed recording carries it.
- **The fake provider can never fire it.** It emits no claims (`llm/fake_provider.py:193`), so there
  are no accusations. The probe's rebuttal-ON game had 0 rebuttals across 4 meetings.
- So paired fake-provider development runs cannot exercise B3. The first live exercise is the record
  itself.

## 2. What version 1 breaks today (follow-through, not new behaviour)

1. **Replay structure check.** `meetings/transcript.py::walk_chain` raises on any non-`opt_in`
   turn after the chain (`:563-567`). The only callers are tests, so production is unaffected, but
   the "load-bearing replay invariant" (`:484-507`) no longer describes a rebuttal meeting.
2. **Gameplay-facts extractor.** `audits/workflows/extract_gameplay_facts.py` emits a
   "high"-severity finding for every rebuttal:
   - "Reply turn after a terminal opt_in turn" (`:1066-1086`);
   - or, when no opt-in exists, "Chain continued past its termination condition" (`:1088-1110`).
   - `scripts/refresh_samples.sh:1049-1076` runs it only when the target is `replays/samples/9p2i`.
3. **Golden harness.** It builds its manager with no evidence profile
   (`tests/meetings/test_prompt_byte_golden.py:447-459`). A rebuttal-ON recording in `_SAMPLE_SETS`
   (`:174-177`) would leave the rebuttal call unconsumed.
4. **Voices.** The rebuttal is kind `reply`, so its redirect accusation can mint an independent
   voice. Opt-in accusations cannot (`meetings/transcript.py:2266`). This is a real, if small,
   channel change to census, not a bug.
5. **Detector surface.** The crew-reply body asks for an alibi and a whereabouts. The opener's second
   account is therefore new material for contradiction checks against the opener. `ContradictionRef`
   carries the event ids to attribute it (`meetings/schemas.py:1243-1251`).

## 3. B3 census, today (count-only, reproducible)

| | s9 | c9 | s4 | c4 | pooled |
|---|---|---|---|---|---|
| meetings | 145 | 449 | 39 | 43 | 676 |
| opener accused (structured, after turn 0) | 125 | 362 | 37 | 37 | 561 |
| ... first accused at turn 1 | 120 | 328 | 37 | 36 | 521 |
| ... **accused and then answered by the opener** | **0** | **0** | **0** | **0** | **0** |
| selector would fire (v1 on these transcripts) | 144 | 447 | 39 | 43 | 673 |
| ... beneficiary is the opener | 123 | 351 | 37 | 37 | 548 |
| ... beneficiary is an impostor (not the opener) | 19 | 86 | 2 | 6 | 113 |
| ... beneficiary is another crewmate | 2 | 10 | 0 | 0 | 12 |
| ... answers turn 1 / turn 2 / turn 3 or later | 120/22/2 | 328/105/14 | 37/2/0 | 36/7/0 | 521/136/16 |

**Fidelity to "one reply for the opener".** Version 1 answers the owner's case in 548 of 561
opener-accused meetings. In 13, an earlier charge against someone else takes the slot. It also gives
125 replies to non-openers, 113 of them to impostors, typically an accused impostor re-accused by a
later speaker. That is the role-blind rule working as written, and I keep version 1 as ruled. An
opener-only variant would be a new version, and under R6 (0 impostor openers) it would give turns
to crew only.

Role cells are reported and never gated.

**Projected spend on s9** (a transcript-based estimate; B1 and B2 will move meeting counts):

- About +1 call per meeting: +144 on 1,694 (+8.5%).
- About +0.68M input tokens (+6.9%), sizing each rebuttal at the meeting's last turn prompt.
- About +52k output tokens (+12%), at 363 output tokens per turn.
- About +12 minutes of wall time on 2h25m.
- The largest per-game input rises from 327,360 to about 347,663, far below the 1.75M cap.

**Census cells for the assessment.** All are process counts, keyed by (set, meeting):

1. rebuttal turns per meeting, which must equal the selector's pick on the pre-rebuttal turns (0 or 1);
2. opener accused, and opener answered: the headline;
3. beneficiary kind (opener, other crew, impostor): reported only;
4. rebuttal content by structure: alibi, whereabouts, `saw_vent`, redirect accusation, or defensive
   only; and whether the redirect targets the accuser;
5. defaulted rebuttals;
6. flags and voices whose event ids cite the rebuttal turn;
7. extra calls and tokens.

Reporter ejections and role-correctness are reported cells only. The Phase-21 share-versus-count
decision stays separate.

## 4. B4: the kill-tick leak

**Where it is.**

- The engine mints `body-{victim}-{tick}` (`engine/rules.py:87`).
- `BodyState` carries no kill tick field (`engine/entities.py:43-49`), so the id is the only carrier.
- `_build_meeting_trigger` passes the raw id when `temporal_observations` is OFF, and
  `public_body_id(victim)` when it is ON (`orchestrator/game.py:3459-3470`; `observation/body_ids.py:6-11`).
- The description reaches only the opener's report prompt:
  - `crewmate_report.j2:96`;
  - `impostor_report.j2:85`;
  - emergency detection matches a phrase, not the id (`meetings/manager.py:932-943`).
- Packets already use the public handle unconditionally (`observation/service.py:425-433`).
- The limitation is documented (`docs/architecture.md:131-133`).

**Reach**, count-only over all 623 report meetings (s9 135, c9 416, s4 36, c4 36):

| channel | count |
|---|---|
| opener's report prompt carries the engine id in the trigger | **623 of 623** |
| any non-opener prompt carries the engine id | 0 |
| the opener's later prompts (its ballot) carry it | 0 |
| any spoken turn carries the engine id | 0 |
| opening `found_body` observation dated at the kill tick (not the trigger tick) | 0 |
| opening free text names "tick k", with k the kill tick and not the trigger tick | 38 (controls: tick k-1: 17; tick k+1: 25) |

**The listener side.** Listeners never receive the engine id. The only possible spill is the
opener's free text: at most 38 openings, a weak excess over the neighbour-tick controls, and not
attributable without reading text. Otherwise the kill tick is known first-hand only to the killer,
fellow impostors and kill witnesses.

So B4 removes the reporter's privileged anchor. It does **not** fix the 11 innocent ejections where
the kill time was assumed from the report time; those listeners never had the tick. Public death
bounds render only when an evidence-reasoning version is set, and none is in this wave
(`agents/memory/evidence_context.py:250-251`). B4 may
also remove the occasional correct time a reporter passed on, which is the honest cost.

**Tests that pin the OFF bytes:**

- `tests/orchestrator/test_temporal_delivery.py:372-417`:
  - OFF asserts `reported body body-p-3-4 at tick 8`;
  - temporal ON asserts `body-p-3` and no legacy handle.
- `tests/meetings/test_prompt_byte_golden.py`: every committed prompt of s9 and s4 re-renders
  byte-identically, with the trigger rebuilt with defaults (`:781`). 25 passed.
- `tests/experiments/test_held_out_prefixes.py:705-720`.

### The options

**(a) Record with `AILIBI_TEMPORAL_OBSERVATIONS=2` (existing lever, no code change).** It closes the
leak, but it is not narrow. Measured by probe:

- **Every prompt changes.** Seed 12 with an identical trajectory: 44 of 44 prompts differ. The
  baseline-9 comparison is lost for every call type.
- **Tactical trajectories change.** Paired fake-provider seeds 0-7: seed 0 diverges from tick 14, and
  seed 6 from tick 22 with one fewer tick. Delivered observations update beliefs
  (`orchestrator/observation_delivery.py:44-68`).
- **Same-tick vents and kills reach the meeting** (`tests/orchestrator/test_temporal_delivery.py:122-190`).
  That is exactly the vent-proof channel B1 and R7 measure, and R8's kill rows.
- **Version trap.** `=1` or `true` selects v1 (`observation/version.py:27-28`), which has the NG3-4
  contradictory-ledger defect. `--expect-levers temporal_observations` cannot tell v1 from v2.
- **Unrecorded pairing.** Temporal v2 without evidence v2 has never been recorded live, and it is not
  the evidence-v2 adopting record the retire card waits for.
- **Extra refusals beyond the experiment stamp:**
  - the golden (`require_legacy_observations`, `test_prompt_byte_golden.py:656`), where extending it
    means implementing temporal delivery in the reconstruction;
  - the ML surrogate table (`test_temporal_delivery.py:505`).
- **Scope.** It respects the no-new-levers stop literally (`tasks/direction-2026-09-19-process-over-outcome.md:318`),
  but it is not the minimal change.

**(b) A narrow arm (recommended).** One field substitutes `public_body_id(victim)` into the trigger
text and nothing else.

- **Home.** `RecordedExperimentConfig`, read by `HeadlessGame` and passed to `_build_meeting_trigger`
  next to `temporal_observations` (call site `orchestrator/game.py:2681-2683`).
  - Set it through the same recorder path B1 and B2 need for `meeting_reset` and `vent_exit_policy`.
    Today `scripts/run_tournament.py` has no experiment-config input.
  - If the orchestrator keeps everything env-driven, use a `MeetingEvidenceProfile` entry instead
    (`meetings/evidence_profile.py:25-32`, which `check_doc_facts` holds `.env.example` to), merged
    into the stamp at `orchestrator/game.py:2254-2270`.
  - Do **not** add a substrate lever: the plain-shell loader refuses a toggle recorded ON
    (`api/replay_loader.py:748-783`; the Phase-21 README says so).
- **Effect.** Only report-opening prompts change: 1 per report meeting, 0 of 44 other prompts in the
  probe comparison. No simulation or perception change.
- **Bytes.** No committed byte moves. The default keeps the legacy branch, so the golden stays 25 of
  25. The key must be omitted from serialisation when OFF, so every fixture config round-trips.
- **Refusals.** It adds none beyond the experiment stamp B3 already sets.

**(c) Anything else the tree supports.** Nothing narrower exists:

- temporal versions are 1 or 2 only;
- an unconditional change breaks the golden, whose trigger is rebuilt with defaults (`:781`);
- changing the engine id moves every state hash;
- coupling the handle to an unrelated arm (rebuttal, reset or format version) would be a dishonest
  gate.

**Under B2 (full reset).**

- Corpses clear at meeting close (`engine/meeting_reset.py:41`), so every report names a body killed
  since the last meeting. Its id still embeds the kill tick, so B4 is still needed.
- Button meetings read "called an emergency meeting" and name no body under OFF, (a) and (b) alike,
  so B2's planted "button names no body" test is unaffected.
- (a) alone does not make the regroup legible. The regroup is ingested only under evidence v2
  (`agents/memory/evidence_context.py:207-208`) and rendered only under evidence v2
  (`agents/memory/store.py:703-708`).

**Relation to `tasks/work/retire-temporal-evidence-v1.md`.**

- It is not a prerequisite for either option: v2 is selectable today.
- It does not precede B4: it is blocked on an evidence-v2 adopting record, which this wave does not
  produce.
- It does not conflict with (b).
- (b) folds into it: once temporal v2 graduates, the trigger's temporal branch is unconditional and
  the narrow arm is dead code. Add "delete the narrow trigger arm" to that card's scope when B4
  lands, per craft rule 3.

### Planted tests

**B4 (b):**

1. **The leak closes.** A fake-provider game (seed 1, 7p1i) with the arm ON and temporal OFF:
   - no prompt matches `LEGACY_BODY_HANDLE_PATTERN` (`experiments/held_out_prefixes.py:168`);
   - the opening reads `reported body body-p-3 at tick 8`.
   - Removing the substitution makes the test fail.
2. **OFF bytes are unchanged.**
   - The existing OFF control (`body-p-3-4 at tick 8`) still passes.
   - The golden stays 25 of 25.
   - `verify_samples.sh` and the four `build_sample_report --check` runs stay green.
3. **Narrowness.** Arm ON versus OFF on one seed:
   - identical state hashes;
   - the only differing prompts are the report openings;
   - no `temporal_observation_version`;
   - the same-tick vent test still shows OFF delivery.
4. **Emergency descriptions** are byte-identical with the arm ON and OFF.
5. **Reconstruction threads the stamp.** Rebuilding a stamped-ON recording without the arm misses
   the opening prompt lookup.
6. **Serialisation.** Every fixture config serialises byte-identically, and the default is still
   omitted (`orchestrator/experiment_config.py:116-142`).
7. **Loading.** An arm-ON fake recording loads in a plain shell.

**B3:**

1. **An opener accused at turn 1 gets exactly one extra turn.** Use a scripted 9-player report
   meeting through the real `accusation_round` renderer. The rendered case block quotes the turn-1
   charge.
2. **An opener nobody accuses gets none.** Plus a documented case where the slot goes to an earlier
   charge against another player.
3. **Never a second rebuttal.** The rebuttal's own accusation of a speaker who has already spoken
   adds no turn. Wrapping the gate in a loop makes the test fail.
4. **The budget counts the extra call.** The `GameBudget` snapshot grows by exactly that call's usage.
5. **Replay accepts only the selected tail.** `walk_chain`, or a successor, accepts exactly one
   trailing reply only when `bounded_rebuttal_version=1` is recorded **and** it equals the selector's
   pick. A planted wrong speaker or `reply_to` raises, and a trailing reply in an OFF recording
   still raises.
6. **The extractor** accepts the selected tail under the stamp and still flags it without the stamp.
7. **The golden threads the recorded profile.** Dropping it leaves a call unconsumed.
8. **Independence.** With the rebuttal ON and `reporter_reasoning` unset:
   - no `<who_reported>` block;
   - `prompt_versions` equal the default registry;
   - `substrate_flags.reporter_reasoning` is false.
9. **Recorder preflight.** Add whole-slate equality over `EXPERIMENT_ENV_NAMES`, in the spirit of
   `--expect-levers`. A missing export is refused.
10. **Probe-seed stop.** On the recorder's honesty-probe seed, every meeting where the selector fires
    carries exactly one non-defaulted rebuttal. Otherwise, halt before spending on the remaining 49
    seeds.

## 5. The partial-record hypothesis, checked against the code

**Holds for the other three sets.**

- A missing config means the historical defaults (`orchestrator/experiment_config.py:137-142`), and
  default-OFF arms leave their bytes, loading and re-simulation untouched.
- The golden passes 25 of 25 at `e886b663`.
- The meeting-profile arms reach recordings through the environment
  (`orchestrator/game.py:1380`, `:2252-2270`) without a recorder change.

**Fails for s9 itself if the record overwrites `replays/samples/9p2i`:**

- **Eight instruments refuse.** Any non-default stamp is refused by eight walk profiles
  (`eval/replay_walk.py:503-515`); probe-confirmed on a rebuttal-ON and a temporal-v2 recording:
  - `eval/evidence_honesty.py:2605`;
  - `eval/validity.py:508`;
  - `eval/solvability.py:698`;
  - `eval/funnel.py:254`;
  - `eval/kill_craft.py:527`;
  - `eval/win_condition_selfcheck.py:205`;
  - `eval/watchability.py:1544`;
  - `eval/balance_eval.py:914`.
  - Only `process-scorecard` (`eval/process_scorecard.py:782-788`), `current-report` and
    `leak-scan-factory` accept them.
  - The synthesis census walker itself used the `evidence-honesty` profile, so it would refuse too.
- **More consumers refuse experiment-stamped games:**
  - `require_baseline_experiments` (`orchestrator/replay.py:778-784`), used by the surrogate table
    (`training/surrogate/dataset.py:1026`) and `experiments/tactical_gameplay.py:194`;
  - the golden harness, which lacks the profile (`:447-459`) and the trigger arm (`:781`), and
    refuses temporal recordings outright (`:656`);
  - 67 test files read s9.
- **Recorder gaps:**
  - `scripts/run_tournament.py` cannot set tactical arms, which B1 and B2 need;
  - the preflight does not cover `EXPERIMENT_ENV_NAMES`.
- **Publication.** `.github/workflows/pages.yml` republishes `replays/samples` on every push to
  `main`, so an overwrite publishes unadopted behaviour (AGENTS.md, Delivery).
- **Precedent.** `replays/records/phase-21-wave2-finding/README.md` kept lever-ON evidence out of
  `replays/samples` for exactly these reasons.

## 6. Reproduction

Count-only scripts, written outside the tree in
`<session scratchpad>/stageb_rb/`.
Run them from the repo root with `PYTHONPATH=. uv run --frozen python <script> <out>`:

- `rb_census.py`: the B3 table and the B4 reach table;
- `rb_cost.py`: the spend projection and the tick-mention controls;
- `rb_roles.py`: beneficiary roles.

Probes use the fake provider, with `AILIBI_BOUNDED_REBUTTAL` and `AILIBI_TEMPORAL_OBSERVATIONS`
unset in the parent shell:

- `probe_arms.py {off|rebuttal|temporal2} <dir>`: stamps and walk-profile refusals;
- `probe_loader.py <dir>`: plain-shell loading;
- `probe_diverge.py <dir>`: fake-provider seeds 0-7, OFF versus temporal v2;
- `probe_promptdiff.py <a> <b>`: prompt-byte differences.

Tests run:

- `uv run --frozen pytest -p no:cacheprovider tests/meetings/test_reasoning_evidence.py tests/orchestrator/test_experiment_config.py`
  plus the two temporal tests: 59 passed;
- `tests/meetings/test_prompt_byte_golden.py`: 25 passed.

## 7. Not established

- How a real 27B uses the rebuttal: whether it answers, repeats itself or only redirects. No live run
  exists, and the fake provider cannot fire it.
- Whether the 38 kill-tick mentions in openings come from the leak. Settling it needs reading speech,
  which this brief excludes.
- The actual extra spend once B1 and B2 change meeting counts. The +8.5% calls figure assumes today's
  transcripts.
- Whether B2 needs evidence v2 for the regroup. That belongs to the B2 investigator, and it decides
  the exception in section 0, item 3.
