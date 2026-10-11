// The mind inspector's header, rendered: one player's view is named the way the
// map toolbar names it ("See as p-1"), pressed or not, and a hidden role says
// why it is hidden in plain words.

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import { MindInspectorPanel, type MindInspectorPanelProps } from "./MindInspector";
import { PERSPECTIVE_COPY, fmt } from "../lib/copy";
import type { PlayerView } from "../types/api";

vi.mock("../store/replayStore", () => ({
  useReplayStore: (selector: (s: Record<string, unknown>) => unknown) =>
    selector({ selectedMeetingId: null, currentReplay: null, selectedEvidence: null }),
}));

const players: PlayerView[] = [
  { agent_id: "p-1", display_name: "p-1", role: "IMPOSTOR", color: "#ff0000" },
  { agent_id: "p-2", display_name: "p-2", role: "CREWMATE", color: "#0000ff" },
];

const mind: MindInspectorPanelProps = {
  players,
  selectedAgentId: "p-1",
  meeting: undefined,
  memory: undefined,
  memoryError: null,
  isAlive: true,
  ownKills: [],
  coverTasks: [],
  perspective: { mode: "agent", agentId: "p-2" },
  noMeetingYet: true,
  onSelectAgent: () => {},
  onShowWhatTheySaw: () => {},
};

/**
 * The inspected player's header's view button: whether it is pressed, and what
 * it says. Read inside the header, since the player picker above it is a row of
 * pressed-or-not buttons too.
 */
function viewButton(html: string): { pressed: string; text: string } | null {
  const header = /<header\b[\s\S]*?<\/header>/.exec(html)?.[0] ?? "";
  const match = /<button type="button" aria-pressed="(true|false)"[^>]*>([\s\S]*?)<\/button>/.exec(
    header,
  );
  if (match === null) return null;
  return { pressed: match[1] ?? "", text: (match[2] ?? "").replace(/<[^>]*>/g, "") };
}

describe("the inspector's view button", () => {
  it("offers to see as the inspected player through another player's view", () => {
    const html = renderToStaticMarkup(<MindInspectorPanel {...mind} />);
    expect(viewButton(html)).toEqual({
      pressed: "false",
      text: fmt(PERSPECTIVE_COPY.seeAs, { agent: "p-1" }),
    });
    expect(html).toContain(`title="${PERSPECTIVE_COPY.roleHiddenTitle.replace(/'/g, "&#x27;")}"`);
    expect(html).not.toMatch(/Show what they saw|\bfog\b|firewall/);
  });

  it("keeps the same name, pressed, once that is the view", () => {
    const html = renderToStaticMarkup(
      <MindInspectorPanel {...mind} perspective={{ mode: "agent", agentId: "p-1" }} />,
    );
    expect(viewButton(html)).toEqual({ pressed: "true", text: "See as p-1 ✓" });
    expect(html).not.toMatch(/Seeing what they saw/);
  });

  it("is not pressed in the all-roles view", () => {
    const html = renderToStaticMarkup(
      <MindInspectorPanel {...mind} perspective={{ mode: "omniscient" }} />,
    );
    expect(viewButton(html)).toEqual({ pressed: "false", text: "See as p-1" });
  });
});
