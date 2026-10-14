# Post-Phase-14 pause — a health assessment and a direction call

**Date:** 2026-07-04
**Author task:** step back after Phase 14 closed (baseline 2, 2026-07-03), independently assess how well the
project is shaped, run the checks worth running, and recommend where Phase 15 should go — the two documented
options (`post-phase-14-ML-planning.md`, `post-phase-14-Voice-and-Judgment-planning.md`) or a new one — plus
where to harden, refactor, or de-stale.
**Method:** read-only. I re-ran the full gate on HEAD (`352a014`), reconstructed all 100 committed samples,
and fanned out a six-dimension adversarially-verified assessment (architecture, tests, staleness, eval-harness
gap, determinism/firewall, direction). Every finding below is cited to a `file:line`, a committed artifact, or
a command I ran. The only repo output is this file.

**Label key:** **[RAN]** reproduced by a command on this checkout · **[VERIFIED]** read directly in source ·
**[CONFIRMED]** independently re-checked by an adversarial verifier · **[INFERRED]** reasoned from verified
facts · **[PROPOSED]** a recommendation.

---

## 0. Verdict in one line

The project is in **genuinely strong mechanical health** — every gate is green, 2463 tests pass, and all 100
committed replays reconstruct byte-identically — but its **written front door and its measurement harness have
drifted out from under the code**: the README/AGENTS/DESIGN docs describe a Phase-5 "MVP" running a provider
and model the repo no longer uses, and the "validity gate" + "R-gate" that every Phase-14 close audit cites
**by filename do not exist as committed code**. The right Phase 15 is **Voice & Judgment, sequenced
harness-first** — it is the only option that moves the one metric Phase 14 did *not* improve, it does so with a
measured ~4:1 trade proven offline before any spend, and its first task is exactly the harness both directions
need. Defer ML tactical play to a later phase — higher ceiling, real roadmap pedigree, but it does not touch
the measured defect and its cheap-fitness linchpin already regressed once.

---

## 1. Mechanical health — what I ran, all green

Everything below is **[RAN]** on HEAD `352a014` (branch `claude/phase-14-assessment-8sfm1t`), fresh `uv sync`.

| Gate | Result |
|---|---|
| `ruff check .` | All checks passed |
| `ruff format --check .` | 228 files already formatted |
| `lint-imports` | `Agents must not import engine` **KEPT** (1 contract, 1 kept, 0 broken) |
| `validate_task_docs.py` | 202 tasks and 202 prompts validated |
| `generate_prompts.py --check` | all 202 prompts in sync |
| `mypy .` | Success: **no issues in 203 source files** (`strict = true`) |
| `pytest` | **2463 passed, 20 skipped, 3 xfailed** in 76 s |
| `verify_samples.sh` (bare env) | **All 100 samples verified clean** (50 × 9p2i + 50 × 4p1i) byte-identical |

The 20 skips are all legitimately env-gated (real-provider / Ollama / perf benchmarks, plus two documented
data-shape skips); the 3 xfails are `strict=True` and encode an **owner-approved** asymmetric-visibility
emergency redesign deferred to "Wave B" (`tests/orchestrator/test_meeting_integration.py:2370-2373`), so they
cannot silently rot. There is **no hidden flakiness**: determinism is enforced by construction, and the one
randomized test (the Hypothesis firewall sweep) runs against a pure function.

This is a real strength and worth stating plainly: **CI discipline on this repo is excellent.** The problems
below all sit *underneath* the green gates — which is exactly where a healthy project's remaining risk lives.

---

## 2. The two findings that matter most

### 2.1 The measurement harness the project's core claim rests on is not committed code — [CONFIRMED]

The project's headline discipline is "a prompt/lever change must move a metric, attributably, reproducibly."
Phase 14's close audit (`audit-phase-14-close.md` §1, §8) grounds every number in two scripts —
`scripts/validity_gate.py` (the HARD validity gate) and `scripts/measure_baseline.py` (the R-gate). **Neither
exists.** [RAN] `find . -name validity_gate.py -o -name measure_baseline.py` → empty;
`grep -rE 'validity_gate|measure_baseline' --include=*.py --include=*.sh` → zero hits. They are named in exactly
two markdown files (the close audit and the ML plan) and nowhere in the tree.

