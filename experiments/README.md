# Experiments

Offline measurement harnesses. Each one drives the engine or reads the committed
recordings and reports what it measured; none of them changes the game. No game
package imports this folder, and `tests/test_firewall.py` fails if `agents/`,
`meetings/`, `observation/` or `llm/` ever does. What a measurement
found is written up in an audit record under
[`process/audits/`](../process/audits/README.md), not here.

The machine-learning program that used some of this work ended in a negative
result: four learned impostors won more games than the scripted one, and none
became the default. That result is [docs/ml-program.md](../docs/ml-program.md).

## The live modules

These six still run and still have tests. Run them from the repository root;
none of them spends money.

| Module | What it does | Run it | Tests |
| --- | --- | --- | --- |
| [`deduction_evaluation.py`](deduction_evaluation.py) | Plays seven hand-written 4-player meeting cases (from [`deduction_scenarios.py`](deduction_scenarios.py)) under several evidence settings and counts what changed. The speech is scripted, so it measures mechanics, not a model's judgment. | `uv run python -m experiments.deduction_evaluation --output-dir DIR` | `tests/eval/test_deduction_evaluation.py` |
| [`investigation_evaluation.py`](investigation_evaluation.py) | Plays five 5-player seeds with the built-in policies, with and without the bounded-investigation and self-report options, and compares actions, sightings and task delays. Fixed speech again: mechanics only. | `uv run python -m experiments.investigation_evaluation --output-dir DIR` | `tests/eval/test_investigation_evaluation.py` |
| [`tactical_gameplay.py`](tactical_gameplay.py) | Counts tactical events in the committed recordings and plays fresh paired games per [arm](../docs/glossary.md#arm-one-measured-configuration) with the deterministic fake provider. Its record is [the tactical lab](../process/audits/tactical-gameplay/README.md). | `uv run python -m experiments.tactical_gameplay --split development --output PATH` | `tests/experiments/test_tactical_gameplay.py` |
| [`held_out_prefixes.py`](held_out_prefixes.py) | Generates game openings up to the first meeting in which no living crewmate saw a kill or a vent, and commits only their hashes. The evaluation it served closed on 2026-09-19, so its writer refuses; `--tally` still counts a seed band outside the frozen ones. | `uv run python -m experiments.held_out_prefixes --tally FIRST LAST` | `tests/experiments/test_held_out_prefixes.py` |
| [`fresh_deduction_instrument.py`](fresh_deduction_instrument.py) | The runner for that closed evaluation: two arms over the frozen openings, ballots scored. The fake-provider dry run is the only mode a check uses; a live run refuses while [the execution manifest](../process/audits/deduction-candidate/execution-manifest.md) carries the owner's closing clause. | `uv run python -m experiments.fresh_deduction_instrument --dry-run` | `tests/experiments/test_fresh_deduction_instrument.py` |
| [`extract_gameplay_facts.py`](extract_gameplay_facts.py) | Re-simulates the 9-player sample set with roles re-derived from each seed, and writes a facts file plus every broken game rule it finds. It reads only recordings made without experiment settings, so on the current set it stops at seed 0 and names them. | `uv run python -m experiments.extract_gameplay_facts` | `tests/experiments/test_gameplay_facts_*.py` |

## The research record

[`lab/`](lab/README.md) and `model_probe/` hold research that is finished. Both
folders are frozen recorded output: [docs/artifacts.md](../docs/artifacts.md)
registers them as one row with a byte promise (170 tracked files and their exact
total size), and `uv run python scripts/verify_ml_evidence.py --only
availability` fails when either changes. Read them; do not edit them. Most of
the code in them carries a `FROZEN` header naming
[`training/README.md`](../training/README.md).

### Machine learning

- [ML spike charter](lab/ml-spike-charter.md) and [results](lab/report-ml-spike.md): the offline feasibility check before the training build (`lab/ml_spike/`). The results page marks its own headline number stale.
- [Grounding audit](lab/report-grounding-audit.md): whether the lab's scorer could serve as a training reward. As written, it could not.
- [Torch probe](lab/report-torch-probe.md) and [its notes](lab/torch_probe/README.md): a recurrent policy trained with gradient methods, kept outside the project's dependencies.

### Model selection

- [Model ceiling](lab/report-model-ceiling-probe.md): the same hard impostor replies across model sizes, asking whether a stronger model fixes them.
- [Hosted model sweep](lab/report-featherless-sweep.md) and [Qwen3.6-27B against the incumbent](lab/report-featherless-sweep-qwen3-6-27b.md): the probes behind the choice of the hosted evaluation model.
- [Prompt ladder](lab/qwen36_prompt_scratch/README.md): that model's prompt set, written from scratch one rule at a time.
- `model_probe/`: the earlier local-model probes of votes, openings, replies and seconding. Findings: [5 seeds](model_probe/results/findings-p1-5seed.md), [7B](model_probe/results/findings-p2-7b.md), [9B](model_probe/results/findings-p2-9b.md). Examples: [openings](model_probe/results/conversation-examples-50seed.md), [decisive openings](model_probe/results/conversation-examples-decisive.md), [smoke run](model_probe/results/conversation-examples-smoke.md), [replies](model_probe/results/reply-examples-v1.md), [seconding](model_probe/results/optin-examples-v1.md).

### Design thread

- [Lab rules](lab/README.md), [the desired-behavior rubric](lab/rubric.md) and [the first synthesis](lab/SYNTHESIS.md).
- Offline counterfactuals and sweeps: [vote tallies](lab/report-tally-lab.md), [the task clock](lab/report-stopwatch-lab.md) and [its retune sweep](lab/report-stopwatch-sweep.md), [suspicion decay](lab/report-decay-emergence.md), [hidden movement](lab/report-vent-escape-lab.md).
- What the impostor's model could say when suspected: [deception battery](lab/report-deception-battery.md), [its sequel](lab/report-deception-battery-2.md), [deflection](lab/report-deflection-probe.md), [kill memory](lab/report-memory-fix-probe.md).
- The rework that followed: [redesign probes](lab/report-forward-redesign-probes.md), [rubric redesign](lab/report-rubric-design.md), [interestingness score](lab/report-rubric-interestingness.md), [deduction rework plan](lab/report-phase-b-plan.md).

### Route lines

Two offline replays of the committed recordings came before the
[route lines](../docs/glossary.md#route-line-what-the-doors-say-about-a-players-stated-places)
that the shown 9-player set was recorded with. Each report is written by its
script, whose `--check` recomputes it: the
[route-check replay](lab/report-route-check-replay.md)
(`lab/route_check_replay.py`) and the
[route-lines replay](lab/report-route-lines-replay.md)
(`lab/route_lines_replay.py`). Tests:
`tests/experiments/test_route_check_replay.py` and
`tests/experiments/test_route_lines_replay.py`.
