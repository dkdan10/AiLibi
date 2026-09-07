# Close the nonblocking follow-up improvements

**Status:** ready

## Outcome

The operator paths, untested guards and doc gates the follow-up review listed as
worth cards rather than gates are closed, one focused commit each, every one with
a planted failure proving the new check detects the defect it claims.

## Evidence

Review claims are leads, not measurements of this tree. Reproduce each item from
the archived follow-up review
([report](../../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md) section 7,
plus the follow-up appendix) on this checkout before implementing it.

Verified anchors at this tree:
`scripts/run_tournament.py:1210-1215` (protection is scoped to `--output-dir`
and matched by name);
`scripts/_verify_samples.py:55-60` (`VerifyFailure.render`);
`orchestrator/game.py:753` (`MeetingArtifacts.skip_confidence_threshold`,
default `None`), `:757` (the `MeetingRunner` protocol), `:2636` (its consumer);
`observation/temporal.py:71` (`can_watch = observer.alive and not observer.in_vent`);
`meetings/manager.py:1683` (the off-profile `TaskActivityAccount` refusal);
`.env.example:243,244,249,250` (the four new experiment env names);
`tasks/README.md` (derived card and gate counts, and the ownership table);
`api/public_results.py:228-232` with `api/replay_loader.py:949-956` and `:1305`
(`clear_cache`); `orchestrator/recording.py:134-139` (the exclusive probe
descriptors, released before the write) and `:60-67` (the zero-byte rollback).

## Acceptance

One commit per item; each box needs its named planted-failure proof, not merely
an implementation.

- [ ] **NC4-2 / FU-5.** `scripts/run_tournament.py` refuses a `--report-output`
  or `--progress-output` whose basename parses as a recording, regardless of the
  directory it names. Planted proof: a destination outside `--output-dir` whose
  basename is `replay-seed-1.jsonl` is refused before any game runs.
  [Report destinations](report-destinations.md) owns the in-directory alias
  protection this extends; do not weaken it.
- [ ] **FU-03.** `scripts/_verify_samples.py::VerifyFailure.render` prints the
  integrity code instead of `recorded None, reconstructed None` when the recorded
  and reconstructed values are absent. Planted proof: an integrity violation
  carrying a tick renders its code, not two `None`s.
- [ ] **FU-06.** A `MeetingRunner` that resolves under a non-default skip cutoff
  must set `MeetingArtifacts.skip_confidence_threshold`. Document the contract at
  `orchestrator/game.py` on the protocol (`:757`) and the field (`:753`), and
  consider a write-time check so the recorder refuses an unattributable cutoff
  rather than leaving the reader to discover a permanently unreadable recording.
  Planted proof: bytes a custom runner would write are refused at write time, or
  the contract change is shown to make them unwritable.
- [ ] **NC5-02.** Adverse test for the vented v2 observer guard at
  `observation/temporal.py:71`. Planted proof: dropping `not observer.in_vent`
  fails the new test where it passes the whole suite today.
- [ ] **NC5-03.** Adverse test for the off-profile `TaskActivityAccount` refusal
  at `meetings/manager.py:1683`. Planted proof: disabling the guard fails the new
  test where it passes the whole suite today.
- [ ] **P-04.** A `check_doc_facts.py` lever-registry rule covering the four new
  experiment env names in `.env.example` (`AILIBI_EVIDENCE_REASONING`,
  `AILIBI_BOUNDED_REBUTTAL`, `AILIBI_PUBLIC_ACCOUNTS`,
  `AILIBI_ATTRIBUTED_TESTIMONY`). Planted proof: renaming one in `.env.example`
  without updating its documentation fails the gate.
- [ ] **P-05 / CMP-01.** Card and gate counts in `tasks/README.md` are derived
  from `tasks/work/*.md` rather than typed. Planted proof: flipping a card's
  Status to `active` without touching the README fails the gate.
- [ ] **P-06 / P-10.** The `tasks/README.md` ownership label describes the
  current batch rather than a finished one, and `tasks/review-ledger.md` gains a
  row per post-review commit. Planted proof for the ledger half: a post-review
  commit with no ledger row is visible in the check.
- [ ] **CONC-6.** `api/public_results.py`'s `clear_cache()` plus install
  (`:228-232`) is serialised under a per-loader lock, and the loader's `lru`
  keys (`api/replay_loader.py:949-956`) carry a cache-generation counter so a
  same-length, same-mtime replacement during a concurrent cold build cannot
  install pre-flip parsed replays under the post-flip fingerprint. Amend the
  [cache card](public-results-cache.md)'s constraint sentence, which currently
  rules out locking. Planted proof: the controlled interleaving that reproduced
  the silent corrupt install now refuses.
- [ ] **Probe-descriptor lifetime.** Either hold the exclusive probe descriptors
  in `orchestrator/recording.py:134-139` for the recording's lifetime — which
  closes the peer-unlink race the zero-byte rollback at `:60-67` opened, by
  construction — or drop the item and keep the module's existing disclaimer.
  Decide explicitly and record the decision; do not leave it implied.

## Constraints

One commit per item, each with its own planted failure; do not batch them into
one change. No re-record, no committed recording or report rewritten, no
provider calls, no new dependencies, no gameplay behaviour change. Volatile
counts in `tasks/README.md` need an explicit "as of" stamp so a derived number is
never read as a standing measurement. Candidates stay default-OFF and nothing
here adopts one. Concurrency work stays inside the area
`orchestrator/recording.py` already disclaims; this card does not introduce a
multi-process transaction protocol. Coordinate on shared files: the accounts card
owns `meetings/manager.py` and the provenance card owns `api/public_results.py`
and `api/replay_loader.py` — take those items after those cards land, or hand
them over explicitly.

## Expected scope

`scripts/run_tournament.py`, `scripts/_verify_samples.py`,
`scripts/check_doc_facts.py`, `orchestrator/game.py` (docstrings and an optional
write-time check), `orchestrator/recording.py`, `api/public_results.py`,
`api/replay_loader.py`, `tasks/README.md`, `tasks/review-ledger.md`,
`tasks/work/public-results-cache.md` (one constraint sentence), and the matching
tests under `tests/scripts`, `tests/observation`, `tests/meetings`, `tests/api`
and `tests/orchestrator`.

## Record impact

No recorded bytes change: no recording, report, DTO or prompt byte moves, and
the default gameplay path is untouched. Two effects to state plainly. A new doc
gate can newly fail an existing document that was green before — name in Results
which documents the new rules now bind. A `MeetingRunner` contract change or a
write-time cutoff check changes future failure handling for custom runners
without changing any committed recording; no in-tree runner is affected today,
since the shipped runners tally at the default cutoff.

## Validation

`uv run pytest tests/scripts tests/meetings/test_lever_registry.py tests/api/test_public_results.py -q`
for the planted failures, plus the targeted observation and orchestrator tests
each item adds, then `bash scripts/check.sh`, then
`bash scripts/verify_samples.sh`.
