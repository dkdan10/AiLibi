// SectionLabel — the shared "eyebrow" (Task 12.13 cross-surface consistency;
// design/phase-12/stage-1-design.md §6). One source for the mono, small-caps,
// muted section label that was hand-restated across MindInspector (TabHeading),
// the dashboard, and the belief panels. Compose from tokens; no hardcoded hex.
//
// Polymorphic `as` so it can be a real heading where the surface needs one
// (MindInspector's per-tab headings) or a plain inline eyebrow elsewhere.

import type { ReactNode } from "react";

type LabelTag = "span" | "p" | "h2" | "h3" | "h4";

export function SectionLabel({
  children,
  as: Tag = "span",
  className = "",
}: {
  children: ReactNode;
  as?: LabelTag;
  className?: string;
}) {
  return (
    <Tag
      className={
        "font-mono text-3xs font-semibold uppercase tracking-wide text-ink-500 " +
        className
      }
    >
      {children}
    </Tag>
  );
}
