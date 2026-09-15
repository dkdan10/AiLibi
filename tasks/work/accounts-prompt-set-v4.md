# Revise the accounts prompt family to v4 so its ballots and turns are bounded

**Status:** done

## Outcome

The candidate arm's account templates carry the three bounds the reference
family already carries: a rationale budget with the truncation warning on the
ballot, the observation-id form shown as a literal example in prose over a
skeleton that keeps the field null, and a one-phrase reason with a "then stop"
reply instruction on the turn. `ACCOUNT_PROMPT_SET_REVISION` reads `v4`, so no recorded stamp can
straddle two generations of the bodies, and the arm-surface digest moves with
them. The execution manifest states, before the next run measures anything,
both ways the candidate's measured surface moves on the treatment arm alone:
the citation repair raises its ejection rate, and the turn bound shortens the
two fields the citation-relevance grader reads. The reference family does not
change, nothing is recorded, and no limit, outcome or rule the run is judged by
moves.

## Evidence

[The diagnosis of 2026-09-15](../diagnosis-2026-09-15-truncation-stop.md)
names the root: the candidate ballot template commissions deliberation, gives
it one unbounded place to land, and the voter with the most to deliberate
about is the impostor. The fourth run stopped at unit 26 of 100 on a
`combined_accounts` ballot whose voter was that seed's impostor, at the vote
cap (`AUTHORIZED_VOTE_MAX_TOKENS`,
`experiments/fresh_deduction_instrument.py:202`; `PerCallCapExceeded`,
`:2412-2417`). The owner approved the memo's section-6 decisions as a set on
2026-09-15; decisions 1 and 2 are this card. Only `combined_accounts` renders
these bodies: it is the arm that sets both account levers
(`experiments/fresh_deduction_instrument.py:937-945`), while `repaired_clock`
(`:931-936`) renders the reference family.

Where the two families differ, read at `10a19df8`:

| Gap | Candidate today | Reference today |
| --- | --- | --- |
| rationale budget | "State a concise reason and honest confidence" (`vote_ballot_accounts.j2:21`); skeleton ends `"rationale_text":"<one short reason>"` (`:23`) | "ONE short sentence (~20 words)" plus "a long rationale can overrun the output limit and truncate the JSON, which discards your vote" (`vote_ballot.j2:270`) |
| citation form | "a reference copied from YOUR OWN private memory" (`:21`); skeleton leaves the field `null` (`:23`) | a literal example, the id with no tag word: `"primary_reason_observation_id": "{{ voter_id }}:12:0"` (`vote_ballot.j2:267`) |
| turn bound | `"reason":"<reason>"` (`_account_rules.j2:38-39`); "explain what it does and does not establish" (`accusation_round_accounts.j2:16`) | `"reason": "<one short phrase>"` (`accusation_round.j2:291`); "Write your reply as 1-2 short sentences, then stop" (`:245`) |
| size | `vote_ballot_accounts.j2`, 23 lines | `vote_ballot.j2`, 273 lines |

The citation gap is a live defect, not a style note. Memory lines render as
`[obs p-1:5:2] ...` (`agents/memory/store.py:589-593`), and that wrapper is
render dressing only: the comment above it already says a ballot cites the raw
`{agent}:{tick}:{seq}` id, not the wrapper (`:587-588`). Thirteen of the
fourteen candidate EJECT citations on the fourth run copied the tag word in.
`meetings/manager.py:3241-3250` nulls an id that is not in the voter's own
valid set, with no suffix-recovery branch by design (`:364-367`), and
`:3778-3800` then coerces the now-uncited EJECT to SKIP whenever the target
carries no contradiction flag: twelve `uncited_coerced` ballots on the
candidate, none on the reference.

`_account_rules.j2` reaches every candidate turn, not just the accusation
round: `_account_opening.j2:11` includes it for both role openings and
`accusation_round_accounts.j2:11` includes it for the replies. Its line 43
already forbids the leak ("Never put a private role, teammate identity or a
bookkeeping score in public speech"), and in 2 of 13 candidate games the
impostor committed its own role and kill to the public transcript anyway. A
prohibition alone did not hold in this register, which is why the length bound
is the lever with evidence behind it (memo section 5 C).

No grader reads a ballot's `rationale_text`, so fix A is measurement-neutral:
the primary outcome and its rubric are about the ejected player's hidden role,
citation presence and citation relevance
(`experiments/fresh_deduction_instrument.py:556-565`). Turn prose is a
different matter, corrected in round 1 of review: `grade_citation_relevance`
(`:3765`) grades a cited TURN through `_turn_bears_on` (`:3726`), which walks
the turn's dumped structure rather than a named field list —
`CITATION_RELEVANCE_RUBRIC` (`:3637-3653`) says "its claims and its free text
included" — and `every_citation_relevant` is a conjunct of
`supported_correct_ejection` (`:3869-3877`). Fix C shortens exactly those two
fields, so it moves a graded input on the treatment arm alone and downward.
Fixes B and C are therefore both declared under Acceptance and in the
manifest; fix A is the only one that touches nothing the run is scored by.

## Acceptance

- [x] Review correction: the v4 ballot skeleton keeps
  `primary_reason_observation_id` null, as `vote_ballot.j2:267`'s skeleton
  does. Three independent verifiers reproduced one residual: the skeleton
  pre-filled the field with the literal `{{ voter_id }}:12:0`, and (a) a
  literal is copyable verbatim into an EJECT, where an id that is not in the
  voter's own valid set is nulled (`meetings/manager.py:3241-3250`, no
  suffix-recovery branch by design, `:364-367`) and the now-uncited ejection
  coerced to SKIP (`:3778-3800`) — the exact defect fix B repairs, re-entering
  through its own example; (b) on the one voter whose real ids the literal
  happens to match (voter `p-N`, tick 12, seq 0), `grade_supported` cannot
  tell a copied example from a citation the voter made, so the treatment arm
  could score a citation it never made; (c) the reference family keeps the
  field `null` in its skeleton and shows the id FORM in prose only. The form
  stays in the prose, built from the voter's own id and without the `obs ` tag
  word, and the prose now says plainly that an ejection resting on a memory
  line replaces that null with the id copied from one of the voter's OWN
  memory lines. The skeleton is a SKIP, which the same line already says needs
  no citation. No reference template is touched.
  `tests/agents/test_public_account_prompts.py::test_every_citation_the_ballot_shows_is_the_bare_id_the_layer_accepts`
  asserts both halves — the bare example in the prose, `null` in the skeleton
  — with a planted failure below.
