# Phase 12 — Front-end rework (spectator replay viewer, vector/observatory)

Goal: rebuild `frontend/` into the most *legible* hidden-information replay viewer — show what each agent knew/believed
vs ground truth — on the existing React 19 + PixiJS + Zustand + FastAPI-loader substrate. Owner decisions (2026-06-17):
art = vector/geometric; scope = spectator replay viewer only (no live, no human player).

Anchors (read before any dispatch): `design/phase-12/stage-0-understand.md` (data dictionary + renderable-surface map +
teardown, incl. §0.5 corrections), `design/phase-12/stage-1-design.md` (the design + §9.5 Claude Design integration),
`design/phase-12/claude-design-brief.md` (the workspace brief → installed as `frontend/CLAUDE.md` in 12.0).

Locked decisions:
- **9p2i is the target set.** The default-served 4p1i set (34/50 zero-meeting, no rubric) gets graceful empty states, not
  first-class treatment.
- **Belief is per-MEETING, not per-tick** (beliefs are "timeless"; the vote-time Rule-2 lift is unpersisted). Map **fog**
  is a separate, genuinely-expensive per-tick *visibility* projection that ships with a UI leak test.
- **Versioned view-model contract + TS codegen from Pydantic** (ends the hand-mirror drift). New surfaces are additive
  loader projections from already-re-walked state.
