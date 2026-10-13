# Source-aware gameplay verification of the deduction development capture

This review checks the recorded play in `/tmp/ailibi-deduction-development-2`,
covering seven scenarios in six experimental configurations. The reviewer
implemented the temporal changes and scenario controls. **This is source-aware
gameplay verification, not a blind or independent gameplay review.** It was
written without reading `code-review.md`, and is frozen before the coordinator's
gameplay/code synthesis. The owner's planned independent Claude branch review
remains separate.

The evidence supports working observation, privacy, body-lifecycle, and meeting
delivery mechanics. It does **not** yet demonstrate that a group uses indirect
evidence to reach a better decision. The clearest missing demonstration is a
witness actually sharing the decisive movement observation, another player
hearing it as testimony, and the accused answering that specific account.

## Evidence and scope

Inputs were the capture's `evaluation.json` and per-run `view.json`,
`memories.json`, `report.json`, and recorded audit data. No live provider was
called, no runtime was changed, and no new games were generated for this review.

| Capture identity | Value |
| --- | --- |
| Provider / verdict | `scripted-deduction-control` / `MECHANICS_ONLY` |
| Evaluation file SHA-256 | `2a30b0c600bd68940273c8e5cd5e444860148643c598d8b2c2b877530854ecb0` |
| Recorded input SHA-256 | `500fa62dc314b64110c70ac4e1a4f83d18e9e96182dcce54c208831fb7e90ebf` |
| Recorded scenario source SHA-256 | `d75b95495c4d727900a282c2620c7fca4a49a9a193ee3e4b81da37f131bf4711` |

This is development evidence, not the final source freeze or an adoption record.
Unlike an earlier development trajectory discussed during implementation, this
capture already includes the witness's typed `saw_kill`/`saw_vent` speech and the
late accusation against the reporter. Findings below refer to those recorded
versions, not the earlier incomplete direct-speech controls.

All runs use seed 1, four players, one impostor, and authored legal tactical
schedules. The spectator record identifies p-4 as the impostor; that privileged
fact is not evidence available to another player. All configurations preserve
positions after meetings. The matrix therefore does not compare reset policies.

| Configuration | Temporal / reasoning | Public accounts | Attributed testimony | Extra reply |
| --- | --- | --- | --- | --- |
| `legacy_reference` | OFF | OFF | OFF | OFF |
| `repaired_clock` | v2 / v2 | OFF | OFF | OFF |
| `common_accounts` | v2 / v2 | v1 | OFF | OFF |
| `attributed_testimony` | v2 / v2 | OFF | v1 | OFF |
| `combined_accounts` | v2 / v2 | v1 | v1 | OFF |
| `combined_with_reply` | v2 / v2 | v1 | v1 | v1 |

Across 42 games there are 48 meetings and 144 ballots. All 144 ballots voluntarily
SKIP; none is rewritten. All games end with impostor parity at tick 12, with no
ejections. These outcomes are authored controls, not measured decision quality.
All five paired comparisons report zero changed world trajectories. The extra
reply configuration adds exactly one turn and one call, in `late_accusation`.

## Observed scenarios

Ticks in the table distinguish a start-of-tick observation from action events
during that tick. Spectator post-action frames are not agent snapshots.

| Scenario | Actual recorded play and observer knowledge | Meeting result / interpretation |
| --- | --- | --- |
| `honest` | p-2 last sees p-1 alive in ADMIN at start tick 3, leaves, and misses the kill at 4. During 5, p-2 returns to ADMIN before observing p-4 leave ADMIN for WEST_HALL. Body discovery is at start 6. | p-4 claims WEST_HALL at 5, which fits the observed departure. A plausible placement does not establish innocence. All SKIP. |
| `impossible_account` | The same real observations occur. p-4 instead claims REACTOR at 5. The ADMIN departure toward WEST_HALL cannot be reconciled with that distant placement by a single within-tick walk. | p-2 holds the relevant observation privately but does not state it publicly. The recorded contradiction list is empty. All SKIP. |
| `insufficient_evidence` | p-2 takes the west-side route through MEDBAY/LABS and misses the relevant departure. Discovery/report occurs at 7. | The observer lacks the time-local evidence needed to reject the REACTOR account. Spectator knowledge of the kill must not fill that gap. All SKIP. |
| `already_known_dead` | p-3 calls an emergency at 5. The public roster establishes p-1 dead by 5; p-2 discovers the still-unreported body at 8. Its memory distinguishes last seen alive at 3, known dead by 5, and discovered at 8. | The two meetings do not turn discovery at 8 into a new death bound. This real case does not itself reproduce the old scalar-proximity defect; that requires the separate adverse control. Both meetings SKIP. |
| `witnessed_kill` | p-2 stays in ADMIN and actually witnesses p-4 kill at 4. The meeting includes the matching typed `saw_kill` account. | First-hand kill count is one in every configuration. Shared role-proof flags remain zero. These fixed ballots still SKIP, so this is delivery coverage only. |
| `witnessed_vent` | p-2 actually sees the ADMIN vent entry at 5 and publicly states `saw_vent` at the meeting at 6. A later exit at 8 explains the second first-hand vent event in whole-game counts. | Shared role-proof flags are one in the legacy, repaired-clock, and common-account configurations; zero in all three configurations with attributed testimony. The real private witness knowledge remains. All SKIP. |
| `late_accusation` | After p-2 opens and p-4 replies, p-3 asks the reporter to explain the return to the body room. The enabled extra turn belongs to p-2 and points to p-3's late turn. | The reply repeats the opening's body/task account and accusation rather than answering the question. Routing works; substantive defense is not demonstrated. All SKIP. |

