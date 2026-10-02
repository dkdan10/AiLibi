// The regroup snap: a single step across a meeting's regroup does not tween.
//
// A recording that regroups (`meeting_reset = "hub_with_grace"`) gathers every
// survivor in the meeting room between a meeting's frame and the next one, when
// the game outlives the meeting, so that step snaps; a `preserve` recording still tweens it, and so does every
// other single step. The planted rule below drops the config check and fails
// the same assertions, which is what proves they read the config.

import { describe, expect, it } from "vitest";

import { MAP_COPY } from "./copy";
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
  expect(rule(reset, MEETING_FRAME, MEETING_FRAME + 2), "two-tick scrub from the meeting").toBe(false);
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
    expect(() => isRegroupStep(replay("hub_with_grace"), 7, 8)).toThrow(/^frame 8 is outside this replay's 8 frames$/);
    expect(() => isRegroupStep(replay("hub_with_grace"), -1, 0)).toThrow(RangeError);
    expect(() => isRegroupStep(replay("hub_with_grace"), 3.5, 4.5)).toThrow(RangeError);
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
    expect(shouldTween(reset, 1.5, 2.5, MOTION)).toBe(false);
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

describe("the regroup note against the committed sets", () => {
  /** Every meeting no later frame follows: the game ended at it, so no regroup came. */
  const endingMeetings = (name: string): string[] =>
    skeletonSet(SKELETON, name).games.flatMap((game) =>
      game.replay.meetings
        .filter((meeting) => !game.replay.ticks.some((frame) => frame.tick > meeting.tick))
        .map((meeting) => meeting.meeting_id),
    );

  /**
   * The note may speak of the gathering only for the meetings play resumes
   * from: a recording with a meeting that ends its game refutes a note that
   * says every meeting ends in one.
   */
  function assertNoteHolds(note: string, ending: readonly string[]): void {
    if (ending.length > 0 && /\b(every|each) meeting\b/i.test(note)) {
      throw new Error(`the note claims every meeting, but ${ending.length} end the game with no frame after`);
    }
    if (!note.includes("whenever play resumes after a meeting")) {
      throw new Error("the note does not limit itself to the meetings play resumes from");
    }
  }

  it("speaks only of the meetings play resumes from", () => {
    const ending = endingMeetings("9p2i");
    // 117 meetings, 102 outlived (the step census above), 15 that end their
    // game. The featured head's third meeting is one: its frame at tick 44 is
    // the recording's last.
    expect(ending).toHaveLength(15);
    expect(ending).toContain("headless-seed-19:meeting-2");
    const head = skeletonSet(SKELETON, "9p2i").games.find((game) => game.gameId === "headless-seed-19");
    if (head === undefined) throw new Error("the featured head is not in the skeleton");
    const third = head.replay.meetings.find((meeting) => meeting.meeting_id === "headless-seed-19:meeting-2");
    expect(third?.tick).toBe(44);
    expect(head.replay.ticks[head.replay.ticks.length - 1]?.tick).toBe(44);
    expect(head.replay.ticks.filter((frame) => frame.tick > 44)).toHaveLength(0);
    assertNoteHolds(MAP_COPY.regroupNote, ending);
  });

  it("would refute the earlier note that every meeting ends gathered", () => {
    // Planted: the note as first shipped, which the 15 game-ending meetings falsify.
    const earlier =
      "On this recording every meeting ends with the survivors gathered in the meeting room and the bodies cleared, so the map jumps to where they stand on the next tick.";
    expect(() => assertNoteHolds(earlier, endingMeetings("9p2i"))).toThrow(/claims every meeting, but 15 end/);
    // A recording with no game-ending meeting could not refute it on that count.
    expect(() => assertNoteHolds(earlier, [])).toThrow(/does not limit itself/);
  });
});
