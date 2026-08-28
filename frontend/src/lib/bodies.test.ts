// The map body layer, pinned against the bytes the API actually serves.
//
// THE INVARIANT. On every frame the Omniscient layer draws exactly the bodies
// the engine still has on the floor — the served `TickView.bodies` — each with
// `killedBy` read off its served row and `isDiscovered` from the
// forward-accumulated `report_body` set. `retiredAccumulateRule` below is the
// NEGATIVE CONTROL: a derivation that accumulates `kill` events instead of
// reading the served rows. Both run the same census on both committed sample
// sets, and the control has to fail it (0 phantom frames vs 668 of 1,217 on
// `9p2i`) — a zero-phantom assertion nothing can fail would be prose, since the
// shipped rule satisfies it by construction.
//
// Hand-built frames follow for the cases the corpus does not exercise: a
// reported body that survives its own meeting, a body nobody reports, a served
// attribution that disagrees with the kill event, and the As-agent firewall.
//
// THE FIXTURE. `bodies.fixture.json` dumps the served `TickView.bodies` + the
// `kill` / `report_body` events for every frame of both sets. It is committed
// rather than derived here because the replay JSONL rows are ACTION-only:
// `tick.bodies` exists only after the Python loader's engine re-walk, and
// re-deriving engine state in the frontend is precisely what `./bodies.ts`
// exists to stop. `corpusSha256` binds each set to the replay bytes it came
// from; `corpusDigest` recomputes it from `replays/samples/<set>` on every run,
// so a re-recorded corpus fails this suite until the fixture is regenerated
// instead of leaving it green over a detached snapshot. Regenerate from the
// repo root with:
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
//           frames = []
//           for t in loader.load_replay(meta.game_id).ticks:
//               frame: dict[str, object] = {"tick": t.tick}
//               if t.bodies:
//                   frame["bodies"] = [
//                       {
//                           "victim_id": b.victim_id,
//                           "room_id": b.room_id,
//                           "killed_by": b.killed_by,
//                       }
//                       for b in t.bodies
//                   ]
//               events = [
//                   e.model_dump(mode="json")
//                   for e in t.events
//                   if e.type in ("kill", "report_body")
//               ]
//               if events:
//                   frame["events"] = events
//               frames.append(frame)
//           games.append({"game_id": meta.game_id, "frames": frames})
//       sets.append(
//           {"name": name, "corpus_sha256": corpus_sha256(replay_dir), "games": games}
//       )
//   Path("frontend/src/lib/bodies.fixture.json").write_text(
//       json.dumps({"sets": sets}, separators=(",", ":")) + "\n"
//   )
//   PY
//
// Read off disk with `readFileSync` rather than a JSON `import` (the pattern
// `src/tokens.test.ts` set): `tsconfig.json` has `resolveJsonModule`, so an
// import would push a 170 KB inferred literal type through `tsc --noEmit` for no
// benefit. The reader below is explicitly typed so the strict flags stay honest.

import { createHash } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import type { AgentVisibilityView, TickEventView } from "../types/api";
import {
  type BodySpec,
  type BodyTickSlice,
  NO_BODIES,
  bodiesForTick,
  bodyStatesByTick,
  visibleBodiesForTick,
} from "./bodies";

// Mirrors `BodyMarker.BODY_CAP`. Not imported: that module pulls Pixi and the
// Vite `?raw` SVG set at module scope, which this node-environment runner cannot
// load — the same import wall that hid the defect above.
const BODY_CAP = 3;

const LIB_DIR = dirname(fileURLToPath(import.meta.url));
const FIXTURE_PATH = resolve(LIB_DIR, "bodies.fixture.json");
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

interface FixtureFrame extends BodyTickSlice {
  /** The engine tick number (the loader's synthetic pre-game frame is -1). */
  readonly tick: number;
}

