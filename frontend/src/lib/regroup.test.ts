// The regroup snap: a single step across a meeting's regroup does not tween.
//
// A recording that regroups (`meeting_reset = "hub_with_grace"`) gathers every
// survivor in the meeting room between a meeting's frame and the next one, so
// that step snaps; a `preserve` recording still tweens it, and so does every
// other single step. The planted rule below drops the config check and fails
// the same assertions, which is what proves they read the config.

import { describe, expect, it } from "vitest";

import { isRegroupStep, type RegroupReplaySlice, regroupsAfterMeetings, shouldTween } from "./regroup";
import { readSkeleton, skeletonSet } from "./skeleton.testkit";

const SKELETON = readSkeleton();

/** Frames at ticks -1..6 with one meeting on tick 3 (frame index 4). */
function replay(reset: "preserve" | "hub_with_grace" | null): RegroupReplaySlice {
  return {
    metadata: { experiment_config: reset === null ? null : { meeting_reset: reset } },
    ticks: [-1, 0, 1, 2, 3, 4, 5, 6].map((tick) => ({ tick })),
    meetings: [{ tick: 3 }],
  };
}

const MEETING_FRAME = 4;
const MOTION = { sameReplay: true, reducedMotion: false } as const;

type StepRule = (replay: RegroupReplaySlice, from: number, to: number) => boolean;

/** The behaviour the map relies on, stated once so a planted rule can fail it. */
function assertRegroupSteps(rule: StepRule): void {
  const reset = replay("hub_with_grace");
  // Onto the first frame after the meeting, and back across it: no travel.
  expect(rule(reset, MEETING_FRAME, MEETING_FRAME + 1), "reset step").toBe(true);
  expect(rule(reset, MEETING_FRAME + 1, MEETING_FRAME), "reset step back").toBe(true);
  // Every other single step on the same recording is ordinary.
  expect(rule(reset, MEETING_FRAME - 1, MEETING_FRAME), "onto the meeting").toBe(false);
  expect(rule(reset, MEETING_FRAME + 1, MEETING_FRAME + 2), "after it").toBe(false);
  // A preserve recording, or one with no config (the historical default), never regroups.
  expect(rule(replay("preserve"), MEETING_FRAME, MEETING_FRAME + 1), "preserve step").toBe(false);
  expect(rule(replay(null), MEETING_FRAME, MEETING_FRAME + 1), "unconfigured step").toBe(false);
  // A two-tick scrub across the regroup is not a step.
  expect(rule(reset, MEETING_FRAME - 1, MEETING_FRAME + 1), "two-tick scrub").toBe(false);
}

describe("isRegroupStep", () => {
  it("snaps only the step across a regroup", () => {
    assertRegroupSteps(isRegroupStep);
  });

  it("would fail a rule that ignored the recording's config", () => {
    // Planted: the same rule with the config check dropped snaps the preserve
    // step too, and the assertions above catch it.
    const configBlind: StepRule = (slice, from, to) =>
      isRegroupStep(
        { ...slice, metadata: { experiment_config: { meeting_reset: "hub_with_grace" } } },
        from,
        to,
      );
    expect(() => assertRegroupSteps(configBlind)).toThrow(/preserve step/);
    // …and one that never snaps lets the reset step tween.
    expect(() => assertRegroupSteps(() => false)).toThrow(/reset step/);
  });

  it("raises on a frame outside the replay", () => {
    expect(() => isRegroupStep(replay("hub_with_grace"), 7, 8)).toThrow(RangeError);
    expect(() => isRegroupStep(replay("hub_with_grace"), -1, 0)).toThrow(RangeError);
  });

  it("reads the regroup off the recorded config", () => {
    expect(regroupsAfterMeetings(replay("hub_with_grace"))).toBe(true);
    expect(regroupsAfterMeetings(replay("preserve"))).toBe(false);
    expect(regroupsAfterMeetings(replay(null))).toBe(false);
  });
});

describe("shouldTween", () => {
  it("tweens a single ordinary step and snaps the regroup", () => {
    const reset = replay("hub_with_grace");
    expect(shouldTween(reset, 1, 2, MOTION)).toBe(true);
    expect(shouldTween(reset, MEETING_FRAME, MEETING_FRAME + 1, MOTION)).toBe(false);
    expect(shouldTween(replay("preserve"), MEETING_FRAME, MEETING_FRAME + 1, MOTION)).toBe(true);
  });

  it("snaps a scrub, another replay, reduced motion and a playhead off the end", () => {
    const reset = replay("hub_with_grace");
    expect(shouldTween(reset, 1, 3, MOTION)).toBe(false);
    expect(shouldTween(reset, 1, 2, { sameReplay: false, reducedMotion: false })).toBe(false);
    expect(shouldTween(reset, 1, 2, { sameReplay: true, reducedMotion: true })).toBe(false);
    expect(shouldTween(reset, 7, 8, MOTION)).toBe(false);
    expect(shouldTween(reset, -1, 0, MOTION)).toBe(false);
  });
});

describe("the regroup steps in the committed sets", () => {
  it("9p2i: one per meeting the game survives; 4p1i: none", () => {
    const steps = (name: string): number =>
      skeletonSet(SKELETON, name).games.reduce((sum, game) => {
        const { ticks } = game.replay;
        let found = 0;
        for (let index = 0; index + 1 < ticks.length; index += 1) {
          if (isRegroupStep(game.replay, index, index + 1)) found += 1;
        }
        return sum + found;
      }, 0);
    const survived = skeletonSet(SKELETON, "9p2i").games.reduce((sum, game) => {
      const last = game.replay.ticks[game.replay.ticks.length - 1]?.tick;
      return sum + game.replay.meetings.filter((meeting) => meeting.tick !== last).length;
    }, 0);
    // 117 meetings, 102 of them outlived by their game: the census's
    // "play resumes ..." cells read over the same 102.
    expect(survived).toBe(102);
    expect(steps("9p2i")).toBe(survived);
    expect(steps("4p1i")).toBe(0);
  });
});
