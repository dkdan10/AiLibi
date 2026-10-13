# Normal-policy gameplay findings before synthesis

The coordinator preserved these findings from the gameplay worker's development
messages before combining them with the separately frozen code review. The worker
built the evaluation harness and inspected actual recorded trajectories; this is
source-aware gameplay verification, not a blind external review. Its observations
below precede the final adjacent-body and immediate-danger refinements. Final
source-bound measurements belong in the later checkpoint, not retroactively here.

The worker scanned ordinary policies on the canonical map with five players, one
impostor and two tasks per crewmate, seeds 0–15, capped at 80 ticks. Every control
ended naturally by tick 28. Seeds 0, 6, 7 and 14 covered repeated body meetings,
post-meeting continuation, urgent repair and task completion. Seed 1 was then
included to exercise a positive contextual self-report. These are selected
DEVELOPMENT inputs; no generalization claim or held-out designation is appropriate.

A concrete search gained useful information. In seed 6, p-2 saw p-1 enter STORAGE
at source tick 2, finished its current ENGINEERING task through tick 5, and searched
at tick 6. It actually moved to STORAGE, discovered the body and reported at tick
7. The ordinary control first reported a body at tick 15. The body came from a
real kill at tick 5; the search was based on the earlier owned sighting, never
knowledge of that hidden death. The reconstructed plan cleared for the report,
and normal policy continued after the meeting.

The cost was substantial in another case. Seed 14's task win moved from tick 26
to tick 41, and seed 6 completed four rather than six tasks while its game ran to
20 rather than 26. Search changed all four initial development trajectories;
changed behavior is not automatically better gameplay. The final comparison must
retain unmatched task completions and compare information over common horizons.

Contextual reporting needed a positive control. It matched ordinary behavior in
the initial four seeds, while unconditional reporting produced reports in all
four. Seed 1 supplied the missing case: the impostor and a crew member shared
ENGINEERING with a visible body and active kill cooldown. The impostor reported
at tick 8 before the later-ordered crew report, which the meeting discarded.
That demonstrates the finite decision table, not improved deception or survival.

The existing accompaniment option did not justify a new follow mechanism in the
initial four controls. Its changed paths mostly came from patrol fallback. A
same-owned-memory diagnostic found no moves distinct from old patrol in seeds 0,
6 or 7. Seed 14 selected one distinct follow move at terminal tick 26, leaving no
later decision that could use newly acquired information. The final matrix will
compare both old variants directly. A new three-tick follow version is deferred
unless a distinct information opportunity is demonstrated; search's positive
result does not establish that a follower adds value.

Fixed neutral speech and authored SKIP ballots isolate tactical mechanics. None
of these runs measures a fresh model's inference, accusation, voting, persuasion
or use of the new observations. The full source-bound capture and coordinator
verification follow these development findings. No adoption or main merge follows.
