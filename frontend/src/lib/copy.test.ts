// The dialect gate for the spectator surface, plus the copy helpers it guards.
//
// Two independent legs, because "no internal dialect reaches a viewer" can fail
// in two different places:
//
//   1. VALUES — every string in `SPECTATOR_COPY` is clean.
//   2. DISK   — the ten component sources, read off disk with comments
//               stripped, carry no dialect either. This is the leg that catches
//               a NEW literal typed straight into JSX, which leg 1 cannot see.
//
// Both legs are useless unless the matcher can fail, so each ships a planted
// case first: a fixture string carrying each dialect class, and a synthetic
// source whose dialect sits in a rendered string (must be caught) alongside
// dialect in a comment (must be ignored). Comments are stripped on purpose —
// provenance in source is allowed and normal; provenance on screen is not.
//
// Those planted fixtures are, deliberately, the ONLY dialect-bearing string
// literals left anywhere in `frontend/src`: nothing renders them, and a gate
// that could not be handed a bad value would prove nothing.

import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  DASHBOARD_COPY,
  GAME_COPY,
  HEADER_COPY,
  MAP_COPY,
  NAV_COPY,
  OUTCOME_COPY,
  PERSPECTIVE_COPY,
  PICKER_COPY,
  PROFILE_COPY,
  PUBLIC_RESULTS_COPY,
  SITE_COPY,
  SPECTATOR_COPY,
  TOUR_COPY,
  TRANSPORT_COPY,
  dialectHits,
  endingPhrase,
  expandSetName,
  fmt,
  gameName,
  gameSeedTitle,
  killedByLabel,
  meetingCount,
  openGameLabel,
  outcomeTag,
  playerCount,
  sabotageHud,
  setOptionLabel,
  showsBallotCorrectness,
} from "./copy";

const LIB_DIR = dirname(fileURLToPath(import.meta.url));

/**
 * The surfaces this task owns. The disk leg must find every one of them clean.
 *
 * `rendered` is a fragment each file still emits inline, asserted to survive the
 * comment strip — a stripper that ate real code would otherwise "pass" every
 * file by handing the matcher an empty string.
 */
const IN_SCOPE_SOURCES: readonly { readonly file: string; readonly rendered: string }[] =
  [
    { file: "TournamentDashboard.tsx", rendered: "TournamentDashboardView" },
    { file: "MeetingView.tsx", rendered: "Resolution" },
    { file: "BallotCard.tsx", rendered: "no rationale recorded" },
    { file: "ReplayPicker.tsx", rendered: "Clear filters" },
    { file: "HighlightCard.tsx", rendered: "Outcome hidden" },
    { file: "ReplayControls.tsx", rendered: "Next key moment" },
    { file: "MetricCaveat.tsx", rendered: "note" },
    { file: "TurnCard.tsx", rendered: "accuses" },
    // The map stage renders the regroup note through `MAP_COPY` and its one
    // literal fallback inline.
    { file: "MapView.tsx", rendered: "Select a replay to view the map." },
    // The public results page: its recorded-behavior groups and its ejection
    // tile render through `PUBLIC_RESULTS_COPY`, the rest of the page still inline.
    { file: "PublicResults.tsx", rendered: "What the recordings show" },
  ];

// EMPTY, and staying that way is the point: every in-scope surface — TurnCard.tsx
// included — must come back clean, so adding an entry here is a deliberate act
// that shows up in a diff. It is a live filter, not decoration: a file listed
// here really is skipped below.
const DIALECT_ALLOW_LIST: readonly string[] = [];

const CHECKED_SOURCES = IN_SCOPE_SOURCES.filter(
  (source) => !DIALECT_ALLOW_LIST.includes(source.file),
);

/**
 * `source` with line comments, block comments and JSX comments removed.
 *
 * String and template literals are tracked so a `//` inside one survives.
 * Regex literals are NOT parsed: a regex containing a quote character would
 * open a phantom string, which is why every file also asserts a known rendered
 * fragment survives the strip.
 */
function stripComments(source: string): string {
  let out = "";
  let i = 0;
  let quote: string | null = null;
  while (i < source.length) {
    const ch = source[i] ?? "";
    const next = source[i + 1] ?? "";
    if (quote !== null) {
      out += ch;
      if (ch === "\\") {
        out += next;
        i += 2;
        continue;
      }
      if (ch === quote) {
        quote = null;
      }
      i += 1;
      continue;
    }
    if (ch === '"' || ch === "'" || ch === "`") {
      quote = ch;
      out += ch;
      i += 1;
      continue;
    }
    if (ch === "/" && next === "/") {
      while (i < source.length && source[i] !== "\n") i += 1;
      continue;
    }
    if (ch === "/" && next === "*") {
      i += 2;
      while (i < source.length && !(source[i] === "*" && source[i + 1] === "/")) i += 1;
      i += 2;
      continue;
    }
    out += ch;
    i += 1;
  }
  return out;
}

/** Every string in a copy tree, with the path that reaches it. */
function stringLeaves(
  value: unknown,
  path: string,
): readonly { readonly path: string; readonly text: string }[] {
  if (typeof value === "string") {
    return [{ path, text: value }];
  }
  if (Array.isArray(value)) {
    return value.flatMap((item, index) => stringLeaves(item, `${path}[${index}]`));
  }
  if (typeof value === "object" && value !== null) {
    return Object.entries(value).flatMap(([key, item]) =>
      stringLeaves(item, `${path}.${key}`),
    );
  }
  return [];
}

// ── the matcher can fail ─────────────────────────────────────────────────────

describe("dialectHits (the planted cases that prove it bites)", () => {
  it.each([
    ["design-doc citation", "Balance split across the games (DESIGN.md §11.3)."],
    ["section reference", "Survived §5.4 contradiction detection."],
    ["task reference", "Typed on the wire by Task 12.2."],
    ["audit path", "See audits/audit-phase-19-triage.md for the recount."],
    ["undefined jargon", "A sentinel, not a down-is-good metric."],
    ["undefined jargon", "It is a bug detector, not a KPI."],
    ["undefined jargon", "The canary cell for this baseline."],
    ["undefined jargon", "Starved on this substrate."],
  ])("flags a %s", (name, planted) => {
    expect(dialectHits(planted)).toContain(name);
  });

  it("flags every class at once in a string that carries them all", () => {
    const planted =
      "The gate surface (DESIGN.md §11.3), re-anchored by Task 19.5; see " +
      "audits/audit-phase-19-triage.md — a sentinel, not a KPI.";
    expect(dialectHits(planted)).toEqual([
      "design-doc citation",
      "section reference",
      "task reference",
      "audit path",
      "undefined jargon",
    ]);
  });

  it("passes prose that says the same thing in plain English", () => {
    expect(
      dialectHits(
        "Whether evidence the engine hands the crew turns into an ejection — a " +
          "bug check rather than a quality score.",
      ),
    ).toEqual([]);
  });

  it("is stateless across repeated calls (no sticky lastIndex)", () => {
    const planted = "Task 19.5 re-anchored it.";
    expect(dialectHits(planted)).toEqual(dialectHits(planted));
  });
});

// ── leg 1: the copy values ───────────────────────────────────────────────────