What *does* exist is the substrate: the atomic metrics are committed, `mypy --strict`-clean, and tested —
ejection accuracy and genuine-class conversion (`eval/vote_correctness.py:302,558`), meeting rate and
indistinguishability (`eval/meeting_quality.py`), win rate (`eval/balance_eval.py:894`), accusation
calibration (`eval/accusation_calibration.py`) — and `scripts/build_sample_report.py` folds them into the
committed per-set `tournament-eval-report.json`. But:

- **No one-command pass/fail gate.** [RAN] `grep -rlE '__main__|argparse|def main' eval/` → empty. The metrics
  are library folds; nothing composes them into a validity boolean or a baseline-to-baseline delta.
- **The numbers that define the Phase-15 target are not reproducible from a fresh checkout.** The zero-flag
  channel-split decomposition — the whole motivation for what comes next — was produced by five scratch scripts
  the Voice doc itself says were "kept out of the repo" (`post-phase-14-Voice-and-Judgment-planning.md:836`:
  `channel_split.py`, `zeroflag_render.py`, `voice_metrics.py`, `vent_census.py`, `pp.py`). A fresh clone can
  regenerate the `vote_correctness`/`meeting_rate` layer, but not the channel decomposition that the strategic
  pivot rests on. [CONFIRMED]
- **The R-gate's own inputs live in non-production tiers.** The R1 eject-decided fold is in
  `audits/workflows/extract_gameplay_facts.py` (a 217 KB audit-side script) and `experiments/lab/rubric_score.py`
  — the latter *self-labels* "a design-thread analyzer, NOT a shipped eval … the rubric is directional, not a
  hard gate." So even the folds that exist for the R-gate carry a provenance caveat.
- **The cited cross-check overstates.** `audit-phase-14-close.md` §1 says the gate is "cross-checked by
  `bash scripts/check.sh`," but check.sh runs static hygiene + unit tests only — no baseline measurement. The
  entire measurement pipeline is **outside CI**; nothing re-derives or guards the baseline numbers on a commit.

**Why this is the top finding:** it is not a code bug — it is a gap between the project's *stated* discipline
and its *committed* tooling. Promoting the scratch folds into a committed `eval/` gate is ~80% wiring of code
that already exists (both plans size it as "promotion + consolidation, not new metric code"), it is **direction-
agnostic** (ML calls it S0, Voice calls it 15.1, and 15.1 has no dependencies), and it is the precondition for
any future "measurable delta" claim being reproducible by anyone but the audit author. **This should be Phase-15
task zero regardless of which direction is chosen.**

### 2.2 The public docs describe a project nine phases and one provider ago — [CONFIRMED]

All three onboarding docs present a Phase-5 "MVP" world. A reader — human or a dispatched coding agent —
onboarding through them would be wrong about the project's phase, provider, model, scale, and sample layout.

| Stale claim | Location | Reality |
|---|---|---|
| Status table ends at Phase 5, "**MVP complete**", Phase 6 = only future | `README.md:50-58` | 14 phases closed, 202 task contracts, baseline 2 committed |
| "82 merged PRs across phases 0–5, 980 passing tests, 29 read-only audits" | `README.md:13` | 202 contracts, **2316** test functions, ~52 audit reports (≈1.8–2.5× every number) |
| Ollama **`qwen3.5:9b`** is "the canonical provider for the meeting-heavy eval set" | `README.md:107-122`, `AGENTS.md:64-72` | Baseline 2 recorded on **Featherless `Qwen/Qwen3-32B`** (`llm/featherless_client.py:135`, `refresh_samples.sh:417-426`) — and `qwen3.5:9b` is not a real model id |
| "50 sample replays under `replays/samples/` … 36% impostor win … ~$0.91" | `README.md:89-91` | **100** samples in `9p2i/`+`4p1i/` subdirs (flat dir is empty), Featherless **$0**, baseline-2 impostor win **0.40** |
| DESIGN: "sabotage (lights only) … No reactor / O2 … task counter still progresses" | `DESIGN.md:734,759,321` | A **reactor task-gating sabotage** (`gates_tasks:true`) is implemented and enforced (`engine/tick.py:151-154,274-277`) |
| DESIGN names Ollama model "**qwen2.5:7b-instruct**"; README names "**qwen3.5:9b**" | `DESIGN.md:709` vs `README.md:114` | The two authoritative docs disagree with each other and both are stale |

