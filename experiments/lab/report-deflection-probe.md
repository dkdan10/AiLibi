# Lab report — Deflection probe (gp-2: does cover-on-reply lift deflection?)

**Decision informed:** whether the Phase-10 close audit's gp-1 (wire the v5 cover directive into the
impostor REPLY path) is worth a re-record. **Date:** 2026-06-14. **Model:** qwen3.5:9b, $0 local.
Within-impostor A/B over the committed Wave-2 baseline (replays/samples/9p2i @ 891234b) via
ReplayLoader; arm A = the production accusation_round reply prompt, arm B = the same + the gp-1 cover
directive injected (simulating the reply-template wiring). 40 reply contexts; **33 body-meeting A/B
pairs** usable (7 emergency meetings have no body, so no cover applies). Raw:
`results-deflection-probe.jsonl`.

## Result

| metric | A baseline | B cover-on-reply | delta |
|---|---|---|---|
| self-co-locates with the body | 18/33 | 7/33 | **−11** |
| self-alibi placed in the body room | 7/33 | 0/33 | **−7 (eliminated)** |
| mints a self-contradiction flag | 7/33 | **17/33** | **+10** |
| legal deflection (counter-accuse a living non-teammate) | 18/33 | 24/33 | +6 |

Within-pair: self-co-location **fixed 14 / broke 3**; legal-deflection **gained 13 / lost 7**.

## The finding (nuanced — it's both halves of the crater in one experiment)

**gp-1 IS a real behavior fix — the tuning gap is genuine and addressable.** The cover-on-reply
directive cut self-co-location ~60% (18→7), eliminated the impostor placing its own alibi in the body
room (7→0), and lifted legal deflection (+6). So the deflection crater is NOT primarily a model
ceiling at the *behavior* level — handed the directive on the reply turn, the 9B stops the dumb
self-incrimination and starts deflecting. The audit's D-1 (tuning-dominant) is confirmed.

**BUT it does NOT cleanly buy impostor SURVIVAL — the repaired detector eats the new lies.**
Self-flag minting went the WRONG way (+10). The mechanism: in arm A the impostor self-incriminates by
NARRATION ("I found the body") — text-suspicious but not a structured contradiction, so often no
detector flag. In arm B the directive pushes it to FABRICATE an away-from-body alibi — and a
fabricated alibi, checked against the real sightings in the transcript, MINTS a contradiction, because
the 9B cannot make its alibi consistent with what the other players actually observed (it doesn't know
their sightings — the model-ceiling residual the audit flagged at 15/71 wrong-subject alibis). The
directive trades "suspicious narration" for "catchable lie." Against THIS detector, trying to lie
better is risky.

## Verdict for the owner

1. **gp-1 is validated as an impostor-competence/legibility fix** (stops self-co-location, lifts
   deflection) — worth landing for game *quality*, and D-1's tuning verdict holds.
2. **gp-1 alone is NOT a balance lever.** The stronger crew detector catches the fabricated alibis it
   produces (+10 self-flags), so net impostor survival is ~a wash — exactly the audit's deeper point
   that the crew side out-paces the impostor side. **A re-record for gp-1 in isolation is not worth
   it.**
3. **Recommendation:** land gp-1 only PACKAGED with a balance lever (the frozen-clock owner-call gp-3,
   the sole lever the close audit found reaches a band), and treat "make deduction decide" as the
   Phase-11 win-condition-structure question (gp-7). This probe is the third independent confirmation
   that the binding constraint is crew/clock dominance, not impostor behavior — fixing the impostor's
   behavior just feeds the detector better.

So: the $0 probe did its job — it stopped a re-record that would have under-delivered. gp-1 ships with
a package or not at all; the balance answer is the clock and/or Phase-11 structure.