- [x] Review correction: the third branch of `accusation_round_accounts.j2:16`
  is rendered by a test. Fix C's bound was extended to the no-prior-turn
  opt-in branch (decision 4 below), but every render case passed a
  `prior_turn`, so that branch was reachable by no test and deleting its bound
  left the suite green — a route-around a verifier reproduced and this round
  reproduces again below. `::test_the_account_turn_asks_for_one_short_phrase_and_then_a_stop`
  now also renders the statement with `prior_turn=None`, on every arm and both
  roles, through the same renderer on the same synthetic, seed-free inputs,
  with a planted failure below.
- [x] Review correction: neither the manifest's dated section nor this card
  claims any more that the turn bound is measurement-neutral.
  `grade_citation_relevance` (`experiments/fresh_deduction_instrument.py:3765`)
  grades a cited TURN through `_turn_bears_on` (`:3726`), which walks the
  turn's dumped structure rather than a named field list —
  `CITATION_RELEVANCE_RUBRIC` (`:3637-3653`) says "its claims and its free text
  included" — so fix C's two shortened fields, a turn's `free_text` and a
  claim's `"reason"`, are inputs to `every_citation_relevant`, itself a
  conjunct of `supported_correct_ejection` (`:3869-3877`). The ONE-SIDED EFFECT
  declaration now covers fix C's direction as well — shorter prose names the
  ejected player less often, so more `off_target` verdicts on the candidate arm
  alone — so the second calibration may not attribute a relevance shift to fix
  B alone. Proved by
  `tests/experiments/test_accounts_v4_measurement_surface.py::test_a_cited_turns_free_text_decides_whether_the_citation_is_relevant`
  and `::test_a_cited_turns_claim_reason_decides_relevance_too`, each with a
  planted failure below.
- [x] Review correction: the surviving half of the withdrawn claim is asserted
  rather than merely written down. No grader reads a ballot's `rationale_text`
  — which is why fix A moves no graded input — and
  `::test_no_ballot_grader_reads_the_rationale_text` grades two ballots
  differing only in that field, requiring identical verdicts from both
  `grade_citation_relevance` and `grade_supported`. The withdrawn sentence may
  not come back:
  `::test_the_manifest_does_not_call_the_turn_bound_measurement_neutral` reads
  the dated manifest section and requires it to name the grader path instead.
- [x] Review correction: the planted-failure table's fix C row reads
  `5 failed, 1 passed, 84 deselected`, which is what
  `.venv/bin/python -m pytest tests/agents/test_public_account_prompts.py -q -k
  one_short_phrase` prints with `"reason":"<reason>"` restored on the accusation
  shape. That selector collects 6 of 90 (`--collect-only`), so the cell's
  earlier "2 passed, 83 deselected" could not occur; the prose beside it, which
  names exactly one correctly unaffected case, was already right.
- [x] Fix A, the ballot bound: `vote_ballot_accounts.j2:21` carries
  `vote_ballot.j2:270`'s two sentences, the "~20 words" rationale budget and
  the warning that a long rationale can overrun the output limit and truncate
  the JSON, which discards the vote; `:23`'s skeleton carries the matching
  placeholder. The wording is ported from the reference sentence rather than
  re-invented, so the two families bound the same field the same way.
- [x] Fix B, the citation form: `vote_ballot_accounts.j2:21` shows the id form
  the reference shows at `vote_ballot.j2:267`, the bare
  `{agent}:{tick}:{seq}` id WITHOUT the `obs ` tag word that
  `agents/memory/store.py:590` renders as the `[obs ...]` prefix, with a
  literal example built from the voter's own id; `:23`'s skeleton keeps
  `primary_reason_observation_id` null, as the reference skeleton does, so no
  literal id sits in the object a model copies verbatim. (This item once
  mandated the pre-fill, following the memo's fix-B sketch; round 3 of review
  withdrew that half and the prose alone now carries the form.) No
  prose is aimed at `considered_alternatives`: it is
  `tuple[PlayerId, ...]` (`meetings/schemas.py:765`) and the arm already files
  non-id prose there.
