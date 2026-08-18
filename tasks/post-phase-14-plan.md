# Post-Phase-14 plan — the roadmap: evidence substrate → learned tactics → voice & judgment → co-adaptation → presentation

> **STATUS: ADOPTED (owner, 2026-07-05).** This is a PLAN document, not a task doc — it contains no
> `### Task` headers and is deliberately named outside the `tasks/phase-*.md` glob that
> `scripts/_task_parser.py` parses. Dispatchable contracts live in `tasks/phase-15.md` (and, for each
> later phase, in its own `tasks/phase-N.md` authored when that phase opens). The cleanup charter that
> motivates Phase 15's Wave 0 is `tasks/post-phase-14-clean-up.md`.

## 1. Owner goals (the thesis this plan serializes)

1. **Tactical gameplay first** — machine-learned between-meeting play, so games produce more diverse
   situations requiring more nuanced deduction than the current 3–4 repeating scenario shapes.
2. **Voice & Judgment second** — personas and evidence-grounded conviction built against those richer
   scenarios, not against the current shallow ones.
3. **Co-adaptation third** — retrain the gameplay agents against the upgraded meeting layer (through the
   no-LLM meeting surrogate), closing the loop.
4. **Presentation last** — mixed-model lobbies, leaderboards, and spectator polish multiply quality that
   already exists; they come after the quality does.

One amendment to that sequence, adopted after a first-principles measurement of the committed baseline-2
bytes (summarized in `tasks/post-phase-14-clean-up.md`, with full numbers): **a thin evidence-substrate
and cleanup wave runs BEFORE any ML data is recorded or any policy is trained.** The measurement showed
the simulation already generates enough information to nearly solve most meetings — pooled crew
sightings narrow ~8 suspects to a median of 3 (often to exactly 1) — but the meeting layer loses roughly
half of it before the vote: witnessed impostor vents (hard, role-proving evidence, present in 57% of
report meetings) have NO structured representation and reach the transcript only half the time, and 22
of 106 ejections removed the meeting's own (always innocent) reporter. Training a policy optimizer
against those two holes would teach it to farm bugs we already intend to fix, and the ~7h ML calibration
corpus would be invalidated the day the fixes land (the FO-6 surrogate regression already demonstrated
exactly this failure mode). The fixes are small; they go first.

## 2. The spine: one layer per baseline

The project's core discipline — a change must move a metric, attributably, reproducibly — extends to the
roadmap: **each recorded baseline isolates exactly one layer change**, so every effect stays
attributable. Anything that records training data or trains a policy binds to the newest baseline.