describe("SPECTATOR_COPY", () => {
  const leaves = stringLeaves(SPECTATOR_COPY, "SPECTATOR_COPY");

  it("exports copy to check", () => {
    expect(leaves.length).toBeGreaterThan(20);
  });

  it("has no duplicate wording hiding under two keys", () => {
    const seen = new Map<string, string>();
    for (const leaf of leaves) {
      // Short fragments legitimately repeat (a shared column header, the two
      // halves of a sentence split around a <code>); only full sentences are
      // worth flagging as an accidental second home for the same words.
      if (leaf.text.length < 40) continue;
      const first = seen.get(leaf.text);
      expect(first, `${leaf.path} duplicates ${first ?? ""}`).toBeUndefined();
      seen.set(leaf.text, leaf.path);
    }
  });

  it.each(leaves.map((leaf) => [leaf.path, leaf.text]))(
    "%s carries no dialect",
    (_path, text) => {
      expect(dialectHits(text)).toEqual([]);
    },
  );

  it("keeps the derived strings clean too", () => {
    expect(dialectHits(setOptionLabel("9p2i"))).toEqual([]);
  });

  // A template still carries its words here, so the walk above already checked
  // it — but only FILLED does it read the way a viewer sees it. Filling every
  // template with a stand-in also proves none of them is missing a closing
  // brace, which would leave a literal `{` on screen.
  it("leaves every template clean once it is filled", () => {
    for (const leaf of leaves) {
      const names = [...leaf.text.matchAll(/\{(\w+)\}/g)].map((m) => m[1] ?? "");
      if (names.length === 0) continue;
      const values = Object.fromEntries(names.map((name) => [name, "7"]));
      const filled = fmt(leaf.text, values);
      expect(filled, leaf.path).not.toContain("{");
      expect(dialectHits(filled), leaf.path).toEqual([]);
    }
  });
});

describe("MAP_COPY", () => {
  it("carries the regroup note in plain words", () => {
    expect(MAP_COPY.regroupNote).toBe(
      "On this recording, whenever play resumes after a meeting, the survivors start from the meeting room with the bodies cleared, so the map jumps to where they stand on the next tick.",
    );
    expect(MAP_COPY.regroupNote).not.toMatch(/regroup/i);
  });
});

// ── the interpolation helper ─────────────────────────────────────────────────

describe("fmt", () => {
  it("fills every placeholder, including a repeated one", () => {
    expect(fmt("{a} / {b} · {a}", { a: "3", b: "9" })).toBe("3 / 9 · 3");
  });

  it("leaves a template with no placeholders alone", () => {
    expect(fmt("non-decisive", {})).toBe("non-decisive");
  });

  // The planted case for the runtime backstop: a value that never arrives must
  // raise, not render `{n}` at a viewer. (At a call site the compiler catches it
  // first — `SPECTATOR_COPY` is `as const`, so the placeholder names are part of
  // the template's type — but a template widened to `string` reaches here.)
  it("raises rather than rendering a placeholder it cannot fill", () => {
    const widened: string = "{count} games scored";
    expect(() => fmt(widened, {})).toThrow(/no value for \{count\}/);
  });
});

// ── leg 2: the component sources ─────────────────────────────────────────────

describe("the in-scope surfaces on disk", () => {
  it("strips comments without eating rendered strings", () => {
    const synthetic = [
      "// Provenance in a comment is fine: Task 19.5, audits/audit-x.md, DESIGN.md §11.3.",
      "/* Also fine in a block: a sentinel, not a KPI. */",
      "const url = { href: 'https://example.test/a//b' };",
      'const shown = "Browse by moment.";',
    ].join("\n");
    const stripped = stripComments(synthetic);
    expect(stripped).toContain("Browse by moment.");
    expect(stripped).toContain("https://example.test/a//b");
    expect(dialectHits(stripped)).toEqual([]);
  });

  it("catches dialect that survives the strip because it is rendered", () => {
    const synthetic = [
      "// A clean comment.",
      'const shown = "The gate surface (Task 10.4), re-anchored by 19.5.";',
    ].join("\n");
    expect(dialectHits(stripComments(synthetic))).toContain("task reference");
  });

  it("checks every in-scope surface — the allow-list is empty", () => {
    expect(DIALECT_ALLOW_LIST).toEqual([]);
    expect(CHECKED_SOURCES).toHaveLength(IN_SCOPE_SOURCES.length);
  });

  it.each(CHECKED_SOURCES.map((s) => [s.file, s.rendered]))(
    "%s renders no dialect",
    (file, rendered) => {
      const source = readFileSync(resolve(LIB_DIR, "../components", file), "utf8");
      const stripped = stripComments(source);
      // The strip is only trustworthy if it left the render behind.
      expect(stripped).toContain(rendered);
      expect(dialectHits(stripped)).toEqual([]);
    },
  );

  it("would catch a planted rendered citation in a real source", () => {
    const source = readFileSync(
      resolve(LIB_DIR, "../components/TournamentDashboard.tsx"),
      "utf8",
    );
    const planted = `${stripComments(source)}\nconst leak = "See DESIGN.md §11.3.";\n`;
    expect(dialectHits(planted)).toContain("design-doc citation");
  });
});

// ── the ownership invariant, on the surface that claims it ───────────────────
//
// `TournamentDashboard.tsx`'s header says the copy tree owns every prose string
// it renders. "No dialect" does not prove that — a perfectly plain literal typed
// straight into the JSX passes the leg above while breaking the claim. So the
// claim gets its own check: on that file, the props that CARRY copy must all be
// expressions, never quoted literals.
//
// Only that one file, plus the recorded-behavior group and the ejection tile of
// `PublicResults.tsx` (checked at the end of this section). The other eight keep prose inline by
// design (the contract scopes `TurnCard.tsx` to a single string, and the
// transport's button titles are not this task's), and none of them claims
// otherwise in its header.

