# Deduction candidate evidence

This directory records the unadopted follow-through to the owner's independent
[cleanup review](../review-2026-09-06/README.md). The work follows the
[six ordered outcomes](../../tasks/post-review-plan.md).

- [Code review](code-review.md) freezes independently checked implementation
  findings before synthesis. Its planted failures matter as much as passing runs.
- [Gameplay verification](gameplay-review.md) records the actual development
  scenarios and a dated disposition after fixture corrections. Its author
  implemented the temporal layer; this is not a blind external review.
- [Prospective evaluation](preregistration.md) separates controlled fresh
  meeting decisions from complete normal-policy games. It requires a frozen
  candidate and budget before live execution.
- [Held-out freeze](held-out/manifest.json) records fifty proof-free scripted
  prefixes as HASHES ONLY, drawn from a preregistered seed band by a session
  that runs no arm. No prefix bytes are committed anywhere. It holds the second
  band, 5000–5999, frozen on 2026-09-10.
- [The first held-out band](held-out/manifest-band-3000-3999.json), 3000–3999,
  is development data since 2026-09-10: the run of that date rendered seed 3000
  to the model before stopping on an instrument defect, and the preregistration
  treats a rendered prefix as development data. Its record was marked rather
  than deleted — the `converted` block names the run, the rendered seed and the
  fix the stop informed — and its digests are the bytes frozen at `23a23c2d`.
- [Execution manifest](execution-manifest.md) binds every preregistration field
  for the fresh-model comparison, including the limits the owner authorized on
  2026-09-07. It authorizes no live call: a call additionally requires an
  explicit runner invocation naming that file, and no test or CI job performs
  one.

The reproducible development command is:

```sh
.venv/bin/python -m experiments.deduction_evaluation --output-dir /tmp/ailibi-deduction-new-run
```

It refuses an existing destination, uses a deterministic scripted provider and
records seven real canonical-map scenarios across six explicitly selected
profiles. The output contains actual recordings plus a flattened measurement
record, source/input hashes and hashes of reconstructed spectator/memory views.
Filesystem creation time is excluded from the spectator hash. Regenerated
recordings and large viewer projections are disposable artifacts; the [checkpoint summary](checkpoint.md) binds this stage to its committed
[flattened measurement](2026-09-06-mechanisms.json). Later runtime changes require a
new separately named capture.

The authored ballots deliberately skip. These runs establish mechanics and
information boundaries, not improved model decisions. No default change,
historical re-recording, live-provider spending or adoption is authorized here.