```
baseline 2 (committed today)   scripted movers · current meeting layer
        │
        │   Phase 15, Wave 0 — evidence substrate & cleanup (post-phase-14-clean-up.md)
        │   ∥ Phase 15, Wave 1 foundations (gates + policy stamp — layer-independent; the training
        │     env and encoder follow the cleanup's shared-config edits, still meeting-layer-neutral)
        ▼
baseline 3                      scripted movers · FIXED meeting substrate
        │                       → the cleanup's effect measured cleanly (funnel metrics before/after)
        │
        │   Phase 15, Wave 1 tail — ML corpus (recorded AT baseline-3 config), ballot surrogate,
        │   Goodhart probe, the multi-method bake-off (impostor primary, crew track)
        ▼
     THE PAUSE                  mid-phase audit picks the winning method + deployment end-state
        │
        │   Phase 15, Wave 2 — champion productization per the pause decision
        ▼
baseline 4 (REPURPOSED,         scripted movers · same mechanics · NEW MODEL
 2026-07-11: Phase 15 chose      → the model effect measured cleanly (Phase 16 Wave 2,
 branch A — no default flip;       probe-locked, GO-conditional; the learned champion
 baseline 4 is now the             stays opt-in and is re-audited against it)
 Qwen3.6-27b swap, if GO)
        │
        │   Phase 16 — Voice & Judgment (tasks/phase-16.md): personas, citation-gated conviction,
        │   and the information-POOLING levers (roll-call / whereabouts / grounded vouching /
        │   absence prior) — richer voices arguing over evidence the substrate can now hold
        ▼
baseline 5                      scripted movers (champion opt-in) · upgraded meeting layer
        │                       → the V&J effect measured cleanly
        │
        │   Phase 17 — co-adaptation: re-ground the meeting surrogate on baseline 5, re-run the
        │   bake-off recipe (cheap now — the Phase-15 harness makes this a re-run, not a rebuild)
        ▼
baseline 6 (NOT RECORDED at     co-adapted movers · upgraded meetings
 the Phase-17 close,             → the evidence-gated flip ruled FAIL — utility-es keeps a
 2026-07-18: Phase 17's            +0.16 win edge but fails the conversion-economy floors;
 evidence-gated flip ruled         policy-es passes the referee at a 0.02 win rate — so the
 FAIL; the champion stays          scripted FSM stays the default mover and no mover baseline
 opt-in and baseline 5             exists; a mover baseline re-enters only via a future
 stood as the ladder tip —         adopting record that passes the referee + win-edge bar
 audits/audit-phase-17-close.md;   (the NUMBER was then taken by a different record class:
 superseded two nodes down)        18.12's meeting-layer adopting record became baseline 6 —
                                   two nodes down; the mover record itself never landed)
        │
        │   Phase 18 — THE ML PHASE (re-chartered, owner 2026-07-18,
        │   audits/audit-phase-18-planning.md; tasks/phase-18.md): emergent
        │   deception/deduction under environmental pressure — the meeting-layer
        │   package behind an evidence gate (its adopting record, if any arm ships,
        │   is baseline 6), the conviction-economy training signal, alternating-
        │   freeze co-evolution impostor-first, pre-registered emergence
        │   instruments; an evidence-gated mover flip at the close records the
        │   next baseline number after whatever the phase adopted
        ▼
baseline 6 (RECORDED at the     meeting layer upgraded — the 18.11 gate ruled CREW-ONLY,
 18.12 adopting record;          and 18.12 graduated the roll-call round, the endpoint-band
 audits/                         exemption, the vent variant/widening, and the absence
 audit-phase-18-baseline-6.md;   prior (`impostor_roll_call` stays a default-OFF toggle);
 the ladder tip at the           the ML corpus re-recorded on it at 18.13 — the canonical
 Phase-18 close, 2026-08-01)     canary denominator at the standing substrate
        │
baseline 7 (NOT RECORDED,       co-adapted movers on the graduated meetings
 2026-08-01: 18.27 read the      → the §1.3 bar failed the WHOLE slate: every learned arm
 §1.3 bar against the 18.26        wins more than the same-seed FSM comparator (+0.12 to
 real-LLM slate and ruled          +0.30) and every arm fails the baseline-6 referee on
 FAIL — the scripted FSM           the supply/conversion gauges — so the scripted FSM
 stays the default mover,          stays the default mover, no mover baseline exists, and
 the champion stays opt-in —       a mover baseline re-enters only via a future adopting
 audits/                           record that passes the referee + win-edge bar
 audit-phase-18-close.md)
        │
        │   Phase 19 — REVIEW-AND-REFRESH (re-chartered, owner 2026-07-18; chartered
        │   2026-08-03, tasks/phase-19.md; CLOSED 2026-08-18 with NOTHING RECORDED,
        │   Task 19.28 — audits/audit-phase-19-close.md): a deep review of the
        │   existing code (dead spots, dead code, refactor opportunities) + an
        │   updated presentation of the frontend and the data displays. NOT a
        │   feature phase. Heterogeneous-model lobbies are NOT in Phase 19 — a
        │   model-vs-model comparison feature comes only AFTER the review/refresh
        │   work, as its own later decision. The human seat is OUT (not
        │   deferred-to-19; out). All 28 contracts merged (the 27 dispatched ones
        │   re-verified at the close, plus the close itself); the ladder tip
        │   stood untouched at baseline 6.
        ▼
      (the post-19 decision, routed at the 19.28 close per locked decision 6:
       the evidence-honesty substrate phase vs the presentation phase — put to
       the owner with the committed 19.14 proof-vs-inference cells as evidence,
       Option A (the substrate phase) recommended;
       audits/audit-phase-19-close.md §4)
```

