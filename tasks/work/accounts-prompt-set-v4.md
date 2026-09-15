# Revise the accounts prompt family to v4 so its ballots and turns are bounded

**Status:** ready

## Outcome

The candidate arm's account templates carry the three bounds the reference
family already carries: a rationale budget with the truncation warning on the
ballot, the observation-id form with a literal example and a pre-filled
skeleton, and a one-phrase reason with a "then stop" reply instruction on the
turn. `ACCOUNT_PROMPT_SET_REVISION` reads `v4`, so no recorded stamp can
straddle two generations of the bodies, and the arm-surface digest moves with
them. The execution manifest states, before the next run measures anything,
that the citation repair raises the candidate's ejection rate on the treatment
arm alone. The reference family does not change, nothing is recorded, and no
limit, outcome or rule the run is judged by moves.

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

No grader reads rationale prose: the primary outcome and its rubric are about
the ejected player's hidden role, citation presence and citation relevance
(`experiments/fresh_deduction_instrument.py:556-565`). Fixes A and C are
therefore measurement-neutral in intent. Fix B is not, and this card says so
under Acceptance and in the manifest.

## Acceptance

- [ ] Fix A, the ballot bound: `vote_ballot_accounts.j2:21` carries
  `vote_ballot.j2:270`'s two sentences, the "~20 words" rationale budget and
  the warning that a long rationale can overrun the output limit and truncate
  the JSON, which discards the vote; `:23`'s skeleton carries the matching
  placeholder. The wording is ported from the reference sentence rather than
  re-invented, so the two families bound the same field the same way.
- [ ] Fix B, the citation form: `vote_ballot_accounts.j2:21` shows the id form
  the reference shows at `vote_ballot.j2:267`, the bare
  `{agent}:{tick}:{seq}` id WITHOUT the `obs ` tag word that
  `agents/memory/store.py:590` renders as the `[obs ...]` prefix, with a
  literal example built from the voter's own id; `:23`'s skeleton pre-fills
  `primary_reason_observation_id` with that example instead of `null`. No
  prose is aimed at `considered_alternatives`: it is
  `tuple[PlayerId, ...]` (`meetings/schemas.py:765`) and the arm already files
  non-id prose there.
- [ ] Fix B's cost is declared, not buried. Thirteen of fourteen candidate
  EJECT citations were nulled and twelve ballots coerced to SKIP on the fourth
  run, so supplying the format converts coerced SKIPs into live ejections on
  the treatment arm only. That is a change in the arm's ejection RATE, which
  `WRONGFUL_EJECTION_TRADEOFF`
  (`experiments/fresh_deduction_instrument.py:590-605`) polices. The card and
  the manifest name it, and the next run reads the wrongful-ejection bound
  against it.
- [ ] Fix C, the turn bound: `_account_rules.j2:38-39` asks for one short
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
- [ ] `ACCOUNT_PROMPT_SET_REVISION` advances `v3` to `v4`
  (`agents/strategic/prompts/loader.py:1236`) with a docstring bullet in the
  same shape as the three above it, naming the three bounds. The four account
  bodies advance as a unit, which is the property the field exists for
  (`loader.py:1247-1254`), and every stamp
  `public_account_prompt_versions` composes (`:1264-1277`) carries `v4`.
- [ ] Every pin that reads the revision is re-checked and stated to DERIVE
  from the constant rather than to hard-code a literal: the composed-stamp
  assertion (`tests/agents/test_public_account_prompts.py:188-191`), the
  `_account_stamps` helper (`:155-172`) and the recorded-capture pin
  (`:204-216`), which asserts that no committed capture already carries a
  stamp composed today. Results states the grep that shows no committed byte
  under `audits/` or `tests/` holds a literal `v3.accounts` stamp, so the bump
  strands no recording.
- [ ] The arm-surface digest move is declared rather than discovered. Every
  file of `agents/strategic/prompts/qwen3_6_27b` is hashed into
  `arm_surface_digests` (`experiments/fresh_deduction_instrument.py:4306-4330`,
  with `ARM_SURFACE_SOURCES` at `:4296-4304`), so these edits move it and
  `assert_checkpoint_matches` (`:4755`, the comparison at `:4791-4802`) will
  refuse a resume of any sitting begun before this card. The card names the
  fourth run's checkpoint (PR #458, branch `work/fresh-deduction-run-4` at
  `5f2383ea`, unmerged) as the sitting that becomes unresumable, and states
  that no committed constant pins the digest, so no recorded byte needs
  editing.
- [ ] `audits/deduction-candidate/execution-manifest.md` gains a dated section
  "Accounts prompt set v4 (2026-09-15)" stating the change, its basis (the
  diagnosis, linked), and explicitly its ONE-SIDED EFFECT: 13 of 14 candidate
  EJECT citations were nulled and 12 ballots coerced to SKIP on the fourth
  run, so the citation fix raises the candidate's ejection rate on the
  treatment arm only, which `WRONGFUL_EJECTION_TRADEOFF` polices and the next
  run must read against. The section also records that run 4's 24 complete
  units are not poolable with what follows, because the candidate's measured
  surface moved. The frozen analysis strings stay byte-identical (test).
- [ ] Planted proofs, each red on the tree before the fix and green after. A
  render test builds the v4 ballot prompt through
  `build_prompt_renderers("qwen3_6_27b", public_account_version=1,
  attributed_testimony_version=1).vote(...)` on synthetic, seed-free inputs
  and asserts the rendered text carries the rationale budget, the truncation
  warning and the literal citation example; it goes red when either sentence
  is removed. A second plant sets the revision back to `v3` and shows the
  stamp assertion fail. A third plant restores `"reason":"<reason>"` in
  `_account_rules.j2` and shows the turn-bound case fail.
- [ ] No recording and no re-record. The account templates are reachable only
  behind two default-OFF levers: `public_account_version` and
  `attributed_testimony_version` default to `None`
  (`orchestrator/experiment_config.py:44-45`,
  `meetings/evidence_profile.py:74-75`), `.env.example:249-250` carries both
  switches commented at `0`, and `public_account_prompt_versions` returns
  `None` when neither is set (`loader.py:1260-1261`). Results cites those four
  places and states that no committed recording renders these bodies, so no
  sample is rebuilt and no report is rewritten.
- [ ] The `audits/` byte change recomputes `docs/artifacts.md`'s audits row
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
