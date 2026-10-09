// Stories for the replay browser + "Browse by moment" (Task 12.9; design/phase-12/
// stage-1-design.md §3.1, §2.1, slice 7). They drive the PRESENTATIONAL
// <ReplayBrowserView/> — the connected <ReplayPicker/> only adds the store + fetch
// + URL wiring, which Storybook can't host — with mock DTOs in the served shape so
// every required state is visible in isolation:
//   • loading / list / empty / error (the contract's state set);
//   • the shelves before and after the reveal, the pair with an empty half, and
//     a game a tripwire keeps off the shelves;
//   • the no-profile and stale states and the role-neutral cards.

import type { Meta, StoryObj } from "@storybook/react-vite";

import { EMPTY_FILTERS } from "../components/ReplayFilters";
import { ReplayBrowserView, buildCards } from "../components/ReplayPicker";
import type {
  GameFacetsView,
  GameProfileView,
  ReplayMetadataView,
  Winner,
} from "../types/api";

function facets(seed: number, meetings: number, tripped = false): GameFacetsView {
  return {
    seed,
    ticks: 30 + seed,
    meetings: Array.from({ length: meetings }, (_, index) => ({
      index,
      tick: 10 + index * 12,
      trigger: "report" as const,
      regrouped: index < meetings - 1,
    })),
    kills: [
      { tick: 5, in_wave: false },
      { tick: 19, in_wave: meetings > 0 },
    ],
    reports: meetings > 0 ? [{ meeting: 0, corpse_age: 5 }] : [],
    bodies_never_found: meetings > 0 ? 1 : 2,
    moments: [],
    tripped: tripped ? [{ tripwire: "decided_by_a_vote_that_held_nothing", meeting: 1 }] : [],
  };
}

function member(seed: number) {
  return { seed, meetings: [0], kill_ticks: [] };
}

const SEEDS = [5, 8, 12, 23, 26, 31];

const PROFILE: GameProfileView = {
  viewModelVersion: "6",
  rubric_version: 2,
  era: "stage-b-r2",
  manifest_key: "43b5ee45",
  source_fingerprint: "sha256:0",
  seedset: "9p2i",
  stale: false,
  constants: {
    slow_burn_ticks: 20,
    wave_slack_ticks: 4,
    close_call_margin: 1,
    third_round_meetings: 3,
    down_to_the_wire_start: 3,
    runaway_share: "1/2",
    leak_p_level: "0.05",
    saturation_share: "3/4",
  },
  catalogue: [],
  pre_reveal: {
    shelves: [
      { name: "the_reporter_saw_it_happen", members: [member(5), member(31)] },
      { name: "double_kill", members: [member(12)] },
      { name: "slow_burn", members: [member(5), member(23)] },
      { name: "a_third_round", members: [member(31)] },
    ],
    chips: [{ name: "an_eyewitness_voted_on_it", members: [{ seed: 5, meetings: [0] }] }],
    games: [facets(5, 2), facets(8, 0), facets(12, 2), facets(23, 1), facets(26, 2, true), facets(31, 3)],
    tripwires: { readings: [] },
  },
  reveal: {
    shelves: [
      { name: "caught_venting", members: [member(31)] },
      { name: "runaway", members: [member(12)] },
    ],
    decided_without_proof: {
      right: { name: "decided_without_proof_right", members: [member(5), member(31)] },
      wrong: { name: "decided_without_proof_wrong", members: [] },
    },
    games: SEEDS.map((seed) => ({
      seed,
      ending: seed === 12 || seed === 23 ? "IMPOSTOR_PARITY" : "CREWMATE_EJECT",
      distance: { counts: "kills_short_of_parity" as const, steps: 2, start: 5 },
      sabotage_starts: [],
      tasks_done: 10,
      tasks_assigned: 14,
      ejections: seed === 8 ? [] : [{ meeting: 0, right: seed !== 26 }],
    })),
  },
};

function meta(seed: number, winner: Winner | null): ReplayMetadataView {
  return {
    game_id: `headless-seed-${seed}`,
    seed,
    total_ticks: 30 + seed,
    winner,
    winner_reason: null,
    meeting_count: 2,
    total_cost_usd: 0,
    prompt_versions: {},
    created_at: null,
  };
}

const LIST: ReplayMetadataView[] = SEEDS.map((seed) =>
  meta(seed, seed === 12 || seed === 23 ? "IMPOSTORS" : "CREWMATES"),
);
const CARDS = buildCards(PROFILE, LIST);

const storyMeta: Meta<typeof ReplayBrowserView> = {
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
    cards: CARDS,
    totalCount: CARDS.length,
    filters: EMPTY_FILTERS,
    onFiltersChange: () => {},
    set: "9p2i",
    profile: PROFILE,
    profileMissing: false,
    reveal: false,
    onReveal: () => {},
    onOpen: () => {},
    onBrowseReplays: () => {},
  },
};

export default storyMeta;
type Story = StoryObj<typeof ReplayBrowserView>;

// LIST — the shelves before the reveal, in the profile's order, then All games;
// seed 26 sits on none and carries its label.
export const List: Story = {};

// REVEALED — the reveal-only shelves and the pair, wrong beside right, the empty
// half saying so.
export const Revealed: Story = {
  args: { reveal: true },
};

// LOADING — the profile is still in flight.
export const Loading: Story = {
  args: { status: "loading", cards: [], totalCount: 0 },
};

// EMPTY (no profile) — the set ships none, so the page shows a real,
// explanatory empty state, not a broken panel.
export const EmptyNoProfile: Story = {
  args: {
    status: "ready",
    profile: null,
    profileMissing: true,
    cards: buildCards(null, LIST),
    totalCount: LIST.length,
    set: "4p1i",
  },
};

// EMPTY (no matches) — filters exclude every game.
export const EmptyNoMatches: Story = {
  args: {
    status: "ready",
    cards: [],
    totalCount: CARDS.length,
    reveal: true,
    filters: { ...EMPTY_FILTERS, winner: "IMPOSTORS", hasEjection: true },
  },
};

// ERROR — the profile fetch failed (a 500, not a 404 — 404 is the empty state).
export const Error: Story = {
  args: {
    status: "error",
    error: "API request to /api/eval/game-profile failed (status 500): internal error",
    cards: [],
    totalCount: 0,
  },
};

// STALE — the profile was computed from other recordings, so its shelves are
// withheld and the page says so.
export const Stale: Story = {
  args: { profile: { ...PROFILE, stale: true } },
};

// REPLAYS BROWSER — a set with no profile: every card stays factual.
export const ReplaysBrowserNoProfile: Story = {
  args: {
    view: "replays",
    profile: null,
    profileMissing: true,
    cards: buildCards(null, LIST),
    totalCount: LIST.length,
    set: "4p1i",
  },
};
