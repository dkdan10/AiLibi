# Phase-21 hardening pass — does the gameplay read logically on baseline 8, and under the slate baseline 9 adopts?

**Dates:** 2026-09-01 → 2026-09-02. **Tree:** `main` at `38b680f0` throughout; PR #419 (the pre-registration)
open at the owner's gate for the whole pass, its head moving `5526e7b8` → `a59d6fbc` → `83580b58` by this pass's
own two commits, then merged at `5ae452d8` on the owner's delegation after the orchestrator ruled on every
open Question (§3.3). **Commissioned by:** the owner's directive at the Fable 5.1 seat hand-off — harden the phase
with fresh eyes, covering everything, with emphasis on how the gameplay reads logically. **Run by:** the
orchestrator (every ruling and this synthesis) over Opus workers: one extractor, sixteen reading lenses in
two waves, five more in a second round, one collator, one adversarial refuter per finding and an
independent re-deriver on every finding that could move an amendment or the pre-registration, one
completeness critic, one register assembler. Everything below is `$0`, offline, over committed bytes; no
model was called and no replay was written.

## 0. The verdict in one paragraph

The machinery is honest and the OFF game reads coherently: 7,271 of 7,271 recorded prompts reproduce
byte-for-byte, the finale and the gate readout tell the truth, every discarded action, double-minted vent and
oracle-voice line the phase set out to repair is gone in situ, nobody ever accuses a dead player, and the
memory a speaker sees matches the engine on all 32,088 single-tick sighting lines. **What does not read
logically is concentrated in three places.** (1) The Wave-2 lever blocks — the prose the adopting record will
render on every ballot and speech turn — say things their own machinery contradicts on the same page: a
source-count line that denies "the evidence above" beneath a transcript that names the accused, a kill
mandate that "outranks even a vent" one line after "one exception, and only one", a confidence ladder beside
a Proof paragraph that contradicts it, a header that promises eyewitnesses and delivers accusers, and a
co-discoverer line that places 57 impostors in a room they were not in. Nine such defects are verified twice
each and are being amended before the record (PR-1); two more need the ledger's grounding semantics changed
and are the owner's decision (PR-2). (2) The reporter railroads mostly stand on charges the exculpation block
does not reach — laundered "impossible transit" claims and hearsay piles — and a living impostor's ballot is
the deciding vote in 16 of the 46 innocent ejections; these bound what the levers can move and are recorded
as reading notes for the record audit, not as bar changes. (3) Substrate defects outside the levers that the
freeze forbids repairing before the record: a vent witnessed on the report tick never reaches that meeting
(40 of 40 same-tick witness pairs; four of the 46 innocent ejections), a departure is credited to whoever stands in the room a
tick later (12% of move lines), and 136 self-placements are mis-copied from the speaker's own route and then
correctly prosecuted. **One structural fact bounds all three levers**: they add zero bytes to the ballot's
belief block, whose `this meeting` term already separates the wrongful convictions (silent on the ejectee
in 90 of 150 convicting ballots) and already exculpates the reporter numerically; the levers act only on
the prose a voter writes, never on the number the ballot tells the voter to trust over rhetoric. Nothing
found moves a bar. One clarification and three Questions went to the pre-registration before the owner's
merge; two committed records get errata; the rest is routed to the contracts that own it and to the close
ledger. The 333 proof-present convictions — the majority regime — read coherently end to end.

## 1. Method

### 1.1 The dossier (one Opus extractor; every assertion machine-checked)

Over the four baseline-8 sets — 300 games, 672 meetings, 3,631 turns, 3,631 ballots, 645 contradiction
flags, 7,271 recorded LLM calls:

| assertion | result |
|---|---|
| every recorded `llm_calls[].prompt` reproduced byte-for-byte by the reconstruction walk (`tests/meetings/test_prompt_byte_golden.py::walk_replay_meetings`) | **7,271 / 7,271** (nine are manager-side opening retries whose recorded prompt is base + feedback; all reproduced) |
| the injustice ledger re-derived through `scripts/counterfactual_phase21.py`'s own fold equals `audits/audit-phase-21-counterfactual.md` §2.3 | **46 / 46 rows**, tags and tallies exact |
| each TURN prompt's `<memory>` block equals `ReplayLoader.get_meeting_memory().rendered_memory_text` | **3,631 / 3,631**; 1,443 BALLOT blocks differ only by the pre-vote suspicion override (`meetings/manager.py:685`), a documented rendering rule |
| the lever-ON renders (the 21.24 slate: `reporter_reasoning`, `corroboration_discipline`, `testimony_shapes` ON; `impostor_roll_call` OFF) | 7,262 captures re-rendered per leg with the counterfactual's own `_on_kwargs` / `_ledger_for`; all eight lever subsets on 70 meetings; no `AILIBI_*` variable ever assigned |
| engine ground truth per tick (rooms, applied / rejected / discarded actions, kills, vents, reports, discoveries) | re-walked from seed through `advance_tick`, every `state_hash` verified |

