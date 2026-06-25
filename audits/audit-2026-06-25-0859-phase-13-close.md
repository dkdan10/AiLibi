# Phase 13 close-audit — the meeting's mechanism is BUILT, the 9B can't drive it

**Date:** 2026-06-25
**Scope:** Close-audit for Phase 13 (pre-ML grounding → deduction rework → *make the meeting decide*).
Characterizes the combined **13.12 re-record** that is now the committed baseline on `main` (PR #195,
`58ee87f`) and that **failed its headline gate**. Grounds every number in the committed data
(`replays/samples/{9p2i,4p1i}/tournament-eval-report.json`, `experiments/lab/results-rubric-score.json`),
not session memory.
**Verdict in one line:** the forward-redesign **plumbing is verified present and correct**, but the
local `qwen3.5:9b` **converts almost none of it** — so Phase 13 closes with its thesis (*the meeting
decides*) **UNVALIDATED**, blocked on model capability + an information-poverty confound. The re-record
is kept as the **honest final-9B baseline**; Phase 14 (model migration) carries this same gate forward.

---

## 1. The gate scorecard (13.12 contract → committed 9p2i: 50 games / 195 meetings)

| Gate term | Required | Committed actual | Verdict |
|---|---|---|---|
| **R1 eject-decided win share** | **UP from 6/50** | **3/50 (6%)** — *down* | ❌ **FAIL (headline)** |
| R4 wrong-ejection games | flat, ≤ +2 | **4** (down from 6) | ✓ |
| Impostor win | ≥ 14% (Phase-11 floor) | **84% (42/50)** | ✓ floor / ❌ crater |
| R7 strong-evidence meeting share | > 0 | **13/195 (7%)** | ✓ |
| geomean ranks eject-decided > stopwatch | yes | 74.2 / 62.1 / 52.5  >  ≤ 33.7 | ✓ |

**4 of 5 terms passed — but the one that *is the phase* failed.** R1 (the meeting deciding the game)
fell 6→3; the impostor win rate blew through the 14% floor to **84%**, i.e. crew win collapsed to 16%.
The **abandon-branch fired correctly** (R1 down → never silently merged as a "win"); the owner then
elected to keep it as a documented baseline (§5), not as a passing gate.

---

## 2. What Phase 13 built (all merged before the re-record)

The substrate the re-record runs *under* is real and landed:

- **13.1** rubric repair (R2/R3/R7 perverse gradients removed) — the rubric is now safe as a held-out gate.
- **Wave B spine (13.2–13.5, 13.7)** — the meeting-time **inferential contradiction detector** (three
  kinds: `alibi_conflict` / `alibi_vs_sighting` / `alibi_vs_physical`, WEAK/STRONG classified) + belief
  wiring + graduated corroboration spread.
- **13.6** prompt rework (richer testimony elicitation + breadcrumb render).
- **13.8** asymmetric **single-room vision** (crew `same_room_only` / impostor `same_room_and_adjacent`).
- **13.9** enriched same-room perception (activity + co-presence + transitions, firewall-gated).
- **13.10** **redistribute** the dead-crewmate task rule (replace `drop`) — removes the crew task-win crutch.
- **Wave E (13.13/13.14/13.15)** the forward-redesign minimal fix: de-imperative the §4.6 vote gate
  (non-directive prompt, deterministic tally floor stays) · promote `alibi_vs_sighting` to STRONG (light
  R7) · geomean(D1–D4) held-out referee.

---

## 3. The mechanism is verified PRESENT — every Wave-E lever did its job

Read against the committed data, the forward-redesign worked **exactly as designed**:

- **R7 is lit:** 13/195 (7%) strong-evidence meetings — the 13.14 detector fires on live recorded data
  (was 0/114 for the entire project before). Mechanism ✓.
- **The geomean referee ranks correctly:** the **3 eject-decided games are the top 3 scores** of all 50
  (seed 46 = 74.2, seed 28 = 62.1, seed 38 = 52.5), far above every stopwatch game (≤ 33.7). The 13.15
  rubric distinguishes a deduction win from a clock win as intended. Mechanism ✓.
- **No railroad regression:** R4 wrong-ejection games = **4, down from 6** — the de-imperatived gate +
  lone-STRONG did **not** over-eject crew (the conversion probe's +2 worst-case did not materialize;
  it came in *negative*). The anti-cascade tally floor held. Mechanism ✓.
