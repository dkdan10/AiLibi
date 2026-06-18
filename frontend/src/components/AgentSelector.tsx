// The agent picker folded into the mind inspector (Task 12.8; was the
// standalone ThoughtStream selector). One chip per player in the current replay:
// identity swatch + display name + agent id. Presentational — the connected
// MindInspector passes the roster, the selection, and the `onSelect` handler.
//
// Firewall: the chip shows IDENTITY ONLY (swatch + id), never a role tag. Role
// is the ground-truth reveal and is gated in the inspector header (Omniscient or
// self-lens) — surfacing it here, for every roster member at once, would leak
// every agent's alignment regardless of perspective.

import type { PlayerView } from "../types/api";

interface AgentSelectorProps {
  players: PlayerView[];
  selectedAgentId: string | null;
  onSelect: (agentId: string) => void;
}

export function AgentSelector({
  players,
  selectedAgentId,
  onSelect,
}: AgentSelectorProps) {
  return (
    <div className="flex flex-wrap gap-1.5" role="group" aria-label="Select an agent">
      {players.map((player) => {
        const isSelected = player.agent_id === selectedAgentId;
        return (
          <button
            key={player.agent_id}
            type="button"
            aria-pressed={isSelected}
            onClick={() => {
              onSelect(player.agent_id);
            }}
            className={
              "flex items-center gap-1.5 rounded-md border-2 px-2 py-1 text-left text-sm font-medium transition-colors " +
              (isSelected
                ? "border-ink-900 bg-paper-0 text-ink-900 shadow-chrome-1"
                : "border-ink-300 bg-paper-1 text-ink-700 hover:border-ink-900 hover:bg-paper-0")
            }
          >
            <span
              aria-hidden
              className="inline-block h-3 w-3 shrink-0 rounded-full ring-2 ring-ink-900"
              style={{ backgroundColor: player.color }}
            />
            <span>{player.display_name}</span>
            <span className="font-mono text-[10px] text-ink-400">{player.agent_id}</span>
          </button>
        );
      })}
    </div>
  );
}
