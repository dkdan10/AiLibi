// Unit tests for the cost chips' frame-bounding (Task 19.17).
//
// The chips exist to be CHEAP and HONEST; the one way they could stop being
// honest is by printing the game total, which is a monotone proxy for how long
// the game ran and how many meetings it took — an outcome-shape statistic
// rendered at frame zero, before a tick has played. So the tests below are
// mostly one assertion said several ways: what has not happened yet does not
// count.

import { describe, expect, it } from "vitest";

import { START_TICK } from "../lib/playback";
import type { FailedCallView, LLMCallView, MeetingView } from "../types/api";
import { costToFrame } from "./CostChips";

function call(inputTokens: number, outputTokens: number, costUsd: number): LLMCallView {
  return {
    call_kind: "meeting",
    model: "Qwen/Qwen3.6-27B",
    prompt_template_id: "meeting_opening@3",
    // The store's `windowReplay` blanks both text fields on the bulk payload;
    // the counts survive, which is exactly what these chips read.
    prompt_text: "",
    response_text: "",
    input_tokens: inputTokens,
    output_tokens: outputTokens,
    cost_usd: costUsd,
    agent_id: "p-1",
  };
}

function meeting(tick: number, calls: LLMCallView[]): MeetingView {
  return {
    meeting_id: `m-${tick}`,
    tick,
    triggered_by: "p-1",
    trigger_kind: "body",
    outcome: "EJECTED",
    ejected_player_id: "p-4",
    turns: [],
    ballots: [],
    contradictions: [],
    llm_calls: calls,
    prompt_versions: {},
    total_cost_usd: calls.reduce((sum, entry) => sum + entry.cost_usd, 0),
    gate: { leader: "p-4", leader_max_confidence: 0.8, threshold: 0.6, passed: true },
  };
}

function failedCall(tick: number, costUsd: number): FailedCallView {
  return {
    meeting_id: `m-${tick}`,
    tick,
    model: "Qwen/Qwen3.6-27B",
    cost_usd: costUsd,
    error_type: "TimeoutError",
    error_message: "deadline exceeded",
  };
}

/**
 * A zero-spend `deadline_default` visibility marker
 * (`orchestrator/game.py::_record_deadline_defaults`): a deadline miss that
 * completed nothing, or a validation default whose real spend is already in
 * `llm_calls`. The sentinel `model` is what distinguishes it — both kinds carry
 * `error_type="deadline_default"`, so the error type cannot.
 */
function deadlineMarker(tick: number): FailedCallView {
  return {
    meeting_id: `m-${tick}`,
    tick,
    model: "(deadline_default)",
    cost_usd: 0,
    error_type: "deadline_default",
    error_message: "vote defaulted (deadline) for p-3",
  };
}

// Three meetings across a game, at ticks 7 / 14 / 35.
const MEETINGS: readonly MeetingView[] = [
  meeting(7, [call(1_000, 100, 0.01), call(2_000, 200, 0.02)]),
  meeting(14, [call(3_000, 300, 0.03)]),
  meeting(35, [call(4_000, 400, 0.04)]),
];
const NO_FAILURES: readonly FailedCallView[] = [];

// The game TOTAL, for contrast — the number these chips must never print.
const TOTAL_INPUT = 10_000;
const TOTAL_OUTPUT = 1_000;

