// Token-ramp integrity (Task 19.12; the durable check Task 19.6 deferred here).
//
// The defect this file exists to prevent, verbatim from 19.6: the seed sheet
// declared seven ink stops and two components reached for an EIGHTH
// (`text-ink-600`). Tailwind emits no rule for an undeclared token, so those
// spans silently inherited the body colour — no build error, no runtime error,
// no visual error loud enough to notice. 19.6 added the missing stop; this file
// is what makes the whole CLASS of that defect impossible to re-introduce.
//
// Three independent checks, because the defect has three possible homes:
//   1. USAGE  — every token utility a component reaches for is declared.
//   2. SYNC   — the generated `@theme` block in index.css matches tokens.ts
//               (the single-source guarantee `npm run gen:tokens` promises).
//   3. FIREWALL — the reserved meaning channels stay disjoint from identity.
//
// It reads the real `src/index.css` and the real component sources off disk on
// purpose: a test that re-derived the theme block from `tokens.ts` in memory
// would pass happily while the COMMITTED css was stale, which is exactly the
// state 19.6 found.

import { readFileSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { pixiHex, suspicionBucketOf, tokens } from "./tokens";

const SRC_DIR = dirname(fileURLToPath(import.meta.url));
const CSS_PATH = resolve(SRC_DIR, "index.css");

const START =
  "/* tokens:start — generated from src/tokens.ts via `npm run gen:tokens`; do not edit by hand */";
const END = "/* tokens:end */";

// ── the committed @theme block ───────────────────────────────────────────────

/** The generated `@theme` custom properties, parsed out of the real index.css. */
function themeVars(): Map<string, string> {
  const css = readFileSync(CSS_PATH, "utf8");
  const start = css.indexOf(START);
  const end = css.indexOf(END);
  if (start === -1 || end === -1) {
    throw new Error("index.css is missing the tokens:start / tokens:end markers");
  }
  const block = css.slice(start + START.length, end);
  const vars = new Map<string, string>();
  for (const match of block.matchAll(/^\s*(--[\w-]+):\s*([^;]+);/gm)) {
    vars.set(match[1]!, match[2]!.trim());
  }
  return vars;
}

const VARS = themeVars();

/** Every `.ts` / `.tsx` under `src/`, excluding the test files themselves. */
function sourceFiles(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) {
      return sourceFiles(path);
    }
    if (!/\.tsx?$/.test(entry.name) || /\.test\.tsx?$/.test(entry.name)) {
      return [];
    }
    return [path];
  });
}

const SOURCES = sourceFiles(SRC_DIR).map((path) => ({
  path,
  text: readFileSync(path, "utf8"),
}));

/** Collect every `<capture>` produced by `pattern` across the component sources. */
function usages(pattern: RegExp, render: (match: RegExpMatchArray) => string): string[] {
  const found = new Set<string>();
  for (const { text } of SOURCES) {
    for (const match of text.matchAll(pattern)) {
      found.add(render(match));
    }
  }
  return [...found].sort();
}

// ── 1. usage: every utility a component reaches for is a declared token ──────

describe("token utilities used in components resolve to declared tokens", () => {
  it("finds sources to scan at all (the check is only as good as its input)", () => {
    expect(SOURCES.length).toBeGreaterThan(30);
    expect(VARS.size).toBeGreaterThan(40);
  });

  it("every numeric ramp step (ink / paper / identity / suspicion) is declared", () => {
    // THE 19.6 CHECK. `text-ink-600` before the fix produced `--color-ink-600`
    // here and found nothing.
    const used = usages(
      /\b(?:[a-z][a-z0-9]*-)+(ink|paper|identity|suspicion)-([0-9]+)\b/g,
      (m) => `--color-${m[1]}-${m[2]}`,
    );
    expect(used.length).toBeGreaterThan(8);
    expect(used.filter((name) => !VARS.has(name))).toEqual([]);
  });

  it("every reserved meaning channel (trust / distrust / kill / contradiction / dead) is declared", () => {
    const used = usages(
      /\b(?:[a-z][a-z0-9]*-)+(trust|distrust|kill|contradiction|dead)(-[a-z]+)?\b/g,
      (m) => `--color-${m[1]}${m[2] ?? ""}`,
    );
    expect(used.length).toBeGreaterThan(5);
    expect(used.filter((name) => !VARS.has(name))).toEqual([]);
  });

  it("every sub-xs type size is declared", () => {
    const used = usages(/\btext-([0-9]xs)\b/g, (m) => `--text-${m[1]}`);
    expect(used.length).toBeGreaterThan(0);
    expect(used.filter((name) => !VARS.has(name))).toEqual([]);
  });

  it("every non-builtin shadow / radius utility is declared", () => {
    // Tailwind ships these as shape/side keywords; everything else has to come
    // from the token sheet.
    const BUILTIN = new Set([
      "none",
      "full",
      "t",
      "r",
      "b",
      "l",
      "tl",
      "tr",
      "br",
      "bl",
      "ss",
      "se",
      "ee",
      "es",
      "s",
      "e",
    ]);
    const shadows = usages(/\bshadow-([a-z0-9-]+)\b/g, (m) => m[1]!).filter(
      (name) => !BUILTIN.has(name),
    );
    expect(shadows.filter((name) => !VARS.has(`--shadow-${name}`))).toEqual([]);

    const radii = usages(/\brounded-([a-z0-9]+)\b/g, (m) => m[1]!).filter(
      (name) => !BUILTIN.has(name),
    );
    expect(radii.filter((name) => !VARS.has(`--radius-${name}`))).toEqual([]);
  });
});

