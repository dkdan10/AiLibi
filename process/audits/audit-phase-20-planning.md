# Phase-20 planning — evidence honesty: the front door made true, the inference channel repaired, one pre-registered record (planning session, 2026-08-19)

Produced by the Phase-20 planning session against `main` @ `b809b19c`. The research is done
— the three-track review of 2026-08-19 (`audits/review-2026-08-19/`: A/ gameplay top-down,
B/ code bottom-up, C/ portfolio perception, D/ synthesis; 42 watch/sweep/area reports, 26
adversarial verdicts, a cross-track map and a judged final synthesis) — so this dossier is
SHORT: it records the phase shape, the decision, the method changes this PR makes to the
phase machinery, and every divergence from the review's roadmap, with reasons. The
dispatchable contracts live in `tasks/phase-20.md`; the owner's merge of that document
ratifies this plan (the 15.18 convention).

---

## 1. Inputs and baseline

- **Reading list consumed in order:** `audits/review-2026-08-19/D/FINAL-synthesis.md` (the
  judged roadmap in waves, the eight root causes, the claim-by-claim credibility grades, the
  rulings), `D/cross-track-map.md`, `A/collated-findings.md` (G-1…G-41) + `A/verdicts.md`
  (12 adversarial re-derivations), `B/collated-findings.md` (C-1…C-130) + `B/verdicts.md`
  (14), `C/collated-portfolio.md` (A1–A6 musts, B/C items, rulings D1–D9),
  `audits/audit-phase-19-close.md` §4 (the routed post-19 decision), `tasks/phase-19.md` and
  `tasks/phase-18.md` (contract conventions; the 18.9 lever pattern; the 18.11/18.12/18.13
  registration-and-record pattern; the 18.4 pre-registration pattern).
- **Anchor validity:** the review ran against `main` @ `b809b19c`, which is HEAD at
  chartering (the tree is unchanged); every file:line anchor a contract cites was
  re-verified at HEAD by the drafting pass, and the drafting rules required correcting any
  that moved. Numbers the review measured with session scripts are labelled
  REVIEW-DERIVED until Task 20.15 pins them as committed instruments.
- **Gate baseline:** the review's code track re-ran the whole gate at HEAD (default tier
  green; `verify_samples.sh` 100/100 in 3.14 s; `lint-imports` 4 kept / 0 broken; mypy
  strict clean on 354 files). The ladder tip is baseline 6 (the 18.12 adopting record).
- **Ratified rulings inherited, not relitigated:** the substrate-cadence doctrine (one
  combined re-record; smoke before record; gates stack; builds freeze during the window;
  full provenance tuple); the evidence-label discipline; the two-owner gate; errata
  discipline; the three things all three ideation lenses said NOT to change (crew
  same-room-only player vision; the vent channel; the structured cited round-robin with
  SKIP first-class).

## 2. The decision (owner — ratified by the merge of tasks/phase-20.md)

The post-19 menu was "the evidence-honesty substrate phase (A) vs the presentation phase
(B)", with A recommended. The review's synthesis (`D/FINAL-synthesis.md` §6) found the
menu a false choice in the order posed:

1. **Six of the ten biggest credibility risks need no re-record and are claim repairs, not
   polish** — a demo whose map is wrong on 67% of committed frames (C-7), a leak scanner that
   cannot check entitlement (C-31), an import-linter contract covering 89 of 383 files
   (C-32), a README no outsider finishes (A1/A2), an authorship nobody states (A5), results
   stated nowhere once (A6). Shipping them first is narrative correctness at $0, not
   amplification of a broken narrative.
2. **The substrate phase's own instrument is already at HEAD at $0** (`eval/deduction_metrics.py`'s
   proof-vs-inference cells; the four 19.11 injustice fixtures), so the measurement can start
   — and the offline counterfactual can be published — before the record is spent.
3. **The close audit's four scope items map exactly onto findings all three blind tracks
   reached independently:** sighting provenance = G-2/G-4/G-9 ↔ C-11; content-vs-own-memory
   = G-1 + the G-3 ↔ C-2 bug; interval/weighting honesty = G-2's single-tick windows,
   G-36 ↔ C-29; flag naming = G-27/G-29 ↔ C-129. That convergence is the strongest evidence
   that Option A is correctly scoped.

**Ruling:** the free half of presentation now (Wave 0–1), the substrate phase as ONE
pre-registered wave with ONE record (Wave 2), the presentation multiplier on corrected bytes
(Wave 3). If the record fails to move the pre-registered metric, publish it as the result —
this repo has reported a NO-FLIP twice with the losing evidence committed, and every persona
named that honesty as the thing they would hire for. The eight locked decisions are in
`tasks/phase-20.md`.

