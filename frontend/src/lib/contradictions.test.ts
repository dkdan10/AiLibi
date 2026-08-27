// The contradiction event-id vocabulary, censused against the bytes the API
// actually serves.
//
// THE INVARIANT. Every endpoint of every served contradiction resolves onto
// exactly one rendered line. A flag names its two halves by event id
// (`turn:<turn_id>:<segment>:<index>`), and `TurnCard` re-mints those ids to
// decide which line wears the badge — so an id the cards cannot mint is a flag
// that renders nowhere. `retiredTwoSegmentRule` below is the NEGATIVE CONTROL:
// the rule the cards shipped before a roll-call self-placement got its own
// segment, which addressed every observation as `:obs:`. Both run the same walk
// over both committed sample sets, and the control has to fail it (31 of 328
// endpoints unresolved vs 0) — a zero-unresolved assertion is true by
// construction once the shipped rule mints the ids it also reads, so without a
// rule that fails it the census would be prose.
//
// THE FIXTURE. `contradictions.fixture.json` dumps, per served meeting, each
// contradiction's `category` and two endpoint ids, and each turn's id with its
// observation discriminants and claim count in served order — everything the id
// vocabulary is a function of, and nothing else. It is committed rather than
// derived here because the replay JSONL rows carry raw meeting artifacts:
// `MeetingView.contradictions` exists only after the Python loader's engine
// re-walk and the detector pass it drives, and re-deriving that in the frontend
// is precisely what the `lib/` split exists to stop. `corpusSha256` binds each
// set to the replay bytes it came from; `corpusDigest` recomputes it from
// `replays/samples/<set>` on every run, so a re-recorded corpus fails this suite
// until the fixture is regenerated instead of leaving it green over a detached
// snapshot. Regenerate from the repo root with:
//
//   uv run python - <<'PY'
//   import hashlib
//   import json
//   from pathlib import Path
//
//   from api.replay_loader import ReplayLoader
//
//
//   def corpus_sha256(replay_dir: Path) -> str:
//       outer = hashlib.sha256()
//       for path in sorted(replay_dir.glob("*.jsonl"), key=lambda p: p.name):
//           inner = hashlib.sha256(path.read_bytes()).hexdigest()
//           outer.update(f"{path.name}\n{inner}\n".encode())
//       return outer.hexdigest()
//
//
//   sets = []
//   for name in ("9p2i", "4p1i"):
//       replay_dir = Path("replays/samples") / name
//       loader = ReplayLoader(replay_dir)
//       games = []
//       for meta in loader.list_replays():
//           meetings = []
//           for m in loader.load_replay(meta.game_id).meetings:
//               meetings.append(
//                   {
//                       "meeting_id": m.meeting_id,
//                       "contradictions": [
//                           {
//                               "contradiction_id": c.contradiction_id,
//                               "category": c.category,
//                               "event_a_id": c.event_a_id,
//                               "event_b_id": c.event_b_id,
//                           }
//                           for c in m.contradictions
//                       ],
//                       "turns": [
//                           {
//                               "turn_id": t.turn_id,
//                               "observations": [o.type for o in t.observations],
//                               "claims": len(t.claims),
//                           }
//                           for t in m.turns
//                       ],
//                   }
//               )
//           games.append({"game_id": meta.game_id, "meetings": meetings})
//       sets.append(
//           {"name": name, "corpus_sha256": corpus_sha256(replay_dir), "games": games}
//       )
//   Path("frontend/src/lib/contradictions.fixture.json").write_text(
//       json.dumps({"sets": sets}, separators=(",", ":")) + "\n"
//   )
//   PY
//
// Read off disk with `readFileSync` rather than a JSON `import` (the pattern
// `src/tokens.test.ts` set): `tsconfig.json` has `resolveJsonModule`, so an
// import would push a large inferred literal type through `tsc --noEmit` for no
// benefit. The reader below is explicitly typed so the strict flags stay honest.

import { createHash } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import type { ContradictionView, ObservationClaimView, TurnView } from "../types/api";
import {
  OBSERVATION_EVENT_SEGMENTS,
  observationEventId,
  turnClaimEventId,
} from "./contradictions";

