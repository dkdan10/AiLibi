# Phase-21 planning audit — the re-ground on corrected bytes

Companion to `tasks/phase-21.md`. That document is the charter; this one records how it was
built, what was cut, what diverged from the handoff, and what the owner must decide before the
first task dispatches. Written at assembly, against the tree at `4002f19b`.

The standing context, stated once and binding on every sentence below: **baseline 7 is canon by
explicit owner override of a FINDING verdict.** The pre-registered rule returned FINDING at the
Phase-20 record — bar 1 non-direct conviction accuracy 61/103 = 0.5922 against ≥ 0.60, bar 2
innocent ejections 42 against < 35, both missed, neither re-priced — and the owner adopted the
substrate over that verdict on 2026-08-26 (`audits/audit-phase-20-baseline-7.md` §6.1). Nothing
in this phase may state or imply that those bars passed.

## 1. The Wave-0 grounding and its method

The plan is chartered from `audits/review-2026-08-26/README.md` — a two-track adversarial audit of
the tree at the Phase-20 close merge, committed at `4002f19b` **before** this plan was drafted.
Its findings are not restated here; they are cited by register id, and the register is the
authority.

What matters for planning is the method and what it licenses. Two tracks ran blind to each other
by the 2026-08-19 review's shape — parallel finder fan-out, dedup and collation, then
**independent adversarial verification** where every finding was re-run against fresh code and
bytes by a verifier instructed to refute it, defaulting to REFUTED when the evidence did not
reproduce. Track A returned 48 canonical findings over gameplay; track B returned 56 over the
code. One was REFUTED outright; the large ADJUSTED share is the method working — a verifier
correcting a claim, a severity or a classification is a stronger input to a contract than a
finding nobody re-ran.

Three consequences bind every contract in the phase:

1. **The verifier's word beats the finder's.** Where a register entry is ADJUSTED, the contract
   quotes the corrected claim and the corrected severity. Quoting the original filing without its
   correction is a defect in the contract, not a stylistic choice. Several contracts here exist in
   a narrower shape than their finding was filed in for exactly this reason — 21.20's `saw_kill`
   half is bounded to legibility because the verifier bounded it; 21.18 refuses A-38's fix sketch
   as written because the verifier's own disconfirming measurement (36.4% of non-reporter
   co-discoverer slots are impostors) says exculpatory framing there would launder an impostor in
   over a third of the meetings it fires in.
2. **Evidence commands that name one-session scratch scripts are not instruments.** The review says
   so itself (§4). Any number that becomes load-bearing in a contract is re-derived by that
   contract's own Measurement command before anything is built on it, and several contracts carry
   verify-then-fix as their first DoD step where an anchor could not be re-confirmed at HEAD.
3. **The audit ran before the plan on the owner's explicit instruction**, which is a divergence
   from the usual sequencing and is recorded as such in §7.

## 2. The phase shape, and why

The mandate in one sentence: repair the verified defects that would otherwise be baked into the ML
re-ground, take ONE combined maintenance re-record on the corrected substrate, execute the
`audits/audit-phase-20-baseline-7.md` §10.2 re-ground on that corpus, then attack the last
injustice as pre-registered levers with their own adopting record.

**Why the repairs come first, and why they are not levers.** The re-ground is a fit. A fit against
a substrate carrying known behavioural defects bakes those defects into the optimizer, and the
review's own "why now" paragraph makes that the reason the audit ran at all. So Wave 1a repairs
first. They are unconditional defect repairs rather than levers because there is nothing to compare
them against: a lever exists to be adopted or not by a record that reads a bar, and 21.15 reads no
bar. They use byte-identity seams — the v4 prompt archive reopened at 21.1, default-OFF gating
where a seam does not exist — so `bash scripts/verify_samples.sh` and the prompt byte-golden stay
green through every merge before the record.

**Why ONE re-record.** The cadence doctrine's "one combined re-record, never two" applied to the
audit's findings. Six recorded-behavior repairs ride a single 23-hour window. The cost of that
choice is stated rather than hidden: attribution is impossible by construction, and 21.15's audit
must say so in its own words. The alternative — one record per repair — is six windows and no more
attribution than one, because the repairs interact.

