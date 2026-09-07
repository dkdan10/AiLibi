# Evidence and meeting checkpoint

This checkpoint implements the evaluation, temporal-evidence and public-account
milestones on `codex/cleanup`. The candidate remains OFF and unadopted. The
[source-bound measurement](2026-09-06-mechanisms.json) identifies its exact runtime
bytes; subsequent investigation work makes this a historical checkpoint.

The code reviewer formed its findings independently of the gameplay note. The
gameplay author inspected real recorded scenarios, but also implemented their
temporal layer: that review is source-aware verification, not a blind external
assessment. Both notes and their dated corrections remain available before this
synthesis. The owner's later Claude review remains outstanding.

Their combined finding is that useful deduction needs evidence a listener can
actually receive. Correct clocks alone do not create public information. The
corrected scenario reporter now shares an actually witnessed departure and cites
its own observation; listeners receive attributed testimony without its private
reference. The honest and impossible route accounts differ conditionally, while
a missed observation leaves uncertainty. The bounded additional reply answers a
late charge with actual route context. Direct kill and vent controls stay separate.

The command below ran seven cases across six independently selected profiles:

```sh
.venv/bin/python -m experiments.deduction_evaluation --output-dir /tmp/ailibi-deduction-checkpoint-20260906
```

All 42 real recordings passed strict report/API reconstruction and live-to-reader
memory comparisons. All 144 authored ballots voluntarily skipped: there were no
correct or wrongful ejections and no changed engine trajectories in any of the
five seven-case comparisons. The reply addition produced one extra reply and one
extra call. Total accounting was 289 scripted-provider calls, 599,767 synthetic
input tokens, 20,492 synthetic output tokens and $0. These are mechanics controls,
not measured model reasoning, win-rate improvement or normal-policy games. The
already-known-dead real case verifies knowledge bounds; the scalar proximity
failure is reproduced by a separate adverse unit input, not claimed for that run.

Verification after runtime corrections:

- `bash scripts/check.sh`: 7,024 Python tests passed, 20 optional skips and three expected failures; 512 frontend tests passed. Strict mypy covered 455 sources. Lint, formatting, import boundaries, documentation, generated types and production build passed.
- `bash scripts/verify_samples.sh`, then the same command with `AILIBI_SAMPLES_ROOT=replays/ml_corpus`: all 100 canonical and 200 ML-corpus recordings verified.
- `.venv/bin/python scripts/build_sample_report.py --sample-dir <set> --check` for each of `replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i`, and `replays/ml_corpus/9p2i`: all four historical reports remained byte-consistent.
- `npm run e2e -- --grep 'exact evidence'` from `frontend`: both real API and static-bundle browser journeys passed with no retries.

The first full run found seven integration failures, corrected without weakening
their gates: legacy optional-field serialization, fixtures that omitted actual
voters or conflicted with their own stamps, report identity expectations and the
production prohibition on importing experiment harnesses. The matrix now lives
entirely in `experiments/`. The first browser attempt found a static type fixture
missing required explicit null fields; the corrected rerun passed both journeys.

The next implementation is a bounded search based on the agent's own typed
sightings, with ordinary-policy replay verification. That is a separate behavioral
comparison. Fresh model decisions require the [preregistration](preregistration.md),
a frozen execution manifest and an explicitly authorized provider/token/wall/cost
budget. Neither this capture nor completion of offline implementation authorizes
spending, adoption or merging into main.