const LIB_DIR = dirname(fileURLToPath(import.meta.url));
const FIXTURE_PATH = resolve(LIB_DIR, "contradictions.fixture.json");
// `frontend/src/lib` → the repo root, where the replay corpus lives.
const SAMPLES_DIR = resolve(LIB_DIR, "../../../replays/samples");

/**
 * A digest of one sample set's committed replay bytes: sha256 over
 * `<filename>\n<sha256 of that file>\n` for every `*.jsonl`, name-sorted. The
 * generator in this file's header computes it the same way, so a corpus that
 * moves and a fixture that does not can no longer both be green.
 */
function corpusDigest(setName: string): string {
  const dir = join(SAMPLES_DIR, setName);
  const outer = createHash("sha256");
  for (const name of readdirSync(dir)
    .filter((entry) => entry.endsWith(".jsonl"))
    .sort()) {
    const inner = createHash("sha256").update(readFileSync(join(dir, name))).digest("hex");
    outer.update(`${name}\n${inner}\n`);
  }
  return outer.digest("hex");
}

// ── the fixture reader ───────────────────────────────────────────────────────

type EvidenceCategory = ContradictionView["category"];

interface FixtureFlag {
  readonly contradictionId: string;
  readonly category: EvidenceCategory;
  readonly endpoints: readonly [string, string];
}

interface FixtureTurn {
  readonly turnId: string;
  /** Observation discriminants in served order — what picks each id's segment. */
  readonly observations: readonly ObservationClaimView["type"][];
  readonly claims: number;
}

interface FixtureMeeting {
  readonly meetingId: string;
  readonly flags: readonly FixtureFlag[];
  readonly turns: readonly FixtureTurn[];
}

interface FixtureGame {
  readonly gameId: string;
  readonly meetings: readonly FixtureMeeting[];
}

interface FixtureSet {
  readonly name: string;
  /** `corpusDigest(name)` at the moment the dump was generated. */
  readonly corpusSha256: string;
  readonly games: readonly FixtureGame[];
}

function asRecord(value: unknown, where: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`${where}: expected an object`);
  }
  return value as Record<string, unknown>;
}

function asArray(value: unknown, where: string): readonly unknown[] {
  if (!Array.isArray(value)) {
    throw new Error(`${where}: expected an array`);
  }
  return value as readonly unknown[];
}

function asString(value: unknown, where: string): string {
  if (typeof value !== "string") {
    throw new Error(`${where}: expected a string`);
  }
  return value;
}

function asNumber(value: unknown, where: string): number {
  if (typeof value !== "number") {
    throw new Error(`${where}: expected a number`);
  }
  return value;
}

/**
 * One stand-in per observation discriminant.
 *
 * The census only needs the discriminant — it is the whole input to the segment
 * choice — but the shipped helper takes a real union member, so building real
 * ones keeps the walk free of casts. Typed as a `Record` over the union so a
 * seventh observation type is a compile error here rather than a fixture row the
 * reader quietly drops; the payload fields are filler and never read.
 */
const OBSERVATION_BY_TYPE: Record<ObservationClaimView["type"], ObservationClaimView> = {
  saw_player: { type: "saw_player", tick: 0, subject: "p-0", room: "room", co_present: [] },
  completed_task: { type: "completed_task", tick: 0, task_id: "task", room: "room" },
  found_body: { type: "found_body", tick: 0, body_of: "p-0", room: "room" },
  saw_vent: { type: "saw_vent", tick: 0, subject: "p-0", room: "room" },
  whereabouts: { type: "whereabouts", tick: 0, room: "room" },
  saw_move: { type: "saw_move", tick: 0, subject: "p-0", from_room: "a", to_room: "b" },
};

const CATEGORIES: readonly EvidenceCategory[] = ["role_proof", "cross_statement", "weak_signal"];

function readCategory(value: unknown, where: string): EvidenceCategory {
  const raw = asString(value, where);
  const found = CATEGORIES.find((candidate) => candidate === raw);
  if (found === undefined) {
    throw new Error(`${where}: the served payload carries an unknown category "${raw}"`);
  }
  return found;
}

function readObservationType(value: unknown, where: string): ObservationClaimView["type"] {
  const raw = asString(value, where);
  const found = Object.values(OBSERVATION_BY_TYPE).find((candidate) => candidate.type === raw);
  if (found === undefined) {
    throw new Error(`${where}: the served payload carries an unknown observation type "${raw}"`);
  }
  return found.type;
}

