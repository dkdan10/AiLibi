// Replays browser + "Browse by moment" (Task 12.9; design/phase-12/stage-1-design.md
// §3.1, §2.1, slice 7; the firewall rules in design/phase-12/claude-design-brief.md).
//
// The App.tsx Replays + Highlights routes both mount THIS component (Wave-B mount
// discipline — App.tsx is untouched); it reads `view` from the store to render the
// right surface:
//   • Replays browser  — every served replay (`/replays`), each card joined to
//                        its game's entry in the set's game-shape profile.
//   • Browse by moment — the profile's shelves, in the profile's fixed order,
//                        each listing its games in seed order, then All games.
//
// A URL-driven filter bar (the same `URLSearchParams` pattern as 12.4) reads + syncs
// the shared keys set · winner · hasEjection, so a filtered list is shareable +
// reload-stable. Clicking a card sets the 12.4 store's game (loading the replay)
// and switches to the workspace at tick 0.
//
// No order but the seed: the profile has no score, no rank and no total, and
// nothing here sorts a game by what it holds. A set may ship no profile (the
// four-player set ships none), so the no-profile state is a first-class path, and
// its copy names no set as the expected one.
//
// Curation (Task 19.9; audits/audit-phase-19-triage.md §7 item 10): a hand-picked
// FEATURED strip leads the browser; its order is EDITORIAL.
//
// Unspoiled by default (Task 19.10): the connected container subscribes the
// store's `revealOutcome` and threads it down as a plain `reveal` prop — the
// cards and the filter bar stay presentational. While it is off, no reveal-only
// shelf, its name, its members or its count renders, the cards emit no outcome
// DOM, and both outcome filter criteria go inert (see `matchesFilters`). The two
// halves of "decided without proof" always render together, wrong beside right,
// as the game working. A game a tripwire keeps off the shelves renders on none of
// them and keeps its label under All games. The curated FEATURED strip is
// spoiler-audited prose, not outcome-derived data, so the gate does not cover it.
//
// Split for Storybook (cf. MindInspector): the connected `ReplayPicker` owns the
// store + fetch + URL wiring; the presentational `ReplayBrowserView` renders the
// loading / list / empty / error states from props and is what the story drives.

import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import {
  HighlightCard,
  shelfTitle,
  type CardProfile,
  type HighlightCardData,
} from "./HighlightCard";
import {
  EMPTY_FILTERS,
  ReplayFilters,
  type ReplayFilterState,
  parseFilterParams,
  writeFilterParams,
} from "./ReplayFilters";

import { ApiError, getGameProfile } from "../api/client";
import { PICKER_COPY, PROFILE_COPY, fmt, setOptionLabel } from "../lib/copy";
import { useReplayStore } from "../store/replayStore";
import type { GameProfileView, ReplayMetadataView, ShelfView } from "../types/api";
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

