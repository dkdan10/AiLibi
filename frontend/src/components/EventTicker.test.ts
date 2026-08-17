// Unit tests for the ticker's perspective projection (Task 19.17).
//
// THE FOUR FOG CASES ARE THE POINT. The served event views are privileged —
// `KillEventView` carries `killer_id` unconditionally, `VentEventView` carries
// the actor and both ends of the route — so the projection, not the DTO, is what
// keeps the As-agent view honest. Each case below is a fixture where the SAME
// bytes are read twice, once Omniscient and once in fog, and the difference is
// asserted in both directions: the fog must withhold what it did not witness AND
// still surface what it did.
//
// A renderer is deliberately not involved. The vitest baseline Task 19.12 landed
// runs `environment: "node"`, and the thing worth pinning here is a pure
// function of the view-model, so it is tested as one; the browser-only facts
// (that the section mounts, that entering fog does not grow the feed) live in
// the Playwright journey.

import { describe, expect, it } from "vitest";

import { OMNISCIENT, START_TICK } from "../lib/playback";
import type { Perspective } from "../lib/playback";
import type {
  AdvantageView,
  AgentTickStateView,
  AgentVisibilityView,
  MeetingView,
  TickEventView,
  TickView,
  VisibleBodyView,
  VisiblePlayerView,
} from "../types/api";
import { projectTicker } from "./EventTicker";

// ── fixtures ─────────────────────────────────────────────────────────────────

const ADVANTAGE: AdvantageView = {
  crew_alive: 7,
  impostors_alive: 2,
  tasks_completed: 3,
  tasks_required: 10,
  tasks_required_total: 12,
  advantage: 0.25,
};

/** The observer every fog case is written from. */
const WATCHER = "p-0";
const AS_WATCHER: Perspective = { mode: "agent", agentId: WATCHER };

function visibility(
  players: VisiblePlayerView[] = [],
  bodies: VisibleBodyView[] = [],
): AgentVisibilityView {
  return {
    visible_players: players,
    visible_bodies: bodies,
    audible_events: [],
  };
}

/**
 * The watcher's own per-tick state. `alive: false` or `vis: null` is the
 * no-field-of-view case the map's `fogNoView` also honours.
 */
function watcherState(
  vis: AgentVisibilityView | null,
  alive = true,
): AgentTickStateView {
  return {
    agent_id: WATCHER,
    room_id: "CAFETERIA",
    is_alive: alive,
    is_venting: false,
    task_progress: null,
    current_action: "IDLE",
    visibility: vis,
  };
}

function frame(
  tick: number,
  events: TickEventView[] = [],
  states: AgentTickStateView[] = [],
): TickView {
  return {
    tick,
    agent_states: states,
    events,
    sabotage_active: [],
    tasks_completed_total: 0,
    tasks_required_total: 12,
    bodies: [],
    sabotage: null,
    advantage: ADVANTAGE,
    meeting_resolution: null,
  };
}

function kill(tick: number, killer = "p-3", victim = "p-5"): TickEventView {
  return { type: "kill", tick, killer_id: killer, victim_id: victim, room_id: "REACTOR" };
}

// The ENTER event's `to_room_id` EQUALS its `from_room_id` — this is the real
// byte shape, verified against every traversal in the committed 9p2i sets
// (e.g. seed 2: `t9 enter from=STORAGE to=STORAGE`, `t10 exit from=STORAGE
// to=ENGINEERING`). The destination is not resolved at dive time. A fixture that
// put the destination on the enter event would be fiction, and it would hide
// exactly the defect these tests exist to prevent: a route rendered off the
// enter event reads `STORAGE → STORAGE`.
function vent(tick: number, actor = "p-3"): TickEventView {
  return {
    type: "vent",
    tick,
    actor_id: actor,
    phase: "enter",
    from_room_id: "REACTOR",
    to_room_id: "REACTOR",
    traversal_ticks: 3,
  };
}

function ventExit(tick: number, actor = "p-3"): TickEventView {
  return {
    type: "vent",
    tick,
    actor_id: actor,
    phase: "exit",
    from_room_id: "REACTOR",
    to_room_id: "ELECTRICAL",
    traversal_ticks: 3,
  };
}

function meetingTriggered(tick: number, by = "p-1"): TickEventView {
  return {
    type: "meeting_triggered",
    tick,
    meeting_id: `m-${tick}`,
    triggered_by: by,
    trigger_kind: "body",
  };
}

