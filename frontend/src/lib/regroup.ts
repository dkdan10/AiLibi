// The meeting regroup, as the map plays it.
//
// A recording made with `meeting_reset = "hub_with_grace"` ends every meeting
// that the game survives with a regroup (`engine/meeting_reset.py`): every
// survivor is moved to the meeting room, anyone inside a vent is pulled out and
// every body is cleared, all at once. No recorded frame shows the gathered
// state: the frame after a meeting already carries each survivor's first move
// of the next tick, so they stand in the meeting room or one corridor from it.
// The step between a meeting's frame and that frame is a gathering plus one
// move, not a walk from where the meeting found them, so tweening the tokens
// across the map would draw travel that never happened. On a `preserve`
// recording players resume where the meeting found them, and a single step
// still tweens.
//
// Pure functions over the view-model; `MapView` reads `shouldTween` and
// `regroupsAfterMeetings`, and `regroup.test.ts` pins them over hand-built
// steps and the committed skeleton dump.

import type { ExperimentConfigView } from "../types/api";

export type MeetingReset = ExperimentConfigView["meeting_reset"];

/** The slice of a `ReplayView` this module reads. */
export interface RegroupReplaySlice {
  readonly metadata: { readonly experiment_config?: Pick<ExperimentConfigView, "meeting_reset"> | null };
  readonly ticks: readonly { readonly tick: number }[];
  readonly meetings: readonly { readonly tick: number }[];
}

/**
 * Whether this recording regroups the survivors after each meeting. A missing
 * config is the historical default, `preserve`.
 */
export function regroupsAfterMeetings(replay: RegroupReplaySlice): boolean {
  return replay.metadata.experiment_config?.meeting_reset === "hub_with_grace";
}

/**
 * Whether moving the playhead from frame `from` to frame `to` crosses a
 * regroup: a single step, in either direction, between a meeting's frame and
 * the frame after it, on a recording that regroups. A longer scrub is never a
 * step and never tweens anyway.
 */
export function isRegroupStep(replay: RegroupReplaySlice, from: number, to: number): boolean {
  for (const index of [from, to]) {
    if (!Number.isInteger(index) || index < 0 || index >= replay.ticks.length) {
      throw new RangeError(`frame ${index} is outside this replay's ${replay.ticks.length} frames`);
    }
  }
  if (!regroupsAfterMeetings(replay) || Math.abs(to - from) !== 1) {
    return false;
  }
  const earlier = replay.ticks[Math.min(from, to)];
  return earlier !== undefined && replay.meetings.some((meeting) => meeting.tick === earlier.tick);
}

/**
 * Whether the map tweens tokens from frame `from` to frame `to`: a single step
 * between two frames of one replay, with motion allowed, that does not cross a
 * regroup. A playhead outside the replay's frames is not a step between two of
 * them, so it snaps.
 */
export function shouldTween(
  replay: RegroupReplaySlice,
  from: number,
  to: number,
  { sameReplay, reducedMotion }: { readonly sameReplay: boolean; readonly reducedMotion: boolean },
): boolean {
  const inRange = (index: number): boolean =>
    Number.isInteger(index) && index >= 0 && index < replay.ticks.length;
  return (
    sameReplay &&
    !reducedMotion &&
    Math.abs(to - from) === 1 &&
    inRange(from) &&
    inRange(to) &&
    !isRegroupStep(replay, from, to)
  );
}
