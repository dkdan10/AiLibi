# Agent Prompt — 21.2 The ballot sees what the meeting heard: structured testimony reaches the vote surface, and the redaction stops writing a blank

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.2 — The ballot sees what the meeting heard: structured testimony reaches the vote surface, and the redaction stops writing a blank, anchored to A-17 [ADJUSTED, P1 on the render half] — audits/review-2026-08-26/A/collated-findings.md §A-17 (the template diff, the side-by-side on `replays/ml_corpus/9p2i/replay-seed-1128.jsonl` headless-seed-1128:meeting-0, the memory walk, and the verifier's two label corrections); A-34 [CONFIRMED, P2] — audits/review-2026-08-26/A/collated-findings.md §A-34 (the shipped-normalizer run, the aggregation re-read, the priced distortion, and the verifier's "not a pre-registered bar" bound). Anchors re-verified at HEAD `4002f19b`: `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:110-118` is the whole `<transcript>` block and `:113` its ONE turn line — a `grep -n 'turn\.\|observations\|claim\.'` over that template returns exactly that single hit, reproducing the register's CMD 1; `agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:122-155` is the structured turn body for the SAME turns (`:124-141` the six observation types, `:142-153` the alibi / accusation-reason / corroboration-reason claims, `:154` the `said:` line) — the register cites `:128-155`, which is the observation-type body only; the loop opens at `:122`; `agents/strategic/prompts/loader.py:838-902` `vote_ballot_prompt` already receives the whole `MeetingTranscript` and passes it into the template unchanged, and `meetings/manager.py:1816-1841` threads the full current-meeting `transcript` into it, so the render half is template-only with no plumbing; `meetings/schemas.py:455-497` `MeetingTurn` carries `observations` and `claims` beside `free_text`; `meetings/manager.py:249-252` is `TEAMMATE_COERCED_VOTE_RATIONALE` and `:224-248` the comment whose "the bracket is what keeps this synthetic body out of an instrument it was never model output for" argument A-34 falsifies; `meetings/manager.py:3096-3112` composes marker + preserved markers + that constant; `eval/vj_instruments.py:230` `_LEADING_MARKER_RE`, `:659-666` `_strip_leading_markers`, `:858-864` the per-meeting skeleton build, `:913-916` the top-5 cluster sum with no empty-string exclusion, `:966-977` the published voice cells, `:30-45` and `:135-138` the module docstring's JSON shape; `eval/vj_instruments.py:700-707` `_is_near_dup` returns `False` whenever either token list is empty, which is why echo is untouched; `training/surrogate/ballots.py:939-946` is the named precedent for dropping a guard-authored row and reporting the dropped count; `tests/eval/test_vj_instruments.py:557-572` holds the four voice pins over `replays/samples/9p2i`; `tests/meetings/test_vote_guard_rationale.py:163-167` pins the constant's literal and `:457-488` is the class that argues the bracket keeps it out of the fold; `frontend/src/stories/MeetingView.stories.tsx:247` hardcodes the same literal; `scripts/measure_baseline.py:451-455` is the `--vj` human voice line; `DESIGN.md:595` is the spec sentence the render violates, which lists the rendered memory, the FULL TRANSCRIPT, the contradiction flags and the suspicion graph as what the voting prompt presents; `frontend/src/components/BallotCard.tsx:82-100` is the fog rule that already hides this body from a non-omniscient viewer, and `frontend/src/stories/MeetingView.stories.tsx:239-249` the story that pins the shape. The byte-golden seam this task rebases onto, also re-verified: `tests/meetings/test_prompt_byte_golden.py:183` `ARCHIVED_PROMPT_VERSION_SETS` is `{}` at HEAD and `tests/fixtures/prompt_archive/` does not exist, so a committed set stamping a version the live registry no longer resolves has nowhere to render from until 21.1 re-opens it; `:424-449` is the two-registry resolution, `:1162-1211` the one-byte perturbation leg that proves the golden can fail. Numbers re-derived at HEAD, not quoted from memory: the 18 recorded redaction rows are 5 in `replays/samples/9p2i` (871 ballots) and 13 in `replays/ml_corpus/9p2i` (2,479 ballots), 0 in either 4p1i set.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-ballot-render`
**Depends on:** 21.1
**Section refs:** A-17 [ADJUSTED, P1 on the render half] — audits/review-2026-08-26/A/collated-findings.md §A-17 (the template diff, the side-by-side on `replays/ml_corpus/9p2i/replay-seed-1128.jsonl` headless-seed-1128:meeting-0, the memory walk, and the verifier's two label corrections); A-34 [CONFIRMED, P2] — audits/review-2026-08-26/A/collated-findings.md §A-34 (the shipped-normalizer run, the aggregation re-read, the priced distortion, and the verifier's "not a pre-registered bar" bound). Anchors re-verified at HEAD `4002f19b`: `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:110-118` is the whole `<transcript>` block and `:113` its ONE turn line — a `grep -n 'turn\.\|observations\|claim\.'` over that template returns exactly that single hit, reproducing the register's CMD 1; `agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:122-155` is the structured turn body for the SAME turns (`:124-141` the six observation types, `:142-153` the alibi / accusation-reason / corroboration-reason claims, `:154` the `said:` line) — the register cites `:128-155`, which is the observation-type body only; the loop opens at `:122`; `agents/strategic/prompts/loader.py:838-902` `vote_ballot_prompt` already receives the whole `MeetingTranscript` and passes it into the template unchanged, and `meetings/manager.py:1816-1841` threads the full current-meeting `transcript` into it, so the render half is template-only with no plumbing; `meetings/schemas.py:455-497` `MeetingTurn` carries `observations` and `claims` beside `free_text`; `meetings/manager.py:249-252` is `TEAMMATE_COERCED_VOTE_RATIONALE` and `:224-248` the comment whose "the bracket is what keeps this synthetic body out of an instrument it was never model output for" argument A-34 falsifies; `meetings/manager.py:3096-3112` composes marker + preserved markers + that constant; `eval/vj_instruments.py:230` `_LEADING_MARKER_RE`, `:659-666` `_strip_leading_markers`, `:858-864` the per-meeting skeleton build, `:913-916` the top-5 cluster sum with no empty-string exclusion, `:966-977` the published voice cells, `:30-45` and `:135-138` the module docstring's JSON shape; `eval/vj_instruments.py:700-707` `_is_near_dup` returns `False` whenever either token list is empty, which is why echo is untouched; `training/surrogate/ballots.py:939-946` is the named precedent for dropping a guard-authored row and reporting the dropped count; `tests/eval/test_vj_instruments.py:557-572` holds the four voice pins over `replays/samples/9p2i`; `tests/meetings/test_vote_guard_rationale.py:163-167` pins the constant's literal and `:457-488` is the class that argues the bracket keeps it out of the fold; `frontend/src/stories/MeetingView.stories.tsx:247` hardcodes the same literal; `scripts/measure_baseline.py:451-455` is the `--vj` human voice line; `DESIGN.md:595` is the spec sentence the render violates, which lists the rendered memory, the FULL TRANSCRIPT, the contradiction flags and the suspicion graph as what the voting prompt presents; `frontend/src/components/BallotCard.tsx:82-100` is the fog rule that already hides this body from a non-omniscient viewer, and `frontend/src/stories/MeetingView.stories.tsx:239-249` the story that pins the shape. The byte-golden seam this task rebases onto, also re-verified: `tests/meetings/test_prompt_byte_golden.py:183` `ARCHIVED_PROMPT_VERSION_SETS` is `{}` at HEAD and `tests/fixtures/prompt_archive/` does not exist, so a committed set stamping a version the live registry no longer resolves has nowhere to render from until 21.1 re-opens it; `:424-449` is the two-registry resolution, `:1162-1211` the one-byte perturbation leg that proves the golden can fail. Numbers re-derived at HEAD, not quoted from memory: the 18 recorded redaction rows are 5 in `replays/samples/9p2i` (871 ballots) and 13 in `replays/ml_corpus/9p2i` (2,479 ballots), 0 in either 4p1i set.
**Complexity:** Medium
**Record impact:** the record itself — rendered vote-prompt bytes move, and the body a future coerced ballot records moves with them. Committed replays are frozen: nothing on disk changes here, and the corrected bytes reach the record only at the combined re-record. The instrument half is different in kind — it re-derives four voice cells over the CURRENT committed bytes, so it is re-pinned twice, here and again after the re-record.
**Measurement:** `uv run pytest tests/agents/test_vote_transcript_parity.py tests/meetings/test_vote_guard_rationale.py tests/eval/test_vj_instruments.py -q` green, with the parity gate's planted regression case proving it bites; `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` green — every committed prompt still re-renders byte-identically through the archived v4 bodies; `uv run python scripts/measure_baseline.py replays/samples/9p2i --vj --json` reports `voice_ballots_total` 866, `response_skeleton_share` 0.013856812933025405, `distinct_skeletons` 849, `distinct_skeleton_ratio` 0.9803695150115473 and `guard_authored_ballots_excluded` 5, against the shipped 871 / 0.01722158438576349 / 850 / 0.9758897818599311 / absent.