function reportBody(tick: number, reporter = "p-1", victim = "p-5"): TickEventView {
  return { type: "report_body", tick, reporter_id: reporter, body_of: victim, room_id: "REACTOR" };
}

function taskCompleted(tick: number): TickEventView {
  return { type: "task_completed", tick, agent_id: "p-2", task_id: "t-1", room_id: "ADMIN" };
}

function sabotage(tick: number, actor = "p-3"): TickEventView {
  return { type: "sabotage", tick, kind: "lights", room_id: null, actor_id: actor };
}

function meeting(
  tick: number,
  outcome: MeetingView["outcome"] = "EJECTED",
  ejected: string | null = "p-4",
): MeetingView {
  return {
    meeting_id: `m-${tick}`,
    tick,
    triggered_by: "p-1",
    trigger_kind: "body",
    outcome,
    ejected_player_id: outcome === "EJECTED" ? ejected : null,
    turns: [],
    ballots: [],
    contradictions: [],
    llm_calls: [],
    prompt_versions: {},
    total_cost_usd: 0,
    gate: { leader: "p-4", leader_max_confidence: 0.8, threshold: 0.6, passed: true },
  };
}

const NO_MEETINGS: readonly MeetingView[] = [];

/** Every rendered line, joined — the DOM text the projection would produce. */
function lines(entries: ReturnType<typeof projectTicker>): string {
  return entries.map((entry) => entry.text).join("\n");
}

// ── fog case 1 + 2: kills ────────────────────────────────────────────────────

describe("kills through the As-agent projection", () => {
  // p-3 kills p-5 at tick 4; the watcher is among the engine's witnesses, so the
  // loader stamped `action: "kill"` on the sighting. The body is co-visible.
  const WITNESSED: readonly TickView[] = [
    frame(START_TICK, [], [watcherState(visibility())]),
    frame(
      4,
      [kill(4)],
      [
        watcherState(
          visibility(
            [{ id: "p-3", room: "REACTOR", action: "kill" }],
            [{ id: "b-1", room: "REACTOR", victim_id: "p-5" }],
          ),
        ),
      ],
    ),
  ];

  // The same kill, unwitnessed: the watcher sees an unrelated player elsewhere
  // at the kill tick, then walks into REACTOR at tick 9 and finds the body.
  const UNWITNESSED: readonly TickView[] = [
    frame(START_TICK, [], [watcherState(visibility())]),
    frame(
      4,
      [kill(4)],
      [watcherState(visibility([{ id: "p-2", room: "ADMIN", action: null }]))],
    ),
    frame(9, [], [watcherState(visibility([], [{ id: "b-1", room: "REACTOR", victim_id: "p-5" }]))]),
  ];

  it("WITNESSED: surfaces the attribution, with the room the fog projected", () => {
    const entries = projectTicker(WITNESSED, NO_MEETINGS, 1, AS_WATCHER);
    expect(entries.map((entry) => entry.kind)).toEqual(["kill"]);
    expect(lines(entries)).toBe("p-3 killed p-5 · REACTOR");
  });

  it("WITNESSED: does not ALSO report the body it just watched being made", () => {
    // The body is in `visible_bodies` on the same tick; one death is one beat.
    const kinds = projectTicker(WITNESSED, NO_MEETINGS, 1, AS_WATCHER).map((e) => e.kind);
    expect(kinds).not.toContain("body");
  });

  it("UNWITNESSED: never attributes — not the killer, not at any later frame", () => {
    for (let index = 0; index < UNWITNESSED.length; index++) {
      const text = lines(projectTicker(UNWITNESSED, NO_MEETINGS, index, AS_WATCHER));
      expect(text).not.toContain("p-3");
      expect(text).not.toContain("killed");
    }
  });

  it("UNWITNESSED: surfaces as a body discovery when the body enters view", () => {
    // At the kill tick: nothing at all — the death has not reached this agent.
    expect(projectTicker(UNWITNESSED, NO_MEETINGS, 1, AS_WATCHER)).toEqual([]);
    // Five ticks later it walks in on the body.
    const entries = projectTicker(UNWITNESSED, NO_MEETINGS, 2, AS_WATCHER);
    expect(entries.map((entry) => entry.kind)).toEqual(["body"]);
    expect(lines(entries)).toBe("Found p-5's body · REACTOR");
    expect(entries[0]?.tick).toBe(9);
  });

  it("UNWITNESSED: reports one discovery, not one per tick the body stays in view", () => {
    const stillThere = [
      ...UNWITNESSED,
      frame(10, [], [watcherState(visibility([], [{ id: "b-1", room: "REACTOR", victim_id: "p-5" }]))]),
      frame(11, [], [watcherState(visibility([], [{ id: "b-1", room: "REACTOR", victim_id: "p-5" }]))]),
    ];
    const kinds = projectTicker(stillThere, NO_MEETINGS, 4, AS_WATCHER).map((e) => e.kind);
    expect(kinds.filter((kind) => kind === "body")).toHaveLength(1);
  });

  it("OMNISCIENT: the same bytes carry the privileged attribution", () => {
    expect(lines(projectTicker(UNWITNESSED, NO_MEETINGS, 2, OMNISCIENT))).toBe(
      "p-3 killed p-5 · REACTOR",
    );
    // …and no body discovery: that construct exists only inside the fog.
    const kinds = projectTicker(UNWITNESSED, NO_MEETINGS, 2, OMNISCIENT).map((e) => e.kind);
    expect(kinds).toEqual(["kill"]);
  });

  it("an agent with no field of view (dead / absent) sees no kill at all", () => {
    const dead: readonly TickView[] = [
      frame(START_TICK, [], [watcherState(visibility())]),
      frame(4, [kill(4)], [watcherState(visibility([{ id: "p-3", room: "REACTOR", action: "kill" }]), false)]),
      frame(5, [kill(5, "p-3", "p-6")], []),
    ];
    expect(projectTicker(dead, NO_MEETINGS, 2, AS_WATCHER)).toEqual([]);
    expect(projectTicker(dead, NO_MEETINGS, 2, OMNISCIENT)).toHaveLength(2);
  });
});