Featherless, Qwen3-32B, the 9p2i/4p1i roster sets, the five substrate levers, and the baseline-1/2/3 program
— the vocabulary that dominates phases 6–14 and *both* next-direction plans — appear **nowhere** in README.
[RAN] `grep -ni 'featherless|qwen3-32b|9p2i|4p1i|baseline' README.md` returns only unrelated Phase-4 "substrate
fix" tasks. Separately, `experiments/lab/report-ml-spike.md` presents its `top-1 64%` surrogate figure as the
final conclusion with **no stale marker**, even though the ML plan has shown it regressed to ~26% on the
re-recorded corpus — a live trap for a future agent deciding whether ML's offline-trainability thesis holds.

This is low *code* risk but high *onboarding/provenance* risk, and it is near-zero-cost to fix. **Bundle the
doc refresh into the same harness task (§2.1)** — turning audit-prose-only state into committed, self-describing
artifacts is the same act in both cases.

---

## 3. Architecture — strong discipline, three real debts under the green gates

**Health: mixed.** The static posture is genuinely good and the substrate-lever machinery is clean. But three
debts are worth naming, and one of them sits directly in Phase 15's path.

- **The entire `StrategicReasoner` (810 LoC) is dead code — stronger than the ML doc reported.** [CONFIRMED]
  The ML plan flags only the *triggered* strategic-LLM path as unwired. In fact the whole class is unused in
  production: `grep 'StrategicReasoner('` finds instantiation **only** in `tests/agents/test_strategic_reasoner.py`
  (1820-LoC test), and the live meeting path is `MeetingManager`, which renders via
  `agents.strategic.prompts.loader` and calls `llm_client.complete()` directly (`meetings/manager.py:1185,1597`).
  `agents/strategic/output_schemas.py` is part of the same dead island. ~2.7 KLoC passes ruff/mypy/tests yet is
  never invoked, and it reads as a *live alternate meeting path* to anyone exploring the code. **[PROPOSED]**
  delete it or explicitly re-wire it before Phase 15 builds new meeting behavior on top of the confusion.

- **`api/replay_loader.py` is the one god-file a decomposition would actually pay for.** [VERIFIED] A 1160-LoC
  stateful `ReplayLoader` class (`:462-1623`, 31 methods) conflating four responsibilities — file
  discovery/caching, tick-walk reconstruction, HTTP view assembly, and substrate/rubric provenance — and it is
  the **highest-churn** of the large files (8 commits). The ~35 pure `_*_view` mappers below it already lift
  cleanly into a view-serialization module. Unlike the other big files, this split reduces real blast radius:
  a mis-stitched mapper here corrupts what the spectator UI shows during Phase-15 eval.
  *(By contrast: `meetings/manager.py` (3084) has extractable pure-function clusters worth ~500 LoC of
  opportunistic cleanup; `eval/meeting_quality.py`, `meetings/transcript.py`, and `agents/memory/store.py` are
  **cohesive-but-large** — a split would move code, not reduce coupling. Do not refactor those.)*

