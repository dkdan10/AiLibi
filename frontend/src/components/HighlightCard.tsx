// HighlightCard (Task 12.9; design/phase-12/stage-1-design.md §3.1, slice 7; the
// firewall rules in design/phase-12/claude-design-brief.md).
//
// PRESENTATIONAL ONLY: one card per game, built from a `RubricGameView` joined to
// its replay metadata. Clicking it calls `onOpen(gameId)` — the connected
// `<ReplayPicker/>` turns that into "load this replay + open the workspace".
//
// It shows: a 0–100 interestingness SCORE badge (decoupled from who won), the
// WIN-SHAPE tag, a DRAMA line (meetings · accused / ejected impostors ·
// survived-accused), and a 4-spoke mini SUB-SCORE bar (R1 decisive / R2 deception
// / R3 arcs / R7 legible).
//
// Firewall (BINDING): the card keys on drama / score, NEVER on who won. The score
// badge + sub-scores are role-neutral ink — they never reuse the suspicion (amber)
// / trust (blue) / kill (red) channels, and the winner is a neutral label, never a
// guilt hue. The 4p1i default set ships no rubric and is mostly zero-meeting, so
// the UNSCORED + ZERO-MEETING states are first-class here, not afterthoughts.

import { scoreBucketOf, type ScoreBucket } from "./ReplayFilters";

import type { RubricGameView, Winner } from "../types/api";

/** One card's data: a rubric row (when scored) joined to its replay metadata. */
export interface HighlightCardData {
  /** Stable React key. */
  readonly key: string;
  /** `headless-seed-{seed}` — what `onOpen` loads. */
  readonly gameId: string;
  readonly seed: number;
  /** From replay metadata; role-neutral display only. `null` when unknown. */
  readonly winner: Winner | null;
  readonly totalTicks: number | null;
  /** `null` = unscored (the set ships no rubric, e.g. the 4p1i default). */
  readonly rubric: RubricGameView | null;
}

const SCORE_BUCKET_LABEL: Record<ScoreBucket, string> = {
  low: "Low",
  med: "Med",
  high: "High",
};

const SUB_SCORES = [
  { key: "R1", label: "decisive", field: "r1_decisive" },
  { key: "R2", label: "deception", field: "r2_deception" },
  { key: "R3", label: "arcs", field: "r3_arcs" },
  { key: "R7", label: "legible", field: "r7_legible" },
] as const;

function winnerLabel(winner: Winner | null): string {
  if (winner === "CREWMATES") return "Crew win";
  if (winner === "IMPOSTORS") return "Impostor win";
  return "Outcome —";
}

// Role-neutral outcome chip: text + a neutral shape glyph, never a guilt hue.
function WinnerTag({ winner }: { winner: Winner | null }) {
  const glyph = winner === "IMPOSTORS" ? "◆" : winner === "CREWMATES" ? "▲" : "·";
  return (
    <span className="inline-flex items-center gap-1 rounded-pill border border-ink-300 px-2 py-0.5 font-mono text-[10px] text-ink-600">
      <span aria-hidden>{glyph}</span>
      {winnerLabel(winner)}
    </span>
  );
}

// 0–100 score badge. Role-neutral ink-on-paper: the number + the Low/Med/High
// bucket carry the meaning, with no reserved-channel hue.
function ScoreBadge({ score }: { score: number }) {
  const bucket = scoreBucketOf(score);
  return (
    <div className="flex shrink-0 flex-col items-center rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-1.5 shadow-data">
      <div className="flex items-baseline gap-0.5">
        <span className="font-display text-2xl leading-none text-ink-900">
          {Math.round(score)}
        </span>
        <span className="font-mono text-[10px] text-ink-400">/100</span>
      </div>
      <span className="mt-0.5 font-mono text-[9px] uppercase tracking-wide text-ink-500">
        {SCORE_BUCKET_LABEL[bucket]} interest
      </span>
    </div>
  );
}

function WinShapeTag({ shape }: { shape: string }) {
  return (
    <span className="inline-block rounded-pill border-2 border-ink-900 bg-paper-2 px-2.5 py-0.5 font-mono text-xs font-medium text-ink-900">
      {shape}
    </span>
  );
}

