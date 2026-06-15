# Lab report — Model-ceiling vs information-ceiling (qwen 7B → 9B → frontier)

**Decision informed:** the owner's question — "study qwen vs other up-to-date models to see *why* these
issues occur." Specifically: is the deflection crater (impostors win ~2%, self-incriminate when accused)
a **model ceiling** (a stronger model would fix it) or an **information ceiling** (no model can deflect
given the impostor's actual information)? **Date:** 2026-06-14. **Cost:** $0 (local Ollama) + frontier via
Claude subagents.

**Method.** 16 hard impostor *reply* contexts reconstructed from the committed Wave-2 baseline
(`replays/samples/9p2i` @ 891234b) — every one a meeting where a body was reported and an impostor must
answer. The **identical** production `accusation_round` reply prompt (baseline, no cover injection) was run
across a model-strength curve, graded by the same detector (`deflection_probe._grade`):

| metric | qwen2.5:7b (think=F) | **qwen3.5:9b (think=F, prod)** | qwen3.5:9b (think=T) | **Claude Opus (frontier)** |
|---|---|---|---|---|
| parsed OK | 16/16 | 16/16 | **0/16** (see below) | 16/16 |
| **legal deflection** (counter-accuse a living non-teammate) | **1/16 (6%)** | **10/16 (62%)** | — | **16/16 (100%)** |
| self-co-locates with the body (the *tell*) | 5/16 (31%) | 11/16 (69%) | — | **13/16 (81%)** |
| self-alibi placed in the body room | 2/16 (12%) | 5/16 (31%) | — | 9/16 (56%) |
| mints a *new* structured self-flag | 5/16 (31%) | 4/16 (25%) | — | 4/16 (25%) |

(The q9b arm reproduces the committed deflection-probe baseline behavior — self-co-locate 55–69%,
self-flag ~21–25% — validating the harness.)

## Finding 1 — a better model does NOT fix the crater; it makes the *tell* WORSE

The scaling curve is counterintuitive and decisive:

- **Deflection *competence* scales cleanly with model strength: 6% → 62% → 100%.** The 7B is nearly
  incapable of producing a legal counter-accusation; the 9B manages it ~62%; the frontier model does it
  *every time*. So the meeting-play *craft* genuinely improves with a stronger model — that part is a real
  model axis.
- **But the self-incrimination *tell* gets WORSE with model strength: 31% → 69% → 81% self-co-location**
  (and 12% → 31% → 56% placing the alibi *in the body room*). **The stronger the model, the more it
  self-incriminates.** Mechanism: a stronger model grounds its alibi faithfully in its own memory — and the
  impostor's memory says **"You discovered {victim}'s body in {room}."** A coherent, well-reasoned turn
  *anchors* on that body-discovery, which is precisely self-co-location. The 7B "escapes" co-location only
  by being too weak to build a coherent grounded alibi at all (it barely deflects, 6%). The **frontier
  model is the worst co-locator *because* it is the best reasoner** — it constructs the most internally
  consistent "I found the body" story, which is exactly the tell that gets an impostor caught.
- **The structured self-flag floor is ~25% and does not fall with model strength** (31% → 25% → 25%). No
  model breaks below ~a quarter, because it is lying into a detector fed by sightings it never saw; the
  frontier's careful transcript-alignment shaves the 7B's 31% to 25% but cannot break the floor.

**This is the empirical proof of the information ceiling.** A frontier model executes the deflection move
*flawlessly* (100% legal redirect, the lowest new-flag rate) and **still self-co-locates 81% of the time.**
It cannot reason its way out of an information position where its own memory says "you found the body here"
and it does not know which of the living players witnessed it. Better reasoning makes the impostor a more
*fluent* deflector while making the *catchable tell worse* — because the binding constraint is the
impostor's poisoned information, and smarter models reason more faithfully from poisoned information.

## Finding 2 — naive `think=True` breaks structured output entirely (0/16)

Turning qwen3.5:9b's reasoning channel on (the obvious response to "the model can't reason") **failed to
produce a single usable turn.** Confirmed mechanism (single diagnostic call): with `format`-schema
constraint + `think=True`, the model emits its JSON **into the thinking channel** (`len(thinking)=709`,
valid-looking JSON) while the answer `text` is **empty** (`len(text)=0`, 236 output tokens). The production
parse path reads `text` → empty → parse fails. So `think=False` is **load-bearing for the structured-output
path**; "just turn thinking on" is not a flag flip — it needs a different call architecture (parse the
thinking channel, or a two-phase reason-then-emit call). And tellingly, the one readable thinking-channel
turn **still self-co-locates** ("I was in ADMIN at tick 9–10" — ADMIN is the body room) — thinking does not
escape the information trap either.

## Verdict — the fix is STRUCTURAL (information), not a model upgrade

A model upgrade buys *fluency* (better redirects, slightly fewer minted contradictions) but **cannot** buy
*survival*, because the impostor is lying into a checker fed by information it provably lacks, and its own
kill is mis-rendered as a body discovery that co-locates it. Three independent lines now agree (this probe;
the deflection probe; the kill-memory probe): **impostor behavior/memory/model fixes feed the detector;
they do not change the information the lie must dodge.** The levers that actually touch the binding
constraint are structural — they change *what information exists and who controls it*:

1. **Fix the kill-memory rendering** (firewalled "You killed X in ROOM", not "You discovered X's body") —
   necessary for legibility, but the kill-memory probe showed it is **not sufficient alone** (self-flags
   17→17), because the impostor still doesn't know what *others* saw.
2. **Give the impostor information-SHAPING tools that are already built in the engine but never emitted:**
   - **Vents** (`engine/rules.py:102-179`, 6 vents in the map): hidden movement breaks the sighting trail,
     so the impostor *truthfully* has an away-from-body location the detector cannot contradict. This is the
     direct structural fix for the 81% co-location — give it a real alibi to tell.
   - **Sabotage / lights** (`engine/rules.py:225-245`, `canonical_1.yaml:370-376`): shrinks the crew's
     sighting graph (`same_room_only`), reducing the *quantity* of others' observations the lie must dodge.
   - **Self-report**: lets the impostor control the meeting opening it is currently barred from.
3. Only after the information environment is contestable does a stronger model (or a working reasoning
   channel) compound — fluent deflection over a *defensible* position. On the current frozen information, it
   does not.

This is the third independent confirmation that the deflection crater is crew/clock dominance + the
impostor's information disadvantage — and the first to **rule out a model upgrade as the lever** with a
head-to-head frontier comparison on identical contexts. Balance/interest must come from the structural
information economy (vents/sabotage/self-report, à la the genre) and/or the win-condition structure
(Phase 11), not from a better model.

**Harness/raw:** `model_ceiling_probe.py` + `results-model-ceiling-{q7b,q9b,q9b-think,frontier}.jsonl`
(frontier turns authored by Claude subagents on the identical prompts; raw in
`results-model-ceiling-frontier-turns.json`).