// ── 2. sync: the generated block matches the token source ────────────────────

describe("the generated @theme block matches tokens.ts", () => {
  it("emits every ink and paper step, with the exact hex", () => {
    for (const [step, hex] of Object.entries(tokens.ink)) {
      expect(VARS.get(`--color-ink-${step}`)).toBe(hex);
    }
    for (const [step, hex] of Object.entries(tokens.paper)) {
      expect(VARS.get(`--color-paper-${step}`)).toBe(hex);
    }
  });

  it("declares NO ramp step tokens.ts does not (the block is generated, not hand-edited)", () => {
    // The reverse direction: a hand-added `--color-ink-800` in index.css would
    // survive `npm run tsc:check` and the build, and vanish the next time anyone
    // ran `npm run gen:tokens`.
    const declared = [...VARS.keys()]
      .filter((name) => /^--color-(ink|paper|identity|suspicion)-/.test(name))
      .sort();
    const expected = [
      ...Object.keys(tokens.ink).map((step) => `--color-ink-${step}`),
      ...Object.keys(tokens.paper).map((step) => `--color-paper-${step}`),
      ...tokens.identity.map((_, i) => `--color-identity-${i}`),
      ...tokens.suspicion.map((_, i) => `--color-suspicion-${i + 1}`),
    ].sort();
    expect(declared).toEqual(expected);
  });

  it("emits the identity palette and the suspicion ramp in order", () => {
    tokens.identity.forEach((hex, i) => {
      expect(VARS.get(`--color-identity-${i}`)).toBe(hex);
    });
    tokens.suspicion.forEach((hex, i) => {
      expect(VARS.get(`--color-suspicion-${i + 1}`)).toBe(hex);
    });
  });

  it("emits the reserved single-hue channels and the status colours", () => {
    expect(VARS.get("--color-trust-strong")).toBe(tokens.trust.strong);
    expect(VARS.get("--color-trust-soft")).toBe(tokens.trust.soft);
    expect(VARS.get("--color-distrust-strong")).toBe(tokens.distrust.strong);
    expect(VARS.get("--color-distrust-soft")).toBe(tokens.distrust.soft);
    expect(VARS.get("--color-kill")).toBe(tokens.kill);
    expect(VARS.get("--color-contradiction")).toBe(tokens.contradiction);
    expect(VARS.get("--color-dead")).toBe(tokens.status.dead.fill);
    expect(VARS.get("--color-contradiction-weak")).toBe(
      tokens.status.contradictionWeak.stroke,
    );
    expect(VARS.get("--color-contradiction-strong")).toBe(
      tokens.status.contradictionStrong.stroke,
    );
  });

  it("emits the radii, the spacing stops, the elevation and the motion tokens", () => {
    for (const [name, value] of Object.entries(tokens.radius)) {
      expect(VARS.get(`--radius-${name}`)).toBe(`${value}px`);
    }
    tokens.space.forEach((value, i) => {
      expect(VARS.get(`--space-${i}`)).toBe(`${value}px`);
    });
    // Tailwind derives every numeric spacing utility from this one base.
    expect(VARS.get("--spacing")).toBe(`${tokens.space[0]! / 16}rem`);
    expect(VARS.get("--shadow-chrome-1")).toBe(tokens.elevation.chrome1);
    expect(VARS.get("--shadow-chrome-2")).toBe(tokens.elevation.chrome2);
    expect(VARS.get("--shadow-data")).toBe(tokens.elevation.data);
    expect(VARS.get("--motion-quick")).toBe(`${tokens.motion.quick}ms`);
    expect(VARS.get("--motion-base")).toBe(`${tokens.motion.base}ms`);
    expect(VARS.get("--motion-slow")).toBe(`${tokens.motion.slow}ms`);
    expect(VARS.get("--ease-chrome")).toBe(tokens.motion.chromeEase);
    expect(VARS.get("--ease-data")).toBe(tokens.motion.dataEase);
  });

  it("emits the sub-xs type sizes", () => {
    for (const [name, px] of Object.entries(tokens.type.size)) {
      expect(VARS.get(`--text-${name}`)).toBe(`${px}px`);
    }
  });
});

