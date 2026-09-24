# B5: record s9 seeds 0-49 as candidate round 1 and assess it

**Status:** ready

## Outcome

Every Stage-B switch now exists as a default-OFF recorded experiment field, but no recording has
them ON, so the owner cannot yet judge whether they work. This card records one 50-seed candidate
round with every switch ON and assesses it against readings committed before the first seed.

After this card:
- `replays/candidates/stage-b-r1/9p2i/` holds seeds 0-49 of the 9-player sample roster (9 players,
  2 impostors, 2 tasks per crewmate). They are recorded on featherless `Qwen/Qwen3.6-27B` with the
  prompt set `qwen3_6_27b`, the bare substrate slate and one declared config file. Every tick row
  carries that config, and the round README carries the file's sha256.
- `audits/audit-<YYYY-MM-DD>-stage-b-r1.md` opens with a pre-registration that lands on `main` before
  the first seed, then records the spend, gates and events, and the assessment: s9 at baseline 9
  before and the candidate after, never pooled; process cells first, then a reading per arm; role-
  correct and win-split rows beside, gating nothing; a decision menu last.
- Nothing publishes, and the ladder tip stays at baseline 9. The candidate adopts nothing. Each arm's
  next step is the owner's decision after reading the audit, and the merge is the owner's.

This card records and reports. It changes no code, template or instrument. It is card 11 of the
Stage-B set (decision memo 3.1), in wave 5, and it merges last.

## Evidence

Sources, dated 2026-09-24, in the orchestrator's `stage-b-2026-09-24/` directory (not in the tree):
the decision memo, sections 0, 1, 2.1, 2.6, 3.2, 3.3, card 11 of 3.4, 4 and 5; `census_and_record.md`,
sections 1 and 5; `partial_record.md`, sections 4 and 7. Every `path:line` below is at `e886b663`;
re-anchor each by its named symbol at dispatch. Every memo count was measured at `e886b663`;
re-measure it at dispatch with the command named for it.

**The owner's rulings of 2026-09-24, verbatim** (memo 0.1):
- "We should implement stage B"
- "Let's not re-record all 300 seeds each time. When it's time to record, record the smaller group
  of 50 seeds, assess if the implementations have been effective and resulted in desired results.
  Also it is understood that updating the vent and body reset logic will probably have a
  substantial effect on previous limits and statistics around the baseline voting results, that
  is okay."
- "B3. Allow one reply for the opener"
- "Hold off on ML as D suggests until gameplay is finished."
- "Tour fix can be deferred to after gameplay is finished"

**The orchestrator's rulings, under the owner's delegation of 2026-09-24** (memo 0.2 and 0.3):
- Landing (0.3 item 1): "The 50 seeds go to `replays/candidates/stage-b-r1/9p2i/`: in-tree, class
  (a) plus (b), under one `replays/candidates/` family row." The owner may overrule it (memo 5,
  item 2). Config only (item 5): the recorder refuses every ambient `EXPERIMENT_ENV_NAMES` export.
- Item 6: "Once round 1 is recorded, an arm value's meaning is frozen." Item 9: "The record card's
  preflight asserts the guard is gone and the declared config validates."
- R6: impostor openers are a conformance cell. R8: the kill row is "assessed for presence only".
  R10: "Enforcement is by instruction, not by the tally"; a census cell counts every ungrounded
  impostor EJECT. R13: "Candidate columns live in the record's audit, computed by `--set-dir` modes
  that write nothing."
- The B3 rider: `bounded_rebuttal_version=1` alone, a stated deviation from ruling 4's words. On
  the s9 transcripts, v1 fires 144 times: 123 to the opener, 19 to impostors and 2 to other
  crewmates. The opener loses the slot in 2 of its 125 accused meetings. The owner confirms v1, or
  asks for an opener-only value, before this card (memo 5, item 4).

**The mechanism and the declared config** (memo 1). Arms are stamped on every tick row and
re-simulated from there, so a bare shell verifies an arms-ON set. Only s9's seeds 0-49 are recorded,
into a candidate directory that the verify leg, the golden and a candidate test walk in CI; the
other three sets and s9 keep their baseline-9 bytes. The config file is one line plus a newline:
`{"format_version": 1, "meeting_reset": "hub_with_grace", "vent_exit_policy": "look_and_wait", "vent_entry_policy": "own_fresh_kill", "vent_witness_rule": "physical", "bounded_rebuttal_version": 1, "report_body_handle_version": 1, "ballot_kill_row_version": 1, "impostor_ballot_version": 1}`.
At those bytes `shasum -a 256` prints
`4f0c4dd4779cd38f69194b6735221d86bf7c6944fe12769a3971e38e4e46d6c7`; recompute it at
pre-registration. `self_report` stays False, `contextual_self_report_version` and
`evidence_reasoning_version` stay None, and the slate is bare, so `reporter_reasoning` is OFF. The
ballot stamp served is
`vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1`,
beside the three unchanged `.v6` stamps (memo 3.3).

