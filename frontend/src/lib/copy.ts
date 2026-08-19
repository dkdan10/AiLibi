// The spectator surface's user-facing copy, plus the pure helpers that keep it
// honest.
//
// Four things live here, and they live here together on purpose:
//
//   • `dialectHits` — the matcher for internal dialect (design-doc citations,
//     bare section numbers, task ids, audit paths, and the two undefined words
//     "sentinel" / "KPI"). It is the gate `copy.test.ts` runs over every value
//     below AND over the component sources with comments stripped.
//   • `SPECTATOR_COPY` — the rewritten prose itself. A copy string in a `.tsx`
//     is only checkable through a renderer; a value here is readable by the
//     node-env test project directly, so "no dialect reaches a viewer" is a
//     unit test rather than a review habit.
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
  { name: "undefined jargon", pattern: /\b(?:sentinel|kpi)\b/i },
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
 * keep in sync.
 */
export const SPECTATOR_COPY = Object.freeze({
  /** The Tournament tab. */
  dashboard: Object.freeze({
    intro:
      "The latest tournament eval report: balance outcome, vote correctness, the conversion and gate surface, the proof-vs-inference deduction instrument, and the interestingness distribution.",
    balanceDescription:
      "Crew / impostor / tick-budget split across the tournament's recorded games.",

    voteCorrectnessDescription:
      "The share of impostor ejections that carry hard evidence on the record — a contradiction naming the ejected player, or a kill-witness chain. It is a bug check rather than a quality score: crewmate ejections sit outside its denominator, so it never says how well the table voted. 'n/a' when no impostors were ejected.",
    voteCorrectnessRateCaveat: "bug check, not a score",
    voteCorrectnessRateCaveatTitle:
      "Below 100% means an impostor was ejected with none of that evidence recorded against them — a game worth opening to find out why. For how often the table ejected the right player, read ejection accuracy in the Conversion section.",
    voteCorrectnessSmallNTitle:
      "Under-powered: fewer than 10 impostor ejections, too few to trust this rate as a gate.",

    conversionDescription:
      "Did accusations convert into impostor ejections, and were the skipped votes the right call?",
    missedSkipsCaveat: "read the split, not the total",
    missedSkipsCaveatTitle:
      "Read the split, not the total: most missed skips are impostors voting their own side, or targets the parser had to normalize away. What is left is a crew voter who declined an accusation that met the confidence bar — see its own tile.",
    thresholdInversionCaveatTitle:
      "A crew voter whose strongest ballot met the confidence bar and who skipped anyway. The vote gate is advice, not an order, so declining is allowed play: a nonzero count is expected on recorded sets, not a bug.",

    gateMetricsDescription:
      "Whether evidence the engine hands the crew turns into an ejection. The live signal is supplied-channel conversion; the alibi-anchored genuine-class cell beside it is a historical column, starved on this substrate, and is not read as a signal.",

    deductionDescription:
      "How this set's ejection accuracy splits by whether engine-donated vent proof was PRESENT. The same bytes are cut TWO different ways below — by whether the MEETING carried role proof, and by whether the proof named the EJECTED player. Both are correct; their denominators are different and are never mixed. Presence is co-occurrence, not causation: the split says what evidence was on the record, never that a vote followed it.",

    alibiDescription:
      "Share of impostor-authored alibis that survived the contradiction detector (a conservative lower bound). High = impostors getting away with fabricated cover; low = the detector catching it. 'n/a' when no impostor alibis were filed.",

    costDescription:
      "Tournament LLM spend roll-up. Per-(template, version) totals OVERLAP — the full game cost is attributed once per template a game ran — so they do not sum to the tournament total.",
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
});

export const DASHBOARD_COPY = SPECTATOR_COPY.dashboard;
export const MEETING_COPY = SPECTATOR_COPY.meeting;
export const PICKER_COPY = SPECTATOR_COPY.picker;
export const TRANSPORT_COPY = SPECTATOR_COPY.transport;
export const TURN_COPY = SPECTATOR_COPY.turn;

/**
 * The partition behind the "Missed skips" count, in words.
 *
 * A function because the three counts are formatted by the caller; the WORDS
 * are the part that belongs here ("imp-voter · invalid · inversion" said
 * nothing to a reader who had not read the eval package).
 */
export function missedSkipsHint(
  impostorVoters: string,
  invalidTargets: string,
  crewDeclined: string,
): string {
  return `impostor voters ${impostorVoters} · invalid targets ${invalidTargets} · crew declined ${crewDeclined}`;
}