## 3. Phase-by-phase summary

- **Phase 15 (contracted, `tasks/phase-15.md`).** Wave 0: the evidence-substrate fixes and repo cleanup
  (charter: `tasks/post-phase-14-clean-up.md`) closing on baseline 3. Wave 1: the ML measurement
  harness, training environment, calibration corpus (recorded at baseline-3 config), rebuilt ballot
  surrogate, and the multi-method training bake-off — BC/DAgger, learned scorer over FSM options + ES,
  direct policy net + ES, MAP-Elites, plus an experiment-tier torch probe. THE PAUSE: a mid-phase audit
  with a real-LLM finalist evaluation settles the winning method, the deployment end-state (opt-in
  factory vs new default + baseline 4), torch promotion, and co-evolution scope; Wave 2 is authored
  there. The training-signal doctrine is locked: optimizers maximize measurable side-specific competence
  with a KL anchor to the scripted FSM; the validity gate and the watchability referee are selection
  gates, never rewards.
- **Phase 16 — Voice & Judgment (`tasks/phase-16.md`, opened 2026-07-11, CLOSED 2026-07-14 on
  baseline 5: J1 + observation-id rendering + the citation gate graduated ON; the absence prior
  stays OFF as a recorded slate ruling pending roll-call calibration — Phase 17 re-runs its
  counterfactual on baseline-5 bytes).** The deferred
  `audits/post-phase-14-Voice-and-Judgment-planning.md` program, upgraded by what Wave 0 lands: personas
  (deterministic per-seed registry + persona-conditioned prompts), the citation-gated vote surface
  (zero-flag convictions must cite a source — with vent observations now citable, the gate has sources
  to demand), suspicion provenance, and the pooling levers deferred out of Wave 0 (ballot-whereabouts /
  roll-call elicitation — the mechanism that converts the measured median-3 oracle candidate sets into
  playable deduction, now including typed-grounded vouching and a capped absence prior). Adds the
  probe-first Qwen3.6-27b model decision (GO ⇒ baseline 4 = the model swap, its own layer). Closes on
  baseline 5 with the funnel + the new V&J instruments as the before/after.
- **Phase 17 — co-adaptation (owner goal 3; `tasks/phase-17.md`, opened 2026-07-14, CLOSED
  2026-07-18 with no mover flip: locked decision 2 failed both finalists — `utility-es` keeps a
  +0.16 win edge over the same-seed scripted FSM but fails the baseline-5 conversion-economy
  floors; `policy-es` passes the referee at a 0.02 win rate — so the scripted FSM stays the
  default mover, the champion stays opt-in, and NO baseline 6 is recorded;
  `audits/audit-phase-17-close.md`).** Re-ground the ballot surrogate on baseline 5, re-run the
  Phase-15 bake-off recipe for both sides against the upgraded meeting model, re-select champions
  through the same gates. Structurally cheap by design: the surrogate staleness/re-grounding machinery
  and the single bake-off harness were contracted in Phase 15 precisely so this phase is a re-run.
  The re-grounding shipped and stands (corpus re-recorded at baseline 5, restoring the Q3
  canary-denominator ruling; surrogate first-GO at training-time-runner tier; ordinal bake-off
  ranking unchanged); the absence-prior graduation + vent widening, the pooling-prompt uptake
  work, the crew deployment surface, and the detector-band relaxation route to Phase 18 as
  recorded contracts (the close audit §6).
