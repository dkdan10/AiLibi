// BeliefRow — one `<tr>` of the Belief × Truth matrix (Task 12.6): a mono
// row-header (the believer) + one BeliefCell per subject, composed by
// BeliefPanel. Props carry the resolved per-cell models so the row stays
// presentational.
//
// (Task 12.13 removed the dead legacy `MemoBar` branch: the single-belief bar
// for the old dark MemoryPanel was off-token neutral ramps and no longer
// rendered anywhere — MemoryPanel does not import BeliefRow.)

import { tokens } from "../tokens";
import type { BeliefViewMode } from "../lib/playback";
import type { PlayerView } from "../types/api";
import { BeliefCell, type BeliefCellModel } from "./BeliefCell";

export interface BeliefRowProps {
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

export function BeliefRow({
  observer,
  cells,
  layer,
  omniscient,
  rowDead,
  cellSize,
  headerWidth,
  selected,
  onSelectCell,
}: BeliefRowProps) {
  return (
    <tr>
      <th
        scope="row"
        className="border border-ink-200 pr-1.5 text-right font-mono text-3xs leading-none"
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