// WHICH games are here is independent of the game-shape profile: three of the five
// (each set's head and the 9p2i second card) are drawn from measured lists, and
// the other two 4p1i cards are hand-picked. Labels state countable facts and
// a setup or question, never an ending, a player, an ejection or a vote tally.
// A lack of detector flags says nothing about how much evidence the agents
// hold. Countable claims are checked against the recordings by
// tests/api/test_sets.py and the browser tests.
//
// The HEAD of each set is measured. A grounded ejection is one where the ejected
// player carries a role_proof flag in the same meeting — the derived category
// for a vent sighting, a spoken observation matched against the speaker's own
// typed vent-witness record. Each set therefore leads with a game whose FIRST
// meeting, the one the viewer's auto-follow opens, ejects on such a flag: the
// tour opens on a table that established something rather than on one that did
// not. Of the eleven 9p2i games that qualify, three (6, 19 and 20) show both
// vent behaviours the map draws before their first meeting, the stretch the
// tour plays before it pauses: a wait of three ticks inside a vent, and a dive
// that meeting's regroup closes. Seed 19 is the one of those whose sighting is a
// second voice: a player other than the body's reporter describes the vent use,
// and that player's ballot and other voters' ballots rest on it.
//
// The second 9p2i card is a measured kind of game too: its first meeting
// ejects an impostor while no flag is raised anywhere in the game and no vent
// event happens at or before that meeting (five games qualify; seed 14 is the
// one that records no vent event at all, and it is not among the games decided
// wrongly without proof). No featured game ejects a crewmate. The two 4p1i
// cards behind that set's head are editorial. Both criteria read the ejected
// player's recorded role; that read is curation: it describes the strip and
// gates no record, instrument or adoption. Reproduce the bands, the eligible
// openers and both lists with
//   uv run python scripts/measure_featured_criterion.py --list
// and see tests/api/test_sets.py, which pins EACH SET'S head and the 9p2i
// second card against these criteria rather than against seeds — per set
// because the tour opens the head of the set it targets — so the next
// re-record re-chooses them instead of quietly keeping these ones.
export const FEATURED_GAMES: readonly FeaturedGame[] = [
  {
    set: "9p2i",
    seed: 19,
    label:
      "Three meetings, nineteen spoken turns, and a reported vent sighting. Which ballots rest on what their voter saw?",
  },
  {
    set: "9p2i",
    seed: 14,
    label:
      "One meeting, eight spoken turns, and no flagged contradictions. What did each voter have to go on?",
  },
  {
    set: "4p1i",
    seed: 2,
    label:
      "A small table, three spoken turns. A player reports seeing someone use a vent. Compare that against what each ballot cites.",
  },
  {
    set: "4p1i",
    seed: 11,
    label:
      "One short meeting with no flagged contradictions. Compare the players' statements before they decide.",
  },
  {
    set: "4p1i",
    seed: 29,
    label:
      "One meeting, three turns, and no flagged contradictions. Compare each player's observations with the claims made aloud.",
  },
];

/** The featured games for one set, in curated order (empty for an uncurated set). */
export function featuredForSet(set: string | null): readonly FeaturedGame[] {
  return set === null ? [] : FEATURED_GAMES.filter((game) => game.set === set);
}

// ── pure data shaping ────────────────────────────────────────────────────────

/** Whether a card passes the active filters.
 *
 *  `reveal` (Task 19.10) makes both OUTCOME criteria — winner, ejection — inert
 *  while outcomes are hidden. ReplayFilters hides those controls unrevealed, and
 *  a hidden control must not keep acting: otherwise a deep link carrying
 *  `?winner=IMPOSTORS` would silently shrink the grid with no visible cause, and
 *  the result COUNT would itself be an outcome statistic. The URL keys are left
 *  untouched, so revealing re-applies them exactly. The ejection criterion reads
 *  whether some meeting voted someone out, from the profile's reveal facets, so
 *  a card with no profile entry cannot match it. */
export function matchesFilters(
  card: HighlightCardData,
  f: ReplayFilterState,
  reveal: boolean,
): boolean {
  if (reveal && f.winner !== null && card.winner !== f.winner) {
    return false;
  }
  if (
    reveal &&
    f.hasEjection &&
    (card.profile?.revealFacets?.ejections.length ?? 0) === 0
  ) {
    return false;
  }
  return true;
}

function membersOf(shelf: ShelfView): ReadonlySet<number> {
  return new Set(shelf.members.map((member) => member.seed));
}

