# Agent Prompt — 21.13 The mover scenario pin tells the truth about hunting

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.13 — The mover scenario pin tells the truth about hunting, anchored to F1's ninth failure — audits/audit-phase-20-close.md:89 (the F1 heading, "the campaign tier is RED at close HEAD (recorded, routed, not fixed)"), :96 (the one-scenario-pin bullet naming `tests/training/test_scenarios.py::test_kill_with_witness_fsm_hunts_elsewhere_and_earns_nothing`, its failing assertion `assert all(k.target != "p-5" for k in kills)` → False, the pre-dating evidence from scheduled CI run 32701066153 of 2026-08-24, and the attribution "It belongs to Task 20.32's mover repair, not to the recording") and :113 ("The one scenario pin is a separate, smaller item belonging to 20.32"); the Wave-0 register's own restatement of F1's identity at audits/review-2026-08-26/B/collated-findings.md:552 ("F1-F5 are the red campaign tier, two stale narrations, three word budgets, the audits-index ladder tip and the carried staging ref"); audits/audit-phase-20-baseline-7.md:728-745 §10.2, which routes the other eight failures and does NOT cover this one — no fit, no fingerprint and no corpus byte enters this test; docs/ml-program.md:118-126, the measured comparator defect this pin sat on top of ("the policy declines 190/415 = 45.8 % of its legal zero-witness kill opportunities, and 168 of those — 40.5 % of all free kills — are the defect: the kill seam re-validates only the top-ranked target"); anchors re-verified at HEAD 4002f19b — tests/training/test_scenarios.py:70 (`pytestmark = pytest.mark.campaign`), :85-99 (the `_run` helper the anchor uses), :167-175 (`test_injected_episode_is_deterministic_twice`, parametrized over `SCENARIO_LIBRARY` at seed 7), :433-444 (the failing anchor, assertion at :443), :447-457 and :460-474 (`_kill_once_selector` and the full-credit sibling), :477-482 (the no-kill sibling), :485-509 and :512-522 (`_snub_the_staged_victim_selector` and the unstaged-kill sibling), :545-554, :584-601 (the farm and pre-kill siblings); training/scenarios.py:255-256 (`_KILL_WITNESS_VICTIM = "p-5"`, `_KILL_WITNESS_ROOM = "LABS"`), :271-313 (the staged state: p-4 impostor and p-5 victim co-located in LABS, p-3 one doorway away in MEDBAY, `cooldowns={"p-4": 0}`), :316-381 (`_kill_with_witness_fitness`, the exactly-one-kill forfeiture clause at :371-380, the "under the default fake layer, which never ejects" note at :333-335), :384-414 (the spec, `staged_tick=40`, and the `does_not_reward` sentence on second kills at :404-406); agents/tactical/impostor_policy.py:451-482 (the repaired kill-emission seam, `_free_kill_target` called at :469 before `best = targets[0]` at :483) and :867-893 (`_free_kill_target`, whose docstring names 2026-08-19 review C-3: "Scanning the whole ranking rather than only its head is what stops a higher-scoring REMOTE lead from vetoing a kill standing in the room"); tests/training/test_rollout.py:51-62 and tests/training/test_rewards.py:448-461 (Task 20.32's own two re-pin precedents, each naming the mover repair and closing "No training code changed"); tests/training/test_suite_tiers.py:53-63 (`_CAMPAIGN_FILES` pins the FILE, not any test name) and :66-68 (`_MODULE_MARK_RE`); pyproject.toml:86 (`addopts = "--strict-markers -m 'not campaign'"`); engine/maps/canonical_1.yaml:34 (`kill_cooldown_ticks: 4`).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-mover-scenario`
**Depends on:** none (root)
**Section refs:** F1's ninth failure — audits/audit-phase-20-close.md:89 (the F1 heading, "the campaign tier is RED at close HEAD (recorded, routed, not fixed)"), :96 (the one-scenario-pin bullet naming `tests/training/test_scenarios.py::test_kill_with_witness_fsm_hunts_elsewhere_and_earns_nothing`, its failing assertion `assert all(k.target != "p-5" for k in kills)` → False, the pre-dating evidence from scheduled CI run 32701066153 of 2026-08-24, and the attribution "It belongs to Task 20.32's mover repair, not to the recording") and :113 ("The one scenario pin is a separate, smaller item belonging to 20.32"); the Wave-0 register's own restatement of F1's identity at audits/review-2026-08-26/B/collated-findings.md:552 ("F1-F5 are the red campaign tier, two stale narrations, three word budgets, the audits-index ladder tip and the carried staging ref"); audits/audit-phase-20-baseline-7.md:728-745 §10.2, which routes the other eight failures and does NOT cover this one — no fit, no fingerprint and no corpus byte enters this test; docs/ml-program.md:118-126, the measured comparator defect this pin sat on top of ("the policy declines 190/415 = 45.8 % of its legal zero-witness kill opportunities, and 168 of those — 40.5 % of all free kills — are the defect: the kill seam re-validates only the top-ranked target"); anchors re-verified at HEAD 4002f19b — tests/training/test_scenarios.py:70 (`pytestmark = pytest.mark.campaign`), :85-99 (the `_run` helper the anchor uses), :167-175 (`test_injected_episode_is_deterministic_twice`, parametrized over `SCENARIO_LIBRARY` at seed 7), :433-444 (the failing anchor, assertion at :443), :447-457 and :460-474 (`_kill_once_selector` and the full-credit sibling), :477-482 (the no-kill sibling), :485-509 and :512-522 (`_snub_the_staged_victim_selector` and the unstaged-kill sibling), :545-554, :584-601 (the farm and pre-kill siblings); training/scenarios.py:255-256 (`_KILL_WITNESS_VICTIM = "p-5"`, `_KILL_WITNESS_ROOM = "LABS"`), :271-313 (the staged state: p-4 impostor and p-5 victim co-located in LABS, p-3 one doorway away in MEDBAY, `cooldowns={"p-4": 0}`), :316-381 (`_kill_with_witness_fitness`, the exactly-one-kill forfeiture clause at :371-380, the "under the default fake layer, which never ejects" note at :333-335), :384-414 (the spec, `staged_tick=40`, and the `does_not_reward` sentence on second kills at :404-406); agents/tactical/impostor_policy.py:451-482 (the repaired kill-emission seam, `_free_kill_target` called at :469 before `best = targets[0]` at :483) and :867-893 (`_free_kill_target`, whose docstring names 2026-08-19 review C-3: "Scanning the whole ranking rather than only its head is what stops a higher-scoring REMOTE lead from vetoing a kill standing in the room"); tests/training/test_rollout.py:51-62 and tests/training/test_rewards.py:448-461 (Task 20.32's own two re-pin precedents, each naming the mover repair and closing "No training code changed"); tests/training/test_suite_tiers.py:53-63 (`_CAMPAIGN_FILES` pins the FILE, not any test name) and :66-68 (`_MODULE_MARK_RE`); pyproject.toml:86 (`addopts = "--strict-markers -m 'not campaign'"`); engine/maps/canonical_1.yaml:34 (`kill_cooldown_ticks: 4`).
**Complexity:** Small
**Record impact:** none — the change is confined to one campaign-tier test file. No production module, prompt template, detector or replay byte moves, so nothing here reaches 21.14's smoke or 21.15's re-record, and no committed replay, manifest or hash chain is touched. The one branch that WOULD carry record impact — repairing `agents/tactical/impostor_policy.py` — is explicitly refused below and escalated instead.
**Measurement:** `uv run pytest tests/training/test_scenarios.py -m campaign -q` is green — it reads `1 failed, 51 passed in 2.79s` at HEAD 4002f19b and must read all-passed afterwards (53 tests once the planted case lands). The PR also runs `uv run pytest -m campaign -q` and records its exit code and failure list verbatim: it still exits 1 on the EIGHT remaining F1 failures — three substrate-sha self-consistency pins and five corpus-derived fit pins, re-run at HEAD as `8 failed, 129 passed in 60.58s` over `tests/training/test_anchor_study.py`, `test_coevo_driver.py`, `test_composed_runner.py`, `test_surrogate_fidelity.py` — which are 21.17's, not this task's. Green means "the ninth is gone", never "the tier is green".

