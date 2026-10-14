# Phase 12 — Front-end rework (spectator replay viewer · Playful cream/ink)

Goal: rebuild `frontend/` into the most *legible* hidden-information replay viewer — show what each agent knew/believed
vs ground truth — on the existing React 19 + PixiJS + Zustand + FastAPI-loader substrate. Owner decisions (2026-06-17):
art = **Playful** (cream + ink chunky-sticker, Fredoka/Space Mono; vector-rendered — the Wave-0 pick, see
`design/phase-12/tokens-seed.md` + `design/phase-12/playful-system/`); scope = spectator replay viewer only (no live, no
human player). (The earlier "vector/observatory" framing was the *rejected* dark Direction-01 — superseded by Playful.)

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
`claude.ai/design`; it is **not** something the build agent invokes. (`/design-sync` was evaluated and **PARKED 2026-06-18** — it's the wrong
tool for a bespoke single-surface viewer with ~1 reusable primitive; the per-slice **handoff** above is the path. Full
verdict in memory / [[project-phase-12-frontend-rework]].)

**Design coverage (what Wave-0's converge already designed vs what still needs Claude Design).** The 0b converge designed
the *hero replay-view* surfaces — tokens (→ 12.1), the map + perspective switcher + fog (→ 12.5 / 12.3), the 9×9
Belief/Truth/Error matrix (→ 12.6), and the meeting view (→ 12.7); their rendered targets live in
`design/phase-12/playful-system/screens/`. The remaining chrome — **12.8 mind inspector · 12.9 replay-browser/highlights
· 12.10 dashboard** — was deliberately NOT in the converge and each still needs **its own owner-run Claude Design pass at
its dispatch** — a focused prompt → Handoff to Claude Code, grounded on `CLAUDE.md` + `tokens-seed` (NOT a sync), per the
per-slice prompts in those tasks. The workspace shell + transport / advantage graph / event-timeline / roster rail (12.4) and 12.11's first-run
overlay are **hand-coded from tokens** — no Claude Design pass.

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

**0b DONE 2026-06-17 — converge delivered + vendored in-repo. Wave 0 is CLOSED.** Token sheet →
`design/phase-12/tokens-seed.md` (the 12.1 seed); the renderable converge (`.dc.html` + `support.js`) + 8 rendered
screenshots → `design/phase-12/playful-system/`. The exploration + converge prompts below are retained as provenance only
— nothing remains to run in Claude Design until the per-slice chrome passes (12.5–12.10).

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

0b landed (see the DONE note above): its token sheet seeds `tokens.ts` in **12.1**, and the chosen Playful system governs
every chrome slice.

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

### Task 12.3 — Per-tick visibility projection + UI leak test
**Branch:** `phase-12-visibility-projection`
**Depends on:** 12.2
**Section refs:** design/phase-12/stage-1-design.md §3.2 (fog), §7 (the visibility row of the view-model table), slice 1b; design/phase-12/stage-0-understand.md §0.5 (fog is the one genuinely-expensive projection); the firewall rules in design/phase-12/claude-design-brief.md
**Complexity:** Integration
**Files in scope:**
- api/replay_loader.py
- api/schemas.py
- frontend/src/types/api.ts
- tests/api/test_leak.py
- tests/api/test_view_model.py
**Files NOT in scope:**
- the map render layer + fog *rendering* — Task 12.5 consumes this projection
- engine/ and observation/ — read `compute_visibility_for_player` / the `ObservationPacket`; never change them; no re-record
- the per-meeting belief / contradiction / §4.6 projections — already shipped in 12.2

A hand-coded backend/loader projection (no Claude Design), deliberately isolated as the one genuinely-expensive compute so
it does not block the cheap 12.2 contract. Persist each living agent's per-tick **field of view** into the view-model so
the As-agent perspective can *simulate* the firewall rather than inherit it. Today `ReplayLoader._walk(collect_memory=True)` runs the full observation pipeline but
routes its audit to a throwaway `tempfile.TemporaryDirectory` and **discards the visibility** — only an `is_venting` bool
survived per tick (see the VentEventView note in `api/schemas.py` that explicitly reserves this for Task 12.3). Capture,
per tick per living agent, each agent's already-firewall-filtered observation packet — `visible_players` / `visible_bodies` (the visual field, from
`engine/visibility.py::compute_visibility_for_player`, graph- and lights-dependent; a naive same-room dim is both wrong
AND a leak) plus `audible_events` (a *separate* audio path, `ObservationService._audible_events` — vent-use-heard /
sabotage-alarm) — all of which `observation/service.py` already assembles per tick, and surface it as a per-tick
`AgentVisibilityView` attached to the agent's tick state. This is **the one genuinely-expensive new compute** (a visibility solve per living agent per tick):
reuse the pipeline output already produced inside the re-walk instead of re-solving, cost it honestly, and cache through
the existing LRU (window it like the other per-tick frames if it inflates the single payload). Ship a **UI leak test** in
`tests/api/test_leak.py` mirroring `eval/leak_test.py`'s recursive hidden-field walk: build the As-agent–filtered view for
a chosen agent across a committed 9p2i game and assert it never exposes a player, body, event, or field that agent could
not have seen at that tick (other-room presence, role, `fellow_impostor_ids`, kill attribution). The projection is a pure
function of the recorded actions — keep it byte-deterministic.
**Definition of done:** per-tick per-living-agent `visible_players` / `visible_bodies` / `audible_events` in the served
view-model, derived from `compute_visibility_for_player` (not same-room shorthand); a **UI leak test** mirroring
`eval/leak_test.py` asserts the As-agent filtered view leaks no unseen field across a committed 9p2i game; the projection
is cached + cost-bounded (no per-request recompute) and documented as the expensive one; the existing leak + determinism
tests stay green; NO re-record; `scripts/check.sh` is green.
**Public types introduced:**
- api.schemas.AgentVisibilityView
**Implementation hint:**
capture the packet the observation pipeline already builds inside the `collect_memory=True` re-walk — read its
`visible_players` / `visible_bodies` / `audible_events` instead of letting the temp-dir audit drop them; do NOT re-solve
visibility a second time. The As-agent view is a server-side projection (compute once, cache), never a client-side hide;
window the per-tick payload as the existing per-tick frames are windowed if it grows.
**Integration risk:**
this is the cost hotspot — a visibility solve per living agent per tick across a whole game; measure and cache or it
regresses load time. The leak surface is the entire point: the test must mirror `eval/leak_test.py`'s recursive
hidden-field walk (role, `fellow_impostor_ids`, kill attribution, cross-room presence) or a subtle leak ships. Reading the
engine visibility / observation modules must not perturb the engine walk — the existing leak + determinism tests must stay
green and the replays are not re-recorded.
**Ready-to-paste prompt:** `agent_prompts/task-12-3-visibility-projection.md`

### Task 12.4 — Playback backbone
**Branch:** `phase-12-playback`
**Depends on:** 12.2
**Section refs:** design/phase-12/stage-1-design.md §4 (the time model), §2.3 (workspace layout), slice 2; design/phase-12/stage-0-understand.md §0.5
**Complexity:** Integration
**Files in scope:**
- frontend/src/store/replayStore.ts
- frontend/src/hooks/usePlayback.ts
- frontend/src/lib/playback.ts
- frontend/src/components/ReplayControls.tsx
- frontend/src/App.tsx
**Files NOT in scope:**
- the map / belief / meeting / inspector surfaces — Waves B/C mount into the shell slots + read the transport
- api/ and the loader — the advantage series + per-tick events already ship from 12.2
- frontend/src/tokens.ts and the design system — 12.1