- **Layering rests on one import-linter contract and reviewer vigilance.** [CONFIRMED] `.importlinter` defines
  exactly one contract (`agents ↛ engine`). A genuine cross-package cycle exists —
  `meetings.manager → agents.memory.beliefs → meetings.schemas` (`meetings/manager.py:88`) — invisible to
  tooling and safe only because the packages import disjoint submodules. And the **0.60 eject-gate constant**,
  which is *exactly* what Voice&J's Judgment lever proposes to cap suspicion below, lives inside the 3084-LoC
  `manager.py` (`DEFAULT_SKIP_CONFIDENCE_THRESHOLD`, `:138`) and is imported upward by agents/api. It is also
  **deliberately re-declared** as a literal in `eval/_suspicion_parse.py:54`
  (`SKIP_SUSPICION_THRESHOLD = 0.60`) — and here the intent is *documented and correct*: eval must classify
  already-recorded ballots against the threshold they were **recorded under**, not "whatever the live knob later
  becomes," and the module stays import-free for the audits workflow (`:46-53`). So this is not an accidental
  drift bug. But it *is* a coupling with a Phase-15 hazard: when baseline 3 is recorded under a new gate value,
  someone must remember to move this pin in lockstep, and **no test asserts the pin still matches the value the
  current baseline was recorded under.** **[PROPOSED]** before the Judgment lever lands: give the *live* gate
  constant one shared home, add a test that pins `SKIP_SUSPICION_THRESHOLD` to the recorded-baseline threshold,
  and add the two cheap import contracts that are clean today but unguarded (`observation ↛ agents/meetings/llm`,
  and `agents ↛ meetings.manager`).

**Strength worth banking:** the substrate-lever machinery (`orchestrator/replay.py:241-303`) is a well-factored
~60-LoC declarative table — 5 retired-always-on levers, 0 toggleable today, all `Final` tuples, no mutable
module state. Adding a Phase-15 lever is a two-line change; graduating it to unconditional appends one string.
The pattern has run five times and is sustainable for the Judgment lever. Phase 14 was right to leave it clean.

---

## 4. Determinism & firewall — sound invariants, four latent hazards, two in Phase 15's path

**Health: mixed.** The two load-bearing invariants are structurally real: the belief fold is order-deterministic
(every *accumulating* consumer wraps `known_players()` in `sorted()`; the unsorted sites are order-independent
`any()` checks), and `ObservationPacket` is a closed `extra="forbid"` schema hand-built field-by-field, so a new
`WorldState` field **cannot auto-leak** into a packet. But four hazards evade CI, and the first two touch exactly
the belief/gate surface Voice&J will edit.

1. **Raw-vs-rendered gate disagreement in the `[0.595, 0.60)` band — [CONFIRMED, HIGH].** The ballot-redirect
   guard (`meetings/manager.py:2486-2498`) recomputes the §4.6 MUST-vote verdict from **raw** `suspicion` floats
   against the 0.60 gate, and its docstring asserts guard and rendered verdict "cannot disagree." But the prompt
   renders suspicion through `"%.2f"` (`store.py:1566-1569`, `manager.py:1577`), so a raw value in `[0.595,0.600)`
   **displays as "0.60" → the model reads MUST-vote** while the guard's raw read is MUST-skip and leaves the
   ballot unredirected. That band is reachable (a 0.63 prior decays toward 0.5 and lands ~0.5975). This is
   precisely the raw-vs-rendered consistency the Judgment lever must get right, since it introduces a new
   render-time clamp on the same scalar.

2. **`state_hash` cannot see a belief-fold change — the exact Phase-15 lever shape. [VERIFIED, MEDIUM]** The
   per-tick `state_hash` serializes only engine `WorldState` (`orchestrator/replay.py:766-796`); agent belief
   state is reconstructed separately by the loader. So retuning a delta in `agents/memory/beliefs.py` (the
   Judgment cap, `ACCUSATION_SUSPICION_DELTA`, testimony-spread) yields **byte-identical engine hashes and passes
   `verify_samples` unchanged.** This is the same gap the tests dimension found independently as the **"C9 catch"**
   [CONFIRMED, HIGH]: `scripts/_verify_samples.py` checks only engine `state_hash`, never re-renders the meeting
   prompt bytes, so a belief-fold change that alters the rendered prompt but not the WorldState slips through
   byte-clean. The only guard is the substrate stamp — and since all levers are retired-unconditional, the
   ambient snapshot is hardcoded all-True, so it only fires on an explicit key mismatch. **[PROPOSED]** Phase
   15's harness task should add a **prompt-byte golden** — re-render every recorded meeting's turn/ballot prompts
   from live belief-fold code and assert equality with the committed `llm_calls[].prompt` (the Voice doc's C9
   remedy, `15.0` DoD). Without it, byte-identity is not actually proven across a belief change.

