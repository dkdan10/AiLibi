// The mind inspector's MEMORY tab (Task 12.8; was the standalone memory snapshot
// rail). Renders one agent's episodic feed from `AgentMemoryView` — the
// observations the agent actually logged (saw_player / saw_body→found_body /
// heard_* surface as the discriminated `ObservationClaimView`), the task tally,
// and the raw rendered memory text the LLM was handed (mono, collapsible).
//
// Firewall (gated by the connected inspector, passed as `revealSecrets`):
//   • an IMPOSTOR's completed_task observations are FABRICATED cover, labelled as
//     such — but ONLY when the secret is revealable (Omniscient or self-lens);
//     through a different agent's eyes the cover reads as a genuine task (the lie
//     working), so no "fabricated" badge leaks the impostor's hand;
//   • the `own_kill` lines and the fellow-impostor roster are impostor secrets,
//     shown under the same Omniscient-OR-self gate and suppressed otherwise.
// Presentational: the connected MindInspector owns the fetch + the gate.

import type { ReactNode } from "react";

import { tokens } from "../tokens";
import type {
  AgentMemoryView,
  KillEventView,
  ObservationClaimView,
  PlayerView,
} from "../types/api";

function SectionHeading({ children }: { children: ReactNode }) {
  return (
    <h4 className="mb-1.5 font-mono text-[10px] font-semibold uppercase tracking-wide text-ink-500">
      {children}
    </h4>
  );
}

function Empty({ children }: { children: ReactNode }) {
  return <p className="text-xs italic text-ink-400">{children}</p>;
}

// A fabricated impostor cover-task is flagged here; every other observation
// renders verbatim. `fabricated` is only ever true under the reveal gate.
function ObservationLine({
  obs,
  fabricated,
}: {
  obs: ObservationClaimView;
  fabricated: boolean;
}) {
  switch (obs.type) {
    case "saw_player":
      return (
        <span className="min-w-0 break-words text-ink-900">
          <span className="font-semibold">saw</span> {obs.subject} in {obs.room} at
          tick {obs.tick}
          {obs.co_present.length > 0 && (
            <span className="text-ink-500"> (with {obs.co_present.join(", ")})</span>
          )}
        </span>
      );
    case "completed_task":
      return (
        <span className="min-w-0 break-words text-ink-900">
          <span className="font-semibold">completed</span> {obs.task_id} in {obs.room}{" "}
          at tick {obs.tick}
          {fabricated && (
            <span
              className="ml-1.5 inline-flex items-center rounded-pill border-2 border-ink-900 px-1.5 py-0 align-middle font-mono text-[9px] font-bold uppercase tracking-wide text-paper-0"
              style={{ background: tokens.contradiction }}
            >
              fabricated
            </span>
          )}
        </span>
      );
    case "found_body":
      return (
        <span className="min-w-0 break-words text-ink-900">
          <span className="font-semibold">found body</span> of {obs.body_of} in{" "}
          {obs.room} at tick {obs.tick}
        </span>
      );
  }
}

interface MemoryPanelProps {
  memory: AgentMemoryView;
  // Firewall: true only when the impostor's secrets are revealable (Omniscient
  // or the perspective lens IS this agent). Drives fabricated/own-kill/fellow.
  revealSecrets: boolean;
  isImpostor: boolean;
  ownKills: KillEventView[];
  fellowImpostors: PlayerView[];
}

export function MemoryPanel({
  memory,
  revealSecrets,
  isImpostor,
  ownKills,
  fellowImpostors,
}: MemoryPanelProps) {
  // The DTO arrives salience-ordered; show the episodic feed newest-first.
  const observations = [...memory.observations].sort((a, b) => b.tick - a.tick);
  const showImpostorExtras = isImpostor && revealSecrets;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2 text-xs text-ink-700">
        <span className="font-mono text-ink-500">tasks</span>
        <span className="font-mono text-ink-900">
          {memory.tasks_completed} / {memory.tasks_assigned}
        </span>
      </div>

      {showImpostorExtras && fellowImpostors.length > 0 && (
        <section
          className="rounded-md border-2 border-ink-900 px-3 py-2"
          style={{ background: tokens.paper[2] }}
        >
          <SectionHeading>Fellow impostors</SectionHeading>
          <div className="flex flex-wrap gap-1.5">
            {fellowImpostors.map((mate) => (
              <span
                key={mate.agent_id}
                className="inline-flex items-center gap-1.5 rounded-pill border-2 border-ink-900 bg-paper-0 px-2 py-0.5 text-xs font-medium text-ink-900"
              >
                <span
                  aria-hidden
                  className="inline-block h-2.5 w-2.5 rounded-full ring-2 ring-ink-900"
                  style={{ backgroundColor: mate.color }}
                />
                {mate.display_name}
                <span className="font-mono text-[10px] text-ink-400">
                  {mate.agent_id}
                </span>
              </span>
            ))}
          </div>
        </section>
      )}

      {showImpostorExtras && ownKills.length > 0 && (
        <section>
          <SectionHeading>Own kills</SectionHeading>
          <ul className="space-y-1">
            {ownKills.map((kill, index) => (
              <li
                key={`kill-${index}`}
                className="flex items-start gap-2 text-sm"
                style={{ color: tokens.kill }}
              >
                <span aria-hidden className="font-bold">
                  ✦
                </span>
                <span className="min-w-0 break-words font-medium">
                  killed {kill.victim_id} in {kill.room_id} at tick {kill.tick}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <SectionHeading>Observations ({observations.length})</SectionHeading>
        {observations.length === 0 ? (
          <Empty>No observations.</Empty>
        ) : (
          <ul className="space-y-1">
            {observations.map((obs, index) => (
              <li
                key={`obs-${index}`}
                className="flex items-start gap-2 text-sm leading-snug"
              >
                <span aria-hidden className="text-ink-300">
                  •
                </span>
                <ObservationLine
                  obs={obs}
                  fabricated={showImpostorExtras && obs.type === "completed_task"}
                />
              </li>
            ))}
          </ul>
        )}
      </section>

      <details className="rounded-md border-2 border-ink-900 bg-paper-0">
        <summary className="cursor-pointer select-none px-2.5 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-wide text-ink-500">
          Raw rendered memory (sent to LLM)
        </summary>
        <pre className="max-h-96 overflow-auto whitespace-pre-wrap break-words border-t-2 border-ink-900 px-2.5 py-2 font-mono text-xs leading-relaxed text-ink-900">
          {memory.rendered_memory_text}
        </pre>
      </details>
    </div>
  );
}
