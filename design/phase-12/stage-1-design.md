# Phase 12 — Stage 1: DESIGN

**Status:** FINAL (Stage 1 complete). Authored from the Stage-0 artifact + owner decisions, then revised against (1) an analogous-product survey and (2) an adversarial blind-spot critique that **broke the draft's per-tick-belief hero** (see §0 *What changed*). Ready for owner review → BUILD.
**Inputs:** `design/phase-12/stage-0-understand.md`; owner 2026-06-17 → art OPENED for Wave-0 exploration → **Playful chosen** (cream/ink; see §5 + `tokens-seed.md`), **scope = spectator replay viewer only**; analogous-product survey; adversarial critique (both archived in this thread).
**Audience:** Claude Design (chrome/tokens) + the BUILD threads (per-slice PRs).
**Closest prior art to study first:** *"Observer, Not Player"* (Theory-of-Mind in LLMs), arXiv 2512.19210 — an observer's probabilistic belief over hidden roles, explicitly diffed against ground truth. Almost exactly our centerpiece.

---

## 0. What changed from the draft (the critique's load-bearing corrections)

1. **The hero is per-MEETING, not per-tick.** Beliefs are "timeless" by an explicit Phase-4 decision (`api/schemas.py:424-433`); between meetings only Rules 1/4 fire (flat except body/vent bumps), games have a **median of 2 meetings (max 4; 7 games have 1)**, and the Rule-2 contradiction lift the agent voted on is computed on a throwaway copy and **never persisted**. A per-tick belief sparkline would be noise *and would disagree with the ballot*. → Belief × Truth is a **per-meeting snapshot with before→after steps**, using the already-existing `AgentMemoryView.beliefs`.
2. **Map fog (per-tick visibility) ≠ beliefs (per-meeting).** These are two different surfaces. Fog is a real, *not-free* per-tick visibility projection that must be built as **firewall-simulation code with its own leak test**.
3. **§4.6 verdict is per-meeting**, recomputed from persisted `ballot.confidence` (the un-persisted `rendered_max` is dropped).
4. **Kill self-channel uses the existing `KillEventView`** (already in `TickView.events`); `own_kill` is reserved for the Mind-inspector memory line.
5. **Lens model simplified** to *perspective switcher + belief panel* (base is always ground truth) to avoid "which truth am I seeing?" disorientation.
6. **9p2i is the target set**; 4p1i (the default-served, 68%-zero-meeting reference set) is handled with graceful empty states; rubric becomes **per-set with a staleness guard**.

---

## 1. Vision & principles

**Vision:** *see the game **and** every mind in it.* The most legible hidden-information replay viewer — it shows not just what happened, but **what each agent knew, believed, and decided, against the ground truth.** Frame the whole tool as the **omniscient "ghost/director" view** (genre-native); the *thing we surface* is how little each living agent actually knew.

