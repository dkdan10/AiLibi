# Stage B decision memo

Synthesis of the Stage-B investigation, 2026-09-24. Read-only on `main` at `e886b663` (baseline 9, fully green).
Inputs: the seven investigator memos in this directory (`partial_record`, `vent_witness_and_exit`,
`vent_movement_options`, `meeting_reset_full`, `rebuttal_and_body_handle`, `ballot_kill_row_and_impostor_strategy`,
`census_and_record`), `orchestrator-vent-ruling.md`, the refuters' verdicts, and Part 1 plus the Part 2 and Part 3
sections of `../analysis-2026-09-24/analysis-memo.md`. No model call, no recorder run, no held-out band, no prompt
printed, no tracked file edited. Every re-check below is count-only, keyed by (set, meeting). Citations are
`path:line` at `e886b663`.

Set names: `s9` = `replays/samples/9p2i`, `c9` = `replays/ml_corpus/9p2i`, `s4` = `replays/samples/4p1i`,
`c4` = `replays/ml_corpus/4p1i`.

**The bottom line.**

- Build every Stage-B switch as a default-OFF `RecordedExperimentConfig` field. Add no `AILIBI_*` lever and no new
  env switch.
- Record `s9` seeds 0-49 at the 9p2i roster with every arm ON, into a new in-tree candidate directory,
  `replays/candidates/stage-b-r1/9p2i/`. Do not write it into `replays/samples/9p2i`.
  - The other three sets and `s9` keep their baseline-9 bytes.
  - Nothing publishes.
  - The ladder tip stays at baseline 9.
  - The candidate is verified in CI like a sample set.
- Adoption is a later owner decision. It happens only after the owner assesses the pre-registered cells.
- Eleven cards: A3, A1, a spine, a readers card (which absorbs B3), a record-plumbing card, B0, B1, B2, B4, B6 and
  B5. The critical path is A3 -> spine -> readers -> B2 -> B6 -> B5.

---

## 0. Rulings

### 0.1 The owner's rulings of 2026-09-24, verbatim

1. "We should implement stage B"
2. "B1. Add vent logic so that imposters try to avoid being caught coming out of a vent."
3. "B2. full reset."
4. "B3. Allow one reply for the opener"
5. "B4. close the tick kill leak"
6. to 10. and 13. "What do you think is best?" (delegated to the orchestrator)
11. "Tour fix can be deferred to after gameplay is finished"
12. "Hold off on ML as D suggests until gameplay is finished."

On the record: "Let's not re-record all 300 seeds each time. When it's time to record, record the smaller group of
50 seeds, assess if the implementations have been effective and resulted in desired results. Also it is understood
that updating the vent and body reset logic will probably have a substantial effect on previous limits and
statistics around the baseline voting results, that is okay."

### 0.2 The orchestrator's rulings, and whether anyone argued against them

| ruling | argued against? | resolution |
|---|---|---|
| **R6.** Impostor self-report stays OFF this wave. Revisit after the 50-seed assessment. | No. The reset investigator confirms consistency: the reset adds no impostor callers. | Stands. The census reports impostor openers as a conformance cell (0 while `self_report` is False and `contextual_self_report_version` is None). |
| **R7.** The vent witness rule becomes PHYSICAL, as a new engine arm. | No. The movement investigator notes that hidden travel would make R7 moot. The orchestrator's vent ruling chose the wait, so R7 bites. | Stands, as B0. The witness-entitlement oracle and the leak scan must take the rule. A refuter showed that the oracle hard-fails a correctly threaded physical recording (`eval/witness_entitlement.py:94-110`, called at `eval/leak_scan.py:1006`), so this is required, not optional. |
| **R8.** A witnessed kill becomes an OWN-EVIDENCE row. No public flag. | No. | Stands, as a separately adoptable field in B6. It gives no statistical power at 50 seeds (4 holder ballots on s9), so it is assessed for presence only. |
| **R9.** The direction's section-5 "4-player artifact" reading is superseded. | No. | Stands. Re-counted: 36 of 37 reporter ejections are in 9-player games (s9 7, c9 29, c4 1, s4 0). Committed commands reproduce every count the amendment cites (0.4, R9 rows). The amendment text is in section 6. |
| **R10.** Impostor ballots express STRATEGY, bounded by grounding. | Partly. The B6 investigator accepts it but warns against reading outcome cells as proof. The refuter showed the proposed wording ("a line that bears on them") is looser than R10's "against whom", and that the confidence floor now lets strategic EJECTs meet 0.6 alone. | Stands, with the wording tightened to "points toward them": someone accused them at this table, or a conflict names them. No confidence clause. Two new cells: EJECTs citing only a neutral row, and ejections whose floor is met only by impostor ballots (baseline 0 of 411). **Enforcement is by instruction, not by the tally.** Under ruling D6 the tally reads no grounding label (`meetings/voting.py:238-250`), so "SKIPs otherwise" is instructed and counted, never enforced: an ungrounded impostor EJECT is recorded and tallied like any other, and the R10 compliance cell counts it. |
| **R13.** The gameplay census is a separate report. No scorecard cell. No D1 amendment. | No. | Stands. Candidate columns live in the record's audit, computed by `--set-dir` modes that write nothing. |
| **B3 rider.** `bounded_rebuttal_version=1` alone; `reporter_reasoning` does not ride along. | No, but v1 is wider than ruling 4's words. | Stands, with a stated **deviation from the literal ruling 4** ("one reply for the opener"). v1 is not opener-only: it gives the one turn to the target of the earliest unanswered new charge, whatever that player's seat or role (`meetings/rebuttal.py:17-55`). Projected on the s9 transcripts it fires 144 times: 123 to the opener and **21 to non-openers, 19 of them impostors** (2 other crewmates). Pooled, the opener loses the slot in 13 of the 561 meetings where it was accused (s9: 2 of 125). The owner either confirms v1, as ruled here, or asks before B5 for an opener-only value under a new version (section 5 item 4). Two known wording limits of the reused reply body become a stated limitation and a census cell, not a template change. |
| **B4 rider.** B4 is the minimal change that closes the leak. | No. The temporal lever (option a) was rejected by the investigator on confound grounds. | Stands, as the narrow `report_body_handle_version` field. |
| **Vent ruling (`orchestrator-vent-ruling.md`).** B1 is the policy-only look-first wait-in-place exit, paired with R7. | The wait-branch objection targeted the superseded `look_first` design. The ruled design waits whenever its own room or a visible neighbour holds a non-teammate, so it is live under the physical rule. | Stands, with one amendment (0.3 item 3). |
| **The partial-record principle** (re-record `replays/samples/9p2i` in place). | Yes: all seven investigators and all refuters. | **Departure, ruled here** (0.3 item 1). The owner may overrule it (section 5). |

### 0.3 Decisions this memo makes (the orchestrator acts on them; each is defended in section 2)

1. **Landing.** The 50 seeds go to `replays/candidates/stage-b-r1/9p2i/`: in-tree, class (a) plus (b), under one
   `replays/candidates/` family row. Not `replays/samples/9p2i`, and not an orphan evidence commit.
2. **Serializer.** Each new field is omitted from the payload while it holds its default: a stated new pattern
   beside `_preserve_version_one_bytes` (`orchestrator/experiment_config.py:97-107`). `format_version` stays 1.
   - No format 4. Format 4 would need a ladder rewrite of `:65-94`, whose checks test `== 3` and `!= 3`, and of
     `api/replay_loader.py:1455`.
   - After adoption, recordings must write adopted values explicitly, so a missing key keeps meaning the
     historical default.
3. **B1 splits into two fields.**
   - `vent_exit_policy = "look_and_wait"`: a new value of the existing field.
   - `vent_entry_policy = "own_fresh_kill"`: a new field (default `"any_body"`).
   - Reason: craft rule 5 (a stamp names its mechanism), and so the lab can attribute exposure changes to exits
     rather than to fewer trips.
4. **R8 and R10 are two fields.** `ballot_kill_row_version` and `impostor_ballot_version`, each `Literal[1] | None`,
   so they can be adopted separately.
   - Stamps follow the in-tree arm convention: `_lever_arm_versions` appends the registry key
     (`orchestrator/game.py:482-497`), and a composite joins stamps with `+` (`:735`). The suffix is derived from the
     field name, never chosen: drop `_version` and append `_v<value>`. So the stamps are
     `vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1` and `vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1`. The spine
     owns the one derivation function and a test that fails on a hand-written suffix.
   - v9 stays unallocated until an adopting decision.
5. **Config-only switches.** The new meeting-profile fields (the two ballot arms) have no env var. They are set only
   by the declared config file. The recorder refuses every ambient `EXPERIMENT_ENV_NAMES` export
   (`meetings/evidence_profile.py:25-32`), including the existing `AILIBI_BOUNDED_REBUTTAL`, and serves the config
   instead.
6. **Versioned values.** Once round 1 is recorded, an arm value's meaning is frozen. A later change adds a new value
   (for example `look_and_wait_2`) and never redefines a recorded one. This applies to `hub_with_grace` too.
7. **B3 folds into the readers card.** B3 has no behaviour code (`meetings/rebuttal.py:17-55` and
   `meetings/manager.py:1508-1539` already exist). Its follow-through is reader work on files that card already
   owns.
8. **B2's fixes 3 and 5 are signed off.** Fix 3 is the regroup notice on the default evidence path (2.3 item 3);
   fix 5 is the regroup relevance window (2.3 item 4), which also keeps regroup sightings out of the ballot's own
   rows.
   - Both are new prompt bytes and a detector change beyond the literal words "full reset". They are signed off
     here as material decisions and must be recorded as such in the B2 card.
   - Why: without them, the recorded reset writes false perceptions and unexplained teleports into every
     post-meeting prompt, which is a defect, not an experiment.
   - Both are gated on the recorded arm and byte-neutral on `preserve`.
9. **A pending-arm guard.** The spine declares every wave field at once. Each ON value is refused (loudly, at
   config validation) while its name sits in `WAVE_ARMS_PENDING`. Each arm card deletes its own entry. B6, the
   last arm card in merge order, empties the set and then deletes the guard and its refusal test (craft rule 3: a
   dead mechanism is deleted). The record card's preflight asserts the guard is gone and the declared config
   validates.
10. **Instrument disposition.** The event-level walks are widened: validity, kill-craft, kill-gift, funnel,
    solvability, win-condition, evidence honesty and the census. The policy-rerunning and frozen instruments keep
    refusing: off-menu, anchor study, surrogate and conviction tables, and the frozen watchability referee
    (ML held, ruling 12).

### 0.4 Facts re-checked (count-only, scripts in `.../scratchpad/synth_b/`)