**Why the re-ground sits between the records.** 21.17 discharges §10.2 in full on the baseline-8
corpus and deletes the STALE amnesty. If it ran after the Wave-2 record instead, the phase would
carry an un-discharged grounding debt through its own adopting event, and the campaign tier —
already red since before the Phase-20 close — would stay red across a record. Running it between
the records buys a green campaign tier and one honest, priced cost: on ADOPTED, 21.24 re-declares a
grounding gap.

**Why Wave 2's changes ARE levers.** They change what the game is. They are default-OFF,
pre-registered at 21.22, and adopted or recorded-as-finding at 21.24 under a rule written before
the record is spent. A miss is a miss.

**Baseline numbering: 8 then 9.** 21.15 mints baseline 8. The glossary defines a numbered reference
recording by which bytes a set holds (`docs/glossary.md:38-59`), not by whether a verdict was read
over them; 21.15 replaces all four committed sets, so leaving the ladder tip at 7 would falsify
every front-door cell that reads those bytes — precisely A-15's defect class. 21.24 mints baseline 9
on ADOPTED; on FINDING the tip stays at 8 and the bytes and the read publish anyway. Two baseline
ids in one phase is the priced consequence of two records in it, and it is put to the owner in §6.

**Two divergences from the handoff's dependency table, recorded.** The planning inputs proposed
seven day-one roots. Assembly added two edges, and neither was a preference — in both cases the
contract could not otherwise satisfy its own stated Measurement.

**21.10 now depends on 21.3.** The two contracts both name `orchestrator/replay.py`,
`api/replay_loader.py`, `tests/orchestrator/test_replay.py` and `tests/api/test_replay_loader.py`
in scope, and the validator rejects two tasks in one phase sharing a scope item with no ordering
between them (`scripts/validate_task_docs.py::validate_parallel_file_scope`). Both are named files,
so the narrow-a-directory remedy did not apply; the edge was the minimal fix. The direction is 21.3
first because 21.3 changes the recorded row shape (`ReplayEntry.action_dispositions`, `record_tick`'s
keyword-only `events`) and 21.10 hardens the recorder and the loader guard around it — the hardening
should harden the shape the record will carry, not race it.

**21.16 now depends on 21.13.** 21.16's campaign-tier Measurement expects exactly the eight residual
§10.2 failures the ML re-ground owns. The ninth is the `tests/test_scenarios.py` mover pin, which
21.13 removes and which belongs to 20.32's repair rather than to the corpus. As parallel roots the
tier reads NINE at 21.16's branch point, so the contract was unsatisfiable without an out-of-scope
scenario edit or an undeclared merge order. The edge is acyclic — 21.13 is a root and 21.8 depends
on 21.16, so the chain is 21.13 → 21.16 → 21.8 — and it costs nothing on the critical path, which
runs through 21.7 → 21.9 → 21.8 rather than through 21.16.

Together the two edges leave the day-one frontier at **five roots**: 21.3, 21.4, 21.7, 21.12, 21.13.
With them, assembly verified **zero** unordered scope collisions across all 26 contracts.

Two smaller assembly rulings are recorded here rather than left implicit. **B-47's bake-off-lag
comment block moved from 21.11 to 21.17**: the block at `eval/watchability.py:908-914` describes a
constant that 21.17 moves, and a note rewritten upstream would describe a constant that had not
moved yet and would need editing again the moment it did. The F2 slot it vacated in 21.11 is taken
by `docs/history.md`'s "## In progress: phase 20" heading, which is the same defect class on the
front door's own reading path. And **the index amendment is blessed phase-wide**: `audits/README.md`
and `docs/artifacts.md`'s `audits/` row are struck from the audit-landing tasks' Files-in-scope
lists (21.14, 21.15, 21.21, 21.22, 21.23, 21.24) and ride those PRs as a standing amendment in the
20.34 precedent's shape, with counts re-read at implementation time and never hard-pinned. The close
(21.26) keeps both as scope because nothing follows it to collide with. 21.25 was named in the
handoff's list but lands no audit, so the amendment is a no-op there and was not added.

