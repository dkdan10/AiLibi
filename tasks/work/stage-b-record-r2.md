# B5 round 2: the balance round

**Status:** ready

## Outcome

Candidate round 1 read every conformance cell at 0 and the vent exit and the one reply effective, but
impostors won 34 of its 50 games, above the pre-registered 0.60 envelope. The owner adopted the seven
non-balance arms and ordered a balance round. The orchestrator's application of that ruling (the
decision memo's section 7) keeps the vent exit, `look_and_wait`, and sets exactly one dial. This card
records one 50-seed round that differs from round 1 in exactly that setting, the impostor kill
cooldown, raised from the map's 4 ticks to 6, and assesses it against readings committed before the
first seed.

After this card:
- `replays/candidates/stage-b-r2/9p2i/` holds seeds 0-49 of the 9-player sample roster (9 players, 2
  impostors, 2 tasks per crewmate), recorded on featherless `Qwen/Qwen3.6-27B` with the prompt set
  `qwen3_6_27b`, the bare substrate slate and one declared config: round 1's eight fields plus
  `kill_cooldown_ticks = 6`. Every tick row carries it; the round README carries its sha256.
- `audits/audit-<YYYY-MM-DD>-stage-b-r2.md` opens with a pre-registration pushed before the first seed,
  then the spend, gates and events, and the assessment in three columns, s9 at baseline 9, round 1 and
  round 2, never pooled; then the step the round-3 rule names, and a decision menu.
- Round 1 stays in the tree byte for byte. Nothing publishes, the ladder tip stays at baseline 9, and
  the round adopts nothing. The next step and the merge are the owner's.

This card records and reports; it changes no code, template or instrument, and its one test edit is the
golden's pin row for the new set. It is round 2's second card (memo section 7), after `kill-cooldown-arm`.

## Evidence

Sources: the decision memo `tasks/decision-2026-09-24-stage-b-wave.md`, sections 1, 3.2, 3.3, 4 and 7;
the direction addendum of 2026-10-01 (`tasks/direction-2026-09-19-process-over-outcome.md`, section
12); `docs/experiment-arms.md`, "Adopted arms" and "One engine-arguments helper". Memo section 7, the
addendum and "Adopted arms" landed in `6acdac92`, the adoption `docs:` commit on `main`. Also
`audits/audit-2026-09-27-stage-b-r1.md`, sections 1 (pre-registration; stop rules in 1.5, readings in
1.6, readings command in 1.8), 4 (amended ceilings 4.2, pause 4.3), 5.2 (batches) and 6 (assessment);
and `tasks/work/stage-b-record-r1.md` and its Results. Every `path:line` is at `6acdac92`, whose code is
`cd1a8454`'s, re-anchored by symbol at dispatch; every count comes from the tree, that audit or the memo
and is re-measured at dispatch.

**The owner's rulings, verbatim and dated:**
- 2026-09-24, the 50-seed record ruling (memo 0.1; round 1's audit quotes it in 1.1): "Let's not
  re-record all 300 seeds each time. When it's time to record, record the smaller group of 50 seeds,
  assess if the implementations have been effective and resulted in desired results. Also it is
  understood that updating the vent and body reset logic will probably have a substantial effect on
  previous limits and statistics around the baseline voting results, that is okay."
- 2026-09-27, round 1's ceilings: "Confirm the ceilings, v1 and the envelope as proposed"
- 2026-09-28, the wall: "Raise the wall to 12h in an 18h window and resume. Make sure it allows for a
  pause."
- 2026-10-01, round 2: "Merge.  Adopt all 7 non-balance arms. And run a balance round"

**What adoption means.** Memo section 7 adopts the seven arms in the sense the direction addendum
defines, verbatim: "(declared ON in every later round; defaults untouched; the shown set moves by the
era-keyed promotion once a round sits inside the envelope)". The direction addendum of 2026-10-01 adds
that "the project's documents describe them as the current game". A missing key keeps its historical
meaning, so the baseline-9 sets and round 1 keep verifying.

**The orchestrator's application, in memo section 7** (not the owner's words): `look_and_wait` stays;
round 2 is a balance round with "exactly one dial, a recorded kill-cooldown override field on the
engine layer, first value 6 ticks against the map's 4, with a pre-registered round-3 rule (win share
above 0.60 at 6 names 8; below 0.20 names 5), the same eight arms, the same amended ceilings, the same
pause mechanism, and its own candidate directory". Both round-2 cards carry the whole rule as this one
sentence, verbatim:

> **The round-3 rule.** On round 2's point share of impostor wins: above 0.60 at 6 it names round 3
> at `kill_cooldown_ticks = 8`; below 0.20 it names round 3 at `kill_cooldown_ticks = 5`;
> otherwise, with no envelope flag and every Conf. cell at 0, it names the era-keyed promotion of
> round 2 for the owner to decide, else no step.

