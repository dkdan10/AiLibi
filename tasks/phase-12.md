# Phase 12 — Front-end rework (spectator replay viewer, vector/observatory)

Goal: rebuild `frontend/` into the most *legible* hidden-information replay viewer — show what each agent knew/believed
vs ground truth — on the existing React 19 + PixiJS + Zustand + FastAPI-loader substrate. Owner decisions (2026-06-17):
art = vector/geometric; scope = spectator replay viewer only (no live, no human player).

Anchors (read before any dispatch): `design/phase-12/stage-0-understand.md` (data dictionary + renderable-surface map +
teardown, incl. §0.5 corrections), `design/phase-12/stage-1-design.md` (the design + §9.5 Claude Design integration),
`design/phase-12/claude-design-brief.md` (the workspace brief → installed as `frontend/CLAUDE.md` in 12.1);
`design/phase-12/tokens-seed.md` (the committed token seed 12.1/12.2 read); and `design/phase-12/playful-system/` (the
in-repo Playful design reference: the renderable 0b converge `.dc.html`, `playful-render.png` visual target, design chat
— chrome slices 12.5–12.7 read the component code there). Do NOT point build agents at the Claude Design share URL.

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
library UP to Claude Design so it composes with our real components) runs **after 12.1** — once Storybook + the
component library exist; a pre-12.1 sync was **deferred 2026-06-17** (the current `frontend/` is a `private` app with no
design system → the converter would fail / import the components we're replacing).

Sequencing: **Wave 0 (art-direction exploration, owner-run) precedes 12.1** — its chosen direction seeds the tokens.
Then 12.1 (foundation) and 12.2 (contract) have no deps and run first/in parallel; 12.3 depends on 12.2; 12.4
depends on 12.2; **12.5–12.10 depend on 12.1 + 12.2** (chrome needs tokens; data needs the contract); 12.3 feeds the
fog in 12.5/12.8; 12.5 feeds the cross-highlight in 12.7; 12.11 is last. Slice ↔ Stage-1 §10 mapping noted per task.

> Note: contracts below are at **plan altitude**. Per the project convention, a full ~250-line dispatch contract is
> elaborated for each task immediately before its dispatch; the Claude-Design prompt + handoff/verify checklist here is
> the design-specific addendum that the gameplay phases didn't need.

---

## Wave 0 — Art-direction exploration (owner-run in Claude Design; no Claude Code dispatch)

The visual personality is OPEN (see `claude-design-brief.md` "Art direction — OPEN"): pick it from concrete renders
before locking tokens. Owner-run on `claude.ai/design` (the build agent can't drive it). **Diverge → pick → converge
into 12.1.** This flips the usual design-system-first order for the exploration phase only (explore → pick → *then*
derive tokens).

**0a DONE 2026-06-17 — DIRECTION 03 "Playful" chosen.** All three explored directions (01 Forensic / 02 Telemetry /
03 Playful) were firewall-compliant + map-faithful; **Playful** picked as most structurally readable + on-theme. Two
converge fixes required (identity-palette re-spacing off the semantic hues + density tuning) — baked into the 0b
converge prompt below.

Steps:
1. Create the workspace, link this repo, paste `frontend/CLAUDE.md` (= the brief) so Claude Design grounds on the GOAL +
   the binding constraints (legibility, firewall color rules, vector pipeline, token architecture, two-truth grammar).
   (Note: `tokens.ts` doesn't exist yet pre-12.1, so it grounds on the brief + the existing `frontend/` code; the
   exploration's OUTPUT informs the tokens.)
2. **Diverge (0a)** — paste the exploration prompt below: ~5 directions, **identical content**, each rendered as ONE
   composite legibility screen (Omniscient mode: restyled map + belief×truth overlay + meeting snippet + transport)
   **plus a small style tile** (palette incl. the firewall-semantic colors, type pairing, 3–4 component swatches).
   Low-fidelity — the pick-enabler, not the product. (Quota is tight; do NOT lay out both modes × 5.)
3. **Pick** one direction (or mix two).
4. **Converge (0b)** — expand ONLY the chosen direction to the **12.1 seed**: a design-system / **token sheet** (full
   ramp + the semantic tokens: identity set, suspicion heat ramp, trust/distrust blue–orange, status, truth
   solid/ghosted; + type, spacing, radii, elevation, motion), the **map fully restyled**, and **both viewing modes**
   (Omniscient + As-agent fog) laid out to prove the two-truth grammar + fog role-suppression — ideally plus the
   **meeting view** (the densest text surface). This feeds `tokens.ts` (12.1) + the per-component handoffs; then the
   per-slice loop runs.

**Wave-0 deliverables:** 0a = 5 × (one composite screen + style tile), identical content, for the PICK · 0b = 1 ×
(token sheet + restyled map + both modes + meeting view) as the 12.1 seed.

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
> semantic color system. Render each direction as ONE composite screen + a small style tile (palette · type · 3–4
> component swatches), and use IDENTICAL content across all five — compare style, not content."

Notes: keep it to one screen + ~5 directions (quota is tight); judge directions on the LEGIBILITY surfaces, not a
generic dashboard; a colorful/cartoony winner is fine as long as it still obeys the firewall rules + the professional bar.

**Converge prompt (0b — paste after picking Playful; attach the map reference):**
> "Lock **DIRECTION 03 — Playful** (cream + ink chunky-sticker; Fredoka / Space Mono) as the chosen direction and produce
> its **design-system seed**. Deliver: **(1)** a **token / design-system sheet** — full color ramp + type scale +
> spacing / radii / elevation / motion, and the **semantic tokens**: a 9-color **identity palette**, the **suspicion**
> heat ramp, **trust↔distrust** (blue↔orange), **status** (alive / dead / sabotage / contradiction-weak /
> contradiction-strong), and the **truth pair** (solid = ground truth, ghosted = belief); **(2)** the **canonical_1 map**
> fully restyled (same fixed layout); **(3) both viewing modes** side by side — **Omniscient** and **As-agent (p-3)
> fog** — proving the two-truth grammar and that the impostor badge + vents hide in fog; **(4)** the **dense surfaces**: a
> full **9×9 belief×truth matrix** with a **Belief / Ground-truth / Error** toggle (confidently-wrong cells rendered
> LOUD), and a **full meeting view** (accusation chain + weak-vs-strong contradiction links + ballots with the §4.6
> verdict + rewrite-reason chips).
> **Two HARD requirements:**
> **A — Fix the palette collisions.** In 0a the bright identity colors overlapped the meaning colors (identity gold ≈
> suspicion-MED ≈ distrust; identity blue ≈ trust). Re-pick the 9 identity colors into a hue band **clearly disjoint**
> from the semantic channels: reserve **amber/orange exclusively for suspicion, blue exclusively for trust, red
> exclusively for kill**; place identity in **purples / teals / greens / magentas**. Pair every status with shape or text
> (never hue-only).
> **B — Survive density.** The 2.5px outlines + hard shadows were only tested on a sparse screen. On the 9×9 matrix and
> the full transcript, **tune the weight down** so it stays calm and legible — keep the playful personality on chrome /
> headers; dense cells / rows must not be noisy (borrow Telemetry's restraint for data panels).
> Keep the firewall rules, the fog default, **'NO BELIEF YET' (≠ 0)**, and the **FABRICATED (omniscient) vs UNVERIFIED
> (fog)** distinction. **Output the token sheet explicitly — it becomes our `tokens.ts`.""

When 0b lands, its token sheet seeds `tokens.ts` in **12.1**; the chosen Playful system then governs every chrome slice.

## Wave A — Foundation & data (no Claude Design chrome; gates everything)

### Task 12.1 — Foundation: design tokens, Storybook, CLAUDE.md, CI
**Branch:** `phase-12-foundation`
**Depends on:** none
**Section refs:** design/phase-12/stage-1-design.md §6, §9, §9.5; design/phase-12/claude-design-brief.md; **the committed 0b token sheet `design/phase-12/tokens-seed.md`** (transcribe `tokens.ts` from it — it is the in-repo source of truth, NOT the Downloads mockup); the Playful visual reference `design/phase-12/playful-system/playful-render.png` (Storybook + the cream theme should match it)
**Complexity:** Integration
**Files in scope:**
- frontend/src/tokens.ts
- frontend/src/index.css
- frontend/CLAUDE.md
- frontend/package.json
- frontend/.storybook/main.ts
- frontend/.storybook/preview.ts
- frontend/src/lib/contradictions.ts
- frontend/src/ui/PlayerChip.tsx
- frontend/src/stories/Tokens.stories.tsx
- .github/workflows/ci.yml
**Files NOT in scope:**
- api/ and the loader — Task 12.2 owns the DTO/contract and the `_COLOR_PALETTE` change
- frontend/src/components/MapView.tsx and the Pixi render layer — Task 12.5
- any belief / meeting / dashboard component — Waves B and C
- data/store wiring — no new fetches; the Zustand store is untouched here

Stand up the Playful design system in the repo so every later chrome slice composes from one source. Build
`frontend/src/tokens.ts` as the single token source, transcribed from the accepted 0b token sheet: paper/ink ramps,
`suspicion[]` + buckets (low ≤ .35 / high > .72), `trust`/`distrust` (blue↔orange), `kill` (#E23B2F), `contradiction`
(#D6249E), `status` (alive / dead / sabotage + contradiction-weak dashed / contradiction-strong solid), the 9-colour
`identity[]` (greens/teals/purples `#5DA83A…#A94FC6`), `truth` (ground solid / belief ghosted / noBelief hatch), plus
`radius`/`space`/`elevation`/`motion`/`type`. Resolve the seed's pseudo-code self-references (`fill:'identity'`,
`ink[500]`) into real TS. The SAME object feeds DOM and Pixi: emit Tailwind v4 `@theme` tokens (CSS custom properties)
for the DOM layer and a `pixiHex(token)` number helper for the canvas — zero magic constants in either. Encode the
density rule from the seed: the hard 2.5px-border / offset-shadow `elevation` is CHROME-only, data surfaces use a 1px
hairline (`elevation.data`). Flip `index.css` from `color-scheme: dark` to the cream/ink Playful base and load Fredoka +
Space Mono (self-hosted woff2 to avoid a render-blocking fetch). Install `design/phase-12/claude-design-brief.md`
verbatim as `frontend/CLAUDE.md`. Stand up Storybook with a story-per-component scaffold and a Tokens story that renders
the full sheet. Split the utilities smuggled into `ContradictionBadge.tsx` (`findContradictions`, `dedupeContradictions`,
the `PlayerChip`/`ObservationLine`/`ClaimLine` primitives, the id helpers) into `frontend/src/lib/contradictions.ts` +
`frontend/src/ui/`, updating imports. Add a frontend job to CI (`npm run build` + `tsc --noEmit`) — today CI builds only
the Python side, so the 859 kB chunk and any TS error are invisible. Use the `frontend-design` skill for distinctive,
non-templated visual choices.
**Definition of done:** `tokens.ts` is the single colour/space/type source consumed by both Tailwind (`@theme`) and a
`pixiHex` helper; `index.css` is the Playful cream/ink base with no `color-scheme: dark`; Fredoka + Space Mono load;
Storybook runs and renders the Tokens sheet plus ≥ 1 component story; `frontend/CLAUDE.md` is the installed brief; the
`ContradictionBadge` utilities live in `lib/`/`ui/` with imports updated and the tree still compiling; CI runs
`npm run build` + `tsc --noEmit` for the frontend and passes.
**Implementation hint:**
transcribe `tokens.ts` directly from the committed seed `design/phase-12/tokens-seed.md` (already structured); keep the
hard-shadow / 2.5px-border tokens namespaced as `chrome` so dense components can opt into the 1px `data` treatment;
prefer self-hosted fonts over a Google Fonts `<link>`.
**Integration risk:**
Tailwind v4 `@theme` ↔ `tokens.ts` wiring is new; the `ContradictionBadge` split touches files
other components import from (keep the tree compiling); the new frontend CI job will surface the pre-existing > 500 kB
chunk warning — record it, do not chase the code-split here (that is 12.11).
**Ready-to-paste prompt:** `agent_prompts/task-12-1-foundation.md`

### Task 12.2 — View-model contract v1 + cheap projections
**Branch:** `phase-12-viewmodel-contract`
**Depends on:** none
**Section refs:** design/phase-12/stage-1-design.md §7, §9.5; design/phase-12/stage-0-understand.md §0.5, §3, §4; the firewall + identity rules in design/phase-12/claude-design-brief.md
**Complexity:** Integration
**Files in scope:**
- api/schemas.py
- api/replay_loader.py
- api/routes/replays.py
- api/routes/eval.py
- frontend/src/types/api.ts
- scripts/gen_frontend_types.py
- experiments/lab/rubric_score.py
- tests/api/test_view_model.py
**Files NOT in scope:**
- frontend components and the Pixi render layer — Waves B and C
- the per-tick per-agent visibility projection + UI leak test — Task 12.3
- engine/ and the recorded replays — every change here is a load-time projection; NO re-record

Introduce a `viewModelVersion` on the served payload and generate `frontend/src/types/api.ts` from the Pydantic schemas
(kill the hand-mirror and its documented drift). Add these additive projections, all from state the loader already
re-walks: a per-meeting belief snapshot plus an `Error` projection vs `PlayerView.role`; a `VentEventView` (enter/exit)
carried as a `TickEventView` member (from the engine's `VentEntered`/`VentExited`); `killed_by` from `state.bodies`;
`ContradictionView.weak: bool` (+ severity) via `is_weak_contradiction()`; a per-meeting §4.6
`gate{leader, leader_max_confidence, threshold, passed}` recomputed from persisted `ballots[].confidence` (drop the
un-persisted `rendered_max` — the real rule is plurality + at least one leader ballot ≥ 0.6, tie → SKIP, NOT a
vote-count majority); parsed `BallotView.rewrite_reasons[]` + `rationale_text_clean` (import the marker constants from
`meetings/voting.py` + `meetings/manager.py`, never hardcode; special-case `VOTE_PARSE_DEFAULT` = the whole string);
reactor `repair_progress` per room + `remaining_ticks`; a per-tick crew/impostor advantage series; and a per-set rubric
surface (`/eval/rubric`) with a staleness guard (compare the rubric `git_head` to the served set's MANIFEST sha) PLUS
its producer — a regen step that re-runs `experiments/lab/rubric_score.py`, stamps `git_head`, and co-locates
`results-rubric-score.json` per served set, wired into the refresh/re-record path so the happy path stays fresh (not only
banner-guarded when stale).
Surface the already-in-DTO render-ready fields (`current_action`, `winner_reason`, task-clock totals, `failed_calls`,
typed `conversion`/`gate_metrics`). Document why `SuspicionGraphView` stays dead (beliefs are timeless). Identity-palette
alignment, the one backend touch: replace `api/replay_loader.py::_COLOR_PALETTE` — today a 12-colour rainbow (`#e6194b`
red / `#ffe119` yellow / `#4363d8` blue / `#f58231` orange …) that collides with the reserved channels (red=kill,
amber=suspicion, blue=trust) — with the Playful identity palette from the committed
`design/phase-12/tokens-seed.md` (the SAME `identity[]` list 12.1 transcribes into `tokens.ts`, so the two parallel tasks
cannot drift on it) so `PlayerView.color` matches it and DTO ↔ design never drift. Colours are derived at load, so this is a loader-only change with NO
replay re-record; keep it firewall-clean (identity never encodes guilt).
**Definition of done:** the served payload carries `viewModelVersion`; `frontend/src/types/api.ts` is generated from the
Pydantic schemas (no hand-mirror); every new surface is served, cached, and covered by a test; the §4.6 gate is
per-meeting and `rendered_max` is gone; the rubric surface is per-set and staleness-guarded; `PlayerView.color` serves
the Playful identity palette (no rainbow) with the leak/determinism tests still green and NO re-record; the §4.6 gate has a CONSISTENCY test (the recomputed leader +
`passed` matches each meeting's actual outcome / `ejected_player_id` across the committed 9p2i set — not just a formula
unit test); the rubric has a regen step (re-run + `git_head` stamp, per-set), not only the staleness banner; a codegen
FIDELITY gate round-trips a real served payload through the generated TS types (compiles + narrows the discriminated
unions); `scripts/check.sh` is green.
**Public types introduced:**
- api.schemas.BeliefFrameView
- api.schemas.VentEventView
**Implementation hint:**
do every projection inside the existing `_walk`/re-walk so nothing new is persisted; reuse
`is_weak_contradiction()` and the meeting marker constants by import; for the TS codegen prefer a small script over a
heavy dependency, wired into `check.sh` so drift fails CI.
**Integration risk:**
the Pydantic→TS codegen pipeline is new — its riskiest spot is discriminated-union narrowing (`TickEventView` ⊃
`VentEventView`/`KillEventView`/…), so a fidelity gate round-trips a real payload through the generated types, and if the
bespoke script can't narrow reliably, fall back to `openapi-typescript` off FastAPI's OpenAPI schema; it must be
deterministic and run in CI; the
`_COLOR_PALETTE` change flows into `PlayerView.color`, so re-run the leak/determinism tests (it is colour-only and
firewall-neutral); the §4.6 recompute must match the engine gate exactly (plurality + ≥ 0.6, tie → SKIP), not the
mock's "majority".
**Ready-to-paste prompt:** `agent_prompts/task-12-2-viewmodel-contract.md`

#### Task 12.3 — Per-tick visibility projection + UI leak test
**Branch:** `phase-12-visibility-projection`
**Depends on:** 12.2
**Complexity:** Integration (backend/loader) — the expensive one, isolated on purpose
**Stage-1 ref:** §3.2, §7, slice 1b — **Hand-coded (no Claude Design).**

Derive each agent's `visible_players` / `visible_bodies` / `audible_events` per tick from the `ObservationPacket` during
the `collect_memory` re-walk and **persist them into the view-model** (today the packet is built into a temp dir and
discarded; visibility is graph/lights-dependent via `compute_visibility_for_player` — a naive same-room dim is wrong AND
a leak). Cost it honestly; cache. Ship a **UI leak test** mirroring `eval/leak_test.py` that asserts the As-agent
filtered view never exposes a field the agent could not have seen.
**Acceptance:** per-tick per-agent visibility in the view-model; UI leak test green; fog renders correctly in 12.5.

#### Task 12.4 — Playback backbone
**Branch:** `phase-12-playback`
**Depends on:** 12.2
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

#### Task 12.5 — Map stage (vector Pixi + SVG assets + fog)
**Branch:** `phase-12-map-stage`
**Depends on:** 12.1, 12.2, 12.3, 12.4
**Complexity:** Integration (Pixi hand-coded + SVG assets + chrome)
**Stage-1 ref:** §3.2, §5, slice 3 — **Mixed.**

Hand-code the Pixi render layer: rooms from real `(x,y)`+size (from the `MapLayoutView` DTO — `canonical_1`'s fixed
10 rooms / 11 corridors / 6-vent ring; reference `design/phase-12/canonical_1-map-reference.svg`, not invented), agent tokens (identity color, action glyph from
`current_action`, role badge **Omniscient-only**), bodies (`KillEventView` + `killed_by`), **vent-escape animation**
(dive→travel `MapLayoutView.vents`→emerge), reactor tint + per-room repair race + countdown, lights tint, and **As-agent
fog** from the 12.3 visibility projection. The map **SVG assets** (room outlines, action/vent/body icon set) are
generated by **Claude Code with a locked style-spec** (not the Claude Design product) and loaded into Pixi.
**Claude Design prompt (for the surrounding map chrome only — the perspective switcher + map toolbar, not the canvas):**
"Using our design system + `frontend/CLAUDE.md`, design the **map toolbar + perspective switcher** (Omniscient ↔ As-agent
[picker]) for the viewer. States: omniscient / agent-selected / no-replay. Make the perspective a **dominant, persistent
mode banner** (two-truth grammar). Presentational only; compose from tokens; no hardcoded hex."
**Style-spec for the SVG asset set (Claude Code):** locked stroke weight, corner radius, grid unit, palette = identity
tokens + status tokens; geometric/line only; one viewBox convention; output one `.svg` per asset under `frontend/src/assets/map/`.
**Handoff/verify:** README (stack/paths/token-source/"the canvas is hand-coded Pixi — only build the toolbar"/DoD) →
Handoff → integrate → screenshot-verify the toolbar isolated + over the live map; assets pass a visual cohesion check.

#### Task 12.6 — Belief × Truth (the hero, per-meeting)
**Branch:** `phase-12-belief-truth`
**Depends on:** 12.1, 12.2, 12.4
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

#### Task 12.7 — Meeting view
**Branch:** `phase-12-meeting-view`
**Depends on:** 12.1, 12.2, 12.4, 12.5
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

#### Task 12.8 — Mind inspector
**Branch:** `phase-12-mind-inspector`
**Depends on:** 12.1, 12.2, 12.3, 12.4
**Complexity:** Integration (chrome + data)
**Stage-1 ref:** §3.5, slice 6 — **Claude Design chrome + hand-coded data.**

Tabbed per-agent panel: **Belief · Prompt · Response · Memory · Flags** + a Thought→Action→Observation trail + "show what
they saw" (ties to the 12.3 fog). Impostor extras Omniscient-only (`fellow_impostor_ids`, cooldown, `own_kill` memory
line, cover-task marked **fabricated**).
**Claude Design prompt:** "Design the **agent mind-inspector** (tabbed: Belief / Prompt / Response / Memory / Flags), with
a reasoning trail and a 'what they saw' toggle. Mono for prompt/response/JSON. States: living / dead / impostor
(Omniscient) / no-agent-selected. Firewall: impostor-only fields appear **only in Omniscient**; cover-tasks labeled
'fabricated'. Presentational only; tokens only."
**Handoff/verify:** README (tabs, mono usage, Omniscient-gating, DoD) → Handoff → wire tabs to `AgentMemoryView` +
LLM-call data → verify all tabs + the Omniscient/fog gating + fabricated-cover labeling.

#### Task 12.9 — Replay browser + Highlights reel
**Branch:** `phase-12-browser-highlights`
**Depends on:** 12.1, 12.2
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

#### Task 12.10 — Dashboard refresh
**Branch:** `phase-12-dashboard`
**Depends on:** 12.1, 12.2
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

#### Task 12.11 — Accessibility, responsive, first-run, perf
**Branch:** `phase-12-polish`
**Depends on:** 12.5, 12.6, 12.7, 12.8, 12.9, 12.10
**Complexity:** Integration — **Hand-coded.**
**Stage-1 ref:** §8, §9, slice 9

Keyboard transport + focus + ARIA on data panels + reduced-motion + AA contrast + never-hue-only audit. Responsive
rail→drawer collapse. A first-run **guided mode** on a high-interestingness seed teaching the perspective switcher + the
two-truth grammar. Verify the code-split (Pixi vendor chunk + lazy Dashboard/Highlights) closed the 859 kB single chunk;
optionally add a Playwright visual smoke to CI (needs the loader + a served 9p2i set — sequence after build/typecheck).
**Acceptance:** a11y audit pass; responsive; guided mode; bundle split verified.