describe("costToFrame", () => {
  it("is zero at the synthetic Start frame, where a total would be the whole game", () => {
    expect(costToFrame(MEETINGS, NO_FAILURES, START_TICK)).toEqual({
      calls: 0,
      failedCalls: 0,
      inputTokens: 0,
      outputTokens: 0,
      costUsd: 0,
      tokensComplete: true,
    });
  });

  it("counts a meeting AT the current tick — its calls happened to reach it", () => {
    const cost = costToFrame(MEETINGS, NO_FAILURES, 7);
    expect(cost.calls).toBe(2);
    expect(cost.inputTokens).toBe(3_000);
    expect(cost.outputTokens).toBe(300);
    expect(cost.costUsd).toBeCloseTo(0.03, 10);
  });

  it("excludes every meeting still in the future", () => {
    const cost = costToFrame(MEETINGS, NO_FAILURES, 20);
    expect(cost.calls).toBe(3);
    expect(cost.inputTokens).toBe(6_000);
    expect(cost.inputTokens).toBeLessThan(TOTAL_INPUT);
    expect(cost.outputTokens).toBeLessThan(TOTAL_OUTPUT);
  });

  it("reaches the game total only at the last frame — never before it", () => {
    const cost = costToFrame(MEETINGS, NO_FAILURES, 35);
    expect(cost.inputTokens).toBe(TOTAL_INPUT);
    expect(cost.outputTokens).toBe(TOTAL_OUTPUT);
    expect(cost.calls).toBe(4);
  });

  it("is monotone non-decreasing in the tick", () => {
    let previous = costToFrame(MEETINGS, NO_FAILURES, START_TICK);
    for (const tick of [0, 6, 7, 13, 14, 34, 35, 40]) {
      const cost = costToFrame(MEETINGS, NO_FAILURES, tick);
      expect(cost.calls).toBeGreaterThanOrEqual(previous.calls);
      expect(cost.inputTokens).toBeGreaterThanOrEqual(previous.inputTokens);
      expect(cost.outputTokens).toBeGreaterThanOrEqual(previous.outputTokens);
      expect(cost.costUsd).toBeGreaterThanOrEqual(previous.costUsd);
      previous = cost;
    }
  });

  it("counts a failed call's dollars and its count — never silently drops it", () => {
    const failures = [failedCall(9, 0.005), failedCall(40, 0.5)];
    const cost = costToFrame(MEETINGS, failures, 14);
    expect(cost.failedCalls).toBe(1); // the tick-40 failure is still the future
    expect(cost.costUsd).toBeCloseTo(0.06 + 0.005, 10);
  });

  it("marks the token counters INCOMPLETE once a failed call is in range", () => {
    // `FailedCallReplayEntry` requires `input_tokens` / `output_tokens` — the row
    // exists precisely to capture the tokens a crashed call already burned, and
    // `eval/balance_eval.py::_cost_summary` folds them into the eval totals. The
    // served `FailedCallView` does not carry them (`_failed_call_view` drops
    // them), so this surface CANNOT count them and must not present its figure
    // as the token spend. Widening the DTO is `api/` work, out of scope here.
    const failures = [failedCall(9, 0.005), failedCall(40, 0.5)];

    // Before the failure: complete, and the chips render a bare number.
    const before = costToFrame(MEETINGS, failures, 7);
    expect(before.tokensComplete).toBe(true);

    // At/after it: a LOWER BOUND, and the flag is what makes the chips say `≥`.
    const after = costToFrame(MEETINGS, failures, 14);
    expect(after.tokensComplete).toBe(false);
    // The counters still carry every token they legitimately know about — the
    // flag qualifies the number, it does not discard it.
    expect(after.inputTokens).toBe(6_000);
    expect(after.outputTokens).toBe(600);
    // …and the DOLLARS remain complete: `cost_usd` IS on the served DTO.
    expect(after.costUsd).toBeCloseTo(0.06 + 0.005, 10);
  });

  it("does NOT mark tokens incomplete for a zero-spend deadline marker", () => {
    // The marker records that nothing was spent, so the totals beside it are
    // EXACT. Flagging `≥` there would claim an undercount that does not exist —
    // the mirror image of the error the flag was added to fix.
    const cost = costToFrame(MEETINGS, [deadlineMarker(9)], 14);
    expect(cost.failedCalls).toBe(1); // still counted and surfaced
    expect(cost.tokensComplete).toBe(true); // …but the numbers are exact
    expect(cost.inputTokens).toBe(6_000);
    expect(cost.costUsd).toBeCloseTo(0.06, 10);
  });

  it("complete + a non-zero failed count implies EVERY in-range row is a marker", () => {
    // The implication the chip's copy and its `aria-describedby` both rely on:
    // when `tokensComplete` is true with failures present, the totals are exact
    // and the lower-bound note is not rendered — so the failed chip must not
    // claim a gap or point at a missing element. Asserted as a property over the
    // pure function rather than trusted from the component, since the chip row
    // itself is DOM and this suite is `environment: "node"`.
    const markersOnly = costToFrame(MEETINGS, [deadlineMarker(9), deadlineMarker(10)], 14);
    expect(markersOnly.failedCalls).toBe(2);
    expect(markersOnly.tokensComplete).toBe(true);

    // …and any real burned row in range breaks the implication, which is what
    // keeps the conditional honest rather than vacuous.
    const mixed = costToFrame(MEETINGS, [deadlineMarker(9), failedCall(10, 0.01)], 14);
    expect(mixed.failedCalls).toBe(2);
    expect(mixed.tokensComplete).toBe(false);
  });

  it("still marks tokens incomplete for a REAL burned call beside a marker", () => {
    // `_record_deadline_defaults` writes both kinds; a default carrying
    // `parse_failures` records real spend under its true model. Only the
    // sentinel model is exempt, so the discriminator has to be the model.
    const cost = costToFrame(MEETINGS, [deadlineMarker(9), failedCall(10, 0.02)], 14);
    expect(cost.failedCalls).toBe(2);
    expect(cost.tokensComplete).toBe(false);
  });

  it("keys incompleteness on the PRESENCE of a spend-bearing failed call", () => {
    // The DTO carries no tokens for a failed call, so "how short is this" is
    // unknowable here — even a zero-dollar failure has to flip the flag.
    const cost = costToFrame([], [failedCall(3, 0)], 5);
    expect(cost.failedCalls).toBe(1);
    expect(cost.tokensComplete).toBe(false);
    expect(cost.inputTokens).toBe(0);
  });

  it("stays complete for a game with no failed calls at all", () => {
    expect(costToFrame(MEETINGS, NO_FAILURES, 35).tokensComplete).toBe(true);
  });

  it("holds the recorded $0 of the flat-rate provider without inventing a price", () => {
    // The committed sample sets were recorded on Featherless, which the recorder
    // stamps as $0 per call (AGENTS.md). Real token counts, zero dollars — the
    // chips must show exactly that rather than back-filling a fallback price.
    const flatRate = [meeting(7, [call(3_091, 177, 0)])];
    const cost = costToFrame(flatRate, NO_FAILURES, 7);
    expect(cost.costUsd).toBe(0);
    expect(cost.inputTokens).toBe(3_091);
    expect(cost.outputTokens).toBe(177);
    expect(cost.calls).toBe(1);
  });

  it("is zero for a game with no meetings at all", () => {
    expect(costToFrame([], NO_FAILURES, 99).calls).toBe(0);
    expect(costToFrame([], NO_FAILURES, 99).costUsd).toBe(0);
  });
});
