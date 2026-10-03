# Diagnosis after Stage-B round 2: is the game in a good state, and does ML have a role?

**About this document.** Written on 2026-10-02 as a read-only synthesis of `main` at `d41c9006` (the merge of
PR #494, before round 2 was promoted), and prepared for the repository against `59bbd1be` with its three
investigator memos beside it. It is advisory: it diagnoses and recommends, it decides nothing, and every item in
Part 4 remains the owner's decision. Its recommendations are carried by the follow-up cards in `tasks/work/`:
`rubric-extractor-era.md`, `census-reporter-base-rate.md`, `route-check-replay.md` and
`post-promotion-follow-through.md`. Every path and `path:line` below is cited at `d41c9006`. Since then the
promotion (PR #495) moved round 2 into `replays/samples/9p2i`, so at later commits that path holds r2 rather than
s9, and `replays/candidates/stage-b-r2/9p2i` no longer exists. The investigators' and the synthesis's scratch
scripts named below were never committed.

Synthesis memo for the owner, 2026-10-02. Read-only on `main` at `d41c9006` (the merge of PR #494). No model call,
no recorder, no commit, no push, no edit to a tracked file, no `.env` read, 0 `AILIBI_*` exports in the shell. No
prompt and no model text is printed here. Every census is count-only and keyed by (set, meeting). Whether an
ejected player was really an impostor is reported to describe the games; it gates nothing, and nothing here feeds
back to any agent.

**Inputs.** The investigator memos [`gameplay-state.md`](gameplay-state.md) and [`ml-tactical.md`](ml-tactical.md)
in this folder, the three refuters' verdicts, and my own re-checks. The reporter-ejections investigator could not
write its memo (the harness refused the file), so its findings reached me as a structured summary, kept here as
[`reporter-ejections.md`](reporter-ejections.md); its scripts are in the session scratch directory
`reporter_ejections_scripts/` (not committed). I re-ran every count the refuters disputed. My scripts are in the
session scratch directory `synthesis-scripts/` (not committed), and the commands are in the appendix. Citations
are `path:line` at `d41c9006`; "audit r2" is
[`audits/audit-2026-10-01-stage-b-r2.md`](../../audits/audit-2026-10-01-stage-b-r2.md).

**Words used here, in plain terms.**

- **s9, r1, r2.** Three recordings of the same 50 games (seeds 0-49, 9 players, 2 impostors), never pooled.
  - s9 is baseline 9, the game shown today (`replays/samples/9p2i`).
  - r1 is round 1: the eight Stage-B rule changes (`replays/candidates/stage-b-r1/9p2i`).
  - r2 is round 2: the same rules plus a 6-tick kill cooldown instead of the map's 4
    (`replays/candidates/stage-b-r2/9p2i`). r1 and r2 differ in that one setting.
- **Report meeting, reporter.** A meeting opened because someone found a body; the reporter is whoever found it.
- **Vent proof.** A meeting where a living crewmate holds a game-checked sighting of a player using a vent. Only
  impostors vent, so this is near-certain evidence.
- **Innocent ejection.** A crewmate voted out.
- **Kill witness.** A crewmate the game records as having seen a kill happen.
- **Regroup.** The full reset at the end of every meeting in r1 and r2. Everyone moves to the Cafeteria, bodies are
  cleared, vents are emptied, kill cooldowns restart, and nobody can kill during a short grace window.
- **Conformance check.** A count that must read zero if a rule was built as specified (the audit's "Conf." cells).
- **Envelope.** Target ranges fixed before the round. Crossing one raises a flag, and flags gate nothing.
- **Counterfactual tally.** Re-counting the same recorded ballots after changing some of them, with the game's own
  counting function (`meetings/voting.py:192`). For example, every impostor ballot can be turned into a SKIP.
- **Tactical layer.** The hand-written rules that move every player between meetings: walking, tasks, kills,
  vents, sabotage, reports. No model runs there.
- **Play tick.** One step of the game between meetings.
- Numbers in brackets after a rate are its 95% range (Wilson interval).

---

## Part 1. The ten-minute version

### 1.1 The bottom line

- **Between meetings, round 2 plays like Among Us, and nothing there is broken.**
  - Every rule the wave added does what it was built to do: every carried conformance check reads 0.
  - Impostors win 24 of 50, inside the target range.
  - Games are longer, with a visible kill rhythm, and they end three different ways.
- **Meetings are honest and grounded, and decisive when someone holds proof.** Without proof, the table makes one
  recurring mistake: it votes out the innocent player who reported the body.
  - Usually the impostor accuses the reporter back, and the table misreads a route the map allows.
  - This is the reporter flag: 17 of 114 report meetings.
  - It is real, but it is mostly an old bias of the meeting table, not something round 2 created.
  - What pushed it over the line was a new, small group: crewmates who actually watched the kill and then were
    disbelieved.
- **Round 2 can be shown once the promotion carries some presentation work:** a regroup moment in the viewer, a
  kill-cooldown label, and a new featured strip.
  - The flag gates nothing, so promotion is your decision, and you have taken it ("Promote").
- **ML: keep it on hold.**
  - Stage B changed where a learned policy could matter between meetings.
  - It did not make ML ready, and it did not make ML necessary.
  - It cannot reach the open problem, which lives in the meetings.

### 1.2 Round 2 against your goals

| your goal | what round 2 shows | verdict |
|---|---|---|
| A vote or skip rests on data the agent holds, true or false | 407 of 410 eject votes cite a line the voter holds that is about the target. 580 of 580 checkable rationales use only facts the voter had. Crew statements of where they were are true in 628 of 632. Of 281 skips, 44 cite a line about a player the voter considered, 214 say the voter holds nothing that points anywhere, 6 cite something off-target, and 17 were not assessed (16 of them are impostor votes the game turned into skips) | **Holds.** The reporter ejections are wrong decisions on lines the voters held, which is the failure you said you prefer |
| Plays like the genre | The kill cooldown restarts after every meeting, bodies are cleared at meetings, a vent is risky only if someone walks in, the crew can win on tasks (13 games), and impostors stall near a task win with sabotage. Impostors never report bodies; that is a deliberate departure | **Mostly yes.** The one un-genre feature is that every reporter is innocent by construction |
| Solid, showable, finished | The engine and the rules are settled. The viewer and the public page need small follow-ups. 11 of 50 games qualify as a tour opener under the spectator card's measured criterion | **Close.** It needs the promotion follow-ups (Part 3, card 0) |
| ML on hold until gameplay settles | Nothing in Stage B lifts the hold's preconditions | **Unchanged** |

Sources: audit r2:1263, :1271 (eject grounding, rationale faithfulness);
`measure_baseline.py --honesty` (crew false 4 of 632); skip labels from `synthesis-scripts/skiplabels.py`, which
reads each ballot's recorded grounding label (the named instruments do not carry the "holds nothing" cell, audit
r2:1439-1441).

### 1.3 What is fine, what is a defect, what is a choice

**Fine; keep as is.**

- **Every rule change is built as specified.** Every carried conformance check reads 0, including the cooldown at
  all three places it is set: round start, after a kill, at a regroup (audit r2:1278, :1363-1371).
- **The game's shape.**
  - Games last 38.8 ticks on average (median 35), with 2.34 meetings each.
  - The crew win 13 by ejection and 13 by finishing tasks; the impostors win 24 by reaching parity (as many
    impostors as crew).
- **Vents.**
  - An impostor never surfaces into a room where it can see a crewmate: 0 of 72 exits.
  - All 8 seen exits and all 16 seen entries were crewmates walking in on the same tick.
  - Vent proof is always right: 24 of 24 impostors seen venting were ejected.
- **Bodies.** 0 stale reports, and the oldest body found was 11 ticks old.
- **Honest, grounded talk.** The numbers are in 1.2.
- **Balance.** Impostors win 24/50 = 0.48 (0.35-0.61), inside the 0.20-0.60 target.

**Defects. All are presentation or measurement, none is in the recording, and all belong with the promotion.**

- **The viewer has no regroup moment.** After each meeting all survivors appear in the Cafeteria and bodies vanish,
  with nothing on screen saying why. There is no regroup handling in `frontend/src`; this is inferred from the
  code, not watched in a running viewer.
- **The public results page has no kill-cooldown label.** It names every other Stage-B rule and still calls adopted
  rules "experimental" (`frontend/src/components/PublicResults.tsx:7-21`).
- **The 9-player featured strip is wrong on round-2 games.**
  - Its opener, seed 23 (`frontend/src/components/ReplayPicker.tsx:112`), fails the opener criterion.
  - Its labels count meetings that no longer happen.
- **Four pre-registered checks have no instrument** (audit r2:1439-1441):
  - false perceptions after a regroup;
  - the regroup notice;
  - ballots citing a reply;
  - skips labelled "holds nothing".
- **The census shows the reporter rate without its base rate.** Section 1.4 supplies one.

**A reasoning failure, not a code defect: the reporter trap (1.4).**

**Choices. Keep each, or revisit it deliberately.**

- **Impostors never report a body or press the button.** This is ruling R6; `self_report` is off, a tactical
  setting (`orchestrator/experiment_config.py:50`, `:224`).
  - So every reporter is innocent: 0 of 117 openers are impostors.
  - In Among Us an impostor sometimes reports its own kill, so suspecting the reporter is sometimes right. Here it
    never is.
- **The kill wave after a regroup.** 70 of 109 post-meeting kills land 7 to 10 ticks after the meeting. That is the
  genre's cooldown restarting after each meeting.
- **The button has nearly gone** (3 of 117 meetings). It was mostly an "I saw a vent" button, and seen vents are now
  rare.
- **Sabotage near a task win is a hand-written trigger.** There were 46 sabotages, one in every task win. The rule
  fires at 6 of 7 tasks done when no kill is available (`agents/tactical/impostor_policy.py:253`, `:437-450`), so
  it is not an emergent tactic. It never ends a game: the engine's fourth ending, the sabotage win
  (`engine/win_conditions.py:35`), fired 0 times.
- **How impostors talk and vote.**
  - The accused impostor's first reply is almost always a counter-accusation with no account of itself (89 of 91).
  - Impostors vote by strategy: 111 eject votes, all inside the wording (audit r2:1355).
  - The one reply can go to an impostor (28 of 117 meetings).

### 1.4 The reporter flag, read with its base rate

**The flag.** Innocent reporters were voted out in 17 of 114 report meetings, 0.149 (0.10-0.23). The line is 0.104,
twice baseline 9's 0.052 (audit r2:1379).

- r1 read 11 of 118 = 0.093 (0.05-0.16).
- The two ranges overlap. Each round is a single recording, so the crossing of the line is itself inside the
  noise between recordings.

**The base rate, per seat, at report meetings** (`baserate.py`):

| | s9 | r1 | r2 |
|---|---|---|---|
| the reporter is ejected | 7/135 = 0.052 | 11/118 = 0.093 | 17/114 = 0.149 |
| another innocent is ejected (per innocent seat) | 2/451 = 0.004 | 2/372 = 0.005 | 5/367 = 0.014 |
| an impostor is ejected (per impostor seat) | 71/194 = 0.366 | 35/194 = 0.180 | 41/195 = 0.210 |
| reporters' share of innocent ejections | 7 of 9 | 11 of 13 | 17 of 22 |
| reporters' share of innocent seats | 0.23 | 0.24 | 0.24 |

**What it says.**

1. **It is an old bias.** In every column the reporter takes about three quarters of innocent ejections while
   holding about a quarter of the innocent seats.
2. **It lives where proof is absent.** Every reporter ejection, in all three columns, happened at a meeting
   without vent proof. At those meetings, per seat:

   | | s9 | r1 | r2 |
   |---|---|---|---|
   | reporter ejected | 7/75 = 0.093 | 11/98 = 0.112 | 17/93 = 0.183 |
   | impostor ejected | 11/102 = 0.108 | 15/160 = 0.094 | 20/158 = 0.127 |

   In r2, at such a meeting, the reporter (always innocent) is more likely to be voted out than any given impostor.
3. **The loss of vent proof explains only part of the rise.**
   - s9's per-meeting rates, applied to r2's mix of meetings with and without vent proof, predict 0.076. So the
     shift away from vent proof explains about a quarter of the rise from 0.052 to 0.149.
   - From r1 to r2 the mix stayed flat: 98 of 118 report meetings without vent proof, then 93 of 114. So none of
     the crossing of the line is the mix.
4. **The crossing came from a new, small group: reporters who watched the kill.**

   | | s9 | r1 | r2 |
   |---|---|---|---|
   | report meetings where the reporter saw the kill | 3 | 3 | 14 |
   | reporter ejected at those meetings | 1 | 0 | 5 |
   | other reporters ejected | 6/132 | 11/115 | 12/100 |

   - The rise from r1 to r2 (11 to 17) is 5 witnesses plus 1 other reporter.
   - Every kill witness walked into the kill room on the kill tick: 3, 3 and 14 of them, in every column. They have
     to. An impostor kills only when alone with one crewmate, so a witness can only exist by arriving at that
     moment.
   - All 5 ejected witnesses had named the real killer in their opening.
   - Why witnesses rose from 4 of 227 kills (r1) to 14 of 195 (r2) is not established. Of the 14, 5 came before
     the first meeting and 9 after one.
5. **Who opens it, and who carries it.**
   - The first accusation against an ejected reporter came from an impostor in 9 of the 17. In 4 of the 5 witness
     cases it came from the killer itself, in the first reply.
   - Most eject votes are crew votes. A majority of the crew voted to eject in 12 of 17, and counting crew ballots
     alone still ejects the reporter in 13 of 17.
   - But if impostors had skipped, as they mostly did at baseline 9 before the strategic ballot, 10 of the 17
     would not have happened (s9: 3 of 7; r1: 7 of 11).
   - The strategic impostor ballot and the table's own reasoning arrived together, so neither can be credited
     alone.
6. **The mistake behind it.**
   - In the 5 witness cases, the table called a walk the map allows impossible (4 cases), or charged a move that was
     really the public regroup (1 case, seed 30 meeting 1).
   - How common this is across all 17 is not counted. A keyword stand-in finds a route argument in an accusing turn
     for 11 of 17 ejected reporters, but also for 12 of 44 ejected impostors, so a keyword is not a measurement.
   - Baseline 9 had the same mistake as the main cause in 15 of 42 innocent ejections (analysis memo, Q6).
   - The model has the map in every ballot (`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:279-284`). It is
     misapplying what it holds, not missing information (analysis memo:459).

**Reading.** The flag is a fair warning about a real, long-standing weakness of the meeting table. In r2 it is
sharpened by kill witnesses who are disbelieved. It is not a defect in the round's rules, and it does not break your
first goal: those votes rest on lines the voters held.

### 1.5 The ML verdict

**Keep tactical ML on hold** (ruling 12, `tasks/decision-2026-09-24-stage-b-wave.md:41`). Here is what Stage B
changed for the decisions made outside the model.

- **More games now end between meetings, but meetings still set up most endings.**
  - Games ending on a play tick: s9 12/50, r1 36/50, r2 35/50. In r2 that is 22 parity kills and 13 task wins.
  - 17 of the 22 parity endings came after a meeting had voted out a crewmate. 10 of the 13 task wins came after a
    meeting had voted out an impostor (s9: 4 of 11 and 1 of 1). So at least 27 of the 35 play-tick endings carry a
    meeting ejection that set up the end.
  - Meetings now remove fewer impostors (81, 39, 44) and more innocents (9, 15, 22).
- **A real task race now exists.** Crew task wins went 1, 4, 13. The race also exists on the fake-provider training
  path: crew finish tasks in 5 to 7 of 20 probe games, against 0 before. So a crew objective would no longer be
  trivial in training.
- **The hand-written rules now remove the vent giveaway that past training rewarded.** Exits seen from the exit
  room fell from 53/85 to 8/72.
- **They do not remove what past search actually found: kills in front of witnesses** ("N1",
  `docs/ml-program.md:105-123`).
  - Crew-witnessed kills rose 3/175, 4/227, 14/195 under the scripted rules, and no conformance check pins them.
  - Kills with two or more crew present stayed 0 in all three columns, as they were before Stage B.
- **The training stack cannot run this game.** That is new work, not a setting.
  - The training environment takes no recorded settings (`training/env.py:583`).
  - The game refuses its agents under the adopted tactical rules (`orchestrator/game.py:3195`, `:3217`).
  - The learned option menu cannot wait inside a vent (`training/bakeoff/utility_es.py:209`).
  - The meeting stand-ins refuse the new era (`training/surrogate/dataset.py:1026`;
    `training/provenance.py:191-194`).
  - Fake meetings still vote nobody out: 0 in 170 fake meetings, and 0 in 49 with the full recorded r2 settings.
- **The open problem is out of reach.** Reporters being voted out is a meeting outcome, and no tactical policy
  touches it.

**So:**

- Stage B raised the tactical layer's share of the outcome and made a crew objective trainable in principle.
- The preconditions from the 2026-09-24 analysis are still unmet (analysis memo:663-675, the list at :667):
  - gameplay settled;
  - an environment that runs the adopted rules;
  - training meetings that actually vote someone out;
  - no reward for guessing roles;
  - a fresh comparison run of the scripted policy;
  - a budget.
- Whether ML is now more or less worth doing has not been measured.
- The cheapest next step is not ML. It is a free lab run of the hand-written crew idle options already in the tree
  (Part 3, card 6).

---

## Part 2. The detail

### 2.1 Gameplay state (investigator `gameplay_state`)

**Refuter's verdict.** The mechanical half reproduces on every count. The meeting half was refuted as worded. I
re-checked every disputed count, and all the refuter's figures hold. I accept all twelve amendments, so the
investigator's memo should be read with the corrections below.

**Counts that stand** (investigator, re-run where marked R; commands in the appendix):

| | s9 | r1 | r2 |
|---|---|---|---|
| endings: crew by ejection / crew by tasks / impostor parity (R) | 38 / 1 / 11 | 12 / 4 / 34 | 13 / 13 / 24 |
| game-over tick, mean (median) (R) | 22.2 (20) | 32.8 (29.5) | 38.8 (35) |
| meetings; by a report / by the button | 145; 135 / 10 | 124; 118 / 6 | 117; 114 / 3 |
| first kill, median tick; kills per game | 4.5; 3.50 | 4.5; 4.54 | 7; 3.90 |
| meetings with vent proof (audit r2:1381) | 70/145 | 26/124 | 24/117 |
| stale report meetings | 43/135 | 0/118 | 0/114 |
| meetings opening with an impostor inside a vent (audit r2:1328) | 29/145 | 66/124 | 66/117 |
| kills a crewmate saw (census `kills_seen_by_crew`) (R) | 3/175 | 4/227 | 14/195 |
| seen killers ejected: at the next meeting / at any meeting (R) | 2/3 / 3/3 | 3/3 / 3/3 | 6/14 / 8/14 |
| innocent ejections; of them reporters (R) | 9; 7 | 15; 11 (+2 button openers) | 22; 17 |
| role-correct ejections (audit r2:1274, reported only) | 81/90 | 39/54 | 44/66 |

**Amendments accepted. Each is re-checked unless marked.**

1. **"Named the real killer" is too strong.**
   - The reporter-trap ejections (12 in r2) are meetings without vent proof where the reporter's opening accused an
     impostor on a placement the engine confirms, and the reporter was then voted out (`gs/trap2.py`).
   - The accused was the killer of the reported body in 9 of the 12, and was placed in the kill room within one
     tick of the kill in 6 of the 12.
   - The 6 are the 5 kill witnesses plus seed 9.
   - The same count in s9 and r1: 3 and 5 trap ejections.
2. **Crew-only tallies.**
   - Counting crew ballots alone ejects the same player in 17 of 22 innocent ejections (13 of 17 reporters).
   - A majority of the crew voted to eject in 15 of 22 (12 of 17) (`gs/q7.py`, `pivot.py`).
   - The investigator's "15 of 22" mixed these two measures.
3. **Impostors usually open the charge.** An impostor made the first accusation against the ejected reporter in 9
   of 17 reporter ejections and in 9 of the 12 trap ejections. Impostors cast 26 of the eject votes against ejected
   reporters.
4. **Kill witnesses: precise, but not certain.**
   - Of 14 crew-witnessed kills, at the next meeting the killer was ejected 6 times, the witness 5 times and the
     other impostor once; 2 meetings skipped.
   - The witness was the reporter every time.
   - Each witness held its own-kill row (census `crew_witnessed_kills_held_at_next_meeting` 14/14).
5. **The rise from r1 to r2 is the witnesses.** Reporter ejections rose from 11 to 17: 5 ejected witnesses plus
   1. Non-witness reporter ejections were 11 of 115 and 12 of 100 non-witness report meetings, a change within the
   noise.
6. **"The excerpts show the cause" is replaced.**
   - Two excerpts, one from a crewmate and one from an impostor, are consistent with a witness who walked in on the
     kill tick being called impossible.
   - The cause is not counted across the round.
7. **Scorecard row 8 pools both roles.**
   - Row 8 counts 189 of 410 eject votes as "wrong but believable", and that includes 111 strategic impostor eject
     votes.
   - The crew-only figure is 79 of 299 crew eject votes against a crewmate, 78 of them supported (`ends.py`).
   - The same figure was 75/450 on s9 and 72/280 on r1.
8. **Endings.**
   - Three of the engine's four endings occur; the sabotage win fired on 0 of 46 sabotages.
   - Sabotage appears in every task win because the rule-based trigger at 6 of 7 tasks done puts it there.
9. **The trap's precondition is a tactical choice.**
   - The meeting failure (misjudged routes, a counter-accusation from the impostor) sits on top of a tactical
     choice: impostors never self-report, which is R6, a tactical setting.
   - So the claim that tactical gameplay is settled holds except for the R6 genre choice.
10. **"Behind 10 of 24 impostor wins" is co-occurrence, not cause.**
    - 19 of 24 impostor wins contain an innocent ejection, against 2 of 26 crew wins (`ends.py`).
    - In 9 players with 2 impostors, an innocent ejection moves the game toward parity mechanically, so the trap
      cannot be isolated as a cause.
11. **"Every conformance cell 0" holds for the carried cells.** Four pre-registered cells are not carried
    (audit r2:1439-1441).
12. **Two options are narrower than stated** (not re-checked: the 2 of 26 is the refuter's).
    - An opener-first reply option favours innocents by seat under R6, because the opener is crew in 117 of 117
      meetings.
    - An own-turn ban on impostor ballots is bounded by 2 own-turn citations among the 26 impostor votes against
      ejected reporters.

**The investigator's ledger, as amended.**

| behaviour in r2 | class |
|---|---|
| the built rules: physical witness, look-and-wait, fresh-kill entry, full reset, cooldown 6 | fine |
| game shape: 39 ticks, 2.3 meetings, three endings, 13 task wins | fine |
| vents risky only when someone walks in; vent proof certain | fine |
| kill witness | precise but not certain (6 of 14 killers ejected next meeting, 5 witnesses ejected) |
| grounded, faithful, truthful speech | fine |
| balance 0.48 | fine; no further cooldown step |
| regroup invisible in the viewer; no cooldown label; "experimental" wording | presentation defect, promotion follow-up |
| 9-player featured strip | defect at promotion; re-curate |
| impostors never self-report | choice (R6), revisit is yours |
| evidence-free counter-accusation, strategic impostor ballot, the one reply going to an impostor, kill wave, button gone | choices to keep |
| reporter trap | the model misapplying the map, on a structure where every reporter is innocent; the envelope's only flag |

**Showability (investigator, not disputed).**

- 11 of 50 r2 games meet the opener criterion: seeds 3, 5, 6, 7, 10, 11, 19, 20, 27, 42 and 49
  (`scripts/measure_featured_criterion.py --parent replays/candidates/stage-b-r2 --set 9p2i`).
- Best openers: seed 7 (a vent ejection, then a kill-witness ejection) and seed 19.
- Strip candidates: 1, 6, 0 and 3.
- Keep out of the opener slot:
  - the 12 trap seeds;
  - seeds 4 and 36 (nothing established);
  - seeds 15 and 31 (task wins with nothing established);
  - seed 48 (two innocent reporters ejected back to back);
  - seeds 2 and 12 (one wrong ejection, then parity at tick 22).

### 2.2 Reporter ejections (investigator `reporter_ejections`; memo not written)

**The investigator's headline.** The flag was called mostly an old reporter bias, enlarged by the switch from vent
proof to deduction. Within it, the failure was route arithmetic: 11 of 22 innocent ejections, including all 5
ejected witnesses. The investigator also called this "a limit of the 27B model" and said the existing one-hop route
check would not catch the witness cases.

**Refuter's verdict.** The descriptive counts hold, but the causal headline does not. I re-ran the investigator's
scripts and agree. Re-checked counts:

| | s9 | r1 | r2 |
|---|---|---|---|
| reporter ejected, all report meetings | 7/135 | 11/118 | 17/114 |
| the same, report meetings without vent proof | 7/75 | 11/98 | 17/93 |
| the same, report meetings with vent proof | 0/60 | 0/20 | 0/21 |
| reporter ejections undone if impostor ballots were SKIP | 3 of 7 | 7 of 11 | 10 of 17 |
| reporter ejections undone if impostor ballots were removed | 0 of 7 | 2 of 11 | 4 of 17 |
| meetings where a skip happened but crew alone would have ejected | 6 | 6 | 3 |
| first accuser of the ejected reporter: impostor / crewmate | 4 / 3 | 8 / 3 | 9 / 8 |
| ejected reporters who got the one reply | n/a (switch off) | 10 of 11 | 15 of 17 |

**Amendments accepted.**

1. **Composition.** "Made larger by the switch from vent proof" becomes:
   - all reporter ejections fall at meetings without vent proof;
   - the shift in mix explains about a quarter of the rise from s9 to r2 (a prediction of 0.076 against 0.149);
   - it explains none of the r1-to-r2 crossing.
2. **The counterfactual tally.** Add it (the table above). Because the strategic impostor ballot and the table's
   reasoning landed together, neither the ballot nor route arithmetic can be credited alone.
3. **The witness split.**
   - The 17 split into 5 of 14 witness reporters and 12 of 100 others (s9: 1 of 3 and 6 of 132; r1: 0 of 3 and 11
     of 115).
   - The crossing rests mainly on the witness class.
4. **"All 5" restated.**
   - In 4 cases a walkable stated route was called impossible. In one of them (seed 28), the refuter reports the
     charge was raised by an impostor and echoed by a crewmate.
   - The fifth (seed 30, meeting 1) is a public-regroup relocation:
     - the previous meeting closed at tick 11;
     - the reporter's own stated route jumps from Labs to the Cafeteria across that regroup;
     - the charge came from the named killer, in the first reply.
   - The refuter's token test found the regroup notice in all four of the other crew voters' prompts. I did not
     re-run that test.
5. **The 11 of 22 is not reproducible.**
   - No script outputs it; it is one rater's classification, with five boundary cases (it moves between 9 and 12).
   - Keyword stand-ins give 4 to 14 of 22. My own gives 11 of 17 reporters, against 12 of 44 impostor ejections,
     so the stand-in is not specific (`routeproxy.py`).
   - Wherever the claim is about the reporter flag, the denominator is 17, not 22.
6. **"A limit of the 27B model" becomes:** in the counted turns, the 27B misapplied the map it held. Nothing here
   overturns the standing verdict that a stronger model is not the first fix (analysis memo:459). No other model
   was run.
7. **The existing route check, and whether it would catch the witness cases.**
   - **What the check is.** It is the walkable-pair clause of the corroboration ledger
     (`meetings/corroboration.py:561-605`), rendered as one ballot line (`vote_ballot.j2:270`).
     - It covers pairs one hop and one tick apart (`meetings/constants.py:62-63`).
     - It lives behind an ambient switch, `AILIBI_CORROBORATION_DISCIPLINE` (`meetings/corroboration.py:89`), off
       in all three columns.
   - **Transcript-only probe** (`walkfire.py`, re-run):
     - a walkable pair for the ejected player in 12 of 22 innocent ejections, against 1 of 44 impostor ejections;
     - none for the 5 ejected witnesses.
   - **The refuter's version.** It adds the movement-sighting destinations and the regroup ticks that the meeting
     manager passes (`meetings/manager.py:1703-1713`). It finds a pair in 3 of the 5 witness cases and in 17 of 22.
   - The claim is **not established either way**. Card 2 settles it at no cost.
8. **Round 3 is an option, and its reading is a process count.**
   - If offered, round 3 is your option.
   - It is read by a process count: impossible-move charges against stated pairs the map or a public regroup
     reconciles.
   - It is never read by reporter ejections or by role-correctness.
   - **Why that matters.** With self-report off, every reporter is a crewmate, so "reporter ejections" is an
     innocent-ejection count. A walkable pair is also strongly tied to role (12 of 22 innocent against 1 of 44
     impostor ejections, because impostors vent).
   - A route check is legitimate only as a line built from public statements, the public map and the regroup notice,
     and judged by what it does to the reasoning.

**What stays open.**

- Why crew-witnessed kills rose from 4/227 to 14/195. The cooldown is the only setting that differs, but each round
  is a single recording.
- Whether any route line would change the 27B's ballots. No column was recorded with one on.

### 2.3 Tactical ML (investigator `ml_tactical`)

**Refuter's verdict.**

- The counts reproduce.
- The training-stack blockers and the 0-of-170 fake ejections hold, also under the full recorded config (0 of 49).
- Keeping the hold matches ruling 12.
- But the headline's framing fails. I re-checked the disputed counts (`ends.py`, the census) and accept all eight
  amendments.

**Counts that stand** (investigator; tactical decision census in `ml_tactical-scripts/tactical_census.py`):

- **Impostor decisions in r2.** There were 3,088; the kill cooldown was running for 1,816 of them.
  - 195 kills were applied, and 44 attempts were lost to a target that moved first.
  - 140 vent entries; 0 entries away from the impostor's own fresh kill.
  - 124 waits inside a vent and 72 exits.
  - 46 sabotages applied.
- **Crew decisions.** There were 9,105.
  - 1,813 idle crew-ticks, all spent standing at the hub. That is 19.9% of crew decisions, against 6.9% on s9.
  - 116 of 116 crew-ticks with a body in the room reported it.
- **Slack the rules leave open:**
  - kill timing: the first kill of a game lands at the earliest legal tick or the next in 39 of 50 games;
  - target choice;
  - where idle crew stand;
  - task routing in a close race: 12 of 24 impostor wins came with the crew at 80% or more of tasks.
- **Blockers.** They are in 1.5, with citations. Fake probe: 69, 52 and 49 fake meetings, 0 ejections
  (`llm/fake_provider.py:120-145`; the lab says so itself, `experiments/tactical_gameplay.py:129`).

**Amendments accepted.**

1. **The headline is restated.**
   - Play-tick endings rose 12, 36, 35 because meetings removed fewer impostors (81, 39, 44) and ejected more
     innocents (9, 15, 22).
   - At least 27 of r2's 35 play-tick endings followed a meeting ejection that set up the end state (re-checked:
     17 of 22 parity endings, 10 of 13 task wins).
   - So the meeting stays decisive; it now decides on thinner data.
2. **Kills with two or more crew present (Phase 18's "N2") were already 0** on s9 and in Phase 18's scripted
   comparator. A scripted zero does not bind a learner.
3. **The lever to name is N1, not seen exits.**
   - The scripted crew-witnessed kill rate is 3/175, 4/227, 14/195, and no conformance check pins it.
   - For scale only (a different setup): Phase 18's scripted comparator read 8/174 and the learned impostor 30/197
     (`docs/ml-program.md:110-111`).
4. **The attribution of fewer, longer meetings to the regroup and the cooldown is removed.** Eight rules landed
   together at r1, and only conformance cells and lab rows attribute a mechanism (audit r2:368-370, section 1.11).
5. **The cost of a seen kill.**
   - 8 of 14 seen killers were ejected at some meeting, against 24 of 24 seen venters.
   - s9, with no kill row, read 3 of 3, so the kill row's effect is not demonstrated.
6. **The fake-path reward does price a seen kill.** `unwitnessed_kills` still does that (`training/rewards.py:288`,
   `:356`). Only being seen venting is free in the impostor terms, and the conviction term pays for evidence on top
   (`training/bakeoff/harness.py:1055-1056`).
7. **The verdict is restated.**
   - The hold stands unchanged under ruling 12.
   - Stage B raises the tactical layer's leverage, but the analysis memo's preconditions remain unmet.
   - The comparative "less worth doing than before" is withdrawn, because nothing measured it.
8. **The fake probe's settings.** The investigator's fake-meeting probe omitted four recorded meeting keys. With the
   full recorded r2 config the result is the same: 0 ejections in 49 fake meetings (refuter's run; I did not re-run
   it).

**What ML could add, ranked (investigator, kept with the amendments).**

1. **Crew idle positioning for role-blind evidence.**
   - The objective would be the share of living players whose room a living crewmate saw first-hand at each kill,
     counted for every player whatever their role.
   - It fits your value: more data held, nobody pushed toward the answer.
   - The hand-written `patrol` and `accompany` idle policies have never been measured on these rules, so measure
     them first.
2. **Impostor kill timing and target choice.**
   - This has the largest win leverage.
   - But it is a balance lever the cooldown already controls, and its natural optimum is N1 and fewer meetings.
3. **The task race.**
   - Crew routing and sabotage timing; this is new in Stage B and decided without the model.
   - Its risk is a task rush that bypasses meetings.

**Rules for any future objective.**

- No term may read roles: `correct_reports` and `patrol_coverage` go (`training/rewards.py:301-357`).
- No term may pay for evidence produced about oneself (`training/bakeoff/harness.py:1056`).
- The conformance checks are hard limits in the option menu, never penalties.
- Meeting counts are read as floors, never rewarded.

### 2.4 My re-checks, in one place

Everything below was re-run at `d41c9006` in a bare shell. All of it agrees with the refuters.

| claim | result | script |
|---|---|---|
| reporter rate by vent proof; the mix prediction | 7/75, 11/98, 17/93; mix flat r1 to r2 (98/118, 93/114); s9 rates on r2's mix give 0.076 | `baserate.py` |
| counterfactual tallies | impostor ballots as SKIP undo 3/7, 7/11, 10/17; removed undo 0/7, 2/11, 4/17 | `pivot.py` |
| witness split | 1 of 3, 0 of 3, 5 of 14; others 6/132, 11/115, 12/100 | `witness.py` |
| witness outcomes and the five witness ejections | killer ejected 6 next meeting, 8 at any; all 5 ejected witnesses named the killer; the first accuser was the killer in 4 of 5; seed 30 meeting 1 follows a regroup at tick 11 | `wit2.py` |
| witnesses walk in on the kill tick | 3 of 3, 3 of 3, 14 of 14 | `skiplabels.py` |
| trap ejections | 12; killer named in 9; at the scene within a tick in 6; impostor first accuser in 9 | `gs/trap2.py` |
| crew-only tally, crew majority | 17 of 22 (13 of 17 reporters); 15 of 22 (12 of 17) | `gs/q7.py`, `pivot.py` |
| endings against earlier ejections | 17 of 22 parity after a crew ejection; 10 of 13 task wins after an impostor ejection; innocent ejection in 19 of 24 impostor wins and 2 of 26 crew wins | `ends.py` |
| crew eject votes against crewmates | 75/450, 72/280, 79/299 (78 supported in r2) | `ends.py` |
| transcript-only walkable pairs | 12 of 22 innocent, 1 of 44 impostor, 0 of 5 witnesses | `walkfire.py` |
| route keyword stand-in | reporters 4/7, 7/11, 11/17; impostors 14/81, 10/39, 12/44 | `routeproxy.py` |
| skip labels | r2: 214 of 281 "holds nothing", 44 supported, 6 off-target, 17 not assessed | `skiplabels.py` |
| seen-kill census cells | 3/175, 4/227, 14/195; held 3/3, 3/3, 14/14; killer ejected next meeting 2/3, 3/3, 6/14 | census `--set-dir` |
| honesty | crew false 4/632, impostor false 0/122 | `measure_baseline.py --honesty --json` |

---

## Part 3. Recommendations, as next cards, in order

Each card is a recorded arm or an instrument. None uses an ambient switch (`AILIBI_*`, `corroboration_discipline`,
`testimony_shapes`). No card re-records unless a mechanism changes.

**Card 0. The promotion follow-ups, carried by the promotion you have chosen.**

- **What it is.** Promotion moves round 2 into `replays/samples/9p2i` as the shown set, path (b) of the decision
  memo (`tasks/decision-2026-09-24-stage-b-wave.md:219-239`). That path's list:
  - the v8 prompt archive;
  - era-keyed scorecard pooling and provenance check;
  - the watchability stage block;
  - the public-results and tour minimum;
  - the s9 re-pin sweep;
  - lifting the record-plumbing refusal;
  - the viewer items deferred from B2 (`:249-251`).
- **This diagnosis adds three items:**
  - a regroup moment in the viewer, saying on screen that everyone returns to the Cafeteria and bodies are cleared;
  - a kill-cooldown label on the public results page, and dropping "experimental" for adopted rules
    (`PublicResults.tsx:7-21`; audit r2:375-380);
  - a re-curated 9-player strip: opener seed 7 or 19, strip candidates 1, 6, 0 and 3, and the seeds in 2.1 kept
    out of the opener slot.
- **Fixes:** showability.
- **Costs:** code and documents, no model spend.
  - Merging it publishes: `pages.yml` rebuilds the demo from `replays/samples`.
  - s9 becomes the legacy-era column.

**Card 1. Instrument: the reporter flag with its base rate ($0).**

- **What it adds to the gameplay census (count-only).** Each new cell comes with a planted case that proves it fails
  on the defect it claims (craft rule 2).
  1. A per-seat ejection table at report meetings: reporter, other innocent, impostor, split by vent proof
     (section 1.4).
  2. A kill-witness outcome row: killer ejected at the next meeting and at any meeting, witness ejected, other
     ejected, skip. Lone witnesses are counted apart from corroborated ones.
  3. The two counterfactual tallies (impostor ballots as SKIP; removed), beside the existing floor-only cell.
  4. The "holds nothing" skip label (214 of 281 today, from my scratch count), so your first goal reads for skips
     too.
- **Fixes:** the flag reads with its base rate, and the next round's reading becomes interpretable.
- **Costs:** eval code, docs and tests; no spend. Census cells stay out of the scorecard (ruling R13), so no
  amendment to ruling D1 is needed.
- Restating the envelope's reporter line relative to the other-innocent rate would be a change to a pre-registered
  rule. That is yours to decide (Part 4).

**Card 2. Instrument: an offline route-check replay ($0). Do this before any round 3.**

- **What it computes.** On the committed bytes of s9, r1 and r2, count-only, what each candidate route check would
  have shown each voter. It covers the 22 innocent ejections, the 44 impostor ejections and the 14 witness meetings.
  It reads two checks:
  - **(a) The existing walkable-pair clause** (`meetings/corroboration.py:561-605`), built as the meeting manager
    builds it, with movement records and regroup ticks (`meetings/manager.py:1703-1713`). Its one-hop, one-tick
    limit is in `meetings/constants.py:62-63`.
  - **(b) The travel-check lines of the existing recorded field `evidence_reasoning_version = 2`**
    (`agents/memory/evidence_context.py:340-560`). This field already handles several hops, and it already says a
    walking-only check cannot decide an interval that crosses the public regroup (`:540`).
- **Fixes:**
  - the disputed counts (0 versus 3 of 5 witness cases; 12 versus 17 of 22);
  - which check, if any, would have reached the misjudged cases.
- **Its reading is a process count:** impossible-move charges against stated pairs that the map or the public
  regroup reconciles, plus ejections of a player who had such a pair. Never reporter ejections, never
  role-correctness.
- **Costs:** an eval instrument or a scratch script; no recording, no spend.

**Card 3. Lab row: attribute the rise in kill witnesses ($0, optional).**

- **What it does.**
  - Add a crew-witnessed-kill row and a walk-in-witness row to the tactical lab.
  - Read them on the existing cooldown arms (`stage_b_full` against `stage_b_full_kill_cooldown_6`,
    `experiments/tactical_gameplay.py:150-157`) over more development seeds.
- **Fixes:** the unexplained rise from 4/227 to 14/195. It is mechanics only; fake meetings do not matter here,
  because witnessing happens between meetings.
- **Costs:** a small lab change; no spend.

**Card 4. Recorded arm: round 3 with one meeting-layer route check. This is your spend decision, and only if card 2
shows a check that reaches the misjudged cases.**

- **Which arm.**
  - **Prefer the existing recorded field `evidence_reasoning_version = 2`** if card 2 shows it reaches them. It needs
    experiment format 2 (`orchestrator/experiment_config.py:103-111`), and it is allowed beside the regroup
    (`:138-144` refuses only version 1).
  - **Two cautions about that field.**
    - It is a package: it also adds death-evidence and account-uncertainty lines.
    - Its only live reading, the archived fifth run (proof-free openings, three ballots per meeting), produced 14
      eject and 136 skip votes, none of the skips citing anything (`docs/process-scorecard.md:266-267`). The risk is
      a table that stops deciding.
  - **Otherwise, a new narrow field.** Versioned, default off, set only from the config file, with its own stamp. It
    renders one line per living candidate, the same for every role:
    - pairs of places stated at the table that the map links within the elapsed ticks (several hops);
    - moves that cross the public regroup.
    - It never asserts presence or honesty.
- **Before any spend:**
  - planted cases: West Hall to Admin, 1 hop in 1 tick; Admin to Cafeteria, 2 hops in 2 ticks; across a regroup;
  - fake and scripted rehearsals;
  - lab rows.
- **The round itself.** Same seeds 0-49, the same eight rules, cooldown 6, the same ceilings.
- **Pre-register:**
  - the card-2 process count;
  - the witness outcome row;
  - the per-seat ejection table;
  - the impostor win share against 0.20-0.60. Saving witnesses helps the crew, so watch the 0.20 floor.
- **Fixes:** if it works, the table's route mistakes, which is the reasoning behind the reporter trap.
- **Costs.**
  - About r2's spend: 1,588 calls, 9.7M input and 0.44M output tokens, a 3.6 h wall, $0 marginal on flat-rate
    Featherless (audit r2:1208-1214). Any live call needs your explicit authorization and budget.
  - Plus the card's code.
  - Plus a second promotion if you adopt it.
  - It changes a mechanism, so a recording is justified.

**Card 5. Your genre choice, not now: revisit R6 (impostor self-report).**

- **What it is.** The existing recorded tactical field `self_report` (`orchestrator/experiment_config.py:50`).
- **What it changes.**
  - Suspecting the reporter becomes sometimes right, as in Among Us.
  - It changes what the reporter flag means.
  - It needs the ballot's reporter paragraph reworded under a new version, since `vote_ballot.j2:331` tells voters
    that impostors rarely report a body.
  - It carries balance risk: in fake test games, always self-reporting removed vent exits entirely (analysis memo,
    Part 5 item 6).
- **Never in the same round as card 4.** Two changes in one round could not be told apart.

**Card 6. Lab, ML-adjacent ($0, after the promotion): the crew idle-policy cross.**

- **What it does.**
  - Cross the Stage-B rules plus cooldown 6 with `crew_idle_policy` = `hub_wait`, `patrol` and `accompany` on
    development seeds (the lab already defines both alternatives, `experiments/tactical_gameplay.py:174-175`).
  - Count the task race, kills, crew-witnessed kills, and a whereabouts-coverage count computed from engine
    positions the same way for every role.
- **Fixes:** whether any slack is left for a learned crew policy. If a hand-written policy closes it, the ML case for
  the best-aligned target disappears.
- **Costs:** a lab change; no spend. No ML is trained.

**Not recommended.**

- **Another cooldown round.** The rule names none, and 0.48 sits mid-envelope.
- **An opener-only reply value.**
  - It is bounded: only 2 of 17 ejected reporters got no reply.
  - It favours innocents by seat under R6.
- **Banning own-turn citations in impostor ballots.** It is bounded by 2 of 26 impostor votes against ejected
  reporters.
- **Giving the table the kill time back.** Removing it was B4's purpose, and the genre does not give it.
- **Any ambient switch.**
- **A stronger model.** It is untested, and the standing verdict says it is not the first fix.
- **Any ML training.**

---

## Part 4. Open for the owner

1. **Promotion over the flag.** You said "Promote".
   - Confirm that you take it with the flag reported beside its base rate (1.4), and with the card-0 follow-ups.
   - Merging the promotion publishes the demo.
2. **The envelope's reporter line.** Keep it as an absolute rate (0.104), or read it relative to the other-innocent
   rate (card 1).
3. **Round 3.** Whether to spend on a route check (card 4) once card 2 has run, and which of the two checks.
4. **R6.** Keep impostors from ever reporting, so every reporter stays innocent, or revisit it (card 5).
5. **The tour** (ruling 11 deferred it until gameplay is finished; promotion may end that).
   - Opener: seed 7 or 19.
   - Whether a reporter-trap game is ever shown, and if so, only labelled honestly as a reasoning mistake.
6. **ML.**
   - Confirm the hold.
   - Decide whether to run the free idle-policy lab (card 6) after the promotion.
7. **The four uncarried checks.** Whether to give them instruments (card 1 covers the skip label).

---

## Limitations

- Each column is one hosted recording of 50 games. r1 and r2 differ in one setting, but their differences are
  readable only within the noise between recordings, and the reporter rates' ranges overlap.
- The rules landed together. Only conformance cells and lab rows attribute a mechanism to one rule.
- **Not counted round-wide:** how often the route mistake drives an ejection. The hand classification (11 of 22) is
  one rater's, and keyword stand-ins are not specific.
- **Not re-run by me:**
  - the refuter's regroup-notice token test for seed 30;
  - the full-config fake probe (0 of 49);
  - the 2 of 26 own-turn citations;
  - the showability criterion run.
  The figures are the investigators' or refuters', and the mechanisms are cited.
- **The viewer finding comes from code, not a running viewer.**
- **The "holds nothing" skip count** reads the recorded grounding label, which is the model's own statement about
  what it holds, not a checked fact.
- **Counterfactual tallies hold every other ballot fixed.** Real voters would have heard different speech.

## Appendix: reproduction (count-only, repo root at `d41c9006`, bare shell, after `uv sync --frozen`)

Committed instruments, which write nothing:

```
uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r2/9p2i --json-stdout
uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout
uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout
uv run python scripts/publish_process_scorecard.py --set-dir replays/candidates/stage-b-r2/9p2i --json-stdout
uv run python scripts/measure_baseline.py replays/candidates/stage-b-r2/9p2i --honesty --json
uv run python scripts/measure_baseline.py replays/candidates/stage-b-r2/9p2i --funnel
```

Synthesis scripts, count-only, in the session scratch directory `synthesis-scripts/` (not committed). They print
ids, ticks, rooms, roles, labels, booleans and counts, never text. Set `S` to that directory and run them from
the repo root:

```
uv run python $S/dossier.py replays/samples/9p2i $S/d_s9.json
uv run python $S/dossier.py replays/candidates/stage-b-r1/9p2i $S/d_r1.json
uv run python $S/dossier.py replays/candidates/stage-b-r2/9p2i $S/d_r2.json
uv run python $S/gs/load.py s9 r1 r2
uv run python $S/gs/walk2.py s9 r1 r2
python3 $S/baserate.py $S/d_s9.json $S/d_r1.json $S/d_r2.json
python3 $S/pivot.py $S/d_s9.json $S/d_r1.json $S/d_r2.json
python3 $S/witness.py $S/d_s9.json $S/d_r1.json $S/d_r2.json
python3 $S/wit2.py
python3 $S/ends.py
python3 $S/routeproxy.py
python3 $S/skiplabels.py
uv run python $S/gs/q5c.py
uv run python $S/gs/q7.py
uv run python $S/gs/trap2.py
uv run python $S/walkfire.py replays/candidates/stage-b-r2/9p2i $S/d_r2.json
```

`dossier.py`, `baserate.py`, `pivot.py`, `witness.py` and `walkfire.py` are the reporter investigator's scripts,
unchanged. `gs/load.py`, `gs/walk2.py`, `gs/q5c.py` and `gs/q7.py` are the gameplay investigator's, unchanged.
`wit2.py`, `ends.py`, `routeproxy.py`, `skiplabels.py` and `gs/trap2.py` are mine. The dossier reads ballot prompts
only to classify which kind of row a ballot cited; it writes no prompt text.
