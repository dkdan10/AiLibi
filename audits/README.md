# Audits index

Every audit in this directory, once, with one line saying what it is. The
records are never rewritten — a correction is an additive, dated erratum inside
the record it corrects — so an old audit is a snapshot of what was known then,
not a claim about today. The current state is on the
[README](../README.md) and in [docs/history.md](../docs/history.md); the
vocabulary is in [docs/glossary.md](../docs/glossary.md).

Two audits with the same date and different suffixes (`-claude`, `-codex`,
`-reconciled`) are one review: two AI auditors run independently, then a third
pass reconciles them row by row. All of them were commissioned by me; none is a
third-party review.

---

## Read these three first

1. [audit-phase-19-input-claude.md](audit-phase-19-input-claude.md) — an
   independent audit run from a fresh clone: 18 games read end to end, all 300
   replays parsed, the vent-sighting cross-tab and four traced injustice classes.
   It proves a stranger can reproduce every derived metric from committed bytes.
2. [audit-phase-19-triage.md](audit-phase-19-triage.md) — the reconciliation of
   that audit against a second, independent one by a different model. It refutes
   a headline term from one of its own sources rather than absorbing it.
3. [audit-phase-18-close.md](audit-phase-18-close.md) — the close of the ML
   phase, and the clearest example of the machinery holding under a result
   nobody wanted.

## The 2026-08-19 review — [`review-2026-08-19/`](review-2026-08-19/D/FINAL-synthesis.md)

A directory rather than a file: a three-track review of the whole tree —
**A** gameplay, **B** code, **C** portfolio and front door — plus **D**, the
synthesis that ruled between them and produced the phase-20 plan. Start at
`D/FINAL-synthesis.md`; each track has its own `collated-findings.md`.

Two more directories sit beside the records: `prompts/` holds the prompts the
early audits were commissioned with, and `workflows/` holds the scripts that
extracted their gameplay facts. The `baseline*-final-measure.json` files are
recorded measurements, not prose.

## The 2026-08-26 Wave-0 audit — [`review-2026-08-26/`](review-2026-08-26/README.md)

The two-track pre-phase audit that grounds Phase 21: **A** gameplay on the
baseline-7 bytes, **B** code-up with the ML re-ground's readiness as its
centerpiece — blind to each other, every finding adversarially re-verified,
per-claim evidence in each track's `collated-findings.md`. Start at the
directory's `README.md`, which carries the tallies and the proposed routing.

---

## Phases 0–2 — scaffolding and the engine

- [audit-2026-05-09-1901.md](audit-2026-05-09-1901.md) — architecture and
  readiness through the first tactical task.
- [audit-2026-05-10-0721.md](audit-2026-05-10-0721.md) — phase-2 checkpoint:
  memory, perception and pathfinding as built.

## Before phase 3 — the meeting layer's readiness

- [audit-2026-05-15-0115-claude.md](audit-2026-05-15-0115-claude.md) —
  pre-phase-3 checkpoint (Claude).
- [audit-2026-05-15-0124-codex.md](audit-2026-05-15-0124-codex.md) — the same
  checkpoint, independently (Codex).
- [audit-2026-05-15-0225-reconciled.md](audit-2026-05-15-0225-reconciled.md) —
  the two reconciled.
- [audit-2026-05-16-0023-codex.md](audit-2026-05-16-0023-codex.md) — the
  re-audit after the first round of fixes (Codex).
- [audit-2026-05-16-0024-claude.md](audit-2026-05-16-0024-claude.md) — the same
  re-audit (Claude).
- [audit-2026-05-16-0036-reconciled.md](audit-2026-05-16-0036-reconciled.md) —
  the re-audit reconciled.
- [audit-2026-05-16-0009-pre-phase-3-verification.md](audit-2026-05-16-0009-pre-phase-3-verification.md)
  — verification that the agreed fixes actually landed.

## Phase 3 — meetings, voting, contradiction detection