Memo 7 states the first two branches. The third reads memo 7's adoption meaning: the promotion comes
once a round sits inside the envelope, and the envelope also flags reporter ejections above 0.104 per
report meeting (memo section 4; round 1's audit, 1.6). No ruling confirms that branch yet, so the owner
confirms the rule before the first seed (Constraints, Stop and ask).

**Round 1, the comparison base** (audit sections 5 and 6), recorded at its P, `f1133de5`: 50 seeds,
124 meetings, tally `1556 9344346 433660 0.0` (reproduced at `cd1a8454`); with the seed-31 husk, 1,586
calls, 9,508,803 input, 441,535 output and 12,776 s (3.55 h) of recording wall, $0. Impostor win share
34/50 = 0.68 (Wilson 0.54-0.79); s9's is 11/50 = 0.22.

**The dial today.**
- The map sets `kill_cooldown_ticks: 4` (`engine/maps/canonical_1.yaml:34`), refused below 1
  (`engine/world.py:284-285`). Three writers set an impostor's cooldown to it: the seeder
  (`orchestrator/seeder.py:111-113`), the engine after each kill (`engine/tick.py:413`) and the regroup
  at each meeting close (`engine/meeting_reset.py:36-40`).
- A kill needs cooldown 0 (`engine/rules.py:86-87`); cooldowns decrement after each play tick's actions
  (`engine/tick.py:687`). With cooldown K, kills after a regroup at meeting tick T are illegal at T+1 to
  T+K: T+1 to T+4 at 4 (memo 0.4), T+1 to T+6 at 6.
- The census's grace-window cell counts `kill.tick - meeting.tick <= inputs.kill_cooldown_ticks`
  (`eval/gameplay_census.py:1929`), read from the loaded map (`:2793`); the census refuses to fold sets
  walked at different cooldowns (`:3141-3143`).
- The kill-cooldown card adds the field (an integer; default None, the map's value; engine layer;
  omitted at its default), threads it to the three writers and every re-simulation site, and makes the
  census read it for the grace window. It also adds the conformance cell
  `kill_cooldowns_differing_from_recorded` ("Kill cooldowns that differ from the recorded value") and
  the table `kill_cooldown_writes_by_writer`, whose rows `round_start`, `after_kill` and `regroup`
  split the cell's denominator by writer. The readings command below reads both keys by those names.
- Two census cells this card reports already exist: kills are the denominator of `kills_seen_by_crew`
  (all kills; s9 175, round 1 227), and impostors able to kill when a meeting opened are
  `impostor_cooldown_zero_at_open` (s9 63/210, round 1 84/203), measured at `6acdac92` by the census
  `--set-dir ... --json-stdout` mode.

**The declared config**, one line plus a newline, 316 bytes: round 1's 290-byte file with
`, "kill_cooldown_ticks": 6` inserted before the closing brace.
`{"format_version": 1, "meeting_reset": "hub_with_grace", "vent_exit_policy": "look_and_wait", "vent_entry_policy": "own_fresh_kill", "vent_witness_rule": "physical", "bounded_rebuttal_version": 1, "report_body_handle_version": 1, "ballot_kill_row_version": 1, "impostor_ballot_version": 1, "kill_cooldown_ticks": 6}`.
At those bytes `shasum -a 256` prints `0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b`;
recompute it at pre-registration (round 1's prints
`4f0c4dd4779cd38f69194b6735221d86bf7c6944fe12769a3971e38e4e46d6c7`). The served stamps are round 1's:
the three `.v6` stamps and
`vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1`.

**The spend anchor** (audit 1.4): the s9 leg, 145 meetings, 1,694 calls, 9,850,930 input, 422,941
output, 8,695 s, $0. Round 1 used 56.6%, 54.3%, 58.9% and 29.6% of the call, input, output and wall
ceilings (audit 5.4); the 90% stops leave 1.59x its calls (2,520 / 1,586), 1.66x its input, 1.53x its
output and 3.04x its wall, so if longer games come, output is the first stop they meet.

**Hazards.**
- The recorder reads `HEAD` once per run into every MANIFEST `git_sha`
  (`scripts/refresh_samples.sh:753`), re-records any seed it is given (audit 2.6), refuses the fake
  provider under `replays/` (`:675-697`) and stages seeds beside the set directory (`:796`), where
  `_replays_tree_restored` (`tests/scripts/test_refresh_samples.py:1193-1219`) deletes new paths.
- Round 1's probe, seed 0 alone on one worker, projected 838 s x 50 = 11.64 h against a two-worker leg
  that took 3.55 h in all (audit 3.3, 5.4). Re-projected by audit 1.4's rule after the probe, a seed 0
  that slow crosses the 10.8 h stop again, though the round would not.
- The golden pins its retired-guard count per set path and raises for an unpinned set
  (`_RETIRED_GUARD_PINS`, `tests/meetings/test_prompt_byte_golden.py:1358-1371`); round 1's Results:
  "A later round's card adds its row, measured through the production walk".

## Acceptance

Each item names its enforcing mechanism and the planted or perturbed case that proves it bites. `F` is
`main` after `kill-cooldown-arm` merges. `P` is the pre-registration `coordination:` commit on
`work/stage-b-record-r2`; its tree differs from `F`'s only in the audit, its `audits/README.md` row and
the `audits/` row of `docs/artifacts.md`. `C` is `replays/candidates/stage-b-r2/9p2i`, `R1` is
`replays/candidates/stage-b-r1/9p2i`, `CFG` is `replays/candidates/stage-b-r2/experiment-config.json`.

- [ ] **The authorization and the pre-registration precede the first seed, and neither is rewritten.**
  Mechanism: no provider call is made until P is pushed. P's section holds the rulings above (verbatim,
  dated), memo section 7's adoption meaning and application, the owner's confirmation of the round-3
  rule (verbatim and dated, with any probe amendment; Constraints, Stop and ask), the config bytes and
  sha256, the ceilings, stop rules and discipline under Constraints, the table and round-3 rule below,
  and the round-2 readings command whole, as Validation states it. The
  config is not committed at P (a round directory without its set directory fails the candidate test);
  the delivery commit adds it with P's sha256. Until then each checkout holds an untracked copy at
  `CFG`, checked by `shasum -a 256` before the dry run and every gate (a mismatch stops the card), and
  no pytest or `check.sh` runs beside that copy. `git merge-base --is-ancestor F P` and
  `git merge-base --is-ancestor P <the MANIFEST's one git_sha>` exit 0, and the section at P equals the
  PR head's (a correction is a dated addendum). Proof: the second command with the PR head in place of
  P exits 1; a one-character edit to a reading, in a scratch copy, makes the comparison print a diff.
- [ ] **Both before columns are computed, never typed.** Mechanism: at `F`, the census and scorecard
  `--set-dir replays/samples/9p2i --json-stdout` modes, which write nothing, equal the s9 entries of
  `docs/gameplay-census.json` and `docs/process-scorecard.json` leaf for leaf. On `R1`, the same modes
  and `measure_baseline.py R1 --honesty --json`, through the readings command, print every count audit
  section 6 states; Results gives the counts compared and differing (0), and a moved round-1 count (a
  reader changed under its bytes) stops the card. Proof: each comparison against a copy with one cell
  edited prints that cell.
