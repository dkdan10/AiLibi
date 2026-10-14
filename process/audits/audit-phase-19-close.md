# Phase-19 close — CLOSED: review-and-refresh complete, the 27 dispatched contracts merged and re-verified at HEAD (the close itself is the 28th); nothing recorded, the ladder tip stands at baseline 6; the post-19 decision routed to the owner (Task 19.28)

**Date:** 2026-08-18.
**Task:** 19.28 — the phase close (owner). Phase 19 was REVIEW-AND-REFRESH by owner charter
(`tasks/post-phase-14-plan.md`; the ratified plan `audits/audit-phase-19-planning.md`): a deep
review of the code that exists plus an updated presentation of the frontend and the data
displays — NOT a feature phase. **No recordings, anywhere**: every task ran $0/offline, replay
bytes never moved, and the ladder tip STANDS at **baseline 6** (the 18.12 adopting record) exactly
where the charter left it. This close therefore performs no evidence assembly — it **re-verifies
and routes**: the whole gate re-run at close HEAD by the verifiers' actual paths (§1), every
contract's headline DoD re-verified with fresh commands (§2 — merge equals done, but the close
re-runs; the phase-18 precedent found real defects in otherwise-green merges, and so did this
one: F1), the before/after story in generated numbers (§3), and the routed post-19 decision —
the evidence-honesty substrate phase vs the presentation phase — put to the owner with the
committed 19.14 proof-vs-inference cells as the evidence and a costed recommendation (§4, locked
decision 6).
**Close HEAD:** `7be97c7` (= `origin/main` tip at the close session; the 19.27 merge, PR #349).
The clone was unshallowed before any history-derived claim (the AGENTS.md rule; a `git fetch
--unshallow` preceded every count below).
**Grounding:** every number below is a fold over committed artifacts via the committed CLIs at
close HEAD, with runnable commands in §7. Everything ran $0, deterministic, under a bare
environment (zero `AILIBI_*` exports). Network was touched only by the named tooling legs: the
evidence fetch by pinned sha (`scripts/fetch_evidence.sh`, §1), the read-only
`git ls-remote --tags origin` query (§6), and one read-only GitHub API read of PR #349's body for
its committed runtime table (§3) — "offline" binds the evidence, not the toolchain (the phase's
standing designer ruling).

**Verdict in one line:** Phase 19 **CLOSES COMPLETE** — 27/27 dispatched contracts merged
(2026-08-03 → 2026-08-18, 33 commits: 27 task merges + 6 coordination anchor-refreshes) and
re-verified at close HEAD with every deviation recorded in the ledger (§2, none silent); the
whole gate is green at close HEAD (§1) with **one real close-found defect** recorded and routed,
not fixed (F1: the default pytest gate and the restored-evidence state are mutually exclusive —
found exactly the way the phase-18 precedent predicted); nothing was recorded, so no baseline
moved and no canary was judged; and the post-19 menu goes to the owner with **Option A — the
evidence-honesty substrate phase — recommended**, argued from the committed 19.14 cells: with
ejectee-specific proof present, conviction accuracy is **1.000 on every committed set (310/310
pooled)**; without it, accuracy is **0.303 (samples 9p2i) / 0.393 (corpus 9p2i)** and **100% of
innocent ejections (79/79 pooled) live in that non-direct cell** (§4).

---

## 1. The gate rerun at close HEAD (the WHOLE gate, the verifiers' actual paths)

The 19.27 tiering made `bash scripts/check.sh` the DEFAULT gate; the close runs BOTH tiers plus
the evidence and byte-identity verifiers, per the contract, by their actual invocation paths.
All legs at close HEAD `7be97c7`, bare environment:

| leg | invocation | result (quoted) | wall |
|---|---|---|---|
| default gate | `bash scripts/check.sh` | GREEN on the clean-state rerun (the state F1 defines; the first run found F1, below): ruff *"All checks passed!"*; format *"383 files already formatted"*; `lint-imports` *"Contracts: 4 kept, 0 broken"* (89 files, 379 dependencies); *"Task docs validation passed: 321 tasks and 321 prompts"*; *"All 321 prompts are in sync"*; mypy *"Success: no issues found in 354 source files"*; pytest **4,621 passed, 20 skipped, 317 deselected, 3 xfailed**; frontend lint + `tsc:check` + vitest + build green | 13m34s quiet (pytest leg 782.95 s = 13:02) |
| campaign tier (19.27 opt-in) | `uv run pytest -m campaign` | **"317 passed, 4644 deselected in 314.93s (0:05:14)"** — green, run WITH the evidence bytes restored (no campaign family couples to the restore) | 5m17s |
| evidence restore | `bash scripts/fetch_evidence.sh` | *"OK: 2953/2953 files match 476a1f85492439277350af9708f1d120eb1c0a71."* — the by-sha fetch, restore, and manifest verification of both class-(c) payloads (coevo 1,383 files + finalist raw slate 1,569 files + the branch README) | 11s |
| evidence completeness | `uv run python scripts/verify_ml_evidence.py --complete` | *"checks: 54 \| OK 49 \| FAIL 0 \| ABSENT 0 \| INFO 5"* / *"verify-ml-evidence: every check passed."* — every archived hash verified once (sidecars 59/59 in-tree + 260/260 evidence-branch over 476 targets; payload 2952/2952; corpus reconstruction 300/300 across all four sets; every recompute cell identical to its committed record). The contract's manifest-recorded-LOST acceptance arm is MOOT at this close: the 19.21 ruling is **RECOVERED** (2026-08-15), so there is no LOST class to accept — `--complete` verified every promised byte instead | 1m13s |
| byte identity | `bash scripts/verify_samples.sh` | *"All 50 samples verified clean."* (4p1i) / *"All 50 samples verified clean."* (9p2i) — the bare no-argument form, zero `AILIBI_*` exports. The corpus sets' reconstruction is covered in the same session by `--complete`'s corpus rows (150/150 + 50/50), so the explicit per-set arms were not duplicated (§5) | 7s |
| front-door truth | `uv run python scripts/check_doc_facts.py` | *"Doc facts verified: README.md and .env.example agree with 2 sample manifests, audits/audit-phase-18-close.md, and the 14-lever substrate registry."* — exit 0 | 2s |

**F1 — the close-found defect (recorded, not fixed; the close verifies).** The FIRST
`bash scripts/check.sh` run at close HEAD exited 1: **1 failed, 4620 passed, 20 skipped, 317
deselected, 3 xfailed in 815.10s** —
`tests/scripts/test_verify_ml_evidence.py::test_complete_accepts_a_manifestless_recorded_loss_end_to_end`.
Root cause, reproduced and confirmed by toggling exactly one variable: the test's scratch tree
symlinks the REAL checkout's `training/artifacts/coevo/` wholesale
(`tests/scripts/test_verify_ml_evidence.py:141`) and asserts the `coevo/ [(c)]` availability row
fails `--complete` as un-restored — its own comment assumes the checkout has "no restored coevo
bytes". This close had just performed the contract-mandated
`bash scripts/fetch_evidence.sh` restore, so the scratch tree saw the restored payload through
the symlink, the row read EVIDENCE-BRANCH-RESTORED instead of ABSENT, and the exact-three-rows
assertion failed. After `bash scripts/fetch_evidence.sh --clean` (*"Removed 2952 restored
file(s). Tracked bytes are untouched."*) the same test passes and the full default gate is green
(the table row above). **The close then found the same defect's second facet on a later rerun
with the evidence restored: `uv run mypy .` fails too** — mypy, unlike ruff, has no gitignore
awareness, so it walks the restored slate's untracked helper scripts
(`training/reports/_finalist_eval_raw/score-arm.py`, `assemble-row.py`, `make-owner-brief.py`)
and reports *"Found 15 errors in 3 files (checked 358 source files)"* against the clean state's
*"354 source files"* — the operator-machine slate scripts were never held to the repo's strict
bar and the restore's `.gitignore` fence stops `git add`, not `mypy .`. **The defect is real and
is exactly the class the close re-run exists to catch: the default gate and the documented
restored-evidence state are mutually exclusive, at two legs (mypy and the scratch-tree pytest
case)** — a developer who runs the documented restore and then the documented gate gets a
spurious red. It is an isolation defect (the gate's walkers inherit untracked state the restore
put there by design), not an evidence defect: every evidence check itself passed in both
states. Routed to the next phase's inputs as a review item; nothing was fixed in this PR (files
NOT in scope: everything else).

---

## 2. The ledger — every contract verified-or-deviation-recorded

All 27 dispatched contracts merged; the close re-ran each contract's headline (contract-specific)
DoD with fresh commands at close HEAD — the boilerplate tail (mypy/ruff/lint-imports/generated
prompts/task docs/pytest/check.sh) is covered once for the whole tree by §1 rather than
re-quoted 27 times. Verification was performed by a nine-way fan-out, three contracts per
verifier, each running the named pins/greps/targeted-pytest invocations directly against the
bytes at HEAD; the decisive command outputs are preserved in the PR's verification record.

**Tally: 25 VERIFIED, 2 DEVIATION-RECORDED (19.22, 19.23 — both expanded below; neither
silent).** The fan-out ran on the close branch's tree (close HEAD `7be97c7` plus this PR's own
doc-only commits, which touch no verified byte beyond the §5 registry-count bump).

