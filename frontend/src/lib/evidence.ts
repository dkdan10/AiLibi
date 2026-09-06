/** Exact public evidence identities; never interpret an ID as a timestamp. */
import { observationEventId, turnClaimEventId } from "./contradictions";
import type { AgentMemoryView, MeetingView, ObservationReferenceView, TurnView, StatementClaimView, ObservationClaimView } from "../types/api";

export interface EvidenceSelection {
  kind: "statement" | "artifact" | "observation";
  id: string;
  meetingId: string;
  observerId: string | null;
}
export type StatementSource =
  | { turn: TurnView; kind: "statement" }
  | { turn: TurnView; kind: "claim"; value: StatementClaimView }
  | { turn: TurnView; kind: "observation"; value: ObservationClaimView };

export function statementSource(meeting: MeetingView, target: EvidenceSelection): StatementSource | null {
  for (const turn of meeting.turns) {
    if (target.kind === "statement" && turn.turn_id === target.id) return { turn, kind: "statement" };
    if (target.kind !== "artifact") continue;
    for (const [index, value] of turn.claims.entries()) {
      if (turnClaimEventId(turn, index) === target.id) return { turn, kind: "claim", value };
    }
    for (const [index, value] of turn.observations.entries()) {
      if (observationEventId(turn, value, index) === target.id) return { turn, kind: "observation", value };
    }
  }
  return null;
}

export function observationSource(memory: AgentMemoryView | undefined, target: EvidenceSelection): ObservationReferenceView | null {
  if (memory?.agent_id !== target.observerId) return null;
  return memory.observation_references?.find((row) => row.observer_id === target.observerId && row.observation_id === target.id && row.resolved) ?? null;
}

/** A malformed link stays an explicit missing target; an absent link stays absent. */
export function parseEvidence(params: URLSearchParams): EvidenceSelection | null {
  const id = params.get("evidenceId");
  const meetingId = params.get("evidenceMeeting");
  const kind = params.get("evidenceKind");
  if (id === null || meetingId === null || (kind !== "statement" && kind !== "artifact" && kind !== "observation")) return null;
  return { id, meetingId, kind, observerId: params.get("evidenceObserver") };
}

export function evidenceDomId(id: string): string { return `evidence-${encodeURIComponent(id)}`; }
