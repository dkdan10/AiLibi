# Forward-Redesign probes — A-1 desk test + inferential-detector signal

**Date:** 2026-06-22
**Scope:** Two $0-offline probes over the committed `replays/samples/9p2i` set (50 games / 114
meetings / 39 ejections), de-risking the minimal fix recommended in
`audits/audit-2026-06-22-1558-forward-redesign.md` (steps 0 and 2) **before any code lands.**
**Reproduce:** `uv run python experiments/lab/forward_redesign_probes.py` (reads only committed
replays + roles; emits no files). The tally model replicates `meetings.voting.tally_ballots`
**exactly — 0/114 mismatches against the recorded outcomes.**

---

## Probe 1 — A-1 desk test: is de-imperative-ing the gate a rationale-text fix or an outcome lever?

A-1 rewrites `vote_ballot.j2` from the §4.6 "you MUST eject/skip" imperative to a non-directive
evidence line, keeping the deterministic tally floor. The desk test estimates the imperative's
effect on OUTCOMES by re-tallying the recorded ballots under counterfactual attributions:

- **imperative-only**: recorded ejections where the ejectee was accused, in the transcript, by
  **nobody** — a pure suspicion-graph/gate ejection.
- **LOOSE**: votes for a target nobody spoke an accusation against drop to SKIP (a voter may still
  concur with *someone's* spoken accusation).
- **BELIEF**: each voter votes only their *own* strongest spoken accusation, else SKIP.

| Measure | Result |
|---|---|
| recorded outcomes | 39 EJECT / 75 SKIP (tally replication 0/114 mismatch) |
| imperative-only ejections (ejectee accused by nobody) | **9 / 39 (23%)** |
| LOOSE counterfactual | EJECT→EJECT 26, **EJECT→SKIP 13**, SKIP→SKIP 75 |
| BELIEF counterfactual | EJECT→EJECT 1, **EJECT→SKIP 38**, SKIP→EJECT 1, SKIP→SKIP 74 |

**Verdict: A-1 is an OUTCOME lever, not a free rationale-text fix** (this corrects the report's
step-0 guess that "likely few outcomes change"). Requiring votes to be backed by *someone's*
spoken accusation already flips **13/39 ejections (33%)** to SKIP; requiring each voter to vote
their *own* accusation collapses **38/39**. That last figure is the prior audit's b1=27 finding
**quantified — spoken testimony has almost no causal path to the eject; the suspicion graph (via
the gate) drives it.** So removing the imperative *without* re-grounding the graph would crater R1
(ejections). **Implication: detector-first is empirically forced** — A-1 cannot ship before/without
the inferential detector + testimony-spread that give the model real STRONG evidence to vote on.
**Caveat:** A-1 keeps the rendered suspicion graph *visible* (just non-binding), so the true effect
lies at or below these bounds; only the step-1 real-LLM smoke measures it exactly. The desk test
bounds the lever; it does not replace the smoke.

---

## Probe 2 — inferential cross-speaker alibi-conflict detector: does R7 leave 0/114?

The committed (firsthand) detector emits only WEAK flags, so R7 (strong-flag meeting share) is
0/114. The B-spine proposes a firewall-clean STRONG class: an alibi (S claims room R over ticks
[f,t]) contradicted by **another** speaker's `saw_player(subject=S, room R2≠R, tick∈[f,t])`. The
probe measures this raw signal (no weak-guards / two-source conjunction yet) plus a ground-truth
ceiling (alibi vs the actual reconstructed position).

| Measure | Result |
|---|---|
| substrate richness | 179 alibis + 574 sightings; 110/114 meetings carry an alibi |
| **meetings with ≥1 cross-speaker alibi_conflict** | **56 / 114 (49%), on 36 / 50 seeds** |
| flagged-subject precision (raw) | **50 true-impostor (TP) / 11 crewmate (FP)** ≈ 82% |
| ground-truth ceiling (alibi vs actual position) | 58 provably-false impostor-alibis / 39 crew |

Spot-checked, the conflicts are real lies, not parsing artifacts:
- **seed-1 m0** — p-6 (impostor) alibis CAFETERIA[0–8]; crewmate p-2 saw p-6 in ENGINEERING@4 and
  STORAGE@5.
- **seed-2 m1** — p-4 (impostor) alibis ADMIN[16–20]; crewmate p-5 saw p-4 in EAST_HALL@20.

**Verdict: the inferential detector lights R7 decisively — 0/114 → 56/114** on 36 seeds at ~82%
raw precision. **The substrate is NOT starved**, and **"the detector is dead" was only ever true of
the *firsthand* detector** — the cross-speaker form has abundant signal. The 11 crew false-positives
are exactly the FP-suppression work the shipped detector still owes (the weak-guards +
two-source-conjunction toward the "~0 crew-named" bar; gp-3 "watch the games" is BLOCKING).

---

## Net

Both of the minimal fix's biggest uncertainties resolve **favorably for the plan's logic:**
1. **The detector spine is real** (R7 0 → 56/114) — lead with it.
2. **A-1 genuinely needs it** (de-imperative alone drops 13–38 of 39 ejections) — so **detector-first
   is empirically the correct sequencing**, not just a hunch.

The recommended minimal fix (A-1 + inferential detector + the epsilon-floored D-1 geomean) stands,
sharpened by one correction: **A-1 is load-bearing, not a freebie** — it ships *with* the detector
+ testimony-spread and is validated by the step-1 real-LLM smoke.

---

## Probe 3 — detector threshold sweep on the LIVE merged detector

Probe 2 hand-rolled the cross-speaker signal. This probe runs the **merged**
`meetings.transcript.detect_contradictions` on `model_validate`'d committed transcripts (0/114
validation fails), so the numbers are the real code's — and they **correct Probe 2's hopeful
framing.** Reproduce: `uv run python experiments/lab/forward_redesign_detector_sweep.py`.