- [x] Fix B's cost is declared, not buried. Thirteen of fourteen candidate
  EJECT citations were nulled and twelve ballots coerced to SKIP on the fourth
  run, so supplying the format converts coerced SKIPs into live ejections on
  the treatment arm only. That is a change in the arm's ejection RATE, which
  `WRONGFUL_EJECTION_TRADEOFF`
  (`experiments/fresh_deduction_instrument.py:590-605`) polices. The card and
  the manifest name it, and the next run reads the wrongful-ejection bound
  against it.
- [x] Fix C, the turn bound: `_account_rules.j2:38-39` asks for one short
  phrase in `"reason"`, matching `accusation_round.j2:291`, and
  `accusation_round_accounts.j2:16` softens "explain what it does and does not
  establish" toward the reference's "1-2 short sentences, then stop"
  (`accusation_round.j2:245`) in both branches of that line. The card records
  that this is also the only proposed lever against the public-transcript role
  leak, that `_account_rules.j2:43` already prohibits it, and that a
  prohibition alone did not hold. The owner's reading of decision 9 on
  2026-09-15 is that the leak does not block the next run on its own, so this
  card does not gate on it. The per-arm leak count is pre-declared as a
  reported diagnostic on
  [the second calibration](fresh-deduction-calibration-2.md).
- [x] `ACCOUNT_PROMPT_SET_REVISION` advances `v3` to `v4`
  (`agents/strategic/prompts/loader.py:1236`) with a docstring bullet in the
  same shape as the three above it, naming the three bounds. The four account
  bodies advance as a unit, which is the property the field exists for
  (`loader.py:1247-1254`), and every stamp
  `public_account_prompt_versions` composes (`:1264-1277`) carries `v4`.
- [x] Every pin that reads the revision is re-checked and stated to DERIVE
  from the constant rather than to hard-code a literal: the composed-stamp
  assertion (`tests/agents/test_public_account_prompts.py:188-191`), the
  `_account_stamps` helper (`:155-172`) and the recorded-capture pin
  (`:204-216`), which asserts that no committed capture already carries a
  stamp composed today. Results states the grep that shows no committed byte
  under `audits/` or `tests/` holds a literal `v3.accounts` stamp, so the bump
  strands no recording.
- [x] The arm-surface digest move is declared rather than discovered. Every
  file of `agents/strategic/prompts/qwen3_6_27b` is hashed into
  `arm_surface_digests` (`experiments/fresh_deduction_instrument.py:4306-4330`,
  with `ARM_SURFACE_SOURCES` at `:4296-4304`), so these edits move it and
  `assert_checkpoint_matches` (`:4755`, the comparison at `:4791-4802`) will
  refuse a resume of any sitting begun before this card. The card names the
  fourth run's checkpoint (PR #458, branch `work/fresh-deduction-run-4` at
  `5f2383ea`, unmerged) as the sitting that becomes unresumable, and states
  that no committed constant pins the digest, so no recorded byte needs
  editing.
- [x] `audits/deduction-candidate/execution-manifest.md` gains a dated section
  "Accounts prompt set v4 (2026-09-15)" stating the change, its basis (the
  diagnosis, linked), and explicitly its ONE-SIDED EFFECT: 13 of 14 candidate
  EJECT citations were nulled and 12 ballots coerced to SKIP on the fourth
  run, so the citation fix raises the candidate's ejection rate on the
  treatment arm only, which `WRONGFUL_EJECTION_TRADEOFF` polices and the next
  run must read against. The section also records that run 4's 24 complete
  units are not poolable with what follows, because the candidate's measured
  surface moved. The frozen analysis strings stay byte-identical (test).
- [x] Planted proofs, each red on the tree before the fix and green after. A
  render test builds the v4 ballot prompt through
  `build_prompt_renderers("qwen3_6_27b", public_account_version=1,
  attributed_testimony_version=1).vote(...)` on synthetic, seed-free inputs
  and asserts the rendered text carries the rationale budget, the truncation
  warning and the literal citation example; it goes red when either sentence
  is removed. A second plant sets the revision back to `v3` and shows the
  stamp assertion fail. A third plant restores `"reason":"<reason>"` in
  `_account_rules.j2` and shows the turn-bound case fail.
- [x] No recording and no re-record. The account templates are reachable only
  behind two default-OFF levers: `public_account_version` and
  `attributed_testimony_version` default to `None`
  (`orchestrator/experiment_config.py:44-45`,
  `meetings/evidence_profile.py:74-75`), `.env.example:249-250` carries both
  switches commented at `0`, and `public_account_prompt_versions` returns
  `None` when neither is set (`loader.py:1260-1261`). Results cites those four
  places and states that no committed recording renders these bodies, so no
  sample is rebuilt and no report is rewritten.
- [x] The `audits/` byte change recomputes `docs/artifacts.md`'s audits row
  (today `15,096,108 tracked bytes / 211 files`, `docs/artifacts.md:109`) with
  the manifest staged, `tasks/README.md`'s derived inventory sentence (`:43`)
  is updated for this card, and `scripts/verify_ml_evidence.py` passes
  offline.

## Constraints