// Every literal form JSX accepts for a prop: `x="…"`, `x='…'`, and the braced
// `x={"…"}` / `x={'…'}` / x={`…`}. Only a real expression passes.
const COPY_BEARING_PROP =
  /\b(?:label|title|hint|description|heading|unit|aria-label)\s*=\s*(?:["']|\{\s*["'`])/;

/**
 * Literal JSX text: what sits between a `>` and a closing `</`, containing no
 * braces.
 *
 * Two deliberate narrowings keep this honest without a JSX parser. Anchoring on
 * a CLOSING tag means TypeScript's own angle brackets (`Record<K, V>`, a
 * comparison) can never be mistaken for markup — they are never followed by
 * `</`. Excluding braces means every `{expression}` child drops out on its own,
 * with no brace-matching pass to get wrong.
 */
function literalJsxText(source: string): readonly string[] {
  return [...source.matchAll(/>([^<>{}]+)<\//g)]
    .map((match) => (match[1] ?? "").trim())
    .filter((text) => text !== "");
}

// Two alphabetic words in a row is the signature of PROSE. A bare identifier —
// `tournament-eval-report.json`, `scripts/run_tournament.py`, the paths this
// surface prints inside <code> — has no space in it and is not copy.
const PROSE_RUN = /[A-Za-z]{2,}\s+[A-Za-z]{2,}/;

function dashboardSource(): string {
  return stripComments(
    readFileSync(resolve(LIB_DIR, "../components/TournamentDashboard.tsx"), "utf8"),
  );
}

describe("the dashboard's copy-ownership claim", () => {
  it.each([
    ["double-quoted prop", '<StatTile label="Crew wins" value={x} />'],
    ["single-quoted prop", "<StatTile label='Crew wins' value={x} />"],
    ["braced string prop", '<MetricSection title={"Balance outcome"}>'],
    ["braced template prop", "<MetricSection title={`Balance outcome`}>"],
    ["aria-label", '<main aria-label="Tournament dashboard">'],
  ])("catches a %s (the planted cases)", (_name, planted) => {
    expect(COPY_BEARING_PROP.test(planted)).toBe(true);
  });

  it("passes the same props written as copy-tree expressions", () => {
    expect(
      COPY_BEARING_PROP.test("<StatTile label={DASHBOARD_COPY.balanceCrewWins} />"),
    ).toBe(false);
    expect(
      COPY_BEARING_PROP.test("<StatTile hint={fmt(DASHBOARD_COPY.x, { n })} />"),
    ).toBe(false);
  });

  it("catches a prose text node, and lets an identifier through", () => {
    expect(literalJsxText("<p>Crew wins</p>").some((t) => PROSE_RUN.test(t))).toBe(true);
    expect(
      literalJsxText("<p>{DASHBOARD_COPY.intro}</p>").some((t) => PROSE_RUN.test(t)),
    ).toBe(false);
    expect(
      literalJsxText("<code>tournament-eval-report.json</code>").some((t) =>
        PROSE_RUN.test(t),
      ),
    ).toBe(false);
    expect(
      literalJsxText('<p>{fmt(T, { a: "}" })}</p>').some((t) => PROSE_RUN.test(t)),
    ).toBe(false);
    // TypeScript's angle brackets are not markup and must not be read as text.
    expect(literalJsxText("const x: Record<ScoreBucket, string> = y;")).toEqual([]);
  });

  it("finds no literal copy-bearing prop in TournamentDashboard.tsx", () => {
    const offenders = dashboardSource()
      .split("\n")
      .map((line, index) => ({ line: line.trim(), number: index + 1 }))
      .filter((entry) => COPY_BEARING_PROP.test(entry.line))
      .map((entry) => `${entry.number}: ${entry.line}`);
    expect(offenders).toEqual([]);
  });

  it("finds no literal prose text node in TournamentDashboard.tsx", () => {
    const offenders = literalJsxText(dashboardSource()).filter((text) =>
      PROSE_RUN.test(text),
    );
    expect(offenders).toEqual([]);
  });
});

// The public results page's recorded-behavior group keeps every word in
// `PUBLIC_RESULTS_COPY`: its span (`recordedSettings` through `BehaviorIdentity`)
// carries no prose string literal and no literal prose text node. Class names
// are styling, not copy, so they are set aside first.
function behaviorSpan(source: string): string {
  const start = source.indexOf("export function recordedSettings(");
  const end = source.indexOf("function CaseCard(");
  if (start < 0 || end <= start) throw new Error("the recorded-behavior span moved");
  return source.slice(start, end).replace(/className="[^"]*"/g, "");
}

function proseLiterals(span: string): readonly string[] {
  const literals = [...span.matchAll(/"([^"\\\n]*)"|'([^'\\\n]*)'|`([^`\\]*)`/g)].map(
    (match) => match[1] ?? match[2] ?? match[3] ?? "",
  );
  return [...literals, ...literalJsxText(span)].filter((text) => PROSE_RUN.test(text));
}

describe("the public results card's copy-ownership claim", () => {
  const source = stripComments(
    readFileSync(resolve(LIB_DIR, "../components/PublicResults.tsx"), "utf8"),
  );

  it("renders no prose of its own in a recorded-behavior group", () => {
    const span = behaviorSpan(source);
    expect(span).toContain("COPY.adoptedLead");
    expect(proseLiterals(span)).toEqual([]);
  });

  it("catches a planted literal in the span (planted)", () => {
    const span = behaviorSpan(source);
    const literal = span.replace("COPY.factoryCustom", '"Custom agent factory"');
    expect(literal).not.toBe(span);
    expect(proseLiterals(literal)).toEqual(["Custom agent factory"]);
    const text = span.replace("{COPY.noRecordedSettings}", "No enabled experiments recorded");
    expect(text).not.toBe(span);
    expect(proseLiterals(text)).toEqual(["No enabled experiments recorded"]);
  });

  it("renders the ejection tile's heading and description from the copy", () => {
    const span = ejectionTileSpan(source);
    expect(span).toContain("COPY.ejectionsHeading");
    expect(span).toContain("COPY.ejectionsDescription");
    expect(proseLiterals(span)).toEqual([]);
  });

  it("catches the old heading typed back into the tile (planted)", () => {
    const span = ejectionTileSpan(source);
    const planted = span.replace("{COPY.ejectionsHeading}", "Correct ejections");
    expect(planted).not.toBe(span);
    expect(proseLiterals(planted)).toEqual(["Correct ejections"]);
  });
});

// The public results tab's ejection tile counts impostors among ejected players:
// a role read, reported beside the process figures and never called correct. Its
// heading describes its own number.

/** The tile that renders the impostor-ejection fraction, class names set aside. */
function ejectionTileSpan(source: string): string {
  const fraction = source.indexOf(
    "<Fraction n={results.impostor_ejections} d={results.ejections} />",
  );
  const start = source.lastIndexOf("<div", fraction);
  const end = source.indexOf("</div>", fraction);
  if (fraction < 0 || start < 0 || end <= fraction) throw new Error("the ejection tile moved");
  return source.slice(start, end).replace(/className="[^"]*"/g, "");
}

/** The path of every string leaf in `tree` that calls an ejection correct. */
function correctEjectionLeaves(tree: unknown, path: string): readonly string[] {
  return stringLeaves(tree, path)
    .filter((leaf) => /correct ejection/i.test(leaf.text))
    .map((leaf) => leaf.path);
}

describe("the public results tab's ejection heading", () => {
  it("says what the fraction counts, and calls no ejection correct", () => {
    expect(PUBLIC_RESULTS_COPY.ejectionsHeading).toBe("Ejected players who were impostors");
    expect(PUBLIC_RESULTS_COPY.ejectionsDescription).toBe(
      "Impostors / all ejected players across {meetings} resolved meetings. {innocent} innocent ejections; skips are excluded.",
    );
    expect(correctEjectionLeaves(PUBLIC_RESULTS_COPY, "PUBLIC_RESULTS_COPY")).toEqual([]);
  });

  it("catches the old heading, or an old sentence, restored as a copy value (planted)", () => {
    const heading = { ...PUBLIC_RESULTS_COPY, ejectionsHeading: "Correct ejections" };
    expect(correctEjectionLeaves(heading, "PUBLIC_RESULTS_COPY")).toEqual([
      "PUBLIC_RESULTS_COPY.ejectionsHeading",
    ]);
    const sentence = {
      ...PUBLIC_RESULTS_COPY,
      ejectionsDescription: "Correct ejections over all ejected players.",
    };
    expect(correctEjectionLeaves(sentence, "PUBLIC_RESULTS_COPY")).toEqual([
      "PUBLIC_RESULTS_COPY.ejectionsDescription",
    ]);
  });
});

// ── the header's and the tour's source link ──────────────────────────────────
//
// The header reads the name, the tagline and one link to the repository, and
// the guided tour's welcome step keeps the same link in plain words; the
// attribution line both used to carry is gone. Their words live in
// `HEADER_COPY`, so the attribution's words are refused anywhere in the copy
// tree, and the two places that typed them inline carry no prose of their own.

/**
 * The removed attribution line's words, refused anywhere a viewer reads copy.
 * "directed by" is bounded so the ballot label "Vote redirected by the meeting
 * rule" is not mistaken for it.
 */
const ATTRIBUTION_WORDS = /\bdirected by|Claude Code|Codex|AI-reviewed|ownership/i;

/** The path of every string leaf in `tree` that carries an attribution word. */
function attributionLeaves(tree: unknown, path: string): readonly string[] {
  return stringLeaves(tree, path)
    .filter((leaf) => ATTRIBUTION_WORDS.test(leaf.text))
    .map((leaf) => leaf.path);
}

/** Class names are styling, not copy, so a span sets them aside first. */
function bareSpan(span: string): string {
  return span.replace(/className="[^"]*"/g, "");
}

/**
 * The header's title block and the shell's `<header>` that mounts it (the
 * workspace's mode banner is a `<header>` too, so the shell's is found inside
 * `App`).
 */
function headerSpans(source: string): readonly [string, string] {
  const titleStart = source.indexOf("export function ShellTitle(");
  const titleEnd = source.indexOf("\n}\n", titleStart);
  const app = source.indexOf("export default function App(");
  const headerStart = source.indexOf("<header", app);
  const headerEnd = source.indexOf("</header>", headerStart);
  if (
    titleStart < 0 ||
    titleEnd <= titleStart ||
    app < 0 ||
    headerStart < 0 ||
    headerEnd <= headerStart
  ) {
    throw new Error("the header moved");
  }
  return [
    bareSpan(source.slice(titleStart, titleEnd)),
    bareSpan(source.slice(headerStart, headerEnd)),
  ];
}

/** The copy keys the title block reads, each as a `HEADER_COPY` read. */
const HEADER_READS: readonly (keyof typeof HEADER_COPY)[] = [
  "tagline",
  "sourceLinkText",
  "sourceUrl",
];

/** The `HEADER_COPY` reads missing from the title block; empty when it reads all three. */
function missingHeaderReads(title: string): readonly string[] {
  return HEADER_READS.filter((key) => !title.includes(`HEADER_COPY.${key}`));
}

/** The tour's welcome step, and the one link inside it. */
function welcomeSpans(source: string): readonly [string, string] {
  const stepStart = source.indexOf("export const STEPS");
  const stepEnd = source.indexOf("title: TOUR_COPY.perspectiveTitle", stepStart);
  const step = source.slice(stepStart, stepEnd);
  const linkStart = step.indexOf("<a ");
  const linkEnd = step.indexOf("</a>", linkStart);
  if (stepStart < 0 || stepEnd <= stepStart || linkStart < 0 || linkEnd <= linkStart) {
    throw new Error("the welcome step moved");
  }
  return [bareSpan(step), bareSpan(step.slice(linkStart, linkEnd + "</a>".length))];
}

/**
 * What the header's two spans carry beyond copy reads: each prose literal,
 * named by the span that types it, then the first attribution word either span
 * says. Empty when every word is a copy read.
 */
function headerSpanProblems(title: string, header: string): readonly string[] {
  const problems = [
    ...proseLiterals(title).map((text) => `the title block types ${text}`),
    ...proseLiterals(header).map((text) => `the shell header types ${text}`),
  ];
  const hit = ATTRIBUTION_WORDS.exec(title + header);
  if (hit !== null) problems.push(`the header says ${hit[0]}`);
  return problems;
}

/**
 * What the welcome step of a tour source carries beyond copy reads: each prose
 * literal its link types, then the first attribution word anywhere in the step,
 * inside the link or outside it. Empty when the step says none. The helper cuts
 * both spans from the source itself, so no caller can hand it one span in the
 * other's place.
 */
function welcomeSpanProblems(source: string): readonly string[] {
  const [step, link] = welcomeSpans(source);
  const problems = proseLiterals(link).map((text) => `the link types ${text}`);
  const hit = ATTRIBUTION_WORDS.exec(step);
  if (hit !== null) problems.push(`the step says ${hit[0]}`);
  return problems;
}

/**
 * The attribution strip's two lines, as a planted case types them beside the
 * title block (class names set aside): the first is a prose text node, the
 * second runs into its link, so only the word check names it.
 */
const OLD_STRIP_PROSE = "<p>Recorded AI social deduction · directed by Daniel Keinan</p>";
const OLD_STRIP_LINE =
  '<p>Code and supporting material by Claude Code and Codex · AI-reviewed · <a href="https://github.com/dkdan10/AiLibi" target="_blank" rel="noreferrer">Source & ownership</a></p>';

describe("the header's and the tour's source link", () => {
  const app = stripComments(readFileSync(resolve(LIB_DIR, "../App.tsx"), "utf8"));
  const tour = stripComments(
    readFileSync(resolve(LIB_DIR, "../components/GuidedTour.tsx"), "utf8"),
  );

  it("holds the tagline, the two link texts and the repository", () => {
    expect(HEADER_COPY).toEqual({
      tagline: "Recorded AI social deduction",
      sourceLinkText: "GitHub",
      tourSourceLinkText: "Read the source on GitHub.",
      sourceUrl: "https://github.com/dkdan10/AiLibi",
    });
  });

  it("carries no attribution word anywhere in SPECTATOR_COPY", () => {
    expect(stringLeaves(SPECTATOR_COPY, "SPECTATOR_COPY").length).toBeGreaterThan(20);
    expect(attributionLeaves(SPECTATOR_COPY, "SPECTATOR_COPY")).toEqual([]);
  });

  it.each([
    "directed by Daniel Keinan",
    "code by Claude Code",
    "and Codex",
    "AI-reviewed",
    "Source & ownership",
  ])("catches %s restored as a copy value, naming the key (planted)", (words) => {
    const planted = {
      ...SPECTATOR_COPY,
      header: { ...HEADER_COPY, tagline: `${HEADER_COPY.tagline} · ${words}` },
    };
    expect(attributionLeaves(planted, "SPECTATOR_COPY")).toEqual([
      "SPECTATOR_COPY.header.tagline",
    ]);
  });

  it("walks the whole tree, not only the header group (planted)", () => {
    const planted = {
      ...SPECTATOR_COPY,
      dashboard: { ...DASHBOARD_COPY, intro: "Directed by Daniel Keinan." },
    };
    expect(attributionLeaves(planted, "SPECTATOR_COPY")).toEqual([
      "SPECTATOR_COPY.dashboard.intro",
    ]);
    // A list leaf is named by its index, so a word inside one points at its slot.
    expect(attributionLeaves({ lines: ["GitHub", "AI-reviewed"] }, "TREE")).toEqual([
      "TREE.lines[1]",
    ]);
  });

  it("lets a ballot that was redirected by the meeting rule through", () => {
    expect(attributionLeaves({ ballot: "Vote redirected by the meeting rule" }, "TREE")).toEqual(
      [],
    );
  });

  it("renders the header's words from the copy", () => {
    const [title, header] = headerSpans(app);
    expect(header).toContain("<ShellTitle />");
    expect(missingHeaderReads(title)).toEqual([]);
    expect(headerSpanProblems(title, header)).toEqual([]);
  });

  it.each([
    ["tagline", "{HEADER_COPY.tagline}", "Recorded AI social deduction"],
    ["sourceLinkText", "{HEADER_COPY.sourceLinkText}", "GitHub"],
    ["sourceUrl", "{HEADER_COPY.sourceUrl}", '"https://github.com/dkdan10/AiLibi"'],
  ])("names the %s read when the title types it as a literal (planted)", (key, read, literal) => {
    const [title] = headerSpans(app);
    const planted = title.replace(read, literal);
    expect(planted).not.toBe(title);
    expect(missingHeaderReads(planted)).toEqual([key]);
  });

  it("catches the old strip typed back into the title block (planted)", () => {
    const [title, header] = headerSpans(app);
    const literal = title.replace(
      "{HEADER_COPY.tagline}",
      "Recorded AI social deduction · directed by Daniel Keinan",
    );
    expect(literal).not.toBe(title);
    expect(headerSpanProblems(literal, header)).toEqual([
      "the title block types Recorded AI social deduction · directed by Daniel Keinan",
      "the header says directed by",
    ]);
    const link = title.replace("{HEADER_COPY.sourceLinkText}", "Source & ownership");
    expect(link).not.toBe(title);
    expect(headerSpanProblems(link, header)).toEqual(["the header says ownership"]);
  });

  it("catches the old strip typed into the shell header beside the title block (planted)", () => {
    const [title, header] = headerSpans(app);
    const strip = header.replace(
      "<ShellTitle />",
      `<ShellTitle />${OLD_STRIP_PROSE}${OLD_STRIP_LINE}`,
    );
    expect(strip).not.toBe(header);
    expect(headerSpanProblems(title, strip)).toEqual([
      "the shell header types Recorded AI social deduction · directed by Daniel Keinan",
      "the header says directed by",
    ]);
    const line = header.replace("<ShellTitle />", `<ShellTitle />${OLD_STRIP_LINE}`);
    expect(line).not.toBe(header);
    expect(headerSpanProblems(title, line)).toEqual(["the header says Claude Code"]);
    const prose = header.replace("<ShellTitle />", "<ShellTitle /><p>Watch saved games</p>");
    expect(prose).not.toBe(header);
    expect(headerSpanProblems(title, prose)).toEqual([
      "the shell header types Watch saved games",
    ]);
  });

  it("renders the welcome step's one link from the copy", () => {
    const [step, link] = welcomeSpans(tour);
    expect(step.split("<a ")).toHaveLength(2);
    expect(link).toContain("HEADER_COPY.sourceUrl");
    expect(link).toContain("HEADER_COPY.tourSourceLinkText");
    expect(welcomeSpanProblems(tour)).toEqual([]);
  });

  it("catches the old link text, or the old sentence, typed back into the step (planted)", () => {
    const literal = tour.replace(
      "{HEADER_COPY.tourSourceLinkText}",
      "Read the source and ownership case study.",
    );
    expect(literal).not.toBe(tour);
    expect(welcomeSpanProblems(literal)).toEqual([
      "the link types Read the source and ownership case study.",
      "the step says ownership",
    ]);
    // The old sentence sits outside the link, so only the step-wide word check reaches it.
    const sentence = tour.replace(
      "not making live model calls.",
      "not making live model calls. Daniel Keinan directs the project; Claude Code and Codex agents write code and supporting material, with separate AI review.",
    );
    expect(sentence).not.toBe(tour);
    expect(welcomeSpanProblems(sentence)).toEqual(["the step says Claude Code"]);
  });
});

// ── the game-shape profile's words ───────────────────────────────────────────

/** A digit in a profile string that is not a filled-in fact: a threshold. */
function thresholdHits(text: string): readonly string[] {
  const unfilled = text.replace(/\{\w+\}/g, "");
  return /\d/.test(unfilled) ? [unfilled] : [];
}

describe("the game-shape profile's copy", () => {
  const leaves = stringLeaves(PROFILE_COPY, "PROFILE_COPY");

  it("states no threshold in any shelf, chip, facet or tripwire string", () => {
    expect(leaves.length).toBeGreaterThan(40);
    for (const leaf of leaves) {
      expect(thresholdHits(leaf.text), leaf.path).toEqual([]);
      expect(dialectHits(leaf.text), leaf.path).toEqual([]);
    }
  });

  it("a description carrying a threshold fails (planted)", () => {
    expect(thresholdHits("A stretch of 20 ticks passed with no kill.")).not.toEqual([]);
    expect(thresholdHits("A meeting settled by at most 1 ballot.")).not.toEqual([]);
    expect(thresholdHits("{count} games")).toEqual([]);
  });

  it("names every shelf the profile can serve, in plain words", () => {
    expect(Object.keys(PROFILE_COPY.shelves)).toEqual([
      "the_reporter_saw_it_happen",
      "double_kill",
      "slow_burn",
      "two_kills_after_one_regroup",
      "a_close_call",
      "suspicion_moved",
      "a_third_round",
      "caught_venting",
      "one_line_two_readings",
      "struck_after_the_regroup",
      "one_vote_ejection",
      "nobody_voted_out",
      "down_to_the_wire",
      "runaway",
      "decided_at_a_meeting",
      "decided_without_proof_right",
      "decided_without_proof_wrong",
    ]);
  });

  it("says the wrong half is the voters' held lines pointing the wrong way, as the game", () => {
    const wrong = PROFILE_COPY.shelves.decided_without_proof_wrong.description;
    expect(wrong).toContain("cited lines they held and it pointed the wrong way");
    expect(wrong).toContain("A wrong call on believable evidence is part of the game");
    expect(PROFILE_COPY.shelves.decided_without_proof_right.description).toContain(
      "the table was right",
    );
    expect(PROFILE_COPY.pair.note).toContain("always show together");
  });

  it("names no score, rank or order anywhere a viewer reads the profile or the browser", () => {
    expect(rankingLeaves(PROFILE_COPY, "PROFILE_COPY")).toEqual([]);
    expect(stringLeaves(PICKER_COPY, "PICKER_COPY").length).toBeGreaterThan(5);
    expect(rankingLeaves(PICKER_COPY, "PICKER_COPY")).toEqual([]);
    expect(DASHBOARD_COPY.momentsDescription).toContain("nothing is averaged");
  });

  it("catches a picker leaf that ranks the games (planted)", () => {
    const planted = { ...PICKER_COPY, replaysIntro: "Recorded games for this set, ranked by drama." };
    expect(rankingLeaves(planted, "PICKER_COPY")).toEqual(["PICKER_COPY.replaysIntro"]);
    const scored = { ...PROFILE_COPY, allGames: "Top games" };
    expect(rankingLeaves(scored, "PROFILE_COPY")).toEqual(["PROFILE_COPY.allGames"]);
  });
});

/** The path of every string leaf in `tree` that scores, ranks or orders a game. */
function rankingLeaves(tree: unknown, path: string): readonly string[] {
  return stringLeaves(tree, path)
    .filter((leaf) => /\bscor|\brank|\bbest\b|\btop\b/i.test(leaf.text))
    .map((leaf) => leaf.path);
}

// ── set ids in words ─────────────────────────────────────────────────────────

describe("expandSetName", () => {
  it("expands the two served sets", () => {
    expect(expandSetName("9p2i")).toBe("9 players, 2 impostors");
    expect(expandSetName("4p1i")).toBe("4 players, 1 impostor");
  });

  it("falls back to the raw id for a set it does not know", () => {
    expect(expandSetName("ml_corpus_v3")).toBe("ml_corpus_v3");
  });

  it("names a set in words with its id after, and an unknown id exactly once", () => {
    expect(setOptionLabel("9p2i")).toBe("9 players, 2 impostors (9p2i)");
    expect(setOptionLabel("4p1i")).toBe("4 players, 1 impostor (4p1i)");
    expect(setOptionLabel("ml_corpus_v3")).toBe("ml_corpus_v3");
  });
});

// ── the ballot correctness gate ──────────────────────────────────────────────

describe("showsBallotCorrectness", () => {
  it.each([
    [true, true, true],
    [true, false, false],
    [false, true, false],
    [false, false, false],
  ])(
    "omniscient=%s reveal=%s → %s",
    (omniscient, revealOutcome, expected) => {
      expect(showsBallotCorrectness(omniscient, revealOutcome)).toBe(expected);
    },
  );

  it("never shows the mark while outcomes are hidden, in either perspective", () => {
    expect(showsBallotCorrectness(true, false)).toBe(false);
    expect(showsBallotCorrectness(false, false)).toBe(false);
  });
});

// ── what the rewritten copy must and must not say ────────────────────────────

describe("the copy's substance", () => {
  it("says what vote correctness counts, and drops the structural-1.0 claim", () => {
    const description = DASHBOARD_COPY.voteCorrectnessDescription;
    expect(description).toContain("impostor ejections");
    expect(description).toMatch(/contradiction/i);
    expect(description).toMatch(/kill-witness/i);
    expect(description).not.toMatch(/pinned|by construction|structurally/i);
    expect(DASHBOARD_COPY.voteCorrectnessRateCaveatTitle).not.toMatch(
      /pinned|by construction|structurally|1\.0/,
    );
  });

  it("says what a value below the ceiling means, without naming a cause", () => {
    const title = DASHBOARD_COPY.voteCorrectnessRateCaveatTitle;
    expect(title).toMatch(/below/i);
    expect(title).not.toMatch(/recording bug|detector bug/i);
  });

  it("claims no completeness for the replays the picker lists", () => {
    expect(PICKER_COPY.replaysIntro).not.toMatch(/every recorded replay/i);
    expect(PICKER_COPY.replaysIntro).not.toMatch(/\bevery\b|\ball\b/i);
  });

  it("keeps the agent-clock note free of measurements and ids", () => {
    // The corroborating counts belong in the component comment and in this
    // test, never on screen: 111,283/111,283 memory sighting lines match world
    // truth at Δ=−1 against 51.8% at Δ=0, and the meeting header matches this
    // readout in 771/771 calls. A note that quoted them would age the moment
    // the engine re-stamps its packets.
    for (const text of [
      TRANSPORT_COPY.agentClockNote,
      TRANSPORT_COPY.agentClockTitle,
    ]) {
      expect(text).not.toMatch(/%/); // no rates
      expect(text).not.toMatch(/\d{2,}/); // no counts
      expect(text).not.toMatch(/,\d/); // no grouped counts
      expect(dialectHits(text)).toEqual([]);
    }
    // The offset itself is the point, so the tooltip states it and the short
    // note beside the readout stays digit-free.
    expect(TRANSPORT_COPY.agentClockNote).not.toMatch(/\d/);
    expect(TRANSPORT_COPY.agentClockTitle).toMatch(/N−1/);
    expect(TRANSPORT_COPY.agentClockTitle).toMatch(/meeting header/i);
  });

  it("spells out the missed-skip partition instead of abbreviating it", () => {
    const hint = fmt(DASHBOARD_COPY.conversionMissedSkipsHint, {
      impostorVoters: "91",
      invalidTargets: "1",
      crewDeclined: "87",
    });
    expect(hint).toBe("impostor voters 91 · invalid targets 1 · crew declined 87");
    expect(hint).not.toMatch(/imp-voter|inversion/);
  });

  it("explains the gate cells instead of naming them", () => {
    // The review's complaint was that "supplied-channel conversion" and its
    // neighbour meant nothing to a visitor. The label survives; the description
    // beside it now says what the cell counts, in words.
    const description = DASHBOARD_COPY.gateDescription;
    expect(description).toMatch(/witnessed vent/i);
    expect(description).toMatch(/whereabouts lie/i);
    expect(description).toMatch(/alibi lies/i);
    expect(dialectHits(description)).toEqual([]);
  });

  it("writes the gate tooltips itself rather than echoing the report's notes", () => {
    // `supplied_channel_conversion.note` / `.legacy_note` are maintainer notes
    // full of task ids and audit paths; rendering them as tooltips put that
    // dialect on screen through the back door.
    for (const text of [
      DASHBOARD_COPY.gateSuppliedCaveatTitle,
      DASHBOARD_COPY.gateGenuineCaveatTitle,
    ]) {
      expect(dialectHits(text)).toEqual([]);
      expect(text).not.toMatch(/successor|legacy_note|compute_/);
    }
  });
});

// ── retired wording: the scan ────────────────────────────────────────────────
//
// The visitor-wording answers of 2026-10-11 retire a set of words from the
// viewer. Each row below names a source those answers rewrote and one retired
// literal. The source is read off disk with comments stripped, so provenance in a
// comment stays allowed while a rendered word, tooltip or accessible name does
// not; the copy tree is walked for the same literals, because a word moved into
// `SPECTATOR_COPY` is rendered just the same.

type Retired = string | RegExp;

/** Whether `text` carries a retired literal (a string matches exactly, case and all). */
function carries(text: string, retired: Retired): boolean {
  return typeof retired === "string" ? text.includes(retired) : retired.test(text);
}

/** The retired literals a source still carries once its comments are stripped. */
function retiredIn(source: string, retired: readonly Retired[]): readonly string[] {
  const stripped = stripComments(source);
  return retired.filter((literal) => carries(stripped, literal)).map(String);
}

// Word-bounded, so the identifiers `inFog`, `fogAgentId` and `lensIsSelf` are code
// rather than copy.
const FOG = /\bfog\b/i;
const LENS = /\blens\b/i;

/**
 * Each rewritten source (from `frontend/src`), a fragment it still renders
 * after the strip, and the literals it no longer carries.
 */
const RETIRED_IN_SOURCES: readonly {
  readonly file: string;
  readonly kept: string;
  readonly retired: readonly Retired[];
}[] = [
  { file: "../index.html", kept: "<title>", retired: ["Replay Viewer"] },
  {
    file: "App.tsx",
    kept: "Show finale",
    retired: [
      "Highlights",
      "Results & cases",
      /\bseed \$\{/,
      /\}p · /,
      "mtg",
      /\bimp [{$]/,
      "As-agent",
      FOG,
      "Next beat",
      "edge-triggered",
      "two-truth grammar",
      "WINNER_REASON_LABEL",
      "reached parity",
      "sabotage unresolved",
      "engine-adjusted",
      "✓",
      "✗",
    ],
  },
  {
    file: "components/GuidedTour.tsx",
    kept: "Start exploring",
    retired: [
      /Results (?:&amp;|&) cases/,
      "As-agent",
      FOG,
      "Perspective switcher",
      "</strong> hero",
      "at parity",
      "unresolved sabotage",
    ],
  },
  {
    file: "components/ReplayPicker.tsx",
    kept: "Clear filters",
    retired: [
      "picked by hand",
      /\bseed \{/,
      "Loading ${set}",
      "Failed to load replays",
      "unknown error",
      "No replays found",
      "configured replay directory",
      "Couldn’t load the set list",
      "Failed to load replay:",
    ],
  },
  {
    file: "components/ReplayFilters.tsx",
    kept: "Any winner",
    retired: ["Show outcome filters", 'label="Set"'],
  },
  {
    file: "components/HighlightCard.tsx",
    kept: "Outcome hidden",
    retired: [/\bseed \{/, "Open replay seed", "Tick limit"],
  },
  {
    file: "components/MapToolbar.tsx",
    kept: "= impostor",
    retired: ["canonical_1", "-vent ring", "corridors", "As-agent", FOG, "simulate"],
  },
  {
    file: "components/EventTicker.tsx",
    kept: "Nothing has happened yet.",
    retired: ["· fog", "fog admits"],
  },
  { file: "components/BodyMarker.tsx", kept: "victimLabel", retired: ["† ${"] },
  { file: "components/RoomRect.tsx", kept: "room.name", retired: ['"FOG"'] },
  {
    file: "components/SabotageOverlay.tsx",
    kept: "hudText",
    retired: ["SABOTAGE · ALARM", "LIGHTS · DARK", "· t-"],
  },
  {
    file: "components/MindInspector.tsx",
    kept: "role hidden",
    retired: ["Show what they saw", "Seeing what they saw", FOG, "(firewall)"],
  },
  {
    file: "components/BallotCard.tsx",
    kept: "no rationale recorded",
    retired: ["perspective to inspect"],
  },
  {
    file: "components/EvidencePanel.tsx",
    kept: "Check the source",
    retired: ["Switch to {observer}"],
  },
  {
    file: "components/MemoryPanel.tsx",
    kept: "Raw rendered memory (sent to LLM)",
    retired: [FOG, LENS],
  },
  {
    file: "components/TournamentDashboard.tsx",
    kept: "TournamentDashboardView",
    retired: ["costMeanHint"],
  },
  { file: "components/CalibrationCurve.tsx", kept: "bins populated", retired: [/\bECE\b/] },
];

/** The same retired words, refused anywhere in the copy tree. */
const RETIRED_IN_COPY: readonly Retired[] = [
  "Replay Viewer",
  "Highlights",
  "Results & cases",
  "picked by hand",
  "Show outcome filters",
  "As-agent",
  FOG,
  LENS,
  "Show what they saw",
  "Next beat",
  "edge-triggered",
  "two-truth grammar",
  "reached parity",
  "sabotage unresolved",
  "engine-adjusted",
  "the vote was",
  "0.20/game",
  /\bECE\b/,
  "in seed order",
  "Nothing here ranks",
  "tripwire keeps",
  "this build serves",
  "unknown error",
  "configured replay directory",
  "canonical_1",
];

/** The path and literal of every string leaf in `tree` that carries a retired word. */
function retiredLeaves(tree: unknown, path: string): readonly string[] {
  return stringLeaves(tree, path).flatMap((leaf) =>
    RETIRED_IN_COPY.filter((literal) => carries(leaf.text, literal)).map(
      (literal) => `${leaf.path}: ${String(literal)}`,
    ),
  );
}

function sourceText(file: string): string {
  return readFileSync(resolve(LIB_DIR, "..", file), "utf8");
}

describe("the retired wording (the scan)", () => {
  it("catches a retired literal in rendered code and ignores it in a comment (planted)", () => {
    expect(retiredIn('const label = "As-agent";', ["As-agent"])).toEqual(["As-agent"]);
    expect(
      retiredIn('// The As-agent switcher used to live here.\nconst label = "See as";', [
        "As-agent",
      ]),
    ).toEqual([]);
    expect(retiredIn("<button>Exit fog</button>", [FOG])).toEqual([String(FOG)]);
    expect(retiredIn("{/* fog of war */}<span>Map</span>", [FOG])).toEqual([]);
    expect(retiredIn("const inFog = fogAgentId !== null && lensIsSelf;", [FOG, LENS])).toEqual(
      [],
    );
  });

  it.each(
    RETIRED_IN_SOURCES.flatMap((row) =>
      row.retired.map((literal) => [row.file, String(literal), row.kept, literal] as const),
    ),
  )("%s no longer carries %s", (file, _name, kept, literal) => {
    const source = sourceText(file);
    // The strip is only trustworthy if it left the render behind.
    expect(stripComments(source)).toContain(kept);
    expect(retiredIn(source, [literal])).toEqual([]);
  });

  it("finds none of them anywhere in SPECTATOR_COPY", () => {
    expect(stringLeaves(SPECTATOR_COPY, "SPECTATOR_COPY").length).toBeGreaterThan(20);
    expect(retiredLeaves(SPECTATOR_COPY, "SPECTATOR_COPY")).toEqual([]);
  });

  it("names the leaf when a retired word returns to the copy (planted)", () => {
    const planted = {
      ...SPECTATOR_COPY,
      picker: { ...PICKER_COPY, highlightsIntro: "Games grouped by moment, in seed order." },
    };
    expect(retiredLeaves(planted, "SPECTATOR_COPY")).toEqual([
      "SPECTATOR_COPY.picker.highlightsIntro: in seed order",
    ]);
    expect(retiredLeaves({ chip: "As p-3 · fog" }, "TREE")).toEqual([`TREE.chip: ${String(FOG)}`]);
  });
});

// ── the tab title and the link preview ──────────────────────────────────────

const INDEX_HTML = resolve(LIB_DIR, "../../index.html");

/** One element of a page's head, named by its tag and the attribute that tells it apart. */
function headElement(tag: string): string {
  const name = /^<(\w+)/.exec(tag)?.[1] ?? "";
  const key = /\b(charset|name|property)="?([^"\s/>]*)/.exec(tag);
  return key === null ? name : `${name} ${key[1] ?? ""}=${key[2] ?? ""}`;
}

/** The head's elements, the only ones the page may carry. */
const HEAD_ELEMENTS: readonly string[] = [
  "meta charset=UTF-8",
  "meta name=viewport",
  "title",
  "meta name=description",
  "meta property=og:title",
];

/** What differs between a page's head and the site copy; empty when they agree. */
function headProblems(html: string): readonly string[] {
  const head = /<head>([\s\S]*?)<\/head>/.exec(html)?.[1];
  if (head === undefined) return ["the page has no head"];
  const problems: string[] = [];
  const title = /<title>([^<]*)<\/title>/.exec(head)?.[1];
  if (title !== SITE_COPY.title) problems.push(`the title reads ${String(title)}`);
  const description = /<meta name="description" content="([^"]*)"/.exec(head)?.[1];
  if (description !== SITE_COPY.title) {
    problems.push(`the description reads ${String(description)}`);
  }
  const preview = /<meta property="og:title" content="([^"]*)"/.exec(head)?.[1];
  if (preview !== SITE_COPY.title) problems.push(`the preview title reads ${String(preview)}`);
  const elements = [...head.matchAll(/<\w+\b[^>]*>/g)].map((match) => headElement(match[0]));
  for (const element of elements) {
    if (!HEAD_ELEMENTS.includes(element)) problems.push(`the head also carries ${element}`);
  }
  return problems;
}

