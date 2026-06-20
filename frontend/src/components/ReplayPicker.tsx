// Replays browser + Highlights reel (Task 12.9; design/phase-12/stage-1-design.md
// §3.1, §2.1, slice 7; the firewall rules in design/phase-12/claude-design-brief.md).
//
// The App.tsx Replays + Highlights routes both mount THIS component (Wave-B mount
// discipline — App.tsx is untouched); it reads `view` from the store to render the
// right surface:
//   • Replays browser  — every recorded replay (`/replays`), enriched with rubric
//                        data by seed when the set ships one.
//   • Highlights reel  — the rubric's `interestingness.per_game[]` (already sorted
//                        best-first), one HighlightCard each.
//
// A URL-driven filter bar (the same `URLSearchParams` pattern as 12.4) reads + syncs
// the shared keys set · winner · winShape · scoreBucket · hasEjection, so a filtered
// reel is shareable + reload-stable and 12.10's histogram deep-links land on the
// right filter. Clicking a card sets the 12.4 store's game (loading the replay) and
// switches to the workspace at tick 0.
//
// Firewall: identity ≠ guilt, outcomes role-neutral — the card keys on drama /
// score, never on who won. The 4p1i default set ships no rubric and is mostly
// zero-meeting, so the empty / zero-meeting state is a first-class path here.
//
// Split for Storybook (cf. MindInspector): the connected `ReplayPicker` owns the
// store + fetch + URL wiring; the presentational `ReplayBrowserView` renders the
// loading / list / empty / error states from props and is what the story drives.

import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { HighlightCard, type HighlightCardData } from "./HighlightCard";
import {
  EMPTY_FILTERS,
  ReplayFilters,
  type ReplayFilterState,
  parseFilterParams,
  scoreBucketOf,
  writeFilterParams,
} from "./ReplayFilters";

import { ApiError, getRubric } from "../api/client";
import { useReplayStore } from "../store/replayStore";
import type {
  ReplayMetadataView,
  RubricGameView,
  RubricView,
} from "../types/api";
import { Banner } from "../ui/Banner";
import { EmptyState } from "../ui/EmptyState";
import { Loading } from "../ui/Loading";

// Debounce the filter → URL write so rapid changes don't thrash history. Both
// this writer and 12.4's transport writer re-read `location.search` at write time
// and only touch their own keys, so the merge is order-independent (12.4 preserves
// these filter keys; see usePlaybackEngine).
const FILTER_URL_DEBOUNCE_MS = 150;

type BrowserView = "replays" | "highlights";
type BrowserStatus = "loading" | "error" | "ready";

// ── pure data shaping ────────────────────────────────────────────────────────

/** Whether a card passes the active filters. Rubric-derived filters exclude
 *  unscored cards (you cannot match a score/shape/ejection a game has no rubric
 *  for) — which is exactly why the 4p1i set lands in the empty state. */
function matchesFilters(card: HighlightCardData, f: ReplayFilterState): boolean {
  if (f.winner !== null && card.winner !== f.winner) {
    return false;
  }
  const rubric = card.rubric;
  if (f.winShape !== null && rubric?.win_shape !== f.winShape) {
    return false;
  }
  if (
    f.scoreBucket !== null &&
    (rubric === null || scoreBucketOf(rubric.score) !== f.scoreBucket)
  ) {
    return false;
  }
  if (f.hasEjection && (rubric === null || rubric.ejected_impostors <= 0)) {
    return false;
  }
  return true;
}

function rubricBySeed(rubric: RubricView | null): Map<number, RubricGameView> {
  const map = new Map<number, RubricGameView>();
  for (const game of rubric?.per_game ?? []) {
    map.set(game.seed, game);
  }
  return map;
}

function metaBySeed(
  list: readonly ReplayMetadataView[] | null,
): Map<number, ReplayMetadataView> {
  const map = new Map<number, ReplayMetadataView>();
  for (const meta of list ?? []) {
    map.set(meta.seed, meta);
  }
  return map;
}

/** Build the ordered card list for a view. Highlights = rubric order (best-first,
 *  already sorted by the scorer); Replays = the loader's replay list, rubric-
 *  enriched by seed. */
