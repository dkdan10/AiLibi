# Agent Prompt — 20.20 The as-built architecture picture and the contract → prompt → PR exhibit

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.20 — The as-built architecture picture and the contract → prompt → PR exhibit, anchored to audits/review-2026-08-19/C/collated-portfolio.md §(B) items B4 and B5 [B4 raised by P1 G, P2 G, P4 G, X2 G, X1 N; B5 by X1 G, X2 fold, P3 N, P1 M-3 fold]; audits/review-2026-08-19/C/p1-backend-hiring-manager.md §2 "12:00–14:00 — docs/architecture.md" [VERIFIED 146 lines — "This is the document I wanted first"] + §7 GOOD 4 (one click from the top) + §7 GOOD 10 (file size will be asked about); audits/review-2026-08-19/C/x1-front-door-reproduction.md §3.4 (architecture.md "is not linked from the README's first screen — only in 'What this is' and the footer"; 1,089 words per §6), §4 "Other builders" ("the workflow artifacts (task contract → prompt) are linked once and never shown"), §5 GOOD 7 (a 15-line contract excerpt + the matching prompt header + the PR it produced, branch `claude/…`, gate green) + §5 NICE 14; audits/review-2026-08-19/C/x2-narrative-and-positioning.md §4 gap row "Architecture diagram (image) — ASCII only; `DESIGN.md` §1.1 diagram is the *target* arch" + §6 proposal 7 (an as-built SVG of the layering plus the firewall arrow); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 1 row 1.14 (C/B4 + C/B5, size S, measurement "three links resolve; a reader verifies agent authorship in git in 30 s"); audits/review-2026-08-19/D/synth-ambition.md §FM-6 (the contract→prompt→PR triple shown, not linked); README.md:76 (`## What it is`), :84 (the architecture link, now a one-line pointer), :85 (20.12's reserved `<!-- ANCHOR: … inlines the as-built layering diagram here. -->`), :59 (`## How it was built — who did what`), :73 (the one workflow-artifact line, linked and never shown), :74 (20.12's reserved `<!-- ANCHOR: … shows a contract, its prompt and the merged pull request inline. -->`), :62 (the owner-ratified authorship paragraph), :162 (the footer link); docs/architecture.md:11-21 (the ASCII layering block), :51-56 (the `meetings/` paragraph), :89-91 (the generated `frontend/src/types/api.ts`), :104-118 ("Enforced boundaries" — the four contracts and their backing tests), 146 lines at HEAD; .importlinter:20-26 (`[importlinter:agents_must_not_import_engine]`, `name = Agents must not import engine`); DESIGN.md:7-12 (the Task 19.1 demotion banner), :49 (§1.1 Component diagram — the target architecture); `wc -l` at HEAD: meetings/manager.py 3,989, orchestrator/game.py 3,193; audits/audit-phase-19-planning.md:170-174 (the monolith decompositions on the recorded backlog); docs/media/README.md:1-10 (the two-row asset table); docs/artifacts.md:108 (the `docs/media/` registry row promises "1.7 MB / 3 files"); scripts/verify_ml_evidence.py:2110 + :2163 + :2171 (`_STATED_FILES`) + :2174-2202 (`inventory_problems`) and tests/scripts/test_verify_ml_evidence.py:1402-1420 (the row-count gate a fourth file under `docs/media/` turns red); agent_prompts/task-19-2-in-code-truth.md:1-16 (the generated prompt header shape) against tasks/phase-19.md:314-361 (its contract) and the merged PR https://github.com/dkdan10/AiLibi/pull/328. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-architecture-exhibit`
**Depends on:** 20.13 — the front door's results section lands first, so this task edits a README whose sections already sit in their rewritten shape and only adds the picture and the workflow exhibit on top of it, rather than racing the rewrite for the same paragraphs; also after 20.17 (the artifacts registry row both tasks touch is ordered behind the hermeticity fix)
**Section refs:** audits/review-2026-08-19/C/collated-portfolio.md §(B) items B4 and B5 [B4 raised by P1 G, P2 G, P4 G, X2 G, X1 N; B5 by X1 G, X2 fold, P3 N, P1 M-3 fold]; audits/review-2026-08-19/C/p1-backend-hiring-manager.md §2 "12:00–14:00 — docs/architecture.md" [VERIFIED 146 lines — "This is the document I wanted first"] + §7 GOOD 4 (one click from the top) + §7 GOOD 10 (file size will be asked about); audits/review-2026-08-19/C/x1-front-door-reproduction.md §3.4 (architecture.md "is not linked from the README's first screen — only in 'What this is' and the footer"; 1,089 words per §6), §4 "Other builders" ("the workflow artifacts (task contract → prompt) are linked once and never shown"), §5 GOOD 7 (a 15-line contract excerpt + the matching prompt header + the PR it produced, branch `claude/…`, gate green) + §5 NICE 14; audits/review-2026-08-19/C/x2-narrative-and-positioning.md §4 gap row "Architecture diagram (image) — ASCII only; `DESIGN.md` §1.1 diagram is the *target* arch" + §6 proposal 7 (an as-built SVG of the layering plus the firewall arrow); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 1 row 1.14 (C/B4 + C/B5, size S, measurement "three links resolve; a reader verifies agent authorship in git in 30 s"); audits/review-2026-08-19/D/synth-ambition.md §FM-6 (the contract→prompt→PR triple shown, not linked); README.md:76 (`## What it is`), :84 (the architecture link, now a one-line pointer), :85 (20.12's reserved `<!-- ANCHOR: … inlines the as-built layering diagram here. -->`), :59 (`## How it was built — who did what`), :73 (the one workflow-artifact line, linked and never shown), :74 (20.12's reserved `<!-- ANCHOR: … shows a contract, its prompt and the merged pull request inline. -->`), :62 (the owner-ratified authorship paragraph), :162 (the footer link); docs/architecture.md:11-21 (the ASCII layering block), :51-56 (the `meetings/` paragraph), :89-91 (the generated `frontend/src/types/api.ts`), :104-118 ("Enforced boundaries" — the four contracts and their backing tests), 146 lines at HEAD; .importlinter:20-26 (`[importlinter:agents_must_not_import_engine]`, `name = Agents must not import engine`); DESIGN.md:7-12 (the Task 19.1 demotion banner), :49 (§1.1 Component diagram — the target architecture); `wc -l` at HEAD: meetings/manager.py 3,989, orchestrator/game.py 3,193; audits/audit-phase-19-planning.md:170-174 (the monolith decompositions on the recorded backlog); docs/media/README.md:1-10 (the two-row asset table); docs/artifacts.md:108 (the `docs/media/` registry row promises "1.7 MB / 3 files"); scripts/verify_ml_evidence.py:2110 + :2163 + :2171 (`_STATED_FILES`) + :2174-2202 (`inventory_problems`) and tests/scripts/test_verify_ml_evidence.py:1402-1420 (the row-count gate a fourth file under `docs/media/` turns red); agent_prompts/task-19-2-in-code-truth.md:1-16 (the generated prompt header shape) against tasks/phase-19.md:314-361 (its contract) and the merged PR https://github.com/dkdan10/AiLibi/pull/328
**Complexity:** Small
**Record impact:** none
**Measurement:** `xmllint --noout docs/media/architecture.svg` is silent and `wc -c docs/media/architecture.svg` is under 60,000; `uv run python scripts/check_doc_facts.py` exits 0; `uv run pytest tests/scripts/test_check_doc_facts.py tests/scripts/test_verify_ml_evidence.py -q` green — the new exhibit link-check resolves all three targets (the contract file, the generated prompt file, and the PR number as a `(#N)` commit-subject suffix reachable from HEAD), the SVG parses under `xml.etree.ElementTree`, docs/architecture.md is under its stated word budget, and the `docs/media/` registry row now reads 4 files against a 4-file index.