### 2.1 Corrections taken at review, before the charter merged

An adversarial review of the assembled charter found nine defects in it. They are recorded here
because three of them changed what the phase DOES, not merely how it reads.

**The FINDING branch no longer replaces the canonical sets.** 21.24 records with all three Wave-2
keys stamped `True`. On ADOPTED those keys graduate, so a bare shell stamps them `True` and the new
bytes reconstruct — replacing the canonical sets is correct. On FINDING they stay live toggles that
resolve `False` on a bare shell, so `api/replay_loader.py:603` would compare a recorded `True`
against a live `False` and REFUSE every canonical game: the bare `verify_samples.sh` leg, the served
frontend and the close's own gate rerun would all break on bytes that are perfectly valid under
their own slate. The contract now preserves the FINDING recording as named, non-canonical evidence
under `replays/records/phase-21-wave2-finding/` — outside `replays/samples/` (which the bare gate
walks whole) and outside the declared corpus sets — and leaves the canonical baseline-8 bytes in
place. Every downstream DoD item that assumed replacement is now branch-aware, and the ones that
become no-ops on FINDING must be recorded as checked no-ops rather than passed in silence.

**21.20 registers its own lever.** The draft deferred `_TOGGLEABLE_LEVER_RESOLVERS` and
`.env.example` to "one collecting task", which left `testimony_shapes` unregistered while 21.21's
live-slate guard refuses to print if a priced lever is absent from that registry — the counterfactual
could not have run. `orchestrator/replay.py`, `.env.example` and `tests/orchestrator/test_replay.py`
are now in 21.20's scope with matching DoD items; the DAG serializes 21.18 → 21.19 → 21.20, so the
three levers register in a fixed order and nothing races. The same serialization made 21.20's
"no ordering between the three levers" integration risk false, and it is rewritten around what the
risk actually is: inherited serial edits on shared surfaces, with anchors that must be re-read.

**Three assertions were unconditional where the contract itself branches**, and each would have made
a valid outcome unreachable: 21.16's measurement demanded a green campaign tier that only 21.17 —
which depends on it — can produce (it now expects exactly the eight residual §10.2 failures and zero
new ones, the shape 21.13 already uses); 21.25's resolver census demanded two resolvers, which is the
ADOPTED reading only (it now derives the expected count from the live registry: two on ADOPTED, five
on FINDING); and 21.26's close checklist demanded `_DEFAULT_BASELINE_ID == "baseline-7"` and zero
STALE rows, contradicting both 21.15 and an adopting 21.24 (it now reads baseline 8 or 9 by branch,
and zero STALE on FINDING against exactly one declared pair on ADOPTED).

Three smaller ones: 21.15's audit no longer has to say baseline 7 *remains* canon while the same task
mints baseline 8 — it states baseline 7's history exactly and states that the tip has succeeded to 8,
because the "what no surface may say" constraint binds the bars story, not the tip's succession;
21.26 UPDATES the Phase-21 README row this planning commit added rather than appending a second one;
and the dead `vent_use_heard` read path — ingest, memory render, feature slot — is now scoped to
21.25's post-record sweep, since 21.5 removes its only producer and 21.15 replaces the last bytes
that carried it, which is exactly when a compatibility argument expires (craft rule 3).

A second review round found six more, all valid, and two of them are design rulings worth recording.

**The Wave-2 prompt-version overlays COMPOSE; they do not exclude.** The drafts had each lever raise
when a sibling overlay was active — which would have made the only slate this phase ever records
(all three levers ON at 21.23 and 21.24) unable to construct a renderer or a stamp. 21.18's seam now
defines composition and its two siblings register into it: application order is
`_TOGGLEABLE_LEVER_RESOLVERS` order, so the result never depends on how the environment was spelled;
each enabled combination resolves to a composite per-template stamp derived from the participating
overlay names in that order; and the all-ON composite is materialised and pinned by name. The
invariant Ruling 3(d) actually cares about is now proved exhaustively rather than by spot check — over
every subset of the live overlay keys, no two subsets share a version string and none collides with a
default value, so an ON ballot can never wear an OFF ballot's stamp. The one `ValueError` left at
construction is for a set with no variant BODY, which is a real defect and not a sibling being on.