// ── 3. firewall: the reserved channels stay disjoint ─────────────────────────

describe("FIREWALL: identity is identity only", () => {
  const RESERVED: readonly string[] = [
    tokens.kill,
    tokens.contradiction,
    tokens.trust.strong,
    tokens.trust.soft,
    tokens.distrust.strong,
    tokens.distrust.soft,
    ...tokens.suspicion,
  ];

  it("no identity hue collides with a reserved meaning channel", () => {
    // Binding rule (frontend/CLAUDE.md): amber = suspicion, blue = trust,
    // orange = distrust, red = kill, fuchsia = contradiction, and identity is
    // identity ONLY. A shared hex would make an identity swatch readable as a
    // claim about role or guilt.
    const reserved = new Set(RESERVED.map((hex) => hex.toUpperCase()));
    for (const hex of tokens.identity) {
      expect(reserved.has(hex.toUpperCase())).toBe(false);
    }
  });

  it("the identity palette has no duplicates (nine distinguishable players)", () => {
    const seen = new Set(tokens.identity.map((hex) => hex.toUpperCase()));
    expect(seen.size).toBe(tokens.identity.length);
    expect(tokens.identity.length).toBe(9);
  });

  it("the suspicion ramp is a 5-stop sequential ramp with its buckets inside it", () => {
    expect(tokens.suspicion).toHaveLength(5);
    expect(tokens.suspicionBucket.low).toBeGreaterThan(0);
    expect(tokens.suspicionBucket.low).toBeLessThan(tokens.suspicionBucket.high);
    expect(tokens.suspicionBucket.high).toBeLessThan(1);
  });

  it("every colour token is a full 6-digit hex (Pixi consumes them as numbers)", () => {
    const hexes = [
      ...Object.values(tokens.ink),
      ...Object.values(tokens.paper),
      ...tokens.identity,
      ...tokens.suspicion,
      ...RESERVED,
    ];
    for (const hex of hexes) {
      expect(hex).toMatch(/^#[0-9A-Fa-f]{6}$/);
    }
  });
});

// ── the two token helpers ────────────────────────────────────────────────────

describe("pixiHex", () => {
  it("converts a token hex to the 0xRRGGBB number the canvas layer needs", () => {
    expect(pixiHex("#FFFFFF")).toBe(0xffffff);
    expect(pixiHex("#000000")).toBe(0);
    expect(pixiHex(tokens.kill)).toBe(0xe23b2f);
  });

  it("accepts the no-hash and whitespace-padded forms", () => {
    expect(pixiHex(" 1B1814 ")).toBe(0x1b1814);
  });

  it("RAISES on a malformed value rather than falling back silently", () => {
    // AGENTS.md: no silent fallbacks. A bad token must not render as black.
    for (const bad of ["#FFF", "not-a-colour", "#GGGGGG", "", "#1234567"]) {
      expect(() => pixiHex(bad)).toThrow(/pixiHex/);
    }
  });

  it("converts every declared colour token without raising", () => {
    for (const hex of [
      ...Object.values(tokens.ink),
      ...Object.values(tokens.paper),
      ...tokens.identity,
      ...tokens.suspicion,
    ]) {
      expect(pixiHex(hex)).toBeGreaterThanOrEqual(0);
    }
  });
});

describe("suspicionBucketOf", () => {
  it("buckets on the seed thresholds (Low ≤ .35 < Med ≤ .72 < High)", () => {
    expect(suspicionBucketOf(0)).toBe("low");
    expect(suspicionBucketOf(0.35)).toBe("low"); // inclusive lower boundary
    expect(suspicionBucketOf(0.351)).toBe("med");
    expect(suspicionBucketOf(0.72)).toBe("med"); // inclusive upper boundary
    expect(suspicionBucketOf(0.721)).toBe("high");
    expect(suspicionBucketOf(1)).toBe("high");
  });

  it("uses the token thresholds, not hardcoded numbers", () => {
    expect(suspicionBucketOf(tokens.suspicionBucket.low)).toBe("low");
    expect(suspicionBucketOf(tokens.suspicionBucket.high)).toBe("med");
  });
});