### Body lifecycle and movement

In the ordinary cases, p-1's body appears at kill tick 4, remains in the report
scene at 6, and is absent from the next playable frame at 7. For
`insufficient_evidence`, report/removal occur at 7/8; for `already_known_dead`, at
8/9. The emergency at 5 does not report the body, so its persistence until 8 is
coherent. The later body created by the terminal kill at 12 is a different body.
Each schedule selects one report action. No repeated engine body report or
post-death non-idle player frame was observed across the matrix. The repeated
`found_body` row in the extra reply is repeated speech, not a second engine
report.

The primary route uses ordinary door-connected moves. The important same-tick
case is explicit: p-2 is in UPPER_HALL at start 5, moves to ADMIN, and is already
there when p-4's later departure occurs. Its own transition and witness record
preserve that order. There is no need to invent simultaneous start-of-tick
co-location. Temporal v2 body handles and the reporter's death window do not
reveal the hidden exact kill tick 4 in the unwitnessed case.

Waiting dominates the authored schedules: the ordinary case selects 26 waits
among 44 actions, and all games finish with zero completed tasks. These are
small evidence controls, not representative autonomous play. They do not assess
normal-policy wandering, chase behavior, sabotage response, a task race, visual
animation, or frame performance. No conclusion that general movement glitches
are resolved follows from this matrix.

## Findings to carry into the next playable demonstration

### 1. Complete the public indirect-evidence exchange

In `combined_accounts/impossible_account`, p-2's memory contains the real
ADMIN-to-WEST_HALL observation at tick 5. Its opening states only the body
discovery, its own task activity, and a generic accusation. It never publicly
states the departure or explains why REACTOR at 5 conflicts with it. p-3's vote
prompt consequently does not contain the private departure observation, and
the shared transcript has no typed movement account. That is the correct
privacy boundary; the missing step is the witness choosing to tell the group.

Before claiming that the candidate enables demonstrated group deduction, add a
bounded control in which the real witness shares this acquired observation,
the accused responds to that placement, and a separate listener reasons from
the attributed account. Keep honest, impossible, and insufficient variants.
Do not copy private memory into publicly certified truth or invent evidence
retroactively. This is a gap in the current scripted demonstration, not evidence
that a real model would always omit the observation.

### 2. Exercise an answer and an evidence-backed decision

The additional reporter turn in `combined_with_reply/late_accusation` repeats
the same `found_body`, task-activity, accusation, and uncertainty text. It does
not explain the return route or answer the question. A useful next control
should supply a defense grounded in the reporter's actual prior observations
or recorded activity, plus a case where the reporter has nothing new to add.
An extra call is not itself a reasoning improvement.

There are 144 opening memory projections and **zero observation-reference
entries** in their recorded API output. Every ballot has null reason/citation
identifiers. This does not establish a broken citation feature; it establishes
that this matrix never exercises a cited decision through the portfolio's
click-through evidence path. Add a clearly labeled authored mechanics ballot
that cites a real source, together with an uncertainty/SKIP control. Separately
measure model decisions later; do not manufacture a winning vote and label it
improved model reasoning. Confidence 1.0 in these fixed SKIPs is likewise not a
calibration result.

### 3. Prioritize the evidence a player needs to read

In the primary v2 reporter memory, several old travel checks concerning the now
dead player and repeated explanations that feasible travel does not establish
innocence precede the decisive departure. The correct evidence is present,
but the small fixture already produces substantial repetitive context.
Prioritize the victim's relevant window and the placement currently in dispute,
while retaining earlier relevant intervals. Do not regress to considering only
the latest pair of sightings.

Two small presentation issues are visible: some memory phrases say “at during
tick,” and the `witnessed_kill` speaker's body account uses tick 6 although its
first private body discovery was at start 5. The latter is an authored public
claim using the report time, not proof that the discovery clock is wrong. Keep
the distinction between seeing a body and reporting it clear in the eventual
demonstration.

## What now works toward escaping the vent-detector pattern

The attributed configurations preserve actual witness knowledge while removing
the shared vent certificate. They therefore permit a player to dispute another
player's claim without silently inheriting that speaker's private proof.

