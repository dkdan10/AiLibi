// ContradictionBadge — the role-neutral kind chip for a flagged contradiction
// (DESIGN.md §5.3, §5.4). In task 12.1 the utilities this file used to smuggle
// were split out (DESIGN.md §6): the matching/id helpers moved to
// `lib/contradictions.ts` and the transcript-render primitives (`PlayerChip`,
// `ObservationLine`, `ClaimLine`) to `ui/`. This file now holds only the badge.

import type { ContradictionView } from "../types/api";

// Kind is colour-coded but role-neutral — the colours do not encode crew/impostor.
const KIND_STYLES: Record<ContradictionView["kind"], string> = {
  alibi_conflict: "bg-amber-900/60 text-amber-200 ring-amber-600/60",
  alibi_vs_sighting: "bg-fuchsia-900/60 text-fuchsia-200 ring-fuchsia-600/60",
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
        "inline-flex items-center rounded px-1.5 py-0.5 text-xs font-semibold uppercase tracking-wide ring-1 " +
        KIND_STYLES[contradiction.kind]
      }
    >
      {KIND_LABELS[contradiction.kind]}
    </span>
  );
}