| disputed fact | result |
|---|---|
| Does B2 zero "meeting opens with an impostor in a vent"? | **No.** 101 meetings, 105 impostor slots; 102 of the 105 entered after the previous meeting (s9: 28 of 29). The reset runs at close (`orchestrator/game.py:1923`). The vent refuter is right. B2 zeroes "in a vent when play resumes" (s9 10/107), not the opening. |
| Is there no post-meeting button cooldown? | **There is one.** `EMERGENCY_COOLDOWN_TICKS = 6` (`agents/tactical/crewmate_policy.py:109`), plus a fresh crossing (`:158-167`). The reset refuter is right. |
| Does `alibi_vs_sighting` use the relevance gate? | **No.** `_detect_alibi_vs_sightings` (`meetings/transcript.py:3175`) never calls `is_relevant_sighting`, which is used only at `:1425`, `:2132`, `:2368` and `:3763`. Fix 5 must be symmetric. |
| Does the co-presence fold happen only at tick 0? | **Yes** (`agents/memory/store.py:2170`, `rows[0].tick == 0`). |
| Does the witness oracle hard-code two rooms? | **Yes** (`eval/witness_entitlement.py:94-110`), via `eval/leak_scan.py:1006`. |
| Does the four-set doc-fact agreement hold? | **Yes** (`scripts/check_doc_facts.py:299-304`, `:2146`). A candidate outside `_RECORDED_SETS` does not touch it. |
| The pytest hazard during a leg | **Real.** `tests/scripts/test_refresh_samples.py:1181-1219` inventories `replays/` and deletes new paths. Seeds stage in `dirname(SAMPLE_DIR)` (`scripts/refresh_samples.sh:736`). |
| Is `refresh_samples.sh` FROZEN? | **Yes**, header at `:3-5`. Card changes need the declared departure; task 20.33 (`fc5cf719`) is the precedent. |
| B3 prompt size | On s9 (141 meetings without retries): a speech call averages 4,092 input tokens, the last speech call 4,714, and a ballot 7,530. The refuter's 7,710 is each meeting's final call, which is a ballot. A rebuttal is a speech call (about 4.7k), so the investigator's +0.68M holds. The headroom concern stands for ballots. |
| Calls carrying the kill-tick body id | **632**, not 642 (s9 138, c9 422, s4 36, c4 36). 623 of 623 report openings carry it. |
| R9 counts | Reporter ejections: s9 7, c9 29, c4 1, s4 0. 36 of 37 are in 9-player games. 42 innocent ejections in all. |
| R9 counts, committed reproduction | `uv run python scripts/measure_baseline.py replays/<set> --funnel`, run once per set, prints `reporter ejected N/M (K innocent)`: s9 7 (7 innocent), c9 29 (29), c4 1 (1), s4 0 (0). That is 37 innocent reporters, 36 of them in 9p2i. `uv run python scripts/publish_process_scorecard.py --check` recomputes `docs/process-scorecard.md` from the recordings and fails on drift; its 9p2i pool line (`:94`) reads reporter slots 36/551 ejected against innocent non-reporter slots 4/1769, with per-set lines at `:131`, `:166`, `:201` and `:236`. Baseline 8's 34 reporters among 46 innocent ejections is `audits/audit-phase-21-close.md:407`. All run and read at `e886b663` on 2026-09-24. |
| The opener's single turn | Enforced by the manager, not only measured. The opener enters `spoken` first (`meetings/manager.py:1378`); the chain stops on an already-spoken target (`meetings/transcript.py:462-463`); opt-in eligibility (`meetings/manager.py:2706`, called at `:1437`) and the roll call (`:1480`) exclude anyone who has spoken. Only the rebuttal (`:1508-1539`) can give the opener a second turn. The counts (the first reply accuses the opener in 521 of 676 meetings; 0 of 676 second turns) have no committed instrument yet. A1 reproduces them. |
| Entry gate under the ruled definition | Own victim in that room, killed at most 3 ticks earlier, no meeting between: it removes **103 of 587** pooled entries (s9 **13 of 105**), not the ruling's 62. The card's census cell fixes the definition. |
| Ballot floor | An ejection needs a ballot at >= 0.6 for the target (`meetings/voting.py:225-236`), so strategic impostor EJECTs can meet it alone. |
| B3 beneficiaries under v1 | s9: 144 fires = 123 to the opener + 19 to impostors + 2 to other crewmates. Pooled: 673 = 548 + 113 + 12. The opener is accused in 561 pooled meetings and loses the slot in 13 (s9 2 of 125, c9 11 of 362). |
| Round-1 wall arithmetic | 145 is baseline 9's s9 meeting count (`audits/audit-2026-09-22-process-rerecord.md:628`, `:824`); the 151 quoted in the Stage-B brief is baseline 8's (`:824`). 8,695 s over 145 meetings is 60 s each. Planning wall scales with calls: 196 x 60 s x (12.68 / 11.68) x 1.1 = 14,043 s = 3.9 h, not 3.6 h. |
| Post-regroup kill window | The regroup sets each living impostor's cooldown to 4 (`engine/meeting_reset.py:36-40`, `engine/maps/canonical_1.yaml:34`), and the close does not decrement it (`orchestrator/game.py:1923-1939`). A kill needs cooldown 0 at validation (`engine/rules.py:82`); the decrement runs after each play tick's actions (`engine/tick.py:629`, `:665`). After a meeting at tick T, kills are illegal at T+1 to T+4 and first legal at T+5. |
| Off-menu under B2 | `eval/off_menu.py` is FROZEN (`:1-2`) and refuses every experiment recording (`:359-361`). B2 edits there would be dead code, so B2 drops them. |
| Regroup sightings in the ballot's own rows | Each `sighting_records` entry becomes a class-0 `own_sighting` row (`meetings/manager.py:3500-3520`), and the budget of 8 rows per subject drops the earliest rows of a class (`:3407`). Regroup co-presence rows could push an early `own_vent` row out of the block. |
| The candidate's policy-side visibility | The in-vent agent receives no visible-room list; the ruled policy infers own room plus neighbours, and own room only under any active sabotage (`vent_witness_and_exit.md` section 1.3). A census predicate read from engine-truth visibility would call a correct surfacing during a reactor sabotage a breach. |

---

## 1. The partial-record mechanism (settled)

**What the working hypothesis gets right.**

- `RecordedExperimentConfig` (`orchestrator/experiment_config.py:29-47`) is stamped on every tick row and on the
  footer, and checked for agreement (`:145-165`). A missing config means the historical defaults (`:137-142`).
- The loader re-simulates from the recorded row, not from the shell (`api/replay_loader.py:1454-1458`, `:1633`,
  `:1810-1816`). So a bare-shell `verify_samples` passes on an arms-ON set.
- Default-OFF arms leave every committed byte, and c9's ML derivation, untouched.

**Where it fails.**

1. **The recorder** cannot set an engine or tactical arm. `scripts/run_tournament.py` has no experiment flag, and
   `eval/balance_eval.py:386-400` builds `HeadlessGame` without a config.
2. **Eight walk profiles refuse** any experiment-stamped recording (`eval/replay_walk.py:503-515`). That includes
   kill-craft, which `refresh_samples.sh:1037` runs through `build_sample_report`. The recorder therefore exits
   non-zero in **any** target directory.
3. **Witness sets live only in events**, not in state (`engine/rules.py:146-156`). A reader that forgets R7 passes
   every hash check. The prototype measured this: 221 of 221 hashes equal, 4 of 28 exits different.
4. **An in-place `s9` write fails further gates**:
   - the four-set provenance agreement (`scripts/check_doc_facts.py:2146`, once the ballot stamp moves);
   - scorecard pooling under "one era" (`scripts/publish_process_scorecard.py:252`);
   - the public-results curated cases, which drop silently on a sha mismatch (`api/public_results.py:35-41`);
   - the featured labels and the e2e guard (`frontend/src/components/ReplayPicker.tsx:109-150`,
     `frontend/e2e/journey.spec.ts:475-483`), which is the tour the owner deferred;
   - the watchability floors;
   - about 72 s9-coupled test files;
   - and `pages.yml` would publish the result on merge.

**The settled mechanism.**

- **Arms.** Each Stage-B switch is a `RecordedExperimentConfig` field, declared once by the spine. The wave config is
  one JSON file, `replays/candidates/stage-b-r1/experiment-config.json`:
  `{"format_version": 1, "meeting_reset": "hub_with_grace", "vent_exit_policy": "look_and_wait", "vent_entry_policy": "own_fresh_kill", "vent_witness_rule": "physical", "bounded_rebuttal_version": 1, "report_body_handle_version": 1, "ballot_kill_row_version": 1, "impostor_ballot_version": 1}`.
  - `self_report` stays False.
  - `contextual_self_report_version` and `evidence_reasoning_version` stay None.
  - The substrate slate stays bare, so `reporter_reasoning` is OFF.
- **Levers.** None added. The five env levers stay as they are (`orchestrator/replay.py:998-1090`). Temporal
  observations stay OFF: the validity gate's bare-shell provenance check fails a temporal-ON set
  (`eval/validity.py:960-993`), and option (a) changes every prompt, confounding B1 and B2.
- **The recorder needs** (record-plumbing card):
  1. `scripts/run_tournament.py --experiment-config FILE`, validated as a `RecordedExperimentConfig`, threaded to:
     - `run_tournament_eval`;
     - `HeadlessGame(experiment_config=...)`;
     - `build_default_agent_factory(experiment_config=...)`;
     - a meeting runner built from the config's meeting profile (the spine adds that constructor);
     - the resume fingerprint.
  2. `scripts/refresh_samples.sh --experiment-config FILE`:
     - passes the file through, and echoes the parsed config in `--dry-run`;
     - refuses any ambient `EXPERIMENT_ENV_NAMES` export;
     - refuses a non-default config unless `AILIBI_SAMPLE_DIR` is explicit and lies outside
       `replays/samples/*` and `replays/ml_corpus/*`. The default target is s4 (`:35`).
     - declares the FROZEN-header departure.
- **The candidate keeps verifying.**
  - `scripts/verify_samples.sh`'s no-argument loop also walks `${AILIBI_CANDIDATES_ROOT:-replays/candidates}/*/*/`.
    The root is overridable like `AILIBI_SAMPLES_ROOT`, because `tests/scripts/test_verify_samples.py:163-191`
    asserts exactly 2 verified sets and must point the new root at an empty directory.
  - A pytest leg re-simulates every candidate directory, as `tests/scripts/test_verify_samples.py:163` does for
    samples. Every test walk of a candidate goes through `tests/_helpers/committed.py`:
    `tests/_helpers/test_committed_single_home.py` flags a walker call whose argument names `replays/`.
  - A candidate test rebuilds each candidate's report gz from its bytes and compares it with the committed file (the
    `tests/scripts/test_build_sample_report.py:88-100` pattern), so the report cannot drift.
  - The prompt-byte golden becomes callable on any directory and walks candidates with their recorded config.
  - A candidate test asserts, for each candidate: exactly its declared seeds, one `git_sha` across its MANIFEST, and
    every tick row equal to the declared config.
  - The validity gate gains `--expected-experiment-config`.
  - The census and the scorecard fold it through `--set-dir`, writing nothing.
- **The other sets keep verifying.** Their bytes never move. Every arm is default-OFF, and every arm card proves
  OFF-path byte identity with the golden on s9 and s4, `verify_samples` run once per set directory on all four
  sets (the bare run walks only `replays/samples/*`, `scripts/verify_samples.sh:38-48`), and the c9 refit pins,
  including their campaign-tier half (`uv run pytest -m campaign`; `pyproject.toml:91` excludes it by default).
- **Prompt stamps.**
  - Default registry: `vote_ballot.qwen3_6_27b.v8`; the three `.v6` stamps are unchanged.
  - The ballot arms serve `v8.<arm>` overlay stamps from the recorded config. This extends
    `prompt_versions_for_set` to experiment-bound arms; the account-arm precedent is at
    `agents/strategic/prompts/loader.py:1300-1340`.
  - No archive is needed during the wave, and the golden's bump-in-flight window stays closed. It accepts a
    registered arm stamp only when that stamp's recording carries the arm.
- **What adoption means later** (not in this wave):
  1. A decision per arm: adopt, iterate (round 2 in `replays/candidates/stage-b-r2/`), escalate (hidden travel, as
     the vent ruling names it) or fall back (status quo).
  2. For adopted arms, either:
     - (a) re-record all four sets once on the adopted config, with the ml_corpus re-freeze. The registry then flips
       `vote_ballot` to v9 with no archive, because every committed byte carries v9; or
     - (b) promote the candidate into `samples/9p2i` and keep the other three as a legacy era. That needs:
       - the v8 archive under `tests/fixtures/prompt_archive/qwen3_6_27b_v8/`, the v5 precedent retired at
         `a4bbee7f`;
       - era-keyed scorecard pooling;
       - an era-keyed `check_vote_correctness_provenance`;
       - the watchability stage block;
       - the public-results and tour minimum;
       - the s9 re-pin sweep.
     - (a) re-freezes `ml_corpus` and forces the ML refit that ruling 12 holds, and it is the 300-seed record the
       owner asked not to repeat. **(b) is the path compatible with the ML hold.**
  3. Graduation deletes each switch and keeps its recorded key (craft rule 3). A missing key keeps meaning the old
     default for as long as any committed recording reads it. `preserve`, the fifth-run archive at
     `audits/deduction-candidate/run-2026-09-16` and the v3 fixture are the current readers.
  4. `observed_risk` loses its mechanism when `look_and_wait` is adopted. Its lab rows stay
     (`audits/tactical-gameplay/README.md:151-152`).
  5. The record-plumbing card refuses a non-default config aimed at `replays/samples/*` or `replays/ml_corpus/*`.
     Promotion (b), or any in-place record, needs that refusal lifted by the adopting card.
  6. A config-field retirement procedure. `docs/agent-procedures.md:6-35` covers only `AILIBI_*` substrate levers.
     The adopting card writes the equivalent for `RecordedExperimentConfig` fields: delete the behaviour switch and
     its dead branch, keep the key as a read-only recorded field whose missing value means the historical default,
     and keep one history line.
  7. A rule for retiring superseded candidate rounds. Proposed: the card that lands round r+1, or the adopting
     card, deletes round r's directory with its verify, probe and inventory entries, and its audit cites the commit
     that held the bytes.
  8. The viewer items deferred from B2: the `MapView.tsx` snap on a reset replay's first post-meeting frame, and
     the `frontend/src/lib/bodies.ts` comment. The demo does not serve the candidate, so they wait for adoption,
     which is a publication decision.

