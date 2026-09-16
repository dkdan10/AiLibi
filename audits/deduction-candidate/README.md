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
  that runs no arm. No prefix bytes are committed anywhere. It holds the fifth
  band, 8000–8999, frozen on 2026-09-15.
- [The first held-out band](held-out/manifest-band-3000-3999.json), 3000–3999,
  is development data since 2026-09-10: the run of that date rendered seed 3000
  to the model before stopping on an instrument defect, and the preregistration
  treats a rendered prefix as development data. Its record was marked rather
  than deleted — the `converted` block names the run, the rendered seed and the
  fix the stop informed — and its digests are the bytes frozen at `23a23c2d`.
- [The second held-out band](held-out/manifest-band-5000-5999.json), 5000–5999,
  is development data since 2026-09-13, for the same reason and kept the same
  way: the run of that date rendered seed 5000 before the provider returned an
  empty completion and the run stopped in its first unit. Its `converted` block
  names that run and the transport-resilience fix it informed; its digests are
  the bytes frozen at `ca6e97d6`.
- [The third held-out band](held-out/manifest-band-6000-6999.json), 6000–6999,
  is development data since 2026-09-13 as well, for the same reason and kept
  the same way: the run of that date rendered seeds 6000 and 6001 before the
  per-unit output ceiling stopped it in its fourth unit. Its `converted` block
  names that run and the re-sized ceilings the stop informed; its digests are
  the bytes frozen at `c06ee085`.
- [The fourth held-out band](held-out/manifest-band-7000-7999.json), 7000–7999,
  is development data since 2026-09-15, for the same reason and kept the same
  way: the run of that date rendered thirteen of its prefixes — seeds 7001
  through 7016 in accepted order — before a candidate-arm ballot on seed 7016
  overran the 1,024-token per-call vote cap and came back as truncated JSON,
  stopping it in its 26th unit of 100. Its `converted` block names that run,
  the thirteen rendered seeds, [the diagnosis of
  2026-09-15](../../tasks/diagnosis-2026-09-15-truncation-stop.md) and the
  fifth authorization's limits card the stop informed; its digests are the
  bytes frozen at `1323cd75`.
- [Execution manifest](execution-manifest.md) binds every preregistration field
  for the fresh-model comparison, including the limits the owner authorized on
  2026-09-07. It authorizes no live call: a call additionally requires an
  explicit runner invocation naming that file, and no test or CI job performs
  one.
- [Development calibration, 2026-09-14](calibration-2026-09-14/CALIBRATION.md)
  measures what the provider CHARGES, on the first five accepted seeds of the
  converted 3000–3999 band, both arms, once, under the calibration limits. It
  grades nothing — no grader ran, no paired statistic was computed and no
  meeting outcome is recorded — so it measures nothing about the candidate's
  merit and no unit of it counts towards the primary outcome. Its output is the
  per-arm, per-call-type token profile, zero refusals and zero defaults on the
  corrected account prompts, and a re-sized ceiling proposal that authorizes
  nothing.
- [Development calibration 2, 2026-09-15](calibration-2-2026-09-15/CALIBRATION.md)
  measures what the FIFTH run would draw: the first sixty accepted seeds across
  the converted bands in the order they were converted — all fifty of the
  3000–3999 record then 5000–5009 of the 5000–5999 record — both arms, once, at
  the run's own caps and under the calibration-2 limits. It grades nothing
  either, and for the same reasons. Its output adds the unit of account the
  fourth run's stop needed: the two call schedules split by the author's hidden
  role, with the prose-field lengths, the truncation count and its
  `finish_reason`, the count of impostor ballots that open by naming that role
  or a kill, and the pre-declared per-arm public-transcript role-leak count. It
  measured zero truncations in sixty impostor-authored candidate ballot draws,
  zero refusals and zero defaults, and a ceiling proposal whose run-level input
  figure the standing authorization does not yet clear — which is a finding for
  the fifth authorization card and authorizes nothing here.
- [Run of 2026-09-16](run-2026-09-16/RESULTS.md) is the fifth held-out attempt
  and the first COMPLETE one: fifty paired seeds of band 8000–8999, both arms,
  one sitting, 601 attempts, all 100 units, no stop and no resumption, $0.00
  marginal. Unlike the calibrations it DOES grade, and its result is a
  measurement rather than an adoption: `repaired_clock` scored the primary
  outcome 0 of 50 and `combined_accounts` 2, so `b = 2`, `c = 0`, the exact
  McNemar p is 0.5 against a bar of 0.05 and the net paired difference is 2
  against a bar of 10; the candidate ejected 12 players to the reference's 1
  with 8 of the 12 wrongful, so the wrongful-ejection bound fails at +7 against
  a permitted 2. All three clauses of the decision rule fail, the result is
  inconclusive, the candidate does not advance and is not rejected, and the two
  one-sided effects the manifest declared for the v4 revision are what the
  reading has to be held against. The pre-declared leak column and the
  role-split ballot profile are reported beside it, and every accepted seed of
  the band is now development data.

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
