// ContradictionBadge — the role-neutral kind chip for a flagged contradiction
// (DESIGN.md §5.3, §5.4). In task 12.1 the utilities this file used to smuggle
// were split out (DESIGN.md §6): the matching/id helpers moved to
// `lib/contradictions.ts` and the transcript-render primitives (`PlayerChip`,
// `ObservationLine`, `ClaimLine`) to `ui/`. This file now holds only the badge.

import type { ContradictionView } from "../types/api";

// Role-neutral cream/ink chip — the KIND is conveyed by the label text, not hue,
// so this badge never spends the reserved amber(=suspicion)/fuchsia(=contradiction)
// channels as decorative colour (firewall discipline; the kinds carry no
// crew/impostor meaning). Weak/strong contradiction emphasis lives on the chain
// links (dashed vs fuchsia), not here.
const KIND_STYLES: Record<ContradictionView["kind"], string> = {
  alibi_conflict: "border border-ink-200 bg-paper-2 text-ink-700",
  alibi_vs_sighting: "border border-ink-200 bg-paper-2 text-ink-700",
};

const KIND_LABELS: Record<ContradictionView["kind"], string> = {
  alibi_conflict: "alibi conflict",
  alibi_vs_sighting: "alibi vs sighting",
};

export function ContradictionBadge({
  contradiction,
}: {
  contradiction: ContradictionView;
}) {
  return (
    <span
      title={contradiction.description}
      className={
        "inline-flex items-center rounded px-1.5 py-0.5 text-xs font-semibold uppercase tracking-wide " +
        KIND_STYLES[contradiction.kind]
      }
    >
      {KIND_LABELS[contradiction.kind]}
    </span>
  );
}