function buildCards(
  view: BrowserView,
  rubric: RubricView | null,
  replayList: readonly ReplayMetadataView[] | null,
): HighlightCardData[] {
  if (view === "highlights") {
    const metas = metaBySeed(replayList);
    return (rubric?.per_game ?? []).map((game) => {
      const meta = metas.get(game.seed);
      return {
        key: `h-${game.seed}`,
        gameId: meta?.game_id ?? `headless-seed-${game.seed}`,
        seed: game.seed,
        winner: meta?.winner ?? null,
        totalTicks: meta?.total_ticks ?? null,
        rubric: game,
      };
    });
  }
  const rubrics = rubricBySeed(rubric);
  return (replayList ?? []).map((meta) => ({
    key: `r-${meta.game_id}`,
    gameId: meta.game_id,
    seed: meta.seed,
    winner: meta.winner,
    totalTicks: meta.total_ticks,
    rubric: rubrics.get(meta.seed) ?? null,
  }));
}

function winShapeOptionsOf(rubric: RubricView | null): string[] {
  const shapes = new Set<string>();
  for (const game of rubric?.per_game ?? []) {
    shapes.add(game.win_shape);
  }
  return [...shapes].sort();
}

// ── presentational view (storied) ────────────────────────────────────────────

export interface ReplayBrowserViewProps {
  view: BrowserView;
  status: BrowserStatus;
  error: string | null;
  /** Filtered + ordered cards (the connected component does the filtering). */
  cards: readonly HighlightCardData[];
  /** Card count BEFORE filtering — distinguishes "no data" from "no matches". */
  totalCount: number;
  filters: ReplayFilterState;
  onFiltersChange: (next: ReplayFilterState) => void;
  winShapeOptions: readonly string[];
  set: string | null;
  /** Rubric staleness (git_head ≠ the set's recorded sha) → honesty banner. */
  stale: boolean;
  /** Highlights view, but the served set ships no rubric (the 4p1i case). */
  rubricMissing: boolean;
  onOpen: (gameId: string) => void;
  onBrowseReplays: () => void;
}

export function ReplayBrowserView({
  view,
  status,
  error,
  cards,
  totalCount,
  filters,
  onFiltersChange,
  winShapeOptions,
  set,
  stale,
  rubricMissing,
  onOpen,
  onBrowseReplays,
}: ReplayBrowserViewProps) {
  const isHighlights = view === "highlights";

  const EMPTY_ACTION_BTN =
    "mt-1 rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-1.5 font-mono text-xs font-medium text-ink-900 hover:bg-paper-2";

  let body: ReactNode;
  if (status === "loading") {
    // In-flight cue (Task 12.13): name the set so a set switch reads as
    // "Loading <set>…", not a generic spinner.
    body = (
      <Loading
        label={
          set !== null
            ? `Loading ${set}…`
            : isHighlights
              ? "Loading highlights…"
              : "Loading replays…"
        }
      />
    );
  } else if (status === "error") {
    body = (
      <Banner tone="error">
        Failed to load {isHighlights ? "the rubric" : "replays"}:{" "}
        {error ?? "unknown error"}
      </Banner>
    );
  } else if (isHighlights && rubricMissing) {
    body = (
      <EmptyState title="No interestingness rubric for this set">
        <p>
          The served set{set !== null ? ` (${set})` : ""} ships no rubric —
          expected for the default 4p1i set, which is mostly zero-meeting. A scored
          set (9p2i) populates the reel.
        </p>
        <button type="button" onClick={onBrowseReplays} className={EMPTY_ACTION_BTN}>
          Browse all replays
        </button>
      </EmptyState>
    );
  } else if (cards.length === 0) {
    body =
      totalCount === 0 ? (
        <EmptyState title={isHighlights ? "No scored games" : "No replays found"}>
          {isHighlights
            ? "The rubric carries no per-game scores."
            : "No replays in the configured replay directory."}
        </EmptyState>
      ) : (
        <EmptyState title="No games match these filters">
          <p>Adjust or clear the filters to see more games.</p>
          <button
            type="button"
            onClick={() => {
              onFiltersChange(EMPTY_FILTERS);
            }}
            className={EMPTY_ACTION_BTN}
          >
            Clear filters
          </button>
        </EmptyState>
      );
  } else {
    body = (
      <>
        {/* One banner for an unscored set (Task 12.13): hoists the per-card "Not
            scored" note (the 4p1i common case) up to a single line. */}
        {!isHighlights && rubricMissing && (
          <Banner tone="caveat">
            This set{set !== null ? ` (${set})` : ""} ships no interestingness
            rubric — its games are unscored.
          </Banner>
        )}
        <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {cards.map((card) => (
            <li key={card.key}>
              <HighlightCard
                data={card}
                onOpen={onOpen}
                hideUnscoredNote={!isHighlights && rubricMissing}
              />
            </li>
          ))}
        </ul>
      </>
    );
  }

  return (
    <section
      aria-label={isHighlights ? "Highlights reel" : "Replay browser"}
      className="flex flex-col gap-4"
    >
      <header className="flex flex-col gap-1">
        <h2 className="font-display text-2xl text-ink-900">
          {isHighlights ? "Highlights" : "Replays"}
        </h2>
        <p className="font-mono text-xs text-ink-500">
          {isHighlights
            ? "Games ranked by interestingness — deduction (R1), deception (R2), suspicion arcs (R3), legibility (R7). Best first."
            : "Every recorded replay in the served set. Click a card to open it."}
        </p>
      </header>

      {stale && (
        <Banner tone="caveat">
          Scores may be stale — the rubric was scored against a different commit
          than these replays (git_head mismatch). Treat the numbers as indicative,
          not fresh.
        </Banner>
      )}

      {/* The filter bar is always shown so its keys round-trip even while loading
          / empty (a shared, reload-stable URL contract). */}
      <ReplayFilters
        filters={filters}
        onChange={onFiltersChange}
        winShapeOptions={winShapeOptions}
        set={set}
        resultCount={cards.length}
        totalCount={totalCount}
        disabled={status === "loading"}
      />

      {body}
    </section>
  );
}