- **Firewall is inviolable in the UI** too: the As-agent perspective must *simulate* the firewall (no leaking data the
  agent didn't have); role/guilt never encoded in identity hue; ground-truth reveal via icon, suppressed in fog.
- **Keep** the existing store's async-ordering guards, payload windowing, and memoization; the role-neutral outcome-color
  constraint.

Claude Design workflow (per `stage-1-design.md` §9.5; division of labor below): **one component at a time, never a
wholesale replace.** Each chrome task: focused Claude-Design prompt → Share→Handoff to Claude Code → integrate
(compose from tokens/components, no hardcoded hex) → screenshot-verify isolated + composed → small PR → fresh-context
review. Logic tasks are hand-coded (the handoff cannot carry data/state/interaction). Claude Design is owner-driven on
`claude.ai/design`; it is **not** something the build agent invokes. **`/design-sync`** (push our built component
library UP to Claude Design so it composes with our real components) runs **after 12.0** — once Storybook + the
component library exist; a pre-12.0 sync was **deferred 2026-06-17** (the current `frontend/` is a `private` app with no
design system → the converter would fail / import the components we're replacing).

Sequencing: **Wave 0 (art-direction exploration, owner-run) precedes 12.0** — its chosen direction seeds the tokens.
Then 12.0 (foundation) and 12.1 (contract) have no deps and run first/in parallel; 12.2 depends on 12.1; 12.3
depends on 12.1; **12.4–12.9 depend on 12.0 + 12.1** (chrome needs tokens; data needs the contract); 12.2 feeds the
fog in 12.4/12.7; 12.4 feeds the cross-highlight in 12.6; 12.10 is last. Slice ↔ Stage-1 §10 mapping noted per task.

> Note: contracts below are at **plan altitude**. Per the project convention, a full ~250-line dispatch contract is
> elaborated for each task immediately before its dispatch; the Claude-Design prompt + handoff/verify checklist here is
> the design-specific addendum that the gameplay phases didn't need.

---

## Wave 0 — Art-direction exploration (owner-run in Claude Design; no Claude Code dispatch)

The visual personality is OPEN (see `claude-design-brief.md` "Art direction — OPEN"): pick it from concrete renders
before locking tokens. Owner-run on `claude.ai/design` (the build agent can't drive it). **Diverge → pick → converge
into 12.0.** This flips the usual design-system-first order for the exploration phase only (explore → pick → *then*
derive tokens).

Steps:
1. Create the workspace, link this repo, paste `frontend/CLAUDE.md` (= the brief) so Claude Design grounds on the GOAL +
   the binding constraints (legibility, firewall color rules, vector pipeline, token architecture, two-truth grammar).
   (Note: `tokens.ts` doesn't exist yet pre-12.0, so it grounds on the brief + the existing `frontend/` code; the
   exploration's OUTPUT informs the tokens.)
2. First render = the exploration prompt below — ~5 distinct STYLE DIRECTIONS on ONE representative composite screen,
   low-fidelity, to conserve quota.
3. Owner picks one (or mixes). The winner is folded back into `claude-design-brief.md` + becomes `tokens.ts` in 12.0;
   then the per-slice loop runs.

**Map ground truth — attach `design/phase-12/canonical_1-map-reference.png` (or `.svg`) with the prompt.** A faithful
schematic generated from `engine/maps/canonical_1.yaml` (regenerate via `uv run python design/phase-12/gen_map_reference.py`).
The map is FIXED — Claude Design must **restyle this exact layout, never invent / move / rename rooms.** Text fallback if
you can't attach an image:

| Room | x,y,w,h | kind | vent | tag |
|---|---|---|---|---|
| CAFETERIA | 36,4,16,10 | meeting | – | hub (spawn/meeting/emergency) |
| UPPER_HALL | 38,16,12,4 | hallway | – | north spine |
| ADMIN | 36,22,16,8 | task | ✓ | lights-repair panel |
| EAST_HALL | 56,12,4,14 | hallway | – | |
| ENGINEERING | 64,14,14,10 | task | ✓ | reactor-repair panel |
| REACTOR | 82,16,10,8 | task | ✓ | dead-end |
| STORAGE | 64,26,14,6 | utility | ✓ | |
| WEST_HALL | 30,12,4,14 | hallway | – | |
| MEDBAY | 14,14,14,10 | task | ✓ | |
| LABS | 0,16,10,8 | task | ✓ | dead-end |

Corridors (11): CAFETERIA–UPPER_HALL–ADMIN; CAFETERIA–EAST_HALL–ENGINEERING–{REACTOR, STORAGE}; ADMIN–EAST_HALL;
CAFETERIA–WEST_HALL–MEDBAY–LABS; ADMIN–WEST_HALL. Vent ring (6, impostor-only): REACTOR–STORAGE–ENGINEERING–LABS–MEDBAY–ADMIN–back to REACTOR.

**Exploration prompt (paste after grounding):**
> "Ground yourself in this project's brief (the legibility goal + the binding FIREWALL COLOR RULES + the vector pipeline
> + the two-truth grammar). Then, on ONE representative composite screen — the replay workspace showing the top-down
> map (restyle the ATTACHED `canonical_1-map-reference.png` — the real fixed layout; never invent/move/rename rooms),
> the belief-vs-truth overlay, a meeting-transcript snippet, and the transport bar — render **5 distinct
> ART-DIRECTION DIRECTIONS** side by side, low-fidelity, each a different visual *personality*: (1) dark technical
> 'observatory'; (2) bright flat & playful; (3) clean cartoon (rounded, characterful, still professional); (4) editorial
> / serious (print-like); (5) 'AI-slop-meta' — a deliberately generic gradient-SaaS take, as a labeled CONTROL. ALL FIVE
> must obey the binding rules: player identity color ≠ guilt; ground-truth impostor = an icon (never a hue); suspicion =
> a heat ramp; trust↔distrust = blue↔orange; outcomes role-neutral; never hue-only; legibility first. For each, give one
> line: the personality + how it serves legibility. Vary the *skin* (palette / type / illustration / density), never the
> semantic color system."

Notes: keep it to one screen + ~5 directions (quota is tight); judge directions on the LEGIBILITY surfaces, not a
generic dashboard; a colorful/cartoony winner is fine as long as it still obeys the firewall rules + the professional bar.

## Wave A — Foundation & data (no Claude Design chrome; gates everything)

### Task 12.0 — Foundation: tokens, Storybook, CLAUDE.md, CI, Claude Design workspace
**Branch:** `phase-12-foundation`
**Depends on:** none
**Complexity:** Setup
**Stage-1 ref:** §6, §9, slice 0

Establish the design system in the repo, then seed Claude Design from it. Deliver: `frontend/src/tokens.ts` (the tier'd
token source — primitives → semantic → component — consumed by both Tailwind and the Pixi layer as hex→number, zero
magic constants); Storybook wired with a story-per-component scaffold; **install `design/phase-12/claude-design-brief.md`
verbatim as `frontend/CLAUDE.md`**; add a frontend `npm run build` + `tsc` typecheck step to CI (today CI never builds
the frontend). Split the smuggled utils out of `ContradictionBadge.tsx` into `lib/`.
**Claude Design setup (owner):** create the workspace on `claude.ai/design`, link this repo, paste `frontend/CLAUDE.md`;
confirm it builds the design-system project from `tokens.ts` + the brief. (Auth note: paid plan; if using `DesignSync`,
the first call prompts for design scopes / `/design-login` — optional, not the backbone.)
**Acceptance:** `tokens.ts` is the single color/space/type source; Storybook renders the token sheet; CI builds + typechecks
the frontend; `frontend/CLAUDE.md` present; Claude Design workspace seeded. Establishes the prerequisites for a later
`/design-sync` (storybook shape): a per-component Storybook + a component-library build.
**Follow-up (post-12.0, owner-run):** `/design-sync` to push the new library to Claude Design so chrome slices 4/5/7/8
compose with our real components.

### Task 12.1 — View-model contract v1 + cheap projections
**Branch:** `phase-12-viewmodel-contract`
**Depends on:** none
**Complexity:** Integration (backend/loader)
**Stage-1 ref:** §7, slice 1a — **Hand-coded (no Claude Design).** Blocks 12.4–12.9.

Introduce `viewModelVersion` and **generate the TS types from the Pydantic schemas** (kill the hand-mirror in
`frontend/src/types/api.ts`). Add these additive loader projections from already-re-walked state: per-meeting belief
snapshot + an `Error` projection vs `PlayerView.role`; `VentEventView` (enter/exit, from the engine's `VentEntered/Exited`)
as a `TickEventView` member; `killed_by` from `state.bodies`; `ContradictionView.weak: bool` (+severity) via
`is_weak_contradiction()`; the per-meeting §4.6 `gate{leader, leader_max_confidence, threshold, passed}` recomputed from
persisted `ballots[].confidence` (drop `rendered_max`); parsed `BallotView.rewrite_reasons[]` + `rationale_text_clean`
(import the marker constants server-side; special-case `VOTE_PARSE_DEFAULT` = whole string); reactor `repair_progress`
per room + `remaining_ticks`; a per-tick crew/impostor advantage series; a **per-set** rubric endpoint/asset
(`/eval/rubric`) with a staleness guard (compare rubric `git_head` to the served set's MANIFEST sha). Render-ready
already in-DTO: `current_action`, `winner_reason`, task-clock totals, `failed_calls`, typed `conversion`/`gate_metrics`.
Document why `SuspicionGraphView` stays dead (the timeless-belief reason).
**Acceptance:** TS types codegen'd; each surface served + cached; rubric staleness-guarded; no `rendered_max` on ballots.

### Task 12.2 — Per-tick visibility projection + UI leak test
**Branch:** `phase-12-visibility-projection`
**Depends on:** 12.1
**Complexity:** Integration (backend/loader) — the expensive one, isolated on purpose
**Stage-1 ref:** §3.2, §7, slice 1b — **Hand-coded (no Claude Design).**

Derive each agent's `visible_players` / `visible_bodies` / `audible_events` per tick from the `ObservationPacket` during
the `collect_memory` re-walk and **persist them into the view-model** (today the packet is built into a temp dir and
discarded; visibility is graph/lights-dependent via `compute_visibility_for_player` — a naive same-room dim is wrong AND
a leak). Cost it honestly; cache. Ship a **UI leak test** mirroring `eval/leak_test.py` that asserts the As-agent
filtered view never exposes a field the agent could not have seen.
**Acceptance:** per-tick per-agent visibility in the view-model; UI leak test green; fog renders correctly in 12.4.

### Task 12.3 — Playback backbone
**Branch:** `phase-12-playback`
**Depends on:** 12.1
**Complexity:** Integration (frontend state)
**Stage-1 ref:** §4, slice 2 — **Hand-coded (no Claude Design).**

Lift playback into the store / a `usePlayback` hook (out of `ReplayControls`). Source of truth = engine tick via **one
derived selector** (kill the index/tick off-by-one re-derived in 3 places; treat `tick=-1` as a real pre-game value).
Transport (scrub / play-pause / speed / step±N / jump prev-next event / jump prev-next meeting / next-key-moment); the
**advantage graph as a clickable second scrubber**; a shared hover **crosshair**; the event-timeline lanes; URL sync
(`set/game_id/tick/perspective/beliefView/selectedAgent/selectedMeeting`). Keep windowing + lazy meeting bodies + the
async-ordering guards. Meetings are time spans (stage morphs when `tick ∈ meeting.span`); auto-follow is interruptible.
**Acceptance:** everything derives from one tick; URL-restorable; no off-by-one; interruptible auto-follow.

---

## Wave B — Surfaces (chrome via Claude Design; logic hand-coded)

### Task 12.4 — Map stage (vector Pixi + SVG assets + fog)
**Branch:** `phase-12-map-stage`
**Depends on:** 12.0, 12.1, 12.2, 12.3
**Complexity:** Integration (Pixi hand-coded + SVG assets + chrome)
**Stage-1 ref:** §3.2, §5, slice 3 — **Mixed.**

Hand-code the Pixi render layer: rooms from real `(x,y)`+size (from the `MapLayoutView` DTO — `canonical_1`'s fixed
10 rooms / 11 corridors / 6-vent ring; reference `design/phase-12/canonical_1-map-reference.svg`, not invented), agent tokens (identity color, action glyph from
`current_action`, role badge **Omniscient-only**), bodies (`KillEventView` + `killed_by`), **vent-escape animation**
(dive→travel `MapLayoutView.vents`→emerge), reactor tint + per-room repair race + countdown, lights tint, and **As-agent
fog** from the 12.2 visibility projection. The map **SVG assets** (room outlines, action/vent/body icon set) are
generated by **Claude Code with a locked style-spec** (not the Claude Design product) and loaded into Pixi.
**Claude Design prompt (for the surrounding map chrome only — the perspective switcher + map toolbar, not the canvas):**
"Using our design system + `frontend/CLAUDE.md`, design the **map toolbar + perspective switcher** (Omniscient ↔ As-agent
[picker]) for the viewer. States: omniscient / agent-selected / no-replay. Make the perspective a **dominant, persistent
mode banner** (two-truth grammar). Presentational only; compose from tokens; no hardcoded hex."
**Style-spec for the SVG asset set (Claude Code):** locked stroke weight, corner radius, grid unit, palette = identity
tokens + status tokens; geometric/line only; one viewBox convention; output one `.svg` per asset under `frontend/src/assets/map/`.
**Handoff/verify:** README (stack/paths/token-source/"the canvas is hand-coded Pixi — only build the toolbar"/DoD) →
Handoff → integrate → screenshot-verify the toolbar isolated + over the live map; assets pass a visual cohesion check.

### Task 12.5 — Belief × Truth (the hero, per-meeting)
**Branch:** `phase-12-belief-truth`
**Depends on:** 12.0, 12.1, 12.3
**Complexity:** Integration (chrome + matrix logic)
**Stage-1 ref:** §3.3, slice 4 — **Claude Design chrome + hand-coded data.**

Directed adjacency **matrix** (rows=suspector, cols=suspected, color=suspicion) with a **Belief / Ground-Truth / Error**
toggle (same layout, swapped data); ground-truth impostor marker **Omniscient-only, suppressed in fog**; **Error** view
renders confidently-wrong cells **LOUD** (fill + thick border + ✗). Granularity = **per-meeting snapshots** with a
before→after **step control** (small-multiples, not animation); click a cell → that pair's suspicion across meetings;
"what changed this meeting" diff. Sparse **node-link** reserved for "active accusations this meeting" (blue↔orange signed
edges); "freeze order" toggle if seriated.
**Claude Design prompt:** "Design the **Belief × Truth matrix panel**. Displays: an N×N suspicion matrix (heat ramp,
bucketed Low/Med/High), a Belief/Ground-Truth/Error segmented toggle, a meeting step control, and a cell-detail popover.
States: 1 meeting / multiple / no-meeting (empty). Firewall rules: identity ≠ guilt; ground-truth marker is an icon,
**must be hideable** (fog); Error cells rendered LOUD via fill+border+glyph (not hue alone); 'no belief yet' ≠ 0.
Presentational only; tokens only."
**Handoff/verify:** README (token source, the three toggle states, the hide-ground-truth requirement, DoD) → Handoff →
wire to per-meeting belief snapshots → verify all three toggle states + empty state + fog-suppression.

### Task 12.6 — Meeting view
**Branch:** `phase-12-meeting-view`
**Depends on:** 12.0, 12.1, 12.3, 12.4
**Complexity:** Integration (chrome + cross-highlight/link logic)
**Stage-1 ref:** §3.4, slice 5 — **Claude Design chrome + hand-coded interactions.**

Accusation chain as a threaded **waterfall** (indent by `reply_to`); **claim↔map cross-highlight** (hover "saw Red in
Electrical" → light Red + Electrical + sightline + truth match); contradiction **links** with **weak=dashed / strong=solid**;
ballots with the per-meeting **§4.6 verdict** + **rewrite-marker chips** (from `rewrite_reasons`) + correctness by
**shape/label, not hue**; role-neutral outcome banner.
**Claude Design prompt:** "Design the **meeting transcript view**: a threaded accusation waterfall of TurnCards
(speaker chip, structured claims/observations + free text toggle), a contradictions section (weak=dashed, strong=solid
links), a ballots section (voter→target, confidence bar, rationale, marker chips, a §4.6 gate readout), and a
role-neutral outcome banner. States: chain / single-turn / skipped / ejected. Firewall: outcome + correctness are
role-neutral (shape/label, not red/green). Presentational only; tokens only."
**Handoff/verify:** README (interactions to preserve: cross-highlight + link drawing are hand-wired; DoD) → Handoff →
wire cross-highlight to the map + links to turn ids → verify EJECTED/SKIPPED/weak/strong + chips + cross-highlight.

### Task 12.7 — Mind inspector
**Branch:** `phase-12-mind-inspector`
**Depends on:** 12.0, 12.1, 12.2, 12.3
**Complexity:** Integration (chrome + data)
**Stage-1 ref:** §3.5, slice 6 — **Claude Design chrome + hand-coded data.**

Tabbed per-agent panel: **Belief · Prompt · Response · Memory · Flags** + a Thought→Action→Observation trail + "show what
they saw" (ties to the 12.2 fog). Impostor extras Omniscient-only (`fellow_impostor_ids`, cooldown, `own_kill` memory
line, cover-task marked **fabricated**).
**Claude Design prompt:** "Design the **agent mind-inspector** (tabbed: Belief / Prompt / Response / Memory / Flags), with
a reasoning trail and a 'what they saw' toggle. Mono for prompt/response/JSON. States: living / dead / impostor
(Omniscient) / no-agent-selected. Firewall: impostor-only fields appear **only in Omniscient**; cover-tasks labeled
'fabricated'. Presentational only; tokens only."
**Handoff/verify:** README (tabs, mono usage, Omniscient-gating, DoD) → Handoff → wire tabs to `AgentMemoryView` +
LLM-call data → verify all tabs + the Omniscient/fog gating + fabricated-cover labeling.

### Task 12.8 — Replay browser + Highlights reel
**Branch:** `phase-12-browser-highlights`
**Depends on:** 12.0, 12.1
**Complexity:** Integration (chrome)
**Stage-1 ref:** §3.1, slice 7 — **Claude Design chrome.**

Cards (score badge, win-shape tag, drama line, 4-spoke sub-score mini-bar) + filters (set/winner/win-shape/score/has-ejection);
Highlights defaults to rubric `interestingness.per_game[]` (9p2i). **First-class empty/zero-meeting states** (4p1i and
single-meeting games).
**Claude Design prompt:** "Design the **replay browser + highlights reel**: a HighlightCard (0–100 score badge, win-shape
tag, drama stats, a 4-spoke mini sub-score bar), a filter bar, and a prominent **empty/zero-meeting state**. States:
loading / list / empty / error. Presentational only; tokens only."
**Handoff/verify:** README (card fields, the empty-state requirement, DoD) → Handoff → wire to `/replays` + `/eval/rubric`
→ verify sorted reel + filters + empty/zero-meeting.

### Task 12.9 — Dashboard refresh
**Branch:** `phase-12-dashboard`
**Depends on:** 12.0, 12.1
**Complexity:** Integration (chrome)
**Stage-1 ref:** §3.6, slice 8 — **Claude Design chrome.**

Keep the metrics; add typed **`conversion` + `gate_metrics`**, **render the honesty caveats** (small-n / low-power /
populated-bins), and an **interestingness distribution** linking into Highlights.
**Claude Design prompt:** "Refresh the **tournament dashboard**: StatTiles, a calibration curve, a metric-caveat
treatment (small-n / low-power badges), and an interestingness histogram. States: loading / loaded / no-report.
Presentational only; tokens only."
**Handoff/verify:** README (the caveat treatment, DoD) → Handoff → wire to `/eval/tournament-report` (typed) → verify
caveats render + histogram links to Highlights.

---

## Wave C — Polish

### Task 12.10 — Accessibility, responsive, first-run, perf
**Branch:** `phase-12-polish`
**Depends on:** 12.4, 12.5, 12.6, 12.7, 12.8, 12.9
**Complexity:** Integration — **Hand-coded.**
**Stage-1 ref:** §8, §9, slice 9

Keyboard transport + focus + ARIA on data panels + reduced-motion + AA contrast + never-hue-only audit. Responsive
rail→drawer collapse. A first-run **guided mode** on a high-interestingness seed teaching the perspective switcher + the
two-truth grammar. Verify the code-split (Pixi vendor chunk + lazy Dashboard/Highlights) closed the 859 kB single chunk;
optionally add a Playwright visual smoke to CI (needs the loader + a served 9p2i set — sequence after build/typecheck).
**Acceptance:** a11y audit pass; responsive; guided mode; bundle split verified.
