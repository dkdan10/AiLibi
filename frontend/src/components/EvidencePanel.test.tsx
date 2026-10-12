// The evidence panel. In the meeting, the source panel and the citation words it
// shares with the ballot links: a citation names what it points at, says so
// plainly when it points at nothing it can read, and carries the "not proof"
// caveat only once it has found its source. Off the meeting, a cited observation
// held by another player offers "See as p-1", the name the map toolbar and the
// inspector give one player's view; once that is the view, the offer gives way
// to the observer's memory.

import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { EvidencePanel, citationLabel } from "./EvidencePanel";
import { EVIDENCE_SOURCE_COPY, PERSPECTIVE_COPY, fmt } from "../lib/copy";
import type { EvidenceSelection } from "../lib/evidence";
import type { Perspective } from "../lib/playback";
import type { AgentMemoryView, MeetingView as MeetingDTO, ReplayView, TurnView } from "../types/api";

// Every case starts from one fixture: an observation p-1 holds, cited in
// meeting-0 and opened off the meeting through p-2's view. Its replay holds only
// what the panel reads of that meeting. The source-panel cases set the
// selection, the view, the replay and the open meeting they render.
const { state, fixture } = vi.hoisted(() => {
  const fixture = () => ({
    selectedEvidence: {
      kind: "observation",
      id: "p-1:12:0",
      meetingId: "meeting-0",
      observerId: "p-1",
    } as EvidenceSelection,
    currentReplay: {
      meetings: [{ meeting_id: "meeting-0", tick: 14, turns: [] }],
      ticks: [],
    } as unknown as Pick<ReplayView, "players" | "meetings" | "ticks">,
    selectedMeetingId: null as string | null,
    perspective: { mode: "agent", agentId: "p-2" } as Perspective,
    memoryCache: {} as Record<string, AgentMemoryView>,
    memoryErrors: {} as Record<string, string>,
    fetchMemoryView: () => Promise.resolve(),
  });
  return { state: fixture(), fixture };
});
vi.mock("../store/replayStore", () => ({
  useReplayStore: Object.assign((selector: (s: typeof state) => unknown) => selector(state), { getState: () => state }),
}));

beforeEach(() => {
  Object.assign(state, fixture());
});

function turn(index: number, speaker: string, kind: TurnView["turn_kind"]): TurnView {
  return { turn_id: `meeting-0:turn-${String(index)}`, turn_index: index, speaker, turn_kind: kind, reply_to: null, observations: [], claims: [], free_text: "said aloud", annotations: [], fabricated_opening: false };
}

const turns: TurnView[] = [turn(0, "p-1", "opening"), turn(3, "p-3", "reply"), turn(4, "p-4", "opt_in")];

const meeting: MeetingDTO = {
  meeting_id: "meeting-0", tick: 12, triggered_by: "p-1", trigger_kind: "body", outcome: "SKIPPED", ejected_player_id: null,
  turns, ballots: [], contradictions: [], llm_calls: [], prompt_versions: {}, total_cost_usd: 0,
  gate: { leader: null, leader_max_confidence: 0, threshold: 0.6, passed: false },
};

describe("citationLabel", () => {
  it.each([
    ["statement", "meeting-0:turn-3", "Statement by p-3 (turn 3)"],
    ["statement", "meeting-0:turn-9", "Statement (turn 9), not found in this meeting"],
    ["statement", "not-a-turn-id", "A statement this recording cannot read"],
    ["observation", "p-1:12:0", "What p-1 saw at tick 12"],
    ["observation", "p-7:-1:2", "What p-7 saw at tick -1"],
    ["observation", "opaque-99999", "An observation this recording cannot read"],
    ["artifact", "turn:meeting-0:turn-3:claim:0", "Part of the statement by p-3 (turn 3)"],
    ["artifact", "turn:meeting-0:turn-4:whereabouts:1", "Part of the statement by p-4 (turn 4)"],
    ["artifact", "turn:meeting-0:turn-9:obs:0", "Part of a statement (turn 9), not found in this meeting"],
    ["artifact", "turn:meeting-0:turn-3:unknown:0", "A source this recording cannot read"],
  ] as const)("names the %s id %s in plain words", (kind, id, words) => {
    expect(citationLabel(kind, id, turns)).toBe(words);
  });
});

