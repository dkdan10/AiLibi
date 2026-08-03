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
// score, never on who won. The 4p1i set (an explicit `?set=4p1i`, no longer the
// server default — Task 19.9) ships no rubric, so the unscored / zero-meeting
// state is a first-class path here: 11 of its 50 games hold no meeting at all.
//
// Curation (Task 19.9; audits/audit-phase-19-triage.md §7 item 10): a hand-picked
// FEATURED strip leads the browser. The interestingness rubric is an internal
// pacing/structure heuristic, NOT a human rating — it top-scores formulaic
// double-vent stomps and bottom-scores the corpus's most dramatic read (9p2i seed
// 8 at 33.6) — so the featured order is EDITORIAL and every rendered rubric
// scalar on this surface carries that narrow label.
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
import { SectionLabel } from "../ui/SectionLabel";

// Debounce the filter → URL write so rapid changes don't thrash history. Both
// this writer and 12.4's transport writer re-read `location.search` at write time
// and only touch their own keys, so the merge is order-independent (12.4 preserves
// these filter keys; see usePlaybackEngine).
const FILTER_URL_DEBOUNCE_MS = 150;

type BrowserView = "replays" | "highlights";
type BrowserStatus = "loading" | "error" | "ready";

// ── the curated featured list (Task 19.9) ────────────────────────────────────

/** One hand-curated game: which set, which seed, and one line on why to watch. */
export interface FeaturedGame {
  readonly set: string;
  readonly seed: number;
  /** The editorial why-watch line — written by hand, never scorer-derived. */
  readonly label: string;
}

// DATA, not machinery. These are the good-tail games the two Phase-19 audits
// named and read end-to-end (audits/audit-phase-19-input-claude.md §5.3–5.4;
// audits/audit-phase-19-input-codex.md §5.3), with a why-watch line each. The
// interestingness rubric does NOT produce this order and cannot: it ranks 9p2i
// seed 8 last-but-five (33.6) and seed 2 third. Editing this list is an editorial
// act — re-scoring the rubric does not update it.
//
// SPOILER RULE (BINDING, PR #324 review): this strip renders BEFORE any game is
// opened, and a static blurb is prose, not outcome-derived data — so 19.10's
// unspoiled-mode reveal gate cannot cover it, and 19.10's contract explicitly
// forbids copy changes in this file. Each label therefore names the SETUP and the
// question a game poses, never its answer: no winner, no ejection, no vote tally,
// no "who the killer turns out to be". A blurb added later must hold that line.
export const FEATURED_GAMES: readonly FeaturedGame[] = [
  {
    set: "9p2i",
    seed: 2,
    label:
      "Four meetings, four acts: a cold open, a case that nearly lands, and a last meeting that turns on one piece of hard evidence.",
  },
  {
    set: "9p2i",
    seed: 17,
    label:
      "An impostor pair builds a fabricated sighting against a truthful vent witness — watch whose testimony the engine stamps “verified”.",
  },
  {
    set: "9p2i",
    seed: 23,
    label:
      "A sighting that is factually true but provenance-impossible: the flag fires, and nothing asks whether the observer could have seen it.",
  },
  {
    set: "9p2i",
    seed: 8,
    label:
      "The corpus's most contested endgame — and the game the rubric ranks 45th of 50. Read the last ballots against what each voter knew.",
  },
  {
    set: "4p1i",
    seed: 29,
    label:
      "One alibi in the only meeting reads completely differently the second time through — the most Among-Us moment in the corpus.",
  },
  {
    set: "4p1i",
    seed: 2,
    label:
      "The emergency button, pressed with no body ever found: the table has to argue from absence alone.",
  },
  {
    set: "4p1i",
    seed: 41,
    label:
      "The one meeting in the corpus an LLM tie-break decided rather than the flags — two flags of equal weight pointing opposite ways.",
  },
];

/** The featured games for one set, in curated order (empty for an uncurated set). */
export function featuredForSet(set: string | null): readonly FeaturedGame[] {
  return set === null ? [] : FEATURED_GAMES.filter((game) => game.set === set);
}

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

