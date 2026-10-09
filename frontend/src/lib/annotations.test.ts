// The omniscient meeting annotations, pinned against the bytes the API serves.
//
// Two of the three facts have census twins, counted by
// `eval/gameplay_census.py` over the shown 9p2i set and published in
// `docs/gameplay-census.json` (`corpse_age_at_report` and
// `accused_opener_answers`). The annotations re-derive both from the served
// frames and turns and must equal the published cells, whatever the recording.
// The third, the accused's true route, is planted against the one thing it must
// never become: a reading of what the accused SAID.

import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

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

interface CensusSet {
  readonly label: string;
  readonly cells: Readonly<Record<string, { readonly numerator: number; readonly denominator: number }>>;
  readonly tables: Readonly<Record<string, { readonly counts: Readonly<Record<string, number>> }>>;
}

/** The published gameplay census's row for the shown set: the Python twin. */
function shownCensus(): CensusSet {
  const path = resolve(dirname(fileURLToPath(import.meta.url)), "../../../docs/gameplay-census.json");
  const parsed = JSON.parse(readFileSync(path, "utf8")) as { readonly sets: readonly CensusSet[] };
  const found = parsed.sets.find((candidate) => candidate.label === "samples/9p2i");
  if (found === undefined) throw new Error("the published census carries no samples/9p2i row");
  return found;
}

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
    // The published table, equal bucket for bucket (114 report meetings on
    // round 2's bytes).
    const published = shownCensus().tables["corpse_age_at_report"]?.counts;
    expect(reports).toBeGreaterThan(0);
    expect(tally).toEqual(published);
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
    // The published cell (87 of 105 on round 2's bytes).
    const cell = shownCensus().cells["accused_opener_answers"];
    expect(accused).toBeGreaterThan(0);
    expect([answered, accused]).toEqual([cell?.numerator, cell?.denominator]);
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

/** Every meeting of the shown set that names at least one accused player. */
function accusingMeetings(): { game: SkeletonGame; meeting: SkeletonMeeting }[] {
  return NINE.games.flatMap((game) =>
    game.replay.meetings
      .filter((meeting) => meeting.turns.some((candidate) => candidate.claims.length > 0))
      .map((meeting) => ({ game, meeting })),
  );
}

/** The index of the first vent leg a surfaced leg follows, or -1. */
function surfacingDive(legs: readonly RouteLeg[]): number {
  return legs.findIndex((leg, index) => leg.inVent && legs[index + 1]?.inVent === false);
}

/** The shown set's first game that holds at least three meetings. */
function gameWithThreeMeetings(): SkeletonGame {
  const found = NINE.games.find((game) => game.replay.meetings.length >= 3);
  if (found === undefined) throw new Error("no game of the shown set holds three meetings");
  return found;
}

describe("the accused player's true route", () => {
  it("reads the recorded rooms, where the accused's own account disagrees", () => {
    // Every accused player of every meeting: the shipped route is the recorded
    // rooms tick for tick. The planted spoken route is not: somewhere on the
    // shown bytes an accused player's stated account disagrees with the
    // recorded rooms (seed 2's first meeting on round 2's bytes, where p-5's
    // account ran one tick ahead of the frames).
    const meetings = accusingMeetings();
    expect(meetings.length).toBeGreaterThan(0);
    let disagreements = 0;
    for (const { game, meeting } of meetings) {
      assertRoutesAreRecorded(shippedRoute, game, meeting.meeting_id);
      try {
        assertRoutesAreRecorded(spokenRoute, game, meeting.meeting_id);
      } catch {
        disagreements += 1;
      }
    }
    expect(disagreements).toBeGreaterThan(0);
  });

  it("names the ticks spent inside a vent", () => {
    // The shown set's first accused route that dives: its vent leg is followed
    // by a surfaced leg that opens the tick after (seed 19's first meeting on
    // round 2's bytes, where p-6 dived in Storage and came up in Engineering).
    const found = accusingMeetings()
      .flatMap(({ game, meeting }) =>
        meetingAnnotations(game.replay, meeting.meeting_id).routes.map((route) => ({ game, meeting, route })),
      )
      .find(({ route }) => surfacingDive(route.legs) !== -1);
    if (found === undefined) throw new Error("no accused route of the shown set dives and surfaces");
    const { game, meeting, route } = found;
    const dive = surfacingDive(route.legs);
    const surfaced = route.legs[dive + 1];
    expect(route.legs[dive]?.inVent).toBe(true);
    expect(surfaced?.inVent).toBe(false);
    expect(surfaced?.fromTick).toBe((route.legs[dive]?.toTick ?? Number.NaN) + 1);
    expect(route.legs).toEqual(truthAbout(game, meeting, route.playerId));

    // The routes follow the accusations in turn order, even served out of order.
    const annotated = meetingAnnotations(game.replay, meeting.meeting_id);
    const order: string[] = [];
    for (const turn of [...meeting.turns].sort((a, b) => a.turn_index - b.turn_index)) {
      for (const claim of turn.claims) {
        if (!order.includes(claim.against)) order.push(claim.against);
      }
    }
    expect(annotated.routes.map((item) => item.playerId)).toEqual(order);
    const reversed = {
      ...game.replay,
      meetings: game.replay.meetings.map((item) => ({ ...item, turns: [...item.turns].reverse() })),
    };
    expect(meetingAnnotations(reversed, meeting.meeting_id).routes.map((item) => item.playerId)).toEqual(order);
    // The other two annotations are the meeting's own.
    expect(annotated.corpse).toEqual(corpseAge(meeting, game.replay.ticks));
    expect(annotated.openerReply).toEqual(openerReply(meeting));
    expect(annotated.routesFrom).toBe(routeWindowStart(game.replay, meeting));
  });

  it("starts after the last regroup on a recording that regroups, and at tick 0 otherwise", () => {
    // The shown set's first game with three meetings (seed 19 on round 2's
    // bytes, whose windows opened at 13 and 32).
    const head = gameWithThreeMeetings();
    const [first, second, third] = head.replay.meetings;
    if (first === undefined || second === undefined || third === undefined) {
      throw new Error("the game has three meetings");
    }
    expect(routeWindowStart(head.replay, first)).toBe(0);
    expect(routeWindowStart(head.replay, second)).toBe(first.tick + 1);
    // After two meetings the window opens after the later one.
    expect(routeWindowStart(head.replay, third)).toBe(second.tick + 1);
    expect(meetingAnnotations(head.replay, second.meeting_id).routesFrom).toBe(first.tick + 1);
    const preserved: AnnotationReplaySlice = { ...head.replay, metadata: { experiment_config: { meeting_reset: "preserve" } } };
    expect(routeWindowStart(preserved, second)).toBe(0);
    const unconfigured: AnnotationReplaySlice = { ...head.replay, metadata: { experiment_config: null } };
    expect(routeWindowStart(unconfigured, second)).toBe(0);
    // The first frame after the regroup already carries each survivor's first
    // move out of the meeting room (no recorded frame shows them gathered), so
    // a route opens there, never on the meeting's own frame.
    for (const route of meetingAnnotations(head.replay, second.meeting_id).routes) {
      expect(route.legs[0]?.fromTick ?? first.tick + 1).toBeGreaterThan(first.tick);
    }
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
