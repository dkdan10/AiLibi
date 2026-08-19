// The spectator surface's user-facing copy, plus the pure helpers that keep it
// honest.
//
// Five things live here, and they live here together on purpose:
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
//   • `RUBRIC_SPOKES` / `rubricLegendLine` — one table behind both the score
//     bars and the picker's legend, so the two cannot drift apart.
//
// Also here: `showsBallotCorrectness`, the ballot correctness-badge gate. It is
// a display gate over copy (the ✓/✗ mark), stated as a pure predicate so the
// four perspective × reveal combinations are assertable with no DOM.
//
// AGENTS.md craft rule 4 ("no internal dialect on user-facing surfaces").

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
const SET_NAMES: Readonly<Record<string, string | undefined>> = Object.freeze({
  "9p2i": "9 players, 2 impostors",
  "4p1i": "4 players, 1 impostor",
});

/** A set id in words, or the id itself when it is not one we can expand. */
export function expandSetName(setId: string): string {
  return SET_NAMES[setId] ?? setId;
}

/**
 * A set id as it reads in a control or a sentence.
 *
 * Keeps the raw id — it is what the `set` URL key and the manifests use — and
 * appends the expansion when there is one, so a known set reads
 * "9p2i — 9 players, 2 impostors" and an unknown one reads as its bare id
 * rather than as the id twice.
 */
export function setOptionLabel(setId: string): string {
  const expanded = expandSetName(setId);
  return expanded === setId ? setId : `${setId} — ${expanded}`;
}

// ── the interestingness sub-scores ───────────────────────────────────────────

/** One spoke of the 4-bar interestingness sub-score. */
export interface RubricSpoke {
  /** The rubric's own short key, which the bar prints. */
  readonly key: "R1" | "R2" | "R3" | "R7";
  /** What the bar measures — printed on the bar AND in the picker legend. */
  readonly word: string;
  /** The `RubricGameView` field this bar reads. */
  readonly field: "r1_decisive" | "r2_deception" | "r3_arcs" | "r7_legible";
}

/** The four spokes, in render order. One table, both surfaces. */
export const RUBRIC_SPOKES: readonly RubricSpoke[] = Object.freeze([
  { key: "R1", word: "deduction", field: "r1_decisive" },
  { key: "R2", word: "deception", field: "r2_deception" },
  { key: "R3", word: "suspicion arcs", field: "r3_arcs" },
  { key: "R7", word: "legibility", field: "r7_legible" },
] as const);

/**
 * The header legend for the score bars, built FROM the table.
 *
 * Built rather than written out so a spoke renamed in one place cannot leave
 * the other saying something else — the drift that left the Replays tab
 * showing four unlabelled bars while only Highlights explained them.
 */
export function rubricLegendLine(): string {
  const spokes = RUBRIC_SPOKES.map((s) => `${s.word} (${s.key})`).join(", ");
  return `Score bars: ${spokes}.`;
}