- [ ] **The readings are pre-registered in three columns.** Mechanism: the round-2 readings command
  (Validation), quoted whole at P, computes every reading from the named source keys in the table, and
  with `--after` exits 1 on a Conf. miss, an empty cooldown writer included. Round 2's rules are round
  1's verbatim (audit 1.6), plus the cooldown cell, the balance row's two keys and the round-3 rule; the
  envelope line no longer names the status-quo fallback for the vent exit, which memo 7 keeps. "Conf."
  cells must read exactly as built; a miss is a code defect that stops the round. "Reported" cells
  carry no rule. Rates carry Wilson 95% intervals; no column is pooled with another. The round-1 column
  is audit section 6's after column, re-measured at `6acdac92` (the balance row's two cells included).
  The table sits in P's section, so the first item's proof covers it. Proof, at `F` on scratch copies
  of the round-1 census section: the command run with `--after --round-3-rule` exits 0 and names round
  3 at 8 on round 1's 34/50; with the cooldown table's `regroup` row emptied it exits 1, naming that
  writer; with one Conf. numerator raised it exits 1, naming that key; with the win share set to 20/50
  it names the promotion, and with the reporter rate also set above 0.104 it names no step.

  | arm | cell | s9 at baseline 9 | round 1 | round 2 reading |
  |---|---|---|---|---|
  | physical witness | exits seen only from the room left; vent-band ejections resting only on them | 9/85; 8/70 | 0/72; 0/24 | Conf. 0; 0 |
  | look and wait | surfacings before the cap with a non-teammate in the inferred-visible set; trips over the cap | 52/85; 0/0 | 0/72; 0/63 | Conf. 0; 0 |
  | look and wait | exits seen from the exit room | 53/85 = 0.624 (0.52-0.72) | 8/72 = 0.111 (0.06-0.20), effective | effective at 0.30 or below; not effective at 0.52 or above, naming the hidden-travel escalation; partial between; n/a with no vent exit |
  | look and wait | forced exits; ticks inside per trip; in-place surfacings a crewmate reaches; kills within 2 ticks of a surfacing | 0/0; 85 at 1 tick; 0/0; 3/175 | 13/72; 1 tick 51, 2 ticks 6, 3 ticks 2, 4 ticks 13; 2/37; 0/227 | reported |
  | own fresh kill | entries not after the impostor's own fresh kill | 13/105 | 0/142 | Conf. 0 |
  | full reset | stale reports; corpses older than the last regroup; play resumes with a vented impostor; with a corpse; kills in the grace window after a regroup | 43/135; 0/0; 10/107; 60/107; 0/0 | 0/118; 0/68; 0/110; 0/110; 0/139 (T+1 to T+4) | Conf. 0 each; at cooldown 6 the window is T+1 to T+6 |
  | full reset | false resume perceptions; regroup notice present | n/a | not carried | Conf. 0; present every time; not carried, resting on mechanism and the golden |
  | full reset | skipped report meetings; meetings per game; trips closed by a regroup; kill-witness button calls within 6 ticks of a regroup; dropped trigger-tick events; meetings opening with an impostor in a vent | 55/135; 2.90; n/a; n/a; n/a; 29/145 | 70/118; 2.48; 46/142; 0/6; Moved 51, TaskProgressed 26, TaskCompleted 6; 66/124 | reported |
  | one reply | rebuttals the selector would not have chosen; meetings with a second repeat-speaker turn | 0/0; 0/145 | 0/121; 0/124 | Conf. 0; 0 |
  | one reply | opener rebuttals answering the charged tick; rebuttals that only redirect | n/a (accused openers answered 0/125); n/a | 19/19 (82 not evaluable); 17/121; effective | effective if half or more answer; not effective below 0.2, or if redirect-only reaches half; partial otherwise; conflicting if both hold; n/a with none evaluable |
  | one reply | accused openers answering; beneficiaries; rebuttals with an alibi, a whereabouts claim, a sighting; accusations against earlier speakers; ballots citing a rebuttal | 0/125; none; n/a; n/a; not carried | 101/112; 71, 30, 17, 3; 104/121, 104/121, 91/121; 121/121; not carried | reported |
  | body handle | report openings carrying the kill-tick handle | 135/135 | 0/118 | Conf. 0 |
  | kill row | own-kill rows naming a teammate or held by a non-witness | 0/0 | 0/4 | Conf. 0 |
  | kill row | own-kill rows served; cited by their holder; honesty cell 5 | 0; n/a; 4 holders, 3 of 4 citing | 4, present; 3 of 4; 4 holders, 3 of 4 | presence only: present when one or more is served |
  | impostor ballot | recorded teammate targets; the gate's betrayal check | 0/210; 0 | 0/203; 0 of 717 | Conf. 0; 0 |
  | impostor ballot | EJECTs whose only citation is a neutral row (honesty cell 3) | 1/46 | 0/107, the wording holds | holds at 0.10 or below; does not bind above 0.25; between otherwise; n/a with no impostor EJECT |
  | impostor ballot | EJECT share; labelled supported; authored teammate targets; ejections only impostors carried; `none_held` SKIPs | 46/210; 44/46; 1/210; 0/90; 95/164 | 107/203; 107/107; 16/203; 0/54; not carried | reported |
  | self-report off | impostor openers | 0/145 | 0/124 | Conf. 0 |
  | kill cooldown | kill cooldowns that differ from the recorded value (`kill_cooldowns_differing_from_recorded`), with writes by writer at round start, after a kill and at a regroup (table `kill_cooldown_writes_by_writer`) | measured at P; expected 0 against 4, regroup row empty | measured at P; expected 0 against 4 | Conf. 0 against 6, with a non-empty count at each of the three writers |
  | envelope | impostor win share (`impostor_wins`) | 11/50 = 0.22 (0.13-0.35) | 34/50 = 0.68 (0.54-0.79), flagged above 0.60 | non-gating; flagged outside 0.20-0.60; the round-3 rule, below, names the step |
  | envelope | innocent ejections; reporters ejected per report meeting; role-correct ejections; meetings with vent proof; scorecard rows 1-9 | 9 of 90; 7/135; 81/90; 70/145; as published | 15 of 54; 11/118; 39/54; 26/124; audit 6.1 | non-gating; reporter ejections above 0.104 per report meeting are flagged |
  | balance | kills (`kills_seen_by_crew`'s denominator); impostors able to kill when a meeting opened (`impostor_cooldown_zero_at_open`); the win split (`impostor_wins`) | 175; 63/210; 39 crew, 11 impostor | 227; 84/203; 16 crew, 34 impostor | reported |

  > **The round-3 rule.** On round 2's point share of impostor wins: above 0.60 at 6 it names round 3
  > at `kill_cooldown_ticks = 8`; below 0.20 it names round 3 at `kill_cooldown_ticks = 5`;
  > otherwise, with no envelope flag and every Conf. cell at 0, it names the era-keyed promotion of
  > round 2 for the owner to decide, else no step.

  The rule names a step and gates no acceptance item; the win share it reads gates nothing, as the
  whole envelope gates nothing. The next card, its spend and any promotion are the owner's. Round 1's
  readings stand (`docs/workflow.md`: a later experiment never changes an earlier verdict), and one key
  separates the rounds, so their difference is the dial's, within hosted-generation noise.
- [ ] **The preflight holds at `F`.** Mechanism: `git grep -n WAVE_ARMS_PENDING -- '*.py'` prints
  nothing. The declared file, read by `scripts/_declared_experiment.py`'s loader, validates as a
  `RecordedExperimentConfig` whose non-default fields are exactly round 1's eight and
  `kill_cooldown_ticks`. `FIELD_LAYER` assigns it `engine`, `OMITTED_AT_DEFAULT` holds it, and
  `engine_arguments` returns on the declared config instead of raising its unthreaded-field refusal.
  `prompt_versions_for_set("qwen3_6_27b", experiment_config=...)` returns round 1's four stamps. Proof:
  an unknown key is refused (`extra_forbidden`); without the cooldown key the non-default fields are
  round 1's eight; the kill-cooldown card's refusals of an unthreaded or invalid cooldown pass at `F`,
  named by test id in Results.
- [ ] **The fake dress rehearsal passes every instrument at `F`, at $0.** Mechanism: seeds 0-49 record
  with `AILIBI_LLM_PROVIDER=fake` on the declared config into a scratch directory outside `replays/`.
  Each of these exits 0 on it: the census `--set-dir` (every Conf. cell 0, the cooldown cell counted at
  all three writers); the scorecard `--set-dir`; the validity gate with `--expected-experiment-config`,
  `--expected-seeds 0-49` and `--require-one-recording-sha`; `verify_samples.sh <dir>`; the golden's
  directory walk; `measure_baseline.py <dir> --honesty`; and `scan_recording_packets.py <dir>`. Proof:
  gated against round 1's config, the gate exits 1 on `cost_and_provenance_exact`; the kill-cooldown
  card's planted breach at each writer passes.
- [ ] **The scripted rehearsal and the lab still hold at `F`.** Mechanism: round 1's scripted and
  ballot-arm cases pass (audit 2.4), and a scratch scripted game recorded from the declared file passes
  the loader, the census and scorecard `--set-dir`, the gate and the golden, each rebuttal counted once.
  The lab on the development split with round 1's ten arms (audit 2.5), plus any dial arm (mechanical
  only), writes a scratch file whose ten rows equal `audits/tactical-gameplay/stage-b-r1-frozen-head.json`
  field for field, or the card stops. Proof: dropping the evidence profile leaves the rebuttal call
  unconsumed; the lab comparison against a copy with one counter edited prints that counter.
- [ ] **The dry run and the probe pass before any batch queues.** Mechanism: the dry run echoes P's
  sha256, the nine fields and the bare slate, and `git status --porcelain` with untracked files hidden
  stays at 0 lines. The probe is the two-seed probe the orchestrator ruled on 2026-10-01 (Constraints,
  Stop and ask): seeds 0-1 record as one leg on the leg's two workers, and the gate with the declared
  config (`--expected-seeds 0-1`), `verify_samples.sh`, the golden's walk, the census conformance
  cells, the scorecard fold, `measure_baseline.py --honesty` (a raise is a STOP) and
  `scan_recording_packets.py` then run on it before the batches queue. Seeds 0-1 with no meeting or no
  fired rebuttal extend the probe by a leg naming seeds 2-3 only; seeds 0-3 with a meeting but no
  rebuttal stop the card. P's section records the ruling, dated, with both batch lists. Proof: the dry
  run with a stray `AILIBI_BOUNDED_REBUTTAL=1` exits 1.
