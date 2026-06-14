# Lab report — Deception battery 2 (Tier 2, CREATIVE; the Wave-2 capability map)

**Decision informed:** the 10.14 impostor-toolkit design + the 10.16 A/B targeting baselines.
**Rubric:** R2 (deception works sometimes), R3 (arcs), R6 (upside). **Date:** 2026-06-13.
**Model:** qwen3.5:9b, production prompts + scaffolding directives, temp 0.4, contexts from the
committed Wave-1 baseline (replays/samples/9p2i @ 0ed6962) via ReplayLoader. ~80 calls, mechanical
grading. Raw: `results-deception-battery-2.jsonl`.

Battery 1 established: the 9B can't invent a lie (2/18 spontaneous) but performs a handed cover
(~92%, sheltered). This battery asks WHAT KIND of scripted deception works — five new angles.

## Results

**P1 — sustained cross-meeting framing (the seed-6 game-deciding skill).** n=12. Mean target
persistence **0.86**; held the SAME frame all 3 rounds in **7/12**; but the justification stayed
stable in only **7/12** — i.e., the model keeps naming the target but its *evidence* for the frame
drifts (room/tick shifts round to round). **Toolkit implication:** a "commit-to-frame" directive
works for TARGET persistence (the thing that decided seed-6) but needs the cover story PINNED, or the
drifting justification becomes the catchable tell. → 10.14 should mint the frame's *evidence* once
and reuse it, not regenerate per turn.

**P2 — adaptive redirect quality.** n=20 (15 redirected). Of legal-or-not redirects: **legal 9/15**
(matches battery 1's ~27% illegal — the id-hallucination class persists under pressure), **teammate
4/15** (firewall suppresses the ballot but not the urge), and of the legal ones, **smart-scapegoat
6** (already-accused or turned-the-tables-on-the-accuser). So when the 9B redirects legally, it's
*often* a sensible scapegoat (6/9 legal) — the deflection instinct is decent; the failure is
target *validity*, not target *choice*. → 10.14's deflection lever needs a legal-target guard
(reuse the roster validation), after which redirect quality is already usable.

**P3 — anticipatory alibi (THE HEADLINE — the invent-vs-perform bridge).** n=12. Baseline (no
scaffold) lies **2/12** (reproduces battery 1's "won't invent" — killers honestly self-place). With
a "you just killed, the body will be found, prepare your account" directive: lies **8/12**, of which
**7 survived a true witness sighting at weak-only (sheltered)** and **5 pre-empted the kill scene**
(named a different room than the kill room). **This is the load-bearing toolkit finding:** the 9B
does NOT need a cover handed to it verbatim — it only needs the GOAL stated ("prepare an account that
doesn't place you at the scene"), and it generates its own sheltered lie 67% of the time. → 10.14's
cover-story lever can be a *directive* ("anticipate the meeting, prepare an alibi away from your kill")
rather than a fully policy-authored script — cheaper and more flexible than battery 1 implied.

**P6 — tell detection (catchability).** n=12 (within P3). Lexical tells (hedging /
reasoning-relocation words): **0.00 vs 0.00** — the scripted lies carry NO hedge-word tells. BUT
length: the anticipatory lie runs **1.47×** the baseline length on average. **Implication:** scripted
lies are NOT catchable by hedge-lexicon, but the over-explanation (longer alibi free_text) is a
mild signal — and it's a design *tension*, not a free win: the catchability the rubric (R2) wants is
weak here. → a Wave-2 crew-side "verbosity/over-justification" signal is a *candidate* but unproven;
do not count on scripted lies being self-defeating.

**P5 — implicit teammate corroboration within the firewall.** n=11. **Supports the teammate 7/11**
(mentions/places them in the injected room), **contradicts 0**, **mentions 7/11** — so handed a
teammate's alibi, the impostor will back it cleanly most of the time. **Firewall:** 1/11 still
ACCUSED the teammate despite the explicit "never accuse {tid}" directive — the 7.12 ballot/accusation
firewall would catch it at the engine layer, but it confirms the prompt-level instruction is not
self-sufficient (the deterministic guard remains load-bearing). → 10.14 coordination lever works at
the directive level; keep the firewall guard inviolate.

## Net for Wave 2

1. **The toolkit is even more tractable than battery 1 implied.** The decisive P3 result — the 9B
   generates its OWN sheltered lie from a stated GOAL (67%), not just a handed script — means 10.14's
   cover-story lever can be a lightweight directive, not a full policy-authored script generator.
2. **Sustained framing is the highest-value lever** (it decided the only impostor-skill game), works
   for target persistence, but **the frame's evidence must be pinned once** or the drift (P1: 5/12
   justification-unstable) becomes the tell.
3. **Deflection quality is fine once legal** — the fix is a legal-target guard, not better targeting.
4. **Coordination works at the directive level; the firewall guard stays load-bearing** (1/11 leaked).
5. **Don't bank on scripted lies being catchable** — no hedge tells; only a mild length signal (R2's
   "sometimes fails" is weaker than hoped; a crew-side verbosity signal is an unproven candidate).

These feed the 10.13 capability map and the 10.14 toolkit contract directly. The A/B baselines to
beat: P3 baseline-lie 2/12, P2 legal-redirect 9/15, P1 justification-stable 7/12, P5 firewall-leak
1/11.
