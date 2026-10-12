// The spectator surface's user-facing copy, plus the pure helpers that keep it
// honest.
//
// These things live here, and they live here together on purpose:
//
//   • `dialectHits` — the matcher for internal dialect (design-doc citations,
//     bare section numbers, task ids, audit paths, and the project words that
//     mean nothing to a visitor: "sentinel", "KPI", "canary", "substrate").
//     It is the gate `copy.test.ts` runs over every value below AND over the
//     component sources with comments stripped.
//   • `SPECTATOR_COPY` — the prose itself. A copy string in a `.tsx` is only
//     checkable through a renderer; a value here is readable by the node-env
//     test project directly, so "no dialect reaches a viewer" is a unit test
//     rather than a review habit.
//   • `fmt` — the one interpolation helper, so a hint that carries a count
//     still keeps its WORDS here as a template rather than in the component.
//   • `expandSetName` / `setOptionLabel` — set ids ("9p2i") expanded into words
//     once per surface, with the raw id as the fallback for ids `/sets` grows
//     later.
//   • the workspace's name helpers — a game's number, its counts, its ending
//     tag, a lone body's killer and the sabotage readout — each a fill of one
//     template below, so a surface that renders them (the map's canvas among
//     them, which no DOM test reads) keeps its words here.
//   • `PROFILE_COPY` — the game-shape profile's shelf, chip, facet and
//     tripwire words, keyed by the names the served profile carries.
//
// Also here: `showsBallotCorrectness`, the ballot correctness-badge gate. It is
// a display gate over copy (the ✓/✗ mark), stated as a pure predicate so the
// four perspective × reveal combinations are assertable with no DOM. And
// `bucketWord`, which turns a suspicion or confidence value into the Low / Med
// / High word a face shows, the number going on hover.
//
// AGENTS.md craft rule 4 ("no internal dialect on user-facing surfaces").

import { suspicionBucketOf } from "../tokens";
import type { ReplayMetadataView, SabotageDetailView, Winner } from "../types/api";

// ── the dialect matcher ──────────────────────────────────────────────────────

/** One class of internal dialect, named so a failure says WHAT it found. */
interface DialectPattern {
  readonly name: string;
  readonly pattern: RegExp;
}

