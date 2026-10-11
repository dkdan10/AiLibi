// The ticker's view chip, rendered: it names the view the feed was projected
// through, in the words the banner uses ("watching as p-6"), and its tooltip
// says in plain words what one player's feed leaves out. The projection itself
// is pinned, renderer-free, in `EventTicker.test.ts`.

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import { EventTicker } from "./EventTicker";
import { PERSPECTIVE_COPY } from "../lib/copy";
import type { Perspective } from "../lib/playback";

const state = vi.hoisted(() => ({
  currentReplay: { ticks: [], meetings: [] } as unknown,
  perspective: { mode: "omniscient" } as Perspective,
}));
vi.mock("../store/replayStore", () => ({
  useReplayStore: (selector: (s: typeof state) => unknown) => selector(state),
}));
vi.mock("../hooks/usePlayback", () => ({
  usePlayback: () => ({ frameIndex: 0, tickNumber: 5 }),
}));

/** The chip beside the ticker's heading: its tooltip and its text. */
function chip(perspective: Perspective): { title: string; text: string } {
  state.perspective = perspective;
  const html = renderToStaticMarkup(<EventTicker />);
  const match = /<span class="rounded-pill[^"]*" title="([^"]*)">([\s\S]*?)<\/span>/.exec(html);
  return {
    title: (match?.[1] ?? "").replace(/&#x27;/g, "'"),
    text: (match?.[2] ?? "").replace(/<!-- -->/g, ""),
  };
}

describe("the ticker's view chip", () => {
  it("names one player's view as the banner does", () => {
    expect(chip({ mode: "agent", agentId: "p-6" })).toEqual({
      title: PERSPECTIVE_COPY.tickerTitle,
      text: "watching as p-6 · to t5",
    });
    expect(chip({ mode: "agent", agentId: "p-2" }).text).toBe("watching as p-2 · to t5");
  });

  it("names the all-roles feed as before", () => {
    expect(chip({ mode: "omniscient" }).text).toBe("omniscient · to t5");
    expect(chip({ mode: "omniscient" }).text).not.toMatch(/\bfog\b/);
  });
});
