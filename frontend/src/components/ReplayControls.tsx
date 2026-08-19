// The playback transport region (Task 12.4; design/phase-12/stage-1-design.md §4,
// §2.3). Three stacked, hand-coded-from-tokens surfaces the workspace shell
// composes into its bottom bar:
//
//   • `AdvantageGraph` — the clickable second scrubber (crew-vs-impostor over
//     ticks, key-moment inflections; click to seek),
//   • `EventTimeline`  — one lane per agent with kill/meeting/vent/sabotage
//     markers,
//   • `ReplayControls` — the transport proper: scrub · play/pause · speed · step
//     ±N · jump prev/next event · jump prev/next meeting · next key moment, plus
//     the disclosure that shows or hides the two surfaces above it.
//
// The advantage graph and timeline share a hover CROSSHAIR via `hoverTick` in the
// store (the engine tick under the cursor), so the two surfaces line up. All
// three derive position from the ONE engine-tick source of truth through
// `usePlayback` + `lib/playback`; there is no local index↔tick re-derivation.

import { Fragment, useMemo, useRef } from "react";
import type {
  KeyboardEvent as ReactKeyboardEvent,
  MouseEvent as ReactMouseEvent,
  ReactNode,
} from "react";

import { usePlayback } from "../hooks/usePlayback";
import { TRANSPORT_COPY } from "../lib/copy";
import {
  type KeyMomentKind,
  type TimelineKind,
  advantageSeries,
  frameIndexForTick,
  keyMoments,
  tickNumberAt,
  timelineMarkers,
} from "../lib/playback";
import { useReplayStore } from "../store/replayStore";
import type { PlaybackSpeed } from "../store/replayStore";

const SPEEDS: readonly PlaybackSpeed[] = [0.5, 1, 2, 4];

// Chunky-sticker chrome (the Playful elevation tokens are CHROME-only — the
// transport is chrome). Disabled controls drop the shadow + dim.
const BUTTON =
  "inline-flex items-center justify-center gap-1 rounded-md border-2 border-ink-900 " +
  "bg-paper-0 px-3 py-1.5 text-sm font-medium text-ink-900 shadow-chrome-1 " +
  "transition-[transform,box-shadow] hover:-translate-y-px active:translate-y-0.5 " +
  "active:shadow-none disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none " +
  "disabled:hover:translate-y-0";

// Per-kind glyph + chip: a letter (text) AND a colour (hue) — never hue-only,
// per the firewall rules. Colours stay on the reserved meaning channels.
const KEY_MOMENT_STYLE: Record<KeyMomentKind, { letter: string; chip: string }> = {
  kill: { letter: "K", chip: "bg-kill text-paper-0" },
  meeting: { letter: "M", chip: "bg-ink-700 text-paper-0" },
  ejection: { letter: "E", chip: "bg-contradiction text-paper-0" },
  // Sabotage = the hazard treatment (Task 12.13): ink stripes + ⚡ glyph, OFF the
  // reserved warm hue (it was colliding with distrust-orange + the kill red).
  sabotage: { letter: "⚡", chip: "hazard-stripe text-paper-0" },
};

const TIMELINE_STYLE: Record<
  TimelineKind,
  { letter: string; chip: string; label: string }
> = {
  kill: { letter: "K", chip: "bg-kill text-paper-0", label: "kill" },
  meeting: { letter: "M", chip: "bg-ink-700 text-paper-0", label: "meeting" },
  vent: { letter: "V", chip: "bg-ink-400 text-paper-0", label: "vent" },
  sabotage: { letter: "⚡", chip: "hazard-stripe text-paper-0", label: "sabotage" },
};

// Clamp a pointer's clientX to a [0,1] fraction within an element's box.
function pointerFraction(clientX: number, rect: DOMRect): number {
  if (rect.width === 0) {
    return 0;
  }
  return Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
}

function fractionToIndex(fraction: number, lastIndex: number): number {
  return Math.round(fraction * lastIndex);
}

