# Lab report — Vent-escape counterfactual (does hidden movement defang the detector?)

**Decision informed:** validate the model-ceiling probe's structural recommendation — is the impostor
catchable because it is *seen moving away from the kill* (a sighting trail that **vents** would hide), or
for some reason intrinsic to its lie? If the former, wiring the (already-implemented) vent action is the
direct structural fix for the deflection crater. **Date:** 2026-06-14. **Cost:** $0 (offline; no model
calls). **Harness:** `vent_escape_lab.py` over the committed 9p2i baseline (`replays/samples/9p2i` @
891234b).

**Method.** For every recorded meeting (96 meetings, 181 alive-impostor instances), simulate that each
impostor **vented at its earliest kill**: strip every `SawPlayerObservation` of that impostor with
`tick >= kill_tick` (the post-kill walk-away trail a vent hides), then re-run the production contradiction
detector on the real transcript. Upper bound — removes the whole post-kill trail, including
non-incriminating sightings. A real vent only hides movement between vent-connected rooms and emits a
`heard_vent_use` audible (a new, smaller tell), so realized benefit is somewhat less.

## Result — vents eliminate ~91% of the structured evidence against impostors

| | baseline | vent-escape | change |
|---|---|---|---|
| **impostor contradiction flags (total)** | **35** | **3** | **−32 (−91%)** |
| &nbsp;&nbsp;`alibi_vs_sighting` (weak) | 33 | 1 | −32 |
| &nbsp;&nbsp;`alibi_conflict` (strong) | 1 | 1 | 0 |
| &nbsp;&nbsp;`alibi_conflict` (weak) | 1 | 1 | 0 |
| crew flags (sanity — only impostor sightings removed) | 20 | 20 | 0 |
| **impostor-meetings carrying ≥1 flag** | **28/181 (15%)** | **3/181 (2%)** | **−25** |
| &nbsp;&nbsp;of the 28 flagged, go FLAG-CLEAN under vent | — | **25 (89%)** | — |

(154 post-kill impostor sightings removed across the set.)

**The impostor's structured catchability is ~91% sighting-trail-driven.** Every eliminated flag is
`alibi_vs_sighting` — the impostor's alibi colliding with *another player's first-hand sighting of it on
the walk-away path*. Hide that movement (a vent) and the detector has almost nothing: 25 of 28 flagged
impostors become entirely flag-clean. No model upgrade, prompt fix, or memory rewrite can do this — those
all *feed* the detector; the vent *starves* it, because it changes what information about the impostor
exists at all.

**The 3 survivors are a different bug.** They are `alibi_conflict` (self-pair) — the impostor contradicting
*its own* story across turns (opening vs reply drift). Vents don't fix that; a cover-consistency directive
does ("state the SAME room and window every time you are asked" — the exact text currently stranded on the
impostor *opening* template impostors never reach). So the residual after vents is a cheap prompt fix.

## Honest caveats (what this does and does NOT show)

1. **The removed flags are WEAK** (33/33 `alibi_vs_sighting` carry the weak-signal marker → sheltered by the
   §4.6 sub-gate). So the impostor was *already* partly sheltered, and the marginal effect on a *single*
   ejection is smaller than the 91% flag-count drop. The value is at the *accumulation* margin (the §6.3
   accumulator / testimony-fold can corroborate weak flags across rounds) and in the **flag-clean
   transition** (28→3 flagged): an impostor with zero structured evidence is far harder to convert than one
   carrying even weak flags.
2. **This is the DEFLECTION (R2) lever, not the BALANCE (R1/R5) lever.** It addresses why impostors get
   *caught in meetings*; it does NOT touch the **task clock**, which decides 49/49 crew wins. An
   un-catchable impostor still loses on the stopwatch unless it reaches parity faster. The full "interesting"
   fix is vents (deception works) **+** a task-clock lever (a sabotage that *gates tasks* — the current
   lights sabotage only degrades visibility and never stalls task progress — or the frozen-clock owner-call
   / win-condition structure) **+** score-the-rubric.
3. **Detector-side only.** This measures *others'* sightings. The impostor's own self-co-location narration
   (81% in the model-ceiling probe) also needs the memory change a vent implies (vented away → no "You
   discovered the body" line; see [[project-impostor-kill-memory-gap]]). A vent provides both; this test
   isolates the structured half.
4. **A vent adds its own tell:** `heard_vent_use` (room, no actor) is observable, so a careless vent near a
   witness is a *new catchable signal* — which is healthy (R2 "deception sometimes fails"), not a downside.

## Verdict

**Vents are validated as the direct structural fix for the deflection crater.** The impostor is caught
because it is *seen*, and ~91% of that structured evidence is the post-kill sighting trail hidden movement
would erase. This is the lever the model-ceiling probe pointed to: starve the detector of information
rather than try to out-talk it. Ship it with (a) the cover-consistency directive to kill the residual
self-pair drift, (b) the kill-memory rendering for the narration half, and (c) a separate task-clock lever
for *balance* — vents fix deception, not the stopwatch. All three are independently testable offline before
any re-record; wiring the vent action is an engine/determinism change (own task + regen fixtures) gated on
firewall + byte-replay integrity.
