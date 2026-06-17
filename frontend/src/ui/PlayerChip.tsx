// PlayerChip — colour swatch + readable display name + the raw agent id.
// Split out of `components/ContradictionBadge.tsx` in task 12.1 (DESIGN.md §6
// lists PlayerChip among the `ui/` primitives). Behaviour is unchanged: the
// swatch uses the player's API-provided identity colour (`PlayerView.color`);
// re-pointing it at the `tokens.identity[]` palette is Task 12.2's job, and the
// cream/ink restyle is a later Wave-B slice.

import type { PlayerView } from "../types/api";

const FALLBACK_COLOR = "#888888";

function playerColor(agentId: string, players: PlayerView[]): string {
  return players.find((p) => p.agent_id === agentId)?.color ?? FALLBACK_COLOR;
}

function playerName(agentId: string, players: PlayerView[]): string {
  return players.find((p) => p.agent_id === agentId)?.display_name ?? agentId;
}

interface PlayerChipProps {
  agentId: string;
  players: PlayerView[];
}

// The DoD references the agent/voter id explicitly, so it is always shown
// alongside the name.
export function PlayerChip({ agentId, players }: PlayerChipProps) {
  return (
    <span className="inline-flex min-w-0 max-w-full items-center gap-1.5 align-middle">
      <span
        aria-hidden
        className="inline-block h-3 w-3 shrink-0 rounded-full ring-1 ring-black/50"
        style={{ backgroundColor: playerColor(agentId, players) }}
      />
      <span className="min-w-0 break-words font-medium text-neutral-100">
        {playerName(agentId, players)}
      </span>
      <span className="min-w-0 break-all font-mono text-xs text-neutral-400">
        {agentId}
      </span>
    </span>
  );
}