3. **A two-accusation gate crossing is correct by IEEE-754 luck. [VERIFIED, LOW-but-sharp]** The design intent
   (`ACCUSATION_SUSPICION_DELTA` docstring) is that a subject accused across two meetings reaches 0.60 and
   becomes ejectable. [RAN] `0.5 + 0.05 + 0.05 == 0.6000000000000001` — it clears the inclusive `>=` gate only
   because the residue rounds *up*. Had it rounded down (as other delta combinations do), the second accusation
   would silently fail to reach the gate. No test pins boundary sums against the gate. **Any Phase-15 retune of
   the accusation/spread deltas — which the Voice/Judgment tracks explicitly touch — could land an intended
   gate-crossing a hair under 0.60 and silently break the two-signal eject.** [PROPOSED] add boundary-sum tests
   pinned to the gate before touching `beliefs.py` deltas.

4. **Firewall enforcement is a test-time denylist. [VERIFIED, MEDIUM-harden]** The structural `extra="forbid"`
   schema is the real protection, but the only *content* check is `eval/leak_test.py` — a denylist of four exact
   field names + three value substrings, run over **3 scripted fixtures** with **no `agent_factory`**. It is
   substantially (not fully) mitigated by a Hypothesis property sweep over the same scanners
   (`tests/observation/test_leak_property.py`), which covers any reachable `WorldState` because `build_packet` is
   pure. Still: a developer who declares a new packet field with an innocuous key name and a non-substring value
   slips the denylist, and a learned agent (ML Option A) would drive the engine into regions the 3 fixtures never
   reach. [PROPOSED] extend `leak_test` to accept an `agent_factory` (both plans list this) before any ML work.

**On the per-tick RNG:** the ML doc's `json.dumps` observation is real (`engine/rng.py:31-38`) but its framing is
correct and I want to be precise so no one "optimizes" it: the drawn value is discarded, **but** `next_rng_state`
is written into `WorldState.rng_state` and is hashed into every `state_hash` (`replay.py:761-796`). It is
vestigial for *gameplay* determinism and **load-bearing for *replay* byte-identity** — all 100 committed samples
reconstruct only because that serialization is stable. The ML doc already scopes any speedup to a training-only
fast path behind a re-record (`post-phase-14-ML-planning.md:639-647`); that is the correct handling. **Do not
touch it in place.**

---

## 5. The direction call — Voice & Judgment, harness-first

**Recommendation: Phase 15 = Voice & Judgment, sequenced harness-first. Defer ML tactical play to a later phase
(deferred, not dropped).**

### 5.1 Why Voice & Judgment, and why not ML — now

The decisive axis is **alignment with the one measured defect**, and it is not close. Phase 14 closed with a
single clean residual: the **zero-flag / voice-driven crew mis-eject channel** rose 22→31 and now dominates 31
of 56 crew mis-ejects (`audit-phase-14-close.md:92-105`) — it is why 9p2i ejection accuracy held flat
(0.566→0.525) even though every other target improved.

- **Voice & Judgment attacks that number head-on.** [CONFIRMED] It independently reproduced the channel split
  from committed bytes, decomposed it (82% of deciding votes are soft-band 0.60–0.69 gate-crossings on a bare,
  unprovenanced suspicion scalar that *no gate requires to cite evidence*), and priced the fix as a measured
  **~24 crew mis-ejects prevented : 6 impostor catches at risk, 10 hard-backed catches preserved (≈4:1
  favorable)**. It ships as **default-OFF levers in the exact 13.5/14.10 pattern the repo has run five times**:
  prove it offline on the committed bytes via `allow_substrate_mismatch`, ship OFF = byte-identical to baseline
  2, spend **one atomic re-record (~3.85 h, $0)**. Fully reversible; inherits the risk profile of every prior
  phase.

