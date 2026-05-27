// One vote ballot (DESIGN.md §5.5): voter + target (a player chip or the
// neutral literal "SKIP"), a confidence bar (0.0–1.0), and the foregrounded
// rationale text.

import type { BallotView, PlayerView } from "../types/api";
import { PlayerChip } from "./ContradictionBadge";

interface BallotCardProps {
  ballot: BallotView;
  players: PlayerView[];
}

export function BallotCard({ ballot, players }: BallotCardProps) {
  const isSkip = ballot.target === "SKIP";
  const confidence = Math.max(0, Math.min(1, ballot.confidence));
  const pct = Math.round(confidence * 100);

  return (
    <article className="rounded-lg border border-neutral-700 bg-neutral-800/40 p-4">
      <header className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1">
        <PlayerChip agentId={ballot.voter} players={players} />
        <span className="text-neutral-500">voted</span>
        {isSkip ? (
          <span className="rounded bg-neutral-700/60 px-2 py-0.5 text-sm font-semibold text-neutral-300">
            SKIP
          </span>
        ) : (
          <span className="inline-flex items-center rounded bg-neutral-700/70 px-2 py-0.5">
            <PlayerChip agentId={ballot.target} players={players} />
          </span>
        )}
      </header>

      <div className="mb-2 flex items-center gap-2">
        <span className="w-20 shrink-0 text-xs text-neutral-400">confidence</span>
        <div className="h-2 flex-1 overflow-hidden rounded bg-neutral-700">
          <div
            className="h-full rounded bg-sky-500"
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className="w-10 shrink-0 text-right font-mono text-xs text-neutral-300">
          {ballot.confidence.toFixed(2)}
        </span>
      </div>

      <p className="whitespace-pre-wrap text-sm leading-relaxed text-neutral-100">
        {ballot.rationale_text}
      </p>
    </article>
  );
}