Candidate family only. `vote_ballot.j2`, `accusation_round.j2` and every other
reference template keep their bytes; this card ports from them and does not
edit them. No live provider call of any kind: fake provider only, no
calibration, no recording, no re-record, no re-scored report. The primary
outcome, decision rule, minimum actionable effect, tradeoff bound and
`STOP_RULE` do not change (`experiments/fresh_deduction_instrument.py:556`,
`:569`, `:574`, `:590`, `:619`); this card changes what the candidate is asked
for, never what it is judged by. The authorized limits are the owner's, fixed
by the merge of [the limits card](fresh-deduction-limits-4.md) at `10a19df8`:
turn cap 4,096 and vote cap 1,024, per unit 106,000 / 16,000, run 3,710,000 /
459,000, six hours of model work inside eight elapsed, transport four attempts
at 180 s.
This card moves none of them, and in particular does not raise the vote cap:
the memo rejects that in decision 5 and `STOP_RULE` forbids a run to widen a
limit. The schema is not touched either (decision 4 is No), so
`meetings/schemas.py:766` stays a bare `rationale_text: str`. No held-out band
prefix is generated, printed or opened; bands 3000-3999, 5000-5999, 6000-6999
and the live 7000-7999 stay unread by this card. Any `audits/` byte change
recomputes the `docs/artifacts.md` audits row.

## Expected scope

`agents/strategic/prompts/qwen3_6_27b/vote_ballot_accounts.j2`,
`agents/strategic/prompts/qwen3_6_27b/_account_rules.j2`,
`agents/strategic/prompts/qwen3_6_27b/accusation_round_accounts.j2`,
`agents/strategic/prompts/loader.py` (the revision constant and its
docstring), `tests/agents/test_public_account_prompts.py`,
`audits/deduction-candidate/execution-manifest.md` (the dated section),
`docs/artifacts.md` (the `audits/` row), `tasks/README.md`'s derived inventory
sentence, this card. `_account_opening.j2` is in scope only if fix C's wording
needs it; the reference templates and the instrument
(`experiments/fresh_deduction_instrument.py`) are not in scope at all.

Delivered on `work/accounts-prompt-set-v4` and one pull request into `main`,
merged as a merge commit or a fast-forward and never squashed, with the commit
trailer `Card: tasks/work/accounts-prompt-set-v4.md`. Every acceptance item
that adds a gate carries a planted failure. This card is independent of
[the finish-reason card](featherless-finish-reason.md) and can land in either
order; [the second calibration](fresh-deduction-calibration-2.md) depends on
both and bases on whichever merges last. The card does not depend on
[the fifth freeze](held-out-prefix-freeze-5.md) and does not read its band.

## Record impact

Moves prompt bytes on the candidate arm only and amends the execution manifest
(an `audits/` document) with one dated section. No recording, report, DTO,
metric or weight byte moves; no sample set is rebuilt; no experiment becomes
ON; no adopting record is created. The measured consequence is that the
candidate's arm-surface digest changes, so the fourth run's 24 complete units
are not poolable with anything measured after this card and its checkpoint is
no longer resumable. Every committed account stamp under `audits/` stays at its
recorded revision, because a stamp records which bodies ran, not which bodies
are current: the 2026-09-14 calibration record keeps `v3`
(`audits/deduction-candidate/calibration-2026-09-14/CALIBRATION.md:28`).

## Validation

