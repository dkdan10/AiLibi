// The cost / token chips (Task 19.17; audits/audit-phase-19-triage.md §7 item 18
// + singleton 29). What this game has spent in model calls, up to the frame you
// are watching.
//
// NO NEW SERVER DATA. The per-call counts are already in the replay bytes and
// already served: `MeetingView.llm_calls` carries `input_tokens` /
// `output_tokens` / `cost_usd` per call, and `ReplayView.failed_calls` carries
// the calls that were billed and then failed. The store's `windowReplay` strips
// only `prompt_text` / `response_text` from the bulk payload, so every number
// this file adds up is already in memory — no request, no `api/` change.
//
// FRAME-BOUNDED, and that is the whole design (the triage's unspoiled-mode
// rule). The chips sum meetings and failed calls at ticks AT OR BEFORE the
// current frame — never `metadata.total_cost_usd`. A game total would be an
// outcome-shape leak: it is a monotone proxy for how long the game ran and how
// many meetings it took, printed at frame zero before a tick has played. The
// difference is directly visible — at the Start frame these chips read 0, where
// a total would already read the whole game.
//
// The chips are perspective-INDEPENDENT by construction: they aggregate over
// meetings, which are public, and carry no player, room, role or outcome. There
// is nothing here for the fog to admit or withhold, so unlike the ticker beside
// them they render identically in both modes.

import { useMemo } from "react";

import { usePlayback } from "../hooks/usePlayback";
import { useReplayStore } from "../store/replayStore";
import type { FailedCallView, MeetingView } from "../types/api";

/** The cumulative model spend at one frame. */
export interface FrameCost {
  /** Completed calls recorded on meetings at or before the frame. */
  readonly calls: number;
  /** Calls that were billed and then failed (`ReplayView.failed_calls`). */
  readonly failedCalls: number;
  readonly inputTokens: number;
  readonly outputTokens: number;
  /** Dollars as RECORDED — see the `$0.0000` note on the component below. */
  readonly costUsd: number;
}

const ZERO_COST: FrameCost = {
  calls: 0,
  failedCalls: 0,
  inputTokens: 0,
  outputTokens: 0,
  costUsd: 0,
};

/**
 * Model spend accumulated up to and including ENGINE TICK `tickNumber`.
 *
 * Pure and exported so the frame-bounding is unit-pinnable. The comparison is on
 * ENGINE TICKS, never frame indices — the loader's synthetic Start frame is tick
 * `-1`, and every meeting is at tick `>= 0`, so the Start frame is zero by
 * arithmetic rather than by a special case.
 *
 * A failed call still spent money and still happened at a tick, so it is counted
 * in `costUsd` and surfaced separately rather than being quietly dropped
 * (AGENTS.md — no silent fallbacks); it contributes no tokens because a call
 * that failed recorded none.
 */
export function costToFrame(
  meetings: readonly MeetingView[],
  failedCalls: readonly FailedCallView[],
  tickNumber: number,
): FrameCost {
  let calls = 0;
  let inputTokens = 0;
  let outputTokens = 0;
  let costUsd = 0;
  for (const meeting of meetings) {
    if (meeting.tick > tickNumber) {
      continue;
    }
    for (const call of meeting.llm_calls) {
      calls += 1;
      inputTokens += call.input_tokens;
      outputTokens += call.output_tokens;
      costUsd += call.cost_usd;
    }
  }
  let failed = 0;
  for (const call of failedCalls) {
    if (call.tick > tickNumber) {
      continue;
    }
    failed += 1;
    costUsd += call.cost_usd;
  }
  return { calls, failedCalls: failed, inputTokens, outputTokens, costUsd };
}

function formatInt(value: number): string {
  return value.toLocaleString("en-US");
}

/** One chip. Mono value, muted label — the dense-data hairline, not chrome. */
function Chip({
  label,
  value,
  title,
}: {
  label: string;
  value: string;
  title?: string;
}) {
  return (
    <span
      title={title}
      className="inline-flex items-center gap-1 rounded-pill border border-ink-200 bg-paper-0 px-2 py-0.5"
    >
      <span className="font-mono text-4xs uppercase tracking-wide text-ink-500">
        {label}
      </span>
      {/* An explicit space so the chip's TEXT reads "in 0 tok" rather than
          "in0 tok" — the gap is CSS, and CSS is invisible to `textContent`, so
          without it the browser journey would have to assert on a string no
          reader would recognise. A whitespace-only child of a flex container is
          not rendered as a flex item, so the layout is unchanged. */}{" "}
      <span className="font-mono text-2xs text-ink-900">{value}</span>
    </span>
  );
}

/** The chip row. Renders nothing until a replay is open. */
export function CostChips() {
  const replay = useReplayStore((s) => s.currentReplay);
  const { tickNumber } = usePlayback();

  // `replay === null` is the only guard, and `meetings` / `failed_calls` are
  // read DIRECTLY off it. An `?? []` normalisation would be the worst possible
  // failure here: both are required fields of the versioned DTO, so a payload
  // missing one is incompatible, and defaulting it would print a confident
  // `0 tok · $0.0000` — a plausible false total, indistinguishable from the
  // genuine frame-zero reading. AGENTS.md: no silent fallbacks. Reading them
  // straight means an incompatible payload fails where a reader can see it.
  const cost = useMemo(
    () =>
      replay === null
        ? ZERO_COST
        : costToFrame(replay.meetings, replay.failed_calls, tickNumber),
    [replay, tickNumber],
  );

  if (replay === null) {
    return null;
  }

  return (
    <div
      role="group"
      aria-label="LLM cost to the current frame"
      className="flex flex-wrap items-center gap-1.5"
    >
      <span className="font-mono text-3xs uppercase tracking-wide text-ink-500">
        cost · to t{tickNumber}
      </span>
      <Chip
        label="calls"
        value={formatInt(cost.calls)}
        title="Completed model calls recorded at or before this frame"
      />
      <Chip label="in" value={`${formatInt(cost.inputTokens)} tok`} />
      <Chip label="out" value={`${formatInt(cost.outputTokens)} tok`} />
      <Chip
        label="usd"
        value={`$${cost.costUsd.toFixed(4)}`}
        // $0.0000 on the committed sample sets is a REAL recorded value, not a
        // missing one: the canonical eval provider is Featherless on a flat-rate
        // subscription, which the recorder stamps as $0 per call (AGENTS.md).
        // Say so rather than hiding a zero that looks like a bug.
        title="Recorded dollars. The committed sample sets were recorded on a flat-rate provider that bills $0 per call, so $0.0000 there is the recorded truth, not a missing value."
      />
      {cost.failedCalls > 0 && (
        <Chip
          label="failed"
          value={formatInt(cost.failedCalls)}
          title="Calls that were billed and then failed — counted in the dollars, no tokens recorded"
        />
      )}
    </div>
  );
}