A hand-coded frontend-state task (no Claude Design — the handoff bundle cannot carry state/interaction). Lift playback out
of `ReplayControls.tsx` into the store plus a `usePlayback` hook so every surface derives from **one source of truth — the
engine tick**. Today the tick↔array-index mapping is re-derived in several spots (the
`ReplayControls` comment already flags "compare against the engine tick NUMBER, not the array index"); collapse it into
**one derived selector** and treat the loader-injected `tick = -1` Start as a real pre-game value, not a sentinel. Build
the full transport: scrub · play/pause · speed (0.5–4×, the existing `PlaybackSpeed`) · **step ±N** · **jump prev/next
event** (kill / meeting / vent / sabotage, from the per-tick `events`) · **jump prev/next meeting** · **next key
moment**. Add the **advantage graph as a clickable second scrubber** from the 12.2 `AdvantageView` per-tick series
(crew-vs-impostor, kills/meetings/ejections as inflection points; click to seek) and a shared hover **crosshair** across
the advantage graph + the event-timeline lanes (one lane per agent). **"Next key moment"** seeks to the next
advantage-graph **inflection** — the next tick carrying a kill, a body-report / meeting, an ejection, or a sabotage start
(the drama beats), ranked kill → meeting → ejection — distinct from the raw step / jump-event controls. Stand up the
**app shell** with pre-declared mount points at **two** levels so *every* Wave-B surface plugs in **without ever editing
`App.tsx`**: **(a)** a top-level view container (view state in the store, URL-synced; no router dependency) for
**Replays** + **Highlights** (→ 12.9), **Tournament** (→ 12.10), and the **Replay Workspace**; and **(b)** within the
workspace, named slots per stage-1 §2.3 — perspective banner, roster rail, **stage** (map↔meeting morph → 12.5 / 12.7),
**mind** panel (→ 12.8), a **belief-panel** mount (overlay / full-screen toggle → 12.6), the **advantage graph**, the
**event-timeline** lanes, and the **transport**. Confirm with a slot↔surface checklist that all of 12.5–12.10 (+
transport / advantage / timeline) have a mount; the slots ship as empty placeholders the Wave-B PRs fill (each owns its
component, never the shell). Add **URL sync** of
`set / game_id / tick / perspective / beliefView / selectedAgent / selectedMeeting` via `history.replaceState` +
`URLSearchParams` (there is no router today) so every moment is shareable + reload-stable — which means adding
`perspective` + `beliefView` to the store now (consumed later by 12.5 / 12.6). Meetings are **time spans**: the stage
morphs to the meeting table when `tick ∈ meeting.span`, and **auto-follow** (pan to the next event) is **interruptible**
(never yank the camera). Keep the existing payload windowing, lazy meeting bodies, and async-ordering guards intact.
**Definition of done:** all playback state lives in `replayStore` + a `usePlayback` hook (not in `ReplayControls`); the
tick↔index mapping is one derived selector with `tick = -1` handled and no off-by-one; the transport supports scrub /
play / speed / step ±N / jump-event / jump-meeting / next-key-moment; the advantage graph seeks on click and shares the
crosshair; the URL round-trips all seven keys (reload restores the exact moment); auto-follow is interruptible; the
shell exposes a pre-declared mount (slot or route) for **every** one of 12.5–12.10 plus transport / advantage / timeline,
verified by a slot↔surface checklist, so no Wave-B PR needs to touch `App.tsx`; windowing + lazy bodies + async-ordering
guards are preserved;
`npm run tsc:check` + `npm run build` pass and `scripts/check.sh` is green.
**Implementation hint:**
the store already holds `currentTick` / `isPlaying` / `playbackSpeed` / `selectedMeetingId` / `selectedAgentId` — extend
it with `perspective` / `beliefView` plus the single derived tick selector rather than starting fresh, and move the
auto-advance timer out of `ReplayControls` into `usePlayback`. Drive jump-event / jump-meeting off the per-tick `events`
list and the meetings list, comparing engine tick numbers, never array indices. Do the URL sync with `replaceState` +
`URLSearchParams` (no router dependency) and debounce it so scrubbing does not thrash history.
**Integration risk:**
the off-by-one is the trap — the current index/tick conflation is re-derived in multiple places; the single selector must
treat `tick = -1` as real and stay consistent across transport, events, meetings, and the advantage scrubber, or
surfaces disagree. The shell-slot layout is load-bearing for Wave 3: define stable mount points now so the parallel
chrome PRs do not collide in `App.tsx`. Preserve the store's async-ordering guards + payload windowing — a naive rewrite
reintroduces the race and the payload inflation they already fixed. Finally, 12.3 regenerates
`frontend/src/types/api.ts` in parallel (it adds `AgentVisibilityView`); 12.4 only *reads* `AdvantageView` and never
writes that file, so there is no scope conflict — but whichever of 12.3 / 12.4 merges second should rebase and recompile
against the regenerated types.
**Ready-to-paste prompt:** `agent_prompts/task-12-4-playback.md`

---

## Wave B — Surfaces (chrome via Claude Design; logic hand-coded)

> **Mount discipline (parallel-dispatch guarantee):** every Wave-B surface mounts into a slot or route that **12.4
> pre-declares**, and **none lists `App.tsx` in scope.** If a surface needs a mount 12.4 didn't provide, fix 12.4 — a
> per-surface `App.tsx` edit reintroduces the collision the shell slots exist to prevent. (Enforce when elaborating each
> contract: no `App.tsx` in Files-in-scope.)

### Task 12.5 — Map stage (vector Pixi + SVG assets + fog)
**Branch:** `phase-12-map-stage`
**Depends on:** 12.1, 12.2, 12.3, 12.4
**Section refs:** design/phase-12/stage-1-design.md §3.2, §5, slice 3; the rendered targets `design/phase-12/playful-system/screens/02-map.png` + `03-two-truths.png` (Omniscient + As-agent fog) and the `renderMap` code in `playful-system/playful-system.dc.html`; `design/phase-12/canonical_1-map-reference.svg` (the fixed layout); the firewall rules in `design/phase-12/claude-design-brief.md`
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/MapView.tsx
- frontend/src/components/RoomRect.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/components/BodyMarker.tsx
- frontend/src/components/VentEdge.tsx
- frontend/src/components/SabotageOverlay.tsx
- frontend/src/components/MapToolbar.tsx
- frontend/src/assets/map/
- frontend/src/stories/MapStage.stories.tsx
**Files NOT in scope:**
- frontend/src/App.tsx — the shell + its persistent PerspectiveBanner are 12.4's; the perspective *switcher control* mounts inside the map stage (its toolbar) and drives the store, never editing the shell (Wave-B mount discipline)
- api/ and the loader — `MapLayoutView` / `AgentVisibilityView` / `KillEventView` already ship; no DTO change, no re-record
- the belief / meeting / inspector surfaces — other Wave-B slices