### 1.2 The lenses

Wave 1 (no dossier needed): the spectator surface and front door against the bytes; a mechanical protocol
census over every meeting; a static composition read of the six lever templates across all 16 subsets (192
composed prompts). Wave 2 (over the dossier): the 46 innocent ejections read twice each — the OFF record as
a spectator, then the ON renders as prose (four readers); chain-of-inference walks over a stratified
24-meeting sample of non-injustice meetings (two readers); six whole games read across meetings; the
corroboration block checked clause by clause on every one of the 3,614 slate ballots; the reporter and
testimony blocks checked against the engine on every speech and opening render; rendered memory read line
by line against the engine for 30 (agent, meeting) pairs (two readers); the impostor's play as a deceiver.
Round 2 (the completeness critic's gaps): the oracle regime as prose, belief movement from speech, the two
4p1i sets as prose, the 7,262 recorded responses, and pair-only lever interactions across the eight subsets.

### 1.3 Verification

145 raw findings → 91 register entries (53 merged, 1 dropped) → one adversarial refuter per entry (default
REFUTED) plus an independent re-deriver, measuring the predicate over the whole population, on every entry
routed amendment-before-record or question-on-419. Verdicts: **91 ADJUSTED, 3 CONFIRMED, 11 REFUTED** over
105 verifier runs (the eleven time-sensitive Wave-1 findings were verified first, in the same two-lens
shape). ADJUSTED means the core observation reproduced and the claim, a number, the severity or the route
was corrected; every corrected number below is the verifier's, not the lens's. A completeness critic then
named eight gaps; five became a second round (32 findings, one refuter each: **27 ADJUSTED, 4 CONFIRMED,
1 REFUTED**), two became Questions on the pre-registration (§3.3), and one was answered from the code (§5).

## 2. What reads logically — the clean reads

Stated with coordinates, because a clean read is a result. Every item below was re-derived by the lens that
filed it and survived the pass.

**The OFF machinery holds byte-for-byte and the protocol is clean.** Ten mechanical protocol checks over
672/672 meetings return zero violations: chain termination, opt-in eligibility, the roll-call tail, the
living-player cap, no ballot by a dead voter, no living voter missing, tally arithmetic against the 0.6 gate.
Citation integrity is 1,865/1,865 turn citations and 646/648 observation citations present verbatim in the
citing voter's own prompt, with no cross-ballot channel (the token `"target"` appears 0 times before
`<output_format>` in 3,584 ballot prompts). Nobody ever accuses a dead player: 0 of 3,114 accusations and 0
of 3,631 ballot targets. Every `vent_sighting` flag names an impostor (453/453). 620/620 body-report openings
name the corpse the engine's applied `report` named; no body is reported twice.

**The five Wave-1a repairs hold in situ, not just in pins.** Discarded and rejected actions are never
remembered as done (2,365/2,365 "You completed" lines match an engine `TaskCompleted`; the hardest case,
`ml_corpus/9p2i` 1000:m0 p-8 with four rejected tasks, a rejected kill and a discarded move, renders none of
them). The belief line's "last seen" is the argmax over the agent's own sightings on 8,866 of 9,610 rows, and
all 50 stale rows are impostor→teammate rows the §4.7 firewall withholds by design. Every witnessed vent is
minted once (793/793 lines match an engine vent event with the owner in its witness set; 0 duplicates). The
oracle voice is gone: `certified`, `detector`, `WEAK`, `STRONG`, `band` occur in 0 of 7,262 OFF and ON
prompts. Structured testimony survives to the next meeting as hedged, attributed `CLAIM by p-N (unverified)`
lines, correctly dated.

**Memory matches the engine.** All 32,088 single-tick and 9,471 coalesced sighting lines across 3,631
renders are true under the role-parameterised visibility; all 1,703 body-discovery lines match that tick's
body visibility; all 32 witnessed-kill lines match an engine `Killed` with the owner among the witnesses.
Speech is mostly faithful to the render: 3,142 of 3,824 spoken `saw_player` rows match a memory line exactly
and 279 more are off by one tick; 506/508 `saw_vent` and 822/824 `found_body` rows match exactly. Hard
fabrication of a sighting is 8 of 3,880. The impostor's own-kill line is present and its own victim's
discovery line suppressed in 936/936 impostor renders; the teammate firewall holds on both guarded channels
(0 of 798 impostor accusations and 0 of 936 impostor ballots name a teammate).

