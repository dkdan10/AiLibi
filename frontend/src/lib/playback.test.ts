// Unit tests for the pure playback derivations (Task 19.12; the module is Task
// 12.4's, extended by 19.10). `lib/playback.ts` is the single home for the
// tick↔frame mapping and every navigation/seek computation — the recurring
// off-by-one it exists to kill lives in the gap between a frame's ARRAY INDEX
// and its ENGINE TICK NUMBER, and the loader's synthetic `tick = -1` Start frame
// is what opens that gap. So the mapping tests below always assert on a timeline
// whose indices and ticks disagree; a fixture where `ticks[i].tick === i` would
// pass with the bug in place.

import { describe, expect, it } from "vitest";

import type {
  AdvantageView,
  GameFinale,
  MeetingView,
  TickEventView,
  TickView,
} from "../types/api";
import {
  OMNISCIENT,
  START_TICK,
  advantageSeries,
  eventTickNumbers,
  finaleAtIndex,
  frameIndexForTick,
  isStartIndex,
  keyMoments,
  keyMomentTicks,
  meetingTickNumbers,
  meetingTickSet,
  nextAfter,
  parsePlaybackParams,
  prevBefore,
  serializePlaybackParams,
  shouldPauseAtMeeting,
  tickNumberAt,
  timelineMarkers,
} from "./playback";

// ── fixtures ─────────────────────────────────────────────────────────────────

const ADVANTAGE: AdvantageView = {
  crew_alive: 7,
  impostors_alive: 2,
  tasks_completed: 3,
  tasks_required: 10,
  tasks_required_total: 12,
  advantage: 0.25,
};

function frame(
  tick: number,
  events: TickEventView[] = [],
  advantage = 0,
): TickView {
  return {
    tick,
    agent_states: [],
    events,
    sabotage_active: [],
    tasks_completed_total: 0,
    tasks_required_total: 12,
    bodies: [],
    sabotage: null,
    advantage: { ...ADVANTAGE, advantage },
    meeting_resolution: null,
  };
}

function kill(tick: number, killer = "p-1", victim = "p-4"): TickEventView {
  return { type: "kill", tick, killer_id: killer, victim_id: victim, room_id: "CAFETERIA" };
}

function vent(tick: number, actor = "p-1"): TickEventView {
  return {
    type: "vent",
    tick,
    actor_id: actor,
    phase: "enter",
    from_room_id: "ELECTRICAL",
    to_room_id: "REACTOR",
    traversal_ticks: 3,
  };
}

function sabotage(tick: number, actor = "p-3"): TickEventView {
  return { type: "sabotage", tick, kind: "lights", room_id: null, actor_id: actor };
}

function meetingTriggered(
  tick: number,
  by = "p-2",
  meetingId = `m-${tick}`,
): TickEventView {
  return {
    type: "meeting_triggered",
    tick,
    meeting_id: meetingId,
    triggered_by: by,
    trigger_kind: "body",
  };
}

function taskCompleted(tick: number, agent = "p-5"): TickEventView {
  return { type: "task_completed", tick, agent_id: agent, task_id: "t-1", room_id: "ADMIN" };
}

function reportBody(tick: number, reporter = "p-6"): TickEventView {
  return { type: "report_body", tick, reporter_id: reporter, body_of: "p-4", room_id: "MEDBAY" };
}

function meeting(
  tick: number,
  outcome: MeetingView["outcome"] = "EJECTED",
  meetingId = `m-${tick}`,
): MeetingView {
  return {
    meeting_id: meetingId,
    tick,
    triggered_by: "p-2",
    trigger_kind: "body",
    outcome,
    ejected_player_id: outcome === "EJECTED" ? "p-4" : null,
    turns: [],
    ballots: [],
    contradictions: [],
    llm_calls: [],
    prompt_versions: {},
    total_cost_usd: 0,
    gate: { leader: "p-4", leader_max_confidence: 0.8, threshold: 0.6, passed: true },
  };
}

const FINALE: GameFinale = {
  winner: "CREWMATES",
  winner_reason: "CREWMATE_EJECT",
  final_tick: 90,
  decisive_events: [],
  agent_recaps: [],
};

// The canonical shape: a synthetic Start frame at engine tick -1, then real
// frames whose engine ticks are neither contiguous nor equal to their indices.
// index:  0    1   2   3   4    5
// tick:  -1    0  10  20  30   40
const TICKS: readonly TickView[] = [
  frame(START_TICK),
  frame(0),
  frame(10, [kill(10)], -0.2),
  frame(20, [meetingTriggered(20), taskCompleted(20)], 0.1),
  frame(30, [vent(30), sabotage(30)], 0.4),
  frame(40, [reportBody(40)], 0.9),
];

// ── the tick↔frame mapping ───────────────────────────────────────────────────

