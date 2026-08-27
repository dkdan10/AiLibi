# Agent Prompt — 21.1 The dialect is no longer taught: the oracle voice leaves the templates (prompt set v5)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.1 — The dialect is no longer taught: the oracle voice leaves the templates (prompt set v5), anchored to A-6 [CONFIRMED, P1] — audits/review-2026-08-26/A/collated-findings.md:693-838 (the origin grep, the perfect causal separation 45/326 vs 0/342, the 78-utterance TIER1 census reproduced to the digit on an independently authored net, the 22-utterance TIER2 "flag as a noun-of-record" tier, the 326/326 conversion, the "NOT the memory render" attribution, the verifier's two nits — the honest ratio is 44 games / 3 seeds and there is a THIRD rendered oracle noun at vote_ballot.j2:135 "the detector already found an innocent reading", which the claim omits and this contract fixes — and the cascade note at :832-833); A-48 [ADJUSTED, P3] — :4781-4854, the register half (240/3602 = 6.66% of turns carry a raw room id across 120/300 games, per-set 141/75/14/10, and the verifier's binding correction: the finder's causal sentence is REFUTED — 3,400 of 7,211 prompts already carry a prose hall name echoed back through the transcript block and the agents prefer prose 3.6:1, so the leak is an UNANCHORED register, not a missing vocabulary; two smaller corrections bind too — the raw-id map card is a deliberate Task 20.31 DoD item at tasks/phase-20.md:5072, and a per-room prose `name` already exists in the map data); A-9 [CONFIRMED, P1] — :1028-1136, context only: the shipped gauge is disjoint from this leak (0/39 overlap, `MACHINERY_VOCABULARY` = two words at eval/deduction_metrics.py:540) and no net runs over `free_text` at all, which is WHY the taught dialect survived to baseline 7; the instrument half is Task 21.9's and no eval module moves here. The standing context every claim below is written against is audits/review-2026-08-26/A/collated-findings.md:4877: baseline 7 is canon by explicit owner override of a FINDING verdict — the pre-registered bars 1 and 2 were missed. Format and mechanics precedent: tasks/phase-20.md:4975-5197 (Task 20.31, the v3→v4 bump that opened and then retired the same archive seam). Anchors re-verified at HEAD (4002f19b): the two oracle lines at agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:164 and vote_ballot.j2:123, both inside `{% if flag_groups.proof %}` (:162-168 / :121-127); agents/strategic/prompts/loader.py:411 `_ROLE_PROOF_KINDS: Final[frozenset[str]] = frozenset({"vent_sighting"})`, so the bucket that renders the line is exactly one kind; the remaining rendered machinery nouns accusation_round.j2:162 + :176 + :252 and vote_ballot.j2:121 + :129 + :135 + :146 + :153 + :158 + :174 + :185 + :192, plus the one shared confidence-rubric phrase at crewmate_report.j2:134 (impostor_report.j2 carries none in its rendered body — its only "flag" hits are inside the `{#- … -#}` header that ends at :64); the version markers at each template's line 3; orchestrator/game.py:322-340 `_bespoke_versions` (four keys, bumped as a unit), :349 `PROMPT_VERSION_SETS` with its four-generation v4 comment block at :381-391 and the entry itself at :392 `"qwen3_6_27b": _bespoke_versions("qwen3_6_27b", version="v4")`, and :415-421 `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`, whose base spread at :417 is the same `version="v4"` call; the archive seam at tests/meetings/test_prompt_byte_golden.py:171-183 (`ARCHIVED_PROMPT_VERSION_SETS = {}` and `tests/fixtures/prompt_archive/` absent since 20.36 retired the v3 entry), its reverse lookup at :424-451, its renderer binding at :848-864 and the one-byte perturbation leg at :1162-1200 (today aimed at the LIVE `crewmate_report.j2`); the registry pins at tests/agents/test_bespoke_prompt_sets.py:505-539 (`TestQwen3627bV4EvidenceHonesty`, whose own docstring still says the committed sets stamp v3 — an F2-class staleness this edit corrects in passing) and tests/agents/test_impostor_answer_arm.py:675-684 + :699-714; the rendered-heading constants at tests/meetings/test_persona_render.py:420-422 and the soft-only marker at tests/meetings/test_elicitation_fixtures.py:123 + :235; the recorder lock at scripts/record_ml_corpus.sh:145-156 with its live-registry equality pin at tests/scripts/test_record_ml_corpus.py:601-620 and the printed dry-run line at :212-226; the map-card render at agents/strategic/prompts/loader.py:371-381 (`_map_card_from_neighbors`), :383-394 (`render_map_card`) and :404 (`CANONICAL_MAP_CARD`), its pins at tests/agents/test_bespoke_prompt_sets.py:703-734, and the ten committed room names in engine/maps/canonical_1.yaml (`engine.world.Room.name`, engine/world.py:118-124) — re-read at HEAD as Admin / Cafeteria / **East Hallway** / Engineering / Labs / MedBay / Reactor / Storage / Upper Hall / **West Hallway**, which corrects A-48's claim text ("`name: East Hall`"); docs/artifacts.md:99 (the `tests/fixtures/` row, `2.0 MB / 23 files`, matching `git ls-files tests/fixtures | wc -l` = 23); the FROZEN default-set pins that must NOT move, tests/orchestrator/test_replay_meetings.py:452-454 and tests/orchestrator/test_meeting_integration.py:2546; docs/glossary.md:140-147 ("flag-minting"), the entry that keeps the word legitimate in the code and the docs while craft rule 4 bans it from the characters' mouths; AGENTS.md craft rules 4, 5, 6, 7.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-dialect-v5`
**Depends on:** 21.3, 21.10
**Section refs:** A-6 [CONFIRMED, P1] — audits/review-2026-08-26/A/collated-findings.md:693-838 (the origin grep, the perfect causal separation 45/326 vs 0/342, the 78-utterance TIER1 census reproduced to the digit on an independently authored net, the 22-utterance TIER2 "flag as a noun-of-record" tier, the 326/326 conversion, the "NOT the memory render" attribution, the verifier's two nits — the honest ratio is 44 games / 3 seeds and there is a THIRD rendered oracle noun at vote_ballot.j2:135 "the detector already found an innocent reading", which the claim omits and this contract fixes — and the cascade note at :832-833); A-48 [ADJUSTED, P3] — :4781-4854, the register half (240/3602 = 6.66% of turns carry a raw room id across 120/300 games, per-set 141/75/14/10, and the verifier's binding correction: the finder's causal sentence is REFUTED — 3,400 of 7,211 prompts already carry a prose hall name echoed back through the transcript block and the agents prefer prose 3.6:1, so the leak is an UNANCHORED register, not a missing vocabulary; two smaller corrections bind too — the raw-id map card is a deliberate Task 20.31 DoD item at tasks/phase-20.md:5072, and a per-room prose `name` already exists in the map data); A-9 [CONFIRMED, P1] — :1028-1136, context only: the shipped gauge is disjoint from this leak (0/39 overlap, `MACHINERY_VOCABULARY` = two words at eval/deduction_metrics.py:540) and no net runs over `free_text` at all, which is WHY the taught dialect survived to baseline 7; the instrument half is Task 21.9's and no eval module moves here. The standing context every claim below is written against is audits/review-2026-08-26/A/collated-findings.md:4877: baseline 7 is canon by explicit owner override of a FINDING verdict — the pre-registered bars 1 and 2 were missed. Format and mechanics precedent: tasks/phase-20.md:4975-5197 (Task 20.31, the v3→v4 bump that opened and then retired the same archive seam). Anchors re-verified at HEAD (4002f19b): the two oracle lines at agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:164 and vote_ballot.j2:123, both inside `{% if flag_groups.proof %}` (:162-168 / :121-127); agents/strategic/prompts/loader.py:411 `_ROLE_PROOF_KINDS: Final[frozenset[str]] = frozenset({"vent_sighting"})`, so the bucket that renders the line is exactly one kind; the remaining rendered machinery nouns accusation_round.j2:162 + :176 + :252 and vote_ballot.j2:121 + :129 + :135 + :146 + :153 + :158 + :174 + :185 + :192, plus the one shared confidence-rubric phrase at crewmate_report.j2:134 (impostor_report.j2 carries none in its rendered body — its only "flag" hits are inside the `{#- … -#}` header that ends at :64); the version markers at each template's line 3; orchestrator/game.py:322-340 `_bespoke_versions` (four keys, bumped as a unit), :349 `PROMPT_VERSION_SETS` with its four-generation v4 comment block at :381-391 and the entry itself at :392 `"qwen3_6_27b": _bespoke_versions("qwen3_6_27b", version="v4")`, and :415-421 `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`, whose base spread at :417 is the same `version="v4"` call; the archive seam at tests/meetings/test_prompt_byte_golden.py:171-183 (`ARCHIVED_PROMPT_VERSION_SETS = {}` and `tests/fixtures/prompt_archive/` absent since 20.36 retired the v3 entry), its reverse lookup at :424-451, its renderer binding at :848-864 and the one-byte perturbation leg at :1162-1200 (today aimed at the LIVE `crewmate_report.j2`); the registry pins at tests/agents/test_bespoke_prompt_sets.py:505-539 (`TestQwen3627bV4EvidenceHonesty`, whose own docstring still says the committed sets stamp v3 — an F2-class staleness this edit corrects in passing) and tests/agents/test_impostor_answer_arm.py:675-684 + :699-714; the rendered-heading constants at tests/meetings/test_persona_render.py:420-422 and the soft-only marker at tests/meetings/test_elicitation_fixtures.py:123 + :235; the recorder lock at scripts/record_ml_corpus.sh:145-156 with its live-registry equality pin at tests/scripts/test_record_ml_corpus.py:601-620 and the printed dry-run line at :212-226; the map-card render at agents/strategic/prompts/loader.py:371-381 (`_map_card_from_neighbors`), :383-394 (`render_map_card`) and :404 (`CANONICAL_MAP_CARD`), its pins at tests/agents/test_bespoke_prompt_sets.py:703-734, and the ten committed room names in engine/maps/canonical_1.yaml (`engine.world.Room.name`, engine/world.py:118-124) — re-read at HEAD as Admin / Cafeteria / **East Hallway** / Engineering / Labs / MedBay / Reactor / Storage / Upper Hall / **West Hallway**, which corrects A-48's claim text ("`name: East Hall`"); docs/artifacts.md:99 (the `tests/fixtures/` row, `2.0 MB / 23 files`, matching `git ls-files tests/fixtures | wc -l` = 23); the FROZEN default-set pins that must NOT move, tests/orchestrator/test_replay_meetings.py:452-454 and tests/orchestrator/test_meeting_integration.py:2546; docs/glossary.md:140-147 ("flag-minting"), the entry that keeps the word legitimate in the code and the docs while craft rule 4 bans it from the characters' mouths; AGENTS.md craft rules 4, 5, 6, 7.
**Complexity:** Medium
**Record impact:** the record itself — the rendered prompt bytes move, and the first recording of them is Task 21.15's combined re-record; no committed replay byte changes in this PR
**Measurement:** `grep -cE "The engine certified|flagged_contradictions|the detector already found" agents/strategic/prompts/qwen3_6_27b/accusation_round.j2 agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2` reads 0 on both files, where it reads 4 on both at HEAD; `uv run pytest tests/meetings tests/agents/test_bespoke_prompt_sets.py tests/agents/test_impostor_answer_arm.py tests/scripts/test_record_ml_corpus.py -q` green (the byte golden walks all 100 committed sample games through the reopened v4 archive); `uv run python -m eval.deduction_metrics` is NOT run and no eval module moves — the A-6 leak net over the committed bytes reads exactly what it read at HEAD (78 TIER1 utterances / 44 games), because committed bytes do not move until 21.15.

The game teaches the dialect it is then measured for. `accusation_round.j2:164` and
`vote_ballot.j2:123` both open the proof group with "Proof. The engine certified these:",
and A-6's causal partition is as clean as this codebase ever gets: over the 668 recorded
meetings in the four committed sets, the oracle net fires in 45 of the 326 meetings where
that block renders and in **0 of the 342** where it does not. Zero. The vocabulary is not
emergent — it is dictated, and 78 utterances across 44 of 300 games repeat it back, 39 in
ballot rationales, 28 in spoken `free_text`, 11 in claim reasons. The three seeds the
project already knew about are 3 of those 44.

Two things make it worse than a cosmetic blemish. First, the block renders on exactly one
flag kind — `agents/strategic/prompts/loader.py:411` fixes `_ROLE_PROOF_KINDS` to
`{"vent_sighting"}` — and every one of the 326 meetings carrying a vent sighting ejects the
flagged venter, 326/326. So the taught phrase sits entirely on the one path that converts
with certainty, and a model fitted to these bytes sees "say *the engine certified it*"
co-occurring with a guaranteed successful ejection. Task 21.17 re-fits on the corpus 21.15
records; whatever register is in the templates at that point is the register the fit
learns. Second, the wording runs against the intent of the very task that wrote it: Task
20.31's DoD required bookkeeping vocabulary to LEAVE the agent's voice, and the verifier
confirmed no test anywhere pins the sentence (`grep -rn "engine certified" tests/` is
empty). It is an unruled implementation choice, not a specified behaviour — which is what
makes deleting it a repair rather than a design change.

Nothing else noticed it. A-9 is the paired instrument half: `MACHINERY_VOCABULARY` at
`eval/deduction_metrics.py:540` is the two words `("threshold", "suspicion")`, its overlap
with the 39 oracle ballots is **0**, and no machinery net runs over `transcript.turns` at
all — so the committed reports read `player_visible_leak_turns = 0` on a surface that is
not clean, and every published cell about this class was measured by an instrument that
cannot see it. That gap is Task 21.9's to close, and this contract deliberately touches no
eval module: the fix and the gauge must be able to move independently, or the next report
proves only that the two were edited together.

The sweep is wider than the two sentences, because the register is the finding. A-6's TIER2
tier counts a further 22 utterances using "flag" as a noun-of-record ("the vent flag is
undeniable", "no hard flags"), and the same two templates hand the word out eleven more
times: the XML section name `<flagged_contradictions>`, the conflicting-accounts paragraph
("The flag says only that … A flag on its own is a lead"), the weak-signal paragraph's
third oracle noun ("the detector already found an innocent reading for it" — the one A-6's
claim omits and its verifier note names), the ballot's transit line, the rendered
provenance tag "no flag; carried/soft only", the reporter paragraph, the §4.6 decision
paragraph and the two output-contract lines. `flag` stays a first-class project word: it is
in `docs/glossary.md:140` as "flag-minting", it names the code that mints, groups and
renders these rows, and none of that changes. Craft rule 4 governs one surface only — what
a character can say out loud — and on that surface the honest words are the in-world ones:
a *witnessed vent*, a *contradiction*, an *innocent reading*.

A-48 rides the same bump, as its own fix sketch asks, and only as far as the evidence
supports. Its measurement stands exactly (240 of 3,602 turns, 6.66%, 120 of 300 games), but
its causal sentence does not: the verifier showed 3,400 of 7,211 recorded prompts already
carry a prose hall name — echoed back off peers' `free_text` through the transcript block —
and the agents use the prose form in 858 turns against 240 raw, preferring prose 3.6 to 1.
So the model is not short of a spelling; it is short of an ANCHOR, because no *authored*
surface has ever offered one. This task adds the anchor at the cheapest honest place, the
`<map>` card, and pairs it: each of the ten walkable rooms renders as its committed prose
name followed by its id, so a prose spelling is authored for the first time and the id
never leaves the surface the JSON contract asks for. One correction the implementer must
carry: the committed names are **East Hallway** and **West Hallway**, not the "East Hall"
A-48's claim text quotes and the agents habitually say — so this publishes the map's own
name, and whether the spoken register follows is re-measured at 21.15, not asserted here.
The per-observation transcript renders and the output schema keep bare ids and are out of
scope: those strings are what the detector and the audit nets read, and swapping them is a
schema-compliance risk priced against a P3 cosmetic blemish.

The version cascade is mechanical and the repo's convention decides it. `_bespoke_versions`
(orchestrator/game.py:322-340) mints all four keys from one `version` argument and every
prior layer of this set moved as a unit — v1 the bespoke port, v2 the elicitation batch, v3
the persona voice, v4 the 20.31 evidence-honesty batch. Here the map card moves, and the
card renders in all four default templates (crewmate_report.j2:107, impostor_report.j2:109,
accusation_round.j2:206, vote_ballot.j2:144), so all four RENDERS move and all four stamps
must: `qwen3_6_27b` → v5, whole set. The variant registry follows for the two keys it
inherits — with the Task-18.10 lever ON the crewmate and ballot bodies ARE the new v5
bodies, so leaving `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS` on the v4 spread would stamp v5
bytes with a v4 name, exactly the collision Ruling 3(d) forbids. The two `*_roll_call.j2`
bodies stay byte-untouched on their own v1 lineage (they render no map card, so their
rendered bytes do not move), and their unswept rubric phrase at
accusation_round_roll_call.j2:210 is a deliberate deferral recorded for the phase-close
ledger — an unrecorded, default-OFF arm, 20.31's precedent.

Everything committed stays readable, and that is the load-bearing seam. The 300 committed
games stamp `*.qwen3_6_27b.v4`; the moment the live registry reads v5 their reverse lookup
at tests/meetings/test_prompt_byte_golden.py:424-451 matches zero registered sets and fails
loud, taking the golden over all 192 recorded meetings of the two committed sample sets
with it (152 in 9p2i, 40 in 4p1i, counted at HEAD off the `kind == "meeting"` rows). So this
task REOPENS the bump-in-flight archive 20.36 retired: byte-copies of all six
pre-PR bodies under `tests/fixtures/prompt_archive/qwen3_6_27b_v4/`, one
`ARCHIVED_PROMPT_VERSION_SETS` entry keyed to the four recorded v4 stamps, and the
perturbation leg re-aimed at the archived body (perturbing a live v5 template is a no-op
for a golden that walks only v4 recordings). Task 21.15 retires the entry again when the
new record stamps v5. No committed replay byte moves in this PR, `scripts/verify_samples.sh`
stays 100/100, and the A-6 leak census over the committed bytes is unchanged by
construction — this contract changes what the NEXT record will say, not what the last one
said.

This is not a lever, and the phase's structure is why. Craft rule 7 makes anything that
changes rendered prompt bytes lever-gated default-OFF until its adopting record — but Wave 1a
carries no adoption. Phase 21 re-grounds on corrected bytes: 21.15 is maintenance-of-record
with no bars and no verdict, and 21.1 is an unconditional repair of a defect that contradicts
its own authoring task's intent. There is no arm to compare it against and nothing to
graduate, so no `AILIBI_*` resolver is introduced, `orchestrator/replay.py` gains no key, and
the substrate stamp does not move. The gate is the one that already exists: the loader's
default set is the frozen 9B set (loader.py:136), so a bare environment renders zero v5 bytes
and only an explicit `AILIBI_PROMPT_SET=qwen3_6_27b` reaches them. That, plus the archive
seam, is the whole containment story — and it is the same story Task 20.31 told for v4.

One consequence must be stated rather than discovered. `scripts/record_ml_corpus.sh:156`
pins `REQUIRED_PROMPT_VERSIONS` to the four v4 strings and
tests/scripts/test_record_ml_corpus.py:601-620 asserts that constant equals the live
registry, so the re-lock is not optional — without it `bash scripts/check.sh` fails at this
PR. Re-locking to v5 means the recorder's freeze-time `check_recorded_prompt_versions`
(scripts/record_ml_corpus.sh:530, called at :1249) will no longer re-freeze the EXISTING
baseline-7 corpus, whose MANIFEST rows carry v4. That is the re-lock conversation the
constant's own comment says is an owner decision, and Phase 21 already took it: 21.15
re-records all four sets from scratch on the corrected substrate. The PR states this
explicitly instead of leaving a recorder that silently refuses a resume.

**Files in scope:**
- agents/strategic/prompts/qwen3_6_27b/*.j2; (the FOUR default bodies → v5: the two oracle sentences rewritten in-world, the machinery nouns swept out of every rendered line, the `<flagged_contradictions>` section renamed, the shared confidence-rubric phrase at crewmate_report.j2:134 and accusation_round.j2:252 de-jargoned, each template's line-3 version marker bumped; the two `*_roll_call.j2` variant bodies stay BYTE-UNTOUCHED on their v1 lineage)
- agents/strategic/prompts/loader.py; (the frozen ten-room display-name table + `_map_card_from_neighbors` renders name-and-id pairs; `_ROLE_PROOF_KINDS` and the grouping logic are read as evidence and NOT changed)
- orchestrator/game.py; (`PROMPT_VERSION_SETS["qwen3_6_27b"]` → v5 and the same move in the variant registry's inherited base, with the v4 comment block replaced by what v5 is)
- tests/fixtures/prompt_archive/qwen3_6_27b_v4/; (new: byte-copies of the six pre-PR bodies)
- tests/meetings/test_prompt_byte_golden.py; (the v4 archive entry, its docstring, and the perturbation leg re-aimed at the archived body)
- tests/meetings/test_persona_render.py; (the three heading constants at :420-422 and the grouping assertions that read them)
- tests/meetings/test_elicitation_fixtures.py; (the soft-only marker at :123 and its rendered assertion at :235)
- tests/agents/test_bespoke_prompt_sets.py; (the v5 registry pin, the map-card pins at :703-734, the new marker-line gate, the negative net over the four rendered bodies)
- tests/agents/test_impostor_answer_arm.py; (the two inherited variant stamps at :680 and :683)
- scripts/record_ml_corpus.sh; (`REQUIRED_PROMPT_VERSIONS` re-lock ONLY — the constant moves WITH the registry or check.sh fails at this PR; the baseline-6/7 narration sweep is Task 21.11's B-50 work and is NOT touched here)
- tests/scripts/test_record_ml_corpus.py; (the registry-equality pin at :601-620 and the printed dry-run line at :212-226, with their stale "all four templates at v3" comment corrected in the same edit)
- docs/artifacts.md; (row 99: the `tests/fixtures/` file count and size re-derived from `git ls-files`, and the "the prompt archive is empty between bumps" clause made true again)

**Files NOT in scope:**
- eval/deduction_metrics.py and every other eval module (A-9's gauge is Task 21.9's; the fix and the instrument must move in separate PRs or neither result means anything)
- agents/strategic/prompts/qwen3_5_9b/ and the other five frozen sets (the DEFAULT set is the frozen 9B one at loader.py:136, so a bare environment renders zero v5 bytes and the frozen pins at tests/orchestrator/test_replay_meetings.py:452-454 and tests/orchestrator/test_meeting_integration.py:2546 are VERIFY-ONLY: if they go red the bump has leaked out of the locked set)
- meetings/transcript.py, meetings/manager.py, api/schemas.py (the evidence taxonomy and the weak stamp are consumed verbatim; only the WORDS the templates wrap them in change, and `classify_evidence` must keep agreeing with `classify_flag_for_prompt` untouched)
- observation/public_map.py (the display names are a render-side table, not a widening of `PublicMapView`; nothing crosses the §1.3 firewall)
- scripts/refresh_samples.sh (its missing per-template version pin is B-19, routed to Task 21.10)
- replays/ (no re-record here; the committed bytes resolve through the reopened archive and `verify_samples.sh` stays 100/100)
- orchestrator/replay.py and the substrate stamp (this bump introduces no `AILIBI_*` lever and registers no key: the gate is the existing `AILIBI_PROMPT_SET` selector plus the archive seam)
- README.md (its `v4` sample-provenance sentence at :217 is re-derived from the sample MANIFESTs by `check_doc_facts.check_sample_provenance`, and those still read v4 until 21.15 records v5)

**Definition of done:**
- [ ] Neither `accusation_round.j2` nor `vote_ballot.j2` contains an out-of-world agent: `grep -c "The engine certified"` reads 0 on both, and a case-insensitive net over the two RENDERED bodies (the `{#- … -#}` header excluded) for `the engine`, `the system`, `the detector`, `certif` and `flag` returns zero. The proof group keeps its full epistemic content in-world — only an impostor can vent, a witnessed vent here names one outright, and nothing said at this table outweighs it.
- [ ] The sweep is surgical and provable as such: every non-proof line changes ONLY its machinery noun — no clause is added, removed or reordered — and the PR quotes a word-diff of both templates showing exactly that. The sites are the `<flagged_contradictions>` open and close tags in both files (accusation_round.j2:162 + :181, vote_ballot.j2:121 + :140), accusation_round.j2:176 + :252, and vote_ballot.j2:129, :135, :146, :153, :158, :174, :185, :192.
- [ ] The one shared confidence-rubric phrase is swept on every default surface that renders it — crewmate_report.j2:134 and accusation_round.j2:252 — so the register is anchored uniformly rather than split across templates; `impostor_report.j2` renders none and its body changes only at its version marker. The identical phrase at accusation_round_roll_call.j2:210 is NOT touched, and the PR records the deferral and its reason for the phase-close ledger.
- [ ] `tests/agents/test_bespoke_prompt_sets.py` carries the net as a GATE, not a grep: one test renders all four default templates with a proof flag, a conflicting flag and a weak flag present and asserts the banned vocabulary is absent from each render; a planted case renders a deliberately re-worded template body from `tmp_path` and asserts the same test FAILS on it.
- [ ] The map card anchors the prose register: `_map_card_from_neighbors` renders each of the ten walkable rooms and each neighbour as `Prose Name (ROOM_ID)`, the card stays at most twelve lines, and the header's single "ONE tick of walking" sentence is unchanged. The display names come from a frozen table in `loader.py` — the same "DATA, not an engine import" discipline `CANONICAL_ROOM_NEIGHBORS` already uses — cross-pinned in `tests/agents/test_bespoke_prompt_sets.py` against `{r: m.rooms[r].name for r in load_canonical_map().rooms}` (tests sit outside the firewall, so the engine import is legal exactly there), with a planted case: one wrong name fails the pin. The committed names are published verbatim, **East Hallway** and **West Hallway** included.
- [ ] The existing map-card pins at `tests/agents/test_bespoke_prompt_sets.py:703-734` are repaired, not weakened: the card still equals `render_map_card(public_map_from_engine_map(load_canonical_map()))`, still renders in every meeting template, still names all ten rooms and their neighbours, and the thinned-graph perturbation still breaks it. `test_map_card_never_publishes_vent_topology` is unchanged and green — no vent id may reach the card through the new formatting.
- [ ] `PROMPT_VERSION_SETS["qwen3_6_27b"]` resolves to four `*.qwen3_6_27b.v5` stamps with no value containing `.v1`…`.v4`, `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS["qwen3_6_27b"]` inherits v5 for `crewmate_report` and `vote_ballot` while its two `*_roll_call.*.v1` overrides are unchanged, and the pins at `tests/agents/test_bespoke_prompt_sets.py:505-539` and `tests/agents/test_impostor_answer_arm.py:680` + `:683` assert both. The stamp-collision test at `test_impostor_answer_arm.py:699-714` stays green: no variant body shares a stamp with any default body.
- [ ] Each template's line-3 `version <template>.<set>.<vN>` marker equals the registry stamp for its key, asserted by a NEW test over the four default files and the two variant files rather than by convention; a planted case feeds the checker a header string carrying the old version and asserts it fails. (The markers live inside `{#- … -#}` and never render, so this gate is the only thing that can catch a marker left behind.)
- [ ] The bump-in-flight seam is exact: all six pre-PR bodies are byte-copied into `tests/fixtures/prompt_archive/qwen3_6_27b_v4/`, `ARCHIVED_PROMPT_VERSION_SETS` gains the `qwen3_6_27b_v4` entry keyed to the four recorded v4 stamps, and the byte golden re-renders all 192 recorded meetings of BOTH committed sample sets byte-identically through it. The PR quotes a per-file byte-level diff of each archived copy against its pre-PR body — a one-byte difference silently voids every one of those goldens — and the module docstring at :74-88 is rewritten to describe the reopened window instead of the retired one.
- [ ] The perturbation leg still proves the golden can fail, re-aimed at the ARCHIVED v4 `crewmate_report.j2` with its docstring saying why (perturbing a live v5 body is a no-op while every committed recording stamps v4), and the PR quotes the failing run.
- [ ] `scripts/record_ml_corpus.sh`'s `REQUIRED_PROMPT_VERSIONS` reads the four v5 strings, `tests/scripts/test_record_ml_corpus.py:601-620` is green against the live registry, the dry-run assertion at `:212-226` reads v5, and the PR states the consequence in one sentence: the recorder can no longer re-freeze the committed v4 corpus, which is the intended re-lock — Task 21.15 records the replacement.
- [ ] `docs/artifacts.md:99` states the re-derived `tests/fixtures/` count and size (`git ls-files tests/fixtures | wc -l` and `du -sh tests/fixtures`, both quoted in the PR — 23 files at HEAD, 29 after this PR) and no longer claims the prompt archive is empty.
- [ ] The committed record is untouched and shown to be: `bash scripts/verify_samples.sh` reports 100/100, no file under `replays/` appears in the diff, and the PR states that the A-6 census over the committed bytes still reads 78 TIER1 utterances across 44 of 300 games — the leak this task removes leaves the record at 21.15, not here.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — archive first, edit second. `mkdir -p tests/fixtures/prompt_archive/qwen3_6_27b_v4 && cp
agents/strategic/prompts/qwen3_6_27b/*.j2 tests/fixtures/prompt_archive/qwen3_6_27b_v4/`
BEFORE touching a byte, then `diff -r` the two directories and paste the empty output into the
PR. All six files, including the two variant siblings: `build_prompt_renderers(name,
root=_ARCHIVE_ROOT)` loads a whole set, and a missing file only fails when the roll-call lever
is ON. Add the `ARCHIVED_PROMPT_VERSION_SETS` entry now too — with the registry still at v4 the
reverse lookup at :424-451 will find TWO matching sets and fail loud, which is the cheap proof
the seam is wired before it is needed.

Step 2 — the templates. Work from the eleven-site list in the DoD, not from memory, and keep
each edit to the noun. The proof line is the only one whose sentence is rewritten:
"Proof. Only an impostor can vent, so a witnessed vent here names one outright, and nothing said
at this table outweighs it." — note `accusation_round.j2:164` has no comma before "and" and
`vote_ballot.j2:123` does; keep each file's own punctuation so the diff stays one clause wide.
For the section name, `<contradictions>` sits in the register its neighbours already use
(`persona`, `voice`, `memory`, `transcript`, `map`, `players`, `rules`) and names the content
rather than an act performed on it. Nothing outside the templates parses the tag: `grep -rn
flagged_contradictions --include=*.py --include=*.ts .` is empty, and A-42 (:4276-4300) measured
zero XML-tag fragments in 11,727 model-authored utterances, so the rename carries no leak risk
of its own. The rendered provenance tag at `vote_ballot.j2:153` is the fiddliest: it is inside a
long one-line Jinja expression, its twin explanation is at `:158`, and
`tests/meetings/test_elicitation_fixtures.py:123` holds it as a constant — change all three or
the fixture asserts a string the template no longer emits.

Step 3 — the map card. Add the frozen name table beside `CANONICAL_MAP_CARD` in
`loader.py` (a `Final[Mapping[str, str]]` under `MappingProxyType`, ten entries, one trailing
provenance line and no history essay), then thread it through `_map_card_from_neighbors` so both
the room and its neighbours render `Name (ID)`. `render_map_card` keeps reading
`PublicMapView.room_neighbors` and nothing else — do NOT widen `PublicMapView`, and do not import
`engine` from `agents/`; `uv run lint-imports` is the gate that will tell you if you drifted. Then
fix the two pins at `tests/agents/test_bespoke_prompt_sets.py:703-734`: the `f"- {room}:
{neighbours}"` assertion at :723 becomes the paired form, and `len(card_lines) <= 12` still holds
at eleven lines. The cross-pin against `load_canonical_map()` goes in the same class; its planted
case can perturb a copy of the name table rather than the file.

Step 4 — the registry. One `version="v5"` in `orchestrator/game.py:392`, one in the variant
registry's spread at `:417`, and the four line-3 markers. Replace the v4 comment block at
`:381-391` with what v5 IS (the in-world flag block, the anchored room register) instead of
appending a fifth paragraph of history — craft rule 1, and that comment is already carrying four
generations. The new marker-line test is small: read each file's first 8 lines, regex
`version\s+(\S+)`, compare to `prompt_versions_for_set("qwen3_6_27b")[key]` (and to the variant
registry for the two `*_roll_call` files).

Step 5 — run the goldens BEFORE the wider suite: `uv run pytest
tests/meetings/test_prompt_byte_golden.py -q`. If a recorded prompt fails to reproduce, the
archived copy is not byte-identical to the pre-PR body — re-copy from `git show HEAD:<path>`
rather than hand-editing. Then `uv run pytest tests/meetings tests/agents -q`, then
`tests/scripts/test_record_ml_corpus.py`. Finally `bash scripts/verify_samples.sh` (100/100) and
`bash scripts/check.sh`.

Step 6 — before pushing, run the blast-radius greps and paste them in the PR: `grep -rn
"qwen3_6_27b.v4" --include=*.py --include=*.sh --include=*.md .` outside `replays/` and `audits/`
must show only intentional history, and `grep -rn "no flag; carried/soft only" .` outside those
two trees must be empty. Note for the reviewer: `scripts/record_ml_corpus.sh` is also edited by
Tasks 21.10 and 21.11 — this task touches ONLY the `REQUIRED_PROMPT_VERSIONS` line, so rebase
conflicts there are one-line and must not be resolved by reverting the re-lock.

## Public types this task introduces
- `agents.strategic.prompts.loader.CANONICAL_ROOM_DISPLAY_NAMES`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import eval.watchability.SupplyFloors"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.replay_walk.ReplayWalkConfig"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-21-dialect-v5` with a title like `task 21.1: the dialect is no longer taught: the oracle voice leaves the templates (prompt set v5)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing A-6 [CONFIRMED, P1] — audits/review-2026-08-26/A/collated-findings.md:693-838 (the origin grep, the perfect causal separation 45/326 vs 0/342, the 78-utterance TIER1 census reproduced to the digit on an independently authored net, the 22-utterance TIER2 "flag as a noun-of-record" tier, the 326/326 conversion, the "NOT the memory render" attribution, the verifier's two nits — the honest ratio is 44 games / 3 seeds and there is a THIRD rendered oracle noun at vote_ballot.j2:135 "the detector already found an innocent reading", which the claim omits and this contract fixes — and the cascade note at :832-833); A-48 [ADJUSTED, P3] — :4781-4854, the register half (240/3602 = 6.66% of turns carry a raw room id across 120/300 games, per-set 141/75/14/10, and the verifier's binding correction: the finder's causal sentence is REFUTED — 3,400 of 7,211 prompts already carry a prose hall name echoed back through the transcript block and the agents prefer prose 3.6:1, so the leak is an UNANCHORED register, not a missing vocabulary; two smaller corrections bind too — the raw-id map card is a deliberate Task 20.31 DoD item at tasks/phase-20.md:5072, and a per-room prose `name` already exists in the map data); A-9 [CONFIRMED, P1] — :1028-1136, context only: the shipped gauge is disjoint from this leak (0/39 overlap, `MACHINERY_VOCABULARY` = two words at eval/deduction_metrics.py:540) and no net runs over `free_text` at all, which is WHY the taught dialect survived to baseline 7; the instrument half is Task 21.9's and no eval module moves here. The standing context every claim below is written against is audits/review-2026-08-26/A/collated-findings.md:4877: baseline 7 is canon by explicit owner override of a FINDING verdict — the pre-registered bars 1 and 2 were missed. Format and mechanics precedent: tasks/phase-20.md:4975-5197 (Task 20.31, the v3→v4 bump that opened and then retired the same archive seam). Anchors re-verified at HEAD (4002f19b): the two oracle lines at agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:164 and vote_ballot.j2:123, both inside `{% if flag_groups.proof %}` (:162-168 / :121-127); agents/strategic/prompts/loader.py:411 `_ROLE_PROOF_KINDS: Final[frozenset[str]] = frozenset({"vent_sighting"})`, so the bucket that renders the line is exactly one kind; the remaining rendered machinery nouns accusation_round.j2:162 + :176 + :252 and vote_ballot.j2:121 + :129 + :135 + :146 + :153 + :158 + :174 + :185 + :192, plus the one shared confidence-rubric phrase at crewmate_report.j2:134 (impostor_report.j2 carries none in its rendered body — its only "flag" hits are inside the `{#- … -#}` header that ends at :64); the version markers at each template's line 3; orchestrator/game.py:322-340 `_bespoke_versions` (four keys, bumped as a unit), :349 `PROMPT_VERSION_SETS` with its four-generation v4 comment block at :381-391 and the entry itself at :392 `"qwen3_6_27b": _bespoke_versions("qwen3_6_27b", version="v4")`, and :415-421 `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`, whose base spread at :417 is the same `version="v4"` call; the archive seam at tests/meetings/test_prompt_byte_golden.py:171-183 (`ARCHIVED_PROMPT_VERSION_SETS = {}` and `tests/fixtures/prompt_archive/` absent since 20.36 retired the v3 entry), its reverse lookup at :424-451, its renderer binding at :848-864 and the one-byte perturbation leg at :1162-1200 (today aimed at the LIVE `crewmate_report.j2`); the registry pins at tests/agents/test_bespoke_prompt_sets.py:505-539 (`TestQwen3627bV4EvidenceHonesty`, whose own docstring still says the committed sets stamp v3 — an F2-class staleness this edit corrects in passing) and tests/agents/test_impostor_answer_arm.py:675-684 + :699-714; the rendered-heading constants at tests/meetings/test_persona_render.py:420-422 and the soft-only marker at tests/meetings/test_elicitation_fixtures.py:123 + :235; the recorder lock at scripts/record_ml_corpus.sh:145-156 with its live-registry equality pin at tests/scripts/test_record_ml_corpus.py:601-620 and the printed dry-run line at :212-226; the map-card render at agents/strategic/prompts/loader.py:371-381 (`_map_card_from_neighbors`), :383-394 (`render_map_card`) and :404 (`CANONICAL_MAP_CARD`), its pins at tests/agents/test_bespoke_prompt_sets.py:703-734, and the ten committed room names in engine/maps/canonical_1.yaml (`engine.world.Room.name`, engine/world.py:118-124) — re-read at HEAD as Admin / Cafeteria / **East Hallway** / Engineering / Labs / MedBay / Reactor / Storage / Upper Hall / **West Hallway**, which corrects A-48's claim text ("`name: East Hall`"); docs/artifacts.md:99 (the `tests/fixtures/` row, `2.0 MB / 23 files`, matching `git ls-files tests/fixtures | wc -l` = 23); the FROZEN default-set pins that must NOT move, tests/orchestrator/test_replay_meetings.py:452-454 and tests/orchestrator/test_meeting_integration.py:2546; docs/glossary.md:140-147 ("flag-minting"), the entry that keeps the word legitimate in the code and the docs while craft rule 4 bans it from the characters' mouths; AGENTS.md craft rules 4, 5, 6, 7.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
