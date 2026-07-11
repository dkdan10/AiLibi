# From-scratch qwen3.6-27b prompt set — the v0→v5 evidence ladder (owner-directed, 2026-07-11)

Input evidence for Task 16.13 (the bespoke set, post-lock). Owner directive:
author an optimized prompt for `Qwen/Qwen3.6-27B` FROM SCRATCH (no reuse of
other models' prompt prose), non-thinking only (thinking latency is not viable
in real runs), starting minimal and building up only where a measured run
fails. Each version directory differs from its predecessor by ONE rule
targeting the previous version's observed failure; every number below
regenerates from the committed `results-v*.jsonl` beside this file.

Method: rendered through the loader's own render functions over these template
directories (`run_iteration.py` — no production prompt-surface registration),
run over the SAME pinned `replays/samples/9p2i` contexts and graded by the
IDENTICAL mechanical detectors as the Task 16.1 probe
(`results-featherless-sweep-qwen3-6-27b.jsonl` is the baseline being compared
against; temp 0.4, `json_object`, 4096 cap — the best-shot non-thinking
profile). Reply corpus n=16 per cover arm; votes n=8; openings n=10.

Design inputs (see PR #254 discussion): the detector mechanics
(`self_co_locates_body` = a structured self-alibi in the body room OR
"found"+"body" co-occurring in free text), the failure anatomy of the 16.1
probe rows, and web research on Qwen3.6 prompting (tag sectioning, positive
framing over bare negative constraints, instructions at both ends, hard length
caps, never a literal think-close tag in template text).

## The ladder

| version | one change | reply self-co off/on | deflect | self-flag | vote conv | notes |
|---|---|---|---|---|---|---|
| v0 | minimal: tag-sectioned, 1-2 sentence cap, accusation-ONLY claims (no self-alibi structurally) | 56% / 31% | 100% | **0%** | — | structural tell + self-flag eliminated at v0; all residual tell is the lexical "found the body" detector |
| v1 | phrasing rule: say "reported it / called the meeting", never discovery talk | 6% / 0% | 100% | 0% | — | one passive-voice slip ("where the body was found") |
| v2 | extend rule to passive forms ("where it happened"; no "found"/"discovered") | **0% / 0%** | 94-100% | 0% | 6/8 | tell fully gone; vote regression surfaced by --full |
| v3 | vote: graph-primacy rule (own suspicion levels over meeting rhetoric) | — | — | — | 7/8 | remaining miss: flag-direction misread |
| v4 | vote: flags are verified + directional; mirror-accusations carry no weight | — | — | — | 7/8 | remaining miss is PRINCIPLED: voter's own sightings exculpate the impostor (vent blind spot) |
| v5 | vote: the vent MECHANIC (invisible travel; sightings of someone elsewhere do not clear a witnessed vent) | **0% / 0%** | **100%** | **0%** | **8/8** | final full-corpus validation below |

## v5 final validation (fresh full-corpus run, `results-v5.jsonl`)

- reply: parse 32/32, self-co-location **0/32** (both cover arms), deflect
  **32/32**, self-flag **0/32**, mean latency ~20.5s
- vote: parse 8/8, conversion **8/8**
- opening: parse 10/10, tell 0/10, confess 0/10

Baselines on the same contexts, same model, non-thinking (from the 16.1 probe
and the prompt-set sensitivity experiment,
`results-featherless-sweep-qwen3-6-27b*.jsonl`): the `qwen3_32b` set posts 50%
reply tell / 50% self-flag / 8/8 conversion; the best existing alternate
(`glm_4_32b`) 31% / 44% / 8/8; the incumbent's best-any-mode tell is 25%
(thinking, ~166s/turn).

## What made the difference (for 16.13)

1. **Structural beats prohibitive**: the output contract allows exactly ONE
   accusation claim and an empty observations list — with no self-alibi claim
   available, the structured tell AND the minted self-contradiction flag
   (self-flag ≥44% on every prior set) go to zero by construction.
2. **The residual tell was lexical**: the committed detector fires on
   "found"+"body" regardless of who found it, and qwen3.6's natural deflection
   ("p-X found the body and instantly accused me") trips it. One
   positively-paired phrasing rule ("say reported it / called the meeting…")
   removed 8/9 hits; covering the passive form removed the last.
3. **Vote misses were comprehension, not preference**: graph-primacy,
   flag-directionality, and the vent mechanic each converted a distinct
   observed miss. The vent-mechanic line matters most: without it a voter's
   own honest sightings ("I saw them leave that room earlier") exculpate the
   impostor.
4. **Compact prompts help**: ~7.9k chars vs the 12.8k `qwen3_32b` render;
   non-thinking replies land in ~20s vs ~26-43s.

## Open caveats

- n=16/8/10 per corpus; single-day, single-seed-set. The 0% cells are strong
  signals, not guarantees.
- The lexical-phrasing rule aligns the model with the committed detector; a
  future detector revision (e.g. speaker-attributed discovery parsing) should
  re-baseline this set.
- These are ISOLATED-turn proxies, not the live R-gate; the 14.x caution
  applies unchanged.
- Productization (versioned set under `agents/strategic/prompts/`,
  `_SET_OWNER` registration, loader discovery, per-template version headers)
  is Task 16.13's, post-lock; these files are its input evidence.

## Reproduce

```
# facts (offline, $0):
PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py
# final validation run of v5 (needs FEATHERLESS_API_KEY; ~25 min, $0 flat-rate):
PYTHONPATH=. uv run python experiments/lab/qwen36_prompt_scratch/run_iteration.py v5 \
    --full --facts $TMPDIR/ailibi-gameplay-facts-9p2i.json
```
