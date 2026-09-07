# Archive the owner's follow-up review beside the first one

**Status:** done

## Outcome

The follow-up review is preserved verbatim beside the first review, in the same
directory and under the same rule: subsequent notes record reproductions and
dispositions without editing the supplied documents.

## Evidence

The [review index](../../audits/review-2026-09-06/README.md) states the rule the
first review was archived under — subsequent correction notes record fresh
reproductions and verification without editing these source documents — and the
follow-up pair falls under it. The follow-up reviews `codex/cleanup` at
`fd1f923c` against main at `cfde4c89`, so its claims attach to that commit and
belong in the same archive as the review it follows. The
[correction record](../../audits/review-2026-09-06/correction-record.md) is
where reproduction and disposition are written instead.

## Acceptance

- [x] The report and its appendix are copied into the review directory
  byte for byte, confirmed by comparing their sha256 digests against the
  supplied files, with no edit of either document.
- [x] The review index, the audits index and the artifacts inventory name the
  new pair, every relative link on the checked documents resolves, and the
  `audits/` inventory row matches the tracked bytes and file count.

## Constraints

The supplied documents are not edited, reformatted or excerpted into. No
runtime source, recording, report or schema byte changes; this is an archive and
its index entries. The reopened cards own their own repairs and gate lines.

## Expected scope

`audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md`,
`audits/review-2026-09-06/REVIEW_APPENDIX_FOLLOWUP.md`,
`audits/review-2026-09-06/README.md`, `audits/README.md`, `docs/artifacts.md`
and this card.

## Record impact

Audit record only. No replay, model, prompt or schema bytes change, and no
committed measurement is restated.

## Validation

Compare the sha256 digest of each copy against its supplied source. Run
`python scripts/check_doc_facts.py`, `python scripts/validate_task_docs.py`,
`python scripts/verify_ml_evidence.py`,
`pytest tests/scripts/test_check_doc_facts.py
tests/scripts/test_verify_ml_evidence.py -q`, Ruff check and format over the
changed sources, and strict mypy over `scripts/check_doc_facts.py`.

## Results

Both copies are byte-identical to the supplied documents:
`c6050188c7907d8a62af78c8560b4ba4ee8c146f9bc28826288fd897afb3ecfa` for the
report and `252309db7e603393321da38247396c7311193b9dd491124e9b01c8009502f950`
for the appendix, each digest equal on the source and on the archived copy.
Neither document was edited.

The review index gained one paragraph and kept the first review's own paragraph
untouched. The audits index names the follow-up pair without a count. The review
directory's index and its correction record are now published documents under
the relative-link rule in `scripts/check_doc_facts.py`, with both-ways tests: a
substituted card link on the record and a substituted appendix link on the index
each fail, naming the document and the missing target, while the committed tree
and the unperturbed fixture copy pass.

Gates on this checkpoint: `scripts/check_doc_facts.py` passed, reporting that
every relative link in 11 front-door and published documents resolves;
`scripts/validate_task_docs.py` passed 390 historical phase tasks, 390 prompts
and 34 work cards; `scripts/verify_ml_evidence.py` reported 60 checks, 48 OK,
0 FAIL, 7 ABSENT and 5 INFO, the absent rows being the evidence-branch bytes a
fresh clone does not carry; `pytest tests/scripts/test_check_doc_facts.py
tests/scripts/test_verify_ml_evidence.py -q` passed 364 tests; Ruff check and
`ruff format --check` passed both changed sources; strict mypy found no issue in
`scripts/check_doc_facts.py`. The `audits/` inventory row was recomputed last,
from the staged tree, to 14,837,891 tracked bytes across 201 files.

<!-- gate paragraph added by the checkpoint commit -->
