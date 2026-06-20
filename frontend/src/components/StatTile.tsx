// StatTile — a single labelled metric tile (Task 12.10;
// design/phase-12/stage-1-design.md §3.6). Presentational.
//
// Data-surface treatment by default (1px hairline, calm) per the token density
// rule — NOT the chunky chrome offset-shadow, which is reserved for chrome. A
// `lead` tile opts into the bold chrome frame to mark a primary gate.
//
// The optional `caveat` slot renders an attached honesty badge INSIDE the tile,
// so an under-powered / sentinel number is never shown bare (the binding "no
// false precision" rule — a metric carries its caveat, not a footnote).

import type { ReactNode } from "react";

export function StatTile({
  label,
  value,
  hint,
  caveat,
  lead = false,
}: {
  label: string;
  value: string;
  /** Sub-label context (omit it — never pass undefined). */
  hint?: string;
  /** Attached honesty badge(s); rendered inside the tile. */
  caveat?: ReactNode;
  /** Bold chrome frame to mark a primary/lead metric. */
  lead?: boolean;
}) {
  return (
    <div
      className={
        "flex flex-col gap-1 rounded-lg bg-paper-0 px-3 py-2.5 " +
        (lead
          ? "border-2 border-ink-900 shadow-chrome-1"
          : "border border-ink-200 shadow-data")
      }
    >
      <div className="font-mono text-[10px] uppercase tracking-wide text-ink-500">
        {label}
      </div>
      <div className="font-mono text-2xl leading-none text-ink-900">{value}</div>
      {hint ? (
        <div className="text-[11px] leading-snug text-ink-500">{hint}</div>
      ) : null}
      {caveat ? (
        <div className="mt-0.5 flex flex-wrap gap-1">{caveat}</div>
      ) : null}
    </div>
  );
}
