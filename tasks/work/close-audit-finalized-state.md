# The close audit: what the project demonstrates, and what it does not

**Status:** ready

## Outcome

The finish wave ends the project's current arc, and nothing in the tree says, in one place, what that arc left. The
last close is phase 21's (`audits/audit-phase-21-close.md`). Since then the process direction of 2026-09-19 and the
Stage-B wave produced records per recording (the baseline-9 re-record, candidate rounds 1 to 3) and dated rulings
across three documents, but no close. A reader who did not watch the work (a next owner, a reviewer, a visitor from
the README) has to rebuild the state from 33 merged pull requests (at `335cbdc9`), a 1,649-line decision memo and
two advisory memos kept outside the tree. Two cards were held: `rubric-extractor-era`, whose purpose fell with rubric
version 1 and whose remaining half the owner's D14 ruling of 2026-10-09 retires, is closed unexecuted by the
orchestrator's `docs:` commit on `main` before `retire-era-locked-pins` merges, a precondition this card reads at B and
does not write; and `retire-temporal-evidence-v1`, which waits for an adopting record for evidence reasoning version 2
that round 3 does not take, stays `ready` and blocked, because closing it is the owner's D15 word (the baselines
memo's D15, which memo 8.5 leaves undecided). The audit lists that closure as an owner confirmation point.

This card is document-only (decision memo 8.7 item 4: the documentation lens alone). When it is done:
- `audits/audit-<YYYY-MM-DD>-finalized-state.md` exists, dated by the head that states its figures, indexed once in
  `audits/README.md`, with these sections in this order:
  0. **For a reader who did not watch the work.** One page: what the project is, what its evidence shows, what it
     does not, where to look next. No internal label (task, decision, ruling or audit id) and no unexplained term.
  1. **What the system is.** The deterministic engine; the rule-based tactical layer, with model calls only at
     meetings and explicit triggers; the observation firewall; the meeting layer that labels a ballot and never
     rewrites it; the game's shape (`docs/game-shape.md`); the recorded eras and the partial-record principle. Each
     claim names its enforcing mechanism at the strength that mechanism delivers.
  2. **The eras and the committed sets.** Every committed and candidate set, its era, its owning record, its declared
     config, and where each recording a promotion replaced is still readable (commit and path, and, for round 2 if
     round 3 was promoted, its candidate copy `replays/candidates/stage-b-r2`, kept by the owner's amendment of
     2026-10-09).
  3. **What it demonstrates, with the command behind each claim.** The process scorecard's rows for each era; the
     census's held-data cells (what a ballot held, cited lines against the engine route, stated places the map or
     the regroup reconciles) and its genre cells (vents, regroups, meeting structure, the shape of a game); the
     profile's shelves and tripwire readings; the route lines' offline reach and round 3's reading of them; what the
     public demo features; and the owner's goal (a vote or skip rests on data the agent holds, true or false) read
     count-only.
  4. **What it does not demonstrate.** Role-correctness, reported and never a gate, stated as such; one 50-seed
     recording per round, so no difference between rounds is claimed as real and any interval is descriptive; the
     27B model's own route arithmetic; the reporter trap's standing; and the ML program, on hold with its re-pricing
     precondition.
  5. **The doctrine and its rulings, by section.** The direction document and its addenda, the Stage-B decision memo
     sections 0 to 8.9 with 8.9's amendment of 2026-10-09 and any dated line after it, the diagnosis, `docs/game-shape.md`, AGENTS.md's craft rules, and the two advisory memos
     outside the tree (the baselines memo, the rubric design memo), each with its path and labelled advisory.
  6. **The work that reached `main`.** One row per pull request merged since the direction's commit `0755c25d`: number,
     card path, merge commit, date. This audit's own pull request is the stated residual.
  7. **Open items for a next owner.** The extractor's fate; impostor self-report (R6); the five live substrate
     toggles and the evidence-reasoning version left selectable; the owner confirmation points the finish wave left:
     closing `retire-temporal-evidence-v1` (D15), the dashboard, belief-panel and badge halves the front-door card
     held (D8-L, D8.1, D9-L), and the before column's form (D12) as the promotion took it, if it ran; any D14 item
     `retire-era-locked-pins` left; a full re-record for baseline 10; the baselines memo's other undecided items;
     every defect this audit found on the way, with its `path:line`, filed and not fixed here.
  8. **Reproduction.** Every number in sections 0 to 7 with its command or its `path:line`, count-only.
  9. **Limitations of this audit**, including that no CI gate binds its figures after it merges.
