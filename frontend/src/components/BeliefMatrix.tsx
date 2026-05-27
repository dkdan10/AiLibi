// N×N "who suspects whom" heatmap (DESIGN.md §6.3, §7). Rows are observers,
// columns are subjects; each cell is the row agent's suspicion of the column
// agent at the selected meeting boundary. Derived entirely client-side from the
// per-agent `AgentMemoryView` snapshots the store already caches — no backend
// endpoint (see tasks/phase-4.md Task 4.10, "Why meeting-boundary-only").
//
// Like ThoughtStream it has meaning only while a meeting is selected, and it
// mounts as a fixed rail (here: left) at a z-index above the MeetingView modal
// (z-50). A matrix in normal document flow would be hidden behind that modal
// for the entire time a meeting is selected — the only state in which it has
// data — so the rail is what makes "visible when a meeting is selected" true.

import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { useReplayStore } from "../store/replayStore";
import type { AgentMemoryView, BeliefEntryView, PlayerView } from "../types/api";
import { BeliefCell } from "./BeliefCell";

// Stable empty roster so the fetch effect doesn't re-fire while no replay is
// loaded (a fresh `[]` literal would be a new dependency every render).
const EMPTY_PLAYERS: readonly PlayerView[] = [];

// Mirrors the store's private memory-cache key format (replayStore.ts).
function memoryKey(meetingId: string, agentId: string): string {
  return `${meetingId}:${agentId}`;
}

function lookupBelief(
  memory: AgentMemoryView,
  subjectId: string,
): BeliefEntryView | undefined {
  return memory.beliefs.find((belief) => belief.subject === subjectId);
}

// Which agents' fetches have resolved (success or error) for a given meeting.
// The store leaves the cache key unset on a failed fetch, so "settled" — not
// "present in cache" — is what tells us loading is done.
interface SettledState {
  meetingId: string;
  agentIds: ReadonlySet<string>;
}

function Rail({ children }: { children: ReactNode }) {
  return (
    <aside
      aria-label="BeliefMatrix — who suspects whom"
      className="fixed left-0 top-0 z-[55] flex h-screen w-fit min-w-[320px] max-w-[42vw] flex-col overflow-auto border-r border-neutral-700 bg-neutral-900/95 p-4 text-neutral-100 shadow-2xl backdrop-blur"
    >
      <header className="mb-3">
        <h2 className="text-lg font-bold">BeliefMatrix</h2>
        <p className="text-xs text-neutral-400">
          Who suspects whom at the selected meeting. Rows observe; columns are
          suspected.
        </p>
      </header>
      {children}
    </aside>
  );
}

function AxisLabel({
  player,
  errored = false,
}: {
  player: PlayerView;
  errored?: boolean;
}) {
  return (
    <span className="inline-flex items-center gap-1 whitespace-nowrap">
      <span
        aria-hidden
        className="inline-block h-3 w-3 shrink-0 rounded-full ring-1 ring-black/50"
        style={{ backgroundColor: player.color }}
      />
      <span className="font-mono text-xs text-neutral-200">
        {player.agent_id}
      </span>
      {errored && (
        <span
          title="memory failed to load"
          className="rounded bg-red-900/70 px-1 text-[10px] font-semibold text-red-200 ring-1 ring-red-700/60"
        >
          err
        </span>
      )}
    </span>
  );
}

function HeatLegend() {
  return (
    <div className="mt-3 flex items-center gap-2 text-[10px] text-neutral-400">
      <span>less suspicious</span>
      <span
        aria-hidden
        className="h-2 w-24 rounded"
        style={{
          background:
            "linear-gradient(to right, hsl(120, 70%, 40%), hsl(60, 70%, 40%), hsl(0, 70%, 40%))",
        }}
      />
      <span>more suspicious</span>
    </div>
  );
}

function Loading() {
  return (
    <div className="flex items-center gap-2 py-2 text-sm text-neutral-400">
      <span
        aria-hidden
        className="h-4 w-4 animate-spin rounded-full border-2 border-neutral-600 border-t-neutral-200"
      />
      Loading agent memories…
    </div>
  );
}

