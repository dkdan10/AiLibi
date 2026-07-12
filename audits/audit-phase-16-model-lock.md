# Phase-16 model lock — GO: `Qwen/Qwen3.6-27B`, pinned non-thinking, on the two-evidence-set reading (Task 16.2)

**Date:** 2026-07-12
**Author task:** 16.2 (`tasks/phase-16.md`) — the mid-phase owner gate: consume 16.1's committed
evidence, record the GO/NO-GO in the 14.6 LOCKED-DECISION shape, then perform the phase-doc surgery
the Phase-16 banner promised (GO: Wave 2 activates as written with the served id concretized; NO-GO:
16.12–16.14 removed and 16.15/16.16 rewritten).
**Method:** decision-record only — no code, no template, no replay changes. Every number below is
regenerated from a committed JSONL and each table names its source artifact: the held-constant probe
rows (`experiments/lab/results-featherless-sweep-qwen3-6-27b.jsonl`, report regenerable via
`uv run python -m experiments.lab.featherless_sweep probe-report`), the prompt-set sensitivity rows
(`experiments/lab/results-featherless-sweep-qwen3-6-27b-promptsets.jsonl`), and the owner-directed
from-scratch ladder rows (`experiments/lab/qwen36_prompt_scratch/results-v0.jsonl` …
`results-v5.jsonl`). Zero hand-computed figures.
**Sign-off:** the 14.6/15.18 convention — the LOCKED-DECISION block below is the owner record,
ratified by the owner's merge of this task's PR.

**Label key:** **[RAN]** reproduced by a command on this checkout · **[VERIFIED]** read directly in a
committed source/artifact · **[INFERRED]** reasoned from verified facts · **[PROPOSED]** a
recommendation pending the sign-off merge.

---

## 0. Verdict in one line

**GO** — `Qwen/Qwen3.6-27B` (the exact served id, generation-preflight-confirmed on the flat-rate
plan) is locked as the Phase-16 production model on the pinned non-thinking profile: validity is
clean on both call kinds under `json_object` (reply 16/16, opening 10/10, vote 8/8 — 100%
everywhere), and the owner-directed from-scratch ladder proves a bespoke-set profile —
**0/32 self-co-location, 0/32 self-flag, 32/32 deflect, 8/8 conversion at ~20.5s non-thinking** —
that no incumbent profile matches at any latency; Wave 2 (16.12–16.14) activates as written.

---

## 1. LOCKED DECISION (owner, 2026-07-12) — GO

The 14.6 shape, re-answered for the Phase-16 gate:

- **meeting_model = trigger_model = `Qwen/Qwen3.6-27B`** (homogeneous — both call kinds; the
  HuggingFace repo form exactly as the Featherless generation preflight served it: `pinned=true,
  served=true, attempts=1, evidence="ok"`). The `-Instruct` variant form does NOT exist on the
  plan (HTTP 404 `model_not_found`) — the un-suffixed id is the only servable form.
  **[VERIFIED** — `results-featherless-sweep-qwen3-6-27b.jsonl` `served_id` rows]
- **prompt set = `qwen3_6_27b` v1** — to be authored by Task 16.13 from the scratch ladder's
  `experiments/lab/qwen36_prompt_scratch/v5/` style base with the baseline-3 mechanics merged in
  (mechanics-pure relative to `qwen3_32b` v5/v6), then A/B'd under 16.13's two-pass protocol.
  Until 16.13 lands, no production prompt surface changes; the probe deliberately ran the
  incumbent's `qwen3_32b` set held constant — itself a finding (§3, §4).
- **mode = `non_thinking`, PINNED at request time.** The new generation REASONS BY DEFAULT: kwarg
  absent ⇒ inline `</think>` reasoning (603 channel chars, 263 out-tokens on the probe row);
  `enable_thinking=false` suppresses it (0 channel chars); `enable_thinking=true` reasons (699
  chars). So the 16.12 `_THINKING_KWARG_BY_MODEL` entry is `("Qwen/Qwen3.6-27B", True)` and
  production must PIN `enable_thinking=false` explicitly on every call — an unpinned call would
  leak think-text into recorded state. Thinking mode is REJECTED for production: ~315.0s isolated
  vs ~43.1s non-thinking on the same contexts, and the viable scratch-ladder profile is
  non-thinking-only at ~20.5s.
  **[VERIFIED** — `thinking_kwarg` + `latency` rows, `results-featherless-sweep-qwen3-6-27b.jsonl`]
- **thinking policy = `fail_loud`** (the 14.6 doctrine, unchanged): a non-thinking recorded
  baseline expects NO reasoning channel; a populated one is an auditable error, never silently
  stripped. **[PROPOSED** — the policy carries over; 16.12 implements]