`uv run pytest tests/agents/test_public_account_prompts.py -q`, then
`uv run pytest tests/agents tests/meetings tests/experiments -q` (fake and
replay providers only), `uv run python scripts/validate_task_docs.py`,
`uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`),
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q`,
`bash scripts/verify_samples.sh`, the four
`uv run python scripts/build_sample_report.py --sample-dir <set> --check`
runs, and `bash scripts/check.sh` to the end rather than to the first gate. Do
not run the live evaluation, a calibration or any provider call as a check.

## Results

Delivered on `work/accounts-prompt-set-v4`. Three candidate templates, the
revision constant, its test pins, one dated manifest section and the two
derived inventory lines. The reference family was read and copied from, never
edited.

### What moved, and where it sits in the architecture

The account bodies are `agents/` strategic prompts — "Strategic reasoning
renders strict-undefined Jinja prompts at meetings" (`docs/architecture.md`,
"Packages"). Everything here is prompt bytes plus the constant that names a
generation of them; no `engine/` byte, no `meetings/` behaviour and no schema
moves, so the determinism story in `docs/architecture.md`'s "Determinism and
the substrate ladder" is untouched and both account levers stay OFF by default.

- `agents/strategic/prompts/qwen3_6_27b/vote_ballot_accounts.j2` — fixes A and
  B, both on the instruction line and the response skeleton (which round 3
  returned to `null`).
- `agents/strategic/prompts/qwen3_6_27b/_account_rules.j2` — fix C's `"reason"`
  bound, on the accusation and the corroboration shape.
- `agents/strategic/prompts/qwen3_6_27b/accusation_round_accounts.j2` — fix C's
  reply instruction.
- `agents/strategic/prompts/loader.py:1248` — `ACCOUNT_PROMPT_SET_REVISION` is
  `v4`, with a docstring bullet in the shape of the three above it.
- `tests/agents/test_public_account_prompts.py` — four new cases, each with a
  planted failure below.
- `audits/deduction-candidate/execution-manifest.md` — the dated section
  "Accounts prompt set v4 (2026-09-15)", and the mechanics-check paragraph's
  candidate input figure re-made (below).
- `docs/artifacts.md:109` and `tasks/README.md:43` — the two derived lines.

### Decisions

1. **Ported, not re-invented.** Fix A carries `vote_ballot.j2`'s own two
   clauses verbatim — "ONE short sentence (~20 words)" and "a long rationale
   can overrun the output limit and truncate the JSON, which discards your
   vote" — and fix C carries `accusation_round.j2`'s `"<one short phrase>"` and
   its "1-2 short sentences ... then stop". The two families now bound the same
   fields in the same words, which is the property that makes the reference
   arm's measured behaviour evidence for the candidate's.
2. **The citation example is shown as a form, and said to be one.** The
   prose shows the form — the bare id, built from the voter's own id — and the
   skeleton keeps `primary_reason_observation_id` null, which is what the
   reference skeleton does and what a SKIP exemplar needs. As first delivered
   the skeleton pre-filled the literal instead, with a sentence beside it
   saying the skeleton shows the FORM rather than the evidence; round 3 of
   review withdrew the pre-fill, because a literal in the copied object is an
   invitation to copy an id the meeting layer nulls exactly as it nulled the
   tag-word ids, and a sentence asking a model not to copy it is the weaker
   half of the pair.
3. **The `[obs ...]` wrapper is named, and the id shown bare.** The prose says
   memory lines render as `[obs p-1:12:0]` and that the id to copy excludes the
   tag word; every id the prompt SHOWS is the bare `{agent}:{tick}:{seq}` form,
   which is what a test now asserts over its prose. Naming the
   wrapper is what the reference does, and the defect was not that voters did
   not cite — 14 of 17 candidate EJECTs did — but that they copied the dressing.
4. **Fix C reached the third branch of the same line.** The card names the two
   branches that carried "explain what it does and does not establish"; the
   no-prior-turn branch of `accusation_round_accounts.j2:16` carried no bound
   at all, and the reference bounds its equivalent branch ("Write 1-2 short
   sentences plus your structured items, then stop", `accusation_round.j2`).
   Leaving it unbounded would have bounded replies and not opening-side turns
   in the same template. Declared as follow-through inside an Expected-scope
   file rather than as a silent extra.
5. **`_account_opening.j2` was not touched.** Fix C's wording did not need it:
   it includes `_account_rules.j2`, so the `"reason"` bound reaches it already,
   and the card puts it in scope only if the wording needs it.
6. **The revision pin is an agreement, not a literal.** The three existing pins
   already DERIVE from the constant — `_account_stamps()` (`:155-172`) composes
   through `public_account_prompt_versions`, the composed-stamp assertion
   (`:188-191`) interpolates `ACCOUNT_PROMPT_SET_REVISION`, and the
   recorded-capture pin (`:204-216`) asserts every composed stamp is ABSENT
   from the two 2026-09-06 captures, which carry `v1`. None hard-codes the
   current value, so none of them goes red when the constant is wound back.
   The new case therefore asserts the agreement instead: a tree that RENDERS
   the three v4 bounds may not compose a stamp from `v1`, `v2` or `v3`.
7. **The manifest's mechanics-check paragraph was re-made.** It quotes the fake
   provider's per-arm input tokens, and longer candidate prompts move the
   candidate figure. Only that arm's number changes (608,664 to 640,552,
   +5.2%) with its two derived figures; the reference arm, every graded count
   and the larger arm's per-unit figure are unchanged, which is the arithmetic
   a prompt-only revision of one arm should produce. Directly necessary
   follow-through in an Expected-scope file:
   `test_the_mechanics_check_paragraph_quotes_the_run_it_describes` is red
   otherwise.

### The three bounds, in the bytes

| Fix | Before (`10a19df8`) | After |
| --- | --- | --- |
| A, rationale budget | "State a concise reason and honest confidence"; skeleton `"rationale_text":"<one short reason>"` | "ONE short sentence (~20 words) in your own voice ... Keep the whole object compact: a long rationale can overrun the output limit and truncate the JSON, which discards your vote"; skeleton `"<one short sentence, ~20 words>"` |
| B, citation form | "a reference copied from YOUR OWN private memory"; skeleton `"primary_reason_observation_id":null` | the bare id named and shown — `(e.g. "primary_reason_observation_id": "p-1:12:0")` — with the `[obs ...]` wrapper named as dressing; skeleton keeps the field `null` (round 3) |
| C, turn bound | `"reason":"<reason>"` x2; "explain what it does and does not establish" | `"reason":"<one short phrase>"` x2; "Write your reply as 1-2 short sentences plus your structured items, then stop" (and the free-text and no-prior-turn branches likewise) |

### The one-sided effect, declared

Fix B is not measurement-neutral and the manifest section says so before
anything is measured: 13 of 14 candidate EJECT citations were nulled on the
fourth run and 12 ballots coerced to SKIP, none on the reference, so supplying
the format converts coerced SKIPs into live ejections on the treatment arm
alone. That is a change in the arm's ejection RATE, which
`WRONGFUL_EJECTION_TRADEOFF` polices and the next run reads the
wrongful-ejection bound against. Run 4's 24 complete units are not poolable
with anything measured after this card, because the candidate's measured
surface moved. Fix A is measurement-neutral — no grader reads a ballot's
`rationale_text` — and fix C is NOT: it shortens the two turn fields
`grade_citation_relevance` reads, so it too moves a graded input, downward and
on the candidate arm alone. Corrected in round 1 of review; see
[the dated subsection below](#review-corrections-round-1-2026-09-15).

### The arm-surface digest, declared rather than discovered

`ARM_SURFACE_SOURCES` plus every file of `agents/strategic/prompts/qwen3_6_27b`
is hashed into `arm_surface_digests`, so all four edited files move it. No
committed constant pins the digest — it is recomputed from the tree — so no
recorded byte needed editing. `assert_checkpoint_matches` compares a resume
against the checkpoint's recorded digests, so the fourth run's sitting (PR
\#458, branch `work/fresh-deduction-run-4` at `5f2383ea`, unmerged) is no longer
resumable. That is the intended consequence of a moved surface.

### No recording, no re-record

The account bodies are reachable only behind two default-OFF levers:
`public_account_version` and `attributed_testimony_version` default to `None`
in `orchestrator/experiment_config.py:44-45` and
`meetings/evidence_profile.py:74-75`, `.env.example:249-250` carries
`AILIBI_PUBLIC_ACCOUNTS` and `AILIBI_ATTRIBUTED_TESTIMONY` commented at `0`,
and `public_account_prompt_versions` returns `None` when neither is set
(`agents/strategic/prompts/loader.py:1272-1273` (the OFF/OFF early return)). No committed recording
renders these bodies, so no sample was rebuilt and no report re-scored;
`bash scripts/verify_samples.sh` and the four `--check` runs below are the
evidence that nothing under `replays/` moved. No literal `v3.accounts` stamp
exists anywhere under `audits/` or `tests/`, so the bump strands no recording:

```
$ grep -rn "v3\.accounts" audits/ tests/ ; echo "exit=$?"
exit=1
```

The only committed stamp that names a revision at all is the 2026-09-14
calibration record, which keeps `v3` by design — a stamp records which bodies
ran, not which bodies are current.

### Planted failures (red before, green after)

Each plant was applied to the working tree, the case run, and the file restored
from a byte-identical copy; the suite is green on the delivered tree (90
passed). Commands are `.venv/bin/python -m pytest
tests/agents/test_public_account_prompts.py -q -k <selector>`.

| Plant | Case | Output |
| --- | --- | --- |
| Fix A: the truncation warning deleted | `-k bounds_its_rationale` | `1 failed, 89 deselected` — `assert 'a long rationale can overrun the output limit and truncate the JSON, which discards your vote' in ...` |
| Fix A: the budget back to "state a concise reason" | `-k bounds_its_rationale` | `1 failed, 89 deselected` — `assert 'ONE short sentence (~20 words)' in ...` |
| Fix B: the run's own defect — `obs ` put back into the example id | `-k bare_id` | `1 failed, 89 deselected` — `assert None ... re.compile('p-\d+:\d+:\d+').fullmatch('obs p-1:12:0')` |
| Fix B: the skeleton pre-filled with the literal example again | `-k bare_id` | `1 failed, 89 deselected` — `assert '"primary_reason_observation_id":null' in '{"voter":"p-1",...'` (row replaced in round 3: the delivered skeleton is `null`, so the round-1 row's plant — "the skeleton back to `null`" — is no longer a plant at all) |
| Fix C: `"reason":"<reason>"` restored on the accusation shape | `-k one_short_phrase` | `5 failed, 1 passed, 84 deselected` — every arm that renders the shape menu; the attributed-only impostor renders no menu and is correctly unaffected (count corrected in round 1 of review) |
| The revision wound back to `v3` with the bodies bound | `-k older_revision` | `1 failed, 89 deselected` — `AssertionError: assert 'v3' not in frozenset({'v1', 'v2', 'v3'})` |

### Verification

Every command run from the worktree with `.venv/bin/python` (`uv run` resolves
the same interpreter), fake and replay providers only. No live provider call,
no calibration, no recording; `scripts/verify_ml_evidence.py` was never run
with `--complete`.

| Command | Result |
| --- | --- |
| `pytest tests/agents/test_public_account_prompts.py -q` | `90 passed` |
| `pytest tests/agents tests/meetings tests/experiments -q` | `3034 passed in 192.21s` |
| `python scripts/validate_task_docs.py` | `390 historical phase tasks and 390 prompts; 59 work cards` |
| `python scripts/check_doc_facts.py` | doc facts, front door, `docs/ml-program.md` and budgets all verified |
| `python scripts/verify_ml_evidence.py` (offline) | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5`; every check passed |
| `pytest tests/scripts/test_verify_ml_evidence.py -q` | `80 passed` |
| `bash scripts/verify_samples.sh` | `All 50 samples verified clean` for `4p1i` and for `9p2i` |
| `python scripts/build_sample_report.py --sample-dir <set> --check` x 4 | `replays/samples/{4p1i,9p2i}` and `replays/ml_corpus/{4p1i,9p2i}` each consistent with its replays |
| `bash scripts/check.sh` | run to the end, real exit code 0: `7717 passed, 20 skipped, 3 xfailed` on the Python side, `19 passed (19) / 515 passed (515)` on the frontend, `All checks passed!` |

