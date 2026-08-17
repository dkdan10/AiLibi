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
//   witnessed vent   → the actor and the ONE endpoint the witness saw. Never the
//                      route: `_ObservedAction` records a single witnessed room,
//                      so a `from → to` line would invent perception.
//   unwitnessed vent → nothing at all, through any channel. (`vent_use_heard` is
//                      not a second chance: `observation/service.py` derives the
//                      audible cue from the SAME witness-gated observed action,
//                      so heard-but-unseen is not a state the bytes contain.)
//
// One consequence worth naming because it looks like a bug and is not: an
// impostor watching its OWN kill in fog does not see it either. The engine
// excludes a killer from its own kill's witnesses, and the privileged self
// channel that would carry it (`SelfView.own_kill`) is deliberately not
// projected into `AgentVisibilityView` — so the bytes the ticker reads simply do
// not contain it. The map has the same blind spot for the same reason.
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

const EMPTY_TICKS: readonly TickView[] = [];
const EMPTY_MEETINGS: readonly MeetingView[] = [];

/**
 * This agent's field of view at a frame, or `null` when it has none.
 *
 * The same rule MapView's `fogNoView` applies: an agent that is absent from the
 * frame or not alive has no perception to project, so nothing fog-gated may
 * surface for it. `?? null` on `visibility` because the API client casts
 * unvalidated JSON — a stale payload yields `undefined` where TS insists on a
 * field.
 */
function fogVisibility(frame: TickView, agentId: string): AgentVisibilityView | null {
  const self = frame.agent_states.find((state) => state.agent_id === agentId) ?? null;
  if (self === null || !self.is_alive) {
    return null;
  }
  return self.visibility ?? null;
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
 * The ticker's entries for everything that has played UP TO AND INCLUDING
 * `frameIndex`, projected through `perspective`.
 *
 * Pure and exported so the four fog cases are unit-pinnable without a renderer
 * (the vitest baseline Task 19.12 landed runs `environment: "node"`).
 *
 * Chronological — the component reverses for display, so "newest first" is a
 * presentation choice and this stays the natural order to reason about. The walk
 * ALWAYS starts at frame 0 rather than resuming from somewhere: body discovery
 * is de-duplicated across the whole walk (a body stays visible for many ticks,
 * and one sighting is one beat), which makes the result a function of the
 * position alone — the same frame yields the same feed however you arrived.
 */
export function projectTicker(
  ticks: readonly TickView[],
  meetings: readonly MeetingView[],
  frameIndex: number,
  perspective: Perspective,
): TickerEntry[] {
  const entries: TickerEntry[] = [];
  if (ticks.length === 0) {
    return entries;
  }
  // Clamp rather than trust: an out-of-range index is a position, not a licence
  // to read past the frame the viewer has actually reached.
  const lastIndex = Math.max(0, Math.min(frameIndex, ticks.length - 1));
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

  for (let index = 0; index <= lastIndex; index++) {
    const frame = ticks[index];
    if (frame === undefined) {
      continue;
    }
    const visibility = fogAgentId === null ? null : fogVisibility(frame, fogAgentId);
    let ordinal = 0;
    const push = (kind: TickerKind, text: string): void => {
      entries.push({ key: `${frame.tick}:${ordinal}:${kind}`, tick: frame.tick, kind, text });
      ordinal += 1;
    };

    for (const event of frame.events) {
      switch (event.type) {
        case "kill": {
          if (fogAgentId === null) {
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
          // The dive is the beat; `exit` is the same act re-emitted at the far
          // end, so surfacing both would double every vent.
          if (event.phase !== "enter") {
            break;
          }
          if (fogAgentId === null) {
            push("vent", `${event.actor_id} vented ${event.from_room_id} → ${event.to_room_id}`);
            break;
          }
          const seen = witnessedAction(visibility, event.actor_id, "vent");
          if (seen === null) {
            break;
          }
          // The witnessed ENDPOINT only — never `from → to`. A witness at one
          // mouth of the network did not see where the actor came out.
          push("vent", `${event.actor_id} used a vent · ${seen.room}`);
          break;
        }
        case "report_body":
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
    for (const meeting of meetingsByTick.get(frame.tick) ?? []) {
      if (meeting.outcome === "EJECTED" && meeting.ejected_player_id !== null) {
        push("ejection", `${meeting.ejected_player_id} ejected by the vote`);
      } else {
        push("ejection", "Vote resolved — no ejection");
      }
    }
  }

  return entries;
}

/** The running feed beside the stage. Renders nothing until a replay is open. */
export function EventTicker() {
  const replay = useReplayStore((s) => s.currentReplay);
  const perspective = useReplayStore((s) => s.perspective);
  const { frameIndex, tickNumber } = usePlayback();

  const entries = useMemo(
    () =>
      projectTicker(
        replay?.ticks ?? EMPTY_TICKS,
        replay?.meetings ?? EMPTY_MEETINGS,
        frameIndex,
        perspective,
      ),
    [replay, frameIndex, perspective],
  );

  if (replay === null) {
    return null;
  }

  const inFog = perspective.mode === "agent";
  // Newest first: the beat that just played is always the top row, so the feed
  // needs no scroll management to stay current (and none of the auto-scrolling a
  // reduced-motion reader would have to opt out of).
  const newestFirst = [...entries].reverse();

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