## 3. The phase shape

**42 contracts, four waves, one record (baseline 7 at 20.36).**

- **Wave 0 — the front door and the demo's defects (20.1–20.7, RR-free, all roots but two):**
  the map body layer reads `TickView.bodies` (C-7); the spectator copy loses the audit
  dialect and the CORRECT-badge spoiler (G-41/B6); the dock stops hiding the map and one
  owner for focus traps (C-9); the replay listing survives a corrupt file (C-5); the
  first-run prompt-set notice goes quiet under the fake provider (B1); `vote_correctness`
  tells the truth (C-113); a GitHub Pages workflow for the static bundle + the owner's About
  checklist (A3/A4).
- **Wave 1 — claims made true, the instruments, readability (20.8–20.22, RR-free):** the leak
  scanner checks entitlement (C-31); import-linter covers the tree and the firewall test
  plants in a temp tree (C-32/C-34); the corpus gate rejects truncation (C-6); kill/report/
  sabotage illegal from a vent (C-1); the README rewrite + authorship + history/glossary/
  audits index (A1/A2/A5/B12); the results stated once — `docs/ml-program.md`, the README
  table, the comparator-defect errata (A6/C-72/C-3); the solvability instrument (the only
  new instrument this phase sanctions); the evidence-honesty instrument set that turns the
  review's numbers into committed pins; the DTO action fidelity + every fetch through the
  client (G-38/C-8); gate hermeticity (C-96/C-35); xdist (C-48); two byte-identical
  speed-ups (C-42/C-43); the architecture SVG + the contract→prompt→PR exhibit (B4/B5); the
  recorder's worker-path coverage (C-74); **THE PRE-REGISTRATION (20.22, owner)**.
- **Wave 2 — the evidence-honesty substrate (20.23–20.36):** eight levers default-OFF
  (completion from events G-3/C-2; the self-location trail G-1; the movement claim shape
  G-9; grounded prosecution + two-source STRONG + endpoint suppression G-2/C-11 — the
  centrepiece; map-aware arbitration R1; structured turn markers G-25; meeting-outcome memory
  with confirm-ejects and testimony-as-content G-35; the coalesced render G-34) + the v4
  prompt-set bump (20.31) + the impostor mover repair as the declared co-intervention
  (20.32) + the stamp registration and recorder preflight (20.33) + **THE OFFLINE
  COUNTERFACTUAL (20.34)** + the smoke (20.35) + **THE ADOPTING RECORD (20.36)**.
- **Wave 3 — presentation on corrected bytes (20.37–20.42):** the graduation sweep under
  "retire means delete" (C-64); the results after the record; the hero still + clip; lessons
  + the curated review; tail truth (B3/B9/B10); **the close (20.42)**.

**Critical path:** 20 tasks, 20.14 → 20.15 → 20.22 → the lever chain → 20.31 → 20.33 → 20.34 →
20.35 → 20.36 → 20.38 → 20.39 → 20.40 → 20.41 → 20.42. The instrument pair heads it —
dispatch 20.14 on day one. The day-one frontier is eleven roots.

**Model assignments, collision discipline and owner gates:** the phase-doc preamble is
authoritative.

## 4. Method changes this PR makes (ratified by the merge; the Phase-19 locked-decision-8 precedent)

The review found the PHASE MACHINERY itself generating findings — history narration in
source (2,691 lines), gates that validate shape not entitlement, graduated levers kept as
accept-and-ignore shims (10 resolvers, 152 test lines), dialect on product surfaces, and
contracts that never said whether a change needed a re-record. Four changes, all in this PR:

1. **AGENTS.md "Craft rules"** — seven rules binding every PR from Phase 20 on (lead with
   intent; a gate must be able to fail; retire means delete; no dialect on user-facing
   surfaces; verifiable-shaped claims; blast radius before scope; record impact + measurement
   on every contract).
2. **The dispatch template (`scripts/prompt_template.md.j2`)** renders into EVERY generated
   prompt: two new pre-flight steps (re-verify every file:line anchor at HEAD; grep the blast
   radius before editing), the seven craft rules, and a verification step that runs the
   contract's `**Measurement:**` command and pastes its output into the PR. This regenerates
   all 363 prompts — a deliberate repository-wide regeneration, recorded here; the contract
   bytes inside every prior prompt are unchanged (the validator's byte-for-byte contract
   check proves it).
