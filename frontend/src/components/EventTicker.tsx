// The event ticker (Task 19.17; audits/audit-phase-19-triage.md §7 item 18 +
// singleton 29 — "subordinate to pause/finale/temporal-coherence work, not
// silently discarded"). Kills, body reports, meetings, ejections and vents as
// they play, in one running feed beside the stage.
//
// It lands LAST in the frontend chain on purpose: the dependency edges
// (19.10 → 19.12 → 19.13 → here) are the point — narrative correctness shipped
// before the chrome that decorates it. Nothing here touches the meeting pause,
// the finale card, or the transport; the ticker is a self-contained section in
// the stage column with no overlay, no z-index, and no `--transport-h` claim, so
// it cannot regress the flows 19.10 landed.
//
// ── WHY THIS FILE IS NOT "JUST CHROME" ──────────────────────────────────────
//
// The served event views are PRIVILEGED. `api/schemas.py` says so in as many
// words: `KillEventView` "projects engine.events.KilledEvent (privileged kill
// attribution)" — it carries `killer_id` unconditionally — and `VentEventView`
// carries the actor and BOTH endpoints of a vent route whose per-vent witness
// sets are deliberately not projected. A component that rendered
// `frame.events` verbatim would publish, in plain text, exactly what the
// As-agent fog exists to withhold. Unspoiled-mode gating is NOT the firewall
// here: `revealOutcome` governs whether the game's ENDING may render, which is a
// different axis entirely (App.tsx's PerspectiveBanner spells the split out).
//
// So the ticker renders through the SAME projection the map and roster enforce:
// the per-tick `AgentVisibilityView` the loader builds from each agent's
// already-firewall-filtered `ObservationPacket` (api/schemas.py; the pipeline
// `eval/leak_test.py` validates). Visibility is never re-derived client-side.
// The four cases, pinned in `EventTicker.test.ts`:
//
//   witnessed kill   → attribution, with the room the FOG projected (the agent
//                      was among the engine's recorded witnesses).
//   unwitnessed kill → never attribution. It reaches the ticker only as a body
//                      DISCOVERY, when the victim's body enters this agent's
//                      `visible_bodies` — killer-free by construction
//                      (`VisibleBodyView` has no `killed_by`).
//   witnessed vent   → the actor and the ONE endpoint the witness saw, on
//                      EITHER phase (both vent events carry `source_witnesses`
//                      and `destination_witnesses`, so an agent may witness only
//                      the dive, only the emergence, or both). Never the route:
//                      `_ObservedAction` records a single witnessed room, so a
//                      `from → to` line would invent perception.
//   unwitnessed vent → nothing at all, through any channel. (`vent_use_heard` is
//                      not a second chance: no audible cue is minted for a vent
//                      the observer did not witness, so heard-but-unseen is not a
//                      state the bytes contain. Older recordings carry the cue as
//                      a duplicate of the sighting beside it.)
//
// A fifth case sits beside them: the agent's OWN kill or vent. The engine
// excludes an actor from its own witness sets, so the four rules above would
// drop it — and worse, an own kill would then resurface through the body pass as
// "Found p-5's body", telling an impostor it had stumbled on a body it made
// itself. Own acts are the one thing an agent knows for certain, and the map
// already treats them that way under fog (the self token draws
// `selfActionGlyph(selfState.current_action)`, KILL and VENT included), so they
// get an explicit self branch. It is a carve-out for ONE actor, never a hole in
// the gate: other agents' unwitnessed acts stay invisible in the same frame, and
// the self's vent still shows one endpoint rather than a route, so "no vent
// route survives the fog" holds for every agent.
//
// PUBLIC beats — a body report, a meeting being called, and how the vote
// resolved — surface in every perspective. They are table-level facts the
// transcript states in the clear, which is why `MeetingView` already renders the
// transcript under fog and gates only the ejectee's ROLE.
//
// FRAME-BOUNDED, like the cost chips beside it: the walk stops at the current
// frame, so the ticker cannot leak the outcome under unspoiled mode — there is
// no future for it to read. It never touches `finale` or `metadata.winner`.

import { useMemo } from "react";

