# Phase history

One paragraph per phase, in order. Each names its contract — the document the
agents were dispatched against — and its close audit where one exists. Close
audits begin at the MVP close and resume at phase 13; the phases in between
closed inside their contract files, which carry the per-task status lines.

The short version is on the [README](../README.md) as a table. Vocabulary that
turns up below is defined in the [glossary](glossary.md); the numbers and what
they do and do not show are in the [reading guide](reading-guide.md).

---

## The MVP: phases 0–5

**Phase 0 — scaffolding.** Repository, CI, the project skeleton, the lint rule
that enforces the observation firewall, and a deliberately failing leak test, so
the firewall had a gate before it had an implementation.
[Contract](../tasks/phase-0.md).

**Phase 1 — the engine.** World state, rules, seeded RNG, visibility, the replay
recorder and the leak test made to pass. The determinism property — one seed,
one set of bytes — dates from here and has never been relaxed.
[Contract](../tasks/phase-1.md).

**Phase 2 — tactical agents.** Memory, perception, pathfinding, the
finite-state-machine policies that still ship as the default mover, and the
headless orchestrator plus tournament harness that every later measurement runs
on. [Contract](../tasks/phase-2.md).

**Phase 3 — the meeting.** LLM-driven meetings, voting, and contradiction
detection across the transcript. The provider-neutral client, the deterministic
fake provider, and robust JSON extraction with failure recording all land here.
[Contract](../tasks/phase-3.md).

**Phase 4 — the spectator.** A FastAPI plus React replay viewer, replay-only by
construction: it reads saved replay files and never drives the engine. The
sanitized DTO inventory dates from this phase.
[Contract](../tasks/phase-4.md).

**Phase 5 — eval.** Metric analyzers over a typed tournament report, the
tournament dashboard, and the prompt-regression close gate that turns "change a
prompt, watch a metric move, attributably" into a test. This is the MVP.
[Contract](../tasks/phase-5.md) ·
[close audit](../audits/audit-2026-05-30-0059-mvp-close.md).

## Making the agents reason: phases 6–13.5

**Phase 6 — repair and hardening.** The post-MVP cleanup pass: the defects the
close audit surfaced, closed before anything was built on top of them.
[Contract](../tasks/phase-6.md).

**Phase 7 — impostor coordination, and a change of eval model.** Impostors
learned to coordinate, and the teammate firewall — a ballot targeting a fellow
impostor is deterministically rewritten to SKIP — landed here. The eval moved
off a hosted commercial model onto a local open one, which made large sample
runs free. [Contract](../tasks/phase-7.md) · [plan](../tasks/phase-7-plan.md).

**Phase 8 — deduction substrate.** A restructure of how evidence reaches the
table, after the phase-7 measurements showed the meeting ejecting people without
deciding anything. [Contract](../tasks/phase-8.md).

**Phase 9 — producer hygiene and conversion.** The quality of what agents
*produce* into a meeting, and how much of it converts into a correct ejection.
[Contract](../tasks/phase-9.md).

**Phase 10 — the conviction engine.** Repair of the flag-to-ballot-to-tally
pipeline, plus the crew's evidence economy — what the table is actually handed
to reason with. [Contract](../tasks/phase-10.md).

**Phase 11 — the impostor's information economy.** Vents and sabotage became
real impostor moves rather than decoration, then were balanced against the
crew's side of the economy. [Contract](../tasks/phase-11.md).

**Phase 12 — the front end.** The spectator rebuilt as a product: map playback
with a fog-of-war perspective toggle, meeting transcripts with ballots and
flags, per-agent memory snapshots, a belief matrix, a guided tour, keyboard
transport. [Contract](../tasks/phase-12.md).

**Phase 13 — pre-ML grounding.** Rubric repair and a deduction rework, intended
to make the meeting decide rather than merely eject. The mechanism was built and
verified present; the model of the day could not drive it, which is what sent
the project to a memory-correctness pass and then a model migration.
[Contract](../tasks/phase-13.md) ·
[close audit](../audits/audit-2026-06-25-0859-phase-13-close.md).

**Phase 13.5 — memory correctness.** Spoken testimony had been collapsing into a
suspicion scalar before it reached anyone's beliefs. This phase took the fix
down to the substrate rather than papering over it at the prompt.
[Contract](../tasks/phase-13-5.md).

## Measurement and the ML program: phases 14–18

**Phase 14 — the hosted provider.** A hosted OpenAI-compatible provider, and the
model and prompt migration onto it. The first numbered reference recording
follows from this migration. [Contract](../tasks/phase-14.md) ·
[close audit](../audits/audit-phase-14-close.md).