describe("the tab title and the link preview", () => {
  const html = readFileSync(INDEX_HTML, "utf8");

  it("carry the name and the tagline, and nothing else enters the head", () => {
    expect(SITE_COPY.title).toBe("AiLibi — Recorded AI social deduction");
    expect(SITE_COPY.title).toBe(`AiLibi — ${HEADER_COPY.tagline}`);
    expect(headProblems(html)).toEqual([]);
  });

  it("name the old title, a dropped tag or a new one (planted)", () => {
    const old = html.replace(
      `<title>${SITE_COPY.title}</title>`,
      "<title>AiLibi — Replay Viewer</title>",
    );
    expect(old).not.toBe(html);
    expect(headProblems(old)).toEqual(["the title reads AiLibi — Replay Viewer"]);
    const dropped = html.replace(/\s*<meta name="description"[^>]*>/, "");
    expect(dropped).not.toBe(html);
    expect(headProblems(dropped)).toEqual(["the description reads undefined"]);
    const image = html.replace(
      "</head>",
      '  <meta property="og:image" content="hero.png" />\n  </head>',
    );
    expect(image).not.toBe(html);
    expect(headProblems(image)).toEqual(["the head also carries meta property=og:image"]);
  });
});

// ── the navigation, the tour and the workspace's names ──────────────────────

