# Lab report — Featherless model x thinking-mode sweep (Task 14.4)

**Decision informed:** which Featherless `(meeting_model, trigger_model, mode)` to lock at Task 14.6, and whether the Phase-13 information-ceiling hypothesis (`audits/audit-2026-06-25-0859-phase-13-close.md`) survives a stronger model. **Method:** the model-ceiling-vs-information design of `experiments/lab/report-model-ceiling-probe.md`, generalized across the Featherless slate over the SAME reconstructed `replays/samples/9p2i` opening/reply/vote contexts (item IDs pinned once and re-rendered under each substrate), on the PINNED 9B prompts, graded by the IDENTICAL mechanical detectors. **Cost:** $0 (Featherless flat-rate).

**9B-class reference (in-sweep, item-matched):** `qwen3.5:9b` is local Ollama (off the hosted endpoint), so the reference column is its closest served analogue **`Qwen/Qwen3-8B`** (same Qwen3 generation / nearest size / native `enable_thinking`), run over the SAME frozen contexts on BOTH substrates. The committed Ollama `results-model-ceiling-q9b.jsonl` (self-co 69%, self-flag 25%, deflect 62%) is folded only as a secondary HISTORICAL row — it predates the current 9p2i recording (non-item-matched).

**Non-Qwen transport:** GLM-4-32B-0414 and Cydonia-24B-v2 are routed through a sweep-local BARE send that OMITS the 14.1 adapter's mandatory `chat_template_kwargs.enable_thinking` field (the Qwen3 convention that otherwise collapses GLM to `{}` and 400/504s Cydonia) — so their rows reflect real model structured-output fidelity, not a harness artifact. The proper conditional-field fix belongs in `llm/featherless_client.py` (out of scope for 14.4; flagged to 14.1/14.6).

Slate substitution (live, 2026-06-29): the contract's `Qwen/Qwen3-30B-A3B` and `zai-org/GLM-4-32B` ids 404; Featherless serves the canonical revisions `Qwen/Qwen3-30B-A3B-Instruct-2507` and `zai-org/GLM-4-32B-0414`.

**Best-shot call profiles (owner decision 2026-06-29):** the probe's job is to rank how each model performs on the corpus, so each model/mode is called with the settings MOST LIKELY TO SUCCEED — not the 9B-era `json_object` / 2048-token handicap. THINKING rows use `response_format=none` (json_object SUPPRESSES Qwen3 reasoning — calibrated: out=243 vs 3187 tokens) + a 16384-token budget so reasoning actually happens and never truncates, with the `<think>` block stripped before extract→validate. NON-THINKING rows use `json_object` + a 4096 budget. The OUTPUT is the schema-identical `MeetingTurn`/`VoteBallot` either way (downstream graders unchanged), and reasoning is DISCARDED (never recorded), so it cannot leak into game state. Per-row `profile` (mode + max_tokens) is stamped in the jsonl. The deployed sim still caps turns at 2048 / votes at 1024; choosing thinking for the recorded baseline is a 14.6/14.7 decision (raise the generation budget, cap the recorded answer, strip reasoning) — see the latency note in the recommendation.

## Structured-output fidelity (parse-success, best-shot profile)

Reply corpus, cover OFF, flag-OFF substrate.

| model | mode | profile | parse-success | latency (isolated) | reasoning | fit? |
|---|---|---|---|---|---|---|
| qwen3-8b (ref) | non_thinking | json_object/4096 | 16/16 (100%) | ~24.0s | — | yes |
| qwen3-8b (ref) | thinking | none/16384 | 15/16 (94%) | ~168.0s | ~17228 ch | yes |
| qwen3-32b | non_thinking | json_object/4096 | 16/16 (100%) | ~27.1s | — | yes |
| qwen3-32b | thinking | none/16384 | 16/16 (100%) | ~226.1s | ~11411 ch | yes |
| qwen3-30b-a3b | non_thinking | json_object/4096 | 16/16 (100%) | ~18.0s | — | yes |
| qwen3-30b-a3b | thinking | none/16384 | 16/16 (100%) | ~20.8s | — | yes |
| glm-4-32b | non_thinking | json_object/4096 | 15/16 (94%) | ~24.8s | — | yes |
| cydonia-24b | non_thinking | json_object/4096 | 16/16 (100%) | ~35.0s | — | yes |

## Model-ceiling-vs-information read (cover OFF, flag-OFF)

`qwen3-8b` is the item-matched 9B-class reference. Read the candidate rows against it on identical contexts.

