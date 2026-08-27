# Phase-20 close — CLOSED: evidence honesty shipped, one pre-registered record spent, the rule returned FINDING and the owner adopted baseline 7 over it; 42 dispatched contracts merged and re-verified at close HEAD (the close is the 43rd); the next decision — the balance wave — routed to the owner (Task 20.42)

**Date:** 2026-08-26.
**Task:** 20.42 — the phase close (owner). Phase 20 was chartered from the three-track review of
2026-08-19 (`audits/review-2026-08-19/`) and its synthesis: wave 0 and wave 1 repair the claims the
front door made and could not support, wave 2 is the evidence-honesty substrate under ONE
pre-registered record, wave 3 is presentation on the corrected bytes. This close **verifies and
routes**: the whole gate re-run at close HEAD by the verifiers' actual paths (§1), every dispatched
contract re-verified with a fresh contract-specific command (§2, none silent), the before/after story
in generated numbers with the pre-registered bars read back bar by bar (§3), the two halves of the
recorded outcome checked against the tree (§3.3), the review's finding→outcome map (§3.4), and the
routed next decision — the balance wave — put to the owner with a costed recommendation (§4).

**Close HEAD:** `937bd805` (= `origin/main` tip at the close session: *"coordination: re-anchor
20.42 …"*, on top of the 20.41 merge `3e0327bc` / PR #394). The clone was complete, not shallow
(`git rev-parse --is-shallow-repository` → `false`), before any history-derived claim below.

**Grounding:** every number below is either read from a committed pin / recorded audit named beside
it, or computed at close HEAD by a command in §7. Everything ran $0, deterministic, against the
fake provider. Network was touched only by the named tooling legs: the evidence fetch by pinned sha
(`scripts/fetch_evidence.sh`, §1), the read-only `git ls-remote` queries (§6), and read-only GitHub
API reads of the Pages workflow's run status (§1) and of PR #363 and #368 for their committed
measurement tables (§3.2).

**Verdict in one line:** Phase 20 **CLOSES COMPLETE** — the other 42 of its 43 dispatched contracts merged
(2026-08-19 → 2026-08-26, PRs #351–#394, 87 commits after the planning commit) and re-verified at
close HEAD, with two deviations recorded and none silent (§2); the default gate is **green at close
HEAD in both the clean and the restored-evidence states**, which is the pair the prior close
recorded as mutually exclusive — Task 20.17's repair holds, and the phase-19 F1 is **CLOSED by
measurement, not by assertion** (§1); the **opt-in campaign tier is RED** at close HEAD and is
recorded as this close's F1, routed and not fixed; the record's outcome is carried forward exactly
as recorded — the pre-registered rule returned **FINDING** (bars 1 and 2 missed) and the owner
**adopted the baseline-7 substrate anyway by explicit override on 2026-08-26**, and everything §6.2
executed is present in the tree while §6.1's "what no surface may say" holds across it (§3.3) — with
one index page found stating the wrong ladder tip and corrected here (F4); and the next decision goes
to the owner as **the balance wave, recommended as its own chartered wave with its own record** (§4).

**Four close-found defects (F1–F4) and one carried forward (F5).** Three are routed to the next
phase's inputs and one — a false ladder-tip clause on a page this PR was already forced to open — is
corrected in place, with the gate-coverage gap that let it survive routed rather than patched.

---

## 1. The gate rerun at close HEAD (the WHOLE gate, the verifiers' actual paths)

Every leg below ran at close HEAD `937bd805` in a clean worktree, in ONE session; §7's first block
lists them in the order they actually ran, while the table below groups them by leg for reading. The
**state** column matters: the prior close's F1 was found precisely by noticing which state each leg
was in, so the state is recorded beside every row rather than assumed.

| leg | invocation | state | result (quoted) | wall |
|---|---|---|---|---|
| default gate | `bash scripts/check.sh` | clean | **GREEN.** ruff *"All checks passed!"*; format *"397 files already formatted"*; `lint-imports` *"Analyzed 152 files, 794 dependencies."* / *"Contracts: 4 kept, 0 broken."*; *"Task docs validation passed: 364 tasks and 364 prompts."*; *"All 364 prompts are in sync."*; mypy *"Success: no issues found in 368 source files"*; pytest **"5304 passed, 20 skipped, 3 xfailed in 265.85s (0:04:25)"**; frontend lint + `tsc:check` + vitest *"Test Files 8 passed (8) / Tests 435 passed (435)"* + build *"✓ built in 296ms"* | 295 s |
| evidence restore | `bash scripts/fetch_evidence.sh` | → restored | *"OK: 2953/2953 files match 476a1f85492439277350af9708f1d120eb1c0a71."* — the by-sha fetch, restore and manifest verification of both class-(c) payloads | 6 s |
| **default gate, again** | `bash scripts/check.sh` | **restored** | **GREEN — exit 0.** mypy *"Success: no issues found in 368 source files"* (the SAME source-file count as the clean run) and pytest **"5304 passed, 20 skipped, 3 xfailed in 205.94s (0:03:25)"**. This is the pair `audits/audit-phase-19-close.md` §1 recorded as mutually exclusive at two legs; Task 20.17 repaired it and the repair holds under the close's own re-run | 223 s |
| campaign tier | `uv run pytest -m campaign` | restored | **RED — exit 1: "9 failed, 308 passed, 5327 deselected in 185.78s (0:03:05)"**. Recorded as **F1** below; routed, not fixed | 188 s |
| evidence completeness | `uv run python scripts/verify_ml_evidence.py --complete` | restored | *"checks: 55 \| OK 39 \| FAIL 0 \| STALE 11 \| ABSENT 0 \| INFO 5"* / *"verify-ml-evidence: every check passed."* — exit 0. The eleven STALE rows are the declared ML-grounding gap (`audits/audit-phase-20-baseline-7.md` §10.2), carried by the `ML grounding` row with both fingerprints; STALE is granted only to that ONE declared digest pair, so the fingerprint checks stay real gates | 27 s |
| byte identity | `bash scripts/verify_samples.sh` | restored, **bare env** (`env -i`) | *"All 50 samples verified clean."* (4p1i) / *"All 50 samples verified clean."* (9p2i) — 100/100, with zero `AILIBI_*` exports of any kind. This is the invariant a FINDING-branch substrate could not have held (§3.3) | 2 s |
| front-door truth | `uv run python scripts/check_doc_facts.py` | restored | *"Doc facts verified: README.md and .env.example agree with 2 sample manifests, audits/audit-phase-20-baseline-7.md, and the 22-lever substrate registry; eval/vote_correctness.py agrees with 4 recorded eval reports."* — exit 0 | 1 s |
| evidence clean-up | `bash scripts/fetch_evidence.sh --clean` | → clean | *"Removed 2952 restored file(s). Tracked bytes are untouched."*; `git status --porcelain` empty afterwards | 23 s |
| Pages deploy | `Deploy to GitHub Pages` (`.github/workflows/pages.yml:85`) | — | **success on `937bd805`** — run 33022737900, both jobs green (`Build the demo bundle` 39 s, `Deploy to GitHub Pages` 9 s incl. its own *"Verify the deployment answers"* step). **This is close HEAD, not the close commit** — see the note below | 57 s |

**The Pages leg is the one that cannot complete before the merge, and it is not claimed as complete.**
`pages.yml` triggers on `push` to `main`, so no run can exist for the close commit until the merge
creates it. What is verified before the merge: the deploy is green on **close HEAD** (the row above),
and the bundle builder that feeds it passes on **this PR's own tree** — `tests/scripts/test_build_demo_bundle.py`
*"28 passed"* locally (§2, 20.7) and inside CI's `Project checks`. The remaining half — the run on
the merge commit itself — fires automatically at merge and is the owner's to observe; the close does
not assert it in advance. Nothing else in this audit depends on it: the bundle bakes the committed
replay bytes, which the byte-identity and validity legs already certify.

**And once more on the tree this close leaves behind.** The rows above are close HEAD itself, before
this PR's own doc-only commits. Re-run on the final tree — the close audit landed, the registry row
bumped, the two banners flipped — `bash scripts/check.sh` is green again: *"All checks passed!"*,
*"397 files already formatted"*, *"Analyzed 152 files, 794 dependencies."* / *"Contracts: 4 kept, 0
broken."*, *"Task docs validation passed: 364 tasks and 364 prompts."*, *"All 364 prompts are in
sync."*, mypy *"Success: no issues found in 368 source files"*, pytest **"5304 passed, 20 skipped, 3
xfailed in 259.47s (0:04:19)"**, frontend 435 passed and *"✓ built in 293ms"* — exit 0, 274 s wall.

**The prior close's F1 is closed.** `audits/audit-phase-19-close.md` §1 recorded that the documented
`fetch_evidence.sh` restore and the documented `check.sh` gate were mutually exclusive at two legs —
mypy walked the restored slate's untracked helper scripts (*"Found 15 errors in 3 files (checked 358
source files)"* against the clean state's 354) and one scratch-tree pytest case symlinked the real
`training/artifacts/coevo/`. Both legs are green here in the restored state, with mypy reporting
**368 source files in BOTH states**. Nothing about that was taken on trust: the two `check.sh` runs
above are the same command at the same HEAD with exactly one variable toggled — whether the payload
is restored.

### F1 — the campaign tier is RED at close HEAD (recorded, routed, not fixed)

`uv run pytest -m campaign` exits 1 with **9 failed, 308 passed**. The nine fall into three classes,
each reproduced by reading the assertion rather than inferred:

* **Three substrate-sha self-consistency pins** — `tests/training/test_anchor_study.py::test_committed_study_artifacts_are_the_baseline6_fit`, `tests/training/test_coevo_driver.py::TestCommittedImpostorCampaignRows::test_substrate_sha_kind_and_value_dispatch_per_block`, `…::TestCommittedCrewCampaignRows::test_substrate_is_the_compute_sha_for_both_blocks`. All three assert `recorded_sha == compute_substrate_sha()` and all three read the same disagreement: recorded `f5865c53…`, live `9bc00af0…`. The eight graduations moved the composite; the committed campaign artifacts still carry the pre-graduation one.
* **Five corpus-derived fit pins** — four in `tests/training/test_composed_runner.py` (`test_composed_fidelity_scores_the_committed_test_split` **87 ≠ 96** test meetings; `test_composed_fidelity_top1_matches_an_independent_recompute` **55 ≠ 60** held-out ejections; `test_go_verdict_holds_under_the_live_teammate_exclusion_ranking`; `test_committed_composed_verdict_is_rederivable`, whose diff is `test_ejections 60 → 55`, `exact_outcome_match 0.7917 → 0.8161`, `top1_bar 0.6375 → 0.6000`) and one in `tests/training/test_surrogate_fidelity.py::test_fo6_rebaseline_collapses_to_always_skip_on_the_big_set` (top-1 `0.2323` against a pinned `20/101`). These are the corpus re-record reaching the ML fits — **87 held-out meetings against the pinned 96 is the very number `audits/audit-phase-20-baseline-7.md` §10.2 quotes** when it names the re-ground as a follow-up.
* **One scenario pin** — `tests/training/test_scenarios.py::test_kill_with_witness_fsm_hunts_elsewhere_and_earns_nothing` (`assert all(k.target != "p-5" for k in kills)` → False). This one **pre-dates the record**: the last scheduled `Campaign tier` CI run (32701066153, 2026-08-24, before the 20.36 merge) already failed it, in a run whose other five failures and four errors have since gone. It belongs to Task 20.32's mover repair, not to the recording.

**What this is, stated precisely.** It is the declared ML-grounding debt arriving at a gate the
declaration did not cover. §10.2 converted `scripts/verify_ml_evidence.py` to a `STALE` status and
re-shaped the `tests/training/` staleness caps into tripwires; it did not convert the campaign
tier's *dynamic* self-consistency pins (which compare against a live composite that the graduation
moved) or the composed/surrogate pins fitted on the pre-record corpus. **It is a bookkeeping debt
with a name, not an evidence defect** — every evidence check itself passed in the same session
(`--complete` exit 0, `verify_samples.sh` 100/100, all four validity gates PASS, §2). It is also not
a regression this close introduced: the tier was already red at its last scheduled run, in a
different shape.