---

## 2. Decisions per topic

### 2.1 Partial record (investigator: partial_record)

**Decision.** The investigator's architecture stands: config fields only, a recorder that takes a declared config,
readers and a validity gate that learn the arms. It is amended as follows.

**Accepted objections.**

1. `check_vote_correctness_provenance` joins the adoption list. It is untouched while the candidate sits outside
   `_RECORDED_SETS`.
2. The witness oracle and its callers (`eval/witness_entitlement.py`, `eval/leak_scan.py:1006`,
   `scripts/scan_recording_packets.py`) join B0, with a planted physical exit that fails the unthreaded oracle.
3. Landing registration is priced. It is folded into record plumbing as one family row, `replays/candidates/`, plus
   one `_IN_TREE_PROBES` entry and one `_IN_TREE_INVENTORY` entry (`scripts/verify_ml_evidence.py:2754`, `:2816`).
   A later round costs a new directory and a file-count edit in `docs/artifacts.md`.
4. Class (c) is rejected because no CI gate would read the bytes. In-tree class (a) puts them under the verify leg,
   the golden and the census on every change.
5. The pytest hazard becomes an operating rule: record in a dedicated recording worktree, and run no pytest or
   `check.sh` there while a leg is live.
6. The direction's stop on adding levers is amended once, with a dated exception listing every new field
   (section 6).
7. The departure from the in-place principle is recorded as a ruling here (0.3 item 1) and put to the owner
   (section 5).
8. The FROZEN-header departure is declared in the record-plumbing card.
9. B3 is re-priced from measured per-kind means (0.4).

**Rejected.**

- **A MANIFEST experiment-config column.**
  - It would change the committed MANIFEST format of all four sets, which `check_doc_facts` parses. That breaks the
    partial-record principle.
  - The declared config file carries a sha256 in the candidate README, and the validity gate checks every tick row
    against it. That is a stronger guard than a column.
  - The MANIFEST `policy` stays `fsm-default`. The stamp docstring (`orchestrator/replay.py:532-548`) states that
    `fsm-default` plus a recorded tactical arm means `ExperimentalImpostorPolicy`. The replay's
    `agent_factory_kind` already records it.
- **Format 4** is superseded by omit-at-default (0.3 item 2).

### 2.2 Vent: B0 physical witness, B1 look-and-wait (investigators: vent_witness_and_exit, vent_movement_options; orchestrator vent ruling)

**Decision.**