// A vertical crosshair / playhead line positioned by fraction across a relative
// parent. `now` is the solid playhead; `hover` is the dashed shared crosshair.
function Crosshair({ fraction, kind }: { fraction: number; kind: "now" | "hover" }) {
  return (
    <div
      aria-hidden
      className={
        "pointer-events-none absolute bottom-0 top-0 w-0 " +
        (kind === "now"
          ? "border-l-2 border-ink-900"
          : "border-l border-dashed border-ink-400")
      }
      style={{ left: `${(fraction * 100).toFixed(2)}%` }}
    />
  );
}

// A small letter+colour chip used as a key-moment dot / timeline marker.
//
// The hit target is enlarged past the 16px chip for touch (Task 12.13 a11y). In
// the roomy advantage graph that's a 24px square; in the cramped 16px event-lane
// rows (`compact`) the box is constrained to the lane HEIGHT (`inset-y-0`) so it
// never spills into the neighbouring agent's row and steals its click — it stays
// 24px WIDE for a comfortable horizontal target (Task 12.13 review).
function MarkerChip({
  letter,
  chip,
  title,
  fraction,
  onSeek,
  compact = false,
}: {
  letter: string;
  chip: string;
  title: string;
  fraction: number;
  onSeek: () => void;
  compact?: boolean;
}) {
  return (
    <button
      type="button"
      title={title}
      aria-label={title}
      onClick={(event) => {
        event.stopPropagation();
        onSeek();
      }}
      className={
        "absolute z-10 flex w-6 -translate-x-1/2 items-center justify-center " +
        (compact ? "inset-y-0" : "top-1/2 h-6 -translate-y-1/2")
      }
      style={{ left: `${(fraction * 100).toFixed(2)}%` }}
    >
      <span
        aria-hidden
        className={
          "flex h-4 w-4 items-center justify-center rounded-sm border border-ink-900 " +
          "font-mono text-4xs font-bold leading-none " +
          chip
        }
      >
        {letter}
      </span>
    </button>
  );
}

