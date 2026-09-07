import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { BallotCard } from "./BallotCard";
import { MeetingView } from "./MeetingView";
import { MindInspectorPanel, type MindInspectorPanelProps } from "./MindInspector";
import type { BallotView, MeetingView as MeetingDTO, PlayerView, ReplayView } from "../types/api";
import type { Perspective } from "../lib/playback";

const state = vi.hoisted(() => ({
  perspective: { mode: "agent", agentId: "p-2" } as Perspective,
  selectedMeetingId: "meeting-0",
  currentReplay: null as Pick<ReplayView, "players" | "meetings"> | null,
  revealOutcome: false,
  selectedEvidence: null,
  memoryCache: {},
  memoryErrors: {},
}));
vi.mock("../store/replayStore", () => ({ useReplayStore: (selector: (s: typeof state) => unknown) => selector(state) }));
const players: PlayerView[] = [
  { agent_id: "p-1", display_name: "p-1", role: "IMPOSTOR", color: "#ff0000" },
  { agent_id: "p-2", display_name: "p-2", role: "CREWMATE", color: "#0000ff" },
];
const ballot: BallotView = { voter: "p-1", target: "p-2", confidence: 0.73, primary_reason_id: "private-statement-choice", primary_reason_observation_id: "private-observation-choice", considered_alternatives: [], rationale_text: "I killed them", rationale_text_clean: "I killed them", rewrite_reasons: [] };
const meeting: MeetingDTO = {
  meeting_id: "meeting-0", tick: 10, triggered_by: "p-1", trigger_kind: "body",
  outcome: "EJECTED", ejected_player_id: "p-2", turns: [], contradictions: [], llm_calls: [], prompt_versions: {}, total_cost_usd: 0,
  ballots: [ballot, { ...ballot, voter: "p-3", confidence: 0.42 }, { ...ballot, voter: "p-2", target: "SKIP", confidence: 0.21 }],
  gate: { leader: "p-2", leader_max_confidence: 0.73, threshold: 0.6, passed: true },
};
const mind: MindInspectorPanelProps = {
  players, selectedAgentId: "p-1", meeting: undefined, memoryError: null,
  memory: { agent_id: "p-1", tick: 10, role: "IMPOSTOR", tasks_completed: 0, tasks_assigned: 0,
    observations: [{ type: "saw_player", subject: "private-subject", room: "private-room", tick: 9, co_present: [] }],
    beliefs: [{ subject: "private-belief", suspicion: 0.81, confidence: 0.74, snapshot_tick: 10 }],
    open_contradictions: [{ contradiction_id: "private-flag", kind: "alibi_conflict", event_a_id: "a", event_b_id: "b", subjects: ["p-2"], description: "private flag description", weak: false, severity: "strong", category: "cross_statement" }],
    rendered_memory_text: "private rendered memory" },
  isAlive: true, ownKills: [], coverTasks: [], perspective: { mode: "agent", agentId: "p-2" },
  onSelectAgent: () => {}, onShowWhatTheySaw: () => {},
};

describe("private reasoning perspective", () => {
  it.each([false, true])("keeps another ballot's confidence out of Resolution, outcome reveal=%s", (revealOutcome) => {
    state.perspective = { mode: "agent", agentId: "p-2" };
    state.currentReplay = { players, meetings: [meeting] };
    state.revealOutcome = revealOutcome;
    const html = renderToStaticMarkup(<MeetingView />);
    expect(html).toContain("Resolution");
    expect(html).toContain("Ejected — p-2");
    expect(html).not.toContain("0.73");
    expect(html).not.toContain("0.42");
    expect(html).not.toContain("top ballot");
  });
  it.each([["p-1", "0.73"], ["p-3", "0.42"]])("Resolution shows only %s's own leader ballot", (observerId, confidence) => {
    state.perspective = { mode: "agent", agentId: observerId };
    state.currentReplay = { players, meetings: [meeting] };
    const html = renderToStaticMarkup(<MeetingView />);
    expect(html).toContain(`your ballot ${confidence}`);
    expect(html).not.toContain("top ballot");
    if (observerId === "p-3") expect(html).not.toContain("0.73");
  });
  it("retains the aggregate Resolution confidence only in omniscient mode", () => {
    state.perspective = { mode: "omniscient" };
    state.currentReplay = { players, meetings: [meeting] };
    const html = renderToStaticMarkup(<MeetingView />);
    expect(html).toContain("top ballot 0.73");
    expect(html).not.toContain("your ballot");
  });
  it.each(["p-2", null])("does not expose confidence when the gate fails or ties, leader=%s", (leader) => {
    state.perspective = { mode: "agent", agentId: "p-2" };
    state.currentReplay = { players, meetings: [{
      ...meeting, outcome: "SKIPPED", ejected_player_id: null,
      ballots: meeting.ballots.map((entry) => entry.voter === "p-1" ? { ...entry, confidence: 0.53 } : entry),
      gate: { ...meeting.gate, leader, passed: false, leader_max_confidence: 0.53 },
    }] };
    const html = renderToStaticMarkup(<MeetingView />);
    expect(html).toContain("SKIPPED");
    expect(html).not.toContain("0.53");
    expect(html).not.toContain("0.42");
  });
  it.each([false, true])("hides model-authored ballot secrets without relying on guard markers, outcome reveal=%s", (revealOutcome) => {
    state.perspective = { mode: "agent", agentId: "p-2" };
    const html = renderToStaticMarkup(<BallotCard ballot={ballot} players={players} omniscient={false} revealOutcome={revealOutcome} />);
    expect(html).toContain("p-1");
    expect(html).toContain("p-2");
    expect(html).toContain("Private ballot reasoning");
    for (const secret of ["I killed them", "0.73", "private-statement-choice", "private-observation-choice"]) expect(html).not.toContain(secret);
    expect(html).not.toContain("no rationale recorded");
  });
  it.each([false, true])("shows reasoning from the voter’s lens or omniscient mode: %s", (omniscient) => {
    state.perspective = { mode: "agent", agentId: omniscient ? "p-2" : "p-1" };
    const html = renderToStaticMarkup(<BallotCard ballot={ballot} players={players} omniscient={omniscient} revealOutcome={false} />);
    expect(html).toContain("I killed them");
    expect(html).toContain("private-observation-choice");
    expect(html).not.toContain("incorrect");
  });
  it("explains redirected votes without presenting the original rationale as the applied choice", () => {
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, rewrite_reasons: ["under_gate_redirect"] }} players={players} omniscient revealOutcome={false} />);
    expect(html).toContain("Vote redirected by the meeting rule");
    expect(html).toContain("before the vote was redirected");
    expect(html).not.toContain("under_gate_redirect");
  });
  it.each(["belief", "memory", "flags", "prompt", "response"] as const)("hides cached private %s through another lens", (tab) => {
    const html = renderToStaticMarkup(<MindInspectorPanel {...mind} tab={tab} />);
    expect(html).toContain("memory and reasoning are private");
    expect(html).toContain("Show what they saw");
    for (const secret of ["private-room", "private-belief", "private flag description", "private rendered memory"]) expect(html).not.toContain(secret);
  });
  it.each(["belief", "memory", "flags"] as const)("keeps real %s available to the observer", (tab) => {
    const html = renderToStaticMarkup(<MindInspectorPanel {...mind} perspective={{ mode: "agent", agentId: "p-1" }} tab={tab} />);
    expect(html).not.toContain("memory and reasoning are private");
    expect(html).toContain(tab === "belief" ? "private-belief" : tab === "memory" ? "private-room" : "private flag description");
  });
});