**Cross-meeting memory is exemplary.** Every post-first-meeting render carries a "Meetings so far" line
naming the ejectee, the tally, the ejectee's true role and the remaining impostor count, and renders a skip
as unresolved. A held vent survives across meetings and convicts correctly (`ml_corpus/9p2i` 1003: the m0
railroad target survives an 8-0 skip and cashes the sighting at m1). A claim carried across two meetings
does not drift (1008, p-8's two `saw_move` rows, both engine-true).

**The reporter block is engine-correct everywhere it renders.** 620/620 openings name the right victim in
the right room and 620/620 reporters hold the matching discovery line; 2,715/2,715 `<who_reported>` blocks
name the meeting's own reporter and 0 of 244 emergency prompts carry one; the reporter is never handed a
block addressed at itself; the ambiguity fallback is never needed even for the 133 reporters holding more
than one discovery record. The answer-to-a-charge clause renders on 33 of the 34 reporter railroads and is
true in every one — it names the exact structural defect A-11 measured, in the voter's own prompt, at the
moment of the vote. The corroboration block's arithmetic is exact on all 6,896 rendered rows (voices, the
first-hand/adopted split, the originating turn, the flag clause), it reaches the ejectee in 425 of 429
ejections, its vent-grounding channel is exactly truthful (0 of 506 spoken vents grounded without a record),
and it is well calibrated: P(impostor) rises monotonically with voices (0.244 → 0.724) and separates hardest
at the 0/1-account boundary (0.080 → 0.506). Where the walkable-transit clause fires, it is exactly the
missing step (`ml_corpus/9p2i` 1036:m3, 1032:m2; `samples/9p2i` 26:m3 — each refutes the "teleport" charge
that convicted). In three of twelve railroads read, the discovery-account instruction asks for precisely the
route that would have defused the meeting.

