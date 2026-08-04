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
// guilt hue. 4p1i is the fast technical fixture — served only on an explicit
// `?set=4p1i` since Task 19.9 flipped the default to 9p2i — and it ships no
// rubric; 11 of its 50 games hold no meeting at all. So the UNSCORED and
// ZERO-MEETING states are first-class here, not afterthoughts.
//
// REVEAL GATING (Task 19.10): this grid renders BEFORE anything is opened, so it
// is the corpus's biggest pre-play spoiler surface. The card therefore takes a
// `reveal` prop and, while it is false, emits NO outcome-derived DOM: the winner
// chip reads "Outcome hidden", and the win shape (which names the MECHANISM of
// the ending) plus the accused/ejected/survived counts collapse to one honest
// line. Structure stays visible — the meeting count, the tick count and the
// interestingness sub-scores describe pacing, not who won. `reveal` is a plain
// prop: this component stays presentational and the store lives in ReplayPicker.

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
  /** `null` = unscored (the set ships no rubric, e.g. the 4p1i fixture set). */
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
//
// `hidden` is NOT the same slot as `winner === null` (Task 19.10). A null winner
// means genuinely unknown ("Outcome —" — a partial replay with no game_over);
// hidden means recorded-but-withheld. They must read differently or the unspoiled
// mode looks like broken data. The pill styling is identical in all three states
// so the header does not reflow when the reveal is toggled.
function WinnerTag({ winner, hidden }: { winner: Winner | null; hidden: boolean }) {
  const glyph = hidden
    ? "·"
    : winner === "IMPOSTORS"
      ? "◆"
      : winner === "CREWMATES"
        ? "▲"
        : "·";
  return (
    <span
      title={hidden ? "Hidden until you reveal outcomes" : undefined}
      // `text-3xs` is the named 10px step — identical to the ad-hoc `text-[10px]`
      // this line carried, minus the literal (the rest of the file still has a
      // few; converting them all is out of 19.10's scope).
      className="inline-flex items-center gap-1 rounded-pill border border-ink-300 px-2 py-0.5 font-mono text-3xs text-ink-600"
    >
      <span aria-hidden>{glyph}</span>
      {hidden ? "Outcome hidden" : winnerLabel(winner)}
    </span>
  );
}

// 0–100 score badge. Role-neutral ink-on-paper: the number + the Low/Med/High
// bucket carry the meaning, with no reserved-channel hue.
//
// The bucket line carries the NARROW LABEL (Task 19.9, restated per-badge because
// the number travels): both Phase-19 audits found this scalar's ordering inverts
// the human-interest tails, so it must never read as a watchability ranking.
const SCORE_TITLE =
  "Internal pacing/structure heuristic — not a human rating, not a watchability ranking";

function ScoreBadge({ score }: { score: number }) {
  const bucket = scoreBucketOf(score);
  return (
    <div
      title={SCORE_TITLE}
      className="flex shrink-0 flex-col items-center rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-1.5 shadow-data"
    >
      <div className="flex items-baseline gap-0.5">
        <span className="font-display text-2xl leading-none text-ink-900">
          {Math.round(score)}
        </span>
        <span className="font-mono text-[10px] text-ink-400">/100</span>
      </div>
      <span className="mt-0.5 font-mono text-[9px] uppercase tracking-wide text-ink-500">
        {SCORE_BUCKET_LABEL[bucket]} · internal heuristic
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
//
// Reveal split (Task 19.10): the MEETING COUNT is structure — how much
// deliberation the game holds — and stays visible unspoiled, as does the
// zero-meeting line. The accused / ejected / survived counts are outcome (they
// say whether the table got it right), so unrevealed they collapse to one line
// that admits the omission rather than silently dropping to a shorter sentence.
function DramaLine({ rubric, reveal }: { rubric: RubricGameView; reveal: boolean }) {
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
      {reveal ? (
        <>
          <span title="impostors verbally accused / impostors ejected">
            {rubric.accused_impostors} accused / {rubric.ejected_impostors} ejected
          </span>
          <span className="text-ink-300"> · </span>
          <span title="accused impostors who survived to game end">
            {rubric.survived_accused} survived
          </span>
        </>
      ) : (
        <span className="text-ink-500">outcome details hidden</span>
      )}
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
            title={`${meta.key} ${meta.label}: ${value.toFixed(2)} (0–1)`}
          >
            <div className="relative flex h-10 w-full items-end overflow-hidden rounded-sm bg-paper-3 shadow-data">
              {/* Baseline reference at the 0.5 midpoint (Task 12.13): without it a
                  bare bar gives no sense of where a value sits on its 0–1 scale. */}
              <div
                aria-hidden
                className="pointer-events-none absolute inset-x-0 top-1/2 border-t border-dashed border-ink-300"
              />
              <div className="relative w-full bg-ink-700" style={{ height: `${pct}%` }} />
            </div>
            <span className="font-mono text-[9px] font-semibold text-ink-700">
              {meta.key}
            </span>
            {/* The concrete value, not just a height (Task 12.13). */}
            <span className="font-mono text-[9px] text-ink-500">{value.toFixed(2)}</span>
          </div>
        );
      })}
    </div>
  );
}

interface HighlightCardProps {
  data: HighlightCardData;
  onOpen: (gameId: string) => void;
  // When the WHOLE set is unscored, the "Not scored" note is hoisted to one
  // banner above the grid (Task 12.13), so the per-card note is suppressed here.
  hideUnscoredNote?: boolean;
  // Outcome reveal (Task 19.10). Required, not optional: an omitted spoiler gate
  // must be a compile error, never a silent default to "show everything".
  reveal: boolean;
}

export function HighlightCard({
  data,
  onOpen,
  hideUnscoredNote,
  reveal,
}: HighlightCardProps) {
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
        <WinnerTag winner={data.winner} hidden={!reveal} />
      </div>

      {scored ? (
        <>
          <div className="flex items-start gap-3">
            <ScoreBadge score={rubric.score} />
            <div className="flex min-w-0 flex-col gap-1.5">
              {/* The win shape names HOW the game ended ("impostor-win",
                  "eject-decided", "stopwatch-no-meeting") — a sharper spoiler
                  than the winner itself, so it is omitted entirely rather than
                  placeheld while unrevealed (Task 19.10). */}
              {reveal && <WinShapeTag shape={rubric.win_shape} />}
              <DramaLine rubric={rubric} reveal={reveal} />
            </div>
          </div>
          <SubScoreBar rubric={rubric} />
        </>
      ) : hideUnscoredNote ? (
        // Whole set unscored: the note is hoisted to one banner above the grid
        // (Task 12.13). Keep just the factual tick count per card.
        data.totalTicks !== null && (
          <span className="font-mono text-[11px] text-ink-500">
            {data.totalTicks} ticks
          </span>
        )
      ) : (
        // Unscored: the set ships no rubric (the 4p1i fixture case). A real
        // state, never a broken score panel — show what we do know and say it
        // plainly.
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