function readFixture(): readonly FixtureSet[] {
  const root = asRecord(JSON.parse(readFileSync(FIXTURE_PATH, "utf8")), "fixture");
  return asArray(root["sets"], "fixture.sets").map((rawSet, s) => {
    const setRow = asRecord(rawSet, `sets[${s}]`);
    const name = asString(setRow["name"], `sets[${s}].name`);
    return {
      name,
      corpusSha256: asString(setRow["corpus_sha256"], `${name}.corpus_sha256`),
      games: asArray(setRow["games"], `${name}.games`).map((rawGame, g) => {
        const gameRow = asRecord(rawGame, `${name}.games[${g}]`);
        const gameId = asString(gameRow["game_id"], `${name}.games[${g}].game_id`);
        return {
          gameId,
          meetings: asArray(gameRow["meetings"], `${gameId}.meetings`).map((rawMeeting, m) => {
            const meetingRow = asRecord(rawMeeting, `${gameId}.meetings[${m}]`);
            const meetingId = asString(meetingRow["meeting_id"], `${gameId}.meetings[${m}].id`);
            return {
              meetingId,
              flags: asArray(meetingRow["contradictions"], `${meetingId}.contradictions`).map(
                (rawFlag, f) => {
                  const where = `${meetingId}.contradictions[${f}]`;
                  const flagRow = asRecord(rawFlag, where);
                  return {
                    contradictionId: asString(flagRow["contradiction_id"], `${where}.id`),
                    category: readCategory(flagRow["category"], `${where}.category`),
                    endpoints: [
                      asString(flagRow["event_a_id"], `${where}.event_a_id`),
                      asString(flagRow["event_b_id"], `${where}.event_b_id`),
                    ] as [string, string],
                  };
                },
              ),
              turns: asArray(meetingRow["turns"], `${meetingId}.turns`).map((rawTurn, t) => {
                const where = `${meetingId}.turns[${t}]`;
                const turnRow = asRecord(rawTurn, where);
                return {
                  turnId: asString(turnRow["turn_id"], `${where}.turn_id`),
                  observations: asArray(turnRow["observations"], `${where}.observations`).map(
                    (type, o) => readObservationType(type, `${where}.observations[${o}]`),
                  ),
                  claims: asNumber(turnRow["claims"], `${where}.claims`),
                };
              }),
            };
          }),
        };
      }),
    };
  });
}

const FIXTURE = readFixture();

function set(name: string): FixtureSet {
  const found = FIXTURE.find((candidate) => candidate.name === name);
  if (found === undefined) {
    throw new Error(`the fixture carries no set named "${name}"`);
  }
  return found;
}

// ── the two rules ────────────────────────────────────────────────────────────

/**
 * The rendered id vocabulary of one turn: every event id the card would mint,
 * and therefore every id a flag can land on.
 */
type IdRule = (turn: FixtureTurn) => string[];

/**
 * The shipped rule, driven through the module's own exported helpers — so this
 * census walks the code the cards run, not a restatement of it.
 *
 * The helpers take real DTO values; the fixture carries only the fields the ids
 * are a function of, so the rest is filler (see `OBSERVATION_BY_TYPE`).
 */
const shippedRule: IdRule = (turn) => {
  const asTurnView: TurnView = {
    turn_id: turn.turnId,
    turn_index: 0,
    speaker: "p-0",
    turn_kind: "opening",
    reply_to: null,
    observations: [],
    claims: [],
    free_text: "",
    annotations: [],
    fabricated_opening: false,
  };
  return [
    ...turn.observations.map((type, index) =>
      observationEventId(asTurnView, OBSERVATION_BY_TYPE[type], index),
    ),
    ...Array.from({ length: turn.claims }, (_, index) => turnClaimEventId(asTurnView, index)),
  ];
};

/**
 * The rule the cards shipped before this task: every observation addressed as
 * `:obs:`, whatever it is. Kept verbatim so the census below can prove it fails
 * the gate the shipped rule passes — a roll-call self-placement is minted
 * `:whereabouts:` by the backend, so under this rule its flag lands on no line.
 */
