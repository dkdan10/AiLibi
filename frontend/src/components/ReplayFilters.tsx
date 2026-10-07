// Replay browser / Highlights reel filter bar (Task 12.9; design/phase-12/
// stage-1-design.md §3.1, §2.1, slice 7; the firewall rules in
// design/phase-12/claude-design-brief.md).
//
// PRESENTATIONAL ONLY: this renders the shared, URL-driven filter controls and
// reports changes through `onChange`. The connected `<ReplayPicker/>` owns the
// state + the `URLSearchParams` round-trip (the same pattern 12.4 uses, so a
// filtered list is shareable + reload-stable).
//
// Shared query keys: set · winner · hasEjection. `set` is the served set (one
// per loader dir), so it is CONTEXT here — displayed + round-tripped via the
// store, never a toggle; the two interactive filters are winner / hasEjection.
// Nothing here filters by a score: the game-shape profile has none.
//
// Firewall: outcomes are role-neutral. The winner is a plain text option, never
// a guilt hue, and nothing here colours by who won. The ejection filter reads
// whether some meeting voted someone out, whoever it was.
//
// Unspoiled mode (Task 19.10): both interactive filters are OUTCOME controls, so
// while `reveal` is false neither renders and one spoiler-warned affordance
// stands in their place. Everything BELOW the presentation layer is untouched:
// `ReplayFilterState`, `hasActiveFilters`, `parseFilterParams` and
// `writeFilterParams` keep both keys round-tripping regardless of reveal, so a
// shared `?winner=…` link survives an unrevealed visit intact and re-applies the
// moment outcomes are shown. The controls hide; the state machinery stays. (The
// connected ReplayPicker makes both criteria INERT while hidden — a control
// nobody can see must not filter.)

import type { ReactNode } from "react";

import type { Winner } from "../types/api";

export interface ReplayFilterState {
  readonly winner: Winner | null; // null = any
  readonly hasEjection: boolean; // true = only games where someone was voted out
}

export const EMPTY_FILTERS: ReplayFilterState = {
  winner: null,
  hasEjection: false,
};

export function hasActiveFilters(f: ReplayFilterState): boolean {
  return f.winner !== null || f.hasEjection;
}

// ── URL round-trip (pure helpers; the connected component does the I/O) ───────
// Only the two interactive keys are owned here; `set` is owned by the store /
// 12.4's sync. `writeFilterParams` MERGES into an existing search string so the
// other shared keys (set / view / game_id / tick / …) survive.

const WINNERS: readonly Winner[] = ["CREWMATES", "IMPOSTORS"];

function isWinner(value: string | null): value is Winner {
  return value !== null && (WINNERS as readonly string[]).includes(value);
}

/** Parse the two filter keys out of a `location.search` string. */
export function parseFilterParams(search: string): ReplayFilterState {
  const params = new URLSearchParams(search);
  const winnerRaw = params.get("winner");
  return {
    winner: isWinner(winnerRaw) ? winnerRaw : null,
    hasEjection: params.get("hasEjection") === "1",
  };
}

/**
 * Merge the two filter keys into `search`, preserving every other key (so
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

const GATE_WARNING_ID = "outcome-filters-spoiler-warning";

// The stand-in for the two outcome fields while outcomes are hidden (Task
// 19.10). Dashed border = the established "honestly nothing here" idiom (cf.
// ui/EmptyState) — this is a declared omission, not a control that failed to
// load. The warning is a sibling line, not a tooltip, because the cost of the
// click is unrecoverable: revealing is set-wide and instant, and there is no
// un-seeing an ending. It is wired with `aria-describedby` so the warning reaches
// assistive tech before activation, not after.
function OutcomeFilterGate({
  onReveal,
  disabled,
}: {
  onReveal: () => void;
  disabled: boolean;
}) {
  return (
    <div className="flex flex-col gap-1 rounded-md border-2 border-dashed border-ink-300 bg-paper-0 px-3 py-2">
      <button
        type="button"
        disabled={disabled}
        aria-describedby={GATE_WARNING_ID}
        onClick={onReveal}
        className="self-start rounded-md border-2 border-ink-900 bg-paper-0 px-2.5 py-1 font-mono text-xs font-medium text-ink-900 hover:bg-paper-2 disabled:cursor-not-allowed disabled:opacity-50"
      >
        Show outcome filters
      </button>
      <span id={GATE_WARNING_ID} className="font-mono text-2xs text-ink-500">
        <span aria-hidden>⚠</span> reveals winners and endings across the whole set
      </span>
    </div>
  );
}

interface ReplayFiltersProps {
  filters: ReplayFilterState;
  onChange: (next: ReplayFilterState) => void;
  /** The served set id (e.g. "9p2i"); context, not a toggle. */
  set: string | null;
  /** Cards after filtering / total before filtering, for the live count. */
  resultCount: number;
  totalCount: number;
  disabled?: boolean;
  /** Outcome reveal (Task 19.10). Required, not optional: an omitted spoiler
   *  gate must be a compile error, never a silent default to "show everything". */
  reveal: boolean;
  /** Turn the reveal on (the connected picker writes the store + the URL key). */
  onReveal: () => void;
}

export function ReplayFilters({
  filters,
  onChange,
  set,
  resultCount,
  totalCount,
  disabled = false,
  reveal,
  onReveal,
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

      {/* Winner + ejection: outcome controls, so they are replaced wholesale by
          one affordance while hidden (Task 19.10). Not disabled-in-place — a
          greyed <select> still carries its option list into the DOM, which is
          exactly the leak. */}
      {reveal ? (
        <>
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
              someone was voted out
            </label>
          </FilterField>
        </>
      ) : (
        <OutcomeFilterGate onReveal={onReveal} disabled={disabled} />
      )}

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