// Meetings · accused / ejected impostors · survived-accused. Zero-meeting games
// (common in the 4p1i set) get an honest "No meetings" rather than a row of 0s.
function DramaLine({ rubric }: { rubric: RubricGameView }) {
  if (rubric.n_meetings === 0) {
    return (
      <p className="font-mono text-xs text-ink-500">
        No meetings — no deduction drama
      </p>
    );
  }
  return (
    <p className="font-mono text-xs text-ink-700">
      <span className="font-semibold">{rubric.n_meetings}</span>{" "}
      {rubric.n_meetings === 1 ? "meeting" : "meetings"}
      <span className="text-ink-300"> · </span>
      <span title="impostors verbally accused / impostors ejected">
        {rubric.accused_impostors} accused / {rubric.ejected_impostors} ejected
      </span>
      <span className="text-ink-300"> · </span>
      <span title="accused impostors who survived to game end">
        {rubric.survived_accused} survived
      </span>
    </p>
  );
}

// The 4-spoke mini sub-score bar. Each sub-score is 0–1; bars are neutral ink so
// they never collide with a semantic channel.
function SubScoreBar({ rubric }: { rubric: RubricGameView }) {
  return (
    <div className="flex items-stretch gap-2" aria-label="Rubric sub-scores">
      {SUB_SCORES.map((meta) => {
        const value = rubric[meta.field];
        const pct = Math.round(Math.max(0, Math.min(1, value)) * 100);
        return (
          <div
            key={meta.key}
            className="flex flex-1 flex-col items-center gap-1"
            title={`${meta.key} ${meta.label}: ${value.toFixed(2)}`}
          >
            <div className="flex h-10 w-full items-end overflow-hidden rounded-sm bg-paper-3 shadow-data">
              <div
                className="w-full bg-ink-700"
                style={{ height: `${pct}%` }}
              />
            </div>
            <span className="font-mono text-[9px] font-semibold text-ink-700">
              {meta.key}
            </span>
          </div>
        );
      })}
    </div>
  );
}

interface HighlightCardProps {
  data: HighlightCardData;
  onOpen: (gameId: string) => void;
}

export function HighlightCard({ data, onOpen }: HighlightCardProps) {
  const { rubric } = data;
  const scored = rubric !== null;
  const ariaLabel = scored
    ? `Open replay seed ${data.seed}, interestingness score ${Math.round(
        rubric.score,
      )} of 100`
    : `Open replay seed ${data.seed} (unscored)`;

  return (
    <button
      type="button"
      onClick={() => {
        onOpen(data.gameId);
      }}
      aria-label={ariaLabel}
      className="flex w-full flex-col gap-3 rounded-lg border-2 border-ink-900 bg-paper-0 p-4 text-left shadow-chrome-1 transition-transform hover:-translate-y-0.5 hover:shadow-chrome-2 focus-visible:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink-900"
    >
      {/* header: seed + role-neutral outcome */}
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-xs font-semibold text-ink-900">
          seed {data.seed}
        </span>
        <WinnerTag winner={data.winner} />
      </div>

      {scored ? (
        <>
          <div className="flex items-start gap-3">
            <ScoreBadge score={rubric.score} />
            <div className="flex min-w-0 flex-col gap-1.5">
              <WinShapeTag shape={rubric.win_shape} />
              <DramaLine rubric={rubric} />
            </div>
          </div>
          <SubScoreBar rubric={rubric} />
        </>
      ) : (
        // Unscored: the set ships no rubric (the 4p1i common case). A real state,
        // never a broken score panel — show what we do know and say it plainly.
        <div className="flex flex-col gap-1 rounded-md border border-dashed border-ink-300 bg-paper-1 px-3 py-2">
          <span className="font-mono text-xs font-semibold text-ink-700">
            Not scored
          </span>
          <span className="font-mono text-[11px] text-ink-500">
            This set ships no interestingness rubric.
          </span>
          {data.totalTicks !== null && (
            <span className="font-mono text-[11px] text-ink-500">
              {data.totalTicks} ticks
            </span>
          )}
        </div>
      )}
    </button>
  );
}