**Phase 15 — cleanup, then the training environment.** An evidence-substrate
cleanup wave closing on reference recording 3, then the machine-learned tactical
policy program proper: measurement harness, training environment, calibration
corpus, a rebuilt meeting surrogate, and a multi-method bake-off with a mid-phase
pause that picked the winning method on measured numbers before any
productization was authored. The learned impostor policy shipped opt-in.
[Contract](../tasks/phase-15.md) ·
[close audit](../audits/audit-phase-15-close.md).

**Phase 16 — voice and judgment.** Citation-gated ballots (every eject ballot
must cite a transcript turn or an observation id, and compliance reached 1.000
at the close), information pooling via a roll-call round and vouching, and
personas — all on the probe-locked model. Three settings graduated together at
that close and became unconditional: the citation gate (`citation_gate`), the
hard-evidence gate (`hard_evidence_gate`) and observation-id rendering
(`observation_id_rendering`). Closed on reference recording 5; the absence prior
(`absence_prior`) stayed off there as a recorded ruling pending roll-call
calibration, and graduated at the next recording. Reference recording 4, one
phase earlier, was the model-only swap, isolated from every behavioural change.
[Contract](../tasks/phase-16.md) ·
[close audit](../audits/audit-phase-16-close.md).

**Phase 17 — co-adaptation.** The monitoring corpus was re-recorded on the
current substrate, the ballot surrogate re-fit to the first GO verdict at the
training-time-runner tier, and the full impostor and crew slate re-run and
re-selected under the new referee. The evidence-gated default flip was ruled
FAIL: the leading learned mover kept a +0.16 win edge over the scripted one and
still failed the conversion floors, while the arm that passed the referee did so
at a 0.02 win rate — a pass bought by losing. No adoption.
[Contract](../tasks/phase-17.md) ·
[close audit](../audits/audit-phase-17-close.md).

**Phase 18 — the ML phase.** The meeting-layer package graduated crew-only at
the baseline-6 adopting record, with the monitoring corpus re-recorded on it. A
conviction model landed GO, and composed with the surrogate's retained ranking
channel into the meeting-outcome runner used for training rollouts.
Alternating-freeze co-evolution ran the impostor campaign, then the crew
campaign, and a real-model finalist eval fed a two-axis owner ruling: NO-FLIP —
every learned arm beat the same-seed scripted comparator on wins, by +0.12 to
+0.30, and every arm failed the supply and conversion floors, reproducing the
starved-economy shape on a co-adapted slate — and zero of the fourteen
pre-registered emergence rulings demonstrated, with two selected-for
kill-placement effects recorded as named findings rather than upgraded to fit
the claim. No crew adoption. [Contract](../tasks/phase-18.md) ·
[close audit](../audits/audit-phase-18-close.md).

## Review and refresh: phase 19

**Phase 19.** Chartered as review-and-refresh after the owner deferred
presentation work. It ran the front-door and in-code truth sweeps with
generated-fact checks, the spectator coherence pass and the static demo bundle,
the frontend test baseline, the deduction metrics and injustice fixtures, the ML
tier map with its retirements and report-honesty close, and a two-tier test
structure. All 28 contracts merged, and the phase closed with nothing recorded:
the substrate did not move, and the choice between an evidence-honesty substrate
phase and a presentation phase was routed to the owner.
[Contract](../tasks/phase-19.md) ·
[close audit](../audits/audit-phase-19-close.md).

## In progress: phase 20

**Phase 20** takes the presentation-and-honesty route out of that decision: the
front door made true, the inference channel repaired, and one pre-registered
record. [Contract](../tasks/phase-20.md).

---

## Where the sample sets came from

The 100 committed replays under `replays/samples/` are the adopting record for
reference recording 6. The meeting layer graduated **crew-only** at that
recording: the roll-call round, the endpoint-band whereabouts exemption, the
vent-placement contradiction variant (flag-minting plus the absent-set widening)
and the absence prior all became unconditional, beside the nine settings already
retired — thirteen graduated in total. The impostor-answer arm did not ship, so
the record was made in a bare environment with that toggle off
([`audits/audit-phase-18-baseline-6.md`](../audits/audit-phase-18-baseline-6.md)).

Each set's `MANIFEST.md` is the canonical provenance record, row by row: model,
prompt-template versions, the thirteen graduated settings stamped on every row,
refresh date, cost and outcome. `scripts/refresh_samples.sh` regenerates the
sets against the active provider and rewrites those rows;
`scripts/verify_samples.sh` replays every sample through the engine, free and
offline, and fails loudly the moment a recorded state hash stops reconstructing.

---

Back to the [README](../README.md), the [reading guide](reading-guide.md), the
[glossary](glossary.md), or the [audits index](../audits/README.md).
