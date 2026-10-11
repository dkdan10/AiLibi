// The omniscient meeting record, rendered: present under the omniscient lens,
// absent from the DOM under every agent lens.
//
// THE PLANTED LEAK. `assertNoEngineRecord` is the check an agent-lens render
// must pass; the same helper applied to the omniscient render of the same
// meeting has to throw, which is what proves it can see the record at all.

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import { MeetingView } from "./MeetingView";
import { MEETING_COPY } from "../lib/copy";
import type { Perspective } from "../lib/playback";
import type {
  AgentTickStateView,
  ContradictionView,
  ExperimentConfigView,
  MeetingView as MeetingDTO,
  PlayerView,
  ReplayView,
  TickEventView,
  TickView,
  TurnView,
} from "../types/api";

type Replay = Pick<ReplayView, "players" | "meetings" | "ticks" | "map" | "metadata">;

const state = vi.hoisted(() => ({
  perspective: { mode: "omniscient" } as Perspective,
  selectedMeetingId: "planted:meeting-0",
  currentReplay: null as Replay | null,
  revealOutcome: false,
  selectedEvidence: null,
  memoryCache: {},
  memoryErrors: {},
}));
vi.mock("../store/replayStore", () => ({
  useReplayStore: (selector: (s: typeof state) => unknown) => selector(state),
}));

const players: PlayerView[] = [
  { agent_id: "p-1", display_name: "p-1", role: "CREWMATE", color: "#3355aa" },
  { agent_id: "p-2", display_name: "p-2", role: "IMPOSTOR", color: "#aa3355" },
  { agent_id: "p-3", display_name: "p-3", role: "CREWMATE", color: "#33aa55" },
  { agent_id: "p-4", display_name: "p-4", role: "CREWMATE", color: "#55aa33" },
];

/** A recorded config with every field at its default. */
const CONFIG: ExperimentConfigView = {
  format_version: 1,
  redistribution_policy: "lowest_id",
  meeting_reset: "preserve",
  crew_idle_policy: "hub_wait",
  vent_exit_policy: "target_distance",
  post_meeting_retarget: false,
  self_report: false,
  sabotage_threshold: "six_sevenths",
  evidence_reasoning_version: null,
  bounded_rebuttal_version: null,
  public_account_version: null,
  attributed_testimony_version: null,
};

const room = (id: string, name: string) => ({ id, name, position: { x: 0, y: 0 }, size: { width: 1, height: 1 } });

/** Where each player stands per tick, and who is inside a vent. */
const PLACES: Record<number, Record<string, string>> = {
  0: { "p-1": "ADMIN", "p-2": "LABS", "p-3": "ADMIN", "p-4": "LABS" },
  1: { "p-1": "ADMIN", "p-2": "LABS", "p-3": "ADMIN", "p-4": "LABS" },
  2: { "p-1": "ADMIN", "p-2": "LABS", "p-3": "ADMIN" },
  3: { "p-1": "ADMIN", "p-2": "LABS", "p-3": "ADMIN" },
  4: { "p-1": "LABS", "p-2": "LABS", "p-3": "ADMIN" },
  5: { "p-1": "LABS", "p-2": "ADMIN", "p-3": "ADMIN" },
};
const VENTING: Record<number, string[]> = { 3: ["p-2"], 4: ["p-2"] };
const EVENTS: Record<number, TickEventView[]> = {
  2: [{ type: "kill", tick: 2, killer_id: "p-2", victim_id: "p-4", room_id: "LABS" }],
  5: [{ type: "report_body", tick: 5, reporter_id: "p-1", body_of: "p-4", room_id: "LABS" }],
};

function frame(tick: number): TickView {
  const places = PLACES[tick] ?? {};
  const states: AgentTickStateView[] = players.map((player) => ({
    agent_id: player.agent_id,
    room_id: places[player.agent_id] ?? null,
    is_alive: places[player.agent_id] !== undefined,
    is_venting: (VENTING[tick] ?? []).includes(player.agent_id),
    task_progress: null,
    current_action: "IDLE",
    visibility: null,
  }));
  return {
    tick,
    agent_states: states,
    events: EVENTS[tick] ?? [],
    sabotage_active: [],
    tasks_completed_total: 0,
    tasks_required_total: 0,
    bodies: [],
    sabotage: null,
    advantage: { crew_alive: 2, impostors_alive: 1, tasks_completed: 0, tasks_required: 0, tasks_required_total: 0, advantage: 0 },
    meeting_resolution: null,
  };
}

