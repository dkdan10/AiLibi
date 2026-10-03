// Test support: the committed replay skeletons, read and bound to the bytes.
//
// `replay-skeleton.fixture.json` dumps, for every game of both sample sets, the
// structure the map's vent trips, the regroup snap and the omniscient meeting
// annotations read, and nothing else:
//
//   • per frame: its tick, the room each living player stands in (one character
//     per player, in roster order: an index into the set's room table, or "-"
//     for a dead player), the players whose `is_venting` holds, and the
//     `vent`, `kill` and `report_body` events;
//   • per meeting: its id, tick, trigger, opener and ejected player, and each
//     turn's skeleton — index, speaker, kind, the players its accusations name
//     and its stated routes. No free text, no prompt, no ballot rationale.
//
// It is committed rather than derived in the test because the replay rows are
// ACTION-only: rooms, venting and the events exist only after the Python
// loader's engine re-walk. `corpus_sha256` binds each set to the replay bytes it
// came from, and `readSkeleton` recomputes it from `replays/samples/<set>` on
// every read, so a re-recorded corpus fails every suite that reads this dump
// until it is regenerated. Regenerate from the repo root with:
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
//       rooms: list[str] = []
//       resets: set[str] = set()
//       games = []
//       for meta in loader.list_replays():
//           replay = loader.load_replay(meta.game_id, include_llm_bodies=False)
//           config = replay.metadata.experiment_config
//           resets.add("preserve" if config is None else config.meeting_reset)
//           players = [player.agent_id for player in replay.players]
//           frames = []
//           for tick in replay.ticks:
//               states = {state.agent_id: state for state in tick.agent_states}
//               placed = ""
//               for player in players:
//                   state = states[player]
//                   if not state.is_alive:
//                       placed += "-"
//                       continue
//                   if state.room_id is None:
//                       raise ValueError(f"{meta.game_id} {tick.tick}: {player} has no room")
//                   if state.room_id not in rooms:
//                       rooms.append(state.room_id)
//                   placed += str(rooms.index(state.room_id))
//               frame: dict[str, object] = {"tick": tick.tick, "rooms": placed}
//               venting = [
//                   index
//                   for index, player in enumerate(players)
//                   if player in states and states[player].is_venting
//               ]
//               if venting:
//                   frame["venting"] = venting
//               events = [
//                   event.model_dump(mode="json")
//                   for event in tick.events
//                   if event.type in ("vent", "kill", "report_body")
//               ]
//               if events:
//                   frame["events"] = events
//               frames.append(frame)
//           meetings = []
//           for meeting in replay.meetings:
//               turns = []
//               for turn in meeting.turns:
//                   turns.append(
//                       {
//                           "turn_index": turn.turn_index,
//                           "speaker": turn.speaker,
//                           "turn_kind": turn.turn_kind,
//                           "accuses": [
//                               claim.against
//                               for claim in turn.claims
//                               if claim.type == "accusation"
//                           ],
//                           "alibis": [
//                               {
//                                   "subject": claim.subject,
//                                   "route": [
//                                       [leg.room, leg.from_tick, leg.to_tick]
//                                       for leg in claim.route or ()
//                                   ],
//                               }
//                               for claim in turn.claims
//                               if claim.type == "alibi"
//                           ],
//                       }
//                   )
//               meetings.append(
//                   {
//                       "meeting_id": meeting.meeting_id,
//                       "tick": meeting.tick,
//                       "trigger_kind": meeting.trigger_kind,
//                       "triggered_by": meeting.triggered_by,
//                       "ejected": meeting.ejected_player_id,
//                       "turns": turns,
//                   }
//               )
//           games.append(
//               {
//                   "game_id": meta.game_id,
//                   "players": players,
//                   "frames": frames,
//                   "meetings": meetings,
//               }
//           )
//       (reset,) = resets
//       if len(rooms) > 10:
//           raise ValueError("one character per room holds ten rooms")
//       sets.append(
//           {
//               "name": name,
//               "corpus_sha256": corpus_sha256(replay_dir),
//               "meeting_reset": reset,
//               "rooms": rooms,
//               "games": games,
//           }
//       )
//   Path("frontend/src/lib/replay-skeleton.fixture.json").write_text(
//       json.dumps({"sets": sets}, separators=(",", ":")) + "\n"
//   )
//   PY
//
// Read off disk with `readFileSync`, as `bodies.test.ts` reads its own dump, and
// typed field by field so the strict flags stay honest.

import { createHash } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import type { AnnotationAgentSlice } from "./annotations";
import type { MeetingReset } from "./regroup";
import type { TickEventView } from "../types/api";

const LIB_DIR = dirname(fileURLToPath(import.meta.url));
const FIXTURE_PATH = resolve(LIB_DIR, "replay-skeleton.fixture.json");
/** `frontend/src/lib` → the repo root's committed sample sets. */
export const SAMPLES_DIR = resolve(LIB_DIR, "../../../replays/samples");

