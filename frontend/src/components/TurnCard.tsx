// One turn of the reactive accusation chain (DESIGN.md §5.2, §5.3): a turn-kind
// badge + speaker + optional accusation target / reply cue, foregrounded free
// text, and collapsed-by-default structured observations + claims. Any
// observation/claim implicated in a contradiction shows a badge inline; the
// union is also surfaced in the header so it stays visible while the detail is
// collapsed. This single card replaces the old ReportCard (opening report) +
// StatementCard split — the chain has exactly one turn type, carrying both
// observations and claims (Task 8.7/8.10).

import {
  dedupeContradictions,
  findContradictions,
  turnClaimEventId,
  turnObsEventId,
} from "../lib/contradictions";
import type { ContradictionView, PlayerView, TurnView } from "../types/api";
import { ClaimLine } from "../ui/ClaimLine";
import { ObservationLine } from "../ui/ObservationLine";
import { PlayerChip } from "../ui/PlayerChip";
import { ContradictionBadge } from "./ContradictionBadge";

interface TurnCardProps {
  turn: TurnView;
  players: PlayerView[];
  contradictions: readonly ContradictionView[];
}

const TURN_KIND_LABELS: Record<TurnView["turn_kind"], string> = {
  opening: "opening",
  reply: "reply",
  opt_in: "opt-in",
};

export function TurnCard({ turn, players, contradictions }: TurnCardProps) {
  const observations = turn.observations.map((obs, index) => ({
    obs,
    contras: findContradictions(turnObsEventId(turn, index), contradictions),
  }));
  const claims = turn.claims.map((claim, index) => ({
    claim,
    contras: findContradictions(turnClaimEventId(turn, index), contradictions),
  }));
  const flagged = dedupeContradictions([
    ...observations.flatMap((o) => o.contras),
    ...claims.flatMap((c) => c.contras),
  ]);
  const detailCount = observations.length + claims.length;
  // The chain's "target" is the turn's first accusation claim (mirrors
  // meetings.transcript.accusation_target); shown as a chip when present.
  const accusation = turn.claims.find((claim) => claim.type === "accusation");
  const target = accusation?.against ?? null;

  return (
    <article className="rounded-lg border border-neutral-700 bg-neutral-800/50 p-4">
      <header className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1">
        <span className="rounded bg-neutral-700/70 px-1.5 py-0.5 font-mono text-xs uppercase tracking-wide text-neutral-300">
          {TURN_KIND_LABELS[turn.turn_kind]}
        </span>
        <PlayerChip agentId={turn.speaker} players={players} />
        {target !== null ? (
          <>
            <span className="text-neutral-500">→</span>
            <span className="inline-flex min-w-0 max-w-full items-center rounded bg-neutral-700/70 px-2 py-0.5">
              <PlayerChip agentId={target} players={players} />
            </span>
          </>
        ) : (
          <span className="rounded bg-neutral-700/40 px-2 py-0.5 text-sm text-neutral-400">
            no accusation
          </span>
        )}
        {turn.reply_to !== null && (
          <span className="min-w-0 break-all font-mono text-xs text-neutral-500">
            ↳ {turn.reply_to}
          </span>
        )}
        {flagged.map((c) => (
          <ContradictionBadge key={c.contradiction_id} contradiction={c} />
        ))}
      </header>

      <p className="whitespace-pre-wrap break-words text-base leading-relaxed text-neutral-100">
        {turn.free_text}
      </p>

      {detailCount > 0 && (
        <details className="mt-3 text-sm text-neutral-300">
          <summary className="cursor-pointer select-none text-neutral-400">
            Structured detail ({observations.length} observation
            {observations.length === 1 ? "" : "s"}, {claims.length} claim
            {claims.length === 1 ? "" : "s"})
          </summary>
          <div className="mt-2 space-y-3">
            {observations.length > 0 && (
              <ul className="space-y-1">
                {observations.map(({ obs, contras }, index) => (
                  <li
                    key={`obs-${index}`}
                    className="flex flex-wrap items-center gap-2"
                  >
                    <span className="text-neutral-500">•</span>
                    <ObservationLine obs={obs} />
                    {contras.map((c) => (
                      <ContradictionBadge
                        key={c.contradiction_id}
                        contradiction={c}
                      />
                    ))}
                  </li>
                ))}
              </ul>
            )}
            {claims.length > 0 && (
              <ul className="space-y-1">
                {claims.map(({ claim, contras }, index) => (
                  <li
                    key={`claim-${index}`}
                    className="flex flex-wrap items-center gap-2"
                  >
                    <span className="text-neutral-500">•</span>
                    <ClaimLine claim={claim} />
                    {contras.map((c) => (
                      <ContradictionBadge
                        key={c.contradiction_id}
                        contradiction={c}
                      />
                    ))}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </details>
      )}
    </article>
  );
}