// ── fog case 3 + 4: vents ────────────────────────────────────────────────────

describe("vents through the As-agent projection", () => {
  // Witnessed at the SOURCE mouth only: the watcher sees p-3 dive at REACTOR and
  // is nowhere near ELECTRICAL when it comes out.
  const WITNESSED: readonly TickView[] = [
    frame(START_TICK, [], [watcherState(visibility())]),
    frame(
      6,
      [vent(6)],
      [watcherState(visibility([{ id: "p-3", room: "REACTOR", action: "vent" }]))],
    ),
    // The far end of the same traversal, which this agent did NOT see.
    frame(9, [ventExit(9)], [watcherState(visibility())]),
  ];

  // The mirror image: the watcher misses the dive and witnesses only the
  // EMERGENCE. Both vent events carry `source_witnesses` AND
  // `destination_witnesses`, so this is a real packet the projection must honour.
  const WITNESSED_EMERGENCE: readonly TickView[] = [
    frame(START_TICK, [], [watcherState(visibility())]),
    frame(6, [vent(6)], [watcherState(visibility())]),
    frame(
      9,
      [ventExit(9)],
      [watcherState(visibility([{ id: "p-3", room: "ELECTRICAL", action: "vent" }]))],
    ),
  ];

  const UNWITNESSED: readonly TickView[] = [
    frame(START_TICK, [], [watcherState(visibility())]),
    frame(
      6,
      [vent(6)],
      // Co-located with somebody else entirely; the vent is not in this packet.
      [watcherState(visibility([{ id: "p-2", room: "ADMIN", action: null }]))],
    ),
    frame(9, [ventExit(9)], [watcherState(visibility())]),
  ];

  it("WITNESSED: names the actor and the ONE endpoint seen — never the route", () => {
    const entries = projectTicker(WITNESSED, NO_MEETINGS, 2, AS_WATCHER);
    expect(entries.map((entry) => entry.kind)).toEqual(["vent"]);
    expect(lines(entries)).toBe("p-3 used a vent · REACTOR");
    // The destination is the privileged half: a witness at one mouth of the
    // network did not see where the actor came out.
    expect(lines(entries)).not.toContain("ELECTRICAL");
    expect(lines(entries)).not.toContain("→");
  });

  it("WITNESSED at the EXIT: an emergence-only witness still gets its beat", () => {
    const entries = projectTicker(WITNESSED_EMERGENCE, NO_MEETINGS, 2, AS_WATCHER);
    expect(entries.map((entry) => entry.kind)).toEqual(["vent"]);
    expect(entries[0]?.tick).toBe(9);
    expect(lines(entries)).toBe("p-3 used a vent · ELECTRICAL");
    // Still no route: this observer saw a player come OUT of a vent, not where
    // they went in.
    expect(lines(entries)).not.toContain("REACTOR");
    expect(lines(entries)).not.toContain("→");
  });

  it("UNWITNESSED: does not surface at all, through any channel", () => {
    for (let index = 0; index < UNWITNESSED.length; index++) {
      expect(projectTicker(UNWITNESSED, NO_MEETINGS, index, AS_WATCHER)).toEqual([]);
    }
  });

  it("OMNISCIENT: the route comes off the EXIT event, never the dive", () => {
    // The dive knows only where it started — its own `to_room_id` is the source
    // repeated, so a route printed here would read `REACTOR → REACTOR`.
    expect(lines(projectTicker(UNWITNESSED, NO_MEETINGS, 1, OMNISCIENT))).toBe(
      "p-3 entered a vent · REACTOR",
    );
    expect(lines(projectTicker(UNWITNESSED, NO_MEETINGS, 1, OMNISCIENT))).not.toContain("→");
    // The emergence is where the destination becomes known.
    expect(lines(projectTicker(UNWITNESSED, NO_MEETINGS, 2, OMNISCIENT))).toBe(
      ["p-3 entered a vent · REACTOR", "p-3 emerged from a vent · REACTOR → ELECTRICAL"].join(
        "\n",
      ),
    );
  });

  it("never prints a same-room route from the dive event's duplicated field", () => {
    for (let index = 0; index < UNWITNESSED.length; index++) {
      expect(lines(projectTicker(UNWITNESSED, NO_MEETINGS, index, OMNISCIENT))).not.toContain(
        "REACTOR → REACTOR",
      );
    }
  });

  it("emits both phases as beats — a dive and an emergence are different moments", () => {
    const kinds = projectTicker(UNWITNESSED, NO_MEETINGS, 2, OMNISCIENT).map((e) => e.kind);
    expect(kinds.filter((kind) => kind === "vent")).toHaveLength(2);
  });

  it("a dive with no recorded emergence yields the dive alone", () => {
    // The actor was ejected or killed mid-traversal — `buildVentSegments` has a
    // pending-dive fallback for the same shape. Per-event projection needs no
    // pairing state, so this is simply one beat.
    const stranded: readonly TickView[] = [
      frame(START_TICK, [], [watcherState(visibility())]),
      frame(6, [vent(6)], [watcherState(visibility())]),
    ];
    expect(lines(projectTicker(stranded, NO_MEETINGS, 1, OMNISCIENT))).toBe(
      "p-3 entered a vent · REACTOR",
    );
  });
});