/** Each game's profile entry, keyed by seed. Empty for a stale profile. */
export function cardProfiles(profile: GameProfileView | null): Map<number, CardProfile> {
  const map = new Map<number, CardProfile>();
  if (profile === null || profile.stale) {
    return map;
  }
  const pre = profile.pre_reveal.shelves.map((shelf) => [shelf.name, membersOf(shelf)] as const);
  const pair = profile.reveal.decided_without_proof;
  const reveal = [...profile.reveal.shelves, pair.right, pair.wrong].map(
    (shelf) => [shelf.name, membersOf(shelf)] as const,
  );
  const revealFacets = new Map(profile.reveal.games.map((game) => [game.seed, game]));
  for (const facets of profile.pre_reveal.games) {
    map.set(facets.seed, {
      facets,
      revealFacets: revealFacets.get(facets.seed) ?? null,
      shelves: pre.filter(([, seeds]) => seeds.has(facets.seed)).map(([name]) => name),
      revealShelves: reveal.filter(([, seeds]) => seeds.has(facets.seed)).map(([name]) => name),
      eyewitness: profile.pre_reveal.chips.flatMap((chip) =>
        chip.members.filter((member) => member.seed === facets.seed).flatMap((m) => m.meetings),
      ),
    });
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

/** The card for every served replay, in the loader's seed-sorted listing,
 *  joined to its profile entry by seed. */
export function buildCards(
  profile: GameProfileView | null,
  replayList: readonly ReplayMetadataView[] | null,
): HighlightCardData[] {
  const profiles = cardProfiles(profile);
  return (replayList ?? []).map((meta) => ({
    key: `r-${meta.game_id}`,
    gameId: meta.game_id,
    seed: meta.seed,
    winner: meta.winner,
    completionStatus: meta.completion_status,
    totalTicks: meta.total_ticks,
    profile: profiles.get(meta.seed) ?? null,
  }));
}

/** One list on the "Browse by moment" page: a shelf, the pair, or All games. */
export interface ReelSection {
  readonly key: string;
  readonly kind: "shelf" | "reveal" | "all";
  readonly name: string;
  readonly seeds: readonly number[];
}

/**
 * The page's lists, in the profile's fixed shelf order, each in seed order.
 *
 * Before the reveal: the shelves before the reveal, then All games. With the
 * reveal on, the reveal-only shelves and the two halves of the pair join after
 * them. A game a tripwire keeps off the shelves is listed only under All games.
 */
export function reelSections(profile: GameProfileView, reveal: boolean): ReelSection[] {
  const tripped = new Set(
    profile.pre_reveal.games.filter((game) => game.tripped.length > 0).map((game) => game.seed),
  );
  const shelf = (view: ShelfView, kind: ReelSection["kind"]): ReelSection => ({
    key: `${kind}-${view.name}`,
    kind,
    name: view.name,
    seeds: view.members
      .map((member) => member.seed)
      .filter((seed) => !tripped.has(seed))
      .sort((a, b) => a - b),
  });
  const sections = profile.pre_reveal.shelves.map((view) => shelf(view, "shelf"));
  if (reveal) {
    const pair = profile.reveal.decided_without_proof;
    sections.push(
      ...profile.reveal.shelves.map((view) => shelf(view, "reveal")),
      shelf(pair.wrong, "reveal"),
      shelf(pair.right, "reveal"),
    );
  }
  sections.push({
    key: "all",
    kind: "all",
    name: "all",
    seeds: profile.pre_reveal.games.map((game) => game.seed).sort((a, b) => a - b),
  });
  return sections;
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

function countText(count: number): string {
  return fmt(count === 1 ? PROFILE_COPY.countOne : PROFILE_COPY.countMany, {
    count: String(count),
  });
}

function CardGrid({
  cards,
  onOpen,
  reveal,
}: {
  cards: readonly HighlightCardData[];
  onOpen: (gameId: string) => void;
  reveal: boolean;
}) {
  return (
    <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {cards.map((card) => (
        <li key={card.key}>
          <HighlightCard data={card} onOpen={onOpen} reveal={reveal} />
        </li>
      ))}
    </ul>
  );
}

/** One shelf: its title, what it means, how many games it lists, and the games.
 *  A shelf that lists no game here (none in the set, none baked into this
 *  build, or none left by the filters) renders nothing. */
function ShelfSection({
  name,
  cards,
  onOpen,
  reveal,
}: {
  name: string;
  cards: readonly HighlightCardData[];
  onOpen: (gameId: string) => void;
  reveal: boolean;
}) {
  const words = (PROFILE_COPY.shelves as Readonly<Record<string, { description: string }>>)[name];
  if (cards.length === 0) {
    return null;
  }
  return (
    <section aria-label={shelfTitle(name)} className="flex flex-col gap-2">
      <SectionLabel as="h3">
        {shelfTitle(name)} · {countText(cards.length)}
      </SectionLabel>
      <p className="text-sm text-ink-700">{words?.description}</p>
      <CardGrid cards={cards} onOpen={onOpen} reveal={reveal} />
    </section>
  );
}

/** The two halves of "decided without proof", always together: wrong beside right. */
function PairBlock({
  wrong,
  right,
  onOpen,
}: {
  wrong: readonly HighlightCardData[];
  right: readonly HighlightCardData[];
  onOpen: (gameId: string) => void;
}) {
  const half = (name: string, cards: readonly HighlightCardData[]) => {
    const words = (PROFILE_COPY.shelves as Readonly<Record<string, { description: string }>>)[
      name
    ];
    return (
      <section aria-label={shelfTitle(name)} className="flex min-w-0 flex-1 flex-col gap-2">
        <SectionLabel as="h4">
          {shelfTitle(name)} · {countText(cards.length)}
        </SectionLabel>
        <p className="text-sm text-ink-700">{words?.description}</p>
        {cards.length === 0 ? (
          <p className="font-mono text-xs text-ink-500">{PROFILE_COPY.pair.emptyHalf}</p>
        ) : (
          <ul className="flex flex-col gap-3">
            {cards.map((card) => (
              <li key={card.key}>
                <HighlightCard data={card} onOpen={onOpen} reveal />
              </li>
            ))}
          </ul>
        )}
      </section>
    );
  };
  return (
    <section aria-label={PROFILE_COPY.pair.heading} className="flex flex-col gap-2">
      <SectionLabel as="h3">{PROFILE_COPY.pair.heading}</SectionLabel>
      <p className="text-sm text-ink-700">{PROFILE_COPY.pair.note}</p>
      <div className="flex flex-col gap-4 md:flex-row">
        {half("decided_without_proof_wrong", wrong)}
        {half("decided_without_proof_right", right)}
      </div>
    </section>
  );
}

/** The "Browse by moment" page body: the reel's lists, in order. */
function MomentReel({
  profile,
  cards,
  reveal,
  onOpen,
}: {
  profile: GameProfileView;
  cards: readonly HighlightCardData[];
  reveal: boolean;
  onOpen: (gameId: string) => void;
}) {
  const bySeed = new Map(cards.map((card) => [card.seed, card]));
  const pick = (seeds: readonly number[]) =>
    seeds.flatMap((seed) => {
      const card = bySeed.get(seed);
      return card === undefined ? [] : [card];
    });
  const sections = reelSections(profile, reveal);
  const pre = sections.filter((section) => section.kind === "shelf");
  const revealed = sections.filter((section) => section.kind === "reveal");
  const all = sections.find((section) => section.kind === "all");
  const wrong = revealed.find((section) => section.name === "decided_without_proof_wrong");
  const right = revealed.find((section) => section.name === "decided_without_proof_right");
  const revealShelves = revealed.filter((section) => section !== wrong && section !== right);
  return (
    <div className="flex flex-col gap-6">
      {pre.map((section) => (
        <ShelfSection
          key={section.key}
          name={section.name}
          cards={pick(section.seeds)}
          onOpen={onOpen}
          reveal={reveal}
        />
      ))}
      {reveal && (
        <section aria-label={PROFILE_COPY.revealHeading} className="flex flex-col gap-6">
          <header className="flex flex-col gap-1">
            <h3 className="font-display text-xl text-ink-900">{PROFILE_COPY.revealHeading}</h3>
            <p className="font-mono text-xs text-ink-500">{PROFILE_COPY.revealNote}</p>
          </header>
          {revealShelves.map((section) => (
            <ShelfSection
              key={section.key}
              name={section.name}
              cards={pick(section.seeds)}
              onOpen={onOpen}
              reveal={reveal}
            />
          ))}
          {wrong !== undefined && right !== undefined && (
            <PairBlock wrong={pick(wrong.seeds)} right={pick(right.seeds)} onOpen={onOpen} />
          )}
        </section>
      )}
      {all !== undefined && (
        <section aria-label={PROFILE_COPY.allGames} className="flex flex-col gap-2">
          <SectionLabel as="h3">
            {PROFILE_COPY.allGames} · {countText(pick(all.seeds).length)}
          </SectionLabel>
          <p className="text-sm text-ink-700">{PROFILE_COPY.allGamesNote}</p>
          <CardGrid cards={pick(all.seeds)} onOpen={onOpen} reveal={reveal} />
        </section>
      )}
    </div>
  );
}

export interface ReplayBrowserViewProps {
  view: BrowserView;
  status: BrowserStatus;
  error: string | null;
  /** Filtered cards, in the loader's seed-sorted listing (the connected
   *  component does the filtering). */
  cards: readonly HighlightCardData[];
  /** Card count BEFORE filtering — distinguishes "no data" from "no matches". */
  totalCount: number;
  filters: ReplayFilterState;
  onFiltersChange: (next: ReplayFilterState) => void;
  set: string | null;
  /** The set's game-shape profile, or `null` while absent or loading. */
  profile: GameProfileView | null;
  /** The served set ships no profile (the eval route answered 404). */
  profileMissing: boolean;
  /** The curated featured games for the served set, joined to their replays
   *  (Task 19.9). Empty for an uncurated set, or before the list loads. */
  featured?: readonly FeaturedEntry[];
  /** Outcome reveal (Task 19.10): threaded straight down to the cards and the
   *  filter bar, which own the actual gating. */
  reveal: boolean;
  /** Turn the reveal on from the filter bar's spoiler-warned affordance. */
  onReveal: () => void;
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
  set,
  profile,
  profileMissing,
  featured = [],
  reveal,
  onReveal,
  onOpen,
  onBrowseReplays,
}: ReplayBrowserViewProps) {
  const isHighlights = view === "highlights";
  const stale = profile?.stale ?? false;

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
              ? PROFILE_COPY.loading
              : "Loading replays…"
        }
      />
    );
  } else if (status === "error") {
    body = (
      <Banner tone="error">
        {isHighlights ? PROFILE_COPY.loadError : "Failed to load replays:"}{" "}
        {error ?? "unknown error"}
      </Banner>
    );
  } else if (isHighlights && profileMissing) {
    body = (
      <EmptyState title={PROFILE_COPY.absentTitle}>
        {/* Set-neutral: it names no set as the one expected to ship none and
            states no per-set count, so it reads true on any set served without
            a profile, revealed or not. */}
        <p>
          {set !== null
            ? fmt(PROFILE_COPY.absentBody, { set: setOptionLabel(set) })
            : PROFILE_COPY.absentBodyUnnamed}
        </p>
        <button type="button" onClick={onBrowseReplays} className={EMPTY_ACTION_BTN}>
          {PROFILE_COPY.browseReplays}
        </button>
      </EmptyState>
    );
  } else if (isHighlights && stale) {
    body = (
      <EmptyState title={PROFILE_COPY.staleTitle}>
        <p>{PROFILE_COPY.staleBody}</p>
        <button type="button" onClick={onBrowseReplays} className={EMPTY_ACTION_BTN}>
          {PROFILE_COPY.browseReplays}
        </button>
      </EmptyState>
    );
  } else if (cards.length === 0) {
    body =
      totalCount === 0 ? (
        <EmptyState title="No replays found">
          No replays in the configured replay directory.
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
  } else if (isHighlights && profile !== null) {
    body = <MomentReel profile={profile} cards={cards} reveal={reveal} onOpen={onOpen} />;
  } else {
    body = (
      <>
        {!isHighlights && profileMissing && (
          <Banner tone="caveat">
            {fmt(PROFILE_COPY.replaysNoProfile, {
              set: set !== null ? setOptionLabel(set) : "",
            })}
          </Banner>
        )}
        <CardGrid cards={cards} onOpen={onOpen} reveal={reveal} />
      </>
    );
  }

  return (
    <section
      aria-label={isHighlights ? PROFILE_COPY.heading : "Replay browser"}
      className="flex flex-col gap-4"
    >
      <header className="flex flex-col gap-1">
        <h2 className="font-display text-2xl text-ink-900">
          {isHighlights ? PROFILE_COPY.heading : "Replays"}
        </h2>
        <p className="font-mono text-xs text-ink-500">
          {isHighlights ? PICKER_COPY.highlightsIntro : PICKER_COPY.replaysIntro}
        </p>
      </header>

      <FeaturedStrip entries={featured} onOpen={onOpen} />

      {/* The filter bar is always shown so its keys round-trip even while loading
          / empty (a shared, reload-stable URL contract). */}
      <ReplayFilters
        filters={filters}
        onChange={onFiltersChange}
        set={set}
        resultCount={cards.length}
        totalCount={totalCount}
        disabled={status === "loading"}
        reveal={reveal}
        onReveal={onReveal}
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
            {setOptionLabel(s)}
          </option>
        ))}
      </select>
    </label>
  );
}

