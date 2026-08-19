// The dialect gate for the spectator surface, plus the copy helpers it guards.
//
// Two independent legs, because "no internal dialect reaches a viewer" can fail
// in two different places:
//
//   1. VALUES — every string in `SPECTATOR_COPY` is clean.
//   2. DISK   — the eight component sources, read off disk with comments
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
  PICKER_COPY,
  RUBRIC_SPOKES,
  SPECTATOR_COPY,
  TRANSPORT_COPY,
  dialectHits,
  expandSetName,
  fmt,
  rubricLegendLine,
  rubricSpokeTitle,
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
    { file: "TournamentDashboard.tsx", rendered: "Tournament dashboard" },
    { file: "MeetingView.tsx", rendered: "Resolution" },
    { file: "BallotCard.tsx", rendered: "no rationale recorded" },
    { file: "ReplayPicker.tsx", rendered: "Clear filters" },
    { file: "HighlightCard.tsx", rendered: "Not scored" },
    { file: "ReplayControls.tsx", rendered: "Next key moment" },
    { file: "MetricCaveat.tsx", rendered: "note" },
    { file: "TurnCard.tsx", rendered: "accuses" },
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

  it.each(leaves.map((leaf) => [leaf.path, leaf.text]))(
    "%s carries no dialect",
    (_path, text) => {
      expect(dialectHits(text)).toEqual([]);
    },
  );

  it("keeps the derived strings clean too", () => {
    expect(dialectHits(rubricLegendLine())).toEqual([]);
    expect(dialectHits(setOptionLabel("9p2i"))).toEqual([]);
    for (const spoke of RUBRIC_SPOKES) {
      expect(dialectHits(rubricSpokeTitle(spoke, 0.62))).toEqual([]);
    }
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
      'const shown = "Ordered by the rubric.";',
    ].join("\n");
    const stripped = stripComments(synthetic);
    expect(stripped).toContain("Ordered by the rubric.");
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

// ── the rubric legend, on both tabs and on the bars ──────────────────────────

describe("the rubric legend table", () => {
  it("names all four spokes and the field each one reads", () => {
    expect(RUBRIC_SPOKES).toEqual([
      { key: "R1", word: "deduction", field: "r1_decisive" },
      { key: "R2", word: "deception", field: "r2_deception" },
      { key: "R3", word: "suspicion arcs", field: "r3_arcs" },
      { key: "R7", word: "legibility", field: "r7_legible" },
    ]);
  });

  it("builds the header legend from that table, so the two cannot drift", () => {
    expect(rubricLegendLine()).toBe(
      "Score bars: deduction (R1), deception (R2), suspicion arcs (R3), legibility (R7).",
    );
    for (const spoke of RUBRIC_SPOKES) {
      expect(rubricLegendLine()).toContain(spoke.key);
      expect(rubricLegendLine()).toContain(spoke.word);
    }
  });

  it("puts a spoke's meaning in its hover text, not only its key", () => {
    expect(rubricSpokeTitle({ key: "R3", word: "suspicion arcs", field: "r3_arcs" }, 0.5)).toBe(
      "R3 suspicion arcs: 0.50 on a 0–1 scale",
    );
  });
});

// ── set ids in words ─────────────────────────────────────────────────────────

describe("expandSetName", () => {
  it("expands the two served sets", () => {
    expect(expandSetName("9p2i")).toBe("9 players, 2 impostors");
    expect(expandSetName("4p1i")).toBe("4 players, 1 impostor");
  });

  it("falls back to the raw id for a set it does not know", () => {
    expect(expandSetName("ml_corpus_v3")).toBe("ml_corpus_v3");
  });

  it("labels a control with id + words, and an unknown id exactly once", () => {
    expect(setOptionLabel("9p2i")).toBe("9p2i — 9 players, 2 impostors");
    expect(setOptionLabel("4p1i")).toBe("4p1i — 4 players, 1 impostor");
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

  it("stops claiming the picker lists every recorded replay", () => {
    expect(PICKER_COPY.replaysIntro).not.toMatch(/every recorded replay/i);
    expect(PICKER_COPY.replaysIntro).toMatch(/serves/i);
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