describe("the navigation and the tour", () => {
  it("names the tabs after the pages they open", () => {
    expect(NAV_COPY).toEqual({
      replays: "Replays",
      highlights: "Moments",
      tournament: "Results",
      tourTitle: "A short tour of how to watch a recorded game",
    });
  });

  it("states the game's endings in the ending words and names one player's view", () => {
    expect(TOUR_COPY.perspectiveTitle).toBe("What one player could see");
    expect(TOUR_COPY.rules).toContain("voting out every impostor");
    expect(TOUR_COPY.rules).toContain("match the crew in number or a sabotage runs out");
    expect(TOUR_COPY.rules).not.toMatch(/parity|unresolved/);
    expect(TOUR_COPY.perspectiveBody).toContain("“See as”");
  });
});

/** The ten rooms of the canonical map, which a one-player view must not name. */
const ROOM_NAMES: readonly string[] = [
  "Cafeteria",
  "Upper Hall",
  "Admin",
  "East Hallway",
  "Engineering",
  "Reactor",
  "Storage",
  "West Hallway",
  "MedBay",
  "Labs",
];

/** What a one-player HUD line reveals that the view hides; empty when it hides both. */
function oneViewHudProblems(text: string): readonly string[] {
  const problems: string[] = [];
  if (/\d/.test(text)) problems.push("a countdown");
  for (const room of ROOM_NAMES) {
    if (text.toLowerCase().includes(room.toLowerCase())) problems.push(`the room ${room}`);
  }
  return problems;
}

