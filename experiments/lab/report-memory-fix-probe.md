# Lab report — Kill-memory validation probe (does "you killed X" memory fix deflection?)

**Hypothesis tested (owner question, 2026-06-14):** an impostor's own kill is never recorded as a kill —
`engine/rules.py:96` excludes the killer from its own kill's witnesses, so the only trace is a cooldown
tick, and the body it created surfaces through the ordinary `saw_body` channel as
`You discovered p-X's body` (see [[project-impostor-kill-memory-gap]]). The conjecture was that this
mis-rendering is the deflection-crater root cause: the 9B narrates "I found the body" (self-co-locating),
and the gp-1 cover directive backfires (+10 self-flags in `report-deflection-probe.md`) because the
directive ("alibi AWAY from the body") *fights* a memory that says "you discovered the body HERE". The
predicted fix: surface the impostor's own kill as an explicit privileged self-channel line
(`You (IMPOSTOR) killed X in ROOM`) so the model has a real kill location to build a consistent cover
away from — predicted to make gp-1 land **and** drop the self-flags.

**Design.** $0 within-impostor A/B over the committed Wave-2 baseline (`replays/samples/9p2i` @ 891234b),
`qwen3.5:9b`, 40 impostor reply contexts. **Both arms carry the gp-1 cover directive** — the only
difference is the memory rendering of the impostor's OWN kills:
- **A** = cover on the CURRENT memory (`You discovered X's body` — the backfire condition).
- **B** = cover on a KILL-EXPLICIT memory (`You (IMPOSTOR) killed X in ROOM`, rewriting the own-victim
  "discovered body" lines via `_kill_explicit_memory`; own-kill rooms/ticks taken from the extractor
  facts).

So this isolates *exactly* the proposed memory fix, on top of the cover. Headline metric: does
`new_self_flag` (a structured detector contradiction minted on the speaker) **DROP** in B vs A? Raw:
`results-memory-fix-probe.jsonl`. All 80 calls parsed (A=40/40, B=40/40). 39/40 contexts have an
own-kill; 33 have a body this meeting; **n=32** carry both (cover + kill-explicit, both arms parsed) —
the decisive population.

## Result — the fix does NOT work

| metric (n=32, cover + kill-explicit) | A (discovered-body mem) | B (kill-explicit mem) | delta |
|---|---|---|---|
| **mints a self-contradiction flag** | **17/32** | **17/32** | **±0 (no drop)** |
| self-co-locates with the body | 6/32 | 10/32 | +4 (worse, noisy) |
| self-alibi placed in body room | 0/32 | 0/32 | 0 (cover kills it in both) |
| legal deflection (counter a living non-teammate) | 23/32 | 22/32 | −1 (flat) |

Within-pair on the headline: self-flag **improved 4 / worse 4** (13 flag in both arms regardless, 11
clear in both). A coin-flip — **no systematic effect.** Across all 39 kill-bearing contexts the picture
is the same or slightly negative (self-flag 22→23, deflection 27→24).

**Verdict: the kill-memory fix does NOT reduce self-flagging and does NOT lift deflection.** The
hypothesis that it "avoids the +10 self-flag backfire and makes gp-1 land" is **falsified** by this probe.

## Why it fails (grounded in the transcripts)

1. **Self-flags come from the alibi contradicting OTHERS' sightings, not from the impostor's own
   memory.** A flag fires when the fabricated alibi clashes with what other players observed —
   information the impostor lacks in *both* arms. Giving it a truthful self-location doesn't help,
   because the cover still requires it to *lie* about that location, and the lie is caught by others'
   sightings just the same.
   > BOTH-FLAG (p-8 killed p-7 in ADMIN): A claims "CAFETERIA tick 9–10", B claims "CAFETERIA, no memory
   > of ADMIN" — both flag, because a sighting puts p-8 elsewhere. The kill-explicit line changed nothing
   > about the catchable part.

2. **The triggering body is usually NOT the impostor's own kill,** so the kill-explicit rewrite and the
   cover concern *different rooms* — they never combine into "one consistent cover." The impostor killed
   earlier (or a teammate's kill triggered the meeting); the cover keys off the new body while the
   rewrite keys off the old victim.
   > p-4 killed p-6 in STORAGE (tick 7), but THIS meeting's body is p-8 in EAST_HALL — the rewrite and
   > the cover are about unrelated rooms.

3. **Naming the kill room+victim can DRAW the model toward the body, not away.** In the clearest
   regression, the explicit "you killed p-4 in ADMIN" line made the model narrate *"I found p-4's body
   there at tick 9"* and place itself in ADMIN — reverting to the exact self-co-location the fix was
   meant to prevent.
   > WORSE case (p-7, body=ADMIN=own kill): A "CAFETERIA, far from ADMIN" (no flag) → B "I found p-4's
   > body there… in CAFETERIA tick 8–9" (flag + co-locate). The explicit kill line backfired.

4. The fix **only** helps in the narrow case where the triggering body IS the impostor's own kill AND
   the fabricated alibi happens to dodge real sightings — rare and luck-dependent (the single clean
   IMPROVED pair: p-3, body=MEDBAY=own kill, B built a clean ADMIN alibi). Not a reliable lever.

## Verdict for the owner

1. **The kill-memory gap is real and worth fixing for LEGIBILITY** — "I, the killer, discovered the
   body" is an absurd, immersion-breaking narration, and a firewalled self-channel kill line is the
   correct rendering. Keep it as an impostor-competence/quality item.
2. **But it is NOT the deflection-survival lever the hypothesis predicted.** Against this detector,
   self-flagging is a wash (17→17) and deflection is flat — the kill-memory rendering is *not* what
   craters deflection. The crater's behavior half is the **model ceiling** (the impostor can't reconcile
   its alibi with sightings it never saw), exactly as `report-deflection-probe.md` concluded; truthful
   self-location doesn't close that gap because the gap is about *others'* information.
3. **This is the THIRD independent confirmation** (audit D-1, deflection probe, this probe) that impostor
   *behavior/memory* fixes feed the detector rather than buy survival. The binding constraint is
   crew/clock dominance + the impostor's information disadvantage — **not** memory rendering. The balance
   answer remains the frozen-clock owner-call (gp-3) and/or the Phase-11 win-condition-structure question
   (gp-7); kill-memory + gp-1 ship as a *legibility package*, never as a balance fix.

So the $0 probe again did its job: it **falsified a plausible root-cause fix before any re-record.** The
kill-explicit memory makes the impostor *honest with itself*, but the detector punishes the lie it must
still tell — and it must tell that lie because it doesn't know what the crew saw.