3. **The validator (`scripts/validate_task_docs.py`)** requires `**Record impact:**` and
   `**Measurement:**` as inline fields on every Phase ≥ 20 contract (earlier phases are
   history and are not re-validated); `tests/scripts/test_task_doc_guards.py` pins both
   directions.
4. **The review's inputs are committed** under `audits/review-2026-08-19/` (Markdown only;
   the review-session scripts referenced inside them by absolute scratch path were
   session-local and are NOT committed — every number a contract relies on is re-derived by
   a committed instrument at 20.14/20.15, which is the point of those tasks). The curated
   index, the retractions first, and the finding→task→PR map land at 20.40.

Two further conventions, stated here and inherited by the contracts: **every substrate
change is a lever with a counterfactual pin** (not new — the 18.9 pattern made standing);
and **the pre-registration memo precedes the first lever merge** (the 18.4 pattern made
standing for every substrate wave).

## 5. Divergences from the review's roadmap (recorded, with reasons)

1. **The render-version stamp (D §4 item 2.13) is NOT a separate task.** The lever + stamp
   mechanism already IS a render-version system (a replay reconstructs under its recorded
   flags); the cost the judge priced (a one-word prompt fix taxed a re-record) is paid by
   the bump-in-flight archive seam (20.31) and by the "retire means delete" rule (20.37), not
   by a new stamp. If a future phase needs a render change outside a lever, the seam is the
   place.
2. **The agent-clock +1 convention (2.14) is labelled, not changed.** 20.2 puts the
   "agent tick = replay tick + 1" note in the spectator; the substrate change is backlog —
   it would move every rendered tick stamp and is not on the honesty causal chain.
3. **The counterfactual pins live in each lever task AND in one assembly task (20.34)** rather
   than only in 20.34, so every lever PR is judged on its own delta the day it merges (the
   18.9 pattern) and the record has one command that reproduces the prediction.
4. **20.32 (the impostor mover repair) is in Wave 2 before the freeze, not a lever.**
   Reconstruction never re-invokes a policy (`TacticalPolicyStamp`), so committed bytes are
   unaffected and no toggle is needed; it is declared in the pre-registration as the named
   co-intervention (ruling R3) and the policy id stays `fsm-default` with the MANIFEST sha as
   its provenance.
5. **The confirm-ejects role reveal is folded into 20.29** (one lever, `meeting_outcome_memory`)
   rather than a separate engine change: the orchestrator already owns engine translation
   and passes the outcome to the memory fold; the leak scanner's entitlement check (20.8)
   pins the allowance both ways. It is the phase's ONE sanctioned firewall widening and is
   named in the designer rulings.
6. **Untracking the regenerable tournament-report JSONs (C-45 forward half) is backlog.** The
   committed reports are read by the Tournament tab, the doc-fact checker and several pins;
   untracking needs a build step the demo bundle and CI would both have to grow. Recorded,
   not done.
7. **No task ships a hosted live API.** The static bundle is the sanctioned public artifact
   (docs/deployment.md); 20.7 hosts it.

## 6. The owner's About checklist (for Task 20.7 and the planning merge)

After the Pages workflow lands: enable Pages (source = the workflow); set the repository
description (≤ 350 chars): *"Deterministic social-deduction sim (Among-Us-style) with LLM
agents behind an enforced observation firewall — built by directing AI coding agents
against written contracts: 350 PRs, 19 phases, byte-identical replays, honest negative ML
results."*; topics: `multi-agent`, `llm-agents`, `social-deduction`,
`deterministic-simulation`, `agentic-coding`, `claude-code`, `evaluation`, `among-us`,
`python`, `fastapi`, `react`, `pixijs`; homepage = the Pages URL. The README badges and the
demo URL land at 20.12.

## 7. The backlog (out, recorded)

The balance wave (post-meeting reset G-5; finished-crew jobs G-15; vent peek G-13; `saw_kill`
+ a kill contradiction kind G-8; symmetric roll-call G-22; sabotage as a real clock G-40; the
4p1i second act) — a chartered wave with its own record. The God-module decompositions
(C-62). The `agents ↛ training` fork (C-33; a parity paragraph + a mask-parity test instead).
The git-history rewrite (C-45). The walker consolidation's 13-flag matrix (C-37). The
remaining ~94 P2 code findings and the text-hygiene tail (G-26, G-29 beyond the prompt bump,
G-36 duplicate flags). The agent-clock convention (G-37). The ML re-open fork (locked at
Phase 19: decided only against a concrete proposal). A spectator "watch" CLI (the review's
`watch.py` instrument, productized). The finalist raw slate's home is decided at 20.41.
