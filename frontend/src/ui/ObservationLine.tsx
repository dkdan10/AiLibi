// ObservationLine — discriminated render of one structured observation, shared
// by the meeting turn cards and any consumer surfacing a turn's observations.
// Split out of `components/ContradictionBadge.tsx` in task 12.1 (DESIGN.md §6:
// the transcript-render primitives move into `ui/`). TypeScript narrows each
// `case` exhaustively. Behaviour unchanged; cream/ink restyle is a Wave-B slice.

import type { ObservationClaimView } from "../types/api";

export function ObservationLine({ obs }: { obs: ObservationClaimView }) {
  switch (obs.type) {
    case "saw_player":
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-ink-900">saw</span> {obs.subject} in{" "}
          {obs.room} at tick {obs.tick}
          {obs.co_present.length > 0 && (
            <span className="text-ink-500"> (with {obs.co_present.join(", ")})</span>
          )}
        </span>
      );
    case "completed_task":
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-ink-900">completed</span>{" "}
          {obs.task_id} in {obs.room} at tick {obs.tick}
        </span>
      );
    case "found_body":
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-ink-900">found body</span> of{" "}
          {obs.body_of} in {obs.room} at tick {obs.tick}
        </span>
      );
    case "saw_vent":
      // Task 15.4.1: the role-proving vent sighting. Role-neutral wording (no
      // hue) — the "impostor-only" meaning is carried by the vent_sighting
      // contradiction badge, not this line (firewall discipline).
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-ink-900">saw</span> {obs.subject}{" "}
          <span className="font-semibold text-ink-900">vent</span> in {obs.room} at
          tick {obs.tick}
        </span>
      );
  }
}
