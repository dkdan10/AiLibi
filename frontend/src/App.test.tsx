// The shell header and the guided tour's welcome step, rendered.
//
// Both carry one link to the repository and nothing about who made what: the
// header reads the name, the tagline and a link whose text is "GitHub", and the
// welcome step keeps the same link in a sentence of its own. Each render is held
// to `HEADER_COPY` here; `lib/copy.test.ts` holds the copy tree and the two
// sources to the same words.

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import {
  FinaleCard,
  FinaleHeadline,
  FinaleReason,
  MeetingPauseBar,
  PerspectiveBanner,
  RecapRow,
  RosterRail,
  ShellTitle,
  TopNav,
} from "./App";
import { STEPS } from "./components/GuidedTour";
import { HEADER_COPY, NAV_COPY, OUTCOME_COPY, TOUR_COPY, TRANSPORT_COPY } from "./lib/copy";
import type { Perspective } from "./lib/playback";
import type { FinaleAgentRecapView, GameFinale } from "./types/api";

// The store, reduced to what the navigation, the mode banner, the roster, the
// pause bar and the finale read.
const state = vi.hoisted(() => ({
  view: "replays",
  setView: () => {},
  currentReplay: null as unknown,
  perspective: { mode: "omniscient" } as Perspective,
  setPerspective: () => {},
  setBeliefOpen: () => {},
  selectAgent: () => {},
  selectedAgentId: null as string | null,
  selectedMeetingId: null as string | null,
  selectMeeting: () => {},
  revealOutcome: false,
  setRevealOutcome: () => {},
}));
vi.mock("./store/replayStore", () => ({
  useReplayStore: (selector: (s: typeof state) => unknown) => selector(state),
}));

// The playback hook, reduced to what the roster, the pause bar and the finale read.
const playback = vi.hoisted(() => ({
  hasReplay: true,
  frame: null as unknown,
  meetingAtTick: null as { tick: number } | null,
  isPlaying: false,
  isAtEnd: false,
  finale: null as unknown,
  play: () => {},
  nextKeyMoment: () => {},
  seekToIndex: () => {},
}));
vi.mock("./hooks/usePlayback", () => ({
  usePlayback: () => playback,
  usePlaybackEngine: () => {},
}));

/** The removed attribution line's words, the same five `lib/copy.test.ts` refuses. */
const ATTRIBUTION_WORDS = /\bdirected by|Claude Code|Codex|AI-reviewed|ownership/i;

/** Markup reduced to the text a reader sees. */
function textOf(html: string): string {
  return html
    .replace(/<[^>]*>/g, "")
    .replaceAll("&#x27;", "'")
    .replaceAll("&quot;", '"')
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">")
    .replaceAll("&amp;", "&");
}

/** Every link in the markup: where it points and what it says. */
function linksOf(html: string): readonly { readonly href: string | null; readonly text: string }[] {
  return [...html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/g)].map((match) => ({
    href: /\bhref="([^"]*)"/.exec(match[1] ?? "")?.[1] ?? null,
    text: textOf(match[2] ?? ""),
  }));
}

/** What differs from the header the copy describes; empty when they agree. */
function titleProblems(html: string): readonly string[] {
  const problems: string[] = [];
  const heading = /<h1\b[^>]*>([\s\S]*?)<\/h1>/.exec(html)?.[1];
  if (heading === undefined || textOf(heading) !== "AiLibi") {
    problems.push(`the heading reads ${String(heading)}`);
  }
  const links = linksOf(html);
  if (
    links.length !== 1 ||
    links[0]?.text !== HEADER_COPY.sourceLinkText ||
    links[0]?.href !== HEADER_COPY.sourceUrl
  ) {
    problems.push(`the links are ${JSON.stringify(links)}`);
  }
  const text = textOf(html);
  if (text !== `AiLibi${HEADER_COPY.tagline} · ${HEADER_COPY.sourceLinkText}`) {
    problems.push(`the header reads ${text}`);
  }
  const hit = ATTRIBUTION_WORDS.exec(text);
  if (hit !== null) {
    problems.push(`the header says ${hit[0]}`);
  }
  return problems;
}

/** What differs from the welcome step the copy describes; empty when they agree. */
function welcomeProblems(html: string): readonly string[] {
  const problems: string[] = [];
  const links = linksOf(html);
  if (
    links.length !== 1 ||
    links[0]?.text !== HEADER_COPY.tourSourceLinkText ||
    links[0]?.href !== HEADER_COPY.sourceUrl
  ) {
    problems.push(`the links are ${JSON.stringify(links)}`);
  }
  const hit = ATTRIBUTION_WORDS.exec(textOf(html));
  if (hit !== null) {
    problems.push(`the step says ${hit[0]}`);
  }
  return problems;
}