- **Phase 18 — THE ML PHASE (re-chartered, owner 2026-07-18; `tasks/phase-18.md`, opened
  2026-07-18, CLOSED 2026-08-01 with NO mover flip: the 18.27 two-axis ruling read the §1.3
  bar against the 18.26 real-LLM slate and ruled FAIL on every arm — the champion candidate
  `ea4bc955…` retains a +0.26 win edge (0.52 vs the same-seed FSM comparator 0.26) but fails
  the baseline-6 referee on both live supply gauges, and so does every finalist (+0.12 to
  +0.30 win edges, referee FAIL ×4) — so the scripted FSM stays the default mover, the
  champion stays opt-in, baseline 7 is NOT recorded, and the ladder tip stands at baseline 6
  (the 18.12 adopting record); zero of the fourteen pre-registered emergence rulings
  demonstrated — the two clause-(c)-blocked kill-placement cells are the phase's named
  behavioral findings N1/N2 — and the crew-adoption slot closed NO-ADOPTION;
  `audits/audit-phase-18-close.md`).** The owner ruled presentation DEFERRED and re-chartered Phase 18 as the ML phase:
  advance the learned agents until deception and deduction arise from environmental pressure rather
  than scripting. Five owner-ratified locked decisions (`audits/audit-phase-18-planning.md` §8):
  layered training signal (a conviction-economy proxy model in the loop + per-generation real-path
  re-ranks), the meeting-layer absence/uptake package in-phase and FIRST behind an evidence gate
  (roll-call round + endpoint-band relaxation + impostor-answer arm + vent widening + absence
  graduation, with pre-registered bars and a crew-only fallback), alternating-freeze co-evolution
  with the stabilizer stack impostor-first, the §1.3 flip bar as target with pre-registered
  emergence instruments co-equal, and encoder work riding the co-evolution wave (first-principles
  primitives rejected on code evidence). What STANDS from the phase: baseline 6 (the CREW-ONLY
  meeting-layer graduation, 18.12) with the ML corpus re-recorded on it (18.13 — the canonical
  canary denominator restored at the standing substrate; the close computes the fresh anchors),
  the conviction-economy model (GO, decision accuracy 0.938 on its held-out split) composed
  with the surrogate's retained ranking channel into the meeting-outcome runner (18.29, GO), the
  co-evolution stack (dual-role rollouts + two-identity stamps, hall-of-fame/PFSP, the
  alternating-freeze driver, scenario staging, campaign ergonomics), and both campaigns closed
  as measured findings (18.24 STOPPED at a screening-tier shortlist; 18.25 with the CF2
  general-base starvation finding; the Red-Queen cycling signature recorded for Phase 19). The
  deferral ledger routes through the close audit §6; the Phase-19 review inputs (dead-spot
  candidates, instrument residuals) through its §7.
- **Phase 19 — REVIEW-AND-REFRESH (re-chartered, owner 2026-07-18; `tasks/phase-19.md`, opened
  2026-08-03, CLOSED 2026-08-18 with NOTHING RECORDED: all 28 contracts merged — the 27
  dispatched ones re-verified at close HEAD, plus the close itself — the ladder tip stands at
  baseline 6, and the whole gate — both test tiers, the
  evidence completeness verifier, and byte identity — re-ran green at the close;
  `audits/audit-phase-19-close.md`).** Not a feature phase: (a) a
  deep review of the code that already exists — dead spots, dead code, refactor opportunities; (b)
  an updated presentation of the frontend and the data displays. The human seat is OUT (not
  deferred-to-19; out). Heterogeneous-model lobbies are NOT in Phase 19 either — a feature comparing
  how models perform relative to one another comes only AFTER the review/refresh work, as its own
  later decision. The former presentation scope (leaderboards, highlight reels, dataset packaging,
  the retrospective) re-enters only through that later decision. What the phase shipped: the
  front-door/in-code truth sweeps with generated-fact checks, the spectator coherence pass
  (unspoiled mode, the evidence taxonomy, the curated default, the static demo), the frontend test
  baseline, the deduction metrics + injustice fixtures (the post-19 decision's committed
  instrument), the ML tier map/retirements/report-honesty close, the coevo prune to the pinned
  evidence branch with `verify-ml-evidence --complete`, the parameterized replay walker, and the
  two-tier test structure. The close routed the post-19 decision — the evidence-honesty substrate
  phase vs the presentation phase — to the owner with Option A (the substrate phase) recommended,
  argued from the committed 19.14 proof-vs-inference cells (direct-proof conviction accuracy 1.000
  everywhere vs non-direct 0.303/0.393 carrying every innocent ejection;
  `audits/audit-phase-19-close.md` §4).