The live detector emits **112 flags, every one WEAK** (111 `alibi_vs_sighting` + 1 `alibi_conflict`),
and **zero `alibi_vs_physical`**. R7 = 0/114 confirmed on the real code.

| Config | R7 (STRONG meetings) | Impostor / Crew flags | Precision |
|---|---|---|---|
| **Current (`MIN_VOICES`=2)** | **0 / 114** | 0 / 0 | — |
| `MIN_VOICES` = 1 | 0 / 114 | 0 / 0 | — |
| **Promote `alibi_vs_sighting` → STRONG** | **54 / 114** | 48 / 11 | **81%** |
| …only if ≥2 corroborating sightings | 14 / 114 | 10 / 5 | 67% |

- **`MIN_VOICES` is a dead knob.** The co-presence `alibi_vs_physical` path the forward-redesign hoped
  to tune produces **zero** flags on the room-only substrate, so lowering 2→1 changes nothing.
- **The only lever that lights R7 is promoting the single-witness `alibi_vs_sighting` band to STRONG**
  — exactly the signal the audit-9.7 fix deliberately down-weighted for precision. It gives **54/114
  at 81%**; the 11 crew flags are the 19% the down-weight was preventing.
- **Corroboration does not rescue precision** — ≥2 sightings *craters* both signal (54→14) and
  precision (81→67%). The "two-source conjunction" hope does not hold for this band.

**Verdict: R7=0 is a deliberate precision floor, not a config bug — there is no precision-safe knob,
so lighting R7 is a genuine precision/recall trade.** And ~81% is the right operating point: (1) it
matches the owner principle *innocents are ejectable, just not at random* — each flag is concrete
evidence ("your alibi says X, but you were seen in Y"), info-backed not a railroad; (2) some crew
flags are impostors *framing* a crewmate via a false sighting — desirable deception, not detector
error; (3) the flag is not the verdict — it adds suspicion, and the downstream plurality + the §4.6
floor (now A-1) mediate it, so 19% flag-FP ≠ 19% wrong ejections. The forward-redesign's **"~0 crew"
target was unrealistic on this substrate** (Probe 2's hand-rolled 56/114 @ 82% overstated the
precision the guarded code achieves); the honest target is **info-backed flags at ~80% precision,
gate-mediated**, with the real friendly-fire trade measured by the held re-record.

**Sizing:** the detector-tuning task is **not a config sweep** — it is a **classification change**
(promote the honest post-weak-guard `alibi_vs_sighting` set to STRONG so it crosses the gate);
`MIN_VOICES`/co-presence is shelved as an empty path.
