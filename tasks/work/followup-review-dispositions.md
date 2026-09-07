# Disposition the 2026-09-06 review and its follow-up by id

**Status:** ready

## Outcome

Every finding id from the 2026-09-06 review and its follow-up has exactly one
stated disposition somewhere a reader can find it, and each of the first
review's seven workflow recommendations has an explicit adopt-or-decline with a
reason. A reader can go from any id to what was done about it without
reconstructing it from commit messages.

## Evidence

Review claims are leads, not measurements of this tree. Reproduce a disposition
claim against the code before writing "repaired"; a green test is not by itself
a repair of the filed defect.

The id inventories are `audits/review-2026-09-06/REVIEW_APPENDIX_findings.md`
and the follow-up appendix
[`audits/review-2026-09-06/REVIEW_APPENDIX_FOLLOWUP.md`](../../audits/review-2026-09-06/REVIEW_APPENDIX_FOLLOWUP.md),
alongside [the follow-up report](../../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md).
The follow-up's findings FU-DISP-1 and FU-DISP-2 are the gap this card closes:
most appendix ids have no disposition anywhere in the tree, and the first
review's section 11 recommendations were declined by omission rather than by
decision. `docs/cleanup-dispositions.md` is the existing shape — grouped id
rows, a current disposition, and the evidence or owner for each — and its
opening rules already state the distinctions this card must preserve: a retained
limitation is not a repaired defect, and an implemented experimental candidate is
not an adopted behaviour.

## Acceptance

- [ ] Every id in `REVIEW_APPENDIX_findings.md` and every id in
  `REVIEW_APPENDIX_FOLLOWUP.md` appears exactly once, with one of: **repaired**
  (naming the commit or card that repaired it), **retained** (with the reason and
  an explicit reconsideration trigger), **refuted** (with the reasoning), or
  **routed** to a named card. No id appears twice and none is left out.
- [ ] Each of the seven workflow recommendations in section 11 of
  `audits/review-2026-09-06/REVIEW_REPORT.md` gets adopt or decline with a
  one-line reason. Declining is a legitimate outcome; declining silently is not.
- [ ] The shape follows `docs/cleanup-dispositions.md`: grouped id rows, current
  disposition, evidence or owner. A reader can go id to disposition to evidence
  without opening a commit log.
- [ ] A new additive record at
  `audits/review-2026-09-06/followup-correction-record.md` carries the follow-up
  dispositions. It is additive: `correction-record.md` and both review reports
  are not edited to agree with it.
- [ ] No historical severity label, refuter vote or verdict is rewritten. Where
  this tree disagrees with a filed severity, the disagreement is stated as a new
  note beside the original, which stays as filed.
- [ ] No review count is republished as a current measurement of this tree. A
  finding count describes the bytes reviewed then; a claim about now needs its
  own reproduction.
- [ ] A spot check proves the table is not decorative: pick three ids marked
  repaired, reproduce their original triggers, and record that they no longer
  fire.

## Constraints

Documentation only — no runtime, test or recording change, no provider calls, no
new gate. This card can run in parallel with every other card in the batch
because it shares no source file with any of them; it does read their Results, so
re-read a card before writing its disposition rather than writing from the plan.
Historical review bytes are preserved verbatim: the two reports and two
appendices are inputs, never edited. Any `audits/` byte change requires
refreshing the `audits/` row of `docs/artifacts.md` — `verify_ml_evidence.py`
compares that row's exact tracked-byte total and file count against disk.

## Expected scope

`docs/cleanup-dispositions.md`, a new
`audits/review-2026-09-06/followup-correction-record.md`, the `docs/artifacts.md`
audits row, and `tasks/review-ledger.md` where a disposition names a commit.
`audits/review-2026-09-06/REVIEW_REPORT.md`,
`REVIEW_APPENDIX_findings.md`, `REVIEW_REPORT_FOLLOWUP.md` and
`REVIEW_APPENDIX_FOLLOWUP.md` are read-only inputs.

## Record impact

No recorded, rendered or served bytes change; no committed recording, report or
measurement is touched. A disposition table is an account of decisions, not
evidence that a defect is gone: a row saying "repaired" points at the commit and
the reproduction that establishes it. `audits/` tracked bytes move when the new
record lands, so the `docs/artifacts.md` registry row moves with them. Adoption
status of every experiment is unchanged by anything written here.

## Validation

`uv run python scripts/check_doc_facts.py` (link resolution and the audits
index), then `uv run python scripts/validate_task_docs.py`, then
`uv run pytest tests/scripts/test_check_doc_facts.py tests/scripts/test_verify_ml_evidence.py -q`,
then `bash scripts/check.sh`.
