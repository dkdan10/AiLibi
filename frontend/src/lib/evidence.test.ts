import { describe, expect, it } from "vitest";

import type { AgentMemoryView, MeetingView, TurnView } from "../types/api";
import { observationEventId, turnClaimEventId } from "./contradictions";
import { observationSource, statementSource, type EvidenceSelection } from "./evidence";
import { parsePlaybackParams, serializePlaybackParams } from "./playback";

const turn: TurnView = { turn_id: "opaque-turn", turn_index: 1, speaker: "p-9", turn_kind: "reply", reply_to: null, free_text: "The route looks impossible.", observations: [{ type: "whereabouts", tick: 29, room: "EAST_HALL" }], claims: [{ type: "accusation", against: "p-1", confidence: 0.9, reason: "route" }], fabricated_opening: false, annotations: [] };
const meeting: MeetingView = { meeting_id: "opaque-meeting", tick: 31, triggered_by: "p-1", trigger_kind: "body", outcome: "EJECTED", ejected_player_id: "p-1", turns: [turn], ballots: [], contradictions: [], llm_calls: [], prompt_versions: {}, total_cost_usd: 0, gate: { leader: "p-1", leader_max_confidence: 0.9, threshold: 0.6, passed: true } };
const target: EvidenceSelection = { kind: "statement", id: turn.turn_id, meetingId: meeting.meeting_id, observerId: turn.speaker };
const memory: AgentMemoryView = { agent_id: "p-3", tick: 31, role: "CREWMATE", tasks_completed: 1, tasks_assigned: 2, observations: [], beliefs: [], open_contradictions: [], rendered_memory_text: "private snapshot", observation_references: [{ observation_id: "p-3:29:1", observer_id: "p-3", resolved: true, observation_tick: 29, scene_tick: 28, provenance: "observed", kind: "saw_player", text: "You saw p-4 in CAFETERIA with p-9.", subject_id: "p-4", room: "CAFETERIA", from_room: null, to_room: null }] };

describe("exact evidence identities", () => {
  it("resolves public statement and individual structured artifact, never nearby IDs", () => {
    expect(statementSource(meeting, target)?.turn).toBe(turn);
    turn.claims.forEach((value, index) => expect(statementSource(meeting, { ...target, kind: "artifact", id: turnClaimEventId(turn, index) })).toEqual({ turn, value, kind: "claim" }));
    turn.observations.forEach((value, index) => expect(statementSource(meeting, { ...target, kind: "artifact", id: observationEventId(turn, value, index) })).toEqual({ turn, value, kind: "observation" }));
    expect(statementSource(meeting, { ...target, id: `${turn.turn_id}-missing` })).toBeNull();
    expect(statementSource(meeting, { ...target, kind: "artifact", id: `turn:${turn.turn_id}:claim:999` })).toBeNull();
  });
  it("shows an unrelated but real citation as its actual content, without judging support", () => {
    const selection: EvidenceSelection = { ...target, kind: "observation", observerId: "p-3", id: "p-3:29:1" };
    const row = observationSource(memory, selection);
    expect(row?.subject_id).toBe("p-4");
    expect(row?.scene_tick).toBe(28);
    expect(row?.observation_tick).toBe(29);
    expect(observationSource(memory, { ...selection, observerId: "p-9" })).toBeNull();
    expect(observationSource(memory, { ...selection, id: "p-3:29:2" })).toBeNull();
    expect(observationSource({ ...memory, observation_references: [] }, selection)).toBeNull();
  });
  it("round-trips exact missing references, fog and unrevealed outcomes without inventing a target", () => {
    const state = { ...parsePlaybackParams("?game_id=example&perspective=p-2&tick=28"), evidence: { ...target, id: "missing?&<>" } };
    expect(parsePlaybackParams(serializePlaybackParams(state))).toEqual(state);
    expect(parsePlaybackParams(serializePlaybackParams(state)).reveal).toBe(false);
  });
});