**Principles:**
1. **Legibility is the hero** — the Belief × Truth surface (who suspects whom vs who's really the impostor) is the centerpiece; everything supports it.
2. **Two-truth honesty** — GROUND TRUTH renders solid/authoritative; AGENT BELIEF / WHAT-AGENT-SAW renders ghosted + attributed. One consistent grammar that mirrors the engine firewall in the UI — and **the UI must *simulate* that firewall, never inherit it** (the privileged viewer must not show an agent data it didn't have when in its perspective).
3. **One timeline** — a single engine tick drives map, fog, event strip, and the advantage graph. Belief is meeting-granular and snaps to the meeting on the timeline.
4. **Progressive disclosure** — overview → open one mind. The deep data (memory/prompt/LLM) is first-class, not 3 clicks deep.
5. **Honest uncertainty** — bucket suspicion (Low/Med/High), graded soft encoding, **"no belief yet" ≠ 0**, surface low-power/small-n caveats, mark impostor "cover" tasks as **fabricated** (never real progress).
6. **Themeable + accessible by construction** — tokens not magic constants; **never hue-only** (critical under the role-neutral constraint); reduced-motion; keyboard transport.
7. **Fast & precomputed** — the loader (which re-executes the engine) computes view-model surfaces server-side + caches; the browser renders.

---

## 2. Information architecture

### 2.1 Top-level
```
[ Replays ]   [ Highlights ]   [ Tournament ]      (Highlights & meeting-rich surfaces target the 9p2i set)
```
- **Replays** — browse/filter the served set. **Highlights** — rubric-driven reel of the most *interesting* seeds (9p2i). **Tournament** — aggregate dashboard.
- Selecting a replay opens the **Replay Workspace**. URL encodes `set / game_id / tick / perspective / beliefView / selectedAgent / selectedMeeting` → every moment is shareable + reload-stable.

### 2.2 Two controls, one base truth (simplified from "3 lenses")
The base is **always Ground Truth** (omniscient). Two independent, clearly-labeled overlays sit on top:

- **Perspective switcher** (map): **Omniscient** (default) ↔ **As [agent ▾]** → applies **fog of war** = only what that agent could see at this tick (per-tick visibility projection, §7). This is the Dota/SC2/poker "reveal toggle," fixed to (a) reveal **all** agents in omniscient mode and (b) **always offer the fog/"fair" mode** so you can judge whether a deduction was *reasonable given what the agent knew*.
- **Belief panel** (its own surface) with a **Belief / Ground-Truth / Error** toggle (same layout, swapped data — the poker range-grid idiom). Meeting-granular.

The **two-truth grammar binds to the overlay, not per-surface**: a persistent, dominant mode indicator shows the current perspective; ghosted/attributed = belief/what-was-seen, solid = ground truth. (Critique M4: this is the disorientation fix — there is always one base truth + at most two labeled overlays.)

### 2.3 Workspace layout
```
┌─ seed 5 · 9p/2i · ★80  ·  PERSPECTIVE: ( Omniscient ▾ )  ────────────────────┐  ← dominant mode banner
├──────────────┬──────────────────────────────────────────┬─────────────────┤
│ ROSTER       │                  STAGE                     │  MIND (agent X) │
│ + advantage  │   PLAY: vector top-down map               │  tabs: Belief · │
│   bar        │   MEETING: accusation table (tick∈meeting)│  Prompt·Reply·  │
│ 9 players,   │                                            │  Memory·Flags   │
│ alive/dead,  │                                            │  + "what X saw" │
│ role badge*  │                                            │                 │
├──────────────┴──────────────────────────────────────────┴─────────────────┤
│ ADVANTAGE GRAPH  crew▁▂▃▅▇ vs impostor  (clickable 2nd scrubber; key moments)│
│ EVENT TIMELINE  ▸kill ▸meeting ▸vent ▸sabotage ──●(now)── lanes: 1/agent    │
│ TRANSPORT  ⏮ ⏯ ⏭  «meeting ‹event  [──scrubber──]  1×▾  next-key-moment  t312│
└────────────────────────────────────────────────────────────────────────────┘
  *role badge shown in Omniscient; HIDDEN in As-agent fog (firewall).  Belief panel = an overlay on the roster rail / full-screen toggle.
```

---

## 3. Key surfaces

### 3.1 Replays browser & Highlights reel
- **Highlights** = `interestingness.per_game[]` (sorted best-first), **9p2i only**. HighlightCard: score badge (0–100), win-shape tag, drama line (n_meetings · accused/ejected impostors · survived-accused), 4-spoke mini-bar (r1/r2/r3/r7). Click → open at tick 0.
- **Replays** = filterable cards (set, winner, win-shape, score, has-ejection). **Zero-meeting / no-rubric games render a first-class empty state** (4p1i set, or 9p2i single-meeting games), not a broken panel. Join: `seed → game_id = headless-seed-{N}`.

### 3.2 Map stage (PLAY) — vector top-down "observatory"
- **Rooms** = geometric cells from real `(x,y)`+size; thin-stroke schematic look; hallways subordinate.
- **Agent tokens** = role-neutral identity color (never guilt) + small **action glyph** from `current_action` (the one render-ready surface; note `report`/`emergency`→REPORT, `repair_sabotage`→TASK collapse); **role badge only in Omniscient**. Tween between adjacent ticks (keep existing).
- **Vent-escape animation** = the Phase-11 lever made visible (today the token just vanishes). From a new `VentEventView` (engine already emits both endpoints + traversal_ticks; just not projected) animate dive→travel-along-`MapLayoutView.vents`→emerge. Highest-value new map motion.
- **Kill** = flash + body marker, sourced from the **existing `KillEventView{killer_id,victim_id,room_id}`** in `TickView.events` (no `own_kill` plumbing needed); persistent body attribution via a new `killed_by` projection from `state.bodies`.
- **Sabotage** = reactor tint on REACTOR/ENGINEERING + a genuine **per-room repair race** (`repair_progress` is really `Mapping[RoomId,int]`) + **countdown** (`remaining_ticks`); lights = visibility tint. All real, but **none is in any DTO yet** → additive projections (§7).
- **Fog (As-agent)** = dim to the agent's `visible_players/visible_bodies/audible_events` for this tick — **from the new per-tick visibility projection, not naive same-room dimming** (visibility is graph/lights-dependent via `compute_visibility_for_player`; a shortcut is wrong *and a leak*).

### 3.3 Belief × Truth — the hero (per-MEETING)
A **directed adjacency matrix** (rows = suspector, cols = suspected, color = suspicion) — chosen over node-link because the relation is dense N×N (node-link → hairball). Three-way toggle, same layout:
- **Belief** (who suspects whom), **Ground-Truth** (impostor columns marked — **Omniscient only; suppressed in fog**), **Error = Belief − Truth** (the honest view: **confidently-wrong cells rendered LOUD** — bright fill + thick border + ✗; a crewmate strongly suspecting the real impostor = "got it"; impostor column staying cool = "getting away with it").
- **Granularity = meeting snapshots** (`AgentMemoryView.beliefs`), with a **before→after step control** across the game's 2–4 meetings (small-multiples "rounds filmstrip" beats animation — change-blindness). Click a cell → that pair's suspicion across the meetings ("the moment it flipped"). Column-sum = a player's "heat" (how cornered).
- **"What changed this meeting"** diff: highlight which beliefs moved and pair it to the cause (a contradiction flag / a sighting). This replaces the (infeasible) per-tick diff.
- A **sparse node-link** view is reserved only for "active accusations *this* meeting" (signed edges **blue=trust / orange=distrust**, not red/green). Offer a **"freeze order"** toggle if the matrix is seriated (don't destroy the mental map every step).

### 3.4 Meeting view (MEETING) — accusation table
- **Chain as a threaded waterfall**: opening → replies (indented by `reply_to`) → opt-ins → vote; each TurnCard = speaker chip + structured claims/observations + free text (toggle).
- **Claim ↔ map cross-highlight** (survey TOP-pattern): hover "I saw Red in Electrical" → light up Red + Electrical + that agent's sightline on the map, and the overlay shows whether it matches truth. The single best legibility device for the transcript.
- **Contradictions**: draw the **link** between the two referenced turns; **weak vs strong** distinguished (dashed=weak/solid=strong) — exposed as a real `weak: bool`/severity field (today it's a string marker in `transcript.py:394`).
- **Ballots**: voter→target + confidence bar + rationale + `considered_alternatives`; the **§4.6 verdict** rendered as a **per-meeting** `gate{leader, leader_max_confidence, threshold 0.6, passed}` (recomputed from persisted ballots — *not* `rendered_max`). Mark vote *correctness* (targeted a real impostor) by **shape/label, not identity hue** (firewall-safe).
- **Rewrite-marker chips**: parse `TEAMMATE_VOTE_TARGET_MARKER` / `BALLOT_TARGET_REDIRECT_MARKER` / `VOTE_PARSE_DEFAULT_MARKER` etc. **server-side by importing the constants** (never hard-code in TS; they're duplicated in `voting.py`+`manager.py`, are `.format()`-interpolated → match prefix-up-to-`{`, and `VOTE_PARSE_DEFAULT` is the *entire* string). Emit `rewrite_reasons[] + rationale_text_clean`. Renders "coerced to SKIP (teammate)", "redirected", "parse-default" chips.
- **Outcome banner**: EJECTED/SKIPPED + reason in **role-neutral colors** (preserve `MeetingView.tsx:37-39` constraint).

### 3.5 Mind inspector (per agent) — front-of-house (LangSmith-trace structure)
Tabs for the selected agent: **Belief** (suspicion/trust per other player, meeting steps) · **Prompt** (the exact `render_for_prompt` text the LLM saw) · **Response** (raw structured output) · **Memory** (episodic feed: saw_player/saw_body/heard_vent/`own_kill`/…) · **Flags** (contradictions/markers affecting them). At meeting ticks, the `LLMCallCard` (model/tokens/cost) inline. A **Thought→Action→Observation** trail per decision. "Show what they saw" ↔ the map fog. Impostor extras (Omniscient): `fellow_impostor_ids`, cooldown, the `own_kill` memory line, and **pretend-task marked as fabricated cover**.

### 3.6 Tournament dashboard (refresh)
Keep the metrics; add: **typed `conversion` + `gate_metrics`** (sent on the wire, untyped today); **render the honesty caveats** — some already typed (`vote_correctness_small_n`, `contradictions_flagged_but_ignored`), plus low-power/populated-bins; an **interestingness distribution** linking into Highlights.

---

## 4. Playback / time model (the backbone)
- **Source of truth = engine tick** (one derived selector maps tick↔frame; kill the off-by-one in 3 places; treat the loader-injected `tick=-1` Start as a real pre-game value, not a sentinel).
- **Transport**: scrub · play/pause · speed (0.5–4×) · step ±N · **jump prev/next event** (kill/meeting/vent/sabotage) · **jump prev/next meeting** · **"next key moment."**
- **Advantage graph = clickable second scrubber** (chess eval-bar / KataGo winrate idiom): crew-vs-impostor advantage over ticks (tasks-remaining vs impostors-alive, from per-tick state) with kills/meetings/ejections as inflection points; click to seek.
- **Global crosshair**: hovering a tick ghosts a crosshair across the advantage graph + event lanes (Grafana shared-crosshair).
- **Everything derives from `currentTick`**; meetings are **time spans** (stage morphs to the table when `tick ∈ meeting.span`). **Auto-follow** (pan to next event) is **interruptible** (anti-pattern: don't yank the camera).
- **Playback in the store / `usePlayback` hook** (not buried in a control). **Keep** the existing payload windowing + lazy meeting bodies + async-ordering guards. Per-tick visibility/advantage frames are modest, but they're the one thing that inflates the single-payload model → fetch/window them per-tick if needed (the dead `/ticks/{t}` endpoint is the hook).

## 5. Art direction — **Playful** (cream / ink) · ⚠️ section below superseded by Wave 0

> **Wave-0 update (2026-06-17):** the art direction was OPENED for exploration (see the brief) and Wave 0 chose
> **DIRECTION 03 — Playful** (cream `#FBF4E6` + ink chunky-sticker; Fredoka / Space Mono) — **not** the dark "observatory"
> described below (that became the *rejected* Direction-01). **Authoritative palette + mood = `design/phase-12/tokens-seed.md`
> + `design/phase-12/playful-system/` (the rendered converge).** The text below is kept only for its still-valid
> STRUCTURE — the firewall color *system* (identity ≠ guilt, suspicion heat, trust↔distrust blue↔orange, status+shape),
> the two-truth grammar, and the motion list all carried into Playful — so read every "dark / near-black / observatory"
> cue as "cream / ink Playful."

*(original, superseded direction:)* vector / geometric, dark "observatory"
- **Mood:** calm, precise control-room for a reasoning testbed; schematic top-down map, thin strokes, generous negative space, dense-but-quiet. Dark-mode rules: near-black (not pure black) canvas, medium weight (thin halates), **mono for ticks/IDs/JSON/prompts**, restrained semantic accents.
- **Two-truth grammar (signature):** ground truth = solid; belief/inference/what-was-seen = ghosted + attributed. Bound to the perspective/overlay, applied everywhere (map fog, belief Error cells, claim cross-highlight).
- **Color (firewall-critical):** **identity** = existing deterministic per-player palette (never role/guilt); **truth reveal** = a *separate* channel — a real impostor is an explicit **icon/badge** in Omniscient, never a hue, and the **ground-truth ring is suppressed in fog**; **suspicion** = a sequential heat ramp distinct from identity; **trust↔distrust** = **blue↔orange** (colorblind-safe, avoids kill-red); **status** = semantic tokens, each paired with shape/text.
- **Motion (legibility-serving, reduced-motion aware):** token tween; **vent dive/emerge**; kill flash; map↔table morph (prototype this transition first — most disorienting); contradiction link-draw. No decorative motion.

## 6. Design system & tokens
- **One source `tokens.ts`** consumed by **both** Tailwind/DOM and the Pixi layer (hex→number) → zero magic constants in either layer.
- **Tiers:** primitives (neutral dark ramp, spacing, type, radii, elevation, motion, identity palette, suspicion ramp, status hues, trust/distrust blue-orange) → semantic (`bg/surface/border/text*`, `identity[]`, `suspicion.{low,med,high}`, `truth.{ground,belief}`, `status.{alive,dead,sabotage,contradiction-weak,contradiction-strong,accent}`) → component tokens. Type: UI sans + mono.
- **Components (layered `ui/`+`domain/`):** *ui:* Button, PlayerChip, Badge, Bar/Meter, Panel, Tabs, Tooltip, Toggle, **PerspectiveSwitcher**, **Transport**, **Timeline**, **AdvantageGraph**, Card, Sparkline, Histogram, MetricCaveat, EmptyState. *domain:* **MapStage** (RoomCell, AgentToken, VentPortal, BodyMarker, SabotageLayer, KillMarker, FogLayer), **BeliefMatrix**/**BeliefGraph**/BeliefCell, **MeetingTimeline** (TurnCard, ClaimRow, ContradictionLink, BallotRow, OutcomeBanner), **MindInspector** (MemoryView, PromptViewer, EpisodicFeed, LLMCallCard), **ReplayBrowser** (HighlightCard, Filters), **Dashboard** (StatTile, CalibrationCurve).
- **Anchors:** Storybook (story per component) + `frontend/CLAUDE.md` (tokens, do/don't, **the firewall color + fog-suppression rules**). Split `ContradictionBadge.tsx`'s smuggled utils into `lib/`.

## 7. The versioned view-model contract (data the design requires)
Introduce **`viewModelVersion`** + **generate TS from Pydantic** (end hand-mirroring/drift). All surfaces below are **additive loader projections from already-available re-walked state** — *not* data gaps — except the per-tick visibility projection (the one genuinely expensive new compute). Cost honestly; cache (LRU, as today).

| Surface | Shape (sketch) | Source / feasibility |
|---|---|---|
| **Per-meeting belief snapshot** | `AgentMemoryView.beliefs` (exists) + an **Error** projection vs `PlayerView.role` | exists today; add Error + before/after step indexing |
| **Per-tick visibility (fog)** | `visible_players/visible_bodies/audible_events` per agent per tick | **NEW + expensive**: derive from the packet during the `collect_memory` re-walk and **persist** (today discarded into a temp dir). **Ship with a UI leak test** mirroring `eval/leak_test.py`. |
| **Kill self-channel** | use existing `KillEventView` (+ `killed_by` from `state.bodies`) | already in `TickView.events`; no `own_kill` plumbing |
| **Vent events** | `VentEventView{tick,actor,from,to,traversal}` | engine emits `VentEntered/Exited`; add a `TickEventView` member |
| **Contradiction class** | `ContradictionView.weak:bool`(+severity) | compute `is_weak_contradiction()` at load |
| **Meeting §4.6 verdict** | `MeetingView.gate{leader,leader_max_confidence,threshold,passed}` | recompute from persisted `ballots[].confidence`; drop `rendered_max` |
| **Parsed ballot markers** | `BallotView.rewrite_reasons[]` + `rationale_text_clean` | parse server-side via imported constants; special-case `VOTE_PARSE_DEFAULT` |
| **Sabotage detail** | reactor `repair_progress` per room + `remaining_ticks` | from re-walked `SabotageState` |
| **Advantage series** | per-tick crew/impostor advantage | from re-walked state |
| **Rubric (per-set)** | `/eval/rubric` → `{seedset, git_head, per_game[]}` + **staleness guard** (compare to served set's MANIFEST `git_sha`) | read `results-rubric-score.json`; fail-loud/banner on set or sha mismatch |
| **Already in DTO, just render** | `current_action`, `winner_reason`, task-clock totals, `failed_calls`, typed `conversion`/`gate_metrics` | render-ready |
| *Abandoned, don't revive silently* | `SuspicionGraphView` (dead per-tick shape) | document *why* (the B1 timeless-belief reason) |

**Forward-compat (Phase D, don't build):** leave room for per-decision policy action-distributions, a per-meeting suspicion-rank vector, a per-game fitness scalar + generation id.

## 8. Cross-cutting
- **A11y:** keyboard transport, focus, ARIA on data panels, reduced-motion, contrast AA, **never hue-only**.
- **Responsive:** rails collapse to drawers; map + transport are the irreducible core.
- **First-run / guided mode:** annotated walkthrough on a high-interestingness seed teaching the perspective switcher + the two-truth grammar.
- **Honesty everywhere:** bucketed suspicion, "no belief yet" ≠ 0, graded soft uncertainty, low-power caveats, fabricated-cover labeling.

## 9. Architecture & build hygiene
- **Code-split:** `manualChunks` (Pixi + react-dom vendor chunk) + `React.lazy` Dashboard/Highlights → fix the 859 kB single chunk.
- **CI:** add `npm run build` + typecheck now; **Playwright visual smoke later** (it needs the FastAPI loader + a served 9p2i set in CI — non-trivial; sequence it after build/typecheck).
- **Codegen** TS from Pydantic; keep store guards/windowing/memoization; lift playback to a hook; one tick-number selector.

## 9.5 Claude Design integration & asset pipeline (researched 2026-06-17)
**Division of labor.** Claude Design (owner-driven, `claude.ai/design`, Opus-4.7, repo-aware) owns the **DOM chrome +
design system + tokens + SVG icon set** — it outputs HTML/CSS/JS + SVG + tokens, **not** React, **not** Pixi/canvas, **not**
raster. Claude Code hand-codes the **Pixi/WebGL map, data/state wiring, playback/interaction, and firewall-simulation /
leak correctness** — the handoff bundle provably cannot carry these.
**SVG map assets (corrects any earlier "art-directed separately from Claude" phrasing).** The vector map/room/icon SVGs
*are* generated with Claude — but via **Claude Code + a locked style-spec** (free-form SVG drifts in stroke/style across a
set; even Opus 4.7 underperforms on vector-art benchmarks), as standalone asset files loaded into the hand-coded Pixi
layer. No raster path (a third-party image MCP only if ever required).
**Workflow (best practice).** Design-system-first → **one durable workspace brief** (`design/phase-12/claude-design-brief.md`,
installed as `frontend/CLAUDE.md` in task 12.1) → **per-component focused prompts** → per-slice **Share → Handoff to Claude
Code** → integrate (compose from tokens, no hardcoded hex) → **screenshot-verify** (`claude --chrome` / Playwright, isolated
+ composed) → small PR → fresh-context review → next. **Anti-patterns:** one mega-prompt for all components; bulk
integration; wholesale regeneration over files holding hand-written logic.
**Caveats.** The official Design→Code path is the **one-way handoff bundle**; `DesignSync`/`/design-sync` is real but
**undocumented** — don't make it the backbone. Claude Design is paid / web-only / quota-metered and owner-driven (the build
agent cannot invoke it). Per-slice Claude-Design prompts + handoff/verify checklists live in **`tasks/phase-12.md`**.

## 10. BUILD slices (Stage 2 → one PR each; design-system-first, plan-mode, Playwright screenshot loop)
0. **Foundation** — tokens (`tokens.ts` for DOM+Pixi) + Storybook + `frontend/CLAUDE.md` + CI build/typecheck.
1a. **View-model contract v1 + cheap projections** — Pydantic + codegen TS; `viewModelVersion`; project vent events, `killed_by`, weak/strong, per-meeting §4.6 verdict, parsed markers, sabotage detail, advantage series, per-set rubric + staleness guard; render-ready surfaces. **Blocks slices 3–6.**
1b. **Per-tick visibility projection (fog) + UI leak test** — the expensive one; isolate it so its cost/risk doesn't block 1a.
2. **Playback backbone** — store/`usePlayback` hook, Transport, event timeline + lanes, advantage graph, crosshair, URL sync, tick selector.
3. **Map stage** — vector rooms/tokens/bodies + action glyphs + **vent-escape** + sabotage/repair + perspective switcher & fog (consumes 1b).
4. **Belief × Truth** — per-meeting matrix with Belief/Truth/Error + step control + cell drill + "what changed this meeting" + sparse accusation node-link.
5. **Meeting view** — chain waterfall, **claim↔map cross-highlight**, contradiction links (weak/strong), ballots (§4.6 verdict + marker chips), outcome.
6. **Mind inspector** — tabbed Belief/Prompt/Response/Memory/Flags + ToA trail + "what they saw."
7. **Replay browser + Highlights reel** — rubric cards + filters + **zero-meeting/empty states**.
8. **Dashboard refresh** — typed conversion/gate + honesty caveats + interestingness distribution.
9. **Polish** — a11y + responsive + first-run guided mode + perf/code-split verification.

## 11. Anti-patterns to avoid (baked into the above)
Reveal **all** agents (not one); always offer fog/"fair" mode; matrix-not-hairball; small-multiples filmstrip over animation; **first-class on-screen controls** (not console commands); interruptible auto-camera; "freeze order" on a seriated matrix; **no false precision** (bucket, soft-encode, "no data"≠0, blue↔orange).
