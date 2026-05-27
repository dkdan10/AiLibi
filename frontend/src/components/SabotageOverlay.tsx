// Sabotage state overlay (DESIGN.md §7, §8.3 — "Sabotage limited to lights").
// When the current tick has a "lights" sabotage active, a translucent dark tint
// covers the whole canvas to signal reduced visibility. Rendering branches on
// the sabotage kind string, so future kinds (reactor / O2, out of MVP scope)
// are silently skipped rather than crashing. Rendered last in the tree so the
// tint sits above rooms, vents, bodies, and tokens.

import type { Graphics } from "pixi.js";

interface SabotageOverlayProps {
  width: number;
  height: number;
  activeKinds: readonly string[];
}

const LIGHTS_TINT_COLOR = 0x000010;
const LIGHTS_TINT_ALPHA = 0.45;

export function SabotageOverlay({
  width,
  height,
  activeKinds,
}: SabotageOverlayProps) {
  // Only "lights" has a rendering in MVP; unknown kinds fall through to null.
  if (!activeKinds.includes("lights")) {
    return null;
  }

  return (
    <pixiGraphics
      draw={(graphics: Graphics) => {
        graphics.clear();
        graphics.rect(0, 0, width, height);
        graphics.fill({ color: LIGHTS_TINT_COLOR, alpha: LIGHTS_TINT_ALPHA });
      }}
    />
  );
}