function render(target: EvidenceSelection, perspective: Perspective = { mode: "omniscient" }, shown: MeetingDTO = meeting): string {
  state.selectedEvidence = target;
  state.perspective = perspective;
  state.selectedMeetingId = "meeting-0";
  state.currentReplay = { players: [], meetings: [shown], ticks: [] };
  return renderToStaticMarkup(<EvidencePanel inMeeting />);
}

const NOTE = EVIDENCE_SOURCE_COPY.resolvedNote;

describe("the source panel", () => {
  it("names a resolved statement, its kind of turn in words, and adds the caveat", () => {
    const html = render({ kind: "statement", id: "meeting-0:turn-4", meetingId: "meeting-0", observerId: null });
    expect(html).toContain('title="meeting-0:turn-4">Statement by p-4 (turn 4)</p>');
    expect(html).toContain("p-4 · public · spoke up · meeting tick 12");
    expect(html).toContain(NOTE);
    expect(html).not.toContain("A resolved citation identifies a source");
  });

  it.each([
    ["meeting-0:turn-0", "p-1 · public · first statement · meeting tick 37"],
    ["meeting-0:turn-3", "p-3 · public · reply · meeting tick 37"],
  ])("reads the kind of turn %s by its own name, at the meeting's own tick", (id, line) => {
    // A meeting at another tick than the fixture's, so the line must read both
    // the turn's kind and the meeting's tick rather than any one value.
    const html = render({ kind: "statement", id, meetingId: "meeting-0", observerId: null }, { mode: "omniscient" }, { ...meeting, tick: 37 });
    expect(html).toContain(line);
    expect(html).not.toContain("spoke up");
    expect(html).not.toContain("meeting tick 12");
  });

  it("drops the caveat from a statement this meeting does not hold, and says so", () => {
    const html = render({ kind: "statement", id: "meeting-0:turn-9", meetingId: "meeting-0", observerId: null });
    expect(html).toContain(">Statement (turn 9), not found in this meeting</p>");
    expect(html).toContain("Reference unavailable");
    expect(html).not.toContain(NOTE);
  });

  it("drops the caveat from an unreadable id", () => {
    const html = render({ kind: "statement", id: "not-a-turn-id", meetingId: "meeting-0", observerId: null });
    expect(html).toContain(">A statement this recording cannot read</p>");
    expect(html).not.toContain(NOTE);
  });

  it("drops the caveat from another player's observation, which this view cannot resolve", () => {
    state.memoryCache = {};
    const html = render({ kind: "observation", id: "p-1:12:0", meetingId: "meeting-0", observerId: "p-1" }, { mode: "agent", agentId: "p-3" });
    expect(html).toContain(">What p-1 saw at tick 12</p>");
    expect(html).toContain("private observation");
    expect(html).not.toContain(NOTE);
  });

  it("adds the caveat once an observation this view may read is found", () => {
    state.memoryCache = {
      "meeting-0:p-1": {
        agent_id: "p-1", tick: 12, role: "CREWMATE", tasks_completed: 0, tasks_assigned: 0, observations: [], beliefs: [], open_contradictions: [], rendered_memory_text: "",
        observation_references: [{ observation_id: "p-1:12:0", observer_id: "p-1", resolved: true, observation_tick: 12, scene_tick: 12, provenance: "observed", kind: "saw_player", text: "seen", subject_id: "p-2", room: null, from_room: null, to_room: null }],
      },
    };
    const html = render({ kind: "observation", id: "p-1:12:0", meetingId: "meeting-0", observerId: "p-1" }, { mode: "agent", agentId: "p-1" });
    expect(html).toContain(NOTE);
    // The same cached memory, read through another player's view, stays unresolved.
    expect(render({ kind: "observation", id: "p-1:12:0", meetingId: "meeting-0", observerId: "p-1" }, { mode: "agent", agentId: "p-3" })).not.toContain(NOTE);
    state.memoryCache = {};
  });
});

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