The `audits/` byte change is accounted for: with the manifest staged,
`git ls-files audits` is 211 files summing 15,102,525 bytes (was 15,096,108 /
211), and `docs/artifacts.md:109` carries the recomputed row.
`tasks/README.md`'s derived sentence moves with this card's Status flip.

### Held-out discipline

No band prefix was generated for inspection, printed, logged or committed, and
no rendered prompt byte of any band seed appears anywhere in this change. The
new render cases build prompts through
`build_prompt_renderers("qwen3_6_27b", env={}, public_account_version=1,
attributed_testimony_version=1)` on synthetic, seed-free inputs — voter `p-1`,
candidates `p-2`/`p-3`, the literal memory string `"own memory"` and one
hand-written transcript turn. The dry-run figures quoted in the manifest are
aggregate token counts and graded counts from the committed offline mechanics
command, which is what that paragraph has always carried. `GENERATOR_SOURCES`
holds none of the four files this card edits, so the freeze manifest needs no
restamp and was not touched.

### Limitations

1. **A budget bounds the symptom, not the channel.** Decoding is non-thinking
   by the model lock, so deliberation still has nowhere to go but the answer's
   last key. The reference arm shows a bound holding it to ~100 characters
   rather than removing it; the v4 candidate is expected to behave like the
   reference, not like a model with a reasoning channel. The second
   calibration is where that is measured, on at least 60 impostor-authored
   candidate ballots.