export function BeliefMatrix() {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const replay = useReplayStore((s) => s.currentReplay);
  const memoryCache = useReplayStore((s) => s.memoryCache);
  const fetchMemoryView = useReplayStore((s) => s.fetchMemoryView);

  const players = replay?.players ?? EMPTY_PLAYERS;

  const [settled, setSettled] = useState<SettledState | null>(null);

  // Fan out one memory fetch per player at the selected meeting. The store
  // caches + dedupes, so this is cheap on re-selection. We mark each agent
  // settled once its fetch resolves (success or error) so the matrix can leave
  // the loading state even when some fetches failed.
  useEffect(() => {
    if (meetingId === null) {
      setSettled(null);
      return;
    }
    let cancelled = false;
    setSettled({ meetingId, agentIds: new Set() });
    for (const player of players) {
      const agentId = player.agent_id;
      void fetchMemoryView(meetingId, agentId).finally(() => {
        if (cancelled) {
          return;
        }
        setSettled((prev) => {
          if (prev === null || prev.meetingId !== meetingId) {
            return prev;
          }
          if (prev.agentIds.has(agentId)) {
            return prev;
          }
          const agentIds = new Set(prev.agentIds);
          agentIds.add(agentId);
          return { meetingId, agentIds };
        });
      });
    }
    return () => {
      cancelled = true;
    };
  }, [meetingId, players, fetchMemoryView]);

  // Data-integrity hint (DESIGN.md §6.3): every belief in an AgentMemoryView is
  // snapshotted at the meeting tick, so all snapshot_tick values across the
  // matrix must agree. Warn (don't throw) if they ever diverge.
  useEffect(() => {
    if (meetingId === null) {
      return;
    }
    const ticks: number[] = [];
    for (const player of players) {
      const memory = memoryCache[memoryKey(meetingId, player.agent_id)];
      if (memory) {
        for (const belief of memory.beliefs) {
          ticks.push(belief.snapshot_tick);
        }
      }
    }
    if (new Set(ticks).size > 1) {
      console.warn(
        "BeliefMatrix: snapshot_tick values diverge across cells",
        ticks,
      );
    }
  }, [meetingId, players, memoryCache]);

  if (meetingId === null) {
    return null;
  }

  if (players.length === 0) {
    return (
      <Rail>
        <p className="text-sm italic text-neutral-400">
          No players in this replay.
        </p>
      </Rail>
    );
  }

  const allSettled =
    settled !== null &&
    settled.meetingId === meetingId &&
    players.every((player) => settled.agentIds.has(player.agent_id));

  if (!allSettled) {
    return (
      <Rail>
        <Loading />
      </Rail>
    );
  }

  // After all fetches settle, the meeting tick is the tick of any loaded
  // snapshot (all equal by construction — see the integrity check above).
  let footerTick: number | null = null;
  for (const player of players) {
    const memory = memoryCache[memoryKey(meetingId, player.agent_id)];
    if (memory) {
      footerTick = memory.tick;
      break;
    }
  }

  return (
    <Rail>
      <div className="overflow-auto">
        <table className="border-separate border-spacing-1">
          <caption className="sr-only">
            Suspicion from each observer (row) toward each subject (column).
          </caption>
          <thead>
            <tr>
              <th scope="col" className="p-1 text-left">
                <span className="text-[10px] font-normal uppercase tracking-wide text-neutral-500">
                  obs ↓ \ subj →
                </span>
              </th>
              {players.map((subject) => (
                <th key={subject.agent_id} scope="col" className="p-1">
                  <AxisLabel player={subject} />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {players.map((observer) => {
              const memory =
                memoryCache[memoryKey(meetingId, observer.agent_id)];
              return (
                <tr key={observer.agent_id}>
                  <th scope="row" className="p-1 text-left">
                    <AxisLabel
                      player={observer}
                      errored={memory === undefined}
                    />
                  </th>
                  {players.map((subject) => (
                    <td key={subject.agent_id} className="p-0">
                      <BeliefCell
                        observer={observer}
                        subject={subject}
                        belief={
                          memory
                            ? lookupBelief(memory, subject.agent_id)
                            : undefined
                        }
                      />
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <HeatLegend />

      <p className="mt-3 text-xs text-neutral-400">
        {footerTick === null
          ? "No agent memories loaded for this meeting."
          : `All beliefs as of meeting tick ${footerTick}.`}
      </p>
    </Rail>
  );
}