At the one moment the crew actually decides, the vote prompt shows them a sentence and
nothing else. `vote_ballot.j2:113` renders each turn as speaker, an optional inline
`accuses X (0.90)`, and `free_text` — one line, one field reference in the entire template.
Twenty-five lines away in `accusation_round.j2:122-155` the SAME turns render their
`saw:` block, their alibi rooms and ticks, their accusation and corroboration reasons, and
then `said: "..."`. The register's side-by-side is the whole argument in two lines: p-8's
turn 6 at headless-seed-1128:meeting-0 reaches the accusation round carrying the reason
"Lying about vent to frame me; I was in Admin with p-4 until I killed him, p-5 arrived
after", and reaches the ballot with that reason gone. Pooled over all four committed sets
the ballot render drops at least one field on 3,593 of 3,602 turns — 99.75%, the verifier's
correction to the filing's mislabelled 85.1%, which was the share of turns carrying at least
one OBSERVATION (3,067) rather than the share carrying anything the render drops. The
volume behind that share: 10,320 observations, 1,001 alibi claims, 1,416 corroborations,
3,107 accusation reasons.

Nothing else carries the testimony in for it. The verifier's own walk of the committed
`llm_calls` found current-meeting claim lines in 0 of 3,350 vote prompts — 1,912 of those
prompts carry claim lines, every one of them from a PRIOR meeting. Engine-certified
contradiction flags and the voter's own memory do survive into the ballot, so hard proof
still reaches the vote; spoken testimony from this table does not. And the projection is
unsanctioned rather than designed: DESIGN.md:595 specifies that the voting prompt presents
the rendered memory, the full transcript, the contradiction flags and the suspicion graph,
and `git log` on the template shows four content commits, none of which introduces or
defends a free-text-only turn render.

