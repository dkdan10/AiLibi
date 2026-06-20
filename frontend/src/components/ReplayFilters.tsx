// Replay browser / Highlights reel filter bar (Task 12.9; design/phase-12/
// stage-1-design.md §3.1, §2.1, slice 7; the firewall rules in
// design/phase-12/claude-design-brief.md).
//
// PRESENTATIONAL ONLY: this renders the shared, URL-driven filter controls and
// reports changes through `onChange`. The connected `<ReplayPicker/>` owns the
// state + the `URLSearchParams` round-trip (the same pattern 12.4 uses, so a
// filtered reel is shareable + reload-stable, and 12.10's interestingness
// histogram deep-links land on the right filter).
//
// Shared query keys (the contract 12.10 builds links with): set · winner ·
// winShape · scoreBucket (low/med/high) · hasEjection. `set` is the served set
// (one per loader dir), so it is CONTEXT here — displayed + round-tripped via the
// store, never a toggle; the four interactive filters are winner / winShape /
// scoreBucket / hasEjection.
//
// Firewall: outcomes are role-neutral. The winner is a plain text option, never
// a guilt hue, and nothing here colours by who won.

import type { ReactNode } from "react";

import type { Winner } from "../types/api";

export type ScoreBucket = "low" | "med" | "high";

export interface ReplayFilterState {
  readonly winner: Winner | null; // null = any
  readonly winShape: string | null; // null = any
  readonly scoreBucket: ScoreBucket | null; // null = any
  readonly hasEjection: boolean; // true = only games that ejected an impostor
}

export const EMPTY_FILTERS: ReplayFilterState = {
  winner: null,
  winShape: null,
  scoreBucket: null,
  hasEjection: false,
};

// The 0–100 interestingness score is bucketed into EQUAL THIRDS. This boundary
// is a shared contract: 12.10's interestingness histogram deep-links into the
// reel with `scoreBucket=<bucket>`, so its bins MUST collapse onto the same
// split — low < 100/3 ≤ med < 200/3 ≤ high.
const SCORE_BUCKET_LOW_MAX = 100 / 3;
const SCORE_BUCKET_HIGH_MIN = 200 / 3;

export function scoreBucketOf(score: number): ScoreBucket {
  if (score < SCORE_BUCKET_LOW_MAX) return "low";
  if (score < SCORE_BUCKET_HIGH_MIN) return "med";
  return "high";
}

const SCORE_BUCKET_LABEL: Record<ScoreBucket, string> = {
  low: "Low",
  med: "Med",
  high: "High",
};

export function hasActiveFilters(f: ReplayFilterState): boolean {
  return (
    f.winner !== null ||
    f.winShape !== null ||
    f.scoreBucket !== null ||
    f.hasEjection
  );
}

// ── URL round-trip (pure helpers; the connected component does the I/O) ───────
// Only the four interactive keys are owned here; `set` is owned by the store /
// 12.4's sync. `writeFilterParams` MERGES into an existing search string so the
// other shared keys (set / view / game_id / tick / …) survive.

const WINNERS: readonly Winner[] = ["CREWMATES", "IMPOSTORS"];
const SCORE_BUCKETS: readonly ScoreBucket[] = ["low", "med", "high"];

function isWinner(value: string | null): value is Winner {
  return value !== null && (WINNERS as readonly string[]).includes(value);
}

function isScoreBucket(value: string | null): value is ScoreBucket {
  return value !== null && (SCORE_BUCKETS as readonly string[]).includes(value);
}

/** Parse the four filter keys out of a `location.search` string. */
export function parseFilterParams(search: string): ReplayFilterState {
  const params = new URLSearchParams(search);
  const winnerRaw = params.get("winner");
  const bucketRaw = params.get("scoreBucket");
  const winShapeRaw = params.get("winShape");
  return {
    winner: isWinner(winnerRaw) ? winnerRaw : null,
    winShape: winShapeRaw === null || winShapeRaw === "" ? null : winShapeRaw,
    scoreBucket: isScoreBucket(bucketRaw) ? bucketRaw : null,
    hasEjection: params.get("hasEjection") === "1",
  };
}

/**
 * Merge the four filter keys into `search`, preserving every other key (so
 * 12.4's set / view / game_id survive). Returns a query string beginning with
 * "?", or "" when empty.
 */
export function writeFilterParams(
  search: string,
  filters: ReplayFilterState,
): string {
  const params = new URLSearchParams(search);
  if (filters.winner !== null) {
    params.set("winner", filters.winner);
  } else {
    params.delete("winner");
  }
  if (filters.winShape !== null) {
    params.set("winShape", filters.winShape);
  } else {
    params.delete("winShape");
  }
  if (filters.scoreBucket !== null) {
    params.set("scoreBucket", filters.scoreBucket);
  } else {
    params.delete("scoreBucket");
  }
  if (filters.hasEjection) {
    params.set("hasEjection", "1");
  } else {
    params.delete("hasEjection");
  }
  const query = params.toString();
  return query === "" ? "" : `?${query}`;
}

