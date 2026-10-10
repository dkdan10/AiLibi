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

- [x] **The audit is indexed once, and its index row agrees with the front door and is plain.** Mechanism:
  `uv run python scripts/check_doc_facts.py` exits 0 at H (`check_audits_index`, `check_relative_links`,
  `check_ladder_tip`, `check_repeated_claims`); the row passes `copy_problems`
  (`tests/scripts/test_candidate_sets.py:538`) with 0 problems; a ladder-tip sentence, if any, names the baseline
  `eval/eras.py` `LADDER_TIP_ERA` names. Proof: the
  committed `test_unindexed_audit_detected` (`tests/scripts/test_check_doc_facts.py:4083`),
  `test_audits_index_ladder_tip_drift_detected` (`:2179`), `test_broken_relative_link_detected` (`:4214`) and
  `test_repeated_results_claim_detected` (`:1430`) pass at H; on a scratch copy, the row removed makes
  `check_doc_facts.py` exit 1 naming the file, "baseline 10" in a ladder-tip sentence exits 1, and "6/7" in the row
  gives `copy_problems` one problem.
- [x] **Section 0 reads for a stranger.** Mechanism: the script's count-only scan of section 0 for
  `\b[A-Z]{1,2}[0-9]+(?:\.[0-9]+)?(?:-T[0-9])?\b|\bTask \d|\baudit-|\bPR #` prints 0; each term it uses links to its
  `docs/glossary.md` entry or is defined in the sentence that first uses it, which the lens confirms by listing the
  terms it checked. Proof: "R6" planted in a scratch copy gives one hit naming the line.
- [x] **Every claim of section 1 names its mechanism at the strength delivered.** Mechanism: section 8 holds a claim
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
- [x] **The era ladder is derived, not typed.** Mechanism: section 2's table equals, row for row, a one-line print of
  `eval.eras.COMMITTED_SETS`, `ERAS` and `LADDER_TIP_ERA` (path, era id, record, `recorded_on`, declared config) plus
  `git ls-files replays/candidates | cut -d/ -f1-3 | sort -u` at H; each replaced recording's location is checked
  with `git cat-file -e <commit>:<path>` (exit 0), at least baseline 9's 9p2i at `d41c9006` and, if round 3 was
  promoted, round 2's bytes at the commit before the promotion and at their candidate copy
  `replays/candidates/stage-b-r2/9p2i` at H (the amendment; the candidate listing above shows it). The partial-record
  principle is stated with its
  sources (decision memo section 1; the 2026-09-24 addendum's "a record covers 50 seeds, not all 300") and its
  mechanisms (the recorder's era refusal;
  `tests/eval/test_eras.py::test_a_registry_filing_samples_9p2i_under_baseline_9_is_refused`). Proof: one era id edited in a scratch copy of section 2 makes the comparison print that row and exit 1.
- [x] **Every figure of section 3 is read from a committed command at H, count-only.** Mechanism: section 8's figure
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
- [x] **Every number in sections 0 to 7 has a row in section 8.** Mechanism: the script extracts each fraction,
  decimal, percentage and "N of M" token from sections 0 to 7 (dates, commit prefixes, seed numbers, section numbers
  and pull request numbers excluded by pattern, and the patterns quoted in Results) and fails on any token with no
  figure row. Proof: "12/34" added to section 3 of a scratch copy makes it exit 1 naming the line.
- [x] **Role-correctness is reported and never a gate, and the audit says so.** Mechanism: section 4 states it with
  its mechanism, `ProcessScorecard._role_correctness_stays_demoted` (`eval/process_scorecard.py:641`), and the round-3
  step rule's pre-registered conditions, which name no role-reading flag (`tasks/work/stage-b-record-r3.md`, the step
  rule item). The script fails if a line of sections 0 to 3 matching `role-correct|correct ejection|ejection accuracy`
  lacks "reported" in the same sentence. Proof: a role-correct figure moved into section 0 of a scratch copy, without
  that word, gives one hit.
- [x] **What it does not demonstrate is stated with a source for each limit.** Mechanism: section 4 names (a) one
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
- [x] **The doctrine table resolves.** Mechanism: section 5 lists each document with its path and the sections used.
  The script checks each in-tree path exists and each cited heading occurs in it (for example `### 8.9` in the decision
  memo), and that the two out-of-tree memos carry the word "advisory" and are the source of no figure (no section 8
  row cites them). Proof: a citation of a section "8.10" makes the script exit 1; a figure row citing the baselines
  memo exits 1.
- [x] **The ledger is complete.** Mechanism: section 6 has one row per pull request merged into `main` from
  `0755c25d` to B. Its row count equals `git log --first-parent --merges --oneline 0755c25d..B | wc -l` (33 at
  `225d2b77`) plus any fast-forwarded pull request a read-only `gh pr list --repo dkdan10/AiLibi --base main --state
  merged --search 'merged:>=2026-09-19'` names without a merge commit, each such row marked. Each row's card path
  exists at H. Proof: a scratch ledger missing one row makes the count comparison exit 1.
- [x] **The open items are all there.** Mechanism: the script requires, in section 7, the keys `extract_gameplay_facts`,
  `self-report`, each of `impostor_roll_call`, `reporter_reasoning`, `corroboration_discipline`, `testimony_shapes`,
  `temporal_observations` (`docs/architecture.md:111-114` at `225d2b77`), `evidence_reasoning_version`, `baseline 10`,
  `retire-temporal-evidence-v1`, and each baselines-memo item memo 8.5 leaves undecided (D9, D12, D13, D15 to D18)
  together with the halves the front-door card held (D8-L, D8.1, D9-L), each with its state at H. Each item names who
  decides it and its source `path:line`, resolving at H; the `retire-temporal-evidence-v1` row names it an owner
  confirmation point under D15 ("wait" or "lift the exclusion") and the card's Status at H. The D14 residue is read
  from `retire-era-locked-pins`'s Results ("none" if it left none). Each defect the audit found is filed with its
  `path:line` and the command showing it (at `225d2b77`, `docs/architecture.md:89` against `uv run lint-imports`).
  Proof: one required key deleted from a scratch copy makes the script exit 1 naming it.