/** The hover text for one bar: what it measures and where the value sits. */
export function rubricSpokeTitle(spoke: RubricSpoke, value: number): string {
  return `${spoke.key} ${spoke.word}: ${value.toFixed(2)} on a 0–1 scale`;
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
  /** The Tournament tab. Every prose string on that surface is here. */
  dashboard: Object.freeze({
    intro:
      "The latest tournament eval report: balance outcome, vote correctness, the conversion and gate surface, the proof-vs-inference deduction instrument, and the interestingness distribution.",
    refresh: "Refresh",
    refreshBusy: "Loading…",
    loadingReport: "Loading tournament report…",
    noReportTitle: "No tournament report.",
    noReportLead: "A 404 means no",
    noReportMiddle: "exists in the configured eval directory yet — run a tournament with",
    noReportTail: "to produce one.",

    balanceTitle: "Balance outcome",
    balanceDescription:
      "Crew / impostor / tick-budget split across the tournament's recorded games.",
    balanceGames: "Games recorded",
    balanceSeedsAttempted: "{n} seeds attempted",
    balanceSeeds: "{n} seeds",
    balanceCrewWins: "Crew wins",
    balanceImpostorWins: "Impostor wins",
    balanceTickBudget: "Tick budget",
    balanceTickBudgetHint: "non-decisive",
    balanceCrewWinRate: "Crew win rate",
    balanceCrewWinRateHint: "of decisive games",

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
    conversionCorrectSkipsHint: "skips where no accusation met the confidence bar",
    conversionMissedSkips: "Missed skips",
    conversionMissedSkipsHint:
      "impostor voters {impostorVoters} · invalid targets {invalidTargets} · crew declined {crewDeclined}",
    conversionMissedSkipsCaveat: "read the split, not the total",
    conversionMissedSkipsCaveatTitle:
      "Read the split, not the total: most missed skips are impostors voting their own side, or targets the parser had to normalize away. What is left is a crew voter who declined an accusation that met the confidence bar — see its own tile.",
    conversionInversions: "Threshold inversions",
    conversionInversionsHint: "crew voters who declined a met bar",
    conversionInversionsCaveat: "discretionary — nonzero intended",
    conversionInversionsCaveatTitle:
      "A crew voter whose strongest ballot met the confidence bar and who skipped anyway. The vote gate is advice, not an order, so declining is allowed play: a nonzero count is expected on recorded sets, not a bug.",
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
    gateGenuineCaveat: "historical — too little data to read",
    gateGenuineCaveatTitle:
      "The older alibi-anchored form of the tile beside it. Checkable alibi lies almost stopped being produced, so this cell reads no-data rather than a regression, and it is reported for continuity only.",
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

    alibiTitle: "Alibi fabrication",
    alibiDescription:
      "Share of impostor-authored alibis that survived the contradiction detector (a conservative lower bound). High = impostors getting away with fabricated cover; low = the detector catching it. 'n/a' when no impostor alibis were filed.",
    alibiSurvivalRate: "Survival rate",
    alibiSurvivalRateHint: "{survived} / {total} survived",
    alibiTotal: "Impostor alibis",
    alibiSurvived: "Survived",

    interestingnessTitle: "Interestingness",
    interestingnessDescription:
      "Distribution of the rubric's 0–100 score — an internal pacing/structure heuristic, not a human rating. Click a bucket to open those seeds in the Highlights reel.",
    interestingnessStaleCaveat: "scores may be stale",
    interestingnessStaleCaveatTitle:
      "The rubric was scored against different bytes than the set now serves, so these scores may be stale. Re-score the set to refresh them.",
    interestingnessLoading: "Loading the interestingness rubric…",
    interestingnessAbsentTitle: "No interestingness rubric.",
    interestingnessAbsentLead:
      "The selected set ships no rubric — expected for 4p1i, the fast technical fixture (median 12 ticks, at most one meeting per game). Switch back to the default 9p2i set, which ships one, or run",
    interestingnessAbsentTail: "over this set to populate the histogram.",
    interestingnessError: "Couldn't load the rubric:",
    interestingnessEmpty: "The rubric is present but scored no games for this set.",
    interestingnessFooter:
      "{games} games scored on {set} · click a bucket to open it in the Highlights reel →",
    interestingnessBucketLink:
      "Open {count} {bucket}-interestingness game{plural} (score {range}) in the Highlights reel",
    interestingnessScorePrefix: "score",

    costTitle: "Cost dashboard",
    costDescription:
      "Tournament LLM spend roll-up. Per-(template, version) totals OVERLAP — the full game cost is attributed once per template a game ran — so they do not sum to the tournament total.",
    costTotal: "Total cost",
    costMean: "Mean / game",
    costMeanHint: "target ≈ $0.20/game",
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

  /** The meeting dialog's Resolution card. */
  meeting: Object.freeze({
    resolutionGateBadge: "vote gate",
    resolutionGateLead: "How the vote resolved",
  }),

  /** The Replays browser and the Highlights reel. */
  picker: Object.freeze({
    highlightsIntro: "Ordered by the interestingness rubric.",
    // True in both the live build and the static demo bundle, which serves a
    // SUBSET of the recorded set — the old "Every recorded replay in the served
    // set" was false there, and the flag that would tell them apart is private
    // to the API client.
    replaysIntro:
      "The replays this build serves for the selected set. Click a card to open it.",
  }),

  /** The playback transport. */
  transport: Object.freeze({
    agentClockNote: "engine clock · agent notes read one tick ahead",
    agentClockTitle:
      "This scrubber shows the engine's own tick. A memory line stamped tick N describes the map as it stood at N−1, while the meeting header's tick matches this readout exactly.",
  }),

  /** One meeting turn. */
  turn: Object.freeze({
    fabricatedOpeningTitle:
      "This emergency opening claimed a body nobody had found; the claim was stripped before the transcript.",
  }),

  /** Shared with `RUBRIC_SPOKES` so the walk covers the spoke words too. */
  rubricSpokes: RUBRIC_SPOKES,
} as const);

export const DASHBOARD_COPY = SPECTATOR_COPY.dashboard;
export const MEETING_COPY = SPECTATOR_COPY.meeting;
export const PICKER_COPY = SPECTATOR_COPY.picker;
export const TRANSPORT_COPY = SPECTATOR_COPY.transport;
export const TURN_COPY = SPECTATOR_COPY.turn;
