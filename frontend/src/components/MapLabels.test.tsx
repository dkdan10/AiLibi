// The map canvas's words. The canvas is Pixi, which no DOM test reads, so each
// component is called as a function and its text elements are read off the
// element tree it returns: a lone body says who killed it, an unseen room says
// it is unseen, and the sabotage readout keeps one style in both views while one
// player's view still hides the room and the countdown.

import { isValidElement, type ReactNode } from "react";
import { describe, expect, it } from "vitest";

import { BodyMarker } from "./BodyMarker";
import { RoomRect } from "./RoomRect";
import { SabotageOverlay } from "./SabotageOverlay";
import { MAP_COPY, killedByLabel, sabotageHud } from "../lib/copy";
import type { RoomView, SabotageDetailView } from "../types/api";

/** The `text` of every `pixiText` in an element tree, in order. */
function canvasTexts(node: ReactNode): readonly string[] {
  if (Array.isArray(node)) return node.flatMap((child: ReactNode) => canvasTexts(child));
  if (!isValidElement(node)) return [];
  const props = node.props as { text?: unknown; children?: ReactNode };
  const own = node.type === "pixiText" && typeof props.text === "string" ? [props.text] : [];
  return [...own, ...canvasTexts(props.children)];
}

const ROOM: RoomView = {
  id: "REACTOR",
  name: "Reactor",
  position: { x: 0, y: 0 },
  size: { width: 10, height: 8 },
} as RoomView;

function body(killedBy: string | null, slotCount = 1): readonly string[] {
  return canvasTexts(
    BodyMarker({
      room: ROOM,
      slotIndex: 0,
      slotCount,
      isDiscovered: true,
      victimLabel: "p-2",
      killedBy,
      glyph: "",
      scale: 10,
      offsetX: 0,
      offsetY: 0,
    }),
  );
}

describe("a body on the map", () => {
  it("says who killed a lone body", () => {
    expect(body("p-4")).toEqual(["p-2", killedByLabel("p-4")]);
    expect(body("p-4")).toEqual(["p-2", "killed by p-4"]);
  });

  it("names no killer in one player's view or in a cluster", () => {
    expect(body(null)).toEqual(["p-2"]);
    expect(body("p-4", 2)).toEqual(["p-2"]);
  });
});

describe("a room on the map", () => {
  it("names a seen room, and says an unseen one is unseen", () => {
    const room = (visible: boolean) =>
      canvasTexts(RoomRect({ room: ROOM, scale: 10, offsetX: 0, offsetY: 0, visible }));
    expect(room(true)).toEqual(["Reactor"]);
    expect(room(false)).toEqual([MAP_COPY.unseenRoom]);
    expect(room(false)).not.toContain("FOG");
  });
});

describe("the sabotage readout", () => {
  const REACTOR: SabotageDetailView = {
    kind: "reactor",
    remaining_ticks: 5,
    affected_rooms: ["REACTOR"],
    repair_progress: {},
  };

  function hud(sabotage: SabotageDetailView, omniscient: boolean, agentAware = true) {
    return canvasTexts(
      SabotageOverlay({
        width: 800,
        height: 600,
        sabotage,
        roomsById: new Map([["REACTOR", ROOM]]),
        scale: 10,
        offsetX: 0,
        offsetY: 0,
        reactorGlyph: "",
        lightsGlyph: "",
        omniscient,
        agentAware,
      }),
    );
  }

  it("counts the sabotage down in the all-roles view", () => {
    expect(hud(REACTOR, true)).toEqual(["Reactor meltdown in 5 ticks"]);
    expect(hud({ ...REACTOR, kind: "lights", remaining_ticks: 12 }, true)).toEqual([
      "Lights out, 12 ticks left",
    ]);
  });

  it("names neither room nor countdown in one player's view, in the same style", () => {
    expect(hud(REACTOR, false)).toEqual([sabotageHud("reactor", 5, false)]);
    expect(hud(REACTOR, false)).toEqual(["Sabotage alarm"]);
    expect(hud({ ...REACTOR, kind: "lights" }, false)).toEqual(["Lights out"]);
    // A player who never heard the alarm sees no readout at all, as before.
    expect(hud(REACTOR, false, false)).toEqual([]);
  });
});