- The audit reads the held cards' state at B and writes neither: `rubric-extractor-era` closed by the orchestrator's
  `docs:` commit (cited by sha), `retire-temporal-evidence-v1` still `ready` and blocked unless a dated owner word on
  D15 closed it before B (cited if so).
- Nothing ships, no recorded byte moves, and the demo rebuilds identically.

## Evidence

Every `path:line` is at `225d2b77` (labelled as such) and is re-anchored by its symbol or heading at dispatch;
`335cbdc9`, the amendment's commit, changes only the decision memo, whose citations are given there. Every
count is count-only, keyed by (set, meeting) where it reads replays, measured at `225d2b77` in a bare shell (`env |
grep -c '^AILIBI_'` printed 0) after `uv sync --frozen`, and re-measured at dispatch; the dispatch figure governs. No
prompt, transcript or seed-band prefix was printed, and `.env` was not read.

**The doctrine every section serves.** `tasks/direction-2026-09-19-process-over-outcome.md`: section 1 (the goal as
P1 to P6), section 7 (the meeting layer labels, never rewrites; nothing pushes an agent toward the correct answer;
wrong-but-believable is the game working), section 8 (role-correct ejection "reported beside, never a gate"), section
12 and its addenda of 2026-09-20, 09-24, 10-01 and 10-06. `tasks/decision-2026-09-24-stage-b-wave.md` sections 0 to
8.9 (8.1 the owner's eight rulings of 2026-10-06; 8.7 the five process amendments; 8.8 the step after round 3,
delegated; 8.9: "Merge both when verified and retire the memo's D14 list", with the two orchestrator defaults: no
wrong-but-believable ejection featured on the strip, and the README leading with the process rows; and 8.9's
amendment of 2026-10-09, `:1612-1622` at `335cbdc9`: "Keep the comparison records", so round 1's candidate directory
stays, the proposal that round r+1 deletes round r is declined, and a promotion of round 3 keeps round 2's bytes as
`replays/candidates/stage-b-r2`).
`tasks/diagnosis-2026-10-02/README.md` Parts 1 to 4. `docs/game-shape.md`. AGENTS.md craft rules 1 to 7. The
baselines memo (`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/baselines-2026-10-03/baselines-memo.md`,
Part 2's classes, Part 3.1's RETIRE and DEMOTE rows, Part 4 D7, D8 and D14 with D14-T1 to T3) and the rubric design
memo (`.../rubric-design-2026-10-06/rubric-design-memo.md`) are advisory, outside the tree, read-only at `cf3341ab`
and `76270d6c`; the decision memo cites both that way (section 8's preamble and 8.6), and so does the audit.

**The state the audit describes, at `225d2b77`.**
- Eras: `ERAS = (BASELINE_9, STAGE_B_R2)` (`eval/eras.py:90`), `LADDER_TIP_ERA = BASELINE_9` (`:95`), four
  `COMMITTED_SETS` (`:98-103`), "baseline 10 is reserved for the full re-record that re-freezes the corpus" (`:24`).
  `replays/candidates/` holds `stage-b-r1` only; baseline 9's 9p2i bytes are readable at `d41c9006`.
- The process scorecard's shown-set column (`docs/process-scorecard.md:108-119`): grounded EJECT 407/410, grounded
  SKIP 44/281, deviating EJECTs 65/292, manufactured contradictions 1/15, unexplained 11/691, agent-authored 674/691,
  wrong-but-believable 189/410 "reported, never penalised", role-correct 44/66 "reported beside, never a gate".
  `uv run python scripts/publish_process_scorecard.py --check` exits 0 (11.7 s).
- The census (`docs/gameplay-census.md`): holds-nothing SKIPs whose prompt names no living candidate 0/214 (`:388`);
  supported EJECTs whose cited line the route makes true 278/281 and false 3/281 (`:390-391`); ejections whose ejected
  player had a stated pair that reconciles 41/66, at witness meetings 7/12 (`:439-442`); reporter seats ejected
  without vent proof 17/93 against other crewmate seats 5/291 (decision memo 8.2 item 1). `uv run python
  scripts/publish_gameplay_census.py --check` exits 0 (5.6 s).
- The profile (`docs/game-profile.md`): the decisive tripwire trips one ejection, (26, 2) (`:63`); "Decided without
  proof: wrong on what it held" 20 games, 21 ejections, beside "the table was right" 18 games, 19 ejections
  (`:99-100`). `uv run python scripts/publish_game_profile.py --check` exits 0 (4.6 s).
- Route lines (`experiments/lab/report-route-lines-replay.md:121-122`, column r2): the lines reach 31 of 40 misjudged
  cases and 7 of 7 at witness meetings, against the reference check's 29 of 40; "Reaching is showing a line, not
  changing a vote" (`:125`). `uv run python -m experiments.lab.route_lines_replay --check` prints "reproduced"
  (49.7 s; it needs full history).
- The public demo features 9p2i seeds 19 and 14 (`frontend/src/components/ReplayPicker.tsx:115-148`); neither is on
  the "wrong on what it held" shelf, so the intersection is 0, memo 8.9's default.
- `uv run lint-imports`: "Contracts: 5 kept, 0 broken". `uv run python scripts/verify_ml_evidence.py` (offline):
  checks 64, OK 52, FAIL 0, ABSENT 7, INFO 5 (30.2 s).
- Merged pull requests since the direction's commit: `git log --first-parent --merges --oneline 0755c25d..225d2b77 |
  wc -l` prints 33 (#471 to #504, less #478); the finish wave adds round 3's record and its own cards.

**The surfaces the card writes, and the gates that hold them** (at `225d2b77`).
- `audits/README.md` is checked both ways by `check_audits_index` (`scripts/check_doc_facts.py:2711-2770`); its links
  by `check_relative_links` (`:5271`, the index is in `_LINKED_DOCUMENTS`, `:255-261`); any "ladder tip" sentence in
  it by `check_ladder_tip` (`:1957`, `_LADDER_TIP_DOCUMENTS` at `:292-298`); any win rate or recording date in it by
  `check_repeated_claims` (`:1612`). The audit file itself is in no checked list, which is phase 21's finding F1
  (`audits/audit-phase-21-close.md`, "F1"); this card's scratch check and the documentation lens stand in for one.
- `docs/artifacts.md:113`, the `audits/` row, reads "31,431,870 tracked bytes / 334 files", equal to `git ls-files
  audits` at `225d2b77`; `scripts/verify_ml_evidence.py` fails any drift (`inventory_problems`, `:2887-2924`).
- `tasks/README.md:43`: "As of 2026-10-09, `tasks/work/` holds 102 cards: 3 ready, 99 done", derived by
  `scripts/validate_task_docs.py` (`validate_card_inventory`, `:188`); a done card with an unchecked box or no
  Results fails (`validate_work_cards`, `:117-171`).

**The two held cards, as this card finds them at B.**
- `tasks/work/rubric-extractor-era.md` (`:3` `ready` at `225d2b77`; `## Results` reads "Not started."). Its own
  alternative (b), "Drop it. This card closes as superseded with one history line, and D14's G27 card deletes
  `_cross_era_trajectory` itself" (`:145-146`, again at `:312-313`), is the branch the owner's 8.9 ruling takes. The
  orchestrator closes it unexecuted by one `docs:` commit on `main`, under one contract that this card does not
  restate, and lands that commit before `retire-era-locked-pins` merges (its paths are outside round 3's freeze, so
  it may land at any time before then). Its witness file, `experiments/lab/results-rubric-geomean.stage-b-r2.json`,
  was never written (`git ls-files` prints nothing).
- `tasks/work/retire-temporal-evidence-v1.md` (`:3` `ready`; no `## Results`). Its first acceptance item blocks it
  until an adopting record for evidence reasoning version 2 exists. Round 3 records with `evidence_reasoning_version`
  unset (`tasks/work/stage-b-record-r3.md:322`), and `git grep -c evidence_reasoning_version --
  'replays/**/experiment-config.json'` exits 1 (no declared config sets it). Whether the card waits or closes is the
  owner's word under the baselines memo's D15 ("wait" or "lift the exclusion"), which memo 8.5 leaves undecided and
  8.9 does not rule; on 2026-09-19 the same card was kept `ready` and blocked rather than closed (`034cad1d`). It
  stays `ready` and blocked, and its sentences in `tasks/README.md:115-116`, `tasks/post-merge-plan.md:51-52` and
  `docs/cleanup-dispositions.md:245` stay true while it does.
- Precedent for a closed-unexecuted card: `tasks/work/held-out-prefix-freeze-6.md` (`done`, one checked item saying
  no band was frozen, Results recording the closure, its date and the ruling);
  `tasks/work/close-deduction-candidate-evaluation.md:466-476`.

**A defect the audit will meet.** `docs/architecture.md:89` says "Four import-linter contracts"; `.importlinter`
holds five since PR #504 and `uv run lint-imports` prints "5 kept". The audit files it (section 7) with that command;
this card does not edit `docs/architecture.md`.

## Acceptance

Each item names its enforcing mechanism and the planted or perturbed case that proves it bites. `B` is `main` after
the front-door card merges (the branch point); `H` is the pull request's head. "The script" is `audit_check.py`,
written in the worker's scratch directory, run from the repository root, quoted whole with its sha256 in Results and
never committed (this card adds no code). It parses the audit's section 8 tables and exits 1 naming the row on any
miss.

- [ ] **The audit is indexed once, and its index row agrees with the front door and is plain.** Mechanism:
  `uv run python scripts/check_doc_facts.py` exits 0 at H (`check_audits_index`, `check_relative_links`,
  `check_ladder_tip`, `check_repeated_claims`); the row passes `copy_problems`
  (`tests/scripts/test_candidate_sets.py:538`) with 0 problems; a ladder-tip sentence, if any, names the baseline
  `eval/eras.py` `LADDER_TIP_ERA` names. Proof: the
  committed `test_unindexed_audit_detected` (`tests/scripts/test_check_doc_facts.py:4083`),
  `test_audits_index_ladder_tip_drift_detected` (`:2179`), `test_broken_relative_link_detected` (`:4214`) and
  `test_repeated_results_claim_detected` (`:1430`) pass at H; on a scratch copy, the row removed makes
  `check_doc_facts.py` exit 1 naming the file, "baseline 10" in a ladder-tip sentence exits 1, and "6/7" in the row
  gives `copy_problems` one problem.
- [ ] **Section 0 reads for a stranger.** Mechanism: the script's count-only scan of section 0 for
  `\b[A-Z]{1,2}[0-9]+(?:\.[0-9]+)?(?:-T[0-9])?\b|\bTask \d|\baudit-|\bPR #` prints 0; each term it uses links to its
  `docs/glossary.md` entry or is defined in the sentence that first uses it, which the lens confirms by listing the
  terms it checked. Proof: "R6" planted in a scratch copy gives one hit naming the line.
- [ ] **Every claim of section 1 names its mechanism at the strength delivered.** Mechanism: section 8 holds a claim
  table (claim, mechanism path, test node id, command). The script checks each path with `git ls-files
  --error-unmatch`, each node id with `uv run pytest --collect-only -q <id>`, and runs each command expecting exit 0
  (at least `uv run lint-imports`, `bash scripts/verify_samples.sh`, the firewall's planted-import test
  `tests/test_firewall.py::test_import_linter_reports_a_planted_agents_to_engine_route`, the scorecard's
  `tests/eval/test_process_scorecard.py::test_the_role_correct_row_is_labelled_as_no_gate`, and
  `tests/eval/test_eras.py`). The wording claims no more than its mechanism shows: the firewall is "bounded checks, not complete privacy
  assurance" (`README.md:22`), a valid citation is resolvable, not supported (`README.md:29`), and determinism holds
  "within their recorded runtime scope" (`docs/architecture.md:105-106`). Each section-1 paragraph ends with a
  reference to its claim-table row, and the script fails on a paragraph without one or a row no paragraph references.
  Proof: a scratch row naming a test id that does not exist makes the script exit 1 naming it; a paragraph "the
  firewall guarantees no leak" added to a scratch copy without a row makes it exit 1 naming that paragraph.
- [ ] **The era ladder is derived, not typed.** Mechanism: section 2's table equals, row for row, a one-line print of
  `eval.eras.COMMITTED_SETS`, `ERAS` and `LADDER_TIP_ERA` (path, era id, record, `recorded_on`, declared config) plus
  `git ls-files replays/candidates | cut -d/ -f1-3 | sort -u` at H; each replaced recording's location is checked
  with `git cat-file -e <commit>:<path>` (exit 0), at least baseline 9's 9p2i at `d41c9006` and, if round 3 was
  promoted, round 2's bytes at the commit before the promotion and at their candidate copy
  `replays/candidates/stage-b-r2/9p2i` at H (the amendment; the candidate listing above shows it). The partial-record
  principle is stated with its
  sources (decision memo section 1; the 2026-09-24 addendum's "a record covers 50 seeds, not all 300") and its
  mechanisms (the recorder's era refusal;
  `tests/eval/test_eras.py::test_a_registry_filing_samples_9p2i_under_baseline_9_is_refused`). Proof: one era id edited in a scratch copy of section 2 makes the comparison print that row and exit 1.
- [ ] **Every figure of section 3 is read from a committed command at H, count-only.** Mechanism: section 8's figure
  table names, per figure, the audit line stating it and either a `path:line` on a generated page (the scorecard,
  census and profile pages, the route reports, the round records) or a command (`--set-dir DIR --json-stdout` folds,
  `measure_baseline.py`, the route instruments). The script checks that the figure string occurs on the cited line at
  H, or in the command's stdout, and every cited page passes its own `--check` at H (the three publishers,
  `route_check_replay --check`, `route_lines_replay --check`). The section covers each era the registry names, never
  pooled across eras, and round 3's column as its record states it (the step the rule named and the orchestrator's
  decision under 8.8, with the record's section). The featured-games claim is the count-only intersection of
  `FEATURED_GAMES` with the profile JSON's "wrong on what it held" seeds. Proof: one figure edited in a scratch copy
  makes the script exit 1 naming the row; a scratch copy of `docs/gameplay-census.md` with one cell edited fails
  `publish_gameplay_census.py --check`.
- [ ] **Every number in sections 0 to 7 has a row in section 8.** Mechanism: the script extracts each fraction,
  decimal, percentage and "N of M" token from sections 0 to 7 (dates, commit prefixes, seed numbers, section numbers
  and pull request numbers excluded by pattern, and the patterns quoted in Results) and fails on any token with no
  figure row. Proof: "12/34" added to section 3 of a scratch copy makes it exit 1 naming the line.
- [ ] **Role-correctness is reported and never a gate, and the audit says so.** Mechanism: section 4 states it with
  its mechanism, `ProcessScorecard._role_correctness_stays_demoted` (`eval/process_scorecard.py:641`), and the round-3
  step rule's pre-registered conditions, which name no role-reading flag (`tasks/work/stage-b-record-r3.md`, the step
  rule item). The script fails if a line of sections 0 to 3 matching `role-correct|correct ejection|ejection accuracy`
  lacks "reported" in the same sentence. Proof: a role-correct figure moved into section 0 of a scratch copy, without
  that word, gives one hit.
