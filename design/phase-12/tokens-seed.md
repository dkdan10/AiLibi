# Phase 12 — Playful design-system token seed (Wave-0b output)

The accepted **Wave-0b** token sheet for the **Playful** direction, transcribed verbatim from the Claude Design converge
deliverable (`AiLibi - Playful System.dc.html`, the `tokensText()` block). **This is the canonical seed Task 12.1
transcribes into `frontend/src/tokens.ts`, and the single source for the `identity[]` palette that Task 12.2 also uses
for `_COLOR_PALETTE`** — both tasks read THIS file, so the parallel dispatch cannot drift on the palette.

It is a *seed*: 12.1 resolves the pseudo-code self-references (`fill:'identity'`, `ink[500]`, `ink[300]`,
`outline:'solid 2px ink900'`) into real TS, emits Tailwind v4 `@theme` (DOM) + a `pixiHex` helper (canvas), and applies
the density rule (hard 2.5px-border / offset-shadow `elevation` = chrome only; `elevation.data` = 1px hairline on dense
surfaces). The firewall rules are binding (identity ≠ guilt; amber = suspicion / blue = trust / red = kill /
fuchsia = contradiction; never hue-only) — see `claude-design-brief.md`.

```ts
export const tokens = {
  paper: { 0:'#FFFDF8', 1:'#FBF4E6', 2:'#F4EAD6', 3:'#EBDFC8' },
  ink:   { 900:'#1B1814', 700:'#443D34', 500:'#6E6556',
           400:'#8A8170', 300:'#A89E8A', 200:'#C9BFA8', 100:'#E2D8C3' },

  // ── reserved meaning channels (never cross-used) ──
  suspicion: ['#FBE6AE','#F6C75A','#EF9D33','#DE6A24','#C24A16'], // sequential, amber only
  suspicionBucket: { low:0.35, high:0.72 },                       // Low ≤ .35 < Med ≤ .72 < High
  trust:    { strong:'#2563D9', soft:'#5B8CE8' },                 // blue — trust only
  distrust: { strong:'#E07A1E', soft:'#EFA24E' },                 // orange — distrust only
  kill:     '#E23B2F',                                            // red — death only
  contradiction: '#D6249E',                                       // fuchsia — lie / mismatch / error

  status: {
    alive:        { fill:'identity',  shape:'disc' },
    dead:         { fill:ink[500],    glyph:'✕',  note:'role-neutral' },
    sabotage:     { pattern:'hazard', glyph:'⚡', note:'ink stripes, no reserved hue' },
    contradictionWeak:   { stroke:ink[300], dash:'4 4', weight:1.5 },
    contradictionStrong: { stroke:'#D6249E', dash:'none', weight:3 }
  },

  // identity — identity ONLY (greens / teals / purples). disjoint from every channel.
  identity: ['#5DA83A','#2BA45E','#14A06E','#0E9C93','#128F9E',
             '#6C5CE0','#8350D6','#9A4FCB','#A94FC6'],

  truth: {
    ground: { opacity:1,   outline:'solid 2px ink900' },          // authoritative
    belief: { opacity:0.5, outline:'dashed 2px',  attributed:true },
    noBelief:{ pattern:'hatch', note:'≠ 0%' }
  },

  radius:  { sm:6, md:10, lg:14, xl:20, pill:999 },
  space:   [4,8,12,16,24,32,48],
  elevation: { chrome1:'3px 3px 0 #1B1814', chrome2:'6px 6px 0 #1B1814',
               data:'0 0 0 1px #C9BFA8' },                        // hard shadow = chrome only
  motion:  { quick:120, base:200, slow:360,
             chromeEase:'cubic-bezier(.34,1.4,.64,1)', dataEase:'ease-out',
             reducedMotion:'disable all' },
  type:    { display:"600 'Fredoka'", body:"400 'Fredoka'", mono:"'Space Mono'" }
};
```

**Residual palette adjacencies to eyeball in context** (from the 0b review): identity periwinkle `#6C5CE0` (p-5) vs
trust `#2563D9`; identity magenta `#A94FC6` (p-8) vs contradiction `#D6249E` — both distinguishable + label-backed; nudge
the purple end bluer if a token ever sits adjacent to a fuchsia flag.