/** A featured game joined to the served replay it opens. */
export interface FeaturedEntry extends FeaturedGame {
  readonly gameId: string;
}

/** The curated strip: hand-picked games with their why-watch lines, best-first by
 *  EDITORIAL judgment (no scalar is shown here — there is none to show). */
function FeaturedStrip({
  entries,
  onOpen,
}: {
  entries: readonly FeaturedEntry[];
  onOpen: (gameId: string) => void;
}) {
  if (entries.length === 0) {
    return null;
  }
  return (
    <section aria-label="Featured games" className="flex flex-col gap-2">
      <SectionLabel as="h3">Featured — picked by hand</SectionLabel>
      <ul className="flex flex-col gap-2">
        {entries.map((entry) => (
          <li key={`f-${entry.set}-${entry.seed}`}>
            <button
              type="button"
              onClick={() => {
                onOpen(entry.gameId);
              }}
              className="flex w-full items-start gap-3 rounded-lg border-2 border-ink-900 bg-paper-0 px-3 py-2 text-left shadow-data hover:bg-paper-2"
            >
              <span className="shrink-0 rounded-pill border-2 border-ink-900 bg-paper-2 px-2 py-0.5 font-mono text-xs font-semibold text-ink-900">
                seed {entry.seed}
              </span>
              <span className="min-w-0 flex-1 text-sm text-ink-900">
                {entry.label}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}

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
  /** Rubric staleness: the rubric's stamped provenance key ≠ the set's own
   *  (the loader recomputes it from MANIFEST.md) → honesty banner. */
  stale: boolean;
  /** Highlights view, but the served set ships no rubric (the 4p1i case). */
  rubricMissing: boolean;
  /** The curated featured games for the served set, joined to their replays
   *  (Task 19.9). Empty for an uncurated set, or before the list loads. */
  featured?: readonly FeaturedEntry[];
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
  featured = [],
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
          expected for 4p1i, the fast technical fixture: median 12 ticks, at most
          one meeting (39 of its 50 games hold exactly one, 11 hold none), and 23
          of 50 decided by the task timer rather than by an ejection. The default
          set, 9p2i, is scored and populates the reel.
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
            scored" note (the 4p1i case) up to a single line. */}
        {!isHighlights && rubricMissing && (
          <Banner tone="caveat">
            This set{set !== null ? ` (${set})` : ""} ships no interestingness
            rubric — its games are unscored. 4p1i is a fast technical fixture
            (median 12 ticks, at most one meeting per game), not the spectator
            set.
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
            ? "Ordered by the interestingness rubric — deduction (R1), deception (R2), suspicion arcs (R3), legibility (R7)."
            : "Every recorded replay in the served set. Click a card to open it."}
        </p>
        {/* The narrow label on the rubric scalar (Task 19.9), shown wherever this
            surface renders a score: it measures pacing/structure, and both
            Phase-19 audits found its ordering inverts the human-interest tails.
            The FEATURED strip is the human ordering. */}
        {(isHighlights || !rubricMissing) && (
          <p className="font-mono text-xs text-ink-500">
            The 0–100 score is an internal pacing/structure heuristic — not a
            human rating, and not a watchability ranking. For games worth
            watching, see Featured below.
          </p>
        )}
      </header>

      {stale && (
        <Banner tone="caveat">
          Scores may be stale — the rubric's stamped provenance key no longer
          matches these replays' recording provenance (their MANIFEST.md rows), so
          it was scored against different bytes. Treat the numbers as indicative,
          not fresh.
        </Banner>
      )}

      <FeaturedStrip entries={featured} onOpen={onOpen} />

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

  // The curated strip for the ACTIVE set, joined to the served replays by seed
  // (Task 19.9). A featured seed the served set does not carry is dropped rather
  // than rendered as a dead link — the list is committed data, the set on disk
  // is the authority.
  const featured = useMemo<readonly FeaturedEntry[]>(() => {
    const metas = metaBySeed(replayList);
    return featuredForSet(seedSet).flatMap((game) => {
      const meta = metas.get(game.seed);
      return meta === undefined ? [] : [{ ...game, gameId: meta.game_id }];
    });
  }, [seedSet, replayList]);

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
        featured={featured}
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
