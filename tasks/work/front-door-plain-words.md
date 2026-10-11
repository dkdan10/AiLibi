# The front door in plain words, with the GIF in place of the clip

**Status:** ready

## Outcome

On 2026-10-11 the owner answered the visitor-wording survey by number (`tasks/decision-2026-10-11-visitor-wording.md`
section 1; each letter is that item's option in `tasks/decisions-2026-10-11-visitor-wording/survey.md`, (a) always "keep
as is"). This card carries ten answers, verbatim: "1. B" and "4. B" (README halves), "16. Keep the byline, but don't
have to  specify what each agent did, because the roles changed throughout so less might be more.", "17. I think go with
GIF / Hero Images. The Video is a lot of work for little payoff when a viewer can go right to the demo page anyway.
Remove the WebM", "18. B. Plain words, focus on readability and air on brevity.", "20. C", "21. A", "22. C", "23. B" and
"24. B". Read with the orchestrator's readings (section 2) and its rulings at card review (section 2b, each reversible
by the owner's word): the README gains its tagline (1) and results link (4), keeps its byline over an undivided "Who did
what" (16), shows the GIF, not the WebM (17), reads plainly (18) and gives the missed bars one sentence, figures to
`docs/history.md` (20); lessons loses its markers (21), the case study gains a ruling (22), the guide a sourced
deception claim and the latest audit first (23), the policy pages two true sentences (24).

Follow-throughs that keep a sentence true, stated in Results, each reversible by a word: `README.md:33`'s "and
deception" softens with item 23's claim; `README.md:58`'s "traces one decision" follows item 22; the guide names the tab
"Results" (4) and drops "hand-picked, not scored," (`docs/reading-guide.md:69-70`), which item 5 corrects in the viewer,
but keeps its "9p2i seed 19" names (`:74-76`), as item 6 renames games in the viewer only and `check_featured_exhibits`
(`scripts/check_doc_facts.py:5553`) binds them. The orchestrator's rulings carried here (section 2b): the per-agent
passage goes from the README only, every other page that says who did what being a record that stays as it is,
`docs/lessons.md:7` and the case study's opening (`docs/ownership-case-study.md:3-6`) among them (2b.9); the guide's
sentences carrying a term the README retires follow it (2b.8); every guide audit entry gets plain link text (2b.7); two
parts of item 18 stay out (2b.6).

## Evidence

Every `path:line` resolves at `f223b9fe` (`survey.md` is the survey named above); counts are re-derived at the head that
states them; no rendered prompt, transcript text or seed-band prefix was printed. `check_doc_facts.py` exits 0 at base.

- **Answers.** `tasks/decision-2026-10-11-visitor-wording.md:15-43`, `:49-66`, `:73-97` (2b), `:99-106` (order),
  `:108-123`; `survey.md:13`, `:21`, `:53`, `:55`, `:57`, `:61`, `:63`, `:65`, `:67`, `:71`, `:152-160`.
- **README.** `README.md:3` (byline, unlinked), `:5`, `:11`, `:13` (caption, opens "*9p2i seed 19, …", links the clip),
  `:17` (raw "in [its own era](…)"), `:19-31` (six number forms), `:33`, `:35`, `:37`, `:49-52`, `:56`, `:58`, `:110`,
  `:112` (six backticked stamps); `CONTRIBUTING.md:10-11` wraps.
- **Ceilings.** `scripts/check_doc_facts.py:1003-1013` (lowered only); `wc -w`: README 1,587 of 1,600, guide 1,339 of
  1,350, lessons 1,444 in 800 to 1,500. A scratch `docs/reading-guide.md` with the fixed changes (every cell restyled,
  "100 of 100 (100%)" and "0 of 198 (0%)" included; row `:29`; the deception line; "Results"; "Four audits") counts
  1,347, 1,343 without "hand-picked, not scored, and"; its audit entries `:122-132` run 25, 35, 40 words, filenames as
  link text; retired README terms at `:12-13`, `:51-53`. `grep -c 'assert '`: 813 and 52.
- **Checks.** `scripts/check_doc_facts.py:1449`, `:1490`, `:1571-1646`, `:1648-1659` (stamps); `:4024`, `:4055-4057`
  (report: 61 ejections, 46 of impostors, 36 evidence-backed); `:2889` (the guide held to the README row by row),
  `:2940`, `:558-575`, `:683-734`, `:3078`, `:3096`, `:3119`, `:3216`, `:3314`, `:3497`, `:5446` (stems `:915-922`),
  `:306`. `eval/vote_correctness.py:11-13` counts impostor ejections, not ballots, so `survey.md:157`'s "ballots naming
  an impostor" misnames 0.783. `docs/history.md:167-179`, `:209-224` lack 50 of 96, 43 of 85, "against 34 of 46" and
  "the rule returns a finding". `tests/scripts/test_public_recording_provenance.py:157-161`, `:202-228`, `:249-255`,
  `:684-752`; `tests/scripts/test_check_doc_facts.py:1711`, `:1831`, `:1900`, `:3245-3251`; 43 README `_substitute`
  calls (AST count; 33 quote lines rewritten here, 12 in the samples paragraph).
- **Media.** `docs/media/spectator-journey.webm` (620,047 bytes, linked only from `README.md:13`);
  `docs/media/provenance.json:21`; `docs/media/README.md:3-7`, `:16-17`, `:44-56`, `:93`, `:112-135`;
  `docs/artifacts.md:114` ("1.6 MB / 7 files"); `frontend/e2e/media.spec.ts:21-22`, `:27-29`, `:119-122`, `:130`,
  `:517-600`, `:663-717`, `:930-1138` (the clip; "As-agent" `:1023`), `:1140-1173` (the GIF, using none), `:813-815`.
- **Items 21 to 24.** `docs/lessons.md:1`, `:10`; `docs/glossary.md:21`;
  `tasks/decision-2026-09-24-stage-b-wave.md:1555-1558` (gate record), `:1612-1620` (the ruling), `:246-247` (the
  declined proposal); `tasks/work/promote-round-3.md:652`, `:705` (54 files, 0 differing);
  `docs/ownership-case-study.md:3-6`, `:8-126`, `:69-102` (exhibit); `docs/reading-guide.md:73`, `:120-132`, `:93`
  (verified at `audits/audit-phase-19-input-claude.md:199`); `SECURITY.md:5-6` against `README.md:5`;
  `CONTRIBUTING.md:9-11` (reviewers are AI agents, `docs/workflow.md:63-66`); `docs/deployment.md:193-195`.

## Acceptance

Each item names its mechanism and the planted case that turns it red; each new test is seen red first.

- [x] **The wording pin.** A new helper in `tests/scripts/test_check_doc_facts.py` reads each page through `strip_links`
  (`scripts/check_doc_facts.py:1878`), drops `*` and backticks, collapses whitespace and returns, by page, required
  strings missing, retired ones present and order cases broken (word boundaries; (f) case-folded); empty on the
  checkout. Planted: `README.md:17`'s era link restored fails on "its own era"; `CONTRIBUTING.md:9-11` restored fails.
  - `README.md`. Required: "Recorded AI social deduction" under the title; "See the results"; the byline byte for byte
    as `:3`. Retired: "Inspect results and decisions", the six stamps, "in its own era", "ML corpus", "body identifier",
    "temporal repair", "default-off", "vote correctness 0.783", "0.5922 against 0.60", "finding" (f), "against 34 of
    46", "50 of 96 = 0.5208", "43 of 85 = 0.5059", "missed 0.40"; under `## Who did what` only, "Claude Code", "Codex".
  - `docs/reading-guide.md`. Required: "Results shows each set's figures" (`:73`), "Deception: demonstrated in earlier
    recordings", "Four audits"; order case, read raw: the list's first link targets the 2026-10-10 audit. Retired:
    "Results & cases", "strongest capability on display", "hand-picked, not scored"; any `audit-` token after
    `strip_links`, a filename as link text (2b.7); the README's retired terms it carries, "in its own era", "ML
    corpus", "body identifier", "temporal repair", "default-off" (2b.8).
  - Retired on `docs/lessons.md` "OWNER: confirm", "OWNER: end"; required on `docs/ownership-case-study.md` "Keep the
    comparison records"; on `SECURITY.md` "There is no hosted instance" retired, the demo's address required; on
    `CONTRIBUTING.md` "a human review as the gates" retired. `docs/history.md`: the verdict checks.
- [x] **1: the tagline.** `README.md:1` is unchanged and the next non-blank line reads "Recorded AI social deduction".
  Mechanism: the pin's README row. Planted: the tagline deleted, or moved below the byline, fails naming README.md.
- [x] **4: "See the results".** `README.md:5`'s link reads "See the results", its address unchanged; the guide names the
  tab "Results". Mechanism: the pin. Planted: "Inspect results and decisions" or "Results & cases" restored fails.
- [x] **16: the byline kept, the work undivided.** The byline stays byte for byte, linked to nothing new; only the
  README's passage moves (2b.9): under `## Who did what`, one sentence naming no agent product keeps both honesty facts,
  e.g. "Daniel Keinan directed the project and decided what was accepted, without hand-writing the production code; AI
  agents wrote it, and the audits are AI reviews, not human assurance." Mechanism: the pin. Planted: "Claude Code
  implemented" under the heading fails, naming the section; the old paragraph, or the byline linked, fails.
- [ ] **17: the GIF under the still, the WebM gone.** The README embeds `docs/media/spectator-journey.gif` under the
  still, plain alt text. Deleted: the WebM, its link, the spec's clip (walk, cut, frame probe, `CLIP_*`, every helper
  only it used, ffmpeg's too), its provenance entry, row, prose and budget; the GIF's row: "README image"; the recipe
  installs chromium only; the artifacts row re-derived; `.webm` stays in the placement inventory. The trimmed spec runs
  once at the head, after the viewer cards (the banner pin, `media.spec.ts:813-815`); a changed asset lands with digest,
  capture revision and row, or Results says none did. Mechanism: `test_public_recording_provenance.py:724` (placement),
  `:138` (hashes), lint, `tsc:check`. Planted: no GIF embed, an empty `.webm` or a digest off by one fails.
- [x] **18: one number style.** Every fraction in both tables, figure and Before cell, reads "k of n (p%)", p rounded as
  the win-rate check rounds (`round(100 * k / n)`): the survey's "394 of 397 (99%)". Win-rate cells keep "36% (4p1i)",
  which `check_repeated_claims` reads on every claim page. One helper renders the form; `check_result_sources`,
  `partition_figure`, `check_process_rows` (the page's cells parsed, the page unchanged) and the Before checks compare
  through it; a new style rule refuses "k/n", "k / n" or "= 0." in either table. Planted: "394 of 397 (98%)" fails by
  row; a scorecard value edited fails; the vent Before cell put back as "24 / 44 = 55%" in both tables fails the rule.
- [x] **18: plain words, identifiers in the manifests.** Plain: the row labels (the guide's twins with them), the era
  sentence (dated plain names; its last sentence kept), the leak paragraph, the caption (scene first, set and seed
  after), the report example (what each number counts), the samples paragraph (the model named, each set's MANIFEST
  linked for its stamps); the guide's sentences carrying a retired term follow (2b.8), today
  `docs/reading-guide.md:12-13`, `:51-53`. Following: the claim constants; the report templates (from the report's three
  ejection counts); `check_sample_provenance`'s stamp half (each MANIFEST linked; any `\bv\d+\b` or `_v\d+` token,
  backticked or not, one the manifests record); `check_dialect_terms`; the caption's anchor and pins. Mechanism: those
  checks and the pin. Planted, each failing: "v5" or "`v5`" in the samples paragraph; a MANIFEST link removed; "36 of
  46" edited; "ML corpus" in the guide; a changed room word (`test_public_recording_provenance.py:568`).
- [x] **20: one sentence on the README, the figures in the history.** `README.md:35` and `:37` become one sentence with
  no figure, no verdict word and no "innocent" or "wrongful" ejections without a recorded count: targets written before
  measuring were missed twice; the owner adopted the first recording anyway, in writing, and nothing from the second; a
  link to the history page. `docs/history.md` gains baseline 8's 50 of 96 and 46 and baseline 9's 43 of 85 and 42, each
  count in its own sentence, "11 of those 20 were the meeting's own reporter, against 34 of 46" and "the rule returns a
  finding"; `check_verdict_passage`'s home moves there, the per-baseline case and planted hunks following. Mechanism:
  `check_verdict_passage`, `check_verdict_figures`, `check_finding_figures`, the pin's README row. Planted:
  `README.md:35` restored verbatim in a scratch copy fails, naming README.md; "Innocent ejections fell from 46 to 21" on
  the README fails; history's "34 of 46" edited fails; the 46 beside "50 of 96 = 0.5208" moved to 47 fails.
- [x] **21: the owner's voice, confirmed.** Both marker lines leave `docs/lessons.md`, the page in its band, the
  glossary's owner entry unchanged. Mechanism: `git diff <base> -- docs/lessons.md` shows only the two marker lines
  removed; the pin; `check_front_door_budgets`. Planted: a marker restored fails; a word changed shows in the diff.
- [x] **22: the case study adds the recent ruling.** One section in the page's order (problem and options, evidence,
  judgment, implementation, limits), from the memo and the promotion card's Results only: whether to delete each
  superseded round's candidate recordings once a newer one lands, the earlier proposal, the advice to keep, "Keep the
  comparison records", round 2's 54 files kept identically, limits worded as what those records do not claim. Every
  existing line stays, opening and exhibit included (2b.9; Results notes the opening names one ruling and one drafter).
  Mechanism: `git diff <base> -- docs/ownership-case-study.md` shows additions only; `check_relative_links`;
  the exhibit tests (`test_check_doc_facts.py:5300`, `:5309`); the pin. Planted: a link misspelled; the opening edited.
- [x] **23: the claim sourced, the latest audit first.** `docs/reading-guide.md:93` reads "Deception: demonstrated in
  earlier recordings", linking the audit that verified it, without "the strongest capability on display"; "Four audits,
  in this order" opens with the audit of 2026-10-10; every entry's link text is plain words (e.g. "the finished-state
  audit of 2026-10-10"), the path in the target only (2b.7); row `:29` reads plainly (the survey's "Learned behaviours
  the ML program set out to show"). Mechanism: the pin and its order case, `check_results_agreement`,
  `check_guide_line_citations`. Planted: the old claim restored; the entry moved second; any filename as link text.
- [x] **24: two true sentences, topics kept.** `SECURITY.md:5-6` says the one hosted copy is the static demo (recorded
  games; no backend, accounts or API) and the API stays on loopback; `CONTRIBUTING.md:9-11` says CI is the gate and
  separate AI reviewers check each change, the owner deciding what is accepted and published. Mechanism: the pin.
  Planted: each old sentence restored fails by page.
- [x] **Both ceilings hold; no check weakens.** README at most 1,600 words, the guide at most 1,350, lessons in band,
  `_FRONT_DOOR_BUDGETS` unchanged. The guide's plan: 1,343 after the fixed changes and the `docs/reading-guide.md:69-70`
  drop; the lead entry at most 25 words; the older three, link text now plain words, cut from 100 words to at most 80,
  each keeping its link and "What it proves" claim, old against new in Results; the sentences 2b.8 moves and the twin
  labels add no words in total; so at most 1,348. Further trims fall on the older three first (2b.7), then on a sentence
  listed old against new; the README pays for its GIF and labels from items 16 and 20; if that fails, stop and ask,
  never dropping a checked figure. Planted hunks follow moved text, assertions kept; Results counts them and gives the
  `grep -c 'assert '` totals of both test files at base and head, head not lower. Mechanism: `check_front_door_budgets`,
  `_readme_rebuilt`'s count assertion. Planted: either page one word over; a stale hunk.
- [x] **Nothing else moves; the live strings and the bundle diff are stated.** `git diff --stat <base>` lists only
  Expected scope's files, no never-written path and no `VIEW_MODEL_VERSION` change; the PR body lists every live string,
  old against new, and the bundle diff built at the merge base and the head in one checkout (expected none; the measured
  diff governs). Perturbed: the caption's tick edited by one in a scratch copy fails.
- [x] **One bounded mutation pass, and the gate record.** One pass over the listed classes (dropped filter or wrapper,
  swapped collection, comparison made a None test, kind or key read made a constant, dropped tuple member, swapped
  branches, loaded source read as its literal, message arguments) over the number-form helper, style rule, verdict home,
  report templates, stamp rule, caption anchor and wording pin; survivors killed or reported; Results and the PR quote
  the rows. CI's green run at the exact head, by run id, is the gate record (memo 8.7 item 1).

## Constraints

**Rules every change keeps.** Viewer copy lives in `SPECTATOR_COPY`, which this card never writes; its pages read in
plain words, with no task or audit id, no unexplained term and no threshold arithmetic, any needed term defined in
`docs/glossary.md` or avoided. Role-correctness is reported and never a gate. Nothing under `engine/`, `agents/`,
`meetings/`, `observation/`, `orchestrator/`, `llm/`, `eval/`, `training/`, `experiments/`, `replays/` or
`tests/fixtures/` moves: no recorded byte, `AILIBI_*` lever or prompt registry bump. Every production line has a test
that goes red when neutered; no test is weakened (a pin following reworded text, assertion kept, is not). No live
provider call; `.env` is never read. Memo 8.7: CI's green run at the exact head is the gate record (no local
`check.sh` at the final head, no card-only gate commit); message-argument survivors are nonblocking after the first
fix round; counts only, never a rendered prompt, transcript text or seed-band prefix.