**The spend anchor** is the baseline-9 s9 leg (`audits/audit-2026-09-22-process-rerecord.md:415`,
meetings at `:628`): 145 meetings, 1,694 calls, 9,850,930 input and 422,941 output tokens, 2h24m55s
(8,695 s), `$0.0000`. Per meeting that is 11.68 calls, 67,937 input, 2,917 output and 60 s. The
tally command in Validation, run at `e886b663`, reproduces the three counts and cost 0.0 from the
replays' own `llm_calls` rows. A rebuttal is a speech call: about 4,714 input (the last speech call
on s9, memo 0.4) and 363 output (`rebuttal_and_body_handle.md`, "Projected spend on s9").

**Operating discipline from the previous record** (`tasks/work/process-rerecord.md` and its audit):
the probe seed records alone, then the rest, because `refresh_samples.sh` re-records a replay on disk
(that card's deviation 1); the honesty probe is a STOP; a `(deadline_default)` row re-records its
seed alone (audit event 3, `:902-914`); the 45-minute stall rule; a count-only key scan over five
patterns, each firing on a planted key (`:1547-1568`); reports gzipped through `eval/report_io.py`;
the key passed by `uv run --env-file` from a 0600 file outside the repository, deleted afterwards
(`tasks/work/fresh-deduction-calibration-2.md:867`). No code loads `.env` (`git grep dotenv`).

**Hazards.**
- `tests/scripts/test_refresh_samples.py:1181-1219` inventories `replays/` and deletes new paths,
  and seeds stage in `dirname(SAMPLE_DIR)` (`scripts/refresh_samples.sh:736`).
- The recorder reads `HEAD` once per run into every MANIFEST `git_sha` (`:692-694`), so a commit in
  the recording checkout between the probe and the rest splits the round across two shas.
- The fake provider is refused under `replays/` (`:615-639`). The demo bundle reads only
  `replays/samples` and the featured list (`scripts/build_demo_bundle.py:90`).
- The ladder tip is read from `_LADDER_TIP_AUDIT` (`scripts/check_doc_facts.py:237`); each "ladder
  tip" sentence in `audits/README.md` must name it (`:1705`), and the index links every audit once
  (`:2428`). The `audits/` registry row states exact tracked bytes (`_STATED_BYTES`,
  `scripts/verify_ml_evidence.py:2864`). s9 is 36 MB; unlike it, the candidate gets no rubric file
  (`scripts/refresh_samples.sh:1049`).

## Acceptance

Each item names its enforcing mechanism and the planted or perturbed case that proves it bites. `P`
is the pre-registration commit. `F` is the frozen HEAD, the `main` commit every MANIFEST row stamps;
P is `F` or an ancestor of it. Symbols from the prerequisite cards are named as those cards specify
them and re-anchored at dispatch: the gate's `--expected-seeds` and `--require-one-recording-sha`,
the census and scorecard `--set-dir DIR --json-stdout`, the golden's directory walk,
`tests/_helpers/scripted_meeting.py` and the candidate test.

- [ ] **The owner's confirmations and the pre-registration precede the first seed, and neither is
  rewritten.**
  - Mechanism: no provider call is made until the owner has answered memo 5 items 1-4 in their own
    words: the ceilings under Constraints, the landing, the readings and envelope below, and v1 or
    an opener-only rebuttal value. P is a `coordination:` commit on `main` holding the audit's
    pre-registration section, its `audits/README.md` row and the re-derived `docs/artifacts.md`
    `audits/` row. The section holds the confirmations (verbatim and dated), the config bytes and
    their sha256, the ceilings with their arithmetic, the stop rules, the before column, the readings
    and the envelope.
  - The config file is not committed at P, because a round directory without its set directory
    fails the candidate test on `main`. The delivery commit adds it, and its sha256 must equal P's.
    Until then the recording and verification checkouts each hold an untracked copy of P's declared
    bytes at the `CFG` path (`replays/candidates/stage-b-r1/experiment-config.json`), and
    `shasum -a 256` on each copy must equal P's before the dry run and before any gate reads it; a
    mismatch stops the card. No pytest or `check.sh` runs in a checkout while that copy sits there
    without its set directory (the candidate test would read a half-formed round): in the
    verification checkout the copy is moved aside for those runs and re-checked when restored.
  - `git merge-base --is-ancestor P <the MANIFEST's one git_sha>` exits 0. The section at P equals
    the section at the PR head; any correction is a dated addendum after it.
  - Proof: the ancestry command with P replaced by the PR head exits 1. A one-character edit to a
    reading, in a scratch copy, makes the section comparison print a difference.
- [ ] **The before column is the shipped baseline-9 numbers.** Mechanism: at `F`, the census and
  scorecard `--set-dir replays/samples/9p2i --json-stdout` outputs equal, cell for cell, the s9
  entries of `docs/gameplay-census.json` and `docs/process-scorecard.json`. A command the audit quotes prints
  the before table from them and re-measures every memo count below. The ballot family's before
  values come from `measure_baseline.py replays/samples/9p2i --honesty --json` at `F`, as the
  ballot card reports them. Proof: the comparison against a copy with one cell edited is
  non-empty.
- [ ] **The readings are pre-registered as memo 4 fixes them.** "Conf." cells must read exactly as
  built, and a miss is a code defect that stops the round. "Reported" cells carry no rule. Rates
  carry Wilson 95% intervals. The per-arm reading is computed from the after column by P's rules,
  never restated, and P's section also fixes each after value's source (the assessment item
  below). The table sits in P's section, so the first item's proof covers it.

  | arm | cell | s9 before | pre-registered reading |
  |---|---|---|---|
  | physical witness | exits seen only from the room left; convictions resting on them | 9/85; 8 | Conf. 0; 0 |
  | look and wait | surfacings before the cap with a non-teammate in the policy's inferred-visible set (own room plus neighbours, own room only under any sabotage); trips over the cap | 31/85 visibly occupied; n/a | Conf. 0; 0 |
  | look and wait | exits seen from the exit room | 53/85 = 0.62 (Wilson 0.52-0.72) | effective at 0.30 or below; not effective at 0.52 or above, which names the hidden-travel escalation (hops capped at 1-2, no maximize-distance-from-body term); partial between |
  | look and wait | forced exits; ticks inside; near-body cost; kills within 2 ticks of a surfacing | 0; 1 tick (5/85 longer) | reported |
  | own fresh kill | entries not after the impostor's own fresh kill | 13/105 | Conf. 0 |
  | full reset | stale reports; play resumes with a vented impostor; with a corpse; kills at T+1 to T+4 after a regroup at meeting tick T; false resume perceptions; regroup notice present | 43/135; 10/107; 60/107; 28/87 within 2 ticks; n/a; n/a | Conf. 0, 0, 0, 0, 0; present every time |
  | full reset | skip rate at report meetings; meetings per game; trips closed by a regroup; kill-witness button calls within 6 ticks; dropped trigger-tick perceptions; meetings opening with an impostor in a vent | 55/135; 2.9; 0; n/a; n/a; 29/145 | reported; the reset does not zero the opening cell |
  | one reply | rebuttals equal the selector's pick; second rebuttals | 0 fired | Conf. |
  | one reply | accused-opener rebuttals answering the charge with an alibi, whereabouts or sighting; redirect-only rebuttals | 0/125 answered | effective if half or more answer; not effective below 0.2, or if redirect-only reaches half. Ballots citing a rebuttal, beneficiary kind and reporter ejections are reported |
  | body handle | openings carrying the kill-tick handle `body-p-N-T` | 135/135 (138 calls) | Conf. 0 |
  | kill row | `own_kill` rows naming a teammate or held by a non-witness | n/a | Conf. 0 |
  | kill row | witness ballots citing the kill row (evidence-honesty ballot cell 5) | 4 holders, 0 rows | presence only |
  | impostor ballot | recorded teammate targets; `check_no_betrayal` (the validity gate) | 0; 0 | Conf. 0 |
  | impostor ballot | impostor EJECTs whose only citation is a neutral row (evidence-honesty ballot cell 3) | n/a | the wording holds at 0.10 or below; it does not bind above 0.25, which calls for a revision under a new value |
  | impostor ballot | EJECT share; SKIP `none_held`; EJECTs `supported`; authored teammate targets; floor met only by impostors | 46/210; 95/164; 44/46; 1; 0 (pooled 0/411) | reported |
  | self-report off | impostor openers | 0 | Conf. 0 |
  | envelope | impostor win share; innocent ejections, and reporters ejected per report meeting; role-correct ejections; vent-proof meetings; scorecard rows 1-9 | 11/50; 9 innocent, 7 of 135; 81/90; 70/145; as published | non-gating. A win share outside 0.20-0.60 is flagged, and one above 0.60 names the status-quo fallback for the vent exit. Reporter ejections above 0.104 per report meeting (twice 7/135) are flagged |

- [ ] **The preflight holds at `F`.** Mechanism: `git grep -n WAVE_ARMS_PENDING -- '*.py'` prints
  nothing. The declared file validates as a `RecordedExperimentConfig` whose non-default fields are
  exactly the eight above, and `prompt_versions_for_set(..., experiment_config=...)` returns the
  composite ballot stamp beside the three `.v6` stamps. Proof: validation with one unknown key added
  is refused (`extra="forbid"`), and with one field removed the non-default set has seven members.
- [ ] **The fake dress rehearsal passes every instrument at `F`, at $0.** Mechanism: seeds 0-49 are
  recorded with `AILIBI_LLM_PROVIDER=fake` on the declared config, into a scratch directory outside
  `replays/`. Each of these then exits 0 on it: the census `--set-dir` with every Conf. cell at 0;
  the scorecard `--set-dir`; the validity gate with `--expected-experiment-config`,
  `--expected-seeds 0-49` and `--require-one-recording-sha`; `verify_samples.sh <dir>`; the golden's
  directory walk; `measure_baseline.py <dir> --honesty`; and `scan_recording_packets.py <dir>`.
  Proof: gated against a copy of the config without `vent_witness_rule`, the gate fails and names
  the field.
- [ ] **The scripted rehearsal proves that the meeting arms fire.** Fake games eject nobody and fire
  no rebuttal (`partial_record.md` section 7). Mechanism: at `F`, the scripted cases that the readers
  and ballot cards landed pass: a rebuttal, an impostor EJECT with and without a row pointing toward
  the target, a kill row and a teammate coercion. Then one scratch scripted game on the full declared
  config passes the plain loader, the census and scorecard `--set-dir` and the gate, with its
  rebuttal counted once. Proof: those cards' perturbed cases pass at `F`; for example, dropping the
  evidence profile leaves the rebuttal call unconsumed.
- [ ] **The lab attribution matrix runs at `F`.** Mechanism: `experiments.tactical_gameplay` runs on
  the development split (seeds 1000-1007, both rosters) for ten arms: `baseline`, `vent_risk`,
  `vent_physical`, `vent_look_and_wait`, `vent_own_fresh_kill`, `stage_b_full` and the four
  minus-one arms. It writes the new `audits/tactical-gameplay/stage-b-r1-frozen-head.json`, and the
  audit quotes count-only rows and the runtime fingerprint as mechanical attribution only. Proof:
  the `baseline` and `vent_risk` rows equal `audits/tactical-gameplay/stage-b-development.json` in
  waits, exposure and calls. A mismatch means a default path moved, and it stops the card.
- [ ] **The dry run and the probe pass before the rest of the round queues.** Mechanism: the dry run
  echoes P's sha256, the eight fields and the bare slate, and leaves `git status --porcelain` at 0
  lines. Seed 0 then records, and the probe runs on it: the gate with the declared config,
  `verify_samples.sh`, the golden's walk, the census conformance cells, the scorecard fold,
  `measure_baseline.py --honesty` (a raise is a STOP) and `scan_recording_packets.py`. A seed 0 with
  no meeting or no fired rebuttal extends the probe to seeds 0-3; seeds 0-3 with a meeting but no
  rebuttal stop the card. Proof: the dry run with a stray `AILIBI_BOUNDED_REBUTTAL=1` exits 1.
- [ ] **The round is exactly the declaration.** Mechanism: `scripts/validity_gate.py` on the
  candidate passes all ten checks, named individually, with `--expected-model Qwen/Qwen3.6-27B
  --require-zero-cost`, the four `--expected-prompt-versions` pairs, `--expected-experiment-config`,
  `--expected-seeds 0-49` and `--require-one-recording-sha`. The MANIFEST's flags column equals s9's
  and its policy column reads `fsm-default`; `grep -l deadline_default` over the 50 replays counts 0;
  the plumbing card's candidate test passes in `check.sh`. Proof: the gate with
  `--expected-seeds 0-50` fails, and so does `replays/samples/9p2i` against the declared config.
- [ ] **Every conformance cell reads 0 on the round.** Mechanism: the census `--set-dir` exits 0 on
  the candidate; on any breach it exits non-zero, naming (set, seed, meeting). The golden, which
  `check.sh` runs on every candidate directory, reproduces every call. Proof: at `F`, the census
  card's planted breach per Conf. cell and each arm card's end-to-end perturbed copy pass; Results
  names them by test id.
- [ ] **The spend stays inside the ceilings.** Mechanism: the tally command counts the candidate's
  `llm_calls` rows. It re-projects after the probe and after 10 seeds, as Constraints defines, and
  compares each figure with 90% of its ceiling. Proof: on `replays/samples/9p2i` the tally prints
  `1694 9850930 422941 0.0`, so it is the same measure as the anchor.
- [ ] **The recording checkout never moves, and no key leaves it.** Mechanism: seeds record in a
  checkout detached at `F`. Checkpoints are commits in a separate delivery worktree on
  `work/stage-b-record-r1`, made after the probe, after the 10-seed re-projection and after the leg.
  A count-only key scan, with gzip decompressed, precedes each push. The key file is 0600, outside
  the repository, and deleted after the last seed. Proof: the MANIFEST names one `git_sha`, the short
  sha of `F`; each of the five scan patterns fires once on a planted key.
- [ ] **The freeze held.** Mechanism: `git log --oneline F..HEAD` and `git log --oneline
  F..origin/main` print nothing over `engine agents meetings observation orchestrator eval api
  scripts llm` at the PR head. Proof: the same pathspec over `e886b663..F` is non-empty, so the
  command does see code changes.
- [ ] **The derived views and the registration are rebuilt, never hand-edited.** Mechanism: the
  recorder's post-step writes `tournament-eval-report.json.gz` through `eval/report_io.py`, and
  `build_sample_report.py --sample-dir <candidate> --check` is consistent. The round README's
  `candidate-declaration` block holds the sha256 line and `9p2i seeds 0-49`. The `replays/candidates/`
  and `audits/` rows of `docs/artifacts.md` are re-derived with `git ls-files`: the family holds 56
  files (the family README, the round README, the config and 53 set files), and offline
  `verify_ml_evidence.py` reads both rows as OK. Proof: the plumbing card's planted round
  perturbations (a config byte, a missing seed, a foreign sha, an edited report cell) pass.
- [ ] **The assessment is written as pre-registered.**
  - Mechanism, the pre-registered source rule: the after column comes only from these, run on the
    candidate: the census and scorecard `--set-dir DIR --json-stdout`; `measure_baseline.py DIR
    --honesty --json`, whose ballot family (the ballot card's evidence-honesty cells) supplies cell
    3, impostor EJECTs whose valid citations are only neutral rows (the impostor-ballot compliance
    reading), and cell 5, witness ballots citing the kill row (the kill-row reading); and the
    validity gate's `check_no_betrayal`. None of them is pooled with the before column. Process
    cells come first, then the
    per-arm readings under P's rules, the envelope, and the role-correct and win-split rows, which
    gate nothing. Only the Conf. cells and the lab rows attribute an effect to one arm.
  - The decision menu, per arm: adopt through the era-keyed promotion (memo 1, adoption option
    (b)), which is compatible with the ML hold; iterate as round 2 under a new value in
    `replays/candidates/stage-b-r2/`; escalate to hidden travel for the vent exit; or fall back to
    the status quo.
  - Proof: pooling s9 with the candidate through the census raises its mixed-era refusal.
- [ ] **Nothing publishes, and nothing committed moves.** Mechanism: `git diff --stat F..HEAD` is
  empty over the committed sets, `tests/fixtures`, `training`, `api`, `frontend` and the scorecard
  and census docs. `verify_samples.sh` passes once per set directory on all four sets and on the
  candidate. The four committed `build_sample_report.py --check` runs, the scorecard and census
  `--check` and `check_doc_facts.py` (with `_LADDER_TIP_AUDIT` unchanged) exit 0, the word-budget
  test stays green with `_ARCHITECTURE_WORD_BUDGET` unedited, and the demo bundle
  built at `F` and at the head is byte-identical (`diff -r`). Proof:
  `test_audits_index_ladder_tip_drift_detected` and `test_unindexed_audit_detected` pass at the head.
- [ ] **The copy this card adds is plain.** Mechanism: in the round README, the candidate
  sentence and the prose of the index row (its link aside), a count-only scan for
  `\b[AB][0-9]\b|\bR[0-9]+\b|Task [0-9]|audit-` prints 0. The README names switches by field and
  in plain words, points to the assessment through `audits/README.md`, and states no threshold
  arithmetic. Proof: the scan over a scratch copy with "R7" inserted prints 1.

## Constraints

**The partial-record principle binds this card.**
- Only `replays/samples/9p2i`'s seeds 0-49 are re-recorded, and only into
  `replays/candidates/stage-b-r1/9p2i/`. The recorder refuses a non-default config aimed at
  `replays/samples/` or `replays/ml_corpus/`.
- Every switch is a `RecordedExperimentConfig` field, default-OFF and omitted at its default. This
  card sets values; it adds no field, lever or env switch.
- Every committed recording, derived view, fixture, gate and doc fact keeps verifying
  byte-identically, and there is no registry prompt bump.
- Role-correctness is reported and never gated. Nothing pushes an agent toward the correct answer,
  and the meeting layer labels and never rewrites.

**Ceilings: PROPOSED, pending the owner's explicit confirmation before the first seed** (memo 4, and
memo 5 item 1; this is the live-call authorization AGENTS.md requires).

| limit | planning case | ceiling (planning / 0.9, rounded up) | hard stop at 90% |
|---|---|---|---|
| model calls | 196 x 12.68 = 2,485 | 2,800 | 2,520 |
| input tokens | 196 x (67,937 x 1.10 + 4,714) = 15.57M | 17,500,000 | 15,750,000 |
| output tokens | 196 x (2,917 + 363) = 642,880 | 750,000 | 675,000 |
| recording wall | 196 x 60 s x (12.68 / 11.68) x 1.1 = 14,043 s = 3.9 h | 4.5 h, inside an 8 h window | 4.05 h |
| marginal cost | $0 on flat-rate Featherless | $0.00 | any `cost_usd` other than 0.0000 |

196 is 145 x 1.35, rounded, and 12.68 is 11.68 plus one rebuttal call. The x1.35 meetings and the
+10% prompt growth are **unmeasured planning assumptions**, re-measured at the probe. The low case,
about 0.72x the meetings with no growth, is 104.4 meetings, about 1,320 calls and 7.6M input. The
subscription fee is already paid and is not incurred by this run.

**Re-projection**, after the probe and after 10 seeds: each count is (the candidate total over the
completed seeds / the s9 total over the same seeds) x the s9 leg total. Wall is the elapsed recording
wall / the completed seeds x 50.

**Stop and report to the owner**, with the partial output and the last checkpoint, on:
- any `cost_usd` other than 0.0000, or a projection past 90% of a ceiling;
- a leg past 1.5x the probe's projected wall, or past 4.05 h;
- a provider refusal that survives 8 attempts, or a probe raise;
- any conformance breach. It is a code defect, not a result. The fix lands under a new arm value,
  and the round re-records from seed 0 under a new declared config, with a dated pre-registration
  addendum and the owner's clearance.

**Stalls and failed seeds.** A stall is 45 minutes with no completed seed: kill and re-run the
batch, or relaunch a fresh operator from the last pushed checkpoint. A seed on disk is never
re-recorded to recover a stall. A `(deadline_default)` row marks a failed recording: remove its husk
and re-record that seed alone at `F`, logging the cause as it happens. No seed re-records for any
other reason.

**Three checkouts.** Recording: a fresh worktree detached at `F` (`uv sync --frozen`, no `.env`)
that runs only the recorder; no pytest or `check.sh` runs there while a leg is live. Verification: a
worktree at `F` for the pre-spend and every gate. Delivery: the `work/stage-b-record-r1` worktree
that receives the checkpoint copies.

**Shells.** Every gate runs in a bare shell and first prints its `AILIBI_*` count (0). The recording
shell sets only `AILIBI_LLM_PROVIDER=featherless`, `AILIBI_PROMPT_SET=qwen3_6_27b`,
`AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B`, the 9/2/2 roster, `AILIBI_SAMPLE_DIR` and
`AILIBI_MANIFEST` on the candidate, `AILIBI_REFRESH_WORKERS=2` and `AILIBI_SEED_MAX_ATTEMPTS=8`.
`FEATHERLESS_API_KEY` enters only through `uv run --env-file` from the key file; no step reads
`.env`. No rendered prompt or seed-band prefix is printed, and every census is count-only.

**The freeze.** From the first seed to the merge, nothing merges into `engine/`, `agents/` (the
prompt set included), `meetings/`, `observation/`, `orchestrator/`, `eval/`, `api/`, `scripts/` or
`llm/`, because the candidate's report, census and verification run at the merge head. If `main`
moves in those paths, stop and ask. Otherwise, merge `main` in and re-run every gate.

**Wave, order and ownership.**
- Wave 5. Start after all ten Stage-B cards have merged, once the ballot card has deleted the
  emptied pending guard and the dated direction addendum (memo 6) is on `main`. This card merges
  last, and the owner merges it.
- Shared files (memo 3.2, as amended for this card set), one writer at a time:
  `docs/experiment-arms.md` (the spine, then this card's sentence), or under the swap
  `docs/architecture.md` (A3, the spine, then this card); `docs/artifacts.md` (A1, readers,
  plumbing, look-and-wait, the meeting reset, then this card, in merge order, each writing only
  its own row; this card's are the `replays/candidates/` file count and the `audits/` row,
  recomputed with `git ls-files` after merging `main`); `audits/README.md` (this card appends one
  row).
- Never edited here: `scripts/verify_ml_evidence.py`, `audits/tactical-gameplay/README.md` (the vent
  and reset cards own it) and `tasks/README.md` (the orchestrator's).

**Delivery.**
- Branch `work/stage-b-record-r1`, one PR into `main`, merged or fast-forwarded, never squashed.
  Never amend a pushed commit; merge `main` in, never rebase. Each commit body, P included, carries
  `Card: tasks/work/stage-b-record-r1.md` immediately followed by
  the `Co-Authored-By:` attribution line the worker's own session supplies (never a model name copied from this card).
- The PR body fills Summary, Definition of done, Decisions and Questions, and ends with the Claude
  Code attribution line. Agents post no PR comments. The worker fills Results; the orchestrator owns
  the Status line.

**What stays out:** a second round, any other set, the held-out band, ML training or refits
(ruling 12), tour, featured-list or public-results changes (ruling 11), scorecard or census cells
(R13), watchability floors, adoption, graduation and the revisit of R6.

**Stop and ask** if the owner's answer to memo 5 item 4 changes `bounded_rebuttal_version` (that
version's card merges first, and the config, its sha256 and P change with it); if the owner
overrules the landing; if a gate at `F` needs a code change; if a test outside the candidate
machinery turns red only because a round exists; or if the scripted helper cannot take the full
declared config.

## Expected scope

- `replays/candidates/stage-b-r1/README.md` (plain copy and the `candidate-declaration` block) and
  `experiment-config.json` (the declared bytes).
- `replays/candidates/stage-b-r1/9p2i/`, written by the recorder: `replay-seed-0.jsonl` to
  `replay-seed-49.jsonl`, `MANIFEST.md`, `roster.json` and `tournament-eval-report.json.gz`.
- `audits/audit-<YYYY-MM-DD>-stage-b-r1.md`, dated the day P lands, and its row in
  `audits/README.md`.
- `audits/tactical-gameplay/stage-b-r1-frozen-head.json`, new, written by the lab harness.
- `docs/artifacts.md`: the `replays/candidates/` file count and the `audits/` row.
- The candidate sentence, the memo's in plain words: "The ladder tip stands at baseline 9.
  `replays/candidates/stage-b-r1/9p2i` is candidate round 1, recorded with the experimental switches
  its README names; it adopts nothing and is not a canonical sample set." By default it goes on the
  spine's arm page, `docs/experiment-arms.md`. `docs/architecture.md` is held to 1,300 words by
  `_ARCHITECTURE_WORD_BUDGET` (`tests/scripts/test_check_doc_facts.py`, `_word_budget_problems`),
  a constant no card edits, and the documentation-truth card and the spine leave it at or near
  that ceiling. If the sentence must sit there instead, after "Baselines are adopting records", it
  replaces a sentence of equal or greater length, the ladder paragraph still names baseline 9 and
  its audit (the documentation-truth card's test), and Results records the swap.
- This card's Results.

Not in scope: every code, template, test and instrument file; `replays/samples/`,
`replays/ml_corpus/`, `tests/fixtures/` and `training/`; `docs/process-scorecard.*`,
`docs/gameplay-census.*`, `docs/glossary.md` and `README.md`; the featured list, public results and
watchability floors; `scripts/check_doc_facts.py`.

## Record impact

**What moves:** the round (55 new tracked files, about 36 MB if it matches s9's size), the audit and
its index row, the lab JSON, two `docs/artifacts.md` rows, one candidate sentence (on the arm page,
or swapped in on the architecture page) and this card.

**What stays unchanged:** all bytes, MANIFESTs and reports under `replays/samples/*` and
`replays/ml_corpus/*`; `docs/process-scorecard.*` and `docs/gameplay-census.*`, which stay at
baseline 9; the tour, public results, watchability floors and the ladder tip; the corpus freeze and
the ML fits; `check_vote_correctness_provenance` and the four-set doc-fact agreement, since the
candidate sits outside `_RECORDED_SETS`; the five levers, the prompt registry and every default. No
future behaviour changes; CI reads the candidate like a sample set (verify leg, golden, candidate
test, report rebuild).

**Publication:** none. `pages.yml` builds only from `replays/samples` and the featured list, and this
card touches no file under `api/` or `frontend/` and no shown replay. P's push to `main` re-runs
`pages.yml` and the bundle rebuilds byte-identical. The record PR proves the bundle identical at `F`
and at its head.

**Evaluation:** the audit reports cells and readings and gives no verdict; the owner decides each
arm. Adoption is a later card. It is either the era-keyed promotion, which lifts the plumbing refusal
for `replays/samples/9p2i` and is the path compatible with the ML hold, or a four-set re-record.
Graduation keeps each field's recorded key.

## Validation

Every command runs in a bare shell. Quote each exit code as it came back.

```
# the tally; on replays/samples/9p2i it prints 1694 9850930 422941 0.0 (run at e886b663)
uv run python -c 'import glob,json,sys
c=i=o=0; u=0.0
for p in glob.glob(sys.argv[1]+"/replay-seed-*.jsonl"):
  for r in map(json.loads,open(p)):
    for k in r.get("llm_calls") or []:
      c+=1; i+=k["input_tokens"]; o+=k["output_tokens"]; u+=k["cost_usd"]
print(c,i,o,u)' <set dir>
git grep -n WAVE_ARMS_PENDING -- '*.py'                         # nothing, at F
CFG=replays/candidates/stage-b-r1/experiment-config.json; C=replays/candidates/stage-b-r1/9p2i
shasum -a 256 "$CFG"                                            # equals P's
# the recording checkout, detached at F, with the slate from Constraints set inline
bash scripts/refresh_samples.sh --full --expect-levers "" --experiment-config "$CFG" --dry-run
uv run --env-file "$KEYFILE" bash scripts/refresh_samples.sh --seeds 0 --expect-levers "" --experiment-config "$CFG"
uv run --env-file "$KEYFILE" bash scripts/refresh_samples.sh --seeds "$(seq -s, 1 49 | sed 's/,$//')" \
  --expect-levers "" --experiment-config "$CFG"
# gates, in the verification or delivery worktree
env | grep -c '^AILIBI_'                                        # 0
uv run python scripts/validity_gate.py "$C" --expected-model Qwen/Qwen3.6-27B --require-zero-cost \
  --expected-prompt-versions <the four KEY=VER pairs> --expected-experiment-config "$CFG" \
  --expected-seeds 0-49 --require-one-recording-sha
uv run python scripts/publish_gameplay_census.py --set-dir "$C" --json-stdout > "$SCRATCH/census-after.json"
uv run python scripts/publish_process_scorecard.py --set-dir "$C" --json-stdout > "$SCRATCH/scorecard-after.json"
uv run python scripts/measure_baseline.py "$C" --honesty
uv run python scripts/scan_recording_packets.py "$C"
bash scripts/verify_samples.sh                                  # both sample sets plus the candidate
for d in replays/samples/9p2i replays/samples/4p1i replays/ml_corpus/9p2i replays/ml_corpus/4p1i "$C"; do
  bash scripts/verify_samples.sh "$d"; uv run python scripts/build_sample_report.py --sample-dir "$d" --check; done
grep -l deadline_default "$C"/replay-seed-*.jsonl | wc -l       # 0
git merge-base --is-ancestor P "$(awk -F'|' '$2 ~ /^ *[0-9]+ *$/ {gsub(/ /,"",$8); print $8}' "$C/MANIFEST.md" | sort -u)"
git log --oneline F..HEAD -- engine agents meetings observation orchestrator eval api scripts llm          # empty
git log --oneline F..origin/main -- engine agents meetings observation orchestrator eval api scripts llm   # empty
git diff --stat F..HEAD -- replays/samples replays/ml_corpus tests/fixtures training api frontend \
  docs/process-scorecard.md docs/process-scorecard.json docs/gameplay-census.md docs/gameplay-census.json  # empty
uv run python scripts/build_demo_bundle.py --out "$SCRATCH/bundle-head"   # and bundle-F at F; diff -r is empty
# the whole gate, in the delivery worktree, after the leg
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/check_doc_facts.py
uv run python -c "print(len(open('docs/architecture.md').read().split()))"   # at most 1300
uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py                     # offline; never --complete
uv run pytest -m campaign -q                                    # the c9 refit pins' campaign half
bash scripts/check.sh; echo "check.sh exit $?"                  # whole, in a clean worktree
```

The pre-spend at `F`: the fake rehearsal with the same gates on a scratch target, the scripted
cases, and the lab with the ten arms and `--output audits/tactical-gameplay/stage-b-r1-frozen-head.json`.
The section comparison diffs `git show P:<audit>`'s pre-registration section against the head's.
`npm --prefix frontend test` and the e2e are not required: nothing under `api/` or `frontend/`
changes, the bundle comparison stands in, and `check.sh` runs the frontend unit tests.

## Results

Not started. The operator records, here and in the PR: the owner's confirmations (verbatim, dated),
P's sha, `F` and each checkout by role; the pre-spend outputs, the dry-run echo, the probe, both
re-projections and the spend against each ceiling; every event and every Validation command with its
real exit code, and the key-scan counts; the architecture sections relied on ("Determinism and the
substrate ladder", and the spine's arm page `docs/experiment-arms.md`, linked under "Explicit
cleanup experiments"); the decisions
(the three checkouts, which reconcile checkpoint pushes with one recording sha; the lab JSON's path;
the candidate sentence's page and wording; the audit date); and the limitations (hosted generation is not
byte-reproducible; the arms land together; the kill row has no power at this size; fake and lab rows
establish mechanics, not reasoning quality).
