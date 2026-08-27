// Contradiction matching + event-id helpers shared by the meeting cards, held
// here rather than in the badge so that leaf stays presentational.
// Split from `components/ContradictionBadge.tsx` in task 12.1 (DESIGN.md §6).

import type { ContradictionView, ObservationClaimView, TurnView } from "../types/api";

/**
 * Every segment a contradiction endpoint can carry, and the ONE place the
 * vocabulary is written down: `MeetingView`'s turn-id parser builds its pattern
 * from this list, so a segment cannot be taught to one reader and not the other.
 */
export const OBSERVATION_EVENT_SEGMENTS = ["claim", "obs", "whereabouts"] as const;

/** A segment the list above does not name will not compile below. */
type EventSegment = (typeof OBSERVATION_EVENT_SEGMENTS)[number];

// A contradiction references the structured artifact that produced it by id, so
// the cards reconstruct those ids and match on them. The ids mirror the three
// minters in `meetings/transcript.py`: `_turn_claim_id` writes
// `turn:<turn_id>:claim:<index>` for a spoken claim, and an observation splits —
// `_turn_whereabouts_id` writes `turn:<turn_id>:whereabouts:<index>` for a
// roll-call self-placement, `_turn_observation_id` writes
// `turn:<turn_id>:obs:<index>` for every other kind. The split is exclusive on
// both sides, so a whereabouts row is never addressable as `:obs:`.
function turnEventId(turn: TurnView, segment: EventSegment, index: number): string {
  return `turn:${turn.turn_id}:${segment}:${index}`;
}

export function turnClaimEventId(turn: TurnView, index: number): string {
  return turnEventId(turn, "claim", index);
}

/** An observation's id, dispatched on the discriminant the DTO carries. */
export function observationEventId(
  turn: TurnView,
  observation: ObservationClaimView,
  index: number,
): string {
  return turnEventId(turn, observation.type === "whereabouts" ? "whereabouts" : "obs", index);
}

export function findContradictions(
  eventId: string,
  contradictions: readonly ContradictionView[],
): ContradictionView[] {
  return contradictions.filter(
    (c) => c.event_a_id === eventId || c.event_b_id === eventId,
  );
}

// A single contradiction can implicate two events on one card (e.g. two
// conflicting alibi claims in the same report); dedupe by id for the always-on
// card-header summary.
export function dedupeContradictions(
  items: readonly ContradictionView[],
): ContradictionView[] {
  const seen = new Set<string>();
  const out: ContradictionView[] = [];
  for (const c of items) {
    if (!seen.has(c.contradiction_id)) {
      seen.add(c.contradiction_id);
      out.push(c);
    }
  }
  return out;
}