The best technical document in the repository is effectively unlinked.
`docs/architecture.md` is 146 lines at HEAD with an ASCII layering block at :11-21
and a four-contract "Enforced boundaries" section at :104-118; the backend hiring
manager read it at minute 12 and wrote "This is the document I wanted first"
(`audits/review-2026-08-19/C/p1-backend-hiring-manager.md` §2), and the narrative
reviewer called it the best single technical page in the repo. Four of the six
personas asked for it one click from the top
(`audits/review-2026-08-19/C/collated-portfolio.md` §(B) B4). Today it is reachable
only from a one-line pointer at `README.md:84` and from the footer at
`README.md:162` — a placement X1 measured and named in
`audits/review-2026-08-19/C/x1-front-door-reproduction.md` §3.4 (X1 read the
pre-20.12 README, where those two routes sat at :45 and :248). There is also no
picture of the system anywhere a reader lands: the only component diagram in the
repo, `DESIGN.md:49` §1.1, draws the *target* architecture of a demoted historical
record (`DESIGN.md:7-12` carries the Task 19.1 banner), so the one diagram a reader
can find is the one that is not the system.

The workflow has the same shape of defect: asserted, never shown. `README.md:73`
offers "One contract and the prompt generated from it" — a link to Task 3.19's contract
and a link to its generated prompt — and that is the whole exhibit; 20.12 left this
task's insertion point as the HTML comment at `README.md:74`. X1 recorded the
consequence for the audience the project fits best: "the workflow artifacts (task
contract → prompt) are linked once and never shown; no diagram, no excerpt, no 'here
is one contract and the PR it produced'" (§4, "Other builders"). The fix both X1 §5
GOOD 7 and `audits/review-2026-08-19/D/synth-ambition.md` §FM-6 ask for is one real
~15-line contract excerpt sitting beside the header its generator produced and the
merged PR that closed it. Note why the exhibit cannot simply promote the pair already
linked: Task 3.19 predates PR-numbered dispatch — its four commits (`e3a327a5`,
`5fd83bfe`, `d042e745`, `305e2cee`) carry no `(#N)` suffix — so it has no PR to show,
and the triple must be drawn from a task that has all three artifacts. Task 19.2 is
the recommended pick: contract at `tasks/phase-19.md:314-361`, prompt at
`agent_prompts/task-19-2-in-code-truth.md`, merged as PR #328.