**The oracle regime is coherent.** In every vent-sighting meeting read, every ejecting ballot cites the vent
turn or the voter's own vent observation, every counter-accusation drew zero votes, and second-hand
endorsers state their own epistemic position before relaying ("I was in Admin at tick 8, so I could not have
seen the vent, but p-5's sighting is the only hard evidence"). Confidence is two-regime and proportionate:
median 0.95 where the target carries a vent flag, 0.75 where it does not. Skip discipline holds under mob
pressure (`samples/9p2i` 0:m1: five of seven turns accuse the reporter and the vote is 6 SKIP / 1 eject).
And the deduction regime does land an impostor with no hard evidence at all (`samples/9p2i` 4:m1: zero flags,
no vent, pure movement).

**The majority regime is coherent, and the levers cannot interact.** All 24 oracle-regime meetings read as
prose close without a gap — the witness's record, the spoken `saw_vent`, the self-linked STRONG flag, the
ballots citing it, the ejection — and 333 of 333 convict an impostor; the oracle also prevents injustice
(`samples/9p2i` 5:m0: six turns prosecute the reporter on a hearsay chain the impostor is pushing, and a
last-turn vent sighting flips all five crew ballots onto the real impostor). The viewer never calls a
self-linked vent a "contradiction": `classify_evidence` routes it to `role_proof` by two independent rules
and every render site branches on the category. Across all 5,696 subset renders of the 70 meetings the pass
holds every lever subset for, there is exactly one non-additive line — the #417 clause PR-1 retires — and
zero lines leak between levers; `reporter_reasoning` is fully orthogonal. Parse health is 7,262 of 7,262
responses as strict JSON on the first try, with no truncation anywhere near the caps.

**The belief line already knows.** On the ballot's own `this meeting +X` term, X ≤ 0.00 names a crewmate in
253 of 259 non-vent eject ballots (97.7%), and the reporter is already numerically exculpated (96.2% of
accused-reporter rows read +0.00, the Task-15.5 cap). The three Wave-2 levers add zero bytes to the belief
block on 3,631 of 3,631 ballots — all 4,032,365 bytes of the slate land upstream of it — so they operate on
the voter's reasoning prose, never on the number the ballot tells the voter to trust over rhetoric.

**The spectator surface tells the truth where a machine checks it.** The head featured card is true and
pinned both ways; the finale card maps the recorded reason with a verbatim fallback; the recap withholds the
belief judgment on every guard-rewritten ballot and says why; the served tournament report equals the
reading guide's cross-tab cell for cell; the meeting resolution card states the real gate rule; the three
evidence bands are self-glossing; the stale-rubric banner fires. 92% of eject-ballot cards read coherently
(485 of 527 rationales name their own target).

## 3. What must land BEFORE the record

### 3.1 PR-1 — the Wave-2 render amendment (orchestrator-ruled; wording and derived fields; every count unchanged)

Verified twice each. Each edit sits inside a lever guard, so every OFF byte stays identical (proven by the
bare `verify_samples.sh` walk and the byte golden); the four corroboration pins (475/1,525; 11/425; 33/429;
48/429), T6's 3,614/3,631 and T2/T5's populations do not move.

| id | P | where | what is false or self-contradictory on the slate | fix |
|---|---|---|---|---|
| H-1 | P1 | `vote_ballot.j2:197` | "Nothing in the evidence above names them" on 5,086 of 6,896 rows beneath a transcript that names them, 3,083 in the same sentence that credits an eyewitness; the block's own header calls testimony evidence | "No contradiction above names them" / "A contradiction above names them — read it there, in its own class" |
| H-2 | P1 | `crewmate_report.j2:131`, `accusation_round.j2:256,:262` | "that outranks even a vent" on 2,695/2,695 crew renders, the line after "the single strongest fact … One exception, and only one"; a rank never specified (21.20 BLOCK 4) and inverted by every downstream weight | "say that too — it is testimony, not proof, and it always makes the cut" (the last clause reconciles the unguarded curation list, H-14) |
| H-3 | P2 | `vote_ballot.j2:205` | the speech ladder ("1.0 only for a … vent you watched") beside the Proof paragraph ("nothing said at this table outweighs it") on 1,910 ballots, 1,475 where the vent is someone else's | render the ladder only when no Proof group renders |
| H-4 (+H-6, H-16, H-18) | P2 | `vote_ballot.j2:195` | "A voice is anyone who named them tonight" while the code counts accusers: eyewitnesses who accused someone else vanish (41:m2 reads "1 voice" under two STRONG flags carried by two speakers; 36 rows print "0 accounts" beneath a Proof line naming the subject), corroborators are not voices (312 rows), and "a second account corroborates" reads "account" in the everyday sense | header rewritten: voice = accused; the exclusions stated; an account only places them somewhere |
| H-9 | P1 | `accusation_round.j2:137-139` | "Your own record places you at the body when it was reported" for 145 speakers; 57 (all impostors, who perceive an adjacent room) were in a different room | "Your own record has you seeing the body when it was reported" |
| H-5 (+#417 residue) | P1 | `vote_ballot.j2:197` | a witness whose own rendered memory holds "You witnessed p-N kill in ROOM" is told, 96 lines below, that they named the killer "without an account their own record bears out" (16 of 16 adopted kill-witness pairs; four are innocent ejectees) | per-speaker adopted clause: silent / spoke-ungrounded / spoke-kill; the slate fork deleted |
| H-15 | P2 | `vote_ballot.j2:195,197` | the account clause names no tick, so a credited speaker's own disputed sighting (the flag's basis, ungrounded) reads as record-borne (10 credits rest wholly on a ±2-tick stale record; one convicts the ejectee of a game-ending meeting) | render the grounding tick(s) on each account |
| H-17 | P3 | `vote_ballot.j2:202` | the transit line "a conflict over that pair is thin" on 1,152 of 1,376 renders sits beneath "no contradiction names them"; 0 of 287 pairs are a flag's endpoints | "that pair is no ground for an impossible-move charge" |
| — | P4 | `loader.py:930` | "An impostor-facing render is byte-identical under both states" is false: the public `saw_kill` transcript row is role-blind by design | docstring |

Bookkeeping ruled with it: the counterfactual's render-census tables are test-pinned, so the amendment
appends a dated Errata section with the re-derived byte and line deltas (every count unchanged) and the
drift test reads errata as the pin when present.

### 3.2 PR-2 — grounding semantics (OWNER DECISION; moves the 475/1,525 cell the memo adopts by reference)

- **H-8 (P1/P2)** `corroboration.py:232-256` tests a spoken `saw_player` only against sighting records and a
  spoken `saw_move` only against move-witness records; 38 speakers (42 under the ±2 tolerance) whose own
  rendered record bears the placement out in the other channel are demoted to "no account", every one on
  their own ballot page. Fix: cross-channel grounding through the repo's own `sighting_placement` definition.
- **H-7 (P2)** the walkable-transit clause reads `reconstruct_stated_paths` raw, so `saw_move` rows place
  nobody; 12 of 20 impossible-transit railroads get no line, and routing the placements through the
  committed `_apply_movement_claim_shape` recovers 6 of them (`ml_corpus/9p2i` 1111:m0: six ballots convict
  p-2 for "impossible travel West Hall → East Hall"; the clause certifies that exact walk for p-9, whom nobody
  convicted, and says nothing for p-2). The 1-hop / 1-tick / 2-pair caps are ratified design and stay.
Sequenced after PR-1; carries an erratum on counterfactual §8.2 and a §11 row in the memo. Its reach is
bounded: at three living players the accused typically has ONE stated placement, so no pair exists for
the transit clause to defuse even after the fix (R2-fourp-6: 10 of 246 4p1i ballots carry a transit line
against 935 of 3,385 at nine players).

### 3.3 The pre-registration (#419) — clarified and questioned before ratification, then merged by delegation

- **H-19 (P2), CLARIFIED at head a59d6fbc.** T5 is a never-worse bar read through `T-9`, a role-blind byte
  diff; the public-transcript `saw_kill` row is rendered to every seat by ratified, test-pinned design, so on
  a lever-ON record any crew `saw_kill` would make every later impostor prompt "gain the block" and STOP a
  correct record. The memo now reads the elicitation block only.
- **Q-A.** Bars 2–4 are absolute counts with no decisiveness cell: 243 of 620 body reports already SKIP and
  one impostor rider ballot flips 16 of 46; a record that decides less passes three bars. RULED and applied
  at `aa2b3c64`: a §5 secondary cell (I-3's `report_ejections` 377/620, the SKIP share 243/620), observed
  and never gated; no floor.
- **Q-B.** `ROLE_PROOF_KINDS = {"vent_sighting"}`, so a kill-witness conviction under `testimony_shapes`
  lands in bar 1's non-direct cell as deduction. RULED and applied: a §5 secondary cell split by a spoken
  `saw_kill` (baseline 8 reads 0 of 96), its reader owed by the T5/T7 reader contract.
- **Q-C (H-29).** "INVERTED: 0/106 vs 6/660" is one set; the Wilson interval of 0/106 covers the crew rate
  and the four-set pool reads 4/409 against 27/2748. RULED: the adjective withdrawn in the memo; the rerecord
  audit §5.1.2(d) carries the matching erratum below.
- **The residue bars stand** (bar 3 ≤ 12, bar 4 < 40%): the constant-burden alternative held the ask constant
  across a moved baseline, which is the re-pricing the memo's §10 rejects; the T5/T7 reader contract — now
  owing three cells — is dispatched at the merge and must land before 21.23.

### 3.4 Errata on committed records (additive, dated; never a rewrite)

- **H-30** `audits/audit-phase-21-counterfactual.md` §2.2 files `samples/9p2i` 41:m2 among six rows that
  "carry nothing beyond the generic herd"; the ledger has no STRONG-flag tag, and that meeting is the only
  innocent ejection named by STRONG `alibi_vs_sighting` flags (two — the entire baseline-8 population of the
  class; all four convicting rationales quote the ADMIN sighting). Five of the six carry zero flags naming the
  ejectee; 41:m2 carries five.
- **H-29** `audits/audit-phase-21-rerecord.md` §5.1.2(d), as above.
- **H-31** `audits/audit-phase-21-rerecord.md` §5.1.1c named only card 0; `FEATURED_GAMES[2]` (seed 13,
  "five meetings … the longest run") holds three meetings on baseline 8 — the leading claim this record
  falsified, unrouted. **OWNER DECISION** on the fix (the #412 copy rule).

## 4. Routed to contracts and to the close ledger

Every entry below survived adversarial verification (the id is the register's; the number is the verifier's).
The full register — corrected claim, coordinates, verdict pair, and the commands — is
`findings/register-final.md` in this pass's scratchpad; its summary table and tally are reproduced in §6.

### 4.1 To the contracts' next re-anchor

- **21.23 (the smoke).** H-38: the `saw_kill` path has zero committed exposure, so the ballot's own render
  clause and the speech-to-ballot chain are unexercised offline; the smoke's read of tripwire T5 should also
  state whether any crew speaker FILED a `saw_kill` on the ON seeds (one clause on the observed shape, no new
  criterion).
- **21.24 (the record).** Reading notes the record audit must carry beside the verdict, none of which moves a
  bar: the reporter lever adds zero bytes to the ballot and 102 of 102 ballots that ejected a reporter already
  carried the exculpation paragraph (H-26); the exculpation forbids only the naked report-accusation, which
  is 17–24 of the 1,041 accusations naming a reporter — the charges that convict cite a sighting or a transit
  (H-21); the source-count block credits an "account" for any record-matched sighting, so on 37 of the 43
  wrongful convictions with a row it prints ≥1 account and on 13 accounts == voices (H-20); a living
  impostor's ballot is pivotal in 16 of the 46 innocent ejections, and 24 of the 46 flip on removing ANY one
  ejecting ballot — thin margins, not a single adversary (H-28); the block has no row for the ejectee in the
  three guard-REDIRECT innocent ejections (H-25); an impostor speaker is credited as an account 190 times,
  119 of them against the meeting's own reporter, and in 17 of the 46 innocent ejections (H-23); the
  first-hand/adopted split publishes a record-match verdict on every spoken sighting to every voter, impostors
  included, the same disclosure a `vent_sighting` flag already makes (H-24); the belief line is silent on the
  ejectee in 90 of the 150 ballots that convict an innocent (83 read `this meeting +0.00`, 7 carry no row)
  against 17 of 1,558 on the guilty side, and the levers add nothing to that channel (R2-belief-1, -2). **The
  three-living stratum** (R2-fourp-1, -2): 127 of 672 meetings run at exactly three living players — all 82
  4p1i meetings and 45 9p2i ones — where an ejection is by construction unanimity of the accused's two peers,
  so IMP-RIDES and ENDGAME are entailed on those rows (12 of the 46); the uniform-null reporter share there is
  50%, against 30% elsewhere, and the pooled null RISES as bar 2 succeeds (0.32 at n=46 → 0.50 at n=12, bar
  3's own target) because shrinkage strips the large-roster rows first. The record audit must print the
  per-row null beside bar 4. Two errata to fold: the
  counterfactual's tag vocabulary has no STRONG-flag tag (H-30, §3.4) and the rerecord audit's "INVERTED"
  cell (H-29). Two featured-card copy facts for the ADOPTED-branch re-curation: card [1]'s "most-argued game
  in the set" is third by turns (seeds 19 and 47 hold 27 across five meetings) and card [3] attributes flag
  minting to "the engine" (H-34, H-39).
- **21.25 (the post-record sweep).** H-32: the stale rubric contradicts the served bytes on the meeting count
  in 16 of 50 games and on the win shape in 9, and both render on the same card as the fresh winner chip.
  H-33: the ballot card's only explanation for a redirected vote is the raw token `under_gate_redirect` (113
  ballots), while the finale card one click away glosses the same fact in English. H-36: `docs/artifacts.md:96`
  still calls the sample sets "the baseline-6 adopting record", invisible to the doc-facts gate. H-37: the
  reading guide sends a reader to seed 46 for "a pair of conflicting accounts" and the viewer files that one
  flag under "Weak signals".

### 4.2 To the close ledger (36 entries, nine themes; the freeze forbids repairing any of them before the record)

- **Same-tick and out-of-window evidence loss (H-22, H-54).** A vent witnessed on the report tick never
  reaches that meeting: 40 of 40 same-tick (vent, witness) pairs are absent from that meeting's
  `vent_witness_records` against 465 of 465 present at any earlier tick, because the engine returns early
  into MEETING and the orchestrator defers the pre-meeting events to the resume tick
  (`orchestrator/game.py:2153-2162`) while the reporter's own discovery, minted by the report action, IS
  present. 26 meetings; four of the 46 innocent ejections, in three of which the ejected innocent is the
  witness. Separately, five of the 46 eject an agent who watched the murder — the account IS on every
  voter's page as prose; what is absent is a typed shape (the testimony lever's case).
- **Movement attribution and the move-witness channel (H-42, H-43, H-55).** `saw_player_move` credits a
  departure to whoever stands in the origin room one tick LATER (`observation/service.py:476-482` tests
  visibility on the post-advance state): 2,734 of 22,828 rendered move rows (12.0%) name an observer who
  could not see the origin room; the 21.4 last-seen argmax is faithful but 694 belief rows (7.2%) are won by
  such a row — true but unearned placements; and a fabricated `saw_move` is unflaggable by ratified design
  (the detector places only its destination), 46 of 1,606 spoken transitions match no engine move.
- **Detector blindness classes (H-47, H-48, H-49, H-66, H-74).** 11 `alibi_vs_sighting` flags print a
  sighting room the cited observation does not contain (the movement rewrite keeps the event id); the
  detector is within-meeting only — 47 new flag instances would fire across meetings in 28 of 197
  multi-meeting games; no arm covers sighting-vs-sighting (70 conflicts in 61 meetings mint nothing); the
  map-refuted "impossible travel" argument runs in SKIP meetings too, so bar 2 does not measure its
  prevalence; and only the physically grounded flag kinds ever catch an impostor — the testimony-only
  channel runs 158 crew to 21 impostors.
- **Claim-shape defects in what the model emits (H-45, H-46, H-60, H-64, H-65, H-67).** A speaker mis-copies
  its own rendered route into a self-placement 136 times (105 alibi claims, 31 whereabouts); the detector
  then correctly prosecutes the slip and 8 innocents are ejected on it, 5 in the interior class — the
  STRONG-pair tripwire case (41:m2) is this. A crewmate speaks three sightings its own memory refutes and the
  innocent reporter is ejected on the one that mints the flag (4:m3). 22.1% of eject ballots are hearsay by
  the citation contract's own terms and 8.1% silently switch target. An inverted `corroboration` claim (a
  reason that argues AGAINST the player it "supports") is read by the fold as support — a suspicion
  decrease on the player the speaker calls guilty (`manager.py:3838-3844`). Hard fabrication of a sighting
  is 8 of 3,880, seven of them by crewmates, none convicting.
- **Time of death and the discovery tick (H-44, H-53).** No channel carries a corpse's age: the memory line
  renders the discovery tick, so rooms litigate the discovery tick as the kill tick over gaps of median 4
  and up to 31 ticks; 3 of 4 correct non-direct ejections read reached the impostor by an argument the
  engine does not support.
- **Impostor behaviour and the teammate firewall (H-23, H-28, H-56, H-57, H-58, H-72, H-75, H-76).** The
  firewall binds two structured fields only — `accusation.against` and the ballot target; free-form fields
  beside them are unguarded, and impostors demand a living teammate's ejection there. It drops a teammate's
  vent only inside a kill window (26 renders carry one; 13 speak the leak in free text). It suppresses the
  witnessed-kill line but leaves the body-discovery derivative, so an impostor's memory tells it that it
  DISCOVERED its partner's victim (78 of 101). 176 ballot belief rows state a suspicion the same page's
  graph omits (the fellow-impostor rows fall back to the gated default). One impostor claims, structurally,
  to have discovered the body it made. Impostors SKIP 76% of ballots against crew 29%.
- **Memory and belief legibility (H-52, H-61, H-62, H-71).** Six phantom-consensus ejections (every ballot
  guard-redirected; two eject crewmates) propagate into later memories as real consensus; two cited
  observation ids sit inside a coalesced span and are unreadable as cited; the render budget sheds 641 of
  1,947 consecutive memory pairs' own observations and 5 of 219 convicting citations vanish by the next
  meeting; the ballot's "maximum suspicion among the living targets" is a maximum over a strict subset in
  69% of ballots.
- **Ledger semantics that survive the amendment (H-24, H-68, H-69, H-78).** The per-sighting truth verdict
  published to all voters; the corroboration-only arm's adopted clause (false on 101 voices before PR-1's
  per-speaker split, now true); the at_body line stating a fact with no rule attached (a lever-efficacy
  read); the `impostor_roll_call` file swap silently dropping six surface families of the sibling arms (OFF
  on the 21.24 slate; pinned-open).