| model | mode | deflect | self-co-loc (the *tell*) | self-flag |
|---|---|---|---|---|
| qwen3-8b (ref) | non_thinking | 10/16 (62%) | 7/16 (44%) | 3/16 (19%) |
| qwen3-8b (ref) | thinking | 11/15 (73%) | 4/15 (27%) | 3/15 (20%) |
| qwen3-32b | non_thinking | 12/16 (75%) | 3/16 (19%) | 7/16 (44%) |
| qwen3-32b | thinking | 15/16 (94%) | 3/16 (19%) | 3/16 (19%) |
| qwen3-30b-a3b | non_thinking | 13/16 (81%) | 6/16 (38%) | 6/16 (38%) |
| qwen3-30b-a3b | thinking | 10/16 (62%) | 5/16 (31%) | 5/16 (31%) |
| glm-4-32b | non_thinking | 12/15 (80%) | 5/15 (33%) | 11/15 (73%) |
| cydonia-24b | non_thinking | 14/16 (88%) | 7/16 (44%) | 3/16 (19%) |
| qwen3.5:9b (Ollama, historical) | non_thinking | 10/16 (62%) | 11/16 (69%) | 4/16 (25%) |

## Cover-directive 2x2 (model x {cover OFF, cover ON-reply})

Self-co-location (the tell) with the cover directive OFF vs ON, flag-OFF:

| model | mode | cover OFF self-co-loc | cover ON self-co-loc | Δ |
|---|---|---|---|---|
| qwen3-8b | non_thinking | 7/16 (44%) | 6/15 (40%) | -4 pp |
| qwen3-8b | thinking | 4/15 (27%) | 5/14 (36%) | +9 pp |
| qwen3-32b | non_thinking | 3/16 (19%) | 1/16 (6%) | -12 pp |
| qwen3-32b | thinking | 3/16 (19%) | 1/16 (6%) | -12 pp |
| qwen3-30b-a3b | non_thinking | 6/16 (38%) | 6/16 (38%) | +0 pp |
| qwen3-30b-a3b | thinking | 5/16 (31%) | 5/16 (31%) | +0 pp |
| glm-4-32b | non_thinking | 5/15 (33%) | 4/12 (33%) | +0 pp |
| cydonia-24b | non_thinking | 7/16 (44%) | 7/16 (44%) | +0 pp |

**Quadrant verdict — BOTH, leaning INFORMATION CEILING.** The cover directive's effect on self-co-location is SMALL and INCONSISTENT across the fit cells (mean Δ +2 pp; helps ≥10 pp in only 2 of 8 comparable cells, back-fires in others) — far weaker than its effect on the 9B's own contexts (cover cut self-co 55%→21% in `results-deflection-probe.jsonl`). So there IS a prompt-artifact component (the v5 directive never reaches the reply path today, audit gp-1) worth wiring in at 14.5, but it does NOT reliably dissolve the tell. The decisive ceiling signal is the self-FLAG floor: it never falls below 19% on any fit model — the impostor keeps minting a structured self-contradiction because it is lying into a detector fed by sightings it never saw (`report-model-ceiling-probe.md`). Capability buys cleaner JSON, not a clean alibi.

## Per-model substrate delta (flag-ON vs flag-OFF)

Does the corrected 13.5 substrate help THIS model decide where the 9B degraded? Reply corpus, cover OFF, SAME pinned contexts re-rendered.