function welcomeHtml(): string {
  const welcome = STEPS[0];
  if (welcome === undefined) throw new Error("the tour has no welcome step");
  return renderToStaticMarkup(<>{welcome.body}</>);
}

describe("the shell header", () => {
  const html = renderToStaticMarkup(<ShellTitle />);

  it("reads the name, the tagline and one link to the source, from the copy", () => {
    expect(titleProblems(html)).toEqual([]);
    expect(textOf(html)).toBe("AiLibiRecorded AI social deduction · GitHub");
  });

  it("names the attribution, a second link or another tagline when one returns (planted)", () => {
    const attributed = html.replace(
      HEADER_COPY.tagline,
      `${HEADER_COPY.tagline} · directed by Daniel Keinan`,
    );
    expect(attributed).not.toBe(html);
    expect(titleProblems(attributed)).toEqual([
      `the header reads AiLibi${HEADER_COPY.tagline} · directed by Daniel Keinan · GitHub`,
      "the header says directed by",
    ]);
    const twoLinks = html.replace("</p>", ' <a href="https://example.test">More</a></p>');
    expect(twoLinks).not.toBe(html);
    expect(titleProblems(twoLinks)).toHaveLength(2);
    expect(titleProblems(twoLinks)[0]).toMatch(/^the links are /);
    const linkText = html.replace(`>${HEADER_COPY.sourceLinkText}</a>`, ">Source &amp; ownership</a>");
    expect(linkText).not.toBe(html);
    expect(titleProblems(linkText)).toEqual([
      `the links are ${JSON.stringify([{ href: HEADER_COPY.sourceUrl, text: "Source & ownership" }])}`,
      `the header reads AiLibi${HEADER_COPY.tagline} · Source & ownership`,
      "the header says ownership",
    ]);
  });

  it("names the heading when its name changes or another tag carries it (planted)", () => {
    const renamed = html.replace(">AiLibi</h1>", ">AiLibi Studio</h1>");
    expect(renamed).not.toBe(html);
    expect(titleProblems(renamed)).toEqual([
      "the heading reads AiLibi Studio",
      `the header reads AiLibi Studio${HEADER_COPY.tagline} · ${HEADER_COPY.sourceLinkText}`,
    ]);
    const demoted = html.replace(/<h1\b([^>]*)>AiLibi<\/h1>/, "<h2$1>AiLibi</h2>");
    expect(demoted).not.toBe(html);
    expect(titleProblems(demoted)).toEqual(["the heading reads undefined"]);
  });

  it("names the link when only its address changes (planted)", () => {
    const moved = html.replace(`href="${HEADER_COPY.sourceUrl}"`, 'href="https://example.test"');
    expect(moved).not.toBe(html);
    expect(titleProblems(moved)).toEqual([
      `the links are ${JSON.stringify([{ href: "https://example.test", text: HEADER_COPY.sourceLinkText }])}`,
    ]);
  });
});

describe("the guided tour's welcome step", () => {
  const html = welcomeHtml();

  it("keeps one plain link to the source and says nothing about who made what", () => {
    expect(welcomeProblems(html)).toEqual([]);
    const opening = /<p\b[^>]*>([\s\S]*?)<\/p>/.exec(html)?.[1] ?? "";
    expect(textOf(opening)).toBe(
      "AiLibi asks whether AI agents can reason from what they actually saw. You are watching saved games, not making live model calls. Read the source on GitHub.",
    );
  });

  it.each(["directed by", "Claude Code", "Codex", "AI-reviewed", "ownership"])(
    "names %s wherever it returns in the step (planted)",
    (word) => {
      const planted = html.replace(
        "not making live model calls.",
        `not making live model calls. ${word}`,
      );
      expect(planted).not.toBe(html);
      expect(welcomeProblems(planted)).toEqual([`the step says ${word}`]);
    },
  );

  it("names the old sentence or the old link when either returns (planted)", () => {
    const sentence = html.replace(
      "not making live model calls.",
      "not making live model calls. Daniel Keinan directs the project; Claude Code and Codex agents write code and supporting material, with separate AI review.",
    );
    expect(sentence).not.toBe(html);
    expect(welcomeProblems(sentence)).toEqual(["the step says Claude Code"]);
    const link = html.replace(
      `>${HEADER_COPY.tourSourceLinkText}</a>`,
      ">Read the source and ownership case study.</a>",
    );
    expect(link).not.toBe(html);
    expect(welcomeProblems(link)).toEqual([
      `the links are ${JSON.stringify([{ href: HEADER_COPY.sourceUrl, text: "Read the source and ownership case study." }])}`,
      "the step says ownership",
    ]);
  });

  it("names the link when only its address changes (planted)", () => {
    const moved = html.replace(`href="${HEADER_COPY.sourceUrl}"`, 'href="https://example.test"');
    expect(moved).not.toBe(html);
    expect(welcomeProblems(moved)).toEqual([
      `the links are ${JSON.stringify([{ href: "https://example.test", text: HEADER_COPY.tourSourceLinkText }])}`,
    ]);
  });

  it("names a second link beside the source link (planted)", () => {
    const twoLinks = html.replace("</a>", '</a> <a href="https://example.test">More</a>');
    expect(twoLinks).not.toBe(html);
    expect(welcomeProblems(twoLinks)).toEqual([
      `the links are ${JSON.stringify([
        { href: HEADER_COPY.sourceUrl, text: HEADER_COPY.tourSourceLinkText },
        { href: "https://example.test", text: "More" },
      ])}`,
    ]);
  });
});

