// ClaimLine — discriminated render of one structured claim, shared across the
// meeting turn cards (every turn exposes `StatementClaimView[]`). Split out of
// `components/ContradictionBadge.tsx` in task 12.1 (DESIGN.md §6: the
// transcript-render primitives move into `ui/`). TypeScript narrows each `case`
// exhaustively. Behaviour unchanged; cream/ink restyle is a Wave-B slice.

import type { StatementClaimView } from "../types/api";

export function ClaimLine({ claim }: { claim: StatementClaimView }) {
  switch (claim.type) {
    case "alibi":
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-sky-300">alibi</span> · {claim.subject}{" "}
          in {claim.room} (ticks {claim.from_tick}–{claim.to_tick})
          {claim.evidence.length > 0 && (
            <span className="text-neutral-400">
              {" "}
              · evidence: {claim.evidence.join(", ")}
            </span>
          )}
        </span>
      );
    case "accusation":
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-rose-300">accusation</span> · against{" "}
          {claim.against} (confidence {claim.confidence.toFixed(2)}) — {claim.reason}
        </span>
      );
    case "corroboration":
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-emerald-300">corroboration</span> ·
          supports {claim.supports} at tick {claim.on_tick} — {claim.reason}
        </span>
      );
  }
}