| model | mode | flag-OFF | flag-ON |
|---|---|---|---|
| qwen3-8b | non_thinking | parse 16/16 (100%) · deflect 10/16 (62%) · self-co-loc 7/16 (44%) · self-flag 3/16 (19%) | parse 16/16 (100%) · deflect 10/16 (62%) · self-co-loc 6/16 (38%) · self-flag 3/16 (19%) |
| qwen3-8b | thinking | parse 15/16 (94%) · deflect 11/15 (73%) · self-co-loc 4/15 (27%) · self-flag 3/15 (20%) | parse 14/16 (88%) · deflect 13/14 (93%) · self-co-loc 5/14 (36%) · self-flag 2/14 (14%) |
| qwen3-32b | non_thinking | parse 16/16 (100%) · deflect 12/16 (75%) · self-co-loc 3/16 (19%) · self-flag 7/16 (44%) | parse 16/16 (100%) · deflect 10/16 (62%) · self-co-loc 4/16 (25%) · self-flag 6/16 (38%) |
| qwen3-32b | thinking | parse 16/16 (100%) · deflect 15/16 (94%) · self-co-loc 3/16 (19%) · self-flag 3/16 (19%) | parse 16/16 (100%) · deflect 16/16 (100%) · self-co-loc 3/16 (19%) · self-flag 3/16 (19%) |
| qwen3-30b-a3b | non_thinking | parse 16/16 (100%) · deflect 13/16 (81%) · self-co-loc 6/16 (38%) · self-flag 6/16 (38%) | parse 16/16 (100%) · deflect 10/16 (62%) · self-co-loc 5/16 (31%) · self-flag 9/16 (56%) |
| qwen3-30b-a3b | thinking | parse 16/16 (100%) · deflect 10/16 (62%) · self-co-loc 5/16 (31%) · self-flag 5/16 (31%) | parse 16/16 (100%) · deflect 12/16 (75%) · self-co-loc 7/16 (44%) · self-flag 9/16 (56%) |
| glm-4-32b | non_thinking | parse 15/16 (94%) · deflect 12/15 (80%) · self-co-loc 5/15 (33%) · self-flag 11/15 (73%) | parse 9/16 (56%) · deflect 7/9 (78%) · self-co-loc 5/9 (56%) · self-flag 2/9 (22%) |
| cydonia-24b | non_thinking | parse 16/16 (100%) · deflect 14/16 (88%) · self-co-loc 7/16 (44%) · self-flag 3/16 (19%) | parse 16/16 (100%) · deflect 15/16 (94%) · self-co-loc 7/16 (44%) · self-flag 4/16 (25%) |

## Opening corpus — impostor self-report (parse + self-incrimination)

Killer opens the meeting for their own kill. `self-co-loc` = the opener placed itself at the true kill room (the opening tell); `confess` = self-incriminating free text. Tabulated per substrate.

| model | mode | substrate | parse-success | self-co-loc | confess |
|---|---|---|---|---|---|
| qwen3-8b (ref) | non_thinking | flag_off | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |
| qwen3-8b (ref) | thinking | flag_off | 6/10 (60%) | 0/6 (0%) | 0/6 (0%) |
| qwen3-32b | non_thinking | flag_off | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |
| qwen3-32b | thinking | flag_off | 9/10 (90%) | 0/9 (0%) | 0/9 (0%) |
| qwen3-30b-a3b | non_thinking | flag_off | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |
| qwen3-30b-a3b | thinking | flag_off | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |
| glm-4-32b | non_thinking | flag_off | 9/10 (90%) | 0/9 (0%) | 0/9 (0%) |
| cydonia-24b | non_thinking | flag_off | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |
| qwen3-8b (ref) | non_thinking | flag_on | 10/10 (100%) | 1/10 (10%) | 0/10 (0%) |
| qwen3-8b (ref) | thinking | flag_on | 3/10 (30%) | 0/3 (0%) | 0/3 (0%) |
| qwen3-32b | non_thinking | flag_on | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |
| qwen3-32b | thinking | flag_on | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |
| qwen3-30b-a3b | non_thinking | flag_on | 10/10 (100%) | 1/10 (10%) | 0/10 (0%) |
| qwen3-30b-a3b | thinking | flag_on | 10/10 (100%) | 1/10 (10%) | 0/10 (0%) |
| glm-4-32b | non_thinking | flag_on | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |
| cydonia-24b | non_thinking | flag_on | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |

## Vote corpus — parse-success + conversion

Crew votes WITH a visible impostor; half are recorded-SKIP inversion cases (a true impostor at suspicion 1.00 over the 0.60 gate where the 9B SKIPPED). `conversion` = voter picked an available impostor. Same pinned vote ids re-rendered under each substrate.