- [audit-2026-05-16-0611-claude.md](audit-2026-05-16-0611-claude.md) —
  checkpoint after the first meeting tasks.
- [audit-2026-05-16-2239-claude.md](audit-2026-05-16-2239-claude.md) —
  checkpoint after voting and contradiction detection.

## Before phase 4 — the first real-provider evals

- [audit-2026-05-25-0357-claude.md](audit-2026-05-25-0357-claude.md) —
  pre-phase-4 checkpoint (Claude).
- [audit-2026-05-25-0402-codex.md](audit-2026-05-25-0402-codex.md) — the same,
  independently (Codex).
- [audit-2026-05-25-0414-reconciled.md](audit-2026-05-25-0414-reconciled.md) —
  the two reconciled.
- [audit-2026-05-25-0345-pre-phase-4-verification.md](audit-2026-05-25-0345-pre-phase-4-verification.md)
  — verification that the fixes landed.
- [audit-2026-05-25-0547-pre-phase-4-real-provider-eval.md](audit-2026-05-25-0547-pre-phase-4-real-provider-eval.md)
  — the first run against a real model.
- [audit-2026-05-25-1539-pre-phase-4-real-provider-eval.md](audit-2026-05-25-1539-pre-phase-4-real-provider-eval.md)
  — second run.
- [audit-2026-05-25-1823-pre-phase-4-real-provider-eval.md](audit-2026-05-25-1823-pre-phase-4-real-provider-eval.md)
  — third run.
- [audit-2026-05-25-2018-pre-phase-4-real-provider-eval.md](audit-2026-05-25-2018-pre-phase-4-real-provider-eval.md)
  — fourth run.
- [audit-2026-05-25-2038-pre-phase-4-real-provider-eval.md](audit-2026-05-25-2038-pre-phase-4-real-provider-eval.md)
  — fifth run.
- [audit-2026-05-25-2138-pre-phase-4-real-provider-eval.md](audit-2026-05-25-2138-pre-phase-4-real-provider-eval.md)
  — sixth run.
- [audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md](audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md)
  — the run the phase-4 decision was taken on.
- [audit-2026-05-25-2320-seed-23-deep-debug.md](audit-2026-05-25-2320-seed-23-deep-debug.md)
  — one game read line by line to explain what those evals showed.

## Phase 4 — the spectator's data contract

- [audit-2026-05-26-2310-mid-phase-4-dto-claude.md](audit-2026-05-26-2310-mid-phase-4-dto-claude.md)
  — the sanitized DTO inventory, audited (Claude).
- [audit-2026-05-26-2309-mid-phase-4-dto-codex.md](audit-2026-05-26-2309-mid-phase-4-dto-codex.md)
  — the same, independently (Codex).
- [audit-2026-05-26-2316-mid-phase-4-dto-reconciled.md](audit-2026-05-26-2316-mid-phase-4-dto-reconciled.md)
  — the two reconciled.

## Phase 5 — eval metrics, and the MVP close

- [audit-2026-05-29-1334-mid-phase-5-metric-claude.md](audit-2026-05-29-1334-mid-phase-5-metric-claude.md)
  — metric correctness (Claude).
- [audit-2026-05-29-1334-mid-phase-5-metric-codex.md](audit-2026-05-29-1334-mid-phase-5-metric-codex.md)
  — metric correctness, independently (Codex).
- [audit-2026-05-29-1338-mid-phase-5-metric-reconciled.md](audit-2026-05-29-1338-mid-phase-5-metric-reconciled.md)
  — the two reconciled.
- [audit-2026-05-30-0059-mvp-close.md](audit-2026-05-30-0059-mvp-close.md) —
  the MVP close: what phases 0–5 delivered and what they did not.

## Phases 6–7 — repair, then impostor coordination

- [audit-2026-05-30-1827-post-phase-6-real-provider-eval.md](audit-2026-05-30-1827-post-phase-6-real-provider-eval.md)
  — the eval after the post-MVP repair pass.
- [audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md](audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md)
  — why games so rarely reached a meeting at all.
