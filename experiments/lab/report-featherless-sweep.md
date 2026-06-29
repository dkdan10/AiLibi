# Lab report — Featherless model x thinking-mode sweep (Task 14.4)

**Decision informed:** which Featherless `(meeting_model, trigger_model, mode)` to lock at Task 14.6, and whether the Phase-13 information-ceiling hypothesis (`audits/audit-2026-06-25-0859-phase-13-close.md`) survives a stronger model. **Method:** the model-ceiling-vs-information design of `experiments/lab/report-model-ceiling-probe.md`, generalized across the Featherless slate over the SAME reconstructed `replays/samples/9p2i` contexts, on the PINNED 9B prompts, graded by the IDENTICAL mechanical `deflection_probe._grade`. **Cost:** $0 (Featherless flat-rate).

Slate substitution (live, 2026-06-29): the contract's owner-confirmed `Qwen/Qwen3-30B-A3B` and `zai-org/GLM-4-32B` ids 404 on the live endpoint; Featherless now serves the canonical revisions `Qwen/Qwen3-30B-A3B-Instruct-2507` and `zai-org/GLM-4-32B-0414`, substituted here (confirmed via `GET /models` + a generation preflight).

## Structured-output fidelity (parse-success under `json_object`)

Reply corpus, cover OFF, flag-OFF substrate (matched to the 9B reference):

| model | mode | parse-success | latency (isolated) | fit for sim? |
|---|---|---|---|---|
| **qwen3.5:9b (ref, Ollama)** | non_thinking | 16/16 (100%) | ~31s | yes (reference) |
| qwen3-32b | non_thinking | 16/16 (100%) | ~35.3s | yes |
| qwen3-32b | thinking | 16/16 (100%) | ~40.8s | yes |
| qwen3-30b-a3b | non_thinking | 16/16 (100%) | ~28.6s | yes |
| qwen3-30b-a3b | thinking | 16/16 (100%) | ~32.1s | yes |
| glm-4-32b | non_thinking | 0/16 (0%) | — | **NO** |
| cydonia-24b | non_thinking | 0/16 (0%) | — | **NO** |

## Model-ceiling-vs-information read (cover OFF, flag-OFF)

**Caveat — the 9B row is a RATE reference, not an item-matched control.** Only 3/16 of this sweep's hard reply contexts overlap the committed `results-model-ceiling-q9b.jsonl` (that file predates the current 9p2i recording, and `_select` picks the hardest body-meeting contexts of *each* recording). So compare the Featherless rows to each other on identical contexts; treat the 9B row as a prior-recording rate baseline. The load-bearing finding is the tell's PERSISTENCE across the Featherless slate, not its absolute level vs 9B.

| model | mode | deflect | self-co-loc (the *tell*) | self-flag |
|---|---|---|---|---|
| **qwen3.5:9b (ref)** | non_thinking | 10/16 (62%) | 11/16 (69%) | 4/16 (25%) |
| qwen3-32b | non_thinking | 10/16 (62%) | 4/16 (25%) | 9/16 (56%) |
| qwen3-32b | thinking | 12/16 (75%) | 5/16 (31%) | 6/16 (38%) |
| qwen3-30b-a3b | non_thinking | 12/16 (75%) | 6/16 (38%) | 6/16 (38%) |
| qwen3-30b-a3b | thinking | 12/16 (75%) | 6/16 (38%) | 5/16 (31%) |
| glm-4-32b | non_thinking | — (unfit) | — | — |
| cydonia-24b | non_thinking | — (unfit) | — | — |

## Cover-directive 2x2 (model x {cover OFF, cover ON-reply})

Self-co-location (the tell) with the cover directive OFF vs ON, flag-OFF:

| model | mode | cover OFF self-co-loc | cover ON self-co-loc | Δ |
|---|---|---|---|---|
| qwen3-32b | non_thinking | 4/16 (25%) | 1/16 (6%) | -19 pp |
| qwen3-32b | thinking | 5/16 (31%) | 6/15 (40%) | +9 pp |
| qwen3-30b-a3b | non_thinking | 6/16 (38%) | 6/15 (40%) | +3 pp |
| qwen3-30b-a3b | thinking | 6/16 (38%) | 5/16 (31%) | -6 pp |
| glm-4-32b | non_thinking | — | — | — |
| cydonia-24b | non_thinking | — | — | — |

