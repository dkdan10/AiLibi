// Stories for the replay browser + Highlights reel (Task 12.9; design/phase-12/
// stage-1-design.md §3.1, §2.1, slice 7). They drive the PRESENTATIONAL
// <ReplayBrowserView/> — the connected <ReplayPicker/> only adds the store + fetch
// + URL wiring, which Storybook can't host — with mock DTOs in the served shape so
// every required state is visible in isolation:
//   • loading / list / empty / error (the contract's state set);
//   • the first-class empty / zero-meeting paths (the 4p1i set ships no rubric, so
//     "no rubric" + zero-meeting cards are common, not edges);
//   • the staleness banner (git_head mismatch) and the role-neutral cards.

import type { Meta, StoryObj } from "@storybook/react-vite";

import type { HighlightCardData } from "../components/HighlightCard";
import { EMPTY_FILTERS } from "../components/ReplayFilters";
import { ReplayBrowserView } from "../components/ReplayPicker";
import type { RubricGameView, Winner } from "../types/api";

// A realistic 9p2i rubric row with sensible defaults; override per card.
function rubricGame(over: Partial<RubricGameView> & { seed: number }): RubricGameView {
  return {
    score: 50,
    reason: "CREWMATE_EJECT",
    n_meetings: 2,
    win_shape: "eject-decided",
    ejected_impostors: 1,
    accused_impostors: 2,
    survived_accused: 0,
    r1_decisive: 1,
    r2_deception: 0.2,
    r3_arcs: 1,
    r7_legible: 1,
    ...over,
  };
}

function card(
  seed: number,
  winner: Winner | null,
  rubric: RubricGameView | null,
  totalTicks: number | null = 420,
): HighlightCardData {
  return {
    key: `seed-${seed}`,
    gameId: `headless-seed-${seed}`,
    seed,
    winner,
    totalTicks,
    rubric,
  };
}

// A varied reel: a top eject-decided game, a stopwatch win, an impostor win where
// deception survived, and a zero-meeting game (drama line + sub-scores degrade
// honestly, never to a broken panel).
const REEL_CARDS: HighlightCardData[] = [
  card(5, "CREWMATES", rubricGame({ seed: 5, score: 80, win_shape: "eject-decided", n_meetings: 2, ejected_impostors: 2, accused_impostors: 1, r2_deception: 0.2, r3_arcs: 1, r7_legible: 1 })),
  card(47, "CREWMATES", rubricGame({ seed: 47, score: 73.3, win_shape: "eject-decided", n_meetings: 3, ejected_impostors: 2, accused_impostors: 2, r7_legible: 0.67 })),
  card(12, "IMPOSTORS", rubricGame({ seed: 12, score: 58.5, reason: "IMPOSTOR_PARITY", win_shape: "impostor-win", n_meetings: 2, ejected_impostors: 0, accused_impostors: 2, survived_accused: 2, r1_decisive: 0, r2_deception: 1, r3_arcs: 0.5, r7_legible: 0.5 })),
  card(31, "CREWMATES", rubricGame({ seed: 31, score: 41.5, win_shape: "stopwatch-some-eject", n_meetings: 1, ejected_impostors: 1, accused_impostors: 1, r1_decisive: 0.5, r2_deception: 0.2, r3_arcs: 0, r7_legible: 1 })),
  card(8, "CREWMATES", rubricGame({ seed: 8, score: 18, win_shape: "stopwatch-no-meeting", n_meetings: 0, ejected_impostors: 0, accused_impostors: 0, survived_accused: 0, r1_decisive: 0, r2_deception: 0, r3_arcs: 0, r7_legible: 0 })),
  card(23, "IMPOSTORS", rubricGame({ seed: 23, score: 15, reason: "IMPOSTOR_PARITY", win_shape: "impostor-win", n_meetings: 0, ejected_impostors: 0, accused_impostors: 0, survived_accused: 0, r1_decisive: 0, r2_deception: 0.4, r3_arcs: 0, r7_legible: 0 })),
];

const WIN_SHAPES = [
  "eject-decided",
  "impostor-win",
  "stopwatch-no-meeting",
  "stopwatch-some-eject",
];

// The 4p1i browser: replays with NO rubric (unscored cards), the common default.
const UNSCORED_CARDS: HighlightCardData[] = [
  card(0, "CREWMATES", null, 510),
  card(1, "CREWMATES", null, 488),
  card(2, "IMPOSTORS", null, 372),
  card(3, "CREWMATES", null, 521),
];

const meta: Meta<typeof ReplayBrowserView> = {
  title: "Browser/ReplayBrowser",
  component: ReplayBrowserView,
  parameters: { layout: "fullscreen" },
  decorators: [
    (Story) => (
      <div className="min-h-screen bg-paper-1 p-6 text-ink-900">
        <Story />
      </div>
    ),
  ],
  args: {
    view: "highlights",
    status: "ready",
    error: null,
    cards: REEL_CARDS,
    totalCount: REEL_CARDS.length,
    filters: EMPTY_FILTERS,
    onFiltersChange: () => {},
    winShapeOptions: WIN_SHAPES,
    set: "9p2i",
    stale: false,
    rubricMissing: false,
    onOpen: () => {},
    onBrowseReplays: () => {},
  },
};

export default meta;
type Story = StoryObj<typeof ReplayBrowserView>;

// LIST — the Highlights reel, best-first, with the four shapes and a zero-meeting
// card showing the honest "No meetings" degrade.
export const List: Story = {};

// LOADING — the rubric is still in flight.
export const Loading: Story = {
  args: { status: "loading", cards: [], totalCount: 0 },
};

// EMPTY (no rubric) — the 4p1i common case: the set ships no rubric, so the reel
// shows a real, explanatory empty state, not a broken panel.
export const EmptyNoRubric: Story = {
  args: {
    status: "ready",
    rubricMissing: true,
    cards: [],
    totalCount: 0,
    set: "4p1i",
    winShapeOptions: [],
  },
};

// EMPTY (no matches) — filters exclude every game (e.g. impostor wins only).
export const EmptyNoMatches: Story = {
  args: {
    status: "ready",
    cards: [],
    totalCount: REEL_CARDS.length,
    filters: { ...EMPTY_FILTERS, winner: "IMPOSTORS", scoreBucket: "high" },
  },
};

// ERROR — the rubric fetch failed (a 500, not a 404 — 404 is the empty state).
export const Error: Story = {
  args: {
    status: "error",
    error: "API request to /api/eval/rubric failed (status 500): internal error",
    cards: [],
    totalCount: 0,
  },
};

// STALE — the rubric's git_head ≠ the set's recorded sha: scores shown with the
// honesty banner, never passed off as fresh.
export const Stale: Story = {
  args: { stale: true },
};

// REPLAYS BROWSER — the 4p1i set with no rubric: every card is unscored, rendered
// as a real "Not scored" state rather than an empty score panel.
export const ReplaysBrowserUnscored: Story = {
  args: {
    view: "replays",
    cards: UNSCORED_CARDS,
    totalCount: UNSCORED_CARDS.length,
    set: "4p1i",
    winShapeOptions: [],
  },
};
