// ContradictionBadge — the role-neutral evidence chip for a flagged
// contradiction (DESIGN.md §5.3, §5.4). In task 12.1 the utilities this file
// used to smuggle were split out (DESIGN.md §6): the matching/id helpers moved
// to `lib/contradictions.ts` and the transcript-render primitives
// (`ObservationLine`, `ClaimLine`) to `ui/`. This file now holds only the badge.
//
// Task 19.11: the badge used to style by `kind` ALONE, so the MindInspector's
// open-flag list drew a grounded `vent_sighting` — role PROOF — exactly like an
// unverified alibi juxtaposition, and drew a `[weak signal: …]` flag at the same
// weight as hard evidence (audits/audit-phase-19-triage.md §7 item 12). It
// receives the full DTO, so it branches on `category`: the KIND stays the label
// text, the CATEGORY sets the weight.

import type { ContradictionView } from "../types/api";

type EvidenceCategory = ContradictionView["category"];

// Weight by category, `Record`-typed over the union so a fourth category is a
// compile error rather than an unstyled chip. Still cream/ink only: the badge
// never spends the reserved amber(=suspicion)/fuchsia(=contradiction) channels
// as decorative colour (firewall discipline; the kinds carry no crew/impostor
// meaning). What changes is EMPHASIS — proof reads as authoritative solid ink,
// a cross-statement conflict reads as ordinary evidence, a weak signal recedes.
// The strong/weak link emphasis itself lives on the chain links (dashed vs
// fuchsia) and on the meeting view's evidence list, not here.
const CATEGORY_STYLES: Record<EvidenceCategory, string> = {
  role_proof: "border-2 border-ink-900 bg-paper-0 text-ink-900",
  cross_statement: "border border-ink-200 bg-paper-2 text-ink-700",
  weak_signal: "border border-dashed border-ink-300 bg-paper-2 text-ink-500",
};

// The one-word category prefix, so the chip states what the flag IS and never
// leaves an unverified statement pair reading as proof. Paired with the kind
// label below — never conveyed by weight alone (firewall: not hue-only).
const CATEGORY_LABELS: Record<EvidenceCategory, string> = {
  role_proof: "proof",
  cross_statement: "contradiction",
  weak_signal: "weak",
};

const KIND_LABELS: Record<ContradictionView["kind"], string> = {
  alibi_conflict: "alibi conflict",
  alibi_vs_sighting: "alibi vs sighting",
  alibi_vs_physical: "alibi vs physical",
  vent_sighting: "vent sighting",
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
        "inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-xs font-semibold uppercase tracking-wide " +
        CATEGORY_STYLES[contradiction.category]
      }
    >
      <span className="font-bold">{CATEGORY_LABELS[contradiction.category]}</span>
      <span aria-hidden>·</span>
      {KIND_LABELS[contradiction.kind]}
    </span>
  );
}