**Quadrant verdict — BOTH, leaning INFORMATION CEILING.** The cover directive's effect on self-co-location is SMALL and INCONSISTENT across the fit Qwen3 cells (mean Δ +3 pp; it helps ≥10 pp in only 1 of 4 cells, and back-fires in others) — a far cry from its strong effect on the 9B's own contexts (cover cut self-co 55%→21% in `results-deflection-probe.jsonl`). So there IS a prompt-artifact component (the v5 directive never reaches the reply path today, audit gp-1) worth wiring in at 14.5, but it does NOT reliably dissolve the tell on the stronger models. The decisive ceiling signal is the self-FLAG floor: it never falls below 31% on any fit model and exceeds the 9B's own ~25% — the impostor keeps minting a structured self-contradiction because it is lying into a detector fed by sightings it never saw (the `report-model-ceiling-probe.md` mechanism), and a stronger model only grounds its alibi more faithfully in that poisoned memory. Capability buys cleaner JSON, not a clean alibi.

## Per-model substrate delta (flag-ON vs flag-OFF)

Does the corrected 13.5 substrate (richer testimony / witnessed-kill / movement / unfrozen memory) help THIS model decide where the 9B degraded? Reply corpus, cover OFF.

| model | mode | flag-OFF | flag-ON |
|---|---|---|---|
| qwen3-32b | non_thinking | parse 16/16 (100%) · deflect 10/16 (62%) · self-co-loc 4/16 (25%) · self-flag 9/16 (56%) | parse 16/16 (100%) · deflect 10/16 (62%) · self-co-loc 3/16 (19%) · self-flag 7/16 (44%) |
| qwen3-32b | thinking | parse 16/16 (100%) · deflect 12/16 (75%) · self-co-loc 5/16 (31%) · self-flag 6/16 (38%) | parse 16/16 (100%) · deflect 12/16 (75%) · self-co-loc 6/16 (38%) · self-flag 5/16 (31%) |
| qwen3-30b-a3b | non_thinking | parse 16/16 (100%) · deflect 12/16 (75%) · self-co-loc 6/16 (38%) · self-flag 6/16 (38%) | parse 16/16 (100%) · deflect 10/16 (62%) · self-co-loc 7/16 (44%) · self-flag 8/16 (50%) |
| qwen3-30b-a3b | thinking | parse 16/16 (100%) · deflect 12/16 (75%) · self-co-loc 6/16 (38%) · self-flag 5/16 (31%) | parse 16/16 (100%) · deflect 10/16 (62%) · self-co-loc 4/16 (25%) · self-flag 7/16 (44%) |
| glm-4-32b | non_thinking | parse 0/16 (0%) · deflect 0/0 (—) · self-co-loc 0/0 (—) · self-flag 0/0 (—) | parse 0/16 (0%) · deflect 0/0 (—) · self-co-loc 0/0 (—) · self-flag 0/0 (—) |
| cydonia-24b | non_thinking | parse 0/16 (0%) · deflect 0/0 (—) · self-co-loc 0/0 (—) · self-flag 0/0 (—) | parse 0/16 (0%) · deflect 0/0 (—) · self-co-loc 0/0 (—) · self-flag 0/0 (—) |

## Vote corpus — parse-success + conversion

Crew votes WITH a visible impostor (the conversion-relevant set; this 8-item slice is half recorded-SKIP inversion cases — a true impostor at suspicion 1.00 over the 0.60 gate where the 9B SKIPPED — and half recorded ejections). `conversion` = voter picked an available impostor. Every fit Featherless model converts 100% on BOTH substrates, i.e. it votes the suspect where the recorded 9B skipped — the single strongest 'a stronger model drives it' signal here, but an isolated-ballot proxy (not the live R-gate; see the hypothesis section).

| model | mode | substrate | parse-success | conversion |
|---|---|---|---|---|
| qwen3-32b | non_thinking | flag_off | 8/8 (100%) | 8/8 (100%) |
| qwen3-32b | thinking | flag_off | 8/8 (100%) | 8/8 (100%) |
| qwen3-30b-a3b | non_thinking | flag_off | 8/8 (100%) | 8/8 (100%) |
| qwen3-30b-a3b | thinking | flag_off | 8/8 (100%) | 8/8 (100%) |
| glm-4-32b | non_thinking | flag_off | 0/8 (0%) | 0/0 (—) |
| cydonia-24b | non_thinking | flag_off | 0/8 (0%) | 0/0 (—) |
| qwen3-32b | non_thinking | flag_on | 8/8 (100%) | 8/8 (100%) |
| qwen3-32b | thinking | flag_on | 8/8 (100%) | 8/8 (100%) |
| qwen3-30b-a3b | non_thinking | flag_on | 8/8 (100%) | 8/8 (100%) |
| qwen3-30b-a3b | thinking | flag_on | 8/8 (100%) | 8/8 (100%) |
| glm-4-32b | non_thinking | flag_on | 0/8 (0%) | 0/0 (—) |
| cydonia-24b | non_thinking | flag_on | 0/8 (0%) | 0/0 (—) |