**The `heard_vent_use` encoder slot is RETAINED, and the reason is blast radius.** The round-1 fix
had 21.25 delete the scalar along with its producer path. `TacticalFeatureEncoderV3` subclasses
`TacticalFeatureEncoder` and its `feature_layout()` / `encode()` call `super()` before appending
(`agents/tactical/features.py:608-668`), so the v2 vector is a strict prefix of the v3 vector:
deleting a v2 scalar re-shapes BOTH layouts while `ENCODER_VERSION_V3` stays `"v3"` and every
training consumer — including the artifacts 21.17 has just re-ground — keeps identifying a
now-different vector with the old stamp. Moving a vector shape means bumping and re-pinning two
version stamps and every downstream consumer, which is a different size of change from a post-record
sweep. So 21.25 deletes the PRODUCER read path (the ingest branch and the memory render) and keeps
the slot: its docstring records that it has been structurally zero since baseline 8, a test pins that
it encodes `0.0` on the new bytes, and the slot's true removal is routed to the next encoder revision
and named in the close's ledger.

Four smaller ones. 21.17's measurement asserted `STALE 0` in a summary line the same task deletes —
it now asserts an `OK` grounding row plus `grep -c STALE scripts/verify_ml_evidence.py` reading 0,
since a counter that could print `STALE 0` would be dead mechanism kept alive to satisfy a checklist;
the same correction propagated to 21.24 (whose ADOPTED path RE-INTRODUCES a declaration with its own
planted counter-case, rather than re-enabling something that no longer exists) and to 21.26's close
readings. 21.24's implementation step still told the operator to flip resolvers to a constant `True`,
contradicting the same task's delete-DoD and the AST gate that rejects exactly that shape — the step
now deletes each resolver while collapsing its guard to the ON path in one commit. 21.15's standing
index amendment named only the `audits/` registry row, but the prompt-archive retirement deletes six
counted fixture bodies, so the amendment now names the `tests/fixtures/` row too. And the README
phase row was written in this project's private dialect ("ML re-ground", "the last injustice"),
neither term defined in the glossary, on the one surface craft rule 4 governs; it is now plain
language.

A third and final round found seven more. Two are worth recording beyond the fix itself.

**The adopting record's ADOPTED scope could not execute its own deletion.** Rounds 1 and 2 established
that 21.24 deletes each graduated resolver and collapses its guard in the same commit. The scope did
not cover where those resolvers live or who reads them: `testimony_shapes_enabled` homes in
`meetings/constants.py` (forced there by the `agents ↛ meetings.manager` import contract), and all
three levers are read in `agents/strategic/prompts/loader.py`'s `build_prompt_renderers` and
`orchestrator/game.py`'s `prompt_versions_for_set` arms. Deleting only the scoped pieces would leave
imports of a deleted symbol, or leave the graduated behaviour default-OFF under a bare shell — which
means the record it just committed would not reconstruct. All three modules are now in scope on the
ADOPTED path, the DoD requires the homes and read sites to be enumerated from a fresh grep before
editing, and a new item proves the graduated behaviour ON under a bare environment rather than
assuming it.

**The sabotage-alarm ingest path was nearly collateral damage.** Round 1 scoped the dead
`vent_use_heard` read path for deletion, naming `_AUDIBLE_EVENT_TYPES` "and its loop arm". That
mapping has two members and `sabotage_alarm` is a LIVE producer — Task 21.5 deletes the vent
derivation and explicitly preserves the global alarm emitted while sabotage is active — so deleting
the mapping or the shared `packet.audible_events` loop would have stripped sabotage alarms from
episodic memory on every active-sabotage tick, changing prompt behaviour AFTER the record meant to
freeze it. 21.25 now deletes exactly the `"vent_use_heard"` member and the vent-specific render, and
pins an end-to-end test that an active-sabotage tick still reaches memory and renders.

