# Gameplay-data close audit — Task 13.12 redistribute + Wave-E re-record

**Date:** 2026-06-24
**Set:** `replays/samples/9p2i` (50 games / 195 meetings) + `replays/samples/4p1i` (50 games / 40 meetings)
**Model:** `qwen3.5:9b` (think=false, local Ollama, $0)
**Substrate:** `canonical_1.yaml` `dead_task_rule: drop → redistribute` + the merged Wave-E
(13.13 de-imperative §4.6 gate / 13.14 `alibi_vs_sighting`→STRONG / 13.15 geomean rubric);
recorded under the bumped prompts `accusation_round.v9 / crewmate_report.v8 / impostor_report_v6 / vote_ballot/v7`.
**Provenance tuple** (cadence-doctrine rule 8): set dir + this branch's recording commit + `qwen3.5:9b`.

## Verdict

**The gate's headline (R1 eject-decided UP) and balance criteria were NOT met. The owner
(2026-06-24) accepted the re-record as the new committed baseline ahead of a potential model
migration** — the structural substrate works (stopwatch broken, meetings doubled, the R7 detector
surface lit), and the crew's failure to convert is read as the frozen-LLM capability ceiling a
migration would address. This is an explicit owner OVERRIDE of the contract's abandon-default, NOT a
passing gate. The close audit's load-bearing job — confirm no firewall/integrity/determinism breach —
is **GREEN**.

## Gate result (9p2i, baseline `drop` → new `redistribute`+Wave-E)

| Criterion | Baseline | New | Met? |
|---|---|---|---|
| **R1 eject-decided** | 6/50 | **3/50** (seeds 28,38,46) | ❌ DOWN (the headline goal) |
| **Impostor win** | 14% (7/50) | **84% (42/50)** | ⚠️ passes the ≥14% floor, but crew cratered |
| **R4 wrong-eject** | 6 | 4 | ✅ did not rise (≤ +2) |
| **R7 strong-flag meetings** | 0/114 | **26/195** (72 strong flags) | ✅ detector lit |
| **Geomean ranking** | — | eject-decided [52.5–74.2] > stopwatch [0.6–33.7] | ✅ ranks correctly |

reason_counts: `IMPOSTOR_PARITY 42, CREWMATE_TASKS 5, CREWMATE_EJECT 3` (the stopwatch broke:
CREWMATE_TASKS 37→5; meetings 114→195).

**Mechanism (airtight from the bytes):** redistribute removed the crew's out-task win path, so the crew
must now eject BOTH impostors to win. They eject ONE often (14 impostor ejections) but BOTH rarely (3
games); the 2 impostors kill to parity first. ~30 ex-task-wins became impostor parity-LOSSES, not
ejection-wins. The de-imperatived §4.6 gate (13.13) compounds this: **`threshold_inversions` 0→201** —
crew now decline met-threshold targets by design, which lowered R4 (6→4) AND R1. The 4p1i set, by
contrast, is well-balanced (CREW 29 / IMP 21 = 42% impostor) — with 1 impostor, ejecting it ends the
game, so the eject-one dynamic does not crater.

## Firewall / integrity / determinism — the close gate (ALL GREEN)

- **Determinism:** both sets reconstruct byte-identically (`verify_samples.sh`, 50/50 each, clean).
- **Leak firewall:** `tests/api/test_leak.py` + `tests/observation/test_leak_property.py` green on the
  new bytes; roles / teammates / kill-attribution never leak. The redistribute re-key surfaces only a
  bare, owner-scoped map id (the property test was re-anchored to model current ownership — owner-approved,
  every leak assertion intact).
- **Mind-inspector render assertion:** 195 agent-perspective belief frames scanned across all 50 seeds,
  **0 role-bearing leaks** — the 13.13/13.14 fields surface no role in the inspected agent's view.
- **Friendly-fire:** `impostor_victim_kills == 0` (245 kills). **Betrayal/firewall breaches:** 0.
- **Extractor self-checks:** all OK (after realigning the extractor's genuine-class re-derivation with
  the shipped one-home classifier — the merged 10.10 proxy-intra-turn exclusion was missing).

## Decisions baked into this re-record (full detail in the PR)

1. **4p1i recorded at tpc=1** (owner call — keep the flat-baseline descriptor-less identity).
2. **Two stale-replica tooling fixes** the redistribute bytes exposed (both realign a drifted parallel
   impl with its documented single-source-of-truth, necessary to regenerate the in-scope rubric):
   `rubric_score.py` now tolerates an empty `suspicion_graph_by_voter` (a no-accusation SKIP meeting);
   `extract_gameplay_facts.py` genuine-class re-derivation gained the 10.10 `WEAK_REASON_PROXY_INTRA_TURN`
   exclusion.
3. **Firewall test re-anchored** (owner-approved) to model the redistribute re-key without weakening any
   leak assertion.
4. **~49 era-pin re-anchors** (3× the contract estimate — the flip + the Wave-E prompt bumps cascade
   broadly): the recording-SHA / prompt-version / computed-value pins across `tests/`, plus the
   canonical-flip cascade (engine drop-tests → explicit drop-maps, the kill-gift map, the balance canary).

## Next

Run the close-audit verdict through the owner, then **Phase C ML** (the model-migration the new baseline
is built to measure against). See `[[project_ml_agents_plan]]`.