// ── the navigation, the mode banner and the finale ──────────────────────────
//
// The tabs carry the names of the pages they open, the banner names the game
// and the one player's view in words, and the finale reads one wording per
// ending and states facts in place of right/wrong marks. Each is held to the
// copy here; `lib/copy.test.ts` holds the copy tree and the retired words.

/** The text of every button in the markup, in order. */
function buttonTexts(html: string): readonly string[] {
  return [...html.matchAll(/<button\b[^>]*>([\s\S]*?)<\/button>/g)].map((match) =>
    textOf(match[1] ?? "").trim(),
  );
}

/** What differs from the navigation the copy names; empty when they agree. */
function navProblems(html: string): readonly string[] {
  const expected = [NAV_COPY.replays, NAV_COPY.highlights, NAV_COPY.tournament, "? Tour"];
  const names = buttonTexts(html);
  const problems =
    JSON.stringify(names) === JSON.stringify(expected) ? [] : [`the tabs read ${names.join(", ")}`];
  if (!html.includes(`title="${NAV_COPY.tourTitle}"`)) problems.push("the tour button has no plain tooltip");
  return problems;
}

describe("the navigation", () => {
  const html = renderToStaticMarkup(<TopNav />);

  it("names each tab after the page it opens, from the copy", () => {
    expect(navProblems(html)).toEqual([]);
    expect(buttonTexts(html)).toEqual(["Replays", "Moments", "Results", "? Tour"]);
    expect(textOf(html)).not.toMatch(/Highlights|Results & cases|two-truth/);
  });

  it("names a tab typed back under its old name, and an old tooltip (planted)", () => {
    const old = html.replace(`>${NAV_COPY.highlights}</button>`, ">Highlights</button>");
    expect(old).not.toBe(html);
    expect(navProblems(old)).toEqual(["the tabs read Replays, Highlights, Results, ? Tour"]);
    const tooltip = html.replace(
      `title="${NAV_COPY.tourTitle}"`,
      'title="Guided tour — perspective switcher + the two-truth grammar"',
    );
    expect(tooltip).not.toBe(html);
    expect(navProblems(tooltip)).toEqual(["the tour button has no plain tooltip"]);
  });
});

const NINE = Array.from({ length: 9 }, (_, index) => ({ agent_id: `p-${index}` }));

function banner(over: Partial<typeof state>, meetings = 3): string {
  Object.assign(state, {
    perspective: { mode: "omniscient" },
    revealOutcome: false,
    selectedMeetingId: null,
    currentReplay: {
      metadata: { seed: 19, meeting_count: meetings, winner: "CREWMATES", completion_status: "completed" },
      players: NINE,
    },
    ...over,
  });
  return renderToStaticMarkup(<PerspectiveBanner />);
}