// ── the selected agent's OWN actions ─────────────────────────────────────────

describe("the fog agent's own actions", () => {
  // The engine excludes an actor from its own kill's / vent's witness sets
  // (`engine/rules.py`), so `visible_players` can never carry them — yet these
  // are the acts the agent knows best. The map already renders them for the self
  // token under fog via `selfActionGlyph(current_action)`.
  const OWN_KILL: readonly TickView[] = [
    frame(START_TICK, [], [watcherState(visibility())]),
    frame(
      4,
      [kill(4, WATCHER, "p-5")],
      // The watcher IS the killer, so nothing witness-gated names it — and the
      // body is right there in its own field of view.
      [watcherState(visibility([], [{ id: "b-1", room: "REACTOR", victim_id: "p-5" }]))],
    ),
  ];

  it("renders its own kill instead of dropping it", () => {
    const entries = projectTicker(OWN_KILL, NO_MEETINGS, 1, AS_WATCHER);
    expect(entries.map((entry) => entry.kind)).toEqual(["kill"]);
    expect(lines(entries)).toBe(`${WATCHER} killed p-5 · REACTOR`);
  });

  it("does not then report its own victim as a body it stumbled upon", () => {
    // The regression this branch exists for: with the kill suppressed, the body
    // pass told an impostor it had "found" a body it made itself.
    const kinds = projectTicker(OWN_KILL, NO_MEETINGS, 1, AS_WATCHER).map((e) => e.kind);
    expect(kinds).not.toContain("body");
  });

  it("renders its own vent at the endpoint it was at — and still no route", () => {
    const ownVent: readonly TickView[] = [
      frame(START_TICK, [], [watcherState(visibility())]),
      frame(6, [vent(6, WATCHER)], [watcherState(visibility())]),
      frame(9, [ventExit(9, WATCHER)], [watcherState(visibility())]),
    ];
    const entries = projectTicker(ownVent, NO_MEETINGS, 2, AS_WATCHER);
    expect(lines(entries)).toBe(
      [
        `${WATCHER} entered a vent · REACTOR`,
        `${WATCHER} emerged from a vent · ELECTRICAL`,
      ].join("\n"),
    );
    // The invariant the browser journey asserts for ANY agent holds here too:
    // no vent route survives the fog, impostors included.
    expect(lines(entries)).not.toContain("→");
  });

  it("still hides OTHER agents' unwitnessed acts from the same agent", () => {
    // The self branch is a carve-out for one actor, not a hole in the gate.
    const mixed: readonly TickView[] = [
      frame(START_TICK, [], [watcherState(visibility())]),
      frame(4, [kill(4, WATCHER, "p-5"), kill(4, "p-8", "p-6")], [watcherState(visibility())]),
    ];
    const text = lines(projectTicker(mixed, NO_MEETINGS, 1, AS_WATCHER));
    expect(text).toBe(`${WATCHER} killed p-5 · REACTOR`);
    expect(text).not.toContain("p-8");
  });
});