// ── the profile request and the browser's status (pure) ─────────────────────

/** The set's profile request: loading, then ready, absent (a 404: the set ships
 *  none, a first-class empty state, not an error) or failed. */
export type ProfileLoad =
  | { readonly status: "loading"; readonly profile: null; readonly error: null }
  | { readonly status: "ready"; readonly profile: GameProfileView; readonly error: null }
  | { readonly status: "absent"; readonly profile: null; readonly error: null }
  | { readonly status: "error"; readonly profile: null; readonly error: string };

const PROFILE_LOADING: ProfileLoad = { status: "loading", profile: null, error: null };

/** A settled profile request, tagged with the set it was made for. */
export interface SetProfileLoad {
  readonly set: string;
  readonly load: ProfileLoad;
}

/** The active set's profile: loading until a request made for that set settles,
 *  so a live set switch never shows the previous set's shelves. */
export function activeProfile(settled: SetProfileLoad | null, seedSet: string | null): ProfileLoad {
  return settled !== null && settled.set === seedSet ? settled.load : PROFILE_LOADING;
}

/** What the set's profile request settles to. */
export async function settledProfile(request: Promise<GameProfileView>): Promise<ProfileLoad> {
  try {
    return { status: "ready", profile: await request, error: null };
  } catch (err: unknown) {
    if (err instanceof ApiError && err.status === 404) {
      return { status: "absent", profile: null, error: null };
    }
    return {
      status: "error",
      profile: null,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}

/** The browser's status. The reel is driven by the profile and the replay list;
 *  the Replays browser by the replay list (the profile only enriches it). */
export function browserState(input: {
  readonly view: BrowserView;
  readonly seedSet: string | null;
  readonly availableSetsError: string | null;
  readonly profile: ProfileLoad;
  readonly replayList: readonly ReplayMetadataView[] | null;
  readonly replayListError: string | null;
}): { readonly status: BrowserStatus; readonly error: string | null } {
  if (input.view === "highlights") {
    // A /sets failure leaves seedSet null, so the profile fetch never starts and
    // the request would read "loading" forever: surface the sets error instead
    // of a permanent silent spinner (else the Highlights route dead-ends).
    if (input.seedSet === null && input.availableSetsError !== null) {
      return { status: "error", error: input.availableSetsError };
    }
    if (input.profile.status === "error") {
      return { status: "error", error: input.profile.error };
    }
    if (input.replayListError !== null) {
      return { status: "error", error: input.replayListError };
    }
    const waiting = input.profile.status === "loading" || input.replayList === null;
    return { status: waiting ? "loading" : "ready", error: null };
  }
  if (input.replayListError !== null) {
    return { status: "error", error: input.replayListError };
  }
  return { status: input.replayList === null ? "loading" : "ready", error: null };
}

// ── connected container ──────────────────────────────────────────────────────

export function ReplayPicker() {
  const view = useReplayStore((s) => s.view);
  const replayList = useReplayStore((s) => s.replayList);
  const replayListError = useReplayStore((s) => s.replayListError);
  // The REPLAY-LOAD failure specifically (Task 19.12's error-field split): this
  // banner says "Failed to load replay", so it must read the field that only a
  // failed `selectReplay` writes — before the split it could print a memory or
  // meeting-transcript failure under that sentence.
  const replayLoadError = useReplayStore((s) => s.replayLoadError);
  const clearReplayLoadError = useReplayStore((s) => s.clearReplayLoadError);
  const seedSet = useReplayStore((s) => s.seedSet);
  const setSeedSet = useReplayStore((s) => s.setSeedSet);
  const availableSets = useReplayStore((s) => s.availableSets);
  const loadSets = useReplayStore((s) => s.loadSets);
  const availableSetsError = useReplayStore((s) => s.availableSetsError);
  const loadReplayList = useReplayStore((s) => s.loadReplayList);
  const setView = useReplayStore((s) => s.setView);
  const selectReplay = useReplayStore((s) => s.selectReplay);
  // Outcome reveal (Task 19.10). Global, URL-round-tripped state — deliberately
  // NOT local to this surface, so the browser's gate and the finale card's
  // Reveal/Hide drive ONE flag and one `reveal` URL key. Note the scope,
  // though: `selectReplay` deliberately resets the flag, so revealing here and
  // then opening a game still starts that game UNSPOILED (a reveal is a choice
  // about one game's ending, not a mode you carry forward); only an explicit
  // `&reveal=1` deep link survives the reset, re-applied by usePlaybackEngine's
  // deferred hydration.
  const revealOutcome = useReplayStore((s) => s.revealOutcome);
  const setRevealOutcome = useReplayStore((s) => s.setRevealOutcome);

  // The workspace/tournament routes don't mount this component, so `view` is
  // effectively replays | highlights here; narrow defensively.
  const browserView: BrowserView = view === "highlights" ? "highlights" : "replays";

  // The set's game-shape profile (the reel's lists + the cards' entries): the last
  // settled request, read as loading until one made for the active set settles.
  const [settled, setSettled] = useState<SetProfileLoad | null>(null);
  const profileLoad = activeProfile(settled, seedSet);

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

  // Re-fetch the profile for the ACTIVE set, live, whenever the set changes — no
  // reload. Skipped until a set is resolved (seedSet !== null).
  useEffect(() => {
    if (seedSet === null) {
      return;
    }
    let cancelled = false;
    void settledProfile(getGameProfile(seedSet)).then((load) => {
      if (!cancelled) {
        setSettled({ set: seedSet, load });
      }
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
    () => buildCards(profileLoad.profile, replayList),
    [profileLoad, replayList],
  );
  const cards = useMemo(
    () => allCards.filter((card) => matchesFilters(card, filters, revealOutcome)),
    [allCards, filters, revealOutcome],
  );

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

  const { status, error } = browserState({
    view: browserView,
    seedSet,
    availableSetsError,
    profile: profileLoad,
    replayList,
    replayListError,
  });

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
      {replayLoadError !== null && (
        // Dismissable (Task 12.13): clears ONLY the replay-load error, so a
        // concurrent /replays list failure stays visible (not hidden behind a
        // spinner).
        <Banner tone="error" onDismiss={clearReplayLoadError}>
          Failed to load replay: {replayLoadError}
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
        // Prefer the ACTIVE set (updates immediately on switch) over the profile's
        // seedset, which lags behind the in-flight fetch — otherwise the loading
        // cue reads "Loading <old set>…" while the new set loads (Task 12.13 review).
        set={seedSet ?? profileLoad.profile?.seedset ?? null}
        profile={profileLoad.profile}
        profileMissing={profileLoad.status === "absent"}
        featured={featured}
        reveal={revealOutcome}
        onReveal={() => {
          setRevealOutcome(true);
        }}
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