Rebuild the map **stage** the App.tsx slot already mounts (`<MapView/>`). Hand-code the Pixi/WebGL render layer (the handoff
bundle cannot carry canvas): rooms from real `(x,y)`+size out of the `MapLayoutView` DTO (`canonical_1`'s fixed 10 rooms /
11 corridors / 6-vent ring — reference `canonical_1-map-reference.svg`, never invent / move / rename), agent tokens
(identity colour via `pixiHex`, action glyph from `current_action`, role badge **Omniscient-only**), bodies
(`KillEventView` + `killed_by`), the **vent-escape animation** (dive → travel along `MapLayoutView.vents` → emerge — the
Phase-11 lever made visible), reactor tint + per-room repair race + countdown, and lights tint. **As-agent fog** dims to
the 12.3 `AgentVisibilityView` (never a naive same-room dim — that is a leak). Every colour / space flows through
`tokens.ts` via `pixiHex`; zero magic constants. The map **SVG asset set** (room outlines + action / vent / body / status
icons) is generated by **Claude Code with a locked style-spec** (locked stroke weight / corner radius / grid unit;
identity + status token palette; geometric-line only; one viewBox convention; one `.svg` per asset under
`frontend/src/assets/map/`) — this is NOT the Claude Design product (free-form SVG drifts across a set). The surrounding
**map chrome** — the toolbar + perspective switcher, NOT the canvas — comes from a focused Claude-Design prompt: *"Using
our design system + frontend/CLAUDE.md, design the map toolbar + perspective switcher (Omniscient ↔ As-agent [agent
picker]); states omniscient / agent-selected / no-replay; make perspective a dominant, persistent mode cue (two-truth
grammar); presentational only, compose from tokens, no hardcoded hex"* → Share → Handoff to Claude Code → integrate, then
screenshot-verify the toolbar isolated + over the live map.
**Definition of done:** the rebuilt vector map renders rooms / tokens / bodies / vents from the DTOs (layout faithful to
`canonical_1-map-reference.svg`), with the vent-escape animation, the sabotage / repair race + countdown, and lights;
**As-agent fog** dims to `AgentVisibilityView` with role badges + ground-truth markers suppressed in fog (verified against
the 12.3 leak guard — no unseen agent / body shows); the perspective switcher drives the store and the shell banner
reflects it; the SVG asset set is visually cohesive (locked style-spec); a Storybook story renders the stage Omniscient +
As-agent; `npm run tsc:check` + `npm run build` pass and `scripts/check.sh` is green; `App.tsx` is untouched.
**Implementation hint:**
the App.tsx slot already imports `<MapView/>` — rebuild that component and its Pixi children in place; do not add a slot
or edit the shell. Drive fog off the per-tick `AgentVisibilityView` the loader now serves (dim, do not delete — the
firewall is enforced server-side; never re-derive visibility client-side). Pull every colour through `pixiHex` so canvas
and DOM share one token source. Match the cream stage in the committed `02-map` render and the fog framing in
`03-two-truths`.
**Integration risk:**
the fog is the firewall surface — dim to exactly what `AgentVisibilityView` exposes; painting a token / body the agent
could not see is a leak (check the 12.3 guard). The perspective switcher must drive the store without editing the shell's
banner, or the Wave-B mount discipline breaks. Only the toolbar comes from the handoff — do not let a CD bundle overwrite
the hand-coded canvas. SVG drift across the asset set is the classic free-form-vector failure mode; hold the style-spec.
**Ready-to-paste prompt:** `agent_prompts/task-12-5-map-stage.md`

### Task 12.6 — Belief × Truth (the hero, per-meeting)
**Branch:** `phase-12-belief-truth`
**Depends on:** 12.1, 12.2, 12.4
**Section refs:** design/phase-12/stage-1-design.md §3.3, slice 4; the rendered targets `design/phase-12/playful-system/screens/04-matrix-belief.png` / `04-matrix-ground-truth.png` / `04-matrix-error.png` and the `renderMatrix` code in `playful-system/playful-system.dc.html`; the firewall + "no belief yet ≠ 0" rules in `design/phase-12/claude-design-brief.md`
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/BeliefMatrix.tsx
- frontend/src/components/BeliefRow.tsx
- frontend/src/components/BeliefCell.tsx
- frontend/src/components/BeliefPanel.tsx
- frontend/src/stories/BeliefMatrix.stories.tsx
**Files NOT in scope:**
- frontend/src/App.tsx — the belief slot already mounts `<BeliefMatrix/>`; rebuild the component, don't edit the shell (Wave-B mount discipline)
- api/ and the loader — `BeliefFrameView` + the per-meeting belief / signed-error projection already ship (12.2); no DTO change, no re-record
- the map / meeting / inspector surfaces — other Wave-B slices

Rebuild the **hero** surface the App.tsx slot mounts (`<BeliefMatrix/>`): a directed adjacency **matrix** (rows =
suspector, cols = suspected, cell = suspicion heat, bucketed Low / Med / High off `tokens.ts` `suspicionBucket`) with a
**Belief / Ground-Truth / Error** segmented toggle — same layout, swapped data, driven by the store's `beliefView`.
Ground-truth impostor markers are **Omniscient-only and suppressed in fog** (an icon, never a hue). The **Error** layer
(the DTO's signed `error` = Belief − Truth) renders confidently-wrong cells **LOUD** — fill + thick border + ✗ glyph, not
hue alone. Render **"no belief yet" ≠ 0** as a distinct hatched cell (the DTO flags it; never paint it as low suspicion —
a binding honesty rule). Granularity is **per-meeting snapshots** (`BeliefFrameView`) with a before → after **step
control** across the game's 2–4 meetings (small-multiples, not animation); click a cell → that pair's suspicion across
meetings + a "what changed this meeting" diff. Reserve a sparse **node-link** for "active accusations this meeting"
(signed edges blue = trust / orange = distrust). The matrix chrome — the segmented toggle, step control, and cell-detail
popover — comes from a focused Claude-Design prompt: *"Design the Belief × Truth matrix panel: an N×N suspicion matrix
(heat ramp, bucketed Low / Med / High), a Belief / Ground-Truth / Error segmented toggle, a meeting step control, a
cell-detail popover; states 1 meeting / multiple / no-meeting (empty); firewall — identity ≠ guilt, the ground-truth
marker is an icon that must be hideable (fog), Error cells LOUD via fill+border+glyph (not hue alone), 'no belief yet' ≠
0; presentational only, tokens only"* → Share → Handoff to Claude Code → wire to the per-meeting snapshots, then verify
the three toggle layers + the empty state + fog-suppression.
**Definition of done:** the matrix renders all three layers (Belief / Ground-Truth / Error) from `BeliefFrameView`, driven
by the store's `beliefView`; ground-truth markers are Omniscient-only and suppressed in fog; Error cells render LOUD (fill
+ border + glyph, never hue-only); "no belief yet" is a distinct hatched cell (≠ 0); the per-meeting step control,
cell-detail popover, and empty (no-meeting) state all work; the result matches the committed `04-matrix-belief` /
`04-matrix-ground-truth` / `04-matrix-error` renders; a Storybook story covers the three layers + empty state;
`npm run tsc:check` + `npm run build` pass and `scripts/check.sh` is green; `App.tsx` is untouched.
**Implementation hint:**
the slot already imports `<BeliefMatrix/>` — rebuild it plus its `BeliefRow` / `BeliefCell` children in place, and put the
toggle / step / popover chrome (from the handoff) in a `BeliefPanel` wrapper, all composed from `tokens.ts`. Drive the
three layers off the store's `beliefView` and the `BeliefFrameView` data (Belief = suspicion, Ground-Truth = the role
marker, Error = the signed `error` field), and suppress the ground-truth marker whenever perspective is As-agent. Match
the committed `04-matrix-belief` / `04-matrix-ground-truth` / `04-matrix-error` renders.
**Integration risk:**
the firewall lives in this surface — the ground-truth marker MUST vanish in fog (As-agent), and Error / correctness must
read by shape + glyph, not hue (role-neutral). Rendering "no belief yet" as 0 violates a binding honesty rule — key on the
DTO flag. Beliefs are per-MEETING (timeless), not per-tick, so the step control walks meetings, not ticks (a per-tick
sparkline would disagree with the recorded ballot). Don't edit `App.tsx` (mount discipline).
**Ready-to-paste prompt:** `agent_prompts/task-12-6-belief-truth.md`

### Task 12.7 — Meeting view
**Branch:** `phase-12-meeting-view`
**Depends on:** 12.1, 12.2, 12.4, 12.5
**Section refs:** design/phase-12/stage-1-design.md §3.4, slice 5; the rendered target `design/phase-12/playful-system/screens/05-meeting.png` and the accusation-chain / ballots / `verdict` code in `playful-system/playful-system.dc.html`; the firewall (role-neutral outcome) + the REAL §4.6 rule in `design/phase-12/claude-design-brief.md`
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/MeetingView.tsx
- frontend/src/components/TurnCard.tsx
- frontend/src/components/BallotCard.tsx
- frontend/src/components/MeetingPill.tsx
- frontend/src/store/replayStore.ts
- frontend/src/components/MapView.tsx
- frontend/src/stories/MeetingView.stories.tsx
**Files NOT in scope:**
- frontend/src/App.tsx — the meeting already mounts in the existing overlay slot (`<MeetingView/>`); rebuild the component, don't edit the shell (Wave-B mount discipline)
- api/ and the loader — `TurnView` / `BallotView` / `GateView` / `ContradictionView` (weak/strong + `rewrite_reasons`) already ship from 12.2; no DTO change, no re-record
- the belief / mind surfaces — other Wave-B slices