The fix is cheap because the data is already there. `vote_ballot_prompt` is handed the whole
`MeetingTranscript` and passes it into the template untouched; the manager threads the full
current-meeting transcript into that call. Every field this task renders is already in the
render context and already public to this audience — the accusation round shows the same
rows to the same players minutes earlier. So this is a template edit, not a plumbing change,
and it is the first of A-17's two fix arms. The second arm — ingesting the current meeting's
testimony into pre-vote MEMORY as content — is deliberately NOT taken here: that changes what
agents believe, not what they are shown, and it belongs with the levered testimony work
(`testimony_shapes`), default-OFF, behind its own counterfactual. One more boundary the
verifier binds: A-17's second half, that the impostor's missing roll-call answer is invisible
and unexploited, is the routed balance item G-22, not this task. This contract restores the
render. It makes no claim that the crew will read the tell — P(IMPOSTOR | turn has zero
observations) is 535/535 over 3,602 turns, and no crewmate turn in the four sets carries an
empty observations array at all (0 of 2,674), so the tell exists whether or not anyone uses it.

The second half is a smaller defect with a sharper edge. `TEAMMATE_COERCED_VOTE_RATIONALE`
was written to keep guard prose out of the model-voice fold, and the comment above it says so
in as many words. It does strip — `_strip_leading_markers` loops over `^\[[^\]]*\]\s*` and
removes both the coercion marker and the bracketed note — but what it leaves is an empty
string, and an empty string is a row that clusters. Running the shipped normalizer over the
committed ballots puts `<EMPTY>` at rank 1 in the top-5 skeleton table of BOTH 9p2i sets:
count 5 of 871 in `replays/samples/9p2i`, 13 of 2,479 in `replays/ml_corpus/9p2i`, and the
counter at `:913-916` takes it into the numerator while `:971-976` divides by a denominator
that still counts it. Eighteen guard-authored ballots are being published as the most
stereotyped model voice in the corpus. The distortion is real and bounded: excluding them
moves `response_skeleton_share` 0.01722158438576349 → 0.013856812933025405 and
0.01855587 → 0.015409570154095702 — roughly a quarter of the reported cell, because dropping
the empties promotes the sixth cluster into the top five — and the verifier's bound stands
with it: `response_skeleton_share` is not a Phase-20 pre-registered bar, so today this is a
distorted instrument cell and not a moved gate. Fixing it before the re-ground reads it is
the cheap moment.

