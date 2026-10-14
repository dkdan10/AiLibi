# Tactical ML after Stage B: has the new gameplay changed the case for it?

Diagnosis memo, topic `ml_tactical`, 2026-10-02. Read-only on `dkdan10/AiLibi` at `main` `d41c9006`.
I made no commit, no push and no edit to tracked files. I made no live provider call, did not read
`.env` and ran no recorder. The probe games in section 4 ran on the fake provider with no replay
(`HeadlessGame.run_unrecorded`), so nothing was written to disk. Every census over replays is
count-only. No prompt, model turn or seed-band text is printed or quoted. Role-correctness is
reported here and gates nothing.

Columns, never pooled: **s9** = `replays/samples/9p2i` (baseline 9, map cooldown 4). **r1** =
`replays/candidates/stage-b-r1/9p2i` (the eight arms). **r2** = `replays/candidates/stage-b-r2/9p2i`
(the eight arms plus `kill_cooldown_ticks = 6`). All three are the same 50 seeds of 9 players with
2 impostors.

Scope: the tactical layer only. That means crew routing, button, reporting, fleeing and repair, and
impostor targeting, kill timing, venting, the look-and-wait exit and sabotage. Speech and ballots at
meetings belong to the LLM and are out of scope except where they set the tactical objective.

---

## Answer in brief

1. **The updated game moves the decisive moment off the LLM meeting and onto the tactical race.**
   - Games that end on a play tick (a parity kill or the last task): s9 12/50, r1 36/50, r2 35/50.
   - Games that end at a meeting: 38, 14 and 15.
   - Crew wins by tasks: 1, 4 and 13. In r2 these are half of the 26 crew wins.
   - So the tactical layer now decides more of the outcome than at any earlier baseline. That gives
     tactical ML more leverage than it ever had.
