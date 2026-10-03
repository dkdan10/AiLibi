// Three facts about a meeting that only the omniscient view may show.
//
// Each is read straight off the served replay, and none reaches a player:
//
//   1. CORPSE AGE — for a body meeting, how long the reported body lay there:
//      the meeting's tick minus the victim's kill tick. The kill tick is the
//      fact the recorded body handle withholds from every agent, so it belongs
//      to the spectator alone.
//   2. THE ACCUSED'S TRUE ROUTE — for each player an accusation in the meeting
//      names, the rooms the engine recorded them in (`agent_states`), from the
//      last regroup (or tick 0) to the meeting, with ticks spent inside a vent
//      named as such. It is never read from what the accused said.
//   3. THE OPENER'S REPLY — whether another speaker accused the player who
//      opened the meeting, and whether the opener spoke again after that.
//
// `MeetingView` renders them only under `perspective.mode === "omniscient"`.
// Pure functions over the view-model: the structural slices below are satisfied
// by a real `ReplayView` and by the committed skeleton dump the tests walk
// (`replay-skeleton.fixture.json`), which also re-derives the census's own
// counts of the same facts.

import { regroupsAfterMeetings } from "./regroup";
import type {
  ExperimentConfigView,
  KillEventView,
  ReportBodyEventView,
  TickEventView,
} from "../types/api";

/** The slice of one agent's frame state this module reads. */
export interface AnnotationAgentSlice {
  readonly agent_id: string;
  readonly room_id: string | null;
  readonly is_alive: boolean;
  readonly is_venting: boolean;
}

/** The slice of a `TickView` this module reads. */
export interface AnnotationFrameSlice {
  readonly tick: number;
  readonly events: readonly TickEventView[];
  readonly agent_states: readonly AnnotationAgentSlice[];
}

/** A turn's claims, narrowed to what this module reads: who an accusation names. */
export interface AnnotationClaimSlice {
  readonly type: string;
  readonly against?: string;
}

export interface AnnotationTurnSlice {
  readonly turn_index: number;
  readonly speaker: string;
  readonly claims: readonly AnnotationClaimSlice[];
}

export interface AnnotationMeetingSlice {
  readonly meeting_id: string;
  readonly tick: number;
  readonly trigger_kind: "body" | "emergency";
  readonly triggered_by: string;
  readonly turns: readonly AnnotationTurnSlice[];
}

/** The slice of a `ReplayView` this module reads. */
export interface AnnotationReplaySlice {
  readonly metadata: { readonly experiment_config?: Pick<ExperimentConfigView, "meeting_reset"> | null };
  readonly ticks: readonly AnnotationFrameSlice[];
  readonly meetings: readonly AnnotationMeetingSlice[];
}

/** How long the reported body lay there before its meeting. */
export interface CorpseAge {
  readonly victimId: string;
  readonly killTick: number;
  /** Meeting tick minus kill tick. */
  readonly age: number;
}

/** One stretch of ticks a player spent in one room, inside a vent or not. */
export interface RouteLeg {
  readonly roomId: string;
  readonly fromTick: number;
  readonly toTick: number;
  readonly inVent: boolean;
}

/** Where one accused player really was before the meeting. */
export interface AccusedRoute {
  readonly playerId: string;
  readonly legs: readonly RouteLeg[];
}

/** Whether an accused opener spoke again. */
export interface OpenerReply {
  readonly openerId: string;
  /** The first other speaker to accuse the opener. */
  readonly accuserId: string;
  /** Whether the opener took a turn after that accusation. */
  readonly answered: boolean;
}

export interface MeetingAnnotations {
  /** `null` for an emergency meeting, which reports no body. */
  readonly corpse: CorpseAge | null;
  /** One per player an accusation names, in the order they were first named. */
  readonly routes: readonly AccusedRoute[];
  /** `null` when no other speaker accused the opener. */
  readonly openerReply: OpenerReply | null;
  /** The first tick the routes cover: the regroup after the last meeting, or 0. */
  readonly routesFrom: number;
}

function accusations(turn: AnnotationTurnSlice): string[] {
  return turn.claims.flatMap((claim) => {
    if (claim.type !== "accusation") return [];
    if (claim.against === undefined) {
      throw new Error(`turn ${turn.turn_index}: an accusation names nobody`);
    }
    return [claim.against];
  });
}

