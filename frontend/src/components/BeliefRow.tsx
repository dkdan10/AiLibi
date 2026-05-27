// One belief entry (DESIGN.md §6.3, §6.6 "Your current beliefs"): the subject
// this agent holds an opinion about, a suspicion bar (0.0–1.0, green below 0.5
// → red above), and a confidence pill. `subject` is a raw agent id because
// `BeliefEntryView` carries no display name; ThoughtStream is a privileged
// post-game view, so showing the id is intended.

import type { BeliefEntryView } from "../types/api";

export function BeliefRow({ belief }: { belief: BeliefEntryView }) {
  // The DTO is a float in [0, 1] by contract; clamp defensively so a malformed
  // value can't render a bar wider than its track or a negative width.
  const suspicion = Math.max(0, Math.min(1, belief.suspicion));
  const pct = Math.round(suspicion * 100);
  const high = suspicion > 0.5;

  return (
    <div className="flex items-center gap-2">
      <span className="w-16 shrink-0 truncate font-mono text-xs text-neutral-200">
        {belief.subject}
      </span>
      <div
        role="meter"
        aria-valuenow={suspicion}
        aria-valuemin={0}
        aria-valuemax={1}
        aria-label={`suspicion of ${belief.subject}`}
        className="h-2 flex-1 overflow-hidden rounded bg-neutral-700"
      >
        <div
          className={"h-full rounded " + (high ? "bg-rose-500" : "bg-emerald-500")}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-9 shrink-0 text-right font-mono text-xs text-neutral-300">
        {belief.suspicion.toFixed(2)}
      </span>
      <span
        title={`confidence ${belief.confidence.toFixed(2)} · snapshot tick ${belief.snapshot_tick}`}
        className="shrink-0 rounded-full bg-neutral-700/70 px-2 py-0.5 text-[10px] font-semibold text-neutral-300"
      >
        conf {belief.confidence.toFixed(2)}
      </span>
    </div>
  );
}
