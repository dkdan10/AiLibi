// EmptyState — the shared first-class empty state (Task 12.13 cross-surface
// consistency; design/phase-12/stage-1-design.md §6, §8 "no belief yet" ≠ 0).
// One source for the role-neutral "nothing here, and that is honest" card used
// by the replay browser, the dashboard, and the mind inspector (a selected agent
// with no deliberation yet). Compose from tokens; no hardcoded hex.

import type { ReactNode } from "react";

export function EmptyState({
  title,
  children,
  icon,
  className = "",
}: {
  title: string;
  children?: ReactNode;
  icon?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={
        "flex flex-col items-center gap-2 rounded-lg border-2 border-dashed border-ink-300 bg-paper-0 px-4 py-6 text-center " +
        className
      }
    >
      {icon !== undefined && (
        <span aria-hidden className="text-2xl text-ink-300">
          {icon}
        </span>
      )}
      <p className="font-display text-sm font-semibold text-ink-700">{title}</p>
      {children !== undefined && (
        <div className="max-w-prose text-xs text-ink-500">{children}</div>
      )}
    </div>
  );
}