import { usePlayback } from "../hooks/usePlayback";
import type { Perspective } from "../lib/playback";
import { useReplayStore } from "../store/replayStore";
import type {
  AgentVisibilityView,
  MeetingView,
  TickEventView,
  TickView,
  VisiblePlayerView,
} from "../types/api";
import { SectionLabel } from "../ui/SectionLabel";

/** The beat classes the ticker carries (audit §7 item 18's list, plus vents). */
export type TickerKind = "kill" | "body" | "report" | "meeting" | "ejection" | "vent";

export interface TickerEntry {
  /** Stable React key: engine tick + per-frame ordinal + kind. */
  readonly key: string;
  /** ENGINE tick number (never the frame's array index). */
  readonly tick: number;
  readonly kind: TickerKind;
  /** The rendered line. Already projected — safe to print verbatim. */
  readonly text: string;
}

// Short, role-NEUTRAL badges. "eject" says the table voted, not that the table
// was right (the firewall's outcome rule: colouring or wording an outcome by
// guilt would leak who the impostor was).
const KIND_LABEL: Record<TickerKind, string> = {
  kill: "kill",
  body: "body",
  report: "report",
  meeting: "meeting",
  ejection: "eject",
  vent: "vent",
};

/**
 * A frame's events with the loader's ONE causal inversion corrected, and
 * everything else exactly where the engine put it.
 *
 * The inversion: `api/replay_loader.py` appends `MeetingTriggeredEventView`
 * and then, inside the body-trigger branch, the `ReportBodyEventView` that
 * caused it. Rendered in arrival order the feed announced the meeting before the
 * report, and the newest-first view stacked the report above it as though it
 * came later — backwards in both reading directions.
 *
 * WHY THIS IS A SURGICAL SWAP AND NOT A SORT BY KIND. Arrival order is the
 * engine's deterministic emission order, which IS chronological, so ranking
 * independent events by kind corrupts real information: 9p2i seed 1 tick 7 emits
 * p-6's vent EXIT before p-7's kill, and a kill-before-vent rank flips two
 * unrelated acts — then the reversed feed shows the earlier vent above the later
 * kill. Only the report/meeting pair is known to arrive inverted, so only it
 * moves; every other event keeps its position.
 */
function orderFrameEvents(events: readonly TickEventView[]): TickEventView[] {
  const ordered = [...events];
  for (let index = 0; index < ordered.length; index++) {
    if (ordered[index]?.type !== "report_body") {
      continue;
    }
    let meetingAt = -1;
    for (let back = index - 1; back >= 0; back--) {
      if (ordered[back]?.type === "meeting_triggered") {
        meetingAt = back;
        break;
      }
    }
    if (meetingAt === -1) {
      continue; // already ahead of its meeting, or a report with no meeting
    }
    const [report] = ordered.splice(index, 1);
    if (report !== undefined) {
      ordered.splice(meetingAt, 0, report);
    }
  }
  return ordered;
}

/**
 * The whole replay's beats, plus the per-frame boundary that makes any frame's
 * prefix an O(1) slice.
 *
 * `countAtFrame[i]` is `entries.length` after frame `i` was walked, so
 * `entries.slice(0, countAtFrame[i])` is exactly the frame-bounded feed — the
 * cumulative walk stays a single pass and the frame-bounding stays exact.
 */
export interface TickerTimeline {
  readonly entries: readonly TickerEntry[];
  readonly countAtFrame: readonly number[];
}

const EMPTY_TIMELINE: TickerTimeline = { entries: [], countAtFrame: [] };

