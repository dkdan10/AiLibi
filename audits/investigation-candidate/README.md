# Bounded investigation candidate

The [checkpoint and synthesis](checkpoint.md) records the implemented behavior,
measured costs and remaining decision. The [code review](code-review.md) and
[source-aware gameplay findings](gameplay-review.md) retain their separate
methods and the states reviewed before synthesis.

- [Normal-policy measurement](2026-09-06-normal-policies.json): 35 real games, five selected development seeds and seven independent/combined controls.
- [Meeting mechanism measurement](2026-09-06-meetings.json): 42 actual scenario/profile runs on the same final runtime source inventory.
- [Candidate handoff](candidate-handoff.json): hashes, configurations and the explicit missing prerequisites for live execution. This is not spending authorization or a frozen execution manifest.

Reproduce into new destinations:

```sh
.venv/bin/python -m experiments.investigation_evaluation --output-dir /tmp/ailibi-investigation-new
.venv/bin/python -m experiments.deduction_evaluation --output-dir /tmp/ailibi-deduction-new
```

Each command refuses existing output, verifies actual recordings and binds source
and input hashes. Raw replays, API projections and generated working reports are
disposable regenerated outputs; the committed flattened measurements retain
source references and verification hashes. All responses use deterministic
scripted providers, with synthetic token accounting and $0 cost. No new model
quality, default adoption, held-out success or merge is established.
