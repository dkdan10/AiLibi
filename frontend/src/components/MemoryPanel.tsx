// Presentational private memory. MindInspector requires the observer’s own lens
// or omniscient mode before mounting this panel. Keep role-bearing extras gated
// here as well for standalone consumers.

import type { ReactElement, ReactNode } from "react";

import { tokens } from "../tokens";
import type {
  AgentMemoryView,
  CompletedTaskObsView,
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

// Exhaustive rendering keeps additive account kinds visible. Reported task
// activity is a claim, and never becomes a completed task in this panel.
function ObservationLine({ obs }: { obs: ObservationClaimView }): ReactElement {
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
        </span>
      );
    case "task_activity":
      return (
        <span className="min-w-0 break-words text-ink-900">
          <span className="font-semibold">claimed task activity</span>{" "}
          {obs.task_id} in {obs.room}, ticks {obs.from_tick}–{obs.to_tick}
        </span>
      );
    case "found_body":
      return (
        <span className="min-w-0 break-words text-ink-900">
          <span className="font-semibold">found body</span> of {obs.body_of} in{" "}
          {obs.room} at tick {obs.tick}
        </span>
      );
    case "saw_vent":
      return (
        <span className="min-w-0 break-words text-ink-900">
          <span className="font-semibold">saw</span> {obs.subject}{" "}
          <span className="font-semibold">vent</span> in {obs.room} at tick{" "}
          {obs.tick}
        </span>
      );
    case "saw_kill":
      return (
        <span className="min-w-0 break-words text-ink-900">
          <span className="font-semibold">saw</span> {obs.subject}{" "}
          <span className="font-semibold">kill</span> in {obs.room} at tick{" "}
          {obs.tick}
        </span>
      );
    case "whereabouts":
      return (
        <span className="min-w-0 break-words text-ink-900">
          <span className="font-semibold">was in</span> {obs.room} at tick {obs.tick}
        </span>
      );
    case "saw_move":
      return (
        <span className="min-w-0 break-words text-ink-900">
          <span className="font-semibold">saw</span> {obs.subject} move from{" "}
          {obs.from_room} to {obs.to_room} at tick {obs.tick}
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
  // The impostor's fabricated cover-task alibis (its meeting `completed_task`
  // turn observations), resolved by the connected inspector.
  coverTasks: CompletedTaskObsView[];
  fellowImpostors: PlayerView[];
}

export function MemoryPanel({
  memory,
  revealSecrets,
  isImpostor,
  ownKills,
  coverTasks,
  fellowImpostors,
}: MemoryPanelProps) {
  const showImpostorExtras = isImpostor && revealSecrets;

  // When the own-kill line is shown, drop the killer's own victim from the body
  // feed so the same event isn't rendered twice (killed p-X + found body p-X) —
  // matching `render_for_prompt`, which suppresses that body for the own-kill.
  const ownVictims = new Set(ownKills.map((k) => k.victim_id));
  const observations = [...memory.observations]
    .filter(
      (obs) =>
        !(
          showImpostorExtras &&
          obs.type === "found_body" &&
          ownVictims.has(obs.body_of)
        ),
    )
    // The DTO arrives salience-ordered; show the episodic feed newest-first.
    .sort((a, b) => {
      const aTick = a.type === "task_activity" ? a.to_tick : a.tick;
      const bTick = b.type === "task_activity" ? b.to_tick : b.tick;
      return bTick - aTick;
    });

  // The raw rendered memory IS the verbatim prompt memory — it carries the
  // agent's `Your role` block + (for an impostor) the own-kill self-channel — so
  // it rides the Omniscient-or-self gate for EVERY agent, not just impostors.
  const rawMemoryRedacted = !revealSecrets;

  return (
    <div className="space-y-4">
      {/* The task tally encodes alignment (impostors carry 0 assigned tasks,
          crewmates carry several), so it is a ground-truth tell — shown only when
          revealable, suppressed through a different agent's fog. */}
      {revealSecrets && (
        <div className="flex flex-wrap items-center gap-2 text-xs text-ink-700">
          <span className="font-mono text-ink-500">tasks</span>
          <span className="font-mono text-ink-900">
            {memory.tasks_completed} / {memory.tasks_assigned}
          </span>
        </div>
      )}

      {revealSecrets && memory.investigation_plan && (
        <section aria-label="Search intention">
          <SectionHeading>Search intention</SectionHeading>
          <p className="text-xs text-ink-700">
            At tick {memory.investigation_plan.decision_tick}, planned to look for{" "}
            {memory.investigation_plan.target_id}, last seen in{" "}
            {memory.investigation_plan.last_known_room} at tick{" "}
            {memory.investigation_plan.source_tick}.
          </p>
          <p className="text-xs text-ink-500">
            This is a plan, not a sighting. Finding someone later does not confirm where they were earlier.
          </p>
        </section>
      )}

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

      {showImpostorExtras && coverTasks.length > 0 && (
        <section>
          <SectionHeading>Cover tasks (fabricated)</SectionHeading>
          <ul className="space-y-1">
            {coverTasks.map((task, index) => (
              <li
                key={`cover-${index}`}
                className="flex flex-wrap items-center gap-2 text-sm text-ink-900"
              >
                <span className="min-w-0 break-words">
                  {task.task_id} in {task.room} at tick {task.tick}
                </span>
                <span
                  className="inline-flex items-center rounded-pill border-2 border-ink-900 px-1.5 py-0 font-mono text-[9px] font-bold uppercase tracking-wide text-paper-0"
                  style={{ background: tokens.contradiction }}
                >
                  fabricated
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
                <ObservationLine obs={obs} />
              </li>
            ))}
          </ul>
        )}
      </section>

      {rawMemoryRedacted ? (
        <p
          className="rounded-md border-2 border-dashed border-ink-300 px-3 py-3 text-xs text-ink-500"
          style={{ background: tokens.paper[2] }}
        >
          Raw rendered memory is hidden through another agent's fog — it embeds
          this agent's role and private memory. Switch to Omniscient, or view this
          agent through its own lens, to read it.
        </p>
      ) : (
        <details className="rounded-md border-2 border-ink-900 bg-paper-0">
          <summary className="cursor-pointer select-none px-2.5 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-wide text-ink-500">
            Raw rendered memory (sent to LLM)
          </summary>
          <pre className="max-h-96 overflow-auto whitespace-pre-wrap break-words border-t-2 border-ink-900 px-2.5 py-2 font-mono text-xs leading-relaxed text-ink-900">
            {memory.rendered_memory_text}
          </pre>
        </details>
      )}
    </div>
  );
}
