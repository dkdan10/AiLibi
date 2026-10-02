// The map's wiring to its pure helpers, pinned on the source.
//
// `MapView.tsx` draws on a Pixi canvas, which this node-environment runner
// cannot load (it pulls Pixi and the Vite `?raw` SVG set at module scope), and
// the browser legs cannot read a token's tween off a canvas. So the BEHAVIOUR is
// pinned where it lives — `lib/vents.ts`, `lib/regroup.ts` and their tests over
// the committed skeleton dump — and this file pins only that the map reads those
// helpers rather than a local rule: each wiring line below, removed or swapped
// back for the rule it replaced, fails here. The regroup note's DOM half is
// also walked in the browser (`e2e/journey.spec.ts`).

import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const SOURCE = readFileSync(resolve(dirname(fileURLToPath(import.meta.url)), "MapView.tsx"), "utf8");

/** `source` with line, block and JSX comments removed (MapView carries no `//` in a string). */
function code(source: string): string {
  return source.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
}

/** Each fragment the map must carry, in order of the frame it draws. */
const WIRING: readonly (readonly [string, string])[] = [
  ["every dive is one trip", "() => ventTrips(currentReplay?.ticks ?? [])"],
  ["a step across a regroup snaps", "const animate = shouldTween(currentReplay, prevTick, currentTick, {"],
  ["the step reads the replay identity", "sameReplay,"],
  ["the step reads reduced motion", "reducedMotion: prefersReducedMotion,"],
  ["the trips drawn on this tick", "? activeTrips(trips, tickNumber)"],
  ["a venting token draws as its trip", "if (activeVentByActor.has(state.agent_id)) continue;"],
  ["each trip is posed", "const pose = tripPose(trip, tickNumber);"],
  ["the pose moves the traveller", "progress={pose.progress}"],
  ["the pose sizes a held trip", "heldScale={pose.heldScale}"],
  ["a held trip keeps its size", "const capsuleScale = heldScale ?? 1 - 0.4 * Math.sin(travelled * Math.PI);"],
  ["the note shows on a regrouping recording", "{regroupsAfterMeetings(currentReplay) && ("],
  ["the note's words come from the copy", "{MAP_COPY.regroupNote}"],
];

function assertWired(source: string): void {
  const stripped = code(source);
  for (const [why, fragment] of WIRING) {
    expect(stripped.includes(fragment), why).toBe(true);
  }
  // The rule `lib/vents.ts` replaced is gone, not merely unused.
  expect(stripped.includes("buildVentSegments"), "the retired pairing rule").toBe(false);
  expect(stripped.includes("pendingDive"), "the retired pairing rule").toBe(false);
}

describe("MapView reads the pure helpers", () => {
  it("carries every wiring line", () => {
    assertWired(SOURCE);
  });

  it("strips comments without eating the code it checks", () => {
    expect(code("const a = 1; // ventTrips(\n/* tripPose( */ const b = 2;")).toBe("const a = 1; \n const b = 2;");
  });

  it.each(WIRING.map(([why, fragment]) => [why, fragment]))("fails without: %s", (_why, fragment) => {
    // Planted, per line: the fragment swapped for a neutral stand-in.
    expect(() => assertWired(SOURCE.replace(fragment, "/* removed */"))).toThrow();
  });

  it("fails when the animate rule reverts to the one that tweened every regroup", () => {
    const reverted = SOURCE.replace(
      "const animate = shouldTween(currentReplay, prevTick, currentTick, {",
      "const animate = sameReplay && Math.abs(currentTick - prevTick) === 1 && !prefersReducedMotion; ({",
    );
    expect(() => assertWired(reverted)).toThrow(/a step across a regroup snaps/);
  });
});