- [x] **The held cards' state at B is a precondition read, not written.** Mechanism: `git log -1 --format=%H --
  tasks/work/rubric-extractor-era.md` at B names the orchestrator's closure commit, whose subject starts `docs:`;
  `git merge-base --is-ancestor <that sha> <the retire-era-locked-pins merge>` exits 0 (the closure landed first);
  the card's Status at B is `done`; `tasks/work/retire-temporal-evidence-v1.md`'s Status at B is `ready`, unless a
  dated owner word on D15 closed it before B, which the audit then cites; and `git log --first-parent --no-merges
  B..H -- tasks/work/rubric-extractor-era.md tasks/work/retire-temporal-evidence-v1.md tasks/post-merge-plan.md
  docs/cleanup-dispositions.md tasks/decision-2026-09-24-stage-b-wave.md tasks/README.md` prints nothing (the
  branch's own commits write none of them). Results and the audit's
  sections 6 and 7 cite the closure sha. Proof: on a scratch branch where the closure commit is not an ancestor, the
  ancestry check exits 1 and the card stops (Constraints, "Stop and ask").
- [x] **The registry row and the inventory follow the bytes.** Mechanism: `docs/artifacts.md`'s `audits/` row is
  recomputed at H from `git ls-files audits` (count, and the byte sum of those files), and `uv run python
  scripts/verify_ml_evidence.py` (offline, never `--complete`) reports FAIL 0; `validate_task_docs.py` exits 0 at
  every commit of this card's branch. Proof: the committed
  `tests/scripts/test_verify_ml_evidence.py::test_exact_inventory_detects_changed_bytes_with_same_paths` (`:2207`)
  and `tests/scripts/test_work_cards.py::test_flipped_card_status_breaks_the_index` (`:168`) pass; the row left at its
  pre-audit value in a scratch checkout makes the verifier report a FAIL naming `audits/`.
- [x] **Nothing ships, nothing recorded moves, and CI is the gate record.** Mechanism: `git diff --stat B..H` lists
  only Expected scope's worker files; it is empty over `replays`, `tests`, `eval`, `api`, `frontend`, `scripts`,
  `experiments`, `training`, `engine`, `agents`, `meetings`, `observation`, `orchestrator`, `llm` and `README.md`. The
  demo bundle built at B and at H is identical (`scripts/build_demo_bundle.py --out`, `diff -r`), since audits are
  not baked (`scripts/build_demo_bundle.py:25-37`). CI's green run at H, cited by run id in the pull request and in
  Results, is the gate record (memo 8.7 item 1); no local `check.sh` at H and no card-only gate commit. Proof: a file
  appended to a scratch copy of the head bundle makes `diff -r` print it.
- [x] **The wave lessons hold at a document's strength.** Mechanism: no production line, constant or test is
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

### Delivered (2026-10-10)

Built on `work/close-audit-finalized-state` from `origin/main` at B = `a3b42fd4` (the front door's merge `4a08f2aa`
and the orchestrator's three `docs:` commits `76d1c826`, `49498b0b`, `a3b42fd4`); `main` did not move under the
branch, so nothing was merged in. Pull request #509. Every count was measured at the head that states it, in a bare
shell (`env | grep -c '^AILIBI_'` printed 0) after `uv sync --frozen`; every census was count-only, keyed by (set,
meeting); no rendered prompt, transcript text or seed-band prefix was printed; band 2100-2999 stayed unseen; the
held-out generator was not run; no provider was called and no recorder ran; the untracked `.env` was not read;
`scripts/verify_ml_evidence.py` ran offline only, never with `--complete`. Scratch work stayed under the session
scratchpad (`close-audit-run/`), and nothing from it is committed. The Status line is the orchestrator's on `main`
(Constraints, "One writer per file"); this commit fills Results and the acceptance boxes only.

**Commits.** `8be948fd` the audit, its index row and the `audits/` row; `f24d9ca9` finding 15, the index row's
ladder-tip phrase kept on one line, the cross-era command scoped to Python files, and the row re-derived;
`082868ca` the automated review's four corrections, findings 16 and 13 (its failing seed), and the row; then this
Results commit, H. Each ends with `Card: tasks/work/close-audit-finalized-state.md` immediately followed by
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`, checked with `git log -1 --format=%B` before each push.

**The held cards at B, read and not written.** `git log -1 --format='%H %s' a3b42fd4 --
tasks/work/rubric-extractor-era.md` prints `97549508875c97f46bc33783cdd3c14ad99bae2b docs: apply the extractor card's
closure span correctly`, the orchestrator's closure (opened by `a331ab90`, also `docs:`); `git merge-base --is-ancestor
97549508 84a4509c` exits 0, and so does `a331ab90` against `84a4509c`; Status at B: `done` (extractor), `ready`
(temporal), the same at H. No dated owner word on D15 arrived before B.

**Sections relied on.** This card; the decision memo sections 0, 1, 3.1 to 3.3, 8 (8.1, 8.5, 8.7 to 8.9 with the
amendment of 2026-10-09 and the two dated lines after it); the direction sections 1, 7, 8 and 12 with its addenda;
`docs/architecture.md` "Enforced boundaries" (the import-linter contracts, the planted import, the packet scans; its
"Four" is finding 1) and "Determinism and the substrate ladder" (bytes within the recorded runtime scope, the
recording as a hosted run's boundary, the five live toggles, eras never pooled); round 3's record sections 1 to 12;
the Results of `stage-b-record-r3`, `retire-era-locked-pins`, `promote-round-3` and `front-door-process-first`;
`docs/process-scorecard.md`, `docs/gameplay-census.md`, `docs/game-profile.md`, `docs/experiment-arms.md`,
`eval/eras.py` and the two route reports under `experiments/lab`.

#### Acceptance, item by item

- *Indexed once, plain, agreeing with the front door.* `uv run python scripts/check_doc_facts.py` exits 0 at H. The
  row's prose after its link passes `copy_problems` (`tests/scripts/test_candidate_sets.py:634`) with 0 problems, and
  so does the opening sentence; the row's ladder-tip sentence names baseline 9, `LADDER_TIP_ERA`'s. The four named
  tests (`test_unindexed_audit_detected` `:4418`, `test_audits_index_ladder_tip_drift_detected` `:2507`,
  `test_broken_relative_link_detected` `:4558`, `test_repeated_results_claim_detected` `:1469`, lines at H) pass, 4
  of the 6 named in the run below. On an archived copy of the head: the row removed, `check_doc_facts.py` exits 1 with
  `audits/README.md: audit-2026-10-10-finalized-state.md is not indexed — every top-level audit needs a row, or the
  corpus goes back to being unnavigable.`; "baseline 10" in the row's ladder-tip sentence exits 1 with
  `audits/README.md:438: a 'ladder tip' sentence names baseline 10, but audits/audit-2026-09-22-process-rerecord.md
  records the ladder tip at baseline 9`; "6/7" appended to the row's prose gives `copy_problems` 1 problem. The first
  build wrapped "ladder tip" across a line, and the second plant then exited 0: that is finding 15 (the phrase regex
  has a literal space), so the row keeps the phrase on one line. The opening sentence carries no link, because
  `check_audits_index` counts every link to the file and a second one would index it twice.
- *Section 0 reads for a stranger.* The script's scan of section 0 for the card's pattern prints 0 hits. Planted:
  "R6" in a scratch copy gives one hit, `FAIL section 0 label: line 67: 'R6'`. Terms the lens checked, each linked to
  `docs/glossary.md` or defined in the sentence that first uses it: crewmate and impostor, meeting, ballot (eject or
  skip), tick, replay, deterministic engine, scripted rules, the model, owner (glossary link), the shown 9-player set,
  a line the voter held (a statement made at the table or an observation in its own memory), a floor, the engine's
  own record of where each player stood, reported and never penalised, a wrong vote on believable data, import rules
  and planted-leak checks, a round of changes, the route line (a plain line saying which stated moves the doors
  allow), general social deduction, the machine-learning program, and the three generated pages, each described where
  it is linked.
- *Every claim of section 1 names its mechanism at the strength delivered.* Section 8.2 holds nine claim rows; the
  script checks each mechanism path with `git ls-files --error-unmatch`, collects the eight test node ids with `uv run
  pytest --collect-only -q`, and runs every claim command to exit 0 (`lint`, `verify-samples`, `firewall-test`,
  `role-test`, `eras-test` among them). The wording holds at the mechanism's strength: the firewall "bounded checks,
  not complete privacy assurance" (`README.md:22`), a valid citation resolvable, not supported (`README.md:33`),
  determinism within the recorded runtime scope (`docs/architecture.md:105-106`), the tactical rule held by review
  with no import gate, "labels and never rewrites" true of the grounding label and not of the teammate firewall, and
  era separation claimed for the instruments the registry names, not for every instrument (finding 16).
  Planted: a claim row naming `tests/eval/test_eras.py::test_no_such_case` exits 1 with `FAIL claim table: row eras:
  test node tests/eval/test_eras.py::test_no_such_case does not collect`; a paragraph "The firewall guarantees no
  leak." added to section 1 exits 1 with `FAIL section 1: paragraph at line 118 ends with no claim-row reference:
  'The firewall guarantees no leak.'`.
- *The era ladder is derived, not typed.* Section 2.1's table equals, row for row, `era-ladder`'s print at H (`tip
  baseline-9`, then the four `COMMITTED_SETS` rows with path, era id, record, `recorded_on` and declared config), and
  section 2.2 equals `git ls-files replays/candidates | cut -d/ -f1-3 | sort -u` (three paths: the family README,
  `stage-b-r1`, `stage-b-r2`). `git cat-file -e` exits 0 on `d41c9006:replays/samples/9p2i` (baseline 9),
  `2eed2e92:replays/samples/9p2i` (round 2 before the promotion), `HEAD:replays/candidates/stage-b-r2/9p2i` (round 2's
  candidate copy) and `2eed2e92:replays/candidates/stage-b-r3/9p2i` (round 3's retired copy). The partial-record
  principle is stated with the owner's words of 2026-09-24, the memo's section 1, the addendum's "a record covers 50
  seeds, not all 300", the recorder's era refusal and the planted registry test. Planted: `stage-b-r3` edited to
  `stage-b-r2` in section 2.1 exits 1 with `FAIL era ladder: row 2: table [...'stage-b-r2'...] against printed
  [...'stage-b-r3'...]`.
- *Every figure of section 3 is read from a committed command at H, count-only.* Section 8.3 holds 129 figure rows,
  each naming the audit section that states it and a `path:line` or a section-8.1 command; the script finds each
  figure in its section and on its source line or in its command's stdout, and runs the `--check` of every cited
  page: the scorecard, census and profile publishers and both route instruments, five pages, each exit 0. Section 3
  covers baseline-9, stage-b-r3 and stage-b-r2 (the registry's three `Era` constants; `ERAS` holds the two with a
  committed set), never pooled; round 3's column is read as its record states it, the step its rule named (record
  section 8.7, `audits/audit-2026-10-09-stage-b-r3.md:1985`) and the orchestrator's decision under memo 8.8 (record
  section 11, labelled a reading). The featured-games claim is `featured 9p2i 2; wrong on what it held 14; both 0`.
  Planted: `394/397` edited to `395/397` in section 3.1 exits 1 with `FAIL figure table: row 1: '394/397 = 0.9924' is
  not in section 3.1` and `FAIL number without a figure row: line 262 (fraction): '395/397'`. With the shown set's
  holds-nothing cell edited from `0/235` to `1/235` in the worktree (restored after, `git status` clean),
  `publish_gameplay_census.py --check` exits 1 with `docs/gameplay-census.md is STALE: it does not match a
  recomputation from the committed recordings`, and exits 0 on the restored page.
- *Every number in sections 0 to 7 has a row in section 8.* The scan reads 177 tokens in sections 0 to 7 and every
  one is covered by a figure row stated in its section. The patterns, quoted from the script: tokens are fractions
  `(?<![\w./,-])\d+(?:,\d{3})* ?/ ?\d+(?:,\d{3})*(?![\w/]|\.\d|,\d)`, "N of M" `(?<![\w.,])\d+(?:,\d{3})* of
  \d+(?:,\d{3})*(?![\w]|\.\d|,\d)`, percentages `(?<![\w.,])\d+(?:\.\d+)?%` and decimals
  `(?<![\w./,])\d+\.\d+(?![\w%]|\.\d)`; excluded before the scan are code spans, link targets, ISO dates, section
  references (`§`, "section", "sections", "subsection", "memo", "item", "ruling", "part", "addendum" followed by
  numbers joined by commas, "and", "to", "or" or hyphens), heading lines and fenced blocks. Seed numbers, commit
  prefixes and pull request numbers are not tokens by those patterns (or sit in code spans). Planted: "A planted count
  reads 12/34." in section 3 exits 1 with `FAIL number without a figure row: line 304 (fraction): '12/34'`.
- *Role-correctness is reported and never a gate, and the audit says so.* Section 4 states it with
  `ProcessScorecard._role_correctness_stays_demoted` (`eval/process_scorecard.py:623`) and the round-3 step rule's
  conditions (`tasks/work/stage-b-record-r3.md:249-255`). The scan of sections 0 to 3 prints 0 hits without
  "reported". Planted: "Role-correct ejections read 46/61." moved into section 0 gives one hit, `FAIL role-correct
  without reported: section 0, near line 57`.
- *What it does not demonstrate, with a source for each limit.* Section 4 names one recording per round (each round
  record's gate line, `--expected-seeds 0-49`, `audits/audit-2026-09-27-stage-b-r1.md:943`,
  `audits/audit-2026-10-01-stage-b-r2.md:1178`, `audits/audit-2026-10-09-stage-b-r3.md:1695`), the intervals labelled
  descriptive; the 27B model's route arithmetic (the lab's reach only, "Reaching is showing a line, not changing a
  vote", and the refuted causal headline, `tasks/diagnosis-2026-10-02/README.md:374-379`); the reporter trap by seat
  per era, the bar 21.28 gating nothing, every reporter a crewmate while self-report stays off (`0/119 by
  construction`); and ML (ruling 12 verbatim, the precondition of 2026-10-06 in `training/README.md` section 7, the
  FROZEN lines, `FAIL 0` offline). The claim-word scan of sections 0 to 4 prints one hit, `'causal', section 4:
  quoted` (inside the refuter's quoted verdict, which also negates it). Planted: "Round 3 improved the meeting." gives
  one hit that is neither, `FAIL claim word: section 3, near line 304: 'improved'`.
- *The doctrine table resolves.* Section 5 lists seven documents; the script finds every cited anchor at the start of
  a line of its in-tree file (`### 8.9` and the three dated paragraph starts of the memo among them) and both
  out-of-tree memos labelled advisory, with no figure row citing either. Planted: `### 8.10` added to the memo's
  anchors exits 1 with `FAIL doctrine: line 483: tasks/decision-2026-09-24-stage-b-wave.md has no line starting
  '### 8.10'`; a figure row citing `baselines-2026-10-03/baselines-memo.md:100` exits 1 with `FAIL figure table: row
  1b: cites baselines-2026-10-03/baselines-memo.md:100, outside the tree`.
