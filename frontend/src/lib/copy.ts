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
//   • `PROFILE_COPY` — the game-shape profile's shelf, chip, facet and
//     tripwire words, keyed by the names the served profile carries.
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

  /** The meeting dialog's Resolution card, and its omniscient-only record. */
  meeting: Object.freeze({
    resolutionGateBadge: "vote gate",
    resolutionGateLead: "How the vote resolved",
    // Three facts the omniscient view adds to a meeting (`lib/annotations.ts`).
    // None renders under a player's lens: the kill tick is withheld from every
    // player at the table, and the rooms are the engine's record of where each
    // accused player stood, not anyone's account of it.
    engineRecordHeading: "What the recording shows",
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
  }),

  /** One ballot card's private-reasoning block. */
  ballot: Object.freeze({
    // The recorded weighing artefact: who this voter wrote down while choosing.
    // The heading deliberately claims NOTHING about who those are — an earlier
    // "Also weighed" said the OTHER players, and the bytes falsify that. Over
    // `replays/samples/9p2i`, 28 of 691 ballots list the voter ITSELF (measured
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
    groundingLabel: "Basis on the record",
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
  }),

  /** The Replays browser and the Highlights reel. */
  picker: Object.freeze({
    highlightsIntro:
      "Games grouped by the moments they hold, each list in seed order. Nothing here ranks or scores a game.",
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

  /** One recorded-behavior group on the public results page. */
  publicResults: Object.freeze({
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
    adoptedLead: "Rules adopted for the current game: {rules}.",
    setForRecordingsLead: "Also in place: {settings}.",
    experimentsLead: "Recorded experiments: {experiments}.",
    noRecordedSettings:
      "No enabled experiments recorded. This alone does not certify the default behavior.",
    ruleSeparator: "; ",
    experimentSeparator: ", ",
    // Each adopted rule in plain words, keyed by the field it adopts.
    adoptedRules: Object.freeze({
      vent_witness_rule: "vent use seen only in the room where it happens",
      vent_entry_policy: "impostors enter a vent only beside a body they have just killed",
      meeting_reset:
        "after each meeting, the survivors start again from the meeting room with the bodies cleared",
      bounded_rebuttal_version: "one reply to a late accusation",
      report_body_handle_version: "body reports without the time of death",
      ballot_kill_row_version: "witnessed kills listed on the voter's ballot",
      impostor_ballot_version: "impostor ballots cast by strategy",
    }),
    // Kept in these recordings, not part of the adopted list.
    ventExitWaits:
      "impostors in a vent wait briefly for the rooms they can see to clear before coming out, set for these recordings",
    killCooldownOne: "a kill cooldown of {ticks} tick set for these recordings",
    killCooldownMany: "a kill cooldown of {ticks} ticks set for these recordings",
    // The settings that stay experiments.
    evidenceReasoning: "observation timing and travel checks v{version}",
    investigation: "bounded missing-player searches",
    contextualSelfReport: "context-dependent self-reporting",
    publicAccount: "common public accounts",
    attributedTestimony: "attributed witness testimony",
    movementPolicies: "experimental movement or action policies",
    roundRules: "experimental round or task rules",
    policyLine: "Impostor policy: {impostor}. Crew policy: {crew}. Rule settings: {rules}.",
    notRecorded: "not recorded",
    recorded: "recorded",
    clockLine: "Observation clock: {clock}.",
    clockVersion: "v{version}",
  }),

  /** The game-shape profile: shelves, the chip, facets and the tripwire. */
  profile: Object.freeze({
    heading: "Browse by moment",
    allGames: "All games",
    allGamesNote:
      "Every game listed here, in seed order, including any a tripwire keeps off the shelves.",
    revealHeading: "After the reveal",
    revealNote:
      "These shelves read how the game ended, whether a meeting voted someone out, or a player's role, so they stay hidden until you reveal outcomes.",
    countOne: "{count} game",
    countMany: "{count} games",
    cardShelves: "Shelves this game sits on",
    loading: "Loading moments…",
    filterVotedOut: "someone was voted out",
    absentTitle: "No game-shape profile for this set",
    absentBody:
      "The served set ({set}) ships no game-shape profile, so its games sit on no shelf. Browse Replays to inspect this set without one.",
    absentBodyUnnamed:
      "The served set ships no game-shape profile, so its games sit on no shelf. Browse Replays to inspect this set without one.",
    staleTitle: "No current game-shape profile",
    staleBody:
      "The profile was computed from recordings that no longer match the served ones, so its shelves are hidden. The recordings remain available through Featured and Replays.",
    replaysNoProfile:
      "This set ({set}) ships no game-shape profile, so its cards show no shelves.",
    browseReplays: "Browse all replays",
    loadError: "Failed to load the game-shape profile:",
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
      ejectionRight: "Meeting {meeting}: the vote was right",
      ejectionWrong: "Meeting {meeting}: the vote was wrong",
    }),
  }),
} as const);

export const BALLOT_COPY = SPECTATOR_COPY.ballot;
export const DASHBOARD_COPY = SPECTATOR_COPY.dashboard;
export const MAP_COPY = SPECTATOR_COPY.map;
export const MEETING_COPY = SPECTATOR_COPY.meeting;
export const PICKER_COPY = SPECTATOR_COPY.picker;
export const PROFILE_COPY = SPECTATOR_COPY.profile;
export const PUBLIC_RESULTS_COPY = SPECTATOR_COPY.publicResults;
export const TRANSPORT_COPY = SPECTATOR_COPY.transport;
export const TURN_COPY = SPECTATOR_COPY.turn;
