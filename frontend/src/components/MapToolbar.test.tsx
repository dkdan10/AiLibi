// The map toolbar, rendered: the chip reads "Map", and the switcher names one
// player's view the way the banner and the inspector do ("See as p-1").

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import { MapToolbar } from "./MapToolbar";
import { MAP_COPY, PERSPECTIVE_COPY } from "../lib/copy";
import type { Perspective } from "../lib/playback";

const state = vi.hoisted(() => ({
  currentReplay: {
    players: [{ agent_id: "p-0" }, { agent_id: "p-1" }, { agent_id: "p-3" }],
    map: { rooms: [], edges: [], vents: [] },
  } as unknown,
  perspective: { mode: "omniscient" } as Perspective,
  setPerspective: () => {},
}));
vi.mock("../store/replayStore", () => ({
  useReplayStore: (selector: (s: typeof state) => unknown) => selector(state),
}));
// p-0 is dead at this frame, so the first player the toggle would open on is p-1.
const playback = vi.hoisted(() => ({
  frame: {
    agent_states: [
      { agent_id: "p-0", is_alive: false },
      { agent_id: "p-1", is_alive: true },
      { agent_id: "p-3", is_alive: true },
    ],
  } as unknown,
}));
vi.mock("../hooks/usePlayback", () => ({ usePlayback: () => playback }));

/** The text of every button in the markup, in order. */
function buttons(html: string): readonly string[] {
  return [...html.matchAll(/<button\b[^>]*>([\s\S]*?)<\/button>/g)].map((match) =>
    (match[1] ?? "").replace(/<[^>]*>/g, ""),
  );
}

function toolbar(perspective: Perspective): string {
  state.perspective = perspective;
  return renderToStaticMarkup(<MapToolbar />);
}

describe("the map toolbar", () => {
  it("names the map plainly and offers the first living player's view", () => {
    const html = toolbar({ mode: "omniscient" });
    expect(html).toContain(`>${MAP_COPY.chip}</span>`);
    expect(buttons(html)).toEqual(["Omniscient", "See as p-1"]);
    expect(html).toContain(`title="${PERSPECTIVE_COPY.daggerTitle}"`);
    expect(html).not.toMatch(/canonical_1|corridors|vent ring|As-agent|\bfog\b/);
  });

  it("names the player on screen, and its picker in the same words", () => {
    const html = toolbar({ mode: "agent", agentId: "p-3" });
    expect(buttons(html)).toEqual(["Omniscient", "See as p-3"]);
    expect(html).toContain('aria-pressed="true"');
    expect(html).toContain(`title="${PERSPECTIVE_COPY.pickerTitle.replace(/'/g, "&#x27;")}"`);
    expect(html).toContain(`>${PERSPECTIVE_COPY.pickerLabel}</span>`);
    expect(html).not.toMatch(/fog of war|As-agent|simulate/);
  });

  it("says who it would show when the recording has no player to see as", () => {
    const players = (state.currentReplay as { players: unknown[] }).players;
    const frame = playback.frame;
    (state.currentReplay as { players: unknown[] }).players = [];
    playback.frame = { agent_states: [] };
    try {
      expect(buttons(toolbar({ mode: "omniscient" }))).toEqual([
        "Omniscient",
        PERSPECTIVE_COPY.seeAsNobody,
      ]);
    } finally {
      (state.currentReplay as { players: unknown[] }).players = players;
      playback.frame = frame;
    }
  });
});