Rebuild the meeting surface the App.tsx overlay slot mounts (`<MeetingView/>`): the accusation chain as a threaded
**waterfall** (TurnCards indented by `reply_to`, speaker chip + structured claims / observations + a free-text toggle);
the **claim↔map cross-highlight** — hovering "saw Red in Electrical" lights the claim's PUBLIC referent — the room + agent NAMED in the transcript (public, safe in any perspective; the sightline and does-it-match-truth overlay are Omniscient-only, and in As-agent fog the highlight reveals no position the fog has hidden),
the single best legibility device for the transcript; contradiction **links** drawn weak = dashed / strong = solid (from
`ContradictionView.weak`); a ballots section (`BallotView`: voter→target, confidence bar, rationale, **rewrite-marker
chips** from `rewrite_reasons`, vote correctness by **shape / label, not hue**); and a **role-neutral** outcome banner.
The per-meeting **§4.6 verdict** renders from `GateView` — the REAL rule (plurality + at least one leader ballot ≥ 0.6,
tie → SKIP). The converge mock's "simple majority of living voters" copy is WRONG — do NOT replicate it. The
cross-highlight is hand-wired: a shared store field set on TurnCard hover, read by `MapView` to light the room + agent (an
additive overlay — do not touch 12.5's fog / leak logic). The transcript chrome (TurnCard / ballot / banner layout) comes
from a focused Claude-Design prompt: *"Design the meeting transcript view: a threaded accusation waterfall of TurnCards
(speaker chip, structured claims + free-text toggle), a contradictions section (weak=dashed / strong=solid links), a
ballots section (voter→target, confidence bar, rationale, marker chips, a §4.6 gate readout), and a role-neutral outcome
banner; states chain / single-turn / skipped / ejected; firewall — outcome + correctness role-neutral (shape/label, not
red/green); presentational only, tokens only"* → Share → Handoff to Claude Code → integrate.
**Definition of done:** the threaded waterfall renders (indented by `reply_to`); the claim↔map cross-highlight works
(hovering a sighting lights the claim's public referent — the named room + agent — with any sightline / truth-match overlay Omniscient-only and no fogged position revealed in As-agent); contradiction links render weak = dashed / strong = solid;
ballots show voter→target + confidence + rationale + rewrite-marker chips + correctness by shape / label (not hue); the
§4.6 readout comes from `GateView` (plurality + ≥ 0.6, tie → SKIP — NOT "majority"); the outcome banner is role-neutral;
the result matches the committed `05-meeting` render; a Storybook story covers chain / single-turn / skipped / ejected;
`npm run tsc:check` + `npm run build` pass and `scripts/check.sh` is green; `App.tsx` is untouched.
**Implementation hint:**
rebuild `MeetingView` + `TurnCard` / `BallotCard` in place. Add a shared highlight field to `replayStore` (e.g.
`highlightedSighting: {agentId, roomId} | null`), set it on TurnCard hover, and read it in `MapView` to light the room +
agent — an additive overlay that must not perturb 12.5's fog logic. Render the §4.6 readout from `GateView` (never the
converge mock's "majority" text); draw contradiction weak / strong from `ContradictionView.weak`; the rewrite chips from
`rewrite_reasons` + `rationale_text_clean`.
**Integration risk:**
the cross-highlight touches the already-merged `MapView` (12.5) — keep it strictly additive (a highlight overlay reading
the store) so the fog + leak behaviour is unchanged. The highlight lights ONLY the claim's public referent (the named
room / agent), never a ground-truth position the current As-agent perspective has fogged; the sightline / truth-match
overlay is Omniscient-only — a hover handler that peeks at fogged ground truth is exactly the leak class this project
guards. The §4.6 readout MUST use `GateView`'s real rule (plurality + ≥ 0.6,
tie → SKIP); the converge mock literally renders the wrong "simple majority" copy, so do not copy its text. Outcome +
vote-correctness must read by shape / label, never red-vs-green (role-neutral firewall). Don't edit `App.tsx` (mount
discipline).
**Ready-to-paste prompt:** `agent_prompts/task-12-7-meeting-view.md`

### Task 12.8 — Mind inspector
**Branch:** `phase-12-mind-inspector`
**Depends on:** 12.1, 12.2, 12.3, 12.4
**Section refs:** design/phase-12/stage-1-design.md §3.5, slice 6; the firewall + Omniscient-gating rules in `design/phase-12/claude-design-brief.md`. NO converge screen exists for this surface — it needs a NEW Claude-Design pass (grounded on the brief + `tokens-seed`, via the §9.5 handoff; not a sync).
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/MindInspector.tsx
- frontend/src/components/ThoughtStream.tsx
- frontend/src/components/MemoryPanel.tsx
- frontend/src/components/LLMCallCard.tsx
- frontend/src/components/AgentSelector.tsx
- frontend/src/stories/MindInspector.stories.tsx
**Files NOT in scope:**
- frontend/src/App.tsx — the mind slot already mounts `<ThoughtStream/>`; keep that export and render `MindInspector` inside it, don't edit the shell (Wave-B mount discipline)
- api/ and the loader — `LLMCallView` (`prompt_text` / `response_text`), `AgentMemoryView`, `ContradictionView`, and the omniscient ground truth (`PlayerView.role`, `KillEventView`) already ship; no DTO change, no re-record
- the map / meeting / belief surfaces — other Wave-B slices