The task control also creates legitimate cover: at tick 2 p-2 privately records
real `upload_logs` progress, while p-4 privately records a rejected attempt at
the same activity. Nearby observers see role-blind activity, and both speakers
can publicly claim task activity. The bystander does not receive the rejected
attempt's ownership reason or a completion certificate. This is useful
counterplay, provided later reasoning treats an activity claim as a claim.

The next useful demonstration is therefore a short causal chain: a legal action
creates a real observation; its owner chooses to share it; another player gives
a specific account or defense; a listener makes a cited decision or justified
SKIP. Bounded investigation can then add a genuinely new observation to the
insufficient case. It should cost an action and operate prospectively, rather
than reveal an earlier unseen event. This review does not establish model
quality, balance, or grounds for adopting the experimental defaults.

## Reproducing the aggregate checks

Run from the repository with the captured directory still present. This reads
the frozen JSON rather than importing or rerunning the current implementation:

```bash
.venv/bin/python - <<'PY'
from collections import Counter
import hashlib
import json
from pathlib import Path

base = Path('/tmp/ailibi-deduction-development-2')
raw = (base / 'evaluation.json').read_bytes()
data = json.loads(raw)
meetings = [m for c in data['captures'] for m in c['report']['meetings']]
ballots = [b for m in meetings for b in m['ballots']]
memories = [
    m for path in base.glob('*/*/memories.json')
    for m in json.loads(path.read_text()).values()
]
print('evaluation_sha256', hashlib.sha256(raw).hexdigest())
print('games/meetings/ballots', len(data['captures']), len(meetings), len(ballots))
print('ballots', Counter(b['target'] for b in ballots))
print('memory projections/references', len(memories),
      sum(len(m['observation_references']) for m in memories))
print('outcomes', Counter(
    (c['report']['winner'], c['report']['reason'], c['report']['final_tick'])
    for c in data['captures']
))
for row in data['comparisons']:
    print(row)
for capture in data['captures']:
    print(capture['arm'], capture['case'], capture['firsthand_kills'],
          capture['firsthand_vents'], capture['role_proof_flags'],
          capture['public_account_counts'])
PY
```

For the concrete exchanges, inspect
`combined_accounts/impossible_account/report.json` and
`combined_with_reply/late_accusation/report.json`; compare their recorded
meeting prompts with the corresponding `memories.json`. Body transitions and
routes are in each run's `view.json`. These are local development artifacts;
the final evaluation record must bind and retain its own source and artifact
hashes before this review can be used as evidence about that final capture.

## Later disposition — 2026-09-06: scenario definition version 2

The review above remains about the unchanged version-1 development capture.
Following coordinator acceptance of its findings, the scenario worker made a
bounded fixture revision. This section records that later implementation; it
does not retroactively change the reviewed outputs or supply an independent
review of the revision.

- The `honest`, `impossible_account`, and `late_accusation` reporter now states
  the movement actually present in its supplied private-memory prompt. It copies
  the displayed clock: source tick 5 in all repaired configurations and the
  historical displayed tick 6 in legacy. It does not quietly repair legacy
  knowledge. The insufficient case and the early emergency do not acquire a
  movement statement or a future body discovery.
- The impossible account now yields a public comparison. `common_accounts`
  retains its legacy `alibi_vs_sighting` interpretation; configurations with
  attributed testimony yield the conditional `alibi_conflict` describing the
  two speakers' accounts and leaving an unseen vent possible. The honest account
  remains conflict-free. The listener sees the public statement without receiving
  the reporter's private observation ID or a new first-hand memory.
- The additional reporter reply gives the actual UPPER_HALL placement at start
  5 and ADMIN placement at start 6, explains the return to the room where the
  reporter had been working, and acknowledges that it missed the kill. It no
  longer repeats the opening's body report and accusation.
- The reporter's fixed SKIP cites the opaque ID copied from its supplied
  movement line. Tests resolve that exact ID through the real recorded API to
  p-2's observed ADMIN-to-WEST_HALL movement and spectator scene tick 5. All
  18 combinations of the three affected scenarios and six configurations pass
  this check. An opaque identifier containing unrelated numbers still uses the
  displayed clock; removing the private line cannot be repaired by an identical
  public statement or a previous provider call.

`ScenarioDefinition` now generates version 2. Historical version-1 definitions
remain readable, but the current scripted provider refuses to execute them as
though they selected the new fixture. The seven cases, six configurations,
authored tactical schedules, and fixed-SKIP mechanics limitation remain. Memory
prioritization and actual model-quality evaluation remain open; this revision
does not establish either.

Development verification: 46 tests passed with
`.venv/bin/pytest -q tests/orchestrator/test_deduction_scenario_exchange.py tests/orchestrator/test_temporal_evidence_v2.py tests/orchestrator/test_public_account_scenario.py`.
Ruff format/check and strict mypy passed for
`experiments/deduction_scenarios.py` and the new scenario-exchange test file.
The coordinator owns the subsequent source freeze, full project gate, and new
matrix capture. The version-1 capture counts above remain historical evidence.
