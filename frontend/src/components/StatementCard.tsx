// One accusation-round statement (DESIGN.md §5.2, §5.3): speaker + optional
// target chip, foregrounded free text, and collapsed-by-default claims. Claims
// implicated in a contradiction show a badge inline; the union is also surfaced
// in the header so it stays visible while claims are collapsed.

import type { ContradictionView, PlayerView, StatementView } from "../types/api";
import {
  ClaimLine,
  ContradictionBadge,
  dedupeContradictions,
  findContradictions,
  PlayerChip,
  statementClaimEventId,
} from "./ContradictionBadge";

interface StatementCardProps {
  statement: StatementView;
  players: PlayerView[];
  contradictions: readonly ContradictionView[];
}

export function StatementCard({
  statement,
  players,
  contradictions,
}: StatementCardProps) {
  const claims = statement.claims.map((claim, index) => ({
    claim,
    contras: findContradictions(
      statementClaimEventId(statement, index),
      contradictions,
    ),
  }));
  const flagged = dedupeContradictions(claims.flatMap((c) => c.contras));

  return (
    <article className="rounded-lg border border-neutral-700 bg-neutral-800/40 p-4">
      <header className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1">
        <PlayerChip agentId={statement.speaker} players={players} />
        <span className="text-neutral-500">→</span>
        {statement.target !== null ? (
          <span className="inline-flex min-w-0 max-w-full items-center rounded bg-neutral-700/70 px-2 py-0.5">
            <PlayerChip agentId={statement.target} players={players} />
          </span>
        ) : (
          <span className="rounded bg-neutral-700/40 px-2 py-0.5 text-sm text-neutral-400">
            general
          </span>
        )}
        <span className="font-mono text-xs text-neutral-400">tick {statement.tick}</span>
        {flagged.map((c) => (
          <ContradictionBadge key={c.contradiction_id} contradiction={c} />
        ))}
      </header>

      <p className="whitespace-pre-wrap break-words text-base leading-relaxed text-neutral-100">
        {statement.free_text}
      </p>

      {claims.length > 0 && (
        <details className="mt-3 text-sm text-neutral-300">
          <summary className="cursor-pointer select-none text-neutral-400">
            Claims ({claims.length})
          </summary>
          <ul className="mt-2 space-y-1">
            {claims.map(({ claim, contras }, index) => (
              <li key={index} className="flex flex-wrap items-center gap-2">
                <span className="text-neutral-500">•</span>
                <ClaimLine claim={claim} />
                {contras.map((c) => (
                  <ContradictionBadge key={c.contradiction_id} contradiction={c} />
                ))}
              </li>
            ))}
          </ul>
        </details>
      )}
    </article>
  );
}