**Routed, not fixed** (files NOT in scope: `tests/`, `training/`, `scripts/`). The destination is the
ML re-ground §10.2 already names: re-fit the surrogate and the conviction model on
`replays/ml_corpus/`, re-stamp the fit-corpus fingerprint and the MAP-Elites pool's substrate stamp,
move `BAKEOFF_BASELINE_ID`, re-publish `docs/ml-program.md`'s arms — and, as this close adds, take
the nine campaign-tier pins with it, either re-grounded or converted to tripwires in §10.2's own
declared shape. The one scenario pin is a separate, smaller item belonging to 20.32.

### F2 — two stale narrations whose own committed pins already disagree with them

Neither moves a byte; both are the exact class Craft rule 5 exists for (*a number is recomputed from
committed bytes*), and both are inside files this contract may not touch.

* **`orchestrator/game.py:388-391`** still reads *"The committed sample sets still stamp `*.qwen3_6_27b.v3` and re-render through the archived v3 bodies (`tests/fixtures/prompt_archive/qwen3_6_27b_v3/`) until the adopting record retires that entry."* The adopting record retired it: every committed replay stamps `qwen3_6_27b.v4`, `ARCHIVED_PROMPT_VERSION_SETS` is `{}` and `tests/fixtures/prompt_archive/` does not exist (§3.3). The neighbouring block at `:373-375` carries the same defect one generation older (the v1 archive, "until 16.17 re-records").
* **`frontend/src/lib/bodies.test.ts:9`** still describes the negative control as *"0 phantom frames vs 1,182 of 1,769 on `9p2i`"* — the baseline-6 census — while the assertion twenty lines below it pins **668 phantom frames of 1,217** on the baseline-7 bytes it now walks. The gate is correct and bites; only its own header sentence is stale.

Routed to the next phase's inputs as a prose-sweep item.

### F3 — three front-door word budgets, un-gated, exceeded at close HEAD

Three contracts set a word budget in their Measurement field and no check enforces any of them
(`grep -n 'word' scripts/check_doc_facts.py` finds no budget). Measured at close HEAD against each
contract's own target, with the count at that contract's own merge beside it — **and the merge
column is itself over budget on all three**, which is the first half of the finding:

| surface | contract target | at its own merge | at close HEAD |
|---|---|---|---|
| `README.md` | 20.12: ≤ ~1,800 (from 3,833) | **2,034 — over** (`d86f979c`) | **3,368** |
| `docs/reading-guide.md` | 20.12: ≤ ~900 (from 3,239) | **940 — over** (`d86f979c`) | **1,303** |
| `docs/ml-program.md` | 20.13: ≤ ~1,400 | **1,439 — over** (`dc9d73b7`) | **1,838** |
| `docs/lessons.md` | 20.40: 800–1,500 | 1,491 — inside (`989f1ee2`) | 1,491 — **inside** |

**Two separate misses, and they are stated separately.** First, each budget was already exceeded at
the merge of the contract that set it — README by 234 words, the reading guide by 40, the ML page
by 39 — so the deviation originated at the owning merge and was not introduced by anything later.
Second, four later contracts widened all three: 20.13's results table, 20.38's before/after column,
20.39's media block and 20.41's tail-truth pass each added prose to pages whose budgets were
already breached, taking README from 2,034 to 3,368.

The honest reading, which is why this is recorded rather than absorbed: the front door ended the
phase **12% shorter than at charter (3,833 → 3,368)**, not the 53% the target implied. Routed as a
next-phase item with the note that a budget nothing can fail is prose — Craft rule 2 applied to a
documentation target.

### F4 — the audits index states the wrong ladder tip, and no gate can catch it there

`audits/README.md`'s Phase-20 entry for the record audit ended *"the decision the arithmetic
selected. FINDING — the ladder tip stands at baseline 6."* That is false at close HEAD: the tip
stands at **baseline 7**, because the owner overrode the FINDING verdict (§3.3). The entry described
the branch the rule would have executed, not the one that was executed, on the index page a reader
reaches from the front door.

**Why it survived every gate.** `scripts/check_doc_facts.py::check_ladder_tip` holds every "ladder
tip" claim to the record audit's own sentence — but only inside `_LADDER_TIP_DOCUMENTS`, which is
`README.md`, `docs/glossary.md`, `docs/history.md` and `docs/reading-guide.md`
(`scripts/check_doc_facts.py:237-242`). `audits/README.md` is indexed for completeness by
`check_audits_index` and scanned for links, never for this claim. A repo-wide
`git grep -nI -i "ladder tip"` finds exactly one live surface making a wrong claim — this one — with
every other hit either a historical close correctly stating its own tip or a review report quoting
the phrase.

**Corrected in this PR rather than routed**, and the reason is mechanical: landing the close audit
*forces* an edit to `audits/README.md` anyway (`check_audits_index` fails the DEFAULT tier on any
un-indexed top-level `audits/*.md`), so the file was already open. Leaving a false ladder tip in it
while editing the paragraph beneath would close the phase on the exact defect class the phase opened
against. **The gate-coverage gap itself is routed, not fixed:** adding `audits/README.md` to
`_LADDER_TIP_DOCUMENTS` is a one-line change in `scripts/check_doc_facts.py`, which is not in scope
here, and it wants its own perturbation case (Craft rule 2) rather than a drive-by.