- [audit-2026-06-01-1425-gameplay-data.md](audit-2026-06-01-1425-gameplay-data.md)
  — gameplay data, first of the series.
- [audit-2026-06-02-2112-gameplay-data.md](audit-2026-06-02-2112-gameplay-data.md)
  — gameplay data after the impostor-coordination wave.
- [audit-2026-06-03-1358-gameplay-data.md](audit-2026-06-03-1358-gameplay-data.md)
  — gameplay data at the phase-7 close.

## Phase 8 — the deduction substrate

- [restructure-impact-map-2026-06-04-0223.md](restructure-impact-map-2026-06-04-0223.md)
  — what the restructure would touch, priced before it was authored.
- [audit-2026-06-06-0632-gameplay-data.md](audit-2026-06-06-0632-gameplay-data.md)
  — gameplay data on the new substrate.
- [audit-2026-06-07-0717-gameplay-data.md](audit-2026-06-07-0717-gameplay-data.md)
  — the same, one wave later.
- [audit-2026-06-09-0347-gameplay-data.md](audit-2026-06-09-0347-gameplay-data.md)
  — the phase-8 close reading.

## Phases 9–10 — conversion quality and the conviction engine

- [audit-2026-06-10-1820-gameplay-data.md](audit-2026-06-10-1820-gameplay-data.md)
  — gameplay data after the producer-hygiene wave.
- [audit-2026-06-11-2218-gameplay-data.md](audit-2026-06-11-2218-gameplay-data.md)
  — the phase-10 wave-0 reading.
- [audit-2026-06-13-1816-gameplay-data.md](audit-2026-06-13-1816-gameplay-data.md)
  — the wave-1 reading.
- [audit-2026-06-14-1631-gameplay-data.md](audit-2026-06-14-1631-gameplay-data.md)
  — the phase-10 close.

## Phases 11–13.5 — information economy, then grounding

- [audit-2026-06-22-0446-ground-up.md](audit-2026-06-22-0446-ground-up.md) — a
  ground-up re-read of the whole system, commissioned mid-phase-13.
- [audit-2026-06-22-1558-forward-redesign.md](audit-2026-06-22-1558-forward-redesign.md)
  — what a redesign would have to change, written against that re-read.
- [audit-2026-06-22-2149-wave-e-review.md](audit-2026-06-22-2149-wave-e-review.md)
  — the review of the resulting plan and its contracts.
- [audit-2026-06-24-1840-gameplay-data.md](audit-2026-06-24-1840-gameplay-data.md)
  — the gameplay reading on the re-recorded set.
- [audit-2026-06-25-0859-phase-13-close.md](audit-2026-06-25-0859-phase-13-close.md)
  — the phase-13 close: the mechanism is built, the model of the day cannot
  drive it.

## Phase 14 — the hosted provider, and what to do next

- [audit-2026-07-01-phase-14-baseline1-characterization.md](audit-2026-07-01-phase-14-baseline1-characterization.md)
  — the first reference recording on the new model: the problem inverted.
- [audit-phase-14-close.md](audit-phase-14-close.md) — the phase-14 close on
  reference recording 2.
- [post-phase-14-pause.md](post-phase-14-pause.md) — a health assessment and a
  direction call before committing to a long program.
- [post-phase-14-ML-planning.md](post-phase-14-ML-planning.md) — the case for
  machine-learned tactical play between meetings.
- [post-phase-14-ML-training-signal.md](post-phase-14-ML-training-signal.md) —
  what a usable training signal would have to look like.
- [post-phase-14-Voice-and-Judgment-planning.md](post-phase-14-Voice-and-Judgment-planning.md)
  — the plan for personas, evidence-grounded conviction and citation gating.

## Phase 15 — cleanup, then the training environment

- [audit-phase-15-wave0-close.md](audit-phase-15-wave0-close.md) — reference
  recording 3: the two measured evidence holes closed.
