# Lab report — Featherless new-generation probe: qwen3.6-27b vs the incumbent (Task 16.1)

**Decision informed:** the Phase-16 model lock (Task 16.2, `audits/audit-phase-16-model-lock.md`) — whether the newer Qwen generation should displace the incumbent `Qwen/Qwen3-32B` before any production change. **Method:** the SAME reconstructed `replays/samples/9p2i` contexts as the 14.4 sweep (opening/reply/vote item ids pinned once and re-rendered per cell), the IDENTICAL mechanical detectors, and the prompt held CONSTANT at the EXISTING `qwen3_32b` set on BOTH thinking modes — running the incumbent's set on the candidate is itself a finding (the bespoke 3.6 set is Task 16.13's). **Cost:** $0 (Featherless flat-rate).

**Owner redirect (2026-07-11):** the 16.1 contract text names `qwen3.5-27b`; the owner redirected the probe mid-task to **Qwen3.6-27B** plus a second candidate **bottlecapai/ThinkingCap-Qwen3.6-27B**. The artifact names (`results-`/`report-featherless-sweep-qwen3-6-27b`) follow the ACTUAL slate. Every finding below is DISCOVERED from the committed probe rows — the generation preflight, not a hardcoded conclusion, is the arbiter.

## Served-id findings (the generation preflight is the arbiter)