function turn(index: number, speaker: string, kind: TurnView["turn_kind"], accuses: string): TurnView {
  return {
    turn_id: `planted:meeting-0:turn-${index}`,
    turn_index: index,
    speaker,
    turn_kind: kind,
    reply_to: null,
    observations: [],
    claims: [{ type: "accusation", against: accuses, confidence: 0.7, reason: "" }],
    free_text: "",
    annotations: [],
    fabricated_opening: false,
  };
}

// p-1 reports p-4's body and accuses p-2; p-2 and p-3 accuse p-1 back, and p-1
// never speaks again.
const MEETING: MeetingDTO = {
  meeting_id: "planted:meeting-0",
  tick: 5,
  triggered_by: "p-1",
  trigger_kind: "body",
  outcome: "SKIPPED",
  ejected_player_id: null,
  turns: [turn(0, "p-1", "opening", "p-2"), turn(1, "p-2", "reply", "p-1"), turn(2, "p-3", "opt_in", "p-1")],
  ballots: [],
  contradictions: [],
  llm_calls: [],
  prompt_versions: {},
  total_cost_usd: 0,
  gate: { leader: null, leader_max_confidence: 0, threshold: 0.6, passed: false },
};

function replay(meeting: MeetingDTO, ticks: TickView[] = [0, 1, 2, 3, 4, 5].map(frame)): Replay {
  return {
    players,
    meetings: [meeting],
    ticks,
    map: { rooms: [room("ADMIN", "Admin"), room("LABS", "Labs")], vents: [], edges: [] },
    metadata: {
      game_id: "planted",
      seed: 0,
      total_ticks: 5,
      winner: null,
      winner_reason: null,
      meeting_count: 1,
      total_cost_usd: 0,
      prompt_versions: {},
      created_at: null,
      experiment_config: null,
    },
  };
}

function render(perspective: Perspective, meeting: MeetingDTO = MEETING, ticks?: TickView[]): string {
  state.perspective = perspective;
  state.currentReplay = replay(meeting, ticks);
  return renderToStaticMarkup(<MeetingView />);
}

/** Every mark the record leaves in the DOM: its attributes and its wording. */
const ENGINE_RECORD_MARKS = [
  MEETING_COPY.engineRecordHeading,
  "killed at tick",
  "really was",
  "speak again",
  "spoke again",
  "inside a vent in",
] as const;

function assertNoEngineRecord(html: string): void {
  const found = ENGINE_RECORD_MARKS.filter((mark) => html.includes(mark));
  if (found.length > 0) {
    throw new Error(`the omniscient record reached this render: ${found.join(", ")}`);
  }
}

