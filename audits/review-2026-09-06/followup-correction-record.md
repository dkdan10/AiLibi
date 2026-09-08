# Follow-up review: disposition of every new finding id

This record is additive. The two supplied reports and their two appendices are
preserved verbatim and are not edited to agree with anything here, and neither is
[the pre-merge correction record](correction-record.md), whose "Follow-up
corrections (2026-09-07)" section stays exactly as it was written. Severities,
refuter votes and verdicts are quoted as filed. Where this tree disagrees with a
filed claim, the disagreement is written here beside the original.

Written 2026-09-08 against `main` at `201849fc`, after the merge of
`codex/cleanup` (#435, `8161689a`).

## What this record disposes

[The follow-up report](REVIEW_REPORT_FOLLOWUP.md) and
[its appendix](REVIEW_APPENDIX_FOLLOWUP.md) reviewed `fd1f923c`. The appendix
carries two kinds of id:

- **Original ids**, in its section A disposition table. Those are the first
  review's, and every one of them is dispositioned in
  [the cleanup disposition ledger](../../docs/cleanup-dispositions.md#the-2026-09-06-review-first-pass-findings),
  together with the ids in the first review's own appendix.
- **New ids**, filed by this follow-up: the round-1 findings in sections B.2
  to B.5, the findings its own adversarial pass did not sustain in section B.6,
  and the round-2 probe findings in sections E and F. All 181 of them are
  dispositioned below, each exactly once.

Between the two documents, all 413 ids in the two appendices have exactly one
disposition, and the ledger carries three more that no appendix holds — `P1-2`,
`C7b-9` and `G4-9`, which the first review withdrew in its own section 9 — for
416 in all. The inventory and that property are mechanical; the command that
rebuilds them is in the card's Results.

Four dispositions, and every id gets exactly one:

- **Repaired** names the commit. A commit, not a green test.
- **Routed** names the card that owns it. Those cards are in flight, and a routed
  row states ownership, never that the work is done.
- **Retained** states the reason and the trigger that would reopen it.
- **Refuted** records that the review's own refuters, or a later reproduction,
  did not sustain the finding as written. The filing stays as filed.

`FU-DISP-1` and `FU-DISP-2` are the gap these two documents close. The review's
own counts — "176 of the 206 finding ids the review left behind have no
disposition anywhere in the tree", and the section A tally — describe `fd1f923c`
and are quoted, never republished as a measurement of this tree.

## Repaired

Every commit below is on `main`. The four merge blockers of section 5 and the
correction-record accuracy item landed before the merge; the branch-policy item
landed after it.

| IDs | Current disposition | Evidence / owner |
| --- | --- | --- |
| NC4-1, FU-01, NC5-04 | Repaired. An interruption before a seed's first recorded row no longer strands the ledger: `--attest-unknown-usage SEED` retains the attempt with its usage recorded as unknown rather than as zero and retries it, the refusal is a labelled error instead of a raw traceback, and the flag is refused alongside any cumulative cap. | `14249a79`; [tournament lifecycle](../../tasks/work/tournament-lifecycle.md). Adverse controls in that commit's body. |
| FU-2 | Repaired. `write_report` emits the shape `--check` compares, so following the tool's own remediation message reproduces a committed legacy report instead of rewriting it. | `29b7bb4a`; reproduced on this tree with an adverse control — [spot check 3](#spot-check-three-repaired-ids-reproduced-on-this-tree). |
| FU-B-01 | Repaired. One recording-filename pattern now feeds the fingerprint, the public completeness check, the loader, the verifier and the manifest reader, so a negative-seed recording cannot be served stale from a warm summary. Every committed fingerprint is unchanged. | `46e74f6d`; also repairs the first review's `M2-F1`. |
| FU-D2, FU-APPX-5, NC4-4 | Repaired. The agent-factory and substrate identity pair rides the first tick row and the terminal row only; rows 1..N-1 inherit row 0. The first tick row is authoritative, and a contradicting later stamp, or a stamp appearing after an unstamped first row, is refused. No committed recording changed. | `24a0fe6a` (`orchestrator/replay.py::record_tick`). |
| CONC-1 | Repaired. A single-game run binds its post-run read-back to the recorded game identity, so a run whose replay path another writer replaced refuses to report an outcome or a cost instead of printing the winner's figures. | `ad0f9b5a`; [recording replacement](../../tasks/work/recording-replacement.md). |
| P-02, FU-3 | Repaired. The pre-merge correction record is qualified by commit: it names the tree each gate ran on, and says which commits changed runtime sources afterwards rather than asserting that none did. | `241a5ca9`. The record's own text carries the correction; this document does not restate it. |
| NC5-10 | Repaired. `.github/workflows/ci.yml` triggers on `main` only; the cleanup branch is gone from the push trigger, and the delivery policy that justified it is retired. | #436 (`081aee15`, content `e9c47c76`). |
| FU-DISP-1, FU-DISP-2 | Repaired by this pass. Every id in both appendices has one stated disposition, and each of the first review's seven section-11 recommendations has an adopt-or-decline with a reason. | [The disposition card](../../tasks/work/followup-review-dispositions.md); this record and [the ledger's first-pass section](../../docs/cleanup-dispositions.md#the-2026-09-06-review-first-pass-findings). |

## Routed to a queued card

Each row names the card that owns the work. The cards are in flight on their own
branches; nothing here says any of them is finished, and a routed row is not
evidence that the defect is gone.

All six cards were re-read at `origin/main` (`201849fc`) before routing. An id is
routed when that card **names it by id**, or when the card carries an
**acceptance item that repairs the same defect**; each row below says which of
the two applies to each id it carries, so a reader can check the claim against
the card. An id that is neither named nor covered by an acceptance item is
retained further down with the adjacent card named as its reconsideration
trigger, even where that card edits the same module — that is why the placement
tests `NC5-05` and `NC5-06` are retained rather than routed to the hardening
card that rewrites those modules.

| IDs | Current disposition | Evidence / owner |
| --- | --- | --- |
| NG3-1, VENT-2, GR-1, FU-D1, GR-6 | Routed. Witnessed vents and third-party sightings must outrank the observer's own routine rows under the production budget, the speaker-controlled uncertainty lines must be bounded and deduplicated, and shedding must be visible rather than silent. Until it lands, every evidence-v2 arm evaluates a starved reasoner. | [Evidence renderer salience](../../tasks/work/evidence-renderer-salience.md) names `NG3-1`, `VENT-2` and `GR-1` by id. `FU-D1` and `GR-6` are routed by mechanism: that card's first acceptance item is exactly the eviction `FU-D1` filed — a witnessed vent and a third-party sighting shed at the default 1,500-token budget — and its third emits the `N further subjects not shown` line that `GR-6` asks for. |
| NC4-3, NC6-1, NG1-7, NC6-2, NC3-1, FU-ORA-2 | Routed. The observation-clock version joins the provenance identity, `view.json` is hashed without its mtime-derived timestamp, both memory guards are bound to the meeting they check, the v3 policy re-decision becomes a profile option that routes through `on_violation`, and a committed format-3 recording is walked against a later tree so "verified" means something. | [Recorded provenance gaps](../../tasks/work/recorded-provenance-gaps.md) names five of the six by id — `NC4-3`, `NC6-1`, `NC6-2`, `NC3-1` and `FU-ORA-2`. `NG1-7` is routed by mechanism: it is the same `view.json` / `created_at` defect as the named `NC6-1` ([appendix](REVIEW_APPENDIX_FOLLOWUP.md) line 2332, "35 of 245 artifact_hashes — every view.json — differ on a fresh run"), and that card's third acceptance item writes `view.json` without the mtime-derived timestamp before hashing it. |
| NC2-1, NC2-2, FU-ALIBI-4, NG2-2, NG3-5, NC2-3, NG2-4, GR-3, FU-ALIBI-8 | Routed. Free text is delimited so no speaker can open a section the prompt structure owns; a conflict needs two distinct speakers, or is labelled as one speaker's self-contradiction and names them; a sighting claim places its own speaker; the teammate firewall covers every observation kind the menu elicits; the reply prompt asks only for what the schema expresses; and the vent-certificate trade-off is stated in both candidate checkpoints. | [Accounts channel hardening](../../tasks/work/accounts-channel-hardening.md) names `NC2-1`, `NC2-2`, `NC2-3`, `NG2-2`, `NG2-4`, `NG3-5` and `FU-ALIBI-4` by id. `GR-3` and `FU-ALIBI-8` are routed by mechanism to its seventh acceptance item, the one that states the vent-certificate trade-off in both candidate checkpoints: they are the disclosure half — the deliberate loss of the shared vent certificate — which that card records rather than repairs. |
| GEV-1, GEV-7, GEV-9, NG2-6 | Routed. The smallest useful fresh-model design, the token calibration with its denominator named, the stated minimum actionable effect and stop rule for a metric with no base rate, and a proof-free filter that excludes the killer's own record. | [Fresh-model deduction instrument](../../tasks/work/fresh-deduction-instrument.md) names no finding id at all — it cites sections 11 and 12.4 of the follow-up report instead — so all four are routed by mechanism: `GEV-1` is the design that card implements arm for arm, `GEV-7`'s calibrated token ratios and `GEV-9`'s stop rule are its manifest item (budget, minimum actionable effect and stop rule fixed before any outcome is inspected), and `NG2-6` is its second acceptance item verbatim, "the killer's own record included". No live call is authorized by that card, and the held-out set it consumes is frozen (#438, `23a23c2d`). |
| NC4-2, FU-5, FU-03, FU-06, NC5-02, NC5-03, P-04, P-05, P-06, P-10, CONC-6, FU-04, CONC-2 | Routed. Report-destination refusal by basename regardless of directory, the integrity code in `verify_samples` output, the `MeetingRunner` cutoff contract, adverse tests for the vented-observer and off-profile guards, a lever-registry rule for the four new env names, derived card and gate counts, the ownership label and per-commit ledger rows, the cache clear-and-install window, and an explicit decision on the probe-descriptor lifetime that closes the peer-unlink race. | [Nonblocking follow-up improvements](../../tasks/work/nonblocking-followup-improvements.md), one commit and one planted failure per item; it names all of these by id except `FU-04` and `CONC-2`, which are routed by mechanism to its probe-descriptor item — the item that closes "the peer-unlink race the zero-byte rollback at `:60-67` opened", which is what both ids describe. `P-06`'s stale-ownership half was already corrected in `e9c47c76`; the label and the ledger rows are what remain. |
| NG3-4, NC1-2, FU-ALIBI-1, FU-ALIBI-2, FU-ALIBI-3 | Routed. Four defects that exist only on the temporal-v1 / evidence-v1 path: a prompt whose movement ledger is dated a tick after the same movement's ordered observation, an inverted breadcrumb that places a killer in a room it had not reached, a false impossible-travel accusation after the engine's hub regroup, and a later benign sighting erasing an earlier impossibility. | [Retire temporal v1 and evidence v1](../../tasks/work/retire-temporal-evidence-v1.md), which names all five by id. That card's first acceptance item **blocks** it until an adopting record for evidence v2 exists, so these four stay live until that record is written. |

## Retained

Each row states why the finding stands and what would reopen it. A retained
limitation is not a repaired defect.

| IDs | Current disposition | Evidence / owner |
| --- | --- | --- |
| NG3-2 | Retained by an explicit owner ruling: the default meeting trigger keeps the death-tick body handle, and the fresh-model evaluation states it in its manifest and asserts its absence from the rendered prompts of the frozen prefixes rather than masking it. **Reconsider** if that assertion fails or the owner reverses the ruling. | [Post-merge plan](../../tasks/post-merge-plan.md), ruled with #437 on 2026-09-07. The first review filed the same behaviour as `G1-01`, `G4-1`, `M3-03`, `C4-1`, `GM-4`. |
| NC1-1, NC1-3, NC1-5, NC1-6, NC1-7 | Retained. The v2 entitlement rule covers the event channel while the same tick's snapshot still serves a vented observer; the census counters are exercised by no committed recording because all 300 are temporal-unstamped; same-tick crossings reach only the lower-id actor; and the lever now raises on an unrecognised value, which changed what the string "2" means relative to the reviewed commit. Each is a property of a default-OFF clock that no committed recording uses. **Reconsider** with the first recording made under temporal v2, which is also what would make the counters non-dead. | Candidate path only; `NC1-4` records that the census defect `GL-3` named is resolved. |
| NC1-4, NG3-8, NG3-9, VENT-7, VENT-8 | Retained as verified observations rather than defects: the census counts under both clocks, the crossing asymmetry is the engine's own ordering faithfully projected, a travel check over two observed placements can only return "a walk fits", the v2 vent stamp records the observer's room, and lever-OFF dates a witnessed vent one tick late where v2 repairs it. **Reconsider** when an adopting record for v2 makes the repaired clock the default. | Round-2 probes; each is the review's own re-measurement, quoted, not remeasured here. |
| VENT-3, VENT-4, VENT-6 | Retained. A spoken `saw_vent` mints no placement for the listener's travel check, a vent observation fed to the walking-feasibility check can render as corroboration of the impostor's alibi, and a conflict built from two spoken vent sightings still ends "an unseen vent is not excluded". These are properties of the attributed and accounts arms, all default-OFF, and each one changes what a candidate is worth rather than what the default path does. **Reconsider** as part of the adoption decision for those arms, which weighs the vent-certificate trade-off explicitly. | Follow-up section 6 item 5; [accounts hardening](../../tasks/work/accounts-channel-hardening.md) records the trade-off but does not restore the certificate. |
| NC2-4, NC2-5, NC2-6, NC2-7, NC2-8, NC5-05, NC5-06, NG2-3, NG2-5, NG2-9, NG3-7, FU-ALIBI-5, FU-ALIBI-6, FU-ALIBI-7 | Retained. Candidate-path residue the hardening card does not name: the referee walk that omits the chronology check, v2 silently disabling v1's refinements, a tally that trusts the recording's own cutoff, an untested switch typo path, a dropped disconnected-room case, two placement rules without adverse tests, a missing contradiction-row metric, an arm-conditional vocabulary claim, absence representable only as a private scalar, a death window that ignores the eyewitness's own witnessed kill, and three ungrammatical or mis-attached model-facing lines. All are ON-path only. **Reconsider** in the hardening card's own adverse suite, which touches the same modules — a row closed there should be closed here. | [Accounts channel hardening](../../tasks/work/accounts-channel-hardening.md) is the adjacent writer: it rewrites the sighting-placement rule these tests sit beside, but no queued card names any of these ids and none carries an acceptance item that repairs them — an adverse suite for the destination-only movement rule (`NC5-05`) or the overlap guard (`NC5-06`) is in no card. That is why they are retained under the routing rule stated above rather than routed. |
| NC3-3, NC3-4, NC3-5, NC3-6, NC3-7, NC3-8, NC3-10, NC6-4, NC6-5, NC6-7, NC6-8, NG1-1, NG1-2, NG1-4, NG1-5, NG1-8, NG3-10, P-01 | Retained. The bounded-investigation candidate's own claims and gaps: an unreachable adjacent-body branch, a headline that rests on a tie-break, search pre-empting task travel, a kill-denial artefact, roughly doubled crew movement against a benefit that all-SKIP ballots cannot test, an unobservable self-report arm, search bounds and reductions without adverse tests, a plan shown on the frame the agent is rendered dead, unsurfaced candidate-only completions, an inert meeting-resolution oracle, double-counted perception signatures, and a seed added because it produced the positive case. The direction of the information effect is unmeasured, not negative, and the arm is default-OFF. **Reconsider** when an investigation arm is proposed for measurement; a checkpoint sentence is not a measurement. | Follow-up sections 6 item 7 and 8; the two committed captures stay `MECHANICS_ONLY`. |
| FU-ORA-1, FU-ORA-6, FU-ORA-7, FU-ORA-8, NC5-08, NC5-09, NC6-10, NC6-11, NG2-7, P-11, P-12, GEV-8, GEV-10 | Retained. What "verified" means on the candidate evidence: the render is a shared oracle no check covers, the memory guard's scope is the game rather than the meeting, the reader's rendered text omits the ballot-time override, two harnesses duplicate a measurement core, a dated capture reads as current, source inventories drift with nothing gating them, no committed recording exercises any experiment field, and two scenario definitions are byte-identical apart from their label. The provenance card repairs the two the review made preconditions (`NC6-2`, `FU-ORA-2`); the rest describe a self-consistency guarantee that only an independent instrument can upgrade. **Reconsider** when the fresh-model instrument needs an oracle it does not share with the code under test. | Follow-up sections 6 item 6 and 9; [recorded provenance gaps](../../tasks/work/recorded-provenance-gaps.md) is the adjacent writer. |
| NG4-1, NG4-2, NG4-3, NG4-4, NG4-5, NG4-6, NG4-7, NG4-8, NG4-9, NG4-10 | Retained. Viewer copy and surfaces: withheld rubric scores described as "scored no games", a legend above an empty state, a 1-based evidence clock beside 0-based prompt memory, a plan dated by the snapshot tick, a policy divergence logged as an unparseable row with no visible reason, a raw 404 page in the error banner, a served field no client reads, the ballot payload behind the repaired `G6-2` lens, and a shared URL that silently rewrites the perspective. None changes a recorded byte. **Reconsider** as one viewer-copy card, which the review recommended and the queue has not created. | Follow-up section 7, "Viewer copy". `NG4-8` is the payload half of the first review's `C5-5`. |
| P-03, P-09, FU-DISP-3, FU-DISP-4, NC5-07 | Retained. Process observations about the correction batch itself: a commit body quoting gate counts its own tree fails, unguarded factual counts in `docs/architecture.md`, four process counts that moved the wrong way while the review was being answered, a duplicate-section guard a parenthetical heading suffix walks past (`scripts/validate_task_docs.py:90` keys `sections` on the exact heading text, and only the exact `Results` key is checked at `:117`), and one 100-file commit carrying five cards. The commits are published history and are not rewritten; the one card that carried two Results sections was corrected in `eae31b03`. `grep -rno '/tmp/' tasks/work/ \| wc -l` prints 64 at `fd1f923c`, the commit the follow-up read and the figure its own appendix records for that scope, and 72 at this branch's head, every added match being this same command quoted in the proofs of this pass's card — a quoted pattern, not evidence cited from a host-local path, which is what this row is about; the follow-up's headline 82 → 89 counts `tasks/` and `docs/` together and is a wider scope. Every surviving `codex/cleanup` string is a historical record naming a real branch rather than a policy statement: `git grep -l 'codex/cleanup' \| wc -l` prints 25 at `201849fc`, the commit this pass was written against, and 28 at this branch's head, the three added files being this record, the disposition ledger and the card that quotes the command. **Reconsider** through recommendation 1's derived-count rule and recommendation 2's Validation gate, both dispositioned in the ledger's section 11 table. | [The ledger's section 11 table](../../docs/cleanup-dispositions.md#section-11-workflow-recommendations). No queued card owns `scripts/validate_task_docs.py`. |
| FU-MLEV-1, FU-MLEV-3, FU-MLEV-4, FU-MLEV-6 | Retained. `verify_ml_evidence.py --complete` cannot pass on a clean clone because the archived evidence bytes are not in it and the fetch step is not stated at the claim; `docs/artifacts.md` still quotes the Phase-19 figure; the reading guide's summary is scoped wider than the audit it cites; and the committed findings appendix anchors `WAVE2-02/03/04` at line numbers valid at `9b333a76`. The appendix is preserved verbatim, so its anchors stay as filed by construction. **Reconsider** when the evidence-branch bytes are restored, which is the only thing that would make `--complete` reproducible. | The first review filed the same rows as `GAP-MLEV-1` to `GAP-MLEV-4` and `P1-4`; `scripts/verify_ml_evidence.py`'s offline half is the standing control. |
| FU-APPX-2, FU-APPX-4 | Retained. No test pins the set of fields the demo bundle bakes, and the published bundle note's enumeration of the private data it carries is incomplete while its test pins only the pre-v4 phrase. The accepted limitation itself is the first review's `C7c-9` / `G5-5` / `GAP-FE-5` row. **Reconsider** with the next change to `api/schemas.py`'s served views — that is the change a field-set pin would have caught. | Round-2 refuters found the v4 bake carries nulls and no value on every committed recording. |
| CONC-4, CONC-5, CONC-7, NC4-6 | Retained inside the area `orchestrator/recording.py` already disclaims: a cold burst on `/eval/summary` does not coalesce, a same-mtime replacement during that burst turns the in-flight requests into 500s, a concurrently-written replay is blamed on the wrong cause, and a successful run that writes no bytes restores the previous recording and reports success. The queue's concurrency work is scoped to the clear-and-install window (`CONC-6`) and the probe descriptor, both routed. **Reconsider** if the API is deployed behind concurrent traffic, or if a recording loss is traced to one of these. | Follow-up section 12.6; [nonblocking improvements](../../tasks/work/nonblocking-followup-improvements.md) states that this card does not introduce a multi-process transaction protocol. |
| FU-02, FU-05, FU-B-03, FU-D3, NC4-5, NC5-11 | Retained. A fabricated ballot rationale or transcript turn still loads and serves, because nothing in the tree is an independent oracle for the content of speech; three parallel skip-confidence constants still decide one question; a cache miss clears the shared LRU; a checked acceptance box claims agreement that temporal 2 alone does not deliver; `_serialize`'s sibling is dead production code the docstring still describes; and unstamped historical recordings are tallied against a hard-coded cutoff. `FU-02` is the surviving half of the first review's `C2-2`. **Reconsider** when a recording carries real model speech that a second source can contradict, and in the module that next changes for a card. | Follow-up sections 3.3 and 7. |

## Findings the review's own adversarial pass did not sustain

These are recorded, not counted, exactly as the appendix records them. Their
filings, severities and votes stay as written; nothing here re-opens or re-grades
them, and nothing here claims the underlying behaviour was repaired.

| IDs | Current disposition | Evidence / owner |
| --- | --- | --- |
| FU-1, NC3-2, NC5-01, NC6-3, NC6-6, NG1-3, NG2-1, NG3-3, NG3-6, FU-B-02, NG1-6, P-08, FU-4, FU-D4, NC3-9, NC6-9, NG2-8 | Refuted in round 1. The appendix's section B.6 records, per id, which load-bearing claim failed against the refuter's own regenerated evidence — in most cases the mechanics reproduced exactly and the characterisation did not. | [Appendix section B.6](REVIEW_APPENDIX_FOLLOWUP.md). `FU-1` is the finding `NC4-1` replaced: the mechanic was real, and the repaired form is the attestation path in `14249a79`. |
| VENT-5, VENT-1, GR-2, GR-4, GR-5, CONC-3, FU-APPX-1, FU-APPX-3, FU-MLEV-2, FU-MLEV-5, FU-ORA-3, FU-ORA-4, FU-ORA-5, GEV-2, GEV-3, GEV-4, GEV-5, GEV-6 | Refuted in round 2, by the refuter votes recorded in the appendix's section F verdict index. Two of them matter for the queue and are stated rather than left implicit: the committed harnesses' refusal of real providers is their acceptance criterion and stays (`GEV-2`, `GEV-3`), and the token cap, deadline and varied initial conditions the same probes asked for are requirements of the **new** instrument, which [its card](../../tasks/work/fresh-deduction-instrument.md) carries (`GEV-4`, `GEV-5`). | [Appendix section F](REVIEW_APPENDIX_FOLLOWUP.md). `GR-4`'s refutation also corrected this review's own first reading of its reachability matrix. |

## Spot check: three repaired ids reproduced on this tree

A disposition table is an account of decisions, not evidence that a defect is
gone. Three rows marked repaired were reproduced here: each original trigger was
run on `main` at `201849fc` with the fake provider, and each was paired with an
adverse control showing the check can still fail. No tracked file was left
changed; the perturbation in check 2 was restored and re-verified.

**1. `G5-1` / `GM-1` — the committed `ml_corpus/9p2i` report was stale.** The
original trigger was `build_sample_report.py --check` exiting 1 on that set.

```text
$ uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
--check: replays/ml_corpus/9p2i/tournament-eval-report.json is consistent with its replays.
exit=0
```

All four committed sets answer the same way (`replays/samples/4p1i`,
`replays/samples/9p2i`, `replays/ml_corpus/4p1i`, `replays/ml_corpus/9p2i`; four
`exit=0`). Adverse control, on a scratch copy of `replays/samples/4p1i` with one
game's `seed` changed from 0 to 999:

```text
--check: .../4p1i/tournament-eval-report.json is STALE — it does not match a rebuild from its own replays.
exit=1
```

**2. `C2-6` / `CARD-01` — `tests/orchestrator/` no longer collected on its own.**

```text
$ .venv/bin/python -m pytest tests/orchestrator/ --collect-only -q -p no:cacheprovider
583 tests collected in 0.43s
exit=0
```

Adverse control: deleting the two-line `sys.path` bootstrap from
`tests/orchestrator/test_aborted_meeting_records.py` reproduces the original
failure exactly, and restoring it restores the collection above.

```text
ERROR tests/orchestrator/test_aborted_meeting_records.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
567 tests collected, 1 error in 0.59s
```

**3. `FU-2` — the writer and the committed-report check disagreed.** The original
trigger was that following `--check`'s own remediation message rewrote a
committed legacy report. Reproduction: copy `replays/samples/4p1i` to a scratch
directory, run the writer there, and compare the result with the committed bytes.

```text
$ uv run python scripts/build_sample_report.py --sample-dir <scratch>/4p1i
Wrote <scratch>/4p1i/tournament-eval-report.json: 50 games | ...
$ cmp replays/samples/4p1i/tournament-eval-report.json <scratch>/4p1i/tournament-eval-report.json
IDENTICAL
```

Adverse control, in one process on the same rebuilt report: the pre-correction
serialization — `report.model_dump_json(indent=2)`, taken from the diff of
`29b7bb4a` — does **not** reproduce the committed bytes, while the current
writer does.

```text
HEAD writer bytes == committed report: True
pre-correction writer bytes == committed report: False
byte lengths: committed 2816272 | HEAD 2816272 | pre-correction 2878097
```

That 61,825-byte difference is what following the remediation message would have
committed over each legacy report.

## Corrections to this record

Additive, dated, with the superseded sentence quoted so nothing is silently
rewritten. The two reports, the two appendices and
[the pre-merge correction record](correction-record.md) are untouched by all of
them.

- **2026-09-08, round 1.** The retained `P-03` row carried an unescaped `|`
  inside a code span, and GFM ends a cell at an unescaped `|` even there: the row
  rendered four cells against a three-column header and lost its Evidence link.
  Both in-table pipelines are now written `\|`. The same round replaced "which
  names all six" in the routed section with what that card holds at
  `origin/main` — five ids by name, `NG1-7` by mechanism — and restated the
  routing rule as it was applied.
- **2026-09-08, round 2.** The two counts in the retained `P-03` row were the
  counts of the tree before this pass's own bytes existed, and the round-1 edit
  that repaired the pipe also put both commands into the card, which moved them
  again. The row said "prints 64, unchanged from the follow-up's reading" and
  "27 on this branch, the two added files being this record and the disposition
  ledger". At this branch's head the same commands print 72 and 28, and the third
  file carrying the branch string is the card that quotes them. The row now names
  the tree each figure belongs to. No id, disposition word, routing or spot check
  changed.

## Boundaries

This record changes no recorded, rendered or served byte. It repairs no defect:
the only rows it closes by its own existence are `FU-DISP-1` and `FU-DISP-2`, and
those are traceability, not behaviour. No committed recording, report, metric,
fitted weight or adoption verdict is rewritten, no candidate is adopted, and no
provider was called. The routed rows name cards that are in flight; none of them
is complete, and a row saying "routed" is a statement about ownership only. The
three spot checks establish that three specific triggers no longer fire on this
tree; they say nothing about the rows they do not cover.