- **Round 2, the oracle and response channels (R2-oracle-1, -2, -3; R2-responses-1, -2, -3).** 91 of the
  453 `vent_sighting` flags name the vent's SOURCE room at a tick the engine has the subject elsewhere: a
  witness record is stamped with the packet tick and `witnessed_rooms[0]`, and under the project's own clock
  decode the destination end lands right while the source end lands one tick late (no conviction is wrong;
  the flag prose is). A single vent trip's source and destination witnesses each mint a Proof row and the
  ledger counts both as accounts (28 split-room pairs; an OFF clash with the map card's "far-apart rooms"
  clause, not the lever's). The teammate firewall does not own the structured `corroboration` claim: a living
  impostor backs the vent witness against its partner 94 times, 83 of them arguing the partner's guilt. The
  per-turn chokepoint deletes 95 model-authored rows — 90 impostor accusations of a living teammate, 50 at
  confidence 1.00, and 5 grounded `saw_vent`s — and annotates none, so every transcript-side census reads the
  guard's output as the model's behaviour. The impostor reply branch mandates `"observations": []`, so its
  placements are prose-only and unfalsifiable by the machinery (529 of 529 zero-observation turns; 90 assert
  a placement in free text). Prose-only witnessed kills are 14, not 26 — the shape the testimony lever makes
  speakable.
- **Spectator copy, citations and the guard-rewrite census (H-35, H-77).** The "cites p-N:T:S" chip promises
  an observation the memory panel can never show (no served row carries an id; 11 of 150 name a tick with no
  row); A-3 re-measured on baseline 8 — guard rewrites 150 → 100, the published worked case no longer
  reproduces, and all 83 under-gate redirects carry a rationale that argues for the target the guard
  overwrote.

### 4.3 Informational (19) — recorded so nothing is rediscovered

The impostor receives the exculpation block (856 of 2,715 prompts) by ratified role-blind design, and the
same sentence already sits on every ballot (H-81); reporter suspicion and the hearsay pile-on run at full
strength in NON-injustice meetings — the reporter is formally accused in 501 of 620 body reports and in 221
of the 243 that do not eject (H-84); stated confidence tracks the flag channel — 96.8% of flag-backed ejects
sit at ≥ 0.9 (H-83); 229 impostor ballots confess a role or a partner in the recorded `rationale_text`, a
field no player sees (H-85); 113 ballots open `rationale_text` with a bracketed engine marker, a sanctioned
audit trail (H-86); README's "Two of the bars" paragraph crosses referents mid-sentence (H-89); `hard
evidence` on 3,601 ballots is not in the glossary (H-90); `DEFAULT_OLLAMA_NUM_CTX`'s docstring is 1.76×
stale and the overflow is already present on the OFF record (H-91); the reporter block's first two asks are
already answered structurally in 620 of 620 openings, the third ("what you saw on the way") is the material
one (H-27, H-70); the ledger's account is time-blind — 89–98 credits rest on a sighting made at the
meeting's own tick (H-11); the charge's originator is listed among its adopters in 635 rows, true but
misreadable (H-12); the opener-charge clause fires only for the opener, as specified (H-13); the at_body
line and the impostor cover directive co-render on 24 prompts, a juxtaposition already present in the OFF
memory (H-10); the block has no row for the ejectee in 4 of 429 ejections (H-25); 76 of 3,114 accusation
reasons cite no room, tick or observation (H-88); two `vent_sighting` flags print the record's tick beside
a transcript line carrying the spoken one, two ticks apart (H-87).

## 5. Explicitly NOT findings (refuted, or specified behaviour read as defect)

- The two STRONG badges at `samples/9p2i` 41:m2 are correct: the crewmate's own structured alibi over-claims
  ENGINEERING for ticks 12–15 against its own evidence array; the engine puts p-9 in ADMIN at 14. The defect
  is the claim shape the model emits, not the detector (close ledger). The lens's "23 STRONG flags of this
  shape" was 2.
- The impostor receiving the exculpation block: a public rule already on every ballot; the memo's T2 counts
  it. The at_body line beside the cover directive: the fact is in the OFF memory already; the canary test
  pins the role-blind render.
- "the impostor almost never reports its own kill": a deliberate hedge on a fact that is true by construction
  today.
- The reporter opening's instruction count: no discarded turn on the record; the budget is safe on the slate
  (worst case 8,614 tokens).
- The #417 reword: true on 1,540/1,540 adopted voices; the OFF wording was false on 101.
- Zero roll-call turns: the roll-call round records its turns as `opt_in` (`meetings/manager.py:1318-1343`).
- The speech-turn prompt does mark the dead: 967 of 967 "highest suspicion names a dead player" cases carry
  that id in the prompt's own dead list (H-51). The `ReporterContext` fill-from-the-receiver constraint is a
  stated DTO invariant, not an undocumented hazard (H-40). The seed-10 "one weak flag ejects" anecdote is two
  weak flags from two sources on a false alibi (H-50). "34 of 34 reporter-ejectees never speak again" is an
  arithmetic corollary of one turn per speaker (H-59). The two observations of an ejected subject are stamped
  at removal + 1 and describe real applied actions (H-63). The voter who "ignored their own vent" was
  choosing between two Proof-named players (H-73).
- `docs/history.md`'s Phase-13.5 paragraph claims spoken testimony stopped collapsing into a scalar before
  reaching beliefs, and that is true on baseline 8 (5,256 of 9,610 belief rows carry a spoken-alibi suffix);
  the bare-accusation-moves-nothing fact is neither asserted nor denied there (R2-belief-8).
- Nothing false renders at three living players: "agreement at this table is often right" is empirically
  true at n=3 (a subject with 2 voices is the impostor in 30 of 40 meetings), the 0.6 gate never misfires
  there, and the 0-versus-4 innocent gap between the two 4p1i sets is seeds, not generator (R2-fourp-3, -9).
- A dossier gotcha for anyone re-running this pass: for the nine retried captures the extract's
  `*.response.txt` holds the DISCARDED first response; the recorded turn is the retry (R2-responses-4).

## 6. Reproduction (all `$0`, offline, against the committed bytes at `38b680f0`)

The pass's working files are not committed (they are a 489 MB dossier plus the lenses' scratch scripts);
what follows is enough to rebuild any number in this audit from the tree.

- **The dossier.** `tests/meetings/test_prompt_byte_golden.py::walk_replay_meetings` over every
  `replays/{samples,ml_corpus}/{4p1i,9p2i}/replay-seed-*.jsonl`, with `renderers_for_set` built from
  `scripts/counterfactual_phase21.py::_RendererCache.capturing(...)`, yields per meeting the recorded prompts
  (`hit_prompts`), the participants (with `sighting_records`, `move_witness_records`,
  `body_discovery_records`), and the render inputs; the ON legs are
  `_renderer_for(bundle, kind)(**_on_kwargs(capture, levers=..., reporter=_reporter_inputs(...),
  ledger=_ledger_for(meeting)))` exactly as `_fold_render_diff` does. Rendered memory per participant is
  `api.replay_loader.ReplayLoader(replay_dir).get_meeting_memory(game_id, meeting_id, agent_id)
  .rendered_memory_text`. Roles are `eval.validity.roles_by_seed`. Engine truth is the same re-seed +
  `advance_tick` walk `api/replay_loader.py::ReplayLoader._walk` performs.
- **The injustice ledger and the counterfactual cells.**
  `uv run python scripts/counterfactual_phase21.py --sets all --json` (28.7 s; the ledger, the four
  corroboration pins, the render census).
- **The reporter cells.** `uv run python -m eval.reporter_justice replays/samples/9p2i replays/ml_corpus/9p2i
  replays/samples/4p1i replays/ml_corpus/4p1i --pooled`.
- **The evidence-honesty cells (the "INVERTED" arm).** `uv run python scripts/measure_baseline.py --honesty
  --json <set>` on each of the four sets.
- **Every count in §§3–4** is stated in the register entry that carries it, with the verifier's own script
  named (`harden/verify/<id>-a/` for the refuter, `<id>-b/` for the re-deriver) and its printed output
  quoted; the register is `harden/findings/register-final.md` (91 entries; tally: PR-1 12, PR-2 2, owner 1,
  #419 1, erratum 1, re-anchor 8, close-ledger 36, informational 19, refuted 11; severity P1 4 / P2 25 /
  P3 35 / P4 27; verdict objects 127: ADJUSTED 107, CONFIRMED 4, REFUTED 16).
- **The commits this pass made to the tree**: to PR #419's branch, `a59d6fbc` (the T5 predicate
  clarification), `83580b58` and `08378e1a` (the audits inventory byte count recomputed at final content) and
  `aa2b3c64` (the owner-delegated rulings applied); the PR merged as `5ae452d8`. On `main`, `ddf86e48` (the
  #420 amendment records on 21.18/21.19/21.20) and `b34dbcba` (21.22's merge-reality record).
  The amendment is PR #420, merged as `5ab03fd7` (three Codex rounds; the four corroboration pins and every
`rendered`/`changed` count unchanged; the render-census byte and line deltas carried by the counterfactual's
new Errata section).