describe("tickNumberAt", () => {
  it("maps a frame index to its ENGINE tick, not its index", () => {
    expect(tickNumberAt(TICKS, 0)).toBe(START_TICK);
    expect(tickNumberAt(TICKS, 1)).toBe(0);
    expect(tickNumberAt(TICKS, 3)).toBe(20);
    expect(tickNumberAt(TICKS, 5)).toBe(40);
  });

  it("clamps an out-of-range index into the array rather than inventing a tick", () => {
    expect(tickNumberAt(TICKS, -7)).toBe(START_TICK);
    expect(tickNumberAt(TICKS, 999)).toBe(40);
  });

  it("yields the Start tick for an empty timeline", () => {
    expect(tickNumberAt([], 0)).toBe(START_TICK);
    expect(tickNumberAt([], 4)).toBe(START_TICK);
  });
});

describe("frameIndexForTick", () => {
  it("is the inverse of tickNumberAt on recorded ticks", () => {
    for (let index = 0; index < TICKS.length; index++) {
      expect(frameIndexForTick(TICKS, tickNumberAt(TICKS, index))).toBe(index);
    }
  });

  it("clamps a tick between recorded frames to the frame AT OR BEFORE it", () => {
    expect(frameIndexForTick(TICKS, 15)).toBe(2); // between tick 10 and 20
    expect(frameIndexForTick(TICKS, 39)).toBe(4); // just before tick 40
  });

  it("clamps below the first frame to index 0, never below", () => {
    expect(frameIndexForTick(TICKS, -50)).toBe(0);
    expect(frameIndexForTick(TICKS, START_TICK)).toBe(0);
  });

  it("clamps past the last frame to the last index", () => {
    expect(frameIndexForTick(TICKS, 10_000)).toBe(TICKS.length - 1);
  });

  it("returns 0 for an empty timeline", () => {
    expect(frameIndexForTick([], 12)).toBe(0);
  });
});

describe("isStartIndex", () => {
  it("is true only for the synthetic pre-game frame", () => {
    expect(isStartIndex(TICKS, 0)).toBe(true);
    expect(isStartIndex(TICKS, 1)).toBe(false);
    // Clamping means an out-of-range low index still resolves to Start.
    expect(isStartIndex(TICKS, -3)).toBe(true);
  });
});

// ── event / meeting / key-moment navigation ──────────────────────────────────

describe("eventTickNumbers", () => {
  it("collects kill / meeting / vent / sabotage ticks, ascending and de-duplicated", () => {
    expect(eventTickNumbers(TICKS)).toEqual([10, 20, 30]);
  });

  it("excludes report_body and task_completed (not jump targets)", () => {
    const only = [frame(5, [reportBody(5), taskCompleted(5)])];
    expect(eventTickNumbers(only)).toEqual([]);
  });

  it("emits one entry for a tick carrying several jump events", () => {
    const busy = [frame(7, [kill(7), vent(7), sabotage(7)])];
    expect(eventTickNumbers(busy)).toEqual([7]);
  });
});

describe("meetingTickNumbers", () => {
  it("returns the meeting ticks in ascending order regardless of input order", () => {
    expect(meetingTickNumbers([meeting(40), meeting(20), meeting(31)])).toEqual([
      20, 31, 40,
    ]);
  });
});

describe("nextAfter / prevBefore", () => {
  const sorted = [10, 20, 30];

  it("nextAfter is STRICTLY greater (standing on a beat moves off it)", () => {
    expect(nextAfter(sorted, 20)).toBe(30);
    expect(nextAfter(sorted, 5)).toBe(10);
    expect(nextAfter(sorted, 30)).toBeNull();
  });

  it("prevBefore is STRICTLY less (standing on a beat moves off it)", () => {
    expect(prevBefore(sorted, 20)).toBe(10);
    expect(prevBefore(sorted, 31)).toBe(30);
    expect(prevBefore(sorted, 10)).toBeNull();
  });

  it("handles an empty list", () => {
    expect(nextAfter([], 0)).toBeNull();
    expect(prevBefore([], 0)).toBeNull();
  });
});

