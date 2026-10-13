# Phase 12 — Claude Design Workspace Brief

**The one durable, workspace-level brief for the AiLibi viewer rebuild.** The global aesthetic / token / firewall
contract lives here *once*; per-component prompts (in `tasks/phase-12.md`) reference it and never restate it.

**How to use this file:** paste **only the PASTE BLOCK below** into Claude Design (Wave-0 grounding) and **attach
`design/phase-12/canonical_1-map-reference.png`** (the generated map reference; or its `.svg`). The Appendix at the bottom is **repo-only
context — do NOT paste it** (it's for the Claude Code build threads, and this whole file is installed as
`frontend/CLAUDE.md` in task 12.0). `tokens.ts` is the canonical source of truth once it exists.

---

## ▼▼▼ PASTE THIS BLOCK INTO CLAUDE DESIGN (Wave-0 grounding) ▼▼▼

**What we're building.** A spectator *replay viewer* for an LLM social-deduction game (an Among-Us-like where AI agents
play). Its one job: make a **hidden-information** game **legible** — show, at any moment, what each agent *knew / believed*
vs the *ground truth* (who's the impostor, who killed whom, who vented). You're designing two viewing modes: an
**Omniscient** view (the spectator sees everything) and an **As-agent** view (fog of war — only what one chosen agent
could see). One visual convention everywhere: **ground truth = solid / authoritative; an agent's belief or limited view =
ghosted + attributed** (e.g. "p-3 believes…").

**The map is FIXED — `canonical_1` (in the attached reference image `canonical_1-map-reference.png` — restyle it, never invent / move / rename rooms).** One top-down
floorplan: 10 rooms at real grid positions, 11 corridors, and a 6-room impostor "vent" network. Cafeteria is the central
hub; Reactor and Labs are dead-ends. 9 players (ids p-0…p-8) move room-to-room; some are secretly impostors.

**Art direction = PLAYFUL (chosen Wave-0a, 2026-06-17).** A cream + ink **chunky-sticker** style: bold ~2.5px ink
outlines, rounded forms, **Fredoka** (headings/labels) + **Space Mono** (data / ticks / IDs), high contrast, bright
accents, hard-offset shadows; defaults to **As-agent fog**. It tested as the most structurally readable + most on-theme.
**TWO converge fixes are MANDATORY before tokens lock** (see `tasks/phase-12.md` Wave-0b): **(1) re-space the identity
palette OFF the semantic channels** — reserve amber=suspicion, blue=trust, red=kill, and put identity in
purples/teals/greens/magentas; **(2) tune the sticker weight for density** — it must stay calm/legible on the 9×9 belief
matrix + full meeting view (borrow Telemetry-style restraint for dense panels). "Vector/geometric" remains the asset
*pipeline* (SVG, no raster).

**Steer these dimensions individually:**
- **Typography:** direction-dependent — a technical grotesque for a serious direction, a rounded/characterful sans for a
  playful one — plus a **mono** for ticks / IDs / JSON / transcripts. **Not Inter, not Roboto.**
- **Color:** canvas mood (dark / light / bright) is direction-dependent; accents restrained; the firewall rules below
  always hold.
- **Motion:** purposeful only (a token moving rooms, a vent dive/emerge, a kill flash, a contradiction link being drawn);
  always a reduced-motion variant. **No decorative motion.**
- **Density:** information-dense but breathable; mono-aligned numeric data.
- **Iconography:** a small geometric **action/status glyph set** (move / task / kill / vent / report / sabotage; body;
  emergency button; reactor / lights).

**Use realistic content, NOT lorem ipsum:** real room names (Cafeteria, MedBay, Reactor, Electrical-style names),
players p-0…p-8, a believable meeting line ("I saw p-5 head toward Reactor around tick 312…"), plausible suspicion values.

**AVOID:** Inter / Roboto; unintentional purple/indigo-on-white gradients; glassmorphism; emoji-as-UI; rainbow
categorical palettes; heavy drop-shadow cards; generic SaaS-landing aesthetics; pure black or pure white; centered "hero"
layouts; the AI-slop "high-probability center."

**FIREWALL COLOR RULES (BINDING — they keep the hidden-information game honest; breaking them leaks secrets or misleads):**
- A player's **identity** color is identity *only* — **never** encode role / guilt / alignment in it.
- **Ground-truth impostor reveal** = an explicit **icon/badge**, never a hue — and it must be **hideable** (it is hidden
  in the As-agent fog view).
- **Suspicion** = a sequential **heat ramp**, visually distinct from identity hues; **bucket it Low / Med / High**.
- **Trust ↔ distrust** = **blue ↔ orange** (not red/green — colorblind-safe, and red is reserved for kills).
- **Outcomes** (ejected / skipped) = **role-neutral** colors (coloring by guilt would leak who the impostor was).
- **Never hue-only** — pair every status with shape or text.

**Build a design system + tokens** (color, type, spacing, radii, elevation, motion) that includes these semantic tokens:
a per-player **identity palette**, a **suspicion heat ramp**, **trust/distrust** (blue/orange), **status** (alive, dead,
sabotage, contradiction-weak, contradiction-strong), and a **truth pair** (ground = solid, belief = ghosted).

**Components are presentational.** Design all states (default / empty / loading / error / responsive), compose from the
tokens (no hardcoded hex), and be **honest about uncertainty**: bucket suspicion, show "no belief yet" (which is *not*
0%), and label an impostor's fake "cover" tasks as **fabricated**.

## ▲▲▲ END PASTE BLOCK ▲▲▲

---

## Appendix — workflow & repo notes (do NOT paste into Claude Design; for `frontend/CLAUDE.md` / build threads)

**Division of labor.** Claude Design owns the **DOM chrome + design system + tokens + SVG icon set** (`ui/` primitives,
belief panels, meeting view, replay browser / highlights, dashboard). Claude Code hand-codes the **Pixi/WebGL map render
layer, data/state wiring, playback/interaction, and firewall-simulation / leak correctness**. The map's **SVG assets are
generated by Claude Code with a locked style-spec**, not by the Claude Design product. No raster (a third-party image MCP
only if ever required). "Connected" components are hand-wired by Claude Code, not Claude-Design-generated.

**Workflow.** Design-system-first → this one durable brief → **per-component focused prompts** → per-slice **Share →
Handoff to Claude Code** → integrate (compose from tokens, no hardcoded hex) → **screenshot-verify** (`claude --chrome` /
Playwright, isolated + composed) → small PR → fresh-context review → next. **One component at a time, never a wholesale
replace.** Anti-patterns: one mega-prompt for all components; bulk integration; regenerating over files holding
hand-written logic.

**Per-component prompt template** (one per component; filled specs in `tasks/phase-12.md`):
> "Using our design system + these `frontend/CLAUDE.md` rules, design the **[Component]**. Purpose: […]. Displays:
> [fields]. States: default / empty / loading / error + responsive. Follow the FIREWALL COLOR RULES (esp. [relevant ones]).
> Compose from tokens; no hardcoded hex. Presentational only — no data fetching. Make the legibility device explicit:
> [e.g. two-truth ghosting / confidently-wrong cell rendered LOUD / weak-vs-strong = dashed-vs-solid]."

**Token implementation.** One source `tokens.ts` consumed by **both** Tailwind/DOM and the Pixi layer (hex→number), zero
magic constants; TS types codegen'd from the Pydantic view-model (no hand-mirroring).

**Tool caveats.** Official Design→Code path = the **one-way handoff bundle**; `DesignSync`/`/design-sync` is real but
**undocumented** — don't make it the backbone. Claude Design is **paid / web-only / quota-metered** and **owner-driven**
(the build agent can't invoke it); manual canvas edits silently regenerate and burn quota — so explore on ONE
representative screen at low fidelity.

**See also:** `stage-1-design.md` §9.5 (integration), `tasks/phase-12.md` Wave 0 (the exploration prompt + the
`canonical_1` map reference + room table).