/** One stated route in a turn: `[room, fromTick, toTick]` legs about `subject`. */
export interface SkeletonAlibi {
  readonly subject: string;
  readonly route: readonly (readonly [string, number, number])[];
}

export interface SkeletonTurn {
  readonly turn_index: number;
  readonly speaker: string;
  readonly turn_kind: "opening" | "reply" | "opt_in";
  /** The served claims, narrowed to accusations: what the annotations read. */
  readonly claims: readonly { readonly type: "accusation"; readonly against: string }[];
  readonly alibis: readonly SkeletonAlibi[];
}

export interface SkeletonMeeting {
  readonly meeting_id: string;
  readonly tick: number;
  readonly trigger_kind: "body" | "emergency";
  readonly triggered_by: string;
  readonly ejected: string | null;
  readonly turns: readonly SkeletonTurn[];
}

export interface SkeletonFrame {
  readonly tick: number;
  readonly events: readonly TickEventView[];
  readonly agent_states: readonly AnnotationAgentSlice[];
}

/** A game as a served-replay slice; assignable to every slice the modules read. */
export interface SkeletonReplay {
  readonly metadata: { readonly experiment_config: { readonly meeting_reset: MeetingReset } };
  readonly ticks: readonly SkeletonFrame[];
  readonly meetings: readonly SkeletonMeeting[];
}

export interface SkeletonGame {
  readonly gameId: string;
  readonly players: readonly string[];
  /** The game as a served-replay slice: what `annotations`, `regroup` and `vents` read. */
  readonly replay: SkeletonReplay;
}

export interface SkeletonSet {
  readonly name: string;
  readonly corpusSha256: string;
  readonly meetingReset: MeetingReset;
  readonly games: readonly SkeletonGame[];
}

/**
 * A digest of one sample set's committed replay bytes: sha256 over
 * `<filename>\n<sha256 of that file>\n` for every `*.jsonl`, name-sorted — the
 * generator's `corpus_sha256`.
 */
