// MetricCaveat — the honesty badge (Task 12.10; design/phase-12/stage-1-design.md
// §3.6; the "no false precision" rule in design/phase-12/claude-design-brief.md).
//
// A small caveat chip ATTACHED to the metric it qualifies (small-n / low-power /
// populated-bins / sentinel notes). The binding honesty rule: an under-powered or
// sentinel number is NEVER shown bare — its caveat rides with it, not in a
// distant footnote.
//
// Firewall-safe by construction: a caveat is meta-UI, not a game semantic, so it
// must NOT borrow a reserved channel hue (amber = suspicion, blue = trust,
// orange = distrust, red = kill, fuchsia = contradiction). It is drawn in neutral
// ink + a leading glyph, so it reads by SHAPE + TEXT, never hue alone.

import type { ReactNode } from "react";

export type CaveatTone = "warn" | "note";

const GLYPH: Record<CaveatTone, string> = {
  warn: "▲", // under-powered / read-with-care
  note: "ⓘ", // honest scope note / context
};

export function MetricCaveat({
  tone = "warn",
  title,
  children,
}: {
  tone?: CaveatTone;
  /** Optional long-form detail surfaced on hover (omit it — never pass undefined). */
  title?: string;
  children: ReactNode;
}) {
  const warn = tone === "warn";
  return (
    <span
      role="note"
      title={title}
      className={
        "inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 font-mono text-[10px] leading-tight " +
        (warn
          ? "border-ink-900 bg-paper-3 text-ink-900"
          : "border-ink-200 bg-paper-1 text-ink-700")
      }
    >
      <span aria-hidden className="font-semibold">
        {GLYPH[tone]}
      </span>
      <span>{children}</span>
    </span>
  );
}
