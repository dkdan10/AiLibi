// Generates the Tailwind v4 `@theme` custom-property block inside src/index.css
// from the single token source (src/tokens.ts), so the DOM layer never restates
// a hex/space/type value by hand. Run with `npm run gen:tokens`.
//
// Only the text between the `tokens:start` / `tokens:end` markers is rewritten;
// the rest of index.css (Tailwind import, fonts, base layer) is hand-authored.
// Re-running on an unchanged tokens.ts must produce no diff — that is the
// single-source guarantee (checkable by hand: regenerate, then `git diff`).
//
// Run via `node --experimental-strip-types` (no build step, no extra deps).

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { tokens } from "../src/tokens.ts";

const START =
  "/* tokens:start — generated from src/tokens.ts via `npm run gen:tokens`; do not edit by hand */";
const END = "/* tokens:end */";

// Pull the family name out of a seed `type` token like "600 'Fredoka'". Only
// the family is single-sourced from tokens.ts; the fallback stack below is a
// rendering concern, not a design token.
function familyOf(typeToken: string): string {
  const match = typeToken.match(/'([^']+)'/);
  if (match === null || match[1] === undefined) {
    throw new Error(`familyOf: no quoted family in ${JSON.stringify(typeToken)}`);
  }
  return match[1];
}

function buildThemeBody(): string {
  const lines: string[] = [];
  const push = (line = ""): void => {
    lines.push(line);
  };

  push("  /* paper & ink neutral ramp */");
  for (const [step, hex] of Object.entries(tokens.paper)) {
    push(`  --color-paper-${step}: ${hex};`);
  }
  for (const [step, hex] of Object.entries(tokens.ink)) {
    push(`  --color-ink-${step}: ${hex};`);
  }
  push();

  push("  /* reserved meaning channels — never cross-used (firewall) */");
  tokens.suspicion.forEach((hex, i) => push(`  --color-suspicion-${i + 1}: ${hex};`));
  push(`  --color-trust-strong: ${tokens.trust.strong};`);
  push(`  --color-trust-soft: ${tokens.trust.soft};`);
  push(`  --color-distrust-strong: ${tokens.distrust.strong};`);
  push(`  --color-distrust-soft: ${tokens.distrust.soft};`);
  push(`  --color-kill: ${tokens.kill};`);
  push(`  --color-contradiction: ${tokens.contradiction};`);
  push();

  push("  /* status colours (components always pair these with a shape/glyph) */");
  push(`  --color-dead: ${tokens.status.dead.fill};`);
  push(`  --color-contradiction-weak: ${tokens.status.contradictionWeak.stroke};`);
  push(`  --color-contradiction-strong: ${tokens.status.contradictionStrong.stroke};`);
  push();

  push("  /* identity palette — identity ONLY (p-0 … p-8) */");
  tokens.identity.forEach((hex, i) => push(`  --color-identity-${i}: ${hex};`));
  push();

  push("  /* radii */");
  for (const [name, value] of Object.entries(tokens.radius)) {
    push(`  --radius-${name}: ${value}px;`);
  }
  push();

  // Tailwind v4 derives every numeric spacing/sizing utility (`p-4`, `gap-2`,
  // `w-8`, …) from the base `--spacing`, so emit it from the token unit
  // (`space[0]`) — that is what makes the scale token-driven rather than the
  // framework default. Expressed in rem (÷16) to keep Tailwind's rem semantics
  // (respects user zoom); the seed's px stops [4,8,12,16,24,32,48] then land on
  // p-1/2/3/4/6/8/12. The named `--space-*` px vars stay for exact `var()` /
  // Pixi use (the canvas needs px numbers).
  const firstSpace = tokens.space[0];
  if (firstSpace === undefined) {
    throw new Error("gen-tokens-css: tokens.space is empty");
  }
  push("  /* spacing — base unit drives Tailwind's numeric scale; --space-* = exact-px stops */");
  push(`  --spacing: ${firstSpace / 16}rem;`);
  tokens.space.forEach((value, i) => push(`  --space-${i}: ${value}px;`));
  push();

  push("  /* elevation — hard offset shadow = CHROME only; data = 1px hairline */");
  push(`  --shadow-chrome-1: ${tokens.elevation.chrome1};`);
  push(`  --shadow-chrome-2: ${tokens.elevation.chrome2};`);
  push(`  --shadow-data: ${tokens.elevation.data};`);
  push();

  push("  /* motion — purposeful only */");
  push(`  --motion-quick: ${tokens.motion.quick}ms;`);
  push(`  --motion-base: ${tokens.motion.base}ms;`);
  push(`  --motion-slow: ${tokens.motion.slow}ms;`);
  push(`  --ease-chrome: ${tokens.motion.chromeEase};`);
  push(`  --ease-data: ${tokens.motion.dataEase};`);
  push();

  push("  /* two-truth grammar */");
  push(`  --truth-belief-opacity: ${tokens.truth.belief.opacity};`);
  push(`  --truth-ground-outline: ${tokens.truth.ground.outline};`);
  push();

  push("  /* type */");
  push(`  --font-display: "${familyOf(tokens.type.display)}", system-ui, sans-serif;`);
  push(`  --font-body: "${familyOf(tokens.type.body)}", system-ui, sans-serif;`);
  push(
    `  --font-mono: "${familyOf(tokens.type.mono)}", ui-monospace, "SFMono-Regular", monospace;`,
  );

  return lines.join("\n");
}

const cssPath = resolve(dirname(fileURLToPath(import.meta.url)), "../src/index.css");
const css = readFileSync(cssPath, "utf8");

const startIdx = css.indexOf(START);
const endIdx = css.indexOf(END);
if (startIdx === -1 || endIdx === -1) {
  throw new Error(
    "gen-tokens-css: could not find the tokens:start / tokens:end markers in src/index.css",
  );
}

const before = css.slice(0, startIdx + START.length);
const after = css.slice(endIdx);
const next = `${before}\n${buildThemeBody()}\n  ${after}`;

writeFileSync(cssPath, next);
console.log("gen-tokens-css: wrote @theme block to src/index.css");
