# Agent Prompt — 20.12 The front door: README for outsiders, the authorship statement, history, glossary, the audits index

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.12 — The front door: README for outsiders, the authorship statement, history, glossary, the audits index, anchored to C/A1, C/A2, C/A5, C/B2, C/B8, C/B12 and the front-door plan F1–F6 (audits/review-2026-08-19/C/collated-portfolio.md §A, §B, §F); audits/review-2026-08-19/C/x2-narrative-and-positioning.md §3, §5, §6a, §6b; audits/review-2026-08-19/C/x1-front-door-reproduction.md §1, §2, §3.1, §3.2; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 row 1.6 and §7 (the endorsed outline plus its three edits — demo link and byline above the commands, every volatile number baseline-stamped, honesty claims in verifiable shape); C-88 (audits/review-2026-08-19/B/collated-findings.md C-88). Anchors re-verified at HEAD `b809b19c`: README.md is 3,833 words / 248 lines; :82-107 is the "Project status" section at 845 words = 22 % of the file; :84 is one 135-word sentence with 11 opening parentheses; :86 says "the paragraph below it carries phases 15–19"; :88-105 is the phase table, last row 14; :107 is one 506-word paragraph with 35 opening parentheses; :149 spends 234 words on lever provenance inside "Watch a replay"; :47 carries "300+ merged agent-authored PRs — the live count is on GitHub, deliberately not re-pinned here" and one of three "MVP complete" declarations (:47, :84, :95); :74 carries "import-linter enforced"; :162-165 is the fake-provider tournament example; :211 and :230 carry the clone caveat; file-wide there are 81 em-dashes and 137 opening parentheses, and the six reading-guide terms occur undefined at baseline 19, adopting record 3, ladder tip 4, graduat* 5, NO-FLIP plus "no mover flip" 2, canary denominator 2. docs/reading-guide.md is 3,239 words / 378 lines: :37-51 the numbers table, :216-291 the eleven-term glossary, :303 the only disclosure that the second audit is "by a different model". The C-88 mechanism at HEAD is llm/fake_provider.py:183 (`f"fake-{field_name}-{seed}"`, so a `target` field mints `fake-target-<digest>`) meeting meetings/manager.py:200-207 and meetings/voting.py:90-92 (`INVALID_VOTE_TARGET_MARKER`, invalid target normalized to SKIP) — the review's `:127-135` anchor was the sibling union leg, corrected here. The committed counter-example is populated: replays/samples/9p2i/tournament-eval-report.json reads 101 ejections, `vote_correctness_rate` 0.9230769, `ejection_accuracy` 0.7722772. Fact-checker anchors re-verified at origin/main `37fe367a` (20.5 and 20.6 both extended this file after the re-verification above): scripts/check_doc_facts.py:110-112 (`_README`, `_ENV_EXAMPLE`, `_LADDER_TIP_AUDIT`), :213-223 (`check_facts`, fanning out to `check_sample_provenance`, `check_ladder_tip`, `check_lever_registry`, `check_vote_correctness_sentinel`), tests/scripts/test_check_doc_facts.py:31-75 (`_COPIED` at :31-44 and the `doc_tree` fixture at :62-75). Derivable counts at origin/main `37fe367a`: `agent_prompts/*.md` = 363, `replays/samples/{4p1i,9p2i}/*.jsonl` = 50 + 50, `git rev-list --count HEAD` = 902, commit authors dkdan10 373 / Claude 310 / Daniel Keinan 218, `Co-Authored-By` trailers on 327 commits.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-front-door-rewrite`
**Depends on:** 20.5, 20.7, 20.8, 20.9, 20.6 — the first-run stderr notice is silenced before the README labels the three commands as a clean one-minute proof; the hosted demo and the owner's About checklist exist before the front door links a live demo above the fold; the leak scanner learns to check entitlement and the import contracts learn to cover the whole tree before the README restates the firewall claim in verifiable shape; and the vote-correctness doc-fact check lands in the fact checker before this task extends that same file.
**Section refs:** C/A1, C/A2, C/A5, C/B2, C/B8, C/B12 and the front-door plan F1–F6 (audits/review-2026-08-19/C/collated-portfolio.md §A, §B, §F); audits/review-2026-08-19/C/x2-narrative-and-positioning.md §3, §5, §6a, §6b; audits/review-2026-08-19/C/x1-front-door-reproduction.md §1, §2, §3.1, §3.2; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 row 1.6 and §7 (the endorsed outline plus its three edits — demo link and byline above the commands, every volatile number baseline-stamped, honesty claims in verifiable shape); C-88 (audits/review-2026-08-19/B/collated-findings.md C-88). Anchors re-verified at HEAD `b809b19c`: README.md is 3,833 words / 248 lines; :82-107 is the "Project status" section at 845 words = 22 % of the file; :84 is one 135-word sentence with 11 opening parentheses; :86 says "the paragraph below it carries phases 15–19"; :88-105 is the phase table, last row 14; :107 is one 506-word paragraph with 35 opening parentheses; :149 spends 234 words on lever provenance inside "Watch a replay"; :47 carries "300+ merged agent-authored PRs — the live count is on GitHub, deliberately not re-pinned here" and one of three "MVP complete" declarations (:47, :84, :95); :74 carries "import-linter enforced"; :162-165 is the fake-provider tournament example; :211 and :230 carry the clone caveat; file-wide there are 81 em-dashes and 137 opening parentheses, and the six reading-guide terms occur undefined at baseline 19, adopting record 3, ladder tip 4, graduat* 5, NO-FLIP plus "no mover flip" 2, canary denominator 2. docs/reading-guide.md is 3,239 words / 378 lines: :37-51 the numbers table, :216-291 the eleven-term glossary, :303 the only disclosure that the second audit is "by a different model". The C-88 mechanism at HEAD is llm/fake_provider.py:183 (`f"fake-{field_name}-{seed}"`, so a `target` field mints `fake-target-<digest>`) meeting meetings/manager.py:200-207 and meetings/voting.py:90-92 (`INVALID_VOTE_TARGET_MARKER`, invalid target normalized to SKIP) — the review's `:127-135` anchor was the sibling union leg, corrected here. The committed counter-example is populated: replays/samples/9p2i/tournament-eval-report.json reads 101 ejections, `vote_correctness_rate` 0.9230769, `ejection_accuracy` 0.7722772. Fact-checker anchors re-verified at origin/main `37fe367a` (20.5 and 20.6 both extended this file after the re-verification above): scripts/check_doc_facts.py:110-112 (`_README`, `_ENV_EXAMPLE`, `_LADDER_TIP_AUDIT`), :213-223 (`check_facts`, fanning out to `check_sample_provenance`, `check_ladder_tip`, `check_lever_registry`, `check_vote_correctness_sentinel`), tests/scripts/test_check_doc_facts.py:31-75 (`_COPIED` at :31-44 and the `doc_tree` fixture at :62-75). Derivable counts at origin/main `37fe367a`: `agent_prompts/*.md` = 363, `replays/samples/{4p1i,9p2i}/*.jsonl` = 50 + 50, `git rev-list --count HEAD` = 902, commit authors dkdan10 373 / Claude 310 / Daniel Keinan 218, `Co-Authored-By` trailers on 327 commits.
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run python scripts/check_doc_facts.py` exits 0 and names the new checks; `uv run pytest tests/scripts/test_check_doc_facts.py -q` green with every new check perturbation-proved; `wc -w README.md` ≤ ~1,800 (from 3,833) and `wc -w docs/reading-guide.md` ≤ ~900 (from 3,239), both quoted in the PR with the em-dash and opening-parenthesis counts before and after; a grep for the six dialect terms in README.md returns only occurrences inside a `docs/glossary.md` link.

Six independent portfolio readers stopped reading the README at the same place. The
"Project status" section (README.md:82-107) is 845 words — 22 % of the whole file — and it
opens with a 135-word single sentence (:84) and closes with a 506-word single paragraph
(:107) whose longest sentence runs 172 words. The phase table stops at 14 and says so
(:86: "the paragraph below it carries phases 15–19"), which is the author noticing that a
paragraph is a table nobody extended. Read literally, the section is a run of negatives —
closed with no mover flip, closed with nothing recorded, zero of fourteen pre-registered
rulings demonstrated — and three of the six readers report understanding it as "the last
two phases produced nothing" until they reached the reading guide's honesty section, one
hop below the front door (audits/review-2026-08-19/C/collated-portfolio.md §A1). The
project's honesty culture is its strongest asset and the front door currently delivers it
as an apology.

The second measured defect is vocabulary. Six of the eleven terms the reading guide
defines appear undefined in the README — re-counted at HEAD as baseline 19, adopting
record 3, ladder tip 4, graduated 5, NO-FLIP plus "no mover flip" 2, canary denominator 2
— and at least fifteen more (referee, slate, arm, mover, champion, conviction economy,
supply and conversion floors, absence prior, roll-call round, endpoint-band whereabouts
exemption, flag-minting, starved-economy shape, screening-tier shortlist, two-axis owner
ruling, training-time-runner tier, evidence-gated default flip) are defined nowhere in the
tree (§A2). Conventions named after task numbers are the clearest tell. The rule this task
adopts is the reviewers' own: nothing in README.md may require the reading guide to parse.
The evicted material lands somewhere real — the phase narrative in `docs/history.md`, the
vocabulary in `docs/glossary.md` (with descriptive names beside the task-numbered ones),
and the 76 top-level audit files, of which only three are named read-first and the rest are
unnavigable, in `audits/README.md` (§B12). The reading guide itself is 3,239 words against
an advertised five minutes; it keeps its numbers table, its demo path, its capability
cross-tab and its three-audits tour, and sheds the glossary (§B3).

The third defect is the one only the human can fix. The README names no person. LICENSE
says Daniel Keinan; git shows three human identities plus "Claude" as first-class author on
310 of 902 commits with `Co-Authored-By` trailers on 327 of them; every merged PR shows one
human author on GitHub. The docs say "the owner", "the human", "the operator" and never
introduce them (audits/review-2026-08-19/C/x2-narrative-and-positioning.md §5: the
mechanics of authorship are unusually legible here and the narrative of authorship is
absent, and absence gets read uncharitably). Two disclosures ride with it: the
"independent external audits" the docs lean on are AI auditors the owner commissioned —
stated today only at docs/reading-guide.md:303 — and every gameplay and ML number in the
repo comes from one model on one prompt set at n=50 per set (§A5). This section is written
first-person, from git evidence, and marked for the owner to confirm rather than invented.

The fourth is a claim that is false in the reader's hands. The README's tournament example
(:162-165) hands a stranger the default fake provider, and a fake ballot's `target` is
minted as `fake-target-<digest>` (llm/fake_provider.py:183), which the meeting layer
defensively normalizes to SKIP (meetings/manager.py:200-207) — so the report an outsider
gets has zero ejections and null rates (C-88; C/B2, reproduced by X1 §1 row 5). The
committed `replays/samples/9p2i/tournament-eval-report.json` is populated (101 ejections,
vote correctness 0.923, ejection accuracy 0.772) and is what the example should point at,
with one sentence on what fake output looks like and why. In the same pass the honesty
claims move to the shape a reader can check — "never breached in CI: import-linter
contract, planted-leak test, recursive leak sweep" — which only becomes true once the
scanner checks entitlement and the contracts cover the whole tree, which is exactly why
those two tasks are upstream of this one.

What keeps this from rotting is the discipline the phase is enforcing: generated facts beat
copied facts. Every number the new README states must either be re-derived by
`scripts/check_doc_facts.py` from a committed source (manifests, the served report cells,
the lever registry, the prompt corpus, the phase files, the audit corpus) or must not be
stated as a bare number at all — volatile counts become a date-stamped claim plus the
command a reader runs, per the fact-check precedent this task extends. This task writes the
front door's structure, prose and checks; it does not write the results table's ML
paragraph, the architecture picture, the contract-to-PR exhibit, the lessons page or the new
hero image, each of which is a later contract that fills a marked anchor here. No link this
task writes may point at a file that does not exist at this merge — the front door's 49
relative links are 0-broken today (X1 §1 row 7) and stay that way; forward pointers are HTML
comments, never live links.

**Files in scope:**
- README.md; (the rewrite per the endorsed outline: pitch-first tagline with the byline, the hosted-demo link above the fold, the labelled reproduce block, at-a-glance, the human/agent split, project status in ≤150 words with the phase table extended through 19, the numbers table, and the honesty claims in verifiable shape)
- docs/history.md; (new — the evicted phase narrative, one paragraph per phase, each linking its close audit where one exists and its contract file otherwise)
- docs/glossary.md; (new — the reading guide's eleven terms plus the fifteen-plus defined nowhere, each with a descriptive name beside any task-numbered convention and one committed usage)
- audits/README.md; (new — the index: the three read-first audits, then every audit by phase with one line each)
- docs/reading-guide.md; (trimmed to a real five minutes: the numbers table, the demo path, the capability cross-tab and the three audits; the glossary moves out; file:line citations become heading anchors)
- scripts/check_doc_facts.py; (the new checks: dialect terms linked, the phase table and history complete, the audits index complete, the results figures agreeing with the reading guide, volatile counts date-stamped, no file:line citations left in the guide, every relative link resolving)
- tests/scripts/test_check_doc_facts.py; (one perturbation test per new check, plus the extended `doc_tree` fixture)

**Files NOT in scope:**
- docs/ml-program.md and the README results-table ML paragraph (20.13 — this task leaves a marked anchor and the table's non-ML rows)
- docs/architecture.md, docs/media/architecture.svg and the contract-to-prompt-to-PR exhibit (20.20 — this task leaves a marked anchor)
- docs/lessons.md and the "What I learned" section (20.40 — the section is not stubbed, only marked)
- docs/media/* and the hero swap (20.39 owns the image and its caption; the existing PNG stays as the hero here, its caption shortened)
- docs/adr/0001-three-load-bearing-decisions.md and the "recorded verbatim" wording (20.13 owns the ADR note; 20.41 owns that README sentence)
- docs/artifacts.md and docs/deployment.md (the clone caveat and the deployment trust boundary already live there — the README links them, neither file is edited)
- .env.example, AGENTS.md, CONTRIBUTING.md (20.5 and 20.9 own their lines)
- scripts/check.sh (the fact check runs under pytest, as it has since it was introduced)
- replays/, audits/audit-*.md (records are read and indexed, never rewritten; records get additive dated errata, and none is due here)
- the prompt templates and agent_prompts/ (no template edit and no prompt regeneration from this task)
- DESIGN.md, AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] README.md follows the endorsed outline: a product-first tagline with a byline line (name, agents, MIT, CI and Python badges, the solo timeline), the hosted-demo URL from the Pages workflow in the first screen, the three existing reproduce commands kept verbatim and each labelled with the claim it proves, an at-a-glance block, "How it was built — who did what", "What it is", "What the measurements said", "Project status" and the phase table, "Run it", and the docs/architecture/glossary/reading-guide/history footer.
- [ ] "Project status" is ≤150 words of plain English, states in one sentence what a no-flip and a nothing-recorded close MEAN (a bar was pre-registered; the honest answer was not yet), leads with what was shown before the refusal to overclaim, and is followed by a phase table covering 0–19 in which every row links a file that exists — its close audit where one exists, its contract file otherwise; the 845-word section and the 506-word paragraph are gone from README.md.
- [ ] A "How it was built — who did what" section names the human and the agents in first person, ~120 words: what the human owned (the task contracts, the standing rules, the review gates, the audit rulings, the product direction), what the agents wrote (every coding PR, most audits), what the human did not do (write production code by hand), and how a reader verifies it in git (the `claude/…` branch names, the commit authors, the `Co-Authored-By` trailers); it states that the commissioned audits were AI auditors, not third parties, and that every gameplay and ML number is one model on one prompt set at n=50 per set; the whole section carries `<!-- OWNER: confirm wording -->`.
- [ ] No undefined private-dialect term survives on the front door: each of the six counted terms and each surviving term from the defined-nowhere list either does not appear in README.md or appears with its first occurrence linked to its `docs/glossary.md` entry, and `scripts/check_doc_facts.py` fails when an occurrence is unlinked or a glossary entry is missing (perturbation-tested both ways in tests/scripts/test_check_doc_facts.py).
- [ ] The firewall and gate claims are verifiable-shaped and true as of this merge: the firewall line reads as never breached in CI with its three named mechanisms (the import-linter contract, the planted-leak test, the recursive leak sweep), and the "merged green through the same gate" claim is restated as what a reader can check (CI is required on main, see the workflow; `bash scripts/check.sh` runs the same gate locally).
- [ ] The fake-provider tournament example points at `replays/samples/9p2i/tournament-eval-report.json` as a real report and says in one sentence what fake-provider output looks like and why (every fake ballot's minted target normalizes to SKIP, so the report has no ejections and null rates); a reader following the README reaches a populated report.
- [ ] `docs/history.md` carries one paragraph per phase 0–19 with the evicted narrative and the lever-graduation provenance, `docs/glossary.md` defines the reading-guide terms plus the ones defined nowhere with a descriptive name beside every task-numbered convention, and `audits/README.md` indexes every top-level `audits/*.md` exactly once (the three read-first audits first, then by phase, one line each) with the review directory named as a unit; a check fails when an audit file is added or removed without an index row.
- [ ] `docs/reading-guide.md` is ≤ ~900 words, keeps its numbers table, demo path, capability cross-tab and three-audits tour, no longer carries the glossary, and contains zero `file.ext:NN` citations — every one replaced by a heading anchor or a symbol reference; a check pins the zero.
- [ ] Every number README.md states is checked: `scripts/check_doc_facts.py` gains checks that the phase table and `docs/history.md` between them account for every `tasks/phase-*.md`; that the README results figures equal the reading guide's canonical rows; that each volatile count (merged PRs) carries an as-of date stamp rather than a bare number; and that every relative link in README.md, docs/history.md, docs/glossary.md, audits/README.md and docs/reading-guide.md resolves to an existing path. Each new check has a perturbation test that fails on a mutated copy and passes on the unperturbed one, and the `doc_tree` fixture copies exactly the files the new checks read.
- [ ] The PR quotes `wc -w README.md` before and after (3,833 → ≤ ~1,800), `wc -w docs/reading-guide.md` before and after (3,239 → ≤ ~900), and the em-dash and opening-parenthesis counts before and after (81 and 137 at HEAD), and states whether the owner has enabled Pages yet — if not, the demo line carries `<!-- OWNER: enable Pages, then confirm this URL resolves -->` and the PR says so.
- [ ] docs/reading-guide.md's enforcement claim quotes the wording the import-contracts task recorded (the widened root set; the temp-tree plant) — the reading guide and the README state the same verifiable shape.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — measure before you cut, and keep the receipts. Record the four counts the PR
must quote (README words, reading-guide words, em-dashes, opening parentheses) at HEAD
before the first edit. The reproduce block at README.md:13-37 is the one thing all six
reviewers praised: keep those three commands byte-for-byte and add only a label above
each naming the claim it proves (same seed twice is byte-identical; the hundred committed
replays reconstruct; the demo is a static directory). Do not rewrite the commands to look
tidier.

Step 2 — move, do not delete. Everything at README.md:84, :86, :107, :149 and :230 leaves
the file: the phase narrative and the lever-graduation provenance to docs/history.md, the
clone caveat to one line plus the existing docs/artifacts.md link, the vocabulary to
docs/glossary.md. The phase table's rows 0–14 already exist; extend to 19 and give every
row a link that resolves. Note that close audits exist only for the MVP close and phases
13 through 19 — for the earlier phases link the contract file and say so in one line above
the table rather than inventing an audit name.

Step 3 — write the numbers once. The reading guide's numbers table is the canonical
statement; the README's "What the measurements said" table quotes the same figures with
the same committed sources, and the new check asserts the two agree row by row so a later
edit cannot drift one from the other. Leave a marked anchor for the ML paragraph and the
before/after column rather than an empty heading. Do not lift the audit-only figures out of
the evicted paragraph into the README — they belong to the results page, and the reading
guide already carries the four that matter.

Step 4 — the authorship section comes from git, not from memory. Re-derive at
implementation time and quote the commands in the PR: `git rev-list --count HEAD`,
`git shortlog -sn --all`, the `Co-Authored-By` trailer count, `ls agent_prompts/*.md | wc -l`,
and the merged-PR count via `gh pr list --state merged`. State the merged count with an
explicit as-of date so the claim ages honestly; the check asserts the stamp is present and
well-formed, never the value, because no doc check may reach the network. Write the section
in first person, mark it for the owner, and change no other document's institutional
register.

Step 5 — the new checks live beside the existing three. `check_facts` at
scripts/check_doc_facts.py:213-223 is the fan-out; add each new check as its own function
accumulating into the same error list so one run names every drift. The dialect-term check
wants a module-level tuple of terms with the glossary heading each must resolve to, so
adding a term later is a one-line change. The audits-index check should walk
`audits/*.md` at top level and diff against the index's rows in both directions — an
un-indexed file and an indexed file that no longer exists are both failures. The
link-resolution check needs no network: parse the relative markdown targets, strip any
fragment, and stat the path. Extend `_COPIED` and the `doc_tree` fixture at
tests/scripts/test_check_doc_facts.py:31-75 with exactly the files the new checks read, and
give every new check a mutated-copy test — a check that cannot fail is not a gate.

Step 6 — forward anchors are comments, never links. The results-table ML paragraph, the
architecture picture, the contract-to-PR exhibit, the lessons page and the hero swap are
later contracts. Mark each spot with an HTML comment naming the work in words. A live link
to a file that does not exist yet would break the zero-broken-links property this task is
also asked to keep.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import check_doc_facts"`
- `uv run python -c "import eval.leak_scan"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-front-door-rewrite` with a title like `task 20.12: the front door: readme for outsiders, the authorship statement, history, glossary, the audits index`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C/A1, C/A2, C/A5, C/B2, C/B8, C/B12 and the front-door plan F1–F6 (audits/review-2026-08-19/C/collated-portfolio.md §A, §B, §F); audits/review-2026-08-19/C/x2-narrative-and-positioning.md §3, §5, §6a, §6b; audits/review-2026-08-19/C/x1-front-door-reproduction.md §1, §2, §3.1, §3.2; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 row 1.6 and §7 (the endorsed outline plus its three edits — demo link and byline above the commands, every volatile number baseline-stamped, honesty claims in verifiable shape); C-88 (audits/review-2026-08-19/B/collated-findings.md C-88). Anchors re-verified at HEAD `b809b19c`: README.md is 3,833 words / 248 lines; :82-107 is the "Project status" section at 845 words = 22 % of the file; :84 is one 135-word sentence with 11 opening parentheses; :86 says "the paragraph below it carries phases 15–19"; :88-105 is the phase table, last row 14; :107 is one 506-word paragraph with 35 opening parentheses; :149 spends 234 words on lever provenance inside "Watch a replay"; :47 carries "300+ merged agent-authored PRs — the live count is on GitHub, deliberately not re-pinned here" and one of three "MVP complete" declarations (:47, :84, :95); :74 carries "import-linter enforced"; :162-165 is the fake-provider tournament example; :211 and :230 carry the clone caveat; file-wide there are 81 em-dashes and 137 opening parentheses, and the six reading-guide terms occur undefined at baseline 19, adopting record 3, ladder tip 4, graduat* 5, NO-FLIP plus "no mover flip" 2, canary denominator 2. docs/reading-guide.md is 3,239 words / 378 lines: :37-51 the numbers table, :216-291 the eleven-term glossary, :303 the only disclosure that the second audit is "by a different model". The C-88 mechanism at HEAD is llm/fake_provider.py:183 (`f"fake-{field_name}-{seed}"`, so a `target` field mints `fake-target-<digest>`) meeting meetings/manager.py:200-207 and meetings/voting.py:90-92 (`INVALID_VOTE_TARGET_MARKER`, invalid target normalized to SKIP) — the review's `:127-135` anchor was the sibling union leg, corrected here. The committed counter-example is populated: replays/samples/9p2i/tournament-eval-report.json reads 101 ejections, `vote_correctness_rate` 0.9230769, `ejection_accuracy` 0.7722772. Fact-checker anchors re-verified at origin/main `37fe367a` (20.5 and 20.6 both extended this file after the re-verification above): scripts/check_doc_facts.py:110-112 (`_README`, `_ENV_EXAMPLE`, `_LADDER_TIP_AUDIT`), :213-223 (`check_facts`, fanning out to `check_sample_provenance`, `check_ladder_tip`, `check_lever_registry`, `check_vote_correctness_sentinel`), tests/scripts/test_check_doc_facts.py:31-75 (`_COPIED` at :31-44 and the `doc_tree` fixture at :62-75). Derivable counts at origin/main `37fe367a`: `agent_prompts/*.md` = 363, `replays/samples/{4p1i,9p2i}/*.jsonl` = 50 + 50, `git rev-list --count HEAD` = 902, commit authors dkdan10 373 / Claude 310 / Daniel Keinan 218, `Co-Authored-By` trailers on 327 commits.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