/**
 * This agent's field of view at a frame, or `null` when it has none.
 *
 * The same rule MapView's `fogNoView` applies: an agent that is absent from the
 * frame or not alive has no perception to project, so nothing fog-gated may
 * surface for it.
 *
 * NO FIELD OF VIEW IS A FACT ABOUT LIVENESS, NOT A DEFAULT. `api/schemas.py`
 * states the invariant exactly: `visibility` is "`None` for a dead agent (no
 * field of view) and populated for every living agent". So `alive` is the ONLY
 * thing that may produce an empty fog, and it does so through the early return
 * above. Once past it, both `undefined` (field absent — an incompatible payload)
 * and `null` (a value the invariant forbids for a living agent) are REJECTED.
 *
 * This is the subtlest place in the file to swallow a malformed payload, because
 * an empty fog is a perfectly LEGITIMATE state elsewhere: coerced quietly, it
 * reads as a real blind agent — every witnessed kill, vent and body discovery
 * suppressed while the public beats keep rendering — and nothing in the output
 * distinguishes it from a genuine sparse feed. A wrong answer that cannot be
 * told from a right one is precisely what AGENTS.md's "raise, do not paper over"
 * exists for.
 *
 * Verified rather than assumed before tightening: across all 18,649 agent-frames
 * in the committed 9p2i + 4p1i sets, `alive && visibility === null` occurs zero
 * times, and so does `!alive && visibility !== null`. The invariant is exact on
 * served data, so the guard cannot fire on a compliant payload.
 *
 * The cast is the honest part — `api/client.ts` casts unvalidated JSON, so the
 * runtime can deliver a shape the generated type calls impossible, and
 * pretending otherwise is what let the original coercion look reasonable.
 */
function fogVisibility(frame: TickView, agentId: string): AgentVisibilityView | null {
  const self = frame.agent_states.find((state) => state.agent_id === agentId) ?? null;
  if (self === null || !self.is_alive) {
    return null; // the ONE legitimate no-fog path
  }
  const visibility = self.visibility as AgentVisibilityView | null | undefined;
  if (visibility === undefined || visibility === null) {
    throw new Error(
      `EventTicker: agent_states["${agentId}"] at tick ${frame.tick} is alive but ` +
        `carries ${visibility === undefined ? "no `visibility` field" : "`visibility: null`"}. ` +
        "The DTO promises visibility is populated for every living agent and `null` " +
        'means "dead agent, no field of view" — so this is an incompatible payload, ' +
        "not an empty fog, and must not be rendered as one.",
    );
  }
  return visibility;
}

/**
 * The witnessed sighting of `actorId` performing `action` this tick, or `null`.
 *
 * This lookup IS the firewall gate. `VisiblePlayerView.action` is stamped only
 * for a RESOLVED kill/vent event whose witness set contains this agent
 * (`observation/service.py::_observed_actions_for_agent`), so its presence is
 * the engine's own answer to "did this agent see it" — never a client-side
 * re-derivation from positions.
 */
function witnessedAction(
  visibility: AgentVisibilityView | null,
  actorId: string,
  action: "kill" | "vent",
): VisiblePlayerView | null {
  if (visibility === null) {
    return null;
  }
  return (
    visibility.visible_players.find(
      (player) => player.id === actorId && player.action === action,
    ) ?? null
  );
}

/**
 * Walk the WHOLE replay once, recording where each frame's beats end.
 *
 * ONE PASS PER (replay, perspective), not one per frame. The frame-scoped
 * `projectTicker` below is the readable contract and the unit-test surface, but
 * calling it on every `frameIndex` change makes a full playthrough quadratic in
 * ticks — the same shape Task 6.7 removed from `MapView`, which precomputes
 * `buildBodyStatesByTick` once per replay and indexes it by tick. This is that
 * pattern: the component memoizes the timeline on `[replay, perspective]` and
 * slices per frame, so autoplay costs a slice rather than a re-walk.
 *
 * (Honest magnitude: committed replays run 6–69 frames, so the quadratic is
 * latent rather than a live bottleneck — 69² is nothing. It matters against the
 * 1,000-tick `DEFAULT_MAX_TICKS` budget, and the fix is cheap and already the
 * house pattern, so there is no reason to leave the shape in place.)
 *
 * Chronological, with each frame's beats in CAUSAL order (see `KIND_ORDER`). The
 * walk always starts at frame 0: body discovery is de-duplicated across the
 * whole walk, which is what makes the result a function of position alone — the
 * same frame yields the same feed however you arrived.
 */