- [ ] **The round is exactly the declaration.** Mechanism: `scripts/validity_gate.py` on `C` passes all
  ten checks, named individually, with `--expected-model Qwen/Qwen3.6-27B --require-zero-cost`, the four
  `--expected-prompt-versions` pairs, `--expected-experiment-config CFG`, `--expected-seeds 0-49` and
  `--require-one-recording-sha`. The MANIFEST's flags column equals s9's, its policy column reads
  `fsm-default`, `grep -l deadline_default` counts 0, and the candidate test passes in `check.sh`.
  Proof: the gate with `--expected-seeds 0-50` fails, and `R1` against `CFG` fails
  `cost_and_provenance_exact`.
- [ ] **Every conformance cell reads 0 on the round, the cooldown cell included.** Mechanism: the census
  `--set-dir` exits 0 on `C`; on a breach it exits non-zero, naming (set, seed, meeting). The cooldown
  cell counts all three writers, and the grace window runs to T+6. The golden, which `check.sh` runs on
  every candidate directory, reproduces every call. Proof: at `F`, the census card's planted breach per
  Conf. cell and the kill-cooldown card's planted breaches (a writer left at the map's value; a kill at
  T+5 after a regroup) pass; Results names them by test id.
- [ ] **The spend stays inside the ceilings.** Mechanism: the tally (Validation) counts `C`'s
  `llm_calls` rows, and `reproject.py` (Validation, quoted whole at P) applies Constraints'
  re-projection, printing each figure against its 90% stop and exiting 1 with a STOP line on one past
  it. Proof: the tally prints `1694 9850930 422941 0.0` on `replays/samples/9p2i` and
  `1556 9344346 433660 0.0` on `R1`, the anchors' own figures. `reproject.py` on a scratch copy of
  `R1`'s seeds 0-10 with round 1's 3,633 s prints round 1's own 10-seed figures (audit 5.4: 1,551
  calls, 9,325,616 input, 433,102 output, 16,514 s) and exits 0. Planted: the same copy with 60,000
  output tokens added to one call projects 678,541 output, past the 675,000 stop, and exits 1 on
  output; the unedited copy with 9,000 s of wall projects 11.36 h and exits 1 on wall. Results quotes
  all three runs.
- [ ] **The recording checkout never moves, a pause strands nothing, and no key leaves.** Mechanism:
  seeds record in a checkout detached at P in the batches under Constraints, a pause file is checked
  before each, and each ends in gates, a count-only key scan (gzip decompressed) and a pushed `record:`
  checkpoint; a resumed leg names only seeds not on disk. Proof: the MANIFEST names one `git_sha`, P's;
  each scan pattern fires once on a planted key; with a planted pause file and the recorder replaced
  by `true`, the loop starts no batch and logs the next one.