// ── the public beats ─────────────────────────────────────────────────────────

describe("public beats", () => {
  const TICKS: readonly TickView[] = [
    frame(START_TICK, [], [watcherState(visibility())]),
    frame(
      7,
      [meetingTriggered(7), reportBody(7)],
      // The watcher perceives nothing this tick — the beats below are still its
      // business, because the table states them in the clear.
      [watcherState(visibility())],
    ),
  ];

  it("a report, the meeting it opens, and how the vote resolved show in BOTH modes", () => {
    const omniscient = projectTicker(TICKS, [meeting(7)], 1, OMNISCIENT);
    const fogged = projectTicker(TICKS, [meeting(7)], 1, AS_WATCHER);
    const expected = [
      "Meeting called by p-1 · body",
      "p-1 reported p-5's body · REACTOR",
      "p-4 ejected by the vote",
    ].join("\n");
    expect(lines(omniscient)).toBe(expected);
    expect(lines(fogged)).toBe(expected);
  });

  it("a body's public report accounts it — the same discovery is not narrated twice", () => {
    // The loader deliberately reopens the reported body in `visible_bodies` for
    // co-located agents on the report tick, so without accounting the victim the
    // feed reads "p-1 reported p-5's body" then "Found p-5's body" on one frame.
    // Real on committed bytes: 9p2i seed 1, tick 8, for p-1 and p-6.
    const reportTick: readonly TickView[] = [
      frame(START_TICK, [], [watcherState(visibility())]),
      frame(
        7,
        [meetingTriggered(7), reportBody(7)],
        [watcherState(visibility([], [{ id: "b-1", room: "REACTOR", victim_id: "p-5" }]))],
      ),
    ];
    const kinds = projectTicker(reportTick, NO_MEETINGS, 1, AS_WATCHER).map((e) => e.kind);
    expect(kinds).toEqual(["meeting", "report"]);
    expect(kinds).not.toContain("body");
  });

  it("a body reported earlier is not re-discovered on a later walk-past", () => {
    const later: readonly TickView[] = [
      frame(START_TICK, [], [watcherState(visibility())]),
      frame(7, [reportBody(7)], [watcherState(visibility())]),
      // The agent wanders into the room several ticks on; it already knows.
      frame(20, [], [watcherState(visibility([], [{ id: "b-1", room: "REACTOR", victim_id: "p-5" }]))]),
    ];
    const kinds = projectTicker(later, NO_MEETINGS, 2, AS_WATCHER).map((e) => e.kind);
    expect(kinds).toEqual(["report"]);
  });

  it("a skipped meeting says the vote resolved, never who was suspected", () => {
    const entries = projectTicker(TICKS, [meeting(7, "SKIPPED", null)], 1, AS_WATCHER);
    expect(lines(entries)).toContain("Vote resolved — no ejection");
  });

  it("leaves out task completions and sabotage (sabotage would name an impostor)", () => {
    const noisy: readonly TickView[] = [
      frame(START_TICK, [], [watcherState(visibility())]),
      frame(3, [taskCompleted(3), sabotage(3)], [watcherState(visibility())]),
    ];
    expect(projectTicker(noisy, NO_MEETINGS, 1, OMNISCIENT)).toEqual([]);
    expect(projectTicker(noisy, NO_MEETINGS, 1, AS_WATCHER)).toEqual([]);
  });
});