describe("the omniscient meeting record", () => {
  it("states the corpse's age, the reply and each accused player's true route", () => {
    const html = render({ mode: "omniscient" });
    expect(html).toContain('aria-label="Where everyone really was"');
    expect(html).toContain(">Where everyone really was</h3>");
    expect(html).toContain("Shown in the omniscient view only, and read from the recording itself.");
    expect(html).toContain(
      "These are the map&#x27;s ticks; a player&#x27;s own account of the same moment is stamped one tick later.",
    );
    expect(html).toContain("The reported body is p-4&#x27;s, killed at tick 2, 3 ticks before this meeting.");
    expect(html).toContain("p-1 opened this meeting and was accused by p-2, but did not speak again.");
    expect(html).toContain("Where each accused player really was, from tick 0 to this meeting.");
    expect(html).toContain("p-2</span>: Labs, ticks 0–2 → inside a vent in Labs, ticks 3–4 → Admin, tick 5");
    expect(html).toContain("p-1</span>: Admin, ticks 0–3 → Labs, ticks 4–5");
  });

  it.each(players.map((player) => player.agent_id))("is absent from the DOM under %s's lens", (agentId) => {
    const html = render({ mode: "agent", agentId });
    expect(html).toContain("Resolution");
    assertNoEngineRecord(html);
  });

  it("is caught by the same check when it does render", () => {
    // Planted: the helper the agent lens passes, applied to the omniscient render.
    expect(() => assertNoEngineRecord(render({ mode: "omniscient" }))).toThrow(/omniscient record reached/);
  });

  it("drops the no-reply note once the opener answers", () => {
    const answered: MeetingDTO = { ...MEETING, turns: [...MEETING.turns, turn(3, "p-1", "reply", "p-3")] };
    const html = render({ mode: "omniscient" }, answered);
    expect(html).not.toContain("did not speak again");
    expect(html).toContain("p-1 opened this meeting, was accused by p-2, and spoke again afterwards.");
    expect(render({ mode: "omniscient" })).toContain("did not speak again");
  });

  it("names whoever opened and whoever accused them", () => {
    // Another opener and accuser than the planted meeting's, so the note reads
    // them off the meeting rather than off a fixed pair.
    const other: MeetingDTO = {
      ...MEETING,
      triggered_by: "p-3",
      trigger_kind: "emergency",
      turns: [turn(0, "p-3", "opening", "p-2"), turn(1, "p-1", "reply", "p-3")],
    };
    const html = render({ mode: "omniscient" }, other);
    expect(html).toContain("p-3 opened this meeting and was accused by p-1, but did not speak again.");
  });

  it("names one tick in the singular", () => {
    const fresh: TickView[] = [0, 1, 2, 3, 4, 5].map(frame).map((item) =>
      item.tick === 2
        ? { ...item, events: [] }
        : item.tick === 4
          ? { ...item, events: [{ type: "kill", tick: 4, killer_id: "p-2", victim_id: "p-4", room_id: "LABS" }] }
          : item,
    );
    expect(render({ mode: "omniscient" }, MEETING, fresh)).toContain(
      "The reported body is p-4&#x27;s, killed at tick 4, one tick before this meeting.",
    );
  });

  it("reads the victim, the kill tick and the age off the recording, in both forms", () => {
    // Another victim than the planted meeting's p-4, killed at other ticks before
    // other meetings, so each argument of the corpse line is read off this
    // recording rather than off the planted one: p-3 dies in Admin at tick 0
    // and is reported at tick 5 (age 5), then dies at tick 2 and is reported at
    // tick 3 (age 1). p-3 takes no turn here, and p-4 lives.
    const reported = (killTick: number, meetingTick: number): string => {
      const meeting: MeetingDTO = { ...MEETING, tick: meetingTick, turns: MEETING.turns.slice(0, 2) };
      const ticks: TickView[] = [0, 1, 2, 3, 4, 5]
        .filter((tick) => tick <= meetingTick)
        .map(frame)
        .map((item) => ({
          ...item,
          agent_states: item.agent_states.map((agent) =>
            agent.agent_id === "p-3" && item.tick >= killTick
              ? { ...agent, room_id: null, is_alive: false }
              : agent.agent_id === "p-4"
                ? { ...agent, room_id: "LABS", is_alive: true }
                : agent,
          ),
          events:
            item.tick === killTick
              ? [{ type: "kill", tick: killTick, killer_id: "p-2", victim_id: "p-3", room_id: "ADMIN" }]
              : item.tick === meetingTick
                ? [{ type: "report_body", tick: meetingTick, reporter_id: "p-1", body_of: "p-3", room_id: "ADMIN" }]
                : [],
        }));
      return render({ mode: "omniscient" }, meeting, ticks);
    };
    const plural = reported(0, 5);
    expect(plural).toContain("The reported body is p-3&#x27;s, killed at tick 0, 5 ticks before this meeting.");
    expect(plural).not.toContain("p-4&#x27;s");
    const singular = reported(2, 3);
    expect(singular).toContain("The reported body is p-3&#x27;s, killed at tick 2, one tick before this meeting.");
    expect(singular).not.toContain("p-4&#x27;s");
  });

  it("names the room of each vent leg off the recording", () => {
    // p-2 is inside a vent in Labs at ticks 3-4 (the planted meeting), and here
    // still inside one at tick 5, when the frames put it in Admin.
    const ticks = [0, 1, 2, 3, 4, 5].map(frame).map((item) =>
      item.tick === 5
        ? {
            ...item,
            agent_states: item.agent_states.map((agent) =>
              agent.agent_id === "p-2" ? { ...agent, is_venting: true } : agent,
            ),
          }
        : item,
    );
    expect(render({ mode: "omniscient" }, MEETING, ticks)).toContain(
      "p-2</span>: Labs, ticks 0–2 → inside a vent in Labs, ticks 3–4 → inside a vent in Admin, tick 5",
    );
  });

  it("has nothing to read on a meeting fixture with no frames", () => {
    assertNoEngineRecord(render({ mode: "omniscient" }, MEETING, []));
  });

  it("lists no route when no one is accused, and no reply when the opener is not", () => {
    const quiet: MeetingDTO = {
      ...MEETING,
      trigger_kind: "emergency",
      turns: MEETING.turns.map((item) => ({ ...item, claims: [] })),
    };
    const html = render({ mode: "omniscient" }, quiet);
    expect(html).toContain("Where everyone really was");
    // The heading says "really was" too, so the route lead is matched by its own words.
    expect(html).not.toContain("accused player really was");
    expect(html).not.toContain("speak again");
    expect(html).not.toContain("killed at tick");
  });

  it("opens the routes after the last regroup on a recording that regroups", () => {
    // A first meeting at tick 2, then this one at 5: under hub_with_grace the
    // routes start on tick 3, the frame after the regroup.
    const earlier: MeetingDTO = { ...MEETING, meeting_id: "planted:meeting-prior", tick: 2, trigger_kind: "emergency", turns: [] };
    state.perspective = { mode: "omniscient" };
    const base = replay(MEETING);
    state.currentReplay = {
      ...base,
      meetings: [earlier, MEETING],
      metadata: { ...base.metadata, experiment_config: { ...CONFIG, meeting_reset: "hub_with_grace" } },
    };
    const html = renderToStaticMarkup(<MeetingView />);
    expect(html).toContain("Where each accused player really was, from tick 3 to this meeting.");
    expect(html).toContain("p-1</span>: Admin, tick 3 → Labs, ticks 4–5");
  });

  it("raises on a route through a room the map does not carry", () => {
    state.perspective = { mode: "omniscient" };
    state.currentReplay = { ...replay(MEETING), map: { rooms: [room("ADMIN", "Admin")], vents: [], edges: [] } };
    expect(() => renderToStaticMarkup(<MeetingView />)).toThrow(/no room LABS/);
  });
});