## Recommended tuple + evidence

**Recommended (meeting_model, trigger_model, mode) = (`Qwen/Qwen3-32B`, `Qwen/Qwen3-32B`, `non_thinking` / `response_format_mode=json_object`).** Evidence: it clears the structured-output bar at 16/16 parse-success on the production prompts (~35.3s/turn isolated), posts the lowest self-co-location of the fit cells, and converts 100% on the hard vote cases — where the non-Qwen slate fails the structured-output bar entirely (see fidelity table). `non_thinking` is chosen because under `json_object` the request-time thinking toggle is effectively INERT (no reasoning channel surfaces; thinking_chars ≈ 0) yet it adds latency and output tokens for no behavior gain. For the trigger_model (latency-sensitive), `Qwen/Qwen3-30B-A3B-Instruct-2507` (MoE) is the speed option — same 16/16 parse and 100% isolated vote conversion at ~28.6s/turn vs ~35.3s for the 32B. GLM-4-32B-0414 and Cydonia-24B-v2 are flagged UNFIT through the pinned 14.1 adapter (its mandatory `chat_template_kwargs.enable_thinking` field collapses GLM to `{}` and 400/504s Cydonia — both DO emit valid JSON under a bare `json_object` request, so this is an adapter-compat finding to feed back to 14.1/14.6, not purely a model verdict). NOTE (integration risk): these isolated-turn metrics are PROXIES, not the live R-gate — a model can deflect/convert better in isolation yet still correctly SKIP in a noisy full game. The lock at 14.6 must read this as evidence, not verdict; the trigger_model defaults to the meeting_model id pending a dedicated trigger-corpus pass.

## Honest read of the information-ceiling hypothesis

**Supported, with one important counter-signal — and a methodological caveat.** The self-incrimination tell does NOT disappear as model strength rises above the 9B: the self-FLAG floor stays ≥ 31% on every fit model (vs the 9B's ~25%) and self-co-location persists at a non-trivial rate, neither dissolved by capability nor by the cover prompt. This is the `model_ceiling_probe.py:11-14` signature of an INFORMATION ceiling, not a model ceiling — the impostor reasons faithfully from a memory that says "you found the body here" into a detector fed by sightings it never saw. Caveat: only 3/16 of this sweep's hard reply contexts overlap the committed 9B run (the 9B file predates the current 9p2i recording), so the 9B column (self-co 69%, self-flag 25%) is a RATE-level reference, not an item-matched control; the load-bearing observation is the tell's PERSISTENCE across the Featherless slate on identical contexts, not the absolute level vs the 9B. The one place the stronger models clearly DIFFER from the 9B is the vote corpus: on the hard inversion cases (a true impostor visible at suspicion 1.00, over the 0.60 gate, where the recorded 9B SKIPPED) every fit Featherless model converts 100% — it votes the suspect. That is the sharpened Phase-14 question ('can the new model DRIVE the corrected substrate where the 9B couldn't?') answered YES *in isolation*. But this is an isolated single-ballot proxy, NOT the live R-gate: a calibrated model may still correctly SKIP inside a noisy full game. Only the 14.7 re-record + 14.8 R-gate can settle it. Net: a stronger model is necessary (it fixes the 9B's structured-output + the isolated skip pathology) but the meeting-deflection tell points at Phase-15 information levers (asymmetric visibility / vents / sabotage), not a further model upgrade.

**Harness/raw:** `experiments/lab/featherless_sweep.py` + `experiments/lab/results-featherless-sweep.jsonl` (per-cell mechanical grades + parse-success + tokens + latency + `substrate_flags`). 9B reference folded from the committed `results-model-ceiling-q9b.jsonl` (reply) and `results-deflection-probe.jsonl` (cover 2x2), both flag-OFF / local Ollama.