- **response_format_mode = `json_object`** (the incumbent posture ports unchanged): the candidate
  accepts `json_object` 2/2 on BOTH probed schemas (MeetingTurn, VoteBallot) with JSON content;
  strict `json_schema` is deterministically rejected — 0/2 accepted on both schemas, HTTP 400
  across attempts, with the same-pass `json_object` control succeeding (a genuinely busy
  deployment fails both shapes). The incumbent re-verified same-day: `json_schema` rejected 0/2 on
  both schemas (HTTP 422/504 observed — the status drifts from the documented 400; the verdict
  does not). `json_schema` stays selectable for a future endpoint; NO silent fallback between
  modes. **[VERIFIED** — `response_format` rows, `results-featherless-sweep-qwen3-6-27b.jsonl`]
- **Baseline-4 preconditions restated** (the Wave-0 merge criterion (5)): the model is the ONLY
  layer — every Phase-16 lever merged OFF/inert, the 16.3 prompt-byte golden green and
  `verify_samples.sh` bare on the pre-record tree, prompt SEMANTICS ported exactly (16.13's
  mechanics-pure merge), one-layer-per-baseline (`tasks/post-phase-14-plan.md` §4), so the model
  effect and the V&J effect stay separately attributable.
- **Rejected — stay on `Qwen/Qwen3-32B`/`qwen3_32b` (NO-GO):** the rejected path, with its full
  rationale and the surgery it would have triggered, is §5 — the short form: the named
  not-served finding did not materialize, no validity NO-GO exists, and the held-constant probe's
  adverse tell cells measure the old set on the new model, not the new model's ceiling.