describe("the workspace's names", () => {
  it("names a game by its number, with the seed in a tooltip", () => {
    expect(gameName(19)).toBe("Game 19");
    expect(gameSeedTitle(19)).toBe("Recorded from random seed 19");
    expect(openGameLabel(19)).toBe("Open game 19");
    expect(GAME_COPY.name).toBe("Game {n}");
  });

  it("spells out the counts, one and many", () => {
    expect(playerCount(9)).toBe("9 players");
    expect(playerCount(1)).toBe("1 player");
    expect(meetingCount(3)).toBe("3 meetings");
    expect(meetingCount(1)).toBe("1 meeting");
    expect(meetingCount(0)).toBe("0 meetings");
    expect(fmt(GAME_COPY.rosterCrew, { count: "7" })).toBe("crew 7");
    expect(fmt(GAME_COPY.rosterImpostors, { count: "2" })).toBe("impostors 2");
  });

  it("gives one tag per ending, from the copy", () => {
    expect(outcomeTag("CREWMATES", "completed")).toBe("Crew win");
    expect(outcomeTag("IMPOSTORS", undefined)).toBe("Impostor win");
    expect(outcomeTag(null, "aborted")).toBe("Aborted");
    expect(outcomeTag(null, "tick_limited")).toBe("Stopped at the tick limit");
    expect(outcomeTag(null, "unfinished")).toBe("Unfinished");
    expect(outcomeTag(null, undefined)).toBe("Unfinished");
    expect(outcomeTag(null, null)).toBe("Unfinished");
    // A recorded winner wins over the stop classification beside it.
    expect(outcomeTag("IMPOSTORS", "tick_limited")).toBe("Impostor win");
    expect([
      OUTCOME_COPY.crewWin,
      OUTCOME_COPY.impostorWin,
      OUTCOME_COPY.aborted,
      OUTCOME_COPY.tickLimited,
      OUTCOME_COPY.unfinished,
    ]).toEqual(["Crew win", "Impostor win", "Aborted", "Stopped at the tick limit", "Unfinished"]);
  });

  it("words a recorded ending as the cards do, and an unknown one not at all", () => {
    expect(endingPhrase("CREWMATE_EJECT")).toBe(PROFILE_COPY.revealFacets.endings.CREWMATE_EJECT);
    expect(endingPhrase("IMPOSTOR_SABOTAGE")).toBe("a sabotage ran out");
    expect(endingPhrase("all_tasks_complete")).toBeNull();
    // Inherited keys are not endings.
    expect(endingPhrase("constructor")).toBeNull();
    expect(endingPhrase("toString")).toBeNull();
  });

  it("says who killed a lone body", () => {
    expect(killedByLabel("p-4")).toBe("killed by p-4");
    expect(MAP_COPY.chip).toBe("Map");
    expect(MAP_COPY.unseenRoom).toBe("Unseen");
  });

  it("counts a sabotage down in the all-roles view", () => {
    expect(sabotageHud("reactor", 5, true)).toBe("Reactor meltdown in 5 ticks");
    expect(sabotageHud("reactor", 1, true)).toBe("Reactor meltdown in 1 tick");
    expect(sabotageHud("lights", 12, true)).toBe("Lights out, 12 ticks left");
    expect(sabotageHud("lights", 1, true)).toBe("Lights out, 1 tick left");
  });

  it("names neither the room nor the countdown in one player's view", () => {
    for (const kind of ["reactor", "lights"] as const) {
      const line = sabotageHud(kind, 5, false);
      expect(line, kind).not.toBe("");
      expect(oneViewHudProblems(line), kind).toEqual([]);
    }
    expect(sabotageHud("reactor", 5, false)).toBe("Sabotage alarm");
    expect(sabotageHud("lights", 5, false)).toBe("Lights out");
  });

  it("catches the all-roles line in one player's view, whatever its case (planted)", () => {
    expect(oneViewHudProblems(sabotageHud("reactor", 5, true))).toEqual([
      "a countdown",
      "the room Reactor",
    ]);
    expect(oneViewHudProblems("REACTOR · ALARM")).toEqual(["the room Reactor"]);
    expect(oneViewHudProblems("Sabotage alarm")).toEqual([]);
  });

  it("names one player's view one way", () => {
    expect(fmt(PERSPECTIVE_COPY.watchingAs, { agent: "p-3" })).toBe("Watching as p-3");
    expect(fmt(PERSPECTIVE_COPY.seeAs, { agent: "p-1" })).toBe("See as p-1");
    expect(fmt(PERSPECTIVE_COPY.bannerLabel, { view: "Watching as p-3" })).toBe(
      "Perspective: Watching as p-3",
    );
    expect(TRANSPORT_COPY.nextKeyMoment).toBe("Next key moment");
    expect(TRANSPORT_COPY.resumeTitle).toBe("Resume playback past this meeting");
  });
});