## 4. Standing rules (carried from the Phase-15 preamble and the planning audits)

1. **One layer per baseline.** Never land a mover change and a meeting-layer change in the same record.
2. **Nothing trains against a layer scheduled to change.** Training data, surrogates, and champions bind
   to the newest baseline; any layer change re-grounds the surrogate before further training (the FO-6
   lesson, operationalized by the Phase-15 staleness cap).
3. **Watchability is a gate, never a reward.** The D1–D4 geomean + evidence-supply floors select
   champions; no optimizer ever maximizes them.
4. **Levers stay reversible.** Behavior changes ship default-OFF where the substrate allows, proven
   offline against committed bytes, graduated to unconditional at the baseline that adopts them (the
   13.5/14.10 pattern).
5. **Dependency posture.** numpy is training-side only; torch stays experiment-tier unless the Phase-15
   pause promotes it; production inference under `agents/` stays pure-Python and byte-deterministic.
6. **Findings, not failures.** A measured flat/negative result closes as a finding (the Phase-14
   doctrine); the pause exists so a small bake-off result redirects effort instead of sinking it.

## 5. Known deferred items (tracked, not dropped — dispositions refreshed at the Phase-18 open, 2026-07-18)

- Ballot-whereabouts / in-meeting roll-call elicitation → LANDED at Phase 16 (the 16.15
  elicitation); the residual uptake/turn-taking gap (53% of living player-meetings never take a
  turn) is now Phase 18's Wave-1 meeting-layer package (`tasks/phase-18.md` 18.8–18.12).
- New physical information channels (cameras/door logs, task-visual confirmation as soft alibis,
  sabotage retune so meetings happen under pressure) → re-evaluated at the Phase-18 close as this
  entry demanded (`audits/audit-phase-18-close.md` §6.6): the demand side now exists and is priced
  (the baseline-6 supply floors; the witnessed gauge's rare-event unresolvability at n=50 is the
  close's L2 finding), but Phase 19 is review-and-refresh, not a feature phase — so REMAINS
  DEFERRED with the trigger refreshed: re-evaluate at the authoring of the next FEATURE phase,
  reading the close audit's §6.1 L2 + §2.2 + §3 anchors as inputs.
- Crew owned-task-set observation surface (task-ordering learnability) → LANDED at 15.22 (pause
  decision 5); the crew DEPLOYMENT surface (production opt-in) is Phase 18's 18.7, adoption
  gated.
- Co-evolution (Hall-of-Fame/PFSP stack) → now OWNED by Phase 18 Wave 3 (alternating-freeze +
  the stabilizer stack, 18.19–18.21); the naive simultaneous two-population form stays barred
  (pause decision 4, unchanged).
- `api/replay_loader.py` decomposition → a Phase-19 review input. A second map as a held-out
  generalization set becomes pressing the moment a learned policy ships as default — i.e. on a
  Phase-18 18.27 PASS branch; the close routes it explicitly in that case.
- DESIGN.md prose refresh (stale sabotage/provider text) → owner-side edit; dispatched agents are
  barred from DESIGN.md by the prompt generator. A Phase-19 review input.