// ── the meeting's words ──────────────────────────────────────────────────────

/** Markup as text: tags and React's text-joining comments dropped. */
function textOf(html: string): string {
  return html.replace(/<!--[\s\S]*?-->/g, "").replace(/<[^>]*>/g, "").replaceAll("&#x27;", "'");
}

/** The planted meeting with `player` voted out on one confident ballot. */
function ejected(player: string): MeetingDTO {
  return {
    ...MEETING,
    outcome: "EJECTED",
    ejected_player_id: player,
    gate: { leader: player, leader_max_confidence: 0.8, threshold: 0.6, passed: true },
  };
}

const LENSES: readonly Perspective[] = players.map((player) => ({ mode: "agent", agentId: player.agent_id }));

/** The role line's text, or null when the render carries none. */
function roleLineOf(html: string): string | null {
  const match = /<div data-role-line="true"[^>]*>([\s\S]*?)<\/div>/.exec(html);
  return match === null ? null : textOf(match[1] ?? "");
}

describe("the ejected player's role line", () => {
  it.each([
    ["p-2", "p-2 was an impostor"],
    ["p-3", "p-3 was a crewmate"],
  ])("names %s's real role in plain words, all-roles view only", (player, words) => {
    const html = render({ mode: "omniscient" }, ejected(player));
    expect(roleLineOf(html)).toBe(`⌖${words}`);
    expect(html).not.toContain("post-hoc");
    for (const lens of LENSES) {
      const fogged = render(lens, ejected(player));
      expect(roleLineOf(fogged)).toBeNull();
      expect(fogged).not.toContain(words);
    }
  });

  it("shows no role line when no one was ejected", () => {
    expect(roleLineOf(render({ mode: "omniscient" }))).toBeNull();
  });
});