describe("keyMoments", () => {
  it("ranks kill → meeting → ejection → sabotage when beats collide on one tick", () => {
    const ticks = [frame(12, [kill(12), meetingTriggered(12), sabotage(12)])];
    expect(keyMoments(ticks, [meeting(12)])).toEqual([{ tick: 12, kind: "kill" }]);
  });

  it("labels a resolved meeting tick 'meeting', not 'ejection' (meeting outranks)", () => {
    expect(keyMoments([], [meeting(20, "EJECTED")])).toEqual([
      { tick: 20, kind: "meeting" },
    ]);
  });

  it("takes sabotage only when nothing louder shares the tick", () => {
    expect(keyMoments([frame(30, [sabotage(30)])], [])).toEqual([
      { tick: 30, kind: "sabotage" },
    ]);
  });

  it("emits at most one moment per tick, ascending", () => {
    const moments = keyMoments(TICKS, [meeting(20), meeting(40, "SKIPPED")]);
    expect(moments).toEqual([
      { tick: 10, kind: "kill" },
      { tick: 20, kind: "meeting" },
      { tick: 30, kind: "sabotage" },
      { tick: 40, kind: "meeting" },
    ]);
    expect(keyMomentTicks(TICKS, [meeting(20), meeting(40, "SKIPPED")])).toEqual([
      10, 20, 30, 40,
    ]);
  });

  it("ignores report_body and task_completed", () => {
    expect(keyMoments([frame(8, [reportBody(8), taskCompleted(8)])], [])).toEqual([]);
  });
});

// ── playback coherence: the meeting pause + the finale beat (Task 19.10) ─────

describe("meetingTickSet", () => {
  it("is the membership form of meetingTickNumbers", () => {
    const set = meetingTickSet([meeting(20), meeting(40)]);
    expect(set.has(20)).toBe(true);
    expect(set.has(40)).toBe(true);
    expect(set.has(30)).toBe(false);
    expect(set.size).toBe(2);
  });
});

describe("shouldPauseAtMeeting", () => {
  const meetingTicks = meetingTickSet([meeting(20), meeting(30)]);

  it("fires on the EDGE of stepping onto a meeting tick", () => {
    // index 2 (tick 10) → index 3 (tick 20, a meeting).
    expect(shouldPauseAtMeeting(TICKS, meetingTicks, 2, 3)).toBe(true);
  });

  it("does not fire when the destination carries no meeting", () => {
    expect(shouldPauseAtMeeting(TICKS, meetingTicks, 1, 2)).toBe(false);
  });

  it("does not fire when already parked on the meeting tick — Resume must work", () => {
    // The whole reason the predicate is edge-triggered: a level predicate would
    // re-pause the instant Play was pressed on the meeting frame, making the
    // transport's single Play/Pause toggle read as dead.
    expect(shouldPauseAtMeeting(TICKS, meetingTicks, 3, 3)).toBe(false);
  });

  it("pauses again on back-to-back meeting ticks", () => {
    // Two adjacent frames both carrying meetings: the second must get its own
    // pause rather than being silently skipped.
    const adjacent = [frame(START_TICK), frame(20), frame(30)];
    expect(shouldPauseAtMeeting(adjacent, meetingTicks, 1, 2)).toBe(true);
  });

  it("clamps out-of-range indices instead of inventing a tick", () => {
    // 999 clamps to the last frame (tick 40), which is not a meeting tick.
    expect(shouldPauseAtMeeting(TICKS, meetingTicks, 5, 999)).toBe(false);
  });
});

describe("finaleAtIndex", () => {
  it("shows the finale on the LAST frame only", () => {
    expect(finaleAtIndex(TICKS, TICKS.length - 1, FINALE)).toBe(FINALE);
    expect(finaleAtIndex(TICKS, TICKS.length - 2, FINALE)).toBeNull();
    expect(finaleAtIndex(TICKS, 0, FINALE)).toBeNull();
  });

  it("is position-derived, so an index past the end still shows it", () => {
    expect(finaleAtIndex(TICKS, 999, FINALE)).toBe(FINALE);
  });

  it("has no finale beat at all for a partial replay", () => {
    expect(finaleAtIndex(TICKS, TICKS.length - 1, null)).toBeNull();
  });

  it("pins nothing to a phantom frame on an empty timeline", () => {
    expect(finaleAtIndex([], 0, FINALE)).toBeNull();
  });
});

// ── advantage graph + event timeline ─────────────────────────────────────────

describe("advantageSeries", () => {
  it("carries BOTH the array index and the engine tick for every frame", () => {
    const series = advantageSeries(TICKS);
    expect(series).toHaveLength(TICKS.length);
    expect(series[0]).toEqual({ index: 0, tick: START_TICK, advantage: 0 });
    expect(series[4]).toEqual({ index: 4, tick: 30, advantage: 0.4 });
  });

  it("is empty for an empty timeline", () => {
    expect(advantageSeries([])).toEqual([]);
  });
});

describe("timelineMarkers", () => {
  it("places each marker on its ACTOR's lane", () => {
    const markers = timelineMarkers([
      frame(10, [kill(10, "p-1", "p-4")]),
      frame(20, [meetingTriggered(20, "p-2")]),
      frame(30, [vent(30, "p-7"), sabotage(30, "p-3")]),
    ]);
    expect(markers.map((m) => [m.tick, m.agentId, m.kind])).toEqual([
      [10, "p-1", "kill"],
      [20, "p-2", "meeting"],
      [30, "p-7", "vent"],
      [30, "p-3", "sabotage"],
    ]);
  });

  it("drops report_body / task_completed (not lane markers)", () => {
    expect(timelineMarkers([frame(5, [reportBody(5), taskCompleted(5)])])).toEqual([]);
  });

  it("gives co-located markers distinct keys", () => {
    const markers = timelineMarkers([frame(30, [vent(30, "p-7"), sabotage(30, "p-3")])]);
    const keys = markers.map((m) => m.key);
    expect(new Set(keys).size).toBe(keys.length);
  });
});