// ── the replay browser's notes ───────────────────────────────────────────────

describe("the replay browser's notes", () => {
  it("say what the browser shows, in plain words", () => {
    expect(PICKER_COPY.featuredHeading).toBe("Featured");
    expect(PICKER_COPY.revealOutcomes).toBe("Reveal outcomes");
    expect(PICKER_COPY.replaysIntro).toBe("Recorded games for this set. Open one to watch it.");
    expect(PICKER_COPY.highlightsIntro).toBe(
      "Games grouped by the moments they hold, each list in game order.",
    );
    expect(PROFILE_COPY.allGamesNote).toBe(
      "Every game listed here, in game order, including games kept off the shelves.",
    );
    expect(PICKER_COPY.emptySet).toBe("No recorded games are available for this set.");
    expect(fmt(PICKER_COPY.loadingSet, { set: setOptionLabel("9p2i") })).toBe(
      "Loading 9 players, 2 impostors (9p2i)…",
    );
    expect(PICKER_COPY.loadingReplays).toBe("Loading recorded games…");
    expect(PICKER_COPY.replaysLoadError).toBe("The recorded games could not be loaded:");
    expect(PICKER_COPY.unknownError).toBe("No reason was given.");
  });
});

// ── the local dashboard's leftovers ──────────────────────────────────────────

describe("the local dashboard's leftovers", () => {
  it("drops the cost target and spells out the calibration error", () => {
    expect(Object.keys(DASHBOARD_COPY)).not.toContain("costMeanHint");
    expect(fmt(DASHBOARD_COPY.calibrationError, { value: "0.123" })).toBe(
      "Expected calibration error 0.123",
    );
    expect(DASHBOARD_COPY.calibrationErrorTitle).toBe("lower is better");
    expect(DASHBOARD_COPY.calibrationLowPower).toBe(
      "Too few to trust the calibration — read the expected calibration error with care.",
    );
  });
});
