# Phase 20 — Evidence honesty: the front door made true, the inference channel repaired, one pre-registered record

STATUS: PLANNED (owner ratification pending — the owner's merge of this document ratifies
the plan, the 15.18 convention). Chartered from the three-track review of 2026-08-19
(`audits/review-2026-08-19/`, the planning inputs, committed by this PR) and its synthesis
(`audits/review-2026-08-19/D/FINAL-synthesis.md`); the phase shape, the decisions, the method
changes this PR makes to the phase machinery, and every divergence from the review's roadmap
are recorded in `audits/audit-phase-20-planning.md`. The pre-registration memo
(`audits/audit-phase-20-preregistration.md`) ships in this PR with REVIEW-DERIVED provisional
cells and is re-pinned from committed instruments at Task 20.22 BEFORE any substrate fix
exists. The ladder tip at chartering is baseline 6 (the 18.12 adopting record); this phase
records ONE adopting record (baseline 7, Task 20.36) under a pre-registered decision rule
that can ADOPT the new substrate or record it as a FINDING — either way the numbers are
published. 42 contracts across four waves; the close (20.42) routes the next decision.

## Locked decisions (owner-ratified by the merge of this document)

1. **The post-19 decision, resolved.** Neither "substrate first" nor "presentation first" in
   the order the close audit posed them. Wave 0 and Wave 1 ship the re-record-free half of
   presentation — which is mostly CLAIM REPAIR (the leak scanner's entitlement check, the
   import-linter coverage, the phantom-corpse map, the results stated once), not polish —
   then Wave 2 is the evidence-honesty substrate phase the close audit recommended
   (`audits/audit-phase-19-close.md` §4.2), as ONE pre-registered wave with ONE record, then
   Wave 3 is the presentation multiplier on corrected bytes. Rationale and the cost argument:
   `audits/audit-phase-20-planning.md` §2.
2. **Pre-registration binds before the fixes.** The primary bars, the decision rule, the
   co-intervention declaration and the record order are written and ratified (20.22) before
   any lever exists; the record (20.36) is read against that memo verbatim; a bar that is
   missed is a finding, never re-priced (the Phase-14/18 doctrine). The offline
   counterfactual (20.34) publishes the predicted deltas before the 23-hour record is spent.
3. **Every substrate change is a lever, default-OFF, until the record.** Eight levers
   (`task_completion_from_events`, `self_location_trail`, `movement_claim_shape`,
   `grounded_prosecution`, `map_aware_arbitration`, `structured_turn_markers`,
   `meeting_outcome_memory`, `coalesced_memory_render`) plus ONE prompt-set bump
   (`qwen3_6_27b` v3 → v4, the 16.15 archive-seam pattern). OFF-path bytes are byte-identical
   (the prompt byte-golden and `verify_samples.sh` stay green through every merge); ON-path
   behaviour is fixture-pinned; every lever carries a committed-bytes counterfactual pin.
   The levers register into the substrate stamp at 20.33 (the 18.11 pattern) and graduate —
   or stay toggles — at 20.36 under the decision rule; graduation DELETES the gate (20.37).
4. **One prompt edit, in one task.** Game prompt templates change ONLY in 20.31 (the v4
   bump: proof vs conflicting accounts, the impostor count, no threshold talk, the
   dead-subject vent exemption, the adjacency card, the movement shape). No other contract
   touches `agents/strategic/prompts/*.j2`; the bump-in-flight archive keeps the committed
   recordings golden until the record re-aligns them.
5. **The comparator is repaired and declared.** The impostor mover's two target-selection
   defects (C-3: 45.8% of free zero-witness kills declined on an id tie-break; G-12: stalking
   ejected players for 8–12% of 9p2i decisions) are fixed at 20.32 BEFORE the freeze and
   declared in the pre-registration as a named co-intervention — a defect repair, not a
   balance lever (the synthesis ruling R3). Balance levers (post-meeting reset, finished-crew
   jobs, vent peek, `saw_kill`, symmetric roll-call, sabotage, the 4p1i second act) are OUT:
   a separate chartered balance wave with its own record (the backlog, §Cut line).
6. **The method changes this PR makes to the phase machinery are ratified by this merge**
   (the Phase-19 locked-decision-8 precedent: a repository-wide control-surface change,
   recorded accurately): (a) AGENTS.md gains the seven "Craft rules" the review found the
   codebase violating at scale (lead with intent; a gate must be able to fail; retire means
   delete; no dialect on user-facing surfaces; verifiable-shaped claims; blast radius before
   scope; record impact + measurement on every contract); (b) the dispatch template
   (`scripts/prompt_template.md.j2`) renders the craft rules, an anchor re-verification and
   blast-radius pre-flight, and a Measurement-paste verification step into EVERY generated
   prompt — this PR regenerates all 363 prompts (321 prior + 42 new), a deliberate
   repository-wide regeneration; (c) `scripts/validate_task_docs.py` requires the two new
   inline fields `**Record impact:**` and `**Measurement:**` on every Phase ≥ 20 contract
   (`tests/scripts/test_task_doc_guards.py` pins it); (d) the review's inputs are committed
   under `audits/review-2026-08-19/` so every `G-n`/`C-n`/`A-n` id a contract cites resolves
   in-repo.
7. **The cut line: 42 contracts, four waves, one record.** OUT and recorded (not silent) in
   `audits/audit-phase-20-planning.md` §5: the balance wave; the God-module decompositions
   (C-62) and the `agents ↛ training` fork consolidation (C-33 — its load-bearing risk was
   REFUTED by experiment; one paragraph + a mask-parity test buys the credit); the git-history
   rewrite (C-45 — it would break the 43/44 live in-code citations and the authorship graph
   that is A5's evidence; untrack regenerable aggregates going forward instead); the
   `died_at` field and the "bodies survive meetings" fix (both REFUTED by the review's own
   verification); the agent-clock +1 convention change (G-37 — labelled in the UI at 20.2,
   the substrate change deferred); any ML re-open; the ~94 remaining P2s as a triaged backlog.

## Designer rulings (recorded here so contracts inherit them)

- **Evidence labels are binding.** Every contract's Section refs cite the review register
  ids (`G-n` gameplay, `C-n` code, `A-n`/`B-n` portfolio) with the committed file under
  `audits/review-2026-08-19/` that owns them, plus file:line anchors re-verified at HEAD by
  the drafting pass. Numbers quoted from the review are labelled review-derived until 20.15
  pins them; a contract whose anchor or number cannot be re-verified carries verify-then-fix
  as its first DoD step.
- **Nothing records before 20.35.** Waves 0–1 and the lever tasks are $0/offline; replay
  bytes never move; `bash scripts/verify_samples.sh` stays green through every merge. The
  smoke (20.35) records into a scratch directory; only 20.36 writes committed sets.
- **OFF-path byte-identity is a DoD item, not a hope.** Every lever task pins it (the
  prompt byte-golden over 204 committed meetings + `verify_samples.sh` + a render/detector
  fixture), and every lever ships a perturbation showing its ON-path bites.
- **Counterfactual before record.** Every detector/render lever pins its own committed-bytes
  counterfactual; 20.34 assembles them into one published prediction with one command.
- **Records get additive, dated errata; living docs are rewritten.** Close audits and
  campaign reports gain errata (20.13's comparator note); README/docs are rewritten.
- **Generated facts beat copied facts.** Every number a contract writes into prose is
  recomputed from committed artifacts with its command in the PR; `scripts/check_doc_facts.py`
  grows with every new README number (20.6, 20.12, 20.13, 20.38).
- **Craft rules apply to this phase's own PRs** (AGENTS.md "Craft rules"): lead with intent
  in every docstring; every new gate ships a perturbation; graduated levers are deleted;
  no dialect on user-facing surfaces; blast-radius grep before scope.
- **Two prior owner rulings are superseded for the post-20 substrate, by name.** The
  2026-06-22 LONE-STRONG relaxation (`tasks/phase-13.md` Task 13.14: a single-witness
  `alibi_vs_sighting` MAY cross the gate) and the Task 18.9 endpoint-band exemption (a
  single-tick roll-call whereabouts contradicted by a sighting mints STRONG) are reversed by
  20.26's lever — on more evidence than adopted them (14.6% sole-flag precision; 70 of 79
  wrongful ejections). The supersession applies only with the lever ON; the committed
  baseline-6 bytes keep reconstructing under the rulings that recorded them.
- **The firewall's one sanctioned widening** is 20.29's confirm-ejects rule: the role of an
  EJECTED player enters memory after its meeting, never before, and never for a player who
  merely died — asserted by the entitlement-checking leak scanner (20.8) both ways.

## Pre-registration

`audits/audit-phase-20-preregistration.md` — **ratified by the owner's merge of Task 20.22's
PR, and from that merge the only normative statement of the bars, the instrument definitions,
the decision rule (ADOPT vs FINDING), the secondary band, the co-intervention (20.32), the
offline-counterfactual protocol and the record order.** 20.34 computes its OFF/ON table
against the memo's cells and 20.36 reads its verdict off the memo's §4 and §6 VERBATIM;
neither re-derives a target from this file, which carries an orientation summary and not a
second copy of the contract. The shape, for a reader who needs it here: eight primary bars
(the non-direct conviction cell, innocent ejections, false crew self-placement, sole-flag
convicting precision, grounded sighting side, fabricated completion lines, the adjacent-room
STRONG share, and pass/fail on each of the four 19.11 injustice fixtures), with the win split
and the 20.14 solvability y-axis observed and reported but never gated, and the record order
samples/9p2i → ml_corpus/9p2i → samples/4p1i → ml_corpus/4p1i.

Every baseline cell in the ratified memo is quoted from a committed pin — `eval/solvability.py`
(20.14), `eval/evidence_honesty.py` (20.15), `eval/deduction_metrics.py` (19.14) and the four
19.11 injustice fixtures — so a stranger can re-run every "before" the phase is judged against.
Where a pin disagrees with the 2026-08-19 review's figure the memo keeps both numbers, marks
the pin authoritative and names the cause (§3.2), and the bar's TARGET does not move with it —
false crew self-placement re-anchors from 20.5% to 21.0% while its `< 5%` target is unchanged.
Any contract or generated prompt still quoting a superseded review figure is re-anchored to the
memo at its pre-dispatch review, never treated as a second baseline. And no bar may be
re-priced after that merge: a miss is reported as a miss, and any later change is a dated
erratum in the memo's amendment log.

## The DAG

```
Wave 0 — the front door and the demo's defects (RR-free; the day-one frontier):
  20.1 (map body layer)  20.2 (spectator copy)  20.4 (loader resilience)
  20.5 (prompt-set notice)  20.6 (vote_correctness truth)
  20.2 -> 20.3 (dock + focus)        20.2 -> 20.7 (Pages demo)

Wave 1 — claims made true, the instruments, readability (RR-free):
  20.9 (import contracts) -> 20.8 (leak scanner entitlement)
  20.10 (truncation gate)  20.11 (in-vent guards)  20.17 (gate hermeticity)  20.21 (recorder)
  (20.5, 20.6, 20.7, 20.8, 20.9) -> 20.12 (front door) -> 20.13 (results page) -> 20.20 (architecture exhibit)
  20.14 (solvability) -> 20.15 (honesty instruments) -> 20.22 (THE PRE-REGISTRATION, owner)
  (20.1, 20.2, 20.4, 20.7) -> 20.16 (DTO action fidelity)
  (20.9, 20.17) -> 20.18 (xdist)      20.5 -> 20.19 (byte-identical speed-ups)

Wave 2 — the evidence-honesty substrate (levers default-OFF; ONE record):
  (20.15, 20.22) -> 20.23 (completion from events) -> 20.24 (self-location trail)
  (20.15, 20.24) -> 20.25 (movement shape) -> 20.26 (grounded prosecution) -> 20.27 (map-aware arbitration)
  (20.16, 20.25, 20.26) -> 20.28 (structured turn markers)
  (20.8, 20.24, 20.28) -> 20.29 (meeting-outcome memory) -> 20.30 (coalesced render; also after 20.19, 20.27)
  (20.19, 20.27, 20.29, 20.30) -> 20.31 (THE PROMPT-SET BUMP v4)
  (20.15, 20.22) -> 20.32 (impostor mover repair — the declared co-intervention)
  (20.21, 20.23 .. 20.31) -> 20.33 (stamp registration + recorder preflight)
  (20.22, 20.33) -> 20.34 (THE OFFLINE COUNTERFACTUAL) -> 20.35 (smoke, operator)
  (20.35 + every Wave-0/1 root that touches pinned tests: 20.6, 20.7, 20.8, 20.10, 20.11,
   20.12, 20.17, 20.18, 20.32) -> 20.36 (THE ADOPTING RECORD: baseline 7, operator ~23 h)

Wave 3 — presentation on corrected bytes:
  20.36 -> 20.37 (graduation sweep: retire means delete)
  (20.13, 20.20, 20.36) -> 20.38 (results after the record) -> 20.39 (hero media; also after 20.1, 20.3)
  20.39 -> 20.40 (lessons + the curated review) -> 20.41 (tail truth)
  (20.6, 20.10, 20.11, 20.17, 20.18, 20.37, 20.39, 20.40, 20.41) -> 20.42 THE PHASE CLOSE [OWNER]
```

Critical path (20 tasks): 20.14 → 20.15 → 20.22 → 20.23 → 20.24 → 20.25 → 20.26 → 20.28 → 20.29 →
20.30 → 20.31 → 20.33 → 20.34 → 20.35 → 20.36 → 20.38 → 20.39 → 20.40 → 20.41 → 20.42.
The instrument pair (20.14 → 20.15) and the owner's pre-registration (20.22) head it —
no lever merges before the bars are ratified; dispatch 20.14 on day one beside the Wave-0
roots. The day-one frontier is eleven roots (20.1, 20.2, 20.4, 20.5, 20.6, 20.9, 20.10,
20.11, 20.14, 20.17, 20.21). Nothing waits on the owner until 20.22 (the pre-registration),
then 20.35/20.36 (the operator record) and 20.42 (the close).

**Baseline numbering.** One record: baseline 7 at 20.36, the first adopting record since
baseline 6 (the mover record the post-14 plan once reserved the number for never landed; the
number is free). Under the pre-registered decision rule the record is either ADOPTED (the
levers graduate; the ladder tip moves to 7) or a FINDING record (the levers stay toggles; the
tip stays at 6; the bytes and the memo are committed either way). No other task records.

**Collision discipline** (dep-ordered; the validator enforces every shared file has an
edge): `README.md` 20.12 → 20.13 → 20.20 → 20.38 → 20.39 → 20.40 → 20.41 → 20.42 (status
line); `agents/memory/store.py` 20.23 → 20.24 → 20.29 → 20.30; `meetings/transcript.py`
20.25 → 20.26 → 20.27; `meetings/manager.py` 20.26 → 20.28 → 20.29; `meetings/schemas.py`
20.25 → 20.28; `meetings/render_contract.py` 20.25 → 20.31; `agents/strategic/prompts/loader.py`
20.5 → 20.19 → 20.31; `orchestrator/game.py` 20.29 → 20.31 → 20.36; `orchestrator/replay.py`
20.33 → 20.36 → 20.37; `api/replay_loader.py` 20.4 → 20.16 → 20.28 → 20.33; `api/schemas.py`
20.16 → 20.28; `eval/leak_scan.py` + `eval/leak_test.py` 20.8 → 20.29; `tests/test_firewall.py`
20.9 → 20.8; `frontend/src/components/TournamentDashboard.tsx` 20.2 → 20.7 → 20.16;
`MapView.tsx` 20.1 → 20.16; `ReplayControls.tsx` 20.2 → 20.3; `ReplayPicker.tsx` 20.2 → 20.36;
`scripts/check_doc_facts.py` 20.6 → 20.12 → 20.38; `scripts/measure_baseline.py` 20.14 → 20.15;
`scripts/refresh_samples.sh` 20.21 → 20.33; `scripts/record_ml_corpus.sh` 20.33 → 20.36;
`tests/eval/test_evidence_honesty.py` 20.15 → 20.23 → 20.24 → 20.25 → 20.26 → 20.27 → 20.30 →
20.31; `tests/agents/test_memory_rendering.py` 20.23 → 20.24 → 20.30;
`tests/meetings/test_contradictions.py` 20.25 → 20.26 → 20.27; `tests/meetings/test_prompt_byte_golden.py`
20.31 → 20.36; `pyproject.toml` + `tests/conftest.py` 20.17 → 20.18; `.env.example` 20.5 →
20.33 → 20.37; `AGENTS.md` 20.5 → 20.37; `docs/*` per the README chain; `tasks/phase-20.md`
20.22 → 20.42; the committed test directories `tests/eval/`, `tests/agents/`, `tests/meetings/`,
`tests/api/`, `tests/scripts/`, `tests/training/` as whole-directory re-pin scopes at 20.36
only (every Wave-0/1 task that edits a file there precedes 20.36 by an explicit edge).

**Model assignments** (the standing rule: Opus for loud-failure work — mechanical fixes,
scaffolding, deletions with consumer greps, generated docs, build/CI; Fable for
silent-failure work — evidence semantics, metric definitions, prompt wording, memory render
truth, the pre-registration and the record reads):
Fable — 20.6, 20.8, 20.12, 20.13, 20.14, 20.15, 20.22, 20.23, 20.24, 20.25, 20.26, 20.27,
20.29, 20.30, 20.31, 20.34, 20.38, 20.40, 20.42. Opus — 20.1, 20.2, 20.3, 20.4, 20.5, 20.7,
20.9, 20.10, 20.11, 20.16, 20.17, 20.18, 20.19, 20.20, 20.21, 20.28, 20.32, 20.33, 20.35,
20.36, 20.37, 20.39, 20.41. The owner may dispatch any task on Opus; the split names where
silent failure is the risk.

**Operator/owner gates.** 20.7 (a five-minute GitHub settings step after the workflow
lands); 20.22 (the pre-registration ratification); 20.35 (the smoke, ~1 h operator); 20.36
(the record, ~23 h operator wall, $0 at the flat-rate provider, checkpoint-pushed); 20.41
(commit-vs-de-scope the finalist raw slate); 20.42 (the close). Everything else is
dispatchable agent work at $0.

---

## Wave 0 — the front door and the demo's defects (RR-free; the day-one frontier)

### Task 20.1 — The map body layer reads engine truth (TickView.bodies) + the first MapView derivation test
**Branch:** `phase-20-map-body-layer`
**Depends on:** none (root)
**Section refs:** C-7 / G-38 (body half) / C-80 / C-101 — audits/review-2026-08-19/B/frontend-a.md §2 F1 (the phantom-corpse census), §2 F7 (no component-level tests, by configuration), §2 F8 (the derivations trapped in `.tsx`), §2 F11 (`TickView.bodies` served to no consumer); audits/review-2026-08-19/B/collated-findings.md rows C-7 and C-80; audits/review-2026-08-19/A/collated-findings.md §G-38; audits/review-2026-08-19/A/ux-visual-pass-lead.md bullet 6 (seed 2 t29: four corpses drawn, one in state); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 0.2; audits/review-2026-08-19/D/cross-track-map.md rows G-6 and G-38; design/phase-12/stage-1-design.md:83 (the body layer was specified to source from `state.bodies`). Anchors re-verified at HEAD `b809b19c`: frontend/src/components/MapView.tsx:85-92 (`BodySpec` / `NO_BODIES`), :226-264 (`buildBodyStatesByTick`), :569-572 (the `useMemo`), :590-591 (`bodyIndex` / `omniscientBodies`), :733-744 (`bodySpecs`; the fog branch already reads `visibility.visible_bodies`), :749-798 (`bodiesByRoom` + the `BODY_CAP` / `bodiesFit` collapse); frontend/src/components/BodyMarker.tsx:13-18 (the two-state truth grammar), :36-38 (the `TickView.bodies[].killed_by` provenance comment), :47 (`BODY_CAP = 3`), :60 (`bodiesFit`), :125 ("Outer kill ring marks a freshly reported body"); orchestrator/game.py:1247-1259 (the corpse consumption at meeting resolution); api/replay_loader.py:2568-2580 (`_bodies_view`); api/schemas.py:345-361 (`BodyView` — no `discovered` field is served), :457-461 (`TickView.bodies`); engine/tick.py:439 (`discovered_by` is written by the report action and nothing else); frontend/vitest.config.ts:10-25 (`environment: "node"` as a stated contract); frontend/tsconfig.json (`resolveJsonModule`, `include: ["src"]`).
**Complexity:** Medium
**Record impact:** none
**Measurement:** `cd frontend && npm run test` green including the new `src/lib/bodies.test.ts`, whose phantom-frame count over the 50 committed `replays/samples/9p2i` served payloads reads 0 while the same walk over the retired accumulate rule reads 1,182 of 1,769 (the gate can fail); `npm run tsc:check`, `npm run lint` and `npm run build` green; `bash scripts/check.sh` green.

The map is the demo's central surface and it is wrong on two thirds of its frames.
`buildBodyStatesByTick` (MapView.tsx:229-264) builds the Omniscient body layer by
*accumulating* `kill` events and never removing anything — a `report_body` only flips
`isDiscovered`. But `orchestrator/game.py:1256-1259` deletes the reported corpse from
`WorldState.bodies` when the body-report meeting resolves, and the served DTO reflects
that exactly: `api/replay_loader.py:2568 _bodies_view` projects the bodies still on the
floor, with the privileged `killed_by`. MapView never reads it. Re-derived at HEAD
`b809b19c` over all 50 committed `replays/samples/9p2i` games (reproducing the review's
probe: audits/review-2026-08-19/B/frontend-a.md §2 F1): 1,182 of 1,769 frames (66.8 %)
paint at least one corpse the engine has already consumed, in 50 of 50 games, 2,426
phantom body instances, `missingFrames: 0`, `phantomWithoutReport: 0` — every phantom is
a consumed corpse, none is unexplained. Named instances, both re-confirmed:
`headless-seed-0` tick 18 serves `[]` and the map draws `["p-2"]`; `headless-seed-2`
tick 29 serves `["p-5"]` and the map draws `["p-1","p-2","p-5","p-6"]` (the UX lead's
"FOUR corpses while the engine state has one",
audits/review-2026-08-19/A/ux-visual-pass-lead.md bullet 6). The As-agent path is
already correct (MapView.tsx:738-744 reads `visibility.visible_bodies`), so Omniscient
and fog disagree about whether a body is on the floor — which reads to a viewer as a fog
artefact rather than as the bug it is.

The error is not only cosmetic. Phantoms are drawn with `BodyMarker`'s *discovered*
treatment, whose own comment (BodyMarker.tsx:125) calls the outer ring "a freshly
reported body" — so a corpse reported at tick 12 still wears the freshly-reported ring
at tick 60. They corrupt the per-room layout downstream: re-derived at HEAD, all 1,182
frames carry an inflated per-room body count, and on 4 frames a room's accumulated pile
exceeds `BODY_CAP = 3` while no served room does, firing a spurious "✕ ×N" collapse
marker over a room that holds nothing. And the served `killed_by` field — built for
exactly this layer, cited as its source at BodyMarker.tsx:36-38 — is dead, because
MapView re-derives the killer from the kill event instead (MapView.tsx:258). The file
header calls this layer "Omniscient ground truth" (MapView.tsx:226-227); the Phase-12
design specified sourcing it from `state.bodies` (design/phase-12/stage-1-design.md:83).
This is doc-vs-code drift and a wrong render on the default perspective of the app the
portfolio track calls the star-making asset.

The second half of the task is why nobody caught it. MapView's pure derivations live
inside a `.tsx` the node-only vitest project cannot import — `MapView.tsx:28-29`
pulls `@pixi/react` / `pixi.js` at module scope (C-80;
audits/review-2026-08-19/B/frontend-a.md §2 F8: "which is precisely why F1 went
unnoticed"), and no component RENDER test exists, by configuration (C-101; §2 F7 — the two
suites under `src/components`, `EventTicker.test.ts` and `CostChips.test.ts`, pin
exported pure projections, never a render).
`frontend/src/lib/` already holds the playback derivations and is the established home
for exactly this kind of code. Moving the body derivation there and pinning it against
the committed served bytes is what turns this class of defect into a caught regression
rather than a review finding — and it is the first brick of the `lib/` layer the review
asks for, without attempting the whole `lib/mapDerivations.ts` split (the other four
derivations stay where they are; this task moves one concern, not a file).

Three invariants the fix must preserve. First, the fog path: `visibility.visible_bodies`
continues to drive the As-agent layer with `isDiscovered: false` and `killedBy: null`
(the firewall — `VisibleBodyView` carries no killer), and that mapping becomes pinned
rather than merely asserted in a comment. Second, discovery: no `discovered` flag is
served (api/schemas.py:345-361 — `BodyView` carries `body_id` / `victim_id` / `room_id`
/ `killed_by` only), so `isDiscovered` stays derived from `report_body` events
accumulated forward; `engine/tick.py:439` shows `discovered_by` is written by the report
action alone, so the derivation and the engine agree by construction. Third, presence: a
body leaves the map on the frame the engine consumes it, and a body that is reported but
*not* consumed (only the meeting's triggering corpse is deleted) keeps rendering with
the discovered treatment. Re-derived at HEAD over `samples/9p2i`: 151 `report_body`
events, each of whose bodies is served on exactly one frame — its own report frame — and
none after; `samples/4p1i` reads 35/35 the same way. So after the fix the "freshly
reported" ring is literally true on the committed sets, which is the honest version of
the semantics BodyMarker already documents.

The DTO is correct and is not touched: no `api/schemas.py` change, no `viewModelVersion`
bump, no re-record. This task is RR-free and moves no committed bytes.

**Files in scope:**
- frontend/src/components/MapView.tsx; (the body layer reads `tick.bodies`; the pure derivations move out)
- frontend/src/lib/bodies.ts; (new: the pure body-layer derivation, importable by vitest)
- frontend/src/lib/bodies.test.ts; (new: walks the committed sample replays' served payloads and asserts zero phantom frames)
- frontend/src/components/BodyMarker.tsx; (the "freshly reported" ring semantics only if the reported body is still served)
- frontend/src/lib/bodies.fixture.json; (new: the committed dump of the 50 served samples/9p2i payloads the test walks — tick.bodies exists only after the Python loader's engine re-walk)

**Files NOT in scope:**
- api/ (the served `TickView.bodies` is already correct; no DTO field, no schema change, no `viewModelVersion` bump — a `discovered` flag on `BodyView` would be a DTO change and is explicitly refused here)
- frontend/src/components/AgentToken.tsx (the action glyphs and the `CurrentAction` enum belong to the DTO-fidelity task later in this phase)
- frontend/src/components/TournamentDashboard.tsx, MeetingView.tsx, ReplayPicker.tsx, ReplayControls.tsx (the product-copy pass owns those surfaces)
- frontend/src/App.tsx, frontend/src/hooks/, frontend/e2e/ (the dock/focus-trap task owns the layout and the Playwright journey)
- frontend/src/components/EventTicker.tsx (its comments at :245 and :548 name `buildBodyStatesByTick` as the Task-6.7 memo precedent — prose about a pattern, not a call site; the DoD's deletion leaves them naming a symbol that has moved to `lib/bodies.ts` as `bodyStatesByTick`. Leave them, or raise a comment-only refresh under Questions)
- frontend/vitest.config.ts (its `include: ["src/**/*.test.ts", "src/**/*.test.tsx"]` glob already picks the new suite up and `environment: "node"` is the right contract for a pure derivation; its header's enumeration of suites is illustrative — if the reviewer wants it refreshed, raise it under Questions rather than widening scope)
- MapView's other four pure derivations — `computeTransform`, `buildVentEdges`, `buildVentSegments`, `normalizeRoomKey` (the full `lib/mapDerivations.ts` split is a separate concern; this task moves the body layer only)
- replays/, orchestrator/, engine/ (the engine is correct — the corpse consumption at `orchestrator/game.py:1247-1259` is the truth this task starts obeying, not a defect)

**Definition of done:**
- [ ] `frontend/src/lib/bodies.ts` exists and owns the body-layer derivation as pure, importable functions: presence for the Omniscient layer comes from `tick.bodies` alone, `killedBy` is read from the served `tick.bodies[].killed_by` (the dead field revived — no re-derivation from the kill event), and `isDiscovered` is the forward-accumulated `report_body` set. The fog mapping from `AgentVisibilityView.visible_bodies` moves into the same module with `isDiscovered: false` / `killedBy: null` unchanged. `BodySpec` is exported from `lib/bodies.ts`; `buildBodyStatesByTick`, `BodySpec` and `NO_BODIES` are DELETED from `MapView.tsx` (retire means delete — no wrapper left behind), and `MapView.tsx` consumes the new module at the `useMemo` (:569-572) and at the `bodySpecs` branch (:733-744).
- [ ] `frontend/src/lib/bodies.test.ts` walks the served payloads of all 50 committed `replays/samples/9p2i` replays from a committed fixture and asserts the phantom-frame count is 0 — a phantom frame being one where the derivation renders a body absent from that tick's `tick.bodies`. The same walk over the retired accumulate rule, re-implemented inside the test as the perturbation leg, reads 1,182 phantom frames of 1,769 total across 50/50 games (2,426 phantom body instances), so the gate demonstrably bites; `missingFrames` is 0 on both legs.
- [ ] The `BODY_CAP` / `bodiesFit` collapse no longer fires on a phantom pile: pinned by the same walk, no frame has a room whose derived body count exceeds `BODY_CAP` while the served state has no such room (the retired rule produces 4 such frames; the scale-dependent `bodiesFit` half stays in `MapView.tsx` and is not re-implemented in `lib/`). Per-room served counts are asserted equal to per-room derived counts on every frame (the retired rule inflates 1,182 of them).
- [ ] Discovery semantics are pinned: over `samples/9p2i` exactly 151 frames carry a discovered body — one per `report_body` event, on the report frame itself — and none afterwards; a hand-built fixture covers the reported-but-unconsumed case (a body with a `report_body` event that is still present in a later tick's `tick.bodies` keeps the discovered treatment) and the unreported case (ghosted), so the rule holds independently of whether the committed sets happen to exercise it.
- [ ] The As-agent path is unchanged and pinned: a hand-built fixture asserts the fog mapping's output is byte-identical to today's — one `BodySpec` per `visible_bodies` entry, `isDiscovered: false`, `killedBy: null` — and that no served `tick.bodies` entry can reach the fog layer.
- [ ] `frontend/src/components/BodyMarker.tsx` states the true semantics: the outer kill ring marks a body reported and still on the floor, and the header's two-state grammar names `tick.bodies` as the presence source. Comment/prop-doc lines only — no rendering behaviour changes, no props added or removed (`BODY_CAP`, `bodiesFit`, `collapsedCount`, `killedBy` all keep their signatures). Provenance is at most one trailing line per docstring.
- [ ] `cd frontend && npm run test`, `npm run lint`, `npm run tsc:check` and `npm run build` all pass; the PR quotes the before/after phantom census (1,182/1,769 → 0/1,769).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — verify before editing. Re-run the census yourself so the PR's before-number is
yours, not inherited: load each `replays/samples/9p2i` replay through
`api.replay_loader.ReplayLoader` (50 games, ~1.5 s total on this HEAD), re-implement
`buildBodyStatesByTick` in a throwaway Python script, and diff its per-tick victim set
against `{b.victim_id for b in tick.bodies}`. Expect exactly `totalFrames 1769,
phantomFrames 1182, missingFrames 0, gamesWithPhantom 50/50, phantomBodyInstances 2426`.
If any of those differ at your HEAD, stop and report it under Questions before writing
code — the contract's numbers are the bar.

Step 2 — the module. Two exports carry the Omniscient layer and one carries the fog
layer. A per-frame function — roughly
`bodiesForTick(tick, reportedVictimIds): BodySpec[]` — maps each `tick.bodies[]` row to
victimId `body.victim_id`, roomId `body.room_id`, isDiscovered
`reportedVictimIds.has(body.victim_id)`, killedBy `body.killed_by`: presence and
attribution both straight from the served row, nothing accumulated. A whole-replay pass
— roughly `bodyStatesByTick(ticks): BodySpec[][]` — threads the `report_body` set
forward and calls the per-frame function, preserving MapView's existing `useMemo` shape
so the call site at :569-572 is a one-line change and the `bodyIndex` clamp at :590
stays as it is. A third — roughly `visibleBodiesForTick(visibility): BodySpec[]` — is
the relocated fog mapping. Keep the sort, the `bodiesByRoom` grouping and the
`BODY_CAP` / `bodiesFit` collapse in `MapView.tsx`: they need `scale`, which is render
state, and a pure module should not take it.

Step 3 — the fixture. The committed replays are action-only
(`replays/samples/9p2i/replay-seed-0.jsonl` rows are
`{"actions":[…],"kind":"tick","state_hash":…}`), so `tick.bodies` exists only after the
Python loader's engine re-walk; the TypeScript test cannot derive it and must not try —
re-deriving engine state in the frontend is the exact mistake this task is undoing.
Commit a compact dump instead: per game, the tick index, the sorted served victim ids,
and the `kill` / `report_body` events. Minified that is about 72 KB for the whole 9p2i
set — smaller than several files already tracked under `frontend/` — and it is stable,
because `replays/` bytes never move. Generate it once with a short `uv run python`
snippet over `ReplayLoader`, record that exact command in the test file's header comment
so the fixture is re-derivable, and read it with `readFileSync` + `JSON.parse` rather
than a JSON `import`: `frontend/tsconfig.json` sets `resolveJsonModule` and includes
`src`, so importing a 72 KB literal would push a large inferred type through
`tsc --noEmit` for no benefit. `frontend/src/tokens.test.ts` is the precedent for reading a
real file off disk under `environment: "node"`. Parse the fixture through a narrow,
explicitly-typed reader function so `noUncheckedIndexedAccess` and
`exactOptionalPropertyTypes` stay honest.

Step 4 — the perturbation leg. The zero-phantom assertion is close to true by
construction once presence comes from `tick.bodies`, so on its own it is a gate nobody
can fail. Put the retired accumulate rule in the test file as a named reference
implementation, run the same walk over it, and assert it reads 1,182 — the test then
proves both that the new derivation is right and that the walk can tell them apart.
Optionally extend the fixture to `samples/4p1i` as a second set (adds ~28 KB; re-derived
at HEAD it reads 101 phantom frames of 682 across 25 of 50 games) — useful, not
required.

Step 5 — blast radius. Before deleting anything, run
`grep -rn 'BodySpec\|NO_BODIES\|buildBodyStatesByTick\|visible_bodies' frontend/src`;
at HEAD the only CODE hits are inside `MapView.tsx` plus the `types/api.ts`
declaration, so the deletion is contained; the rest are inert — two comments in
`EventTicker.tsx` (:245, :548) naming `buildBodyStatesByTick` as the Task-6.7 memo
precedent, and `visible_bodies` fixture data in `types/api.fidelity.ts`,
`stories/MapStage.stories.tsx` and `EventTicker.test.ts`. If a NEW code hit appears
outside the files in scope, stop and report it rather than widening scope.

**Ready-to-paste prompt:** `agent_prompts/task-20-1-map-body-layer.md`

### Task 20.2 — Product copy: the audit dialect leaves the spectator surface
**Branch:** `phase-20-spectator-copy`
**Depends on:** none (root)
**Section refs:** G-41 and G-37 (`audits/review-2026-08-19/A/collated-findings.md` §D — "Spectator UI: internal jargon and layout on the product surface" and "Agent tick stamps are +1 vs the replay timeline"); `audits/review-2026-08-19/A/ux-visual-pass-lead.md` (the picker-legend line, the CORRECT-badge spoiler line, the Tournament-tab dialect line); `audits/review-2026-08-19/C/p3-frontend-product-engineer.md` §3 weakest-3 item 3, §4 "Hurt", §7 GOOD 6 and GOOD 9; `audits/review-2026-08-19/C/collated-portfolio.md` B6; `audits/review-2026-08-19/D/FINAL-synthesis.md` §4 wave-0 row 0.3, §2 row 12 (C-113 [D-VERIFIED]), §4 wave-2 row 2.14 (the clock re-stamp — NOT scheduled in Phase 20); `audits/audit-phase-20-planning.md` §3 (wave 0); AGENTS.md:95-98 (craft rule 4, no internal dialect on user-facing surfaces) and :99-102 (rule 5, verifiable-shaped claims). Anchors re-verified at HEAD `b809b19c` (with the planning PR in the working tree): `frontend/src/components/TournamentDashboard.tsx`:188, :241, :251-253, :299, :320, :324-326, :338, :366, :518, :703, :838, :935; `MeetingView.tsx`:224, :233, :524-549, :672-682; `BallotCard.tsx`:30-35, :100-105, :131, :145-150, :166-178; `ReplayPicker.tsx`:373-387, :421-427, :456, :457, :509-542; `HighlightCard.tsx`:54-59, :102-104, :119, :175-197; `ReplayControls.tsx`:603-614; `MetricCaveat.tsx`:1-12. Also in scope, and the boundary this measures: `TurnCard.tsx`:291 is the ONLY user-facing dialect string in `frontend/src` outside this task's seven core files. The clock seam is `orchestrator/game.py`:1778 (packets built), :1785-1786 (`input_tick` then `advance_tick`), :1794 (`record_tick(input_tick, …)`) — the review's ":1778-1793" is one line short at HEAD. The metric truth is `eval/vote_correctness.py`:11-25 ("structurally pinned to 1.0") against `replays/samples/9p2i/tournament-eval-report.json` → `vote_correctness.vote_correctness_rate` = 0.9230769230769231 (72 evidence-backed of 78 impostor ejections). Test-runner facts: `frontend/vitest.config.ts` (`environment: "node"`, `include: src/**/*.test.ts(x)`) and `frontend/src/components/CostChips.test.ts`:12-14 (an existing node-env `.test.ts` importing a `.tsx` — the precedent this task reuses).
**Complexity:** Small
**Record impact:** none — display copy and one display gate only; no engine, prompt-template, DTO or detector byte moves, so nothing here waits on the Phase-20 adopting record.
**Measurement:** `cd frontend && npm run test && npm run lint && npm run tsc:check` green (including the new `src/lib/copy.test.ts`, whose perturbation leg proves the dialect matcher bites); `grep -rnE 'DESIGN\.md §|Task [0-9]+\.[0-9]+|audits/|sentinel|KPI' frontend/src` returns hits only on source-comment lines, never on a rendered string.

The spectator is the project's best asset and its copy is written in a private
dialect. Every reviewer who opened the Tournament tab hit it: card subtitles carrying
"(DESIGN.md §11.3)" (TournamentDashboard.tsx:188, :935), "(Task 9.6 / 10.x; typed on
the wire by 12.2.)" (:299), "(Task 19.14; audits/audit-phase-19-triage.md §7 item 15)"
(:518), "(Task 10.4), re-anchored by 19.5 … the Task-17.6 successor" (:366), and
caveat chips reading "sentinel — not a KPI" (:253) and "sentinel — read the split"
(:326) over hint strings like `imp-voter 91 · invalid 1 · inversion 87` (:320). The
meeting dialog's Resolution card labels its verdict "§4.6" twice (MeetingView.tsx:224,
:233). The reviewer's summary of the whole viewer was that its two real problems are
the corpse bug and the internal jargon in copy (`A/ux-visual-pass-lead.md`), and the
portfolio track independently made "strip audit/task citations from user-facing text"
its B6. AGENTS.md's craft rule 4 now makes this binding for every PR from Phase 20 on;
this contract is that rule executed on the surface the rule was written for.

Three of the strings are not merely opaque — they are false or spoiling. The
vote-correctness section (TournamentDashboard.tsx:241, :251) tells a visitor the rate
is "pinned to 1.0 by construction" and that "Below 1.0 means a detector/recording bug
to chase", while the committed report the tile renders reads 0.9230769230769231 — 72
evidence-backed of 78 impostor ejections in
`replays/samples/9p2i/tournament-eval-report.json`. The dashboard therefore
contradicts its own number on screen, in the one place a sceptical reader is looking
for honesty ([D-VERIFIED], `D/FINAL-synthesis.md` §2 row 12; the README leg of that
finding is refuted and no README edit belongs here). Separately, the ballot
CORRECT/INCORRECT badge (BallotCard.tsx:166-178) renders on role ground truth whenever
the perspective is Omniscient, including while the spectator has outcomes hidden — a
viewer who deliberately chose the unspoiled mode is told, per ballot, who the
impostors were.

That badge is a deliberate decision being revisited, not an oversight, and the
contract records the reversal rather than silently flipping it: BallotCard.tsx:30-35
states that the gating is "on PERSPECTIVE alone, deliberately never on
`revealOutcome`", on the reasoning that reveal governs outcome information and
perspective governs what the current frame may know. The ruling here: a per-ballot
correctness mark is outcome information for a first-time viewer — it names the
impostors before the game names them — so it is gated on Omniscient AND the reveal,
and the module comment is rewritten to say that, with the superseded reasoning kept as
one history line. The narrower firewall rule the same file enforces (role-disclosing
rewrite chips and the coerced-rationale body suppressed under fog,
`visibleRewriteReasons` / `visibleRationale` at :68-98) is untouched: reveal must
never WIDEN what fog hides, and it does not here.

Two smaller truths ride along. The rubric bars R1/R2/R3/R7 (HighlightCard.tsx:54-59,
:175-197) render as bare keys with their words available only in a hover title, and
the header legend that spells them out exists only on the Highlights tab
(ReplayPicker.tsx:456) — so the Replays tab, which is where the picker opens, shows
four unlabelled bars. And the set names "9p2i" / "4p1i" are never expanded anywhere on
the surface, including in the set selector (ReplayPicker.tsx:509-542) that is the
first control a visitor touches. Finally the two-clock seam (G-37): agent-facing
observation stamps are one ahead of the replay timeline the transport scrubs —
111,283/111,283 memory sighting lines match world truth at Δ=−1 and only 51.8% at Δ=0
(`A/s3-meeting-decisions.md`), while the meeting header's "It is tick N" matches the
replay tick exactly in 771/771 calls (`A/s2-movement-positions.md`) — because the
packet is built at `orchestrator/game.py`:1778 before `advance_tick` at :1786 and
recorded against the pre-advance `input_tick` at :1794. Every one of the review's
eight watchers opened by hand-deriving that convention. The engine-side resolution
(re-stamp or assert) is `D/FINAL-synthesis.md` §4 row 2.14 and is NOT scheduled in
Phase 20, so this task ships the honest label only: a one-line note beside the tick
readout that states the convention truthfully, and that a later re-stamp would delete.

**Files in scope:**
- frontend/src/components/TournamentDashboard.tsx; (copy + tooltips only — every tile value, ordering and layout byte-identical)
- frontend/src/components/MeetingView.tsx; (the §-citation copy on the Resolution card; threading the reveal state to the ballots panel)
- frontend/src/components/BallotCard.tsx; (the CORRECT/INCORRECT badge gated on the outcome-reveal state; the module comment records the reversed ruling)
- frontend/src/components/ReplayPicker.tsx; (the rubric legend on both tabs + set-name expansion in the selector and the empty states)
- frontend/src/components/HighlightCard.tsx; (the sub-score bars carry their words, not only a hover title)
- frontend/src/components/MetricCaveat.tsx; (the caveat component's own "sentinel notes" doc wording; no rendered string lives here — if the file needs no change after the call sites are rewritten, the PR says so)
- frontend/src/components/ReplayControls.tsx; (the agent-clock note beside the tick readout)
- frontend/src/lib/copy.ts; (new: the user-facing copy tables + the pure expandSetName / dialectHits / badge-gate helpers)
- frontend/src/lib/copy.test.ts; (new: the dialect gate with its perturbation leg, the legend/set-expansion pins, the badge-gate combinations)
- frontend/src/components/TurnCard.tsx; (the one dialect string at :291 — copy only)

**Files NOT in scope:**
- frontend/src/components/MapView.tsx and BodyMarker.tsx (the body-layer task owns the map this wave)
- frontend/src/hooks/useFocusTrap.ts, frontend/src/components/GuidedTour.tsx, frontend/src/App.tsx (the dock-and-focus task owns layout and the overlay stack; it lands after this one)
- everything in frontend/src/components/TurnCard.tsx except the :291 tooltip string (the structured-turn-markers task owns this file's chips and markers in wave 2; this task rewrites that one tooltip's wording and nothing else, and lands well ahead of it — 20.28 depends on 20.16, which depends on this task, so the shared file is dep-ordered)
- api/, api/schemas.py and the generated `frontend/src/types/` (no data, DTO or view-model-version change; the action-fidelity task owns the DTO)
- eval/vote_correctness.py (the vote-correctness-truth task owns the docstring and the doc-fact pin; coordinate the WORDING of what the metric measures, never the file)
- agents/strategic/prompts/ and every prompt template (no task in this phase edits a game prompt except the single prompt-set bump)
- replays/ and any recorded byte (nothing re-records)
- frontend/src/stories/ (the stories already drive `revealOutcome` through the store at MeetingView.stories.tsx:421-447 and :484-524, so they need no edit; if one breaks, fix the component, not the story)

**Definition of done:**
- [ ] Every user-facing string on the eight surfaces lives as a value in one new `frontend/src/lib/copy.ts` module (plain `.ts`, no JSX, importable by the node-env vitest project) and NONE of those values matches the dialect matcher: a `DESIGN.md §…` citation, a bare `§N.N` section reference, a `Task N.M` reference, an `audits/…` path, or the words "sentinel" / "KPI". Every rendered string named in Section refs (the fourteen on the dashboard, including the §5.4 alibi-survival description at :703, and the two on the Resolution card) is rewritten in plain English that keeps the substance (what the number counts, what its denominator is, what a caveat warns about) and drops the pointer.
- [ ] `frontend/src/lib/copy.test.ts` pins it two ways and can fail: it asserts the matcher flags a deliberately dialect-bearing fixture string (the perturbation leg, craft rule 2), then asserts every exported copy value is clean, then reads the eight in-scope `.tsx` files off disk with `//`, `/* */` and `{/* */}` comments stripped and asserts zero dialect hits in what remains. The disk leg ships with an EMPTY allow-list — `TurnCard.tsx` included, every in-scope surface must come back clean — and the test states that in one line, so any future allow-list entry is a deliberate act.
- [ ] The rubric bars carry their words wherever they render: `HighlightCard.tsx`'s `SubScoreBar` labels each spoke with its meaning (not only in the hover `title` at :183), and the Replays tab header carries the same R1/R2/R3/R7 legend the Highlights header carries at `ReplayPicker.tsx`:456 — pinned by a vitest assertion over the exported legend table. The other half of that same ternary, the Replays-tab sentence at :457 ("Every recorded replay in the served set."), stops asserting a completeness this build cannot honour — the static demo bundle serves a subset (the reviewer measured 4 of 50 in bundle mode, `C/p3-frontend-product-engineer.md` §4 "Hurt" and §7 GOOD 9) — and becomes a sentence that is true in BOTH live and bundle mode without reading a build flag (`STATIC_DATA_MODE` is module-private to `frontend/src/api/client.ts`, which this task does not edit); the new value is pinned in `copy.test.ts`.
- [ ] Set ids are expanded once per surface: a pure `expandSetName` helper in `frontend/src/lib/copy.ts` maps `9p2i` → "9 players, 2 impostors" and `4p1i` → "4 players, 1 impostor", falls back to the raw id for any unrecognised set (the selector's options come from `/sets` and grow), and is used by the `SetSelector` options (`ReplayPicker.tsx`:509-542) and by the first mention in the picker's empty states (:373-387, :421-427). The three cases — both known ids and one unknown id — are pinned in `copy.test.ts`.
- [ ] The ballot CORRECT/INCORRECT badge renders only when the perspective is Omniscient AND the store's `revealOutcome` is true: `MeetingView` reads `revealOutcome` from `useReplayStore` and threads it through `BallotsPanel` (:524-549, :672-682) to `BallotCard`; the badge's gate is an exported pure predicate so `copy.test.ts` pins all four (omniscient × revealed) combinations with no DOM. `BallotCard.tsx`:30-35's comment is rewritten to state the new rule with one history line for the superseded one, and the fog-side rules (`visibleRewriteReasons`, `visibleRationale`) are unchanged and still pinned.
- [ ] The vote-correctness copy (`TournamentDashboard.tsx`:241, :251-253) states what the metric counts — the share of impostor ejections that carry a naming contradiction or a kill-witness chain on the record — says that it is a bug detector rather than a quality score in plain English (the words "sentinel" and "KPI" do not appear), and makes NO structural-1.0 claim; instead it says what a value below 1 means (an impostor ejection with no such evidence recorded against them) without asserting which cause applies. The tile keeps rendering the live value; no number is hard-coded into copy.
- [ ] A one-line agent-clock note sits beside the tick readout (`ReplayControls.tsx`:603-614): this timeline is the replay/engine clock, and an agent's own observation stamps read one ahead of it, with a tooltip saying that a memory line stamped tick N describes the map shown at N−1 while the meeting header's tick matches this readout. The note carries no measurement figures and no task or audit id; the corroborating counts live in the code comment and the test, not on screen.
- [ ] No layout, tile, value, ordering or aria-label semantic changes beyond the copy and the one badge gate; the PR quotes `git diff --stat` and the reviewer can see the dashboard's numbers are untouched.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — build the matcher before touching copy. Write `frontend/src/lib/copy.ts` with
an exported `DIALECT_PATTERNS` array and a `dialectHits(text: string): string[]`
helper, then write the perturbation assertion in `copy.test.ts` FIRST and watch it
pass on a fixture like "The §4.6 gate (Task 19.14; audits/audit-phase-19-triage.md §7
item 15) — a sentinel, not a KPI". A gate that has never flagged anything is prose.

Step 2 — inventory, then rewrite. Run the Measurement grep, widened with the bare
section-symbol alternative, over `frontend/src` at HEAD: it returns every rendered
string named in Section refs, plus `TurnCard.tsx:291`, plus source comments. That
output IS the work list. Move each rendered string into `copy.ts` as a named export
and import it back into the component, so the test can read the copy without a
renderer.
The vitest project is `environment: "node"` with no React plugin, so keep `copy.ts`
free of JSX; `CostChips.test.ts:12-14` shows a node-env `.test.ts` importing a `.tsx`
if you need a predicate that must live beside a component.

Step 3 — rewrite the substance, not just the pointer. "Did accusations convert into
impostor ejections, and were the SKIPs correct?" is already the good half of :299 —
delete only the parenthetical. `imp-voter 91 · invalid 1 · inversion 87` (:320)
becomes words for the same three buckets ("impostor voters", "invalid targets",
"declines at the line"). The threshold-inversion tooltip at :338 should say the crew
voter met the ejection reference and skipped anyway and that this is allowed, without
citing the task that made it allowed. "§4.6" on the Resolution card becomes "Vote
gate"; the readout sentence at :233 already explains the rule (plurality plus one
leader ballot at or above the threshold), so the section reference adds nothing.

Step 4 — the reveal gate. `revealOutcome` is already in the store
(`store/replayStore.ts`:198, :301, :684) and MeetingView already subscribes to store
state, so this is a prop thread, not new state. Export the rule as something like
`showsVoteCorrectness(omniscient: boolean, revealOutcome: boolean): boolean` so the
four combinations are unit-pinnable; the stories at `MeetingView.stories.tsx`:484-524
already set `revealOutcome` on the store and will render the new states without edits.

Step 5 — the clock note. Keep it under about fifteen words on screen and put the
evidence in the comment: packets are built at `orchestrator/game.py`:1778 before
`advance_tick` at :1786 and recorded against the pre-advance `input_tick` at :1794,
which is why an agent's stamp is one ahead. Do not promise a fix — no Phase-20 task
re-stamps the clock, and a note that implies otherwise is the same class of defect
this task is closing.

Step 6 — blast radius. `BallotCard`, `SetSelector` and `HighlightCard` are all
re-exported or reused elsewhere; run the grep for each symbol you touch before you
touch it. If a consumer outside the seven files needs to change, stop and put it under
Questions rather than widening scope.

**Ready-to-paste prompt:** `agent_prompts/task-20-2-spectator-copy.md`

### Task 20.3 — Layout and keyboard: the dock stops hiding the map; one owner for focus traps
**Branch:** `phase-20-dock-and-focus`
**Depends on:** 20.2 — the spectator copy pass settles the wording inside the same transport component, so this task moves that component's layout on top of a finished copy diff instead of racing it
**Section refs:** audits/review-2026-08-19/B/frontend-a.md §2 F3 (register C-9; the row in audits/review-2026-08-19/B/collated-findings.md reads "two stacked focus traps lock the keyboard onto one control", repro `work/frontend-a/probe/trap.mjs` → `Tab -> tour:Skip (×4, never advances)`); audits/review-2026-08-19/A/ux-visual-pass-lead.md [VERIFIED — layout] (the fixed dock takes ~35% of a 900-px-tall viewport; the Mind Inspector is clipped behind it); audits/review-2026-08-19/C/p3-frontend-product-engineer.md §2 (canvas top 311 px vs dock top 308 px at the 1000×640 GIF recording viewport), §5 (map hidden at 1000×640, ~40 px clipped at 1280×800, clean at 1440×900), §7 item 10; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-0 row 0.3 and §1 RC8; register context C-79 and C-101 in audits/review-2026-08-19/B/collated-findings.md. Re-verified at HEAD by this contract: `frontend/src/hooks/useFocusTrap.ts:32-67` (the window-level Tab handler) with its `FOCUSABLE` string at :15-16; `frontend/src/components/GuidedTour.tsx:327-374` (the un-deleted inline copy — Escape and Tab in one effect; the duplicated selector string at :349; the review's 325-372 is the comment-inclusive span), its focus-on-open effect at :317-321, the re-open channel at :27 and :34, the dialog at :388 (`z-[90]`); `frontend/src/components/MeetingView.tsx:584` (`useFocusTrap(dialogRef, isOpen)`), its :581-583 comment stating the tour "runs its own trap", the Escape yield at :602, the modal at :653 (`z-50`); `frontend/src/components/BeliefMatrix.tsx:122` (the second consumer), :110 (Escape yield), :143-145 (it steps aside while a meeting is open), the dialog at :178 (`z-[80]`); the two launchers and the header gate in `frontend/src/App.tsx:250-261` (`aria-label="Open the guided tour"`, inside the nav), :353-382 (`aria-label="Open the Belief × Truth matrix"`, itself hidden while a meeting is open) and :1161 (the header, and with it the Tour button, is unmounted while a meeting is open); `frontend/src/App.tsx:1122-1138` (the fixed dock, `z-[70]`, with `MeetingPauseBar` / `AdvantageGraph` / `EventTimeline` in a `max-h-40` scroller / `ReplayControls`), :1027-1057 (`useTransportHeight` publishes `--transport-h`), the consumers at :1074, `frontend/src/components/MeetingView.tsx:654` and `frontend/src/components/ThoughtStream.tsx:131`, :601-612 (why `MeetingPauseBar` must stay the first child), :129-134 (the tour suppresses every transport accelerator), :145-165 (the activatable carve-out keyed on `[data-transport-region]`), :1-13 (the stale "WITHOUT ever editing this file" header claim); `frontend/src/index.css:14-100` (the generated `tokens:start`/`tokens:end` block), :162-166 (`.map-canvas-fill`, the map's only stable handle — `frontend/src/components/MapView.tsx:830`), :191-199 (the reduced-motion blanket); `frontend/vitest.config.ts:10-19` (`environment: "node"` declared a CONTRACT — a DOM test belongs in the journey); `frontend/playwright.config.ts:70` (the default 1440×960 viewport); `frontend/e2e/journey.spec.ts:29` and :48-50 (the tour-seen key), :63 and :67 (the `[data-transport-region]` and `canvas` handles), :254-300 (the keyboard-transport pins), :396-431 (the reduced-motion pins)
**Complexity:** Medium
**Record impact:** none
**Measurement:** `cd frontend && npm run e2e` green with the two new steps, and each of them shown failing against the un-fixed code in the PR; `cd frontend && npm run test && npm run lint && npm run tsc:check && npm run build` green; the PR quotes the before/after `getBoundingClientRect` numbers at 1280×800 and 1000×640 beside the review's 311 px / 308 px.

Two defects meet on the one surface a stranger actually looks at. The first is a
keyboard lock: `useFocusTrap` and the inline copy `GuidedTour` never deleted both attach
their `keydown` listener to `window`, so whenever the tour is open over another overlay
BOTH run. On each Tab the lower dialog's trap sees focus outside itself and yanks it in;
the tour's trap then sees focus outside itself and yanks it back to its own FIRST
element. The review drove both handler bodies verbatim over a DOM shim and recorded
`Tab -> tour:Skip` four times running and `Shift+Tab -> tour:Next` four times running —
"Back" is unreachable by keyboard, and every keypress transiently parks focus inside the
scrim-covered overlay behind (audits/review-2026-08-19/B/frontend-a.md §2 F3). The
hook's own header says it was factored out of GuidedTour "so the meeting + belief
overlays share ONE implementation"; the extraction happened and the source was never
removed, down to a duplicated one-line `FOCUSABLE` selector. `MeetingView.tsx:581-583`
then documents the collision as if it were the design ("The guided tour, when open over
this, runs its own trap"). The Escape story is already correct — both overlays yield
Escape to the tour by reading `guidedTourOpen` — so this task gives Tab the same
single-owner treatment Escape already has.

The second is layout. The transport region is `fixed inset-x-0 bottom-0 z-[70]` and
stacks four surfaces inside it: the meeting pause bar, the advantage graph, a `max-h-40`
event-timeline scroller, and the transport proper. The visual pass measured it at ~35% of
a 900-px-tall viewport with the Mind Inspector clipped behind it; the product read
measured the map canvas starting at 311 px against a dock top of 308 px at 1000×640 —
the PixiJS map is entirely covered — and ~40 px clipped at 1280×800, clean only at
1440×900 (audits/review-2026-08-19/C/p3-frontend-product-engineer.md §2, §5). That is
why the README GIF, "the one asset most readers will ever see", shows a picker, a
timeline, a modal and a finale card, and never a moving agent. The dock earns its space
on a desktop and takes the whole product on a laptop, so the timeline half becomes a
disclosure that is closed by default below a documented viewport height.

The repair is cheaper than it looks because the measurement contract already exists:
`useTransportHeight` publishes the dock's real height as `--transport-h` via a
`ResizeObserver` (App.tsx:1027-1057) and three overlays consume it (App.tsx:1074,
MeetingView.tsx:654, ThoughtStream.tsx:131). Collapsing the timeline half shrinks the
measured height, and the map's padding, the meeting modal and the Mind rail all reflow
with no magic constants — which is also what un-clips the Mind Inspector the visual pass
complained about. Likewise the overlay z-order is already a stated contract (tour
`z-[90]` > belief `z-[80]` > transport `z-[70]` > finale `z-60` > mind rail `z-[55]` >
meeting `z-50`), so "which trap owns Tab" has a correct answer already written down; the
hook just has to read it.

Nothing here moves a recorded byte: no engine, agent, prompt or DTO code is touched, the
committed replays are untouched, and the four existing journey tests run at the config's
1440×960 viewport, which stays above the collapse threshold. Two constraints bound the
work. `frontend/vitest.config.ts:10-19` pins `environment: "node"` as a deliberate
contract and is out of scope, so the trap's pin is a Playwright keyboard step, not a
jsdom render test (this is exactly the gap C-101 names). And `frontend/src/index.css` is
GENERATED between its `tokens:start` (:14) and `tokens:end` (:100) markers from
`src/tokens.ts`, which is out of scope — a breakpoint written between the markers would
be erased by `npm run gen:tokens` and is read back off disk by `src/tokens.test.ts`, so
it goes in the hand-written region below :100.

**Files in scope:**
- frontend/src/hooks/useFocusTrap.ts; (the single-owner rule: only the top-most active overlay handles Tab)
- frontend/src/components/GuidedTour.tsx; (delete the inline trap copy; consume the hook or an overlay-stack owner)
- frontend/src/App.tsx; (the dock layout: collapsible / non-fixed below a height breakpoint)
- frontend/src/components/ReplayControls.tsx; (the collapsed-dock affordance)
- frontend/src/index.css; (breakpoint tokens only)
- frontend/e2e/journey.spec.ts; (a keyboard step: Tab reaches every tour control over an open meeting; map visible at 1280×800)

**Files NOT in scope:**
- frontend/src/components/MapView.tsx (20.1 owns it — the e2e addresses the map through the existing `.map-canvas-fill` class, never a new test id)
- any copy or tooltip string (20.2 owns the product wording; this task changes layout and keyboard behaviour, and the disclosure's label follows the vocabulary 20.2 landed — a plain inline label in ReplayControls.tsx beside its existing `aria-label`s, not a new key in `frontend/src/lib/copy.ts`; 20.2's dialect gate in `frontend/src/lib/copy.test.ts` now reads ReplayControls.tsx off disk, so `npm run test` bites on internal jargon in the new label)
- scripts/build_demo_bundle.py and frontend/e2e/bundle.spec.ts (20.7's bundle work — bundle.spec.ts asserts `[data-transport-region]` is visible and must stay green unchanged)
- frontend/src/components/MeetingView.tsx and BeliefMatrix.tsx (the two existing `useFocusTrap` call sites — they must keep compiling and behaving with no edit, which is the constraint on the hook's signature)
- frontend/src/store/replayStore.ts (no store field is added; the disclosure's state is component state in the workspace shell)
- frontend/vitest.config.ts and frontend/src/tokens.ts (the node-environment contract and the generated token source both stand)
- any Jinja prompt template, rendered prompt, replay or report byte (nothing this task touches reaches a recorded artifact)

**Definition of done:**
- [ ] Exactly one focus trap handles a Tab keypress at any moment: `useFocusTrap` acquires an explicit overlay ownership rule (top-most active overlay wins, matching the z-order contract the components already state) and the two existing call sites at `MeetingView.tsx:584` and `BeliefMatrix.tsx:122` compile and behave unchanged, with no edit to either file.
- [ ] `GuidedTour.tsx`'s inline Tab trap and its duplicated `FOCUSABLE` selector string are DELETED and the tour consumes `useFocusTrap`; the tour's Escape handling survives (both overlays still yield Escape to it via `guidedTourOpen`), and its redundant focus-on-open effect is removed rather than left beside the hook's.
- [ ] With the tour stacked over an already-open overlay, Tab cycles through every tour control including Back and Shift+Tab walks the same ring backwards, with focus never landing on a control inside the overlay behind — pinned by a new keyboard step in `frontend/e2e/journey.spec.ts` covering both stacks: the pointer-reachable Belief × Truth stack, and the meeting stack driven through the app's own re-open channel (the header carrying the Tour button is unmounted while a meeting is open, `App.tsx:1161`). The PR states which stack a user can reach by pointer today.
- [ ] The timeline half of the dock (the advantage graph and the event-timeline scroller) is CLOSED by default below a documented viewport-height breakpoint and open above it, toggled by a labelled disclosure control in `ReplayControls.tsx` with `aria-expanded`; the breakpoint value has ONE home in `frontend/src/index.css` below the `tokens:end` marker at :100, and the review's clean case (1440×900) stays expanded so the four existing journey tests are unaffected at the config's 1440×960 viewport.
- [ ] `MeetingPauseBar` remains the FIRST child of the measured column inside `[data-transport-region]` (App.tsx:601-612 makes that mount load-bearing for the ResizeObserver, the z-70 stacking and the accelerator carve-out), and `--transport-h` still measures the dock's real height in both states — asserted by the e2e reading the published property in the collapsed and expanded states.
- [ ] The map canvas is not covered by the dock at either measured viewport, asserted in the e2e from `getBoundingClientRect`: at 1280×800 the `.map-canvas-fill` box is entirely inside the viewport AND entirely above the dock's top edge; at 1000×640 it is entirely above the dock's top edge (the review measured canvas top 311 px against dock top 308 px there). The PR quotes both before and after numbers.
- [ ] Both new e2e steps are shown to BITE: the keyboard step fails against the un-fixed hook and the layout step fails against the un-collapsed dock, each demonstrated in the PR (craft rule 2).
- [ ] Reduced motion and the existing keyboard shortcuts are unchanged: `journey.spec.ts:254-300` and :396-431 pass untouched, the disclosure animates only through CSS transitions already collapsed by `index.css:191-199`, and the transport accelerators keep the same behaviour for a focused control inside `[data-transport-region]`.
- [ ] `App.tsx:1-13`'s claim that surfaces plug in "WITHOUT ever editing this file" is corrected to what is true now (craft rule 1, register C-79); no other restructuring of App.tsx is attempted.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — blast radius before scope (craft rule 6). `grep -rn "useFocusTrap" frontend/src`
returns exactly three sites at HEAD: the hook, `MeetingView.tsx:584`, and
`BeliefMatrix.tsx:122`. Both consumers are out of scope, so any parameter the hook grows
is OPTIONAL with a default and the two-argument calls keep compiling untouched. Grep
`--transport-h` and `data-transport-region` the same way before moving the dock — the
consumers are App.tsx:1074, MeetingView.tsx:654, ThoughtStream.tsx:131, the accelerator
carve-out at App.tsx:161, and both e2e specs.

Step 2 — the owner. The z-order is already written down in the components (tour 90 >
belief 80 > transport 70 > finale 60 > mind rail 55 > meeting 50), so give the hook an
optional overlay-layer argument defaulting to the base overlay layer, keep the set of
currently-active layers in one small explicit store created inside useFocusTrap.ts (a
zustand store or a useSyncExternalStore-backed registry — explicit state, not a mutable
module flag, the same reason GuidedTour's open state lives in the store), and let a
handler act only when its layer is the maximum active one. Ties break on registration
order, last registered wins, which matches DOM stacking for equal z; in practice a tie
cannot occur today because BeliefMatrix returns null while a meeting is open.

Step 3 — GuidedTour. Delete the Tab half of the :327-374 effect together with the
inline selector string at :349, keep the Escape half (it calls `finish()`, and both
overlays gate their own Escape on `guidedTourOpen`), and call the hook with the tour's
layer. The hook already focuses the dialog on open and restores focus on close, so the
separate focus effect at :317-321 goes too — except for the step-change dependency, which
is a one-line re-focus if the hook's open-only focus is not enough; do not reintroduce a
second listener to get it.

Step 4 — the dock. Only the advantage graph and the `max-h-40` timeline scroller
(App.tsx:1133-1136) move into the collapsible half; `MeetingPauseBar` stays first and
`ReplayControls` stays last. Own the open/closed flag as React state in `Workspace()`,
seeded once from `window.matchMedia`, and pass it plus a toggle callback down to
`ReplayControls` as props — replayStore.ts is out of scope and component state is the
smaller change. A user toggle wins over the media default for the rest of the session.
Nothing needs to touch `--transport-h`: the ResizeObserver republishes the smaller height
and every consumer reflows, which is the mechanism that un-clips the Mind Inspector.

Step 5 — the breakpoint. The review's own measurements bound it: clipped at 800 px tall,
clean at 900, so a threshold in between (around 860 px) collapses the broken cases and
leaves the clean one alone — and leaves the journey's 1440×960 default expanded, so the
four existing tests see today's layout. index.css is generated between :14 and :100 from
src/tokens.ts and is read back off disk by src/tokens.test.ts, so write the custom
property in the hand-authored region below :100 beside `.map-canvas-fill`, and read that
one value in the matchMedia query via `getComputedStyle(document.documentElement)` so the
number has a single home.

Step 6 — the journey. `openFeaturedReplay` suppresses the tour through
`localStorage` (:29, :48-50), so a stacked-trap step re-opens it deliberately. The
pointer-reachable stack is the Belief × Truth one: click the launcher
(`aria-label="Open the Belief × Truth matrix"`, App.tsx:362 — the journey already names
this control at :330) and then the nav's Tour button (`aria-label="Open the guided
tour"`, App.tsx:257). The meeting stack needs the tour's own re-open event
(GuidedTour.tsx:27, :34) because App.tsx:1161 unmounts the header, and the launcher gate
at App.tsx:353 hides the belief button, once a meeting is open. Both overlays and the
tour render `role="dialog"`, so disambiguate by a control each one owns — the tour's
`aria-label="Close the guided tour"` at GuidedTour.tsx:415 is stable across steps while
its `aria-labelledby` title is not. Read the focused control with
`page.evaluate(() => document.activeElement?.textContent)` after each Tab rather than
asserting on a locator's focus, and assert the whole visited ring, not just that Back is
reachable once. For the layout step use `setViewportSize` and the bounding boxes of
`.map-canvas-fill` and `[data-transport-region]`; no test id is added to MapView.tsx.

Step 7 — prove the gates bite before opening the PR. Stash the hook change and run the
keyboard step; stash the dock change and run the layout step; paste both failures. Then
quote the after numbers beside the review's 311 px canvas top / 308 px dock top so the
claim is verifiable-shaped rather than "the map is visible now".

**Ready-to-paste prompt:** `agent_prompts/task-20-3-dock-and-focus.md`

### Task 20.4 — The replay listing survives a corrupt or empty replay file
**Branch:** `phase-20-loader-resilience`
**Depends on:** none (root)
**Section refs:** C-5 (audits/review-2026-08-19/B/collated-findings.md, the C-5 row, P1; full finding audits/review-2026-08-19/B/api.md §2 F1 and §5 "Gaps"; adversarial verdict audits/review-2026-08-19/B/verdicts.md verdict #6 — CONFIRMED, all three sub-claims including the exception typing; roadmap slot audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-0 row 0.4 and §2 credibility row 11 UNDERMINED; audits/review-2026-08-19/D/cross-track-map.md, the C-5 row, RR-free); api/replay_loader.py:703-729 (`list_replays`; the sole guard is `except ReplayLog.CorruptedFileError` at :727, logged at :728), :714-718 (the docstring claim "one bad replay no longer blocks the picker (Audit K-K-8, backend half)"), :731-748 (`load_replay` — the direct-fetch path this task deliberately leaves loud), :750-778 (`cost_summary`; the per-file reduction at :759 has no guard at all), :1683-1686 (`_file_summary`), :1688-1725 (`_read_summary`), :1727-1739 (`_metadata_view`), :1944-1969 (`_replay_paths`), :1985-1997 (`_resolve_path`); orchestrator/replay.py:1137-1187 (`read_all_entries`) with :1165 `raise ValueError(f"invalid replay JSON at line {line_number}")` for a truncated last line and :1190-1207 `_parse_entry` whose four `model_validate` calls raise pydantic `ValidationError` (a `ValueError` subclass) plus bare `ValueError` at :1192 and :1207, and :1146-1148 recording that "Broader corruption hardening (mid-line partial writes, etc.) is deferred"; tests/api/test_replay_loader.py:539-559 (`test_list_replays_skips_corrupted_file_and_logs` — pins the doubled-write branch only, and is the source of the false confidence); AGENTS.md:50 ("No silent fallbacks. If something is invalid, raise."), AGENTS.md:76-110 craft rules 1, 2 and 6
**Complexity:** Small
**Record impact:** none — read-side listing guard plus tests; no replay bytes, no rendered prompt bytes and no detector output move, so nothing here waits on the Phase-20 adopting record
**Measurement:** `uv run pytest tests/api/test_replay_loader.py -q` green with the three new corrupt-fixture cases; the review's repro directory (a copy of replays/samples/4p1i with one replay truncated by 40 bytes, one emptied, one row typed `"tick": "not-an-int"`) served through `TestClient` now returns 200 from `GET /replays` and `GET /eval/cost-summary` — both 500 at HEAD — with every healthy replay present and one WARNING line per skipped path

`api/replay_loader.py:714-718` promises that "one bad replay no longer blocks the
picker", and `list_replays` delivers that promise for exactly one corruption shape: the
doubled-write `ReplayLog.CorruptedFileError` Task 4.16 detects. Every other way a replay
file goes bad leaves the whole collection unreachable. `orchestrator/replay.py:1165`
raises a bare `ValueError` when the last line is a partial write — precisely the shape a
Ctrl-C'd, OOM-killed or disk-full tournament run leaves behind, because the runner writes
incrementally — and `_parse_entry` (:1190-1207) raises pydantic `ValidationError` for a
schema-invalid row. Neither is a `CorruptedFileError`, so both escape :727 and 500 the
listing. `cost_summary` (:750-778) has no guard at all, so the eval dashboard falls over
with it. The review's repro is decisive
(audits/review-2026-08-19/B/verdicts.md verdict #6): with one truncated, one emptied and
one type-invalid file in a copy of `replays/samples/4p1i`, `GET /replays` and
`GET /eval/cost-summary` both return 500 while `GET /replays/headless-seed-0` still
returns a perfectly healthy 21-tick game — healthy, and unreachable through the listing.
Deleting the truncated file alone still 500s; deleting the invalid one too restores a
200 with four items. One bad byte takes out the set.

The fix is a one-clause widening, and the review verified the typing detail that makes it
a one-clause fix: pydantic v2's `ValidationError` subclasses `ValueError`, so
`except (ReplayLog.CorruptedFileError, ValueError)` at the per-file boundary covers the
truncated line, the schema-invalid row and the unknown-`kind` row together. What matters
is where the boundary sits. This contract rules it explicitly: the LISTING and the COST
SUMMARY degrade — skip the file, log at WARNING with the path and the reason, keep
serving every healthy replay — while a DIRECT `load_replay` of the broken game id keeps
failing loud, exactly as it does at HEAD. Degradation on the collection view, fail-loud
on the item view: the picker stops being hostage to one file, and nobody can fetch a
half-written game and be told it is fine.

The empty-file leg is the one with no ruling anywhere, and it is the leg AGENTS.md:50
speaks to. A zero-byte file parses to zero entries, so `_read_summary` (:1688-1725)
reduces it to `total_ticks=0, winner=None`, `_metadata_view` (:1727-1739) advertises it
in the picker as an ordinary replay, and `cost_summary` counts it in `total_replays` —
diluting `mean_cost_per_replay` for the whole set. The review measured the shape
directly: `read_all_entries(replay-seed-2) -> OK, 0 entries`, and
`GET /replays/headless-seed-2 -> 200 ticks=1 meetings=0`. That is a silent fallback in a
repo whose own rule is "If something is invalid, raise. Do not paper over." A file that
contributes no replay records is not a 0-tick game; it is an unusable file, and this
contract treats it as one on every path.

Two things make this front-door work rather than housekeeping. The README hands a
stranger a tournament command, so the very first artifact a visitor produces is the one
that can break the picker — this is the X1 reproduction path
(audits/review-2026-08-19/D/cross-track-map.md, the C-5 row). And the existing test at
tests/api/test_replay_loader.py:539-559 is worse than no test: it pins the implemented
branch, is named as though it pins the docstring's general claim, and so certifies K-K-8
as fixed. Craft rule 2 applies — the replacement fixtures must be a gate that can fail,
demonstrated by narrowing the guard back to `CorruptedFileError` and watching all three
cases go red. Blast radius (craft rule 6) is small and checked: the only non-test
consumers of these two methods are `api/routes/replays.py:34-42`,
`api/routes/eval.py:183-184` (bare delegates, unchanged) and
`scripts/build_demo_bundle.py:279` (a skipped replay simply does not enter the bundle,
which is the wanted behaviour and is traceable through the WARNING line).

**Files in scope:**
- api/replay_loader.py; (list_replays / cost_summary / the summary reader: catch ValueError, skip zero-byte files, log at WARNING with the path)
- tests/api/test_replay_loader.py; (the three corrupt fixtures: truncated, empty, invalid-row → listing 200 with the healthy replays; the skipped path named in the log)

**Files NOT in scope:**
- orchestrator/replay.py (the reader's CorruptedFileError semantics and the recorded deferral at :1146-1148 are unchanged — the loader decides what to tolerate, the reader keeps raising)
- the routes (api/routes/replays.py, api/routes/eval.py: bare delegates; the fix is in the loader's listing/summary path, and no new exception handler is registered in api/main.py)
- frontend/ (no DTO, no copy, no version bump — the served shapes are identical)
- tests/api/fixtures/sample_replay.py (out of scope: build the three corrupt fixtures inline in the test from `write_sample_replay`'s output rather than adding a shared helper)
- scripts/build_demo_bundle.py (a downstream consumer of `list_replays`, read for blast radius only; the demo bundle belongs to the Pages task)
- replays/ (no committed bytes move; the four committed sets are healthy and must stay green unchanged)

**Definition of done:**
- [ ] `list_replays` and `cost_summary` guard the PER-FILE boundary with `except (ReplayLog.CorruptedFileError, ValueError)`, so a set directory holding a truncated replay, a zero-byte file and a schema-invalid row still lists every healthy replay and still computes a cost summary over the healthy subset — asserted in tests/api/test_replay_loader.py both at the loader level and through `TestClient` (HTTP 200, not 500), for both endpoints.
- [ ] `cost_summary`'s `total_replays` counts only the files it actually reduced, so `mean_cost_per_replay` is no longer diluted by a skipped file — pinned in tests/api/test_replay_loader.py against a directory of two healthy replays plus the three broken ones.
- [ ] Every skipped file is logged exactly once at WARNING naming its path and which class of failure it hit (doubled write / unparseable row / no replay records), distinguishable per class — pinned with `caplog` on the `api.replay_loader` logger; nothing is swallowed silently.
- [ ] A replay file that contributes no replay records — zero-byte, or containing only blank lines — is skipped by the listing and by the cost summary and is never served as a 0-tick game; pinned in tests/api/test_replay_loader.py (the review measured `GET /replays/headless-seed-2 -> 200 ticks=1 meetings=0` at HEAD).
- [ ] The direct-fetch contract is unchanged and now pinned: `load_replay` of the truncated id and of the schema-invalid id still raises out of the loader (a loud 500 through the route), and `load_replay` of the no-record file raises rather than synthesizing a game — so the listing's skip is degradation, never silence.
- [ ] The `list_replays` docstring (api/replay_loader.py:714-718) states the true behaviour: which failure classes are skipped, that they are logged, and that a direct fetch of the same id still fails loud; history is at most one trailing provenance line (craft rule 1), and the K-K-8 sentence no longer over-claims.
- [ ] The gate can fail (craft rule 2): narrowing the guard back to `except ReplayLog.CorruptedFileError` turns all three new cases red, and the PR quotes that run alongside the green one.
- [ ] The four committed sets are unaffected: `uv run pytest tests/api -q` green, including the existing `test_list_replays_skips_corrupted_file_and_logs` doubled-write case and the `list_replays` consumers in tests/api/test_view_model.py, test_leak.py and test_sets.py.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — reproduce before editing. Copy `replays/samples/4p1i` into a tmp dir, truncate
one file by ~40 bytes, empty a second, and retype one row of a third to
`"tick": "not-an-int"`; point a `ReplayLoader` at it and confirm the two 500s and the
empty-file 200 exactly as audits/review-2026-08-19/B/api.md §2 F1 records them. Paste the
before/after in the PR.

Step 2 — widen at the per-file boundary, not around the loop. In `list_replays` the guard
already wraps a single `self._metadata_view(path, seed)` call; add `ValueError` to the
same clause. `cost_summary` currently builds `summaries` as one list comprehension at
:759 — turn it into an explicit loop with the identical guard so a bad file is skipped
rather than aborting the aggregate, and so the WARNING carries the path. Keep the two
guards textually identical (one shared private helper that yields `(path, summary)` pairs
for the healthy files is the cleanest form, and it keeps the skip rule in exactly one
place).

Step 3 — the no-record rule. Cheapest exact check is a `path.stat().st_size == 0`
short-circuit before any parse; that alone leaves a blank-lines-only file serving as a
0-tick game, so also treat a summary derived from zero entries as unusable. Either add an
entry count to `_ReplaySummary` (:617, constructed only at :1717) and raise from the
skip helper when it is zero, or have the helper raise before returning. Raise
`ReplayLog.CorruptedFileError` with a message naming the file — it is already imported,
it already means "this file is unusable", and reusing it keeps both the listing guard and
`load_replay`'s loud failure on one type rather than inventing a public exception for a
Small task.

Step 4 — the direct path. `load_replay` (:731-748) resolves through `_resolve` /
`_resolve_path` (:1971, :1985-1997), which walk `_replay_paths` (:1944-1969). Do NOT
filter inside `_replay_paths`: that would turn a direct fetch of the broken id into a 404
"not found", which is a different and less honest answer than "this file is broken".
Apply the no-record check on the `load_replay` side instead, so the truncated and
schema-invalid ids keep raising from the walk and the empty id joins them.

Step 5 — tests. Build the three fixtures inline from `write_sample_replay` (already
imported at tests/api/test_replay_loader.py:56-64): write a healthy replay then
`path.write_bytes(path.read_bytes()[:-40])` for the truncated one, `path.write_text("")`
for the empty one, and rewrite one JSON line with a wrong-typed field for the invalid one.
Assert at the loader level and through `TestClient` (`raise_server_exceptions=False` so a
500 is observable as a status code). Mirror the shape of the existing doubled-write test
at :539-559 and leave that test alone — the point is that it stays green beside the three
new ones.

**Ready-to-paste prompt:** `agent_prompts/task-20-4-loader-resilience.md`

### Task 20.5 — First-run quiet: the prompt-set notice and its documentation
**Branch:** `phase-20-prompt-set-notice`
**Depends on:** none (root)
**Section refs:** C/B1 (audits/review-2026-08-19/C/collated-portfolio.md §B item B1, ruled GOOD-top in §D3); audits/review-2026-08-19/C/x1-front-door-reproduction.md §1 (the "Noise observed on every run" note under the command table) + §5 MUST-3; audits/review-2026-08-19/C/p1-backend-hiring-manager.md §2 ("reads like a misconfiguration"), §4 and §7 GOOD-6; C-83 + C-126 + C-130 (audits/review-2026-08-19/B/collated-findings.md); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 0.5 and audits/review-2026-08-19/D/cross-track-map.md §"0. Front-door pre-wave"; anchors re-verified at HEAD — agents/strategic/prompts/loader.py:145-167 (`_notify_bare_prompt_set_fallback`, the stderr print), :170-201 (`resolve_prompt_set`, the emitter call at :200), :238 (`_ENV` built at import); orchestrator/game.py:910 (`build_default_meeting_runner`'s bare `resolve_prompt_set()`) vs :915 (`prompt_versions_for_set(active_prompt_set)`, explicit and therefore silent); llm/provider.py:31 (`ENV_PROVIDER`), :42 (`PROVIDER_FAKE`), :302-306 (the default/strip/lower resolution expression and the fake branch it selects); llm/fake_provider.py:8-11 + meetings/manager.py:1380-1382, :1863-1865 (both client call sites pass a Pydantic `schema`); orchestrator/replay.py:93-103 (the deliberately mirrored 18.10 resolver and the reason the loader is not imported there); tests/agents/test_prompt_loader.py:78-152 (`TestBareEnvironmentFallbackIsLoud`, the Task-19.6 pins); .env.example:29 (`AILIBI_LLM_PROVIDER=fake`); AGENTS.md:48 ("No global state"), :112 ("Environment setup"), :127-146 (the LLM-providers bullet); tasks/phase-19.md Task 19.6 (the notice's origin; its Files-NOT-in-scope routed the env-var documentation to Task 19.1, which never carried it)
**Complexity:** Small
**Record impact:** none — stderr diagnostics and documentation only; no rendered prompt byte moves, no recorded `prompt_versions` stamp moves, no detector output moves, pinned by the prompt byte-golden and `verify_samples.sh`.
**Measurement:** with `env -u AILIBI_PROMPT_SET -u AILIBI_LLM_PROVIDER`, each of the three front-door commands emits ZERO stderr lines — `uv run python scripts/run_game.py --seed 42 --replay-path <tmp>` (2 notice lines at HEAD), `bash scripts/verify_samples.sh` (2), `uv run python scripts/run_tournament.py --num-games 5 --output-dir <tmp>` (6); `uv run pytest tests/agents/test_prompt_loader.py -q` green with the real-provider leg asserting exactly one notice line per process; `bash scripts/verify_samples.sh` 100/100 clean; `uv run python scripts/check_doc_facts.py` green.

The first thing a stranger sees when they run this project is a warning about a variable
this project documents nowhere. Every front-door command prints
`agents.strategic.prompts.loader: AILIBI_PROMPT_SET is unset — falling back to the frozen
reference set 'qwen3_5_9b', two generations behind the operational baseline 'qwen3_6_27b'`
on stderr, and it is the ONLY thing on stderr. Re-measured at HEAD in this planning
session, bare-environment: `run_game.py` prints it twice, `verify_samples.sh` twice, the
README's own five-game tournament six times — matching the review's counts
(audits/review-2026-08-19/C/x1-front-door-reproduction.md §1). `AILIBI_PROMPT_SET` appears
zero times in README.md, .env.example, AGENTS.md and docs/architecture.md (grep count 0 in
each, re-verified at HEAD). Five of six portfolio personas said they would not star the repo
today (audits/review-2026-08-19/D/FINAL-synthesis.md §4), and the one who ran the
determinism demo recorded that the first output "reads like a misconfiguration"
(audits/review-2026-08-19/C/p1-backend-hiring-manager.md §2). A
reproducibility pitch whose first line is an unexplained warning is spending its strongest
asset on nothing.

The notice is not wrong — it is untargeted. Task 19.6 added it for a real reason: the
default set VALUE must stay `qwen3_5_9b` for byte-identity with every committed render,
while every operational surface runs `qwen3_6_27b`, so a bare shell used to take a
two-generations-old prompt family with no signal at all. That reasoning holds for a real
provider and evaporates under the fake one. Both client call sites that can reach a
provider pass a Pydantic `schema` (meetings/manager.py:1382 `MeetingTurn`, :1865
`VoteBallot`), and with a schema the fake builds a minimal valid instance by introspecting
the model rather than reading the prompt's wording (llm/fake_provider.py:8-11) — so "two
generations behind the operational baseline", a claim about MODEL behaviour, describes a
risk that cannot exist on the default path. The set does still select which template bytes
render and which `prompt_versions` a recording stamps, which is exactly why this task
DOCUMENTS the variable rather than deleting the notice: the honest fix is to make the
notice fire where it means something and to name the knob where a reader will look.

The second defect is volume. The notice fires once per resolution point, and the resolution
points are per-process and per-game: the import-time `_ENV` build (loader.py:238) plus one
per `build_default_meeting_runner` call (orchestrator/game.py:910). That is why a five-game
tournament prints six lines. Under a real provider the message is worth saying once; saying
it once per game is the same noise with a better excuse. This task makes it once per
process. That reverses a deliberate 19.6 ruling recorded in the emitter's own docstring
(loader.py:149-150: no warn-once flag, because that would be module-level mutable state
under AGENTS.md:48), so the reversal is recorded in place of that sentence, not stacked on
top of it: AGENTS.md:48 forbids module-level mutable state that OWNS state the program
reads back; a de-duplication cache for a stderr diagnostic owns nothing, changes no return
value, and is resettable — and the tests reset it explicitly rather than depending on
collection order.

Nothing here moves a byte the record depends on. C-126 (audits/review-2026-08-19/B/collated-findings.md)
counted `.env.example` documenting 11 of 43 `AILIBI_*` names; this task closes the one the
front door prints. C-83's separate finding — that the loader's import-time `_ENV` side
effect is what forces `orchestrator/replay.py:93-103` to mirror the 18.10 resolver
byte-for-byte instead of importing it — is NOT addressed here and must not be: removing the
import-time build changes what a stray prompt-set export does to every replay-only consumer,
which is a different task with a different blast radius. This task adds no import-time work
beyond two constant imports.

**Files in scope:**
- agents/strategic/prompts/loader.py; (silence the notice when `AILIBI_LLM_PROVIDER` resolves to the fake provider; emit at most once per process otherwise; the docstring ruling)
- tests/agents/test_prompt_loader.py; (both provider branches, the once-per-process pin, the env grid, and the reset seam the Task-19.6 pins now need)
- .env.example; (document `AILIBI_PROMPT_SET` beside `AILIBI_LLM_PROVIDER` at :29 — the default, the operational baseline, where the registered names live, and that the notice is expected under a real provider)
- AGENTS.md; (one sentence naming the variable in the Environment-setup LLM-providers bullet at :127-146)

**Files NOT in scope:**
- README.md (the front-door rewrite owns it and carries the documented variable there; this task must not pre-empt that text)
- orchestrator/game.py (the prompt-version registry and the runner's resolution points are unchanged — the gate lives at the emitter, not at the call sites)
- orchestrator/replay.py (the mirrored 18.10 resolver and C-83's import-time-side-effect finding are a separate defect; `_ENV` at loader.py:238 stays exactly as it is)
- llm/provider.py (read for `ENV_PROVIDER` / `PROVIDER_FAKE` and the resolution expression at :302; imported, never re-implemented, never edited)
- any `.j2` prompt template and any prompt-set directory (prompt-template edits belong to the phase's single prompt-set bump task and to no other)
- scripts/check_doc_facts.py (no new checked fact is added here; it must stay green over the edited `.env.example`)
- tests/conftest.py (pinning the whole `AILIBI_*` env surface for the suite is another contract's file)

**Definition of done:**
- [ ] With `AILIBI_LLM_PROVIDER` unset or resolving to the fake provider, `resolve_prompt_set` takes the default and emits NOTHING on stderr; with `AILIBI_PROMPT_SET` unset and the provider resolving to `anthropic`, `ollama` or `featherless`, the one-line notice still prints — both branches pinned in `tests/agents/test_prompt_loader.py`.
- [ ] The notice prints at most ONCE per process on the real-provider path: a test drives at least three fallback resolutions under a real-provider env mapping and asserts exactly one stderr line, and a companion test asserts the FIRST resolution still emits (the gate can fail — AGENTS.md craft rule 2).
- [ ] Suppression never consumes the one allowed emission: a fake-provider resolution followed by a real-provider resolution in the same process still prints the notice once — pinned.
- [ ] The provider gate uses `ENV_PROVIDER` and `PROVIDER_FAKE` imported from `llm.provider` (no mirrored string literal in the loader) and its verdict agrees with `llm.provider.build_default_client`'s branch selection over the env grid `unset`, `"fake"`, `"FAKE"`, `" fake "`, `""`, `"anthropic"`, `"ollama"`, `"featherless"` — pinned as a table-driven test; the provider is read from the SAME `env` mapping the prompt set is resolved from, never from `os.environ` when a mapping was passed.
- [ ] The Task-19.6 pins at `tests/agents/test_prompt_loader.py:78-152` still assert the notice, via an explicit documented reset of the once-per-process seam in a fixture; no test in the file depends on collection order or on whether the import-time `_ENV` build already fired.
- [ ] `.env.example` documents `AILIBI_PROMPT_SET` in the LLM-provider section immediately after `AILIBI_LLM_PROVIDER=fake` (:29) as a COMMENTED example line — never an active assignment — naming the default set, the operational baseline set, `orchestrator/game.py::PROMPT_VERSION_SETS` as the enumerable source of the registered names, that an unknown name fails loud, and that the notice under a real provider is expected rather than a misconfiguration; AGENTS.md's Environment-setup LLM-providers bullet names the variable in one sentence.
- [ ] The emitter's docstring states the current rule in intent-first form (fake provider: silent; real provider: once per process) with at most one trailing provenance line, and the Task-19.6 sentence refusing a warn-once flag is REPLACED by the ruling this task makes — AGENTS.md craft rules 1 and 3, and the graduation-sweep convention applied to a reversed decision.
- [ ] Record impact none is proven, not asserted: `bash scripts/verify_samples.sh` reports 100/100 clean and `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` is green, so no rendered prompt byte and no recorded `prompt_versions` stamp moved; `uv run python scripts/check_doc_facts.py` stays green over the edited `.env.example`.
- [ ] The PR quotes the before/after stderr line counts for all three front-door commands run with `env -u AILIBI_PROMPT_SET -u AILIBI_LLM_PROVIDER` (before: 2, 2, 6 — all of them this notice; after: 0, 0, 0) and the same three commands under `AILIBI_LLM_PROVIDER=featherless` (after: 1, 1, 1).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — import `ENV_PROVIDER` and `PROVIDER_FAKE` from `llm.provider` at module level in
the loader. This is a new `agents -> llm` package edge and no import-linter contract forbids
it: the four contracts are agents-not-engine, agents-not-training, agents-not-meetings.manager,
and observation-not-agents/meetings/llm (`.importlinter`). `llm.provider` imports only
`llm.client`, `llm.report_normalize` and pydantic, so there is no cycle and no meaningful
import-time weight. Do NOT copy the two literals into the loader: the byte-for-byte mirror
at `orchestrator/replay.py:93-103` exists only because the loader raises at import, it
needed a CI equivalence pin to stay honest, and it is the drift hazard an import avoids.
Run `uv run lint-imports` immediately after adding the import and before anything else; if
a contract reports BROKEN, stop and report it under Questions rather than routing around it.

Step 2 — resolve the provider from the same mapping the set is resolved from. Inside
`resolve_prompt_set` the mapping is already `env if env is not None else os.environ`; reuse
that value and copy `llm/provider.py:302`'s expression exactly —
`mapping.get(ENV_PROVIDER, PROVIDER_FAKE).strip().lower() == PROVIDER_FAKE` — so an unset
variable reads fake, `" FAKE "` reads fake, and an empty string does not (an empty string
raises in `build_default_client`; the loader must not disagree with it). Pass the mapping
into the emitter rather than re-reading `os.environ` there, or a test that passes `env=`
will silently consult the ambient shell.

Step 3 — gate first, dedupe second. Return early on the fake path so nothing is emitted and
nothing is recorded; only on the real-provider path call the once-per-process emitter. A
`functools.lru_cache`-wrapped private emitter keyed on the resolved `(set_name, provider)`
gives the dedupe with no hand-rolled boolean, and its own `cache_clear()` is the reset seam
the tests need — put that reset in an autouse fixture in `tests/agents/test_prompt_loader.py`
so the Task-19.6 assertions keep working (by the time any test runs, the import-time `_ENV`
build at loader.py:238 has already fired, so without a reset every one of those tests would
see silence and pass for the wrong reason).

Step 4 — the docs. In `.env.example`, put the block right after `AILIBI_LLM_PROVIDER=fake`
at :29 and keep the example line commented, matching `AILIBI_OLLAMA_HOST` and friends: an
active `AILIBI_PROMPT_SET=qwen3_6_27b` in a copied `.env` would move every locally rendered
prompt away from the committed default, which is the opposite of what the byte-identity
default is for. Name the default and the operational baseline, then point at
`orchestrator/game.py::PROMPT_VERSION_SETS` for the registered names instead of hand-listing
the seven directories under `agents/strategic/prompts/` — five of the seven are model-sweep
sets that appear in no committed replay, and the default set appears in none either (C-130),
so a hand-maintained list here would be a fact that rots. In AGENTS.md the
sentence belongs in the existing LLM-providers bullet (:127-146), beside the sentence that
already names `AILIBI_LLM_PROVIDER`; do not open a new section.

Step 5 — measure before and after with `env -u AILIBI_PROMPT_SET -u AILIBI_LLM_PROVIDER`
and redirect stderr to a file per command, so the PR can quote counts rather than
impressions. The bare-environment baseline at HEAD is 2 / 2 / 6 lines for
`run_game.py --seed 42`, `verify_samples.sh`, and `run_tournament.py --num-games 5`, with
nothing else on stderr in any of the three.

**Ready-to-paste prompt:** `agent_prompts/task-20-5-prompt-set-notice.md`

### Task 20.6 — vote_correctness tells the truth: docstring, doc-fact pin, and the six zero-flag ejections
**Branch:** `phase-20-vote-correctness-truth`
**Depends on:** none (root)
**Section refs:** C-113 (audits/review-2026-08-19/B/eval-and-scripts.md §F2; audits/review-2026-08-19/B/collated-findings.md row C-113; audits/review-2026-08-19/D/FINAL-synthesis.md §2 row 12 [D-VERIFIED], §4 wave-0 item 0.7, ruling R8; audits/review-2026-08-19/D/synth-credibility.md §row 7; audits/review-2026-08-19/D/cross-track-map.md C-113 row); audits/audit-phase-20-planning.md:75-76 (the phase's wave-0 slate names this task); eval/vote_correctness.py:11-25 (the module-docstring paragraph; :17 "structurally pinned to 1.0", :19-21 "any value below 1.0 … a detector/recording bug to chase"), :90-94 (the same claim restated for the 9.5 baseline), :224-231 (`VoteCorrectnessReport`'s class docstring repeats the pin), :182 (`KILL_WITNESS_TICK_WINDOW`), :320 (`compute_vote_correctness`), :393/:406/:412 (`_has_real_evidence` and its two disjuncts); replays/samples/9p2i/tournament-eval-report.json → `impostor_ejections=78, evidence_backed_impostor_ejections=72, vote_correctness_rate=0.9230769230769231`; replays/samples/4p1i/tournament-eval-report.json → 10/10 = 1.0; replays/ml_corpus/9p2i/tournament-eval-report.json → 235/248 = 0.9475806451612904; replays/ml_corpus/4p1i/tournament-eval-report.json → 20/20 = 1.0; tests/eval/test_vote_correctness.py:1869-1922 (the committed-9p2i pin ALREADY asserts 72/78 at :1914 — the module's prose contradicts its own test file); meetings/manager.py:2004-2019 (the citation-gate comment block and its call site) and :3259-3350 (`guard_ballot_citation`: "A flagged target is convictable uncited … the ballot cites NOTHING" — a zero-flag EJECT that cites a turn or an observation id passes), meetings/constants.py:55-70 (the gate is unconditional since the 16.17 baseline-5 record); eval/vj_instruments.py:12, :93-106, :737 (Task 16.10 already instruments the zero-flag conviction channel with a typed provenance split); scripts/check_doc_facts.py:125-171 (`main` / `check_facts`), :172 (`check_sample_provenance`, the per-check shape), :595 (`read_document`, the `--repo-root` convention); tests/scripts/test_check_doc_facts.py:29-52 (`_COPIED` + the `doc_tree` perturbation fixture), :71-78 (the both-sides contract); README.md:194 (the metric's only README mention — a one-line description that carries NO structural-1.0 claim: C-113's README leg is refuted); frontend/src/components/TournamentDashboard.tsx:226-228 and :241 (the repeating surface — the copy pass owns it, not this task); AGENTS.md:83-102 (craft rules 1, 2, 5)
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run python scripts/check_doc_facts.py` exits 0; `uv run pytest tests/eval/test_vote_correctness.py tests/scripts/test_check_doc_facts.py -q` green; the census pin lists exactly 6 non-evidence-backed impostor ejections over replays/samples/9p2i (seeds 4, 17, 18, 22, 29, 40) and exactly 8 zero-naming-flag ones (those six plus seeds 26 and 38, which the kill-witness-chain disjunct backs); the two perturbation legs in tests/scripts/test_check_doc_facts.py each fail with a message naming the drifted fact.

The repo's thesis is that its prose and its committed bytes never disagree, and this is the
one place a reader can catch them disagreeing in under a minute. `eval/vote_correctness.py`
opens by declaring `vote_correctness_rate` **"structurally pinned to 1.0"**, with the
operational rule that "any value below 1.0 on a recorded set means an impostor ejection
happened WITHOUT its own triggering evidence — a detector/recording bug to chase"
(:17-21, restated at :90-94 and again in the `VoteCorrectnessReport` class docstring at
:224-231). The committed flagship artifact reads **0.9230769** (72 of 78 impostor
ejections evidence-backed). A reader who follows the docstring files a bug; a reader who
reads the test file finds the number already pinned at `tests/eval/test_vote_correctness.py:1914`
— the module's own regression test has been asserting 72/78 while its docstring called that
value impossible. Nothing in the repo surfaces the contradiction.

The mechanism sentence is the part that is actually false. The docstring's argument is that
"the §4.6 vote gate only crosses the eject threshold when the contradiction detector flagged
the ejected player" (:12-16), so `evidence_backed_impostor_ejections == impostor_ejections`
by construction. That has not been true since the Task 16.6 citation gate: `guard_ballot_citation`
(meetings/manager.py:3259-3350) coerces a zero-flag EJECT ballot to SKIP **only when it cites
nothing** — a zero-flag target convicted on a ballot citing a transcript turn or a private
observation id is legal by design, and the gate has been unconditional since the 16.17
baseline-5 record (meetings/constants.py:55-70). The re-derivation at HEAD shows exactly that
shape: in all six of the 9p2i counter-examples the meeting recorded **zero** `ContradictionRef`
rows and the eject ballots cited a transcript turn (seed 4's three ejectors all cite
`headless-seed-4:meeting-2:turn-2`). The claim is not a recording bug; it is a stale claim
about a substrate two phases old.

Re-derived at HEAD with the module's own predicate over the four committed reports:
samples/9p2i 72/78 = 0.923 (6 not evidence-backed), ml_corpus/9p2i 235/248 = 0.9476 (13 not
evidence-backed), samples/4p1i 10/10 = 1.0, ml_corpus/4p1i 20/20 = 1.0. The six 9p2i
counter-examples are seeds 4, 17, 18, 22, 29 and 40 — matching the review's probe
(audits/review-2026-08-19/B/eval-and-scripts.md §F2) seed for seed. One correction the review
did not draw: **eight** impostor ejections carry no naming `ContradictionRef` at all; two of
them (seeds 26 and 38) are rescued by `_has_kill_witness_chain`, the metric's second disjunct.
"Zero-flag" and "not evidence-backed" are therefore different populations, and a census that
conflates them would re-import the confusion this task exists to remove.

The review's ruling R8 (audits/review-2026-08-19/D/FINAL-synthesis.md §R8) narrows the blast
radius: the "README sells it as the circularity guard" leg is **refuted** — README.md:194
carries only a neutral one-line description of what the analyzer asks, with no pinned value.
Do not edit README.md. The one repeating user-facing surface is the Tournament tooltip
(frontend/src/components/TournamentDashboard.tsx:226-228, :241, "the live §4.6 pipeline pins
it to 1.0 by construction"); the Phase-20 spectator copy pass owns that string and lands
independently of this task, so this task's doc-fact check must NOT scan frontend copy — a
check that did would go red on `main` until the copy pass merged, and both tasks are roots.

This task ships three things and no behaviour: an honest docstring, a check that bites when
the prose and the data diverge again, and a pinned census of the counter-examples with a
stated classification rule so the next reader inherits an answer instead of an anomaly. Zero
production bytes move — no analyzer arithmetic changes, no report is regenerated, no replay
is touched — so `Record impact: none`, and the two byte pins (the prompt byte-golden and
`scripts/verify_samples.sh`) are unaffected by construction.

**Files in scope:**
- eval/vote_correctness.py; (docstring and comment lines ONLY — the module docstring's pin paragraph, the :90-94 restatement, and the `VoteCorrectnessReport` class docstring; zero behaviour bytes)
- scripts/check_doc_facts.py; (a fourth check: the module's documented semantics against the committed reports' recomputed values)
- tests/scripts/test_check_doc_facts.py; (the committed tree passes; the two perturbation legs fail, each naming the drifted fact)
- tests/eval/test_vote_correctness.py; (the census of the six non-evidence-backed and eight zero-naming-flag impostor ejections over samples/9p2i, each classified under a stated rule)

**Files NOT in scope:**
- README.md (its only mention carries no structural-1.0 claim — ruling R8 refutes that leg; the front-door rewrite owns the file and depends on this task's recorded wording)
- frontend/src/components/TournamentDashboard.tsx (the tooltip repeats the claim; the spectator copy pass owns it and lands independently — the new check must not read frontend copy)
- replays/ (bytes never move; the four committed reports are read, never rewritten)
- eval/vote_correctness.py's executable body — `compute_vote_correctness`, `_has_real_evidence`, `_has_naming_contradiction`, `_has_kill_witness_chain`, `KILL_WITNESS_TICK_WINDOW` (the arithmetic is correct; only its description is wrong)
- eval/vj_instruments.py (the Task 16.10 zero-flag channel is read as the reference definition, never edited)
- scripts/check.sh (`check_doc_facts` deliberately runs via pytest, not the gate script; wiring it in is a separate decision)

**Definition of done:**
- [ ] `eval/vote_correctness.py`'s module docstring and `VoteCorrectnessReport` class docstring state what the metric measures (the evidence-backed share of impostor ejections, under the two named disjuncts) and what a sub-1.0 value means on this substrate — that a zero-flag EJECT citing a transcript turn or an observation id is legal since the Task 16.6 citation gate — and a repo grep for "structurally pinned", "pinned to 1.0" and "pins it to 1.0" over `eval/` returns nothing; the PR quotes the grep.
- [ ] The rewritten paragraphs lead with intent per AGENTS.md craft rule 1: at most one trailing provenance line each, and the module-docstring line count (155 at HEAD) is quoted before and after in the PR. A whole-module prose sweep is explicitly NOT required — only the paragraphs this task rewrites.
- [ ] The docstring states the committed values in a single machine-checkable sentence per sample set, each stamped with its set and the baseline-6 record, and the four values agree with the committed reports (samples/9p2i 72/78, samples/4p1i 10/10, ml_corpus/9p2i 235/248, ml_corpus/4p1i 20/20).
- [ ] `scripts/check_doc_facts.py` gains `check_vote_correctness_sentinel`, wired into `check_facts`, which (a) re-derives each committed report's `evidence_backed_impostor_ejections / impostor_ejections` from the JSON under `--repo-root` and requires the docstring's stamped sentence for that set to carry the recomputed numerator, denominator and rate, and (b) fails when the docstring asserts a structural pin the data contradicts. The rate is RE-DERIVED at run time, never a literal in the checker, so a future re-record only re-stamps the docstring.
- [ ] `tests/scripts/test_check_doc_facts.py` proves the check bites both ways (craft rule 2): `check_facts(_REPO_ROOT) == []` on the committed tree; perturbing the copied `eval/vote_correctness.py` to reinstate a structural-pin sentence fails with a message naming the phrase; perturbing the copied `replays/samples/9p2i/tournament-eval-report.json` rate fails with a message naming the set and both values. The `_COPIED` fixture list grows by exactly the files the new check reads.
- [ ] `tests/eval/test_vote_correctness.py` pins a census over the committed samples/9p2i report: exactly 6 impostor ejections fail `_has_real_evidence` (seeds 4, 17, 18, 22, 29, 40, with meeting id, tick and ejectee), and exactly 8 carry no naming `ContradictionRef` (those six plus seeds 26 and 38, which the kill-witness chain backs). The two populations are asserted separately and the test docstring says why they differ.
- [ ] Each of the six is classified **detector miss** or **rhetoric-only conviction** under one rule stated in the test docstring, and the rule is decidable from recorded bytes alone: detector-miss iff the meeting's transcript contains the structured pair the detector is specified to flag against the ejectee (a `SawPlayerObservation` / `WhereaboutsClaim` conflict or a vent sighting naming them) while `contradictions` mints nothing for that subject; rhetoric-only otherwise (the eject ballots cite turns that carry no such pair). The counts per class are pinned; whichever way the six split, the split is a recorded finding, not a code change.
- [ ] No production behaviour changes: the `eval/vote_correctness.py` diff is comment and docstring lines only (the PR quotes `git diff -U0 eval/vote_correctness.py` showing no executable line), and `bash scripts/verify_samples.sh` plus the prompt byte-golden stay green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — reproduce before writing a word. Load each committed report with
`eval.meeting_quality.TournamentEvalReport.model_validate_json` (that is where the wrapper
class lives, not `eval.report_schema`), walk `report.report.games[].meetings[]`, keep the
EJECTED meetings whose `ejected_player_id` is an IMPOSTOR in `game.roles`, and call the
module's own `_has_real_evidence` — never a re-implementation. The four sets reproduce as
72/78, 10/10, 235/248 and 20/20; the 9p2i counter-examples reproduce as seeds
4/17/18/22/29/40. Compare `_has_naming_contradiction` alone to get the eight.

Step 2 — the checker. Follow the shape of `check_sample_provenance`: a function taking
`(repo_root, errors)`, reading its documents through `read_document` so `--repo-root` keeps
working, appending precise errors rather than raising, and called from `check_facts`. Read
`eval/vote_correctness.py` as TEXT, not by importing it: the perturbation fixture copies a
tree, and a text read is what makes the copy checkable. Bind the claim to a stamped sentence
shape (one per set, anchored on the set path) the same way the provenance check binds to one
paragraph, so a correct number elsewhere in the file cannot alibi a drifted sentence. Ban the
pin phrases by literal substring; keep the ban list short and name it.

Step 3 — the census. Keep it in the existing Task 9.6 committed-report block near
`_COMMITTED_9P2I_REPORT` (tests/eval/test_vote_correctness.py:1860). Pin the six as a frozen
tuple of (seed, meeting_id, tick, ejected) so a drifting record fails loud with the row that
moved, and pin the eight as a second tuple. For the classification, `eval/vj_instruments.py`
already owns a typed zero-flag provenance split (:93-106, `compute_vj_instruments` at :737) —
read it as the reference vocabulary and state in the test docstring how your rule relates to
it; do not import it if a direct read of `meeting.transcript.turns[].observations` (typed
`FoundBodyObservation` / `SawPlayerObservation` / `WhereaboutsClaim` / `CompletedTaskObservation`)
plus each eject ballot's `primary_reason_id` answers the question, which it does on these bytes.

Step 4 — record the ruling, do not chase it. If the six split entirely into rhetoric-only
convictions, that is the answer: the sentinel semantics are retired and the docstring says so.
If any is a genuine detector miss, do NOT fix the detector here — record it in the test
docstring and in the PR's Questions block; detector behaviour is lever-gated work and moves
rendered bytes, which this task must not.

**Public types introduced:**
- `check_doc_facts.check_vote_correctness_sentinel`

**Ready-to-paste prompt:** `agent_prompts/task-20-6-vote-correctness-truth.md`

### Task 20.7 — The hosted demo: a GitHub Pages workflow for the static bundle + the owner's About checklist
**Branch:** `phase-20-pages-demo`
**Depends on:** 20.2 (the spectator copy pass lands first — this task rewrites the same dashboard component's no-report panel, and the replacement wording has to be written in the cleaned product voice instead of re-introducing the audit dialect the copy pass just removed)
**Section refs:** audits/review-2026-08-19/C/collated-portfolio.md §A3 (host the bundle; the two warts to fix first) and §A4 (About/topics/homepage — description `""`, topics none, homepage `null`, `has_pages: false`, verified via `gh` by four personas); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-0 rows 0.1 and 0.8; audits/review-2026-08-19/C/p3-frontend-product-engineer.md (the built bundle drove in a browser: 8.8 MB, 7 featured games, 204 JSON files, 5.2 s warm — and the Tournament tab's raw `<!DOCTYPE HTML PUBLIC …>` dump, plus the bundle README's baked `/Users/danielkeinan/…` path); audits/review-2026-08-19/C/x1-front-door-reproduction.md (the reproduction table's bundle row: 4.3 s, served and played; the same absolute-path wart); audits/audit-phase-20-planning.md §6 (the owner's About checklist text, verbatim); scripts/build_demo_bundle.py:410 (`samples_dir=samples_dir.resolve()`) and :580 (the generated README's "baked from" line interpolating that resolved path), :339-343 (the standing absence-is-a-404 precedent for the unscored set), :510-533 (`_assert_static_mode_compiled_in`, the compiled-in-marker pattern); tests/scripts/test_build_demo_bundle.py:537 and :548 (the two asserts that currently PIN the absolute path); frontend/src/components/TournamentDashboard.tsx:1045-1058 (the no-report panel; :1057 renders the raw transport string); frontend/src/api/client.ts:65 (`ApiError` folds the response body into its message) and frontend/src/store/tournamentStore.ts:32-33 (the store flattens it to `error.message`); docs/deployment.md:12-14 and :58 (the ONLY-sanctioned-artifact rule) and :84-85 (the "first-class 'no report' state" claim the review contradicts); .github/workflows/ci.yml:12-13 (least privilege) and :29-34 (the full-SHA pin convention and its worked example); .github/workflows/campaign-tier.yml:10-15 (why a separate workflow file rather than a job in ci.yml); frontend/e2e/bundle.spec.ts:15-22 (zero `/api` proven twice) and :167 (`AILIBI_DEMO_BUNDLE_DIR` reuses a prebuilt bundle); frontend/vitest.config.ts:24-26 (`environment: "node"` — no renderer, so a component render test is not available here)
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run pytest tests/scripts/test_build_demo_bundle.py -q` green, including the out-of-repo bake (the generated README carries no absolute host path) and the planted leg where stripping the empty-state fragment from a synthesized `assets/*.js` makes the builder's compiled-in check RAISE; `cd frontend && AILIBI_DEMO_BUNDLE_DIR=<the built dir> npx playwright test e2e/bundle.spec.ts` green against the exact directory the workflow uploads; after the owner enables Pages, the workflow's own post-deploy step reports HTTP 200 for the deployment's `page_url` and the PR quotes it.

The one artifact in this repository that a stranger could actually look at is built, tested,
and unpublished. `scripts/build_demo_bundle.py` produces an 8.8 MB static directory — 7
featured games, 204 baked JSON files, a relative asset base — in about 4–5 seconds; two
reviewers served it and played it in a browser, and `frontend/e2e/bundle.spec.ts` drives the
BUILT output with every `/api` request aborted at the network layer
(audits/review-2026-08-19/C/p3-frontend-product-engineer.md; audits/review-2026-08-19/C/x1-front-door-reproduction.md).
Against that: `has_pages: false`, homepage `null`, description empty, no topics
(audits/review-2026-08-19/C/collated-portfolio.md §A4, verified through `gh` by four
personas). Every reader must clone ~256 MiB and install two toolchains to see anything move.
The frontend persona's sentence is the whole finding: for this audience the URL *is* the
project. This task publishes the artifact and hands the owner the five-minute checklist for
the repository card.

Hosting now is not work done twice. Pages rebuilds on push, so a future re-record refreshes
the demo for free (audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 0.8) — which is also
why the workflow belongs on `main` pushes and manual dispatch and nowhere else: a
`pull_request` trigger would hand a fork's head commit a deployment of the project's public
face.

Two warts have to go before the artifact is public. The first is the Tournament tab. The
bundle deliberately bakes no tournament report — the 9p2i one is the corpus, not a demo — so
the client 404s, exactly as it already does for the unscored set's missing rubric
(scripts/build_demo_bundle.py:339-343). But `ApiError` concatenates the RESPONSE BODY into
its message (frontend/src/api/client.ts:65), the store flattens that message to a string
(frontend/src/store/tournamentStore.ts:32-33), and the panel prints the string verbatim
(frontend/src/components/TournamentDashboard.tsx:1057) — so the reviewer's browser showed
`<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"…` inside the card. The designer ruling
here is that the absence signal STAYS a 404 and no payload gets baked to dodge it: GitHub
Pages answers a missing file with its own HTML page too, so a builder-side payload could not
have fixed the deployed case at all. The defect is that a card renders a server-supplied
document; the fix is that it never does. `docs/deployment.md:84-85` currently asserts the
Dashboard renders a "first-class 'no report' state" — after this task that sentence is true.

The second wart is that the generated bundle README bakes the builder's absolute home path
(`baked from /Users/danielkeinan/projects/AiLibi/replays/samples`) into the file
docs/deployment.md calls the only sanctioned public artifact — scripts/build_demo_bundle.py:410
resolves the directory and :580 prints it. The note's doctrine is right and stays: it names
the SOURCE and makes no claim about whether those bytes are public, because the script cannot
establish that. Only the rendering changes — a repo-relative path when the recordings live
inside the checkout, and no filesystem path at all when they do not — and a builder-side check
makes the class impossible to reintroduce in any text file the builder authors.

**Files in scope:**
- .github/workflows/pages.yml; (new: build the bundle on push to main, deploy to GitHub Pages)
- scripts/build_demo_bundle.py; (the relative-path README; a baked empty-state payload for the Tournament tab so the bundle never shows raw 404 HTML)
- tests/scripts/test_build_demo_bundle.py
- docs/deployment.md; (the Pages path as the sanctioned public artifact; the owner's one-time checklist: enable Pages, set About/description/topics/homepage — with the exact text from the planning audit)
- frontend/src/components/TournamentDashboard.tsx; (the bundle empty state when no report is served — a friendly card, not raw HTML)
- frontend/src/lib/copy.ts; (20.2 moved this surface's prose into the copy tree — the empty state's replacement strings are values here, not literals in the .tsx)

**Files NOT in scope:**
- README.md (20.12 adds the demo URL and the badges; this task adds no README text and no badge)
- frontend/e2e/bundle.spec.ts (it already proves zero `/api` requests against the built artifact — unchanged; reuse it via `AILIBI_DEMO_BUNDLE_DIR`, do not edit it)
- frontend/src/api/client.ts and frontend/src/store/tournamentStore.ts (the client seam and the store's error flattening are 20.16's region; this task sanitizes what the card renders, it does not retype the error)
- .github/workflows/ci.yml and campaign-tier.yml (read for convention only — the new workflow is its own file, per the reason campaign-tier.yml:10-15 records)
- docs/deployment.md's dangling `audit C-C-1/2/4` anchor line at :7 (a later docs-errata task owns it — leave it alone)
- docs/media/ and the hero capture re-record (a separate later task in this phase)
- any replay, report, or manifest bytes

**Definition of done:**
- [ ] `.github/workflows/pages.yml` builds `frontend/dist/demo-bundle` with `bash scripts/setup_env.sh` followed by `uv run python scripts/build_demo_bundle.py`, and deploys it with `actions/configure-pages` + `actions/upload-pages-artifact` + `actions/deploy-pages`; every action is pinned to a full commit SHA with the tag it resolved from in a trailing comment (the convention stated at .github/workflows/ci.yml:29-34); the workflow's top-level `permissions` is `contents: read` with `pages: write` and `id-token: write` granted ONLY to the deploy job; `concurrency` is set to a `pages` group with `cancel-in-progress: false`; the triggers are exactly `push` on `main` plus `workflow_dispatch`, and there is no `pull_request` trigger.
- [ ] The workflow gates on the artifact before it publishes it — a step running `uv run pytest tests/scripts/test_build_demo_bundle.py -q` ahead of the upload — and verifies it after: a final step that requests the deployment's `page_url` and fails on any non-200.
- [ ] The dashboard's no-report card renders NO server-supplied text: with `report === null`, `isLoading === false` and a non-null error, the panel shows only app-authored copy, and a repo grep confirms the transport string at TournamentDashboard.tsx:1057 no longer reaches the DOM. In a static build the guidance names the demo bundle (the featured games ship, the eval dashboard needs a tournament report, the repository has it), gated on `import.meta.env.VITE_AILIBI_STATIC_DATA` with a comment naming client.ts's sibling reader.
- [ ] That bundle-only sentence is proven to have survived dead-code elimination: `scripts/build_demo_bundle.py` asserts a short, stable fragment of it is present in the emitted `assets/*.js`, in the same place and shape as the existing `./data` marker check (scripts/build_demo_bundle.py:510-533), so a regression that deletes the designed empty state fails the BUILD instead of shipping. `tests/scripts/test_build_demo_bundle.py` pins both legs against a synthesized build directory: absent fragment raises, present fragment passes.
- [ ] The generated bundle README names its source as a repository-relative path when the recordings are inside the checkout, and names no filesystem path at all when they are not; the "does not judge whether they are public" sentence and the surrounding no-claim doctrine survive word for word. tests/scripts/test_build_demo_bundle.py's two asserts at :537 and :548 are REPLACED by assertions of the new rendering (not deleted), and the out-of-repo bake asserts the resolved absolute path is absent from the note.
- [ ] No text file the builder authors (the generated `README.md`, the ownership marker) contains an absolute host path: a builder-side check fails the build when one appears, and its perturbation leg is pinned in tests/scripts/test_build_demo_bundle.py.
- [ ] `docs/deployment.md` documents the Pages deployment as the sanctioned public route for the bundle (the live API's loopback posture and the :12-14 / :58 rules untouched and still true), corrects the :84-85 claim to state what the Dashboard tab now renders, carries the owner's one-time checklist copied verbatim from `audits/audit-phase-20-planning.md` §6 (enable Pages with the workflow as source; the ≤350-character description; the twelve topics; homepage = the Pages URL), and states how to re-verify a deployment — the `page_url` request, and re-running the bundle browser spec against the built directory with `AILIBI_DEMO_BUNDLE_DIR`, noting plainly that that spec serves a directory and does not drive a remote URL.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — the workflow. Two jobs, the official Pages shape: a `build` job (checkout,
setup-python, setup-uv, setup-node with the npm cache keyed on
`frontend/package-lock.json`, `bash scripts/setup_env.sh` with AILIBI_SKIP_FRONTEND UNSET
because this job needs `npm ci`, the pytest gate, `uv run python
scripts/build_demo_bundle.py`, `configure-pages`, then `upload-pages-artifact` with
`path: frontend/dist/demo-bundle`) and a `deploy` job with `environment: github-pages` and
`needs: build`. `frontend/dist/` is gitignored, so the default `--out` never dirties the
tree. Do NOT paste action SHAs from memory: resolve each tag at implementation time (for
example `gh api repos/actions/deploy-pages/git/ref/tags/v4 --jq .object.sha`, or
`git ls-remote`) and write the tag into the trailing comment beside it, the same way ci.yml
does. Reuse ci.yml's already-resolved SHAs for checkout / setup-python / setup-uv /
setup-node rather than re-pinning those four to different revisions.

Step 2 — the card. This is an EMPTY STATE, not an error surface, and that reframing is the
whole fix: the store hands the component one flattened string that concatenates whatever
the server sent, so the component has no way to tell a useful status line from an arbitrary
HTML document, and typed transport detail belongs to whoever owns the store seam. Drop the
line; keep the headline and the guidance; branch the guidance on the static-build flag.
The replacement strings are new values in `frontend/src/lib/copy.ts` beside
`SPECTATOR_COPY.dashboard.noReportTitle` (:207-210): 20.2 moved this surface's prose into
the copy tree, and `copy.test.ts` now fails a prose literal typed back into the `.tsx`.
Leave the header copy above the panel alone — the copy pass owns it.

Step 3 — the bundle README path. `bake_data` resolves `samples_dir` at :410, so decide the
rendering inside `write_bundle_readme`: if the resolved directory is inside the repository
root, print its `relative_to` form; otherwise print a fixed phrase that names no path (the
operator running the build already knows which directory they pointed at, and the note is
read by strangers). Both branches keep the existing "this script bakes whatever recordings
it is pointed at and does not judge whether they are public" sentence — the docstring at
:548-562 explains at length why that sentence is the way it is, and nothing here reopens it.

Step 4 — the host-path check. Keep it narrow and cheap: scan only the text files the builder
writes, look for a leading `/Users/`, `/home/`, or a Windows drive-and-`Users` prefix plus
`str(Path.home())`, and raise with the offending file and the matched span. The perturbation
leg writes a README containing such a path into a temp directory and asserts the check
raises — a gate nobody can fail is prose.

Step 5 — the compiled-in fragment. Pick a fragment of the bundle-only sentence with no
punctuation a minifier could re-quote or re-escape, keep the sentence itself in exactly one
place — a value in `frontend/src/lib/copy.ts`, not a literal in the `.tsx` — and put a
comment on each side naming the other. The existing
`./data` check at :510-533 and its test at tests/scripts/test_build_demo_bundle.py:333-352
are the pattern to copy, including the synthesized `assets/index.js` fixture — the fast
Python tests must not shell out to `npm run build`.

**Ready-to-paste prompt:** `agent_prompts/task-20-7-pages-demo.md`

## Wave 1 — claims made true, the instruments, readability (RR-free)

### Task 20.8 — The leak scanner checks entitlement, not shape
**Branch:** `phase-20-leak-scanner-entitlement`
**Depends on:** 20.9 (the firewall test is restructured first so its planted files live in a temp tree instead of fixed paths under the agent and observation packages; this task appends another planted leg to that same file and must land on the restructured version)
**Section refs:** C-31 — audits/review-2026-08-19/B/collated-findings.md row C-31; audits/review-2026-08-19/B/observation-firewall.md §2 F1 (the mutation table), §4 (channel coverage: "visibility gating of players/bodies (absent)"), §5 recommendation 1; audits/review-2026-08-19/B/verdicts.md claim 2 CONFIRMED P1 (the M6 repro: packets 534→564, body_views 33→249, cross-room body views 7→222, whole-suite diff EMPTY); audits/review-2026-08-19/D/cross-track-map.md row C-31; audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC7 and §4 Wave 1 row 1.1. Anchors re-verified at HEAD: eval/leak_scan.py:609-650 (`assert_packet_is_leak_clean`, signature 609-611), :626-640 (the kill/vent witness cross-check), :641-644 (the body key-set pin), :460 (`PacketRecord`), :486-556 (`_reconstruct_factory_records`, which already holds `walk_event.state` and `game_map`), :354 (`_assert_owned_tasks_match_engine_truth` — the in-repo engine-truth-cross-check precedent, `(packet, *, state, game_map)`), :189-280 (`assert_moved_players_are_witness_gated`, whose docstring at :215-217 gives "callers hold packets and events but no world state" as the reason it is NOT folded into the main scanner); engine/visibility.py:64-80 (`_visible_player_ids`, the vent filter at :78), :83-95 (`_visible_body_ids`), :130-168 (`compute_visibility_for_player`, keyword-only `observer_id`/`world_state`/`game_map`), :141-147 (a dead observer's empty entitlement); observation/service.py:298-305 (bodies copied verbatim from `visibility.visible_body_ids`), :330-361 (`_visible_players`) with the action-actor allowance at :348-356 — the review's "365-372" anchor is stale, that range is inside `_audible_events` at HEAD; eval/leak_test.py:112-158 (`_run_scripted_game`, holds `state` + `game_map`), :229-269 (the scripted sweep), :351-424 (the factory sweeps and the planted-leak self-tests); tests/observation/test_leak_property.py:240-396 (the main sweep, which holds `state` + `game_map`), :609-631 (the movement-vocabulary rationale), :674-741 (the movement sweep) and :744-819 (the deterministic non-vacuity companion); training/crew/scorer.py:1730-1744 and training/bakeoff/harness.py:1823-1837 (the champion-gate call sites, both `scan_factory_packets(...)` inside `try/except AssertionError`); tests/eval/test_replay_walk.py:733-734 and :767-768 (the four `for packet, _ in records` comprehensions that fix `PacketRecord`'s arity) and :714, :723, :749, :758 (its `_reconstruct_factory_records` calls); DESIGN.md:933 (§11.2 "the most important test") and :944 ("no field whose value should be hidden ever appears"); README.md:47 ("zero observation-firewall violations") and :74 ("the leak test walks every emitted packet recursively").
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run pytest eval/leak_test.py tests/observation tests/test_firewall.py tests/training/test_leak_gate.py -q` green, and each planted-mutation leg (M6, M1, M10, widened rooms) FAILS when the entitlement assertion alone is commented out — the PR pastes both runs.

The repo's loudest test does not test the thing it is named for. `assert_packet_is_leak_clean`
(eval/leak_scan.py:609-611) takes `(packet, engine_events)` and nothing else, so it can validate
packet SHAPE (key sets, forbidden field names), packet STRINGS (role-bearing substrings) and
WITNESS PERMISSION for `kill`/`vent` actions — but it has no world state, and therefore cannot
ask the only question that matters: was this observer ENTITLED to see these players and these
bodies? The review planted the obvious regression and measured the answer. Mutation M6 (drop the
room filter in `engine/visibility.py::_visible_body_ids`, so every undiscovered corpse is visible
to everyone) takes body views from 33 to 249 over the factory walk and passes eval/leak_test.py,
tests/observation/test_leak_property.py, tests/observation/test_service.py and
tests/test_firewall.py — with an EMPTY whole-suite diff. Zero tests in the repo catch it. M1
(every alive player visible) and M10 (the vent filter dropped) are caught only by
single-scenario unit tests in tests/observation/test_service.py — two for M1, one for M10 — and by
no gate that runs outside pytest. All numbers here are review-derived from audits/review-2026-08-19/B/verdicts.md claim 2.

That gap is load-bearing in three places at once. DESIGN.md:933 titles §11.2 "Information-leakage
test (the most important test)" and :944 asks for a version that "asserts no field whose value
should be hidden ever appears in a packet for a non-self agent" — a presence check, which is
exactly what is missing. README.md:47 advertises "zero observation-firewall violations" and :74
describes the leak test as the thing that makes the agent surface safe; the front-door rewrite
(20.12) amplifies both claims, which is why this repair lands first. And `scan_factory_packets` is
not merely a test: it is the leak gate the ML champion path runs OUTSIDE pytest
(training/crew/scorer.py:1735, training/bakeoff/harness.py:1828, both converting an
`AssertionError` into a recorded `leak_passed=False`), so a learned agent that reached bodies
differently would be admitted as champion with a total hidden-information leak. Later in this
phase the same scanner becomes the instrument that adjudicates the firewall's one sanctioned
widening — the confirm-ejects rule at 20.29, where an ejected player's role enters memory after
its meeting and never before — so the scanner has to be able to state entitlement in both
directions before that widening is drafted.

The design question this contract settles is what "independent" means. `assert_moved_players_are_witness_gated`
already states the principle in its own docstring: it takes the room sets as arguments "so the
check is INDEPENDENT of the service's own gating — a scanner that reused the code under test would
prove nothing". For entitlement the code under test is wider than the service: M6, M1 and M10 all
live inside `engine/visibility.py`'s private entity filters, so a scanner that simply called
`compute_visibility_for_player` and compared id sets would inherit the mutation and catch NONE of
the three. The ruling: the scanner takes the observer's ROOM SET from the engine
(`compute_visibility_for_player(...).visible_rooms`, the same posture the movement scanner already
uses, bounded by an independent adjacency check so a widened room rule is caught too) and
re-derives the ENTITY filters itself from `WorldState` — alive, not in a vent, in a visible room
for players; undiscovered and in a visible room for bodies. Ten lines of oracle, no duplication of
the role-asymmetric mode ruling, and every mutation the review planted bites.

Two properties of the existing scan must survive the change. The kill/vent witness allowance is
REAL: observation/service.py:348-356 adds any actor carrying an observed kill or vent action to
`visible_players` even when the actor is not in `visibility.visible_player_ids` (a vented killer
surfaces as `('p-3','ADMIN','kill')` — the review's secondary C-1 finding). That is intended
kill-attribution, so it is asserted as a NAMED allowance whose members must each pass
`_action_is_permitted_by_witness_event`, never as a silent superset. And `PacketRecord` must stay a
two-element tuple: tests/eval/test_replay_walk.py unpacks `for packet, _ in records` in four
comprehensions across two assertions (:733-734 and :767-768) and is not in this task's scope, so
the tick context rides as the SECOND element rather than a third. Nothing under `engine/`,
`observation/` or `agents/` changes: this is a gate repair, replay bytes cannot move, and there is
no lever and no record.

**Files in scope:**
- eval/leak_scan.py; (the scanner gains the tick context, re-derives entitlement, folds in the movement gate; the docstrings state what it now asserts)
- eval/leak_test.py; (the scripted sweep and the planted-leak self-tests pass the context they already hold)
- tests/observation/test_leak_property.py; (the two Hypothesis sweeps assert entitlement; the observer-class legs; the non-vacuity counter)
- tests/test_firewall.py; (the planted-mutation leg: M6, M1, M10 and a widened room rule each caught — the gate proves it can fail)
- training/crew/scorer.py; (call site only — expect a zero-line or comment-only diff)
- training/bakeoff/harness.py; (call site only — expect a zero-line or comment-only diff)
- tests/training/test_leak_gate.py; (new — the champion-gate contract pinned: same function object, positive packet count, an entitlement failure recorded as a failed gate)

**Files NOT in scope:**
- engine/visibility.py (correct on main; the scanner recomputes independently and never changes visibility — a mutation here is planted in a test, never in the tree)
- observation/service.py (no behaviour change; the vented-actor-in-`visible_players` allowance is DOCUMENTED by this task and CHANGED by none)
- agents/ (the packet consumers are untouched)
- tests/eval/test_replay_walk.py (its four `for packet, _ in records` comprehensions at :733-734 and :767-768 must keep working unchanged — that constraint shapes the record type; if they need editing, STOP and report it under Questions)
- tests/observation/test_service.py (the incidental M1/M10 catches stay exactly as they are)
- DESIGN.md and docs/architecture.md (§11.2's sketch is a historical design record and docs/architecture.md belongs to 20.20; the truth-up lands in the scanner's own docstring)
- README.md (20.12 restates the firewall claim in verifiable shape, using the wording this task's PR records)
- replays/ and any prompt template (no bytes move; template edits belong to 20.31 alone)

**Definition of done:**
- [ ] `eval.leak_scan.assert_packet_is_leak_clean` takes the tick context (engine events + `WorldState` + `Map`) as a REQUIRED argument; the `engine_events: Sequence[EngineEvent] = ()` default is gone so no caller can silently reduce the gate to shape-only, and `PacketRecord` stays a two-element tuple whose second element is the context (the PR quotes the blast-radius grep for `PacketRecord`, `assert_packet_is_leak_clean` and `assert_no_factory_packet_leaks` across the tree).
- [ ] `eval.leak_scan.assert_visible_entities_match_engine_truth` asserts, deriving the entity filters from `WorldState` and NOT from `engine.visibility`'s private helpers: the observer's engine-reported `visible_rooms` contains the observer's own room and is contained in that room plus its map neighbours; the packet's visible player ids EQUAL the set of alive, non-vented, in-visible-room players other than the observer, PLUS exactly the named witness allowance (ids whose `PlayerView.action` is `kill` or `vent` AND that pass `_action_is_permitted_by_witness_event`) — an equality, never a superset; the packet's visible body ids EQUAL the undiscovered bodies in visible rooms, with no allowance; and every `PlayerView.room` and `BodyView.room` lies in `visible_rooms`.
- [ ] Four observer classes are covered by hand-built world states in tests/observation/test_leak_property.py: a crewmate (same-room-only), an impostor (same-room-and-adjacent), a VENTED observer (the engine grants a vented observer the full room set — restated in the module docstring as a rule the scanner asserts, not an accident), and a DEAD observer (empty entitlement; any visible player or body trips).
- [ ] `assert_moved_players_are_witness_gated` is called from `assert_packet_is_leak_clean` using the context's `visible_rooms`, so the ML champion gate scans `moved_players` for the first time; the docstring at eval/leak_scan.py:215-217 that gives "no world state" as the reason it is not folded in is corrected to state what is now true.
- [ ] The planted-mutation leg in tests/test_firewall.py proves the gate can fail: M6 (`_visible_body_ids` drops the room filter), M1 (`_visible_player_ids` returns every alive player), M10 (the vent filter dropped) and a widened `visible_rooms_for_player` are each planted by monkeypatching the named symbol INSIDE the test — never by writing a file into the tree — and each is asserted to raise `AssertionError` from the scanner with a message naming the observer and the offending ids; the unmutated tree is green.
- [ ] The scripted sweep (eval/leak_test.py), both Hypothesis sweeps and the factory walk all pass the context, and the sweep whose vocabulary separates players carries a NON-VACUITY counter — at least one scanned packet whose entitled-player set is a proper subset of the living others — mirroring `scan_factory_packets`'s `bodies_seen > 0` coverage assertion; a sweep in which everyone stands in the spawn room proves nothing about M6, which is why the review called the existing sweeps' visibility coverage vacuous.
- [ ] The ML champion gate keeps its contract: `scan_factory_packets` keeps its signature and still runs outside pytest, training/crew/scorer.py and training/bakeoff/harness.py carry at most a comment-only diff, and tests/training/test_leak_gate.py pins that both call sites bind `eval.leak_scan.scan_factory_packets`, that a scan returns a positive packet count under the entitlement check, and that an entitlement `AssertionError` is recorded as a failed gate rather than escaping the run.
- [ ] `assert_packet_is_leak_clean`'s docstring leads with what the scanner asserts — shape, strings, witness permission, movement gating and ENTITLEMENT — in the shape DESIGN.md:944 describes, with one provenance line and no history narration.
- [ ] No production bytes move: `git diff --name-only` contains nothing under `engine/`, `observation/`, `agents/`, `orchestrator/` or `replays/`, and `bash scripts/verify_samples.sh` stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — verify-then-fix. Before editing, reproduce the defect: monkeypatch
`engine.visibility._visible_body_ids` to drop its room filter, run
`uv run pytest eval/leak_test.py tests/observation tests/test_firewall.py -q`, and confirm green.
Paste that into the PR beside the red run at the end. This is the evidence that the gate could not
fail; without it the fix is unfalsifiable.

Step 2 — the record type. Add a frozen dataclass `PacketContext` with `engine_events:
Sequence[EngineEvent]`, `world_state: WorldState` and `game_map: Map`, then redefine
`PacketRecord: TypeAlias = tuple[ObservationPacket, PacketContext]`. Two elements, deliberately:
tests/eval/test_replay_walk.py (out of scope) unpacks `for packet, _ in records` in four
comprehensions at :733-734 and :767-768 and must keep compiling. `_reconstruct_factory_records`
already has `walk_event.state` and `game_map` in hand at eval/leak_scan.py:542-551, and
`_run_scripted_game` has `state` + `game_map` at eval/leak_test.py:119-148 — both build the
context where they build the packet.

Step 3 — the oracle. Write `assert_visible_entities_match_engine_truth(packet, *, state, game_map)`,
mirroring the naming and signature of the existing `_assert_owned_tasks_match_engine_truth` at
eval/leak_scan.py:354. Take `visible_rooms` from `compute_visibility_for_player(observer_id=...,
world_state=..., game_map=...)` (keyword-only — the review's shorthand signature is not the real
one), bound it independently with `game_map.room_neighbors(observer.room)`, then derive the entity
sets yourself from `state.players` and `state.bodies`. Do NOT call `_visible_player_ids` or
`_visible_body_ids`, and do NOT compare against `visibility.visible_player_ids` /
`visible_body_ids`: those are the mutated symbols in M1, M6 and M10, and a scanner that reads them
catches nothing. Compute the witness allowance as a set first, assert the packet's ids equal
`entitled | allowance`, and put the allowance in the failure message so a future widening reads as
a decision rather than a mystery.

Step 4 — fold in the movement gate. With the context in hand, call
`assert_moved_players_are_witness_gated(packet, engine_events=..., visible_rooms=...)` from
`assert_packet_is_leak_clean` with `departure_visible_rooms=None` (today's service rule, already
pinned on both sides by tests/observation/test_leak_property.py:822). Then fix the docstring at
:215-217 that says the fold-in is impossible.

Step 5 — the planted mutations. Prefer `monkeypatch.setattr(engine.visibility, "_visible_body_ids",
...)` over copying a scratch tree: `compute_visibility_for_player` resolves those helpers as module
globals, so the patch reaches the SERVICE while the scanner's own oracle stays clean — which is
precisely the asymmetry the fix creates. Nothing is written into the working tree, so the
concurrent-run hazard the firewall test is being restructured to remove is not reintroduced. Build
one small helper that runs a handful of ticks and scans, and parameterize it over the four
mutations.

Step 6 — if a real counterexample appears. If the room-membership assertion or the equality trips
on the unmutated tree over the committed scripted fixtures or the factory walk, STOP: that is
either a genuine leak (a finding for the PR's Questions, not a silent weakening) or a real
allowance that must be named, justified and asserted explicitly. Do not relax an equality to a
subset to get green. Keep runtime honest — if the new sweeps push the file past its budget, mark
the heaviest test `slow` (registered in pyproject.toml) and quote the before/after wall time.

**Public types introduced:**
- `eval.leak_scan.PacketContext`
- `eval.leak_scan.assert_visible_entities_match_engine_truth`

**Ready-to-paste prompt:** `agent_prompts/task-20-8-leak-scanner-entitlement.md`

### Task 20.9 — Import-linter covers the whole tree; the firewall test plants in a temp tree
**Branch:** `phase-20-import-contracts-coverage`
**Depends on:** none (root)
**Section refs:** C-32 + C-34 + C-125 [D-VERIFIED] — audits/review-2026-08-19/B/observation-firewall.md §2 F2; audits/review-2026-08-19/B/tests-ci-tooling.md §2 P1-1 + §2 P2-15 + §6 recommendations 1 and 8; audits/review-2026-08-19/B/verdicts.md (the C-32 verdict, "Analyzed 90 files … Contracts: 4 kept, 0 broken", and the C-34 verdict, "2/12 false BROKEN"); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 rows 1.2 + 1.3 and §3 claim-table row 3 ("agents cannot import engine directly or transitively (import-linter enforced)" — UNDERMINED); anchors re-verified at HEAD `b809b19c` by the drafting session: `.importlinter:2-8` (six root packages; `orchestrator`/`api`/`eval`/`scripts`/`experiments` absent, `include_external_packages` unset), `tests/test_firewall.py:21-23`, `:41-47`, `:142-144`, `:213-215` (five fixed plant paths written into the live checkout, each removed in a bare `finally` at `:36-37`, `:60-62`, `:156-157`, `:224-225`), `:90` (the repo-wide `agents/` AST scan bans `numpy`/`torch` only), `:160-169` (the in-code comment that names the invisible `agents -> orchestrator -> engine` chain and fixes it for one subpackage), `:172-174` (the learned-only rglob), `agents/tactical/learned/__init__.py:19-21` (the same posture claim), `.gitignore:1-43` (no `_firewall*` pattern; `git check-ignore -v agents/_firewall_bad_import.py` exits 1), `CONTRIBUTING.md:60-62` ("it runs the same checks CI runs") and `:79-80` (the transitive-firewall invariant) against `.github/workflows/ci.yml:90-160` (the `frontend-e2e` Playwright job) and `scripts/check.sh:30-35` (why the journey is deliberately excluded), `.github/workflows/campaign-tier.yml:23-28` (the weekly campaign tier), `eval/validity.py:95` (`from api import replay_loader`), `eval/leak_test.py:60` + `eval/determinism_test.py:14` (`from tests._helpers.world_state import …`), `README.md:74` (the claim 20.12 restates)
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run lint-imports` prints `Analyzed 149 files, 741 dependencies` (HEAD prints `Analyzed 89 files, 379 dependencies`) with `Contracts: 4 kept, 0 broken`, both lines quoted in the PR; the three planted probes each print `Contracts: 2 kept, 2 broken` naming the chain; `uv run pytest tests/test_firewall.py -q` green with `git status --porcelain` empty afterwards; and `uv run pytest tests/test_firewall.py -q & for i in $(seq 12); do uv run lint-imports --no-cache; done` prints zero BROKEN (review-measured 2/12 false BROKEN at HEAD).

The repository's loudest architectural claim is enforced over 89 of its 383 tracked
`.py` files. `.importlinter:2-8` lists six root packages — `agents`, `engine`, `llm`,
`meetings`, `observation`, `training` — and grimp builds no nodes for anything else, so
the traversal dies at the first hop into a package it does not know. The review planted
`agents/_probe_orch.py` containing `import orchestrator.game` and got `Contracts: 4 kept,
0 broken` with `scripts/check.sh` fully green
(audits/review-2026-08-19/B/verdicts.md, the C-32 verdict; the same evidence in
audits/review-2026-08-19/B/observation-firewall.md §2 F2). The drafting session reproduced
it exactly at HEAD in a scratch copy: `Analyzed 90 files, 379 dependencies. Contracts: 4
kept, 0 broken`. `orchestrator/game.py:71-81` imports seven `engine` modules,
`eval/leak_scan.py:38-47` and `api/replay_loader.py` likewise, so `agents -> orchestrator
-> engine`, `agents -> api -> engine` and `agents -> eval -> engine` are all live
back-channels that no gate in this repo can see. The blind spot is known and written down
in-repo (`tests/test_firewall.py:160-169`) and was closed for exactly one subpackage —
`agents/tactical/learned/` — by a source scan; the top-level `agents/` scan at `:90` bans
only `numpy` and `torch`. Meanwhile `README.md:74`, `CONTRIBUTING.md:79-80`,
`docs/architecture.md:106` and `docs/reading-guide.md:30` all state the transitive
guarantee uncaveated, and the front-door rewrite is about to amplify it.

The fix is four lines of config and it makes the claim TRUE rather than softening it. The
drafting session measured the widened configuration against unmodified sources at HEAD:
`Analyzed 149 files, 741 dependencies. Contracts: 4 kept, 0 broken` — no existing import
breaks, and the run costs ~0.17 s against ~0.19 s today, so the gate pays nothing. The 149
reconciles exactly: 148 tracked non-test `.py` files under the ten roots (agents 22,
engine 10, llm 9, meetings 7, observation 6, training 35, orchestrator 8, api 8, eval 25,
scripts 18) plus one synthetic node grimp mints for `scripts`, which carries no
`__init__.py` and is therefore a namespace package (confirmed by a two-root control:
`api` + `engine` analyses exactly 18 files, `scripts` + `engine` analyses 29 for 28
files). With the roots widened, the planted probe becomes loud: `import orchestrator.game`
under `agents/` prints `Contracts: 2 kept, 2 broken` with the chain spelled out —
`agents._probe_orch -> orchestrator.game (l.1)` then `orchestrator.game -> engine.world
(l.81)` — and `import api.main` and `import eval.leak_scan` break the same two contracts
through their own chains. What stays outside the graph after this task is small, nameable
and closed by the second layer below: `experiments/` (49 tracked `.py`, the frozen
investigation tier that imports the inner packages by design —
`experiments/__init__.py:6-8`), `tests/` (184), and two loose generators
(`audits/workflows/extract_gameplay_facts.py`, `design/phase-12/gen_map_reference.py`).

The same file carries a second defect, and it is the one that costs time today.
`tests/test_firewall.py` plants five files at fixed paths INSIDE the live checkout
(`:21-23`, `:41-47`, `:142-144`, `:213-215`), each cleaned up in a bare `finally` rather
than a fixture. Any second process touching the checkout during those few seconds sees the
repository's most alarming possible output: the review measured 2 of 12 concurrent
`lint-imports` runs printing `Agents must not import engine BROKEN` against modules that
do not exist (audits/review-2026-08-19/B/tests-ci-tooling.md §2 P1-1; the same 2/12 in
audits/review-2026-08-19/B/verdicts.md's C-34 verdict). Worse, a SIGKILL or Ctrl-C during
the subprocess leaves the plant behind, and `.gitignore` has no `_firewall*` pattern
(`git check-ignore -v agents/_firewall_bad_import.py` exits 1 at HEAD), so `git add -A`
commits a file containing `import engine` and turns a flake into a permanently red
architectural gate. It also caps the cheapest available speed-up: the parallel-suite task
later in this phase cannot run `pytest -n auto` while five process-independent plants
collide worker-to-worker. The plant-detect-cleanup SHAPE is right and is kept —
"a gate that cannot fail is not a gate" (`tests/test_firewall.py:138-139`); only the location
moves.

Scope discipline: no source import moves in this task. If the widened roots surface a real
violation, that is a finding for the PR's Questions, not a silent fix — the candidate
edges the drafting session already looked at are `eval/validity.py:95`
(`from api import replay_loader`, legal: `eval` and `api` are both consumer-layer) and
`eval/leak_test.py:60` / `eval/determinism_test.py:14` importing `tests._helpers`
(invisible to grimp, since `tests` is not a root). `README.md` is 20.12's file; that task
restates the front-door claim in the wording this PR's measured output records. No prompt
template moves anywhere in this phase outside the single prompt-set bump, and this task
records nothing: it is a $0, committed-bytes-untouched config-and-test change.

**Files in scope:**
- .importlinter; (add orchestrator, api, eval, scripts to root_packages; contracts unchanged in intent)
- tests/test_firewall.py; (plant into a tmp_path copy with a generated linter config; the repo-wide AST scan covers agents/ at top level for orchestrator/api/eval imports)
- .gitignore; (the `_firewall*` plant pattern as a belt-and-braces guard)
- CONTRIBUTING.md; (the 'same checks CI runs' sentence made true: check.sh + the Playwright job)
- tests/experiments/test_torch_probe_excluded.py; (the second live-tree plant moves to tmp_path)

**Files NOT in scope:**
- README.md (20.12 restates the claim in verifiable shape, using the wording this task's PR records)
- agents/, orchestrator/, api/, eval/ source (no import moves; if widening the roots surfaces a real violation, STOP and report it under Questions)
- eval/leak_scan.py + eval/leak_test.py (the entitlement-scanner task owns the dynamic firewall; this task is the static one)
- docs/architecture.md + docs/reading-guide.md (the enforcement paragraphs are restated by their owning tasks from this PR's recorded wording)
- .github/workflows/ci.yml + scripts/check.sh (the job set is described in CONTRIBUTING, not changed; the parallel-suite task owns the pytest invocation)
- experiments/ (stays out of root_packages: 49 files of frozen investigation code that imports the inner packages by design; it is covered by the agents-side source scan instead)

**Definition of done:**
- [ ] Verify-then-fix, before any other edit: the widened root list is run once against unmodified sources (a scratch config plus `lint-imports --config`, so the repo is not edited yet) and the verdict recorded in the PR. The drafting session measured `4 kept, 0 broken`; if a real violation appears instead, STOP and report it under Questions rather than moving any import.
- [ ] `.importlinter` `root_packages` gains `orchestrator`, `api`, `eval`, `scripts`; the four contract sections are unchanged; `uv run lint-imports` analyses 149 modules (148 tracked non-test `.py` under the ten roots plus the synthetic node for the `__init__.py`-less `scripts` namespace package) against 89 at HEAD, and all four contracts still read KEPT. Both `Analyzed …` lines and both `Contracts: …` lines are quoted in the PR.
- [ ] A planted `agents/_probe_orch.py` containing `import orchestrator.game` — and, separately, `import api.main` and `import eval.leak_scan` — is reported BROKEN by `lint-imports`, with the transitive chain named; demonstrated in the PR and pinned as a parameterized planted leg in `tests/test_firewall.py` that runs against the temp copy, so a future narrowing of `root_packages` fails the suite instead of passing it silently.
- [ ] `tests/test_firewall.py` writes NOTHING under the checkout: all five plant sites move into a `tmp_path` copy of the source tree with the linter run there, cleanup happens in a `yield` fixture rather than a bare `finally`, and no path built from the repo root is passed to `write_text` anywhere in the file (assert by reading the diff; `git status --porcelain` is empty immediately after `uv run pytest tests/test_firewall.py`).
- [ ] The copy's linter config is DERIVED from the committed `.importlinter` — parsed, with only `root_packages` rewritten to the packages present in the copy — never a second hand-written copy of the contract sections, so a fifth contract added later is exercised by the planted legs automatically. The PR states which mechanism invokes the linter from the temp cwd.
- [ ] Concurrency pin, recorded in the PR: `uv run pytest tests/test_firewall.py -q` running while 12 serial `uv run lint-imports --no-cache` invocations poll prints zero BROKEN (the review measured 2/12 false BROKEN at HEAD). The rewritten legs are also worker-independent, so the later parallel-suite task inherits no fixed-path collision.
- [ ] The top-level `agents/` AST scan (`tests/test_firewall.py:90`) widens from `{numpy, torch}` to also ban `orchestrator`, `api`, `eval`, `scripts`, `experiments`, `audits`, `design` and `tests` — the second, grimp-independent layer — and a covering assertion pins the pair: every top-level directory holding at least one tracked `.py` file is either a `root_packages` entry read from the committed `.importlinter` or a member of the ban set, so a new top-level package must join one of the two lists to land. Both the widened scan and the covering assertion are green at HEAD (verified: no file under `agents/` imports any banned name today) and both have a planted-failure leg.
- [ ] `.gitignore` carries a `_firewall*` pattern with a one-line comment saying it is residue insurance from older checkouts, not a licence to plant in-tree; `git check-ignore -v agents/_firewall_bad_import.py` now exits 0.
- [ ] `CONTRIBUTING.md:60-62` states exactly what CI runs beyond `check.sh`: the `frontend-e2e` Playwright journey (`.github/workflows/ci.yml`, deliberately excluded from the script per `scripts/check.sh:30-35`, runnable locally with `cd frontend && npm run e2e`), and one clause noting the campaign tier is in neither — it runs weekly on `main` from `.github/workflows/campaign-tier.yml`. The invariant bullet at `:79-80` is left as written, and the PR records why it is now true as written.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — measure before you edit. Write the widened root list into a scratch file outside
the repo and run `uv run lint-imports --no-cache --config <scratch>.ini` from the repo
root; that gives you the before/after numbers without a dirty tree. One trap the drafting
session hit: the literal line `    training` appears twice in `.importlinter` — once in
`root_packages` and once as the forbidden module of the second contract — so a blind
`sed` substitution silently widens a CONTRACT and prints two phantom BROKEN verdicts. Edit
`root_packages` by hand.

Step 2 — the temp tree. Copy only `*.py` (148 files, ~4.4 MB, well under a second) for the
ten root packages into a `tmp_path_factory` directory built once per module, then plant
and unplant per test through a `yield` fixture. grimp parses ASTs and never imports, so no
data files, weights or `__pycache__` need to travel. Run the linter with the copy as cwd.
Two invocations both verified working from a temp cwd: `uv run --project <repo_root>
lint-imports --no-cache --config <tmp>/.importlinter` (the plain `uv run` of today fails
there — it would look for a project at the temp path), or resolve the console script
directly with `shutil.which("lint-imports")` falling back to `Path(sys.executable).parent
/ "lint-imports"`, which skips uv's env resolution entirely. Whichever you choose, fail
loudly when the executable is missing; a firewall test that silently skips is worse than
the flake it replaced.

Step 3 — the copy's config. Read the committed `.importlinter` with `configparser`,
replace only the `root_packages` value with the packages actually present in the copy, and
write it into the copy. Never re-type the contract sections in the test file.

Step 4 — the source-scan layer. `_agent_source_files()` and
`_learned_package_source_files()` currently hard-code the repo root; give both a root
parameter defaulting to the repo so the real-tree assertions are unchanged and the planted
legs can point at a two-file temp skeleton (no copy needed for the AST scans at all). For
the covering assertion, `git ls-files` is established practice in this repo
(`scripts/verify_ml_evidence.py` uses it as an inventory source); derive the top-level
directory set from tracked `*.py` paths and compare against `root_packages` read from the
committed config plus the ban set.

Step 5 — the prose. CONTRIBUTING's fix is one sentence plus one clause, not a rewrite: CI
runs `check.sh` verbatim (with `AILIBI_SKIP_FRONTEND=1` because a parallel job owns the
one frontend build), and adds the Playwright journey; the campaign tier is weekly and in
neither. Keep the file's voice — short, blunt, second person.

**Ready-to-paste prompt:** `agent_prompts/task-20-9-import-contracts-coverage.md`

### Task 20.10 — The corpus acceptance gate rejects a truncated replay
**Branch:** `phase-20-truncation-gate`
**Depends on:** none (root)
**Section refs:** register C-6 in audits/review-2026-08-19/B/collated-findings.md (P1, "reconstruct_episode reads a corrupted replay as a legitimate truncation"); audits/review-2026-08-19/B/training-ml.md §3 F1 (P1, VERIFIED — the `and not truncated` guard, with the seed-1000 repro); audits/review-2026-08-19/B/verdicts.md:204-228 (the C-6 adversarial verdict — PARTIALLY-TRUE: mechanism CONFIRMED, the recorder-lock-race CAUSE REFUTED, and the NEW worse instance named at `eval/validity.py`); audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC7 ("gates validate shape, not entitlement") and §4 Wave 1 item 1.4 (back-port the anchor_study check; measurement = the corrupt fixture is rejected by `validity_gate.py`); audits/audit-phase-20-planning.md §3 Wave 1 ("the corpus gate rejects truncation"); anchors re-verified at HEAD `b809b19c`: eval/validity.py:491-536 (`check_all_games_reach_game_over`; :509 the only truncation-adjacent violation, :517-518 the winner cross-check skipped when `reconstructed_winner is None`, :529-535 the summary + facts), training/rollout.py:652-663 (the cross-check with `and not truncated` at :656) and :23-32 (the "Silent truncation is structurally unreachable" docstring claim), training/anchor_study.py:627-646 (the correct three-part check, the back-port source), scripts/validity_gate.py:3 ("the eight composed checks" — the gate reports ten) and :19-21 (the exit-code contract), orchestrator/game.py:1776 (`TICK_BUDGET_REACHED` returns WITHOUT `record_game_end`) vs :1838-1844 (`record_game_end` fires only after a `GameOverEvent`), training/README.md:240 (§6 item 5, the recorder lock-race label the review refuted as this defect's cause)
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run python scripts/validity_gate.py` over each of `replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i`, `replays/ml_corpus/9p2i` still exits 0 with every check PASS (300 committed games, gate output quoted in the PR); the truncated fixture exits 1 with `all_games_reach_game_over` as its ONLY failing check and `truncated_replay` in the violation text; `uv run pytest tests/eval/test_validity.py tests/training/test_rollout.py tests/scripts/test_validity_gate_cli.py -q` green.

The corpus acceptance gate accepts a replay it should reject. Drop the trailing
tick rows of a committed replay while leaving its `game_over` row in place, and
`eval/validity.py`'s `check_all_games_reach_game_over` reports PASS — because the
recorded row is still there (`check.game_over_tick is not None`, so the :509
violation never fires) while the engine's reconstruction never reaches
`GAME_OVER` (`reconstructed_winner is None`, so the :517-518 forged-label
cross-check is skipped by its own `is not None` guard). Re-verified at HEAD
`b809b19c` on a scratch copy of `replays/samples/9p2i/replay-seed-12.jsonl` with
its last tick row removed: the WHOLE gate exits 0, all ten checks PASS, and
`all_games_reach_game_over` prints `1/1 games reached game_over with a
consistent win condition` for a game whose reconstruction stopped a tick short.
Every state hash still verifies — dropping trailing rows shortens the walk
without breaking the chain — so nothing downstream catches it either. This is
the corpus acceptance gate, sitting directly under the byte-reconstruct claim
the front door is about to feature (`audits/review-2026-08-19/D/FINAL-synthesis.md`
§4 Wave 1 item 1.4), and it is the RC7 pattern in miniature: the check validates
that a row is present, not that the walk earned it.

`training/rollout.py` carries the same inversion in the form the review found
first. At :655-658 the winner cross-check is guarded by `and not truncated` —
disabled in exactly the case that needs it. Re-verified at HEAD on the same
fixture: intact, `reconstruct_episode` returns `outcome=IMPOSTORS truncated=False
winner=IMPOSTORS complete=True` over 20 tick frames; with one tick row dropped it
returns `outcome=TICK_BUDGET truncated=True winner=None complete=False` over 19
tick frames and raises nothing, matching the review's seed-1000 repro
(`audits/review-2026-08-19/B/training-ml.md` §3 F1: 25 ticks → 23, and → 14 with
ten rows dropped). The guard is vestigial and provably so: it dates from when
`EpisodeBoundary` still had `first_meeting`, a boundary that legitimately
truncated a winner-bearing replay; Task 19.19 retired the boundary and left the
clause, and `EpisodeBoundary` is now `Literal["full_game"]` alone
(training/rollout.py:73). The module docstring at :29-31 promises "Silent
truncation is structurally unreachable"; the bytes say otherwise.

Two corrections the contract inherits from the adversarial verdict, so this task
does not re-publish a refuted claim. First, the CAUSE is not the recorder: the
`record_ml_corpus.sh` mutex guards `MANIFEST.md` only, each seed lands by an
atomic `mv -f` from a private stage, and `orchestrator/replay.py` flushes every
row — the lock-race labelled at `training/README.md:240` cannot produce this byte
shape. The reachable routes are an interrupted direct tournament writing into a
set dir, a bad copy, or a hand edit; the fix is worth making because the gate is
what admits foreign bytes, not because a live producer is corrupting them today.
Second, the blast radius through `reconstruct_episode` is narrow: every caller
(`training/env.py:719`, `training/bakeoff/harness.py:717`,
`training/crew/scorer.py:942`, `training/coevo/rollout.py:210`) reconstructs a
replay it wrote seconds earlier, and the reward channel already refuses to score
an incomplete episode. The `eval/validity.py` instance is the P1 — it is the one
that reads committed corpus bytes.

The correct check already exists in this repo, un-back-ported. `training/anchor_study.py:627-646`
rejects the same bytes with three explicit clauses (no terminal `game_over`
winner; the reconstructed walk never reached `GAME_OVER`; reconstructed winner
disagrees with the recorded one), raising `CorpusWalkError: seed …: the
reconstructed walk never reached GAME_OVER (truncated tick stream)`. Back-port
its semantics into the two sites that lack them. The check cannot false-positive
on a legitimate recording: `orchestrator/game.py:1776` returns
`TICK_BUDGET_REACHED` WITHOUT calling `record_game_end`, and :1838-1844 writes
the `game_over` row only after the engine fires a `GameOverEvent`, so "a
`game_over` row exists AND the reconstruction never reached `GAME_OVER`" is
unconditionally corruption, and a genuinely tick-budget-capped rollout has no
`game_over` row to trip the new clause.

Craft rule 2 governs the fixture, and it is the part this task is easiest to get
wrong. A truncation that removes a tick row carrying a meeting trigger already
turns seven other checks red today (verified at HEAD on both
`replays/samples/9p2i/replay-seed-0.jsonl` and
`replays/ml_corpus/9p2i/replay-seed-1000.jsonl`), so a fixture of that shape
would "fail the gate" before the fix and prove nothing. The fixture must be a
replay whose trailing tick rows come AFTER its last meeting row — 16 of the 50
committed 9p2i samples end `tick, tick, tick, game_over`, and `replay-seed-12`
is the verified green-today case — so that at HEAD the gate is fully PASS and
after the fix `all_games_reach_game_over` is the ONLY failing check.

**Files in scope:**
- eval/validity.py; (the truncation check: a replay whose last record is not game_over, or whose game_over winner disagrees with the reconstructed final state, FAILS the gate)
- training/rollout.py; (the same check in reconstruct_episode; the `and not truncated` guard inverted to what the docstring promises)
- tests/eval/test_validity.py; (the truncated-fixture rejection)
- tests/training/test_rollout.py; (the corrupt-as-truncation repro becomes a failing case)
- scripts/validity_gate.py; (exit code + message for the new failure class)
- tests/scripts/test_validity_gate_cli.py

**Files NOT in scope:**
- replays/ (the committed sets are intact — the gate must stay green on all four, pinned; no replay byte moves)
- training/anchor_study.py (the reference implementation is read, not edited)
- eval/win_condition_selfcheck.py (the `WinConditionSelfCheck` shape and its predicate are reused as-is)
- training/bakeoff/harness.py, training/crew/scorer.py, training/bakeoff/goodhart.py (gate consumers — grep them for blast radius, edit none)
- scripts/measure_baseline.py (shares the loaders; the R-gate measurement is untouched)
- tests/training/_goldens/finalist_eval_pins.json (a record of closed-campaign gate outcomes; if the new clause would move a pinned failing-check list, stop and report rather than re-pinning)
- agents/strategic/prompts/ (no prompt template moves in this phase outside the single prompt-set bump)

**Definition of done:**
- [ ] `check_all_games_reach_game_over` fails a game whose recorded `game_over` row is present while the reconstruction never reached `GAME_OVER`, and fails a game whose recorded `game_over` row carries no winner; both violations carry the reason token `truncated_replay` plus the seed, mirroring `training/anchor_study.py:627-646`. Pinned by new cases in `tests/eval/test_validity.py` beside `test_all_games_reach_game_over_fails_without_game_over`.
- [ ] The check's summary and `facts["games_reached_game_over"]` count reconstruction-confirmed terminals, so a truncated game can never be summarised as having "reached game_over"; asserted in `tests/eval/test_validity.py`. Blast-radius grep for `games_reached_game_over` recorded in the PR (at HEAD the only hit is its own definition).
- [ ] An end-to-end fixture: a copy of `replays/samples/9p2i/replay-seed-12.jsonl` with its trailing tick row dropped (the `game_over` row kept) is REJECTED by `run_validity_gate`, and `report.failing_checks() == ("all_games_reach_game_over",)` — the gate-can-fail proof that the fixture is otherwise green. The same fixture is pinned through the CLI in `tests/scripts/test_validity_gate_cli.py`: exit code 1 and `truncated_replay` in the rendered output.
- [ ] All four committed sets still pass unchanged: `run_validity_gate` green over `replays/samples/{4p1i,9p2i}` and `replays/ml_corpus/{4p1i,9p2i}` (300 games), with the existing 9p2i/4p1i reproduction tests in `tests/eval/test_validity.py` untouched and the gate output for all four quoted in the PR.
- [ ] `reconstruct_episode` raises `RolloutReconstructionError` on the same fixture instead of returning `outcome="TICK_BUDGET"` silently: the cross-check no longer carries `and not truncated`, and fires when a recorded `game_over` winner exists and the walk either truncated or disagrees. Pinned by a new case in `tests/training/test_rollout.py` beside `test_reconstruction_fails_loud_on_state_hash_drift`.
- [ ] The legitimate tick-budget path is proven unaffected: a capped episode (no `game_over` row) still reconstructs as `outcome="TICK_BUDGET" truncated=True` without raising — `tests/training/test_scenarios.py::test_scenario_episodes_score_dense_while_the_terminal_gate_refuses` and `tests/training/test_env.py` stay green, and the PR names them as the guard against a false positive.
- [ ] The prose matches the bytes: `training/rollout.py`'s module docstring no longer claims silent truncation is structurally unreachable as a property of the boundary alone but names the check that enforces it, and `scripts/validity_gate.py:3` says ten composed checks (the gate reports ten) with its exit-code paragraph naming the truncated-replay failure class. One trailing provenance line at most, per Craft rule 1.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — reproduce before editing. Copy `roster.json` plus one replay into a
scratch dir, drop the LAST tick row (keep every other row, including
`game_over`), and run `uv run python scripts/validity_gate.py <dir>`. On
`replay-seed-12` this exits 0 with ten PASS lines at HEAD; on `replay-seed-0` it
exits 1 for seven unrelated checks because the dropped row carried a meeting
trigger. Only the first shape proves the new check bites. Record both in the PR.

Step 2 — `eval/validity.py`. The data you need is already on
`_GameReconstruction`: `win_check.game_over_tick` / `win_check.winner` come from
the RECORDED `game_over` row (`WalkComplete.game_end`), while
`reconstructed_winner` / `reconstructed_reason` come from the engine's own
`GameOverEvent`. The gap is that the existing cross-check is guarded on
`reconstructed_winner is not None`. Add a clause for the complementary case
before it — a recorded terminal row with no reconstructed terminal state — and a
clause for a recorded row with `winner is None`. Keep the violation strings in
the file's established `f"seed {game.seed}: …"` shape and put the reason token in
them; one module-level constant is enough, not a taxonomy.

Step 3 — `training/rollout.py`. The literal edit the review specifies: drop
`and not truncated`, and raise when `game_end.winner is not None and (truncated
or game_end.winner != winner)`. Widen the message so the truncation case reads
as truncation rather than as a winner mismatch against `None`. Nothing else in
the reconstruction moves; `EpisodeRollout.__post_init__` and `complete` already
hold the terminal-shape invariant and are not touched.

Step 4 — the tests. `tests/eval/test_validity.py` has `_mini_set(tmp_path,
seeds=…)` and `tests/scripts/test_validity_gate_cli.py` has `_mini` plus
`_rewrite_lines(path, transform)` (return `None` to drop a line) — reuse them
rather than writing a fourth copy of the fixture recipe. The unit-level cases can
build `_GameReconstruction` directly through the existing `_recon` / `_win_check`
helpers; the end-to-end case needs a real dropped row so the walk actually stops
short.

Step 5 — blast radius before scope, per Craft rule 6. `run_validity_gate` is the
champion-acceptance gate at `training/crew/scorer.py:1692`,
`training/bakeoff/harness.py:1757` and `training/bakeoff/goodhart.py:455,:1582`.
Those paths are frozen and run no campaign in this phase, but grep them, confirm
no test drives them over a truncated directory, and say so in the PR. If any
committed golden or report pin moves, stop and report instead of re-pinning it.

**Public types introduced:**
- `eval.validity.TRUNCATED_REPLAY_REASON`

**Ready-to-paste prompt:** `agent_prompts/task-20-10-truncation-gate.md`

### Task 20.11 — Kill, report and sabotage are illegal from inside a vent
**Branch:** `phase-20-in-vent-guards`
**Depends on:** none (root)
**Section refs:** C-1 [CONFIRMED, P1] — audits/review-2026-08-19/B/engine.md §2 P1 F1 (the three-probe repro: kill, report and sabotage all resolve from inside a vent) and audits/review-2026-08-19/B/verdicts.md claim 1 (the full code-path read, three failed refutation attempts, the framing correction on the mask, the "committed replays unaffected" confirmation); the fix is roadmap row 1.5 of audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 1. Anchors re-verified at HEAD: engine/rules.py:56 `resolve_kill` (role, target-role, cooldown, same-room — no `in_vent`), :182 `resolve_report` (body-room only), :225 `resolve_sabotage` (role + not-already-active) against the four rules that DO guard — engine/tick.py:243 move, :280 do_task, engine/rules.py:209 `resolve_emergency_meeting` ("cannot call emergency meeting while in vent"), :254 `resolve_repair_sabotage` ("cannot repair sabotage while in vent"); engine/rules.py:64-70, the friendly-fire guard's own defense-in-depth argument, which this task extends to `in_vent` (the review cites :60-66; the true anchor at HEAD is :64-70); engine/rules.py:102-107 `resolve_vent` (impostor-only, so an in-vent actor is always an impostor) and engine/tick.py:530-536 `_apply_wait`; engine/tick.py:601 (`ActionRejectedError` → `ActionRejectedEvent`, the conversion the mask property test reads); engine/visibility.py:78 (`not player.in_vent` — the vented are hidden from others and never blinded themselves); training/env.py:213-223 (the mask's "a faithful mirror the property test pins against the real engine" docstring), :288-298 KILL, :322-329 REPORT, :341-350 SABOTAGE (whose comment asserts "no location or in-vent requirement"); tests/training/test_env.py:339-374 `test_mask_legality_against_engine` (8 seeds, BOTH directions asserted); tests/engine/test_tick.py:929 and :987 (the vent-exit allowance and the unconnected-destination rejection) and :488 `test_vent_sabotage_and_passive_effects_apply` (the ONE existing test the ruling turns red: it queues `vent` then `sabotage` for the SAME impostor p-3 in one batch and asserts `events[:2] == ["VentEntered", "SabotageStarted"]` at :531) and :1158 `test_emergency_rejects_actor_in_vent`; agents/tactical/impostor_policy.py:304 and agents/tactical/learned/forward.py:323-325 (the two shipped in-vent short-circuits); observation/service.py:348-356 (the `visible_players` allowance the review logs as its P2 secondary finding — the review's :365-372 anchor has moved); DESIGN.md:332-338 §3.4 and :359 §3.6 ("the engine is the single source of truth"); the in-vent census over committed bytes in audits/review-2026-08-19/B/verdicts.md claim 3 (`impostor_ticks=2461  in_vent=130` across all 50 committed 9p2i seeds).
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run pytest tests/engine/test_rules.py tests/training/test_env.py -q` green (the three new rejections, the exhaustive in-vent action table, and the mask-versus-engine property test over all 8 seeds); `bash scripts/verify_samples.sh` reports 100/100 committed samples clean; `uv run pytest -m campaign -q` green, with the PR recording that no pinned ML value moved.

The engine is the project's declared single source of truth for the rules (DESIGN.md:359),
and on three of them it is not. `resolve_kill`, `resolve_report` and `resolve_sabotage`
never look at `actor.in_vent`, while the four sibling rules that share the same physical
premise all do — move and do_task reject it in `engine/tick.py`, emergency and repair
reject it in `engine/rules.py` two and three functions away from the gap. The review
reproduced all three from a live state (B/engine.md §2 F1: `['Killed','TickAdvanced']`,
`['MeetingTriggered']`, `['SabotageStarted','TickAdvanced']`, each with
`killer in_vent: True`), and its refutation pass found no compensating guard anywhere:
no orchestrator or agent-boundary check (`grep -rn in_vent orchestrator/` returns only
`seeder.py:186`), no test covering the three cases, and no design ruling — DESIGN.md:334
lists the kill preconditions as role, crew target, same room and cooldown, and says
nothing about acting from inside a vent. This is an unruled gap, not an intentional
mechanic.

Combined with `engine/visibility.py:78` — which hides the vented from everyone else but
never restricts a vented *observer* — the gap composes into a strictly dominant impostor
line: see the whole room, never appear in anyone's `visible_players`, kill on cooldown,
stay inside, then open the meeting yourself. This is exactly the argument
`engine/rules.py:64-70` already makes for the friendly-fire guard — "a buggy or future
LLM-driven policy must not be able to" break the rule — simply never applied to
`in_vent`, which leaves rule enforcement load-bearing on agent code. Today it is latent
and the review confirmed it: both shipped policies take an in-vent branch before any kill,
body or sabotage logic (`agents/tactical/impostor_policy.py:304`,
`agents/tactical/learned/forward.py:323-325`), so no committed replay, eval number or ES
artifact is contaminated and this task is re-record-free. The forward risk is concentrated
in `training/`: `build_action_mask` mirrors the engine and therefore *advertises* kill,
report and sabotage as engine-legal from inside a vent (the review's repro3 printed
`ENGINE-LEGAL while vented: ['kill','sabotage','vent','wait']`), and the mask is not
hypothetical machinery — `training/bakeoff/policy_es.py:292` scores every
`mask.submission_legal` intent with no in-vent short-circuit of its own. The next policy
that samples the mask rather than the hand-written option menu can discover the untraceable
line and silently invalidate any impostor-side balance measurement taken with it.

The ruling this contract records is total rather than three patches: from inside a vent the
only legal actions are `vent` and `wait`. Sabotage is decided explicitly and ruled ILLEGAL.
Its remoteness is not the question — `resolve_sabotage` has no room check and that stays
true — the question is whether an actor with no physical presence may act at all, and the
engine's own answer everywhere else is no, including for `repair_sabotage`, sabotage's
mirror image. Leaving it legal would hand a mask-sampling policy a global action that costs
zero alibi exposure, from the one state in which the actor is absent from every other
agent's perception. `training/env.py` moves in the same commit and for a mechanical reason,
not a stylistic one: `test_mask_legality_against_engine` asserts both directions —
masked-legal implies engine-accepts *and* masked-illegal implies engine-rejects — so either
half alone turns the repo's own mirror gate red. That two-way pin is the finding's own
safeguard and must be kept working, not worked around.

Nothing else moves. This is not a lever: the rule ships unconditionally, with no
`AILIBI_*` gate and nothing to register in the substrate stamp. No prompt template is
touched. `observation/service.py` is read as evidence and left alone, but the PR should
note the consequence, because the leak-scanner entitlement work reads the same surface:
`_visible_players` (:348-356) admits an actor carrying an observed action even when
visibility excluded them, and after this task the only observed action that can still
surface a vented player is the `vent` sighting itself — which DESIGN.md:336 makes
observable by design. The "vented players are invisible" invariant goes from leaky to
exactly-one-documented-exception.

**Files in scope:**
- engine/rules.py; (three `if actor.in_vent: raise ActionRejectedError(...)` guards matching :209/:254)
- tests/engine/test_rules.py; (the three rejections + the existing in-vent allowances pinned)
- training/env.py; (the action mask excludes kill/report/sabotage while in_vent)
- tests/training/test_env.py; (mask==engine still green; the in-vent row asserted)
- tests/engine/test_tick.py; (ONLY to repair `test_vent_sabotage_and_passive_effects_apply` at :488, whose same-batch vent-then-sabotage the ruling makes illegal; the vent-exit tests at :929/:987 and `test_emergency_rejects_actor_in_vent` at :1158 stay untouched)
- DESIGN.md; (§3.4 kill preconditions gain 'not in a vent' — a one-line truth-up, historical content untouched)

**Files NOT in scope:**
- agents/tactical/ (the FSM and the compact learned forward pass already short-circuit on `in_vent`; the engine guard is the defense-in-depth layer beneath them, not a replacement)
- observation/service.py (the vented-actor-in-`visible_players` allowance at :348-356 is read as evidence and reported in the PR, never edited here)
- training/bakeoff/, training/crew/, experiments/lab/ (mask consumers — grep-verified and re-run, not edited)
- orchestrator/replay.py (this is an unconditional rule, not a lever: there is no resolver and nothing to register in the substrate stamp)
- agents/strategic/prompts/ (no task in this phase edits a game prompt template except the single prompt-set bump)
- replays/ and replays/samples/ (no re-record; byte-identical reconstruction is the gate, not an output)

**Definition of done:**
- [ ] `engine.rules.resolve_kill`, `resolve_report` and `resolve_sabotage` each reject an in-vent actor with `ActionRejectedError`, the guard placed immediately after the function's `_get_live_player` call so it reads before the role and room checks — the shape `resolve_emergency_meeting` (:209) and `resolve_repair_sabotage` (:254) already use — and each message names the rule it enforces rather than the symptom.
- [ ] Three new tests in `tests/engine/test_rules.py` pin the rejections from states where every OTHER precondition is satisfied — an impostor off cooldown with a living crewmate in the same room; a body in the actor's own room; no sabotage already active — so each rejection is attributable to the vent alone and not to an incidentally illegal fixture.
- [ ] The ruling is pinned as a TOTAL rule, not three ad-hoc guards: a table-driven test in `tests/engine/test_rules.py` asserts that from one in-vent state `engine.tick.advance_tick` accepts exactly `vent` and `wait` and rejects the other seven action types, and asserts the table's own coverage against the members of `engine.actions.Action` so a tenth action type fails this test until it is ruled.
- [ ] `tests/engine/test_tick.py::test_vent_sabotage_and_passive_effects_apply` (:488) is repaired, not weakened: it queues `vent` then `sabotage` for the same impostor in ONE batch and asserts `events[:2] == ["VentEntered", "SabotageStarted"]`, which the ruling makes illegal — order the sabotage BEFORE the vent (or split the test) so its vent-entry witnesses, sabotage start, cooldown decrement and sabotage-timer coverage all survive.
- [ ] Every other existing in-vent allowance is unchanged and still green, unedited: the vent-exit tests at `tests/engine/test_tick.py:929` and `:987`, `test_emergency_rejects_actor_in_vent` at `:1158`, and all five pre-existing `resolve_kill` tests in `tests/engine/test_rules.py` (friendly-fire, crewmate target, actor-role, cooldown, same-room) with their current match strings.
- [ ] `training/env.py`'s mask marks kill, report and sabotage illegal while `in_vent` across its three regions (:288-298, :322-329, :341-350), and the SABOTAGE region's comment claim "no location or in-vent requirement" is corrected in the same edit rather than left contradicting the code beneath it.
- [ ] `tests/training/test_env.py::test_mask_legality_against_engine` stays green over all 8 seeds, and a new hand-built in-vent case — in the `_mask_with_impostor_in(..., in_vent=True)` style already in the file — asserts that the kill, report and sabotage intents land in `mask.illegal` AND that `_engine_rejects` agrees on the same state, so the pairing is pinned directly instead of depending on a sampled rollout happening to vent beside a victim.
- [ ] `DESIGN.md` §3.4 records the ruling additively, in the document's own Superseded style established by its demotion banner: a short dated note at the top of the section stating that kill, report and sabotage are rejected from inside a vent, that `vent` and `wait` are the only actions legal from there, and that `engine/rules.py` is the enforcing site — with the historical rule bullets at `:334-338` left as written.
- [ ] `bash scripts/verify_samples.sh` reports all 100 committed samples (50 × 4p1i + 50 × 9p2i) reconstructing byte-identically, and the PR states the conclusion this supports: no committed replay contains a now-illegal action, which is what makes this change re-record-free — the review measured 130 in-vent impostor ticks out of 2,461 across the 50 committed 9p2i seeds, so the state is common and the absence of the action is a real result, not an untested corner.
- [ ] The blast radius of the narrowed mask is stated in the PR from a fresh grep: `training/bakeoff/policy_es.py:292`, `training/bakeoff/harness.py:597`, `training/crew/scorer.py:778` and `experiments/lab/torch_probe/entrant.py:345` all enumerate the mask, and `policy_es` carries no in-vent short-circuit of its own, so a vented ES candidate's option set narrows; `uv run pytest -m campaign` is run and the PR records either that no pinned ML value moved or which one did and why.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — write the three rejection tests first and watch them fail at HEAD. This is the
cheap proof that the gate can fail; a guard added before the test proves nothing. The
existing `_player` helper in `tests/engine/test_rules.py:31` hardcodes `in_vent=False`, so
give it an `in_vent: bool = False` keyword rather than a second helper, and generalise
`_kill_state` (:43) — or add one sibling builder beside it — so the same state can carry a
`bodies` entry and a `sabotage` value for the report and sabotage cases. `load_canonical_map`
is already imported in that module.

Step 2 — the guards. Three lines, each immediately after the `_get_live_player` call, in the
existing voice: "cannot kill while in vent", "cannot report a body while in vent", "cannot
sabotage while in vent". One short comment above the set (not three) recording the ruling
and citing this task is enough provenance; the standing convention is one provenance line,
not a history essay. Note that only impostors can vent (`resolve_vent` rejects a
non-impostor actor at :106), so placing the vent check ahead of `resolve_kill`'s role check
cannot change any existing rejection message.

Step 3 — the exhaustive table. `engine.actions.Action` is
`Annotated[Union[...], Field(discriminator="type")]` at `engine/actions.py:127`, so
`typing.get_args` twice yields the nine action classes; assert the table's keys equal that
set. Drive each case through `advance_tick(state, [action], game_map=game_map)` and look for
an `ActionRejectedEvent` for the actor — the same predicate `tests/training/test_env.py:83`
uses, and the reason `engine/tick.py:601` matters here. Two setup details: the state must be
`phase="PLAY"`, and the actor's room must be one the canonical map actually vents, or the
accepted `vent` case has no current-or-connected destination to exit through.

Step 4 — the mask. Add `(not in_vent)` to the three `legal=` expressions and fix the
SABOTAGE comment. Then the new `tests/training/test_env.py` case: the file already has the
exact pattern at :410 (`_mask_with_impostor_in(room, *, in_vent=False)` over a
`seed_initial_state` base) and `_packet_for` at :445 — reuse both, place a crewmate in the
impostor's vent room and a body there so all three intents are actually enumerated, and
assert the mask and `_engine_rejects` agree.

Step 5 — the DESIGN.md note. Additive and dated, at the top of §3.4, in the same voice as
the notes at :140 and :595. Do not rewrite the Kill bullet at :334 in place: the document is
a demoted historical record and the current-architecture note (`docs/architecture.md`) does
not enumerate rules, so a §3.4 section note is where this ruling lives. The generated prompt
for this task already permits the edit, because the scope item names the file.

Step 6 — before pushing, run `uv run pytest -m campaign` as well as the default gate. The
default filter is `-m 'not campaign'`, so the frozen ES/bakeoff machinery that enumerates
the mask does not run unless you ask for it, and that is precisely the code whose option set
this change narrows.

**Ready-to-paste prompt:** `agent_prompts/task-20-11-in-vent-guards.md`

### Task 20.12 — The front door: README for outsiders, the authorship statement, history, glossary, the audits index
**Branch:** `phase-20-front-door-rewrite`
**Depends on:** 20.5, 20.7, 20.8, 20.9, 20.6 — the first-run stderr notice is silenced before the README labels the three commands as a clean one-minute proof; the hosted demo and the owner's About checklist exist before the front door links a live demo above the fold; the leak scanner learns to check entitlement and the import contracts learn to cover the whole tree before the README restates the firewall claim in verifiable shape; and the vote-correctness doc-fact check lands in the fact checker before this task extends that same file.
**Section refs:** C/A1, C/A2, C/A5, C/B2, C/B8, C/B12 and the front-door plan F1–F6 (audits/review-2026-08-19/C/collated-portfolio.md §A, §B, §F); audits/review-2026-08-19/C/x2-narrative-and-positioning.md §3, §5, §6a, §6b; audits/review-2026-08-19/C/x1-front-door-reproduction.md §1, §2, §3.1, §3.2; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 row 1.6 and §7 (the endorsed outline plus its three edits — demo link and byline above the commands, every volatile number baseline-stamped, honesty claims in verifiable shape); C-88 (audits/review-2026-08-19/B/collated-findings.md C-88). Anchors re-verified at HEAD `b809b19c`: README.md is 3,833 words / 248 lines; :82-107 is the "Project status" section at 845 words = 22 % of the file; :84 is one 135-word sentence with 11 opening parentheses; :86 says "the paragraph below it carries phases 15–19"; :88-105 is the phase table, last row 14; :107 is one 506-word paragraph with 35 opening parentheses; :149 spends 234 words on lever provenance inside "Watch a replay"; :47 carries "300+ merged agent-authored PRs — the live count is on GitHub, deliberately not re-pinned here" and one of three "MVP complete" declarations (:47, :84, :95); :74 carries "import-linter enforced"; :162-165 is the fake-provider tournament example; :211 and :230 carry the clone caveat; file-wide there are 81 em-dashes and 137 opening parentheses, and the six reading-guide terms occur undefined at baseline 19, adopting record 3, ladder tip 4, graduat* 5, NO-FLIP plus "no mover flip" 2, canary denominator 2. docs/reading-guide.md is 3,239 words / 378 lines: :37-51 the numbers table, :216-291 the eleven-term glossary, :303 the only disclosure that the second audit is "by a different model". The C-88 mechanism at HEAD is llm/fake_provider.py:183 (`f"fake-{field_name}-{seed}"`, so a `target` field mints `fake-target-<digest>`) meeting meetings/manager.py:200-207 and meetings/voting.py:90-92 (`INVALID_VOTE_TARGET_MARKER`, invalid target normalized to SKIP) — the review's `:127-135` anchor was the sibling union leg, corrected here. The committed counter-example is populated: replays/samples/9p2i/tournament-eval-report.json reads 101 ejections, `vote_correctness_rate` 0.9230769, `ejection_accuracy` 0.7722772. Fact-checker anchors re-verified at origin/main `37fe367a` (20.5 and 20.6 both extended this file after the re-verification above): scripts/check_doc_facts.py:110-112 (`_README`, `_ENV_EXAMPLE`, `_LADDER_TIP_AUDIT`), :213-223 (`check_facts`, fanning out to `check_sample_provenance`, `check_ladder_tip`, `check_lever_registry`, `check_vote_correctness_sentinel`), tests/scripts/test_check_doc_facts.py:31-75 (`_COPIED` at :31-44 and the `doc_tree` fixture at :62-75). Derivable counts at origin/main `37fe367a`: `agent_prompts/*.md` = 363, `replays/samples/{4p1i,9p2i}/*.jsonl` = 50 + 50, `git rev-list --count HEAD` = 902, commit authors dkdan10 373 / Claude 310 / Daniel Keinan 218, `Co-Authored-By` trailers on 327 commits.
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run python scripts/check_doc_facts.py` exits 0 and names the new checks; `uv run pytest tests/scripts/test_check_doc_facts.py -q` green with every new check perturbation-proved; `wc -w README.md` ≤ ~1,800 (from 3,833) and `wc -w docs/reading-guide.md` ≤ ~900 (from 3,239), both quoted in the PR with the em-dash and opening-parenthesis counts before and after; a grep for the six dialect terms in README.md returns only occurrences inside a `docs/glossary.md` link.

Six independent portfolio readers stopped reading the README at the same place. The
"Project status" section (README.md:82-107) is 845 words — 22 % of the whole file — and it
opens with a 135-word single sentence (:84) and closes with a 506-word single paragraph
(:107) whose longest sentence runs 172 words. The phase table stops at 14 and says so
(:86: "the paragraph below it carries phases 15–19"), which is the author noticing that a
paragraph is a table nobody extended. Read literally, the section is a run of negatives —
closed with no mover flip, closed with nothing recorded, zero of fourteen pre-registered
rulings demonstrated — and three of the six readers report understanding it as "the last
two phases produced nothing" until they reached the reading guide's honesty section, one
hop below the front door (audits/review-2026-08-19/C/collated-portfolio.md §A1). The
project's honesty culture is its strongest asset and the front door currently delivers it
as an apology.

The second measured defect is vocabulary. Six of the eleven terms the reading guide
defines appear undefined in the README — re-counted at HEAD as baseline 19, adopting
record 3, ladder tip 4, graduated 5, NO-FLIP plus "no mover flip" 2, canary denominator 2
— and at least fifteen more (referee, slate, arm, mover, champion, conviction economy,
supply and conversion floors, absence prior, roll-call round, endpoint-band whereabouts
exemption, flag-minting, starved-economy shape, screening-tier shortlist, two-axis owner
ruling, training-time-runner tier, evidence-gated default flip) are defined nowhere in the
tree (§A2). Conventions named after task numbers are the clearest tell. The rule this task
adopts is the reviewers' own: nothing in README.md may require the reading guide to parse.
The evicted material lands somewhere real — the phase narrative in `docs/history.md`, the
vocabulary in `docs/glossary.md` (with descriptive names beside the task-numbered ones),
and the 76 top-level audit files, of which only three are named read-first and the rest are
unnavigable, in `audits/README.md` (§B12). The reading guide itself is 3,239 words against
an advertised five minutes; it keeps its numbers table, its demo path, its capability
cross-tab and its three-audits tour, and sheds the glossary (§B3).

The third defect is the one only the human can fix. The README names no person. LICENSE
says Daniel Keinan; git shows three human identities plus "Claude" as first-class author on
310 of 902 commits with `Co-Authored-By` trailers on 327 of them; every merged PR shows one
human author on GitHub. The docs say "the owner", "the human", "the operator" and never
introduce them (audits/review-2026-08-19/C/x2-narrative-and-positioning.md §5: the
mechanics of authorship are unusually legible here and the narrative of authorship is
absent, and absence gets read uncharitably). Two disclosures ride with it: the
"independent external audits" the docs lean on are AI auditors the owner commissioned —
stated today only at docs/reading-guide.md:303 — and every gameplay and ML number in the
repo comes from one model on one prompt set at n=50 per set (§A5). This section is written
first-person, from git evidence, and marked for the owner to confirm rather than invented.

The fourth is a claim that is false in the reader's hands. The README's tournament example
(:162-165) hands a stranger the default fake provider, and a fake ballot's `target` is
minted as `fake-target-<digest>` (llm/fake_provider.py:183), which the meeting layer
defensively normalizes to SKIP (meetings/manager.py:200-207) — so the report an outsider
gets has zero ejections and null rates (C-88; C/B2, reproduced by X1 §1 row 5). The
committed `replays/samples/9p2i/tournament-eval-report.json` is populated (101 ejections,
vote correctness 0.923, ejection accuracy 0.772) and is what the example should point at,
with one sentence on what fake output looks like and why. In the same pass the honesty
claims move to the shape a reader can check — "never breached in CI: import-linter
contract, planted-leak test, recursive leak sweep" — which only becomes true once the
scanner checks entitlement and the contracts cover the whole tree, which is exactly why
those two tasks are upstream of this one.

What keeps this from rotting is the discipline the phase is enforcing: generated facts beat
copied facts. Every number the new README states must either be re-derived by
`scripts/check_doc_facts.py` from a committed source (manifests, the served report cells,
the lever registry, the prompt corpus, the phase files, the audit corpus) or must not be
stated as a bare number at all — volatile counts become a date-stamped claim plus the
command a reader runs, per the fact-check precedent this task extends. This task writes the
front door's structure, prose and checks; it does not write the results table's ML
paragraph, the architecture picture, the contract-to-PR exhibit, the lessons page or the new
hero image, each of which is a later contract that fills a marked anchor here. No link this
task writes may point at a file that does not exist at this merge — the front door's 49
relative links are 0-broken today (X1 §1 row 7) and stay that way; forward pointers are HTML
comments, never live links.

**Files in scope:**
- README.md; (the rewrite per the endorsed outline: pitch-first tagline with the byline, the hosted-demo link above the fold, the labelled reproduce block, at-a-glance, the human/agent split, project status in ≤150 words with the phase table extended through 19, the numbers table, and the honesty claims in verifiable shape)
- docs/history.md; (new — the evicted phase narrative, one paragraph per phase, each linking its close audit where one exists and its contract file otherwise)
- docs/glossary.md; (new — the reading guide's eleven terms plus the fifteen-plus defined nowhere, each with a descriptive name beside any task-numbered convention and one committed usage)
- audits/README.md; (new — the index: the three read-first audits, then every audit by phase with one line each)
- docs/reading-guide.md; (trimmed to a real five minutes: the numbers table, the demo path, the capability cross-tab and the three audits; the glossary moves out; file:line citations become heading anchors)
- scripts/check_doc_facts.py; (the new checks: dialect terms linked, the phase table and history complete, the audits index complete, the results figures agreeing with the reading guide, volatile counts date-stamped, no file:line citations left in the guide, every relative link resolving)
- tests/scripts/test_check_doc_facts.py; (one perturbation test per new check, plus the extended `doc_tree` fixture)

**Files NOT in scope:**
- docs/ml-program.md and the README results-table ML paragraph (20.13 — this task leaves a marked anchor and the table's non-ML rows)
- docs/architecture.md, docs/media/architecture.svg and the contract-to-prompt-to-PR exhibit (20.20 — this task leaves a marked anchor)
- docs/lessons.md and the "What I learned" section (20.40 — the section is not stubbed, only marked)
- docs/media/* and the hero swap (20.39 owns the image and its caption; the existing PNG stays as the hero here, its caption shortened)
- docs/adr/0001-three-load-bearing-decisions.md and the "recorded verbatim" wording (20.13 owns the ADR note; 20.41 owns that README sentence)
- docs/artifacts.md and docs/deployment.md (the clone caveat and the deployment trust boundary already live there — the README links them, neither file is edited)
- .env.example, AGENTS.md, CONTRIBUTING.md (20.5 and 20.9 own their lines)
- scripts/check.sh (the fact check runs under pytest, as it has since it was introduced)
- replays/, audits/audit-*.md (records are read and indexed, never rewritten; records get additive dated errata, and none is due here)
- the prompt templates and agent_prompts/ (no template edit and no prompt regeneration from this task)
- DESIGN.md, AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] README.md follows the endorsed outline: a product-first tagline with a byline line (name, agents, MIT, CI and Python badges, the solo timeline), the hosted-demo URL from the Pages workflow in the first screen, the three existing reproduce commands kept verbatim and each labelled with the claim it proves, an at-a-glance block, "How it was built — who did what", "What it is", "What the measurements said", "Project status" and the phase table, "Run it", and the docs/architecture/glossary/reading-guide/history footer.
- [ ] "Project status" is ≤150 words of plain English, states in one sentence what a no-flip and a nothing-recorded close MEAN (a bar was pre-registered; the honest answer was not yet), leads with what was shown before the refusal to overclaim, and is followed by a phase table covering 0–19 in which every row links a file that exists — its close audit where one exists, its contract file otherwise; the 845-word section and the 506-word paragraph are gone from README.md.
- [ ] A "How it was built — who did what" section names the human and the agents in first person, ~120 words: what the human owned (the task contracts, the standing rules, the review gates, the audit rulings, the product direction), what the agents wrote (every coding PR, most audits), what the human did not do (write production code by hand), and how a reader verifies it in git (the `claude/…` branch names, the commit authors, the `Co-Authored-By` trailers); it states that the commissioned audits were AI auditors, not third parties, and that every gameplay and ML number is one model on one prompt set at n=50 per set; the whole section carries `<!-- OWNER: confirm wording -->`.
- [ ] No undefined private-dialect term survives on the front door: each of the six counted terms and each surviving term from the defined-nowhere list either does not appear in README.md or appears with its first occurrence linked to its `docs/glossary.md` entry, and `scripts/check_doc_facts.py` fails when an occurrence is unlinked or a glossary entry is missing (perturbation-tested both ways in tests/scripts/test_check_doc_facts.py).
- [ ] The firewall and gate claims are verifiable-shaped and true as of this merge: the firewall line reads as never breached in CI with its three named mechanisms (the import-linter contract, the planted-leak test, the recursive leak sweep), and the "merged green through the same gate" claim is restated as what a reader can check (CI is required on main, see the workflow; `bash scripts/check.sh` runs the same gate locally).
- [ ] The fake-provider tournament example points at `replays/samples/9p2i/tournament-eval-report.json` as a real report and says in one sentence what fake-provider output looks like and why (every fake ballot's minted target normalizes to SKIP, so the report has no ejections and null rates); a reader following the README reaches a populated report.
- [ ] `docs/history.md` carries one paragraph per phase 0–19 with the evicted narrative and the lever-graduation provenance, `docs/glossary.md` defines the reading-guide terms plus the ones defined nowhere with a descriptive name beside every task-numbered convention, and `audits/README.md` indexes every top-level `audits/*.md` exactly once (the three read-first audits first, then by phase, one line each) with the review directory named as a unit; a check fails when an audit file is added or removed without an index row.
- [ ] `docs/reading-guide.md` is ≤ ~900 words, keeps its numbers table, demo path, capability cross-tab and three-audits tour, no longer carries the glossary, and contains zero `file.ext:NN` citations — every one replaced by a heading anchor or a symbol reference; a check pins the zero.
- [ ] Every number README.md states is checked: `scripts/check_doc_facts.py` gains checks that the phase table and `docs/history.md` between them account for every `tasks/phase-*.md`; that the README results figures equal the reading guide's canonical rows; that each volatile count (merged PRs) carries an as-of date stamp rather than a bare number; and that every relative link in README.md, docs/history.md, docs/glossary.md, audits/README.md and docs/reading-guide.md resolves to an existing path. Each new check has a perturbation test that fails on a mutated copy and passes on the unperturbed one, and the `doc_tree` fixture copies exactly the files the new checks read.
- [ ] The PR quotes `wc -w README.md` before and after (3,833 → ≤ ~1,800), `wc -w docs/reading-guide.md` before and after (3,239 → ≤ ~900), and the em-dash and opening-parenthesis counts before and after (81 and 137 at HEAD), and states whether the owner has enabled Pages yet — if not, the demo line carries `<!-- OWNER: enable Pages, then confirm this URL resolves -->` and the PR says so.
- [ ] docs/reading-guide.md's enforcement claim quotes the wording the import-contracts task recorded (the widened root set; the temp-tree plant) — the reading guide and the README state the same verifiable shape.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — measure before you cut, and keep the receipts. Record the four counts the PR
must quote (README words, reading-guide words, em-dashes, opening parentheses) at HEAD
before the first edit. The reproduce block at README.md:13-37 is the one thing all six
reviewers praised: keep those three commands byte-for-byte and add only a label above
each naming the claim it proves (same seed twice is byte-identical; the hundred committed
replays reconstruct; the demo is a static directory). Do not rewrite the commands to look
tidier.

Step 2 — move, do not delete. Everything at README.md:84, :86, :107, :149 and :230 leaves
the file: the phase narrative and the lever-graduation provenance to docs/history.md, the
clone caveat to one line plus the existing docs/artifacts.md link, the vocabulary to
docs/glossary.md. The phase table's rows 0–14 already exist; extend to 19 and give every
row a link that resolves. Note that close audits exist only for the MVP close and phases
13 through 19 — for the earlier phases link the contract file and say so in one line above
the table rather than inventing an audit name.

Step 3 — write the numbers once. The reading guide's numbers table is the canonical
statement; the README's "What the measurements said" table quotes the same figures with
the same committed sources, and the new check asserts the two agree row by row so a later
edit cannot drift one from the other. Leave a marked anchor for the ML paragraph and the
before/after column rather than an empty heading. Do not lift the audit-only figures out of
the evicted paragraph into the README — they belong to the results page, and the reading
guide already carries the four that matter.

Step 4 — the authorship section comes from git, not from memory. Re-derive at
implementation time and quote the commands in the PR: `git rev-list --count HEAD`,
`git shortlog -sn --all`, the `Co-Authored-By` trailer count, `ls agent_prompts/*.md | wc -l`,
and the merged-PR count via `gh pr list --state merged`. State the merged count with an
explicit as-of date so the claim ages honestly; the check asserts the stamp is present and
well-formed, never the value, because no doc check may reach the network. Write the section
in first person, mark it for the owner, and change no other document's institutional
register.

Step 5 — the new checks live beside the existing three. `check_facts` at
scripts/check_doc_facts.py:213-223 is the fan-out; add each new check as its own function
accumulating into the same error list so one run names every drift. The dialect-term check
wants a module-level tuple of terms with the glossary heading each must resolve to, so
adding a term later is a one-line change. The audits-index check should walk
`audits/*.md` at top level and diff against the index's rows in both directions — an
un-indexed file and an indexed file that no longer exists are both failures. The
link-resolution check needs no network: parse the relative markdown targets, strip any
fragment, and stat the path. Extend `_COPIED` and the `doc_tree` fixture at
tests/scripts/test_check_doc_facts.py:31-75 with exactly the files the new checks read, and
give every new check a mutated-copy test — a check that cannot fail is not a gate.

Step 6 — forward anchors are comments, never links. The results-table ML paragraph, the
architecture picture, the contract-to-PR exhibit, the lessons page and the hero swap are
later contracts. Mark each spot with an HTML comment naming the work in words. A live link
to a file that does not exist yet would break the zero-broken-links property this task is
also asked to keep.

**Ready-to-paste prompt:** `agent_prompts/task-20-12-front-door-rewrite.md`

### Task 20.13 — The results stated once: docs/ml-program.md, the README results table, and the comparator-defect errata
**Branch:** `phase-20-results-page`
**Depends on:** 20.12 (the front-door rewrite lands first — this task fills the results section and the ML paragraph that rewrite leaves anchored, and quotes the reading guide only after its trim); also after 20.11 (the engine-rule line both tasks add to the design record lands first)
**Section refs:** audits/review-2026-08-19/C/collated-portfolio.md §A6 (state the results once — MUST for the research lead, GOOD for three more personas; the concrete fix names both halves, the README table and the ≤2-page page); audits/review-2026-08-19/C/p2-ml-research-lead.md §3 Weakest-1 ("no artifact tells the ML story in the standard research shape … `training/README.md` is a tier map, not that document") + §6 ("the single change that would most raise it") + §7 MUST-2; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 rows 1.7 and 1.8 (the two roadmap items this task implements), §2 row 5 (the "(suspicion, trust, alibi)" claim graded UNDERMINED) and §2 row 9 (the win edge graded CAVEAT — "the method holds, one input is contaminated"); audits/review-2026-08-19/B/collated-findings.md C-72 (`trust` never written; `## Open contradictions` rendered in 0 of 1,656 replay renders); audits/review-2026-08-19/B/verdicts.md C-3 (CONFIRMED **and understated** — 190/415 = 45.8 % of free zero-witness kills declined over the 50 committed 9p2i seeds, 168/168 of them on an exact 1.0 score tie broken by the lower id; the reconstruction replays `decide()` against the recorded bytes with an empty `policy_would_kill_but_action_differs` bucket); audits/review-2026-08-19/A/verdicts.md G-12 (CONFIRMED-BUG — 10,335 impostor decisions re-run offline with 0 mismatches; ghost-top 303/2461 = 12.3 % on samples/9p2i, 555/6663 = 8.3 % on ml_corpus/9p2i, 0/632 and 0/579 across the two 4p1i sets; seed 36 provably thrown) — **both rates are now committed pins**, landed by 20.15 (PR #365): tests/agents/test_impostor_policy.py:1812-1864 (`TestCommittedCorpusTargetingPins` — 190/415 with the 168 / 15 / 7 / 0 decline-reason split, ghost-top 303/2461, 555/6663, 0/632, 0/579, 222 ejected / 81 unseen on samples/9p2i, 0 reconstruction mismatches over 10,335 decisions) computed by eval/evidence_honesty.py's I-11 cells, with audits/audit-phase-20-preregistration.md:174-175 stating all four sets [VERIFIED]; README.md:83 (the belief-state sentence as 20.12 left it — the "(suspicion, trust, alibi)" wording is already gone, so this leg is verify-only), :88-96 (the "What the measurements said" section and table 20.12 built, whose 100/100, 520/520 and 87 % rows this task keeps), :100 (the marked anchor `<!-- ANCHOR: a later contract adds the ML program's paragraph, titled by its result, plus the table's before/after column. -->` this task fills), :107 (the numberless "Four learned tactical policies each beat the scripted one on wins" sentence — the "+0.12 to +0.30" and "+0.16" figures no longer appear in README and now live only in the two close audits); docs/adr/0001-three-load-bearing-decisions.md:18 (decision 3 — "trust scores, alibi map, suspicion graph"); agents/memory/beliefs.py:1111 (`adjust_trust` — the definition is the only non-test occurrence in the tree; seven callers, all under `tests/`), :1493 (`record_contradiction` inside `apply_contradiction_rule` at :1340 — the write lands on the derived result, not the persistent store) with agents/memory/store.py:1811 (the `## Open contradictions:` block that renders); audits/audit-phase-19-close.md §4.1 (pooled 310/310 = 1.000 with direct proof vs 46/125 = 0.368 without; 79/79 of innocent ejections in the non-direct cell); audits/audit-phase-18-close.md:78-84 (the four-arm table: win 0.52 / 0.56 / 0.38 / 0.42857 vs the fresh same-seed `p18-fsm-comparator` 13/50 = 0.26, referee FAIL ×4), :105 ("+0.12 to +0.30"); audits/audit-phase-17-close.md:25 and :60 (`utility-es` win 0.52 = 26/50, Δ +0.16 over the same-seed FSM 0.36, referee FAIL on two gauges); audits/audit-phase-18-flip-emergence.md:466-481 (N1 witnessed-kill rate 30/197 = 0.15228 vs 8/174 = 0.04598, z = +3.370; N2 co-present kills 20/197 = 0.10152 vs 0/174, z = +4.321; both NOT-DEMONSTRATED because clause (c) is unsatisfiable by construction); docs/reading-guide.md:11-22 (§1 "The numbers worth knowing" — the canonical numbers table after the 20.12 trim, rows at :15-22), :57-84 (§3 "What the corpus demonstrates — and what it does not", the 165-meeting cross-tab 68/2 flagged vs 10/21 unflagged at :74-77), :102 (the marked anchor `<!-- ANCHOR: a later contract adds the research-shaped ML page and links it here. -->`; the old §6 ML story was cut in the trim and the file now has five sections); training/README.md:1 (the title — a disposition ledger), :128-165 (§3 what the program positively learned); agents/tactical/learned/forward.py:14 (the 19-weight linear scorer, no numpy/torch), :111 (`ENCODER_VERSION = "impostor-option-features-v1"`), :114 (`GENOME_LENGTH` = 18 features + bias); training/env.py:1-40 (the rollout env drives the real `HeadlessGame`; the legal-action mask is derived from `engine/rules.py`); training/rewards.py:16-26 (the corrected shaping claim — telescoping is not invariance); eval/watchability.py:9-20 (SELECTION-ONLY — the referee is a champion gate and is NEVER a training reward); scripts/paired_stats.py:1-36 (stdlib-only exact McNemar + Wilson, written so a fresh clone reproduces the cells); training/reports/report-finalist-eval.md:2493 (the §18 errata form — additive, dated, nothing above it rewritten)
**Complexity:** Medium
**Record impact:** none (documentation and errata only — no rendered, detector, replay or report byte moves, so nothing here waits on the Phase-20 adopting record)
**Measurement:** `uv run python scripts/paired_stats.py training/reports/results-finalist-eval.jsonl` reproduces every McNemar cell the results table states (ea4bc955 17/4 p=0.0072; bfd145cb 20/5 p=0.0041; shipped 6d327dcb 15/9 p=0.3075 n.s.; 7f73929d 12/3 p=0.0352, failing Bonferroni α=0.0125), output pasted into the PR Summary; `uv run python scripts/check_doc_facts.py` green; `uv run pytest tests/scripts/test_check_doc_facts.py -q` green; `wc -w docs/ml-program.md` ≤ ~1,400.

The repo's best numbers are the ones it never states. The 19.14 partition, committed and
re-quoted at `audits/audit-phase-19-close.md` §4.1, reads: **310/310 = 1.000 conviction
accuracy where the substrate hands the crew direct proof, 46/125 = 0.368 where it does not,
and 79 of 79 innocent ejections in the non-direct cell.** That is the sharpest measured
statement in the project — a social-deduction environment whose convictions are perfect on
engine-certified evidence and worse than a coin flip on inference — and the README states
none of it. Four portfolio personas independently reached for the same repair
(`audits/review-2026-08-19/C/collated-portfolio.md` §A6): the research lead called the
missing artifact "the single change that would most raise it"
(`audits/review-2026-08-19/C/p2-ml-research-lead.md` §6), having spent forty minutes to
find that `training/README.md`'s own title is a keep/freeze/retire disposition ledger
(`training/README.md:1`) and that the program summary he wanted is §3, buried past ~150
lines of tier tables. The numbers themselves are fine: the review re-derived the McNemar
table and the vent cross-tab from committed files with stdlib and got exact agreement. The
defect is location and shape, and it is repaired with text.

This task writes the two artifacts the review names. `docs/ml-program.md` (new, ≤2 pages) tells
the ML story in the standard research shape: problem; environment (observation, action mask
and reward in one paragraph plus one inline figure — the rollout env drives the real
`HeadlessGame` with the mask derived from `engine/rules.py`, `training/env.py:1-40`, and the
shaping term telescopes without being policy-invariant, `training/rewards.py:16-26`); method
(ES over a 19-weight linear utility scorer — 18 features plus bias on the
`impostor-option-features-v1` basis, `agents/tactical/learned/forward.py:14`, `:111`, `:114`
— with the referee as a SELECTION gate and never a training reward,
`eval/watchability.py:9-20`); one results table (arm · impostor win vs the same-seed
comparator · exact McNemar p · referee verdict) built from
`audits/audit-phase-18-close.md:78-84` and reproduced by `scripts/paired_stats.py`; N1 and N2
framed as what they are — a learned impostor discovering that witnessed kills are cheap
because the conviction engine convicts on vent proof, i.e. specification gaming of a
social-deduction referee (`audits/audit-phase-18-flip-emergence.md:466-481`); limitations
(one model, one prompt set, n=50, the bar's construction, the finalist raw slate off-repo);
and related work, so a reader can place the environment. The README gains the results table
under "What the measurements said" — the rows the review lists, each with its committed
source and, where the number is volatile, its baseline and record date — plus one ML
paragraph titled by its result rather than by its process.

Two claims get corrected in the same pass because they are the ones a hostile reader breaks
first. **The memory claim.** `docs/adr/0001-three-load-bearing-decisions.md:18` still
advertises a three-channel belief state (20.12 already removed the claim from README, whose
:83 now reads "a belief state derived from it"); `trust` has no production writer at HEAD
(`agents/memory/beliefs.py:1111` is the definition, and the only other callers in the tree are
seven under `tests/`), and the contradictions block at `agents/memory/store.py:1811` rendered
in 0 of 1,656 replay renders the review sampled — the `record_contradiction` call at
`agents/memory/beliefs.py:1493` writes a derived state inside `apply_contradiction_rule`, and
nothing persists it (`audits/review-2026-08-19/B/collated-findings.md` C-72;
`audits/review-2026-08-19/D/FINAL-synthesis.md` §2 row 5 grades the claim UNDERMINED). The
README needed no further repair on this claim — 20.12 already dropped the three-channel
wording, so this task only re-verifies it at HEAD; the ADR is a record of a 2026-05-01 decision and gets an
additive dated note, never a rewrite.

And **the comparator claim.** The "+0.12 to +0.30" and "+0.16" win edges over the same-seed
scripted FSM no longer appear in README (20.12 cut the figures; :107 now states the edge in
words), but both close audits record the cells and are the surface a reader reaches. The review found
the comparator carries two identified target-selection defects, both 9p2i-only, both depressing
the FSM: the kill seam re-validates only `targets[0]`, so **190/415 = 45.8 %** of free
zero-witness kills are declined — 168 of the 190 in the ranking branch's exact-1.0 score tie
broken by the lower player id, the other 22 in the named fellow-defer (15) and cover (7)
branches with none unattributed (`audits/review-2026-08-19/B/verdicts.md` C-3, verdict CONFIRMED
and understated); and the dead-set is built only from seen bodies, so an ejected player stays
targetable and the mover spends **303/2461 = 12.3 %** (samples/9p2i) and **555/6663 = 8.3 %**
(ml_corpus/9p2i) of its decisions topping its target list with someone the whole table watched
get ejected — **0/632 and 0/579 across the two 4p1i sets** — with seed 36 a demonstrably thrown game
(`audits/review-2026-08-19/A/verdicts.md` G-12, verdict CONFIRMED-BUG; 10,335 decisions re-run
offline with 0 mismatches against the recorded action stream). A project whose thesis is that it
does not publish numbers it knows are confounded cannot leave this unstated: the honest paragraph
lands in `docs/ml-program.md` and, as additive dated errata in the form
`training/reports/report-finalist-eval.md:2493` established, in both close audits. This task
states the confound; the mover repair and the re-measurement on corrected bytes are separate,
later contracts, and the errata say so.

**Files in scope:**
- docs/ml-program.md; (new — problem; environment: observation/action-mask/reward in one paragraph plus one inline figure; method: ES over the 19-weight utility scorer with the referee as selection gate, not reward; one results table: arm, win vs the same-seed FSM, McNemar p, referee verdict; N1/N2 framed as referee exploitation / specification gaming; limitations: one model, n=50, bar construction, raw finalist slate off-repo, the comparator defects; related work)
- README.md; (the "What the measurements said" section — the results table with its sources and baseline stamps, one ML paragraph titled by its result, and the memory-claim wording; no other section moves)
- docs/adr/0001-three-load-bearing-decisions.md; (an additive dated note only — the ADR text is a record of a 2026-05-01 decision and is appended to, never rewritten)
- training/README.md; (program-summary-first, the tier map second, the reopening checklist last; a pointer to docs/ml-program.md as the entry point)
- audits/audit-phase-18-close.md; (an additive dated erratum naming the comparator defects with the measured rates and their instruments)
- audits/audit-phase-17-close.md; (the same erratum for that close's win-edge figures)
- scripts/check_doc_facts.py; (the results table's new numbers checked against their committed sources)
- tests/scripts/test_check_doc_facts.py
- DESIGN.md; (the §6.6 target-not-as-built caption only — historical content untouched)
- docs/reading-guide.md; (TWO edits only: the numbers-table row(s) mirroring whatever this task adds to the README results table — `scripts/check_doc_facts.py::check_results_agreement` fails any README results row with no identical-figure match in the guide's canonical table — and the marked anchor at :102, replaced by a link to docs/ml-program.md; the 20.12 trim is not re-opened)

**Files NOT in scope:**
- training/ code and artifacts (nothing retrains and nothing is re-fit; every number is quoted from a committed report or audit and re-derived with `scripts/paired_stats.py`)
- docs/reading-guide.md beyond the two edits named in scope (the 20.12 trim owns the rest of the file; this task quotes it, never re-shapes it)
- eval/ (no new instrument here — 20.15 already landed the comparator rates as committed pins; this task quotes eval/evidence_honesty.py's I-11 cells, it does not extend them)
- agents/tactical/impostor_policy.py (the defects are STATED, not repaired; the repair is a separate Wave-2 contract and the errata name it as routed)
- docs/media/ and the architecture SVG (the architecture-exhibit contract owns that asset; this page's figure is inline)
- replays/ and training/reports/*.jsonl (committed measurement bytes are read, never edited)

**Definition of done:**
- [ ] `docs/ml-program.md` exists in research shape — problem, environment (with one inline figure; no new asset file), method, one results table, N1/N2, limitations, related work — at ≤2 pages (`wc -w` ≤ ~1,400, quoted in the PR), and every number in it carries an inline citation to a committed path with a line or section anchor.
- [ ] The results table's four learned arms and the comparator match `audits/audit-phase-18-close.md:78-84` cell for cell, and each arm's paired p comes from `uv run python scripts/paired_stats.py training/reports/results-finalist-eval.jsonl` re-run in-session (output pasted into the PR), with the shipped champion's 15/9 p=0.3075 stated as not significant rather than elided.
- [ ] N1 and N2 are stated with their cells (30/197 = 0.15228 vs 8/174 = 0.04598, z = +3.370; 20/197 = 0.10152 vs 0/174, z = +4.321), framed as specification gaming of the referee, AND with the NOT-DEMONSTRATED ruling and the clause-(c)-unsatisfiable reason in the same breath — the framing never upgrades the claim.
- [ ] README's "What the measurements said" table (built by 20.12 at README.md:88-96) states, each row with its committed source — the 100/100, 520/520 and 87 % rows already exist and are re-verified rather than rewritten, and every row this task ADDS is mirrored with an identical claim string and figure in docs/reading-guide.md's numbers table so `check_results_agreement` stays green: 100/100 committed replays reconstruct byte-identically; 520/520 eject ballots carry a valid citation, followed by the one-sentence qualification that valid means resolvable, not supported; the proof-vs-inference cross-tab 310/310 = 1.000 against 46/125 = 0.368 with 79/79 innocent ejections in the non-direct cell; the 87 % vent-sighting cross-tab (68/78 correct 9p ejections; the 165-meeting 2×2 — 70 flagged → 68/2, 95 unflagged → 10/21) with "general social deduction: NOT demonstrated" as the row's own reading; and one ML paragraph whose title is its result, written in place of the marked anchor at README.md:100 (four learned arms beat the same-seed comparator on wins, none was adopted, and why the gate is right to say so), with docs/reading-guide.md:102's anchor likewise replaced by a link to the new page.
- [ ] Every volatile number the README table states carries its baseline and record date inline; the PR lists which rows are machine-checked by `scripts/check_doc_facts.py` today and which are stamped-only, so the unchecked set is recorded rather than silent.
- [ ] README's belief-state sentence (README.md:83, as 20.12 left it) is re-verified at HEAD as asserting no live three-channel state — no README edit is due here unless that re-verification finds one — and `docs/adr/0001-three-load-bearing-decisions.md` carries an additive dated note stating that `trust` is a present-but-unwritten channel at HEAD (the definition at `agents/memory/beliefs.py:1111`, callers only under `tests/`) and that the rendered contradictions block appeared in 0 of 1,656 sampled renders — with the grep and the render count quoted in the PR as the verify-then-fix step.
- [ ] The comparator-defect paragraph exists in `docs/ml-program.md` and as an additive dated erratum in BOTH close audits, quoting 45.8 % (190/415 free zero-witness kills declined, 168 of them in the ranking branch's exact-1.0 id tie-break, 15 fellow-defer, 7 cover, 0 unattributed) and the 8–12 % ghost-top band (303/2461 = 12.3 % samples/9p2i, 555/6663 = 8.3 % corpus/9p2i, 0/632 and 0/579 on the two 4p1i sets), naming as the source the committed pins 20.15 landed — `tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins` over `eval/evidence_honesty.py`'s I-11 cells, with the 2026-08-19 review as their origin — and stating that the mover repair is Task 20.32 and the re-measurement Task 20.38, and saying plainly which direction the confound runs (the comparator is depressed, so the learned arms' win edge is an upper bound).
- [ ] Both errata are additive and dated: `git diff` on the two audit files shows appended lines only, no verdict, table cell or hash above the erratum heading altered, and the PR quotes the diffstat.
- [ ] `training/README.md` opens with the program summary and a pointer to `docs/ml-program.md`, with the tier map second and the reopening checklist last; the freeze-header coverage registry and every existing section body survive the reorder unchanged (verified by a word-level diff quoted in the PR).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Everything this page needs already exists in the tree; the job is selection and shape, not
research. Write from `docs/reading-guide.md` §1 and §3 (the 20.12 trim cut the old §6 ML story), `training/README.md` §3,
`audits/audit-phase-19-input-claude.md` §6 (the frank retrospective, including its own
"roughly 20 % of the apparatus delivered ~90 % of the decision value" line — quoting the
project's self-criticism is the credibility move, not a risk),
`audits/audit-phase-18-flip-emergence.md` §8.3 for N1/N2, and `audits/audit-phase-19-close.md`
§4.1 for the proof cells. Add no number you cannot cite to a committed path.

Step 1 — verify-then-fix on the memory claim before writing a word of it: run the greps
(`adjust_trust` and `record_contradiction` across the production packages, then across
`tests/`) and confirm at HEAD what is written and what is not. State exactly what you find,
including that a `record_contradiction` call does exist on a derived belief state; the honest
sentence is "not persisted", not "never called".

Step 2 — the results table is a quote, never a computation. Read the arm cells from the
close audit's table and re-run `scripts/paired_stats.py` for the p-values; if any cell
disagrees with the audit, stop and record the disagreement in the PR rather than picking a
number.

Step 3 — the figure is inline (a fenced diagram block inside the page), because the media
directory belongs to the architecture-exhibit contract. Keep it to the loop a reader needs:
seed → real `HeadlessGame` rollout with the interposed intent selector → per-episode record →
ES over the 19-weight genome → referee gate → accept or reject. Do not draw the whole
training package.

Step 4 — the errata copy the established form: a heading naming the coordination, the date,
the task, and "additive, no in-place rewrites"; then the anchor, then numbered items, then an
explicit item recording what the erratum does NOT touch. Say in the erratum which direction
the bias runs and what is unaffected (the referee verdicts, the NO-FLIP rulings and the
pre-registration ordering all stand — the defects depress the comparator, so the win edge is
an upper bound and the referee failures are, if anything, understated).

Step 5 — the README table rows the front-door rewrite already machine-checks stay as they
are; for the rows this task adds, prefer a stamped quote with its committed path over an
invented check. Two merged checks bite here: a row added to the README table must also be
added to `docs/reading-guide.md`'s numbers table with the identical claim string and figure or
`check_results_agreement` fails, and any private-dialect term the new ML paragraph introduces
must sit inside a `docs/glossary.md` link on its FIRST README occurrence
(`check_dialect_terms`). Record the split in the PR. If a row's number is cheap to check and
the existing checker can take it without touching its file, say so in the PR as a routed
follow-up rather than editing a file outside this scope.

Step 6 — `training/README.md` is a reorder plus a pointer, not a rewrite. Move §3 to the
front as the program summary, keep every other section's body byte-identical, and let
`docs/ml-program.md` carry the narrative. Its FROZEN header and the freeze-coverage registry
must survive.

**Ready-to-paste prompt:** `agent_prompts/task-20-13-results-page.md`

### Task 20.14 — The solvability instrument: who could have done it, from the crew's own eyes
**Branch:** `phase-20-solvability-instrument`
**Depends on:** none (root)
**Section refs:** FM-2 + ruling R4 (audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 row 1.9, §5 ruling R4, §4 wave-2 "Y-axis"; audits/review-2026-08-19/D/synth-ambition.md FM-2); the census itself audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D1 (the 626-meeting table + the honest-pooling caveat) and its R2 proposal (the "recorded perception only, never engine truth" line); audits/review-2026-08-19/A/s4-info-economy-beliefs.md; audits/audit-phase-20-preregistration.md §2 instrument I-12, §3 (the `[REVIEW-DERIVED]` I-12 row this task's pin replaces), §5 (I-12 reported as the y-axis); eval/replay_walk.py:230-258 (`ReplayWalkConfig` — every check is a profile option), :259-271 (`TickOpened`, the packet-building seam), :273-281 (`TickAdvanced.pre_state`), :283-300 (`MeetingOpened.body_id`, `None` on an emergency trigger), :353-372 (`walk_replay`); eval/kill_craft.py:324-343 (the set driver) + :400-449 (the Task-19.25 consumer pattern this module copies — kills folded off `TickAdvanced.pre_state.players`); eval/validity.py:252, :267, :278 (`resolve_roster_knobs` / `seeds_on_disk` / `roles_by_seed`); engine/visibility.py:98-127 (the Task-13.8 role-asymmetric mode — a CREWMATE observer is `same_room_only` at base) + :130-160 (`compute_visibility_for_player`, `()` for a dead observer, vented players never visible); engine/rules.py:56-77 (`resolve_kill`; :76 "kill requires same room"); engine/events.py:70-77 (`KilledEvent`: tick, actor, target, room, witnesses); orchestrator/boundary.py:44-50 (one translated action batch per tick); orchestrator/game.py:1778-1786 (the +1 agent-clock seam — packets built from the pre-advance state, `input_tick = state.tick` recorded beside the post-advance state; the review's G-37 / C-36); engine/world.py:290-312 (`room_neighbors` / `vent_neighbors` / `vent_for_room`), :420 (`load_canonical_map`); engine/maps/canonical_1.yaml:229-271 (the 6-node vent graph); eval/deduction_metrics.py:852-871 (`_wilson_interval`), :873-926 (`WilsonRateCell`); scripts/measure_baseline.py:471-479 + :497-507 (the `--funnel` / `--vj` flag pattern) + :549-555 (the vj branch); eval/report_schema.py:289 + :354-359 (`TournamentReport`'s field block); api/routes/eval.py:112-125 (`_TournamentReportEvalView`, `extra="forbid"`) and tests/api/test_leak.py:445 + :753 (the recursive served-field snapshot) — the two mirrors that decide where the block may live.
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run pytest tests/eval/test_solvability.py tests/scripts/test_measure_baseline_cli.py -q` green; `uv run python scripts/measure_baseline.py --solvability replays/samples/9p2i` prints the containment / singleton / singleton-correct / cleared-ejection cells matching the pins over 151 body meetings and 87 ejections at them, in under 60 s from a fresh clone (wall time pasted into the PR Summary); the four-set run prints 626 body meetings and 354 ejections at them.

This is the one new instrument the review sanctions, and the ruling says it is the last
(D/FINAL-synthesis.md §5 R4: "build exactly one (1.9), and say it is the last"). It answers
the question the project has never answered about itself: not "did the crew deduce?" but
"how much was there to deduce?" Computed with no LLM, from what living crewmates could
themselves perceive, the killer sits inside a computable candidate set in a large majority
of body-triggered meetings, the set is a singleton in a sixth of them and almost always the
right name — while a sixth of actual ejections land on someone the crew's own pooled
perception had already cleared. That converts the project's biggest standing admission
("deduction not demonstrated") from an apology into a measured gap with a denominator, and
it is the y-axis every later wave is read against (audit-phase-20-preregistration.md §5
lists I-12 as exactly that; §3 currently carries it as the only wholly `[REVIEW-DERIVED]`
instrument row, which Task 20.22 replaces with this task's committed pin).

The numbers in the review are review-measured and this task must RE-DERIVE them, never copy
them. Two halves of that were separated at HEAD by the planning session. The denominators
reproduce EXACTLY: walking all four committed sets under the walker and counting meetings
whose `MeetingOpened.body_id` is not `None` gives 626 body-triggered meetings and 354
ejections at them — per set, 151/87 (samples/9p2i, of 165 meetings), 35/8 (samples/4p1i, of
39), 411/250 (ml_corpus/9p2i, of 463), 29/9 (ml_corpus/4p1i, of 40). The candidate-set cells
do NOT reproduce from the review's one-sentence rule: a direct implementation of "clear every
living player whom a surviving crewmate was co-present with, in a room other than R, at the
kill tick" — observers restricted to crewmates alive both at the kill tick and at the
meeting, clearing via `compute_visibility_for_player` on the walker's PRE-advance state,
never self-clearing — measured containment 544/626, singleton 126/626 with 114/126 correct,
≤2 candidates 246/626, and 83/354 ejections landing outside the set, against the review's
581/626, 109/626, 103/109, 208/626 and 61/354. The planning probe is a cross-check, not a
target: it is tighter (it clears more), and the plausible causes are all definitional — the
reported body's own kill versus "the last kill before the meeting"; the candidate pool taken
at the meeting versus at the kill tick; whether a player's own uncorroborated self-placement
clears it; and whether clearing was read off engine perception (as here) or off the agents'
recorded rows, where the +1 agent clock lands a tick away. The FIRST job is to fix the
definition in prose, then count — the C5 define-before-counting lesson, and the reason this
contract pins the re-derived value with the review's beside it and the cause of every
difference stated.

The instrument is eval-privileged and must say so loudly. It reads engine state and then
narrows it through each surviving crewmate's own visibility — that is legitimate for a
measurement in `eval/`, and it is exactly what the crew CANNOT do, because nothing in the
game pools perception across agents. The module docstring must state that this view is never
an agent input; the review's own R2 note is the warning ("it must be built from recorded
perception only — never from engine truth — or it becomes omniscience and the firewall
argument collapses"), and a future gameplay lever that renders any of this into a prompt is
a different task under a different record. Nothing here changes a byte of gameplay: the
module is pure, offline, $0, reads committed bytes, and ships behind no lever.

The soundness argument is short and worth stating in code, because it is what makes the
ceiling a ceiling rather than a heuristic. A kill requires the killer to be in the victim's
room (engine/rules.py:76) and each player submits at most one action per tick
(orchestrator/boundary.py:44-50), so a player whom a surviving crewmate perceived in a room
other than the body's room, in the pre-advance state of the kill tick, cannot have killed at
that tick. No reachability computation is needed for the same-tick rule — doorway adjacency
and the vent graph enter only as the reason the rule is safe (a mover cannot also kill, and a
vented player is visible to nobody and therefore never cleared).

**Files in scope:**
- eval/solvability.py; (new — a replay_walk consumer computing, per body meeting, the co-presence candidate set from living crewmates' recorded perception; the cleared-ejection census; per-set summaries with Wilson intervals via eval.deduction_metrics._wilson_interval)
- tests/eval/test_solvability.py; (new — hand-built fixtures for the set logic; the four committed sets' cells pinned — the 109/626-class numbers re-derived and recorded as the pin)
- scripts/measure_baseline.py; (a `--solvability` emitter printing the cells, the pattern of the existing --vj/--funnel flags)
- tests/scripts/test_measure_baseline_cli.py
- eval/report_schema.py; (the `solvability` block's attachment seam — the provenance line plus the mirror tripwire; the block model itself lives in eval/solvability.py, because a defaulted field on TournamentReport is rejected by the two `extra="forbid"` mirrors named in Files NOT in scope)
- tests/eval/test_report_schema.py
- eval/replay_walk.py; (the profile-table docstring row for the new consumer only)

**Files NOT in scope:**
- api/ and frontend/ (display is a later phase; the instrument is CLI + pins) — in particular api/routes/eval.py's `_TournamentReportEvalView` mirror and tests/api/test_leak.py's `EXPECTED_EVAL_REPORT_FIELDS` snapshot, which is why the block's attachment is a recorded seam rather than a field here
- agents/ (reads packets via the walker; no agent code)
- eval/deduction_metrics.py (the Wilson helper is imported, not edited)
- meetings/, agents/memory/, engine/, replays/ (zero substrate movement; no replay byte moves; no prompt template is touched — the single prompt-set bump is Task 20.31's alone)
- orchestrator/replay.py (this task ships no lever, so there is nothing to register in the substrate stamp; Task 20.33 owns that registration for the levers that do)
- the compounding "unclearable tally" ranker from the same review section (the 286/463 top-ranked census) — a named non-goal: R4 sanctions ONE module producing the ceiling, not a second ranking instrument

**Definition of done:**
- [ ] Define-before-counting: `eval/solvability.py`'s module docstring states, in prose and before any cell is computed, the candidate-set rule — which meetings enter (body-triggered, `MeetingOpened.body_id is not None`), which kill anchors each one, who counts as an observer (crewmates alive at the kill tick AND at the meeting), what "could have been in the room" means and what clears a player, whether a player's own placement clears it, and what the metric does NOT measure (it assumes honest pooling; an impostor lying about co-presence could falsely clear a teammate, so containment is an upper bound).
- [ ] The candidate set is computed from living crewmates' perception only: per surviving crewmate, `engine.visibility.compute_visibility_for_player` on the walker's PRE-advance state of the kill tick (`TickOpened.state` / `TickAdvanced.pre_state` — the state the recorded actions were decided from, the kill-craft precedent at eval/kill_craft.py:420-449), never the post-advance state and never a raw roster read. A player is cleared only when a surviving crewmate OTHER than that player perceived it in a room other than the body's room; a player inside a vent is perceived by nobody and is therefore never cleared.
- [ ] `tests/eval/test_solvability.py` pins the set logic on hand-built fixtures, one behaviour per test, each of which fails when the rule is perturbed: a player cleared by one crewmate's sighting; the same player NOT cleared when its only witness is the impostor; NOT cleared when its only witness was killed before the meeting; NOT cleared when the witness stood in the body's own room; a vented player never cleared; a lights-sabotage tick (the degrade applies to everyone) leaving the rule unchanged for crew observers; an emergency meeting excluded entirely.
- [ ] `compute_solvability_report(sample_dir)` returns a frozen `SolvabilityReport` carrying, per set: games walked, body meetings, ejections at body meetings, and the cells — killer-in-set containment, singleton rate, singleton correctness, ≤2-candidate rate, and ejections landing on a player outside the set ("already cleared") — each as an `eval.deduction_metrics.WilsonRateCell` built from the imported `_wilson_interval` (the helper is imported, not copied and not edited), count-only fields so the block carries no roles, ids, or transcripts.
- [ ] Denominators re-derived and pinned per set and pooled: 626 body meetings and 354 ejections at them across the four committed sets, splitting 151/87, 35/8, 411/250, 29/9 in samples/9p2i, samples/4p1i, ml_corpus/9p2i, ml_corpus/4p1i (re-derived at HEAD by the planning session; the task re-derives them itself and the pin is its own recount).
- [ ] The four headline cells are pinned per set and pooled from the task's own recount, with the review's `[REVIEW-DERIVED]` values quoted BESIDE them in the test comments — containment 581/626, singleton 109/626, singleton correctness 103/109, ≤2 208/626, cleared-player ejections 61/354 (audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D1) — and the cause of every difference stated as a definitional sentence, not a shrug. Where the module's rule is a choice, the rejected alternative is named in the docstring with the cell it would have produced.
- [ ] The soundness argument and the clock are in the docstring: the same-room kill requirement and one-action-per-tick premises that make the same-tick rule valid; doorway adjacency (engine/maps/canonical_1.yaml, `Map.room_neighbors`) and the vent graph (`Map.vent_neighbors` / `Map.vent_for_room`) named as why no reachability search is needed here and as the machinery any window variant would use; and the two-clock convention named explicitly — every tick in this module is an ENGINE tick from the walker, the agent-facing clock runs +1 (orchestrator/game.py:1778-1786), and no agent-recorded row is consumed.
- [ ] `scripts/measure_baseline.py --solvability [set_dir]` emits the cells, human-rendered by default and as a JSON array under `--json`, following the `--vj` / `--funnel` regions exactly (its own disjoint fold region, its own branch in `main`, the existing missing-dir / empty-dir usage errors unchanged); `tests/scripts/test_measure_baseline_cli.py` pins both renderings and the committed-set cells.
- [ ] Runtime: `--solvability replays/samples/9p2i` completes in under 60 s from a fresh clone with the wall time recorded in the PR (the planning session's four-set probe walked all 300 committed games in 3.7 s wall, so this budget is loose by design — record the number, do not assume it).
- [ ] The attachment seam is recorded rather than silently skipped: `eval/report_schema.py` gains ONE provenance line on `TournamentReport` naming `eval.solvability.SolvabilityReport` as the block's home and why it is not a field here — a defaulted field is dumped as `"solvability": null` by `model_dump(mode="json")`, which the `extra="forbid"` mirror at api/routes/eval.py:112-125 rejects on the re-validation that serves `/eval/tournament-report`, and an `exclude=True` field still appears in `model_json_schema()` and so still trips the recursive snapshot at tests/api/test_leak.py:445 — both legs reproduced in the PR Summary.
- [ ] `tests/eval/test_report_schema.py` gains the tripwire that makes the seam loud: `set(TournamentReport.model_fields)` equals its pinned six names, with a failure message naming both surfaces (`api/routes/eval.py::_TournamentReportEvalView` and `tests/api/test_leak.py::EXPECTED_EVAL_REPORT_FIELDS`) as the mirrors a new field must be added to in the same change.
- [ ] Nothing recorded, nothing moved: `bash scripts/verify_samples.sh` stays green, the prompt byte-golden stays green, no file under `replays/` changes, and the module makes no LLM call and no network call.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — write the definition paragraph first, then the code. The review's cells did not
reproduce from its one-sentence rule, which means the rule underdetermines the count; every
hour spent choosing and writing down the four choices named in the WHY (which kill anchors a
meeting; when the candidate pool is taken; whether self-placement clears; engine perception
vs agent rows) is repaid at the pin.

Step 2 — copy the walk from eval/kill_craft.py:400-449. Resolve the set with
`eval.validity.resolve_roster_knobs` / `seeds_on_disk` / `roles_by_seed` and
`engine.world.load_canonical_map`, then declare one module-level `ReplayWalkConfig`
(`profile="solvability"`, a `NoReturn` violation hook raising this module's own error type,
the referee-grade check set kill-craft uses: tick hashes, duplicate meeting rows, meeting
pre/post hashes, `missing_meeting_row="violation"`, terminal tick, trailing rows, game-end
row). An instrument that silently under-measures a truncated recording is worse than one
that fails loudly.

Step 3 — fold two things off the walk. On `TickAdvanced`, index `walk_event.pre_state` by
`entry.tick` and record each `KilledEvent` keyed by the body id the engine mints
(`f"body-{target}-{tick}"`, engine/rules.py:78) so a reported body resolves to its killer,
victim, room and tick. On `MeetingOpened`, skip `body_id is None` (emergency), look the body
up, and compute the set against the pre-advance state of that kill tick and the living
roster in `walk_event.state`.

Step 4 — keep the set function pure and separately testable: a module-level function taking
the pre-advance `WorldState`, the seed's roles, the body's room, the victim and the surviving
roster, returning a frozenset of candidate ids. Every fixture test in the DoD targets that
function directly; only the census tests walk a real replay. Note while writing it that a
CREWMATE observer resolves to `same_room_only` at base visibility (the Task-13.8 asymmetry,
engine/visibility.py:98-127) so "co-present" and "visible" coincide today — call
`compute_visibility_for_player` anyway, so the instrument stays honest if that ever changes,
and say in a comment that the equivalence is current-HEAD, not an assumption.

Step 5 — cells via `_cell`-shaped construction over the imported `_wilson_interval`; do not
re-derive the interval arithmetic and do not edit eval/deduction_metrics.py. Rare cells (the
4p1i sets contain 35 and 29 body meetings) are exactly why the interval rides beside the
rate.

Step 6 — the CLI branch is a copy of the `--vj` shape: one `add_argument`, one branch in
`main` before the core folds, `_emit_solvability_json` and `_render_solvability_human`
beside their siblings, and the region kept disjoint from the 15.1 / 15.2 / 15.3 / 16.10
regions the module docstring already partitions.

**Public types introduced:**
- `eval.solvability.SolvabilityReport`
- `eval.solvability.compute_solvability_report`
- `eval.solvability.candidate_set_for_body_meeting`

**Ready-to-paste prompt:** `agent_prompts/task-20-14-solvability-instrument.md`

### Task 20.15 — The evidence-honesty instrument set: the review's numbers become committed pins
**Branch:** `phase-20-honesty-instruments`
**Depends on:** 20.14 — the solvability instrument lands the shared `scripts/measure_baseline.py` emitter slot and its CLI test first, and sets the Wilson-cell convention both instruments report through; a serialization edge on two files plus one convention, not a semantic prerequisite
**Section refs:** audits/review-2026-08-19/A/verdicts.md G-1 (false crew self-placement 148/723), G-2 (the 830-row flag census; sole-flag precision 12 right / 70 wrong; the 63.5% ungrounded sighting side; the 25.3% base rate), G-3 (fabricated completions + the +1 render calibration), G-4, G-5 (venting participants 69/707; reporters killed within 3 ticks 111/707), G-9 (movement-origin flags 38/313), G-12 (ghost-top 303/2461; 0 mismatches over 10,335 reconstructed decisions), G-25 (markers 53/971 turns, 246/1956 prompts; singular persona 1956/1956); audits/review-2026-08-19/B/verdicts.md C-3 (free zero-witness kills declined 190/415; the hash-verified reconstruction harness); audits/review-2026-08-19/A/ideas-multi-agent-researcher.md (adjacent-room STRONG 148/234); audits/review-2026-08-19/D/FINAL-synthesis.md §4 (the wave-2 pre-registration rule + the primary bars); audits/audit-phase-20-preregistration.md §2 rows I-2…I-11, §3, §4 bars 3-7; audits/audit-phase-20-planning.md §4 item 4 (the review's session scripts are NOT committed). Anchors re-verified at HEAD: eval/deduction_metrics.py:14-20 + :852 + :2629-2654; eval/replay_walk.py:237 + :359; eval/funnel.py:236-248 + :376-401; observation/service.py:219 + :605-612; agents/perception.py:90; agents/memory/store.py:1010 + :1028 + :1163 + :1194 + :1451; meetings/transcript.py:561 + :666 + :759 + :2170 + :2380; meetings/schemas.py:57-64 + :183-199 + :298-323 + :423-459; meetings/manager.py:381-383 + :3908-3912; orchestrator/replay.py:120-149 + :164-194; orchestrator/game.py:1029-1031; agents/tactical/impostor_policy.py:185 + :261 + :766 + :813 + :937 + :1008; agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:79 + :136, accusation_round_roll_call.j2:76 + :133, crewmate_report.j2:58, impostor_report.j2:59, impostor_report_roll_call.j2:69, vote_ballot.j2:74 + :100; engine/maps/canonical_1.yaml:179-207; api/replay_loader.py:1540; pyproject.toml:74-79
**Complexity:** Integration
**Record impact:** none — the module only reads committed bytes; no rendered-prompt byte and no detector output moves, and the OFF-path pins stay green unchanged.
**Measurement:** `uv run pytest tests/eval/test_evidence_honesty.py -q` green; `uv run python scripts/measure_baseline.py --honesty replays/samples/9p2i` prints all ten cell families in under 2 minutes with the pinned values (false whereabouts 148/723, sole-flag precision 12 right / 70 wrong, grounded sighting side, fabricated completions 53/529, adjacent-room STRONG 148/234, markers 53/971 turns and 246/1956 prompts, singular persona 1956/1956, venting participants 16/165, free kills declined 190/415, ghost-top 303/2461) — output pasted into the PR Summary.

The Phase-20 pre-registration is a falsifiability contract, and a contract whose
numbers cannot be re-run is not one. Ten of the thirteen instrument rows in
`audits/audit-phase-20-preregistration.md` §2 are today [REVIEW-DERIVED]: they were
measured by the 2026-08-19 review's session scripts over the committed baseline-6
bytes, and those scripts are deliberately NOT committed
(`audits/audit-phase-20-planning.md` §4 item 4 — the Markdown is the record, the
instrument is the deliverable). Until this task lands, bars 3 through 7 of the
pre-registration name a "before" that nobody can recompute, which is exactly the
failure mode this phase exists to stop repeating. This contract turns those ten
rows into one typed module, four committed sets of pins, and one command.

The cells, with the review's values as the expected pins. I-2 false crew
self-placement — a spoken `whereabouts` whose room matches the speaker's true room
at NEITHER agent-tick N nor N−1 — 148/723 = 20.5% (samples/9p2i), 402/2038 = 19.7%
(ml_corpus/9p2i), 7/78 = 9.0% (samples/4p1i), 11/79 = 13.9% (ml_corpus/4p1i)
[A/verdicts.md G-1]. I-3 sole-`alibi_vs_sighting` convicting precision, 12 right /
70 wrong = 14.6%, and the STRONG-class impostor share 33/192 = 17.2% against a
25.3% living-voter base rate — a class that is anti-informative, below chance at
one-sided p=0.0048 [G-2]. I-4 grounded sighting side, 36.5% of 170 resolvable
sides supported by the speaker's own perception, 28.8% not supported even at ±2
ticks [G-2]. I-5 fabricated `You completed` lines, 53/529 = 10.0%, 140/1528 = 9.2%,
15/65 = 23.1%, 14/64 = 21.9% [G-3, corroborated independently by B/verdicts.md
C-2]. I-6 adjacent-room STRONG share 148/234 = 63.2%
[A/ideas-multi-agent-researcher.md]. I-7 movement-origin flags 7/76, 30/233, 0/3,
1/1 — 38/313 pooled, and 38/38 of them memory-truthful and spoken-false [G-9]. I-8
dev-marker contamination, 53/971 turns and 246/1956 prompts (samples/9p2i),
139/2726 and 671/5502 (ml_corpus/9p2i), zero on both 4p1i sets [G-25]. I-9
singular-persona prompts 1956/1956 and 5502/5502 [G-25(b)]. I-10 the two context
cells: meetings with a participant inside a vent 16/165, 50/463, 1/39, 2/40 (69/707
pooled) and reporters killed within 3 ticks of their own meeting 27/165, 75/463,
5/39, 4/40 (111/707 pooled) [G-5]. I-11 the two co-intervention cells that price
Task 20.32's comparator repair: free zero-witness kills declined 190/415 = 45.8%
[B/verdicts.md C-3] and ghost-top impostor decisions 303/2461 = 12.3%, 555/6663,
0/632, 0/579 [G-12].

Three definitional collisions sit inside those numbers, and adjudicating them IS
the work — a bar measured on a definition nobody wrote down is a bar anyone can
move. First, I-3's 14.6% and its 84.4%-crewmate companion come from two different
conventions: "12 right / 70 wrong" is per-VICTIM (the only STRONG flag naming the
ejected player, denominator 82) while "77 ejections, 65 of them crewmates" is
per-MEETING (the meeting's only STRONG flag). Second, I-4's tolerance: the review
measured at-tick and at ±2, `audits/audit-phase-20-preregistration.md` §2 writes
"±1 agent tick", and production's exculpatory vouch channel uses
`SIGHTING_GROUNDING_TICK_TOLERANCE = 2` (meetings/transcript.py:666) — three
different tolerances for one cell. Third, the review disagrees with itself on the
samples-pooled fabricated-completion count: A/verdicts.md G-3's per-set table sums
to 68/594 while D/FINAL-synthesis.md §4 item 2.1 quotes 65/594. All three are
resolved here, in code, with the losing reading named in the test comment; this
task emits every reading, and Task 20.22 then names the ONE convention each of
bars 4 and 5 gates on when it restates those pre-registration rows.

Underneath every cell is one clock. The agent memory frame runs exactly +1 against
the engine/replay frame — the review proved it on 18,936/18,936 discriminating
sightings, and G-7's headline statistic was a two-clock artefact that inflated
three of Track A's own numbers by one tick. The module therefore does not assume
the offset; it asserts it on committed bytes before counting anything, so a future
clock change (roadmap item 2.14, deferred) fails here first instead of silently
re-pricing every bar.

Nothing in production moves. This is an instrument over recorded bytes: the
meeting rows already carry the transcript, the detector's `ContradictionRef` flags
and the verbatim `LLMCallRecord.prompt` text
(orchestrator/replay.py:164-194, :120-149), and everything else is reconstructed by
the hash-verifying `eval/replay_walk.py` walk. Record impact is none and prompt
templates are untouchable here — the single Phase-20 prompt-set bump is Task
20.31's alone. Downstream, `compute_evidence_honesty` is the ONLY home of these
definitions: Task 20.22 pins the pre-registration from it, Task 20.34 runs it under
the lever-ON slate for the offline counterfactual, and Task 20.36 reads it cell by
cell on the baseline-7 bytes. If a cell is re-implemented anywhere else, the
before and the after stop being comparable, which is the one failure this phase
cannot survive.

**Files in scope:**
- eval/evidence_honesty.py; (NEW — the instrument module: one frozen typed cell family per metric above, computed from committed bytes via the replay walker and the recorded transcripts/prompts; Wilson intervals imported from `eval.deduction_metrics`)
- tests/eval/test_evidence_honesty.py; (NEW — hand-built fixture tests per cell plus the four committed sets' pins, with every difference from the review's value explained in a comment)
- eval/deduction_metrics.py; (expected to need NO edit at all — Task 20.14's `eval/solvability.py` imports `_wilson_interval`, `WilsonRateCell` and `_RARE_EVENT_ADVISORY_MAX_NUMERATOR` directly from this module with no export, and that is the Wilson-cell convention this instrument reports through; another copy of the Wilson helper is forbidden)
- scripts/measure_baseline.py; (the `--honesty` emitter, following the `--vj` / `--funnel` shape at :538-584 and :618-642)
- tests/scripts/test_measure_baseline_cli.py
- agents/tactical/impostor_policy.py; (NO behaviour change — only if a pure read-only accessor must be exposed to reconstruct target rankings; prefer reconstructing via the public `decide()` on rebuilt memory as the review's C-3 harness did)
- tests/agents/test_impostor_policy.py; (the free-kill-declined pin over samples/9p2i, 190/415 — read-only reconstruction, the policy untouched)
- eval/replay_walk.py; (the profile-table docstring row for the new consumer only — the Task 19.25 drift-record obligation, exactly as Task 20.14 did for `solvability`)

**Files NOT in scope:**
- meetings/, agents/memory/, observation/, orchestrator/ (no behaviour change anywhere; the instrument reads recorded bytes and re-runs the engine, it does not edit either)
- agents/strategic/prompts/ (prompt templates are editable in Task 20.31 only, the single prompt-set bump; the singular-persona and marker cells COUNT the current bytes, they do not fix them)
- replays/ (bytes never move; no recording of any kind)
- audits/audit-phase-20-preregistration.md (Task 20.22 pins it from this task's cells; this task supplies numbers, not the memo)
- eval/solvability.py (the sibling instrument is Task 20.14's; import it if a cell needs it, never edit it)
- tests/conftest.py (out of scope — cache the per-set report in a module-scoped fixture inside the new test file instead of adding a session fixture beside `committed_9p2i_report`)
- orchestrator/replay.py (no lever, no stamp key; Task 20.33 owns substrate-stamp registration for the whole phase)

**Definition of done:**
- [ ] `eval/evidence_honesty.py` exposes exactly the ten cell families I-2…I-11 of `audits/audit-phase-20-preregistration.md` §2 as frozen typed dataclasses hung off one `EvidenceHonestyReport`, each carrying a docstring that states its numerator, its denominator, the clock convention it uses and what it does NOT measure — the `eval/deduction_metrics.py:14-20` definitions-before-counting discipline; `tests/eval/test_evidence_honesty.py` asserts each definition sentence is present verbatim so the string 20.22 copies into the memo cannot drift from the code that computes it.
- [ ] The +1 agent-clock alignment is ASSERTED, not assumed: the module resolves every recorded observation tick to the engine frame as `obs.tick − 1`, and a test reproduces the review's proof on committed bytes (for discriminating sightings — subject changed room between T−1 and T — the spoken room matches the walker's room at `obs.tick − 1` with zero exceptions). A perturbed offset makes the assertion fail (craft rule 2).
- [ ] I-2 is pinned per set with the "matches at NEITHER agent-tick N nor N−1" rule and crew/impostor split: 148/723, 402/2038, 7/78, 11/79 — or the re-derived values, each difference explained by cause in the test comment.
- [ ] I-3 ships BOTH conventions, named and separately pinned — per-victim (the only STRONG `alibi_vs_sighting` naming the ejected player: 12 right / 70 wrong = 12/82 = 14.6%) and per-meeting (the meeting's only STRONG flag: 77 ejections, 65 crewmates) — and the module states which one the pre-registration's bar 4 is measured on. The class impostor share is deduped by subject (33/192 = 17.2%) and compared against the same meetings' living-voter impostor base rate (25.3%), both reported with Wilson intervals.
- [ ] I-4 takes the tick tolerance as an explicit parameter and reports the ±0, ±1 and ±2 cells side by side (the review: 36.5% grounded at-tick, 71.2% within ±2, over 170 resolvable sides), with the resolvable / unresolvable split quoted so the denominator is never silently the full 234, and with `meetings/transcript.py:666`'s production value named in the docstring as a distinct thing from this instrument's parameter.
- [ ] I-5 is pinned per set (53/529, 140/1528, 15/65, 14/64) with the +1 render offset calibrated in-module against `task_completed` events, and the review's internal disagreement resolved in the test comment: A/verdicts.md G-3's per-set table sums to 68/594 over the two samples sets while D/FINAL-synthesis.md §4 item 2.1 quotes 65/594 — the instrument's value is authoritative and the comment says which reading was wrong and why.
- [ ] I-6 computes adjacency from `engine/maps/canonical_1.yaml`'s doorway list (never a hard-coded room table) with the tick-gap rule stated, pinned at 148/234 pooled plus per-set cells; I-7 is pinned at 7/76, 30/233, 0/3, 1/1 (38/313 pooled) with the origin-vs-destination test derived from the speaker's own `saw_player_move` render line.
- [ ] I-8 is pinned on BOTH denominators (turns 53/971 and 139/2726; prompts 246/1956 and 671/5502; zero on both 4p1i sets) reading the recorded `LLMCallRecord.prompt` bytes and `MeetingTurn.free_text`, with the marker set derived from the `meetings/manager.py` constants rather than re-typed literals; I-9 is pinned at 1956/1956 and 5502/5502, and the 4p1i sets report NOT-APPLICABLE (one impostor makes the singular persona true) rather than a zero that would read as "clean".
- [ ] I-10 is pinned per set — venting participants 16/165, 50/463, 1/39, 2/40 and reporters killed within 3 ticks 27/165, 75/463, 5/39, 4/40 — with the "within 3 ticks" window defined inclusively and the body-triggered restriction stated.
- [ ] I-11 refuses to count until the reconstruction is faithful: rebuilding each impostor's memory tick-by-tick and calling `ImpostorPolicy.decide` reproduces the recorded action stream with ZERO mismatches for every set (the review: 0 over 10,335 decisions), asserted as a hard precondition before any cell is emitted; free zero-witness kills declined pins at 190/415 with the miss-reason breakdown (168 ranking / 15 fellow-defer / 7 cover) and ghost-top decisions pin at 303/2461, 555/6663, 0/632, 0/579. A planted mismatch makes the precondition fire.
- [ ] `uv run python scripts/measure_baseline.py --honesty <set-dir>` prints every cell for one set with denominators and Wilson intervals in under 2 minutes on the author's machine (timed in the PR), and `--honesty --json` emits the machine-readable rows 20.34 consumes; `tests/scripts/test_measure_baseline_cli.py` covers both the human and JSON paths and the missing-directory exit code.
- [ ] The module is the only home of these definitions: the PR quotes a repo grep showing no second implementation of any cell, and states that 20.22, 20.34 and 20.36 consume `compute_evidence_honesty` rather than re-deriving.
- [ ] No production behaviour changes: `tests/meetings/test_prompt_byte_golden.py` and `bash scripts/verify_samples.sh` stay green, `git diff --stat` shows zero changed lines under `meetings/`, `agents/memory/`, `observation/` and `orchestrator/`, and any `agents/tactical/impostor_policy.py` diff is a pure read-only accessor with no change to an existing call site (quoted in the PR).
- [ ] Three further cells are defined in the module and pinned: the movement-origin flag cell (alibi_vs_sighting whose sighting is the origin half of a move line in the speaker's memory — 7/76, 30/233, 0/3, 1/1 review-derived), the self-placement coverage cell (share of crew whereabouts claims a rendered self-location line could have been copied from), and the two render-budget cells (mean rendered lines per snapshot; reported-testimony rows kept, by candidate-count bucket) — so the lever tasks and the counterfactual print them from one place.
- [ ] The policy-reconstruction cells (free kills declined; ghost-top decisions) live in tests/agents/test_impostor_policy.py — the file the mover-repair task owns — never in tests/eval/test_evidence_honesty.py, so the repair updates one pin set.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — read `eval/deduction_metrics.py`'s module docstring before writing a line. Its
"every metric is defined below — numerator, denominator, and what it does NOT measure —
before it is counted" rule is the house style this module extends, and the C5 lesson it
records (two audits' counts differed ONLY by definition) is the exact hazard I-3, I-4 and
I-5 carry. Write all ten definitions first, in prose, then count.

Step 2 — one walk per game serves all ten cells. Do NOT walk four times. Build a
`ReplayWalkConfig` profile in the shape of `eval/funnel.py:236-248` (verify tick hashes,
verify meeting pre/post hashes, fail loud on a missing meeting row) and drive
`eval.replay_walk.walk_replay`. Two passes keep the runtime honest: pass A reads the
meeting rows only (no engine) and indexes exactly which `(agent, tick)` perceptions the
sighting-grounding cell needs plus which impostors are alive per tick; pass B walks once
and builds `ObservationService.build_packet` packets only for those pairs, plus every
impostor tick for the policy reconstruction. Building packets for all nine agents at every
tick is the obvious way and it is the slow one.

Step 3 — the recorded bytes already carry more than you may expect. `MeetingReplayEntry`
holds `transcript` (turns, observations, claims, `free_text`), `contradictions` (the
detector's own flags, so no re-detection is needed for I-3/I-6/I-7) and `llm_calls`, whose
`prompt` field is the verbatim rendered prompt — that is where the rendered-memory lines,
the spliced dev markers and the singular-persona strings live. Read the marker prefixes
from the `meetings/manager.py` constants and the persona strings from the templates rather
than re-typing literals, so a Task-20.31 template edit shows up as a changed cell instead
of a silently stale one. STRONG vs weak is `meetings.transcript.is_weak_contradiction`,
never a substring check on the description.

Step 4 — the impostor reconstruction is the C-3 harness verbatim: rebuild each impostor's
`MemoryStore` tick-by-tick with `ObservationService.build_packet` +
`agents.perception.ingest_packet`, then call the public `ImpostorPolicy.decide(memory,
public_map)`. Derive the "free zero-witness kill" predicate from the ENGINE rules
(`engine/rules.py` legality: alive impostor, not vented, cooldown 0, an alive crewmate
co-located, zero other living non-vented non-fellow players) and not from the policy's own
`_kill_available_now`, which inherits the same `targets[0]`-only defect the cell measures.
Assert 0 mismatches against the recorded action stream BEFORE emitting; a reconstruction
that drifts must fail loudly rather than quietly re-price the co-intervention. Ghost-top is
"the top-ranked target is a player the meeting record already ejected, or one whose death
the impostor never saw" — state the two sub-populations separately (the review: 222
ejected / 81 unseen on samples/9p2i).

Step 5 — resolve the three definition collisions explicitly and cheaply. I-3: emit both
conventions as separate typed cells and let 20.22 pick; do not average them. I-4: make the
tolerance a parameter with ±0/±1/±2 emitted; the pre-registration says ±1, the review
measured at-tick, and production's vouch tolerance is 2 — three numbers, one parameter.
I-5: recount and say which of 65 or 68 was right. Every difference from a review value goes
in a test comment as a sentence with a cause, never as a silent re-pin.

Step 6 — pins live in the test file, values quoted with denominators, and the four sets get
a module-scoped cached fixture inside `tests/eval/test_evidence_honesty.py` (tests/conftest.py
is out of scope). Mark the four-set pins `slow` for tiering annotation — it carries no
default filter, so they still run in the default gate (pyproject.toml:77). Hand-built
fixtures come first for each cell's logic; the committed-set pins are the second layer, not
the only one.

Step 7 — the `--honesty` emitter mirrors `--vj`: a boolean flag, a `_render_*_human`
function, an `_emit_*_json` function, an early return in `main()`. Keep the JSON row shape
stable and documented — Task 20.34 diffs OFF against ON through it, and Task 20.36 reads it
on the baseline-7 bytes.

**Public types introduced:**
- `eval.evidence_honesty.EvidenceHonestyReport`
- `eval.evidence_honesty.compute_evidence_honesty`
- `eval.evidence_honesty.FalseWhereaboutsCells`
- `eval.evidence_honesty.SoleFlagPrecisionCells`
- `eval.evidence_honesty.GroundedSightingCells`
- `eval.evidence_honesty.FabricatedCompletionCells`
- `eval.evidence_honesty.AdjacentRoomFlagCells`
- `eval.evidence_honesty.MovementOriginFlagCells`
- `eval.evidence_honesty.MarkerContaminationCells`
- `eval.evidence_honesty.SingularPersonaCells`
- `eval.evidence_honesty.MeetingPhysicalityCells`
- `eval.evidence_honesty.ImpostorTargetingCells`

**Integration risk:**

Ten cells, four sets, one module: the risk is silently disagreeing definitions between this
module and the pre-registration text, or a cell whose reconstruction drifts from the
recorded bytes. Mitigation, in this order. Every cell's definition sentence is ONE string,
present verbatim in the module docstring and asserted by the test that 20.22 will copy into
the memo — if the memo and the module ever disagree, the test is what fails. The FSM
reconstruction asserts zero mismatches against the recorded action stream before any I-11
cell is emitted, and the hash-verifying walk profile means a drifted engine reconstruction
raises rather than counts. Every pin quotes its denominator, so a denominator change reads
as a diff and not as a moved bar.

Two second-order risks. Runtime: the honest budget is one walk per game with targeted
packet construction; if the two-pass design is skipped the emitter will not meet the
2-minute bar and the pressure will be to drop cells rather than to fix the walk — resist
that and fix the walk. Scope creep toward repair: this task MEASURES eight defects that
later tasks FIX, and every one of them is tempting to fix while you are standing in the
file. The instrument must read baseline-6 behaviour exactly as it is, including the bugs;
a cell computed against a quietly repaired code path would make the phase's before/after
comparison meaningless. If a cell cannot be computed without touching production, stop and
report rather than widening scope (craft rule 6).

**Ready-to-paste prompt:** `agent_prompts/task-20-15-honesty-instruments.md`

### Task 20.16 — Spectator action fidelity: PRETEND_TASK, EMERGENCY, REPAIR, BLOCKED in the DTO; every fetch through the client
**Branch:** `phase-20-dto-action-fidelity`
**Depends on:** 20.1, 20.2, 20.4, 20.7 — the map's body layer and its pure-derivation split land first, so the glyph work here sits on the restructured component instead of racing it; the dashboard's product-copy pass lands first, so rewriting its data fetch is a mechanical change against settled copy; the loader's corrupt-file resilience fix lands first because both changes edit the loader and the same loader test module; and the static bundle's Tournament empty-state card lands first, so routing the dashboard through the typed client preserves exactly the missing-report behaviour the bundle relies on.
**Section refs:** audits/review-2026-08-19/A/collated-findings.md §G-38; audits/review-2026-08-19/A/s2-movement-positions.md §"BUG — B3" and §2.3; audits/review-2026-08-19/B/collated-findings.md §C-8; audits/review-2026-08-19/B/frontend-a.md §F2; audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 1.10 and the sequencing-hazard note beneath the wave table; audits/review-2026-08-19/D/cross-track-map.md §G-38, §C-8. Anchors re-verified at HEAD: api/replay_loader.py:2269-2289 (`_current_action`, keyed on `last_action` alone), :1542 (its only call site), :1475-1488 (`_tick_view`), :1205-1206 (the walk that already holds the tick's deserialized `actions`); api/schemas.py:249-251 (the inline seven-value `Literal`), :49 (`VIEW_MODEL_VERSION = "1"`), :622 (the `EvidenceCategory` TypeAlias pattern to mirror); engine/tick.py:215-220 (`_with_actor_last_action` — only an ACCEPTED action updates the label), :271-306 (`_apply_do_task` rejects an actor that owns no instance of the map task, at :290-293), :382 (a killed victim's `last_action` is cleared), :593-604 (rejections become `ActionRejectedEvent`; a `MEETING` phase change returns early and silently DROPS every later action in the list); engine/events.py:146-151 (`MeetingTriggeredEvent.actor`), :28-33 (`ActionRejectedEvent.actor` / `.action`); observation/service.py:435-436 + :438-455 (the fake-task lever keys the crew's `action="task"` off exactly that rejection event); scripts/gen_frontend_types.py:94 (the `AgentAction` alias tuple); frontend/src/types/api.ts:22, :25, :116; frontend/src/assets/map/glyphs.ts:66-77 (`ACTION_GLYPH` is an exhaustive `Record` over the alias); frontend/src/components/MapView.tsx:452-455 (`selfActionGlyph`), :633 (omniscient tokens), :647 (the fog view's SELF token); frontend/src/api/client.ts:117-133 (`assertViewModelVersion`), :135-159 (`getJson`, module-private), :319-321 (`getRubric`); frontend/src/components/TournamentDashboard.tsx:1119-1154; frontend/src/components/BeliefMatrix.tsx:33-48; tests/api/test_replay_loader.py:136.
**Complexity:** Medium
**Record impact:** none — the projection is read-side only: no recorded `actions` row, no engine transition and no `state_hash` moves, so nothing here is re-recorded and no committed replay changes.
**Measurement:** `uv run pytest tests/api/test_replay_loader.py tests/api/test_view_model.py -q` green with the action-class census pinned over `replays/samples/9p2i` (415 impostor `do_task` intents leave the stale-label classes: IDLE 0 / MOVING 0 / TASK 0, with at most 5 of them landing on BLOCKED; 14 EMERGENCY; 83 REPAIR); `uv run python scripts/gen_frontend_types.py --check` clean; `cd frontend && npm run tsc:check && npm run test` green; and `grep -rn 'fetch(' frontend/src --include='*.tsx' --include='*.ts' | grep -v src/api/client | grep -v '.test.'` prints nothing (it prints exactly 2 lines at HEAD).

The spectator's `current_action` reports the last action the engine ACCEPTED, not the action
the agent took, and four whole classes of behaviour are therefore rendered as a lie.
`engine/tick.py:215-220` only stamps `last_action` from inside a successful handler, so a
rejected or dropped intent leaves the previous tick's label standing; `_current_action` at
api/replay_loader.py:2269 then reads that stale label and collapses `emergency` into REPORT
and `repair_sabotage` into TASK on top. The A-track census
(audits/review-2026-08-19/A/s2-movement-positions.md §"BUG — B3") measured the damage over
the 300 committed games: 1,747 impostor fake `do_task` intents render IDLE 800 / MOVING 844
/ **TASK 0**; 112 emergency-button presses render REPORT; 408 `repair_sabotage` intents
render TASK 302 / MOVING 95 / IDLE 11; and 1,964 agent-ticks show MOVING while the token
does not move. Those three intent totals were recomputed at HEAD from the committed replay
bytes for this contract and match exactly (1,747 / 112 / 408 across
`replays/samples/{9p2i,4p1i}` and `replays/ml_corpus/{9p2i,4p1i}`); over
`replays/samples/9p2i` alone the same census reads 415 / 19 / 114.

The fake-task case is the one that costs the project something.
`observation/service.py:435-455` already keys the crew's witnessed `action="task"` off the
very `ActionRejectedEvent` the impostor's `do_task` produces — a co-located crewmate
correctly sees the impostor working, which is the point of the fake-task lever — while the
omniscient spectator dump shows the same agent aimlessly MOVING. The replay viewer, whose
whole job since Phase 12 is to make the deception legible, is blind at exactly the moments
the deception is succeeding. Every byte needed to fix this is already recorded: the per-tick
`actions` array carries every submitted intent including the rejected ones, and the walk at
api/replay_loader.py:1205-1206 already has it in hand and throws it away. This is a
projection bug, not a data gap.

The fix is additive and mechanical: name the DTO field's value set
(`api.schemas.CurrentAction`, mirroring the `EvidenceCategory` TypeAlias at
api/schemas.py:622), add PRETEND_TASK, EMERGENCY, REPAIR and BLOCKED, and derive the label
from THIS tick's recorded intent plus its outcome instead of from the last accepted action.
A label can then never be stale: the "MOVING while standing still" class disappears by
construction rather than by patching, because the projection no longer has a previous tick
to inherit from.

Changing the DTO bumps `VIEW_MODEL_VERSION`, and that is what forces the second half of this
task into the same PR. `VIEW_MODEL_VERSION` has never been bumped, so C-8 has been latent:
`frontend/src/api/client.ts:117-133` is the one runtime check standing between a
version-skewed server and silently-wrong UI, and two components skip it with a bare `fetch`
— `TournamentDashboard.tsx:1122` re-implements `getRubric` by hand for one of only two
stamped payloads, and `BeliefMatrix.tsx:42` does the same for an endpoint the client has no
getter for (audits/review-2026-08-19/B/frontend-a.md §F2; the grep returns exactly those two
lines at HEAD). On the first bump, a stale build talking to a fresh server fails loud in the
tour and the picker and renders a thousand lines of statistics from foreign bytes in the
dashboard. Shipping the bump without the routing fix would be shipping the failure mode;
audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 1.10 names them as one item for exactly
this reason.

**Files in scope:**
- api/replay_loader.py; (`_current_action` derives PRETEND_TASK / EMERGENCY / REPAIR / BLOCKED from the recorded intent + outcome)
- api/schemas.py; (the CurrentAction enum; viewModelVersion bump)
- frontend/src/types/api.ts; (regenerated by scripts/gen_frontend_types.py --check)
- frontend/src/types/api.fidelity.ts; (same)
- frontend/src/components/AgentToken.tsx; (glyphs for the new classes)
- frontend/src/components/MapView.tsx; (selfActionGlyph mapping)
- frontend/src/components/TournamentDashboard.tsx; (the raw fetch routed through api/client getRubric/getJson)
- frontend/src/components/BeliefMatrix.tsx; (same)
- frontend/src/api/client.ts; (a shared getJson with the version guard if missing)
- frontend/src/api/client.test.ts
- tests/api/test_replay_loader.py; (the four action classes pinned over the committed samples/9p2i replays: 410 of the 415 impostor fake tasks → PRETEND_TASK and the other 5 → BLOCKED, of the 1,747 corpus-wide; emergency → EMERGENCY; meeting-frozen move → BLOCKED)
- tests/api/test_view_model.py; (the version bump pin)
- frontend/src/assets/map/glyphs.ts; (ACTION_GLYPH gains the four classes; the alias rename lands here)
- scripts/gen_frontend_types.py; (the _ENUM_ALIASES entry for the widened action enum)

**Files NOT in scope:**
- engine/ and observation/ (the recorded actions already carry the intent; this is a DTO projection and no engine byte moves)
- meetings/ (no transcript change)
- the As-agent fog layer's witnessed actions (unchanged: co-located crew already see `task` for a fake task, via `visibility.visible_players[].action`, which is a different field from `current_action`)
- frontend/src/assets/map/*.svg (the four new classes reuse committed glyph assets; no new artwork here)
- scripts/build_demo_bundle.py (the bundle bakes payloads at build time and pins no version of its own)
- eslint.config.js (the no-raw-fetch guard ships as an executable test, not a lint-config edit)
- agents/strategic/prompts/ (a prompt-template edit belongs only to the single Phase-20 prompt-set bump, never here)

**Definition of done:**
- [ ] `api.schemas.CurrentAction` exists as a documented `TypeAlias = Literal[...]` in the
  shape of `EvidenceCategory`, carries the seven existing values plus PRETEND_TASK,
  EMERGENCY, REPAIR and BLOCKED, and `AgentTickStateView.current_action` is annotated with
  it instead of the inline literal; the docstring states that the label describes THIS
  tick's recorded intent and its outcome, never the last accepted action.
- [ ] `_current_action` derives the label from the tick's recorded action for that actor
  plus this tick's events, under a stated precedence: an intent the engine never attempted
  (positioned after the tick's `MeetingTriggeredEvent` actor) or rejected because the actor
  died earlier in the same tick → BLOCKED; an impostor `do_task` → PRETEND_TASK; any other
  rejected intent → BLOCKED; an accepted `emergency` → EMERGENCY, `repair_sabotage` →
  REPAIR, and the existing five mappings unchanged; no recorded intent for that actor this
  tick (a dead agent, the synthesized Start frame) → IDLE.
- [ ] The census is pinned in `tests/api/test_replay_loader.py` over the committed
  `replays/samples/9p2i` set: all 415 impostor `do_task` intents leave the stale-label
  classes (IDLE 0 / MOVING 0 / TASK 0 for that intent), at most 5 of them read BLOCKED (the
  intents sharing a tick with an earlier meeting trigger) and the other 410 read
  PRETEND_TASK; 14 agent-ticks read EMERGENCY and 83 read REPAIR (the 19 `emergency` and 114
  `repair_sabotage` INTENTS less the 5 dropped after an earlier meeting trigger and the 31
  rejected, which read BLOCKED); and no agent-tick anywhere in the walk
  carries a label inherited from a previous tick. The PR quotes the produced census table.
- [ ] The gate bites: a unit test builds a tick in which an impostor submits `do_task` and
  asserts PRETEND_TASK, and asserts that the pre-fix derivation (the actor's `last_action`
  at that moment) would have produced a DIFFERENT label — so reverting the projection fails
  the test rather than passing it silently.
- [ ] `VIEW_MODEL_VERSION` is bumped in api/schemas.py; `tests/api/test_view_model.py` pins
  the new value and its lockstep appearance in the regenerated `frontend/src/types/api.ts`;
  `uv run python scripts/gen_frontend_types.py --check` is clean with `api.ts` and
  `api.fidelity.ts` committed.
- [ ] The generated TypeScript alias and the Python alias carry ONE name — `CurrentAction` —
  with all eleven values, and every consumer of the old `AgentAction` alias is updated;
  nothing in the frontend indexes the action set with a mapping that silently omits a value
  (an exhaustive mapping stays exhaustive and fails to compile if a value is added later).
- [ ] The map renders the new classes with committed glyph assets and no new artwork:
  PRETEND_TASK and BLOCKED are drawn as an INTENT (a hollow chip variant on `AgentToken`,
  glyphs `task` and `idle` respectively), EMERGENCY and REPAIR as resolved outcomes (solid
  chip, glyphs `report` and `task`); IDLE still draws nothing. The As-agent view is
  byte-for-byte unchanged: the fog branch still reads `witnessedActionGlyph(vp.action)` for
  every other agent and only the selected agent's own token reads `current_action`.
- [ ] `TournamentDashboard` uses `getRubric(seedSet)` with `err instanceof ApiError &&
  err.status === 404` for the absent-rubric state (the pattern `ReplayPicker` already uses),
  and `BeliefMatrix` uses a new exported `getBeliefFrames(gameId, set)` on `api/client.ts`;
  neither component constructs a URL or calls `fetch` any more.
- [ ] `frontend/src/api/client.test.ts` asserts that a stamped-but-skewed payload throws
  `ViewModelVersionError` through BOTH newly-routed getters, that a non-200 from the belief
  route throws `ApiError` rather than a bare `Error`, and — as a source scan over
  `frontend/src` — that no file outside `src/api/client.ts` calls `fetch(`; the scanner is
  exercised against a planted fixture string so it is proven to bite. The belief payload is
  a bare array and therefore carries no stamp today: the test says so explicitly rather than
  implying a guard that is a no-op on that shape.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — read the outcome, not the state. The walk at api/replay_loader.py:1205-1206 already
holds both halves: `actions` (the deserialized recorded intents for this tick) and `events`
(what `advance_tick` did with them). Thread `actions` through `_tick_view` as a keyword
argument alongside the events it already receives, and build one small per-tick lookup
before projecting the agents — actor to submitted action, plus the set of actors carrying an
`ActionRejectedEvent`, plus the drop cut-off. The synthesized Start frame at :1186 passes an
empty sequence and every agent stays IDLE, which is what tests/api/test_replay_loader.py:136
already pins.

Step 2 — the drop rule is exact, not heuristic. `advance_tick` returns the moment a handler
flips the phase to MEETING (engine/tick.py:599-600), so every action positioned strictly
AFTER the triggering actor's action in the recorded list was never attempted and emitted no
event at all. `MeetingTriggeredEvent.actor` names the trigger, so the cut-off is the index
of that actor's action in `actions`. Over `replays/samples/9p2i` this is what puts up to 227
move intents and up to 5 impostor `do_task` intents into BLOCKED; measure the real split
rather than asserting these bounds.

Step 3 — PRETEND_TASK reads the same evidence the fog layer reads. An impostor owns no task
instance, so `_apply_do_task` always rejects it (engine/tick.py:290-293) and
observation/service.py:435-436 turns that same `ActionRejectedEvent` into the crew's
`action="task"`. Deriving PRETEND_TASK from the recorded intent plus the actor's role keeps
the two projections describing one event; say so in a comment so nobody later "fixes" one
side alone. Role is on `state.players[pid].role`, already used two lines away by
`_task_progress`.

Step 4 — no new leak. `AgentTickStateView` is the omniscient spectator DTO and
`ReplayView.players[].role` is already served, so PRETEND_TASK exposes nothing new; the
firewall question is only whether an As-agent perspective can reach it. MapView.tsx:647
reads `current_action` for the SELECTED agent's own token and MapView.tsx:654-662 reads
`visibility.visible_players[].action` for everyone else, so the answer today is no — keep it
that way and assert it in the test rather than in prose.

Step 5 — the version bump is a two-file lockstep plus a regeneration. `api/schemas.py:49` is
the source; `frontend/src/types/api.ts:22` is generated from it; the fidelity fixture at
frontend/src/types/api.fidelity.ts is rebuilt by the same script from a 4p1i game that
submits no actions, so its only diff should be the stamp string. If more than the stamp
changes there, stop and understand why before committing it.

Step 6 — grep the blast radius before touching the alias. At HEAD exactly one file imports
the generated action alias (the map's glyph registry) and one story types a prop off
`AgentTickStateView["current_action"]`; `tests/api/test_schemas.py` constructs views with
existing values and stays valid because the change is additive. If your grep finds a
consumer outside the files in scope, stop and ask rather than widening.

Step 7 — the client is the only place that knows a URL. Copy `ReplayPicker`'s existing 404
handling into the dashboard rather than inventing a second shape, and give the belief route
a real getter next to `getMemory` instead of exporting `getJson` raw — an exported `getJson`
is a new bypass wearing a seatbelt.

**Public types introduced:**
- `api.schemas.CurrentAction`

**Ready-to-paste prompt:** `agent_prompts/task-20-16-dto-action-fidelity.md`

### Task 20.17 — Gate hermeticity: the documented restore and the documented gate stop excluding each other; the env surface is pinned
**Branch:** `phase-20-gate-hermeticity`
**Depends on:** none (root)
**Section refs:** audits/review-2026-08-19/B/tests-ci-tooling.md §2 P1-3 (C-96, the mypy facet) + §2 P1-2 (C-35, the env surface), §1 items 7-8, §6 recommendations 2-3, Appendix (both repro commands); audits/review-2026-08-19/B/collated-findings.md rows C-96 + C-35; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 row 1.11; audits/review-2026-08-19/D/cross-track-map.md rows C-96 + C-35; audits/audit-phase-19-close.md §1 F1 (both facets, quoted); pyproject.toml:45-61 (`[tool.mypy]`, the exclude regex at :61); scripts/fetch_evidence.sh:44-45 (`COEVO_DEST` + `SLATE_DEST`), :347-372 (`write_gitignore`); scripts/verify_ml_evidence.py:110-111 (the same two destinations as constants); tests/scripts/test_verify_ml_evidence.py:138-156 (F1's pytest facet, fixed at HEAD by rebuilding coevo/ from `git ls-files`); tests/conftest.py:1-38 (the diagnosis of exactly this failure class) + :57-61 (the one-variable guard); the three hand-rolled cleaners tests/scripts/test_record_ml_corpus.py:117-129, tests/scripts/test_refresh_samples.py:537, tests/api/test_replay_loader.py:959-964; the three opt-in gates tests/llm/test_client.py:619 + :647, tests/llm/test_ollama_client.py:845 + :879 + :897, tests/eval/test_performance.py:30 + :72; tests/experiments/test_torch_probe_excluded.py:92-112 (`test_mypy_exclude_covers_the_probe_directory`, the precedent for pinning a mypy exclude both ways); docs/artifacts.md:58-69 (the `.gitignore` rule) + :116-122 (the restore commands); scripts/check.sh:15-21 (the gate legs); AGENTS.md craft rules 2, 5, 6
**Complexity:** Small
**Record impact:** none — tooling and test isolation only; no engine, detector, memory-render or prompt byte moves, and no committed replay is read differently
**Measurement:** `bash scripts/fetch_evidence.sh && bash scripts/check.sh && bash scripts/fetch_evidence.sh --clean && bash scripts/check.sh` — all four legs green, with mypy reporting the SAME source-file count in both states (review-measured today: 354 clean vs *"Found 15 errors in 3 files (checked 358 source files)"* restored); `AILIBI_MAX_COST_USD=0.001 uv run pytest tests/eval/test_balance_eval.py -q` green (review-measured today: 2 failed); `uv run pytest` under every non-gate `AILIBI_*` name exported to a valid value reports the same passed/skipped/xfailed counts as the bare run.

Two steps this repo documents — `bash scripts/fetch_evidence.sh` (docs/artifacts.md:116-122) and
`bash scripts/check.sh` (the one-command gate, AGENTS.md) — currently exclude each other. `ruff`
honours `.gitignore` and `mypy` does not, so after the restore mypy walks the four untracked
helper scripts the slate payload puts under `training/reports/_finalist_eval_raw/`
(`assemble-row.py`, `make-owner-brief.py`, `score-arm.py`, `sync-jsonl.py` — the manifest's §7
digest rows) and reports *"Found 15 errors in 3 files (checked 358 source files)"* against the
clean state's 354. The phase-19 close hit this at its own contract-mandated gate rerun and
recorded it as F1 — routed, not fixed (audits/audit-phase-19-close.md §1). F1's pytest facet WAS
closed at HEAD: the scratch tree now rebuilds `coevo/` from `git ls-files` output instead of
symlinking the live directory (tests/scripts/test_verify_ml_evidence.py:138-156). The mypy facet
is untouched, and the review re-verified the mechanism independently in scratch
(audits/review-2026-08-19/B/tests-ci-tooling.md §2 P1-3: `git check-ignore` hits, `ruff check .`
clean, `mypy .` errors). The fence has to be stated in `pyproject.toml`, because a `.gitignore`
fences `git add`, not a type checker — and docs/artifacts.md:58-69 currently states the `.gitignore`
half as though it were the whole guarantee.

The second half is the environment the suite runs in. tests/conftest.py:57-61 is the only env
guard in 4,621 default-tier tests: one `monkeypatch.setenv(ENV_PROVIDER, PROVIDER_FAKE)`, against
43 distinct `AILIBI_*` names in the tracked `.py`/`.sh` tree (re-counted at HEAD: 43). Review-
measured: `AILIBI_MAX_COST_USD=0.001` alone fails 2 tests in tests/eval/test_balance_eval.py
(*"LLM budget exceeded on cost_usd: current=0.0 + delta=0.072942 > cap=0.001"*), and a realistic
13-variable operator environment over `tests/api tests/scripts tests/eval` gives **10 failed, 1541
passed**. The loud direction is a spurious red for anyone who has ever exported a documented knob;
the silent direction is worse — an ambient value that makes a test pass which would otherwise fail
is undetectable. The conftest's own opening docstring diagnoses exactly this failure class and
then fixes one variable instead of the category, and three modules have since hand-rolled the
categorical fix locally (tests/scripts/test_record_ml_corpus.py:117-129,
tests/scripts/test_refresh_samples.py:537, tests/api/test_replay_loader.py:959-964). Promote the
pattern to the root conftest and every machine's suite runs in CI's environment, which exports
none of these.

The allow-list is where this task can do harm, so it is specified rather than left to taste. Three
families are opt-in BY environment variable — `AILIBI_RUN_REAL_PROVIDER_TESTS`,
`AILIBI_RUN_OLLAMA_TESTS`, `AILIBI_RUN_PERF_BENCHMARK`. Each is read by a module-level `skipif` at
import time AND re-read at call time by a meta-test that asserts the two agree
(tests/llm/test_client.py:619 + :647; tests/llm/test_ollama_client.py:845 + :879;
tests/eval/test_performance.py:30 + :72), so a naive namespace clear turns all three red the moment
an operator exports a gate. The gate keys therefore survive the clear unconditionally; the
credentials and endpoints those families read at call time (`ANTHROPIC_API_KEY`,
`FEATHERLESS_API_KEY`, `AILIBI_LLM_MEETING_MODEL`, `AILIBI_OLLAMA_HOST` — tests/llm/test_real_provider.py:62
and :664-668, tests/llm/test_ollama_client.py:897) survive only while their gate reads `1`. A stray
API key with the gates off is cleared, which is the safety direction: no test can fall into a paid
path from ambient state.

Nothing about game behaviour moves. The by-product is that the subprocess families which hand
`dict(os.environ)` to a child (tests/scripts/test_verify_samples.py:152, :184,
tests/api/test_cwd_independence.py:62, tests/scripts/test_verify_ml_evidence.py:176) inherit the
cleaned parent environment for free — which is where the review's 10 failures lived. This task is
also the precondition for running the suite in parallel: a shared, ambient-dependent process
environment is not parallel-safe, and the task that lands `pytest-xdist` sits directly downstream.

**Files in scope:**
- pyproject.toml; ([tool.mypy] exclude gains the two restore destinations)
- tests/conftest.py; (an autouse session fixture that clears/pins the whole AILIBI_* namespace to the documented bare defaults, with an allow-list for the opt-in gates)
- tests/scripts/test_verify_ml_evidence.py; (if its scratch-tree case still couples to the restored payload — make it independent of the checkout state)
- docs/artifacts.md; (the restore + gate sentence made true)
- tests/test_env_hermeticity.py; (new: asserts the in-process AILIBI_* surface the fixture guarantees)

**Files NOT in scope:**
- scripts/fetch_evidence.sh (the restore is correct; the gate's walkers are the defect — the new test READS its destination assignments, never edits them)
- training/reports/_finalist_eval_raw/ and training/artifacts/coevo/ (operator-machine slate scripts and campaign evidence; not held to the repo bar — excluded from the walk, not fixed, and their restored bytes stay untracked by design)
- scripts/check.sh (its legs are correct as written; the parallel invocation belongs to the xdist task)
- .env.example, README.md (documenting the operator knobs is the first-run-quiet task's item; this task changes what the SUITE reads, not what the docs advertise)
- tests/scripts/test_record_ml_corpus.py, tests/scripts/test_refresh_samples.py, tests/api/test_replay_loader.py (the three hand-rolled cleaners stay: each builds a CHILD env explicitly and remains correct over a clean parent; collapsing them onto the new fixture is a follow-up, not this task)
- tests/llm/, tests/eval/test_performance.py (the opt-in gates are read as evidence and must keep behaving exactly as they do today)
- orchestrator/replay.py, llm/ (read for the live `AILIBI_*` surface; never edited)

**Definition of done:**
- [ ] Verify-then-fix, recorded in the PR: `bash scripts/fetch_evidence.sh` then `uv run mypy .` reproduces the F1 mypy facet at HEAD (quote the error line and the file count), and the same restore then `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` is quoted to show whether the pytest facet is still closed.
- [ ] `[tool.mypy] exclude` covers both destinations `scripts/fetch_evidence.sh` restores into (`training/artifacts/coevo/`, `training/reports/_finalist_eval_raw/`) and swallows no tracked Python: a test in tests/scripts/test_verify_ml_evidence.py derives the two roots from the script's own `COEVO_DEST=`/`SLATE_DEST=` assignments (cross-checked against `verify_ml_evidence.py:110-111`), asserts a path under each is excluded, and asserts the two ADDED alternatives match ZERO paths in `git ls-files '*.py'` (the whole regex cannot: its pre-existing `experiments/lab/` + `design/` alternatives legitimately cover 29 tracked files).
- [ ] That test can fail: it applies its own coverage helper to a deliberately narrowed pattern (the exclude without the two new alternatives) and asserts that pattern does NOT cover the destinations — so a future edit that drops one alternative is caught, not merely described (AGENTS.md craft rule 2).
- [ ] After `bash scripts/fetch_evidence.sh`, `uv run mypy .` prints the same "checked N source files" count as the clean state — the restored `.py` files are outside the walk, not merely error-free — and the full `bash scripts/check.sh` is green in BOTH states (restored, and after `--clean`), with the final line of each run quoted in the PR.
- [ ] tests/conftest.py carries one autouse session fixture that clears every `AILIBI_*` name plus `ANTHROPIC_API_KEY`/`FEATHERLESS_API_KEY` from the process environment and re-pins `AILIBI_LLM_PROVIDER=fake`; the clear is derived BY PREFIX from the live environment (never from a hardcoded list of the 43 names), and the fixture's docstring enumerates the allow-list with the reason each entry is preserved.
- [ ] The allow-list holds: with each of the three opt-in gates exported to `1` in turn, the three marker meta-tests (`uv run pytest tests/llm/test_client.py tests/llm/test_ollama_client.py tests/eval/test_performance.py -k "marker_is_skipif or marker_is_opt_in" -q`) pass; with the gates unset and `ANTHROPIC_API_KEY` exported, a test that prints the in-process environment sees no key — quoted in the PR.
- [ ] Hermeticity is measured, not asserted: with every non-gate `AILIBI_*` name exported to a valid value, `uv run pytest` reports the same passed/skipped/xfailed counts as the bare run, and `AILIBI_MAX_COST_USD=0.001 uv run pytest tests/eval/test_balance_eval.py -q` is green (review-measured today: 2 failed). Both invocations and both outputs go in the PR Summary.
- [ ] tests/scripts/test_verify_ml_evidence.py is independent of the checkout state: the whole file is green with the evidence restored AND after `--clean`, both quoted; any case still reading the working tree where it means the committed inventory is switched to the `git ls-files` pattern already used at :138-156.
- [ ] docs/artifacts.md states the relationship truthfully in the class-(c) rule (:58-69) and beside the restore commands (:116-122): restored bytes are outside `git add` (the per-destination `.gitignore`) AND outside the strict type gate (the pyproject exclude), so the documented restore and the documented gate compose in either state. No sentence claims or implies that the `.gitignore` alone makes the restore gate-safe.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — the fence. pyproject.toml:61 is one regex of alternatives; add `^training/artifacts/coevo/`
and `^training/reports/_finalist_eval_raw/` to it and extend the comment above it with ONE sentence
of intent (these two roots are restore destinations for untracked class-(c) evidence; mypy has no
gitignore awareness, so the fence lives here) — intent, not a changelog. Neither root holds a
tracked `.py` today (checked: `git ls-files training/artifacts/coevo training/reports | grep '\.py$'`
is empty), so the exclusion costs zero coverage; the DoD's zero-tracked-Python assertion is what
keeps that true. The tempting alternative is mypy's own `exclude_gitignore = true` (the pinned
mypy 1.20.2 supports it) — do not take it: it makes the type-checked set a function of transient
untracked state, and it would silently drop any future gitignored production path from the strict
gate. The fence should name what it excludes.

Step 2 — the drift test. tests/experiments/test_torch_probe_excluded.py is the working precedent:
`tomllib.loads(pyproject)` → `re.compile(exclude)` → assert it matches the probe paths and no
production path. Do the same here, but read the two destinations from
`scripts/fetch_evidence.sh` itself (the `COEVO_DEST=`/`SLATE_DEST=` lines, stripped of
`$REPO_ROOT/`) so the pair cannot drift, and cross-check them against `verify_ml_evidence.py`'s
`COEVO_DEST`/`SLATE_DEST` constants, which the module already imports as `vme`. mypy matches its
exclude against relative POSIX paths, so build the probe paths as `f"{dest}/x.py"`.

Step 3 — the fixture. Keep it in the existing autouse slot rather than adding a second layer: one
session-scoped autouse fixture entered through `with pytest.MonkeyPatch.context() as mp:` (the
function-scoped `monkeypatch` fixture cannot be requested at session scope), clearing
`[k for k in os.environ if k.startswith("AILIBI_")]` plus the two provider keys, then re-pinning
the fake provider. Per-test `monkeypatch.setenv`/`delenv` still works exactly as before — those are
deltas over the cleared baseline and pytest undoes them per test. Order matters if you keep a
second function-scoped fixture: the clear must be established before any fixture that sets a value.
The allow-list is read BEFORE the clear and re-applied after it: the three gate keys always, their
credentials/endpoints only while the matching gate reads `1`.

Step 4 — blast radius before scope (AGENTS.md craft rule 6). `grep -rn "os.environ\|os.getenv"
tests/ --include='*.py'` returns ~35 hits; walk them and classify each as (a) an explicit child-env
construction (unaffected — it filters an already-clean parent), (b) an opt-in gate (allow-listed),
or (c) an ambient read that should not exist. The review's recommendation 2 also suggests an
opt-out MARKER for env-selection tests; today the env-selection tests pass an explicit `env=`
mapping to `build_default_client` and need nothing, so add a marker only if class (c) turns out
non-empty — and if you do, register it in pyproject's `markers` list with a one-line reason.

Step 5 — the docstring. tests/conftest.py's opening docstring is the diagnosis of exactly this
failure class, written for one variable; rewrite it to state the current contract (the suite runs
in CI's environment; here is the allow-list and why), keeping the current-state reasoning about the
provider and the session-scoped report fixture and dropping the narration that is now history —
provenance at most one trailing line (AGENTS.md craft rule 1).

Budget note: `bash scripts/check.sh` runs ~13.5 minutes (close-audit measured 13m34s at the phase-19
close), so the four-leg measurement is roughly half an hour of wall time plus a ~300 MiB fetch; the
restore itself takes ~11 s. Network is used only by the evidence fetch — ordinary tooling network,
which the standing designer ruling permits; nothing here records, and every other leg is offline.

**Ready-to-paste prompt:** `agent_prompts/task-20-17-gate-hermeticity.md`

### Task 20.18 — The default test tier runs in parallel: pytest-xdist + the session-scoped replay fixture
**Branch:** `phase-20-xdist-suite`
**Depends on:** 20.9, 20.17 (the firewall test must plant into a temp tree first — a test that writes fixed paths into the live checkout is what makes worker-beside-worker execution structurally unsafe, not merely slow; and the whole `AILIBI_*` namespace must be pinned in the root conftest first, because in a parallel log an order-dependent failure and an ambient-environment failure are indistinguishable, so the hermeticity work has to be finished before "green three times under `-n auto`" means anything)
**Section refs:** C-48 and C-107 (audits/review-2026-08-19/B/collated-findings.md, the C-48 and C-107 rows); audits/review-2026-08-19/B/perf-runtime.md §F8 and §6 R8; audits/review-2026-08-19/B/tests-ci-tooling.md §P1-1, §P1-4, §P2-2, §P2-3, §P2-4, §P2-11; audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 1 row 1.12; audits/review-2026-08-19/D/synth-pragmatic.md P6; audits/review-2026-08-19/D/cross-track-map.md (the C-42/C-43/C-46/C-48 perf row and the C-34 row naming this task as blocked by the live-tree plant). Anchors re-verified at HEAD: pyproject.toml:70-86 (`[tool.pytest.ini_options]`; `addopts` at :81; the unused `slow`/`perf` markers at :84-85), :88-100 (`[dependency-groups] dev`, `pytest==9.0.3` at :97); scripts/check.sh:21 (the single `uv run pytest`), :9-13 (the `AILIBI_SKIP_FRONTEND` loud-validation idiom the serial hatch copies); scripts/setup_env.sh:27 (`uv sync --locked --group dev`); .github/workflows/ci.yml:47-48 (the Python job runs `bash scripts/check.sh`, not pytest directly); .github/workflows/campaign-tier.yml:64 (`uv run pytest -m campaign` — the only literal pytest invocation in CI); tests/conftest.py:64-65 (the repo-root and committed-9p2i path constants), :152-177 (Task 20.17's autouse session-scoped hermetic env guard, which now carries the provider pin), :180-201 (the committed-9p2i session fixture — no longer the only session-scoped fixture in the suite); tests/eval/test_gate_spec_metrics.py:983 (a second `build_report(_COMMITTED_9P2I_DIR)`); tests/eval/test_kill_craft.py:46-58 and :273-276, tests/eval/test_deduction_metrics.py:1369 (the 4p1i kill-craft walk computed three times per run, one of them a deliberate determinism re-derivation); tests/eval/test_funnel.py:582, tests/agents/test_beliefs_hard_evidence_gate.py:775, tests/agents/test_beliefs.py:3673 (the 9p2i information-funnel walk computed in three modules); tests/experiments/test_torch_probe_excluded.py:168-178 (the second live-tree plant the review named — MOVED to `tmp_path` by Task 20.9, so it no longer races `test_no_production_package_imports_the_probe` at :157-165 whose `_PRODUCTION_ROOTS` at :60-71 includes `training`); tests/agents/test_memory_rendering.py:32 and tests/eval/test_prompt_regression.py:43 (the cwd-relative fixture roots); tests/training/test_suite_tiers.py:102-116 (the marker-registration pin)
**Complexity:** Medium
**Record impact:** none
**Measurement:** `time uv run pytest -n auto` under 90 s wall and green on three consecutive runs on the 10-core review machine class (the three exit codes and the three wall times pasted into the PR Summary); `time uv run pytest` serial still green with its wall time quoted beside the review's 337.96 s baseline; `AILIBI_PYTEST_SERIAL=1 bash scripts/check.sh` green and demonstrably serial; the before/after count of test modules that independently walk the committed sets quoted from the same grep.

The default gate is 337.96 s serial — 4,621 passed, 20 skipped, 317 deselected, 3 xfailed — on a 10-core machine, and 783 s in CI, review-measured over this HEAD (audits/review-2026-08-19/B/collated-findings.md C-48; audits/review-2026-08-19/B/perf-runtime.md §F8). Fifty-nine percent of that wall time lives in 60 tests, and a third of *that* is fixture *setup* rather than assertion: the same committed replay bytes re-walked, re-hashed and re-folded by module after module. Wave 2 of the roadmap runs this gate dozens of times; at the current cost the gate is the wave's largest single line item, which is why audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 1.12 puts it in wave 1 with the explicit note that it pays for itself inside the following wave.

The structural cause is named in audits/review-2026-08-19/B/tests-ci-tooling.md §P1-4 and §P2-4 (collated as the C-107 row): the suite has no test-infrastructure layer. At HEAD, `grep -rn 'scope="session"' tests/` returns exactly **2** (tests/conftest.py:152, Task 20.17's autouse hermetic env guard, and :180, the committed-9p2i report) against **56** `scope="module"` fixtures, and **60** test modules reference the committed sample sets independently (the review recorded 61 under its own pattern). The duplication is concrete and quotable, not statistical: `compute_information_funnel(replays/samples/9p2i)` runs in three separate modules (tests/eval/test_funnel.py:582, tests/agents/test_beliefs_hard_evidence_gate.py:775, tests/agents/test_beliefs.py:3673); `compute_kill_craft_report(replays/samples/4p1i)` runs three times (tests/eval/test_kill_craft.py:58, :275 and tests/eval/test_deduction_metrics.py:1369); `build_report(replays/samples/9p2i)` runs twice (tests/conftest.py:201 and tests/eval/test_gate_spec_metrics.py:983). The conftest module docstring at tests/conftest.py:40-46 already diagnosed this class correctly for one consumer group — "six `build_report` calls per suite run … one session-scoped walk serves them all" — and then stopped. Each of these walks is a pure, deterministic function of committed bytes; sharing the result cannot couple the tests, and the docstring says so in as many words.

The two changes are complementary and neither substitutes for the other, which is the design point this contract has to get right. Parallelism cuts *wall* time; the shared walker cuts *total CPU work* and is what keeps the serial invocation — still the fallback, still what a contributor's IDE runs — from being the only place the saving exists. Under xdist a session-scoped fixture is session-scoped *per worker*, so ten workers perform ten walks: the deduplication that is worth 66 s serially is worth proportionally less in parallel, and the honest claim in the PR is the two measured numbers, not an arithmetic product of them. Get both, measure both, and say which one bought what.

Parallelism has been structurally unavailable, not merely unadopted. audits/review-2026-08-19/B/tests-ci-tooling.md §P1-1 recorded 2 of 7 concurrent `lint-imports` runs printing a false BROKEN contract (D/cross-track-map.md's C-34 row records 2 of 12 under its own repro) because tests/test_firewall.py plants five modules at fixed paths in the live checkout; the dependency edge to the firewall repair exists for exactly that reason. The second instance the review named — tests/experiments/test_torch_probe_excluded.py:168-178, which planted `training/_torch_probe_planted_import.py` while :157-165 in the same file AST-scans `training/` for that very import — was repaired inside the same Task-20.9 PR: the plant now goes under `tmp_path`, so that cross-worker race is gone and needs re-confirming rather than fixing. Two further hazards are latent rather than live: §P2-2's 21 cwd-relative test modules (tests/agents/test_memory_rendering.py:32, tests/eval/test_prompt_regression.py:43) only pass from the repo root, and §P2-11's duplicated `test_schemas.py` basename survives collection today only because tests/api/ has an `__init__.py` and tests/meetings/ does not. Verify each of these under `-n auto` before declaring green; a parallel suite that is green by luck of scheduling is worse than a serial one.

This task ships no production behaviour and no lever: `Record impact: none`. Nothing under `agents/`, `engine/`, `eval/`, `meetings/`, `orchestrator/` or the prompt templates is touched, so the committed bytes, the substrate stamp and `bash scripts/verify_samples.sh` are untouched by construction — but the PR states that explicitly, with `verify_samples.sh` re-run as evidence, because "only test plumbing moved" is a claim a reviewer should be able to check rather than take.

**Files in scope:**
- pyproject.toml; (`pytest-xdist` pinned into the `dev` dependency group beside pytest at :97; `addopts` does NOT gain `-n` — check.sh passes it, so an explicit `uv run pytest <node-id>` stays serial and debuggable)
- uv.lock; (regenerated — scripts/setup_env.sh:27 runs `uv sync --locked`, so a stale lock fails setup in CI before a single test runs)
- scripts/check.sh; (the pytest leg at :21 becomes the parallel invocation, with the `AILIBI_PYTEST_SERIAL` escape hatch validated loudly in the same idiom as :9-13 — the shell reads that variable and no test does: Task 20.17's root conftest clears the whole `AILIBI_*` namespace by prefix, and tests/test_env_hermeticity.py reds on any module-level read of a name outside its allow-list)
- tests/conftest.py; (the session-scoped committed-bytes accessors delegate to the shared helper; the existing `committed_9p2i_report` fixture at :180-201 keeps its name and becomes a thin wrapper)
- tests/_helpers/; (new `committed.py`: the one home for cached walks/folds over `replays/samples/**` and `replays/ml_corpus/**`, plus a repo-root constant the cwd-relative modules can adopt)
- tests/eval/conftest.py; (new — session fixtures delegating to the helper for the eval-side instrument reports)
- tests/api/conftest.py; (new — the same delegation for the api-side loader fixtures)
- .github/workflows/ci.yml; (the Python job's `Run checks` step at :47-48 — it invokes check.sh, so the parallel invocation arrives through it; the job documents the hosted runner's worker count and the serial hatch rather than duplicating the pytest command)
- tests/scripts/test_gate_invocation.py; (new: pins the parallel invocation in check.sh and the AILIBI_PYTEST_SERIAL escape hatch)

**Files NOT in scope:**
- individual test logic (only fixture plumbing moves; an assertion that changes is a bug in this task)
- tests/test_firewall.py (the temp-tree plant is already done upstream; unchanged here)
- eval/, agents/, engine/, meetings/, orchestrator/, api/ production modules (the instrument entry points take a `sample_dir: Path` and walk internally — sharing happens at the test layer or not at all in this task)
- agents/strategic/prompts/**/*.j2 (prompt-template edits belong to the single prompt-set bump task and to no other)
- orchestrator/replay.py (no lever is introduced, so there is nothing to register in the substrate stamp)
- replays/ and the committed sample bytes (read-only inputs)
- .gitignore and .importlinter (owned upstream by the firewall/import-contract repair)

**Definition of done:**
- [ ] `uv run pytest -n auto` is green and deterministic: three consecutive full runs, same pass/skip/xfail counts, zero order-dependent failures, with the three wall times and exit codes quoted in the PR; wall time under 90 s on the 10-core review machine class against the review-measured 337.96 s serial baseline — measured over a suite that has grown since (Task 20.14 alone added four module-scoped walks over 400 committed games), so quote your own serial baseline at this HEAD beside it and report the ratio.
- [ ] `uv run pytest` with no `-n` is still green and still the debuggable path; its new serial wall time is quoted beside the 337.96 s baseline so the walker-sharing saving is visible separately from the parallelism saving.
- [ ] `tests/_helpers/committed.py` is the single home for the shared walks: the 9p2i report, the 9p2i information funnel, and the 4p1i/9p2i kill-craft reports are each computed once per worker, and a test in that package asserts no test module outside `tests/_helpers/` calls `build_report(`, `compute_information_funnel(`, `compute_kill_craft_report(`, `compute_deception_instruments(` or `compute_solvability_report(` (Task 20.14's instrument, whose four module-scoped fixtures in tests/eval/test_solvability.py walk 400 committed games) against a committed sample directory — the exceptions allow-listed by name with a stated reason.
- [ ] The two deliberate re-derivations keep their own uncached walk and the allow-list records why: tests/eval/test_kill_craft.py:273-276 (`test_report_is_deterministic` — a second independent computation is the assertion) and tests/scripts/test_build_sample_report.py:43 (it tests the builder itself). Delegating either to the cache would make its pin tautological.
- [ ] The before/after counts are quoted in the PR from one grep each: modules that independently construct a walk/fold over the committed sets (60 at HEAD), `scope="module"` fixtures (56 at HEAD) and `scope="session"` fixtures (2 at HEAD — the second is Task 20.17's autouse hermetic env guard, not a committed-bytes walk).
- [ ] `scripts/check.sh` runs the parallel invocation, and `AILIBI_PYTEST_SERIAL=1 bash scripts/check.sh` runs it serially; an unrecognised value of that variable exits non-zero with an explicit message, matching the `AILIBI_SKIP_FRONTEND` idiom at scripts/check.sh:9-13. Both behaviours are pinned by a test that reads the script (the hatch's absence and a typo'd value each fail the pin).
- [ ] The parallel-safety hazards are checked, not assumed: the former second live-tree plant at tests/experiments/test_torch_probe_excluded.py:168-178 is re-confirmed to write only under `tmp_path` after Task 20.9 (this task does not edit that file), and the duplicated `test_schemas.py` basename still collects cleanly under xdist with the chosen import mode.
- [ ] `.github/workflows/ci.yml` states, in the Python job, how many workers the hosted runner gets and how to fall back to serial; no second pytest command is introduced there — the invocation stays single-homed in check.sh.
- [ ] `uv.lock` is regenerated and `uv sync --locked --group dev` succeeds from a clean environment (quoted in the PR), so scripts/setup_env.sh:27 does not fail on a stale lock.
- [ ] No production bytes moved: the diff touches only the eight scoped paths, `bash scripts/verify_samples.sh` is re-run green, and the PR says so.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — measure before you change anything. Record `time uv run pytest -p no:cacheprovider --durations=60` at HEAD on your machine and note the core count; every later number in the PR is a delta against that, not against the review's, because the review's 337.96 s was measured on its own host under load 4.5-8.3. Keep the review's numbers as the labelled reference, not as your baseline.

Step 2 — turn on parallelism before doing any deduplication, so the two effects stay separable. Add `pytest-xdist` to the `dev` group, regenerate the lock, and try `-n auto --dist loadfile` first: `loadfile` keeps every test in one file inside one worker, which is the cheapest way to preserve module-scoped fixture semantics. Then measure plain `-n auto` (default `--dist load`) as well; if it is materially faster and still green three times, prefer it and say why in the script's comment. Whichever you pick, put it in scripts/check.sh, not in `addopts` — `addopts` would silently parallelise a single-node-id debug run and cost a developer an afternoon.

Step 3 — hunt the order dependence deliberately rather than hoping. There is no `pytest-randomly` in this repo, so the review-suggested `-p no:randomly` comparison does not apply; the available levers are running the suite three times under `-n auto` and comparing counts, running `-n 2` and `-n auto` and comparing, and running the known-risky families alone: tests/experiments/, tests/scripts/, tests/training/ and anything writing outside `tmp_path`. `grep -rn 'write_text\|mkdir\|write_bytes' tests/ | grep -v tmp_path` is the blast-radius grep; run it first and read every hit that resolves under the repo root. Also confirm the 21 cwd-relative modules still pass — xdist workers inherit the invocation cwd, so they should, but confirm rather than reason.

Step 4 — the shared walker. `tests/_helpers/committed.py` exposes `functools.cache`-keyed accessors taking a directory and returning the folded artifact; the callers become one-line delegations. `tests/` and `tests/_helpers/` both have `__init__.py` and pyproject sets `pythonpath = ["."]`, so `from tests._helpers.committed import ...` resolves from any test module — the api-side fixtures package is the precedent. Consumers inside tests/eval/ and tests/api/ get fixture-shaped access through the two new package conftests; consumers in tests/agents/ import the helper directly rather than growing a third conftest this task did not scope. Keep the existing `committed_9p2i_report` fixture name at tests/conftest.py:180 so no signature in tests/eval/test_wave2_metrics.py changes.

Step 5 — do not let the cache eat a gate. Two call sites exist precisely to recompute, and the allow-list is where you record that. More generally: after wiring the helper, perturb one committed byte in a scratch copy and confirm the pins still fail — a cache that outlives the perturbation is a gate that cannot fail.

Step 6 — the collection hazards, if they bite. `--import-mode=importlib` in `addopts` is the one-line fix for the duplicated `test_schemas.py` basename should xdist's collection surface it, and it is preferable to sprinkling `__init__.py` into seven directories from a task scoped to fixture plumbing. The `.hypothesis` example database is shared by all workers across the four modules that import hypothesis; if it produces cross-run noise, pin the database off for the suite rather than chasing individual flakes. Neither change is required unless a measurement demands it — take it only with the failing output quoted.

Step 7 — the registered-but-unused `slow` and `perf` markers at pyproject.toml:77-78 are NOT this task's to delete: tests/training/test_suite_tiers.py:108 pins their registration and that file is out of scope. Leave them, and leave `addopts`' `-m 'not campaign'` filter exactly as it is; the tier split and the parallelism are independent decisions and mixing them makes the wall-time comparison meaningless.

**Public types introduced:**
- `tests._helpers.committed.repo_root`
- `tests._helpers.committed.report_9p2i`
- `tests._helpers.committed.funnel_9p2i`
- `tests._helpers.committed.kill_craft_report`

**Ready-to-paste prompt:** `agent_prompts/task-20-18-xdist-suite.md`

### Task 20.19 — Two byte-identical speed-ups: the cached Jinja environment and the bisecting episodic scan
**Branch:** `phase-20-byte-identical-speedups`
**Depends on:** 20.5 — the loader's first-run-notice change lands first, so the two edits to the prompt-loader module and its test file serialise instead of colliding, and this memo is layered beneath an already-settled set-resolution path.
**Section refs:** C-42 + C-43 [both P1, adversarially CONFIRMED] — audits/review-2026-08-19/B/collated-findings.md rows C-42 and C-43; audits/review-2026-08-19/B/perf-runtime.md §3 F1, §3 F2, §5 (the lifetime-conflation and derived-view-sprawl diagnoses) and §6 R1/R2/R3; audits/review-2026-08-19/B/verdicts.md (the C-42 verdict corrects the win to 1.20x, REFUTES the "the cache key must include the roll-call lever" caveat, and corrects "the production path never uses `_ENV`" — `_ENV` is the live default for the `experiments/lab/` wrappers; the C-43 verdict reproduces 5,160 `recent()` calls and 3,158,709 event-visits exactly, measures 1.34x and 1.27x on long games, and records that the bisect ALONE is not enough — the full-log tuple must also be cached); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 1, the C-42 + C-43 row ("replay SHA unchanged; A/B ratios reproduce"). Anchors re-verified at HEAD f1e970a4: agents/strategic/prompts/loader.py:194-235 `resolve_prompt_set`, :238-266 `build_environment`, :272 the import-time `_ENV`, :683 + :711 `build_prompt_renderers` calling `build_environment` on every construction, :712-718 the impostor-roll-call lever selecting template FILENAMES outside the environment; orchestrator/game.py:858 + :910-911 a fresh runner — and therefore a fresh environment — per game; agents/memory/episodic.py:96-117 `append` with its non-decreasing-tick guard and :119-122 the linear `recent()`; 32 non-test `.recent(` call sites of which 29 pass `since_tick=0` — 13 in agents/memory/store.py, orchestrator/game.py:2758,2819,2870,2921,2988,3049, agents/perception.py:284, agents/tactical/crewmate_policy.py:304 and :361, agents/tactical/impostor_policy.py:266, agents/tactical/features.py:471, agents/tactical/learned/forward.py:252, agents/tactical/learned/crew_forward.py:342, api/replay_loader.py:2308, training/crew/options.py:349 and training/bakeoff/utility_es.py:270, the only three windowed callers being agents/perception.py:143 taking since_tick=tick, :315 taking since_tick=earliest_tick and agents/tactical/features.py:392 taking a tick-minus-window bound; tests/agents/test_memory.py:26-92 the existing `recent()` behaviour pins; tests/meetings/test_prompt_byte_golden.py:835-840, :1089 and :1149-1160 the golden and one-byte-perturbation legs, each built against its own root.
**Complexity:** Small
**Record impact:** none — no lever is introduced, no template byte moves, no committed artifact is regenerated, and both changes are replay-byte-identical, so the Phase-20 adopting record is untouched by this task.
**Measurement:** `bash scripts/verify_samples.sh` re-walks 100/100 committed replays clean; three 9p2i fake-provider games recorded with `uv run python scripts/run_game.py --seed <s> --num-players 9 --num-impostors 2 --tasks-per-crewmate 2 --replay-path <tmp>/r-<s>.jsonl` have `shasum -a 256` digests identical to the same three seeds recorded on the merge-base; `uv run pytest tests/agents tests/meetings/test_prompt_byte_golden.py -q` green; and `time uv run python scripts/run_tournament.py --num-games 10 --roster-preset 9p2i --output-dir <tmp>` quoted before/after — three interleaved legs per arm with the `uptime` load average beside each, expected direction: faster, with the review-measured references 1.20x from the environment memo and 1.27–1.34x on long games from the bisect.

Two accidental costs sit in the hot path of every LLM-free game, and the review measured
both, fixed both by monkeypatch, and proved both byte-identical before recommending
anything. First: `build_prompt_renderers` builds a fresh `jinja2.Environment` on every
call (agents/strategic/prompts/loader.py:711), and `build_default_meeting_runner` is
constructed once per game by design (orchestrator/game.py:910-911), so the three to four
meeting templates are re-lexed, re-parsed and re-compiled per game. The 10-game
tournament profile in audits/review-2026-08-19/B/perf-runtime.md §2.4 attributes 0.405 s
of 2.52 s — 16 % — to `jinja2/loaders.py:107(load)`; the adversarial re-measurement in
audits/review-2026-08-19/B/verdicts.md reads 0.369 s / 14.7 % and, decisively,
`Environment.__init__ == 11` for ten games — one import-time `_ENV` plus one per game.
A fresh environment plus four compiles costs 15.6 ms; the warm cache costs 0.010 ms.
Second: `MemoryStore.recent()` (agents/memory/episodic.py:119-122) is a full-log generator
scan, although `append` (:96-117) already raises on a decreasing tick and is the only
mutator of `_events` anywhere in the repo. The invariant that makes the scan unnecessary
is enforced and unused. The consequence is Θ(T²) agent cost: the review's instrumented
`_collect_intents` rises cleanly from 0.35 ms/tick at tick 0 to 2.11 ms/tick at tick 120,
and one 119-tick 9p2i game makes 5,160 `recent()` calls visiting 3,158,709 events.

Neither fix changes a byte that anyone records. Both were A/B'd inside one process with
the replay SHA-256 compared across arms and found identical — the environment memo at
1.24x claimed and 1.20x re-measured, the bisect-plus-cache at 1.28x claimed and
1.34x / 1.27x re-measured on long games (all figures review-measured on the reviewer's
macOS box under load averages of 5.7–10.4, and to be reproduced, not trusted, by this task).
That is why this contract's record impact is none: there is no recording to shorten here,
and audits/review-2026-08-19/D/cross-track-map.md is explicit that these two do not
shorten the ~23 h re-record, which is LLM-bound. What they do shorten is everything the
rest of Phase 20 leans on — the default test gate, the eval harness, and every offline
counterfactual a lever task runs over committed bytes.

Two review claims are wrong at HEAD and this contract corrects them rather than
inheriting them. The recommendation in perf-runtime.md §6 R1 says the cache key should
include the roll-call lever; it must not, and need not — the lever is read in
`build_prompt_renderers` at loader.py:712 and only chooses which template FILENAMES the
renderers bind, while `build_environment` at :238-266 never reads it. And F1's aside that
the module's `_ENV` is dead code is false: it is the live default for the module-level
wrapper callables (loader.py:382, :463, :583, :647) that `experiments/lab/` drives.
`_ENV` stays exactly where it is; after this task it simply becomes the first entry in
the memo instead of the one environment in eleven that the game path never reached.

The scope is deliberately the cheap half. The structural fix — O(1) incremental
accessors for the three per-tick recomputations at agents/perception.py:143,284,315 and
one pass replacing the thirteen independent projections in agents/memory/store.py — is
perf-runtime.md §6 R3, a day of work that touches the render path, and it is recorded
here as out of scope rather than left silent. This task keeps the public signature of
`recent()` and every call site's arguments untouched, which is what makes the byte
identity provable in one diff.

**Files in scope:**
- agents/strategic/prompts/loader.py; (memoize the Environment per resolved set and root — the AGENTS.md no-mutable-global rule is respected because the memo is `functools.lru_cache` over a pure constructor, holding no game state)
- agents/memory/episodic.py; (bisect on the sorted tick index; a cached full-log tuple invalidated on append)
- tests/agents/test_prompt_loader.py; (the memo: same object for the same key, different for a different set or root; an in-process AILIBI_PROMPT_SET change still re-resolves; the unknown-set raise still fires on every call)
- tests/agents/test_episodic_ids.py; (recent() equivalence against a linear reference over random legal logs, plus the structural bisect and invalidation pins)
- tests/agents/test_memory_store.py; (no render change: render_for_prompt is byte-identical over a fixture)

**Files NOT in scope:**
- agents/perception.py and agents/memory/store.py (every call site keeps its `since_tick` argument; the speed-up lives entirely inside `recent()`, and the O(1)-accessor rewrite is perf-runtime.md §6 R3, explicitly deferred)
- orchestrator/, api/, training/, eval/ (no API change and no call-site edit; `build_default_meeting_runner`'s documented per-game freshness of the budget and the recording client is preserved untouched)
- eval/balance_eval.py (the process-parallel tournament is perf-runtime.md §6 R4, a separate change)
- replays/ and any committed artifact (reconstruction must stay byte-identical; `scripts/verify_samples.sh` is the pin)
- agents/strategic/prompts/*.j2 (no task in this phase edits a game prompt template except the single prompt-set bump; a memo over template loading must not become an excuse to touch one)
- orchestrator/replay.py (this task introduces no lever, so there is no substrate-stamp registration to do)
- tests/agents/test_memory.py (the existing `recent()` behaviour pins at :26-92 are the regression evidence: they stay untouched and must stay green)

**Definition of done:**
- [ ] Byte identity is proved, not asserted: three 9p2i fake-provider seeds recorded before and after the change produce replay JSONL files with identical `shasum -a 256` digests, and `bash scripts/verify_samples.sh` re-walks all 100 committed replays clean; both outputs are pasted into the PR Summary.
- [ ] `build_environment` keeps its signature and its behaviour — it resolves the set, rejects an unknown set with `ValueError`, and then returns an environment memoized on the resolved set name and the templates root. `tests/agents/test_prompt_loader.py` pins that two calls for one set return the same object, that a different set and a different `root` each return a different object, and that the environment carried by two separate `build_prompt_renderers` bundles for one set is one object.
- [ ] The memo sits strictly beneath resolution: `resolve_prompt_set` is still called once per `build_environment` call, so the bare-fallback stderr notice that Task 20.5 leaves in place fires exactly as often as it did before. `tests/agents/test_prompt_loader.py` pins the notice count over N consecutive `build_prompt_renderers` calls under a real-provider environment — that count is ONE, because Task 20.5 landed the notice as a once-per-process `functools.lru_cache` memo on `_notify_bare_prompt_set_fallback` (loader.py:148-149) which the file's autouse `_reset_bare_fallback_notice` fixture clears around every test.
- [ ] An in-process prompt-set change still re-resolves: `build_environment` called with `env={ENV_PROMPT_SET: "qwen3_32b"}` and with `env={ENV_PROMPT_SET: "qwen3_5_9b"}` returns two different environments, each bound to its own set, and an unknown set raises `ValueError` on the second call as well as the first — the memo caches no failure. Pinned in `tests/agents/test_prompt_loader.py`.
- [ ] The impostor-roll-call lever is NOT part of the key, with the reason recorded in one line at the memo: the lever chooses template filenames at loader.py:712-718, outside the environment. `uv run pytest tests/agents/test_impostor_answer_arm.py tests/agents/test_bespoke_prompt_sets.py -q` stays green, including the ON-with-a-variant-less-set `ValueError`.
- [ ] `MemoryStore.recent()` locates its window with one `bisect_left` over a tick index maintained in `append`, and returns a cached materialized tuple when the window starts at index 0; the full-log generator expression at episodic.py:122 is gone. The public signature, the return type, and the append-order guarantee are unchanged.
- [ ] `tests/agents/test_episodic_ids.py` pins output equivalence against a linear reference implementation over at least 1,000 randomly generated legal append sequences — including duplicate ticks, gaps, and negative and past-the-end `since_tick` values — with zero mismatches, and pins structurally that exactly one `bisect_left` call occurs per `recent()` call.
- [ ] The full-log cache is invalidated on write: `recent(since_tick=0)`, then `append`, then `recent(since_tick=0)` returns the longer tuple including the new event; the duplicate-observation-id and non-decreasing-tick guards still raise, and a rejected `append` leaves the tick index and the cache consistent with `_events`.
- [ ] No render change: `tests/agents/test_memory_store.py` pins that `render_for_prompt` produces byte-identical output over a fixture store before and after the change, with the expected bytes committed as the fixture rather than recomputed at assert time.
- [ ] Both new gates are shown able to fail: the PR quotes the failing output produced by temporarily restoring the linear generator in `recent()` and by temporarily removing the append-time cache invalidation.
- [ ] The 10-game fake-provider tournament timing is quoted before and after with the load average beside each leg, using interleaved arms in the same session rather than one run per arm.
- [ ] Provenance discipline: each touched function gains at most one line naming this task and the finding it closes; no narration of the change's history beyond that.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — the environment memo. Keep `build_environment`'s body doing exactly what it does
today up to and including the unknown-set `ValueError`, then hand off: add a private
`_environment_for(name: str, root: Path) -> Environment` carrying the `Environment(...)`
construction verbatim and decorate it with `functools.lru_cache` at a small bounded
maxsize. Both key components must be hashable and both are — a `str` and a `Path`. Do not
normalise the root; two spellings of one directory splitting the cache is harmless, while
normalising could merge roots a test means to keep apart. Because resolution and the
directory check stay above the cache, the env-mapping argument never reaches it, the
first-run notice fires unchanged, and an unknown set raises on every call, since
`lru_cache` does not memoize exceptions. `_ENV` at loader.py:272 stays as it is and simply
warms the memo for the default set at import.

Step 2 — the two hazards worth checking before believing step 1. Sharing an environment
means sharing jinja2's per-instance template cache; that is safe only because the
environment is left at jinja2's `auto_reload=True` default, so `FileSystemLoader` re-stats a template
whose bytes changed and does not serve stale ones. The byte-golden suite is where this
bites: `tests/meetings/test_prompt_byte_golden.py:1149-1160` copies the template tree into
a fresh `tmp_path`, appends one byte to `crewmate_report.j2`, and asserts at least one
prompt no longer reproduces. Run that file and confirm the perturbation leg still fails
when it should. The archive leg at :838 and the perturbation leg use distinct roots, so
keying on the root is what keeps them apart.

Step 3 — the episodic index. In `__init__` add a parallel `list[int]` of ticks and an
optional cached full tuple. In `append`, after both existing guards have passed and the
event is stored, append the tick and clear the cache — order matters, so a rejected append
leaves both structures untouched. In `recent`, compute `bisect_left(self._ticks,
since_tick)`; when the index is 0 return the cached full tuple, building it once on
demand; otherwise return `tuple(self._events[index:])`. Handling index 0 through the cache
is what covers `since_tick=0` and every negative or below-the-first-tick value with one
branch, and it is the half the review found load-bearing — bisect alone still pays an O(n)
materialisation on the 29 `since_tick=0` call sites.

Step 4 — measure the way the review did, not the way that is convenient. Interleave the
arms in one session, three legs each, record `uptime` beside every number, and quote the
medians. Do not add a timing assertion to any test; the `perf` marker exists but carries
no default filter, so a wall-clock assertion would run in the default gate and flake. The
sub-linearity claim is pinned structurally by the single-`bisect_left` test, not by a
clock.

**Ready-to-paste prompt:** `agent_prompts/task-20-19-byte-identical-speedups.md`

### Task 20.20 — The as-built architecture picture and the contract → prompt → PR exhibit
**Branch:** `phase-20-architecture-exhibit`
**Depends on:** 20.13 — the front door's results section lands first, so this task edits a README whose sections already sit in their rewritten shape and only adds the picture and the workflow exhibit on top of it, rather than racing the rewrite for the same paragraphs; also after 20.17 (the artifacts registry row both tasks touch is ordered behind the hermeticity fix)
**Section refs:** audits/review-2026-08-19/C/collated-portfolio.md §(B) items B4 and B5 [B4 raised by P1 G, P2 G, P4 G, X2 G, X1 N; B5 by X1 G, X2 fold, P3 N, P1 M-3 fold]; audits/review-2026-08-19/C/p1-backend-hiring-manager.md §2 "12:00–14:00 — docs/architecture.md" [VERIFIED 146 lines — "This is the document I wanted first"] + §7 GOOD 4 (one click from the top) + §7 GOOD 10 (file size will be asked about); audits/review-2026-08-19/C/x1-front-door-reproduction.md §3.4 (architecture.md "is not linked from the README's first screen — only in 'What this is' and the footer"; 1,089 words per §6), §4 "Other builders" ("the workflow artifacts (task contract → prompt) are linked once and never shown"), §5 GOOD 7 (a 15-line contract excerpt + the matching prompt header + the PR it produced, branch `claude/…`, gate green) + §5 NICE 14; audits/review-2026-08-19/C/x2-narrative-and-positioning.md §4 gap row "Architecture diagram (image) — ASCII only; `DESIGN.md` §1.1 diagram is the *target* arch" + §6 proposal 7 (an as-built SVG of the layering plus the firewall arrow); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 1 row 1.14 (C/B4 + C/B5, size S, measurement "three links resolve; a reader verifies agent authorship in git in 30 s"); audits/review-2026-08-19/D/synth-ambition.md §FM-6 (the contract→prompt→PR triple shown, not linked); README.md:76 (`## What it is`), :84 (the architecture link, now a one-line pointer), :85 (20.12's reserved `<!-- ANCHOR: … inlines the as-built layering diagram here. -->`), :59 (`## How it was built — who did what`), :73 (the one workflow-artifact line, linked and never shown), :74 (20.12's reserved `<!-- ANCHOR: … shows a contract, its prompt and the merged pull request inline. -->`), :62 (the owner-ratified authorship paragraph), :162 (the footer link); docs/architecture.md:11-21 (the ASCII layering block), :51-56 (the `meetings/` paragraph), :89-91 (the generated `frontend/src/types/api.ts`), :104-118 ("Enforced boundaries" — the four contracts and their backing tests), 146 lines at HEAD; .importlinter:20-26 (`[importlinter:agents_must_not_import_engine]`, `name = Agents must not import engine`); DESIGN.md:7-12 (the Task 19.1 demotion banner), :49 (§1.1 Component diagram — the target architecture); `wc -l` at HEAD: meetings/manager.py 3,989, orchestrator/game.py 3,193; audits/audit-phase-19-planning.md:170-174 (the monolith decompositions on the recorded backlog); docs/media/README.md:1-10 (the two-row asset table); docs/artifacts.md:108 (the `docs/media/` registry row promises "1.7 MB / 3 files"); scripts/verify_ml_evidence.py:2110 + :2163 + :2171 (`_STATED_FILES`) + :2174-2202 (`inventory_problems`) and tests/scripts/test_verify_ml_evidence.py:1402-1420 (the row-count gate a fourth file under `docs/media/` turns red); agent_prompts/task-19-2-in-code-truth.md:1-16 (the generated prompt header shape) against tasks/phase-19.md:314-361 (its contract) and the merged PR https://github.com/dkdan10/AiLibi/pull/328
**Complexity:** Small
**Record impact:** none
**Measurement:** `xmllint --noout docs/media/architecture.svg` is silent and `wc -c docs/media/architecture.svg` is under 60,000; `uv run python scripts/check_doc_facts.py` exits 0; `uv run pytest tests/scripts/test_check_doc_facts.py tests/scripts/test_verify_ml_evidence.py -q` green — the new exhibit link-check resolves all three targets (the contract file, the generated prompt file, and the PR number as a `(#N)` commit-subject suffix reachable from HEAD), the SVG parses under `xml.etree.ElementTree`, docs/architecture.md is under its stated word budget, and the `docs/media/` registry row now reads 4 files against a 4-file index.

The best technical document in the repository is effectively unlinked.
`docs/architecture.md` is 146 lines at HEAD with an ASCII layering block at :11-21
and a four-contract "Enforced boundaries" section at :104-118; the backend hiring
manager read it at minute 12 and wrote "This is the document I wanted first"
(`audits/review-2026-08-19/C/p1-backend-hiring-manager.md` §2), and the narrative
reviewer called it the best single technical page in the repo. Four of the six
personas asked for it one click from the top
(`audits/review-2026-08-19/C/collated-portfolio.md` §(B) B4). Today it is reachable
only from a one-line pointer at `README.md:84` and from the footer at
`README.md:162` — a placement X1 measured and named in
`audits/review-2026-08-19/C/x1-front-door-reproduction.md` §3.4 (X1 read the
pre-20.12 README, where those two routes sat at :45 and :248). There is also no
picture of the system anywhere a reader lands: the only component diagram in the
repo, `DESIGN.md:49` §1.1, draws the *target* architecture of a demoted historical
record (`DESIGN.md:7-12` carries the Task 19.1 banner), so the one diagram a reader
can find is the one that is not the system.

The workflow has the same shape of defect: asserted, never shown. `README.md:73`
offers "One contract and the prompt generated from it" — a link to Task 3.19's contract
and a link to its generated prompt — and that is the whole exhibit; 20.12 left this
task's insertion point as the HTML comment at `README.md:74`. X1 recorded the
consequence for the audience the project fits best: "the workflow artifacts (task
contract → prompt) are linked once and never shown; no diagram, no excerpt, no 'here
is one contract and the PR it produced'" (§4, "Other builders"). The fix both X1 §5
GOOD 7 and `audits/review-2026-08-19/D/synth-ambition.md` §FM-6 ask for is one real
~15-line contract excerpt sitting beside the header its generator produced and the
merged PR that closed it. Note why the exhibit cannot simply promote the pair already
linked: Task 3.19 predates PR-numbered dispatch — its four commits (`e3a327a5`,
`5fd83bfe`, `d042e745`, `305e2cee`) carry no `(#N)` suffix — so it has no PR to show,
and the triple must be drawn from a task that has all three artifacts. Task 19.2 is
the recommended pick: contract at `tasks/phase-19.md:314-361`, prompt at
`agent_prompts/task-19-2-in-code-truth.md`, merged as PR #328.

The authorship sentence that ships beside the exhibit must be verifiable-shaped, and
the true mechanics are slightly more interesting than the review assumed. At HEAD,
`main` holds 910 commits; `git log --author=Claude` returns 310 of them (the 35%
`audits/review-2026-08-19/D/synth-ambition.md` §FM-6 quotes, measured on a smaller
`main`) and a `--grep='Co-Authored-By: Claude'` walk returns 299; `origin` still
carries 282 `claude/…` branch heads. But the squash commit for a merged PR carries the human as author with
no trailer — `ac162041` ("task 19.2: … (#328)") is authored by `dkdan10` — while the
trailer and the model name live on the pre-squash branch commit (`8344d025`,
`Co-Authored-By: Claude Fable 5`), reachable through the PR. The README sentence
therefore hands the reader the *commands* and says where each signal lives; it does
not pin the counts, which move with every merge and which the front door's own
doc-fact discipline exists to keep out of prose.

What this task ships is small and entirely presentational: one committed SVG of the
as-built layering with the firewall drawn as an arrow and its import-linter contract
named, embedded in both `docs/architecture.md` and the README's "what it is" section;
the contract → prompt → PR exhibit in the README's "how it was built" section; one
sentence in `docs/architecture.md` acknowledging that `meetings/manager.py` (3,989
lines) and `orchestrator/game.py` (3,193 lines) are large and that their
decomposition is on the recorded backlog at
`audits/audit-phase-19-planning.md:170-174` — the answer P1 §7 GOOD 10 says an
interviewer will ask for; and the asset row in `docs/media/README.md`. Nothing behind
the firewall moves, no recording is touched, and no prompt template is edited — the
single Phase-20 prompt-set bump is Task 20.31's alone, and this task must not touch
`agents/strategic/prompts/` or `scripts/prompt_template.md.j2`. One non-obvious
coupling the blast-radius grep found: `docs/artifacts.md:108` promises `docs/media/`
holds "1.7 MB / 3 files", and `tests/scripts/test_verify_ml_evidence.py:1402-1420`
compares that promise against the git index, so a fourth committed file under
`docs/media/` turns the evidence command red until the row is corrected in the same
PR.

**Files in scope:**
- docs/media/architecture.svg; (new: the as-built layering with the firewall arrow, hand-authored SVG or generated by a small script committed under docs/media/)
- docs/architecture.md; (embeds the SVG; one sentence on why meetings/manager.py and orchestrator/game.py are large — the decomposition is backlog)
- README.md; (the 'What it is' section embeds the SVG; the 'How it was built' section shows a ~15-line contract excerpt beside its generated prompt header and links the PR it produced)
- docs/media/README.md; (the asset list)
- docs/artifacts.md; (the docs/media/ registry row count — verify_ml_evidence compares it against the git index)
- tests/scripts/test_check_doc_facts.py; (ORCHESTRATOR RULING 2026-08-23 on PR #374: an authoring omission — the DoD names this file five times and the Measurement runs it; the new pins are pytest-side and live here)

**Files NOT in scope:**
- DESIGN.md (the diagram there stays as the historical target; a caption is 19.1's demoted-record convention — not touched here)
- scripts/prompt_template.md.j2 and agents/strategic/prompts/ (unchanged; the one Phase-20 prompt-set bump belongs to 20.31, and no other task may edit a template)
- docs/reading-guide.md, docs/history.md, docs/glossary.md, docs/ml-program.md (the front-door rewrite and the results page landed upstream; this task adds to the README, it does not restructure it)
- scripts/check_doc_facts.py (run as a gate, not edited — the new pins are pytest-side)
- .importlinter and any source package (the contract is quoted in the picture, never changed)
- docs/media/spectator-journey.gif and spectator-meeting.png (the hero media swap is a later task; these bytes do not move here)

**Definition of done:**
- [ ] `docs/media/architecture.svg` exists, is hand-authored text (no embedded raster, no `<foreignObject>`, no external font or image reference, real `<text>` rather than outlined paths), parses under `xml.etree.ElementTree`, and is under 60,000 bytes — the parse and the size ceiling pinned in `tests/scripts/test_check_doc_facts.py`.
- [ ] The picture shows the as-built layering that `docs/architecture.md:11-21` states in text — engine → observation → agents/meetings ← orchestrator, `llm/` sitting beside the reasoning layer behind the `LLMClient` Protocol, `eval/` and `api/` as privileged readers, `frontend/` running on types generated from the DTOs (`docs/architecture.md:89-91`) — plus the observation firewall drawn as an arrow labelled with its import-linter contract name, `Agents must not import engine` (`.importlinter:20-26`), and a legend line stating that arrows are data flow while imports run the other way.
- [ ] The SVG is legible in both GitHub themes: it declares no opaque light backdrop, uses no pure-black or pure-white stroke/text fills, and carries an internal `@media (prefers-color-scheme: dark)` block; the PR body records the README rendered in both GitHub themes as the evidence for the rendering claim.
- [ ] `docs/architecture.md` embeds the SVG near the top of its layering section, keeps the ASCII block as the text-only fallback, and stays inside two pages — pinned as a word budget (≤ 1,300 words; 1,089 at HEAD per `audits/review-2026-08-19/C/x1-front-door-reproduction.md` §6) asserted in `tests/scripts/test_check_doc_facts.py`, so growth fails the gate rather than the reviewer.
- [ ] `docs/architecture.md` carries one sentence naming `meetings/manager.py` and `orchestrator/game.py` as the two large modules, why they are one unit each, and that the decomposition is on the recorded backlog at `audits/audit-phase-19-planning.md:170-174`; the line counts are not written into the prose as numbers.
- [ ] The README's `## What it is` section (`README.md:76`) embeds the same SVG with a one-line caption and a link to `docs/architecture.md`, in place of 20.12's reserved comment at `README.md:85`; the pointer line at `README.md:84` and the footer link at `README.md:162` survive as links but are no longer the only routes to the page.
- [ ] The README's `## How it was built — who did what` section (`README.md:59`) shows the triple inline, in place of 20.12's reserved comment at `README.md:74`: a ~15-line verbatim excerpt of one real contract, the first lines of the prompt the generator produced from it, and a link to the merged PR that closed it — recommended pick Task 19.2 (`tasks/phase-19.md:314-361`, `agent_prompts/task-19-2-in-code-truth.md`, PR #328); the excerpt and the prompt lines are byte-identical substrings of their sources, asserted in `tests/scripts/test_check_doc_facts.py` so a future contract edit cannot silently falsify the exhibit.
- [ ] One sentence beside the exhibit tells a reader how to verify agent authorship in git and where each signal lives: `git log --author=Claude` and `git log --grep='Co-Authored-By: Claude'` on `main`, the `Co-Authored-By` trailer naming the model on the PR's own branch commits rather than on the squash commit, and the `claude/…` branch heads on `origin`. It ADDS the commands and the squash-vs-branch mechanic to 20.12's owner-ratified authorship paragraph at `README.md:62`, which already names all three signals; that paragraph sits inside an `<!-- OWNER: … -->` block and its as-of-stamped trailer count stays exactly as merged (`check_volatile_stamps` in `scripts/check_doc_facts.py` gates the stamp's shape). This task's own sentence adds no new commit count to prose.
- [ ] A link-check in `tests/scripts/test_check_doc_facts.py` fails when any of the three exhibit targets stops resolving: the contract path and the prompt path must exist on disk, and the PR number in the README URL must appear as a `(#N)` suffix on a commit subject reachable from HEAD (skipped, not passed, when git is unavailable — the `in_tree_inventory` precedent).
- [ ] `docs/media/README.md` lists the SVG in its asset table with what it is, that it is hand-authored rather than captured, and the rule for changing it; `docs/artifacts.md:108`'s `docs/media/` row states the new file count and size, and `uv run python scripts/verify_ml_evidence.py` reports the row OK against the index.
- [ ] docs/architecture.md's firewall paragraph states the plant location and the analysed-package set the import-contracts task recorded (the temp-tree plant; the widened root_packages), so no sentence in it is stale at this merge.
- [ ] docs/artifacts.md's docs/media/ row count equals the git index after the SVG lands (tests/scripts/test_verify_ml_evidence.py green).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — draw the picture from `docs/architecture.md`, not from memory. The ASCII block at
:11-21 is already correct and already reviewed; the SVG is that block with the firewall
promoted from a line of text to a labelled arrow. Six boxes is the whole budget: engine,
observation, agents + meetings sharing a band with llm beside it, orchestrator, eval + api,
frontend. Hand-author it. Do not commit a generator script: `docs/media/README.md` already
records the repo's reasoning for the capture harness it deliberately did not commit — a
second copy of a thing that must stay in sync — and a one-off generator for a static
diagram falls in the same class. Hand-authored also means the diff of a future edit is
readable.

Step 2 — theming, which is the part that is easy to get wrong. GitHub renders a Markdown
image through an `<img>` element, so `currentColor` does not inherit the page's theme — it
resolves against the image's own default colour and a `currentColor`-only diagram reads as
near-black on GitHub's dark theme. Two mechanisms actually work through `<img>`: a palette
that is legible on both grounds (mid-tone strokes and text, no opaque backdrop rect, no
`#000`/`#fff`), and a `<style>` block inside the SVG carrying
`@media (prefers-color-scheme: dark) { … }`, which is evaluated in the image's own context.
Ship both, and know the residual limit before writing the caption: `prefers-color-scheme`
follows the operating system, not GitHub's in-app theme switch, so a reader on OS-light with
GitHub-dark gets the light variant — which is exactly why the base palette must survive on
either ground and why the DoD asks for both-theme screenshots rather than a claim.

Step 3 — verify locally before pinning. `xmllint --noout docs/media/architecture.svg`
catches malformed markup; the committed pin uses `xml.etree.ElementTree` from the standard
library instead of shelling out, so the gate does not depend on `libxml2-utils` being
installed on the CI image. Check the rendering the way a reader will: open the raw SVG in a
browser with the OS appearance toggled both ways, and open the README preview in both GitHub
themes.

Step 4 — the exhibit. Pick the excerpt for readability, not for completeness, and test the
pick against the front door's dialect gate first: Task 19.2's Files-in-scope and
Files-NOT-in-scope blocks through the `**Definition of done:**` line that follows
(`tasks/phase-19.md:329-341`) read well at ~13 lines and are clean. Do NOT quote its WHY
paragraph (`:320-328`) — it uses "graduated" and "graduation", and 20.12's
`check_dialect_terms` in `scripts/check_doc_facts.py` fires on the FIRST README occurrence
of a gated term outside a glossary link; it does not exempt code fences, README carries no
`graduat*` today, and a byte-identical excerpt cannot carry a link, so that pick turns this
task's own `check_doc_facts.py` measurement red. Quote bytes, do not retype — the test asserts the excerpt is a substring of
`tasks/phase-19.md`, and a retyped em-dash or a re-wrapped line will fail it. For the prompt
side, the first ~10 lines of `agent_prompts/task-19-2-in-code-truth.md` are the interesting
part: the generated title, the AGENTS.md routing line, and the "Exact section reference"
paragraph the generator materializes from the contract. Say in one clause that the mirror is
gated (`scripts/generate_prompts.py --check`) rather than asserting it.

Step 5 — the registry row. Run `git ls-files docs/media | wc -l` and `du -sh docs/media`
after the SVG is staged and write those into `docs/artifacts.md:108`; then run
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q` and confirm the in-tree family
inventory row reads OK. Doing this last, after the SVG is final, avoids re-editing the row
for a size that changed while you were still drawing.

**Ready-to-paste prompt:** `agent_prompts/task-20-20-architecture-exhibit.md`

### Task 20.21 — The recorder's worker paths get real coverage before the record
**Branch:** `phase-20-recorder-hardening`
**Depends on:** none (root)
**Section refs:** C-74 (audits/review-2026-08-19/B/collated-findings.md row C-74; audits/review-2026-08-19/B/eval-and-scripts.md §2 P1 F1 + §1 item 8 + §5 item 2; audits/review-2026-08-19/B/tests-ci-tooling.md §3 "Script gigantism in the tooling tier" :530-532); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.0 (:251) + §6 note 2 (:420, "the record itself runs on 917 lines of untested Bash"); audits/review-2026-08-19/D/cross-track-map.md row C-74 + the "1-pre" row ("the record runs on untested Bash"); audits/review-2026-08-19/B/verdicts.md C-6 verdict (**"lock-race attribution refuted"** — replays land via a per-seed private stage + atomic `mv -f`, so the recorder race cannot truncate a replay; the exposure is a lost MANIFEST row, not a truncated file). Re-verified at HEAD: `scripts/refresh_samples.sh` = 917 lines, `set -euo pipefail` at :27; the provider remap comment :256-268 and its code `PROVIDER="$(...)"` :289 + `case` :290-297 with `anthropic | fake) PROVIDER="anthropic" ;;` at :293; the ANTHROPIC_API_KEY preflight :490-495; the Task-18.12 substrate-lever preflight :497-534 (the 20.33 hook point); `export AILIBI_LLM_PROVIDER="$PROVIDER"` :566; the stage mktemp + EXIT trap :611-612; `_acquire_lock` :639-659 with a bare `$BASHPID` at :657; `_release_lock` :661; `claim_next_seed` :666-680; `record_one_seed` :689-795 (the guarded stage mktemp :701-706, the atomic `mv -f` :739-746, the lock-held `_manifest_writer.py update` :760-775); `run_worker` :801-809; the pool spawn/join :811-836; the `.failed` fail-loud check :838-842. `tests/scripts/test_refresh_samples.py` = 915 lines / 59 `def test_`, 42 of them `--dry-run` and 17 real-path cases that abort at arg-parse or a preflight before spend (module docstring :3-6; the review's quoted example `assert "[dry-run] seed workers: 2 parallel" in proc.stdout` at :228). The un-back-ported hardening: `scripts/record_ml_corpus.sh:994-999` + `:1017` uses `${BASHPID:-$$}` with the recorded Bash-3.2 degradation, ledgered at audits/audit-phase-18-close.md §7 row 5 and training/README.md §6 row 5. `scripts/_manifest_writer.py::update_manifest` :446-473 is a whole-file read-modify-write with `_atomic_write_text` :361-384.
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run pytest tests/scripts/test_refresh_samples.py -q` green with the end-to-end and concurrency cases present; the fake-provider `--seeds 0,1` end-to-end case records two replays, writes two MANIFEST rows, and `bash scripts/verify_samples.sh <scratch dir>` exits 0, in < 30 s wall (a fake 4p1i game measured 0.4 s at HEAD, so the whole case is seconds); the `bash -x` trace quoted in the PR names `_acquire_lock`, `claim_next_seed`, `record_one_seed` and `run_worker`.

The project's canonical baseline is produced by 917 lines of Bash whose worker pool has
never been executed by a test. 42 of the 59 tests in `tests/scripts/test_refresh_samples.py`
are `--dry-run` echo assertions and the other 17 abort at arg-parse or a preflight; not one reaches `run_worker`, `claim_next_seed`,
`_acquire_lock` or `record_one_seed`, because `AILIBI_LLM_PROVIDER=fake` — the only
hermetic provider — is remapped to `anthropic` at `refresh_samples.sh:293`, which then
demands a real key at :490-495 and spends. Three review reports reached this
independently (audits/review-2026-08-19/B/eval-and-scripts.md §2 F1;
audits/review-2026-08-19/B/tests-ci-tooling.md §3 "Script gigantism"; the cross-track row in
audits/review-2026-08-19/D/cross-track-map.md), and the synthesis routes it as the FIRST
item of wave 2 — before the record — precisely because ~23 h of operator wall and the
comparator every Phase-20 number is measured against ride on it
(audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 2.0 and §6 note 2).

The gap is not hypothetical. Drafting this contract, a single execution of the real path
found a live defect that the dry-run suite cannot see: `_acquire_lock` writes its owner PID
with a bare `"$BASHPID"` (`refresh_samples.sh:657`) under `set -euo pipefail` (:27), and
`$BASHPID` does not exist in Bash 3.2 — the only `bash` on the owner's machine
(`/bin/bash` and PATH `bash` are both GNU bash 3.2.57(1)-release, arm64-apple-darwin24).
Repro at HEAD, into a scratch `AILIBI_SAMPLE_DIR`, single-worker path, after the roster
descriptor is written and before any provider call: `scripts/refresh_samples.sh: line 657:
BASHPID: unbound variable`. Every real refresh on the host interpreter dies at the first
seed claim. It fails loud rather than corrupting anything, which is the doctrine working —
but the script is unusable on stock macOS bash and no gate says so. The identical hazard
was already found and fixed once in the sibling recorder: `record_ml_corpus.sh:1017` uses
`${BASHPID:-$$}` and its comment block :994-999 records exactly why (the
dead-owner-detection degradation on 3.2 is a ledgered, accepted limitation —
audits/audit-phase-18-close.md §7 row 5, training/README.md §6 row 5). This is the same
shape as C-6's finding: the hardening exists, un-back-ported.

One review claim needs correcting in flight, and this contract corrects it rather than
inheriting it. The recorder lock-race does NOT produce truncated replay files.
audits/review-2026-08-19/B/verdicts.md's C-6 verdict refuted that attribution: the mutex
guards `MANIFEST.md` only, replays are staged per-seed in a private `mktemp -d` and land
via an atomic same-filesystem `mv -f` (`refresh_samples.sh:739-746`), and every row is
flushed. The real concurrency exposure is a LOST MANIFEST ROW:
`_manifest_writer.py::update_manifest` (:446-473) parses the whole manifest, mutates one
seed's row and atomically replaces the file, so two workers updating different seeds
without serialization leave one row silently missing — and a missing row is fatal at the
next gate (`verify_samples.sh` refuses an unmanifested sample: "replay-seed-N.jsonl is
present but not listed in MANIFEST.md"). The lock at :760-775 is what prevents it, and
nothing pins that the lock is load-bearing. This task pins it.

The hermetic path is cheap and already proven to work end to end: a fake-provider 4p1i
game records in 0.4 s, `_manifest_writer.py update` writes a well-formed row from it
(model column carries the fake model, `cost_usd 0.0000`), and `verify_samples.sh`
reconstructs it byte-identically. What is missing is only the script's permission to run
that way, plus a guard strong enough that the permission can never become a way to write
fake bytes over a committed set. The safety property the remap was protecting is
specifically "an UNSET `AILIBI_LLM_PROVIDER` must never silently record fake output over
real samples" (:559-566); that property is preserved untouched here — unset/empty still
resolves to `anthropic`. Only an EXPLICIT `fake`, targeting a sample dir outside the
repo's committed replay tree, is newly allowed. Note the remap ALSO absorbed an INHERITED
`fake`: `tests/conftest.py` forces `AILIBI_LLM_PROVIDER=fake` for every test and `SAMPLE_DIR`
defaults to `$REPO_ROOT/replays/samples/4p1i` (:36), so after this change the `replays/`
refusal — not the remap — is what stops an ambient `fake` from recording over a committed set.

**Files in scope:**
- scripts/refresh_samples.sh; (the fake-provider path runs end-to-end as a real worker; the lock/append race fixed or documented with a guard; the 20.33 preflight hook point kept)
- tests/scripts/test_refresh_samples.py; (a fake-provider end-to-end run of 2 seeds into a tmp dir exercising run_worker/_acquire_lock/record_one_seed and the MANIFEST writer; a concurrent two-worker lock test)
- scripts/_manifest_writer.py; (only if the end-to-end run exposes a defect)
- tests/scripts/test_manifest_writer.py

**Files NOT in scope:**
- replays/ (no bytes move — this task records only into scratch dirs and never touches a committed set)
- scripts/record_ml_corpus.sh (the corpus recorder; 20.36 reprises its runbook — the two scripts share the mutex SHAPE, not a function, so mirror any fix there in 20.36, not here)
- orchestrator/replay.py (20.33 registers the Phase-20 levers into the substrate stamp for all levers at once; the preflight here READS `substrate_flag_snapshot()` and must keep doing so unchanged)
- scripts/check.sh (the gate composition is not this task's; the new cases run under the ordinary `uv run pytest`)
- scripts/verify_samples.sh and scripts/_verify_samples.py (used as an assertion, never edited)
- agents/strategic/prompts/ and every `.j2` template (20.31 owns the single Phase-20 prompt-set bump; no prompt bytes move here)

**Definition of done:**
- [ ] Verify-then-fix recorded: before any edit, the `BASHPID: unbound variable` abort is reproduced at HEAD on Bash 3.2 (or the interpreter's version is quoted if it does not reproduce there) and the failing line + the exact stderr are quoted in the PR Summary.
- [ ] `scripts/refresh_samples.sh:657` writes the lock owner as `${BASHPID:-$$}`, carrying the same degradation note `scripts/record_ml_corpus.sh:994-999` already records (on Bash 3.2 every worker shares `$$`, so dead-owner detection degrades to a no-op while the mutex still serializes); a test runs the real worker path under the host `bash` and fails if the unbound-variable abort returns.
- [ ] The provider remap is made EXPLICIT, not removed wholesale: unset/empty `AILIBI_LLM_PROVIDER` still resolves to `anthropic` (the anti-silent-fake guard at `:559-566` is preserved and its comment updated to state the new rule), an explicit `fake` resolves to `fake`, and a `fake` refresh whose resolved `$SAMPLE_DIR` lies inside the repo's `replays/` tree fails loud before any staging, naming the dir and the rule (the refusal gates the RECORDING path; `--dry-run` stages nothing, so it still echoes the resolved provider at :363 and the pre-existing dry-run cases stay green). Both branches are test-pinned, including the refusal against `replays/samples/4p1i` and `replays/samples/9p2i` by name.
- [ ] Under the `fake` provider the ANTHROPIC_API_KEY preflight (:490-495) is skipped (no spend is possible) while the Task-18.12 substrate-lever preflight (:497-534) still runs unchanged — it is provider-independent and it is the hook point 20.33 extends; a test asserts the substrate preflight still fires on the fake path.
- [ ] A new end-to-end test runs the real script (no `--dry-run`) as `--seeds 0,1` with `AILIBI_LLM_PROVIDER=fake` into a scratch `AILIBI_SAMPLE_DIR`/`AILIBI_MANIFEST`, and asserts: both `replay-seed-0.jsonl` and `replay-seed-1.jsonl` land in the sample dir; the MANIFEST holds exactly one row per seed with the fake model and `0.0000` cost; the staging dir is gone (the EXIT trap at :612 fired); and `bash scripts/verify_samples.sh <scratch dir>` exits 0.
- [ ] A concurrency test runs the same end-to-end case with `AILIBI_REFRESH_WORKERS=2` over ≥4 seeds and asserts no row is lost, no seed is recorded twice, exactly one manifest header block is present, and the run exits 0 — i.e. the lock at `:760-775` is what makes the read-modify-write safe. The claim it pins is the LOST-ROW race, not truncated replays (audits/review-2026-08-19/B/verdicts.md's C-6 verdict refuted the truncation attribution); the PR Summary states that correction.
- [ ] The concurrency gate can fail: a perturbation case shows that concurrent `update_manifest` calls WITHOUT the serialization lose a row (drive `scripts/_manifest_writer.py::update_manifest` from two processes, or interleave read-then-write deterministically if the natural race is not reproducible within a bounded retry — ship a deterministic pin, never a flaky one).
- [ ] `run_worker`, `claim_next_seed`, `_acquire_lock` and `record_one_seed` each have ≥1 real (non-dry-run) test path; the PR quotes a `bash -x` trace from the end-to-end case showing all four invoked, and `record_one_seed`'s fail-loud branch is exercised by a deterministic injected failure that ends in exit 1 plus the "INCOMPLETE and must NOT be committed" message (:838-842).
- [ ] The script's CLI is byte-identical on every path except the newly-explicit `fake`: the pre-existing tests pass unmodified EXCEPT those that pin the old `fake` → `anthropic` resolution, which are updated with the reason stated in the PR — `tests/conftest.py` forces `AILIBI_LLM_PROVIDER=fake` for every test and `_run(env=None)` inherits it, so 23 of the 59 resolve `fake` today, and `test_dry_run_fake_provider_maps_to_anthropic` (:164), `test_dry_run_inherited_fake_provider_still_resolves_anthropic` (:176) and `test_preflight_requires_api_key_before_spend` (:158) pin the old rule by name and must change. Any new dry-run output added for the fake path is asserted rather than left unpinned (20.33 adds a preflight and 20.36 runs this script for ~23 h — neither may need to relearn the interface).
- [ ] `scripts/_manifest_writer.py` and `tests/scripts/test_manifest_writer.py` are edited only if the end-to-end run exposes an actual defect; if it does not, the PR says so explicitly and those two files carry no diff.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — reproduce before fixing. Point `AILIBI_SAMPLE_DIR` and `AILIBI_MANIFEST` at a
scratch dir, export `AILIBI_LLM_PROVIDER=fake` and a dummy `ANTHROPIC_API_KEY`, run
`bash scripts/refresh_samples.sh --seeds 0`, and watch it die at :657 before the
tournament call. That is the whole finding in one command, and it is what the dry-run
suite has been unable to see.

Step 2 — the provider gate. Keep the `case` at :290-297 as the single resolution point.
Add a `fake)` arm that leaves `PROVIDER="fake"`, then immediately assert the target:
resolve `$SAMPLE_DIR` to an absolute real path and refuse when it is inside
`$REPO_ROOT/replays`. Prefer a positive comparison over a string prefix that a symlink or
a `..` can defeat — `cd` into the dir in a subshell and `pwd -P`, or compare against
`$REPO_ROOT/replays` with the same `-ef`-style device/inode reasoning the rubric block at
:890 already uses on `SAMPLE_DIR`. Fail with the dir, the rule, and the sentence that
nothing was staged. On the fake arm also skip the key preflight, and set `active_model`
from the fake client's own model id rather than `DEFAULT_MEETING_MODEL`, so no fake row
can ever render as a Sonnet or Featherless row in a MANIFEST.

Step 3 — the lock. `${BASHPID:-$$}` is the whole fix at :657; copy the wording of
`record_ml_corpus.sh:994-999` rather than inventing a second explanation of the same
degradation, and keep the pointer to the ledger rows (audit-phase-18-close.md §7 row 5,
training/README.md §6 row 5). Do not switch to `flock`: it is absent on stock macOS and
the mkdir mutex is the portable choice both recorders already made.

Step 4 — the tests. Reuse the file's existing `_run` and `_clean_env` helpers and add a
fixture that builds a scratch set dir with `AILIBI_SAMPLE_DIR`, `AILIBI_MANIFEST` and the
default 4-player / 1-impostor / 1-task roster. Watch the roster: the loader reconstructs
from `roster.json`, so a run whose `--tasks-per-crewmate` disagrees with the descriptor
verifies as a tick-0 hash divergence rather than a missing file — let the script write the
descriptor itself and do not pass roster overrides unless the test is about them. Two
seeds are enough for the end-to-end case (~0.4 s each under the fake client); use ≥4 for
the two-worker case so the queue actually hands work to both. For the fail-loud injection,
the cheapest deterministic one is a sample dir made read-only before the run with its
`roster.json` already written and agreeing: `mkdir -p` and the descriptor step no-op, the
tournament records into the writable stage, and the `mv -f` at :739-746 fails into the
`.failed` path and exit 1. Skip that case when the test process is root, where mode 0555
does not block a write.

Step 5 — proving coverage. Run the end-to-end case a second time with `BASH_XTRACEFD`
pointed at a file (or plain `bash -x`) and assert the trace contains the four function
invocations; that is the quotable evidence the DoD asks for, and it beats asserting on
progress strings that a later refactor may reword.

Step 6 — what not to touch. The substrate-lever preflight at :497-534 stays exactly as it
is, including which levers it names: 20.33 extends that block for the whole Phase-20 lever
slate at once, and a second author editing it here would collide. Likewise leave the
`build_sample_report` / rubric tail (:864-917) alone — the audits/experiments shell-out
that F1 also flags is a separate finding and is not in this scope.

**Ready-to-paste prompt:** `agent_prompts/task-20-21-recorder-hardening.md`

### Task 20.22 — THE PRE-REGISTRATION (owner): bars, instruments and the decision rule, pinned from committed cells
**Branch:** `phase-20-preregistration`
**Depends on:** 20.14, 20.15 — the solvability instrument must merge first because the y-axis cells this memo quotes are its committed pins; the evidence-honesty instrument set must merge first because five of the eight primary bars read cells only that module computes, and a bar whose "before" number lives in an uncommitted review script is a bar nobody can re-run
**Section refs:** audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 — the day-1 rule "Day 1, before any code: pre-register" (:239-241), the pre-registered primary bar (:282-287) and the record order (:272-276); audits/review-2026-08-19/A/verdicts.md — the G-1 block (crew whereabouts false at neither tick N nor N−1: 148/723 = 20.5% samples/9p2i, 402/2038 = 19.7% ml_corpus/9p2i, 7/78, 11/79), the G-2 block (sole-`alibi_vs_sighting` convicting precision 12 right / 70 wrong = 14.6%; 63.5% of resolvable sighting sides never perceived by the speaker; the review's anchors corrected at HEAD — `_iter_sightings` at `meetings/transcript.py:2170-2179` yields every `SawPlayerObservation` unfiltered, and `_detect_alibi_vs_sightings` at `:2380-2494` never inspects the sighter's own record), the G-3 block (fabricated "You completed" lines 53/529 = 10.0% samples/9p2i, 15/65 = 23.1% samples/4p1i), and the G-5 / G-9 / G-12 / G-25 blocks; audits/review-2026-08-19/B/verdicts.md C-2 and C-3 (`kill_available_ticks=415 intent_kill=225 MISSED_KILL=190`, 45.8% of free zero-witness opportunities declined); audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D1 (the zero-LLM deduction oracle over 626 body meetings; 61 of 354 ejections landed on someone the crew's pooled perception had already cleared) and §D2 (adjacent-room STRONG share 148/234 = 63.2%); audits/audit-phase-19-close.md §4.1 (the committed 19.14 cells: 310/310 = 1.000 with ejectee-specific proof, 46/125 = 0.368 without, 79/79 innocent ejections inside the non-direct cell) and §4.4 (the owner's Option-A ruling that chartered this phase); tests/eval/test_deduction_metrics.py:178 and :224 (`non_direct_ejections == 33`, samples/9p2i), :256 (`(35, 89)` corpus 9p2i), :295-296 (samples/4p1i), :309-310 (the corpus-4p1i no-cell) — the pins re-verified at HEAD; tests/api/test_evidence_mechanisms.py:173, :194, :220, :249 (the four 19.11 injustice fixtures, served through the real `ReplayLoader`); eval/deduction_metrics.py:852 (`_wilson_interval` — the only interval producer any cell may quote); scripts/check_doc_facts.py:226 (`check_sample_provenance` — the win split re-derived from `replays/samples/<set>/MANIFEST.md`, the committed source for the secondary band); orchestrator/replay.py:531 (`_RETIRED_ALWAYS_ON_LEVERS`) and :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS` — `impostor_roll_call`, the one live toggle at HEAD); audits/audit-phase-18-emergence-preregistration.md:23-25 (the label key), §6 (the claim-discipline shape), §8 (THE RATIFIED DECISION section), §9 (the amendment log); audits/audit-phase-20-preregistration.md §§0-10 (the provisional memo this task pins); eval/evidence_honesty.py:226 (`CELL_DEFINITIONS` — the ten cell sentences the memo copies verbatim; tests/eval/test_evidence_honesty.py:135 pins them against each cell family's docstring, so the memo's definition text is the one the code computes); scripts/measure_baseline.py:26-55 (`--honesty --json` and `--solvability --json`, the committed readers that emit every I-2…I-12 cell); AGENTS.md:106-110 (craft rule 7 — record impact and measurement on every contract)
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run pytest -q -k "evidence_honesty or solvability or deduction_metrics"` green — every pin the memo cites resolves at this HEAD; plus an inline `python3 - <<'EOF'` reader pasted into the PR Summary that loads each cited pin and diffs it against the memo's stated cell, printing `0 mismatches` across all cells and naming any deliberate difference with its recorded cause.

The phase's whole credibility rests on one ordering: the bars exist, in the tree, before the
first fix does. The review states the rule as the wave's day-1 item
(`audits/review-2026-08-19/D/FINAL-synthesis.md` §4, :239-241), and the repo has done it once
already — the 18.4 memo, where every baseline cell was quoted from a committed pin and the
owner ratified definitions and bars by merge. This task is that gate for Phase 20. The
planning PR shipped `audits/audit-phase-20-preregistration.md` in PROVISIONAL form: the
instrument list, the bars, the decision rule and the record order are all drafted, but nearly
every baseline cell is labelled [REVIEW-DERIVED] — measured by the 2026-08-19 review's session
scripts, which were deliberately NOT committed. Today, therefore, five of the eight primary
bars have a "before" number that nobody in this repository can re-run. That is exactly the
defect the phase is elsewhere fixing in documentation, and it would be fatal here: a bar
anchored to an unreproducible figure cannot judge a record.

The pinning is now possible because the two instrument tasks have merged. `eval/solvability.py`
owns the y-axis cells — the zero-LLM candidate-set oracle over the 626 body meetings, the
singleton rate and correctness, and the 61-of-354 ejections that landed on an already-cleared
player (`audits/review-2026-08-19/A/ideas-multi-agent-researcher.md` §D1).
`eval/evidence_honesty.py` owns the honesty and bug-class cells: false crew self-placement
(20.5% samples/9p2i, `A/verdicts.md` G-1), sole-flag convicting precision (12 right / 70 wrong
= 14.6%) and grounded sighting side (36.5% of resolvable sides; `A/verdicts.md` G-2),
fabricated completion lines (53/529 = 10.0% samples/9p2i, 15/65 = 23.1% samples/4p1i;
`A/verdicts.md` G-3, `B/verdicts.md` C-2), the adjacent-room STRONG share (148/234 = 63.2%;
`A/ideas-multi-agent-researcher.md` §D2), and the context and co-intervention cells
(G-5, G-9, G-12, G-25; `B/verdicts.md` C-3's 190/415 declined free kills). The two cells that
were already committed stay where they are: the I-1 proof-vs-inference partition is quoted
from `tests/eval/test_deduction_metrics.py` (non-direct 33 at samples/9p2i, 35/89 at corpus
9p2i, 3 at samples/4p1i, the corpus-4p1i no-cell — pooled 46/125 = 0.368 with 79/79 of the
innocent ejections, restated in `audits/audit-phase-19-close.md` §4.1), and the I-13 injustice
exhibits from `tests/api/test_evidence_mechanisms.py`. After this task every cell in the memo
names a file that a stranger can run.

What the owner ratifies, and what re-anchors without ratification, follows the standing rule
this repo set at 18.4: the DEFINITIONS, the statistical conventions, the BARS and the decision
rule are the ratified content; the quoted baseline CELLS are evidence and re-anchor
mechanically at the adopting record. One consequence is load-bearing and must be stated in the
memo: where a pinned re-derivation differs from the review-measured figure, the PIN replaces
the cell and the bar's TARGET does not move with it. The targets — non-direct conviction
accuracy at least 0.60, innocent ejections under 35, false crew whereabouts under 5%,
sole-flag precision at least 50%, grounded sighting side 100%, fabricated completions 0,
adjacent-room STRONG share about 0, and the four fixtures each flipping — are ratified as
written, not recomputed from whatever the pin turns out to say. A bar that follows its own
baseline is not a bar.

The memo also fixes three things the record cannot renegotiate later. The co-intervention is
declared by name: task 20.32 repairs the scripted impostor mover before the freeze, and that
repair changes game dynamics inside the same record, so attribution of the honesty bars rests
on the offline counterfactual plus the record, never on the win split — which is reported
inside a pre-registered band and never gated. The offline-counterfactual protocol names its
command, the cells it can predict from frozen baseline-6 bytes, the cells it explicitly
cannot, and the abandon criteria. The record order is fixed as `replays/samples/9p2i` →
`replays/ml_corpus/9p2i` → `replays/samples/4p1i` → `replays/ml_corpus/4p1i`, corpus 9p2i
before any 4p1i leg because the non-direct cell has n=89 there against n=33 in the samples and
a delta on n=33 will not separate. The DAG enforces the ordering the memo claims: every lever
contract and the co-intervention depend on this task, so no substrate change can merge before
the bars are ratified. Ratification is the owner's merge of this PR; anything after it is
dated errata in the amendment log.

**Files in scope:**
- audits/audit-phase-20-preregistration.md; (the pinned version: every cell cites tests/eval/test_evidence_honesty.py / test_solvability.py / test_deduction_metrics.py; bars and decision rules as [PROPOSED — ratified at merge])
- tasks/phase-20.md; (the 'Pre-registration' preamble section points at the ratified memo — one paragraph)

**Files NOT in scope:**
- eval/ (the instruments belong to the two upstream tasks; this memo quotes them and never redefines a cell)
- replays/ (bytes never move at a pre-registration gate)
- any production or test code (a defect found while pinning routes back as its own contract, exactly as the 18.4 batch findings did)
- the STATUS line of tasks/phase-20.md (the phase close owns it)
- agents/strategic/prompts/ (prompt templates are substrate; the single prompt-set bump is task 20.31's alone)

**Definition of done:**
- [ ] Every cell in the memo's baseline table names its committed source beside it — `tests/eval/test_deduction_metrics.py` for the I-1 partition, `tests/eval/test_solvability.py` for the I-12 y-axis, `tests/eval/test_evidence_honesty.py` for I-2 through I-11, `tests/api/test_evidence_mechanisms.py` for the I-13 fixtures, and `scripts/check_doc_facts.py::check_sample_provenance` over `replays/samples/<set>/MANIFEST.md` for the secondary win split; a grep for `[REVIEW-DERIVED]` in the memo returns zero hits, and the label key is the 18.4 one — [VERIFIED] quoted from a committed pin, [INFERRED] arithmetic over quoted cells with inputs shown, [PROPOSED — ratified at merge] for every bar and rule.
- [ ] Where a pinned re-derivation differs from the review-measured figure, the memo keeps BOTH numbers, marks the pin authoritative, and states the cause in one sentence quoted from the instrument task's test comment; a silent replacement fails this item. No cell is computed by hand: every interval quoted comes from `eval.deduction_metrics._wilson_interval`, as the 18.4 memo's §10 convention requires.
- [ ] The eight primary bars are stated verbatim with the per-set cells beside the pooled figure: non-direct-cell conviction accuracy 0.368 → ≥ 0.60 pooled, no set < 0.50; corpus innocent ejections 79 → < 35; false crew whereabouts 20.5% → < 5%, every set < 8%; sole-`alibi_vs_sighting` convicting precision 14.6% → ≥ 50% with the class impostor share above the base rate; grounded sighting side → 100% of surviving STRONG sighting sides; fabricated completion lines → 0 on every set; adjacent-room STRONG share 63.2% → ~0; and each of the four 19.11 injustice fixtures stated pass/fail individually.
- [ ] The secondary cells are stated as observed-and-reported, never gated: the win split inside its pre-registered band with the baseline-6 rates re-derived from the MANIFESTs rather than quoted from prose, the solvability y-axis, and the movement-origin, marker-contamination, singular-persona, context and co-intervention cells.
- [ ] The decision rule is written in ADOPTED / FINDING / partial-adoption form, naming the exact subset of bars each verdict requires and the eligibility test for a partially adopted lever; the memo states that no bar may be re-priced after this merge and that a miss is reported as a miss.
- [ ] The co-intervention is declared by name with its attribution consequence; the offline-counterfactual protocol names its command, the cells predictable from frozen baseline-6 bytes, the cells explicitly not predictable with the reason, and the abandon criteria; the record order and the freeze list are fixed, with the power argument for the corpus-9p2i leg preceding either 4p1i leg.
- [ ] A sign-off section records that ratification is the owner's merge of this PR, and an amendment log section exists and is empty at merge; the memo's status line no longer says PROVISIONAL.
- [ ] The `tasks/phase-20.md` preamble gains one paragraph naming the ratified memo as the document the counterfactual and the record read verbatim; the STATUS line is untouched.
- [ ] The PR Summary carries the pin-diff reader's output showing `0 mismatches` and the green `pytest -k` run from Measurement.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — read `audits/audit-phase-18-emergence-preregistration.md` end to end and copy its
structure: verdict in one line, the standing rule about what re-anchors without ratification,
definitions, the quoted cells, the discipline, the rare-event framing, the ratified decision,
the amendment log, and a method section that reproduces every derived figure offline. The
Phase-20 memo already has the matching skeleton; the work is replacing contents, not
reshaping the document.

Step 2 — pin, do not re-measure. For each cell, open the test that pins it and quote the
asserted numerator and denominator with the file and the test name beside the number. Prefer
the assertion over the module: a pin is what fails when the value moves.

Step 3 — write the pin-diff reader as a heredoc in the PR Summary rather than a committed
script; scripts/ is out of scope here and the memo is a one-time gate. Read each pin by
importing the instrument module and recomputing over the committed sets — or, simpler, from the
readers the two instrument tasks committed for exactly this, `uv run python
scripts/measure_baseline.py --honesty --json` and `--solvability --json`
(scripts/measure_baseline.py:26-55) — or by parsing the
test's asserted constants, and print one line per cell: cell id, memo value, pin value, and
`OK` or `MISMATCH`. Investigate every mismatch before editing the memo — a mismatch is either
a transcription slip or a real disagreement between the instrument and the review definition,
and the second kind routes back to the instrument task as a finding rather than being papered
over in the memo.

Step 4 — do NOT add instruments. The list is closed at the thirteen rows the provisional memo
registers; a cell you wish existed is a note in the amendment log's preamble, not a new row. Equally, do not soften a bar because a re-derived baseline
looks harder than the review's figure: targets are ratified as written and only the baselines
re-anchor.

Step 5 — the rare-event discipline carries over. Any cell whose denominator cannot separate a
plausible effect is labelled advisory with the powering arithmetic shown, in the 18.4 §7
shape; the corpus-4p1i non-direct cell is the obvious member, with no cell at all.

**Ready-to-paste prompt:** `agent_prompts/task-20-22-preregistration.md`

## Wave 2 — the evidence-honesty substrate (levers default-OFF; ONE record)

### Task 20.23 — Completed-task memory comes from the engine event, not a pending-id flip
**Branch:** `phase-20-completion-from-events`
**Depends on:** 20.15 — the evidence-honesty instrument set must land first: its committed I-5 fabricated-completion cell is the OFF number this task's ON path must drive to zero, and re-running it green is the proof that the perception widening moved no cell; the ON census over the committed games belongs to the offline-counterfactual task, which owns the only OFF/ON entry point (audits/audit-phase-20-preregistration.md §8).; also after 20.22 (no lever merges before the bars are ratified); also after 20.32 (the mover repair and its I-11 instrument-mode change land before any lever, so the levers’ counterfactual pins read one instrument shape and the comparator is repaired before the freeze)
**Section refs:** G-3 (audits/review-2026-08-19/A/collated-findings.md §G-3, severity P0, corroboration 5; audits/review-2026-08-19/A/verdicts.md §claim 3 — VERDICT CONFIRMED-BUG, with the four-set prevalence table, the 100% redistribution correlation and the three minted STRONG flags) and C-2 (audits/review-2026-08-19/B/collated-findings.md §C-2 row, severity P1; audits/review-2026-08-19/B/verdicts.md §claim 4 — VERDICT CONFIRMED, with the engine+ObservationService+ingest+render repro); audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC3 (the root cause) and §4 wave-2 row 2.1 (the roadmap item this task implements); agents/memory/store.py:1155-1207 (the inference inside `_build_observations`), :1161-1168 (the false invariant comment), :1170-1177 (the PR #155 impostor-gate rationale), :1179 (the `role == "CREWMATE"` gate), :1189-1203 (the emit), :78 (`_SALIENCE_COMPLETED_TASK`); engine/tick.py:314-367 (`redistribute_dead_tasks`), :365-366 (the owned set GROWS), :401 (the kill-path call); orchestrator/game.py:1235 (the ejection-path call), :2026-2027 (dead players get no packet); engine/maps/canonical_1.yaml:45 (`dead_task_rule: redistribute`); observation/service.py:638-645 (the lexicographically-first pending pick), :647-691 (`_owned_task_ids_for_agent`, impostor branch :672-683); observation/packet.py:73 (`SelfView.owned_task_ids`, present since 15.22); agents/perception.py:326-361 (`_self_state_payload`, records no `owned_task_ids`); tests/agents/test_memory_rendering.py:835-852 (the pin that enshrines the wrong rule); tests/agents/test_perception.py:128-135 (the exact self-state payload assertion); the lever pattern — agents/strategic/prompts/loader.py:321-364 (the live default-OFF `*_enabled(env)` resolver) and orchestrator/replay.py:547-572 (`_TOGGLEABLE_LEVER_RESOLVERS`); the OFF-path instruments — tests/meetings/test_prompt_byte_golden.py:1-40 and scripts/verify_samples.sh:1-24
**Complexity:** Medium
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/agents/test_memory_rendering.py tests/agents/test_perception.py tests/eval/test_evidence_honesty.py -q` green; `uv run python scripts/measure_baseline.py --honesty replays/samples/9p2i` reports the committed OFF cell (the ratified pin 19/458 over rendered rows that reached a model; the review's offline re-render measured 53/529) with `AILIBI_TASK_COMPLETION_FROM_EVENTS=1` exported AND with it unset — the instrument scores I-5 off the recorded prompt bytes and exposes no lever slate by design (audits/audit-phase-20-preregistration.md §8), so the ON census over the 300 committed games is Task 20.34's `scripts/counterfactual_phase20.py` and the ON rule here is fixture-pinned in tests/agents/test_memory_rendering.py; and `bash scripts/verify_samples.sh` plus the prompt byte-golden stay green with the lever unset.

The memory store mints first-hand completions that never happened. `agents/memory/store.py:1161-1166`
justifies its inference on an invariant — "Its owned set only ever shrinks -- a task completes; none is
added mid-game -- so the pending id changes if and only if the previous pending task completed" — that
`engine/maps/canonical_1.yaml:45` broke two phases later: under `dead_task_rule: redistribute` a victim's
unfinished instances are re-keyed onto living crewmates (`engine/tick.py:365-366`, reached from the kill
path at :401 and the ejection path at `orchestrator/game.py:1235`), so a live crewmate's owned set GROWS
mid-game. `observation/service.py:638-645` then hands the packet the lexicographically-first owned
unfinished map id, so an inherited earlier-sorting task silently displaces the pending id and
`store.py:1178-1203` renders `[tick N] You completed X (you were in ROOM).` for a task the agent never
touched. The line carries an `observation_id`, so it is citable evidence in the meeting. Both review
tracks confirmed it independently with separate repros: A/verdicts.md §claim 3 (CONFIRMED-BUG) and
B/verdicts.md §claim 4 (CONFIRMED), and D/FINAL-synthesis.md §1 RC3 names it a root cause.

The review-measured rates over the committed baseline-6 bytes: 53/529 = 10.0% of rendered completion
lines in samples/9p2i, 15/65 = 23.1% in samples/4p1i, 140/1528 in ml_corpus/9p2i, 14/64 in
ml_corpus/4p1i — 159 of the 300 committed games hit, 67 of the false lines spoken at the table, and 3 of
them minted STRONG `alibi_vs_sighting` flags against innocents (s11 p-6 `upload_logs@14 MEDBAY`, s46 p-1
`fuel_reserves@10 ADMIN`, s13 p-5 `fuel_reserves@14 LABS`), per A/verdicts.md §claim 3. The correlation
with redistribution is 100%, not merely enriched: of the false lines in `samples/`, 58 sit at T−1/T−2 of a
crewmate kill and the remaining 7 at T−1 of a meeting ejection — both paths call `redistribute_dead_tasks`.
Because the inference is gated to `role == "CREWMATE"` (store.py:1179 — the Task-10.14 / PR #155 fix that
kept the impostor's rotating pretend id from minting fiction), the damage is strictly one-sided: the crew
poisons its own first-hand channel, on exactly the tick the next meeting litigates, while the impostors
are exempt. The store's own comment at :1174-1176 names the failure it is now suffering — a fabricated
`completed_task` alibi that "corrupt[s] the meeting/eval evidence".

The fix is to key the inference on the true invariant instead of the broken one. For a LIVING agent the
owned set loses an id only when that instance completes: redistribution only ever ADDS to a survivor
(`engine/tick.py:365-366`) and only ever empties the VICTIM, who receives no further packet
(`orchestrator/game.py:2026-2027`). So "an id that was in `owned_task_ids` last tick and is absent this
tick" is a truthful completion signal available entirely inside the observation firewall — strictly better
than the pending-id flip, because it also catches the completion the current rule DROPS (a genuine
completion whose pending id was already displaced by an inherited earlier-sorting task). It costs one
recorded field: `SelfView.owned_task_ids` has existed since Task 15.22 (`observation/packet.py:73`) but
`agents/perception.py:355-361` never writes it into the self-state payload, which is why the store
"genuinely cannot see the set" (B/verdicts.md §claim 4). The role gate then goes away without reopening
PR #155: an impostor's `owned_task_ids` is the per-seat camouflage WINDOW from
`observation/service.py:672-683`, which is constant for the whole game (no tick argument; seats are taken
over all `role == "IMPOSTOR"` players alive or dead), so the rotating pretend id never leaves it and the
disappearance rule mints nothing for an impostor — by construction, not by a role bit.

Everything ships behind `AILIBI_TASK_COMPLETION_FROM_EVENTS`, default-OFF, so the committed baseline and
every gate stay green until the Phase-20 adopting record. OFF-path bytes are identical (the perception
field is additive and unread; the render path is unchanged), pinned by the prompt byte-golden and
`scripts/verify_samples.sh` over the 100 committed sample games and by the honesty instrument's OFF cells
reproducing the review's numbers over all four sets. ON-path behaviour is fixture-pinned and paid for with
the counterfactual the record's gate reads: re-render the 300 committed games under the lever and publish
the fabricated-completion census, which must be 0. This task does NOT re-date or re-room the line (the
uniform +1 agent-clock stamp and the room-at-that-tick belong to the self-location trail task), does NOT
register the lever in the substrate stamp (Task 20.33 registers all eight Phase-20 levers at once), and
touches no prompt template (Task 20.31 owns the single prompt-set bump).

**Files in scope:**
- agents/memory/store.py; (the lever: the `task_completion_from_events_enabled` resolver beside `observation_id_rendering_enabled`, the env constant, the read once in `render_for_prompt` threaded into `_build_observations`, the ON-path disappearance rule, the deleted false-invariant comment, `__all__`)
- agents/perception.py; (record `owned_task_ids` into `_self_state_payload` — additive, one key, only read under the lever)
- agents/memory/working.py; (only if the self-state model needs the field — the episodic payload is `Mapping[str, Any]`, so the expected diff is empty)
- tests/agents/test_memory_rendering.py; (the wrong-rule pin replaced; OFF-path byte-identity; ON-path: a redistribution never mints a completion, a real completion still renders, a payload without the field renders nothing)
- tests/agents/test_perception.py; (the exact-payload assertion at :128-135 gains `owned_task_ids`)
- tests/eval/test_evidence_honesty.py; (the committed I-5 pins re-run unchanged after the perception widening — the instrument rebuilds memory through `agents.perception` — plus a lever-ON re-read (set through `monkeypatch.setenv`, not a shell export — the 20.17 hermetic guard clears `AILIBI_*` at session start) proving it is inert; the ON census is the offline-counterfactual task's)
- observation/service.py; (the :63-66 comment only — the same false invariant in prose; no behaviour change)

**Files NOT in scope:**
- engine/ (redistribution is correct engine behaviour — the Task-13.10 variant `engine/maps/canonical_1.yaml:45` selects; DESIGN.md §3.5 still documents only the older drop rule, per A/verdicts.md §claim 3's design check; nothing about the rule changes)
- orchestrator/replay.py (Task 20.33 registers this lever in `_TOGGLEABLE_LEVER_RESOLVERS` and the substrate stamp, together with the other Phase-20 levers; this task registers nothing)
- agents/strategic/prompts/ (Task 20.31 owns the single prompt-set bump; no template may move here)
- the line's tick and room (the self-location trail task owns the re-dating and the room-at-that-tick; this task must not shift a genuine completion's tick or room relative to the OFF path)
- replays/ (no bytes are re-recorded; the record is Task 20.36)

**Definition of done:**
- [ ] With `AILIBI_TASK_COMPLETION_FROM_EVENTS` unset, rendered memory and rendered prompts are byte-identical: `tests/meetings/test_prompt_byte_golden.py` and `bash scripts/verify_samples.sh` stay green over the 100 committed sample games, the three `tests/fixtures/memory_rendering/*.expected.md` fixtures are untouched, and the honesty instrument's OFF fabricated-completion cells still read the committed values over all four sets.
- [ ] `agents.memory.store.task_completion_from_events_enabled` follows the 13.5 signature `(env: Mapping[str, str] | None = None) -> bool`, reads `AILIBI_TASK_COMPLETION_FROM_EVENTS` from the passed mapping (defaulting to the process environment), accepts `1/true/yes/on` case-insensitively, is read exactly ONCE in `render_for_prompt` and threaded down as a boolean, and is pinned both ways in `tests/agents/test_memory_rendering.py` without mutating `os.environ`.
- [ ] `agents/perception.py::_self_state_payload` records `owned_task_ids` from `packet.self_state`; `tests/agents/test_perception.py` asserts the new exact payload for a crewmate AND an impostor, and asserts the field is the packet's tuple verbatim (no re-sorting, no filtering).
- [ ] With the lever ON, a crewmate whose pending task is displaced by a redistributed instance renders NO completion line — the fixture reproduces B/verdicts.md §claim 4's repro shape (pre-kill pending `upload_logs`, post-kill pending `align_engine_output`, `upload_logs` still owned) and asserts `"You completed" not in view`.
- [ ] With the lever ON, a genuine completion still renders `[tick N] You completed X (you were in ROOM).` with the same tick, room and `observation_id` as the OFF path — including the rollover case the old pin covered, the final-clear case, and the case the OLD rule dropped: a task that completes while the pending id is already held by an inherited earlier-sorting instance now renders its completion.
- [ ] The `role == "CREWMATE"` asymmetry is gone: the ON path applies the same rule to both roles, and a test drives an impostor's rotating pretend `pending_task_id` over a constant camouflage window and asserts zero completion lines — the PR #155 property held by construction rather than by a role gate.
- [ ] Fail-closed on missing evidence: a self-state payload without an `owned_task_ids` key (a hand-built fixture or a pre-widening row) mints NO completion under the lever ON, pinned by a test — the ON path never fabricates when it cannot see the set.
- [ ] `tests/agents/test_memory_rendering.py:835-852 test_pending_rollover_to_next_map_id_emits_completion` no longer pins the any-change-emits rule; it is rewritten to pin the disappearance rule (or replaced by named ON/OFF tests) and its comment states why the old premise was false.
- [ ] `tests/eval/test_evidence_honesty.py::test_i5_fabricated_completion_pins` still reads 19/458, 40/1311, 15/61 and 14/58 — unchanged by the perception widening and unchanged with `AILIBI_TASK_COMPLETION_FROM_EVENTS=1` set inside the test via `monkeypatch.setenv` (Task 20.17's session-scoped `_hermetic_ailibi_env` guard in tests/conftest.py clears the whole `AILIBI_*` namespace, so a shell export is invisible under pytest), because the instrument scores I-5 off the recorded prompt bytes and deliberately exposes no lever slate (audits/audit-phase-20-preregistration.md §8); the ON census over the four sets is Task 20.34's, and this PR quotes the OFF column beside the fixture-level ON proof.
- [ ] The false invariant comment at `agents/memory/store.py:1161-1168` is deleted; the replacement states the true rule in one sentence plus one provenance line (no docstring history narration), and the impostor-gate rationale at :1170-1177 is rewritten to say the property now holds by construction.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — the field. `_self_state_payload` (agents/perception.py:326-361) gains one key,
`"owned_task_ids": self_state.owned_task_ids`, beside `pending_task_id`. It is a tuple of map ids; keep it
a tuple (the payload already carries `fellow_impostor_ids` as one). Nothing else in production reads the
self-state payload's shape — the tactical policies read named keys (agents/tactical/impostor_policy.py:566,
agents/tactical/crewmate_policy.py:430) and the training features read `packet.self_state.owned_task_ids`
directly (agents/tactical/learned/crew_forward.py:728) — so the blast radius is the one exact-dict
assertion at tests/agents/test_perception.py:128-135. Grep before you widen.

Step 2 — the resolver. Put it in agents/memory/store.py next to `observation_id_rendering_enabled`
(:189-208), which is the same module's lever home, but copy the LIVE default-OFF shape from
agents/strategic/prompts/loader.py:321-364 rather than the retired always-True bodies: an
`ENV_TASK_COMPLETION_FROM_EVENTS` constant, a frozenset of truthy strings, `env if env is not None else
os.environ`. Export both from `__all__` (:1886). `render_for_prompt` already takes `env` and already reads
one lever this way at :275-285 — read yours in the same place and pass a plain `bool` into
`_build_observations`; do not thread the mapping into the loop.

Step 3 — the rule. In `_build_observations` (:1117-1207) keep the OFF branch byte-for-byte as it is and
add the ON branch beside it. Track the previous payload's `owned_task_ids` as a frozenset alongside
`last_pending_task` / `last_pending_task_room`; on each `self_state` event, the completed ids are
`previous_owned - current_owned`. Emit at most the ids that were the previous pending task if you want the
minimal diff, or emit each departed id — decide it, state the choice in the comment, and pin it; the
review's cell counts LINES, so a rule that emits more than one line per tick must be reflected in the
counterfactual. Keep the existing tick, room, salience and `observation_id` sources untouched so a genuine
completion's bytes do not move (the trail task re-dates later). If either payload lacks the key, emit
nothing.

Step 4 — the pins. The OFF-path proof already exists: tests/meetings/test_prompt_byte_golden.py
reconstructs every committed meeting through the real render path
(`api.replay_loader.ReplayLoader._walk` with `collect_memory=True`, then `render_for_prompt`), so an
additive payload key that nothing reads under OFF is proven inert by running it. The ON path is
proved by fixture, not by that instrument: the honesty module scores I-5 by matching its
`_COMPLETED_LINE` regex against the recorded `LLMCallRecord.prompt` (eval/evidence_honesty.py:1840-1872)
and takes no lever-slate parameter by design (audits/audit-phase-20-preregistration.md §8), so its cells
cannot move under this lever — Task 20.34's `scripts/counterfactual_phase20.py` owns the OFF/ON census.
Toggle through the `env` parameter, never `os.environ`, so the pins stay parallel-safe.

Step 5 — the numbers. Quote the four RATIFIED OFF cells — 19/458, 40/1311, 15/61, 14/58
(audits/audit-phase-20-preregistration.md §3.1) — not the review's offline re-render (53/529, 140/1528,
15/65, 14/64). §3.2 already rules on the divergence: the pin counts rendered rows that actually REACHED a
model, the review re-rendered memory offline, and the review disagrees with itself on the samples-pooled
total (68 vs 65; the instrument's own recount over the prompt population is 34). Cite that ruling in the
PR; do not re-litigate it.

**Public types introduced:**
- `agents.memory.store.task_completion_from_events_enabled`
- `agents.memory.store.ENV_TASK_COMPLETION_FROM_EVENTS`

**Ready-to-paste prompt:** `agent_prompts/task-20-23-completion-from-events.md`

### Task 20.24 — The self-location trail: an agent's memory says where it was
**Branch:** `phase-20-self-location-trail`
**Depends on:** 20.23 — the completed-task line must already be derived from the engine completion event before this task re-dates it and re-rooms it; both edits land in the same self-state loop of the memory store, and the evidence-honesty instrument arrives transitively along the same chain
**Section refs:** G-1 [audits/review-2026-08-19/A/verdicts.md §"VERDICT: PARTIALLY-TRUE — mechanism is a CONFIRMED-BUG" — the 971-render line-shape census, the 843 completed-task instances, the 16.0% / 97.0% / 100% room-match triple, the 44.3% victim-caused / 21.5% witness-caused split]; audits/review-2026-08-19/A/collated-findings.md §G-1 (P0, corroboration 10, the s30-m3 and 4p1i-s10 exemplars); audits/review-2026-08-19/A/ideas-among-us-veteran.md §V8 (the render shape); audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC1 + §4 wave-2 row 2.2 (the roadmap item this task implements); audits/audit-phase-20-preregistration.md §2 instrument I-2, §3 cell I-2 (152/723 = 21.0% samples/9p2i — the review's 148/723 = 20.5% is superseded per §3.2), §4 bar 3, §8 ("I-2 after the trail exists" is explicitly NOT predictable offline); agents/memory/store.py:1051 + :1065-1069 (`own_room_by_tick`, a LOCAL of `_collect_transitions`, consumed only at :1087 and :1104-1114 to scope OTHERS' sightings), :1173-1190 + :1240-1283 (the completed-task emission — after 20.23 it is the `_completed_task_observation` helper plus the two lever branches that call it, both still passing `room=last_self_room`), :1284-1287 (the previous-iteration `last_self_room` roll-forward that mis-rooms it), :216-242 (`task_completion_from_events_enabled`, 20.23's default-OFF resolver in this same file — the shape to clone; the retired `observation_id_rendering_enabled` at :190-209 is signature-only), :245-251 and :317 (`render_for_prompt`'s `env` thread and the resolve-once read site), :1859-1933 (`_assemble_view`'s block order and budget arithmetic); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:184 and :209, crewmate_report.j2:96 and :110 (the roll-call ask — "copied from your own record"); DESIGN.md:724 (the §6.6 worked example that specifies a tick RANGE, never built; historical design record per AGENTS.md:20-23); DESIGN.md:481 + orchestrator/game.py:1186-1190 (a meeting freezes movement); meetings/manager.py:2820-2859 (`_normalize_ballot_observation_id` nulls any id outside the voter's own set and splices a marker into `rationale_text`); AGENTS.md:76-110 craft rules 1, 2, 5, 6, 7
**Complexity:** Medium
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/agents/test_memory_rendering.py tests/eval/test_evidence_honesty.py -q` green; with the lever unset the three committed render goldens are byte-identical and `bash scripts/verify_samples.sh` is 100/100 clean; with `AILIBI_SELF_LOCATION_TRAIL=1` set in-test through `monkeypatch.setenv` or the resolver's `env` parameter (Task 20.17's session-scoped `_hermetic_ailibi_env` guard in tests/conftest.py clears the whole `AILIBI_*` namespace, so a shell export is invisible under pytest) the pinned self-placement coverage cell reads 100% of crew `whereabouts` claim ticks over each of the four committed sets (the OFF value recorded as measured beside it), and the completed-task room/tick agreement pin reads 843/843 over samples/9p2i

The agent has no record of itself. Across all 971 rendered memories in
`replays/samples/9p2i` the review's line-shape census found 41 distinct "You"
shapes and exactly one that places the agent anywhere: the suffix of `[tick N]
You completed <task> (you were in ROOM).` — 843 instances, and no dated
self-position line of any kind (audits/review-2026-08-19/A/verdicts.md §G-1).
Meanwhile every meeting prompt orders the speaker to answer the roll-call with
"one room, one tick, copied from your own record" (`accusation_round.j2:184`,
`:209`; `crewmate_report.j2:96`, `:110`). There is no such row to copy, so the
model extrapolates: crew `whereabouts` answers name a room the speaker was in
at neither the stated tick nor the tick before it 152/723 = 21.0% of the time
in samples/9p2i and 409/2038 = 20.1% in the corpus (the committed I-2 pin over
the baseline-6 bytes; the review's own 148/723 and 402/2038 are superseded per
audits/audit-phase-20-preregistration.md §3.2).
Those inventions are then stamped VERIFIED and convict: of the 79 innocent
ejections corpus-wide, 44.3% are the victim mis-stating its own position and
21.5% are a witness's mis-dated sighting, and games carrying at least one
innocent ejection end in an impostor win 39/68 = 57% against 14/132 = 11%
without.

The one anchor that does exist is itself mis-dated. For all 843 completed-task
lines the agent's real room matches the stated tick only 16.0% of the time,
matches at N−1 97.0%, and at N−2 100% — because `store.py:1285` rolls the
room forward from the PREVIOUS self-state iteration while `:1186` stamps
the CURRENT event's tick. One line, two clocks. `DESIGN.md:724` specified more
than was ever built — `- [tick 380] You completed wiring_admin (you were in
Admin tick 375-385).`, with a range — so the shipped shape is not the designed
one.

The data is already in the store: `store.py:1051` builds `own_room_by_tick`
from the agent's own self-state events at `:1065-1069` and then uses it only
to decide which of OTHERS' sightings happened in the observer's room (`:1087`,
`:1104-1114`). This task is rendering, not modelling: no new perception, no
new engine read, no prompt-template edit (the roll-call ask is unchanged, and
every game template is frozen until the single prompt-set bump task). It
renders the trail the store already keeps as coalesced spans, and it makes the
completed-task line take its tick and its room from one event instead of two.

What ships is a default-OFF lever, `AILIBI_SELF_LOCATION_TRAIL`, resolved by
`self_location_trail_enabled(env)`: with it unset the rendered bytes and every
committed replay reproduce byte-identically, so the baseline-6 gates stay
green until the adopting record. The counterfactual this task can honestly pin
offline is COVERAGE — whether the record the prompt orders the agent to copy
from now exists at the tick under discussion — because whether the model then
copies it is a behavioural question the pre-registration explicitly lists as
not predictable offline (`audits/audit-phase-20-preregistration.md` §8); bar 3
(I-2, 21.0% → < 5% on samples/9p2i, every set < 8%) is judged on the recorded bytes. Two costs are stated
rather than hidden: the block consumes token budget the observations block
used to have, so its cap is pinned against measured claim ticks and its effect
on higher-salience lines is measured; and the impostor gets the same truthful
own-record, which is the design's standing position — the tactical record is
what it is, and fabrication is the LLM's job (DESIGN.md §4.7). Crew inability
to retrace its own route was never a balance mechanism.

**Files in scope:**
- agents/memory/store.py; (the lever: a coalesced self-location trail rendered as "You were in ROOM from tick a to b" spans, plus the completed-task line re-dated to the tick its room belongs to; OFF-path bytes identical)
- tests/agents/test_memory_rendering.py; (OFF byte-identity with a perturbation case; ON: the spans match the per-tick own-room record; the completed-task tick and room agree with the engine event)
- tests/fixtures/memory_rendering/; (a new ON-path expected render fixture pair)
- tests/eval/test_evidence_honesty.py; (the counterfactual: with the trail rendered, the share of crew whereabouts claim ticks that COULD have been copied from the record is 100%; the false-rate bar itself is judged at the record)

**Files NOT in scope:**
- agents/strategic/prompts/ (the roll-call instruction is unchanged; the whole game prompt set moves once, at the prompt-set bump task, and nowhere else)
- meetings/ (grounding the prosecutorial side is its own task; this one changes what the agent can read, not what the detector accepts)
- orchestrator/replay.py (the stamp registration task binds every Phase-20 lever key to its home resolver at once — register nothing here)
- api/replay_loader.py (its `render_for_prompt` call site passes no `env` and therefore reads the same ambient default; with the lever OFF the spectator's `rendered_memory_text` is unchanged)
- eval/evidence_honesty.py and scripts/measure_baseline.py (the instrument module and its emitter belong to the honesty-instrument task upstream; this task consumes them)
- DESIGN.md (the historical design record per AGENTS.md:20-23, cited as evidence, not edited)
- engine/, observation/ (per-tick self-state perception is already correct; nothing new is perceived)

**Definition of done:**
- [ ] `self_location_trail_enabled(env: Mapping[str, str] | None = None) -> bool` lives in `agents/memory/store.py`, reads `ENV_SELF_LOCATION_TRAIL` from `env` or the process environment against the repo's truthy set, and DEFAULTS OFF; it is resolved exactly ONCE in `render_for_prompt` beside the observation-id fold and the boolean is threaded down (no deeper environment read). Pinned in `tests/agents/test_memory_rendering.py` for unset, "0", "1" and a garbage value.
- [ ] OFF-path byte-identity: with the lever unset and with it set to "0", the three committed fixtures (`crewmate_basic`, `tight_budget_drops_low_salience`, `impostor_minimal`) render byte-identically, `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` is green, and `bash scripts/verify_samples.sh` is 100/100. The identity assertion ships with a perturbation case proving it bites (a deliberately altered expected byte fails the test), per craft rule 2.
- [ ] ON-path shape: a `## Where you were:` block renders between the fixed role/tasks block and the observations block; consecutive ticks in the same room coalesce into one span and the spans chain onto ONE route line, oldest first — `- Your route (t = tick): REACTOR t12-16 -> ADMIN t17` — with in-vent steps inline and gaps rendered as `(no record)`, never bridged (AMENDED at merge per the orchestrator's encoding ruling on PR #376: the chained line holds identical coverage at 43% less displacement than one bullet per span). Pinned by a NEW golden fixture pair under `tests/fixtures/memory_rendering/` rendered with the lever ON, and by unit cases; the existing OFF-path golden parametrization keeps exactly its three names.
- [ ] The trail never claims a tick it has no record for: a gap between recorded self-state ticks BREAKS a span (no interpolation), while a meeting-boundary tick does NOT break one, because the meeting freezes movement (DESIGN.md:481, `orchestrator/game.py:1186-1190`). A property test over generated event streams asserts the spans partition the recorded ticks exactly — no gaps invented, no overlaps, no tick outside the recorded set.
- [ ] No synthetic citation ids: a trail line carries either the real `observation_id` of the self-state event that OPENS its span or no `[obs …]` prefix at all. A test asserts that every `[obs …]` id appearing anywhere in a rendered view is a member of the store's own id set — the same set `meetings/manager.py:2820-2859` validates a ballot citation against — so no rendered line can teach a model to cite an id the citation validator will null and prefix with a marker into spoken text.
- [ ] The cap is documented and empirically justified: `SELF_LOCATION_TRAIL_MAX_SPANS` is a named module constant; when it binds, the OLDEST spans are dropped (the recent route survives) and the block states the truncation in one plain-English line carrying no ids or arithmetic (craft rule 4). Its value is chosen so the coverage pin below reads 100% on every committed set, and the PR quotes the measured distribution of (meeting tick − claimed whereabouts tick) that justifies it.
- [ ] Budget interplay is measured, not assumed: the trail block is charged through the same `_estimate_tokens` arithmetic as every other block, and over the reconstructed memories of samples/9p2i at `DEFAULT_TOKEN_BUDGET` the displaced protected rows are MEASURED and pinned per set (AMENDED at merge: the zero-drop prediction was FALSIFIED — the committed 9p2i renders saturate the budget, so 100% claim coverage costs 1117 protected rows over 971 renders on samples/9p2i (479 reported testimony, 14 completions) and 2736 over 2726 on the corpus, 0 on both 4p1i sets; a reported secondary attributed per-lever by 20.34's counterfactual, never a bar). The PR quotes the mean added lines and tokens per render. Recorded deviation at merge, accepted by ruling: one cell of docs/artifacts.md (the tests/fixtures/ registry row, 19 -> 21) moved because 20.20's gate counts tracked fixture files — a prose record, not a scope entry. If the block cannot fit at all, trail lines are shed oldest-first BEFORE any observation is dropped.
- [ ] The completed-task line takes its tick and its room from ONE event: the stated tick is the completion event's engine tick plus one (the agent clock the packet loop stamps) and the stated room is the agent's own recorded room at that same tick; the previous-iteration `last_self_room` roll-forward at `store.py:1284-1287` no longer feeds the rendered line. Self-consistency leg: the room a completed-task line names equals the room the trail gives for the tick it states — asserted over the fixtures and as a property over generated streams.
- [ ] Engine-agreement leg for the same line: over samples/9p2i, 843/843 completed-task lines (the review's offline re-render census over all 971 rendered memories — not the honesty instrument's recorded-prompt population, which is 458 rows for this set per audits/audit-phase-20-preregistration.md §3.2) name the agent's engine-truth room at the stated tick under the honesty instrument's documented clock alignment (agent tick minus one equals the engine tick), with any residual disagreement enumerated and explained in the test comment rather than rounded away.
- [ ] No role asymmetry: the trail renders for every role (the crew-only gate is the shape of the bug the upstream task just removed; it is not re-introduced here). An impostor's in-vent ticks render distinguishably inside the self channel, and `test_render_passes_canonical_leak_scanners` stays green with its planted-leak counterpart still failing as designed.
- [ ] The offline coverage pin in `tests/eval/test_evidence_honesty.py`: with the lever ON, the share of crew `whereabouts` claim ticks covered by a span in the SPEAKER's own memory as rendered at THAT meeting is 100% over all four committed sets; the OFF-path value is recorded as measured beside it, never predicted. The pin's docstring states in one sentence that the false-placement rate itself (bar 3 / cell I-2) is judged at the adopting record because it depends on the model reading the line, quoting `audits/audit-phase-20-preregistration.md` §8.
- [ ] `render_for_prompt`'s docstring documents the block, the span shape, the gap and meeting-boundary rules, the cap and the id rule in one paragraph, with at most one trailing provenance line and no history narration added anywhere in the file (craft rule 1).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — verify the anchors before editing, then decide the seam.
`own_room_by_tick` is a LOCAL of `_collect_transitions` (declared at :1051,
filled at :1065-1069), not shared state; its only consumers today are the
own-room sighting scope at :1087 and the adjacency walk at :1104-1114. Lift
the per-tick map into one small module-level helper that both
`_collect_transitions` and the new span builder call, so there is a single
answer to "where was I at tick N". Grep every consumer first (craft rule 6):
that helper and the completed-task emission are the whole blast radius inside
this file.

Step 2 — the resolver. Clone the default-OFF shape already in the tree
(`agents/memory/store.py:216-242` — 20.23's default-OFF sibling in this very file — and `agents/strategic/prompts/loader.py:321-364` are the live examples): a `Final`
`ENV_SELF_LOCATION_TRAIL` constant, a module-level frozenset of truthy
strings, `environment = env if env is not None else os.environ`. Resolve once
in `render_for_prompt` next to the observation-id fold and pass the boolean
into the builder; the offline counterfactual toggles levers through the `env`
parameter and never mutates `os.environ`, so the parameter must reach the
resolver.

Step 3 — spans. Walk the recorded ticks ascending and coalesce a run only when
the next tick is adjacent AND the room is equal. Never bridge a missing tick.
Do bridge a meeting boundary: the agent does not move during a meeting, so a
span across it is true, and that is the one place where this walk deliberately
differs from `_collect_transitions` (which must NOT bridge, because OTHERS
change discontinuously across a meeting). Write that difference down in one
comment.

Step 4 — the block. `_assemble_view` owns block order and the budget
arithmetic; add the trail as a new block between the fixed lines and the
observations block so `view.startswith("## Your role: ...")` and the existing
header assertions still hold. Apply the cap before charging tokens, and shed
trail lines oldest-first if the remaining budget cannot take the whole block —
the observations block must never pay for the trail's overflow.

Step 5 — the completed-task line. After the upstream engine-event fix the
emission point may have moved; whatever it is, take the stated tick and the
stated room from the SAME self-state event, and delete the roll-forward's role
in the rendered line. Keep the line's existing `observation_id` behaviour so
its citation handle stays valid.

Step 6 — the counterfactual. Reconstruct each meeting's rendered memories the
way the honesty instrument does (the replay walker plus the served
transcripts), and resolve each spoken crew `whereabouts` claim tick against
the spans in that speaker's own render. Coverage is a property of the RENDER,
so it is computable offline; the truth of the claim is not, and the pin must
say so rather than implying the bar moved.

Step 7 — leave the neighbours alone. Co-presence coalescing, the spawn-block
drop and the salience re-order arrive later on this same file's chain, as does
the meetings block; do not pre-implement any of them, and do not tune the
token budget constant to make room.

**Public types introduced:**
- `agents.memory.store.self_location_trail_enabled`
- `agents.memory.store.ENV_SELF_LOCATION_TRAIL`
- `agents.memory.store.SELF_LOCATION_TRAIL_MAX_SPANS`

**Ready-to-paste prompt:** `agent_prompts/task-20-24-self-location-trail.md`

### Task 20.25 — Movement is a first-class claim: the detector reads 'A at T−1 → B at T' as B at T
**Branch:** `phase-20-movement-claim-shape`
**Depends on:** 20.15, 20.24 — the evidence-honesty instrument set lands first because this task pins its counterfactual against that module's committed cells instead of re-deriving a definition of its own; the self-location trail lands first because it edits the same evidence-honesty test module and because the truthful self-placement it renders is the other half of every flag pair this lever adjudicates.
**Section refs:** G-9(a) CONFIRMED-BUG — audits/review-2026-08-19/A/verdicts.md §G-9 (the twelve-claim adversarial verification; 313 `alibi_vs_sighting` flags over 300 committed games, 124 backed by a move line in the speaker's own memory, 86 spoke the destination, 38 spoke the origin (32 STRONG), ground truth 38/38 memory-true / speech-false, 25 games / 27 meetings, subjects 31 CREWMATE / 7 IMPOSTOR, 10 meetings ejected the falsely-flagged crewmate; per set 7/76, 0/3, 30/233, 1/1); audits/review-2026-08-19/A/collated-findings.md §G-9 (P0, corrob 8); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.3 (the routed change and its bar: "those 38 flags → 0, with no new flag class in their place"); agents/memory/store.py:1695-1747 (`_render_saw_player_move`; the rendered line at :1742-1745); agents/perception.py:74 (`EVENT_SAW_PLAYER_MOVE`) and :203-215 (each `packet.moved_players` entry becomes one first-hand episodic row); orchestrator/game.py:1778-1791 (packets built at the top of tick N from post-advance state plus tick N−1 events — the +1 agent-clock convention that makes `(T, from_room)` unrepresentable); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:204-209 (five observation shapes, no transition; the same five at crewmate_report.j2:105-110 and accusation_round_roll_call.j2:202-207); meetings/schemas.py:57-63 (`SawPlayerObservation`), :142-149 (the `ObservationClaim` discriminated union), :157-180 (`VentWitnessRecord`), :183-216 (`SightingRecord`); meetings/transcript.py:160-182 (the 16.7 grounding channel and its "ships INERT" precedent), :655 + :666 (the two grounding tick tolerances), :1354-1409 (the resolver homes and the resolver signature this lever clones), :1414-1567 (`detect_contradictions` — takes `vent_witness_records`, has no movement channel), :2170-2180 (`_iter_sightings`, unfiltered), :2380-2390 (`_detect_alibi_vs_sightings`); tasks/phase-13-5.md:271 (Task 13.5.4 shipped the render and deferred exactly this: "A movement-driven belief/contradiction rule is a deliberate later item"); tasks/phase-13.md:700-704 (the 13.14 owner LONE-STRONG ruling that lets one of these flags eject alone); tasks/phase-18.md Task 18.9 (the default-OFF flag-minting lever precedent and its committed-bytes counterfactual pattern); tests/meetings/test_contradictions.py:2071-2108 (the committed byte-identity walk and `_committed_meeting_entries`); tests/meetings/test_vote_tally_parity.py:107-137 (the four-set corpus pin: 707 meetings, all four sets baseline-6).
**Complexity:** Medium
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/meetings tests/eval/test_evidence_honesty.py -q` green; the counterfactual pin reads origin-spoken movement flags 38 → 0 over the four committed sets under the lever ON, with the reverse census (newly minted flags by subject role) and the total STRONG `alibi_vs_sighting` count before/after quoted in the PR Summary.

Memory can say a thing the speech schema cannot. `_render_saw_player_move` puts a witnessed transition into a
crewmate's prompt as "[tick T] You saw p-3 move from MEDBAY to LABS." (agents/memory/store.py:1742-1745), and in
the agent clock that line asserts two facts: p-3 was in MEDBAY at T−1 and in LABS at T. The five observation
shapes the model may answer with carry no transition (accusation_round.j2:205-209), so the witness re-encodes the
line as the one static placement that is never true — `saw_player(p-3, MEDBAY, T)` — and the referee compares that
placement to the subject's truthful roll-call answer. Over the 300 committed games the review measured 313
`alibi_vs_sighting` flags, 124 of them backed by a move line the speaker actually holds; 86 spoke the destination
and are fine, 38 spoke the origin and are wrong in exactly this way, 32 of them STRONG, ground truth 38/38 memory
truthful and speech false (audits/review-2026-08-19/A/verdicts.md §G-9).

Ten of those meetings ejected the person the flag framed. In seed 12 m0 the witness holds the MEDBAY→LABS line,
speaks MEDBAY at tick 3, the subject truthfully answers LABS at tick 3, the detector mints
`[alibi_vs_sighting/strong]`, and the table votes the innocent out 6–0–1 while a voter cites "the flag proves they
were in Medbay". In seed 39 m0 an IMPOSTOR holds a true EAST_HALL→CAFETERIA line about the body reporter, speaks
the origin half, and manufactures a 7–1 ejection of the reporter with both impostors riding the flag; the
impostors win the game. Because the 13.14 owner ruling lets a lone `alibi_vs_sighting` cross the ejection gate
(tasks/phase-13.md:700-704), one mis-encoded word converts straight into a lost game — and none of these ten sat
inside the probe that priced that ruling.

This is unsanctioned drift rather than a design choice: Task 13.5.4 shipped the movement render and wrote the
deferral down in its own contract — "A movement-driven belief/contradiction rule is a deliberate later item"
(tasks/phase-13-5.md:271). This task is that item, in the narrowest form that closes the defect. It ships one
default-OFF lever, `AILIBI_MOVEMENT_CLAIM_SHAPE`, with two arms. The resolution arm is what carries the 38: when a
spoken `saw_player` names a subject the SPEAKER's own first-hand movement record moved OUT of that room at that
exact tick, the placement is re-indexed at the DESTINATION before pairing — the encoding the witness meant. The
shape arm makes the transition sayable: an additive `SawMoveObservation` the turn schema accepts, which under the
lever participates as the destination placement, so once the prompt set names the shape the model no longer has to
choose between two half-truths. Grounding is the whole firewall, exactly as the vent channel draws it: a spoken
sighting with no matching record in the speaker's own channel is never rewritten, so the lever can only ever
re-read testimony the speaker demonstrably held — it can never launder a fabrication into a different room.

The bar is two-directional and pre-registered. Dissolving 38 wrong flags is only half the measurement; the other
half is the census of flags that NEWLY mint because a resolved destination placement now contradicts a subject who
was agreeing with the mis-spoken origin. Both numbers, by subject role, over the four committed sets, before any
recording — the 18.9 counterfactual pattern, and the honest price of the change in both directions.

**Files in scope:**
- meetings/schemas.py; (an additive `SawMoveObservation` shape: subject, from_room, to_room, tick — accepted by the turn schema — plus the typed `MoveWitnessRecord` grounding channel, the third sibling of the vent and sighting records)
- meetings/transcript.py; (the lever: a spoken saw_player whose speaker holds a move-line for that subject at that tick is resolved as the DESTINATION placement before contradiction detection; saw_move observations participate as 'B at T' placements; OFF-path byte-identical)
- meetings/render_contract.py; (the contract documents the new shape)
- tests/meetings/test_schemas.py
- tests/meetings/test_contradictions.py; (OFF byte-identity over committed transcripts; ON: the seed-12/39 shapes no longer mint; a true destination-vs-alibi conflict still does)
- tests/eval/test_evidence_honesty.py; (counterfactual: the 38 origin-spoken flags → 0 with no new flag class in their place)
- orchestrator/game.py; (a move-witness records accessor on the meeting-aware agent, beside the sighting/vent accessors — the LIVE feed for the movement channel)
- meetings/manager.py; (the call site that passes the move records into detection — call-site only)

Recorded deviation at merge (PR #377, orchestrator-ratified): two names (from_room/to_room) added to EXPECTED_EVAL_REPORT_FIELDS in tests/api/test_leak.py — forced by SawMoveObservation joining the ObservationClaim union; FORBIDDEN_EVAL_ENGINE_FIELDS untouched. A prose record, not a scope entry.

**Files NOT in scope:**
- agents/strategic/prompts/ (the schema line in the templates lands in 20.31's single bump; until then the model cannot emit saw_move and the detector-side resolution carries the lever)
- agents/memory/ (the move line render is unchanged)
- orchestrator/replay.py (20.33)
- api/ and frontend/ (the spectator mirror of the new observation shape; `api/replay_loader.py:2445-2496` raises `TypeError` on an unmapped claim, so the mirror must exist before any record can carry a saw_move — it belongs with the turn-annotation task that already opens those files)
- meetings/constants.py (the two threshold-owning tasks in this wave own it; this lever's one constant lives beside the existing grounding tolerances in transcript.py)
- eval/evidence_honesty.py (the cell definitions are the instrument set's; this task pins a lever-ON value, it does not define a metric)

**Definition of done:**
- [ ] With the lever OFF, `detect_contradictions` re-derives every recorded flag byte-identically over the committed corpus, and the walk is widened from the samples-only set to all four committed sets (707 meetings — the samples-only restriction and its "deferred to 18.13" comment in `tests/meetings/test_contradictions.py:2071-2096` are stale; both manifests now carry the same baseline-6 flag slate). A set that cannot re-derive is named in the PR with its cause, never silently dropped.
- [ ] OFF-path bytes are pinned elsewhere too: `tests/meetings/test_prompt_byte_golden.py` stays green and `bash scripts/verify_samples.sh` stays 100/100.
- [ ] ON, the resolution arm fires under a stated conjunction and only then: the speaker holds a `MoveWitnessRecord` for that subject whose tick EQUALS the spoken tick (no tolerance — a window could match a different transition of the same subject), whose `from_room` canonically intersects the spoken room, and whose `to_room` is canonically disjoint from it; the indexed sighting is then re-read at `to_room`. Fixtures in `tests/meetings/test_contradictions.py` reproduce the seed-12 m0 and seed-39 m0 shapes and assert no flag mints.
- [ ] ON, the three non-firing cases each have their own fixture: a spoken room matching `to_room` is untouched; a spoken origin at tick T−1 (truthful under the agent clock) is untouched; an UNGROUNDED spoken sighting — no matching record in that speaker's channel — is never rewritten. Plus the perturbation that shows the rule bites: a genuine conflict (the subject claims room C at T while the speaker's own record places them in `to_room` B at T) still mints its STRONG `alibi_vs_sighting`.
- [ ] Id-invariance is asserted, not assumed: the resolution rewrites only the indexed sighting's room, never its event id, so the direct-sighting exclusion set, the proxy-intra-turn guard, `reconstruct_stated_paths`, the absent-set derivation and every id-keyed downstream surface are untouched — pinned by `tests/meetings/test_absent_set.py` and `tests/meetings/test_transcript_reconstruct.py` staying green with the lever ON.
- [ ] `SawMoveObservation` round-trips through the turn schema (accepted unconditionally — the widen-the-contract-inert pattern, so nothing depends on the lever to PARSE it) and under the lever participates as exactly ONE placement, the destination "subject in `to_room` at T". The origin half is deliberately NOT placed at T−1; the docstring states why in one line (a second placement per shape re-opens the off-by-one class this task closes). `tests/meetings/test_schemas.py` pins acceptance, the discriminator, and that the OFF detector ignores the shape entirely.
- [ ] The committed-bytes counterfactual is pinned in `tests/eval/test_evidence_honesty.py` over all four sets, in both directions: origin-spoken movement flags 38 → 0 (20.15's I-7 cell `MovementOriginFlagCells.spoke_origin`, whose per-set 7/76, 30/233, 0/3, 1/1 `test_i7_movement_origin_flag_pins` already pins); the number of flags that NEWLY mint from a resolved destination placement, split by subject role; and the total STRONG `alibi_vs_sighting` count before and after. No new contradiction KIND appears in the ON output (asserted over the kind set, which is the review's "no new flag class in their place").
- [ ] The resolver `movement_claim_shape_enabled(env: Mapping[str, str] | None = None) -> bool` reads `AILIBI_MOVEMENT_CLAIM_SHAPE`, is read ONCE in `detect_contradictions` and threaded down as a boolean (the one-resolver-read convention at meetings/transcript.py:1554-1555), and defaults to False with no environment set. Registration into the substrate stamp is deliberately absent — Task 20.33 registers every Phase-20 lever at once.
- [ ] `meetings/render_contract.py` documents the new observation shape in the renderer contract and stays a leaf (imports only `meetings.schemas` and the stdlib).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — re-verify the defect before changing anything. Read one of the named exemplar meetings out of the
committed bytes, print the speaker's rendered memory line and the spoken observation beside the minted flag, and
quote that triple in the PR. The clock is the trap: the packet is built at the top of tick N from post-advance
state plus tick N−1 events (orchestrator/game.py:1778-1791), so the rendered "[tick T]" transition means
from_room at T−1 and to_room at T. Every comparison in this task is in that agent frame; no engine-frame tick
arithmetic appears anywhere in the diff.

Step 2 — the channel. Add `MoveWitnessRecord` (subject, from_room, to_room, tick) to meetings/schemas.py as the
third sibling of `VentWitnessRecord` and `SightingRecord`, sourced from the speaker's own first-hand
`saw_player_move` episodic rows, and give `detect_contradictions` an optional per-speaker mapping keyed by speaker
id, defaulting to None. None or an absent speaker entry grounds nothing — that default is what makes every legacy
caller and every committed re-derivation byte-identical, the same convention the vent channel uses. Do NOT widen
`SightingRecord` with from_room/to_room: it feeds the exculpatory vouch channel, and a transition is not a vouch.

Step 3 — one chokepoint. Resolve the indexed sightings once, immediately after `_iter_sightings` filtering and
before they reach `_detect_alibi_vs_sightings`, by rebuilding the `_IndexedSighting` with the destination room and
its canonical room set; keep the event id, the speaker and the observation object's identity semantics intact so
nothing id-keyed downstream can notice. Match on exact tick equality — introduce the tolerance as a named
constant beside `VENT_GROUNDING_TICK_TOLERANCE` / `SIGHTING_GROUNDING_TICK_TOLERANCE` with the value 0 and a
sentence saying why a window is unsafe here. If two of a speaker's records name the same subject at the same tick
with different destinations (engine truth forbids it; defend anyway), leave the sighting untouched and say so in
the docstring rather than picking one.

Step 4 — the shape. Add `SawMoveObservation` to the `ObservationClaim` union (meetings/schemas.py:142-149). There
is no `assert_never` over that union in production, so the addition is inert for existing consumers — but grep
before you trust that, and note in the PR that the spectator mirror (`_observation_claim_view`'s `TypeError` tail
at api/replay_loader.py:2445-2496) is out of scope and must exist before any record carries the shape. Under the
lever, index a spoken `saw_move` as a destination placement grounded the same way as the resolution arm; under
OFF, ignore it entirely.

Step 5 — the counterfactual. Reconstruct each speaker's movement records offline from the committed replays the
way the instrument set's harness rebuilds agent state — replay the recorded actions, rebuild each agent's packets
tick by tick, ingest them, and collect the first-hand movement rows — then re-run the detector with the lever ON
through the resolver's `env` parameter. Never mutate `os.environ`; every resolver in this codebase takes `env` for
exactly this reason. Report both directions: the 38 that dissolve and the flags that newly mint, by subject role.

Step 6 — what not to do. Do not consult omniscient state, the engine, or any other agent's memory: the speaker's
own record is the only admissible source, which is what keeps the lever firewall-clean and what stops it becoming
a way to correct testimony the speaker never held. Do not touch the memory render, the prompt templates, or the
weak/strong banding rules. Do not register the lever in the substrate stamp. And leave one line in the module
docstring recording that this closes the movement rule Task 13.5.4 deferred — history as history, one sentence,
no narration.

**Public types introduced:**
- `meetings.transcript.movement_claim_shape_enabled`
- `meetings.transcript.ENV_MOVEMENT_CLAIM_SHAPE`
- `meetings.schemas.SawMoveObservation`
- `meetings.schemas.MoveWitnessRecord`

**Ready-to-paste prompt:** `agent_prompts/task-20-25-movement-claim-shape.md`

### Task 20.26 — Grounding the prosecution: every spoken sighting is checked against the speaker's own record; STRONG needs two sources
**Branch:** `phase-20-grounded-prosecution`
**Depends on:** 20.24 (the self-location trail lands first — this lever judges a spoken sighting against the same first-hand record the memory now renders, so an agent can copy from the record it is prosecuted by; grounding a channel the speaker cannot read would move the injustice rather than close it), 20.25 (movement resolution lands first — it rewrites an origin-half re-speak into a destination placement inside the same sighting index this lever then grounds, and both edit the same detector function, so the order is a semantic prerequisite AND a file-collision edge)
**Section refs:** audits/review-2026-08-19/A/collated-findings.md §G-2 + audits/review-2026-08-19/A/verdicts.md (the G-2 verdict: CONFIRMED-DESIGN-CHOICE, twice ratified, P0/corrob-9); audits/review-2026-08-19/B/collated-findings.md §C-11 + audits/review-2026-08-19/B/verdicts.md (the C-11 verdict: CONFIRMED, severity corrected to P1); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 item 2.4 ("the centrepiece") + §2 claim 6 + §1 RC2; meetings/transcript.py:1486-1495 (`detect_contradictions` takes `vent_witness_records` and `move_witness_records`, and NO `sighting_records`), :2273-2282 (`_iter_sightings` yields every spoken `SawPlayerObservation` unfiltered), :2285-2325 (`_apply_movement_claim_shape`, the merged 20.25 pre-detector rewrite whose destination placements this lever must not read as ungrounded), :2696-2810 (`_detect_alibi_vs_sightings` never inspects the sighter's record), :2727-2730 (the Task 18.9 interior exemption) + :2731-2735 (the 13.14 LONE-STRONG comment), :160-181 + :3037-3063 + :3065-3172 (the Task 16.7 grounding chokepoint, wired only to the −0.05 vouch), :105 ("A STRONG flag naming a CREWMATE is a false positive"), :566 + :584-591 + :666 + :691 (the weak-marker literal, the reason literals, `PHYSICAL_CONTRADICTION_MIN_VOICES`, `SIGHTING_GROUNDING_TICK_TOLERANCE`), :3655-3715 (`_apply_proxy_intra_turn_guard`, the post-pass precedent); meetings/manager.py:1075-1079 (the per-speaker vent mapping) + :1082-1086 (the merged 20.25 per-speaker move mapping, the exact shape this task copies) + :1136, :1169, :1212, :1254 (the four detector call sites) + :1261-1272 (the 16.7 "deliberately NOT threaded" note); meetings/schemas.py:215-231 ("NEVER a contradiction flag"); orchestrator/game.py:1105 + :2806-2886 (`sighting_records` already built per participant on the live path) + :2887-2949 (`move_witness_records_for_meeting`, the DISJOINT `saw_player_move` channel); agents/memory/beliefs.py:104 + :108 + :636 (0.30 / 0.08 / −0.05); tasks/phase-13.md:700 (the 2026-06-22 LONE-STRONG owner ruling); tasks/phase-18.md Task 18.9 (the default-OFF lever + committed-bytes counterfactual precedent); tests/meetings/test_contradictions.py:2512-2740 (the committed-bytes re-derivation harness this task extends, already widened to all four sets by 20.25). Re-anchored to origin/main 46d0f7f1 after 20.24 and 20.25 merged; one correction to the harness's own comment is folded into this task's scope (below).
**Complexity:** Integration
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/meetings tests/api/test_evidence_mechanisms.py tests/eval/test_evidence_honesty.py -q` green; the counterfactual cells quoted in the PR Summary — STRONG `alibi_vs_sighting` 234 → after for this lever alone and 268 → after with the merged movement lever also ON, grounded share of surviving sighting sides 100%, impostor share of surviving STRONG subjects against the 25.3% base (quoted, not gated), and how many of the 70 sole-flag wrongful-ejection meetings still carry a STRONG flag on the innocent; sole-flag PRECISION cannot be measured until the record, so the pre-record proxies are the impostor share and the grounded share.

The project built the right thing once, on the wrong half. A spoken `saw_vent`
is checked against the speaker's own typed record before it can mint a flag
(the 15.4 chokepoint), and a spoken `saw_player` is checked against the
speaker's own record before it can earn its subject the −0.05 vouch (the 16.7
chokepoint at `meetings/transcript.py:3065-3172`). The PROSECUTORIAL half was
never wired: `_iter_sightings` (`:2273-2282`) yields every spoken
`SawPlayerObservation` unfiltered, `_detect_alibi_vs_sightings` (`:2696-2810`)
never reads `sighting.speaker` except for the proxy re-target, and
`detect_contradictions` (`:1486-1495`) has no `sighting_records` parameter at
all — it structurally cannot ground this kind. `meetings/schemas.py:226` states
the asymmetry as doctrine: grounding a sighting feeds the vouch channel,
"NEVER a contradiction flag". The live path already HOLDS the missing input:
`orchestrator/game.py:1105` puts each participant's
`sighting_records_for_meeting()` on `MeetingParticipant`, and
`meetings/manager.py:1261-1272` records in prose that the mapping is
"deliberately NOT threaded" because threading it would move committed bytes.
This task threads it, behind a lever, so the bytes move only at the record.

The cost of the asymmetry is the largest single defect the review found, and
both tracks found it independently. Review-measured over the committed
baseline-6 bytes (A/verdicts.md §G-2): resolving the 170 resolvable sighting
sides against the sighter's own per-tick visibility, **63.5% were never
perceived by that speaker at that tick** (28.8% not even within ±2 ticks); the
STRONG `alibi_vs_sighting` class names an impostor **33/192 = 17.2%** against a
25.3% random baseline of living voters — *below chance*, binomial one-sided
p=**0.0048**; as the SOLE convicting evidence it is **12 right / 70 wrong =
14.6% precise**, against `vent_sighting`'s 310/316; **70 of the 79 wrongful
ejections carry one, and in all 70 it is the only strong flag on the victim**;
82 meetings whose only strong flag is this kind eject 77 times (93.9%) versus
42/306 (13.7%) with no strong flag. B/verdicts.md §C-11 re-derives the same
shape from engine role-truth on 96 games: 60 STRONG flags, **53 naming a
crewmate (88.3%)**, 17 of them minted off an impostor-authored sighting, while
the grounded sibling reads `vent_sighting` 107/107 impostor; ejections whose
only strong flag was this kind split IMP 3 / CREW 20, i.e. **80% of that
corpus's wrongful ejections**. Re-derived at HEAD by the planning session over
all four committed sets (707 meetings, 435 ejections): the recorded census
reproduces the review's table exactly — `alibi_vs_sighting` 234 STRONG / 79
weak, `vent_sighting` 440 STRONG, `alibi_vs_physical` 37 STRONG / 5 weak,
`alibi_conflict` 35 weak — and **187 of the 234 STRONG flags (79.9%) rest on a
single-tick alibi window with the sighting on that same tick**.

The lever installs three rules on this ONE kind. (a) GROUNDING: a spoken
sighting is GROUNDED iff its speaker holds at least one own `SightingRecord`
matching it — same subject, canonically intersecting room, tick within
`SIGHTING_GROUNDING_TICK_TOLERANCE` — reusing `_sighting_observation_matches_record`
verbatim, the same predicate the vouch channel uses; an ungrounded sighting can
still mint a flag (flags are information, §5.4) but never a STRONG one. A
placement produced by the merged 20.25 `_apply_movement_claim_shape` — either
arm — is GROUNDED BY CONSTRUCTION and exempt from this predicate: that pass
emits it only when the SPEAKER's own `MoveWitnessRecord` confirms the
transition, and the two episodic channels are disjoint (`saw_player` vs
`saw_player_move`, `orchestrator/game.py:2806-2886` vs `:2887-2949`), so an
observer who witnessed a DEPARTURE holds no `SightingRecord` at the destination
room (`observation/service.py::_moved_players_for_agent`). Without the exemption
this lever would demote the 58 engine-true STRONG flags 20.25 pinned as newly
minted, cancelling its own dependency at the record. (b) TWO
SOURCES: a surviving STRONG `alibi_vs_sighting` needs
`GROUNDED_PROSECUTION_MIN_SOURCES` distinct grounded speakers contradicting the
same subject over the same claim, OR one grounded source plus a physical anchor
— a `vent_sighting` or `alibi_vs_physical` flag naming that subject in this same
meeting, the two channels that are grounded by construction. (c) SINGLE-TICK
ENDPOINT: the degenerate `from_tick == to_tick` self-placement stops being
adjudicated as its own interior, so it keeps the pre-18.9 narrow-window /
endpoint band. Rules (b) and (c) knowingly SUPERSEDE two owner rulings for the
post-20 substrate: the 2026-06-22 LONE-STRONG relaxation
(`tasks/phase-13.md:700`, "a single-witness `alibi_vs_sighting` contradiction
MAY cross the gate") and the Task 18.9 endpoint-band exemption that promoted
roll-call whereabouts answers to STRONG. Both were adopted on evidence and are
being reversed on more of it; the module docstring records each in one
history line and the phase doc carries the ruling.

The scope firewall is deliberate and narrow. `vent_sighting` (440/440 impostor)
and `alibi_vs_physical` (37 STRONG, already two-voice-gated) are UNTOUCHED —
their counts over the committed sets are pinned unchanged under the lever, and
`alibi_conflict` has no sighting side to ground. The lever is inert twice over:
OFF by default, and a NO-OP when the caller supplies no per-speaker mapping —
one predicate gates all three rules, so the record-free re-derivers (eval,
audit workflows) keep the pre-20.26 rules rather than silently reading every
sighting as fabricated. Before the record, the honest price is published: the
counterfactual re-runs the detector under the lever over the 300 committed
games' reconstructed inputs and quotes what the class becomes, in both
directions — the pre-registration's falsifiable prediction, made before the
23 h event that would test it.

**Files in scope:**
- meetings/transcript.py; (the lever: `detect_contradictions` receives the per-speaker SightingRecords; a spoken sighting not grounded in the speaker's own record cannot mint a STRONG flag (weak at most, labelled ungrounded); a STRONG alibi_vs_sighting requires two independent grounded sources OR one grounded source plus a physical/vent anchor; single-tick endpoint windows are suppressed; OFF-path byte-identical)
- meetings/manager.py; (pass the sighting records it already builds for vouching into detection — call-site only)
- meetings/constants.py; (the lever's thresholds as named constants)
- tests/meetings/test_contradictions.py; (OFF byte-identity; ON fixtures for each rule; the seed-17 m0 / seed-23 m1 / seed-8 m4 injustice shapes do not mint STRONG)
- tests/meetings/test_manager.py; (the wiring)
- tests/api/test_evidence_mechanisms.py; (the four 19.11 injustice fixtures read under the lever: each records its new outcome)
- tests/eval/test_evidence_honesty.py; (counterfactual: STRONG alibi_vs_sighting count, grounded share, impostor share under the lever over the 300 committed games)

**Files NOT in scope:**
- agents/strategic/prompts/ (the "VERIFIED evidence" wording is the single prompt-set bump, Task 20.31 — no template byte moves here, and no other task in this phase may touch a `.j2`)
- agents/memory/ (the records are built by the manager from memory; memory is not edited)
- eval/deduction_metrics.py (reads flags; unchanged)
- eval/evidence_honesty.py (the instrument module is Task 20.15's; this task CONSUMES its cells and must not redefine one — if a needed cell is missing, say so in the PR rather than re-implementing it here)
- eval/meeting_quality.py, eval/vote_correctness.py, eval/watchability.py, audits/workflows/extract_gameplay_facts.py (record-free re-derivers; the lever is a structural no-op for them — see Integration risk)
- meetings/voting.py, agents/memory/beliefs.py (the §4.6 gate and the 0.30 / 0.08 / −0.05 deltas are untouched: this task changes CLASSIFICATION only, the 13.14 precedent)
- orchestrator/replay.py (Task 20.33 registers every Phase-20 lever in the substrate stamp at once; this task registers nothing and adds no `SUBSTRATE_FLAG_KEYS` entry)
- replays/ (no committed byte moves; the counterfactual reads them and writes nothing)

**Definition of done:**
- [ ] `meetings.transcript.grounded_prosecution_enabled(env)` follows the 13.5 resolver signature, defaults OFF on an unset/empty/unrecognised value, accepts `1/true/yes/on` case-insensitively, and is read ONCE in `detect_contradictions`, which threads the boolean down (the 18.9 one-read convention).
- [ ] OFF-path byte identity: `detect_contradictions` re-derives the recorded flags over ALL 707 committed meetings in the four sets (`tests/meetings/test_contradictions.py`), with `env` absent and `env={}` agreeing, and with the sighting mapping supplied but the lever OFF also agreeing. Task 20.25 already widened that walk to all four sets (`_COMMITTED_SETS`, `_COMMITTED_MEETINGS = 707`) and removed the samples-only comment, so this task extends the existing walk rather than widening it; the one residual stale line — the vent-tick divergence note still calling ml_corpus/9p2i seed 1075 "now outside this samples-only walk" — is corrected here.
- [ ] `bash scripts/verify_samples.sh` stays 100/100 and `tests/meetings/test_prompt_byte_golden.py` stays green (204 committed meetings), with the lever unset — the standing OFF-path proof that no rendered or recorded byte moved.
- [ ] Rule (a) is fixture-pinned in `tests/meetings/test_contradictions.py`: a speaker with no matching record mints an `alibi_vs_sighting` carrying the ungrounded weak reason and never a STRONG one; the perturbation — give that speaker a matching record — restores STRONG on the identical transcript; and a move-derived placement (a `SawMoveObservation` the speaker's own `MoveWitnessRecord` confirms, with NO `SightingRecord` at the destination room) reads GROUNDED, so the movement lever's newly minted flags survive with both levers ON.
- [ ] Rule (b) is fixture-pinned: one grounded source alone bands weak; two grounded sources from DISTINCT speakers band STRONG; the SAME speaker grounding twice (two records, or two sightings in one turn) stays weak (the double-count guard); one grounded source plus a `vent_sighting` or `alibi_vs_physical` anchor naming the same subject bands STRONG.
- [ ] Rule (c) is fixture-pinned: a `from_tick == to_tick` self-placement contradicted at that tick bands weak under the lever (the pre-18.9 narrow-window/endpoint reasons, unchanged literals); the perturbation — widen the claim to a multi-tick window with an interior sighting — mints STRONG.
- [ ] Non-interference is pinned over the committed sets under the lever ON with reconstructed inputs: `vent_sighting` 440 STRONG, `alibi_vs_physical` 37 STRONG / 5 weak, `alibi_conflict` 35 weak — all unchanged; only `alibi_vs_sighting` moves, and no flag's `contradiction_id`, `kind`, `event_a_id`, `event_b_id` or `subjects` changes (a demotion rewrites the description only, so the detector's sort and every citation id are stable).
- [ ] The three named injustice shapes are pinned by name in `tests/meetings/test_contradictions.py`: samples/9p2i seed 17 m0, seed 23 m1 and seed 8 m4 mint no STRONG `alibi_vs_sighting` on the ejected crewmate under the lever, each case naming which rule bit.
- [ ] `tests/api/test_evidence_mechanisms.py` keeps its frozen-pipeline assertions over the served DTOs unchanged (the lever is OFF for the served bytes) and ADDS one lever-ON counterfactual read per mechanism, recording each fixture's new outcome explicitly — `provenance_impossible_sighting`, `content_vs_own_memory_miss`, `one_tick_interval_artifact`, `equal_weight_conflict` — as asserted values, never as a loosened assertion.
- [ ] `meetings/manager.py` passes the per-speaker `sighting_records` mapping (built from `MeetingParticipant.sighting_records`, participants with no records omitted) into ALL FOUR `detect_contradictions` call sites, so a mid-chain turn prompt and the final recorded flag set read one grounding source (the 15.4 threading convention); `tests/meetings/test_manager.py` pins the wiring and pins that the mid-chain and final derivations agree.
- [ ] The counterfactual pins in `tests/eval/test_evidence_honesty.py`, over the four committed sets under the lever ON with per-speaker records reconstructed from the replay, quoted for BOTH slates — this lever alone against the 234 committed-byte baseline, and this lever composed with the merged movement lever against its 268 baseline (`tests/eval/test_evidence_honesty.py::test_the_price_of_the_lever_in_the_other_direction`), which is the slate the record actually runs: STRONG `alibi_vs_sighting` 234 → after and 268 → after; the grounded share of surviving sighting sides = 100%; the impostor share of surviving STRONG subjects against the 25.3% base (quoted, not gated); and, over the meetings behind the 70 sole-flag wrongful ejections, how many still carry a STRONG flag on the innocent (quoted).
- [ ] The module docstring records the two supersessions in one history line each (the LONE-STRONG relaxation and the endpoint-band exemption, each naming the ruling it supersedes and that it applies only with the lever ON) — history, not narration; the phase-doc ruling is the assembler's, not this task's.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — the input seam. Widen `detect_contradictions` with a keyword-only
`sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]] | None = None`,
exactly mirroring `vent_witness_records`. Gate all three rules on ONE predicate
computed once at the top: the resolver is ON AND the mapping is non-empty. A
caller with no mapping keeps the pre-20.26 rules by construction — that is what
makes the record-free re-derivers safe and what makes the OFF-path pin trivially
true. Say so in the docstring the way the 16.7 chokepoint states its own
record/replay boundary.

Step 2 — rule (c) rides an existing branch. `_detect_alibi_vs_sightings` already
takes `whereabouts_interior_flags: bool` and its `False` branch is the
byte-identical pre-18.9 path (`meetings/transcript.py:2727-2730` and the comment
above it). Thread the new boolean in and make `interior_exempt` require it to be
OFF; nothing else in that function changes, and the weak-reason literals stay
untouched.

Step 3 — rules (a) and (b) are a post-pass, the `_apply_proxy_intra_turn_guard`
shape (`:3655-3715`). Build two indexes once: `event_id -> speaker` for sighting
events (the guard already builds a speaker index — reuse the pattern), and
`event_id -> grounded?` from `_sighting_observation_matches_record` over the
speaker's own rows. Run the pass AFTER the 10.10 guard and AFTER the vent flags
are joined, so the physical-anchor set is complete. Touch only
`kind == "alibi_vs_sighting"` flags that are not already weak (an existing weak
marker means the flag is already banded — never double-mark), and rebuild a
demoted flag through the same description builder with the reasons appended in
one fixed order (ungrounded first, then lone-source) so the output is
deterministic. `_build_contradiction` derives `contradiction_id` from the kind
and the sorted event-id pair, so a re-description leaves ids, sort order and
ballot citations byte-stable.

Step 4 — independence means DISTINCT SPEAKER IDS. Collect the grounded
contradicting sightings for a given (subject, claim) as a set of speaker ids,
excluding the subject itself and the alibi's own speaker; one speaker with two
records or two sightings is ONE source. The physical anchor is a
`vent_sighting` or `alibi_vs_physical` flag naming the same subject in this
meeting's flag set — both are grounded channels, so the anchor never
re-introduces ungrounded speech.

Step 5 — the constant. `GROUNDED_PROSECUTION_MIN_SOURCES = 2` is homed in
`meetings/constants.py` (stdlib-only leaf, the 15.6 constant-homing convention)
so the pre-registration memo can cite it without importing the 3-KLoC detector;
the tick tolerance is the existing `SIGHTING_GROUNDING_TICK_TOLERANCE`, reused,
never re-declared. The weak-reason string literals stay beside their siblings in
`meetings/transcript.py`.

Step 6 — the counterfactual reconstructs, it does not peek. Per-speaker
`SightingRecord`s come from rebuilding each participant's own memory from the
replayed packets and reading the accessor's projection (the instrument module's
reconstruction, the same one the review's harness used) — never from omniscient
state, and never by parsing a description. Toggle the lever through the `env`
parameter of the resolver, never by mutating `os.environ`. Quote the cells in
the PR Summary in both directions: what stops being minted AND what the class
looks like after.

**Public types introduced:**
- `meetings.transcript.grounded_prosecution_enabled`
- `meetings.transcript.ENV_GROUNDED_PROSECUTION`
- `meetings.transcript.WEAK_REASON_UNGROUNDED_SIGHTING`
- `meetings.transcript.WEAK_REASON_LONE_GROUNDED_SOURCE`
- `meetings.constants.GROUNDED_PROSECUTION_MIN_SOURCES`

**Integration risk:**

This is the phase's centrepiece and the widest `meetings/transcript.py` change
since the 13.14 reversal: three rules, one lever, the vouch path untouched.

Risk 1 — over-suppression. The vent channel must not move: `vent_sighting` flags
are grounded by construction and must keep 440/440 over the committed sets, and
`alibi_vs_physical` (37 STRONG) is already two-voice-gated, so neither is
re-banded here. The pass filters on `kind == "alibi_vs_sighting"` and on the
absence of an existing weak marker; the census pin above is what proves it. The movement channel must not move either: the 58 STRONG flags the merged 20.25 lever newly mints are grounded in the speaker's own `MoveWitnessRecord`, not in a `SightingRecord`, so applying rule (a)'s predicate over the sighting channel alone would demote every one of them — the grounded-by-construction exemption is what stops this lever cancelling its own dependency.

Risk 2 — a second-source definition that counts the same speaker twice. One
speaker holding two matching records, or emitting two sightings in one turn, is
ONE source; the subject and the alibi's own speaker are never sources. The
double-count case has its own fixture, and it is the shape most likely to pass a
casual review while restoring exactly the lone-witness conviction this lever
exists to remove.

Risk 3 — the 19.11 fixtures change MEANING under the lever. Their frozen
assertions describe the served committed bytes and must stay exactly as they
are; the lever-ON reading is an ADDITIONAL recorded outcome per mechanism.
Loosening an assertion to make both readings pass would delete the exhibit's
evidentiary value, which is the one thing Task 19.11 built it for.

Risk 4 — the record-free re-derivers. `eval/meeting_quality.py`,
`eval/vote_correctness.py`, `eval/watchability.py` and
`audits/workflows/extract_gameplay_facts.py` call `detect_contradictions`
without any typed records, so they already lose the whole grounded vent channel
relative to the recorded flags; after the Phase-20 record their
`alibi_vs_sighting` re-derivation will diverge too. This task does NOT change
them — the "mapping absent means pre-20.26 rules" gate keeps them exactly where
they are — but the phase's own instruments must read RECORDED flags or
reconstruct the records, never the record-free re-derivation, or they will
measure the old substrate on new bytes. State this explicitly in the PR.

Risk 5 — owner-ruling supersession. Two ratified rulings are reversed for the
post-20 substrate. They are reversed behind a default-OFF lever, with the
counterfactual published before the record, and each is recorded in one
docstring line; nothing about the pre-record substrate changes, so a reader of
the committed bytes still sees the rulings that produced them.

**Ready-to-paste prompt:** `agent_prompts/task-20-26-grounded-prosecution.md`

### Task 20.27 — Map-aware flag arbitration: adjacent rooms within one tick are not a contradiction
**Branch:** `phase-20-map-aware-arbitration`
**Depends on:** 20.26 — the grounded-prosecution rules rewrite the same `alibi_vs_sighting` read-site and re-band its STRONG tier, so this lever must compose with the banding that survives that task rather than with the one it replaces
**Section refs:** audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D2 (the geometry-blind aggregation; the 234-flag adjacency census) and §R1 (rank 1, "kill the corridor artifact"); audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave-2 row 2.5; audits/review-2026-08-19/A/verdicts.md §(d) (0/16,905 move intents ever named a non-adjacent room — the engine enforces the geometry the detector ignores); audits/audit-phase-20-preregistration.md §2 instrument I-6, §3 baseline cell (148/234 = 63.2% pooled), §4 bar 7 (63.2% → ≤ 5%), §6 (this lever is a named partial-adoption candidate), §8 (the offline counterfactual reads I-6); meetings/transcript.py:2836-2961 (`_detect_alibi_vs_sightings`, the single read-site), :2939-2950 (the `weak_reasons` assignment and the endpoint band it must join), :597 + :608 + :626-631 (`NARROW_ALIBI_WINDOW_TICKS`, `WEAK_CONTRADICTION_MARKER_PREFIX`, the `WEAK_REASON_*` literals), :758-789 (`CANONICAL_ROOMS` — the frozen "DATA, not an engine import" precedent this task extends), :812-846 (`canonical_rooms`), :849-868 (`is_weak_contradiction`), :1444-1501 (the Task-18.9 `ENV_*` + resolver pair whose shape this lever mirrors), :1580-1591 + :1754-1765 + :1792-1802 (`detect_contradictions`: the signature, the read-the-resolver-once block, the call that threads the boolean down); meetings/constants.py:1-22 (the stdlib-only leaf rule) and :54-73 (the resolver/threshold homing precedent); tests/meetings/test_contradictions.py:1571-1656 (the resolver-test shape), :3238-3266 (`_COMMITTED_SETS` / `_committed_meeting_entries` — all FOUR sets, `_COMMITTED_MEETINGS = 707`, since 20.25), :3412-3458 (the committed-bytes re-derivation pin), :3542-3543 (`_L1_ENV` / `_L2_ENV`), :3629-3755 (the lever-census harness); tests/meetings/test_transcript.py:715 (the sibling `CANONICAL_ROOMS == load_canonical_map().rooms` pin); engine/maps/canonical_1.yaml:178-203 (the 11 room edges, every one `traversal_ticks: 1`) and :184 (EAST_HALL↔ENGINEERING, the exemplar doorway); replays/samples/9p2i/replay-seed-17.jsonl (the exemplar flag text, present in the committed bytes)
**Complexity:** Small
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record — ON re-bands flag descriptions, and those strings render into turn and ballot prompts and drive belief Rule 2's graduated delta, so the changed bytes wait for the record
**Measurement:** `uv run pytest tests/meetings tests/eval/test_evidence_honesty.py -q` green and `bash scripts/verify_samples.sh` 100/100 with the key unset; then the I-6 cell over the four committed sets under `AILIBI_MAP_AWARE_ARBITRATION=1` — pooled baseline 148/234 = 63.2%, bar 7 asks for ≤ 5% but a re-derivation against this task's own predicate lands at 8/94 = 8.5% (a MISS, reported as a miss) — pasted into the PR Summary with per-set numerators, the un-gated `adjacent_any_gap` beside the registered cell (bar 7 requires both), and the count of ejections that lose their only STRONG flag

The one cross-agent aggregation the project has is geometry-blind. `_detect_alibi_vs_sightings`
compares a room-at-a-tick to a room-at-a-tick, and nothing under `meetings/` knows that the
station is a graph. Review-measured over the committed baseline-6 bytes and pinned as
instrument I-6 by the evidence-honesty instrument task: **148 of 234 (63.2%) STRONG
`alibi_vs_sighting` flags name two rooms that share a doorway** — one tick of walking
reconciles both statements — **130 of those 148 name innocents**, 187/234 rest on a
single-tick alibi window, and the 234 drove 126 ejections of which **78 were adjacent-room
and 68 of those 78 (87.2%) ejected an innocent**
(audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D2). The same census found **0
of 7,458 meeting prompts carrying a room list, an adjacency table or a travel time**, so
neither the detector nor the reader it feeds can tell a corridor from a lie. This is the
largest single measured defect in the gameplay track and the review ranks its repair first.

The exemplar is in the committed bytes. `replays/samples/9p2i/replay-seed-17.jsonl` carries,
verbatim, `Alibi places p-1 in ENGINEERING (ticks 6-6); sighting reports p-1 in EAST_HALL at
tick 6.` — printed twice in the same flag block, one line under a *grounded* `vent_sighting`
naming the real impostor. EAST_HALL and ENGINEERING are joined by a doorway with
`traversal_ticks: 1` (engine/maps/canonical_1.yaml:184). `p-1` was truthfully in EAST_HALL at
t4 and ENGINEERING at t5–t6; an impostor re-dated a true sighting by one tick and manufactured
a STRONG, prompt-labelled "VERIFIED" contradiction out of a corridor. `p-1` was ejected 7–1,
both impostors survived, and a crewmate who had named the right suspect in its own turn voted
against itself because a label outranked its own reasoning. The polarity is worth stating: the
engine never permits a non-adjacent step — the review re-derived **0 of 16,905 move intents
naming a non-adjacent room** (audits/review-2026-08-19/A/verdicts.md §(d)) — so the geometry
the detector ignores is the geometry the engine enforces on every tick of every game.

What ships is the detector half, behind a default-OFF lever. `AILIBI_MAP_AWARE_ARBITRATION`
resolves through `meetings.transcript.map_aware_arbitration_enabled` with the 13.5 signature,
is read ONCE in `detect_contradictions` and threaded down as a boolean — the Task-18.9
convention at meetings/transcript.py:1754-1802, one resolver read, one read-site. ON, an
alibi/sighting pair whose canonical room sets are **one doorway hop apart** AND whose sighting
tick sits **within one tick of an edge of the alibi window** carries a new weak reason instead
of standing STRONG. The flag is demoted, never dropped: flags are information (DESIGN.md §5.4),
the id set is identical between OFF and ON, and `is_weak_contradiction` then routes the pair
through belief Rule 2's graduated down-weight — a corridor informs, and can no longer eject
alone. A two-hop pair keeps its STRONG band, and so does a sighting buried two or more ticks
inside a multi-tick claim of continuous presence, because one hop cannot reconcile that: an
out-and-back excursion costs two ticks and contradicts the claim's interior anyway.

Adjacency arrives the way `CANONICAL_ROOMS` already does, and for the same reason. That
constant (meetings/transcript.py:758-789) is a frozen room allowlist duplicated out of the map
under an explicit "This is DATA, not an engine import" rationale — `meetings` must stay
engine-free because `agents` imports it — and it is kept honest by an equality pin against
`engine.world.load_canonical_map()` at tests/meetings/test_transcript.py:715. This task adds
the neighbour table beside it under the same discipline, with a pin that additionally asserts
every room edge costs exactly one tick, so the phrase "one hop = one tick" cannot quietly stop
being true. No signature widening, no call-site wiring, no new detector input: the rule stays a
pure function of the transcript and a frozen table, which is what keeps the replay-stability
invariant (DESIGN.md §0 rule 1) untouched. The map card in the meeting prompt is the agent-side
half of this repair and belongs to the single prompt-set bump; this task ships no template byte.

**Files in scope:**
- meetings/transcript.py; (the lever: the env key and resolver beside the Task-18.9 pair, the frozen `CANONICAL_ROOM_NEIGHBORS` table beside `CANONICAL_ROOMS`, the new weak reason, and the one read-site inside `_detect_alibi_vs_sightings`)
- meetings/constants.py; (the lever's two thresholds as named constants — the module stays a stdlib-only leaf)
- tests/meetings/test_contradictions.py; (OFF byte-identity over the committed sample bytes; ON: the adjacent-room one-tick shape demotes, a two-hop or two-tick pair still mints; the engine-equality pin for the table and its perturbation)
- tests/eval/test_evidence_honesty.py; (the counterfactual: the I-6 adjacent-room STRONG share OFF and ON over the four committed sets, plus the drift guard between the instrument's classifier and the detector's predicate)

**Files NOT in scope:**
- engine/ (the map is read as pinned data, never imported from `meetings`)
- agents/strategic/prompts/ (the adjacency card in the meeting prompt is the single prompt-set bump; no template byte moves here)
- orchestrator/replay.py (the substrate-stamp registration is done for all Phase-20 levers at once by the stamp-registration task; do NOT add the key to `_TOGGLEABLE_LEVER_RESOLVERS` here)
- meetings/manager.py, orchestrator/game.py (no call-site change is needed: the rule is a pure function of the transcript and the frozen table, so the four live `detect_contradictions` calls are untouched)
- eval/evidence_honesty.py (the I-6 instrument already exists; this task reads it and pins its cells, it does not re-implement or re-define it)
- tests/meetings/test_transcript.py (the sibling room-allowlist pin is cited as precedent, not edited)

**Definition of done:**
- [ ] `meetings.transcript.map_aware_arbitration_enabled(env: Mapping[str, str] | None = None) -> bool` reads `AILIBI_MAP_AWARE_ARBITRATION`, returns False in a bare environment, and is read exactly once in `detect_contradictions` and threaded down as a boolean parameter; `tests/meetings/test_contradictions.py` pins default-OFF, the truthy/falsey value table, and that the passed mapping is neither mutated nor consulted twice — mirroring the resolver tests at :1571-1656.
- [ ] OFF-path byte identity: the committed-bytes walk at `tests/meetings/test_contradictions.py:3412-3458` is extended so re-deriving `detect_contradictions` with the key absent and with `env={}` still reproduces the recorded flags byte-identically on every one of the 707 committed meetings across all four sets; `uv run pytest tests/meetings/test_prompt_byte_golden.py` and `bash scripts/verify_samples.sh` (100/100) stay green.
- [ ] ON behaviour, fixture-pinned in `tests/meetings/test_contradictions.py`: a single-tick alibi in ENGINEERING contradicted by a sighting in EAST_HALL at the same tick demotes to weak carrying `WEAK_REASON_ADJACENT_ONE_TICK`, and `is_weak_contradiction` returns True for it; a two-hop pair (ENGINEERING versus CAFETERIA) still mints STRONG; a sighting two or more ticks inside a multi-tick window still mints STRONG; a pair already weak for another reason gains the new reason in a fixed, byte-stable position rather than replacing the existing marker text.
- [ ] The flag set is re-banded, never thinned: a test asserts the OFF and ON legs over the committed sample bytes carry the identical `contradiction_id` set, and that every flag whose band changes is an `alibi_vs_sighting` (no other kind moves).
- [ ] The table is pinned and the pin bites: `CANONICAL_ROOM_NEIGHBORS` equals `{room: load_canonical_map().room_neighbors(room)}` for every canonical room, and every room edge in the canonical map has `traversal_ticks == 1`; a perturbation case (one flipped neighbour entry) is shown to fail the pin, so the gate cannot silently pass.
- [ ] Counterfactual pin in `tests/eval/test_evidence_honesty.py` over the four committed sets: the I-6 adjacent-room STRONG share OFF and ON per set and pooled, and the count of ejections whose only STRONG flag is an adjacent-room one — the flags that would lose their sole STRONG backing. The review's pooled 148/234 = 63.2% is re-derived rather than restated, and any difference from the pre-registration cell is quoted and explained in the PR.
- [ ] Instrument/detector drift guard: a test asserts the ADJACENCY half of the detector's new predicate agrees flag-for-flag with the I-6 classifier's `distance == 1` reading in `eval/evidence_honesty.py` over the committed bytes (148 of 234 pooled), and pins the tick half as the KNOWN, enumerated difference — the registered `adjacent` cell's gap term measures ticks OUTSIDE the alibi window (always 0 on a minted flag, which is why `adjacent` and `adjacent_any_gap` both read 148), whereas `MAP_ARBITRATION_MAX_TICK_GAP` measures distance to the nearest window ENDPOINT, so 8 adjacent flags sit ≥ 2 ticks inside their window and are deliberately NOT demoted. A disagreement outside that enumerated set of 8 fails loud instead of letting the gauge and the mechanism measure two different rules.
- [ ] `meetings/` remains engine-free: `uv run lint-imports` passes and a grep of `meetings/` for `engine` returns only the data-not-an-import comments; `meetings/constants.py` gains no import.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — read the read-site before touching it. `_detect_alibi_vs_sightings`
(meetings/transcript.py:2836-2961) already pairs only when the sighting's canonical rooms are
non-empty and disjoint from the alibi's and the sighting tick is inside the alibi window, so
the new predicate runs on a pair that is already comparable and already contradictory by room.
The only thing it decides is the band.

Step 2 — the predicate. Adjacency is `min` hop distance over the cross product of the two
canonical room sets, and the sets are disjoint by construction, so "one doorway apart" is
simply: some room in one set is a member of some room's neighbour tuple in the other. The tick
side is `min(abs(t - from_tick), abs(t - to_tick)) <= MAP_ARBITRATION_MAX_TICK_GAP`. For the
single-tick windows that carry 79.9% of the class this is 0; for an endpoint sighting on a
multi-tick window it is also 0 and the pair is already weak, so the reason simply joins the
existing marker; for a sighting buried deeper it is 2 or more and nothing moves. Keep both
knobs named (`MAP_ARBITRATION_MAX_HOPS`, `MAP_ARBITRATION_MAX_TICK_GAP`) rather than writing
`1` twice — the counterfactual has to be able to say what it varied.

Step 3 — the weak reason is user-facing text. It renders into turn and ballot prompts, so the
literal is plain English ("adjacent rooms within one tick"), never a snake_case token and never
a task or audit id — the craft rule about dialect on rendered surfaces applies to this string.
Append it in one fixed position in the reason order so the joined marker stays byte-stable.

Step 4 — the neighbour table goes directly beside `CANONICAL_ROOMS` and inherits its comment's
logic: it is DATA, the duplication is deliberate, and the pin is what makes it safe. Do not
reach for `observation.public_map.PublicMapView` here: nothing under `meetings/` receives one
today (a grep for `public_map` under `meetings/` returns nothing at HEAD), and threading one in
would mean editing the manager and the orchestrator for a rule that needs ten rooms and eleven
edges of frozen topology.

Step 5 — the counterfactual is a read, not a new instrument. The I-6 cell is already owned by
`eval/evidence_honesty.py`; run it over the four sets with the lever OFF and ON and pin both
legs. Reuse the cached committed-bytes walk rather than adding a second one, and quote the
per-set numerators in the PR — bar 7 is judged pooled but a set that moves the wrong way is
the finding, not a rounding error.

Step 6 — if the ON leg lands above the bar's 5%, report the residue and its shape (which
window widths and which hop distances survive) under Decisions. A re-derivation of the committed
bytes against this exact predicate already predicts the miss: 140 of the 148 adjacent STRONG
flags demote, leaving 8 adjacent on a 94-flag STRONG denominator = 8.5% pooled — all 8 in
ml_corpus/9p2i, at endpoint gaps 2-4 inside windows 4-10 ticks wide.
Do not widen the rule to reach
a number: the pre-registration says a miss is reported as a miss, and the offline counterfactual
exists precisely so the owner sees this before the record.

**Public types introduced:**
- `meetings.transcript.map_aware_arbitration_enabled`
- `meetings.transcript.ENV_MAP_AWARE_ARBITRATION`
- `meetings.transcript.CANONICAL_ROOM_NEIGHBORS`
- `meetings.transcript.WEAK_REASON_ADJACENT_ONE_TICK`
- `meetings.constants.MAP_ARBITRATION_MAX_HOPS`
- `meetings.constants.MAP_ARBITRATION_MAX_TICK_GAP`

**Ready-to-paste prompt:** `agent_prompts/task-20-27-map-aware-arbitration.md`

### Task 20.28 — Dev markers leave spoken text: structured turn annotations, chips in the spectator
**Branch:** `phase-20-structured-turn-markers`
**Depends on:** 20.16 (the spectator DTO pass settles the view-model contract and regenerates the same TypeScript type files this task extends, so the generated-types diff stays one change per PR), 20.25 (the additive movement-claim shape lands in the turn schema first, so the annotations field is added to a settled turn model rather than racing it), 20.26 (the grounded-prosecution wiring edits the same manager call-site region and the same manager test module, so it merges ahead)
**Section refs:** G-25 (audits/review-2026-08-19/A/verdicts.md verdict 11 — turn half CONFIRMED-BUG, ballot half CONFIRMED-DESIGN-CHOICE; audits/review-2026-08-19/A/collated-findings.md §D "G-25 — Dev audit markers leak into `free_text`") + C-67 (audits/review-2026-08-19/B/collated-findings.md §4 row C-67; audits/review-2026-08-19/B/meetings-manager.md §P2-9); roadmap item audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.8, audits/review-2026-08-19/D/synth-credibility.md §4 row 9, audits/review-2026-08-19/D/cross-track-map.md §2.2 G-25 row; meetings/manager.py:382-384, :403-408, :479-481, :516-518 (the five turn-side marker literals), :1595-1597 + :1648-1652 (the two splice sites, both inside `MeetingManager._collect_turn` at :1353), :3937-3940 (the contract the splice breaks), :3910-3981 (`_drop_non_roster_claims`, the markers built in its loop at :3958-3966); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:136 + :154, accusation_round_roll_call.j2:133 + :151, vote_ballot.j2:91 (the five unfiltered `turn.free_text` renders); api/replay_loader.py:2528-2550 (`_turn_view` and today's one-off emergency-strip), :2856-2863 (`_BALLOT_PREFIX_MARKERS`), :2874-2882 (`_MARKER_REPR_VALUE` / `_marker_pattern`), :2893-2923 (`_parse_rewrite_reasons`); api/schemas.py:627-657 (`TurnView`), :840-876 (`BallotView`, the chip precedent); meetings/schemas.py:358-383 (`MeetingTurn`); DESIGN.md:595-597 (the ballot-marker sanction); audits/audit-2026-06-11-2218-gameplay-data.md:38 (H-H-4, the "Frankenstein turn record" that bounded the quote and left the visibility); tasks/phase-18.md 18.9 (the default-OFF lever shape with committed-bytes counterfactuals)
**Complexity:** Small
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/meetings/test_manager.py tests/api -q` green; the committed-bytes census pin reads marker-bearing turns 53/971 and contaminated prompts 246/1956 over samples/9p2i with zero raw marker substrings surviving into any served `TurnView.free_text`; with `AILIBI_STRUCTURED_TURN_MARKERS=1` a fresh fake-provider 9p2i tournament records 0 marker-bearing turns and 0 contaminated prompts (I-8, `eval/evidence_honesty.py`'s marker-contamination cell, reads 0); with the lever OFF `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` and `bash scripts/verify_samples.sh` stay green

Editor-console text is sitting inside quoted dialogue in one prompt in eight. The manager's
per-turn roster guard drops a claim naming a non-living participant and prepends an audit
marker to the turn's `free_text` (`meetings/manager.py:1595-1597`, the marker built at
:3961-3965 from the constant at :382-384); every later speaker's prompt then renders that
string verbatim inside the transcript block — `accusation_round.j2:136` and
`accusation_round_roll_call.j2:133` both emit `said: "{{ turn.free_text }}"`, and
`vote_ballot.j2:91` repeats it into the vote prompt. Re-verified by me at HEAD over the
committed baseline-6 bytes, exactly reproducing the review's census: marker-bearing turns
53/971 in samples/9p2i and 139/2726 in ml_corpus/9p2i (0/117 and 0/120 in the two 4p1i sets
— one-impostor games rarely produce dead-target accusations), and prompts carrying a marker
246/1956 and 671/5502, i.e. 33/165 and 91/463 meetings across 25/50 and 68/150 games. The
kind split is narrow: 53 invalid-accusation-target in samples/9p2i, 137 of the same plus 2
invalid-corroboration-supports in ml_corpus/9p2i, and zero instances of the emergency-strip
or opening-degrade markers anywhere in the committed corpus.

The function's own docstring is the contract this breaks. `meetings/manager.py:3937-3940`
promises that "a dropped claim never reaches the transcript, contradiction detection, the
post-meeting belief fold, or any prompt surface" — and the *claim* does not; the *marker*
does. The 2026-06-11 gameplay audit already called a spliced marker "a Frankenstein turn
record" (audits/audit-2026-06-11-2218-gameplay-data.md:38) and fixed only the 60-char quote
bound, never the visibility. The review's own reading of the harm is that the token lands
immediately before the sentence that usually names a vent sighting — an unexplained
editor-console string injected into the deliberation context at the highest-leverage moment,
and read verbatim by any spectator watching the transcript.

This task stops the splice behind an env lever and gives turns the structured treatment
ballots have had since Task 17.3. Recording side, default-OFF: with
`AILIBI_STRUCTURED_TURN_MARKERS` set, `_collect_turn` records each dropped claim as a typed
`TurnAnnotation` on the turn instead of prepending a string, and `free_text` is exactly what
the model authored. Reading side, unconditional: `api/replay_loader._turn_view` projects
BOTH shapes — the legacy spliced markers already frozen into the committed bytes and the new
structured field — onto one chip vocabulary, using the imported constants and the existing
repr-aware `_marker_pattern` rather than a second regex, so the spectator half ships now with
no re-record (audits/review-2026-08-19/D/synth-credibility.md §4 row 9 asks for exactly this
split). That read-side change is the one deliberate exception to OFF-path identity: recorded
bytes and rendered prompts stay byte-identical with the lever OFF, but the SERVED transcript
stops printing dev jargon immediately, the same way `fabricated_opening` already lifts the
emergency-strip marker out of `free_text` into a role-neutral chip
(`api/replay_loader.py:2528-2550`).

Scope discipline, both halves. The ballot markers are NOT touched: the review verified they
reach 0/7458 prompts (ballots are post-meeting) and `DESIGN.md:597` explicitly sanctions "an
audit marker in `rationale_text`" — that half is a design choice with no model-facing effect,
and the spectator already strips it into labelled chips. And the four other packages C-67
names as marker consumers keep working unchanged on committed bytes: `eval/vj_instruments.py`
strips leading `[...]` spans before its voice folds (:653-660, tolerant of absence by
construction), and the offline `audits/workflows/extract_gameplay_facts.py` counts marker
substrings on recorded `free_text` (:1264-1265) — a count that reads 0 for ON-path recordings
and is re-pointed at the structured field with the adopting record, not here.

**Files in scope:**
- meetings/manager.py; (the lever: the validator records dropped/invalid claims in a structured `annotations` field on the turn instead of splicing into free_text; OFF-path bytes identical)
- meetings/schemas.py; (the additive `MeetingTurn.annotations` field)
- api/replay_loader.py; (turn annotations → the same chip projection ballots already get; legacy spliced markers in committed bytes still parsed into chips)
- api/schemas.py; (TurnView.annotations)
- frontend/src/components/TurnCard.tsx; (render the chips)
- frontend/src/types/api.ts; (regenerated)
- api.fidelity.ts; (same)
- tests/meetings/test_manager.py; (OFF byte-identity; ON: free_text carries no marker; the annotation carries the dropped claim)
- tests/api/test_replay_loader.py; (legacy marker → chip; new annotation → chip)
- frontend/src/stories/MeetingView.stories.tsx; (the TurnView literal gains the annotations field)
- frontend/src/stories/MindInspector.stories.tsx; (same)

Recorded deviations at merge (PR #380, orchestrator-ratified per the #377 precedent): four files outside scope, all forced by the SawMoveObservationView DoD item widening ObservationClaimView — frontend/src/ui/ObservationLine.tsx and frontend/src/components/MemoryPanel.tsx (exhaustive TS switches), scripts/gen_frontend_types.py (union/enum alias lists), tests/api/test_leak.py (EXPECTED_DTOS + two EXPECTED_EVAL_REPORT_FIELDS names; FORBIDDEN_EVAL_ENGINE_FIELDS untouched). Ruling implemented as shipped: MeetingTurn stays the single wire shape with `annotations` an optional system-authored field stripped at the parse boundary (no AuthoredTurn type exists); MARKER_QUOTED_ORIGINAL_MAX_CHARS moved to meetings/schemas.py with re-exports, MARKER_TRUNCATION_SUFFIX beside it. A prose record, not scope entries.

**Files NOT in scope:**
- agents/strategic/prompts/ (the transcript block renders free_text; with the lever ON the free_text is clean so no template change is needed — and the single prompt-set bump of this phase is another task's, no template byte moves here)
- the ballot marker path (sanctioned by DESIGN.md:595-597, spectator-stripped, 0/7458 prompts — the four ballot-side constants and `_BALLOT_PREFIX_MARKERS` are imported, never edited)
- orchestrator/replay.py (registering this lever into `_TOGGLEABLE_LEVER_RESOLVERS` and the substrate stamp is Task 20.33's, which does it for every Phase-20 lever at once, before any ON-path seed records)
- audits/workflows/extract_gameplay_facts.py (an offline audit tool whose drop-marker count reads committed bytes today; its re-point at the structured field rides the adopting record)
- eval/vj_instruments.py + eval/meeting_quality.py + training/surrogate/dataset.py (marker consumers that already tolerate absence; read as evidence, never edited)
- eval/evidence_honesty.py (a FOURTH marker consumer, landed by 20.15 after this contract was authored: its I-8 cells derive their marker set from the three `_drop_non_roster_claims` constants and are ratified at audits/audit-phase-20-preregistration.md:169-170; this task READS those cells and must not redefine or re-implement one — if a needed split is missing, say so in the PR)

**Definition of done:**
- [ ] `structured_turn_markers_enabled` follows the 13.5 signature (optional `env` mapping, default OFF, accepting `1/true/yes/on`), is read ONCE per turn collection and threaded down, and with the lever OFF `MeetingManager._collect_turn` prepends the identical marker string in BOTH its branches (the normal path and the degraded-opening path) — pinned in `tests/meetings/test_manager.py`, plus a committed-line re-serialization pin in `tests/api/test_replay_loader.py` showing a recorded meeting entry round-trips byte-identically (the empty `annotations` tuple is elided from the serialized turn, so newly recorded bytes do not gain a key on the OFF path).
- [ ] Lever ON: a manager test plants EACH of the five turn-side marker constants' trigger conditions and asserts none of the five literals survives into `free_text`, into the rendered transcript block, or into any recorded prompt; each dropped claim is recoverable from `MeetingTurn.annotations` in claim order with its bounded original (the `MARKER_QUOTED_ORIGINAL_MAX_CHARS` bound still applied), and a perturbation shows the assertion bites when a marker is re-spliced.
- [ ] OFF-path identity holds at the gates: `tests/meetings/test_prompt_byte_golden.py` and `bash scripts/verify_samples.sh` stay green, and no prompt template byte moves in this PR.
- [ ] `api/replay_loader._turn_view` projects BOTH shapes to one chip vocabulary via the IMPORTED constants and the existing `_marker_pattern` (no second regex, no hard-coded literal): a committed replay's legacy spliced markers become `TurnView.annotations` labels with `free_text` cleaned, a recorded structured annotation becomes the same label, and `fabricated_opening` is derived from either shape — all three pinned in `tests/api/test_replay_loader.py`.
- [ ] The committed-bytes counterfactual is pinned over the two samples sets and quoted for all four in the PR (the four rate cells are ALREADY pinned by `tests/eval/test_evidence_honesty.py::test_i8_marker_contamination_pins` — cite that test rather than duplicating it; only the kind split is new here): marker-bearing turns 53/971 and contaminated prompts 246/1956 for samples/9p2i (33/165 meetings, 25/50 games), 0/117 and 0/234 for samples/4p1i, 139/2726 and 671/5502 for ml_corpus/9p2i (91/463 meetings, 68/150 games), 0/120 and 0/240 for ml_corpus/4p1i, with the kind split (53 invalid-accusation-target; 137 plus 2 invalid-corroboration-supports; zero emergency-strip and zero opening-degrade markers corpus-wide) and the stated would-be effect — every one of those turns carries a structured annotation instead, and the contaminated-prompt cell reads 0 at the adopting record.
- [ ] `TurnCard` renders the annotation labels as ink/paper chips beside the existing FABRICATED chip, in every perspective, with a one-line comment recording why no turn-annotation label carries role information (unlike the ballot side's `teammate_coerced` gate); the regenerated types are committed and `uv run python scripts/gen_frontend_types.py --check` passes.
- [ ] The spectator mirror of the movement shape exists: api/replay_loader.py::_observation_claim_view maps SawMoveObservation to a SawMoveObservationView (api/schemas.py + the generated types), pinned — the first recorded saw_move turn must not break the viewer before the record.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — the resolver. Clone `agents.strategic.prompts.loader.impostor_roll_call_enabled`
(:327-363) verbatim in shape: a module-level `ENV_STRUCTURED_TURN_MARKERS` constant, a frozen
true-value set, `env if env is not None else os.environ`. Its home is `meetings/manager.py`
because that is where the single write-site lives. Do NOT register it in
`orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS` — say so in a comment the way
`ENV_IMPOSTOR_ROLL_CALL` does at loader.py:316-320, naming the registration task.

Step 2 — the five literals, both branches. The turn-side markers are
`INVALID_ACCUSATION_TARGET_MARKER`, `INVALID_ALIBI_SUBJECT_MARKER`,
`INVALID_CORROBORATION_SUPPORTS_MARKER` (built in `_drop_non_roster_claims`),
`EMERGENCY_BODY_STRIP_MARKER` (prepended to `drop_markers` at :1559) and
`OPENING_UNSURE_DEGRADE_MARKER` (:1649). They are consumed at TWO places in `_collect_turn`
— the normal return at :1595-1597 and the degraded-opening return at :1648-1652 — so the
lever branch must cover both or the degraded path keeps splicing. Keep every constant exactly
where it is: they stay the definition of what each guard did, and the annotation `kind`
values are the labels derived from them.

Step 3 — the schema. `TurnAnnotation` is a frozen model with a `kind` literal and the bounded
`original` (`None` for the two kinds that quote nothing), and `MeetingTurn.annotations`
defaults to `()`. The replay writer serializes via `model_dump(mode="json")`
(`orchestrator/replay.py:1234-1240`), which emits defaults, so an empty tuple would add a key
to every future recording; a model serializer on `MeetingTurn` that drops the key when the
tuple is empty is what makes the OFF path byte-identical — pin it, do not assume it.

Step 4 — the projection. `_BALLOT_PREFIX_MARKERS` (:2856-2863) and `_parse_rewrite_reasons`
(:2893-2923) are the shape to mirror: a `(label, marker)` registry built from imported
constants, patterns precompiled through `_marker_pattern`, stripped front-to-back so stacked
markers all surface. Reuse `_marker_pattern` rather than writing a second regex — C-67's
complaint is precisely that the `{x!r}` repr shape and the `]` terminator are re-implemented
per package. On the API side project labels only: the raw hallucinated value is dev jargon
and stays off the spectator surface, exactly as the emergency-strip marker already does.

Step 5 — blast radius before you touch the DTO. `grep -rn "fabricated_opening" frontend/src`
first: `frontend/src/stories/MeetingView.stories.tsx:72` and
`frontend/src/stories/MindInspector.stories.tsx:70` construct whole `TurnView` object
literals, the generator emits every field as REQUIRED in TypeScript, and `tsconfig.json`
includes `src` — so both fixtures need the new field or `npm run tsc:check` and `npm run
build` fail inside `scripts/check.sh`. `VIEW_MODEL_VERSION` does NOT move: the header at
api/schemas.py:42-54 says additive projections do not bump it (it now reads "2" — 20.16 bumped it for the widened `CurrentAction`; this task's additive field does not move it again).

Step 6 — the census. Do NOT re-implement the four rate cells: Task 20.15 landed them as
`eval/evidence_honesty.py`'s I-8 marker-contamination cells (marker set derived from the
manager constants, so a constant edit moves the cell rather than leaving it silently stale),
and `tests/eval/test_evidence_honesty.py::test_i8_marker_contamination_pins` already pins
turns, prompts, meetings and games across all four sets at exactly the numbers quoted above —
read and cite those. Only the per-kind split is not an I-8 cell; derive that one locally, mark
it `slow` (the two ml_corpus sets are the slow half) and quote it in the PR.

**Public types introduced:**
- `meetings.manager.structured_turn_markers_enabled`
- `meetings.schemas.TurnAnnotation`
- `meetings.schemas.TurnAnnotationKind`

**Ready-to-paste prompt:** `agent_prompts/task-20-28-structured-turn-markers.md`

### Task 20.29 — Meetings leave a record: outcomes, revealed roles and testimony as content in memory
**Branch:** `phase-20-meeting-outcome-memory`
**Depends on:** 20.24 — the self-location trail lands its own non-elastic block in the same render assembly first, so this block stacks on a settled layout instead of racing it; 20.8 — the entitlement-checking leak scanner must exist before this task widens it with a role-disclosure allowance, or the allowance is written against a scanner that cannot check entitlement at all; 20.28 — the structured turn annotations settle the manager's public reduction surface before an additive outcome payload is added beside it.
**Section refs:** G-35 and G-23 (audits/review-2026-08-19/A/collated-findings.md §G-35, §G-23); R4 and R5 and D5 (audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §R4, §R5, §D5); V1 and M1 (audits/review-2026-08-19/A/ideas-among-us-veteran.md §V1, §1 row M1); idea #9 (audits/review-2026-08-19/A/ideas-game-designer.md §9); audits/review-2026-08-19/A/s4-info-economy-beliefs.md §3; the roadmap item audits/review-2026-08-19/D/FINAL-synthesis.md §Wave 2 row 2.10. Re-verified at HEAD 1ceab2c4: agents/memory/working.py:57-73 (`MeetingOutcome`, exactly `end_tick` + `ejected_id`), :133-185 (`MeetingHistory`, `record` at :176); agents/memory/store.py:685-711 (`record_meeting_outcome`, "inert to `render_for_prompt` … no prompt-byte impact anywhere"), :579-682 (`absorb_reported_testimony`), :1750-1804 (`_render_reported_testimony`, the `CLAIM by X (unverified):` prefix at :1777, `accused {subject}` at :1792), :86 (`_SALIENCE_REPORTED_TESTIMONY = 25`), :2070-2163 (`_assemble_view`, the fixed/elastic split); orchestrator/game.py:674-715 (the `MeetingPacingAgent` protocol), :2020-2035 (the belief fold then the pacing fold), :2328-2345 (the testimony fan-out), :2392-2432 (`_notify_meeting_concluded`), :3188-3228 (`TacticalAgent.note_meeting_concluded`); meetings/manager.py:3597 (`MeetingBeliefEvidence`, the sibling reduction DTO), :3913-4004 (`derive_reported_testimony`); meetings/schemas.py:537-539 (`ReportedStatementKind`, the closed four), :95-119 (`SawVentObservation`, ":112-113 deliberately NOT reduced to a `ReportedStatement`"), :721 (`MeetingResult.ejected_player_id`); eval/leak_scan.py:68-80 (the forbidden role-value constants and their single allowed path), :185-210 (`_assert_no_role_bearing_values`), :848-920 (`assert_packet_is_leak_clean`, whose signature 20.8 changed to `(packet, context: PacketContext)`); tests/agents/test_memory_meeting_history.py:249-260 (the field-set provenance pin), :301-308 (the render-inertness pin); DESIGN.md:463 §4.7, :702 §6.6; .importlinter (agents must not import engine, agents must not import meetings.manager)
**Complexity:** Integration
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/agents tests/orchestrator tests/observation eval/leak_test.py -q` green; a fake-provider 9p2i game with `AILIBI_MEETING_OUTCOME_MEMORY=1` renders the meetings block in every living agent's memory after its first meeting, pasted into the PR Summary alongside the committed-bytes counterfactual census.

Nothing survives a meeting. Across the 300 committed baseline-6 games the review grepped every
rendered memory for any trace of an ejection outcome — "ejected", "voted out", "was not",
"remain" — and found 0 of 3,934, including the 1,799 that were rendered *after* an ejection had
already happened (A/ideas-among-us-veteran.md §1 row M1, all four sets, VERIFIED); the same
census over the prompt bytes reads 0 of 7,458 meeting LLM calls carrying any record of a prior
ejection or its revealed role (A/ideas-multi-agent-researcher.md §D5). This is not a missing
channel — the channel was built and left inert. `MeetingOutcome` at
agents/memory/working.py:57-73 already carries the concluded meeting's public result,
`record_meeting_outcome` at agents/memory/store.py:685-711 already folds it per living agent
off the `note_meeting_concluded` hook, and its own docstring states the terminal fact: it "is
consumed ONLY by the v3 tactical feature encoder's meeting-history channel and is inert to
`render_for_prompt` … it carries no prompt-byte impact anywhere". Three survived meetings
currently reach the model as three floats in a feature vector no LLM ever reads.

The cost is measured, and it is the corpus's least watchable behaviour. With no record that a
case is closed, the crew re-prosecutes corpses: 68 `saw_vent` observations in samples/9p2i and
232 in ml/9p2i name a player already dead or ejected, and 5.0–5.5% of all turns have their
accusation struck for naming an out-of-game player (A/collated-findings.md §G-23). Seed 2
spends meeting 2 *and* meeting 3 re-arguing p-4, ejected at meeting 1; seeds 13 and 15 spend
their last three-alive meeting entirely on an already-ejected impostor; in seed 6 the crew end
up branding their own two vent witnesses liars (A/ideas-among-us-veteran.md §V1;
A/ideas-game-designer.md §9). In the real game "X was not the Impostor. 1 Impostor remains." is
the sentence the whole mid- and endgame is built on: without it there is no cleared player, no
parity count, and no reason for a skip to feel expensive.

The second half is the testimony content. `_render_reported_testimony`
(agents/memory/store.py:1750-1804) reduces an accusation to `accused {subject}` at :1792, and
`SawVentObservation` is deliberately excluded from the reduction altogether —
meetings/schemas.py:112-113 says so in as many words, because the Task 13.5.2 scope was
owner-locked to four kinds. The consequence is exactly inverted from the design intent: the
game's one 100%-precise signal is destroyed on the way into memory (a witnessed vent becomes
`CLAIM by p-8 (unverified): accused p-4`) while the impostor's fabricated *sighting* keeps its
room and its tick. Testimony is 16.8–17.2% of all rendered lines, and its only mechanical
effect on belief is a flat asserted-alibi discount that is *larger* for the liar — −0.086 for
an impostor subject against −0.038 for a crew subject in corpus9p2i
(A/s4-info-economy-beliefs.md §3). Restoring the vent's content costs one statement kind and
one render branch.

The disclosure is deliberate and it is narrow. Confirm-ejects is the Among Us rule, and the
revealed role of an EJECTED player is public at the table on exactly the same footing as
`dead_ids` and the announced tally — the footing on which `ejected_id` already crosses into
memory (DESIGN.md §4.7; the 18.22 argument recorded at orchestrator/game.py:2392-2414). A
player killed rather than ejected reveals nothing, and no living player's role is ever
disclosed. Because `agents/` may not import `engine` (.importlinter), the translation happens
where it already belongs: the orchestrator, which holds post-meeting `WorldState`, reads the
ejected player's role and passes it through the existing hook; the manager contributes only the
public tally, derived from the recorded ballots the way `derive_reported_testimony` and
`extract_belief_evidence` already derive their reductions. That split is what makes the
allowance auditable rather than a hole, and 20.8's entitlement-checking scanner is extended to
assert it in both directions.

Everything ships behind `AILIBI_MEETING_OUTCOME_MEMORY`, default OFF: OFF-path render bytes are
byte-identical over all 300 committed games, so `tests/meetings/test_prompt_byte_golden.py` and
`bash scripts/verify_samples.sh` stay green and the Phase-20 gate slate is undisturbed until
the adopting record flips it. The honest price is quoted in advance from the committed bytes
rather than promised: how many renders would gain a prior-ejection line, how many of those
would tell the crew it had ejected a crewmate, and how many `saw_vent` rows name a player the
block would already have closed out.

**Files in scope:**
- agents/memory/store.py; (the lever, its resolver and its env key: a non-elastic `## Meetings so far:` block rendered above observations — `Meeting 1 (tick 14): p-4 EJECTED 7-1 — p-4 was an IMPOSTOR. 1 impostor remains.` / `Meeting 2 (tick 27): no ejection (6 skip). 1 impostor remains.` — plus reported testimony kept as CONTENT with its speaker, its meeting index and the restored vent body; OFF-path bytes identical)
- agents/memory/working.py; (`MeetingOutcome` gains optional revealed-role and tally fields, all defaulting to None so every existing construction and the v3 three-scalar channel are untouched; `impostors_remaining` derived on `MeetingHistory`, engine-free and pure-Python as the module's own import pin requires)
- orchestrator/game.py; (after `apply_meeting_result`, `_notify_meeting_concluded` passes the ejected player's role read off the post-meeting state plus the public tally and the roster impostor count into the memory fold — the orchestrator is the only module allowed to translate engine roles; the `MeetingPacingAgent` protocol and `TacticalAgent.note_meeting_concluded` widen additively with None defaults)
- meetings/manager.py; (the additive public outcome payload the orchestrator hands to the fold: a pure, engine-free tally reduction over the recorded ballots, the sibling of `derive_reported_testimony`; plus the reduction of a spoken vent sighting into reported testimony)
- eval/leak_scan.py; (a memory-render scanner with one explicit, named allowance: a role word may name an EJECTED player only in a render taken at or after that player's ejection tick, and the agent's own `## Your role:` line; every other role disclosure fails)
- tests/agents/test_memory_meeting_history.py; (OFF byte-identity; ON: the block renders, the impostors-remaining arithmetic, a role never appears before its ejection tick, and the restated field-set provenance pin)
- tests/agents/test_reported_testimony.py; (the content lines: the vent body survives, the speaker and meeting index render, the OFF path is byte-identical)
- tests/orchestrator/test_meeting_integration.py; (the payload: the hook carries the revealed role and the tally end to end, and carries nothing for a kill victim)
- eval/leak_test.py; (the planted-leak legs: a pre-ejection role disclosure FAILS the scanner)
- tests/observation/test_leak_property.py; (the other direction: with the lever ON the observation packets are unchanged — the disclosure never travels through perception)
- meetings/schemas.py; (a ReportedStatementKind member for the spoken vent; the SawVentObservation docstring correction)

Recorded deviation at merge (PR #381, orchestrator-ratified): four files outside scope forward the widened note_meeting_concluded keywords verbatim — training/env.py:466, training/crew/scorer.py:814, agents/tactical/learned/factory.py:293 + :388, tests/training/test_learned_factory_acceptance.py:769 — because runtime_checkable capability gates check attribute presence, not signature, so the wrapper implementations had to accept what the orchestrator now passes. A prose record, not scope entries.

**Files NOT in scope:**
- engine/ (no engine change — the orchestrator already holds the post-meeting state and its roles)
- agents/strategic/prompts/ (no template may move in this task; the dead-subject exemption to the speak-your-vent-first mandate is the prompt-set bump's, and it is the only task in the phase permitted to touch a `.j2`)
- agents/tactical/ (the FSM's dead-set fold is the impostor-mover task)
- orchestrator/replay.py (the substrate stamp registration is Task 20.33 — this task ships the resolver and the env key and registers nothing; a bare-environment snapshot is unchanged here by construction)
- agents/tactical/features.py and tests/training/test_bakeoff_harness.py (the v3 `meeting_history_scalars` channel stays exactly three floats — the widened dataclass must not move a single feature byte, which is a DoD assertion, not an edit)
- api/replay_loader.py and tests/meetings/test_prompt_byte_golden.py (both reconstruct memories without the outcome fold; under the default OFF lever their bytes cannot move, and ON-path reconstruction parity is carried by the stamp registration and the adopting record — see Integration risk)
- the belief-line alibi suffix and `record_alibi` de-duplication (register id C-3 class, a separate P2 living in the same file; touching it here would move OFF-path belief bytes)
- DESIGN.md (§6.6's prose stays true while the lever is OFF; the adopting record's sweep restates it)

**Definition of done:**
- [ ] `agents.memory.store.meeting_outcome_memory_enabled(env)` reads `AILIBI_MEETING_OUTCOME_MEMORY`, accepts `1/true/yes/on` case-insensitively, defaults False on unset/empty/unrecognised, and takes `env` so tests toggle without mutating `os.environ` — mirroring the resolver at agents/strategic/prompts/loader.py:327 (and the in-file sibling 20.24 landed, `self_location_trail_enabled` at agents/memory/store.py:290). `render_for_prompt` reads it once and threads the boolean down.
- [ ] OFF-path byte-identity: `tests/agents/test_memory_meeting_history.py` pins that a memory populated with outcomes carrying roles and tallies renders byte-identically to the same memory without them, and `bash scripts/verify_samples.sh` plus `uv run pytest tests/meetings/test_prompt_byte_golden.py` stay green over all 300 committed games.
- [ ] ON-path render: every post-meeting render carries the `## Meetings so far:` block as a non-elastic block placed above the observations block, one line per concluded meeting, naming the meeting index, the resume tick, the ejection or the skip with its tally, the revealed role of the ejected player, and the impostors-remaining count — pinned line-for-line in `tests/agents/test_memory_meeting_history.py` for an eject-an-impostor, an eject-a-crewmate and a skip.
- [ ] The impostors-remaining arithmetic is derived, not asserted: it equals the roster impostor count minus the number of recorded outcomes whose revealed role is IMPOSTOR, is never decremented by a kill, and is pinned across a two-impostor game where the first ejection is wrong and the second is right.
- [ ] ON-path testimony content: a spoken vent sighting reaches memory as content — `[tick 15] [meeting 1] CLAIM by p-8 (unverified): saw p-4 VENT in ENGINEERING @ tick 11.` — with the load-bearing `CLAIM by X (unverified):` frame preserved verbatim, and every reported line names the meeting it was spoken at; pinned in `tests/agents/test_reported_testimony.py`, with the OFF path byte-identical to HEAD in the same file.
- [ ] The widened `MeetingOutcome` field set is re-pinned as a provenance assertion, not merely updated: `tests/agents/test_memory_meeting_history.py`'s field-set test states the new exact tuple and asserts each added field is a fact announced at the table, and `tests/agents/test_memory_meeting_history.py`'s working-module import pin still shows no `engine`, numpy or torch import.
- [ ] The v3 encoder is untouched: `TacticalFeatureEncoder.encode` over a memory whose outcomes carry roles and tallies is byte-identical to the same memory without them, and the `meeting_history_scalars` segment is still three floats — asserted in `tests/agents/test_memory_meeting_history.py`.
- [ ] The orchestrator payload: `tests/orchestrator/test_meeting_integration.py` drives a real meeting to an ejection and asserts every living agent's memory holds the ejected player's true role and the true tally, that a player killed rather than ejected contributes no role anywhere in any agent's memory, and that an agent that died before the meeting receives nothing.
- [ ] The leak allowance is narrow and asserted in both directions: `eval/leak_scan.py`'s memory-render scanner passes a render taken after an ejection that names the ejected player's role, and FAILS on the same disclosure taken before the ejection tick, on a living player's role, and on a kill victim's role — the failing legs planted in `eval/leak_test.py`, and `tests/observation/test_leak_property.py` asserting that turning the lever ON changes no observation packet byte.
- [ ] The §6.6 render contract in `render_for_prompt`'s docstring documents the block: its position in the non-elastic set, its line grammar, and the entitlement rule that makes the role disclosure legal.
- [ ] The committed-bytes counterfactual is pinned and quoted in the PR Summary: over all four committed sets, the count of rendered memories that would now carry at least one prior-ejection line (review-measured 1,799 of 3,934 over the committed baseline-6 bytes; re-derived per set here), that count split by whether the revealed role is IMPOSTOR or CREWMATE, and the count of `saw_vent` observations naming an already-ejected player (review-measured 68 in samples/9p2i and 232 in ml/9p2i) as the re-litigation denominator the record is judged against.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Illustrative, not exhaustive — the anchors are re-verified at HEAD, the shapes are yours to
settle.

Step 1 — blast-radius grep before anything moves. `record_meeting_outcome`, `MeetingOutcome`
and `meeting_history` reach agents/memory/working.py, agents/memory/store.py,
agents/tactical/features.py, orchestrator/game.py, tests/agents/test_memory_meeting_history.py
and tests/training/test_bakeoff_harness.py; the `note_meeting_concluded` hook additionally has
protocol fakes in tests/training/test_crew_scorer.py,
tests/training/test_learned_factory_acceptance.py and tests/training/test_surrogate_runner.py,
which is why the widened parameters must be keyword-only with None defaults. Note that
`meetings.schemas.MeetingOutcome` is a DIFFERENT symbol (a `Literal["EJECTED", "SKIPPED"]`
alias at meetings/schemas.py:674) imported by meetings/voting.py, meetings/manager.py,
training/rollout.py and training/surrogate/dataset.py — do not widen that one.

Step 2 — the payload, orchestrator-side. `_notify_meeting_concluded` at
orchestrator/game.py:2392-2432 already holds the post-meeting `next_state`, so the ejected
player's role is one lookup away; the roster impostor count is `self._num_impostors`, held at
orchestrator/game.py:1634. Widen `MeetingPacingAgent.note_meeting_concluded` and
`TacticalAgent.note_meeting_concluded` with keyword-only additive parameters defaulting to
None, exactly as `ejected_id` was added at :708-715 — every existing direct caller keeps
working untouched and the capability gate is unchanged. Read the role from the post-meeting
state rather than from the meeting result: the result is engine-free by design and must stay
so.

Step 3 — the tally, manager-side. Add a pure reduction beside `derive_reported_testimony`
(meetings/manager.py:3913) that turns a recorded `MeetingResult` into the public tally — votes
for the ejected target and the skip count, over `result.ballots`, remembering `SKIP_TARGET` is
a first-class tally target (meetings/voting.py:145-215) and that a tie resolves to SKIPPED.
Keep it engine-free, deterministic and role-blind; the manager must never see a role.
`MeetingBeliefEvidence` at meetings/manager.py:3597 is the precedent for the DTO's home. The
orchestrator flattens it into the hook's keyword arguments so `agents/` never imports
`meetings.manager` (.importlinter forbids it).

Step 4 — the fold and the carrier. `agents/memory/working.py` is engine-free and its own test
pins that it imports no engine: type the revealed role as a local string literal alias in that
module, not `engine.entities.Role`. Give `MeetingHistory` the impostors-remaining derivation so
the arithmetic lives next to the data it reads; a kill never moves it.

Step 5 — the render. `_assemble_view` (agents/memory/store.py:2070-2163) is where the
elastic/non-elastic split lives: the meetings block joins `fixed_lines` and the
beliefs/contradictions blocks, NOT the salience-sorted observation list, so a tight budget can
never shed it. Keep it short — one line per concluded meeting; the coalescing task that follows
is what buys back the room, and this block must not be what makes the budget bind. The OFF path
must not merely produce equal bytes but take the same code path shape it takes today.

Step 6 — the testimony content. `SawVentObservation` is currently excluded from the reduction
on purpose (meetings/schemas.py:112-113); widening the reduction is the point of R5's half, and
the schema's own docstring is one of the false claims that must be corrected in the same PR.
Preserve the `CLAIM by X (unverified):` frame verbatim — agents/memory/store.py:1753-1757
documents it as load-bearing, and replacing the frame is a legibility decision this task is not
making. The meeting index is available at absorb time as the length of the agent's own
`meeting_history` (the fold order at orchestrator/game.py:2020-2035 is beliefs, then testimony,
then the outcome). R5's second half — a citable `[tst …]` id a later ballot can quote — is
deliberately NOT built here: minting new ids collides with the coalescing task's span ids and
the citation gate; leave `observation_id` as it is.

Step 7 — the scanner. The existing packet scanner's shape is the model: a frozen set of
forbidden role substrings with one named allowed path (eval/leak_scan.py:68-80, :185-226). The
render scanner is a pure function over the rendered string plus an ejection ledger of player id
to ejection tick plus the render tick; assert every role-bearing disclosure resolves to an
entitled one and fail loud with the offending line quoted. A gate that cannot fail is not a
gate — the planted legs in `eval/leak_test.py` are the proof, not the decoration.

Step 8 — the counterfactual. Roles are NOT in the replay JSONL (the leak firewall keeps them
out); re-derive them deterministically from the seeded setup via
`orchestrator.seeder.seed_initial_state`, the same route eval/balance_eval.py:612-643 takes on
its meeting-abort path. Walk the committed replays, count the renders that would gain a line
and the `saw_vent` rows naming an already-ejected subject, and pin the census in
`tests/agents/test_memory_meeting_history.py` behind the registered `slow` marker with the
session-scoped replay fixture in `tests/conftest.py`. Where a re-derived number differs from
the review's, state the cause in the pin's comment rather than moving the bar.

**Public types introduced:**
- `agents.memory.store.meeting_outcome_memory_enabled`
- `agents.memory.store.ENV_MEETING_OUTCOME_MEMORY`
- `meetings.manager.MeetingOutcomeSummary`
- `meetings.manager.derive_meeting_outcome_summary`
- `eval.leak_scan.assert_memory_render_role_disclosure_is_entitled`

**Integration risk:**

Role disclosure crosses the §4.7 firewall boundary by design, and that is the whole risk.
Confirm-ejects is the rule being implemented, but the allowance has to be exactly as wide as
the rule and no wider: ejected players only, only at or after their ejection tick, never a
living player and never a kill victim, whose role stays hidden precisely because nobody at the
table saw it. If the allowance is written as "roles may appear in memory renders" rather than
as an entitlement check, this lever converts the project's most-defended invariant into a hole,
and the scanner is the only thing standing between the two readings — which is why the failing
legs are a DoD item and not a nicety. Keep the translation in the orchestrator: the moment
`agents/` or `meetings/` learns to read a role, the import contracts stop being the argument.

Second risk, the token budget. The memory render is already 66% co-presence noise and sheds
prior-meeting testimony first under pressure (365 of 456 measured budget-pressure transitions
cut testimony while keeping the tick-0 spawn block at full size — A/collated-findings.md
§G-34), so a meetings block appended to the elastic observation list would be shed exactly in
the long games that need it. It must join the non-elastic set above observations, and it must
stay one line per meeting; the coalescing task that depends on this one is what frees the room,
and it inherits a block that is already small.

Third risk, reconstruction parity. Neither `api/replay_loader.py`'s memory walk nor the prompt
byte-golden's mirror of it folds meeting outcomes today, because the channel was inert. While
the lever is OFF that is invisible and their bytes cannot move; the day the adopting record
turns it ON, a served or re-golden'd memory that omits the block diverges from the recorded
prompt. Both files are out of scope here by dependency ordering, so the ON-path parity gap must
be stated explicitly in the PR description and handed forward to the stamp-registration and
record tasks rather than discovered during a 23-hour recording.

Fourth risk, the v3 encoder. `agents/tactical/features.py:678-700` reads
`memory.meeting_history` for three scalars and the bakeoff harness pins the segment width. The
widened dataclass must be additive with None defaults and the encoder must not learn to read
the new fields in this task; a single moved feature byte silently invalidates the shipped
champion comparison.

**Ready-to-paste prompt:** `agent_prompts/task-20-29-meeting-outcome-memory.md`

### Task 20.30 — The memory render earns its budget: coalesced spans, no spawn block, testimony survives
**Branch:** `phase-20-coalesced-memory-render`
**Depends on:** 20.29, 20.27, 20.19 — the meetings-outcome block and the testimony-as-content lines land in the same store module first, so this task coalesces and re-bands the FINAL line set instead of a superseded one; the map-aware arbitration lever writes its counterfactual cells into the shared evidence-honesty test module before this task adds the render-budget cells there; and the bisecting episodic scan lands in the episodic module first, so any span helper builds on the sorted-tick index rather than colliding with it.
**Section refs:** audits/review-2026-08-19/A/collated-findings.md §G-34 (P1, corrob 6); audits/review-2026-08-19/A/s4-info-economy-beliefs.md §1.2 (duplicate rows + the spawn block), §1.3 (memory is 32–38% of the prompt, 70.4% of it sightings + spawn), §1.4 (the budget cuts the social memory first), §10 design-hole D6; audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D7 + proposal R8; audits/review-2026-08-19/A/ideas-game-designer.md §0.4 (the seed-17 smoking gun) + idea #5; audits/review-2026-08-19/B/agents-memory.md §1 items 6 and 10 + §2 F2 (register id C-73); audits/review-2026-08-19/B/collated-findings.md C-73; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.11 (the enabler + its measurement); audits/review-2026-08-19/D/cross-track-map.md G-34 row; anchors re-verified at HEAD ee7634dc: agents/memory/store.py:47 (`DEFAULT_TOKEN_BUDGET = 1500`), :55-92 (the salience ladder; `_SALIENCE_REPORTED_TESTIMONY = 25` at :91 under the "load-bearing band invariant" comment at :85-90), :142-157 (`_Observation.observation_id`), :212-231 (the graduated `observation_id_rendering_enabled` resolver shape, hard-returning True at :231), :234-264 / :267-312 / :315-348 (the three DEFAULT-OFF resolver siblings that landed IN THIS FILE since this contract was authored — `task_completion_from_events_enabled` 20.23, `self_location_trail_enabled` 20.24, `meeting_outcome_memory_enabled` 20.29 — the in-file shape to copy), :505-518 (the lever reads inside `render_for_prompt`, `ids_on` at :510), :541-544 (the `(-salience, -tick, line)` sort), :953 (`_known_roster_ids`), :1213-1281 (`_collect_co_presence` keyed by `(tick, room)` + `_co_presence_suffix`), :1566-1794 (`_build_observations`), :1795-1866 (`_render_saw_player`), :1922-2000 (`_render_reported_testimony`, which since 20.29 takes a lever bool keyword `meeting_outcome_memory`), :2264-2374 (`_assemble_view`, where the meeting record and the trail are charged before the elastic block), :2413-2442 (`_select_within_budget`, the strict salience-ordered prefix); agents/memory/episodic.py:138 (`recent`, now a `bisect_left` over the sorted `_ticks` index 20.19 added at :94); orchestrator/game.py:1131 (`observation_ids=agent.observation_ids_for_meeting()`) and meetings/manager.py:2129-2132 (the ballot observation-id validation the ids feed, `_normalize_ballot_observation_id` at :2987-3026); agents/strategic/prompts/loader.py:321-364 (the default-OFF resolver shape this lever clones, moved by 20.19's cached environment); orchestrator/replay.py:570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`, where this key is NOT registered by this task); eval/evidence_honesty.py:704-721 (`RenderBudgetCells` — the merged render census, whose docstring hands the candidate-count bucketing to THIS task) with tests/eval/test_evidence_honesty.py:1217-1234 (`test_render_budget_pins`, the committed OFF-path cell) and :1341-1469 (`_self_placement_census`, 20.24's merged OFF/ON re-render walk); audits/audit-phase-20-preregistration.md:351-356 (the ratified §5 render-census row: 20.30's cells, secondary and observed-and-reported, never gated); DESIGN.md:667 (stage-1 coalescing "NOT IMPLEMENTED at HEAD"), :668 (the unmet "elides routine task work" claim), :724 (the specified tick-range line shape)
**Complexity:** Medium
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/agents -q` and `uv run pytest tests/eval/test_evidence_honesty.py -q` green; with the key unset `bash scripts/verify_samples.sh` reports 100/100 and `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` is green; under the lever ON the pinned cells over `replays/samples/9p2i` read mean rendered lines per snapshot ≤ 36 (the committed OFF-path baseline is now the 20.15 pin — mean 51.1038 over 1,956 snapshots, `tests/eval/test_evidence_honesty.py::test_render_budget_pins`, ratified at audits/audit-phase-20-preregistration.md:351-356; the review's 53.2 was pooled over BOTH samples sets, and per 20.22's standing rule the pin replaces the baseline cell while the ≤ 36 target does not move) and reported-testimony rows kept ≥ 80% in every candidate bucket (0/4,150 at >150 candidates today).

The information economy is spent on noise. Over the 1,088 memory snapshots reconstructed
from `replays/samples/`, the mean rendered block is 53.2 lines, of which bare
co-presence/sightings are 51.7%, the tick-0 spawn block 12.5%, `[meeting] CLAIM` stubs
15.6% and movement 20.3% — while vent lines are 0.69% and body lines 0.82%
(audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D7). The gameplay register
states the same shape set-wide: 66.1% of lines are bare co-presence or movement, hard
evidence is 1.54%, and 49.8% of all memory snapshots contain zero hard-evidence line;
duplicate `(subject, room)` rows are 23.1–23.7% and the tick-0 spawn block 14.4–14.7%
(19.7–20.7% in the 4p1i sets) — audits/review-2026-08-19/A/collated-findings.md §G-34.
That spawn block is eight lines saying every player started in CAFETERIA: identical in
every game ever played, carrying no discriminating information. Run-length-coalescing the
co-presence rows removes 37.4% of them — about 19% of the whole block — and dropping the
spawn block adds another 12.5%: ~32% of the context is recoverable at ZERO information
loss (§D7 again, and audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 2.11).

What the noise displaces is the game's only cross-meeting social memory.
`agents/memory/store.py:47` sets the production budget at 1500 tokens; `:85-91` places
`_SALIENCE_REPORTED_TESTIMONY = 25` below every first-hand row with a comment declaring
that "a budget-tight render sheds reported rows BEFORE any first-hand observation" is the
load-bearing band invariant; `_select_within_budget` at `:2413-2442` keeps a strict
salience-ordered prefix. Measured over 60 committed `replays/ml_corpus/9p2i` games and
1,656 renders: reported rows are kept 0 of 4,150 times once a render carries more than 150
candidate observations, 718 of 5,886 in the 101–150 bucket, and in 166 of the 835 renders
that HAD reported rows every one of them was shed; the agent's own completed-task row goes
0/52 in the same regime (audits/review-2026-08-19/B/agents-memory.md §2 F2, register id
C-73). The gameplay track measured the same shedding from the other side: 365 of 456
budget-pressure transitions in the corpus cut prior-meeting testimony while retaining the
8-line spawn block at full size, 143 of 188 (76.1%) in samples
(audits/review-2026-08-19/A/s4-info-economy-beliefs.md §1.4). The band invariant is
defensible; the elastic pool it protects is dead weight, so the game trades away its social
memory to keep eight constant lines.

The reasoning cost is legible in one exemplar. In seed 17 the voter p-9 spoke a stale
CAFETERIA sighting — but p-9's own rendered memory CONTAINED the right row,
`You saw p-1 in EAST_HALL (with p-4) (moved from CAFETERIA, last seen there at tick 4)`,
sitting at line 22 underneath twelve near-identical CAFETERIA co-presence rows and above
the eight-line lobby block. In the review's words, the model is reading the top of a badly
sorted list, not hallucinating
(audits/review-2026-08-19/A/ideas-game-designer.md §0.4). That reframes the phase: this is
a rendering defect, not a model-capacity ceiling. It is also the wave's ENABLER — the
self-location trail, the meetings-outcome block and the testimony-content lines the
upstream levers add are exactly the rows the current band sheds first, so without this task
they arrive and are cut in the long games where later meetings happen
(audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 2.11).

This task builds the fix as ONE default-OFF lever behind
`AILIBI_COALESCED_MEMORY_RENDER`, three folds under a single key: (a) consecutive
same-subject, same-room, same-action sightings with an unchanged companion set coalesce
into one span line carrying the tick range; (b) the tick-0 group renders as one line when
and only when it names the full known roster; (c) the salience ladder is re-banded so
reported testimony and every first-hand hard-evidence row rank strictly above bare
co-presence, with hard evidence still strictly above testimony. `DESIGN.md:667` already
records stage-1 coalescing as NOT IMPLEMENTED and `:724` already specifies the tick-range
line shape, so the ON path moves the render TOWARD the design of record rather than away
from it. OFF-path bytes are byte-identical over all 300 committed games; the ON path is
fixture-pinned and carries the committed-bytes counterfactual the pre-registration reads.

**Files in scope:**
- agents/memory/store.py; (the lever: coalesce consecutive co-presence sightings of the same subject in the same room into one span line; drop the tick-0 spawn block when it names the full roster; raise reported testimony and first-hand vent/body/kill lines above bare co-presence in salience; OFF-path bytes identical)
- agents/memory/episodic.py; (only if a span helper belongs there)
- tests/agents/test_memory_rendering.py; (OFF byte-identity; ON: spans, spawn-block rule, salience order, budget behaviour)
- tests/agents/test_reported_testimony.py; (reported rows kept ≥80% at every budget over the committed memories)
- tests/fixtures/memory_rendering/; (ON-path expected fixtures)
- tests/eval/test_evidence_honesty.py; (lines/snapshot and testimony-kept cells under the lever over samples/9p2i)

Recorded at merge (PR #382, orchestrator-ratified): the ≤ 36 rows/snapshot criterion is a FALSIFIED PREDICTION — the review projection (53.2 × 0.68) was computed against already-budget-capped renders and `_select_within_budget`'s refill makes any candidate-side fold unable to reach it; the cell re-pins at the measured mean 42.1493 (971 snapshots, samples/9p2i), with the refill arithmetic pinned (18,050 sighting rows removed − 8,663 net = 9,387 refill) and the decomposition cells kept (fold alone 40,924 rows / 39,012 subject-ticks — strictly better than OFF on both axes; the band lift costs 17.8% first-hand coverage for 0% → 95.8% testimony survival in the largest renders). One out-of-scope cell in docs/artifacts.md (tests/fixtures/ 21 → 23) accepted per the 20.24 precedent. Prose records, not scope entries.

**Files NOT in scope:**
- agents/strategic/prompts/ (no template change — the single prompt-set bump is the phase's only template edit, and it is a different task)
- meetings/ (consumes the render; the citation gate and the detector are read as consumers, never edited here)
- orchestrator/replay.py (Task 20.33 registers every Phase-20 lever in the substrate stamp at once — this task registers nothing)
- api/replay_loader.py (the served render stays on the OFF path; the counterfactual re-renders reconstructed memories explicitly)
- scripts/measure_baseline.py + eval/evidence_honesty.py (the instrument module and its CLI are the honesty-instrument task's surface; this task pins its cells in the shared test module)
- DESIGN.md (the §6.2 stage-1 "NOT IMPLEMENTED" note becomes false only at the adopting record's doc sweep)

**Definition of done:**
- [ ] `agents.memory.store.coalesced_memory_render_enabled(env: Mapping[str, str] | None = None) -> bool` exists with the 13.5 resolver signature — DEFAULT OFF, accepting `1/true/yes/on` case-insensitively, reading `os.environ` only when `env` is `None` — and is resolved ONCE inside `render_for_prompt` beside the existing observation-id resolution; `ENV_COALESCED_MEMORY_RENDER` names the key and both are exported from the module's `__all__`.
- [ ] OFF-path byte-identity: with the key unset the rendered memory is byte-identical over all 300 committed games — `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` green, `bash scripts/verify_samples.sh` 100/100, and the three committed OFF-path goldens under `tests/fixtures/memory_rendering/` — `crewmate_basic`, `tight_budget_drops_low_salience`, `impostor_minimal`, the set parametrised at `tests/agents/test_memory_rendering.py:219-233` — unchanged in the diff. That directory now holds a FOURTH `*.expected.md` (`self_location_trail.expected.md`, Task 20.24's ON-path fixture), which is likewise untouched, so the glob no longer names the OFF-path three.
- [ ] The OFF-path pin can FAIL: a perturbation test asserts the ON-path render of the same fixture memory DIFFERS from the OFF-path render (a byte-identity pin that would pass with the lever inert is not a gate).
- [ ] ON, spans: consecutive same-subject / same-room / same-action sightings whose co-presence set does not change render as ONE line carrying the tick range (shape: `You saw p-9 in CAFETERIA ticks 0–4 (with p-8).`), and a change of room, action or companion set BREAKS the run into a new span — both directions pinned in `tests/agents/test_memory_rendering.py` against a committed ON-path expected fixture under `tests/fixtures/memory_rendering/`.
- [ ] ON, the spawn block: the tick-0 sighting group collapses to a single line when and only when it names the full known roster (`_known_roster_ids`) minus the observer; a PARTIAL tick-0 view keeps its individual rows because a missing player at spawn is real information — both directions pinned.
- [ ] ON, salience: the ladder places reported testimony and every first-hand hard-evidence row (body, own kill, witnessed kill, witnessed vent, heard vent) strictly ABOVE bare co-presence/sighting rows, and hard evidence strictly above testimony; the band comment at `agents/memory/store.py:85-90` is rewritten to state the OFF-path invariant and the ON-path ordering as two truthful, lever-conditional sentences.
- [ ] Salience stays a SORT KEY, not a filter: at an unbounded budget the ON-path candidate set is the same set of facts as the OFF path (the same subjects, rooms, ticks and companions, re-shaped into spans) — asserted by a test that reconstructs the per-tick `(subject, room, companions)` triples from both renders and compares them as sets.
- [ ] The budget cell: mean rendered lines per snapshot over `replays/samples/9p2i` falls to ≤ 36 under the lever ON — pinned as an asserted range in `tests/eval/test_evidence_honesty.py`, with the OFF-path value from the SAME re-render pinned beside it so the delta is visible, and the committed baseline named: mean 51.1038 over 1,956 snapshots and 99,959 rendered rows (`test_render_budget_pins` at :1217-1234, stated VERIFIED and secondary/observed-not-gated at audits/audit-phase-20-preregistration.md:351-356). The review's 53.2 was pooled over BOTH `replays/samples/` sets, so per 20.22's standing rule the pin replaces the baseline cell and the ≤ 36 target does not move with it; the PR quotes all three numbers.
- [ ] Reported-testimony survival: at `DEFAULT_TOKEN_BUDGET` over the committed memories, reported rows are kept in ≥ 80% of renders in EVERY candidate bucket (≤60, 61–100, 101–150, >150), against the committed baseline of 0/4,150 at >150 candidates and 718/5,886 at 101–150 — pinned per bucket WITH denominators in `tests/agents/test_reported_testimony.py`.
- [ ] Citation ids still resolve: every rendered `[obs …]` prefix under the lever names an id present in that agent's own store id set (the universe `orchestrator/game.py:1086` hands the manager and `meetings/manager.py:1962-1965` validates against) — a span carries the FIRST tick's `observation_id` and the range lives in the line text; asserted as a property over reconstructed memories, and the meeting citation path stays green on a fake-provider 9p2i game run with the lever ON.
- [ ] The new code carries the current rule in one sentence plus at most one provenance line — no changelog narration in the docstrings (the standing convention).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — the resolver. The default-OFF shape now has three siblings IN THIS FILE, landed by
20.23 / 20.24 / 20.29: `task_completion_from_events_enabled` (store.py:234-264),
`self_location_trail_enabled` (:267-312) and `meeting_outcome_memory_enabled` (:315-348).
Copy one of those verbatim in structure — a module-level `ENV_COALESCED_MEMORY_RENDER`
constant, a `_..._FLAG_TRUE` frozenset, and a resolver that reads `env` when given and
`os.environ` otherwise — rather than reaching for
`agents/strategic/prompts/loader.py:321-364`, which is the same shape one module away. Do
NOT clone the GRADUATED shape at `agents/memory/store.py:212-231` — that one hard-returns
`True` at :231. Resolve once in `render_for_prompt` beside the existing
`ids_on = observation_id_rendering_enabled(env)` line at store.py:510 (the other three
levers are read immediately below it, :511-518), and thread the boolean, not the env
mapping, into the helpers.

Step 2 — where the fold belongs. Everything happens between `_build_observations`
(store.py:1566) and the sort at store.py:541-544, on the list of `_Observation` records —
NOT inside the per-event renderers. Coalescing after the observations are built keeps the
firewall suppressions, the co-presence suffix and the breadcrumb suffix exactly as they are
today, and keeps the OFF path a single early return. Prefer keeping the whole fold in
store.py; touch `agents/memory/episodic.py` only if a genuinely reusable sorted-run helper
falls out, and remember the bisecting tick index landed there upstream.

Step 3 — the span. Group the bare-sighting rows (the `_SALIENCE_SAW_PLAYER` and
`_SALIENCE_SAW_PLAYER_ACTIVE` classes only — never a vent, kill, body, move or testimony
row) by `(subject, room, action, companions)` and cut the run at any gap in ticks or any
change in that tuple. `_collect_co_presence` (store.py:1213, keyed by `(tick, room)`) is the
companion source; a changed "with" list is NEW information and must break the run. The span
keeps the FIRST tick's `observation_id` so the citation universe still resolves, and states
the range in the text; a run of length one renders exactly as today's single line, which is
what keeps the ON-path diff small and reviewable.

Step 4 — the spawn block. Derive the roster with `_known_roster_ids` (store.py:953) and
collapse the tick-0 group only when subject-plus-companions equals roster-minus-self. A
one-line summary is better than a deletion: the fact that everyone started together is
still a fact, it just costs one line instead of eight. Keep an observation id on the
summary line for the same reason as the spans.

Step 5 — the band. The ordering is the contract; the exact integers are yours. The shape
that satisfies it without disturbing anything else is a single elevated constant for
reported testimony placed above `_SALIENCE_SAW_PLAYER_ACTIVE` and below
`_SALIENCE_SABOTAGE_HEARD`, selected by the lever at render time. `_render_reported_testimony`
(store.py:1922-1926) already takes a lever bool as a keyword — `meeting_outcome_memory`, added
by 20.29 — so thread the second one the same way, never an env read
there. Leave the within-band
tie-break alone — the reviewers flagged the alphabetical `CLAIM by p-N` ordering as
arbitrary, and re-ranking within a band is a different change than re-ranking the bands.
Do not touch `_select_within_budget`: it stays a strict salience-ordered prefix, and the
whole point of the task is that the prefix now contains different things.

Step 6 — the counterfactual. Compute both cells by re-rendering the memories the honesty
instrument already reconstructs, once with an empty env mapping and once with
`{"AILIBI_COALESCED_MEMORY_RENDER": "1"}` — pass the mapping explicitly, never mutate
`os.environ`, so the pin is deterministic and the offline counterfactual task can reuse the
same call. Task 20.24 already landed exactly this walk: `_self_placement_census`
(tests/eval/test_evidence_honesty.py:1341) stops the instrument's replay walk at each
`MeetingOpened` and calls `render_for_prompt(composite, token_budget=DEFAULT_TOKEN_BUDGET,
env=…)` twice on the RETAINED composite (:1409-1414) — reuse that shape instead of building a
second walk. And note that `eval/evidence_honesty.py`'s own `render_budget` cells count rows
in the RECORDED prompt text, so the instrument can produce the OFF number and never the ON
one; the ON cell has to come from the re-render, which is why it lives in the test
module. Quote both directions in the PR summary: lines per snapshot OFF and ON, and the
per-bucket kept/total for reported rows OFF and ON.

Step 7 — honesty about what this does not do. This lever changes no gameplay rule and mints
no flag; it changes which true rows reach the model. Say that in the PR, and do not claim a
reasoning improvement the offline instruments cannot measure — the conviction-side effect
is the record's business, not this task's.

**Public types introduced:**
- `agents.memory.store.coalesced_memory_render_enabled`

**Ready-to-paste prompt:** `agent_prompts/task-20-30-coalesced-memory-render.md`

### Task 20.31 — The prompt-set bump v3 → v4: proof vs conflicting accounts, the impostor count, no threshold talk, no dead-subject vent mandate, the map card
**Branch:** `phase-20-prompt-set-v4`
**Depends on:** 20.19, 20.27, 20.29, 20.30 — the cached Jinja environment lands first so the new per-game render inputs bind per call instead of being baked into a memoized environment, and it edits the same loader file; the map-aware flag arbitration lands first so the detector and the agents read ONE adjacency graph, never a prompt promising a reconciliation rule the detector does not apply; the meetings-record memory block lands first so an agent's memory can say who is already ejected before the prompt tells it to leave a closed case alone, and it edits the same orchestrator file; the memory-render budget rework lands first so the lines this bump adds are not the first thing the budget sheds.
**Section refs:** review register ids — G-2 prompt, G-23, G-27, G-29 and R12 in audits/review-2026-08-19/A/collated-findings.md §A (G-2, lines 33-49), §C (G-23, lines 307-318), §D (G-27, lines 354-366; G-29, lines 378-386) and audits/review-2026-08-19/A/ideas-multi-agent-researcher.md R12; the adversarial verdicts in audits/review-2026-08-19/A/verdicts.md claim 2 (CONFIRMED-DESIGN-CHOICE: the "VERIFIED evidence" framing verbatim in 2,543/2,543 recorded ballot prompts; the class is 14.6% precise as sole convicting evidence) and claim 11 (b) (CONFIRMED: all six templates hard-code a singular impostor; 1,956/1,956 and 5,502/5,502 prompts; the stated win condition is arithmetically wrong for two impostors); C-129 in audits/review-2026-08-19/B/collated-findings.md line 194 ("the render contract carries no impostor count, so the templates *cannot* say it right") and F9/F12 in audits/review-2026-08-19/B/llm-and-prompts.md; the roadmap items in audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 rows 2.6, 2.7, 2.9 and the R1+R12 half of row 2.5, with the wave's own ordering ruling "2.6+2.7+2.9 batched into ONE prompt-version bump". Anchors re-verified at HEAD: the singular persona at agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:58, impostor_report.j2:59, accusation_round.j2:79, vote_ballot.j2:74 and the two variant siblings accusation_round_roll_call.j2:76, impostor_report_roll_call.j2:69; the "VERIFIED evidence" block at vote_ballot.j2:100 (and its echo "whose account a verified flag broke" at :144); the turn-phase framing "Evidence, not verdicts:" at accusation_round.j2:145; the threshold arithmetic at vote_ballot.j2:139-144; the vent-first mandate with no dead-subject exemption at crewmate_report.j2:95, accusation_round.j2:186 and :189; the version markers at each template's line 3; the registry at orchestrator/game.py:350-384 (`PROMPT_VERSION_SETS`) and :404-410 (`IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`); the archive seam at tests/meetings/test_prompt_byte_golden.py:167-181 (empty since the 16.17 retirement), its resolution at :432-449, its renderer binding at :828-841 and the perturbation leg at :1134-1181; the registry pin at tests/agents/test_bespoke_prompt_sets.py:517-533; the evidence taxonomy at api/schemas.py:704-762 (`EvidenceCategory` at :704, `ROLE_PROOF_KINDS` at :755, `CROSS_STATEMENT_KINDS` at :760-762) and :775-834 (`classify_evidence`); the weak predicate at meetings/transcript.py:633 (`WEAK_CONTRADICTION_MARKER_PREFIX`) and :912-931 (`is_weak_contradiction`); the ballot scrape at eval/_suspicion_parse.py:34-56, whose two offline consumers are eval/meeting_quality.py and eval/vj_instruments.py; the public topology at observation/public_map.py:14-32; the ten walkable rooms and eleven one-tick edges at engine/maps/canonical_1.yaml:69-175 and :176-203; the DETECTOR's own frozen copy of that same graph at meetings/transcript.py:839-852 (`CANONICAL_ROOM_NEIGHBORS`, landed by the 20.27 dependency, pinned equal to `engine.world.load_canonical_map().room_neighbors` with every edge at one tick) — the table the rendered card must agree with, since it is what makes "one adjacency graph" true rather than asserted; the render Protocols at meetings/render_contract.py:134-147, :199-215, :257-271; the renderer construction seam at agents/strategic/prompts/loader.py:694-773 and orchestrator/game.py:895-977 (`build_default_meeting_runner`); and the per-game seam that already carries a render-only roster from world state into the renderers at orchestrator/game.py:840-864 (`DefaultMeetingRunner.run_meeting`, the Task-10.3 `dead_ids` derivation) through `MeetingManager.run` at meetings/manager.py:1091-1098.
**Complexity:** Integration
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/meetings/test_prompt_byte_golden.py tests/agents tests/orchestrator tests/meetings -q` green; `grep -c "VERIFIED evidence" agents/strategic/prompts/qwen3_6_27b/*.j2` reads 0 on every file; `uv run python scripts/measure_baseline.py --honesty` over a fresh fake-provider 9p2i tournament reads the singular-persona cell 0/N where the committed baseline-6 bytes read 1,956/1,956; `bash scripts/verify_samples.sh` stays 100/100 and the prompt byte-golden still fails on a one-byte perturbation of the ARCHIVED v3 body (both runs quoted in the PR Summary).

The ballot prompt tells every voter that a bookkeeping artifact is proof.
`vote_ballot.j2:100` reads "Each flag below is VERIFIED evidence, not a verdict … never
side with [an unverified counter-accusation] over a verified flag", and the review found
that sentence in 2,543 of 2,543 recorded ballot prompts
(audits/review-2026-08-19/A/verdicts.md claim 2, review-measured over the committed
baseline-6 bytes; the phrase COUNT itself is not a committed cell — 20.15 shipped rows
I-2…I-11 and pinned the CLASS instead: sole-flag precision 12/82 as I-3 and the singular
persona 1,956/1,956 as I-9, both in tests/eval/test_evidence_honesty.py). The
flags that sentence dignifies are not one class: a grounded `vent_sighting` is
engine-certified and names an impostor 440 times out of 440, while `alibi_vs_sighting`
compares one spoken alibi against one spoken sighting and, as the sole convicting evidence
in a meeting, is right 12 times and wrong 70 — 14.6% precision against a 25.3% base rate.
The product already knows the difference: `api/schemas.py:704-762` defines
`EvidenceCategory` as `role_proof` / `cross_statement` / `weak_signal` and the spectator
renders the three apart. The agents have never been told. This task makes the prompt speak
the taxonomy the code already holds, and deletes the word that converts an artifact into a
conviction. It does NOT widen the taxonomy: `alibi_vs_physical` stays `cross_statement` on
both surfaces, because api/schemas.py:721-737 records that widening it is one decision
taken once, in two cross-pinned places.

Three more prompt defects ride the same bump, because the wave's own ordering ruling
batches them into one version layer (audits/review-2026-08-19/D/FINAL-synthesis.md §4,
"2.6+2.7+2.9 batched into ONE prompt-version bump"). Every template hard-codes a singular
hidden impostor and a parity sentence that is arithmetically wrong for two — present in
1,956/1,956 and 5,502/5,502 recorded prompts, and self-contradicting inside one prompt
where a crewmate persona line sits ninety lines above "Your fellow saboteurs: p-8"
(verdicts claim 11 (b)). C-129 names the mechanism exactly: the render contract carries no
impostor count, so the templates cannot say it right. The vent-first mandate at
crewmate_report.j2:95 and accusation_round.j2:186 orders a witness to re-speak a held vent
"even if you already said it at an earlier meeting" with no exemption for a subject who is
already dead or ejected — 232 `saw_vent` observations in the corpus name a corpse and
5.0-5.5% of turns lose their accusation to one (G-23). And the ballot's §4.6 bookkeeping
block is recited back in the characters' voices, "the 0.60 threshold" quoted 208 times
corpus-wide (G-29).

The one thing the prompts do not contain is the map. R12 measured 0 of 7,458 prompts
carrying any room list, adjacency or travel time, while 148 of 234 STRONG
`alibi_vs_sighting` flags name rooms one doorway apart — a single tick of walking
reconciles both statements. The arbitration half of that finding is the map-aware detector
lever this task depends on; this is its agent-side half, so the detector and the agents
reason over the same graph instead of the agents guessing at a geometry only the engine
can see. The canonical map is small enough to publish honestly: ten walkable rooms, eleven
edges, every one of them one tick (engine/maps/canonical_1.yaml:176-203).

This is the ONE prompt-template edit Phase 20 allows; no other task in the phase may touch
a `.j2` body, and this task touches only the locked `qwen3_6_27b` set. It is "default-OFF"
in the phase's sense without introducing any `AILIBI_*` lever: the loader's default set is
the frozen `qwen3_5_9b` reference set (agents/strategic/prompts/loader.py:133), so a bare
environment renders zero v4 bytes, and the 300 committed games keep resolving their
recorded `*.qwen3_6_27b.v3` stamps through the bump-in-flight archive that Task 16.15
built and the 16.17 re-record retired empty. That means this task introduces no
`*_enabled` resolver and registers nothing in the substrate stamp — it is the one Phase-20
wave-2 change whose gate is the existing `AILIBI_PROMPT_SET` selector plus the archive
seam, and the adopting record is what retires the archive again.

**Files in scope:**
- agents/strategic/prompts/qwen3_6_27b/*.j2; (the four default templates → v4, the two `*_roll_call` variant bodies byte-untouched on their v1 lineage: the flag block split into 'Proof' (engine-certified: vent_sighting) and 'Conflicting accounts' (alibi_conflict, alibi_vs_sighting, alibi_vs_physical — the committed `CROSS_STATEMENT_KINDS`, not widened here) with honest wording and no 'VERIFIED evidence' phrasing for the latter; persona parameterised by impostor count with the correct parity sentence; the vent-first mandate exempts dead/ejected subjects; no threshold arithmetic in the agent's voice; a compact adjacency card ('Rooms and doors: …') rendered from the public map view; the saw_move observation shape listed)
- agents/strategic/prompts/loader.py; (the impostor-count and map-card render inputs)
- meetings/render_contract.py; (the v4 contract)
- orchestrator/game.py; (PROMPT_VERSION_SETS qwen3_6_27b → v4; IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS stays v1 for the variant templates; the render inputs threaded)
- tests/fixtures/prompt_archive/qwen3_6_27b_v3/; (new: byte-copies of the six v3 bodies)
- tests/meetings/test_prompt_byte_golden.py; (ARCHIVED_PROMPT_VERSION_SETS gains the v3 entry; the committed meetings still golden through the archive)
- tests/orchestrator/test_replay_meetings.py; (VERIFY-ONLY — re-checked at HEAD: it pins the FROZEN DEFAULT-set stamps `accusation_round.v9` / `crewmate_report.v8` / `impostor_report_v6` at :443-445, names neither `qwen3_6_27b` nor `AILIBI_PROMPT_SET`, and therefore must NOT move; if it goes red the bump has leaked out of the locked set into the default path)
- tests/orchestrator/test_meeting_integration.py; (same — its one live pin is the default-set `crewmate_report.v8` at :2542; verify-only, no edit)
- tests/agents/test_strategic_prompts.py; (v4 render pins: plural persona in a 2i game, singular in a 1i game; the proof/conflict split; no 'VERIFIED evidence' string; dead-subject exemption text; the map card)
- tests/agents/test_bespoke_prompt_sets.py; (same)
- tests/meetings/test_persona_render.py
- tests/eval/test_evidence_honesty.py; (the singular-persona cell reads 0/N under v4 on a fake tournament)
- meetings/manager.py; (render-input threading only — the impostor count and the map card reach the renderer; optional kwargs with defaults so non-test callers need no change)
- scripts/record_ml_corpus.sh; (the REQUIRED_PROMPT_VERSIONS re-lock — the recorder's version pin moves WITH the registry)
- tests/scripts/test_record_ml_corpus.py; (the registry-equality pin)
- tests/agents/test_impostor_answer_arm.py; (the variant registry's inherited keys follow the set to v4)
- tests/meetings/test_elicitation_fixtures.py; (the two removed threshold-block phrases)

Recorded deviations at merge (PR #383, orchestrator-ratified): (1) five test files outside scope gained one stub parameter + import each (tests/meetings/_manager_helpers.py, tests/meetings/test_manager.py, tests/agents/test_beliefs.py, and the verify-only tests/orchestrator/test_meeting_integration.py / test_replay_meetings.py) — the Protocol widening makes every stub structurally incompatible; no pinned stamp moved, the frozen default-set pins stayed byte-unchanged and green (16.3 precedent). (2) docs/artifacts.md tests/fixtures/ row 23 → 29 / 2.1 MB — the six archived v3 bodies join the tracked count; retire with the archive entry at the re-record. Prose records, not scope entries.

**Files NOT in scope:**
- every other prompt set directory (frozen references; untouched — in particular the DEFAULT `qwen3_5_9b` set, whose crewmate_report.j2:72 carries the "do NOT emit a `found_body` observation" string two integration suites assert; those assertions stay green precisely because the frozen set does not move)
- replays/ (committed bytes resolve through the archive; nothing moves, no re-record happens here)
- orchestrator/replay.py and the substrate stamp (this bump introduces no lever key at all — there is nothing for the stamp-registration task to register; the gate is the existing prompt-set selector plus the archive)
- api/schemas.py and eval/deduction_metrics.py (the evidence taxonomy is consumed and cross-pinned, never widened — moving `alibi_vs_physical` out of `cross_statement` is a separate two-place decision)
- eval/_suspicion_parse.py (its regex is a constraint on the v4 render, not an edit target)

**Definition of done:**
- [ ] The ballot and turn flag blocks render the committed taxonomy: flags are grouped "Proof" (`role_proof`) and "Conflicting accounts", with the detector's weak stamp shown as its own subordinate group; the grouping is computed in Python from `ContradictionRef.kind` plus `meetings.transcript.is_weak_contradiction`, never re-derived in Jinja; `grep -c "VERIFIED evidence"` over the set reads 0 and vote_ballot.j2's "whose account a verified flag broke" echo is gone. Pinned in `tests/meetings/test_persona_render.py`.
- [ ] The render-side split is cross-pinned against `api.schemas.classify_evidence` over every flag in both committed sample sets (identical per-category counts), so the agents' view and the spectator's view cannot drift; `alibi_vs_physical` classifies `cross_statement` on both sides and the test says why. Pinned in `tests/meetings/test_persona_render.py`.
- [ ] The persona sentence and the win condition are parameterised by the game's impostor count: a two-impostor render says two hidden impostors and states the parity condition correctly, a one-impostor render keeps the singular wording, and the teammate line's grammar is correct for one and for many. Pinned in `tests/agents/test_bespoke_prompt_sets.py`; the fresh-tournament cell in `tests/eval/test_evidence_honesty.py` reads 0 singular-persona strings where the committed bytes read 1,956/1,956.
- [ ] The vent-first mandate carries a dead/ejected-subject exemption in every branch that states it (crewmate_report.j2:95 and BOTH branches of accusation_round.j2, :186 and :189), while "speak it FIRST" and "already said it at an earlier meeting" survive verbatim for the branches that still hold an open case. Pinned per branch in `tests/meetings/test_persona_render.py`.
- [ ] Threshold arithmetic leaves the agent's voice: no template asks the model to reason in threshold arithmetic or to name a numeric cutoff in prose it will parrot, and the ballot explicitly forbids quoting bookkeeping numbers in `rationale_text`. The rendered clause "maximum suspicion among the living ejection targets is **X**" survives byte-shaped — a test asserts `eval._suspicion_parse.VOTE_MAX_SUSPICION_RE` still matches a freshly rendered v4 ballot and captures the same value, because that line is the only per-ballot gate input that survives into a replay and two offline consumers read it on the new record.
- [ ] The map card renders in every meeting template this bump edits (the four defaults; the two `*_roll_call.j2` siblings stay byte-untouched) as at most twelve lines from `PublicMapView.room_neighbors` over the ten walkable rooms, stating the one-tick doorway fact once; `vent_graph` and `vent_rooms` never render — a negative assertion names each vent id and fails if any appears. Pinned in `tests/agents/test_bespoke_prompt_sets.py`.
- [ ] The movement observation shape introduced upstream is listed in the schema block of the turn templates, so an agent can speak the claim the detector now reads.
- [ ] The bump-in-flight seam is exact: all six pre-PR bodies are byte-copied to `tests/fixtures/prompt_archive/qwen3_6_27b_v3/` (the four default templates because the recorded stamps resolve through them, the two untouched variant siblings so the archived directory is a complete loadable set), `ARCHIVED_PROMPT_VERSION_SETS` gains the v3 entry keyed to the four recorded stamps, and the golden still re-renders every meeting of both committed sample sets byte-identically through the archive. The PR quotes a byte-level diff of each archived copy against its pre-PR body (a one-byte difference silently voids 204 goldens).
- [ ] The perturbation leg still proves the golden can fail, re-targeted at the ARCHIVED v3 body — perturbing the live v4 set is a no-op for the golden during the window, and the test's docstring says so; the v4 bodies are guarded instead by the render pins above, which the PR demonstrates by quoting one deliberately perturbed run of each.
- [ ] `PROMPT_VERSION_SETS['qwen3_6_27b']` resolves to four `*.qwen3_6_27b.v4` stamps, no value contains `.v1`, `.v2` or `.v3`, and the renamed pin in `tests/agents/test_bespoke_prompt_sets.py` asserts it; the roll-call variant registry still resolves and its two variant-file stamps keep their own lineage; the two `*_roll_call.j2` bodies are byte-untouched and the PR records their unfixed singular persona as a deliberate deferral, with the reason (an unrecorded, default-OFF arm) for the phase-close ledger.
- [ ] The frozen default path is unmoved: with `AILIBI_PROMPT_SET` unset every render is byte-identical to HEAD, `bash scripts/verify_samples.sh` stays 100/100, and `uv run python scripts/regen_test_goldens.py --check` is clean (its two targets derive from ML evidence bytes and are unaffected by construction — the PR says so rather than implying the check validates the bump).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — inventory before you edit. Run `git grep -n 'assert "'
tests/meetings/test_elicitation_fixtures.py tests/meetings/test_persona_render.py
tests/agents/test_bespoke_prompt_sets.py tests/agents/test_impostor_answer_arm.py` and
write down every rendered phrase those suites assert on the locked set. Most must survive
verbatim ("speak it FIRST", "one room, one tick", "Every EJECT names its evidence", "SKIP
is the sound call", the seven-key output contract, the worked `[obs p-2:12:0]` example).
Exactly three should break, and they are the point of the task: the two threshold-block
phrases the elicitation suite asserts, and the persona/flag strings. A phrase you break by
accident is a silent behaviour change riding a wording change.

Step 2 — the render inputs. Add one frozen dataclass to meetings/render_contract.py
carrying the game's impostor count and the pre-rendered map card, and one additive
defaulted keyword on the three render Protocols; a default of None keeps every existing
call site valid and every existing render byte-identical. Bind the inputs onto the four
renderer callables — never into the Jinja Environment, whose memo `_environment_for_set`
(loader.py:245-255) is keyed on set and root and nothing else, so per-game values must not
enter it. Split the two inputs by their lifetime, because only one of them is bindable at
construction. The MAP CARD is a constant of the canonical map: build it in the loader and
bind it onto the four renderer callables at construction (`functools.partial`, the same
discipline the roll-call lever already uses — resolved once at construction at
loader.py:741, bound at :760-772). The IMPOSTOR COUNT is per-game and CANNOT be bound
there: `build_prompt_renderers` is only reached through `build_default_meeting_runner`,
and every caller that knows a roster — eval/balance_eval.py:359, scripts/run_game.py:91,
eval/benchmark.py:124, eval/leak_scan.py:938 and the training harnesses — is out of scope
and passes none. Thread it the way `dead_ids` already travels: derive it in
`DefaultMeetingRunner.run_meeting` from the `WorldState` that seam already reads
(orchestrator/game.py:840-864) and pass it through `MeetingManager.run`
(meetings/manager.py:1091-1098) to the renderers — both files are in scope and no
out-of-scope call site moves. The card itself is built
in the loader from the public map view: agents may import observation, and rendering the
room list plus its one-tick doorways keeps the meetings leaf free of any topology import;
cross-pin the rendered adjacency against `meetings.transcript.CANONICAL_ROOM_NEIGHBORS` so
the card and the 20.27 detector cannot disagree.

Step 3 — the flag split. Classify each `ContradictionRef` in Python with the api table's
rules, sourced from what the meetings layer already exports: role proof when the kind is
`vent_sighting` or the two event ids are the same artifact, weak when
`meetings.transcript.is_weak_contradiction` is true, cross-statement otherwise. Pass the
three groups into the template context so Jinja only loops. Then cross-pin the result
against `api.schemas.classify_evidence` on the committed flags — the test may import both;
the production code must not, which is exactly why the cross-pin is the evidence.

Step 4 — the wording. Write the "Conflicting accounts" preamble so it states what is true
and nothing more: two accounts cannot both be true, nothing here says which one is wrong,
and a flag is a question to test against the transcript. The proof preamble keeps the
strength the vent channel has earned. For the persona, say the count in words rather than
a bare integer and derive the parity sentence from it, so a one-impostor render is the
sentence the four-player roster has always had. For the vent mandate, add the exemption
without touching the priority clause. For the threshold, keep the rendered maximum, drop
the numeric cutoff from the prose, and add one line telling the model the bookkeeping is
for its decision, not for its rationale.

Step 5 — the seam, in this order. Copy the four default v3 bodies into the archive
directory BEFORE editing them (`git show HEAD:<path>` into the new file is the safest
copy), register the archive entry, then edit the live bodies, then bump the version
markers on line 3 of each edited template, then the registry, then re-target the
perturbation victim. Run the golden after each of the first two steps: it must be green
after the archive lands and still green after the live bodies move.

Step 6 — the cascade. A registry bump has a known fan-out (the version-bump cascade in the
project's standing notes): the template line-3 markers, the registry entry, the variant
registry's inherited keys, the registry pin test, the recorder's locked-version constant
and the test that asserts the two agree. Walk all of them and quote the grep in the PR;
the manifest columns read as-recorded and do not move.

Step 7 — the cells. Run a small fake-provider 9p2i tournament with the set exported and
read the singular-persona cell; it must be zero. Quote the before/after beside the
committed 1,956/1,956 in the PR Summary, since the counterfactual task and the
pre-registration both consume this number.

**Public types introduced:**
- `meetings.render_contract.PromptRenderInputs`
- `agents.strategic.prompts.loader.render_map_card`
- `agents.strategic.prompts.loader.classify_flag_for_prompt`

**Integration risk:**

The widest prompt change since the persona-voice layer, and the only prompt edit this
phase allows. Three hazards, in order of how quietly they fail.

First, the blocking cascade item — verified present in Files-in-scope at HEAD (both `scripts/record_ml_corpus.sh` and `tests/scripts/test_record_ml_corpus.py` are listed), and it stays blocking:
`tests/scripts/test_record_ml_corpus.py:524`
(`test_prompt_version_registry_matches_locked_script_constant`) asserts that
`PROMPT_VERSION_SETS['qwen3_6_27b']` still equals the shell constant
`REQUIRED_PROMPT_VERSIONS` at `scripts/record_ml_corpus.sh:155`, and the recorder itself
re-asserts it at preflight. The moment the registry reads v4 that test goes red and the
full suite cannot pass, so the re-lock must ride this PR exactly as the baseline-6
record's contract required. Confirm the scope line covers it before starting; if it does
not, stop and raise it rather than shipping a red suite or a recorder that refuses to
start on the eve of a 23-hour record.

Second, byte-exactness in both directions. Every load-bearing rendered phrase the
locked-set suites assert must survive verbatim so that only the version string and the
intended lines break; and the archived v3 copies must be exact — a single trailing newline
difference leaves 204 committed meetings "golden" against bodies they never rendered,
which is worse than a red gate. Verify the copies with a byte diff, not by eye. Note also
that during the window the golden's teeth move: the live v4 templates are exercised by no
committed byte, so the perturbation leg must attack the archive or it silently stops
proving anything.

Third, the two things the change must not leak or lose. The impostor COUNT is a public
game setting — the roster preset and its impostor count are stated in the design and in
every set's name — so rendering it to crewmates leaks nothing; say that in the render
input's docstring so a later reader does not "fix" it back. And the map card must render
walkable-room adjacency only: vent topology is impostor-only knowledge that the same
public view happens to carry, and publishing it to the table would convert a legibility
fix into a firewall breach.

**Ready-to-paste prompt:** `agent_prompts/task-20-31-prompt-set-v4.md`

### Task 20.32 — The impostor mover stops declining free kills and stalking ejected players
**Branch:** `phase-20-impostor-fsm-repair`
**Depends on:** 20.15 (the free-kill and ghost-top cells become committed instruments with pinned baseline values first, so this task re-derives them under the revised policy instead of inventing a second harness; the same task also makes the read-only reconstruction pass over the impostor policy module and its test file, and a read-only pass must land before a behaviour change to the same two files); also after 20.22 (the co-intervention is declared in the ratified memo before it lands)
**Section refs:** C-3 [audits/review-2026-08-19/B/verdicts.md claim 5 — CONFIRMED and "understated"; the register row at audits/review-2026-08-19/B/collated-findings.md C-3 still quotes the pre-verification 387/233/126, superseded there by the verified 415/225/190]; C-4 [audits/review-2026-08-19/B/collated-findings.md C-4, measured in audits/review-2026-08-19/B/agents-tactical.md §2 F2 — reviewer-measured, NOT adversarially re-verified, so it is corroborated here by G-12 rather than relied on alone]; G-12 [audits/review-2026-08-19/A/verdicts.md claim 12 — CONFIRMED-BUG over 300 games / 10,335 impostor decisions with 0 mismatches against the recorded action stream]; audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 2.12 (the two-line fix), §5 ruling R3 (defect-not-lever; pre-register as a named co-intervention), §4 row 1.8 and the caveat table row 9 (the ML comparator errata this repair retires); anchors re-verified at HEAD — agents/tactical/impostor_policy.py:413-453 (the kill seam; `best = targets[0]` at :414, the co-location re-validation at :431-434, the walk-toward-best fall-through at :447-451), :825-869 (`_kill_available_now`, the same `targets[0]`-only shape at :858), :872-898 (`_confirmed_dead_from_bodies`, `saw_body` only), :996-1068 (`_scored_targets`, the `(-score, player_id)` sort at :1067), :187 (`_STALENESS_THRESHOLD = 30`), :1275-1312 (`_idle`, the pretend-task blend the fall-through lands in); agents/memory/store.py:110 and :433-440 (the `meeting_boundary` episodic marker every living agent receives at the resume tick), :549-575 (`record_meeting_outcome`), :134 (`AgentMemory.meeting_history`); agents/memory/working.py:176-185 (`MeetingHistory.record`); agents/tactical/features.py:678-696 (the v3 encoder, today's only meeting-history consumer); orchestrator/game.py:2297-2306 (the per-living-agent post-meeting fold), :2644 (the policy is handed `memory.episodic` only); api/replay_loader.py:1352-1379 (the replay-side mirror of that fold — beliefs and testimony, never the meeting outcome); agents/perception.py:62-82 (no ejection event type exists); engine/visibility.py:98-127 (the impostor keeps `same_room_and_adjacent` at base visibility); engine/rules.py:56-107 (the engine kill backstop, `:71-85`, with Task 20.11's in-vent guard at `:60-68`); agents/tactical/learned/forward.py:404-413 and training/bakeoff/utility_es.py:426-430 (both option enumerators call the policy's private statics); orchestrator/replay.py:234 (`TacticalPolicyStamp`), :319 (`FSM_DEFAULT_POLICY_ID`)
**Complexity:** Medium
**Record impact:** none for committed bytes — reconstruction replays the recorded action stream and never re-invokes a policy, so every committed replay, hash chain and MANIFEST stands; the change is a declared co-intervention in the Phase-20 pre-registration and first reaches recorded bytes at the adopting record.
**Measurement:** `uv run pytest tests/agents/test_impostor_policy.py tests/agents/test_learned_policy.py -q` green and `bash scripts/verify_samples.sh` 100/100; the committed-bytes counterfactual cells over the 50 samples/9p2i replays pasted into the PR's Summary with before beside after — free zero-witness kills declined 190/415 (45.8%) → 22/415 (5.3%), bar `< 10%`; ghost-top decisions 303/2461 (12.3%) → the 222 ejected-subject decisions 0 and the partner's-unseen-victim residual (≤ 81) quoted as measured; blocked kills 30 across 9/50 games → 0.

The impostor FSM declines almost half of its free kills for a string comparison. Over the
50 committed `replays/samples/9p2i` replays the C-3 verification counted 2,461 impostor
decisions, 415 of them carrying a legal zero-witness kill (the predicate derived from
`engine/rules.py:56-107` and `:29-44`, not from the policy's own view), and 190 of those
declined — 45.8%. 168 of the 190 are exact `1.0` score ties broken by the lexicographically
lower player id: `_scored_targets` (`agents/tactical/impostor_policy.py:937-1009`) carries
no proximity term at all, so a victim standing in the impostor's own room and one seen
alone in an adjacent room score identically, and the kill seam re-validates only
`targets[0]` (`:355`, `:372-375`). The unit repro is one line of difference: with the ids
one way the FSM walks out of the room it could have killed in, with them swapped it kills.
`_kill_available_now` (`:766-810`) inherits the same `targets[0]`-only shape at `:799`, so
the SABOTAGE lever can fire on a tick that carried a free kill. All numbers here are
review-measured over the committed baseline-6 bytes and re-pinned by the instrument task.

The same ranking keeps dead players at the top of the hunt. `_confirmed_dead_from_bodies`
(`:813-839`) builds the dead set from seen bodies only; an ejection mints no body and a
partner's victim's body is never seen, so an ejected player stays a maximum-score target
until the sighting ages past `_STALENESS_THRESHOLD = 30` (`:185`). G-12 measured this by
re-running the real `decide()` on rebuilt memory across 300 committed games with 0
mismatches against the recorded actions: on samples/9p2i, 303 of 2,461 decisions (12.3%)
rank a dead player first — 222 of them an ejected player, 81 the partner's unseen victim —
in 22 of 50 games, blocking 30 kills across 9 games. Seed 36 tick 50 is the demonstrable
case: `p-6` was ejected at tick 34 and still outranks `p-7`, alive, isolated, in the
impostor's own room, cooldown 0, on the string `"p-6" < "p-7"`; `p-7` completes the
fourteenth task at tick 51 and the crew wins a game that killing at tick 50 would have
taken to parity. Both 4p1i sets are 0/100 — the defect exists only on the 9p2i roster,
which is to say it biases exactly the canonical eval baseline downward. The ejections are
already in memory (`agents/memory/store.py:549-575` folds them into
`AgentMemory.meeting_history`, `agents/memory/working.py:176-185`); the FSM has simply
never had a channel that reaches them.

The third symptom is the pacing artifact. A sighting whose room the impostor is standing in
and can see is empty stays the best lead for the full 30 ticks, so the FSM walks to a room,
finds nobody, blends one step toward its pretend task, is re-attracted by the same stale
sighting and walks back. C-4 measured 298 of 880 stalk moves (34%) heading toward a
refuted sighting and reproduced a 25-tick oscillation; G-12 independently attributes only
about 42-46% of the A↔B windows to dead subjects, the rest to exactly this fall-through
against a live but refuted stale target — so removing the ghosts alone would leave the
artifact half-standing. C-4 is the one finding in this contract that was not adversarially
re-verified; it is taken here only where G-12 corroborates it.

This is a defect repair, not a balance lever, and that distinction is the reason it ships
in the same phase as the substrate work rather than after it. Ruling R3 in
audits/review-2026-08-19/D/FINAL-synthesis.md is explicit: C-3 and G-12 are bugs that bias
a measured baseline, every design lever stays out, and the repair is pre-registered as a
named co-intervention so the attribution stays honest. The stake is the comparator: the
ML program's headline "+0.12-0.30 win edge over the same-seed FSM" was measured against an
inner loop that discards 45.8% of its free kills and spends 8-12% of its decisions hunting
someone the whole table watched get ejected. Committed bytes do not move here — the replay
walk applies recorded actions and `orchestrator/replay.py:234` stamps the policy rather
than re-running it — so this task's evidence is a per-decision counterfactual over frozen
inputs, and the behaviour first reaches recorded bytes at the adopting record.

One design constraint dominates the implementation. `agents/tactical/learned/forward.py:404-413`
and `training/bakeoff/utility_es.py:426-430` both call the policy's private statics
(`_scored_targets`, `_confirmed_dead_from_bodies`, `_target_colocated_now`,
`_defers_to_colocated_fellow` and six more) to build the ES champion's option menu, and
`tests/agents/test_learned_policy.py:377-406` and `:462` pin the two enumerators bit-exact
against each other. Those statics are frozen: every new behaviour in this task composes
NEW private helpers inside `decide()` over the tuple `_scored_targets` already returns.
That is not merely safe, it is the correct target state — the review's own reading is that
the learned menu already enumerates `kill_now` for every co-located target, "so the ES
champion is not affected — the FSM is" (audits/review-2026-08-19/B/agents-tactical.md §2
F1). This task moves the FSM onto the behaviour the learned menu has had all along.

**Files in scope:**
- agents/tactical/impostor_policy.py; (the kill seam and the sabotage guard re-validate co-location across ALL scored targets; the decision-time target set excludes players ejected at a concluded meeting; a refuted sighting — the room since entered and the subject absent — is dropped for good; proximity enters as a tie-break tier below the score; the shared statics both option enumerators call stay byte-identical)
- tests/agents/test_impostor_policy.py; (the free co-located victim beside a higher-ranked remote one → KillIntent with the ids swapped both ways; an ejected target never ranks; the refuted-sighting drop; the two re-fixtured stalk-ordering tests; the committed-bytes counterfactual cells over samples/9p2i)
- eval/determinism_test.py; (the scripted fixtures stay deterministic — expected to be a zero-line diff, since the fixtures are recorded action streams and no policy runs in this module)
- eval/evidence_honesty.py; (ORCHESTRATOR RULING 2026-08-20 — the I-11 fold gains an explicit policy parameter defaulting to the live policy, and its fidelity guard applies only when the caller asserts it: the ratified I-11 baseline values become frozen constants measured at the pre-repair sha, quoted from the ratified memo, and the live-policy fold over the baseline-6 bytes becomes THIS repair's own counterfactual 'after' cell. I-11 is §5 secondary, observed-not-gated, so no ratified bar moves)
- tests/eval/test_evidence_honesty.py; (the module fixture split so the I-2…I-10 pins never invoke the policy fold; the I-11 pin tests quote the ratified constants and add the repaired-policy 'after' cells)
- tests/scripts/test_measure_baseline_cli.py; (the --honesty emitter labels the I-11 block by mode: ratified-baseline constants vs live-policy fold)
- audits/audit-phase-20-preregistration.md; (§11 amendment log ONLY — one dated entry recording the I-11 instrument-mode change and that no bar rides I-11)

**Files NOT in scope:**
- agents/tactical/learned/ (the ES champion and its option menus are frozen; the parity gates stay green — if a shared option enumerator or any static it calls must change, STOP and report)
- training/ (frozen; the comparator change is recorded in the pre-registration, not in training code — and `training/env.py:441` wraps the FSM as the surrogate's proposal, so a moved training-side value pin is a report, never a silent re-pin here)
- orchestrator/game.py (`:2644` hands the policy `memory.episodic` and this task does not widen that call; the ejection signal is derived from episodic memory instead)
- agents/memory/ (no new memory channel and no new event type; the post-meeting marker is read, never written)
- orchestrator/replay.py (the policy stamp id stays `fsm-default`; the record's MANIFEST git sha is the provenance of the revised FSM, stated in the record audit)
- agents/strategic/prompts/ and every `.j2` (no template edit belongs in any task but the single prompt-set bump)

**Definition of done:**
- [ ] The kill seam and the sabotage guard pick the kill target by scanning the ranked targets for the first co-located, zero-witness, non-deferred candidate instead of testing only `targets[0]`: a free co-located victim beside a higher-ranked remote one yields a `KillIntent` naming the victim, pinned in `tests/agents/test_impostor_policy.py` with the two ids swapped both ways, and the same shared helper backs `_kill_available_now` so SABOTAGE can no longer fire on a tick carrying a free kill (fixture-pinned both directions).
- [ ] No player ejected at a concluded meeting can occupy the ranking on a later decision, derived from episodic memory alone: a sighting recorded before the most recent post-meeting marker cannot rank, pinned as a unit fixture and on the reconstructed seed-36 tick-50 state where the ejected `p-6` outranks the co-located, isolated, cooldown-0 `p-7` at HEAD.
- [ ] A refuted sighting is dropped for good — once the agent has itself been in the sighting's room on a later tick without seeing the subject there, that subject stops driving STALK; pinned as a unit fixture and on the reconstructed seed-31 run (ticks 14-43, the ejected `p-1`), where the fall-through now settles into the pretend-task blend instead of alternating A↔B, asserted as a decision sequence with no room repeated in alternation.
- [ ] Proximity enters the ranking as a tier BELOW the score (`(-score, proximity_rank, player_id)`, own room ahead of adjacent ahead of remote), never above it; `test_stalk_picks_alphabetically_first_id_when_scores_tie` (`tests/agents/test_impostor_policy.py:555`) and `test_stalk_prefers_more_isolated_target_over_witnessed_one` (`:575`) are re-fixtured to pin the new rule, with an equidistant pair still falling to the player id and an isolated remote target still beating a witnessed neighbour.
- [ ] The committed-bytes counterfactual is pinned in `tests/agents/test_impostor_policy.py`, computed per decision over the reconstructed inputs of the 50 committed samples/9p2i replays with no re-simulation, the harness first asserting 0 mismatches between `decide()` and the recorded action stream at HEAD: free zero-witness kills declined 190/415 (45.8%) → only the 22 legitimate misses (15 fellow-impostor defers, 7 COVER-body) = 22/415 (5.3%) against a `< 10%` bar; ghost-top decisions 303/2461 (12.3%) → the 222 ejected-subject decisions go to 0 and the partner's-unseen-victim residual (≤ 81, the half a kill-knowledge channel would be needed to close and the ruling excludes) is pinned as measured; blocked kills 30 across 9/50 games → 0. Every before value is quoted beside its after, and a measured value that differs from the prediction is explained, not re-barred.
- [ ] No recorded kill is lost: at the 225 reconstructed states where the recorded impostor emitted a kill, the revised policy still emits the same `KillIntent`, asserted by the same harness.
- [ ] The frozen learned path does not move: `agents/tactical/learned/forward.py` and `training/bakeoff/utility_es.py` still call `_scored_targets`, `_confirmed_dead_from_bodies`, `_target_colocated_now`, `_defers_to_colocated_fellow`, `_body_visible_rooms`, `_non_teammate_witness_present`, `_crew_near_task_win`, `_sabotage_window_open`, `_active_sabotage` and `_vent_in_room` with unchanged signatures and unchanged returns; `uv run pytest tests/agents/test_learned_policy.py tests/training -q` is green, the bit-exact Q4 parity gate included.
- [ ] Committed bytes are untouched: `bash scripts/verify_samples.sh` is 100/100 and `eval/determinism_test.py` carries a zero-line diff — reconstruction replays recorded actions and the determinism fixtures are scripted action streams, so neither can move; if either does, STOP and report rather than re-pinning.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 0 — blast radius before scope. Run `grep -rn "ImpostorPolicy\._" agents/ training/ experiments/`.
It returns ten private statics consumed from outside the module by BOTH option enumerators
(agents/tactical/learned/forward.py:404-413, training/bakeoff/utility_es.py:426-430). Treat
all nine as frozen — same names, same signatures, same returns for the same inputs. Every
new behaviour in this task belongs in NEW private helpers composed inside `decide()` over
the tuple `_scored_targets` already returns. That single discipline is what keeps the ES
champion's option menu and the bit-exact Q4 parity gate green; touching `_scored_targets`
itself would move both enumerators together and invalidate a frozen artifact.

Step 1 — reproduce the baseline BEFORE changing anything. Rebuild each impostor's memory
tick by tick over the 50 committed samples/9p2i replays: `eval/replay_walk.py` for the
engine walk, `observation.service.ObservationService.build_packet` plus
`agents.perception.ingest_packet` for perception, and at each `MeetingApplied` the SAME
post-meeting fold the replay loader runs at api/replay_loader.py:1352-1379
(`absorb_meeting_evidence` then `absorb_reported_testimony`, per living agent). That fold is
load-bearing here, not cosmetic: the marker step 3 keys on is appended inside
`absorb_meeting_evidence` (agents/memory/store.py:433-440), so a harness that skips the fold
will silently measure the wrong thing. Task 20.15 already ships that reconstruction: `eval/evidence_honesty.py`'s I-11 fold runs
the same walk, the same fold and the same 0-mismatch assertion, and
`tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins` pins 190/415 with
the 168 / 15 / 7 decline split and ghost-top 303/2461 split 222/81 across all four sets.
Re-derive the baseline THROUGH that committed instrument rather than standing up a second
harness; only the 30 blocked kills has no committed cell. Read the Watch items before
editing anything.

Step 2 — the kill seam. Add one helper returning the first co-located, zero-witness
candidate in rank order, and use it in both `decide()` and `_kill_available_now` so the two
copies of the predicate cannot drift apart. Note that at most one target can satisfy it:
`co_present` is counted within the sighting's own tick-and-room bucket, and a target
co-located THIS tick necessarily has its latest sighting this tick in our room, so a second
co-located target lifts both counts above zero. The iteration therefore FINDS the free kill
rather than choosing among several, which is why it is safe and why the ranking order does
not decide which victim dies. Keep the branch order as it stands (vent exit, COVER,
SABOTAGE with the corrected guard, kill / hold / stalk, idle) and keep the fellow-defer and
witness-hold branches exactly as they are. Do NOT take the review's further suggestion to
delete `_kill_available_now` and re-order the ladder — that moves sabotage semantics and
the pins at tests/agents/test_impostor_policy.py:1387-1437, and it is a separate change.

Step 3 — the ejection barrier, derived from episodic memory only. There is no ejection
event in perception (agents/perception.py:62-82) and `decide()` is handed `memory.episodic`
alone (orchestrator/game.py:2644), so `memory.meeting_history` is not reachable from the
policy without a caller change outside this task's files; worse, the replay loader never
populates `meeting_history` at all (api/replay_loader.py:1352-1379 folds beliefs and
testimony, not the outcome), so a meeting-history-based fix would be invisible to every
replay-driven measurement in this repo, including this task's own counterfactual. Use the
signal that IS in episodic memory on both the live and the replay path: the
`meeting_boundary` marker appended at the resume tick for every living agent
(agents/memory/store.py:433-440). Compute the latest marker tick and drop any target whose
latest `saw_player` predates it. An ejected player's last sighting is necessarily
pre-meeting, so the whole ejected class disappears; genuinely stale cross-meeting leads go
with it, which is the intended direction. Mirror the marker string as a module-level `Final`
in the policy with a one-line provenance comment naming agents/memory/store.py:110 as its
producer, and pin the two strings equal in a test — a pinned local mirror is better than
importing a private name across modules.

Step 4 — the refuted-sighting drop, own-room only. A sighting of subject X at tick t in
room R is refuted when a later `self_state` puts the agent in R and no `saw_player` for X
in R is recorded at that tick. Own-room vision is the floor under every visibility mode, so
the rule needs no visibility model and stays correct under a lights sabotage; do not try to
derive adjacent-room vision inside `agents/` (engine/visibility.py:98-127 owns that and
`agents/` may not import `engine/`). The drop must be permanent — a refutation that lapses
the moment the agent leaves the room re-creates the pendulum it exists to remove.

Step 5 — proximity as a tier below the score. Re-sort inside `decide()` on
`(-score, proximity_rank, player_id)`, rank 0 own room / 1 a `public_map.room_neighbors`
entry / 2 otherwise. Do not put proximity ABOVE the score, as one reading of the finding
suggests: a witnessed neighbour would then outrank an isolated remote target and the FSM
would hold beside a crowd instead of hunting — the exact inversion the isolation test
exists to prevent. If a measurement says otherwise, STOP and report instead of ruling on it
here.

Step 6 — re-run the harness and pin the after cells beside the before cells. The predicted
residual is exactly the 22 legitimate declines; a different number means the harness or the
implementation disagrees with the review, and the PR states which.

Watch items. BLOCKER, unresolved at dispatch — read this before starting.
`eval/evidence_honesty.py`'s I-11 fold re-invokes `ImpostorPolicy.decide()` over the
committed bytes and RAISES `EvidenceHonestyReconstructionError` on any mismatch against the
recorded action stream, so this repair does not merely re-price one cell: it makes
`compute_evidence_honesty` raise on every committed set, taking the module-scoped `reports`
fixture in `tests/eval/test_evidence_honesty.py` (all of I-2…I-11),
`tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins` and
`tests/scripts/test_measure_baseline_cli.py::test_honesty_json_emits_array` down with it,
and no committed instrument can then recompute the ratified pre-registration's I-11 before
values. Where that baseline lives once the policy that produced the recorded bytes is no
longer in the tree is an owner decision this contract does not make — STOP and report
rather than widening scope into `eval/evidence_honesty.py`. `training/env.py:441` wraps the FSM as the
surrogate's proposal, so a training-side value pin may move; `training/` is frozen here.
Nothing in this task touches a prompt template or the prompt-set registry — the single
prompt-set bump (Task 20.31) owns every template edit. Keep the docstring discipline: one
provenance line per changed behaviour, no narration of the journey.

**Ready-to-paste prompt:** `agent_prompts/task-20-32-impostor-fsm-repair.md`

### Task 20.33 — The substrate stamp registration + the recorder preflight: every Phase-20 lever self-describes
**Branch:** `phase-20-stamp-registration`
**Depends on:** 20.21, 20.23, 20.24, 20.25, 20.26, 20.27, 20.28, 20.29, 20.30, 20.31 — the recorder hardening lands first because this task edits the same wrapper and its preflight is only trustworthy once the worker paths beneath it have real coverage; then each of the eight levers must already own its `*_enabled` resolver before this task can bind that resolver into the stamp BY IDENTITY, one edge per lever: the completed-task-from-events fix, the self-location trail, the movement-claim shape, the grounded prosecution, the map-aware arbitration, the structured turn markers, the meeting-outcome memory and the coalesced memory render; and the prompt-set bump must be merged because the pre-registration names THIS merge as the substrate freeze, and a version bump landing after the freeze would falsify it.; also after 20.20 (the architecture note this task corrects is embedded by the exhibit task first)
**Section refs:** audits/audit-phase-20-preregistration.md §9 (the freeze is declared at this task's merge; the record slate is "lever slate all eight ON, `impostor_roll_call` OFF") and §6 (the decision rule; each lever is independently stampable so a recording self-describes its slate); audits/review-2026-08-19/B/orchestrator.md item 6 + §"Staleness found" (b) (the registry is thirteen always-True constants plus one env read, with stale comments inside its own tests — the review's anchor `tests/orchestrator/test_replay.py:707,728` is CORRECTED at HEAD to :703-704 and :726-727, the "it is the only non-retired lever" comments); audits/review-2026-08-19/B/collated-findings.md C-64 (the accept-and-ignore residue and the 540-line constant-pinning block `tests/orchestrator/test_replay.py:212-750` — swept post-record, not here); audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 preamble ("Every item lands default-OFF / lever-gated so the committed baseline and all gates stay green until the record") and row 2.0; tasks/phase-18.md 18.11 (the precedent: lever flags registered into the snapshot BEFORE any probe seed records, so a probe/adoption recording self-describes its arms) and 18.12 (the graduation reclassification shape); orchestrator/replay.py:93-117 (`_impostor_roll_call_enabled`, the loader-only mirror and its stated reason), :547-569 (the registry comment block), :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`), :580-587 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` / `SUBSTRATE_FLAG_KEYS`), :590-625 (`substrate_flag_snapshot`); api/replay_loader.py:390-391 (the stale "env-gated; NONE today" comment) and :601-648 (`_assert_substrate_matches`); scripts/refresh_samples.sh:440-442 (the dry-run echo, featherless-only) and :576-613 (the Task-18.12 substrate-lever preflight); scripts/record_ml_corpus.sh:546-653 (`check_replay_provenance`, whose expected slate is a hard-coded bare snapshot at :572) and :789-832 (the mirrored preflight); scripts/check_doc_facts.py:794-906 (`check_lever_registry` — the live registry drives .env.example); .env.example:85-135 (the belief-substrate section); scripts/_manifest_writer.py:102-115 (`_render_flags`); eval/validity.py:931-964 (the gate's tolerant per-lever match)
**Complexity:** Medium
**Record impact:** none — stamp-side registration only: a bare environment stamps all eight new keys `False`, every committed replay omits them and the missing-key-reads-False rule makes both sides agree, so no rendered byte, no detector output and no MANIFEST cell moves.
**Measurement:** `uv run pytest tests/orchestrator tests/scripts -q` green; `bash scripts/verify_samples.sh` clean at 100/100; `uv run python scripts/check_doc_facts.py` green; `AILIBI_GROUNDED_PROSECUTION=1 uv run python -c 'from orchestrator.replay import substrate_flag_snapshot as s; print(s())'` prints that key `True` with the other seven still `False`; `bash scripts/refresh_samples.sh --seeds 0 --dry-run --expect-levers grounded_prosecution` refuses in a bare shell and passes with the export set, and the same pair holds for `scripts/record_ml_corpus.sh`.

Phase 20 builds eight substrate levers, each shipped default-OFF behind its own `AILIBI_*`
gate so the committed baseline and every gate stay green until the adopting record. None of
them registers itself into the replay substrate stamp: the lever contracts explicitly defer
registration here, exactly as the Phase-18 wave deferred its four meeting-layer flags to the
gate task that recorded with them. Without this task the eight levers are invisible to the
provenance chain — a recording made with the record slate ON would stamp a `game_over`
substrate snapshot identical to a bare baseline-6 recording, the MANIFEST `flags` cell would
claim the old substrate, and `api/replay_loader.py`'s cross-substrate guard would happily
reconstruct baseline-7 bytes under an OFF build. That is precisely the failure the stamp
exists to prevent, and it would be discovered only after a ~23 h operator record.

The registry today is one entry: `orchestrator/replay.py:570-572` binds `impostor_roll_call`
to a LOCAL mirror resolver because importing `agents.strategic.prompts.loader` would execute
its import-time, prompt-set-sensitive Jinja build inside every replay-only consumer
(:93-103 states the reason; a CI equivalence pin at `tests/orchestrator/test_replay.py:573`
stands in for the identity binding). That caveat is loader-specific and does NOT apply to the
eight Phase-20 levers: their homes are `agents/memory/store.py`, `meetings/transcript.py` and
`meetings/manager.py`, and this session verified at HEAD that importing all three under
`AILIBI_PROMPT_SET=garbage_set` pulls in no `agents.strategic` module at all and costs no
import-time env read. So each of the eight binds BY IDENTITY — the strongest form, and the
one the graduated levers kept before they retired — and the stamp cannot drift from the
read-site without a test failing.

The second half is the recorder preflight, and it is not optional housekeeping: both
recorders currently assert the toggleable set is EXACTLY `("impostor_roll_call",)`
(`scripts/refresh_samples.sh:600-601`, `scripts/record_ml_corpus.sh:819-820`), so the moment
eight keys are registered BOTH recorders refuse every run. The fix is the 18.12 preflight
generalized: an explicit `--expect-levers` slate the operator passes, checked positively
against the live snapshot before any seed stages. The hazard is the one
`replays/ml_corpus/README.md` §"the lever slate" already names — a stale export silently
mis-substrates a multi-hour record while the echo claims the ruled slate, and an acceptance
gate run in the same polluted shell passes coherently because it reads the same environment.
With eight toggles instead of one, the blast radius of a half-set export is eight times
wider and a blacklist of variable names is hopeless; only a positive whole-slate assertion
against a stated expectation catches a lever that is missing from the export as readily as
one that should not be there. `check_replay_provenance`
(`scripts/record_ml_corpus.sh:546-653`) needs the same treatment: it currently freezes
`substrate_flag_snapshot(env={})` as the expected slate at :572, which would refuse every
seed of an ON-path record by name.

Two smaller truths ride along. `api/replay_loader.py:390-391` still says a toggleable lever
is "NONE today — the machinery stays for a future lever"; that has been false since the 18.11
registration and becomes badly false with nine live toggles, and the remediation hint it
guards is the first thing an operator reads when a record and a build disagree. And the
`scripts/refresh_samples.sh` dry-run echo that describes the substrate-lever preflight sits
inside the `featherless` branch (:440-442) while the preflight itself is deliberately
provider-independent (:592, outside the provider block) — so an operator previewing an
anthropic or ollama refresh is told nothing about the check that will refuse them.

What this task does NOT do is graduate anything. Every key lands as a DEFAULT-OFF toggle;
`substrate_flag_snapshot()` in a bare environment must equal the committed baseline-6 stamp
with eight `False` entries appended, `_render_flags` never emits an OFF key so regenerating
the committed MANIFESTs is a no-op, and `eval/validity.py`'s tolerant per-lever match reads
the absent keys as `False` on both sides. The retirement sweep — folding adopted keys into
`_RETIRED_ALWAYS_ON_LEVERS`, deleting their gates, and clearing the accept-and-ignore residue
the review logged as C-64 — belongs to the adopting record and the post-record graduation
sweep, not here.

**Files in scope:**
- orchestrator/replay.py; (the eight Phase-20 levers registered in `_TOGGLEABLE_LEVER_RESOLVERS` bound to their home-module resolvers by identity; SUBSTRATE_FLAG_KEYS ordering documented; one shared slate-comparison helper)
- tests/orchestrator/test_replay.py; (the snapshot stamps all eight False in a bare env and True under their exports; identity binding per lever; the mismatch guard refuses a stamped-OFF replay under an ON environment; the two stale registry comments corrected)
- scripts/refresh_samples.sh; (the preflight asserts the slate equals an explicit expected list passed by flag; refuses otherwise; the dry-run echo describes it for every provider)
- tests/scripts/test_refresh_samples.py
- scripts/record_ml_corpus.sh; (the same preflight, plus `check_replay_provenance` judging recorded stamps against the same expected slate)
- tests/scripts/test_record_ml_corpus.py
- .env.example; (the eight levers documented as default-OFF Phase-20 toggles, with their record fate)
- tests/scripts/test_manifest_writer.py; (the flags column carries the new keys)
- api/replay_loader.py; (the substrate-mismatch remediation comment stops claiming no toggleable lever exists; the hint text itself already enumerates keys dynamically)
- tests/experiments/test_probe_backends.py; (the hard-coded _FLAGS_ON slate gains the eight keys)
- docs/architecture.md; (the toggle-count sentence only)

Coordination ruling (2026-08-24, supersedes the routed PR #381 note): this task OWNS the lever-7 reconstruction-parity closure — the slate is not recordable until a lever-ON recording reconstructs. Scope is widened accordingly (orchestrator ruling; the reverifier verified the gap at HEAD: `record_meeting_outcome` has exactly one production caller, orchestrator/game.py:3274, and none of the three mirrors folds it). Additional Files in scope: api/replay_loader.py's memory walk (:1361-1386 — fold `record_meeting_outcome` per living agent at MeetingApplied, after absorb_meeting_evidence/absorb_reported_testimony, exactly mirroring the live order), tests/meetings/test_prompt_byte_golden.py (the mirror folds the same way), eval/evidence_honesty.py (the fold at :1302 gains the same call), plus their test modules. Additional DoD: (1) a lever-ON reconstruction test proves a meeting-outcome-memory-ON render served by the loader equals the store's own render byte-for-byte at the seam; (2) the byte-golden mirror folds outcomes identically (a planted divergence bites); (3) the honesty instrument's fold is measurement-neutral on committed bytes with the channel inert OFF — every committed cell reproduces, asserted not assumed; (4) the Record impact field reads: none while OFF; this closure gates the adopting record. The three folds must share one helper or provably identical logic so the mirrors cannot drift.

Recorded deviation at merge (PR #384, orchestrator-ratified): tests/scripts/test_check_doc_facts.py — two lines re-anchoring a perturbation off the swept '# The ONE live toggle' heading onto a named constant; no assertion weakened. A prose record, not a scope entry.

**Files NOT in scope:**
- every lever's home module (the resolvers already exist; this task imports and binds them, and changes no lever behaviour)
- replays/ and replays/*/MANIFEST.md (committed stamps lack the new keys; the missing-key-reads-False rule makes both sides agree, and `_render_flags` never emits an OFF key — pinned unchanged, not edited)
- agents/strategic/prompts/ and every `.j2` template (the single prompt-set bump owns the template surface; no task after it may touch a template)
- orchestrator/replay.py's `_RETIRED_ALWAYS_ON_LEVERS` (no graduation happens here — the adopting record moves keys across, and the post-record sweep deletes the residue)
- eval/validity.py (its per-lever match already tolerates an absent key; evidence, not an edit target)
- scripts/check_doc_facts.py (it derives everything from the live registry, so .env.example alone must make it pass; if it needs a code change, that is a finding to report, not a silent edit)
- scripts/_manifest_writer.py (`_render_flags` is read as evidence that OFF keys never reach a cell)

**Definition of done:**
- [ ] All eight Phase-20 lever keys — `task_completion_from_events`, `self_location_trail`, `movement_claim_shape`, `grounded_prosecution`, `map_aware_arbitration`, `structured_turn_markers`, `meeting_outcome_memory`, `coalesced_memory_render` — are entries in `_TOGGLEABLE_LEVER_RESOLVERS`, each bound BY IDENTITY to its home-module resolver; `tests/orchestrator/test_replay.py` asserts `dict(_TOGGLEABLE_LEVER_RESOLVERS)[key] is <home_module>.<key>_enabled` for every one of the eight, and pins `SUBSTRATE_FLAG_KEYS` in its documented order with the rationale for that order stated in one line beside the table.
- [ ] `substrate_flag_snapshot({})` equals the committed baseline-6 stamp plus the eight new keys at `False`, and `substrate_flag_snapshot({"AILIBI_<KEY>": "1"})` flips exactly that one key and no other — both pinned in `tests/orchestrator/test_replay.py`, replacing the hard-coded stamp dict at :498-513 rather than sitting beside it.
- [ ] `bash scripts/verify_samples.sh` stays 100/100 and regenerating the four committed MANIFESTs leaves every `flags` cell byte-identical (the missing-key-reads-False rule plus `_render_flags` emitting only ON keys) — the PR quotes both.
- [ ] `_assert_substrate_matches` refuses a replay whose stamp records a new key `False` when that key's `AILIBI_*` export is live, and the raised `ReplaySubstrateMismatchError` lists the offending key under the TOGGLEABLE remediation hint (not the retired one) — pinned in `tests/orchestrator/test_replay.py`; the stale `api/replay_loader.py:390-391` comment now states the true live-toggle count.
- [ ] `scripts/refresh_samples.sh` accepts `--expect-levers <comma list>` naming the toggleable keys expected ON (absent or empty = the bare slate, today's behaviour), positively checks the live snapshot against it before any seed stages, and refuses with a diagnostic naming every deviating key in BOTH directions — an expected-ON key that is OFF and an unexpected export that is ON; `tests/scripts/test_refresh_samples.py` pins accept and refuse for each direction, and pins that the dry-run echo describes the expected slate for anthropic, ollama and featherless alike.
- [ ] `scripts/record_ml_corpus.sh` mirrors the flag and the refusal (`tests/scripts/test_record_ml_corpus.py` pins both directions), AND `check_replay_provenance` judges each recorded `game_over` stamp against the SAME expected slate instead of the hard-coded `substrate_flag_snapshot(env={})` at :572 — so an ON-path record is accepted by its own recorder while a stale baseline-6 replay dropped into an ON-slate set is still refused by name (pinned both ways).
- [ ] `.env.example` documents the eight toggles inside the `# Belief-substrate levers` section — one commented `# AILIBI_<KEY>=0` example line per key showing the bare-environment default, each with a one-sentence description of what turning it on changes and the explicit statement that the Phase-20 adopting record graduates whichever of them the decision rule adopts — and `uv run python scripts/check_doc_facts.py` passes with no change to the checker.
- [ ] `tests/scripts/test_manifest_writer.py` pins that a replay stamped with one Phase-20 lever ON renders that key in the MANIFEST `flags` cell (the same round-trip the `evidence_quality_lift` test at :168-192 pins), and that an all-OFF stamp still renders the unchanged baseline-6 cell.
- [ ] The two stale comments at `tests/orchestrator/test_replay.py:703-704` and :726-727 ("Task 16.8's live default-OFF absence_prior … it is the only non-retired lever") state the truth; no comment in the touched files claims a single live toggle.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — the registration. Follow the comment block above `_TOGGLEABLE_LEVER_RESOLVERS`
(orchestrator/replay.py:547-569): it is the registry's documentation and it must come out of
this task describing nine live toggles, not one. The 18.10 mirror caveat at :93-103 applies
ONLY to the loader-side lever; the eight Phase-20 resolvers live in `agents.memory.store`
(`task_completion_from_events_enabled`, `self_location_trail_enabled`,
`meeting_outcome_memory_enabled`, `coalesced_memory_render_enabled`), `meetings.transcript`
(`movement_claim_shape_enabled`, `grounded_prosecution_enabled`,
`map_aware_arbitration_enabled`) and `meetings.manager` (`structured_turn_markers_enabled`),
and this session verified at HEAD that importing all three modules pulls in zero
`agents.strategic` modules even under `AILIBI_PROMPT_SET=garbage_set` — so import them at
module scope and bind the real functions. Re-run that check yourself before you rely on it
(`AILIBI_PROMPT_SET=garbage_set uv run python -c "import orchestrator.replay"`), because the
existing `test_replay_module_imports_under_a_garbage_prompt_set` pin is what protects every
replay-only consumer. Registration order: append the eight AFTER `impostor_roll_call`, in
wave order (completed-task, trail, movement shape, grounded prosecution, map arbitration,
turn markers, meeting memory, coalesced render), and say in one line why — the tuple is
`Final` and never mutated at runtime, so the order is documentary and the stable choice is
"registration order, newest last", which keeps every prior key's index unchanged and makes
the diff to the pinned `SUBSTRATE_FLAG_KEYS` a pure append.

Step 2 — the shared slate helper. Both recorders inline the same `uv run python -c` snippet
today and both would need the same eight-key edit; give them one home instead. A function
taking the keys expected ON and returning a list of human-readable mismatch strings (empty
when the slate matches) lets the shells stay three lines and lets pytest cover the logic
directly rather than only through a subprocess. Keep the three failure classes the existing
snippets already distinguish: a retired lever reading `False` (a partial graduation), a
toggleable lever whose live state differs from the expectation, and an unknown key in the
expectation itself (a typo in the operator's `--expect-levers` list must fail loud, never be
silently ignored — that is the whole point of a positive check).

Step 3 — the shells. Add `--expect-levers` to the argument loops
(scripts/refresh_samples.sh:224-250, scripts/record_ml_corpus.sh:206-230) and to both usage
blocks. Default it to the empty slate so every existing invocation and every existing test
keeps its meaning. Move the `[dry-run] substrate-lever preflight` echo in refresh_samples out
of the `featherless` branch at :440-442 so it prints for every provider, matching where the
real check runs (:592, outside the provider block), and make both echoes quote the resolved
expected slate rather than a hard-coded baseline-6 sentence. In `check_replay_provenance`,
replace the frozen `slate = substrate_flag_snapshot(env={})` at :572 with the expected slate
threaded in from the same flag; keep the tolerant per-lever match exactly as it is (present
and True for always-on, boolean equality otherwise, unknown key = foreign stamp) so a stale
baseline-6 replay is still refused by name.

Step 4 — the docs surface. `scripts/check_doc_facts.py::check_lever_registry` derives
everything from the live registry, so .env.example is the only file that must move: for each
new key it requires the variable to appear inside the `# Belief-substrate levers` section AND
a commented line matching exactly `# AILIBI_<KEY>=0` (the bare default), and it rejects any
uncommented assignment anywhere in the file. Put the eight in a new block AFTER the blank line
that ends the `# GRADUATED LEVERS` note — the graduated note is parsed as the contiguous
comment block up to the first blank line and it rejects any "default-off" wording inside
itself, so the new default-OFF prose must live outside it, beside the existing
`AILIBI_IMPOSTOR_ROLL_CALL` block. Do not edit the checker.

Step 5 — blast radius before you widen scope. `grep -rn "impostor_roll_call" --include="*.py"
--include="*.sh"` finds every place that assumes one live toggle. Inside scope you will hit
the two shells, `tests/orchestrator/test_replay.py` (the hard-coded stamp dict at :498-513,
the registration pin at :386-420, the stale comments at :703-704 and :726-727) and the
manifest test. Outside scope you will hit `tests/experiments/test_probe_backends.py` and two
prose files — report those in the PR's Decisions rather than editing them.

**Public types introduced:**
- `orchestrator.replay.substrate_slate_mismatches`

**Ready-to-paste prompt:** `agent_prompts/task-20-33-stamp-registration.md`

### Task 20.34 — THE OFFLINE COUNTERFACTUAL: the new detector and render rules over the 300 committed games, published before the record
**Branch:** `phase-20-offline-counterfactual`
**Depends on:** 20.22 (the ratified pre-registration is the input: it fixes the cell list, the bars, the decision rule's partial-adoption clause and the abandon vocabulary this memo predicts against — a counterfactual cannot pre-register a prediction against bars the owner has not yet ratified), 20.33 (all eight lever resolvers must exist and be registered in the substrate stamp before one command can toggle the whole slate through their `env` parameters and prove the ambient process stayed OFF)
**Section refs:** audits/audit-phase-20-preregistration.md §8 (the offline-counterfactual protocol this task executes verbatim), §2 (the I-1…I-13 instrument list), §3 (the baseline cells and their denominators), §4 (the eight primary bars), §5 (the secondary observed-not-gated cells), §6 (the decision rule — partial adoption graduates nothing; this memo's per-lever predictions inform the record audit's narrative, not a graduation subset), §9 (the record order the abandon criteria guard), §10 (THE RATIFIED DECISION — its two named exceptions BIND this task by name: I-3 is `sole_flag_precision.per_victim_precision`, the kind-sole cell reading 12/82 pooled, NOT the exactly-one-flag `per_victim_single_flag_precision`'s 8/58; I-6 is `adjacent_room_flags.adjacent` — one doorway apart AND the sighting within ≤ 1 tick of the alibi window — with the un-gated `adjacent_any_gap` reported BESIDE it, never in place of it), §11 (the amendment log: the 2026-08-20 I-11 erratum — the ratified I-11 cells are frozen constants in `eval.evidence_honesty.RATIFIED_I11_CELLS`, no ratified bar rides I-11, so this script neither recomputes nor gates on them); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 preamble (the "$0 offline counterfactual … how many of the 79 innocent ejections would no longer be minted … a falsifiable prediction made before the measurement, and it de-risks a 23 h event"), §4 wave-2 row 2.5 ("run as the offline counterfactual first"), §4 wave-1 row 1.13 (the two byte-identical speed-ups exist to cut "every offline counterfactual wave 2 depends on"), §5 ruling R3 (with the mover repair declared as a co-intervention, "the offline counterfactual (frozen bytes, detector-only)" is the clean attribution instrument); audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §R1 (148/234 = 63.2% adjacent-room STRONG, and the review's own single-lever offline prediction: "78 of the 126 were adjacent-room flags, and 68 of those 78 (87.2%) ejected an innocent"), Part 1 D1 (the zero-LLM solvability oracle: containment 581/626 = 92.8%, singleton 109/626 correct 103/109, 61/354 ejections on an already-cleared player); audits/review-2026-08-19/A/verdicts.md G-2 (sole-`alibi_vs_sighting` precision 12 right / 70 wrong = 14.6%; 63.5% of resolvable sighting sides never perceived by the speaker; 70 of 79 wrongful ejections ride one), G-3 (fabricated completion lines 53/529 = 10.0% on samples/9p2i, 15/65 = 23.1% on samples/4p1i), G-9 (movement-origin flags 38/313 pooled, 38/38 memory-truthful and spoken-false, 10 meetings ejected the innocent they framed), G-25 (dev markers in turn `free_text` 53/971 = 5.5% and in 246/1956 prompts = 12.6%; singular-persona prompts 1956/1956); audits/review-2026-08-19/A/verdicts.md G-12:260 (the offline reconstruction-fidelity standard, quoted from where it actually lives: "300 games / 10,335 impostor decisions: 0 mismatches vs the recorded action stream" — that held for the PRE-20.32 policy; since the mover repair merged (`09dab356`) the live-policy fold no longer reproduces the recorded action stream, `compute_evidence_honesty(..., assert_recorded_action_fidelity=True)` RAISES, and the ratified I-11 cells are the frozen `eval.evidence_honesty.RATIFIED_I11_CELLS` — so this script must never assert recorded-action fidelity); audits/review-2026-08-19/B/verdicts.md C-3 (the state-hash-verified `eval.replay_walk.walk_replay` harness style the DoD's fidelity bullet means); tests/eval/test_deduction_metrics.py:179-182 (samples/9p2i non-direct 10/33 → 23 innocent), :257 (ml_corpus/9p2i 35/89 → 54), :296-297 (samples/4p1i 1/3 → 2), :310-311 (ml_corpus/4p1i 0/0 → 0) — the committed 19.14 pins that sum to the 79; orchestrator/replay.py:587-609 (`_TOGGLEABLE_LEVER_RESOLVERS` and `TOGGLEABLE_SUBSTRATE_FLAG_KEYS` — 20.33 MERGED (`fc5cf719`), so the table now holds NINE registered keys: the eight Phase-20 levers at :591-598, each bound BY IDENTITY to its home-module resolver, beside the pre-existing `impostor_roll_call` at :590), :620-643 (`substrate_flag_snapshot`'s threaded `env`, the no-`os.environ`-mutation seam), :646 (`env_var_for_lever`, the registry-key → `AILIBI_*` derivation), :714 (`fold_meeting_outcome_into_memories`, 20.33's shared lever-7 fold that the replay-loader walk, the prompt byte-golden walk and the evidence-honesty walk all route through — reuse it, never re-derive the meeting fold); meetings/transcript.py:1515, :1542 (the 13.5 `*_enabled(env: Mapping[str, str] | None = None) -> bool` resolver signature every Phase-20 lever follows), :1576 / :1612 / :1652 (the three merged detector-lever resolvers `movement_claim_shape_enabled`, `grounded_prosecution_enabled`, `map_aware_arbitration_enabled`), :1683-1693 (`detect_contradictions`, whose `env` keyword IS the ON-slate seam); eval/replay_walk.py:366 (`walk_replay`, the 19.25 typed per-tick consumer pattern); api/replay_loader.py:697 (`ReplayLoader`, the reconstruction entry point); eval/deduction_metrics.py:852 (`_wilson_interval`); scripts/measure_baseline.py:656 (`main`, the CLI + `--json` emitter pattern this script copies; its `--solvability` :716 and `--honesty` :726 flags are the committed readers the pre-registration §12 names)
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run python scripts/counterfactual_phase20.py --sets all` completes in < 10 min offline at $0 over the 300 committed games and prints an OFF/ON table whose every cell equals the corresponding table row in `audits/audit-phase-20-counterfactual.md`; the OFF column equals the committed 20.15 / 20.14 / 19.14 pins cell for cell (the 79-meeting enumeration reproducing 23 / 54 / 2 / 0); `uv run pytest tests/scripts/test_counterfactual_phase20.py -q` green.

The record is a one-shot, ~23-hour, $0-but-irreplaceable operator event, and a bar without a
prediction is still a post-hoc read. The pre-registration fixes what will be measured; this task
fixes what is *expected*, in advance, for every cell an instrument can compute without spending the
record. The synthesis states the protocol as the thing that de-risks the event: re-run the new
detector rules over the existing 300 committed games and publish, before recording, how many of the
79 innocent ejections would no longer be minted
(audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 preamble). The 79 is not a review figure —
it is the sum of the committed 19.14 non-direct innocent cells (33 − 10 = 23 on samples/9p2i,
89 − 35 = 54 on ml_corpus/9p2i, 3 − 1 = 2 on samples/4p1i, 0 on ml_corpus/4p1i;
tests/eval/test_deduction_metrics.py:179-182, :257, :296-297, :310-311), against 435 ejections in
total. That is the population this memo walks.

Attribution is the second reason, and it is the one the phase's own doctrine forces. Ruling R3
(audits/review-2026-08-19/D/FINAL-synthesis.md §5) admits the scripted-mover repair into the same
record as a declared co-intervention because publishing a before/after against a knowingly hobbled
comparator is precisely the failure this project's thesis forbids — and then names the price: the
record alone can no longer attribute a delta to the honesty levers. The frozen-bytes counterfactual
is the instrument that pays it. It holds the model, the mover, the seeds and the recorded bytes
constant and moves only the detector and render rules, so whatever it predicts is caused by the
levers and nothing else. Detector-only is not a limitation of the method here; it is the method.

Each lever task already pinned its own single-lever counterfactual beside the honesty instrument's
tests, and that is exactly why this task exists: nobody has yet run them as ONE slate. The levers
interact and their per-lever censuses double-count. Grounding the prosecution removes flags the
map-aware arbitration would also have removed; the movement-claim shape removes a third overlapping
set; the review's own single-lever
estimate for the adjacency rule alone — 78 of 126 flag-driven ejections vetoed, 68 of them wrongful
(audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §R1) — cannot simply be added to G-2's
70-of-79 sole-flag census (audits/review-2026-08-19/A/verdicts.md G-2) or to G-9's 38/313 origin-half
class (same file, G-9). One command, one shipping slate, one table, with denominators.

The memo's other half is the half a weaker memo would omit: what the instrument *cannot* see.
Everything downstream of new model behaviour is unpredictable offline — the non-direct conviction
accuracy (a bar about how agents vote once the substrate changes), the false crew self-placement rate
once a self-location trail exists to copy from, the model-dependent halves of the four injustice
fixtures, and the win split. A flag that stops being minted is not a vote that changes; asserting
otherwise would be the exact overreach the phase is built to demonstrate against. The memo states
each of those by name, with its reason, and then converts the whole thing into an operational
artefact: the abandon criteria the smoke and the record read as written STOP conditions, and the
per-lever predictions the record audit reads against (the ratified §6 rules out subset graduation)
(audits/audit-phase-20-preregistration.md §6), which that rule explicitly defers to this task.

Nothing here changes production behaviour: the script reads committed bytes, toggles resolvers
through their `env` parameters, writes no replay, and mutates no process environment.

**Files in scope:**
- scripts/counterfactual_phase20.py; (new — runs the 20.15 and 20.14 instruments over all four committed sets under a chosen lever slate, OFF as the baseline and ON as all eight, and emits the before/after table plus `--json`)
- tests/scripts/test_counterfactual_phase20.py; (new — the CLI contract, the OFF-equals-committed-pins property, the environment-purity assertion, and the memo-matches-the-script doc-fact check)
- audits/audit-phase-20-counterfactual.md; (new — the memo: the table, the predicted direction of each pre-registered bar, the cells that CANNOT be predicted offline with their reasons, the per-lever prediction table, and the abandon criteria for the record)

**Files NOT in scope:**
- agents/memory/store.py, meetings/transcript.py, meetings/manager.py, agents/perception.py and every other lever home module (read-only here — the mechanisms froze at the stamp registration; this task toggles them, never edits them, and a defect found here routes to a named fix task rather than being patched inside the counterfactual)
- orchestrator/replay.py (the stamp registration and the `--expect-levers` preflight are not this task's; the registry is imported and read)
- eval/evidence_honesty.py, eval/solvability.py, eval/deduction_metrics.py (the instruments are IMPORTED, never re-implemented — no cell definition may be born in this script; a cell this script needs and the instruments lack is a finding to route, not a local reimplementation). Verified at HEAD: `compute_evidence_honesty(sample_dir, *, impostor_policy, assert_recorded_action_fidelity)` (eval/evidence_honesty.py:850) and `compute_solvability_report(sample_dir)` (eval/solvability.py:395) take a DIRECTORY and expose NO lever-slate parameter — the deliberate §8 declination, restated in code at tests/eval/test_evidence_honesty.py:1044-1047 ("this instrument exposes no lever slate by design ... the ON census over the committed sets belongs to the offline counterfactual"). So the OFF column calls them as-is under the bare ambient environment, and the ON column is THIS script's own reconstruction re-evaluated through the resolvers' `env` seam. That asymmetry is exactly why the RECORDED-OFF / RECONSTRUCTED-OFF split below exists; it is NOT a defect to route
- every `.j2` prompt template (template edits belong to the single prompt-set bump; this task re-renders under whatever set is default at HEAD and never authors one)
- replays/ (nothing records and no byte moves; the committed bytes are the frozen substrate the whole method depends on holding still)
- audits/audit-phase-20-preregistration.md (ratified at merge; this memo reads against it and may only add dated errata — it never re-prices a bar)
- scripts/check.sh (the full run is a manual pre-record command, not a gate leg; the fast pins run under pytest)

**Definition of done:**
- [ ] `uv run python scripts/counterfactual_phase20.py --sets all` prints, for the OFF slate and the ON slate, every pre-registered cell the instruments can compute offline, per set and pooled, each with its numerator and denominator: the STRONG `alibi_vs_sighting` class size, its impostor share against the roster base rate and the sole-flag precision proxy; the grounded sighting side; the adjacent-room STRONG share; fabricated completion lines; origin-spoken movement flags; dev-marker contamination in turns and in prompts; singular-persona prompts; rendered lines per snapshot and reported-testimony retention; the solvability cells (containment, singleton rate and correctness, ejections on an already-cleared player); and the surviving-STRONG-flag census over the 79 innocent-ejection meetings.
- [ ] The OFF column is proven to BE the committed baseline before any ON number is believed: every OFF cell equals its committed 20.15 / 20.14 pin and the 79-meeting enumeration reproduces the 19.14 non-direct innocent split 23 / 54 / 2 / 0 — with I-11 excluded by the pre-registration's §11 erratum (its ratified cells are the frozen `RATIFIED_I11_CELLS`, not a recomputation, because the 20.32 mover repair deleted the policy that produced them; a live-policy fold reports `impostor_targeting.reconstruction_mismatches > 0` by construction) (asserted in `tests/scripts/test_counterfactual_phase20.py`, not eyeballed in the memo). A disagreement is a defect in this script, not a finding about the bytes, and the script says so in its failure message.
- [ ] Reconstruction fidelity is asserted, not assumed, in the C-3 harness style: the script separates RECORDED-OFF (an instrument reading committed bytes) from RECONSTRUCTED-OFF (the same instrument over re-derived inputs with all eight levers OFF) and refuses to print an ON column for any cell whose two OFF readings disagree. Cells that cannot agree by construction because the default prompt set moved at the prompt-set bump are printed with their RECORDED value and labelled prompt-set-coupled, with the reason in the memo.
- [ ] The slate is toggled ONLY through each resolver's `env` parameter: the script never assigns to `os.environ`, never writes a replay, and never calls an LLM. A test asserts the process environment is identical before and after a full run and that `substrate_flag_snapshot()` read from the ambient process still reports all eight Phase-20 keys False after the run completes.
- [ ] Lever interaction is reported rather than summed: the ON column is one shipping slate (all eight ON), and for each cell the memo states either the leave-one-out attribution the script computed or an explicit declination with its reason. Where the review published a single-lever estimate — the adjacency rule's 78-of-126 / 68-wrongful veto census — the memo quotes it beside the slate figure and explains the difference.
- [ ] `audits/audit-phase-20-counterfactual.md` states, for each of the eight primary bars, the predicted direction and, where the instrument computes it offline, the predicted value with its denominator; and names every cell it CANNOT predict offline with the reason — at minimum the non-direct conviction accuracy, the false crew self-placement rate once the trail exists to copy from, the model-dependent halves of the four injustice fixtures, and the win split — stating in one sentence that a flag that stops being minted is not a vote that changes.
- [ ] The memo states, per lever, the offline-predictable delta and which levers no offline instrument can support (with the reason) — the record audit's per-lever narrative under either verdict; it does NOT propose a graduation subset (the ratified §6 rules partial adoption graduates nothing).
- [ ] The abandon criteria are written as operator-applicable STOP conditions requiring no judgment call, covering at minimum: a validity-gate FAIL; a seed whose opening defaults; a substrate stamp that does not equal the intended slate; a guard trip; and a cell-level tripwire — a cell this memo predicts to reach exactly 0 that is non-zero on the smoke seeds is an ABANDON at any n, while a directional bar that merely misses on five seeds is explicitly NOT (sampling noise, recorded and carried forward).
- [ ] The run is bounded and reproducible: `--sets all` completes in under 10 minutes over the 300 committed games from a fresh clone (the wall time recorded in the PR Summary), needs no network and no `AILIBI_*` export from the operator, and `--json` emits the same table machine-readably for the record audit to consume.
- [ ] `tests/scripts/test_counterfactual_phase20.py` pins the CLI contract on a small committed slice (fast enough for the default tier, with the whole-corpus run marked `slow` if it is kept as a test at all), and asserts the memo's table equals the script's output so the document cannot drift from the instrument.
- [ ] The memo is committed before the smoke record starts — the DAG enforces the order — and the PR Summary carries the headline prediction in one sentence so the smoke report can be read directly against it.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — Read `audits/audit-phase-20-preregistration.md` §2, §3, §6 and §8 first and build the cell
list from it directly. §8 is the specification; anything this script prints that §8 does not name is
scope creep, and anything §8 names that the script cannot compute is a line in the "cannot predict
offline" section, not a silent omission.

Step 2 — One walk, two slates. Reconstruct each game ONCE (`eval.replay_walk.walk_replay` for the
typed per-tick events, `api.replay_loader.ReplayLoader` for the served meeting views), then evaluate
both slates from the same reconstruction. Reconstructing twice doubles the runtime for no signal and
invites the two passes to diverge. The detector levers are pure functions of the reconstructed
meeting inputs plus each speaker's own record, so the ON evaluation is a second call to
`detect_contradictions` with a lever-ON mapping (its `env` keyword, meetings/transcript.py:1693); the
render levers are a second render of the same rebuilt memory. Fold each meeting's outcome into those
rebuilt memories through 20.33's shared helper
`orchestrator.replay.fold_meeting_outcome_into_memories` (orchestrator/replay.py:714) — the same
helper the replay-loader walk, the prompt byte-golden walk and the evidence-honesty walk already use,
so lever 7 (`meeting_outcome_memory`) reconstructs identically in all four places.

Step 3 — Toggle by argument, never by environment. Build one frozen mapping per slate, e.g.
`{"AILIBI_GROUNDED_PROSECUTION": "1", ...}` for ON and `{}` for OFF, and thread it into the
resolvers' `env` parameter the way `orchestrator.replay.substrate_flag_snapshot` already threads it
(the 13.5 signature at meetings/transcript.py:1515). Assert the ambient snapshot is all-False at
process start and again at exit; a monkeypatched `os.environ` would make the whole memo
unreproducible for anyone who runs the command with a stale export.

Step 4 — The 79-meeting census is a join, not a new metric. Take the innocent ejections from the
committed `EjecteeProofCrossTab` partition (eval/deduction_metrics.py), key each one by
`(set, game, meeting)`, then for each recompute the ON-slate flag set and report three things: how
many still carry ANY STRONG flag naming the ejectee, how many lose the sole STRONG flag they
convicted on, and the residue grouped by which lever removed it. Cross-check the enumeration's total
against the committed pins before reporting anything — 23 / 54 / 2 / 0 — and fail loud on a mismatch.

Step 5 — Runtime. The wave-1 speed-ups (the memoized Jinja environment and the bisecting episodic
scan) exist partly for this command; use them rather than re-deriving. If `--sets all` still runs
long, parallelize per game with a process pool over immutable per-game inputs — never by sharing a
mutable renderer — and keep a `--sets <dir>` single-set path for iteration. Report the wall time in
the PR; a command nobody can afford to re-run is a command nobody re-runs.

Step 6 — Write the memo as a falsifiable prediction, not as a summary. Predicted value, denominator,
and the bar it is predicted against, in one row each; a separate short section for the cells that are
not predictable offline with one clause of reason apiece; then the per-lever prediction table and
the abandon criteria. Copy the pre-registration's evidence-label key rather than inventing one, and
state at the top that this memo is detector-and-render only by construction — the declared
co-intervention to the scripted mover is deliberately absent, which is exactly why the table is a
clean attribution instrument.

Step 7 — Keep the definitions in one place. If a cell needs a definition the instruments do not
already own, do not write it here: the instrument module is the single home for cell definitions, and
a second definition of the same cell in a script is how a memo and a record end up disagreeing about
what was measured.

**Ready-to-paste prompt:** `agent_prompts/task-20-34-offline-counterfactual.md`

### Task 20.35 — The smoke record (operator): 3–5 seeds, STOP-and-report, with the abandon branch
**Branch:** `phase-20-smoke-record`
**Depends on:** 20.34 — the offline counterfactual memo must be committed before the first live seed: it fixes the abandon criteria this smoke rules against, and its published predictions are what the smoke's directional read is compared to.
**Section refs:** audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 2 (the pre-record protocol — the $0 offline counterfactual "de-risks a 23 h event"; the record order; the primary bars) + §6 fact 2 ("The record itself runs on 917 lines of untested Bash (C-74). Harden that first … or the 23 h is at risk"); audits/review-2026-08-19/B/collated-findings.md C-74 (P1: `refresh_samples.sh` = 917 lines of worker pool + mkdir mutex + per-seed retry, `tests/scripts/test_refresh_samples.py` = 915 lines / 59 all-`--dry-run` tests, none touching `run_worker`/`_acquire_lock`/`record_one_seed` — re-verified at HEAD: the wrapper is 917 lines, `_acquire_lock` at scripts/refresh_samples.sh:639, `record_one_seed` at :689, `run_worker` at :801, and the test file is 915 lines / 59 tests); scripts/refresh_samples.sh:36-37 (`AILIBI_SAMPLE_DIR`, and `AILIBI_MANIFEST` defaulting under it), :442 (`REQUIRED_PROMPT_SET="qwen3_6_27b"`), :461 (`REQUIRED_SET_OWNER_MODEL="Qwen/Qwen3.6-27B"`), :497-534 (the substrate-lever preflight, today hard-pinned to the baseline-6 slate), :551-555 (the pre-spend roster descriptor write), :611 (the stage dir created under `dirname "$SAMPLE_DIR"`); scripts/verify_samples.sh:16-23 (a bare invocation walks EVERY set under the samples root); scripts/validity_gate.py:73-85 (`--expected-model` / `--require-zero-cost`); eval/validity.py:26-54 (the ten named checks; :47 `cost_and_provenance_exact`, :52 `byte_identical_reconstruction`); orchestrator/replay.py:570 (`_TOGGLEABLE_LEVER_RESOLVERS`), :584-588 (`SUBSTRATE_FLAG_KEYS`), :590 (`substrate_flag_snapshot`); tasks/phase-18.md:941-944 (the standing record watch item — the `cost_and_provenance_exact` blindness around the `(deadline_default)` synthetic marker, and "a seed whose opening defaults is a FAILED recording and re-records"); audits/audit-phase-16-baseline-4.md §7 (the precedent: 9p2i seed 5 re-recorded after a `(deadline_default)` phantom, its MANIFEST row stamped honestly); tasks/phase-10.md:1133 (the 5-seed smoke that covered no emergency meeting — the full run then crashed on the uncovered path), :668-680 (smoke-first STOP-for-go and the smoke-abandon evidence branch); audits/audit-phase-20-preregistration.md and audits/audit-phase-20-counterfactual.md (the ratified bars, the decision rule, and the abandon criteria this smoke executes rather than invents)
**Complexity:** Small
**Record impact:** the record itself — the first live seeds of the Phase-20 recording window; the bytes land in a scratch directory and never enter the tree.
**Measurement:** `uv run python scripts/validity_gate.py "$SMOKE_DIR" --expected-model Qwen/Qwen3.6-27B --require-zero-cost` PASS (all ten checks green, quoted in the report); `bash scripts/verify_samples.sh "$SMOKE_DIR"` reconstructs every smoke seed byte-identically; `uv run python scripts/measure_baseline.py --honesty "$SMOKE_DIR"` prints the cells the report quotes with denominators; and the committed sets are untouched — `bash scripts/verify_samples.sh` (bare) clean and `git status --porcelain replays/` empty.

The standing cadence rule is smoke before full-record: 3–5 seeds, STOP-and-report, with an
explicit abandon branch for guard trips. Phase 20 buys one measurement with roughly 23 h of
operator wall across four sets (audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 2,
which prices the record at "~23 h operator wall, $0 flat-rate"), and the review named the
hazard on the way in: the recorder is 917 lines of Bash whose worker pool, mkdir mutex and
per-seed retry had zero automated coverage (C-74 in
audits/review-2026-08-19/B/collated-findings.md; the recorder-coverage contract closes that
before this task runs). This is the cheap proof — five seeds, an hour, $0 — that the whole
stack is live and coherent before the expensive event starts: the lever slate, the v4 prompt
set, the recorder's real worker path, the substrate stamp, the validity gate, and the
honesty instruments reading a freshly recorded set rather than committed bytes.

The slate under test is the phase's, exactly: all eight Phase-20 levers ON,
`impostor_roll_call` OFF, prompt set `qwen3_6_27b` at v4, Featherless
`Qwen/Qwen3.6-27B` non-thinking, 9p2i roster. Two independent things must agree and the
smoke is where the disagreement is cheap to find. First, the wrapper's substrate-lever
preflight refuses a stale `AILIBI_*` export before any seed stages
(scripts/refresh_samples.sh:497-534) — the guard that exists because a mis-substrated
multi-hour record only reveals itself in the MANIFEST afterwards. Second, the recorded
bytes self-describe: `substrate_flag_snapshot` (orchestrator/replay.py:590) folds
`_TOGGLEABLE_LEVER_RESOLVERS` (:570) into the `SUBSTRATE_FLAG_KEYS` ordering (:584-588) and
stamps it into every `game_over` row, so the report reads the slate out of the recorded
games rather than out of the shell it was launched from. A slate that disagrees between
those two reads is an ABANDON, not a footnote.

The seed slate is a coverage decision, not a convenience one, and this project has already
paid for the lesson: the phase-10 smoke ran 5 seeds green, fired zero emergency meetings, and
the full run then crashed on that uncovered path (tasks/phase-10.md:1133). Re-derived at HEAD
over the committed baseline-6 `replays/samples/9p2i` (50 seeds, 165 meetings — the same
denominator the honesty instrument's venting-participant cell uses): every seed carries at
least 2 meetings and at least 1 ejection, so meeting-outcome memory is covered by any slate;
but the recorded contradiction rows are 96 `vent_sighting`, 76 `alibi_vs_sighting` and 8
`alibi_conflict`, with `alibi_vs_sighting` present in only 33 of 50 seeds and `alibi_conflict`
in 6 (seeds 12, 21, 28, 31, 40, 47). Seeds 0–4 carry 0, 2, 0, 0 and 0 `alibi_vs_sighting`
rows: four of five would exercise the phase's centrepiece lever — grounded prosecution —
zero times. Baseline-6 coverage is only a proxy, because the corrected substrate moves
trajectories; so the slate is chosen from it and coverage is then reported as OBSERVED on
the smoke bytes, with any lever the five seeds never exercised named as untested rather
than implied green.

The output is a report and a fork. GO means the recording window opens and the adopting
record starts on frozen source. ABANDON means the defect is described concretely enough to
author a follow-up contract, the routing is named, and the record does not start. Unlike the
phase-10 attempt-1 evidence branch — closed UNMERGED because its deliverable was the record —
the deliverable here IS the report, so this PR merges on both branches: a smoke that found
something is the smoke working. The freeze begins at GO (the standing rule that builds freeze
during measurement windows): no merge into `agents/`, `meetings/`, `observation/` or the
prompt set between this report and the record, and a routed fix reopens the window — the
smoke then runs again from zero, on the changed source, with every number re-derived.

**Files in scope:**
- audits/audit-phase-20-smoke.md; (new: the smoke report — per-seed outcome, validity gate, the honesty cells on the smoke seeds, any guard trip, the GO/ABANDON call)

**Files NOT in scope:**
- replays/samples/, replays/ml_corpus/ (the smoke records into a scratch directory that is NOT committed; committed bytes do not move at this task)
- every code path (no edits: a defect found here routes to a named follow-up contract before the adopting record — no papering fixes inside the recording session)
- tasks/phase-20.md (the phase-doc surgery for any routed follow-up is owner-side, in its own PR)
- audits/audit-phase-20-preregistration.md, audits/audit-phase-20-counterfactual.md (ratified/committed upstream; this report reads against them, errata only)

**Definition of done:**
- [ ] Five seeds of 9p2i recorded into a scratch directory OUTSIDE `replays/` at the full slate (the eight Phase-20 levers ON, `impostor_roll_call` OFF, `AILIBI_PROMPT_SET=qwen3_6_27b` at v4, Featherless `Qwen/Qwen3.6-27B`), with the resolved environment and the seed-selection rationale quoted in the report; `git status --porcelain` shows no replay bytes and no staging dir at the end.
- [ ] `uv run python scripts/validity_gate.py "$SMOKE_DIR" --expected-model Qwen/Qwen3.6-27B --require-zero-cost` PASS with all ten checks named individually in the report (`byte_identical_reconstruction` and `cost_and_provenance_exact` quoted verbatim), and a second run of the same seeds under the same environment reproduces byte-identically.
- [ ] The recorded substrate stamp is read out of the five `game_over` rows (not out of a live snapshot) and carries the eight Phase-20 lever keys True with `impostor_roll_call` False; any disagreement between the recorded stamp and the wrapper's preflight is reported as a defect, not reconciled by hand.
- [ ] The honesty cells are computed on the smoke seeds and quoted with numerators and denominators beside the counterfactual memo's predicted direction, each labelled directional-only at this n; no pre-registered bar is declared met or missed on five seeds, and the report says so in those words.
- [ ] Lever coverage is reported as OBSERVED on the smoke bytes (which levers actually fired, with counts), and any lever the slate never exercised is named as untested.
- [ ] Operating data for the record's re-plan is recorded: per-seed wall clock, tokens per call and per meeting, worker occupancy, and every retry or transport blip the run absorbed — so the roughly 23 h projection is re-derived from measured tokens before the adopting record starts.
- [ ] GO or ABANDON is recorded verbatim against the abandon criteria in `audits/audit-phase-20-counterfactual.md` — no criterion invented here; a seed whose opening defaults follows the standing rule (a FAILED recording that re-records, stamped honestly), and a repeat of that class across seeds is a class defect, not a re-record.
- [ ] On ABANDON: the defect is described with symptom, seed, suspected file and a reproduction; the follow-up is named as a routing slot for the owner to land; and the report states plainly that the adopting record does not start.
- [ ] Committed bytes untouched: `bash scripts/verify_samples.sh` (bare) still verifies every committed set clean, and no file under `replays/` differs from HEAD.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — Read the two memos before touching a terminal. The pre-registration owns the bars
and the decision rule; the counterfactual memo owns the predicted cells and the abandon
criteria. This task executes them. Where the smoke's reading and a memo disagree, the memo
wins and the disagreement is the finding.

Step 2 — Pick the seeds by coverage. Draw candidates from the counterfactual memo's
enumerated meetings first (a seed whose baseline-6 game is in the wrongful-ejection census
gives the strongest before/after read), then top up so the slate covers, at minimum: several
`alibi_vs_sighting` rows, at least one `vent_sighting`, at least one `alibi_conflict`, at
least one multi-ejection game, and a game that ends by task completion rather than ejection.
The HEAD census above is the shopping list — for instance seeds 31 and 13 are the two
`alibi_vs_sighting`-densest baseline-6 games, 16 is vent-dense, and 40 carries three
`alibi_conflict` rows. Do not default to 0,1,2,3,4: four of those five carry no
`alibi_vs_sighting` row at all.

Step 3 — Export the whole environment in one block BEFORE any worker process starts; every
lever is read at runner construction, never mid-run. The block is `AILIBI_LLM_PROVIDER=featherless`,
`FEATHERLESS_API_KEY` (operator's, never echoed into the report), `AILIBI_PROMPT_SET=qwen3_6_27b`,
`AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B`, the 9p2i roster
(`AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2`),
`AILIBI_SAMPLE_DIR="$SMOKE_DIR"`, and the eight lever exports `.env.example` documents in
its Phase-20 block. `AILIBI_MANIFEST` needs no export — it defaults under the sample dir
(scripts/refresh_samples.sh:37).

Step 4 — Put `$SMOKE_DIR` at an absolute path OUTSIDE the repo. Two reasons, both verified:
a bare `bash scripts/verify_samples.sh` walks EVERY set under the samples root
(scripts/verify_samples.sh:16-23), so a scratch set parked under `replays/samples/` would
silently join the committed gate; and the per-refresh stage is created under
`dirname "$SAMPLE_DIR"` (:611), so an out-of-tree sample dir keeps the staging out of tree
too. The wrapper creates the dir and writes its `roster.json` before any spend (:551-555),
failing loud if an existing descriptor disagrees.

Step 5 — Preflight, then record. Run `bash scripts/refresh_samples.sh --seeds <slate> --dry-run`
first: it touches nothing and echoes the resolved provider, prompt set, roster, sample dir,
worker count, retry budget and the preflights it would run — paste that block into the
report as the recorded configuration. Then run the same command with the lever-slate
expectation the stamp-registration work added (`--expect-levers`), without `--dry-run`.
The preflight refusing to start is a SUCCESS of this task, not a failure: it means a stale
export was caught before the 23 h event.

Step 6 — Gate, then measure, in that order. A set that fails the validity gate is not
measured — its cells are meaningless and quoting them invites reading them. When the gate is
green, run the honesty instrument over the scratch dir and tabulate every cell beside its
baseline-6 value and the memo's predicted direction, with denominators, all labelled
directional at n=5.

Step 7 — Watch items carried forward from the last two records: the gate's
`cost_and_provenance_exact` has a known blindness around the `(deadline_default)` synthetic
marker, so scan the recorded failed-call rows by hand for that class rather than trusting the
gate alone (the precedent is a 9p2i seed re-recorded for exactly this phantom); and confirm
the v4 prompt set actually rendered by reading one meeting prompt out of a recorded game
rather than inferring it from the version string.

Step 8 — Write the report as a record, not a narrative: configuration, per-seed table,
gate output, coverage table, cells table, watch-item scan, the wall-clock and token
measurements, then the verdict in one line with the criterion it was ruled against beside it.
STOP there and report — the go/no-go is the owner's, and the adopting record is a separate
contract that starts only after this one merges.

**Ready-to-paste prompt:** `agent_prompts/task-20-35-smoke-record.md`

### Task 20.36 — THE ADOPTING RECORD: baseline 7 (operator ~23 h, $0) — samples 9p2i → corpus 9p2i → samples 4p1i → corpus 4p1i, graduation flips, floors, re-pins, the record audit
**Branch:** `phase-20-baseline-7-record`
**Depends on:** 20.35, 20.6, 20.7, 20.8, 20.10, 20.11, 20.12, 20.17, 20.18, 20.32 — the smoke leg must report GO on the real provider before a single seed of the committed record stages, and it is the only place the token cost of the new prompt set is measured before the wall clock is committed; the vote-correctness truth pass owns the zero-flag ejection census this record moves; the Pages workflow must be live so the re-curated featured strip redeploys from the new bytes rather than shipping a dead link; the entitlement-checking leak scanner must be the version that runs over the new bytes, because a record verified by the old shape-only scanner proves nothing about the firewall; the truncation acceptance gate must be fixed first or a half-written seed enters the canonical corpus as "verified"; the in-vent action guards must land before the freeze so the recorded action stream cannot contain an untraceable kill; the front-door rewrite owns the README prose and the generated-fact checks whose numbers this record moves; the gate-hermeticity fix and the parallel test runner must both be merged because this PR runs the full suite dozens of times during the re-pin sweep and a false BROKEN or a 338-second serial run makes that sweep unaffordable; the impostor-mover comparator repair is the declared co-intervention and must be inside the freeze, not straddling it.; also after 20.13 (the README sections those tasks own precede the provenance paragraph this record moves); also after 20.20
**Section refs:** audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 "The record" (:272-276 — record in value order, corpus 9p2i before either 4p1i leg because the non-direct cell is n=89 there against n=33 in the samples), "Close gates" (:278-281) and "Primary bar (pre-registered)" (:282-287), plus §4 Wave 3 row 3.1 (re-curate the featured games against the new bytes); audits/audit-phase-20-preregistration.md §4 (the eight primary bars), §5 (the secondary win-split band — baseline-6 impostor rates re-derived at HEAD from the MANIFEST `winner` column: samples 17/50 4p1i and 15/50 9p2i, corpus 38/150 9p2i and 11/50 4p1i), §6 (the decision rule: ADOPTED / FINDING / partial adoption), §7 (the co-intervention and the unchanged `fsm-default` policy id), §8 (the abandon criteria), §9 (the record order and the freeze list); audits/audit-phase-20-planning.md §2; tasks/phase-18.md Task 18.12 and Task 18.13 (the two runbooks this contract fuses); audits/audit-phase-18-baseline-6.md §§0-10 (the record-audit shape) and §7 (the provenance tuple and the `(deadline_default)` validity-gate watch item); replays/ml_corpus/README.md:300-320 (the MEASURED baseline-6 legs: 4p1i 0h45m, 9p2i 19h26m, phantom-repair 2h43m, total ~22h54m) and :39-51 (the Q3 canary-denominator rule); review register ids: G-1, G-2, G-3, G-5, G-9, G-12, G-25 (audits/review-2026-08-19/A/verdicts.md), C-2, C-3 (audits/review-2026-08-19/B/verdicts.md), C/A6 and C/B2 (audits/review-2026-08-19/C/collated-portfolio.md). Anchors re-verified at HEAD: orchestrator/replay.py:531-546 (`_RETIRED_ALWAYS_ON_LEVERS`, thirteen keys today), :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS` — `impostor_roll_call` is the sole live toggle at HEAD), :580-587 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` / `SUBSTRATE_FLAG_KEYS`), :590-624 (`substrate_flag_snapshot`, retired keys report unconditionally True); eval/watchability.py:538 (`_BASELINE_SUPPLY_FLOORS`), :777-839 (the baseline-6 block, its three gauges and the 16.11 population-relative derivation), :854 (`_DEFAULT_BASELINE_ID = "baseline-6"`); tests/meetings/test_prompt_byte_golden.py:165-181 (the 16.15 archive seam — `ARCHIVED_PROMPT_VERSION_SETS` is EMPTY at HEAD and `tests/fixtures/prompt_archive/` does not exist; the v3 entry is created by the prompt-set bump and retires HERE), :1149-1160 (the one-byte perturbation gate, which walks both registries); orchestrator/game.py:301 + :346-347 + :400 (`DEFAULT_PROMPT_VERSIONS`, `PROMPT_VERSION_SETS`, `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`); scripts/record_ml_corpus.sh:102-155 (the pin block and `REQUIRED_PROMPT_VERSIONS`, all four templates at v3 today), :273-323 (the `seed % 5` splits writer); scripts/refresh_samples.sh:878 + :894-913 (the post-record eval-report rebuild and the rubric refresh); scripts/validity_gate.py:73-87 (`--expected-model`, `--require-zero-cost`); scripts/verify_ml_evidence.py:126-138 (the five legs and `FAST_SAMPLE_PER_SET = 8` — `--fast` SAMPLES eight seeds per set, so a 300/300 claim requires the full run), :1244-1263 (every declared set is walked); tests/eval/test_deduction_metrics.py:178 and :224 (`non_direct_ejections == 33`), :256 (`(35, 89)`), :295-310 (the two 4p1i cells and the empty-denominator sentinel); tests/api/test_evidence_mechanisms.py:114-135 (the anchors point at committed bytes), :173, :194, :220-241, :249 (the four 19.11 injustice exhibits, each pinned to a named seed and meeting index); tests/scripts/test_manifest_writer.py:82-121 (the thirteen-ON flags string, twice); tests/api/test_sets.py:343-348 (the rubric regeneration recipe), :364-372 (the provenance-fingerprint pin), :431-442 (the featured-seed pin — 9p2i {2, 8, 17, 23}, 4p1i {2, 29, 41}, head `("9p2i", 2)`); frontend/src/components/ReplayPicker.tsx:95-101 (the BINDING spoiler rule) and :102-146 (`FEATURED_GAMES`); scripts/check_doc_facts.py:172-183 (`check_sample_provenance` re-derives README's refresh date, impostor win rates, recording model and prompt-set version FROM the sample MANIFESTs), :360-385 (`check_ladder_tip`, sourced from the phase-18 close audit), :409-508 (`check_lever_registry` — a graduated key must be named in `.env.example`'s always-ON note and must NOT appear as an `AILIBI_*=` line anywhere in the file); tests/scripts/test_check_doc_facts.py:71-72 and :482 (the real-repo assertions `check_facts(_REPO_ROOT) == []` and `main(["--repo-root", str(_REPO_ROOT)]) == 0`); README.md:149 (the sample-provenance paragraph, today naming 2026-07-20, `v3`, 34% and 30%); AGENTS.md:106-110 (craft rule 7).
**Complexity:** Integration
**Record impact:** the record itself
**Measurement:** `bash scripts/verify_samples.sh` 100/100 on the new samples bytes; `uv run python scripts/verify_ml_evidence.py` (FULL — no `--fast`, which samples eight seeds per set) green with reconstruction 300/300 across the four declared sets; `uv run python scripts/validity_gate.py <set> --expected-model Qwen/Qwen3.6-27B --require-zero-cost` PASS on each of the four; `uv run python scripts/measure_baseline.py --honesty <set>`, `--solvability <set>` and `--watchability` cells equal the record audit's tables cell for cell; `uv run pytest -q` and `bash scripts/check.sh` green in a CLEAN worktree — every output pasted into the PR Summary.

This is the phase's one record, and the only task in Phase 20 that writes committed replay bytes. Four sets, 300 games, in the order the ratified memo fixes (`audits/audit-phase-20-preregistration.md` §9): `replays/samples/9p2i` (the set the demo and the featured strip serve) → `replays/ml_corpus/9p2i` (where the power is: the non-direct conviction cell is n=89 in the corpus against n=33 in the samples, `tests/eval/test_deduction_metrics.py`:256 and :178) → `replays/samples/4p1i` → `replays/ml_corpus/4p1i`. Every leg records at the frozen Phase-20 slate — `Qwen/Qwen3.6-27B` non-thinking on Featherless, the `qwen3_6_27b` prompt set at v4, the eight evidence-honesty levers ON, `impostor_roll_call` OFF, `$0` — and every leg passes the validity gate before the next one starts.

The task does not decide anything. The decision rule was ratified before the first lever existed (`audits/audit-phase-20-preregistration.md` §6): ADOPTED iff bars 1, 2, 3, 5, 6 and 7 are met AND at least three of the four injustice fixtures flip AND either bar 4 is met or the sole-flag meeting count has fallen below 20 pooled; FINDING otherwise; partial adoption graduates NOTHING (the ratified §6 ruling: a subset slate matches neither committed stamp — all eight graduate under ADOPTED, none under FINDING). The contract's job is to execute whichever branch the arithmetic selects, in code, in the same PR that commits the bytes. On ADOPTED the eight `*_enabled` resolvers hard-return `True`, their keys move from `_TOGGLEABLE_LEVER_RESOLVERS` (orchestrator/replay.py:570-572) into `_RETIRED_ALWAYS_ON_LEVERS` (:531-546), and the v3 prompt-archive entry the bump created retires because no committed set stamps v3 any more. On FINDING the levers stay toggles, the bytes and the read are committed anyway as the finding record, and the ladder tip stays at baseline 6. Either way the numbers are published — that discipline is the reason the phase exists, and "adopt anyway" is the single failure this task must not produce.

The read itself is mechanical and must be written that way. Each of the eight primary bars is quoted on the new bytes beside its baseline-6 value, from the instrument that owns it and no other: `eval/deduction_metrics.py` for the non-direct conviction cell (0.303 samples 9p2i, 0.393 corpus 9p2i, 1/3 samples 4p1i, no cell for corpus 4p1i — pooled 46/125 = 0.368 with 79/79 innocent ejections inside the non-direct cell, [VERIFIED] pins at `tests/eval/test_deduction_metrics.py`:178, :224, :256, :295-310); `eval/evidence_honesty.py` for false self-placement, sole-flag precision, grounded sighting side, fabricated completions and the adjacent-room share (review-measured over the committed baseline-6 bytes and re-pinned by the honesty-instrument task; the RATIFIED pins are authoritative where they re-anchored the review: 152/723 = 21.0%, per-victim 12/82 = 14.6%, 124/234 = 53.0% grounded at tick, 19/458 fabricated rows that reached a model, 148/234 = 63.2%); `eval/solvability.py` for the y-axis; and `tests/api/test_evidence_mechanisms.py`:173/:194/:220/:249 for the four injustice exhibits, each of which is anchored to a named seed and meeting index (:114-135) and therefore either flips, survives, or must be re-anchored with its reason recorded. The secondary cells are reported and never gated, the win split inside its pre-registered band.

The re-pin sweep is the widest this repository has ever run. At HEAD, `grep -rln 'replays/samples\|replays/ml_corpus' tests/` returns 37 test files, and this phase added roughly twenty more cells on top of them (the solvability pins, the ten honesty cell families, the deduction cells re-read on new bytes). Every one moves: the watchability floor block (`eval/watchability.py`:777-839 must gain a `baseline-7` sibling pinned from these bytes with the same 16.11 population-relative derivation and the same self-consistency property — the record scores PASS against its own floors at exact equality), the MANIFEST flags string pinned twice in `tests/scripts/test_manifest_writer.py`:82-121, the manifest provenance fingerprint and the rubric that keys off it (`tests/api/test_sets.py`:364-372, regenerated by the recipe at :343-348 which `scripts/refresh_samples.sh`:894-913 already runs after a re-record), the tournament eval report the front door points a stranger at, and the curated featured strip. Budget this pass as its own day; a stale pin discovered after merge is a two-artifact seam that costs more than the sweep did.

Duration honesty, from committed numbers rather than hope. The measured baseline-6 corpus legs were 4p1i 0h45m for 50 games and 9p2i 19h26m for 150 games, plus a 2h43m phantom-repair pass — ~22h54m for 200 games (`replays/ml_corpus/README.md`:300-310). At those same per-game rates the two samples legs add roughly 6h30m (9p2i) and 0h45m (4p1i), so the four-set sum is ~27-28 h BEFORE the v4 prompt set's added tokens: the adjacency card and the restructured flag block both grow every meeting call. The title's ~23 h is the corpus-only baseline-6 figure and must not be planned against. Measure tokens per meeting call on the smoke, scale the baseline-6 legs by the measured ratio, and re-plan the wall clock in writing before the first seed stages. A partial record is not a baseline: checkpoint-push each completed seed range, and never commit a half-set as canonical.

**Files in scope:**
- orchestrator/replay.py; (the eight levers reclassified to `_RETIRED_ALWAYS_ON_LEVERS` IF the pre-registered decision rule adopts the record; otherwise they stay toggles and the record is committed as a FINDING record — the rule decides, the task executes)
- agents/memory/store.py; (the graduation flips ONLY — `*_enabled` bodies hard-return True for adopted levers; mechanism bodies froze at 20.33)
- meetings/transcript.py; (same)
- meetings/manager.py; (same)
- orchestrator/game.py; (no registry change — v4 is already the default; the archive entry retires in the golden test)
- tests/meetings/test_prompt_byte_golden.py; (ARCHIVED_PROMPT_VERSION_SETS: retire the qwen3_6_27b_v3 entry and delete tests/fixtures/prompt_archive/qwen3_6_27b_v3/ once no committed set stamps v3)
- replays/samples/9p2i/; (the baseline-7 record: bytes, MANIFESTs, splits.json, READMEs)
- replays/samples/4p1i/; (same)
- replays/ml_corpus/9p2i/; (same)
- replays/ml_corpus/4p1i/; (same)
- replays/ml_corpus/README.md
- scripts/record_ml_corpus.sh; (the pin block moves to baseline 7)
- eval/watchability.py; (the baseline-7 floor block pinned from the recorded bytes)
- audits/audit-phase-20-baseline-7.md; (new: the record audit — the pre-registered read, cell by cell, ADOPTED or FINDING per the decision rule; the provenance tuple; the co-intervention declared)
- tests/eval/; (the byte-coupled committed-bytes re-pins this record moves — every pin over replays/samples/ and replays/ml_corpus/, including the 19.14 deduction cells, 20.14/20.15 cells, 18.1/18.2/18.3 instrument pins, the manifest writer pins, the rubric score)
- tests/agents/; (same)
- tests/meetings/; (same)
- tests/api/; (same)
- tests/scripts/; (same)
- tests/training/; (same)
- frontend/src/components/ReplayPicker.tsx; (FEATURED_GAMES re-curated against the new bytes — seed ids kept where the game still earns its blurb, replaced where not; blurbs stay spoiler-free)
- tests/api/test_sets.py; (the featured-seeds pin)
- .env.example; (the graduated keys move to the always-ON note — check_lever_registry couples it to the reclassification)
- README.md; (the sample-provenance paragraph and the ladder-tip sentence only — check_sample_provenance re-derives both from the new MANIFESTs)
- scripts/check_doc_facts.py; (the _LADDER_TIP_AUDIT repoint to the record audit)
- tests/scripts/test_check_doc_facts.py

**Files NOT in scope:**
- agents/tactical/ (the mover repair landed before the freeze; frozen during the window)
- training/ artifacts and fits (the ML program is frozen; a re-ground is a future owner decision — the staleness rule is STATED in the audit, not discharged)
- agents/strategic/prompts/ (the templates froze at the single prompt-set bump; a record that edits a template is not a record)
- the lever mechanism bodies (they froze at the stamp-registration merge; only the resolver return values move here)
- eval/evidence_honesty.py, eval/solvability.py, eval/deduction_metrics.py (the instruments are read here and never redefined — a cell re-implemented at the record makes before and after incomparable)

**Definition of done:**
- [ ] All four committed sets are recorded at the Phase-20 slate in the pre-registered order (samples 9p2i → corpus 9p2i → samples 4p1i → corpus 4p1i), each with `scripts/validity_gate.py <set> --expected-model Qwen/Qwen3.6-27B --require-zero-cost` PASS, byte-identical reconstruction under a bare environment, the substrate-flag snapshot in the recorded bytes equal to the slate exactly (eight Phase-20 levers ON, `impostor_roll_call` OFF, the thirteen prior graduations ON), MANIFEST provenance exact on every row (model, the four v4 template versions, flags, `fsm-default` policy, sha, `0.0000`, winner), and each completed seed range checkpoint-pushed before the next begins.
- [ ] The pre-registered read is executed cell by cell in `audits/audit-phase-20-baseline-7.md`: every primary bar quoted with its own instrument's pin on the new bytes beside the baseline-6 value and its denominator, with the eight bars answered in the memo's own order and each verdict stated MET or MISSED in one word; no bar is re-priced, and a missed bar is reported as missed with its number.
- [ ] The decision rule is applied verbatim and its output executed in this PR: on ADOPTED, the eight `*_enabled` resolvers in `agents/memory/store.py`, `meetings/transcript.py` and `meetings/manager.py` hard-return `True`, their keys move from `_TOGGLEABLE_LEVER_RESOLVERS` into `_RETIRED_ALWAYS_ON_LEVERS`, `substrate_flag_snapshot({})` stamps them True unconditionally, and the tests that pinned their OFF path are re-pointed or deleted; on FINDING, the registry is unchanged, the ladder tip stays baseline 6, and the audit says so in its verdict line; no subset graduates under any verdict (the ratified §6 ruling); a per-lever cell that met its bar under FINDING is reported in the audit's narrative, never executed as a graduation.
- [ ] The v3 prompt archive retires: `ARCHIVED_PROMPT_VERSION_SETS` returns to empty and `tests/fixtures/prompt_archive/qwen3_6_27b_v3/` is deleted once no committed set stamps a v3 template, with `tests/meetings/test_prompt_byte_golden.py` still walking every committed meeting golden through the live registry alone and still failing on a one-byte perturbation of a v4 template (the perturbation test is run and its red output quoted in the PR).
- [ ] A `baseline-7` block is added to `eval/watchability.py::_BASELINE_SUPPLY_FLOORS` pinned from the recorded bytes with all three gauges and their raw numerators, the 16.11 population-relative derivation restated, and the self-consistency check demonstrated: the referee scores the record's own bytes PASS at exact floor equality. `_DEFAULT_BASELINE_ID` moves to `"baseline-7"` on ADOPTED and stays `"baseline-6"` on FINDING; the training-side selection constants deliberately lag and the audit says which task owns the re-ground.
- [ ] Every byte-coupled pin across the six test directories is re-pinned in the same PR with the old value quoted in a comment beside the new one — the deduction cross-tab cells, the ten honesty cell families, the solvability cells, the funnel / V&J / watchability instrument pins, the MANIFEST flags strings in `tests/scripts/test_manifest_writer.py`, the manifest-fingerprint and rubric pins in `tests/api/test_sets.py`, and the corpus-derived training pins — and `uv run pytest` is green with no `xfail` added to absorb a moved number.
- [ ] The four 19.11 injustice fixtures are re-read against the new bytes: each is recorded as FLIPPED, SURVIVING, or RE-ANCHORED, `tests/api/test_evidence_mechanisms.py` is updated to assert what is now true of those seeds, and a fixture that no longer has an anchor is retired with its reason in the audit rather than silently weakened.
- [ ] `scripts/record_ml_corpus.sh`'s pin block and `REQUIRED_PROMPT_VERSIONS` move to the baseline-7 substrate and the v4 template map, the measured leg durations replace the baseline-6 figures, `replays/ml_corpus/README.md` is refreshed end to end (substrate, env, duration, the canary-denominator restatement), and `splits.json` is regenerated non-degenerate under the unchanged `seed % 5` rule for both corpus sets.
- [ ] Each set's `tournament-eval-report.json` and `results-rubric-score.json` are regenerated from the new bytes by the committed recipes, the served rubric reads FRESH (producer fingerprint equals loader fingerprint), and `FEATURED_GAMES` is re-curated by watching the new games: a seed is kept only where its blurb is still true of the recorded game, every replacement carries a hand-written spoiler-free line under the binding rule at `ReplayPicker.tsx`:95-101, and `tests/api/test_sets.py`'s seed pin is updated to the new list with the curated head named.
- [ ] The record audit carries the co-intervention by name with its attribution consequence, the FSM provenance (`fsm-default` in every MANIFEST `policy` cell, with the repaired mover's identity carried by the `git_sha` column), the DURATION ACTUALLY TAKEN per leg against the pre-record projection, every seed that had to be re-recorded with why, the `(deadline_default)` watch item's status, and one section stating what this record does NOT discharge (the ML re-ground, the ladder-tip prose, the results table).
- [ ] `bash scripts/verify_samples.sh` reports 100/100 on the new samples bytes and `uv run python scripts/verify_ml_evidence.py` (full, not `--fast`) reports reconstruction 300/300 across the four declared sets, both outputs pasted into the PR Summary.
- [ ] The record audit contains the exact sentence form scripts/check_doc_facts.py parses ("the ladder tip stands at baseline N" with N = 7 on ADOPTED, 6 on FINDING) and _LADDER_TIP_AUDIT points at it; README's provenance paragraph and ladder-tip sentence are re-derived from the new MANIFESTs; .env.example's always-ON note names every graduated key (check_doc_facts green).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Follow the 18.12 runbook then the 18.13 runbook verbatim in structure; the only novelty is that they are fused into one record and one PR, and that the graduation branch is conditional on arithmetic rather than on a prior ruling.

Step 1 — plan the clock before touching anything. Take the smoke report's tokens-per-meeting-call figure, divide by the baseline-6 figure for the same call kind, and scale the committed legs (4p1i 0h45m for 50, 9p2i 19h26m for 150). Write the projected four-leg total into the audit's §0 BEFORE recording, so the actual can be read against a number you committed to in advance. If the projection exceeds the operator's available window, record in the memo's order and stop at a set boundary — the memo's power argument is the reason the corpus 9p2i leg outranks both 4p1i legs.

Step 2 — this is a LOCAL operator session on the owner's machine, not a dispatch container (the 18.13 choice, made to remove container-reclaim risk from a multi-day leg). Run `bash scripts/setup_env.sh`, then export ONLY the recording environment plus the eight lever exports the slate needs, and nothing else. Run the recorder's `--expect-levers` preflight on EVERY leg — it exists precisely so a stale or forgotten export cannot silently record the wrong substrate — and confirm `impostor_roll_call` is UNSET before each leg. Preview with `--dry-run` first.

Step 3 — record, gate, push, repeat. After each leg: validity gate with the two flags, reconstruct byte-identically under a BARE environment, diff the recorded substrate snapshot against the intended slate key by key, then commit and push that seed range. A seed whose opening defaults, or whose recorded stamp disagrees with the slate, is a FAILED recording and re-records — that is the standing rule and it does not bend for the clock. Log every re-record with its cause as you go; reconstructing that list afterwards from shell history is how records lose their provenance.

Step 4 — read before you flip. Compute all four sets' cells with the three instrument emitters, write the audit's read section end to end, and only then apply the decision rule. Applying the rule to a partially-written table is how "adopt anyway" happens. If the rule says FINDING, the audit's verdict line says FINDING, the levers stay toggles, and the PR is still merged — the bytes and the read are the deliverable.

Step 5 — the graduation flips are two-line edits and nothing more. Each resolver becomes an unconditional `return True` with one provenance line naming this record; the key moves between the two tuples in `orchestrator/replay.py`; the mechanism bodies are not touched (they froze at the stamp registration) and the dead OFF branches are deleted by the graduation-sweep task, not here. Re-run the substrate snapshot fixtures immediately after the move — a bare-environment snapshot that no longer equals the recorded stamp is a same-hour bug, not a same-week one.

Step 6 — the floor block. Copy the baseline-6 block's shape exactly: the three `FloorPin` values with their raw numerators in the comment, the population-relative flag, and the derivation worked through to the equality point. Then prove self-consistency by scoring the record against its own floors and pasting the PASS. A numerator of 1 or 0 makes its gauge ADVISORY under the standing rare-event rule; say so in the comment rather than pinning a floor that cannot fail.

Step 7 — the re-pin sweep, done as a census rather than a chase. Start from `grep -rln 'replays/samples\|replays/ml_corpus' tests/` (37 files at HEAD) plus the Phase-20 instrument tests, list every asserted constant that reads committed bytes, and work the list top to bottom keeping the old value in a comment beside the new one. Run the suite in a CLEAN worktree — a concurrent session in the same checkout produces false failures on the import-linter and hash-pin gates, which is exactly the noise that makes a sweep of this size go wrong.

Step 8 — re-curate the featured strip LAST, by watching the new games rather than by pattern-matching seed numbers. Some of the current entries exist because they were injustices; if the levers worked, those blurbs are now false, and a false blurb on the demo's front strip is worse than a plain one. Keep a seed only where its line is still true, write replacements from the recorded game, hold the spoiler rule, and update the pin.

Step 9 — the audit is the deliverable that outlives the bytes. Mirror the baseline-6 audit's section shape: pre-registration read, validity gate, the cell-by-cell before/after, the referee, the provenance tuple, the permanent record, the decisions, and a method section that reproduces every derived figure offline at $0. Cite the audit for the record's truth, never this PR's body — PR bodies quote first-cut numbers and have already caused one downstream citation error in this repo's history.

**Integration risk:**

The widest byte-coupled re-pin sweep the repository has run: every committed-bytes pin moves at once, across six test directories and roughly 37 files at HEAD plus the ~20 cells this phase added. Budget the sweep explicitly as its own leg, and run the full suite in a clean worktree before the record commit is cut.

The wall clock is the second risk and it is systematically under-estimated. The committed baseline-6 legs sum to ~22h54m for 200 corpus games; the four-set record is 300 games, and the v4 prompt set adds tokens to every meeting call. Measure on the smoke and re-plan in writing before starting; do not plan against the title's figure.

A partial record is not a baseline. Checkpoint-push each completed seed range, never commit a half-set as canonical, and if the window closes mid-phase stop at a set boundary with the audit stating which legs exist and which do not.

Two couplings fire the moment the levers reclassify, and both are outside this contract's given scope — see the assembler notes. `check_lever_registry` requires a graduated key to be named in the `.env.example` always-ON note and to appear nowhere as an `AILIBI_*=` line, and `check_sample_provenance` re-derives README's refresh date, win rates, model and prompt-set version from the sample MANIFESTs this record rewrites. Both are asserted against the real repository by `tests/scripts/test_check_doc_facts.py`, which `uv run pytest` runs, which `bash scripts/check.sh` runs. Resolve the scope question before dispatch rather than discovering it at the end of a 27-hour operator window.

Finally, the doctrinal risk: if the decision rule says FINDING, resist the temptation to adopt anyway. Publishing a record that missed its own pre-registered bars, and saying so, is the single most valuable artifact this phase can produce.

**Ready-to-paste prompt:** `agent_prompts/task-20-36-baseline-7-record.md`

## Wave 3 — presentation on corrected bytes

### Task 20.37 — Retire means delete: the post-record graduation sweep and the old accept-and-ignore residue
**Branch:** `phase-20-graduation-sweep`
**Depends on:** 20.36 — the adopting record is the ruling that says which levers graduated, and a lever may only be deleted after its verdict exists; the record's own graduation flips are the commit this sweep deletes on top of, so it cannot run in parallel with them
**Section refs:** C-64 and C-104 in `audits/review-2026-08-19/B/collated-findings.md` §4 and §5; RC6 in `audits/review-2026-08-19/D/FINAL-synthesis.md` §1 ("the render-version stamp, plus one deletion pass"); the per-area sources `audits/review-2026-08-19/B/repo-health-architecture.md` §2 F6, `audits/review-2026-08-19/B/agents-memory.md` §2 F4, `audits/review-2026-08-19/B/meetings-transcript-voting.md` §2 F5, `audits/review-2026-08-19/B/meetings-manager.md` §2 P1-3, `audits/review-2026-08-19/B/orchestrator.md` §2 (the `suspicion_graph_for_meeting` dead-kwarg leg). Anchors RE-VERIFIED at HEAD: the nine accept-and-ignore resolvers `agents/memory/store.py:189`, `agents/memory/beliefs.py:190,224,292,407`, `meetings/constants.py:54`, `meetings/transcript.py:1362,1389`, `meetings/manager.py:859` (200 source lines in total, each ending `del env  # retired: the lever is unconditional, no environment is consulted`); their nine `ENV_*` constants `agents/memory/store.py:186`, `agents/memory/beliefs.py:187,221,289,404`, `meetings/constants.py:51`, `meetings/manager.py:856`, `meetings/transcript.py:1354,1359` and the nine matching `__all__` entries; the thirteen production read sites `agents/memory/store.py:280,286,1632,1652`, `agents/memory/beliefs.py:1463,1465,1502,1826,1835,1841`, `meetings/manager.py:1185,1759,2018,2448`, `meetings/transcript.py:1554,1555`, `orchestrator/game.py:2713`; the dead private-helper parameter `meetings/transcript.py:2380-2385` with its own "survives only for direct callers" comment at `:2407-2410`; the stamp registry `orchestrator/replay.py:531-545` (`_RETIRED_ALWAYS_ON_LEVERS`, thirteen keys) and `:570-572` (`_TOGGLEABLE_LEVER_RESOLVERS`, one live entry); the rule this task amends, `AGENTS.md:62-75` (Graduation sweeps) beside craft rule 3 at `AGENTS.md:91-94`; `.env.example:68-97` (the graduated always-ON note); the test residue `tests/agents/test_absence_prior.py:166-216`, `tests/agents/test_beliefs_hard_evidence_gate.py:86-115`, `tests/agents/test_beliefs.py:2634-2660`, `tests/agents/test_episodic_ids.py:383-458`, `tests/meetings/test_citation_gate.py:127-158`, `tests/meetings/test_manager.py:475-512` and `:772` (`TestRollCallOffPath`, whose docstring says the round is skipped while its test asserts the round fires), `tests/meetings/test_contradictions.py:1531-1617`
**Complexity:** Medium
**Record impact:** post-record
**Measurement:** `grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator | wc -l` reads 11 at HEAD and must read 2 plus one per Phase-20 lever the record did NOT adopt; `grep -rnE 'ENV_(ROLL_CALL_ROUND|WHEREABOUTS_INTERIOR_FLAGS|VENT_PLACEMENT_CONTRADICTIONS|ABSENCE_PRIOR|CITATION_GATE|HARD_EVIDENCE_GATE|OBSERVATION_ID_RENDERING|EVIDENCE_QUALITY_LIFT|REPORTER_EXCULPATION)' tests/ | wc -l` reads 152 at HEAD and must read 0; `grep -rnE "accepted and ignored|no longer read|now always True" --include="*.py" agents meetings orchestrator | wc -l` reads 29 at HEAD and must read 0; `bash scripts/verify_samples.sh` stays 100/100 and `bash scripts/check.sh` is green.

Graduating a lever in this repo has so far meant deleting the env *read* and keeping the
*shape*. Nine resolvers of the form `def x_enabled(env: Mapping[str, str] | None = None) ->
bool: del env; return True` survive at HEAD — 200 source lines, each carrying a 12-to-31-line
docstring explaining a switch that no longer exists — with nine `ENV_*` constants "retained
for naming provenance", nine `__all__` exports, and thirteen production read sites that still
spell an unconditional behaviour as `if always_true():`. The review reproduced the tax three
ways and all three numbers reproduce byte-for-byte at HEAD today: 29 comment lines in
`agents/`, `meetings/` and `orchestrator/` say "accepted and ignored" / "no longer read" /
"now always True", and 152 lines of the test suite set environment variables that no
production code reads (`audits/review-2026-08-19/B/repo-health-architecture.md` §2 F6 — the
review's own grep, re-run by this contract with the same result). Of those 152, 94 live in a
single 538-line test class (`tests/orchestrator/test_replay.py:212-749`) whose job is to
assert that constants are constant.

One correction to the register, made at HEAD and to be carried into the phase file: C-64
counts **ten** accept-and-ignore resolvers, listing `agents/strategic/prompts/loader.py:264`
and `orchestrator/replay.py:110` among them. Both are LIVE — they read
`AILIBI_IMPOSTOR_ROLL_CALL` and return its parsed value; the 18.10 impostor-answer arm is
still default-OFF because the CREW-ONLY ruling did not ship it. The true count of
accept-and-ignore resolvers is **nine**, and the eleven-hit `def *_enabled(` grep is nine
dead plus two live. Likewise C-64's "13 `ENV_*` constants" is the size of
`_RETIRED_ALWAYS_ON_LEVERS`, not the constant count: the four Phase-13.5 levers were swept
properly at Task 14.9 and left nothing behind, which is the existence proof that this sweep
is achievable.

The class doubles the moment the adopting record lands. If the pre-registered decision rule
adopts baseline 7, the eight Phase-20 levers built default-OFF in wave 2 have their bodies
hard-return `True` and their keys move into `_RETIRED_ALWAYS_ON_LEVERS` — by construction
they become exactly the same residue, in exactly the same three modules. This task is the
first execution of craft rule 3 (`AGENTS.md:91-94`, "Retire means delete"), applied to both
generations at once, and it closes the loop by amending the older Graduation-sweeps rule at
`AGENTS.md:62-75`, which today demands only a *prose* sweep and explicitly blesses keeping
the function: *"the lever stays in the substrate stamp for provenance"*. That sentence is
true of the stamp KEY and false of everything else, and it is why nine dead functions
accumulated across five graduations.

Nothing observable moves. Every deleted branch is the branch production already takes, so the
committed bytes are the invariant and the gate is `verify_samples.sh` at 100/100 plus the
prompt byte-golden: if either moves, a deletion was not equivalent. The substrate stamp is
untouched — the keys stay in `_RETIRED_ALWAYS_ON_LEVERS`, `substrate_flag_snapshot()` keeps
stamping every one of them `True`, and a legacy replay stamped OFF keeps failing loud. What
goes is the resolver, its `env` parameter where nothing else reads one, the dead `if`, the
`ENV_*` constant, and the tests that pin a parameter — including the test class whose
docstring at `tests/meetings/test_manager.py:772` states the opposite of what its body
asserts (C-104's flagship example).

**Files in scope:**
- agents/memory/beliefs.py; (delete `evidence_quality_lift_enabled`, `reporter_exculpation_enabled`, `hard_evidence_gate_enabled`, `absence_prior_enabled`, their `ENV_*` constants and `__all__` entries, and collapse the read sites at :1463-1465, :1502, :1826, :1835, :1841; one history line per deleted lever)
- agents/memory/store.py; (same for `observation_id_rendering_enabled` and the `hard_evidence_gate_enabled` import; collapse `ids_on` at :280-286 and `gate_on` at :1632-1652; plus every Phase-20 store lever the record adopted)
- meetings/transcript.py; (same for `whereabouts_interior_flags_enabled` and `vent_placement_contradictions_enabled`; collapse :1554-1555 and delete the `whereabouts_interior_flags` parameter and its dead `False` branch at :2380-2410; plus every Phase-20 transcript lever the record adopted)
- meetings/manager.py; (same for `roll_call_round_enabled`; collapse :1185, :1759, :2018, :2448 and drop the `env` plumbing that only fed them; plus every Phase-20 manager lever the record adopted)
- meetings/constants.py; (delete `citation_gate_enabled`, `ENV_CITATION_GATE` and their `__all__` entries; `UNCITED_ZERO_FLAG_EJECT_MARKER` and the threshold constants stay)
- agents/strategic/prompts/loader.py; (the live 18.10 resolver STAYS — only its dangling `:func:` cross-references to deleted siblings at :253, :269, :271 are rewritten)
- orchestrator/replay.py; (the keys stay in `_RETIRED_ALWAYS_ON_LEVERS`; the resolver imports and any identity bindings for graduated levers go)
- tests/agents/; (the resolver-only classes and the tautology halves deleted; behaviour tests kept)
- tests/meetings/; (same, plus the new deletion-guard pin and its planted counter-case)
- AGENTS.md; (the Graduation-sweeps rule amended to "delete the mechanism, keep the stamp key and one history line", naming this task as its precedent)
- .env.example; (the newly graduated keys join the always-ON note; no lever gains a variable)
- orchestrator/game.py; (the hard_evidence_gate_enabled import and read-site; the stale narration beside it)
- tests/orchestrator/test_replay.py; (the graduated resolver/constant imports and parameter pins)
- meetings/render_contract.py; (one dangling resolver reference)
- eval/meeting_quality.py; (one dangling resolver reference)
- tests/eval/test_meeting_quality.py; (same)

Coordination note (routed from PR #384): eight comment-only forward references in the lever home modules are now FALSE — each reads 'Not registered in orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS: Task 20.33 wires the whole Phase-20 slate…' at agents/memory/store.py:265-267, :298-299, :349 block, :382-383; meetings/transcript.py:1567-1568, :1603-1604, :1643-1644; meetings/manager.py:924-925 (lines as of fc5cf719). Sweep them here with the other residue (comment-only, re-verify lines at HEAD first).

**Files NOT in scope:**
- any lever the record did NOT adopt (it stays a live env-gated toggle with its resolver, parameter, tests and `.env.example` entry intact — the 18.10 impostor arm is the standing example)
- replays/ (the committed bytes are the pin, not an edit target; `verify_samples.sh` green is the invariant this task must not move)
- orchestrator/replay.py's `_TOGGLEABLE_LEVER_RESOLVERS` semantics and `substrate_flag_snapshot` behaviour (registration is not re-litigated here; only imports of deleted symbols change)
- the prompt templates under agents/strategic/prompts/qwen3_6_27b/ (no task except the single prompt-set bump may edit template bytes)
- tasks/ and agent_prompts/ (historical contracts record what was true when they were written and are never retro-edited)

**Definition of done:**
- [ ] Zero accept-and-ignore resolvers remain for graduated levers: a new AST-walking pin in `tests/meetings/test_lever_registry.py` parses every module under `agents/`, `meetings/` and `orchestrator/` and fails on any function whose name ends `_enabled` and whose body neither reads its `env` argument nor returns anything but a bare `True`; the pin ships with a planted counter-case (a fixture module written into `tmp_path` carrying exactly that shape) proving it bites.
- [ ] No `if <graduated>_enabled():` branch survives: each of the thirteen verified read sites is replaced by its always-taken side, with `ids_on`, `gate_on`, `lift_enabled`, `render_reporter` and the `absence_prior` disjunct in `meetings/manager.py:2448` folded into unconditional code, and `meetings/transcript.py::_detect_alibi_vs_sightings` loses its `whereabouts_interior_flags` parameter along with the `False` branch its own comment describes as reachable only by direct callers.
- [ ] The nine graduated `ENV_*` constants and their `__all__` entries are deleted; the nine snake_case keys remain in `orchestrator/replay.py::_RETIRED_ALWAYS_ON_LEVERS`, `SUBSTRATE_FLAG_KEYS` is unchanged in content and order, and `substrate_flag_snapshot()` in a bare environment still stamps every retired key `True` — pinned by one consolidated test that replaces the nine per-lever repeats.
- [ ] An `env` parameter survives on a public function only where a LIVE resolver still reads it: `render_for_prompt`, `detect_contradictions`, `apply_contradiction_rule`, `apply_meeting_evidence_rules`, `_build_belief_lines`, `_suspicion_graph_with_contradictions` and `TacticalAgent.suspicion_graph_for_meeting` each either keep `env` with a named live reader or lose it, and the PR states which and why for each.
- [ ] The test residue is gone and the keepers survive: the seven resolver-only classes named in Section refs are deleted, `TestRollCallOffPath` at `tests/meetings/test_manager.py:772` is deleted or renamed so no test name or docstring describes an OFF path that cannot exist, `test_marker_literal_pinned_exactly` and the behaviour halves of `TestObservationIdRenderLever` are preserved verbatim, and the three ON-path assertions in `tests/agents/test_impostor_answer_arm.py` are untouched because that lever is live.
- [ ] The three Measurement greps read their target values and the PR Summary pastes all three with before/after; the default pytest tier is smaller by the deleted line count, which the PR quotes from `git diff --stat`.
- [ ] `bash scripts/verify_samples.sh` reports 100/100 and `tests/meetings/test_prompt_byte_golden.py` is green over every committed meeting; the golden still fails on a one-byte perturbation of a template body, demonstrated in the PR, so the no-behaviour-moved claim rests on a gate that can fail.
- [ ] `AGENTS.md`'s Graduation-sweeps section states the amended rule — delete the resolver, its parameter, the dead branch and the parameter-pinning tests; keep the stamp key and one history line; the prose sweep remains the smaller half — and names this task as the precedent, with craft rule 3 cross-referencing it instead of restating it.
- [ ] `.env.example` lists every graduated lever in the always-ON note with its adopting record, documents no variable for any of them, and still documents exactly the live toggles read from `orchestrator/replay.py::_TOGGLEABLE_LEVER_RESOLVERS`; the existing registry-cross-check test stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Do this one lever at a time, never as a bulk regex pass, and commit per lever so a bisect
lands on a single symbol. The 19.19 deletion pattern applies verbatim.

Step 1 — read the record's verdict first. Open the record audit written by the adopting task
and list, explicitly, which Phase-20 levers graduated. `_RETIRED_ALWAYS_ON_LEVERS` after that
commit is the authoritative list; anything still in `_TOGGLEABLE_LEVER_RESOLVERS` is LIVE and
this task must not touch its resolver, its parameter, its tests or its `.env.example` entry.
Write that list at the top of the PR description before editing anything.

Step 2 — per symbol, grep the consumers before deleting. For each resolver name and its
`ENV_*` constant run the blast-radius grep over the whole tree, not just the files in scope,
and read every hit. Expect hits in three shapes: real read sites (collapse them), `__all__`
entries (delete), and prose `:func:` cross-references in modules that are not in scope
(rewrite where the module is in scope, and report the rest rather than widening scope
silently). Two known consumers sit outside this contract's files and are called out in the
notes below; if a third appears, stop and ask.

Step 3 — collapse, do not comment out. `ids_on = observation_id_rendering_enabled(env)`
followed by `if ids_on:` becomes the body of the `if`, dedented, with the guard gone. A
disjunct like `or (evidence.absent and absence_prior_enabled(env))` becomes `or
evidence.absent`. A ternary like `reporter_id if reporter_exculpation_enabled() else None`
becomes `reporter_id`. After each collapse run the module's own test file plus
`tests/meetings/test_prompt_byte_golden.py` before moving on — a wrong collapse shows up as a
prompt-byte diff immediately, and finding it one lever at a time costs minutes instead of a
bisect.

Step 4 — the parameter is the subtle part. `env` is threaded through several public
signatures purely to reach these resolvers. Delete it only where the grep proves no live
resolver is reached from that call chain; where a Phase-20 lever survived the record, `env`
survives with it. Leaving a parameter that nothing reads is the exact defect this task
exists to remove, and deleting one a live lever needs breaks the toggle silently, so record
the decision per signature in the PR.

Step 5 — the tests. Delete whole classes where the class exists only to assert a constant;
inside mixed classes delete only the tautology methods and keep the behaviour ones. Replace
the nine per-lever stamp repeats with one test that asserts the full retired tuple stamps
`True` under a bare mapping, an explicit "0", a junk value and the ambient process
environment — one test, four cases, the whole registry. The new AST guard belongs beside it;
give it a planted bad module in `tmp_path` so it is a gate rather than prose.

Step 6 — the docstrings that survive. Each lever's mechanism keeps one trailing provenance
line naming its adopting record, and nothing more; the 12-to-31-line narrations go with the
functions. Do not migrate the narration into the surviving mechanism docstring — that
converts a deletion into a move and the reader is no better off.

**Ready-to-paste prompt:** `agent_prompts/task-20-37-graduation-sweep.md`

### Task 20.38 — The results on corrected bytes: re-curated featured games, the before/after column, the ML page amended
**Branch:** `phase-20-results-after-record`
**Depends on:** 20.13, 20.20, 20.36 — the results table and the ML page must exist before a column can be added to them; the architecture and contract-exhibit sections settle the README shape this task edits around; and the record must be committed before any of its numbers can be quoted.
**Section refs:** audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 rows 3.1 and 3.2 ("the results table gains its before/after column … *pre-registered, measured, reported — including the part that did not move*") and §7 (the post-wave-2 pitch paragraph; endorsement edit (b): every volatile number carries its baseline stamp from day one "so wave 3 adds a column instead of rewriting the page"); audits/review-2026-08-19/C/collated-portfolio.md §A6 (state the results once, plainly — the enabling move this task completes) and §B3 (the reading guide is 3,239 words / 378 lines against an advertised five minutes, with `file:line` anchors already drifting); byte-coupled front-door anchors re-verified at HEAD — README.md:84 (the status/ladder-tip paragraph), README.md:149 (the single sample-provenance paragraph: `regenerated 2026-07-20`, the recording model, the `qwen3_6_27b` `v3` prompt set, "34% (4p1i) and 30% (9p2i)"); docs/reading-guide.md:39-50 (the numbers table), :45 (the row that states in prose that only *the README's* copy of the win rates is re-derived), :101-105 and :109-117 (the featured table and its claim to mirror `FEATURED_GAMES` exactly), :175-184 (the vent cross-tab, 70/95 meetings); scripts/check_doc_facts.py:87 (`_README` — the only document the checker reads), :89 (`_LADDER_TIP_AUDIT` = `audits/audit-phase-18-close.md`), :99-101 (the `ladder tip stands at baseline N` parse), :160-169 (`check_facts`), :172 (`check_sample_provenance`), :360 (`check_ladder_tip`); the pins the record moves — tests/eval/test_deduction_metrics.py:163 and :237 (the proof / non-proof cells; pooled 310/310 = 1.000 and 46/125 = 0.368 at audits/audit-phase-19-close.md:233), tests/eval/test_vj_instruments.py:509 (520/520 citation compliance), tests/api/test_sets.py:431 and :376 (the featured-seed and spoiler-free pins), frontend/src/components/ReplayPicker.tsx:102 (`FEATURED_GAMES`).
**Complexity:** Small
**Record impact:** post-record (the record's bytes, MANIFESTs and re-pinned cells already exist; nothing recorded moves here)
**Measurement:** `uv run python scripts/check_doc_facts.py` green; `uv run pytest tests/scripts/test_check_doc_facts.py tests/api/test_sets.py -q` green, including the new perturbation cases — a stale reading-guide win rate, a featured row the picker no longer carries, and a moved figure quoted without its baseline stamp each fail the check.

This is the payoff task. The phase pre-registered its bars before any fix existed, measured them on a
23-hour record, and now has to report the answer — including the part that did not move. The front
door is still quoting the previous baseline: README.md:149 says the samples were `regenerated
2026-07-20` on the `qwen3_6_27b` `v3` prompt set with impostor win rates "34% (4p1i) and 30% (9p2i)",
README.md:84 names the ladder tip at baseline 6, and docs/reading-guide.md:39-50 repeats both win
rates at :45 while crediting the guard to "the README's copy", beside two further rows the record
touches: 520/520 citation compliance (tests/eval/test_vj_instruments.py:509) and the 87% vent
cross-tab at :175-184 (70 flagged meetings against 95 unflagged). The pooled deduction cells the
results table states — 310/310 = 1.000 with proof against 46/125 = 0.368 without
(audits/audit-phase-19-close.md:233, pinned by tests/eval/test_deduction_metrics.py:163 and :237) —
are re-derived on the new bytes by those same pins. Every one of those is a cell the record either
moved or deliberately left standing. The whole argument of this phase — that a measurement made
after a pre-registration is worth more than a measurement made after a result — is only visible if
both columns are on the page.

The mechanical work is small because the earlier tasks built for it: the results table already stamps
each volatile row with its baseline and record date, so the edit is one added column and a header,
not a rewrite. What makes the task worth a contract is the discipline around the numbers. Quote; do
not compute. Every figure in this diff comes from `audits/audit-phase-20-baseline-7.md` or from the
test pin that owns it, and a figure with no pin does not go in the front door. The review-measured
bars the phase registered — false crew `whereabouts` 20.5%, sole-`alibi_vs_sighting` precision 14.6%,
grounded sighting side 36.5%, adjacent-room STRONG share 63.2% (all review-measured over the
committed baseline-6 bytes, re-pinned as committed cells by the honesty instrument set) and the
solvability y-axis (killer inside the crew's own candidate set in 581/626 body meetings = 92.8%, a
correct singleton in 103 of 109, and 61 of 354 ejections landing on a player the crew's pooled
perception had already cleared — same provenance) — are read off their new pins here, never
re-derived by hand.

The verdict sentence is the other half. The record's decision rule produced one of two outcomes, and
this task publishes whichever one happened in one sentence titled by its result: ADOPTED, in which
case baseline 7 is the ladder tip and `scripts/check_doc_facts.py:89` must point at the audit that
records it; or FINDING, in which case the record is published in full, the tip stands where it stood,
and the front door says so. The FINDING sentence is the stronger of the two and must not be softened
or buried — a project whose thesis is that it does not publish numbers it knows are confounded
cannot flinch at publishing a bar it missed. The decision itself belongs to the record audit; this
task states it and links it, and re-argues nothing.

There is one guard gap to close while the numbers are being touched. `scripts/check_doc_facts.py`
reads exactly one document (`_README` at :87, the only path threaded through `check_facts` at
:160-169), so the same win rates, refresh date and ladder-tip claim repeated in
docs/reading-guide.md are unguarded — the guide's own row at :45 says as much in prose, crediting the
check to "the README's copy". That is precisely the drift class the checker exists to kill, and after
a record it is the class most likely to fire: the guide and the ML page now repeat figures whose
committed source just moved. Widening the checker to the front-door document set, with a perturbation
test per new check, is what stops this page rotting the next time a baseline lands.

Finally, docs/ml-program.md needs an honest amendment rather than an update. The impostor mover's
target-selection defects are repaired now, so the comparator the Phase-17 and Phase-18 win edges
(+0.12 to +0.30) were measured against no longer exists in that form — and nothing was retrained, so
those figures were not re-measured. The page states that plainly: the erratum stands, the numbers are
stale by construction, and re-grounding them is a future owner decision, not a quiet edit.

**Files in scope:**
- README.md; (the results table's before/after column from audits/audit-phase-20-baseline-7.md; the status line; the demo sentence)
- docs/ml-program.md; (the Phase-20 read: what moved, what did not, the comparator note now that the FSM is repaired)
- docs/reading-guide.md; (the numbers table and the cross-tab re-quoted from the new pins; the featured table mirrors FEATURED_GAMES)
- docs/history.md; (Phase 20 row)
- scripts/check_doc_facts.py; (the new numbers checked against the new pins)
- tests/scripts/test_check_doc_facts.py

**Files NOT in scope:**
- replays/ (the record is done; no recorded byte moves in this PR)
- frontend/ (the featured list was re-curated at the record; the bundle redeploys via Pages)
- tests/api/test_sets.py (the featured-seed pin belongs to the record's re-pin sweep; this task reads it and mirrors it, never edits it)
- audits/ (the record audit and the pre-registration are quoted, never rewritten; records get dated errata from their owning tasks)
- agents/, meetings/, orchestrator/, eval/ (no behaviour and no instrument changes; every cell is read from an existing pin)
- agents/strategic/prompts/ (prompt templates are edited by the single prompt-set bump task and by nothing else)
- docs/media/ and docs/lessons.md (the hero media and the lessons page are later tasks in this wave)

**Definition of done:**
- [ ] Every figure in README.md, docs/reading-guide.md and docs/ml-program.md that the record moved is re-quoted from its new pin, carrying the baseline-7 stamp with its baseline-6 value beside it in the before/after column; the PR body lists each row with the pin or audit section it came from, and no figure in the diff was computed by this task.
- [ ] The README states the record's verdict in one sentence titled by its result — ADOPTED, naming the new ladder tip, or FINDING, naming the bar that did not clear — and links `audits/audit-phase-20-baseline-7.md`; the sentence names at least one pre-registered bar that did not move.
- [ ] README's sample-provenance paragraph agrees with the new MANIFESTs on the refresh date, recording model, prompt-set family and version and both per-set impostor win rates, and every "ladder tip" sentence names the baseline the owning audit records; `scripts/check_doc_facts.py:89` points at that audit, and `uv run python scripts/check_doc_facts.py` is green at HEAD.
- [ ] `scripts/check_doc_facts.py` checks the moved facts wherever the front door repeats them — the win rates, the refresh date and the ladder-tip claim in docs/reading-guide.md and docs/ml-program.md, not README alone — and each new check has a perturbation case in tests/scripts/test_check_doc_facts.py that fails when the fact is drifted in the newly-covered document; docs/reading-guide.md:45's prose about which copy is guarded is updated to match.
- [ ] The reading guide's featured table equals `FEATURED_GAMES` seed-for-seed and in curated order, pinned by a check that parses the picker source and fails on an added, removed or re-ordered row; the guide's blurbs stay spoiler-free under the existing rule.
- [ ] docs/ml-program.md carries the Phase-20 read — which pre-registered bars moved, which did not, and the win split as the observed-not-gated secondary — plus the amended comparator note: the FSM target-selection defects are repaired, the Phase-17/18 win edges were measured against the defective comparator, nothing was retrained, so the erratum stands and the figures are stale by construction.
- [ ] docs/history.md gains the Phase-20 row in the file's existing shape, linking the record audit.
- [ ] A grep for each baseline-6 figure the record moved returns only before-column cells explicitly stamped baseline 6; the PR quotes the grep.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — build the number ledger before touching a document. Read
audits/audit-phase-20-baseline-7.md cell by cell and, for each figure, find the pin that owns it:
tests/eval/test_deduction_metrics.py for the proof / non-proof cross-tab, tests/eval/test_evidence_honesty.py
for the honesty bars, tests/eval/test_solvability.py for the y-axis, tests/eval/test_vj_instruments.py:509
for citation compliance, the set MANIFESTs for win rates and provenance, scripts/verify_samples.sh for
the reconstruction claim. Put the ledger in the PR body first. Anything without a pin does not enter
the front door — it goes in the PR as a question instead.

Step 2 — the before/after column is a column. The results table already stamps each volatile row
with its baseline and record date, so add one cell per row plus a header and leave the source column
untouched. Rows the record did not move still get a cell, and it says so.

Step 3 — the verdict sentence is one sentence, titled by its result, immediately followed by the
link to the record audit. Under FINDING, resist every instinct to add a mitigating clause; the
record audit already carries the reasoning and the next decision.

Step 4 — extend the fact checker by widening the documents it reads rather than by copying checks.
`check_sample_provenance` and `check_ladder_tip` already take the document text as a parameter, so
the cheap change is a front-door document tuple threaded through the claim-shaped checks (the
`_WIN_RATE_CLAIM`, `_REGENERATED_DATE` and `_LADDER_TIP_PHRASE` scans) while the paragraph-anchored
provenance check stays bound to README, where the one provenance paragraph lives. Keep the error
strings naming the file and line they came from. Every new check needs its perturbation test, and the
existing fixture pattern in tests/scripts/test_check_doc_facts.py (copy the tree, substitute one
string, assert the failure) is the shape to follow.

Step 5 — the featured mirror. Parse `FEATURED_GAMES` out of frontend/src/components/ReplayPicker.tsx:102
the way tests/api/test_sets.py:58-78 already does, compare the parsed set/seed sequence against the
guide's table rows in order, and fail loud on any difference. Do not edit the picker or the api test:
the curation is the record's, and this task mirrors it.

Step 6 — sequencing. The record's own PR may already have re-quoted the mechanical provenance facts
to keep its gate green. Re-verify each one rather than assuming either way, and leave anything that is
already correct alone; the diff should be the reporting, not churn.

**Ready-to-paste prompt:** `agent_prompts/task-20-38-results-after-record.md`

### Task 20.39 — The hero image: one tick, two truths — and a ten-second clip
**Branch:** `phase-20-hero-media`
**Depends on:** 20.1, 20.3, 20.36, 20.38 (four edges, in the order the ids are listed: the body layer must read engine truth before a still of the map becomes the front door, or the hero paints corpses the engine already deleted; the dock must stop covering the canvas before any capture can contain the map at all, which is the measured cause of the current failure; the adopting record moves the bytes and re-curates the featured list, so the seed, the tick, the agent and the accusation this still names cannot be chosen before it exists; and the README results prose lands first, so this task swaps images into a finished page instead of racing another writer for the same file)
**Section refs:** audits/review-2026-08-19/C/collated-portfolio.md §A3 (the GIF finding, VERIFIED by frame sheet + layout math) + §F4 (the media list: keep the meeting still, re-record the walk, optionally ship MP4/WebM) + §D1 (the ruling: "re-record"); audits/review-2026-08-19/C/p3-frontend-product-engineer.md (the measurement: at the 1000×640 recording viewport the fixed bottom dock covers the PixiJS canvas entirely — canvas top 311 px vs dock top 308 px, page height 1078 px — over all 20 sampled frames; "I never see the map or an agent move"); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 row 3.3 + §7 "The one image"; audits/review-2026-08-19/B/frontend-a.md §F1 (the phantom-body layer the map still would otherwise show); README.md:5 + :7 (the GIF and the caption that promises "the map"), :9 + :11 (the meeting still and its "seed 2, tick 7" caption); docs/media/README.md:7-8 (the asset table), :16-18 ("a screenshot is a claim about the product, and a stale one is a false claim"), :22-25 (the harness deliberately NOT committed), :36-42 (the recorded walk and the 1000×640 recording viewport), :43-55 (the stripped ffmpeg + the Pillow palette note), :57-59 (the size budget); docs/artifacts.md:96 (the registry row `docs/media/` — "1.7 MB / 3 files") enforced against `git ls-files docs/media` by tests/scripts/test_verify_ml_evidence.py:1400-1417; frontend/e2e/journey.spec.ts:302-339 (the fog firewall walk and its controls — the "As-agent" button, "Exit fog", the "Perspective agent" picker, the `perspective=p-N` URL key), :396-431 (the reduced-motion probe); frontend/e2e/bundle.spec.ts:63-80 (`buildBundle` + the `AILIBI_DEMO_BUNDLE_DIR` reuse env), :88-114 (`serveStatic`), :158-198 (the `bundle` fixture); frontend/playwright.config.ts (testDir `./e2e`, `video: "off"`, one worker, `outputDir: "./e2e/.artifacts"`); frontend/src/lib/playback.ts:381-388 (the eight round-tripping URL keys — set / game_id / tick / perspective / beliefView / selectedAgent / selectedMeeting / reveal), :423 (`parsePlaybackParams`); frontend/src/components/MapView.tsx:102-105 (`prefersReducedMotion` gates the tween, the kill flash and the vent dive), :229 (`buildBodyStatesByTick`), :455 (`KillFlash`); frontend/src/components/MapToolbar.tsx:134-173 (the Omniscient ↔ As-agent group and the agent picker); frontend/src/App.tsx:326-346 (the perspective banner and "Exit fog"), :1118-1128 (`data-transport-region`); frontend/src/components/ReplayPicker.tsx:102-145 (`FEATURED_GAMES`, seven curated games)
**Complexity:** Small
**Record impact:** post-record — both assets are captures OF the baseline-7 bytes and cannot honestly be shot before the record lands; this task moves no recorded byte and no production source file.
**Measurement:** `cd frontend && AILIBI_CAPTURE_MEDIA=1 npx playwright test e2e/media.spec.ts` regenerates both assets from the committed bytes — two consecutive runs produce a byte-identical `spectator-two-truths.png` and a clip with identical frame dimensions and a duration equal within one recorded frame (the spec prints both), the still is ≤ 400 kB and the clip ≤ 3 MB; `cd frontend && npm run e2e` and `npm run tsc:check` stay green with the media spec reported SKIPPED; `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` green (the `docs/media/` registry row still equals `git ls-files docs/media`); the README rendered on the PR branch shows the still and the clip.

The single asset the most people will ever see does not show the product. The
review verified it by extracting twenty frames and re-measuring the layout at
three viewports: at the 1000×640 viewport `docs/media/README.md:40-42` records as
the recording viewport, the fixed bottom dock covers the PixiJS canvas entirely —
canvas top 311 px against dock top 308 px on a 1078 px page — so
`spectator-journey.gif` shows a picker, a timeline dock, a modal and a finale card,
and never a map or a moving token (audits/review-2026-08-19/C/p3-frontend-product-engineer.md;
collated as §A3 of audits/review-2026-08-19/C/collated-portfolio.md). Meanwhile
README.md:7 promises "the map, an autoplay that stops itself at a meeting". The
autoplay is there; the map is not. By `docs/media/README.md`'s own standard at
:16-18 — a screenshot is a claim about the product, and a stale one is a false
claim — the front door's loudest image is currently a false claim, and the
committed recipe encodes the cause.

The endorsed replacement is not a better GIF. It is a still of ONE tick shown
twice: the omniscient map on the left, the same tick under one crewmate's
As-agent fog on the right, captioned in the shape "Left: what happened. Right:
everything <that crewmate> was allowed to know when it voted", with the
accusation card that crewmate actually wrote at the following meeting composited
underneath (audits/review-2026-08-19/D/FINAL-synthesis.md §7 "The one image").
That frame states all four of this project's stories at once — the observation
firewall, the product, the research premise, and, beside the byline, the
authorship — and it needs no new UI: both halves already render, and
`frontend/e2e/journey.spec.ts:302-339` already pins the firewall behaviour the
right half is a picture of. Beside it goes an 8–10 s clip at ≥1440×900 carrying
the four beats a still cannot: a token moving between rooms, a kill flash, the
transport stopping ITSELF when a meeting starts, and the perspective flipping into
fog (audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 row 3.3). The meeting
still stays — every persona called it the money shot (§F4, §D1) — but it stops
being the only picture that shows anything.

Three of this task's four edges are the reason it is last rather than first. The
dock had to stop covering the canvas before any capture could contain the map;
the omniscient body layer had to start reading engine truth before a front-door
still could be trusted not to paint corpses the engine already deleted
(audits/review-2026-08-19/B/frontend-a.md §F1); and the adopting record both moves
the bytes and re-curates `FEATURED_GAMES` (frontend/src/components/ReplayPicker.tsx:102-145),
so the seed, the tick, the fog subject and the quoted accusation can only be
chosen from the recorded corpus that will actually ship. Choosing them earlier
would publish a caption about a game the repository no longer contains — which is
exactly the failure mode already latent in README.md:11, whose "seed 2, tick 7"
caption describes baseline-6 bytes.

This task also reverses one earlier call, deliberately and with its reason
recorded. Phase 19 chose NOT to commit the capture harness
(`docs/media/README.md:22-25`: "a dozen lines of throwaway Playwright"), and the
consequences are now measurable — an asset nobody can regenerate, a recipe that
silently encodes a broken viewport, and no way to re-shoot the hero when the bytes
move. A composite of two perspectives of one tick is not a dozen lines: it must
prove the two halves are the same tick, it must name the fog subject, and its
provenance is load-bearing to the caption's truth. So the walk becomes a committed,
re-runnable script — gated OFF in the default gate, so the standing Playwright leg
(`npm run e2e`, and the `frontend-e2e` CI job that runs it) costs exactly what it
costs today.

Two honesty constraints ride along. First, the clip's README reference is
verify-then-write: check what GitHub actually renders for the committed reference
form on the PR branch and record the answer; if inline playback does not render
from a repository-relative path, the README falls back to the still linking to
the clip and the regenerated GIF stays as the motion asset — the choice recorded
in `docs/media/README.md`, never assumed. Second, the `docs/media/` row of the
artifact registry states a file count that a test compares against `git ls-files`
at HEAD (docs/artifacts.md:96 against tests/scripts/test_verify_ml_evidence.py:1400-1417),
so changing this directory's file set without restating that row turns
`uv run pytest` red — the count moves in this PR or the PR is not green.

**Files in scope:**
- frontend/e2e/media.spec.ts; (new: a Playwright script that opens the featured seed at the chosen tick in both perspectives, screenshots at 1440×900, and records the clip — re-runnable against the built bundle)
- docs/media/spectator-two-truths.png; (new)
- docs/media/spectator-journey.mp4; (new — the clip, with the GIF retired or regenerated at the correct viewport)
- docs/media/README.md; (asset provenance: seed, tick, viewport, the command)
- README.md; (the hero swap + caption)
- docs/artifacts.md; (the docs/media/ registry row count)
- docs/media/spectator-meeting.png; (re-shot from the re-recorded featured seed so the hero still pictures a game the repository contains)

**Files NOT in scope:**
- frontend/src (no UI change: the body layer, the dock and the fog switcher all landed earlier in this phase — if the capture wants a UI change to look good, the capture is wrong)
- replays/ (reads the committed bytes; nothing re-records here)
- frontend/playwright.config.ts + frontend/package.json (the capture opts itself out from inside the spec; the shared browser config, the worker count and the npm scripts are untouched)
- docs/media/spectator-meeting.png (the existing meeting still: unanimously the money shot at audits/review-2026-08-19/C/collated-portfolio.md §F4 and §D1, and this task neither re-shoots nor retires it)

**Definition of done:**
- [ ] `frontend/e2e/media.spec.ts` is committed, typechecks under `cd frontend && npm run tsc:check` (the `e2e/tsconfig.json` leg), and is INERT in the default gate: the whole file skips unless the capture is explicitly requested, so `npm run e2e` and the `frontend-e2e` CI job report the same passing counts as before this PR plus the skip — the PR quotes both run summaries.
- [ ] The still is one PNG of ONE tick shown twice — omniscient left with the map, rooms and tokens in frame; the same tick under one crewmate's As-agent fog right, lit only where that crewmate could see — with the caption naming the ACTUAL fog subject and the actual moment (not the review's illustrative "p-3"), and the accusation card that crewmate wrote composited underneath. The spec ASSERTS both halves came from the same `tick=` deep-link value and the same `game_id`, so "the same tick" is a checked claim rather than a caption.
- [ ] Each half is captured at ≥1440×900 with the map canvas fully uncovered — the spec asserts the canvas rect is not overlapped by `[data-transport-region]` before it shoots — and the committed PNG is ≤ 400 kB.
- [ ] The clip is ≤ 10 s and ≤ 3 MB and contains, in order, an agent token moving between rooms, a kill flash, the transport pausing itself at a meeting, and the perspective flipping into As-agent fog; it is recorded at ≥1440×900, and the spec asserts each beat happened (a room change between two frames, a kill event at the flashed tick, the pause state, the `perspective=p-N` URL key) rather than trusting the walk.
- [ ] Determinism, pinned by the measurement: two consecutive capture runs produce a byte-identical `spectator-two-truths.png`, and a clip whose frame dimensions are identical and whose duration differs by at most one recorded frame; the spec prints the digests, the dimensions and the duration so the PR can quote them.
- [ ] `docs/media/README.md` states the exact one-line command that regenerates both assets from the committed bytes, plus the full provenance tuple for each (set, seed, game id, engine tick, viewport, fog subject, the bundle build command, and the baseline the bytes come from), and its asset table lists exactly the files committed under `docs/media/` — no row for a retired asset, no asset without a row.
- [ ] README's hero is swapped: the two-truths still leads with a one-sentence caption, the clip replaces the GIF, and every remaining sentence about the media describes what the asset actually shows — the "the map" promise at :7 is either true of the new asset or gone. The clip's reference form is VERIFIED against the rendered README on the PR branch and the PR states what rendered; if inline playback does not render from a repository-relative path, the recorded fallback ships instead.
- [ ] The artifact registry's `docs/media/` row states the committed file set (count and size) for the new inventory, so `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` and `uv run python scripts/verify_ml_evidence.py --complete` stay green — the file-count comparison at tests/scripts/test_verify_ml_evidence.py:1400-1417 reads `git ls-files docs/media` and fails otherwise.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — opt the spec out of the standing gate from inside the file. The Playwright
config's testDir is the whole `e2e/` directory and is not yours to edit, so put a
describe-level skip at the top keyed on an explicit capture variable (for example
`test.skip(process.env.AILIBI_CAPTURE_MEDIA !== "1", "capture-only: regenerates docs/media")`).
That keeps `npm run e2e` and CI byte-identical in behaviour while the file still
typechecks and still lives beside the specs it borrows from.

Step 2 — drive the BUILT bundle, not the dev server, for the same reason
`docs/media/README.md:10-14` gives: the picture is then a picture of the artifact a
reader can build. `bundle.spec.ts` already has both halves of that — `buildBundle`
at :67 (honouring `AILIBI_DEMO_BUNDLE_DIR` so a re-shoot does not rebuild) and the
deliberately dumb `serveStatic` at :88. Copy the shape rather than importing across
specs if importing would drag its fixtures in; the point is one origin serving the
built directory.

Step 3 — address the exact moment by URL, never by clicking to it. `playback.ts`
round-trips eight keys (:381-388), so `?set=…&game_id=…&tick=…&perspective=p-N&selectedMeeting=…&reveal=…`
IS the reproducible address of a frame, and shooting the two halves as two loads of
the same URL differing only in `perspective` is what makes "the same tick" checkable.
Suppress the first-run tour first (`localStorage["ailibi.guidedTourSeen.v1"] = "1"`),
or it auto-loads a second replay mid-capture.

Step 4 — freeze the still, animate the clip. `MapView.tsx:102-105` reads
`prefers-reduced-motion` once and gates the token tween, the kill flash and the
vent dive on it, so a context created with `reducedMotion: "reduce"` renders the
canvas at a fixed phase — that, plus awaiting `document.fonts.ready` before the
shot (the font nudge at MapView.tsx:107-112 re-rasterises Pixi text when the
bundled faces land), is what makes two runs byte-identical. Record the clip in a
separate context at `no-preference`, because there the motion is the content.

Step 5 — composite with Pillow in an ephemeral environment, following the
precedent already recorded at `docs/media/README.md:47-49`
(`uv run --with pillow python …`, which never touches `pyproject.toml`/`uv.lock`).
Shoot three PNGs — omniscient half, fog half, accusation card — and paste them into
one canvas with the caption; a `locator.screenshot()` on the map region and on the
turn `<article>` is steadier than hand-computed clip rectangles. Choosing the fog
subject: it must be a crewmate whose fog is genuinely narrower than the truth at
that tick AND who speaks an accusation at the next meeting, so pick the tick and
the agent together by reading the recorded bytes, not by eye.

Step 6 — the container's Playwright ffmpeg is a stripped demux-only build with no
GIF encoder and no `fps`/`palettegen` filters (`docs/media/README.md:43-46`), and
`recordVideo` emits WebM, so an H.264 file needs a real encoder. Check for one
before assuming (`ffmpeg -hide_banner -encoders | grep 264`); an ephemeral
`uv run --with imageio-ffmpeg …` binary is the same ephemeral-env trick as the
Pillow step and keeps the lockfile untouched. Budget the clip by shortening it, not
by dropping resolution — the whole finding is that a small frame hides the map.
If neither the encoder nor GitHub's rendering cooperates, the honest exit is the
recorded fallback in the definition of done, not a quietly worse hero.

Step 7 — before you commit, re-count. `git ls-files docs/media` is what the
registry row is compared against; add, retire and restate in one PR so the gate is
never red at an intermediate commit.

**Ready-to-paste prompt:** `agent_prompts/task-20-39-hero-media.md`

### Task 20.40 — What was learned, and the review that found it: docs/lessons.md + the curated review publication
**Branch:** `phase-20-lessons-and-review`
**Depends on:** 20.38, 20.39 — the corrected-bytes results page lands first, because the lessons page and the review index both state what the record actually moved and neither may re-derive a figure the results page owns; and the hero media lands on the same front page before this task edits it, so the two front-door edits are ordered rather than racing for the same screen.
**Section refs:** C/B11 with the rulings C/D7 and C/D9 (audits/review-2026-08-19/C/collated-portfolio.md:293-298 — the "What I learned" page, 2–3 screens, raised by four independent persona reads; :379-388 — the process-ceremony ruling, "P2's sharper point … belongs in the 'what I learned' page as an owned lesson, not hidden"; :394-399 — the apparatus-to-result ruling, owned in prose rather than by deleting the record; :564-565 — the sequencing item that puts this page last, "the one thing only the human can write"); audits/review-2026-08-19/C/p2-ml-research-lead.md:82 (the line owned verbatim — "strong on measurement, weak on knowing when to stop building measurement"); audits/review-2026-08-19/D/FINAL-synthesis.md:296 (wave-3 row 3.4 — the themes this page must cover), :297 (wave-3 row 3.5 — publish the review, hook = the retractions, "sequenced here so every finding links to its fix PR"), :360-366 (ruling R6 — yes, in wave 3, curated, titled by the retractions; "not 171 findings dumped"; publishing open self-criticism before any of it is fixed "reads as chaos, not rigor"), :388-391 (ruling R11 — B's P0 is correctness/security/data-loss, A's P0 is believability of the core loop; "Put that sentence in `docs/lessons.md`"), :393-398 (ruling R12 — keep and index the audits tree, trim in-code narration, evict the README's 846 words), :31-56 (§0, the judgment in five sentences), :160 (§2 row 15 — in-code provenance HOLDS, 43 of 44 cited paths resolve), :169-186 (§3 — where the project is stronger than it claims); audits/review-2026-08-19/D/synth-ambition.md:249-262 (FM-5 — the essay's hook, the four retracted headline claims named, and "corrected severities in both directions (C-1, C-31, C-32 up; others down)"), :109-111 (the quotable ratio); audits/review-2026-08-19/D/synth-pragmatic.md:202 (F3 — the same page reached independently by the pragmatic lane); audits/review-2026-08-19/B/repo-health-architecture.md:314-329 (the measured bucket table — 95,824 lines of process narration against 57,776 lines of core product Python, 1.66:1, against 3,358 lines of durable engineering docs), :231 and :296 (43 of 44 cited `audits/`/`tasks/` paths resolve — "maintained, not rotted"); the five retractions in the verdict files that own them — audits/review-2026-08-19/A/verdicts.md:12-22 (G-1 — 44.3% victim-caused / 21.5% witness-caused, the 23 one-tick corridor transits that made 58/79 read as 73.4%, and two of the claim's own exemplars falling in the opposite bucket), :111-131 (G-6 REFUTED — `discovered_by=None` is precisely what makes a body visible; zero real misses corpus-wide; 189/798 measured against the claimed 230/798), :137-147 (G-7 — the agent clock runs +1 against the engine clock on 18,936/18,936 discriminating sightings, so the headline is a two-clock artefact; corrected median 3 and 171/963 = 17.8% landing exactly on the kill tick), :222-228 (G-4's `saw_vent` half REFUTED — 739 of 748 spoken vent claims = 98.8% grounded in the speaker's own recorded field of view, all nine exceptions naming real impostors, seven of them witnessed kills); audits/review-2026-08-19/B/verdicts.md:340-375 (C-33's load-bearing risk REFUTED by experiment — five always-on parity gates, a 1e-9 one-sided perturbation producing 446 mismatches, severity corrected down to P2), :67 (C-32 severity corrected P2 → P1 — the other direction), :415-441 (C-42 — mechanism exact, severity overstated, corrected to P2); audits/review-2026-08-19/B/collated-findings.md:63 (C-32 — the import contracts cover 89 of 383 Python files); anchors re-verified at HEAD `b809b19c` — .importlinter:10, :18, :26, :34 (exactly four contracts), tasks/phase-19.md:7 (the default tier ran 4,621 tests at the Phase-19 close), README.md:47 (the workflow paragraph and its enforcement claim), :53-66 (`## How this is being built` and the two linked workflow artifacts), :194 (the README's only mention of the metric — the identifier `vote_correctness` appears nowhere in README.md, which is the ground the synthesis's own [D-VERIFIED] correction overstated), engine/visibility.py:93 (`body.discovered_by is None and body.room in visible_room_set` — the line that makes G-6's refutation true), docs/reading-guide.md:196-201 (the standing disclosure that the flag doctrine convicts innocents), CONTRIBUTING.md:4 ("pull requests are not the workflow"), AGENTS.md:76-107 (the seven craft rules added by the planning PR; rule 4, no internal dialect on user-facing surfaces, binds this page); the review tree as committed by the planning PR — 49 markdown files (A 19, B 18, C 7, D 5), 16,849 lines, ~249,000 words, 1.7 MB; audits/audit-phase-20-planning.md §5 (the divergences from the review's roadmap) and §7 (the backlog, out and recorded).
**Complexity:** Small
**Record impact:** post-record (the record is quoted and linked; no recorded byte, MANIFEST, pin, lever or instrument moves — this task ships two prose documents and one index)
**Measurement:** `uv run pytest tests/scripts/test_check_doc_facts.py -q` green with the new link-check bites — every relative link in docs/lessons.md and in audits/review-2026-08-19/README.md resolves, every mapped PR number resolves to a merge commit reachable from HEAD, and the perturbation cases (a broken relative link, a mapped task id with no matching contract, a PR number nothing on main carries) each fail naming the drifted row; `wc -w docs/lessons.md` between 800 and 1,500; `uv run python scripts/check_doc_facts.py` exits 0.

This is the page every hiring-manager persona said they would ask about on the call, and the only
one nobody but the author can write (audits/review-2026-08-19/C/collated-portfolio.md:293-298,
:564-565). The material already exists and is scattered across the training program summary, the
reading guide, the triage and nineteen close audits; what does not exist is the assembly, in the
first person, of what directing coding agents against written contracts actually taught. The
sharpest input is not a win but a critique: the research-lead read closed with "strong on
measurement, weak on knowing when to stop building measurement"
(audits/review-2026-08-19/C/p2-ml-research-lead.md:82), no other reader rebutted it, and the code
track handed over the measurement that makes it concrete — 95,824 lines of process narration
against 57,776 lines of core product Python, a 1.66:1 ratio, against 3,358 lines of durable
engineering documentation (audits/review-2026-08-19/B/repo-health-architecture.md:314-329). The
ruling on process-as-theatre was explicit: the fix is framing, not removing the process, and the
line belongs on this page as an owned lesson rather than answered with more tooling
(:379-388, :394-399). Quoting a critic verbatim on your own front door is a stronger claim to
judgment than any number in the results table.

The lesson that organizes the page is the review's own headline, and the synthesis says where to
put it: B's P0 means correctness, security or data loss; A's P0 means the core loop stops being
believable; every gameplay P0 is a product defect sitting on top of correct code
(audits/review-2026-08-19/D/FINAL-synthesis.md:388-391, with the same sentence opening §0 at
:31-56). That is what explains how a default test tier of 4,621 (tasks/phase-19.md:7) and four
import contracts (.importlinter:10, :18, :26, :34) stayed green while a fifth of crew testimony
was invented. The page must be specific about what those gates structurally could not see: an
invariant asserted in a docstring and falsified two phases later by a map-config flip; a leak
scanner that checked packet shape and string content but never entitlement, so the mutation the
design calls the most important test survived all four suites; import contracts covering 89 of 383
Python files (audits/review-2026-08-19/B/collated-findings.md:63). The honest counterweight belongs
in the same breath — the prompt byte-golden ships the perturbation that proves it can fail, and 43
of 44 provenance paths cited from Python still resolve on disk
(audits/review-2026-08-19/B/repo-health-architecture.md:231, :296) — because the lesson is not
"tests are useless" but "a gate only sees the axis it was pointed at."

The second half of the task publishes the review, and the ruling is precise about the shape: yes,
in wave 3, curated, titled by the retractions, sequenced after the fixes so every finding links to
the PR that closed it, and explicitly not a dump of 171 findings
(audits/review-2026-08-19/D/FINAL-synthesis.md:360-366). The tree the planning PR committed is 49
markdown files and roughly 249,000 words; nobody reads that, so the index IS the artifact. Its lede
is the adversarial layer: three blind reviews of an AI-built codebase that disproved four of their
own headline claims — the surviving-corpse finding refuted by `discovered_by=None` being the flag
that makes a body visible, with zero real misses corpus-wide; the time-of-death headline dissolved
into a two-clock artefact once the +1 agent-memory convention was applied; the fabricated-vent half
measured 98.8% grounded; the flagship attribution corrected from 73.4% to 44.3% victim-caused with
21.5% running the opposite way — plus severities corrected in both directions, one code finding up
from P2 to P1 and the 888-line fork's load-bearing risk experimentally refuted and marked down
(audits/review-2026-08-19/D/synth-ambition.md:249-262; the verdict files named in Section refs).
That framing is also the evidence-backed answer to the process-theatre critique: the process
catches things, including itself.

Two disciplines separate this task from an essay. First, the audience split. docs/lessons.md is a
user-facing surface and craft rule 4 (AGENTS.md:76-107) binds it: no task ids, no register ids, no
threshold arithmetic, no term the glossary has not defined — the mechanisms get described in plain
English and the numbers do the arguing. The review index is an audit-tree document where the
finding ids are the subject matter, so there they are used freely and each one links the file that
owns it. Second, nothing on either page is composed. Every figure is quoted from a committed
source with its path, every mapped row names a task and a PR that exist, and the mapping is
harvested mechanically from the phase document's contracts and from the merge subjects on main
rather than typed from memory — the third column is a link that must resolve, which is exactly the
property that makes "the process caught it and here is the fix" a checkable claim rather than a
boast.

**Files in scope:**
- docs/lessons.md; (new — first person, 800–1,500 words, opening with an owner-confirm marker comment; the themes, the owned critique verbatim, and no internal dialect)
- audits/review-2026-08-19/README.md; (new — the curated index: what each of the four tracks is and how it was run, the retractions first, the acted-on map from finding id to task to merged PR, and the not-acted-on classes with where each is recorded)
- README.md; (the new "What I learned" section only — six to ten one-sentence bullets linking docs/lessons.md, plus the one line pointing at the review index; no other section moves)
- scripts/check_doc_facts.py; (the link-check over the new pages)
- tests/scripts/test_check_doc_facts.py

**Files NOT in scope:**
- audits/review-2026-08-19/A/, audits/review-2026-08-19/B/, audits/review-2026-08-19/C/, audits/review-2026-08-19/D/ (records — the index describes, orders and corrects by pointing; a correction found while indexing is recorded in the index's own errata line and routed to the close, never written into a report)
- audits/audit-phase-20-baseline-7.md, audits/audit-phase-20-preregistration.md, audits/audit-phase-20-planning.md (records — quoted and linked, never edited)
- docs/reading-guide.md, docs/history.md, docs/glossary.md, docs/ml-program.md, docs/architecture.md (owned by the earlier front-door tasks; this page links them and adds no competing narrative)
- every Python package, test fixture, prompt template and replay byte (this task ships prose and an index; nothing executable changes)

**Definition of done:**
- [ ] `docs/lessons.md` exists, is between 800 and 1,500 words, is written in the first person, and opens with an HTML comment marking the wording as the owner's to confirm; the PR states plainly that the voice is a draft for the owner to edit.
- [ ] The page covers, each in its own short section: directing coding agents at scale (the contract, the byte-mirrored generated prompt, the fresh-checkout dispatch, the re-anchoring coordination commit, and why outside pull requests are refused — CONTRIBUTING.md:4); what the automated gates could and could not catch, naming the three mechanism classes (a docstring invariant falsified by a later config flip, a gate that validated shape instead of entitlement, and import contracts covering 89 of 383 Python files) against the 4,621-test default tier and the four contracts; documentation drift treated as a first-class bug, with the structural fix that followed; pre-registration and the negative result, including that a missed bar is reported rather than re-priced; and the owned critique.
- [ ] The research-lead line appears verbatim — "strong on measurement, weak on knowing when to stop building measurement" — attributed to the review's research-lead read, immediately followed by the measured ratio (95,824 lines of process narration against 57,776 of core product Python, against 3,358 lines of durable docs) and by the author's own answer to it.
- [ ] The ruling sentence the synthesis asked for is on the page in the author's words: the code was right and the game was wrong — the two tracks used different definitions of a severe defect, and nearly every gameplay defect was a faithful implementation of a rule nobody would have written after watching it run.
- [ ] Craft rule 4 holds on `docs/lessons.md`: a grep of the file for task ids, review register ids, lever env keys, baseline numbering and threshold arithmetic returns nothing, and any surviving term links `docs/glossary.md`; the PR quotes the grep.
- [ ] `README.md` gains a "What I learned" section of six to ten single-sentence bullets, each a claim rather than a topic, linking `docs/lessons.md`, plus one sentence linking the review index; the diff touches no other README section.
- [ ] `audits/review-2026-08-19/README.md` opens with the retractions: a table whose rows are at minimum the four gameplay headline claims the review disproved and the code finding whose load-bearing risk it refuted by experiment, each row naming the original claim, what the re-derivation measured, and the verdict file with the line range that owns it; a second short block records severity corrections in both directions with one example each way.
- [ ] The index states what each track was and how it was run — the four track directories with their file counts, the number of adversarial verdicts each produced, and the fact that the tracks were blind to one another — plus the tree's size, so a reader knows what they are not being asked to read.
- [ ] The index carries the acted-on map: one row per finding id this phase acted on, with a one-line claim, the Phase-20 task that closed it, and a link to the merged PR; the ids are harvested from the phase document's contracts rather than typed by hand, and the PR numbers from the merge subjects reachable on main.
- [ ] The index carries the not-acted-on classes with the reason and the record that holds it — the balance wave, the refuted items, the decomposition and history-rewrite refusals, and the remaining triaged findings — each pointing at `audits/audit-phase-20-planning.md` §5 or §7 rather than re-arguing the ruling.
- [ ] The index records the one place the review's own correction over-reached, as its dated errata line: the synthesis's verified correction stated that `README.md` mentions the vote-correctness metric nowhere, and the identifier indeed appears nowhere in the file, but the metric is described by name at README.md:194 — the finding's leg is still refuted, on the narrower ground that no structural claim about the metric ever reached the front door.
- [ ] A link-check pins both new documents: every relative link resolves to a file in the tree, every mapped task id matches a contract in `tasks/phase-20.md`, and every mapped PR number appears as a `(#N)` merge-subject suffix reachable from HEAD; the check ships perturbation cases for each of those three legs, and each failure message names the offending row.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — build the map before writing a word of prose. Parse `tasks/phase-20.md` for each contract's
Section refs, pull the `G-n` / `C-n` / `A-n` / `B-n` ids out of it, and pair each id with the task
that cites it; then take the PR number from the merge subject on main for that task's branch. Put
the raw table in the PR body first. Any id whose task never merged, and any task whose PR cannot be
found, is a question for the PR description, not a row.

Step 2 — write the retractions from the verdict files, never from the collated findings. The
collated files carry the original claim; the verdict files carry the re-derivation that overturned
it, and the honest row quotes both. Keep each row to one measured sentence — the reader who wants
the derivation follows the link.

Step 3 — the lessons page is drafted from the synthesis's judgment section and its rulings plus the
verdict files, then stripped of everything that only makes sense inside the project. A useful test
while drafting: read a paragraph aloud imagining a reader who has never seen the repository. If a
sentence needs a task number to land, the sentence is about the process rather than the lesson, and
the lesson is still unwritten.

Step 4 — the owned critique is the hardest paragraph and it is the one worth the most. State the
number, agree with the part that is true, and say concretely what you would do differently. Do not
add a mitigating clause, and do not answer it with a plan for more instrumentation; the review
already ruled that the answer to "too much measurement" is not another measurement.

Step 5 — the link-check is a small parser plus three perturbations, in the same fixture shape the
existing document-fact tests use: copy the tree, break exactly one thing, assert the failure names
it. Resolve PR numbers offline from `git log` subjects, never from the network, so the check runs in
the ordinary gate.

Step 6 — the index links out of the repository only for PRs. Everything else is a relative path, so
the tree stays readable from a clone with no network and the check can prove it.

**Ready-to-paste prompt:** `agent_prompts/task-20-40-lessons-and-review.md`

### Task 20.41 — Tail truth: verifiable-shaped claims, the reading guide's anchors, and the finalist raw slate's status
**Branch:** `phase-20-tail-truth`
**Depends on:** 20.38, 20.40 — the results prose settles the README and the reading guide on the new bytes first, so this task edits final wording rather than a draft; and the lessons page plus the curated review index claim the last README real estate, so the tail sentences are stable before they are made checkable.
**Section refs:** audits/review-2026-08-19/C/collated-portfolio.md §B9 (verifiable-shaped claims and the three named wobbles), §B10 (the finalist raw slate), §B3 (the reading guide's `file:line` citations); audits/review-2026-08-19/C/x1-front-door-reproduction.md reproduction row 1 (the unmentioned `r1.audit.jsonl` sidecar, 38,881 B beside two 50,337-byte replays), GOOD-9, GOOD-11, GOOD-12 and the "ADR-0001 vs README" note; audits/review-2026-08-19/C/p2-ml-research-lead.md §3:33 (weakest-3 item 3: the 449-game slate behind the adoption ruling is not in the repo) and §7:94 (the GOOD item: commit or explicitly de-scope it); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 row 3.6. Re-verified at HEAD: README.md:72 ("recorded verbatim in ADR-0001") vs docs/adr/0001-three-load-bearing-decisions.md:5 (author Codex), :14 (target 2 Hz), :16 (≤ 100 LLM calls) and DESIGN.md §0 (whose call-target sentence carries a parenthetical the ADR drops); docs/deployment.md:7, :38, :104, :129 (bare `audit C-C-1 / C-C-2 / C-C-4`) resolving to audits/audit-2026-05-30-0059-mvp-close.md:53-55 + :164; scripts/run_game.py:46-49 and orchestrator/game.py:1594-1600 (the `<replay-stem>.audit.jsonl` default) with README.md:22-23, :119-120 (the determinism block) and .gitignore:25 + docs/artifacts.md:101 (class (d)); docs/artifacts.md:94, :100, :111, :132-145; training/reports/report-finalist-eval.md:115-118, :569 (§9.2 as-recorded paths), :1066-1070, :2618-2684 (§19, the Task 19.21 erratum); training/reports/results-finalist-eval.jsonl (9 rows carrying `/Users/danielkeinan/ailibi-campaign-1826/…`); scripts/verify_ml_evidence.py:109-111, :120, :486-496, :499, :2108, :2161; tests/scripts/test_verify_ml_evidence.py:210 (the real-tree leg), :262-267, :839-871, :946-975; audits/audit-phase-19-close.md:52 ("OK: 2953/2953 files match 476a1f85…"), :387.
**Complexity:** Small
**Record impact:** post-record
**Measurement:** `uv run python scripts/verify_ml_evidence.py --complete` green with the PR quoting the slate's availability row verbatim (`OK` on the commit path, `INFO … LOST (recorded …)` on the de-scope path); `uv run python scripts/check_doc_facts.py` green; `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` green including the new erratum-pin test and its perturbation leg; `grep -n 'audit C-C-' docs/deployment.md` shows every hit naming its source audit file.

This phase spent itself on making the loudest claims true. Three quieter ones are
still shaped so that a reader cannot check them, and all three sit on the paths a
stranger actually walks. README.md:72 says the three load-bearing decisions are
"recorded verbatim in [ADR-0001]"; the ADR's text is not the README's — it carries a
`target 2 Hz` tick rate (docs/adr/0001-three-load-bearing-decisions.md:14), a `≤ 100
LLM calls` per-game target (:16) and an author line reading Codex (:5), and the
README's restatement carries none of the three. docs/deployment.md opens with
`Anchors: audit C-C-1, C-C-2, C-C-4` (:7) and repeats the bare ids in its body (:38)
and in two section headings (:104, :129); the ids do resolve — to the MVP-close
security review, audits/audit-2026-05-30-0059-mvp-close.md:53-55, listed at :164 —
but only to someone who already knows to grep, which is exactly what the outside
reproduction session recorded
(audits/review-2026-08-19/C/x1-front-door-reproduction.md GOOD-12). And the
determinism demo the README hands every visitor (README.md:22-23 and :119-120) leaves
a file the README never names: orchestrator/game.py:1594-1600 defaults the
observation audit log to `<replay-stem>.audit.jsonl` beside the replay unless
`--audit-log-path` overrides it (scripts/run_game.py:46-49), so the reproduction
session's very first row logged an unexplained 38,881-byte sidecar next to two
50,337-byte replays (review-measured,
audits/review-2026-08-19/C/x1-front-door-reproduction.md row 1).

None of these is a defect in the code; each is a sentence that spends the project's
credibility instead of earning it. A repo whose front door says "verify it yourself"
pays a disproportionate price for a claim that fails on the first check, and the
reproduction session's judgment was that these are the cheapest remaining fixes on
the whole credibility ledger (audits/review-2026-08-19/C/collated-portfolio.md §B9;
audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 row 3.6, "tail polish"). The
standing convention is already written down — claims verifiable-shaped, every
assertion naming the mechanism or the file that settles it — so this task is the
convention applied to its own documentation.

The fourth item, the finalist raw slate, needs its anchor corrected before it can be
acted on. The review reports `training/reports/_finalist_eval_raw` as empty with the
report's rows pointing at `/Users/…`
(audits/review-2026-08-19/C/collated-portfolio.md §B10, carried from
audits/review-2026-08-19/C/p2-ml-research-lead.md §3, itself carried from the
Phase-19 triage). RE-VERIFIED AT HEAD, that anchor has moved: `git ls-files
training/reports/_finalist_eval_raw` now returns exactly one path, `MANIFEST.md` —
Task 19.21's 1,569 per-file digests, registered at docs/artifacts.md:94 — and the
payload itself was folded into the one orphan evidence commit
`evidence/phase-18-coevo` @ `476a1f85492439277350af9708f1d120eb1c0a71` as class-(c)
evidence: 298.157 MiB / 1,569 files (docs/artifacts.md:100 and the paragraph at
:132-145), restored and hash-verified end to end at the Phase-19 close ("OK:
2953/2953 files match 476a1f85…", audits/audit-phase-19-close.md:52), with
`scripts/verify_ml_evidence.py`'s availability leg already carrying both the
recovered row and a recorded-loss ruling (:499, :2108, :2161; the two paths are
pinned at tests/scripts/test_verify_ml_evidence.py:262-267 and :839-871).

What the review actually caught is still true and still unfixed: the document a
research reader opens does not say any of that.
training/reports/report-finalist-eval.md:115-118 still states the provenance
separation as "the raw recordings … live **outside** the repo tree"; :1066-1070 still
names `~/ailibi-campaign-1826/scoring/<arm>/` as the source of every §16 cell; and
the report's one availability erratum (§19, :2618) still locates the bytes on the
temporary `evidence/raw-slate-staging` ref @ `c27ab7b5…` and says Task 19.22 "folds
them" into `evidence/phase-18-coevo` — a promise recorded with no destination sha, no
restore command and no verification result, so the reader has no way to see it kept.
So the central ML ruling still reads as resting on evidence outside the repo, one
restore command away from being auditable. The nine
`/Users/danielkeinan/ailibi-campaign-1826/…` `replay_set_dir` values in
`training/reports/results-finalist-eval.jsonl` stay verbatim by design (the
as-recorded rule at report :569, §9.2) and are not an edit target — they need an
explanation the reader can follow, not a rewrite.

This task closes all four in one pass, additively, and post-record: it moves no
recorded byte, edits no prompt template, introduces no lever, and changes no
production module. The slate half is written for two outcomes because only the owner
can settle it — the agent prepares both and the owner picks in the PR.

**Files in scope:**
- README.md; (the ADR sentence made true, plus at most one clause in the determinism block naming the sidecar if the rewritten block does not already)
- docs/deployment.md; (the four bare `audit C-C-*` citations resolved to their source file; one short subsection explaining the sidecar and its exposure posture)
- docs/artifacts.md; (the finalist raw slate's class and current status legible from the registry row and its detail paragraph, including the one open owner step)
- training/reports/report-finalist-eval.md; (an additive dated erratum stating where the raw slate lives — the evidence-branch commit and the restore command — or that it is de-scoped, with the reason and the reproducibility boundary)
- scripts/fetch_evidence.sh; (touch ONLY if its usage/help text must point a reader at the new erratum — no behaviour change; leaving it untouched is the expected outcome)
- tests/scripts/test_verify_ml_evidence.py; (the real-tree pin: the erratum's sha equals the manifest pin, or the erratum's loss wording equals the recorded ruling)
- docs/reading-guide.md; (path:line citations become heading/symbol anchors)
- docs/adr/0001-three-load-bearing-decisions.md; (the "verbatim" claim and the dropped ≤100-call qualifier — an additive dated note)

**Files NOT in scope:**
- DESIGN.md (§0 is the source both the README and the ADR restate; it is evidence here, not an edit target)
- training/reports/results-finalist-eval.jsonl (as-recorded measurement bytes; the report's own §9.2 keeps the recorded paths verbatim — the erratum explains them, nothing rewrites them)
- training/artifacts/coevo/EVIDENCE-MANIFEST.md (the pin and the staging-ref owner step live there; this task points at them and changes neither)
- scripts/verify_ml_evidence.py (the availability leg already carries the slate row and both rulings; the new guard is a test, not a production change)
- scripts/check_doc_facts.py (extended by earlier tasks; this task only runs it)
- scripts/build_demo_bundle.py (the generated bundle README's absolute local path is the hosted-demo task's fix)
- orchestrator/replay.py (no lever is introduced, so there is nothing to register in the substrate stamp; lever registration is a separate task's job in any case)
- agents/strategic/prompts/ (no task in this phase except the single prompt-set bump may edit a template; this task edits none)
- replays/, training/ code (nothing is recorded and no measurement is re-run)

**Definition of done:**
- [ ] README.md:72's "recorded verbatim in ADR-0001" is replaced by a claim a reader can check in one click: the README restates the decisions and names ADR-0001 (and DESIGN.md §0) as the record, and either restates the two figures the ADR carries — the 2 Hz tick target and the ≤ 100-LLM-calls-per-game target — or says explicitly that the ADR carries them. `grep -n "verbatim" README.md` returns no claim about the ADR, and the PR quotes the before/after sentence.
- [ ] Each of docs/deployment.md's four `audit C-C-*` citations (:7, :38, :104, :129) names its source, `audits/audit-2026-05-30-0059-mvp-close.md`, at least once per section, so no id is resolvable only by grep; the PR quotes `grep -n 'audit C-C-' docs/deployment.md` showing every remaining hit resolved.
- [ ] docs/deployment.md gains one short subsection explaining the `*.audit.jsonl` sidecar: what writes it (the default at orchestrator/game.py, overridable by `--audit-log-path` at scripts/run_game.py), what it holds (the observation-service packet log the firewall's leak scan reads), that it is class (d) and gitignored (.gitignore:25, docs/artifacts.md:101), and — the exposure-relevant part this document exists for — that it is a GM-view artifact that never ships beside the public bundle. If the rewritten README determinism block does not already name the extra file, one clause is added there pointing at this subsection.
- [ ] The finalist raw slate's status is stated where each of its readers lands: docs/artifacts.md's registry row and its class-(c) detail paragraph state the current ruling and the one remaining owner step (the staging-ref deletion that GitHub refused, whose one-command form lives in the coevo evidence manifest §4), and training/reports/report-finalist-eval.md gains a new dated erratum section numbered after §19, following the same "additive, no in-place rewrites" convention §18 and §19 already use.
- [ ] On the COMMIT path the erratum names the pinned commit `evidence/phase-18-coevo` @ its sha, the one restore command, and the verification result it produced, and states in one sentence that §2's "outside the repo tree" separation (:115-118), §16's `~/ailibi-campaign-1826/scoring/<arm>/` sources (:1066-1070) and the nine `/Users/…` `replay_set_dir` values kept verbatim in results-finalist-eval.jsonl per §9.2 all resolve to those pinned bytes. On the DE-SCOPE path the erratum instead records the loss with its date, its reason, and the exact reproducibility boundary (which derived cells remain reproducible from committed rows and which event-level lineage does not), and docs/artifacts.md carries the matching ruling. Neither path rewrites §2, §9.2 or §16 in place.
- [ ] A new test in tests/scripts/test_verify_ml_evidence.py's real-tree section pins the erratum against the machinery: on the commit path the sha named in the report's availability erratum equals `verify_ml_evidence.read_pinned_sha(repo_root)`; on the de-scope path the erratum's loss wording agrees with `verify_ml_evidence.read_slate_ruling(repo_root)`. The test ships with a perturbation leg — a copy of the erratum text with the sha (or the ruling word) altered must FAIL it — so the gate can be seen to fail.
- [ ] `uv run python scripts/verify_ml_evidence.py --complete` is green and the PR quotes the availability leg's slate row verbatim; `uv run python scripts/check_doc_facts.py` is green.
- [ ] scripts/fetch_evidence.sh is unchanged, or its diff is comment/usage text only and the PR says why it was needed; no restore, verify or clean behaviour moves.
- [ ] Every sentence this task adds or changes names the file or command a reader checks it with; the PR's Decisions section lists each one beside that mechanism, and records which slate path the owner chose and on what evidence.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Step 1 — settle the slate before writing prose, because the wording depends on the
answer. This is an OWNER STEP of a few minutes: run `bash scripts/fetch_evidence.sh`
(network, by sha, never by branch name) and then `bash scripts/fetch_evidence.sh
--verify`. The Phase-19 close recorded this restoring and hashing 2953/2953 files
against the pinned sha, and a fresh anonymous fetch of the pushed ref was checked at
that time, so the commit path is the expected outcome and the de-scope path exists
for the case where the pinned objects are no longer reachable. Record the exact
command output in the PR — that output is the evidence the erratum cites. Afterwards
`bash scripts/fetch_evidence.sh --clean` puts the tree back; do not commit restored
bytes, and note that the documented restore and the type gate coexist only because an
earlier task extended the mypy exclude to the restore destinations.

Step 2 — write the erratum additively. Copy the shape of §18 and §19: a numbered `##
N. … erratum (coordination, <date> — the Phase-20 tail-truth pass; additive, no
in-place rewrites)` heading, then numbered items. Item 1 states where the bytes are
and how to get them; item 2 states what that does and does not buy, reusing the
existing boundary language rather than inventing a new one (recovery buys the exact
hash-pinned bytes behind every §16 cell; it does not make a real-provider run
re-runnable); item 3 is the one sentence that redirects a reader who landed on §2,
§9.2 or §16. Keep it short — the existing §19 already tells the recovery story, and
this erratum's whole job is to close it out.

Step 3 — the deployment anchors. The cheapest honest fix is a single expansion at the
top (`Anchors: audits/audit-2026-05-30-0059-mvp-close.md findings C-C-1, C-C-2, C-C-4
— the MVP-close security review; …`) plus a short-form pointer where each id recurs,
so a section read on its own still resolves. Do not renumber or rename the findings:
they are the audit's ids and other documents cite them.

Step 4 — the sidecar subsection belongs in the exposure document rather than the
front door because the interesting fact about it is a privilege fact: it is the full
observation-packet log, which is exactly the GM-view content the rest of that
document is about not publishing. Two short paragraphs is the right size. Then check
the README determinism block as it stands after the earlier README work; add the
naming clause only if it is missing.

Step 5 — the test. Put it in the real-tree section beside the other HEAD-green legs;
read the report through `verify_ml_evidence.FINALIST_REPORT` and compare against
`read_pinned_sha` / `read_slate_ruling` rather than hardcoding a sha in the test. For
the perturbation leg, mutate the erratum text in memory (or in a scratch copy) rather
than the committed file. Keep the assertion narrow: this pins the erratum against the
manifest, not the whole report.

Step 6 — before opening the PR, walk the diff sentence by sentence and ask, for each,
"what does a reader run or open to check this?" If a sentence has no answer, either
give it one or delete it. That question is the whole task.

**Ready-to-paste prompt:** `agent_prompts/task-20-41-tail-truth.md`

### Task 20.42 — THE PHASE CLOSE (owner): the close audit, the gate rerun, the ledger, the next decision
**Branch:** `phase-20-phase-close`
**Depends on:** 20.6 (the front-door fact check must already be green on the vote-correctness truth-up before the close can quote it as a passing leg), 20.10 (the corpus acceptance gate must reject a truncated replay before the close re-runs the validity legs over the recorded sets), 20.11 (the in-vent legality guards are the last engine-rule change, so the close's byte-identity leg runs after them), 20.17 (the close runs the documented restore and the documented gate in one session — the pair the prior phase close recorded as mutually exclusive; the hermeticity fix is what makes this close's rerun quotable at all), 20.18 (the parallel default tier is the invocation the close quotes, and its wall clock is a before/after row), 20.37 (the graduation sweep is the last change to production bytes, so the close verifies the tree it leaves behind), 20.39 (the hero media is a ledger row the close re-verifies against the deployed bundle), 20.40 (the curated review index publishes the finding-to-outcome map the close's ledger mirrors), 20.41 (the tail-truth pass is the last documentation change — bannering a front door that still carried an uncheckable claim would close the phase on the defect class it opened against)
**Section refs:** [L] the prior close's pattern, reprised — audits/audit-phase-19-close.md §1 (the whole gate re-run at close HEAD by the verifiers' actual paths, and its close-found F1: the documented restore and the documented gate are mutually exclusive at two legs), §2 (every contract verified-or-deviation-recorded, none silent), §3 (the before/after story in generated numbers only), §4 (the routed decision, recommendation first, the committed cells doing the arguing), §6 (provenance + the frontier), §7 (the reproduction block); audits/review-2026-08-19/D/FINAL-synthesis.md §4 (the roadmap this phase implements; the wave-2 close-gate list; the pre-registered primary bar), §4 "Later, or never" (the balance-lever ruling: a separate chartered wave with its own record), §6 (the owner's decision framing and the four-week collapse plan), §8 (the re-record ledger); audits/review-2026-08-19/A/collated-findings.md G-5, G-8, G-13, G-15, G-22, G-40 (the six excluded balance levers and their measured evidence); audits/audit-phase-20-preregistration.md (the bars and the decision rule this close reads back); AGENTS.md:76-110 (the seven craft rules every ledger row is audited against); scripts/check.sh:15-21 (the default gate's seven legs); pyproject.toml:74-76 (`addopts = "--strict-markers -m 'not campaign'"` and the registered `campaign` marker — the opt-in tier); .github/workflows/ci.yml + .github/workflows/campaign-tier.yml (the two standing jobs; the Pages workflow is added earlier this phase); docs/artifacts.md:95 (the counted `audits/` registry row, stated as 4.8 MB / 98 files, matching `git ls-files audits | wc -l` = 98 at HEAD); tests/scripts/test_verify_ml_evidence.py:1400 (`test_every_counted_registry_row_matches_the_index`, unmarked and therefore in the DEFAULT tier) via scripts/verify_ml_evidence.py:2162 (`"audits/": (("audits",), ())`) and :2174-2201 (`inventory_problems` — the document's stated count against the git index); scripts/compute_next_task.py:94 (`compute_frontier`, the frontier cross-check); README.md:82-84 and :107 (the two living project-status/roadmap sentences — re-locate by the `## Project status` heading, since the front-door rework and the results pass both restructure this section before the close); tasks/phase-19.md:3 (the STATUS-banner exemplar)
**Complexity:** Small
**Record impact:** post-record — the close verifies and banners the tree the adopting record left; it moves no rendered prompt byte, no detector output and no replay byte.
**Measurement:** `bash scripts/check.sh` green at close HEAD in a clean worktree, quoted leg by leg, plus `uv run pytest -m campaign`, `bash scripts/fetch_evidence.sh` followed by `uv run python scripts/verify_ml_evidence.py --complete`, `bash scripts/verify_samples.sh`, `uv run python scripts/check_doc_facts.py` and the Pages deploy job on the close commit — every leg green or recorded as a named finding; every number in the close audit's before/after table equals a committed pin or a command reproduced in its own method section.

Phase 20 dispatched 41 contracts; this is the 42nd and it is the only one whose job is to
distrust the other 41. The convention the prior two closes established is that a merge is not a
verification: the phase-18 close found real defects inside otherwise-green merges, and the
phase-19 close's own first `bash scripts/check.sh` run at close HEAD exited 1 and then found a
second facet under `mypy` — the F1 recorded at `audits/audit-phase-19-close.md` §1, where the
documented `fetch_evidence.sh` restore and the documented gate turned out to be mutually
exclusive. That finding is this phase's Task 20.17, which means the close is now re-running the
exact pairing that was broken the last time anyone tried it. Re-running is the point.

The gate this close re-runs is not the gate the phase started with. The default tier became
parallel and lost most of its wall clock; the env surface became hermetic; import-linter's
contracts were widened past the six root packages that left `agents/_probe_orch.py` importing
`orchestrator.game` at `4 kept, 0 broken` (C-32, [D-VERIFIED] in
`audits/review-2026-08-19/D/FINAL-synthesis.md` §2 row 3); the leak scanner started checking
entitlement rather than shape, so mutation M6 — every undiscovered body visible to everyone —
can no longer survive all four suites (C-31, the same table row 4); the corpus acceptance gate
started reading truncation as truncation rather than as a legitimate `TICK_BUDGET` (C-6); and a
Pages deploy became a standing job. The close is the first moment all of those run together at
one HEAD, in a clean worktree, with the evidence payload restored and then cleaned. A close that
quotes only the default tier would be quoting the smallest of the phase's own gates.

The ledger is a two-owner surface and the close owns only half of it. The record's ruling belongs
to the adopting-record contract and to its own merge: whether the pre-registered decision rule
produced ADOPTED (baseline 7, the levers graduate, the ladder tip moves) or FINDING (the levers
stay toggles, the record is committed as the finding record, the tip stays at baseline 6 — the
18.12 tip that has stood since 2026-08-01). This close does not re-open that ruling and does not
improve it. It verifies that the ruling was APPLIED — the graduation flips present or absent as
the rule required, the lever slate stamped in the recorded bytes, the floors re-pinned, the
archived prompt-version set retired or kept — and it publishes the numbers either way. A close
that quietly upgrades a FINDING to an ADOPTED is the single failure this phase's whole
pre-registration apparatus exists to make impossible, and the close audit says so in its own
words.

The before/after table reads the pre-registration back, bar by bar, and does not recompute. Every
baseline-6 figure it carries was review-measured over the committed baseline-6 bytes and re-pinned
by the honesty-instrument contract — false crew `whereabouts` 148/723 = 20.5% on `samples/9p2i`;
sole-`alibi_vs_sighting` convicting precision 12/70 = 14.6%; grounded sighting side 36.5%;
fabricated `You completed` lines 53/529 = 10.0% on `samples/9p2i` and 15/65 = 23.1% on
`samples/4p1i`; adjacent-room STRONG share 148/234 = 63.2%; dev markers in spoken `free_text`
53/971 = 5.5%; singular-persona prompts 1,956/1,956; 79 crewmate ejections corpus-wide
(`audits/review-2026-08-19/A/verdicts.md`); non-direct-cell conviction accuracy 46/125 = 0.368
against direct-proof 310/310 (`audits/review-2026-08-19/D/FINAL-synthesis.md` §7). Beside each
sits its baseline-7 value or the stated reason there is none, and the verdict the decision rule
produced. The RR-free half gets the same treatment against measurements that need no record at
all: phantom body frames 1,182/1,769 = 66.8% of committed frames in 50/50 games (C-7) against the
post-fix count, and the default tier's serial 320–338 s against its parallel wall clock. Then the
map: every review finding id this phase acted on resolves to exactly one outcome — fixed,
lever-ON-and-graduated, recorded-as-finding, or triaged backlog — and the backlog is named as a
backlog with its size, which is the synthesis's own instruction ("a triaged backlog reads better
than a half-done sweep").

Finally the close routes. The next decision is the balance wave: the levers this phase excluded
by charter so that one measured delta would have one cause. They are well evidenced and several
are large — no post-meeting position or cooldown reset, so 89 reporters are killed within three
ticks of their own meeting and 69 of 707 meetings carry a participant speaking from inside a vent
(G-5); a witnessed kill that reaches peers only as a +0.08 belief nudge because the turn schema
has no kill shape, at 0.02% of all rendered memory lines (G-8); blind vent exits that produce the
56.5% emerge-sighting rate carrying 310/435 ejections (G-13); finished crewmates standing still,
one for 36 consecutive ticks, across the 48.6% of 9p2i ticks in which nothing happens at all
(G-15); the roll-call asymmetry that makes P(impostor | turn has no whereabouts) 97.7–100% and
leaves `impostor_report.qwen3_6_27b.v3` at 0 calls out of 7,932 (G-22); and sabotage as a walk
simulator, 32 set-wide and 0 in 100 committed 4p1i games (G-40). The synthesis's ruling is that
they belong to a separate chartered wave with its own record, because shipping any of them
alongside the honesty wave destroys the attribution of the delta this phase bought with roughly
23 hours of operator wall clock. The close states the recommendation first, prices each lever
against a second record, and leaves the ruling to the owner.

**Files in scope:**
- audits/audit-phase-20-close.md (new); (the close audit — the section shape below)
- tasks/phase-20.md; (the STATUS line only — CLOSED, the date, the outcome in one sentence, the close audit's path)
- README.md; (the status line only — the two living project-status/roadmap sentences under `## Project status`, flipped from "under way" to the close's outcome; no other README content moves)
- docs/artifacts.md; (the audits/ registry row count only)
- audits/review-2026-08-19/README.md; (the last two rows of the finding→task→PR map)

**Files NOT in scope:**
- every production package, `eval/`, `scripts/`, `tests/`, `frontend/` (the close verifies; it does not fix — a close-found defect is recorded as a finding and routed to the next phase's inputs, exactly as F1 was at the prior close)
- replays/ (the record is done and its bytes are canonical; the close reads them)
- audits/audit-phase-20-preregistration.md, audits/audit-phase-20-counterfactual.md, audits/audit-phase-20-smoke.md, audits/audit-phase-20-baseline-7.md (records — the close quotes them; a correction is an additive dated erratum in the owning document, never a rewrite)
- docs/history.md, docs/reading-guide.md, docs/ml-program.md, docs/lessons.md (the results pass and the lessons pass own them and land before this close)
- docs/artifacts.md; (BLOCKING COORDINATION ITEM — landing the close audit adds one file under `audits/`, and `docs/artifacts.md:95` states a counted `98 files` that `tests/scripts/test_verify_ml_evidence.py:1400` compares against the git index in the DEFAULT tier, so this PR's own `uv run pytest` goes red without the one-token bump. The prior close carried exactly this bump for exactly this reason. Do NOT widen scope silently — craft rule 6: stop and report the blast radius, and ask the owner to admit the file)

**Definition of done:**
- [ ] `audits/audit-phase-20-close.md` re-runs the WHOLE gate at close HEAD by the verifiers' actual invocation paths, each output quoted verbatim with its wall clock: `bash scripts/check.sh` (the default tier, parallel), `uv run pytest -m campaign` (the opt-in tier registered at `pyproject.toml:74-76`), `bash scripts/fetch_evidence.sh` followed by `uv run python scripts/verify_ml_evidence.py --complete`, `bash scripts/verify_samples.sh` in a bare environment, `uv run python scripts/check_doc_facts.py`, and the Pages deploy job's status on the close commit — with the restore-then-gate pair executed in ONE session and its result recorded (green, or a named finding in the F1 shape).
- [ ] Each of the 41 dispatched contracts has a ledger row carrying a fresh contract-specific command, its quoted output, and a verdict of VERIFIED or DEVIATION-RECORDED; no row is silent, no row's verdict rests on the merge alone, and the boilerplate tail is verified once by the gate rerun rather than re-quoted per row.
- [ ] The before/after table states every pre-registered bar from `audits/audit-phase-20-preregistration.md` with its baseline-6 value, its baseline-7 value (or the stated reason there is none), and the verdict the pre-registered decision rule produced — quoted from the record audit and the committed pins, never recomputed in the close; the RR-free rows (phantom body frames, default-tier wall clock, import-contract coverage, the leak scanner's M6 result) sit in the same table with their own sources.
- [ ] The close records that the record's ruling is the record contract's, not the close's: the audit states whether the applied outcome is ADOPTED or FINDING, verifies that the graduation flips, the stamped lever slate, the re-pinned floors and the archived prompt-version set match that outcome, and asserts in words that the close did not re-rule it.
- [ ] Every review finding id this phase acted on maps to exactly one outcome — fixed / lever-ON-and-graduated / recorded-as-finding / triaged backlog — and the untouched remainder is stated as a triaged backlog with its size; the map is consistent row-for-row with the curated review index published earlier this phase.
- [ ] The routed next decision is the balance wave, framed with a costed recommendation: the six excluded levers named with their measured evidence (post-meeting reset, finished-crew jobs, vent peek, `saw_kill`, symmetric roll-call, sabotage — the synthesis's list also carries the 4p1i second act), the attribution argument for a separate record, the operator cost of a second record, and no unilateral ruling; the owner's ruling is recorded in the audit when given.
- [ ] The phase-complete frontier is cross-checked with `scripts/compute_next_task.py::compute_frontier` against a git-log title index PINNED to close HEAD, and the provenance section records close HEAD, the phase's merged-PR range, the coordination commits, the evidence pin and any observed remote tags.
- [ ] `tasks/phase-20.md`'s STATUS line and README's two `## Project status` sentences state the close, its date, its outcome and the close audit's path; a reader who opens either surface after the merge cannot conclude the phase is still under way.
- [ ] docs/artifacts.md's audits/ row count equals the git index at close HEAD; the finding→task→PR map under audits/review-2026-08-19/README.md is complete for every Phase-20 task.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Reprise the prior close's section shape, not its length. It ran 447 lines for 27 contracts and a
phase that recorded nothing; this phase recorded a baseline, so the gate and ledger sections stay
the same size while the before/after section carries real weight.

Step 1 — the gate rerun. Run the clean-worktree default tier FIRST and quote it, then restore the
evidence payload and run the campaign tier and `--complete` in that restored state, then
`--clean` and re-run whatever the restore touched. The prior close discovered its F1 precisely by
noticing which state each leg was in; record the state beside every row. If a leg goes red,
reproduce it by toggling exactly one variable before writing a cause.

Step 2 — the ledger. One table, one row per dispatched contract, columns: id, headline DoD, the
command run at close HEAD, quoted output, verdict. Pick the contract-specific command from each
contract's own Measurement field — that field exists in this phase precisely so the close does
not have to invent one. A deviation is recorded as a finding with a routed destination, never
softened into a pass.

Step 3 — the before/after. Generated numbers only. Every baseline-6 figure comes from the
honesty-instrument pins or the pre-registration; every baseline-7 figure comes from the record
audit. Where a bar could not be read, say which one and why, with the same prominence as the bars
that moved. If the record's outcome was FINDING, the table is still the deliverable — a
pre-registered null on a fixed instrument is the phase's result and is published as one.

Step 4 — the decision menu. Recommendation first, then per-option outcomes, risks and costs, with
the review's own numbers doing the arguing. Price a second record honestly against the operator
wall clock this phase actually took, which the record audit states.

Step 5 — the method section. A single fenced block of every command the audit quotes, in the
order run, each annotated with the section it feeds, and the frontier snippet pinned to close HEAD
so it still reproduces after this close merges. Unshallow the clone before any history claim, and
guard the unshallow so a complete clone does not error.

Two traps from the prior close, both cheap to avoid. An unbounded `git log` already contains this
close's own merge title and collapses the before/after — pin it. And the audits registry count is
fail-loud in the default tier: `docs/artifacts.md:95` promises a file count that
`scripts/verify_ml_evidence.py:2174-2201` compares against `git ls-files audits`, so adding the
close audit moves it by one. That file is not in scope here; report it as a blocking coordination
item rather than editing it.

**Ready-to-paste prompt:** `agent_prompts/task-20-42-phase-close.md`