interface FixtureGame {
  readonly gameId: string;
  readonly frames: readonly FixtureFrame[];
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

function readEvent(raw: unknown, where: string): TickEventView {
  const row = asRecord(raw, where);
  const type = asString(row["type"], `${where}.type`);
  if (type === "kill") {
    return {
      type: "kill",
      tick: asNumber(row["tick"], `${where}.tick`),
      killer_id: asString(row["killer_id"], `${where}.killer_id`),
      victim_id: asString(row["victim_id"], `${where}.victim_id`),
      room_id: asString(row["room_id"], `${where}.room_id`),
    };
  }
  if (type === "report_body") {
    return {
      type: "report_body",
      tick: asNumber(row["tick"], `${where}.tick`),
      reporter_id: asString(row["reporter_id"], `${where}.reporter_id`),
      body_of: asString(row["body_of"], `${where}.body_of`),
      room_id: asString(row["room_id"], `${where}.room_id`),
    };
  }
  throw new Error(`${where}: the dump carries kill / report_body only, got "${type}"`);
}

function readFrame(raw: unknown, where: string): FixtureFrame {
  const row = asRecord(raw, where);
  const bodiesRaw = row["bodies"] === undefined ? [] : asArray(row["bodies"], `${where}.bodies`);
  const eventsRaw = row["events"] === undefined ? [] : asArray(row["events"], `${where}.events`);
  return {
    tick: asNumber(row["tick"], `${where}.tick`),
    bodies: bodiesRaw.map((body, i) => {
      const cell = asRecord(body, `${where}.bodies[${i}]`);
      return {
        victim_id: asString(cell["victim_id"], `${where}.bodies[${i}].victim_id`),
        room_id: asString(cell["room_id"], `${where}.bodies[${i}].room_id`),
        killed_by: asString(cell["killed_by"], `${where}.bodies[${i}].killed_by`),
      };
    }),
    events: eventsRaw.map((event, i) => readEvent(event, `${where}.events[${i}]`)),
  };
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
          frames: asArray(gameRow["frames"], `${gameId}.frames`).map((frame, f) =>
            readFrame(frame, `${gameId}.frames[${f}]`),
          ),
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

// ── the perturbation leg: the rule this task retired ─────────────────────────

/**
 * The body layer exactly as `MapView.tsx` derived it before this task: kill
 * events accumulated forward and never removed, `report_body` only flipping a
 * flag, the killer re-derived from the kill event. Kept verbatim so the census
 * below can prove it fails the gate the shipped rule passes.
 */
function retiredAccumulateRule(ticks: readonly BodyTickSlice[]): BodySpec[][] {
  const result: BodySpec[][] = new Array<BodySpec[]>(ticks.length);
  const killRoomByVictim = new Map<string, string>();
  const killerByVictim = new Map<string, string>();
  const discovered = new Set<string>();
  let current: BodySpec[] = [];
  for (const [t, tick] of ticks.entries()) {
    let changed = false;
    for (const event of tick.events) {
      if (event.type === "kill") {
        killRoomByVictim.set(event.victim_id, event.room_id);
        killerByVictim.set(event.victim_id, event.killer_id);
        changed = true;
      } else if (event.type === "report_body" && !discovered.has(event.body_of)) {
        discovered.add(event.body_of);
        changed = true;
      }
    }
    if (changed) {
      current = [...killRoomByVictim.entries()].map(([victimId, roomId]) => ({
        victimId,
        roomId,
        isDiscovered: discovered.has(victimId),
        killedBy: killerByVictim.get(victimId) ?? null,
      }));
    }
    result[t] = current;
  }
  return result;
}

// ── the walk ─────────────────────────────────────────────────────────────────

type Derivation = (ticks: readonly BodyTickSlice[]) => BodySpec[][];

interface Census {
  games: number;
  frames: number;
  /** Frames drawing at least one body the engine no longer has on the floor. */
  phantomFrames: number;
  /** Frames omitting a body the engine DOES have on the floor. */
  missingFrames: number;
  phantomBodies: number;
  gamesWithPhantom: number;
  /** Frames whose per-room body counts differ from the served per-room counts. */
  roomCountMismatchFrames: number;
  /** Frames where a room exceeds BODY_CAP while no served room does. */
  capOverflowFrames: number;
  /** Frames rendering at least one body with the discovered treatment. */
  discoveredFrames: number;
  /** Discovered bodies drawn on a LATER frame than their own report frame. */
  discoveredAfterReportFrame: number;
  /**
   * Bodies whose derived `killedBy` differs from the served `killed_by`, over
   * the bodies that ARE served (a phantom has no served row to compare with).
   * The committed sets never diverge, so the planted case further down is what
   * proves the field is read rather than re-derived.
   */
  attributionMismatches: number;
}

function countByRoom(rooms: readonly string[]): Map<string, number> {
  const counts = new Map<string, number>();
  for (const room of rooms) {
    counts.set(room, (counts.get(room) ?? 0) + 1);
  }
  return counts;
}

function sameCounts(a: Map<string, number>, b: Map<string, number>): boolean {
  if (a.size !== b.size) return false;
  for (const [room, n] of a) {
    if (b.get(room) !== n) return false;
  }
  return true;
}

function census(games: readonly FixtureGame[], derive: Derivation): Census {
  const total: Census = {
    games: 0,
    frames: 0,
    phantomFrames: 0,
    missingFrames: 0,
    phantomBodies: 0,
    gamesWithPhantom: 0,
    roomCountMismatchFrames: 0,
    capOverflowFrames: 0,
    discoveredFrames: 0,
    discoveredAfterReportFrame: 0,
    attributionMismatches: 0,
  };
  for (const game of games) {
    total.games += 1;
    const derived = derive(game.frames);
    let gamePhantoms = 0;
    for (const [i, frame] of game.frames.entries()) {
      total.frames += 1;
      const specs = derived[i] ?? [];
      const served = new Map(frame.bodies.map((body) => [body.victim_id, body]));
      const reportedHere = new Set(
        frame.events.filter((e) => e.type === "report_body").map((e) => e.body_of),
      );

      const phantoms = specs.filter((spec) => !served.has(spec.victimId));
      if (phantoms.length > 0) {
        total.phantomFrames += 1;
        total.phantomBodies += phantoms.length;
        gamePhantoms += phantoms.length;
      }
      const drawn = new Set(specs.map((spec) => spec.victimId));
      if (frame.bodies.some((body) => !drawn.has(body.victim_id))) {
        total.missingFrames += 1;
      }

      const derivedRooms = countByRoom(specs.map((spec) => spec.roomId));
      const servedRooms = countByRoom(frame.bodies.map((body) => body.room_id));
      if (!sameCounts(derivedRooms, servedRooms)) {
        total.roomCountMismatchFrames += 1;
      }
      const overCap = [...derivedRooms].some(
        ([room, n]) => n > BODY_CAP && (servedRooms.get(room) ?? 0) <= BODY_CAP,
      );
      if (overCap) {
        total.capOverflowFrames += 1;
      }

      const discovered = specs.filter((spec) => spec.isDiscovered);
      if (discovered.length > 0) {
        total.discoveredFrames += 1;
      }
      for (const spec of discovered) {
        if (!reportedHere.has(spec.victimId)) {
          total.discoveredAfterReportFrame += 1;
        }
      }
      for (const spec of specs) {
        const row = served.get(spec.victimId);
        if (row !== undefined && spec.killedBy !== row.killed_by) {
          total.attributionMismatches += 1;
        }
      }
    }
    if (gamePhantoms > 0) {
      total.gamesWithPhantom += 1;
    }
  }
  return total;
}

function reportBodyEvents(games: readonly FixtureGame[]): number {
  let n = 0;
  for (const game of games) {
    for (const frame of game.frames) {
      n += frame.events.filter((event) => event.type === "report_body").length;
    }
  }
  return n;
}

function victimsAt(games: readonly FixtureGame[], gameId: string, tick: number) {
  const game = games.find((candidate) => candidate.gameId === gameId);
  if (game === undefined) throw new Error(`no game "${gameId}" in the fixture`);
  const index = game.frames.findIndex((frame) => frame.tick === tick);
  if (index === -1) throw new Error(`game "${gameId}" has no tick ${tick}`);
  const frame = game.frames[index];
  if (frame === undefined) throw new Error(`game "${gameId}" tick ${tick} is empty`);
  const victims = (specs: readonly BodySpec[]): string[] =>
    [...specs].map((spec) => spec.victimId).sort();
  return {
    served: frame.bodies.map((body) => body.victim_id).sort(),
    shipped: victims(bodyStatesByTick(game.frames)[index] ?? []),
    retired: victims(retiredAccumulateRule(game.frames)[index] ?? []),
  };
}

// ── the census, both legs, both committed sets ───────────────────────────────

describe("the Omniscient body layer over the committed served payloads", () => {
  it.each(["9p2i", "4p1i"])("%s: the dump still matches the committed corpus", (name) => {
    // Without this the suite would keep passing over a detached snapshot after a
    // re-record replaced `replays/samples/`, covering bytes nobody serves. The
    // digest folds in every replay's filename AND bytes, so an added, removed or
    // rewritten replay all fail here until the fixture is regenerated.
    expect(corpusDigest(name)).toBe(set(name).corpusSha256);
    expect(set(name).games).toHaveLength(
      readdirSync(join(SAMPLES_DIR, name)).filter((entry) => entry.endsWith(".jsonl")).length,
    );
  });

  it("9p2i: reads engine truth on every frame", () => {
    expect(census(set("9p2i").games, bodyStatesByTick)).toEqual({
      games: 50,
      frames: 1217,
      phantomFrames: 0,
      missingFrames: 0,
      phantomBodies: 0,
      gamesWithPhantom: 0,
      roomCountMismatchFrames: 0,
      capOverflowFrames: 0,
      // One frame per report_body event, each on the report frame itself.
      discoveredFrames: 144,
      discoveredAfterReportFrame: 0,
      attributionMismatches: 0,
    });
    expect(reportBodyEvents(set("9p2i").games)).toBe(144);
  });

  it("9p2i: the retired accumulate rule fails the same walk", () => {
    expect(census(set("9p2i").games, retiredAccumulateRule)).toEqual({
      games: 50,
      frames: 1217,
      // Over half the frames painted a corpse the engine had consumed.
      phantomFrames: 668,
      missingFrames: 0,
      phantomBodies: 1371,
      gamesWithPhantom: 48,
      // Every phantom frame also inflates that room's body count …
      roomCountMismatchFrames: 668,
      // … and on 7 of them a room's pile crosses BODY_CAP, firing a spurious
      // "✕ ×N" collapse marker over a room the engine has emptied.
      capOverflowFrames: 7,
      discoveredFrames: 718,
      // Exactly the phantom count: every phantom IS a consumed corpse, so every
      // one of them still wears the "freshly reported" kill ring on a frame long
      // after its report. The shipped rule reads 0 here.
      discoveredAfterReportFrame: 1371,
      attributionMismatches: 0,
    });
  });

  it("4p1i: reads engine truth on every frame", () => {
    expect(census(set("4p1i").games, bodyStatesByTick)).toEqual({
      games: 50,
      frames: 601,
      phantomFrames: 0,
      missingFrames: 0,
      phantomBodies: 0,
      gamesWithPhantom: 0,
      roomCountMismatchFrames: 0,
      capOverflowFrames: 0,
      discoveredFrames: 37,
      discoveredAfterReportFrame: 0,
      attributionMismatches: 0,
    });
    expect(reportBodyEvents(set("4p1i").games)).toBe(37);
  });

  it("4p1i: the retired accumulate rule fails the same walk", () => {
    const retired = census(set("4p1i").games, retiredAccumulateRule);
    expect(retired.phantomFrames).toBe(66);
    expect(retired.phantomBodies).toBe(66);
    expect(retired.gamesWithPhantom).toBe(18);
    expect(retired.roomCountMismatchFrames).toBe(66);
    expect(retired.missingFrames).toBe(0);
  });

  it("draws the two shapes the review named", () => {
    // The review named two instances, and the SHAPES it named are what these
    // pin: a floor the engine has emptied that the retired rule still paints,
    // and a pile the retired rule inflates around a single real corpse. The
    // coordinates move with every re-record — the first survived the baseline-7
    // recording, the second re-anchored from seed 2 tick 29 to seed 6 tick 39 —
    // so the census above is what proves the class, and these two draw it.

    // "the engine has nothing on the floor, the map draws p-2."
    const empty = victimsAt(set("9p2i").games, "headless-seed-0", 18);
    expect(empty.served).toEqual([]);
    expect(empty.shipped).toEqual([]);
    expect(empty.retired).toEqual(["p-2"]);

    // "FOUR corpses drawn while the engine state has one."
    const pile = victimsAt(set("9p2i").games, "headless-seed-6", 39);
    expect(pile.served).toEqual(["p-4"]);
    expect(pile.shipped).toEqual(["p-4"]);
    expect(pile.retired).toEqual(["p-2", "p-3", "p-4", "p-5"]);
  });
});

// ── the semantics, on hand-built frames the committed sets do not exercise ───

const ROOM = "ADMIN";

function frame(
  bodies: readonly { victim: string; room?: string; killedBy?: string }[],
  events: readonly TickEventView[] = [],
): BodyTickSlice {
  return {
    bodies: bodies.map((body) => ({
      victim_id: body.victim,
      room_id: body.room ?? ROOM,
      killed_by: body.killedBy ?? "p-9",
    })),
    events,
  };
}

function reportOf(victim: string, tick = 0): TickEventView {
  return { type: "report_body", tick, reporter_id: "p-3", body_of: victim, room_id: ROOM };
}

function killOf(victim: string, killer: string, tick = 0): TickEventView {
  return { type: "kill", tick, killer_id: killer, victim_id: victim, room_id: ROOM };
}

describe("presence and discovery", () => {
  it("drops a body on the frame the engine consumes it", () => {
    const layers = bodyStatesByTick([
      frame([{ victim: "p-1" }], [killOf("p-1", "p-9")]),
      frame([{ victim: "p-1" }]),
      frame([], [reportOf("p-1", 2)]), // the meeting consumed the corpse
      frame([]),
    ]);
    expect(layers.map((specs) => specs.map((spec) => spec.victimId))).toEqual([
      ["p-1"],
      ["p-1"],
      [],
      [],
    ]);
  });

  it("keeps the discovered treatment on a reported body still on the floor", () => {
    // Only the meeting's TRIGGERING corpse is deleted, so a second reported body
    // can survive its own report — it must stay solid, not revert to ghosted.
    const layers = bodyStatesByTick([
      frame([{ victim: "p-1" }, { victim: "p-2" }], [reportOf("p-1")]),
      frame([{ victim: "p-1" }, { victim: "p-2" }]),
    ]);
    expect(layers[0]).toEqual([
      { victimId: "p-1", roomId: ROOM, isDiscovered: true, killedBy: "p-9" },
      { victimId: "p-2", roomId: ROOM, isDiscovered: false, killedBy: "p-9" },
    ]);
    expect(layers[1]?.[0]?.isDiscovered).toBe(true);
    expect(layers[1]?.[1]?.isDiscovered).toBe(false);
  });

  it("ghosts a body nobody has reported, however long it sits there", () => {
    const layers = bodyStatesByTick([
      frame([{ victim: "p-1" }]),
      frame([{ victim: "p-1" }]),
      frame([{ victim: "p-1" }]),
    ]);
    expect(layers.map((specs) => specs.map((spec) => spec.isDiscovered))).toEqual([
      [false],
      [false],
      [false],
    ]);
  });

  it("reads killedBy off the served row rather than the kill event", () => {
    // Planted divergence: the served attribution and the kill event disagree.
    // The layer must report the SERVED value — the field exists for this layer,
    // and re-deriving it from the event is what this task removed.
    const specs = bodiesForTick(
      frame([{ victim: "p-1", killedBy: "p-7" }], [killOf("p-1", "p-4")]),
      new Set<string>(),
    );
    expect(specs[0]?.killedBy).toBe("p-7");
  });

  it("has no layer at all for a replay with no frames", () => {
    expect(bodyStatesByTick([])).toEqual([]);
    expect(NO_BODIES).toEqual([]);
  });
});

// ── the As-agent firewall ────────────────────────────────────────────────────

function visibility(
  bodies: readonly { id: string; room: string; victim: string }[],
): AgentVisibilityView {
  return {
    visible_players: [],
    visible_bodies: bodies.map((body) => ({
      id: body.id,
      room: body.room,
      victim_id: body.victim,
    })),
    audible_events: [],
  };
}

describe("the As-agent body layer", () => {
  it("maps one spec per visible body, killer-free and never discovered", () => {
    expect(
      visibleBodiesForTick(
        visibility([
          { id: "body-p-1-4", room: "CAFETERIA", victim: "p-1" },
          { id: "body-p-2-9", room: "STORAGE", victim: "p-2" },
        ]),
      ),
    ).toEqual([
      { victimId: "p-1", roomId: "CAFETERIA", isDiscovered: false, killedBy: null },
      { victimId: "p-2", roomId: "STORAGE", isDiscovered: false, killedBy: null },
    ]);
  });

  it("lights nothing for an agent with no field of view", () => {
    expect(visibleBodiesForTick(null)).toEqual([]);
  });

  it("cannot leak a served body the agent did not see", () => {
    // The engine has two corpses on the floor and the packet lists neither, so
    // the fog layer draws neither: `visibleBodiesForTick` is never handed the
    // tick, and the packet carries no killer to leak.
    const tick = frame([{ victim: "p-1" }, { victim: "p-2" }]);
    expect(tick.bodies).toHaveLength(2);
    expect(visibleBodiesForTick(visibility([]))).toEqual([]);
  });
});