describe("the mode banner", () => {
  it("names the game, its players and one player's view in words", () => {
    const html = banner({ perspective: { mode: "agent", agentId: "p-3" } });
    const text = textOf(html);
    expect(text).toContain("Game 19 · 9 players · outcome hidden");
    expect(html).toContain('title="Recorded from random seed 19"');
    expect(html).toContain('aria-label="Perspective: Watching as p-3"');
    expect(text).toContain("Watching as p-3");
    expect(buttonTexts(html)).toContain("Back to Omniscient");
    expect(text).not.toMatch(/\bfog\b|As p-3|seed 19|9p\b/);
    expect(banner({ perspective: { mode: "agent", agentId: "p-7" } })).toContain(
      'aria-label="Perspective: Watching as p-7"',
    );
  });

  it("names the ending in the tag the cards use once revealed", () => {
    const text = textOf(banner({ revealOutcome: true }));
    expect(text).toContain(`Game 19 · 9 players · ${OUTCOME_COPY.crewWin}`);
    expect(text).not.toContain("CREWMATES");
    // A recording with no winner reads its recorded stop, never a dash.
    const stopped = {
      metadata: { seed: 4, meeting_count: 0, winner: null, completion_status: "tick_limited" },
      players: NINE.slice(0, 4),
    };
    const html = banner({ revealOutcome: true, currentReplay: stopped });
    expect(textOf(html)).toContain(`Game 4 · 4 players · ${OUTCOME_COPY.tickLimited}`);
    expect(html).toContain('title="Recorded from random seed 4"');
  });

  it("names each recorded stop of a game with no winner in the tag the cards use", () => {
    const stops = [
      ["aborted", OUTCOME_COPY.aborted],
      ["tick_limited", OUTCOME_COPY.tickLimited],
      ["unfinished", OUTCOME_COPY.unfinished],
      [null, OUTCOME_COPY.unfinished],
    ] as const;
    for (const [completion_status, tag] of stops) {
      const stopped = {
        metadata: { seed: 4, meeting_count: 0, winner: null, completion_status },
        players: NINE.slice(0, 4),
      };
      expect(textOf(banner({ revealOutcome: true, currentReplay: stopped }))).toContain(
        `Game 4 · 4 players · ${tag}`,
      );
    }
  });

  it("counts the meetings in words beside the Belief × Truth launcher", () => {
    expect(textOf(banner({}))).toContain("Belief × Truth3 meetings");
    expect(textOf(banner({}, 1))).toContain("Belief × Truth1 meeting");
    expect(textOf(banner({}))).not.toContain("mtg");
  });
});

const FINALE: GameFinale = {
  winner: "IMPOSTORS",
  winner_reason: "IMPOSTOR_PARITY",
  final_tick: 44,
  decisive_events: [],
  agent_recaps: [],
};

describe("the finale", () => {
  it("heads the card with the tag the cards use", () => {
    expect(textOf(renderToStaticMarkup(<FinaleHeadline winner="IMPOSTORS" />))).toBe(
      `◆${OUTCOME_COPY.impostorWin}`,
    );
    expect(textOf(renderToStaticMarkup(<FinaleHeadline winner="CREWMATES" />))).toBe(
      `▲${OUTCOME_COPY.crewWin}`,
    );
  });

  it("reads the reason in the cards' ending words, and an unmapped one verbatim", () => {
    const reason = (winner_reason: string) =>
      textOf(renderToStaticMarkup(<FinaleReason finale={{ ...FINALE, winner_reason }} />));
    expect(reason("IMPOSTOR_PARITY")).toBe("the impostors matched the crew in number · final tick 44");
    expect(reason("IMPOSTOR_SABOTAGE")).toBe("a sabotage ran out · final tick 44");
    expect(reason("all_tasks_complete")).toBe("all_tasks_complete · final tick 44");
    expect(reason("constructor")).toBe("constructor · final tick 44");
  });
});

const RECAP: FinaleAgentRecapView = {
  agent_id: "p-2",
  role: "CREWMATE",
  alive_at_end: true,
  final_vote_target: "p-5",
  final_vote_named_impostor: true,
  final_vote_rewritten: false,
};

function recap(over: Partial<FinaleAgentRecapView>): string {
  return renderToStaticMarkup(<RecapRow recap={{ ...RECAP, ...over }} color="#000000" />);
}

describe("the finale's recap", () => {
  it("states what each final ballot named, with no right or wrong mark", () => {
    const named = textOf(recap({ final_vote_named_impostor: true }));
    expect(named).toContain(`voted p-5${OUTCOME_COPY.namedImpostor}`);
    const missed = textOf(recap({ final_vote_named_impostor: false }));
    expect(missed).toContain(`voted p-5${OUTCOME_COPY.namedNoImpostor}`);
    expect(OUTCOME_COPY.namedImpostor).toBe("named an impostor");
    expect(OUTCOME_COPY.namedNoImpostor).toBe("named no impostor");
    for (const text of [named, missed]) expect(text).not.toMatch(/[✓✗]|missed/);
    const none = textOf(recap({ final_vote_target: "SKIP", final_vote_named_impostor: null }));
    expect(none).not.toMatch(/named an impostor|named no impostor/);
  });

  it("says in plain words when the vote rule changed a ballot", () => {
    const html = recap({ final_vote_rewritten: true, final_vote_named_impostor: null });
    expect(textOf(html)).toContain(OUTCOME_COPY.voteRuleChanged);
    expect(OUTCOME_COPY.voteRuleChanged).toBe("changed by the vote rule");
    expect(html).toContain(`title="${OUTCOME_COPY.voteRuleChangedTitle.replaceAll("'", "&#x27;")}"`);
    expect(textOf(html)).not.toContain("engine-adjusted");
    expect(textOf(recap({}))).not.toContain(OUTCOME_COPY.voteRuleChanged);
  });
});

