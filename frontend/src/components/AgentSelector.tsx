// The affordance for picking which agent's reasoning ThoughtStream shows
// (DESIGN.md §6, §7). One button per player in the current replay: color swatch
// + display name + agent id + a muted role tag. Role is privileged-spectator
// info (4.1 model) so it is shown without guarding. Visible only while a meeting
// is selected — outside a meeting there is no ThoughtStream context to pick for.

import { useReplayStore } from "../store/replayStore";

export function AgentSelector() {
  const replay = useReplayStore((s) => s.currentReplay);
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const selectedAgentId = useReplayStore((s) => s.selectedAgentId);
  const selectAgent = useReplayStore((s) => s.selectAgent);

  if (meetingId === null || replay === null) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-2" role="group" aria-label="Select an agent">
      {replay.players.map((player) => {
        const isSelected = player.agent_id === selectedAgentId;
        return (
          <button
            key={player.agent_id}
            type="button"
            aria-pressed={isSelected}
            onClick={() => {
              selectAgent(player.agent_id);
            }}
            className={
              "flex items-center gap-1.5 rounded border px-2 py-1 text-left text-sm transition-colors " +
              (isSelected
                ? "border-emerald-500 bg-emerald-900/50 text-emerald-100"
                : "border-neutral-700 bg-neutral-800 text-neutral-100 hover:bg-neutral-700")
            }
          >
            <span
              aria-hidden
              className="inline-block h-3 w-3 shrink-0 rounded-full ring-1 ring-black/50"
              style={{ backgroundColor: player.color }}
            />
            <span className="font-medium">{player.display_name}</span>
            <span className="font-mono text-xs text-neutral-400">{player.agent_id}</span>
            <span className="text-[10px] uppercase tracking-wide text-neutral-500">
              ({player.role})
            </span>
          </button>
        );
      })}
    </div>
  );
}