| label | id form tried | pinned? | served | attempts | evidence |
|---|---|---|---|---|---|
| qwen3-6-27b | `Qwen/Qwen3.6-27B` | yes | yes | 1 | ok |
| qwen3-6-27b | `Qwen/Qwen3.6-27B-Instruct` | no | no | 1 | HTTP 404 {"error":{"message":"The model `Qwen/Qwen3.6-27B-Instruct` does not exist.","type":"invalid_request_error","param":null,"code":"model_not_found"}} |
| thinkingcap-27b | `bottlecapai/ThinkingCap-Qwen3.6-27B` | yes | no | 2 | HTTP 400 {"error":{"message":"The model `bottlecapai/ThinkingCap-Qwen3.6-27B` is not available for inference.","type":"invalid_request_error","param":null,"code |
| qwen3-32b | `Qwen/Qwen3-32B` | yes | yes | 1 | ok |

**NO-GO — thinkingcap-27b** (`bottlecapai/ThinkingCap-Qwen3.6-27B`, forms tried ['bottlecapai/ThinkingCap-Qwen3.6-27B']): HTTP 400 {"error":{"message":"The model `bottlecapai/ThinkingCap-Qwen3.6-27B` is not available for inference.","type":"invalid_request_error","param":null,"code

A NO-GO is a FIRST-CLASS recorded outcome for the 16.2 lock, not a task failure: the probe records the deterministic evidence and excludes the model from the later passes rather than crashing.

## response_format verdict (json_object AND json_schema, both probed)

| model | rf_mode | schema | attempts accepted | content-was-JSON | verdict |
|---|---|---|---|---|---|
| qwen3-32b | json_object | MeetingTurn | 2/2 | yes | supported |
| qwen3-32b | json_object | VoteBallot | 2/2 | yes | supported |
| qwen3-32b | json_schema | MeetingTurn | 0/2 | — | rejected (deterministic HTTP 422 across attempts + busy-body retries; a busy-TYPED 4xx counts as rejection here because the same-pass json_object control succeeded — a genuinely busy deployment fails both shapes; 1 transient failure(s) recorded beside it) |
| qwen3-32b | json_schema | VoteBallot | 0/2 | — | rejected (deterministic HTTP 422 across attempts + busy-body retries; a busy-TYPED 4xx counts as rejection here because the same-pass json_object control succeeded — a genuinely busy deployment fails both shapes) |
| qwen3-6-27b | json_object | MeetingTurn | 2/2 | yes | supported |
| qwen3-6-27b | json_object | VoteBallot | 2/2 | yes | supported |
| qwen3-6-27b | json_schema | MeetingTurn | 0/2 | — | rejected (deterministic HTTP 400 across attempts + busy-body retries; a busy-TYPED 4xx counts as rejection here because the same-pass json_object control succeeded — a genuinely busy deployment fails both shapes) |
| qwen3-6-27b | json_schema | VoteBallot | 0/2 | — | rejected (deterministic HTTP 400 across attempts + busy-body retries; a busy-TYPED 4xx counts as rejection here because the same-pass json_object control succeeded — a genuinely busy deployment fails both shapes) |

Production posture (`llm/featherless_client.py` docstring, recorded 2026-06-27): the incumbent rejects strict `json_schema` deterministically (a 400 at the time) and runs on `json_object`. Re-verified here same-day — the incumbent's `json_schema` verdict above is **rejected for every schema probed** (each verdict cell is per-schema and quotes the HTTP status actually observed, which may drift from the documented code); read each candidate's row beside it.

## Thinking-kwarg behavior (the evidence a 16.12 registry entry will encode)

| model | kwarg | accepted | reasoning channel | channel chars | out_tokens | content head |
|---|---|---|---|---|---|---|
| qwen3-32b | absent | yes | inline_think_close | 839 | 338 | 391 |
| qwen3-32b | false | yes | — | 0 | 3 | 391 |
| qwen3-32b | true | yes | inline_think_close | 839 | 338 | 391 |
| qwen3-6-27b | absent | yes | inline_think_close | 603 | 263 | 391 |
| qwen3-6-27b | false | yes | — | 0 | 3 | 391 |
| qwen3-6-27b | true | yes | inline_think_close | 699 | 287 | 391 |

**qwen3-32b:** kwarg absent ⇒ REASONS by default; `enable_thinking=false` SUPPRESSES reasoning; reasoning channel(s): `inline_think_close`. Reasoning is INLINE in `content`, closed by a bare `</think>` with no side-channel; the production adapter's `strip` policy excises it for this registered id (and production always pins `enable_thinking` explicitly, so the bare-request default never reaches game state).

**qwen3-6-27b:** kwarg absent ⇒ REASONS by default; `enable_thinking=false` SUPPRESSES reasoning; reasoning channel(s): `inline_think_close`. Reasoning is INLINE in `content`, closed by a bare `</think>` with no side-channel — `_raw_from_response_body` reads only `reasoning_content`, so the sweep-local transport carries the split (the production mapping is 16.12's).

## Structured-output fidelity (parse-success per call kind, best-shot profile)

Reply / opening / vote parse-success per served model and mode, on the held-constant `qwen3_32b` prompt set, flag-on substrate. `fit?` uses the 14.4 bar: >=90% yes, >=50% marginal, else NO (reply parse).

| model | mode | profile | reply parse | opening parse | vote parse | isolated latency | reasoning | fit? |
|---|---|---|---|---|---|---|---|---|
| qwen3-32b | non_thinking | json_object/4096 | 16/16 (100%) | 10/10 (100%) | 8/8 (100%) | ~32.3s | — | yes |
| qwen3-32b | thinking | none/16384 | 16/16 (100%) | 10/10 (100%) | 8/8 (100%) | ~166.2s | ~6981 ch | yes |
| qwen3-6-27b | non_thinking | json_object/4096 | 16/16 (100%) | 10/10 (100%) | 8/8 (100%) | ~43.1s | — | yes |
| qwen3-6-27b | thinking | none/16384 | 16/16 (100%) | 10/10 (100%) | 8/8 (100%) | ~315.0s | ~17007 ch | yes |

## Opening corpus — impostor self-report

Killer opens the meeting for their own kill. `self-co-loc` = the opener placed itself at the true kill room (the opening tell); `confess` = self-incriminating free text. flag-on substrate.

| model | mode | parse-success | self-co-loc | confess |
|---|---|---|---|---|
| qwen3-32b | non_thinking | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |
| qwen3-32b | thinking | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |
| qwen3-6-27b | non_thinking | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |
| qwen3-6-27b | thinking | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |

## Reply corpus — cover 2×2

Cover OFF metrics (parse / deflect / self-co-location — the impostor tell — / self-flag), then the cover OFF->ON self-co-location delta. flag-on substrate, held-constant `qwen3_32b` set.

| model | mode | parse | deflect | self-co-loc | self-flag |
|---|---|---|---|---|---|
| qwen3-32b | non_thinking | 16/16 (100%) | 14/16 (88%) | 6/16 (38%) | 4/16 (25%) |
| qwen3-32b | thinking | 16/16 (100%) | 15/16 (94%) | 4/16 (25%) | 6/16 (38%) |
| qwen3-6-27b | non_thinking | 16/16 (100%) | 16/16 (100%) | 8/16 (50%) | 8/16 (50%) |
| qwen3-6-27b | thinking | 16/16 (100%) | 16/16 (100%) | 7/16 (44%) | 5/16 (31%) |

Cover OFF vs ON — self-co-location (the tell):

| model | mode | cover OFF self-co-loc | cover ON self-co-loc | Δ |
|---|---|---|---|---|
| qwen3-32b | non_thinking | 6/16 (38%) | 6/16 (38%) | +0 pp |
| qwen3-32b | thinking | 4/16 (25%) | 4/16 (25%) | +0 pp |
| qwen3-6-27b | non_thinking | 8/16 (50%) | 4/16 (25%) | -25 pp |
| qwen3-6-27b | thinking | 7/16 (44%) | 4/16 (25%) | -19 pp |

## Vote corpus — parse + conversion

`conversion` = voter picked an available impostor. flag-on substrate.

| model | mode | parse-success | conversion |
|---|---|---|---|
| qwen3-32b | non_thinking | 8/8 (100%) | 7/8 (88%) |
| qwen3-32b | thinking | 8/8 (100%) | 7/8 (88%) |
| qwen3-6-27b | non_thinking | 8/8 (100%) | 8/8 (100%) |
| qwen3-6-27b | thinking | 8/8 (100%) | 8/8 (100%) |

## Latency

Isolated single-turn latency (sequential micro-pass), flag-on substrate only. Candidate rows sit beside the same-day incumbent rows.

| model | mode | isolated latency |
|---|---|---|
| qwen3-32b | non_thinking | ~32.3s |
| qwen3-32b | thinking | ~166.2s |
| qwen3-6-27b | non_thinking | ~43.1s |
| qwen3-6-27b | thinking | ~315.0s |

## Recommendation (ranked, not self-declared — 16.2 decides)

Ranked by: parse fitness (desc), then reply self-co-location (asc — lower is a cleaner alibi), then vote conversion (desc), then isolated latency (asc).

| rank | model | mode | reply parse | self-co-loc | vote conversion | latency |
|---|---|---|---|---|---|---|
| 1 | qwen3-32b | thinking | 16/16 (100%) | 4/16 (25%) | 7/8 (88%) | ~166.2s |
| 2 | qwen3-32b | non_thinking | 16/16 (100%) | 6/16 (38%) | 7/8 (88%) | ~32.3s |
| 3 | qwen3-6-27b | thinking | 16/16 (100%) | 7/16 (44%) | 8/8 (100%) | ~315.0s |
| 4 | qwen3-6-27b | non_thinking | 16/16 (100%) | 8/16 (50%) | 8/8 (100%) | ~43.1s |

Served candidate id(s): `Qwen/Qwen3.6-27B` (qwen3-6-27b).

**Open risks:**

- The prompt set is the INCUMBENT's (`qwen3_32b`), held constant across both models and modes; the bespoke 3.6 set is Task 16.13's, so candidate numbers may UNDERSTATE a model authored against its own templates.
- The isolated-turn parse / self-co-location / conversion metrics are PROXIES, not the live R-gate — a model can look better in isolation yet behave differently in a full noisy game.
- The new generation's thinking DEFAULT posture (it reasons unless `enable_thinking` is pinned false) means a production integration must PIN `enable_thinking` explicitly (or strip the inline `</think>` reasoning), or reasoning leaks into recorded state.
- The production registry entry does NOT exist yet (Task 16.12, post-lock): the probe carries the Qwen kwarg + the inline reasoning split sweep-locally; the fail-loud `_THINKING_KWARG_BY_MODEL` classification is 16.12's.
- ThinkingCap-Qwen3.6-27B is a documented NO-GO (its deployment 400s on the chat template / every generation — see the served-id evidence), a first-class outcome for 16.2, not a probe failure.

This report recommends; the 16.2 lock decides.

## Reproduce

```
# facts (offline, $0):
PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py
# probe run (needs FEATHERLESS_API_KEY; hours-scale, $0 flat-rate):
uv run python -m experiments.lab.featherless_sweep probe \
    --sample-dir replays/samples/9p2i \
    --facts $TMPDIR/ailibi-gameplay-facts-9p2i.json
# regenerate THIS report from the committed rows:
uv run python -m experiments.lab.featherless_sweep probe-report
```

**Harness/raw:** `experiments/lab/featherless_sweep.py` + `experiments/lab/results-featherless-sweep-qwen3-6-27b.jsonl` (served-id + response_format + thinking-kwarg discovery rows and the graded matrix cells; every number in this report regenerates from those rows).


## Two-pass bespoke-set A/B (Task 16.13): `qwen3_6_27b`

One set, one model, one mode (the `_SET_OWNER` binding — a cross-set control is structurally rejected), the SAME pinned contexts and detectors; the arms differ ONLY by the committed template bytes, told apart per row by `template_source_sha`. Pass 1 = the scratch-v5-verbatim commit (the known-clean, mechanics-incomplete control); pass 2 = the mechanics-complete commit (the candidate baseline 4 records with). The open question measured: HOW MUCH of the scratch profile survives the mechanics merge.

### Reply corpus — parse / deflect / tell / self-flag, per cover arm

| arm | template sha | cover | parse | deflect | self-co-loc (tell) | self-flag |
|---|---|---|---|---|---|---|
| control (scratch-v5-verbatim) | `df731018e0a6` | off | 16/16 (100%) | 16/16 (100%) | 0/16 (0%) | 0/16 (0%) |
| control (scratch-v5-verbatim) | `df731018e0a6` | on | 16/16 (100%) | 15/16 (94%) | 0/16 (0%) | 0/16 (0%) |
| candidate (mechanics-complete) | `ba0b6a015cf3` | off | 16/16 (100%) | 14/16 (88%) | 0/16 (0%) | 0/16 (0%) |
| candidate (mechanics-complete) | `ba0b6a015cf3` | on | 16/16 (100%) | 15/16 (94%) | 0/16 (0%) | 0/16 (0%) |

### Vote corpus — parse + conversion

| arm | template sha | parse | conversion |
|---|---|---|---|
| control (scratch-v5-verbatim) | `df731018e0a6` | 8/8 (100%) | 8/8 (100%) |
| candidate (mechanics-complete) | `ba0b6a015cf3` | 8/8 (100%) | 8/8 (100%) |

### Opening corpus — impostor self-report

| arm | template sha | parse | self-co-loc (tell) | confess |
|---|---|---|---|---|
| control (scratch-v5-verbatim) | `df731018e0a6` | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |
| candidate (mechanics-complete) | `ba0b6a015cf3` | 10/10 (100%) | 0/10 (0%) | 0/10 (0%) |

### Latency

| arm | isolated latency (s) | mean reply latency (s) |
|---|---|---|
| control (scratch-v5-verbatim) | 16.7 | 22.2 |
| candidate (mechanics-complete) | 32.0 | 18.7 |

**Verdict (computed from the rows): no clean cell regressed — the scratch profile SURVIVES the mechanics merge, and the restyled mechanics-complete templates are adopted as the set's v1 (the bytes baseline 4 records with).**

Reproduce (each pass from ITS template commit; rows are the evidence):

```
PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py
uv run python -m experiments.lab.featherless_sweep ab \
    --prompt-set qwen3_6_27b --facts $TMPDIR/ailibi-gameplay-facts-9p2i.json
# ... commit the mechanics-complete templates, then:
uv run python -m experiments.lab.featherless_sweep ab \
    --prompt-set qwen3_6_27b --facts $TMPDIR/ailibi-gameplay-facts-9p2i.json \
    --append
```