- [audit-phase-15-pause.md](audit-phase-15-pause.md) — the mid-phase pause: the
  seven decisions and the authorization to continue.
- [review-phase-15-midwave.md](review-phase-15-midwave.md) — an implementation
  review of the merged work and the contracts still to dispatch.
- [audit-phase-15-close.md](audit-phase-15-close.md) — the phase-15 close: the
  learned impostor policy ships opt-in.

## Phase 16 — voice and judgment

- [audit-phase-16-model-lock.md](audit-phase-16-model-lock.md) — the model lock,
  ruled GO on a two-evidence-set reading.
- [audit-phase-16-baseline-4.md](audit-phase-16-baseline-4.md) — reference
  recording 4: the model-only re-record, isolated from every other change.
- [audit-phase-16-close.md](audit-phase-16-close.md) — reference recording 5 and
  the phase close.

## Phase 17 — co-adaptation

- [audit-phase-17-absence-gate.md](audit-phase-17-absence-gate.md) — the
  absence-prior graduation and vent-widening ruling.
- [audit-phase-17-close.md](audit-phase-17-close.md) — NO-FLIP: the default
  mover stays scripted, and no new reference recording is made.

## Phase 18 — the machine-learning phase

- [audit-phase-18-planning.md](audit-phase-18-planning.md) — the research
  dossier the phase was priced from.
- [audit-phase-18-meeting-gate.md](audit-phase-18-meeting-gate.md) — the
  meeting-layer package probe and its ruling.
- [audit-phase-18-baseline-6.md](audit-phase-18-baseline-6.md) — reference
  recording 6: the meeting-layer graduation and the atomic re-record.
- [audit-phase-18-emergence-preregistration.md](audit-phase-18-emergence-preregistration.md)
  — the falsifiability contract: eight instruments and their bars, committed
  before the measurement.
- [audit-phase-18-flip-emergence.md](audit-phase-18-flip-emergence.md) — the
  two-axis reading, derived cell by cell.
- `audit-phase-18-close.md` — the phase close, linked at the top of this page.

## Phase 19 — review and refresh

- [audit-phase-19-planning.md](audit-phase-19-planning.md) — the
  review-and-refresh plan.
- `audit-phase-19-input-claude.md` — the independent input audit, linked at the
  top of this page.
- [audit-phase-19-input-codex.md](audit-phase-19-input-codex.md) — the second,
  independent input audit by a different model.
- `audit-phase-19-triage.md` — the reconciliation of the two, linked at the top
  of this page.
- [audit-phase-19-close.md](audit-phase-19-close.md) — the phase close, with
  nothing recorded and the next decision routed to the owner.

## Phase 20 — evidence honesty

- [audit-phase-20-planning.md](audit-phase-20-planning.md) — the plan: the front
  door made true, the inference channel repaired, one pre-registered record.
- [audit-phase-20-preregistration.md](audit-phase-20-preregistration.md) — the
  falsifiability contract for that record, committed before it is taken.
- [audit-phase-20-counterfactual.md](audit-phase-20-counterfactual.md) — the
  offline counterfactual: every predictable bar predicted on frozen bytes, and
  the cells no offline instrument can reach, published before the record.
- [audit-phase-20-smoke.md](audit-phase-20-smoke.md) — the smoke record: live
  seeds at the full slate into a scratch directory, the validity gate, the
  observed lever coverage, and the GO/ABANDON call before the record starts.
- [audit-phase-20-baseline-7.md](audit-phase-20-baseline-7.md) — the record
  itself: 300 games at the frozen slate, the pre-registered read bar by bar, and
  the decision the arithmetic selected. FINDING: two bars missed, neither
  re-priced — and the owner then adopted the substrate over that verdict by
  explicit override (§6.1), which is why the ladder tip stands at baseline 7.
- [audit-phase-20-close.md](audit-phase-20-close.md) — the phase close: the
  whole gate re-run at close HEAD in both evidence states, every dispatched
  contract re-verified, the before/after read back bar by bar, the defects it
  found, and the balance wave put to the owner.