The authorship sentence that ships beside the exhibit must be verifiable-shaped, and
the true mechanics are slightly more interesting than the review assumed. At HEAD,
`main` holds 910 commits; `git log --author=Claude` returns 310 of them (the 35%
`audits/review-2026-08-19/D/synth-ambition.md` §FM-6 quotes, measured on a smaller
`main`) and a `--grep='Co-Authored-By: Claude'` walk returns 299; `origin` still
carries 282 `claude/…` branch heads. But the squash commit for a merged PR carries the human as author with
no trailer — `ac162041` ("task 19.2: … (#328)") is authored by `dkdan10` — while the
trailer and the model name live on the pre-squash branch commit (`8344d025`,
`Co-Authored-By: Claude Fable 5`), reachable through the PR. The README sentence
therefore hands the reader the *commands* and says where each signal lives; it does
not pin the counts, which move with every merge and which the front door's own
doc-fact discipline exists to keep out of prose.

What this task ships is small and entirely presentational: one committed SVG of the
as-built layering with the firewall drawn as an arrow and its import-linter contract
named, embedded in both `docs/architecture.md` and the README's "what it is" section;
the contract → prompt → PR exhibit in the README's "how it was built" section; one
sentence in `docs/architecture.md` acknowledging that `meetings/manager.py` (3,989
lines) and `orchestrator/game.py` (3,193 lines) are large and that their
decomposition is on the recorded backlog at
`audits/audit-phase-19-planning.md:170-174` — the answer P1 §7 GOOD 10 says an
interviewer will ask for; and the asset row in `docs/media/README.md`. Nothing behind
the firewall moves, no recording is touched, and no prompt template is edited — the
single Phase-20 prompt-set bump is Task 20.31's alone, and this task must not touch
`agents/strategic/prompts/` or `scripts/prompt_template.md.j2`. One non-obvious
coupling the blast-radius grep found: `docs/artifacts.md:108` promises `docs/media/`
holds "1.7 MB / 3 files", and `tests/scripts/test_verify_ml_evidence.py:1402-1420`
compares that promise against the git index, so a fourth committed file under
`docs/media/` turns the evidence command red until the row is corrected in the same
PR.

**Files in scope:**
- docs/media/architecture.svg; (new: the as-built layering with the firewall arrow, hand-authored SVG or generated by a small script committed under docs/media/)
- docs/architecture.md; (embeds the SVG; one sentence on why meetings/manager.py and orchestrator/game.py are large — the decomposition is backlog)
- README.md; (the 'What it is' section embeds the SVG; the 'How it was built' section shows a ~15-line contract excerpt beside its generated prompt header and links the PR it produced)
- docs/media/README.md; (the asset list)
- docs/artifacts.md; (the docs/media/ registry row count — verify_ml_evidence compares it against the git index)

