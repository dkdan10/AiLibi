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
baseline 6                      co-adapted movers · upgraded meetings
        │
        │   Phase 18 — presentation: mixed-model lobbies + deduction/deception leaderboard,
        │   auto-highlight reels from the referee, a turn-paced human seat, the public
        │   deception-dataset packaging, and the workflow retrospective write-up
        ▼
      (ship)
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
- **Phase 16 — Voice & Judgment (contracted, `tasks/phase-16.md`, opened 2026-07-11).** The deferred
  `audits/post-phase-14-Voice-and-Judgment-planning.md` program, upgraded by what Wave 0 lands: personas
  (deterministic per-seed registry + persona-conditioned prompts), the citation-gated vote surface
  (zero-flag convictions must cite a source — with vent observations now citable, the gate has sources
  to demand), suspicion provenance, and the pooling levers deferred out of Wave 0 (ballot-whereabouts /
  roll-call elicitation — the mechanism that converts the measured median-3 oracle candidate sets into
  playable deduction, now including typed-grounded vouching and a capped absence prior). Adds the
  probe-first Qwen3.6-27b model decision (GO ⇒ baseline 4 = the model swap, its own layer). Closes on
  baseline 5 with the funnel + the new V&J instruments as the before/after.
- **Phase 17 — co-adaptation (owner goal 3).** Re-ground the ballot surrogate on baseline 5, re-run the
  Phase-15 bake-off recipe for both sides against the upgraded meeting model, re-select champions
  through the same gates. Structurally cheap by design: the surrogate staleness/re-grounding machinery
  and the single bake-off harness were contracted in Phase 15 precisely so this phase is a re-run.
- **Phase 18 — presentation (owner goal 4).** Heterogeneous-model lobbies (per-agent model routing +
  per-player provenance — plumbing already sized in the V&J planning doc) and a which-model-deceives/
  deduces-best leaderboard; referee-driven auto-highlight reels in the spectator UI; a turn-paced
  human seat; packaging the recorded corpora as a labeled deception benchmark; the agentic-workflow
  retrospective write-up. Ordering inside the phase is flexible; nothing here changes game substance.

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

## 5. Known deferred items (tracked, not dropped)

- Ballot-whereabouts / in-meeting roll-call elicitation → Phase 16 (pooling belongs with Judgment).
- New physical information channels (cameras/door logs, task-visual confirmation as soft alibis,
  sabotage retune so meetings happen under pressure) → after Phase 16 proves the funnel keeps what it is
  given; re-evaluate at the Phase-16 close.
- Crew owned-task-set observation surface (task-ordering learnability) → owner-gated at the Phase-15
  pause.
- Co-evolution (Hall-of-Fame/PFSP stack) → Phase-15 pause decision; never the naive two-population form.
- `api/replay_loader.py` decomposition; a second map as a held-out generalization set (becomes pressing
  the moment a learned policy ships as default) → standalone hygiene work, schedule opportunistically.
- DESIGN.md prose refresh (stale sabotage/provider text) → owner-side edit; dispatched agents are barred
  from DESIGN.md by the prompt generator.