const retiredTwoSegmentRule: IdRule = (turn) => [
  ...turn.observations.map((_, index) => `turn:${turn.turnId}:obs:${index}`),
  ...Array.from({ length: turn.claims }, (_, index) => `turn:${turn.turnId}:claim:${index}`),
];

// ── the walk ─────────────────────────────────────────────────────────────────

interface Walk {
  meetings: number;
  flags: number;
  endpoints: number;
  /** Endpoints that landed on no rendered line at all. */
  unresolved: number;
  /** Endpoints claimed by more than one rendered line. */
  ambiguous: number;
  unresolvedByCategory: Record<EvidenceCategory, number>;
  unresolvedBySet: Record<string, number>;
  /** Flags with exactly one unresolved endpoint — the half-linked class. */
  halfLinkedFlags: number;
  /** Flags with BOTH endpoints unresolved. */
  unlinkedFlags: number;
  /** `<gameId>|<turnId>` → the flag ids that would render on that turn. */
  flagsByTurn: Map<string, Set<string>>;
}

function walk(sets: readonly FixtureSet[], rule: IdRule): Walk {
  const result: Walk = {
    meetings: 0,
    flags: 0,
    endpoints: 0,
    unresolved: 0,
    ambiguous: 0,
    unresolvedByCategory: { role_proof: 0, cross_statement: 0, weak_signal: 0 },
    unresolvedBySet: {},
    halfLinkedFlags: 0,
    unlinkedFlags: 0,
    flagsByTurn: new Map(),
  };
  for (const fixtureSet of sets) {
    result.unresolvedBySet[fixtureSet.name] ??= 0;
    for (const game of fixtureSet.games) {
      for (const meeting of game.meetings) {
        result.meetings += 1;
        // The rendered vocabulary of the whole meeting: every id any card on
        // screen would mint, mapped back to the line that minted it.
        const lines = new Map<string, string[]>();
        for (const turn of meeting.turns) {
          for (const eventId of rule(turn)) {
            const owners = lines.get(eventId);
            if (owners === undefined) {
              lines.set(eventId, [turn.turnId]);
            } else {
              owners.push(turn.turnId);
            }
          }
        }
        for (const flag of meeting.flags) {
          result.flags += 1;
          let missing = 0;
          for (const endpoint of flag.endpoints) {
            result.endpoints += 1;
            const owners = lines.get(endpoint) ?? [];
            if (owners.length === 0) {
              missing += 1;
              result.unresolved += 1;
              result.unresolvedByCategory[flag.category] += 1;
              result.unresolvedBySet[fixtureSet.name] =
                (result.unresolvedBySet[fixtureSet.name] ?? 0) + 1;
              continue;
            }
            if (owners.length > 1) {
              result.ambiguous += 1;
            }
            for (const turnId of owners) {
              const key = `${game.gameId}|${turnId}`;
              const rendered = result.flagsByTurn.get(key);
              if (rendered === undefined) {
                result.flagsByTurn.set(key, new Set([flag.contradictionId]));
              } else {
                rendered.add(flag.contradictionId);
              }
            }
          }
          if (missing === 1) {
            result.halfLinkedFlags += 1;
          } else if (missing === 2) {
            result.unlinkedFlags += 1;
          }
        }
      }
    }
  }
  return result;
}

/** The turns that render at least one flag under `reference` and none under `candidate`. */
function turnsThatLostEveryFlag(reference: Walk, candidate: Walk): string[] {
  const lost: string[] = [];
  for (const key of reference.flagsByTurn.keys()) {
    if (!candidate.flagsByTurn.has(key)) {
      lost.push(key.split("|")[1] ?? key);
    }
  }
  return lost.sort();
}

/** The segment of an event id, read without consulting the list under test. */
function endpointSegment(eventId: string): string | null {
  const match = /^turn:(?:.+):([a-z_]+):\d+$/.exec(eventId);
  return match ? match[1]! : null;
}

// ── the census, both rules, both committed sets ──────────────────────────────