- [ ] **What it does not demonstrate is stated with a source for each limit.** Mechanism: section 4 names (a) one
  recording per round: 50 seeds each (`--expected-seeds 0-49` in each round record's gate), no difference claimed as
  real, any Wilson interval labelled descriptive; (b) the 27B model's route arithmetic: the route field hands the
  model the map's reading and the lab measures only its reach, offline ("reaching is showing a line, not changing a
  vote", `experiments/lab/report-route-lines-replay.md`); the diagnosis's causal headline that the failure was the
  model's arithmetic was refuted (`tasks/diagnosis-2026-10-02/README.md:375-400`); round 3 is one recording, so
  whether a served line changes a vote is read once and not established; (c) the reporter trap: the by-seat cells for each era, the re-keyed flag's bar (21.28, memo 8.7) gating
  nothing, and every reporter a crewmate while impostor self-report stays off (`impostor_openers` reading 0); (d) ML:
  ruling 12 (memo 0.1), the re-pricing precondition dated 2026-10-06 (`training/README.md` section 7), the corpus
  FROZEN line, and `verify_ml_evidence.py` offline FAIL 0. The script's count-only scan of sections 0 to 4 for
  `\b(significant|improv\w*|caus\w*|proves?)\b` prints only lines that negate or quote, each listed in Results with
  its negation or quotation. Proof: "round 3 improved the meeting" planted in a scratch copy gives one hit that is
  neither.
- [ ] **The doctrine table resolves.** Mechanism: section 5 lists each document with its path and the sections used.
  The script checks each in-tree path exists and each cited heading occurs in it (for example `### 8.9` in the decision
  memo), and that the two out-of-tree memos carry the word "advisory" and are the source of no figure (no section 8
  row cites them). Proof: a citation of a section "8.10" makes the script exit 1; a figure row citing the baselines
  memo exits 1.
- [ ] **The ledger is complete.** Mechanism: section 6 has one row per pull request merged into `main` from
  `0755c25d` to B. Its row count equals `git log --first-parent --merges --oneline 0755c25d..B | wc -l` (33 at
  `225d2b77`) plus any fast-forwarded pull request a read-only `gh pr list --repo dkdan10/AiLibi --base main --state
  merged --search 'merged:>=2026-09-19'` names without a merge commit, each such row marked. Each row's card path
  exists at H. Proof: a scratch ledger missing one row makes the count comparison exit 1.
- [ ] **The open items are all there.** Mechanism: the script requires, in section 7, the keys `extract_gameplay_facts`,
  `self-report`, each of `impostor_roll_call`, `reporter_reasoning`, `corroboration_discipline`, `testimony_shapes`,
  `temporal_observations` (`docs/architecture.md:111-114` at `225d2b77`), `evidence_reasoning_version`, `baseline 10`,
  `retire-temporal-evidence-v1`, and each baselines-memo item memo 8.5 leaves undecided (D9, D12, D13, D15 to D18)
  together with the halves the front-door card held (D8-L, D8.1, D9-L), each with its state at H. Each item names who
  decides it and its source `path:line`, resolving at H; the `retire-temporal-evidence-v1` row names it an owner
  confirmation point under D15 ("wait" or "lift the exclusion") and the card's Status at H. The D14 residue is read
  from `retire-era-locked-pins`'s Results ("none" if it left none). Each defect the audit found is filed with its
  `path:line` and the command showing it (at `225d2b77`, `docs/architecture.md:89` against `uv run lint-imports`).
  Proof: one required key deleted from a scratch copy makes the script exit 1 naming it.
- [ ] **The held cards' state at B is a precondition read, not written.** Mechanism: `git log -1 --format=%H --
  tasks/work/rubric-extractor-era.md` at B names the orchestrator's closure commit, whose subject starts `docs:`;
  `git merge-base --is-ancestor <that sha> <the retire-era-locked-pins merge>` exits 0 (the closure landed first);
  the card's Status at B is `done`; `tasks/work/retire-temporal-evidence-v1.md`'s Status at B is `ready`, unless a
  dated owner word on D15 closed it before B, which the audit then cites; and `git log --first-parent --no-merges
  B..H -- tasks/work/rubric-extractor-era.md tasks/work/retire-temporal-evidence-v1.md tasks/post-merge-plan.md
  docs/cleanup-dispositions.md tasks/decision-2026-09-24-stage-b-wave.md tasks/README.md` prints nothing (the
  branch's own commits write none of them). Results and the audit's
  sections 6 and 7 cite the closure sha. Proof: on a scratch branch where the closure commit is not an ancestor, the
  ancestry check exits 1 and the card stops (Constraints, "Stop and ask").
- [ ] **The registry row and the inventory follow the bytes.** Mechanism: `docs/artifacts.md`'s `audits/` row is
  recomputed at H from `git ls-files audits` (count, and the byte sum of those files), and `uv run python
  scripts/verify_ml_evidence.py` (offline, never `--complete`) reports FAIL 0; `validate_task_docs.py` exits 0 at
  every commit of this card's branch. Proof: the committed
  `tests/scripts/test_verify_ml_evidence.py::test_exact_inventory_detects_changed_bytes_with_same_paths` (`:2207`)
  and `tests/scripts/test_work_cards.py::test_flipped_card_status_breaks_the_index` (`:168`) pass; the row left at its
  pre-audit value in a scratch checkout makes the verifier report a FAIL naming `audits/`.
- [ ] **Nothing ships, nothing recorded moves, and CI is the gate record.** Mechanism: `git diff --stat B..H` lists
  only Expected scope's worker files; it is empty over `replays`, `tests`, `eval`, `api`, `frontend`, `scripts`,
  `experiments`, `training`, `engine`, `agents`, `meetings`, `observation`, `orchestrator`, `llm` and `README.md`. The
  demo bundle built at B and at H is identical (`scripts/build_demo_bundle.py --out`, `diff -r`), since audits are
  not baked (`scripts/build_demo_bundle.py:25-37`). CI's green run at H, cited by run id in the pull request and in
  Results, is the gate record (memo 8.7 item 1); no local `check.sh` at H and no card-only gate commit. Proof: a file
  appended to a scratch copy of the head bundle makes `diff -r` print it.
- [ ] **The wave lessons hold at a document's strength.** Mechanism: no production line, constant or test is
  written, so the bounded mutation pass and the planted source-change cases have no target and Results says so; no
  test is weakened (`git diff B..H -- tests` is empty); every number is measured at the head that states it (the
  script runs at H, after the last merge of `main`); no sentence the audit writes about a held card claims more than
  its Status at B. Proof: the script run against a scratch audit whose figures were taken at `225d2b77` fails on the
  ledger count once the finish wave has merged.

## Constraints

**House rules carried.** The engine stays a pure deterministic tick function; replays stay byte-identical within their
recorded scope; `agents/` never imports `engine/`; no module-level mutable state; invalid input raises. This card adds
no code, no `AILIBI_*` lever, no environment switch, no experiment field and no prompt registry or version bump. No
recorded byte is edited, no history is re-scored, and the corpus FROZEN line and every ML artifact stay put
(`verify_ml_evidence.py` offline only, never `--complete`). No live provider call and no recorder run; `.env` is never
read. Every census is count-only, keyed by (set, meeting), and no rendered prompt, transcript text or seed-band prefix
is printed, in the audit or in any log the worker keeps.

**The doctrine, applied to the audit.** It decides nothing and adopts nothing. Owner rulings are quoted verbatim and
dated; orchestrator readings are labelled as readings. Role-correctness is reported beside and never a gate;
wrong-but-believable is the game working and is stated as such; nothing in the audit recommends pushing an agent
toward the correct answer. Claims name their enforcing mechanism; numbers reproduce from committed evidence with the
command in section 8; no number is typed from memory or from an advisory memo. Records are not rewritten: an error the
audit finds in an earlier audit is filed in section 7 as a finding, never edited into that audit.

**Process (memo 8.7).** Document-only: the documentation lens alone verifies it (item 4). CI's green run at the exact
head, cited by run id, is the gate record (item 1). Message-argument mutation survivors do not arise (no code).

**Prerequisites and merge window against round 3's freeze.** Round 3's record (`stage-b-record-r3`) merges first,
which lifts its freeze (this card writes no frozen path, but its figures read the merged state); then
`retire-era-locked-pins` (memo 8.9: the D14 retirement as amended, whose merge waits for the record's); then
`promote-round-3` if the orchestrator takes that step under 8.8; then `front-door-process-first`. One precondition
is the orchestrator's alone: its `docs:` commit closing `rubric-extractor-era` lands before `retire-era-locked-pins`
merges, under the one closure contract the orchestrator holds, which this card does not restate. The
`retire-temporal-evidence-v1` closure is not a precondition: it waits for the owner's D15 word, and the audit lists it
as an owner confirmation point. This card dispatches from B and merges last. If anything merges into `main` between B
and the merge, the worker merges `main`, re-runs the script and every count, updates the figures and the ledger, and
cites the new CI run. The audit's file name carries the date of H.

**One writer per file.** `audits/README.md` and the `audits/` row of `docs/artifacts.md` are also written by the
round-3 record, `retire-era-locked-pins` and `promote-round-3`; this card writes them last, after all of them merge,
and recomputes the row at H. The round-3 audit is the record's, with the orchestrator's step and the promotion's
section appended; this card reads it. `tasks/README.md`, both held cards, `tasks/post-merge-plan.md`,
`docs/cleanup-dispositions.md`, the decision memo and this card's Status line are written only by the orchestrator's
`docs:` commits on `main`; this card writes none of them and contracts none of those commits.

**Delivery and publication.** Branch `work/close-audit-finalized-state`, one pull request into `main`, merged by a
merge commit or a fast-forward, never squashed. Each commit of the branch ends with the trailer
`Card: tasks/work/close-audit-finalized-state.md` immediately followed by `Co-Authored-By: Claude Fable 5.1
<noreply@anthropic.com>`. Nothing ships: audits, task cards
and the dispositions page are not in the demo bundle, and a push to `main` rebuilds the demo identically
(`.github/workflows/pages.yml`). The merge is the orchestrator's once the documentation lens passes and CI is green
at H; the card publishes nothing, and memo 8.9 delegates even the publishing merges of this wave.

**Stop and ask** the orchestrator, writing nothing more, if: a figure the audit needs has no committed command or
page line (state "not reproduced" rather than type it, and ask whether to keep the claim); the record,
`retire-era-locked-pins` or `front-door-process-first` has not merged, or `main` shows a round-3 step that its record
does not name; the `rubric-extractor-era` closure is not on `main`, or landed after `retire-era-locked-pins` merged;
the audit would need to write a held card, the task index or the decision memo; or the lens finds a claim the tree
contradicts in a place this card may not write.

**Out of scope.** `README.md`, the viewer, `docs/history.md`, `docs/glossary.md` and `docs/architecture.md` (its
defect is filed, not fixed); every other audit; the decision memo and the direction document; `tasks/review-ledger.md`;
any code, test, replay, MANIFEST, generated page or lab output.

## Expected scope

Written by the card's worker on `work/close-audit-finalized-state`:
- `audits/audit-<YYYY-MM-DD>-finalized-state.md` (new; sections 0 to 9 as Outcome lists them).
- `audits/README.md`: one row under a new heading after "The Stage-B gameplay wave", and one sentence in the opening
  paragraph pointing a new reader to the audit.
- `docs/artifacts.md`: the `audits/` row only (file count and tracked bytes).
- `tasks/work/close-audit-finalized-state.md`: Results only.

Read by this card at B, written only by the orchestrator's `docs:` commits on `main` (this card contracts none of
them): the `rubric-extractor-era` closure (a precondition), `tasks/work/retire-temporal-evidence-v1.md` (left `ready`
pending the owner's D15 word), `tasks/README.md`'s inventory sentence, `tasks/post-merge-plan.md`,
`docs/cleanup-dispositions.md`, the decision memo, and this card's Status line (`ready`, then `active` at dispatch,
then `done` after the merge).

Scratch only, never committed: `audit_check.py` and its planted copies, under the worker's private scratch
subdirectory; Results quotes the script whole with its sha256.

## Record impact

No recorded byte, behaviour, schema, prompt, stamp or compatibility moves, and no evaluation is run: the audit reads
numbers the tree already produces. What moves: one new class-(b) record under `audits/` and its index row; the
`audits/` registry row. No card's Status moves here. Evidence reasoning versions 1 and 2 stay selectable and
default-off with their four v1 defects on the v1 path (no committed recording selects either), and the gameplay-facts
extractor keeps refusing the shown era by name (`refuse_experiment_settings`), whatever rows `retire-era-locked-pins`
removed from it; the audit lists both as open items. The ladder tip stays where `eval/eras.py` puts it (baseline 9
at `225d2b77`). The demo bundle is unchanged. After merge no CI gate binds the audit's figures; the audit says so in section 9.

## Validation

```sh
uv sync --frozen
env | grep -c '^AILIBI_'                                           # 0
# the gates on the surfaces this card writes
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py                        # offline; FAIL 0; never --complete
uv run pytest tests/scripts/test_check_doc_facts.py tests/scripts/test_work_cards.py \
  tests/scripts/test_verify_ml_evidence.py tests/scripts/test_candidate_sets.py tests/eval/test_eras.py \
  tests/eval/test_process_scorecard.py tests/test_firewall.py -q
# the pages and instruments the audit reads, each bound to the recordings (the route ones need full history)
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/publish_game_profile.py --check
uv run python -m experiments.lab.route_check_replay --check
uv run python -m experiments.lab.route_lines_replay --check
uv run lint-imports
bash scripts/verify_samples.sh
# the era ladder and the registry row, derived
uv run python -c "from eval import eras; print(eras.LADDER_TIP_ERA.id); [print(s.path, s.era.id, s.era.record, s.era.recorded_on, s.era.declared_config) for s in eras.COMMITTED_SETS]"
git ls-files replays/candidates | cut -d/ -f1-3 | sort -u
git ls-files audits | wc -l
git ls-files -z audits | xargs -0 stat -f %z | awk '{s += $1} END {print s}'   # macOS; stat -c %s on Linux
# the ledger
git log --first-parent --merges --format='%h %ad %s' --date=short 0755c25d..HEAD
gh pr list --repo dkdan10/AiLibi --base main --state merged --search 'merged:>=2026-09-19' --limit 200 \
  --json number,mergeCommit                                         # read-only cross-check
# the held cards' state at B, read only
git log -1 --format='%H %s' -- tasks/work/rubric-extractor-era.md                # the orchestrator's docs: closure
git merge-base --is-ancestor <that sha> <the retire-era-locked-pins merge>; echo "exit $?"   # exit 0
grep -h '^\*\*Status:\*\*' tasks/work/rubric-extractor-era.md tasks/work/retire-temporal-evidence-v1.md
git grep -c evidence_reasoning_version -- 'replays/**/experiment-config.json'; echo "exit $?"   # exit 1
git grep -n _cross_era_trajectory; echo "exit $?"                                 # exit 1 once the retirement merged
git ls-files tests/fixtures/phase10 experiments/lab/results-rubric-geomean.stage-b-r2.json
git log --first-parent --no-merges B..HEAD -- tasks/ docs/cleanup-dispositions.md   # only this card's Results
# the audit's own check, then each planted copy named in Acceptance (each exits 1, then the clean run exits 0)
uv run python "$SCRATCH/audit_check.py" audits/audit-<YYYY-MM-DD>-finalized-state.md
# nothing ships
git diff --stat B..HEAD
git diff --stat B..HEAD -- replays tests eval api frontend scripts experiments training engine agents meetings \
  observation orchestrator llm README.md                           # empty
uv run python scripts/build_demo_bundle.py --out "$SCRATCH/bundle-head"   # and at B into bundle-base
diff -r "$SCRATCH/bundle-base" "$SCRATCH/bundle-head"                       # empty
# the house gate: CI's green run at the exact head, cited by run id (memo 8.7 item 1)
```

Every command runs in a bare shell from the repository root of a clean worktree; Results quotes each exit code and
the count it printed.

## Results

Filled at delivery: B, H and the `rubric-extractor-era` closure commit read at B; the script whole with its sha256 and each planted run's exit and
message; each Validation command's exit code and count; the CI run id at H; the sections relied on (this card; the
decision memo 8.7 to 8.9; the direction section 8; `docs/architecture.md` "Enforced boundaries" and "Determinism and
the substrate ladder"); every defect filed in section 7; decisions and limitations.
