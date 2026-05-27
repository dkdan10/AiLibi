// Renders one agent's meeting-boundary memory snapshot (DESIGN.md §6.6). Mirrors
// the rendered prompt blocks: role, tasks-completed, recent observations, current
// beliefs, open contradictions — plus the raw rendered text in a collapsible for
// prompt-render debugging. Memory is fetched lazily into the store cache; this
// panel owns the loading + error display.

import { useEffect } from "react";
import type { ReactNode } from "react";

import { useReplayStore } from "../store/replayStore";
import type { ObservationClaimView, PlayerRole } from "../types/api";
import { BeliefRow } from "./BeliefRow";
import { ContradictionBadge } from "./ContradictionBadge";

// Mirrors the store's private memory-cache key format (replayStore.ts).
function memoryKey(meetingId: string, agentId: string): string {
  return `${meetingId}:${agentId}`;
}

// Role is exposed by design (privileged post-game spectator, 4.1 model); the
// chip is color-coded since this view is explicitly about one chosen agent.
const ROLE_STYLES: Record<PlayerRole, string> = {
  CREWMATE: "bg-sky-900/60 text-sky-200 ring-sky-600/60",
  IMPOSTOR: "bg-rose-900/60 text-rose-200 ring-rose-600/60",
};

function RoleBadge({ role }: { role: PlayerRole }) {
  return (
    <span
      className={
        "inline-flex items-center rounded px-2 py-0.5 text-xs font-bold uppercase tracking-wide ring-1 " +
        ROLE_STYLES[role]
      }
    >
      {role}
    </span>
  );
}

function ObservationLine({ obs }: { obs: ObservationClaimView }) {
  switch (obs.type) {
    case "saw_player":
      return (
        <span>
          <span className="font-semibold text-amber-300">saw</span> {obs.subject} in{" "}
          {obs.room} at tick {obs.tick}
          {obs.co_present.length > 0 && (
            <span className="text-neutral-400"> (with {obs.co_present.join(", ")})</span>
          )}
        </span>
      );
    case "completed_task":
      return (
        <span>
          <span className="font-semibold text-amber-300">completed</span> {obs.task_id}{" "}
          in {obs.room} at tick {obs.tick}
        </span>
      );
    case "found_body":
      return (
        <span>
          <span className="font-semibold text-amber-300">found body</span> of{" "}
          {obs.body_of} in {obs.room} at tick {obs.tick}
        </span>
      );
  }
}

function SectionHeading({ children }: { children: ReactNode }) {
  return (
    <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-neutral-400">
      {children}
    </h4>
  );
}

interface MemoryPanelProps {
  meetingId: string;
  agentId: string;
}

export function MemoryPanel({ meetingId, agentId }: MemoryPanelProps) {
  const memoryCache = useReplayStore((s) => s.memoryCache);
  const fetchMemoryView = useReplayStore((s) => s.fetchMemoryView);
  // The frozen store has no dedicated memory-error field; a failed memory fetch
  // surfaces on `currentReplayError`. Once a replay is loaded and a meeting +
  // agent are selected, that error is the memory fetch's.
  const error = useReplayStore((s) => s.currentReplayError);

  useEffect(() => {
    void fetchMemoryView(meetingId, agentId);
  }, [meetingId, agentId, fetchMemoryView]);

  const memory = memoryCache[memoryKey(meetingId, agentId)];

  if (memory === undefined) {
    if (error !== null) {
      return (
        <p className="rounded border border-red-700 bg-red-950 px-3 py-2 text-sm text-red-200">
          Failed to load memory: {error}
        </p>
      );
    }
    return (
      <div className="flex items-center gap-2 py-4 text-sm text-neutral-400">
        <span
          aria-hidden
          className="h-4 w-4 animate-spin rounded-full border-2 border-neutral-600 border-t-neutral-200"
        />
        Loading memory…
      </div>
    );
  }

  // The DTO arrives salience-ordered; the contract asks for newest-first here,
  // so re-sort by tick descending for display.
  const observations = [...memory.observations].sort((a, b) => b.tick - a.tick);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <RoleBadge role={memory.role} />
        <span className="text-xs text-neutral-400">
          tasks{" "}
          <span className="font-mono text-neutral-200">
            {memory.tasks_completed} / {memory.tasks_assigned}
          </span>
        </span>
      </div>

      <section>
        <SectionHeading>Observations ({observations.length})</SectionHeading>
        {observations.length === 0 ? (
          <p className="text-xs italic text-neutral-500">No observations.</p>
        ) : (
          <ul className="space-y-1">
            {observations.map((obs, index) => (
              <li
                key={`obs-${index}`}
                className="flex items-start gap-2 text-sm text-neutral-200"
              >
                <span className="text-neutral-600">•</span>
                <ObservationLine obs={obs} />
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <SectionHeading>Beliefs ({memory.beliefs.length})</SectionHeading>
        {memory.beliefs.length === 0 ? (
          <p className="text-xs italic text-neutral-500">No beliefs yet.</p>
        ) : (
          <div className="space-y-1.5">
            {memory.beliefs.map((belief) => (
              <BeliefRow key={belief.subject} belief={belief} />
            ))}
          </div>
        )}
      </section>

      <section>
        <SectionHeading>
          Open contradictions ({memory.open_contradictions.length})
        </SectionHeading>
        {memory.open_contradictions.length === 0 ? (
          <p className="text-xs italic text-neutral-500">None.</p>
        ) : (
          <ul className="space-y-1.5">
            {memory.open_contradictions.map((contradiction) => (
              <li
                key={contradiction.contradiction_id}
                className="flex flex-wrap items-center gap-2 text-xs text-neutral-300"
              >
                <ContradictionBadge contradiction={contradiction} />
                <span>{contradiction.description}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <details className="rounded border border-neutral-700 bg-neutral-900/60">
        <summary className="cursor-pointer select-none px-2 py-1 text-xs font-semibold uppercase tracking-wide text-neutral-400">
          Raw rendered memory (sent to LLM)
        </summary>
        <pre className="max-h-96 overflow-auto whitespace-pre-wrap break-words border-t border-neutral-700 px-2 py-2 font-mono text-xs text-neutral-200">
          {memory.rendered_memory_text}
        </pre>
      </details>
    </div>
  );
}
