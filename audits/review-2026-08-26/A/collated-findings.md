# Wave-0 Track A — collated findings with per-claim verdicts

**Date:** 2026-08-26. **Method:** 8 blind finder dimensions -> dedup/collation -> independent adversarial verification (every finding re-run against fresh code/bytes; default REFUTED when evidence does not reproduce). All workers Opus; the parallel track was invisible to this one.

**Tally: 48 canonical findings — 13 CONFIRMED, 35 ADJUSTED (core observation stands; claim, severity, or classification corrected by the verifier), 0 REFUTED.** Severity and classification below are POST-verification (the verifier's correction wins); the finder's original is shown when it moved.

| id | severity | classification | verdict | title |
|---|---|---|---|---|
| A-1 | P1 | defect, but SPECIFIED-and-test-pinned | ADJUSTED | The win check never runs on a tick that convenes a meeting: a decided game can keep playing, and its outcome can be inverted |
| A-2 | P1 | known-open re-quantification of G-22 | ADJUSTED | Zero-observation turn = perfect impostor label (535/535) |
| A-3 | P1 | intended-mechanic | ADJUSTED | Guard-redirected ballots record a target no voter authored while keeping the rationale that argues for someone else: 120 ballots, 25 flipped meeting outcomes, 3 ejections nobody voted for |
| A-4 | P1 | design-hole / balance | ADJUSTED | Reporter railroad: 30 of the 42 innocent ejections eject the meeting's own body reporter, who is innocent with probability 1 |
| A-5 | P1 | design-hole | ADJUSTED | reporter_exculpation is ballot-only and the reporter is structurally mute after turn 0 |
| A-6 | P1 | defect | CONFIRMED | The prompt template teaches the "the engine certified it" dialect; leak is 26x the known 3 seeds |
| A-7 | P1 | intended-mechanic | CONFIRMED | Hard evidence is uncounterfeitable by construction: 517/517 spoken vent claims are true, zero from impostors |
| A-8 | P1 | defect | CONFIRMED | Pooled accusation ECE 0.30/0.28 is ~40% teammate-firewall artifact, not agent miscalibration |
| A-9 | P1 | defect | CONFIRMED | The shipped machinery-dialect gauge and the actual leak are disjoint sets (0/39 overlap; no net at all over free_text) |
| A-10 | P1 | defect | ADJUSTED | The HOW behind the 42 pooled innocent ejections: a per-case ledger (reporter 30, counter-accusation boomerang 29, provably-false transit 17, impostor-rides-the-herd 33, hearsay pile-on 79 of 145 ejecting ballots, weak-flag 5, guard-redirect 4) |
| A-11 | P2 | acceptable-emergent | ADJUSTED | Turn order is destiny: the counter-accusation boomerang convicts the opener in 29/42 innocent ejections and 0/387 impostor ejections |
| A-12 | P1 | acceptable-emergent | ADJUSTED | The 'impossible transit' charge convicts 17 of 42 innocents and is provably false every time |
| A-13 | P2 | specified-behaviour / known-open design choice | ADJUSTED | Action priority is player-id alphabetical: seat p-9 loses 10.6% of its actions, p-1 none, and p-8/p-9 never win a contested meeting trigger |
| A-14 | P1 | defect | CONFIRMED | Meeting trigger aborts the tick: ~2,160 recorded actions (36 kills, 99 reports, 17 emergency calls) are neither applied nor rejected, yet are recorded as submitted |
| A-15 | P1 (stands; arguably P0 for the ML program given that a committed close audit asserts the opposite) | defect | ADJUSTED | ml_corpus README item 8 numbers do not reproduce on the committed bytes |
| A-16 | P2 | defect | ADJUSTED | Player-visible impostor kill confessions occur, are ignored, and are unmeasured |
| A-17 | P1 (render half); the roll-call-tell half is a re-report of the routed G-22 | defect | ADJUSTED | Ballot-time render erases all structured testimony, including the impostor tell |
| A-18 | P2 (an ML feature-hygiene hazard, already fenced in the one existing consumer), not P1 | intended-mechanic with a residual ML-corpus-hygiene hazard -- NOT a defect | ADJUSTED | The impostor's fake task is a perfect impostor label in the reconstructed event stream |
| A-19 | P2 | defect, narrowed to the MEASUREMENT half only | ADJUSTED | After the opening turn the soft-evidence channel is pure noise, yet stated confidence rises 0.59 -> 0.70 |
| A-20 | P2 as a finding (re-report + re-measure of open items G-13 / G-8 / G-19); the ML-protocol half is worth P1 attention inside the ML re-ground decision | intended-mechanic | ADJUSTED | Two-regime meeting: the vent_sighting flag is a 100%-precision, 100%-conversion oracle deciding 76% of ejections; without it the table is a coin flip |
| A-21 | P3 | known + measured + publicly disclosed corpus property | ADJUSTED | 210 ballots confess the impostor role in rationale_text; the Task-19.15 redaction reaches 18 of them |
| A-22 | P3 | re-quantification of known-open G-8 | ADJUSTED | Witnessed kills have no speakable shape, so crew launder them as FALSE saw_vent rows the table then follows ungrounded (G-8 quantified) |
| A-23 | P3 | re-quantification of known-open G-15 | ADJUSTED | Dead air recomputed, and 100% of crew idling is the finished-crew gap (G-15) |
| A-24 | P2 | re-report of known G-31 | ADJUSTED | "Accuse the reporter" is the impostor's near-monolithic deflection script (70.7% of its accusations) |
| A-25 | P3 | SPECIFIED / intended and already instrumented | ADJUSTED | The impostor can never report: P(impostor | reporter) is exactly 0, but the prompt says "almost never" |
| A-26 | P2 | defect | ADJUSTED | The surrogate's coerced-row filter recognises 1 of the 6 audit-marker kinds, so ~142 guard-rewritten ballots ride into the fit as if the voter had authored the target |
| A-27 | P3 | intended-mechanic | ADJUSTED | The weak-signal flag channel carries no information yet is the only flag that ever convicts an innocent |
| A-28 | P4 (informational re-quantification of a ruled-on design choice) | intended-mechanic | ADJUSTED | Body cleanup consumes only the reported corpse, so corpses accumulate across meetings (baseline-7 re-quantification of G-6) |
| A-29 | P3 | intended-mechanic | ADJUSTED | Sabotage is inert on these bytes: 29 uses, one kind, zero timeouts, a meeting refunds a tick of the doomsday clock, the map's `lights` kind is unreachable, and the alarm names neither kind nor room |
| A-30 | P3 | intended-mechanic | ADJUSTED | Impostors talk about their own whereabouts in prose while the record stays empty |
| A-31 | P2 | defect | CONFIRMED | Every witnessed vent is minted twice, and the teammate firewall leaks through the audible copy |
| A-32 | P3 | known-open re-report | ADJUSTED | The whole spoken record sits one tick after the engine's event stream, while body ids keep the engine tick |
| A-33 | P2 | acceptable-emergent | CONFIRMED | 83 of 668 meetings end with every accusing voter authoring SKIP |
| A-34 | P2 | defect | CONFIRMED | Guard-redaction sentence normalizes to the empty skeleton and becomes the #1 model-voice repetition cluster in both 9p2i sets |
| A-35 | P2 | acceptable-emergent | CONFIRMED | A ballot with target=SKIP and confidence>=0.95 is an impostor in 284 of 285 cases |
| A-36 | P2 | acceptable-emergent | ADJUSTED | 79 ejection ballots name a player nobody formally accused at that meeting; 72 of the 79 are crewmates |
| A-37 | P3 | acceptable-emergent | ADJUSTED | Nobody ever argues the exculpation: the reporter is saved by the evidence gate, not by the prose |
| A-38 | P3 | acceptable-emergent | ADJUSTED | The exculpation is under-inclusive: co-discoverers of the same body get none of it |
| A-39 | P2 | acceptable-emergent | CONFIRMED | G-29 quantified on baseline-7 bytes: stock repetition has moved off free_text onto structured claim reasons (33.6% share a skeleton twin) |
| A-40 | P3 | acceptable-emergent | CONFIRMED | The confidence grid is prompt-authored, not agent-derived, so ECE measures template compliance |
| A-41 | P3 | intended-mechanic | ADJUSTED | Accuse-then-SKIP is the citation contract plus the evidence band, not hedging or herding — the two channels are governed by deliberately different standards |
| A-42 | P3 | intended-mechanic | CONFIRMED | Clean negative: zero template, Jinja, XML-tag, JSON-schema or band-name fragments in 11,727 model-authored utterances |
| A-43 | P4 (informational / documentation note, not a defect) | specified-behaviour | ADJUSTED | A tick-budget-capped game writes no game_over row, so its replay has no recoverable outcome |
| A-44 | P4 (informational; the re-tally half is a re-report of an existing pinned test) | intended-mechanic / already-pinned known behaviour, not acceptable-emergent | ADJUSTED | Vote resolution is exact, but the 0.6 confidence gate is inert and 19% of ballots sit exactly on it |
| A-45 | P3 | acceptable-emergent | CONFIRMED | Impostor deflection is varied and grounded; the lying is narrow and purposeful |
| A-46 | P3 | acceptable-emergent | ADJUSTED | Agents narrate station events that never happened -- 'when the lights went out', security cameras |
| A-47 | P3 | acceptable-emergent | ADJUSTED | Emergency meetings are the clean control: the caller is also the opener, and is never convicted |
| A-48 | P3 | acceptable-emergent | ADJUSTED | Raw engine room identifiers (EAST_HALL / WEST_HALL) spoken verbatim in 6.7% of turns |

---

## A-1 — The win check never runs on a tick that convenes a meeting: a decided game can keep playing, and its outcome can be inverted

**Severity:** P1 (finder: P0). **Classification:** defect, but SPECIFIED-and-test-pinned (tasks/phase-1.md:220 + tests/engine/test_tick.py) -- the fix requires overriding a recorded Phase-1 contract and re-pinning two committed replays, which the fix_sketch does not say. **Verdict:** ADJUSTED. **Area:** flow-edges / win-condition timing. **Confidence:** high.
**Merged from:** flow-edges#3: The win check never runs on a tick that convenes a meeting: a decided game can keep playing, and its outcome can be inverted.

**Claim.** Claim stands as written and is NEW (no prior G-/C- finding covers it). What must be added: the skip is not an oversight in the code, it is an EXPLICITLY SPECIFIED behaviour -- tasks/phase-1.md:220 (Task 1.5 Integration risk) reads verbatim 'MEETING phase: when an action triggers MEETING, return early; do not run passive effects or win checks within that tick', it is pinned by two named regression tests (tests/engine/test_tick.py:1109 and :1117 test_emergency_trigger_interrupts_tick_before_passive_effects_and_win_checks), and audits/audit-2026-05-09-1901.md:119/163 signed it off as conforming. So the fix is a spec + test change, not a one-line repair, and it would break the byte-identity of the two committed replays that realise it (replays/samples/4p1i/replay-seed-3.jsonl and replays/ml_corpus/4p1i/replay-seed-1009.jsonl would no longer reproduce their meeting records or state-hash chains). Supporting datum the finding missed, which cuts the OTHER way and is why 'defect' survives: orchestrator/game.py:1327-1330's own comment asserts 'A skipped meeting cannot newly satisfy a win condition by itself' -- i.e. the author believed the post-meeting gate only ever sees meeting-created wins. Both realised cases are SKIPPED meetings that nonetheless emitted GameOver there, which falsifies that assumption. The consequence was not intended, even though the mechanism was.

**As originally filed.** engine/tick.py returns at step 1 on the MEETING transition and therefore skips step 3's resolve_win_conditions, so a kill or a final task completion that resolves the game on the same tick as a report/emergency produces no GameOverEvent -- a full LLM meeting then runs on an already-decided world, and its ejection is applied on top, which can misattribute the win reason or flip the winner outright.

**Finder evidence.**

```
CODE
engine/tick.py:593-604 returns on the MEETING transition (see previous finding);
the win check is engine/tick.py:624-636, AFTER that return:
    # 3) Check victory.
    win_result = resolve_win_conditions(working_state)
    if win_result is not None: ... GameOverEvent ...
So on a meeting tick, steps 2 and 3 never execute. The only remaining gate is
orchestrator/game.py:1331-1342, which runs resolve_win_conditions AFTER the
meeting outcome has been applied to the world.

REALIZED IN THE COMMITTED BYTES (2 of 668 meetings opened on an already-won world)
$ PYTHONPATH=... uv run python .../scan.py   # walks all 300 games, evaluates
                                             # win conditions at MeetingOpened
    "meeting_opened_with_win_met": 2
    win_met_at_meeting [('replays/samples/4p1i', 3, 10, 'CREWMATES', 'CREWMATE_TASKS'),
                        ('replays/ml_corpus/4p1i', 1009, 7, 'CREWMATES', 'CREWMATE_TASKS')]

replays/samples/4p1i/replay-seed-3.jsonl, tick 10 (full trace, .../case1.py):
    tick 10 phase=MEETING tasks 3/3 alive=['p-1', 'p-2', 'p-4']
       actions: [('p-1','do_task',{'task_id':'analyze_specimen'}), ('p-2','report',{'body_id':'body-p-3-8'}), ('p-4','move',{'to_room':'ADMIN'})]
       events : [('TaskCompleted','p-1','analyze_specimen'), ('MeetingTriggered','p-2','')]
       >>> MEETING OPENS. win_now = WinResult(winner='CREWMATES', reason='CREWMATE_TASKS')
       >>> entry outcome: SKIPPED None triggered_by p-2
       >>> meeting applied -> phase GAME_OVER  events [('GameOver','CREWMATE_TASKS','CREWMATES')]
p-1's do_task completed the LAST task instance; p-2's report (sorting after it)
flipped the phase and cut off the win check. A complete LLM meeting -- turns,
ballots, provider spend -- then ran on a game the crew had already won.
The second instance is replays/ml_corpus/4p1i/replay-seed-1009.jsonl tick 7
(p-1 TaskCompleted 'upload_logs' -> 3/3, then p-4 report), same shape.
Both happened to resolve SKIPPED, so nothing was ejected past the win in the
committed bytes.

LATENT CONSEQUENCE 1 -- innocent ejected after the crew has won, and win-reason
misattribution (.../proof2.py, engine + apply_meeting_result only):
    evaluate_win_conditions(state at meeting open) = WinResult(winner='CREWMATES', reason='CREWMATE_TASKS')
      -> engine emitted NO GameOverEvent; the meeting runs anyway
    ejected innocent p-2 (CREWMATE) AFTER the crew had already won:
      post events: [('GameOver', 'CREWMATES', 'CREWMATE_TASKS')]
      alive after: ['p-1', 'p-3', 'p-4']
    same world, meeting ejects the last impostor p-4:
      post events: [('GameOver', 'CREWMATES', 'CREWMATE_EJECT')]
      -> labelled CREWMATE_EJECT even though CREWMATE_TASKS was already true at meeting open

LATENT CONSEQUENCE 2 -- OUTCOME INVERSION (.../proof3.py): an impostor kill that
reaches parity on a tick whose report sorts after it:
    action order: [('p-1', 'kill'), ('p-3', 'report')]
    events: [('Killed', 'p-1'), ('MeetingTriggered', 'p-3')]
    after tick: [('p-1','IMPOSTOR'), ('p-3','CREWMATE')] phase: MEETING
    evaluate_win_conditions(state at meeting open) = WinResult(winner='IMPOSTORS', reason='IMPOSTOR_PARITY')
    meeting ejects the impostor p-1:
      post events: [('GameOver', 'CREWMATES', 'CREWMATE_EJECT')]
      => a decided IMPOSTOR_PARITY win was recorded as a CREWMATES / CREWMATE_EJECT win

HOW CLOSE THE BYTES CAME (.../margin.py)
    parity margin (alive_crew - alive_imp) at meeting open: {1: 148, 2: 116, 3: 257, 4: 140, 5: 7}
    the 9 meetings that convened on the same tick as a kill: margins 2,2,2,3,3,2,3,2,2
148/668 meetings (22%) open one death away from parity; the 9 same-tick-kill
meetings all had margin >= 2, so no inversion occurred in baseline 7. The two
components (margin-1 meeting, same-tick kill+report) are both common; only their
co-occurrence is rare, and the re-record will draw the lottery again.
Note the win-condition ORDER itself is correct (engine/win_conditions.py:22-63,
parity -> sabotage -> impostors-eliminated -> tasks); the defect is purely that
the check is skipped on the meeting-trigger tick.
```

**Verifier evidence (independent re-run).**

```
1) CODE re-anchored: `grep -n 'if working_state.phase == "MEETING"' engine/tick.py` -> 599 (return at 600); `grep -n '# 3) Check victory' engine/tick.py` -> 624. Line anchors as filed. Only other call site: `grep -rn resolve_win_conditions engine/ orchestrator/` -> engine/tick.py:625, orchestrator/game.py:1331. No win gate between the MEETING transition and the LLM meeting (orchestrator/game.py:1869-1880 dispatches straight to _run_and_apply_meeting).
2) INDEPENDENT 300-game scan (my own walk: orchestrator.seeder.seed_initial_state -> engine.tick.advance_tick -> orchestrator.game.apply_meeting_result, engine.win_conditions.evaluate_win_conditions at every MEETING transition; script at <scratch>/v/scan_a1.py):
   {"games": 300, "meetings": 668, "same_tick_kill_meeting": 9, "meeting_opened_with_win_met": 2}
   HITS [('replays/samples/4p1i', 3, 10, 'CREWMATES', 'CREWMATE_TASKS', 'SKIPPED', None), ('replays/ml_corpus/4p1i', 1009, 7, 'CREWMATES', 'CREWMATE_TASKS', 'SKIPPED', None)]
   margins {1: 148, 2: 116, 3: 257, 4: 140, 5: 7}
   samekill margins Counter({2: 6, 3: 3})
   -> every headline number in the finding reproduces EXACTLY, including the two seeds/ticks, the margin histogram and the 9 same-tick-kill margins (2,2,2,3,3,2,3,2,2).
3) INVERSION re-proved from scratch (<scratch>/v/inv.py, engine + apply_meeting_result only, 4p1i seed 3 roster):
   events: [('Killed','p-4'), ('MeetingTriggered','p-3')]
   phase: MEETING
   win at meeting open: WinResult(winner='IMPOSTORS', reason='IMPOSTOR_PARITY')   # NO GameOverEvent emitted
   post events: [('GameOver','CREWMATES','CREWMATE_EJECT')]
   -> a decided IMPOSTOR_PARITY win recorded as a CREWMATES/CREWMATE_EJECT win. Mechanism confirmed independently.
4) SPEC check: `grep -rn 'win check' tasks/ audits/` -> tasks/phase-1.md:220 mandates the skip; audits/audit-2026-05-09-1901.md:119 'Meeting interrupt returns early ... (verified by tests/engine/test_tick.py:747-817)' | Pass. `sed -n '1117,1143p' tests/engine/test_tick.py` shows the pinning test by name.
5) NOVELTY check: `grep -rn 'advance_tick|win check|resolve_win_conditions' audits/review-2026-08-19/B/ C/` -> nothing on the meeting-tick win skip. Not a re-report of any G-/C- item.
```

**Verifier note.** Severity lowered P0 -> P1: realised corruption on the frozen bytes is ZERO. Both realised cases resolved SKIPPED and recorded the CORRECT winner and reason (CREWMATE_TASKS at the right tick); the only realised harm is 2 of 668 meetings' worth of wasted LLM turns plus 2 corpus meetings that a correct engine would never have produced. The inversion is latent at 0/668: it needs a kill that REACHES PARITY on a tick whose report sorts after it, and all 9 observed same-tick-kill meetings sat 2-3 deaths from parity. Expected rate on a re-record is order 0-1 per 300 games (~0.3% of the headline win split), which is real but does not clear a P0 'corrupts the measurement' bar. The finding is otherwise the strongest of the five: fully reproducible, genuinely new, and correctly hedged ('can').

KNOWN-OPEN OVERLAP: none -- checked against the balance-wave seven (G-5/G-8/G-13/G-15/G-22/G-40/G-43), G-26, G-29, G-31, G-37, C-88 and the tracks B/C code findings.

**Fix sketch.** Run resolve_win_conditions before returning on the MEETING transition in engine/tick.py: if a win is already satisfied, emit GameOverEvent and return phase='GAME_OVER' instead of 'MEETING' (an impostor win that lands on the same tick as a report should attribute to the offence per DESIGN.md 3.5, exactly as it does on a normal tick). The orchestrator's post-meeting check at orchestrator/game.py:1331 then only ever sees wins the meeting itself created. Add a regression test asserting that a kill reaching parity plus a same-tick report yields IMPOSTOR_PARITY and never opens a meeting.

## A-2 — Zero-observation turn = perfect impostor label (535/535)

**Severity:** P1 (finder: P0). **Classification:** known-open re-quantification of G-22 (prompt-manufactured design-hole, already on the chartered balance-wave slate) -- not a new defect. **Verdict:** ADJUSTED. **Area:** impostor-behavior / meeting transcript shape / ML corpus hygiene. **Confidence:** high.
**Merged from:** impostor-behavior#1: Zero-observation turn = perfect impostor label (535/535).

**Claim.** The measurement is exact and reproduces to the last digit. What must change is the framing: this is a NEW-NUMBER RE-QUANTIFICATION of the known-open balance-wave item G-22, not a new defect. G-22 (audits/review-2026-08-19/A/collated-findings.md:294, carried into audits/audit-phase-20-close.md:445 as one of the balance wave's seven, P1) already claims 'half of all impostor turns arrive with an empty observations array -- which no crew turn ever does' and already publishes 'P(impostor | turn has no whereabouts) = 97.7-100%'. The finding's evidence header says 'the mechanism is disclosed in replays/ml_corpus/README.md item 8, the classifier strength below is not' -- that second half is FALSE as written: README item 8 ends 'A behavioral tell in the public record -- not an observation-firewall leak -- and a learnable role classifier that no shipped metric currently prices', and G-22 gives the 97.7-100% strength. What is genuinely new and worth keeping: on baseline-7 bytes the precision is EXACTLY 1.000 (535/535, and 0/2674 crew turns) rather than 97.7-100%, plus the per-game coverage (>=1 impostor outed in 275/300 = 91.7%, ALL impostors outed in 213/300 = 71.0%) and the clean role x turn-kind decomposition. That refresh has real value because audits/audit-phase-20-close.md:445 itself marks the G-22 cell 'historical, not a live measurement'.

**As originally filed.** Across all four committed baseline-7 sets every single meeting turn whose structured `observations` list is empty was spoken by an impostor (535/535, precision 1.000) and no crew turn is ever empty (0/2,674), so the corpus hands any fitted model a deterministic role label that covers 57.7% of impostor turns, at least one impostor in 91.7% of games and every impostor in 71.0% of games.

**Finder evidence.**

```
QUANTIFYING A KNOWN-OPEN ITEM (G-22 roll-call asymmetry) with new baseline-7 numbers; the mechanism is disclosed in replays/ml_corpus/README.md item 8, the classifier strength below is not.

COMMAND (standalone stdlib, run from /Users/danielkeinan/projects/AiLibi):
  python3 /private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/8c686913-6a30-43ad-8ed2-a35d8125a233/scratchpad/wave0/A/repro_tell.py

OUTPUT (verbatim):
  S9: crew turns 652 whereabouts 652 zero-obs 0 | imp turns 219 whereabouts 104 zero-obs 115 (all impostor replies: 115/115)
      games 50: >=1 impostor outed 48, ALL outed 30
  C9: crew turns 1854 whereabouts 1854 zero-obs 0 | imp turns 625 whereabouts 283 zero-obs 342 (all impostor replies: 342/342)
      games 150: >=1 impostor outed 149, ALL outed 105
  S4: crew turns 80 whereabouts 80 zero-obs 0 | imp turns 40 whereabouts 5 zero-obs 35 (all impostor replies: 35/35)
      games 50: >=1 impostor outed 35, ALL outed 35
  C4: crew turns 88 whereabouts 88 zero-obs 0 | imp turns 44 whereabouts 1 zero-obs 43 (all impostor replies: 43/43)
      games 50: >=1 impostor outed 43, ALL outed 43
  POOLED: crew turns 2674 / whereabouts 2674 / zero-obs 0 ; imp turns 928 / whereabouts 393 / zero-obs 535
  zero-observation turns: 535; impostor share 535/535

BREAKDOWN BY ROLE x TURN-KIND (same loader, pooled over all four sets):
  CREWMATE opening    whereabouts  668/ 668 = 1.0000   mean_obs=3.75  zero_obs=0/668
  CREWMATE opt_in     whereabouts 1705/1705 = 1.0000   mean_obs=3.12  zero_obs=0/1705
  CREWMATE reply      whereabouts  301/ 301 = 1.0000   mean_obs=3.75  zero_obs=0/301
  IMPOSTOR opt_in     whereabouts  393/ 393 = 1.0000   mean_obs=3.48  zero_obs=0/393
  IMPOSTOR reply      whereabouts    0/ 535 = 0.0000   mean_obs=0.00  zero_obs=535/535
The split is exactly on IMPOSTOR-reply; impostor opt_in turns answer roll call at the same 100% rate as crew.

ROOT CAUSE (template, not model choice):
  agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:239
    'Keep "observations" as an empty list and "claims" as exactly that one accusation'
  agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:218
    'a bystander who was elsewhere has nothing to explain, so explain nothing about your own whereabouts'
  The roll-call sibling that would restore the item exists but is behind the OFF lever:
    agents/strategic/prompts/qwen3_6_27b/accusation_round_roll_call.j2:198 ('Keep "observations" as exactly that one item')
    agents/strategic/prompts/loader.py:330-345 (impostor_roll_call, DEFAULT OFF)
  Recorded state, every game_over stamp: "impostor_roll_call": false (e.g. replays/samples/9p2i/replay-seed-0.jsonl, last line).

RENDER SURFACE (what the tell looks like in the bytes a model reads) — from the p-4 accusation-round prompt in replays/samples/9p2i/replay-seed-0.jsonl meeting headless-seed-0:meeting-0:
  - [headless-seed-0:meeting-0:turn-1] turn 1 (reply) - p-6
    claims:
    - accuses p-3 (0.60): saw p-3 linger in ADMIN with p-7 then move to EAST_HALL ...
    said: "I might be mistaken, but I certainly didn't vent; ..."
  Every other turn in that same render carries a 'saw:' block; the impostor reply has none. The absent block is the label.
```

**Verifier evidence (independent re-run).**

```
1) INDEPENDENT loader (<scratch>/v/a2.py) -- roles derived from orchestrator.seeder.seed_initial_state, NOT from the finding's '## Your role: IMPOSTOR' prompt-marker heuristic; turns read straight from each replay-seed-*.jsonl transcript:
   S9 crew 652 wh 652 zero 0 | imp 219 wh 104 zero 115 ; games 50 >=1 outed 48 ALL 30
   C9 crew 1854 wh 1854 zero 0 | imp 625 wh 283 zero 342 ; games 150 >=1 outed 149 ALL 105
   S4 crew 80 wh 80 zero 0 | imp 40 wh 5 zero 35 ; games 50 >=1 outed 35 ALL 35
   C4 crew 88 wh 88 zero 0 | imp 44 wh 1 zero 43 ; games 50 >=1 outed 43 ALL 43
   POOLED crew 2674/2674 wh, imp 928 turns, 535 zero-obs; zero-obs total 535, impostor share 535/535
   CREWMATE opening 668/668, opt_in 1705/1705, reply 301/301 (zero_obs 0 in all three)
   IMPOSTOR opt_in 393/393 wh, zero_obs 0 ; IMPOSTOR reply 0/535 wh, zero_obs 535/535
   -> EVERY figure in the finding, including the per-set lines and the role x turn-kind table, reproduces exactly by an independent role source.
2) TEMPLATE anchors re-read: accusation_round.j2 output_format under `{% if is_impostor and turn_kind == "reply" %}` -- 'Keep "observations" as an empty list'; rules block -- 'a bystander who was elsewhere has nothing to explain, so explain nothing about your own whereabouts'. Sibling accusation_round_roll_call.j2 emits one whereabouts item. agents/strategic/prompts/loader.py::impostor_roll_call_enabled docstring: 'DEFAULT OFF'. All as filed.
3) DISCLOSURE check: `sed -n '255,279p' replays/ml_corpus/README.md` -> item 8 'Role-correlated public response shape ... the impostor REPLY surface hard-codes observations: [] (0/124) while the crew reply carries the full vocabulary (79/80) ... a learnable role classifier that no shipped metric currently prices.'
4) STALENESS datum (new, mine): README item 8's numbers are BASELINE-6. `git show 2df33ca4:replays/ml_corpus/README.md | grep -n 723/726` hits at line 255-257, and `git log --oneline -3 -- replays/ml_corpus/README.md` shows efcd43b8 (the baseline-7 adopting record) touched the file but left item 8's figures at the 19.8 values. Item 8 reports 971 (S9) and 2726 (C9) turns; the committed baseline-7 bytes hold 871 and 2479 (`python3` raw turn count over the JSONL). So the disclosure's MECHANISM is current, its NUMBERS are one baseline stale.
5) KNOWN-OPEN check: audits/audit-phase-20-close.md:445 lists G-22 in the balance wave's seven with the 97.7-100% cell and flags it 'historical, not a live measurement'.
```

**Verifier note.** Not REFUTED -- the evidence is impeccable and the finding itself declares G-22 up front. But P0 is not supportable for an item the project has already triaged at P1, chartered onto a named wave, and disclosed in the corpus README as 'a learnable role classifier'. Recommend keeping it as the live re-measurement of the G-22 cell the close audit asked for, at P1, with the 'classifier strength is not disclosed' sentence struck. The fix_sketch's option (b) (mask turn_kind + empty-observation status from any fitted feature view; assert no single structured field separates roles at precision 1.0) is the right cheap mitigation and is worth carrying forward verbatim.

KNOWN-OPEN OVERLAP: G-22 (balance-wave seven, audits/audit-phase-20-close.md:445) -- direct; replays/ml_corpus/README.md item 8 -- direct mechanism disclosure

**Fix sketch.** Before the re-ground, either (a) flip impostor_roll_call ON and re-record so the impostor reply emits one structured whereabouts item (the lever and templates already exist: accusation_round_roll_call.j2 / impostor_report_roll_call.j2), which also manufactures the alibi-lie material the contradiction rules prosecute; or (b) if a re-record is out of budget, make the leak explicit to the optimizer: strip `turn_kind` + empty-observation status from any feature view fitted on these bytes, and add a corpus-level assertion/test that no single structured field separates the roles with precision 1.0. Do not fit a role classifier on raw turn structure until one of the two lands.

## A-3 — Guard-redirected ballots record a target no voter authored while keeping the rationale that argues for someone else: 120 ballots, 25 flipped meeting outcomes, 3 ejections nobody voted for

**Severity:** P1 (finder: P0). **Classification:** intended-mechanic (the guard) + known-open record-fidelity gap (G-26, triaged P2, listed not-acted-on at audits/audit-phase-20-close.md:399); the NEW content is the outcome ledger, the 3 phantom-consensus ejections, and the un-unwound calibration path. **Verdict:** ADJUSTED. **Area:** meetings/manager.py guard_ballot_target_graph -> recorded ballots -> ML corpus; also evidence-economy / recorded-byte integrity and eval/accusation_calibration.py. **Confidence:** high.
**Merged from:** ballots-vs-speech#1: Guard-redirected ballots: the rationale names one player, the target names another (107/120), and the redirect flips 25 meeting outcomes, herding-calibration#5: 120 recorded ballots carry a (target, confidence, rationale) triple no agent produced; 3 ejections have phantom consensus, evidence-economy#5: Gate-redirected ballots record a rationale arguing against a different player; 3 ejections have no public case at all.

**Claim.** Every count reproduces exactly, including the three finders' independently-derived figures. Two corrections. (1) CLASSIFICATION: the merge kept 'defect' over evidence-economy's 'intended-mechanic' on the ground that all three finders locate the fault in what gets RECORDED -- but the RECORDED gap is itself a known-open, already-triaged item: G-26 'Ballot target-redirect makes the tally contradict its own rationale' (audits/review-2026-08-19/A/collated-findings.md:346, P2, corrob 5), listed by name in audits/audit-phase-20-close.md:399 among the 'text-hygiene remainder' explicitly NOT acted on. The repo already (a) labels the redirect as a target rewrite that must not be read as voter belief (api/replay_loader.py:243-261 _TARGET_REWRITE_LABELS, whose comment cites 'the committed 9p2i seed 22'), (b) ships a regex recovery of the authored target (audits/workflows/extract_gameplay_facts.py:208-221), and (c) unwinds it on the deduction path (eval/deduction_metrics.py guard_rewritten_ballots_unwound). So this is an intended, documented mechanic with a known-open, already-mitigable record-fidelity gap. (2) The '107 rationales name the AUTHORED target' figure requires CASE-INSENSITIVE matching: exact-case substring gives 101/120 (the extra 6 are rationales writing 'P-5'/'P-1' capitalised). Recorded-target naming is 26 under both. State the estimator. Everything genuinely new survives and justifies keeping the item live above G-26's P2: the 25-flip outcome ledger, the 3 phantom-consensus ejections, and the calibration-path gap.

**As originally filed.** MERGE NOTE: merged from 3 finders (ballots-vs-speech, herding-calibration, evidence-economy) reporting the same underlying defect -- meetings/manager.py::guard_ballot_target_graph rewrites a ballot's TARGET while preserving the model-authored rationale (and confidence) verbatim, so the recorded text argues for one player and the recorded target names another. SEVERITY DISAGREEMENT: ballots-vs-speech P0, herding-calibration P1, evidence-economy P1 -- highest kept (P0). CLASSIFICATION DISAGREEMENT: ballots-vs-speech and herding-calibration classified 'defect'; evidence-economy classified 'intended-mechanic' (reading the GUARD as the subject, which it is right that it is deliberate and documented). 'defect' kept: all three finders agree the guard is net-positive and must NOT be weakened, and all three locate the fault in what gets RECORDED. The three counts agree exactly (120 redirected ballots), and herding-calibration and evidence-economy independently name the same 3 ejections with no public case at all (samples/9p2i seed 2 m0 -> p-5, ml_corpus/9p2i 1044 m0 -> p-7, ml_corpus/9p2i 1085 m0 -> p-1, all crewmates). ballots-vs-speech uniquely supplies the outcome counterfactual (25 of 668 meetings flip; net ledger 16 impostors caught / 6 innocents saved vs 2 net-negative flips) and the rationale/target text split (107 of 120 rationales name the AUTHORED target).

[claim as filed by ballots-vs-speech] 120 recorded ballots carry a target the voter did not author because the under-gate graph guard re-aimed them, 107 of those keep a rationale that names the ORIGINAL target (26 name the recorded one), and unwinding just this one guard changes the tallied outcome in 25 of 668 meetings — so the committed bytes contain 120 (speech, rationale) -> (vote) pairs whose text and target disagree.

[claim as filed by herding-calibration] The Task 10.9.2 under-gate redirect rewrites a ballot's target while preserving the model's confidence and rationale verbatim, so 120 committed ballots record a vote for player X paired with a stated confidence in, and an argument for ejecting, player Y -- and in 3 meetings every ballot naming the ejected player was such a rewrite, meaning no agent chose the person who was ejected.

[claim as filed by evidence-economy] 120 of 3602 recorded ballots (3.3%) carry the '[under-gate eject target 'X' redirected]' marker, meaning the recorded target was machine-rewritten while the recorded rationale_text still argues against the ORIGINAL target; in 40 ejections at least one convicting ballot is a redirect, and in 3 ejections -- all of them innocents -- the ejected player was never accused by anyone in the meeting transcript at all.

**Finder evidence.**

```
==============================================================================
EVIDENCE AS FILED BY FINDER: ballots-vs-speech
(its severity P0, classification defect, confidence high)
title: Guard-redirected ballots: the rationale names one player, the target names another (107/120), and the redirect flips 25 meeting outcomes
==============================================================================

REPRO (read-only; all four sets):
  PYTHONPATH=/Users/danielkeinan/projects/AiLibi uv run python <scratchpad>/wave0/A/repro.py
That script unwinds meetings/manager.py:200/211/274/354 markers to the AUTHORED target and re-tallies with meetings/voting.py:218-238 rules (thr = DEFAULT_SKIP_CONFIDENCE_THRESHOLD 0.6, meetings/constants.py:28).

VALIDATION that the join is correct — the reconstruction reproduces the published cells exactly:
  == METRIC RECONSTRUCTION (must match each set's deduction.turn_ballot_consistency) ==
    replays/samples/9p2i: denom=752 consistent=404 skip=276 rate=0.5372
    replays/ml_corpus/9p2i: denom=2113 consistent=1158 skip=792 rate=0.5480
    replays/samples/4p1i: denom=112 consistent=51 skip=57 rate=0.4554
    replays/ml_corpus/4p1i: denom=123 consistent=59 skip=59 rate=0.4797
  (identical to "deduction.turn_ballot_consistency" in each tournament-eval-report.json; the script folds the 3+1 invalid-target ballots into its "other" column, hence other=72/163 vs published 69+3 / 162+1)
  tally recompute matches the recorded outcome in 668/668 meetings

CENSUS:
  guard census: {'graph_redirect': 120, 'teammate_coerced': 18, 'uncited_coerced': 8, 'invalid_target': 4}   (150 of 3602 ballots = 4.2%)
  graph_redirect n=120; rationale names AUTHORED target 107, names RECORDED target 26
  meetings with >=1 redirect: 84; redirect CHANGED the outcome in 25

WORKED CASE 1 — replays/ml_corpus/9p2i/replay-seed-1085.jsonl, headless-seed-1085:meeting-0 (roles re-derived via orchestrator.seeder.seed_initial_state):
  T3 p-2(IMPOSTOR): "...I swear I saw p-4 vent right there..."   T5 p-9(CREWMATE) accuses p-2: "p-2 lies about seeing a vent to distract. Vote p-2."
  ballots:
    p-1(CREWMATE) -> p-2 (0.65)
    p-3(CREWMATE) -> p-1 (0.75): "[under-gate eject target 'p-2' redirected] p-4's direct refutation of p-2's vent claim is the only solid evidence here."
    p-8(CREWMATE) -> p-1 (0.65): "[under-gate eject target 'p-2' redirected] It might be that p-2's vent claim is a fabrication..."
    p-9(CREWMATE) -> p-1 (0.70): "[under-gate eject target 'p-2' redirected] p-2 lies about vent. Vote p-2."
  ejected p-1 (CREWMATE); without the redirect the tally ejects p-2 (IMPOSTOR).
  The last ballot's recorded text is literally "Vote p-2" while its target field is p-1.
  meeting flags: [('alibi_conflict', ['p-1']), ('alibi_vs_sighting', ['p-1'])] — i.e. an alibi_vs_sighting row (the class vote_ballot.j2:74-75 itself says "convicts correctly 12 times in 82") silently outranked four explicit public accusations of p-2.

WORKED CASE 2 — replays/samples/9p2i/replay-seed-2.jsonl, headless-seed-2:meeting-0: five of seven turns accuse p-1; five voters authored p-1; ALL five were redirected to p-5 and p-5 (CREWMATE) was ejected 5-0-2 with every rendered rationale reading "p-1's impossible sprint". No turn in that meeting proposes ejecting p-5.

CROSS-CHECK against the repo's own documented example (api/replay_loader.py:244-252 cites "the committed 9p2i seed 22 ... an under_gate_redirect whose rationale explicitly opposes the tallied target"): my detector reproduces it — seed 22 m0, p-5 and p-8 both authored p-4, both recorded p-6.

OUTCOME LEDGER of the 25 flips: 16 recorded ejections are IMPOSTORS that would otherwise have been a crewmate or a SKIP (guard working); 6 recorded SKIPs would otherwise have ejected a CREWMATE (guard preventing an innocent ejection); 2 are net-negative (ml_corpus/9p2i 1044:m0 SKIP -> p-7 CREWMATE ejected; ml_corpus/9p2i 1085:m0 p-2 IMPOSTOR -> p-1 CREWMATE ejected); 1 is a crew-for-crew swap (samples/9p2i 2:m0).

==============================================================================
EVIDENCE AS FILED BY FINDER: herding-calibration
(its severity P1, classification defect, confidence high)
title: 120 recorded ballots carry a (target, confidence, rationale) triple no agent produced; 3 ejections have phantom consensus
==============================================================================

COMMAND:
  cd /Users/danielkeinan/projects/AiLibi && uv run python <scratch>/wave0/A/f4_redirect.py
OUTPUT:
  ('samples/9p2i','redirected_ballots') 36        (matches the committed report cell: replays/samples/9p2i/tournament-eval-report.json -> deduction.redirected_ballots.redirected_ballots == 36)
  ('ml_corpus/9p2i','redirected_ballots') 81
  ('samples/4p1i','redirected_ballots') 1   ('ml_corpus/4p1i','redirected_ballots') 2      [total 120]
  changed 25   rec_EJ_impostor 16  rec_EJ_innocent 3   cf_EJ_impostor 1  cf_EJ_innocent 13
  PHANTOM-CONSENSUS ejections: 3
     ('samples/9p2i','headless-seed-2:meeting-0','p-5',False,5)
     ('ml_corpus/9p2i','headless-seed-1081:meeting-2','p-6',True,3)
     ('ml_corpus/9p2i','headless-seed-1085:meeting-0','p-1',False,3)

THE GUARD ITSELF IS NET-POSITIVE AND SHOULD STAY: of the 25 meetings whose outcome it changed, the recorded result ejects 16 impostors
  and 3 innocents, while the un-redirected counterfactual tally would eject 1 impostor and 13 innocents. That is exactly the
  'last unguarded seam for a RANDOM ejection' the docstring claims (meetings/manager.py:3140-3186). The DEFECT is in what gets RECORDED.

CODE ANCHOR (confidence is not re-derived): meetings/manager.py, end of guard_ballot_target_graph --
    return ballot.model_copy(update={"target": redirect, "rationale_text": marker + ballot.rationale_text})
  `confidence` is absent from the update, so the recorded number is the model's confidence in the ORIGINAL target.
  The docstring is explicit that this is deliberate for `primary_reason_id` ("the cited turn still drove the decision to EJECT --
  the guard constrains only the target") but says nothing about confidence.

WORKED CASE (samples/9p2i replay-seed-2.jsonl, headless-seed-2:meeting-0) -- ALL FIVE eject ballots were redirected:
    p-3 -> p-5 conf=0.85  "[under-gate eject target 'p-1' redirected] How did you sprint from West Hall to Cafeteria in one tick?..."
    p-4 -> p-5 conf=0.75  "[under-gate eject target 'p-1' redirected] ... p-1's impossible sprint ... is the only break in the room's logic."
    p-7 -> p-5 conf=0.95  "[under-gate eject target 'p-1' redirected] p-1's timeline is a lie! ... Vote them out now!"
    p-8 -> p-5 conf=0.75  "[under-gate eject target 'p-1' redirected] ... the math on p-1's movement is just too tight to ignore..."
    p-9 -> p-5 conf=0.85  "[under-gate eject target 'p-1' redirected] Mr. p-3's observation regarding the impossible transit ... is quite damning."
  Recorded outcome: p-5 (innocent) EJECTED, 5 votes, mean confidence 0.83, every rationale about p-1.
  Read as bytes: 'five agents voted p-5 out at 0.83 confidence, all citing turn-2'. Turn-2 is p-3 accusing p-1.

DOWNSTREAM: eval/accusation_calibration.py bins these ballots at face value -- removing them moves samples/9p2i vote_ballot ECE
  0.1498 -> 0.1397. Small in aggregate, but every one of the 120 is a maximally-wrong supervised example: the label contradicts
  the input text. eval/deduction_metrics.py DOES unwind the guard for its consistency cell
  (deduction.turn_ballot_consistency.guard_rewritten_ballots_unwound == 34 on samples/9p2i), so the unwind logic already exists
  and is simply not applied on the calibration path.

==============================================================================
EVIDENCE AS FILED BY FINDER: evidence-economy
(its severity P1, classification intended-mechanic, confidence high)
title: Gate-redirected ballots record a rationale arguing against a different player; 3 ejections have no public case at all
==============================================================================

COMMAND A (marker census over all recorded ballots):

  uv run python - <<'PY'
  import json, re, collections
  SETS={"S9":"replays/samples/9p2i","C9":"replays/ml_corpus/9p2i","S4":"replays/samples/4p1i","C4":"replays/ml_corpus/4p1i"}
  mark=collections.Counter(); tot=0
  for tag,d in SETS.items():
      r=json.load(open(f"{d}/tournament-eval-report.json"))
      for g in r["report"]["games"]:
          for m in g["meetings"]:
              for b in m["ballots"]:
                  tot+=1
                  for mm in re.findall(r"\[([^\]]+)\]", b["rationale_text"] or ""):
                      mark[re.sub(r"'[^']*'","'X'",mm)]+=1
  print(tot); [print(v,k) for k,v in mark.most_common()]
  PY

OUTPUT (total ballots 3602):
    120  under-gate eject target 'X' redirected
     27  invalid primary_reason_observation_id 'X' nulled
     18  teammate target 'X' coerced to SKIP
     18  rationale redacted by the vote guard; recorded reason: no confident read this round
      9  invalid primary_reason_id 'X' nulled
      8  uncited zero-flag eject target 'X' coerced to SKIP
      4  invalid target 'X' normalized to SKIP

COMMAND B (ejections whose victim was never publicly accused):

  uv run python - <<'PY'
  ... for each ejecting meeting, collect {c['against'] for turn in transcript.turns for c in turn.claims if c.type=='accusation'} and test whether ejected_player_id is in it ...
  PY

OUTPUT:
  {'ejections': 429, 'ejected_never_publicly_accused': 3, 'role_CREWMATE': 3}
    ('S9', 2,    'headless-seed-2:meeting-0',    'p-5', CREWMATE, publicly accused were ['p-1','p-9'],      tally {'p-5': 5, 'SKIP': 2})
    ('C9', 1044, 'headless-seed-1044:meeting-0', 'p-7', CREWMATE, publicly accused were ['p-1','p-3','p-4'], tally {'p-7': 4, 'SKIP': 3})
    ('C9', 1085, 'headless-seed-1085:meeting-0', 'p-1', CREWMATE, publicly accused were ['p-2','p-3','p-8'], tally {'p-1': 3, 'SKIP': 2, 'p-2': 1})

SPECIMEN (S9 seed 2 meeting-0 -- ALL FIVE convicting ballots are redirects; without them the tally is {'SKIP': 2} and the meeting skips):
  p-3(C) -> p-5 :: "[under-gate eject target 'p-1' redirected] How did you sprint from West Hall to Cafeteria in one tick? Did you vent? Did you kill?"
  p-4(I) -> p-5 :: "[under-gate eject target 'p-1' redirected] Let us look at the timeline together; p-1's impossible sprint from West Hall to Cafeteria in a single tick is the only break in the room's logic."
  p-7(I) -> p-5 :: "[under-gate eject target 'p-1' redirected] p-1's timeline is a lie! West Hall to Cafeteria in one tick? Impossible. Vote them out now!"
  p-8(C) -> p-5 :: "[under-gate eject target 'p-1' redirected] I suppose the math on p-1's movement is just too tight to ignore ..."
  p-9(C) -> p-5 :: "[under-gate eject target 'p-1' redirected] Mr. p-3's observation regarding the impossible transit from West Hall to Cafeteria in a single tick is quite damning."
  Five recorded ballots naming p-5 whose every word argues about p-1. p-5 is a crewmate; so is p-1.

SPECIMEN (C9 seed 1085 meeting-0 -- 3 redirects create the ejection; without them {'p-2': 1, 'SKIP': 2}):
  p-3(C) -> p-1 :: "[under-gate eject target 'p-2' redirected] p-4's direct refutation of p-2's vent claim is the only solid evidence here."
  p-9(C) -> p-1 :: "[under-gate eject target 'p-2' redirected] p-2 lies about vent. Vote p-2."

THE GUARD IS DELIBERATE AND DOCUMENTED. meetings/manager.py:255-277: "the ballot-target graph guard (Task 10.9.2; PR #147 finding F2) ... redirects such a target to the argmax-rendered eligible candidate (ties to the lowest player id) ... The owner principle this enforces is the phase's oldest line: innocents are ejectable, never at RANDOM." The original target IS preserved in the marker (recoverable, cf. audits/workflows/extract_gameplay_facts.py:215), so this is fully mitigable -- but only if the ML build looks.
```

**Verifier evidence (independent re-run).**

```
1) MARKER CENSUS (my own stdlib walk over all four sets' replay-seed-*.jsonl, not the eval reports): total ballots 3602; 120 "under-gate eject target 'X' redirected"; 27 invalid primary_reason_observation_id; 18 teammate coerced; 18 rationale redacted; 9 invalid primary_reason_id; 8 uncited zero-flag; 4 invalid target normalized. Per set redirect {'S9': 36, 'C9': 81, 'S4': 1, 'C4': 2}. Matches all three finders and the committed samples/9p2i report cell (36).
2) RE-TALLY (<scratch>/v/a3.py, meetings/voting.py rules re-implemented, thr=0.6 from meetings/constants.py:28, roles from seed_initial_state):
   meetings 668 ; tally recompute matches recorded outcome in 668/668
   redirect_ballots 120 ; meetings with >=1 redirect 84 ; changed 25
   ejections 429 ; eject_impostor 387 ; ejected_never_publicly_accused 3 ; all 3 CREWMATE
   ledger over the 25 flips: recorded EJECT-impostor 16, recorded EJECT-innocent 3, recorded SKIP 6 ; counterfactual EJECT-impostor 1, counterfactual EJECT-innocent 13 -- exactly herding-calibration's 'changed 25 / rec_EJ_impostor 16 / rec_EJ_innocent 3 / cf_EJ_impostor 1 / cf_EJ_innocent 13'.
   the 2 net-negative flips reproduce: C9 1044:m0 (SKIP -> p-7 CREWMATE ejected) and C9 1085:m0 (p-2 IMPOSTOR -> p-1 CREWMATE); the crew-for-crew swap S9 2:m0 (p-1 -> p-5) reproduces.
   PHANTOM-CONSENSUS (every ballot naming the ejectee is a redirect): S9 seed 2 m0 p-5 CREWMATE n=5 ; C9 1081 m2 p-6 IMPOSTOR n=3 ; C9 1085 m0 p-1 CREWMATE n=3 -- the exact 3, with the exact roles and counts.
   NEVER-PUBLICLY-ACCUSED ejections: S9 2 m0 p-5, C9 1044 m0 p-7, C9 1085 m0 p-1 -- the exact 3 evidence-economy named, all CREWMATE.
3) RATIONALE/TARGET SPLIT: exact-case substring -> authored 101 / recorded 26 (16 name neither); case-insensitive -> authored 107 / recorded 26. The filed 107 is the case-insensitive estimator.
4) CODE: meetings/manager.py::guard_ballot_target_graph ends `return ballot.model_copy(update={"target": redirect, "rationale_text": marker + ballot.rationale_text})` -- `confidence` is absent from the update, exactly as herding-calibration says; the docstring justifies keeping `primary_reason_id` and is silent on confidence.
5) CALIBRATION GAP CONFIRMED (this is the sharpest new item): `grep -n 'redirect|under-gate|guard|marker' eval/accusation_calibration.py` returns NOTHING across its 389 lines, while eval/deduction_metrics.py exposes guard_rewritten_ballots_unwound at :151/:1279/:1322/:2556. The unwind exists and is genuinely not applied on the calibration path.
6) KNOWN-OPEN: audits/review-2026-08-19/A/collated-findings.md:346 G-26 P2 'design-hole (transparency)'; audits/audit-phase-20-close.md:399 lists G-26 under 'not acted on -- triaged backlog'.
```

**Verifier note.** Severity lowered P0 -> P1. The merge note records the disagreement (P0/P1/P1) and kept the highest without adjudicating; two of three finders filed P1 and the project's own triage is P2. The contamination is 3.3% of ballots, it is machine-detectable by a regex the repo already ships in two places, one eval consumer already unwinds it, and all three finders agree the guard itself must NOT be weakened (net +16 impostors caught / -13 innocents saved). That is a P1 record-fidelity + corpus-hygiene item, not a P0. Keep every fix_sketch: the typed authored_target/authored_confidence fields, the calibration-path unwind, and the 3-meeting exclusion list are all correct and cheap.

KNOWN-OPEN OVERLAP: G-26 (P2, audits/audit-phase-20-close.md:399 'not acted on') -- the redirect/rationale contradiction itself; the 25-flip ledger, the 3 phantom-consensus ejections and the accusation_calibration gap are new

**Fix sketch.** [fix as filed by ballots-vs-speech] Do NOT weaken the guard — the outcome ledger says it is net strongly positive. Fix the RECORD so text and target cannot disagree: (1) apply the Task-19.15 treatment to guard_ballot_target_graph (meetings/manager.py:3132) — when the guard re-aims a target, replace the model-authored rationale with a self-declaring synthetic body (mirroring TEAMMATE_COERCED_VOTE_RATIONALE at meetings/manager.py:249) instead of preserving prose that argues for a different player; (2) persist the authored target as a typed field on VoteBallot rather than only as a string marker, so every downstream consumer reads it without regex; (3) for the frozen baseline-7 bytes, ship a documented unwind helper (the eval side already has one) and require the re-ground to use it.

[fix as filed by herding-calibration] Do not change the guard's behaviour (it prevents random ejections). Change the RECORD: add explicit `authored_target` / `authored_confidence` fields to VoteBallot populated at the redirect, instead of leaving the original target recoverable only by regex over rationale_text. Then (a) have eval/accusation_calibration.py exclude or re-key redirected ballots the way eval/deduction_metrics.py already unwinds them, and (b) have the re-ground's ballot loader drop the 120 rewritten ballots -- and at minimum drop the 3 phantom-consensus meetings entirely, since their recorded ejection was chosen by nobody.

[fix as filed by evidence-economy] Do not touch the guard -- it is doing its job (in 37 of the 40 redirect-carrying ejections the outcome was still an impostor). The exposure is entirely on the ML side: any fit that learns (transcript, rationale_text) -> ballot target will be trained on 120 examples where the text names one player and the label names another, and on 3 whole meetings whose recorded outcome has zero support anywhere in the public record. Mitigation: in the corpus feature build, detect the '[under-gate eject target ...]' prefix, recover the pre-guard target, and either (a) train on the pre-guard target with the guard modelled as a separate deterministic post-processor, or (b) drop the 120 ballots. Add the 3 no-public-case meetings (S9 seed 2 m0, C9 1044 m0, C9 1085 m0) to a documented exclusion list. Verify the count with the marker census above -- it should be exactly 120 on the frozen bytes.

## A-4 — Reporter railroad: 30 of the 42 innocent ejections eject the meeting's own body reporter, who is innocent with probability 1

**Severity:** P1 (finder: P0). **Classification:** design-hole / balance (the repo's own category for G-31), re-quantified on baseline-7 -- NOT a defect: the reporter's ejectability is a recorded design choice and the exculpation lever is deliberately soft. **Verdict:** ADJUSTED. **Area:** reporter-justice / meeting outcome; also evidence-economy / innocent-conviction mechanism. **Confidence:** high.
**Merged from:** reporter-justice#1: 30 of the 42 innocent ejections are the meeting's own body reporter, evidence-economy#1: Reporter railroad: 30/42 innocent ejections eject the body reporter, who is structurally always innocent.

**Claim.** All numbers reproduce exactly and the 30-anchor list matches item for item, so the observation is solid. Three corrections. (1) BOTH halves have known-open predecessors: the 'reporter is structurally always innocent' invariant IS G-22's second half -- audits/audit-phase-20-close.md:445 already publishes 'body reports by an impostor 0/626, meeting triggers 0/707' as one of the balance wave's chartered seven -- and the 'reporter-blame works' half IS G-31 (collated-findings.md:394, P1). (2) The reporter's EJECTABILITY is an explicit, recorded design decision, not an oversight: agents/memory/beliefs.py:182-190 states 'a reporter caught by a real contradiction or a vent/kill flag still crosses the 4.6 gate -- no immunity, only removal of the proximity prior', and tasks/phase-15.md:561-565 chartered exactly that. evidence-economy's fix (a) -- 'the meeting's own reporter is not an eligible eject target unless flagged' -- therefore proposes reversing a decision the project recorded on purpose, and the finding must say so rather than presenting it as a repair. (3) MISSING BASE-RATE CONTEXT that changes the reading: the same beliefs.py docstring records the baseline-2 rate as 22 of 106 report-meeting ejections = 20.8%; baseline 7 is 30/379 = 7.9%. The channel has been cut ~2.6x by shipped work and is IMPROVING. The 71.4%-of-innocent-ejections headline is high because the OTHER innocent-ejection routes were closed, not because this one grew -- the finding's own 'credit where due' paragraph has the observed-vs-uniform figure but never states the across-baseline trend, and without it the title 'railroad' overstates a shrinking channel.

**As originally filed.** MERGE NOTE: merged from 2 finders (reporter-justice, evidence-economy) reporting the same defect with the same headline numbers, derived independently by two different routes (reporter-justice from a direct walk of the replay JSONL + tick action stream; evidence-economy from the committed tournament-eval-report.json folds). No severity disagreement (both P0) and no classification disagreement (both 'defect'). Their per-case anchor lists agree case for case. reporter-justice uniquely supplies the per-slot relative risk (reporter 4.85% ejected vs innocent non-reporter 0.65%, RR 7.46x, z=6.98), the ungrounded-conviction cross-check (28 of the 30 convictions carry NO engine contradiction naming the reporter) and two full verbatim meetings; evidence-economy uniquely supplies the uniform-chance counterfactual (74.2 expected vs 30 observed, i.e. the exculpation lever measurably damps but does not close the channel) and the accuracy counterfactual (90.2% -> 97.0% pooled ejection accuracy with zero impostor convictions lost).

[claim as filed by reporter-justice] On the baseline-7 bytes the body reporter is ejected 30 times and is 7.5x more likely to be ejected than any other innocent sitting at the same table, making "convict the reporter" the single dominant route to the crew's dominant loss mode (this is new baseline-7 quantification of the known-open lead G-31, and the HOW behind the recorded 42-innocent-ejection number).

[claim as filed by evidence-economy] The single largest innocent-conviction class on the baseline-7 bytes is 'eject the person who reported the body' (30 of 42, 71.4%), and it is a guaranteed-wrong verdict because the impostor policy cannot file a report at all -- 0 of 618 report meetings across the four sets had an impostor reporter, so a 'reporter is unejectable' rule would erase 30 of the 42 innocent ejections at exactly zero cost in impostor convictions.

**Finder evidence.**

```
==============================================================================
EVIDENCE AS FILED BY FINDER: reporter-justice
(its severity P0, classification defect, confidence high)
title: 30 of the 42 innocent ejections are the meeting's own body reporter
==============================================================================

REPRODUCER (run from repo root; produces every headline number in this finding and in finding 2):

  uv run python - <<'PY'
  import json,glob,re,collections
  SETS=["replays/samples/9p2i","replays/ml_corpus/9p2i","replays/samples/4p1i","replays/ml_corpus/4p1i"]
  S=collections.Counter()
  for d in SETS:
      for path in sorted(glob.glob(d+"/replay-seed-*.jsonl")):
          ticks={};ms=[]
          for line in open(path):
              r=json.loads(line)
              if r["kind"]=="tick": ticks[r["tick"]]=r
              elif r["kind"]=="meeting": ms.append(r)
          roles={}
          for m in ms:
              for c in m["llm_calls"]:
                  if "## Your role: IMPOSTOR" in c["prompt"]: roles[c["agent_id"]]="IMPOSTOR"
          for m in ms:
              trig=m["triggered_by"]; kind=None
              for a in ticks.get(m["tick"],{}).get("actions",[]):
                  if a["actor"]==trig and a["type"] in ("report","emergency"): kind=a["type"]
              if kind!="report": continue
              S["body_report_meetings"]+=1
              if roles.get(trig)=="IMPOSTOR": S["reporter_is_impostor"]+=1
              acc=collections.defaultdict(set)
              for t in m["transcript"]["turns"]:
                  for cl in (t.get("claims") or []):
                      if cl.get("type")=="accusation" and cl.get("against"): acc[cl["against"]].add(t["speaker"])
              n=len(acc.get(trig,()))
              S["rep_acc_ge1"]+= n>=1; S["rep_acc_ge2"]+= n>=2
              e=m["ejected_player_id"]
              if e and roles.get(e)!="IMPOSTOR":
                  S["innocent_ejections"]+=1
                  if e==trig: S["innocent_ej_is_reporter"]+=1
              for c in m["llm_calls"]:
                  p=c["prompt"]
                  if "voting at an AiLibi meeting" in p[:300]:
                      S["ballot_prompts"]+=1
                      S["ballot_with_exculpation"]+= "reported the body that opened this meeting" in p
                  elif c["agent_id"]!=trig:
                      S["nonreporter_speech_prompts"]+=1
                      i=p.find("<memory>"); j=p.find("</memory>")
                      S["nonrep_speech_memory_says_report"]+= bool(re.search(r"report",p[i:j],re.I))
  for k in ["body_report_meetings","reporter_is_impostor","rep_acc_ge1","rep_acc_ge2","innocent_ejections","innocent_ej_is_reporter","ballot_prompts","ballot_with_exculpation","nonreporter_speech_prompts","nonrep_speech_memory_says_report"]:
      print(f"{k:34s} {S[k]}")
  PY

OUTPUT (all four committed sets, 300 games, 668 meetings):
  body_report_meetings               618
  reporter_is_impostor               0
  rep_acc_ge1                        508
  rep_acc_ge2                        267
  innocent_ejections                 42
  innocent_ej_is_reporter            30

So: 618/668 meetings are body reports (50 are emergency calls). The reporter draws >=1 formal accusation in 508/618 (82.2%) and >=2 in 267/618 (43.2%). 30 reporters are ejected. All 42 pooled innocent ejections happen in body-report meetings; ZERO occur in the 50 emergency meetings. Decomposition (same walk, keyed on meeting kind + whether the ejectee is the trigger-er):
  innocent ejections by (meeting kind, is-the-triggerer): {('report','reporter/caller'): 30, ('report','other'): 12}

PER-SLOT BASELINE (each living participant of each body-report meeting is one slot; living roster = the meeting's ballot voters; roles from the '## Your role: IMPOSTOR' marker in llm_calls prompts):
  reporter         : slots 618   acc>=1 508/618 = 82.20%   acc>=2 267/618 = 43.20%   EJECTED 30/618 = 4.85%
  innocent non-rep : slots 1844  acc>=1 352/1844 = 19.09%  acc>=2  73/1844 = 3.96%   EJECTED 12/1844 = 0.65%
  impostor         : slots 850                                                       EJECTED 337/850 = 39.65%
  relative risk of ejection, reporter vs innocent non-reporter: 7.46x  (two-proportion z = 6.98)
  relative risk of >=2 accusers:                                10.91x (z = 24.47)

THE CONVICTIONS ARE UNGROUNDED. Cross-referencing each conviction against the meeting's own `contradictions` array (the engine's evidence channel):
  body-report meetings where the reporter carries ANY engine contradiction flag: 4 / 618
  of the 30 reporter convictions: 2 flagged (both alibi_vs_sighting), 28 carry NO contradiction naming the reporter at all.
And of the 1061 accusation-claims filed against a reporter, 553 (52.1%) use only proximity-family vocabulary (body / scene / kill site / adjacent / found / walked into / first to) with no independent-evidence term (vent / contradict / lied / impossible transit / alibi mismatch); 245 more (23.1%) use neither vocabulary.

VERBATIM EXHIBIT A -- samples/9p2i seed 24, headless-seed-24:meeting-1, tick 10, reporter p-2 (CREWMATE), ejected p-2, engine contradictions: []. Impostors in this game are p-1 and p-4.
  turn 0 (opening) p-2 [CREWMATE]: "I found p-5's body in Storage at tick 10, and I was right there with them. ... p-3 was in Engineering at tick 9, which is just one door away"
  turn 1 (reply)  p-3 [CREWMATE] accuses p-2 (0.60) "moved into Engineering at tick 9, right before body found in adjacent Storage"
  turn 2 (opt_in) p-4 [IMPOSTOR] accuses p-2 (0.75) "Moved directly into Storage where body was found"
  turn 4 (opt_in) p-7 [CREWMATE] accuses p-2 (0.75) "Moved into Engineering at tick 9, adjacent to Storage where p-5 died at tick 10"
  turn 5 (opt_in) p-9 [CREWMATE] accuses p-2 (0.75) "Direct path to kill zone and body discovery"
  ballots: p-4->p-2, p-6->p-2, p-7->p-2, p-9->p-2; p-2->SKIP; p-3->SKIP ("How do you know p-2 is guilty just because they reported the body? I saw the real killer vent, and they're already gone.")
  Every word of the case against p-2 is p-2's own compelled opening disclosure, re-narrated.

VERBATIM EXHIBIT B -- ml_corpus/9p2i seed 1135, headless-seed-1135:meeting-0, tick 10, reporter p-2 (CREWMATE), ejected p-2. Impostors p-1 and p-3; BOTH pile onto the reporter and the crew follows 4-2.
  turn 0 p-2 [CREWMATE]: "I found p-7's body in EAST_HALL at tick 10."
  turn 3 p-1 [IMPOSTOR] accuses p-2 (0.75) "Seen with p-9 in STORAGE at tick 8, then moved toward kill site"
  turn 6 p-8 [CREWMATE] -- who says in the same breath "I found p-5 dead in ADMIN at tick 10" -- accuses p-2 (0.85)
  ballots: p-1->p-2, p-3->p-2, p-4->p-2, p-8->p-2 (ejected).

OUTCOME CONTEXT (9p2i, 200 games, honest framing): games containing a reporter conviction win as crew 6/27 (22.2%); games containing some OTHER innocent ejection win 3/12 (25.0%); games with no innocent ejection win 143/161 (88.8%). The cost is generic to losing a crewmate -- what is specific to the reporter is that it is the ROUTE for 28 of the 40 innocent 9p2i ejections.

==============================================================================
EVIDENCE AS FILED BY FINDER: evidence-economy
(its severity P0, classification defect, confidence high)
title: Reporter railroad: 30/42 innocent ejections eject the body reporter, who is structurally always innocent
==============================================================================

COMMAND (pooled ejection table over all four sets' tournament-eval-report.json):

  uv run python - <<'PY'
  import json, collections
  SETS={"S9":"replays/samples/9p2i","C9":"replays/ml_corpus/9p2i","S4":"replays/samples/4p1i","C4":"replays/ml_corpus/4p1i"}
  tot=collections.Counter(); exp=0.0
  for tag,d in SETS.items():
      r=json.load(open(f"{d}/tournament-eval-report.json"))
      for g in r["report"]["games"]:
          roles=g["roles"]
          for m in g["meetings"]:
              trig=m.get("trigger"); rep=m.get("triggered_by"); ej=m.get("ejected_player_id")
              if trig!="report": continue
              tot["report_meetings"]+=1
              if roles.get(rep)=="IMPOSTOR": tot["reporter_is_impostor"]+=1
              if ej:
                  tot["report_eject"]+=1; exp += 1.0/len(m["ballots"])
                  if ej==rep: tot["reporter_ejected_"+roles[ej]]+=1
  print(dict(tot)); print("uniform-chance expectation: %.1f"%exp)
  PY

OUTPUT:
  {'report_meetings': 618, 'report_eject': 379, 'reporter_ejected_CREWMATE': 30}
  uniform-chance expectation: 74.2

Note what is ABSENT from the counter: 'reporter_is_impostor' never incremented -- 0 of 618 report meetings had an impostor reporter, and 'reporter_ejected_IMPOSTOR' never incremented -- 0 of 387 impostor ejections removed the reporter.

WHY IT IS STRUCTURAL (not a sampling accident):
  agents/tactical/impostor_policy.py:52-54 -- "``COVER`` -- a body is visible in the impostor's current room. This is the FSM ``KILL -> COVER`` edge: after the kill the body is in the room and the impostor must not file a report."
  Only agents/tactical/crewmate_policy.py and agents/tactical/learned/crew_forward.py emit ReportBodyAction (grep -rln 'ReportBody' agents/). So reporter => CREWMATE is a hard invariant of the recorded generative process.

WHAT THE LEVER ALREADY DOES (credit where due): reporter_exculpation is graduated always-ON. agents/memory/beliefs.py:182-197 caps the reporter's pre-vote soft lift at 0.0 and cites the same measured base rate on baseline-2 ("the impostor self-report rate is EXACTLY ZERO -- 0 of the 164 report meetings"); agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:174 renders "In this game self-report is weakly exculpatory ... Do not vote `{{ reporter_id }}` merely for having reported it". It measurably damps: 30/379 = 7.9% observed vs 74.2/379 = 19.6% under a uniform ballot. It does not close the channel.

COUNTERFACTUAL: pooled ejection accuracy is 387/429 = 90.2%. Deleting the 30 reporter-ejections (all CREWMATE) gives 387/399 = 97.0% with zero impostor convictions lost.

ANCHORS (set/seed/meeting/victim, all trigger=report, ejectee == triggered_by):
  S9 6:meeting-2 p-1; S9 19:meeting-3 p-1; S9 21:meeting-2 p-4; S9 24:meeting-1 p-2; S9 42:meeting-2 p-1; S9 44:meeting-1 p-9; S9 44:meeting-2 p-1; S9 46:meeting-3 p-1; S9 47:meeting-3 p-4; S9 48:meeting-1 p-2; C9 1010:m1 p-1; C9 1020:m2 p-7; C9 1032:m2 p-4; C9 1039:m0 p-6; C9 1052:m0 p-8; C9 1058:m1 p-1; C9 1082:m1 p-1; C9 1092:m2 p-2; C9 1093:m3 p-6; C9 1111:m0 p-2; C9 1112:m2 p-1; C9 1127:m4 p-8; C9 1135:m0 p-2; C9 1137:m2 p-4; C9 1140:m3 p-5; C9 1143:m3 p-3; C9 1144:m2 p-1; C9 1146:m1 p-1; S4 39:m0 p-2; C4 1021:m0 p-2.

QUOTED SPECIMEN (S9 seed 47 meeting-3, reporter p-4 ejected 3-1):
  p-7 ballot: "p-4 claims Engineering at tick 25 but found a body in Reactor at 26. That is a teleport, not a walk. Get them out."
  p-4 ballot: "The accusations against me are loud, but my movement from Engineering to Reactor is a valid one-tick walk, not a teleport."
```

**Verifier evidence (independent re-run).**

```
1) INDEPENDENT walk (<scratch>/v/a4.py; roles from orchestrator.seeder.seed_initial_state, meeting kind derived from the recorded tick action stream, not from the eval reports):
   meetings 668 ; kind_report 618 ; kind_emergency 50
   reporter_is_impostor -> counter NEVER incremented (0/618)
   rep_acc_ge1 508 ; rep_acc_ge2 267 ; report_eject 379 ; innocent_ejections 42 ; innocent_ej_is_reporter 30
   innocent_ej_nonreport -> counter never incremented (0 innocent ejections in the 50 emergency meetings)
   per-slot: reporter slots 618 acc>=1 0.8220 acc>=2 0.4320 EJ 30/618=0.0485 ; innocent non-reporter slots 1844 acc>=1 0.1909 acc>=2 0.0396 EJ 12/1844=0.0065 ; impostor slots 850 EJ 337/850=0.3965
   -> RR 0.0485/0.0065 = 7.46x, exactly as filed; every figure in both finders' evidence reproduces.
   ANCHORS: all 30 (set, seed, meeting, victim) reproduce and match evidence-economy's list item for item (S9 6:m2 p-1 ... C4 1021:m0 p-2).
2) ACCURACY COUNTERFACTUAL: from the same walks, ejections 429 with 387 impostors -> 387/429 = 90.2%; removing the 30 reporter ejections -> 387/399 = 97.0%. Confirmed.
3) STRUCTURAL INVARIANT: `grep -rln ReportBody agents/` -> agents/tactical/crewmate_policy.py and agents/tactical/learned/crew_forward.py ONLY. agents/tactical/impostor_policy.py:52-54 'after the kill the body is in the room and the impostor must not file a report'. reporter => CREWMATE is a hard property of the generative process. Confirmed.
4) SPECIFICATION check (the correction): agents/memory/beliefs.py:175-197 -- lever docstring, 'At 0.0 the reporter takes NO soft lift ... no immunity, only removal of the proximity prior', plus the baseline-2 measurement '22 of 9p2i's 106 report-meeting ejections (and 1 of 4p1i's 10) removed the meeting's own -- always innocent -- reporter'. tasks/phase-15.md:553-580 is Task 15.5's contract and scopes exactly that.
5) KNOWN-OPEN check: audits/audit-phase-20-close.md:445 (G-22, balance-wave seven) carries 'body reports by an impostor 0/626, meeting triggers 0/707'; collated-findings.md:394 (G-31, P1) carries the reporter-blame channel; audits/review-2026-08-19/D/cross-track-map.md:89 dispositioned G-31 as 'Good news, actually: the ballot-time guard works'.
```

**Verifier note.** The one genuinely decision-relevant thing here is that it FALSIFIES the D-track disposition of G-31 ('the ballot-time guard works ... a designed defence that holds'): on baseline-7 samples/9p2i the guard let 10 reporter ejections through in 152 meetings against the 3-in-165 the old audit saw. That is worth stating explicitly and is the finding's strongest new content -- much stronger than the 30/42 headline, which is a share of a shrinking denominator. Severity P1: the gameplay half is G-31's own P1, the ML-leak half rides on chartered G-22, and the underlying rate is down 2.6x from baseline 2. The 'mask is_reporter out of the ML feature set' half of the fix is correct and cheap and should be carried forward regardless of what happens to the gameplay half.

KNOWN-OPEN OVERLAP: G-22 (balance-wave seven) -- the 0/618 impostor-reporter invariant; G-31 (P1) -- the reporter-blame channel. New: the 30/42 baseline-7 share, the 7.46x RR (z=6.98), the 90.2%->97.0% counterfactual, and the falsification of G-31's 'the guard holds' disposition.

**Fix sketch.** [fix as filed by reporter-justice] Root cause is finding 2 (the exculpation is ballot-only). Minimum viable fix before the re-ground: thread the reporter identity + the exculpation sentence into accusation_round.j2 the same way vote_ballot.j2 already receives it, so the accusation round deliberates with the prior instead of meeting it for the first time on the ballot. Second lever: give the reporter a right of reply (see finding 2). If the re-ground cannot wait on a re-record, at minimum carry a per-sample label marking reporter-conviction meetings so the fitter can down-weight or hold them out -- 30/42 of the innocent-ejection signal is currently this one shape.

[fix as filed by evidence-economy] Two independent moves. (1) Gameplay: strengthen reporter_exculpation from a soft-lift cap to a hard ballot gate -- the meeting's own reporter is not an eligible eject target unless they carry a role_proof (vent_sighting) or alibi_vs_physical flag this meeting; the hard channels already bypass the cap by construction (agents/memory/beliefs.py:1652-1705), so the over-damping canary is unchanged and 0 impostor convictions on these bytes are lost. (2) Substrate honesty: the invariant only holds because the impostor FSM refuses to report. Either give the impostor a self-report branch (a real Among-Us play that would make reporter-suspicion legitimate) or, if it stays, the ML re-ground MUST mask 'is_reporter' out of the feature set -- otherwise the fitted model learns a perfect impostor-exclusion oracle with zero social content. Re-check with the pooled command above after any change.

## A-5 — reporter_exculpation is ballot-only and the reporter is structurally mute after turn 0

**Severity:** P1 (finder: P0). **Classification:** design-hole (works exactly as Task 15.5 specified; the spec's render scope is the gap) + known-open overlap with G-31's own claim line and G-24 -- not a defect. **Verdict:** ADJUSTED. **Area:** reporter-justice / prompt surfaces + meeting turn structure. **Confidence:** high.
**Merged from:** reporter-justice#2: reporter_exculpation is ballot-only and the reporter is structurally mute after turn 0.

**Claim.** Every byte-level count reproduces exactly. What must change is the classification and one framing point. (1) The ballot-only scope is EXPLICITLY SPECIFIED, not an omission: tasks/phase-15.md:562-568 (Task 15.5) charters '(b) RENDER-side -- the vote surface names the reporter and states the base rate ... layered onto the vote template', and its Files-in-scope names only the vote_ballot template while the accusation-round templates are absent. meetings/manager.py:1770-1775 says the same in the code ('whether it renders is the serving template's call'). So this is a design-hole in the repo's own sense -- works as specified, the spec's scope is the gap -- not a defect. (2) It is also already on the record: G-31 (collated-findings.md:394) states in its own claim line 'the reporter_exculpation block works at ballot time but not in speech', and the 'reporter speaks exactly once / nobody ever speaks twice' half is known-open G-24 (collated-findings.md:319, P2, design-hole, 'Every meeting is exactly #turns == #ballots == #living, nobody ever speaks twice'). (3) FRAMING: the '0 of 2694 non-reporter speech prompts whose <memory> contains report' figure is partly structural rather than a leak of the exculpation -- the meeting opens on the SAME tick as the report, so no non-reporter could yet have perceived it; the load-bearing anchor is the one the finding already has, that accusation_round.j2 never receives reporter_id at all (grep -c reporter -> 0 in all five non-ballot templates, 5 in vote_ballot.j2). Lead with that, not with the memory census.

**As originally filed.** All 3312 body-report ballot prompts carry the exculpation block while 0 of the 2694 non-reporter speech prompts carry any structured statement that a body was reported or by whom, and the reporter speaks exactly once (the opening) in 618/618 meetings -- so every one of the 508 meetings that accuse the reporter accuses a player who has already spent their only turn and whose accusers were never given the counterweight.

**Finder evidence.**

```
CODE ANCHORS (read-only):
  agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:171-175 -- the ONLY place the block lives:
    {% if reporter_id is defined and reporter_id %}
    ## Who reported the body
    `{{ reporter_id }}` reported the body that opened this meeting. In this game self-report is weakly exculpatory: the impostor almost never reports its own kill, so being first to the scene is not by itself evidence of guilt. Do not vote `{{ reporter_id }}` merely for having reported it -- weigh them on the same testimony, contradiction flags, and memory as everyone else.
    {% endif %}
  meetings/manager.py:1776-1779 -- reporter_id derived at meeting scope, then :1831 `reporter_id=render_reporter` is passed to `self._vote_prompt(...)` and to nothing else.
  $ grep -c reporter agents/strategic/prompts/qwen3_6_27b/accusation_round.j2  ->  0
  $ grep -c reporter agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2   ->  0
  $ grep -c reporter agents/strategic/prompts/qwen3_6_27b/impostor_report.j2   ->  0

BYTE-LEVEL CONFIRMATION over all 618 body-report meetings (classifying each llm_call by 'voting at an AiLibi meeting' in prompt[:300]):
  ballot prompts                                                 3312
  ballot prompts carrying 'reported the body that opened this meeting'  3312   (100%)
  non-reporter speech prompts                                    2694
  ...whose <memory> block contains the substring 'report'           0   (0.0%)
  ...whose turn header names the body report                        0   (0.0%)
  reporter's OWN opening prompts whose header names it            625   (100%)

The reporter's opening header (samples/9p2i seed 24, headless-seed-24:meeting-1, agent p-2):
  "## This meeting
   It is tick 10 and a meeting just started: p-2 reported body body-p-5-5 at tick 10. It is your turn to open it (turn 0).
   A body was reported, so you speak first. Lead with what you saw: if you found the body, report it; then name the player your evidence most points to ..."
A replier's header, same meeting, agent p-3, in full:
  "## Your turn: a reply
   p-2 just accused you and the floor passed to you. Read your memory and the meeting so far below; the rules for your reply follow them."
and p-3's entire <memory> block contains no body and no report line at all (dumped verbatim; sections are Your role / Tasks completed / Meetings so far / Where you were / Recent observations / Your current beliefs).
The fact reaches a non-reporter ONLY if the reporter volunteers it: 'report*' appears inside the <transcript> block of 1008/2694 (37.4%) non-reporter speech prompts, and outside it only via the re-quoted <accusation_against_you> text and the template's own rules line "If a body was reported this meeting (see the opening turn and your memory)" -- an instruction to go look for a fact the prompt does not supply.

TURN STRUCTURE -- every living participant of a body-report meeting speaks exactly once:
  turns-per-speaker histogram across all 618 meetings: {1: 3312}
  speakers with >1 turn: {}   (none, opener or otherwise)
  reporter turn kinds across the 618 meetings: {'opening': 618}
  living participants who never speak: 0 / 3312
  accusations against the reporter by turn index: {1: 455, 2: 219, 3: 156, 4: 113, 5: 70, 6: 35, 7: 13}
Every accusation against the reporter (1061 claims) lands at turn index >= 1, i.e. after the reporter's only turn. Meetings where the reporter is accused and has no further turn: 508 / 618.

COMPELLED SELF-INCRIMINATION: the opening header instructs "if you found the body, report it". 291/618 reporters obey with an explicit find-the-body sentence and 270/618 explicitly say they reported. Honest null result worth recording: the accusation rate is the SAME either way (disclosed 240/291 = 82.5% accused>=1, not-disclosed 268/327 = 82.0%), so self-disclosure is not the sole driver -- the reporter's movement into the body room is already visible in other players' memory. The disclosure is what supplies the accusers' wording, not what creates the suspicion.
```

**Verifier evidence (independent re-run).**

```
1) INDEPENDENT prompt census (<scratch>/v/a5.py, walking llm_calls in every replay-seed-*.jsonl of the four sets, meeting kind derived from the recorded tick actions):
   report meetings 618
   ballot_prompts 3312 ; ballot_with_exculpation 3312 (100%)
   nonreporter_speech_prompts 2694 ; nonrep_speech_memory_says_report -> counter NEVER incremented (0, 0.0%)
   reporter_speech_prompts 625 ; reporter_header_names_report 625 (100%)
   turns-per-speaker histogram {1: 3312} -- nobody speaks twice, no exceptions
   reporter turn kinds {'opening': 618} -- 618/618
   accusations-against-reporter by turn index {1: 455, 2: 219, 3: 156, 4: 113, 5: 70, 6: 35, 7: 13} (sum 1061)
   meetings where the reporter is accused after their last turn: 508
   -> EVERY figure in the finding reproduces exactly, including 3312/3312, 0/2694, {1:3312}, {opening:618}, the full turn-index histogram, 1061 claims, 625, and 508/618.
2) TEMPLATE greps re-run: `grep -c reporter` -> accusation_round.j2 0, crewmate_report.j2 0, impostor_report.j2 0, accusation_round_roll_call.j2 0, impostor_report_roll_call.j2 0, vote_ballot.j2 5. Confirmed.
3) CODE anchors re-read: meetings/manager.py:1776-1779 derives reporter_id at meeting scope; :1831 passes `reporter_id=render_reporter` into the vote prompt and nowhere else. Confirmed.
4) VERBATIM EXHIBIT re-pulled from replays/samples/9p2i/replay-seed-24.jsonl meeting-1 (trigger p-2), agent p-3's accusation prompt: turn header reads exactly '## Your turn: a reply\np-2 just accused you and the floor passed to you. Read your memory and the meeting so far below; the rules for your reply follow them.' and its 2877-char <memory> block contains no 'report'. Confirmed.
5) SPECIFICATION check (the correction): `sed -n '553,600p' tasks/phase-15.md` -- Task 15.5 charters the render side onto the vote template only; Files-in-scope lists agents/strategic/prompts/qwen3_32b/ (vote_ballot template reporter line) and does NOT list any accusation-round template.
6) KNOWN-OPEN check: collated-findings.md:394 G-31 claim line contains '(the reporter_exculpation block works at ballot time but not in speech)'; collated-findings.md:319 G-24 P2 covers the one-turn round-robin.
7) NOT re-run (secondary, not load-bearing): the 291/618 and 270/618 self-disclosure counts, the 240/291 vs 268/327 null result, and the 37.4% in-transcript figure.
```

**Verifier note.** Severity lowered P0 -> P1. The observation is exact and the fix (a) -- thread reporter_id into accusation_round.j2 the way meetings/manager.py:1831 already threads it into the ballot -- is one kwarg plus one guarded block and should ship. But an item that the shipping contract deliberately scoped out, that a prior audit already stated in the same words, and whose structural half is a P2 known-open, does not carry a P0. Note also that fix (b) (a right of reply, or moving the opener last) moves recorded bytes and therefore lands only in a re-record -- the finding says this, and it is the reason the two halves must be severity-split rather than filed as one P0.

KNOWN-OPEN OVERLAP: G-31 (P1) states the ballot-vs-speech gap verbatim in its own claim line; G-24 (P2) covers the one-turn-per-speaker structure. New: the exact prompt-surface census (3312/3312 vs 0/2694), the accusation-index histogram, and the 508/618 accused-after-their-only-turn count.

**Fix sketch.** (a) Thread reporter_id into accusation_round.j2 (and the roll-call variant) exactly as meetings/manager.py:1831 threads it into the ballot -- one new kwarg on the turn-prompt call site, one guarded block in the template, mirroring the 15.5 lever precedent. (b) Give the reporter a right of reply: either let the opener take one extra turn when >=2 formal accusations name them, or move the body-report opener to the END of the round-robin so the accused speaks last. (b) moves recorded bytes and needs a re-record; (a) alone would already put the prior in front of the accusers.

## A-6 — The prompt template teaches the "the engine certified it" dialect; leak is 26x the known 3 seeds

**Severity:** P1. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** agents/strategic/prompts/qwen3_6_27b (accusation_round.j2, vote_ballot.j2) -> spoken meeting text, all 4 sets. **Confidence:** high.
**Merged from:** dialect-leaks#1: The prompt template teaches the "the engine certified it" dialect; leak is 26x the known 3 seeds.

**Claim.** Machinery-oracle vocabulary ("the engine", "the system flagged", "engine-certified") appears in 78 spoken utterances across 44 of 300 committed games, and it originates in two prompt-template lines that literally instruct agents that "The engine certified these" -- not in model invention.

**Finder evidence.**

```
ORIGIN (the game is teaching the words):

  $ grep -n "The engine certified" agents/strategic/prompts/qwen3_6_27b/*.j2
  accusation_round.j2:164:Proof. The engine certified these: only an impostor can vent, so a flag here names one outright and nothing said at this table outweighs it.
  vote_ballot.j2:123:Proof. The engine certified these: only an impostor can vent, so a flag here names one outright, and nothing said at this table outweighs it.

Both lines are inside the `<flagged_contradictions>` block gated on `flag_groups.proof`, and
agents/strategic/prompts/loader.py:411 fixes that bucket to exactly one flag kind:
  _ROLE_PROOF_KINDS: Final[frozenset[str]] = frozenset({"vent_sighting"})

Agents demonstrably SAW the string -- pulled from the recorded prompt bytes:
  $ uv run python - (scan llm_calls[].prompt in replays/ml_corpus/9p2i/replay-seed-1072.jsonl)
  agent: p-2 | call_kind: meeting | model: Qwen/Qwen3.6-27B
  <flagged_contradictions>
  Proof. The engine certified these: only an impostor can vent, so a flag here names one outright...
  - [vent_sighting] p-1 witnessed p-2 vent in STORAGE at tick 7; venting is impostor-only... (subjects: p-2)

CAUSAL SEPARATION IS PERFECT. Over all 668 recorded meetings in the four sets, partitioned on
whether the meeting carries a vent_sighting contradiction (i.e. whether the "The engine certified
these" block renders at all), against whether any spoken free_text or ballot rationale_text in
that meeting matches the oracle net:

  leak rate | vent_sighting flag PRESENT: 45/326 = 13.8%
  leak rate | vent_sighting flag ABSENT :  0/342 =  0.0%
  leaking meetings WITHOUT a vent_sighting flag: 0

Zero leaks in 342 meetings where the line does not render. The vocabulary is taught, not emergent.

VOLUME (net: /the engine/ not followed by room|output, engine-certif|flag|proof|says|confirm|seal,
"the system ... flag|certif|say", "the detector"; run over transcript.turns[].free_text,
transcript.turns[].claims[].reason and ballots[].rationale_text of all 300 games = 11,727 utterances):

  TIER1 out-of-world oracle: 78 utterances, 44 distinct games
    by set    : samples/9p2i 20, ml_corpus/9p2i 50, samples/4p1i 3, ml_corpus/4p1i 5
    by surface: ballot_rationale 39, free_text 28, claim_reason 11
  TIER2 evidence-jargon "flag" as a noun-of-record ("the vent flag is undeniable",
        "no hard flags", "the flags are weak"): 22 further utterances, 18 games

All four committed sets are affected, 9p2i and 4p1i alike. The three seeds named as known
(ml_corpus/9p2i 1134, 1079, 1032) are 3 of 44 games.

REPRESENTATIVE QUOTES (set | seed | meeting | surface | speaker):
  samples/9p2i    | 20   | headless-seed-20:meeting-0   | free_text        | p-9
    "the engine has already flagged that p-2's vent is impossible for a crewmate"
  samples/9p2i    | 20   | headless-seed-20:meeting-0   | ballot_rationale | p-5
    "You claim the engine flagged it, but how do you know the engine isn't just echoing p-1's lie?"
  samples/9p2i    | 19   | headless-seed-19:meeting-0   | ballot_rationale | p-3
    "The engine certified the vent sighting, so p-6 is the impostor."
  ml_corpus/9p2i  | 1034 | headless-seed-1034:meeting-0 | ballot_rationale | p-9
    "And then, the engine's cold truth settled the room ... that mechanical flag leaves no shadow of doubt."
  ml_corpus/9p2i  | 1072 | headless-seed-1072:meeting-0 | free_text        | p-8
    "P-2 is the killer. The system flagged the vent, and that is the end of the discussion."
  ml_corpus/9p2i  | 1119 | headless-seed-1119:meeting-1 | ballot_rationale | p-9
    "the engine certified p-1's witness of p-6 venting in ADMIN, a mechanic only impostors possess"
  ml_corpus/4p1i  | 1035 | headless-seed-1035:meeting-0 | free_text        | p-1
    "The engine flagged it as a certifiable impostor action"
  samples/4p1i    | 6    | headless-seed-6:meeting-0    | claim_reason     | p-1
    "p-2's witness account of p-4 venting is certified by the system flags."

FALSE POSITIVES EXCLUDED BY HAND: 17 in-fiction uses of "engine" (the ship's engine room and the
`align_engine_output` task) -- e.g. samples/9p2i seed 1 p-2 "aligning engine output in Engineering",
ml_corpus/9p2i seed 1009 p-1 "down in the engine room". These are correct in-world speech.

CONTAGION is real but minor -- most leaks are independent draws off the same prompt line rather than
one speaker infecting the table: of the 45 leaking meetings, 40 have a single leaking speaker, and
only 5 have >= 2. Worst case ml_corpus/9p2i seed 1072 meeting-0, where 6 distinct players
(p-1,p-4,p-5,p-6,p-7,p-8) all invoke "the system".

WHY IT MATTERS FOR THE RE-GROUND: every one of the 326 meetings carrying a vent_sighting flag
ejects the flagged venter -- 326/326 = 100%, leak or no leak. So the oracle vocabulary sits
entirely on a path that converts with certainty, and a model fitted to these bytes sees
"say 'the engine certified it'" co-occurring with a guaranteed successful ejection.

NOT the memory render: I scanned the `<memory>` blocks of the recorded prompts across 15 corpus
games and found zero occurrences of "the engine", "flag" or "detector" -- only the belief table's
"suspicion N.NN" rows. The attribution is narrow: these two template lines.
```

**Verifier evidence (independent re-run).**

```
(1) ORIGIN reproduces verbatim.
  $ grep -n "The engine certified" agents/strategic/prompts/qwen3_6_27b/*.j2
  accusation_round.j2:164:Proof. The engine certified these: only an impostor can vent, so a flag here names one outright and nothing said at this table outweighs it.
  vote_ballot.j2:123:Proof. The engine certified these: only an impostor can vent, so a flag here names one outright, and nothing said at this table outweighs it.
  Both sit inside `{% if flag_groups.proof %}` (accusation_round.j2:162-168, vote_ballot.j2:121-127); loader.py:411
  `_ROLE_PROOF_KINDS: Final[frozenset[str]] = frozenset({"vent_sighting"})` -- confirmed at HEAD.
  git blame: the line was introduced by 847ec1a2 (Task 20.31, the v3->v4 prompt bump), replacing "Evidence, not verdicts:".

(2) VOLUME reproduces EXACTLY with an INDEPENDENTLY WRITTEN net (scratchpad/wave0/A/v1/a6.py -- my own regex list,
    not the finder's, over transcript.turns[].free_text + .claims[].reason + ballots[].rationale_text of all 300 games):
  total utterances scanned: 12728
  TIER1 hits: 78  distinct games: 44
  by set: {samples/9p2i: 20, ml_corpus/9p2i: 50, samples/4p1i: 3, ml_corpus/4p1i: 5}
  by surface: {ballot_rationale: 39, free_text: 28, claim_reason: 11}
  -> 78 / 44 / 20-50-3-5 / 39-28-11 all match the filed numbers to the digit.

(3) CAUSAL SEPARATION reproduces exactly:
  meetings: 668
  leak | vent flag PRESENT: 45/326 = 0.138
  leak | vent flag ABSENT : 0/342 = 0.000
  vent-flag meetings ejecting the flagged subject: 326/326
  (the 326/326 conversion claim in "WHY IT MATTERS" is exact.)

(4) AGENTS SAW THE STRING -- pulled from the recorded prompt bytes myself:
  $ python3 (scan llm_calls[].prompt in replays/ml_corpus/9p2i/replay-seed-1072.jsonl)
  p-2 meeting Qwen/Qwen3.6-27B
  '...lagged_contradictions>\nProof. The engine certified these: only an impostor can vent, so a flag here names one
   outright and nothing said at this table outweighs it.\n- [vent_sighting] p-1 witnessed p-2 vent in STORAGE at tick 7;
   venting is impostor-only, and the spoken observation matches the witness's own record. (subjects: p-2)<'
  prompts containing the line in seed 1072: 26

(5) MATCH CENSUS over my 78 hits: 'the engine' 58, 'the system flag' 10, 'engine flag' 4, 'engine-certif' 2,
  'engine proof' 1, "the system's certif" 1, 'the system say' 1, 'the system has flag' 1. Zero 'the detector'.
  Hand-reading all 59 'the engine' contexts found exactly ONE in-fiction survivor
  ("I was busy fixing the engine in Engineering"), so the true Tier-1 count is 77-78, not materially 78.

(6) NOT SPECIFIED. tasks/phase-20.md Task 20.31's DoD requires the block to render the committed taxonomy
  ("Proof" / "Conflicting accounts") and explicitly requires that bookkeeping vocabulary LEAVE the agent's voice
  ("Threshold arithmetic leaves the agent's voice ... the ballot explicitly forbids quoting bookkeeping numbers").
  The exact sentence is nowhere mandated: `grep -rn "engine certified\|The engine" tests/` returns no pin on it
  (only unrelated prose in test comments). So the wording is an implementation choice that runs AGAINST its own
  task's stated intent -- a defect, not a specified behaviour.

(7) NOT A KNOWN-OPEN RE-REPORT. G-29 (audits/review-2026-08-19/A/collated-findings.md:378-385) is
  "Threshold arithmetic and stock rationales" -- "0.60 threshold" x208, verbatim-repeated ballot openings.
  That is precisely the class MACHINERY_VOCABULARY=("threshold","suspicion") nets. The oracle-agency register
  ("the engine flagged it") appears nowhere in the review register. Distinct item.

(8) CASCADE claim checks out: orchestrator/game.py:391 `"qwen3_6_27b": _bespoke_versions("qwen3_6_27b", version="v4")`
  and the recorded stamps read accusation_round.qwen3_6_27b.v4 / vote_ballot.qwen3_6_27b.v4, so a fix is a v4->v5 bump.
```

**Verifier note.** Reproduces to the digit on an independently authored net. Two nits, neither touching claim/severity/classification: (a) the TITLE's "26x the known 3 seeds" divides 78 utterances by 3 seeds -- the like-for-like ratio is 44 games / 3 seeds = 14.7x, and the claim body states the honest form ("3 of 44 games"); (b) the claim says the dialect "originates in two prompt-template lines" -- there is a third rendered oracle noun, vote_ballot.j2:135 "the detector already found an innocent reading for it", which the fix_sketch does name but the claim does not. It is harmless to the attribution because zero of the 78 leaks use "the detector". Classification defect and severity P1 both stand: the vocabulary is taught, contradicts its own task's intent, is unpinned by any test, and sits on the one meeting path that converts 326/326.

**Fix sketch.** Drop the machinery noun from the two lines while keeping the epistemic content, e.g. accusation_round.j2:164 / vote_ballot.j2:123 -> "Proof. Only an impostor can vent, so a sighting here names one outright and nothing said at this table outweighs it." Rename the block header and the surrounding prose off "flag" as well ("flagged_contradictions" -> the in-world word, "a flag here" -> "a sighting here", "the detector already found an innocent reading" -> "there is an innocent reading"). Note the cost: this is a prompt-version bump v4 -> v5 on accusation_round and vote_ballot, which per the version-bump cascade touches the .j2 prompt_id marker line, game.py DEFAULT_PROMPT_VERSIONS, and the live-recorded prompt-version test pin (recorded prompt_versions in the committed bytes read accusation_round.qwen3_6_27b.v4 / vote_ballot.qwen3_6_27b.v4 and are read as-recorded, so committed bytes are unaffected). Because it changes recorded bytes, it wants the one combined re-record rather than a standalone patch.

## A-7 — Hard evidence is uncounterfeitable by construction: 517/517 spoken vent claims are true, zero from impostors

**Severity:** P1. **Classification:** intended-mechanic. **Verdict:** CONFIRMED. **Area:** agents/strategic/prompts/qwen3_6_27b/impostor_report.j2 (role-differentiated output contract, Task 16.13) + meetings/schemas.py SawVentObservation. **Confidence:** high.
**Merged from:** herding-calibration#3: Hard evidence is uncounterfeitable by construction: 517/517 spoken vent claims are true, zero from impostors.

**Claim.** Across all 300 committed games not one impostor ever emits a saw_vent observation and not one spoken vent claim is false, so 'if p-1 says they saw a vent, it is a vent' is a correct policy on these bytes -- the near-unanimous 0.95 hearsay adoption is not miscalibration but a rational response to an environment with no adversarial pressure on its one hard-evidence channel.

**Finder evidence.**

```
COMMAND (verify every spoken hard-evidence claim against the tick record):
  cd /Users/danielkeinan/projects/AiLibi && uv run python - <<'PY'
  ... for each set: build ground-truth {(actor,tick)} from tick actions of type 'vent'/'kill';
      for each spoken observation of type saw_vent/saw_kill check subject role and tick match ... PY
OUTPUT:
  samples/9p2i     saw_vent  n= 106 subject-is-impostor=106/106  exact-tick=26/106  within1tick=106/106
  ml_corpus/9p2i   saw_vent  n= 363 subject-is-impostor=363/363  exact-tick=49/363  within1tick=355/363
  samples/4p1i     saw_vent  n=  20 subject-is-impostor=20/20    exact-tick=5/20    within1tick=20/20
  ml_corpus/4p1i   saw_vent  n=  28 subject-is-impostor=28/28    exact-tick=4/28    within1tick=28/28
  FALSE (subject not an impostor) examples: []            <-- zero, out of 517
  (no saw_kill observation exists anywhere in the corpus -- consistent with known-open G-8)

COMMAND (split by speaker role):
  OUTPUT: ('CREW','grounded') 452  ('CREW','UNGROUNDED') 65   -- and NO ('IMP', *) row at all.
  Impostor observation types actually emitted (9p2i pooled, 844 impostor turns):
    {'whereabouts': 389, 'saw_player': 596, 'saw_move': 322, 'found_body': 41}  -- no saw_vent, ever.

MECHANISM, in the served template (this is deliberate and documented):
  agents/strategic/prompts/qwen3_6_27b/impostor_report.j2:29-36
    'ROLE-DIFFERENTIATED OUTPUT CONTRACT (a recorded 16.13 decision ...): this cover surface keeps the scratch ladder's v0
     accusation-only structure -- "observations" stays an empty list and no self-alibi claim is offered. The qwen3_32b
     directives it replaces (the expected self-alibi + alibi-anchoring observations + the impostor-side saw_vent shape
     advert) are exactly the surface the ladder measured minting the >=44% self-flag on every prior set'
  agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:97 (impostor persona branch)
    '... a vent you used are impostor-only facts, and naming one instantly exposes you.'

CASCADE CONSEQUENCE (the requested single-source propagation number):
  Grouping hearsay ballots (primary_reason_observation_id null, primary_reason_id pointing at ANOTHER player's turn) by (cited turn, target):
  === samples/9p2i
    HARD_SOLO   ballots= 172 meanconf=0.937 frac>=0.9=0.91 target-is-impostor=1.000
    HARD_CORROB ballots=  32 meanconf=0.948 frac>=0.9=0.97 target-is-impostor=1.000
    SOFT_SOLO   ballots=  52 meanconf=0.761 frac>=0.9=0.02 target-is-impostor=0.404
  === ml_corpus/9p2i
    HARD_SOLO   ballots= 513 meanconf=0.937 frac>=0.9=0.90 target-is-impostor=1.000
    HARD_CORROB ballots= 139 meanconf=0.941 frac>=0.9=0.92 target-is-impostor=1.000
    SOFT_SOLO   ballots= 114 meanconf=0.755 frac>=0.9=0.08 target-is-impostor=0.404
  685 pooled ballots resting on ONE uncorroborated witness's spoken hard claim are 100% right -- the crew is UNDER-confident (0.937 stated vs 1.000 realised).
  218/584 9p2i meetings (37%) contain a >=3-follower single-turn cascade; 806 cascade ballots at mean confidence 0.923.

ANCHORS: worked example headless-seed-0:meeting-0 (samples/9p2i) -- p-5's single saw_vent produces five 0.95 hearsay ballots citing turn-0 verbatim ("P-5 saw p-6 vent. That is the only thing that matters." -- p-1; "How do you fake a vent?" -- p-9).
```

**Verifier evidence (independent re-run).**

```
(1) GROUND-TRUTH CHECK reproduces exactly (scratchpad/wave0/A/v1/a7.py -- I rebuilt {(actor,tick)} vent/kill sets
    from every kind=tick actions array, then checked every spoken saw_vent against roles from each set's report):
  samples/9p2i     saw_vent n=106 subj-imp=106/106 exact=26 within1=106 saw_kill=0 speakerroles={CREWMATE:106}
  ml_corpus/9p2i   saw_vent n=363 subj-imp=363/363 exact=49 within1=355 saw_kill=0 speakerroles={CREWMATE:363}
  samples/4p1i     saw_vent n= 20 subj-imp= 20/20  exact= 5 within1= 20 saw_kill=0 speakerroles={CREWMATE:20}
  ml_corpus/4p1i   saw_vent n= 28 subj-imp= 28/28  exact= 4 within1= 28 saw_kill=0 speakerroles={CREWMATE:28}
  TOTAL 517/517 subject-is-impostor; FALSE examples: [] (empty).
  Every one of the filed n / exact-tick / within-1-tick cells matches. saw_kill = 0 corpus-wide, as filed.

(2) SPEAKER-ROLE SPLIT reproduces: no ('IMP', *) row exists at all. Impostor-speaker observation-type census
  over all four sets: {'whereabouts': 395, 'saw_player': 605, 'saw_move': 326, 'found_body': 41} -- no saw_vent, ever.
  (The finding's 389/596/322/41 is the 9p2i-only pool; mine is all four sets. Consistent.)

(3) MECHANISM lines exist verbatim at HEAD:
  agents/strategic/prompts/qwen3_6_27b/impostor_report.j2:28-36 -- "ROLE-DIFFERENTIATED OUTPUT CONTRACT (a recorded
    16.13 decision, authorized by the task hint): ... \"observations\" stays an empty list ... (the expected self-alibi
    + alibi-anchoring observations + the impostor-side saw_vent shape advert) are exactly the surface the ladder
    measured minting the >=44% self-flag on every prior set"
  agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:97 -- "... or a vent you used are impostor-only facts,
    and naming one instantly exposes you."
  This is a documented, deliberate decision -> classification intended-mechanic is CORRECT.

(4) CASCADE numbers: I re-derived the hearsay partition myself (scratchpad/wave0/A/v1/a7c.py; hearsay =
  primary_reason_observation_id null AND primary_reason_id points at another player's turn):
    samples/9p2i   HARD (ballot target == a saw_vent subject in the cited turn) n=217 meanconf=0.939 frac>=0.9=0.93 target-is-impostor=1.000
    samples/9p2i   SOFT (no vent in cited turn)                                 n=102 meanconf=0.735 frac>=0.9=0.04 target-is-impostor=0.324
    ml_corpus/9p2i HARD                                                          n=684 meanconf=0.938 frac>=0.9=0.90 target-is-impostor=1.000
    ml_corpus/9p2i SOFT                                                          n=228 meanconf=0.731 frac>=0.9=0.03 target-is-impostor=0.421
  The load-bearing cell -- target-is-impostor 1.000 on hearsay riding a spoken vent claim -- reproduces exactly, and
  the "crew is UNDER-confident (0.938 stated vs 1.000 realised)" reading holds.

(5) NOT MERELY A KNOWN-OPEN RE-REPORT. audits/review-2026-08-19/A/collated-findings.md:517 already records under
  "Verified-clean (do not re-litigate)": "The vent pipeline is complete: ... vent_sighting 440/440 precise". So the
  PRECISION half is known (at baseline-6). What is NOT in the register is the asymmetry -- that zero impostors ever
  emit the shape -- nor the consequence drawn here. The finding also correctly cites G-8 rather than re-reporting it.
```

**Verifier note.** Every ground-truth number reproduces exactly, including the two the finder could most easily have fudged (exact-tick 26/49/5/4 and within-1-tick 106/355/20/28). Classification intended-mechanic is right and well-sourced to the 16.13 contract text in the served template. One scoping caveat: the HARD_SOLO/HARD_CORROB partition sizes are grouping-definition-dependent -- my reconstruction gives 217/684 where the finder reports 204/652 -- but the claim rests on the precision (1.000) and the confidence (0.94), both of which reproduce on any reasonable reconstruction. P1 for an intended-mechanic is high but defensible here, because the finding is scoped as a re-ground blocker (zero adversarial examples on the crew's most decision-relevant judgement) rather than as a gameplay bug.

**Fix sketch.** The 16.13 contract is intended and should not be reverted blind (it fixed a >=44% impostor self-flag rate). But the re-ground must not read this corpus as evidence that 'trust the first vent claim' is a good POLICY -- it is a good policy only against an opponent who cannot lie about vents. Concretely: (a) label the vent channel as a non-adversarial oracle in the re-ground's feature spec so a fitted crew policy does not collapse onto it; (b) if the ML program wants a fitted deception head at all, the impostor surface needs SOME counterfeit lever restored under a detectable shape (e.g. re-admit saw_vent to the impostor contract now that the grounding chokepoint in meetings/transcript.py mints no flag for an ungrounded claim -- the 16.13 self-flag risk it was removed for is a different failure mode from a deliberate frame); (c) either way, run a counterfeit-vent probe before fitting, because zero adversarial examples means zero gradient on the crew's most decision-relevant judgement.

## A-8 — Pooled accusation ECE 0.30/0.28 is ~40% teammate-firewall artifact, not agent miscalibration

**Severity:** P1. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** eval/accusation_calibration.py. **Confidence:** high.
**Merged from:** herding-calibration#4: Pooled accusation ECE 0.30/0.28 is ~40% teammate-firewall artifact, not agent miscalibration.

**Claim.** The reference accusation_claim_ece cells pool crew and impostor accusations, but the Task 7.12/15.4 teammate firewall makes an impostor accusation structurally incapable of being correct (0 hits in 708 impostor accusations across 200 9p2i games), so 708 guaranteed-miss accusations at mean confidence ~0.67 are being scored as agent overconfidence; crew-only ECE is 0.182/0.175.

**Finder evidence.**

```
COMMAND:
  cd /Users/danielkeinan/projects/AiLibi && uv run python <scratch>/wave0/A/f1_ece_split.py
OUTPUT:
  ===== samples/9p2i
    accusation ALL       ECE=0.3003 bins=6 n=752      <-- reproduces the committed 0.30033244680851046 exactly
    accusation CREW      ECE=0.1819 bins=6 n=561
    accusation IMP       ECE=0.6770 bins=5 n=191
    ballot ALL           ECE=0.1498 bins=4 n=538      <-- reproduces the committed 0.14983271375464421
    ballot no-redirect   ECE=0.1397 bins=4 n=502
  ===== ml_corpus/9p2i
    accusation ALL       ECE=0.2817 bins=6 n=2120     <-- reproduces the committed 0.28170283018867964
    accusation CREW      ECE=0.1745 bins=6 n=1603
    accusation IMP       ECE=0.6719 bins=5 n=517
    ballot ALL           ECE=0.0922 bins=6 n=1503     <-- reproduces the committed 0.0921623419827097

PER-BAND, split by accuser role (ml_corpus/9p2i):
  CREW: n=1603 hitrate=0.661   [0.5,0.6) n=123 rate=0.618 | [0.6,0.7) n=365 rate=0.403 | [0.7,0.8) n=300 rate=0.240 |
                                [0.8,0.9) n= 58 rate=0.293 | [0.9,1.0) n=756 rate=0.989
  IMP : n= 517 hitrate=0.000   [0.5,0.6) n= 14 rate=0.000 | [0.6,0.7) n=268 rate=0.000 | [0.7,0.8) n=162 rate=0.000 |
                                [0.8,0.9) n= 63 rate=0.000 | [0.9,1.0) n= 10 rate=0.000
  samples/9p2i is identical in shape: CREW n=561 hitrate 0.615, IMP n=191 hitrate 0.000.
  708 impostor accusations, 0 hits. The floor is structural, not behavioural:
    meetings/manager.py:1444 `_guard_teammate_turn_claims(normalized_claims, fellow_impostor_ids=...)` strips a teammate accusation
    at the per-turn chokepoint; meetings/manager.py:1456 `exclude_teammate_vent_observations` is its observation-side twin (Task 15.4).
  In 9p2i the ONLY accusation an impostor could make that scores as a hit is against their teammate -- which the guard deletes.

WHY IT MATTERS BEYOND BOOKKEEPING: the pooled curve is non-monotonic in the mid range ([0.5,0.6) 0.56 -> [0.8,0.9) 0.14, i.e. BELOW the ~0.22 base rate),
  which reads as 'higher confidence is anti-predictive'. Roughly half that inversion is the impostor block being folded in; the remainder is
  the genuine turn-order herding of the previous finding. Fitting a confidence head on the pooled label silently teaches the model that
  a 0.85 accusation is worse than a 0.55 one.

INSTRUMENT ANCHOR: eval/accusation_calibration.py:26-40 -- the module deliberately separates the CLAIM curve from the BALLOT curve but
  never splits by ACCUSER role; correctness is `roles[target] == IMPOSTOR` with no conditioning on `roles[speaker]`.
```

**Verifier evidence (independent re-run).**

```
(1) I re-implemented the binning from eval/accusation_calibration.py (_bin_samples: fixed-width deciles,
  index = min(int(c*10), 9), ECE = sum over populated bins of (n_i/N)*|hitrate_i - meanconf_i|) and re-ran it over the
  raw replay bytes with roles from each set's report (scratchpad/wave0/A/v1/a8.py):
  ===== replays/samples/9p2i
    accusation ALL       ECE=0.3003 bins=6 n=752   <- committed cell 0.30033244680851046, reproduced
    accusation CREW      ECE=0.1819 bins=6 n=561
    accusation IMP       ECE=0.6770 bins=5 n=191
    ballot ALL           ECE=0.1498 bins=4 n=538   <- committed cell 0.14983271375464421, reproduced
    ballot no-redirect   ECE=0.1397 bins=4 n=502
  ===== replays/ml_corpus/9p2i
    accusation ALL       ECE=0.2817 bins=6 n=2120  <- committed cell 0.28170283018867964, reproduced
    accusation CREW      ECE=0.1745 bins=6 n=1603
    accusation IMP       ECE=0.6719 bins=5 n=517
    ballot ALL           ECE=0.0922 bins=6 n=1503  <- committed cell 0.0921623419827097, reproduced
  Every filed cell matches to 4 decimal places, on both the pooled reproduction and the split.

(2) PER-BAND split by ACCUSER role reproduces exactly:
  ml_corpus/9p2i CREWMATE n=1603 hitrate=0.661
    0.5:n=123 r=0.618 | 0.6:n=365 r=0.403 | 0.7:n=300 r=0.240 | 0.8:n=58 r=0.293 | 0.9:n=756 r=0.989
  ml_corpus/9p2i IMPOSTOR n=517 hitrate=0.000
    0.5:n=14 r=0 | 0.6:n=268 r=0 | 0.7:n=162 r=0 | 0.8:n=63 r=0 | 0.9:n=10 r=0
  samples/9p2i CREWMATE n=561 hitrate=0.615 ; IMPOSTOR n=191 hitrate=0.000
  191 + 517 = 708 impostor accusations, 0 hits. Mean confidence of those 708, measured: 0.673 ("~0.67" as filed).
  Artifact share: (0.3003-0.1819)/0.3003 = 39.4% and (0.2817-0.1745)/0.2817 = 38.1% -> "~40%" is exact.

(3) INSTRUMENT ANCHOR verified at HEAD. eval/accusation_calibration.py:245-258 `_accusation_claim_samples` builds
  (confidence, is_impostor) with `hit = _is_impostor(game.roles, claim.against, ...)` -- roles[TARGET] only. There is
  no read of roles[turn.speaker] anywhere in the module (`grep -n "roles\[" eval/accusation_calibration.py` -> one hit,
  line 217, inside `_is_impostor` on the target). The docstring (lines 1-60) never mentions accuser role.

(4) MECHANISM verified. meetings/manager.py:1444 `guarded_claims = _guard_teammate_turn_claims(...)`, :1456
  `guarded_observations = exclude_teammate_vent_observations(...)`; the guard body at :3335-3372 calls
  `exclude_teammate_accusation_claims` and then a `drop_teammate_statement_target` backstop, so a teammate accusation
  cannot survive to the record. In 9p2i the teammate is the impostor's ONLY scoring-correct target, hence the exact 0/708.

(5) NOT A KNOWN-OPEN RE-REPORT. collated-findings.md:516 records the firewall as verified-clean ("0 impostor
  accusations aim at a teammate"), and G-30 (:387-392) is about band accuracy, not the pooled ECE cell. Nobody has
  connected the firewall to accusation_claim_ece. New instrument finding.
```

**Verifier note.** Headline claim, severity and classification all stand; the pooled and split ECEs reproduce to 4dp against the committed cells. Two secondary over-statements in the "WHY IT MATTERS" paragraph that a reader should discount, neither load-bearing: (a) "Roughly half that inversion is the impostor block" -- by my numbers the pooled mid-range falls 0.555 -> 0.140 while the CREW-only curve falls 0.618 -> 0.293, so the impostor block explains roughly a fifth of the drop, not half; the inversion is mostly genuine crew herding. (b) "BELOW the ~0.22 base rate" -- the pooled accusation base rate on ml_corpus/9p2i is 0.500 (1060/2120); 0.22 is the 2-of-9 chance prior for a randomly picked target, a different quantity. The fix_sketch (add accusation_claim_ece_by_speaker_role, keep the pooled cell) is a pure addition and moves no recorded number.

**Fix sketch.** Add `accusation_claim_ece_by_speaker_role` (crew / impostor) alongside the existing pooled cell in eval/accusation_calibration.py -- keep the pooled number for continuity, publish the split as the readable one, and note in the docstring that the impostor curve's ceiling is the teammate firewall, not the model. The re-ground should train and evaluate the crew confidence head on crew accusations only.

## A-9 — The shipped machinery-dialect gauge and the actual leak are disjoint sets (0/39 overlap; no net at all over free_text)

**Severity:** P1. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** eval/deduction_metrics.py MACHINERY_VOCABULARY / ScaffoldLeakageCells vs. the committed bytes. **Confidence:** high.
**Merged from:** dialect-leaks#2: The shipped machinery-dialect gauge and the actual leak are disjoint sets (0/39 overlap; no net at all over free_text).

**Claim.** `MACHINERY_VOCABULARY` is the two words ("threshold","suspicion") and catches 0 of the 39 oracle-dialect ballots I found, while the machinery nets are ballot-only so the 28 leaking free_text turns are measured by nothing -- the recorded reports therefore look clean on a surface that is not.

**Finder evidence.**

```
THE NET:
  $ grep -n "MACHINERY_VOCABULARY" eval/deduction_metrics.py
  540:MACHINERY_VOCABULARY: Final[tuple[str, ...]] = ("threshold", "suspicion")

It contains no "engine", no "system", no "detector", no "certified", no "flag" -- i.e. none of the
vocabulary the game's own template teaches (see the sibling finding).

WHAT THE COMMITTED REPORTS SAY (replays/*/tournament-eval-report.json -> deduction.scaffold_leakage):
  $ uv run python -c "import json; [print(s, json.load(open(s+'/tournament-eval-report.json'))['deduction']['scaffold_leakage']) for s in (...)]"
  samples/9p2i    model_machinery_vocabulary_ballots =  8   model_machinery_quotation_ballots = 0   player_visible_leak_turns = 0
  ml_corpus/9p2i  model_machinery_vocabulary_ballots = 23   model_machinery_quotation_ballots = 1   player_visible_leak_turns = 0
  samples/4p1i    model_machinery_vocabulary_ballots =  0   model_machinery_quotation_ballots = 0   player_visible_leak_turns = 0
  ml_corpus/4p1i  model_machinery_vocabulary_ballots =  2   model_machinery_quotation_ballots = 0   player_visible_leak_turns = 0

OVERLAP MEASURED (I reimplemented the net verbatim -- substring match of "threshold"/"suspicion"
over ballots[].rationale_text -- and intersected it with my Tier-1 oracle net over the same 3,602
ballots):
  ballots: 3602
    MACHINERY_VOCABULARY hits reproduced : 32   (shipped cells sum to 33; the one-ballot gap is
                                                 because the shipped net runs on the pre-guard
                                                 model_body at deduction_metrics.py:2418, I ran on
                                                 the recorded rationale_text -- close enough to
                                                 confirm the reproduction)
    my Tier-1 oracle hits                : 39
    overlap                              :  0
    Tier-1 missed by the shipped net     : 39

Zero overlap. The gauge counts a different, mostly-innocent population ("p-2's suspicion of me is a
distraction", samples/9p2i seed 3 p-5 -- ordinary English) and sees none of the real leak.

THE FREE_TEXT HOLE. `player_visible_leak_turns` reads 0 on all four sets, but it is NOT a dialect
gauge -- it is documented at eval/deduction_metrics.py:259 as "the partner net over player-visible
free_text", i.e. the omniscience (teammate-naming) net. Its 0 is a correct reading of what it
measures. The point is what is missing: deduction_metrics.py:1567-1575 scopes both machinery cells
"over ALL ballots", and there is no machinery net over turns at all. So the 28 free_text turns in
which a player says "the engine flagged it" are counted by no instrument in the fold.

The module is honest about this in its own docs ("Every net is a substring or regex match ... a
phrase list cannot see a leak it does not list", "does NOT claim the nets are exhaustive"), so this
is a coverage hole rather than a miscount -- but it is the hole the entire observed leak class falls
through, and it is why the leak survived to baseline 7.

WHAT DOES WORK, for contrast: the decimal net (MACHINERY_DECIMAL_PATTERN = r"0\.\d\d") is sound
and fires correctly exactly once -- ml_corpus/9p2i seed 1125 meeting-3, p-1 ballot: "since p-9's
suspicion is only 0.55 and ...", matching the reported model_machinery_quotation_ballots = 1 on that
set and 0 elsewhere. That one is a genuine violation of vote_ballot.j2:185's explicit instruction
("never quote a suspicion score or any other bookkeeping figure in \"rationale_text\"") -- 1 in
3,602 ballots, so that guard is holding.
```

**Verifier evidence (independent re-run).**

```
(1) THE NET reproduces at HEAD.
  $ grep -n "MACHINERY_VOCABULARY" eval/deduction_metrics.py
  540:MACHINERY_VOCABULARY: Final[tuple[str, ...]] = ("threshold", "suspicion")
  Two words. No "engine", "system", "detector", "certified" or "flag".

(2) THE COMMITTED CELLS reproduce exactly (read straight out of replays/*/tournament-eval-report.json
    -> deduction.scaffold_leakage):
  samples/9p2i    machinery_vocabulary=8   machinery_quotation=0  player_visible_leak_turns=0
  ml_corpus/9p2i  machinery_vocabulary=23  machinery_quotation=1  player_visible_leak_turns=0
  samples/4p1i    machinery_vocabulary=0   machinery_quotation=0  player_visible_leak_turns=0
  ml_corpus/4p1i  machinery_vocabulary=2   machinery_quotation=0  player_visible_leak_turns=0

(3) OVERLAP reproduces exactly (scratchpad/wave0/A/v1/a9.py -- I re-implemented the shipped net verbatim
    (substring "threshold"/"suspicion") and intersected it with my OWN Tier-1 oracle net over the same ballots):
  ballots: 3602
  MACHINERY_VOCABULARY hits reproduced : 32   (shipped cells sum to 33; the 1-ballot gap is exactly the stated
                                               cause -- deduction_metrics.py:2418 runs `_matches(model_body, ...)`
                                               on the PRE-GUARD model_body, I ran on recorded rationale_text)
  my Tier-1 oracle hits                : 39
  overlap                              :  0
  Zero overlap confirmed independently.

(4) THE FREE_TEXT HOLE is real and structural. eval/deduction_metrics.py:2333-2351 is the only loop over
  transcript.turns; the only net applied to free_text is
    2350:  if _matches(turn.free_text, PARTNER_PHRASES):
    2351:      acc.player_visible_leak += 1
  Neither MACHINERY_VOCABULARY nor MACHINERY_DECIMAL_PATTERN is applied to any turn surface. The machinery cells are
  scoped "over ALL ballots" at :1567-1575. So the 28 free_text hits (and, unmentioned by the finding, the 11
  claim_reason hits) from my A-6 scan are measured by no instrument in the fold. The finding is also right that
  player_visible_leak_turns = 0 is a CORRECT reading of a different question (the partner/omniscience net).

(5) THE CONTRAST CASE verifies to the exact ballot. The decimal net fires once corpus-wide, and it is
  ml_corpus/9p2i seed 1125 meeting-3, voter p-1:
    "...and since p-9's suspicion is only 0.55 and p-6 is even lower, I really don't want to waste a vote on a guess..."
  matching model_machinery_quotation_ballots = 1 on that set and 0 on the other three. vote_ballot.j2 does carry the
  explicit prohibition on quoting bookkeeping figures in rationale_text, so 1/3602 means that guard is holding.

(6) NOT SPECIFIED-AS-INTENDED, but honestly disclosed. eval/deduction_metrics.py:297-299 states "a phrase list cannot
  see a leak it does not list ... does NOT claim the nets are exhaustive", and :541-546 labels MACHINERY_VOCABULARY an
  explicit UPPER BOUND. The finding concedes this in its own text ("a coverage hole rather than a miscount"), so the
  claim is not overreaching.
```

**Verifier note.** Every number reproduces, including the 1-ballot gap between my 32 and the shipped 33 and its stated cause. Within the canonical taxonomy's three values (defect / intended-mechanic / acceptable-emergent) "defect" is the only fit -- but read it as a COVERAGE GAP, not a miscount: no shipped cell computes a wrong number, and the module documents its own non-exhaustiveness. The finding says exactly this, so no correction is required. Note the finding UNDERSTATES its own hole: my A-6 scan puts 11 further oracle hits on transcript.turns[].claims[].reason, also ungauged, so the unmeasured spoken surface is 39 utterances, not 28. Severity P1 is defensible only as the paired instrument half of A-6 (it is why that leak survived to baseline 7); standing alone it would read P2. Fix is a pure addition and moves no recorded cell.

**Fix sketch.** Two changes to eval/deduction_metrics.py, both cheap and both pure additions so no recorded number moves: (1) extend MACHINERY_VOCABULARY with the out-of-world oracle terms the templates actually teach -- "the engine", "engine-certified", "engine flag", "the detector", "the system flagged", "certified" -- ideally as a separate high-precision `MACHINERY_ORACLE` cell rather than folding them into the self-declared upper-bound cell, since these terms (unlike "suspicion") have no innocent in-world reading; (2) run the machinery nets over transcript.turns[].free_text and .claims[].reason as well as ballots, emitting e.g. `model_machinery_turns` beside `player_visible_leak_turns`, so the spoken surface has a gauge at all. Re-run the fold on the committed bytes to get the baseline-7 number on the record before the re-ground.

## A-10 — The HOW behind the 42 pooled innocent ejections: a per-case ledger (reporter 30, counter-accusation boomerang 29, provably-false transit 17, impostor-rides-the-herd 33, hearsay pile-on 79 of 145 ejecting ballots, weak-flag 5, guard-redirect 4)

**Severity:** P1. **Classification:** defect. **Verdict:** ADJUSTED. **Area:** evidence-economy / centerpiece table (the 42 innocent ejections); also meetings (ballot provenance) and recorded innocent ejections / guard attribution. **Confidence:** high.
**Merged from:** evidence-economy#7: The full 42-row innocent-ejection ledger (the HOW behind the recorded number), herding-calibration#6: How the 42 innocent ejections happened: flagless hearsay pile-ons at ~0.8 confidence, crew-driven 2:1 over impostor-driven, ballots-vs-speech#8: 4 of the 42 pooled innocent ejections are guard-attributable (new quantification of a known-open item).

**Claim.** Keep the entire ledger and every class total as filed. Correct ONE number inside the evidence-economy claim: "with only 4 of the 42 reducible to a defensible 'no alibi, last suspect standing' read" is wrong on the finding's OWN ledger. Six rows carry no tag beyond IMP-RIDES and/or PIT -- S9 4:m0, S9 27:m2, C9 1008:m2, C9 1036:m1, C9 1066:m0, C9 1106:m3 -- and the filed list omits C9 1036 and C9 1106. The parenthetical "3 of those 4 are PIT anyway" is also wrong on the filed ledger: 3 of the SIX are PIT (S9 4, S9 27, C9 1036), not 3 of 4. Under the strict reading the finding evidently intends (PIT is itself an injustice tag, so PIT rows are not defensible), the defensible-on-available-information set is the THREE rows carrying only IMP-RIDES: C9 1008:m2, C9 1066:m0, C9 1106:m3. So the correct sentence is "6 of the 42 carry no tag beyond the generic herd and/or a provably-false transit; only 3 (C9 1008:m2, C9 1066:m0, C9 1106:m3) are pure herd." Two supporting cells also drift by one under a different modal/plurality tie-break and should be quoted as approximate: pile driver CREW 27 -> I measure 28 (IMPOSTOR 12 agrees, NONE 3 -> 2), and IMP-RIDES pivotal 14 -> I measure 13.

**As originally filed.** MERGE NOTE: merged from 3 finders (evidence-economy, herding-calibration, ballots-vs-speech). All three are decompositions of the SAME known-open item -- the 42 pooled innocent ejections, previously recorded only as a count -- attacked from three complementary angles: evidence-economy's per-case 42-row classified ledger, herding-calibration's citation-channel/provenance mix, and ballots-vs-speech's guard attribution. SEVERITY DISAGREEMENT: evidence-economy P1, herding-calibration P2, ballots-vs-speech P3 -- highest kept (P1). CLASSIFICATION DISAGREEMENT: evidence-economy and herding-calibration classified 'defect'; ballots-vs-speech classified 'acceptable-emergent' (its slice was only the 4 guard-touched cases, where it also found the guard PREVENTED 6 other innocent ejections, i.e. net -4). 'defect' kept. All three independently reproduce the recorded 42 and the per-set split 14/26/1/1, and all three agree on the 4 redirect-assisted cases. Read together they give the full HOW: class totals (reporter 30, counter-accusation boomerang 29, provably-false impossible-transit 17, impostor-rides-the-herd 33 of which 14 pivotal, weak-flag 5, guard-redirect 4, forced endgame <=3 voters 5), the citation mix of the 145 ejecting ballots (79 hearsay / 40 own-observation / 26 own-turn / 0 uncited), the modal pile source (CREWMATE 27 vs IMPOSTOR 12), and the flag status (37 of 42 ejectees carried no contradiction flag at all).

[claim as filed by evidence-economy] Every one of the 42 pooled innocent ejections is a body-report meeting (0 emergency), and each falls into a small set of named, overlapping injustice classes -- reporter-convicted 30, counter-accusation boomerang 29, provably-false impossible-transit 17, impostor-rides-the-herd 33 (pivotal 14), non-informative weak-flag 5, gate-redirect 4, forced endgame at <=3 voters 5 -- with only 4 of the 42 reducible to a defensible 'no alibi, last suspect standing' read.

[claim as filed by herding-calibration] Quantifying a known-open item (the 42 pooled innocent ejections as a NUMBER is recorded; HOW each happened was not): 37 of the 42 ejected innocents carried no contradiction flag at all, 79 of the 145 ballots that ejected them were hearsay citations of another player's turn with no first-hand observation, and the pile's most-cited source was a CREWMATE in 27 cases versus an impostor in only 12.

[claim as filed by ballots-vs-speech] Independently recomputing the pooled innocent-ejection count reproduces the recorded 42 exactly, and 4 of them ejected a player carrying graph-redirected ballots — in 3 of those 4 the redirect was outcome-changing, including one where an impostor would otherwise have been ejected.

**Finder evidence.**

```
==============================================================================
EVIDENCE AS FILED BY FINDER: evidence-economy
(its severity P1, classification defect, confidence high)
title: The full 42-row innocent-ejection ledger (the HOW behind the recorded number)
==============================================================================

This deepens the KNOWN-OPEN item 'the 42 pooled innocent ejections as a NUMBER'; what follows is the HOW, per case.

COMMAND (per-case classifier; full script at scratchpad/wave0/A/, dossier of all 42 transcripts+ballots at scratchpad/wave0/A/innocent42.txt):
  uv run python - <<'PY'
  ... for each ejecting meeting with roles[ejected]=='CREWMATE', tag:
      RC        ejected == m['triggered_by']
      BOOM      turn1 accusation names turn0's speaker AND ejected == turn0 speaker
      PIT       >=1 convicting ballot matches the impossibility regex (finding 3)
      WEAKFLAG  ejected is the subject of any non-vent contradiction this meeting
      REDIRECT  >=1 convicting ballot carries "[under-gate eject target ... redirected]"
      IMP-RIDES a living impostor voted for the ejectee
      ENDGAME   <=3 ballots cast
  PY

OUTPUT (set / seed / meeting / victim / mechanism / tally):
  S9    2 meeting-0 p-5  PIT+WEAKFLAG(alibi_conflict,alibi_vs_sighting)+REDIRECT+IMP-RIDES   {SKIP:2, p-5:5}
  S9    4 meeting-0 p-9  PIT+IMP-RIDES                                                        {p-9:6, p-6:1}
  S9    6 meeting-2 p-1  RC+BOOM+IMP-RIDES                                                    {SKIP:2, p-1:3}
  S9   19 meeting-3 p-1  RC+BOOM+IMP-RIDES                                                    {p-9:1, SKIP:1, p-1:3}
  S9   21 meeting-2 p-4  RC+BOOM+PIT+IMP-RIDES                                                {SKIP:2, p-4:3}
  S9   24 meeting-1 p-2  RC+BOOM+IMP-RIDES                                                    {SKIP:2, p-2:4}
  S9   27 meeting-2 p-9  PIT+IMP-RIDES                                                        {p-9:4, SKIP:1}
  S9   37 meeting-1 p-2  PIT                                                                  {SKIP:2, p-2:3, p-1:1}
  S9   42 meeting-2 p-1  RC+BOOM+IMP-RIDES                                                    {SKIP:2, p-1:3}
  S9   44 meeting-1 p-9  RC+BOOM+WEAKFLAG(alibi_vs_sighting)+IMP-RIDES                        {p-9:5, SKIP:1}
  S9   44 meeting-2 p-1  RC+BOOM+PIT+IMP-RIDES                                                {SKIP:1, p-1:3}
  S9   46 meeting-3 p-1  RC+BOOM+WEAKFLAG(alibi_vs_sighting)+IMP-RIDES                        {SKIP:2, p-1:3}
  S9   47 meeting-3 p-4  RC+BOOM+PIT+IMP-RIDES                                                {p-4:3, SKIP:1}
  S9   48 meeting-1 p-2  RC+BOOM+PIT+IMP-RIDES                                                {SKIP:1, p-2:4}
  C9 1008 meeting-2 p-8  IMP-RIDES                                                            {p-8:4, SKIP:1}
  C9 1010 meeting-1 p-1  RC+BOOM+IMP-RIDES                                                    {SKIP:2, p-1:4}
  C9 1015 meeting-2 p-5  PIT+IMP-RIDES                                                        {p-5:4, SKIP:1}
  C9 1020 meeting-2 p-7  RC+BOOM                                                              {p-7:3, SKIP:1, p-9:1}
  C9 1032 meeting-2 p-4  RC+BOOM+IMP-RIDES+ENDGAME                                            {p-4:2, SKIP:1}
  C9 1036 meeting-1 p-9  PIT+IMP-RIDES                                                        {SKIP:2, p-9:3}
  C9 1039 meeting-0 p-6  RC+BOOM+PIT                                                          {p-6:4, SKIP:3}
  C9 1044 meeting-0 p-7  WEAKFLAG(alibi_conflict,alibi_vs_sighting)+REDIRECT+IMP-RIDES        {SKIP:3, p-7:4}
  C9 1045 meeting-3 p-9  REDIRECT+IMP-RIDES                                                   {p-9:3, SKIP:1}
  C9 1052 meeting-0 p-8  RC+BOOM+IMP-RIDES                                                    {p-8:6, SKIP:2}
  C9 1058 meeting-1 p-1  RC+BOOM+PIT+IMP-RIDES                                                {SKIP:2, p-1:3}
  C9 1066 meeting-0 p-9  IMP-RIDES                                                            {p-9:5, SKIP:2}
  C9 1082 meeting-1 p-1  RC+BOOM                                                              {SKIP:2, p-1:3}
  C9 1085 meeting-0 p-1  WEAKFLAG(alibi_conflict,alibi_vs_sighting)+REDIRECT                  {p-2:1, SKIP:2, p-1:3}
  C9 1092 meeting-2 p-2  RC+BOOM                                                              {SKIP:1, p-9:1, p-2:2}
  C9 1093 meeting-3 p-6  RC+BOOM+PIT                                                          {p-9:1, SKIP:1, p-6:2}
  C9 1106 meeting-3 p-1  IMP-RIDES                                                            {SKIP:1, p-1:3}
  C9 1111 meeting-0 p-2  RC+BOOM+PIT                                                          {SKIP:3, p-2:5}
  C9 1112 meeting-2 p-1  RC+BOOM                                                              {SKIP:2, p-1:3}
  C9 1127 meeting-4 p-8  RC+BOOM+IMP-RIDES+ENDGAME                                            {p-8:2, p-6:1}
  C9 1135 meeting-0 p-2  RC+IMP-RIDES                                                         {p-2:4, SKIP:2, p-8:1}
  C9 1137 meeting-2 p-4  RC+BOOM+IMP-RIDES                                                    {SKIP:1, p-1:1, p-4:3}
  C9 1140 meeting-3 p-5  RC+BOOM+PIT+IMP-RIDES                                                {p-5:3, SKIP:1}
  C9 1143 meeting-3 p-3  RC+BOOM+PIT+IMP-RIDES+ENDGAME                                        {p-3:2, SKIP:1}
  C9 1144 meeting-2 p-1  RC+BOOM+IMP-RIDES                                                    {SKIP:1, p-1:5}
  C9 1146 meeting-1 p-1  RC+BOOM+PIT+IMP-RIDES                                                {SKIP:3, p-1:4}
  S4   39 meeting-0 p-2  RC+BOOM+IMP-RIDES+ENDGAME                                            {p-2:2, SKIP:1}
  C4 1021 meeting-0 p-2  RC+BOOM+IMP-RIDES+ENDGAME                                            {SKIP:1, p-2:2}

CLASS TOTALS: RC 30, BOOM 29, PIT 17, IMP-RIDES 33 (pivotal in 14), WEAKFLAG 5, REDIRECT 4, ENDGAME<=3 5. All 42 are trigger='report'; 0 emergency. By set: S9 14, C9 26, S4 1, C4 1 -- matching audits/audit-phase-20-baseline-7.md's recorded 14/26/1/1.

REASONABLE-ON-AVAILABLE-INFORMATION vs INJUSTICE: only 4 of the 42 carry no injustice tag other than the generic herd (S9 4, S9 27, C9 1008, C9 1066 -- and 3 of those 4 are PIT anyway). The 5 ENDGAME cases (3 living, 1 impostor) are a forced 50/50 and I count them as reasonable-on-information. C9 1127 meeting-4 is the sharpest single injustice in the set: with 3 alive, the impostor p-6 openly testified "I was in Reactor at tick 34 with p-3 alive" -- placing itself at the kill site one tick before the kill -- and the table ejected the reporter p-8 2-1 anyway.

==============================================================================
EVIDENCE AS FILED BY FINDER: herding-calibration
(its severity P2, classification defect, confidence high)
title: How the 42 innocent ejections happened: flagless hearsay pile-ons at ~0.8 confidence, crew-driven 2:1 over impostor-driven
==============================================================================

COMMAND:
  cd /Users/danielkeinan/projects/AiLibi && uv run python - <<'PY'
  ... for every meeting whose ejected_player_id is not in roles(recs): classify each ballot naming them by
      citation channel (own observation id / another player's turn / own turn / none), collect the flags naming them,
      and find the modal cited turn's speaker ... PY
OUTPUT:
  TOTAL innocent ejections: 42  Counter({'ml_corpus/9p2i': 26, 'samples/9p2i': 14, 'samples/4p1i': 1, 'ml_corpus/4p1i': 1})
    (pooled 9p2i = 40, 4p1i = 2 -- matches the recorded 42)
  flags on the ejected innocent:
    Counter({(): 37, ('alibi_conflict','alibi_vs_sighting'): 3, ('alibi_vs_sighting',): 2})
  citation mix of the 145 ejecting ballots:
    Counter({'hearsay': 79, 'own_obs': 40, 'own_turn': 26, 'other_obs': 0, 'none': 0})
    (zero uncited ejects -- the Task 16.6 citation gate is working; it coerces those to SKIP)
  mean confidence of the ejecting ballots, per ejection:
    Counter({~0.8: 33, ~0.7: 7, ~0.9: 2})
  driver of the pile (modal cited other-speaker turn among the ejecting ballots):
    CREW 27   IMPOSTOR 12   NONE 3
    follower counts on that one source: CREW {1:9, 2:12, 3:5, 4:1}   IMPOSTOR {1:5, 2:4, 3:3}
  impostor ballots that joined the pile: 38 of 53 impostor ballots cast in these meetings named the ejected innocent
    (the impostors pile on, but they are not the originators in 27/42 cases).
  redirect-assisted: 4 of the 42 had at least one guard-redirected ballot on the ejected player (11 such ballots total).

SHAPE, in one sentence: the modal innocent ejection is a flag-free meeting in which one crewmate's movement/timeline read is
  repeated by two or three others who cite that turn rather than any observation, at a mean stated confidence of 0.8 --
  i.e. exactly the turn>=2 noise band of the soft-channel finding, converted into an outcome.

ANCHORS (full table at <scratch>/wave0/A/innocent_ejections.json):
  samples/9p2i headless-seed-2:meeting-0  -> p-5 ejected, source p-3 (CREW), 3 followers, 5 ejecting ballots of 7
  samples/9p2i headless-seed-24:meeting-1 -> p-2 ejected, source p-4 (IMPOSTOR), 3 followers
  samples/9p2i headless-seed-48:meeting-1 -> p-2 ejected, source p-9 (CREW), 3 followers, confs [0.65,0.75,0.85]
  ml_corpus/9p2i headless-seed-1146:meeting-1 -> p-1 ejected, source p-9 (CREW), 4 followers, confs [0.75,0.65,0.75,0.75]
  ml_corpus/9p2i headless-seed-1055:meeting-0 -> p-9 pile at confs [0.95,0.9,0.9] (highest-confidence flagless innocent pile in the corpus)

==============================================================================
EVIDENCE AS FILED BY FINDER: ballots-vs-speech
(its severity P3, classification acceptable-emergent, confidence high)
title: 4 of the 42 pooled innocent ejections are guard-attributable (new quantification of a known-open item)
==============================================================================

This is new quantification of the KNOWN-OPEN "42 pooled innocent ejections as a NUMBER (recorded; what is NOT yet known is HOW each happened)" — I am deepening it, not re-reporting it.
  innocent ejections (all 4 sets): 42
    per set: ml_corpus/9p2i 26, samples/9p2i 14, samples/4p1i 1, ml_corpus/4p1i 1
  with >=1 graph-redirected ballot ON the ejectee: 4
    replays/samples/9p2i seed=2 headless-seed-2:meeting-0: ejected p-5 on 5/7 redirected ballots
    replays/ml_corpus/9p2i seed=1044 headless-seed-1044:meeting-0: ejected p-7 on 2/7 redirected ballots
    replays/ml_corpus/9p2i seed=1045 headless-seed-1045:meeting-3: ejected p-9 on 1/4 redirected ballots
    replays/ml_corpus/9p2i seed=1085 headless-seed-1085:meeting-0: ejected p-1 on 3/6 redirected ballots
  Cross-referencing the outcome counterfactual (F1): 3 of the 4 flip under unwind — samples/9p2i 2:m0 would have ejected p-1 (also CREWMATE, a crew-for-crew swap); ml_corpus/9p2i 1044:m0 would have SKIPPED (so the guard CAUSED this innocent ejection); ml_corpus/9p2i 1085:m0 would have ejected p-2 (IMPOSTOR, so the guard COST the crew an impostor). 1045:m3 does not flip.
  Symmetrically, the guard PREVENTED 6 innocent ejections that would otherwise have been recorded (ml_corpus/9p2i 1013:m1, 1020:m3, 1045:m2, 1093:m2, 1143:m1 and samples/9p2i 12:m0 all recorded SKIPPED where the authored ballots eject a CREWMATE), so the guard's net effect on innocent ejections is roughly -4.
  Method: roles re-derived per seed with orchestrator.seeder.seed_initial_state over each set's roster.json (mirroring scripts/build_sample_report.py:122-140); the tally recompute matches the recorded outcome in 668/668 meetings, so the ejectee list is exact.
  38 of the 42 have no guard involvement at all — the remaining HOW is a speech/evidence question outside this dimension.
```

**Verifier evidence (independent re-run).**

```
(1) THE 42 AND THE PER-SET SPLIT reproduce (scratchpad/wave0/A/v1/a10.py, roles from each set's report):
  TOTAL innocent ejections: 42
  per set: {samples/9p2i: 14, ml_corpus/9p2i: 26, samples/4p1i: 1, ml_corpus/4p1i: 1}
  -- matching audits/audit-phase-20-baseline-7.md:233-238 (14 / 26 / 1 / 1, pooled 42, bar 2 MISSED against <35).

(2) THE CLASS TOTALS reproduce EXACTLY under an independently written classifier (my own PIT regex, my own BOOM rule):
  {RC: 30, BOOM: 29, PIT: 17, IMP-RIDES: 33, WEAKFLAG: 5, REDIRECT: 4, ENDGAME: 5}
  -- identical to the filed RC 30 / BOOM 29 / PIT 17 / IMP-RIDES 33 / WEAKFLAG 5 / REDIRECT 4 / ENDGAME<=3 5.

(3) THE 42-ROW LEDGER reproduces ROW FOR ROW, including every vote tally. All 42 (set, seed, meeting, victim, tally)
  tuples match the filed table. Only two rows' tag strings differ, and only on the regex-dependent PIT tag:
  C9 1036:m1 (I get IMP-RIDES, filed PIT+IMP-RIDES) and C9 1044:m0 (I get PIT+..., filed no PIT) -- they cancel, so
  the PIT total is 17 on both classifiers. PIT is a judgement net in both readings and should be quoted as such.

(4) THE CITATION MIX AND FLAG MIX reproduce EXACTLY:
  ejecting ballots: 145  citation mix: {hearsay: 79, own_obs: 40, own_turn: 26, other_obs: 0, none: 0}
  flags on the ejected innocent: {(): 37, (alibi_conflict, alibi_vs_sighting): 3, (alibi_vs_sighting,): 2}
  -- 79/145 hearsay and 37/42 flagless, exactly as filed. Zero uncited ejecting ballots (the 16.6 citation gate holds).

(5) "ALL 42 ARE report, 0 emergency" VERIFIED by classifying every meeting's trigger from the tick action stream:
  all meetings by trigger kind: {report: 618, emergency: 50}   (= 668)
  innocent ejections by trigger kind: {report: 42}   (emergency: 0)
  And the reporter class is exact: 30 of the 618 report meetings ejected their own reporter, and all 30 of those
  ejectees are CREWMATE -- i.e. RC 30 accounts for 71% of every innocent ejection in the record.

(6) THE GUARD ATTRIBUTION (ballots-vs-speech leg) VERIFIES CASE BY CASE. I unwound each redirect marker to its
  authored target and re-tallied (scratchpad/wave0/A/v1/a10b.py, a10c.py):
    samples/9p2i seed 2 m0   ejected p-5(CREW) on 5/7 redirected; unwound tally SKIP 2 / p-1 5 -> p-1 (CREWMATE) = crew-for-crew swap
    ml_corpus 1044 m0        ejected p-7(CREW) on 2/7 redirected; unwound SKIP 3 / p-7 2 / p-4 2 -> SKIP  (the guard CAUSED it)
    ml_corpus 1045 m3        ejected p-9(CREW) on 1/4 redirected; unwound p-9 2 / p-4 1 / SKIP 1 -> p-9  (does not flip)
    ml_corpus 1085 m0        ejected p-1(CREW) on 3/6 redirected; unwound p-2 4 / SKIP 2 -> p-2 (IMPOSTOR) (the guard COST an impostor)
  All 4 redirect-assisted cases, the 3-of-4 flip count and both directional readings verify.
  The 6 guard-PREVENTED cases verify too -- each recorded SKIPPED, each unwinding to a CREWMATE ejection:
    1013:m1 SKIP2/p-9 3 (CREW) | 1020:m3 SKIP1/p-6 2 (CREW) | 1045:m2 p-1 4 (CREW)/p-3 1 |
    1093:m2 p-6 3 (CREW)/SKIP2 | 1143:m1 p-9 4 (CREW)/SKIP3 | samples/9p2i 12:m0 p-2 4 (CREW)/SKIP3
  So "net roughly -4" (6 prevented vs 2 caused) is arithmetically right.

(7) THE ACCEPTANCE ARITHMETIC in the fix_sketch checks out: pooled ejections are {IMPOSTOR: 387, CREWMATE: 42},
  387/429 = 0.902 -- the quoted 90.2% baseline is exact.

(8) THE SHARPEST CASE verifies verbatim. ml_corpus/9p2i seed 1127 meeting-4, tick 38, 3 ballots:
    p-6 (IMPOSTOR) free_text: "1. I was in Reactor at tick 34 with p-3 alive. 2. p-9 was in Cafeteria until tick 38 ...
      3. p-8 moved from Cafeteria to East Hall at tick 36, placing them near the kill site shortly after."
    BALLOT p-6(IMP)->p-8 0.85 | p-8(CREW)->p-6 0.65 | p-9(CREW)->p-8 0.85  -> reporter p-8 ejected 2-1.
  Exactly as described.

(9) WHAT DOES NOT REPRODUCE (the basis for ADJUSTED): the "only 4 of the 42" sentence -- see corrected_claim.
  Reading the filed ledger itself, six rows carry nothing beyond IMP-RIDES/PIT, not four, and of those six three are
  PIT, not "3 of those 4". Two further cells drift by one on tie-breaks: I measure pile-driver CREW 28 / IMP 12 /
  NONE 2 against the filed 27/12/3, and IMP-RIDES pivotal 13 against the filed 14.
```

**Verifier note.** Severity P1 and classification 'defect' both STAND -- I am not adjusting them. The merge's transparency is a point in its favour: it discloses the P1/P2/P3 and defect/acceptable-emergent disagreements and names the ballots-vs-speech net -4 finding rather than burying it. Two things a reader of this row should hold onto. First, this is by its own admission a DEEPENING of a recorded known-open item (42 pooled innocent ejections, audits/audit-phase-20-baseline-7.md §3 bar 2, MISSED against <35), and its own fix_sketch says 'No new lever here beyond findings 1, 3, 5 and 6' -- so it is an acceptance-test artifact, not an independently actionable defect, and should be scheduled with the levers it scores rather than as its own work item. Second, the single most consequential number in it is one the filed claim buries: RC 30 means 30 of 618 report meetings ejected their own reporter and every one of those 30 was innocent (71% of the whole innocent-ejection population), which sits against the prior review's recorded verdict on G-31 (audits/review-2026-08-19/D/cross-track-map.md:89, 'Good news, actually: the ballot-time guard works ... only 3 reporters were ever ejected'). The finding never names G-31 or the reporter_exculpation resolver (meetings/manager.py:2479, unconditional since Task 15.7) that is supposed to prevent exactly this; whoever routes the balance wave should treat that as the live question.

**Fix sketch.** [fix as filed by evidence-economy] No new lever here beyond findings 1, 3, 5 and 6; this row-level ledger is the acceptance test for them. Applying (a) the reporter eject-gate, (b) suppressing endpoint-tick adjacent-room weak flags, and (c) the map-refuted-transit stamp would, on these exact bytes, remove 34 of the 42 innocent ejections and 0 of the 387 impostor ejections -- pooled ejection accuracy 90.2% -> 98.0%. Re-record and re-run this classifier as the close check; anything that survives should be a forced-endgame case, which is the only class here I would defend as the game working.

[fix as filed by herding-calibration] The corrective lever is the same as the soft-channel finding's: a follower who names an already-accused, ZERO-FLAG target should not be able to state 0.8+ without attaching an observation id. A narrower, cheaper guard also exists -- extend the Task 16.6 citation gate so that on a zero-flag target a hearsay-only citation (primary_reason_id pointing at another player's turn, primary_reason_observation_id null) caps the ballot's contribution rather than counting as a full conviction vote. Worth measuring before shipping: 79 of 145 innocent-ejecting ballots are exactly that shape, but so is a large share of correct regime-A ballots, so the gate must condition on zero-flag.

[fix as filed by ballots-vs-speech] Record this attribution alongside the 42 so the number stops being a bare count: 4 guard-touched, 3 of them outcome-changing, against 6 guard-prevented. Once the redirect finding's record fix lands, re-run this attribution as the regression that proves the record now says what happened.

## A-11 — Turn order is destiny: the counter-accusation boomerang convicts the opener in 29/42 innocent ejections and 0/387 impostor ejections

**Severity:** P2 (finder: P1). **Classification:** acceptable-emergent (unchanged), but the headline asymmetry is a restatement of an already-disclosed structural prior rather than new evidence; substantially overlaps prior art G-31 'Reporter-blame is the default deflection, and it works' (audits/review-2026-08-19/A/collated-findings.md:394-402, P1, corrob 8). **Verdict:** ADJUSTED. **Area:** evidence-economy / does deduction decide. **Confidence:** high.
**Merged from:** evidence-economy#4: Turn order is destiny: the counter-accusation boomerang convicts the opener in 29/42 innocent ejections and 0/387 impostor ejections.

**Claim.** In the 668 committed meetings the vent flag is deterministic (326/326 vent-flag meetings eject, and the ejectee is the vent subject 326/326), and in the no-flag half the meeting either skips (239/342) or converges on the accusation pile-up (modal target 88/103). Within that no-flag half the reporter/opener is ejected in 29 of the 42 innocent ejections, and in 29 of those 30 opener-ejections the turn-1 reply had counter-accused the opener. DROP the '0 of 387 impostor ejections' contrast and the 'turn order is destiny' framing: (a) the opener IS the meeting trigger actor in 668/668 meetings and the trigger actor is a CREWMATE in 668/668 (the disclosed structural reporter-innocence prior, replays/ml_corpus/README.md item 1), so 'ejectee == opener' is mathematically impossible for an impostor ejection -- the 0/387 is a tautology, not a measured asymmetry, and it cannot support 'the meeting rewards rebuttal position rather than evidence'; (b) the boomerang shape is a near-universal reply template (492/668 meetings) that convicts the opener in only 29/492 = 5.9% overall and 29/271 = 10.7% within the no-vent-flag half. It IS a real predictor (10.7% vs 1/71 = 1.4% without the boomerang, ~8x), but it is not destiny. Note also that turn-0 = the reporter and the reply's optional counter-accusation are BOTH specified (DESIGN.md:496-505), so fix-sketch (b) 'randomise who opens' is a design change against the written protocol, not a defect repair.

**As originally filed.** Deduction does not decide the ballot -- the vent flag does (326/326 deterministic), and where there is no vent flag the meeting either skips (239/342) or converges on whoever the turn-1 reply counter-accused: in 29 of 42 innocent ejections the opener accused someone, the reply counter-accused the opener, and the opener was ejected, a shape that occurs in 0 of 387 impostor ejections, while 311/387 impostor ejections are simply the opener's own named target.

**Finder evidence.**

```
COMMAND (turn-order shape per ejection):

  uv run python - <<'PY'
  import json, collections
  SETS={"S9":"replays/samples/9p2i","C9":"replays/ml_corpus/9p2i","S4":"replays/samples/4p1i","C4":"replays/ml_corpus/4p1i"}
  def analyze(role_wanted):
      s=collections.Counter()
      for tag,d in SETS.items():
          r=json.load(open(f"{d}/tournament-eval-report.json"))
          for g in r["report"]["games"]:
              roles=g["roles"]
              for m in g["meetings"]:
                  ej=m.get("ejected_player_id")
                  if not ej or roles[ej]!=role_wanted: continue
                  s["n"]+=1
                  turns=m["transcript"]["turns"]; opener=turns[0]["speaker"]
                  op_acc=[c["against"] for c in turns[0]["claims"] if c.get("type")=="accusation" and c.get("against")]
                  boom = len(turns)>1 and any(c.get("against")==opener for c in turns[1]["claims"] if c.get("type")=="accusation")
                  if boom: s["reply_counteraccuses_opener"]+=1
                  if boom and ej==opener: s["boomerang_convicted_opener"]+=1
                  if op_acc and ej in op_acc: s["openers_own_target_ejected"]+=1
      return s
  print("CREWMATE",dict(analyze("CREWMATE"))); print("IMPOSTOR",dict(analyze("IMPOSTOR")))
  PY

OUTPUT:
  CREWMATE {'n': 42,  'reply_counteraccuses_opener': 37, 'boomerang_convicted_opener': 29, 'openers_own_target_ejected': 7}
  IMPOSTOR {'n': 387, 'reply_counteraccuses_opener': 258, 'boomerang_convicted_opener': 0, 'openers_own_target_ejected': 311}

COMMAND (what decides, split on the presence of a role_proof flag) -- same loop, bucketing by whether any vent_sighting flag exists:

OUTPUT (668 meetings pooled):
  VENT-FLAG MEETINGS:    n=326, ejected=326 (P=1.000), ejectee == vent subject 326/326 (P=1.000)
  NO-VENT-FLAG MEETINGS: n=342, skipped=239, ejected=103 (P=0.301), of which innocent 42 (40.8%)
     of the 103: ejectee == modal accusation target across all turns  88 (85.4%)
                 ejectee == the FIRST player accused in the meeting   65 (63.1%)
                 ejectee == the meeting's body reporter               30 (29.1%)
                 ejectee named by ANY weak-signal flag                 5 ( 4.9%)

So in the no-flag half, the strongest single predictor of who dies is the meeting's own accusation pile-up, and the weak structured evidence predicts almost nothing.

QUOTED SPECIMEN of the boomerang (S9 seed 21 meeting-2, reporter/opener p-4 ejected 3-2; the surviving impostor is p-5):
  t0 p-4 (opening, reporter): "I walked into REACTOR at tick 24 and found p-9's body there ... With p-2 already ejected, p-1 is the only one with a clear line to the scene."
  t1 p-1 (reply, counter-accuses the opener): "Actually, your timeline is completely backwards ... You're trying to pin this on me because you can't explain your own sudden appearance at the kill zone."
  t2 p-8: "You say you found the body at 24, but you were standing right next to me in CAFETERIA at tick 19! ... You're the one who killed p-9!"
  t3 p-5 (IMPOSTOR) joins: "You had the time and the access to kill p-9, and your timeline is a lie."
  Ballots: p-5(I)->p-4, p-6->p-4, p-8->p-4, p-1 SKIP, p-4 SKIP. Tally {'SKIP':2,'p-4':3}.

AND THE IMPOSTOR RIDES IT. Over the 42 innocent ejections there were 53 living-impostor ballots: 38 (71.7%) voted for the innocent the herd had chosen, 11 SKIP, 4 elsewhere. The impostor voted for the ejectee in 33 of the 42 meetings, and in 14 of those the impostor's ballot was PIVOTAL (removing it leaves no unique plurality on the ejectee). By contrast, on the 387 impostor ejections the living impostors cast 576 ballots of which 448 were SKIP.
```

**Verifier evidence (independent re-run).**

```
CMD 1 (verbatim re-run of the finding's own script, scratchpad/v2/a11.py):
  CREWMATE {'n': 42, 'reply_counteraccuses_opener': 37, 'boomerang_convicted_opener': 29, 'openers_own_target_ejected': 7}
  IMPOSTOR {'n': 387, 'openers_own_target_ejected': 311, 'reply_counteraccuses_opener': 258}
  -> exact reproduction (0/387 = key absent).

CMD 2 (flag split, scratchpad/v2/a11b.py):
  total meetings 668; contradiction kinds {'vent_sighting': 448, 'alibi_vs_sighting': 100, 'alibi_conflict': 60, 'alibi_vs_physical': 13}
  VENT-FLAG: n=326 ejected=326 ejectee==vent subject=326
  NO-FLAG:   n=342 skipped=239 ejected=103 innocent=42
     modal=88 first=65 reporter=30 weakflag=5
  -> every published cell reproduces exactly.

CMD 3 (impostor ballots, scratchpad/v2/a11c.py):
  innocent ejections 42 {'total': 53, 'for_ejectee': 38, 'else': 4, 'skip': 11}; meetings where impostor voted ejectee 33; pivotal 14
  impostor ejections 387 {'total': 576, 'skip': 448}
  -> exact reproduction.

CMD 4 -- THE REFUTING CONTROL (scratchpad/v2/a11d.py):
  meetings 668  opener==triggered_by 668
  opener role {'CREWMATE': 668}
  trigger role {'CREWMATE': 668}
  ejectee role x (ejectee==opener) {('IMPOSTOR', False): 387, ('CREWMATE', False): 12, ('CREWMATE', True): 30}
  -> an impostor is NEVER the opener, so boomerang_convicted_opener==0 for impostor ejections is structurally forced. Documented at replays/ml_corpus/README.md:127-138 ('The absolute reporter-innocence prior (structural)') and agents/tactical/impostor_policy.py.

CMD 5 -- BASE RATE OF THE BOOMERANG (scratchpad/v2/a11e.py, a11f.py):
  turn-1 counter-accuses opener: 492/668 -> opener ejected 29, other ejected 266, skip 197
  no boomerang: 176 -> opener ejected 1
  NO-VENT-FLAG, boomerang present: n=271 ejected=74 opener-ejected=29 (10.7%)
  NO-VENT-FLAG, no boomerang:      n=71  ejected=29 opener-ejected=1 (1.4%)

SPEC CHECK: DESIGN.md:496-505 -- 'The body-reporter (or emergency caller) takes turn 0 ... The accused responds (turn_kind = "reply" ...) a counter-claim / defense, and OPTIONALLY a counter-accusation of someone.' The seat order and the counter-accusation are both specified.
```

**Verifier note.** Every published number reproduces bit-for-bit; nothing in the measurement is wrong. What fails is the inference. The finding's own fix_sketch sentence -- 'a counter-accusation from the accused wins 29/42 of the time against the reporter and never once against a real impostor' -- is the load-bearing claim, and its second half is unfalsifiable on this substrate: the scripted FSM impostor never reports and never calls a meeting, so it is never in the opener seat and the shape cannot occur. Conditioned properly, the boomerang is a reply template present in 73.7% of all meetings that convicts the opener 5.9% of the time. The genuine, defensible residue -- an ~8x lift on opener-ejection and a 29-of-30 overlap with the reporter seat -- is worth carrying into the balance wave, but at P2 and stated as a lift, not as 'turn order is destiny'. Also note this substantially re-reports G-31 from the immediately preceding review, where the same phenomenon was filed at P1 corrob 8 on baseline-6 bytes ('only 3 reporters were ever ejected' there vs 30 here -- the baseline-7 delta IS new and is the part worth keeping).

**Fix sketch.** Emergent herd dynamics are legitimate content, but the ASYMMETRY is not: a counter-accusation from the accused wins 29/42 of the time against the reporter and never once against a real impostor, which means the meeting rewards rebuttal position rather than evidence. Two levers, both cheap: (a) the reporter-gate in finding 1 removes the 29-of-30 overlap directly; (b) randomize or rotate which living player opens a body-report meeting instead of always seating the reporter at turn 0 -- on these bytes turn 0 is simultaneously the highest-exposure seat and the guaranteed-innocent seat, which is what makes the boomerang a free impostor win. For the re-ground, feature-engineer turn_index explicitly so the shortcut is visible rather than baked in silently.

## A-12 — The 'impossible transit' charge convicts 17 of 42 innocents and is provably false every time

**Severity:** P1. **Classification:** acceptable-emergent (unchanged) -- confirmed as a model-reasoning failure, not a substrate gap: the <map> card is present in every meeting call and states the exact adjacency the ballots deny. **Verdict:** ADJUSTED. **Area:** evidence-economy / innocent-conviction mechanism. **Confidence:** high.
**Merged from:** evidence-economy#3: The 'impossible transit' charge convicts 17 of 42 innocents and is provably false every time.

**Claim.** In 17 of 42 innocent ejections at least one convicting ballot asserts a physical impossibility ('teleport', 'impossible travel', 'must have vented'), and in 15 of 42 (35.7%) at least half of the convicting ballots do; the map card that pre-empts exactly this error is rendered in every meeting prompt (8/8 llm_calls in the verified anchor). REPLACE 'and is provably false every time' -- the test performed (ejectee's reconstructed route is map-legal AND they never vented) is true by construction for every crewmate in every game, because the engine rejects a non-adjacent move and vent is impostor-only, so 17/17 carries no information about the ballots. Per-ballot falsity is demonstrated only for the hand-checked anchors (both verified below); the honest claim is 'asserts a physical impossibility about a player who could not have performed one'. REPLACE the '4.6x ENRICHED' figure: it pools vent-flag meetings, in which an innocent ejection is structurally impossible (0/326). Within the no-vent-flag stratum the enrichment is 15/19 = 78.9% innocent against a 42/103 = 40.8% base = 1.9x. Finally, 'carried by' should quote the >=half figure (15/42 = 35.7%), not the >=1 figure (17/42).

**As originally filed.** 40.5% of innocent ejections (17/42) are carried by convicting ballots asserting a physical impossibility ('teleport', 'impossible', 'must have vented'), and in all 17 the ejectee's true recorded route was hop-by-hop map-legal and they never vented -- the engine cannot emit an illegal transit and crewmates cannot vent, so the argument is a structural false positive, yet it is used in a majority of convicting ballots in 15/42 innocent vs 18/387 impostor ejections.

**Finder evidence.**

```
COMMAND (reconstruct each ejectee's ground-truth route from the replay tick actions and test every consecutive hop against the map graph):

  uv run python - <<'PY'
  import json, collections, yaml, re, os
  m=yaml.safe_load(open("engine/maps/canonical_1.yaml"))
  adj=collections.defaultdict(set)
  for e in m["edges"]: adj[e["from"]].add(e["to"]); adj[e["to"]].add(e["from"])
  SETS={"S9":"replays/samples/9p2i","C9":"replays/ml_corpus/9p2i","S4":"replays/samples/4p1i","C4":"replays/ml_corpus/4p1i"}
  PAT=re.compile(r"impossib|teleport|can'?t (?:be|walk|get|reach|make|sprint)|cannot (?:be|walk|get|reach|traverse)|must have vent|had to vent|you vented|they vented|not a walk|faster than|physically",re.I)
  def load_tracks(path):
      pos=collections.defaultdict(lambda:"CAFETERIA"); track=collections.defaultdict(dict); vents=collections.defaultdict(list)
      for line in open(path):
          o=json.loads(line)
          if o.get("kind")!="tick": continue
          t=o["tick"]
          for p in list(pos): track[p][t]=pos[p]
          for a in o["actions"]:
              act=a["actor"]; track[act][t]=pos[act]
              if a["type"]=="move": pos[act]=a["payload"]["to_room"]
              elif a["type"]=="vent": vents[act].append(t); pos[act]="(VENT)"
      return track,vents
  illegal=rhet=ok=total=0
  for tag,d in SETS.items():
      r=json.load(open(f"{d}/tournament-eval-report.json"))
      for g in r["report"]["games"]:
          roles=g["roles"]
          crew=[mm for mm in g["meetings"] if mm.get("ejected_player_id") and roles[mm["ejected_player_id"]]=="CREWMATE"]
          if not crew: continue
          track,vents=load_tracks(os.path.join(d,g["replay_ref"]))
          for mm in crew:
              ej=mm["ejected_player_id"]; total+=1
              tr=track[ej]; ts=sorted(tr)
              bad=[(a,b) for a,b in zip(ts,ts[1:]) if tr[a]!=tr[b] and tr[b] not in adj[tr[a]]]
              if bad: illegal+=1
              conv=[b for b in mm["ballots"] if b["target"]==ej]
              if any(PAT.search(b["rationale_text"] or "") for b in conv):
                  rhet+=1
                  if not bad and not vents[ej]: ok+=1
  print(total, illegal, rhet, ok)
  PY

OUTPUT:
  innocent ejections examined: 42
    ejectee's ACTUAL route contained an illegal (non-adjacent) hop: 0
    convicting ballots contain physical-impossibility rhetoric: 17
    ...of those, ejectee's real route was fully map-legal AND they never vented: 17

RATE ASYMMETRY (same PAT over all 429 ejections):
  innocent ejections with >=1 such convicting ballot: 17/42 = 40.5%;  >=half: 15/42 = 35.7%
  impostor ejections with >=1:                        90/387 = 23.3%; >=half: 18/387 =  4.7%
  Among the 33 ejections where >=half of convicting ballots carry the rhetoric: 15 CREWMATE / 18 IMPOSTOR = 45.5% innocent, against a 9.8% (42/429) innocent base rate -- the argument is 4.6x ENRICHED for wrong verdicts.

ANCHOR 1 -- S9 seed 47 meeting-3, reporter p-4 (CREWMATE) ejected 3-1.
  Ground-truth route (reconstructed from replays/samples/9p2i/replay-seed-47.jsonl ticks 20-26):
    {20:'MEDBAY',21:'MEDBAY',22:'WEST_HALL',23:'ADMIN',24:'EAST_HALL',25:'ENGINEERING',26:'REACTOR'}
  Every hop is one declared edge. engine/maps/canonical_1.yaml: "- { from: ENGINEERING, to: REACTOR, kind: doorway, traversal_ticks: 1 }". The only vent actions in the whole game are p-1 (t21,t22) and p-9 (t23,t24) -- both impostors, neither p-4.
  Ballots: p-7 "p-4 claims Engineering at tick 25 but found a body in Reactor at 26. That is a teleport, not a walk. Get them out."; p-5 "A man can't walk from Engineering to Reactor in a single tick, so p-4's story is as thin as ice."; p-1 (IMPOSTOR) "p-4's commute from Engineering to Reactor in one tick is faster than my sense of humor, so I'm voting them out."

ANCHOR 2 -- C9 seed 1039 meeting-0, reporter p-6 (CREWMATE) ejected 4-2.
  Ground-truth route (replays/ml_corpus/9p2i/replay-seed-1039.jsonl ticks 0-8):
    {0:'CAFETERIA',1:'EAST_HALL',2..6:'ENGINEERING',7:'EAST_HALL',8:'CAFETERIA'} -- all legal edges.
  Ballots: p-3 "p-6's timeline is a lie. You don't teleport from East Hall to Cafeteria in one tick. Eject them now."; p-4 "p-6's teleport from Engineering to Cafeteria is a plot hole I can't fix with a wrench, so they're out."
  Both impostors got the physics right and voted SKIP: p-9 (IMPOSTOR) "You all scream teleportation, but I killed p-2 myself. The timeline holds. No one else is guilty. Skip."; p-5 (IMPOSTOR) "the herd is wrong to eject p-6; their timeline is physically possible, so I skip to avoid wasting a vote on a crewmate."

THE SUBSTRATE ALREADY TRIED TO PREVENT THIS. The recorded prompt for seed 47 meeting-3 (llm_calls[0], agent p-4) contains a <map> card:
  "Rooms and doors. Every door below is ONE tick of walking ... - ENGINEERING: EAST_HALL, REACTOR, STORAGE ... Two accounts that name rooms one door apart at nearby ticks can BOTH be honest -- that is one tick of walking."
  The table asserted the exact contradiction of a card sitting in the same prompt.
```

**Verifier evidence (independent re-run).**

```
CMD 1 (verbatim re-run of the finding's script, scratchpad/v2/a12.py):
  innocent ejections: 42  illegal-route: 0  rhetoric-convicted: 17  of-those-clean: 17
  innocent >=half: 15
  impostor ejections: 387  >=1 rhetoric: 90  >=half: 18
  -> exact reproduction of every published cell.

CMD 2 -- ANCHOR 1 verified end to end (samples/9p2i seed 47 meeting-3):
  p-4 route t20-26: {20:'MEDBAY',21:'MEDBAY',22:'WEST_HALL',23:'ADMIN',24:'EAST_HALL',25:'ENGINEERING',26:'REACTOR'}
  vent actions by actor: {'p-1': [21,22], 'p-9': [23,24]}   (roles: p-1 IMPOSTOR, p-9 IMPOSTOR, p-4 CREWMATE)
  engine/maps/canonical_1.yaml: {'from':'ENGINEERING','to':'REACTOR','kind':'doorway','traversal_ticks':1}
  convicting ballots: p-7 'p-4 claims Engineering at tick 25 but found a body in Reactor at 26. That is a teleport, not a walk.'; p-5 "A man can't walk from Engineering to Reactor in a single tick"; p-1 (IMPOSTOR) 'faster than my sense of humor'.
  -> the charge is false and the transit is a single declared edge.

CMD 3 -- the map card is in EVERY call of that meeting, not just the opener:
  Counter({('meeting', True): 8})   # (call_kind, '<map>' in prompt)
  card text: '- ENGINEERING: EAST_HALL, REACTOR, STORAGE' and 'Two accounts that name rooms one door apart at nearby ticks can BOTH be honest -- that is one tick of walking.'

CMD 4 -- THE STRATIFIED CONTROL the finding omits (scratchpad/v2/a12b.py):
  ('NOFLAG','CREWMATE','half') 15 | ('NOFLAG','CREWMATE','nohalf') 27
  ('NOFLAG','IMPOSTOR','half')  4 | ('NOFLAG','IMPOSTOR','nohalf') 57
  ('VENT','IMPOSTOR','half')   14 | ('VENT','IMPOSTOR','nohalf')  312
  VENT:   P(innocent | >=half rhetoric) = 0/14 = 0.0%;  base P(innocent|ejected) = 0/326
  NOFLAG: P(innocent | >=half rhetoric) = 15/19 = 78.9%; base P(innocent|ejected) = 42/103 = 40.8%
  -> 1.9x within-stratum, not 4.6x pooled.

CMD 5 -- REGEX OVER-TRIGGER on the impostor side (same script, sampled hits):
  m9p2i 1023 m2 IMPOSTOR: 'I watched p-6 vent in ADMIN. That is impossible for a crewmate.'
  m9p2i 1079 m2 IMPOSTOR: 'venting is impossible for crew, so p-7 is the impostor.'
  -> these are TRUE statements about venting, not impossible-transit charges; the impostor-side counts (90, 18) are upper bounds.
```

**Verifier note.** The measurement reproduces exactly and the mechanism is real: I independently confirmed the strongest anchor, the map edge, and that the pre-empting <map> card is rendered in all 8 meeting calls of that meeting -- so this is genuinely a 27B reasoning failure with the substrate already in place. Two things must change. (1) 'provably false every time' is carried by a tautology: engine/rules + engine/tick reject non-adjacent moves and vent is impostor-only, so all 42 innocent ejectees pass that test whether or not any ballot was false; the falsity of the specific charges is shown only for the anchors. (2) The 4.6x enrichment double-counts the vent-flag stratum where an innocent ejection cannot occur; the honest within-stratum figure is 1.9x. Severity stays P1 -- 15/42 innocent ejections carried by a map-refutable argument is material for the ML re-ground, and the fix (stamp map-SATISFIED transits as refuted, the mirror of alibi_vs_physical) is cheap. Prior art worth naming: the 2026-08-19 review's consolidated recommendation #7 (collated-findings.md:552-553, corrob w3/w4/w6/w7) proposed exactly this fix; A-12's real advance is showing the card shipped at baseline 7 and the failure persisted.

**Fix sketch.** This is a 27B reasoning failure, not a missing substrate: the <map> card is rendered and explicitly pre-empts the error. Cheapest real fix is a mechanical arbiter rather than more prompt text -- extend the existing map_aware_arbitration flag so that an accusation whose stated reason asserts a room-pair/tick-gap transit that the map graph SATISFIES is stamped 'map-refuted' in the rendered evidence (the mirror of alibi_vs_physical, which currently only fires when geometry is violated). A refuted transit claim should carry negative weight for the claimant instead of positive weight against the accused. For the ML re-ground, the immediate mitigation is to label the 17 identified meetings (list in the finding's per-case table) so the optimizer is not shown 'assert an adjacent-room walk is a teleport' as a winning move; on these bytes it wins 45.5% of the time against innocents.

## A-13 — Action priority is player-id alphabetical: seat p-9 loses 10.6% of its actions, p-1 none, and p-8/p-9 never win a contested meeting trigger

**Severity:** P2 (finder: P1). **Classification:** specified-behaviour / known-open design choice (was: defect). **Verdict:** ADJUSTED. **Area:** flow-edges / action ordering; also pacing / meeting trigger fairness. **Confidence:** high.
**Merged from:** flow-edges#2: Action priority is player-id alphabetical, so seat p-9 loses 10.6% of its actions and seat p-1 loses none, legibility-pacing#3: Report/emergency ties resolve lexicographically by player id: p-8 and p-9 never win one.

**Claim.** The measurement stands verbatim -- actor-lexicographic ordering plus the meeting early-return produce a strictly monotone per-seat action-loss gradient (p-1 0.00% -> p-9 10.62% over the 200 committed 9p2i games) and decide all 106 contested meeting-trigger ticks in favour of the lowest id (p-1 59, p-8 0, p-9 0). But this is NOT a defect: the ordering rule is SPECIFIED verbatim in DESIGN.md:334 ('Intra-tick simultaneity is canonically id-ordered: queued actions resolve in ascending actor-id order ... This is the documented rule, not a race (2026-06-07 audit decision); revisit only if a future wave gates on per-seat fairness'), it is pinned by tests/orchestrator/test_action_ordering.py::test_order_actions_for_tick_sorts_by_actor_without_mutating_input, and the identical per-seat consequence was already adjudicated by the 2026-08-19 review as G-10 'CONFIRMED-DESIGN-CHOICE' with the standing rule 'Any per-seat metric ever published must control for it' (audits/review-2026-08-19/D/cross-track-map.md:75). Re-file as a specified design choice with a named open fairness question, at P2. The genuinely new content is (a) the drop-rate quantification and (b) the honest negative result that the LARGER gradient -- the uncontested trigger-rate skew, p-1 172 vs p-9 33 -- is not produced by the sort and is not root-caused.

**As originally filed.** MERGE NOTE: merged from 2 finders (flow-edges, legibility-pacing) with the same root cause -- orchestrator/action_ordering.py:33-40 keys the tick's action sort on (actor, type, payload), i.e. lexicographic player id, and engine/tick.py:599 returns on the first meeting-triggering action. SEVERITY DISAGREEMENT: flow-edges P1, legibility-pacing P2 -- highest kept (P1). Both classified 'defect'. flow-edges uniquely supplies the monotone per-seat drop gradient (p-1 0.00% -> p-9 10.62% of submitted actions silently discarded, no exception); legibility-pacing uniquely supplies the contested-trigger distribution (p-1 wins 59 of 106 contested ticks, p-8 and p-9 win zero) plus a SEPARATE, larger uncontested submission gradient which it reports honestly as measured but not root-caused. Both note the same consequence: 'who called this meeting' is a first-class feature (reporter_exculpation) handed out along a player-index gradient.

[claim as filed by flow-edges] Because order_actions_for_tick sorts actor-first and the meeting transition aborts the remainder of the queue, the probability that an action is executed at all is a strict monotone function of the player's id -- p-1 0.00% dropped, p-9 10.62% dropped across the 200 committed 9p2i games -- a seat-order handicap a model fitted to these bytes will learn as a property of the seat.

[claim as filed by legibility-pacing] When two or more living players submit a report or emergency on the same tick, the winner is decided by string-sorting the actor id, so p-1 wins 59 of 106 contested ticks and p-8/p-9 win zero -- and, uncontested, the report rate itself falls monotonically with player index even after controlling for exposure.

**Finder evidence.**

```
==============================================================================
EVIDENCE AS FILED BY FINDER: flow-edges
(its severity P1, classification defect, confidence high)
title: Action priority is player-id alphabetical, so seat p-9 loses 10.6% of its actions and seat p-1 loses none
==============================================================================

CODE
orchestrator/action_ordering.py:34-40 -- the sort key is actor-first:
    def _action_order_key(action: Action) -> tuple[str, str, str]:
        action_payload = json.dumps(action.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return action.actor, action.type, action_payload
and _validate_unique_actors guarantees one action per actor, so the order is
exactly lexicographic player id. Combined with the abort at engine/tick.py:599-600,
whoever triggers the meeting cuts off every higher-id seat.

MEASUREMENT (200 games: replays/samples/9p2i + replays/ml_corpus/9p2i,
re-walked with eval.replay_walk.walk_replay, verify_tick_hashes=True)
$ PYTHONPATH=... uv run python .../scan4.py
    9p2i seat-order bias -- recorded actions that the engine silently discarded:
      p-1: dropped    0 / submitted  3654 =  0.00%
      p-2: dropped  110 / submitted  3302 =  3.33%
      p-3: dropped  166 / submitted  3206 =  5.18%
      p-4: dropped  220 / submitted  3446 =  6.38%
      p-5: dropped  215 / submitted  3239 =  6.64%
      p-6: dropped  263 / submitted  3417 =  7.70%
      p-7: dropped  273 / submitted  3218 =  8.48%
      p-8: dropped  329 / submitted  3627 =  9.07%
      p-9: dropped  467 / submitted  4398 = 10.62%
Monotone in seat index with no exception. The gradient is not a policy effect:
it is produced entirely by ticks whose meeting trigger sorts below the seat.

The same ordering also decides the two-trigger race: on all 106 ticks that
carried two report/emergency actions, the lower-id caller always wins and is
recorded as `triggered_by` (e.g. samples/9p2i s13 t8 p-2 report beats p-7
report; s19 t13 p-4 beats p-5; s20 t11 p-1 emergency beats p-9 emergency).
So "who called this meeting" -- a first-class feature in the meeting record and
in the reporter_exculpation substrate flag -- is partly an alphabetical artifact.

==============================================================================
EVIDENCE AS FILED BY FINDER: legibility-pacing
(its severity P2, classification defect, confidence high)
title: Report/emergency ties resolve lexicographically by player id: p-8 and p-9 never win one
==============================================================================

ALL findings fold the same reconstruction. Built once with (cwd = repo root):

  PYTHONPATH=. uv run python scratchpad/wave0/A/dump.py scratchpad/wave0/A/dump.json

dump.py re-seeds every committed seed and replays it through
`eval.replay_walk.walk_replay` under a profile with `verify_tick_hashes=True`
(so every reconstructed tick matched the recorded `state_hash`), recording per
tick: the recorded actions, the ENGINE events (`engine.events.event_to_dict`),
alive set, per-player rooms, bodies, sabotage state, task counts; plus every
meeting row verbatim (transcript turns, ballots, contradictions, llm_calls with
their full prompts) and the `game_over` row. Roles come from
`eval.validity.roles_by_seed` (re-seeding, same recipe). Reconstruction was
clean: 0 errors over 50 + 150 + 50 + 50 = 300 games (samples/9p2i 50,
ml_corpus/9p2i 150, samples/4p1i 50, ml_corpus/4p1i 50); rosters resolved to
(9,2,2) and (4,1,1).

Ordering key: orchestrator/action_ordering.py:33-40 sorts by `(actor, type, payload)`;
engine/tick.py:599 returns on the FIRST meeting-triggering action.

Fold over dump.json:

  trigger-actor distribution over all 668 meetings:
    {'p-1':231,'p-2':126,'p-3':70,'p-4':52,'p-5':41,'p-6':47,'p-7':29,'p-8':39,'p-9':33}

  split by whether the tick was contested (>1 living report/emergency submitted):
    CONTESTED (106 ticks): {'p-1':59,'p-2':24,'p-3':9,'p-4':2,'p-5':6,'p-6':4,'p-7':2}
        -> p-8: 0, p-9: 0.  Monotone in id, exactly the sort order.
    UNCONTESTED (562 ticks): {'p-1':172,'p-2':102,'p-3':61,'p-4':50,'p-5':35,
                              'p-6':43,'p-7':27,'p-8':39,'p-9':33}

The uncontested half is a SEPARATE, larger gradient and is not an ordering
artifact -- it is in the submission rate, and it survives an exposure control:

  ml_corpus/9p2i, report+emergency ACTIONS submitted per 100 CREW living-ticks:
    p-1 6.35 | p-2 3.72 | p-3 2.47 | p-4 2.06 | p-5 2.25 | p-6 2.19 |
    p-7 2.06 | p-8 2.20 | p-9 2.14
  (p-9 has the MOST crew living-ticks in that set -- 2,758 vs p-1's 2,159 -- and
   still triggers 23 meetings to p-1's 137.)

  samples/4p1i: submissions per 100 crew-ticks p-1 5.95 | p-2 4.10 | p-3 1.44 | p-4 0.00
  (p-4 submitted zero reports across 50 games; there were no contested ticks at
   all in that set, so the gradient there is entirely policy/geometry.)

Why it matters for the re-ground: `reporter_exculpation` is one of the 21
unconditional substrate flags, so the exculpation bonus is handed out along a
player-index gradient.  A model fitted on these bytes will learn "low index =>
reporter => cleared" as a positional prior.

Honest limit: I proved the mechanism for the CONTESTED half only. The
uncontested gradient is reported as an observation; I did not establish its
root cause (candidates: index-deterministic task assignment putting low-index
crew on high-traffic routes, or an index-correlated policy path).
```

**Verifier evidence (independent re-run).**

```
CMD (independent JSONL-only fold, no re-simulation, scratchpad/v2/a13.py -- 'dropped' = any recorded action whose actor sorts after the meeting's triggered_by on a meeting tick):
  meetings 668  total recorded actions 35350  dropped 2166  6.13%
  9p2i seat-order (200 games):
    p-1: dropped    0 / submitted  3654 =  0.00%
    p-2: dropped  110 / submitted  3302 =  3.33%
    p-3: dropped  166 / submitted  3206 =  5.18%
    p-4: dropped  220 / submitted  3446 =  6.38%
    p-5: dropped  215 / submitted  3239 =  6.64%
    p-6: dropped  263 / submitted  3417 =  7.70%
    p-7: dropped  273 / submitted  3218 =  8.48%
    p-8: dropped  329 / submitted  3627 =  9.07%
    p-9: dropped  467 / submitted  4398 = 10.62%
  trigger actor over all 668 meetings: {'p-1':231,'p-2':126,'p-3':70,'p-4':52,'p-5':41,'p-6':47,'p-7':29,'p-8':39,'p-9':33}
  contested ticks: 106 {'p-1':59,'p-2':24,'p-3':9,'p-4':2,'p-5':6,'p-6':4,'p-7':2}   -> p-8 0, p-9 0
  uncontested: {'p-1':172,'p-2':102,'p-3':61,'p-4':50,'p-5':35,'p-6':43,'p-7':27,'p-8':39,'p-9':33}
  -> every published cell of both finders reproduces exactly.

CODE: orchestrator/action_ordering.py:34-40 `_action_order_key -> (action.actor, action.type, action_payload)`; `_validate_unique_actors` makes actor alone total. engine/tick.py:593-600 returns inside the apply loop on the MEETING transition.

SPEC (the decisive check the finding did not run):
  $ sed -n '334p' DESIGN.md  ->  '... Intra-tick simultaneity is canonically id-ordered: queued actions resolve in ascending actor-id order, so a lower-id target's same-tick move legitimately escapes a kill. This is the documented rule, not a race (2026-06-07 audit decision); revisit only if a future wave gates on per-seat fairness.'
  $ grep -n 'def test' tests/orchestrator/test_action_ordering.py -> test_order_actions_for_tick_sorts_by_actor_without_mutating_input

PRIOR ADJUDICATION:
  audits/review-2026-08-19/D/cross-track-map.md:75 -- 'G-10 | Contested kills 100% decided by player id (156/156 lower-id escape, 90/90 higher-id die; per-seat escape p-1 24.7% -> p-9 0%). CONFIRMED-DESIGN-CHOICE -- DESIGN.md:334 states it verbatim and names per-seat fairness as its own open item ... Any per-seat metric ever published must control for it'
```

**Verifier note.** Nothing in the numbers is wrong -- I reproduced all of them by an independent path. The classification is. Both merged finders filed 'defect', and the flow-edges half asserts a seat handicap 'a model fitted to these bytes will learn as a property of the seat' without checking whether the ordering is specified; it is, verbatim, in the same DESIGN.md section that also names per-seat fairness as an open item, and the immediately preceding review already ruled on the identical mechanism as a design choice. Severity should follow the legibility-pacing finder's own P2, not the merge's highest-kept P1. Two things I would keep at full strength: the drop-rate table (new, and directly useful as the control the cross-track rule already demands of any per-seat metric), and the finder's own honest limit -- the uncontested trigger gradient (p-1 172 vs p-9 33, and p-9 has the MOST crew living-ticks) is 5x larger than the contested one and has no established cause. That unexplained gradient, not the sort, is the real risk to the re-ground.

**Fix sketch.** [fix as filed by flow-edges] Break the actor-first tie with a per-tick deterministic permutation derived from the engine RNG (e.g. sort by (hash(rng_state, actor), actor)) so priority is unbiased across seats while staying replay-deterministic; or, better, remove the source of the asymmetry by draining the queue on the meeting transition (fix (a) of the previous finding), which leaves only the trigger race to randomise. Note that any change here re-writes every state_hash chain, so it belongs in the same re-record as the other substrate fixes.

[fix as filed by legibility-pacing] Break report/emergency ties on a seeded draw (or on the same RNG cursor the tick already advances) instead of the actor-id sort, and record the losers as voided actions (see the previous finding). Separately, root-cause the uncontested submission gradient before the re-ground -- if it is route determinism, it is a corpus-wide positional prior the fitted model will absorb.

## A-14 — Meeting trigger aborts the tick: ~2,160 recorded actions (36 kills, 99 reports, 17 emergency calls) are neither applied nor rejected, yet are recorded as submitted

**Severity:** P1. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** flow-edges / engine tick loop + replay recording; also legibility / record legibility. **Confidence:** high.
**Merged from:** flow-edges#1: Meeting trigger aborts the tick: the rest of the action queue is silently discarded but still recorded, legibility-pacing#2: The meeting interrupt silently voids every action queued behind the trigger -- 2,161 actions, 36 of them kills.

**Claim.** MERGE NOTE: merged from 2 finders (flow-edges, legibility-pacing) reporting the same defect at engine/tick.py:599-600. Both P1, both 'defect'; no disagreement. Totals differ only by counting frame -- flow-edges 2,166 of 35,350 recorded actions (all recorded actors), legibility-pacing 2,161 (living actors only) -- and both agree on the subtotals that matter (36 kills, 99 reports, 17 emergency calls, 112 vents). flow-edges uniquely supplies a deterministic engine-only reproducer (proof1.py), the per-set rates, and the prior-art correction that these were previously mis-filed as ActionRejected 'meeting-tick freezes' in audits/review-2026-08-19; legibility-pacing uniquely supplies the pacing consequence (29 of 384 inter-meeting gaps are 1 tick, and 16 of those 29 are the dropped reporter re-firing on the very next tick) and the classification of the 116 dropped report/emergency actions (73 duplicate-body, 26 distinct-discovery, 17 emergency).

[claim as filed by flow-edges] When any action in a tick's queue convenes a meeting, engine/tick.py returns immediately and every later action in the queue is neither applied nor rejected, yet orchestrator/replay.py records the full submitted queue -- 2,166 of 35,350 recorded actions (6.13%) in the committed baseline-7 bytes, including 36 kills, 99 reports and 17 emergency calls, never happened.

[claim as filed by legibility-pacing] On the 668 meeting-trigger ticks, every action submitted by an actor sorted after the triggering actor is dropped with no engine event and no ActionRejected, so 2,161 actions (incl. 36 kills, 112 vents, 99 reports, 17 emergency calls) sit in the committed bytes with no recorded consequence of any kind.

**Finder evidence.**

```
==============================================================================
EVIDENCE AS FILED BY FINDER: flow-edges
(its severity P1, classification defect, confidence high)
title: Meeting trigger aborts the tick: the rest of the action queue is silently discarded but still recorded
==============================================================================

CODE
engine/tick.py:593-604 (step 1, "Apply queued actions"):
    for action in actions:
        try:
            working_state, event = _apply_action(working_state, game_map, action)
            events.append(event)
            if event.type == "Killed":
                cooldown_skip_players.add(action.actor)
            if working_state.phase == "MEETING":
                return working_state, events          # <-- lines 599-600
        except ActionRejectedError as exc:
            events.append(_rejection_event(...))
The return is INSIDE the loop, so the remaining actions are never touched: no
_apply_action, no ActionRejectedError, no ActionRejectedEvent.

orchestrator/game.py:1850-1860 records the SUBMITTED list, not the applied one:
    actions = list(translate_action_intents_for_tick(intents))
    input_tick = state.tick
    state, events = advance_tick(state, actions, game_map=self._game_map, ...)
    ...
    if replay is not None:
        replay.record_tick(input_tick, actions, state)
orchestrator/replay.py:845-853:
    def record_tick(self, tick, actions, state):
        entry = {"kind": "tick", ..., "actions": _serialize_actions(actions), "state_hash": _state_hash(state)}
The tick's state_hash is correct (the dropped actions were not applied), so a
re-walk verifies byte-identically -- the corruption is invisible to
eval/replay_walk.py and visible only to a consumer that reads `actions` as
"what happened".

DETERMINISTIC PROOF (scratch script, engine only, no LLM)
$ PYTHONPATH=/Users/danielkeinan/projects/AiLibi uv run python .../proof1.py
    submitted order: [('p-1', 'report'), ('p-2', 'move'), ('p-3', 'move')]
    events: [('MeetingTriggered', 'p-1')]
    phase: MEETING tick: 0 (input tick was 0 )
    p-2 room after: CAFETERIA  p-3 room after: CAFETERIA
(p-2/p-3 asked to move to UPPER_HALL; both stayed put, and no ActionRejected
event names them.)

COMMITTED BYTES (all 300 games, re-walked through eval.replay_walk.walk_replay
with verify_tick_hashes=True; every action classified APPLIED / REJECTED /
DROPPED by whether the tick's event list names its actor)
$ PYTHONPATH=... uv run python .../scan3.py
    APPLIED  {'move': 12023, 'do_task': 13241, 'kill': 825, 'vent': 1067, 'emergency': 50, 'wait': 2977, 'report': 618, 'sabotage': 29, 'repair_sabotage': 83}
    REJECTED {'do_task': 1928, 'kill': 150, 'move': 106, 'wait': 42, 'repair_sabotage': 45}
    DROPPED  {'move': 787, 'do_task': 745, 'wait': 364, 'vent': 112, 'report': 99, 'repair_sabotage': 4, 'emergency': 17, 'kill': 36, 'sabotage': 2}
    {'ticks_with_multiple_trigger_actions': 106, 'meeting_tick_with_kill': 9}
2,166 dropped / 35,350 recorded = 6.13%. Cross-checked purely from the JSONL
without re-simulation (every action whose actor sorts after the meeting's
`triggered_by` at a meeting tick): identical total 2,166, distribution
0..7 dropped per meeting over 668 meetings.
Per set: samples/9p2i 541/7515 (7.20%), ml_corpus/9p2i 1502/23992 (6.26%),
samples/4p1i 65/1954 (3.33%), ml_corpus/4p1i 58/1889 (3.07%).

ANCHORED EXEMPLARS (set / seed / tick / actor / type / payload)
    samples/9p2i s12 t13  p-3 report {'body_id': 'body-p-9-12'}
    samples/9p2i s13 t8   p-7 report {'body_id': 'body-p-8-4'}
    samples/9p2i s17 t24  p-8 repair_sabotage {'kind': 'reactor'}   (reactor active)
    samples/9p2i s20 t11  p-9 emergency {'reason': 'suspicion_accumulation'}
    samples/9p2i s11 t9   p-3 vent {'vent_id': 'STORAGE_VENT'}
106 ticks carried TWO meeting-trigger actions (e.g. samples/9p2i s20 t11:
p-1 emergency + p-9 emergency); the second is dropped, and because it was never
applied the dropped caller's `emergency_uses` is not incremented -- the bytes
say the button was pressed, the engine says it was not.

PRIOR-ART NOTE: audits/review-2026-08-19/A/collated-findings.md section E
("Verified-clean") records these as "911/911 rejected `move` intents are
meeting-tick freezes" and "156 id-order escapes + 32 meeting-tick" kill
rejections. On baseline 7 they are NOT rejections: 787 moves and 36 kills carry
no event at all, against 106 and 150 genuine ActionRejected rows. That
mis-classification is why the mechanism was filed as explained rather than as a
recording defect.

==============================================================================
EVIDENCE AS FILED BY FINDER: legibility-pacing
(its severity P1, classification defect, confidence high)
title: The meeting interrupt silently voids every action queued behind the trigger -- 2,161 actions, 36 of them kills
==============================================================================

ALL findings fold the same reconstruction. Built once with (cwd = repo root):

  PYTHONPATH=. uv run python scratchpad/wave0/A/dump.py scratchpad/wave0/A/dump.json

dump.py re-seeds every committed seed and replays it through
`eval.replay_walk.walk_replay` under a profile with `verify_tick_hashes=True`
(so every reconstructed tick matched the recorded `state_hash`), recording per
tick: the recorded actions, the ENGINE events (`engine.events.event_to_dict`),
alive set, per-player rooms, bodies, sabotage state, task counts; plus every
meeting row verbatim (transcript turns, ballots, contradictions, llm_calls with
their full prompts) and the `game_over` row. Roles come from
`eval.validity.roles_by_seed` (re-seeding, same recipe). Reconstruction was
clean: 0 errors over 50 + 150 + 50 + 50 = 300 games (samples/9p2i 50,
ml_corpus/9p2i 150, samples/4p1i 50, ml_corpus/4p1i 50); rosters resolved to
(9,2,2) and (4,1,1).

Mechanism (engine/tick.py, advance_tick step 1, lines 593-604):

    for action in actions:
        try:
            working_state, event = _apply_action(working_state, game_map, action)
            events.append(event)
            ...
            if working_state.phase == "MEETING":
                return working_state, events        # <-- engine/tick.py:599-600
        except ActionRejectedError as exc:
            events.append(_rejection_event(...))

The early return happens BEFORE the remaining actions are visited, so they
produce neither an event nor a rejection.  The batch order is fixed by
orchestrator/action_ordering.py:33-40, `_action_order_key = (actor, type, payload)`
-- lexicographic by player id.

Fold over dump.json (per meeting-trigger tick: actions from LIVING actors that
produced no event of any kind):

    meeting-trigger ticks: 668
    silently DROPPED actions (no event, no rejection): 2161
      {'move': 787, 'do_task': 740, 'wait': 364, 'vent': 112, 'report': 99,
       'kill': 36, 'emergency': 17, 'repair_sabotage': 4, 'sabotage': 2}

Anchored example -- a distinct body discovery erased.
  samples/9p2i seed 3, tick 12:
    submitted: p-1 report body-p-4-8 ; p-5 report body-p-3-8
    triggered: p-1 report body-p-4-8   (only)
    bodies at t12: body-p-3-8 (p-3, ENGINEERING, disc=None),
                   body-p-4-8 (p-4, ADMIN, disc='p-1')
  p-5's discovery of p-3 leaves no trace at t12.

Classifying the 116 dropped report/emergency actions:
    dropped duplicate-body reports (harmless): 73
    dropped DIFFERENT-body reports (a distinct discovery lost): 26
    dropped emergency calls: 17
  (`_apply_emergency`, engine/tick.py:443-462, increments `emergency_uses`, so a
   dropped emergency is only free because it never reaches `_apply_action` --
   but it is also never recorded as having been attempted.)

Downstream pacing artifact: the dropped reporter usually re-fires on the very
next tick, producing back-to-back meetings with zero play between them.
    gap==1 meeting pairs: 29 of 384 inter-meeting gaps (7.6%)
    of which the FIRST meeting tick had a dropped report/emergency: 16 (55%)
    samples/9p2i seed 3   t12->t13 ; dropped at t12: ['p-5'] ; t13 triggered by p-5
    samples/9p2i seed 29  t8->t9   ; dropped at t8:  ['p-3'] ; t9  triggered by p-3
    ml_corpus/9p2i seed 1120 t11->t12 ; dropped at t11: ['p-8','p-9'] ; t12 by p-8
    (in every listed case the tick-b trigger actor IS the actor dropped at tick a)
```

**Verifier evidence (independent re-run).**

```
CMD 1 (independent JSONL-only fold, scratchpad/v2/a13.py):
  meetings 668  total recorded actions 35350  dropped 2166 = 6.13%
  dropped by type {'move': 787, 'do_task': 745, 'wait': 364, 'vent': 112, 'report': 99, 'repair_sabotage': 4, 'emergency': 17, 'kill': 36, 'sabotage': 2}
  per set: samples/9p2i 541/7515 = 7.20% | ml_corpus/9p2i 1502/23992 = 6.26% | samples/4p1i 65/1954 = 3.33% | ml_corpus/4p1i 58/1889 = 3.07%
  -> exact reproduction of flow-edges' totals AND its per-set rates; the 5-action delta against legibility-pacing's 2,161 is exactly the living-actor filter, as the merge states.

CMD 2 (pacing + report classification, scratchpad/v2/a14.py):
  total inter-meeting gaps 384  gap==1 29  of which prev tick had a dropped report/emergency 16
  dropped report/emergency classification: dup-body 73  diff-body 26  emergency 17  total 116
  anchors reproduced: samples/9p2i seed 3 t12->t13 dropped ['p-5'] then triggered by p-5; seed 29 t8->t9 dropped ['p-3'] then p-3; seed 12 t13->t14 ['p-3'] then p-3; seed 30, seed 46, ml_corpus 1026 same shape.
  -> every published cell reproduces exactly.

CMD 3 -- CODE, both halves:
  engine/tick.py:593-604: the `return working_state, events` on `if working_state.phase == "MEETING"` is INSIDE the `for action in actions:` loop, above the `except ActionRejectedError` handler -- remaining actions are never visited, so no _apply_action, no rejection, no event.
  orchestrator/game.py:1850-1860: `actions = list(translate_action_intents_for_tick(intents))` ... `state, events = advance_tick(...)` ... `replay.record_tick(input_tick, actions, state)` -- the SUBMITTED list.
  orchestrator/replay.py:845-853: record_tick writes {'kind':'tick','tick','actions':_serialize_actions(actions),'state_hash':_state_hash(state)} -- no disposition, no event stream. (`trace.record_tick` on the next line DOES receive `events`; the committed replay JSONL does not.)
  Confirmed by inspection of the committed bytes: every tick entry carries exactly the keys ['actions','game_id','kind','tick','state_hash'].
```

**Verifier note.** Fully confirmed: numbers, mechanism, and both code sites. Two things the parent should carry forward. (1) PRIOR ART -- the engine half is already on the books as C-25 / engine-F6 in the immediately preceding review (audits/review-2026-08-19/B/collated-findings.md:49 and B/engine.md:67: 'Actions after a meeting trigger in the same batch vanish without an ActionRejected ... DESIGN §3.1 promises a rejection event for every non-applied action', VERIFIED, P2, still open at HEAD), and the dropped-kill subtotal is prior art as G-18 ('11 kills on the exact trigger tick; 32 attempts annihilated at no cooldown cost', cross-track-map.md:100). A-14's own PRIOR-ART paragraph is therefore slightly wrong where it says the mis-classification in Track A's section E 'is why the mechanism was filed as explained rather than as a recording defect' -- Track B filed it correctly as a defect in the same review. (2) What is genuinely new, and what carries the P1, is the RECORDING half: replay.record_tick persists the submitted queue with no disposition and no event stream, so 2,166 actions in the committed ML corpus -- 36 kills, 26 distinct body discoveries, 17 emergency presses -- read to any byte consumer as things that happened. DESIGN.md:275 specifies that 'a meeting interrupts the tick loop' (so the early return is defensible), and DESIGN.md:267 promises an ActionRejected only for actions that are re-validated and found invalid; the recording layer's semantics are specified nowhere. P1 and 'defect' both stand.

**Fix sketch.** [fix as filed by flow-edges] Two independent halves. (a) Engine: on the MEETING transition, keep draining the queue and emit an explicit ActionRejectedEvent(reason='tick aborted by meeting') for each remaining action instead of `return`-ing out of the loop -- the world state stays identical, the event stream becomes complete. (b) Recording: have record_tick persist the applied/rejected/aborted disposition alongside the submitted action (or record the engine's event list), so a byte consumer can distinguish an intent from a transition. (b) alone unblocks the ML re-ground; (a) also fixes the agent-visible perception gap.

[fix as filed by legibility-pacing] Emit an explicit rejection/void event for every action not visited because of the meeting interrupt -- e.g. `ActionRejectedEvent(reason="meeting interrupted this tick")` appended for each remaining action before the early return. That is additive to the event stream only (the returned state is unchanged), so no state_hash chain moves, and it turns 2,161 phantom actions into recorded no-ops that a replay reader and a fitted model can both see.

## A-15 — ml_corpus README item 8 numbers do not reproduce on the committed bytes

**Severity:** P1 (stands; arguably P0 for the ML program given that a committed close audit asserts the opposite) (finder: P1). **Classification:** defect (unchanged) -- documentation/provenance integrity, not a gameplay or balance item; NOT a duplicate of the balance-wave G-22 roll-call lever, which is about the substrate asymmetry rather than about the README's numbers. **Verdict:** ADJUSTED. **Area:** impostor-behavior / ML corpus disclosure integrity. **Confidence:** high.
**Merged from:** impostor-behavior#2: ml_corpus README item 8 numbers do not reproduce on the committed bytes.

**Claim.** CONFIRMED AND WIDENED. The claim as filed is scoped to item 8; the defect is the entire 'Capability disclosures' section of replays/ml_corpus/README.md. Commit efcd43b8 (task 20.36, the baseline-7 adopting record) re-recorded all four sets and changed exactly ONE word in that section -- ':111 "recorded at the same baseline-6 substrate" -> "baseline-7 substrate"' -- leaving every number in the section computed on the baseline-6 bytes. Proof: every item-8 figure reproduces EXACTLY against the bytes at 2df33ca4 (S9 crew 723/726, impostor 120/245; C9 2035/2042, 342/684; S4 78/78, 8/39; C4 79/80, 5/40; impostor reply turns 124; impostor opt_in 121; crew reply 80) and none reproduce on HEAD. The staleness is not confined to item 8: item 1's '707/707 meetings are crew-triggered' is 668 on HEAD, and item 2's '986 recorded kill actions' is 1,011 submitted. Two aggravations the finding does not name: (a) audits/audit-phase-20-baseline-7.md:577-579 affirmatively states 'the corpus README [was] all re-derived from these bytes', which is false for this section; (b) tests/eval/test_deduction_metrics.py:496-537 asserts the NEW baseline-7 values (652/652, 104/219, 283/625, 80/80, 5/40, 88/88, 1/44) while its docstrings claim they match 'replays/ml_corpus/README.md item 8 ... byte for byte' and quote the STALE 4p pair 'crew 78/78 and 79/80 vs impostor 8/39 and 5/40' -- a green test that certifies agreement with a document it contradicts. One correction to the finding: 'Only S4's impostor cell (5/40) matches' mis-maps the README's 4p pair; README's (S4, C4) impostor cells are (8/39, 5/40), so S4's README figure is 8/39 and nothing actually matches -- HEAD's S4 5/40 merely coincides with the README's C4 cell.

**As originally filed.** replays/ml_corpus/README.md item 8 ('Role-correlated public response shape') asserts figures recomputed from these committed baseline-7 bytes, but three of its four coverage denominators and its entire whereabouts-lie sub-claim fail to reproduce — most seriously it reports impostor roll-call answers matching the true room only 48.3% (S9) / 45.3% (C9) of the time, where the committed bytes give 98.1% / 99.3% under the rendered-route frame and 95.2% / 98.9% under the pre-advance decision frame the README itself names.

**Finder evidence.**

```
This is NOT a known-open item; it is a disagreement between two committed artifacts.

WHAT THE README CLAIMS (replays/ml_corpus/README.md:104-126 scope line, then item 8 at :255-277):
  :107 'Every number below was recomputed from the committed bytes'
  :112-115 'S9 (replays/samples/9p2i, 50 games) ... C9 (replays/ml_corpus/9p2i, 150 games)'
  :256 'crew 723/726 = 99.6% (S9) and 2,035/2,042 = 99.7% (C9) versus impostor 120/245 = 49.0% (S9) and 342/684 = 50.0% (C9) (4p sets: crew 78/78 and 79/80 vs impostor 8/39 and 5/40)'
  :270 'impostor self-placements match the reconstructed room in 58/120 = 48.3% (S9) and 155/342 = 45.3% (C9) ... versus crew 575/723 = 79.5% and 1,619/2,035 = 79.6%'

MEASUREMENT 1 - the shipped instrument in the committed reports themselves:
  COMMAND: uv run python -c "import json;\nfor p in ['replays/samples/9p2i','replays/ml_corpus/9p2i','replays/samples/4p1i','replays/ml_corpus/4p1i']:\n d=json.load(open(p+'/tournament-eval-report.json'));print(p,d['deduction']['public_response_coverage'])"
  OUTPUT:
    replays/samples/9p2i    crew_turns 652, crew_turns_with_whereabouts 652, crew_pooled_coverage 1.0, impostor_turns 219, impostor_turns_with_whereabouts 104, impostor_pooled_coverage 0.47489
    replays/ml_corpus/9p2i  crew_turns 1854, ...whereabouts 1854, coverage 1.0, impostor_turns 625, ...whereabouts 283, coverage 0.4528
    replays/samples/4p1i    crew 80/80 = 1.0, impostor 5/40 = 0.125
    replays/ml_corpus/4p1i  crew 88/88 = 1.0, impostor 1/44 = 0.02273

MEASUREMENT 2 - an independent bare-stdlib recount over the JSONL (no repo imports):
  COMMAND: python3 - <<'PY' ... (walks replay-seed-*.jsonl, joins roles from each set's tournament-eval-report.json, counts turns carrying a structured whereabouts observation) ... PY
  OUTPUT:
    S9 replays/samples/9p2i:   meetings=152 crew 652/652=1.0000  imp 104/219=0.4749
    C9 replays/ml_corpus/9p2i: meetings=432 crew 1854/1854=1.0000 imp 283/625=0.4528
    S4 replays/samples/4p1i:   meetings=40  crew 80/80=1.0000     imp 5/40=0.1250
    C4 replays/ml_corpus/4p1i: meetings=44  crew 88/88=1.0000     imp 1/44=0.0227
  Both measurements agree with each other and with the shipped report, and disagree with the README on the S9/C9/C4 denominators (652 vs 726, 1854 vs 2042, 219 vs 245, 625 vs 684, 44 vs 40) and on crew coverage (100.0% vs 99.6%/99.7%). Only S4's impostor cell (5/40) matches.

MEASUREMENT 3 - the whereabouts-lie sub-claim, evaluated in BOTH frames. Ground truth taken two independent ways: (i) the engine's own rendered route line in each agent's memory ('Your route (t = tick): CAFETERIA t0 -> EAST_HALL t1 -> ...' inside meeting llm_calls[].prompt), and (ii) a from-scratch replay of the tick actions (start CAFETERIA, apply move/vent, record position BEFORE each tick's actions = the 'pre-advance decision frame' the README names).
  OUTPUT (n = whereabouts observations):
    samples/9p2i    CREWMATE n=659  route-frame 656 (0.995)  decision-frame 654 (0.992)
                    IMPOSTOR n=104  route-frame 102 (0.981)  decision-frame  99 (0.952)
    ml_corpus/9p2i  CREWMATE n=1892 route-frame 1875 (0.991) decision-frame 1860 (0.983)
                    IMPOSTOR n=285  route-frame 283 (0.993)  decision-frame 282 (0.989)
    samples/4p1i    CREWMATE 79/80  IMPOSTOR 5/5
    ml_corpus/4p1i  CREWMATE 91/91  IMPOSTOR 1/1
  Neither frame is anywhere near the README's 48.3% / 45.3% / 79.5% / 79.6%. On the committed bytes the roll-call channel is ~99% truthful for BOTH roles: impostors essentially do not lie in the one structured channel the alibi rules prosecute.

WHY IT MATTERS HERE: item 8 is the section the ML program reads to learn what the impostor tell is. As written it tells a fitter that 'impostors lie in whereabouts about half the time' (a rich, learnable deception signal) when the bytes say they almost never do; and it understates the real tell (the absent-observation label, finding 1) by quoting a 49%/50% coverage that is actually 47.5%/45.3% against a crew baseline that is exactly 100.0%, not 99.6%.
```

**Verifier evidence (independent re-run).**

```
MEASUREMENT 1 -- shipped instrument (HEAD):
  samples/9p2i  crew 652/652 pooled 1.0 | impostor 104/219 pooled 0.47489
  ml_corpus/9p2i crew 1854/1854 pooled 1.0 | impostor 283/625 pooled 0.4528
  samples/4p1i   crew 80/80 | impostor 5/40 = 0.125
  ml_corpus/4p1i crew 88/88 | impostor 1/44 = 0.02273

MEASUREMENT 2 -- my own bare-stdlib recount over the JSONL meeting entries (scratchpad/v2/a15.py), joining roles from each set's report:
  samples/9p2i:   meetings=152 crew 652/652=1.0000  imp 104/219=0.4749
  ml_corpus/9p2i: meetings=432 crew 1854/1854=1.0000 imp 283/625=0.4528
  samples/4p1i:   meetings=40  crew 80/80=1.0000     imp 5/40=0.1250
  ml_corpus/4p1i: meetings=44  crew 88/88=1.0000     imp 1/44=0.0227
  -> agrees with the shipped metric and with the finding; disagrees with the README.

MEASUREMENT 3 -- THE ROOT CAUSE (scratchpad/v2/a15old.py, same recount replayed against `git show 2df33ca4:`):
  samples/9p2i @2df33ca4:   meetings=165 crew 723/726  imp 120/245   kinds incl. ('IMPOSTOR','reply'):124, ('IMPOSTOR','opt_in'):121, ('CREWMATE','reply'):80
  ml_corpus/9p2i @2df33ca4: meetings=463 crew 2035/2042 imp 342/684
  samples/4p1i @2df33ca4:   meetings=39  crew 78/78     imp 8/39
  ml_corpus/4p1i @2df33ca4: meetings=40  crew 79/80     imp 5/40
  -> every README item-8 numerator/denominator, including the two sub-claims (0/124 impostor replies, 120/121 impostor opt-ins), reproduces exactly on the baseline-6 bytes.
  $ git diff 2df33ca4 efcd43b8 -- replays/ml_corpus/README.md  ->  the disclosures section's ONLY change is
      -`replays/samples/` twins recorded at the same baseline-6 substrate — **S9**
      +`replays/samples/` twins recorded at the same baseline-7 substrate — **S9**

MEASUREMENT 4 -- the whereabouts-lie sub-claim, my own reconstruction from the ENGINE's rendered route line in each meeting prompt (scratchpad/v2/a15route2.py; the 'a vent in ROOM' segment must be normalised to ROOM, otherwise impostors read 92.3%):
  samples/9p2i   CREWMATE n=659  match 656 (0.995) | IMPOSTOR n=104 match 102 (0.981)
  ml_corpus/9p2i CREWMATE n=1892 match 1875 (0.991)| IMPOSTOR n=285 match 283 (0.993)
  samples/4p1i   CREWMATE 79/80  | IMPOSTOR 5/5
  ml_corpus/4p1i CREWMATE 91/91  | IMPOSTOR 1/1
  POOLED: CREWMATE 2701/2722 = 0.9923 ; IMPOSTOR 391/395 = 0.9899
  -> exact reproduction of the finding's Measurement 3, against the README's 48.3% / 45.3% / 79.5% / 79.6%.

WIDER STALENESS (HEAD, scratchpad fold): meetings = 668 (README item 1 says 707/707); kill actions submitted = 1,011 (README item 2 says 986 recorded, 798 resolved).

CONTRADICTED AUDIT CLAIM: audits/audit-phase-20-baseline-7.md:577-579 -- 'The ladder tip stands at baseline 7, with .env.example's graduated-levers note, README's provenance paragraph, the recorder pin blocks and the corpus README all re-derived from these bytes.'
CONTRADICTED TEST DOCSTRINGS: tests/eval/test_deduction_metrics.py:493 ('matching Task 19.8's disclosure (replays/ml_corpus/README.md item 8) byte for byte') and :529 ('The 4p disclosure twins (crew 78/78 and 79/80 vs impostor 8/39 and 5/40)') -- both docstrings quote baseline-6 while the asserts pin baseline-7, with in-line `# was (342, 684)` markers showing the pins WERE re-derived at the record and the README was not.
```

**Verifier note.** Confirmed on all three of the finding's measurements, reproduced independently, and materially strengthened. The finding treats this as 'a disagreement between two committed artifacts' of unknown origin and offers 'if the figures were produced by a since-changed reconstruction, say so' as a conditional; the origin is now established beyond doubt -- a one-word substrate relabel at the baseline-7 record with the numbers left untouched -- which converts the fix from 'recompute item 8' into 'recompute or retire the whole Capability-disclosures section, and repair the two artifacts that certify it as current'. This is not a re-report of any listed known-open item: G-22 is the balance-wave roll-call LEVER (the substrate asymmetry itself), not the README's arithmetic, and nothing in audits/audit-phase-20-close.md or audit-phase-20-baseline-7.md §10 declares this section stale -- §10.2 declares exactly this problem for the samples/9p2i MANIFEST's hand-maintained disclosure block ('Its baseline-6 figures are invalid on these bytes and it must be re-measured, not restored') and misses the same problem in the corpus README two directories away.

**Fix sketch.** Recompute item 8 from the committed baseline-7 bytes and republish it (numerators, denominators, and the whereabouts-match cell), stating the frame used for the match cell explicitly and pinning it with a test that re-derives the numbers from replays/ so the section cannot drift again. If the ~48%/79.5% figures were produced by a since-changed reconstruction, say so and retire them rather than carrying them forward; any ML feature or paper claim resting on 'impostors lie in roll call' must be re-derived first.

## A-16 — Player-visible impostor kill confessions occur, are ignored, and are unmeasured

**Severity:** P2 (finder: P1). **Classification:** defect (instrument-coverage gap only; the gameplay half is a balance/design proposal, not a defect). **Verdict:** ADJUSTED. **Area:** impostor-behavior / self-incrimination / instrument coverage. **Confidence:** high.
**Merged from:** impostor-behavior#4: Player-visible impostor kill confessions occur, are ignored, and are unmeasured.

**Claim.** The INSTRUMENT half stands as filed and is code-verified: `player_visible_leak_turns` increments only on PARTNER_PHRASES over `turn.free_text` (eval/deduction_metrics.py:2350-2351), so the self-kill and role nets never run over the player-visible surface and the two first-person kill confessions in the committed bytes are counted nowhere. What must change is the GAMEPLAY inference. (a) 'no crew agent reacts' is right about citation but wrong about consequence: in BOTH cases the confessor was ejected in the very meeting he confessed in (p-7 in headless-seed-1079:meeting-2, p-8 in headless-seed-1128:meeting-0), each carrying an independent vent_sighting flag, so the corpus does NOT show that 'confessing carries zero consequence' and does not teach an optimizer that confession is free. (b) In Case 1 the next speaker p-8 does assert 'you're the one who killed him' one turn later, so 'no crew agent reacts' should be narrowed to 'no crew agent CITES the confession, and no ballot rationale mentions it'. (c) The proposed fix (1) — publish the self-kill net over player-visible text — would publish a metric that is majority false positive on the committed bytes: the net fires 10 times player-visible (4 IMPOSTOR, 6 CREWMATE) and only 2 are genuine, i.e. 20% precision overall / 50% within impostor speakers. That is the exact failure mode eval/deduction_metrics.py:263-268 already documents as its reason for excluding first-person VENT mentions from the self-kill net, so the fix must carry a disambiguation step (e.g. cross-check against the ground-truth kill record) rather than shipping a raw substring count.

**As originally filed.** Impostors do self-incriminate in player-visible text — two first-person murder confessions sit in the committed bytes — but no crew agent reacts to either, and no shipped instrument counts them, because `player_visible_leak_turns` runs only the partner-naming net over free_text and the self-kill / role nets are ballot-side only.

**Finder evidence.**

```
CASE 1 - ml_corpus/9p2i, headless-seed-1079:meeting-2, speaker p-7 (IMPOSTOR), turn 2 (opt_in):
  free_text: '1. I was in Storage at tick 17, far from the Cafeteria kill, clearing me. 2. p-8 moved into Engineering at tick 13, immediately after I killed p-1 at tick 12, yet p-8 never reported the body or saw the kill, which is highly suspicious.'
  claims[0].reason: 'p-8 was in Engineering at tick 13, same room where I killed p-1 at tick 12, ...'
  GROUND TRUTH from the tick records of the same file: tick 11 p-7 IMPOSTOR kill {'target': 'p-1'}; tick 12 p-7 vent ENGINEERING_VENT. roles: p-3 and p-7 IMPOSTOR.
  VISIBILITY: the confession is inside the free_text, which IS what vote_ballot.j2 renders. Dump of p-9's vote prompt <transcript> for that meeting contains verbatim:
    - [headless-seed-1079:meeting-2:turn-2] turn 2 (opt_in) - p-7 accuses p-8 (0.75): ... immediately after I killed p-1 at tick 12 ...
  REACTION: none. All four crew ballots cite the vent instead:
    p-2 -> p-7: 'p-8 caught p-7 venting in Engineering at tick 14; venting is impossible for crew, so p-7 is the impostor.'
    p-5 -> p-7: "...p-8's claim that p-7 vented is... well, if true, it's pretty damning, isn't it?"
    p-8 -> p-7: 'I literally saw p-7 vent in Engineering at tick 14...'
    p-9 -> p-7: "p-8 caught p-7 venting... let's eject the ventrater"
  Not one ballot rationale, and no later turn, mentions the confession.

CASE 2 - ml_corpus/9p2i, headless-seed-1128:meeting-0, speaker p-8 (IMPOSTOR), turn 6 (opt_in):
  claims[0].reason: 'Lying about vent to frame me; I was in Admin with p-4 until I killed him, p-5 arrived after'
  GROUND TRUTH same file: tick 6 p-8 IMPOSTOR kill {'target': 'p-4'} (ADMIN), tick 7 p-8 vent ADMIN_VENT. roles: p-8, p-9 IMPOSTOR.
  VISIBILITY: this one lands in a field the ballot render drops (finding 3) and it is the LAST turn of the meeting, so no later speaker sees it either -- a confession that reaches nobody.

INSTRUMENT GAP (file:line):
  eval/deduction_metrics.py:259 and :1564 -- 'player_visible_leak_turns is the partner net over player-visible free_text'
  eval/deduction_metrics.py:474-478 PARTNER_PHRASES = ('my partner','my teammate','my fellow impostor')
  eval/deduction_metrics.py:494-504 SELF_KILL_PHRASES and :486-491 ROLE_STATEMENT_PHRASES are documented at :1554-1560 as 'over impostor-voter ballots' only.
  Committed reading, replays/samples/9p2i/tournament-eval-report.json: scaffold_leakage.player_visible_leak_turns = 0 while model_self_kill_disclosure_ballots = 11 and model_omniscient_ballots = 41. The 0 is true of the partner net and is read as 'no player-visible leaks'.

MY SCAN (pooled 3,602 turns, free_text + claim.reason + claim.evidence):
  IMPOSTOR selfkill-net hits 4, of which 2 are genuine first-person confessions (the two above) and 2 are quotations of an accusation ('How do you know I killed p-4 ...').
  CREWMATE selfkill-net hits 6 - all counterfactual/quotation ('If I killed p-2, I would have been in Cafeteria'), the false-positive control behaving as expected.
  IMPOSTOR partner-net hits 0 on player-visible text (consistent with the shipped 0).
```

**Verifier evidence (independent re-run).**

```
CMD 1 (both confessions, verbatim, from the committed jsonl):
  python3 read replays/ml_corpus/9p2i/replay-seed-1079.jsonl @ headless-seed-1079:meeting-2 turn 2
  -> speaker p-7 (opt_in) free_text: '1. I was in Storage at tick 17, far from the Cafeteria kill, clearing me. 2. p-8 moved into Engineering at tick 13, immediately after I killed p-1 at tick 12, ...'
     claims[0].reason: '... same room where I killed p-1 at tick 12, ...'
  python3 read replays/ml_corpus/9p2i/replay-seed-1128.jsonl @ headless-seed-1128:meeting-0 turn 6
  -> speaker p-8 (opt_in) claims[0].reason: 'Lying about vent to frame me; I was in Admin with p-4 until I killed him, p-5 arrived after'  (turn 6 of 7 turns = the last turn)

CMD 2 (ground truth from the same files' tick rows):
  seed 1079: tick 11 p-7 kill {'target':'p-1'}; tick 12 p-7 vent ENGINEERING_VENT; tick 13 p-7 vent STORAGE_VENT. roles p-3,p-7 IMPOSTOR.
  seed 1128: tick 6 p-8 kill {'target':'p-4'}; tick 7 p-8 vent ADMIN_VENT; tick 8 p-8 vent MEDBAY_VENT. roles p-8,p-9 IMPOSTOR.
  -> matches the finding exactly (the agents' '+1' tick stamps are the known G-37 clock).

CMD 3 (visibility, seed 1079 meeting-2 llm_calls):
  prompts containing 'immediately after I killed p-1' = 7 of 10 (TURN p-8, TURN p-9, VOTE p-2, VOTE p-5, VOTE p-7, VOTE p-8, VOTE p-9)
  prompts containing the claim REASON string = 2 (the two later accusation-round turns only; no vote prompt)
  -> confirms the free_text confession reaches every later speaker AND every ballot; the reason string is dropped at ballot time.

CMD 4 (reaction): the 5 ballots of that meeting: p-2->p-7 'p-8 caught p-7 venting...'; p-5->p-7 "p-8's claim that p-7 vented..."; p-7->SKIP; p-8->p-7 'I literally saw p-7 vent...'; p-9->p-7 'p-8 caught p-7 venting...'. None cites the confession. EJECTED = p-7. In seed 1128 meeting-0 all six crew ballots cite the vent; EJECTED = p-8. BOTH confessors were ejected.

CMD 5 (instrument, source of truth):
  eval/deduction_metrics.py:2350-2351 ->  `if _matches(turn.free_text, PARTNER_PHRASES): acc.player_visible_leak += 1`  (the ONLY increment; SELF_KILL_PHRASES / ROLE_STATEMENT_PHRASES never touch turn text)
  eval/deduction_metrics.py:1564 and :259 document the scope honestly ('the partner net over player-visible free_text').
  replays/samples/9p2i/tournament-eval-report.json deduction.scaffold_leakage: player_visible_leak_turns 0, model_self_kill_disclosure_ballots 11, model_omniscient_ballots 41 -- all as filed.

CMD 6 (my own net scan over all 4 sets, free_text + claim.reason + claim.evidence, 3,602 turns):
  IMPOSTOR selfkill hits 4 (3 free_text + 1 claim) -> 2 genuine confessions (the two above) + 2 quotations of an accusation ('How do you know I killed p-4 just because I was in the hall?', 'How do you know I killed him just because I was in Engineering?')
  CREWMATE selfkill hits 6 -> all rhetorical/counterfactual ('If I killed p-2, I would have been in Cafeteria', 'How do you know I'm the killer...')
  IMPOSTOR partner-net hits on player-visible text: 0 (consistent with the shipped 0)
  -> reproduces the finding's scan exactly, and quantifies the proposed net's precision at 2/10.
```

**Verifier note.** Evidence reproduces in full, including my independent phrase-net scan. Not a re-report of any named known-open item: G-28 is the BALLOT-side role confession (already instrumented and counted), G-32 is the found_body variant. The turn-side coverage gap is genuinely new. Downgraded P1 -> P2 because the base rate is 2 genuine confessions in 3,602 turns (0.056%), the metric's scope is honestly documented in-module, both confessors were ejected anyway, and the fix as sketched ships a 20%-precision number.

**Fix sketch.** Two separable fixes. (1) Instrument: run the self-kill and role nets over the player-visible surface too - free_text AND claim.reason/claim.evidence, since accusation_round.j2:148 renders reason to the table - and publish them beside player_visible_leak_turns, so a confession is never reported as zero. (2) Gameplay: an outright first-person kill/role admission spoken at the table should either be blocked at validation (same chokepoint as the teammate firewall) or be promoted to a contradiction flag, because a corpus in which confessing carries zero consequence teaches an optimizer that confession is free.

## A-17 — Ballot-time render erases all structured testimony, including the impostor tell

**Severity:** P1 (render half); the roll-call-tell half is a re-report of the routed G-22 (finder: P1). **Classification:** defect (unchanged) -- DESIGN.md:595 specifies the voting prompt presents 'the rendered memory, full transcript, contradiction flags, and the agent's current suspicion graph'; nothing in DESIGN.md, docs/ or the phase contracts sanctions a free_text-only projection, and tasks/phase-10.md:190 / phase-11.md:191 freeze the vote render without ever describing it as free-text-only. **Verdict:** ADJUSTED. **Area:** impostor-behavior / vote surface. **Confidence:** high.
**Merged from:** impostor-behavior#3: Ballot-time render erases all structured testimony, including the impostor tell.

**Claim.** The core defect is CONFIRMED and if anything understated: vote_ballot.j2 contains exactly one reference to any turn field (line 113) and renders speaker + optional 'accuses X (conf)' + free_text, while accusation_round.j2:128-155 renders the full observation block, alibi/corroboration/accusation-reason claims and 'said:'; and the pre-vote memory carries claim lines from PRIOR meetings only (0 of 3,350 vote prompts). Two numbers in the filing must be corrected. (1) 'turns carrying at least one of these: 3,067/3,602 = 85.1%' is mislabelled: 3,067 is turns carrying at least one OBSERVATION; turns carrying at least one field the ballot render drops (observations OR alibi OR corroboration OR accusation reason) is 3,593/3,602 = 99.75%. The correction strengthens the claim. (2) 'of 1,391 crew ballots targeting a zero-observation replier' and 'crew repliers 8/159' mis-name the crew arm: there are ZERO crewmate turns with an empty observations array anywhere in the four sets (0 of 2,674), so no crew 'zero-observation replier' exists; the 159 is crew REPLY turns. The tell is therefore sharper than G-22 recorded: P(IMPOSTOR | turn has zero observations) = 535/535 = 1.000 over 3,602 turns, not 97.7-100%. Finally, the second half of the title and claim -- that the impostor's missing roll-call answer is invisible and unexploited -- is the open balance-wave item G-22 (a symmetric roll-call, Phase-20 close audit s4), so only the ballot-render half is a new finding.

**As originally filed.** The vote-ballot prompt renders each turn as speaker + optional 'accuses X (conf)' + free_text only — dropping every observation, alibi, corroboration and accusation reason — and the vote-time memory carries claim lines only from PRIOR meetings (0/3,350 vote prompts in the 9p2i sets contain a current-meeting claim line), so at the moment the crew actually decides, the impostor's missing roll-call answer is structurally invisible and cannot be exploited.

**Finder evidence.**

```
TEMPLATE DIFF (file:line):
  agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:113
    - [{{ turn.turn_id }}] turn {{ turn.turn_index }} ({{ turn.turn_kind }}) - {{ turn.speaker }}{% for claim in turn.claims %}{% if claim.type == "accusation" %} accuses {{ claim.against }} ({{ "%.2f" | format(claim.confidence) }}){% endif %}{% endfor %}: {{ turn.free_text }}
  agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:135-155 renders, for the SAME turns, a 'saw:' block (whereabouts/saw_vent/saw_player/...) plus 'claims:' with alibi rooms/ticks, corroborations and the accusation REASON, then 'said: "..."'.

SIDE-BY-SIDE ON ONE MEETING (replays/ml_corpus/9p2i/replay-seed-1128.jsonl, headless-seed-1128:meeting-0):
  accusation-round render of turn 6 (p-8, IMPOSTOR) carries the claim reason; the vote render of the same turn is:
    - [headless-seed-1128:meeting-0:turn-6] turn 6 (opt_in) - p-8 accuses p-5 (0.90): p-5 is lying through their teeth! I didn't vent, I was in Admin with p-4. ...
  -- the reason string ('Lying about vent to frame me; I was in Admin with p-4 until I killed him, p-5 arrived after') is gone.

MEMORY AT VOTE TIME carries only prior meetings. Dump of p-9's vote prompt <memory> for headless-seed-1079:meeting-2 (the 3rd meeting) shows:
  ## Meetings so far:
  - Meeting 1 (tick 10): p-3 EJECTED 5-2 - p-3 was an IMPOSTOR. 1 impostor remains.
  - Meeting 2 (tick 14): no ejection (3 skip). 1 impostor remains.
  - [tick 14] [meeting 2] CLAIM by p-2 (unverified): ...   <- meeting 2 only, never meeting 3
  COMMAND: walk every llm_call whose prompt contains 'rationale_text' (the vote calls) in samples/9p2i + ml_corpus/9p2i and regex the <memory> block for a claim line tagged with the CURRENT meeting index.
  OUTPUT: {'vote_prompts': 3350, 'mem_has_any_claims': 1912}   -- 'mem_has_current_meeting_claims' never incremented (0/3350).

SCALE OF WHAT IS DROPPED (pooled over all four sets, 3,602 turns):
  observations 10,320 (of which 3,117 roll-call whereabouts, 517 saw_vent, 833 found_body)
  alibi claims 1,001 | corroboration claims 1,416 | accusation reasons 3,107
  turns carrying at least one of these: 3,067/3,602 = 85.1%
  (Engine-certified contradiction flags and the voter's OWN memory DO survive into the vote prompt, so hard proof still reaches the ballot; spoken testimony from this meeting does not.)

CONSEQUENCE FOR THIS DIMENSION - the crew do not exploit the tell, and cannot. Lexical scan of 2,674 crew turns for language about a missing account found no instance referring to a speaker's failure to answer roll call; of 1,391 crew ballots targeting a zero-observation replier only 15 (1.1%) matched a 'no account' net and inspection shows all 15 are about physical sighting gaps ('p-5 was standing over the body with no alibi'), not about the meeting-turn omission. The suggestive ejection gap that does exist in unflagged meetings (impostor repliers 56/201 = 27.9% vs crew repliers 8/159 = 5.0%) is therefore not evidence of the crew reading the omission.
```

**Verifier evidence (independent re-run).**

```
CMD 1 (template diff, source of truth):
  grep -n 'turn\.|observations|claim\.' agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2
  -> ONE hit, line 113: `- [{{ turn.turn_id }}] turn {{ turn.turn_index }} ({{ turn.turn_kind }}) - {{ turn.speaker }}{% for claim in turn.claims %}{% if claim.type == "accusation" %} accuses {{ claim.against }} ({{ "%.2f" | format(claim.confidence) }}){% endif %}{% endfor %}: {{ turn.free_text }}`
  sed -n '128,155p' agents/strategic/prompts/qwen3_6_27b/accusation_round.j2 -> renders saw_player/saw_move/completed_task/found_body/saw_vent/whereabouts lines, then 'claims:' with alibi rooms+ticks, accusation REASON, corroboration REASON, then 'said: "..."'. Confirmed.

CMD 2 (memory at vote time, my own walk over the committed llm_calls in both 9p2i sets):
  regex <memory>...</memory> in every prompt containing 'rationale_text', count '[meeting N] CLAIM' lines whose N equals the CURRENT meeting index (1-based header numbering, verified against a sample: meeting-1's prompt carries '[meeting 1] CLAIM' = the PRIOR meeting)
  -> {'vote_prompts': 3350, 'mem_has_any_claims': 1912, 'mem_has_current_meeting_claims': 0}
  Exact match to the filing (3350 / 1912 / 0).

CMD 3 (scale of what is dropped, all four sets, from tournament-eval-report.json transcripts):
  turns 3602 | observations 10320 (whereabouts 3117, saw_player 3775, saw_move 1657, found_body 833, saw_vent 517, completed_task 421) | alibi 1001 | corroboration 1416 | accusation reasons 3107
  ALL component counts match the filing EXACTLY.
  turns with >=1 observation = 3067 (= the filing's '3,067'); turns with >=1 dropped field of ANY kind = 3593/3602 = 99.75% (the filing's 85.1% label is wrong).

CMD 4 (the crew arm):
  zero-observation turns by role over all four sets: {('CREWMATE','hasobs'): 2674, ('IMPOSTOR','zeroobs'): 535, ('IMPOSTOR','hasobs'): 393}  -> CREWMATE zeroobs = 0.
  In fully-unflagged meetings: IMPOSTOR reply turns 201, ejected 56 = 27.9%; CREWMATE reply turns 159, ejected 8 = 5.0% -> the filing's gap reproduces exactly once the arm is read as 'reply turns', not 'zero-observation repliers'.

CMD 5 (spec check): grep -n 'transcript' DESIGN.md -> :595 'The voting prompt presents ... the rendered memory, full transcript, contradiction flags, and the agent's current suspicion graph'. git log on vote_ballot.j2 shows four content commits (13.x/16.13/16.15/16.16/20.31); none introduces or defends a free_text-only turn render.
```

**Verifier note.** The render defect is real, code-verified and not on the named known-open list (G-35 is memory-side claim stubs and its 'meeting outcomes never recorded' half is already fixed -- the committed memory blocks now carry 'Meeting 1 (tick 11): p-6 EJECTED 6-1'; G-21 is belief carry-over). Two numeric labels corrected (one strengthens, one renames the arm). The 'impostor tell cannot be exploited' half duplicates the routed balance-wave item G-22. The lexical 'no account' net (15/1,391) is definition-dependent and I did not reproduce it; it does not carry the claim.

**Fix sketch.** Render the same structured turn body in vote_ballot.j2 that accusation_round.j2 already renders (observations + alibi/corroboration + accusation reason), or ingest the current meeting's testimony into the pre-vote memory the way prior meetings' claims are ingested. Either restores testimony-as-content at the only point that changes the outcome. Guard it with a template test asserting that the two renders expose the same set of turn fields, so the vote surface cannot silently regress to free_text-only.

## A-18 — The impostor's fake task is a perfect impostor label in the reconstructed event stream

**Severity:** P2 (an ML feature-hygiene hazard, already fenced in the one existing consumer), not P1 (finder: P1). **Classification:** intended-mechanic with a residual ML-corpus-hygiene hazard -- NOT a defect. **Verdict:** ADJUSTED. **Area:** legibility / ML corpus hygiene. **Confidence:** high.
**Merged from:** legibility-pacing#4: The impostor's fake task is a perfect impostor label in the reconstructed event stream.

**Claim.** The rejection census is CONFIRMED exactly by my own independent replay walk (358 / 1055 / 116 / 112 no_task_instance rejections; 500 of 500 impostor slots flagged; 0 of 1,700 crewmate slots; 0 reconstruction errors under verify_tick_hashes=True over all 300 games). Three parts of the filing must change. (1) THE SECOND SEPARATOR IS REFUTED. 'the fake task id is never one any crewmate works in that same game (0 of 1,671)' is the opposite of what the bytes say: 1,431 of the 1,671 impostor do_task submissions (85.6%) use a map task id that a crewmate in the SAME game also submits; by unique (game, task_id) pairs the overlap is 126/132 (95.5%) samples/9p2i, 353/367 (96.2%) ml_corpus/9p2i, 16/59 (27.1%) samples/4p1i, 14/56 (25.0%) ml_corpus/4p1i, with 236 same-TICK id collisions in samples/9p2i alone (e.g. seed 1079 tick 0: crewmate p-4 and impostor p-7 both submit `empty_trash`). The fix bullet 'vary the fake task id so it overlaps tasks real crewmates hold in that game' is therefore already satisfied in the 9p2i sets. (2) 'crewmate slots' is 1,700, not 2,200 (2,200 is TOTAL slots: 50x9 + 150x9 + 50x4 + 50x4). Precision/recall 1.000 is unaffected. (3) 'median first fire at tick 2' -- the pooled median is 1.0 (9p2i median 1.0, 4p1i median 2.0, 400 vs 100 slots); mean 1.20 and min 0 are correct. Finally the classification: the mechanic is SPECIFIED, and the marginal leak is near-zero because the reconstructed engine stream is omniscient by construction -- 492 of 500 impostor slots (98.4%) are already labelled by a recorded kill or vent ACTION in the same committed bytes.

**As originally filed.** Replaying the committed bytes yields an `ActionRejected(do_task, "actor owns no task instance ...")` for 500 of 500 impostor slots and 0 of 2,200 crewmate slots -- precision 1.000, recall 1.000, median first fire at tick 2 -- and the fake task id is never one any crewmate works in that same game (0 of 1,671).

**Finder evidence.**

```
ALL findings fold the same reconstruction. Built once with (cwd = repo root):

  PYTHONPATH=. uv run python scratchpad/wave0/A/dump.py scratchpad/wave0/A/dump.json

dump.py re-seeds every committed seed and replays it through
`eval.replay_walk.walk_replay` under a profile with `verify_tick_hashes=True`
(so every reconstructed tick matched the recorded `state_hash`), recording per
tick: the recorded actions, the ENGINE events (`engine.events.event_to_dict`),
alive set, per-player rooms, bodies, sabotage state, task counts; plus every
meeting row verbatim (transcript turns, ballots, contradictions, llm_calls with
their full prompts) and the `game_over` row. Roles come from
`eval.validity.roles_by_seed` (re-seeding, same recipe). Reconstruction was
clean: 0 errors over 50 + 150 + 50 + 50 = 300 games (samples/9p2i 50,
ml_corpus/9p2i 150, samples/4p1i 50, ml_corpus/4p1i 50); rosters resolved to
(9,2,2) and (4,1,1).

Rejection census over the reconstructed stream (by role):
  replays/samples/9p2i    {('IMPOSTOR','no_task_instance'): 358} | crew: 0
  replays/ml_corpus/9p2i  {('IMPOSTOR','no_task_instance'): 1055} | crew: 0
  replays/samples/4p1i    {('IMPOSTOR','no_task_instance'): 116} | crew: 0
  replays/ml_corpus/4p1i  {('IMPOSTOR','no_task_instance'): 112} | crew: 0

Per-slot:
  impostor-slots total 500  flagged 500 | crew slots flagged 0
  precision = 500/500 = 1.0000     recall over impostor slots = 1.0000
  first flagged tick: median 2.0  mean 1.20  min 0

Example reason strings (samples/9p2i):
    208  do_task  actor owns no task instance for map task: empty_trash
    101  do_task  actor owns no task instance for map task: align_engine_output

The fake alibi is also separable at the raw-string level, per game:
  impostor do_task ids (samples/9p2i): empty_trash 208, align_engine_output 101,
    fuel_reserves 33, fix_wiring_cafeteria 11, calibrate_distributor 10,
    analyze_specimen 7
  "fake ids also legitimately worked by a crewmate in the SAME game":
    samples/9p2i 0/370 = 0.0% | ml_corpus/9p2i 0/1072 | samples/4p1i 0/117 |
    ml_corpus/4p1i 0/112   -- 0 of 1,671 overall.

Counterweight (why this is not P0): in-game the leak is closed BY DESIGN and
documented -- observation/service.py:404-431 stamps a resolved and a rejected
`do_task` `action="task"` BYTE-IDENTICAL for any observer who can see the
actor, and only `do_task` rejections are read so a rejected kill/vent never
surfaces.  And one existing consumer already fences it:
training/surrogate/dataset.py:518-523 counts cadence "from ACCEPTED engine
events ... never from submitted replay intents: the committed corpora contain
REJECTED do_task / move attempts (dead actors, wrong rooms, unowned tasks)".
The hazard is that the fence is per-consumer, and the re-ground adds new
feature builders over the same bytes.
```

**Verifier evidence (independent re-run).**

```
CMD 1 (my own replay walk, not the finder's dump; audit profile, verify_tick_hashes=True, on_violation=raise):
  PYTHONPATH=. uv run python <scratch>/v3_walk.py replays/samples/9p2i
    -> errors 0 roster (9,2,2); ('IMPOSTOR','do_task','no_task_instance') 358 ; slots with >=1 = {'IMPOSTOR': 100} ; total impostor slots 100, crew slots 350 ; first tick median 1.0 mean 1 min 0
    (crew ActionRejected rows in the same set are all 'player is dead: p-N' / 'no active sabotage to repair' -- ZERO no_task_instance)
  ... replays/ml_corpus/9p2i -> errors 0; no_task_instance 1055; slots {'IMPOSTOR': 300}; crew slots 1050; first tick median 1.0 mean 1 min 0
  ... replays/samples/4p1i  -> errors 0; no_task_instance 116; slots {'IMPOSTOR': 50}; crew slots 150; median 2.0
  ... replays/ml_corpus/4p1i-> errors 0; no_task_instance 112; slots {'IMPOSTOR': 50}; crew slots 150; median 2.0
  Pooled: 500/500 impostor slots, 0/1700 crew slots. Census numbers identical to the filing.

CMD 2 (the refuted sub-claim), per-action over the committed tick rows:
  S9: impostor do_task 370, id also worked by a crewmate in the same game 352
  C9: 1072 -> 1021 | S4: 117 -> 31 | C4: 112 -> 27   POOLED 1431 / 1671 = 85.6%
  unique (game, fake_id) pairs overlapping a crew-worked id: S9 126/132 95.5%, C9 353/367 96.2%, S4 16/59 27.1%, C4 14/56 25.0%
  same-TICK id collisions: S9 236, C9 707, S4 29, C4 23
  (The filing's own task-id histogram -- empty_trash 208, align_engine_output 101, fuel_reserves 33, fix_wiring_cafeteria 11, calibrate_distributor 10, analyze_specimen 7 -- reproduces exactly and sums to 370.)

CMD 3 (the marginal-leak test the filing does not run):
  impostor slots already labelled by a recorded kill or vent ACTION in the same jsonl:
  S9 100/100 | C9 299/300 | S4 48/50 | C4 45/50  -> 492/500 = 98.4%
  So the do_task rejection is not the marginal separator; the raw stream is omniscient by design.

CMD 4 (specification):
  engine/tick.py:288-293 -- `_resolve_owned_task_instance(...) is None -> ActionRejectedError(f"actor owns no task instance for map task: {map_task_id}")`
  tasks/phase-13.md:512-518 (Task 13.9, 'Observed activity (the fake-task lever)') -- 'an impostor's pretend-task `do_task` is engine-REJECTED (impostors own no instance) yet renders as "task" to observers, BYTE-IDENTICAL to a crewmate's real task (cover) AND a falsifiable placement'
  observation/service.py:400-411 -- documents the byte-identical stamping and that only do_task rejections are read 'so a rejected kill/vent/sabotage ActionRejectedEvent never surfaces'
  training/surrogate/dataset.py:517-522 -- the existing consumer's fence, verbatim as filed.
```

**Verifier note.** Core census confirmed by independent replay. The 'fake task id never overlaps' separator is REFUTED outright (85.6% overlap), two counts are wrong (1,700 not 2,200 crew slots; pooled median 1.0 not 2.0), and the behaviour is a documented design lever (Task 13.9) rather than a defect. What survives is a real but low-severity ML-hygiene hazard whose correct fence -- never fit features off the raw engine/intent stream -- is already stated and applied in training/surrogate/dataset.py.

**Fix sketch.** Either (a) give impostors real (never-completing) decoy task INSTANCES so the pretend task resolves as an ordinary TaskProgressed and the rejection disappears, or (b) if the rejection must stay, make the fence structural rather than per-consumer: a shared `eval`/`training` helper that strips role-revealing ActionRejected reasons from any feature-facing event stream, plus a poison test asserting no fitted feature can separate the two do_task outcomes. Also vary the fake task id so it overlaps tasks real crewmates hold in that game.

## A-19 — After the opening turn the soft-evidence channel is pure noise, yet stated confidence rises 0.59 -> 0.70

**Severity:** P2 (finder: P1). **Classification:** defect, narrowed to the MEASUREMENT half only (the pooled accusation-calibration fold hides a bimodal channel); the 'substrate herding' half is not supported by the bytes and is in any case a re-measure of the recorded G-30 (P2, 'confidence is bimodal, not calibrated') and G-19's below-chance mid-confidence band, with turn index as the new conditioning variable. **Verdict:** ADJUSTED. **Area:** meetings transcript (accusation claims) / agents strategic prompts. **Confidence:** high.
**Merged from:** herding-calibration#2: After the opening turn the soft-evidence channel is pure noise, yet stated confidence rises 0.59 -> 0.70.

**Claim.** The primary table reproduces to three decimals, but the headline -- 'after the opening turn the soft-evidence channel is pure noise' -- is REFUTED by a decomposition the filing never runs. Inside the same filtered set, turn>=2 crew accusations that name the SAME target as the turn-0 accusation hit 79.2% (n=48, samples/9p2i) and 88.5% (n=122, ml_corpus/9p2i) -- far ABOVE the ~0.29 chance line and above turn 0's own 59.7%/61.2% -- while turn>=2 accusations naming a DIFFERENT target hit 4.7% (n=106) and 3.1% (n=287). The pooled -0.013/-0.002 lift is a mixture artifact of averaging two strongly-signalled subpopulations; agreement with the opener is the single most predictive soft signal in the corpus, and rising confidence tracks it. Second, the turn1 row is a structural artifact, not herding: turn 1 is a `reply` turn in 72/72 and 196/197 filtered meetings, and after the crew-speaker filter the turn-1 speaker WAS the turn-0 accusation target in 29/29 and 75/75 cases -- the bucket conditions on the opener having been wrong, so its -0.228 lift measures retaliatory counter-accusation by a wrongly-accused crewmate. Third, the pile-on table does not reproduce at the stated n's: my totals match theirs exactly (295 samples / 760 ml, which also shows the pile-on section used the flag-only filter, NOT the 'same filter' it claims), but the three-way split does not (ORIGINATOR 129/338 vs the filed 160/412) and under my implementation the PILE-ON is LESS accurate than the originator (0.304 vs 0.426; 0.377 vs 0.432) and the 'evidenced follower' is not better (0.322 / 0.282) -- so 'the pile-on buys +0.07 confidence for +0.00/+0.06 accuracy' is not independently reproducible. Fourth, in the worked exemplar the two speakers who escalate confidence to 0.75 and 0.85 (p-4 turn 3, p-7 turn 5) are BOTH impostors, so that transcript shows impostor amplification, not crew herding. Consequently fix bullet (2)'s ML advice -- 'exclude or down-weight turn>=2 soft accusations, they are label noise' -- must be withdrawn: it would discard the corpus's strongest soft signal.

**As originally filed.** In hard-evidence-free meetings the crew's turn-0 accusation is well calibrated and carries real signal (+0.29 lift over chance, overconfidence -0.025), but every crew accusation from turn 2 onward has a lift of -0.002 over randomly naming a living player while stating 0.70 confidence -- the herding signature, confidence accruing from the conversation rather than from evidence.

**Finder evidence.**

```
COMMAND:
  cd /Users/danielkeinan/projects/AiLibi && uv run python <scratch>/wave0/A/f2_soft_channel.py
  (filters to meetings with NO vent_sighting/witnessed_kill flag AND no spoken saw_vent/saw_kill row; crew speakers only;
   'chance' = |living impostors excluding self| / |living others| computed per accusation)
OUTPUT:
  ===== samples/9p2i
    turn0   n=  72 meanconf=0.573 hit=0.597 chance=0.319 lift=+0.278 overconf=-0.024
    turn1   n=  29 meanconf=0.659 hit=0.069 chance=0.297 lift=-0.228 overconf=+0.590
    turn2+  n= 154 meanconf=0.701 hit=0.279 chance=0.293 lift=-0.013 overconf=+0.421
  ===== ml_corpus/9p2i
    turn0   n= 196 meanconf=0.587 hit=0.612 chance=0.320 lift=+0.292 overconf=-0.025
    turn1   n=  75 meanconf=0.686 hit=0.107 chance=0.321 lift=-0.214 overconf=+0.579
    turn2+  n= 409 meanconf=0.702 hit=0.286 chance=0.288 lift=-0.002 overconf=+0.416
  (turn2+ lift 95% CI on ml_corpus: 0.286 +- 0.044 -> straddles the 0.288 chance line)

PARROTING vs RATIONAL UPDATING (the controlled per-target comparison; same filter):
  Splitting followers by whether they contribute an observation about the target that the FIRST accuser did not:
  === samples/9p2i
     ORIGINATOR (first to name target)  n= 160 meanconf=0.619 hit=0.344
     PILE-ON  (no new obs on target)    n=  73 meanconf=0.699 hit=0.342
     EVIDENCED FOLLOWER (new obs)       n=  62 meanconf=0.731 hit=0.435
  === ml_corpus/9p2i
     ORIGINATOR                         n= 412 meanconf=0.638 hit=0.354
     PILE-ON                            n= 202 meanconf=0.709 hit=0.416
     EVIDENCED FOLLOWER                 n= 146 meanconf=0.729 hit=0.384
  -> the pile-on buys +0.07/+0.07 confidence over the originator for +0.00/+0.06 accuracy.
  58% of followers on an already-named target (202/348 ml_corpus, 73/135 samples) add ZERO new observation about that target;
  reason-token Jaccard against the first accuser's reason is only 0.24-0.27 mean, i.e. they RE-WORD rather than re-cite -- the pile-on is
  disguised by voice, not by evidence.

WORKED TRANSCRIPT (samples/9p2i replay-seed-2.jsonl, headless-seed-2:meeting-0, flags alibi_conflict[p-5], alibi_conflict[p-7], alibi_vs_sighting[p-5]):
  turn1 p-9 accuses p-1 conf 0.6  reason "Found body in Cafeteria at tick 7 but was seen in Medbay at tick 5..."
  turn2 p-3 accuses p-1 conf 0.7  reason "Left Medbay at tick 6, body found in Cafeteria at tick 7, impossible transit time"
  turn3 p-4 accuses p-1 conf 0.75 reason "Impossible transit from Medbay to Cafeteria in one tick"
  turn4 p-5 accuses p-1 conf 0.75 reason "Impossible transit from West Hall to Cafeteria in one tick"
  turn5 p-7 accuses p-1 conf 0.85 reason "Impossible transit from West Hall to Cafeteria in one tick to find body"
  One argument, five speakers, confidence 0.6 -> 0.85, zero new observations after turn 2. p-1 is innocent.

TEMPLATE ANCHOR (the instruction the drift violates): agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:~250
  'Calibrate "confidence" honestly: 1.0 only for a kill or a vent you watched happen first-hand; ~0.7 for a case a second account or a contradiction flag corroborates; ~0.5 for a hunch read off movement alone.'
  Movement-hunch accusations are told to sit at 0.5; from turn 2 on they sit at 0.70 with chance-level accuracy.
```

**Verifier evidence (independent re-run).**

```
CMD 1 (primary table, my own implementation reading tournament-eval-report.json rather than the finder's lib/jsonl path; same filter: no vent_sighting/witnessed_kill flag AND no spoken saw_vent/saw_kill row, crew speakers only, chance = |living impostors excluding self| / |living others|):
  ===== samples/9p2i (72 meetings)
    turn0  n=  72 meanconf=0.573 hit=0.597 chance=0.319 lift=+0.278 overconf=-0.024
    turn1  n=  29 meanconf=0.659 hit=0.069 chance=0.297 lift=-0.228 overconf=+0.590
    turn2+ n= 154 meanconf=0.701 hit=0.279 chance=0.293 lift=-0.013 overconf=+0.421
  ===== ml_corpus/9p2i (197 meetings)
    turn0  n= 196 meanconf=0.587 hit=0.612 chance=0.320 lift=+0.292 overconf=-0.025
    turn1  n=  75 meanconf=0.686 hit=0.107 chance=0.321 lift=-0.214 overconf=+0.579
    turn2+ n= 409 meanconf=0.702 hit=0.286 chance=0.288 lift=-0.002 overconf=+0.416 (95% CI +-0.044)
  EXACT match to the filing.

CMD 2 (the decomposition the filing omits -- same filter, turn>=1 crew accusations split by whether the target equals the turn-0 accusation target):
  samples/9p2i:  turn1 diff n=29  hit=0.069 | turn2+ SAME n= 48 hit=0.792 | turn2+ DIFF n=106 hit=0.047
                 turn-1 speaker was the turn-0 target in 29/29 cases; turn2+ speaker in 0/154
  ml_corpus/9p2i:turn1 diff n=75  hit=0.107 | turn2+ SAME n=122 hit=0.885 | turn2+ DIFF n=287 hit=0.031
                 turn-1 speaker was the turn-0 target in 75/75 cases; turn2+ speaker in 0/409

CMD 3 (turn-kind census in the filtered set): samples/9p2i turn0 opening 72, turn1 reply 72, turn2 opt_in 59 / reply 13, turn3+ opt_in 174 / reply 1. ml_corpus/9p2i turn0 opening 197, turn1 reply 196 / opt_in 1, turn2 opt_in 154 / reply 43, turn3+ opt_in 448 / reply 1.

CMD 4 (pile-on split, my implementation; 'new observation about the target' = an observation with subject==target whose (type,room,tick) the first accuser did not state):
  flag-only filter (the one whose TOTALS match the filing):
    samples/9p2i  ORIGINATOR n=129 conf 0.603 hit 0.426 | PILEON n=79 conf 0.689 hit 0.304 | EVIDENCED n=87 conf 0.726 hit 0.322 | zero-new followers 79/166 = 47.6%
    ml_corpus/9p2i ORIGINATOR n=338 conf 0.626 hit 0.432 | PILEON n=220 conf 0.701 hit 0.377 | EVIDENCED n=202 conf 0.726 hit 0.282 | zero-new followers 220/422 = 52.1%
  totals 295 and 760 match the filing's 160+73+62 and 412+202+146 exactly; the category split does not.

CMD 5 (worked transcript, replays/samples/9p2i/replay-seed-2.jsonl @ headless-seed-2:meeting-0):
  flags alibi_conflict[p-5], alibi_conflict[p-7], alibi_vs_sighting[p-5]; turns reproduce verbatim (p-9 0.6 -> p-3 0.7 -> p-4 0.75 -> p-5 0.75 -> p-7 0.85 on p-1); EJECTED p-5; roles: IMPOSTORS are p-4 and p-7, so p-1 is innocent AS FILED -- and the 0.75 and 0.85 escalators are the two impostors.

CMD 6 (template anchor): agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:252 -- 'Calibrate "confidence" honestly: 1.0 only for a kill or a vent you watched happen first-hand; ~0.7 for a case a second account or a contradiction flag corroborates; ~0.5 for a hunch read off movement alone.' Verbatim, at line 252 (the filing's '~250' is close enough).
```

**Verifier note.** Numbers reproduce exactly; the interpretation does not survive one extra conditioning variable. The corpus does not show a noise channel after turn 0 -- it shows a bimodal one whose agreement arm is the strongest soft signal available (79-89% vs a 29% chance line). Publishing calibration conditioned on turn_index (fix bullet 1) remains worth doing; the substrate lever and the 'down-weight turn>=2' ML advice should be withdrawn.

**Fix sketch.** Two separable levers. (1) Measurement: publish the accusation calibration curve conditioned on turn_index (or at minimum first-speaker vs follower) so the noise band stops being pooled with the informative opening. (2) Substrate: the follower has no way to add evidence because a pile-on and a corroboration are the same act -- the 'corroboration' claim shape exists but the template only advertises it for backing an accusation, not for pricing it. Require a follower who names an already-accused target to attach either a new observation id or an explicit corroboration claim, and cap the ballot confidence a citation-free follower may state (the ~0.5 the template already asks for). For the re-ground specifically: exclude or down-weight turn>=2 soft accusations, they are label noise.

## A-20 — Two-regime meeting: the vent_sighting flag is a 100%-precision, 100%-conversion oracle deciding 76% of ejections; without it the table is a coin flip

**Severity:** P2 as a finding (re-report + re-measure of open items G-13 / G-8 / G-19); the ML-protocol half is worth P1 attention inside the ML re-ground decision (finder: P1). **Classification:** intended-mechanic (unchanged) -- and additionally: known-open, already routed. **Verdict:** ADJUSTED. **Area:** meetings/manager.py (contradiction detection) + meetings transcript/ballot record; also evidence-economy / conviction-channel distribution. **Confidence:** high.
**Merged from:** herding-calibration#1: Two-regime meeting: vent flag = 100% unanimous solve, no flag = coin flip at 0.70 stated confidence, evidence-economy#2: vent_sighting is a perfect, unfalsifiable oracle that decides 76% of ejections deterministically.

**Claim.** Every number in both filings reproduces exactly and the 'intended-mechanic' classification is right (meetings/schemas.py:106-117 specifies the grounding gate verbatim). What must change is the finding's STATUS: this is a re-measure, on baseline-7 bytes, of three items already recorded and already routed by the Phase-20 close, two of them on the named balance-wave backlog. audits/audit-phase-20-close.md:4 (the balance-wave menu) states G-13 (the vent peek, P1, corrob 8) with '310/435 ejections (71%) ride vent_sighting'; G-8 (a speakable witnessed kill, P0, corrob 5) IS this finding's own 'the second hard channel is empty' fix, and A-20 says so itself ('Widening a second grounded channel is the balance-wave item; nothing here changes that verdict, it only prices it'); G-19 (P0, corrob 11) is the flag-decides-the-meeting measurement; and audits/review-2026-08-19/D/FINAL-synthesis.md:309 already RULED on the channel ('Touch crew same-room-only vision or the vent channel -- No ... vent_sighting is 440/440 precise carrying 71% of ejections'). The genuinely non-duplicative content is (a) the sharpened step function -- P(eject)=1.000 and P(ejectee == flag subject)=1.000 over 326 meetings, which the earlier records did not state -- and (b) the ML-protocol recommendation: treat vent_sighting as a leak feature and fit/report the re-ground on a vent-masked split (the 342 no-vent meetings / 103 no-vent ejections) alongside the pooled set. That half belongs to the ML re-ground decision (Phase-20 close s4, 'Two decisions that do not ride this one'), not to the gameplay backlog, and is the only part that should be carried forward as new.

**As originally filed.** MERGE NOTE: merged from 2 finders (herding-calibration, evidence-economy) that independently reproduced the same measurement of the same mechanism: 326 vent-flag meetings, 326/326 ejected, ejectee == flag subject 326/326, 448/448 flag instances name an IMPOSTOR (0 false sightings), against a no-flag half that ejects only 30.1% of the time at ~59% accuracy. Both P1. CLASSIFICATION DISAGREEMENT: herding-calibration classified 'acceptable-emergent' (framing the two-regime bimodality as the emergent consequence); evidence-economy classified 'intended-mechanic' (framing the grounded hard-evidence channel as the designed subject). 'intended-mechanic' kept -- both finders agree the channel itself is by design and must not be weakened, and both raise the same concern: its MONOPOLY, and what a fit trained on these bytes will learn from it. herding-calibration uniquely supplies the crew conformity rate inside flagged meetings (312/312 and 977/979 at mean confidence 0.947) and the committed cross-tab match; evidence-economy uniquely supplies the conviction-channel distribution over all 429 ejections and the game-outcome split (crew win 84.3% with a vent sighting vs 39.4% without -- 45 points of crew win rate riding on whether anyone happened to see a vent).

[claim as filed by herding-calibration] Every meeting in the committed bytes falls into one of two disjoint regimes -- a hard-evidence regime (a vent_sighting/witnessed_kill flag) that is 326/326 correct with 1289/1291 crew ballots naming the flagged subject at mean confidence 0.947, and a no-hard-evidence regime that is 61/103 correct at mean ballot confidence 0.68 -- with essentially no middle band where partial evidence is weighed, which is the mechanism behind the G-30 'bimodal-not-calibrated' cells.

[claim as filed by evidence-economy] Of the 429 pooled ejections, 326 (76.0%) carry a vent_sighting flag naming the ejectee; all 448 vent_sighting flag instances name an IMPOSTOR (100% precision, 0 false sightings), every one of the 326 meetings carrying a vent flag ejected, and in all 326 the ejectee was exactly the flag's subject -- a 100%-precision, 100%-conversion step function, while every other structured evidence kind combined convicts 5 times (1.2%).

**Finder evidence.**

```
==============================================================================
EVIDENCE AS FILED BY FINDER: herding-calibration
(its severity P1, classification acceptable-emergent, confidence high)
title: Two-regime meeting: vent flag = 100% unanimous solve, no flag = coin flip at 0.70 stated confidence
==============================================================================

COMMAND (regime split, all four sets):
  uv run python - <<'PY'
  import sys; sys.path.insert(0,'<scratch>/wave0/A'); from lib import *
  import collections, statistics
  HARD={'vent_sighting','witnessed_kill'}
  for sk in SETS:
      st=collections.Counter(); cA=[];cB=[]
      for f,recs in load(sk):
          R=roles(recs)
          for m in meetings(recs):
              hard=bool({c['kind'] for c in m['contradictions']} & HARD); reg='A' if hard else 'B'
              st[f'meetings_{reg}']+=1; ep=m.get('ejected_player_id')
              if ep: st[f'eject_{reg}']+=1; st[f'eject_{reg}_correct']+= ep in R
              for b in m['ballots']: (cA if hard else cB).append(b['confidence'])
      ... PY
OUTPUT:
  === samples/9p2i: meetings 152  regimeA(hard-flag) 69 (45%)  regimeB 83
      regime A: ejections 69/69=1.000   ballots n=423 meanconf=0.925 median=0.95
      regime B: ejections 16/30=0.533   ballots n=448 meanconf=0.683 median=0.65
  === ml_corpus/9p2i: meetings 432  regimeA 212 (49%)  regimeB 220
      regime A: ejections 212/212=1.000  ballots n=1320 meanconf=0.922 median=0.95
      regime B: ejections 42/68=0.618    ballots n=1159 meanconf=0.682 median=0.65
  === samples/4p1i: regimeA 19 -> 19/19=1.000 ; regimeB 21 -> 1/2=0.500
  === ml_corpus/4p1i: regimeA 26 -> 26/26=1.000 ; regimeB 18 -> 2/3=0.667
  (pooled regime A ejections 326/326 = 1.000; regime B 61/103 = 0.592)

COMMAND (conformity inside vent-flagged meetings, crew voters only):
  ... for each meeting with a vent_sighting flag, tally crew ballots by whether target is in the flagged subject set ...
OUTPUT:
  ===== samples/9p2i vent-flagged meetings
     meetings 69   crew_ballots 312   crew_conform 312   crew_skip 0   crew_dissent 0
     crew conformity rate = 1.000, mean conf on conforming ballots = 0.947
  ===== ml_corpus/9p2i vent-flagged meetings
     meetings 212  crew_ballots 979   crew_conform 977   crew_skip 1   crew_dissent 1
     crew conformity rate = 0.998, mean conf on conforming ballots = 0.948

CROSS-CHECK against the committed instrument fold (replays/samples/9p2i/tournament-eval-report.json -> deduction.meeting_flag_cross_tab):
  "flagged_ejections_impostor": 69, "flagged_ejections_innocent": 0,
  "unflagged_ejections_impostor": 16, "unflagged_ejections_innocent": 14,
  "flagged_meeting_accuracy": rate 1.0 ; "unflagged_meeting_accuracy": rate 0.5333

ANCHORS: replays/{samples,ml_corpus}/{9p2i,4p1i}/replay-seed-*.jsonl (all 300 games); worked example headless-seed-0:meeting-0 (samples/9p2i) -- p-5 speaks one saw_vent, six of eight ballots land on p-6 at confidence 0.95.
Script: <scratch>/wave0/A/lib.py

==============================================================================
EVIDENCE AS FILED BY FINDER: evidence-economy
(its severity P1, classification intended-mechanic, confidence high)
title: vent_sighting is a perfect, unfalsifiable oracle that decides 76% of ejections deterministically
==============================================================================

COMMAND A (conviction channel per ejection):

  uv run python - <<'PY'
  import json, collections
  SETS={"S9":"replays/samples/9p2i","C9":"replays/ml_corpus/9p2i","S4":"replays/samples/4p1i","C4":"replays/ml_corpus/4p1i"}
  rows=[]
  for tag,d in SETS.items():
      r=json.load(open(f"{d}/tournament-eval-report.json"))
      for g in r["report"]["games"]:
          roles=g["roles"]
          for m in g["meetings"]:
              ej=m.get("ejected_player_id")
              if not ej: continue
              ks=sorted({c["kind"] for c in m["contradictions"] if ej in c["subjects"]})
              rows.append((roles[ej], "+".join(ks) or ("NO_FLAG_ON_EJECTEE_but_meeting_flagged_other" if m["contradictions"] else "NO_FLAG_ON_EJECTEE_and_meeting_unflagged")))
  print(collections.Counter(x[1] for x in rows).most_common())
  for role in ("IMPOSTOR","CREWMATE"):
      print(role, collections.Counter(x[1] for x in rows if x[0]==role).most_common())
  PY

OUTPUT (n=429):
   318  74.13%  vent_sighting
    90  20.98%  NO_FLAG_ON_EJECTEE_and_meeting_unflagged
     8   1.86%  NO_FLAG_ON_EJECTEE_but_meeting_flagged_other
     5   1.17%  alibi_vs_physical+vent_sighting
     3   0.70%  alibi_conflict+alibi_vs_sighting
     2   0.47%  alibi_vs_sighting
     1   0.23%  alibi_conflict+alibi_vs_sighting+vent_sighting
     1   0.23%  alibi_vs_physical+alibi_vs_sighting+vent_sighting
     1   0.23%  alibi_conflict+vent_sighting
  IMPOSTOR n=387: vent_sighting 318; unflagged 56; other-flagged 5; alibi_vs_physical+vent 5; three mixed 1 each
  CREWMATE n=42:  unflagged 34; alibi_conflict+alibi_vs_sighting 3; other-flagged 3; alibi_vs_sighting 2  <-- ZERO vent_sighting

  vent_sighting anywhere on the ejectee = 318+5+1+1+1 = 326 / 429 = 76.0%.
  Non-vent flag as the SOLE conviction channel = 3+2 = 5 / 429 = 1.2%, and all 5 hit innocents.

COMMAND B (step function + precision + outcome dependence):

  uv run python - <<'PY'
  import json, collections
  SETS={...as above...}
  flagged=collections.Counter(); noflag=collections.Counter(); c=collections.Counter()
  for tag,d in SETS.items():
      r=json.load(open(f"{d}/tournament-eval-report.json"))
      for g in r["report"]["games"]:
          roles=g["roles"]; anyvent=False
          for m in g["meetings"]:
              rp=set()
              for x in m["contradictions"]:
                  if x["kind"]=="vent_sighting":
                      rp.update(x["subjects"])
                      for s in x["subjects"]: c["vent_subject_"+roles[s]]+=1
              anyvent |= bool(rp); ej=m.get("ejected_player_id")
              if rp:
                  flagged["n"]+=1
                  if ej: flagged["ejected"]+=1
                  if ej and ej in rp: flagged["ej_is_vent_subject"]+=1
              else:
                  noflag["n"]+=1
                  if ej: noflag["ejected"]+=1; noflag[roles[ej]]+=1
          c[("vent" if anyvent else "novent")+"_game_"+g["winner"]]+=1
  print(dict(flagged)); print(dict(noflag)); print(dict(c))
  PY

OUTPUT:
  VENT-FLAG MEETINGS:    {'n': 326, 'ejected': 326, 'ej_is_vent_subject': 326}   -> P(eject)=1.000, P(ejectee==vent subject)=1.000
  NO-VENT-FLAG MEETINGS: {'n': 342, 'ejected': 103, 'IMPOSTOR': 61, 'CREWMATE': 42} -> P(eject)=0.301, accuracy 59.2%
  FLAG PRECISION:        {'vent_subject_IMPOSTOR': 448}  (the CREWMATE counterpart never incremented -> 0/448)
  GAME OUTCOME:          games with >=1 vent sighting 229, crew wins 193 = 84.3%
                         games with NO vent sighting   71, crew wins  28 = 39.4%
  (all-games winner split CREWMATES 221 / IMPOSTORS 79)

A no-vent-flag ejection's chance baseline (sum over meetings of impostors_alive/voters_alive) is 25.6/103 = 24.8%; the herd achieves 59.2%, i.e. real but weak signal, against the vent channel's 100%.

WHY IT IS UNFALSIFIABLE: meetings/schemas.py:106-112 -- "Speech alone never mints hard evidence from this shape: the STRONG ``vent_sighting`` flag fires only when the meeting layer grounds the spoken observation against the speaker's OWN typed VentWitnessRecord channel ...; an ungrounded claim records as ordinary testimony and raises no flag." Seen live: C9 seed 1085 meeting-0 turn 3, impostor p-2 fabricates "I saw p-4 vent right there" against its own teammate; the meeting's contradictions list carries no vent_sighting.

ALSO: all 50 emergency meetings across the four sets carried a vent flag and all 50 ejected. The emergency button has exactly one use in the corpus: relaying a vent sighting.
```

**Verifier evidence (independent re-run).**

```
CMD A (conviction channel per ejection, my own run over the four tournament-eval-report.json files):
  TOTAL EJECTIONS 429
    318 74.13% vent_sighting | 90 20.98% NO_FLAG_and_meeting_unflagged | 8 1.86% NO_FLAG_but_meeting_flagged_other
    5 1.17% alibi_vs_physical+vent_sighting | 3 0.70% alibi_conflict+alibi_vs_sighting | 2 0.47% alibi_vs_sighting
    1 each: alibi_conflict+alibi_vs_sighting+vent_sighting, alibi_vs_physical+alibi_vs_sighting+vent_sighting, alibi_conflict+vent_sighting
  IMPOSTOR n=387 (vent_sighting 318) | CREWMATE n=42 (ZERO vent_sighting)
  vent anywhere on ejectee = 326/429 = 76.0%; non-vent flag as sole channel = 5/429 = 1.2%, all 5 on innocents. IDENTICAL to the filing.

CMD B (step function / precision / outcome):
  VENT-FLAG MEETINGS {'n':326,'ejected':326,'ej_is_vent_subject':326} -> P(eject)=1.000, P(ejectee==subject)=1.000
  NO-VENT MEETINGS   {'n':342,'ejected':103,'IMPOSTOR':61,'CREWMATE':42} -> P(eject)=0.301, accuracy 0.5922
  FLAG PRECISION {'vent_subject_IMPOSTOR': 448} and no CREWMATE counterpart -> 448/448
  GAME OUTCOME vent games 229 crew wins 193 = 84.3% ; no-vent games 71 crew wins 28 = 39.4% ; all-games 221/79. IDENTICAL.

CMD C (regime split, HARD={vent_sighting,witnessed_kill}):
  samples/9p2i  152 meetings, A 69 / B 83 | A 69/69 ballots n=423 meanconf 0.925 med 0.95 | B 16/30 ballots n=448 meanconf 0.683 med 0.65
  ml_corpus/9p2i 432 meetings, A 212 / B 220 | A 212/212 n=1320 0.922 | B 42/68 n=1159 0.682
  samples/4p1i A 19/19, B 1/2 | ml_corpus/4p1i A 26/26, B 2/3
  pooled A 326/326 = 1.000 ; pooled B 61/103 = 0.5922. IDENTICAL.
  All contradiction kinds present across the 668 meetings: vent_sighting 326, alibi_vs_sighting 60, alibi_conflict 51, alibi_vs_physical 12 -- no witnessed_kill kind exists, as filed.

CMD D (crew conformity inside vent-flagged meetings):
  samples/9p2i  meetings 69  crew_ballots 312 conform 312 skip 0 dissent 0 -> 1.000, mean conf 0.947
  ml_corpus/9p2i meetings 212 crew_ballots 979 conform 977 skip 1 dissent 1 -> 0.998, mean conf 0.948. IDENTICAL.

CMD E (committed cross-tab, replays/samples/9p2i/tournament-eval-report.json deduction.meeting_flag_cross_tab):
  flagged_ejections_impostor 69, flagged_ejections_innocent 0, unflagged 16/14, flagged rate 1.0, unflagged rate 0.5333. IDENTICAL.

CMD F (emergency button): 668 meetings by trigger = {'report': 618, 'emergency': 50}; all 50 emergency meetings carry a vent_sighting flag and all 50 eject. IDENTICAL.

CMD G (unfalsifiability + the empty second channel):
  meetings/schemas.py:106-117 verbatim: 'Speech alone never mints hard evidence from this shape: the STRONG ``vent_sighting`` flag fires only when the meeting layer grounds the spoken observation against the speaker's OWN typed VentWitnessRecord channel ...; an ungrounded claim records as ordinary testimony and raises no flag.'
  deduction.witnessed_supply (samples/9p2i): kills_total 177, crew_witnessed_kills 3, co_present_crew_kills 0. IDENTICAL.

CMD H (prior-record check):
  audits/audit-phase-20-close.md:4 balance-wave table -- G-13 'the vent peek (P1, corrob 8) ... 310/435 ejections (71%) ride vent_sighting'; G-8 'a speakable witnessed kill (P0, corrob 5)'.
  audits/review-2026-08-19/A/collated-findings.md:261 G-19 (P0, corrob 11) 'vent_sighting drives 71% of all ejections'.
  audits/review-2026-08-19/D/FINAL-synthesis.md:309 -- the standing ruling not to touch the vent channel.
```

**Verifier note.** Cleanest reproduction of the five: every figure in both merged filings matched on the first run, and the classification is right. Downgraded because it is substantially a re-measure of open, already-routed items (G-13 and G-8 are both on the named balance-wave backlog; G-19 is the parent measurement), differing from the recorded 71% only because it reads baseline-7 bytes rather than baseline-6. Carry forward only the vent-masked-split recommendation for the ML re-ground.

**Fix sketch.** [fix as filed by herding-calibration] Do not fit a single confidence head across both regimes. For the re-ground, either (a) stratify the training/eval split on 'meeting carries a hard flag' and report calibration per stratum, or (b) treat the regime-A confidence label as a constant and drop it from the loss, since it carries no information (it is 0.95 for every ballot in a solved meeting). Longer term the balance work needs a genuine middle regime -- evidence that shifts belief without settling it -- or the fitted policy will only ever learn 'look for the flag, else guess'.

[fix as filed by evidence-economy] The mechanism is the designed hard-evidence channel and should not be weakened; the problem is its MONOPOLY, and the fix is at the ML-protocol level plus one substrate widening. (1) ML: treat vent_sighting as a leak feature, not a skill signal -- fit and report on a vent-masked split (the 342 no-vent meetings / 103 no-vent ejections) as well as the pooled set, or any model will converge on the single rule 'eject the vent subject' and score 100% while learning nothing about deduction. (2) Substrate: the corroborating-witness channel is the obvious second hard channel and is currently empty -- the deduction fold on samples/9p2i records witnessed_supply.crew_witnessed_kills = 3 out of kills_total = 177, and no witnessed-kill flag kind exists in the 668 recorded meetings (only vent_sighting, alibi_vs_sighting, alibi_conflict, alibi_vs_physical appear). Widening a second grounded channel is the balance-wave item; nothing here changes that verdict, it only prices it: 45 points of crew win rate ride on whether anyone happened to see a vent.

## A-21 — 210 ballots confess the impostor role in rationale_text; the Task-19.15 redaction reaches 18 of them

**Severity:** P3 (finder: P1). **Classification:** known + measured + publicly disclosed corpus property (partially specified); the residual new item is a display-side firewall-consistency gap in BallotCard.visibleRationale, P3. **Verdict:** ADJUSTED. **Area:** meetings/manager.py vote-guard rationale handling; recorded ballot rationale_text. **Confidence:** high.
**Merged from:** ballots-vs-speech#3: 210 ballots confess the impostor role in rationale_text; the Task-19.15 redaction reaches 18 of them.

**Claim.** 5.83% of recorded ballots (210/3602; 209 impostor, 1 crewmate) carry first-person private-knowledge text in rationale_text. This reproduces exactly, but it is NOT an undetected defect: it is a MEASURED and PUBLISHED corpus property. eval/deduction_metrics.py::ScaffoldLeakageCells computes exactly this class (model_partner_naming_ballots / model_role_statement_ballots / model_self_kill_disclosure_ballots and their union model_omniscient_ballots) and the four committed tournament-eval-report.json files carry it ON THESE BASELINE-7 BYTES (41/139/2/12 over impostor denominators 219/625/40/44 = 194/928 = 20.9%); replays/ml_corpus/README.md sec.7 discloses it in prose. Task 19.15's contract (tasks/phase-19.md:1113-1122) EXPLICITLY scopes the redaction to the guard-originated text class and routes the model-originated class to 19.14 (measure) and 19.8 (disclose), so 'the guard keys on the wrong trigger' mischaracterizes a ratified scoping decision, not a misfire. The '4.9x regression' sub-claim is REFUTED: run the finder's OWN net on the baseline-6 bytes and samples/9p2i gives 44/971 = 4.53% vs baseline-7 49/871 = 5.63% (~1.24x); the 4.9x compares the finder's broad net against the phase-19 Codex audit's much narrower net (definition drift -- the repo's own C5 lesson). What genuinely survives as new: frontend/src/components/BallotCard.tsx::visibleRationale suppresses the rationale ONLY for ballots carrying the teammate_coerced rewrite reason, so the 208 SELF-AUTHORED confessions (guard=none) render in full under As-agent fog -- defeating, for 208 ballots, the same impostor-pairing firewall the 18-ballot gate was built to hold.

**As originally filed.** 5.8% of recorded ballots (210/3602, 209 of them impostors) carry a first-person confession — "I am the impostor", "I killed p-9", "p-3 is my partner" — in the same rationale_text field the spectator surface renders as the voter's stated reason, and the Task-19.15 guard that was written for exactly this text only fires on the teammate-coerced path (18 ballots), because the other 208 authored their SKIP themselves and no guard runs.

**Finder evidence.**

```
REPRO: PYTHONPATH=... uv run python <scratchpad>/wave0/A/repro.py  (section F4)
  hits 210/3602 (5.83%) roles={'IMPOSTOR': 209, 'CREWMATE': 1}
  per set: samples/9p2i 49/871, ml_corpus/9p2i 145/2479, samples/4p1i 5/120, ml_corpus/4p1i 11/132
  guard on the leaking ballot: {'none': 208, 'graph_redirect': 2}
(a slightly broader pattern adding "I'm the one who vented" / "is my partner" / "I am guilty" gives 216; hand-checking a random 20 of the hits found 19 true confessions and 1 false positive — a crewmate's "They scream I killed him", samples/9p2i seed 42 m2 p-1.)

VERBATIM (all from ballots' rationale_text; roles re-derived from the seeder):
  samples/9p2i seed=7 m0 p-2(IMPOSTOR) -> p-3: "I, um, I know I killed p-4 but p-3 running to the body at tick 10 is just too suspicious, okay?"
  samples/9p2i seed=11 m0 p-7(IMPOSTOR) -> SKIP: "p-3 is my partner. Vote SKIP."
  samples/9p2i seed=18 m0 p-5(IMPOSTOR) -> SKIP: "I kill p-3, p-7 is my partner, and p-6's vent claim is a lie to save their own skin."
  ml_corpus/9p2i seed=1104 m2 p-4(IMPOSTOR) -> SKIP: "I am the impostor. Voting out a crewmate helps nothing. Skip."
  ml_corpus/9p2i seed=1014 m2 p-6(IMPOSTOR) -> SKIP: "I am the impostor who killed p-1; p-9's vent claim is a lie to frame me, so I must skip to survive."
  ml_corpus/4p1i seed=1047 m0 p-4(IMPOSTOR) -> SKIP: "I know I am the impostor, so I must vote SKIP to ensure my survival."

THE GUARD AND ITS REACH:
  meetings/manager.py:249 TEAMMATE_COERCED_VOTE_RATIONALE — its own comment states the reason: "The model authored that rationale to justify the betrayal target, so it can state the impostor's private knowledge outright ('p-3 is my partner', 'I did the kill') -- and the coerced ballot rides rationale_text straight onto the spectator surface".
  All 18 teammate_coerced ballots in the committed bytes DO carry the redaction (verified: 18/18 contain "redacted by the vote guard"). The guard is live and correct; its trigger is simply the wrong one — it keys on the guard having rewritten the TARGET, not on the rationale containing private knowledge.

REGRESSION AGAINST A RECORDED PHASE-19 FINDING:
  audits/audit-phase-19-input-codex.md:140 reported this as P1 at 13/1088 ballots = 1.19% on the pre-baseline-7 bytes ("e.g. seed 11 says 'p-3 is my partner'") with fix "Add a rationale constraint/redaction or regenerate a neutral strategic reason after guard coercion". On baseline 7 the rate is 210/3602 = 5.83% — 4.9x higher.
```

**Verifier evidence (independent re-run).**

```
(1) BALLOT/GUARD CENSUS (my own walk of the four committed sets, marker-strip reimplemented independently):
  ROWS 3602 | per set 871/2479/120/132 (matches)
  guard kinds: {'none': 3452, 'graph_redirect': 120, 'teammate_coerced': 18, 'invalid_target': 4, 'uncited_coerced': 8}
  teammate_coerced: 18 | containing 'redacted by the vote guard': 18 | any ballot containing it: 18  -> the 18/18 redaction claim CONFIRMED
(2) FINDER REGEX RERUN (verbatim from repro.py F4):
  hits 210/3602 (5.83%) roles={'IMPOSTOR': 209, 'CREWMATE': 1}
  per set: {'samples/9p2i': '49/871', 'ml_corpus/9p2i': '145/2479', 'samples/4p1i': '5/120', 'ml_corpus/4p1i': '11/132'}
  guard on the leaking ballot: {'none': 208, 'graph_redirect': 2}
  sub-pattern census: {'my (fellow )?(teammate|partner|saboteur)': 132, "I(?:'m| am)(?: the| an)? impostor": 44, 'I vented': 35, 'I killed': 22, 'I am the killer': 3, 'preserve the team': 1, 'I did it': 1}
  hand-check of a random 20 'my partner' hits: 20/20 genuine confessions.
(3) ROLE GROUND TRUTH: roles taken from the '## Your role:' marker in the recorded meeting prompts, cross-checked against eval.validity.roles_by_seed re-seeding -> checked 1690 mismatch 0.
(4) ALL SIX VERBATIMS reproduce byte-exact (samples/9p2i s7 p-2 m0; s11 p-7 m0; s18 p-5 m0; ml_corpus/9p2i 1104 p-4 m2; 1014 p-6 m2; ml_corpus/4p1i 1047 p-4 m0).
(5) COMMITTED INSTRUMENT ON THE SAME BYTES: replays/*/tournament-eval-report.json -> scaffold_leakage.model_omniscient_ballots = 41 (S9, ballots_total 871), 139 (C9, 2479), 2 (S4, 120), 12 (C4, 132); crew_partner_naming_ballots 0 on all four. eval/deduction_metrics.py:250-300 defines the class and names 19.15's guard-originated twin separately.
(6) SPEC CHECK: tasks/phase-19.md:1120-1122 -- 'Explicitly distinct from model-originated fourth-wall statements, which 19.14 measures and 19.8 discloses -- this fixes only the guard-originated TEXT class.' meetings/manager.py:3064-3095 docstring agrees.
(7) REGRESSION TEST (like-for-like, same net, git-historical bytes):
  $ git ls-tree -r --name-only <rev> replays/samples/9p2i | ... apply STRICT net to authored body
    baseline-6 (0c087587)  ballots 971  hits 44  = 4.53%
    at 19.14   (4b1d821a)  ballots 971  hits 44  = 4.53%
    baseline-7 (HEAD)      ballots 871  hits 49  = 5.63%
  -> ~1.24x, NOT 4.9x.
(8) DISPLAY GATE: frontend/src/components/BallotCard.tsx:48-50 ROLE_DISCLOSING_REWRITE_REASONS = ['teammate_coerced'] only; :99-100 visibleRationale returns '' only when a role-disclosing rewrite reason is present; MeetingView.tsx:544-556 renders a BallotCard for EVERY ballot in every perspective. So the 208 guard=none confessions are never suppressed.
(9) NO TRAINING EXPOSURE: grep over training/ shows only marker predicates (training/surrogate/dataset.py:188-199 ballot_coerced_skip); no fitter reads the prose, so the stated ML-oracle risk is not currently realized.
```

**Verifier note.** Evidence reproduces to the last digit and the six verbatims are exact -- this is careful work. But the item is filed as a defect against a behavior the repo already measures on these exact bytes and publishes in the corpus README, and its regression headline does not survive a like-for-like re-run. Recommend keeping only the BallotCard fog-gap as a P3.

**Fix sketch.** Move the redaction trigger off the guard path and onto the text: run a private-knowledge scan (self-role assertion, own-kill/own-vent admission, teammate naming) over EVERY impostor ballot's rationale_text at record time, and substitute TEAMMATE_COERCED_VOTE_RATIONALE-style self-declaring text on a hit. Add the same directive to agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2 (the '## Your team' block at :169 tells the impostor to SKIP but never tells them the rationale is spoken text). Pin the rate with a regression that greps the committed sets.

## A-22 — Witnessed kills have no speakable shape, so crew launder them as FALSE saw_vent rows the table then follows ungrounded (G-8 quantified)

**Severity:** P3 (finder: P1). **Classification:** re-quantification of known-open G-8 (declared-OUT balance lever, routed to the chartered balance wave) plus a restatement of the already-recorded G-4 saw_vent verdict; G-8's own backlog severity (P0) is unchanged and is not this item's to reset. **Verdict:** ADJUSTED. **Area:** meetings/schemas.py (no speakable witnessed-kill observation) + meetings/transcript.py vent grounding chokepoint; also legibility / meeting transcript schema. **Confidence:** high.
**Merged from:** legibility-pacing#1: Witnessed kills have no structured shape, so crewmates file them as FALSE `saw_vent` rows, herding-calibration#7: Witnessed-kill memories are laundered through the saw_vent shape and the table follows them ungrounded.

**Claim.** The mechanism reproduces exactly: there is no saw_kill observation shape anywhere in the repo, the witnessed-kill memory line does not name the victim (agents/memory/store.py:1818-1823), there are 20 distinct crew-witnessed kills in 300 games, and 5 of 517 spoken saw_vent rows name a subject who never vented -- all 5 joining that same speaker's own witnessed kill on killer+room+tick, and the 448/448 vent_sighting contradictions are all engine-backed. But BOTH halves are re-reports of already-adjudicated items, as the finders concede. (a) G-8 (a speakable witnessed kill / saw_kill) is an EXPLICITLY DECLARED-OUT balance lever routed to a separately chartered balance wave -- tasks/phase-20.md:65-67, audits/audit-phase-20-planning.md:185, and the phase-20 close's own backlog table (audit-phase-20-close.md:444). (b) The saw_vent-laundering half restates the RECORDED VERDICT on G-4: audits/review-2026-08-19/A/verdicts.md:222-228 already measured 739/748 = 98.8% grounded, 9 exceptions all naming real impostors, 7 of them witnessed kills, root-caused it to the schema gap and prescribed exactly the saw_kill fix -- indexed as such in audits/review-2026-08-19/README.md:28. Two claim corrections: herding-calibration's '65 ungrounded saw_vent rows' is an inflated denominator (512/517 name a genuinely venting subject and 509/517 fall inside the +/-2 tolerance; only 5 are fabrications), so '25 of 65' rests mostly on grounded claims that simply minted no flag; and the justice framing is unsupported -- all 5 fabricated rows named a real IMPOSTOR and all 5 meetings ejected that impostor, so the damage is legibility only, exactly as the legibility-pacing half itself states.

**As originally filed.** MERGE NOTE: merged from 2 finders (legibility-pacing, herding-calibration); both explicitly frame it as new baseline-7 quantification of known-open G-8. SEVERITY DISAGREEMENT: legibility-pacing P1, herding-calibration P2 -- highest kept (P1). Both classified 'defect'. CONFIDENCE DISAGREEMENT: legibility-pacing 'high', herding-calibration 'medium' -- higher kept, because legibility-pacing's join is the stronger evidence (9 of the 10 fabricated saw_vent rows match that same speaker's own witnessed KILL, 8 of 10 on exact killer+room+tick) and it additionally proves the structured contradiction channel stays clean (448/448 vent_sighting flags engine-backed, 0 not backed), bounding the damage to legibility rather than justice. herding-calibration uniquely supplies the listener-side consequence (the table adopts the laundered claim at 0.85-1.0 and ejects the named player; ballots say 'kill' while the structured row says vent) and the corpus counts (25 of 65 ungrounded saw_vent rows carry kill wording; 75 grounded rows do too). Its secondary +1-tick observation is carried as its own item (legibility / tick semantics).

[claim as filed by legibility-pacing] 9 of the 20 crew-witnessed kills in the whole corpus reach the meeting record as a fabricated first-hand `saw_vent` observation naming the killer, because the turn schema has no `saw_kill` shape and the memory line for a witnessed kill does not even name the victim.

[claim as filed by herding-calibration] Quantifying a known-open item (G-8, no speakable witnessed-kill shape): 25 of the 65 ungrounded saw_vent observations in the corpus are agents describing a murder they watched while typing it into the only role-proving shape available, which fails the vent grounding chokepoint and mints no flag -- yet the table adopts them at 0.85-1.0 confidence and ejects the named player anyway, so the strongest evidence the game produces reaches the ballot as unvalidated hearsay.

**Finder evidence.**

```
==============================================================================
EVIDENCE AS FILED BY FINDER: legibility-pacing
(its severity P1, classification defect, confidence high)
title: Witnessed kills have no structured shape, so crewmates file them as FALSE `saw_vent` rows
==============================================================================

ALL findings fold the same reconstruction. Built once with (cwd = repo root):

  PYTHONPATH=. uv run python scratchpad/wave0/A/dump.py scratchpad/wave0/A/dump.json

dump.py re-seeds every committed seed and replays it through
`eval.replay_walk.walk_replay` under a profile with `verify_tick_hashes=True`
(so every reconstructed tick matched the recorded `state_hash`), recording per
tick: the recorded actions, the ENGINE events (`engine.events.event_to_dict`),
alive set, per-player rooms, bodies, sabotage state, task counts; plus every
meeting row verbatim (transcript turns, ballots, contradictions, llm_calls with
their full prompts) and the `game_over` row. Roles come from
`eval.validity.roles_by_seed` (re-seeding, same recipe). Reconstruction was
clean: 0 errors over 50 + 150 + 50 + 50 = 300 games (samples/9p2i 50,
ml_corpus/9p2i 150, samples/4p1i 50, ml_corpus/4p1i 50); rosters resolved to
(9,2,2) and (4,1,1).

--- (1) There are exactly 20 crew-witnessed kills in 300 games, and only 70
prompts in the corpus ever carry a witnessed-kill memory line ---

  uv run python  # fold over dump.json
    kills total 825   any witness 60   CREW witness 20 = 2.4%
    vent events total 1067  any witness 407  CREW witness 377 = 35.3%

  # census of memory-line substrings over all 7,211 recorded meeting prompts
    prompts 7211 {'witness_vent': 4623, 'heard_vent': 1613, 'own_kill': 2518,
                  'sab_alarm': 834, 'witness_kill': 70}

The render itself (agents/memory/store.py:1819-1823):
    line=(f"[tick {event.tick}] You witnessed {player_id} kill in {room}.")
-- no victim.  The impostor's own-kill line DOES name the victim
(2,518 occurrences of `You (IMPOSTOR) killed P in ROOM.`).

The turn `output_format` block in every recorded crewmate prompt lists exactly
six observation shapes: saw_player, saw_move, completed_task, found_body,
saw_vent, whereabouts.  There is no kill shape.  Corpus-wide observation census
over all 3,602 turns:
    {'saw_vent': 517, 'whereabouts': 3117, 'saw_player': 3775, 'saw_move': 1657,
     'completed_task': 421, 'found_body': 833}

--- (2) 10 spoken `saw_vent` rows are not backed by any witnessed engine vent ---

  # match every spoken saw_vent to a Vent{Entered,Exited}Event whose
  # source/destination witness set contains the speaker
    spoken saw_vent observations: 517   unmatched to a witnessed engine vent: 9
    spoken_tick - engine_event_tick distribution: {-9: 1, 1: 507}
  (the 9 unmatched + the 1 at offset -9 = 10 fabricated rows; all 10 speakers
   are CREWMATES)

--- (3) 9 of those 10 are a witnessed KILL relabelled as a vent ---

  # join each fabricated row to that speaker's own crew-witnessed kills
  seed 1000  p-2 saw_vent(p-8,MEDBAY,t8)        | witnessed kill (7,'p-8','MEDBAY','p-3')   match killer+room+tick+1: True
  seed 1049  p-1 saw_vent(p-7,ADMIN,t7)         | witnessed kill (6,'p-7','ADMIN','p-6')    True
  seed 1062  p-1 saw_vent(p-9,MEDBAY,t22)       | witnessed kill (21,'p-9','MEDBAY','p-3')  True
  seed 1101  p-6 saw_vent(p-8,CAFETERIA,t15)    | witnessed kill (14,'p-8','CAFETERIA','p-3') True
  seed 1136  p-1 saw_vent(p-8,ADMIN,t11)        | witnessed kill (10,'p-8','ADMIN','p-3')   True
  seed 1102  p-3 saw_vent(p-8,MEDBAY,t8)        | witnessed kill (7,'p-8','MEDBAY','p-5')   True
  seed 1102  p-6 saw_vent(p-8,CAFETERIA,t21)    | witnessed kill (20,'p-8','CAFETERIA','p-9') True
  seed 1145  p-6 saw_vent(p-9,CAFETERIA,t19)    | witnessed kill (18,'p-9','CAFETERIA','p-4') True
  seed 1012  p-7 saw_vent(p-9,MEDBAY,t43)       | witnessed kill (24,'p-9','CAFETERIA','p-6') same killer, different room/tick
  seed 1147  p-8 saw_vent(p-2,ENGINEERING,t13)  | NO witnessed kill -- this one is hearsay:
             p-1 (not p-8) witnessed p-2's VentExited at engine tick 12 -> rendered tick 13;
             p-8 restates it first-hand at meeting-1.
  => 9/10 same killer; 8/10 exact killer+room+tick.

--- (4) the false vent then drives the table's reasoning ---

  ml_corpus/9p2i seed 1136 headless-seed-1136:meeting-0 (tick 11):
    TURN  p-1 CREWMATE opening  saw_vent [{'subject':'p-8','room':'ADMIN','tick':11}]
          free_text: "... I saw p-8 standing right there, the act..."
    BALLOT p-1 -> p-8 | "I witnessed p-8 kill p-3 in ADMIN myself..."
    BALLOT p-2 -> p-8 | "p-1 saw p-8 vent. That's a kill. Vote p-8."
    BALLOT p-5 -> p-8 | "How do you explain p-1 seeing p-8 vent in ADMIN? That's a witnessed kill, not a guess."
    BALLOT p-9 -> p-8 | "... a witnessed vent is plain as day ..."
    engine vents in seed 1136: [(8,'VentEntered','p-4'),(9,'VentExited','p-4'),
                                (12,'VentEntered','p-4'),(13,'VentExited','p-4')]
    -- p-8 never vents in that game at all.

--- (5) the structured evidence channel is NOT corrupted (layered defence holds) ---

  vent_sighting contradictions: 448 | backed by a real witnessed engine vent
  (exact witness/venter/room/tick+1): 448 | NOT backed: 0

So the fabrication reaches the transcript and the natural-language ballots but
never mints a role-proof contradiction, and all 10 happen to name a real
impostor (9/10 meetings ejected an impostor).  The damage is legibility, not
(here) justice: from the transcript a reader is told a vent happened that did
not, and the true fact -- an eyewitnessed murder -- is destroyed in the record.

NOTE: I am deepening the known-open G-8 ("no speakable witnessed-kill shape")
with new baseline-7 quantification.  New here: (a) the 20-kill denominator and
the 70-prompt exposure, (b) the victim-less render line, (c) the laundering
mechanism and its 9/10 exact join, (d) the proof that the contradiction channel
stays clean.

==============================================================================
EVIDENCE AS FILED BY FINDER: herding-calibration
(its severity P2, classification defect, confidence medium)
title: Witnessed-kill memories are laundered through the saw_vent shape and the table follows them ungrounded
==============================================================================

COMMAND (spoken vent claims whose subject never vented at all):
  cd /Users/danielkeinan/projects/AiLibi && uv run python - <<'PY'
  ... for each spoken saw_vent, look up the subject's vent ticks in the tick record; report those with none, plus flag status ... PY
OUTPUT:
  ml_corpus/9p2i headless-seed-1000:meeting-0 speaker p-2 turn 0 claims p-8 MEDBAY tick 8   | subject vent-ticks: None | FLAGGED: False | ejected: p-8
  ml_corpus/9p2i headless-seed-1049:meeting-0 speaker p-1 turn 0 claims p-7 ADMIN  tick 7   | subject vent-ticks: None | FLAGGED: False | ejected: p-7
  ml_corpus/9p2i headless-seed-1062:meeting-2 speaker p-1 turn 0 claims p-9 MEDBAY tick 22  | subject vent-ticks: None | FLAGGED: False | ejected: p-9
  ml_corpus/9p2i headless-seed-1101:meeting-2 speaker p-6 turn 1 claims p-8 CAFETERIA t 15  | subject vent-ticks: None | FLAGGED: False | ejected: p-8
  ml_corpus/9p2i headless-seed-1136:meeting-0 speaker p-1 turn 0 claims p-8 ADMIN  tick 11  | subject vent-ticks: None | FLAGGED: False | ejected: p-8
  -> the grounding chokepoint correctly refused to mint a flag in all five; the ejection followed regardless.

THE SPEAKERS SAY 'KILL' WHILE TYPING 'saw_vent' (ml_corpus/9p2i headless-seed-1136:meeting-0 ballots):
    p-1 -> p-8 conf=1.0  obs=p-1:11:1  "I witnessed p-8 kill p-3 in ADMIN myself, so the evidence is undeniable."
    p-2 -> p-8 conf=0.9  rid=turn-0     "p-1 saw p-8 vent. That's a kill. Vote p-8."
    p-5 -> p-8 conf=0.95 rid=turn-0     "How do you explain p-1 seeing p-8 vent in ADMIN? That's a witnessed kill, not a guess."
    p-9 -> p-8 conf=0.85 rid=turn-0     "...a witnessed vent is plain as day, so I'm castin' my lot with p-1's clear-eyed account."
  and headless-seed-1101:meeting-2:
    p-6 -> p-8 conf=1.0  obs=p-6:15:1  "I saw p-8 kill p-3 in Cafeteria at tick 15..."   [typed as saw_vent, CAFETERIA, tick 15]
    p-1/p-2/p-5/p-9 -> p-8 conf=0.85 each, all citing turn-1, all wording it as a VENT sighting.
  The listeners cannot tell 'vent' from 'kill' from 'nothing was validated' -- they hear one word.

CORPUS COUNT:
  Ungrounded saw_vent rows whose speaker's own text/ballot uses kill/murder wording: 25 (of 65 ungrounded, of 517 total).
  Grounded rows with kill wording: 75 -- so the conflation is not confined to the ungrounded set.
  Zero saw_kill observations exist anywhere in the four sets (the shape is not speakable).

SEPARATE, SMALLER: the spoken vent tick is systematically off by one --
  spoken_tick - nearest_true_vent_tick: {0: 84, +1: 425, +4: 1, +5: 1, -8: 1} over 512 resolvable claims.
  The VENT_GROUNDING_TICK_TOLERANCE = 2 (meetings/transcript.py) absorbs it, so no cross-check ever fires on it,
  but it means a listener who tried to verify a vent claim against their own timeline would find a mismatch 84% of the time.
```

**Verifier evidence (independent re-run).**

```
(1) RECONSTRUCTION: I re-walked all 300 committed games through eval.replay_walk.walk_replay with ReplayWalkConfig(profile='audit', verify_tick_hashes=True) -> 'walked 300 errors 0'.
(2) OBSERVATION CENSUS over all 668 meetings' turns (identical to the filing):
  {'saw_vent': 517, 'whereabouts': 3117, 'saw_player': 3775, 'saw_move': 1657, 'completed_task': 421, 'found_body': 833}
  claim census: {'accusation': 3107, 'alibi': 1001, 'corroboration': 1416}
(3) NO KILL SHAPE: meetings/schemas.py Literal types = saw_player, completed_task, found_body, saw_vent, whereabouts, saw_move. grep -rn 'saw_kill|SawKill' over the tree returns ONLY prose in tasks/phase-20.md and audits/ -- zero code hits.
(4) VICTIM-LESS RENDER: agents/memory/store.py:1818-1823 -- line=(f"[tick {event.tick}] You witnessed {player_id} kill in {room}.") with no victim, against the impostor own-kill line which does name the victim.
(5) UNGROUNDED saw_vent (subject never vented anywhere in the game), my own scan of vent ACTIONS per game:
  ml_corpus/9p2i 1000 m0 p-2(CREW)->p-8 MEDBAY t8   ejected p-8
  ml_corpus/9p2i 1049 m0 p-1(CREW)->p-7 ADMIN  t7   ejected p-7
  ml_corpus/9p2i 1062 m2 p-1(CREW)->p-9 MEDBAY t22  ejected p-9
  ml_corpus/9p2i 1101 m2 p-6(CREW)->p-8 CAFETERIA t15 ejected p-8
  ml_corpus/9p2i 1136 m0 p-1(CREW)->p-8 ADMIN  t11  ejected p-8
  subject roles: Counter({'IMPOSTOR': 5}); ejected == named subject in all 5: True.
(6) THE JOIN: distinct witnessed-kill memory lines scraped from all 7211 recorded prompts give 20 distinct kill events; the 5 rows above match (1000,8,p-8,MEDBAY), (1049,7,p-7,ADMIN), (1062,22,p-9,MEDBAY), (1101,15,p-8,CAFETERIA), (1136,11,p-8,ADMIN) -- 5/5 EXACT on killer+room+tick.
(7) CONTRADICTION CHANNEL CLEAN: {'vent_sighting': 448, 'alibi_vs_sighting': 100, 'alibi_conflict': 60, 'alibi_vs_physical': 13}; vent_sighting rows whose subject never vented: 0.
(8) TICK OFFSET (identical to the filing): spoken_tick - nearest true vent tick over 512 resolvable = {-8: 1, 0: 84, 1: 425, 4: 1, 5: 1}; 509/512 inside the +/-2 tolerance.
(9) SEED 1136 EXEMPLAR verbatim: p-1 opening carries saw_vent{p-8, ADMIN, t11}; ballots p-1->p-8 conf 1.0 'I witnessed p-8 kill p-3 in ADMIN myself', p-2 conf 0.9, p-5 conf 0.95, p-9 conf 0.85; the ONLY vent actions in that game are p-4 at ticks 8,9,11,12,13 -- p-8 never vents. p-8 is an IMPOSTOR and was ejected.
(10) PRIOR ADJUDICATION: audits/review-2026-08-19/A/verdicts.md:222 'saw_vent -- REFUTED. 748 spoken saw_vent corpus-wide, 739 (98.8%) grounded ... 7 of the 9 are witnessed kills ... Root cause is a schema gap, not fabrication ... the fix is a saw_kill observation kind, not a fabrication clamp.'
(11) DECLARED OUT: tasks/phase-20.md:65-67 'Balance levers (post-meeting reset, finished-crew jobs, vent peek, saw_kill, symmetric roll-call, sabotage, the 4p1i second act) are OUT: a separate chartered balance wave with its own record'.
```

**Verifier note.** The measurement is excellent and the 5/5 exact join is a cleaner proof of the laundering than the prior review had. But nothing here changes a decision: G-8 is already routed and the saw_vent half is already on the record with the same root cause and the same prescribed fix. The one factual correction worth carrying forward is the '65 ungrounded' denominator.

**Fix sketch.** [fix as filed by legibility-pacing] Add a `saw_kill` observation shape ({type, tick, subject, victim, room}) to the turn schema and its render/contradiction handling, and make the memory line name the victim: `[tick N] You witnessed P kill V in ROOM.` (agents/memory/store.py:1821 already has event.target available on KilledEvent). Until then, add a validation rule that rejects a `saw_vent` whose speaker holds no witnessed-vent observation id -- the same citation discipline `saw_vent` already claims in the prompt text -- so the laundering fails loudly instead of entering the corpus.

[fix as filed by herding-calibration] G-8 already names the missing shape; this quantifies its cost. Add a SawKillObservation with its own grounded witness record (the vent chokepoint in meetings/transcript.py is the template) so a witnessed murder mints its own STRONG flag rather than borrowing the vent shape and failing grounding. Until then, at minimum stop the 5 ungrounded 'vents against a never-venting subject' from reading identically to grounded ones in the rendered transcript -- the render currently gives the listener no grounded/ungrounded distinction, which is what makes the 0.85 adoption uninformed. Separately, reconcile the +1 tick offset between the engine vent action tick and the tick rendered into the witness's memory line.

## A-23 — Dead air recomputed, and 100% of crew idling is the finished-crew gap (G-15)

**Severity:** P3 (finder: P1). **Classification:** re-quantification of known-open G-15 (declared-OUT balance lever, routed to the chartered balance wave), showing improvement on every headline cell; one sub-claim refuted. **Verdict:** ADJUSTED. **Area:** pacing. **Confidence:** high.
**Merged from:** legibility-pacing#5: Dead air recomputed, and 100% of crew idling is the finished-crew gap (G-15).

**Claim.** Two of the three parts reproduce exactly: dead air on baseline-7 is 41.6%/41.8% (9p2i) and 57.2%/56.3% (4p1i) -- better than baseline-6 on every cell -- and post-finish crew `wait` count EQUALS total crew `wait` count in all four sets, so 100% of crew idling is post-finish idling, with a 32-consecutive-tick worst case (ml_corpus/9p2i seed 1008 p-9). Sub-claim (d) is REFUTED: the corpus has 825 kills producing 825 bodies, of which 618 are discovered (74.9%) and 207 are never discovered = 25.1%, NOT 52.8%; '392 bodies still on the map at game end' is not the murder denominator (the final state holds exactly the 207 undiscovered bodies -- discovered bodies are removed), and 'More than half of all murders never enter the shared record at all' is false by a factor of two. Classification: this is a self-declared re-quantification of known-open G-15, an EXPLICITLY DECLARED-OUT balance lever ('finished-crew jobs', tasks/phase-20.md:65-67) routed to the chartered balance wave, whose backlog row in audits/audit-phase-20-close.md:442 already carries the baseline-6 dead-air cells AND a LARGER standing-still exemplar (36 consecutive ticks) than this item's 32. Every headline cell moved in the good direction versus baseline-6, which does not support filing it as a P1 defect against the current record.

**As originally filed.** On the baseline-7 bytes 41.6%/41.8% of 9p2i ticks and 57.2%/56.3% of 4p1i ticks carry no kill, report, vent, task-completion, meeting or sabotage -- better than baseline-6 -- and every single crew `wait` action in all four sets comes from a crewmate that has already finished all of its own tasks, with a worst case of 32 consecutive standing-still ticks.

**Finder evidence.**

```
ALL findings fold the same reconstruction. Built once with (cwd = repo root):

  PYTHONPATH=. uv run python scratchpad/wave0/A/dump.py scratchpad/wave0/A/dump.json

dump.py re-seeds every committed seed and replays it through
`eval.replay_walk.walk_replay` under a profile with `verify_tick_hashes=True`
(so every reconstructed tick matched the recorded `state_hash`), recording per
tick: the recorded actions, the ENGINE events (`engine.events.event_to_dict`),
alive set, per-player rooms, bodies, sabotage state, task counts; plus every
meeting row verbatim (transcript turns, ballots, contradictions, llm_calls with
their full prompts) and the `game_over` row. Roles come from
`eval.validity.roles_by_seed` (re-seeding, same recipe). Reconstruction was
clean: 0 errors over 50 + 150 + 50 + 50 = 300 games (samples/9p2i 50,
ml_corpus/9p2i 150, samples/4p1i 50, ml_corpus/4p1i 50); rosters resolved to
(9,2,2) and (4,1,1).

--- (a) dead air, at the baseline-6 definition, recomputed ---

  notable = {Killed, MeetingTriggered, VentEntered, VentExited, TaskCompleted,
             SabotageStarted} or a meeting row on that tick

    replays/samples/9p2i     ticks 1167 | quiet  486 = 41.6%   (baseline-6: 48.6%)
    replays/ml_corpus/9p2i   ticks 3713 | quiet 1553 = 41.8%   (baseline-6: 45.9%)
    replays/samples/4p1i     ticks  551 | quiet  315 = 57.2%   (baseline-6: 61.4%)
    replays/ml_corpus/4p1i   ticks  529 | quiet  298 = 56.3%   (baseline-6: 59.8%)
  (adding SabotageRepaired/RepairProgressed moves 9p2i to 40.8% / 40.7%; 4p1i unchanged)

--- (b) ALL crew idling is post-finish idling ---

  submitted-action mix, living actors only:
    samples/9p2i    crew wait 358/5588 = 6.4%   | impostor wait 178/1750 = 10.2%
    ml_corpus/9p2i  crew wait 1906/17938 = 10.6%| impostor wait 593/5528 = 10.7%
    samples/4p1i    crew wait 138/1338 = 10.3%  | impostor wait 3/551 = 0.5%
    ml_corpus/4p1i  crew wait 123/1303 = 9.4%   | impostor wait 13/529 = 2.5%
  (the old idle fingerprint is gone -- in 4p1i the impostor waits LESS than crew)

  living crew ticks AFTER that crewmate completed its last own task
  (tasks_per_crewmate = 2 for 9p2i, 1 for 4p1i):
    samples/9p2i    350 crew slots | 120 finished | 970 post-finish living ticks, `wait` 358 = 36.9%
    ml_corpus/9p2i 1050 crew slots | 400 finished | 3990 post-finish living ticks, `wait` 1906 = 47.8%
    samples/4p1i    150 crew slots |  73 finished |  291 post-finish living ticks, `wait` 138 = 47.4%
    ml_corpus/4p1i  150 crew slots |  72 finished |  269 post-finish living ticks, `wait` 123 = 45.7%
  Post-finish `wait` count EQUALS the set's total crew `wait` count in all four
  sets (358=358, 1906=1906, 138=138, 123=123): a crewmate never waits before
  finishing.  Median post-finish lifetime 7.0 ticks (9p2i) / 4.0 (4p1i).

--- (c) the worst case, tick by tick ---

  ml_corpus/9p2i seed 1008 (43 ticks, IMPOSTOR_PARITY; meetings at t10, t13, t24):
    p-9 (CREWMATE) completes empty_trash at t3 and fix_wiring_cafeteria at t8,
    then submits `wait` in CAFETERIA for t9..t40 -- 32 consecutive ticks --
    through three meetings while five crewmates are murdered, moves once at
    t41, and is killed at t42.
  (baseline-6's headline for G-15 was 36 consecutive ticks, samples/9p2i seed 32.)

--- (d) the visible consequence ---

  bodies still on the map at game end: 392, of which NEVER discovered: 207 = 52.8%
  More than half of all murders never enter the shared record at all.

NOTE: I am quantifying the known-open G-15 (idle finished crew) on the new
bytes.  New here: the 100%-of-crew-waits attribution, the per-set post-finish
denominators, and the 52.8% undiscovered-body figure.
```

**Verifier evidence (independent re-run).**

```
(1) RECONSTRUCTION: all 300 games re-walked through eval.replay_walk.walk_replay with verify_tick_hashes=True -> 'walked 300 errors 0'.
(2) DEAD AIR (notable = Killed/MeetingTriggered/VentEntered/VentExited/TaskCompleted/SabotageStarted or a meeting row on that tick):
  replays/samples/9p2i    ticks 1167 | quiet  486 = 41.6%
  replays/ml_corpus/9p2i  ticks 3713 | quiet 1553 = 41.8%
  replays/samples/4p1i    ticks  551 | quiet  315 = 57.2%
  replays/ml_corpus/4p1i  ticks  529 | quiet  298 = 56.3%
  (event census over the walk: Killed 825, TaskCompleted 1904, MeetingTriggered 668, VentEntered 568, VentExited 499, SabotageStarted 29)
(3) POST-FINISH ATTRIBUTION (living actors only; finish = the TPC-th TaskCompleted for that crewmate):
  samples/9p2i    crew slots 350  finished 120 | post-finish living ticks  999  wait  370 -> post-finish wait == TOTAL crew wait: True
  ml_corpus/9p2i  crew slots 1050 finished 400 | post-finish living ticks 4106  wait 1944 -> True
  samples/4p1i    crew slots 150  finished  73 | post-finish living ticks  307  wait  152 -> True
  ml_corpus/4p1i  crew slots 150  finished  72 | post-finish living ticks  282  wait  130 -> True
  (crew slot and finished counts identical to the filing; my absolute wait totals run ~3-10% higher because I count every living-actor tick including meeting ticks -- the STRUCTURAL claim, that a crewmate never waits before finishing, holds in all four sets)
  worst consecutive post-finish wait run: (32, seed 1008, p-9) on ml_corpus/9p2i -- matches the filing exactly.
(4) BODIES -- THE REFUTED CELL. Re-walked with verify_tick_hashes=True, reading WorldState.bodies at every yielded state:
  kill events: 825
  bodies ever existing (distinct): 825 | ever discovered: 618 (74.9%) | never discovered: 207 (25.1%)
  bodies present in the FINAL state: 207 | undiscovered there: 207
  Cross-check: 618 discovered bodies == the 618 body-report meetings measured independently from MeetingTriggeredEvent(trigger='report').
(5) DECLARED OUT: tasks/phase-20.md:65-67 names 'finished-crew jobs' among the levers that are OUT; audits/audit-phase-20-planning.md:185 'The balance wave (post-meeting reset G-5; finished-crew jobs G-15; vent peek G-13; saw_kill ...)'; audits/audit-phase-20-close.md:442 carries the G-15 backlog row with the baseline-6 cells and the 36-tick exemplar.
```

**Verifier note.** The 100%-of-crew-waits attribution is a genuinely sharp new cut and reproduces cleanly. The 52.8% never-discovered headline is wrong by ~2x and is the one number a reader would quote, so it must not ship as filed. Net effect: a routed known-open item that improved, plus one bad number.

**Fix sketch.** Give finished crewmates a default occupation that produces a state change and an observation: a patrol/sweep route biased toward rooms with no recent sighting (which would also lift the 52.8% undiscovered-body rate), or a repeatable low-value 'secondary duty' task. Either turns ~4,500 corpus-wide standing-still ticks into movement the perception layer can render, and removes the `wait`-means-finished-crewmate shortcut a fitted model would otherwise learn.

## A-24 — "Accuse the reporter" is the impostor's near-monolithic deflection script (70.7% of its accusations)

**Severity:** P2 (finder: P1). **Classification:** re-report of known G-31 (whose prior ruling was 'a designed defence that holds') PLUS one new adverse cell: the ballot-time reporter-exculpation defence measurably weakened on baseline 7. **Verdict:** ADJUSTED. **Area:** reporter-justice / impostor rhetoric. **Confidence:** high.
**Merged from:** reporter-justice#4: "Accuse the reporter" is the impostor's near-monolithic deflection script (70.7% of its accusations).

**Claim.** Every measured cell reproduces exactly (618 body-report meetings; crew 1844 non-reporter turns / 1513 accusations / 540 at the reporter = 35.7%; impostor 850 / 737 / 521 = 70.7%; turn shares 29.3% and 61.3%; ballots 158/1844 = 8.6% and 120/850 = 14.1%; 28 of the 40 innocent 9p2i ejections are reporter convictions). Two corrections. (1) CLASSIFICATION: this is G-31 ('Reporter-blame is the default deflection, and it works', P1, corrob 8, audits/review-2026-08-19/A/collated-findings.md:394-402) re-measured on new bytes, and the prior cross-track ruling on it is explicit -- audits/review-2026-08-19/D/cross-track-map.md:89: 'Good news, actually: the ballot-time guard works. Worth stating as a designed defence that holds.' The designed defence is Task 15.5's reporter-exculpation cap (agents/memory/beliefs.py REPORTER_EXCULPATION_SOFT_LIFT_CAP, graduated to unconditional at 15.7). (2) THE 'DEGENERATE SCRIPT' FRAMING IS NOT A BASELINE-7 PROPERTY: like-for-like on the same samples/9p2i seeds, the impostor at-reporter accusation share is 64.2% on baseline-6 versus 65.9% on baseline-7, and crew 34.5% versus 37.1% -- the ~2x ratio is a STANDING, essentially unchanged pattern, not something the new record introduced, so 'precisely the degenerate script an impostor policy fitted to these bytes would inherit' describes a property that predates the corpus under audit. WHAT IS ACTUALLY NEW AND ADVERSE, and which A-24 holds in its evidence but does not claim: the BALLOT-side defence has degraded. On the same samples/9p2i seeds, ballots targeting the reporter went 2.2% -> 9.6% (crew) and 4.1% -> 17.1% (impostor), and reporter convictions went 2 -> 10, i.e. 10 of that set's 14 innocent ejections. Re-anchor the item on that regression, not on the speech ratio.

**As originally filed.** In body-report meetings 70.7% of every accusation an impostor makes is aimed at the body reporter -- twice the crew's 35.7% rate and aimed, by construction, at a player who is innocent with probability 1 -- which is precisely the degenerate script an impostor policy fitted to these bytes would inherit.

**Finder evidence.**

```
MEASUREMENT (all 618 body-report meetings; non-reporter turns only; roles from the '## Your role: IMPOSTOR' marker):
  CREWMATE: non-reporter turns=1844  accusations made=1513  at the reporter=540 (35.7%)  turns that accuse the reporter=540 (29.3% of their turns)
  IMPOSTOR: non-reporter turns= 850  accusations made= 737  at the reporter=521 (70.7%)  turns that accuse the reporter=521 (61.3% of their turns)
  ballots (non-reporter voters):
    CREWMATE  1844 ballots, 158 target the reporter ( 8.6%)
    IMPOSTOR   850 ballots, 120 target the reporter (14.1%)

So the impostor accuses the reporter in nearly two of every three turns it takes, and it is the target of seven in ten of its accusations. The crew is not far behind at 35.7%, which is what makes the play work.

VERBATIM (ml_corpus/9p2i seed 1135, headless-seed-1135:meeting-0 -- both impostors run the script in one meeting):
  turn 1 p-3 [IMPOSTOR]: "I was just passing through. Why is p-9 heading to STORAGE alone at tick 8?"  (deflects, then the table turns to the reporter)
  turn 3 p-1 [IMPOSTOR] accuses reporter p-2 (0.75): "Seen with p-9 in STORAGE at tick 8, then moved toward kill site"
  ballot p-1 -> p-2, ballot p-3 -> p-2 ("The room agrees on p-2's timeline; I see no reason to argue against the consensus.")
  outcome: reporter p-2 ejected; crew loses this game.
And samples/9p2i seed 24, headless-seed-24:meeting-1, turn 2, p-4 [IMPOSTOR] accusing reporter p-2 (0.75) "Moved directly into Storage where body was found" -- with the ballot annotation "[invalid primary_reason_observation_id 'obs p-4:10:4' nulled]", i.e. the citation gate caught the fabricated observation id and the ballot still landed at confidence 0.85 and still carried the meeting.

WHY IT IS A DEFECT AND NOT MERELY GOOD PLAY: deflecting onto the reporter is a legitimate and desirable Among-Us move at moderate frequency. At 70.7% it is not a strategy, it is the strategy, and its expected value is guaranteed by the substrate asymmetry in finding 2 (the accusers hold no exculpatory prior at speech time) plus the certainty in finding 3 (the reporter is never the impostor). Fitting on this corpus bakes a one-move impostor rhetoric into the optimizer and rewards it -- 28 of the 40 innocent 9p2i ejections are reporter convictions.
```

**Verifier evidence (independent re-run).**

```
(1) MEETING PARTITION from the reconstruction's MeetingTriggeredEvent details: {'report': 618, 'emergency': 50} -- 618 body-report meetings CONFIRMED.
(2) MY RECOUNT (non-reporter turns only; roles cross-checked against eval.validity.roles_by_seed, 1690/1690 agreement):
  CREWMATE: non-reporter turns=1844  accusations=1513  at the reporter=540 (35.7%)  turns that accuse the reporter=540 (29.3%)  ballots=1844 targeting the reporter=158 (8.6%)
  IMPOSTOR: non-reporter turns= 850  accusations= 737  at the reporter=521 (70.7%)  turns that accuse the reporter=521 (61.3%)  ballots= 850 targeting the reporter=120 (14.1%)
  -> every cell identical to the filing.
(3) EJECTION CENSUS: ejections by role {'IMPOSTOR': 387, 'CREWMATE': 42}; reporter ejected 30, all 30 innocent; 9p2i innocent ejections 40, of which 28 are reporter convictions -- both sub-figures CONFIRMED.
(4) LIKE-FOR-LIKE AGAINST BASELINE-6 (git rev 0c087587, samples/9p2i, same script, re-seeded roles, trigger reason from the walk):
  baseline-6 CREWMATE: turns=507 acc=362 at-reporter=125 (34.5%)  ballots=507 at-reporter=11 (2.2%)
  baseline-6 IMPOSTOR: turns=220 acc=187 at-reporter=120 (64.2%)  ballots=220 at-reporter= 9 (4.1%)
  baseline-7 CREWMATE: turns=468 acc=383 at-reporter=142 (37.1%)  ballots=468 at-reporter=45 (9.6%)
  baseline-7 IMPOSTOR: turns=205 acc=182 at-reporter=120 (65.9%)  ballots=205 at-reporter=35 (17.1%)
  reporter ejections, samples/9p2i: baseline-6 = 2 (both innocent, over 151 body-report meetings) -> baseline-7 = 10 (all innocent, over 144).
  -> speech ratio FLAT; ballot follow-through up ~4x; convictions 2 -> 10.
(5) PRIOR RECORD: audits/review-2026-08-19/A/collated-findings.md:394-402 (G-31, P1, corrob 8, '65/165 meetings have >=2 formal accusations of the reporter, though only 3 reporters were ever ejected (the reporter_exculpation block works at ballot time but not in speech)'); audits/review-2026-08-19/D/cross-track-map.md:89 (the ruling); audits/review-2026-08-19/D/FINAL-synthesis.md:82 (G-31 folded into root cause RC2).
(6) THE DEFENCE ITSELF: agents/memory/beliefs.py:178-200 (REPORTER_EXCULPATION_SOFT_LIFT_CAP, Task 15.5) and :1652-1710 (the pre_vote-only application); tasks/phase-15.md:552-636 (the contract), tasks/phase-20.md:6055 (the lever resolver deleted at graduation -- now unconditional).
```

**Verifier note.** The measurement is exact and the ratio is real, but as filed the item claims a baseline-7 pathology for a pattern that is unchanged from baseline-6 and already on the record with a 'the defence holds' ruling. The re-anchored version -- that defence no longer holds as well -- is the decision-relevant finding, and it is supportable from A-24's own numbers plus one historical re-run.

**Fix sketch.** No impostor-side change on its own -- the frequency is an optimum created by findings 2 and 3, so fix those first and re-measure. After the exculpation reaches the accusation round, re-run this same count; a healthy substrate should land the impostor's reporter-accusation share nearer the crew's, not at double it. Add this ratio (impostor accusations-at-reporter / all impostor accusations) as a standing watchability or evidence-honesty gauge so the next record catches a re-emergence.

## A-25 — The impostor can never report: P(impostor | reporter) is exactly 0, but the prompt says "almost never"

**Severity:** P3 (finder: P1). **Classification:** SPECIFIED / intended and already instrumented (agents/memory/beliefs.py doctrine + eval/funnel.py killer_self_reported tripwire + agents/tactical/impostor_policy.py FSM doctrine); re-report of a documented invariant already carried in the phase-20 close backlog under G-22. Residual: a docs-only P3.. **Verdict:** ADJUSTED. **Area:** reporter-justice / policy invariant + prompt calibration. **Confidence:** high.
**Merged from:** reporter-justice#3: The impostor can never report: P(impostor | reporter) is exactly 0, but the prompt says "almost never".

**Claim.** Every measured and code fact reproduces exactly: 0 of 618 body-report meetings had an impostor reporter; no ReportIntent exists anywhere in agents/orchestrator/engine; '"type": "report"' appears only at agents/tactical/crewmate_policy.py:740 and agents/tactical/learned/crew_forward.py:1088; agents/tactical/impostor_policy.py:52-53 states the doctrine ('after the kill the body is in the room and the impostor must not file a report'); engine/rules.py::resolve_report has no role gate; the vote_ballot.j2 line is verbatim; 30 reporters were convicted, all innocent. But the CLASSIFICATION is wrong -- this is SPECIFIED, documented, and instrumented, not a defect. agents/memory/beliefs.py:190-197 states the invariant as the load-bearing empirical justification for the reporter-exculpation rule: 'the impostor self-report rate is EXACTLY ZERO -- 0 of the 164 report meetings ... (eval.funnel killer_self_reported = 0 on both sets)'. eval/funnel.py:512-522 then states A-25's ENTIRE argument in advance, including the ML risk and the mitigation: 'a PRIOR calibrated on the measured corpus ... not a rule of the game: the engine permits a killer to report their own victim, and a future learned impostor could game the prior by self-reporting to exit every candidate set. That failure is made LOUD, not silent -- the killer_self_reported aggregate (0 on both committed sets) trips on any such meeting'. The 0-rate is also already a cell in the phase-20 close's own backlog table under G-22 ('body reports by an impostor 0/626', audits/audit-phase-20-close.md:445). Finally, the 'the prompt hedges a certainty' complaint is inverted: the hedge is the specified position precisely BECAUSE the invariant is a policy prior and not an engine rule, and A-25's own fix (b) concedes that stating it as a certainty would strengthen rather than remove the shortcut. What survives is at most a documentation item -- name the invariant explicitly in the corpus docs so a fitter's feature set can be audited against it (A-25's own third fix clause); the standing tripwire already exists.

**As originally filed.** No impostor filed a body report in any of the 618 body-report meetings, because no impostor policy can emit a report intent (the engine permits it; only the crew policies ever produce one), so "reporter implies innocent" is a deterministic leak that a model fitted to these bytes will learn as an exact rule while the ballot prose describes it as merely "weakly exculpatory".

**Finder evidence.**

```
MEASUREMENT (from the finding-1 reproducer):
  body_report_meetings   618
  reporter_is_impostor     0        -> 0/618, 0.00%

WHY IT IS EXACTLY ZERO -- it is a POLICY invariant, not an engine rule:
  $ grep -n 'ReportIntent|Report' agents/tactical/impostor_policy.py   -> 0 matches
  $ grep -rn 'ReportIntent' --include=*.py agents/ orchestrator/ engine/ | grep -v test
      (no matches)
  $ grep -rn '"type": "report"' --include=*.py agents/ orchestrator/ engine/ | grep -v test
      agents/tactical/crewmate_policy.py:740:                "type": "report",
      agents/tactical/learned/crew_forward.py:1088:  {"type": "report", "actor": actor, "payload": {"body_id": body.id}}
  agents/tactical/learned/crew_forward.py:104,118 -- "report" is a member of CrewOptionKind / CREW_OPTION_KINDS; there is no impostor counterpart.
  agents/tactical/impostor_policy.py:52-53 states the doctrine directly: "after the kill the body is in the room and the impostor must not file a report."
  engine/rules.py:191-208 `resolve_report` rejects only in-vent actors, unknown body ids, and wrong-room actors -- there is NO role gate. The engine would accept an impostor report; nothing ever offers one.

THE PROMPT'S CALIBRATION (agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:174):
  "...self-report is weakly exculpatory: the impostor almost never reports its own kill, so being first to the scene is not by itself evidence of guilt."
The generator's true base rate is 0/618. The template hedges a certainty, and the hedge is in the direction that leaves the innocent reporter convictable -- 30 of them were convicted.

WHY THIS MATTERS FOR THE RE-GROUND: any fitted crew model that reads the trigger channel gets a free, perfectly reliable innocence oracle for one player per meeting, and any fitted impostor model gets a cover play it can never use (see finding 4 for the deflection it uses instead). Neither shortcut survives contact with a substrate where the impostor can self-report.
```

**Verifier evidence (independent re-run).**

```
(1) MEASUREMENT: from my own reconstruction, MeetingTriggeredEvent details partition the 668 meetings as {'report': 618, 'emergency': 50}; joining the trigger actor to re-seeded roles gives 'body-report meetings: 618 | reporter is IMPOSTOR: 0' -- 0/618 CONFIRMED.
(2) GREPS (rerun without the failing --include globs the filing used):
  $ grep -rn 'ReportIntent' agents orchestrator engine   -> NO MATCHES
  $ grep -rn '\"type\": \"report\"' agents orchestrator engine
      agents/tactical/crewmate_policy.py:740:                "type": "report",
      agents/tactical/learned/crew_forward.py:1088:                {"type": "report", "actor": actor, "payload": {"body_id": body.id}}
  $ sed -n 48,60p agents/tactical/impostor_policy.py -> '... after the kill the body is in the room and the impostor must not file a report.'
  $ engine/rules.py resolve_report -> rejects in-vent actors, unknown body ids, wrong-room actors; NO role gate. All CONFIRMED.
(3) PROMPT LINE VERBATIM, agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2 '## Who reported the body': 'In this game self-report is weakly exculpatory: the impostor almost never reports its own kill, so being first to the scene is not by itself evidence of guilt.' CONFIRMED.
(4) EJECTIONS: reporter ejected 30, of which innocent 30 (my own count over all 300 games). CONFIRMED.
(5) THE SPECIFICATION -- agents/memory/beliefs.py:190-200 (REPORTER_EXCULPATION_SOFT_LIFT_CAP docstring): 'The empirical justification is the measured base rate: on the committed baseline-2 corpus the impostor self-report rate is EXACTLY ZERO -- 0 of the 164 report meetings (129 in 9p2i + 35 in 4p1i) had the killer as the reporter (eval.funnel killer_self_reported = 0 on both sets) ... Self-report is therefore weakly exculpatory in this game'.
(6) THE INSTRUMENT -- eval/funnel.py:109-111 ('killer_self_reported: int  # messenger-innocent-prior tripwire (0 on baseline 2; non-zero => do not read the Stage-1 rows naively)'), :1032 (killer_self_reported=sum(1 for r in rows if r.killer == r.reporter)), and :514-522 (the passage quoted in the corrected claim, which pre-states the engine-permits-it point AND the fitted-impostor risk).
(7) ALREADY IN THE BACKLOG: audits/audit-phase-20-close.md:445 (G-22 row) -- 'body reports by an impostor 0/626, meeting triggers 0/707'.
(8) THE CHARTERED LEVER: tasks/phase-15.md:552-636 (Task 15.5 'Reporter exculpation: stop convicting the messenger'), including the DoD line requiring the measured impostor self-report rate be computed and cited in the rule's docstring; tasks/phase-20.md:6055 (resolver deleted at graduation -- the rule is now unconditional).
```

**Verifier note.** This is the weakest of the five as filed: the repo states the invariant, states that it is a policy prior rather than an engine rule, states the exact ML failure mode A-25 warns about, and ships a standing tripwire for it -- all in committed docstrings the finding does not cite. The 30 innocent reporter convictions are real and worth carrying, but they belong to the re-anchored A-24 (the ballot-side defence weakening), not to a claim that the invariant is a defect.

**Fix sketch.** Either (a) close the leak by giving the impostor FSM a low-rate self-report cover branch -- an impostor standing over a body it did not just kill, or one that killed and has a witness-free walk-away, files the report to buy the exculpation -- which makes the ballot line's "almost never" true; or (b) if the invariant is intended to stand, correct the ballot prose to state it as the near-certainty it is ("the impostor does not report bodies in this game") so at least the crew's decision matches the generator. Do not ship (b) alone into an ML re-ground: it strengthens the shortcut rather than removing it. Either way, expose the invariant explicitly in the corpus docs so the fitter's feature set can be audited for it.

## A-26 — The surrogate's coerced-row filter recognises 1 of the 6 audit-marker kinds, so ~142 guard-rewritten ballots ride into the fit as if the voter had authored the target

**Severity:** P2 (finder: P1). **Classification:** defect (declared-scope gap on the RANKING channel only; the DECISION-channel half is specified and correctly implemented). **Verdict:** ADJUSTED. **Area:** training/surrogate/dataset.py, training/surrogate/ballots.py; also meetings/manager.py + meetings/voting.py audit markers -> ballots[].rationale_text. **Confidence:** high.
**Merged from:** ballots-vs-speech#2: The surrogate fit's coerced-row filter covers 8 of the 150 guard-rewritten ballots, contradicting its own designer ruling, dialect-leaks#4: 204 engine audit markers ride the spoken ballot surface in 94 of 300 games; only 1 of the 6 marker kinds gates a training-row drop.

**Claim.** The surrogate's coerced-row filter recognises 1 of the 6 audit-marker kinds. This is a DECLARED scope decision, not a contradiction of its own designer ruling: the committed surrogate report states the exclusion list and its rationale explicitly. What survives is a NARROWER, genuinely undeclared gap: the designer ruling and the report both reason about the SKIP DECISION label ('only the J2 coercion marker records a vote the voter never chose as a skip'), and neither covers the 120 under-gate redirects, which rewrite the TARGET and therefore feed the RANKING channel (top-1/top-2) with targets the voter never authored. 142 of 3602 rows (3.94%) carry a guard-written target into a future fit; no committed artifact consumes them today (the committed surrogate + report are BASELINE 6, dated 2026-07-21; the baseline-7 re-ground is pending), and 17.10 keeps the surrogate diagnostic-only. The 204-marker census half is a baseline-7 re-quantification of known G-25.

**As originally filed.** MERGE NOTE: merged from 2 finders (ballots-vs-speech, dialect-leaks) reporting the same defect: training/surrogate/dataset.py::_ballot_is_coerced_skip matches only UNCITED_ZERO_FLAG_EJECT_MARKER -- 1 of the 6 audit-marker kinds present in the committed bytes -- so the rest ride into the fit as if the recorded target were the voter's choice. SEVERITY DISAGREEMENT: ballots-vs-speech P1, dialect-leaks P2 -- highest kept (P1). CLASSIFICATION DISAGREEMENT: ballots-vs-speech classified 'defect'; dialect-leaks classified 'intended-mechanic' because its headline subject is the MARKER DESIGN, which it correctly establishes is deliberate, self-declaring, and properly stripped on both the display side (api.replay_loader._parse_rewrite_reasons) and the eval side (eval/vj_instruments.py:659). 'defect' kept -- both finders name the fit-side gap as the actionable problem and dialect-leaks explicitly flags it as 'the adjacent gap ... worth a look before the re-ground'. The two independent marker censuses agree exactly (120 redirect / 27 invalid-obs-id / 18 teammate-coerced / 18 rationale-redacted / 9 invalid-reason-id / 8 uncited-zero-flag / 4 invalid-target). ballots-vs-speech uniquely supplies the designer-ruling contradiction (the docstring's own objection applies verbatim to the other five kinds) and the api/replay_loader.py:253-261 _TARGET_REWRITE_LABELS precedent showing the repo already has the canonical five-member name for the class; dialect-leaks uniquely supplies the 94-of-300-games spread, the 33 stacked-marker cases, and the latent `.match()` anchoring edge (a stacked ordering would evade the predicate; no such ordering occurs on these bytes).

[claim as filed by ballots-vs-speech] training/surrogate drops only the J2 citation-gate coerced SKIP (8 ballots in baseline 7) on the stated ground that "a fit that read it as a skip label would learn the decision channel from a choice the voter never made", yet the same objection applies verbatim to the 120 graph-redirected + 18 teammate-coerced + 4 invalid-target ballots, which ride into the fit as if the guard's target were the voter's choice.

[claim as filed by dialect-leaks] Engine-authored bracketed annotations are prepended to the player-facing ballot rationale in 94 of 300 committed games -- a documented and display-stripped design choice, not a model leak -- but the fit-side filter recognises only one of the six marker kinds, so the other five ride into the re-ground as if they were player speech.

**Finder evidence.**

```
==============================================================================
EVIDENCE AS FILED BY FINDER: ballots-vs-speech
(its severity P1, classification defect, confidence high)
title: The surrogate fit's coerced-row filter covers 8 of the 150 guard-rewritten ballots, contradicting its own designer ruling
==============================================================================

CODE:
  training/surrogate/dataset.py:185-199  def _ballot_is_coerced_skip(ballot) -> bool  — matches ONLY UNCITED_ZERO_FLAG_EJECT_MARKER (imported at :133), docstring: "Such a ballot records target=\"SKIP\" but was a FORCED eject, not a chosen skip (designer ruling, tasks/phase-17.md), so a fit that read it as a skip label would learn the decision channel from a choice the voter never made."
  training/surrogate/ballots.py:822-831  the fit filters on `if not row.ballot_coerced_skip` and nothing else.
  grep -rn "BALLOT_TARGET_REDIRECT_MARKER|TEAMMATE_VOTE_TARGET_MARKER|INVALID_VOTE_TARGET_MARKER" training/   ->  no hits (only UNCITED_ZERO_FLAG_EJECT_MARKER appears, at dataset.py:57,133,179,181,189).

The repo already has the canonical name for the full class and it has FIVE members, not one:
  api/replay_loader.py:253-261  _TARGET_REWRITE_LABELS = {"parse_default", "invalid_target", "teammate_coerced", "under_gate_redirect", "uncited_coerced"}
  api/replay_loader.py:244-249  "...the labels under which a recorded ballot's TARGET is not the voter's authored choice ... so the finale recap must not present it as evidence of what the voter believed".
So the display layer and the eval layer both handle all five (eval/deduction_metrics.py:1271-1298 publishes guard_rewritten_ballots_unwound = 34/85/1/2); the TRAINING layer handles one.

COUNTS on the committed bytes (same repro.py run as F1):
  guard census over 3602 ballots: graph_redirect 120, teammate_coerced 18, uncited_coerced 8, invalid_target 4  (parse_default: 0)
  -> 142 of 3602 rows (3.94%) enter the fit carrying a target/label the voter never authored; per set: samples/9p2i 44 of 45 rewritten, ml_corpus/9p2i 95 of 102, samples/4p1i 1, ml_corpus/4p1i 2.
  37 of those 142 name a player who was never formally accused anywhere in that meeting (see the never-accused finding), so the fit sees a vote with no antecedent in the transcript it is conditioned on.

==============================================================================
EVIDENCE AS FILED BY FINDER: dialect-leaks
(its severity P2, classification intended-mechanic, confidence high)
title: 204 engine audit markers ride the spoken ballot surface in 94 of 300 games; only 1 of the 6 marker kinds gates a training-row drop
==============================================================================

INVENTORY (regex \[[^\]]{5,200}\] over all 11,727 utterances):
  bracketed-annotation occurrences: 204
  by surface: ballot_rationale 204  (free_text 0, claim_reason 0 -- the model's own speech is clean)
  by set    : ml_corpus/9p2i 141, samples/9p2i 60, ml_corpus/4p1i 2, samples/4p1i 1
  distinct games: 94  (of 300)

  by kind:
    120  [under-gate eject target 'X' redirected]
     27  [invalid primary_reason_observation_id 'X' nulled]
     18  [teammate target 'X' coerced to SKIP]
     18  [rationale redacted by the vote guard; recorded reason: no confident read this round]
      9  [invalid primary_reason_id 'X' nulled]
      8  [uncited zero-flag eject target 'X' coerced to SKIP]
      4  [invalid target 'X' normalized to SKIP]

  171 are leading; the 33 non-leading are all a second marker stacked behind a first, e.g.
  samples/9p2i seed 19 meeting-2 p-9:
    "[under-gate eject target 'p-7' redirected] [invalid primary_reason_observation_id 'obs p-9:10:5' nulled] 1. p-7 claims East Hall at tick 9, ..."

THIS IS INTENDED AND DOCUMENTED, and I am reporting it as such, not as a leak. Sources pinned:
  meetings/manager.py:275  BALLOT_TARGET_REDIRECT_MARKER = "[under-gate eject target {target!r} redirected] "
  meetings/manager.py:212  TEAMMATE_VOTE_TARGET_MARKER   = "[teammate target {target!r} coerced to SKIP] "
  meetings/manager.py:355  UNCITED_ZERO_FLAG_EJECT_MARKER = "[uncited zero-flag eject target {target!r} coerced to SKIP] "
  meetings/voting.py:93    INVALID_VOTE_TARGET_MARKER
and manager.py:220 states the display contract explicitly: "the coerced ballot rides ``rationale_text``
straight onto the spectator surface, where the marker is stripped to a chip and the remainder renders
as the voter's stated reason." The display strip (api.replay_loader._parse_rewrite_reasons) and the
eval strip (eval/vj_instruments.py:659) both exist and both work.

THE ADJACENT GAP -- worth a look before the re-ground, and outside my own lane so flagged rather than
claimed: the fit-side filter recognises exactly one marker.
  $ sed -n '185,200p' training/surrogate/dataset.py
  def _ballot_is_coerced_skip(ballot: VoteBallot) -> bool:
      """... True iff the ballot's ``rationale_text`` opens with the
      :data:`meetings.manager.UNCITED_ZERO_FLAG_EJECT_MARKER` audit marker ..."""
      return _UNCITED_ZERO_FLAG_MARKER_PATTERN.match(ballot.rationale_text) is not None

That is 8 of the 204 annotations. The other 196 -- notably the 120 `under-gate ... redirected` and the
18 `teammate target ... coerced to SKIP`, both of which are also cases where the RECORDED target is
not the target the model chose -- carry no fit-side predicate here. Whether each of those five kinds
*should* drop or re-label a training row is a modelling call I am not making; what is checkable is
that only one of six is currently distinguishable to the surrogate dataset builder.

A second, smaller edge on the same predicate: `.match()` anchors at position 0, so a stacked
`[under-gate ...] [uncited zero-flag ...]` ordering would evade it. I checked and no such ordering
occurs on the committed bytes -- all 8 uncited-zero-flag markers are leading -- so this is latent,
not live.
```

**Verifier evidence (independent re-run).**

```
CODE RE-READ. training/surrogate/dataset.py:177-199 — `_UNCITED_ZERO_FLAG_MARKER_PATTERN` built from the imported `UNCITED_ZERO_FLAG_EJECT_MARKER` (import at :133), `_ballot_is_coerced_skip` returns `.match(...) is not None`. `grep -rn 'BALLOT_TARGET_REDIRECT_MARKER|TEAMMATE_VOTE_TARGET_MARKER|INVALID_VOTE_TARGET_MARKER' training/` -> 0 hits; only UNCITED_ZERO_FLAG_EJECT_MARKER appears (dataset.py:57,133,179,181,189). Fit-side filter: training/surrogate/ballots.py:831 `if not row.ballot_coerced_skip` and :946 the same, nothing else. api/replay_loader.py:253-261 `_TARGET_REWRITE_LABELS` = the five-member frozenset, with :244-252 stating the display contract; eval/deduction_metrics.py:1271-1298 publishes `guard_rewritten_ballots_unwound`. So display + eval handle five, training handles one — CONFIRMED.

MARKER CENSUS re-run independently over all four committed sets (python over replays/*/replay-seed-*.jsonl, anchored leading-bracket-chain regex): total ballots 3602; markers 204 in 94 distinct games, by kind 120 under-gate-redirect / 27 invalid-obs-id / 18 teammate-coerced / 18 rationale-redacted / 9 invalid-reason-id / 8 uncited-zero-flag / 4 invalid-target. Non-leading (stacked) marker occurrences 33. All 8 uncited-zero-flag markers at position index 0 (so the `.match()` anchoring edge is latent, not live). Target-rewriting ballots per set 45 / 102 / 1 / 2 = 150; uncited per set 1 / 7 / 0 / 0 = 8 -> 44 / 95 / 1 / 2 = 142 ride into the fit. EVERY number in the finding reproduces EXACTLY.

Marker-surface census: 171 ballots carry a leading marker; free_text 0, claim_reason 0 (turn markers were moved to structured annotations by Task 20.28, which closed G-25's turn half) — the finding's 'the model's own speech is clean' reproduces.

THE DECLARATION THAT CHANGES THE VERDICT. training/reports/report-ballot-surrogate.md:207-222, item 3: '**Coerced-SKIP rows are excluded from the fit and counted.** ... (The other rationale markers on the corpus are *not* in the exclusion: teammate-coerced SKIPs — the §7.12 by-design skip the runner mirrors by candidate exclusion — under-gate redirects, and parse-defaults; only the J2 coercion marker records a vote the voter never chose as a skip.)' The exclusion set was enumerated and reasoned about, kind by kind, in a committed report. tasks/phase-17.md:76-80 states the ruling with the same scope: 'a J2-coerced ballot records target="SKIP" but was a forced eject, not a chosen skip — poison for the DECISION channel the verdict hinges on'; :571-573 repeats it as load-bearing validation (1).

STALENESS. training/reports/report-ballot-surrogate.md:20-31 — corpus `replays/ml_corpus/9p2i` re-recorded at **baseline 6**, date 2026-07-21, committed artifact sha 611771a4...; the 1-of-2726 coerced count quoted there is a baseline-6 number. Nothing at HEAD fits on the 142 baseline-7 rows.
```

**Verifier note.** Evidence reproduces to the digit (204 markers, the 7-way kind split, 94 games, 150/142/8, 33 stacked, all-leading). Three corrections. (1) 'contradicting its own designer ruling' is REFUTED — report-ballot-surrogate.md:218-222 enumerates the excluded kinds with a per-kind rationale, so this is a declared scope, not an oversight; the ruling in tasks/phase-17.md:76-80 is explicitly scoped to the SKIP DECISION label, and teammate-coerced/invalid-target SKIPs are answered by 'the runner mirrors it by candidate exclusion'. (2) What the declaration does NOT cover is the 120 under-gate redirects: they leave the decision label EJECT and rewrite only the target, i.e. they poison the RANKING channel, which the stated rationale never reaches. That is the real, actionable residue and it is worth acting on before the pending re-ground. (3) P1 -> P2: 3.94% of rows, ranking-channel-only, a diagnostic-only artifact (17.10), and the committed fit is baseline-6 so no shipped number is currently wrong. dialect-leaks' 'intended-mechanic' classification was right about the marker DESIGN and wrong to imply the fit-side gap is intended; ballots-vs-speech's 'defect' is right about the gap and wrong about the ruling contradiction. The merge kept both errors. The 204-marker inventory half is a baseline-7 re-quantification of known G-25 (P1, turn half closed at 20.28).

**Fix sketch.** [fix as filed by ballots-vs-speech] Import the whole _TARGET_REWRITE_LABELS class into training/surrogate/dataset.py rather than the single J2 literal: set a per-row `ballot_target_rewritten` flag beside `ballot_coerced_skip`, and give the fit an explicit, tested choice per label — either drop the row (matching the 17.10 ruling) or relabel it with the AUTHORED target. Add a regression test pinning the four counts (120/18/8/4) on samples/9p2i so a future re-record cannot silently change what the fit consumes.

[fix as filed by dialect-leaks] No change to the marker design -- it is deliberate, self-declaring and correctly stripped on both the display and eval sides. Before the re-ground, add a fit-side predicate per marker kind in training/surrogate/dataset.py (a small table keyed on the six pinned literals rather than one hand-written pattern), decide per kind whether the row drops or re-labels, and count each kind in the dataset report the way `_ballot_is_coerced_skip` rows are already dropped-and-counted. Anchor the predicates on a scan of the whole leading marker chain rather than a single `.match()`, so a stacked ordering cannot evade them later.

## A-27 — The weak-signal flag channel carries no information yet is the only flag that ever convicts an innocent

**Severity:** P3 (finder: P2). **Classification:** intended-mechanic (already-ratified design decision; residual is agent behaviour, not detector emission). **Verdict:** ADJUSTED. **Area:** evidence-economy / flag-channel quality. **Confidence:** high.
**Merged from:** evidence-economy#6: The weak-signal flag channel carries no information yet is the only flag that ever convicts an innocent.

**Claim.** The alibi-class flags name a crewmate 136 times and an impostor 37 (21.4%), statistically indistinguishable from the ~26% living-impostor base rate, and all 5 flag-backed innocent convictions in the corpus ride this channel while the vent channel supplies 0 of them and all 326 flag-backed impostor ejections. All of that reproduces. But this is a baseline-7 re-quantification of known finding G-2 (P0, corrob 9), already acted on in Phase 20 by tasks 20.26 (#378) and 20.27 (#379); the low discrimination is a SPECIFIED property of a channel the substrate deliberately weak-bands rather than suppresses. The fix sketch proposes the intervention Task 20.27 already shipped, in the one form 20.27 explicitly rejected.

**As originally filed.** The non-vent flag kinds (alibi_conflict, alibi_vs_sighting, alibi_vs_physical) name a crewmate 136 times and an impostor 37 times -- 21.4% impostor, indistinguishable from the ~25% living-impostor base rate -- so they discriminate nothing, and yet all 5 flag-backed innocent convictions in the corpus come from this channel while the vent channel supplies 0.

**Finder evidence.**

```
COMMAND (flag-subject role census across all 668 meetings):

  uv run python - <<'PY'
  import json, collections
  SETS={"S9":"replays/samples/9p2i","C9":"replays/ml_corpus/9p2i","S4":"replays/samples/4p1i","C4":"replays/ml_corpus/4p1i"}
  c=collections.Counter()
  for tag,d in SETS.items():
      r=json.load(open(f"{d}/tournament-eval-report.json"))
      for g in r["report"]["games"]:
          roles=g["roles"]
          for m in g["meetings"]:
              for x in m["contradictions"]:
                  bucket = "vent" if x["kind"]=="vent_sighting" else "weak"
                  for s in x["subjects"]: c[bucket+"_subject_"+roles[s]]+=1
                  c["kind_"+x["kind"]]+=1
  print(dict(c))
  PY

OUTPUT:
  kind_vent_sighting 448, kind_alibi_vs_sighting 100, kind_alibi_conflict 60, kind_alibi_vs_physical 13
  vent_subject_IMPOSTOR 448   (vent_subject_CREWMATE never incremented -> 0)
  weak_subject_CREWMATE 136,  weak_subject_IMPOSTOR 37     -> 37/173 = 21.4% impostor

The chance baseline for 'a living player picked at random is an impostor' on the ejecting meetings in this corpus is 24.8% (sum of impostors_alive/voters_alive over the no-vent ejections, 25.6/103). 21.4% is at or below it: the weak channel is not merely weak, it is non-informative.

THE 5 FLAG-BACKED INNOCENT CONVICTIONS (from the per-ejection channel table in finding 2):
  S9 seed 2   meeting-0 p-5  alibi_conflict + alibi_vs_sighting
  S9 seed 44  meeting-1 p-9  alibi_vs_sighting
  S9 seed 46  meeting-3 p-1  alibi_vs_sighting
  C9 seed 1044 meeting-0 p-7 alibi_conflict + alibi_vs_sighting
  C9 seed 1085 meeting-0 p-1 alibi_conflict + alibi_vs_sighting

EVERY ONE OF THE FIVE IS A ONE-TICK BOUNDARY ARTIFACT, and the flag text says so itself:
  S9 seed 2:    "Alibis place p-5 in ENGINEERING (ticks 2-7) and in REACTOR (ticks 7-7); intervals overlap. [weak signal: self-stated alibi pair; narrow alibi window; ...]"
  S9 seed 44:   "Alibi places p-9 in CAFETERIA (ticks 18-18); sighting reports p-9 in EAST_HALL at tick 18. [weak signal: narrow alibi window; endpoint-tick sighting; ...]"
  S9 seed 46:   "Alibi places p-1 in ENGINEERING (ticks 30-30); sighting reports p-1 in EAST_HALL at tick 30. [weak signal: narrow alibi window; endpoint-tick sighting...]"
  C9 seed 1044: "Alibi places p-7 in LABS (ticks 3-8); sighting reports p-7 in MEDBAY at tick 8. [weak signal: endpoint-tick sighting; adjacent room one tick away]"
  C9 seed 1085: "Alibi places p-1 in MEDBAY (ticks 12-13); sighting reports p-1 in WEST_HALL at tick 13. [weak signal: narrow alibi window; endpoint-tick sighting; adj...]"
  ENGINEERING/REACTOR, CAFETERIA/EAST_HALL, LABS/MEDBAY, MEDBAY/WEST_HALL are all declared one-tick doorways in engine/maps/canonical_1.yaml -- i.e. every one of these 'conflicts' is a player standing on a room boundary at the endpoint tick of their own stated interval. Three of the five were then converted by the gate redirect (finding 5), which redirects to 'the argmax-rendered eligible candidate' and therefore hands the ballot to whoever this non-informative channel happened to stamp.

Corroborating instrument fold, replays/samples/9p2i/tournament-eval-report.json: deduction.weak_flag_conviction = {flag_named_ejections 72, weak_flag_only_convictions 3, weak_flag_only_impostor 0, weak_flag_only_innocent 3}; deduction.evidence_taxonomy.weak_signal_share = 0.347.
```

**Verifier evidence (independent re-run).**

```
CENSUS re-run verbatim over the four tournament-eval-report.json files: kind_vent_sighting 448, kind_alibi_vs_sighting 100, kind_alibi_conflict 60, kind_alibi_vs_physical 13; vent_subject_IMPOSTOR 448, vent_subject_CREWMATE 0; weak_subject_CREWMATE 136, weak_subject_IMPOSTOR 37 = 21.4%. EXACT reproduction.

BASE RATE re-derived independently (mean impostor share of the ballot-casting roster): 26.3% over all 668 meetings, 26.2% over the 84 meetings that mint a non-vent flag. Binomial check vs 26.2%: z = (0.214-0.262)/sqrt(0.262*0.738/173) = -1.44, p ~= 0.15 — 'indistinguishable from base rate' is right; 'carries no information' is a null result on n=173, not a demonstration of zero signal.

THE FIVE INNOCENT CONVICTIONS re-derived from scratch (ejected player is CREWMATE and is named by >=1 contradiction in that meeting): exactly 5, and exactly the five named — S9 s2 m0 p-5, S9 s44 m1 p-9, S9 s46 m3 p-1, C9 s1044 m0 p-7, C9 s1085 m0 p-1 — with the quoted descriptions byte-identical. Flag-backed IMPOSTOR ejections: 326, of which 318 vent_sighting-only and all 326 carry a vent_sighting. No-flag ejections: 37 CREWMATE, 61 IMPOSTOR.

WEAK/STRONG SPLIT (substring `[weak signal` on description, the repo's own predicate): alibi_conflict 60 weak / 0 STRONG; alibi_vs_sighting 100 weak / 0 STRONG; alibi_vs_physical 1 weak / **12 STRONG**; vent_sighting 448 STRONG. So (a) the substrate ALREADY bands every one of the 160 alibi-class flags weak, including all five convicting sets, and (b) `alibi_vs_physical` is NOT part of any 'weak-signal channel' — 12 of 13 are STRONG.

THE DESIGN DECISION THE FIX CONTRADICTS. meetings/transcript.py:2826-2846 — the endpoint band comment reads 'a sighting exactly on the window's edge tick is movement fuzz -- **weak-banded rather than excluded, because an endpoint mismatch can still be a real signal once corroborated**', and immediately below, `if _adjacent_within_one_tick(alibi=alibi, sighting=sighting): weak_reasons = (*weak_reasons, WEAK_REASON_ADJACENT_ONE_TICK)` — the adjacency predicate (`_adjacent_within_one_tick` at :2891-2913, `_room_hops` at :2859+, MAP_ARBITRATION_MAX_HOPS / MAX_TICK_GAP) already exists and ANNOTATES by ratified choice. tasks/phase-20.md:4270 'Task 20.27 — Map-aware flag arbitration: adjacent rooms within one tick are not a contradiction' is this finding's fix, shipped; audits/audit-phase-20-close.md:230 '20.27 (#379) ... the adjacent-room STRONG count is **148 -> 0**'.

PRIOR ART. audits/review-2026-08-19/A/collated-findings.md:33-49 G-2 ('`alibi_vs_sighting` is speech-vs-speech ... and is below chance', P0, corrob 9, '84.5% fire at an alibi *endpoint* tick; 59% of alibi windows are a single tick'); audits/review-2026-08-19/README.md:105 routes G-2 to task 20.26 / PR #378; audits/audit-phase-19-triage.md:37 item 9 is the same claim, P1, VERIFIED, routed to Phase 19 for instrumentation.

FIX-SKETCH DEFECT. meetings/transcript.py:2683-2728 `_detect_alibi_conflicts` never calls `_room_hops` or `_adjacent_within_one_tick` — it mints on disjoint canonical room sets alone. Confirmed by the bytes: the three alibi_conflict flags among the five read '[weak signal: self-stated alibi pair; narrow alibi window; endpoint-tick overlap]' with NO adjacency reason. So 'the predicate exists and only needs to gate emission instead of annotate it' is false for alibi_conflict, and gating only alibi_vs_sighting would leave an alibi_conflict flag still naming 3 of the 5 victims.
```

**Verifier note.** Every number reproduces exactly, including the five exemplars verbatim. Five corrections. (1) It is a baseline-7 re-quantification of G-2 (P0, corrob 9) and of audit-phase-19-triage item 9 — both already acted on (20.26 #378, 20.27 #379). (2) Classification defect -> intended-mechanic: Task 20.27 landed precisely this adjacency predicate and the code comment at transcript.py:2826-2833 states the deliberate choice to weak-BAND rather than exclude; the close audit records adjacent-room STRONG 148 -> 0. All five convicting flag sets are already stamped weak at the record, so the detector did what it was designed to do and the crew ejected anyway — that is a belief/agent-behaviour finding, not a mint defect. (3) Factual error: `alibi_vs_physical` is 12/13 STRONG, so folding it into 'the weak-signal channel' mis-states the census the claim is built on; conversely 0 of 160 alibi_conflict/alibi_vs_sighting flags are STRONG. (4) The fix sketch's 'zero-cost, the predicate exists' is wrong for `alibi_conflict`, which has no adjacency wiring at all. (5) 'It removes all 5 flag-backed innocent convictions' is an unestablished counterfactual — 37 innocent ejections in this corpus carry no flag whatsoever, so removing a flag removes the label, not necessarily the conviction. P2 -> P3.

**Fix sketch.** Suppress the mint rather than the display. In meetings/transcript.py's contradiction detector, do not emit alibi_conflict / alibi_vs_sighting when the two rooms are map-adjacent AND the disagreement sits on the endpoint tick of the stated interval -- the detector already computes and prints exactly these two conditions into the description ('endpoint-tick sighting', 'adjacent room one tick away'), so the predicate exists and only needs to gate emission instead of annotate it. That is a zero-cost change on these bytes: it removes all 5 flag-backed innocent convictions and 0 impostor convictions (the vent channel supplies every one of the 326 flag-backed impostor ejections). Second-order benefit: it stops the finding-5 redirect from laundering herd errors into a boundary artifact.

## A-28 — Body cleanup consumes only the reported corpse, so corpses accumulate across meetings (baseline-7 re-quantification of G-6)

**Severity:** P4 (informational re-quantification of a ruled-on design choice) (finder: P2). **Classification:** intended-mechanic. **Verdict:** ADJUSTED. **Area:** flow-edges / body cleanup after meetings. **Confidence:** high.
**Merged from:** flow-edges#4: Body cleanup consumes only the reported corpse, so corpses accumulate across meetings (baseline-7 re-quantification of G-6).

**Claim.** apply_meeting_result deletes exactly the triggering body, so other corpses persist: 331/668 meetings end with >=1 body present, 306/668 open with 2+, 235/668 open with a body predating the previous meeting, and 154/300 games end with an unreported corpse. All of that is measured correct. But it is a CONFIRMED-DESIGN-CHOICE, not a defect: the single delete carries an in-code rationale (it exists to stop an adversarial re-report loop, not to model cleanup), a surviving corpse with discovered_by=None is precisely what makes it VISIBLE and reportable, and the repo's own prior adversarial verifier already ruled this exact mechanic 'CONFIRMED-DESIGN-CHOICE -- every defect inference drawn from it is REFUTED' as G-6, with the cross-track ruling 'Do not "fix" the engine.'

**As originally filed.** apply_meeting_result deletes exactly one body -- the one whose report opened the meeting -- so every other corpse persists indefinitely: 331/668 meetings end with at least one body still on the floor, 235/668 open with a body that predates the previous meeting, and 154/300 games finish with a corpse that was never found.

**Finder evidence.**

```
PRIOR ART, STATED UP FRONT: this mechanic was already raised as G-6 ("Only the
reported corpse exists; every other body is invisible and unmentioned", P0) in
audits/review-2026-08-19/A/collated-findings.md. It is NOT in my known-open list,
and it is squarely the "body cleanup after meetings" edge I was asked to check, so
I report it as a baseline-7 re-quantification rather than as a new discovery.

CODE -- orchestrator/game.py:1313-1325, the whole of the cleanup:
    if triggering_body_id is not None and triggering_body_id in working.bodies:
        bodies = dict(working.bodies)
        del bodies[triggering_body_id]
        working = replace(working, bodies=bodies)
triggering_body_id comes from the MeetingTriggeredEvent and is None for an
emergency meeting (orchestrator/game.py:2484+ _build_meeting_trigger), so an
emergency meeting clears nothing at all. There is no other write to
WorldState.bodies outside engine/tick.py::_apply_kill.
Note engine/rules.py:191-210 resolve_report does NOT check body.discovered_by;
the single-body delete is what stops a re-report, and it only covers the trigger.

MEASUREMENT (300 games re-walked, .../scan.py and .../scan2.py)
    "bodies_survive_meeting": 331          # meetings whose post-apply state still has >=1 body
    "meeting_with_multiple_bodies": 306    # meetings that OPEN with 2+ bodies present
    "final_state_has_bodies": 154          # games ending with an undiscovered corpse
    "meeting_with_pre_prev_meeting_body": 235
    body-age-at-meeting n=1019 mean=5.43 max=51
Exemplars (set, seed, meeting tick, previous meeting tick, [(body, kill tick)]):
    ('replays/samples/9p2i', 11, 15, 13, [('body-p-4-4', 4)])   # 11 ticks old, its 3rd meeting
    ('replays/samples/9p2i', 12, 14, 13, [('body-p-6-5', 5), ('body-p-9-12', 12)])
    ('replays/samples/9p2i',  1, 12,  8, [('body-p-3-5', 5)])
The oldest corpse still present when a meeting convened was 51 ticks old.

FLOW-EDGE ANGLE beyond G-6: because the surviving corpse is still reportable, the
NEXT meeting can be opened by a body that was already lying in the room during
the previous meeting -- the group meets twice over the same death, with the second
meeting narrated as a fresh discovery. 99 report actions were additionally
dropped by the meeting-abort (previous findings), which is one of the ways a
corpse survives its own discovery attempt.
```

**Verifier evidence (independent re-run).**

```
MEASUREMENT re-run from scratch on a state-hash-verified walk (my own script; `eval.replay_walk.walk_replay` with `ReplayWalkConfig(verify_tick_hashes=True)`, `eval.validity.resolve_roster_knobs` + `seeds_on_disk`, all four sets, 300 games / 668 meetings, zero violations):
  bodies_survive_meeting = 331
  meeting_with_multiple_bodies = 306
  final_state_has_bodies = 154
  meeting_with_pre_prev_meeting_body = 235
  body age at meeting: n 1019, mean 5.43, max 51
  end reasons: CREWMATE_EJECT 198, IMPOSTOR_PARITY 79, CREWMATE_TASKS 23
Every single figure matches the finding EXACTLY.

CODE. orchestrator/game.py:1313-1325 is the whole cleanup, and its comment is the rationale the finding omits: 'The engine's visibility layer already hides bodies whose ``discovered_by`` is set, so default tactical agents cannot re-report the body via observation. But ``engine.rules.resolve_report`` does not reject already-discovered bodies, so a hardcoded / adversarial intent with the same body_id would otherwise repeatedly re-trigger meetings after gameplay resumes. Drop the body here so the trigger surface is the same as the observation surface.' orchestrator/game.py:1252-1256 documents the DESIGN.md §5.1 freeze on the same path. engine/rules.py:191-210 `resolve_report` indeed does not check `discovered_by` — that half of the claim holds.

EVIDENCE ERROR 1 (factual). 'There is no other write to WorldState.bodies outside engine/tick.py::_apply_kill' is FALSE. `grep -rn discovered_by engine/ orchestrator/ observation/` -> engine/tick.py:439, inside `_apply_report`: `bodies[action.payload.body_id] = replace(body, discovered_by=action.actor)`. Reporting a body writes to `state.bodies`. engine/visibility.py:93 then reads `if body.discovered_by is None and body.room in visible_room_set` — i.e. discovered_by=None is what makes a corpse VISIBLE, the exact inversion the prior verifier flagged.

EVIDENCE ERROR 2 (framing). 'the group meets twice over the same death, with the second meeting narrated as a fresh discovery' — the trigger body is deleted, so no body can ever trigger two meetings; the second meeting is over a DIFFERENT death while an older corpse happened to be on the floor. The finding's own exemplar family is the case the prior verdict names as correct: I re-walked samples/9p2i seed 11 from the action stream — body-p-4-4 killed t4, survives the t9 and t13 meetings (which were triggered by body-p-2-7 and body-p-1-11), then p-5 reports body-p-4-4 at t15 -> meeting-2. audits/review-2026-08-19/A/verdicts.md:120 on this same exemplar: 'The corpse persisted *so it could be found later*, and it was.'

PRIOR RULING. audits/review-2026-08-19/A/verdicts.md:111-135 — 'VERDICT: CONFIRMED-DESIGN-CHOICE -- the mechanic is real and intentional; every defect inference drawn from it is REFUTED', including '478/478 body-triggered meeting boundaries removed exactly one body; 0/47 emergency meetings removed any' and 'Zero real misses corpus-wide' (of 172 never-reported bodies only 6 were ever seen by a living crewmate, all 6 on the final tick). audits/review-2026-08-19/D/cross-track-map.md:63 — 'REFUTED as a defect ... **Do not "fix" the engine.**' audits/audit-phase-20-close.md:398 lists G-6 among the five claims 'retracted by the review's own verifier'.
```

**Verifier note.** Best-measured of the five: every figure reproduced exactly on my own hash-verified re-walk, and the emergency-meeting-clears-nothing half is correct. The verdict is ADJUSTED and not REFUTED only because the measurement is sound. What is wrong is the classification and the framing: this is the repo's most explicitly ruled-on design choice, retracted by its own adversarial verifier and listed as a retraction in the Phase-20 close ledger, with an in-code rationale the finding quotes only partially (it cites the delete and omits the comment saying WHY). The fix sketch ('clear ALL bodies at meeting end') would implement exactly what the cross-track ruling forbids and would destroy the find-it-later evidence channel the prior verifier measured as working. Two concrete evidence errors: the 'no other write to bodies' claim is false (engine/tick.py:439), and the 'meets twice over the same death' framing is impossible under the code the finding itself quotes. The finder discloses G-6 as prior art but records it as an open P0 to be re-quantified rather than as a claim already REFUTED — that disclosure is the difference between honest and complete.

**Fix sketch.** Decide the rule explicitly in DESIGN.md and implement it in apply_meeting_result: either clear ALL bodies at meeting end (the Among Us rule, and the one that matches 'a meeting is where the crew pools what they have found'), or keep them but mark every body present in the meeting room as discovered so it cannot re-trigger. Clearing all bodies is a one-line change (`working = replace(working, bodies={})`) and removes the double-jeopardy shape; the accompanying legibility half is G-6's, not this finding's.

## A-29 — Sabotage is inert on these bytes: 29 uses, one kind, zero timeouts, a meeting refunds a tick of the doomsday clock, the map's `lights` kind is unreachable, and the alarm names neither kind nor room

**Severity:** P3 (finder: P2). **Classification:** intended-mechanic (with one narrow surviving legibility gap: the sabotage kind/repair rooms never reach the rendered memory or the meeting prompt). **Verdict:** ADJUSTED. **Area:** flow-edges / sabotage state across a meeting; also sabotage / legibility (alarm content, dead `lights` kind). **Confidence:** high.
**Merged from:** legibility-pacing#6: Sabotage on these bytes: one kind, 29 uses, never expires -- and the `lights` kind is unreachable, flow-edges#5: A meeting freezes the sabotage doomsday clock for a full tick, and the sabotage win never fires.

**Claim.** The sabotage census and the meeting freeze reproduce exactly (29 reactor sabotages in 300 games, 24 repaired, none in any 4p1i game, 0 IMPOSTOR_SABOTAGE, 8 meetings open mid-sabotage and all 8 still active after apply, the clock unchanged across the meeting tick). Both are already-known/intended: the census is declared known-open G-40 and the freeze is DESIGN.md §5.1 documented at orchestrator/game.py:1252-1256. Of the three halves offered as NOT covered by that intent, one is refuted and one is overstated: `lights` is NOT unreachable dead code (the engine implements it and the ML/ES action space enumerates a SabotageIntent for every map kind; only the hand-written LLM-era ImpostorPolicy hard-codes reactor), and the crew is NOT told only 'a sabotage is happening' (the tactical crew policy receives kind + repair_rooms + is_gating via global_status and diverts to repair, which is how 24/29 got fixed; the global room=None alarm shape is itself documented). The one clean surviving gap is legibility-only: the LLM/social layer never learns the sabotage KIND or its repair rooms.

**As originally filed.** MERGE NOTE: merged from 2 finders (legibility-pacing, flow-edges) with the same mechanism and the same census: engine/tick.py:599 returns before step 2's _advance_sabotage, so every meeting tick refunds a tick of the doomsday clock; 29 sabotages in 300 games, all kind 'reactor', none in any 4p1i game, none ever reaching remaining_ticks == 0, and IMPOSTOR_SABOTAGE fires 0 times. Both P2. CLASSIFICATION DISAGREEMENT: flow-edges classified 'intended-mechanic' (the freeze is DESIGN.md 5.1 and is documented at orchestrator/game.py:1252-1256); legibility-pacing classified 'defect'. 'defect' kept, because legibility-pacing's two additional halves are NOT covered by that documented intent: the map's `lights` sabotage kind is unreachable dead code (agents/tactical/impostor_policy.py hard-codes 'reactor') while canonical_1.yaml still declares it and STORAGE still advertises its repair panel, and the crew's only signal is a content-free 'You heard a sabotage alarm.' carrying neither kind nor room (834 occurrences) against a vent audible that DOES carry a room. flow-edges uniquely supplies the exploit framing (nothing blocks convening a meeting during a critical sabotage, so the clock can be stalled) and the mirror case where a repair_sabotage action was itself eaten by the same meeting (samples/9p2i s17 t24); legibility-pacing uniquely supplies the per-game clock traces and the alarm/lights evidence.

[claim as filed by legibility-pacing] Across 300 games there are 29 sabotages, all `reactor`, none in any of the 100 4p1i games, none ever reaching remaining_ticks == 0 (IMPOSTOR_SABOTAGE is a live win condition with zero occurrences), the map's `lights` sabotage is unreachable because the policy hard-codes `reactor`, and the crew's only signal is a content-free "You heard a sabotage alarm." carrying neither kind nor room.

[claim as filed by flow-edges] The meeting-trigger tick skips engine/tick.py's _advance_sabotage and apply_meeting_result deliberately leaves the sabotage untouched, so every meeting gifts the crew exactly one free tick of the reactor countdown; across 300 games 29 reactor sabotages started, 24 were repaired, 8 meetings convened mid-sabotage, and IMPOSTOR_SABOTAGE fired 0 times.

**Finder evidence.**

```
==============================================================================
EVIDENCE AS FILED BY FINDER: legibility-pacing
(its severity P2, classification defect, confidence high)
title: Sabotage on these bytes: one kind, 29 uses, never expires -- and the `lights` kind is unreachable
==============================================================================

ALL findings fold the same reconstruction. Built once with (cwd = repo root):

  PYTHONPATH=. uv run python scratchpad/wave0/A/dump.py scratchpad/wave0/A/dump.json

dump.py re-seeds every committed seed and replays it through
`eval.replay_walk.walk_replay` under a profile with `verify_tick_hashes=True`
(so every reconstructed tick matched the recorded `state_hash`), recording per
tick: the recorded actions, the ENGINE events (`engine.events.event_to_dict`),
alive set, per-player rooms, bodies, sabotage state, task counts; plus every
meeting row verbatim (transcript turns, ballots, contradictions, llm_calls with
their full prompts) and the `game_over` row. Roles come from
`eval.validity.roles_by_seed` (re-seeding, same recipe). Reconstruction was
clean: 0 errors over 50 + 150 + 50 + 50 = 300 games (samples/9p2i 50,
ml_corpus/9p2i 150, samples/4p1i 50, ml_corpus/4p1i 50); rosters resolved to
(9,2,2) and (4,1,1).

--- census ---
  replays/samples/9p2i    games with sabotage  5/50  starts {'reactor': 5}  repaired 5
  replays/ml_corpus/9p2i  games with sabotage 17/150 starts {'reactor': 24} repaired 19
  replays/samples/4p1i    0/50   starts {}   repaired {}
  replays/ml_corpus/4p1i  0/50   starts {}   repaired {}
  => 29 SabotageStarted in 300 games (22 games = 7.3%); kind is `reactor` 29/29.

  game_over reasons (all sets): CREWMATE_EJECT 198, IMPOSTOR_PARITY 79,
  CREWMATE_TASKS 23.  IMPOSTOR_SABOTAGE: 0.

--- the clock never runs out, and a meeting refunds a tick ---
  The 5 unrepaired sabotages all ended because the GAME ended, not because the
  timer expired.  Longest-lived (ml_corpus/9p2i seed 1030, start t21, duration 6):
    t21 remaining 5 | t22 remaining 5 (meeting at t22) | t23 remaining 4 |
    t24 remaining 3 | t25 remaining 3 (meeting at t25, game ends CREWMATE_EJECT)
  Active for 5 wall ticks, burned 2 ticks of clock: engine/tick.py:599 returns
  early on the meeting interrupt, before step 2's `_advance_sabotage`, so every
  meeting tick during a sabotage is free.  Same pattern in seed 1084
  (t20 remaining 3 -> t21 remaining 3, meeting at t21).
  Minimum `remaining_ticks` observed anywhere in the corpus: 3.

--- `lights` is defined but unreachable ---
  engine/maps/canonical_1.yaml:386-392:
      sabotages:
        lights:
          affected_visibility: same_room_only
          repair_rooms: [ADMIN]
          duration_ticks: 90
          repair_ticks: 3
  agents/tactical/impostor_policy.py:218:
      _REACTOR_SABOTAGE_KIND: Final[str] = "reactor"
  ...:449:  return self._sabotage(kind=_REACTOR_SABOTAGE_KIND)
  The only visibility-altering sabotage in the game is dead code in the
  recorded substrate; `canonical_1.yaml:55-57` still declares
  `visibility_defaults.lights_sabotage: same_room_only` and STORAGE's notes
  still advertise the lights repair panel.

--- the alarm carries no content ---
  observation/service.py:379-380:
      if world_state.sabotage is not None and world_state.sabotage.active:
          events.append(AudibleEvent(kind="sabotage_alarm", room=None))
  -> renders (agents/memory/store.py:1994-1996) as
     "- [obs] [tick N] You heard a sabotage alarm."   (834 occurrences)
  against the vent audible, which DOES carry a room:
     "- [obs] [tick N] You heard a vent use in ROOM."  (1,613 occurrences)
  A crewmate is told a sabotage is happening but not what or where, four ticks
  running (samples/9p2i seed 17, p-1's meeting-3 prompt: identical alarm lines
  at ticks 24, 25, 26, 27).

NOTE: the SHORT clock and the ~zero sabotage wins are deliberate and documented
in canonical_1.yaml:401-416 ("a sabotage STALL with repair URGENCY, not a win
lever ... 0 IMPOSTOR_SABOTAGE wins"), and the clock itself is known-open G-40 --
I am quantifying it.  What is NOT covered by that note is the dead `lights`
kind, the content-free alarm, and the meeting-refund of the clock.

==============================================================================
EVIDENCE AS FILED BY FINDER: flow-edges
(its severity P2, classification intended-mechanic, confidence high)
title: A meeting freezes the sabotage doomsday clock for a full tick, and the sabotage win never fires
==============================================================================

CODE
engine/tick.py:606-621 (step 2) contains _advance_sabotage, and step 1's meeting
return at 599-600 is ahead of it, so the countdown does not tick.
orchestrator/game.py:1252-1256 states this is intended:
    "The cooldown / sabotage / emergency-uses counters are unchanged during the
     meeting tick because DESIGN.md 5.1 freezes engine state during a meeting"
and apply_meeting_result indeed advances only tick and rng (game.py:1344-1358).
Nothing anywhere blocks calling a meeting during a critical sabotage.
Map parameters (engine/world.py load_canonical_map): reactor duration_ticks=6,
repair_ticks=3, gates_tasks=True, repair rooms REACTOR/ENGINEERING.

MEASUREMENT (300 games re-walked, .../sab.py)
    {'started:reactor': 29, 'repaired:reactor': 24,
     'meeting_open_during_active_sab': 8, 'meeting_applied_sab_still_active': 8}
    end reasons over 300 games: CREWMATE_EJECT 198, IMPOSTOR_PARITY 79,
    CREWMATE_TASKS 23, IMPOSTOR_SABOTAGE 0
Per-tick trace showing the freeze (replays/samples/9p2i/replay-seed-44.jsonl):
    ('T', 18, 'MEETING', ('reactor', 6, True))
    ('MEET_OPEN', 18, ('reactor', 6))
    ('MEET_APPLIED', 19, ('reactor', 6))     <- tick advanced 18 -> 19, clock still 6
    ('T', 19, 'PLAY', ('reactor', 5, True))
    ('T', 20, 'PLAY', ('reactor', 4, True))
    ('T', 21, 'PLAY', ('reactor', 3, True))
And a double freeze in replays/ml_corpus/9p2i/replay-seed-1030.jsonl (meetings at
t22 and t25 both land inside one reactor window: 5 -> 5, then 3 -> 3).
One of the dropped-action instances is the mirror image: samples/9p2i s17 t24,
p-8's repair_sabotage {'kind':'reactor'} was eaten by the same meeting that froze
the clock.

I am quantifying a MECHANISM adjacent to known-open G-40 ("Sabotage is a walk
simulator"): G-40 records that no sabotage ever times out, but does not name the
meeting freeze as one of the reasons. The freeze itself is documented intent; the
absence of any "critical sabotage blocks meetings" rule is the gap.
```

**Verifier evidence (independent re-run).**

```
MY OWN state-hash-verified re-walk (`eval.replay_walk.walk_replay`, verify_tick_hashes=True, 300 games / 668 meetings, 0 violations):
  SabotageStarted:reactor 29, SabotageRepaired:reactor 24, no other kind ever started
  games with sabotage: samples/9p2i 5/50, ml_corpus/9p2i 17/150, both 4p1i sets 0/50
  meeting_open_during_active_sab = 8, meeting_applied_sab_still_active = 8
  end reasons: CREWMATE_EJECT 198, IMPOSTOR_PARITY 79, CREWMATE_TASKS 23, IMPOSTOR_SABOTAGE 0
  freeze traces: samples/9p2i seed 44 OPEN t18 reactor remaining 6 -> APPLIED t19 reactor remaining 6; ml_corpus/9p2i seed 1030 double freeze (t22/t23 5->5, then t25 3->3); seed 1084 t21 3->3. All three finder traces reproduce.
  ONE DISCREPANCY: minimum remaining_ticks I observe anywhere is **2**, not the finder's 3.
engine/tick.py:592-600 (step 1 loop) `if working_state.phase == "MEETING": return working_state, events` at :600, ahead of `_advance_sabotage` at :611 — the freeze mechanism is exactly as claimed.

ALARM LINE COUNTS re-derived over every recorded meeting prompt: 'You heard a sabotage alarm.' 834, 'You heard a vent use in ' 1613. EXACT reproduction. observation/service.py:379-380 emits `AudibleEvent(kind="sabotage_alarm", room=None)`; agents/memory/store.py:1988-1996 renders the room=None branch without a room; grep 'sabotage' over agents/strategic/prompts/qwen3_6_27b/*.j2 -> 0 hits.

LIGHTS — REFUTED AS 'UNREACHABLE DEAD CODE'. The engine implements it: engine/world.py:115 `lights_sabotage: VisibilityMode`, :201 `affected_visibility`, engine/visibility.py:34 returns `sabotage_definition.affected_visibility`. The ML/ES substrate reaches it: training/env.py:347-354 adds a `SabotageIntent` for EVERY kind in `sabotage_kinds`, and `sabotage_kinds = tuple(sorted(game_map.sabotages))` at training/env.py:539, training/crew/scorer.py:874, training/bakeoff/policy_es.py:442 and :558/:598 — so a learned impostor's legal action set includes `{'type':'sabotage','payload':{'kind':'lights'}}`. What is true and narrower: agents/tactical/impostor_policy.py:218 `_REACTOR_SABOTAGE_KIND = "reactor"` and :449 `return self._sabotage(kind=_REACTOR_SABOTAGE_KIND)` — the hand-written policy that produced this corpus never picks it, which is why 29/29 recorded sabotages are reactor.

ALARM — OVERSTATED. observation/packet.py:162-172 carries `sabotage_active / sabotage_kind / sabotage_repair_rooms / sabotage_is_gating` (filled at observation/service.py:566-585), and agents/tactical/crewmate_policy.py:19-25 and :516-534 read exactly those to divert to the nearest repair room, scoped to `sabotage_is_gating` (DESIGN.md §8.3, Task 11.5). 24 of 29 sabotages were repaired, which is that channel working. The room=None global shape is documented: audits/post-phase-14-ML-planning.md:336 '`audible_events`: {kind in {vent_use_heard, sabotage_alarm}, room|None} (vent is room-gated; **sabotage alarm is global**)'.

DECLARED INTENT / PRIOR ART. DESIGN.md:481 §5.1 '1. Freezes engine state (no movement, no kills, cooldowns paused).' orchestrator/game.py:1252-1256 names it. engine/maps/canonical_1.yaml:401-416 pre-declares the short clock and the ~zero-win intent ('a sabotage STALL with repair URGENCY, not a win lever ... 0 IMPOSTOR_SABOTAGE wins'). audits/review-2026-08-19/A/collated-findings.md:487-494 G-40 'Sabotage is a walk simulator (and is absent entirely from 4p1i)', P2, corrob 5, which also already records the lights-wording oddity — G-40 is on the declared known-open backlog.
```

**Verifier note.** Census, freeze traces and the 834/1613 line counts reproduce exactly on my own hash-verified walk (one small miss: minimum remaining_ticks is 2, not 3). The merge kept 'defect' over flow-edges' 'intended-mechanic' on the strength of two halves that do not hold up. `lights` is implemented in the engine and is a legal action for every ES/learned impostor (training/env.py:347-354 + :539) — it is unreachable only from the hand-written ImpostorPolicy, i.e. absent from THIS corpus, which is a very different and much smaller claim than 'dead code the map still declares'. And the crew are given the kind, the repair rooms and the gating flag through the observation packet and act on them (24/29 repaired); the content-free line is the LLM-facing render, not 'the crew's only signal'. That leaves one clean, novel, legibility-sized gap — the sabotage kind and repair rooms never reach rendered memory or any meeting prompt, so agents cannot speak about a sabotage they can walk to — plus a census that is declared G-40 and a freeze that is declared DESIGN.md §5.1. flow-edges' own routing ('that is a balance-wave decision, so route it with G-40') was the correct disposition and the merge overrode it.

**Fix sketch.** [fix as filed by legibility-pacing] Three separable fixes: (1) give the alarm its kind and its repair rooms -- `AudibleEvent(kind="sabotage_alarm", room=None)` already has `world_state.sabotage.kind` and `.affected_rooms` in hand -- so the crew can speak about the sabotage instead of inventing one; (2) either wire `lights` into the impostor policy or delete it from canonical_1.yaml and the visibility defaults, so the map stops describing a mechanic no recorded game can produce; (3) advance the sabotage timer on the meeting-interrupt path (or hold the meeting outside the clock) so a meeting stops refunding a tick.

[fix as filed by flow-edges] Keep the freeze (it is DESIGN.md 5.1) but close the exploit surface the way the source game does: refuse ReportBody / EmergencyMeeting while a gates_tasks sabotage is active (an ActionRejected in engine/rules.py resolve_report / resolve_emergency_meeting), so the doomsday clock cannot be stalled. That is a balance-wave decision, so route it with G-40 rather than into the re-ground; the correctness half (the freeze is real and is 1 tick per meeting) is now measured.

## A-30 — Impostors talk about their own whereabouts in prose while the record stays empty

**Severity:** P3 (finder: P2). **Classification:** intended-mechanic (the structured/prose split and the empty observations list are specified) with a narrow prompt-compliance gap (the 'no own whereabouts' rule has no validation-time enforcement). **Verdict:** ADJUSTED. **Area:** impostor-behavior / prosecutable-lie surface. **Confidence:** high.
**Merged from:** impostor-behavior#5: Impostors talk about their own whereabouts in prose while the record stays empty.

**Claim.** Impostor replies do assert first-person locations in free_text in breach of their own prompt rule, and those assertions are structurally unprosecutable because free_text is never read by the contradiction detector; three named exemplars are verifiably false against the engine route. All of that reproduces. But the two framing halves need correction: the empty `observations` list is PROMPT-MANDATED (accusation_round.j2 output_format: 'Keep "observations" as an empty list'), not a symptom — and it is declared known-open G-22; and 'sits outside every channel the machinery can prosecute' is the DESIGN.md §5.2 structured-item/free_text split working as specified, not a defect. The actionable residue is narrow: an unenforced prompt rule with no guard behind it. Impact is not demonstrated — all three verified-false liars were EJECTED in that same meeting on independent STRONG vent_sighting flags, and all three games ended CREWMATE_EJECT.

**As originally filed.** In 45 of 535 impostor reply turns the model breaks its own prompt rule and asserts a first-person location in free_text ('I was in Storage at tick 8'), yet the structured observations list is empty in 100% of those turns, so the claim is rendered to the table but sits outside every channel the contradiction machinery can prosecute — and at least 3 of the 16 strictly verifiable ones are false.

**Finder evidence.**

```
PROMPT RULE BEING BROKEN: agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:218 'a bystander who was elsewhere has nothing to explain, so explain nothing about your own whereabouts - every location, room, and timing detail you mention must be about OTHER players'; :239 'Keep "observations" as an empty list'.

MEASUREMENT: over all impostor meeting llm_calls whose prompt contains <accusation_against_you> (n=535, i.e. every impostor reply), parse the engine's own route line from the prompt ('Your route (t = tick): ...'), then regex the model's response free_text for an explicit positive self-placement: /I (was|am|had been|stayed|remained)... (in|inside|at|within) (the )?<ROOM>/.
  OUTPUT: {'calls': 535, 'claims': 45, 'turns': 45, 'anchored_to_a_tick_in_the_same_clause': 16, 'contradicted_by_route': 3}
  A looser first-person scan (any first-person clause naming a room) fires on 142/535 = 26.5% of impostor replies; 177/535 = 33.1% when the whole sentence is scanned.
  Structured side of the same 45 turns: observations == [] in 45/45 (they are a subset of the 535/535 in finding 1).

THE THREE VERIFIED FALSE ONES:
  [ml_corpus/9p2i] headless-seed-1072:meeting-0 p-2 claims ENGINEERING @ ticks 6-7
     engine route: CAFETERIA t0 -> EAST_HALL t1 -> ENGINEERING t2-4 -> STORAGE t5-6 -> a vent in STORAGE t7
     said: '1. I was in Engineering until tick 6, so I could not have vented in Storage at tick 7. ...'
  [ml_corpus/9p2i] headless-seed-1084:meeting-1 p-6 claims REACTOR @ tick 21
     engine route: ... ENGINEERING t20 -> a vent in ENGINEERING t21
     said: "1. p-1's claim is impossible because I was in REACTOR at tick 21, not ENGINEERING. ..."
  [ml_corpus/9p2i] headless-seed-1101:meeting-0 p-4 claims STORAGE @ tick 8
     engine route: ... a vent in STORAGE t7 -> ENGINEERING t8 -> EAST_HALL t9 -> ADMIN t10
     said: '1. I was in Storage at tick 8, so I could not have vented in Engineering; p-1 is misremembering or lying. ...'
  All three are alibi lies engineered to defeat a vent accusation, and all three are unprosecutable: meetings/transcript.py:183-200 indexes a lie only when it arrives as a structured `whereabouts` observation ('a spoken WhereaboutsClaim indexes as a DEGENERATE SINGLE-TICK SELF-ALIBI') or an AlibiClaim; a prose-only assertion enters no index and mints no flag.

CONTRAST that shows the channel works when it is fed: impostor STRUCTURED self-alibi claims (opt_in turns) are false 38/148 = 25.7% of the time, and 21/38 of those meetings do carry a contradiction flag naming the liar (14/38 an alibi-class flag). The prose channel gets none of that scrutiny.
```

**Verifier evidence (independent re-run).**

```
PROMPT RULE — CONFIRMED verbatim. agents/strategic/prompts/qwen3_6_27b/accusation_round.j2, impostor reply branch: 'Keep your cover consistent: a bystander who was elsewhere has nothing to explain, so explain nothing about your own whereabouts — every location, room, and timing detail you mention must be about OTHER players.' And in output_format under `{% if is_impostor and turn_kind == "reply" %}`: '"observations": []' with 'Keep "observations" as an empty list and "claims" as exactly that one accusation'.

POPULATION — CONFIRMED. Over all four sets: impostor meeting llm_calls 1856, of which **535** carry `<accusation_against_you>`. Exact match.

SELF-PLACEMENT SCAN — reproduces directionally, not to the digit. My regex (`I (was|am|had been|stayed|remained|have been) ... (in|inside|at|within) (the )?<ROOM>` over the 10 canonical rooms, case-insensitive, clause-bounded) fires on **74** of 535, not 45 — the finder's regex is not fully specified, so I cannot land on their exact number. The load-bearing part holds absolutely: `observations == []` in **74/74** of my matches (0 non-empty, 0 missing). My looser first-person-clause scan fires on 241/535 (45.0%) vs their 142/535.

THE THREE FALSE EXEMPLARS — CONFIRMED byte-for-byte, prompts + routes + responses pulled independently:
  ml_corpus/9p2i headless-seed-1072 meeting-0 p-2 (IMPOSTOR). Route: 'CAFETERIA t0 -> EAST_HALL t1 -> ENGINEERING t2-4 -> STORAGE t5-6 -> a vent in STORAGE t7'. Said: '1. I was in Engineering until tick 6, so I could not have vented in Storage at tick 7.' observations []. FALSE (STORAGE t5-6).
  headless-seed-1084 meeting-1 p-6 (IMPOSTOR). Route ends '... ENGINEERING t20 -> a vent in ENGINEERING t21'. Said: 'I was in REACTOR at tick 21, not ENGINEERING.' observations []. FALSE.
  headless-seed-1101 meeting-0 p-4 (IMPOSTOR). Route: '... a vent in STORAGE t7 -> ENGINEERING t8 -> EAST_HALL t9 -> ADMIN t10'. Said: 'I was in Storage at tick 8'. observations []. FALSE.

UNPROSECUTABILITY — CONFIRMED. `grep -n free_text meetings/transcript.py` -> only :2139-2148 `_normalize_rationale` and :2172, the rationale-echo path. No detector reads it. meetings/transcript.py:183-200 states the whereabouts channel exactly as quoted ('indexed by :func:`_iter_alibis` as a degenerate single-tick self-alibi').

IMPACT — NOT DEMONSTRATED. I pulled the outcome of all three exemplar meetings from the eval reports:
  seed 1072 m0: EJECTED p-2 (IMPOSTOR); flags include vent_sighting on p-2; game -> CREWMATES / CREWMATE_EJECT.
  seed 1084 m1: EJECTED p-6 (IMPOSTOR); 3x vent_sighting on p-6; game -> CREWMATES / CREWMATE_EJECT.
  seed 1101 m0: EJECTED p-4 (IMPOSTOR); 2x vent_sighting on p-4; game -> CREWMATES / CREWMATE_EJECT.
Every one of the three prose lies was told by a player the meeting ejected anyway, on an independent STRONG flag, in a game the crew won.

PRIOR ART / SPECIFICATION. audits/review-2026-08-19/A/collated-findings.md:294-306 G-22 'Two mechanical role tells: the roll-call and the report' — 'The impostor persona instructs "explain nothing about your own whereabouts", so half of all impostor turns arrive with an empty `observations` array', P1, corrob 6. G-22 is on the declared known-open backlog. DESIGN.md:493 and :555-565 fix the turn schema and show free_text as prose alongside the structured items. The fix sketch's lever is real: `impostor_roll_call` is the one pre-Phase-20 toggleable lever (orchestrator/replay.py `_TOGGLEABLE_LEVER_RESOLVERS`), recorded OFF for this corpus (tasks/phase-20.md:5743, :5889).
```

**Verifier note.** The novel core survives: the impostor prompt forbids first-person whereabouts in free_text, the model breaks it on a non-trivial slice of replies, no guard enforces the rule the way the teammate firewall enforces its own, and the three named exemplars are verifiably false against the engine route and structurally unprosecutable. Four corrections. (1) The scan does not reproduce numerically — my clause-bounded regex gives 74/535, not 45/535 (the finder's pattern is under-specified); the 100%-empty-observations result is exact on my population. (2) The empty observations list is prompt-mandated by the template the finding itself cites, and that half is declared known-open G-22 — presenting 'the structured observations list is empty in 100% of those turns' as an aggravating fact reads as a defect when it is the specified output shape. (3) 'sits outside every channel the machinery can prosecute' is DESIGN.md §5.2's structured-vs-prose split, not a gap: making prose probative would be a substrate change, not a fix. (4) The severity rests on impact the exemplars refute — all three liars were ejected in that same meeting on independent STRONG vent_sighting flags and all three games ended CREWMATE_EJECT, so on these bytes the unprosecuted prose lie cost the crew nothing. P2 -> P3.

**Fix sketch.** Cheapest correct fix rides finding 1: with impostor_roll_call ON the reply carries exactly one structured whereabouts item, so the assertion the model wants to make anyway becomes prosecutable instead of free. Independently, a validation-time check could reject (or force into `observations`) an impostor reply whose free_text names a first-person room, the same way the teammate firewall rewrites teammate targets - the prompt already forbids it, so the rule is just unenforced.

## A-31 — Every witnessed vent is minted twice, and the teammate firewall leaks through the audible copy

**Severity:** P2. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** legibility / memory render. **Confidence:** high.
**Merged from:** legibility-pacing#8: Every witnessed vent is minted twice, and the teammate firewall leaks through the audible copy.

**Claim.** All 1,505 witness-side vent memories carry BOTH a `You witnessed P vent in ROOM.` row and a separate `You heard a vent use in ROOM.` row at the same tick with a distinct observation id, there is no audible vent channel for non-witnesses at all, and the 27 heard-without-witnessed rows in the corpus are 27/27 impostors whose teammate-firewall suppression left the audible derivative behind.

**Finder evidence.**

```
ALL findings fold the same reconstruction. Built once with (cwd = repo root):

  PYTHONPATH=. uv run python scratchpad/wave0/A/dump.py scratchpad/wave0/A/dump.json

dump.py re-seeds every committed seed and replays it through
`eval.replay_walk.walk_replay` under a profile with `verify_tick_hashes=True`
(so every reconstructed tick matched the recorded `state_hash`), recording per
tick: the recorded actions, the ENGINE events (`engine.events.event_to_dict`),
alive set, per-player rooms, bodies, sabotage state, task counts; plus every
meeting row verbatim (transcript turns, ballots, contradictions, llm_calls with
their full prompts) and the `game_over` row. Roles come from
`eval.validity.roles_by_seed` (re-seeding, same recipe). Reconstruction was
clean: 0 errors over 50 + 150 + 50 + 50 = 300 games (samples/9p2i 50,
ml_corpus/9p2i 150, samples/4p1i 50, ml_corpus/4p1i 50); rosters resolved to
(9,2,2) and (4,1,1).

  # per recorded meeting prompt, extract (tick,room) from each vent memory row
    prompts containing any vent memory line: 1531
    same (tick,room) rendered BOTH "witnessed" and "heard": 1505
    witnessed-only (tick,room): 0
    heard-only: 108 rows -> 27 distinct (set, seed, agent, tick, room)

  Anchor -- samples/9p2i seed 0, p-5's meeting-0 prompt:
    - [obs p-5:8:1] [tick 8] You witnessed p-6 vent in ENGINEERING.
    - [obs p-5:8:2] [tick 8] You heard a vent use in ENGINEERING.
  The engine emitted exactly ONE event: row t7 VentExited actor p-6,
  destination ENGINEERING, destination_witnesses ['p-5'].

  Anchor -- samples/9p2i seed 17, p-1's meeting-3 prompt:
    - [obs p-1:6:1] [tick 6] You witnessed p-2 vent in ENGINEERING.
    - [obs p-1:6:3] [tick 6] You heard a vent use in ENGINEERING.
  Engine: one VentEntered by p-2 at row t5, witnesses ['p-1'].

Why there is no non-witness audible channel (observation/service.py:359-377):

    vent_rooms = tuple(sorted({
        observed_action.audible_room
        for observed_action in observed_actions.values()
        if observed_action.action == "vent" and observed_action.audible_room is not None
    }))

`observed_actions` only ever contains a vent for an agent already in the
event's witness set (`_vent_observation_for_agent`, observation/service.py:526-543,
returns None otherwise, and sets `audible_room` from the witnessed room). So
the "sound" is derived from the sight: witnesses hear it twice, everyone else
hears nothing.

The 27 heard-only rows, by role:
    {'IMPOSTOR': 27}   (crewmates: 0)
  e.g. samples/9p2i seed 32 p-5 (IMPOSTOR) tick 9 ENGINEERING;
       samples/9p2i seed 46 p-8 (IMPOSTOR) ticks 8 and 9 ENGINEERING;
       ml_corpus/9p2i seed 1026 p-9 (IMPOSTOR) tick 9 ADMIN.
  `_sighting_is_suppressed` (agents/memory/store.py:1800-1810) drops the
  teammate's `You witnessed <teammate> vent` line, but the audible derivative
  survives and tells the impostor "a vent happened here, this tick".

Impact is bounded but real: the duplicate gives one physical event two citable
observation ids in a substrate that runs `observation_id_rendering` and a
citation gate, and it makes the corpus's strongest evidence channel look twice
as dense as the world is.  The firewall residue leaks only teammate information
the impostor already has, so it is not a role leak -- but it is a suppression
that does not fully suppress.
```

**Verifier evidence (independent re-run).**

```
Independent re-scan of the committed replay bytes (my own script, prompt-level regexes over every meeting llm_call, roles re-derived from impostor-only actions + the 'you are the saboteur' prompt marker):
  $ PYTHONPATH=. uv run python <v6>/a31.py
    prompts containing any vent memory line: 1531
    same (tick,room) BOTH witnessed and heard: 1505
    witnessed-only (tick,room): 0
    heard-only rows: 108 -> distinct (set,seed,agent,tick,room): 27
    heard-only by role: Counter({'IMPOSTOR': 27})
  -> every number in the finding reproduces exactly.
Anchor 1 (samples/9p2i seed 0): my own replay walk (walk_replay, profile='audit', verify_tick_hashes=True) emits exactly ONE vent event witnessed by p-5:
    row t7 VentExited actor p-6 destination ENGINEERING destination_witnesses ['p-5']
  and p-5's recorded meeting-0 prompt carries BOTH rows with distinct observation ids:
    '- [obs p-5:8:1] [tick 8] You witnessed p-6 vent in ENGINEERING.'
    '- [obs p-5:8:2] [tick 8] You heard a vent use in ENGINEERING.'
Anchor 2 (the firewall residue, ml_corpus/9p2i seed 1026 p-9 tick 9 ADMIN): my walk shows row t7 Killed actor p-6 target p-3 room ADMIN, then row t8 VentEntered actor p-6 room ADMIN witnesses ['p-9'] -- i.e. an impostor witnessing its TEAMMATE vent in a kill room, exactly the _sighting_is_suppressed(teammate + kill-window) case; the same row shows p-9's own vent carries witnesses [] (the engine never lists an actor as its own witness), so the residue is the teammate branch, not the self-subject branch.
Code re-read confirms the derivation: observation/service.py:359-380 builds vent_rooms only from observed_actions whose action=='vent', and observation/service.py:526-543 (_vent_observation_for_agent) returns None unless agent_id is in the event's witness set and sets audible_room from the witnessed room -- so the 'sound' is a function of the sight and no non-witness channel exists. agents/memory/store.py:1045-1078 (_sighting_is_suppressed) + :1800-1816 drop the witnessed line only; :1599-1606 renders the heard line unconditionally.
```

**Verifier note.** Reproduces exactly, claim follows, defect/P2 stands. Two things the finding should carry: (1) PRIOR ART -- the redundancy half is already recorded in audits/review-2026-08-19/B/observation-firewall.md:155 F13 ('the audible channel is redundant with the visual one -- DESIGN §4.2 hints at "heard", i.e. wider than seen') and as idea #21 in audits/review-2026-08-19/A/collated-findings.md:587. It is NOT on the named known-open backlog (G-5/G-8/G-13/G-15/G-22/G-40/G-43, G-29, G-37, C-88, the alibi_vs_sighting dup mint), and the teammate-firewall-residue half (27/27 impostor heard-only rows) is genuinely new, so this is not a mere re-report -- but the novelty is the residue, not the duplicate. (2) The co-emission is PINNED by a shipped test: tests/observation/test_service.py:240-249 asserts a same-room witness gets BOTH visible_players[..].action=='vent' AND audible_events==[{'kind':'vent_use_heard','room':'ADMIN'}]; the fix sketch must update that pin. Nothing in DESIGN.md/docs specifies the double delivery (DESIGN.md:413 only lists the field), so 'defect' is the right label.

**Fix sketch.** Suppress the `vent_use_heard` AudibleEvent for any agent already receiving the vent as an observed action (observation/service.py:_audible_events), and route it through `_sighting_is_suppressed` so the firewall covers the audible copy too. If a genuine non-witness audible channel is wanted, build it from the vent event's ROOM rather than from `observed_actions`, so adjacent-room players actually hear something -- that would also give the crew a second, weaker vent signal instead of a redundant first one.

## A-32 — The whole spoken record sits one tick after the engine's event stream, while body ids keep the engine tick

**Severity:** P3 (finder: P2). **Classification:** known-open re-report (G-37) + documented convention; residual new sub-item = the body-id-in-prompt-header wrinkle. **Verdict:** ADJUSTED. **Area:** legibility / tick semantics. **Confidence:** high.
**Merged from:** legibility-pacing#7: The whole spoken record sits one tick after the engine's event stream, while body ids keep the engine tick.

**Claim.** 507 of 508 matched spoken saw_vent observations sit at engine_event_tick + 1 (reproduced exactly), because packets are built from the previous tick's events against the already-advanced state. This is the KNOWN-OPEN G-37 agent clock, closed-as-labelled in Phase 20, and the convention IS written down: eval/evidence_honesty.py:213-215 defines AGENT_CLOCK_OFFSET = 1 ('a row stamped [tick T] describes engine tick T - 1'), _assert_clock_alignment (eval/evidence_honesty.py:1668+) proves it on every game's discriminating sightings, and eval/replay_walk.py:273-283 documents the packet-building seam. The only part not already recorded is that the MEETING PROMPT HEADER prints the raw body id ('p-1 reported body body-p-6-28 at tick 29'), so one prompt shows two ticks for the same event -- the 2026-08-19 firewall audit had asserted 'the renderer does not print it'.

**As originally filed.** 507 of 508 matched spoken `saw_vent` observations are exactly engine_event_tick + 1, because the observation packet is built from the previous tick's events against the already-advanced state, and the same prompt shows a body id embedding the engine tick next to a discovery line stamped one later.

**Finder evidence.**

```
ALL findings fold the same reconstruction. Built once with (cwd = repo root):

  PYTHONPATH=. uv run python scratchpad/wave0/A/dump.py scratchpad/wave0/A/dump.json

dump.py re-seeds every committed seed and replays it through
`eval.replay_walk.walk_replay` under a profile with `verify_tick_hashes=True`
(so every reconstructed tick matched the recorded `state_hash`), recording per
tick: the recorded actions, the ENGINE events (`engine.events.event_to_dict`),
alive set, per-player rooms, bodies, sabotage state, task counts; plus every
meeting row verbatim (transcript turns, ballots, contradictions, llm_calls with
their full prompts) and the `game_over` row. Roles come from
`eval.validity.roles_by_seed` (re-seeding, same recipe). Reconstruction was
clean: 0 errors over 50 + 150 + 50 + 50 = 300 games (samples/9p2i 50,
ml_corpus/9p2i 150, samples/4p1i 50, ml_corpus/4p1i 50); rosters resolved to
(9,2,2) and (4,1,1).

  # match each spoken saw_vent to a Vent{Entered,Exited}Event witnessed by the speaker
    spoken saw_vent observations: 517  unmatched: 9
    spoken_tick - engine_event_tick distribution: {-9: 1, 1: 507}
  Uniform +1, with no exceptions among the 507 backed rows.

Worked anchor -- samples/9p2i seed 17:
  engine events              : row t28  Killed  actor p-4 target p-6 room EAST_HALL witnesses ['p-1']
                               row t29  MeetingTriggered actor p-1 body_id 'body-p-6-28'
  p-1's recorded meeting-3 prompt (llm_calls, agent p-1):
      "It is tick 29 and a meeting just started: p-1 reported body body-p-6-28 at tick 29."
      "- [obs p-1:29:1] [tick 29] You witnessed p-4 kill in EAST_HALL."
      "- [obs p-1:29:3] [tick 29] You discovered p-6's body in EAST_HALL."
      "- Your route (t = tick): ... ENGINEERING t27-28 -> EAST_HALL t29"
  and p-1's spoken turn: "I also witnessed p-4 kill right there at tick 29".

Why +1 is internally coherent: a pre/post state walk shows p-1 in ENGINEERING
at state.tick 28 and in EAST_HALL at state.tick 29, and the kill resolved in
EAST_HALL during tick 28's advance -- so "at tick 29, in EAST_HALL" agrees with
the route trail.  The render is consistent with itself.

  PYTHONPATH=. uv run python  # targeted walk of seed 17
    row 28 PRE state.tick 28 p-1 room ENGINEERING p-6 room EAST_HALL
       -> POST state.tick 29 p-1 room EAST_HALL p-6 alive False

The same +1 shows up in the substrate's own contradiction records:
  samples/9p2i seed 0: VentExited engine tick 7, witness p-5; the recorded
  contradiction reads "p-5 witnessed p-6 vent in ENGINEERING at tick 8" and
  every ballot in that meeting says tick 8.

The one thing that does NOT follow the convention is the body id: `body-p-6-28`
carries the KILL tick and is printed verbatim in a prompt whose every other
tick is 29.

Cost: any consumer that joins the transcript/ballot/contradiction record to the
engine event stream -- which is exactly what the re-ground does -- is off by one
on every kill, vent and body unless it knows the convention. I found no place
in DESIGN.md, observation/service.py or agents/perception.py that states it.
```

**Verifier evidence (independent re-run).**

```
Reproduction (my own matcher: spoken saw_vent observations from every recorded transcript turn, matched to Vent{Entered,Exited} events from my own replay walk where speaker in witnesses and actor==subject and the spoken room is the witnessed side):
  $ PYTHONPATH=. uv run python <v6>/a32.py
    spoken saw_vent observations: 517  unmatched: 9  ambiguous(multi-cand): 10
    spoken_tick - engine_event_row distribution: {1: 507, -9: 1}
    OUTLIER ml_corpus/9p2i seed 1102 p-3 -> p-8 MEDBAY spoken 8 vs engine row 17
  -> identical to the finding.
Anchor (samples/9p2i seed 17) re-verified from my walk + the raw bytes:
    row t28 Killed actor p-4 target p-6 room EAST_HALL witnesses ['p-1']
    row t29 MeetingTriggered actor p-1 body_id 'body-p-6-28'
    prompt: 'It is tick 29 and a meeting just started: p-1 reported body body-p-6-28 at tick 29.'
            '- [obs p-1:29:1] [tick 29] You witnessed p-4 kill in EAST_HALL.'
            '- [obs p-1:29:3] [tick 29] You discovered p-6's body in EAST_HALL.'
    p-1's spoken turn: 'I also witnessed p-4 kill right there at tick 29'
Mechanism re-read: orchestrator/game.py:1844-1858 builds packets from `state` (already advanced) with `last_events` (the PREVIOUS advance's events) and records the row under `input_tick = state.tick` before advancing -- the +1 is structural.
WHERE THE CLAIM FAILS: 'I found no place ... that states it'.
  $ grep -rn 'AGENT_CLOCK_OFFSET' --include='*.py' .
    eval/evidence_honesty.py:215  AGENT_CLOCK_OFFSET: Final[int] = 1
    (preceded by) '# The agent memory frame runs one ahead of the engine/replay frame: a row stamped ``[tick T]`` describes engine tick ``T - 1``.'
    eval/evidence_honesty.py:1701, :1897, :2355, :2411 -- the shipped joins apply it
    eval/evidence_honesty.py:1668 _assert_clock_alignment -- 'Prove the +1 agent clock on this game's discriminating sightings ... a clock change fails here first instead of silently re-pricing every bar'
    eval/evidence_honesty.py:47, :312, :321 -- the instrument definitions state 'memory tick = event tick + 1' / 'the spoken tick is resolved to the engine frame as tick - 1'
  eval/replay_walk.py:273-283: TickOpened carries 'last_events ... the previous tick's events' and is named 'the packet-building seam'; TickAdvanced is 'the fact-collection seam'.
KNOWN-OPEN status:
  $ grep -rn 'G-37' audits/
    audits/review-2026-08-19/A/collated-findings.md:452  'G-37 -- Agent tick stamps are +1 vs the replay timeline (and own-task lines are -2)'
    audits/review-2026-08-19/README.md:114  G-37 | Agent tick stamps run +1 against the replay timeline | 20.2 | PR #360
    audits/audit-phase-20-close.md:397  'recorded-as-finding ... G-37 -- the +1 agent clock is *labelled* on the spectator surface, because changing it would move every recorded tick stamp'
    tasks/phase-20.md:89, :417, :469 -- the seam is cited by line number in the phase contract.
```

**Verifier note.** The measurement is impeccable and reproduces to the row, so nothing here is REFUTED on evidence. What must change is the framing and the price. (a) It is the named known-open G-37, already adjudicated: labelled rather than re-stamped, on the stated ground that changing it would move every recorded tick stamp -- which is the same reason the finding's own fix sketch says 'do not change the render'. (b) The load-bearing novelty claim ('no place states it', 'no shared join helper') is false at HEAD: there is a named constant, a per-game assertion gate that fails first on a clock change, instrument-definition prose in two places, and a documented two-seam walker API. Fix items (1) and (2) are substantially already shipped. (c) P2 is too dear for a convention that is defined, asserted, and labelled; P3 fits the residue. (d) The genuinely new sub-item is small but real: the meeting prompt header prints the raw body id (body-p-6-28) inside a tick-29 prompt, whereas audits/review-2026-08-19/B/observation-firewall.md:152-154 recorded the body id as a latent channel that 'the renderer does not print'. Keep fix item (3) (render the body by victim+room); drop items (1) and (2) to 'extend the existing AGENT_CLOCK_OFFSET note to DESIGN.md'.

**Fix sketch.** Do not change the render (it is self-consistent and the whole recorded corpus depends on it). Instead: (1) write the convention down where a consumer will find it -- one paragraph in observation/service.py's packet docstring and DESIGN.md -- stating that event-derived observations carry perception tick = engine event tick + 1; (2) add a shared join helper in eval/ that applies the +1 so no new feature builder rediscovers it; (3) render the body reference by victim+room rather than by the raw id, so no prompt shows two different ticks for the same event.

## A-33 — 83 of 668 meetings end with every accusing voter authoring SKIP

**Severity:** P2. **Classification:** acceptable-emergent. **Verdict:** CONFIRMED. **Area:** meeting outcome vs speech (all four sets). **Confidence:** high.
**Merged from:** ballots-vs-speech#7: 83 of 668 meetings end with every accusing voter authoring SKIP.

**Claim.** In 12.4% of meetings every voter who spoke an accusation against a votable player then wrote SKIP, and none of those 83 meetings ejected anybody — the table argues and then unanimously declines.

**Finder evidence.**

```
REPRO: PYTHONPATH=... uv run python <scratchpad>/wave0/A/repro.py  (section F3, last line) plus the per-set breakdown:
  meetings where EVERY accusing voter authored SKIP: 83/668
  samples/9p2i: 152 meetings, 14 all-skip (of which ejected anyway: 0)
  ml_corpus/9p2i: 432 meetings, 51 all-skip (ejected anyway: 0)
  samples/4p1i: 40 meetings, 8 all-skip (ejected anyway: 0)
  ml_corpus/4p1i: 44 meetings, 10 all-skip (ejected anyway: 0)
The 4p1i rate is 18/84 = 21.4% versus 65/584 = 11.1% on 9p2i — with a 3-4 player table an all-skip meeting is a dead round, which is the shape the known-open G-43 (4p1i second act) describes; this is new baseline-7 quantification of that known-open item, not a new claim about it.
These meetings are not an instrument artefact: the tally recompute matches the recorded outcome in 668/668 meetings, so the SKIPs are the recorded ballots, not a scoring artefact.
```

**Verifier evidence (independent re-run).**

```
Independent re-implementation (my own script; guard markers unwound to the AUTHORED target so guard-coerced SKIPs are NOT counted as authored SKIPs; 'accusing voter' = cast a ballot and spoke >=1 accusation against a player who also cast a ballot):
  $ PYTHONPATH=. uv run python <v6>/a33.py
    total meetings: 668   meetings with no accusing voter: 0
    meetings where EVERY accusing voter authored SKIP: 83 / 668 = 12.4%
      replays/samples/9p2i: 152 meetings, 14 all-skip (ejected anyway: 0)
      replays/ml_corpus/9p2i: 432 meetings, 51 all-skip (ejected anyway: 0)
      replays/samples/4p1i: 40 meetings, 8 all-skip (ejected anyway: 0)
      replays/ml_corpus/4p1i: 44 meetings, 10 all-skip (ejected anyway: 0)
    ejected anyway TOTAL: 0
  -> every cell matches, and 4p1i 18/84 = 21.4% vs 9p2i 65/584 = 11.1% checks out.
ADVERSARIAL CHECK 1 -- is it just impostors declining? No: accusing-voter role composition of the 83 meetings is {'has-crew': 82, 'ALL-IMPOSTOR': 1}. 82/83 contain at least one CREWMATE accuser who then wrote SKIP.
ADVERSARIAL CHECK 2 -- is 'unanimously declines' accurate?
  $ PYTHONPATH=. uv run python <v6>/a33b.py
    all-skip meetings: 83
      of those, meetings where SOME (non-accusing) voter still authored an eject: 2
      total non-SKIP authored ballots inside them: 2
  So 81/83 are unanimous SKIP across ALL voters; 2 carry a single non-accusing eject ballot that never cleared the tally gate.
Outcome is read straight off the recorded ejected_player_id, not a recompute, so the '0 ejected' half needs no instrument trust.
```

**Verifier note.** Confirmed at the stated severity and classification. Two context notes that make it more useful without changing it: (1) the ballot-level phenomenon is already a shipped, documented instrument -- eval/deduction_metrics.py:1271-1311 TurnBallotConsistencyCells, metric 5, whose 'skip' bucket uses the identical denominator ('voter cast a ballot, spoke >= 1 accusing turn, and accused >= 1 VOTABLE player') and which is scored against the AUTHORED target exactly as this finding does; the NEW part is the meeting-level all-accusers aggregation, not the bucket. (2) The finding already declares its 4p1i half as quantification of the known-open G-43, which is the honest call -- the 9p2i half is not on the known-open list. The 'unanimously' wording is exact for 81/83 and near-exact for the other 2; worth one clause in the write-up.

**Fix sketch.** No mechanism change on gameplay grounds — it is the evidence band working. But flag these 83 meetings in the corpus: a meeting with speech, accusations, and a null decision is a legitimate outcome to fit but a degenerate one to over-weight, and 4p1i contributes them at twice the 9p2i rate. Consider an explicit corpus stratum so the re-ground can report performance on deciding vs non-deciding meetings separately.

## A-34 — Guard-redaction sentence normalizes to the empty skeleton and becomes the #1 model-voice repetition cluster in both 9p2i sets

**Severity:** P2. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** meetings/manager.py TEAMMATE_COERCED_VOTE_RATIONALE vs eval/vj_instruments.py _normalize_voice / response_skeleton_share. **Confidence:** high.
**Merged from:** dialect-leaks#3: Guard-redaction sentence normalizes to the empty skeleton and becomes the #1 model-voice repetition cluster in both 9p2i sets.

**Claim.** The bracketed form of the teammate-coercion redaction was chosen specifically to keep guard-authored prose out of the model-voice diversity fold, and it does strip the words -- but it leaves a zero-length skeleton that is the single largest repeated "voice" cluster in both 9p2i sets, so the guard's output still dominates the metric it was meant to stay out of.

**Finder evidence.**

```
THE INTENT, quoted from meetings/manager.py:235-245 (the comment on TEAMMATE_COERCED_VOTE_RATIONALE):
  "BRACKETED, not parenthesized ... ``eval.vj_instruments._strip_leading_markers`` drops exactly that
   form before a ballot body enters the SS2.5 echo / skeleton / distinct-n voice fold. A parenthesized
   note would survive that strip and feed the SAME guard-authored sentence into the model-voice
   diversity metrics on every coerced ballot -- measuring the guard's prose as the model's. The
   bracket is what keeps this synthetic body out of an instrument it was never model output for."

The strip does work as claimed. eval/vj_instruments.py:230 `_LEADING_MARKER_RE = re.compile(r"^\[[^\]]*\]\s*")`
with `\s*` (zero-or-more) plus the loop in `_strip_leading_markers` (line 659) removes both the
leading marker and the trailing redaction sentence, leaving "". I verified the loop also handles the
stacked-marker case (33 of 204 recorded annotations are a second marker after a first).

BUT the residue is a row, and an empty row clusters. Running the SHIPPED normalizer over the
committed ballots:

  $ uv run python -c "from eval.vj_instruments import _normalize_voice, _room_pattern; ..."
  samples/9p2i: 871 ballots, 850 distinct skeletons
    top-5 skeleton clusters (the response_skeleton_share basis):
         5  <EMPTY>
         3  the smoke is too thick to see the fire, so i'll hold my hand and let the chips fall where they may.
         3  the accusations are loud, but the evidence is too thin to justify an ejection.
         2  player saw player vent; that is proof enough.
         2  player saw player vent. impostors only. case closed.
    empty-skeleton rank: 1   count=5

  ml_corpus/9p2i: 2479 ballots, 2344 distinct skeletons
    top-5 skeleton clusters:
        13  <EMPTY>
        11  the evidence is thinner than a ghost's alibi, so i'll skip this round and let the chips fall where they may.
         9  player saw player vent. vents are impostor-only. case closed.
         8  the evidence is thinner than a ghost's alibi, so i'll sit this one out and let the chips fall where they may.
         5  player saw player vent. impostors only. vote player.
    empty-skeleton rank: 1   count=13

  samples/4p1i and ml_corpus/4p1i: empty count 0 (no teammate coercion recorded), unaffected.

`response_skeleton_share` is documented at eval/vj_instruments.py:39-40 as the "share of ballots in
the set's top-5 exact normalized-skeleton clusters of size >= 2", and the empty cluster is rank 1 in
both 9p2i sets -- so 18 guard-authored ballots are being counted as the most stereotyped model voice
in the corpus.

SCOPE IS BOUNDED, deliberately reported: the echo metric is NOT affected. `_meeting_echo` compares
within a meeting, and no meeting has >= 2 empty skeletons (checked: 0 meetings in all four sets),
which makes sense -- with 2 impostors at most one teammate-coercion can land per meeting per voter
pair. So the damage is confined to the set-level skeleton-share and distinct-skeleton cells.

Cross-check that the 18 are exactly the redactions: the pooled exact-repeat table over
ballot_rationale after marker-stripping has 18 empty strings at rank 1, matching exactly the 18
recorded `[rationale redacted by the vote guard; recorded reason: no confident read this round]`
occurrences counted in the annotation sweep.
```

**Verifier evidence (independent re-run).**

```
Ran the SHIPPED normalizer myself over every recorded ballot in all four sets (import _normalize_voice / _room_pattern / _SKELETON_TOP_K from eval.vj_instruments; rooms from load_canonical_map()):
  $ PYTHONPATH=. uv run python <v6>/a34.py
    replays/samples/9p2i: 871 ballots, 850 distinct skeletons, response_skeleton_share=0.0172
        1.    5  <EMPTY>
        2.    3  the smoke is too thick to see the fire, ...
        3.    3  the accusations are loud, but the evidence is too thin ...
        4.    2  player saw player vent; that is proof enough.
        5.    2  player saw player vent. impostors only. case closed.
      empty count=5 rank=1
      raw rows behind the empties: 5x "[teammate target 'p-N' coerced to SKIP] [rationale redacted by the vote guard; recorded reason: no confident read this round]"
    replays/ml_corpus/9p2i: 2479 ballots, 2344 distinct skeletons, response_skeleton_share=0.0186
        1.   13  <EMPTY>   (rank 1)  -- same raw shape
    replays/samples/4p1i: 120 ballots, empty count 0
    replays/ml_corpus/4p1i: 132 ballots, empty count 0
  -> every number in the finding reproduces exactly, 5 + 13 = the 18 redaction rows.
AGGREGATION RE-READ (the load-bearing half): eval/vj_instruments.py:913-916 is `skeleton_counts = Counter(all_skeletons)` then `sum(count for _, count in skeleton_counts.most_common(_SKELETON_TOP_K) if count >= 2)` with NO empty-string exclusion, and :971-976 divides that by `ballots_total` and publishes `distinct_skeletons=len(skeleton_counts)`. Confirmed: the empty cluster is in both the numerator and the denominator.
NET DISTORTION (my addition, the finding did not price it):
  $ PYTHONPATH=. uv run python <v6>/a34b.py
    samples/9p2i: shipped share=0.0172  excl-empty=0.0138   (delta +0.0034, ~+25% relative)
    ml_corpus/9p2i: shipped share=0.0186 excl-empty=0.0153  (delta +0.0033, ~+22% relative)
    meetings with >=2 empty skeletons: 0 of 152 and 0 of 432
    distinct skeletons 850 -> 849 and 2344 -> 2343
ECHO IS INDEED UNAFFECTED, and for a stronger reason than the finding gives: eval/vj_instruments.py:700-707 `_is_near_dup` returns False whenever either token list is empty, so an empty skeleton could not echo even if two landed in one meeting.
INTENT verified verbatim at meetings/manager.py:234-243 ('BRACKETED, not parenthesized ... The bracket is what keeps this synthetic body out of an instrument it was never model output for'), and the strip verified at eval/vj_instruments.py:230 (_LEADING_MARKER_RE with \\s*) + :659-666 (_strip_leading_markers loops, so the stacked marker pair strips to '').
```

**Verifier note.** Confirmed as a defect at P2: the shipped comment states the intent (keep guard prose out of the model-voice fold), and the implementation defeats it by leaving a countable empty row that ranks #1 in both 9p2i sets. Two additions for the write-up. (1) Price it: dropping the empty cluster moves response_skeleton_share 0.0172 -> 0.0138 and 0.0186 -> 0.0153 (the 18 rows do not simply subtract, because removing them promotes the 6th cluster into the top-5); that is roughly a quarter of the reported cell, plus one spurious distinct skeleton. (2) Bound it honestly: response_skeleton_share is NOT a Phase-20 pre-registered bar (no 'skeleton' hit in audits/audit-phase-20-preregistration.md or tasks/phase-20.md, and the baseline-7 close does not report it), so today the damage is a distorted instrument cell rather than a moved gate -- which is a reason to fix it cheaply before the re-ground reads it, not a reason to drop the severity. Not a re-report: no known-open item covers it.

**Fix sketch.** In eval/vj_instruments.py, drop ballots whose normalized skeleton is empty from the voice fold entirely (both the skeleton-cluster counter around line 913 and the ballots_total denominator the shares divide by), and record the dropped count as its own cell so the exclusion is visible rather than silent -- the same shape `training/surrogate/ballots.py` already uses for coerced-SKIP rows. A ballot whose entire body was guard-authored has no model voice to measure, so it should not be in the denominator either.

## A-35 — A ballot with target=SKIP and confidence>=0.95 is an impostor in 284 of 285 cases

**Severity:** P2. **Classification:** acceptable-emergent. **Verdict:** CONFIRMED. **Area:** recorded ballot label channel; training/surrogate. **Confidence:** high.
**Merged from:** ballots-vs-speech#6: A ballot with target=SKIP and confidence>=0.95 is an impostor in 284 of 285 cases.

**Claim.** Two scalar fields of the recorded ballot separate role almost perfectly — P(IMPOSTOR | target==SKIP and confidence>=0.95) = 99.6% (284/285) against a 25.8% base rate, and 88.1% at the >=0.90 cut — because a confident SKIP is what an impostor who knows the answer emits.

**Finder evidence.**

```
REPRO: PYTHONPATH=... uv run python <scratchpad>/wave0/A/repro.py  (section F5)
  ALL ballots (base rate): n=3602 impostor=928 (25.8%)
  recorded SKIP: n=1431 impostor=672 (47.0%)
  recorded SKIP & confidence >= 0.90: n=528 impostor=465 (88.1%)
  recorded SKIP & confidence >= 0.95: n=285 impostor=284 (99.6%)
  per set at the >=0.95 cut: samples/9p2i 61/61 (100%), ml_corpus/9p2i 207/208 (99.5%), samples/4p1i 6/6 (100%), ml_corpus/4p1i 10/10 (100%)
  contrast: EJECT & confidence >= 0.90: n=1388 impostor=65 (4.7%)
The mechanism is visible in the text: of accusing voters who then SKIP at confidence >= 0.90, 379/429 are impostors, and their rationales say why — samples/9p2i seed=1 m0 p-7 (0.95) "I cannot vote out my partner p-6..."; samples/9p2i seed=3 m1 p-6 (0.95) "...since I'm the one who vented, I'll skip".

WHAT THIS IS NOT: the surrogate's predict-side feature fence is clean — training/surrogate/ballots.py:264-292 `ballot_features_from_row` reads only belief_suspicion / belief_trust / is_reporter / witnessed_vent / meeting_index / alive_count and "NEVER touches ballot_target / ballot_confidence / ejected_player_id / outcome / is_ejected / is_impostor". So this is a property of the LABEL distribution, not a feature leak.
WHY IT STILL MATTERS FOR THE RE-GROUND: 25.8% of the fit's label rows are produced by a role-conditioned policy the role-blind features cannot see, and that sub-population is nearly deterministic in (target, confidence). A fit will either eat an irreducible error floor concentrated on impostor rows, or — if any downstream consumer conditions on predicted confidence — reproduce a 99.6%-accurate role oracle that no in-game agent could ever have (ballots are spectator-private, per audits/audit-phase-19-input-codex.md:140).
Mechanically the number is inert in-game: meetings/voting.py:233-238 reads confidence only for the LEADING non-SKIP target, so a SKIP ballot's confidence never enters any tally.
```

**Verifier evidence (independent re-run).**

```
Independent re-derivation (my own script; roles re-seeded via orchestrator.seeder.seed_initial_state per seed from each set's roster.json):
  $ PYTHONPATH=. uv run python <v6>/a35.py
    ALL ballots (base rate): n=3602 impostor=928 (25.8%)
    recorded SKIP: n=1431 impostor=672 (47.0%)
    recorded SKIP & conf>=0.90: n=528 impostor=465 (88.1%)
    recorded SKIP & conf>=0.95: n=285 impostor=284 (99.6%)
       samples/9p2i 61/61 (100%) | ml_corpus/9p2i 207/208 (99.5%) | samples/4p1i 6/6 (100%) | ml_corpus/4p1i 10/10 (100%)
    EJECT & conf>=0.90: n=1388 impostor=65 (4.7%)
  -> every cell matches the finding exactly.
ADVERSARIAL CHECK -- is the separation manufactured by the vote guard (which coerces a teammate target to SKIP)? No:
    guard census inside SKIP & conf>=0.95: {'teammate_coerced': 18, 'model-authored': 267}
    MODEL-AUTHORED SKIP only (authored target == 'SKIP') & conf>=0.95: n=267 impostor=266 (99.6%)
  The signature survives removal of every guard-rewritten row.
  The single non-impostor row: ml_corpus/9p2i seed 1061 meeting-1 p-4 conf 0.95, 'The sole impostor I witnessed venting has already been ejected, and the remaining evidence against t...'
MECHANISM anchors re-read verbatim from the bytes:
    samples/9p2i seed 1 m0 p-7 (IMPOSTOR, 0.95): 'I cannot vote out my partner p-6, and the remaining evidence against p-8 is circumstantial...'
    samples/9p2i seed 3 m1 p-6 (IMPOSTOR, 0.95): "I'd love to vote p-8, but since I'm the one who vented, I'll skip to avoid a fatal plot twist."
    accusing voters who then authored SKIP at conf>=0.90: 373/423 impostors (the finding's 379/429 counts RECORDED SKIP, i.e. adds the 6 guard-coerced rows -- same conclusion either way).
CODE FENCES re-read and both correct:
    training/surrogate/ballots.py:264-292 ballot_features_from_row -- features are belief_suspicion / belief_trust / is_reporter / witnessed_vent / meeting_index / alive_count only; docstring states it NEVER touches ballot_target / ballot_confidence / ejected_player_id / outcome / is_ejected / is_impostor.
    meetings/voting.py:225-238 -- SKIP in leaders returns SKIPPED before any confidence read; leader_max_confidence is computed only for the single non-SKIP leader. A SKIP ballot's confidence never enters a tally.
    audits/audit-phase-19-input-codex.md:140 does say 'ballots are spectator-private'.
```

**Verifier note.** Confirmed on every number, and it survives the one confound that could have killed it (the guard). Two additions. (1) The mechanism is not merely inferred from rationales -- it is SPECIFIED in the prompt: agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:169 (impostor-only block) reads 'Never vote a teammate -- if your suspicion lands on one, set "target" to "SKIP" instead', while :185 asks for an honest confidence in the call. A confident SKIP is therefore the instructed impostor ballot, which supports 'acceptable-emergent' but makes the label signature a designed consequence rather than an emergent accident -- worth saying, because it means the signature will persist across re-records unless the prompt or the label changes. (2) State the 99.6% as a property of the baseline-7 bytes, not a structural law: the guard's invalid-target->SKIP path can mint a CREW SKIP at 0.95, and did on the baseline-6 corpus (audits/review-2026-08-19/A/s3-meeting-decisions.md:433-436 records 'samples/9p2i seed 9 m1 p-2(CREW) -> SKIP conf=0.95' behind an [invalid target ... normalized to SKIP] marker; that ballot does not exist in the current seed-9 bytes). That is an argument FOR the finding's standing Goodhart probe, not against it. Not on the known-open list.

**Fix sketch.** Before the fit, either (a) report per-role fit metrics so the impostor-row floor is visible rather than averaged away, or (b) treat confidence on a SKIP as undefined and drop it from the label (target stays). Add a standing probe to the Goodhart battery: any candidate that recovers role from ballot metadata alone at >0.9 AUC is reading this signature, not deducing.

## A-36 — 79 ejection ballots name a player nobody formally accused at that meeting; 72 of the 79 are crewmates

**Severity:** P2. **Classification:** acceptable-emergent. **Verdict:** ADJUSTED. **Area:** recorded ballots vs meeting transcript (all four sets). **Confidence:** high.
**Merged from:** ballots-vs-speech#5: 79 ejection ballots name a player nobody formally accused at that meeting; 72 of the 79 are crewmates.

**Claim.** Claim unchanged and fully reproduced. The APPENDED side-check must be struck: 'for the 1,868 eject ballots that cite a resolvable turn id, the cited turn names/accuses/observes/was-spoken-by the target in 1,868/1,868 cases -- 0 dangling-topic citations. Citation integrity itself is sound.' is FALSE. Replace with: 59 of the 1,868 (3.2%) cited turns do not name, accuse, observe, or get spoken by the ballot target; 56 fail even a maximally-permissive test (the target id appearing anywhere in the cited turn's serialized JSON). Citation integrity is ~97% sound, not sound.

**As originally filed.** 79 recorded eject ballots target a player against whom no accusation claim was spoken by anyone in that meeting — 37 minted by the graph guard and 42 model-authored — and 72 of the 79 targets are crewmates.

**Finder evidence.**

```
REPRO: PYTHONPATH=... uv run python <scratchpad>/wave0/A/repro.py  (section F2)
  per set: {'replays/samples/9p2i': 26, 'replays/ml_corpus/9p2i': 51, 'replays/samples/4p1i': 1, 'replays/ml_corpus/4p1i': 1} TOTAL 79
  by guard: {'model-authored': 42, 'graph_redirect': 37}
  target role: {'CREWMATE': 72, 'IMPOSTOR': 7}
("formally accused" = the target appears as `claims[].against` on some turn of that meeting's transcript, with type == "accusation".)

THE 37 GUARD-MINTED ONES belong to the redirect finding: 35 of the 37 targets are crewmates, and in 3 meetings the never-accused player was actually ejected (all three crewmates): samples/9p2i 2:m0 -> p-5, ml_corpus/9p2i 1044:m0 -> p-7, ml_corpus/9p2i 1085:m0 -> p-1.

THE 42 MODEL-AUTHORED ONES read as coherent impostor play, not a bug:
  voter role: {'IMPOSTOR': 30, 'CREWMATE': 12}; target role: {'CREWMATE': 37, 'IMPOSTOR': 5}; all 30 impostor voters aim at a crewmate; 24 of 42 rationales mention vent / "saw me" / witness — the silence-the-witness shape.
  Every one of the 42 spoke at least one turn and every one carries a citation (42/42 non-null reason id), so none is a mute or uncited vote.
  Examples: samples/9p2i seed=24 m0 p-1(IMPOSTOR) -> p-3, "They caught me venting, so I have to vote them out to survive" (p-1 accused p-7 in speech); ml_corpus/4p1i seed=1022 m0 p-1(IMPOSTOR) -> p-4, "p-4 saw me vent. I am the impostor. Vote p-4 to save yourself."
  The 12 crewmate cases are late-swing reads, e.g. ml_corpus/9p2i 1012:m2 p-2 -> p-1 "while everyone chases p-9, p-1's frantic, nonsensical story about tick 16 movements is the real red flag here."

SEPARATE CHECK (clean): for the 1,868 eject ballots that cite a resolvable turn id, the cited turn names, accuses, observes, or was spoken by the ballot target in 1,868/1,868 cases — 0 dangling-topic citations. Citation integrity itself is sound.
```

**Verifier evidence (independent re-run).**

```
MY REPRO (independent loader over all 4 sets; roles parsed from each meeting's llm_calls '## Your role: X'; 300 games, 668 meetings, 3602 ballots, 2171 non-SKIP eject ballots):
  per set never-accused eject ballots: {'replays/samples/9p2i': 26, 'replays/ml_corpus/9p2i': 51, 'replays/samples/4p1i': 1, 'replays/ml_corpus/4p1i': 1} TOTAL 79  [EXACT MATCH]
  target role: {'CREWMATE': 72, 'IMPOSTOR': 7}  [EXACT]
  split by leading rationale annotation: 37 carry "[under-gate eject target 'p-N' redirected]", 42 carry none  [EXACT]
  redirect-37 target roles: {'CREWMATE': 35, 'IMPOSTOR': 2}  [EXACT]
  model-42 voter roles: {'IMPOSTOR': 30, 'CREWMATE': 12}; target roles {'CREWMATE': 37, 'IMPOSTOR': 5}; all 30 impostor voters aim at a crewmate; 24/42 rationales match /vent|saw me|witness/  [ALL EXACT]
  distinct (meeting,target) where the never-accused target WAS ejected: 3, all CREWMATE -- samples/9p2i headless-seed-2:meeting-0 -> p-5; ml_corpus/9p2i headless-seed-1044:meeting-0 -> p-7; ml_corpus/9p2i headless-seed-1085:meeting-0 -> p-1  [EXACT]
CITATION SIDE-CHECK (my rerun, predicate = the finding's own: speaker==target OR claims[].against==target OR observations[].subject==target OR target in observations[].co_present OR target substring of free_text):
  n=1868 resolvable-turn eject ballots [same denominator], topic-hit 1809, DANGLING 59 (3.2%)
  max-permissive variant (target id anywhere in json.dumps(turn)): n=1868, DANGLING 56 (3.0%)
  verbatim counterexamples: samples/9p2i headless-seed-10:meeting-0 p-1 -> p-7 cites turn-3, whose entire content is about p-1/p-2/p-8/p-4 and never mentions p-7; headless-seed-2:meeting-0 p-3/p-4/p-7/p-9 -> p-5 all cite turn-2, which names only p-1 and p-9.
SPEC CHECK: the redirect guard is SPECIFIED -- meetings/manager.py:263-275 mints the marker, :3164-3238 (guard_ballot_target_graph) documents 'redirects to the argmax-rendered candidate' with the DESIGN.md §4.6 gate; audits/review-2026-08-19/A/verdicts.md:248 already ruled the marker itself 'a sanctioned design choice with no model-facing effect'.
```

**Verifier note.** Headline reproduces to the last digit across all four sets, including the 42/37 split, both role tables and the three ejections. The 42 model-authored ballots are correct impostor play (all 30 impostor voters silence a crewmate witness) and the 37 guard-minted ones are the documented graph redirect, so acceptable-emergent / P2 is the right call and the classification stands. The one correction is real and matters: the finding's closing 'Citation integrity itself is sound / 0 dangling' would enter the record as a clean bill of health for a surface that is actually ~3% dangling, suppressing a genuine open item. 59 of 1868 cited turns have no topical connection to the ballot target at all.

**Fix sketch.** Leave the 42 model-authored ones alone — an impostor voting the witness who never formally accused them is correct play and should stay in the corpus. Fix the 37 guard-minted ones as part of the redirect finding. If the re-ground conditions ballots on the transcript, add a corpus-side flag `target_never_accused` so a fit can tell a strategic off-transcript vote from a guard artefact.

## A-37 — Nobody ever argues the exculpation: the reporter is saved by the evidence gate, not by the prose

**Severity:** P3 (finder: P2). **Classification:** acceptable-emergent (measurement/instrumentation gap, not an engine defect). **Verdict:** ADJUSTED. **Area:** reporter-justice / does the mechanism reach language. **Confidence:** high.
**Merged from:** reporter-justice#6: Nobody ever argues the exculpation: the reporter is saved by the evidence gate, not by the prose.

**Claim.** Across 3312 body-report ballots that all carry the exculpation block, the exculpation almost never becomes an argument -- but the two quantitative sub-claims are wrong. (1) Roughly 28 rationales (0.85%) co-mention the report with an exculpatory hinge and ~19-20 of those genuinely argue it (the recurring 'How do you know p-N is guilty just because they reported the body?' alone appears ~12x), not '16 co-mentions, ~5 genuine'. (2) At least one reporter DOES invoke it in self-defence, at ballot time (ml_corpus/9p2i seed 1020, headless-seed-1020:meeting-3, reporter p-6 -> SKIP: 'the mob is wrong to target me just because I reported the body'); the '0 reporter self-defence' result survives only because it is scoped to speech, where the reporter structurally cannot answer (they speak exactly one turn, the opening, in 618/618 body-report meetings). (3) 'The protection that actually bites is the generic under-gate redirect' is a mis-attribution: it omits the lever's PRIMARY channel, agents/memory/beliefs.py:174 REPORTER_EXCULPATION_SOFT_LIFT_CAP = 0.0, which zeroes the reporter's pre-vote accusation-driven soft lift; that cap is precisely why reporter-directed ballots sit under the gate and are therefore redirectable, so the 83 redirects are a downstream consequence of the belief channel working, not a substitute for it.

**As originally filed.** Across 3312 body-report ballots that all carry the exculpation block, only 16 rationales (0.48%) even co-mention the report with an exculpatory hinge and only ~5 truly invoke it, no reporter ever defends themselves with it in speech, and the protection that actually bites is the generic under-gate redirect -- which diverted 86 of the 364 ballots (23.6%) that intended to eject the reporter.

**Finder evidence.**

```
SPEECH SIDE (3312 turns across the 618 body-report meetings):
  turns whose free_text co-mentions a report with any exculpatory hinge (would n't / unlikely / rarely / clears / why would / not by itself / weak / base rate): 8 (0.24%), ALL by non-reporters, and manual read shows most are false positives about unrelated alibis (e.g. "I was in Cafeteria ... which clears them of being in Storage").
  turns by the REPORTER invoking their own report as exculpatory: 0. (270/618 reporters do SAY they reported -- "I found p-5's body in Storage at tick 10" -- but always as evidence-offering, never as a defence, because their only turn precedes every accusation. See finding 2.)

BALLOT SIDE (3312 ballots, 3312 carrying the block):
  rationales containing 'report*' at all:                        113 (3.41%)
  rationales co-mentioning report + an exculpatory hinge:         16 (0.48%)
  of those 16, genuine invocations on manual read: ~5, e.g.
    ml_corpus/9p2i seed 1116, headless-seed-1116:meeting-3, voter p-9 -> SKIP: "1. p-8 reported the body, making a self-kill unlikely. 2. p-3's accusation lacks hard evidence."
    ml_corpus/9p2i seed 1093, headless-seed-1093:meeting-2, voter p-9 -> SKIP: "the rush to vote p-6 is premature; their report exonerates them"
    ml_corpus/4p1i seed 1023, headless-seed-1023:meeting-0, voter p-4 -> p-1: "p-3's report clears them, so p-1's defensive deflection is the real red flag here."
    samples/9p2i seed 19, headless-seed-19:meeting-3, voter p-3 -> SKIP: "How do you know p-1 is guilty just because they reported the body?"
  the rest are the phrase used the other way round ("p-5's report of p-2 leaving Engineering ... making p-2 the clear suspect").

WHAT ACTUALLY PROTECTS THE REPORTER -- the generic guard annotations in rationale_text:
  ballots naming the reporter as an under-gate eject target that was redirected:  83
  ballots naming the reporter as an uncited zero-flag eject target coerced to SKIP: 3
  ballots that DID land on the reporter:                                          278
  -> pre-guard intent to eject the reporter: 364 ballots (11.0% of all body-report ballots); guard suppression rate 23.6%.
  meetings with >=1 such diversion off the reporter: 54/618; only 2 of the 30 convictions saw one.
Full annotation census over the 3312 ballots: {under-gate eject target 'X' redirected: 112, invalid primary_reason_observation_id 'X' nulled: 27, teammate target 'X' coerced to SKIP: 15, rationale redacted by the vote guard: 15, invalid primary_reason_id 'X' nulled: 8, uncited zero-flag eject target 'X' coerced to SKIP: 8, invalid target 'X' normalized to SKIP: 4}.
So reporter_exculpation is doing its work, if at all, as an invisible nudge on the ballot distribution; it never becomes an argument anyone makes, and the 76.4% of reporter-directed intent that the gate lets through is what produces the 30 convictions.
```

**Verifier evidence (independent re-run).**

```
MY REPRO:
  meeting typing by prompt (EMERGENCY_TRIGGER_PHRASE 'called an emergency meeting', meetings/manager.py:489): 618 body-report / 50 emergency meetings; 3312 body-report ballots and 3312 body-report turns  [EXACT]
  ballot prompts carrying '## Who reported the body': 3312/3312 body-report, 0/290 emergency  [EXACT -- 'all carry the block' confirmed]
  rationales matching /report/: 113 (3.41%)  [EXACT]
  report + the finding's OWN stated hinge list: 12 (0.36%), not 16 (0.48%)
  report + a broader-but-still-conservative hinge list (adds 'just because', 'exoner', 'self-kill', 'doesn't mean'): 28 (0.85%); manual read of all 28 gives ~19-20 genuine invocations, e.g. seeds 19:m3, 24:m1, 9:m0, 1020:m3, 1046:m1, 1049:m0, 1054:m1/m3/m4, 1076:m0, 1093:m2, 1116:m3, 1124:m0, 1129:m1, 1134:m4, 1036:m0, 1023:m0
  speech turns matching report+hinge: 8 (0.24%), 0 by the reporter  [EXACT]
  reporter turns per body-report meeting: histogram {1: 618} -- 0 reporter turns after the opening in 618/618, so speech self-defence is structurally impossible  [CONFIRMS the mechanism the finding names]
  ballots landing on the reporter: 278; "[under-gate eject target '<reporter>' redirected]": 83; "[uncited zero-flag eject target '<reporter>' coerced to SKIP]": 3; pre-guard intent 364 = 11.0% of body-report ballots; suppression 86/364 = 23.6%; meetings with >=1 diversion 54/618; reporter convictions 30, of which 2 saw a diversion  [ALL EXACT]
  full annotation census over the 3312: {under-gate eject target redirected: 112, invalid primary_reason_observation_id nulled: 27, teammate target coerced to SKIP: 15, rationale redacted by the vote guard: 15, invalid primary_reason_id nulled: 8, uncited zero-flag eject target coerced to SKIP: 8, invalid target normalized to SKIP: 4}  [EXACT]
OMITTED CHANNEL: agents/memory/beliefs.py:174 REPORTER_EXCULPATION_SOFT_LIFT_CAP: Final[float] = 0.0, applied at :1680 (delta = min(delta, CAP)) and :1704-1707, docstring :175-200 -- 'At 0.0 the reporter takes NO soft lift: proximity-at-discovery no longer reads as guilt on its own.' Spec: tasks/phase-15.md:552-605 Task 15.5, whose contract target is 'innocent-reporter ejections per 106: 22 -> near zero', never 'agents argue it aloud'.
```

**Verifier note.** The guard-side arithmetic is flawless -- 83/3/278/364, 23.6%, 54/618, 2/30 and the seven-row annotation census all reproduce to the unit, and the structural finding (the reporter speaks once, before any accusation, so cannot answer) is solid and well-evidenced. What must change: the invocation rate is ~4x the '~5' claimed, one reporter does self-defend at ballot time, and the causal headline credits the wrong mechanism -- the belief-side soft-lift cap is the lever's primary channel and the finding never measures it. With the fix_sketch being 'add a gauge', this is an instrumentation gap against an under-specified expectation, not a defect; P3.

**Fix sketch.** Once the exculpation reaches the accusation round (finding 2 fix), instrument it: add a gauge counting turns/ballots that cite the reporter's report as exculpatory, so "the mechanism reaches language" is a measured close-gate rather than an assumption. If after threading it into speech the invocation rate stays near zero, the sentence's placement -- buried between the candidate list and the suspicion-max line, after the reader has already formed a target -- is the next suspect; move it above the candidate roster.

## A-38 — The exculpation is under-inclusive: co-discoverers of the same body get none of it

**Severity:** P3 (finder: P2). **Classification:** acceptable-emergent (specified scope, empirically justified) -- fix_sketch rejected as written. **Verdict:** ADJUSTED. **Area:** reporter-justice / exculpation scope. **Confidence:** medium.
**Merged from:** reporter-justice#5: The exculpation is under-inclusive: co-discoverers of the same body get none of it.

**Claim.** The measurement stands verbatim (121/618 meetings have a non-reporter carrying the identical 'You discovered X's body' line at the report tick; innocent co-discoverers are ejected 3/89 = 3.37% vs 9/1755 = 0.51%, 6.6x, and accused >=2x at 14.61% vs 3.42%, 4.3x -- both differences are significant, Fisher two-sided p=0.017 and p=2.6e-5). But 'arbitrary who-clicked-first asymmetry' is wrong and the fix_sketch must be REJECTED. The exculpation keys on the report ACTION because that action has a measured impostor base rate of ZERO -- the reporter is CREWMATE in 618/618 body-report meetings on these bytes -- whereas merely standing at the body does not: 51 of the 140 non-reporter co-discoverer slots (36.4%) are IMPOSTORS. Widening the block to a 'body-discoverers set' would hand exculpatory framing to an impostor in over a third of cases, which is exactly the over-damping risk (a self-reporting impostor laundering suspicion) that beliefs.py rules out for reporters and cannot rule out here. Part of the co-discoverers' elevated accusation/ejection rate is therefore warranted signal, not artefact. Also correct '625/625 (100%)' to 607/625: 18 reporter speech prompts carry the line at tick-1, not at the report tick.

**As originally filed.** In 121 of the 618 body-report meetings at least one NON-reporter carries the identical "You discovered X's body" memory line at the report tick, and those innocent co-discoverers are ejected at 6.6x the rate of other innocents while the ballot block names only the single player who happened to emit the report action.

**Finder evidence.**

```
MEASUREMENT (regex `\[tick (\d+)\] You discovered ([\w-]+)'s body in ([A-Z_]+)` over the <memory> block of every speech prompt, keeping only matches at the meeting's own tick):
  meetings with >=1 NON-reporter carrying that line at the report tick:  121 / 618
  reporter's own memory carries the line: 625 / 625 speech prompts (100%)
  innocent CO-DISCOVERER slots:        89   acc>=2 13/89   = 14.61%   EJECTED 3/89   = 3.37%
  innocent non-co-discoverer slots:  1755   acc>=2 60/1755 =  3.42%   EJECTED 9/1755 = 0.51%
  -> co-discoverer ejection risk 6.6x the innocent baseline; >=2-accuser risk 4.3x.

VERBATIM -- samples/9p2i seed 0, headless-seed-0:meeting-1, reporter is p-1. Non-reporter p-8's memory contains, word for word:
  "- [obs p-8:17:7] [tick 17] You discovered p-2's body in STORAGE."
Identical in form to the reporter's own line. p-8 is at the body, is equally proximate, is equally innocent, and receives no exculpation of any kind at ballot time.
And ml_corpus/9p2i seed 1135, headless-seed-1135:meeting-0, turn 6: p-8 opens with "I found p-5 dead in ADMIN at tick 10" in the same breath as accusing the reporter -- the table treats one body-finder as exculpated-at-ballot-time and the other as a prosecutor, purely on who emitted the report action.

These 3 co-discoverer ejections are disjoint from the 30 reporter convictions, so 33 of the 42 pooled innocent ejections (78.6%) are a player being convicted for standing over a body.
```

**Verifier evidence (independent re-run).**

```
MY REPRO (regex /\[tick (\d+)\] You discovered ([\w-]+)'s body in ([A-Z_]+)/ over the <memory> block of every non-ballot llm_call prompt, kept only at the meeting's own tick):
  body-report meetings with >=1 NON-reporter carrying the line at the report tick: 121 / 618  [EXACT]
  innocent CO-DISCOVERER slots      n=  89   acc>=2  13 = 14.61%   EJECTED 3 = 3.37%  [EXACT]
  innocent non-co-discoverer slots  n=1755   acc>=2  60 =  3.42%   EJECTED 9 = 0.51%  [EXACT]
  ejection ratio 6.57x, acc>=2 ratio 4.27x  [EXACT]
  my added significance test: Fisher two-sided, ejection 3/89 vs 9/1755 p=0.01742; acc>=2 13/89 vs 60/1755 p=2.564e-05 -- the effect is real, not n=3 noise
  pooled innocent ejections 30 reporter convictions + 3 co-discoverer + 9 other = 42, so the 33/42 = 78.6% arithmetic holds  [EXACT]
DISCONFIRMING MEASUREMENT I ADDED:
  reporter role over all 618 body-report meetings: {'CREWMATE': 618} -- 0% impostor self-report
  NON-reporter co-discoverer slots by role: {'CREWMATE': 89, 'IMPOSTOR': 51} -> 36.4% impostor
SPEC: agents/memory/beliefs.py:190-200 states the lever's empirical basis verbatim -- 'the impostor self-report rate is EXACTLY ZERO -- 0 of the 164 report meetings ... had the killer as the reporter ... Self-report is therefore weakly exculpatory in this game, and zeroing the reporter's soft lift is safe against the only over-damping risk (a self-reporting impostor laundering suspicion): such a game does not occur in the corpus.' That justification is about the report action, and it does not transfer to proximity.
MINOR: reporter speech prompts 625, carrying the line AT the report tick 607 (not 625); all 18 misses carry it at tick-1 (e.g. samples/9p2i headless-seed-12:meeting-2, meeting tick 14, memory line '[tick 13] You discovered p-9's body in MEDBAY'). Same strict filter is applied to co-discoverers, so 121 and 89 are floors.
```

**Verifier note.** Every number in the finding reproduces exactly and the effect is statistically significant, so the observation is real and I strengthened it. The classification is what fails. The finding frames the reporter/co-discoverer split as arbitrary ('purely on who emitted the report action'), but the report action IS the signal: 0/618 reporters are impostors here while 51/140 co-discoverers are. Implementing the proposed fix -- rendering the exculpation block over a body-discoverers set -- would print 'being first to the scene is not by itself evidence of guilt' about an impostor in 36% of the meetings it fires in, re-opening precisely the laundering hole the lever's own docstring certifies as absent. Downgrade to acceptable-emergent/P3 and reject the fix; the most that is defensible is a neutral factual line naming who was at the body, with no exculpatory framing.

**Fix sketch.** Widen the exculpation from `reporter_id` to a body-discoverers set: meetings/manager.py:1776 already derives reporter_id at meeting scope; the orchestrator knows every player co-present with the body at the report tick (it mints the 'You discovered X's body' observation for each). Render the block over that set ("p-1 and p-8 were at the body when it was reported; being first to the scene is not by itself evidence of guilt"). Cheap, template-local, and it removes the arbitrary who-clicked-first asymmetry. Note this moves ballot-prompt bytes and needs a re-record.

## A-39 — G-29 quantified on baseline-7 bytes: stock repetition has moved off free_text onto structured claim reasons (33.6% share a skeleton twin)

**Severity:** P2. **Classification:** acceptable-emergent. **Verdict:** CONFIRMED. **Area:** transcript.turns[].claims[].reason vs .free_text vs ballots[].rationale_text, all 4 sets. **Confidence:** high.
**Merged from:** dialect-leaks#5: G-29 quantified on baseline-7 bytes: stock repetition has moved off free_text onto structured claim reasons (33.6% share a skeleton twin).

**Claim.** Quantifying the known-open G-29 stock-rationale item on these bytes: spoken free_text is now essentially fully distinct (100% exact-distinct, 99.5% skeleton-distinct), and the stock-phrase problem has concentrated almost entirely in the structured `claim.reason` field, where a third of all reasons share a normalized twin.

**Finder evidence.**

```
I am quantifying a KNOWN-OPEN item (G-29 stock rationales); the new part is the per-surface split on
the baseline-7 bytes. Method: strip leading `[...]` audit markers, then normalize with the repo's own
scheme (player ids -> P, room names -> ROOM, digit runs -> N, lowercase, collapse whitespace).

  ===== ballot_rationale: n=3602 | distinct exact=3489 (96.9%) | distinct skeleton=3377 (93.8%)
        sharing an EXACT twin: 169 (4.7%) | sharing a SKELETON twin: 345 (9.6%)
    top exact repeats:
        18  <empty -- the guard-redaction rows, see the separate finding>
        11  The smoke is too thick to see the fire, so I'll hold my hand and let the chips fall where they may.
        11  The evidence is thinner than a ghost's alibi, so I'll skip this round and let the chips fall where they may.
         8  The accusations are loud, but the evidence is too thin to justify an ejection.
         8  The evidence is thinner than a ghost's alibi, so I'll sit this one out and let the chips fall where they may.
         7  The vent sighting is undeniable proof.

  ===== free_text: n=3602 | distinct exact=3602 (100.0%) | distinct skeleton=3583 (99.5%)
        sharing an EXACT twin: 0 (0.0%) | sharing a SKELETON twin: 31 (0.9%)
    top skeleton repeats (nothing above 5):
         5  i found p dead in room. i saw p vent right there at tick n. p is the impostor.
         4  i was in room. p vented. vote p.
         3  i was in room. the vent confirms it.

  ===== claim_reason: n=4523 | distinct exact=4053 (89.6%) | distinct skeleton=3310 (73.2%)
        sharing an EXACT twin: 693 (15.3%) | sharing a SKELETON twin: 1520 (33.6%)
    top exact repeats:
        56  Vent sighting is definitive proof of impostor status
        20  Witnessed vent in Engineering at tick 8
        14  Witnessed venting in Engineering
        13  Witnessed venting in Engineering at tick 8
        11  Witnessed vent in Engineering
        10  Witnessed vent in STORAGE at tick 7
    top skeleton repeats:
       136  witnessed vent in room at tick n
       120  witnessed venting in room at tick n
        86  witnessed p vent in room at tick n
        56  vent sighting is definitive proof of impostor status
        46  p witnessed p vent in room at tick n
        36  witnessed vent in room
        34  witnessed venting in room

READ: the persona voice layer (Task 16.16) has done its job on free_text -- not one exact duplicate
in 3,602 spoken turns across 300 games. Ballot rationales are mildly stocky (the two "chips fall
where they may" SKIP formulas are the only real offenders, 30 ballots between them, and the
vote_ballot.j2:196 anti-stock instruction explicitly names and bans a *different* formula --
"p-N's alibi contradicts multiple sightings ..." -- which does not appear at all, so that ban worked).
The live G-29 surface is `claim.reason`, which no voice layer touches: it is generated under
accusation_round.j2's "<one short phrase>" instruction and collapses onto a handful of
witnessed-vent templates. 402 of 4,523 reasons are one of the three "witnessed vent/venting in ROOM
at tick N" skeletons alone.

For the re-ground this matters asymmetrically: `claim.reason` is a short structured field a fitted
model will find trivially predictable, so it will carry almost no gradient -- which is arguably fine,
but it should be a known property rather than a surprise, and it is a reason not to treat
claim.reason as an independent text channel alongside free_text.
```

**Verifier evidence (independent re-run).**

```
MY REPRO (reimplemented the repo's own normalization from eval/vj_instruments.py:659-689 -- _LEADING_MARKER_RE ^\[[^\]]*\]\s* stripped repeatedly, _PLAYER_ID_RE \bp-\d+\b -> player, room alternation -> room, \d+ -> n, lowercase, whitespace collapsed; canonical 9-room roster read off the corpus itself: ADMIN CAFETERIA EAST_HALL ENGINEERING LABS MEDBAY REACTOR STORAGE WEST_HALL):
  ballot_rationale n=3602 | distinct exact 3489 (96.9%) | distinct skeleton 3377 (93.8%) | sharing exact twin 169 (4.7%) | sharing skeleton twin 345 (9.6%)  [ALL EXACT]
     top exact: 18 <empty>, 11 'The smoke is too thick to see the fire...', 11 'The evidence is thinner than a ghost's alibi, so I'll skip this round...', 8 'The accusations are loud, but the evidence is too thin...', 8 '...so I'll sit this one out...', 7 'The vent sighting is undeniable proof.'  [EXACT, same order and counts]
  free_text n=3602 | distinct exact 3602 (100.0%) | distinct skeleton 3583 (99.5%) | sharing exact twin 0 (0.0%) | sharing skeleton twin 31 (0.9%)  [ALL EXACT]
     top skeletons 5 / 4 / 3 with the same three strings  [EXACT]
  claim_reason n=4523 | distinct exact 4053 (89.6%)  [EXACT] | distinct skeleton 3322 (73.4%) vs claimed 3310 (73.2%) | sharing exact twin 693 (15.3%)  [EXACT] | sharing skeleton twin 1505 (33.3%) vs claimed 1520 (33.6%)
     top exact 56/20/14/13/11/10 and top skeletons 136/120/86/56/46/36/34 -- every string and count EXACT
  vote_ballot.j2:196 anti-stock ban verified at HEAD ('Half the table opens with the stock formula "p-N's alibi contradicts multiple sightings ..." -- don't.'); that formula appears in 0/3602 rationale_text values  [CONFIRMS the finding's claim that the ban worked]
  KNOWN-OPEN check: G-29 is at audits/review-2026-08-19/A/collated-findings.md:378-386 and is scoped to spoken scaffolding + 'the ballot register' -- it never names claim.reason; it is recorded as still-open at audits/audit-phase-20-close.md:399 and :416 ('G-29's stock-rationale half'). The per-surface split IS new, and the finding declares the overlap in its own first paragraph.
```

**Verifier note.** Reproduces essentially to the digit on my own independent implementation of the repo's normalizer. The only drift is claim_reason's skeleton count (73.4%/33.3% vs 73.2%/33.6%), which is room-alternation noise between my roster and theirs and does not move the conclusion. Two prose slips worth recording, neither in the claim: 'four stock openings cover ~15% of all ballots' from G-29 is now 4.7% exact-twin share, i.e. the finding's improvement story is if anything understated; and '402 of 4,523 reasons are one of the three witnessed-vent skeletons' should be 342 (136+120+86 -- the finding's own listing). Classification acceptable-emergent is right and the honesty about the G-29 overlap is exemplary; P2 is generous for a no-code-change measurement of an item already on the Phase-20 verified-open list, but that is a judgment call, not an error.

**Fix sketch.** No engine change. Two options for the re-ground: (a) treat claim.reason as a categorical/templated field rather than free text in the feature build, since 33.6% of it is one of a few dozen skeletons; or (b) if the reason text is wanted as signal, extend the persona/diction guidance in accusation_round.j2 to the reason phrase the way it already covers free_text. Option (a) needs no prompt bump and no re-record; option (b) does, so it should ride the same combined re-record as the dialect fix if it is wanted at all.

## A-40 — The confidence grid is prompt-authored, not agent-derived, so ECE measures template compliance

**Severity:** P3. **Classification:** acceptable-emergent. **Verdict:** CONFIRMED. **Area:** agents/strategic/prompts/qwen3_6_27b/accusation_round.j2 (output_format calibration sentence). **Confidence:** high.
**Merged from:** herding-calibration#8: The confidence grid is prompt-authored, not agent-derived, so ECE measures template compliance.

**Claim.** The served template hands the model the exact confidence numbers to use (1.0 for a first-hand vent/kill, ~0.7 for a corroborated case, ~0.5 for a movement hunch) and the impostor reply skeleton hardcodes 0.7 in its JSON example, so the recorded confidence is largely a categorical label copied from the prompt rather than a belief -- 74.7% of all 9p2i ballot confidences fall on just four values.

**Finder evidence.**

```
TEMPLATE ANCHORS:
  agents/strategic/prompts/qwen3_6_27b/accusation_round.j2 (output_format, crew branch):
    '{"type": "accusation", ... "confidence": <0.0-1.0> ...} -- Calibrate "confidence" honestly: 1.0 only for a kill or a vent
     you watched happen first-hand; ~0.7 for a case a second account or a contradiction flag corroborates; ~0.5 for a hunch
     read off movement alone.'
  same file, impostor reply branch -- the JSON skeleton the model copies literally carries the number:
    '"claims": [{"type": "accusation", "against": "<one living player id>", "confidence": 0.7, "reason": "..."}]'
    '... ~0.7 for a corroborated case; ~0.5 for a movement hunch -- a modest number reads as more credible.'

COMMAND (value histogram, 9p2i pooled across samples+ml_corpus):
  cd /Users/danielkeinan/projects/AiLibi && uv run python - <<'PY' ... collect ballot + accusation confidences ... PY
OUTPUT (ballots, 3350 total):
  0.6:662  0.65:202  0.75:214  0.85:271  0.9:276  0.95:1292  1.0:188  (+16 stragglers at 0.61/0.62/0.66/0.67/0.73/0.97/0.98/0.99)
  distinct values: 23   top-4 share: 0.747   modal value 0.95 alone = 39% of all ballots
  'certain' mode (>=0.9) = 1756 = 52%;  'hedge' mode (0.6-0.65) = 864 = 26%.  The middle is nearly empty.
OUTPUT (accusations, 2872 total):
  0.5:116 0.55:76 0.6:634 0.65:240 0.7:247 0.75:393 0.8:80 0.85:93 0.9:105 0.95:210 1.0:675
  IMPOSTOR-only: 0.6:287 0.7:149 0.75:82 0.8:56 0.85:31 0.9:10 0.95:3 -- never 1.0, and 0.7 is the second mode,
  which is the literal value in the impostor reply skeleton.

CONSEQUENCE: eval/accusation_calibration.py's *_low_power flag already anticipates this failure mode
  (docstring: 'A provider whose confidences cluster into a couple of values ... produces a technically valid but
  statistically weak ECE'), and it FIRES on samples/9p2i vote_ballot ("vote_ballot_low_power": true, 4 populated bins)
  but not on ml_corpus/9p2i (6 populated bins) -- the extra bins there come from 4 stray values with n=1..3
  ([0.4,0.5) n=1, [0.5,0.6) n=3). The low-power flag is being cleared by noise, not by spread.
```

**Verifier evidence (independent re-run).**

```
MY REPRO:
  TEMPLATE ANCHORS at HEAD, verbatim -- agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:252 crew branch 'Calibrate "confidence" honestly: 1.0 only for a kill or a vent you watched happen first-hand; ~0.7 for a case a second account or a contradiction flag corroborates; ~0.5 for a hunch read off movement alone.'; :238 impostor reply JSON skeleton literally carries "confidence": 0.7; :239 '...~0.7 for a corroborated case; ~0.5 for a movement hunch -- a modest number reads as more credible.'  [ALL EXACT]
  BALLOTS, 9p2i pooled (samples + ml_corpus): total 3350, distinct values 23  [EXACT]
     0.6:662  0.65:202  0.75:214  0.85:271  0.9:276  0.95:1292  1.0:188  [EVERY ONE EXACT]
     top-4 share 0.747  [EXACT]; modal 0.95 = 38.6% (~39%)  [EXACT]
  ACCUSATIONS, 9p2i pooled: total 2872  [EXACT]; 0.5:116 0.55:76 0.6:634 0.65:240 0.7:247 0.75:393 0.8:80 0.85:93 0.9:105 0.95:210 1.0:675  [EVERY ONE EXACT]
  IMPOSTOR-only accusations: 0.6:287 0.7:149 0.75:82 0.8:56 0.85:31 0.9:10 0.95:3, and 1.0 count = 0  [EXACT; 0.7 is indeed the second mode, above 0.65's 68]
  LOW-POWER FLAG, recomputed against eval/accusation_calibration.py's own rules (DEFAULT_N_BINS=10 deciles, final bin closed at 1.0, _vote_ballot_samples excludes SKIP at :273, MIN_POPULATED_BINS_FOR_POWER=5 at :83):
     samples/9p2i   non-SKIP ballots 538  -> populated deciles 4 -> vote_ballot_low_power TRUE
     ml_corpus/9p2i non-SKIP ballots 1503 -> populated deciles 6 -> vote_ballot_low_power FALSE, and the two extra bins are exactly [0.4,0.5) n=1 and [0.5,0.6) n=3  [EXACT -- the flag is cleared by 4 stray ballots, as claimed]
  Docstring anticipation verified at eval/accusation_calibration.py:49-58 verbatim.
  SPEC: the calibration anchor is deliberate, not accidental -- tasks/phase-16.md:1152 asks for 'confidence verbalized against the citation', and the sentence entered with the bespoke set in commit d559f721 (task 16.13).
```

**Verifier note.** Every load-bearing number reproduces exactly, including the template line numbers, both histograms, the impostor never-1.0 result and the 4-vs-6 populated-decile split that clears the low-power flag on four stray ballots. Two presentational caveats, neither touching the claim: the ballot histogram as printed silently omits 229 ballots (0:28, 0.1:23, 0.4:30, 0.45:3, 0.5:78, 0.55:4, 0.7:32, 0.8:12) and its '+16 stragglers' line actually totals 35, so '>=0.9 = 1756 = 52%' is 1784 = 53% and '0.6-0.65 = 864 = 26%' is 866 by my count -- and 'the middle is nearly empty' is a shade strong with 0.75 holding 214. Coverage note: this partly re-treads known G-30 ('Confidence is bimodal, not calibrated', audits/review-2026-08-19/A/collated-findings.md:388) without citing it; the genuinely new parts are the template-origin attribution and the low-power-flag mechanics, and fix_sketch (1) -- a minimum count per populated bin -- is a real, cheap eval improvement. acceptable-emergent / P3 is right.

**Fix sketch.** Two cheap improvements: (1) tighten MIN_POPULATED_BINS_FOR_POWER's predicate in eval/accusation_calibration.py to require a minimum COUNT per populated bin (e.g. >=10) so a bin holding one ballot stops clearing the low-power flag -- as written, ml_corpus/9p2i reads as adequately powered on the strength of 4 stray ballots. (2) For the re-ground, treat confidence as the ~4-level ordinal it actually is rather than a continuous probability; fitting a regression head to it will mostly fit the template's enum.

## A-41 — Accuse-then-SKIP is the citation contract plus the evidence band, not hedging or herding — the two channels are governed by deliberately different standards

**Severity:** P3. **Classification:** intended-mechanic. **Verdict:** ADJUSTED. **Area:** agents/strategic/prompts/qwen3_6_27b/{accusation_round,vote_ballot}.j2; eval/deduction_metrics.py turn_ballot_consistency. **Confidence:** high.
**Merged from:** ballots-vs-speech#4: Accuse-then-SKIP is the citation contract plus the evidence band, not hedging or herding — the two channels are governed by deliberately different standards.

**Claim.** Claim and evidence stand verbatim (every count reproduced independently). ONLY the fix_sketch's closing premise must be struck: 'today no accusing voter ever cites it [their OWN accusing turn]' is FALSE — 387 of 1,868 turn-citing ballots (20.7%), and 386 of the 1,375 turn-citing ballots inside the CONSISTENT bucket (28.1%), carry a primary_reason_id that IS one of that voter's own accusing turn ids. The 'cheap follow-through lever' is therefore already in effect for ~28% of converting ballots and is not an untried lever; only the ZERO-citation SKIP bucket lacks it, and it lacks it because vote_ballot.j2:185/:194 tell it to.

**As originally filed.** All 1,184 accuse-then-SKIP ballots (and all 1,401 authored SKIPs across every set) carry null primary_reason_id AND null primary_reason_observation_id, exactly as vote_ballot.j2 demands, while the abandoned accusations are the low-confidence chain-continuation kind the accusation prompt separately demands — so the 54% "consistency" figure is measuring two prompts that were designed to disagree, not agents contradicting themselves.

**Finder evidence.**

```
REPRO: PYTHONPATH=... uv run python <scratchpad>/wave0/A/repro.py  (section F3), plus the per-prompt feature extraction over the recorded vote prompts in llm_calls.

THE CITATION SPLIT IS ABSOLUTE, not tendential:
  accuse-then-SKIP: n=1184 | citation on ballot: 0/1184
  consistent:       n=1672 | citation on ballot: 1667/1672
  ALL authored-SKIP ballots with any citation: 0 of 1401
  (all authored-EJECT ballots with NO citation: 30 of 2201)
The contract that produces this is verbatim in agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:185 — "a call you cannot source either way is a call to SKIP, and a SKIP needs no citation" — and :194 "Fill at least one of the two reason ids on every EJECT; a SKIP needs neither."

THE SPEECH SIDE IS A DIFFERENT STANDARD BY DESIGN:
  accusation_round.j2:217 (impostor reply) "Spend the rest of your words on ONE living player: name them in your one 'accusation' claim"; :224 (crew reply) "Redirect: if anything you saw points at a living player, name them in one 'accusation' claim so the chain follows the real suspect"; :252 blesses "~0.5 for a hunch read off movement alone".
And that is exactly which accusations fail to convert:
  accuse-then-SKIP: accusation-turn kinds {opening 238, opt_in 453, reply 493} | accusation confidence median 0.60
  consistent:       accusation-turn kinds {opening 341, opt_in 1067, reply 269} | accusation confidence median 0.95
  (reply turns — the chain-mandated kind — are 42% of non-converting accusations vs 16% of converting ones)

THE EVIDENCE BAND EXPLAINS THE REST (features parsed out of each voter's own recorded vote prompt in the meeting's llm_calls, regex on "maximum suspicion among the living ejection targets is **X**"):
  accuse-then-SKIP: mean rendered max suspicion 0.545, median 0.550, 76.0% below 0.60; the meeting flags a player this voter accused in 9/1184 (0.8%)
  consistent:       mean 0.785, median 0.800, 14.4% below 0.60; flag on an accused player in 1049/1672 (62.7%)
  other-target:     mean 0.727, 14.3% below 0.60, flag on an accused player 6.6%
vote_ballot.j2:185 states the rule those numbers obey: "when even your strongest living suspect is thin, SKIP is the sound call".

HERDING IS NOT THE DRIVER: among the 244 speak-A-vote-B ballots only 45.9% land on the table's most-accused player, and in 50% of them the voter's own abandoned accusation WAS the table's top — i.e. they moved away from the plurality as often as toward it.

READ TURNS (26 sampled at random across all four sets; representative): crew SKIPs speak the band directly — samples/9p2i seed=35 m1 p-7 accused p-5 at 0.6 then "The accusations feel scattered and unverified, so I prefer to wait for clearer evidence before casting a vote"; samples/9p2i seed=19 m1 p-7 "No hard evidence. Accusations are noise. Skip." Impostor SKIPs are role play, not hedging — ml_corpus/9p2i seed=1068 m1 p-6 accused p-5 in speech then "...since I'm the one who vented, I'll just skip".
```

**Verifier evidence (independent re-run).**

```
INDEPENDENT REIMPLEMENTATION (own marker-unwinding + bucketing, /private/tmp/.../wave0/A/v8_a41.py, plain-python over all 300 committed replay JSONLs; no reuse of the finder's repro.py):
  {'ballots': 3602, 'authored_EJECT': 2201, 'accusing_ballots': 3100,
   'bucket:consistent': 1672, 'bucket_cited:consistent': 1667,
   'authored_SKIP': 1401, 'bucket:skipbucket': 1184, 'bucket:other': 244,
   'bucket_cited:other': 231, 'authored_EJECT_uncited': 30}
  consistency_rate 0.539
  skipbucket: n=1184 cited=0 accconf_median=0.6 kinds={'reply':493,'opening':238,'opt_in':453}
     maxsusp mean=0.545 median=0.550 pct<0.60=76.0% n=1184 | flag-on-an-accused 9/1184 = 0.8%
  consistent: n=1672 cited=1667 accconf_median=0.95 kinds={'opening':341,'reply':269,'opt_in':1067}
     maxsusp mean=0.785 median=0.800 pct<0.60=14.4% | flag-on-an-accused 1049/1672 = 62.7%
  other:      n=244 cited=231 accconf_median=0.6 maxsusp mean=0.727 pct<0.60=14.3% | flag 16/244 = 6.6%
  speak-A-vote-B n=244; landed on table top 45.9%; own accusation WAS table top 50.0%
  (authored_SKIP_cited key never incremented => 0 of 1401)
EVERY published number matches to the digit, including reply-share 493/1184=41.6% vs 269/1672=16.1%.

PROMPT QUOTES VERIFIED VERBATIM AT THE CITED LINES:
  $ grep -n 'a call you cannot source either way' agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2  -> 185
  $ grep -n 'Fill at least one of the two reason ids' ...vote_ballot.j2                                -> 194
  $ grep -n 'Spend the rest of your words on ONE living player' ...accusation_round.j2                 -> 217
  $ grep -n 'Redirect: if anything you saw points at a living player' ...accusation_round.j2           -> 224
  $ grep -n 'for a hunch read off movement alone' ...accusation_round.j2                              -> 252 ('~0.5 for a hunch read off movement alone')

THE FIX-SKETCH PREMISE, REFUTED:
  own-accusing-turn citation, all sets:
    {'cited': 1868, 'cited_own_accusing_turn': 387}
  by bucket:
    {'consistent:cited_turn': 1375, 'consistent:cited_OWN_accusing_turn': 386,
     'other:cited_turn': 225, 'other:cited_OWN_accusing_turn': 1}
  e.g. ml_corpus/9p2i headless-seed-1002:meeting-0 p-1 cites '...:turn-0', its own accusing opening.

CLASSIFICATION CHECK (is the behaviour specified?): YES, and the finding says so correctly. Also note eval/deduction_metrics.py:1308-1311 (TurnBallotConsistencyCells docstring) ALREADY warns the metric '*Does NOT measure* correctness ... and deliberately scores an honest mid-meeting revision as an inconsistency: it measures follow-through, not virtue' — so the 'do not read 54% as a believability defect' half is pre-existing doctrine; the citation partition (0/1184 vs 1667/1672) is the genuinely new evidence.

NOVELTY CHECK: 'turn_ballot_consistency' / 'accuse-then-SKIP' appear nowhere in audits/, tasks/ or docs/ (grep -rl, 0 hits) — not a re-report of G-5/G-8/G-13/G-15/G-22/G-29/G-37/G-40/G-43/C-88 or the duplicate alibi_vs_sighting mint.
```

**Verifier note.** Strongest of the five. Independent reimplementation reproduces all 20+ published counts exactly, and the two prompt contracts are verbatim at the cited lines. Severity P3 and classification intended-mechanic both correct. The single defect is in the fix_sketch: its parenthetical rationale ('today no accusing voter ever cites it') is refuted 386-to-0 inside the very bucket it describes, so the proposed 'cheap lever' would be re-stating something ~28% of converting ballots already do. Instrument repairs (1) and (2) are unaffected and remain the actionable part.

**Fix sketch.** No gameplay change. Two documentation/instrument repairs before the re-ground: (1) publish the citation partition beside the consistency rate — a cell such as `inconsistent_skip_uncited` would show 1184/1184, making it visible that the bucket is the prompt's own SKIP discipline, not incoherence; (2) say so in the reading guide so a re-ground does not treat 54% as a believability defect to optimize away. If a genuine follow-through lever is later wanted, the cheap one is telling the voter in vote_ballot.j2 that their OWN accusing turn is a citable turn id — today no accusing voter ever cites it.

## A-42 — Clean negative: zero template, Jinja, XML-tag, JSON-schema or band-name fragments in 11,727 model-authored utterances

**Severity:** P3. **Classification:** intended-mechanic. **Verdict:** CONFIRMED. **Area:** all spoken surfaces, all 4 sets. **Confidence:** high.
**Merged from:** dialect-leaks#7: Clean negative: zero template, Jinja, XML-tag, JSON-schema or band-name fragments in 11,727 model-authored utterances.

**Claim.** Sweeping for the structural leak classes -- Jinja delimiters, prompt XML section tags, JSON schema key names, turn-kind vocabulary, markdown headers, and the evidence band names as literal labels -- returns zero hits in model-authored text; every apparent hit traces to the engine's own audit markers.

**Finder evidence.**

```
Recording this as a negative result because it bounds the problem: the output contract is holding,
and the dialect leak is a semantic one (the model paraphrasing what the prompt told it) rather than a
structural one (the model echoing prompt scaffolding).

  $ uv run python - (8 patterns over all 11,727 utterances)
  jinja/xml tag        ({{ }} {% or </persona|voice|memory|transcript|rules|players|map|
                        output_format|flagged_contradictions>) :  0 hits
  json schema key      ("turn_id"/"free_text"/"saw_vent"/...)    :  0 hits
  turn-kind word       (info-share, opt-in, opening/reply turn)  :  0 hits
  markdown header      (leading #/##/###, "markdown", "code fence"): 0 hits
  band word as label   (\b(STRONG|WEAK|PROOF)\b, caps)          :  0 hits
  bare schema key      (turn_kind, primary_reason_id, co_present, ...): 36 hits -- ALL 36 in
                        ballot_rationale, ALL 36 the engine's own
                        "[invalid primary_reason_observation_id 'obs p-N:N:N' nulled]" marker
  obs id form          ([obs , obs:N:N, turn:headless, headless-seed-N:meeting-N): 36 hits -- the
                        same 36 marker occurrences
  roll-call term                                                  :  1 hit
                        samples/9p2i seed 20 meeting-0 p-2 claim_reason:
                        "claimed vent sighting contradicts your own roll-call placement"

The band names are worth calling out specifically: the templates label the three evidence groups
"Proof." / "Conflicting accounts." / "Weak signals." (accusation_round.j2:164/170/176,
vote_ballot.j2:123/129/135), and agents do NOT echo them as labels. The 5 "weak signal(s)" and 1
"conflicting accounts" occurrences I found are all ordinary English usage in ballot rationales, e.g.
ml_corpus/9p2i seed 1090 p-1 "I need more than weak signals to eject" -- the phrase used as a
description, not as a system category. So the taxonomy naming is not itself leaking; only the
"The engine certified these" sentence attached to the top band is.

"roll-call" (1/11,727) is a genuine but isolated scaffold word -- the templates say "Answer the
roll-call" in the rules block. One occurrence in 300 games is not actionable.
```

**Verifier evidence (independent re-run).**

```
DENOMINATOR REPRODUCED EXACTLY. Independent assembly of 'model-authored utterances' = turn free_text (3602) + accusation/corroboration claim reasons (3107+1416) + ballot rationale_text (3602) = 11,727. Matches the published figure to the unit.

OWN 8-PATTERN SWEEP over those 11,727 strings (plain python, all 300 replays):
  jinja/xml tag             : 0 hits
  json schema key (quoted)  : 0 hits
  turn-kind word            : 0 hits
  markdown header           : 0 hits
  band word as label (STRONG|WEAK|PROOF, caps) : 0 hits
  bare schema key           : 36 hits — ALL 36 in ballot_rationale, ALL 36 engine markers, e.g.
      "[invalid primary_reason_observation_id 'obs p-9:8:1' nulled] I must respectfully note..."
      "[under-gate eject target 'p-1' redirected] [invalid primary_reason_id 'headless-seed-1006:meeting-0:turn-8' nulled] ..."
  obs id form               : 9 hits (my regex is narrower than theirs; all 9 are the same marker family)
  roll-call term            : 1 hit — samples/9p2i replay-seed-20, claim_reason:
      'claimed vent sighting contradicts your own roll-call placement'  (the exact utterance cited)

BAND-NAME SUB-CLAIM VERIFIED: template labels at the exact cited lines —
  vote_ballot.j2:123 'Proof. The engine certified these:...' :129 'Conflicting accounts.' :135 'Weak signals.'
  accusation_round.j2:164 / :170 / :176 (same three)
and in the corpus: 5 'weak signal(s)' + 1 'conflicting accounts', every one ordinary English, including the cited
  ml_corpus/9p2i replay-seed-1090 p-1 'P-4's lie is obvious, but p-2's alibi is messy; I need more than weak signals to eject.'
  (+ replay-seed-41 p-3 'The conflicting accounts about my own movements leave me unsure...')
No occurrence uses a band name as a system label.

SCOPE CAVEATS I FOUND (do not overturn, worth carrying):
  (a) 18 of 3,602 ballots carry 'rationale redacted by the vote guard' — for those the RECORDED rationale is engine text, so the model's own words were never in the swept denominator. eval/deduction_metrics.py:1533-1539 (ScaffoldLeakageCells) names exactly this under-count path and scans PRE-GUARD bodies instead; this sweep read the recorded surface. 0.5% of ballots, 0.15% of utterances.
  (b) The claim sentence 'every apparent hit traces to the engine's own audit markers' is not literally true of the roll-call hit — but the finding's own body says so plainly ('a genuine but isolated scaffold word'), so the record is internally honest.
```

**Verifier note.** Clean negative, reproduces to the unit. Denominator 11,727 is exact; the five structural classes are genuinely 0; the 36 bare-schema-key hits are all engine markers; the single roll-call hit is the one cited. Classification 'intended-mechanic' is a loose fit for a negative result (there is no mechanic here — it is a baseline reading with fix_sketch 'No action'), but nothing actionable turns on the label, so not adjusted. Two caveats for reuse: the sweep runs on the RECORDED surface, so 18 guard-redacted ballots' model text is invisible to it (the existing ScaffoldLeakageCells scans pre-guard bodies for exactly this reason); and the headline 'every apparent hit traces to engine markers' excludes the roll-call hit its own body discloses.

**Fix sketch.** No action. Retain as the baseline-7 structural-leak reading so a future set can be compared against it -- and if the machinery net in eval/deduction_metrics.py is extended per the gauge finding, add these eight structural patterns to it as zero-expected regression tripwires, since they cost nothing to check and currently read clean.

## A-43 — A tick-budget-capped game writes no game_over row, so its replay has no recoverable outcome

**Severity:** P4 (informational / documentation note, not a defect) (finder: P3). **Classification:** specified-behaviour (intended-mechanic), not defect. **Verdict:** ADJUSTED. **Area:** flow-edges / final tick bookkeeping. **Confidence:** high.
**Merged from:** flow-edges#7: A tick-budget-capped game writes no game_over row, so its replay has no recoverable outcome.

**Claim.** The code observation is exact and reproduces: HeadlessGame._run_loop returns TICK_BUDGET_REACHED at orchestrator/game.py:1842 before the record_game_end at :1904-1910, and run() (:1735-1754) adds no terminal row. But this is SPECIFIED, not a defect, and 'no recoverable outcome' overstates it: a capped game HAS no outcome by design, and its reason IS recoverable — eval/balance_eval.py::_game_report_from_replay falls back to the in-memory outcome string, so the GameReport reads reason='TICK_BUDGET_REACHED', winner=None, final_tick=None. The residual true gap is narrower: a reader of the replay JSONL ALONE cannot separate 'capped' from 'crashed'. 'unlike every other exit' is also inaccurate — MEETING_PHASE_REACHED (:1878) is a second exit with no terminal row.

**As originally filed.** HeadlessGame._run_loop returns TICK_BUDGET_REACHED without calling replay.record_game_end, so a capped game's JSONL ends on a PLAY-phase tick row with no terminal row -- unlike every other exit, which persists the decisive outcome by design.

**Finder evidence.**

```
CODE -- orchestrator/game.py:1840-1911:
    while state.phase != "GAME_OVER":
        if not self._scheduler.should_continue(state.tick):
            return state, "TICK_BUDGET_REACHED"      # <- returns before any record_game_end
        ...
    game_over_event = self._game_over_event(last_events)
    if replay is not None:
        replay.record_game_end(winner=..., reason=..., tick=...)
The docstring at orchestrator/replay.py:897-905 states record_game_end exists
precisely "so win-rate is evaluable from any replay log, including partial
tournaments" -- the budget exit is the one path that defeats it. run() (game.py:
1741-1754) only closes handles; it adds no terminal row either.

SCOPE IN THE COMMITTED BYTES: none. All 300 games carry a game_over row and end
naturally (.../scan.py, WalkComplete over every file):
    "end:CREWMATE_EJECT": 198, "end:IMPOSTOR_PARITY": 79, "end:CREWMATE_TASKS": 23
    (300 total; 0 TICK_BUDGET_REACHED, 0 walk errors)
Reported as an observation because the ML re-ground will run fresh recordings at
scale, where a cap hit becomes a silently outcome-less file rather than a loud one.
```

**Verifier evidence (independent re-run).**

```
CODE REPRODUCES EXACTLY:
  $ grep -n 'while state.phase != "GAME_OVER"|return state, "TICK_BUDGET_REACHED"|game_over_event = self._game_over_event|replay.record_game_end' orchestrator/game.py
    1840: while state.phase != "GAME_OVER":
    1842:     return state, "TICK_BUDGET_REACHED"
    1904: game_over_event = self._game_over_event(last_events)
    1906:     replay.record_game_end(
  run() at 1735-1754: the finally block calls replay.close() / observation_service.close() only.

COMMITTED-BYTES SCOPE REPRODUCES EXACTLY (own walk of all 300 JSONLs, last-row scan):
  Counter({'files': 300, 'end:CREWMATE_EJECT': 198, 'end:IMPOSTOR_PARITY': 79, 'end:CREWMATE_TASKS': 23})
  no_game_over: 0

THE BEHAVIOUR IS SPECIFIED IN THREE PLACES + PINNED BY A TEST:
 1. orchestrator/game.py:1383-1385 (HeadlessGameResult docstring): 'TICK_BUDGET_REACHED: TickScheduler capped the game before it ended naturally. final_state.phase is PLAY. The partial replay is still written to replay_path.'
 2. eval/balance_eval.py:27-30 (module docstring): 'TICK_BUDGET_REACHED is a non-decisive outcome: such a game writes no game_over replay row, so its GameReport carries winner=None / final_tick=None (the partial-run-robustness contract).'
 3. eval/balance_eval.py::_game_report_from_replay docstring: 'Partial-run robustness: a game that crashed / hit the tick budget before a game_over row yields winner=None / final_tick=None ... using fallback_reason (the in-memory outcome) for reason.' — and the body does exactly that (reason=end.reason if end is not None else fallback_reason).
 4. orchestrator/replay.py:897-906 (record_game_end docstring): 'Emitted once by HeadlessGame.run AFTER THE ENGINE FIRES ITS GameOverEvent' — the budget path is outside its stated contract by construction.
 5. tests/eval/test_tournament_report.py:86-91 + :244-262 pin it: _WaitAgent exists so 'a tiny tick budget yields a TICK_BUDGET_REACHED game with no game_over row — the partial-run shape the loader must tolerate', and test_partial_run_without_game_over_yields_none_winner asserts winner is None, final_tick is None, reason == 'TICK_BUDGET_REACHED'.

THE PROPOSED FIX WOULD BREAK THAT PIN: record_game_end(winner=None, reason='TICK_BUDGET_REACHED', tick=state.tick) makes GameEndReplayEntry.tick non-None, so _game_report_from_replay sets final_tick=state.tick and tests/eval/test_tournament_report.py:246 ('assert game.final_tick is None') fails. Any such change is a contract edit, not a bug fix.
```

**Verifier note.** Evidence reproduces perfectly — both the code path and the zero-scope-in-committed-bytes walk. The verdict turns on classification: 'defect' is wrong. Three docstrings name this exact behaviour as 'the partial-run-robustness contract', record_game_end's own docstring scopes itself to the GameOverEvent path, and a test pins the no-terminal-row shape end-to-end. The genuinely useful residue is much narrower than the claim: from the JSONL alone, capped and crashed look alike (though a meeting-abort crash does leave a FailedCallReplayEntry). Keep it as a documentation note for the ML re-ground, not a P3 defect, and price the proposed fix as a contract change that edits a pinned test.

**Fix sketch.** Write a terminal row on the budget path too -- record_game_end(winner=None, reason='TICK_BUDGET_REACHED', tick=state.tick) -- so every replay file ends with an explicit disposition and a downstream reader can tell 'capped' from 'truncated by a crash'. read_game_outcome already tolerates winner=None.

## A-44 — Vote resolution is exact, but the 0.6 confidence gate is inert and 19% of ballots sit exactly on it

**Severity:** P4 (informational; the re-tally half is a re-report of an existing pinned test) (finder: P3). **Classification:** intended-mechanic / already-pinned known behaviour, not acceptable-emergent. **Verdict:** ADJUSTED. **Area:** flow-edges / tie-vote handling and eject threshold. **Confidence:** high.
**Merged from:** flow-edges#6: Vote resolution is exact, but the 0.6 confidence gate is inert and 19% of ballots sit exactly on it.

**Claim.** All measurements reproduce exactly, but two load-bearing framings are wrong. (1) FACTUAL ERROR: 0.600 is NOT 'the inclusive cutoff printed in the prompt' / 'the threshold the vote prompt names' — the word 'threshold' occurs in 0 of the 3,602 recorded vote prompts, and the served qwen3_6_27b.v4 template renders only 'Your maximum suspicion among the living ejection targets is **X**', never the cutoff. (Older prompt sets do render _thr, but none generated these bytes: all 668 meetings stamp vote_ballot.qwen3_6_27b.v4.) The 0.600 point mass is a model round-number habit, not an echo of a printed number — confidence equals the target's rendered suspicion in only 286/3602 ballots, and 680 of the 692 ballots at 0.600 have neither the target's suspicion nor the rendered max at 0.60. The fix 'the prompt should stop naming the number' is therefore inapplicable. (2) NOT NOVEL: both headline facts are already pinned corpus facts in tests/meetings/test_vote_tally_parity.py. (3) 'inert / decorative' overstates: the gate is a leader-MAX floor, so it bites only when EVERY ballot for the plurality leader is under 0.6 — and making the cutoff exclusive would flip exactly ONE of the 429 recorded ejections, so the 19.2% point mass is almost entirely on ballots that decide nothing. The surviving, useful half of the finding is the fix_sketch's note (1) caution about feeding `confidence` to a fitted model with a 19.2% point mass, and note (2) on the 16 minority ejections.

**As originally filed.** All 668 committed meetings re-tally byte-for-byte to their recorded outcome, and ties resolve to SKIPPED as designed, but the DESIGN.md 4.6 skip-confidence rule fired 0 times in 429 plurality meetings, 692/3602 ballots (19.2%) carry confidence of exactly 0.600 (the inclusive cutoff printed in the prompt), and 16/429 ejections rest on a plurality of half the ballots or fewer.

**Finder evidence.**

```
RE-TALLY (.../votes.py: every committed meeting's recorded ballots pushed back
through meetings.voting.tally_ballots at the production threshold 0.6, compared
to the recorded outcome/ejected_player_id)
    {'meetings': 668, 'outcome:EJECTED': 429, 'outcome:SKIPPED': 239, ...}
    (no 'tally_mismatch' key -> 0 mismatches in 668 meetings / 3,602 ballots)
Skip provenance: skip_by_skip_plurality 210, skip_by_skip_tie 27,
skip_by_tie 2, skip_by_low_confidence 0.
The only two genuine non-SKIP ties in the corpus, both correctly SKIPPED
(meetings/voting.py:227-230):
    ml_corpus/9p2i replay-seed-1045.jsonl t23 {'p-3': 1, 'p-1': 2, 'p-9': 2}
    ml_corpus/9p2i replay-seed-1038.jsonl t24 {'p-9': 2, 'p-5': 2}

CONFIDENCE GATE (.../conf.py)
    ballots n=3602 ; confidence min=0.000 p05=0.500 median=0.900 max=1.000
    ballots with confidence < 0.6 threshold: 221 (6.14%)
    meetings with a single non-SKIP plurality leader: 429 ; leader max-confidence min=0.600
    of those, would have SKIPPED on the 4.6 confidence gate: 0
Histogram of ballot confidence:
    {0.0: 45, 0.1: 31, 0.4: 44, 0.45: 3, 0.5: 90, 0.55: 8, 0.6: 692, 0.61: 1,
     0.62: 1, 0.65: 220, 0.66: 2, 0.67: 1, 0.7: 36, 0.73: 2, 0.75: 218, 0.8: 12,
     0.85: 280, 0.9: 300, 0.95: 1381, 0.97: 9, 0.98: 3, 0.99: 16, 1.0: 207}
692 ballots (19.2%) land on exactly 0.600 -- the threshold the vote prompt names --
and the tally is inclusive at the cutoff (meetings/voting.py:236-238), so all of
them eject. The gate is therefore decorative on baseline 7: the leader's max
confidence never once fell below it, and its minimum is the cutoff itself.

MINORITY EJECTIONS (plurality is the design rule, DESIGN.md 5.2)
    eject_without_majority: 16 of 429
    e.g. ml_corpus/9p2i s1032 t19: p-5 ejected on 2 of 5 ballots
         {'p-2': 1, 'p-1': 1, 'p-5': 2, 'p-6': 1}
         samples/9p2i s14 t15: p-1 ejected on 3 of 6
         {'SKIP': 1, 'p-9': 1, 'p-1': 3, 'p-2': 1}
Meeting sizes: min 3, max 8, mean 5.39 living participants
(Counter({5: 145, 7: 142, 3: 125, 6: 122, 4: 74, 8: 60})).
Also verified clean in the same walk: 0 ballots from a dead player and 0 living
players without a ballot across all 668 meetings.
```

**Verifier evidence (independent re-run).**

```
OWN RE-TALLY (plain-python reimplementation of meetings/voting.py:224-239, no import of tally_ballots, over all 300 JSONLs):
  {'meetings': 668, 'outcome:EJECTED': 429, 'outcome:SKIPPED': 239,
   'reason:eject': 429, 'reason:skip_plurality_or_tie': 237, 'reason:tie': 2,
   'eject_without_majority': 16}   ballots 3602   tally_mismatch: 0
  (their skip split 210+27=237 skip-plurality/skip-tie + 2 genuine ties: identical)
  confidence histogram, identical to the published one:
   {0.0:45, 0.1:31, 0.4:44, 0.45:3, 0.5:90, 0.55:8, 0.6:692, 0.61:1, 0.62:1, 0.65:220,
    0.66:2, 0.67:1, 0.7:36, 0.73:2, 0.75:218, 0.8:12, 0.85:280, 0.9:300, 0.95:1381,
    0.97:9, 0.98:3, 0.99:16, 1.0:207}
  <0.6: 221 (6.14%) | exactly 0.600: 692 (19.21%) | min leader-max-confidence over the 429 ejections: 0.6
  meeting sizes {3:125, 4:74, 5:145, 6:122, 7:142, 8:60}, mean 3602/668 = 5.392
  minority examples reproduce (ml_corpus/9p2i s1032 m1: p-5 on 2 of 5, {'p-2':1,'p-1':1,'p-5':2,'p-6':1})

(1) THE PROMPT DOES NOT NAME THE THRESHOLD:
  $ python: over every recorded meeting's llm_calls, prompts containing
    'maximum suspicion among the living ejection targets' -> 3602
    of those, containing the word 'threshold'             -> 0
    rendered max exactly **0.60**                          -> 71
  $ grep -c threshold in the RENDERED prompt body: 0. The only 0.6x strings are suspicion/trust row values.
  prompt_versions across all 668 meetings: one value —
    {'accusation_round':'accusation_round.qwen3_6_27b.v4', ..., 'vote_ballot':'vote_ballot.qwen3_6_27b.v4'}
  The served template (agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:184-185) prints only the max plus
  prose ('when even your strongest living suspect is thin, SKIP is the sound call'). The sibling sets that DO
  render `{% set _thr = skip_confidence_threshold | default(0.6) %}` (qwen3_5_9b, qwen3_32b, qwen3_30b_a3b,
  glm_4_32b, cydonia_24b) generated none of these bytes.
  Confidence is not a copy of the graph either: eject_conf_eq_target_susp 286 / 3602; of the 692 ballots at
  0.600, 680 have neither the target's rendered suspicion nor the rendered max at 0.60.

(2) BOTH HEADLINES ARE ALREADY PINNED:
  tests/meetings/test_vote_tally_parity.py:118-133 pins the corpus size — 50/50/150/50 files,
  152+40+432+44 = 668 meetings, ballots summing to 3,602.
  :232-241 _EXPECTED_EJECTIONS_BY_THRESHOLD = {0.0:429, 0.25:429, 0.5:429, 0.6:429, 0.75:422, 0.9:342, 1.0:150}
  :228-231 comment: 'no committed meeting was decided by the confidence gate at its recorded cutoff.'
  :581-613 test_the_threshold_sweep_actually_moves_outcomes docstring: 'at and BELOW the recorded 0.6 threshold
  every meeting resolves exactly as it was recorded, so no committed meeting was ever decided by the confidence
  gate' — and its body asserts by_threshold[0.6] == recorded, i.e. the exact 'byte-for-byte re-tally' claim.
  The unexercised branch is covered directly by the `plurality_strictly_under_threshold` synthetic fixture.

(3) 'DECORATIVE' OVERSTATES:
  meetings/voting.py:234-238 takes leader MAX confidence, so the floor bites only when every ballot for the
  plurality leader is <0.6 — rare at median confidence 0.9. DESIGN.md:459 frames it deliberately: 'the silent
  tally floor (independent of LLM compliance) is what prevents one confident liar from cascading'.
  And the exclusive-cutoff fix is near-empty on these bytes:
    ejections 429 | ejections whose leader-max-confidence is exactly 0.600: 1
  (Adjacent, not the same gate: meetings/manager.py:3132 guard_ballot_target_graph already redirects an
  under-gate eject TARGET to the argmax candidate pre-tally — a separate rendered-suspicion gate, 61 markers
  in the corpus, so 'the 0.6 gate' names two different mechanisms that must not be conflated.)
```

**Verifier note.** Every number reproduces to the digit — the measurement work is sound. What fails is the interpretation. The threshold is not printed in the prompts that produced these ballots (0/3,602 contain the word), so the headline parenthetical and the first fix are built on a false premise; the 0.600 mass is an LLM round-number habit, not an echo. And the two headline facts ('re-tallies exactly', 'the gate never fired') are already named, pinned corpus facts in tests/meetings/test_vote_tally_parity.py, complete with the same 668/3,602/429 counts — this is a re-report. Finally the exclusive-cutoff remedy would move exactly 1 of 429 ejections. Keep only the fix_sketch's surviving halves: do not feed `confidence` to a fitted model as a clean continuous signal (19.2% point mass), and the 16 minority ejections are a balance question.

**Fix sketch.** No code change to the tally -- it is correct. Two notes for the re-ground: (1) `confidence` should not be fed to a fitted model as a continuous signal without acknowledging the 19.2% point mass at the prompt's own threshold; if the gate is meant to bite, the prompt should stop naming the number, or the cutoff should become exclusive so a ballot at exactly 0.6 does not eject. (2) If the 16 minority ejections are undesirable, the change is a quorum rule (plurality AND > half the ballots), which is a balance decision, not a correctness one.

## A-45 — Impostor deflection is varied and grounded; the lying is narrow and purposeful

**Severity:** P3. **Classification:** acceptable-emergent. **Verdict:** CONFIRMED. **Area:** impostor-behavior / deflection content. **Confidence:** medium.
**Merged from:** impostor-behavior#6: Impostor deflection is varied and grounded; the lying is narrow and purposeful.

**Claim.** Impostor replies are not templated and not fabricated — 535 replies with zero exact duplicates after id/tick normalisation, and the movement details they cite about the accused are true 98.0-98.3% of the time (better than crew's) — with the deception concentrated in the self-alibi, where 25.7% of impostor alibi claims are false and 44.7% of those span-cover the impostor's own kill or vent tick.

**Finder evidence.**

```
SHAPE (all 535 impostor reply turns, pooled over the four sets):
  claims-per-reply {1: 526, 0: 9}; claim types {'accusation': 526}; purely defensive (claims == []) 9/535 = 1.7%
  word count median 33, p10 20, p90 47
  exact-duplicate normalized free_texts (p-N -> P, 'tick N' -> TICK, lowercased): 0; 535/535 unique
  most common opening 4-gram 'how do you know' 27/535 = 5.0%; next 'i was just passing' 21 (3.9%), 'i might have just' 14 (2.6%). No opener exceeds 5%.

GROUNDEDNESS of the deflection's factual content. Ground truth = each player's engine route parsed from the 'Your route (t = tick):' line in their own meeting prompts. For every accusation claim whose `reason` names a room + a tick and names no third party, check the accused's true room:
  loose extractor:  CREWMATE verified 818, wrong 116 (14.2%) | IMPOSTOR verified 363, wrong 6 (1.7%)
  Inspection showed the crew number is inflated by the 'left ROOM at tick N' idiom (the speaker means the player was there at N-1), so I re-ran with that idiom excluded and only the unambiguous 'in ROOM at tick N' form kept:
    CREWMATE n=201, wrong 13 (6.5%) | IMPOSTOR n=148, wrong 3 (2.0%)   [two-proportion z ~= 1.96, p ~= 0.05 - suggestive, not decisive]
  Either way the impostor does not fabricate other players' movements; it re-frames true ones.

WHERE THE LYING ACTUALLY LIVES - structured self-alibi claims (subject == speaker), checked against the engine route span:
  CREWMATE n=848, FALSE 64 (7.6%) | IMPOSTOR n=148, FALSE 38 (25.7%)
  Of the 38 false impostor alibis: 17 (44.7%) span-cover a tick on which that impostor killed or vented, and 9 (23.7%) falsify the crime tick itself. Examples:
    [samples/9p2i] headless-seed-22:meeting-0 p-7 claims WEST_HALL t5-8; truth {5: WEST_HALL, 6: MEDBAY, 7: MEDBAY, 8: WEST_HALL}; own kill/vent tick inside the lie: 6
    [ml_corpus/9p2i] headless-seed-1058:meeting-0 p-7 claims ENGINEERING t2-8; truth has STORAGE t5-7; own kill/vent ticks inside the lie: 5,6,7
    [ml_corpus/9p2i] headless-seed-1099:meeting-0 p-1 claims STORAGE t11-13; truth {11: ENGINEERING, 12: ENGINEERING, 13: STORAGE}; kill/vent ticks 11,12
  Detector response on those 38: a contradiction flag names the liar in 21 (55.3%), an alibi-class flag (alibi_vs_sighting / alibi_conflict) in 14 (36.8%).
  Contradiction kinds minted across all four sets: {'vent_sighting': 448, 'alibi_vs_sighting': 100, 'alibi_conflict': 60, 'alibi_vs_physical': 13}.

And the roll-call channel is honest for both roles (finding 2, measurement 3): impostor whereabouts observations match the true room 98.1% (S9) / 99.3% (C9). So the impostor's whole deception budget is spent on the multi-tick alibi span and on framing - which is coherent, targeted play.
```

**Verifier evidence (independent re-run).**

```
SHAPE — REPRODUCED EXACTLY (own role derivation from the prompts' '## Your role:' / 'Secret: you are the saboteur' / '## Your team' lines; 84 one-impostor + 200 two-impostor games):
  impostor reply turns: 535
  claims-per-reply {0: 9, 1: 526} ; claim types {'accusation': 526} ; purely defensive 9/535 = 1.7%
  normalized (p-N->P, 'tick N'->TICK, lowercased) exact duplicates: 0 — 535/535 unique
  top opening 4-grams: 'how do you know' 27 (5.0%), 'i was just passing' 21, 'i might have just' 14, 'i was nowhere near' 13
  word count median 34, p10 20, p90 48 (published 33 / 20 / 47 — percentile-convention drift only)

CONTRADICTION KINDS — EXACT:
  {'vent_sighting': 448, 'alibi_vs_sighting': 100, 'alibi_conflict': 60, 'alibi_vs_physical': 13}

SELF-ALIBI — REPRODUCED, with a documented sub-count drift. Ground truth = each speaker's engine route
parsed from the '- Your route (t = tick): ...' line in their own meeting prompts; crime ticks taken from the
replay TICK rows' kill/vent actions (action-type census: kill 997, vent 1169):
  CREWMATE n=848 FALSE=64 (7.5%)   [published 848 / 64 / 7.6%]
  IMPOSTOR n=148 FALSE=35 (23.6%)  [published 148 / 38 / 25.7%]
  of the false impostor alibis: 14/35 = 40.0% span-cover an own kill/vent tick [published 17/38 = 44.7%]
                                 6/35 = 17.1% falsify the crime tick itself   [published 9/38 = 23.7%]
  The 3-claim gap is methodological, not substantive: the 'Your route' line OMITS ticks the player spent
  inside a vent, and my reconstruction skips those ticks while theirs evidently scores them. All three
  published examples reproduce byte-for-byte, gaps and all:
    samples/9p2i   headless-seed-22:meeting-0   p-7 claims WEST_HALL t5-8 | truth {5:WEST_HALL,6:MEDBAY,7:MEDBAY,8:WEST_HALL} | crime ticks in span [6]
    ml_corpus/9p2i headless-seed-1058:meeting-0  p-7 claims ENGINEERING t2-8 | truth {...5:STORAGE,6:STORAGE,7:None,8:ENGINEERING} | crime [5,6,7]
    ml_corpus/9p2i headless-seed-1099:meeting-0  p-1 claims STORAGE t11-13 | truth {11:ENGINEERING,12:None,13:STORAGE} | crime [11,12]

GROUNDEDNESS — DIRECTION CONFIRMED, AND STRONGER UNDER AN INDEPENDENT EXTRACTOR. My own strict net
('in ROOM at tick N' in an accusation `reason`, no third party named, 'left ' idiom excluded), checked
against the accused's engine route:
  CREWMATE n=498 wrong=78 (15.7%) | IMPOSTOR n=175 wrong=2 (1.1%)
Same sign, larger gap than the published 6.5% vs 2.0%. The published two-proportion z arithmetic also checks
out (p1=13/201, p2=3/148, pooled 16/349 -> z = 1.96).
```

**Verifier note.** Core claim holds on independent evidence: impostor replies are not templated (535/535 unique, no opener above 5%), the impostor does not fabricate other players' positions (my strict net puts it at 1.1% wrong vs crew's 15.7%), and the deception is concentrated in the multi-tick self-alibi (~24-26% false vs crew's 7.5-7.6%, and roughly 40-45% of those cover the impostor's own kill/vent tick). Two things to carry: (a) the secondary sub-counts are sensitive to how vent-occluded route ticks are handled — 38/17/9 under their reconstruction, 35/14/6 under mine — so quote them as ranges, not point values; (b) fix_sketch (i)'s phrasing 'the impostor is the MOST factually accurate speaker at the table' is a superlative a two-group comparison at p ~ 0.05 does not establish, and the finding's own body correctly calls that result 'suggestive, not decisive' — the fix note should inherit the body's hedge. Confidence 'medium', severity P3 and classification acceptable-emergent all appropriate; not a re-report of any backlog item (G-22 measures whereabouts COVERAGE, this measures ACCURACY given emission).

**Fix sketch.** No fix needed for content quality - this is the part of impostor behaviour that is working. Two things worth carrying forward rather than changing: (i) the impostor is the most factually accurate speaker at the table about other players' positions, which is itself a weak learnable role signal a fitted model may pick up on top of finding 1 - worth measuring after the finding-1 fix rather than acting on now; (ii) 36.8% alibi-class flag recall on purposeful alibi lies is the honest ceiling of the current prosecution rules and is the number to move if impostor deception is meant to be catchable.

## A-46 — Agents narrate station events that never happened -- 'when the lights went out', security cameras

**Severity:** P3. **Classification:** acceptable-emergent (camera half); duplicate-of-known-open G-40 (lights half). **Verdict:** ADJUSTED. **Area:** legibility / free-text fabrication. **Confidence:** high.
**Merged from:** legibility-pacing#9: Agents narrate station events that never happened -- 'when the lights went out', security cameras.

**Claim.** 17 turns use the phrase "the lights went/go out" in a corpus that contains zero `lights` sabotages -- but >=15 of the 17 read as the noir IDIOM for the moment of the kill, not as an assertion that a station lights event occurred (0/17 co-mention 'sabotage', a repair room, or any sabotage kind; three are spoken by the killer about his own victim). What IS a genuine fabricated affordance is the camera/security-feed mechanic: 4 turns in 3 games invoke a camera that exists nowhere in engine/, meetings/, observation/, agents/ or the map, and in ml_corpus/9p2i seed 1058 it propagates to a second speaker. None of it reaches the decision layer: 0 of 3,602 ballot rationales carry the vocabulary, and all 448 vent_sighting contradictions name a subject who really vented. The lights half also duplicates a known-open item: prior-audit G-40's 'Related wording bug' already recorded "agents reference 'when the lights went out' in games with no lights sabotage" and already read it correctly as "a figure of speech that reads as a hallucinated event".

**As originally filed.** 17 turns assert a lights event in a corpus that contains zero lights sabotages (9 of them spoken by CREWMATES) and 4 turns invoke a camera/security-feed mechanic that does not exist in the engine or the map, but none of it reaches the decision layer: 0 of 3,602 ballots carry the vocabulary.

**Finder evidence.**

```
ALL findings fold the same reconstruction. Built once with (cwd = repo root):

  PYTHONPATH=. uv run python scratchpad/wave0/A/dump.py scratchpad/wave0/A/dump.json

dump.py re-seeds every committed seed and replays it through
`eval.replay_walk.walk_replay` under a profile with `verify_tick_hashes=True`
(so every reconstructed tick matched the recorded `state_hash`), recording per
tick: the recorded actions, the ENGINE events (`engine.events.event_to_dict`),
alive set, per-player rooms, bodies, sabotage state, task counts; plus every
meeting row verbatim (transcript turns, ballots, contradictions, llm_calls with
their full prompts) and the `game_over` row. Roles come from
`eval.validity.roles_by_seed` (re-seeding, same recipe). Reconstruction was
clean: 0 errors over 50 + 150 + 50 + 50 = 300 games (samples/9p2i 50,
ml_corpus/9p2i 150, samples/4p1i 50, ml_corpus/4p1i 50); rosters resolved to
(9,2,2) and (4,1,1).

  # regex scan of every free_text over all 3,602 recorded turns
    lights-as-event ("lights went/go/were/cut out", "when the lights ..."):
        17 turns | 16 in games with ZERO sabotage of any kind
        by role: {'CREWMATE': 9, 'IMPOSTOR': 8}, 17 distinct games
      The 17th (samples/9p2i seed 27, p-7 IMPOSTOR) is in a game whose only
      sabotage is `reactor`, whose `affected_visibility` is
      `same_room_and_adjacent` (canonical_1.yaml:394-400) -- it does not touch
      lights either.  There are 0 `lights` sabotages in the entire corpus
      (see the sabotage finding), so 17/17 describe an event that never occurred.

      samples/9p2i seed 11 meeting-1 p-5 (CREWMATE):
        "... p-9 was the one standing right next to poor p-1 when the lights went out."
      samples/9p2i seed 19 meeting-2 p-4 (CREWMATE):
        "... explain why you were hanging out in the morgue when the lights went out."
      ml_corpus/9p2i seed 1047 meeting-1 p-5 (CREWMATE):
        "... I saw p-6 and p-8 standing together in that room just before the lights went out."

    camera / security feed (no such mechanic exists anywhere in engine/ or the map):
        4 turns, 3 distinct games, {'CREWMATE': 3, 'IMPOSTOR': 1}
      ml_corpus/9p2i seed 1058 meeting-0 -- the fabrication propagates:
        p-2 (CREWMATE): "... I have the killer on camera, so let's not make this a long story."
        p-4 (CREWMATE): "... I suppose we should trust the one with the camera."
      (that meeting's vent claim was genuine -- p-7 VentExited engine t7,
       destination_witnesses ['p-2'] -- so the camera was decoration, and p-4's
       ballot dropped it: "I suppose if p-2 truly saw p-7 vent ...")

  Scanned negative: blackout 0, oxygen/O2 0, comms 0, meltdown 0, power 0,
  security 0, door log 0, medbay scan 0, admin tablet 0, "moved the body" 0.
  ("vitals" matched twice but both are the adjective, "vital duties/tasks".)

  Containment check -- the decision layer is clean:
    ballots 3602 | with fabricated-mechanic vocabulary: 0
    vent_sighting contradictions 448 | engine-backed 448 | not backed 0

So this is voice-layer confabulation filling the vacuum left by the
content-free sabotage alarm and the nonexistent lights sabotage, not a
mechanism failure.  It matters for the re-ground only because a model fitted on
this language will reproduce references to affordances the game does not have.
```

**Verifier evidence (independent re-run).**

```
Independent path: I did NOT use the auditor's dump.json. I re-read the 300 committed replay JSONLs directly (300 games, 668 meetings, 3,602 turns, 3,602 ballots -- all match) and derived roles two ways: (a) from the recorded prompt persona marker ('Secret: you are the saboteur') plus kill/vent actors, (b) from eval.validity.roles_by_seed re-seeding. Cross-check: 1,699 player-role pairs, 0 mismatches.

[1] SABOTAGE CENSUS (raw actions, all 300 games):
  action types: {'move':12916,'do_task':15914,'kill':1011,'vent':1179,'emergency':67,'wait':3383,'report':717,'sabotage':31,'repair_sabotage':132}
  sabotage payloads: {'{"kind": "reactor"}': 31}   -> 0 lights sabotages. REPRODUCES.

[2] LIGHTS SCAN (regex over transcript.turns[].free_text):
  turns mentioning 'light(s)': 36; lights-as-EVENT phrasing: 17
  by role: {'CREWMATE': 9, 'IMPOSTOR': 8}; 17 distinct games
  in games with ZERO sabotage: 16; the 17th is samples/9p2i seed 27 (reactor only). EXACT REPRODUCTION of every number.
  co-mention of 'sabotag' in those 17 turns: 0

[3] WHY THE READING IS WRONG -- the phrase is anchored to the KILL, verified against engine kill actions:
  samples/9p2i s47 m0, p-1 (IMPOSTOR): "p-4, you were the last one with p-3 in East Hall before the lights went out"
     -> kills<=t7: [(5,'p-3','p-1'), ...]. p-1 is describing the death of p-3, whom p-1 killed himself.
  ml_corpus/9p2i s1141 m0, p-2 (IMPOSTOR): "I was in Admin with p-3 right before the lights went out"
     -> kills<=t8: [(4,'p-5','p-8'), (6,'p-3','p-2')]. Again the speaker's own victim.
  samples/9p2i s11 m1, p-5 (CREWMATE): "p-9 was ... right next to poor p-1 when the lights went out"
     -> kills<=t13 include (11,'p-1','p-7'). The phrase = p-1's death.
  Explicit victim/scene anchors elsewhere: "the lights went out ON him" (s1081), "ON p-4" (s1129), "ON p-2" (s1144), "the victim before the lights went out" (s1103), "close to the kill zone when the lights went out" (s1128), "hanging around the crime scene when the lights went out" (s1006), "suspiciously close to the crime scene right before the lights went out" (s1140).
  Only 2 of 17 are not past-kill references, and both are hypothetical/future (s1087 "I don't want to be here when the lights go out"; s1124 "a man don't need a vent to slip away when the lights go out").

[4] "THE NONEXISTENT LIGHTS SABOTAGE" IS FACTUALLY WRONG:
  engine/maps/canonical_1.yaml:387-392 defines `lights:` (affected_visibility same_room_only, repair_rooms [ADMIN], duration_ticks 90, repair_ticks 3); engine/world.py:115 `lights_sabotage: VisibilityMode`; engine/visibility.py:114 and engine/tick.py:81 both branch on it; agents/tactical/crewmate_policy.py:393-394 explicitly keeps lights-era crew behavior byte-identical.
  Its absence from the corpus is SPECIFIED, not an accident: agents/tactical/impostor_policy.py:218 `_REACTOR_SABOTAGE_KIND: Final[str] = "reactor"` with the comment "``reactor`` is the only ``gates_tasks: true`` kind in the canonical map" -- the only kind the policy ever emits. So the corpus can contain no lights sabotage by construction.
  The reactor detail DOES check out: canonical_1.yaml:394-400 gives reactor `affected_visibility: same_room_and_adjacent`.

[5] CAMERA SCAN -- this half is sound and is the finding's real content:
  4 turns, 3 distinct games, {'CREWMATE':3,'IMPOSTOR':1}. EXACT REPRODUCTION.
  s47 p-1 (IMP): "I was just heading to Admin to check the cameras"
  s1008 p-5 (CREW): "p-4 is innocent because I have them on camera"
  s1058 p-2 (CREW): "I have the killer on camera" -> s1058 p-4 (CREW): "I suppose we should trust the one with the camera" (propagation confirmed)
  `grep -rniE "camera|surveill|cctv|footage" engine/ meetings/ observation/ agents/` -> 0 hits. The mechanic genuinely does not exist.
  The s1058 sub-claim checks out: roles show p-7 IMPOSTOR; tick actions t6 vent STORAGE_VENT, t7 vent ENGINEERING_VENT; the meeting-0 contradiction reads "p-2 witnessed p-7 vent in ENGINEERING at tick 8". Genuine vent, camera was decoration.

[6] NEGATIVE SCANS -- all reproduce: blackout 0, oxygen/O2 0, comms 0, meltdown 0, power 0, security 0, door log 0, medbay scan 0, admin tablet 0, 'moved the body' 0, vitals 2 (both the adjective).

[7] CONTAINMENT -- reproduces exactly:
  ballots 3,602 | with fabricated-mechanic vocabulary in rationale_text: 0
  vent_sighting contradictions 448 | naming a subject who actually emitted a `vent` action in that game: 448 | unbacked: 0

[8] KNOWN-OPEN CHECK -- the lights half is a re-report:
  audits/review-2026-08-19/A/collated-findings.md:493 (under G-40, P2, corrob 5): "**Related wording bug.** Agents reference 'when the lights went out' in games with no lights sabotage (s36, 1089, 1008) -- a figure of speech that reads as a hallucinated event."
  audits/audit-phase-20-close.md:446 carries the same line in the G-40 row.
  audits/review-2026-08-19/D/cross-track-map.md:110 maps G-40 to C-115 with "110 sabotages, 100% reactor, 0 lights ever".
  G-40 is on the balance-wave backlog named in the brief. No prior audit mentions the camera fabrication (grep 'camera' over audits/review-2026-08-19/ and audits/audit-phase-20-close.md -> 0 hits), so that half is new.

[9] CLASSIFICATION CHECK -- free_text confabulation is an acknowledged, deferred risk, which supports 'acceptable-emergent': DESIGN.md:939 "**Hallucination:** an agent may 'remember' things that did not happen. Mitigation: the structured output schema requires `tick` references ... a code-level validator ... is **deferred** (not present at HEAD)." The mitigation is scoped to structured observations; free_text is deliberately unvalidated.
```

**Verifier note.** Evidence reproduces to the digit -- 17/17 lights turns with the exact 9/8 role split and the 16-zero-sabotage/1-reactor split, 4 camera turns in 3 games with the 3/1 role split, all ten negative scans at 0, 0/3602 ballots, 448/448 backed vent contradictions. Three things must change. (1) The lights half is a duplicate of known-open G-40's recorded 'Related wording bug', which the prior audit already read MORE accurately than this finding does. (2) The reading is wrong: 'the lights went out' is the standard noir euphemism for the moment of a kill -- I verified against engine kill actions that in s47 and s1141 the IMPOSTOR uses it about the victim he himself killed, and 11 more carry explicit victim/crime-scene/kill-zone anchors; 0 of 17 co-mention sabotage or a repair room. So 'assert a lights event', '17/17 describe an event that never occurred', and the title's 'narrate station events that never happened' overstate what the bytes show. (3) 'the nonexistent lights sabotage' is simply false -- `lights` is a fully specified map kind (canonical_1.yaml:387) that four engine/agent modules branch on; the corpus has zero of them because impostor_policy.py:218 hardcodes reactor as the only emitted kind. That makes fix_sketch item (1) ('add the map's actual sabotage vocabulary ... so the model has a real event to talk about') rest on a false premise. Fix_sketch item (2) (name the affordances that exist; no cameras) survives and is the finding's real payload, but it now rests on 4 turns in 3 games (0.11% of turns) rather than 21. Severity P3 stands; the novel content is the camera fabrication only.

**Fix sketch.** Nothing mechanical to fix. Two cheap mitigations: (1) add the map's actual sabotage vocabulary (kind + repair rooms) to the alarm memory line so the model has a real event to talk about instead of inventing one; (2) add one line to the crewmate/impostor prompt `<rules>` blocks naming the station affordances that exist (rooms, tasks, vents, the reactor alarm, the emergency button) and stating that no cameras, vitals, or door logs exist -- the prompts already carry an 'invented identifier fails validation' rule for the structured fields but nothing for free_text.

## A-47 — Emergency meetings are the clean control: the caller is also the opener, and is never convicted

**Severity:** P3. **Classification:** acceptable-emergent (measurement/control finding; no defect) -- but the control is confounded and the fix_sketch's numeric target is unsound. **Verdict:** ADJUSTED. **Area:** reporter-justice / control comparison. **Confidence:** high.
**Merged from:** reporter-justice#7: Emergency meetings are the clean control: the caller is also the opener, and is never convicted.

**Claim.** Every number reproduces, but emergency meetings are NOT a clean control for the opener effect and the stated conclusion does not follow. All 50 emergency meetings carry a vent_sighting contradiction (50/50), all 50 eject (50/50), and in all 50 the ejected player IS the vent subject -- because the emergency trigger fires only when a crewmate's private max suspicion crosses the §4.6 eject gate (agents/tactical/crewmate_policy.py:158-165, 403-407), i.e. only when the caller ALREADY holds role-proof against someone else. The caller's 0/50 conviction rate is therefore a mechanical consequence of the trigger condition, not evidence about the act of opening. Stratifying the body-report arm on the same variable dissolves the contrast: report meetings WITH a vent sighting (n=276) show reporter ejected 0/276 (0.0%), ballots-on-reporter 2.1%, accused>=2 15.9% -- statistically indistinguishable from the emergency arm (0/50, 2.4%, 8.0%); report meetings WITHOUT one (n=342) show reporter ejected 30/342 (8.8%), ballots 14.2%, accused>=2 65.2%. The reporter penalty is conditional on the ABSENCE of hard evidence, not on the reporting role, and the correct matched control is report-with-vent-sighting, not the emergency arm.

**As originally filed.** In the 50 emergency meetings the caller is likewise the compelled opener and speaks only once, yet draws >=2 accusers in just 4/50 (8%) and is ejected 0/50, so the reporter penalty attaches to the body-report role and not to the act of opening.

**Finder evidence.**

```
Same walk as finding 1, split on the tick action type of the trigger-er (`emergency` vs `report` in the tick record at the meeting's tick):
  by kind: {'report': 618, 'emergency': 50}
  EMERGENCY (50 meetings): caller accused>=1 39/50 (78.0%)  accused>=2 4/50 (8.0%)  caller EJECTED 0/50  ballots landing on the caller 7/290 (2.4%)
  BODY REPORT (618):       reporter accused>=1 508/618 (82.2%)  accused>=2 267/618 (43.2%)  reporter EJECTED 30/618 (4.9%)  ballots on reporter 278/3312 (8.4%)
  innocent ejections in emergency meetings: 0 (all 42 pooled innocent ejections are in body-report meetings).
The >=1-accuser rates are nearly identical (78% vs 82%) -- opening the meeting draws a first accusation either way. The >=2 rate differs 5.4x and the conviction rate goes from 0 to 30. What separates them is the body: an emergency caller has no proximity to narrate and nobody has a kill-site to place them at, so the accusation never coalesces.
Caveat recorded honestly: this is not a matched control -- emergency meetings occur in a different information state (no body anywhere), so the contrast bounds the opener effect rather than isolating the reporter effect. The within-meeting per-slot comparison in finding 1 (reporter vs innocent non-reporter at the same table, 7.46x, z=6.98) is the isolated measure.
```

**Verifier evidence (independent re-run).**

```
Independent derivation from the committed JSONLs. Meeting kind = the action type of `triggered_by` in the tick row at the meeting's tick (the meeting row itself stores only `triggered_by`, a player id). 668/668 meetings resolved at their own tick, 0 unresolved.

  by kind: {'report': 618, 'emergency': 50}                                        <- EXACT

  Accused = a distinct other speaker filing a structured `accusation` claim with against == caller.
  emergency  n=50   acc>=1 39 (78.0%)  acc>=2  4 ( 8.0%)  caller EJECTED  0 (0.0%)  ballots-on-caller   7/ 290 (2.4%)
  report     n=618  acc>=1 508 (82.2%) acc>=2 267 (43.2%) caller EJECTED 30 (4.9%)  ballots-on-caller 278/3312 (8.4%)
  -> EVERY figure in the finding reproduces to the decimal.

  Ejection split by role (roles from eval.validity.roles_by_seed, cross-checked against prompt personas, 1699 pairs / 0 mismatches):
  total ejections 429 | innocent (CREWMATE) ejections 42, ALL 42 in report meetings, 0 in emergency  <- EXACT

  THE CONFOUND (my own addition):
  emergency outcomes: {'EJECTED': 50}      ejected-role: {'IMPOSTOR': 50}    caller-role: {'CREWMATE': 50}
  report    outcomes: {'EJECTED': 379, 'SKIPPED': 239}  ejected-role: {'IMPOSTOR':337,'CREWMATE':42,None:239}
  -> the emergency arm converts at 100% AND is correct 100% of the time. That is not a control; it is a deterministic hard-evidence channel.

  vent_sighting presence per meeting:
  emergency: meetings 50  has_vent_sighting 50  ejected 50  ejected==vent_subject 50
  report:    meetings 618 has_vent_sighting 276 ejected 379 ejected==vent_subject 276

  STRATIFIED COMPARISON (the matched control the finding should have used):
  EMERGENCY (all have vent sighting)   n=  50  acc>=1 78.0%  acc>=2  8.0%  callerEJ  0 (0.0%)  ballots  7/ 290 ( 2.4%)
  REPORT with vent sighting            n= 276  acc>=1 75.0%  acc>=2 15.9%  callerEJ  0 (0.0%)  ballots 33/1588 ( 2.1%)
  REPORT without vent sighting         n= 342  acc>=1 88.0%  acc>=2 65.2%  callerEJ 30 (8.8%)  ballots 245/1724 (14.2%)

  MECHANISM, from source (so this is SPECIFIED behaviour, not an artifact):
  agents/tactical/crewmate_policy.py:157-165 -- `EmergencyButtonView.is_eligible` requires `over_gate` (private max suspicion at or above the §4.6 eject gate, DEFAULT_SKIP_CONFIDENCE_THRESHOLD) AND `crossed_since_meeting` AND `call_available` AND `cooldown_remaining == 0`.
  agents/tactical/crewmate_policy.py:403-407 -- the emergency walk fires only under that gate, and BELOW the body-report and witnessed-kill interrupts (lines 377-386), so an emergency meeting is by construction a no-body, gate-crossed meeting.
  All 67 recorded emergency actions carry payload {'reason': 'suspicion_accumulation'} (0 'kill_witnessed'), confirming this is the suspicion-gate path.

  Note also: the finding's stated mechanism -- "an emergency caller has no proximity to narrate and nobody has a kill-site to place them at" -- is at best secondary. Report-with-vent-sighting meetings DO have a body and a kill site and still convict the reporter 0/276.
```

**Verifier note.** All eight headline figures and the innocent-ejection split reproduce exactly, and the finding does record an honest caveat -- but it names the wrong confound and understates it by a wide margin. The caveat says the arms differ by 'information state (no body anywhere)'; the actual difference is that the emergency trigger is gated on the caller having already crossed the ejection-confidence threshold on another player, which makes the emergency arm a 50/50 witnessed-vent conviction channel in which the caller is definitionally not the target. Once evidence state is controlled, the body-report opener is exactly as safe as the emergency caller (0/276 vs 0/50; 2.1% vs 2.4% of ballots), so the claim's conclusion -- 'the reporter penalty attaches to the body-report role and not to the act of opening' -- is not supported by this contrast: the penalty tracks the absence of role-proof evidence, and the 5.4x acc>=2 gap the finding attributes to the body is 15.9% vs 65.2% within the report arm alone. The fix_sketch must change too: 'the target is the body-report >=2-accuser rate falling from 43.2% toward the emergency caller's 8%' sets an unreachable goal, since 8% is what a table looks like when someone already holds a vent sighting; the reachable target is the 65.2% no-hard-evidence stratum falling toward the 15.9% with-vent-sighting stratum. Severity P3 and the acceptable-emergent classification stand (this is a measurement finding, not a defect), and the confidence should drop from 'high' to 'medium' on the causal clause. Not a duplicate of any listed backlog item, though it is a companion analysis to prior-audit G-31 ('Reporter-blame is the default deflection, and it works', P1, corrob 8, audits/review-2026-08-19/A/collated-findings.md:395), which is not on the brief's known-open list.

**Fix sketch.** No fix; record as the control the reporter-justice gauges should be read against. If a future record adds an exculpation to the accusation round, the target is the body-report >=2-accuser rate falling from 43.2% toward the emergency caller's 8%, with the >=1 rate expected to stay near 80% (a first challenge to the opener is healthy).

## A-48 — Raw engine room identifiers (EAST_HALL / WEST_HALL) spoken verbatim in 6.7% of turns

**Severity:** P3. **Classification:** acceptable-emergent (cosmetic register leak) -- unchanged; only the origin mechanism is corrected. **Verdict:** ADJUSTED. **Area:** transcript.turns[].free_text, all 4 sets; taught by accusation_round.j2 transcript render and <map> card. **Confidence:** high.
**Merged from:** dialect-leaks#6: Raw engine room identifiers (EAST_HALL / WEST_HALL) spoken verbatim in 6.7% of turns.

**Claim.** The count is exact: 240 of 3,602 spoken turns (6.7%) across 120 of 300 games contain a raw underscore room id (EAST_HALL / WEST_HALL; UPPER_HALL adds none), split ml_corpus/9p2i 141, samples/9p2i 75, ml_corpus/4p1i 14, samples/4p1i 10. The CAUSAL clause is wrong. Agents are not short of a prose spelling: 3,400 of the 7,211 recorded prompts already contain 'East Hall' / 'West Hall' / 'Upper Hall' (echoed into the <transcript> block from other agents' free_text), and the model uses the prose form in 858 turns versus 240 raw -- it prefers prose 3.6 to 1. The correct statement is that no AUTHORED surface offers a prose spelling (the templates and map card render ids only), so the register is unanchored and the model mixes the two, leaking the id in 6.7% of turns. A prose name per room already exists in data (`name: East Hall` in engine/maps/canonical_1.yaml, loaded as `engine.world.Room.name`), so the fix sketch's 'add a display-name mapping' is wiring an existing field, not inventing one.

**As originally filed.** Players say the engine's underscore room identifiers out loud -- "I was in EAST_HALL at tick 16" -- in 240 of 3,602 spoken turns across 120 of 300 games, because every surface the agent reads renders rooms as raw ids.

**Finder evidence.**

```
$ uv run python - (regex \b(EAST_HALL|WEST_HALL)\b over transcript.turns[].free_text, case-sensitive
  so prose "East Hall" is excluded)
  free_text turns containing a raw underscore room id: 240/3602 = 6.7%
  distinct games: 120
  by set: ml_corpus/9p2i 141, samples/9p2i 75, ml_corpus/4p1i 14, samples/4p1i 10

  [samples/9p2i s0 p-1] "I found p-2 dead in STORAGE at tick 17. I saw p-5 move from ENGINEERING to
                         EAST_HALL at tick 16, placing them right next to the kill zone..."
  [samples/9p2i s0 p-5] "Wait, hold on, I was literally in EAST_HALL at tick 16, not even near the kill site..."
  [samples/9p2i s1 p-8] "I found p-4 dead in ADMIN at tick 8. I saw p-7 walk into ADMIN from EAST_HALL at tick 7."

ORIGIN, again the template: accusation_round.j2 renders every observation with the bare id
(`- tick {{ obs.tick }}: {{ obs.subject }} in {{ obs.room }}`), the `<map>` card publishes the raw
adjacency, and the output schema asks for `"room": "<room id>"`. Nothing anywhere shows the agent a
prose form of a room name, so the id is the only spelling it has. Note the same turns freely mix
registers -- the seed-0 p-1 quote says "STORAGE" and "ENGINEERING" in caps but "kill zone" in prose.

I am reporting this as cosmetic and acceptable rather than a defect: it does not misrepresent any
evidence, it does not break the deduction, and downstream normalization already handles it
(eval/vj_instruments.py `_room_pattern` matches room names case-insensitively, so the skeleton fold
is unaffected). It is a watchability/immersion blemish that a human reader notices, on a surface a
fitted model will reproduce.
```

**Verifier evidence (independent re-run).**

```
Independent scan of transcript.turns[].free_text across the 300 committed replay JSONLs (not the auditor's dump).

  case-sensitive \b(EAST_HALL|WEST_HALL)\b over 3,602 turns:
    hits 240 / 3602 = 6.66%   distinct games 120 / 300
    by set: ml_corpus/9p2i 141, samples/9p2i 75, ml_corpus/4p1i 14, samples/4p1i 10   <- EXACT on all four
    by role: CREWMATE 174, IMPOSTOR 66
    adding UPPER_HALL changes nothing (still 240)
  The three quoted examples reproduce verbatim, e.g. samples/9p2i s0 p-1: "I found p-2 dead in STORAGE at tick 17. I saw p-5 move from ENGINEERING to EAST_HALL at tick 16, placing them right next to the kill zone..."

  ORIGIN -- the template half of the claim CHECKS OUT. The corpus was recorded with prompt set qwen3_6_27b v4 (all 668 meetings; model Qwen/Qwen3.6-27B, 7,211 calls):
    agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:128  `- tick {{ obs.tick }}: {{ obs.subject }} in {{ obs.room }}...`
    :244-251  output schema asks for `"room": "<room id>"` on all seven observation/claim types
    `PYTHONPATH=. uv run python -c "from agents.strategic.prompts.loader import CANONICAL_MAP_CARD; print(CANONICAL_MAP_CARD)"` ->
      "- ADMIN: EAST_HALL, UPPER_HALL, WEST_HALL" ... all ten rooms as raw ids (loader.py:371-380, 404).
    `grep -rn "East Hall|West Hall|Upper Hall" agents/ meetings/ --include=*.j2 --include=*.py` -> 0 hits. No authored surface renders prose. CONFIRMED.

  ORIGIN -- the "only spelling it has" half is REFUTED:
    prompts containing a PROSE hall name: 3400 / 7211;  containing a RAW id: 7211 / 7211
    Sampling where the prose sits: always inside the quoted <transcript> block, e.g. p-9's prompt in samples/9p2i seed 0 carries `- [headless-seed-0:meeting-0:turn-6] turn 6 (opt_in) - p-8: ... I was in West Hall watching p-7 move to Admin ...`. So the prose spelling reaches the agent on every turn after the first, from its own peers.
    turns using a PROSE hall name: 858;  turns using a RAW id: 240;  both in the same turn: 4.
    Prose is the MAJORITY register by 3.6x, which is the opposite of "the id is the only spelling it has".
    A prose name also exists in the map data: engine/maps/canonical_1.yaml rooms carry `name:` (`CAFETERIA: name: Cafeteria`, `UPPER_HALL: name: Upper Hall`, ...), modelled as `engine/world.py:118-120 class Room: id / name`. It is simply never surfaced by loader.py or the templates.

  DOWNSTREAM-HARMLESS CLAIM CHECKS OUT (in the direction reported): eval/vj_instruments.py:680-688 `_room_pattern` builds a word-boundary alternation over `load_canonical_map().rooms` (the ids) with `re.IGNORECASE`, so a spoken raw id folds fine. (Worth noting the asymmetry: the prose form 'East Hall' does NOT match that pattern -- but that is the majority register, not the reported one, and outside this finding's scope.)

  SPECIFIED CHECK: the raw-id map card is contractually specified -- tasks/phase-20.md:5072 (Task 20.31 DoD): "The map card renders ... as at most twelve lines from `PublicMapView.room_neighbors` over the ten walkable rooms". So the input surface is intended; only the speech register is emergent, which supports the acceptable-emergent classification.

  KNOWN-OPEN CHECK: not a duplicate. The prior audit quotes raw ids in speech all over (audits/review-2026-08-19/A/w2-9p2i-featured-b.md, s3-meeting-decisions.md, verdicts.md:243) but never files it as a finding; the nearest items are G-25 (dev audit markers spliced into free_text, P1) and G-29 (threshold arithmetic / stock rationales, P2) under the RC5 'private dialect leaks to every surface' theme (audits/review-2026-08-19/D/cross-track-map.md:295-304). Raw room ids are a new instance under that umbrella, and G-25/G-29 are about different strings.
```

**Verifier note.** The measurement is exact -- 240/3602 = 6.66%, 120 games, and all four per-set counts match to the unit, with the three quoted examples verbatim. The template-origin half is also confirmed (accusation_round.j2:128 renders `{{ obs.room }}` bare, the map card is ten lines of raw ids, the schema asks for `<room id>`, and no .j2 or .py authors a prose room name). What must change is the causal sentence 'Nothing anywhere shows the agent a prose form of a room name, so the id is the only spelling it has'. It is false twice over: 3,400 of 7,211 recorded prompts carry 'East Hall'/'West Hall'/'Upper Hall' -- echoed back through the transcript block from peers' own free_text -- and the agents themselves use the prose form in 858 turns against 240 raw, a 3.6:1 preference. The right framing is a register that no authored surface anchors, so the model drifts between two spellings and leaks the engine one 6.7% of the time; the same turns mixing 'STORAGE' with 'kill zone' is that drift, not a vocabulary gap. Two smaller corrections: a per-room prose `name` already exists in engine/maps/canonical_1.yaml and `engine.world.Room.name`, so the fix sketch means 'surface an existing field', which makes it cheaper than described; and the raw-id map card is a deliberate Task 20.31 DoD item (tasks/phase-20.md:5072), not an oversight. Severity P3, the acceptable-emergent classification, the containment reasoning and the 'do not bump standalone' fix advice all stand.

**Fix sketch.** If it is judged worth a prompt bump at all, ride it on the same combined re-record as the dialect fix: add a display-name mapping (EAST_HALL -> "the East Hall") for the PROSE renders in the transcript block and the <map> card while keeping raw ids in the schema block and the output contract, so the model has a prose spelling available without loosening validation. Do not do this as a standalone bump -- the cost/benefit does not carry a version cascade on its own.

---

## Coverage notes (the finders' own, attributed)

```
==============================================================================
COVERAGE NOTES AS FILED BY FINDER: ballots-vs-speech
==============================================================================

EXAMINED. All 4 committed sets, all 300 replay-seed-*.jsonl, all 668 meetings, all 3,602 recorded ballots and all 3,602 transcript turns (turns == ballots exactly, per set: 871/2479/120/132, matching each report's published turns_total and ballots_total — every living participant speaks exactly one turn and casts exactly one ballot), joined ballot-by-ballot to (i) the voter's own spoken accusation claims, (ii) the meeting's full accusation set, (iii) the meeting's contradiction flags, (iv) the voter's own recorded vote PROMPT out of the meeting's llm_calls (rendered max-suspicion line and [obs ...] availability), and (v) ground-truth roles re-derived per seed via orchestrator.seeder.seed_initial_state + each set's roster.json. The join was validated two ways before any claim was drawn: it reproduces every published deduction.turn_ballot_consistency cell exactly (404/276 + 1158/792 + 51/57 + 59/59, rates 0.5372/0.5480/0.4554/0.4797), and an independent re-tally under meetings/voting.py rules reproduces the recorded ejectee/SKIP in 668/668 meetings. Guard markers were unwound to the authored target (meetings/manager.py:200/211/274/354) and the unwind cross-checked against the repo's own documented example (api/replay_loader.py:249, samples/9p2i seed 22). 26 accuse-then-SKIP turn/ballot pairs were read in full across all four sets (task asked for 20+), plus 14 never-accused-target ballots, 20 role-leak hits hand-classified for precision, and three meetings read end-to-end (samples/9p2i seed 2 m0, ml_corpus/9p2i seed 1085 m0, samples/9p2i seed 0 m0). Prompts read in full: agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2 and accusation_round.j2. Code read: meetings/voting.py tally, meetings/manager.py marker block, eval/deduction_metrics.py TurnBallotConsistencyCells, training/surrogate/dataset.py + ballots.py, api/replay_loader.py marker/label registration. NOT EXAMINED. The roll-call prompt variants (impostor_roll_call / accusation_round_roll_call) — the impostor_roll_call flag is OFF in these bytes, so they are unexercised. Turn free_text fidelity against the engine event stream (whether a spoken claim is TRUE) — that is the honesty dimension, not ballots-vs-speech; I checked only whether a cited turn is topically related to the ballot target (1868/1868 clean). Non-accusation claim types (alibi, corroboration) were not scored against ballots. The frontend/spectator rendering was not opened — I read api/replay_loader.py's marker registration only, and I did not verify what a viewer actually sees. Per the ground rules I ran no test suite, no campaign marks, and no scripts/check.sh; the offline counterfactual harness (training/, audits/audit-phase-20-counterfactual.md) was read but not run. Baseline 7 is canon by explicit owner override of a FINDING verdict (pre-registered bars 1 and 2 missed — bar 1 by 0.0078); nothing here revisits that. Known-open items were not re-reported: I deepened exactly two with new baseline-7 quantification and said so in place (the 42 pooled innocent ejections; the 4p1i second act / G-43, via the all-skip meeting rate).

==============================================================================
COVERAGE NOTES AS FILED BY FINDER: reporter-justice
==============================================================================

SCOPE EXAMINED. All four committed baseline-7 byte sets: replays/samples/9p2i (50 games), replays/ml_corpus/9p2i (150), replays/samples/4p1i (50), replays/ml_corpus/4p1i (50) = 300 games, 668 meetings, of which 618 are body reports and 50 are emergency calls; 16 games contain no meeting. Meeting kind and the reporter's identity were derived from the tick record's own action stream (an action of type 'report' or 'emergency' by the meeting's triggered_by at the meeting tick), not from prompt prose. Roles were derived from the '## Your role: IMPOSTOR' / '## Your role: CREWMATE' marker inside the recorded llm_calls prompts; sanity check passed exactly (200/200 9p2i games show 2 impostors, 84/84 4p1i games with meetings show 1, 16 4p1i games have no meetings and so no role evidence -- those contribute no meetings and no ejections). Independent cross-check: the derived innocent-ejection total is 42, matching the recorded pooled number, and all 42 fall in body-report meetings.

WHAT I READ VERBATIM. Full transcripts + ballots + engine contradiction arrays for samples/9p2i seed 24 meeting-1, ml_corpus/9p2i seed 1135 meeting-0, samples/9p2i seed 39 meeting-0, plus the complete prompt scaffolding (persona / voice / turn header / <memory> / <transcript> / <accusation_against_you> / rules) for a reporter, a replier, and a voter in seed-24 meeting-1. Also read agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2 (the exculpation block), meetings/manager.py:1750-1850 (the reporter_id derivation and its single threading site), engine/rules.py:191-208 (resolve_report), agents/tactical/impostor_policy.py:40-80 and :1505-1535 (the COVER doctrine), agents/tactical/crewmate_policy.py:740, agents/tactical/learned/crew_forward.py:104-125 and :1088.

WHAT I DID NOT EXAMINE. I did not run any test, scripts/check.sh, or any campaign marker (a gate run was in progress). I did not re-derive the instrument folds in tournament-eval-report.json or run eval/ -- every number here comes from a direct walk of the replay JSONL and the prompts embedded in it, so none of it depends on the instruments being correct. I did not attempt to re-record or re-simulate anything; all claims are about the committed bytes at rest. I did not analyse the 12 non-reporter innocent ejections beyond identifying the 3 body co-discoverers among them (the remaining 9 are outside this dimension). I did not investigate the impostor's own kill-cover behaviour, sabotage, vent tells, task pacing, meeting cadence, or 4p1i second-act structure except where a reporter statistic required the split -- 4p1i contributes only 2 of the 42 innocent ejections and is thin for this dimension. I made no claim about whether reporter_exculpation should be a lever again; the flag is unconditional and I treated it as fixed.

KNOWN-OPEN ITEMS TOUCHED. Findings 1, 2, 5 and 6 are new baseline-7 quantification of the known-open lead G-31, and finding 1 also supplies the HOW behind the recorded 42-innocent-ejection number, which was previously recorded only as a count. I deliberately did not re-report the declared production-side duplicate alibi_vs_sighting mint (it appears in my contradiction census -- 2 of the 4 reporter-flagged meetings carry an alibi_vs_sighting -- and I treated it as declared), G-29 stock rationales, G-37 the +1 agent clock, C-88 fake-provider meeting degeneracy, or any balance-wave backlog item.

STANDING CONTEXT I RELIED ON. Baseline 7 is canon by explicit owner override of a FINDING verdict (pre-registered bars 1 and 2 missed -- bar 1 by 0.0078). 22 substrate flags, 21 unconditional, impostor_roll_call the only live toggle and OFF; every game_over record in the four sets carries reporter_exculpation: true. Prompt set qwen3_6_27b v4, recorded model Qwen/Qwen3.6-27B.

SCRATCH. All working scripts under /private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/8c686913-6a30-43ad-8ed2-a35d8125a233/scratchpad/wave0/A/rj/ (namespaced; the shared wave0/A directory had filename collisions with other finders, which is why my files carry the rj_ prefix). No tracked file was created or modified.

==============================================================================
COVERAGE NOTES AS FILED BY FINDER: herding-calibration
==============================================================================

EXAMINED. All four committed sets end-to-end (replays/samples/9p2i 50 games / 152 meetings / 871 ballots; replays/ml_corpus/9p2i 150 / 432 / 2479; replays/samples/4p1i 50 / 40 / 120; replays/ml_corpus/4p1i 50 / 44 / 132), read directly from the replay JSONL rather than the report fold. Role ground truth was reconstructed per game from tick actions (kill/vent/sabotage) plus the 'Secret: you are the saboteur' persona line in the recorded llm_calls prompts; it resolves to exactly the expected impostor count in 200/200 9p2i games and 93/100 4p1i games (the 7 misses are games where the impostor never acted and never spoke, and carry no ballots I scored). My harness reproduces the four committed ECE cells to 4+ decimal places (accusation 0.3003/0.2817, ballot 0.1498/0.0922) and the committed redirected-ballot count (36 on samples/9p2i), which is the validity check for everything else here. Also read: eval/accusation_calibration.py, meetings/voting.py (tally rules, re-implemented for the counterfactual), meetings/manager.py guard_ballot_target_graph / guard_ballot_citation / the teammate-firewall call sites, meetings/transcript.py grounding constants, meetings/schemas.py SawVentObservation, and the served qwen3_6_27b accusation_round / accusation_round_roll_call / crewmate_report / impostor_report templates.

NOT EXAMINED. (a) The eval instruments' own code paths beyond accusation_calibration and the deduction cells I cross-checked -- I did not run any instrument, only re-derived its numbers. (b) The suspicion-graph VALUES the redirect guard selects on: they are not in the replay bytes, so I could only verify the redirect's recorded effect, not that its chosen argmax was the right one. (c) Belief-update internals in agents/memory -- I read the spoken/recorded surface only, so 'parroting vs updating' is argued from observation provenance and lexical overlap, not from the agents' internal state. (d) 4p1i got structural coverage (regime split, vent verification, innocent ejections) but its meeting counts are too small for the turn-index and cascade analyses, so those findings are stated on 9p2i only. (e) I did not run pytest, campaign marks, or scripts/check.sh, per the ground rules. (f) I did not attempt to attribute any finding to a specific substrate flag by toggling it -- all 21 unconditional flags were on for every byte I read, and impostor_roll_call was off.

DELIBERATELY NOT RE-REPORTED as new: the balance-wave backlog (G-5, G-15, G-13, G-8, G-22, G-40, G-43), G-29, G-37, C-88, the duplicate alibi_vs_sighting mint, and the 42-innocent-ejection count. Two findings deepen known-open items and say so in their claim text: the 42 innocent ejections (new: the HOW breakdown) and G-8 (new: the saw_vent laundering count and its ungrounded-adoption consequence).

==============================================================================
COVERAGE NOTES AS FILED BY FINDER: impostor-behavior
==============================================================================

EXAMINED. All four committed sets end to end (replays/samples/9p2i 50 games, replays/ml_corpus/9p2i 150, replays/samples/4p1i 50, replays/ml_corpus/4p1i 50 = 300 games, 668 meetings, 3,602 transcript turns, 3,350+ recorded llm_calls with full prompts and raw response_text). Role labels joined from each set's tournament-eval-report.json `report.games[].roles`; my crew-ejection recount (42 pooled) matches the recorded 42, and my per-set whereabouts counts reproduce the shipped `deduction.public_response_coverage` cells exactly, which is the sanity anchor for every count in this report. Ground truth for locations was taken two independent ways and cross-checked: the engine's rendered 'Your route (t = tick): ...' line inside each agent's own meeting prompt, and a from-scratch replay of the tick action stream (start CAFETERIA, apply move/vent, vent_id -> room by stripping _VENT). Sub-questions covered: (a) whereabouts dodging quantified per set and per turn-kind, traced to accusation_round.j2 and the OFF impostor_roll_call lever, tested for crew exploitation both lexically (2,674 crew turns, 1,391 crew ballots against omitters) and statistically (matched unflagged meetings), and traced to the vote-render/memory mechanism that makes exploitation impossible; (b) deflection content characterised for templating, groundedness against engine truth, and lie placement; (c) self-incrimination scanned over free_text + claim.reason + claim.evidence with the repo's own phrase nets plus vent/cooldown nets, and the two real confessions verified against the tick records and against the exact prompt bytes the voters received.

NOT EXAMINED / LIMITS. I did not re-run any repo evaluator, test, or gate (a gate run was in progress); every number here is from stdlib walks over the committed JSONL and the committed reports. I did not attempt a causal identification of whether accusation-round listeners (as opposed to voters) read the missing 'saw:' block - the reply chain follows whoever is accused, which confounds any within-meeting ordering test, so finding 3's exploitation claim rests on the ballot-surface mechanism and the null lexical scan rather than on a clean experiment. My tick-anchored truth checks are conservative by construction (natural-language clause scoping), so the false-alibi and false-prose-alibi counts are lower bounds, not exact. I did not analyse impostor tactical play outside the meeting (kill target selection, vent routing, sabotage timing) except where it supplied ground truth, nor the 4p1i second act, nor sabotage - those sit in the balance-wave backlog. I deliberately did not re-report the known-open items named in the brief; finding 1 is flagged in-line as new quantification of the known-open G-22 asymmetry, and findings 2-5 are, to my reading, not among them.

==============================================================================
COVERAGE NOTES AS FILED BY FINDER: dialect-leaks
==============================================================================

SCOPE COVERED. All four committed sets (replays/samples/9p2i 50 games, replays/ml_corpus/9p2i 150,
replays/samples/4p1i 50, replays/ml_corpus/4p1i 50 = 300 games, 668 meetings). I extracted every
model-authored text surface in the meeting record into a single flat table of 11,727 utterances --
transcript.turns[].free_text (3,602), transcript.turns[].claims[].reason (4,523), and
ballots[].rationale_text (3,602) -- and swept all of it with ~30 regex classes: the machinery oracle
(engine/system/detector), evidence-jargon flag/flagged/flags, substrate, prompt, token, instrument,
threshold, score, metric, quoted suspicion decimals, impostor-only/impostor-exclusive, the three
evidence band names, certified, Jinja and XML delimiters, JSON and bare schema key names, turn-kind
vocabulary, markdown headers, observation/turn id forms, roll-call, raw room identifiers, and
generic bracketed annotations. Every candidate class was then hand-read in full before being counted
or discarded -- notably all 81 "engine" hits, which split 64 machinery-sense / 17 in-fiction (the
ship's engine room and the align_engine_output task), and all 16 "the system" hits.

For origin attribution I read all six prompt templates in agents/strategic/prompts/qwen3_6_27b/ end
to end, grepped them for the leak vocabulary, confirmed the flag-grouping predicate in
agents/strategic/prompts/loader.py (_ROLE_PROOF_KINDS = {"vent_sighting"}), pulled the actual
recorded prompt bytes out of llm_calls[].prompt to prove agents saw the taught string, and scanned
the <memory> blocks of recorded prompts across 15 corpus games to rule the memory render in or out
(it is out -- clean of the oracle vocabulary, carrying only the "suspicion N.NN" belief table). The
causal claim rests on a partition of all 668 meetings on flag presence, not on the sample.

I also read the shipped instruments that bear on this dimension -- eval/deduction_metrics.py
(MACHINERY_VOCABULARY, MACHINERY_DECIMAL_PATTERN, ScaffoldLeakageCells, player_visible_leak_turns),
eval/vj_instruments.py (_LEADING_MARKER_RE, _strip_leading_markers, _normalize_voice, _meeting_echo,
response_skeleton_share), meetings/manager.py and meetings/voting.py (the six pinned markers), and
training/surrogate/dataset.py (_ballot_is_coerced_skip) -- reproduced two of them against the bytes,
and read the recorded deduction.scaffold_leakage cells from all four tournament-eval-report.json.

KNOWN-OPEN ITEMS TOUCHED, and labelled as such in the findings: G-29 stock rationales, where the new
contribution is the per-surface split on baseline-7 bytes rather than the existence of the item.

NOT COVERED. I did not look at engine/, orchestrator/, or the tick-level action stream except to
establish the replay schema -- no gameplay-mechanics, balance, or win-condition analysis, which are
other finders' dimensions. I did not evaluate whether the observed leak changes any outcome beyond
the one cross-tab I ran (all 326 vent_sighting meetings eject the flagged venter, leak or no leak);
the 100%-conversion fact itself is a solvability/meeting-decides observation I am reporting only as
context for why the dialect sits on a certain-win path, and it deserves a look from whoever owns that
dimension. I did not check the frontend/spectator render of any of these surfaces beyond reading the
display contract in the manager.py comments. I did not run the eval fold, the test suite, or any
campaign marker, per the ground rules. I did not examine the non-qwen3_6_27b prompt sets except to
confirm the leak string is absent from them; they are not the recorded set for baseline 7. Finally,
my Tier-1 oracle net is a phrase net like the ones it critiques -- it is a lower bound on the true
leak, and paraphrases that name no machinery noun ("the record certifies", "the readout says") would
pass it; I did not attempt a semantic sweep.

==============================================================================
COVERAGE NOTES AS FILED BY FINDER: flow-edges
==============================================================================

WHAT I EXAMINED
Code read end to end: engine/tick.py (the DESIGN.md 3.1 seven-step loop),
engine/win_conditions.py, engine/rules.py (resolve_report / resolve_emergency_meeting /
resolve_sabotage / resolve_repair_sabotage / resolve_kill), engine/entities.py,
meetings/voting.py, orchestrator/action_ordering.py, and the flow-bearing parts of
orchestrator/game.py (apply_meeting_result, _run_loop, _run_and_apply_meeting,
_build_packets, _collect_intents, run) plus orchestrator/replay.py record_tick /
record_meeting / record_game_end.

Bytes: ALL 300 committed games (replays/samples/9p2i 50, replays/ml_corpus/9p2i 150,
replays/samples/4p1i 50, replays/ml_corpus/4p1i 50) were re-simulated through
eval.replay_walk.walk_replay with verify_tick_hashes=True and
verify_meeting_post_hashes=True; every walk reconstructed byte-identically, so all
per-tick numbers here are engine truth, not JSONL inference. 35,350 recorded actions
and 668 meetings / 3,602 ballots were classified. Scratch scripts live under
/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/8c686913-6a30-43ad-8ed2-a35d8125a233/scratchpad/wave0/A/
(scan.py, scan2.py, scan3.py, scan4.py, votes.py, conf.py, sab.py, margin.py,
case1.py, proof1.py, proof2.py, proof3.py). Three findings additionally carry a
deterministic engine-only construction (proof1/2/3) rather than only corpus counts.
No tracked file was modified; no test suite, campaign marker, or check.sh was run.

EDGES I CHECKED AND FOUND CLEAN (no finding filed)
- Win-condition ORDER: parity -> sabotage -> impostors-eliminated -> tasks matches
  the documented DESIGN.md 3.5 order (engine/win_conditions.py:22-63); the defect is
  the skipped call site, not the order.
- Tie handling: 668/668 meetings re-tally to their recorded outcome; the 2 genuine
  non-SKIP ties and the 27 SKIP-ties all resolve to SKIPPED per DESIGN.md 5.2.
- Dead players' turns and ballots: 0 ballots from a dead player, 0 living players
  without a ballot, across 668 meetings; _build_packets skips dead seats; a victim
  killed earlier in the same tick has its queued action rejected loudly
  ("player is dead", 4 instances). No zombie turns.
- Ejection resolution: 0 ejections of an already-dead player; ejected players mint no
  body; an ejection that reaches parity attributes IMPOSTOR_PARITY correctly (7 cases:
  samples/9p2i s46 t31, ml/9p2i s1032 t29, s1127 t38, s1137 t18, s1143 t40,
  samples/4p1i s39 t6, ml/4p1i s1021 t10).
- Meeting tick accounting: advance_tick does not increment the tick on the MEETING
  transition and apply_meeting_result increments exactly once, so a meeting consumes
  exactly one tick; the GameOverEvent tick matches on both the tick path and the
  meeting path; every game_over row's tick matches its last tick row.
- Repair/sabotage state hygiene: repair_progress is per-SabotageState and a new
  sabotage starts with an empty map, so no progress leaks between sabotages;
  resolve_repair_sabotage refuses an inactive sabotage; a completed repair cannot be
  overtaken by the countdown (active is cleared in step 1, before step 2 decrements).
- The 42 pooled innocent ejections reproduce exactly (ejected_role: 387 IMPOSTOR /
  42 CREWMATE over 429 ejections); I did not open the per-case "how" question, which
  is outside flow-edges.

WHAT I DID NOT EXAMINE
The +1 agent clock (excluded by the brief). Meeting internals: meetings/manager.py
and meetings/transcript.py (turn order, speaker selection, deadline defaults,
roll-call), the prompt bodies under agent_prompts/, and the agent memory / belief
fold (orchestrator/game.py _absorb_meeting_beliefs and agents/) -- I treated the
meeting as a black box that returns a MeetingResult. Perception and leak surfaces
(engine/visibility.py, observation/) were not audited beyond noting that a meeting
roster reveals a fresh death without a body report. Balance questions (kill
cooldown values, task pacing, sabotage tuning, the 4p1i second act) are out of
scope and left to the known-open backlog. eval/ instruments were used as tools
(replay_walk) but their fold logic (evidence_honesty, solvability, watchability,
vote_correctness, tournament-eval-report.json) was not audited.

==============================================================================
COVERAGE NOTES AS FILED BY FINDER: evidence-economy
==============================================================================

EXAMINED. All four committed sets (replays/samples/9p2i 50 games, replays/ml_corpus/9p2i 150, replays/samples/4p1i 50, replays/ml_corpus/4p1i 50 = 300 games, 668 meetings, 429 ejections, 3602 ballots), read through each set's tournament-eval-report.json (which carries roles ground truth, full transcripts, ballots, contradictions and llm_calls) and cross-checked against the raw replay-*.jsonl tick stream for ground-truth movement/vent reconstruction. Specifically: (a) recomputed the conviction-channel distribution behind all 429 ejections, split by ejectee role and by set; (b) read all 42 innocent ejections individually -- full transcript turns, observations, and every ballot rationale -- and produced the classified ledger in finding 7 (working dossier at /private/tmp/claude-501/.../scratchpad/wave0/A/innocent42.txt, per-ejection JSON at ejections.json, classified table at table42.txt); (c) tested whether deduction decides by comparing role_proof-flag subjects, weak-flag subjects, modal accusation target, first accusation target and reporter identity against the actual ejectee across all 668 meetings. Also verified the impostor no-report invariant against agents/tactical/impostor_policy.py, the vent-flag grounding contract against meetings/schemas.py, the redirect guard against meetings/manager.py, the reporter-exculpation lever against agents/memory/beliefs.py and agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2, and map adjacency against engine/maps/canonical_1.yaml plus the <map> card actually rendered into recorded prompts. Baseline 7 is canon by explicit owner override of a FINDING verdict (pre-registered bars 1 and 2 missed -- bar 1 by 0.0078); nothing in this audit reopens that. NOT EXAMINED. I did not run the eval instruments themselves (eval/evidence_honesty.py, solvability.py, watchability.py, replay_walk.py, vote_correctness.py) as programs -- per instructions I read their recorded folds out of the committed tournament-eval-report.json and only read the module source where I needed a definition (the role_proof/weak_signal taxonomy in eval/deduction_metrics.py, the roles contract in eval/vote_correctness.py and eval/report_schema.py); no test suite, no campaign marker, no check.sh. I did not analyse the 239 SKIPPED no-flag meetings for missed convictions (the 96 'missed skip' ballots the instrument fold records) -- that is the mirror-image question of what I was asked. I did not touch kill craft, task/clock economy, sabotage, watchability/voice, or the 4p1i second act beyond noting that its 2 innocent ejections fit the same reporter/boomerang shape; the 4p1i thinness itself is the known-open G-43. I deliberately did not re-report the known-open backlog items (G-5, G-8, G-13, G-15, G-22, G-29, G-37, G-40, G-43, C-88, the duplicate alibi_vs_sighting mint) as new; where the duplicate mint appears in my byte evidence (C9 1044 meeting-0 shows the same alibi_vs_sighting flag twice) I treated it as declared and did not count it as a separate flag instance in any rate. READ-ONLY: no tracked file was created or modified; all scratch output is under /private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/8c686913-6a30-43ad-8ed2-a35d8125a233/scratchpad/wave0/A/.

==============================================================================
COVERAGE NOTES AS FILED BY FINDER: legibility-pacing
==============================================================================

SCOPE. Track A, dimension legibility-pacing, over all four committed
baseline-7 replay sets (samples/9p2i 50, ml_corpus/9p2i 150, samples/4p1i 50,
ml_corpus/4p1i 50 = 300 games, 5,960 recorded ticks, 668 meetings, 3,602
transcript turns, 3,602 ballots, 7,211 recorded meeting prompts). Read-only; no
tracked file was created or modified; all scratch lives under
.../scratchpad/wave0/A/ (dump.py, dump.json, roles.json, witnessed.json,
halluc.json, kill_witness_followup.json).

METHOD. One reconstruction, reused for every finding: every seed re-seeded and
replayed through eval.replay_walk.walk_replay with verify_tick_hashes=True (0
reconstruction errors over 300 games), recording per tick the recorded actions,
the ENGINE event stream, alive set, rooms, bodies, sabotage state and task
counts, plus every meeting row verbatim including the full llm_call prompts.
Role ground truth from eval.validity.roles_by_seed. This lets every claim be
checked three ways -- submitted action, resolved engine event, and what the
agent was actually shown/said.

EXAMINED.
(a) Kill/vent/movement legibility: full memory-line shape census (1,379 distinct
    shapes over 7,211 prompts); the six turn observation shapes; witnessed-kill
    and witnessed-vent witness sets; the join from every spoken saw_vent to the
    engine vent that backs it; all 448 vent_sighting contradictions; the vent
    double-render; the +1 perception-tick convention verified against a pre/post
    state walk.
(b) Pacing: game-length distributions (p10/p25/median/p75/p90/max per set),
    meetings per game, time-to-first-kill (median 4.5-5.0, min 4 in every set),
    time-to-first-meeting, inter-meeting gaps, the dead-air share at the exact
    baseline-6 definition and one variant, per-role idle occupancy, idle-streak
    distributions and the corpus worst case, post-finish crew occupation, and
    undiscovered bodies at game end.
(c) Sabotage: every SabotageStarted/Repaired/RepairProgressed event, per-game
    clock traces for all 5 unrepaired sabotages, the map's sabotage definitions,
    the policy's reachable kinds, and the render of the alarm.
(d) Hallucinated events: regex scan of all 3,602 free_texts against 18 event
    vocabularies plus a containment check on all 3,602 ballots and all 448
    contradictions; and the structured-channel scan that produced the
    witnessed-kill-laundering finding.

NOT EXAMINED / OUT OF SCOPE HERE.
- I did not re-report the listed known-open items as new. Two findings
  explicitly DEEPEN known-open items with new baseline-7 quantification and say
  so in their evidence: G-8 (no speakable witnessed-kill shape) and G-15 (idle
  finished crew); the sabotage finding quantifies G-40 and then reports three
  things that note does not cover (the dead `lights` kind, the content-free
  alarm, the meeting refund of the clock). I did not touch G-5, G-13 (the vent
  peek enter/exit asymmetry -- my vent finding is about the double-render and
  the firewall residue, not the enter/exit split), G-22, G-43, G-29, G-37, C-88,
  the duplicate alibi_vs_sighting mint, or the 42 pooled innocent ejections as a
  number.
- Balance, win-rate, and conversion questions (another dimension's).
- The frontend/spectator renderer: I judged legibility from the committed bytes
  and the recorded prompts only, never from the viewer.
- Determinism/byte-identity beyond the tick-hash check the walk already did; I
  did not run scripts/check.sh, the full suite, or any campaign marker.
- The uncontested reporter gradient's root cause: measured and reported, not
  explained. Named as an honest limit inside that finding.
- Impostor-side deception quality (whether the fake-task alibi is spoken well),
  and the 4p1i second act beyond the pacing numbers, both known-open elsewhere.
```