describe("the tour's other steps", () => {
  const text = (index: number) => textOf(renderToStaticMarkup(<>{STEPS[index]?.body}</>));

  it("names the Results tab, and states the endings in the ending words", () => {
    expect(renderToStaticMarkup(<>{STEPS[0]?.body}</>)).toContain(
      `Start at <strong>${NAV_COPY.tournament}</strong> for each set`,
    );
    expect(text(0)).toContain(TOUR_COPY.rules);
    expect(text(0)).not.toMatch(/Results & cases|parity|unresolved sabotage/);
  });

  it("names one player's view as the controls do", () => {
    expect(STEPS[1]?.title).toBe(TOUR_COPY.perspectiveTitle);
    expect(text(1)).toBe(TOUR_COPY.perspectiveBody);
    expect(text(1)).not.toMatch(/As-agent|\bfog\b/);
  });

  it("calls the Belief × Truth view a panel", () => {
    expect(text(2)).toContain("Open the Belief × Truth panel");
    expect(text(2)).not.toContain(" hero ");
  });
});

// ── the roster, the pause bar and the finale card ──────────────────────────

const ROSTER = {
  metadata: { seed: 19, meeting_count: 3, winner: "CREWMATES", completion_status: "completed" },
  players: NINE.map((player, index) => ({
    ...player,
    color: "#000000",
    role: index < 2 ? "IMPOSTOR" : "CREWMATE",
  })),
};

describe("the roster's counts", () => {
  it("spells out the impostors in both layouts", () => {
    Object.assign(state, { currentReplay: ROSTER, perspective: { mode: "omniscient" } });
    playback.frame = {
      agent_states: [],
      advantage: { crew_alive: 7, impostors_alive: 2, tasks_completed: 3, tasks_required_total: 10 },
      meeting_resolution: null,
    };
    const text = textOf(renderToStaticMarkup(<RosterRail />));
    // The collapsed bar, then the full rail.
    expect(text).toContain("crew 7 · impostors 2 · tasks 3/10");
    expect(text).toContain("crew 7impostors 2");
    expect(text).not.toMatch(/\bimp \d/);
    playback.frame = {
      agent_states: [],
      advantage: { crew_alive: 5, impostors_alive: 1, tasks_completed: 3, tasks_required_total: 10 },
      meeting_resolution: null,
    };
    const later = textOf(renderToStaticMarkup(<RosterRail />));
    expect(later).toContain("crew 5 · impostors 1 · tasks 3/10");
    expect(later).toContain("crew 5impostors 1");
  });
});

describe("the meeting pause bar", () => {
  it("offers the next key moment, and resumes past the meeting in plain words", () => {
    Object.assign(playback, { meetingAtTick: { tick: 12 }, isPlaying: false, isAtEnd: false });
    const html = renderToStaticMarkup(<MeetingPauseBar />);
    expect(buttonTexts(html)).toEqual(["▶ Resume", `${TRANSPORT_COPY.nextKeyMoment} →`]);
    expect(html).toContain(`title="${TRANSPORT_COPY.resumeTitle}"`);
    expect(html).not.toMatch(/Next beat|edge-triggered/);
  });
});

describe("the finale card", () => {
  function card(finale: GameFinale): string {
    Object.assign(state, { currentReplay: ROSTER, selectedMeetingId: null, revealOutcome: true });
    playback.finale = finale;
    return textOf(renderToStaticMarkup(<FinaleCard />));
  }

  it("reads the recorded winner and reason in the cards' words", () => {
    const text = card({ ...FINALE, agent_recaps: [RECAP] });
    expect(text).toContain(`◆${OUTCOME_COPY.impostorWin}`);
    expect(text).toContain("the impostors matched the crew in number · final tick 44");
    expect(text).toContain(`voted p-5${OUTCOME_COPY.namedImpostor}`);
    const crew = card({ ...FINALE, winner: "CREWMATES", winner_reason: "CREWMATE_TASKS" });
    expect(crew).toContain(`▲${OUTCOME_COPY.crewWin}`);
    expect(crew).toContain("the crew finished its tasks · final tick 44");
  });
});