Both halves of that defect get fixed, because either alone is half a repair. The recorded
body stops asserting a reason nobody gave: "recorded reason: no confident read this round"
is a fiction — the ballot reads SKIP because a guard rewrote its target, not because the
voter had no confident read — and any consumer reading `rationale_text` reads that fiction as
the voter's account. The note instead states the redirect reason, in the same self-declaring
register, still naming no role, no teammate and no kill and still carrying no `{...!r}`
payload. And the fold stops relying on an accident: excluding a guard-authored ballot because
the strip happened to leave an empty string is not a mechanism, which is exactly why the row
survived into the metric. The instrument excludes by predicate — a ballot with no
model-authored body left after marker-stripping has no model voice to measure — and publishes
the count it dropped, the shape `training/surrogate/ballots.py` already uses for coerced-SKIP
rows. Keying on the predicate rather than on the new literal is what lets the corrected cells
be computed on the CURRENT committed bytes, which still carry the old sentence.

What changes for the reader at the table is small and specific. p-8's turn 6 arrives at the
ballot carrying the reason it was spoken with, so a voter weighing it reads the argument
rather than a bare `accuses p-5 (0.90)`. An alibi that named a room and a tick window is a
room and a tick window again, not a sentence about one. And a turn that carried no
observations at all renders with no `saw:` block, where every other turn has one — the
contrast is simply present on the page, with no instruction anywhere telling anyone to read
it. That is the correct shape for this repair: the vote surface stops erasing what the
meeting produced, and whether the crew makes anything of it is a question for a record, not
a claim this contract makes.

Two renders of the same object that drifted this far apart will drift again, so the repair
ships with the mechanism that stops it. A shared Jinja macro is the obvious answer and is
deliberately refused: factoring the block would move `accusation_round.j2`'s bytes, and that
file belongs to 21.1 in this wave, is stamped by the prompt-set version, and is read
byte-for-byte by the golden against 100 committed replays. Paying that risk to avoid
duplicating twenty lines of template is a bad trade. The gate instead is a test that renders
one transcript through BOTH renderers and asserts the vote render exposes every turn field
the statement render exposes — the guard A-17's own fix sketch asks for, and the thing that
would have caught this defect at the moment it was introduced. It earns its keep immediately:
the register question A-48 raises about raw room identifiers on rendered surfaces is a
property of THIS block, and with the parity gate in place a future answer to it can be written
once and proved to have reached both prompts.

The coordination with 21.1 is mechanical, not editorial. Both tasks change bytes in the same
template, and the repo's version policy says changed template bytes get a new stamp, so both
edits must land inside ONE `qwen3_6_27b` v5 generation — a second bump would mint a stamp for
a body that never recorded anything. 21.1 owns that bump and owns re-opening the byte-golden
archive seam with it: at HEAD `ARCHIVED_PROMPT_VERSION_SETS` is empty and
`tests/fixtures/prompt_archive/` does not exist, because the baseline-7 record retired the
previous entry, so the moment the live registry stops resolving v4 the committed recordings
need the archived v4 bodies to re-render through. This task therefore edits the template and
nothing about versioning, and its golden run is the proof that 21.1's seam is actually
carrying the committed bytes rather than the assertion that it is.

**Files in scope:**
- agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2; (the `<transcript>` block at :110-118 gains the structured turn body accusation_round.j2:122-155 already renders — the ONLY edit this task makes to the template)
- tests/agents/test_vote_transcript_parity.py; (new file: the field-parity gate over the two renders plus its planted regression case)
- meetings/manager.py; (`TEAMMATE_COERCED_VOTE_RATIONALE` at :249-252 and the comment at :224-248 that states its now-falsified rationale — nothing else in this file moves)
- eval/vj_instruments.py; (the voice fold only: the skeleton build at :858-862, the cluster sum at :913-916, the published cells at :966-977, and the JSON shape in the module docstring at :30-45 / :135-138)
- tests/eval/test_vj_instruments.py; (the four moved voice pins at :557-572, the new excluded-count assertions, and a planted case proving the exclusion bites)
- tests/meetings/test_vote_guard_rationale.py; (the literal pin at :163-167, the corrected class docstring at :457-467, and the new fold-level assertion)
- scripts/measure_baseline.py; (the `--vj` human voice line at :451-455 names the excluded count)
- frontend/src/stories/MeetingView.stories.tsx; (the hardcoded sentinel at :247 tracks the constant)