// ── URL sync ─────────────────────────────────────────────────────────────────

describe("parsePlaybackParams", () => {
  it("falls back to the defaults on an empty query", () => {
    expect(parsePlaybackParams("")).toEqual({
      set: null,
      gameId: null,
      tick: null,
      perspective: OMNISCIENT,
      beliefView: "belief",
      selectedAgent: null,
      selectedMeeting: null,
      view: null,
      reveal: false,
    });
  });

  it("reads the eight keys plus the top-level view", () => {
    const parsed = parsePlaybackParams(
      "?set=9p2i&game_id=g-1&tick=42&perspective=p-3&beliefView=error" +
        "&selectedAgent=p-5&selectedMeeting=m-2&view=tournament&reveal=1",
    );
    expect(parsed).toEqual({
      set: "9p2i",
      gameId: "g-1",
      tick: 42,
      perspective: { mode: "agent", agentId: "p-3" },
      beliefView: "error",
      selectedAgent: "p-5",
      selectedMeeting: "m-2",
      view: "tournament",
      reveal: true,
    });
  });

  it("treats an unparseable tick as absent rather than as 0", () => {
    expect(parsePlaybackParams("?tick=soon").tick).toBeNull();
  });

  it("rejects an unknown beliefView / view rather than trusting the URL", () => {
    const parsed = parsePlaybackParams("?beliefView=guesses&view=admin");
    expect(parsed.beliefView).toBe("belief");
    expect(parsed.view).toBeNull();
  });

  it("reads an empty or omniscient perspective as Omniscient", () => {
    expect(parsePlaybackParams("?perspective=").perspective).toEqual(OMNISCIENT);
    expect(parsePlaybackParams("?perspective=omniscient").perspective).toEqual(OMNISCIENT);
  });

  it("only `reveal=1` reveals — anything else stays unspoiled", () => {
    expect(parsePlaybackParams("?reveal=1").reveal).toBe(true);
    for (const raw of ["0", "true", "yes", ""]) {
      expect(parsePlaybackParams(`?reveal=${raw}`).reveal).toBe(false);
    }
  });
});

describe("serializePlaybackParams", () => {
  const DEFAULTS = {
    set: null,
    gameId: null,
    tick: null,
    perspective: OMNISCIENT,
    beliefView: "belief",
    selectedAgent: null,
    selectedMeeting: null,
    view: null,
    reveal: false,
  } as const;

  it("emits nothing at all for the default state", () => {
    // Load-bearing: GuidedTour's first-run check is "does this URL carry ANY
    // key?", so a bare visit must serialize to the empty string.
    expect(serializePlaybackParams(DEFAULTS)).toBe("");
  });

  it("omits `reveal` when off and writes `reveal=1` when on", () => {
    expect(serializePlaybackParams({ ...DEFAULTS, reveal: false })).toBe("");
    expect(serializePlaybackParams({ ...DEFAULTS, reveal: true })).toBe("?reveal=1");
  });

  it("omits the default beliefView but writes a non-default one", () => {
    expect(serializePlaybackParams({ ...DEFAULTS, beliefView: "belief" })).toBe("");
    expect(serializePlaybackParams({ ...DEFAULTS, beliefView: "truth" })).toBe(
      "?beliefView=truth",
    );
  });

  it("writes the agent id (not the literal 'agent') for a fog perspective", () => {
    expect(
      serializePlaybackParams({
        ...DEFAULTS,
        perspective: { mode: "agent", agentId: "p-3" },
      }),
    ).toBe("?perspective=p-3");
  });

  it("round-trips every moment through parse", () => {
    const moments = [
      DEFAULTS,
      { ...DEFAULTS, set: "9p2i", gameId: "g-1", tick: 0 },
      { ...DEFAULTS, tick: START_TICK, reveal: true },
      {
        ...DEFAULTS,
        set: "4p1i",
        gameId: "g-9",
        tick: 312,
        perspective: { mode: "agent", agentId: "p-5" } as const,
        beliefView: "error" as const,
        selectedAgent: "p-2",
        selectedMeeting: "m-1",
        view: "highlights" as const,
        reveal: true,
      },
    ];
    for (const moment of moments) {
      expect(parsePlaybackParams(serializePlaybackParams(moment))).toEqual(moment);
    }
  });
});
