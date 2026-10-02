// The omniscient meeting annotations, pinned against the bytes the API serves.
//
// Two of the three facts have census twins, counted by
// `eval/gameplay_census.py` over the promoted 9p2i set and published by
// `uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout`:
// `corpse_age_at_report` (114 report meetings) and `accused_opener_answers`
// (87 of 105). The annotations re-derive both from the served frames and turns.
// The third, the accused's true route, is planted against the one thing it must
// never become: a reading of what the accused SAID.

import { describe, expect, it } from "vitest";

import {
  type AnnotationMeetingSlice,
  type AnnotationReplaySlice,
  type AnnotationTurnSlice,
  corpseAge,
  meetingAnnotations,
  openerReply,
  recordedRoute,
  type RouteLeg,
  routeWindowStart,
} from "./annotations";
import {
  readSkeleton,
  type SkeletonGame,
  type SkeletonMeeting,
  skeletonGame,
  skeletonSet,
} from "./skeleton.testkit";
import type { TickEventView } from "../types/api";

const SKELETON = readSkeleton();
const NINE = skeletonSet(SKELETON, "9p2i");

describe("the census twins over the promoted 9p2i set", () => {
  it("reproduces corpse_age_at_report", () => {
    const tally: Record<string, number> = {};
    let reports = 0;
    for (const game of NINE.games) {
      for (const meeting of game.replay.meetings) {
        const corpse = corpseAge(meeting, game.replay.ticks);
        if (meeting.trigger_kind === "emergency") {
          expect(corpse).toBeNull();
          continue;
        }
        if (corpse === null) throw new Error(`${meeting.meeting_id}: a body meeting with no corpse`);
        reports += 1;
        tally[String(corpse.age)] = (tally[String(corpse.age)] ?? 0) + 1;
      }
    }
    expect(reports).toBe(114);
    expect(tally).toEqual({ "1": 19, "2": 13, "3": 33, "4": 30, "5": 6, "6": 6, "7": 2, "8": 2, "10": 2, "11": 1 });
  });

  it("reproduces accused_opener_answers", () => {
    let accused = 0;
    let answered = 0;
    for (const game of NINE.games) {
      for (const meeting of game.replay.meetings) {
        const reply = openerReply(meeting);
        if (reply === null) continue;
        accused += 1;
        if (reply.answered) answered += 1;
      }
    }
    expect([answered, accused]).toEqual([87, 105]);
  });
});

// ── the opener's reply, planted ─────────────────────────────────────────────

function turn(index: number, speaker: string, accuses: readonly string[] = []): AnnotationTurnSlice {
  return { turn_index: index, speaker, claims: accuses.map((against) => ({ type: "accusation", against })) };
}

function meeting(turns: readonly AnnotationTurnSlice[]): AnnotationMeetingSlice {
  return { meeting_id: "planted:meeting-0", tick: 9, trigger_kind: "emergency", triggered_by: "p-1", turns };
}

describe("the opener's reply", () => {
  it("shows the no-reply case and loses it when the opener's rebuttal is added", () => {
    const accusedOnly = meeting([turn(0, "p-1", ["p-2"]), turn(1, "p-2", ["p-1"]), turn(2, "p-3", ["p-1"])]);
    expect(openerReply(accusedOnly)).toEqual({ openerId: "p-1", accuserId: "p-2", answered: false });
    const rebutted = meeting([...accusedOnly.turns, turn(3, "p-1", ["p-2"])]);
    expect(openerReply(rebutted)).toEqual({ openerId: "p-1", accuserId: "p-2", answered: true });
  });

  it("counts only a turn after the first accusation, in turn order", () => {
    // Served out of order: the opener's second turn comes BEFORE the charge.
    const early = meeting([turn(2, "p-2", ["p-1"]), turn(0, "p-1"), turn(1, "p-1")]);
    expect(openerReply(early)).toEqual({ openerId: "p-1", accuserId: "p-2", answered: false });
  });

  it("is absent when no other speaker accuses the opener", () => {
    expect(openerReply(meeting([turn(0, "p-1", ["p-1"]), turn(1, "p-2", ["p-3"])]))).toBeNull();
    expect(openerReply(meeting([turn(0, "p-1")]))).toBeNull();
  });

  it("reads only accusations among a turn's claims", () => {
    const withAlibi = meeting([
      turn(0, "p-1"),
      { turn_index: 1, speaker: "p-2", claims: [{ type: "alibi" }, { type: "accusation", against: "p-1" }] },
    ]);
    expect(openerReply(withAlibi)).toEqual({ openerId: "p-1", accuserId: "p-2", answered: false });
  });

  it("raises on an accusation that names nobody", () => {
    expect(() => openerReply(meeting([turn(0, "p-1"), { turn_index: 1, speaker: "p-2", claims: [{ type: "accusation" }] }]))).toThrow(
      /^turn 1: an accusation names nobody$/,
    );
  });
});

// ── the corpse's age, planted ───────────────────────────────────────────────

