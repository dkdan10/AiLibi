# Bounded investigation: implementation and decision

The offline implementation is an unadopted candidate on `codex/cleanup`.
[Normal-policy evidence](2026-09-06-normal-policies.json) and the
[meeting comparison](2026-09-06-meetings.json) share the exact runtime source
inventory. The [handoff](candidate-handoff.json) binds both files by SHA-256 and
names the missing prerequisites for fresh evaluation. Main remains unchanged.

## Result and recommendation

Agents can now choose a short search from an actual owned last-known sighting,
obtain new information, and resume ordinary work. This addresses the information-
gathering part of the vent-detector problem. It does not establish that a model
uses that information to reason or vote better. The next evaluation should test
fresh meeting decisions on the corrected evidence/account pipeline, with search
kept as an independent candidate because its task cost is material.

Five selected development seeds, five players, one impostor and two tasks per
crewmate were run across seven arms. All 35 games completed naturally and passed
strict report/API reconstruction. The 476 scripted-provider calls returned
1,038,620 synthetic input tokens and 24,038 synthetic output tokens at $0.
All 238 ballots voluntarily skipped; there were no authored accusations or
wrongful ejections. These controls do not measure model judgment or win-rate
significance. Each comparison has only five inspected game inputs.

| Candidate versus ordinary behavior | Changed engine trajectories | Concrete result or cost |
| --- | --- | --- |
| Search | 5/5 | Seed 6 reported a body at tick 7 rather than 15; seed 14's task win moved from tick 26 to 41. |
| Contextual self-report | 1/5 | Seed 1 supplies a real report with an observed nearby crew member and active cooldown; four controls retain the same world trajectory. |
| Unconditional self-report | 5/5 | The older option reports in every selected game; outcomes remain an independent comparison, not evidence for contextual reporting. |
| Existing patrol | 4/5 | Finished-crew movement changes some later information and outcomes. |
| Existing accompaniment | 4/5 | Its direct comparison with patrol changes only 1/5 world trajectories, at the final tick of that game. |
| Search plus contextual reporting | 5/5 | Compared with search alone it changes 2/5 world trajectories and can further delay or lose task completions. |

Search adds 435 and loses 280 observer/tick/placement signatures across the five
common horizons. At those horizons it completes six fewer tasks in aggregate.
Those signatures are not independent clues or a quality score. Matched task
completion delays and unmatched completions remain separate in the measurement;
missing completions are never reported as zero delay. In seed 6 search completes
four tasks rather than six, and the game ends at tick 20 rather than 26.

The old accompaniment-versus-patrol difference in seed 14 consists of two new
movement observations at terminal tick 26; no later decision can use them. In
seed 1 a different submitted action is discarded without changing the world.
A new three-tick follow option is therefore deferred for lack of a demonstrated
useful additional information opportunity. The existing historical option and its
verdicts are retained; no inert new switch was added. This is a scoped decision
from the authorized plan's “accompaniment if justified” condition, not a claim
that every possible accompaniment design has been disproved.

## Mechanisms and review synthesis

The [code review](code-review.md) was frozen before the gameplay worker's findings
were shared. The coordinator preserved the worker's [gameplay findings](gameplay-review.md)
from its messages before synthesis. That worker also built the measurement
harness, so this is source-aware verification, not a blind external review.
The owner's later Claude review remains outstanding.

The two perspectives agree that a search must have observable consequences and
must preserve what remains unknown. Typed sources retain actual clocks and IDs;
plans cannot become witness events or suspicion. The source-consumption index
prevents a stale-source restart loop. Search expires after six elapsed ticks,
including interruptions, and inspects at most three rooms. It does not interrupt
task execution for discretionary exploration. Currently visible bodies and
immediate witnessed danger receive urgent treatment; unknown corpses never become
route targets. Public meetings retain only plans valid under their original
expiry and announced deaths. A later observation cannot certify an earlier alibi.

Version 3 accepts only exact built-in agents/policies and verifies full ordinary
FSM, emergency and plan state through shared live/reader code. Repeated identical
packets return before a second ingestion; conflicting packets fail. The reader
checks all submitted actions, including rejected/discarded ones, then applies
the original recording. Plan projections carry their decision tick and are shown
only under the appropriate own-agent or omniscient lens. Version-1/2 behavior and
encoding remain supported under their original interpretation.

Review found and corrected adjacent-body routing, the prior-source-tick witnessed-
kill interruption, and constructor-failure cleanup. The final measurement review
also separated submitted-action changes from actual engine-state changes, including
meeting resolutions. Those controls prevent a discarded action from earning a
false gameplay improvement. Immediate danger handling is not a new persistent
flight strategy; no new tactical model call or hidden-information input was added.

The meeting matrix on the same final runtime still has 42 strictly reconstructed
runs, 144 voluntary SKIP ballots, 289 scripted calls, no ejections and no changed
trajectories. The independent reply arm adds exactly one answer and one call.
It retains direct kill/vent controls, actual no-direct-proof cases, common account
vocabulary and attributed public testimony. Its earlier checkpoint remains a
separately preserved historical record.

## Verification

`bash scripts/check.sh` passed: **7,137 Python tests**, 20 optional skips and
three expected failures; **514 frontend tests**; strict mypy on 466 sources;
lint/format, four import contracts, document/generated-type checks and production
build. The Python test leg took 185.21 seconds in this local run, not a deployment
performance claim. The runtime priority/integration suite separately passed 51
tests. Both actual API and static browser journeys passed with no retries.
All 100 canonical and 200 ML-corpus recordings verified, and all four historical
report `--check` commands passed without rewriting evidence.

Development failures were retained and corrected: the first combined run caught
audit-directory indexing, the architecture word budget, source hashing while
sources were still being edited, and old-DTO comparison normalization. The next
run caught a test import's explicit-export typing requirement. A later run passed
7,135 tests but exposed two stale audit-byte inventory checks; the corrected inventory
passed in the final combined run. No gate was weakened to make these pass.

Reproduction commands are in the [index](README.md). Raw recordings/views are
regenerated working artifacts; the two committed measurements bind their hashes.
No hosted model, model fit, new map/role/dependency, historical re-recording,
default adoption, main merge or deployment occurred.