export function projectTickerTimeline(
  ticks: readonly TickView[],
  meetings: readonly MeetingView[],
  perspective: Perspective,
): TickerTimeline {
  const entries: TickerEntry[] = [];
  const countAtFrame: number[] = [];
  if (ticks.length === 0) {
    return { entries, countAtFrame };
  }
  const fogAgentId = perspective.mode === "agent" ? perspective.agentId : null;

  const meetingsByTick = new Map<number, MeetingView[]>();
  for (const meeting of meetings) {
    const list = meetingsByTick.get(meeting.tick);
    if (list === undefined) {
      meetingsByTick.set(meeting.tick, [meeting]);
    } else {
      list.push(meeting);
    }
  }

  // Victims this agent has already accounted for — by watching the kill, or by
  // finding the body earlier. Fog only; Omniscient reports the kill itself.
  const accountedVictims = new Set<string>();

  for (let index = 0; index < ticks.length; index++) {
    const frame = ticks[index];
    if (frame === undefined) {
      countAtFrame.push(entries.length);
      continue;
    }
    const visibility = fogAgentId === null ? null : fogVisibility(frame, fogAgentId);
    // Collected per frame so the whole frame can be causally ordered before it
    // joins the timeline; `ordinal` is assigned at push time, so the keys stay
    // unique regardless of how the sort below rearranges them.
    const frameEntries: TickerEntry[] = [];
    let ordinal = 0;
    const push = (kind: TickerKind, text: string): void => {
      frameEntries.push({
        key: `${frame.tick}:${ordinal}:${kind}`,
        tick: frame.tick,
        kind,
        text,
      });
      ordinal += 1;
    };

    for (const event of orderFrameEvents(frame.events)) {
      switch (event.type) {
        case "kill": {
          if (fogAgentId === null) {
            push("kill", `${event.killer_id} killed ${event.victim_id} · ${event.room_id}`);
            break;
          }
          // The agent's OWN act is self-knowledge, and it needs its own branch
          // because the engine excludes a killer from its own kill's witnesses
          // (`engine/rules.py`) — so `witnessedAction` below can NEVER match it.
          // Without this the fog would drop the kill and the body pass would
          // then report the victim as a discovery, telling an impostor it had
          // stumbled on a body it made itself. The map already carries this
          // exact fact under fog: the self token draws
          // `selfActionGlyph(selfState.current_action)`, which includes KILL.
          if (event.killer_id === fogAgentId) {
            accountedVictims.add(event.victim_id);
            push("kill", `${event.killer_id} killed ${event.victim_id} · ${event.room_id}`);
            break;
          }
          const seen = witnessedAction(visibility, event.killer_id, "kill");
          if (seen === null) {
            // Unwitnessed: the privileged attribution stops here. The body pass
            // below is the only route this death may take to the feed.
            break;
          }
          accountedVictims.add(event.victim_id);
          push("kill", `${event.killer_id} killed ${event.victim_id} · ${seen.room}`);
          break;
        }
        case "vent": {
          // BOTH phases are beats, and which room each one knows is the whole
          // point. On a real traversal the ENTER event's `to_room_id` EQUALS its
          // `from_room_id` — the destination is not resolved yet, which is why
          // `MapView.buildVentSegments` pairs the two events to get a route — so
          // only the EXIT event carries the emergence room. Reading a route off
          // the enter event printed `STORAGE → STORAGE`, and skipping the exit
          // dropped the destination entirely *and*, under fog, silently
          // discarded an emergence the agent genuinely witnessed.
          // `phase` decides whether this beat is a dive or an emergence, and an
          // unrecognised value must not default into either. `!== "enter"` alone
          // would treat a missing or unknown phase as an EXIT and then fabricate
          // an emergence — a route in Omniscient, an emergence endpoint in the
          // actor's own fog — out of data that says no such thing.
          const phase = event.phase as string;
          if (phase !== "enter" && phase !== "exit") {
            throw new Error(
              `EventTicker: vent event at tick ${event.tick} has phase ` +
                `${JSON.stringify(event.phase)}; the DTO admits only "enter" or ` +
                '"exit". An unknown phase is an incompatible payload, not an exit.',
            );
          }
          const entering = phase === "enter";
          if (fogAgentId === null) {
            push(
              "vent",
              entering
                ? `${event.actor_id} entered a vent · ${event.from_room_id}`
                : `${event.actor_id} emerged from a vent · ${event.from_room_id} → ${event.to_room_id}`,
            );
            break;
          }
          if (event.actor_id === fogAgentId) {
            // Self-knowledge, same as the own-kill branch above (the actor is
            // excluded from its own witness sets). The endpoint it was AT on
            // this tick, never the route — so the "no vent route survives the
            // fog" invariant holds for every agent, impostors included.
            push(
              "vent",
              entering
                ? `${event.actor_id} entered a vent · ${event.from_room_id}`
                : `${event.actor_id} emerged from a vent · ${event.to_room_id}`,
            );
            break;
          }
          const seen = witnessedAction(visibility, event.actor_id, "vent");
          if (seen === null) {
            break;
          }
          // Endpoint-agnostic wording on purpose: BOTH vent events carry
          // `source_witnesses` AND `destination_witnesses`, and
          // `_vent_observation_for_agent` projects whichever endpoint THIS
          // observer stood at — so naming the phase would assert perception the
          // packet does not support.
          push("vent", `${event.actor_id} used a vent · ${seen.room}`);
          break;
        }
        case "report_body":
          // A public report IS this body's discovery, so it accounts the victim
          // before the body pass below runs. Without this the fog narrates the
          // same discovery twice on one frame: the loader deliberately reopens
          // the reported body in `visible_bodies` for co-located agents, so a
          // report tick reads "p-8 reported p-4's body" immediately followed by
          // "Found p-4's body". Real on committed bytes — 9p2i seed 1, tick 8,
          // for p-1 and p-6 (not p-8, whose earlier sighting already accounted
          // it, which is exactly why the duplicate is easy to miss).
          //
          // Unconditional rather than fog-only: `accountedVictims` is read only
          // by the fog body pass, so this costs Omniscient nothing and keeps the
          // "one death, one beat" rule in one place.
          accountedVictims.add(event.body_of);
          push(
            "report",
            `${event.reporter_id} reported ${event.body_of}'s body · ${event.room_id}`,
          );
          break;
        case "meeting_triggered":
          push("meeting", `Meeting called by ${event.triggered_by} · ${event.trigger_kind}`);
          break;
        default:
          // `task_completed` is not a beat, and `sabotage` names its ACTOR —
          // only impostors sabotage, so printing it would leak a role the fog
          // has no channel to admit. Both stay out of the ticker.
          break;
      }
    }

    // Fog-only: bodies this agent can currently SEE. This is where an
    // unwitnessed kill surfaces — as a discovery, with no killer attached.
    if (fogAgentId !== null && visibility !== null) {
      for (const body of visibility.visible_bodies) {
        if (accountedVictims.has(body.victim_id)) {
          continue;
        }
        accountedVictims.add(body.victim_id);
        push("body", `Found ${body.victim_id}'s body · ${body.room}`);
      }
    }

    // How the table resolved. Public in both perspectives — the ejection is a
    // table-level fact; only the ejectee's ROLE is Omniscient-gated, and that
    // lives on MeetingView, not here.
    //
    // The two fields are COUPLED by the schema — `api/schemas.py` states it in
    // as many words: "``outcome`` and ``ejected_player_id`` are coupled
    // (EJECTED <=> non-null id)". So a contradiction is rejected rather than
    // resolved into whichever branch it happens to fall through to. The previous
    // `else` was the trap: an `EJECTED` meeting with a null id printed
    // "Vote resolved — no ejection", which is not a degraded rendering of the
    // truth but its exact opposite, and indistinguishable from a real SKIP.
    // (0 contradictions across the 204 committed meetings — this cannot fire on
    // a compliant payload.)
    for (const meeting of meetingsByTick.get(frame.tick) ?? []) {
      const ejectedId = meeting.ejected_player_id ?? null;
      // `MeetingOutcome` is a CLOSED pair. A bare `else` would have swept a
      // third value ("CANCELLED", a typo, a future outcome) into "Vote resolved
      // — no ejection", which is a specific claim about what the table did, not
      // a neutral fallback.
      const outcome = meeting.outcome as string;
      if (outcome === "EJECTED") {
        if (ejectedId === null) {
          throw new Error(
            `EventTicker: meeting ${meeting.meeting_id} at tick ${meeting.tick} is ` +
              "EJECTED with no `ejected_player_id`. The DTO couples the two " +
              "(EJECTED <=> non-null id), so this is an incompatible payload — " +
              'rendering it as "no ejection" would state the opposite of the outcome.',
          );
        }
        push("ejection", `${ejectedId} ejected by the vote`);
      } else if (outcome === "SKIPPED") {
        if (ejectedId !== null) {
          throw new Error(
            `EventTicker: meeting ${meeting.meeting_id} at tick ${meeting.tick} is ` +
              `SKIPPED but names an ejected player (${ejectedId}). The DTO couples ` +
              "the two (EJECTED <=> non-null id), so this is an incompatible " +
              "payload, not a skip.",
          );
        }
        push("ejection", "Vote resolved — no ejection");
      } else {
        throw new Error(
          `EventTicker: meeting ${meeting.meeting_id} at tick ${meeting.tick} has ` +
            `outcome ${JSON.stringify(meeting.outcome)}; the DTO admits only ` +
            '"EJECTED" or "SKIPPED". An unknown outcome is an incompatible ' +
            "payload — it must not be narrated as a skip.",
        );
      }
    }

    // The frame joins the timeline in walk order and its boundary is recorded.
    // No re-sort here: the events were already ordered on the way in, the fog's
    // body discoveries follow them (they are derived from `visible_bodies`, not
    // engine-emitted, so they carry no emission time of their own), and the
    // resolution is last because that is when the table actually resolved.
    entries.push(...frameEntries);
    countAtFrame.push(entries.length);
  }

  return { entries, countAtFrame };
}