| task (PR) | headline re-verification — the decisive fresh command(s), quoted | verdict |
|---|---|---|
| 19.1 (#333) | `check_doc_facts.py` green in 0.33 s + its 35-test perturbation suite; README carries the three reproducibility scopes ("designed for, not yet confirmed" on cross-platform), baseline 6 as the tip everywhere, the 0.938 conversion-label relabel beside 0.8646, manifest-quoted provenance (2026-07-20; 34%/30%), Node/npm prerequisite; DESIGN.md demotion banner → `docs/architecture.md` (8,543 bytes / 146 lines ≈ 1.1k words, ≤2 pages — word counts are splitter-dependent: 1,057 by this session's `wc -w`, 1,089 by ASCII-whitespace split); `.env.example` documents exactly the one live toggle vs `_TOGGLEABLE_LEVER_RESOLVERS` | VERIFIED |
| 19.2 (#328) | `grep 'DEAD in production'` → zero hits across the four swept files; every remaining "default-OFF" historical-tense except the genuinely live `impostor_roll_call`; AST compare at merge `ac16204`^..`ac16204` with docstrings stripped → all four files identical (zero behavior bytes moved) | VERIFIED |
| 19.3 (#329) | The AS241 sampler's distribution-quality pins green (40k-draw moments/tails/KS vs an independent `math.erfc` reference); fresh double-run digest-identical to the pinned golden `e72e24fe…`; the cross-platform claim NOT advertised in es.py or README (Darwin-arm64 run pending, owner-assisted) | VERIFIED |
| 19.4 (#325) | `training/rewards.py` states "the Ng et al. 1999 FORM — NOT policy-invariant here" naming the missing hypothesis; the non-invariance test asserts shaping 0.0 vs 2.0 on equal-env-reward trajectories; seed-0 exact-`==` pins prove no computed number moved (impostor 19.0, crew 12.925465838509316) | VERIFIED |
| 19.5 (#327) | 139 targeted tests green; `survival_rate` None-iff-undefined with validator; the 87-inversion recount pinned marker-free over committed bytes (9p2i 87/87, 4p1i 1/1); `supplied_channel_conversion` in all four committed reports; `build_sample_report.py --check` consistent on both sample sets | VERIFIED |
| 19.6 (#323) | Unknown-model Anthropic pricing raises (`pytest.raises` pin; the flipped former fallback test); `uv lock --check` exit 0 with httpx declared; `--color-ink-600` exists in the generated CSS; the loader's bare-env notice pinned both ways | VERIFIED |
| 19.7 (#330) | ci.yml `permissions: contents: read` + every action SHA-pinned; exactly one frontend build per CI run; `uv run --no-dev --exact` smoke imports the six entry modules with 18 dev packages uninstalled (pytest/mypy/ruff/hypothesis absent by `find_spec`); MIT LICENSE + CONTRIBUTING posture + SECURITY trust boundary present | VERIFIED |
| 19.8 (#326) | The nine capability disclosures at `replays/ml_corpus/README.md:104` with committed-bytes citations, numbers independently recomputed this session from the JSONL (roll-call split re-derived, not copied); mirror notes in both samples MANIFESTs | VERIFIED |
| 19.9 (#324) | `DEFAULT_SET = "9p2i"` pinned (`tests/api/test_sets.py`, 32 passed); the re-score committed with set-fingerprint `multi:29735b32fcb9` agreeing across producer/loader/committed stamp over the 3-sha mixed-provenance manifest (probe-pinned); `FEATURED_GAMES` carries the named seeds with editorial labels | VERIFIED |
| 19.10 (#335) | Meeting-pause/finale/unspoiled behavior fixture-pinned; outcome reveal a store state independent of perspective, default off, gating every outcome surface incl. URL state; stale 4p1i-default claims swept in `replay_loader.py`/`schemas.py`; both generated type artifacts drift-check green | VERIFIED |
| 19.11 (#339) | 47 taxonomy+mechanism tests green; exact per-category counts pinned on all four sets (9p2i 96/64/26; corpus 313/204/90) with fail-loud unknown-kind; no `p-X ↔ p-X` proof rendering; the four evidence-honesty mechanisms as separate committed fixtures at the contract's exact seed/meeting anchors; `teammate_coerced` chip omniscient-only under both reveal states | VERIFIED |
| 19.12 (#341) | `npm run test` 173 passed (6 files); `npm run lint` zero findings with the four legacy findings ledgered in `eslint.config.js`; the error-field three-way split with stale-response race tests; the Playwright journey green headless against auto-started dev servers (chromium pinned/preinstalled) | VERIFIED |
| 19.13 (#343) | 22 demo-bundle tests green incl. the Playwright case serving the BUILT bundle with network interception asserting **zero `/api` requests** through play → pause → ballots → finale; repo-wide stale default-claim grep clean; README opens with the committed capture + three reproducible-claim commands | VERIFIED |
| 19.14 (#342) | 85 deduction-metric tests green; the 13 redirected ejects and both roll-call estimators recomputed from committed bytes as pins; BOTH partitions in the committed report bytes with separate denominators (meeting-flag 70→68/2, 95→10/21, 10/31; ejectee-proof 68/101, 10/33) matching the triage recount; the `api/routes/eval.py` stale-default sweep quoted in place | VERIFIED |
| 19.15 (#331) | 28 vote-guard-rationale tests green; the coerced rationale is marker + upstream markers + the neutral note (whole string pinned; phrasing scan proves no teammate/kill vocabulary); "**Dormant for committed bytes.**" in the docstring — committed surfaces unaffected | VERIFIED |
| 19.16 (#336) | The guide's demo path matches `FEATURED_GAMES` seed-for-seed with verbatim blurbs; its quoted numbers re-verified against their committed sources (citation-compliance pins, the triage cross-tab); the outsider path README → guide → demo → the three named audits intact | VERIFIED |
| 19.17 (#344) | 56 ticker/cost-chip tests green: the four fog cases pinned in as-agent view (unwitnessed never attributes; body-discovery surfacing), unspoiled mode leaks no outcome, chips cumulative-to-current-frame reaching the game total only at the last frame | VERIFIED |
| 19.18 (#334) | The three rendered-prose scrape sites re-confirmed in the bytes before trusting their FROZEN labels; 70 files carry the tier-map freeze label; `training/README.md` §2 names the disputed surrogate boundary (RANKING kept 46/60; standalone DECISION arm retired on the 0-eject/96-skip census); the reopening checklist documents both routes + the four pre-campaign checks | VERIFIED |
| 19.19 (#338) | Every deletion's consumer grep on the record (PR #338 + per-deletion commits); `training/realpath.py`/`llm/cache.py`/probe recorder gone, `training/realpath_schema.py` + its 122 relocated tests green; both skipped candidates recorded with blockers (SectionLabel revived by 19.9/19.10 — live at HEAD with 8 references; the surrogate no-op recorded in `runner.py:48-58`) | VERIFIED |
| 19.20 (#332) | Fresh `scripts/paired_stats.py` run reproduces every §18 cell (ea4bc955 17/4 p=0.0072; bfd145cb 20/5 p=0.0041; shipped 6d327dcb 15/9 p=0.3075 n.s.; 7f73929d 12/3 p=0.0352 failing Bonferroni α=0.0125); 47 pin tests green; all five in-scope reports carry additive dated errata | VERIFIED |
| 19.21 (#337) | The RECOVERED outcome recorded as a dated erratum (finalist §19, 2026-08-15); 1,569 manifest digests counted fresh and the restored slate hashes 1,569/1,569 OK; the staging ref pushed at the pinned `c27ab7b5`; no re-recording (the ~57-busy-hour price named and declined). The staging ref's DELETION was 19.22's box — see below | VERIFIED |
| 19.22 (#346) | The 90 retained paths each marked with a pinning test (empirically finding a third consumer file, recorded); the evidence commit is ONE orphan (`rev-list --count` 1, no parent header) at the manifest's pin, 2953/2953 sha-clean; weight/sidecar pairs 245/245 paired; `fetch_evidence.sh --verify` OK — **but the staging ref is NOT retired at origin (F2)** | **DEVIATION-RECORDED (F2)** |
| 19.23 (#348) | One command green in one invocation on BOTH states: un-restored → 54 checks, ABSENT its own reported class (260 sidecars), exit 0; restored → `--complete` 54 checks 0 FAIL, 2952/2952 + 260/260 hash-verified; accept-recorded-LOST implemented and asserted — **but its own new test file carries the restored-state coupling (= F1)** | **DEVIATION-RECORDED (F1)** |
| 19.24 (#345) | The `data as T` cast now gated by `assertViewModelVersion` with `VIEW_MODEL_VERSION="1"` in generated lockstep; `eval/leak_scan.py` pytest-free with BOTH production consumers importing it, pinned by the hermetic subprocess partition probe; the `moved_players` Hypothesis sweep + planted-leak proofs green (19 + 6 + 3 targeted tests) | VERIFIED |
| 19.25 (#347) | 21 walker tests green (one negative fixture per profile); all four committed reports `--check` byte-consistent through the walker; the seven consumer modules each on their own `ReplayWalkConfig` profile; 162 consumer-suite tests green | VERIFIED |
| 19.26 (#340) | 98 parity tests green pinning ALL 707 committed meetings / 3,934 ballots across the four sets plus synthetic edges; the two-implementation zero-disagreement run on the record (PR #340); consolidation DONE — `MeetingManager._tally` is a thin delegation to `meetings.voting.tally_ballots` (2026-08-16) | VERIFIED |
| 19.27 (#349) | The 6 meta-tests green (tier split + no-test-module imports); `regen_test_goldens.py --check` byte-identical on both goldens; markers registered with `--strict-markers -m 'not campaign'`; the weekly `campaign-tier.yml` home (`17 6 * * 1`); the re-walk delta on the record (6→2 rebuilds, 1,735→1,335 walks) | VERIFIED |

**F2 — the un-retired staging ref (19.22's one unmet DoD box; recorded openly, routed to the
owner).** `git ls-remote origin 'evidence/*'` still returns
`c27ab7b5… refs/heads/evidence/raw-slate-staging` at this close, three days after the 19.21
recovery. The shortfall is NOT silent — `training/artifacts/coevo/EVIDENCE-MANIFEST.md` records
it verbatim ("its deletion is the one step this task could not execute …
`git push origin --delete evidence/raw-slate-staging` was refused by GitHub with HTTP 403") and
`docs/artifacts.md` repeats it — but the contract sanctioned no couldn't-delete outcome, so the
ledger records it as a deviation rather than absorbing it. The consequence is duplication only,
never integrity: the pinned orphan commit `476a1f85…` independently carries and hashes every
staged byte (§1), so the staging ref is redundant by construction. Per AGENTS.md's
detect-and-fall-back rule for GitHub operations, this close ATTEMPTED every path its
environment offers before attributing the step to the owner, and all three are refused or
absent, each named: (a) `git push origin --delete evidence/raw-slate-staging` — denied by this
dispatch environment's action-permission layer (remote ref deletion is policy-blocked here, a
distinct refusal class from 19.22's HTTP 403); (b) the `gh` CLI — no authenticated mutation
path in this environment (its GitHub API surface is proxy-limited to a pinned read/review set;
the frontier CLI's own `gh pr list` observed HTTP 403, §5); (c) the GitHub MCP integration —
exposes branch creation but no ref-deletion capability. **The routed remedy remains the
manifest's own one-command owner step, at the owner's convenience:**
`git push origin --delete evidence/raw-slate-staging`.

**On 19.23's deviation:** the failing test IS §1's F1 — the contract's own new test file
(`tests/scripts/test_verify_ml_evidence.py:141`) symlinks the real `training/artifacts/coevo/`
into its scratch tree, so the close-mandated restore leaks in and the exact-failure-set
assertion breaks; green on an un-restored checkout (57/57 at this close after `--clean`). Every
headline item of the 19.23 contract itself verified green on both evidence states. One finding,
recorded once, owned by the close (F1) and routed forward.

---

## 3. The before/after story (generated numbers only)

Every figure below is generated: computed at close HEAD by the commands in §7, or quoted from a
committed/recorded measurement named beside it.

- **Gate runtime.** Before 19.27 the default gate WAS the full suite: **801.4 s (13:21), 4,932
  passed / 20 skipped / 3 xfailed** (PR #349's measured table, same container class). At the
  close: the default gate runs **4,621 passed / 20 skipped / 317 deselected / 3 xfailed**, and
  the campaign tier **317 passed in 314.93 s (5:14)** — the default gate dropped **−27.0 %**
  (801.4 s → 585.1 s in 19.27's quiet-container measurement; this close's own default-tier
  pytest read 815.1 s under a deliberately loaded container — §5 quotes the load honestly — and
  the campaign tier 314.9 s). Both tiers together still run every pre-existing test: 4,621 + 317
  = 4,938 vs the charter baseline **4,531 passed / 20 skipped / 3 xfailed** at `67166b3` — the
  phase ADDED a net **+407 tests** while cutting the default gate by a quarter.
- **Clone weight.** The 19.22 prune moved every unpinned Phase-18 co-evolution byte plus the
  recovered finalist raw slate to the ONE orphan evidence commit `476a1f85…`:
  **101.097 MiB / 1,383 files (coevo) + 298.157 MiB / 1,569 files (raw slate)** off the working
  tree (`docs/artifacts.md`, the registry generated at 19.22), restorable and verifiable by
  pinned sha (§1's two evidence legs prove both directions round-trip). Fresh reads at close
  HEAD: the full-history pack is **109.29 MiB** (`git count-objects -vH`), the tracked working
  tree **261 MB** (`du` over `git ls-files`), and the documented blobless fast path
  (`git clone --filter=blob:none`) downloads roughly the working tree alone. Stated honestly, as
  the registry itself states it: the prune shrinks the working tree, not the history — a
  full-history clone still carries the pre-prune coevo bytes, and no history rewrite happened
  this phase (locked decision 5).
- **The truth checks.** At charter, zero generated-fact checks existed and the front door was
  documented as false by both input audits. At close: `scripts/check_doc_facts.py` (19.1)
  re-derives every checked README/.env.example fact from the bytes that own it — 3 check
  families, 28 distinct fail-loud drift classes — and reads green (§1); the task/prompt surface
  is generator-checked (*"321 tasks and 321 prompts"*, *"All 321 prompts are in sync"*); the
  tier split is meta-tested (`tests/training/test_suite_tiers.py`); and the evidence promises
  are machine-verified end to end (`verify-ml-evidence`'s 54 checks, §1). The drift classes the
  input audits catalogued by hand are now the gate's job.
- **The deduction instrument exists.** The four committed `tournament-eval-report.json` views
  now carry the 19.14 `deduction` block — the proof-vs-inference cross-tabs under BOTH
  partitions with separate denominators, weak-flag-only conviction, turn→ballot consistency,
  role-split response coverage, redirected-ballot share, and scaffold-leakage rates — rendered
  on the dashboard's proof-vs-inference panel. Those committed cells are §4's evidence, which is
  the point: the phase built the instrument the post-19 decision reads.

---

## 4. The post-19 decision menu (locked decision 6) — the owner's routed decision

Locked decision 6, verbatim in intent: the evidence-honesty substrate fixes are decided AFTER
the metrics; the close routes the decision — **the evidence-honesty substrate phase vs the
presentation phase** — to the owner, argued from the 19.14 metrics. No unilateral ruling is made
here.

**The recommendation, first (the framing rule): Option A — the evidence-honesty substrate
phase — then presentation.** The 19.14 numbers do the arguing (§4.1): today "deduction" is
proof-lookup — conviction accuracy is a perfect 1.000 wherever ejectee-specific proof exists and
0.303–0.393 where it does not, every innocent ejection in every committed set happens in that
non-direct cell, and the rare weak-flag-only convictions are 100% wrongful (5/5 innocent pooled
over all four sets: 1 samples 9p2i + 3 corpus 9p2i + 1 samples 4p1i + 0 corpus 4p1i). The substrate phase attacks exactly that cell, and this phase already committed its
measurement (19.14's cells), its executable exhibits (19.11's four injustice fixtures), and its
display (the proof-vs-inference panel) — the before/after instrument costs $0 and is already at
HEAD. Presentation multiplies quality; the quality gap is now measured and located, and the
charter's own clause prices the order: polish never ahead of narrative correctness (locked
decision 1). Sequencing A → B also preserves the roadmap thesis (presentation LAST, multiplying
quality that already exists).

### 4.1 The evidence — the committed 19.14 cells (all quoted from the four committed reports)

The ejectee-proof partition (the headline cross-tab; Wilson 95% intervals as committed):

| cell | samples 9p2i | corpus 9p2i | samples 4p1i | corpus 4p1i |
|---|---|---|---|---|
| **direct-proof accuracy** | **68/68 = 1.000** [0.947, 1.0] | **213/213 = 1.000** [0.982, 1.0] | 9/9 = 1.000 | 20/20 = 1.000 |
| **non-direct accuracy** | **10/33 = 0.303** [0.174, 0.473] | **35/89 = 0.393** [0.298, 0.497] | 1/3 = 0.333 (advisory) | 0/0 — no cell |
| innocent ejections (all in the non-direct cell) | 23 | 54 | 2 | 0 |
| proof-present innocent ejections | **0** | **0** | **0** | **0** |

Pooled across all four committed sets: **310/310 = 1.000 with proof; 46/125 = 0.368 without;
79/79 of innocent ejections in the non-direct cell.** The meeting-flag partition (its own
denominators, never mixed — the C5 discipline), quoted 9p2i-only: flagged-meeting accuracy
68/70 = 0.971 (samples 9p2i) / 213/216 = 0.986 (corpus 9p2i) vs unflagged 10/31 = 0.323 /
35/86 = 0.407 (same two sets; the committed 4p1i cells — flagged 9/10 and 20/20, unflagged 1/2
advisory and 0/0 no-cell — tell the same story at advisory-grade n). The supporting cells,
the two 9p2i reports: weak-flag-only convictions 1/90 (samples) and 3/275 (corpus), **innocent in every
instance** (share 1.0, advisory-flagged at these n); turn→ballot consistency **0.447 / 0.459**
(an agent's spoken accusation and its ballot agree less than half the time); impostor
whereabouts-response coverage **0.490 / 0.500** pooled vs crew ≈ 0.996; engine-redirected
ballots 1.3 % / 1.8 %; scaffold leakage in rendered rationales: model-omniscient ballot rate
**42/245 = 0.171 / 110/684 = 0.161**, partner-naming 0.118 on both 9p2i sets. The 4p1i sets'
weak-flag cells complete the pool: samples 4p1i 1/12 (innocent), corpus 4p1i 0/20 — **pooled
weak-flag-only convictions 5/5 innocent across all four sets**.

Read together: the game's convictions are near-perfectly grounded where the substrate hands the
crew role-proving evidence, and WORSE than a coin flip — with all the injustice — where agents
must actually infer (every defined non-direct cell sits below 0.5). The inference channel is the broken one, and it is broken by
measured substrate/prompt honesty mechanisms, not by model capability alone: the four committed
19.11 fixtures exhibit them executably (the provenance-impossible sighting, 9p2i seed 23 M1; the
content-vs-own-memory miss, seed 12 M0; the one-tick interval artifact, 4p1i seeds 41/49; the
equal-weight conflict, seed 41), and the prompt-side flag naming ("VERIFIED evidence" for
unverified statement pairs) was explicitly routed to THIS decision by locked decision 1.

### 4.2 Option A — the evidence-honesty substrate phase (recommended)

- **Scope (pre-chartered on the planning backlog §5):** sighting provenance,
  content-vs-own-memory validation, interval/weighting honesty, and the prompt-side flag naming
  — the four mechanisms the 19.11 fixtures pin — plus the equal-response-shape prototype behind
  a measured gate. Gameplay-adjacent BEHAVIOR change, i.e. exactly what Phase 19's NOT-list
  forbade and deferred here.
- **Outcome:** the non-direct cell becomes a real, movable inference channel; success is
  measurable at $0 against the committed instrument (non-direct accuracy and the
  innocent-ejection count move, or they don't — findings either way, the Phase-14 doctrine).
- **Costs:** prompt-template edits break the prompt byte-goldens and bump the prompt-set version
  (the pinned regeneration path exists); a substrate change makes every baseline-6-anchored
  artifact prior-substrate per the 18-close §5 staleness rules, so adopting it means ONE new
  adopting record + a corpus re-record before anything trains against it — operator time on the
  order of the 18.13 recording (~23 h wall on the owner's machine), $0 at the flat-rate
  provider. Until that record, the committed sets stay canonical and every gate stays green:
  the work ships default-OFF/lever-gated per standing rule 4.
- **Risks:** recording variance (the record may need re-runs); scope creep into mechanics (the
  charter for the phase must carry its own NOT-list); the fixes may move supply more than
  honesty (the deduction metrics and the injustice fixtures are the guard — they pin the
  failure modes, not just the rates).
- **What A does NOT decide:** the ML re-open fork stays its own owner decision against a
  concrete proposal (locked decision 3); no mover flip, no training campaign, no bar re-pricing
  rides along.

### 4.3 Option B — the presentation phase

- **Scope (the re-scoped roadmap node):** leaderboards, highlight reels, dataset packaging, the
  retrospective; heterogeneous-model lobbies remain their own later decision and the human seat
  stays OUT (charter).
- **Outcome:** multiplies the presentation of what exists; $0/offline; zero substrate risk; no
  re-record; no staleness ripple.
- **Costs:** low per item; mostly frontend/docs work on the 19.12 test baseline.
- **Risks:** it amplifies the measured narrative as-is — every surface it builds presents a game
  whose no-proof convictions run 0.303–0.393 with all the innocent ejections, and a leaderboard
  computed over the current cells ranks proof SUPPLY, not deduction; the charter's "polish never
  ahead of narrative correctness" clause prices exactly this. The marginal value is also lower
  than at charter: 19.13's static demo, the curated default, and the dashboard already give the
  project a truthful presentable front door.

The owner can also rule NEITHER now (defer the charter decision); the menu as locked names the
two phases above, and deferral leaves the backlog routed and the instrument committed.

### 4.4 The owner's ruling

Put to the owner on this close's PR with the recommendation above. Per the 15.18 convention the
owner's merge of this document ratifies the close reading; for the MENU, the merge ratifies the
recommended route (Option A as the next chartered phase's candidate) **unless the owner records
a different ruling on the PR before merging** — and any post-merge modification lands here as a
dated erratum, never an in-place rewrite. The ruling, whichever way, charters nothing by itself:
the next phase opens only when its own `tasks/phase-N.md` is authored and ratified (the standing
convention).

---

## 5. Decisions

- **The close verifies; it does not fix.** F1 (§1) and F2 (§2) are recorded and routed — F1 to
  the next phase's inputs, F2 to the manifest's own one-command owner step; no test, script, or
  doc outside this contract's files was touched, with the ONE mechanical exception below.
- **The one added-scope edit: `docs/artifacts.md`'s `audits/` registry row, 97 → 98 files.**
  Landing `audits/audit-phase-19-close.md` (this file — in scope, mandated) trips the in-tree
  family inventory check exactly as 19.23 built it to fail on registry drift (*"audits/:
  docs/artifacts.md promises 97 files, the index tracks 98"* — the verifier and 3 of its tests
  go red on any audits/ addition that skips the bump). The count is re-derived from the index
  (98 files; the 4.8 MB size figure is unchanged at its own precision), the full evidence cycle
  re-ran green after the bump (fetch *"OK: 2953/2953"*; `--complete` *"54 | OK 49 | FAIL 0 |
  ABSENT 0 | INFO 5"*), and the edit is one token in one generated-registry row — the mechanical
  consequence of the close's own mandated artifact, not a fix to phase work. **So the diff stays
  within contracted scope rather than carrying a recorded exception, the 19.28 contract's own
  files-in-scope list gains the row as a dated close-recorded surgery note in this same PR**
  (`tasks/phase-19.md` is 19.28-scoped for exactly such notes; its generated prompt regenerates
  in lockstep) — the owner's merge ratifies the amended scope, the 15.18 convention (the review
  round's P1, absorbed).
- **The second review round's front-door refreshes (three more dated surgery notes, same
  mechanism):** flipping the banner made the two README project-status/roadmap sentences and
  DESIGN.md's §9 supersession-banner line stale ("Phase 19 … is under way"), and the banner
  expansion shifted the two `tasks/phase-19.md` line anchors `docs/reading-guide.md` cites (3-4 →
  22-23; 87-89 → 106-108; a repo-wide grep found no other line-anchored citation). Leaving any
  of them would reintroduce at the close the exact front-door drift class 19.1 removed, so all
  three files join the contract's files-in-scope as dated close-recorded surgery notes (README's
  two sentences, the one DESIGN.md supersession line — demotion-era prose, not historical
  content — and the guide's two anchors, nothing else), the 19.28 prompt regenerated in
  lockstep, and the owner's merge ratifies. `check_doc_facts.py` re-ran green over the edited
  README.
- **The gate-ordering decision (F1's consequence):** the default gate's green is quoted from the
  clean state (`fetch_evidence.sh --clean` → `check.sh`), the evidence legs from the restored
  state — the two states the verifiers themselves define. Both invocations and both states are
  quoted; nothing is averaged.
- **The corpus sets' byte identity is certified via `--complete`'s reconstruction rows** (300/300
  across all four sets) rather than by duplicating the explicit
  `verify_samples.sh replays/ml_corpus/*` arms in the same session; the bare wrapper covered the
  two canonical sets exactly as the DoD names it.
- **Timing honesty:** this close's first `check.sh` run and the campaign run shared the container
  with the ledger fan-out (deliberate — correctness legs, not timing legs); the quoted default-
  gate runtime story (§3) rests on PR #349's quiet-container measurements, and this close's own
  quiet-state rerun time is quoted in §1's table. The re-walk counts and all evidence numbers
  are load-independent.
- **The frontier CLI's gh leg is environment-degraded here** (`gh pr list` GraphQL 403 in this
  dispatch environment), so `compute_next_task.py --phase 19` was demonstrated on its offline
  preview and the PHASE-COMPLETE claim rests on the same second index the 18-close used: feeding
  `compute_frontier` the merged `task 19*` titles from the unshallowed `git log` (§6, snippet in
  §7). `parse_all_tasks` returned zero errors.
- **No tag is minted at this close.** Nothing this close produced requires byte-level provenance
  beyond git itself (no replay bytes moved); the provenance point is this PR's merge commit,
  and the owner MAY tag it at leisure — the honest precedent stands that neither
  `phase-17-close` nor `phase-18-close` was ever minted (§6).
- **The 19.14 evidence is quoted, never recomputed with new definitions:** every §4.1 cell is
  read verbatim from the four committed `tournament-eval-report.json` deduction blocks (the
  cells 19.14 pinned against the triage's independent recount), so the menu argues from the
  committed instrument, not from a close-session reinterpretation.

---

## 6. Provenance + the frontier

- **Close HEAD:** `7be97c7` — *"task 19.27: test-suite structure: markers, the shared fixture,
  pins to goldens (#349)"*, merged 2026-08-18. `origin/main` and the close branch agree; the
  working tree was clean apart from the by-design untracked evidence restore (§1), which was
  `--clean`ed before the gate's clean-state rerun and never staged (the restore's own
  `.gitignore` fence held: `git add -A` cannot stage it).
- **The phase's evidence chain:** 27 merged `task 19.*` titles (#323–#349, waves per the phase
  doc's DAG), the planning PR #322 (`8813702`, 2026-08-03 — the charter ratification), and 6
  coordination commits (anchor refreshes between merge batches: `94d8809`, `9e34656`, `f87d4a0`,
  `300221e`, `c25b1b5`, `f730e4d`). 34 commits to `main` total this phase: the planning merge
  plus 33 execution commits after it (27 task merges + 6 coordination —
  `git rev-list --count 8813702..7be97c7` = 33, the range exclusive of the planning commit).
- **The frontier computes complete on this close's merge:** with the merged `task 19*` titles
  from the unshallowed log, `compute_frontier` reads **AT HEAD: dispatchable `['19.28']`,
  blocked `[]`, merged 27**; **WITH 19.28 MERGED: dispatchable `[]`, blocked `[]`, merged 28.**
- **The evidence pin:** `476a1f85492439277350af9708f1d120eb1c0a71` (the ONE orphan commit on
  `evidence/phase-18-coevo`), fetched by sha and verified twice at this close (§1). The 19.21
  raw-slate ruling stands RECOVERED (2026-08-15) in `docs/artifacts.md`.
- **Remote tags observed** (read-only query, identical to the 18-close's observation plus
  nothing): `attempt-1-phase-10-wave1-rerecord`, `phase-16-baseline-4` → `a43b178`,
  `phase-16-baseline-5` → `2428044`, `phase-18-corpus-8f5f434` → `8f5f434`. No `phase-19-*` tag
  exists and none is required (§5).
- **The banner and the roadmap record the close in this PR:** `tasks/phase-19.md` STATUS →
  CLOSED (this close), and `tasks/post-phase-14-plan.md`'s Phase-19 spine node + §3 bullet gain
  the close tick — the roadmap tick this close owns. The PR also carries the one-token
  `docs/artifacts.md` registry bump (§5).

---

## 7. Method + reproduction (all $0 against committed bytes; network only where named)

```
# Full history before any history claim (the AGENTS.md rule). --unshallow errors on a
# complete clone, so it is guarded; a complete clone just fetches normally.
if [ "$(git rev-parse --is-shallow-repository)" = "true" ]; then
  git fetch --unshallow origin
else
  git fetch origin
fi
bash scripts/check.sh                                               # §1 default gate — CLEAN state (F1 defines the state)
bash scripts/fetch_evidence.sh                                      # §1 OK: 2953/2953 files match 476a1f85…
uv run pytest -m campaign                                           # §1 opt-in tier — 317 passed, run in the RESTORED state §1 records
uv run python scripts/verify_ml_evidence.py --complete              # §1 checks: 54 | OK 49 | FAIL 0 | ABSENT 0 | INFO 5
bash scripts/verify_samples.sh                                      # §1 both canonical sets clean (bare env)
uv run python scripts/check_doc_facts.py                            # §1 front-door facts green
uv run pytest tests/scripts/test_verify_ml_evidence.py -q           # §1 F1: fails restored / 57 passed after --clean
uv run mypy .                                                       # §1 F1's second facet: 15 errors restored / clean green
bash scripts/fetch_evidence.sh --clean                              # §1 removes the 2,952 restored files
git count-objects -vH ; git ls-files -z | du -ch --files0-from=-    # §3 clone-weight fresh reads
python3 - <<'EOF'                                                   # §4.1 the committed 19.14 cells, read verbatim
import json
for d in ("replays/samples/9p2i", "replays/samples/4p1i",
          "replays/ml_corpus/9p2i", "replays/ml_corpus/4p1i"):
    print(d, json.load(open(f"{d}/tournament-eval-report.json"))["deduction"])
EOF
git ls-remote --tags origin                                         # §6 read-only remote query
```

```python
# §6 — the phase-complete frontier, cross-checked with a git-log title index (the 18-close method).
# The log is PINNED to close HEAD so the snippet reproduces after this close merges — an
# unbounded log would already contain 19.28's own merge title and collapse the before/after.
import subprocess, sys; sys.path.insert(0, "scripts")
import compute_next_task as cnt
from _task_parser import parse_all_tasks
titles = [t for t in subprocess.run(["git", "log", "7be97c7", "--format=%s", "--grep=^task 19"],
          capture_output=True, text=True, check=True).stdout.splitlines()
          if t.lower().startswith("task 19")]
errors: list[str] = []; tasks = parse_all_tasks(errors); assert not errors
print(cnt.compute_frontier(tasks, set(), titles, 19))   # dispatchable ['19.28'], merged 27
print(cnt.compute_frontier(tasks, set(), titles + [
    "task 19.28: the phase close (owner)"], 19))        # dispatchable [], merged 28
```

The per-contract ledger commands (§2) are enumerated in the close PR's verification record; each
row's decisive invocation is quoted in the table itself.