**Files NOT in scope:**
- DESIGN.md (the diagram there stays as the historical target; a caption is 19.1's demoted-record convention — not touched here)
- scripts/prompt_template.md.j2 and agents/strategic/prompts/ (unchanged; the one Phase-20 prompt-set bump belongs to 20.31, and no other task may edit a template)
- docs/reading-guide.md, docs/history.md, docs/glossary.md, docs/ml-program.md (the front-door rewrite and the results page landed upstream; this task adds to the README, it does not restructure it)
- scripts/check_doc_facts.py (run as a gate, not edited — the new pins are pytest-side)
- .importlinter and any source package (the contract is quoted in the picture, never changed)
- docs/media/spectator-journey.gif and spectator-meeting.png (the hero media swap is a later task; these bytes do not move here)

**Definition of done:**
- [ ] `docs/media/architecture.svg` exists, is hand-authored text (no embedded raster, no `<foreignObject>`, no external font or image reference, real `<text>` rather than outlined paths), parses under `xml.etree.ElementTree`, and is under 60,000 bytes — the parse and the size ceiling pinned in `tests/scripts/test_check_doc_facts.py`.
- [ ] The picture shows the as-built layering that `docs/architecture.md:11-21` states in text — engine → observation → agents/meetings ← orchestrator, `llm/` sitting beside the reasoning layer behind the `LLMClient` Protocol, `eval/` and `api/` as privileged readers, `frontend/` running on types generated from the DTOs (`docs/architecture.md:89-91`) — plus the observation firewall drawn as an arrow labelled with its import-linter contract name, `Agents must not import engine` (`.importlinter:20-26`), and a legend line stating that arrows are data flow while imports run the other way.
- [ ] The SVG is legible in both GitHub themes: it declares no opaque light backdrop, uses no pure-black or pure-white stroke/text fills, and carries an internal `@media (prefers-color-scheme: dark)` block; the PR body records the README rendered in both GitHub themes as the evidence for the rendering claim.
- [ ] `docs/architecture.md` embeds the SVG near the top of its layering section, keeps the ASCII block as the text-only fallback, and stays inside two pages — pinned as a word budget (≤ 1,300 words; 1,089 at HEAD per `audits/review-2026-08-19/C/x1-front-door-reproduction.md` §6) asserted in `tests/scripts/test_check_doc_facts.py`, so growth fails the gate rather than the reviewer.
- [ ] `docs/architecture.md` carries one sentence naming `meetings/manager.py` and `orchestrator/game.py` as the two large modules, why they are one unit each, and that the decomposition is on the recorded backlog at `audits/audit-phase-19-planning.md:170-174`; the line counts are not written into the prose as numbers.
- [ ] The README's `## What it is` section (`README.md:76`) embeds the same SVG with a one-line caption and a link to `docs/architecture.md`, in place of 20.12's reserved comment at `README.md:85`; the pointer line at `README.md:84` and the footer link at `README.md:162` survive as links but are no longer the only routes to the page.
- [ ] The README's `## How it was built — who did what` section (`README.md:59`) shows the triple inline, in place of 20.12's reserved comment at `README.md:74`: a ~15-line verbatim excerpt of one real contract, the first lines of the prompt the generator produced from it, and a link to the merged PR that closed it — recommended pick Task 19.2 (`tasks/phase-19.md:314-361`, `agent_prompts/task-19-2-in-code-truth.md`, PR #328); the excerpt and the prompt lines are byte-identical substrings of their sources, asserted in `tests/scripts/test_check_doc_facts.py` so a future contract edit cannot silently falsify the exhibit.
- [ ] One sentence beside the exhibit tells a reader how to verify agent authorship in git and where each signal lives: `git log --author=Claude` and `git log --grep='Co-Authored-By: Claude'` on `main`, the `Co-Authored-By` trailer naming the model on the PR's own branch commits rather than on the squash commit, and the `claude/…` branch heads on `origin`. It ADDS the commands and the squash-vs-branch mechanic to 20.12's owner-ratified authorship paragraph at `README.md:62`, which already names all three signals; that paragraph sits inside an `<!-- OWNER: … -->` block and its as-of-stamped trailer count stays exactly as merged (`check_volatile_stamps` in `scripts/check_doc_facts.py` gates the stamp's shape). This task's own sentence adds no new commit count to prose.
- [ ] A link-check in `tests/scripts/test_check_doc_facts.py` fails when any of the three exhibit targets stops resolving: the contract path and the prompt path must exist on disk, and the PR number in the README URL must appear as a `(#N)` suffix on a commit subject reachable from HEAD (skipped, not passed, when git is unavailable — the `in_tree_inventory` precedent).
- [ ] `docs/media/README.md` lists the SVG in its asset table with what it is, that it is hand-authored rather than captured, and the rule for changing it; `docs/artifacts.md:108`'s `docs/media/` row states the new file count and size, and `uv run python scripts/verify_ml_evidence.py` reports the row OK against the index.
- [ ] docs/architecture.md's firewall paragraph states the plant location and the analysed-package set the import-contracts task recorded (the temp-tree plant; the widened root_packages), so no sentence in it is stale at this merge.
- [ ] docs/artifacts.md's docs/media/ row count equals the git index after the SVG lands (tests/scripts/test_verify_ml_evidence.py green).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Open a PR from branch `phase-20-architecture-exhibit` with a title like `task 20.20: the as-built architecture picture and the contract → prompt → pr exhibit`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/C/collated-portfolio.md §(B) items B4 and B5 [B4 raised by P1 G, P2 G, P4 G, X2 G, X1 N; B5 by X1 G, X2 fold, P3 N, P1 M-3 fold]; audits/review-2026-08-19/C/p1-backend-hiring-manager.md §2 "12:00–14:00 — docs/architecture.md" [VERIFIED 146 lines — "This is the document I wanted first"] + §7 GOOD 4 (one click from the top) + §7 GOOD 10 (file size will be asked about); audits/review-2026-08-19/C/x1-front-door-reproduction.md §3.4 (architecture.md "is not linked from the README's first screen — only in 'What this is' and the footer"; 1,089 words per §6), §4 "Other builders" ("the workflow artifacts (task contract → prompt) are linked once and never shown"), §5 GOOD 7 (a 15-line contract excerpt + the matching prompt header + the PR it produced, branch `claude/…`, gate green) + §5 NICE 14; audits/review-2026-08-19/C/x2-narrative-and-positioning.md §4 gap row "Architecture diagram (image) — ASCII only; `DESIGN.md` §1.1 diagram is the *target* arch" + §6 proposal 7 (an as-built SVG of the layering plus the firewall arrow); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 1 row 1.14 (C/B4 + C/B5, size S, measurement "three links resolve; a reader verifies agent authorship in git in 30 s"); audits/review-2026-08-19/D/synth-ambition.md §FM-6 (the contract→prompt→PR triple shown, not linked); README.md:76 (`## What it is`), :84 (the architecture link, now a one-line pointer), :85 (20.12's reserved `<!-- ANCHOR: … inlines the as-built layering diagram here. -->`), :59 (`## How it was built — who did what`), :73 (the one workflow-artifact line, linked and never shown), :74 (20.12's reserved `<!-- ANCHOR: … shows a contract, its prompt and the merged pull request inline. -->`), :62 (the owner-ratified authorship paragraph), :162 (the footer link); docs/architecture.md:11-21 (the ASCII layering block), :51-56 (the `meetings/` paragraph), :89-91 (the generated `frontend/src/types/api.ts`), :104-118 ("Enforced boundaries" — the four contracts and their backing tests), 146 lines at HEAD; .importlinter:20-26 (`[importlinter:agents_must_not_import_engine]`, `name = Agents must not import engine`); DESIGN.md:7-12 (the Task 19.1 demotion banner), :49 (§1.1 Component diagram — the target architecture); `wc -l` at HEAD: meetings/manager.py 3,989, orchestrator/game.py 3,193; audits/audit-phase-19-planning.md:170-174 (the monolith decompositions on the recorded backlog); docs/media/README.md:1-10 (the two-row asset table); docs/artifacts.md:108 (the `docs/media/` registry row promises "1.7 MB / 3 files"); scripts/verify_ml_evidence.py:2110 + :2163 + :2171 (`_STATED_FILES`) + :2174-2202 (`inventory_problems`) and tests/scripts/test_verify_ml_evidence.py:1402-1420 (the row-count gate a fourth file under `docs/media/` turns red); agent_prompts/task-19-2-in-code-truth.md:1-16 (the generated prompt header shape) against tasks/phase-19.md:314-361 (its contract) and the merged PR https://github.com/dkdan10/AiLibi/pull/328), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
