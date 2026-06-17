// Contradiction matching + event-id helpers shared by the meeting cards.
// Split out of `components/ContradictionBadge.tsx` in task 12.1 (DESIGN.md §6:
// "Split `ContradictionBadge.tsx`'s smuggled utils into `lib/`") so the badge
// component is no longer the catch-all leaf for non-presentational logic.

import type { ContradictionView, TurnView } from "../types/api";

// Event-id construction mirrors `meetings/transcript.py` exactly (the
// `_turn_claim_id` / `_turn_observation_id` helpers): a contradiction references
// the structured artifact that produced it as `turn:<turn_id>:claim:<index>` or
// `turn:<turn_id>:obs:<index>`, so we reconstruct those ids and match on them.
export function turnClaimEventId(turn: TurnView, index: number): string {
  return `turn:${turn.turn_id}:claim:${index}`;
}

export function turnObsEventId(turn: TurnView, index: number): string {
  return `turn:${turn.turn_id}:obs:${index}`;
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
