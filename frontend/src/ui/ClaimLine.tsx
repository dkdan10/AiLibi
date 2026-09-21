// ClaimLine — discriminated render of one structured claim, shared across the
// meeting turn cards (every turn exposes `StatementClaimView[]`). Split out of
// `components/ContradictionBadge.tsx` in task 12.1 (DESIGN.md §6: the
// transcript-render primitives move into `ui/`). TypeScript narrows each `case`
// exhaustively. Behaviour unchanged; cream/ink restyle is a Wave-B slice.
//
// An alibi is a ROUTE. A claim recorded before that change carries the flat
// one-room envelope and still renders exactly as it always did; a route claim
// carries `route` and renders its legs in order, so a spectator sees the walk
// the speaker actually described instead of a single room it was squeezed into.
// The two surfaces are disjoint on the wire, so `route` is the discriminant.

import type { AlibiSegmentView, StatementClaimView } from "../types/api";

function alibiLegs(claim: Extract<StatementClaimView, { type: "alibi" }>):
  | AlibiSegmentView[]
  | null {
  if (claim.route != null && claim.route.length > 0) {
    return claim.route;
  }
  if (
    claim.room != null &&
    claim.from_tick != null &&
    claim.to_tick != null
  ) {
    return [
      { room: claim.room, from_tick: claim.from_tick, to_tick: claim.to_tick },
    ];
  }
  return null;
}

export function ClaimLine({ claim }: { claim: StatementClaimView }) {
  switch (claim.type) {
    case "alibi": {
      const legs = alibiLegs(claim);
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-ink-900">alibi</span> · {claim.subject}{" "}
          {legs === null ? (
            <span className="text-ink-500">(no route stated)</span>
          ) : (
            legs.map((leg, index) => (
              <span key={`${leg.room}-${leg.from_tick}-${leg.to_tick}`}>
                {index > 0 && <span className="text-ink-500"> → </span>}
                in {leg.room} (ticks {leg.from_tick}–{leg.to_tick})
              </span>
            ))
          )}
          {claim.evidence.length > 0 && (
            <span className="text-ink-500">
              {" "}
              · evidence: {claim.evidence.join(", ")}
            </span>
          )}
        </span>
      );
    }
    case "accusation":
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-ink-900">accusation</span> · against{" "}
          {claim.against} (confidence {claim.confidence.toFixed(2)}) — {claim.reason}
        </span>
      );
    case "corroboration":
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-ink-900">corroboration</span> ·
          supports {claim.supports} at tick {claim.on_tick} — {claim.reason}
        </span>
      );
  }
}
