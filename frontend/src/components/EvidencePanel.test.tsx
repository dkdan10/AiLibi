// The evidence panel, rendered off the meeting: a cited observation held by
// another player offers "See as p-1", the name the map toolbar and the inspector
// give one player's view; once that is the view, the offer gives way to the
// observer's memory.

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import { EvidencePanel } from "./EvidencePanel";
import { PERSPECTIVE_COPY, fmt } from "../lib/copy";
import type { Perspective } from "../lib/playback";

const state = vi.hoisted(() => ({
  selectedEvidence: {
    kind: "observation",
    id: "p-1:12:0",
    meetingId: "meeting-0",
    observerId: "p-1",
  },
  currentReplay: {
    meetings: [{ meeting_id: "meeting-0", tick: 14, turns: [] }],
    ticks: [],
  },
  selectedMeetingId: null,
  perspective: { mode: "agent", agentId: "p-2" } as Perspective,
  memoryCache: {},
  memoryErrors: {},
  fetchMemoryView: () => Promise.resolve(),
}));
vi.mock("../store/replayStore", () => ({
  useReplayStore: Object.assign(
    (selector: (s: typeof state) => unknown) => selector(state),
    { getState: () => state },
  ),
}));

/** The text of every button the panel offers. */
function buttons(html: string): readonly string[] {
  return [...html.matchAll(/<button\b[^>]*>([\s\S]*?)<\/button>/g)].map((match) =>
    (match[1] ?? "").replace(/<[^>]*>/g, "").replace(/&#x27;/g, "'"),
  );
}

describe("the evidence panel's way into a private observation", () => {
  it("offers to see as the observer through another player's view", () => {
    state.perspective = { mode: "agent", agentId: "p-2" };
    const html = renderToStaticMarkup(<EvidencePanel />);
    expect(buttons(html)).toContain(fmt(PERSPECTIVE_COPY.seeAs, { agent: "p-1" }));
    expect(buttons(html)).not.toContain("Open p-1's meeting memory");
    expect(html).not.toMatch(/Switch to p-1|perspective<\/button>/);
  });

  it("names whichever player holds the observation", () => {
    const held = state.selectedEvidence;
    state.selectedEvidence = { ...held, id: "p-3:12:0", observerId: "p-3" };
    state.perspective = { mode: "agent", agentId: "p-2" };
    try {
      expect(buttons(renderToStaticMarkup(<EvidencePanel />))).toContain("See as p-3");
    } finally {
      state.selectedEvidence = held;
    }
  });

  it("gives way to the observer's memory once that is the view", () => {
    for (const perspective of [
      { mode: "agent", agentId: "p-1" },
      { mode: "omniscient" },
    ] as const) {
      state.perspective = perspective;
      const html = renderToStaticMarkup(<EvidencePanel />);
      expect(buttons(html)).toContain("Open p-1's meeting memory");
      expect(buttons(html)).not.toContain(fmt(PERSPECTIVE_COPY.seeAs, { agent: "p-1" }));
    }
  });
});