**Files NOT in scope:**
- agents/strategic/prompts/qwen3_5_9b/ and the four dormant bespoke sets (the frozen 9B reference set's bytes and recorded stamp never move — AGENTS.md; only the recording set `qwen3_6_27b` is edited, which is also why `DEFAULT_OLLAMA_NUM_CTX` is not a constraint on this change)
- agents/strategic/prompts/qwen3_6_27b/accusation_round.j2 and the two `*_roll_call.j2` variants (21.1 owns every edit to the turn templates; this task COPIES their turn body and does not touch them — and deliberately introduces no shared Jinja macro, because factoring the block would move accusation_round.j2's bytes under a second owner and put the byte golden at risk for a cosmetic win)
- orchestrator/game.py, tests/agents/test_bespoke_prompt_sets.py, tests/meetings/test_prompt_byte_golden.py, tests/fixtures/prompt_archive/ (the prompt-set version bump and the re-opened byte-golden archive seam belong to 21.1; this task rebases onto them and asserts the golden still passes)
- agents/memory/, meetings/transcript.py (the memory-ingest arm of A-17's fix sketch is levered testimony work, not a render change)
- training/surrogate/ballots.py (its coerced-row handling is READ as the precedent for the exclusion cell; its own marker-kind repair is 21.8's)
- api/replay_loader.py, frontend/src/components/BallotCard.tsx (the display-side marker parse and the fog rule are unchanged by construction — the new note still carries no `{...!r}` payload, so it registers no chip and stays the ballot's clean body; the PR states the re-check rather than editing either)
- meetings/voting.py and the ballot guards themselves (no guard's target, tally or firing condition changes)
- replays/ (no re-record; committed bytes are frozen and move only at the combined re-record)

**Definition of done:**
- [ ] `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2`'s `<transcript>` loop renders the same turn body `accusation_round.j2:122-155` renders: all six observation types (`saw_player`, `saw_move`, `completed_task`, `found_body`, `saw_vent`, `whereabouts`), the `claims:` block with alibi rooms and ticks, the accusation REASON and the corroboration REASON, then `said: "..."` — in the accusation round's exact wording, so a voter reads one register across both prompts.
- [ ] The turn line still OPENS with `- [{{ turn.turn_id }}]`, so `primary_reason_id` stays copyable verbatim and the output-format skeleton at `:189` and its explanation at `:192`, both of which interpolate `transcript.turns[-1].turn_id`, still resolve to a rendered id.
- [ ] The inline `accuses X (conf)` on the header line is REMOVED rather than left beside the new `claims:` row that supersedes it; the PR records the fresh grep proving no consumer parses it — `audits/workflows/extract_gameplay_facts.py:264-272` and `eval/validity.py:178-182` read the suspicion-graph header and row shape only, and nothing in the tree parses a vote-prompt transcript line.
- [ ] The vote template keeps its own empty-transcript line `(no turns recorded)` at `:116`; parity is over the TURN BODY, not over the empty state, because a voter is never the first to speak.
- [ ] `tests/agents/test_vote_transcript_parity.py` asserts the two renders expose the same set of turn fields over a fixture turn carrying ALL six observation types and all three claim types — build the transcript once, render it through `build_prompt_renderers("qwen3_6_27b").statement` and `.vote`, and assert every rendered observation and claim substring present in the statement render is present in the vote render.
- [ ] That gate ships with its planted case: a copy of the template with the structured body removed (or the observations loop deleted) drives the same assertion and FAILS, proving the parity gate bites rather than passing on a render nobody changed.
- [ ] The parity gate also runs over at least one REAL committed meeting, not only a hand-built fixture: load a `kind == "meeting"` row from `replays/ml_corpus/9p2i`, rebuild its `MeetingTranscript` from the recorded `transcript.turns`, and assert the same field parity — a synthetic turn cannot prove the render survives the shapes the corpus actually contains, and the register's own side-by-side came from `replay-seed-1128`.
- [ ] The rendered output is inspected for Jinja whitespace regressions, not only for content: the vote render's `<transcript>` section carries no blank line a turn body did not have in the statement render, and the PR quotes one rendered turn from each prompt side by side.
- [ ] The render-budget cost is measured and published, not assumed: the PR quotes the per-prompt delta over `replays/ml_corpus/9p2i` (this contract measured the structured body at a median 579.2 chars per turn against 302.3 on the flat line, implying a median +1,659 / p95 +2,536 / max +6,715 chars per vote prompt over 432 meetings) against the recorded vote-prompt lengths in that set (n=2,479; median 13,326, p95 15,569, max 18,002) and the recorded statement prompts that already carry the block (n=2,047; median 12,082, max 20,528), and states the worst-case total against `DEFAULT_VOTE_MAX_TOKENS` at `meetings/manager.py:185` and the four-chars-per-token estimate at `llm/budgeted_client.py:95`.
- [ ] `meetings/manager.py`'s `TEAMMATE_COERCED_VOTE_RATIONALE` states the REDIRECT reason — that the vote guard rewrote this ballot's target, so the voter's own stated reason no longer describes the recorded vote — replacing "recorded reason: no confident read this round", a reason no voter gave. It keeps every property the guard depends on: one leading `[...]` with no nested `]`, no `{...!r}` payload, and no naming of a role, a teammate or a kill, so the note is no more disclosing standalone than the string it replaces.
- [ ] The comment at `meetings/manager.py:224-248` is rewritten to what is true now — the bracket keeps the note out of the marker parse and off the spectator card as a chip, and the VOICE-fold exclusion is enforced by `eval.vj_instruments`, not by the strip happening to leave an empty string. Craft rule 1: intent, not a history of the correction.
- [ ] `eval/vj_instruments.py` excludes a ballot with no model-authored body from the voice tier by PREDICATE, not by matching the new literal, so the exclusion covers the 18 rows already on disk and every future one: the per-meeting skeleton list at `:858-862` is built from the surviving ballots, `voice_ballots_total` becomes that surviving count, and `response_skeleton_share` / `distinct_skeleton_ratio` / `within_meeting_echo_rate` divide by it.
- [ ] `ballots_total`, `skip_ballots`, `eject_ballots`, the citation cells and `citation_compliance_rate` are NOT touched by the exclusion — the judgment tier still counts every recorded ballot. `voice_ballots_total` is the seam, and the PR states that the two denominators now differ and why.
- [ ] The excluded count is published rather than absorbed: a new set-level cell reports how many ballots the voice tier dropped, a per-meeting cell gives each row's `distinct_skeletons` its denominator, and both appear in the module docstring's JSON shape and in the `--vj` human render at `scripts/measure_baseline.py:451-455`.
- [ ] The four moved pins in `tests/eval/test_vj_instruments.py` are re-derived from the committed bytes and recorded with their before values in the file's established `# was <old>` style: `voice_ballots_total` 871 → 866, `response_skeleton_share` 0.01722158438576349 → 0.013856812933025405, `distinct_skeletons` 850 → 849, `distinct_skeleton_ratio` 0.9758897818599311 → 0.9803695150115473, and the new excluded cell 5. `distinct_1` (0.10613751730503) and `distinct_2` (0.3636308439587128) are asserted UNCHANGED — an empty skeleton contributes no n-grams — and `echo_ballots` stays 0.
- [ ] The 4p1i pins are asserted unmoved with the reason recorded: neither 4p1i set carries a teammate coercion, so `voice_ballots_total` stays 120, `distinct_skeletons` stays 117, and the new excluded cell reads 0 — the set is the natural control for the change.
- [ ] `tests/eval/test_vj_instruments.py` gains a planted case that proves the exclusion bites: a synthetic ballot whose rationale is marker-only is folded in, and the test asserts it lands in the excluded count and NOT in the skeleton clusters. A gate that only re-states a re-derived number is prose.
- [ ] `tests/meetings/test_vote_guard_rationale.py` is repaired, not weakened: the literal pin at `:163-167` carries the new sentence, the shape assertions at `:469-473` stay exactly as they are, the class docstring at `:457-467` no longer claims the bracket keeps the body out of the voice fold, and the class gains one assertion that the SHIPPED fold excludes a coerced ballot — the property the docstring used to claim and the code did not deliver.
- [ ] `frontend/src/stories/MeetingView.stories.tsx:247` carries the new sentence verbatim so the fog stories keep exercising the real recorded shape, and the PR confirms from a fresh read that `frontend/src/components/BallotCard.tsx:82-100` is still true — the sentence has exactly one writer, and a fogged role-disclosing ballot still shows no rationale at all.
- [ ] `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` passes: every committed prompt in both sample sets re-renders byte-identically through the archived v4 template bodies 21.1 registered, so changing the live vote template does not break the gate that proves the committed record reproduces.
- [ ] The PR states the record consequence in the phase's own terms: committed replays are frozen and unchanged by this task; the corrected vote render and the corrected redaction body enter the record only at the combined re-record, and the four voice cells are re-pinned again there. Baseline 7 is canon by explicit owner override of a FINDING verdict, so no surface here may describe the corrected instrument as restoring a passed bar.
- [ ] Blast radius is stated from a fresh grep, not from this contract: `grep -rn TEAMMATE_COERCED_VOTE_RATIONALE` and a grep for the literal sentence over `.py`, `.ts` and `.tsx` are both re-run and every hit is either edited here or explained in the PR — at drafting time that set is `meetings/manager.py` (definition, use, `__all__`), `tests/meetings/test_vote_guard_rationale.py`, `tests/eval/test_deduction_metrics.py` (symbolic, unaffected), `frontend/src/components/BallotCard.tsx` (doc reference, no literal) and `frontend/src/stories/MeetingView.stories.tsx` (literal).
- [ ] The template edit is confirmed to be the ONLY byte change this task makes to `vote_ballot.j2`: `git diff` on the file touches the `<transcript>` block and nothing in the persona, memory, flag, map, suspicion-graph or output-format regions, so the version generation this task rides carries exactly two authors' edits and both are attributable.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — write the parity gate first and watch it fail at HEAD. `tests/agents/test_bespoke_prompt_sets.py:75-115` already has the fixture pattern to copy: two `MeetingTurn` objects with observations and accusation claims, wrapped in a `MeetingTranscript`, rendered through `build_prompt_renderers("qwen3_6_27b")`. Build ONE richer turn than that fixture — every observation type in `meetings/schemas.py` plus an alibi, an accusation with a reason and a corroboration with a reason — because the shipped fixture carries only `found_body`, `saw_player` and accusations, and a gate blind to `whereabouts` and `saw_move` would not have caught this defect. Assert field-by-field, not by whole-string equality: the two templates legitimately differ in their empty-state line, their surrounding prose and their flag blocks.

Step 2 — the template edit. Copy `accusation_round.j2:122-155` into `vote_ballot.j2`'s loop verbatim, keeping the vote template's `{% if transcript.turns %}` / `{% else %}` / `(no turns recorded)` frame. Jinja whitespace control matters more than it looks: the accusation body relies on `{% if %}` / `{% for %}` block tags each sitting on their own line, and moving one onto a content line changes the rendered bytes. Render both prompts over the same transcript and diff the `<transcript>` sections until the turn bodies match line for line.

Step 3 — the measurement, before you argue the budget is fine. Walk the committed meeting rows in `replays/ml_corpus/9p2i` (`kind == "meeting"`), pull each recorded vote prompt out of `llm_calls` — the vote calls are the ones whose prompt contains `rationale_text` — and each meeting's `transcript.turns`, extract the `<transcript>...</transcript>` section from both the recorded vote prompt and the largest recorded statement prompt in the same meeting, and report the per-turn cost of each shape. That is how the numbers in the DoD were derived; reproduce them rather than trusting them, and put the command in the PR.

Step 4 — the constant. Change the VALUE, never the name: `TEAMMATE_COERCED_VOTE_RATIONALE` is exported at `meetings/manager.py:3998` and imported by two test modules. Before writing the sentence, re-read the three properties `tests/meetings/test_vote_guard_rationale.py:469-488` pins — leading `[`, trailing `]`, no interior `]`, and no marker payload — and write to them. The interior-`]` rule is not cosmetic: a nested bracket stops `_strip_leading_markers` early and leaks a fragment into the fold.

Step 5 — the fold. The cleanest seam is a small public predicate beside `_strip_leading_markers` at `eval/vj_instruments.py:659`, used in exactly two places: the skeleton comprehension at `:858-862`, and the new excluded counter. `voice_ballots_total` at `:966` already exists as a separate field from `ballots_total` — that is the whole reason the change can be surgical. Do NOT touch `ballots_total` at `:903`; the judgment and citation cells divide by it, and moving it would silently re-price `citation_compliance_rate`.

Step 6 — re-derive the pins rather than hand-editing them. Import `_normalize_voice`, `_room_pattern` and `_SKELETON_TOP_K` from `eval.vj_instruments` with the rooms from `engine.world.load_canonical_map()`, fold the committed ballots both ways, and paste the printed values. Note that `engine.world` is the import site — not `engine.map_loader`. Then run the planted case: a marker-only ballot must land in the excluded count and never in a cluster.

Step 7 — the two surfaces that quietly track the constant. `scripts/measure_baseline.py:451-455` builds the `--vj` human voice line as one f-string run; add the excluded count there in the same register as the neighbouring cells, and check `tests/eval/test_vj_instruments.py`'s CLI legs still pass — the human-render test asserts the presence of gauge names, not exact numbers, so it will not tell you if you drop a cell. Then `frontend/src/stories/MeetingView.stories.tsx:239-249`: the literal there is a fixture standing in for a recorded ballot, and the two fog stories below it assert the body stays hidden. Update the string only; the fog assertions must keep passing untouched, which is the check that the new sentence did not change what a viewer can see.

Step 8 — before pushing, run `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` on its own. It is the one gate that reads the live templates against the committed recordings, it is slow enough that it is easy to skip, and it is the gate that tells you whether 21.1's archive seam is actually carrying the committed v4 bytes. If it fails with a template mismatch rather than a reconstruction error, the archive is the problem, not this task's edit.

## Public types this task introduces
- `eval.vj_instruments.has_model_authored_body`
- `eval.vj_instruments.VJInstrumentReport.guard_authored_ballots_excluded`
- `eval.vj_instruments.VJMeetingRow.voice_ballots`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.strategic.prompts.loader"`
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
Open a PR from branch `phase-21-ballot-render` with a title like `task 21.2: the ballot sees what the meeting heard: structured testimony reaches the vote surface, and the redaction stops writing a blank`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing A-17 [ADJUSTED, P1 on the render half] — audits/review-2026-08-26/A/collated-findings.md §A-17 (the template diff, the side-by-side on `replays/ml_corpus/9p2i/replay-seed-1128.jsonl` headless-seed-1128:meeting-0, the memory walk, and the verifier's two label corrections); A-34 [CONFIRMED, P2] — audits/review-2026-08-26/A/collated-findings.md §A-34 (the shipped-normalizer run, the aggregation re-read, the priced distortion, and the verifier's "not a pre-registered bar" bound). Anchors re-verified at HEAD `4002f19b`: `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:110-118` is the whole `<transcript>` block and `:113` its ONE turn line — a `grep -n 'turn\.\|observations\|claim\.'` over that template returns exactly that single hit, reproducing the register's CMD 1; `agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:122-155` is the structured turn body for the SAME turns (`:124-141` the six observation types, `:142-153` the alibi / accusation-reason / corroboration-reason claims, `:154` the `said:` line) — the register cites `:128-155`, which is the observation-type body only; the loop opens at `:122`; `agents/strategic/prompts/loader.py:838-902` `vote_ballot_prompt` already receives the whole `MeetingTranscript` and passes it into the template unchanged, and `meetings/manager.py:1816-1841` threads the full current-meeting `transcript` into it, so the render half is template-only with no plumbing; `meetings/schemas.py:455-497` `MeetingTurn` carries `observations` and `claims` beside `free_text`; `meetings/manager.py:249-252` is `TEAMMATE_COERCED_VOTE_RATIONALE` and `:224-248` the comment whose "the bracket is what keeps this synthetic body out of an instrument it was never model output for" argument A-34 falsifies; `meetings/manager.py:3096-3112` composes marker + preserved markers + that constant; `eval/vj_instruments.py:230` `_LEADING_MARKER_RE`, `:659-666` `_strip_leading_markers`, `:858-864` the per-meeting skeleton build, `:913-916` the top-5 cluster sum with no empty-string exclusion, `:966-977` the published voice cells, `:30-45` and `:135-138` the module docstring's JSON shape; `eval/vj_instruments.py:700-707` `_is_near_dup` returns `False` whenever either token list is empty, which is why echo is untouched; `training/surrogate/ballots.py:939-946` is the named precedent for dropping a guard-authored row and reporting the dropped count; `tests/eval/test_vj_instruments.py:557-572` holds the four voice pins over `replays/samples/9p2i`; `tests/meetings/test_vote_guard_rationale.py:163-167` pins the constant's literal and `:457-488` is the class that argues the bracket keeps it out of the fold; `frontend/src/stories/MeetingView.stories.tsx:247` hardcodes the same literal; `scripts/measure_baseline.py:451-455` is the `--vj` human voice line; `DESIGN.md:595` is the spec sentence the render violates, which lists the rendered memory, the FULL TRANSCRIPT, the contradiction flags and the suspicion graph as what the voting prompt presents; `frontend/src/components/BallotCard.tsx:82-100` is the fog rule that already hides this body from a non-omniscient viewer, and `frontend/src/stories/MeetingView.stories.tsx:239-249` the story that pins the shape. The byte-golden seam this task rebases onto, also re-verified: `tests/meetings/test_prompt_byte_golden.py:183` `ARCHIVED_PROMPT_VERSION_SETS` is `{}` at HEAD and `tests/fixtures/prompt_archive/` does not exist, so a committed set stamping a version the live registry no longer resolves has nowhere to render from until 21.1 re-opens it; `:424-449` is the two-registry resolution, `:1162-1211` the one-byte perturbation leg that proves the golden can fail. Numbers re-derived at HEAD, not quoted from memory: the 18 recorded redaction rows are 5 in `replays/samples/9p2i` (871 ballots) and 13 in `replays/ml_corpus/9p2i` (2,479 ballots), 0 in either 4p1i set.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