2. **The levers ML found or chased are now set by hand-written rules, and the census pins them.**
   - Vent exposure. Exits seen from the exit room fell from 53/85 to 8/72. All 8 residual sightings
     came from a crewmate walking in on the same tick: exits into a room a crewmate already stood in
     are 0/72.
   - Vent entries away from the impostor's own fresh kill: 0/140.
   - Kills inside the grace window: 0/109.
   - Co-present kills (Phase 18's N2): 0 in all three sets.
   - A seen kill now gives the witness a ballot row about it. 13 of 14 such witnesses voted the
     killer, and 6 of the 14 killers were ejected. Being seen killing is no longer free, but it is
     still cheaper than being seen venting (24 of 24 seen-venting impostors were ejected).
3. **Real slack remains in four places.** None of it is in a Conf. cell.
   - Kill timing. The FSM kills at the earliest legal tick or the next one in 39 of 50 first kills
     of a game.
   - Target choice. 594 of 1,076 kill-ready ticks had two or more isolated crewmates on the map.
   - Where idle crew stand. There are 1,813 idle crew-ticks, all at the hub: 19.9% of crew
     decisions, up from 6.9% on s9.
   - Crew task routing in a close race. 12 of the 24 impostor wins came with the crew at 80% or more
     of their tasks done.
4. **The training stack cannot run this game today, and fixing that is new work, not a
   configuration.**
   - `TacticalRolloutEnv` takes no experiment config.
   - Its interposed agents, and the served learned champion, are refused by the orchestrator
     whenever a recorded config has tactical fields:
     `agent factory does not implement the recorded tactical experiment`.
   - The learned impostor's option menu cannot express wait-in-vent or the fresh-kill entry rule.
   - The surrogate refuses experimental recordings, and the version-one fits refuse current scope.
   - Fake meetings still eject nobody: 0 ejections in 170 fake meetings over 60 probe games.
5. **Verdict: leave tactical ML on hold. The updated game makes it less worth doing for the finished
   state, not more.**
   - The new leverage is mostly over balance. A pre-registered dial (the kill cooldown) already
     controls balance legibly.
   - The owner's open flag is reporter ejections, 17/114 = 0.149. That comes from LLM meetings, and
     tactical ML cannot touch it.
   - Any impostor-side objective trades the data the crew holds for wins. The owner values the
     opposite.
   - The one aligned target is crew evidence-gathering with a role-blind objective. Hand-written
     alternatives for it (`crew_idle_policy = patrol | accompany`) already exist and have never been
     measured on the Stage-B arms. They come first, at no cost.
   - Preconditions and a first experiment, if the owner takes it up later, are in section 10.

---

## 1. What changed in the game the tactical layer plays

| | s9 | r1 | r2 |
|---|---|---|---|
| median game length, ticks (min to max) | 20 (11 to 48) | 29.5 (15 to 61) | 35 (20 to 66) |
| meetings; meetings per game | 145; 2.90 | 124; 2.48 | 117; 2.34 |
| games ending on a play tick: parity by kill + crew task win | 11 + 1 = 12 | 32 + 4 = 36 | 22 + 13 = 35 |
| games ending at a meeting: crew eject win + parity at a meeting | 38 + 0 | 12 + 2 | 13 + 2 |
| tasks done at game end | 425/698 | 517/697 | 608/700 |
| impostor wins (reported, gates nothing) | 11 | 34 | 24 |
| impostors able to kill when a meeting opened | 63/210 | 84/203 | 54/200 |
| meetings with vent proof | 70/145 | 26/124 | 24/117 |

Sources:
- Win split and end kinds: the scratch walk (section 11, command C4), which reads `GameOver` from
  play ticks and from meeting post-events.
- Meetings and vent proof: the census (C1).
- Cooldown at open: census `impostor_cooldown_zero_at_open`.

Reading: the regroup (`meeting_reset = hub_with_grace`, `engine/meeting_reset.py:10-23`) and the
6-tick cooldown give fewer and longer meetings and longer games. The task bar now finishes 13 times.
Each impostor kill and each crew task step is now a larger share of what decides the game. The
meeting still ejects in 66 of 117 meetings, and 44 of those 66 ejections removed an impostor. So the
LLM still removes about 0.9 impostors per game. But the game is over by a tactical event in 35 of 50
cases.

## 2. What the tactical layer decides in r2, and how often

Counted per living player per play tick. The engine either applied the action or rejected it.
Actions thrown away on a trigger tick are counted separately: 142 impostor, 316 crew. Ground truth
means engine state, not the agent's view.

**Impostor decisions: 3,088.** On 1,816 of them (59%) the kill cooldown was running.

| decision | r2 | s9 | r1 | rule that makes it |
|---|---|---|---|---|
| move (stalk, cover, reposition) | 1,340 | 677 | 1,105 | `impostor_policy.py` ladder, docstring `:37-75` |
| pretend task (engine-rejected camouflage) | 961 | 354 | 624 | `_idle` blend; `training/env.py:263-276` |
| kill attempts: applied + target moved out first | 195 + 44 | 175 + 41 | 227 + 57 | kills only when alone with one crewmate, `impostor_policy.py:1050-1075` |
| wait outside a vent (mostly the fellow-defer rule) | 157 | 152 | 165 | `_defers_to_colocated_fellow`, `:1123` |
| vent entries | 140 | 105 | 142 | `own_fresh_kill`, `agents/tactical/experimental.py:330-339` |
| in-vent decisions: wait / exit (forced at the cap) | 124 / 72 (5) | 0 / 85 (0) | 120 / 72 (13) | `look_and_wait`, `experimental.py:456-530`; cap `:48` |
| sabotage: applied + rejected | 46 + 9 | 8 + 0 | 15 + 0 | near-task-win trigger, `impostor_policy.py` docstring `:62-75` |
| report or button | 0 | 0 | 0 | impostors never open (census `impostor_openers` 0/117) |

**Crew decisions: 9,105.**

| decision | r2 | s9 | r1 | rule |
|---|---|---|---|---|
| task step, applied | 3,790 | 2,932 | 3,286 | route to own pending task |
| move | 3,151 | 1,965 | 2,786 | A* toward the task or the hub |
| idle wait, every one in the hub | 1,813 | 382 | 1,121 | `crewmate_policy.py:40-46` (hub_wait) |
| sabotage repair (incl. rejected) | 172 | 33 | 55 | `crewmate_policy.py:15-28` |
| body report | 116 | 136 | 119 | report interrupt, `crewmate_policy.py:8-11` |
| emergency button | 3 | 10 | 6 | suspicion 0.6 or more and the pacing gate, `crewmate_policy.py:29-38` |
| crew-ticks alone in a room, of all crew decisions | 2,746 (30.2%) | 1,968 (35.7%) | 2,366 (31.8%) | consequence of routing |

What each decision is worth in r2:
- A kill is 1 of 195. 22 of the 24 impostor wins ended on a parity kill.
- A task step is 1 of 3,790. 13 crew wins ended on the last task.
- Reports open 114 of 117 meetings. The button opens 3.
- Of 14 kills a crewmate saw, the witness held a row about the kill at the next meeting in all 14.
  The killer was ejected in 6 (census `held_kill_killers_ejected`).

## 3. Which decisions are fixed by rule, and which still have slack

**Fixed by rule (no slack an optimizer may use without breaking an adopted arm)**

| decision | how it is fixed | r2 count |
|---|---|---|
| vent entry | only beside the impostor's own kill from the last 3 ticks (`experimental.py:41`, `:595-645`) | Conf. 0/140 |
| surfacing before the cap | only with no non-teammate in an inferred-visible room (`experimental.py:502-530`) | Conf. 0/72 |
| trip length | at most 4 ticks inside (`experimental.py:48`, `:502-512`) | Conf. 0/66 |
| kill after a regroup | illegal T+1 to T+6 (engine cooldown, `engine/meeting_reset.py:17-23`) | Conf. 0/109 |
| impostor report or button | never (`self_report` False) | Conf. 0/117 |
| crew seeing a body | reports it that tick (interrupt) | 116 of 116 crew-ticks with a body in the room |
| two impostors with one crewmate | the higher id defers (`impostor_policy.py:1123`) | 44 waits |
| killing with two or more crew present | never (`impostor_policy.py:1050-1075`) | 0 kills in 205 such kill-ready ticks |
| a free kill (cooldown 0, alone with one crewmate, ground truth) | always attempted | 287 states: 195 applied, 44 lost to a target that moved first in player-id order (`kill requires same room`), 44 fellow defers, 4 body-in-room cover moves; 0 declined by choice |

**Slack still open (what an optimizer could change)**

| decision | evidence of slack in r2 | what changing it would touch |
|---|---|---|
| **kill timing** | First kill of the game at the earliest legal tick or the next: 39/50 (s9 45/50). First kill after a meeting at the earliest legal tick or the next: 41/95. The FSM is greedy. | Balance directly (22/24 impostor wins are parity kills); meetings per game |
| **target choice (stalk)** | 1,076 kill-ready ticks. 584 had no crewmate in the impostor's room. 594 had two or more crewmates alone in rooms somewhere on the map (ground truth, an upper bound on what the impostor knows). | Balance; which crewmates hold sightings; the 14 seen kills |
| **vent exit room and wait** | 196 in-vent decisions. 171 had two or more of the 3 exit options with no crewmate there (ground truth), and so did 68 of 72 exits. The pick among clear rooms is a lexical key (`experimental.py:516-530`). | Little. The 8 seen exits are same-tick arrivals the impostor cannot observe in advance |
| **where idle crew stand** | 1,813 idle crew-ticks, all at the hub (19.9% of crew decisions, s9 6.9%). 30.2% of crew-ticks alone. | What the crew hold at a meeting: hard clue in 67/114 report meetings, last seen with the killer 34, killer at the scene 30 (`measure_baseline.py --funnel`). Kill opportunities. |
| **task routing** | 608/700 tasks done. 13 task wins. 12/24 impostor wins came with the crew at 80% or more of tasks. | Balance through the task race |
| **button timing** | 3 presses in 117 meetings | Meetings with less data (button meetings carry no body) |
| **sabotage timing** | 46 applied (s9 8). 30 crew task steps refused under a gating sabotage. | The task race |
| **pretend-task placement** | 961 impostor decisions (31%) | Camouflage and alibi claims at meetings |

## 4. Can the training environment run the eight arms and the cooldown?

**No. Three separate code paths block it, and the probe confirms each one.**

1. **The env has no seam for a recorded config.**
   - `TacticalRolloutEnv.__init__` (`training/env.py:583-597`) has no experiment parameter.
   - Each rollout builds `HeadlessGame` without `experiment_config` (`:711-724`, `:750-763`).
   - Its factory builds plain `ImpostorPolicy` and `CrewmatePolicy` (`:552-566`).
   - Probe C5 printed the parameter list: `episode_boundary, game_map, intent_selector, max_ticks,
     meeting_runner_factory, no_replay, num_impostors, num_players, output_dir, rng_hash_policy`.
2. **The orchestrator refuses the env's agents under any tactical arm.**
   - `_InterposedAgent` wraps a `TacticalAgent` but is not one. `HeadlessGame` raises when the config
     has tactical fields and an agent is not a built-in `TacticalAgent`
     (`orchestrator/game.py:3189-3218`; tactical fields per `orchestrator/experiment_config.py:197-208`,
     `:216-238`).
   - Probe C5, interposition factory plus the r2 config: `refused: agent factory does not implement
     the recorded tactical experiment`.
   - The served learned champion wraps impostors in `_LearnedAgent` (`agents/tactical/learned/factory.py:123`).
     It hits the same branch, so it cannot be recorded on the adopted arms either.
   - Engine and orchestrator fields alone (`vent_witness_rule`, `meeting_reset`, `kill_cooldown_ticks`)
     do pass through the interposition factory: probe C5 ran them. But `look_and_wait` and
     `own_fresh_kill` are tactical, so the full era cannot run.
3. **The learned arbitration cannot express the arms.**
   - `utility_es.enumerate_options` offers an in-vent impostor only exit options, never a wait
     (`training/bakeoff/utility_es.py:342-364`). It also offers `cover_vent` beside any body
     (`:368-390`).
   - A learned argmax over that menu would surface at 1 tick and could enter vents away from its own
     fresh kill. That breaks two adopted arms whose Conf. cells read 0.
4. **The meeting instruments refuse the era.**
   - The surrogate table calls `require_baseline_experiments` (`training/surrogate/dataset.py:1026`).
     Probe C6 on an r2 replay: `refused: frozen surrogate meeting table does not support experimental
     recordings`.
   - The committed fits are version one, and current scope refuses them (`training/provenance.py:191-194`).
     `load_conviction_fitness_term()` and `load_composed_components()` both raised `historical
     version-one fit cannot score current inputs` in this session.
   - Campaign preflight requires the baseline profile (`training/provenance.py:39-49`, called at
     `training/coevo/driver.py:1185`).

**Fake meetings still eject nobody** (probe C5, 20 seeds per condition, fake provider, no replay):

| condition | meetings | ejections | wins |
|---|---|---|---|
| env baseline (interposition, no config) | 69 | 0 | impostor parity 20/20 |
| engine and orchestrator arms only (physical, regroup, cooldown 6), interposition | 52 | 0 | crew tasks 7, impostor parity 13 |
| the r2 play arms, production factory (the lab's path) | 49 | 0 | crew tasks 5, impostor parity 15 |

Why: the fake returns a minimal zero-valued instance (`llm/fake_provider.py:120-145`). The lab says
so in its own words: "a fake meeting ejects nobody" (`experiments/tactical_gameplay.py:129`). The
crew track recorded the same at `training/reports/report-crew-track.md:213`.

**Does that still break the objective?** Yes, though now only in part.

- **Still broken.**
  - The impostor terms `survival` and `meetings_survived` are constant at 1 under fake meetings
    (`training/rewards.py:268-291`), so being seen at a vent or a kill costs nothing.
  - The conviction term adds 0.5 times predicted evidence supply (`training/bakeoff/harness.py:281`,
    `:1056`), which still pays for being seen.
  - The crew's `correct_reports` is constant at 0 and is role-correct by its own comment
    (`training/rewards.py:301-306`).
- **New.** The arms turn the fake path into a real race. The crew win by tasks in 5 to 7 of 20
  games, against 0 of 20 before, so the terminal term is no longer constant and a crew task-race
  objective is non-degenerate on the fake path for the first time.
- **Still wrong for the real game.** The real race is shaped by ejections: 44 impostors ejected in
  50 r2 games. A fake-trained policy optimizes a game with no meeting consequence. That transfer
  failure is on record: policy-es scored win 0.02 on the real path after fake training
  (`training/reports/report-finalist-eval.md:182-188`).

## 5. A fitness function that rewards neither being seen nor guessing roles

The census cells are the natural candidates. Every one can be computed role-blind. The risk is what
an optimizer does to the cells the owner reads: grounded decisions (SKIP grounded 44/281 in r2),
reporter ejections (17/114, flagged), meetings with data, and genre feel.

| candidate | side | computable on fake path? | Goodhart risk against the owner's cells |
|---|---|---|---|
| time to parity, or impostor win | impostor | yes (race) | **High.** Rediscovers N1/N2 (Phase 18). Shortens games and cuts meetings (already 2.34 per game). Lowers the data the crew hold. Pushes balance past the 0.60 envelope the cooldown dial was set to hold. |
| seen-exit share (`vent_exits_seen_from_exit_room`) | impostor | yes | **Exhausted.** 8/72 residual, all same-tick arrivals. The cheapest optimum is to stop venting or killing, which starves vent proof (24/117 meetings). |
| near-body cost (impostor in the body's room or next door at report) | impostor | yes | **High.** A stealth objective by definition. It moves the funnel's killer-at-scene cell (30/114) down and SKIP-grounded share with it. It cannot be rewarded without partly paying for crew ignorance. |
| task completion share | crew | yes | **Medium.** A task rush wins by tasks and bypasses meetings. It is genre-legal, but it shrinks the LLM showcase. Hub idling already removes 20% of crew-ticks from both tasks and evidence. |
| meetings opened | crew | yes (count) | **High.** Button spam: an emergency carries no body and less data. Reporting more is impossible (116/116 already). |
| grounded-decision share (scorecard row 1) | crew | **no**, it needs LLM ballots | **Low in kind, high in cost.** This is the owner's own value. Every evaluation is a real 50-seed round (about 1,700 calls). A policy can raise it only by giving voters more held data, which is the aligned direction. |
| **role-blind whereabouts coverage**: at each kill tick, the share of living players whose room a living crewmate saw first-hand (every player counted, whatever the role) | crew | yes, from engine positions and the visibility rule | **Medium.** The optimum is stick together. That is genre-plausible (Among Us buddy play), but it cuts kill chances and so meetings. It also gives an impostor standing in a group a free alibi. Pair it with a meeting-count floor that is read, not rewarded. |
| report latency (corpse age at report; r2 mostly 3 to 4 ticks, census table) | crew | yes | **Medium.** Patrolling near kill sites shortens games and raises reporter exposure. The reporter-ejection flag is already the owner's open item. |

Rules that hold for any objective:
- No term may read roles. `correct_reports` and `patrol_coverage` must go (`training/rewards.py:301-306`).
- No term may pay for evidence produced about oneself. That is the conviction term at
  `harness.py:1056`.
- The census Conf. cells must be hard constraints in the option menu, never penalties.
- The selection referee stays selection-only (`docs/ml-program.md:68-76`).

## 6. What hand-written look-and-wait already captures of what ML found

Phase 18's measured findings were N1 (kills into witnesses at 3.3 times the scripted rate) and N2
(co-present kills): `docs/ml-program.md:105-123`. Its documented failure mode was the vent tell
(policy-es win 0.02). "Avoid vent witnesses" was the gradient the 2026-09-24 analysis inferred, and
it is now card B1 in hand-written form (`agents/tactical/experimental.py:456-571`, `:595-645`).

- **The vent lever is captured almost completely.**
  - Exits seen from the exit room: s9 53/85, r2 8/72.
  - Exits into a room a crewmate stood in: 53/85, then 0/72.
  - Seen-venting impostors: 77 on s9, 24 in r2.
  - What remains (same-tick arrivals; entries seen 16/140, also arrivals) is not observable to the
    impostor. A learner could only reduce it by predicting crew routes it cannot see.
- **N2 stays structurally absent from the scripted policy.** There were 0 co-present kills in
  205 r2 kill-ready ticks with two or more crew present.
- **N1's premise is weaker.** R8's kill row makes a witnessed kill evidential (13/14 witnesses voted
  the killer; 6/14 killers ejected).
- **What ML would still find is N1 and N2 again.** A seen kill still mints no certified flag, and
  6/14 is not 24/24.

## 7. Is co-evolution stability still the open problem?

Yes. Nothing in Stage B addresses it, and it gets sharper.

- **On record.** The first co-evolution attempt collapsed. The Red-Queen cycling signature was
  present on the general-base impostor (`audits/audit-phase-18-close.md:769-771`). Screening was
  unstable: 10 of 22 arms changed wins between tranches, and no referee PASS replicated
  (`training/README.md:180-190`).
- **Why it gets sharper (inference, not measured).** On the fake path both sides now have a winnable
  objective (impostor parity, crew tasks: probe C5), so a two-sided race is likelier to cycle than
  the old one-sided game. The race also omits the ejections that decide real games. I ran no
  co-evolution; this is reasoning from the probe.

## 8. What ML could add that rules cannot: the three most promising targets

1. **Crew idle positioning for evidence (role-blind).**
   - Evidence: 1,813 idle crew-ticks all at the hub. SKIP grounded only 44/281. Report meetings with
     a hard clue held 67/114.
   - Rules choose one place (hub_wait) or a fixed exploration (patrol, accompany). A learner could
     place crew where they are most likely to hold first-hand whereabouts at the next kill.
   - Aligned with the owner's value: more data held, nobody pushed toward the answer.
   - Caveat: the hand-written patrol and accompany have not been measured on the arms. Run them
     first.
2. **Impostor kill timing and target choice under the cooldown.**
   - Evidence: the greedy timing (39/50 and 41/95 at the earliest two ticks). 594/1,076 kill-ready
     ticks with several isolated crewmates. 22/24 impostor wins are parity kills. The 44 kill
     attempts lost to targets moving first.
   - This is where a learner would gain the most wins. But it is a balance lever the cooldown dial
     already controls legibly, and its natural optimum is N1/N2 and meeting starvation.
3. **The task race: crew routing and impostor sabotage timing.**
   - Evidence: 13 task wins. 12/24 impostor wins with the crew at 80% or more. 46 sabotages. 30
     refused task steps.
   - This is new to the Stage-B game and is decided entirely without the LLM. The rules are greedy
     (nearest pending task; sabotage at about 6/7 completion).
   - It is computable on the fake path. Its Goodhart risk is a task rush that bypasses meetings.

The in-vent exit room ranks below these. Its slack is real (171/196 decisions with two or more
clear exits), but the outcome it could move is already near its floor.

## 9. What ML cannot add

- **Anything the LLM decides.** That covers who speaks, what is claimed, rebuttals, ballots, who is
  ejected, and the reading of a vent or kill row.
- **The owner's open flag.** Reporters ejected per report meeting, 17/114 = 0.149, are meeting
  outcomes. The report itself is an un-suppressible interrupt (116/116), and a crew policy that
  avoids finding bodies would be anti-genre.
- **Role-correct ejection** (44/66). It is reported only. Any objective that reads it breaks
  ruling D1.
- **The meeting conversion** that removes 0.9 impostors per game. Fake training cannot model it.
  The composed runner that once stood in for it is version one, fit on the baseline corpus, and
  refuses the era.

## 10. Verdict, preconditions and the first experiment

**Verdict: keep tactical ML on hold. The updated gameplay makes it less worth doing for the
finished, showable state.**

- The game's outcome now hangs more on the tactical race: 35/50 games end on a tactical event.
- But the levers ML historically exploited are now hand-written, legible and pinned at 0 by the
  census.
- Balance has a pre-registered dial: r2 sits at 24/50 = 0.48, inside the envelope.
- What remains for an optimizer either trades crew data for impostor wins, which the owner values
  against, or has untested hand-written alternatives already in the tree.
- The cost of a real-path read is unchanged (one 50-seed round is about 1,700 calls and 10M input
  tokens).
- Before any search the stack needs new code in protected wiring: the env's config seam, the
  orchestrator's built-in-agent check and a constrained menu.

**Preconditions, if the owner takes it up later.** All are needed, and the program should start
fresh.

1. Gameplay is settled. The era-keyed promotion of a round inside the envelope with no flag is
   adopted. Today the round-3 rule names no step, because of the reporter flag.
2. The env takes a `RecordedExperimentConfig`. The interposed or learned agent is accepted by the
   orchestrator's tactical-arm check, as a built-in subclass of the experimental policy that
   overrides only arbitration. The option menu includes wait-in-vent and enforces the fresh-kill
   entry, so every Conf. cell stays 0 by construction. A test runs the census Conf. cells on the
   learned arm.
3. A meeting path that ejects. Either the real provider for selection only, or version-two
   surrogate and conviction fits on a Stage-B corpus. Those need a corpus larger than r2's 117
   meetings, and a guard that admits the era.
4. A role-blind objective with none of the terms in section 5's rules, and the four pre-campaign
   checks (`training/README.md:312-364`).
5. A fresh same-seed scripted comparator on the adopted arms. The cooldown and seeds are fixed
   before search.
6. Search on Linux under an explicit token, wall and cost budget.

**First experiment, at $0 and before any ML.** Measure the slack with the rules already in the tree.
- Run the lab on the Stage-B play arms plus cooldown 6, crossed with `crew_idle_policy` in
  `hub_wait`, `patrol` and `accompany`, on development seeds. `experiments/tactical_gameplay.py`
  already builds Stage-B configs (`:131-197`); adding the idle-policy cross is a lab change.
- Count the task race (end kind, tasks at end) and kills. Count a role-blind whereabouts-coverage
  cell computed from engine positions.
- If a hand-written idle policy closes most of the gap, the ML case for target 1 disappears. If it
  leaves measurable slack, the next step is a small menu-bounded ES over idle-position choice. Its
  fitness is role-blind coverage with a read-only meeting-count floor. It is selected by one real
  50-seed round on the process scorecard, with role-correctness reported only.

## 11. Commands (count-only, run at `d41c9006`) and limitations

Committed instruments (each writes nothing to the tree):

```
# C1: census, three columns (exit 0 each)
uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r2/9p2i --json-stdout
uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout
uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout
# C2: scorecard (grounded 451/691, SKIP 44/281, role-correct 44/66)
uv run python scripts/publish_process_scorecard.py --set-dir replays/candidates/stage-b-r2/9p2i --json-stdout
# C3: information funnel (hard clue 67/114, last seen with killer 34, killer at scene 30, kill witnessed 14)
uv run python scripts/measure_baseline.py replays/candidates/stage-b-r2/9p2i --funnel --json
```

Scratch scripts, uncommitted and count-only, kept in the session scratch directory `ml_tactical-scripts/`. Each
is run from the worktree root with `PYTHONPATH=<worktree root>`:

```
# C4: tactical decision census over the census walk profile (state-hash verified)
uv run python ml_tactical-scripts/tactical_census.py replays/candidates/stage-b-r2/9p2i   # and r1, s9
# C5: env probe: env parameters, the tactical-arm refusal, fake-meeting ejections (20 seeds x 3 conditions, no replay)
uv run python ml_tactical-scripts/env_probe.py 20
# C6: the surrogate's baseline guard on an r2 replay
uv run python ml_tactical-scripts/refusal_probe.py
# C7: the version-one loaders at current scope (inline): training.bakeoff.harness.load_conviction_fitness_term()
#     and training.composed_runner.load_composed_components() both raise "historical version-one fit cannot score current inputs"
```

Limitations:
- Single hosted recordings of 50 games per column. r1 and r2 differ by one key, so their difference
  is the dial's only within generation noise.
- The slack counts use engine ground truth (isolated crewmates, clear exit rooms). They are upper
  bounds on what an agent could know, not what it knew.
- "Free kill" is defined on engine positions at the start of the tick. The 44 kill attempts lost to
  targets moving first are a player-id-order race, not a policy choice.
- The whereabouts-coverage cell in sections 5 and 10 is proposed, not computed. I did not rebuild
  memories to measure first-hand holdings.
- The co-evolution statement in section 7 is inference. I ran no search.
- Fake probe outcomes measure mechanics, not model quality.