2. **Nothing here is evidence that the fix works on the model.** Every gate in
   this card runs the fake or the replay provider. What is asserted is that the
   bytes are present, that the revision cannot straddle two generations, and
   that the arm-surface digest moves — not that the 27B writes shorter
   rationales or cites bare ids.
3. **Fix C mitigates the public-transcript role leak; it does not close it.**
   `_account_rules.j2:43` already prohibits the leak in words and it happened
   anyway in 2 of 13 candidate games. The length bound is the lever with
   evidence behind it, and the per-arm leak count is a reported diagnostic on
   the second calibration rather than a gate here — the owner's reading of
   decision 9.
4. **One stale line reference is left as it is.** The 2026-09-14 calibration
   record cites `agents/strategic/prompts/loader.py:1236` for the constant,
   which the docstring bullet moves to `:1248`. The record keeps its `v3` stamp
   and its commit-time citation by design; editing a recorded calibration to
   chase a line number is not in this card's scope.

### Review corrections, round 1 (2026-09-15)

Three blocking findings from independent review, read against
`a88168ed2db2a9279e4e039f4c91a69f4e85269f`. All three are valid; none is
refuted. Two of them are one defect seen from two lenses, and the third is an
arithmetic error in a quoted count. Nothing the run is judged by moves in this
round either: the repair is to what the record CLAIMS about the change, not to
the change.

**The defect.** The manifest and this card said fixes A and C were
"measurement-neutral in intent — no grader reads rationale or turn prose". The
rationale half is true; the turn-prose half is false, and the diagnosis this
card cites never said it — it says "rationale prose", and the widened clause
was new here. `grade_citation_relevance`
(`experiments/fresh_deduction_instrument.py:3765`) grades a ballot that cites a
TURN through `_turn_bears_on` (`:3726`), which walks
`_every_string_in(turn.model_dump(mode="json"))` rather than a named field
list, deliberately (`:3729-3734`). A turn's `free_text`
(`meetings/schemas.py:591`) and each claim's `reason` (`:417`) are in that
walk, and `CITATION_RELEVANCE_RUBRIC` (`:3637-3653`) says so in as many words:
"its claims and its free text included". `every_citation_relevant` is a
conjunct of `supported_correct_ejection` (`:3869-3877`), which is
`PRIMARY_OUTCOME` (`:556`) and whose rubric names relevance (`:558-565`). Fix C
shortens exactly those two fields and only on the candidate arm
(`_account_rules.j2`'s `"reason"`, `accusation_round_accounts.j2`'s reply
instruction), so it moves a graded input. Reproduced on a synthetic turn at
`a88168ed`:

```
$ PYTHONPATH=. .venv/bin/python -c "
from experiments.fresh_deduction_instrument import _turn_bears_on
from meetings.schemas import MeetingTurn
t = lambda s: MeetingTurn(turn_id='t-1', turn_index=0, speaker='p-9',
    turn_kind='opening', reply_to=None, observations=(), claims=(), free_text=s)
print(_turn_bears_on(t('p-2 was in Reactor at tick 12 and never left.'), 'p-2'),
      _turn_bears_on(t('I have nothing further.'), 'p-2'))
"
True False
```

The same two turns are the committed case
`::test_a_cited_turns_free_text_decides_whether_the_citation_is_relevant`,
which grades a ballot citing each of them and reads `relevant` against
`off_target` rather than the helper's boolean.