- *The ledger is complete.* `git log --first-parent --merges --oneline 0755c25d..a3b42fd4 | wc -l` prints 37 (36
  before the front door, then #508); the ledger has 37 rows, each merge commit the first-parent merge of its pull
  request and each card path tracked at H. The read-only `gh pr list --repo dkdan10/AiLibi --base main --state merged
  --search 'merged:>=2026-09-19' --limit 200 --json number,mergeCommit` lists the same 37 numbers (#471 to #508, less
  #478), each with its merge commit, so no row is a fast-forward. Planted: the #490 row removed exits 1 with `FAIL
  ledger: missing row: #490 merged as 4b1e9a01` and `36 rows against 37 first-parent merges plus 0 fast-forwards`.
- *The open items are all there.* Section 7.1 holds all twenty required keys and two more (D7, D14), each with its
  state at H, who decides it and a source `path:line` whose anchor the script finds on that line at H; the
  `retire-temporal-evidence-v1` row names D15 ("wait" or "lift the exclusion") and its Status at H, `ready`. The D14
  residue is read from the retirement card's Results (`tasks/work/retire-era-locked-pins.md:582`, classed and kept)
  and its Constraints (`:282`, G28 waits on D15). Sixteen defects are filed in section 7.4, each with its `path:line`
  and its showing command. Planted: the `testimony_shapes` row deleted exits 1 with `FAIL open items: required key
  testimony_shapes is missing`.
- *The held cards' state at B is read, not written.* Above, under "The held cards at B". `git log --first-parent
  --no-merges a3b42fd4..HEAD -- tasks/work/rubric-extractor-era.md tasks/work/retire-temporal-evidence-v1.md
  tasks/post-merge-plan.md docs/cleanup-dispositions.md tasks/decision-2026-09-24-stage-b-wave.md tasks/README.md`
  prints nothing. Planted: with `76270d6c` (an earlier merge) in place of the retirement merge, `git merge-base
  --is-ancestor 97549508 76270d6c` exits 1, the case in which the card stops.
- *The registry row and the inventory follow the bytes.* The `audits/` row is recomputed from the index at each commit
  that moves audits bytes (`git ls-files audits | wc -l`, and the blob sizes of `git ls-files -s audits` through `git
  cat-file --batch-check='%(objectsize)'`, which equal the `stat -f %z` sum): 31,595,671 / 335 at B, 31,664,615 / 336
  at `8be948fd`, 31,665,710 / 336 at `f24d9ca9`, 31,668,929 / 336 at `082868ca` and at H. Offline `verify_ml_evidence.py`: 64 checks, 52 OK, 0 FAIL,
  7 ABSENT, 5 INFO, exit 0. `validate_task_docs.py` exits 0 at every commit of the branch.
  `test_exact_inventory_detects_changed_bytes_with_same_paths` (`tests/scripts/test_verify_ml_evidence.py:2207`) and
  `test_flipped_card_status_breaks_the_index` (`tests/scripts/test_work_cards.py:168`) pass. Planted: the row left at
  its pre-audit value in the worktree (restored after, `git status` clean) makes the verifier exit 1 with `[ FAIL ]
  in-tree family inventory` and `audits/: docs/artifacts.md promises 335 files, the index tracks 336`.
- *Nothing ships, nothing recorded moves, and CI is the gate record.* `git diff --stat a3b42fd4..HEAD` lists
  `audits/README.md`, `audits/audit-2026-10-10-finalized-state.md`, `docs/artifacts.md` and this card; over `replays
  tests eval api frontend scripts experiments training engine agents meetings observation orchestrator llm README.md`
  it prints nothing. The demo bundle built at B (the clean worktree at `a3b42fd4`, before any edit), at `f24d9ca9`
  and again at `082868ca` (this commit changes only the card, which is not baked): 110 files each, `diff -r` exit 0
  both times. Planted: a file appended
  to a copy of the head bundle makes `diff -r` print `Only in .../bundle-plant: planted.txt`, exit 1. CI is the gate
  record (memo 8.7 item 1): run 38040036120 at `f24d9ca9`, success (Project checks 10,822 passed, 40 skipped, 3 xfailed; Frontend checks with vitest 821 passed; Frontend
  e2e 15 passed), and run 38042437327, success with the same counts, at `082868ca`; the run at H is cited by run id in the pull
  request body, since a commit cannot name its own run, and no card-only gate commit is added. No local `check.sh` ran
  at H.
- *The wave lessons hold at a document's strength.* No production line, constant or test is written, so the bounded
  mutation pass and the planted source-change cases have no target; `git diff a3b42fd4..HEAD -- tests` is empty. The
  script ran at H after the last edit; `main` did not move. No sentence about a held card claims more than its Status
  at B. Planted: a scratch audit with B stated as `225d2b77` and its ledger cut to that head's 33 rows exits 1 with
  `FAIL ledger: stated B 225d2b77 against merge-base a3b42fd4`, four `missing row` lines (#505 to #508) and `33 rows
  against 37 first-parent merges plus 0 fast-forwards`.

#### The script

`audit_check.py`, run from the repository root as `python3 audit_check.py
audits/audit-2026-10-10-finalized-state.md` (full) or with `--fast` (skipping the `slow-` commands and the claim
commands, used for the planted copies); sha256 `27ef870ddf084bb1b23feda114a3d92e66478808eb4ef92063d3aae8cc92750f`. The full run at H: exit 0, `audit_check: 0 failures`, with
section 0's scan 0, nine claim rows and eight test nodes, four sets, three candidate paths and four replaced
locations, 129 figure rows over five cited pages, 177 tokens, no role-correct line without "reported", one claim word
(quoted), seven doctrine rows with two advisory memos, 37 ledger rows against 37 merges, 22 open items against 20
required keys, 16 findings, and every one of its 44 commands exit 0. In the final run, at `082868ca`, each planted copy
above exited 1 with only its own failure lines (`plant.py`, scratch). An earlier run, before finding 13's command
was pinned to a seed, also printed `row 119: '1 passed' is not in the stdout of flaky-alone` on the
firewall-paragraph copy: the unseeded case failed once, the flake the finding files.

````python
#!/usr/bin/env python3
"""Count-only check of the close audit against the tree at HEAD.

Scratch for tasks/work/close-audit-finalized-state.md; never committed. Run from
the repository root:

    python3 audit_check.py audits/audit-<date>-finalized-state.md [--fast]

It parses the audit's section 8 tables (commands, claims, figures), section 2's
era tables, section 5's doctrine table, section 6's ledger and section 7's open
items and findings, and exits 1 naming the row on any miss. ``--fast`` skips the
commands whose id starts with ``slow-`` and the claim commands; the clean run at
the head is the full run. Nothing is printed from a recording: every command the
audit quotes is count-only.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

DIRECTION_COMMIT = "0755c25d"
REQUIRED_KEYS = (
    "extract_gameplay_facts",
    "self-report",
    "impostor_roll_call",
    "reporter_reasoning",
    "corroboration_discipline",
    "testimony_shapes",
    "temporal_observations",
    "evidence_reasoning_version",
    "baseline 10",
    "retire-temporal-evidence-v1",
    "D9",
    "D12",
    "D13",
    "D15",
    "D16",
    "D17",
    "D18",
    "D8-L",
    "D8.1",
    "D9-L",
)
OUT_OF_TREE_MEMOS = ("baselines-memo", "rubric-design-memo")
PAGE_CHECKS = {
    "docs/process-scorecard.md": "scorecard-check",
    "docs/gameplay-census.md": "census-check",
    "docs/game-profile.md": "profile-check",
    "replays/samples/9p2i/results-game-profile.json": "profile-check",
    "experiments/lab/report-route-check-replay.md": "slow-route-check",
    "experiments/lab/results-route-check-replay.json": "slow-route-check",
    "experiments/lab/report-route-lines-replay.md": "slow-route-lines",
    "experiments/lab/results-route-lines-replay.json": "slow-route-lines",
}
CLAIM_COMMANDS_REQUIRED = ("lint", "verify-samples", "firewall-test", "role-test", "eras-test")

STRANGER = re.compile(r"\b[A-Z]{1,2}[0-9]+(?:\.[0-9]+)?(?:-T[0-9])?\b|\bTask \d|\baudit-|\bPR #")
NUM = r"\d+(?:,\d{3})*"
TOKENS = (
    ("fraction", re.compile(rf"(?<![\w./,-]){NUM} ?/ ?{NUM}(?![\w/]|\.\d|,\d)")),
    ("N of M", re.compile(rf"(?<![\w.,]){NUM} of {NUM}(?![\w]|\.\d|,\d)")),
    ("percentage", re.compile(r"(?<![\w.,])\d+(?:\.\d+)?%")),
    ("decimal", re.compile(r"(?<![\w./,])\d+\.\d+(?![\w%]|\.\d)")),
)
EXCLUSIONS = (
    ("code span", re.compile(r"`[^`\n]*`")),
    ("link target", re.compile(r"\]\([^)\s]*\)")),
    ("ISO date", re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),
    (
        "section reference",
        re.compile(
            r"(?:§\s?|\b(?:sections?|subsections?|memo|items?|rulings?|parts?|addendum|addenda)\s+)"
            r"\d+(?:\.\d+)*(?:\s*(?:,|and|to|or|-)\s*\d+(?:\.\d+)*)*",
            re.IGNORECASE,
        ),
    ),
)
ROLE_WORDS = re.compile(r"role-correct|correct ejection|ejection accuracy", re.IGNORECASE)
CLAIM_WORDS = re.compile(r"\b(significant|improv\w*|caus\w*|proves?)\b", re.IGNORECASE)
NEGATION = re.compile(
    r"\b(not|no|never|nor|neither|none|cannot|without|refuted|unmeasured|unestablished)\b",
    re.IGNORECASE,
)
QUOTES = re.compile(r"\"[^\"]*\"|“[^”]*”")
SENTENCE_BREAK = re.compile(r"(?<=[.;!?])\s+(?=[A-Z(\[*`\"“])")


@dataclass
class Report:
    failures: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def fail(self, check: str, detail: str) -> None:
        self.failures.append(f"FAIL {check}: {detail}")

    def note(self, line: str) -> None:
        self.notes.append(line)


def run(command: str, timeout: int = 1800) -> tuple[int, str]:
    result = subprocess.run(
        ["bash", "-c", command], capture_output=True, text=True, timeout=timeout
    )
    return result.returncode, result.stdout + result.stderr


def git(*args: str) -> tuple[int, str]:
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    return result.returncode, result.stdout


def collapse(text: str) -> str:
    return " ".join(text.replace("**", "").split())


@dataclass
class Audit:
    lines: list[str]

    def section_of(self) -> list[tuple[str, str]]:
        """Per line, (top section, subsection) keys; '' before section 0."""

        keys: list[tuple[str, str]] = []
        top, sub = "", ""
        for line in self.lines:
            top_match = re.match(r"^## (\d+)\. ", line)
            sub_match = re.match(r"^### (\d+\.\d+) ", line)
            if top_match:
                top, sub = top_match.group(1), ""
            elif sub_match:
                sub = sub_match.group(1)
            keys.append((top, sub))
        return keys

    def numbered(self, key: str) -> list[tuple[int, str]]:
        """(1-based line number, text) of every line in section or subsection ``key``."""

        out = []
        for number, (line, (top, sub)) in enumerate(zip(self.lines, self.section_of()), 1):
            if (("." in key) and sub == key) or (("." not in key) and top == key):
                out.append((number, line))
        return out

    def text(self, key: str) -> str:
        return "\n".join(line for _, line in self.numbered(key))


def split_cells(line: str) -> list[str]:
    """The cells of one pipe-table line; an escaped ``\\|`` stays inside its cell."""

    return [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def tables_under(audit: Audit, key: str, first_header: str) -> list[tuple[int, list[str]]]:
    """Body rows of the tables in ``key`` whose first header cell is ``first_header``.

    A table is a run of consecutive lines starting with ``|``: its first line is
    the header, its second the rule, and the rest are its body rows.
    """

    rows: list[tuple[int, list[str]]] = []
    table: list[tuple[int, str]] = []
    for number, line in audit.numbered(key) + [(0, "")]:
        if line.startswith("|"):
            table.append((number, line))
            continue
        if len(table) >= 2 and split_cells(table[0][1])[0] == first_header:
            rows.extend((n, split_cells(text)) for n, text in table[2:])
        table = []
    return rows


def code_spans(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)


def parse_commands(audit: Audit, report: Report) -> dict[str, str]:
    commands: dict[str, str] = {}
    inside = False
    for _, line in audit.numbered("8.1"):
        if line.startswith("```"):
            inside = not inside
            continue
        if inside:
            match = re.match(r"^([a-z0-9-]+): (.+)$", line)
            if not match:
                report.fail("commands", f"unparsed line {line!r}")
                continue
            if match.group(1) in commands:
                report.fail("commands", f"duplicate id {match.group(1)}")
            commands[match.group(1)] = match.group(2)
    if not commands:
        report.fail("commands", "section 8.1 holds no command block")
    return commands


class Runner:
    def __init__(self, commands: dict[str, str], fast: bool, report: Report) -> None:
        self.commands = commands
        self.fast = fast
        self.report = report
        self.cache: dict[str, tuple[int, str] | None] = {}

    def output(self, command_id: str) -> tuple[int, str] | None:
        if command_id not in self.commands:
            self.report.fail("commands", f"no command {command_id}")
            return None
        if command_id not in self.cache:
            if self.fast and command_id.startswith("slow-"):
                self.cache[command_id] = None
            else:
                self.cache[command_id] = run(self.commands[command_id])
        return self.cache[command_id]


def check_stranger(audit: Audit, report: Report) -> None:
    hits = 0
    for number, line in audit.numbered("0"):
        for match in STRANGER.finditer(line):
            hits += 1
            report.fail("section 0 label", f"line {number}: {match.group(0)!r}")
    report.note(f"section 0 label scan: {hits} hits")


def paragraphs(lines: list[tuple[int, str]]) -> Iterator[tuple[int, str]]:
    block: list[tuple[int, str]] = []
    fenced = False
    for number, line in lines + [(0, "")]:
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if not line.strip() or line.startswith("#") or line.startswith("|"):
            if block:
                yield block[0][0], " ".join(text for _, text in block)
            block = []
            continue
        block.append((number, line.strip()))


def check_claims(audit: Audit, runner: Runner, report: Report) -> None:
    rows = tables_under(audit, "8.2", "claim row")
    keys: dict[str, list[str]] = {}
    for number, cells in rows:
        if len(cells) != 5:
            report.fail("claim table", f"line {number}: {len(cells)} cells, not 5")
            continue
        key = code_spans(cells[0])
        if not key:
            report.fail("claim table", f"line {number}: no key")
            continue
        keys[key[0]] = cells
    referenced: set[str] = set()
    for start, paragraph in paragraphs(audit.numbered("1")):
        match = re.search(r"\(claim row `([a-z-]+)`\)\s*$", paragraph)
        if not match:
            report.fail("section 1", f"paragraph at line {start} ends with no claim-row reference: {paragraph[:70]!r}")
            continue
        if match.group(1) not in keys:
            report.fail("section 1", f"paragraph at line {start} names claim row {match.group(1)}, which section 8.2 lacks")
        referenced.add(match.group(1))
    for key in sorted(set(keys) - referenced):
        report.fail("claim table", f"row {key} is referenced by no section-1 paragraph")
    node_ids: dict[str, str] = {}
    for key, cells in keys.items():
        for path in code_spans(cells[2]):
            if git("ls-files", "--error-unmatch", path)[0] != 0:
                report.fail("claim table", f"row {key}: mechanism path {path} is not tracked at HEAD")
        for node in code_spans(cells[3]):
            node_ids[node] = key
        for command_id in code_spans(cells[4]):
            if command_id not in runner.commands:
                report.fail("claim table", f"row {key}: no command {command_id}")
            elif not runner.fast:
                result = runner.output(command_id)
                if result is not None and result[0] != 0:
                    report.fail("claim table", f"row {key}: command {command_id} exited {result[0]}")
    used_commands = {c for cells in keys.values() for c in code_spans(cells[4])}
    for command_id in CLAIM_COMMANDS_REQUIRED:
        if command_id not in used_commands:
            report.fail("claim table", f"no row runs the required command {command_id}")
    if node_ids:
        code, _ = run("uv run pytest --collect-only -q -p no:cacheprovider " + " ".join(f"'{n}'" for n in node_ids))
        if code != 0:
            for node, key in node_ids.items():
                if run(f"uv run pytest --collect-only -q -p no:cacheprovider '{node}'")[0] != 0:
                    report.fail("claim table", f"row {key}: test node {node} does not collect")
    report.note(f"claim table: {len(keys)} rows, {len(node_ids)} test nodes, {len(referenced)} paragraphs referenced")


def check_eras(audit: Audit, runner: Runner, report: Report) -> None:
    result = runner.output("era-ladder")
    if result is None or result[0] != 0:
        report.fail("era ladder", "the era-ladder command did not run")
        return
    printed = [line.split() for line in result[1].strip().splitlines()]
    tip_line = [p for p in printed if p and p[0] == "tip"]
    sets = [p for p in printed if p and p[0] != "tip"]
    stated_tip = re.search(r"Ladder tip: `([^`]+)`", audit.text("2.1"))
    if not tip_line or not stated_tip or stated_tip.group(1) != tip_line[0][1]:
        report.fail("era ladder", f"stated tip {stated_tip.group(1) if stated_tip else None} against printed {tip_line}")
    rows = tables_under(audit, "2.1", "committed set")
    table = [[(code_spans(c) or [c])[0] for c in cells] for _, cells in rows]
    if len(table) != len(sets):
        report.fail("era ladder", f"{len(table)} table rows against {len(sets)} printed")
    for index, (row, line) in enumerate(zip(table, sets)):
        if row != line:
            report.fail("era ladder", f"row {index + 1}: table {row} against printed {line}")
    result = runner.output("candidates")
    listed = sorted(result[1].split()) if result else []
    stated = sorted((code_spans(cells[0]) or [cells[0]])[0] for _, cells in tables_under(audit, "2.2", "candidate path"))
    if listed != stated:
        report.fail("candidates", f"table {stated} against git ls-files {listed}")
    located = tables_under(audit, "2.3", "recording")
    for number, cells in located:
        spans = code_spans(cells[1])
        if not spans:
            report.fail("replaced recordings", f"line {number}: no location")
            continue
        if git("cat-file", "-e", spans[0])[0] != 0:
            report.fail("replaced recordings", f"line {number}: git cat-file -e {spans[0]} exits non-zero")
    report.note(f"era ladder: {len(table)} sets, {len(stated)} candidate paths, {len(located)} replaced locations")


def check_figures(audit: Audit, runner: Runner, report: Report) -> list[tuple[str, list[str]]]:
    rows = tables_under(audit, "8.3", "figure row")
    figures: list[tuple[str, list[str]]] = []
    cited_pages: set[str] = set()
    for number, cells in rows:
        if len(cells) != 4:
            report.fail("figure table", f"line {number}: {len(cells)} cells, not 4")
            continue
        row_id = cells[0].strip("`")
        figure_spans = code_spans(cells[1])
        if not figure_spans:
            report.fail("figure table", f"row {row_id}: no figure")
            continue
        figure = figure_spans[0]
        stated = [s.strip() for s in cells[2].split(",") if s.strip()]
        figures.append((figure, stated))
        for key in stated:
            if collapse(figure) not in collapse(audit.text(key)):
                report.fail("figure table", f"row {row_id}: {figure!r} is not in section {key}")
        source = (code_spans(cells[3]) or [cells[3]])[0]
        if any(memo in source for memo in OUT_OF_TREE_MEMOS) or source.startswith(("/", "..")):
            report.fail("figure table", f"row {row_id}: cites {source}, outside the tree")
            continue
        if source.startswith("cmd:"):
            result = runner.output(source[4:])
            if result is None:
                continue
            if collapse(figure) not in collapse(result[1]):
                report.fail("figure table", f"row {row_id}: {figure!r} is not in the stdout of {source[4:]}")
            continue
        match = re.fullmatch(r"(.+):(\d+)(?:-(\d+))?", source)
        if not match:
            report.fail("figure table", f"row {row_id}: unparsed source {source!r}")
            continue
        path, first, last = match.group(1), int(match.group(2)), int(match.group(3) or match.group(2))
        if git("ls-files", "--error-unmatch", path)[0] != 0:
            report.fail("figure table", f"row {row_id}: {path} is not tracked at HEAD")
            continue
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        span = collapse(" ".join(lines[first - 1 : last]))
        if collapse(figure) not in span:
            report.fail("figure table", f"row {row_id}: {figure!r} is not on {path}:{first}{'-' + str(last) if last != first else ''}")
        if path in PAGE_CHECKS:
            cited_pages.add(path)
    for page in sorted(cited_pages):
        result = runner.output(PAGE_CHECKS[page])
        if result is not None and result[0] != 0:
            report.fail("page check", f"{page}: {PAGE_CHECKS[page]} exited {result[0]}")
    report.note(f"figure table: {len(figures)} rows; pages cited {len(cited_pages)}")
    return figures


def scrub(line: str) -> str:
    for _, pattern in EXCLUSIONS:
        line = pattern.sub(" ", line)
    return line


def check_tokens(audit: Audit, figures: list[tuple[str, list[str]]], report: Report) -> None:
    keys = audit.section_of()
    fenced = False
    count = 0
    for number, (line, (top, sub)) in enumerate(zip(audit.lines, keys), 1):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced or top not in {str(n) for n in range(8)} or line.startswith("#"):
            continue
        text = scrub(line)
        for kind, pattern in TOKENS:
            for match in pattern.finditer(text):
                token = match.group(0)
                count += 1
                covered = any(
                    re.search(rf"(?<![\w./,]){re.escape(token)}(?![\w]|,\d|\.\d)", figure)
                    and any(key in (top, sub) for key in stated)
                    for figure, stated in figures
                )
                if not covered:
                    report.fail("number without a figure row", f"line {number} ({kind}): {token!r}")
    report.note(f"number scan, sections 0 to 7: {count} tokens")


def units(lines: list[tuple[int, str]]) -> Iterator[tuple[int, str]]:
    for number, line in lines:
        if line.startswith("|"):
            yield number, line
    for start, paragraph in paragraphs(lines):
        for sentence in SENTENCE_BREAK.split(paragraph):
            yield start, sentence


def check_role_and_claim_words(audit: Audit, report: Report) -> None:
    role_hits = 0
    for key in ("0", "1", "2", "3"):
        for start, unit in units(audit.numbered(key)):
            if ROLE_WORDS.search(unit) and "reported" not in unit.lower():
                role_hits += 1
                report.fail("role-correct without reported", f"section {key}, near line {start}: {unit[:80]!r}")
    report.note(f"role-correct scan, sections 0 to 3: {role_hits} hits without 'reported'")
    for key in ("0", "1", "2", "3", "4"):
        for start, unit in units(audit.numbered(key)):
            for match in CLAIM_WORDS.finditer(unit):
                quoted = any(q.start() <= match.start() < q.end() for q in QUOTES.finditer(unit))
                negated = bool(NEGATION.search(unit))
                kind = "quoted" if quoted else "negated" if negated else "NEITHER"
                report.note(f"claim word {match.group(0)!r}, section {key}, near line {start}: {kind}")
                if kind == "NEITHER":
                    report.fail("claim word", f"section {key}, near line {start}: {match.group(0)!r} in {unit[:80]!r}")


def check_doctrine(audit: Audit, report: Report) -> None:
    rows = tables_under(audit, "5", "document")
    outside = 0
    for number, cells in rows:
        if len(cells) != 4:
            report.fail("doctrine", f"line {number}: {len(cells)} cells, not 4")
            continue
        if "outside the tree" in cells[1]:
            outside += 1
            if "advisory" not in cells[3].lower():
                report.fail("doctrine", f"line {number}: an out-of-tree memo not labelled advisory")
            continue
        paths = code_spans(cells[1])
        if not paths or git("ls-files", "--error-unmatch", paths[0])[0] != 0:
            report.fail("doctrine", f"line {number}: {paths} is not tracked at HEAD")
            continue
        text = Path(paths[0]).read_text(encoding="utf-8").splitlines()
        for anchor in code_spans(cells[2]):
            if not any(line.lstrip().startswith(anchor) for line in text):
                report.fail("doctrine", f"line {number}: {paths[0]} has no line starting {anchor!r}")
    if outside != 2:
        report.fail("doctrine", f"{outside} out-of-tree memos listed, not 2")
    report.note(f"doctrine table: {len(rows)} rows, {outside} advisory memos outside the tree")


def check_ledger(audit: Audit, report: Report) -> None:
    code, base = git("merge-base", "HEAD", "origin/main")
    base = base.strip()
    stated = re.search(r"B is `([0-9a-f]{7,40})`", audit.text("6"))
    if code != 0 or not stated or not base.startswith(stated.group(1)):
        report.fail("ledger", f"stated B {stated.group(1) if stated else None} against merge-base {base[:8]}")
    _, log = git("log", "--first-parent", "--merges", "--format=%h %s", f"{DIRECTION_COMMIT}..{base}")
    merges = {}
    for line in log.splitlines():
        sha, subject = line.split(" ", 1)
        match = re.search(r"#(\d+)", subject)
        merges[sha[:8]] = match.group(1) if match else ""
    rows = tables_under(audit, "6", "pull request")
    seen: set[str] = set()
    fast_forward = 0
    for number, cells in rows:
        if len(cells) != 5:
            report.fail("ledger", f"line {number}: {len(cells)} cells, not 5")
            continue
        pr = cells[0].lstrip("#")
        card = (code_spans(cells[1]) or [""])[0]
        sha = (code_spans(cells[2]) or [""])[0][:8]
        if git("ls-files", "--error-unmatch", card)[0] != 0:
            report.fail("ledger", f"#{pr}: card {card} is not tracked at HEAD")
        if "fast-forward" in cells[4]:
            fast_forward += 1
            continue
        if merges.get(sha) != pr:
            report.fail("ledger", f"#{pr}: {sha} is not its first-parent merge into main")
        seen.add(sha)
    for sha, pr in merges.items():
        if sha not in seen:
            report.fail("ledger", f"missing row: #{pr} merged as {sha}")
    if len(rows) != len(merges) + fast_forward:
        report.fail("ledger", f"{len(rows)} rows against {len(merges)} first-parent merges plus {fast_forward} fast-forwards")
    report.note(f"ledger: {len(rows)} rows, {len(merges)} first-parent merges from {DIRECTION_COMMIT} to {base[:8]}")


def check_open_items(audit: Audit, runner: Runner, report: Report) -> None:
    rows = tables_under(audit, "7", "open item")
    found: dict[str, list[str]] = {}
    for number, cells in rows:
        if len(cells) != 5:
            report.fail("open items", f"line {number}: {len(cells)} cells, not 5")
            continue
        key = (code_spans(cells[0]) or [cells[0]])[0]
        found[key] = cells
        if not cells[2].strip():
            report.fail("open items", f"{key}: names no one who decides it")
        source = (code_spans(cells[3]) or [""])[0]
        match = re.fullmatch(r"(.+):(\d+)", source)
        if not match or git("ls-files", "--error-unmatch", match.group(1))[0] != 0:
            report.fail("open items", f"{key}: source {source!r} does not resolve at HEAD")
            continue
        lines = Path(match.group(1)).read_text(encoding="utf-8").splitlines()
        line_number = int(match.group(2))
        anchor = (code_spans(cells[4]) or [""])[0]
        if line_number > len(lines) or collapse(anchor) not in collapse(lines[line_number - 1]):
            report.fail("open items", f"{key}: {anchor!r} is not on {source}")
    for key in REQUIRED_KEYS:
        if key not in found:
            report.fail("open items", f"required key {key} is missing")
    held = found.get("retire-temporal-evidence-v1")
    if held:
        status = re.search(r"^\*\*Status:\*\* (\w+)", Path("tasks/work/retire-temporal-evidence-v1.md").read_text(encoding="utf-8"), re.M)
        if "D15" not in held[1] or not status or f"`{status.group(1)}`" not in held[1]:
            report.fail("open items", "the retire-temporal-evidence-v1 row does not name D15 and its Status at HEAD")
    findings = tables_under(audit, "7", "finding")
    for number, cells in findings:
        if len(cells) != 4:
            report.fail("findings", f"line {number}: {len(cells)} cells, not 4")
            continue
        where = code_spans(cells[2])
        match = re.fullmatch(r"(.+):(\d+)", where[0]) if where else None
        if not match or git("ls-files", "--error-unmatch", match.group(1))[0] != 0:
            report.fail("findings", f"{cells[0]}: {where} does not resolve at HEAD")
        elif int(match.group(2)) > len(Path(match.group(1)).read_text(encoding="utf-8").splitlines()):
            report.fail("findings", f"{cells[0]}: line {match.group(2)} is past the end of {match.group(1)}")
        for command_id in code_spans(cells[3]):
            if command_id not in runner.commands:
                report.fail("findings", f"{cells[0]}: no command {command_id}")
    report.note(f"open items: {len(found)} rows, {len(REQUIRED_KEYS)} required keys; findings: {len(findings)} rows")


def check_shape(audit: Audit, report: Report) -> None:
    headings = [int(m.group(1)) for line in audit.lines if (m := re.match(r"^## (\d+)\. ", line))]
    if headings != list(range(10)):
        report.fail("sections", f"top-level sections {headings}, not 0 to 9 in order")
    if "no CI gate" not in collapse(audit.text("9")):
        report.fail("sections", "section 9 does not say that no CI gate binds the figures")


def main(argv: list[str]) -> int:
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    audit = Audit(Path(argv[0]).read_text(encoding="utf-8").splitlines())
    report = Report()
    runner = Runner(parse_commands(audit, report), fast="--fast" in argv, report=report)
    check_shape(audit, report)
    check_stranger(audit, report)
    check_claims(audit, runner, report)
    check_eras(audit, runner, report)
    figures = check_figures(audit, runner, report)
    check_tokens(audit, figures, report)
    check_role_and_claim_words(audit, report)
    check_doctrine(audit, report)
    check_ledger(audit, report)
    check_open_items(audit, runner, report)
    for command_id, result in sorted(runner.cache.items()):
        report.note(f"command {command_id}: {'skipped (--fast)' if result is None else 'exit ' + str(result[0])}")
    for line in report.notes:
        print(line)
    for line in report.failures:
        print(line)
    print(f"audit_check: {len(report.failures)} failures")
    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
````

#### Validation

The battery ran in full at `f24d9ca9`. After the review corrections, at `082868ca` (the audit's last head; this commit
adds only Results), `check_doc_facts.py`, `validate_task_docs.py` and offline `verify_ml_evidence.py` exit 0 again
(64 checks, 0 FAIL), `audit_check.py` (full) exits 0 with 0 failures, the seven named test files pass again
(665 passed), and the bundle built there equals B's (110 files, `diff -r` exit 0). The table is the run at `f24d9ca9`.

| command | exit | count |
| --- | --- | --- |
| `env \| grep -c '^AILIBI_'` | | 0 |
| `uv run python scripts/check_doc_facts.py` | 0 | |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 historical phase tasks, 390 prompts, 106 work cards |
| `uv run python scripts/verify_ml_evidence.py` (offline) | 0 | 64 checks: 52 OK, 0 FAIL, 7 ABSENT, 5 INFO |
| `uv run pytest` over the seven named files, `-n 8` | 0 | 665 passed, 109 s |
| the six named planted-case tests | 0 | 6 passed |
| `publish_process_scorecard.py --check`, `publish_gameplay_census.py --check`, `publish_game_profile.py --check` | 0, 0, 0 | 10 s, 5 s, 4 s |
| `route_check_replay --check`, `route_lines_replay --check` | 0, 0 | "reproduced", 56.6 s and 58.6 s |
| `uv run lint-imports` | 0 | Contracts: 5 kept, 0 broken |
| `bash scripts/verify_samples.sh` | 0 | 4 directories, each "All 50 samples verified clean" |
| `build_sample_report.py --check`, the four committed sets (and both candidate copies at B) | 0 each | |
| the era print | 0 | `baseline-9`, then four rows equal to section 2.1 |
| `git ls-files replays/candidates \| cut -d/ -f1-3 \| sort -u` | 0 | 3 paths |
| `git ls-files audits \| wc -l`; the byte sum | 0 | 336; 31,665,710 |
| the ledger log | 0 | 37 merges |
| `gh pr list ... --json number,mergeCommit` (read-only) | 0 | 37 pull requests, each with a merge commit |
| `git log -1 --format='%H %s' -- tasks/work/rubric-extractor-era.md` | 0 | `97549508... docs: apply the extractor card's closure span correctly` |
| `git merge-base --is-ancestor 97549508 84a4509c` | 0 | |
| `grep -h '^\*\*Status:\*\*'` on the two held cards | 0 | `done`, `ready` |
| `git grep -c evidence_reasoning_version -- 'replays/**/experiment-config.json'` | 1 | |
| `git grep -n _cross_era_trajectory` | 0 | document hits only (finding 14); `-- '*.py'` exits 1 |
| `git ls-files tests/fixtures/phase10 experiments/lab/results-rubric-geomean.stage-b-r2.json` | 0 | nothing listed |
| `git log --first-parent --no-merges B..HEAD -- tasks/ docs/cleanup-dispositions.md` | 0 | nothing at `f24d9ca9`; this Results commit at H |
| `audit_check.py` (full) | 0 | 0 failures |
| `git diff --stat B..HEAD`, and over the code and recording paths | 0 | 3 files at `f24d9ca9`, 4 at H; nothing over the code paths |
| `build_demo_bundle.py --out` at B and at `f24d9ca9`, then `diff -r` | 0, 0, 0 | 110 files each, no difference |

#### Decisions

The orchestrator's rulings for this dispatch, recorded:
1. The audit file is `audits/audit-2026-10-10-finalized-state.md`: H falls on 2026-10-10.
2. Section 2's ladder is the `eval.eras` print at H and the candidate listing is `git ls-files`; the three named
   locations are checked with `git cat-file -e`, and a fourth, round 3's retired candidate copy at `2eed2e92`.
3. Section 3 covers every era the registry names (baseline-9, stage-b-r3, and stage-b-r2, which owns no committed
   set) and never pools; round 3's column is read as its record states it. The dispatch note's parenthetical "the step
   rule named no step" is contradicted by the record, whose section 8.7 prints the rule's line naming the era-keyed
   promotion of round 3 (`audits/audit-2026-10-09-stage-b-r3.md:1985`); it was round 2's rule that named no step (memo
   section 8, "Since section 7"). The audit follows the record, as this card's acceptance item reads it ("the step the
   rule named and the orchestrator's decision under 8.8"), and labels the orchestrator's taking of the step a reading.
   The featured-games claim is the count-only intersection.
4. Section 4 states each limit with its source, including the refuted route-arithmetic headline and that reaching is
   showing a line, not changing a vote.
5. The ledger has one row per first-parent merge from `0755c25d` to B: 37, no fast-forward.
6. Section 7 lists every required key with its state at H, who decides it and its source; the
   `retire-temporal-evidence-v1` row names it an owner confirmation point under D15 with Status `ready`. The
   nonblocking review defects were each re-checked at H with the command that shows it and filed (findings 2 to 13).
   Two differ from the dispatch note, as the tree shows them: finding 2's test lives in
   `tests/eval/test_gameplay_census.py` (the census's shallow-clone proof, `recording_blob_problems`), not under
   `tests/experiments`; and finding 10's scan finds eight pull requests carrying another Co-Authored-By line (70
   commits: #477 21, #483 4, #484 6, #495 12, #498 4, #502 9, #504 1, #507 13), not the three the note named. Three
   more were found on the way: finding 1 (the card's own architecture defect), finding 14 (this card's Validation line
   on `_cross_era_trajectory`) and finding 15 (the wrapped ladder-tip phrase, found by this card's index proof);
   finding 16 came from the automated review and was re-checked at H before it was filed.
7. The owner confirmation points are in one place, section 7.3, with the D15 recommendation labelled the
   orchestrator's reading and its prepared closure text named as held outside the tree.
8. Section 0 carries no task, card, decision, ruling, audit or pull request id (scan 0) and defines each term.
9. The index row and the `audits/` row were written at the heads that move audits bytes and re-derived at H.
10. The merge is the orchestrator's under memo 8.9; this pull request is not merged here.

Decisions of this build:
- Figure rows name the audit section that states a figure rather than a line of the audit, whose own lines move as it
  is written; the script checks the figure occurs in that section, and on its source line or in its command's stdout.
- A command's output is quoted in the audit inside a code span, which the number scan skips and the figure row
  verifies.
- `copy_problems` reads the index row's prose after its link: the link target is the file name, which
  `_TASK_OR_AUDIT_ID` matches by design (every audit file is named `audit-...`).
- The `audits/` row is derived from the index's blob sizes, which run on Linux and macOS alike; the `stat -f %z` sum
  of the card's Validation agrees.
- The CI run at H is cited in the pull request body; this Results commit cites the runs at `f24d9ca9` and
  `082868ca`.
- The placeholder paragraph of this section is replaced by the delivered Results.
- Finding 16 is filed rather than raised as a stop. The claim it contradicts sits where this card may not write
  (`eval/eras.py`'s docstring and round 3's record), which is the Constraints' stop case read literally; but the
  card's own Evidence files its one such defect (`docs/architecture.md:89` against `uv run lint-imports`) and its
  Outcome asks for "every defect this audit found on the way ... filed and not fixed here", so a contradiction the
  audit does not rely on is filed. The audit narrows its own sentence and relies on nothing the finding contradicts.
  The orchestrator may read it as a stop instead.
- Finding 13's showing commands are pinned to seeds (0 passes, 58 fails), since an unseeded run is not reproducible
  and made one plant run print an extra failure.

#### Defects filed (audit section 7.4)

1. `docs/architecture.md:89` "Four import-linter contracts" against five kept. 2. Round 3's lab column pinned at
`60059688`, whose tree holds the profile; the shallow-clone proof
`tests/eval/test_gameplay_census.py::test_the_route_check_columns_read_the_recordings_now_at_head` breaks on a later
profile regeneration in CI's depth-one checkout. 3. `check_verdict_figures` accepts the swapped 46 and 42. 4 to 8.
No doc-facts check holds the grounded row's floor label, the order of the four process rows, the
previously-shown-recording sentence, the body-handle disclosure (0 of 115) or the ML paragraph's 50 games. 9. The four
process rows carry no record date. 10. Eight pull requests with another Co-Authored-By line, never rewritten. 11. The
promotion card's wide-scan sentence names two of nine lines. 12. Its build-decisions trailer bullet is stale at its
head. 13. The profile tests' fold-reading Hypothesis case is seed-dependent: it passes under seed 0 and fails with
"DID NOT RAISE" under seed 58. 14. This card's Validation line expects the bare `_cross_era_trajectory` grep to exit
1. 15. The ladder-tip check does not see a phrase wrapped across a line. 16. The offline reasoning-evidence scorecard
folds all four sets across both eras into one block without the era registry, against the registry's docstring and
round 3's record section 12.3.

#### The automated review (Codex, five comments on `f24d9ca9`), assessed

- 4237134940 (P1, the Results missing): valid at that head and answered by this Results commit; the audit's claims
  about H stand on the Results and the pull request body, which cite the head's figures and CI runs.
- 4237134946 (P2, the five shelf counts without a row): valid; `082868ca` adds the `shelves` command and its figure
  row, read from the served profile, beside `docs/game-profile.md:76-80`.
- 4237134953 (P2, "every instrument reads the registry"): valid and re-checked at H (`eval/reasoning_evidence.py:342`,
  `_fixed_recording_inventory`, and `:386`, `_measure_historical_inputs`; `era registry reads 0`, `inventory sets
  4`); section 1 and its claim row are narrowed to the instruments the registry names, and the gap is filed as
  finding 16, not fixed (the instrument, the registry's docstring and round 3's record are outside this card).
- 4237134956 (P2, "every decision names its basis" beside the unexplained count): valid; the bullet now reads
  "Whether a decision names its basis" and says what the unexplained ballots are.
- 4237134962 (P2, a route line for every voter): valid; section 0 and section 3.5 now say a line reaches a voter only
  when a candidate's stated places change room, and section 3.5 states 671/702 ballots carried one.

#### Limitations

- After this merges, no CI gate binds the audit's figures (its section 9): the audit file is in no checked list, the
  gap the phase-21 close filed as its F1, and `audit_check.py` is scratch, quoted here and never committed.
- Finding 13 is filed from an observation the tree does not record. Locally the case passed alone at H and under
  twenty fixed Hypothesis seeds (scratch loop, seeds 0 to 19), and failed once in an unseeded run inside the planted
  firewall-paragraph check; the scratch sweep then ran seeds 20 to 57 (all passed) and seed 58
  failed with "DID NOT RAISE" in 0.97 s, twice more on re-run. The audit pins its passing command to seed 0 and
  shows the failure with seed 58, so its own check is deterministic.
- The pull-request cross-check against GitHub was read once, at dispatch; the ledger's count is git's.
- The two advisory memos were read only to name what the undecided items (D9, D12, D13, D15 to D18) ask; they are
  the source of no figure.
- Local runs are macOS; CI is Linux, and its run is the gate record.