// ── presentational control ────────────────────────────────────────────────

const SELECT_CLASS =
  "rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-1 font-mono text-xs " +
  "text-ink-900 disabled:cursor-not-allowed disabled:opacity-50";

const FIELD_LABEL_CLASS =
  "font-mono text-[10px] uppercase tracking-wide text-ink-500";

interface FilterFieldProps {
  label: string;
  children: ReactNode;
}

function FilterField({ label, children }: FilterFieldProps) {
  return (
    <label className="flex flex-col gap-1">
      <span className={FIELD_LABEL_CLASS}>{label}</span>
      {children}
    </label>
  );
}

interface ReplayFiltersProps {
  filters: ReplayFilterState;
  onChange: (next: ReplayFilterState) => void;
  /** Distinct `win_shape` tags present in the available data (sorted). */
  winShapeOptions: readonly string[];
  /** The served set id (e.g. "9p2i"); context, not a toggle. */
  set: string | null;
  /** Cards after filtering / total before filtering, for the live count. */
  resultCount: number;
  totalCount: number;
  disabled?: boolean;
}

export function ReplayFilters({
  filters,
  onChange,
  winShapeOptions,
  set,
  resultCount,
  totalCount,
  disabled = false,
}: ReplayFiltersProps) {
  const active = hasActiveFilters(filters);

  return (
    <div
      className="flex flex-wrap items-end gap-3 rounded-lg border-2 border-ink-900 bg-paper-1 px-4 py-3 shadow-chrome-1"
      role="group"
      aria-label="Replay filters"
    >
      {set !== null && (
        <FilterField label="Set">
          <span className="rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-1 font-mono text-xs font-semibold text-ink-900">
            {set}
          </span>
        </FilterField>
      )}

      <FilterField label="Winner">
        <select
          className={SELECT_CLASS}
          disabled={disabled}
          value={filters.winner ?? ""}
          onChange={(e) => {
            const v = e.target.value;
            onChange({
              ...filters,
              winner: v === "" ? null : (v as Winner),
            });
          }}
        >
          <option value="">Any winner</option>
          <option value="CREWMATES">Crew</option>
          <option value="IMPOSTORS">Impostor</option>
        </select>
      </FilterField>

      <FilterField label="Win shape">
        <select
          className={SELECT_CLASS}
          disabled={disabled || winShapeOptions.length === 0}
          value={filters.winShape ?? ""}
          onChange={(e) => {
            const v = e.target.value;
            onChange({ ...filters, winShape: v === "" ? null : v });
          }}
        >
          <option value="">Any shape</option>
          {winShapeOptions.map((shape) => (
            <option key={shape} value={shape}>
              {shape}
            </option>
          ))}
        </select>
      </FilterField>

      <FilterField label="Score">
        <select
          className={SELECT_CLASS}
          disabled={disabled}
          value={filters.scoreBucket ?? ""}
          onChange={(e) => {
            const v = e.target.value;
            onChange({
              ...filters,
              scoreBucket: v === "" ? null : (v as ScoreBucket),
            });
          }}
        >
          <option value="">Any score</option>
          {SCORE_BUCKETS.map((bucket) => (
            <option key={bucket} value={bucket}>
              {SCORE_BUCKET_LABEL[bucket]}
            </option>
          ))}
        </select>
      </FilterField>

      <FilterField label="Ejection">
        <label className="flex items-center gap-1.5 rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-1 font-mono text-xs text-ink-900">
          <input
            type="checkbox"
            className="accent-ink-900"
            disabled={disabled}
            checked={filters.hasEjection}
            onChange={(e) => {
              onChange({ ...filters, hasEjection: e.target.checked });
            }}
          />
          ejected an impostor
        </label>
      </FilterField>

      <div className="ml-auto flex items-center gap-3">
        <span className="font-mono text-xs text-ink-500" aria-live="polite">
          {resultCount === totalCount
            ? `${totalCount} games`
            : `${resultCount} / ${totalCount} games`}
        </span>
        {active && (
          <button
            type="button"
            disabled={disabled}
            onClick={() => {
              onChange(EMPTY_FILTERS);
            }}
            className="rounded-md border-2 border-ink-900 bg-paper-0 px-2.5 py-1 font-mono text-xs font-medium text-ink-900 hover:bg-paper-2 disabled:opacity-50"
          >
            Clear
          </button>
        )}
      </div>
    </div>
  );
}
