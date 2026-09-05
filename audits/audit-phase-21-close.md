# Phase-21 close — CLOSED: the substrate re-ground on corrected bytes, two operator records spent in one arc, and the pre-registered rule returned FINDING on the second — bar 4 missed, no lever graduated, the ladder tip stands at baseline 8; 34 merged PRs re-verified at close HEAD (the close is the 35th); the next decision routed to the owner (Task 21.26)

**Date:** 2026-09-05.
**Task:** 21.26 — the phase close (owner). Phase 21 was chartered from the two-track Wave-0 audit of
2026-08-26 (`audits/review-2026-08-26/`): repair the substrate the previous phase's own close and
audit found wrong, re-record it, re-ground the ML fits on the corrected corpus, and then measure the
two remaining injustice levers under a pre-registration written before the levers existed. This
close **verifies and routes**: the whole gate re-run at close HEAD by the verifiers' actual paths
(§1), one ledger row per merged PR with a fresh contract-specific command (§2, none silent), the
before/after story in generated numbers with the four pre-registered bars read back (§3), both
records' rulings checked against the tree (§3.3), the two registers' finding→outcome map (§3.4), and
everything the phase routed by name, carried forward with a disposition each (§4), and the routed
next decision put to the owner with a costed recommendation (§5).

**Close HEAD:** `fa739ccb` (= `origin/main` tip at the close session: *"coordination: re-anchor Task
21.26 (the close audit and ledger) to the FINDING outcome at 9618fe95 …"*, on top of the 21.25
merge-reality commit `9618fe95` / PR #429 `d255f5fe`). The clone was complete, not shallow
(`git rev-parse --is-shallow-repository` → `false`), before any history-derived claim below.

**Grounding:** every number below is either read from a committed pin / recorded audit named beside
it, or computed at close HEAD by a command in §8. Everything ran `$0`, deterministic, against the
fake provider. Network was touched only by the named tooling legs: the evidence fetch by pinned sha
(`scripts/fetch_evidence.sh`, §1), the read-only `git ls-remote` queries (§7), and read-only GitHub
API reads of the Pages workflow's run status (§1) and of the merged-PR list (§2, §7).

**One reading convention, so no anchor here is stale on arrival.** Every `tasks/phase-21.md` line
number below reads that file **at close HEAD `fa739ccb`** (`git show fa739ccb:tasks/phase-21.md`).
This PR's own STATUS-banner edit replaces a 4-line block with an 18-line one at the top of that file,
so on the merged tree every anchor below line 3 sits **+14 lines** lower — H-38's citation, quoted as
`:6781` here, reads `:6795` after the merge. Anchors into every other file are at close HEAD and this
PR does not move them.

**Verdict in one line:** Phase 21 **CLOSES COMPLETE** — its other 34 merged PRs (2026-08-27 →
2026-09-05, **#396–#429**, 83 commits from the planning commit through close HEAD) are re-verified
at close HEAD with **34 VERIFIED / 0 DEVIATION-RECORDED** (§2); the default gate is **green at close
HEAD in both the clean and the restored-evidence states**, and for the first time in three closes
**both legs the prior close routed forward come back GREEN as results rather than as debts** — the
opt-in campaign tier reads *"331 passed, 6111 deselected"* exit 0 against the prior close's
*"9 failed, 308 passed"*, and `--complete` reports **no declared grounding gap at all** where it
reported eleven STALE rows (§1); the two records are carried forward as their own contracts' rulings
and never flattened into one — the combined re-record is **maintenance-of-record, no bars and no
verdict**, and the adopting record's pre-registered rule returned **FINDING**, bars 1, 2 and 3 MET
and **bar 4 MISSED at 11/20 = 0.5500 against < 0.40**, so no lever graduated, the **ladder tip stands
at baseline 8**, and the four canonical sets keep their baseline-8 bytes (§3.1, §3.3); and the next
decision goes to the owner as **a next pre-registration that re-parameterises the share-and-count
pair, against the §6.1-shape override and against carrying the slate as toggles** (§5).

**Four close-found defects (F1–F4) and one carried forward (F5).** F1, F2, F3 and F5 are routed to the
next phase's inputs and none of them is fixed here; F4 is half of each — the surface this PR was
already opening is corrected by a dated line, and the record's own README is carried, because a
record is never rewritten. Both mechanical scope admissions are recorded in §6. **F1 is the third
instance in three phases of the same class** — the document that restates the verdict is held by no
gate.

---

## 1. The gate rerun at close HEAD (the WHOLE gate, the verifiers' actual paths)

Every leg below ran at close HEAD `fa739ccb` in ONE session; §8's first block lists them in the order
they actually ran, while the table groups them by leg for reading. The **state** column matters: the
phase-20 close found its F1 precisely by noticing which state each leg was in, so the state is
recorded beside every row rather than assumed.

**The `wall` column is measured, not estimated**, and it is honest about where it comes from: the
whole cycle was re-run end to end on this branch with each leg timed, so the walls are that timed
session's and the quoted outputs are the close-HEAD session's. The two agree everywhere they can —
the campaign tier reads 154.67 s at close HEAD and 159.03 s on the timed re-run, the two `check.sh`
runs report the same counts — because the only difference between the trees is this PR's own
doc-only commits. This session shared a machine with sibling worktrees; the correctness legs are
load-independent and are quoted as measured.

| leg | invocation | state | result (quoted) | wall |
|---|---|---|---|---|
| default gate | `bash scripts/check.sh` | clean | **GREEN — exit 0.** ruff *"All checks passed!"*; format *"406 files already formatted"*; `lint-imports` *"Analyzed 155 files, 834 dependencies."* / *"Contracts: 4 kept, 0 broken."*; *"Task docs validation passed: 390 tasks and 390 prompts."*; *"All 390 prompts are in sync."*; mypy *"Success: no issues found in 377 source files"*; pytest **"6088 passed, 20 skipped, 3 xfailed in 149.84s (0:02:29)"**; frontend lint + `tsc:check` + vitest *"Test Files 9 passed (9) / Tests 440 passed (440)"* + build *"✓ built in 214ms"* | **146 s** |
| evidence restore | `bash scripts/fetch_evidence.sh` | → restored | *"OK: 3269/3269 files match 476a1f85492439277350af9708f1d120eb1c0a71 + 29af85d5457caeba4f8ba8ba77610c6a0ab2213a."* — **TWO** evidence families now, the phase-18 co-evolution slate and the FINDING recording 21.24 landed; the prior close's 2953/2953 is against ONE | **6 s** |
| campaign tier | `uv run pytest -m campaign -q` | restored | **GREEN — exit 0: "331 passed, 6111 deselected in 154.67s (0:02:34)"**. This is the prior close's F1, **CLOSED BY MEASUREMENT** — see below | **160 s** |
| evidence completeness | `uv run python scripts/verify_ml_evidence.py --complete` | restored | *"checks: 63 \| OK 58 \| FAIL 0 \| ABSENT 0 \| INFO 5"* / *"verify-ml-evidence: every check passed."* — exit 0. **There is no STALE column, because there is no STALE status**: 21.17 deleted the amnesty and nothing re-recorded the corpus afterwards to need one (`grep -c STALE scripts/verify_ml_evidence.py` → **0**). The `ML grounding` row reads `OK` with both fingerprints equal at `cc54d3c02a98…` | **29 s** |
| **default gate, again** | `bash scripts/check.sh` | **restored** | **GREEN — exit 0.** mypy *"Success: no issues found in 377 source files"* (the SAME source-file count as the clean run) and pytest **"6088 passed, 20 skipped, 3 xfailed in 132.54s (0:02:12)"**; frontend 440 passed, *"✓ built in 226ms"*. This is the pair `audits/audit-phase-19-close.md` §1 recorded as mutually exclusive; Task 20.17 repaired it, and the repair now holds with a **second** restored family in the tree, which no prior close exercised | **148 s** |
| byte identity | `bash scripts/verify_samples.sh` | restored, **bare env** (`env -i`) | *"All 50 samples verified clean."* (4p1i) / *"All 50 samples verified clean."* (9p2i) — 100/100, with zero `AILIBI_*` exports of any kind. On a FINDING branch this is the leg the ON-stamped recording could not have passed had it overwritten the canonical sets (§3.3) | **2 s** |
| validity gates | `uv run python scripts/validity_gate.py <set>` × 4 | restored | *"Validity gate PASSED (all checks green)."* on all four committed sets, each with *"byte_identical_reconstruction: 0 samples drifted"* and *"cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact"* over 50 / 150 / 50 / 50 games | **12 s** (3 + 7 + 1 + 1) |
| front-door truth | `uv run python scripts/check_doc_facts.py` | restored | exit 0, four lines, and the third is the one this phase added: *"the claim-shaped facts hold across 6 documents, the four bars audits/audit-phase-21-adopting-record.md decided among them"*; also *"the 25-lever substrate registry"* and *"Budgets verified: 4 front-door pages sit inside their word budgets"* | **1 s** |
| evidence clean-up | `bash scripts/fetch_evidence.sh --clean` | → clean | *"Removed 3267 restored file(s). Tracked bytes are untouched."*; afterwards `git status --porcelain` shows nothing but this PR's own five doc edits and `git status --porcelain replays/` is **empty**, **including under the new `replays/records/phase-21-wave2-finding/` destination** — see below | **14 s** |
| evidence completeness, **the other state** | `uv run python scripts/verify_ml_evidence.py --complete` | clean | *"checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5"* — **exit 1**, and that is the check working: `--complete` REFUSES a checkout that holds only the sidecars, and the seven ABSENT rows name both families with the note *"restore with `bash scripts/fetch_evidence.sh`"*. The `ABSENT 7` / `ABSENT 0` pair is the one `audits/audit-phase-21-adopting-record.md` §6.1 records, reproduced here at a different HEAD | **24 s** |
| Pages deploy | `Deploy to GitHub Pages` (`.github/workflows/pages.yml:85`) | — | **success on `fa739ccb`** — run 33950817155, both jobs green (`Build the demo bundle` 50 s, `Deploy to GitHub Pages` 12 s incl. its own verification step). **This is close HEAD, not the close commit** — see the note below | 62 s (GitHub's) |

**The Pages leg is the one that cannot complete before the merge, and it is not claimed as complete.**
`pages.yml` triggers on `push` to `main`, so no run can exist for the close commit until the merge
creates it. What is verified before the merge: the deploy is green on **close HEAD** (the row above),
and the bundle builder that feeds it passes on **this PR's own tree** inside `check.sh`. The
remaining half — the run on the merge commit itself — fires automatically at merge and is the
owner's to observe; the close does not assert it in advance.

**The `--clean` leg, given its own attention, because this phase gave it new work.** The prior
close's cycle only ever placed and removed bytes under `training/`. Task 21.24 added a second
destination, `replays/records/phase-21-wave2-finding/`, which holds **two tracked files**
(`EVIDENCE-MANIFEST.md`, `README.md`) beside a **generated `.gitignore`** and 315 restored,
untracked ones. That is the interaction a `--clean` could plausibly get wrong: remove a tracked file,
leave a generated one behind, or leave the porcelain dirty under a path the bare gate walks.
Measured rather than assumed — after `--clean`, `git status --porcelain replays/` is **empty** and
the whole-tree porcelain shows nothing but this PR's own doc edits. `git status --porcelain
replays/` was empty at every gate in this session.

**And once more on the tree this close leaves behind.** The rows above quote the close-HEAD session,
before this PR's own doc-only commits. The whole cycle was then re-run on the final tree — the close
audit landed, the index entry added, the registry row re-derived, the banners flipped — and every leg
is green again, with the walls above coming from that run. §8's final block lists all twelve legs
with their exit codes.

### F1 — the close audit itself is bound by no gate, and this is the third instance in three phases

`grep -rn 'audit-phase-2[01]-close' scripts/ tests/scripts/` is **EMPTY** at close HEAD. So
`audits/audit-phase-21-close.md` — this document — sits outside `_CLAIM_DOCUMENTS`
(`scripts/check_doc_facts.py`:245-246), outside `_LADDER_TIP_DOCUMENTS` (:249-255), outside
`_FRONT_DOOR_BUDGETS` (:835-840) and outside `check_relative_links`'s scan set. Nothing in the
default tier can fail when the one document that restates the verdict word, the four bar cells, the
ladder tip and dozens of relative links drifts — and the same is true of
`audits/audit-phase-20-close.md`, whose F1 this close corrects by erratum below precisely because
nothing else could.

**It is the F4 class one level up, and the third instance in three phases.** The phase-20 close found
a false ladder tip on `audits/README.md` and routed the gate-coverage half; 21.11 closed that half by
adding `audits/README.md` to `_LADDER_TIP_DOCUMENTS`; 21.25 found a second instance — the phase's
four headline figures ungated — and closed it with `_FINDING_RECORD_AUDIT` + `check_finding_figures`
and six siblings. Each repair covered the surface that had just been caught. The close audit is the
surface nobody has caught yet, and it is the one that speaks last.

**Filed, not fixed** (`scripts/` and `tests/` are out of scope on a close). The minimal gate, sketched
so the next phase inherits a shape and not a complaint: add the close audit to `_CLAIM_DOCUMENTS`;
pin its verdict WORD and its four bar readings against `_FINDING_RECORD_AUDIT`'s §5 table
(`scripts/check_doc_facts.py`:635 with `check_finding_figures` :3577); and add it to
`check_relative_links`'s set — **but that half needs one repair to the checker before it can be
turned on, and this document is the case that proves it.** `relative_targets`
(`scripts/check_doc_facts.py`:4435-4454) runs `_MARKDOWN_LINK` over RAW text with no code-span
stripping, so a close audit that quotes a front-door table cell — as §6 does, with
`` `[audit](…), [contract](tasks/phase-21.md)` `` inside backticks — would resolve that example
against `audits/` and fail on `audits/tasks/phase-21.md`, a path that does not exist. The gate would
bite on a clean document rather than on a broken link, which is the opposite of craft rule 2. So the
routed item is **two lines, not one**: enrol the document, and teach `relative_targets` to skip
inline code first. Per craft rule 2 it ships with its own perturbation cases — a close audit stating
"bar 4 met" or "the ladder tip stands at baseline 9" must fail the DEFAULT tier, a genuinely broken
relative link must fail it, and a *quoted* link inside backticks must NOT.

### F2 — the `docs/artifacts.md` registry rows state a byte count nothing can fail

`scripts/verify_ml_evidence.py::inventory_problems` (:2834-2864) compares a registry row's stated
**file count** against `git ls-files`, and `tests/scripts/test_verify_ml_evidence.py:1871`
(`test_every_counted_registry_row_matches_the_index`, unmarked, therefore DEFAULT tier) runs it. The
only size parse in the file is `_STATED_FILES = re.compile(r"([\d,]+) files")` (:2831); the
`N tracked bytes` half of the same cell is parsed **past** at :3201 and is never compared to
anything.

Two rows in `docs/artifacts.md` write bytes at exact precision — `audits/` at :109 and
`tests/fixtures/` at :101 — and **both are exact at close HEAD**, re-derived from the index rather
than trusted:

```
audits: 8,528,101 tracked bytes / 166 files
tests/fixtures: 2,054,135 tracked bytes / 23 files
```

**This is gate coverage, not staleness**, and the distinction is the finding: today's count-only gate
cannot see the mutation that moves bytes without moving the file count — which is exactly the
**6,894-byte drift 21.15 caught by hand** (`tasks/phase-21.md`:3767). Routed with its perturbation
case: a one-byte edit to a tracked file under `audits/` must fail the DEFAULT tier. The MB/KiB
approximations on the other rows are left alone; they are not falsifiable at byte precision and
generalising to them would be inventing a claim. This PR re-derives the `audits/` row's **both**
halves in the same edit (§6), which is the scope admission the contract names, not the fix.

### F3 — the finding→outcome map this close publishes is held by no gate either

`scripts/check_doc_facts.py::check_review_map` (:4457) is a real gate and it is green — but it is
pinned to `_REVIEW_INDEX` = `audits/review-2026-08-19/README.md` (:236) and to `_PHASE_20_CONTRACT` =
`tasks/phase-20.md` (:238), and its finding-id patterns are `[GC]-\d{1,3}` (:437, :449). The
2026-08-26 registers this phase was chartered from use `A-`/`B-` ids, which those patterns do not
match, in an index the constant does not name. **So §3.4's map below is unguarded**, and this close
says so plainly rather than letting a green checker imply otherwise. The map is published in a form
a reader can check by hand, with the command that derived it in §8.

**Routed, not patched.** The generalization — a review index and a phase contract per phase rather
than one pinned pair, with the id pattern read from the index — is a `scripts/` change with its own
perturbation case (craft rule 2: a mapped row crediting a contract that does not name the finding
back must fail). Claiming a gate that does not exist would be the same defect class in a different
file.

### F4 — two living surfaces called a ratified decision "provisional"; one is fixed here, one is carried

The owner's merge of #428 on 2026-09-04 **ratified the class-(c) landing mechanism** for the FINDING
recording (§3.3). Two surfaces written before that ruling existed still describe it in the present
tense as undecided:

* **`docs/artifacts.md`:195-197** — *"Whether a recording like this is carried in the tree or on a pinned commit is an owner decision that was open when it was taken, and the pinned commit is the provisional answer."*
* **`replays/records/phase-21-wave2-finding/README.md`:43-46** — the same sentence under a `## How the landing may still change` heading.

Neither is gated: `docs/artifacts.md` is not in `_CLAIM_DOCUMENTS`, and the record's own README is a
record and is never rewritten. **The two halves take DIFFERENT dispositions, and the finding says so
rather than carrying both:**

* **`docs/artifacts.md`:195-197 — FIXED HERE**, by one dated additive line, because that page is already open in this PR for the registry row; recorded in §6 as a mechanical scope admission.
* **`replays/records/phase-21-wave2-finding/README.md`:43-46 — CARRIED**, with file, line and the ruling that disagrees with it. It is a record, and a record is never rewritten. It is the only surface still presenting the ratified landing as an open question, and it is the whole of what F4 hands forward.

### F5 — the phase-19 close's F2, still open, carried rather than re-found

`git ls-remote origin 'refs/heads/evidence/*'` at close HEAD returns three refs, and the third is the
one the phase-19 and phase-20 closes both recorded:

```
476a1f85492439277350af9708f1d120eb1c0a71  refs/heads/evidence/phase-18-coevo
29af85d5457caeba4f8ba8ba77610c6a0ab2213a  refs/heads/evidence/phase-21-wave2-finding
c27ab7b5f5e7e10bfab5c6dc752362b137862cac  refs/heads/evidence/raw-slate-staging
```

The shortfall is not silent — it is recorded in `training/artifacts/coevo/EVIDENCE-MANIFEST.md` and
repeated in `docs/artifacts.md` — and its consequence is duplication only, never integrity: the
pinned orphans independently carry and hash every staged byte (§1's restore verified 3269/3269
against the two of them). The remedy remains the manifest's own **one-command owner step**,
`git push origin --delete evidence/raw-slate-staging`, observed read-only here and never executed by
a worker.

### Erratum to `audits/audit-phase-20-close.md` (2026-09-05, additive; that record is not rewritten)

The prior close's F1 diagnosed its three substrate-sha self-consistency pins as reading *"recorded
`f5865c53…`, live `9bc00af0…`"*. **The pair is the other way round**:
`compute_substrate_sha()` returned **`f5865c53…` LIVE** at that HEAD, while
`training/artifacts/anchor_study/study.json` and all 60 `compute_substrate_sha`-kind campaign rows
(36 impostor + 24 crew) **RECORDED `9bc00af0…`** — the pre-graduation composite. Task 21.17
re-derived the pair at its own HEAD and its contract carries the correction
(`tasks/phase-21.md`:4432); this ledger is where the erratum lands, because repeating F1's direction
in the authoritative close audit would publish an already-identified false provenance claim, which is
the exact defect class this phase opened against.

**F1's diagnosis and its routing are unaffected** — the pins disagreed, the eight graduations moved
the composite, and the disposition was to route them to the ML re-ground. Both live values then moved
AGAIN under 21.15's record, so `f5865c53…` is history and not a target: at close HEAD
`training/artifacts/anchor_study/study.json` records `c845602d7e58…` and every one of those pins is
green (§1's campaign leg).

### The two legs the prior close routed forward, read as RESULTS

`audits/audit-phase-20-close.md` §1 recorded `uv run pytest -m campaign` at
**"9 failed, 308 passed, 5327 deselected in 185.78s (0:03:05)"**, exit 1, and `--complete` at
**"checks: 55 | OK 39 | FAIL 0 | STALE 11 | ABSENT 0 | INFO 5"** with the eleven STALE rows named as
the declared ML-grounding gap of `audits/audit-phase-20-baseline-7.md` §10.2. This phase executed
that routing, so both are results here and not defects re-routed.

**The campaign tier: CLOSED BY MEASUREMENT.** `uv run pytest -m campaign -q` reads
**"331 passed, 6111 deselected in 154.67s (0:02:34)"**, exit 0. The nine, by disposition:

| F1's class | the nine pins | disposition at close HEAD |
|---|---|---|
| three substrate-sha self-consistency pins | `tests/training/test_anchor_study.py`, `tests/training/test_coevo_driver.py` ×2 | **RE-GROUNDED by 21.17** (#413) — the coevo pair was RULED rather than forced: it now asserts each block's recorded sha against the campaign's OWN committed provenance (`training/artifacts/coevo/provenance/`), a cross-file pin rather than a live digest a graduation can move |
| five corpus-derived fit pins | four in `tests/training/test_composed_runner.py` (incl. `87 ≠ 96` held-out meetings), one in `tests/training/test_surrogate_fidelity.py` | **RE-GROUNDED by 21.17** — the fits moved onto the baseline-8 corpus and the verdicts were re-derived; `--complete`'s `ML grounding` row now reads `OK` with both fingerprints equal |
| one scenario pin | `tests/training/test_scenarios.py::test_kill_with_witness_fsm_hunts_elsewhere_and_earns_nothing` | **CLOSED by 21.13** (#397), which pre-dated the record and owned it; `uv run pytest tests/training/test_scenarios.py -m campaign -q` → *"53 passed in 2.08s"* |

**The evidence leg: the stronger form, asserted rather than counted.** `--complete` reports **no
declared grounding gap at all** — not `STALE 0`, but no STALE status in the source:
`grep -c STALE scripts/verify_ml_evidence.py` reads **0**, exactly as 21.17 left it and as
`audits/audit-phase-21-adopting-record.md` §6.2 and §7 record as a checked no-op. What 21.24 added to
this command is a second evidence **FAMILY**, not a gap: the FINDING recording's class-(c) payload at
`evidence/phase-21-wave2-finding` @ `29af85d5…`, registered through `_IN_TREE_PROBES`,
`_IN_TREE_INVENTORY`, `_EVIDENCE_PREFIXES` and the manifest parser, so the row reads
`EVIDENCE-BRANCH-RESTORED (315/315 present)` restored — and the close ran the other state too rather
than describing it: on the cleaned checkout the same command reads
**"checks: 60 | OK 48 | FAIL 0 | ABSENT 7 | INFO 5"** and **exits 1**, the seven ABSENT rows naming
both families, so `--complete` cannot be satisfied by a tree that merely holds the sidecars. That is
the `ABSENT 7` against `ABSENT 0` pair `audits/audit-phase-21-adopting-record.md` §6.1 records,
reproduced here at a different HEAD. Any fingerprint mismatch still FAILS; that is the whole gate,
and it is intact.

---

## 2. The ledger — ONE ROW PER MERGED PR (#396–#429, thirty-four rows)

**The row count is derived at close HEAD and is BROADER than the grep.**
`grep -c '^### Task 21\.' tasks/phase-21.md` reads **26** — ids 21.1 … 21.26 with **no hole** — so 25
contract headings besides this one. That is a FLOOR, not the ledger. Reconciled against
`gh pr list --state merged --base main` over the phase's window, the phase merged **34 PRs, #396
through #429**: the planning PR, the twenty-five `### Task` contracts, and **EIGHT dispatched units
carrying no `### Task` heading** and therefore no `**Measurement:**` field of their own. Each of
those eight is verified against the artifact it edited.

**Tally: 34 VERIFIED, 0 DEVIATION-RECORDED.** Four rows take a NAMED byte-verification substitute,
stated as a substitution with its reason (below); a substitution named as such is not a deviation, an
unnamed one is. The boilerplate tail (ruff / format / lint-imports / generated prompts / task docs /
mypy / pytest / `check.sh`) is verified **once for the whole tree** by §1 rather than re-quoted 34
times.

**Every id in the phase's range is accounted for, and the two owner decision points are the reason
this paragraph exists.** Task 21.6 (the win-condition ordering repair) and Task 21.20 (the
`testimony_shapes` lever) were dispatched as owner decision points the planning merge could have
struck. **Neither was struck**: 21.6 merged as #409 with a ratified scope widening and 21.20 as #416
with its Q4 ballot-render amendment as #417. The id sequence 21.1 … 21.26 is contiguous, so no hole
can read to a stranger as a merge that went missing. The same accounting runs in the other direction
for the mid-phase **addition**: **task 21.22a** has no `### Task` heading in the contract file at all
and is routed by `audits/audit-phase-21-preregistration.md` §11's first row; it merged as **#421**
(`75e2e782`).

### 2.1 The twenty-five contracts

| task (PR) | the fresh command at close HEAD | quoted output | verdict |
|---|---|---|---|
| 21.1 (#406) | `grep -cE "The engine certified\|flagged_contradictions\|the detector already found" agents/strategic/prompts/qwen3_6_27b/{accusation_round,vote_ballot}.j2` | **0 on both files**, where its Measurement records 4 on both at its own HEAD — the machinery dialect is no longer taught | VERIFIED |
| 21.2 (#408) | `uv run pytest tests/agents/test_vote_transcript_parity.py tests/meetings/test_vote_guard_rationale.py tests/eval/test_vj_instruments.py -q` | *"78 passed in 6.44s"* — the ballot's structured-testimony parity gate and its planted regression case | VERIFIED |
| 21.3 (#399) | `uv run pytest tests/orchestrator/test_replay.py tests/eval/test_replay_walk.py tests/eval/test_wave2_metrics.py -q` | *"163 passed in 3.82s"* — including the planted-mismatch case that proves the walker's disposition check bites. The ~2,160 recorded-but-never-applied actions now carry a disposition (§3.2) | VERIFIED |
| 21.4 (#403) | `uv run pytest tests/agents/test_memory_rendering.py tests/agents/test_memory.py tests/agents/test_features.py -q` | *"172 passed in 3.24s"* — the last-seen argmax over every sighting, the equal-tick rule and the two stale-sighting probes | VERIFIED |
| 21.5 (#404) | `uv run pytest tests/observation/test_service.py -q` | *"47 passed in 1.37s"* — one vent, one record: the flipped co-emission pin, the teammate-residue, non-witness and sabotage-alarm cases | VERIFIED |
| 21.6 (#409) | `uv run pytest tests/engine/test_tick.py tests/eval/test_replay_walk.py tests/api/test_replay_loader.py -q` | *"184 passed in 6.91s"* — the win check runs when the game is decided, meeting or no meeting; §1's `verify_samples.sh` is the 100/100 half of the same Measurement. **An owner decision point that was NOT struck** | VERIFIED |
| 21.7 (#400) | `uv run pytest tests/eval/test_watchability.py tests/eval/test_meeting_quality.py tests/eval/test_vote_correctness.py tests/eval/test_gate_spec_metrics.py -q` | *"185 passed in 11.29s"* — the flag census comes off the record rather than a re-derivation (B-6's four live consumers) | VERIFIED |
| 21.8 (#407) | `uv run pytest tests/training/test_surrogate_dataset.py tests/training/test_surrogate_runner.py tests/training/test_conviction_model.py -q` | *"98 passed, 6 deselected in 36.76s"* — rewritten targets, memory at speech time, the precision axis and the missing fingerprints; `--complete`'s `fit-corpus identity fingerprint` row is the same claim from the other side (§1) | VERIFIED |
| 21.9 (#402) | `uv run pytest tests/eval/test_accusation_calibration.py tests/eval/test_deduction_metrics.py -q` | *"151 passed in 4.46s"* — calibration without the firewall artifact, and a dialect gauge that overlaps the dialect | VERIFIED |
| 21.10 (#405) | `uv run pytest tests/scripts/test_record_ml_corpus.py tests/scripts/test_validity_gate_cli.py tests/scripts/test_verify_ml_evidence.py -q` | *"212 passed in 155.82s (0:02:35)"* — the dead-owner streak, the tested recording engine, the version pin's CLI and the loader guard sweep. This is the machinery both records then ran on | VERIFIED |
| 21.11 (#410) | `uv run pytest tests/scripts/test_check_doc_facts.py -q` + `uv run python scripts/check_doc_facts.py` (§1) | *"237 passed in 101.25s (0:01:41)"* and the front-door check exit 0; `grep -nI "baseline-6\|baseline 6" scripts/record_ml_corpus.sh \| wc -l` → **4**, its Measurement's four historical citations exactly | VERIFIED |
| 21.12 (#398) | `cd frontend && npm run test` | *"Test Files 9 passed (9) / Tests 440 passed (440)"* — including `src/lib/contradictions.test.ts`, whose walk over the committed served payloads is the gate 21.12 shipped | VERIFIED |
| 21.13 (#397) | `uv run pytest tests/training/test_scenarios.py -m campaign -q` | *"53 passed in 2.08s"* — the mover scenario pin tells the truth about hunting. This is F1's ninth failure, and it is the one this contract owned | VERIFIED |
| **21.14 (#411)** | **SUBSTITUTE: `git status --porcelain replays/`** — an operator smoke has no runnable Measurement at a later HEAD (its scratch directory is gone). The phase-20 precedent is `audits/audit-phase-20-close.md`:238 | **empty** — the smoke left the committed sets untouched, which is the invariant its Measurement's last clause names | VERIFIED (named substitute) |
| **21.15 (#412)** | **SUBSTITUTE: `bash scripts/verify_samples.sh` bare + `validity_gate.py` × 4** — the record's own Measurement re-records 300 games; the byte-level invariant it left behind is what a close can re-run. Precedent: `audits/audit-phase-20-close.md`:239 | 100/100 byte-clean in a **bare** environment; all four gates *"Validity gate PASSED (all checks green)"* over 50 / 150 / 50 / 50 games with `substrate stamped exact` (§1) | VERIFIED (named substitute) |
| 21.16 (#401) | `uv run pytest tests/training/test_rewards.py tests/training/test_bakeoff_harness.py tests/engine/test_rng.py -q` | *"122 passed in 12.12s"* — bars that discriminate, a comparator told what it measures, objectives that rank a win above a loss. Its Measurement's "exactly one expected failure" clause is now moot: §1's campaign tier is green | VERIFIED |
| 21.17 (#413) | `uv run pytest -m campaign -q` (§1) + `grep -c STALE scripts/verify_ml_evidence.py` | **"331 passed, 6111 deselected"**, exit 0, and **0** — the amnesty is GONE from the source, not merely unused. `--complete`'s `ML grounding` row reads `OK` with conviction and surrogate fingerprints both `cc54d3c02a98…` | VERIFIED |
| 21.18 (#414) | `uv run pytest tests/eval/test_reporter_justice.py tests/orchestrator/test_meeting_integration.py -q` | *"75 passed, 3 xfailed in 1.90s"* — the reporter's exculpation reaches speech (lever `reporter_reasoning`, still default-OFF after the FINDING) | VERIFIED |
| 21.19 (#415) | `uv run pytest tests/orchestrator/test_replay_meetings.py tests/experiments/test_probe_backends.py -q` | *"31 passed in 0.78s"* — the registration blast radius its Measurement widened to, with `_FLAGS_ON` carrying the key (lever `corroboration_discipline`) | VERIFIED |
| 21.20 (#416) | `uv run pytest tests/meetings -q` | *"1260 passed in 22.99s"* — what you saw is what you can say (lever `testimony_shapes`), including the prompt byte golden over the committed meetings. **The second owner decision point, also NOT struck** | VERIFIED |
| 21.21 (#418) | `uv run pytest tests/scripts/test_counterfactual_phase21.py -q` | *"112 passed in 44.94s"* — the offline OFF/ON table still reproduces, including the four corroboration cells the script is the first pin for | VERIFIED |
| 21.22 (#419) | `uv run pytest -q -k "deduction_metrics or funnel or evidence_honesty or solvability or reporter_justice"` | *"339 passed, 6103 deselected in 45.70s"* — every pin the ratified memo quotes resolves at close HEAD. Merged by the orchestrator **on the owner's explicit per-PR delegation of 2026-09-02**, which the record notes did not generalize | VERIFIED |
| **21.23 (#425)** | **SUBSTITUTE: `git status --porcelain replays/`** — the smoke's staged bytes were removed entirely and *"the staging root is empty in the final commit and owes no artifacts row"* (`tasks/phase-21.md`:7501) | **empty**; the report itself is `audits/audit-phase-21-smoke-wave2.md`, GO with one watch item FIRED (§16) and a dated post-#424 re-smoke addendum on `44f0a28c` (§18) | VERIFIED (named substitute) |
| **21.24 (#428)** | **SUBSTITUTE: `bash scripts/fetch_evidence.sh` + `verify_ml_evidence.py --complete`** — the record's bytes are NOT in the tree; they are on the parentless commit `29af85d5…`, so the only close-time verification is the reconstruction of that family | *"OK: 3269/3269 files match …"* and `wave2-finding/ [(c)] … EVIDENCE-BRANCH-RESTORED (315/315 present)` with all four `wave2-finding reconstruction` rows OK under the manifest's **declared slate** — the recording is READ, not merely hashed (§1) | VERIFIED (named substitute) |
| 21.25 (#429) | `grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator \| wc -l` + `uv run pytest tests/meetings/test_lever_registry.py tests/api/test_sets.py -q` | **5** = 1 + `len(_TOGGLEABLE_LEVER_RESOLVERS)`, the branch-aware expectation its Measurement derives rather than types; *"42 passed in 1.17s"* including both planted counter-cases and the seed-13 card's spoken-turn check | VERIFIED |

### 2.2 The nine PRs the grep does not reach

The planning PR plus the eight amendment/addition units. None has a `**Measurement:**` field; each is
verified against the artifact it edited, and the five that touched the ratified memo are verified
against the `audits/audit-phase-21-preregistration.md` §11 row that ratifies them.

| PR (squash) | what it was | verified against | verdict |
|---|---|---|---|
| **#396** (`772742c2`) | the planning PR — the charter and 26 contracts | `grep -c '^### Task 21\.' tasks/phase-21.md` → **26**, ids 21.1 … 21.26, no hole; `audits/audit-phase-21-planning.md` linked **once** from `audits/README.md` (the `check_audits_index` gate, green in §1) | VERIFIED |
| **#417** (`64de009e`) | the 21.20 Q4 ballot-render amendment | `grep -n 'saw_kill' agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2` → `:145`, inside the `testimony_shapes` guard: the ballot renders the shape the turn prompt offers | VERIFIED |
| **#420** (`5ab03fd7`) | the Wave-2 render amendment (pre-21.24) | the diff touches the three lever blocks and their tests only — `accusation_round.j2`, `crewmate_report.j2`, `vote_ballot.j2`, `loader.py`, `meetings/corroboration.py` and five test files, +1,157/−173 — and it published its cell moves as `audits/audit-phase-21-counterfactual.md` Erratum **E.1** rather than editing a ratified memo | VERIFIED |
| **#421** (`75e2e782`) | **task 21.22a** — the T5/T7 tripwire readers (a mid-phase ADDITION with no `### Task` heading) | §11 row 1; `grep -c "P-1k\|P-1ka" scripts/counterfactual_phase21.py` → **5** — the cells exist in both of the script's modes, which is the condition §8.1's T5 disposition names | VERIFIED |
| **#422** (`96b61318`) | instrument amendment — the counterfactual reads a lever-ON recording | §11 row 2; `grep -c '\-\-recording\|recorded.slate' scripts/counterfactual_phase21.py` → **18** — the `--recording <dir> --recorded-slate on` mode §8.1's reader clause needed to be executable at 21.23 | VERIFIED |
| **#423** (`88bc8be7`) | instrument amendment — T2's and T6's readers re-read at BLOCK level | §11 row 3; the `R-13` / `R-14` / `C-9` cells present in the reader (6 hits). This is also the phase's **falsified-by-derivation precedent**: the "owner routing" it was drafted against was disproved by re-derivation and no cell moved | VERIFIED |
| **#424** (`ffaf9991`) | grounding semantics — a first-hand account is a placement (**OWNER-GATED**, owner-merged) | §11 row 4; `grep -c 'def sighting_placement' meetings/transcript.py` → **1**, the repo's own definition the amended clause reads. It reopened the smoke window by §16's own rule, which is what forced #426 | VERIFIED |
| **#426** (`e0c2adde`) | the 21.23 post-#424 re-smoke (**OWNER-GATED**, owner-merged) | `audits/audit-phase-21-smoke-wave2.md` **§18**, present and dated: two seeds on `44f0a28c`, all ten validity checks, all seven tripwires PASS, **zero** `failed_call` rows of any kind, §§0–17 un-rewritten | VERIFIED |
| **#427** (`608ae1f6`) | the memo amendment — six §11 rows plus E.3 (**OWNER-GATED**, owner-merged) | §11 rows 5–11: **seven** rows ratified by this PR, counted by its own ratification-vehicle cell. With #421, #422, #423 and #424 at one row each, §11 carries **ELEVEN** dated rows in total, under its convention *"amendments land BEFORE the record or not at all"* | VERIFIED |

**On the absence of deviations.** The prior close recorded three, all of the same two shapes: a
contract whose Measurement named a red tier, and two whose Measurement named a word budget already
over at their own merge. Neither shape recurs here — the campaign tier is green (§1) and the four
front-door budgets are now a gate that passes (`check_front_door_budgets`, §1). Deviations recorded
at their own merges are not re-litigated here; they live in `tasks/phase-21.md` beside their
contracts as orchestrator-ratified merge-reality records (21.2, 21.4, 21.6, 21.8, 21.9, 21.10, 21.11,
21.17, 21.18, 21.19, 21.20, 21.21, 21.22, 21.23, 21.24, 21.25). This close re-read each and found
none that changes a verdict above.

---

## 3. The before/after story (generated numbers only)

Every pre-record figure below is the instrument pin the pre-registration cites or the cell
`audits/audit-phase-21-rerecord.md` publishes as its before column; every post-record figure is read
from `audits/audit-phase-21-adopting-record.md`. **Nothing in this section is recomputed by the
close.**

### 3.1 The four pre-registered bars, read back

The rule: `audits/audit-phase-21-preregistration.md` §6 — **ADOPTED iff all four of bars 1, 2, 3 and 4
are met, FINDING otherwise.** It is conjunctive, it names its subset exactly, and it has no "and/or",
no waiver and no substitute.

| bar | cell | target | baseline 8 | this record | verdict |
|---|---|---|---|---|---|
| **1** | `EjecteeProofCrossTab.non_direct_accuracy` pooled | ≥ 0.60, no powered set < 0.50 | 50/96 = 0.5208 | **46/66 = 0.6970** | **MET** |
| **2** | `MeetingFlagCrossTab` innocent ejections pooled | < 35 | 46 | **20** | **MET** |
| **3** | `reporter_innocent_ejections` pooled | ≤ 12 | 34 | **11** | **MET** |
| **4** | `reporter_share_of_innocent_ejections` pooled | < 0.40 | 34/46 = 0.7391 | **11/20 = 0.5500** | **MISSED** |

**VERDICT: FINDING.** Three of four is not adoption. The three Wave-2 levers stay live toggles, the
ladder tip stands at **baseline 8**, and the four canonical replay sets keep their baseline-8 bytes.

**Bar 4 fired exactly where it was aimed, and that is the reading.** The memo, written a phase before
these bytes existed, named the configuration it was built to catch — *"`R = 10`, `I = 20` passes bars
2 and 3 and fails bar 4 at 50%. That is the outcome this phase would most want to mistake for
success, and it is the only thing bar 4 is for"*
(`audits/audit-phase-21-preregistration.md`:365-372). The record read **`R = 11`, `I = 20`**: one
event from that configuration, on the wrong side of it.

**The composition, from the record's own cells** — the reporter channel closed FASTER than every
other route, and the share stayed high because the reporter dominated the starting composition:

| wrongful ejections | baseline 8 | this record | move |
|---|---|---|---|
| reporter | 34 | 11 | **−67.6%** |
| non-reporter | 12 | 9 | −25.0% |
| **total (bar 2)** | **46** | **20** | −56.5% |

Per slot the same ordering holds: the reporter's own ejection risk fell 5.48% → **1.76%** while the
innocent non-reporter's fell 0.65% → **0.43%**, a relative risk of **4.12x** against baseline 8's
8.50x.

**The flip cost, quoted whole, because its three rows hold DIFFERENT constants and no column is "the"
number** (`audits/audit-phase-21-adopting-record.md` §4):

| operation | what it would take |
|---|---|
| reclassify reporter → non-reporter (bar 2's total held at 20) | **4** reclassifications: `R = 7`, 7/20 = 0.3500 passes; `R = 8` reads exactly 0.40 and does not |
| vanish reporter ejections outright (non-reporter held at 9) | **6** vanished: `R = 5`, 5/14 = 0.3571 passes |
| hold `R = 11` and grow the wrongful total | **+8** more wrongful ejections, to 28 — a worse record on bar 2 |

Bar 4's Wilson interval from the memo's only interval producer is **[0.3421, 0.7418]**, and it
CONTAINS the 0.40 target; the record reports that as context and not as a test, because every bar in
the memo is a point-estimate bar. **No set passes bar 4 alone**, so the miss is not one leg's.

#### The structural null, in its own paragraph, as the hand-off to the next pre-registration

This is a separate read on a **different denominator**, and the two are not interchangeable. Bar 4's
registered cell is **11/20 = 0.5500**, pooled over all twenty wrongful ejections. The per-row
structural null is computed over the **nineteen** of those twenty that occurred at a body-report
meeting, because only there does a "body reporter" exist to be the null's target; the twentieth was
at an emergency meeting, and all eleven reporter ejections are inside the nineteen
(`audits/audit-phase-21-adopting-record.md`:952-956).

| | baseline 8 | this record |
|---|---|---|
| wrongful ejections at a body-report meeting | 46 | 19 |
| pooled per-row uniform null | **0.3152** | **0.2553** |
| observed reporter share on those rows | 0.7391 | **0.5789** |
| three-living rows | 12 of 46 (null 0.50) | **1** of 19 |
| exact Poisson-binomial P(X ≥ observed) | 1.27 × 10⁻⁹ | **0.0024** |

**The null FELL rather than rising toward 0.50, so the hardening's fear did not materialise and 0.40
was reachable on these bytes.** This reading is **OFFLINE and observed-never-gated**: the record
states it *"did not enter the verdict"*, no bar, tripwire or §9.2 criterion reads it, and the rows
are only approximately independent (19 rows from 18 games). It is here as the hand-off to the next
pre-registration, and nowhere else in this document.

#### The SHARE-vs-COUNT observation, verbatim from the record's §7

> a SHARE bar and a COUNT bar registered on the same cell can pull against each other, and here they
> did — at the record's 9 non-reporter wrongful ejections bar 4 needed `R ≤ 7` (holding the total)
> while bar 3 asked for `R ≤ 12` and got 11. That is a fact about how the two were parameterised
> together, not about these bytes, and it is never a retroactive edit to this memo.

### 3.2 The record-free rows — measurements that needed no record

This phase has an unusual number of these, because most of it was repair.

| row | before | after | source |
|---|---|---|---|
| the opt-in campaign tier | **9 failed, 308 passed, 5327 deselected in 185.78s**, exit 1 | **331 passed, 6111 deselected in 154.67s**, exit 0 | §1; `audits/audit-phase-20-close.md` F1 |
| the declared ML-grounding gap | **STALE 11** of 55 checks | **no STALE status at all** — `grep -c STALE scripts/verify_ml_evidence.py` = 0; 63 checks, OK 58, FAIL 0, ABSENT 0 | §1; 21.17 (#413) |
| recorded actions never applied | **~2,160** recorded as submitted with no disposition (A-14 + B-1) | every recorded action carries a disposition, with a planted-mismatch case proving the walker's check bites | §2 (21.3) |
| the double-minted vent record | one vent minting two records, one of them audible through the teammate firewall (A-31) | one vent, one record — four planted cases | §2 (21.5) |
| the belief line against the agent's own eyes | **19%** of rendered belief rows contradicted a sighting the same agent held (B-8) | last-seen reads every sighting, argmax and equal-tick rules pinned | §2 (21.4) |
| the machinery dialect taught in the templates | **4** oracle-voice lines across the two templates; leak 78 utterances in 44 of 300 games (A-6) | **0** on both files; the oracle-register leak class reads **zero on all four sets** on the re-recorded bytes | §2 (21.1); `audits/audit-phase-21-rerecord.md` §5.1.2c |
| substrate registry | 22 keys, 21 True, 1 False | **25 keys, 21 True, 4 False** — twenty-one retired always-on levers and **four** live toggles (`impostor_roll_call` + the three Wave-2 levers) | §3.3 |
| the evidence restore | 2953/2953 files, ONE family | **3269/3269**, TWO families (2,953 coevo + finalist-raw, 316 Wave-2) | §1 |
| non-direct conviction accuracy (the re-record's own before column) | baseline 7: 61/103 = 0.5922 | **baseline 8: 50/96 = 0.5208** — the cell FELL, and the maintenance record published it unchanged | `audits/audit-phase-21-rerecord.md` §5.1 |
| innocent ejections (the same) | baseline 7: 42 | **baseline 8: 46** — rose | `audits/audit-phase-21-rerecord.md` §5.1 |

**The maintenance re-record's own hand-off is a row in its own right, and it is unflattering.** The
combined re-record decided nothing — no bars, no verdict — but it published *"one improvement and
four regressions"*: accuracy fell 0.5922 → 0.5208, innocent ejections rose 42 → 46, the sole-flag
wrongful-conviction class re-opened 0 → 4, the STRONG statement-pair class re-opened 0 → 1, and
against those the oracle-register leak class went to zero. That is the before column the Wave-2
pre-registration was then written against, which is why it could be written honestly.

**Three rows the record makes mandatory, published beside the bars rather than under them:**

**(a) Decisiveness moved ADVERSELY** (`…adopting-record.md` §3.4). Memo §5 registered it beside bar 2
for one reason the memo states outright: *a bar-2 pass that came from deciding LESS reads as such.*

| | baseline 8 | this record |
|---|---|---|
| body-report ejections / body-report meetings | 377/620 = **60.8%** | 352/626 = **56.23%** |
| ejection accuracy | 383/429 = **89.3%** | 391/411 = **95.1%** |

The record decided less on every leg and pooled. It bounds the reading rather than changing the
verdict: the wrongful total fell 56.5% while the ejection rate fell 7.5% relative, so the great
majority of bar 2's movement is not accounted for by deciding less — and accuracy rose.

**(b) THREE of four legs FAIL baseline 8's evidence-supply floors** (§3.6). **A gauge whose baseline
numerator was 0 or 1 is ADVISORY under the standing rare-event rule and can never fail the referee**
— that treatment is stated here, in the column header, rather than applied case by case:

| leg | referee | binding gauges below their floor |
|---|---|---|
| 1 `samples/9p2i` | **FAIL** | `flags_per_meeting` 0.857 < 0.974; `testimony_backed_conversion` 0.605 < 0.719; `transcript_flags_per_meeting` 0.268 < 0.377; `persisted_vent_flags_per_meeting` 0.589 < 0.596 |
| 2 `ml_corpus/9p2i` | **FAIL** | `transcript_flags_per_meeting` 0.303 < 0.377 |
| 3 `samples/4p1i` | **FAIL** | `testimony_backed_conversion` 0.559 < 0.577 (`witnessed_event_rate` below its floor is ADVISORY) |
| 4 `ml_corpus/4p1i` | **PASS** | none (`witnessed_event_rate` 0.0 below its floor is ADVISORY) |

Leg 4's PASS beside a below-floor gauge is the advisory rule working, not an inconsistency. The
reading it supports, stated plainly: **the Wave-2 slate convicts more accurately on FEWER flags.** On
ADOPTED a successor floor block would have been pinned from these bytes; on FINDING
`_BASELINE_SUPPLY_FLOORS` and `_DEFAULT_BASELINE_ID` are untouched (§3.3).

**(c) The three registered §5 secondaries** (§3.7), observed and never gated:

| secondary | baseline 8 | this record |
|---|---|---|
| solvability containment (`killer_in_set`) | 557/620 = 0.8984 | **563/626 = 0.8994** — flat |
| zero-flag convictions | 86/429, **37 CREW** | **63/411, 17 CREW** — seventeen of the record's twenty wrongful ejections are flagless |
| co-discovery seats | 118/620 meetings, **49.0%** impostor | **127/626 meetings, 48.4%** impostor — **A-38's rejection HOLDS**: the seat is still a coin flip, so framing it exculpatory would have sheltered an impostor half the time |
| per-slot reporter risk ratio | 8.50x | **4.12x** |
| spoken kills | **0** pooled | **30** accounts, 30/30 joining the engine's own kill event on killer and room, **16 converted** — and one meeting on `9p2i` seed 19 ejected the truthful eyewitness **4 ballots to 1** |
| win split (memo §5's ±15-point band) | 30.0 / 24.0 / 36.0 / 26.0% impostor | **24.0 / 18.7 / 36.0 / 28.0%** — every leg inside the band |

### 3.3 Both records' rulings, verified present in the tree

**The two are never flattened into one.** The combined re-record (21.15, #412) is
**maintenance-of-record**: it re-recorded four sets on repaired bytes at the bumped prompt set,
published every instrument cell before and after, and *declared no verdict* — its own audit says
*"Nothing"* under "what this record decides", and its surprising moves were STOP-and-report items to
the owner while it ran. The adopting record's verdict is the adopting record's and its merge's, and
it is carried here exactly as recorded.

**What the FINDING verdict executed, checked item by item at close HEAD by command:**

| the FINDING branch says | how it was checked | result |
|---|---|---|
| no lever graduates | `orchestrator/replay.py` `_RETIRED_ALWAYS_ON_LEVERS` / `_TOGGLEABLE_LEVER_RESOLVERS` | **21 retired keys, 4 live toggles** — `impostor_roll_call`, `reporter_reasoning`, `corroboration_discipline`, `testimony_shapes` |
| the sweep rule is NOT APPLIED, because nothing graduated | `grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator \| wc -l` | **5** = 1 (the 18.10 loader arm) + 4 live registry entries. AGENTS.md:62-89's graduation sweep is verified as a **RECORDED NO-OP**, not performed |
| the stamp is 25 keys, the toggles OFF in a bare shell | `substrate_flag_snapshot({})` | **25 keys, 21 True**, the four False keys being exactly the four toggles |
| the ladder tip does not move | `eval/watchability.py:1050` | `_DEFAULT_BASELINE_ID` = **`"baseline-8"`**; `_BASELINE_SUPPLY_FLOORS` carries blocks `baseline-2 … baseline-8`, no successor minted |
| the ML grounding does not move | `training/bakeoff/harness.py:186` | `BAKEOFF_BASELINE_ID` = **`"baseline-8"`**, where the 21.17 re-ground set it |
| the canonical bytes do not move | `bash scripts/verify_samples.sh` bare + the four validity gates (§1) | 100/100 and four PASSes over the baseline-8 bytes |
| `.env.example` documents all four as live toggles | `check_lever_registry` inside `check_doc_facts` (§1) | green, naming *"the 25-lever substrate registry"*; the four `# AILIBI_*=0` lines are at :143, :166, :189, :223 |

**`_LADDER_TIP_AUDIT` points at a RE-RECORD, and that is CORRECT.** For the first time in this
project `scripts/check_doc_facts.py:215` names `audits/audit-phase-21-rerecord.md` — the
**maintenance** record — rather than a close or adopting audit, because no lever graduated and the
tip did not move. A later reader will be tempted to "repair" it. **It is not a defect and the close
does not touch it** (`scripts/` is out of scope, and the constant is right on a FINDING). The
deciding record is a different document, anchored separately at :635 (`_FINDING_RECORD_AUDIT`), which
is what 21.25 landed so the phase's four headline figures would not be the only ungated ones on the
front door.

**The owner made NO override at the gate.** The merge of #428 on 2026-09-04 was silent on it, so
**FINDING stands as read**. The `audits/audit-phase-20-baseline-7.md` §6.1-shape override path stays
the owner's to take at any later point — recorded then as an override of a FINDING verdict, and
**never as a bar that passed**. Nothing in this close takes it, and nothing in this close re-rules a
verdict or re-prices a cell.

**(G8), the recording's carry mechanism, was RULED AT THE GATE by that same merge — a transcription
row, not a reopened question.** The class-(c) parentless evidence commit
`29af85d5457caeba4f8ba8ba77610c6a0ab2213a` is the ratified mechanism.
`audits/audit-phase-21-adopting-record.md` §6.1's PROVISIONAL heading and its in-tree-alternative
paragraph are **DISCHARGED by the merge** and stand unrewritten as the record's own text
(`tasks/phase-21.md`:7297, ticked, and :7509). An in-tree class-(a)+(b) re-landing would be a
follow-up of the owner's own asking, not a close option. The two surfaces that called it provisional
are **F4** — `docs/artifacts.md` corrected here by a dated line, the record's own README carried.

#### The inherited constraint, re-swept across everything this phase wrote

**Baseline 7 is canon by explicit owner override of a FINDING verdict.** The phase-20 pre-registered
rule returned FINDING with bar 1 at 61/103 = 0.5922 against ≥ 0.60 and bar 2 at 42 innocent ejections
against < 35, **both MISSED**, and nothing anywhere re-prices them; separately and by explicit
prerogative the owner adopted the substrate over that verdict on 2026-08-26
(`audits/audit-phase-20-baseline-7.md` §6, §6.1). That document's *"what no surface may say"*
paragraph binds this phase's tree exactly as it bound the last one.

The sweep (§8 lists it) walked every tracked file for the full forbidden set — `bars? (were )?(passed|met)`,
`passed the bars?`, `met the bars?`, `met its bars?`, `adopted on the (arithmetic|numbers)`,
`verdict was ADOPTED`, `ADOPTED under the rule` — and over the commit half for the phase's whole
history, `772742c2^..fa739ccb`, subjects and bodies together. **Every hit is either the constraint
being stated, a generated prompt repeating it, or a negation. No surface and no commit message in
this phase states or implies that a pre-registered bar passed.**

And the phase's own new claim carries the same shape, gated this time rather than swept: README:152
reads *"Innocent ejections fell from 46 to 20, and 11 of those 20 were the meeting's own reporter,
against 34 of 46 — but 11 of 20 = 0.5500 against a registered share of 0.40, so the rule returns **a
finding**, not an adoption. No override was made"* — held by `check_verdict_passage`,
`check_finding_figures` and `check_owner_action` (§1). **This close neither re-ruled a verdict nor
re-priced a cell, and asserts so here in its own words.**

### 3.4 The two registers' findings → outcomes

The 2026-08-26 audit published **48 canonical findings on track A** (13 CONFIRMED / 35 ADJUSTED / 0
REFUTED) and **56 on track B** (18 / 37 / 1 REFUTED) — `audits/review-2026-08-26/README.md` §1.
**No gate holds this map** (F3), so it is published in a form a reader can check, derived by the §8
command rather than assembled by hand: the acted-on set is every `A-`/`B-` id named inside a
`### Task 21.N` section of `tasks/phase-21.md`, excluding ids only this close's own section cites.

| outcome | count | the findings |
|---|---|---|
| **fixed** (repair merged and re-verified at close HEAD, **no open half**) | 44 | `A-1`, `A-3`, `A-6`, `A-8`, `A-9`, `A-14`, `A-15`, `A-17`, `A-26`, `A-31`, `A-34`, `A-48`; `B-1`, `B-2`, `B-6`, `B-8`, `B-9`, `B-10`, `B-11`, `B-12`, `B-13`, `B-14`, `B-15`, `B-16`, `B-17`, `B-18`, `B-19`, `B-20`, `B-21`, `B-22`, `B-23`, `B-28`, `B-35`, `B-40`, `B-43`, `B-46`, `B-47`, `B-48`, `B-50`, `B-51`, `B-52`, `B-53`, `B-55`, `B-56` |
| **partly fixed, remainder CARRIED** (a split id, given its own row rather than credited whole) | 1 | `B-26` — 21.16 took its objective half; its `world.py` half is unexecuted and is carried by name in §4 |
| **lever-ON, measured, NOT adopted** (shipped default-OFF, recorded, and left as toggles by the FINDING) | 15 | `A-4`, `A-5`, `A-24`, `A-37`, `A-38` (`reporter_reasoning`); `A-10`, `A-11`, `A-12`, `A-19`, `A-44`, `B-3`, `B-4` (`corroboration_discipline`); `A-16`, `A-22`, `B-7` (`testimony_shapes`) |
| **recorded-as-finding** (answered by measurement, not by change) | 4 | `A-20` — the meeting's two regimes, republished in §3.2's flagged/unflagged split rather than "fixed"; `A-25` — recorded impostor reports **0 of 626** on this record too, the premise bars 3 and 4 rest on; `A-42` — the clean negative re-verified as 21.1's control; `A-47` — an observation the smoke reports |
| **triaged backlog** (untouched, and actionable) | 39 | the live remainder of the 104: **20 on track A and 19 on track B**, none of them touched by any contract in this phase |
| **refuted by the review's own verifier — no work to carry** | 1 | `B-34`, the track-B register's single REFUTED id, severity *"n/a (not a defect)"* — a specified-and-ratified behaviour filed as one (`audits/review-2026-08-26/README.md` §1). It is untouched, but it is not backlog, and counting it as such would overstate the next phase's inputs by one |

**The `lever-ON` row is the one this close will not let read as a success.** All three levers were
ELIGIBLE by the memo's own per-lever RENDER test — every render prediction held on all four legs and
no tripwire fired against any of them (`…adopting-record.md` §4.5) — **and eligibility graduates
nothing.** Fifteen findings were shipped, recorded, measured against pre-registered bars, and left in
exactly the state they were in before, because one bar of four missed. That is the whole cost of the
apparatus, and it is what the apparatus is for.

**`B-26` is the one split id and it gets its own row rather than a footnote**, because a "fixed" row
that quietly contains a half-open finding is the arithmetic this map exists to make checkable: 21.16
took its objective half, its `world.py` half is unexecuted, and it is carried by name in §4's routed
opens. Nothing else in the fixed column has an open half — the derivation snippet in §8 prints every
id with the contracts that named it, so a second split would be visible the same way.

**The rows partition the 104 exactly:** 44 + 1 + 15 + 4 + 39 + 1 = 104. `A-20` and `A-25` are the two
ids no `### Task` section cites — the close's own section cites them — so they enter through the
recorded-as-finding row and not through the derived acted-on set. **The actionable backlog is 39, not
40**, because the untouched remainder contains the review's one REFUTED id; a close that hands
forward a refuted finding as work is doing the thing the prior close's map went out of its way not to
do (`audits/audit-phase-20-close.md` §3.4 lists its five retracted claims in their own row for the
same reason).

### 3.5 The hardening audit's routings, reconciled by measurement

`audits/audit-phase-21-hardening.md` §4.2 routes its own entries to this ledger. **The ledger inherits
its counts the way the audit's own registers count them, and makes no discrepancy claim:** the
heading reads *"36 entries, nine themes"*; the section carries **TEN** bullets, its **36 `H-` ids**
(the round-1 register's routing tally, corroborated by §6's *"close-ledger 36"*), and a tenth bullet
carrying **SIX round-2 ids** (`R2-oracle-1..3`, `R2-responses-1..3`) drawn from the separate 32-finding
second round — **42 entries inherited in total**. **Every one is BASELINE-8 vintage**, measured before
the Wave-2 record, and none was re-read on the record's bytes; they are carried as a sized backlog and
not re-verified here. §4.3's **nineteen** informational entries are sized the same way. No erratum is
offered on the heading: the two counts reconcile.

**§4.1's five named routings, reconciled BY MEASUREMENT rather than assumed** — a routing that named a
contract and was never picked up is a worse silence than one routed here, so each gets a row:

| finding | routed to | disposition at close HEAD |
|---|---|---|
| **H-38** (the `saw_kill` path has no committed exposure) | 21.23 | **CITED** — `tasks/phase-21.md`:6781 carries it in 21.23's Section refs, so its disposition is the smoke report's: §18's re-smoke read all seven tripwires including T5 on the merged head |
| **H-36** (`docs/artifacts.md`:96 called the sample sets "the baseline-6 adopting record") | 21.25 | **CLOSED** — the one-word fix rode 21.24's standing index amendment (`tasks/phase-21.md`:7286); `grep -c 'baseline-6' docs/artifacts.md` reads **0** |
| **H-37** (the reading guide sends a reader to 9p2i seed 46 for "a pair of conflicting accounts") | 21.25 | **OPEN** — `docs/reading-guide.md`:69-70 still does. **CARRIED** |
| **H-32** (the stale rubric contradicts the served bytes on 16 of 50 games) | 21.25 | **NO DISPOSITION ANYWHERE** — `grep -n 'H-3[23]' tasks/phase-21.md` finds only this contract's own text. **CARRIED** |
| **H-33** (the ballot card's only explanation for a redirected vote is the raw token `under_gate_redirect`) | 21.25 | as above. **CARRIED** |

---

## 4. What this phase routed, carried by name into the next phase's inputs

Contract prose is where routed items go to be forgotten. Each row below names what it is, what
decided it, and a disposition. **DISCHARGED** means a command or a merge closed it; **CARRIED** means
it is open and its size is stated; **OWNER-DECIDED** means a ruling closed it.

| item | where it was routed from | disposition |
|---|---|---|
| **the second ML re-fit** | `…adopting-record.md` §7 — *"becomes due at that record and not before"* | **DISCHARGED-BY-RECORD, carried not scheduled.** The trigger is falsifiable: an adoption that LANDS BYTES IN TREE, by a later record OR by a §6.1-shape owner override of this FINDING, at which point §10.2's dated digest-pair re-declaration and the re-fit become due AT THAT RECORD. The corpus is unmoved at close HEAD (`grep -c STALE` = 0), so this needs no owner ruling. Size: **zero now; one corpus re-fit at the triggering record** |
| **21.17's Q1** — the λ-grid and campaign re-search under 21.16's repaired objective | 21.17, *"an OWNER decision at campaign scale, held for the close ledger"* | **CARRIED, and put to the owner in §5.1 and in this PR's `## Questions`.** No ruling has closed it, so it is not OWNER-DECIDED; it is a live open, costed at campaign scale, sitting BESIDE the re-fit row rather than folded into it |
| **the `heard_vent_use` encoder slot** | 21.25 | **CARRIED** to the next encoder revision. Retained as a structurally-zero scalar because `TacticalFeatureEncoderV3` inherits the v2 layout; removing it re-shapes the v3 vector under an unchanged `ENCODER_VERSION_V3`, so it belongs to the revision that owns both version stamps and every downstream consumer |
| **the dead `vent_use_heard` path** | 21.25, as ONE named open to a wire-owning contract | **CARRIED**, with its full census: `observation/packet.py:157` and `api/schemas.py:201` `Literal` members, `agents/perception.py:85`, `agents/memory/beliefs.py:533`/`:1107`, `agents/tactical/features.py:382`, `frontend/src/types/api.ts:140`, `EventTicker.tsx:43`, six test files. A partial deletion is refused on the coupling gate. **`grep -rl vent_use_heard replays` = 0 is NOT evidence of deadness** — audible kinds never enter replay bytes, and the live `sabotage_alarm` reads 0 too |
| **`observation.packet.AudibleEvent.kind`'s `Literal` member and the served `AudibleEventView`** | 21.25 | **CARRIED** — a DTO narrowing with a `viewModelVersion` question attached |
| **B-26's `world.py` half** | 21.16 | **CARRIED** — the objective half merged; this half is unexecuted |
| **G7(b)** the breadcrumb third gap | `tasks/phase-21.md`:1316-1318 | **CARRIED** — the breadcrumb path reads `saw_player` rows only and never consults `saw_player_move`; 12 contradictions on BOTH arms at seed 4104, unrepaired in baseline 8 |
| **G7(c)** the confidence-rubric deferral | `tasks/phase-21.md`:431 | **CARRIED** — `agents/strategic/prompts/qwen3_6_27b/accusation_round_roll_call.j2:210` still carries the un-swept phrase |
| **G7(d)** the staging-rule incident tally | `tasks/phase-21.md`:5979-5981 | **DISCHARGED as a recorded rule**, tallied here: the fourth masked-verdict incident; the staging rule is now *"tasks file + the entire `agent_prompts/` dir"* |
| **21.17's Q4** (the conviction corpus fence, `training/bakeoff/harness.py:759`) and **D7** (the `rederived_flags` rename, `training/conviction/dataset.py:289`) | 21.17 → 21.25 → here | **CARRIED** — both under the frozen `training/`. Q4's wiring was attempted, six fixtures measured red, and reverted; D7 was declined on scope |
| **the husk `free_text` fix** | routed to this ledger by `…adopting-record.md` §7 | **DISCHARGED — EXECUTED by 21.25** (#429): `meetings/manager.py:218-222`'s `DEFAULT_TURN_FREE_TEXT` is now a read-only mapping keyed on `DefaultTrigger`. Record impact nil |
| **`DEFAULT_VOTE_RATIONALE`** (`meetings/manager.py:226`) | 21.25, as the same defect on the same trigger split | **FALSIFIED BY DERIVATION — an erratum, not a repair.** See below |
| **the checker prose heuristics — now THREE** | 21.25 (two, after a fifth Codex round), plus one this close met while drafting | **CARRIED** as checker-hardening residue, each with a required perturbation case: (i) negation binding in `check_owner_action` (`scripts/check_doc_facts.py:4348-4360` searches `_NEGATION` (:777-779) over the sentence HEAD, so a negation in an unrelated earlier clause licenses a positive adoption assertion later in the same sentence); (ii) the word `"reporter"` alone scoping a rate claim to bar 4 (`_FINDING_BAR_SUBJECTS[_SHARE_BAR]`, `:729-732`); (iii) **new, met while drafting this close's own index entry** — `check_owner_action`'s unit is a `prose_blocks` block, which in a tight bullet list is the whole section, and its verb pattern matches inside a link's own FILENAME, so `audit-phase-21-adopting-record.md` in a neighbouring bullet reads as an adoption assertion (§6). Not fixed here: `scripts/` is out of scope |
| **the un-bumped ballot stamp (E.3)** | memo §11's tenth row, PR #427 | **DISCHARGED — ACCEPTED with the erratum and no bump.** A version bump would have been an edit inside a §9-frozen directory and would have reopened the smoke window a third time for a change that moves no cell, no bar and no OFF byte; the record quotes each leg's `git_sha` beside the stamp |
| **the featured-strip cards [1] and [3]** | `…adopting-record.md` §6.3, deferred *"to whichever record adopts"* | **CARRIED** — no record adopted. Their copy is misattributed rather than false (H-34/H-39), and the served surface is named: `frontend/src/components/ReplayPicker.tsx`:118 `FEATURED_GAMES`. **This is the only conditional-on-adoption open the phase leaves that a visitor can see today** |
| **`README.md:29`'s Status bullet** | 21.25 | **DISCHARGED here** — the scope admission in §6; corrected to the final closed state, eleven words for eight, so the edit is word-NEGATIVE |
| **`docs/lessons.md`'s "Writing the bar down before the measurement" (:88-99)** | this close | **CARRIED, with its price stated.** The section narrates only the phase-20 finding-then-override and is silent on this phase's FINDING — the project's second pre-registered miss and **the first not overridden**, i.e. the strongest instance of that essay's own thesis. The page is Files-NOT-in-scope here and `wc -w docs/lessons.md` = **1,499** against the 800–1,500 band, so taking it is a **trim-plus-add, not an add**. It sits in `_PUBLISHED_DOCUMENTS` and NOT in `_CLAIM_DOCUMENTS` — a second live instance of F1's ungated-figures class |

**Four items were routed BY NAME to Task 21.24 that a recording contract could not execute, and its
merge-reality record never mentions them.** Each is quoted with the line that routed it; the reason is
the same for all four — *a recording contract could not take it* — and all four are unexecuted
anywhere at close HEAD. All four are also named in the ratified memo's own DoD (:6551) as *"21.24's
own re-anchor business"*.

| routed item | the line that routed it | disposition |
|---|---|---|
| 21.19 Decision 12's version/environment REFUSAL, awaiting generalisation | `tasks/phase-21.md`:5790 | **CARRIED** |
| the `roll_call` variant gap — 21.18's block absent from the frozen v1 variant | `tasks/phase-21.md`:5939, PINNED-OPEN | **CARRIED** |
| 21.17's Q2 — the analysis-time re-derivation seam, five unguarded consumers plus the live-game freeze | `tasks/phase-21.md`:5975-5976 | **CARRIED** |
| `testimony_shapes` lacking the stamp-vs-environment guard its 21.19 sibling carries | `tasks/phase-21.md`:5998-5999 | **CARRIED** |

### Erratum (2026-09-05) to Task 21.25's merge-reality record, and to `audits/review-2026-08-19/B/meetings-manager.md`:101

Both records state that `DEFAULT_VOTE_RATIONALE` (`meetings/manager.py`:226) carries **the same
trigger-split defect** the husk `free_text` fix repaired — a single unconditional literal where the
trigger is recorded on the `DefaultedCall` beside it. **Re-derived at close HEAD, that is false: the
ballot path is ALREADY split by trigger.**

* the **deadline** branch returns `_default_vote` (`meetings/manager.py`:2144), which carries the literal `"(missed deadline; default skip)"` from the constant at :226;
* the **`ValidationError`** branch returns `_vote_parse_default` (:2178-2180), whose `model_copy` at :2883-2889 **REPLACES `rationale_text` wholesale** with `VOTE_PARSE_DEFAULT_MARKER` (:333-335);
* both halves are pinned, in `tests/meetings/test_manager.py` and `tests/eval/test_vote_correctness.py`:1561.

So the row is **re-typed from residue to CORRECTION**, on the #423 falsified-by-derivation precedent:
an additive dated erratum against both records, **never a repair and never a rewrite of either**
(`meetings/` is out of scope on a close). **The genuine item beside it, routed and not fixed,** is a
legibility one: the comment at `meetings/manager.py`:224-225 calls it *"the same marker"* as the turn
default, which is the reading that invited this finding twice.

---

## 5. The routed next decision — the next pre-registration (the owner's)

**The recommendation, first: charter a NEXT pre-registration that re-parameterises the SHARE-and-COUNT
pair, and take a further record on the same slate. Do not take the override, and do not carry the
slate as toggles indefinitely.** The reason is in the record's own cells, and it is the strongest
argument this phase produced:

* the reporter channel **closed faster than every other route** — 34 → 11, **−67.6%**, against non-reporter 12 → 9, −25% (§3.1);
* the structural null the share is read against **FELL**, 0.3152 → 0.2553, so **0.40 was reachable on these bytes** and the miss is not an artifact of who happened to be alive (§3.1);
* and the two bars **pulled against each other by construction**: at the record's 9 non-reporter wrongful ejections bar 4 needed `R ≤ 7` holding the total, while bar 3 asked for `R ≤ 12` and got 11 (§3.1's verbatim §7 quote).

A share bar and a count bar on the same cell is a design question, not a result. Re-parameterising
them is cheap — it is a memo, not a record — and it is the only option that converts this phase's
FINDING into a decision rather than a stalemate.

**The three options, priced. One counting note first, because the two numbers are easy to conflate:
the Wave-2 SLATE is THREE levers** — `reporter_reasoning`, `corroboration_discipline`,
`testimony_shapes` — and every option below scopes exactly those three. The registry's **four** live
toggles are those three plus `impostor_roll_call`, which is Phase 18's, is unrelated to this record,
and rides none of these options (§3.3).

| option | what it costs | what it buys | what it risks |
|---|---|---|---|
| **(i) a next pre-registration + a further record on the same slate** — *recommended* | one memo (offline, `$0`), then one record: **≈ 12h05m of recording wall, ≈ 15h48m elapsed with outages** at this phase's own measured rate (`…adopting-record.md` §2.6), against the smoke's bracket 12h46m50s / 13h56m45s / 16h02m42s and 21.15's realized **11h54m28s** | a verdict the slate can actually reach, on bars that do not pull against each other; and a second read of a slate that already met three of four | a second FINDING, if the reporter share is structural rather than parameterised. The counter-evidence is the falling null |
| **(ii) the §6.1-shape owner override of the FINDING verdict** | zero operator wall | the slate graduates now; the ladder tip moves; the ML re-fit and the §10.2 digest-pair re-declaration become due AT THAT RECORD (§4) | it is the **second** override in two phases. The apparatus survives one override that is written down as one; a habit of them is the failure mode pre-registration exists to prevent. **Available and UNTAKEN — the owner's alone, at any later point, recorded as an override of a FINDING verdict and never as a bar that passed** |
| **(iii) neither — carry the slate as its three live toggles** | zero | optionality | the featured-strip residue stays visible to visitors (§4), and three measured levers sit unadopted with no scheduled decision. This is the status quo, and it is what the tree does if nothing is chartered |

**The backlog the two registers added, sized for whichever route is taken:** **39 actionable findings**
untouched (20 A, 19 B — §3.4; the fortieth untouched id is `B-34`, which the register itself REFUTED
and which is therefore not work), plus the hardening audit's **42** close-ledger entries and **19**
informational ones, all of BASELINE-8 vintage (§3.5). The balance wave the prior close recommended
(`audits/audit-phase-20-close.md` §4, six levers with their measured evidence) **chartered nothing and
is unspent**; it is still the largest single block of measured, unaddressed gameplay work, and it now
competes with the injustice slate rather than following it.

**Two decisions that do not ride this one, stated separately as the prior close stated them.**

### 5.1 The ML program's cadence, now that the re-ground is spent

The re-ground was this phase's mandatory step and it is done: the fits are on the baseline-8 corpus,
the amnesty is deleted, the campaign tier is green (§1). Two live items sit under this decision and
they are **different sizes**, so they are not folded together:

* **21.17's Q1 — the λ-grid and campaign re-search under 21.16's repaired objective.** Explicitly an OWNER decision at campaign scale, held for this ledger. Live, and priced as a campaign.
* **the second ML re-fit — NOT DUE**, by the record's own §7. Sized *"zero now; one corpus re-fit at the triggering record"* (§4).

### 5.2 The live-API deployment

**Still refused.** The static bundle remains the sanctioned path and the Pages deploy is green on
close HEAD (§1).

**What the close does NOT do.** It makes no ruling. Per the 15.18 convention **the owner's merge of
this document ratifies the close reading and the routed next decision** — for this menu, option (i)
as the recommended route — **unless the owner records a different ruling on the PR before merging**,
which is folded into this audit body pre-merge; any ruling arriving after the merge lands as a dated
additive erratum here rather than an in-place rewrite. The ruling charters nothing by itself: the next
phase opens only when its own `tasks/phase-N.md` is authored and ratified.

---

## 6. Decisions

- **The close verifies; it does not fix.** F1 (the close audit's own unbound state), F2 (the ungated byte half of the registry rows), F3 (the unguarded finding map), F4's record-README half and F5 (the carried staging ref) are recorded and routed. No test, script, production package or front-door page outside this contract's files was touched, with the two mechanical scope admissions below — each forced by a fail-loud check that the close's own mandated artifact trips, or named by the contract.
- **`audits/README.md` gains exactly one entry — forced, and drafted to the gates that scan it.** `scripts/check_doc_facts.py::check_audits_index` fails the DEFAULT tier on any top-level `audits/*.md` the index does not link exactly once, so landing this file forces the entry. That entry is itself scanned by `check_ladder_tip` (it names **baseline 8** as the tip), by `_INJUSTICE_SENTENCE` (its wrongful-ejection sentence names the record's own counts), by `check_finding_figures` (its `11/20 = 0.5500` is the verdict table's own cell, and no bare `11/19` appears) and by `check_owner_action` (no positive undated owner-action verb, because **this phase's owner made no override** — the phase-20 close's *"the owner ratified … and adopted"* banner may not be reprised).
- **The index entry states the fall in its own words rather than in `_FINDING_FALL_CLAIM`'s, because the gate's own test suite pins it that way.** The first draft carried the required sentence *"innocent ejections fell from 46 to 20"* verbatim. `tests/scripts/test_check_doc_facts.py:2460-2468` (`test_a_claim_document_that_never_states_the_fall_is_not_required_to`) asserts that `audits/README.md` carries **neither** claim stem — it is the deliberate NEGATIVE CONTROL proving the wording rule is a gate on pages that publish the count and not a demand that every claim document publish it — and three sibling perturbation tests count errors against that same tree. So the entry writes the counts as *"a wrongful-ejection total that fell from 46 to 20"* and *"11 of 20 = 0.5500"*. **The figures stay gated**: `check_finding_figures` binds the share to the verdict table wherever a claim document writes it beside the word "reporter", and `check_ladder_tip` binds the tip. Only the fall's phrasing is the index's own, which is exactly what that test exists to permit.
- **A checker false positive met while drafting, recorded because it is reproducible.** With the required fall sentence present, `check_owner_action` fired on the word *"adopting"* inside the **filename** `audit-phase-21-adopting-record.md` in the neighbouring bullet — *"it states this record's fall beside 'adopting'"* — because `prose_blocks` splits on blank lines only, so a tight bullet list is one block, and a link's own filename is read as prose. It is moot for the wording finally used, and it is filed with the other two checker-prose heuristics (§4) with its perturbation case: a positive owner-action verb in a NEIGHBOURING list item must not fail this check, and one in the same sentence must.
- **`docs/artifacts.md` is edited twice, both named.** (a) The `audits/` registry row, re-derived from the git index rather than incremented by hand — landing the close audit trips `inventory_problems` in the DEFAULT tier — with **both** halves re-derived in the same edit because the byte half drifts silently (F2). (b) One **dated additive line** correcting the "provisional answer" sentence at :195-197, which the owner's merge of #428 ratified (F4). The page was already open for (a); leaving a ratified decision described as open while editing the paragraph beside it would close the phase on the exact defect class the phase opened against. The record's own README is **not** touched.
- **The README phase-21 row KEEPS its contract link, breaking the table's own convention.** Every closed row carries `[audit](…)` alone, but `README.md`:203's `[contract](tasks/phase-21.md)` cell is the **only** link to this phase's contract in either front-door document — `docs/history.md`'s `## Phase 21` section, alone among the phases, never linked it (compare `docs/history.md`:173's `[Contract](../tasks/phase-20.md)`) — and `docs/history.md` is out of scope here. Following the convention would orphan `tasks/phase-21.md` and fail `check_phase_coverage` in the DEFAULT tier. The cell is written `[audit](…), [contract](…)` on the two-link precedent the table already carries at `README.md`:188, and **the missing `docs/history.md` contract link is routed as a named carried item** for the next contract that owns that page.
- **`README.md:29`'s Status bullet is corrected in the same pass, and the scope admission is recorded.** It read *"phases 0–19 closed, the last on 2026-08-18; phase 20 open"* and contradicted `:173` two sections below. The contract widens the README scope line to admit it and prices the rewording as word-neutral; 21.25 routed it here by name as an F2-class instance. **It is corrected to the final state — *"phases 0–21 closed, the last on 2026-09-05"* — rather than to the contract's example wording *"phase 21 closing"***, because after this merge "closing" is the same contradiction one word softer: the DoD requires that a reader of either surface cannot conclude the phase is still under way. The correction is word-NEGATIVE (eleven for eight), which the ceiling permits. Precedent: `audits/audit-phase-20-close.md`:475-477.
- **The word budgets bind and were measured, not hoped — and the real headroom is smaller than the ceiling.** `wc -w README.md` read **3,535** against the gated ceiling **3,550** (`scripts/check_doc_facts.py:835-840`) before the edit and **3,533** after it: the phase-table row's trim from its 62-word `Open:` blurb to the table's closed one-line convention is word-NEGATIVE and more than pays for the status paragraph, so all three edits fit with **no ceiling change and no unrelated prose cut**. **The binding constraint turned out not to be the ceiling but the perturbation suite**: `tests/scripts/test_check_doc_facts.py`'s `test_stray_win_rate_claim_detected` and `test_repeated_results_claim_detected` APPEND 9 and ~12 words to the real README and then assert an exact error count, so a page inside its ceiling by fewer than about a dozen words makes those tests fail with a budget error beside the drift they are testing — which the second test's own comment already warns about. A first draft at **3,543** did exactly that; the page was trimmed and the suite reads *"237 passed"*. Worth stating because the effective ceiling is ~3,538, not 3,550, and nothing says so where an author would look. `docs/lessons.md` at 1,499/1,500 is why its carry (§4) is a trim-plus-add. **No ceiling was raised**; raising one takes an owner-ratified contract.
- **Every `tasks/phase-21.md` anchor is stated at close HEAD, and the shift this PR introduces is stated with it.** The contract's anchors were re-verified before editing; the STATUS-banner edit then moved every line below line 3 down by 14 (a 4-line block became 18), so `:6781` becomes `:6795`, `:7286` becomes `:7300`, `:7501` becomes `:7515`, and so on. Rather than half-updating them, the audit fixes ONE convention in its Grounding paragraph — the numbers read `git show fa739ccb:tasks/phase-21.md` — and names the offset. Anchors into every other file are unmoved by this PR.
- **`_LADDER_TIP_AUDIT` is NOT "corrected".** It points at the maintenance re-record because nothing graduated, which is right on a FINDING (§3.3). `scripts/` is out of scope and the constant is correct; the close states the inversion in one place so a later reader does not repair it.
- **The gate's two states are both quoted and nothing is averaged.** The default tier is green in the clean state AND in the restored state — that is the finding, and it is the point of running the pair. The campaign tier, `--complete` and the validity gates ran restored; `verify_samples.sh` ran in a bare environment (`env -i`); every §1 row names its state. **The record's own end-to-end proof (`…adopting-record.md` §6.1) is quoted beside this close's run, never in place of it.**
- **The before/after table quotes; it never recomputes.** Every baseline-8 cell is the instrument pin the memo cites or the re-record audit's published cell; every post-record cell is read from the adopting record's §3/§4/§5. A close-session recomputation with new definitions is exactly how a pre-registered read gets quietly re-priced.
- **Bar 4's two denominators are kept apart on purpose.** The verdict restatement carries **11/20 = 0.5500 alone** — the registered cell, pooled over all twenty wrongful ejections. The per-row null read (19 rows, 11/19 = 0.5789) lives in one paragraph of its own, labelled OFFLINE and observed-never-gated, because the record states it did not enter the verdict. No gate can catch a mis-scope here, which is why the rule is written down rather than assumed.
- **The hardening audit's §4.2 counts are reconciled, not contradicted, and no erratum is offered.** The heading's 36 is the round-1 register's routing tally across nine themed bullets; the tenth bullet carries six round-2 ids; 42 entries in total (§3.5). Filing a "discrepancy" against a record that counts consistently within its own registers would be a false finding.
- **No tag is minted.** Nothing this close produced needs byte-level provenance beyond git. The honest precedent stands: no `phase-17-close`, `phase-18-close`, `phase-19-close` or `phase-20-close` tag was ever minted (§8's `git ls-remote --tags`, which
returns only `attempt-1-phase-10-wave1-rerecord`, `phase-16-baseline-4`, `phase-16-baseline-5` and
`phase-18-corpus-8f5f434`).
- **The PR STOPS OPEN.** This contract is owner-gated on its own face — the title says `(owner)`, the ratified plan's owner-gate roster lists `21.26 (the close)` (`tasks/phase-21.md`:253-261), and the DAG edge is tagged `[OWNER]` (:159). The 2026-09-02 per-PR delegation recorded on #419 **did not generalize**: #424, #426, #427 and #428 each stopped open and were owner-merged. No ruling of a worker's or an orchestrator's stands in for the owner's here.

---

## 7. Provenance + the frontier

- **Close HEAD:** `fa739ccb` — *"coordination: re-anchor Task 21.26 (the close audit and ledger) to the FINDING outcome at 9618fe95 …"*, 2026-09-05, sitting on the 21.25 merge-reality commit `9618fe95` above PR #429 (`d255f5fe`). `origin/main` and the close branch agree; the working tree was clean apart from the by-design untracked evidence restore, which was `--clean`ed and never staged.
- **The phase's chain:** the planning commit `772742c2` (*"planning: phase 21 — the re-ground on corrected bytes (charter + 26 contracts)"*, PR #396, 2026-08-27) and everything after it through close HEAD: `git rev-list --count 772742c2^..fa739ccb` = **83** — **34 PR merges** (#396–#429) and **49 coordination commits** (pre-dispatch re-anchors, merge-reality records, rulings and errata).
- **The window:** 2026-08-27 → 2026-09-05, ten days, with **two** operator recording sessions inside it — 21.15's realized 11h54m28s over 299 games (2026-08-30/31) and 21.24's ≈12h05m of recording wall / ≈15h48m elapsed over 300 games (2026-09-03/04). This is the first phase in the project's history to spend two operator records in one arc.
- **The frontier computes complete on this close's merge.** With the merged `task 21*` titles from a log **pinned to close HEAD** (28 titles), `compute_frontier` reads **AT HEAD: dispatchable `['21.26']`, blocked `[]`, merged 25**; **WITH 21.26 MERGED: dispatchable `[]`, blocked `[]`, merged 26.** `parse_all_tasks` returned zero errors. The log is pinned so the snippet still reproduces after this close merges.
- **The evidence pins, both fetched by sha and verified at this close (3269/3269, §1):** `476a1f85492439277350af9708f1d120eb1c0a71` (`evidence/phase-18-coevo`) and `29af85d5457caeba4f8ba8ba77610c6a0ab2213a` (`evidence/phase-21-wave2-finding`, the FINDING recording — 316 files, 260,116,543 bytes, parentless). The 19.21 raw-slate ruling stands **RECOVERED**.
- **Remote refs observed** (read-only): branches `evidence/phase-18-coevo` → `476a1f85`, `evidence/phase-21-wave2-finding` → `29af85d5`, and `evidence/raw-slate-staging` → `c27ab7b5`, the last being **F5**. Tags: no `phase-21-*` tag exists and none is required.
- **THE GATE.** This contract is **owner-gated** (`tasks/phase-21.md`:253-261) and its PR **stops open**. The ratification convention is `audits/audit-phase-20-close.md`:459-464: the owner's merge IS the ratification of the close reading and of the recommended route. No merge is asserted here before it has happened.
- **The banner and the front door record the close in this PR:** `tasks/phase-21.md`'s STATUS line → CLOSED, and README's `## Project status` sentences, its `**Status**` bullet and its phase-21 row → the close, its date, its outcome and this audit's path. The PR also carries the `docs/artifacts.md` registry re-derivation and its one dated line (§6).

---

## 8. Method + reproduction (all `$0` against committed bytes; network only where named)

```
# Full history before any history claim (the AGENTS.md rule); guarded so a
# complete clone does not error.
if [ "$(git rev-parse --is-shallow-repository)" = "true" ]; then
  git fetch --unshallow origin
else
  git fetch origin
fi

# §1, in the order actually run. §1's table is grouped by leg for reading; this is the session.
bash scripts/check.sh                                       # 1. default gate — CLEAN state
bash scripts/fetch_evidence.sh                              # 2. OK: 3269/3269 — TWO families
uv run pytest -m campaign -q                                # 3. RESTORED — 331 passed, exit 0
uv run python scripts/verify_ml_evidence.py --complete      # 4. RESTORED — 63 | OK 58 | FAIL 0 | ABSENT 0 | INFO 5
bash scripts/check.sh                                       # 5. THE PAIRING — same gate, RESTORED state
env -i PATH="$PATH" HOME="$HOME" bash scripts/verify_samples.sh   # 6. 100/100, zero AILIBI_* exports
for s in replays/samples/9p2i replays/ml_corpus/9p2i \
         replays/samples/4p1i replays/ml_corpus/4p1i; do
  uv run python scripts/validity_gate.py "$s"; done         # 7. four PASSes
uv run python scripts/check_doc_facts.py                    # 8. front-door facts green
bash scripts/fetch_evidence.sh --clean                      # 9. removes the 3,267 restored files
git status --porcelain replays/                             # 10. empty, incl. replays/records/
uv run python scripts/verify_ml_evidence.py --complete      # 11. CLEAN — 60 | OK 48 | FAIL 0 | ABSENT 7 | INFO 5, exit 1 BY DESIGN
grep -c STALE scripts/verify_ml_evidence.py                 # 0 — the amnesty is gone from the source

# §2 — the ledger, one fresh command per contract
grep -cE "The engine certified|flagged_contradictions|the detector already found" \
  agents/strategic/prompts/qwen3_6_27b/accusation_round.j2 \
  agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2                                     # 21.1 — 0/0
uv run pytest tests/agents/test_vote_transcript_parity.py tests/meetings/test_vote_guard_rationale.py \
  tests/eval/test_vj_instruments.py -q                                                    # 21.2
uv run pytest tests/orchestrator/test_replay.py tests/eval/test_replay_walk.py \
  tests/eval/test_wave2_metrics.py -q                                                     # 21.3
uv run pytest tests/agents/test_memory_rendering.py tests/agents/test_memory.py \
  tests/agents/test_features.py -q                                                        # 21.4
uv run pytest tests/observation/test_service.py -q                                        # 21.5
uv run pytest tests/engine/test_tick.py tests/eval/test_replay_walk.py \
  tests/api/test_replay_loader.py -q                                                      # 21.6
uv run pytest tests/eval/test_watchability.py tests/eval/test_meeting_quality.py \
  tests/eval/test_vote_correctness.py tests/eval/test_gate_spec_metrics.py -q             # 21.7
uv run pytest tests/training/test_surrogate_dataset.py tests/training/test_surrogate_runner.py \
  tests/training/test_conviction_model.py -q                                              # 21.8
uv run pytest tests/eval/test_accusation_calibration.py tests/eval/test_deduction_metrics.py -q   # 21.9
uv run pytest tests/scripts/test_record_ml_corpus.py tests/scripts/test_validity_gate_cli.py \
  tests/scripts/test_verify_ml_evidence.py -q                                             # 21.10
uv run pytest tests/scripts/test_check_doc_facts.py -q                                    # 21.11
grep -nI "baseline-6\|baseline 6" scripts/record_ml_corpus.sh | wc -l                     # 21.11 — 4
(cd frontend && npm run test)                                                             # 21.12
uv run pytest tests/training/test_scenarios.py -m campaign -q                             # 21.13
git status --porcelain replays/                                                           # 21.14, 21.23 — empty
uv run pytest tests/training/test_rewards.py tests/training/test_bakeoff_harness.py \
  tests/engine/test_rng.py -q                                                             # 21.16
uv run pytest tests/eval/test_reporter_justice.py tests/orchestrator/test_meeting_integration.py -q  # 21.18
uv run pytest tests/orchestrator/test_replay_meetings.py tests/experiments/test_probe_backends.py -q # 21.19
uv run pytest tests/meetings -q                                                           # 21.20
uv run pytest tests/scripts/test_counterfactual_phase21.py -q                             # 21.21
uv run pytest -q -k "deduction_metrics or funnel or evidence_honesty or solvability or reporter_justice"  # 21.22
uv run pytest tests/meetings/test_lever_registry.py tests/api/test_sets.py -q             # 21.25
grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator | wc -l                    # 21.25 — 5

# §2.2 — the nine PRs the grep does not reach
grep -c '^### Task 21\.' tasks/phase-21.md                                                # #396 — 26
grep -n 'saw_kill' agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2                    # #417 — :145
git show 5ab03fd7 --stat                                                                  # #420
grep -c "P-1k\|P-1ka" scripts/counterfactual_phase21.py                                   # #421 — 5
grep -c '\-\-recording\|recorded.slate' scripts/counterfactual_phase21.py                 # #422 — 18
grep -cE '"R-13"|"R-14"|"C-9"' scripts/counterfactual_phase21.py                          # #423 — 6
grep -c 'def sighting_placement' meetings/transcript.py                                   # #424 — 1
grep -c '^## 18 — Post-#424 re-smoke' audits/audit-phase-21-smoke-wave2.md                # #426 — 1
grep -c 'PR #427, OWNER-GATED' audits/audit-phase-21-preregistration.md                   # #427 — 7
gh pr list --state merged --base main --limit 60 \
  --json number,title,mergedAt,mergeCommit                                                # the 34-row reconciliation

# §3.3 — the FINDING branch, read out of the tree rather than from this contract
uv run python -c "
from orchestrator.replay import (SUBSTRATE_FLAG_KEYS, TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    _RETIRED_ALWAYS_ON_LEVERS, _TOGGLEABLE_LEVER_RESOLVERS, substrate_flag_snapshot)
s = substrate_flag_snapshot({})
print('retired', len(_RETIRED_ALWAYS_ON_LEVERS), '| toggles', len(_TOGGLEABLE_LEVER_RESOLVERS),
      '| stamp keys', len(SUBSTRATE_FLAG_KEYS), '| True', sum(s.values()),
      '| False', [k for k, v in s.items() if not v])"
uv run python -c "
from eval.watchability import _BASELINE_SUPPLY_FLOORS, _DEFAULT_BASELINE_ID
from training.bakeoff.harness import BAKEOFF_BASELINE_ID
print(_DEFAULT_BASELINE_ID, BAKEOFF_BASELINE_ID, sorted(_BASELINE_SUPPLY_FLOORS))"

# §3.3 — §6.1's "what no surface may say", over the tree AND the phase's whole commit history
git grep -nI -iE '(bars? (were )?(passed|met)|passed the bars?|met the bars?|met its bars?|adopted on the (arithmetic|numbers)|verdict was ADOPTED|ADOPTED under the rule)' -- .
git rev-list --count 772742c2^..fa739ccb                    # 83
git log 772742c2^..fa739ccb --format='%H%n%s%n%b%n---' | grep -inE \
  'bars? (were )?(passed|met)|passed the bars?|met the bars?|met its bars?|adopted on the (arithmetic|numbers)|verdict was ADOPTED|ADOPTED under the rule'

# F1, F2, F3 — the three unbound surfaces, each measured rather than asserted
grep -rn 'audit-phase-2[01]-close' scripts/ tests/scripts/  # EMPTY — F1
uv run python -c "
import subprocess
from pathlib import Path
for root in ('audits', 'tests/fixtures'):
    files = subprocess.run(['git','ls-files',root],capture_output=True,text=True,check=True).stdout.split()
    print(f'{root}: {sum(Path(f).stat().st_size for f in files):,} tracked bytes / {len(files)} files')"
sed -n '234,240p;437p;449p' scripts/check_doc_facts.py      # F3 — the pinned index, contract and id pattern

# §3.5 — the hardening routings
grep -n 'H-3[23]' tasks/phase-21.md                          # empty — no disposition
grep -c 'baseline-6' docs/artifacts.md                       # 0 — H-36 closed
sed -n '68,71p' docs/reading-guide.md                        # H-37 still open

# §6 — remote observation (read-only), and the word budgets
git ls-remote origin 'refs/heads/evidence/*' ; git ls-remote --tags origin
gh run list --workflow=pages.yml --limit 5
wc -w README.md docs/reading-guide.md docs/ml-program.md docs/lessons.md
```

```python
# §3.4 — the finding→outcome map's acted-on set, DERIVED rather than assembled by hand:
# every A-/B- id named inside a `### Task 21.N` section, minus ids only the close's own
# section cites (A-20, A-25, which §3.4 carries in the recorded-as-finding row).
import re, pathlib
text = pathlib.Path("tasks/phase-21.md").read_text()
heads = [(m.start(), m.group(0)) for m in re.finditer(r"^### Task 21\.\d+[a-z]? — .*$", text, re.M)]
spans = [(heads[i][0], heads[i + 1][0] if i + 1 < len(heads) else len(text), heads[i][1])
         for i in range(len(heads))]
seen: dict[str, list[str]] = {}
for start, end, head in spans:
    tid = re.match(r"### Task (21\.\d+[a-z]?)", head).group(1)
    for a, b in re.findall(r"\b([AB])-(\d{1,3})\b", text[start:end]):
        seen.setdefault(f"{a}-{b}", []).append(tid)
acted = {i: t for i, t in seen.items() if [x for x in t if x != "21.26"]}
print(len(acted), "acted-on;", sorted(i for i in seen if i not in acted), "cited only by the close")
```

```python
# §6 — the phase-complete frontier, cross-checked against a git-log title index PINNED to
# close HEAD, so the snippet still reproduces after this close merges (an unbounded log
# would already carry 21.26's own merge title and collapse the before/after).
import subprocess, sys; sys.path.insert(0, "scripts")
import compute_next_task as cnt
from _task_parser import parse_all_tasks
titles = [t for t in subprocess.run(
    ["git", "log", "fa739ccb", "--format=%s", "--grep=^task 21"],
    capture_output=True, text=True, check=True).stdout.splitlines()
    if t.lower().startswith("task 21")]
errors: list[str] = []; tasks = parse_all_tasks(errors); assert not errors
print(cnt.compute_frontier(tasks, set(), titles, 21))                  # dispatchable ['21.26'], merged 25
print(cnt.compute_frontier(tasks, set(), titles + [
    "task 21.26: the phase close (owner)"], 21))                       # dispatchable [], merged 26
```

### The gate on the tree this close leaves behind

The whole cycle above was re-run end to end on this branch — the close audit landed, the index entry
added, the registry row re-derived from the index, the three banners flipped — with every leg timed.
**All twelve legs green, exit 0** (bar the deliberate clean-state `--complete`, exit 1 by design):

```
check.sh CLEAN                        146 s (exit 0)   ✓ built in 223ms
fetch_evidence                          6 s (exit 0)   OK: 3269/3269
campaign tier                         160 s (exit 0)   331 passed, 6111 deselected in 159.03s (0:02:39)
verify_ml_evidence --complete RESTORED 29 s (exit 0)   checks: 63 | OK 58 | FAIL 0 | ABSENT 0 | INFO 5
check.sh RESTORED                     148 s (exit 0)   ✓ built in 229ms
verify_samples BARE                     2 s (exit 0)   All 50 samples verified clean.  (×2)
validity gate 9p2i samples              3 s (exit 0)   Validity gate PASSED (all checks green).
validity gate 9p2i corpus               7 s (exit 0)   Validity gate PASSED (all checks green).
validity gate 4p1i samples              1 s (exit 0)   Validity gate PASSED (all checks green).
validity gate 4p1i corpus               1 s (exit 0)   Validity gate PASSED (all checks green).
check_doc_facts                         1 s (exit 0)   Front door verified: … Budgets verified: 4 pages
fetch_evidence --clean                 14 s (exit 0)   Removed 3267 restored file(s).
verify_ml_evidence --complete CLEAN    24 s (exit 1)   checks: 60 | OK 48 | FAIL 0 | ABSENT 7 | INFO 5
```

and `wc -w README.md` reads **3,533** against its gated 3,550. That is the last measurement this
phase takes.