/**
 * The ticker's entries for everything that has played UP TO AND INCLUDING
 * `frameIndex`, projected through `perspective`.
 *
 * The readable contract, and the unit-test surface: pure, frame-bounded, and
 * expressible without a renderer (the vitest baseline Task 19.12 landed runs
 * `environment: "node"`). The component does NOT call this per frame — it
 * memoizes {@link projectTickerTimeline} and slices, which is the same work
 * without the per-frame re-walk.
 */
export function projectTicker(
  ticks: readonly TickView[],
  meetings: readonly MeetingView[],
  frameIndex: number,
  perspective: Perspective,
): TickerEntry[] {
  const timeline = projectTickerTimeline(ticks, meetings, perspective);
  return entriesThroughFrame(timeline, frameIndex, ticks.length);
}

/**
 * The frame-bounded prefix of an already-walked timeline.
 *
 * Clamps rather than trusts, at BOTH ends — the same convention
 * `lib/playback`'s `tickNumberAt` uses: an out-of-range index is a position, not
 * a licence to read past the frame the viewer has actually reached, and not a
 * reason to invent one either.
 */
export function entriesThroughFrame(
  timeline: TickerTimeline,
  frameIndex: number,
  frameCount: number,
): TickerEntry[] {
  if (frameCount === 0) {
    return [];
  }
  const clamped = Math.max(0, Math.min(frameIndex, frameCount - 1));
  return timeline.entries.slice(0, timeline.countAtFrame[clamped] ?? 0);
}