/** The reported body's age at a body meeting, or `null` for an emergency. */
export function corpseAge(
  meeting: AnnotationMeetingSlice,
  frames: readonly AnnotationFrameSlice[],
): CorpseAge | null {
  if (meeting.trigger_kind !== "body") return null;
  const report = frames
    .filter((frame) => frame.tick === meeting.tick)
    .flatMap((frame) => frame.events)
    .find((event): event is ReportBodyEventView => event.type === "report_body");
  if (report === undefined) {
    throw new Error(`${meeting.meeting_id}: a body meeting with no report on its frame`);
  }
  const kill = frames
    .flatMap((frame) => frame.events)
    .find((event): event is KillEventView => event.type === "kill" && event.victim_id === report.body_of);
  if (kill === undefined) {
    throw new Error(`${meeting.meeting_id}: the reported body ${report.body_of} joins no kill`);
  }
  return { victimId: report.body_of, killTick: kill.tick, age: meeting.tick - kill.tick };
}

/**
 * Whether another speaker accused the opener and, if so, whether the opener
 * spoke again afterwards. `null` when nobody else accused the opener.
 */
export function openerReply(meeting: AnnotationMeetingSlice): OpenerReply | null {
  const opener = meeting.triggered_by;
  const turns = [...meeting.turns].sort((a, b) => a.turn_index - b.turn_index);
  const charge = turns.findIndex(
    (turn) => turn.speaker !== opener && accusations(turn).includes(opener),
  );
  if (charge === -1) return null;
  const accuser = turns[charge];
  if (accuser === undefined) {
    throw new Error(`${meeting.meeting_id}: turn ${charge} vanished`);
  }
  return {
    openerId: opener,
    accuserId: accuser.speaker,
    answered: turns.slice(charge + 1).some((turn) => turn.speaker === opener),
  };
}

/**
 * The first tick an accused player's route covers: the frame after the
 * previous meeting on a recording that regroups (everyone starts that frame in
 * the meeting room), and tick 0 otherwise.
 */
export function routeWindowStart(replay: AnnotationReplaySlice, meeting: AnnotationMeetingSlice): number {
  if (!regroupsAfterMeetings(replay)) return 0;
  const previous = replay.meetings
    .filter((other) => other.tick < meeting.tick)
    .reduce<number | null>((latest, other) => (latest === null ? other.tick : Math.max(latest, other.tick)), null);
  return previous === null ? 0 : previous + 1;
}

/**
 * The rooms `playerId` was recorded in, frame by frame, from `fromTick` to the
 * meeting's tick inclusive, merged into legs. A frame on which the player is
 * not alive has no room and is left out.
 */
export function recordedRoute(
  frames: readonly AnnotationFrameSlice[],
  playerId: string,
  fromTick: number,
  toTick: number,
): RouteLeg[] {
  const legs: RouteLeg[] = [];
  for (const frame of frames) {
    if (frame.tick < fromTick || frame.tick > toTick) continue;
    const state = frame.agent_states.find((candidate) => candidate.agent_id === playerId);
    if (state === undefined || !state.is_alive) continue;
    if (state.room_id === null) {
      throw new Error(`tick ${frame.tick}: living ${playerId} has no recorded room`);
    }
    const last = legs[legs.length - 1];
    if (last !== undefined && last.roomId === state.room_id && last.inVent === state.is_venting) {
      legs[legs.length - 1] = { ...last, toTick: frame.tick };
    } else {
      legs.push({ roomId: state.room_id, fromTick: frame.tick, toTick: frame.tick, inVent: state.is_venting });
    }
  }
  return legs;
}

/** All three omniscient facts for one meeting of the replay. */
export function meetingAnnotations(replay: AnnotationReplaySlice, meetingId: string): MeetingAnnotations {
  const meeting = replay.meetings.find((candidate) => candidate.meeting_id === meetingId);
  if (meeting === undefined) {
    throw new Error(`no meeting ${meetingId} in this replay`);
  }
  const routesFrom = routeWindowStart(replay, meeting);
  const accused: string[] = [];
  for (const turn of [...meeting.turns].sort((a, b) => a.turn_index - b.turn_index)) {
    for (const target of accusations(turn)) {
      if (!accused.includes(target)) accused.push(target);
    }
  }
  return {
    corpse: corpseAge(meeting, replay.ticks),
    routes: accused.map((playerId) => ({
      playerId,
      legs: recordedRoute(replay.ticks, playerId, routesFrom, meeting.tick),
    })),
    openerReply: openerReply(meeting),
    routesFrom,
  };
}