describe("the vote readout", () => {
  it.each([
    ["a passed vote", ejected("p-2"), "Most votes went to p-2 and a voter was sure enough, so p-2 was ejected."],
    [
      "a vote no one was sure enough of",
      { ...MEETING, gate: { leader: "p-2", leader_max_confidence: 0.4, threshold: 0.6, passed: false } },
      "Most votes went to p-2, but none of those voters was sure enough, so no one was ejected.",
    ],
    ["a tie or a skip lead", MEETING, "No single player got the most votes (a tie, or skip led), so no one was ejected."],
  ])("says why for %s, the same under every perspective", (_name, meeting, sentence) => {
    for (const perspective of [{ mode: "omniscient" } as Perspective, ...LENSES]) {
      const readout = /<p data-vote-readout="true"[^>]*>([\s\S]*?)<\/p>/.exec(render(perspective, meeting))?.[1];
      expect(textOf(readout ?? "")).toBe(`${MEETING_COPY.resolutionGateLead}: ${sentence}`);
    }
  });
});

describe("the accusation chain", () => {
  it("captions the arrows plainly and has every turn accuse, a reply included", () => {
    const html = render({ mode: "omniscient" });
    expect(textOf(html)).toContain("Arrows point from accuser to accused");
    const verbs = [...html.matchAll(/text-ink-900">(accuses|redirects)<\/span><svg/g)].map((match) => match[1]);
    // The planted meeting's three turns: an opening, a reply and a speak-up.
    expect(verbs).toEqual(["accuses", "accuses", "accuses"]);
    expect(html).not.toMatch(/distrust orange|who points at whom|guilt is never|role-neutral/);
  });
});

describe("the turn tag", () => {
  it("reads each kind of turn by name, with its tick in words", () => {
    const tags = [...render({ mode: "omniscient" }).matchAll(/text-ink-500">(tick \d+ · [^<]+)<\/span>/g)].map((match) => match[1]);
    expect(tags).toEqual(["tick 5 · first statement", "tick 5 · reply", "tick 5 · spoke up"]);
  });
});

describe("the evidence list", () => {
  const flag = (id: string, category: ContradictionView["category"], a: string, b: string): ContradictionView => ({
    contradiction_id: id,
    kind: category === "role_proof" ? "vent_sighting" : "alibi_conflict",
    event_a_id: a,
    event_b_id: b,
    subjects: ["p-2"],
    description: "",
    weak: category === "weak_signal",
    severity: category === "weak_signal" ? "weak" : "strong",
    category,
  });
  const claimOf = (turnIndex: number) => `turn:planted:meeting-0:turn-${String(turnIndex)}:claim:0`;
  const flagged: MeetingDTO = {
    ...MEETING,
    contradictions: [
      flag("proof", "role_proof", claimOf(0), claimOf(0)),
      flag("conflict", "cross_statement", claimOf(0), claimOf(1)),
      flag("weak", "weak_signal", claimOf(2), "turn:planted:meeting-0:turn-2:whereabouts:0"),
    ],
  };

  it("says in each caption what its group holds, with no detector words", () => {
    const text = textOf(render({ mode: "omniscient" }, flagged));
    // The evidence list alone: the record beside it says "stamped" of the clock.
    const list = text.slice(text.indexOf("Evidence (3)"), text.indexOf("Ballots ("));
    expect(list).toContain("Evidence (3)");
    for (const group of Object.values(MEETING_COPY.evidenceGroups)) {
      expect(list).toContain(`${group.heading} (1)`);
      expect(list).toContain(group.caption);
    }
    expect(list).not.toMatch(/grounded|detector|stamped|endpoint tick/);
  });

  it("names each source by its speaker and kind of turn", () => {
    const text = textOf(render({ mode: "omniscient" }, flagged));
    expect(text).toContain("from p-1 (first statement)");
    expect(text).toContain("p-1 (first statement) ↔ p-2 (reply)");
    expect(text).toContain("within p-3 (spoke up)");
    expect(text).toContain("Source 1 · p-1 (first statement)");
    expect(text).not.toMatch(/\((?:opening|opt-in)\)/);
  });
});
