// Per-agent reasoning viewer (DESIGN.md §6, §7). A right-rail companion to an
// open meeting: pick an agent and see that agent's meeting-boundary memory plus
// every LLM call it originated during the meeting. Memory comes from the store's
// AgentMemoryView cache (MemoryPanel); LLM calls come from MeetingView.llm_calls
// filtered by the per-call agent_id that Task 4.7 added.
//
// Layout (implementing agent's choice; see PR ## Decisions): a fixed right rail
// (~30vw, clamped) at a higher z-index than the meeting modal so MapView and the
// MeetingView overlay both stay visible while drilling into an agent. The rail
// mounts iff a meeting is selected — the AgentSelector is meeting-gated by the
// contract, and outside a meeting there is no ThoughtStream context, so the rail
// stays hidden rather than floating an empty panel over the map.

import { useReplayStore } from "../store/replayStore";
import type { MeetingView as MeetingViewDTO } from "../types/api";
import { AgentSelector } from "./AgentSelector";
import { LLMCallCard } from "./LLMCallCard";
import { MemoryPanel } from "./MemoryPanel";

function LLMCallList({
  meeting,
  agentId,
}: {
  meeting: MeetingViewDTO | undefined;
  agentId: string;
}) {
  const calls = meeting?.llm_calls ?? [];
  const attributed = calls.filter((call) => call.agent_id === agentId);
  // Pre-4.7 replays captured no per-call agent_id; surface one notice rather
  // than an empty list so the spectator knows attribution is unavailable.
  const hasUnattributed = calls.some((call) => call.agent_id === null);

  return (
    <section>
      <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-neutral-400">
        LLM calls ({attributed.length})
      </h3>
      {attributed.length > 0 ? (
        <div className="space-y-2">
          {attributed.map((call, index) => (
            <LLMCallCard key={`${call.prompt_template_id}#${index}`} call={call} />
          ))}
        </div>
      ) : hasUnattributed ? (
        <p className="rounded border border-amber-700/60 bg-amber-950/40 px-3 py-2 text-xs text-amber-200">
          Older replay — per-call agent attribution unavailable.
        </p>
      ) : (
        <p className="text-xs italic text-neutral-500">
          No LLM calls recorded for this agent in this meeting.
        </p>
      )}
    </section>
  );
}

export function ThoughtStream() {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const agentId = useReplayStore((s) => s.selectedAgentId);
  const replay = useReplayStore((s) => s.currentReplay);

  if (meetingId === null || replay === null) {
    return null;
  }

  const meeting = replay.meetings.find((m) => m.meeting_id === meetingId);

  return (
    <aside
      aria-label="ThoughtStream — agent reasoning"
      className="fixed right-0 top-0 z-[60] flex h-screen w-[30vw] min-w-[300px] max-w-[20rem] flex-col overflow-y-auto border-l border-neutral-700 bg-neutral-900/95 p-4 text-neutral-100 shadow-2xl backdrop-blur"
    >
      <header className="mb-3">
        <h2 className="text-lg font-bold">ThoughtStream</h2>
        <p className="text-xs text-neutral-400">
          Per-agent memory + LLM calls for the selected meeting.
        </p>
      </header>

      <AgentSelector />

      {agentId === null ? (
        <p className="mt-6 text-sm italic text-neutral-400">
          Open a meeting and pick an agent to see their reasoning.
        </p>
      ) : (
        <>
          <div className="mt-4">
            <MemoryPanel meetingId={meetingId} agentId={agentId} />
          </div>
          <hr className="my-4 border-neutral-700" />
          <LLMCallList meeting={meeting} agentId={agentId} />
        </>
      )}
    </aside>
  );
}
