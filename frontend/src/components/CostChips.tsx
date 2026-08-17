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
  /**
   * Whether the token counters are the COMPLETE spend to this frame, or a lower
   * bound. False as soon as any failed call is in range — see `costToFrame`.
   * The dollars are unaffected: `FailedCallView.cost_usd` IS served.
   */
  readonly tokensComplete: boolean;
}

const ZERO_COST: FrameCost = {
  calls: 0,
  failedCalls: 0,
  inputTokens: 0,
  outputTokens: 0,
  costUsd: 0,
  tokensComplete: true,
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
 * (AGENTS.md — no silent fallbacks).
 *
 * ITS TOKENS ARE REAL BUT UNREACHABLE FROM HERE, and that asymmetry is disclosed
 * rather than papered over. `orchestrator.replay.FailedCallReplayEntry` REQUIRES
 * `input_tokens` / `output_tokens` — capturing exactly those burned tokens is
 * the row's stated reason to exist — and `eval/balance_eval.py::_cost_summary`
 * folds them into the eval token totals. The frontend cannot: the DTO projection
 * `api/replay_loader.py::_failed_call_view` does not carry them onto
 * `FailedCallView`, and `api/` is out of scope for Task 19.17 ("no new server
 * data — client-side data only"). So the token counters here are a LOWER BOUND
 * whenever a failed call is in range, and `tokensComplete` says so; the chips
 * render `≥` rather than presenting a partial figure as the game's token spend.
 *
 * Dormant on the committed sample sets, which contain zero `failed_call` rows —
 * but a false comment is not made true by being unreachable, and the honest
 * label is what stops the next reader trusting a number that is short.
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
  return {
    calls,
    failedCalls: failed,
    inputTokens,
    outputTokens,
    costUsd,
    // Keyed on the PRESENCE of a failed call, not on a token count: the DTO
    // does not carry the tokens, so "how short is this" is not knowable here.
    // Unknown-and-said-so beats a confident undercount.
    tokensComplete: failed === 0,
  };
}

function formatInt(value: number): string {
  return value.toLocaleString("en-US");
}

// The id the token chips point `aria-describedby` at when the figure is a lower
// bound. Module-scope constant, not `useId`: there is exactly one chip row in the
// workspace, and a stable literal keeps the association readable in the DOM.
const LOWER_BOUND_NOTE_ID = "cost-chips-lower-bound";

/** One chip. Mono value, muted label — the dense-data hairline, not chrome. */
function Chip({
  label,
  value,
  title,
  describedBy,
}: {
  label: string;
  value: string;
  title?: string;
  // Required-but-nullable rather than optional: `exactOptionalPropertyTypes`
  // rejects passing an explicit `undefined` to a `?:` prop, and the call sites
  // genuinely compute "described, or not" per render.
  describedBy: string | undefined;
}) {
  return (
    <span
      title={title}
      aria-describedby={describedBy}
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

  const tokenPrefix = cost.tokensComplete ? "" : "≥ ";
  const tokenTitle = cost.tokensComplete
    ? "Tokens recorded on completed model calls at or before this frame"
    : "A LOWER BOUND: a failed call in range burned tokens that the replay bytes record but the served DTO does not carry, so they cannot be counted here";

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
        describedBy={undefined}
      />
      {/* `≥` when a failed call is in range: its burned tokens are recorded in
          the replay bytes but are not projected onto `FailedCallView`, so this
          figure is a lower bound and must not be presented as the token spend.
          Reaching the real number means widening the DTO — `api/`, which this
          task is scoped out of.

          The `≥` alone is a symbol, not an explanation, and a `title` is not one
          either: a tooltip on a non-focusable span is unreachable by keyboard and
          is only a fallback DESCRIPTION for a screen reader. So the reason is
          rendered as VISIBLE text below and associated here — the qualifier
          travels with the number for every reader, and the `title` stays as a
          pointer convenience rather than the sole channel. */}
      <Chip
        label="in"
        value={`${tokenPrefix}${formatInt(cost.inputTokens)} tok`}
        title={tokenTitle}
        describedBy={cost.tokensComplete ? undefined : LOWER_BOUND_NOTE_ID}
      />
      <Chip
        label="out"
        value={`${tokenPrefix}${formatInt(cost.outputTokens)} tok`}
        title={tokenTitle}
        describedBy={cost.tokensComplete ? undefined : LOWER_BOUND_NOTE_ID}
      />
      <Chip
        label="usd"
        value={`$${cost.costUsd.toFixed(4)}`}
        // $0.0000 on the committed sample sets is a REAL recorded value, not a
        // missing one: the canonical eval provider is Featherless on a flat-rate
        // subscription, which the recorder stamps as $0 per call (AGENTS.md).
        // Say so rather than hiding a zero that looks like a bug.
        title="Recorded dollars. The committed sample sets were recorded on a flat-rate provider that bills $0 per call, so $0.0000 there is the recorded truth, not a missing value."
        describedBy={undefined}
      />
      {cost.failedCalls > 0 && (
        <Chip
          label="failed"
          value={formatInt(cost.failedCalls)}
          title="Calls that were billed and then failed. Their dollars ARE counted; their tokens are recorded in the replay bytes but not served on the failed-call DTO, which is why the token chips read ≥"
          describedBy={LOWER_BOUND_NOTE_ID}
        />
      )}
      {/* The `≥` explained in the open, for every reader: on screen, in the
          accessibility tree, and reachable without a pointer. It renders only
          when the qualifier applies, so the ordinary row stays a clean chip
          strip — and because it is real text inside the labelled group, a screen
          reader meets it whether or not it follows the `aria-describedby`. */}
      {!cost.tokensComplete && (
        <span
          id={LOWER_BOUND_NOTE_ID}
          className="font-mono text-3xs leading-snug text-ink-600"
        >
          ≥ token counts exclude a failed call&apos;s burned tokens — recorded in
          the replay, not served on the failed-call DTO. Dollars are complete.
        </span>
      )}
    </div>
  );
}