Five smaller ones. **21.16 gained a dependency on 21.13**: its campaign Measurement expects the eight
residual §10.2 failures, and the ninth is the scenario pin 21.13 removes — as parallel roots the tier
reads nine at 21.16's branch point (§2). **The FINDING evidence path is registered, not just
described**: `scripts/verify_ml_evidence.py` cross-checks `_IN_TREE_PROBES` and `_IN_TREE_INVENTORY`
against every in-tree registry row, so the new `docs/artifacts.md` row needs its entry in both
mappings or the task fails its own gate — the verifier and its tests are now both-branch scope.
**`_LADDER_TIP_AUDIT` stays on the re-record audit on FINDING**: `check_conviction_partition` and
`check_verdict_figures` parse the named audit's bars and compare them with README's live figures, so
pointing them at a lever-ON audit whose bytes are not canonical would either fail the checker or force
the front door to be re-pinned to evidence the record did not adopt. **21.17's risk section stopped
asking for a ruling the DAG already made** — 21.24 depends on 21.17, so the alternative ordering does
not exist; the risk is rewritten around what is actually live, which is that the ADOPTED
re-declaration is new code and must keep mismatch-FAILS. And **the close ledger's sha pair is written
in the corrected direction** (`compute_substrate_sha()` returns `f5865c53…` LIVE against `9bc00af0…`
RECORDED), since publishing F1's reversed version in the authoritative close audit would reproduce the
exact defect class this phase opened against.

The first review round also caught the charter head's "four waves" against five wave headings, and five
collision-discipline chains whose membership or arrow direction disagreed with the contracts' actual
Files-in-scope lists — including two arrows pointing the wrong way (`eval/evidence_honesty.py` and
its test read 21.9 → 21.8, not the reverse). Both classes are now checked mechanically rather than
by eye: every stated chain's membership equals the set of tasks that name the file, and every arrow
is a real transitive dependency.

## 3. The routing table

`audits/review-2026-08-26/README.md` §3 published a PROPOSED routing. The owner's merge of the
planning PR ratifies it. This is that routing resolved to contract ids.

| review §3 bucket | finding ids | contracts |
|---|---|---|
| recorded-behavior fixes → one combined re-record | A-6, A-48 | **21.1** (prompt set v5) |
| " | A-17, A-34 | **21.2** (ballot render) |
| " | A-14, A-3, B-1 (record-fidelity halves) | **21.3** (recorded action fidelity) |
| " | B-8 | **21.4** (last-seen argmax) |
| " | A-31, B-28 (context) | **21.5** (one vent, one record) |
| " | A-1, B-2 — *flagged for an owner ruling* | **21.6** (win ordering) |
| instrument/fit-side, no recorded-byte change | B-6, B-9, B-10 | **21.7** (grounded instruments) |
| " | A-26, B-40, B-15, B-16, B-17 | **21.8** (fit hygiene) |
| " | A-8, A-9 | **21.9** (instrument aim) |
| " | B-18, B-21, B-19, B-23, B-48, B-52 | **21.10** (recorder hardening) |
| " | A-15, B-47 (evidence only), B-50, F2/F3/F4 | **21.11** (prose truth) |
| " | B-39, B-51, B-55, B-56 | **21.12** (frontend gates) |
| " | the 20.32 mover pin (F1's ninth) | **21.13** (mover scenario) |
| the re-ground contract itself | B-11 (fresh bars), B-12 (FO-6 reframe), B-13/B-14, B-26 (harness half) | **21.16** (harness reshape) |
| " | §10.2's moves, F1's nine campaign pins, B-20/B-46, B-43, B-44/B-45, B-47 (the comment) | **21.17** (the ML re-ground) |
| the last-injustice levers | A-4, A-5, A-24, A-37, A-38 | **21.18** (reporter voice) |
| " | A-10's hearsay pile-on, A-19, A-11, A-12 | **21.19** (corroboration) |
| " | B-7, A-22, A-16 (instrument half) | **21.20** (testimony shapes) |
| balance-wave backlog / re-quantifications | A-2, A-13, A-20, A-22 (G-8 half), A-23, A-25, A-27, A-28, A-29, B-24, B-25, B-38 | **none — §5** |
| record-only | everything else, incl. the clean negatives A-42 and A-45 | **the registers** |