Phase 20 closed with nine campaign-tier failures recorded as F1 and routed rather than
fixed. Eight of them are one thing: the declared ML-grounding debt of
`audits/audit-phase-20-baseline-7.md` §10.2, where fits keyed to a corpus the baseline-7
record replaced now disagree with the corpus in the tree. The ninth is not that. It reads
no artifact, no fingerprint and no committed replay byte; it runs a six-player scenario
state through the deterministic engine and asserts what the scripted FSM impostor does.
The close audit separated it deliberately — *"This one pre-dates the record … It belongs to
Task 20.32's mover repair, not to the recording"* (:96) — and routed it as *"a separate,
smaller item"* (:113). This task is that item, and it is the whole of it.

The failure re-reproduces at HEAD 4002f19b in under a second:
`uv run pytest tests/training/test_scenarios.py -m campaign -q` → `1 failed, 51 passed`,
with `assert all(k.target != "p-5" for k in kills)` False at :443.

**The two-point bisect, run before this contract was written.** The test file was last
edited at Task 19.27 (#349) and `training/scenarios.py` at Task 19.18 — both before Task
20.32 (`09dab356`, "the impostor mover stops declining free kills and stalking ejected
players"). A detached worktree at `09dab356^` (`bf523ccc`) runs the same file green:
`52 passed in 3.86s`. The same worktree, driven by a scratch rollout probe, shows why. On
seed 7, *before* the repair, the FSM impostor stood in LABS beside a co-located victim with
its cooldown at 0 — and walked out: it moved to MEDBAY, killed the would-be witness `p-3`
there at tick 41, killed `p-1` at tick 48, never touched `p-5`, and the episode ended
`CREWMATES` with fitness `0.0`. *After* the repair, on the same seed and the same staged
state, it kills `p-5` in LABS at tick 40 — the staged victim, in the staged room, at the
staged tick — then `p-3` in MEDBAY at 50 and `p-1` in LABS at 56, and the episode truncates
on the tick budget with fitness `1.0`.

**That is the repair working, not a mover defect.** The pre-repair trajectory is the exact
shape the 2026-08-19 review measured and named — walking past a co-located free kill toward
a remote target, which is what the head-only kill seam produces: *"the policy declines
190/415 = 45.8 % of its legal zero-witness kill opportunities, and 168 of those … are the
defect: the kill seam re-validates only the top-ranked target"* (docs/ml-program.md:120-123).
The ranking for this particular state was not re-measured here; what was measured is the
behaviour it produced, on both sides of the repair. `agents/tactical/impostor_policy.py`
now scans the whole ranking for a free kill at :469 before falling back to `targets[0]` at
:483, and `_free_kill_target` (:867-893) defines the candidate exactly as the staged state
constructs one: co-located in `own_room` at the latest tick, with zero co-present
non-teammate witnesses. `p-5` is alone in LABS with the impostor; `p-3` is one doorway away
in MEDBAY and, under the Task 13.8 asymmetric visibility the scenario docstring states
(training/scenarios.py:276-279), a crewmate at base visibility sees the same room only, so
`p-3` cannot see into LABS at all. The staged window IS a free kill by the repaired seam's
own definition, and the repaired seam takes it.

**So the pin was pinning the defect.** The test's name says the FSM *hunts elsewhere*; its
comment says *"The scripted FSM impostor never takes the staged LABS window at all — it
walks next door and kills through MEDBAY instead."* Both were true, and both were a
description of the bug — written down as a fixture in a scenario named for killing under
nearby discovery pressure, in a drill built to reward exactly the kill the mover was
declining. This is Craft rule 5 read from the other end: the sentence stopped reproducing
the moment the code got better, and because the file carries `pytestmark =
pytest.mark.campaign` at :70 and `pyproject.toml:86` filters `-m 'not campaign'` out of the
default gate, 20.32's own green `check.sh` could not see it. That PR did re-pin the three
default-tier training files whose FSM trajectory moved — `tests/training/test_rollout.py`,
`test_rewards.py`, `test_bakeoff_harness.py` — and the campaign-marked fourth was the one
it could not see. State that mechanism in the PR; it is the reason the failure travelled
from its own merge through a scheduled campaign-tier run (32701066153, 2026-08-24) to the
phase close before anyone read it, and it is the same reason the DoD below asks for
`-m campaign` explicitly rather than trusting the default gate.

**What the anchor should assert instead.** The rewritten test is not a weaker test — it is
a sharper one, because the post-repair trajectory exercises a clause the old one never
reached. The FSM now earns the kill credit and then throws the survival credit away by
killing twice more: `_kill_with_witness_fitness` requires `len(kill_events) == 1`
(training/scenarios.py:376-380), and `does_not_reward` promises that *"second kills (any
kill beyond the first FORFEITS the survival credit, so silencing the discoverer or thinning
the electorate costs the score, not just gains nothing)"* (:404-406). Re-run the fitness
terms by hand on the seed-7 rollout and every other qualifier is satisfied: the staged
body `body-p-5-40` was reported by `p-1`, a CREWMATE, at tick 49, and that meeting
concluded. Only the exactly-one-kill clause withholds. The un-scripted FSM is therefore
the only anchor in the file that demonstrates the forfeiture clause biting on a trajectory
nobody wrote — and the assertions must say that, not merely re-pin a number.

**No coverage is lost by re-aiming it.** The Goodhart guard the old name half-carried —
unstaged kills earn nothing — already has a dedicated scripted home two functions down:
`_snub_the_staged_victim_selector` (:485-509) and
`test_kill_with_witness_pays_nothing_for_an_unstaged_kill` (:512-522), which forces the
kill away from `p-5` and asserts `0.0`. Both are green at HEAD and neither is touched here.
The full-credit path (:460-474), the no-kill path (:477-482), the self-report farm
(:545-554) and the pre-kill-meeting ordering pin (:584-601) are likewise green and
untouched. What changes is one anchor that described the tree before 20.32.

**One honesty constraint on the new assertions.** Under the default fake meeting layer no
meeting can ever eject — `training/scenarios.py:333-335` says so in the fitness docstring,
and all three seed-7 meetings record `outcome=SKIPPED`, `ejected_player_id=None`. So the
no-impostor-ejected clause is satisfied *vacuously* here. The test must not present that as
evidence the clause works; it must name the one live cause of the withheld credit (the
second kill) and say the ejection clause is vacuous under this layer. A test that lists
four satisfied conditions without saying which one is load-bearing is the same defect as
the sentence it replaces.

**Why one seed is enough, and what a re-pin of a deterministic fixture is for.** The
scenario harness is byte-deterministic by construction, and the file already proves it for
this exact scenario at this exact seed: `test_injected_episode_is_deterministic_twice`
(:167-175) parametrizes over `SCENARIO_LIBRARY` at seed 7 and asserts an identical
state-hash digest, identical `events` and identical `meetings` across two runs. The probe
above reproduces the same kill list run after run. So the anchor is not a sample of
FSM behaviour; it is a fixture over one fully determined trajectory, and its job is to trip
the next time that trajectory moves, exactly as `tests/training/test_rollout.py:54-56` says
of its own descriptors. That is why the answer to "the mover moved it" is a re-pin with the
cause written down, not a loosened assertion: an anchor rewritten to accept any trajectory
stops being able to fail, and Craft rule 2 calls that prose.

**One more thing the trajectory moved, worth naming and not pinning.** Pre-repair, seed 7
ended `CREWMATES` inside the horizon; post-repair it truncates on the tick budget
(`outcome == "TICK_BUDGET"`, `truncated` True) because the impostor spends the window
killing. Record both in the PR, because they are part of the evidence that hunt behaviour
changed — but do not add an outcome assertion to this anchor. The drill's fitness reads
typed events and meeting records only (`training/scenarios.py:346-381`); coupling it to the
episode's terminal shape would pin a horizon this task has no mandate over.

**What this task does not do.** It does not re-fit anything, does not touch the record, and
does not turn the campaign tier green — the eight §10.2 failures are 21.17's, verified
still red at HEAD in this task's own re-run. It does not edit `audits/audit-phase-20-close.md`:
F1 is a historical record of what was true at close HEAD and stays exactly as written. And
it does not edit the mover. If the diagnosis had landed the other way — if the emitted kill
violated `_free_kill_target`'s own stated invariants — the repair would move the FSM's
trajectory again, which moves `tests/training/test_rollout.py`, `test_rewards.py` and
`test_bakeoff_harness.py` with it and reaches recorded bytes at 21.14's smoke and 21.15's
re-record as an undeclared co-intervention. That is not a Small task and not this one:
the ruling below is STOP-and-report. Context for the reader who arrives here from the
phase-20 story: baseline 7 is canon by explicit owner override of a FINDING verdict — the
bars did not pass — and nothing in this task's evidence bears on that either way, because
this pin pre-dates the record it was found beside.

**Files in scope:**
- tests/training/test_scenarios.py; (the one anchor re-aimed and renamed, its comment rewritten, one planted case added; the module mark at :70 and the five sibling drills untouched)

**Files NOT in scope:**
- agents/tactical/impostor_policy.py (the diagnosed cause is the 20.32 repair behaving as designed; a mover edit would move the FSM trajectory, three further training pins and the bytes 21.14/21.15 record — if the diagnosis inverts, STOP and report rather than widening scope)
- training/scenarios.py (the fitness definition is verified correct here: it is what withholds the survival credit, exactly as `does_not_reward` promises, and `_kill_with_witness_fitness` reads only typed events — changing a fitness axis under the frozen campaign machinery is not a test re-pin)
- tests/training/test_rollout.py, tests/training/test_rewards.py, tests/training/test_bakeoff_harness.py (20.32 already re-pinned these three and they are green; they are read here only as the precedent for how a moved FSM trajectory is documented)
- tests/training/test_anchor_study.py, test_coevo_driver.py, test_composed_runner.py, test_surrogate_fidelity.py (F1's other eight failures — the §10.2 grounding debt, routed to 21.17)
- tests/training/test_suite_tiers.py (`_CAMPAIGN_FILES` pins the file path and `_MODULE_MARK_RE` the module-level mark; a rename inside the file needs no edit here, and the mark must survive it)
- audits/ (F1 is the record of what was true at close HEAD; this task's finding is reported in its PR, never back-written into a closed audit)
- pyproject.toml, .github/workflows/campaign-tier.yml (the tier split and its weekly schedule are correct; this task changes what a test asserts, not when it runs)
- replays/, training/artifacts/ and every ML fit (no corpus byte, fingerprint or fitted artifact is read by this test)

**Definition of done:**
- [ ] The diagnosis is executed as a two-point bisect and its result recorded in the PR's `## Decisions`: `uv run pytest tests/training/test_scenarios.py -m campaign -q` at HEAD, and the same command in a detached worktree at `09dab356^`, with both outputs quoted. The PR states the per-tick trajectory on both sides (victim, room and tick of every `KilledEvent`, plus the episode outcome and the scenario's fitness), so the claim "the repair changed hunt behaviour" is a measurement in the PR body and not an inherited sentence.
- [ ] The verdict is stated against a rule written down BEFORE the evidence is read, in these terms: the pin is stale and re-pinned when the emitted kill satisfies `_free_kill_target`'s own definition (co-located in `own_room` at the latest tick, `co_present == 0`, cooldown 0) and the pre-repair tree declined that same free kill; it is a mover defect when the emitted kill violates any of those, when the engine rejects a queued kill, or when a kill fires against a sighting the mover's own staleness rules should have dropped.
- [ ] If and only if the verdict is "mover defect": nothing in `agents/tactical/` is edited, the test is left red, and the PR opens with the diagnosis in `## Questions` as a STOP — a mover change is a declared co-intervention that must reach the owner before 21.14's smoke, not a side effect of a test re-pin. On that branch every item below that asserts a green file is reported UNCHECKED with this item as the reason, never ticked on a narrowed command; the evidence gathered here says the branch will not be taken, and the contract still says what happens if it is.
- [ ] `test_kill_with_witness_fsm_hunts_elsewhere_and_earns_nothing` is renamed to state what the anchor now proves — that the scripted FSM takes the staged free kill and then forfeits the survival credit — and no other test in the file is renamed.
- [ ] The test's comment is rewritten, not patched: the pre-repair narration ("never takes the staged LABS window at all — it walks next door and kills through MEDBAY instead") is deleted, and the replacement says what the FSM does now and why, with at most one trailing provenance line naming Task 20.32 — the shape `tests/training/test_rollout.py:58-61` and `tests/training/test_rewards.py:458-461` already use ("No training code changed").
- [ ] The assertions are semantic, not a bare number: the anchor pins that exactly one `KilledEvent` targets `p-5` in `LABS` at `KILL_WITH_WITNESS_NEARBY.staged_tick`; that the fitness is `1.0`; and that the survival credit is withheld by the second-kill clause ALONE — the staged body `body-p-5-40` WAS reported by a player whose role is `CREWMATE` at a meeting that concluded, and more than one kill landed. The comment states that the no-impostor-ejected clause is vacuously true under the default fake meeting layer (`training/scenarios.py:333-335`) and is therefore not evidence of anything here.
- [ ] A planted case ships beside it proving the pin bites on the cause it names: the same FSM rollout run through an intent selector that converts the impostor's kill intents after `staged_tick` into waits leaves exactly one kill — `p-5`, `LABS`, tick 40 — and lifts the fitness to `2.0`. The selector is a module-level pure function in the file's existing style (a tick comparison, no mutable state), and the case asserts both halves: one kill, and `2.0`.
- [ ] The five sibling drills are byte-untouched and still green: `test_kill_with_witness_single_kill_then_survive_earns_full_credit` (:460), `test_kill_with_witness_rewards_nothing_without_the_kill` (:477), `test_kill_with_witness_pays_nothing_for_an_unstaged_kill` (:512), `test_kill_with_witness_self_report_farm_earns_only_the_kill` (:545) and `test_kill_with_witness_pre_kill_meeting_carries_no_survival_credit` (:584) — the unstaged-kill guard in particular, which is where the Goodhart clause the old name half-carried actually lives.
- [ ] `pytestmark = pytest.mark.campaign` at :70 is unchanged and the file stays listed in `tests/training/test_suite_tiers.py::_CAMPAIGN_FILES`; `uv run pytest tests/training/test_suite_tiers.py -q` is green, proving the tier map still recognises the file after the rename.
- [ ] `git diff --name-only` lists exactly one path, `tests/training/test_scenarios.py`.
- [ ] The PR records the residue honestly: `uv run pytest -m campaign` still exits 1, the eight remaining failures are named with their files, each is attributed to `audits/audit-phase-20-baseline-7.md` §10.2 and routed to Task 21.17, and the PR says in so many words that this task closes F1's ninth failure and no other.
- [ ] The PR records the escape mechanism in one sentence for the next mover change: 20.32 re-pinned the three default-tier training files its trajectory moved and could not see the campaign-marked fourth, because `pyproject.toml:86` filters the marker out of `check.sh`.
- [ ] `uv run pytest tests/training/test_scenarios.py -m campaign -q` passes (53 tests).
- [ ] `uv run pytest -m campaign -q` is run and its full failure list pasted into the PR; the ninth failure is absent from it.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-21-mover-scenario` with a title like `task 21.13: the mover scenario pin tells the truth about hunting`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing F1's ninth failure — audits/audit-phase-20-close.md:89 (the F1 heading, "the campaign tier is RED at close HEAD (recorded, routed, not fixed)"), :96 (the one-scenario-pin bullet naming `tests/training/test_scenarios.py::test_kill_with_witness_fsm_hunts_elsewhere_and_earns_nothing`, its failing assertion `assert all(k.target != "p-5" for k in kills)` → False, the pre-dating evidence from scheduled CI run 32701066153 of 2026-08-24, and the attribution "It belongs to Task 20.32's mover repair, not to the recording") and :113 ("The one scenario pin is a separate, smaller item belonging to 20.32"); the Wave-0 register's own restatement of F1's identity at audits/review-2026-08-26/B/collated-findings.md:552 ("F1-F5 are the red campaign tier, two stale narrations, three word budgets, the audits-index ladder tip and the carried staging ref"); audits/audit-phase-20-baseline-7.md:728-745 §10.2, which routes the other eight failures and does NOT cover this one — no fit, no fingerprint and no corpus byte enters this test; docs/ml-program.md:118-126, the measured comparator defect this pin sat on top of ("the policy declines 190/415 = 45.8 % of its legal zero-witness kill opportunities, and 168 of those — 40.5 % of all free kills — are the defect: the kill seam re-validates only the top-ranked target"); anchors re-verified at HEAD 4002f19b — tests/training/test_scenarios.py:70 (`pytestmark = pytest.mark.campaign`), :85-99 (the `_run` helper the anchor uses), :167-175 (`test_injected_episode_is_deterministic_twice`, parametrized over `SCENARIO_LIBRARY` at seed 7), :433-444 (the failing anchor, assertion at :443), :447-457 and :460-474 (`_kill_once_selector` and the full-credit sibling), :477-482 (the no-kill sibling), :485-509 and :512-522 (`_snub_the_staged_victim_selector` and the unstaged-kill sibling), :545-554, :584-601 (the farm and pre-kill siblings); training/scenarios.py:255-256 (`_KILL_WITNESS_VICTIM = "p-5"`, `_KILL_WITNESS_ROOM = "LABS"`), :271-313 (the staged state: p-4 impostor and p-5 victim co-located in LABS, p-3 one doorway away in MEDBAY, `cooldowns={"p-4": 0}`), :316-381 (`_kill_with_witness_fitness`, the exactly-one-kill forfeiture clause at :371-380, the "under the default fake layer, which never ejects" note at :333-335), :384-414 (the spec, `staged_tick=40`, and the `does_not_reward` sentence on second kills at :404-406); agents/tactical/impostor_policy.py:451-482 (the repaired kill-emission seam, `_free_kill_target` called at :469 before `best = targets[0]` at :483) and :867-893 (`_free_kill_target`, whose docstring names 2026-08-19 review C-3: "Scanning the whole ranking rather than only its head is what stops a higher-scoring REMOTE lead from vetoing a kill standing in the room"); tests/training/test_rollout.py:51-62 and tests/training/test_rewards.py:448-461 (Task 20.32's own two re-pin precedents, each naming the mover repair and closing "No training code changed"); tests/training/test_suite_tiers.py:53-63 (`_CAMPAIGN_FILES` pins the FILE, not any test name) and :66-68 (`_MODULE_MARK_RE`); pyproject.toml:86 (`addopts = "--strict-markers -m 'not campaign'"`); engine/maps/canonical_1.yaml:34 (`kill_cooldown_ticks: 4`).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