Rebuild the mind slot: keep the `ThoughtStream` export (the slot the App.tsx workspace mounts) and have it render a new
`MindInspector` — a tabbed per-agent panel. **Belief** (this agent's suspicion / trust of each other player, with the
meeting steps — the per-agent reasoning *detail*, complementary to 12.6's cross-agent matrix, NOT a duplicate) ·
**Prompt** (`LLMCallView.prompt_text` — the exact text the LLM saw, mono) · **Response** (`LLMCallView.response_text`,
mono) · **Memory** (`AgentMemoryView` episodic feed: saw_player / saw_body / heard_* / `own_kill`) · **Flags**
(contradictions / markers affecting them, from `ContradictionView`) — plus a **Thought → Action → Observation** trail per
decision. A **"show what they saw"** control drives the store (`setPerspective(agent)` + `selectAgent`) so the 12.5 map
fogs to that agent — no map edit, the map already reacts. **Impostor extras** (`fellow_impostor_ids`, the `own_kill` memory line, and the cover-task marked **fabricated**) are
gated **Omniscient OR when the perspective lens IS the inspected agent itself** — an impostor viewing its own mind is its
own knowledge, not a leak, so "show what they saw" on an impostor (which flips to As-agent-self) correctly keeps its
secrets visible. They are suppressed ONLY when inspecting an impostor through a DIFFERENT agent's eyes (a real leak). They
derive from the omniscient ground truth already in the view-model (the roster's roles → fellow impostors; `KillEventView`
→ own kills).
Consolidate the existing `MemoryPanel` / `LLMCallCard` / `AgentSelector` into the tabs. This surface has no converge
reference, so its chrome comes from a NEW focused Claude-Design pass: *"Design the agent mind-inspector (tabbed: Belief /
Prompt / Response / Memory / Flags) with a reasoning trail and a 'what they saw' toggle; mono for prompt / response /
JSON; states living / dead / impostor (Omniscient) / impostor-viewing-itself / no-agent-selected; firewall — impostor-only
fields appear in Omniscient or when the lens is that impostor itself, cover-tasks labelled 'fabricated'; presentational
only, tokens only"* → Share → Handoff to Claude Code →
integrate.
**Definition of done:** the tabbed Belief / Prompt / Response / Memory / Flags inspector renders via the existing
`ThoughtStream` slot (App.tsx unchanged); Prompt / Response read `LLMCallView` (mono); Memory reads `AgentMemoryView`; the
Thought → Action → Observation trail renders; "show what they saw" switches the map to that agent's fog (store-driven, no
map edit); impostor extras appear in Omniscient OR when the perspective lens is the inspected impostor itself, and are
suppressed only when inspecting an impostor through a different agent's perspective; cover-tasks are labelled fabricated; a Storybook story covers living / dead / impostor (Omniscient) / no-agent-selected; `npm run tsc:check` +
`npm run build` pass and `scripts/check.sh` is green; `App.tsx` is untouched.
**Implementation hint:**
keep the `ThoughtStream` export (the slot) and have it render the new `MindInspector`; fold `MemoryPanel` / `LLMCallCard`
/ `AgentSelector` into the tabs. Prompt / Response tabs read `LLMCallView.prompt_text` / `response_text` (mono, verbatim).
"Show what they saw" is just `setPerspective(agent)` + `selectAgent` — the 12.5 map already fogs to the selected agent, so
no map edit. Derive impostor extras from the omniscient ground truth (roles → fellow impostors; `KillEventView` → own
kills) and gate every one of them on perspective = Omniscient.
**Integration risk:**
the firewall gate is Omniscient OR self-perspective — an impostor's secrets (`fellow_impostor_ids` / `own_kill` /
fabricated-cover) show to Omniscient and to As-agent-of-that-same-impostor (the agent's own knowledge), but MUST disappear
when inspecting an impostor through a DIFFERENT agent's eyes (the real leak). A blanket "suppress in all As-agent" is
WRONG — it would hide an impostor's own team from its own perspective. Prompt / Response are the agent's actual LLM I/O — render them
mono + verbatim. This is the per-agent belief *detail*; 12.6's matrix is the cross-agent overview — don't duplicate it.
There is no converge screen, so verify the chrome against the brief's firewall rules, not a screenshot. Don't edit
`App.tsx` (mount discipline).
**Ready-to-paste prompt:** `agent_prompts/task-12-8-mind-inspector.md`

### Task 12.9 — Replay browser + Highlights reel
**Branch:** `phase-12-browser-highlights`
**Depends on:** 12.1, 12.2
**Section refs:** design/phase-12/stage-1-design.md §3.1, §2.1, slice 7; the firewall rules in `design/phase-12/claude-design-brief.md`. No converge screen exists for this top-level surface — it needs a NEW Claude-Design pass (a focused prompt → Handoff, grounded on the brief + `tokens-seed`).
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/HighlightCard.tsx
- frontend/src/components/ReplayFilters.tsx
- frontend/src/stories/ReplayBrowser.stories.tsx
**Files NOT in scope:**
- frontend/src/App.tsx — the Replays + Highlights routes already mount `<ReplayPicker/>`; rebuild the component, don't edit the shell (Wave-B mount discipline)
- api/ and the loader — the `/replays` list + `/eval/rubric` (`RubricView` / `RubricGameView`) already ship from 12.2; no DTO change, no re-record
- the map / belief / meeting / inspector surfaces — other slices

Rebuild the two top-level views the App.tsx routes mount through `<ReplayPicker/>`: the **Replays browser** and the
**Highlights reel**. A **HighlightCard** (from `RubricGameView`): a 0–100 **score** badge (decoupled from who won), the
**win-shape** tag, a **drama** line (n_meetings · accused / ejected impostors · survived-accused), and a 4-spoke mini
**sub-score** bar (R1 / R2 / R3 / R7). The **Highlights** reel defaults to the rubric's `interestingness` `per_game[]`
sorted best-first (**9p2i**). A **filter bar** that is **URL-driven** — it reads + syncs the shared query keys `set` · `winner` · `winShape` ·
`scoreBucket` (low/med/high) · `hasEjection` (the same URLSearchParams pattern as 12.4, so a filtered reel is shareable +
reload-stable and 12.10's histogram deep-links land on the right filter — 12.10 builds links with exactly these keys).
**Clicking a card opens that replay** — it sets the 12.4 store's `game_id` (which loads the replay) and switches to the
Replay Workspace at tick 0. And **first-class
empty / zero-meeting states** — the default-served **4p1i** set has no rubric and is mostly zero-meeting, so an empty /
zero-meeting card is the COMMON case there, not an edge: render a real state, never a broken panel. Firewall: identity ≠
guilt, and outcomes stay role-neutral (the card keys on drama / score, never on who won). Data-bound — wire to `/replays`
(the list) + `/eval/rubric` (`RubricView`, respecting its staleness guard). The chrome (HighlightCard, filter bar, empty
state) comes from a NEW Claude-Design pass: *"Design the replay browser + highlights reel: a HighlightCard (0–100 score
badge, win-shape tag, drama stats, a 4-spoke mini sub-score bar), a filter bar, and a prominent empty / zero-meeting
state; states loading / list / empty / error; identity ≠ guilt, outcomes role-neutral; presentational only, tokens
only"* → Share → Handoff to Claude Code → integrate.
**Definition of done:** the Replays browser + Highlights reel render via the existing `ReplayPicker` slot; HighlightCards
show score / win-shape / drama / 4-spoke sub-scores from `RubricGameView`; the reel sorts by `interestingness` (9p2i); the
filter bar is URL-driven over the shared keys `set` / `winner` / `winShape` / `scoreBucket` / `hasEjection` (reads + syncs them — shareable / reload-stable); clicking a card opens that replay (sets the 12.4 store `game_id`, switches to the Workspace at tick 0); a first-class empty / zero-meeting state handles the
4p1i + single-meeting cases; loading / list / empty / error states render; identity ≠ guilt and outcomes role-neutral; a
Storybook story covers loading / list / empty / error; `npm run tsc:check` + `npm run build` pass and `scripts/check.sh`
is green; `App.tsx` is untouched.
**Implementation hint:**
rebuild `ReplayPicker` in place; build `HighlightCard` from `RubricGameView` (`score`, `win_shape`, `n_meetings`, the
four sub-scores). The reel is `RubricView.per_game` (already sorted best-first); the browser list is `/replays`. Respect
the `RubricView` staleness guard (banner when `git_head` mismatches; never render stale scores as fresh), and build the
zero-meeting / 4p1i empty state first — do not assume rubric data exists.
**Integration risk:**
the 4p1i default set has no rubric and is mostly zero-meeting, so the empty / zero-meeting state is the COMMON path there,
not an afterthought. Score is decoupled from the winner — never colour a card by who won (outcomes are role-neutral, a
firewall rule). `RubricView` can be stale (a `git_head` mismatch) — show the staleness banner rather than passing stale
scores off as fresh. No converge screen — verify the chrome against the brief, not a screenshot. Don't edit `App.tsx`
(mount discipline).
**Ready-to-paste prompt:** `agent_prompts/task-12-9-browser-highlights.md`

### Task 12.10 — Dashboard refresh
**Branch:** `phase-12-dashboard`
**Depends on:** 12.1, 12.2
**Section refs:** design/phase-12/stage-1-design.md §3.6, slice 8; the honesty rules ("no false precision") in `design/phase-12/claude-design-brief.md`. No converge screen — a NEW Claude-Design pass (a focused prompt → Handoff, grounded on the brief + `tokens-seed`).
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/TournamentDashboard.tsx
- frontend/src/components/StatTile.tsx
- frontend/src/components/CalibrationCurve.tsx
- frontend/src/components/MetricCaveat.tsx
- frontend/src/stories/TournamentDashboard.stories.tsx
**Files NOT in scope:**
- frontend/src/App.tsx — the Tournament route already mounts `<TournamentDashboard/>`; rebuild the component, don't edit the shell (Wave-B mount discipline)
- api/ and the loader — `/eval/tournament-report` (typed `conversion` + `gate_metrics`) + `/eval/rubric` already ship from 12.2; no DTO change, no re-record
- the browser / map / belief / meeting / inspector surfaces — other slices

Refresh the tournament dashboard the App.tsx Tournament route mounts (`<TournamentDashboard/>`): keep the existing
metrics; surface the **typed `conversion` + `gate_metrics`** (sent on the wire, typed by 12.2); **render the honesty
caveats** — small-n / low-power / populated-bins badges (`vote_correctness_small_n`, `contradictions_flagged_but_ignored`,
…) **attached to the metric each one qualifies** (never a bare metric — that is false precision, a binding honesty rule);
**StatTiles** + a **calibration curve**; and an **interestingness histogram** (from `RubricView`) whose buckets **deep-link into the Highlights reel** by building a Highlights-view URL with the **shared filter keys 12.9
reads** — `scoreBucket=<bucket>` (+ the current `set`), never an invented param. Data-bound — wire to `/eval/tournament-report` (typed) + `/eval/rubric`. The
chrome comes from a NEW Claude-Design pass: *"Refresh the tournament dashboard: StatTiles, a calibration curve, a
metric-caveat treatment (small-n / low-power badges), and an interestingness histogram; states loading / loaded /
no-report; presentational only, tokens only"* → Share → Handoff to Claude Code → integrate.
**Definition of done:** the dashboard renders via the existing `TournamentDashboard` slot; the typed `conversion` +
`gate_metrics` render; the honesty caveats (small-n / low-power / populated-bins) render as badges attached to the metrics
they qualify (no bare metric); a calibration curve + StatTiles render; an interestingness histogram links into the
Highlights reel; loading / loaded / no-report states render; a Storybook story covers them; `npm run tsc:check` +
`npm run build` pass and `scripts/check.sh` is green; `App.tsx` is untouched.
**Implementation hint:**
refresh `TournamentDashboard` in place; wire to `/eval/tournament-report` (the typed `conversion` / `gate_metrics`) +
`/eval/rubric` (the histogram). Render each caveat badge ATTACHED to the metric it qualifies (the honesty rule — never a
bare number). The histogram buckets deep-link to the Highlights view by building a URL with the shared filter keys 12.9 reads —
`scoreBucket=<bucket>` + the current `set` (NOT an invented `?bucket=`); target the route (present since the 12.4 shell)
so it works even if 12.9 lands second.
**Integration risk:**
the honesty caveats are binding — a metric shown without its small-n / low-power caveat is false precision; render them
attached, not as a footnote. `conversion` / `gate_metrics` are already typed by 12.2 — consume, don't re-type. 12.9 + 12.10
land in the same batch; the histogram→Highlights deep-link rides the SHARED query keys (`set` / `winner` / `winShape` /
`scoreBucket` / `hasEjection`) that 12.9 reads — 12.10 must use those exact keys (not invent `?bucket=`) or the filter
silently no-ops. The link targets the shell ROUTE (present since 12.4), so it degrades gracefully if 12.9 lands second. No converge screen — verify against the brief. Don't edit `App.tsx` (mount discipline).
**Ready-to-paste prompt:** `agent_prompts/task-12-10-dashboard.md`

---

## Wave C — Polish

### Task 12.11 — Accessibility, responsive, first-run, perf
**Branch:** `phase-12-polish`
**Depends on:** 12.5, 12.6, 12.7, 12.8, 12.9, 12.10, 12.12
**Section refs:** design/phase-12/stage-1-design.md §8, §9, slice 9; the never-hue-only + reduced-motion a11y/firewall rules in `design/phase-12/claude-design-brief.md`; the holistic-visual-pass punch-list (in the body below).
**Complexity:** Integration
**Files in scope:**
- frontend/src/App.tsx
- frontend/vite.config.ts
- frontend/src/components/MapView.tsx
- frontend/src/components/MeetingView.tsx
- frontend/src/components/BeliefMatrix.tsx
- frontend/src/components/ThoughtStream.tsx
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TournamentDashboard.tsx
- frontend/src/components/GuidedTour.tsx
- frontend/src/index.css
- .github/workflows/ci.yml
**Files NOT in scope:**
- api/ and the loader — pure frontend polish; no DTO change, no re-record
- the engine / recorded replays — no re-record

The phase-close polish pass, hand-coded (no Claude Design). **This is the one task that legitimately edits `App.tsx`** —
the shell-level responsive / first-run / code-split — and it runs sequentially after every surface, so the Wave-B mount
discipline does not apply here. Scope:
- **A11y:** keyboard-operable transport (scrub / step / play / jump), focus management + `:focus-visible`, ARIA on the
  data panels (matrix, ballots, mind tabs, browser, dashboard, and 12.12's set selector), a **reduced-motion** variant (vent dive / kill flash /
  contradiction link-draw / map↔meeting morph respect `prefers-reduced-motion`), AA contrast, and a **never-hue-only
  audit** — every status / correctness / suspicion encoding must also read by shape or label (the firewall a11y rule).
- **Responsive:** rails collapse to drawers on narrow widths; the map + transport are the irreducible core.
- **First-run guided mode:** an annotated walkthrough on a high-interestingness 9p2i seed teaching the perspective switcher
  + the two-truth grammar (a new `GuidedTour`).
- **Perf / code-split:** `vite.config.ts` `manualChunks` (Pixi + react-dom vendor chunk) + `React.lazy` for Dashboard /
  Highlights → close the **859 kB single chunk** (the build's > 500 kB warning gone).
- **Holistic-pass visual nits:** (a) the **map token↔label overlap** — room-name labels (Admin / Storage / Reactor) sit
  under their centered player tokens; reposition the label clear of the token. (b) the **map dead-end cluster density** —
  at Reactor / Storage the kill ✕ + impostor dagger (†) + body marker + labels stack; de-conflict them. (c) the
  **overlay-composition bug** (the owner-reported "meeting overlap", confirmed from screenshots — it shows only in the
  *composed* app, not isolated stories). The MeetingView (`z-50`), BeliefMatrix (`z-55`), and MindInspector / ThoughtStream
  (`z-60`) are independent *fixed* overlays that stack and collide: the Mind-inspector rail covers the Ballots panel, and
  the background map / belief bleeds through the gaps. Coordinate them into one clean layout — an open meeting masks the
  workspace, the inspector never overlaps the ballots, no background bleed. (d) the **map does not fill its stage** — it
  renders small with large empty space; scale the canvas to fill the stage container, and fan out / de-overlap the
  Cafeteria spawn cluster (all 9 tokens pile on the room label at tick 0).
- Optional: a Playwright visual smoke in CI (needs the loader + a served 9p2i set; sequence after build / typecheck).
**Definition of done:** keyboard transport + ARIA on data panels + reduced-motion + AA contrast + a passing
never-hue-only audit; responsive rail→drawer; a first-run guided mode on a high-interestingness seed; the 859 kB chunk
split (the > 500 kB build warning gone); the map token↔label overlap + dead-end cluster + Cafeteria spawn-cluster
de-cluttered and the map fills its stage (no large empty space); the overlay-composition bug is fixed (the meeting /
belief / mind overlays no longer collide — the inspector doesn't cover the ballots and no background bleeds through);
every surface still renders correctly after the changes; `npm run tsc:check` +
`npm run build` pass and `scripts/check.sh` is green.
**Implementation hint:**
this task owns the shell, so editing `App.tsx` is expected (responsive layout, the `GuidedTour` mount, `React.lazy`
boundaries). Fix the map nits in `MapView` (offset the room label vs the centered token; de-conflict the Reactor /
Storage markers). For the meeting overlap, run the spectator and open a meeting over the live workspace to reproduce
before touching `MeetingView` — it is composition-level, not the isolated component. Code-split via `vite.config.ts`
`manualChunks` + `React.lazy`.
**Integration risk:**
a11y + responsive touch every surface — regression-check each (map fog, matrix layers, meeting verdict, dashboard
caveats) still renders after the reduced-motion / responsive / lazy changes. The never-hue-only audit is the firewall
a11y rule — don't let a colour-only status slip through. The code-split must not break Pixi or the lazy-loaded routes.
The overlay-composition bug is confirmed (owner screenshots) but shows only in the composed app — build + test it in the
running spectator, not isolated stories. This task owns the all-surface a11y, so it edits `ReplayPicker` /
`TournamentDashboard` (also 12.12's files) — that is why it `depends on 12.12` and runs sequentially after it; do not
dispatch them in parallel.
**Ready-to-paste prompt:** `agent_prompts/task-12-11-polish.md`

---

## Wave D — Multi-set viewer (feature)

### Task 12.12 — Multi-set serving + set selector
**Branch:** `phase-12-multi-set`
**Depends on:** 12.2, 12.3, 12.4, 12.7, 12.9, 12.10
**Section refs:** design/phase-12/stage-1-design.md §2.1 (top-level nav / the 9p2i-vs-4p1i set), §7; `scripts/run_spectator.sh` (`AILIBI_REPLAY_DIR=replays/samples`).
**Complexity:** Integration
**Files in scope:**
- replays/samples/4p1i/
- api/replay_loader.py
- api/routes/replays.py
- api/routes/eval.py
- api/routes/sets.py
- api/main.py
- frontend/src/store/replayStore.ts
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TournamentDashboard.tsx
- tests/api/test_sets.py
- scripts/_manifest_writer.py
- scripts/_verify_samples.py
- scripts/verify_samples.sh
- scripts/refresh_samples.sh
- scripts/build_sample_report.py
- scripts/run_spectator.sh
- tests/api/test_eval_routes.py
- tests/api/test_replay_dir_fallthrough.py
- tests/scripts/test_manifest_writer.py
- tests/scripts/test_refresh_samples.py
- tests/scripts/test_build_sample_report.py
**Files NOT in scope:**
- the engine / recorded game CONTENT — the 4p1i move is a `git mv` only; NO re-record
- the chrome surfaces' internals (map / belief / meeting / mind) — only the set-fetch wiring in the browser + dashboard

Let the spectator serve **all** recorded sets in one run, with a live **set selector** (no reload) that auto-grows as new
sets are recorded. Three parts:
- **Restructure (the foundation — bigger than it looks; it reaches the substrate sample tooling).** `replays/samples/` is
  inconsistent today — **4p1i is flat at the root** (`replay-seed-*.jsonl` + `MANIFEST.md` + `tournament-eval-report.json`)
  while **9p2i is already a subdir**. `git mv` the root 4p1i files into `replays/samples/4p1i/` so `replays/samples/`
  becomes a uniform **parent of per-set subdirs** (`4p1i/`, `9p2i/`, + future) — no content change, no re-record. This
  **collapses the flat-4p1i-baseline special-casing** several tools carry: `_manifest_writer.py`'s `is_default_sample_dir`
  / `_DEFAULT_SAMPLE_DIR`, and `refresh_samples.sh`'s "refusing to refresh the flat 4p/1i baseline" guard, exist only
  because 4p1i sits at the root where a misconfigured refresh lands. Once every set is a named subdir that footgun is gone,
  so **remove** the special case (a simplification) rather than re-point it. Then update **every** root-layout reference —
  grep the repo for `replays/samples`, `SAMPLE_DIR`, `_DEFAULT_SAMPLE_DIR` and fix each: the determinism gate
  (`verify_samples.sh` / `_verify_samples.py`), the re-record workflow (`refresh_samples.sh`), the manifest writer + report
  (`_manifest_writer.py`, `build_sample_report.py`), the loader default (`api/main.py::_resolve_replay_dir`, now resolving
  to a set subdir such as `4p1i` rather than the flat root), and their tests.
- **Backend (set-aware loader).** `AILIBI_REPLAY_DIR` (`replays/samples`) becomes the **parent**; `get_replay_loader`
  takes a `set` (query param; sane default) → resolves `<parent>/<set>/` → a **per-set loader cached** (`lru_cache` keyed
  by set, so each set's engine re-walk caches independently). Thread `set` through `/replays`, `/replays/{game_id}/*`,
  `/eval/rubric`, `/eval/tournament-report`. Add **`GET /sets`** → list the parent's subdirs (the available sets),
  skipping stray non-set files — this **auto-grows**: a newly-recorded `replays/samples/<set>/` appears with no code
  change. Determinism + the leak guard run **per set**.
- **Frontend (set selector).** The browser's existing **SET dropdown** (12.9) + the dashboard fetches become set-driven.
  On load, fetch `/sets` → populate the selector + the store's `availableSets`; the active set rides the **existing `set`
  URL key** that `usePlayback.ts` already syncs to the `seedSet` store field (see `usePlayback.ts:52,473`) — `seedSet` is
  the store field name only, so **do not introduce a second URL key** or the existing deep-links / 12.9 filters break. The
  selector just calls `setSeedSet` (already URL-synced). On change, re-fetch `/replays?set=` + `/eval/rubric?set=` +
  `/eval/tournament-report?set=` — **switch live, no reload**. `run_spectator.sh` is unchanged (its `replays/samples` is
  now the parent).
**Definition of done:** `replays/samples/` is a uniform parent of per-set subdirs (`4p1i/` + `9p2i/`); the flat-4p1i
special-casing is removed (no `is_default_sample_dir` / flat-baseline refuse-guard remains); every root-layout reference
is updated (the determinism gate, the re-record workflow, the manifest writer + report, the loader default, and their
tests) and `scripts/verify_samples.sh replays/samples/4p1i` passes; `GET /sets` lists the subdirs and auto-grows; `/replays`
+ `/eval/*` are set-parametrized over a per-set cached loader; the frontend set selector toggles sets **live (no reload)**
via the existing `set` URL key, and a newly-recorded set appears with no code change; `run_spectator.sh` serves all sets in
one run; determinism + leak tests pass **per set**; NO re-record (the 4p1i move is a `git mv`); `scripts/check.sh` is
green.
**Implementation hint:**
do it in order: (1) `git mv` the root `replay-seed-*.jsonl` + `MANIFEST.md` + `tournament-eval-report.json` into `4p1i/`
(no content edit); (2) grep the repo for `replays/samples` / `SAMPLE_DIR` / `_DEFAULT_SAMPLE_DIR` and fix every code
reference, removing the flat-baseline special case rather than re-pointing it; (3) run `scripts/verify_samples.sh
replays/samples/4p1i` to confirm byte-determinism survived the move; (4) make `get_replay_loader` resolve
`<AILIBI_REPLAY_DIR>/<set>` and cache per-set (`lru_cache` by set), and add `GET /sets`; (5) wire the frontend selector to
`/sets` + the per-set re-fetch, reusing the existing `set` URL key (do not add a new one).
**Integration risk:**
this reaches the **substrate sample tooling** — `verify_samples.sh` / `_verify_samples.py` is the byte-determinism gate
the gameplay/ML cadence depends on, and `refresh_samples.sh` is the real-provider re-record workflow; update both with
care and run `verify_samples.sh` after the move. The move + the loader/scripts/tests must land together — moving the files
alone breaks the root-`glob`, the `is_default_sample_dir` logic, and every test asserting the flat root (and `check.sh`
runs `pytest`, so those failures block green). The `set` param needs a sane default so existing deep-links + the dashboard
still resolve; per-set loader caching must be bounded (LRU cap); `/sets` must skip stray non-set entries (a top-level
README, etc.); determinism + leak tests run per-set. 12.11 depends on this task (it does the all-surface a11y including
the set selector), so dispatch 12.12 first.
**Ready-to-paste prompt:** `agent_prompts/task-12-12-multi-set.md`

---

### Task 12.13 — UX-polish (close-audit backlog)
**Branch:** `phase-12-ux-polish`
**Depends on:** 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 12.10, 12.11, 12.12
**Section refs:** the Phase-12 UX close-audit (two multi-agent passes + a manual composed-app pass, 2026-06-20); design/phase-12/stage-1-design.md; design/phase-12/tokens-seed.md; `frontend/CLAUDE.md`.
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/MapView.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/components/MeetingView.tsx
- frontend/src/components/MindInspector.tsx
- frontend/src/components/ThoughtStream.tsx
- frontend/src/components/BeliefMatrix.tsx
- frontend/src/components/BeliefPanel.tsx
- frontend/src/components/ReplayControls.tsx
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TournamentDashboard.tsx
- frontend/src/components/BeliefRow.tsx
- frontend/src/App.tsx
- frontend/src/tokens.ts
- frontend/src/index.css
- frontend/src/ui/
- api/replay_loader.py
- api/schemas.py
**Files NOT in scope:**
- the engine + recorded replays — no re-record (a `tasks_required_total` is a loader projection, not an engine change)
- the six P1s ALREADY fixed pre-dispatch (palette restyle, BeliefCell contrast, perspective banner, focus-trap, highlights /sets dead-end, narrow meeting nav-bleed) — do NOT redo or revert them

The Phase-12 UX close-audit backlog, hand-coded + design-system-first. Build and verify every change in the COMPOSED
running app (`scripts/run_spectator.sh`), not isolated Storybook stories — the audit's recurring lesson is that the
overlay / composition / data-populate bugs only show composed. Severity in brackets.

Remaining P1s — each needs an owner decision or map-render iteration:
- **[P1] Task-meter denominator drifts.** `App.tsx:379` shows `adv.tasks_completed`/`adv.tasks_required`; `tasks_required`
  is recomputed per tick (living-crew), so "tasks 0/14 → 7/10" shrinks mid-game and reads as misleading progress. DECISION
  (owner, baked): expose the FIXED game-start required-task total as a loader projection — add `tasks_required_total` to
  the advantage DTO (`api/replay_loader.py` + `api/schemas.py`, then regenerate the TS types), computed once at game
  start, and render the roster meter as `tasks_completed / tasks_required_total` (a stable, monotonic denominator + bar).
  Keep the per-tick `tasks_required` as the internal win-condition value; the DISPLAY denominator is the fixed total.
- **[P1] Agent inspection only reachable inside a meeting.** Map tokens (`MapView`/`AgentToken`) and roster rows
  (`App.tsx` RosterRail) have no click → `selectAgent`. Wire a Pixi pointer handler + a roster-row onClick. DECISION
  (owner, baked): clicking an agent selects it and opens the mind inspector to that agent's LATEST meeting snapshot at or
  before the current tick (belief / prompt / response / memory / flags from the most recent meeting ≤ tick); before the
  first meeting, open to the belief tab with an honest "no deliberation yet" empty state — do NOT fabricate non-existent
  between-meeting LLM data. This requires the mind rail to render outside an open meeting: lift `ThoughtStream`'s null-gate
  (`ThoughtStream.tsx:54`, returns null when no meeting is selected) so it renders for a selected agent, sourcing the
  latest snapshot.
- **[P1] Belief × Truth launcher overlaps the Reactor room.** It floats at the map's lower-right over the Reactor cell +
  its vent corridor. DECISION (owner, baked): RE-ANCHOR the launcher into chrome — a tab beside the Omniscient/As-agent
  perspective toggle (or a roster-rail entry) — so it never overlaps a room cell or corridor. Letting the hero COEXIST
  with an open meeting (it deliberately steps aside when `selectedMeetingId !== null` per 12.11's overlay coordination) is
  OUT OF SCOPE — flag it as a follow-up so it is not reintroduced as a collision.
- **[P1] Admin dead-body cluster collision** (`MapView`): multiple bodies in one room garble the room title and the
  oversized kill-flash ring clips stacked labels. Reserve the title band, lay bodies in a non-overlapping grid with bottom
  padding, cap the kill-flash ring to the cell, collapse to "✕ ×N" past capacity.
- **[P1] Sabotage marker** renders as a solid warm-orange disc — make it the hazard treatment (ink/neutral fill + stripe +
  ⚡ glyph) per `tokens.ts` `status.sabotage`, off the reserved warm hue (it currently collides with the red kill disc and
  distrust-orange). `MapView` event markers.

P2 polish — the bulk:
- **[P2] Debug annotation leaks into the transcript** — `[emergency opening: fabricated found_body stripped]` renders
  inline (`MeetingView`/`TurnCard`); render a role-neutral "FABRICATED" chip instead and drop the dev-jargon string.
- **[P2] Muted-text + label contrast sweep** — `text-ink-400` (3.79:1) → `text-ink-500` for informational text, and
  distrust-strong orange label TEXT → `ink-900` (keep the orange edge/arrow as the channel) across `TurnCard`,
  `MeetingView`, `MindInspector`, `ReplayControls`, `BeliefPanel`, `MapToolbar` (matrix numerals + error glyph already fixed).
- **[P2] Type + spacing scale** — add a `type.size` scale to `tokens.ts` (+ `--text-*` utilities), map the ~88 ad-hoc
  `text-[9/10/11px]` onto named steps; round off-scale `px-2.5`/`py-2.5`/`gap-1.5`/`py-0.5` to `tokens.space` stops.
- **[P2] Incomplete ARIA widgets** — `MindInspector` tablist (`aria-controls` + `role="tabpanel"`/`aria-labelledby` +
  Left/Right roving-tabindex) and the `AdvantageGraph` slider (`ReplayControls`: its own Arrow/Home/End `onKeyDown`).
- **[P2] Cross-surface consistency** — one panel radius (`MeetingView`/`GuidedTour` `rounded-2xl` → the `rounded-lg`
  majority); shared `ui/SectionLabel` (eyebrow) + `ui/PlayerSwatch`; extract `ui/EmptyState`/`ui/Banner`/`ui/Loading`
  (with `role="status"`) and adopt them in `ReplayPicker`/`TournamentDashboard`/`App`; delete the dead `ui/PlayerChip`.
- **[P2] Map legibility** — draw the vent endpoints (the "6-vent ring" subtitle promises them) or drop the claim; enlarge
  the impostor-reveal badge + add an Omniscient-only legend; align the advantage-graph and event-timeline to a shared
  left plot origin so the tick crosshair lines up.
- **[P2] Narrow-820** — inset the seek-marker track so the last-tick marker isn't clipped + give 16px markers a ≥24px
  hitbox; tighten the ~200px dead space below the map card; keep a compact crew/imp/tasks summary on the collapsed roster
  bar; inset the clipped "Mind inspector" drawer tab.
- **[P2] Feedback + edge states** — an in-flight "Loading <set>…" cue on set switch; render `availableSetsError` as an
  inline retry chip where `SetSelector` would be; give the replay-load error Banner a dismiss (`clearError()`); grey the
  "0 mtg" Belief launcher with a tooltip; hoist the repeated 4p1i "Not scored" note to ONE Banner when
  `rubricStatus === "absent"`; fill the mind-inspector default empty column (default-select / how-to-read).
- **[P2] Misc** — verify the dashboard "interestingness distribution" section populates (it shows an empty card below the
  fold); add a baseline/value to the Highlights R1/R2/R3/R7 mini-bars; mark/disable dead agents in the fog agent picker;
  add a tour step for opening a mind; delete the dead `BeliefRow` MemoBar branch (off-token neutral ramps).
**Definition of done:** the five remaining P1s are addressed (task-meter shows a stable fixed-total denominator via
`tasks_required_total`; agent inspection reachable from the map + roster, opening to the latest meeting snapshot; the
belief launcher re-anchored into chrome off the room cells; the Admin body-cluster and sabotage-marker fixed in the map);
the P2 backlog is worked through; every
change verified in the composed running app; no firewall regression (the leak test still passes — fog suppresses roles,
the matrix stays Omniscient-only); `npm run tsc:check` + `npm run build` pass and `scripts/check.sh` is green.
**Implementation hint:**
build + test in the running spectator, not isolated stories — the overlay / composition / populate bugs only show
composed. Group edits by file to minimise churn (most map items are `MapView`; the contrast sweep is largely a
find-replace of `text-ink-400` + the distrust-orange label text). The task-meter likely needs a small loader/DTO
projection for the fixed total (then regenerate the TS types). Reuse the `useFocusTrap` hook + the cream/ink primitive
pattern the pre-dispatch P1 fixes established.
**Integration risk:**
broad surface area — regression-check each surface in the composed app and re-run the firewall leak test. This builds ON
the six pre-dispatch P1 fixes (committed first); do not redo or revert them. The task-meter touches `api/` — keep it a
loader projection, no engine change, no re-record. Dispatch this AFTER the pre-dispatch P1 fixes land on main.
**Ready-to-paste prompt:** `agent_prompts/task-12-13-ux-polish.md`