// ── set selector (Task 12.12) ─────────────────────────────────────────────────

// The live SET selector: switches the served set with NO reload. Options come
// from `/sets` (auto-grows as new sets are recorded); selecting one calls
// `setSeedSet`, which usePlayback syncs to the existing `set` URL key and which the
// per-set re-fetches key off. Hidden until at least one set is known. Exported so
// the Tournament dashboard reuses the exact control (Task 12.12).
export function SetSelector({
  sets,
  value,
  onChange,
}: {
  sets: readonly string[];
  value: string | null;
  onChange: (set: string) => void;
}) {
  if (sets.length === 0) {
    return null;
  }
  return (
    <label className="flex items-center gap-2">
      <span className="font-mono text-3xs uppercase tracking-wide text-ink-500">
        Set
      </span>
      <select
        className="rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-1 font-mono text-xs font-semibold text-ink-900"
        value={value ?? ""}
        onChange={(e) => {
          onChange(e.target.value);
        }}
        aria-label="Served replay set"
      >
        {value === null && <option value="">…</option>}
        {sets.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
    </label>
  );
}

// ── connected container ──────────────────────────────────────────────────────

export function ReplayPicker() {
  const view = useReplayStore((s) => s.view);
  const replayList = useReplayStore((s) => s.replayList);
  const replayListError = useReplayStore((s) => s.replayListError);
  const currentReplayError = useReplayStore((s) => s.currentReplayError);
  const clearReplayLoadError = useReplayStore((s) => s.clearReplayLoadError);
  const seedSet = useReplayStore((s) => s.seedSet);
  const setSeedSet = useReplayStore((s) => s.setSeedSet);
  const availableSets = useReplayStore((s) => s.availableSets);
  const loadSets = useReplayStore((s) => s.loadSets);
  const availableSetsError = useReplayStore((s) => s.availableSetsError);
  const loadReplayList = useReplayStore((s) => s.loadReplayList);
  const setView = useReplayStore((s) => s.setView);
  const selectReplay = useReplayStore((s) => s.selectReplay);

  // The workspace/tournament routes don't mount this component, so `view` is
  // effectively replays | highlights here; narrow defensively.
  const browserView: BrowserView = view === "highlights" ? "highlights" : "replays";

  // Per-set rubric (the reel's data + the browser's enrichment). 404 → "absent"
  // (the set ships none) is a first-class empty state, NOT an error.
  const [rubric, setRubric] = useState<RubricView | null>(null);
  const [rubricStatus, setRubricStatus] = useState<
    "loading" | "absent" | "error" | "ready"
  >("loading");
  const [rubricError, setRubricError] = useState<string | null>(null);

  // Filters hydrate from the URL at mount (reads), then sync back (the same
  // URLSearchParams pattern as 12.4).
  const [filters, setFilters] = useState<ReplayFilterState>(() =>
    typeof window === "undefined"
      ? EMPTY_FILTERS
      : parseFilterParams(window.location.search),
  );

  // Fetch the available sets on mount (Task 12.12). `loadSets` adopts the server
  // default into `seedSet` when none is active yet, which then drives the per-set
  // fetches below; a deep-linked `set` (already hydrated by usePlayback) is kept.
  useEffect(() => {
    void loadSets();
  }, [loadSets]);

  // Re-fetch the rubric for the ACTIVE set, live, whenever the set changes — no
  // reload. 404 → "absent" (the set ships none, e.g. 4p1i) is a first-class empty
  // state, NOT an error. Skipped until a set is resolved (seedSet !== null).
  useEffect(() => {
    if (seedSet === null) {
      return;
    }
    let cancelled = false;
    setRubricStatus("loading");
    getRubric(seedSet)
      .then((loaded) => {
        if (cancelled) return;
        setRubric(loaded);
        setRubricStatus("ready");
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 404) {
          setRubric(null);
          setRubricStatus("absent");
          return;
        }
        setRubricError(err instanceof Error ? err.message : String(err));
        setRubricStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [seedSet]);

  // Re-fetch the replay list for the active set on change (the store reads the
  // active `seedSet`), so switching sets refreshes the browser live. The initial
  // (null-set) load is App.tsx's mount fetch; this owns every set switch after.
  useEffect(() => {
    if (seedSet === null) {
      return;
    }
    void loadReplayList();
  }, [seedSet, loadReplayList]);

  // Sync filters → URL (debounced). Merges into the live query string so 12.4's
  // keys (set / view / game_id / tick / …) survive; 12.4 likewise preserves these
  // filter keys, so the round-trip is order-independent.
  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const handle = window.setTimeout(() => {
      const search = writeFilterParams(window.location.search, filters);
      const url = `${window.location.pathname}${search}${window.location.hash}`;
      window.history.replaceState(null, "", url);
    }, FILTER_URL_DEBOUNCE_MS);
    return () => {
      window.clearTimeout(handle);
    };
  }, [filters]);

  const allCards = useMemo(
    () => buildCards(browserView, rubric, replayList),
    [browserView, rubric, replayList],
  );
  const cards = useMemo(
    () => allCards.filter((card) => matchesFilters(card, filters)),
    [allCards, filters],
  );
  const winShapeOptions = useMemo(() => winShapeOptionsOf(rubric), [rubric]);

  // Status: the reel is driven by the rubric; the browser by the replay list
  // (rubric is best-effort enrichment there).
  let status: BrowserStatus;
  let error: string | null;
  if (browserView === "highlights") {
    // A /sets failure leaves seedSet null, so the rubric fetch never starts and
    // rubricStatus would hang on "loading" forever — surface the sets error
    // instead of a permanent silent spinner (else the Highlights route dead-ends).
    if (seedSet === null && availableSetsError !== null) {
      status = "error";
      error = availableSetsError;
    } else {
      status =
        rubricStatus === "loading"
          ? "loading"
          : rubricStatus === "error"
            ? "error"
            : "ready";
      error = rubricError;
    }
  } else {
    status =
      replayList === null && replayListError === null
        ? "loading"
        : replayListError !== null
          ? "error"
          : "ready";
    error = replayListError;
  }

  return (
    <div className="flex flex-col gap-4">
      {/* The set selector, or — when /sets failed — an inline retry chip in its
          place (Task 12.13), so a sets outage isn't a silent dead-end. */}
      {availableSets.length === 0 && availableSetsError !== null ? (
        <Banner tone="error">
          Couldn’t load the set list: {availableSetsError}{" "}
          <button
            type="button"
            onClick={() => {
              void loadSets();
            }}
            className="ml-1 rounded-md border-2 border-current px-2 py-0.5 text-xs font-semibold"
          >
            Retry
          </button>
        </Banner>
      ) : (
        <SetSelector sets={availableSets} value={seedSet} onChange={setSeedSet} />
      )}
      {currentReplayError !== null && (
        // Dismissable (Task 12.13): clears ONLY the replay-load error, so a
        // concurrent /replays list failure stays visible (not hidden behind a
        // spinner).
        <Banner tone="error" onDismiss={clearReplayLoadError}>
          Failed to load replay: {currentReplayError}
        </Banner>
      )}
      <ReplayBrowserView
        view={browserView}
        status={status}
        error={error}
        cards={cards}
        totalCount={allCards.length}
        filters={filters}
        onFiltersChange={setFilters}
        winShapeOptions={winShapeOptions}
        // Prefer the ACTIVE set (updates immediately on switch) over the rubric's
        // seedset, which lags behind the in-flight fetch — otherwise the loading
        // cue reads "Loading <old set>…" while the new set loads (Task 12.13 review).
        set={seedSet ?? rubric?.seedset ?? null}
        stale={rubric?.stale ?? false}
        rubricMissing={rubricStatus === "absent"}
        onOpen={(gameId) => {
          void selectReplay(gameId);
        }}
        onBrowseReplays={() => {
          setView("replays");
        }}
      />
    </div>
  );
}