- **B0.**
  - `vent_witness_rule: Literal["both_rooms", "physical"] = "both_rooms"` (engine layer).
  - Under `physical`, an exit whose destination differs from the room left has `source_witnesses = ()` and
    `witnesses = destination_witnesses`. Entries and exits in place are already one-room.
  - It is threaded by one helper (0.3 item 9, in the spine) at every re-simulation site: `orchestrator/game.py:2566`,
    `api/replay_loader.py:1633`, `eval/replay_walk.py:636`, `experiments/tactical_gameplay.py`.
  - The rule is also taken by `observation/temporal.py:132-135` (switched to the event's own lists), both
    entitlement oracles, the leak scan and `scan_recording_packets`.
- **B1** follows the orchestrator's vent ruling verbatim, with the entry gate split into `vent_entry_policy`.
  - It is implemented only in `ExperimentalImpostorPolicy`. The default `ImpostorPolicy` is untouched, so every
    committed decision reconstruction stays identical.
  - At adoption, a missing config keeps meaning `both_rooms`. A pooled instrument must refuse or stratify sets
    recorded under different witness rules; the census era key does this.

**Accepted objections.**

- **In-vent openings.** 102 of 105 in-vent meeting slots entered after the previous meeting, so B2 does not zero the
  opening cell. The census separates C24 ("opens with an impostor in a vent", reported) from C21 ("in a vent when
  play resumes", conformance 0).
- **The prototype headline (16/29 to 6/18) is withdrawn as evidence for B1.** It mixes B0, the entry gate and the
  exit ranking, at p about 0.5.
  - The B1 card reports per mechanism.
  - The lab adds attribution arms: full wave, and full wave minus exit, minus entry, minus R7 and minus reset.
    B5's pre-spend rehearsal runs them at the frozen HEAD, since fake meetings eject nobody and these rows measure
    mechanics only.
- **Craft rule 5.** The entry gate becomes its own field.
- **Precedents.**
  - B1 reverses `tasks/phase-11.md:65-68` (and `:87`). The reversal is dated in the direction addendum.
  - `observed_risk` retires at adoption.
- **The record path is priced** (the record-plumbing card).
- **The candidate is under a verification gate:** the verify leg, the golden on candidates, and the reader-gate
  test.

**Moot.** The idle-wait and kill-tempo objections targeted `look_first`, which the ruling replaced. The ruled design:
- waits while its own room or any visible neighbour holds a non-teammate;
- forces an exit at the 4-play-tick cap, restarted at a meeting boundary (B2 clears it anyway);
- accepts the tempo cost.

**Kept from the investigator:**
- the B0 planted tests 2.1-1 to 2.1-9;
- the teammate-is-never-a-witness test and the Hypothesis never-stuck property;
- the lights refinement (under an active sabotage, treat a neighbour as unseen). The census's B1 conformance
  predicate reads the same inputs, never engine-truth visibility (section 4).

**Projection for the card to publish** (the ruling requires it):

- **Today on s9:** 85 exit trips, 62 seen, 53 seen from the exit room, 9 seen only from the room left.
- **R7 alone** removes the 9 and about 8 of 70 s9 vent convictions, by construction.
- **Pooled projection for the wait** (vent ruling): about 20 seen exits under R7, or 51 under the stricter variant,
  against 313 today.
- The card must add the s9-only projection, computed with the movement memo's projection script.
- Ruled 2026-09-24, after the cards were authored: the cap key ranks a visibly clear room before a room the
  impostor cannot see, which ranks before a watched room (the B1 card's Acceptance cap item states the full key).
  The "about 20" pooled figure above is that key's; the literal fewest-visible reading, under which an unseen room
  counts as zero watchers, gives 36 pooled. On s9 both give 7. The A3 card was also ruled to leave
  `engine/maps/canonical_1.yaml` byte-identical (its digest is provenance in nine audit records).

### 2.3 B2 full reset on `meeting_reset = "hub_with_grace"` (investigator: meeting_reset_full)

**Decision.** Record on the existing arm with no engine change: `engine/meeting_reset.py:10-41` is the full reset
the owner ruled. Sabotage surviving the reset is documented, not changed.

The card lands the investigator's five arm-gated coherence fixes, amended as below. All are byte-neutral on
`preserve`, which the golden proves.

1. **Resume perception.** One shared resume-events helper keeps only `KilledEvent` and vent events after a regroup.
   It is used at `orchestrator/game.py:2635`, `api/replay_loader.py:1958`, `eval/replay_walk.py:795`, the golden
   and evidence honesty. `eval/off_menu.py` is not edited: it is FROZEN (`:1-2`) and refuses every experiment
   recording (`:359-361`). The new parameters are keyword-only with a no-regroup default, so its calls stay as
   they are.
   - The dropped trigger-tick perceptions (398 movement and 136 task views on 9p2i) become a census cell,
     attributed to B2.
2. **Own-completion placement** across a regroup row (`agents/memory/store.py:1905-1948`).
3. **The regroup notice on the default evidence path.** Ingest for evidence None, keep v1 excluded, and fold it into
   `fold_meeting_outcome_into_memories` (`orchestrator/replay.py:1282`).
4. **A symmetric regroup relevance window.**
   - `is_relevant_sighting` excludes a regroup tick and the tick after it.
   - The same window excludes such sightings from `alibi_vs_sighting` prosecution.
   - It is threaded through every `extract_belief_evidence` caller: `api/replay_loader.py:1883`,
     `eval/evidence_honesty.py:1366`, `eval/funnel.py:1298`, `scripts/counterfactual_phase20.py:526`,
     `orchestrator/game.py:3261` (not `eval/off_menu.py:520`, per item 1).
   - It is also threaded through every `reconstruct_stated_paths` caller (`eval/funnel.py:1419`,
     `meetings/corroboration.py:648`) and through the shared fold.
   - A loader-versus-live belief equality test covers an arm recording.
   - The same window keeps regroup sightings out of the ballot's own rows. Each `sighting_records` entry becomes a
     class-0 `own_sighting` row (`meetings/manager.py:3500-3520`), and the budget of 8 rows per subject drops the
     earliest rows of a class (`:3407`), so regroup co-presence could push an early `own_vent` row out of the
     block. Planted test: an early `own_vent` row survives a regroup that adds co-presence sightings of the same
     subject, and removing the exclusion fails it.
5. **Instruments.**
   - The scorecard room table is taken from `MeetingApplied.state` (`eval/process_scorecard.py:821-830`).
   - Evidence honesty: `room_at` and the clock alignment.
   - The golden and `tests/_helpers/committed.py` thread the arm.

**Accepted objections.**

- **The button cooldown is real.** Drop the standing-on-the-button argument. Add a cell: kill-witness button calls
  within 6 ticks of a regroup.
- **The window is symmetric**, with a planted test: an envelope alibi spanning a regroup mints no strong flag.
- **The co-presence fold extends** to public regroup ticks under the arm (`agents/memory/store.py:2146-2205`), with a
  planted line count. The refuter's probe measured 421 visible-player rows under preserve against 3,009 under the
  regroup, on s9.
- **The resume filter's information loss is priced** (the cell above).
- **Full caller threading**, with the equality test.
- **Separate landing** (section 1).
- **R10 interaction.** The tightened R10 wording (only accusations or conflicts point toward a player) keeps
  regroup co-presence rows from counting as grounding. The R10 compliance cell counts any EJECT whose only citation
  is a neutral sighting.
- **The self-location trail** shows a regroup step, not a bare arrow. The two freeze docstrings are corrected
  (`agents/memory/store.py:540-543`, `:1521-1524`).
- **Fixes 3 and 5 are material decisions**, signed off here.
- **Stamp semantics.** `hub_with_grace` keeps its name, because no committed replay stamps it. The lab README gains
  a dated note that its reset row measured the arm before this card. After round 1 the value is frozen
  (0.3 item 6).

**Optional guards, taken.** The config validator refuses evidence v1 with the reset (FU-ALIBI-2) and
`post_meeting_retarget` with the reset (inert). The spine lands both, because the spine owns the validator.

### 2.4 B3 one reply, B4 the leak (investigator: rebuttal_and_body_handle)

**Decision on B3.** Record `bounded_rebuttal_version=1` alone. No template change. The follow-through moves into
`stage-b-readers`:

- `walk_chain` (`meetings/transcript.py:563-567`) accepts exactly one trailing reply, and only when the recorded
  version is 1 and the reply equals `select_bounded_rebuttal`'s pick.
- The rubric extractor refuses experiment-stamped sets with a named error. Its rebuttal acceptance moves to
  adoption, since the rubric step runs only for `replays/samples/9p2i` (`scripts/refresh_samples.sh:1049`).
- The golden threads the recorded evidence profile.
- A scripted-client `HeadlessGame` rehearsal records a real rebuttal turn. It passes through the plain loader, the
  walks, the census and the viewer data layer.

**Accepted objections.**

- Kill-craft refuses in any directory, so it is widened.
- The landing is concrete (section 1).
- The headline cell is tautological (548 of 561 by construction). The pre-registered cells in section 4 read
  **structured answers to the charge**.
- The reused reply body says "just accused you" and "the chain follows whoever you accuse"
  (`agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:129`, `:254`, `:275`, `:291`). This is a stated
  limitation of ruling v1-alone, plus a census cell: rebuttal accusations against players who have already spoken.
- The confound is acknowledged. B3 also gives accused impostors the last word: 21 of the 144 projected s9 replies
  go to non-openers, 19 of them impostors (0.2, B3 rider). Beneficiary kind and the accuser's role are reported
  cells, and the deviation from ruling 4's words goes to the owner (section 5 item 4).
- Scripted pre-spend exercise, as above.
- One dated amendment carries every new field.

**Decision on B4.**

- A narrow field, `report_body_handle_version: Literal[1] | None = None` (orchestrator layer).
- Under the arm, `_build_meeting_trigger` (`orchestrator/game.py:3459-3470`) substitutes `public_body_id(victim)`.
  Nothing else changes.
- It needs no stamp, because no template body changes; the recorded config carries the provenance.

**Accepted objections.**

- **Retirement keeps the stamp key.** `RecordedExperimentConfig` is `extra="forbid"`, so deleting the field would
  orphan the candidate. At graduation the key stays as a read-only recorded field. The B4 card writes that rule into
  the scope of `tasks/work/retire-temporal-evidence-v1.md`.
- **The view mirror** (`api/schemas.py:1430-1447`, generated types, a `PublicResults.tsx` label) lands in the spine
  for every new field.

**Moot.** The section-0 exception ("fold B4 into evidence v2") does not fire: the reset investigator showed that
evidence v2 is not needed for the regroup.

### 2.5 B6 ballot: R8 kill row, R10 strategic impostor ballot (investigator: ballot_kill_row_and_impostor_strategy)

**Decision.** The investigator's design, with these amendments.

1. **Two fields**, each with its own stamp (0.3 item 4). v9 stays unallocated.
2. **The kill row.**
   - `KillWitnessRecord` moves to `meetings/schemas.py`, gains an `observation_id`, and keeps a re-export from
     `orchestrator.game`.
   - An optional `KillWitnessAgent` protocol; `MeetingParticipant.kill_witness_records`.
   - One class-0 `own_kill` row per first-hand record, built only under `ballot_kill_row_version`.
   - The assembly drops a teammate again, even though the accessor already does.
   - The crew suspicion-header sentence changes under the arm (`vote_ballot.j2:271`). No public flag, no ledger.
3. **The impostor ballot.** `voter_role` is threaded to the vote renderer, so a sole impostor is covered. Under
   `impostor_ballot_version`:
   - the impostor persona sentence replaces the belief framing (`vote_ballot.j2:150`);
   - the team block renders for every impostor, with the honest-citation paragraph. It is tightened to: "Name a
     crewmate only when you can cite a line you hold that points toward them: a turn in which someone accused them
     at this table, or a conflict that names them."
   - No confidence clause.
4. **Cells.** Impostor EJECTs whose only cited row is a neutral own sighting or transit (R10 compliance).
   Ejections whose 0.6 floor is met only by impostor ballots (baseline 0 of 411).
5. **Refusals.** Refused with account mode and the four legacy overlays, following the `:1389-1403` precedent.
6. **Config-only.** No env var, so `EXPERIMENT_ENV_NAMES` and `.env.example` are unchanged.
   - If a registry check requires every profile field to have an env name, the card adds an explicit config-only
     allow-list with a planted case.
   - `tests/training/test_conviction_serving.py:378-380` and `:409-411` are updated for `observation_id`.
7. **Process cells** come from evidence honesty, which the readers card widens:
   - the cited row kind;
   - the R10 compliance cell;
   - kill-row presence;
   - `check_no_betrayal = 0`.

**Accepted objections.**
- the stamp shape;
- the gate list;
- the cells need widened instruments;
- the wording;
- the confidence floor, as a cell rather than a clause;
- the cascade, where applicable;
- the serializer description;
- governance (two fields, one amendment);
- publication, which is moot under candidate landing.

**Moot.** The OFF-leg shrink objection: samples stays at baseline-9 bytes, so the five kill-holder sample meetings
remain. They are s9 seeds 17 m3, 19 m3, 26 m0 and 26 m1, and s4 seed 22 m0.

### 2.6 Census, record, documentation (investigator: census_and_record)

**Decision.** A1 as designed (`eval/gameplay_census.py` plus `scripts/publish_gameplay_census.py`), with the
refuter's amendments:

- era-keyed pooling, taking the prompt stamp only from MANIFEST rows that record a meeting;
- a mixed-era refusal inside one set;
- C33 split: recorded teammate targets are conformance (0 by the guard); authored teammate targets are behavioural
  (s9 1, pooled 13);
- 809 moves thrown away, not 808;
- 632 calls carrying the id.

Added cells (all structural, computed by the census walk):

| mechanism | cells |
|---|---|
| B1 | forced (cap) exits; ticks inside per trip; in-place surfacings where a crewmate enters or shares the corpse room before the impostor walks out; kills within 2 ticks of a surfacing |
| B2 | trips closed by a regroup; kill-witness button calls within 6 ticks of a regroup; dropped trigger-tick move and task events; sabotage active at a regroup |
| B3 | rebuttal claim structure (alibi, whereabouts, sighting, redirect-only); rebuttal accusations against already-spoken players; beneficiary kind, with the accuser's role |
| R10 | ejections carried only by impostor ballots |

**B5** is the operator record card (section 4).

- It keeps the evidence-honesty probe as the first-seed STOP, widened by the readers card.
- It runs the golden, the validity gate with the expected config, `verify_samples`, `scan_recording_packets`, the
  census conformance cells and the scorecard `--set-dir` on the probe and on the full leg.
- It records effective-means readings with the before column before the first seed.

**A3.**

- Documentation truth, plus the typed `MeetingTrigger.kind`: required, with no default
  (`meetings/manager.py:907-943`; construction at `orchestrator/game.py:3477` and
  `eval/reasoning_evidence.py:284`; about 35 test sites).
- The templates keep their substring; a lockstep pin ties them together.
- A3 lands **first**, because it shares `_build_meeting_trigger` with B4 and touches `tests/_helpers/committed.py`.

**Rejected.** The census memo's option-B wording ("widen only the validity gate"). The failure table shows eight
walks refuse, and kill-craft crashes the recorder's own post-step.

---

## 3. The card set

### 3.1 Cards, dependencies, dispatch and merge order

| # | slug | title | wave | starts after | merges |
|---|---|---|---|---|---|
| 1 | `docs-truth-typed-trigger` | A3: documentation truth and a typed meeting trigger | 0 | now | first |
| 2 | `gameplay-census` | A1: the gameplay census report | 0 | now (parallel) | after the spine, before any arm card |
| 3 | `stage-b-arm-spine` | Declare the Stage-B arms and thread them through one helper | 1 | A3 merged | 2nd |
| 4 | `stage-b-readers` | Instruments and reconstructors read the recorded arms, including the one-reply follow-through (B3) | 2 | spine merged | before plumbing |
| 5 | `stage-b-record-plumbing` | Recorder, validity gate and candidate landing for experiment-config records | 2 | spine merged (parallel) | after readers and A1 |
| 6 | `vent-witness-physical` | B0: the physical vent witness rule (R7) | 2 | spine merged (parallel) | in wave 2, after A1 |
| 7 | `vent-look-and-wait` | B1: impostors look before leaving a vent and vent only after their own fresh kill | 3 | B0 merged | before B2 |
| 8 | `report-body-handle` | B4: close the kill-tick leak with the public body handle | 3 | readers merged (parallel) | before B2 |
| 9 | `meeting-reset-coherence` | B2: the full meeting reset, coherent for agents and instruments | 3 | readers merged (parallel) | after B1 and B4 |
| 10 | `ballot-kill-row-and-impostor-strategy` | B6: the witnessed-kill ballot row (R8) and the strategic impostor ballot (R10) | 4 | B2 merged | before B5 |
| 11 | `stage-b-record-r1` | B5: record s9 seeds 0-49 as candidate round 1 and assess it | 5 | all merged; B6 has deleted the emptied pending guard | last (owner) |

**Parallel worktrees.**

| wave | cards | condition |
|---|---|---|
| 0 | A3 and A1 | |
| 2 | readers, plumbing, B0 | |
| 3 | B1, B4, B2 | under the region rules in 3.2 |

**Serial.**
- A3 -> spine -> readers -> B2 -> B6 -> B5 (the critical path).
- B0 -> B1.

**Merges.** Every merge is the owner's.

### 3.2 One writer per file: shared files and their resolution

Files a single card owns are listed in its brief (3.4). Every file touched by more than one card:

| file | cards, in order | resolution |
|---|---|---|
| `orchestrator/game.py` | A3 (`_build_meeting_trigger` construction `:3477`), spine (live tick `:2566`, runner from config `:1377-1427`, agreement loop `:2253-2263`, tactical options `:4422-4433`, the `_build_meeting_trigger` keyword, an empty experiment-arm stamp registry and an `experiment_config` parameter on `prompt_versions_for_set` `:661`), B4 (`_build_meeting_trigger` body), B2 (resume events `:2635`, regroup ticks into the meeting run, `apply_meeting_result` docstring `:1820-1825`), B6 (protocol `:966-997`, `_build_participants` `:1632-1668`, accessor `:4074-4134`, re-export, its entries in the spine's arm-stamp registry) | Serial, except B4 and B2 run in wave 3 on disjoint named functions. **Region ownership**: B4 merges first and B2 rebases. |
| `orchestrator/experiment_config.py` | spine (owner), then one-line removals from `WAVE_ARMS_PENDING` by B0, B1, B4 and B6, plus B0's helper line | **Declared exception**: each later card deletes only its own pending names (and B0 adds `vent_witness_rule` to the engine-arguments helper). Merge order B0, B1, B4, B6. B6 empties the set and deletes the guard and its refusal test (0.3 item 9). |
| `meetings/manager.py` | A3 (MeetingTrigger, docstrings), B2 (`run` regroup ticks, vouch gate `:4822`, the regroup exclusion from own rows `:3500-3520`), B6 (participant, kinds, own-channel rows, assembler gate, render call) | Serial: A3, then B2, then B6. |
| `meetings/schemas.py` | A3 (docstrings `:983-991`, `:1081-1083`), then B6 (`KillWitnessRecord` moves in, with `observation_id`) | Serial. |
| `meetings/corroboration.py` | B2 (the relevance window through `reconstruct_stated_paths`, `:648`), then B6 (docstring) | Serial. |
| `tests/meetings/test_manager.py` | A3 (the `MeetingTrigger` construction sites), then B6 | Serial. |
| `meetings/transcript.py` | readers (`walk_chain`), then B2 (relevance window and alibi exclusion) | Serial. |
| `meetings/evidence_profile.py` | spine (profile fields, `profile_from_config`), then B6 (arm refusals) | Serial. |
| `agents/memory/store.py` | A3 (comment `:94`), then B2 | Serial. |
| `agents/tactical/experimental.py` | spine (option fields and Literal), then B1 (behaviour) | Serial. |
| `experiments/tactical_gameplay.py` | spine (helper call), then B1 (lab arms) | Serial. |
| `engine/tick.py` | A3 (comment `:399`), then B0 | Serial. |
| `eval/replay_walk.py` | spine (helper, thread-or-refuse), then B2 (resume helper `:795`) | Serial. |
| `api/replay_loader.py` | spine (helper `:1633`), then B2 (resume `:1958`, belief window `:1883`) | Serial. |
| `eval/evidence_honesty.py` | readers (profile, recorded-policy reconstruction), B2 (`room_at`, clock alignment, perception, belief window), B6 (process cells in `_fold_grounding`) | Serial, along the critical path. |
| `eval/funnel.py` | readers (profile), then B2 (belief window, stated paths) | Serial. |
| `tests/meetings/test_prompt_byte_golden.py` | readers (directory-callable, config threading, arm-stamp resolution), B2 (resume helper, regroup ingestion), B6 (planted OFF leg) | Serial. |
| `tests/_helpers/committed.py` | A3 (`:382-392` trigger kind), A1 (census cache), readers (helper threading), B2 (reset) | A1 rebases on A3 (disjoint regions); then serial. |
| `tests/_helpers/scripted_meeting.py` (new) | readers (rebuttal case), then B6 (ballot cases) | Serial. |
| `audits/workflows/extract_gameplay_facts.py` | readers only (refusal); B2 does not touch it | Single writer. |
| `api/schemas.py`, `frontend/src/types/api.ts`, `frontend/src/types/api.fidelity.ts`, `frontend/src/components/PublicResults.tsx`, `tests/api/test_leak.py` | spine only, for every new field | Single writer. |
| `docs/architecture.md` | A3 (`:116-120`, the game-shape facts), spine (the wave's arm section as contract), B5 (one candidate sentence) | Serial. |
| `docs/observation-contract.md` | B0, then B2 | Serial. |
| `docs/glossary.md` | A3 ("hard evidence" `:157`), spine (terms its labels introduce), B2 ("regroup") | Serial. |
| `docs/artifacts.md` and `scripts/verify_ml_evidence.py` | A1 (census row and probe), plumbing (the `replays/candidates/` family row), B5 (file count) | Plumbing edits them only after A1 has merged. |
| `audits/tactical-gameplay/README.md` | B1 (new rows, the `observed_risk` disposition), then B2 (dated reset-row note) | B1 merges first. |
| `orchestrator/replay.py` | spine (policy-stamp docstring `:532-548`), then B2 (shared resume helper, the fold at `:1282`) | Serial. |
| `tasks/direction-2026-09-19-process-over-outcome.md` | the section-6 `docs:` commit (before wave 1), then A1 (one appended sentence with the census's opener counts) | Serial. |
| `scripts/verify_samples.sh`, `tests/scripts/test_verify_samples.py` | plumbing only (the candidates root and the empty-root override in the two-set test) | Single writer. |
| `eval/gameplay_census.py`, `tests/eval/test_gameplay_census.py` | A1 only. Each arm card's end-to-end conformance test lives in that card's own test file. | Single writer. |

### 3.3 Version plan

| item | this wave | the round-1 record carries |
|---|---|---|
| `crewmate_report`, `impostor_report`, `accusation_round` | unchanged at `.qwen3_6_27b.v6`. B3 reuses the reply body; B4 changes the trigger text, not the template. | the three `.v6` stamps |
| `vote_ballot` | default registry stays `vote_ballot.qwen3_6_27b.v8`. B6 adds guarded blocks in the same `vote_ballot.j2`; its header marker stays v8 first. | `vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1` (suffixes derived from the field names, 0.3 item 4) |
| map card | unchanged | unchanged |
| substrate flags | unchanged; the bare slate (`--expect-levers ""`) | the baseline-9 flags column, identical |
| policy column | `fsm-default` (docstring rule, 2.1) | `fsm-default` |
| experiment config | declared by the spine, pending until each arm card | the JSON in section 1. Its sha256 goes in `replays/candidates/stage-b-r1/README.md`. |

**Arms.** No env var for any new field. `AILIBI_BOUNDED_REBUTTAL` stays in the registry, and the recorder refuses it
ambiently.

| field | values (default first) | layer | card |
|---|---|---|---|
| `vent_witness_rule` | `both_rooms`, `physical` | engine | B0 |
| `vent_exit_policy` | adds `look_and_wait` | tactical | B1 |
| `vent_entry_policy` | `any_body`, `own_fresh_kill` | tactical | B1 |
| `meeting_reset` | `hub_with_grace` (existing) | orchestrator | B2 |
| `bounded_rebuttal_version` | 1 (existing) | meeting | B3 |
| `report_body_handle_version` | None, 1 | orchestrator | B4 |
| `ballot_kill_row_version` | None, 1 | meeting | B6 |
| `impostor_ballot_version` | None, 1 | meeting | B6 |

### 3.4 Dispatch briefs

**Common to every card.**

- **Base and branch.** Base: `main` after the listed prerequisites merge (today `e886b663`). Branch:
  `work/<slug>`. One PR into `main`, with the template filled.
- **Providers.** Fake provider and scripted clients only. No live call, no `.env`, no held-out band, no ML training
  or refit (ruling 12). No tour or featured-list change (ruling 11). No scorecard cell (R13).
- **Default-OFF.** Every committed byte under `replays/` is unchanged. The OFF path is byte-identical, proved by:
  - the golden on s9 and s4;
  - `bash scripts/verify_samples.sh replays/<set>`, run once per set directory for all four sets (the bare run
    walks only `replays/samples/*`, `scripts/verify_samples.sh:38-48`);
  - the c9 refit pins, which are partly campaign-tier: `pyproject.toml:91` excludes `campaign` from the default
    run, so `check.sh` alone does not prove them, and the card also runs `uv run pytest -m campaign`;
  - `uv run python scripts/publish_process_scorecard.py --check` (plus the census `--check` once A1 has merged).
- **Instruments.** No instrument pushes an agent toward the correct answer. Role-correctness is reported, never
  gated.
- **Tests.** Every new invariant has a planted case that fails on the defect (craft rule 2).
- **Validation.** `bash scripts/check.sh` in a clean worktree, `uv run pytest -m campaign`, and the card's targeted
  commands.
- **Committed walks.** A test that walks a committed or candidate set goes through `tests/_helpers/committed.py`:
  `tests/_helpers/test_committed_single_home.py` flags a walker call whose argument names `replays/`.
- **Publication.** `pages.yml` republishes the viewer and the demo bundle on every push to `main`, and AGENTS.md
  treats a viewer or public-results change as a publication decision. A card that touches `frontend/` or `api/`
  (the bundle reads `api/replay_loader.py`, `scripts/build_demo_bundle.py:85`) says so under Record impact and
  proves that the committed demo bundle and every shown replay render identically.
- **Record impact.** Default-OFF, no committed byte moves, unless the card states otherwise.
- **Direction.** The dated direction addendum (section 6) lands as a `docs:` commit before wave 1. Each B card cites
  it.

**1. `docs-truth-typed-trigger` (A3).**

Scope:
- Fix the stale text at:
  - `meetings/schemas.py:983-991`, `:1081-1083`;
  - `meetings/manager.py:4294`, `:4522`;
  - `meetings/voting.py:29`;
  - `agents/memory/beliefs.py:220-221`;
  - `agents/memory/store.py:94`;
  - `engine/maps/canonical_1.yaml:50-53` (a comment; first check that no digest pins the file);
  - `engine/tick.py:399`;
  - `observation/service.py:670-673`;
  - the glossary's "hard evidence" (`docs/glossary.md:157`);
  - `docs/architecture.md:116-120` (baseline 9);
  - `training/README.md:119-122` (a baseline-6 history label);
  - `training/rewards.py`, marking `correct_reports` and `patrol_coverage` as role-correct rewards. The edit is
    comment-only: no reward value, signature or behaviour changes, since ML is held (ruling 12).
- Add a game-shape facts note in `docs/architecture.md`: the vent tell, impostors never reporting, player-id order
  and the trigger-tick throwaway, and (until B2 is adopted) persistent corpses and paused cooldowns.
- Add the required `kind: MeetingTriggerKind` on `MeetingTrigger`. `_trigger_is_emergency` reads it. Update the
  constructions and about 35 test sites. `tests/_helpers/committed.py:382-392` derives the kind from the event.
- `DESIGN.md` is historical: cite it, do not edit it.

Acceptance:
- A planted report trigger whose description contains "called an emergency meeting" is still a report, seen through
  the reporter render id and the contradiction trigger kind. The test fails on today's code.
- A lockstep pin: for every trigger the production builder constructs, the typed kind equals the templates'
  substring test.
- The golden, `verify_samples` and the scorecard `--check` are unchanged.

Rulings relied on: "B4. close the tick kill leak" (sequencing only).

**2. `gameplay-census` (A1).**

Scope:
- New files: `eval/gameplay_census.py` (a pure fold over a hand-buildable carrier), `scripts/publish_gameplay_census.py`
  (`--check`, and a write-nothing `--set-dir DIR --json-stdout`), `docs/gameplay-census.md` and `.json`,
  `tests/eval/test_gameplay_census.py`, `tests/scripts/test_publish_gameplay_census.py`.
- Edits: `tests/_helpers/committed.py` (cache region, after rebasing on A3); `docs/artifacts.md` and
  `scripts/verify_ml_evidence.py` (the census row, its probe and its inventory).
- The walk profile is a `replace` of the current-report config (profile `gameplay-census`,
  `missing_meeting_row=violation`). It uses the spine's engine-arguments helper and its layer classification, and
  refuses any field it does not thread.
- The cells are C1-C34 from the census memo plus the 2.6 additions:
  - the body kill tick is joined from `KilledEvent`, never parsed from the id;
  - discarded actions come from the recorded dispositions;
  - pooling is era-keyed and raises across eras, including within one set;
  - each by-construction cell has a conformance guard, with its arm predicate and a planted breach;
  - the arm predicates read the carrier's plain recorded arm values and never build a `RecordedExperimentConfig`.
    A1 merges before the R7, B1, B4 and R8 arm cards, while `WAVE_ARMS_PENDING` still refuses those ON values, so
    the planted breaches are hand-built carriers and need no bypass of the guard. Each arm card then adds one
    end-to-end test in its own test file: a fake or scripted arm-ON recording reads 0 on its cell, and a perturbed
    copy raises. B5's STOP rules rely on both;
  - the B1 surfacing predicate is defined on the policy's own inputs: a `saw_player` of a non-teammate in the own
    room or an inferred-visible neighbour, where inferred-visible is own room plus neighbours, and own room only
    under any active sabotage (0.4). It never reads engine-truth visibility;
  - the post-regroup kill window is T+1 to T+4 for a meeting at tick T (0.4).

Acceptance: it reproduces 20/849, 73/587, 313/512 (251 and 62), 330/355, 13/89, 26/56, 330/346 with 326/43,
253+10+63, 50, 167/551, 335/676, 521/676, 0/676, 38/42 and 809 moves.

Planted tests:
1. An exit seen only from the room left flips when that crewmate moves.
2. A stale corpse flips to fresh.
3. A moved vent flag leaves the vent band.
4. The id tick differs from the event tick.
5. A move thrown away on a game-ending trigger tick is counted.
6. An authored teammate target.
7. A mixed-era pool raises.
8. One breach per conformance cell raises.
9. An unclassified field raises.
10. `--check` is red on one edited cell.
11. A surfacing during a reactor sabotage, with a crewmate in a neighbour that is truly visible, is not a B1 breach.
12. A kill at T+5 after a regroup is outside the grace window; a planted kill at T+4 is a breach.

Also: append one dated sentence to the 2026-09-24 addendum of `tasks/direction-2026-09-19-process-over-outcome.md`
with the census's opener counts (the first reply accuses the opener in 521 of 676 meetings; 0 of 676 opener
second turns) and the command that reproduces them (`uv run python scripts/publish_gameplay_census.py --check`).

Merges after the spine. Rulings relied on: R13 "the gameplay census stays a separate published report beside the
nine-row scorecard; no cell joins the scorecard; no D1 amendment."

**3. `stage-b-arm-spine`.**

Scope:
- `orchestrator/experiment_config.py`:
  - the eight fields and values of 3.3;
  - the omit-at-default serializer pattern;
  - `FIELD_LAYER`, plus a test that fails on an unclassified field;
  - the engine-arguments helper (today `redistribution_policy`);
  - `WAVE_ARMS_PENDING`;
  - validator refusals of evidence v1 with `hub_with_grace` and of `post_meeting_retarget` with `hub_with_grace`.
- `meetings/evidence_profile.py`: the two ballot profile fields (config-only) and `profile_from_config`.
- `orchestrator/game.py`:
  - the helper at the live tick;
  - `build_default_meeting_runner(profile=...)`;
  - the new fields in the agreement loop;
  - the pending refusal at construction;
  - `vent_entry_policy` into the tactical options;
  - the `report_body_handle_version` keyword into `_build_meeting_trigger`.
- `agents/tactical/experimental.py`: the option field and the Literal.
- The helper at `api/replay_loader.py:1633`, `eval/replay_walk.py:636` (with thread-or-refuse by layer in the walk
  configs) and `experiments/tactical_gameplay.py`.
- The view and types: `api/schemas.py:1430-1447`, the regenerated `frontend/src/types/api.ts` and
  `api.fidelity.ts`, the `PublicResults.tsx` labels, `tests/api/test_leak.py:497-500`.
- The docstring rule at `orchestrator/replay.py:532-548`.
- The arm-stamp plumbing the readers card and B6 consume: an empty experiment-arm stamp registry in
  `orchestrator/game.py`, an `experiment_config` parameter on `prompt_versions_for_set` (`:661`) that folds it, and
  the one function that derives a stamp suffix from a field name (0.3 item 4).
- The wave's arm section in `docs/architecture.md:143-165`, and glossary entries for any label term.
- Publication: the view mirror and the `PublicResults.tsx` labels republish on merge (`pages.yml`). Record impact
  says so.

Acceptance:
- Every committed experiment-config row re-serializes byte-identically: the 100 rows of
  `audits/deduction-candidate/run-2026-09-16` and the v3 fixture.
- A config with a new field at its default serializes without the key.
- A pending arm ON is refused. A planted walk config that does not thread an engine-layer field refuses a
  non-default value.
- The runner built from a config agrees with `HeadlessGame`, and a disagreeing runner raises.
- A fake game with `meeting_reset=hub_with_grace` and `bounded_rebuttal_version=1` from a declared config (no env)
  records both keys.
- Nothing refuses ON that exists today.
- With no config, `prompt_versions_for_set` returns today's mapping by identity, and a planted registry entry is
  served only for a config that carries its arm. The derived suffix of each new field matches its name.
- The demo bundle built from the committed sets (`scripts/build_demo_bundle.py`) is byte-identical before and
  after, and the `PublicResults` text of every shown group is unchanged.

Rulings relied on: "We should implement stage B"; the partial-record principle; AGENTS.md craft rule 7.

**4. `stage-b-readers` (includes B3).**

Scope:
- Flip `supports_experiments` after a per-instrument review for `eval/kill_craft.py:527`, `eval/funnel.py:254`,
  `eval/solvability.py:698` and `eval/win_condition_selfcheck.py:205`, each threading every recorded arm through
  the spine helper.
- `eval/evidence_honesty.py:2605`: profile support. Decision reconstruction uses the recorded tactical arm's policy
  (the factory at `:896-970`, `:1238-1282`), not the default.
- The golden (`tests/meetings/test_prompt_byte_golden.py`):
  - callable on any directory;
  - builds the manager from the recorded evidence profile (`:433-458`) and applies meetings with the recorded
    `meeting_reset` (`:723-730`);
  - rebuilds the trigger through the production builder with the recorded config (`:781`);
  - resolves experiment-bound arm stamps through `_overlay_stamp_owners`, from the spine's experiment-arm registry
    (empty until B6) through `prompt_versions_for_set(..., experiment_config=...)`;
  - the window test accepts a registered arm stamp only on a recording that carries the arm.
- `tests/_helpers/committed.py` threads the helper.
- `audits/workflows/extract_gameplay_facts.py` refuses experiment-stamped sets by name.
- `meetings/transcript.py` `walk_chain` accepts the selected rebuttal tail.
- `scripts/publish_process_scorecard.py --set-dir DIR --json-stdout`, writing nothing.
- A new `tests/_helpers/scripted_meeting.py`: a scripted-client `HeadlessGame` whose turn 1 accuses the opener.
- Explicit refusal tests for off-menu, the anchor study, the surrogate and conviction tables, and the watchability
  referee.

Acceptance:
- Each widened profile verifies an arms-ON fake fixture and refuses a planted unknown field.
- Honesty reconstruction on an `observed_risk` fixture has 0 mismatches with the recorded policy and more than 0
  with the default.
- The golden reproduces a scripted rebuttal meeting byte-equal, and dropping the profile fails it.
- `walk_chain`:
  - accepts the selected tail;
  - raises on a wrong speaker or `reply_to`;
  - raises on a trailing reply in an OFF recording.
- The scripted rebuttal game passes the plain loader, the walks and the viewer data layer.

Constraint: B3 has no template change.

Rulings relied on: "B3. Allow one reply for the opener"; "B3 adopts bounded_rebuttal_version=1 ALONE,
reporter_reasoning does NOT ride along"; "Hold off on ML as D suggests until gameplay is finished."

**5. `stage-b-record-plumbing`.**

Scope:
- `scripts/run_tournament.py --experiment-config FILE`, with the resume fingerprint.
- `eval/balance_eval.py`: `run_tournament_eval` passes the config to `HeadlessGame`, the factory and the runner;
  the kill-gift profile is widened (`:914`).
- `scripts/refresh_samples.sh`, per section 1, with the FROZEN departure declared under Record impact (precedent:
  task 20.33).
- `scripts/validity_gate.py` and `eval/validity.py`:
  - `--expected-experiment-config`;
  - every tick row equal to the declared config;
  - exactly the declared seeds;
  - one `git_sha`;
  - profile support after a check-by-check review.
- `scripts/verify_samples.sh`: the candidates loop over `${AILIBI_CANDIDATES_ROOT:-replays/candidates}/*/*/`.
  `tests/scripts/test_verify_samples.py:163-191` asserts exactly 2 verified sets, so it points the new root at an
  empty directory, and a new test walks a planted candidate root.
- A candidate report check: each candidate's report gz equals a rebuild from its bytes (the
  `tests/scripts/test_build_sample_report.py:88-100` pattern), walked through `tests/_helpers/committed.py`.
- `scripts/verify_ml_evidence.py` and `docs/artifacts.md`: the `replays/candidates/` family row, probe and
  inventory.
- A new `replays/candidates/README.md`: not canonical, not published, and the adoption rule.
- Tests.

Acceptance:
- Planted failures:
  - a stray `AILIBI_BOUNDED_REBUTTAL` export is refused;
  - an unknown config field is refused;
  - a non-default config aimed at `replays/samples/9p2i` or at the default target is refused;
  - a set mixing two configs fails the gate;
  - a set with one seed from another sha fails;
  - a set missing a seed fails.
- A fake seed recorded through `refresh_samples.sh` with existing arms (reset, `observed_risk`, rebuttal) into a
  scratch target:
  - stamps exactly the file's config;
  - loads in a bare shell with `outcome_verified` true;
  - passes the post-step report.
- The served set list and the demo bundle are unchanged with a candidate directory present.

Merges after readers and A1. Rulings relied on: the owner's record paragraph (verbatim, 0.1).

**6. `vent-witness-physical` (B0).**

Scope:
- `engine/rules.py` (`resolve_vent`, `:111-188`) and `engine/tick.py` (validate and thread the rule).
- The helper line and the pending line in `orchestrator/experiment_config.py`.
- `observation/temporal.py:132-135`.
- `eval/witness_entitlement.py` and `eval/temporal_entitlement.py`, which take the rule.
- `eval/leak_scan.py:1006` and `scripts/scan_recording_packets.py`, which pass the recorded rule.
- `docs/observation-contract.md`.
- Tests.

Acceptance: the investigator's planted tests 2.1-1 to 2.1-9, including:
- the exit twin of `tests/engine/test_tick.py:931-987`;
- entries equal under both rules;
- the poisoned-event oracle pair;
- the reader gate: a fake physical game loaded through `ReplayLoader` with memory and through `walk_replay` gives the
  room-left crewmate no vent observation, and bypassing the helper at one call site fails the test.

Also a planted physical exit that fails the unthreaded oracle, and one end-to-end census test in B0's own test
file: a fake physical game reads 0 on the room-left-only exit cell, and a perturbed copy raises.

Rulings relied on: R7 "a vent action is witnessed by the living non-vented occupants of the room where it
physically happens, the entry by the room entered from and the exit by the room surfaced into".

**7. `vent-look-and-wait` (B1).**

Scope:
- `agents/tactical/experimental.py`: `look_and_wait` and `own_fresh_kill`, exactly as `orchestrator-vent-ruling.md`
  specifies:
  - surface in place, or at a visibly clear connected vent by the key (no body, not the room fled from, vent id),
    only when the own room and every visible neighbour hold no non-teammate;
  - otherwise wait, up to a cap of 4 play ticks inside, restarted at a meeting boundary;
  - at the cap, surface at the connected vent with the fewest visible non-teammates, then in place;
  - never steer toward a player;
  - a teammate is never a witness;
  - under an active sabotage, a neighbour counts as unseen.
- The pending lines.
- `experiments/tactical_gameplay.py` arms, each named after the recorded value it sets: `vent_look_and_wait`,
  `vent_own_fresh_kill`, `vent_physical`, `stage_b_full`, and the four minus-one arms.
- `audits/tactical-gameplay/README.md`: the development-seed rows beside `observed_risk`, and the `observed_risk`
  retire-at-adoption note.
- Tests.
- The card publishes the s9 projection (85 trips, 62 seen, 53 from the exit room) with the ruled wait.

Acceptance, planted:
- An occupied visible exit against a blind one: the anchor exits into the occupied room; `look_and_wait` waits,
  then surfaces clear.
- An own-room non-teammate forces a wait.
- The cap forces an exit.
- A teammate is not a watcher.
- A teammate's victim, and an own victim across a meeting, cause no vent.
- A fresh own kill vents.
- Invariance to stale target sightings.
- A reactor-sabotage case: with a crewmate in a neighbour that is truly visible, the policy treats the neighbour
  as unseen and surfaces when its own room is clear, and the census predicate, defined on the policy's own inputs,
  reads no breach.
- One end-to-end census test in B1's own test file: a fake arm-ON game reads 0 on the B1 conformance cells, and a
  perturbed copy raises.
- The Hypothesis never-stuck property.
- The default policy is untouched: the I-11 pins do not move.

Record impact: default-OFF. The balance shift is accepted by the owner.

Rulings relied on: "B1. Add vent logic so that imposters try to avoid being caught coming out of a vent."; the
orchestrator vent ruling.

**8. `report-body-handle` (B4).**

Scope: `_build_meeting_trigger` in `orchestrator/game.py` (region-owned), the pending line, a new
`tests/orchestrator/test_report_body_handle.py`, and a scope note in `tasks/work/retire-temporal-evidence-v1.md`
(keep the stamp key at retirement).

Acceptance, the investigator's B4 tests 1-7:
- With the arm ON, no prompt matches `LEGACY_BODY_HANDLE_PATTERN`, and the opening reads `body-p-3 at tick 8`.
- Removing the substitution fails the test.
- The OFF control still reads `body-p-3-4`.
- Only report openings differ.
- Emergency text is identical.
- Configs round-trip.
- A plain-shell load succeeds.
- A joint test with the reset: a report after a regroup names the handle without a tick, and a button meeting names
  no body.
- One end-to-end census test in `tests/orchestrator/test_report_body_handle.py`: the opening-handle conformance cell
  reads 0 on a fake arm-ON game, and a perturbed copy raises.

Rulings relied on: "B4. close the tick kill leak"; "B4 is the minimal change that closes the leak".

**9. `meeting-reset-coherence` (B2).**

Scope: section 2.3 in full. Files:
- orchestrator: `orchestrator/game.py` (region-owned), `orchestrator/replay.py`;
- readers: `api/replay_loader.py`, `eval/replay_walk.py`, `eval/funnel.py`, `eval/evidence_honesty.py`,
  `eval/process_scorecard.py`, `scripts/counterfactual_phase20.py`. Not `eval/off_menu.py`: it is FROZEN (`:1-2`)
  and refuses experiment recordings (`:359-361`), so an edit there would be dead code or an undeclared FROZEN
  departure;
- meetings: `meetings/transcript.py`, `meetings/manager.py`, `meetings/corroboration.py`;
- agent memory: `agents/memory/evidence_context.py`, `agents/memory/store.py`;
- tests: the golden, `tests/_helpers/committed.py`;
- viewer: none. The `MapView.tsx` snap and the `bodies.ts` comment move to adoption (section 1, adoption item 8):
  the demo does not serve the candidate, and a viewer change republishes on merge;
- docs: `docs/observation-contract.md`, `docs/glossary.md` ("regroup"), `docs/cleanup-dispositions.md`
  (A-28 note), `audits/tactical-gameplay/README.md` (a dated note, after B1).

Acceptance:
- T1-T10 from the reset memo.
- A symmetric-window planted test.
- A regroup fold line count.
- The loader-versus-live belief equality test.
- A kill-witness button call within 6 ticks of a regroup is counted.
- The preserve bytes are unchanged on all four sets: s9, s4, c9 and c4.
- The grace window is pinned: after a regroup at meeting tick T, a fake game's first legal kill is at T+5, and the
  census window (T+1 to T+4) matches it.
- The own-row exclusion: an early `own_vent` row survives a regroup (2.3 item 4).
- Publication: B2 edits `api/replay_loader.py`, which the demo bundle reads, and `pages.yml` republishes on merge.
  The bundle built from the committed sets is byte-identical before and after.

Material decisions to record in Results: fixes 3 and 5 (signed off here).

Rulings relied on: "B2. full reset."

**10. `ballot-kill-row-and-impostor-strategy` (B6).**

Scope: section 2.5. Files:
- meetings: `meetings/schemas.py`, `meetings/manager.py`, `meetings/render_contract.py`,
  `meetings/evidence_profile.py`, `meetings/corroboration.py` (docstring);
- orchestrator and prompts: `orchestrator/game.py` (region-owned; its two entries in the spine's arm-stamp
  registry), `orchestrator/experiment_config.py` (its two pending names, then the emptied guard and its refusal test,
  0.3 item 9), `agents/strategic/prompts/loader.py`, `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2`;
- honesty: `eval/evidence_honesty.py` (cells);
- tests: `tests/_helpers/scripted_meeting.py` (ballot cases), `tests/meetings/test_weighing_channel.py`,
  `tests/meetings/test_manager.py`, `tests/agents/test_bespoke_prompt_sets.py`, the golden (OFF leg),
  `tests/training/test_conviction_serving.py`.

Acceptance, the investigator's planted tests 1-10 with the tightened wording, plus:
- the arm stamps are never equal to a default stamp, and they are the derived
  `vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1` and `vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1`;
- the composite stamp when both arms are ON;
- a railroad tripwire that cannot go vacuous: B6 edits the text under the suspicion header (`vote_ballot.j2:270-271`),
  and `check_no_railroaded_crew_ejections` finds rows only through that header and a row regex
  (`eval/validity.py:176-191`), passing vacuously when nothing parses. A ballot rendered with each arm ON parses to
  one row per living player, and a planted header edit fails the test;
- one end-to-end census test: the `own_kill`-naming-a-teammate cell reads 0 on a scripted arm-ON game, and a
  perturbed copy raises;
- `WAVE_ARMS_PENDING` no longer exists, and the declared round-1 config validates;
- a scripted impostor EJECT with no pointing-toward row is recorded and counted in the compliance cell;
- a scripted teammate target is coerced and `check_no_betrayal` passes.

Rulings relied on:
- R8 "a witnessed kill becomes an OWN-EVIDENCE row in the voter's weighing channel; no public certified flag";
- R10 "impostor ballots express STRATEGY bounded by grounding: an impostor may EJECT only a target against whom it
  can cite an evidence row it holds, never a teammate, and SKIPs otherwise; its decision_basis and citations stay
  honest as to the data cited; the wording never pushes toward the correct answer."

**11. `stage-b-record-r1` (B5).** Section 4.

Files:
- `replays/candidates/stage-b-r1/**`: 50 replays, MANIFEST, `roster.json`, the report gz, `README.md`,
  `experiment-config.json`;
- `docs/artifacts.md` (the file count);
- `audits/audit-<date>-stage-b-r1.md`, with its pre-registration section landed as a `coordination:` commit before
  the first seed;
- `audits/README.md`;
- `docs/architecture.md` (one sentence);
- the card.

Rulings relied on: the owner's record paragraph, verbatim.

---

## 4. The record plan

**The slate.**

| item | value |
|---|---|
| target | `AILIBI_SAMPLE_DIR=replays/candidates/stage-b-r1/9p2i` |
| roster | 9 players, 2 impostors, 2 tasks per crewmate; seeds 0-49 (the s9 seed set) |
| model | `featherless`, `Qwen/Qwen3.6-27B`, `AILIBI_PROMPT_SET=qwen3_6_27b` |
| substrate slate | `--expect-levers ""` |
| experiment config | `--experiment-config replays/candidates/stage-b-r1/experiment-config.json` (section 1); no ambient experiment export (refused) |
| operating values | 2 workers; 8 attempts per seed |
| key | `FEATHERLESS_API_KEY` in the recording shell only |

Sequence:
1. `--dry-run`.
2. `--seeds 0`, then the probe.
3. `--seeds 1..49` at the same HEAD, with no commit between.

**Pre-spend (at the frozen HEAD, $0).**

1. `WAVE_ARMS_PENDING` is gone (B6 deleted it once empty), and the declared config file validates as a
   `RecordedExperimentConfig`.
2. **A fake-provider dress rehearsal** of seeds 0-49 on the declared config, into a scratch directory **outside**
   `replays/`. The recorder refuses fake writes under `replays/` (`scripts/refresh_samples.sh:615-639`). Run on it:
   - census conformance;
   - scorecard `--set-dir`;
   - the validity gate with the expected config;
   - `verify_samples <dir>`;
   - the golden walker;
   - evidence honesty;
   - `scan_recording_packets`.
3. **The scripted-client rehearsal**, which the fake cannot provide. It proves the meeting arms fire:
   - a rebuttal;
   - an impostor EJECT with and without a pointing-toward row;
   - a kill row;
   - a teammate coercion.
4. **The lab attribution matrix** on development seeds 1000-1007.
5. **The before column and the effective-means readings** below, committed before the first seed.

**Ceilings (proposed to the owner, per round).**

Baseline-9 s9 leg: 145 meetings, 1,694 calls, 9,850,930 input, 422,941 output, 2h24m55s, $0
(`audits/audit-2026-09-22-process-rerecord.md:415`). Per meeting that is 11.68 calls, 67,937 input, 2,917 output and
60 s of wall. 145 is baseline 9's meeting count (`:628`, `:824`); the 151 quoted in the Stage-B brief is baseline
8's (`:824`).

The upper planning case. The x1.35 meetings and the +10% prompt growth are **unmeasured planning assumptions**.
The probe and the 10-seed re-projection measure both against the baseline-9 bytes of the same seeds.
- meetings x1.35 = 196, if a weaker vent tell lengthens games;
- +1 rebuttal call per meeting, at 4,714 input and 363 output;
- +10% prompt growth, from regroup lines and the ballot paragraphs.

| | planning case | ceiling (planning / 0.9) | stop at 90% |
|---|---|---|---|
| calls | 196 x 12.68 = 2,485 | **2,800** | 2,520 |
| input tokens | 196 x (67,937 x 1.10 + 4,714) = 15.57M | **17,500,000** | 15.75M |
| output tokens | 196 x (2,917 + 363) = 643k | **750,000** | 675k |
| recording wall | 196 x 60 s x (12.68 / 11.68) x 1.1 = 14,043 s = 3.9 h | **4.5 h**, inside an **8 h** window | 4.05 h |
| marginal cost | $0 (flat-rate Featherless) | **$0.00** | any non-zero `cost_usd` |

Wall scales with calls as well as meetings: the rebuttal alone adds about 12 minutes to the 2h25m leg (rebuttal
memo, section 3). An earlier draft priced the wall at 196 x 60 s x 1.1 = 3.6 h, which left out the extra call per
meeting, so a run at the planning case would have tripped its own stop.

The fake lab moved calls both ways (reset 676 to 484; vent-risk up 9%). The low case is about 0.72x the meetings
with no prompt growth: 104.4 meetings, 1,320 calls and 104.4 x (67,937 + 4,714) = 7.6M input.

**Stop rules.**

- Any `cost_usd` other than 0.0000.
- Any re-projection past 90% of a ceiling. Re-project after the probe and after 10 seeds, matched seed by seed
  against the baseline-9 bytes of the same seeds.
- A leg past 1.5x its projected wall.
- A provider refusal surviving 8 attempts.
- **Any conformance breach**, which is a code defect, not a result. Stop, fix under a new arm value, and re-record
  the round:
  - a corpse after a regroup;
  - an impostor in a vent when play resumes;
  - a kill-tick handle in an opening;
  - a second rebuttal;
  - an entry not after the impostor's own fresh kill;
  - a surfacing before the cap while the policy's own inputs showed a non-teammate in its inferred-visible set (own
    room plus neighbours; own room only under any active sabotage). Engine-truth visibility is not the test (0.4);
  - a kill at T+1 to T+4 after a regroup at meeting tick T;
  - a room-left-only witnessed exit;
  - a recorded teammate ballot target;
  - an `own_kill` row naming a teammate.
- **Checkpoints.** The recording branch is pushed after the probe, after the 10-seed re-projection and after the
  leg, each after a count-only key scan. The stall rule restarts from the last of these.
- A stall of 45 minutes with no completed seed: kill and re-run the batch, or relaunch a fresh operator from the
  pushed checkpoint. A seed on disk is never re-recorded to recover a stall.
- A `(deadline_default)` row re-records that seed alone.
- No pytest or `check.sh` in the recording checkout while a leg is live.
- Every gate runs in a bare shell, with 0 `AILIBI_*` exports printed.
- A count-only key scan before any push.
- **The freeze.** From the first seed to the merge, nothing merges into `engine/`, `agents/`, `meetings/`,
  `observation/`, `orchestrator/`, `eval/`, `api/`, `scripts/`, `llm/` or the prompt set, because the candidate's
  report, census and verification run at the merge HEAD. The record PR also re-runs every gate at its merge HEAD:
  the validity gate with the expected config, `verify_samples` on the candidate and on each committed set, the
  golden, the census conformance cells, the scorecard fold and the report-gz rebuild check.

**The probe** (seed 0; if it has no meeting or no rebuttal fired, extend to seeds 0-3):
- validity gate with `--expected-experiment-config`;
- `verify_samples`;
- the golden walker;
- census conformance;
- the scorecard fold;
- `measure_baseline.py --honesty` (a STOP);
- `scan_recording_packets.py`.

**Before and after columns.**

- **Before**: s9 at baseline 9, from the shipped census and scorecard.
- **After**: the candidate only, via `--set-dir`.
- Never pooled. Rates carry Wilson intervals.

**Assessment cells.** "Conf." means it must read exactly as built; a miss is a defect that blocks adoption. Readings
are pre-registered; the owner confirms them before the first seed (section 5).

| mechanism | cell | s9 before | effective means |
|---|---|---|---|
| R7 (B0) | exits seen only from the room left; convictions resting on them | 9/85; 8 | Conf. 0 |
| B1 exit | surfacings before the cap with a non-teammate in the policy's inferred-visible set (0.4); trips over the cap | 31/85 visibly occupied; n/a | Conf. 0 |
| B1 exit | exits seen from the exit room | 53/85 (0.62, Wilson about 0.52-0.72) | **Effective** if the share is <= 0.30. **Not effective** if >= 0.52, which triggers the named escalation: the hidden-travel card, hops capped at 1-2, with no maximize-distance-from-body term. Between the two: partial. |
| B1 exit | forced exits; ticks inside; near-body cost; kills within 2 ticks of a surfacing | 0; 1 tick (5/85 longer) | reported |
| B1 entry | entries not after the impostor's own fresh kill | 13/105 | Conf. 0 |
| B2 | stale reports; play resumes with a vented impostor; with a corpse; post-meeting kills at T+1 to T+4 after a regroup at meeting tick T; false resume perceptions; regroup notice present | 43/135; 10/107; 60/107; 28/87 within 2 ticks; n/a; n/a | Conf. 0, 0, 0, 0, 0; 100% present |
| B2 | skip rate at report meetings; meetings per game; trips closed by a regroup; kill-witness button calls within 6 ticks; dropped trigger-tick perceptions; meetings opening with an impostor in a vent | 55/135; 2.9; 0; n/a; n/a; 29/145 | reported; the opening cell is not zeroed by the reset |
| B3 | rebuttals equal the selector's pick; second rebuttals | 0 fired | Conf. |
| B3 | accused-opener rebuttals carrying a structured alibi, whereabouts or sighting for the charged tick; redirect-only rebuttals | 0/125 answered | **Effective** if >= 0.5 of opener rebuttals answer the charge. **Not effective** if < 0.2, or if redirect-only >= 0.5. Ballots citing a rebuttal turn, beneficiary kind and reporter ejections are reported only. |
| B4 | openings carrying `body-p-N-T` | 135/135 (138 calls) | Conf. 0 |
| R8 | `own_kill` rows naming a teammate or held by a non-witness | n/a | Conf. 0 |
| R8 | witness ballots citing the kill row | 4 holders, 0 rows | presence only; no power |
| R10 | recorded teammate targets; `check_no_betrayal` | 0; 0 | Conf. 0 |
| R10 | impostor EJECTs whose only citation is a neutral row | n/a | **Wording holds** if <= 0.10 of impostor EJECTs. **Does not bind** if > 0.25, which means a revision under a new arm value. |
| R10 | EJECT share; SKIP `none_held`; EJECTs `supported`; authored teammate targets; floor met only by impostors | 46/210; 95/164; 44/46; 1; 0 (pooled 0/411) | reported |
| envelope (non-gating) | impostor win share; innocent ejections, reporters per report meeting; role-correct ejections; vent-proof meetings; scorecard rows 1-9 | 11/50; 9 innocent, 7 reporters of 135; 81/90; 70/145; as published | Impostor win share outside [0.20, 0.60] flags. Above 0.60 names the fallback (status quo for B1). Reporter ejections above 0.104 per report meeting (2x baseline) flags. Reported only; the owner already accepted that the statistics move. |

Read the seen-exit cell against the exit-room column, not the all-rooms column: R7 alone removes the 9 room-left
exits. B1, B2 and R7 share the record, so outcome deltas are not attributable to one arm. The lab minus-one arms give
mechanical attribution only.

**Ladder and doc wording.** The audit and the architecture sentence say: "The ladder tip stands at baseline 9.
`replays/candidates/stage-b-r1/9p2i` is candidate round 1, recorded on the Stage-B arms named in its README; it
adopts nothing and is not a canonical sample set." `_LADDER_TIP_AUDIT` (`scripts/check_doc_facts.py:237`) is
unchanged.

**Publication.** None. `pages.yml` builds only from `replays/samples` and the featured list
(`scripts/build_demo_bundle.py:90`). The candidate is class-(a) bytes in the tree. The record PR's merge is the
owner's, and it publishes nothing.

**Untouched.**
- the bytes, MANIFESTs and reports of `replays/samples/*` and `replays/ml_corpus/*`;
- `docs/process-scorecard.*` and `docs/gameplay-census.*` (both stay baseline 9);
- the featured tour and public results;
- the watchability floors;
- the ladder tip;
- the corpus freeze and the ML fits;
- `check_vote_correctness_provenance`;
- the five levers.

---

## 5. Open for the owner

1. **Spend ceilings for round 1.** 2,800 calls, 17.5M input, 750k output, a 4.5 h recording wall (planning case
   3.9 h, stop at 4.05 h) in an 8 h window, and $0.00 marginal, with the 90% stop. The x1.35 meetings and the +10%
   prompt growth behind them are unmeasured planning assumptions, re-measured at the probe. This is the live-call
   authorization AGENTS.md requires.
2. **Landing.** Confirm `replays/candidates/stage-b-r1/9p2i` (in-tree, about 36 MB per round, verified in CI, not
   published) over the computed in-place principle. The in-place price:
   - the deferred tour work now (featured labels and the e2e guard);
   - public-results cases dropped;
   - an era-keyed doc-fact gate;
   - scorecard era pooling;
   - watchability floors;
   - about 72 re-pinned test files;
   - publication on merge;
   - all of it repeated every round.
3. **The pre-registered effective-means readings** and the non-gating balance envelope in section 4. Confirm or
   amend them before the first seed.
4. **B3's beneficiaries.** `bounded_rebuttal_version=1` is not opener-only (0.2, B3 rider). On the s9 transcripts
   it gives 21 of 144 projected replies to non-openers, 19 of them impostors, and pooled the opener loses the slot
   in 13 of 561 accused meetings. Confirm v1, as the orchestrator ruled, or ask before B5 for an opener-only value.
   That value would be new selector code under a new `bounded_rebuttal_version`, with planted tests, landed before
   B5.
5. **The direction addendum** (section 6). It lands as a `docs:` commit before wave 1 unless the owner overrules it:
   the R9 supersession, the dated exception to "stop adding levers", the B2 supersession of the section-9 deferral,
   and the B1 reversal of the phase-11 exit design.
6. **Merges.** Each of the ten implementation PRs, and the record PR.
7. **After the assessment** (not now), per arm:
   - adopt: a full four-set re-record once, or an era-keyed promotion (section 1). Only the promotion is compatible
     with the ML hold: the four-set re-record re-freezes `ml_corpus`, forces the refit and repeats the 300-seed record;
   - iterate: round 2 under a new value;
   - escalate: hidden travel for B1;
   - fall back.
   Also: R6's revisit, and the tour (ruling 11).

---

## 6. Dated amendment for `tasks/direction-2026-09-19-process-over-outcome.md`

Append after the 2026-09-20 addendum in section 12:

> Addendum, 2026-09-24 (Stage B). Section 5 called the reporter problem an instrument artifact of the 4-player
> slice. Baseline 9 contradicts that reading and it is superseded. Of the 37 innocent reporters ejected across the
> four committed sets, 36 were in 9-player games (`replays/samples/9p2i` 7, `replays/ml_corpus/9p2i` 29,
> `replays/ml_corpus/4p1i` 1, `replays/samples/4p1i` 0). `uv run python scripts/measure_baseline.py <set dir>
> --funnel`, run once per set, prints each count as `reporter ejected N/M (K innocent)`. At the 551 body-report
> meetings of the two 9-player sets, 36 of 551 reporter slots were ejected, against 4 of 1,769 innocent
> non-reporter slots: the 9p2i pool's context line in `docs/process-scorecard.md`, which
> `uv run python scripts/publish_process_scorecard.py --check` recomputes from the recordings. Baseline 8 had 34
> reporters among 46 innocent ejections (`audits/audit-phase-21-close.md` section 3.1, bar 4). The cause is the
> meeting structure. The opener speaks first; the reply chain stops on a player who has already spoken
> (`meetings/transcript.py`, `next_chain_step`); opt-in and the roll call exclude such players
> (`meetings/manager.py`, `MeetingManager.run`). So with the rebuttal switch off the opener never speaks again.
> Section 5's measurement that the reporter block renders stands; its conclusion does not.
>
> The owner took Stage B on 2026-09-24 ("We should implement stage B"). Section 10's stop on adding levers is
> amended for this wave only. No `AILIBI_*` lever and no environment switch is added. The wave adds recorded
> experiment fields, each default-OFF and recorded ON only in a candidate recording under `replays/candidates/`:
> - `vent_witness_rule` (R7, the physical witness rule);
> - `vent_exit_policy = look_and_wait` and `vent_entry_policy` (B1);
> - `report_body_handle_version` (B4);
> - `ballot_kill_row_version` (R8);
> - `impostor_ballot_version` (R10).
>
> It records the existing `meeting_reset = hub_with_grace` (B2) and `bounded_rebuttal_version = 1` (B3, without
> `reporter_reasoning`). Graduation deletes each switch and keeps its recorded key (craft rule 3). A recorded value's
> meaning is frozen, and a revision adds a new value.
>
> B2 ("full reset") supersedes section 9's deferral of the body-freshness band and cleanup decision A-28. B1 reverses
> `tasks/phase-11.md:65-68`, which exited toward the best isolated target and let a careless vent near a witness serve
> as the deliberate tell. The tell stays catchable, but the exit no longer walks into witnesses by default.
> `observed_risk` loses its mechanism when `look_and_wait` is adopted, and its lab rows stay. Impostor ballots under
> R10 express strategy: an impostor may name a crewmate only when it can cite a line it holds that points toward
> that crewmate (a turn in which someone accused them at this table, or a conflict that names them). It never
> names a teammate, and it SKIPs otherwise. The tally does not enforce the SKIP (ruling D6); a census cell counts
> every impostor EJECT whose only citation is a neutral row. The teammate firewall is unchanged. Impostor self-report stays off (R6).
> ML work and the featured tour wait until gameplay is finished (owner rulings 11 and 12).
>
> The owner also ruled that a record covers 50 seeds, not all 300. Each Stage-B round records `samples/9p2i`'s
> seeds 0-49 into its own candidate directory, and the owner assesses it against readings fixed before the first
> seed. The ladder tip stays at baseline 9 until an adopting decision.

Every number in the amendment comes from a committed command or a committed audit line, as craft rule 5 requires.
Both commands were run at `e886b663` on 2026-09-24 and gave these counts (0.4, R9 rows); the `docs:` commit re-runs
them before it lands. The meeting-structure counts (521 of 676 first replies accuse the opener; 0 of 676 opener
second turns) are left out until a committed instrument reproduces them: A1 appends them with its `--check`
command when it merges (3.4, card 2).

---

## Appendix: reproduction

The scratch scripts named here are session aids and are not committed; the load-bearing counts are
reproduced by the committed commands in the second table. Count-only re-checks, in
`<session scratchpad>/synth_b/`.
Run each from the repo root at `e886b663`:

| script | gives |
|---|---|
| `invent.py <synth0924>/walk.json` | the in-vent openings: 101 meetings, 102 of 105 slots |
| `entry_gate.py <synth0924>/walk.json` | 103 of 587 entries removed (s9 13 of 105) |
| `r9.py <synth0924>/walk.json` | reporter ejections per set |
| `calls.py replays/samples/9p2i` | the per-meeting totals: 5,815 input per call; 7,710 on each meeting's last call |
| `calls2.py replays/samples/9p2i` | speech 4,092, last speech 4,714, ballot 7,530 |
| `handle_count.py <four set dirs>` | 632 calls, 623 meetings carrying `body-p-N-T` (a regex count; no text printed) |

`<synth0924>/walk.json` is the synthesis walk (`walk.py`), which is state-hash verified.

Added when the critic's findings were applied (same date, same commit):

| command | gives |
|---|---|
| `uv run python scripts/measure_baseline.py replays/<set> --funnel` (committed; once per set) | `reporter ejected 7/80 (7 innocent)` on s9, `29/241 (29 innocent)` on c9, `1/21 (1 innocent)` on c4, `0/17 (0 innocent)` on s4 |
| `uv run python scripts/publish_process_scorecard.py --check` (committed) | `docs/process-scorecard.md:94`: reporter slots 36/551 ejected against innocent non-reporter slots 4/1769 (per set `:131`, `:166`, `:201`, `:236`) |
| `.../scratchpad/stageb_rb/rb_roles.py <out.json>` (scratch, count-only) | B3 beneficiaries by role: s9 123 opener, 19 impostor, 2 other crew; pooled 548, 113, 12 |
| `.../scratchpad/stageb_rb/rb_census.py <out.json>` (scratch, count-only) | opener accused 561 pooled (s9 125); selector fires 673 (s9 144) |
