// One cell of the BeliefMatrix (DESIGN.md §6.3): how strongly `observer`
// suspects `subject` at the selected meeting boundary. Color encodes suspicion
// on a green→yellow→red heat scale; lightness encodes confidence. The diagonal
// (observer === subject) is muted — an agent holds no belief about itself — and
// a missing belief renders grey (the sparse, no-evidence-recorded state).

import type { BeliefEntryView, PlayerView } from "../types/api";

// Shared so every cell is the same square regardless of which branch renders.
const CELL_BASE = "h-8 w-8 rounded-sm";

// The DTO contract bounds these to [0, 1]; clamp defensively so a malformed
// value can't push the hue/lightness outside the intended heat scale.
function clamp01(value: number): number {
  return Math.max(0, Math.min(1, value));
}

interface BeliefCellProps {
  observer: PlayerView;
  subject: PlayerView;
  belief: BeliefEntryView | undefined;
}

export function BeliefCell({ observer, subject, belief }: BeliefCellProps) {
  if (observer.agent_id === subject.agent_id) {
    return (
      <div
        className={CELL_BASE + " bg-neutral-800"}
        aria-label={`${observer.agent_id} (self — no belief)`}
      />
    );
  }

  if (belief === undefined) {
    const label = `${observer.agent_id} → ${subject.agent_id}: no belief recorded`;
    return (
      <div
        className={CELL_BASE + " bg-neutral-700 cursor-help"}
        title={label}
        aria-label={label}
      />
    );
  }

  const suspicion = clamp01(belief.suspicion);
  const confidence = clamp01(belief.confidence);
  // hue 120 (green) at suspicion 0 → 0 (red) at 1; more confident → lighter.
  const hue = 120 - 120 * suspicion;
  const lightness = 30 + 20 * confidence;
  const label = `${observer.agent_id} → ${subject.agent_id}: suspicion=${suspicion.toFixed(
    2,
  )} (confidence=${confidence.toFixed(2)})`;

  return (
    <div
      className={CELL_BASE + " cursor-help ring-1 ring-black/30"}
      style={{ background: `hsl(${hue}, 70%, ${lightness}%)` }}
      title={label}
      aria-label={label}
    />
  );
}
