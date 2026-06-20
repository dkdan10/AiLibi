// AiLibi Playful design-system tokens — the SINGLE source of every colour,
// space, radius, type, elevation and motion value in the spectator viewer.
//
// Transcribed from the accepted Wave-0b token sheet
// (design/phase-12/tokens-seed.md). The seed's pseudo-code self-references are
// resolved into real TS here: the `paper` / `ink` ramps and the `kill` /
// `contradiction` hues are declared as standalone `const`s FIRST, so the
// semantic tokens below reference them for real (`ink[500]`, `ink[300]`,
// `ink[200]`, `ink[900]`) instead of as pseudo-code. `status.alive.fill:
// "identity"` stays a marker — it means "fill with this player's per-player
// identity colour" (firewall: identity ≠ guilt), resolved against `identity[]`
// at render time, NEVER a fixed hue.
//
// The SAME object feeds two render layers with zero magic constants in either:
//   • DOM  — the Tailwind v4 `@theme` block in `index.css` is GENERATED from
//            this file (`npm run gen:tokens`), so every CSS custom property and
//            utility (`bg-paper-1`, `text-ink-900`, `shadow-chrome-1`, …)
//            traces back here.
//   • Pixi — `pixiHex(tokens.kill)` converts a token hex string to the
//            0xRRGGBB number the canvas layer needs.
//
// FIREWALL (binding): amber = suspicion · blue = trust · orange = distrust ·
// red = kill · fuchsia = contradiction · greens/teals/purples = identity ONLY.
// Never cross-use a channel, and never encode status with hue alone.
//
// Density rule (from the seed): the hard 2.5px-border / offset-shadow
// `elevation.chrome*` is CHROME-ONLY; dense data surfaces use the 1px hairline
// `elevation.data`.

// ── primitive ramps (declared first so the semantic tokens reference them as
//    real TS, resolving the seed's `ink[…]` / `paper[…]` self-references) ──
const paper = {
  0: "#FFFDF8",
  1: "#FBF4E6",
  2: "#F4EAD6",
  3: "#EBDFC8",
} as const;

const ink = {
  900: "#1B1814",
  700: "#443D34",
  500: "#6E6556",
  400: "#8A8170",
  300: "#A89E8A",
  200: "#C9BFA8",
  100: "#E2D8C3",
} as const;

// Reserved single-hue channels, declared so `status` can reference them.
const kill = "#E23B2F"; // red — death only
const contradiction = "#D6249E"; // fuchsia — lie / mismatch / error

export const tokens = {
  paper,
  ink,

  // Sequential amber heat ramp (5 stops); bucket Low ≤ .35 < Med ≤ .72 < High.
  suspicion: ["#FBE6AE", "#F6C75A", "#EF9D33", "#DE6A24", "#C24A16"],
  suspicionBucket: { low: 0.35, high: 0.72 },

  trust: { strong: "#2563D9", soft: "#5B8CE8" }, // blue — trust only
  distrust: { strong: "#E07A1E", soft: "#EFA24E" }, // orange — distrust only
  kill,
  contradiction,

  // Each status pairs a colour with a SHAPE / GLYPH / PATTERN — never hue-only.
  status: {
    // `fill: "identity"` is a marker: fill with the player's identity[] colour.
    alive: { fill: "identity", shape: "disc" },
    dead: { fill: ink[500], glyph: "✕", note: "role-neutral" },
    sabotage: { pattern: "hazard", glyph: "⚡", note: "ink stripes, no reserved hue" },
    contradictionWeak: { stroke: ink[300], dash: "4 4", weight: 1.5 },
    contradictionStrong: { stroke: contradiction, dash: "none", weight: 3 },
  },

  // identity — identity ONLY (greens / teals / purples); disjoint from every
  // reserved channel. Indexed p-0 … p-8.
  identity: [
    "#5DA83A",
    "#2BA45E",
    "#14A06E",
    "#0E9C93",
    "#128F9E",
    "#6C5CE0",
    "#8350D6",
    "#9A4FCB",
    "#A94FC6",
  ],

  // Two-truth grammar: ground = solid/authoritative, belief = ghosted +
  // attributed, noBelief = hatched ("no belief yet" ≠ 0%).
  truth: {
    ground: { opacity: 1, outline: `solid 2px ${ink[900]}` },
    belief: { opacity: 0.5, outline: "dashed 2px", attributed: true },
    noBelief: { pattern: "hatch", note: "≠ 0%" },
  },

  radius: { sm: 6, md: 10, lg: 14, xl: 20, pill: 999 },
  space: [4, 8, 12, 16, 24, 32, 48],

  // Hard offset shadow = CHROME only; data surfaces get the 1px hairline.
  elevation: {
    chrome1: `3px 3px 0 ${ink[900]}`,
    chrome2: `6px 6px 0 ${ink[900]}`,
    data: `0 0 0 1px ${ink[200]}`,
  },

  motion: {
    quick: 120,
    base: 200,
    slow: 360,
    chromeEase: "cubic-bezier(.34,1.4,.64,1)",
    dataEase: "ease-out",
    reducedMotion: "disable all",
  },

  type: {
    display: "600 'Fredoka'",
    body: "400 'Fredoka'",
    mono: "'Space Mono'",
    // Sub-`xs` data type sizes in px. The dense numeric / label surfaces use
    // sizes below Tailwind's 12px `text-xs` floor; naming them here (and emitting
    // `--text-*` utilities in `index.css`) lets the ~88 ad-hoc `text-[9/10/11px]`
    // usages map onto a named scale instead of magic px. Tailwind's `xs`+
    // defaults are untouched — this only ADDS the smaller steps.
    size: { "4xs": 9, "3xs": 10, "2xs": 11 },
  },
} as const;

export type Tokens = typeof tokens;

// Convert a token hex string ("#RRGGBB") to the 0xRRGGBB number the Pixi/canvas
// layer needs. Raises on a malformed value — no silent fallback (AGENTS.md).
export function pixiHex(hex: string): number {
  const normalized = hex.trim().replace(/^#/, "");
  if (!/^[0-9a-fA-F]{6}$/.test(normalized)) {
    throw new Error(`pixiHex: expected "#RRGGBB", received ${JSON.stringify(hex)}`);
  }
  return Number.parseInt(normalized, 16);
}

export type SuspicionBucket = "low" | "med" | "high";

// Bucket a 0–1 suspicion value into Low / Med / High using the seed thresholds
// (Low ≤ .35 < Med ≤ .72 < High). Honesty rule: always bucket — the viewer must
// never imply false precision on a soft belief value.
export function suspicionBucketOf(value: number): SuspicionBucket {
  if (value <= tokens.suspicionBucket.low) return "low";
  if (value <= tokens.suspicionBucket.high) return "med";
  return "high";
}
