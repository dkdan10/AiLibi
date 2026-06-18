// BeliefRow serves TWO call sites through one name (a discriminated props union),
// because a Wave-B scope lock lets 12.6 rebuild this file but NOT the out-of-scope
// MemoryPanel that still imports it:
//
//   • MATRIX ROW (the 12.6 hero) — one `<tr>` of the Belief × Truth matrix: a
//     mono row-header (the believer) + one BeliefCell per subject. This is the
//     primary shape, composed by BeliefPanel. Props carry the resolved per-cell
//     models so the row stays presentational.
//   • MEMO BAR (legacy) — the single-belief horizontal bar the still-dark
//     MemoryPanel (Task 12.8's surface) renders for `AgentMemoryView.beliefs`.
//     Kept compiling + restyled onto the suspicion ramp (the old green→red bar
//     violated the firewall: green/red is reserved away from suspicion). 12.8
//     will absorb this when it rebuilds the inspector.
//
// Discriminated structurally on `"belief" in props` — no tag prop — so
// `<BeliefRow belief={…} />` (MemoryPanel) and `<BeliefRow observer={…} … />`
// (the matrix) both type-check.

import { tokens } from "../tokens";
import type { BeliefViewMode } from "../lib/playback";
import type { BeliefEntryView, PlayerView } from "../types/api";
import { BeliefCell, heatColor, type BeliefCellModel } from "./BeliefCell";

interface MatrixRowProps {
  observer: PlayerView;
  // One entry per column, in roster order; pre-resolved by BeliefPanel.
  cells: ReadonlyArray<{ subject: PlayerView; model: BeliefCellModel }>;
  layer: BeliefViewMode;
  omniscient: boolean;
  rowDead: boolean;
  cellSize: number;
  headerWidth: number;
  selected: { observer: string; subject: string } | null;
  onSelectCell: (observer: string, subject: string) => void;
}

interface MemoRowProps {
  belief: BeliefEntryView;
}

export type BeliefRowProps = MatrixRowProps | MemoRowProps;

export function BeliefRow(props: BeliefRowProps) {
  if ("belief" in props) {
    return <MemoBar belief={props.belief} />;
  }
  return <MatrixRow {...props} />;
}

function MatrixRow({
  observer,
  cells,
  layer,
  omniscient,
  rowDead,
  cellSize,
  headerWidth,
  selected,
  onSelectCell,
}: MatrixRowProps) {
  return (
    <tr>
      <th
        scope="row"
        className="border border-ink-200 pr-1.5 text-right font-mono text-[10px] leading-none"
        style={{
          width: headerWidth,
          height: cellSize,
          color: rowDead ? tokens.ink[300] : tokens.ink[900],
          background: tokens.paper[0],
        }}
      >
        {observer.agent_id}
      </th>
      {cells.map(({ subject, model }) => (
        <BeliefCell
          key={subject.agent_id}
          model={model}
          layer={layer}
          omniscient={omniscient}
          size={cellSize}
          selected={
            selected !== null &&
            selected.observer === observer.agent_id &&
            selected.subject === subject.agent_id
          }
          onSelect={() => {
            onSelectCell(observer.agent_id, subject.agent_id);
          }}
        />
      ))}
    </tr>
  );
}

// Legacy single-belief bar (MemoryPanel). MemoryPanel still renders inside the
// dark ThoughtStream rail (`bg-neutral-900/95`), so the text/track/pill stay on
// the original light-on-dark neutrals (cream `ink` text would be dark-on-dark and
// unreadable there) until 12.8 rebuilds the inspector. The ONLY change vs the old
// bar is the firewall fix: the fill is the amber suspicion ramp, not the old
// green→red (green/red is reserved away from suspicion).
function MemoBar({ belief }: { belief: BeliefEntryView }) {
  const suspicion = Math.max(0, Math.min(1, belief.suspicion));
  const pct = Math.round(suspicion * 100);

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
        className="h-2 flex-1 overflow-hidden rounded-pill bg-neutral-700"
      >
        <div className="h-full rounded-pill" style={{ width: `${pct}%`, background: heatColor(suspicion) }} />
      </div>
      <span className="w-9 shrink-0 text-right font-mono text-xs text-neutral-300">
        {belief.suspicion.toFixed(2)}
      </span>
      <span
        title={`confidence ${belief.confidence.toFixed(2)} · snapshot tick ${belief.snapshot_tick}`}
        className="shrink-0 rounded-pill bg-neutral-700/70 px-2 py-0.5 font-mono text-[10px] font-semibold text-neutral-300"
      >
        conf {belief.confidence.toFixed(2)}
      </span>
    </div>
  );
}