**Not in scope.** The viewer (items 3, 5 to 15, 25, the viewer halves of 1 and 4); items 2 and 19 keep as is. Two
parts of item 18, by 2b.6: the process scorecard page's opening sentence, generated from
`eval/process_scorecard.py:190`, which this wave does not write, stays (a later card may reword the generated
preface); the survey's direction word per README row (`survey.md:155`) is declined, since the sources state no
direction and the doctrine does not declare improvement from one recording. Also out: the guide's bar paragraph
(`docs/reading-guide.md:32-44`; item 20 names the README's, `survey.md:61`) but for a term 2b.8 reaches,
`docs/ml-program.md`, the topics, the glossary's owner entry, the case study's title and existing lines, the three held
halves. Another README sentence changes only if a stranger needs another page to parse it, listed old against new.

**One writer per file, across the three cards and the header card.** Section 2b's order, binding and verbatim
(`tasks/decision-2026-10-11-visitor-wording.md:99-106`): "`GuidedTour.tsx`: header card, then `viewer-browse-wording`,
then `viewer-meeting-results-wording` (step 3's one word). `PublicResults.tsx` and its test:
`viewer-meeting-results-wording` alone (it calls the set-name helper the browse card exports). `BeliefPanel.tsx` view
names (item 8's words at its four lines): `viewer-meeting-results-wording`, which also carries item 11 there.
`PrivateReasoning.test.tsx`, `journey.spec.ts`, `MindInspector.test.tsx`, `EvidencePanel.test.tsx`: the browse card,
then the meeting card. `media.spec.ts`: the header card if it changed a selector, then the browse card (the banner pin),
then `front-door-plain-words` (the clip removal). `copy.ts` and `copy.test.ts`: the header card, the browse card, the
meeting card, in different groups. Items 2 and 19 are kept as is and are no card's work." Of these this card writes
`frontend/e2e/media.spec.ts` only, last, after the browse card's banner pin (`:813-815`), which the item-17 capture run
reads; the clip's "As-agent" (`:1023`) leaves with the clip. By the decision's section 3, `viewer-header-source-link`
merges first, writing the GIF, the stills, `provenance.json`, `docs/media/README.md` and the media row of
`docs/artifacts.md`; this card writes them last. `docs/glossary.md`: the meeting card's entries, then this card's. This
card alone writes the rest of Expected scope and merges last, after merging `main` (never rebasing), re-deriving every
count, string and asset; `tasks/README.md` and the Status line are the orchestrator's.

**Delivery and publication.** Branch `work/front-door-plain-words`, one PR into `main`, merged or fast-forwarded,
never squashed or amended after push; each commit body carries `Card: tasks/work/front-door-plain-words.md`
immediately followed by the exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`; the PR fills every
template section. Merging publishes the README, its pages and media, and `.github/workflows/pages.yml` rebuilds the
bundle. The owner's answers of 2026-10-11 are the publication decision: the orchestrator merges once reviews pass and
the PR body states every live string, old against new, and the bundle diff file by file.

**Stop and ask** if the plan above cannot hold a ceiling without dropping a checked figure; a check cannot follow the
text without weakening; a label needs a judgment no source gives; the viewer's results tab is not "Results"; the capture
changes an asset beyond the viewer's words, or cannot run; a served label or `VIEW_MODEL_VERSION` would change; an
unmerged card the map does not order writes a file here; or a sentence needs a decision the owner did not give.

## Expected scope

- Front door: `README.md`, `docs/reading-guide.md`, `docs/history.md`, `docs/lessons.md`,
  `docs/ownership-case-study.md`, `SECURITY.md`, `CONTRIBUTING.md`; `docs/glossary.md` only for a needed term.
- Media: `docs/media/spectator-journey.webm` (deleted), `provenance.json`, `docs/media/README.md`, the media row of
  `docs/artifacts.md`, `frontend/e2e/media.spec.ts`; the GIF and stills only if the capture changes them.
- Checks: `scripts/check_doc_facts.py` (claim constants, number form and style rule, verdict home, report templates,
  stamp rule, docstring), `tests/scripts/test_check_doc_facts.py` (following hunks, the wording pin),
  `tests/scripts/test_public_recording_provenance.py` (caption anchor and pins, placement); this Results.

Four files sit outside the decision's surface list (`tasks/decision-2026-10-11-visitor-wording.md:118`), by warrant:
the media spec by reading 17 (`:52-54`) and 2b's order; the artifacts row, whose "1.6 MB / 7 files" the WebM's
deletion makes untrue and `scripts/verify_ml_evidence.py` reads; the provenance tests, which pin caption and placement;
`docs/glossary.md`, under the copy rule, after `viewer-meeting-results-wording`. Other follow-through goes in Results;
a file outside, to the orchestrator. Never written: the packages Constraints names, `api/`, `frontend/src/`, every
other `frontend/e2e/` spec, every MANIFEST, the scorecard, census and profile pages, `docs/deployment.md`,
`docs/ml-program.md`, `docs/architecture.md` and its SVG, `scripts/build_demo_bundle.py`, `.github/`, `DESIGN.md`, the
audits, `tasks/README.md`.

## Record impact

**What moves:** front-door prose; both tables' labels and number form; the doc-facts code and test pins that follow
them; the WebM with its capture code, provenance entry and rows; other media only if the capture changes them. **What
stays unchanged:** every recording, MANIFEST, config and report; the corpus and ML artifacts; the scorecard, census and
profile pages and JSON; the public payload and every `data/` file of the bundle; `VIEW_MODEL_VERSION` (a served label
change is a stop-and-ask); prompts, levers, defaults, ladder tip, era registry, pre-registrations, verdicts, topics, the
exhibit. **Future behaviour, evaluation:** none. **Publication:** as Constraints states.

## Validation

From the branch's worktree, each exit code quoted; `<base>` is the merge base with `main` at the final review.

```sh
uv run python scripts/check_doc_facts.py; uv run python scripts/validate_task_docs.py
uv run pytest tests/scripts/test_check_doc_facts.py tests/scripts/test_public_recording_provenance.py -q
wc -w README.md docs/reading-guide.md docs/lessons.md; uv run python scripts/verify_ml_evidence.py  # never --complete
(cd frontend && npm run tsc:check && npm run lint && npm run e2e)
(cd frontend && AILIBI_CAPTURE_MEDIA=1 npx playwright test e2e/media.spec.ts)  # once, at the head
git ls-files docs/media; git grep -n -i -E 'webm|ffmpeg|recordVideo' -- frontend/e2e docs/media README.md
git diff --stat <base>; git diff <base> -- docs/lessons.md docs/ownership-case-study.md  # markers out; additions only
git diff --exit-code <base> -- engine agents meetings observation orchestrator llm api eval training experiments \
  replays tests/fixtures frontend/src docs/process-scorecard.md docs/deployment.md docs/ml-program.md
uv run python scripts/build_demo_bundle.py --out <dir-base>   # at <base>, then at the head into <dir-head>
diff -r <dir-base> <dir-head>                                 # file by file into the PR body
```

## Results

Implemented on `work/front-door-plain-words` from base B = `7d781f8e` (main had not moved at the push), pull
request #513. Commits, oldest first: `453438a2` (item 20: the missed bars' one sentence, the figures and the verdict
home on the history page), `e30b6981` (item 17: the GIF shown, the WebM removed), `5f36b70c` (item 23 and its
follow-through on the guide), `adcde449` (item 18: plain words, stamps to the manifests), `4564fbdf` (item 18: one
number style), `cca4e5b3` (items 1, 4, 16, 21, 22, 24 and the wording pin), `6b8f9fb2` (the mutation pass's fix
round), then this Results commit. Each commit passes `check_doc_facts.py` and both test files on its own; they were
put in this order before the first push, and no pushed commit was rewritten.

**Sections relied on.** This card; `tasks/decision-2026-10-11-visitor-wording.md` sections 1, 2 (readings 16, 17,
18, 20, 22), 2b (rulings 6 to 9 and the binding order) and 3; the survey's rows 1, 4, 16 to 18, 20 to 24 and Appendix
A; `tasks/decision-2026-09-24-stage-b-wave.md` 8.7 (process) and 8.9 (the ruling of item 22) with its earlier
proposal; `tasks/work/promote-round-3.md` Results (round 2 kept, 54 files, 0 differing); `docs/architecture.md`
"Packages" (only `scripts/`, `tests/`, the docs and one e2e spec move; no package below them) and "Enforced
boundaries" (the observation boundary row keeps its wording); `docs/workflow.md`; AGENTS craft rules 2, 4, 5 and 6.

### Decisions

Each is the implementer's reading inside the card, reversible by a word.

1. **Row labels, old against new, in both tables** (the claim constants follow): "Committed sample replays that
   reconstruct byte-identically" to "Sample games that replay byte for byte"; "Eject ballots citing a line the voter
   held about their target (9p2i)" to "Eject ballots citing what the voter saw or heard about the accused (9p2i)";
   "Eject ballots carrying a valid citation, a turn or an observation id (9p2i)" to "Eject ballots with a valid
   citation of a statement or sighting (9p2i)"; "Impostor win rate, committed samples" to "Impostor win rate, sample
   games"; "Ejection accuracy with engine-certified proof of the ejectee's role, against without (9p2i)" to
   "Impostors among those ejected, with and without proof of their role (9p2i)"; "Correct 9p ejections riding an
   ejectee-specific vent sighting" to "Impostors ejected after a reported sighting of them venting (9p2i)"; the
   guide's row 29 to the survey's "Learned behaviours the ML program set out to show". Kept as plain already:
   "Observation boundary checks", the top-suspect, no-reason, voter-wrote, partner and learned-tactical rows.
2. **Dated plain names.** The era sentence reads "The shown 9-player set was recorded 2026-10-09 under the adopted
   gameplay changes; the 4-player set and the ML training games were recorded 2026-09-22.", its last sentence kept;
   the leak paragraph says "in the 2026-09-22 recordings" (the baseline-9 recordings, dated) and "the opening prompts
   name each body by a label that reveals when it died" (`docs/observation-contract.md`: the internal body ID
   encodes the death tick); the samples paragraph drops "at baseline 9". So neither "baseline" nor "era" is on the
   README any more; `check_dialect_terms` is unchanged and its two cases now plant an unlinked use.
3. **The caption** opens on its scene and then reads "This is 9p2i seed 19, the game the demo's guided tour opens
   on, from the 2026-10-09 record (9p2i)"; the provenance tests find it as the first line under the hero picture.
4. **The report example** states counts: "records 61 ejections; 46 removed an impostor, 36 of those 46 with
   evidence against that player on the meeting's record" (`eval/vote_correctness.py`: co-occurrence on the meeting's
   record, not attribution). Its three templates read `total_ejections`, `impostor_ejections` and
   `evidence_backed_impostor_ejections`.
5. **README.md:33** reads "and deception in older recordings", not "earlier": `test_media_hashes_and_labels_are_current`
   refuses "earlier recording" on the README, a guard about the hero picture being historical.
6. **The missed bars** link to `docs/history.md#evidence-honesty-phase-20`; the history page's new sentences are
   "Pooled over its four recorded sets, accuracy without that proof read 50 of 96 = 0.5208 with 46 innocent
   ejections." and "Pooled over the four sets, accuracy without engine-certified proof read 43 of 85 = 0.5059 with
   42 innocent ejections, a movement these samples cannot call real.", and the adopting-record paragraph now carries
   "11 of those 20 were the meeting's own reporter, against 34 of 46" and "the rule returns a finding".
7. **The number form** rounds with Python's `round`, as the win-rate check does (half to even: 1 of 8 is 12%). The
   partner row's zero is the firewall's (`_PARTNER_BALLOTS_CAST`): the pin's first count, 10, is the ballots the
   model wrote naming a partner before the rewrite to a skip.
8. **The guide's audits, old against new** (2b.7). Lead entry, new, 22 words: "[The finished-state audit of
   2026-10-10]" with "what the finished project shows and does not, each figure with its command". The older three,
   100 words to 73: the fresh-clone audit 25 to 18 ("an independent audit from a fresh clone" folded into the link
   text "The fresh-clone audit", "raw" dropped); the reconciliation 35 to 25 ("its reconciliation against a second,
   independent audit by a different model" to the link text "Its reconciliation with a second model's audit";
   "one of its own sources' headline terms is refuted" to "a source's headline term is refuted"); the ML close 40 to
   30 ("the close of the ML program" to the link text "The ML program's close"; "pre-registered" and "so none became
   the default" dropped, the README stating the latter). Each keeps its link and its "What it proves" claim.
9. **The case study's section** is appended after the page's closing paragraph, as "## A later ruling: keep the
   comparison records", its five parts led in bold in the page's order, so "What later evidence limits" keeps its
   closing paragraph. Its facts are the memo's 8.9 amendment and earlier proposal and the promotion card's Results;
   its limits say keeping a round adopts nothing (the route field stays a recorded setting) and decides nothing about
   play. By 2b.9 the opening stays; it now names one ruling and one drafter, "drafted by Codex", while the page holds
   two rulings and this card's agent drafted the added section.
10. **The GIF** sits under the still's caption, linked to the demo as the still is, alt text "The same game playing
    from its first tick to the meeting"; its row reads "README image". The directory is 988,029 bytes in 6 files,
    so the media README says 1.0 MB and the registry row "1.0 MB / 6 files".
11. **The Status line** stays as the orchestrator set it (this card's Constraints), although the dispatch asked for
    `done`.

### Acceptance evidence

Each planted proof edited the checkout, ran the named check and restored it (a scratch script; the outputs below are
the check's own lines, cut).

- **The wording pin.** `_wording_problems(root)` in `tests/scripts/test_check_doc_facts.py` reads the six pages
  through `strip_links`, drops `*` and backticks and collapses whitespace; it returns, by page, required strings
  missing, retired ones present (word boundaries, "finding" case-folded) and the order cases (the tagline under the
  title, the byline's bytes, the "Who did what" section, the guide's first audit link, no `audit-` token as link
  text). At H it returns `{}`; on the six pages as they stood at B it names 45 problems (README 24, guide 15, lessons
  2, case study 1, SECURITY 2, CONTRIBUTING 1). Twenty-one planted cases put one replaced text back on a scratch page
  (`test_the_wording_pin_refuses_each_restored_text`), among them the era link restored ("carries 'in its own era'")
  and CONTRIBUTING's sentence restored; one more moves the 2026-10-10 entry second.
- **1, 4, 16, 21, 24.** Held by the pin's rows; planted: the tagline deleted, the tagline below the byline, "Inspect
  results and decisions", "Results & cases", the byline linked, "Claude Code implemented" under the heading, the old
  per-agent paragraph, a lessons marker, SECURITY's and CONTRIBUTING's old sentences, the demo address removed; each
  fails naming its page. `git diff --numstat B -- docs/lessons.md` prints `0 2` (the two marker lines); a planted word
  change prints `1 3`. Lessons counts 1,420 words, inside 800 to 1,500.
- **17.** Deleted: the WebM, its README link, the spec's clip (the recorded walk, the cut, the frame probe,
  `CLIP_SETTLE_SECONDS`, `CLIP_SECONDS`, `CLIP_BITRATE`, `CLIP_MAX_BYTES`, `ffmpegBinary`, `runFfmpeg`, `probeFfmpeg`,
  `videoDurationSeconds`, `videoDimensions`, `frameDistances`, `extractFrame`, the `homedir` and `readdirSync`
  imports), its provenance entry, row, prose and budget; the recipe installs chromium only. `git grep -c -i -E
  'webm|ffmpeg|recordVideo' -- frontend/e2e docs/media README.md` prints nothing (0). Outside audits and tasks the
  word remains only in the generated `agent_prompts/task-20-39-hero-media.md` (history, never hand-edited), the
  2eed2e92 README the rebuild test quotes, and the placement test's inventory and its planted clip. Planted: the GIF
  embed removed fails `test_media_placement_claims_follow_actual_frontdoor_links` (`['spectator-journey.gif']`); an
  empty `spectator-journey.webm` fails it ("media placement table does not match the visual inventory"); a digest off
  by one fails `test_media_hashes_and_labels_are_current` (`['spectator-journey.gif']`). `tsc:check` and `lint` exit
  0. The capture run is not done (box open; Limitations).
- **18, one number style.** `fraction_figure` renders "k of n (p%)"; `check_result_sources`, `partition_figure`,
  `check_process_rows` (through `scorecard_fraction`, the page's "k/n = rate" cells parsed) and the partner row compare
  through it; `check_number_style` (check 23) holds every fraction in a figure or before cell to its percentage and
  refuses `k/n`, `k / n` and a printed `= 0.…` rate in any value cell. Red first: run over B's tables it named every
  old-form cell, 36 errors on the two tables before they were restyled. Planted: "394 of 397 (98%)" fails three ways
  by row (the style rule, the agreement check, the process row); the scorecard's "6/702 = 0.0085" made "7/702 =
  0.0100" fails both tables ("recomputes to '7 of 702 (1%)'"); the vent before cell back as "24 / 44 = 55%" in both
  tables fails the rule once per table, and nothing else.
- **18, plain words.** Planted, each exit 1 of `check_doc_facts.py`: "v5" in the samples paragraph ("names the
  prompt-set version 'v5', which no row's `prompt_versions` column records (recorded: v6, v8)"); "`v5`" (the same);
  the 9p2i MANIFEST link removed ("does not link replays/samples/9p2i/MANIFEST.md"); "36 of those 46" made "35" ("does
  not state '36 of those 46 with evidence against that player'"); a label put back (three errors naming the row);
  "ML corpus" in the guide (the pin); "MedBay" made "Admin" in the caption (`test_the_captions_scene_is_the_recorded_one`
  fails, "the replay has ['MEDBAY']"). The caption's tick moved by one either way is a planted case
  (`one-tick-later`, `one-tick-earlier`).
- **20.** Planted: the README's old paragraph 35 back on a scratch page fails the pin naming README.md ("carries
  '0.5922 against 0.60'", "'50 of 96 = 0.5208'", "'43 of 85 = 0.5059'", "'finding'"); "Innocent ejections fell from
  46 to 21." on the README fails `check_verdict_passage` naming README.md; history's "against 34 of 46" made "33"
  fails naming docs/history.md; the 46 beside "50 of 96 = 0.5208" made 47 fails `check_verdict_figures` at
  `docs/history.md:206`; history without "the rule returns" fails naming the page, which is the verdict home.
- **22.** `git diff --numstat B -- docs/ownership-case-study.md` prints `32 0`. Planted: a link misspelled
  (`promote-round3.md`) fails `check_relative_links`; the opening edited fails the pin. The exhibit tests pass.
- **23.** The pin's guide row and order case, with `check_results_agreement` and `check_guide_line_citations` green.
  Planted: the old deception claim, the entry moved second and a filename as link text each fail.
- **Both ceilings.** README 1,474 of 1,600 (B 1,587), guide 1,340 of 1,350 (B 1,339), `_FRONT_DOOR_BUDGETS`
  unchanged. Planted: the README one word over (1,601) and the guide one word over (1,351) each fail
  `check_front_door_budgets`; a README line a round-2 hunk quotes, edited, fails `_readme_rebuilt`'s count
  assertion. The rebuilt round-2 README equals `git show 2eed2e92:README.md` byte for byte, as at B. `grep -c
  'assert '`: `test_check_doc_facts.py` 813 at B, 857 at H; `test_public_recording_provenance.py` 52 at B, 63 at H.
  By AST, 46 tests and 6 constants of the first file follow moved text with their assertions kept, 27 are new and 3
  are renamed or replaced (`test_composite_stamp_names_every_arm_in_the_provenance_paragraph`, whose rule the
  stamps' move to the manifests retires, by `test_composite_stamp_arms_are_the_manifests_to_name`, and the two
  report-rate cases by the two report-count cases); in the second file 3 tests and 2 helpers follow and 1 is new.
- **Nothing else moves.** `git diff --stat B` lists the 15 files of Expected scope and this card. `git diff
  --exit-code --stat B -- engine agents meetings observation orchestrator llm api training experiments replays
  tests/fixtures frontend/src docs/process-scorecard.md docs/deployment.md docs/ml-program.md` exits 0, and so does
  the same over `docs/architecture.md`, its SVG, `scripts/build_demo_bundle.py`, `.github`, `DESIGN.md`, the audits,
  `tasks/README.md` and `docs/glossary.md`; the evaluation package is absent from the stat. `VIEW_MODEL_VERSION` is
  in `api/`, untouched. The demo bundle built at B and at H in this one checkout (`uv run python
  scripts/build_demo_bundle.py --out <dir>`): 110 files each, `diff -r` exits 0, all 72 `data/` files included.

### Validation

At H before this commit (`6b8f9fb2`), count-only: `check_doc_facts.py` exit 0; `validate_task_docs.py` exit 0 (110
work cards); the two test files 464 passed; `wc -w` README 1,474, guide 1,340, lessons 1,420; `verify_ml_evidence.py`
exit 0 (64 checks: 52 OK, 0 FAIL, 7 evidence-branch absent, 5 info); `tsc:check` 0; `lint` 0; `build_sample_report.py
--check` exit 0 on `samples/4p1i`, `samples/9p2i`, `ml_corpus/4p1i` and `ml_corpus/9p2i`; `verify_samples.sh` exit
0 (four sets of 50: both samples, both candidate rounds); `git ls-files docs/media` lists six files. Local `npm run
e2e` could not start a browser: Playwright 1.56.1 needs `chromium_headless_shell-1194`, which this machine does not
have, and installing it is a download this run does not make (15 failed at launch, 3 skipped); CI's "Frontend e2e
(Playwright)" job runs it. No local `check.sh` at the final head (memo 8.7 item 1); the gate record is CI's run at the
exact head of #513, cited there by run id.

### Mutation pass

One pass, 39 mutants, exactly the listed classes: dropped filter or wrapper 7, swapped collection 5, None test or
inverse 4, key read made a constant 6, message argument made a constant 5, dropped tuple member 3, swapped adjacent
branches 3, loaded source read as its literal 6. Each was one exact replacement, run against the two test files and
restored (a scratch script). First round: 34 killed, 4 survived, 1 not applied (W7, whose line the formatter had
rewrapped, run in the second round). The survivors were source reads no test moved: N3 (the replay count read as the literal 100), N6 (the
page-cell parser's message argument), N7 (the cited count read as 397), N8 (the partner total read as 198). The fix
round `6b8f9fb2` adds a removed replay, a moved cited-count pin, a moved partner pin and the parser's exact message;
on re-run N3, N6, N7, N8 and W7 are killed. Final: 39 of 39 killed.

| Target | Mutants (class: first test to fail) |
| --- | --- |
| number-form helper | N1 None: `test_a_fraction_over_no_population_raises`; N2 drop `round`: committed; N3 literal: `test_a_removed_replay_moves_the_count_figure`; N4 swap value and before: committed; N5 key constant: committed; N6 message: `test_a_scorecard_cell_of_another_shape_is_refused`; N7 literal: `test_the_cited_count_pin_moves_the_citation_figure`; N8 key constant: `test_the_partner_ballot_pin_moves_the_row` |
| style rule | S1 drop the column filter: committed; S2 drop the before header: `test_a_fraction_without_its_percentage_fails`; S3 swap fractions for all cells: committed; S4 None inverse: committed; S5 message: `test_each_retired_number_form_is_refused`; S6 branch: committed; S7 drop the guide: `test_the_vent_before_cell_in_its_old_form_fails_the_rule` |
| verdict home | V1 home made the README: committed; V2 None inverse: committed |
| report templates | R1 drop the evidence claim: `test_evidence_count_above_its_denominator_fails_loud`; R2 key constant: committed; R3 message: `test_eval_report_count_drift_reaches_the_report_example`; R4 literal counts: the same; R5 two entries' keys swapped (collection): the same |
| stamp rule | T1 branch: `test_samples_paragraph_naming_an_unrecorded_stamp_detected`; T2 swap sets: `test_samples_paragraph_naming_recorded_stamps_passes`; T3 drop filter: the same; T4 message: `test_samples_paragraph_without_a_manifest_link_detected`; T5 literal sets: the same |
| caption anchor | C1 drop the blank-line filter: `test_the_front_door_names_the_pictured_game_in_plain_words`; C2 literal README: `test_a_caption_naming_another_scene_fails_by_name`; C3 tick constant: the same (`one-tick-later`) |
| wording pin | W1 drop the marks wrapper and W2 drop `strip_links`: `test_the_wording_pin_refuses_each_restored_text`; W3 None inverse: the same; W4 swap folded for retired: the same; W5 drop "Codex": the same; W6 key constant: `test_the_front_door_wording_pin_holds`; W7 message: `test_the_wording_pin_refuses_each_restored_text`; W8 branch: `test_the_front_door_wording_pin_holds`; W9 literal root: `test_the_wording_pin_refuses_each_restored_text` |

"committed" is `test_committed_front_door_passes`.

### Limitations

- **The capture has not run.** Item 17 asks for one run of the trimmed spec at the head after the viewer cards
  (`viewer-browse-wording`, PR #511, writes the banner pin this spec reads; `viewer-meeting-results-wording`, PR
  #512). Neither had merged at this head, and this machine lacks the Playwright browser build the spec needs (see
  Validation). The run is a stop-and-ask item: the next round merges `main` after both viewer cards, runs
  `AILIBI_CAPTURE_MEDIA=1 npx playwright test e2e/media.spec.ts` once, and lands any changed asset with its digest,
  capture revision and row. Their words move what the meeting still and the GIF show, so a change is expected.
- **Merging `main` later** re-derives every count here. PR #511 also writes `ReplayPicker.tsx`, which
  `check_featured_exhibits` reads; its diff changes the loading label, not the `FEATURED_GAMES` list. The guide names
  the tab "Results", which is the viewer's name only once PR #511 lands. My `media.spec.ts` hunks are the clip's, apart
  from the banner pin's lines PR #511 edits, so the binding order holds once `main` is merged.
- **Out of scope by the card and kept:** the guide's bar paragraph still says "finding" and gives the bar arithmetic
  (`docs/reading-guide.md:32-44`); the scorecard page's generated opening (2b.6); the README's "Four learned impostor
  policies" paragraph; the media README's provenance paragraph naming v6 prompts and a v8 ballot.
- The labels and the case study's added section are written by an AI agent from the sources named above; no source
  states them word for word.