The machinery contracts have no register bucket of their own: 21.14 and 21.23 are the two smokes,
21.15 and 21.24 the two records, 21.21 the offline counterfactual, 21.22 the pre-registration and
21.26 the close. 21.25 is the post-record sweep — the graduation sweep proper, the results on the
phase's own bytes, and the F-class checks re-run.

## 4. The strike procedures

Two contracts are owner decision points that can be struck at the planning PR. Both are written so
the subtraction is survivable; this section is the procedure, and it lives here rather than in the
contracts so that a struck contract does not leave instructions behind describing its own absence.

### 4.1 Striking 21.6 (the win-ordering repair)

Grounds for striking: the current ordering is not an accident. `tasks/phase-1.md:220` specified the
skip verbatim as a Task-1.5 Integration risk, `audits/audit-2026-05-09-1901.md` §I-2 signed it off
as conforming, and two tests pin it by name. Changing specified, test-pinned behaviour is the
owner's call, not a repair an agent takes on its own. The realized exposure is zero: both cases in
the committed record recorded the correct winner, and the only realized harm is two meetings' worth
of wasted turns.

The procedure, from the contract's own strike note:

- Delete the `### Task 21.6` section and `agent_prompts/task-21-6-win-ordering.md`.
- Remove `21.6` from the Depends-on rows of **21.11** and **21.14**. Neither loses a real
  ordering: 21.11 keeps 21.1/21.7/21.10 and 21.14 keeps the other seven.