export function corpusDigest(setName: string): string {
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

function asOneOf<T extends string>(value: unknown, allowed: readonly T[], where: string): T {
  const text = asString(value, where);
  const found = allowed.find((candidate) => candidate === text);
  if (found === undefined) {
    throw new Error(`${where}: "${text}" is not one of ${allowed.join(", ")}`);
  }
  return found;
}

function readEvent(raw: unknown, where: string): TickEventView {
  const row = asRecord(raw, where);
  const type = asString(row["type"], `${where}.type`);
  const tick = asNumber(row["tick"], `${where}.tick`);
  if (type === "vent") {
    return {
      type: "vent",
      tick,
      actor_id: asString(row["actor_id"], `${where}.actor_id`),
      phase: asOneOf(row["phase"], ["enter", "exit"] as const, `${where}.phase`),
      from_room_id: asString(row["from_room_id"], `${where}.from_room_id`),
      to_room_id: asString(row["to_room_id"], `${where}.to_room_id`),
      traversal_ticks: asNumber(row["traversal_ticks"], `${where}.traversal_ticks`),
    };
  }
  if (type === "kill") {
    return {
      type: "kill",
      tick,
      killer_id: asString(row["killer_id"], `${where}.killer_id`),
      victim_id: asString(row["victim_id"], `${where}.victim_id`),
      room_id: asString(row["room_id"], `${where}.room_id`),
    };
  }
  if (type === "report_body") {
    return {
      type: "report_body",
      tick,
      reporter_id: asString(row["reporter_id"], `${where}.reporter_id`),
      body_of: asString(row["body_of"], `${where}.body_of`),
      room_id: asString(row["room_id"], `${where}.room_id`),
    };
  }
  throw new Error(`${where}: the dump carries vent / kill / report_body only, got "${type}"`);
}

function readFrame(
  raw: unknown,
  players: readonly string[],
  rooms: readonly string[],
  where: string,
): SkeletonFrame {
  const row = asRecord(raw, where);
  const placed = asString(row["rooms"], `${where}.rooms`);
  if (placed.length !== players.length) {
    throw new Error(`${where}.rooms: ${placed.length} places for ${players.length} players`);
  }
  const venting = new Set(
    (row["venting"] === undefined ? [] : asArray(row["venting"], `${where}.venting`)).map(
      (index, i) => {
        const player = players[asNumber(index, `${where}.venting[${i}]`)];
        if (player === undefined) throw new Error(`${where}.venting[${i}]: no such player`);
        return player;
      },
    ),
  );
  const agentStates = players.map((agentId, index) => {
    const mark = placed[index] ?? "-";
    if (mark === "-") {
      return { agent_id: agentId, room_id: null, is_alive: false, is_venting: venting.has(agentId) };
    }
    const room = rooms[Number(mark)];
    if (room === undefined) throw new Error(`${where}.rooms[${index}]: no room "${mark}"`);
    return { agent_id: agentId, room_id: room, is_alive: true, is_venting: venting.has(agentId) };
  });
  const events = row["events"] === undefined ? [] : asArray(row["events"], `${where}.events`);
  return {
    tick: asNumber(row["tick"], `${where}.tick`),
    events: events.map((event, i) => readEvent(event, `${where}.events[${i}]`)),
    agent_states: agentStates,
  };
}

function readTurn(raw: unknown, where: string): SkeletonTurn {
  const row = asRecord(raw, where);
  return {
    turn_index: asNumber(row["turn_index"], `${where}.turn_index`),
    speaker: asString(row["speaker"], `${where}.speaker`),
    turn_kind: asOneOf(row["turn_kind"], ["opening", "reply", "opt_in"] as const, `${where}.turn_kind`),
    claims: asArray(row["accuses"], `${where}.accuses`).map((against, i) => ({
      type: "accusation" as const,
      against: asString(against, `${where}.accuses[${i}]`),
    })),
    alibis: asArray(row["alibis"], `${where}.alibis`).map((rawAlibi, i) => {
      const alibi = asRecord(rawAlibi, `${where}.alibis[${i}]`);
      return {
        subject: asString(alibi["subject"], `${where}.alibis[${i}].subject`),
        route: asArray(alibi["route"], `${where}.alibis[${i}].route`).map((rawLeg, j) => {
          const leg = asArray(rawLeg, `${where}.alibis[${i}].route[${j}]`);
          const at = `${where}.alibis[${i}].route[${j}]`;
          return [asString(leg[0], at), asNumber(leg[1], at), asNumber(leg[2], at)] as const;
        }),
      };
    }),
  };
}

function readMeeting(raw: unknown, where: string): SkeletonMeeting {
  const row = asRecord(raw, where);
  const ejected = row["ejected"];
  return {
    meeting_id: asString(row["meeting_id"], `${where}.meeting_id`),
    tick: asNumber(row["tick"], `${where}.tick`),
    trigger_kind: asOneOf(row["trigger_kind"], ["body", "emergency"] as const, `${where}.trigger_kind`),
    triggered_by: asString(row["triggered_by"], `${where}.triggered_by`),
    ejected: ejected === null ? null : asString(ejected, `${where}.ejected`),
    turns: asArray(row["turns"], `${where}.turns`).map((turn, i) => readTurn(turn, `${where}.turns[${i}]`)),
  };
}

/**
 * Every set the dump carries, each checked against the replay bytes it names.
 * A set whose digest no longer matches `replays/samples/<set>` raises.
 */
export function readSkeleton(): readonly SkeletonSet[] {
  const root = asRecord(JSON.parse(readFileSync(FIXTURE_PATH, "utf8")), "fixture");
  return asArray(root["sets"], "fixture.sets").map((rawSet, s) => {
    const setRow = asRecord(rawSet, `sets[${s}]`);
    const name = asString(setRow["name"], `sets[${s}].name`);
    const corpusSha256 = asString(setRow["corpus_sha256"], `${name}.corpus_sha256`);
    if (corpusDigest(name) !== corpusSha256) {
      throw new Error(
        `${name}: the skeleton dump was taken from other bytes than replays/samples/${name}; regenerate it`,
      );
    }
    const meetingReset = asOneOf(
      setRow["meeting_reset"],
      ["preserve", "hub_with_grace"] as const,
      `${name}.meeting_reset`,
    );
    const rooms = asArray(setRow["rooms"], `${name}.rooms`).map((room, i) => asString(room, `${name}.rooms[${i}]`));
    return {
      name,
      corpusSha256,
      meetingReset,
      games: asArray(setRow["games"], `${name}.games`).map((rawGame, g) => {
        const gameRow = asRecord(rawGame, `${name}.games[${g}]`);
        const gameId = asString(gameRow["game_id"], `${name}.games[${g}].game_id`);
        const players = asArray(gameRow["players"], `${gameId}.players`).map((p, i) =>
          asString(p, `${gameId}.players[${i}]`),
        );
        return {
          gameId,
          players,
          replay: {
            metadata: { experiment_config: { meeting_reset: meetingReset } },
            ticks: asArray(gameRow["frames"], `${gameId}.frames`).map((frame, f) =>
              readFrame(frame, players, rooms, `${gameId}.frames[${f}]`),
            ),
            meetings: asArray(gameRow["meetings"], `${gameId}.meetings`).map((meeting, m) =>
              readMeeting(meeting, `${gameId}.meetings[${m}]`),
            ),
          },
        };
      }),
    };
  });
}

/** One set of the dump, by name. */
export function skeletonSet(sets: readonly SkeletonSet[], name: string): SkeletonSet {
  const found = sets.find((candidate) => candidate.name === name);
  if (found === undefined) throw new Error(`the skeleton dump carries no set named "${name}"`);
  return found;
}

/** One game of a set, by game id. */
export function skeletonGame(set: SkeletonSet, gameId: string): SkeletonGame {
  const found = set.games.find((candidate) => candidate.gameId === gameId);
  if (found === undefined) throw new Error(`${set.name} carries no game "${gameId}"`);
  return found;
}