describe("the contradiction event-id vocabulary over the committed served payloads", () => {
  it.each(["9p2i", "4p1i"])("%s: the dump still matches the committed corpus", (name) => {
    // Without this the suite would keep passing over a detached snapshot after a
    // re-record replaced `replays/samples/`, censusing bytes nobody serves. The
    // digest folds in every replay's filename AND bytes, so an added, removed or
    // rewritten replay all fail here until the fixture is regenerated.
    expect(corpusDigest(name)).toBe(set(name).corpusSha256);
    expect(set(name).games).toHaveLength(
      readdirSync(join(SAMPLES_DIR, name)).filter((entry) => entry.endsWith(".jsonl")).length,
    );
  });

  it("every served endpoint segment is one the module knows", () => {
    // A fifth observation type minted with its own segment fails HERE, naming
    // the segment, rather than half-linking its flags in silence.
    const observed = new Set<string>();
    for (const fixtureSet of FIXTURE) {
      for (const game of fixtureSet.games) {
        for (const meeting of game.meetings) {
          for (const flag of meeting.flags) {
            for (const endpoint of flag.endpoints) {
              const segment = endpointSegment(endpoint);
              if (segment === null) {
                throw new Error(`endpoint "${endpoint}" is not a turn event id`);
              }
              observed.add(segment);
            }
          }
        }
      }
    }
    const unknown = [...observed].filter(
      (segment) => !OBSERVATION_EVENT_SEGMENTS.some((known) => known === segment),
    );
    expect(unknown).toEqual([]);
    // …and the corpus exercises all three, so the membership check above is not
    // passing over a vocabulary the served bytes never reach.
    expect([...observed].sort()).toEqual([...OBSERVATION_EVENT_SEGMENTS].sort());
  });

  it("the shipped rule lands every endpoint on exactly one rendered line", () => {
    expect(FIXTURE.flatMap((fixtureSet) => fixtureSet.games)).toHaveLength(100);
    const shipped = walk(FIXTURE, shippedRule);
    expect({
      meetings: shipped.meetings,
      flags: shipped.flags,
      endpoints: shipped.endpoints,
      unresolved: shipped.unresolved,
      ambiguous: shipped.ambiguous,
      halfLinkedFlags: shipped.halfLinkedFlags,
      unlinkedFlags: shipped.unlinkedFlags,
    }).toEqual({
      meetings: 192,
      flags: 164,
      endpoints: 328,
      unresolved: 0,
      ambiguous: 0,
      halfLinkedFlags: 0,
      unlinkedFlags: 0,
    });
    // The two sets, stated separately: the 9p2i share is what the finding
    // measured, and 4p1i proves the walk is not reading one set twice.
    expect(walk([set("9p2i")], shippedRule).flags).toBe(144);
    expect(walk([set("4p1i")], shippedRule).flags).toBe(20);
  });

  it("the retired two-segment rule fails the same walk", () => {
    const shipped = walk(FIXTURE, shippedRule);
    const retired = walk(FIXTURE, retiredTwoSegmentRule);
    expect({
      endpoints: retired.endpoints,
      unresolved: retired.unresolved,
      unresolvedBySet: retired.unresolvedBySet,
      unresolvedByCategory: retired.unresolvedByCategory,
      // Every loss is HALF a flag: no flag in the corpus carries a roll-call
      // placement on both ends, so none disappears entirely — the badge lands on
      // one line and not the other.
      halfLinkedFlags: retired.halfLinkedFlags,
      unlinkedFlags: retired.unlinkedFlags,
    }).toEqual({
      endpoints: 328,
      unresolved: 31,
      unresolvedBySet: { "9p2i": 31, "4p1i": 0 },
      unresolvedByCategory: { role_proof: 0, cross_statement: 2, weak_signal: 29 },
      halfLinkedFlags: 31,
      unlinkedFlags: 0,
    });

    // Seven turns are the whole loss made visible: the flag pointing at them was
    // their ONLY one, so under the retired rule they render with no badge at all.
    expect(turnsThatLostEveryFlag(shipped, retired)).toEqual([
      "headless-seed-1:meeting-0:turn-4",
      "headless-seed-1:meeting-0:turn-6",
      "headless-seed-32:meeting-0:turn-3",
      "headless-seed-33:meeting-1:turn-3",
      "headless-seed-36:meeting-2:turn-0",
      "headless-seed-44:meeting-1:turn-0",
      "headless-seed-46:meeting-3:turn-0",
    ]);
  });
});