function frameWith(tick: number, events: readonly TickEventView[]) {
  return { tick, events, agent_states: [] };
}

describe("the reported corpse's age", () => {
  const kill: TickEventView = { type: "kill", tick: 4, killer_id: "p-9", victim_id: "p-2", room_id: "ADMIN" };
  const report: TickEventView = { type: "report_body", tick: 9, reporter_id: "p-1", body_of: "p-2", room_id: "ADMIN" };
  const body: AnnotationMeetingSlice = { ...meeting([turn(0, "p-1")]), trigger_kind: "body" };

  it("is the meeting tick minus the reported victim's kill tick", () => {
    expect(corpseAge(body, [frameWith(4, [kill]), frameWith(9, [report])])).toEqual({ victimId: "p-2", killTick: 4, age: 5 });
    // Another kill and a vent on the same frames do not stand in for them.
    const other: TickEventView = { type: "kill", tick: 2, killer_id: "p-9", victim_id: "p-3", room_id: "LABS" };
    const vent: TickEventView = {
      type: "vent",
      tick: 9,
      actor_id: "p-9",
      phase: "enter",
      from_room_id: "LABS",
      to_room_id: "LABS",
      traversal_ticks: 0,
    };
    expect(corpseAge(body, [frameWith(2, [other]), frameWith(4, [kill]), frameWith(9, [vent, report])])).toEqual({
      victimId: "p-2",
      killTick: 4,
      age: 5,
    });
  });

  it("is absent for an emergency meeting and raises on a body meeting it cannot join", () => {
    expect(corpseAge(meeting([turn(0, "p-1")]), [frameWith(4, [kill])])).toBeNull();
    expect(() => corpseAge(body, [frameWith(4, [kill]), frameWith(9, [])])).toThrow(
      /^planted:meeting-0: a body meeting with no report on its frame$/,
    );
    expect(() => corpseAge(body, [frameWith(9, [report])])).toThrow(
      /^planted:meeting-0: the reported body p-2 joins no kill$/,
    );
    // A report on another frame is not this meeting's.
    expect(() => corpseAge(body, [frameWith(4, [kill]), frameWith(8, [report])])).toThrow(/no report/);
  });
});

// ── the accused's route, planted against the spoken alibi ───────────────────

type RouteRule = (game: SkeletonGame, meeting: SkeletonMeeting, playerId: string) => RouteLeg[];

/** The shipped rule: rooms read from the recorded agent states. */
const shippedRoute: RouteRule = (game, meeting, playerId) =>
  recordedRoute(game.replay.ticks, playerId, routeWindowStart(game.replay, meeting), meeting.tick);

/**
 * Planted: the route the accused STATED, read from their own alibi in the
 * meeting — the reading the annotation must never become.
 */
const spokenRoute: RouteRule = (_game, meeting, playerId) => {
  const stated = meeting.turns
    .flatMap((candidate) => candidate.alibis)
    .find((alibi) => alibi.subject === playerId);
  return (stated?.route ?? []).map(([roomId, fromTick, toTick]) => ({ roomId, fromTick, toTick, inVent: false }));
};

/** The truth, read independently: one room per frame off the dump, merged. */
function truthAbout(game: SkeletonGame, meeting: SkeletonMeeting, playerId: string): RouteLeg[] {
  const from = routeWindowStart(game.replay, meeting);
  const legs: RouteLeg[] = [];
  for (const frame of game.replay.ticks) {
    if (frame.tick < from || frame.tick > meeting.tick) continue;
    const state = frame.agent_states.find((candidate) => candidate.agent_id === playerId);
    if (state === undefined || state.room_id === null) continue;
    const last = legs.at(-1);
    if (last !== undefined && last.roomId === state.room_id && last.inVent === state.is_venting) {
      legs[legs.length - 1] = { ...last, toTick: frame.tick };
    } else {
      legs.push({ roomId: state.room_id, fromTick: frame.tick, toTick: frame.tick, inVent: state.is_venting });
    }
  }
  return legs;
}

function assertRoutesAreRecorded(
  rule: RouteRule,
  game: SkeletonGame,
  meetingId: string,
  only: string | null = null,
): void {
  const meeting = game.replay.meetings.find((candidate) => candidate.meeting_id === meetingId);
  if (meeting === undefined) throw new Error(`no ${meetingId}`);
  const accused = [...new Set(meeting.turns.flatMap((candidate) => candidate.claims.map((claim) => claim.against)))];
  expect(accused.length).toBeGreaterThan(0);
  for (const playerId of accused) {
    if (only !== null && playerId !== only) continue;
    expect(rule(game, meeting, playerId), `${meetingId} ${playerId}`).toEqual(truthAbout(game, meeting, playerId));
  }
}