- **Evidence:** validity is clean everywhere it was probed — parse 16/16 reply, 10/10 opening,
  8/8 vote, on both modes, both models, under `json_object` (§2). The behavior case is the
  two-set weighing of §4: held constant on the incumbent's prompts the candidate ranks LAST of
  four profiles (reply tell 8/16 vs the incumbent's 6/16 non-thinking), but the owner-directed
  from-scratch ladder — same contexts, same detectors, same model — lands 0/32 tell, 0/32
  self-flag, 32/32 deflect, 8/8 conversion at ~20.5s, strictly dominating the incumbent's
  recorded-baseline profile (38% tell / 25% self-flag / 7/8 conversion at ~32.3s) AND its
  best-any-mode tell (25%, thinking, at ~166.2s). NO validity NO-GO exists; the "not served on
  the flat-rate plan" finding did not materialize. Proceed to Wave 2.

---

## 2. Evidence set 1 — the held-constant probe (Task 16.1)

Source for every number in this section: `experiments/lab/results-featherless-sweep-qwen3-6-27b.jsonl`
(the committed probe rows; the graded report `experiments/lab/report-featherless-sweep-qwen3-6-27b.md`
regenerates from them). **[VERIFIED]**

**Served-id findings** (`served_id` rows — the generation preflight is the arbiter):

| id form tried | pinned? | served | attempts | evidence |
|---|---|---|---|---|
| `Qwen/Qwen3.6-27B` | yes | **yes** | 1 | ok |
| `Qwen/Qwen3.6-27B-Instruct` | no | no | 1 | HTTP 404 `model_not_found` |
| `bottlecapai/ThinkingCap-Qwen3.6-27B` | yes | no | 2 | HTTP 400 "not available for inference" |
| `Qwen/Qwen3-32B` (incumbent re-run) | yes | yes | 1 | ok |

**Validity + latency** (`reply`/`opening`/`vote`/`latency` rows; the incumbent's `qwen3_32b` set
held constant on both models; flag-on substrate):

| model | mode | reply parse | opening parse | vote parse | isolated latency |
|---|---|---|---|---|---|
| qwen3-32b | non_thinking | 16/16 (100%) | 10/10 (100%) | 8/8 (100%) | ~32.3s |
| qwen3-32b | thinking | 16/16 (100%) | 10/10 (100%) | 8/8 (100%) | ~166.2s |
| qwen3-6-27b | non_thinking | 16/16 (100%) | 10/10 (100%) | 8/8 (100%) | ~43.1s |
| qwen3-6-27b | thinking | 16/16 (100%) | 10/10 (100%) | 8/8 (100%) | ~315.0s |

**Behavior cells, read honestly** (`reply` cover-OFF arm + `vote` rows): on the incumbent's
prompts the candidate is WORSE on the tell cells — reply self-co-location 8/16 (50%) vs 6/16
(38%) non-thinking, self-flag 8/16 (50%) vs 4/16 (25%) — and better on deflect (16/16 vs 14/16)
and conversion (8/8 vs 7/8, both modes). The report's ranked recommendation places the candidate
3rd–4th of four profiles ON THIS SET. Two probe-only reads worth keeping: the candidate's cover
lever actually moves its tell (8/16 → 4/16, −25 pp; the incumbent's moves +0 pp), and the opening
corpus is clean for everyone (0/10 tell, 0/10 confess, all four profiles).

**Thinking-kwarg behavior** (`thinking_kwarg` rows): kwarg absent ⇒ reasons by default
(inline `</think>`, no side channel); `false` ⇒ suppressed; `true` ⇒ reasons — the exact evidence
the 16.12 registry entry encodes.

---

## 3. Evidence set 2 — the owner-directed from-scratch ladder (v0→v5)

Sources: `experiments/lab/qwen36_prompt_scratch/results-v0.jsonl` … `results-v5.jsonl` (the ladder,
one rule per version; method and per-version table in
`experiments/lab/qwen36_prompt_scratch/README.md`); comparison baselines from
`results-featherless-sweep-qwen3-6-27b.jsonl` and
`results-featherless-sweep-qwen3-6-27b-promptsets.jsonl`. Same pinned `replays/samples/9p2i`
contexts, same mechanical detectors as the probe; non-thinking, `json_object`, temp 0.4. **[VERIFIED]**

**v5 final validation** (`results-v5.jsonl`, fresh full-corpus run):

| corpus | parse | tell / self-flag | deflect | conversion | latency |
|---|---|---|---|---|---|
| reply (n=32, both cover arms) | 32/32 | **0/32** self-co-location, **0/32** self-flag | **32/32** | — | ~20.5s mean |
| vote (n=8) | 8/8 | — | — | **8/8** | — |
| opening (n=10) | 10/10 | 0/10 tell, 0/10 confess | — | — | — |

**The bar it cleared** (same model, same contexts, non-thinking): the `qwen3_32b` set on
qwen3-6-27b posts 8/16 (50%) reply tell / 8/16 (50%) self-flag / 8/8 conversion
(`results-featherless-sweep-qwen3-6-27b.jsonl`, reply cover-OFF + vote rows); the best existing
alternate set (`glm_4_32b`) posts 5/16 (31%) / 7/16 (44%) / 8/8
(`…-promptsets.jsonl`, cover-OFF arm); the incumbent's best-any-mode tell is 4/16 (25%, thinking,
~166.2s isolated — an n=2 latency micro-pass). Basis note: the baseline reply cells above are the
cover-OFF arm (the sweep report's stated convention); v5's 0/32 spans BOTH cover arms, so the
comparison holds on either basis (cover-OFF 0/16 vs 8/16; both-arms 0/32 vs 12/32). The ladder's
profile beats every one of those cells simultaneously, at the lowest latency measured on any
profile (~20.5s mean reply latency — the README attributes this partly to the compact set: ~7.9k
chars of v5 template text vs the incumbent set's ~12.8k rendered reply prompt).

**Ladder shape** (one rule per version — the README's table, each row regenerable from its
`results-vN.jsonl`): v0's structural accusation-only contract eliminated the structured tell and
the self-flag at the start (self-flag 0% from v0 on); v1–v2's phrasing rules removed the residual
lexical "found the body" tell (56%/31% → 0%/0%); v3–v5's vote rules (graph primacy, flag
directionality, the vent mechanic) converted three distinct observed miss classes (6/8 → 8/8).

---

## 4. How the two evidence sets weigh (the lock reading)

- **The probe answers transport + validity** — served id, `json_object` posture, thinking-kwarg
  semantics, 100% parse on both call kinds — and those answers are unambiguous. It CANNOT answer
  prompt-fit: its own open-risks section records that running the incumbent's set on the candidate
  may understate a model authored against its own templates. **[VERIFIED]**
- **The ladder answers prompt-fit**: on the same contexts and the same detectors, a bespoke set
  takes the candidate to a profile no incumbent configuration matches at any latency — 0% tell /
  0% self-flag / 8/8 conversion at ~20.5s, vs the incumbent's recorded-baseline 38% / 25% / 7/8 at
  ~32.3s and best-any-mode tell 25% at ~166.2s. **[VERIFIED]**
- **The 14.6 lock criterion — validity + latency — is met outright** (validity equal at 100%
  parse; latency wins on the bespoke render), and the behavior upside is large. The residual
  unknown — how much of the scratch profile survives the baseline-3 mechanics merge — is exactly
  what 16.13's two-pass A/B is contracted to measure, with a regression recorded as a finding
  against this lock, and 16.14's canaries pause the phase if the live record disagrees.
  **[INFERRED]**

---

## 5. The rejected path — NO-GO (stay on `Qwen/Qwen3-32B`/`qwen3_32b`), and why not

- **The named NO-GO finding did not materialize**: "not served on the flat-rate plan" is refuted
  by the preflight (`Qwen/Qwen3.6-27B`: served on attempt 1, pinned form). **[VERIFIED]**
- **No validity NO-GO exists**: the candidate parses 100% on both call kinds, both modes, under
  the production `response_format_mode`. **[VERIFIED]**
- **The held-constant probe alone would have argued NO-GO** — the candidate ranks behind both
  incumbent profiles on the tell cells when forced through the incumbent's prompts. Rejected as
  the deciding read: the set–model mismatch is the confounder (the probe's own recorded risk),
  and the owner-directed ladder resolves it on the same contexts and detectors. Weighing both
  sets, the adverse probe cells measure the OLD SET on the new model, not the new model's
  ceiling. **[INFERRED]**
- **What NO-GO would have done** (the surgery branch NOT taken, recorded for auditability):
  REMOVE the 16.12–16.14 contracts and their generated prompts (one prose drop record; task and
  prompt counts fall by three — `scripts/compute_next_task.py` has no dropped state, so removal,
  not labeling); rewrite 16.15 (drop the 16.14 edge; template paths to
  `agents/strategic/prompts/qwen3_32b/`; per-template bumps — the three v5 templates → v6,
  `vote_ballot` v6 → v7) and 16.16 (paths likewise; the second bump — the three → v7,
  `vote_ballot` → v8); re-anchor 16.17's BEFORE column to baseline 3; collapse the model chain in
  the DAG text. None of this was performed.
- **The second candidate is a NO-GO on its own row**: `bottlecapai/ThinkingCap-Qwen3.6-27B` is
  not available for inference on the plan (HTTP 400, 2 attempts — a deployment/chat-template
  failure, not a 404). A first-class recorded outcome, excluded from the graded passes.
  **[VERIFIED]**

---

## 6. Risks carried forward (named, not hedged)

1. **Isolated-turn proxies ≠ the live R-gate** (the 14.x caution, unchanged): parse/tell/
   conversion in isolation can diverge from full-game behavior. Owned by 16.14's canaries
   (degraded-Q3 discipline) — a canary regression PAUSES the phase.
2. **The mechanics merge may erode the scratch profile**: v5 deliberately omits baseline-3
   mechanics (vent elicitation, reporter exculpation, the full observation vocabulary). 16.13's
   two-pass A/B (scratch-verbatim arm vs mechanics-complete arm, per-arm template shas) measures
   exactly this; a measured regression on the tell/self-flag/conversion cells is a finding for
   this lock record, not a silent cost.
3. **Detector-aligned phrasing** (the ladder's own caveat): the v1/v2 phrasing rules align the
   set with the committed lexical detector; a future detector revision (speaker-attributed
   discovery parsing) must re-baseline.
4. **Small n, single day**: 32/8/10 per corpus, one seed set — the 0% cells are strong signals,
   not guarantees.
5. **Default-reasoning posture**: an unpinned request leaks inline `</think>` text; 16.12
   registers the exact id fail-loud and pins `enable_thinking=false`.
6. **Recording-scale latency**: ~43.1s/turn on the incumbent-set render (the bespoke compact
   render measured ~20.5s); 16.14's ~4–5h budget and per-seed crash-retry absorb the spread.

---

## 7. The surgery performed (the GO branch)

Per the 16.2 contract: the Phase-16 STATUS banner records the lock outcome and date; the served id
is concretized where the phase doc said Qwen3.6-27b; the Wave-2 section is marked ACTIVE
(16.12–16.14 stay as written — their contracts already bind to "the locked served id from the lock
audit", which this document supplies); 16.15/16.16's template paths are CONFIRMED already pointing
at `agents/strategic/prompts/qwen3_6_27b/` (no edit needed); `agent_prompts/` regenerated
mechanically (no contract text changed, so no prompt drifts); `validate_task_docs.py` and
`generate_prompts.py --check` green on the re-authored doc. **[RAN** — the CI tail in this PR]

---

## 8. Reproduce

```
# probe report from the committed rows (offline, $0):
uv run python -m experiments.lab.featherless_sweep probe-report
# ladder v5 final validation (needs FEATHERLESS_API_KEY; ~25 min, $0 flat-rate):
PYTHONPATH=. uv run python experiments/lab/qwen36_prompt_scratch/run_iteration.py v5 \
    --full --facts $TMPDIR/ailibi-gameplay-facts-9p2i.json
# doc gates on this checkout:
uv run python scripts/validate_task_docs.py
uv run python scripts/generate_prompts.py --check
```