- [ ] **The freeze held.** Mechanism: `git log --oneline F..HEAD` and `F..origin/main` print nothing
  over `engine agents meetings observation orchestrator eval api scripts llm` at the PR head. Proof: the
  same pathspec over `f937dfaa..F` is non-empty (the kill-cooldown card's commits).
- [ ] **The derived views and the registration are rebuilt, never hand-edited.** Mechanism: the
  recorder's post-step writes the report through `eval/report_io.py`, and `build_sample_report.py
  --sample-dir C --check` passes. The round README's `candidate-declaration` block holds the sha256 line
  and `9p2i seeds 0-49`. The `replays/candidates/` and `audits/` rows of `docs/artifacts.md` are
  re-derived with `git ls-files` (111 files with both rounds: the README, two round READMEs, two
  configs, 106 set files), and offline `verify_ml_evidence.py` reads both as OK. The golden's pin row
  for `candidates/stage-b-r2/9p2i` is what its production walk measures on `C`. Proof: the plumbing
  card's planted round perturbations pass; without the new row the golden raises `KeyError`.
- [ ] **The assessment is written as pre-registered.** Mechanism: round 2's column comes only from the
  census and scorecard `--set-dir C --json-stdout`, `measure_baseline.py C --honesty --json` (ballot
  cells 3 and 5) and the gate's betrayal check, through P's readings command. The order: process cells;
  each arm's Conf. cells and reading; the cooldown cell; the envelope and the step the round-3 rule
  names, which gates nothing; role-correct ejection, the balance row and the win split, gating nothing.
  The decision menu: the step the rule names; round 1's options for `look_and_wait` alone (adopt,
  iterate, escalate, fall back); Conf. cells only for the seven adopted arms. If the step is the
  promotion, the menu lists the promoting card's follow-ups this round adds to memo 1's adoption list:
  a public-results label for the kill cooldown (`frontend/src/components/PublicResults.tsx` names each
  recorded experiment and has no words for it, so a group set apart only by its cooldown reads as
  having no enabled experiment). Proof: pooling `C` with s9 or `R1` through the census raises its
  refusal.
- [ ] **Nothing publishes, and nothing committed moves.** Mechanism: `git diff --stat F..HEAD` is empty
  over the committed sets, `R1`'s round directory, `tests/fixtures`, `training`, `api`, `frontend` and
  the scorecard and census docs. `verify_samples.sh` and `build_sample_report.py --check` pass once per
  set directory on the four sets, `R1` and `C`. The scorecard and census `--check` and
  `check_doc_facts.py` (`_LADDER_TIP_AUDIT` unchanged) exit 0, and the demo bundle built at `F` and at
  the head is identical (`diff -r`, mtimes pinned as round 1 did). Proof:
  `test_audits_index_ladder_tip_drift_detected` and `test_unindexed_audit_detected` pass.
- [ ] **The copy this card adds is plain.** Mechanism: the round README, the candidate sentence and the
  index row's prose, each saved to a scratch file, pass `copy_problems` from
  `tests/scripts/test_candidate_sets.py` (task or audit identifiers and threshold arithmetic) with 0
  problems, and a count-only scan for the wave's own identifiers, `\b[AB][0-9]\b|\bR[0-9]+\b`, prints
  0. They name switches by field and in plain words. Proof: a scratch copy with "6/7" inserted gives
  `copy_problems` one problem, and one with "R7" inserted makes the scan print 1.

## Constraints

**The partial-record principle binds this card.**
- Only `C` is recorded; the recorder refuses a non-default config aimed at `replays/samples/` or
  `replays/ml_corpus/`. The declared config differs from round 1's in exactly one key: the seven adopted
  arms and `look_and_wait` keep their round-1 values. This card adds no field, lever or env switch.
- `kill_cooldown_ticks` is default-OFF and omitted from the payload at its default, so every committed
  recording, fixture and audit payload re-serializes byte-identically (the spine's committed-payload
  test, `tests/orchestrator/test_experiment_arms.py`). No `AILIBI_*` lever and no prompt bump.
  Role-correctness is reported and never gated.
- Round 1 stays (`replays/candidates/README.md` leaves that to the card landing the next round): it is
  the comparison column and keeps verifying. Retiring a superseded round is a later card.

**Ceilings: round 1's, as amended** (audit section 4.2, verbatim). The live-call authorization is the
owner's ruling of 2026-10-01 under them, as memo section 7 applies it.

| limit | ceiling | hard stop at 90% |
|---|---|---|
| model calls | **2,800** (unchanged) | 2,520 |
| input tokens | **17,500,000** (unchanged) | 15,750,000 |
| output tokens | **750,000** (unchanged) | 675,000 |
| recording wall | **12 h** summed over sittings, each sitting inside an **18 h** elapsed window (was 4.5 h inside 8 h) | **10.8 h** summed (was 4.05 h) |
| marginal cost | **$0.00** (unchanged) | any `cost_usd` other than 0.0000 |

The cost is marginal against the flat-rate Featherless subscription, already paid and not incurred by
this run. Recording wall is each leg's own "Refresh complete in" figure summed over sittings; time
between batches counts only against the sitting's window. No seed re-records outside the rules below.

**Re-projection**, audit 1.4's rule as 4.2 continues it, unchanged: after the probe, after 10 seeds
(the first checkpoint holding at least 10 seeds) and at every batch checkpoint, each count is (C's total
over the completed seeds / s9's total over the same seeds) x the s9 leg total, and the wall is the
summed recording wall / the completed seeds x 50, each compared with its 90% stop; a figure past its
stop at any of them stops the round. `reproject.py` (Validation) computes it. Beside each, for context
only, the same ratio against `R1`'s same seeds. A slow seed 0 can project past the wall stop by itself
(Hazards); that stop is reported as 1.5 says, and the owner's choices are round 1's (audit 3.4).

**Stop and report to the owner** (audit 1.5, with 4.2's 10.8 h in place of 4.05 h), with the partial
output and the last checkpoint, on:
- any `cost_usd` other than 0.0000, or a re-projection past 90% of a ceiling;
- a leg past 1.5x the probe's projected wall, or summed recording wall past 10.8 h, or a sitting past
  its 18 h window;
- a provider refusal that survives the 8-attempt budget, or a raise from `measure_baseline.py
  --honesty`;
- any conformance breach (a "Conf." cell of the table that does not read as built, the cooldown cell
  included). It is a code defect, not a result: the fix lands under a new arm value, and a fix to the
  cooldown writers lands as a new field, since a recorded `kill_cooldown_ticks` value's meaning is
  frozen (memo 0.3 item 6). The round re-records from seed 0 under a new declared config, with a dated
  addendum and the owner's clearance.

**Stalls and failed seeds** (audit 1.5). A stall is 45 minutes with no completed seed: kill the batch
and re-run it for the seeds not on disk, or relaunch a fresh operator from the last pushed checkpoint; a
seed on disk is never re-recorded to recover a stall. A `(deadline_default)` row marks a failed
recording: move its husk outside the repository (its spend counts, as round 1's did) and re-record that
seed alone at P, logging the cause as it happens. No seed re-records for any other reason.

**Operating discipline** (round 1's second sitting, audit 4.3 and 5.2).
- After the two-seed probe, batches of 5: `--seeds 2,3,4,5,6`, then 7-11, and so on to 42-46, then
  47-49. If the probe extended to seeds 0-3, the batches start at 4: 4-8, 9-13, and so on to 44-48,
  then 49. Each leg names only the seeds it must record, never `--full`; a probed seed is never
  re-recorded, and no seed on disk is named again (the recorder re-records any seed it is given, audit
  2.6). The operator log, the key file and any husk stay outside the repository.
- Before each batch the operator checks a pause file outside the repository. If it exists, no batch
  starts: the key file is deleted, the last checkpoint is pushed, and the log names the seed reached and
  the next batch. The next sitting opens a new 18 h window, copies the key again and resumes there.
- After each batch, in the delivery checkout and a bare shell: the probe gates with `--expected-seeds
  0-N`, the tally, the re-projection and the key scan, then a pushed `record:` checkpoint commit.

**Checkouts, shells and the key.** Recording: a fresh worktree detached at P (`uv sync --frozen`, no
`.env`) running only the recorder, with no pytest, `check.sh` or commit. Verification: a worktree at
`F`. Delivery: the `work/stage-b-record-r2` worktree. Every gate runs in a bare shell and first prints
its `AILIBI_*` count (0). The recording shell sets only round 1's slate (audit 2.6) with
`AILIBI_SAMPLE_DIR` and `AILIBI_MANIFEST` on `C`: featherless, `qwen3_6_27b`, `Qwen/Qwen3.6-27B`, the
9/2/2 roster, 2 workers and 8 attempts. `FEATHERLESS_API_KEY` is copied as audit 2.7 describes, never
printed, into a 0600 file outside every checkout, passed only by `uv run --env-file` and deleted at a
pause and after the last push. No rendered prompt or seed-band prefix is printed; censuses are
count-only.

**The freeze.** From the first seed to the merge, nothing merges into `engine/`, `agents/` (the prompt
set included), `meetings/`, `observation/`, `orchestrator/`, `eval/`, `api/`, `scripts/` or `llm/`. If
`main` moves there, stop and ask; otherwise merge `main` in and re-run every gate.

**Wave, order and ownership.** Starts after `kill-cooldown-arm` merges; merges after it, by the owner.
One writer per file: the kill-cooldown card owns the code, the census, every test for the field and the
field's row on `docs/experiment-arms.md`. This card owns `replays/candidates/stage-b-r2/**`, its audit
and index row, the two `docs/artifacts.md` rows it recomputes after merging `main`, its sentence on
`docs/experiment-arms.md` (after the arm card's edit), the one golden pin row and this card. Never
edited here: round 1's directory and audit, `scripts/verify_ml_evidence.py`,
`audits/tactical-gameplay/` and `tasks/README.md` (the orchestrator's).

**Delivery.** Branch `work/stage-b-record-r2`, one PR into `main`, merged or fast-forwarded, never
squashed; never amend a pushed commit; merge `main` in, never rebase. Each commit body, P included,
carries `Card: tasks/work/stage-b-record-r2.md` immediately followed by the exact line
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. The PR body fills every template section
and ends with the Claude Code attribution line; agents post no PR comments. The worker fills Results;
the orchestrator owns the Status line.

**What stays out:** round 3, other sets, the held-out band, ML, the tour, featured list and public
results, scorecard or census cells, watchability floors, adoption, promotion, graduation, retiring
round 1 and the impostor self-report revisit.

**Ruled by the orchestrator on 2026-10-01, under the owner's delegation, and reported to the owner the
same day.** P's section records both rulings, dated, verbatim:
- the round-3 rule as written above stands. Memo 7 states its first two branches; its third, the
  promotion branch, is the orchestrator's application of memo 7's adoption meaning: it NAMES the
  era-keyed promotion of round 2 as the shown set, and the promotion itself stays a separate card and a
  publication decision the owner takes at that time. An owner amendment before P changes the table, the
  rule sentence and `readings.py` with it, at P.
- the probe is the two-seed probe: seeds 0-1 as one leg on the leg's two workers, then 2-6, 7-11 and so
  on to 42-46, then 47-49; or, if seeds 0-1 hold no meeting or no fired rebuttal, an extension naming
  seeds 2-3 only, then 4-8, 9-13 and so on to 44-48, then 49. Reason: round 1's single seed 0 projected
  11.64 h by itself against a round that took 3.55 h, because one seed's wall carries the provider's
  latency of the moment and a one-worker figure for a two-worker leg; two seeds on the leg's own two
  workers give the wall projection a basis that matches how the leg runs. The re-projection rule itself
  is unchanged. If the owner overrules either ruling before P, P records the amendment instead.

**Stop and ask** also if the owner amends the ceilings or the dial's value before the first seed (P and
the config change with them); if at `F` the cooldown cell or its writer table is missing, or merged under
names other than those in Evidence; if a round-1 count moves or a gate needs a code change; if the
scripted helper cannot take the declared config; or if a test other than the golden pin turns red only
because a second round exists.

## Expected scope

- `replays/candidates/stage-b-r2/README.md` (plain copy: the eight switches carried from round 1, the
  one dial in plain words, the `candidate-declaration` block) and `experiment-config.json`.
- `replays/candidates/stage-b-r2/9p2i/`, written by the recorder: `replay-seed-0.jsonl` to
  `replay-seed-49.jsonl`, `MANIFEST.md`, `roster.json` and `tournament-eval-report.json.gz`.
- `audits/audit-<YYYY-MM-DD>-stage-b-r2.md`, dated the day P lands, and its row in `audits/README.md`
  under the Stage-B gameplay wave.
- `docs/artifacts.md`: the `replays/candidates/` row and the `audits/` row, re-derived.
- `docs/experiment-arms.md`: a "Candidate round 2" heading and one sentence:
  "`replays/candidates/stage-b-r2/9p2i` is candidate round 2, recorded with the adopted switches, the
  kept vent exit and a longer kill cooldown, as its README names; it adopts nothing and is not a
  canonical sample set."
- `tests/meetings/test_prompt_byte_golden.py`: one `_RETIRED_GUARD_PINS` row for
  `candidates/stage-b-r2/9p2i`, measured through the production walk. It is directly necessary: without
  it the golden raises on the new set and `check.sh` fails.
- This card's Results.

Not in scope: all other code, template, instrument and test files; `replays/samples/`, `replays/ml_corpus/`,
`replays/candidates/stage-b-r1/`, `tests/fixtures/`, `training/`; the scorecard and census docs,
`docs/architecture.md`, `docs/glossary.md`, `README.md`, the featured list, public results and floors.

## Record impact

**What moves:** the round (55 new tracked files, about 35 MB if it matches round 1), the audit and its
index row, two `docs/artifacts.md` rows, one candidate sentence, one golden pin row and this card.

**What stays unchanged:** every byte, MANIFEST and report under `replays/samples/*`,
`replays/ml_corpus/*` and `R1`; the scorecard and census docs (baseline 9); the tour, public results,
watchability floors and ladder tip; the corpus freeze and ML fits; `check_vote_correctness_provenance`
and the four-set doc-fact agreement (candidates sit outside `_RECORDED_SETS`); the five levers, the
prompt registry and every default. CI reads round 2 as it reads round 1: verify leg, golden, candidate
test and report rebuild.

**Publication:** none. `pages.yml` builds only from `replays/samples` and the featured list, this card
touches nothing under `api/` or `frontend/`, and the PR proves the bundle identical.

**Evaluation:** the audit reports cells, readings and the round-3 rule's named step, with no verdict;
the owner decides. A promotion is a later card lifting the recorder's refusal for `replays/samples/9p2i`.

## Validation

Every command runs in a bare shell unless it is the recording shell; quote each exit code as it came
back. The tally is round 1's card's Validation command, carried whole and unchanged; at `6acdac92` it
prints `1694 9850930 422941 0.0` on `replays/samples/9p2i` and `1556 9344346 433660 0.0` on `R1`.

```
# the tally (count-only)
uv run python -c 'import glob,json,sys
c=i=o=0; u=0.0
for p in glob.glob(sys.argv[1]+"/replay-seed-*.jsonl"):
  for r in map(json.loads,open(p)):
    for k in r.get("llm_calls") or []:
      c+=1; i+=k["input_tokens"]; o+=k["output_tokens"]; u+=k["cost_usd"]
print(c,i,o,u)' <set dir>
git grep -n WAVE_ARMS_PENDING -- '*.py'                         # nothing, at F
CFG=replays/candidates/stage-b-r2/experiment-config.json; C=replays/candidates/stage-b-r2/9p2i; R1=replays/candidates/stage-b-r1/9p2i
shasum -a 256 "$CFG"; git merge-base --is-ancestor F P          # equals P's; exit 0
# the recording checkout, detached at P, with the slate from Constraints set inline
bash scripts/refresh_samples.sh --full --expect-levers "" --experiment-config "$CFG" --dry-run
uv run --env-file "$KEYFILE" bash scripts/refresh_samples.sh --seeds 0 --expect-levers "" --experiment-config "$CFG"
# only if seed 0 holds no meeting or no fired rebuttal: the extension, seeds 1-3
uv run --env-file "$KEYFILE" bash scripts/refresh_samples.sh --seeds 1,2,3 --expect-levers "" --experiment-config "$CFG"
test -e "$PAUSEFILE" || uv run --env-file "$KEYFILE" bash scripts/refresh_samples.sh \
  --seeds 1,2,3,4,5 --expect-levers "" --experiment-config "$CFG"   # then 6-10 ... 41-45, 46-49
# (after an extension: --seeds 4,5,6,7,8, then 9-13 ... 44-48, 49)
# gates, in the verification or delivery worktree
env | grep -c '^AILIBI_'                                        # 0
uv run python scripts/validity_gate.py "$C" --expected-model Qwen/Qwen3.6-27B --require-zero-cost \
  --expected-prompt-versions <the four KEY=VER pairs> --expected-experiment-config "$CFG" \
  --expected-seeds 0-49 --require-one-recording-sha
python3 "$SCRATCH/reproject.py" "$C" replays/samples/9p2i <summed recording wall, s>   # at each checkpoint
for d in replays/samples/9p2i "$R1" "$C"; do n=$(basename "$(dirname "$d")")
  uv run python scripts/publish_gameplay_census.py --set-dir "$d" --json-stdout > "$SCRATCH/census-$n.json"
  uv run python scripts/publish_process_scorecard.py --set-dir "$d" --json-stdout > "$SCRATCH/scorecard-$n.json"
  uv run python scripts/measure_baseline.py "$d" --honesty --json > "$SCRATCH/honesty-$n.json"; done
python3 "$SCRATCH/readings.py" "$SCRATCH/census-samples.json" "$SCRATCH/honesty-samples.json"          # s9 column
python3 "$SCRATCH/readings.py" "$SCRATCH/census-stage-b-r1.json" "$SCRATCH/honesty-stage-b-r1.json" --after   # round 1
python3 "$SCRATCH/readings.py" "$SCRATCH/census-stage-b-r2.json" "$SCRATCH/honesty-stage-b-r2.json" --after --round-3-rule
uv run python scripts/scan_recording_packets.py "$C"
bash scripts/verify_samples.sh                                  # both sample sets and both rounds
for d in replays/samples/9p2i replays/samples/4p1i replays/ml_corpus/9p2i replays/ml_corpus/4p1i "$R1" "$C"; do
  bash scripts/verify_samples.sh "$d"; uv run python scripts/build_sample_report.py --sample-dir "$d" --check; done
grep -l deadline_default "$C"/replay-seed-*.jsonl | wc -l       # 0
git merge-base --is-ancestor P "$(awk -F'|' '$2 ~ /^ *[0-9]+ *$/ {gsub(/ /,"",$8); print $8}' "$C/MANIFEST.md" | sort -u)"
git log --oneline F..HEAD -- engine agents meetings observation orchestrator eval api scripts llm          # empty
git log --oneline F..origin/main -- engine agents meetings observation orchestrator eval api scripts llm   # empty
git diff --stat F..HEAD -- replays/samples replays/ml_corpus replays/candidates/stage-b-r1 tests/fixtures \
  training api frontend docs/process-scorecard.md docs/process-scorecard.json docs/gameplay-census.md docs/gameplay-census.json  # empty
uv run python scripts/build_demo_bundle.py --out "$SCRATCH/bundle-head"   # and bundle-F at F; diff -r is empty
# the copy scan, over the README, the candidate sentence and the index row, each saved to scratch
uv run python -c 'import sys; sys.path[:0]=["scripts"]
from tests.scripts.test_candidate_sets import copy_problems
for p in sys.argv[1:]: print(p, len(copy_problems(open(p).read())))' <the three scratch files>
grep -cE '\b[AB][0-9]\b|\bR[0-9]+\b' <the three scratch files>  # 0 each
# the whole gate, in the delivery worktree, after the leg
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py                     # offline; never --complete
uv run pytest tests/meetings/test_prompt_byte_golden.py -k "retired_guard or stage-b-r2" -q
uv run pytest -m campaign -q                                    # the c9 refit pins' campaign half
bash scripts/check.sh; echo "check.sh exit $?"                  # whole, in a clean worktree
```

`readings.py` is round 2's readings command, quoted whole here and again at P (standard library only;
it prints counts and rates, never a prompt). It is round 1's (audit 1.8) with these changes: the
envelope line no longer names the status-quo fallback for the vent exit; the cooldown cell is read with
its writer table, and an empty writer is a Conf. miss; the balance row's kills and
`impostor_cooldown_zero_at_open` are printed; with `--after` a Conf. miss exits 1; and with
`--round-3-rule` the last line names the step the round-3 rule names, by the rule sentence above.

```python
"""Print round 2's pre-registered table from its named sources (count-only).

Usage: readings.py CENSUS.json HONESTY.json [--after] [--round-3-rule]

CENSUS.json is one census section: `publish_gameplay_census.py --set-dir DIR
--json-stdout`, or the s9 entry of docs/gameplay-census.json (the s9 column;
the two are equal cell for cell at F). HONESTY.json is
`measure_baseline.py DIR --honesty --json`. With --after, each reading is
computed by the pre-registered rule and the command exits 1 on a Conf. miss;
without it, values only. With --round-3-rule (after --after), the last line
names the step the round-3 rule names.
"""

import json
import math
import sys


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def rate(k, n):
    if n == 0:
        return f"{k}/{n} (n/a)"
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.3f} (Wilson {lo:.2f}-{hi:.2f})"


census = json.load(open(sys.argv[1]))
if "sets" in census:
    census = next(s for s in census["sets"] if s["label"] == "samples/9p2i")
honesty = json.load(open(sys.argv[2]))[0]["ballot_conduct"]
after = "--after" in sys.argv
cells = census["cells"]
tables = census["tables"]
misses = []
flags = []


def cell(key):
    c = cells[key]
    return c["numerator"], c["denominator"]


def show(label, key):
    k, n = cell(key)
    ne = cells[key]["not_evaluable"]
    extra = f"; {ne} not evaluable" if ne else ""
    print(f"  {label} [{key}]: {rate(k, n)}{extra}")
    return k, n


def conf(label, key):
    k, n = show(label, key)
    if after:
        print(f"    Conf.: {'reads 0 as built' if k == 0 else 'BREACH'}")
        if k != 0:
            misses.append(key)
    return k, n


print(f"games {census['games']}; meetings {census['meetings']}; "
      f"meetings per game {census['meetings'] / census['games']:.2f}")
print("physical witness")
conf("exits seen only from the room left", "vent_exits_seen_only_from_room_left")
conf("vent-band ejections resting only on them", "vent_band_resting_only_on_room_left")
print("look and wait")
conf("surfacings before the cap with someone in view", "surfacings_before_cap_in_view")
conf("trips over the cap", "trips_longer_than_cap")
show("  beside: exits into a room the impostor could see a crewmate in",
     "vent_exits_into_visibly_occupied_room")
k, n = show("exits seen from the exit room", "vent_exits_seen_from_exit_room")
if after:
    if n == 0:
        print("    reading: n/a (no vent exit)")
    else:
        share = k / n
        verdict = ("effective" if share <= 0.30 else
                   "not effective (names the hidden-travel escalation)" if share >= 0.52
                   else "partial")
        print(f"    reading: {verdict}")
show("forced exits", "forced_surfacings")
print(f"  ticks inside per surfaced trip [ticks_inside_per_trip]: "
      f"{json.dumps(tables['ticks_inside_per_trip']['counts'], sort_keys=True)}")
show("near-body cost: in-place surfacings a crewmate reaches", "in_place_surfacings_near_crew")
show("kills within 2 ticks of the killer's surfacing", "kills_soon_after_surfacing")
print("own fresh kill")
conf("entries not after the impostor's own fresh kill", "vent_entries_not_after_own_fresh_kill")
print("full reset")
conf("stale report meetings", "stale_report_meetings")
conf("reported corpses older than the last regroup", "report_corpses_older_than_last_close")
conf("play resumes with an impostor in a vent", "play_resumes_with_impostor_in_vent")
conf("play resumes with a corpse", "play_resumes_with_corpse")
conf("kills in the grace window after a regroup", "kills_in_grace_window_after_regroup")
show("  beside: kills within 2 ticks of any meeting", "post_meeting_kills_soon_after")
show("skipped report meetings", "skipped_report_meetings")
show("trips closed by a regroup", "trips_closed_by_regroup")
show("kill-witness button calls within 6 ticks of a regroup",
     "kill_witness_button_calls_soon_after_regroup")
print(f"  dropped trigger-tick events [trigger_tick_events_dropped_by_regroup]: "
      f"{json.dumps(tables['trigger_tick_events_dropped_by_regroup']['counts'], sort_keys=True)}")
show("meetings opening with an impostor in a vent", "meetings_opening_with_impostor_in_vent")
print("one reply")
conf("rebuttals the selector would not have chosen", "rebuttals_differing_from_selector")
conf("meetings with two repeat-speaker turns", "meetings_with_second_repeat_speaker")
show("an accused opener answers", "accused_opener_answers")
ka, na = show("opener rebuttals answering the charged tick",
              "opener_rebuttals_answering_charged_tick")
kr, nr = show("rebuttals that only redirect", "rebuttals_redirect_only")
if after:
    effective = na > 0 and ka / na >= 0.5
    not_effective = (na > 0 and ka / na < 0.2) or (nr > 0 and kr / nr >= 0.5)
    if na == 0 and not (nr > 0 and kr / nr >= 0.5):
        print("    reading: n/a (no evaluable opener rebuttal)")
    elif effective and not_effective:
        print("    reading: conflicting (an effective and a not-effective condition both hold)")
    elif effective:
        print("    reading: effective")
    elif not_effective:
        print("    reading: not effective")
    else:
        print("    reading: partial")
show("rebuttals carrying an alibi", "rebuttals_with_alibi")
show("rebuttals carrying a whereabouts claim", "rebuttals_with_whereabouts")
show("rebuttals carrying a sighting", "rebuttals_with_sighting")
show("rebuttal accusations against players who already spoke",
     "rebuttal_accusations_against_earlier_speakers")
print(f"  beneficiaries [rebuttal_beneficiaries]: "
      f"{json.dumps(tables['rebuttal_beneficiaries']['counts'], sort_keys=True)}")
print("body handle")
conf("report openings carrying the kill-tick handle", "report_openings_with_kill_tick_handle")
print("kill row")
conf("own-kill rows naming a teammate or held by a non-witness", "own_kill_rows_breaching")
served = cell("own_kill_rows_breaching")[1]
show("own-kill rows their holder cited", "own_kill_rows_cited_by_holder")
holders = honesty["kill_holders"]
citing = honesty["kill_holders_citing_the_kill"]
print(f"  honesty cell 5: kill holders {holders}; citing the kill "
      f"{rate(citing['numerator'], citing['denominator'])}")
if after:
    print(f"    presence: {'present' if served > 0 else 'absent'} ({served} rows served)")
print("impostor ballot")
conf("recorded teammate ballot targets", "recorded_teammate_ballot_targets")
neutral = honesty["ejects_citing_only_neutral"]
print(f"  honesty cell 3: impostor EJECTs citing only a neutral row "
      f"{rate(neutral['numerator'], neutral['denominator'])}")
if after:
    if neutral["denominator"] == 0:
        print("    reading: n/a (no impostor EJECT)")
    else:
        share = neutral["numerator"] / neutral["denominator"]
        verdict = ("the wording holds" if share <= 0.10 else
                   "it does not bind (a revision under a new value)" if share > 0.25
                   else "between the two readings")
        print(f"    reading: {verdict}")
show("impostor EJECT share", "impostor_eject_ballots")
show("impostor EJECTs labelled supported", "impostor_ejects_labelled_supported")
show("authored teammate targets", "authored_teammate_ballot_targets")
show("ejections whose floor only impostors met", "ejections_carried_only_by_impostor_ballots")
print("self-report off")
conf("impostor openers", "impostor_openers")
print("kill cooldown")
conf("kill cooldowns that differ from the recorded value",
     "kill_cooldowns_differing_from_recorded")
writes = tables["kill_cooldown_writes_by_writer"]["counts"]
print(f"  writes by writer [kill_cooldown_writes_by_writer]: "
      f"{json.dumps(writes, sort_keys=True)}")
if after:
    for writer in ("round_start", "after_kill", "regroup"):
        if writes.get(writer, 0) == 0:
            print(f"    Conf.: BREACH (no write counted at {writer})")
            misses.append(f"kill_cooldown_writes_by_writer.{writer}")
print("envelope (non-gating)")
k, n = show("impostor win share", "impostor_wins")
if after and n:
    share = k / n
    if share > 0.60 or share < 0.20:
        flags.append("win share")
    print(f"    envelope: {'flagged above 0.60' if share > 0.60 else 'flagged below 0.20' if share < 0.20 else 'inside 0.20-0.60'}")
rk, rn = cell("role_correct_ejections")
print(f"  innocent ejections: {rn - rk} of {rn} ejections")
reporters = tables["innocent_opener_ejections_by_trigger"]["counts"].get("report", 0)
report_meetings = tables["meetings_by_trigger"]["counts"].get("report", 0)
print(f"  reporters ejected per report meeting: {rate(reporters, report_meetings)}")
if after and report_meetings:
    per = reporters / report_meetings
    if per > 0.104:
        flags.append("reporter ejections")
    print(f"    envelope: {'flagged above 0.104' if per > 0.104 else 'at or below 0.104'}")
show("role-correct ejections (reported, gates nothing)", "role_correct_ejections")
show("meetings with vent proof", "meetings_with_vent_proof")
print("balance (reported, gates nothing)")
kills = cell("kills_seen_by_crew")[1]
print(f"  kills [kills_seen_by_crew, its denominator]: {kills}")
show("impostors able to kill when a meeting opened", "impostor_cooldown_zero_at_open")
print(f"  the win split [impostor_wins]: {n - k} crew, {k} impostor")
if after and "--round-3-rule" in sys.argv and n:
    share = k / n
    step = ("round 3 at kill_cooldown_ticks = 8" if share > 0.60 else
            "round 3 at kill_cooldown_ticks = 5" if share < 0.20 else
            "the era-keyed promotion of round 2, for the owner to decide"
            if not flags and not misses else "no step")
    print(f"round-3 rule: names {step}")
if misses:
    print(f"Conf. misses: {', '.join(misses)}")
    sys.exit(1)
```

`reproject.py` is Constraints' re-projection, quoted whole here and again at P (standard library only,
count-only). On a scratch copy of `R1`'s seeds 0-10 with 3,633 s it prints round 1's 10-seed figures
(1,551 calls, 9,325,616 input, 433,102 output, 16,514 s) and exits 0.

```python
"""Re-project the round's spend against the 90% stops (count-only).

Usage: reproject.py CAND_DIR S9_DIR SUMMED_WALL_SECONDS

Each count is (the candidate's total over its completed seeds / the s9 total
over the same seeds) x the s9 leg total; the wall is the summed recording wall
/ the completed seeds x 50. Exits 1 when any figure is past its stop.
"""

import glob
import json
import re
import sys

STOPS = {"calls": 2_520, "input": 15_750_000, "output": 675_000}
WALL_STOP = 38_880  # 10.8 h


def tally(directory):
    per_seed = {}
    for path in glob.glob(directory + "/replay-seed-*.jsonl"):
        seed = int(re.search(r"replay-seed-(\d+)\.jsonl$", path).group(1))
        calls = tokens_in = tokens_out = 0
        cost = 0.0
        for row in map(json.loads, open(path)):
            for call in row.get("llm_calls") or []:
                calls += 1
                tokens_in += call["input_tokens"]
                tokens_out += call["output_tokens"]
                cost += call["cost_usd"]
        per_seed[seed] = (calls, tokens_in, tokens_out, cost)
    return per_seed


cand = tally(sys.argv[1])
s9 = tally(sys.argv[2])
wall = float(sys.argv[3])
seeds = sorted(cand)
stops = []
print(f"completed seeds {len(seeds)} ({seeds[0]}-{seeds[-1]})")
for index, name in enumerate(("calls", "input", "output")):
    done = sum(cand[s][index] for s in seeds)
    base = sum(s9[s][index] for s in seeds)
    projected = done / base * sum(v[index] for v in s9.values())
    past = projected > STOPS[name]
    stops += [name] if past else []
    print(f"  {name}: {done} / {base} x s9 = {projected:,.0f} "
          f"({projected / STOPS[name]:.1%} of the {STOPS[name]:,} stop){' STOP' if past else ''}")
wall_projected = wall / len(seeds) * 50
past = wall_projected > WALL_STOP
stops += ["wall"] if past else []
print(f"  wall: {wall:,.0f} s / {len(seeds)} x 50 = {wall_projected:,.0f} s "
      f"= {wall_projected / 3600:.2f} h (stop 10.8 h){' STOP' if past else ''}")
nonzero = [s for s in seeds if cand[s][3] != 0.0]
if nonzero:
    stops.append("cost")
    print(f"  cost: non-zero on seeds {nonzero} STOP")
if stops:
    print(f"STOP: {', '.join(stops)}")
    sys.exit(1)
```

The pre-spend at `F` runs the fake rehearsal, the scripted cases, the lab, and the readings and
re-projection proofs on scratch targets; the section comparison diffs `git show P:<audit>`'s
pre-registration section against the head's.

## Results

Not started. The operator records, here and in the PR: P, `F` and each checkout; the pre-spend and the
round-1 comparison counts; the dry run, the probe and every batch with wall, spend and checkpoint; each
re-projection; every event, pause and Validation command with its real exit code; the architecture
sections relied on ("Determinism and the substrate ladder", `docs/experiment-arms.md`); the decisions
(the owner's answer on the round-3 rule and the probe, the golden pin row, keeping round 1, the audit
date); and the limitations (hosted generation is not byte-reproducible; 50 games; fake and lab rows
establish mechanics, not reasoning quality).
