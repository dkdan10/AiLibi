# The finalized state: what the project demonstrates, and what it does not (2026-10-10)

Card: [`tasks/work/close-audit-finalized-state.md`](../tasks/work/close-audit-finalized-state.md).
Base B: `main` at `a3b42fd4`, after the finish wave merged in its card's order
(round 3's record, the retirement of the era-locked pins, round 3's promotion
and the process-first front door), the orchestrator's four `card:` commits
flipped those cards and its `docs:` commit stamped the task inventory (section
6 names all five). Branch
`work/close-audit-finalized-state`, one pull request into `main`; its head H and
CI's green run at H are cited in the card's Results and the pull request.

This is a close. It decides nothing, adopts nothing and moves no recorded byte.
Every figure below is read at H from a committed command or a page line,
count-only, and section 8 lists each one with its source; the two advisory memos
kept outside the tree are cited as advisory and are the source of no figure.
Owner rulings are quoted verbatim and dated; orchestrator readings are labelled
as readings. An error this audit finds in an earlier record is filed in section
7, never edited into that record.

## 0. For a reader who did not watch the work

**What AiLibi is.** A recorded game of hidden roles played by language-model
agents on one fixed space-station map. At the nine-player table seven players
are crewmates, who do tasks, and two are impostors, who kill and deceive. When
a body is reported or someone presses the emergency button, play stops for a
meeting: the living players speak in turn, then each casts a ballot, either to
eject one player or to skip. A deterministic engine advances the world one tick
(the game's unit of time) at a time, simple scripted rules move the players
between meetings, and the model speaks and votes only at meetings. Every game
is committed as a replay that the engine re-runs byte for byte.

**What it asks.** Not whether the players vote the impostors out. The
[owner](../docs/glossary.md#owner), the project's one human decision-maker, set
its goal on 2026-09-19: an agent's vote or skip must rest on data the agent
actually holds, true or false. A crewmate who ejects an innocent player on a
believable but false statement made at the table is the game working, not a
failure of the system.

**What the evidence shows.** The figures below come from the shown 9-player
set: the fifty games the public demo and the README show, recorded once on
2026-10-09.
- Of the ballots to eject a player, 394/397 = 0.9924 cite a line their voter
  held about that player: a statement made at the table, or an observation in
  the voter's own memory. That is a floor, not a quality reading, because the
  ballot asks every eject to cite.
- 6/702 ballots carry no reason their voter stated.
- A skip whose voter said it held nothing always had a living candidate named
  somewhere in its own inputs: 0/235 such skips had none.
- Where a cited line places its target somewhere checkable, the engine's own
  record of where each player stood makes the line true in 245/248 cases.
- 177/397 eject ballots name a crewmate while citing a line their voter held.
  That count is reported and never penalised: a wrong vote on believable data
  is the game working.
- The replays reconstruct byte for byte, and import rules and planted-leak checks
  guard what an agent may see. Those checks are bounded, not a complete privacy
  assurance.

**What it does not show.**
- That the players find the impostors. How often an ejection removed an
  impostor, 46/61 on the shown set, is reported and gates nothing.
- That one version of the game plays better than another. Each round of
  changes was recorded once, as fifty games, so no difference between rounds is
  claimed as real.
- That the model reasons about routes. The newest change hands a voter, when a
  candidate's places stated at the table change room, a plain line saying which
  of those moves the station's doors allow; the tree measures that the line was
  shown, not that it changed a vote.
- General social deduction. The machine-learning program is on hold.

**Where to look next.** [The README](../README.md) and its
[reading guide](../docs/reading-guide.md); three pages generated from the
replays, each with a check that recomputes it from them:
[the process scorecard](../docs/process-scorecard.md) (whether each decision
rested on data its voter held), [the gameplay census](../docs/gameplay-census.md)
(what happened in the games) and [the game-shape profile](../docs/game-profile.md)
(each game's moments, with no score); [the glossary](../docs/glossary.md);
[the audits index](README.md); and the
[recorded demo](https://dkdan10.github.io/AiLibi/). Sections 3 and 4 below give
each claim its command, and sections 6 and 7 list the work that reached the main
branch and what is left open.

## 1. What the system is

The engine is a pure tick function: from one tick's state and actions it returns
the next state, and every recorded tick carries a state hash, so a committed
replay re-runs through the engine byte for byte. At H
`bash scripts/verify_samples.sh` re-runs every committed sample set and
candidate round and exits 0, and a fake-provider game recorded twice is
byte-identical
(`tests/orchestrator/test_game.py::test_headless_game_replay_is_byte_identical_for_same_seed`).
The claim holds at the strength `docs/architecture.md:105-106` states it: a seed,
configuration, agent factory and provider responses determine the bytes within
their recorded runtime scope. Fresh hosted generation is not deterministic, so
for a hosted run the recording, not the seed, is the reproducibility boundary.
(claim row `engine`)

Between meetings every player is moved by the scripted tactical policy, which
every committed set's MANIFEST stamps `fsm-default`; the model is called only at
meetings and explicit triggers. That is AGENTS.md's load-bearing rule 2, and its
strength is a review rule's: no import gate forbids `agents/tactical` from
importing the model client, because `llm` sits inside the observation firewall's
interior beside the agents (`tests/test_firewall.py`, `_FIREWALL_INTERIOR`). At H
no file under `agents/tactical` imports it. (claim row `tactical`)

Agents reason from sanitized observation packets and a public map, never from
the engine. Five import-linter contracts forbid agents importing the engine,
training or the meeting manager, forbid the observation package importing
agents, meetings or the model client, and forbid the running game importing the
game-shape profile (`.importlinter`; `uv run lint-imports` prints
`Contracts: 5 kept, 0 broken.`). A forbidden import planted in an isolated copy
must be rejected
(`tests/test_firewall.py::test_import_linter_reports_a_planted_agents_to_engine_route`),
and packet scans look for planted leaks (`eval/leak_scan.py`). These are bounded
checks, not complete privacy assurance (`README.md:22`): in the baseline-9
recordings a default opening prompt reveals a hidden death tick through a body
identifier, and on the shown set no report opening carries it (the census cell
reads 0/115 by construction). (claim row `firewall`)

The meeting layer writes a [grounding label](../docs/glossary.md#grounding-label-what-the-meeting-found-under-a-ballot)
onto each ballot after the vote, and the tally never reads it: the outcome is
the same under every label, and the tally's source names neither the field nor
any of its values
(`tests/meetings/test_grounding_label.py::TestTheTallyNeverReadsTheLabel`). One
mechanism does re-aim ballots, and the scorecard counts it: the teammate
firewall turns an impostor's ballot against its own partner into a skip, so on
the shown set 692/702 = 0.9858 of ballots keep the target their voter wrote, the
other ten being such skips (scorecard row 7's detail, `teammate_coerced 10`).
The doctrine's "the layer labels; it never rewrites" holds for the grounding
label, not for the teammate firewall. (claim row `labels`)

The game's shape is written down in `docs/game-shape.md`: venting is visible,
impostors never report, actions resolve in player-id order, meetings pause the
world, and crewmates see one room. Where a recorded setting makes a shape a rule,
the census counts it as a conformance cell that reads zero by construction and
exits non-zero on a breach: on the shown set no meeting was opened by an
impostor (0/119 by construction). Its planted pairs are
`tests/eval/test_gameplay_census.py::test_every_guarded_cell_has_a_planted_pair`,
and `uv run python scripts/publish_gameplay_census.py --check` recomputes the
page from the replays. (claim row `shape`)

The committed replays fall into recorded eras. An
[era](../docs/glossary.md#era-recordings-that-share-one-recorded-identity) is the
recorded identity a group of games shares (its settings, temporal delivery,
substrate stamp and prompt stamps), and `eval/eras.py` is the one place a
committed set's era is named. The instruments its docstring names (the process
scorecard, the gameplay census, the counterfactual, the watchability referee's
default floors and the front door's fact checker) read it and pool only within
an era, and `tests/eval/test_eras.py` holds the registry to the bytes, including
a planted registry that files the shown set under baseline 9 and is refused
(`tests/eval/test_eras.py::test_a_registry_filing_samples_9p2i_under_baseline_9_is_refused`).
The docstring's "every instrument" is wider than the tree: the offline
reasoning-evidence scorecard folds all four sets, across both eras, into one
block without reading the registry (section 7.4, finding 16). Section 2 prints
the registry. (claim row `eras`)

A record covers 50 seeds, not all 300: the partial-record principle. The owner
ruled it on 2026-09-24, verbatim: "Let's not re-record all 300 seeds each time.
When it's time to record, record the smaller group of 50 seeds, assess if the
implementations have been effective and resulted in desired results." (decision
memo section 0.1, quoted again in the direction's addendum of 2026-09-24, "a
record covers 50 seeds, not all 300"). Each candidate round records seeds 0-49 of
the 9-player roster once, into its own directory under `replays/candidates/`, and
a promotion moves one round into `replays/samples/9p2i` under its own era while
the other three sets keep their baseline-9 bytes (decision memo section 1). The
recorder refuses to record a committed set under any config but its own era's
declared one (`scripts/_declared_experiment.py`;
`tests/scripts/test_refresh_samples.py::test_an_era_refusal_names_the_set_and_the_declared_file_it_found`).
(claim row `recorder`)

A ballot's citation is checked for resolution, not for truth. "*Valid* means
resolvable, not supported." (`README.md:33`), and the scorecard's grounded row
states the same limit in its own definition: "It does NOT measure whether the
cited line was factually true." (`docs/process-scorecard.md:211`). The citation
counter splits valid citations from dangling ones
(`tests/eval/test_vj_instruments.py::test_citation_counts_split_valid_from_dangling`),
and whether a cited line is true of the engine's route is a separate census cell
(section 3.2). (claim row `citations`)

Role-correct ejection is reported beside the scorecard's rows and is never a
gate: the scorecard refuses to build itself if role-correctness is marked a gate
or not reported (`ProcessScorecard._role_correctness_stays_demoted`,
`eval/process_scorecard.py:623`), and the row's own label says so
(`tests/eval/test_process_scorecard.py::test_the_role_correct_row_is_labelled_as_no_gate`).
`uv run python scripts/publish_process_scorecard.py --check` recomputes the page
from the replays. (claim row `role`)

## 2. The eras and the committed sets

### 2.1 The era registry at H

The table below equals, row for row, the print of `eval.eras.COMMITTED_SETS`
and `LADDER_TIP_ERA` at H (command `era-ladder`, section 8.1).

Ladder tip: `baseline-9`

| committed set | era | owning record | recorded on | declared config |
| --- | --- | --- | --- | --- |
| `replays/ml_corpus/9p2i` | `baseline-9` | `audits/audit-2026-09-22-process-rerecord.md` | `2026-09-22` | `None` |
| `replays/samples/9p2i` | `stage-b-r3` | `audits/audit-2026-10-09-stage-b-r3.md` | `2026-10-09` | `replays/samples/9p2i/experiment-config.json` |
| `replays/ml_corpus/4p1i` | `baseline-9` | `audits/audit-2026-09-22-process-rerecord.md` | `2026-09-22` | `None` |
| `replays/samples/4p1i` | `baseline-9` | `audits/audit-2026-09-22-process-rerecord.md` | `2026-09-22` | `None` |

`ERAS` holds the two eras these sets belong to, `baseline-9` and `stage-b-r3`.
The registry also names `STAGE_B_R2`, round 2's era, which owns no committed
set: its bytes are the candidate copy `replays/candidates/stage-b-r2`, read with
the declared config `replays/candidates/stage-b-r2/experiment-config.json`
(`eval/eras.py:79-87`). The substrate ladder tip stays at baseline 9, and
baseline 10 stays reserved for the full re-record that re-freezes the corpus
(`eval/eras.py:23-24`). The shown 9-player set is round 3, promoted on 2026-10-09
by the orchestrator under the owner's delegation (section 3.6); the 4-player
sample set and the two corpus sets keep the baseline-9 process re-record.

The partial-record principle (section 1) is why the eras split: a round
re-records one set, so the shown 9-player set moved era and the other three did
not. Its mechanisms are the recorder's era refusal and the registry's planted
refusal, both named in section 1.

### 2.2 The candidate rounds at H

`git ls-files replays/candidates | cut -d/ -f1-3 | sort -u` at H (command
`candidates`) lists exactly the paths below.

| candidate path | what it holds |
| --- | --- |
| `replays/candidates/README.md` | the candidate family's rule and the format of a round's declaration |
| `replays/candidates/stage-b-r1` | round 1: seeds 0-49 of the 9-player roster with every Stage-B switch on and the map's own kill cooldown, declared by `replays/candidates/stage-b-r1/experiment-config.json`; record `audits/audit-2026-09-27-stage-b-r1.md`; kept as the comparison record that isolates the cooldown dial |
| `replays/candidates/stage-b-r2` | round 2: the same seeds with the seven adopted switches, the kept vent exit and a six-tick kill cooldown, declared by `replays/candidates/stage-b-r2/experiment-config.json`; record `audits/audit-2026-10-01-stage-b-r2.md`; the shown set from 2026-10-02 to 2026-10-09, kept at round 3's promotion as the comparison record for the route lines |

Both stay by the owner's ruling of 2026-10-09, verbatim: "Keep the comparison
records" (decision memo section 8.9, its amendment). Round 3's own candidate
directory retired at its promotion, because its bytes became the samples set.

### 2.3 Where each replaced recording is still readable

Each location is checked at H with `git cat-file -e <location>` (exit 0).

| recording | location | replaced by |
| --- | --- | --- |
| baseline 9's 9-player sample set | `d41c9006:replays/samples/9p2i` | round 2's promotion, merged as `0e67f42a` on 2026-10-02 |
| round 2's bytes while they were the shown set | `2eed2e92:replays/samples/9p2i` | round 3's promotion, merged as `54dff069` |
| round 2's bytes, kept | `HEAD:replays/candidates/stage-b-r2/9p2i` | nothing: the candidate copy at H |
| round 3's candidate copy before its promotion | `2eed2e92:replays/candidates/stage-b-r3/9p2i` | its own promotion, which moved the same bytes into `replays/samples/9p2i` |

## 3. What it demonstrates, with the command behind each claim

Every figure here is a page line or a command's stdout at H, listed in
section 8.3. Each era is read alone and never pooled across eras: **baseline-9** (its
three sets, pooled within the era as the pages publish them), **stage-b-r3** (the
shown 9-player set, its era's one set) and **stage-b-r2** (round 2, which owns
no committed set at H; its process rows are the scorecard's dated before column
for the shown set, and its census readings are round 3's record's round-2
column). Round 1 appears only in section 2. Each page passes its own `--check`
at H (section 8).

### 3.1 The process scorecard, era by era

`docs/process-scorecard.md`, checked by
`uv run python scripts/publish_process_scorecard.py --check` (exit 0 at H). Rows
8 and 9 read a role; both are reported and gate nothing.

| row | baseline-9, pooled | stage-b-r2, the before column | stage-b-r3, the shown set |
| --- | --- | --- | --- |
| 1 grounded decisions, EJECT (a floor) | 1589/1602 = 0.9919 | 407/410 = 0.9927 | 394/397 = 0.9924 |
| 1 grounded decisions, SKIP | 272/1183 = 0.2299 | 44/281 = 0.1566 | 47/305 = 0.1541 |
| 2 crew EJECTs naming someone other than the voter's top suspect | 147/1362 = 10.8% | 65/292 = 22.3% | 56/291 = 19.2% |
| 3 manufactured contradictions | 0/57 = 0.0000 (not evaluable 57) | 1/15 = 0.0667 (not evaluable 14) | 0/15 = 0.0000 (not evaluable 15) |
| 4 unexplained decisions | 12/2785 = 0.0043 | 11/691 = 0.0159 | 6/702 = 0.0085 |
| 6 rationale faithfulness, by token | 2307/2309 = 0.9991 | 580/580 = 1.0000 | 583/583 = 1.0000 |
| 7 agent-authored share | 2768/2785 = 0.9939 | 674/691 = 0.9754 | 692/702 = 0.9858 |
| 8 wrong-but-believable, reported and never penalised | 343/1602 = 0.2141 | 189/410 = 0.4610 | 177/397 = 0.4458 |
| 9 role-correct ejection, reported beside and never a gate | 288/321 = 0.8972 | 44/66 = 0.6667 | 46/61 = 0.7541 |

How each row reads, from the page's own definitions: row 1 counts ballots whose
citation resolves in the voter's own inputs and bears on its subject, and does
not test the cited line's truth; row 2 is a departure from the arithmetic the
engine handed the voter (its [top suspect](../docs/glossary.md#top-suspect-the-player-a-voters-own-suspicion-rates-highest)),
not a judgment of whether the departure was right; row 6 tests tokens, not
propositions; row 8 counts eject ballots against a crewmate that row 1 calls
grounded and that rest on no manufactured contradiction, without testing the
cited line's truth either.

### 3.2 The census: what a ballot held

`docs/gameplay-census.md`, checked by
`uv run python scripts/publish_gameplay_census.py --check` (exit 0 at H). A stated pair that
reconciles is a pair of places a player stated at the table that the station's
doors allow within the ticks between, or that the public regroup (the full
meeting reset, see the [glossary](../docs/glossary.md#regroup-the-full-meeting-reset))
falls between.

| cell | baseline-9, pooled | stage-b-r2 | stage-b-r3 |
| --- | --- | --- | --- |
| skips labelled as holding nothing | 764/1183 (64.6%) | 214/281 | 235/305 (77.0%) |
| holds-nothing skips whose own inputs name no living candidate | 0/764 (0.0%) | 0/214 | 0/235 (0.0%) |
| supported ejects whose cited line the route makes true | 818/842 (97.1%) | 278/281 | 245/248 (98.8%) |
| supported ejects whose cited line the route makes false | 24/842 (2.9%) | 3/281 | 3/248 (1.2%) |
| ejections charged on a stated pair that reconciles | 198/321 (61.7%) | 40/66 | 29/61 (47.5%) |
| the same, at meetings a kill witness opened | 8/13 (61.5%) | 7/12 | 7/13 (53.8%) |

The stage-b-r2 column is round 3's record's round-2 column, read from its own
tables (`audits/audit-2026-10-09-stage-b-r3.md`, sections 8.2 and 8.8), as
fractions, the form in which that record prints them.

### 3.3 The census: the genre

| cell | baseline-9, pooled | stage-b-r2 | stage-b-r3 |
| --- | --- | --- | --- |
| vent exits a crewmate saw | 251/427 (58.8%) | n/a | 7/70 (10.0%) |
| vent trips ended by a regroup | n/a | 47/140 | 47/140 (33.6%) |
| kills soon after a meeting | 107/302 (35.4%) | 0/109 | 0/106 (0.0%) |
| the opener speaks a second time | 0/531 (0.0%) | n/a | 90/119 (75.6%) |
| meetings opened by an impostor | 0/531 by construction | 0/117 by construction | 0/119 by construction |
| task wins in games with a sabotage in play | 2/23 (8.7%) | n/a | 17/19 (89.5%) |
| games the impostors won, reported beside | 77/250 (30.8%) | 24/50 | 17/50 (34.0%) |

The stage-b-r2 column is round 3's record's round-2 column
(`audits/audit-2026-10-09-stage-b-r3.md`, sections 8.2, 8.5 and 8.8), as
fractions, the form in which that record prints them. Three of its cells read
n/a because that record prints no round-2 value for them: it states
`vent_exits_seen_from_exit_room` rather than `vent_exits_seen_by_crew`,
`accused_opener_answers` rather than `opener_speaks_again`, and nothing for
`task_wins_with_sabotage_in_play`; this audit types no number its sources do
not print.

Each stage-b-r3 cell follows a recorded setting the census names on its page:
the impostor looks before leaving a vent and a vent exit is seen only from the
room surfaced into; the full reset regroups everyone after a meeting; the
accused opener gets one reply; impostors never report a body. The win split is
an outcome, reported beside the cells and gating nothing.

### 3.4 The game-shape profile, the shown set only

`docs/game-profile.md`, checked by
`uv run python scripts/publish_game_profile.py --check` (exit 0 at H); the
4-player set ships no profile. The
[profile](../docs/glossary.md#game-shape-profile-shelves-facets-and-the-tripwire)
describes each game by named moments (shelves) and plain facts (facets), with no
score and no rank.

- The tripwire "decided by a vote that held nothing": the governing readings
  trip no game on the shown set, and the loosest reading, any ejecting ballot so
  labelled, names one entry, (44, 0) as seed and meeting index.
- Shelves before the reveal: the reporter saw it happen, 13 games; double kill,
  7; slow burn, 15; suspicion moved, 16; a third round, 22 (command `shelves`
  prints
  `the_reporter_saw_it_happen 13; double_kill 7; slow_burn 15; suspicion_moved 16; a_third_round 22`
  from the served profile, and `docs/game-profile.md:76-80` holds the same).
- Behind the reveal, "decided without proof" splits by the ejected player's
  role: the table was right, 19 (21 ejections); wrong on what it held,
  14 (15 ejections). Both halves are reported and gate nothing, and "wrong on
  what it held" reads the grounding labels, not whether the cited line is true.

The card's Evidence read the profile on round 2's bytes at `225d2b77`; the
promotion regenerated it for round 3, and the figures above are those at H.

### 3.5 The route lines: offline reach, and round 3's reading of them

A [route line](../docs/glossary.md#route-line-what-the-doors-say-about-a-players-stated-places)
tells a voter, the same for every role, which of a candidate's stated changes of
room the station's doors or the public regroup allow; a candidate with no such
change has no line, so on round 3 671/702 (95.6%) of ballots carried one.

- Offline, on round 2's ballots rendered again with the lines on, the lines
  reach 31 of 40 misjudged cases (ejections charged on a stated pair that
  reconciles) and 7 of 7 at meetings a kill witness opened
  (`experiments/lab/report-route-lines-replay.md`, column r2), against the
  route-check replay's reference check, which reaches 29 of 40
  (`experiments/lab/report-route-check-replay.md`, column r2). On round 3's
  ballots, read off the blocks actually served, the lines reach 26 of 29, and
  7 of 7 at witness meetings, where the reference check reaches 25 of 29 (column
  r3 of each report). The route-lines report's own words: "Reaching is showing a
  line, not changing a vote."
- Round 3's record reads the misjudged count at 29 against round 2's 40, and the
  census agrees: 26/29 (89.7%) of round 3's misjudged ejections had a route line
  shown to an ejecting voter.
- The orchestrator's reading of them, labelled as such in round 3's record
  (section 11): held kill witnesses ejected read 6 of 14 against round 2's
  5 of 14, with the witness's line served in all six, "so the route line reached
  the witness meetings and did not change their outcome".

### 3.6 Round 3's column, as its record states it

Round 3's record (`audits/audit-2026-10-09-stage-b-r3.md`) reads every
conformance cell at 0, the impostor win share at 17/50 = 0.34 (0.22-0.48),
inside its band, 0.20-0.60, and the pre-registered step rule's line,
verbatim:

```
step rule: names the era-keyed promotion of round 3 as the shown set, the owner's to take or override (Conf. misses 0; impostor wins 17/50; M 29 against round 2's 40)
```

The rule names the promotion; the step itself was the orchestrator's, under the
owner's ruling of 2026-10-09, verbatim: "I will let this session, as the
orchestrator, decide about promoting round 3. Keep what I want for the project
in mind. I lean towards wanting to promote round 3, but if there is an issue you
find with recording, or think it is really a step down in terms of gameplay, you
can make the decision to keep round 2." (decision memo section 8.8). The
orchestrator took the promotion and wrote its readings into the record's section
11, a reading labelled as the orchestrator's, with a dated amendment there that
quotes the wrong-but-believable row as reported and not as a criterion; the
promotion itself is that record's section 12.

### 3.7 What the public demo features

The featured strip (`FEATURED_GAMES`, `frontend/src/components/ReplayPicker.tsx`)
holds 9-player seeds 19 and 14 and three 4-player games. Count-only, the
featured 9-player seeds against the profile's "wrong on what it held" seeds:
`featured 9p2i 2; wrong on what it held 14; both 0` (command `featured`). So the
public demo features no wrong-but-believable ejection, which is the
orchestrator's default under the owner's delegation of 2026-10-09 (decision memo
section 8.9), and the front door's strip guard fails by name on any featured
crewmate ejection
(`tests/api/test_sets.py::test_the_strip_guard_reads_the_pickers_featured_list`).

### 3.8 The owner's goal, read count-only

The direction of 2026-09-19 states the goal: "an agent's vote or skip must rest
on data the agent actually holds, true or false, and a wrong decision on
believable data is better than a right one on none." On the shown set:

- Whether a decision names its basis: 394/397 = 0.9924 of ejects and
  47/305 = 0.1541 of skips carry a grounded citation, 235/305 (77.0%) of skips
  say instead that they hold nothing, and 6/702 = 0.0085 of ballots are
  unexplained, an eject whose citation does not resolve or a skip that names no
  player.
- What a skip held: 0/235 (0.0%) of the holds-nothing skips had no living
  candidate named in their own inputs.
- The data is worth following: 245/248 (98.8%) of the checkable cited lines are
  true to the engine's route, and 3/248 (1.2%) false.
- The agent's call is the recorded call: 692/702 = 0.9858.
- Wrong on believable data, the game working: 177/397 = 0.4458, reported and
  never penalised.

## 4. What it does not demonstrate

**Role-correctness, reported and never a gate.** Role-correct ejection on the
shown set, 46/61 = 0.7541, is reported beside the process rows and gates
nothing. Its mechanism is `ProcessScorecard._role_correctness_stays_demoted`
(`eval/process_scorecard.py:623`), and round 3's pre-registered step rule names
no role-reading flag among its conditions
(`tasks/work/stage-b-record-r3.md:249-255`): with the reporter flag forced on or
the role-correct count edited, its line was byte-identical (round 3's record,
section 1.11). Nothing in this audit recommends pushing an agent toward the
correct answer.

**One recording per round.** Each round recorded seeds 0-49 once: each round
record's gate ran `--expected-seeds 0-49` and read 50/50 games at game over
(`audits/audit-2026-09-27-stage-b-r1.md:943`,
`audits/audit-2026-10-01-stage-b-r2.md:1178`,
`audits/audit-2026-10-09-stage-b-r3.md:1695`). Hosted generation is not
reproducible, so no difference between rounds is claimed as real, and every
Wilson interval in the records is descriptive: round 2's impostor win share,
24/50 = 0.48 (0.35-0.61), and round 3's, 17/50 = 0.34 (0.22-0.48), overlap, as
round 3's record says in its limitations.

**The 27B model's own route arithmetic.** The route field hands the model the
map's reading of the stated places, so the model is not asked to do the
arithmetic; the lab measures only the field's reach, offline: "Reaching is
showing a line, not changing a vote" (`experiments/lab/report-route-lines-replay.md`).
The diagnosis of 2026-10-02 had an investigator's headline that the failure was
route arithmetic, "a limit of the 27B model"; its refuter's verdict, which the
diagnosis accepts: "The descriptive counts hold, but the causal headline does
not." (`tasks/diagnosis-2026-10-02/README.md:374-379`). Round 3 is one recording,
so whether a served line changes a vote is read once and not established.

**The reporter trap's standing.** The census reports, per era, reporter seats
ejected without vent proof against other crewmate seats ejected without it:
baseline-9 29/271 (10.7%) against 2/703 (0.3%), stage-b-r2 17/93 against 5/291
(round 3's record, section 8.8), stage-b-r3 10/95 (10.5%) against 5/302
(1.7%). The re-keyed flag's bar, flagged above twice round 2's relative rate
(21.28, decision memo section 8.7), gates nothing and the step rule never read
it; round 3 read it at 6.4, not flagged. While impostor self-report stays
off, every reporter is a crewmate: no meeting was opened by an impostor
(0/119 by construction), so any reporter line reads a role.

**The ML program, on hold.** The owner's ruling 12 of 2026-09-24, verbatim:
"Hold off on ML as D suggests until gameplay is finished." (decision memo
section 0.1). Any reopening first re-prices the crew terms of the objective
role-blind, under the precondition dated 2026-10-06 in `training/README.md`
section 7. The corpus's FROZEN lines stand
(`replays/ml_corpus/9p2i/MANIFEST.md:163`, `replays/ml_corpus/4p1i/MANIFEST.md:63`),
and `uv run python scripts/verify_ml_evidence.py`, offline and never with
`--complete`, reads `FAIL 0` at H.

**General social deduction.** "This demonstrates processing of certified facts
and deception, **not general social deduction**." (`README.md:33`): of the shown
set's role-correct ejections, a number reported and gating nothing, 24 of 46
follow certified vent evidence.

## 5. The doctrine and its rulings, by section

| document | path | sections used | standing |
| --- | --- | --- | --- |
| The direction of 2026-09-19 | `tasks/direction-2026-09-19-process-over-outcome.md` | `## 1.`; `## 7.`; `## 8.`; `## 12.`; `Addendum, 2026-09-20.`; `Addendum, 2026-09-24`; `Addendum, 2026-10-01`; `Addendum, 2026-10-06` | the owner's goal and the rulings of 2026-09-19, with four dated addenda |
| The Stage-B decision memo | `tasks/decision-2026-09-24-stage-b-wave.md` | `## 0.`; `## 1.`; `## 2.`; `## 3.`; `## 4.`; `## 5.`; `## 6.`; `## 7.`; `## 8.`; `### 8.1`; `### 8.2`; `### 8.3`; `### 8.4`; `### 8.5`; `### 8.6`; `### 8.7`; `### 8.8`; `### 8.9`; `**Amendment of 2026-10-09`; `**Closure (2026-10-09).**`; `**Orchestrator default of 2026-10-09` | the owner's rulings verbatim and dated; the orchestrator's readings, labelled |
| The diagnosis after round 2 | `tasks/diagnosis-2026-10-02/README.md` | `## Part 1.`; `## Part 2.`; `## Part 3.`; `## Part 4.` | the orchestrator's synthesis with its refuters' verdicts |
| The game's shape | `docs/game-shape.md` | `## Venting is visible`; `## Impostors never report`; `## Actions resolve in player-id order`; `## Meetings pause the world`; `## Crewmates see one room` | the rules as built |
| The house rules | `AGENTS.md` | `## Load-bearing rules`; `## Craft rules` | standing |
| The baselines memo | baselines-2026-10-03/baselines-memo.md, kept with the session's records outside the tree, read-only on `cf3341ab` | Part 2's classes; Part 3.1's RETIRE and DEMOTE rows; Part 4 D7, D8, D9, D12 to D18, D14 with D14-T1 to T3 | advisory; it decides nothing and is the source of no figure here |
| The rubric design memo | rubric-design-2026-10-06/rubric-design-memo.md, kept with the session's records outside the tree, read-only on `76270d6c` | Part 4 | advisory; it decides nothing and is the source of no figure here |

What each section carries, as this audit relies on it:

- **The direction.** Section 1 restates the goal as six testable properties
  (section 3.8 reads them). Section 7: "The layer labels; it never rewrites.",
  "Nothing pushes the agent toward the correct answer.", and a wrong decision on
  believable data is "the game working". Section 8's yardstick: role-correct
  ejection is "reported beside, never a gate". Section 12 records the owner's
  acceptance of its decisions on 2026-09-19, and the addenda of 2026-09-20,
  2026-09-24, 2026-10-01 and 2026-10-06 date the re-record's sizing, the
  Stage-B wave with its partial record, round 1's assessment and the re-keyed
  reporter line.
- **The decision memo.** Section 0.1 holds the owner's rulings of 2026-09-24
  verbatim, ruling 12 among them; section 1 the partial-record mechanism;
  sections 2 to 6 the cards, plans and amendment the wave ran on; section 7 the
  owner's ruling of 2026-10-01, verbatim "Merge.  Adopt all 7 non-balance arms.
  And run a balance round"; section 8.1 the owner's eight rulings of
  2026-10-06, verbatim; section 8.7 the ruling of 2026-10-09, verbatim "Apply all
  five redundancy removals and confirm the five points as proposed"; section 8.8
  the delegated step (quoted in section 3.6); section 8.9 the ruling of
  2026-10-09, verbatim "Merge both when verified and retire the memo's D14
  list", its amendment of the same day, verbatim "Keep the comparison records",
  and the orchestrator's two defaults (no wrong-but-believable ejection featured
  on the strip; the README leading with the process rows). The two dated lines
  after the amendment are the extractor card's closure (2026-10-09) and the
  orchestrator's default for the frozen before column (2026-10-09), each the
  orchestrator's.
- **The diagnosis.** Parts 1 to 4: the state after round 2, the refuted causal
  headline on route arithmetic (section 4 here), the recommendations as cards,
  and what was left open for the owner.
- **The game's shape and the house rules.** The five shape facts of section 1;
  AGENTS.md's load-bearing rules 1 to 5 and craft rules 1 to 7, among them that
  claims name their enforcing mechanism and that numbers reproduce from
  committed evidence (craft rule 5), which this audit's section 8 serves.
- **The two advisory memos.** The baselines memo classed every measure against
  the direction and posed the open decisions D1 to D18 that the owner then ruled
  on in part (decision memo section 8); the rubric design memo recommended the
  game-shape profile the owner adopted on 2026-10-06. Both are advisory, outside
  the tree, and cited the way the decision memo cites them.

## 6. The work that reached `main`

B is `a3b42fd4`. From the direction's commit `0755c25d` to B, `main` took 37
first-parent merges (command `ledger-count` prints `first-parent merges 37`). A
read-only
`gh pr list --repo dkdan10/AiLibi --base main --state merged --search 'merged:>=2026-09-19'`
at dispatch names the same 37 pull requests, each with a merge commit, so no
row is a fast-forward. The date is the merge commit's author date. Between merges, two kinds of
commit landed on `main` without a pull request: `docs:` commits, which AGENTS.md
allows for planning and contract documents, and the orchestrator's `card:`
flips, which set a merged card's Status line and the task index's inventory
sentence, the two lines the finish-wave cards reserve to the orchestrator on
`main`. This audit cites two groups of them: the extractor card's
closure, two `docs:` commits (`a331ab90`, then `97549508`); and the
orchestrator's five commits of the finish wave, one after each of its four
merges and the inventory stamp after the last, each printed with its subject
by command `finish-commits`:
`3d32d31e card: flip stage-b-record-r3 to done after its merge`,
`2eed2e92 card: flip retire-era-locked-pins to done after its merge`,
`76d1c826 card: flip promote-round-3 to done after its merge`,
`49498b0b card: flip front-door-process-first to done after its merge` and
`a3b42fd4 docs: stamp the task inventory with the day of its last flip`.

| pull request | card | merge commit | date | how |
| --- | --- | --- | --- | --- |
| #473 | `tasks/work/close-deduction-candidate-evaluation.md` | `c0258333` | 2026-09-20 | merge commit |
| #471 | `tasks/work/spectator-tour-and-alternatives.md` | `f9bf1f1c` | 2026-09-20 | merge commit |
| #472 | `tasks/work/process-scorecard.md` | `cdefb7a6` | 2026-09-20 | merge commit |
| #474 | `tasks/work/alibi-as-route.md` | `038a22a5` | 2026-09-20 | merge commit |
| #475 | `tasks/work/grounded-skip-and-guard-labels.md` | `0a1100ea` | 2026-09-21 | merge commit |
| #476 | `tasks/work/ballot-weighing-channel.md` | `39a568c6` | 2026-09-22 | merge commit |
| #477 | `tasks/work/process-rerecord.md` | `acf6c604` | 2026-09-23 | merge commit |
| #480 | `tasks/work/committed-channel-rederivation.md` | `ff5e177a` | 2026-09-23 | merge commit |
| #479 | `tasks/work/report-fog-and-counterfactual-freeze.md` | `efadfe06` | 2026-09-23 | merge commit |
| #481 | `tasks/work/ml-reground-baseline-9.md` | `df129a49` | 2026-09-24 | merge commit |
| #482 | `tasks/work/docs-truth-typed-trigger.md` | `7f2890f0` | 2026-09-25 | merge commit |
| #484 | `tasks/work/stage-b-arm-spine.md` | `8df69e15` | 2026-09-25 | merge commit |
| #483 | `tasks/work/gameplay-census.md` | `bdfa5b19` | 2026-09-26 | merge commit |
| #485 | `tasks/work/vent-witness-physical.md` | `fb9d2e31` | 2026-09-26 | merge commit |
| #486 | `tasks/work/stage-b-readers.md` | `e22b54e6` | 2026-09-26 | merge commit |
| #487 | `tasks/work/stage-b-record-plumbing.md` | `f98bfae9` | 2026-09-26 | merge commit |
| #489 | `tasks/work/vent-look-and-wait.md` | `f83050c6` | 2026-09-27 | merge commit |
| #488 | `tasks/work/report-body-handle.md` | `9741a20b` | 2026-09-27 | merge commit |
| #490 | `tasks/work/meeting-reset-coherence.md` | `4b1e9a01` | 2026-09-27 | merge commit |
| #491 | `tasks/work/ballot-kill-row-and-impostor-strategy.md` | `f937dfaa` | 2026-09-27 | merge commit |
| #492 | `tasks/work/stage-b-record-r1.md` | `cd1a8454` | 2026-10-01 | merge commit |
| #493 | `tasks/work/kill-cooldown-arm.md` | `e87403b7` | 2026-10-01 | merge commit |
| #494 | `tasks/work/stage-b-record-r2.md` | `d41c9006` | 2026-10-02 | merge commit |
| #495 | `tasks/work/promote-round-2.md` | `0e67f42a` | 2026-10-02 | merge commit |
| #496 | `tasks/work/spectator-tour-round-2.md` | `59bbd1be` | 2026-10-02 | merge commit |
| #497 | `tasks/work/census-reporter-base-rate.md` | `a0fdb570` | 2026-10-03 | merge commit |
| #499 | `tasks/work/route-check-replay.md` | `cf3341ab` | 2026-10-03 | merge commit |
| #498 | `tasks/work/post-promotion-follow-through.md` | `76270d6c` | 2026-10-06 | merge commit |
| #500 | `tasks/work/crew-idle-policy-lab.md` | `88227569` | 2026-10-06 | merge commit |
| #501 | `tasks/work/route-lines-field.md` | `47bee59a` | 2026-10-06 | merge commit |
| #503 | `tasks/work/census-spy-cold-cache.md` | `e0bf4d92` | 2026-10-06 | merge commit |
| #502 | `tasks/work/census-held-data-cells.md` | `9caac0cf` | 2026-10-07 | merge commit |
| #504 | `tasks/work/rubric-v2-profile.md` | `cee6d2f5` | 2026-10-09 | merge commit |
| #505 | `tasks/work/stage-b-record-r3.md` | `c71ea63e` | 2026-10-09 | merge commit |
| #506 | `tasks/work/retire-era-locked-pins.md` | `84a4509c` | 2026-10-09 | merge commit |
| #507 | `tasks/work/promote-round-3.md` | `54dff069` | 2026-10-09 | merge commit |
| #508 | `tasks/work/front-door-process-first.md` | `4a08f2aa` | 2026-10-10 | merge commit |

The stated residual is this audit's own pull request: it merges after B and is
not a row.

## 7. Open items for a next owner

### 7.1 The open items, each with who decides it

| open item | state at H | who decides | source | anchor |
| --- | --- | --- | --- | --- |
| `extract_gameplay_facts` | The gameplay-facts extractor keeps refusing the shown era by name (`refuse_experiment_settings`); its cross-era rows left with the retirement, and the card that would have widened it closed unexecuted. An audit of the shown era starts from the census instead. | the owner, if a card for the extractor is wanted | `audits/workflows/extract_gameplay_facts.py:184` | `def refuse_experiment_settings(` |
| `self-report` | Impostor self-report stays off: impostors never report a body, so every reporter is a crewmate. Held through round 3 under the owner's rulings 5 to 7 of 2026-10-06, verbatim "Sounds good", as the orchestrator reads them; a revisit would be a round of its own. | the owner | `tasks/decision-2026-09-24-stage-b-wave.md:1460` | `R6 is kept through round 3` |
| `impostor_roll_call` | A live substrate toggle, default off in every committed recording; selectable. | the owner | `docs/architecture.md:113` | `impostor_roll_call` |
| `reporter_reasoning` | A live toggle, default off; one of the three Wave-2 toggles bound to D15. | the owner | `docs/architecture.md:113` | `reporter_reasoning` |
| `corroboration_discipline` | A live toggle, default off; bound to D15. | the owner | `docs/architecture.md:113` | `corroboration_discipline` |
| `testimony_shapes` | A live toggle, default off; bound to D15. | the owner | `docs/architecture.md:114` | `testimony_shapes` |
| `temporal_observations` | A live toggle, default off; its full repair stays unadopted. | the owner | `docs/architecture.md:114` | `temporal_observations` |
| `evidence_reasoning_version` | Versions 1 and 2 stay selectable and default off, with version 1's four defects on its path; no committed config sets it (`git grep` exits 1). | the owner | `orchestrator/experiment_config.py:52` | `evidence_reasoning_version: Literal[1, 2]` |
| `baseline 10` | Reserved for the full re-record that re-freezes the corpus; not run. | the owner (D12, and the ML hold) | `eval/eras.py:24` | `baseline 10 is reserved for the full re-record that re-freezes the corpus` |
| `retire-temporal-evidence-v1` | Status `ready` at B and at H, blocked on an adopting record for evidence reasoning version 2 that no round took; an owner confirmation point under D15, "wait" or "lift the exclusion". | the owner (D15) | `tasks/decision-2026-09-24-stage-b-wave.md:1626` | `and blocked: whether` |
| `D9` | Whether row 1's skip cell credits an explicit "none held": undecided. | the owner | `tasks/decision-2026-09-24-stage-b-wave.md:1498` | `D9, D12, D13 and D15 to D18` |
| `D12` | The before column's form: taken in the grow form by the orchestrator's default of 2026-10-09 when round 3 was promoted. The memo gave the owner a window, "the owner may replace it with a ruling at any time before that card merges" (`tasks/decision-2026-09-24-stage-b-wave.md:1633-1634`), which closed when the promotion merged as `54dff069`; as the orchestrator reads it, a later owner ruling could still replace the form, by a new card. An owner confirmation point; baseline 10 and the ladder's frame stay undecided. | the owner | `tasks/decision-2026-09-24-stage-b-wave.md:1629` | `Orchestrator default of 2026-10-09 for the frozen before column (baselines memo D12)` |
| `D13` | The watchability floors and the stage block: undecided; the retirement kept them as the frozen referee's. | the owner | `tasks/decision-2026-09-24-stage-b-wave.md:1498` | `D9, D12, D13 and D15 to D18` |
| `D15` | The routed decision of the phase-21 close, the three Wave-2 toggles and the held temporal card: undecided. | the owner | `tasks/decision-2026-09-24-stage-b-wave.md:1627` | `it waits or closes is the owner's D15 word` |
| `D16` | The status of the balance pair (the kept vent exit and the six-tick cooldown): undecided; round 3 declared it as round 2 did. | the owner | `tasks/decision-2026-09-24-stage-b-wave.md:1499` | `its status (D16) does not change here` |
| `D17` | Whether the meeting-rate floor stays a hard validity check: undecided. | the owner | `tasks/decision-2026-09-24-stage-b-wave.md:1498` | `D9, D12, D13 and D15 to D18` |
| `D18` | Whether the betrayal check and the railroad tripwire stay role-conditioned gates: undecided. | the owner | `tasks/decision-2026-09-24-stage-b-wave.md:1498` | `D9, D12, D13 and D15 to D18` |
| `D8-L` | The local dashboard's "gate" vocabulary and order, and the published "vote gate" badge: held by the front-door card, no line written. | the owner | `tasks/work/front-door-process-first.md:30` | `D8-L, the local Tournament dashboard's "gate" vocabulary and order` |
| `D8.1` | The belief panel's Error layer and whether the ballot badge follows: held, no line written. | the owner | `tasks/work/front-door-process-first.md:31` | `D8.1, the belief panel's Error layer` |
| `D9-L` | Whether a skip is read "by the line" or "by the label": held, no line written. | the owner | `tasks/work/front-door-process-first.md:32` | `D9-L, whether a skip is read "by the line" or "by the label"` |
| `D7` | No wrong-but-believable ejection is featured on the strip: the orchestrator's default under the delegation, confirmable; whether one is ever featured stays the owner's. | the owner | `tasks/decision-2026-09-24-stage-b-wave.md:1620` | `no wrong-but-believable ejection is featured on the strip (D7, the current state)` |
| `D14` | The residue the retirement card's Results name: the evidence-mechanism anchors and the frozen referee's floors, classed and kept; the phase-21 counterfactual's test, never written there, with the counterfactual and its pins left by its Constraints to D15 (`tasks/work/retire-era-locked-pins.md:282`); round 1's directory, kept by the owner's amendment. | the owner | `tasks/work/retire-era-locked-pins.md:582` | `classed and kept: the mechanism anchors` |

### 7.2 The held cards, read at B and not written

- `tasks/work/rubric-extractor-era.md`: Status `done` at B. Its last commit at
  B is the orchestrator's closure,
  `97549508 docs: apply the extractor card's closure span correctly`, which
  `a331ab90` opened; the closure is an ancestor of the retirement's merge
  `84a4509c`, so it landed before the retirement merged (command `closure`
  prints both, the ancestry as `ancestor exit 0`).
- `tasks/work/retire-temporal-evidence-v1.md`: Status `ready` at B and at H, and
  no dated owner word on D15 arrived before B. No committed experiment config
  under `replays/` sets `evidence_reasoning_version` (command `erv-configs`
  prints `configs exit 1`).

### 7.3 The owner's confirmation points, in one place

- **D15: close `retire-temporal-evidence-v1` unexecuted, or let it wait.** The
  orchestrator's reading, labelled as such: close it unexecuted, because no
  round took an evidence reasoning version and no planned record adopts
  version 2; the orchestrator holds its prepared closure text outside the tree.
  The word is the owner's.
- **D8-L, D8.1 and D9-L**, the dashboard, belief-panel and skip-reading halves
  the front-door card held without writing a line of them.
- **D7's default** (no wrong-but-believable ejection featured) and **D12's grow
  form** for the before column, both taken as the orchestrator's defaults under
  the owner's delegation of 2026-10-09 (decision memo section 8.9), both owner
  confirmation points. D7's default holds "unless the owner says otherwise"
  (`tasks/decision-2026-09-24-stage-b-wave.md:1619-1620`). For D12 the memo
  stated a window, "the owner may replace it with a ruling at any time before
  that card merges" (`tasks/decision-2026-09-24-stage-b-wave.md:1633-1634`);
  that window closed when the promotion merged as `54dff069`, and, as the
  orchestrator reads it, a later owner ruling could still replace the form by
  a new card.
- **D9, D13, D16, D17 and D18**, which decision memo section 8.5 leaves
  undecided; and D12's remainder, baseline 10 and the ladder's frame.
- **A full re-record for baseline 10**, which would re-freeze the corpus and
  force the ML refit the hold defers.

### 7.4 Defects found on the way, filed and not fixed here

Each is filed with the place it lives and the command that shows it at H;
nothing here edits the file a finding names.

| finding | what it is | where | showing command |
| --- | --- | --- | --- |
| 1 | The architecture page says "Four import-linter contracts"; `.importlinter` holds five, and `uv run lint-imports` prints `Contracts: 5 kept, 0 broken.` (`four-contracts lines 1`) | `docs/architecture.md:89` | `arch-four`, `lint` |
| 2 | Round 3's lab column is pinned at `60059688`, whose tree of `replays/samples/9p2i` holds `results-game-profile.json` (`profile in pinned tree 1`). The census's proof that a pinned column's recordings are HEAD's rebuilds that tree from HEAD's files when the pinned commit is not in the clone, as in CI's checkout, whose `actions/checkout` steps set no `fetch-depth` and so clone one commit deep (`ci fetch-depth lines 0`); a later regeneration of the profile leaves no subset of HEAD's files that rebuilds it, so the proof fails. The test is `tests/eval/test_gameplay_census.py::test_the_route_check_columns_read_the_recordings_now_at_head`, in the census suite rather than `tests/experiments`. | `tests/eval/test_gameplay_census.py:10391` | `pinned-profile`, `ci-depth` |
| 3 | The verdict check accepts any recorded innocent-ejection count in a wrongful-ejection sentence: with the README's 46 and 42 swapped it exits 0 (`swapped exit 0`), while 46 moved to 47 alone exits 1 (`moved exit 1`). | `scripts/check_doc_facts.py:4359` | `slow-swap-46-42`, `slow-move-46-47` |
| 4 | No doc-facts check holds the README grounded row's floor label: removed, the checker exits 0 (`no floor label exit 0`). | `README.md:23` | `slow-floor-label` |
| 5 | No doc-facts check holds the order among the four process rows: two swapped, the checker exits 0 (`rows swapped exit 0`). | `README.md:24` | `slow-row-order` |
| 6 | No doc-facts check holds the previously-shown-recording sentence: deleted, the checker exits 0 (`no before sentence exit 0`). | `README.md:17` | `slow-before-sentence` |
| 7 | The README and reading-guide disclosure of the body handle on the shown set has no enforcing check: both counts moved by one, the checker exits 0 (`handle moved exit 0`). | `README.md:51` | `slow-body-handle` |
| 8 | The ML paragraph's 50-games figure is unchecked: moved to 60, the checker exits 0 (`games moved exit 0`). | `README.md:39` | `slow-ml-50-games` |
| 9 | The four process rows show no record date in the "Recorded on" column, in the README and in the reading guide (`dated process rows 0`, `dated guide rows 0`). | `README.md:23` | `process-row-dates` |
| 10 | Commits carrying a Co-Authored-By line other than the Fable line the later cards name as the house line, never rewritten, some recorded as deviations in their cards: eight pull requests, counted per pull request by command (`#507 13`, `#495 12`, `#484 6`, `#477 21`, `#483 4`, `#498 4`, `#502 9`, `#504 1`). The dispatch named the first three. | `tasks/work/promote-round-3.md:1068` | `trailers` |
| 11 | The promotion card's Results says its wider scan "finds no other report size" and names two hits; the command as quoted lists nine lines at H (`wide-scan hits 9`). | `tasks/work/promote-round-3.md:1040` | `wide-scan` |
| 12 | The promotion card's build-decisions bullet says the commits from `d9c3ada3` on carry the Opus line; the two commits after `9de107b9` carry the Fable line (`fable after 9de107b9 2`), so the bullet is stale at the card's head. | `tasks/work/promote-round-3.md:696` | `fable-after` |
| 13 | The fold-reading Hypothesis case of the profile tests was seen to fail once under xdist with "DID NOT RAISE", as the orchestrator's dispatch reports it from a finish-wave review (no record of it is in the tree). Its planted proof expects a random search to find a counterexample, so a search that finds none passes the property and the case fails. At H it passes alone under Hypothesis seed 0 (`1 passed`) and fails under seed 58 with "DID NOT RAISE" on every run (`seed 58 DID NOT RAISE lines 1`), so the case is seed-dependent wherever it runs, and one unseeded run inside this audit's own check printed no pass; the card's Results give the local seed counts. | `tests/eval/test_game_profile.py:1022` | `flaky-alone`, `flaky-seed` |
| 14 | This card's Validation expects `git grep -n _cross_era_trajectory` to exit 1 once the retirement merged; at H the function is gone from every Python file (`code hits exit 1`), but the bare grep exits 0 on the documents that name it, task cards and this audit among them (`card hits exit 0`). | `tasks/work/close-audit-finalized-state.md:419` | `cross-era` |
| 15 | The ladder-tip check reads the phrase with a literal space, so a "ladder tip" wrapped across a line is never scanned: the index holds one such sentence, round 3's row (`wrapped ladder-tip phrases 1`), and with its baseline 9 made baseline 10 the checker exits 0 (`wrapped tip exit 0`). This audit's own row keeps the phrase on one line, where the same edit exits 1. | `scripts/check_doc_facts.py:356` | `wrapped-tips`, `slow-wrapped-tip` |
| 16 | The offline reasoning-evidence scorecard builds one fixed inventory of all four committed sets, the shown set's era and baseline 9's together, and folds them into one block of historical diagnostics without reading the era registry (`era registry reads 0`, `inventory sets 4`). So the registry's docstring, "Every instrument that walks more than one committed set ... read it" (`eval/eras.py:11-15`), and round 3's record, "No instrument pools across eras." (`audits/audit-2026-10-09-stage-b-r3.md:2312`), claim more than the tree holds; neither is edited here. Found by the pull request's automated review. | `eval/reasoning_evidence.py:344` | `reasoning-pool` |

## 8. Reproduction

Every number in sections 0 to 7 has a row below, with its command or its
`path:line` at H, count-only. Commands run from the repository root in a bare
shell (`env | grep -c '^AILIBI_'` prints 0) after `uv sync --frozen`; none prints
a rendered prompt, transcript text or a seed-band prefix, and none calls a
provider. A command whose id starts with `slow-` takes about a minute; those a
finding names archive the head into a temporary directory, edit one document
there, run the doc-facts checker on that copy, print its exit code and delete
the copy.

### 8.1 Commands

```
scorecard-check: uv run python scripts/publish_process_scorecard.py --check
census-check: uv run python scripts/publish_gameplay_census.py --check
profile-check: uv run python scripts/publish_game_profile.py --check
slow-route-check: uv run python -m experiments.lab.route_check_replay --check
slow-route-lines: uv run python -m experiments.lab.route_lines_replay --check
lint: uv run lint-imports
verify-samples: bash scripts/verify_samples.sh
vme: uv run python scripts/verify_ml_evidence.py
engine-test: uv run pytest -q -p no:cacheprovider tests/orchestrator/test_game.py::test_headless_game_replay_is_byte_identical_for_same_seed
tactical-imports: test -z "$(git grep -l -E '^(from|import) llm' -- agents/tactical)"
firewall-test: uv run pytest -q -p no:cacheprovider tests/test_firewall.py::test_import_linter_reports_a_planted_agents_to_engine_route
labels-test: uv run pytest -q -p no:cacheprovider tests/meetings/test_grounding_label.py::TestTheTallyNeverReadsTheLabel
census-test: uv run pytest -q -p no:cacheprovider tests/eval/test_gameplay_census.py::test_every_guarded_cell_has_a_planted_pair
eras-test: uv run pytest -q -p no:cacheprovider tests/eval/test_eras.py
recorder-test: uv run pytest -q -p no:cacheprovider tests/scripts/test_refresh_samples.py::test_an_era_refusal_names_the_set_and_the_declared_file_it_found
citations-test: uv run pytest -q -p no:cacheprovider tests/eval/test_vj_instruments.py::test_citation_counts_split_valid_from_dangling
role-test: uv run pytest -q -p no:cacheprovider tests/eval/test_process_scorecard.py::test_the_role_correct_row_is_labelled_as_no_gate
era-ladder: uv run python -c "from eval import eras; print('tip', eras.LADDER_TIP_ERA.id); [print(s.path, s.era.id, s.era.record, s.era.recorded_on, s.era.declared_config) for s in eras.COMMITTED_SETS]"
candidates: git ls-files replays/candidates | cut -d/ -f1-3 | sort -u
ledger-count: echo "first-parent merges $(git log --first-parent --merges --oneline 0755c25d..a3b42fd4 | wc -l | tr -d ' ')"
featured: uv run python -c "import json, re; j = json.load(open('replays/samples/9p2i/results-game-profile.json')); w = {m['seed'] for m in j['reveal']['decided_without_proof']['wrong']['members']}; f = {int(s) for s in re.findall(r'set: .9p2i.,\s*seed: (\d+)', open('frontend/src/components/ReplayPicker.tsx').read())}; print(f'featured 9p2i {len(f)}; wrong on what it held {len(w)}; both {len(f & w)}')"
finish-commits: git log --no-walk=unsorted --format='%h %s' 3d32d31e 2eed2e92 76d1c826 49498b0b a3b42fd4
closure: git log -1 --format='%h %s' a3b42fd4 -- tasks/work/rubric-extractor-era.md; git merge-base --is-ancestor 97549508 84a4509c; echo "ancestor exit $?"
erv-configs: git grep -c evidence_reasoning_version -- 'replays/**/experiment-config.json'; echo "configs exit $?"
arch-four: echo "four-contracts lines $(grep -c 'Four import-linter contracts' docs/architecture.md)"
pinned-profile: echo "profile in pinned tree $(git ls-tree --name-only 60059688:replays/samples/9p2i | grep -c results-game-profile.json)"
ci-depth: echo "ci fetch-depth lines $(grep -c fetch-depth .github/workflows/ci.yml)"
slow-swap-46-42: d=$(mktemp -d) && git archive HEAD | tar -x -C "$d" && perl -0777 -pi -e 's/with 46 innocent ejections\. Nor did baseline 9: 43 of 85 = 0\.5059 with 42 /with 42 innocent ejections. Nor did baseline 9: 43 of 85 = 0.5059 with 46 / or die' "$d/README.md" && uv run python scripts/check_doc_facts.py --repo-root "$d" >/dev/null 2>&1; echo "swapped exit $?"; rm -rf "$d"
slow-move-46-47: d=$(mktemp -d) && git archive HEAD | tar -x -C "$d" && perl -0777 -pi -e 's/with 46 innocent/with 47 innocent/ or die' "$d/README.md" && uv run python scripts/check_doc_facts.py --repo-root "$d" >/dev/null 2>&1; echo "moved exit $?"; rm -rf "$d"
slow-floor-label: d=$(mktemp -d) && git archive HEAD | tar -x -C "$d" && perl -0777 -pi -e 's/; a floor: the ballot asks every eject to cite// or die' "$d/README.md" && uv run python scripts/check_doc_facts.py --repo-root "$d" >/dev/null 2>&1; echo "no floor label exit $?"; rm -rf "$d"
slow-row-order: d=$(mktemp -d) && git archive HEAD | tar -x -C "$d" && perl -0777 -pi -e 's/(\| Crew eject ballots naming[^\n]*\n)(\| Ballots with no stated reason[^\n]*\n)/$2$1/ or die' "$d/README.md" && uv run python scripts/check_doc_facts.py --repo-root "$d" >/dev/null 2>&1; echo "rows swapped exit $?"; rm -rf "$d"
slow-before-sentence: d=$(mktemp -d) && git archive HEAD | tar -x -C "$d" && perl -0777 -pi -e 's/ Each before cell is what that set.s previously shown recording read\.// or die' "$d/README.md" && uv run python scripts/check_doc_facts.py --repo-root "$d" >/dev/null 2>&1; echo "no before sentence exit $?"; rm -rf "$d"
slow-body-handle: d=$(mktemp -d) && git archive HEAD | tar -x -C "$d" && perl -0777 -pi -e 's/\(0 of 115\)/(0 of 114)/ or die' "$d/README.md" && perl -0777 -pi -e 's/\(body handle 0 of\n115\)/(body handle 0 of\n114)/ or die' "$d/docs/reading-guide.md" && uv run python scripts/check_doc_facts.py --repo-root "$d" >/dev/null 2>&1; echo "handle moved exit $?"; rm -rf "$d"
slow-ml-50-games: d=$(mktemp -d) && git archive HEAD | tar -x -C "$d" && perl -0777 -pi -e 's/not significant at 50 games/not significant at 60 games/ or die' "$d/README.md" && uv run python scripts/check_doc_facts.py --repo-root "$d" >/dev/null 2>&1; echo "games moved exit $?"; rm -rf "$d"
process-row-dates: echo "dated process rows $(sed -n 23,26p README.md | grep -cE '20[0-9]{2}-[0-9]{2}-[0-9]{2}')"; echo "dated guide rows $(sed -n 20,23p docs/reading-guide.md | grep -cE '20[0-9]{2}-[0-9]{2}-[0-9]{2}')"
trailers: for p in 507:54dff069 495:0e67f42a 484:8df69e15 477:acf6c604 483:bdfa5b19 498:76270d6c 502:9caac0cf 504:cee6d2f5; do m=${p#*:}; n=$(git log --format='%(trailers:key=Co-Authored-By,valueonly,separator=;)' "$m^1..$m^2" | grep -v '^$' | grep -vc '^Claude Fable 5.1 <noreply@anthropic.com>$'); echo "#${p%%:*} $n"; done
wide-scan: echo "wide-scan hits $(git grep -n -E '32\.9|2\.79 ?MB|about 33|33 ?MiB|2\.[78] ?MB' -- . ':!tasks' ':!audits' | wc -l | tr -d ' ')"
fable-after: echo "fable after 9de107b9 $(git log --format='%(trailers:key=Co-Authored-By,valueonly)' 9de107b9..54dff069^2 | grep -c 'Claude Fable 5.1')"
flaky-alone: uv run pytest -q -p no:cacheprovider --hypothesis-seed=0 tests/eval/test_game_profile.py::test_a_fold_reading_the_carrier_fails_both_properties
flaky-seed: echo "seed 58 DID NOT RAISE lines $(uv run pytest -q -p no:cacheprovider --hypothesis-seed=58 tests/eval/test_game_profile.py::test_a_fold_reading_the_carrier_fails_both_properties 2>&1 | grep -c 'DID NOT RAISE')"
cross-era: git grep -c _cross_era_trajectory -- '*.py' >/dev/null; echo "code hits exit $?"; git grep -c _cross_era_trajectory >/dev/null; echo "card hits exit $?"
wrapped-tips: echo "wrapped ladder-tip phrases $(perl -0777 -ne 'my $n = () = /ladder[ \t]*\n[ \t>]*tip/gi; print $n' audits/README.md)"
shelves: uv run python -c "import json; d = json.load(open('replays/samples/9p2i/results-game-profile.json')); print('; '.join(s['name'] + ' ' + str(len(s['members'])) for s in d['pre_reveal']['shelves']))"
reasoning-pool: echo "era registry reads $(grep -c -E 'eval\.eras|from eval import eras|era_of|era_groups' eval/reasoning_evidence.py)"; echo "inventory sets $(sed -n 344,352p eval/reasoning_evidence.py | grep -c -E '\("(samples|ml_corpus)", "(4p1i|9p2i)"')"
slow-wrapped-tip: d=$(mktemp -d) && git archive HEAD | tar -x -C "$d" && perl -0777 -pi -e 's/and the ladder\n  tip stays at baseline 9\./and the ladder\n  tip stays at baseline 10./ or die' "$d/audits/README.md" && uv run python scripts/check_doc_facts.py --repo-root "$d" >/dev/null 2>&1; echo "wrapped tip exit $?"; rm -rf "$d"
```

### 8.2 Claims

Each section-1 paragraph ends with its row here; every path is tracked at H,
every test node collects, and every command exits 0.

| claim row | claim | mechanism | test | command |
| --- | --- | --- | --- | --- |
| `engine` | replays re-run byte for byte within their recorded runtime scope | `engine/tick.py`, `scripts/verify_samples.sh` | `tests/orchestrator/test_game.py::test_headless_game_replay_is_byte_identical_for_same_seed` | `verify-samples`, `engine-test` |
| `tactical` | the scripted tactical layer moves players; the model is called at meetings and explicit triggers, a rule held by review | `agents/tactical/crewmate_policy.py`, `agents/tactical/impostor_policy.py`, `AGENTS.md` | none: no gate | `tactical-imports` |
| `firewall` | agents never read the engine; bounded checks, not complete privacy assurance | `.importlinter`, `eval/leak_scan.py` | `tests/test_firewall.py::test_import_linter_reports_a_planted_agents_to_engine_route` | `lint`, `firewall-test` |
| `labels` | the tally never reads the grounding label; the teammate firewall re-aims, and is counted | `meetings/voting.py`, `eval/process_scorecard.py` | `tests/meetings/test_grounding_label.py::TestTheTallyNeverReadsTheLabel` | `labels-test`, `scorecard-check` |
| `shape` | the shape's recorded rules read zero by construction, and a breach stops the census | `docs/game-shape.md`, `eval/gameplay_census.py` | `tests/eval/test_gameplay_census.py::test_every_guarded_cell_has_a_planted_pair` | `census-test`, `census-check` |
| `eras` | one registry names each set's era, and the instruments it names pool only within one | `eval/eras.py` | `tests/eval/test_eras.py::test_a_registry_filing_samples_9p2i_under_baseline_9_is_refused` | `eras-test` |
| `recorder` | a record covers 50 seeds; a committed set records only its own era's config | `scripts/_declared_experiment.py`, `scripts/refresh_samples.sh` | `tests/scripts/test_refresh_samples.py::test_an_era_refusal_names_the_set_and_the_declared_file_it_found` | `recorder-test` |
| `citations` | a valid citation is resolvable, not supported | `eval/process_scorecard.py`, `eval/vj_instruments.py` | `tests/eval/test_vj_instruments.py::test_citation_counts_split_valid_from_dangling` | `citations-test` |
| `role` | role-correct ejection is reported and never a gate | `eval/process_scorecard.py` | `tests/eval/test_process_scorecard.py::test_the_role_correct_row_is_labelled_as_no_gate` | `role-test`, `scorecard-check` |

### 8.3 Figures

Each figure is held to the section that states it and to its source at H: a
`path:line` (or line range) on which the figure occurs, or the stdout of a
command in section 8.1. A cited generated page also passes its own `--check`.

| figure row | figure | stated in | source |
| --- | --- | --- | --- |
| 1 | `394/397 = 0.9924` | 0, 3.1, 3.8 | `docs/process-scorecard.md:110` |
| 2 | `407/410 = 0.9927` | 3.1 | `docs/process-scorecard.md:110` |
| 3 | `1589/1602 = 0.9919` | 3.1 | `docs/process-scorecard.md:34` |
| 4 | `272/1183 = 0.2299` | 3.1 | `docs/process-scorecard.md:35` |
| 5 | `44/281 = 0.1566` | 3.1 | `docs/process-scorecard.md:111` |
| 6 | `47/305 = 0.1541` | 3.1, 3.8 | `docs/process-scorecard.md:111` |
| 7 | `147/1362 = 10.8%` | 3.1 | `docs/process-scorecard.md:37` |
| 8 | `65/292 = 22.3%` | 3.1 | `docs/process-scorecard.md:113` |
| 9 | `56/291 = 19.2%` | 3.1 | `docs/process-scorecard.md:113` |
| 10 | `0/57 = 0.0000 (not evaluable 57)` | 3.1 | `docs/process-scorecard.md:39` |
| 11 | `1/15 = 0.0667 (not evaluable 14)` | 3.1 | `docs/process-scorecard.md:115` |
| 12 | `0/15 = 0.0000 (not evaluable 15)` | 3.1 | `docs/process-scorecard.md:115` |
| 13 | `12/2785 = 0.0043` | 3.1 | `docs/process-scorecard.md:40` |
| 14 | `11/691 = 0.0159` | 3.1 | `docs/process-scorecard.md:116` |
| 15 | `6/702 = 0.0085` | 3.1, 3.8 | `docs/process-scorecard.md:116` |
| 16 | `6/702` | 0 | `docs/process-scorecard.md:116` |
| 17 | `2307/2309 = 0.9991` | 3.1 | `docs/process-scorecard.md:42` |
| 18 | `580/580 = 1.0000` | 3.1 | `docs/process-scorecard.md:118` |
| 19 | `583/583 = 1.0000` | 3.1 | `docs/process-scorecard.md:118` |
| 20 | `2768/2785 = 0.9939` | 3.1 | `docs/process-scorecard.md:43` |
| 21 | `674/691 = 0.9754` | 3.1 | `docs/process-scorecard.md:119` |
| 22 | `692/702 = 0.9858` | 1, 3.1, 3.8 | `docs/process-scorecard.md:119` |
| 23 | `343/1602 = 0.2141` | 3.1 | `docs/process-scorecard.md:44` |
| 24 | `189/410 = 0.4610` | 3.1 | `docs/process-scorecard.md:120` |
| 25 | `177/397 = 0.4458` | 3.1, 3.8 | `docs/process-scorecard.md:120` |
| 26 | `177/397` | 0 | `docs/process-scorecard.md:120` |
| 27 | `288/321 = 0.8972` | 3.1 | `docs/process-scorecard.md:45` |
| 28 | `44/66 = 0.6667` | 3.1 | `docs/process-scorecard.md:121` |
| 29 | `46/61 = 0.7541` | 3.1, 4 | `docs/process-scorecard.md:121` |
| 30 | `46/61` | 0 | `docs/process-scorecard.md:121` |
| 31 | `teammate_coerced 10` | 1 | `docs/process-scorecard.md:135` |
| 32 | `764/1183 (64.6%)` | 3.2 | `docs/gameplay-census.md:341` |
| 33 | `235/305 (77.0%)` | 3.2, 3.8 | `docs/gameplay-census.md:341` |
| 34 | `0/764 (0.0%)` | 3.2 | `docs/gameplay-census.md:387` |
| 35 | `0/235 (0.0%)` | 3.2, 3.8 | `docs/gameplay-census.md:387` |
| 36 | `0/235` | 0 | `docs/gameplay-census.md:387` |
| 37 | `0/214` | 3.2 | `audits/audit-2026-10-09-stage-b-r3.md:2027` |
| 38 | `818/842 (97.1%)` | 3.2 | `docs/gameplay-census.md:389` |
| 39 | `245/248 (98.8%)` | 3.2, 3.8 | `docs/gameplay-census.md:389` |
| 40 | `245/248` | 0 | `docs/gameplay-census.md:389` |
| 41 | `278/281` | 3.2 | `audits/audit-2026-10-09-stage-b-r3.md:2029` |
| 42 | `24/842 (2.9%)` | 3.2 | `docs/gameplay-census.md:390` |
| 43 | `3/248 (1.2%)` | 3.2, 3.8 | `docs/gameplay-census.md:390` |
| 44 | `3/281` | 3.2 | `audits/audit-2026-10-09-stage-b-r3.md:2029` |
| 45 | `198/321 (61.7%)` | 3.2 | `docs/gameplay-census.md:439` |
| 46 | `29/61 (47.5%)` | 3.2 | `docs/gameplay-census.md:439` |
| 47 | `40/66` | 3.2 | `audits/audit-2026-10-09-stage-b-r3.md:2031` |
| 48 | `8/13 (61.5%)` | 3.2 | `docs/gameplay-census.md:441` |
| 49 | `7/13 (53.8%)` | 3.2 | `docs/gameplay-census.md:441` |
| 50 | `7/12` | 3.2 | `audits/audit-2026-10-09-stage-b-r3.md:2032` |
| 51 | `251/427 (58.8%)` | 3.3 | `docs/gameplay-census.md:117` |
| 52 | `7/70 (10.0%)` | 3.3 | `docs/gameplay-census.md:117` |
| 53 | `47/140 (33.6%)` | 3.3 | `docs/gameplay-census.md:229` |
| 54 | `107/302 (35.4%)` | 3.3 | `docs/gameplay-census.md:192` |
| 55 | `0/106 (0.0%)` | 3.3 | `docs/gameplay-census.md:192` |
| 56 | `0/531 (0.0%)` | 3.3 | `docs/gameplay-census.md:262` |
| 57 | `90/119 (75.6%)` | 3.3 | `docs/gameplay-census.md:262` |
| 58 | `0/531 by construction` | 3.3 | `docs/gameplay-census.md:266` |
| 59 | `0/119 by construction` | 1, 3.3, 4 | `docs/gameplay-census.md:266` |
| 60 | `0/115 by construction` | 1 | `docs/gameplay-census.md:267` |
| 61 | `2/23 (8.7%)` | 3.3 | `docs/gameplay-census.md:468` |
| 62 | `17/19 (89.5%)` | 3.3 | `docs/gameplay-census.md:468` |
| 63 | `77/250 (30.8%)` | 3.3 | `docs/gameplay-census.md:584` |
| 64 | `17/50 (34.0%)` | 3.3 | `docs/gameplay-census.md:584` |
| 65 | `trip no game` | 3.4 | `docs/game-profile.md:70` |
| 66 | `(44, 0)` | 3.4 | `docs/game-profile.md:67` |
| 67 | `19 (21 ejections)` | 3.4 | `docs/game-profile.md:99` |
| 68 | `14 (15 ejections)` | 3.4 | `docs/game-profile.md:100` |
| 69 | `31 of 40` | 3.5 | `experiments/lab/report-route-lines-replay.md:122` |
| 70 | `29 of 40` | 3.5 | `experiments/lab/report-route-check-replay.md:216` |
| 71 | `25 of 29` | 3.5 | `experiments/lab/report-route-check-replay.md:293` |
| 72 | `7 of 7` | 3.5 | `experiments/lab/report-route-lines-replay.md:179` |
| 73 | `26 of 29` | 3.5 | `experiments/lab/report-route-lines-replay.md:179` |
| 74 | `Reaching is showing a line, not changing a vote.` | 3.5 | `experiments/lab/report-route-lines-replay.md:125` |
| 75 | `26/29 (89.7%)` | 3.5 | `docs/gameplay-census.md:446` |
| 76 | `6 of 14 against round 2's 5 of 14` | 3.5 | `audits/audit-2026-10-09-stage-b-r3.md:2120` |
| 77 | `5 of 14` | 3.5 | `audits/audit-2026-10-09-stage-b-r3.md:2120` |
| 78 | `17/50 = 0.34 (0.22-0.48)` | 3.6, 4 | `audits/audit-2026-10-09-stage-b-r3.md:1950` |
| 79 | `0.20-0.60` | 3.6 | `audits/audit-2026-10-09-stage-b-r3.md:1950` |
| 80 | `step rule: names the era-keyed promotion of round 3 as the shown set, the owner's to take or override (Conf. misses 0; impostor wins 17/50; M 29 against round 2's 40)` | 3.6 | `audits/audit-2026-10-09-stage-b-r3.md:1985` |
| 81 | `featured 9p2i 2; wrong on what it held 14; both 0` | 3.7 | `cmd:featured` |
| 82 | `24/50 = 0.48 (0.35-0.61)` | 4 | `audits/audit-2026-10-09-stage-b-r3.md:1950` |
| 83 | `50/50` | 4 | `audits/audit-2026-10-09-stage-b-r3.md:1695` |
| 84 | `29/271 (10.7%)` | 4 | `docs/gameplay-census.md:173` |
| 85 | `10/95 (10.5%)` | 4 | `docs/gameplay-census.md:173` |
| 86 | `2/703 (0.3%)` | 4 | `docs/gameplay-census.md:176` |
| 87 | `5/302 (1.7%)` | 4 | `docs/gameplay-census.md:176` |
| 88 | `21.28` | 4 | `tasks/decision-2026-09-24-stage-b-wave.md:1578` |
| 89 | `6.4, not flagged` | 4 | `audits/audit-2026-10-09-stage-b-r3.md:1951` |
| 90 | `FAIL 0` | 4 | `cmd:vme` |
| 91 | `24 of 46` | 4 | `README.md:33` |
| 92 | `Contracts: 5 kept, 0 broken.` | 1, 7.4 | `cmd:lint` |
| 93 | `first-parent merges 37` | 6 | `cmd:ledger-count` |
| 94 | `97549508 docs: apply the extractor card's closure span correctly` | 7.2 | `cmd:closure` |
| 95 | `ancestor exit 0` | 7.2 | `cmd:closure` |
| 96 | `configs exit 1` | 7.2 | `cmd:erv-configs` |
| 97 | `four-contracts lines 1` | 7.4 | `cmd:arch-four` |
| 98 | `profile in pinned tree 1` | 7.4 | `cmd:pinned-profile` |
| 99 | `ci fetch-depth lines 0` | 7.4 | `cmd:ci-depth` |
| 100 | `swapped exit 0` | 7.4 | `cmd:slow-swap-46-42` |
| 101 | `moved exit 1` | 7.4 | `cmd:slow-move-46-47` |
| 102 | `no floor label exit 0` | 7.4 | `cmd:slow-floor-label` |
| 103 | `rows swapped exit 0` | 7.4 | `cmd:slow-row-order` |
| 104 | `no before sentence exit 0` | 7.4 | `cmd:slow-before-sentence` |
| 105 | `handle moved exit 0` | 7.4 | `cmd:slow-body-handle` |
| 106 | `games moved exit 0` | 7.4 | `cmd:slow-ml-50-games` |
| 107 | `dated process rows 0` | 7.4 | `cmd:process-row-dates` |
| 108 | `dated guide rows 0` | 7.4 | `cmd:process-row-dates` |
| 109 | `#507 13` | 7.4 | `cmd:trailers` |
| 110 | `#495 12` | 7.4 | `cmd:trailers` |
| 111 | `#484 6` | 7.4 | `cmd:trailers` |
| 112 | `#477 21` | 7.4 | `cmd:trailers` |
| 113 | `#483 4` | 7.4 | `cmd:trailers` |
| 114 | `#498 4` | 7.4 | `cmd:trailers` |
| 115 | `#502 9` | 7.4 | `cmd:trailers` |
| 116 | `#504 1` | 7.4 | `cmd:trailers` |
| 117 | `wide-scan hits 9` | 7.4 | `cmd:wide-scan` |
| 118 | `fable after 9de107b9 2` | 7.4 | `cmd:fable-after` |
| 119 | `1 passed` | 7.4 | `cmd:flaky-alone` |
| 120 | `code hits exit 1` | 7.4 | `cmd:cross-era` |
| 121 | `card hits exit 0` | 7.4 | `cmd:cross-era` |
| 122 | `wrapped ladder-tip phrases 1` | 7.4 | `cmd:wrapped-tips` |
| 123 | `wrapped tip exit 0` | 7.4 | `cmd:slow-wrapped-tip` |
| 124 | `the_reporter_saw_it_happen 13; double_kill 7; slow_burn 15; suspicion_moved 16; a_third_round 22` | 3.4 | `cmd:shelves` |
| 125 | `671/702 (95.6%)` | 3.5 | `docs/gameplay-census.md:443` |
| 126 | `era registry reads 0` | 7.4 | `cmd:reasoning-pool` |
| 127 | `inventory sets 4` | 7.4 | `cmd:reasoning-pool` |
| 128 | `No instrument pools across eras.` | 7.4 | `audits/audit-2026-10-09-stage-b-r3.md:2312` |
| 129 | `seed 58 DID NOT RAISE lines 1` | 7.4 | `cmd:flaky-seed` |
| 130 | `3d32d31e card: flip stage-b-record-r3 to done after its merge` | 6 | `cmd:finish-commits` |
| 131 | `2eed2e92 card: flip retire-era-locked-pins to done after its merge` | 6 | `cmd:finish-commits` |
| 132 | `76d1c826 card: flip promote-round-3 to done after its merge` | 6 | `cmd:finish-commits` |
| 133 | `49498b0b card: flip front-door-process-first to done after its merge` | 6 | `cmd:finish-commits` |
| 134 | `a3b42fd4 docs: stamp the task inventory with the day of its last flip` | 6 | `cmd:finish-commits` |
| 135 | `214/281` | 3.2 | `audits/audit-2026-10-09-stage-b-r3.md:1916` |
| 136 | `47/140` | 3.3 | `audits/audit-2026-10-09-stage-b-r3.md:2009` |
| 137 | `0/109` | 3.3 | `audits/audit-2026-10-09-stage-b-r3.md:2012` |
| 138 | `0/117` | 3.3 | `audits/audit-2026-10-09-stage-b-r3.md:1883` |
| 139 | `24/50` | 3.3 | `audits/audit-2026-10-09-stage-b-r3.md:1950` |
| 140 | `17/93` | 4 | `audits/audit-2026-10-09-stage-b-r3.md:2020` |
| 141 | `5/291` | 4 | `audits/audit-2026-10-09-stage-b-r3.md:2020` |

## 9. Limitations of this audit

- After this audit merges, no CI gate binds its figures. The audit file is in no
  checked document list, the gap the phase-21 close filed as its own first
  finding (`audits/audit-phase-21-close.md`); the next promotion or re-record
  turns these figures into history, and this file is not edited then.
- Its own check, `audit_check.py`, is a scratch script quoted whole with its
  sha256 in the card's Results and never committed; it holds the figures at H
  only, and the documentation lens is the review that stands beside it.
- Every figure is one recording's: one 50-game hosted recording per round, so a
  difference between rounds is never claimed as real.
- The pull-request cross-check against GitHub was read once, at dispatch; the
  ledger's own count is git's and reproduces offline.
- The two advisory memos were read outside the tree and are the source of no
  figure; where this audit names their decisions it cites the decision memo's
  in-tree line.
- Finding 13 starts from an observation the tree does not record; it is filed
  with the two fixed seeds that show the case passing and failing.
- One finding (finding 16) came from the pull request's automated review and was
  re-checked at H with its own command before it was filed.