- **ML tactical play is the wrong Phase 15 — by its own document.** [CONFIRMED] Its §12 concedes a smarter
  stealth impostor *starves meetings of testimony and un-makes the deduction game* — a self-identified tail
  risk. Its cheap-offline-fitness linchpin (a physical suspicion-rank surrogate) **already regressed** top-1
  64%→26% on the re-recorded corpus, *because of the very channel shift Voice&J targets*. It needs new
  dependencies (numpy minimum, torch if PPO — breaking the pure-Python/$0 posture; [RAN] neither is in
  `pyproject.toml`), a training harness, and a surrogate meeting-runner that don't exist. It does **not move the
  measured number** — it is discovery/portfolio work, and this project's whole discipline is measured-defect-
  driven.

### 5.2 The honest case for ML (why *deferred*, not *dropped*)

Weighed fairly: ML has the **higher ceiling and real roadmap pedigree** — `DESIGN.md §12` explicitly rosters
"Reinforcement learning for tactical policies" and a "Tournament simulator (Strong portfolio piece)," the
substrate is genuinely ML-ready (drop-in `agent_factory`, zero engine edits, byte-deterministic record path),
and the feasibility spike already proved the plumbing. The conservative Option-1 path (a learned utility scorer
over the FSM's own legal options, ES not PPO, watchability-gated) is well-bounded. It is the right *later*
phase — attempted **after** the harness exists and **after** a structural-information lever gives learned
tactics something legible to produce.

### 5.3 On the third path, and the deeper ceiling

The prompt invited a third option — a standalone "harness-first hardening phase." That instinct is right about
the gap (§2), but it **does not merit its own phase**: it is already the first task of the direction I
recommend (Voice 15.1 == ML S0 == "productize the gate"). Fold the doc refresh (§2.2) and the determinism
guards (§4) into that same task. Do **not** let 15.1 be narrowly scoped to just the eval folds.

One deeper truth both plans independently reach, worth flagging to the owner: neither headline option lifts the
**~45% detection ceiling**. The crew's entire deduction signal is "the impostor was seen where it shouldn't be"
under same-room-only vision (112/112 committed contradictions are `alibi_vs_sighting`), and Voice&J's own seed-9
hand-read shows the sharp version — a *witnessed vent* (real hard evidence) **lost to voice because it stayed
private and never entered the transcript**. That is a structural-information / aggregation problem the Judgment
track only partially reaches. It does not change the ranking, but the **structural-information lever
(vents/sabotage/vision surfacing, private-evidence aggregation)** is the real ceiling-lifter behind both
options, and it is the honest answer to "what's the biggest lever" once the measured Judgment win is banked.

### 5.4 Recommended sequence

```
15.1  Productize the harness (task zero, direction-agnostic):
        · promote channel_split/zeroflag_render/voice_metrics/vent_census scratch folds into committed eval/
        · a one-command validity-gate + R-gate that reproduces every baseline-2 number from committed bytes
        · a prompt-byte golden (the C9 remedy, §4.2) + boundary-sum gate tests (§4.3)
        · refresh README / AGENTS / DESIGN to the Featherless/Qwen3-32B/14-phase reality; mark ml-spike stale
        · (opportunistic) delete the dead StrategicReasoner; home the 0.60 gate constant; add 2 import contracts
15.0  Shared foundation: per-subject suspicion provenance + widened render-input contract (byte-identical)
15.2  Judgment: hard-evidence gate lever (default-OFF)   ┐  disjoint tracks
15.4  Voice: deterministic per-seed persona registry     ┘  after 15.0
15.3  Judgment: provenance-aware, citation-gated vote surface (evidence gate must precede persona text)
15.5  Voice: persona-conditioned prompts (v5) — lands after 15.3, so louder voices never ship without the gate
15.7  Baseline 3: one atomic re-record + phase close
```

This honors the Voice doc's "design them together" thesis (the persuasion literature says a louder persona
layer without an evidence gate makes "voice beats evidence" *worse*), gets the measured 4:1 Judgment win moving
first, and de-risks a future ML phase by leaving behind a committed, reproducible harness.

