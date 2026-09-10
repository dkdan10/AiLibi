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
  that runs no arm. No prefix bytes are committed anywhere.
- [Execution manifest](execution-manifest.md) binds every preregistration field
  for the fresh-model comparison, including the limits the owner authorized on
  2026-09-07. It authorizes no live call: a call additionally requires an
  explicit runner invocation naming that file, and no test or CI job performs
  one.
- [Run of 2026-09-10](run-2026-09-10/RESULTS.md) is the one authorized live run
  under that manifest. It **stopped after 1 of 100 units** on the post-unit
  spend reconciliation, so no paired unit completed and the primary outcome was
  not measured. The directory retains the partial evidence and the unresolved
  accounting the stop rule requires: the two per-unit replays and the
  instrument's partial-state log. It records a defect in the instrument, not a
  measurement of the candidate, and no limit was near exhaustion ($0.00, 160 s).

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