- Remove `engine/tick.py`, `eval/replay_walk.py` (21.6's allowance half), `api/replay_loader.py`
  (same), `training/surrogate/dataset.py` (same), `tests/engine/test_win_ordering_census.py` and
  `tests/_helpers/test_committed_single_home.py` from **21.15**'s Files in scope, and delete its
  win-ordering-expiry DoD item — there is nothing to expire.
- **21.14**'s "six corrected behaviours" DoD item and its "six behavioural repairs" prose become
  five, and its named-UNTESTED sentence about the win-ordering repair goes with them.
- A-1's and B-2's register entries join the named backlog in §5 as a re-quantification, with the
  two-seed census recorded there so the number is not lost.

Everything else is untouched: 21.6 registers no lever key, adds no entry to the substrate stamp, and
moves no committed byte. Its one public type, `engine.tick.superseded_meeting_tick`, is consumed by
no contract except 21.15's expiry — which the third bullet above removes in the same edit. The
remaining scope chains survive the subtraction without a new edge: `api/replay_loader.py` reads
21.3 → 21.10 → 21.15, `eval/replay_walk.py` reads 21.3 → 21.11 → 21.15 (21.11 sits behind 21.3
through 21.1), `training/surrogate/dataset.py` reads 21.8 → 21.15, and `engine/tick.py` leaves the
phase entirely. Re-run `uv run python scripts/validate_task_docs.py` after the strike; it is the
authority on whether the subtraction held.

### 4.2 Striking 21.20 (the `testimony_shapes` lever)

Grounds for striking: it executes G-8's charter, which Phase 20 explicitly routed OUT to a chartered
balance wave (`tasks/phase-20.md:65-67`). Chartering it here is defensible — it arrives as a
default-OFF lever with an offline counterfactual and a pre-registration ahead of it, which is what
Phase 20 asked for — but the decision is the owner's.

The procedure, from the contract's own strike note:

- Delete the `### Task 21.20` section and `agent_prompts/task-21-20-testimony-shapes.md`.
- Remove `21.20` from **21.21**'s Depends-on row. 21.21 keeps 21.18 and 21.19 and prices a
  two-lever slate; it is written subtraction-ready and its per-lever tables are per-lever.
- **21.22** prices bars for the levers that exist. Its DoD already reads the slate from the tree
  rather than from a list, so no edit is required; the memo simply carries two levers.
- **21.23**'s DoD already contains the branch: "If the third lever's contract was struck before
  merge, the report records a two-lever slate as the declared slate and does not file the absent
  lever as untested."
- **21.24** graduates or does not graduate whatever the registry holds; all-or-none across the slate
  is unaffected by the slate's size.
- **21.25** sweeps whatever graduated; nothing in it names the third lever specifically.
- A-16's instrument cells and A-17's memory half join the named backlog in §5. **They do not move
  to another contract** — A-16's cells are scoped to the instrument the lever ships beside, and
  relocating them would smuggle a struck decision back in through a gauge.

## 5. The cut line

OUT of this phase, recorded rather than silent.

| item | size | why out |
|---|---|---|
| The balance-wave backlog: G-5, G-13, G-15, G-22, G-40, G-43 | a chartered wave with its own record | Routed by the Phase-20 close (§4) and still the owner's next decision. This phase spends its two records on maintenance and the last injustice. |
| Wave-0 re-quantifications: A-2, A-13, A-20, A-22, A-23, A-25, A-27, A-28, A-29, B-24, B-25, B-38 | 12 register entries, no code | Deepenings of already-routed items, per the review's §4. Recorded in the registers; no contract reads them. |
| Phase C co-evolution | a campaign-scale phase | Rejoins on the re-grounded substrate; the owner's appetite decides when. |
| The λ-grid / coevo re-search and the arms re-measure under the repaired objective | two campaign-scale runs | 21.16 repairs the fitness objective, which makes the committed λ grid a recording under a superseded objective. Re-searching it is a NEW study, not a re-ground, and would silently re-price a recorded result. 21.17 routes both to the close ledger. |
| B-26's `world.py` half | ~1 contract | 21.16 takes the harness half; the engine half is routed to the close ledger. |
| B-28's audible entitlement scan | ~1 small contract | 21.5 removes the only live producer, so the scan would gate a channel with nothing on it. |
| C-120's transcript-docstring half | a few lines | Named open in 21.12; carried, not silently dropped. |
| The register's remaining P3/P4 tail | A: 17 P3 + 3 P4; B: 19 P3 | Triaged backlog. Each entry carries its own verdict and evidence in the register. |
| F5: `git push origin --delete evidence/raw-slate-staging` | one command | An owner one-command step, not a task. Carried from the Phase-20 close. |

## 6. The owner decision points

Each is a strike or a re-price to be taken **at the planning PR, before merge**. The PR body states
them as instructions; this section is the record.

1. **21.6 — the win-ordering repair.** Strike to reject. It changes behaviour that
   `tasks/phase-1.md:220` specified and two tests pin by name. Procedure: §4.1.
2. **21.20 — the `testimony_shapes` lever.** Strike to defer. It executes G-8's charter, which
   Phase 20 routed OUT to a chartered balance wave. 21.21/21.23/21.24 are written
   subtraction-ready. Procedure: §4.2.
3. **The F3 front-door word ceilings** (21.11): README ≤ 3,500, `docs/reading-guide.md` ≤ 1,350,
   `docs/ml-program.md` ≤ 1,950, `docs/lessons.md` 800–1,500. These are set bite-don't-trim — every
   page is under its ceiling at HEAD (3,425 / 1,303 / 1,838 / 1,491), so the gate bites on the next
   addition rather than forcing a trim now. Re-price if trims are wanted instead.
4. **Two baseline ids in one phase**: 8 at the maintenance re-record, 9 on ADOPTED. The alternative
   is leaving the tip at 7 across a record that replaces all four committed sets, which falsifies
   the front-door cells that read them.
5. **The re-ground before the Wave-2 record, and its priced cost.** On ADOPTED, 21.24 re-declares a
   NAMED, dated grounding gap in §10.2's exact shape — STALE granted to exactly one new digest pair,
   with a fingerprint mismatch outside that pair still FAILING. The second re-fit is routed to the
   close ledger as an owner decision rather than taken inside a record window.
6. **21.22's [PROPOSED] reporter bars**: ≤ 12 pooled reporter convictions; < 40% reporter share of
   innocent ejections. Priced at the owner's merge of that PR, not here — but flagged now so the
   shape is not a surprise.
7. **21.12's 1440x900 premise.** The contract keeps 20.3's premise on correct-either-way branches.
   If it reads red at HEAD, the premise itself needs an owner revision.
8. **The cost envelope**: two operator records at roughly 23 h wall each at two Featherless workers,
   $0 flat-rate, plus two smokes at about an hour each. Order: 21.14 smoke → 21.15 record → 21.23
   smoke → 21.24 record. A smoke's ABANDON is a real branch and its restart is the owner's.

Carried for the owner but not Phase-21 contracts: F5 (the staging-ref delete above), the README
authorship block and `docs/lessons.md` wording confirmations, and the Phase-20 close audit's F1
sha-pair erratum — F1 states the anchor-study substrate pair as "recorded `f5865c53…`, live
`9bc00af0…`" and it is the other way round; 21.17's contract carries the correction and 21.26's
ledger records it.

## 7. Divergences from the orchestrator handoff

Three, all deliberate.

**Wave 0 ran before the charter existed.** The usual sequencing is plan then audit. Here the
grounding audit ran first, on the owner's explicit instruction, and was committed at `4002f19b`
before a line of this plan was drafted. The benefit is that every contract cites verified findings
rather than a handoff's leads. The cost is that the audit could not be scoped by the plan, so it
returned 104 canonical findings against a phase that can carry 26 contracts — which is why §5's cut
line is longer than usual and why the routing table in §3 exists at all.

**The counterfactual precedes the pre-registration in Wave 2, inverting Phase 20's order.** At
Phase 20 the memo (20.22) was ratified before the counterfactual (20.34) was computed. Here 21.21
publishes first and 21.22 writes the bars afterwards. The inversion is deliberate — the Wave-2
levers are largely PROMPT levers whose effect on conviction and accuracy cannot be predicted
offline at all, so a memo written before the counterfactual would price bars for cells nobody had
yet established were predictable. But the inversion carries an obvious hazard: bars written after
seeing an offline prediction are bars fitted to a prediction. Two mitigations are built into
21.22's contract and both are load-bearing:

1. **The counterfactual owns no bar and predicts no bar's outcome.** 21.21 publishes per-lever
   OFF/ON tables and an explicit NOT-PREDICTABLE-OFFLINE list; it is forbidden from proposing a
   target. Its role in 21.22 is to say which cells have an offline prediction at all, not what the
   prediction was.
2. **The two primary bars are inherited verbatim and their targets do not move.** Non-direct
   conviction accuracy ≥ 0.60 pooled and innocent ejections < 35 pooled are the two bars the
   baseline-7 record MISSED, carried forward with unchanged targets. They cannot be fitted to
   anything, because they were fixed before either record existed. Only the reporter-justice bars
   are new, they are read from cells 21.18 ships as a committed instrument, and 21.22's DoD
   requires each to state whether an offline prediction for its cell exists — which makes the
   dependency visible in the memo rather than hidden in its authorship.

**The day-one frontier is five roots, not seven.** The handoff's dependency table listed 21.10 and
21.16 as roots. Assembly added two edges — 21.3 → 21.10 for a scope collision the table did not
cover, and 21.13 → 21.16 because 21.16's campaign Measurement counts on the ninth failure already
being gone. Rationale, the collision inventory and the acyclicity argument: §2.

## 8. Reproduce

```
uv run python scripts/validate_task_docs.py          # exit 0; 390 tasks / 390 prompts
uv run python scripts/compute_next_task.py --phase 21 # 6 dispatchable, 20 blocked, 0 errors
bash scripts/check.sh                                 # the full default tier
git ls-files audits | wc -l                           # the audits/ row in docs/artifacts.md
```