---

## 6. Prioritized punch list

**Do in Phase-15 task 15.1 (foundational, direction-agnostic):**
1. Promote the five scratch measurement scripts into committed `eval/` + a one-command validity/R-gate that
   reproduces baseline-2 from committed bytes (§2.1). *The single highest-leverage item.*
2. Add a prompt-byte golden that re-renders recorded meeting prompts from live belief-fold code (§4.2, C9).
3. Refresh README / AGENTS.md / DESIGN.md to current reality; add a `[STALE]` banner to `report-ml-spike.md`
   (§2.2).
4. Add boundary-sum tests pinning belief deltas against the 0.60 gate before any delta retune (§4.3).

**Do before the Judgment lever touches the gate:**
5. Give the *live* `DEFAULT_SKIP_CONFIDENCE_THRESHOLD` one shared home; add a test pinning eval's
   (deliberately re-declared) `SKIP_SUSPICION_THRESHOLD` to the threshold the current baseline was recorded
   under, so a Phase-15 gate change can't desync the two silently (§3).
6. Resolve the raw-vs-rendered `[0.595,0.60)` gate disagreement — the guard and the model must agree on the
   verdict (§4.1).

**Cheap hardening / hygiene, opportunistic:**
7. Delete or re-wire the dead `StrategicReasoner` island (~2.7 KLoC) (§3).
8. Add the two clean-but-unguarded import contracts (`observation ↛ agents/meetings/llm`;
   `agents ↛ meetings.manager`) (§3).
9. Extend `eval/leak_test.py` to accept an `agent_factory` (blocks a firewall gap; prerequisite for any ML
   work) (§4).

**Deferred, larger, own-phase work:**
10. Decompose `api/replay_loader.py` — the one god-file whose split reduces real blast radius (§3).
11. ML tactical play — after the harness exists and a structural-information lever lands (§5.2).
12. A structural-information lever (vents/sabotage/vision surfacing + private-evidence aggregation) — the real
    detection-ceiling lift behind both directions (§5.3).

---

## 7. What I did not do / caveats

- This is a static + committed-bytes assessment. I did **not** run a live-provider re-record (that is 15.7's
  spend gate) or re-validate the ML surrogate's 26% figure end-to-end (I take the ML doc's `[V-ran]` at its
  word; the number's *direction* is corroborated by the close audit's rising zero-flag channel, which I
  reproduced conceptually via the committed split).
- Two verifier corrections are folded in above so they don't propagate: the README staleness magnitude is
  **~1.8–2.5×** on every metric, not the larger figure a first pass suggested; and the per-tick RNG is
  **load-bearing for replay byte-identity** and already handled correctly by the ML doc — it is a "don't touch
  in place" note, not a doc defect.
- The direction call is a recommendation, not a mandate. The genuinely owner-only questions remain: (a) is a
  rise in impostor win-rate from smarter play acceptable if watchability holds (the ML watchability contract);
  (b) is body-proximity "hard evidence" for the Judgment exemption or should it be downweighted; (c) is the
  owner willing to spend an owner-gated structural-information lever (§5.3) to lift the detection ceiling. Those
  three are laid out in each planning doc's "open questions for the owner."

---

## 8. Bottom line

Phase 14 landed cleanly and the machine is healthy — green gates, 2463 passing tests, byte-identical replays,
and a substrate-lever pattern that is a pleasure to extend. The remaining risk is not in the running code; it
is that the project's **measurement discipline and its own documentation have quietly become audit-prose rather
than committed artifacts.** Phase 15 should **fix that first** (productize the gate, refresh the docs, add the
two belief-fold determinism guards), then take the **Voice & Judgment** win — the one direction that moves the
metric Phase 14 could not, with a measured favorable trade, proven offline before a dollar is spent. Keep ML
tactical play on the roadmap for the phase after, from a de-risked and instrumented base.