**What the record says now.** The manifest's dated section keeps its fix-B
paragraph byte-for-byte and gains a second bolded declaration, "ONE-SIDED
EFFECT, second channel — the turn bound reaches a grader too": it names the
`grade_citation_relevance` / `_turn_bears_on` path and the rubric clause,
states the direction (shorter prose names fewer players, so a ballot citing a
bounded turn is likelier to be graded OFF_TARGET and its unit likelier to score
0), states that the direction is DOWNWARD and on the candidate arm alone, and
states the consequence for the next calibration: two of the three edits move
graded inputs and they push in opposite directions, so a shift in candidate
citation relevance may not be attributed to the citation repair alone. The
surviving half is stated as narrowly as it is true: no grader reads a ballot's
`rationale_text`, so fix A moves prompt bytes and no graded input. This card's
Evidence paragraph and its "one-sided effect, declared" paragraph carry the
same correction in place, because leaving a false sentence standing under a
`- [x]` is what the round is for.

**The claim is enforced, not just written.**
`tests/experiments/test_accounts_v4_measurement_surface.py` is new: five cases
on hand-written turns and ballots — no seed of any band is read, rendered or
constructed in it — asserting the rubric clause, that a cited turn's
`free_text` decides its relevance, that a claim's `reason` decides it too (the
accusation is against a THIRD player, so the subject can only be named in the
`reason`), that two ballots differing only in `rationale_text` grade identically
under `grade_citation_relevance` and `grade_supported`, and that the manifest's
dated section neither carries the withdrawn sentence nor omits the grader path.
It lives beside the instrument it grades rather than in
`tests/agents/test_public_account_prompts.py`, which is where the prompt-byte
gates belong and which would otherwise import `experiments/` across a layer;
`tests/experiments/test_fresh_deduction_instrument.py` is left alone because
the sibling finish-reason card is its one writer this week. A file outside the
card's Expected scope is declared here rather than taken silently.

**The corrected count.** The fix C planted-failure cell said
`5 failed, 2 passed, 83 deselected`. The `one_short_phrase` selector collects 6
of 90 (`--collect-only` prints `6/90 tests collected (84 deselected)`), so
seven cases could never run. Reproduced at `a88168ed` with
`"reason":"<reason>"` restored on the accusation shape:
`5 failed, 1 passed, 84 deselected in 0.17s`, the one pass being the
attributed-only impostor that renders no shape menu — the prose beside the cell
already said exactly that. The cell now reads `5 failed, 1 passed, 84
deselected`. The other five rows were re-checked by the reviewer and reproduce
as written.

**Planted failures for the new gates** (red before, green after; each plant
applied to the working tree, the case run, the file restored byte-identical,
`git status --porcelain` clean afterwards). Commands are
`.venv/bin/python -m pytest tests/experiments/test_accounts_v4_measurement_surface.py -q`:

| Plant | Result |
| --- | --- |
| The withdrawn sentence restored to the manifest's dated section | `1 failed, 4 deselected` (`-k manifest`) — `assert _WITHDRAWN_CLAIM not in section` |
| `free_text` dropped from `_turn_bears_on`'s walk | `2 failed, 3 passed` — the free-text case and the rationale-invariance case, whose cited turn names the subject in its free text |
| `claims` dropped from `_turn_bears_on`'s walk | `1 failed, 4 passed` — the claim-`reason` case only |
| `grade_citation_relevance` made to consult `ballot.rationale_text` | `3 failed, 2 passed` — including the invariance case, which is the point of it |

**Verification, round 1.** Run from the worktree with `.venv/bin/python`, fake
and replay providers only; no live provider call, no calibration, no recording,
and `scripts/verify_ml_evidence.py` was never run with `--complete`.

| Command | Result |
| --- | --- |
| `pytest tests/experiments/test_accounts_v4_measurement_surface.py -q` | `5 passed` |
| `pytest tests/agents/test_public_account_prompts.py -q` | `90 passed` |
| `pytest tests/agents tests/meetings tests/experiments -q` | `3039 passed in 193.81s` (was 3034; the five new cases are the difference) |
| `python scripts/validate_task_docs.py` | `390 historical phase tasks and 390 prompts; 59 work cards` |
| `python scripts/check_doc_facts.py` | doc facts, front door, `docs/ml-program.md` and budgets all verified |
| `python scripts/verify_ml_evidence.py` (offline) | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5`; every check passed |
| `pytest tests/scripts/test_verify_ml_evidence.py -q` | `80 passed` |
| `bash scripts/verify_samples.sh` | `All 50 samples verified clean` for `4p1i` and for `9p2i` |
| `python scripts/build_sample_report.py --sample-dir <set> --check` x 4 | each of the four consistent with its replays |
| `bash scripts/check.sh` | run to the end, real exit code 0: `7722 passed, 20 skipped, 3 xfailed` on the Python side (was 7717), `19 passed (19) / 515 passed (515)` on the frontend, `All checks passed!` |

The `audits/` byte change is re-accounted: the dated section is longer, so
`docs/artifacts.md`'s audits row is recomputed again with the manifest staged
— the tracked `audits/` inventory is 211 files summing 15,103,940 bytes (was
15,102,525 / 211) and `docs/artifacts.md:109` carries the recomputed row.
`tasks/README.md`'s derived sentence does not move: Status stays `done` and no
card's status flips in this round. No `GENERATOR_SOURCES` file is touched, so
no freeze restamp is due, and the arm-surface digest does not move again
either: no file of `agents/strategic/prompts/qwen3_6_27b` and no
`ARM_SURFACE_SOURCES` file changes in this round — the repairs are a manifest
section, a card and one new test.