/** The running feed beside the stage. Renders nothing until a replay is open. */
export function EventTicker() {
  const replay = useReplayStore((s) => s.currentReplay);
  const perspective = useReplayStore((s) => s.perspective);
  const { frameIndex, tickNumber } = usePlayback();

  // Memoized on [replay, perspective] and deliberately NOT on `frameIndex`: the
  // walk happens ONCE per replay/perspective and each frame is an O(1) slice of
  // it. Depending on the frame here is what would make autoplay quadratic — the
  // shape Task 6.7 removed from MapView, whose per-replay invariants
  // (`buildBodyStatesByTick`) are memoized exactly like this.
  //
  // `replay === null` is the only guard, and `ticks` / `meetings` are read
  // DIRECTLY off it. Both are required fields of the versioned DTO, so an
  // `?? []` normalisation would turn a malformed payload into an empty feed that
  // looks exactly like "nothing has happened yet" — a plausible false result,
  // which is the silent fallback AGENTS.md forbids. Read them straight: an
  // incompatible payload throws where a reader can see it.
  const timeline = useMemo(
    () =>
      replay === null
        ? EMPTY_TIMELINE
        : projectTickerTimeline(replay.ticks, replay.meetings, perspective),
    [replay, perspective],
  );
  const entries = useMemo(
    () => entriesThroughFrame(timeline, frameIndex, replay?.ticks.length ?? 0),
    [timeline, frameIndex, replay],
  );

  if (replay === null) {
    return null;
  }

  const inFog = perspective.mode === "agent";
  // Newest first: the beat that just played is always the top row, so the feed
  // needs no scroll management to stay current (and none of the auto-scrolling a
  // reduced-motion reader would have to opt out of).
  const newestFirst = [...entries].reverse();
  // EVERY beat on the frame just reached, not merely the last one. A single tick
  // routinely carries several — `meeting_triggered` + `report_body` + the vote
  // resolution all land together (the multi-beat case `EventTicker.test.ts`
  // already pins at four entries on one tick) — so announcing `newestFirst[0]`
  // alone would read out the ejection and silently drop the report and the
  // meeting that explain it.
  //
  // Selected by TICK rather than by diffing against the previous render: the
  // projection is position-derived, so "the beats belonging to this frame" is
  // exactly the set a reader has just arrived at, and it stays correct after a
  // scrub or a jump — where a diff would either flood (every beat since the last
  // position) or go silent. Chronological, so the announcement matches the order
  // the beats happened rather than the newest-first visual order.
  const arriving = entries.filter((entry) => entry.tick === tickNumber);

  return (
    <section
      aria-label="Event ticker"
      className="mt-3 rounded-lg border-2 border-ink-900 bg-paper-0 p-3 shadow-chrome-1"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <SectionLabel as="h2">Ticker</SectionLabel>
        {/* The projection is NAMED, not implied: a feed that silently carries
            less under fog reads as a bug. This says which lens produced it. */}
        <span
          className="rounded-pill bg-paper-2 px-1.5 font-mono text-3xs uppercase tracking-wide text-ink-500"
          title={
            inFog
              ? "Only what this agent's fog admits — an unwitnessed kill shows as a body discovery, unwitnessed vents not at all"
              : "Every recorded beat up to this frame, including privileged attribution"
          }
        >
          {inFog ? `as ${perspective.agentId} · fog` : "omniscient"} · to t{tickNumber}
        </span>
      </div>
      {/* The beats arrive on their own during autoplay and keyboard stepping,
          which is exactly the otherwise-silent playback transition the meeting
          pause bar solves with `role="status"`. This is the same device for the
          same reason.

          It holds ONLY this frame's beats, never the accumulated feed: a live
          region announces its content when that content CHANGES, so a node
          containing the whole list would re-read every beat on every step —
          worse than silence by the time a game has twenty of them. Scoped to the
          arriving frame, landing on a tick announces everything that happened
          there and nothing that did not, and a frame with no beats announces
          nothing (empty content). The visible <ol> below is deliberately NOT
          live for the same reason — do not add `aria-live` to it. */}
      <p role="status" aria-live="polite" className="sr-only">
        {arriving.length === 0
          ? ""
          : `tick ${tickNumber}: ${arriving.map((entry) => entry.text).join("; ")}`}
      </p>
      {newestFirst.length === 0 ? (
        <p className="mt-2 font-mono text-2xs text-ink-500">
          {inFog
            ? "Nothing this agent has seen yet."
            : "Nothing has happened yet."}
        </p>
      ) : (
        <ol className="mt-2 flex max-h-44 flex-col gap-1 overflow-y-auto pr-1">
          {newestFirst.map((entry) => (
            <li
              key={entry.key}
              className="flex items-center gap-2 rounded-md border border-ink-200 px-2 py-1"
            >
              <span className="shrink-0 rounded-pill bg-paper-2 px-1.5 font-mono text-3xs text-ink-500">
                t{entry.tick}
              </span>{" "}
              <span className="shrink-0 rounded-sm border border-ink-300 px-1 text-4xs font-semibold uppercase tracking-wide text-ink-500">
                {KIND_LABEL[entry.kind]}
              </span>{" "}
              {/* The explicit spaces are for `textContent`, not for layout (the
                  gap is CSS): a whitespace-only child of a flex container is not
                  rendered, so the row reads "t4 kill p-3 killed p-5 · REACTOR"
                  to a screen reader and to the browser journey, and unchanged on
                  screen. */}
              <span className="min-w-0 font-mono text-2xs text-ink-900">{entry.text}</span>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