| model | mode | substrate | parse-success | conversion |
|---|---|---|---|---|
| qwen3-8b | non_thinking | flag_off | 8/8 (100%) | 8/8 (100%) |
| qwen3-8b | thinking | flag_off | 8/8 (100%) | 8/8 (100%) |
| qwen3-32b | non_thinking | flag_off | 8/8 (100%) | 8/8 (100%) |
| qwen3-32b | thinking | flag_off | 8/8 (100%) | 8/8 (100%) |
| qwen3-30b-a3b | non_thinking | flag_off | 8/8 (100%) | 8/8 (100%) |
| qwen3-30b-a3b | thinking | flag_off | 8/8 (100%) | 8/8 (100%) |
| glm-4-32b | non_thinking | flag_off | 8/8 (100%) | 8/8 (100%) |
| cydonia-24b | non_thinking | flag_off | 8/8 (100%) | 8/8 (100%) |
| qwen3-8b | non_thinking | flag_on | 8/8 (100%) | 8/8 (100%) |
| qwen3-8b | thinking | flag_on | 8/8 (100%) | 8/8 (100%) |
| qwen3-32b | non_thinking | flag_on | 8/8 (100%) | 8/8 (100%) |
| qwen3-32b | thinking | flag_on | 8/8 (100%) | 8/8 (100%) |
| qwen3-30b-a3b | non_thinking | flag_on | 8/8 (100%) | 8/8 (100%) |
| qwen3-30b-a3b | thinking | flag_on | 8/8 (100%) | 8/8 (100%) |
| glm-4-32b | non_thinking | flag_on | 8/8 (100%) | 8/8 (100%) |
| cydonia-24b | non_thinking | flag_on | 8/8 (100%) | 8/8 (100%) |

## Recommended tuple + evidence

**Recommended (meeting_model, trigger_model, mode) = (`Qwen/Qwen3-32B`, `Qwen/Qwen3-32B`, `non_thinking`).** Evidence: it clears the structured-output bar at 16/16 (100%) parse-success (~27.1s/turn isolated), posts a low self-co-location, and converts on the hard vote cases. For the trigger_model (latency-sensitive), `Qwen/Qwen3-30B-A3B-Instruct-2507` (MoE) is the speed option at ~18.0s/turn vs ~27.1s for the 32B. **Mode is a genuine tradeoff now** (the fair best-shot test — thinking really reasons, ~16k tokens): on this model thinking MEASURABLY IMPROVES behavior (deflect +19 pp, self-flag -25 pp, self-co +0 pp) at a real latency cost (~226.1s vs ~27.1s/turn). Mode is therefore a 14.6 quality-vs-latency call — `non_thinking` is the latency-cheap default, `thinking` the higher-quality option; it is no longer the degenerate axis it was under the 2048/json_object handicap. Via the bare send (omitting the Qwen-only chat kwarg), Cydonia-24B-v2 clears the 90% bar (100%); GLM-4-32B-0414 clears the 90% bar (94%) — so the 0% in the prior version was an adapter artifact, now corrected. They remain non-default (a marginal/lower-deflection profile behind the recommended Qwen3-32B), not disqualified on a parse artifact. NOTE (integration risk): these isolated-turn metrics are PROXIES, not the live R-gate — a model can deflect/convert better in isolation yet still correctly SKIP in a noisy full game. The lock at 14.6 must read this as evidence, not verdict; the trigger_model defaults to the meeting_model id pending a dedicated trigger-corpus pass.

## Honest read of the information-ceiling hypothesis

**Supported — and now controlled on identical contexts.** With the 9B-class `qwen3-8b` reference run over the SAME frozen contexts as the stronger candidates, the self-incrimination tell does NOT fall as model strength rises: the self-FLAG floor stays ≥ 19% across every fit model (reference self-flag 19%, self-co 44%) and the cover prompt does not reliably remove it. This is the `model_ceiling_probe.py:11-14` signature of an INFORMATION ceiling, not a model ceiling — the impostor reasons faithfully from a memory that says "you found the body here" into a detector fed by sightings it never saw. The one place the stronger models clearly DIFFER from the 9B is the vote corpus: on the hard inversion cases (a true impostor at suspicion 1.00 over the 0.60 gate where the recorded 9B SKIPPED) the fit Featherless models convert — the sharpened Phase-14 question ('can the new model DRIVE the corrected substrate where the 9B couldn't?') answered YES *in isolation*. But that is an isolated single-ballot proxy, NOT the live R-gate: only the 14.7 re-record + 14.8 R-gate can settle it. Net: a stronger model is necessary (it fixes the 9B's structured output + the isolated skip pathology) but the meeting-deflection tell points at Phase-15 information levers (asymmetric visibility / vents / sabotage), not a further model upgrade.

**Harness/raw:** `experiments/lab/featherless_sweep.py` + `experiments/lab/results-featherless-sweep.jsonl` (per-cell grades + parse-success + tokens + latency + `transport` + `substrate_flags`; the matrix actually run is logged at run time — no silent truncation). The 9B-class reference is the in-sweep `Qwen/Qwen3-8B`; the committed Ollama `results-model-ceiling-q9b.jsonl` is a secondary historical row.