- **Redistribute lengthened games:** meetings/game **2.3 → 3.9** (histogram now reaches 6–7/game); the
  runway for deduction arcs exists. Mechanism ✓.

**Every part of the machine that was supposed to *enable* a deciding meeting is functioning.**

---

## 4. …but the 9B does not DRIVE it — the conversion is the failure

The driver, not the mechanism, is where it breaks:

- **eject-rate 9%** — 177 of 195 meetings SKIP; only 18 eject (14 impostor / 4 crew).
- **only 3/50 games are eject-decided** (R1 = 6%); 42/50 are **IMPOSTOR_PARITY** (the histogram is
  `{IMPOSTOR_PARITY: 42, CREWMATE_TASKS: 5, CREWMATE_EJECT: 3}`).
- mean interestingness 31.2; only **1** R5 win-shape clears 10%.

**Root cause (this session's diagnosis, consistent with the data): an information + model bottleneck,
not a vote-mechanism bug.** Single-room vision (13.8) starves crew observation, which drops the
cross-speaker detector's *precision* on the new substrate to ~45%. Faced with a 45%-noisy signal and a
now-**non-directive** gate, the de-imperatived 9B **correctly SKIPs** rather than railroad on noise — so
meetings don't decide, and once redistribute (13.10) removes the task-win crutch, impostors win by
**parity**. This is the **first** recorded run combining **LLM voting + single-room vision**, so this
interaction is newly observed — the changes "designed to hinder crew" (single-room vision, redistribute,
LLM voting) all landed together and compounded.

The de-imperatived skip is **adaptive, not broken**: on a 45%-precise signal, forcing ejections would
*raise* R4 (wrong ejections), not R1. The bottleneck is upstream of the vote — the crew cannot *see*
enough to corroborate, and the 9B cannot *reason* its way past that scarcity.

---

## 5. Owner decision — keep it as the final-9B baseline

The re-record is **merged and kept** (PR #195) as the **honest final record of the local `qwen3.5:9b`
era** under the complete Phase-13 substrate. Rationale (owner, this session):
- the substrate changes are **intended** to make crew *earn* the win by deduction — an 84% impostor rate
  on a model that *can't* deduce is the expected, informative outcome, not a defect to patch away;
- it is a clean, documented **before-picture** for the model migration — the mechanism is proven present,
  so any post-migration R1 lift is attributable to the model/vision, not to new plumbing;
- 13 h local re-records on a small model are not a sustainable iteration loop regardless.

---

## 6. Forward — Phase 14 = model migration, carrying THIS gate

Phase 14 migrates the LLM to a pinned, flat-rate cloud model (Featherless AI candidate). The close
explicitly hands these forward (see the strategic write-up this session):

1. **Phase 14's success gate is *this* gate, re-run** (R1 up, R4 flat, impostor ≥ 14%, R7 > 0, geomean
   ranks eject-decided above stopwatch). The migration must *prove the meeting decides*, not merely swap
   providers. A passing re-record retroactively validates the Phase-13 mechanism as model-bound.
2. **Control the confound:** a cheap 2-variable smoke (new-model × {single-room, wider} vision) on a
   small seed set, *before* the full re-record. If R1 rises under wider vision but not single-room, the
   bottleneck is the **information** (13.8 vision), an owner balance lever — not the model.
3. **Pin the snapshot** ("frozen by name, not behavior"): the LLM layer is recorded+replayed, so a cloud
   model that silently rotates breaks replay determinism. Pin a snapshot, stamp baselines with it,
   confirm throughput/pinning before committing the phase.

---

## 7. Not resolved by this close (open, carried forward)

- **R4 threshold-inversions = 201** (rubric "hard floor 0" diagnostic) — needs a look during Phase-14
  re-record verification; not gate-blocking but flagged.
- **R2 impostor `do_task` emissions** still `NEEDS-10.16` (action-by-role ingest) — the blending metric
  is unmeasured.
- **Whether single-room vision stays** is an owner balance decision deferred to the Phase-14 confound smoke.
- **Phase-C ML** (the destination) is unchanged and sits *after* a passing migration re-record: LLM-free
  physical-suspicion-RANK surrogate inner loop + impostor tactical training + real-LLM selection gate +
  geomean held-out referee; co-evolution stability the open engineering problem.