### F5 — the phase-19 close's F2 is still open (carried, not re-found)

`git ls-remote origin 'evidence/*'` at close HEAD still returns
`c27ab7b5… refs/heads/evidence/raw-slate-staging` beside the pinned
`476a1f85… refs/heads/evidence/phase-18-coevo`. The shortfall is not silent — it is recorded in
`training/artifacts/coevo/EVIDENCE-MANIFEST.md` and repeated in `docs/artifacts.md` — and its
consequence is duplication only, never integrity: the pinned orphan commit independently carries and
hashes every staged byte (§1's restore verified 2953/2953 against it). The remedy remains the
manifest's own one-command owner step: `git push origin --delete evidence/raw-slate-staging`.

---

## 2. The ledger — every dispatched contract verified-or-deviation-recorded

All 42 of the phase's other dispatched contracts merged. Each row below re-runs a **contract-specific** command at close
HEAD — taken from that contract's own `**Measurement:**` field, which is why the field exists — and
quotes its output. The boilerplate tail (ruff / format / lint-imports / generated prompts / task
docs / mypy / pytest / `check.sh`) is verified **once for the whole tree** by §1 rather than
re-quoted 42 times.

**Tally: 40 VERIFIED, 2 DEVIATION-RECORDED (20.12 and 20.13 — the word budgets of F3; neither
silent).**

| task (PR) | the fresh command at close HEAD | quoted output | verdict |
|---|---|---|---|
| 20.1 (#354) | `cd frontend && npx vitest run` (incl. `src/lib/bodies.test.ts`) | *"Test Files 8 passed (8) / Tests 435 passed (435)"* — the shipped rule reads **0 phantom frames of 1,217** on 9p2i and **0 of 601** on 4p1i; the retired accumulate rule, the negative control, reads **668/1,217** phantom frames and 1,371 phantom bodies, so the gate can fail | VERIFIED |
| 20.2 (#360) | same vitest run (`src/lib/copy.test.ts`) + `grep -rnE 'DESIGN\.md §\|Task [0-9]+\.[0-9]+\|audits/\|sentinel\|KPI' frontend/src` | 435 frontend tests pass; the grep's 293 hits are **all on source-comment lines**, none on a rendered string | VERIFIED |
| 20.3 (#367) | same vitest run (the layout/focus-trap suites) | 435 passed; `npm run lint`, `tsc:check` and `build` green in §1's frontend leg | VERIFIED |
| 20.4 (#357) | `uv run pytest tests/api/test_replay_loader.py -q` | *"83 passed in 8.63s"* — the corrupt/empty/mistyped fixtures still return 200 through the listing and the cost endpoint | VERIFIED |
| 20.5 (#351) | `uv run pytest tests/agents/test_prompt_loader.py -q` | *"56 passed in 0.28s"* — the one-notice-per-process pin holds; §1's bare-env `verify_samples.sh` emitted no notice line | VERIFIED |
| 20.6 (#353) | `uv run pytest tests/eval/test_vote_correctness.py -q` + `check_doc_facts.py` | *"89 passed in 1.08s"*; the front-door check names *"eval/vote_correctness.py agrees with 4 recorded eval reports"* | VERIFIED |
| 20.7 (#366) | `uv run pytest tests/scripts/test_build_demo_bundle.py -q` + the Pages job | *"28 passed in 2.94s"*, including the out-of-repo bake and the planted leg; `Deploy to GitHub Pages` **success on close HEAD** with its post-deploy verification step green. The run on the close *commit* fires at merge and is not claimed here (§1) | VERIFIED |
| 20.8 (#363) | `uv run pytest eval/leak_test.py tests/observation tests/test_firewall.py tests/training/test_leak_gate.py -q` | *"154 passed in 16.30s"*. The entitlement gate can fail: `tests/test_firewall.py:908` plants **M6** (`_visible_body_ids` without its room filter) and `:1017` asserts the scan catches it, with M1, M10 and a widened `visible_rooms_for_player` beside it. Before the change the same suite ran **125 passed with M6 planted** (PR #363's own recorded run) | VERIFIED |
| 20.9 (#352) | `uv run lint-imports` (§1) | *"Analyzed 152 files, 794 dependencies."* / *"Contracts: 4 kept, 0 broken."* against the review's `Analyzed 89 files, 379 dependencies`; the firewall suite's planted-route legs are inside the 154 above and `git status --porcelain` is empty after them | VERIFIED |
| 20.10 (#356) | `uv run python scripts/validity_gate.py <set>` × 4 | *"Validity gate PASSED (all checks green)."* on all four recorded sets, each with *"byte_identical_reconstruction: 0 samples drifted"* and *"cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact"* over 50 / 150 / 50 / 50 games | VERIFIED |
| 20.11 (#355) | `uv run pytest tests/engine/test_rules.py -q` + §1's byte-identity leg | *"10 passed in 0.95s"* (the in-vent action table and the mask-versus-engine property test); `verify_samples.sh` 100/100 in a bare env | VERIFIED |
| 20.12 (#371) | `wc -w README.md docs/reading-guide.md` + `check_doc_facts.py` | The front-door checks are green (§1), but the budgets read **3,368** and **1,303** against ≤ ~1,800 and ≤ ~900 — F3 | **DEVIATION-RECORDED (F3)** |
| 20.13 (#372) | `uv run python scripts/paired_stats.py training/reports/results-finalist-eval.jsonl` + `wc -w docs/ml-program.md` | The McNemar cells reproduce — *"clears alpha: p18-imp-ea4bc955, p18-imp-bfd145cb"*, *"fails alpha: p18-imp-6d327dcb, p18-imp-7f73929d"*, *"not significant even UNCORRECTED: p18-imp-6d327dcb"*, with `7f73929d 12/3 p=0.0352` against `alpha = 0.05 / 4 = 0.0125` — but the page reads **1,838 words** against ≤ ~1,400 — F3 | **DEVIATION-RECORDED (F3)** |
| 20.14 (#358, #364) | `uv run pytest tests/eval/test_solvability.py -q` | *"26 passed in 3.73s"* — the containment / singleton / singleton-correct / cleared-ejection cells re-derive from the committed bytes | VERIFIED |
| 20.15 (#365) | `uv run pytest tests/eval/test_evidence_honesty.py -q` | *"95 passed in 39.31s"* — every I-1…I-13 pin the pre-registration cites resolves at this HEAD | VERIFIED |
| 20.16 (#370) | `uv run pytest tests/api/test_view_model.py tests/api/test_sets.py -q` + the fetch grep | *"74 passed, 1 skipped in 10.06s"*; `grep -rn 'fetch(' frontend/src … \| grep -v src/api/client` prints **0** lines (2 at charter) | VERIFIED |
| 20.17 (#361) | `bash scripts/fetch_evidence.sh && bash scripts/check.sh` in ONE session (§1) | Both green, mypy reporting **368 source files in both states** — the phase-19 F1 pairing, re-run and closed | VERIFIED |
| 20.18 (#368) | §1's pytest leg | `uv run pytest -n auto --dist loadfile` → *"5304 passed, 20 skipped, 3 xfailed in 265.85s"* under sibling-worktree load; PR #368's own quiet measurement is **364.61 s serial → 89.75 s parallel** on the same 10-core host at `755fc487` (§3.2 states both, and §5 states the load honestly) | VERIFIED |
| 20.19 (#362) | `bash scripts/verify_samples.sh` (bare env, §1) | *"All 50 samples verified clean."* ×2 — the cached Jinja environment and the bisecting episodic scan are still byte-identical over 100 committed replays | VERIFIED |
| 20.20 (#374) | `python -c "xml.etree.ElementTree.parse(…)"` + `wc -c` + `check_doc_facts.py` | *"architecture.svg parses; 9671 bytes"* (budget < 60,000); the contract→prompt→PR exhibit link-check is inside §1's green `check_doc_facts` and the 178-test perturbation suite below | VERIFIED |
| 20.21 (#359, #388) | `uv run pytest tests/scripts/test_refresh_samples.py -q` | *"95 passed in 23.48s"* — the end-to-end and concurrency cases, including the #388 follow-up's dead-owner verdict surviving a release racing the probe | VERIFIED |
| 20.22 (#369) | `uv run pytest -q -k "evidence_honesty or solvability or deduction_metrics"` | *"211 passed, 5433 deselected in 49.27s"* — every pin the ratified memo cites resolves at close HEAD | VERIFIED |
| 20.23 (#375) | `uv run pytest tests/agents -q` | *"1007 passed in 47.18s"* (the completed-task memory rules, fixture-pinned); the lever is unconditional at close HEAD and its bar-6 cell is **0 fabricated lines on all four sets** (§3.1) | VERIFIED |
| 20.24 (#376) | same `tests/agents` run | 1007 passed — the self-location trail's coverage and room/tick agreement pins; bar 3's recorded cell is **0.77% pooled** against 20.12% (§3.1) | VERIFIED |
| 20.25 (#377) | `uv run pytest tests/meetings -q` | *"1050 passed in 13.96s"* — movement read as a destination claim; the I-7 movement-origin cell is **1/91** pooled against 38/313 (§3.1) | VERIFIED |
| 20.26 (#378) | `uv run pytest tests/api/test_evidence_mechanisms.py -q` + the meetings run | *"16 passed in 1.95s"* / 1050 passed — grounded prosecution and the two-source STRONG rule; bar 5's surviving-STRONG population is **0** (§3.1) | VERIFIED |
| 20.27 (#379) | `uv run pytest tests/meetings -q` | 1050 passed — map-aware arbitration; the adjacent-room STRONG count is **148 → 0** (§3.1). Closes no review finding, so it correctly carries no row in the published map (§3.4) | VERIFIED |
| 20.28 (#380) | `uv run pytest tests/meetings -q` (incl. `test_manager.py`) | 1050 passed; the I-8 marker cells are **0/3602 turns and 0/7211 prompts** on the recorded bytes (§3.1) | VERIFIED |
| 20.29 (#381) | `uv run pytest tests/agents -q` (incl. the meeting-history and reported-testimony suites) | 1007 passed — meeting outcomes, revealed roles and testimony as content | VERIFIED |
| 20.30 (#382) | `uv run pytest tests/agents tests/eval/test_evidence_honesty.py -q` | 1007 + 95 passed — the render census reads **mean 37.03 rows/snapshot with 26,735 testimony rows** against 51.1038 / 18,319 (§3.2) | VERIFIED |
| 20.31 (#383) | `grep -c "VERIFIED evidence" agents/strategic/prompts/qwen3_6_27b/*.j2` + the meetings run | **0 on all six templates**; 1050 meetings tests pass, the byte-golden among them; `orchestrator/game.py:391` pins the set at `v4` and every committed replay stamps `qwen3_6_27b.v4` | VERIFIED |
| 20.32 (#373) | `uv run pytest tests/agents/test_impostor_policy.py -q` | *"109 passed in 24.29s"* — the declined-free-kill and ejected-stalking pins. The co-intervention is declared in the record (`audits/audit-phase-20-baseline-7.md` §9) and no honesty bar is attributed to it | VERIFIED |
| 20.33 (#384) | `uv run pytest tests/orchestrator/test_replay.py -q` + the bare-env snapshot | *"73 passed in 0.78s"*; `substrate_flag_snapshot({})` → **22 keys, 21 True, 1 False**, the single False being `impostor_roll_call` (§3.3) | VERIFIED |
| 20.34 (#385) | `uv run pytest tests/scripts/test_counterfactual_phase20.py -q` | *"5 passed in 0.28s"* — the committed OFF/ON table still reproduces. Its published prediction was **FINDING**, which is the verdict the record returned, by different reasoning (§3.1) | VERIFIED |
| 20.35 (#386) | `git status --porcelain replays/` + the §1 legs | **empty** — the smoke left the committed sets untouched; the smoke's own ABANDON→GO history is recorded in `audits/audit-phase-20-smoke.md` §14 and routed Task 20.43 | VERIFIED |
| 20.36 (#389) | `bash scripts/verify_samples.sh` + `validity_gate.py` × 4 + `verify_ml_evidence.py --complete` | 100/100 byte-clean in a **bare** environment; all four validity gates PASS; `--complete` exit 0 with reconstruction green. What the record executed is verified item by item in §3.3 | VERIFIED |
| 20.37 (#391) | the three retirement greps + `uv run pytest tests/meetings/test_lever_registry.py -q` | `def [a-z_]+_enabled\(` in `agents meetings orchestrator` → **2** (the live 18.10 pair, `loader.py:329` and `replay.py:117`); the seventeen retired `ENV_*` names in `tests/` → **0**; `accepted and ignored\|no longer read\|now always True` → **0**; the structural gate *"7 passed in 0.22s"* | VERIFIED |
| 20.38 (#390) | `uv run pytest tests/scripts/test_check_doc_facts.py -q` + `check_doc_facts.py` | *"178 passed in 44.60s"* including the stale-win-rate, dropped-featured-seed and unstamped-figure perturbations; the front-door check exits 0 | VERIFIED |
| 20.39 (#392) | `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` + `git ls-files docs/media` | *"64 passed in 75.73s"*; the `docs/media/` registry row equals the index at **6 files**, the still is 93,046 B (≤ 400 kB) and the clip 613,669 B (≤ 3 MB). The `.webm`-not-`.mp4` deviation was ratified at merge and is recorded in `docs/media/README.md` | VERIFIED |
| 20.40 (#393) | `uv run pytest tests/scripts/test_check_doc_facts.py -q` + `wc -w docs/lessons.md` | 178 passed — every relative link resolves, every mapped PR number resolves to a merge commit reachable from HEAD, and each perturbation fails naming the drifted row; the page is **1,491 words**, inside its 800–1,500 budget | VERIFIED |
| 20.41 (#394) | `uv run python scripts/verify_ml_evidence.py --complete` + `grep -n 'audit C-C-' docs/deployment.md` | *"verify-ml-evidence: every check passed."* with the slate row reading *"RECOVERED → EVIDENCE-BRANCH-RESTORED (1569/1569)"*; all **4** `C-C-` hits name their source audit file | VERIFIED |
| 20.43 (#387) | `uv run pytest tests/eval/test_evidence_honesty.py -q` + the counterfactual pins | *"95 passed in 39.31s"* and *"5 passed"* — the movement-sided sighting resolves and a duplicated flag counts once. The production-side duplicate mint was routed POST-record and **rides inside the recorded bytes**, which the record states rather than hides (`…baseline-7.md` §10.2) | VERIFIED |

**On the two deviations.** Both are F3 and both are the same shape: a word budget written into a
contract's Measurement field, **already exceeded at that contract's own merge** (README 2,034
against ≤ ~1,800, the reading guide 940 against ≤ ~900, the ML page 1,439 against ≤ ~1,400), and
exceeded further at close HEAD because four later contracts each added prose to the same pages.
Neither is silent, neither is softened into a pass, and neither is fixed here — the close verifies;
it does not edit the front door's content.

**Deviations already recorded at their own merges** are not re-litigated here; they live in
`tasks/phase-20.md` beside their contracts as orchestrator-ratified prose records (20.24, 20.25,
20.28, 20.29, 20.30, 20.31, 20.33, 20.34, 20.37, 20.39, 20.40). This close re-read each one and
found none that changes a verdict above.

---

## 3. The before/after story (generated numbers only)

Every baseline-6 figure below is the **20.22 instrument pin**, which is also the record audit's own
before column — never the review's raw session cell. Where the two disagree,
`audits/audit-phase-20-preregistration.md` §3.2 records the disagreement and its cause and the pin
is authoritative; the four moved cells are marked. Every baseline-7 figure is quoted from
`audits/audit-phase-20-baseline-7.md` §3 / §5. **Nothing in this section is recomputed by the
close.**

### 3.1 The pre-registered bars, read back

| bar | baseline 6 (the pin) | baseline 7 (recorded) | verdict per the rule |
|---|---|---|---|
| **1** — I-1 non-direct conviction accuracy ≥ 0.60 pooled | 46/125 = 0.3680 [0.2886, 0.4553] | **61/103 = 0.5922** [0.4957, 0.6822] | **MISSED** by 0.0078 — less than one ejection (62/103 = 0.6019 would have met it) |
| **2** — I-1 innocent ejections < 35 pooled | 79 (23 / 54 / 2 / 0) | **42** (14 / 26 / 1 / 1) | **MISSED** — a 47% fall, and not enough |
| **3** — I-2 false crew self-placement < 5% on samples/9p2i, every set < 8% | 152/723 = 21.0% *(re-pinned; review 148/723)*; pooled 587/2918 = 20.12% | **3/659 = 0.46%**; pooled **21/2722 = 0.77%** | **MET** on every clause, by more than an order of magnitude |
| **4** — I-3 sole-`alibi_vs_sighting` precision ≥ 50% + class share above base rate | 12/82 = 14.6% *(the kind-sole cell; class share 33/192 = 17.2% against a 255/1017 = 25.1% base rate)* | **0/0 (None)** — the class is empty on all four sets | **MISSED** (a bar whose cell is undefined is not met). The §6 class-closed waiver is separately **satisfied**: the denominator fell 82 → 0 |
| **5** — I-4 grounded sighting side, 100% at tick | 124/234 = 53.0% at tick *(re-pinned; review 36.5% over 170 sides)*, 154/234 = 65.8% within ±1 beside it | **0/0 (None)** — zero surviving STRONG sighting sides | **MET (vacuously)**, labelled **SUPPRESSED-NOT-FIXED** |
| **6** — I-5 fabricated completion lines, 0 on every set | 19/458 (samples/9p2i) and 15/61 (samples/4p1i) *(re-pinned; review 53/529 and 15/65)*; pooled 88/1888 = 4.66% | **0/308, 0/979, 0/38, 0/40** — pooled **0/1365** | **MET** on all four sets, with the population still an order of magnitude above the label floor |
| **7** — I-6 adjacent-room STRONG share ≤ 5% pooled | 148/234 = 63.2% (distance 2 / ≥3 / single-tick window: 71 / 15 / 187) | **0/0 (None)**; the adjacent COUNT fell **148 → 0**, the denominator 234 → 0 | **reported both ways; not decision-bearing** — §6 is conjunctive and bars 1 and 2 already decide it |
| **8** — the four I-13 injustice fixtures, ≥ 3 of 4 flip | 4/4 exhibit the injustice | **4 of 4 FLIPPED** | **MET** |

**The rule's output, and what it is not.** `audits/audit-phase-20-preregistration.md` §6: ADOPTED iff
bars 1, 2, 3, 5, 6 and 7 are met AND ≥ 3 fixtures flip AND bar 4 is met or its denominator has
fallen below 20. Bars 1 and 2 are missed, so **the verdict is FINDING**. That verdict was produced by
the record contract, is stated in its own §6, and is **not re-ruled, re-priced or re-read here.**

The direct-proof cell, for contrast, stayed perfect and grew: **326/326 = 1.000** pooled against
310/310 before. The 2026-08-24 counterfactual (`audits/audit-phase-20-counterfactual.md` §6)
predicted FINDING and named bars 5 and 7 as the expected misses; the verdict matches and the
reasoning does not — bars 5 and 7 emptied rather than missed, and bars 1 and 2, which that memo
declared NOT PREDICTABLE OFFLINE, are what decided it.

### 3.2 The RR-free rows — measurements that needed no record

| row | before | after | source |
|---|---|---|---|
| phantom body frames on the map (C-7) | **1,182 of 1,769 = 66.8%** of committed frames in 50/50 games | the shipped rule reads **0 of 1,217** on 9p2i and **0 of 601** on 4p1i; the negative control reads **668 of 1,217** (1,371 phantom bodies, 48/50 games) so the gate can still fail | `frontend/src/lib/bodies.test.ts`, re-run at close HEAD (§2). The frame denominators differ because the fixture was regenerated on the baseline-7 bytes; the control census is what proves the assertion is not vacuous |
| default test tier, wall clock (C-48) | **364.61 s serial**, 4,804 tests at `755fc487` (PR #368's own quiet-host measurement; the review's labelled reference is 337.96 s) | **89.75 s** with `-n auto --dist loadfile` on that same host and tree; this close's own reading at HEAD is **265.85 s for 5,304 tests** under sibling-worktree load (§5 states the load honestly) | PR #368's committed table + §1 |
| import-contract coverage (C-32) | `Analyzed 89 files, 379 dependencies`, `Contracts: 4 kept, 0 broken` — a planted `agents/_probe_orch.py` importing `orchestrator.game` passed all four | **`Analyzed 152 files, 794 dependencies.`**, `Contracts: 4 kept, 0 broken.`, with planted-route legs inside `tests/test_firewall.py` | §1, §2 (20.9) |
| the leak scanner's M6 (C-31) | mutation M6 — every undiscovered body visible to everyone — survived all four suites: **125 passed** with it planted (`body_views 33 → 249`) | M6, M1, M10 and a widened room rule are each planted and each **raises from the scanner**; the four suites read **154 passed** | PR #363's committed before-run + §2 (20.8) |
| memory render census | mean **51.1038** rows/snapshot over 1,956 snapshots; 18,319 testimony rows | mean **37.03** over 1,746 snapshots; **26,735** testimony rows | `…baseline-7.md` §5.4 — less budget per snapshot, more testimony inside it |
| dev markers in spoken text (I-8) | 53/971 turns (5.5%) and 246/1,956 prompts on samples/9p2i; pooled 192/3,934 and 917/7,932 | **0/3,602 turns and 0/7,211 prompts** — zero on both halves, all four sets | `…baseline-7.md` §5.3 |
| singular-persona prompts (I-9) | 1,956/1,956 violations on samples/9p2i (5,502/5,502 on the corpus) | **0/1,746 and 0/4,961**; both 4p1i sets stay NOT-APPLICABLE | `…baseline-7.md` §5.3 |
| solvability: ejections on an already-cleared player (I-12) | 83/354 = 23.4% *(the fourth re-pinned cell; review 61/354 = 17.2% under its own kill anchor)* | **68/379 = 17.9%**; containment 544/626 = 86.9% → **555/618 = 89.8%** | `…baseline-7.md` §5.2; the anchor difference is `…preregistration.md` §3.2 |
| win split (secondary, never gated) | 30% / 25.3% / 34% / 22% impostor | **24% / 24% / 36% / 26%** — every leg inside the pre-registered ±15-point band | `…baseline-7.md` §5.1. Un-attributable by construction: the mover repair rides the same record (§9's declared co-intervention) |
| evidence completeness | 54 checks, 0 FAIL, 0 ABSENT (phase-19 close) | **55 checks, 0 FAIL, 11 STALE, 0 ABSENT** — the eleven naming the declared ML-grounding gap | §1 |

### 3.3 Both halves of the recorded outcome, verified present in the tree

The close owns only half the ledger. The record's ruling is the record contract's, and the recorded
answer is **neither branch alone**. What this close verified — by running commands, not by reading
prose:

**The verdict, as recorded.** The pre-registered rule returned **FINDING**: bars 1 and 2 are MISSED
(§3.1) and nothing anywhere re-prices them. **Separately**, on **2026-08-26** and by explicit
prerogative, the owner **ADOPTED the baseline-7 substrate as canon over that verdict**
(`audits/audit-phase-20-baseline-7.md` §6.1, the ruling recorded on PR #389 with its five grounds,
each traceable to a §3 or §5 cell). This close **neither re-ruled the verdict nor re-priced a
cell**, and states so here in its own words.

**What §6.2 executed, checked item by item at close HEAD:**

| §6.2 item | how it was checked | result |
|---|---|---|
| the eight levers unconditional | `grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator` | **2** resolvers survive, both the live 18.10 pair (`agents/strategic/prompts/loader.py:329`, `orchestrator/replay.py:117`). The eight hard-returned `True` at 20.36 and 20.37 then **deleted the husks**, per the Graduation-sweeps rule — the stronger form of the same state |
| the eight keys retired | read `orchestrator/replay.py:524-546` | all eight (`task_completion_from_events`, `self_location_trail`, `movement_claim_shape`, `grounded_prosecution`, `map_aware_arbitration`, `structured_turn_markers`, `meeting_outcome_memory`, `coalesced_memory_render`) sit in `_RETIRED_ALWAYS_ON_LEVERS`; `_TOGGLEABLE_LEVER_RESOLVERS` holds exactly one entry |
| twenty-one keys stamped True in a bare environment | `substrate_flag_snapshot({})` | **22 keys, 21 True, 1 False** — the single False is `impostor_roll_call`, the sole live toggle, recorded OFF |
| the invariant that graduation exists to protect | `env -i … bash scripts/verify_samples.sh` | **100/100 byte-clean with zero `AILIBI_*` exports** — the reconstruction a FINDING-branch substrate could not have produced (`…baseline-7.md` §10.1: 182 `ReplaySubstrateMismatchError` occurrences no re-pin reaches) |
| `_DEFAULT_BASELINE_ID` at `baseline-7` | import `eval.watchability` | `baseline-7`; `_BASELINE_SUPPLY_FLOORS` carries blocks `baseline-2 … baseline-7` |
| the v3 prompt archive retired | read `ARCHIVED_PROMPT_VERSION_SETS`; stat the fixture dir; grep the committed stamps | `ARCHIVED_PROMPT_VERSION_SETS = {}`; `tests/fixtures/prompt_archive/` **does not exist**; every committed replay stamps `qwen3_6_27b.v4` and `orchestrator/game.py:391` pins the set at v4. (The stale comment that still describes the archive is F2) |
| the ladder tip | `uv run python scripts/check_doc_facts.py` | green, and it names *"the 22-lever substrate registry"* — the front door, `.env.example`, the glossary, the history page and the reading guide all name baseline 7 and are checked against the record audit's own sentence |

**§6.1's "what no surface may say", swept across the tree.** The constraint: *no document, comment,
docstring, README row or commit message in this repository may state or imply that the pre-registered
bars passed, that the verdict was ADOPTED under the rule, or that baseline 7 was adopted on the
arithmetic.* The sweep (§7 lists it) walked every tracked file naming baseline 7, every occurrence of
"adopted"/"ADOPTED", every phrasing of "bars passed / met the bars / passed the bar", and the phase's
own commit subjects and bodies. **It holds.** Every surface that carries the adoption carries the
FINDING beside it, in that order:

* `README.md:150` — *"Under the rule as written that is a **finding, not an adoption**. I then adopted this recording as the reference anyway, by an explicit owner override of that verdict … The bars did not pass; the miss stays on this page."*
* `docs/architecture.md:162` — *"returned **FINDING** and the owner adopted it anyway, by explicit override; §6.1"*
* `docs/history.md:188-190` — *"returned **FINDING**, not adoption: two of its bars missed"* … *"stated grounds — not because the bars passed"*
* `.env.example:110-111` — the graduated slate is named *"at the baseline-7 record, adopted by owner override of a FINDING verdict"*
* `orchestrator/replay.py:521-523` and `replays/ml_corpus/README.md:13-16` — the same sentence in the source and in the corpus's own provenance
* `eval/vote_correctness.py:31` — *"record missed two of its own pre-registered bars -- the rule's verdict is FINDING"*

No surface was found stating or implying a pass. The only occurrences of "ADOPTED" as a verdict word
sit inside the pre-registration's own rule statement and the contracts that quote it, where it names
the branch **not** taken by the arithmetic.

**The sweep did find one wrong surface, in the other direction.** A repo-wide
`git grep -nI -i "ladder tip"` — a check the four gated documents pass but which nothing runs
outside them — found `audits/README.md` still describing the branch the arithmetic selected as the
branch executed, and stating the tip at baseline 6. That is F4: corrected in this PR because the
index gate had already forced the file open, with the gate-coverage gap routed. It is worth naming
plainly: the constraint §6.1 wrote is honoured everywhere it was checked *by a gate*, and the one
place it slipped is the one place no gate looked.

### 3.4 The review's findings → outcomes

171 findings were published. **40 carry a closed-by row** in the curated index's §3 map
(`audits/review-2026-08-19/README.md`), which is one row per finding closed — the map's own rule
since 20.40, enforced in the default tier by `scripts/check_doc_facts.py::check_review_map` and
proved green in §1. This close **adds no row**: 20.42 and 20.43 close no review finding, and inventing
one would fail that gate.

**Those 40 acted-on ids partition exactly**, 24 + 14 + 2, across the first three rows below — no id
appears twice and none is missing. The last two rows are **not** part of that partition and are not
counted into it: they describe what happened to findings the phase did **not** act on, and two ids
appear in them as *facets* rather than as whole findings, which is stated rather than glossed —
`G-1`'s 73.4% headline was retracted while the finding's substance ("nothing in memory said where
the agent itself had been") is what 20.24 closed, and `C-33`'s load-bearing risk was refuted while
its duplication remains a maintenance item on the backlog. Those are the only two ids whose facets
land in different rows.

| outcome | count | the findings |
|---|---|---|
| **fixed** (RR-free repair, merged and re-verified) | 24 | `C-1`, `C-3`, `C-4`, `C-5`, `C-6`, `C-7`, `C-8`, `C-9`, `C-31`, `C-32`, `C-34`, `C-35`, `C-42`, `C-43`, `C-48`, `C-64`, `C-74`, `C-96`, `C-104`, `C-113`, `C-125`, `G-12`, `G-38`, `G-41` |
| **lever-ON-and-graduated** (shipped default-OFF, measured, adopted at the record) | 14 | `C-2`/`G-3` (20.23), `G-1` (20.24), `G-9` (20.25), `C-11`/`G-2` (20.26), `C-67`/`G-25` (20.28), `G-35` (20.29), `C-73`/`G-34` (20.30), `C-129`/`G-23`/`G-27` (20.31) |
| **recorded-as-finding** (answered by disclosure, not by change) | 2 | `G-37` — the +1 agent clock is *labelled* on the spectator surface, because changing it would move every recorded tick stamp; `C-88` — the degenerate fake-provider meeting is *disclosed* on the front door, with a real report handed to the reader instead |
| *not acted on —* **retracted by the review's own verifier** | 5 claims | `G-1`'s 73.4% headline, `G-6`, `G-7`'s headline, `G-4`'s vent half, `C-33`'s load-bearing risk (§1 of the index) |
| *not acted on —* **triaged backlog** | the rest of the 171 | the balance wave's seven (§4), six begun-not-finished (`C-79`, `C-80`, `C-101`, `C-107`, `C-126`, `G-29`), five named-but-deliberately-not-closed (`C-46`, `C-83`, `C-130`, `C-36`, `C-72`), two decomposition refusals (`C-62`, and `C-33`'s duplication), the history rewrite (`C-45`), and **roughly 94 P2 code findings** plus the text-hygiene remainder (`G-26`, `G-36`, `G-29` beyond the prompt change) and the walker flag matrix (`C-37`) |

The backlog is named as a backlog with its size, which is the synthesis's own instruction: *"A
triaged backlog reads better than a half-done sweep."* Nothing was built for a claim its own
verifier withdrew.

Two items the orchestrator routed to this ledger mid-phase, recorded here so neither becomes a
silent debt:

* **`eval/replay_walk.py` performs no substrate check.** `compute_pooling_funnel` and the VJ instruments would reconstruct always-on rules over earlier-substrate bytes without noticing. The one-line fix is the now-public `orchestrator.replay.retired_levers_stamped_off`. Routed with 20.37's merge record (`a9952d29`); a next-phase item, not a close edit.
* **No standing gate asserts that a DEFAULT 1440×900 arrival shows the whole map.** `frontend/e2e/journey.spec.ts` pins 1280×800 and 1000×640 only, and the dock covered the map until the Timeline drawer collapsed. Routed with 20.39's merge record (`69255980`).

The published index's §4 also records **five verified-open items** by name — `C-46` (the tournament
loop still runs strictly serially, cited beside the test tier that did go parallel), `C-83`
(import-time side effects in the prompt loader, deliberately not addressed because removing the
import-time build changes what a stray prompt-set export does to every replay-only consumer),
`C-126` (the operator environment surface is still undocumented past the one variable the front door
prints), `C-130` (dead prompt-set weight and a default set no committed replay uses) and `G-29`'s
stock-rationale half. Each is open at its own scope, in writing, on a published page.

Two owner-facing items are likewise open by design rather than by omission: `docs/lessons.md` is a
first-person **draft for the owner to edit** (owner markers in place, 1,491 words), and the
authorship statement's wording on the front door awaits the same confirmation. Neither blocks the
close; both are wording the owner owns.

---

## 4. The routed next decision — the balance wave (the owner's)

**The recommendation, first: charter the balance wave as its own phase, with its own recording, and
do not let any of its levers ride a presentation or hygiene phase.** The reason is attribution, and
it is the same argument the synthesis made and this phase just spent 23 h 25 m of operator wall
clock validating: shipping a balance lever alongside anything else destroys the one measured delta
you paid for. This phase kept exactly one co-intervention (20.32's mover repair), declared it in the
pre-registration, and consequently could not attribute a single honesty bar to the win split — a
cost it paid deliberately and states in `…baseline-7.md` §9. Six levers at once would make the whole
recording unreadable.

The six excluded levers, with the review's own measured evidence (`audits/review-2026-08-19/A/collated-findings.md`):

| lever | the measured evidence | size |
|---|---|---|
| **post-meeting position and cooldown reset** (`G-5`, P0, corrob 12) | All living agents in CAFETERIA in 0/39, 0/165, 0/40 and 3/463 meetings; mean fraction present 0.27 and *lower* the tick after. **89 reporters killed within 3 ticks of their own meeting**; 31 kills land the tick after a meeting; **69 of 707 meetings carry a participant speaking from inside a vent** | large |
| **finished-crew jobs** (`G-15`, P1, corrob 12) | **48.6% / 45.9% of 9p2i ticks** and 61.4% / 59.8% of 4p1i ticks contain no kill, report, vent, task-completion, meeting or sabotage; one crewmate stands still for **36 consecutive ticks** (samples/9p2i seed 32, t20–t55) while its three teammates are murdered | large |
| **the vent peek** (`G-13`, P1, corrob 8) | Vent EXIT seen by a crewmate **56.5%** (samples/9p2i) / 59.2% (corpus) against ENTER at 8.8% / 6.4%; **310/435 ejections (71%) ride `vent_sighting`** — the channel the crew wins on is a blind exit | medium |
| **a speakable witnessed kill** (`G-8`, P0, corrob 5) | The turn schema has no kill shape and the contradiction vocabulary no kill kind, so "I watched them do it" reaches peers as a **+0.08 belief nudge**; `You witnessed pN kill in ROOM.` is **0.02% of all rendered memory lines** | medium |
| **a symmetric roll-call** (`G-22`, P1, corrob 6) | Crew turns carrying a `whereabouts` 99.6–100%, impostor turns 12.5–50.0%, so **P(impostor \| turn has no whereabouts) = 97.7–100%**; body reports by an impostor **0/626**, meeting triggers **0/707** — `impostor_report.qwen3_6_27b.v3` was a version-bumped template with **0 calls out of 7,932** over the baseline-6 bytes (the set is at **v4** since 20.31 — `orchestrator/game.py:391` — so this cell is historical, not a live measurement) | medium |
| **sabotage as a real clock** (`G-40`, P2, corrob 5) | **32 sabotages set-wide, none ever times out**; **0 sabotage actions in 50 4p1i games**; 8 corpus kills within 4 ticks of a sabotage. Agents also speak of "when the lights went out" in games with no lights sabotage | small |

The synthesis's list carries a seventh: **a second act for the 4p1i roster** (`G-43`), where 61.4% of
ticks are empty and both sets carry zero testimony rows in the render census.

**The cost of a second record, priced against what this one actually took**
(`…baseline-7.md` §0.3, §9): **23 h 25 m 42 s** of operator wall clock across two parallel seed
workers, **$0.0000** on every row at the flat-rate provider, 300 games over four sets, two re-records
with cause, zero absorbed transport retries. A balance wave would need the same again, plus its own
pre-registration (bars written before the levers exist), its own offline counterfactual where one is
possible, and a smoke record first — this phase's smoke returned ABANDON before it returned GO, which
is the whole reason it exists.

**What the close does *not* do.** It makes no ruling. Per the 15.18 convention the owner's merge of
this document ratifies the close reading; for this menu the merge ratifies the recommended route —
the balance wave as the next chartered phase's candidate — **unless the owner records a different
ruling on the PR before merging**, and any post-merge change lands here as a dated erratum rather
than an in-place rewrite. The ruling charters nothing by itself: the next phase opens only when its
own `tasks/phase-N.md` is authored and ratified.

**Two decisions that do not ride this one.** The **ML re-ground** (`…baseline-7.md` §10.2) is its own
owner decision on the ML program's cadence and is now also the destination for this close's F1 (§1).
The **live-API deployment** stays refused; the static bundle is the sanctioned path and the Pages
deploy is green (§1).

---

## 5. Decisions

- **The close verifies; it does not fix.** F1 (the red campaign tier), F2 (two stale narrations), F3 (the word budgets) and F5 (the carried staging ref) are recorded and routed; the *gate-coverage* half of F4 is routed too. No test, script, production package or front-door page outside this contract's files was touched, with the mechanical exceptions below — each forced by a fail-loud check that the close's own mandated artifact trips.
- **`audits/README.md` gains the close-audit entry, and its stale ladder-tip clause is corrected.** `scripts/check_doc_facts.py::check_audits_index` fails the DEFAULT tier on any top-level `audits/*.md` the index does not link exactly once, so landing this file forces the entry; the file is not in the contract's files-in-scope list and this is reported as a blocking coordination item rather than absorbed. Having been forced open, the same paragraph's false *"the ladder tip stands at baseline 6"* is corrected in place (F4) — two clauses, no other content. The owner's merge ratifies the amended scope, the 15.18 convention and the 19.28 precedent for close-recorded surgery notes.
- **`docs/artifacts.md`'s `audits/` registry row, 154 → 155.** Landing this file — in scope and mandated — trips the in-tree family inventory check in the DEFAULT tier (`scripts/verify_ml_evidence.py:2359-2390` compares the document's stated count against `git ls-files audits`, and `tests/scripts/test_verify_ml_evidence.py:1624` runs it unmarked). The contract lists `docs/artifacts.md` in **both** its files-in-scope list (*"the audits/ registry row count only"*) and, from an earlier authoring pass, in its files-NOT-in-scope list as a blocking coordination item. The in-scope entry and the Definition-of-done item (*"docs/artifacts.md's audits/ row count equals the git index at close HEAD"*) resolve the contradiction, and the prior close carried exactly this bump for exactly this reason. The count is re-derived from the index, not incremented by hand; the size figure is unchanged at its own precision.
- **`README.md`'s phase-20 table row, "In progress" → the close audit.** The Definition of done requires that *"a reader who opens either surface after the merge cannot conclude the phase is still under way"*, and the row sits inside the `## Project status` section the contract scopes. Leaving it would have contradicted the sentence two lines above it. One cell, one link; no other README content moves.
- **The gate's two states are both quoted, and nothing is averaged.** The default tier is green in the clean state AND in the restored state — that is the finding, and it is the point of running the pair. The campaign tier and `--complete` ran in the restored state, `verify_samples.sh` in a bare environment (`env -i`), and every row in §1 names its state.
- **The campaign tier is recorded as RED rather than re-run until green.** Re-running it serially or after a `--clean` would not change any of the nine assertions: three compare against a live composite the graduation moved and five against a corpus the record replaced. Diagnosing them by class and routing them is the honest disposition; hiding a red tier behind a state selector is not.
- **Timing honesty.** This close's own gate runs shared a 10-core machine with fifteen sibling agent worktrees. The correctness legs are load-independent and are quoted as measured; the *runtime* story in §3.2 rests on PR #368's quiet-host measurement (364.61 s serial → 89.75 s parallel at `755fc487`), with this close's own 265.85 s reading stated beside it and labelled as loaded rather than presented as the parallel tier's true wall clock.
- **The before/after table quotes; it never recomputes.** Every baseline-6 cell is the 20.22 instrument pin (the four cells where the pin and the review disagree are marked, with the pre-registration's §3.2 owning the cause); every baseline-7 cell is read from the record audit's §3 / §5. A close-session recomputation with new definitions is exactly how a pre-registered read gets quietly re-priced.
- **The review map gains no row.** 20.42 and 20.43 close no review finding, and `check_review_map` fails a row invented for a task that closed none. The map's completeness was proved by running the gate, not by reading the table.
- **No tag is minted.** Nothing this close produced needs byte-level provenance beyond git; the provenance point is this PR's merge commit. The honest precedent stands that neither `phase-17-close`, `phase-18-close` nor `phase-19-close` was ever minted (§6).
- **The frontier's `gh` leg was not needed.** The `compute_frontier` cross-check ran against a git-log title index **pinned to close HEAD** (§6, §7), which is the method both prior closes used and which keeps the snippet reproducible after this close merges.

---

## 6. Provenance + the frontier

- **Close HEAD:** `937bd805` — *"coordination: re-anchor 20.42 — the close verifies BOTH halves of the recorded outcome …"*, 2026-08-26, sitting on the 20.41 merge `3e0327bc` (PR #394). `origin/main` and the close branch agree; the working tree was clean apart from the by-design untracked evidence restore, which was `--clean`ed and never staged.
- **The phase's chain:** the planning commit `4a7bd9c0` (*"audit and setup phase 20"*, 2026-08-19, pushed direct to `main` per the planning convention) plus **87 commits** after it: **44 task merges** (42 dispatched contracts + the 20.14 and 20.21 follow-ups, PRs **#351–#394**) and **43 coordination commits** (pre-dispatch re-anchors, merge-reality records and rulings). `git rev-list --count 4a7bd9c0..937bd805` = 87.
- **The window:** 2026-08-19 → 2026-08-26, eight days, with the 23 h 25 m recording session inside it on 2026-08-25.
- **The frontier computes complete on this close's merge.** With the merged `task 20*` titles from a log pinned to close HEAD (44 titles), `compute_frontier` reads **AT HEAD: dispatchable `['20.42']`, blocked `[]`, merged 42**; **WITH 20.42 MERGED: dispatchable `[]`, blocked `[]`, merged 43.** `parse_all_tasks` returned zero errors.
- **The evidence pin:** `476a1f85492439277350af9708f1d120eb1c0a71` (the one orphan commit on `evidence/phase-18-coevo`), fetched by sha and verified at this close (2953/2953, §1). The 19.21 raw-slate ruling stands **RECOVERED**, and `--complete` reads its row as *"RECOVERED → EVIDENCE-BRANCH-RESTORED (1569/1569)"*.
- **Remote refs observed** (read-only queries): tags `attempt-1-phase-10-wave1-rerecord`, `phase-16-baseline-4` → `a43b178`, `phase-16-baseline-5` → `2428044`, `phase-18-corpus-8f5f434` → `8f5f434` — no `phase-19-*` or `phase-20-*` tag exists and none is required; branches `evidence/phase-18-coevo` → `476a1f85` and `evidence/raw-slate-staging` → `c27ab7b5`, the latter being F4.
- **The banner and the front door record the close in this PR:** `tasks/phase-20.md`'s STATUS line → CLOSED, and README's `## Project status` sentences and phase row → the close, its date, its outcome and this audit's path. The PR also carries the one-token `docs/artifacts.md` registry bump (§5).

---

## 7. Method + reproduction (all $0 against committed bytes; network only where named)

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
bash scripts/fetch_evidence.sh                              # 2. OK: 2953/2953 files match 476a1f85…
uv run pytest -m campaign                                   # 3. RESTORED — F1: 9 failed, 308 passed
uv run python scripts/verify_ml_evidence.py --complete      # 4. RESTORED — 55 | OK 39 | FAIL 0 | STALE 11 | ABSENT 0 | INFO 5
bash scripts/check.sh                                       # 5. THE PAIRING — same gate, RESTORED state (20.17)
env -i PATH="$PATH" HOME="$HOME" bash scripts/verify_samples.sh   # 6. 100/100, zero AILIBI_* exports
uv run python scripts/check_doc_facts.py                    # 7. front-door facts green
bash scripts/fetch_evidence.sh --clean                      # 8. removes the 2,952 restored files

# §2 — the per-contract ledger, one fresh command per contract
(cd frontend && npx vitest run)                             # 20.1, 20.2, 20.3
uv run pytest tests/api/test_replay_loader.py -q            # 20.4
uv run pytest tests/agents/test_prompt_loader.py -q         # 20.5
uv run pytest tests/eval/test_vote_correctness.py -q        # 20.6
uv run pytest tests/scripts/test_build_demo_bundle.py -q    # 20.7
uv run pytest eval/leak_test.py tests/observation tests/test_firewall.py tests/training/test_leak_gate.py -q   # 20.8
for s in replays/samples/9p2i replays/ml_corpus/9p2i replays/samples/4p1i replays/ml_corpus/4p1i; do
  uv run python scripts/validity_gate.py "$s"; done         # 20.10, 20.36
uv run pytest tests/engine/test_rules.py -q                 # 20.11
uv run python scripts/paired_stats.py training/reports/results-finalist-eval.jsonl   # 20.13
uv run pytest tests/eval/test_solvability.py -q             # 20.14
uv run pytest tests/eval/test_evidence_honesty.py -q        # 20.15, 20.43
uv run pytest tests/api/test_view_model.py tests/api/test_sets.py -q                 # 20.16
uv run pytest tests/scripts/test_refresh_samples.py -q      # 20.21
uv run pytest -q -k "evidence_honesty or solvability or deduction_metrics"           # 20.22
uv run pytest tests/agents -q                               # 20.23, 20.24, 20.29, 20.30
uv run pytest tests/meetings -q                             # 20.25, 20.27, 20.28, 20.31
uv run pytest tests/api/test_evidence_mechanisms.py -q      # 20.26
uv run pytest tests/agents/test_impostor_policy.py -q       # 20.32
uv run pytest tests/orchestrator/test_replay.py -q          # 20.33
uv run pytest tests/scripts/test_counterfactual_phase20.py -q                        # 20.34
uv run pytest tests/meetings/test_lever_registry.py -q      # 20.37
uv run pytest tests/scripts/test_check_doc_facts.py -q      # 20.38, 20.40
uv run pytest tests/scripts/test_verify_ml_evidence.py -q   # 20.39, 20.41
git status --porcelain replays/                             # 20.35 — empty
wc -w README.md docs/reading-guide.md docs/ml-program.md docs/lessons.md            # 20.12, 20.13, 20.40 (F3)
grep -c "VERIFIED evidence" agents/strategic/prompts/qwen3_6_27b/*.j2               # 20.31 — 0 on all six
grep -rn 'fetch(' frontend/src --include='*.tsx' --include='*.ts' \
  | grep -v src/api/client | grep -v '\.test\.' | wc -l                             # 20.16 — 0
grep -n 'audit C-C-' docs/deployment.md | wc -l                                     # 20.41 — 4
git ls-files docs/media | wc -l ; ls -l docs/media                                  # 20.39 — 6 files
python3 -c "import xml.etree.ElementTree as E;E.parse('docs/media/architecture.svg')" ; wc -c docs/media/architecture.svg   # 20.20

# §2 (20.37) — the three retirement greps
grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator | wc -l              # 2
grep -rnE 'ENV_(ROLL_CALL_ROUND|WHEREABOUTS_INTERIOR_FLAGS|VENT_PLACEMENT_CONTRADICTIONS|ABSENCE_PRIOR|CITATION_GATE|HARD_EVIDENCE_GATE|OBSERVATION_ID_RENDERING|EVIDENCE_QUALITY_LIFT|REPORTER_EXCULPATION|TASK_COMPLETION_FROM_EVENTS|SELF_LOCATION_TRAIL|MEETING_OUTCOME_MEMORY|COALESCED_MEMORY_RENDER|MOVEMENT_CLAIM_SHAPE|GROUNDED_PROSECUTION|MAP_AWARE_ARBITRATION|STRUCTURED_TURN_MARKERS)' tests/ | wc -l   # 0
grep -rnE "accepted and ignored|no longer read|now always True" --include="*.py" agents meetings orchestrator | wc -l       # 0

# §3.3 — what §6.2 executed, read out of the tree
uv run python -c "
from orchestrator.replay import substrate_flag_snapshot, SUBSTRATE_FLAG_KEYS
s = substrate_flag_snapshot({})
print('keys', len(SUBSTRATE_FLAG_KEYS), '| True', sum(s.values()),
      '| False keys', [k for k, v in s.items() if not v])"
uv run python -c "
from eval.watchability import _BASELINE_SUPPLY_FLOORS, _DEFAULT_BASELINE_ID
print(_DEFAULT_BASELINE_ID, sorted(_BASELINE_SUPPLY_FLOORS))"
grep -n 'ARCHIVED_PROMPT_VERSION_SETS: Mapping' tests/meetings/test_prompt_byte_golden.py
ls tests/fixtures/prompt_archive 2>&1                       # No such file or directory

# §3.3 — §6.1's "what no surface may say", swept
git grep -lI -iE 'baseline[- ]7' -- .
git grep -nI -iE 'ADOPTED' -- .
git grep -nI -iE '(bars? (were )?(passed|met)|passed the bars?|met the bars?)' -- .
git log 937bd805 --format='%h %s%n%b' -60 | grep -inE 'adopt'

# §3.3, F4 — the ladder-tip claim, swept everywhere rather than in the four gated documents
git grep -nI -i "ladder tip" -- .

# §6 — remote observation (read-only)
git ls-remote --tags origin ; git ls-remote origin 'evidence/*'
gh run list --workflow=pages.yml --limit 5                  # §1 Pages deploy on the close HEAD
```

```python
# §6 — the phase-complete frontier, cross-checked against a git-log title index PINNED to
# close HEAD, so the snippet still reproduces after this close merges (an unbounded log
# would already carry 20.42's own merge title and collapse the before/after).
import subprocess, sys; sys.path.insert(0, "scripts")
import compute_next_task as cnt
from _task_parser import parse_all_tasks
titles = [t for t in subprocess.run(
    ["git", "log", "937bd805", "--format=%s", "--grep=^task 20"],
    capture_output=True, text=True, check=True).stdout.splitlines()
    if t.lower().startswith("task 20")]
errors: list[str] = []; tasks = parse_all_tasks(errors); assert not errors
print(cnt.compute_frontier(tasks, set(), titles, 20))                 # dispatchable ['20.42'], merged 42
print(cnt.compute_frontier(tasks, set(), titles + [
    "task 20.42: the phase close (owner)"], 20))                      # dispatchable [], merged 43
```

The word counts of §3.2 and F3 were traced across merges with
`git show <sha>:README.md | wc -w` at `d86f979c`, `dc9d73b7`, `3ff2a82b`, `51844177` and
`3e0327bc`; the two committed measurement tables §3.2 quotes are read from PR #363 and PR #368.