function BarShell({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="flex items-center gap-3">
      <span className="w-28 shrink-0 font-mono text-3xs uppercase tracking-wide text-ink-500">
        {title}
      </span>
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}

function PlaceholderBar({ title }: { title: string }) {
  return (
    <BarShell title={title}>
      <div className="flex h-10 items-center rounded-md border border-dashed border-ink-200 px-3 text-sm italic text-ink-500">
        Select a replay.
      </div>
    </BarShell>
  );
}

// ── Advantage graph — clickable second scrubber (DESIGN.md §4) ───────────────
export function AdvantageGraph() {
  const replay = useReplayStore((s) => s.currentReplay);
  const hoverTick = useReplayStore((s) => s.hoverTick);
  const setHoverTick = useReplayStore((s) => s.setHoverTick);
  const { frameIndex, lastIndex, seekToIndex, seekToTick } = usePlayback();
  const containerRef = useRef<HTMLDivElement>(null);

  const series = useMemo(() => advantageSeries(replay?.ticks ?? []), [replay]);
  const moments = useMemo(
    () => keyMoments(replay?.ticks ?? [], replay?.meetings ?? []),
    [replay],
  );

  if (replay === null || series.length === 0) {
    return <PlaceholderBar title="Advantage" />;
  }

  const ticks = replay.ticks;
  const points = series
    .map((point) => {
      const x = lastIndex > 0 ? (point.index / lastIndex) * 1000 : 0;
      // advantage +1 → top (y 0), -1 → bottom (y 100); 0 → midline (y 50).
      const y = (0.5 - point.advantage / 2) * 100;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  const nowFraction = lastIndex > 0 ? frameIndex / lastIndex : 0;
  const hoverFraction =
    hoverTick === null
      ? null
      : lastIndex > 0
        ? frameIndexForTick(ticks, hoverTick) / lastIndex
        : 0;

  const move = (event: ReactMouseEvent<HTMLDivElement>): void => {
    const rect = containerRef.current?.getBoundingClientRect();
    if (rect === undefined) {
      return;
    }
    const fraction = pointerFraction(event.clientX, rect);
    setHoverTick(tickNumberAt(ticks, fractionToIndex(fraction, lastIndex)));
  };
  const click = (event: ReactMouseEvent<HTMLDivElement>): void => {
    const rect = containerRef.current?.getBoundingClientRect();
    if (rect === undefined) {
      return;
    }
    seekToIndex(fractionToIndex(pointerFraction(event.clientX, rect), lastIndex));
  };
  // The slider's OWN keyboard contract (Task 12.13 a11y): Arrow/Home/End seek.
  // Stop propagation on the keys it handles so the global transport accelerator
  // (App KeyboardTransport) doesn't also fire and double-step; other keys (space
  // = play) fall through to it.
  const onKeyDown = (event: ReactKeyboardEvent<HTMLDivElement>): void => {
    let handled = true;
    switch (event.key) {
      case "ArrowLeft":
      case "ArrowDown":
        seekToIndex(frameIndex - (event.shiftKey ? 10 : 1));
        break;
      case "ArrowRight":
      case "ArrowUp":
        seekToIndex(frameIndex + (event.shiftKey ? 10 : 1));
        break;
      case "Home":
        seekToIndex(0);
        break;
      case "End":
        seekToIndex(lastIndex);
        break;
      default:
        handled = false;
    }
    if (handled) {
      event.preventDefault();
      event.stopPropagation();
    }
  };

  return (
    <BarShell title="Advantage ▲crew ▼imp">
      <div
        ref={containerRef}
        onMouseMove={move}
        onMouseLeave={() => {
          setHoverTick(null);
        }}
        onClick={click}
        onKeyDown={onKeyDown}
        role="slider"
        aria-label="Advantage graph — Arrow keys seek, click to jump"
        aria-valuemin={0}
        aria-valuemax={lastIndex}
        aria-valuenow={frameIndex}
        tabIndex={0}
        className="relative h-16 cursor-pointer rounded-md border border-ink-200 bg-paper-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ink-900"
      >
        <svg
          viewBox="0 0 1000 100"
          preserveAspectRatio="none"
          className="absolute inset-0 h-full w-full"
          aria-hidden
        >
          <rect x={0} y={0} width={1000} height={50} className="fill-trust-soft/10" />
          <rect x={0} y={50} width={1000} height={50} className="fill-distrust-soft/10" />
          <line
            x1={0}
            y1={50}
            x2={1000}
            y2={50}
            className="stroke-ink-300"
            strokeWidth={1}
            strokeDasharray="6 6"
            vectorEffect="non-scaling-stroke"
          />
          <polyline
            points={points}
            className="fill-none stroke-ink-700"
            strokeWidth={2}
            strokeLinejoin="round"
            vectorEffect="non-scaling-stroke"
          />
        </svg>
        {moments.map((moment) => {
          const style = KEY_MOMENT_STYLE[moment.kind];
          const fraction =
            lastIndex > 0 ? frameIndexForTick(ticks, moment.tick) / lastIndex : 0;
          return (
            <MarkerChip
              key={`${moment.tick}:${moment.kind}`}
              letter={style.letter}
              chip={style.chip}
              title={`${moment.kind} @ tick ${moment.tick}`}
              fraction={fraction}
              onSeek={() => {
                seekToTick(moment.tick);
              }}
            />
          );
        })}
        {hoverFraction !== null && <Crosshair fraction={hoverFraction} kind="hover" />}
        <Crosshair fraction={nowFraction} kind="now" />
      </div>
    </BarShell>
  );
}

// ── Event timeline — one lane per agent (DESIGN.md §2.3) ─────────────────────
export function EventTimeline() {
  const replay = useReplayStore((s) => s.currentReplay);
  const hoverTick = useReplayStore((s) => s.hoverTick);
  const setHoverTick = useReplayStore((s) => s.setHoverTick);
  const { frameIndex, lastIndex, seekToIndex, seekToTick } = usePlayback();
  const overlayRef = useRef<HTMLDivElement>(null);

  const markersByAgent = useMemo(() => {
    const grouped = new Map<string, ReturnType<typeof timelineMarkers>>();
    for (const marker of timelineMarkers(replay?.ticks ?? [])) {
      const lane = grouped.get(marker.agentId) ?? [];
      lane.push(marker);
      grouped.set(marker.agentId, lane);
    }
    return grouped;
  }, [replay]);

  if (replay === null) {
    return <PlaceholderBar title="Timeline" />;
  }

  const ticks = replay.ticks;
  const players = replay.players;
  const nowFraction = lastIndex > 0 ? frameIndex / lastIndex : 0;
  const hoverFraction =
    hoverTick === null
      ? null
      : lastIndex > 0
        ? frameIndexForTick(ticks, hoverTick) / lastIndex
        : 0;

  // Pointer → fraction within the TRACK column only. Returns null when the
  // pointer is over the row labels (left of the tracks) so clicking a label
  // doesn't clamp to 0 and seek to Start, and hovering one doesn't misplace the
  // crosshair.
  const fractionFromEvent = (event: ReactMouseEvent<HTMLDivElement>): number | null => {
    const rect = overlayRef.current?.getBoundingClientRect();
    if (rect === undefined || event.clientX < rect.left || event.clientX > rect.right) {
      return null;
    }
    return pointerFraction(event.clientX, rect);
  };

  return (
    <BarShell title="Event timeline">
      <div
        className="grid items-center gap-x-2 gap-y-0.5"
        style={{ gridTemplateColumns: "max-content 1fr" }}
        onMouseMove={(event) => {
          const fraction = fractionFromEvent(event);
          setHoverTick(
            fraction === null
              ? null
              : tickNumberAt(ticks, fractionToIndex(fraction, lastIndex)),
          );
        }}
        onMouseLeave={() => {
          setHoverTick(null);
        }}
        onClick={(event) => {
          const fraction = fractionFromEvent(event);
          if (fraction !== null) {
            seekToIndex(fractionToIndex(fraction, lastIndex));
          }
        }}
      >
        {players.map((player, row) => (
          <Fragment key={player.agent_id}>
            <div
              className="flex items-center gap-2 font-mono text-3xs text-ink-700"
              style={{ gridColumn: 1, gridRow: row + 1 }}
            >
              <span
                aria-hidden
                className="inline-block h-2.5 w-2.5 shrink-0 rounded-full ring-1 ring-ink-900/40"
                style={{ backgroundColor: player.color }}
              />
              {player.agent_id}
            </div>
            <div
              className="relative h-4 rounded-sm bg-paper-2/60"
              style={{ gridColumn: 2, gridRow: row + 1 }}
            >
              {(markersByAgent.get(player.agent_id) ?? []).map((marker) => {
                const style = TIMELINE_STYLE[marker.kind];
                const fraction =
                  lastIndex > 0 ? frameIndexForTick(ticks, marker.tick) / lastIndex : 0;
                return (
                  <MarkerChip
                    key={marker.key}
                    letter={style.letter}
                    chip={style.chip}
                    title={`${player.agent_id} — ${style.label} @ tick ${marker.tick}`}
                    fraction={fraction}
                    onSeek={() => {
                      seekToTick(marker.tick);
                    }}
                    compact
                  />
                );
              })}
            </div>
          </Fragment>
        ))}
        {/* Crosshair overlay spanning the track column across every lane.
            `self-stretch` overrides the grid's `items-center` so the overlay
            fills its full grid-area height — otherwise its only (absolutely
            positioned) children give it 0 height and the crosshair lines would
            be invisible. */}
        <div
          ref={overlayRef}
          className="pointer-events-none relative self-stretch"
          style={{ gridColumn: 2, gridRow: `1 / ${players.length + 1}` }}
        >
          {hoverFraction !== null && <Crosshair fraction={hoverFraction} kind="hover" />}
          <Crosshair fraction={nowFraction} kind="now" />
        </div>
      </div>
    </BarShell>
  );
}

// ── Transport — the control surface (DESIGN.md §4) ───────────────────────────
//
// `timelineOpen` / `onToggleTimeline` are the dock's disclosure: the shell owns
// whether the advantage graph and the event timeline are showing (it seeds that
// from the viewport height), and the transport carries the control that flips it,
// because the transport is the row that is always on screen.
export function ReplayControls({
  timelineOpen,
  onToggleTimeline,
}: {
  timelineOpen: boolean;
  onToggleTimeline: () => void;
}) {
  const autoFollow = useReplayStore((s) => s.autoFollow);
  const setAutoFollow = useReplayStore((s) => s.setAutoFollow);
  const {
    hasReplay,
    frameIndex,
    lastIndex,
    tickNumber,
    lastTickNumber,
    isPlaying,
    isAtStart,
    canStepBack,
    canStepForward,
    meetingAtTick,
    speed,
    setSpeed,
    seekToIndex,
    stepBy,
    togglePlay,
    jumpToEvent,
    jumpToMeeting,
    nextKeyMoment,
  } = usePlayback();

  return (
    <section
      aria-label="Replay transport"
      className="flex flex-wrap items-center gap-x-3 gap-y-2"
    >
      {/* Jump / step / play cluster. */}
      <div className="flex items-center gap-1">
        <button
          type="button"
          disabled={!hasReplay}
          onClick={() => {
            jumpToMeeting(-1);
          }}
          title="Previous meeting"
          aria-label="Previous meeting"
          className={BUTTON}
        >
          «M
        </button>
        <button
          type="button"
          disabled={!hasReplay}
          onClick={() => {
            jumpToEvent(-1);
          }}
          title="Previous event (kill / meeting / vent / sabotage)"
          aria-label="Previous event"
          className={BUTTON}
        >
          ‹e
        </button>
        <button
          type="button"
          disabled={!canStepBack}
          onClick={() => {
            stepBy(-10);
          }}
          title="Step back 10 ticks"
          aria-label="Step back 10 ticks"
          className={BUTTON}
        >
          −10
        </button>
        <button
          type="button"
          disabled={!canStepBack}
          onClick={() => {
            stepBy(-1);
          }}
          title="Step back 1 tick"
          aria-label="Step back 1 tick"
          className={BUTTON}
        >
          −1
        </button>
        <button
          type="button"
          disabled={!hasReplay || (!canStepForward && !isPlaying)}
          onClick={togglePlay}
          className={BUTTON + " min-w-[5rem] font-semibold"}
        >
          {isPlaying ? "⏸ Pause" : "▶ Play"}
        </button>
        <button
          type="button"
          disabled={!canStepForward}
          onClick={() => {
            stepBy(1);
          }}
          title="Step forward 1 tick"
          aria-label="Step forward 1 tick"
          className={BUTTON}
        >
          +1
        </button>
        <button
          type="button"
          disabled={!canStepForward}
          onClick={() => {
            stepBy(10);
          }}
          title="Step forward 10 ticks"
          aria-label="Step forward 10 ticks"
          className={BUTTON}
        >
          +10
        </button>
        <button
          type="button"
          disabled={!hasReplay}
          onClick={() => {
            jumpToEvent(1);
          }}
          title="Next event (kill / meeting / vent / sabotage)"
          aria-label="Next event"
          className={BUTTON}
        >
          e›
        </button>
        <button
          type="button"
          disabled={!hasReplay}
          onClick={() => {
            jumpToMeeting(1);
          }}
          title="Next meeting"
          aria-label="Next meeting"
          className={BUTTON}
        >
          M»
        </button>
      </div>

      {/* Scrubber + tick label. `value` is the array index; the label reads the
          engine tick number through the one selector.

          TWO CLOCKS. This readout is the ENGINE clock. An agent's own
          observation stamps sit one ahead of it, because a tick's packets are
          built from pre-advance state and recorded against the pre-advance tick
          (`orchestrator/game.py`, `input_tick` beside `advance_tick`). Measured
          on the committed sets: 111,283/111,283 memory sighting lines match
          world truth at Δ=−1 and 51.8% at Δ=0, while the meeting header's
          "It is tick N" matches this readout exactly in 771/771 calls. Every
          reviewer re-derived that by hand, so the note below states it on
          screen. The counts stay here and in `lib/copy.test.ts`, never in the
          copy; an engine-side re-stamp would delete the note outright. */}
      <div className="flex min-w-[12rem] flex-1 items-center gap-3">
        <input
          type="range"
          min={0}
          max={Math.max(0, lastIndex)}
          value={frameIndex}
          disabled={!hasReplay}
          aria-label="Seek tick"
          onInput={(event) => {
            seekToIndex(Number(event.currentTarget.value));
          }}
          onChange={(event) => {
            seekToIndex(Number(event.currentTarget.value));
          }}
          className="w-full cursor-pointer accent-ink-700 disabled:cursor-not-allowed"
        />
        <span className="whitespace-nowrap font-mono text-sm text-ink-900">
          {!hasReplay
            ? "—"
            : isAtStart
              ? "Start"
              : `t${tickNumber} / ${lastTickNumber}`}
          {meetingAtTick !== null && (
            <span className="ml-2 rounded-pill border-2 border-ink-900 bg-suspicion-2 px-2 py-1 text-xs font-semibold text-ink-900">
              meeting
            </span>
          )}
        </span>
      </div>

      {/* A SIBLING of the scrubber, not a child of it: the transport row wraps,
          so on a narrow bar the note drops to its own line instead of squeezing
          the seek control. */}
      <span
        title={TRANSPORT_COPY.agentClockTitle}
        className="whitespace-nowrap font-mono text-3xs text-ink-500"
      >
        {TRANSPORT_COPY.agentClockNote}
      </span>

      {/* Next key moment — distinct from raw step / jump-event. */}
      <button
        type="button"
        disabled={!hasReplay}
        onClick={nextKeyMoment}
        title="Seek to the next key moment (kill / meeting / ejection / sabotage)"
        aria-label="Next key moment"
        className={BUTTON}
      >
        ★ Next key moment
      </button>

      {/* Speed selector. */}
      <div className="flex items-center gap-1">
        <span className="mr-1 font-mono text-3xs uppercase tracking-wide text-ink-500">
          Speed
        </span>
        {SPEEDS.map((value) => {
          const isActive = speed === value;
          return (
            <button
              key={value}
              type="button"
              disabled={!hasReplay}
              aria-pressed={isActive}
              onClick={() => {
                setSpeed(value);
              }}
              className={
                "rounded-md border-2 border-ink-900 px-3 py-1.5 font-mono text-sm transition-colors " +
                "disabled:cursor-not-allowed disabled:opacity-40 " +
                (isActive
                  ? "bg-ink-900 text-paper-0"
                  : "bg-paper-0 text-ink-900 hover:bg-paper-2")
              }
            >
              {value}×
            </button>
          );
        })}
      </div>

      {/* The dock's disclosure. The NAME stays fixed and `aria-expanded` carries
          the state, so a screen reader hears "Timeline, collapsed" rather than a
          control that renames itself under the user; the chevron is the sighted
          half of the same signal. */}
      <button
        type="button"
        aria-expanded={timelineOpen}
        onClick={onToggleTimeline}
        title="Show or hide the advantage graph and the event timeline"
        className={BUTTON}
      >
        <span aria-hidden>{timelineOpen ? "▾" : "▸"}</span> Timeline
      </button>

      {/* Auto-follow toggle (interruptible meeting follow). */}
      <button
        type="button"
        aria-pressed={autoFollow}
        onClick={() => {
          setAutoFollow(!autoFollow);
        }}
        title="Auto-follow meetings while playing"
        className={
          "rounded-md border-2 border-ink-900 px-3 py-1.5 text-sm transition-colors " +
          (autoFollow ? "bg-ink-900 text-paper-0" : "bg-paper-0 text-ink-900 hover:bg-paper-2")
        }
      >
        Auto-follow {autoFollow ? "on" : "off"}
      </button>
    </section>
  );
}