describe("the accused player's true route", () => {
  const seed2 = skeletonGame(NINE, "headless-seed-2");

  it("reads the recorded rooms, where the accused's own account disagrees", () => {
    // Seed 2's first meeting ejects crewmate p-5 on two flags that set its
    // stated route against other players' sightings. Its account is stamped on
    // the players' clock, one tick ahead of the frames, and opens in the
    // Cafeteria where the game spawned everyone, so it disagrees with the
    // recorded rooms tick for tick, for p-5 and for both other accused players.
    assertRoutesAreRecorded(shippedRoute, seed2, "headless-seed-2:meeting-0");
    expect(() => assertRoutesAreRecorded(spokenRoute, seed2, "headless-seed-2:meeting-0", "p-5")).toThrow(
      /headless-seed-2:meeting-0 p-5/,
    );
    expect(() => assertRoutesAreRecorded(spokenRoute, seed2, "headless-seed-2:meeting-0")).toThrow(
      /headless-seed-2:meeting-0 p-3/,
    );
  });

  it("names the ticks spent inside a vent", () => {
    // Seed 19's first meeting accuses p-6, who dived in Storage at 8 and came up
    // in Engineering at 11.
    const seed19 = skeletonGame(NINE, "headless-seed-19");
    const annotated = meetingAnnotations(seed19.replay, "headless-seed-19:meeting-0");
    const p6 = annotated.routes.find((route) => route.playerId === "p-6");
    expect(p6?.legs.slice(-2)).toEqual([
      { roomId: "STORAGE", fromTick: 8, toTick: 10, inVent: true },
      { roomId: "ENGINEERING", fromTick: 11, toTick: 12, inVent: false },
    ]);
    expect(annotated.routes.map((route) => route.playerId)).toEqual(["p-5", "p-4", "p-6", "p-1"]);
    // Served out of order, the turns are still read in turn order.
    const reversed = {
      ...seed19.replay,
      meetings: seed19.replay.meetings.map((item) => ({ ...item, turns: [...item.turns].reverse() })),
    };
    expect(meetingAnnotations(reversed, "headless-seed-19:meeting-0").routes.map((route) => route.playerId)).toEqual([
      "p-5",
      "p-4",
      "p-6",
      "p-1",
    ]);
    expect(annotated.corpse).toEqual({ victimId: "p-8", killTick: 9, age: 3 });
    expect(annotated.openerReply).toEqual({ openerId: "p-4", accuserId: "p-5", answered: true });
    expect(annotated.routesFrom).toBe(0);
  });

  it("starts after the last regroup on a recording that regroups, and at tick 0 otherwise", () => {
    const seed19 = skeletonGame(NINE, "headless-seed-19");
    const second = seed19.replay.meetings[1];
    if (second === undefined) throw new Error("seed 19 has a second meeting");
    expect(routeWindowStart(seed19.replay, second)).toBe(13);
    // After two meetings the window opens after the later one.
    const third = seed19.replay.meetings[2];
    if (third === undefined) throw new Error("seed 19 has a third meeting");
    expect(routeWindowStart(seed19.replay, third)).toBe(32);
    expect(meetingAnnotations(seed19.replay, second.meeting_id).routesFrom).toBe(13);
    const preserved: AnnotationReplaySlice = { ...seed19.replay, metadata: { experiment_config: { meeting_reset: "preserve" } } };
    expect(routeWindowStart(preserved, second)).toBe(0);
    const unconfigured: AnnotationReplaySlice = { ...seed19.replay, metadata: { experiment_config: null } };
    expect(routeWindowStart(unconfigured, second)).toBe(0);
    // The first frame after the regroup already carries each survivor's first
    // move out of the meeting room (no recorded frame shows them gathered), so
    // the route opens there: p-3, accused first, stands one corridor away.
    const route = meetingAnnotations(seed19.replay, second.meeting_id).routes[0];
    expect(route?.playerId).toBe("p-3");
    expect(route?.legs[0]).toEqual({ roomId: "WEST_HALL", fromTick: 13, toTick: 13, inVent: false });
  });

  it("leaves out frames on which the player is not alive, and raises on a living one with no room", () => {
    const frames = [
      { tick: 0, events: [], agent_states: [{ agent_id: "p-1", room_id: "ADMIN", is_alive: true, is_venting: false }] },
      { tick: 1, events: [], agent_states: [{ agent_id: "p-1", room_id: "ADMIN", is_alive: false, is_venting: false }] },
    ];
    expect(recordedRoute(frames, "p-1", 0, 1)).toEqual([{ roomId: "ADMIN", fromTick: 0, toTick: 0, inVent: false }]);
    expect(recordedRoute(frames, "p-7", 0, 1)).toEqual([]);
    const roomless = [{ tick: 4, events: [], agent_states: [{ agent_id: "p-3", room_id: null, is_alive: true, is_venting: false }] }];
    expect(() => recordedRoute(roomless, "p-3", 0, 4)).toThrow(/^tick 4: living p-3 has no recorded room$/);
  });

  it("raises on a meeting the replay does not carry", () => {
    expect(() => meetingAnnotations(skeletonGame(NINE, "headless-seed-2").replay, "headless-seed-2:meeting-9")).toThrow(
      /^no meeting headless-seed-2:meeting-9 in this replay$/,
    );
  });
});