// ── frame-bounding (the unspoiled-mode rule) ─────────────────────────────────

describe("frame-bounding", () => {
  const TICKS: readonly TickView[] = [
    frame(START_TICK, [], [watcherState(visibility())]),
    frame(4, [kill(4)], [watcherState(visibility())]),
    frame(7, [meetingTriggered(7)], [watcherState(visibility())]),
    frame(30, [kill(30, "p-3", "p-8")], [watcherState(visibility())]),
  ];
  const MEETINGS = [meeting(7), meeting(30, "EJECTED", "p-3")];

  it("the Start frame carries nothing — the feed cannot open on a spoiler", () => {
    expect(projectTicker(TICKS, MEETINGS, 0, OMNISCIENT)).toEqual([]);
    expect(projectTicker(TICKS, MEETINGS, 0, AS_WATCHER)).toEqual([]);
  });

  it("never reads past the current frame, in either perspective", () => {
    for (const perspective of [OMNISCIENT, AS_WATCHER]) {
      const entries = projectTicker(TICKS, MEETINGS, 2, perspective);
      const text = lines(entries);
      expect(entries.every((entry) => entry.tick <= 7)).toBe(true);
      // The game's decisive last meeting is four frames away and stays there.
      expect(text).not.toContain("p-8");
      expect(text).not.toContain("p-3 ejected");
    }
  });

  it("grows monotonically as the playhead advances", () => {
    let previous = 0;
    for (let index = 0; index < TICKS.length; index++) {
      const count = projectTicker(TICKS, MEETINGS, index, OMNISCIENT).length;
      expect(count).toBeGreaterThanOrEqual(previous);
      previous = count;
    }
    expect(previous).toBeGreaterThan(0);
  });

  it("is position-derived: the same frame yields the same feed however reached", () => {
    // Walking forward one frame at a time and jumping straight there must agree
    // — the body-discovery de-duplication is what could have made this stateful.
    const direct = projectTicker(TICKS, MEETINGS, 3, AS_WATCHER);
    let walked = projectTicker(TICKS, MEETINGS, 0, AS_WATCHER);
    for (let index = 1; index <= 3; index++) {
      walked = projectTicker(TICKS, MEETINGS, index, AS_WATCHER);
    }
    expect(walked).toEqual(direct);
  });

  it("clamps an out-of-range index instead of reading past the timeline", () => {
    expect(projectTicker(TICKS, MEETINGS, 999, OMNISCIENT)).toEqual(
      projectTicker(TICKS, MEETINGS, TICKS.length - 1, OMNISCIENT),
    );
    expect(projectTicker(TICKS, MEETINGS, -5, OMNISCIENT)).toEqual([]);
  });

  it("yields nothing for an empty timeline", () => {
    expect(projectTicker([], MEETINGS, 3, OMNISCIENT)).toEqual([]);
  });

  it("the fog projection is a SUBSET of the omniscient one at every frame", () => {
    for (let index = 0; index < TICKS.length; index++) {
      const fogged = projectTicker(TICKS, MEETINGS, index, AS_WATCHER);
      const omniscient = projectTicker(TICKS, MEETINGS, index, OMNISCIENT);
      expect(fogged.length).toBeLessThanOrEqual(omniscient.length);
    }
  });

  it("gives every entry a distinct key, including several on one tick", () => {
    const busy: readonly TickView[] = [
      frame(START_TICK, [], [watcherState(visibility())]),
      frame(7, [meetingTriggered(7), reportBody(7), kill(7)], [watcherState(visibility())]),
    ];
    const keys = projectTicker(busy, [meeting(7)], 1, OMNISCIENT).map((entry) => entry.key);
    expect(new Set(keys).size).toBe(keys.length);
    expect(keys.length).toBe(4);
  });
});