// Unanchored and case-insensitive where the word can be typed either way; none
// carries the `g` flag, because a stateful `lastIndex` would make `test` return
// different answers on successive calls with the same input.
const DIALECT_PATTERNS: readonly DialectPattern[] = Object.freeze([
  { name: "design-doc citation", pattern: /DESIGN\.md/i },
  { name: "section reference", pattern: /§\s*\d/ },
  { name: "task reference", pattern: /\btask\s+\d+\.\d+/i },
  { name: "audit path", pattern: /\baudits\//i },
  { name: "undefined jargon", pattern: /\b(?:sentinel|kpi|canary|substrate)\b/i },
]);

/**
 * The names of every dialect class present in `text` (empty when it is clean).
 *
 * Names rather than booleans so a failing assertion reports the class it
 * caught, not just that something matched.
 */
export function dialectHits(text: string): readonly string[] {
  return DIALECT_PATTERNS.filter((d) => d.pattern.test(text)).map((d) => d.name);
}

// ── interpolation ────────────────────────────────────────────────────────────

const PLACEHOLDER = /\{(\w+)\}/g;

/** The `{name}` placeholders in a copy template, as a union of their names. */
export type Placeholders<S extends string> =
  S extends `${string}{${infer Name}}${infer Rest}` ? Name | Placeholders<Rest> : never;

/**
 * Fill `{name}` placeholders in a copy template.
 *
 * The point is where the WORDS live: a hint built with a template literal in a
 * component is invisible to the copy walk, while `fmt(COPY.x, {…})` keeps the
 * sentence here and passes only the formatted numbers in.
 *
 * The signature is what makes that safe. `SPECTATOR_COPY` is `as const`, so a
 * template's placeholder names are part of its TYPE: passing the wrong key is a
 * compile error, not a hint that renders `{typo}` — or, with the runtime guard
 * below, a blank panel — at a viewer. The throw is the backstop for a template
 * that reaches here already widened to `string`.
 */
export function fmt<S extends string>(
  template: S,
  values: Readonly<Record<Placeholders<S>, string>>,
): string {
  const lookup = values as Readonly<Record<string, string | undefined>>;
  return template.replace(PLACEHOLDER, (_match, name: string) => {
    const value = lookup[name];
    if (value === undefined) {
      throw new Error(`copy template has no value for {${name}}: ${template}`);
    }
    return value;
  });
}

// ── set ids → words ──────────────────────────────────────────────────────────

// The served sets a visitor can currently pick. `/sets` grows as new sets are
// recorded, so an unknown id is a NORMAL case, not an error: it falls back to
// the raw id rather than inventing an expansion.
//
// A `Map`, not an object literal: the backend's set-name pattern admits ids like
// `constructor` and `toString`, and a plain object would answer those from
// `Object.prototype` — the lookup would "succeed" and the selector would render
// a function body instead of the id. A Map has no inherited keys, so every
// unrecognised id takes the documented fallback.
const SET_NAMES: ReadonlyMap<string, string> = new Map([
  ["9p2i", "9 players, 2 impostors"],
  ["4p1i", "4 players, 1 impostor"],
]);

/** A set id in words, or the id itself when it is not one we can expand. */
export function expandSetName(setId: string): string {
  return SET_NAMES.get(setId) ?? setId;
}

/**
 * A set's name as it reads in a control or a sentence.
 *
 * The words first, then the raw id in parentheses — the id is what the `set`
 * URL key and the manifests use — so a known set reads
 * "9 players, 2 impostors (9p2i)" and an unknown one reads as its bare id
 * rather than as the id twice.
 */
export function setOptionLabel(setId: string): string {
  const expanded = expandSetName(setId);
  return expanded === setId ? setId : `${expanded} (${setId})`;
}

// ── the ballot correctness badge ─────────────────────────────────────────────

/**
 * Whether a ballot may show its ✓ correct / ✗ incorrect mark.
 *
 * The mark reads the target's role, so it needs the omniscient perspective —
 * and it is also OUTCOME information: applied per ballot it names the impostors
 * before the game does, which is precisely what a viewer who left outcomes
 * hidden asked not to be told. So it needs both.
 *
 * Superseded: the mark used to be gated on perspective alone, on the reasoning
 * that reveal governs outcome and perspective governs what the frame may know.
 */
export function showsBallotCorrectness(
  omniscient: boolean,
  revealOutcome: boolean,
): boolean {
  return omniscient && revealOutcome;
}

// ── suspicion and confidence in words ────────────────────────────────────────

/**
 * A 0–1 suspicion or confidence value as the word a face shows: Low, Med or
 * High, cut where the heat ramp cuts (`suspicionBucketOf`), with no cut point of
 * its own. The number itself belongs on hover, never on the face.
 */
export function bucketWord(value: number): string {
  return SPECTATOR_COPY.buckets[suspicionBucketOf(value)];
}

// ── the copy itself ──────────────────────────────────────────────────────────

/**
 * Every string this module owns, in one frozen tree.
 *
 * One tree rather than a scatter of exported consts so the test can walk it:
 * anything added inside is checked for dialect automatically, with no list to
 * keep in sync. Templates keep their `{placeholders}` and are filled by `fmt`,
 * so a counted hint is checked here too.
 *
 * `as const` is load-bearing, not decoration: it keeps each template's literal
 * type, which is what lets `fmt` reject a wrong placeholder name at compile
 * time.
 */
export const SPECTATOR_COPY = Object.freeze({
  /**
   * The page's tab title, which is also its link preview: `frontend/index.html`
   * types it into its `<title>`, its description and its `og:title`, and the
   * copy test holds the three to this value.
   */
  site: Object.freeze({
    title: "AiLibi — Recorded AI social deduction",
  }),
  /** The shell's tabs, named after the pages they open, and the tour button. */
  nav: Object.freeze({
    replays: "Replays",
    highlights: "Moments",
    tournament: "Results",
    tourTitle: "A short tour of how to watch a recorded game",
  }),
  /** The guided tour's words this copy owns. */
  tour: Object.freeze({
    // The game's rules in the cards' ending words.
    rules:
      "Players move one room edge per tick. The crew wins by finishing its tasks or voting out every impostor; impostors kill, deceive, and sabotage, and win when they match the crew in number or a sabotage runs out. Body reports and emergency calls begin discussion and voting. Movement is rule-based; models deliberate at meetings.",
    perspectiveTitle: "What one player could see",
    perspectiveBody:
      "The map toolbar, at the top right of the stage, switches between Omniscient and “See as” one player. Seen as one player, the map dims to only what that player could see: role badges and the impostor reveal disappear, because that player never knew them. Identity colour is identity only; it never encodes guilt.",
  }),
  /**
   * A game's name and counts. A game is named by its number, which is the
   * random seed it was recorded from, so the tooltip says so.
   */
  game: Object.freeze({
    name: "Game {n}",
    seedTitle: "Recorded from random seed {seed}",
    open: "Open game {n}",
    playersOne: "{count} player",
    playersMany: "{count} players",
    meetingsOne: "{count} meeting",
    meetingsMany: "{count} meetings",
    rosterCrew: "crew {count}",
    rosterImpostors: "impostors {count}",
  }),
  /**
   * How a game ended, one wording wherever it shows (the card tag, the
   * workspace banner and the finale), and what each final ballot named.
   */
  outcome: Object.freeze({
    crewWin: "Crew win",
    impostorWin: "Impostor win",
    aborted: "Aborted",
    // A short form of the cards' "the run stopped at its tick limit".
    tickLimited: "Stopped at the tick limit",
    unfinished: "Unfinished",
    // Facts about the target's recorded role, never a right or wrong mark.
    namedImpostor: "named an impostor",
    namedNoImpostor: "named no impostor",
    voteRuleChanged: "changed by the vote rule",
    voteRuleChangedTitle:
      "The vote rule changed this ballot's target, so the counted vote is not the one the voter chose, and nothing is said about what it named.",
  }),
  /**
   * One player's view, named one way everywhere: the banner says whose view is
   * on screen ("Watching as p-3"), and every control that opens one says
   * "See as p-1". "Omniscient" stays the all-roles view's name.
   */
  perspective: Object.freeze({
    bannerLabel: "Perspective: {view}",
    watchingAs: "Watching as {agent}",
    seeAs: "See as {agent}",
    // Only when the recording has no player to see as.
    seeAsNobody: "See as one player",
    backToOmniscient: "Back to Omniscient",
    backTitle:
      "Return to the Omniscient view, which shows every role. Choose a player in the map toolbar to see as them.",
    pickerLabel: "See as",
    pickerTitle: "Choose which player's view to see",
    tickerChip: "watching as {agent}",
    tickerTitle:
      "Only what this player could see: an unwitnessed kill shows as a body discovery, and unwitnessed vents not at all",
    roleHiddenTitle: "This player's role is hidden in another player's view.",
    privateMind:
      "This player’s memory and reasoning are private. Use “See as {agent}” or switch to Omniscient to inspect them. Public statements remain in the meeting transcript.",
    privateBallot: "Private ballot reasoning. See as {voter} to inspect it.",
    hiddenMemory:
      "Raw rendered memory is hidden in another player's view: it holds this player's role and private memory. Switch to Omniscient, or use “See as {agent}”, to read it.",
    daggerTitle: "A dagger badge marks a real impostor. It shows only in the Omniscient view.",
  }),
  /**
   * The shell header and its one link to the source; the guided tour's welcome
   * step links to the same repository in a sentence of its own.
   */
  header: Object.freeze({
    tagline: "Recorded AI social deduction",
    sourceLinkText: "GitHub",
    tourSourceLinkText: "Read the source on GitHub.",
    sourceUrl: "https://github.com/dkdan10/AiLibi",
  }),
  /** The Tournament tab. Every prose string on that surface is here. */
  dashboard: Object.freeze({
    ariaLabel: "Tournament dashboard",
    intro:
      "The latest tournament eval report: balance outcome, vote correctness, the conversion and gate surface, the proof-vs-inference deduction instrument, and the moments of the game-shape profile.",
    refresh: "Refresh",
    refreshBusy: "Loading…",
    loadingReport: "Loading tournament report…",
    detailedReport: "Full diagnostic report (larger download)",
    noReportTitle: "No tournament report.",
    noReportLead: "A 404 means no",
    noReportMiddle: "exists in the configured eval directory yet — run a tournament with",
    noReportTail: "to produce one.",
    noReportBundle:
      "This bundle omits the full diagnostic report. Compact verified results are available separately.",

    balanceTitle: "Balance outcome",
    balanceDescription:
      "Verified outcomes and recorded stop reasons across the tournament.",
    balanceGames: "Games recorded",
    balanceSeedsAttempted: "{n} seeds attempted",
    balanceSeeds: "{n} seeds",
    balanceCrewWins: "Verified crew wins",
    balanceImpostorWins: "Verified impostor wins",
    balanceTickBudget: "Tick limit reached",
    balanceTickBudgetHint: "explicit normal stop",
    balanceCrewWinRate: "Crew win rate",
    balanceCrewWinRateHint: "of {n} verified outcomes",
    balanceAborted: "Aborted",
    balanceUnfinished: "Unfinished",
    balanceUnverified: "Unverified outcomes",
    balanceUnverifiedHint: "excluded from verified win rates",

    voteCorrectnessTitle: "Vote correctness",
    voteCorrectnessDescription:
      "The share of impostor ejections that carry hard evidence on the record — a contradiction naming the ejected player, or a kill-witness chain. It is a bug check rather than a quality score: crewmate ejections sit outside its denominator, so it never says how well the table voted. 'n/a' when no impostors were ejected.",
    voteCorrectnessRate: "Evidence-backed share",
    voteCorrectnessRateHint: "{backed} / {total} evidence-backed",
    voteCorrectnessRateCaveat: "bug check, not a score",
    voteCorrectnessRateCaveatTitle:
      "Below 100% means an impostor was ejected with none of that evidence recorded against them — a game worth opening to find out why. For how often the table ejected the right player, read ejection accuracy in the Conversion section.",
    voteCorrectnessSmallN: "small-n",
    voteCorrectnessSmallNTitle:
      "Under-powered: fewer than 10 impostor ejections, too few to trust this rate as a gate.",
    voteCorrectnessTotalEjections: "Total ejections",
    voteCorrectnessImpostorEjections: "Impostor ejections",
    voteCorrectnessCrewmateEjections: "Crewmate ejections",
    voteCorrectnessIgnored: "Contradictions ignored",
    voteCorrectnessIgnoredCaveat: "skipped w/ a flag",
    voteCorrectnessIgnoredCaveatTitle:
      "Meetings that carried at least one structured contradiction yet ejected no one — the deduction signal was there and went unused.",

    conversionTitle: "Conversion",
    conversionDescription:
      "Did accusations convert into impostor ejections, and were the skipped votes the right call?",
    conversionAccuracy: "Ejection accuracy",
    conversionAccuracyHint: "{hit} / {total} ejections hit an impostor",
    conversionAccused: "Accused → eject",
    conversionAccusedHint: "{converted} / {meetings} accused-impostor meetings",
    conversionCorrectSkips: "Correct skips",
    conversionCorrectSkipsHint:
      "skips where nobody still ejectable had reached the suspicion line",
    conversionMissedSkips: "Missed skips",
    conversionMissedSkipsHint:
      "impostor voters {impostorVoters} · invalid targets {invalidTargets} · crew declined {crewDeclined}",
    conversionMissedSkipsCaveat: "read the split, not the total",
    conversionMissedSkipsCaveatTitle:
      "Read the split, not the total: most missed skips are impostors voting their own side, or targets the parser had to normalize away. What is left is a crew voter who was shown someone who had reached the suspicion line and skipped anyway — see its own tile.",
    conversionInversions: "Threshold inversions",
    conversionInversionsHint: "crew voters who skipped at or over the line",
    conversionInversionsCaveat: "discretionary — nonzero intended",
    conversionInversionsCaveatTitle:
      "A crew voter who was shown a still-ejectable player whose suspicion had reached the line — most of them sit exactly on it — and who skipped anyway. The vote gate is advice, not an order, so declining is allowed play: a nonzero count is expected on recorded sets, not a bug.",
    conversionInversionsNone: "no declines recorded",

    gateTitle: "Gate metrics",
    gateDescription:
      "Whether hard evidence the engine hands the crew turns into an ejection. The live signal is the first tile: of the impostors the engine gave the crew a checkable tell about — a witnessed vent, a sighting the map contradicts, a whereabouts lie — how many the table actually voted out. The second tile is the older version of the same question, anchored on alibi lies; this build barely produces those, so it is kept as history and is not read as a signal.",
    gateSupplied: "Supplied-channel conversion",
    gateSuppliedHint:
      "{converted} / {supplied} impostors with a checkable tell were ejected · vent {ventConverted}/{ventSupplied} · sighting {sightingConverted}/{sightingSupplied} · whereabouts {whereaboutsConverted}/{whereaboutsSupplied}",
    gateSuppliedCaveat: "the live signal",
    gateSuppliedCaveatTitle:
      "Counts the three checkable tells the engine records against a true impostor — a witnessed vent, a sighting the map contradicts, a lie about where they were — and asks whether that impostor was then ejected.",
    gateGenuine: "Genuine-class conversion (historical)",
    gateGenuineHint: "{converted} / {supplied} alibi-anchored flags",
    gateGenuineCaveat: "historical — a handful of cases",
    gateGenuineCaveatTitle:
      "The older alibi-anchored form of the tile beside it. Checkable alibi lies became rare, so this rate rests on a handful of cases and moves by a large step when one of them changes. Reported for continuity; the tile beside it is the one to read.",
    gateLostOpenings: "Lost opening accusations",
    gateLostOpeningsHint: "chain died on turn 0",
    gateCapDefaults: "Cap-defaulted turns",
    gateCapDefaultsHint: "deadline/token-cap truncations",
    gateSurvivals: "Accused-impostor survivals",
    gateSurvivalsHint: "met {met} · sheltered {sheltered} · unevidenced {unevidenced}",
    gateSurvivalsCaveat: "met ≠ deception",
    gateSurvivalsCaveatTitle:
      "This split separates impostors who talked their way out from impostors the table simply failed to eject. A 'met' survival is the second kind — a voter was shown evidence past the bar and the table still did not eject — so only the 'sheltered' count is deception the impostor earned.",

    deductionTitle: "Proof vs inference",
    deductionDescription:
      "How this set's ejection accuracy splits by whether the engine's own vent proof was PRESENT. The same bytes are cut TWO different ways below — by whether the MEETING carried role proof, and by whether the proof named the EJECTED player. Both are correct; their denominators are different and are never mixed. Presence is co-occurrence, not causation: the split says what evidence was on the record, never that a vote followed it.",
    deductionPartitionA: "Partition A · did the meeting carry proof",
    deductionPartitionAUnit: "the unit is the MEETING ({meetings} meetings)",
    deductionPartitionB: "Partition B · did the proof name the ejected player",
    deductionPartitionBUnit: "the unit is the EJECTION ({ejections} ejections)",
    deductionSupporting: "Supporting instrument",
    deductionSupportingUnit: "each cell carries its own denominator",
    deductionFlagged: "Flagged-meeting accuracy",
    deductionFlaggedHint:
      "{impostor} / {total} ejections in the {meetings} meetings that carried role proof",
    deductionUnflagged: "Unflagged-meeting accuracy",
    deductionUnflaggedHint:
      "{impostor} / {total} ejections in the {meetings} meetings with no role proof at all",
    deductionInnocents: "Innocents ejected",
    deductionInnocentsHint: "flagged / unflagged meetings",
    deductionDirect: "Direct-proof accuracy",
    deductionDirectHint:
      "{impostor} / {total} ejections where a vent sighting named the ejected player",
    deductionNonDirect: "Non-direct accuracy",
    deductionNonDirectHint:
      "{impostor} / {total} ejections with NO proof naming the ejected player",
    deductionProofShare: "Proof-present share",
    deductionProofShareHint:
      "{present} / {total} ejections had proof naming the ejected player on the record",
    deductionInterval: "95% CI {low}–{high}",
    deductionIntervalMissing: "no data",
    deductionRareCaveat: "rare — read the interval",
    deductionRareCaveatTitle:
      "Rare cell: the numerator is {numerator}. The point rate is statistically fragile at this scale — read the interval ({interval}), not the percentage.",
    deductionNonCausationCaveat: "proof-present ≠ proof-driven",
    deductionNonCausationCaveatTitle:
      "Co-occurrence inside one meeting, not causation: the cell says no role-proof flag NAMED the ejected player, not that the vote ignored evidence. {interval}.",
    deductionWeakFlag: "Weak-flag-only convictions",
    deductionWeakFlagHint: "{innocent} of them ejected an innocent",
    deductionConsistency: "Turn → ballot consistency",
    deductionConsistencyHint: "{consistent} / {accusing} accusing voters voted their accusation",
    deductionConsistencyCaveat: "follow-through, not correctness",
    deductionConsistencyCaveatTitle:
      "Follow-through, not virtue: an honest mid-meeting revision scores as an inconsistency, and a skip counts against the voter only when someone they accused was votable.",
    deductionCoverage: "Roll-call coverage",
    deductionCoverageHint:
      "crew {crewWith}/{crewTotal} vs impostor {impostorWith}/{impostorTotal} turns (pooled)",
    deductionCoverageCaveat: "pooled — macro differs",
    deductionCoverageCaveatTitle:
      "A behavioural tell that follows from what each role is asked to say — NOT a leak of hidden state. How you average matters: the per-meeting average reads {macro} for impostors against the pooled {pooled}.",
    deductionRedirected: "Engine-redirected ballots",
    deductionRedirectedHint: "{redirected} / {total} ballots · {ejected} still ejected",
    deductionSupply: "Kill-scene evidence supply",
    deductionSupplyHint: "crew-witnessed kills · {coPresent} with a crewmate co-present",
    deductionSupplyMissing: "not supplied with this report",
    deductionSupplyMissingCaveat: "not supplied",
    deductionSupplyMissingCaveatTitle:
      "The kill-craft fold needs a verified walk over the committed replay directory, so a live tournament report carries no supply cells. Rebuild the sample report to populate them.",

    calibrationTitle: "Accusation calibration",
    calibrationDescription:
      "Per-confidence-bin actual-impostor rate. A well-calibrated population tracks the dashed y=x diagonal. Mid-meeting accusation claims and final vote ballots are shown separately (they are different acts).",
    calibrationClaims: "Accusation claims",
    calibrationBallots: "Vote ballots",
    calibrationError: "Expected calibration error {value}",
    calibrationErrorTitle: "lower is better",
    calibrationLowPower:
      "Too few to trust the calibration — read the expected calibration error with care.",

    alibiTitle: "Alibi fabrication",
    alibiDescription:
      "Share of impostor-authored alibis that survived the contradiction detector (a conservative lower bound). High = impostors getting away with fabricated cover; low = the detector catching it. 'n/a' when no impostor alibis were filed.",
    alibiSurvivalRate: "Survival rate",
    alibiSurvivalRateHint: "{survived} / {total} survived",
    alibiTotal: "Impostor alibis",
    alibiSurvived: "Survived",

    momentsTitle: "Moments in this set",
    momentsDescription:
      "How many games sit on each shelf of the game-shape profile, and how its facets spread across the set. No game is ranked or scored, and nothing is averaged.",
    momentsLoading: "Loading the game-shape profile…",
    momentsAbsentTitle: "No game-shape profile.",
    momentsAbsentBody:
      "The selected set ships no game-shape profile, so there are no shelves to count.",
    momentsStaleCaveat: "profile out of date",
    momentsStaleCaveatTitle:
      "The profile was computed from recordings that no longer match the served ones, so its counts are hidden.",
    momentsError: "Couldn't load the game-shape profile:",
    momentsBeforeReveal: "Shelves before the reveal",
    momentsAfterReveal: "Shelves after the reveal",
    momentsRevealHint:
      "The shelves that read an ending, an ejection or a role stay hidden until you reveal outcomes.",
    momentsShelfColumn: "shelf",
    momentsGamesColumn: "games",
    momentsValueColumn: "value",
    momentsFacetMeetings: "Meetings per game",
    momentsFacetKills: "Kills per game",
    momentsFacetUnfound: "Bodies never found per game",

    costTitle: "Cost dashboard",
    costDescription:
      "Tournament LLM spend roll-up. Per-(template, version) totals OVERLAP — the full game cost is attributed once per template a game ran — so they do not sum to the tournament total.",
    costTotal: "Total cost",
    costMean: "Mean / game",
    costGames: "Games",
    costTokens: "Tokens (in / out)",
    costPerModel: "Per model",
    costPerModelEmpty: "No model spend recorded.",
    costPerPrompt: "Per prompt (template · version)",
    costPerPromptEmpty: "No prompt-version breakdown.",
    costColModel: "Model",
    costColCost: "Cost",
    costColTemplate: "Template",
    costColVersion: "Version",
    costColGames: "Games",
  }),

  /**
   * The meeting dialog: the accusation chain, the evidence list, the
   * Resolution card and its omniscient-only record.
   */
  meeting: Object.freeze({
    resolutionGateBadge: "vote gate",
    resolutionGateLead: "How the vote resolved",
    // Why the vote came out as it did, in words. No number, threshold or
    // comparison sign: a player's view may not learn another voter's
    // confidence, and the all-roles view needs no figure to say whether a
    // voter was sure enough. One sentence per way a vote can end.
    readoutEjected:
      "Most votes went to {leader} and a voter was sure enough, so {leader} was ejected.",
    readoutNotSure:
      "Most votes went to {leader}, but none of those voters was sure enough, so no one was ejected.",
    readoutNoLeader:
      "No single player got the most votes (a tie, or skip led), so no one was ejected.",
    // The ejected player's real role, shown in the all-roles view only.
    roleImpostor: "{player} was an impostor",
    roleCrewmate: "{player} was a crewmate",
    chainCaption: "Arrows point from accuser to accused",
    chainVerb: "accuses",
    // The three kinds of evidence a meeting can carry, each with what it holds.
    evidenceGroups: Object.freeze({
      role_proof: Object.freeze({
        heading: "Role proof",
        caption:
          "A vent sighting that matches what the witness really saw: one source, not two statements at odds.",
        label: "proof",
      }),
      cross_statement: Object.freeze({
        heading: "Contradictions",
        caption: "These two statements cannot both be true; nothing here says which one is false.",
        label: "contradiction",
      }),
      weak_signal: Object.freeze({
        heading: "Weak signals",
        caption:
          "Clashes marked weak when found, such as an alibi a player gave for themselves, a very short time window, or a clash only at the first or last tick of a stated stretch.",
        label: "weak signal",
      }),
    }),
    evidenceSource: "Source {index} · {endpoint}",
    evidenceSourceMissing: "not found in this meeting",
    // Three facts the omniscient view adds to a meeting (`lib/annotations.ts`).
    // None renders under a player's lens: the kill tick is withheld from every
    // player at the table, and the rooms are the engine's record of where each
    // accused player stood, not anyone's account of it.
    engineRecordHeading: "Where everyone really was",
    engineRecordLead: "Shown in the omniscient view only, and read from the recording itself.",
    corpseAgeOneTick:
      "The reported body is {victim}'s, killed at tick {killTick}, one tick before this meeting.",
    corpseAgeTicks:
      "The reported body is {victim}'s, killed at tick {killTick}, {age} ticks before this meeting.",
    openerAnswered: "{opener} opened this meeting, was accused by {accuser}, and spoke again afterwards.",
    openerUnanswered:
      "{opener} opened this meeting and was accused by {accuser}, but did not speak again.",
    // The map's clock, not a player's: an account stamped tick N describes the
    // map at N−1, so the lead says so rather than letting a one-tick offset read
    // as a lie.
    routesLead:
      "Where each accused player really was, from tick {from} to this meeting. These are the map's ticks; a player's own account of the same moment is stamped one tick later.",
    routeInVent: "inside a vent in {room}",
    routeSpanOneTick: "tick {tick}",
    routeSpanTicks: "ticks {from}–{to}",
  }),

  /** The map stage. */
  map: Object.freeze({
    // Shown on a recording that regroups after each meeting the game outlives,
    // in both lenses: it is a rule of the game, which the players are told too.
    // A meeting that ends the game is followed by no frame and no regroup, so
    // the note speaks only of the meetings play resumes from.
    regroupNote:
      "On this recording, whenever play resumes after a meeting, the survivors start from the meeting room with the bodies cleared, so the map jumps to where they stand on the next tick.",
    chip: "Map",
    // A room one player's view does not see.
    unseenRoom: "Unseen",
    // Under a lone body, in the all-roles view only.
    killedBy: "killed by {killer}",
    // The sabotage readout. The all-roles view counts it down; one player's
    // view names neither the room nor the countdown, which it hides.
    reactorCountdownOne: "Reactor meltdown in {ticks} tick",
    reactorCountdownMany: "Reactor meltdown in {ticks} ticks",
    lightsCountdownOne: "Lights out, {ticks} tick left",
    lightsCountdownMany: "Lights out, {ticks} ticks left",
    reactorAlarm: "Sabotage alarm",
    lightsOut: "Lights out",
  }),

  /** One ballot card's private-reasoning block. */
  ballot: Object.freeze({
    // The recorded weighing artefact: who this voter wrote down while choosing.
    // The heading deliberately claims NOTHING about who those are — an earlier
    // "Also weighed" said the OTHER players, and the bytes falsify that. Over
    // `replays/samples/9p2i`, 27 of 702 ballots list the voter ITSELF (measured
    // by `scripts/measure_featured_criterion.py --alternatives`); none lists the
    // target the vote applied to, which the ballot schema still admits, and the
    // recordings also admit an id no longer in the game and the literal `SKIP`.
    // Those entries are annotated by the two notes below rather than dropped,
    // so the block stays the record.
    alternativesLabel: "Weighed on this ballot",
    alternativesEmpty: "no alternatives recorded",
    // An entry the card's header already shows, named so a viewer reads one
    // player twice rather than two players.
    alternativesSelfNote: "this voter",
    alternativesTargetNote: "the vote cast",
    // What the meeting FOUND under this ballot, in plain language. It is a
    // description, never a correction: the vote it sits beside is the one the
    // voter cast, because the label was never allowed to move a target or to
    // count in the tally. Wording therefore avoids "rejected", "invalid vote"
    // and every other word that would read as the meeting overruling the
    // voter — `invalidCitation` is about the CITATION, not the vote.
    // Recordings made before the label exists carry none of these and the chip
    // does not render.
    // The weighing channel's second citation (ruling D5 of 2026-09-19): what
    // the voter itself named as pointing AWAY from the vote it cast. Worded as
    // the voter's own act, not as a correction — naming it cost the ballot
    // nothing, the target beside it is the one the voter chose, and no layer
    // weighed it against them.
    counterLabel: "Weighed against it",
    // Shown on the chip itself, before what the meeting found.
    groundingLabel: "Basis on the record:",
    groundingLabels: Object.freeze({
      // Both subjects in one line: an ejection's is the player it names, a
      // skip's is the alternatives it weighed (or any living candidate when it
      // weighed none).
      supported: "Cited evidence about the accused, or about who was weighed",
      off_target: "Cited evidence about someone else",
      invalid_citation: "Citation did not match anything on record",
      none_held: "Voter said it held nothing",
      flag_only: "Rests on a contradiction raised at this meeting",
      uncited: "No basis given",
      not_assessed: "Not assessed — the meeting set this vote",
    }),
    // What the meeting changed about a recorded ballot, keyed by the reason the
    // recording gives. Each names what changed, never the voter's intent; a
    // reason this build has not been taught reads as the fallback.
    rewriteLabels: Object.freeze({
      invalid_target: "Vote for someone who could not be voted out changed to skip",
      teammate_coerced: "Vote for a teammate changed to skip",
      under_gate_redirect: "Vote changed by the vote rule",
      invalid_reason_id: "The statement it cited was not found, so the citation was removed",
      invalid_observation_id: "The observation it cited was not found, so the citation was removed",
      uncited_coerced: "Vote with no cited reason changed to skip",
      off_target_coerced: "Vote citing evidence about someone else changed to skip",
      invalid_basis: "Unreadable stated reason removed",
      invalid_counter_reason_id: "The evidence it weighed against its vote was not found, so it was removed",
      parse_default: "Unreadable ballot counted as a skip",
    }),
    rewriteFallback: "The meeting changed this ballot",
    redirectNote:
      "The recorded explanation describes the original choice, before the vote rule changed the vote.",
  }),

  /**
   * Where a citation points, in words: a statement by its speaker and turn, an
   * observation by who saw it and when. An id that names nothing in the meeting,
   * or that cannot be read, says so.
   */
  evidenceSource: Object.freeze({
    statement: "Statement by {speaker} (turn {turn})",
    statementMissing: "Statement (turn {turn}), not found in this meeting",
    statementUnreadable: "A statement this recording cannot read",
    observation: "What {observer} saw at tick {tick}",
    observationUnreadable: "An observation this recording cannot read",
    part: "Part of the statement by {speaker} (turn {turn})",
    partMissing: "Part of a statement (turn {turn}), not found in this meeting",
    partUnreadable: "A source this recording cannot read",
    // Shown only once the citation has found its source.
    resolvedNote: "A citation shows where a claim came from, not that it is right.",
    publicLine: "{speaker} · public · {kind} · meeting tick {tick}",
  }),

  /** The Replays browser and the Highlights reel. */
  picker: Object.freeze({
    // Game order is seed order: a game is named by its seed.
    highlightsIntro: "Games grouped by the moments they hold, each list in game order.",
    // True in both the live build and the static demo bundle, which serves a
    // SUBSET of the recorded set, so it claims no completeness.
    replaysIntro: "Recorded games for this set. Open one to watch it.",
    featuredHeading: "Featured",
    revealOutcomes: "Reveal outcomes",
    loadingSet: "Loading {set}…",
    loadingReplays: "Loading recorded games…",
    emptySet: "No recorded games are available for this set.",
    // Each failure says what could not load; the raw error follows it.
    replaysLoadError: "The recorded games could not be loaded:",
    setListError: "The set list could not be loaded:",
    replayLoadError: "This game could not be loaded:",
    unknownError: "No reason was given.",
  }),

  /** The playback transport. */
  transport: Object.freeze({
    agentClockNote: "engine clock · agent notes read one tick ahead",
    agentClockTitle:
      "This scrubber shows the engine's own tick. A memory line stamped tick N describes the map as it stood at N−1, while the meeting header's tick matches this readout exactly.",
    // The meeting pause bar's two ways forward.
    nextKeyMoment: "Next key moment",
    resumeTitle: "Resume playback past this meeting",
  }),

  /** One meeting turn. */
  turn: Object.freeze({
    fabricatedOpeningTitle:
      "This emergency opening claimed a body nobody had found; the claim was stripped before the transcript.",
    // One name per kind of turn, read by the turn card's tag, the evidence
    // list and the source panel alike.
    kinds: Object.freeze({
      opening: "first statement",
      reply: "reply",
      opt_in: "spoke up",
    }),
    tag: "tick {tick} · {kind}",
  }),

  /** The mind inspector's belief tab: what the player did at the meeting. */
  inspector: Object.freeze({
    trailHeading: "Said / Claimed / Voted / Result",
    trailLabels: Object.freeze({
      said: "Said",
      claimed: "Claimed",
      voted: "Voted",
      result: "Result",
    }),
    resultEjected: "Meeting: {player} was ejected",
    resultNone: "Meeting: no one was ejected",
    trailEmpty: "No recorded decisions for this agent in this meeting.",
    // Each step's own words: a claim as the player made it, the vote as cast.
    accused: "accused {against} — {reason}",
    alibi: "alibi for {subject}: {path}",
    alibiNoRoute: "alibi for {subject}: no route stated",
    alibiLeg: "{room}, ticks {from}–{to}",
    corroborated: "corroborated {supports} on tick {tick} — {reason}",
    votedSkip: "voted to skip",
    votedEject: "voted to eject {target}",
    // A confidence's face is its word; the number is on hover.
    confidence: "confidence {bucket}",
    confidenceTitle: "confidence {value} · snapshot tick {tick}",
    suspicionOf: "suspicion of {subject}: {bucket}",
  }),

  /** The belief panel: who suspects whom, the real roles, and its legend. */
  beliefPanel: Object.freeze({
    heading: "Who suspects whom",
    rowsColumns: "Read across a row: how much that player suspects each of the others.",
    // The layer names. "Error" is the held layer's own word.
    layers: Object.freeze({ belief: "Belief", truth: "Real roles", error: "Error" }),
    layerGroup: "Belief / Real roles / Error layer",
    perspectiveChip: "One player's perspective · real roles hidden",
    hiddenTitle: "Hidden in one player's perspective, because it would show real roles",
    legendTruthHeading: "READING: REAL ROLES",
    suspicionLabel: "Suspicion",
    suspicionDesc:
      "How much the row's player suspects the column's player: Low, Med or High. Hover a cell for the number.",
    noBeliefLabel: "No belief yet",
    noBeliefDesc: "Hatched: this player has formed no view yet, which is not the same as no suspicion.",
    selfLabel: "Self",
    selfDesc: "The diagonal: a player holds no suspicion of themselves.",
    daggerLabel: "Dagger",
    daggerDesc: "A real impostor, all-roles view only.",
    impostorColumnLabel: "Impostor column",
    impostorColumnDesc: "A faint hatch on a real impostor's column.",
    deadLabel: "Dead",
    deadDesc: "A frozen row and column: this player was dead at this meeting.",
    perspectiveNote:
      "One player's perspective: real roles and error are hidden (they would show who the impostor is).",
    cellTitle: "suspicion {value} of 100",
    cellLabel: "{pair}: suspicion {bucket} ({value} of 100), confidence {confidenceBucket} ({confidence})",
    // The change since the last meeting, as a move between words; the points
    // are on hover.
    changeAbsent: "Agent absent at this meeting.",
    changeNoBelief: "No belief formed about this subject yet.",
    changeFirst: "First recorded meeting.",
    changeBelieverAbsent: "Believer was absent before — first belief here.",
    changeNew: "New belief formed this meeting.",
    changeNone: "No change in suspicion since the previous meeting.",
    changeRose: "Suspicion rose from {from} to {to} since the previous meeting.",
    changeFell: "Suspicion fell from {from} to {to} since the previous meeting.",
    changeRoseWithin: "Suspicion rose but stayed {bucket} since the previous meeting.",
    changeFellWithin: "Suspicion fell but stayed {bucket} since the previous meeting.",
    changeTitle: "{points} points, from {from} to {to} of 100",
  }),

  /** Suspicion and confidence in words, cut where the heat ramp cuts. */
  buckets: Object.freeze({ low: "Low", med: "Med", high: "High" }),

  /** The public results page: its ejection tile and its recorded-behavior groups. */
  publicResults: Object.freeze({
    intro:
      "These are recorded games, not live AI responses. Results cover all {games} games with {set}; the replay browser may offer a smaller featured selection. Each recording was replayed and checked before counting.",
    // The curated cases: two, both on the 9-player set, so the other set's
    // empty state points there (`tests/api/test_public_results.py` holds the
    // count word to the published cases).
    noCases: "No worked examples for this set yet; the 9-player set has two.",
    inspectMeeting: "Inspect the meeting (shows roles)",
    revealAnalysis: "Reveal case analysis (spoilers)",
    hideAnalysis: "Hide analysis",
    rawRecording: "Raw recording file",
    // The proof row, after the cases: a role read, reported and never a
    // headline, so it says what it counts and why its first half measures no
    // deduction.
    proofHeading: "Ejected players who were impostors, with and without a vent sighting",
    proofWith: "With a vent sighting:",
    proofWithout: "Without one:",
    proofCaptionLead:
      "Each count is impostors among the ejected players in that group. Only impostors can vent, so the first count says nothing about how well the table reasoned.",
    proofCaptionOne: "The {count} ejection without a sighting shows how the table decided without proof.",
    proofCaptionMany: "The {count} ejections without a sighting show how the table decided without proof.",
    proofCaptionTail:
      "A sighting in a meeting does not show that it caused the vote, and these counts describe this set of recordings only.",
    usageLine:
      "Reported call usage, including incomplete attempts: {input} input tokens · {output} output tokens · {cost}. An interrupted call may lack provider usage.",
    // Both shown sets were recorded on a flat-rate service, so a zero reads as
    // that; any other value keeps its figure.
    costZero: "$0: a flat-rate service, so usage, not a bill",
    costValue: "{cost} of usage, not a bill",
    technicalHeading: "Technical identifiers, for reproduction",
    promptVersions: "Prompt versions: {versions}.",
    promptVersionsNone: "not recorded",
    fingerprint: "Source fingerprint: {fingerprint}",
    // The tile counts impostors among ejected players, a role read reported
    // beside the process figures, so its heading says what the fraction counts
    // and never calls an ejection correct.
    ejectionsHeading: "Ejected players who were impostors",
    ejectionsDescription:
      "Impostors / all ejected players across {meetings} resolved meetings. {innocent} innocent ejections; skips are excluded.",
    // The group's agents, by the factory kind its recordings stamp. The
    // `experimental` kind is exact built-in agents run with recorded tactical
    // settings, so its label says that and not "experimental".
    factoryCustom: "Custom agent factory",
    factoryBuiltInWithSettings: "Built-in agents with recorded tactical settings",
    factoryScripted: "Built-in scripted agent factory",
    factoryUnknown: "Agent factory not recorded",
    recordingCountOne: "{count} recording",
    recordingCountMany: "{count} recordings",
    // Three leads, one per kind of recorded setting. A field is listed as
    // adopted only at a value `lib/adoptedRules.ts` names; a setting these
    // recordings carry without its being adopted is named as set for them; any
    // other value off its default stays an experiment.
    adoptedLead: "Rules adopted for the current game: {rules}",
    setForRecordingsLead: "Also in place: {settings}.",
    experimentsLead: "Recorded experiments: {experiments}.",
    noRecordedSettings:
      "No enabled experiments recorded. This alone does not certify the default behavior.",
    ruleSeparator: "; ",
    // The adopted rules are each a sentence of their own.
    sentenceSeparator: " ",
    experimentSeparator: ", ",
    // Each adopted rule as a plain sentence, keyed by the field it adopts.
    adoptedRules: Object.freeze({
      vent_witness_rule: "Vent use is seen only in the room where it happens.",
      vent_entry_policy: "Impostors enter a vent only beside a body they have just killed.",
      meeting_reset:
        "After each meeting, the survivors start again from the meeting room with the bodies cleared.",
      bounded_rebuttal_version: "A player accused after already speaking gets one reply.",
      report_body_handle_version: "A body report does not give the time of death.",
      ballot_kill_row_version: "Each ballot lists the kills its voter saw a player from the other side make.",
      impostor_ballot_version: "An impostor is asked to vote as a move for its own side.",
    }),
    // Kept in these recordings, not part of the adopted list.
    ventExitWaits:
      "impostors in a vent wait briefly for the rooms they can see to clear before coming out, set for these recordings",
    killCooldownOne: "a kill cooldown of {ticks} tick set for these recordings",
    killCooldownMany: "a kill cooldown of {ticks} ticks set for these recordings",
    // The route lines: kept in the shown recordings since 2026-10-09, not adopted.
    routeLines:
      "each ballot lists which changes of room stated at the meeting the doors, or the restart after a meeting, allow, set for these recordings",
    // The settings that stay experiments.
    evidenceReasoning: "observation timing and travel checks v{version}",
    investigation: "bounded missing-player searches",
    contextualSelfReport: "context-dependent self-reporting",
    publicAccount: "common public accounts",
    attributedTestimony: "attributed witness testimony",
    movementPolicies: "experimental movement or action policies",
    roundRules: "experimental round or task rules",
    policyLine: "Impostor policy: {impostor}. Crew policy: {crew}. Rule settings: {rules}.",
    // A recording with no policy stamp ran the default movers; "unknown" is
    // kept for what the record cannot say.
    defaultPolicy: "the built-in scripted policy",
    recorded: "recorded",
    unknown: "unknown",
    clockLine: "Observation clock: {clock}.",
    // Recorded settings with timed observations off mean the standard timing.
    clockStandard: "the standard timing",
    clockVersion: "v{version}",
  }),

  /** The game-shape profile: shelves, the chip, facets and the tripwire. */
  profile: Object.freeze({
    heading: "Browse by moment",
    allGames: "All games",
    allGamesNote:
      "Every game listed here, in game order, including games kept off the shelves.",
    revealHeading: "After the reveal",
    revealNote:
      "These shelves read how the game ended, whether a meeting voted someone out, or a player's role, so they stay hidden until you reveal outcomes.",
    countOne: "{count} game",
    countMany: "{count} games",
    cardShelves: "Shelves this game sits on",
    loading: "Loading moments…",
    filterVotedOut: "someone was voted out",
    absentTitle: "No game-shape profile for this set",
    // The set's name leads, since it carries its own parentheses.
    absentBody:
      "{set}: the served set ships no game-shape profile, so its games sit on no shelf. Browse Replays to inspect this set without one.",
    absentBodyUnnamed:
      "The served set ships no game-shape profile, so its games sit on no shelf. Browse Replays to inspect this set without one.",
    staleTitle: "No current game-shape profile",
    staleBody:
      "The profile was computed from recordings that no longer match the served ones, so its shelves are hidden. The recordings remain available through Featured and Replays.",
    replaysNoProfile: "{set}: this set ships no game-shape profile, so its cards show no shelves.",
    browseReplays: "Browse all replays",
    loadError: "The game-shape profile could not be loaded:",
    // Each shelf by the name the served profile gives it. No description
    // carries a number: the definitions, with their constants, are on the
    // generated page.
    shelves: Object.freeze({
      the_reporter_saw_it_happen: Object.freeze({
        title: "The reporter saw it happen",
        description:
          "The player who reported the body is one the game records as seeing that kill.",
      }),
      double_kill: Object.freeze({
        title: "Double kill",
        description: "Two players were killed in the same moment.",
      }),
      slow_burn: Object.freeze({
        title: "Slow burn",
        description: "A long quiet stretch passed with no kill.",
      }),
      two_kills_after_one_regroup: Object.freeze({
        title: "Two kills after one regroup",
        description:
          "Soon after the survivors were gathered back together, two of them were killed.",
      }),
      a_close_call: Object.freeze({
        title: "A close call",
        description: "A meeting was settled by a single ballot, or ended in a tie.",
      }),
      suspicion_moved: Object.freeze({
        title: "Suspicion moved",
        description:
          "From one meeting to the next the votes turned toward someone new, or away from someone still alive.",
      }),
      a_third_round: Object.freeze({
        title: "A third round",
        description: "The table met for a third time, or more.",
      }),
      caught_venting: Object.freeze({
        title: "Caught venting",
        description: "Someone told the table they saw a player use a vent.",
      }),
      one_line_two_readings: Object.freeze({
        title: "One line, two readings",
        description:
          "Two voters cited the same spoken line and came to different decisions.",
      }),
      struck_after_the_regroup: Object.freeze({
        title: "Struck after the regroup",
        description: "A kill came soon after the survivors were gathered back together.",
      }),
      one_vote_ejection: Object.freeze({
        title: "One-vote ejection",
        description: "A player was voted out by the margin of a single ballot.",
      }),
      nobody_voted_out: Object.freeze({
        title: "Nobody voted out",
        description: "Every meeting ended without anyone being voted out.",
      }),
      down_to_the_wire: Object.freeze({
        title: "Down to the wire",
        description: "The losing side was one step from winning.",
      }),
      runaway: Object.freeze({
        title: "Runaway",
        description: "The losing side was still far from winning when the game ended.",
      }),
      decided_at_a_meeting: Object.freeze({
        title: "Decided at a meeting",
        description: "The game ended at a meeting.",
      }),
      decided_without_proof_right: Object.freeze({
        title: "Decided without proof: the table was right",
        description:
          "The voters ejected on lines they held, with no vent sighting, and the table was right.",
      }),
      decided_without_proof_wrong: Object.freeze({
        title: "Decided without proof: wrong on what it held",
        description:
          "The voters cited lines they held and it pointed the wrong way. A wrong call on believable evidence is part of the game.",
      }),
    }),
    pair: Object.freeze({
      heading: "Decided without proof",
      note: "Ejections whose voters rested on lines they held, with no vent sighting. The two halves always show together.",
      emptyHalf: "No game listed here lands on this half.",
    }),
    chip: Object.freeze({
      atMeeting: "An eyewitness voted on it at meeting {meeting}",
      description:
        "A player who saw the kill cited it on their own ballot at this meeting.",
    }),
    // The tripwire's plain label, before the reveal by the owner's ruling.
    tripwires: Object.freeze({
      decided_by_a_vote_that_held_nothing:
        "Kept off the shelves: at meeting {meeting} a player was voted out on ballots that cited nothing the voters held about them, and without those ballots the meeting would have gone another way.",
      decided_on_a_manufactured_contradiction:
        "Kept off the shelves: at meeting {meeting} a player was voted out on a contradiction raised against an account that was in fact true.",
    }),
    facets: Object.freeze({
      ticks: "{ticks} ticks",
      meetings: "{count} meetings · {reported} reported, {called} called",
      noMeetings: "No meetings",
      kills: "{count} kills · {wave} soon after a regroup",
      noKills: "No kills",
      bodiesNeverFound: "{count} bodies never found",
      report: "Meeting {meeting}: the body was found {age} ticks after the kill",
      timeline: "Game timeline: kills and meetings, tick by tick",
      timelineKill: "Kill at tick {tick}",
      timelineWaveKill: "Kill at tick {tick}, soon after a regroup",
      timelineMeeting: "Meeting {meeting} at tick {tick}",
    }),
    revealFacets: Object.freeze({
      ending: "Ended: {ending}",
      endings: Object.freeze({
        CREWMATE_EJECT: "the crew voted out every impostor",
        CREWMATE_TASKS: "the crew finished its tasks",
        IMPOSTOR_PARITY: "the impostors matched the crew in number",
        IMPOSTOR_SABOTAGE: "a sabotage ran out",
        TICK_BUDGET_REACHED: "the run stopped at its tick limit",
        MEETING_PHASE_REACHED: "the run stopped at a meeting",
      }),
      tasksLeft: "The crew had {steps} of {start} tasks left.",
      killsShort:
        "The impostors were {steps} kills from matching the crew; they started {start} away.",
      tasks: "{done} of {assigned} tasks done",
      sabotage: "A sabotage was in play from tick {tick}.",
      // Facts about the ejected player's recorded role, never a verdict on the vote.
      ejectedImpostor: "Meeting {meeting}: an impostor was voted out",
      ejectedCrewmate: "Meeting {meeting}: a crewmate was voted out",
    }),
  }),
} as const);

export const BALLOT_COPY = SPECTATOR_COPY.ballot;
export const BELIEF_PANEL_COPY = SPECTATOR_COPY.beliefPanel;
export const BUCKET_COPY = SPECTATOR_COPY.buckets;
export const DASHBOARD_COPY = SPECTATOR_COPY.dashboard;
export const EVIDENCE_SOURCE_COPY = SPECTATOR_COPY.evidenceSource;
export const GAME_COPY = SPECTATOR_COPY.game;
export const HEADER_COPY = SPECTATOR_COPY.header;
export const INSPECTOR_COPY = SPECTATOR_COPY.inspector;
export const MAP_COPY = SPECTATOR_COPY.map;
export const MEETING_COPY = SPECTATOR_COPY.meeting;
export const NAV_COPY = SPECTATOR_COPY.nav;
export const OUTCOME_COPY = SPECTATOR_COPY.outcome;
export const PERSPECTIVE_COPY = SPECTATOR_COPY.perspective;
export const PICKER_COPY = SPECTATOR_COPY.picker;
export const PROFILE_COPY = SPECTATOR_COPY.profile;
export const PUBLIC_RESULTS_COPY = SPECTATOR_COPY.publicResults;
export const SITE_COPY = SPECTATOR_COPY.site;
export const TOUR_COPY = SPECTATOR_COPY.tour;
export const TRANSPORT_COPY = SPECTATOR_COPY.transport;
export const TURN_COPY = SPECTATOR_COPY.turn;

// ── the workspace's names ────────────────────────────────────────────────────

/** A game by its number, which is its seed: "Game 19". */
export function gameName(seed: number): string {
  return fmt(GAME_COPY.name, { n: String(seed) });
}

/** The tooltip beside a game's name, which says where the number comes from. */
export function gameSeedTitle(seed: number): string {
  return fmt(GAME_COPY.seedTitle, { seed: String(seed) });
}

/** A game card's accessible name: "Open game 19". */
export function openGameLabel(seed: number): string {
  return fmt(GAME_COPY.open, { n: String(seed) });
}

/** "1 player" / "9 players". */
export function playerCount(count: number): string {
  return fmt(count === 1 ? GAME_COPY.playersOne : GAME_COPY.playersMany, {
    count: String(count),
  });
}

/** "1 meeting" / "3 meetings". */
export function meetingCount(count: number): string {
  return fmt(count === 1 ? GAME_COPY.meetingsOne : GAME_COPY.meetingsMany, {
    count: String(count),
  });
}

/**
 * How a recording ended, as its tag reads on the card, in the workspace banner
 * and on the finale: the recorded winner, or else the recorded stop. A
 * recording older than the stop classification carries none and reads as
 * unfinished, never as a winner it did not record.
 */
export function outcomeTag(
  winner: Winner | null,
  completionStatus: ReplayMetadataView["completion_status"] | null,
): string {
  if (winner === "CREWMATES") return OUTCOME_COPY.crewWin;
  if (winner === "IMPOSTORS") return OUTCOME_COPY.impostorWin;
  if (completionStatus === "aborted") return OUTCOME_COPY.aborted;
  if (completionStatus === "tick_limited") return OUTCOME_COPY.tickLimited;
  return OUTCOME_COPY.unfinished;
}

/**
 * A recorded ending in the cards' words, or `null` for an ending this build has
 * no words for. Own keys only: a recorded reason such as `constructor` must not
 * be answered from `Object.prototype`.
 */
export function endingPhrase(ending: string): string | null {
  const endings: Readonly<Record<string, string>> = PROFILE_COPY.revealFacets.endings;
  return Object.hasOwn(endings, ending) ? (endings[ending] ?? null) : null;
}

/** The line under a lone body in the all-roles view: "killed by p-4". */
export function killedByLabel(killer: string): string {
  return fmt(MAP_COPY.killedBy, { killer });
}

/**
 * The sabotage readout, one style in both views. The all-roles view names the
 * sabotage and counts it down; one player's view keeps hiding the room and the
 * countdown it has always hidden, naming only the darkness or the alarm that
 * player perceives.
 */
export function sabotageHud(
  kind: SabotageDetailView["kind"],
  remainingTicks: number,
  omniscient: boolean,
): string {
  if (!omniscient) {
    return kind === "lights" ? MAP_COPY.lightsOut : MAP_COPY.reactorAlarm;
  }
  const one = remainingTicks === 1;
  const template =
    kind === "lights"
      ? one
        ? MAP_COPY.lightsCountdownOne
        : MAP_COPY.lightsCountdownMany
      : one
        ? MAP_COPY.reactorCountdownOne
        : MAP_COPY.reactorCountdownMany;
  return fmt(template, { ticks: String(remainingTicks) });
}
