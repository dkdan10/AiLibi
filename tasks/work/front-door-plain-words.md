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

- [ ] **The wording pin.** A new helper in `tests/scripts/test_check_doc_facts.py` reads each page through `strip_links`
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
- [ ] **1: the tagline.** `README.md:1` is unchanged and the next non-blank line reads "Recorded AI social deduction".
  Mechanism: the pin's README row. Planted: the tagline deleted, or moved below the byline, fails naming README.md.
- [ ] **4: "See the results".** `README.md:5`'s link reads "See the results", its address unchanged; the guide names the
  tab "Results". Mechanism: the pin. Planted: "Inspect results and decisions" or "Results & cases" restored fails.
- [ ] **16: the byline kept, the work undivided.** The byline stays byte for byte, linked to nothing new; only the
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
- [ ] **18: one number style.** Every fraction in both tables, figure and Before cell, reads "k of n (p%)", p rounded as
  the win-rate check rounds (`round(100 * k / n)`): the survey's "394 of 397 (99%)". Win-rate cells keep "36% (4p1i)",
  which `check_repeated_claims` reads on every claim page. One helper renders the form; `check_result_sources`,
  `partition_figure`, `check_process_rows` (the page's cells parsed, the page unchanged) and the Before checks compare
  through it; a new style rule refuses "k/n", "k / n" or "= 0." in either table. Planted: "394 of 397 (98%)" fails by
  row; a scorecard value edited fails; the vent Before cell put back as "24 / 44 = 55%" in both tables fails the rule.
- [ ] **18: plain words, identifiers in the manifests.** Plain: the row labels (the guide's twins with them), the era
  sentence (dated plain names; its last sentence kept), the leak paragraph, the caption (scene first, set and seed
  after), the report example (what each number counts), the samples paragraph (the model named, each set's MANIFEST
  linked for its stamps); the guide's sentences carrying a retired term follow (2b.8), today
  `docs/reading-guide.md:12-13`, `:51-53`. Following: the claim constants; the report templates (from the report's three
  ejection counts); `check_sample_provenance`'s stamp half (each MANIFEST linked; any `\bv\d+\b` or `_v\d+` token,
  backticked or not, one the manifests record); `check_dialect_terms`; the caption's anchor and pins. Mechanism: those
  checks and the pin. Planted, each failing: "v5" or "`v5`" in the samples paragraph; a MANIFEST link removed; "36 of
  46" edited; "ML corpus" in the guide; a changed room word (`test_public_recording_provenance.py:568`).
- [ ] **20: one sentence on the README, the figures in the history.** `README.md:35` and `:37` become one sentence with
  no figure, no verdict word and no "innocent" or "wrongful" ejections without a recorded count: targets written before
  measuring were missed twice; the owner adopted the first recording anyway, in writing, and nothing from the second; a
  link to the history page. `docs/history.md` gains baseline 8's 50 of 96 and 46 and baseline 9's 43 of 85 and 42, each
  count in its own sentence, "11 of those 20 were the meeting's own reporter, against 34 of 46" and "the rule returns a
  finding"; `check_verdict_passage`'s home moves there, the per-baseline case and planted hunks following. Mechanism:
  `check_verdict_passage`, `check_verdict_figures`, `check_finding_figures`, the pin's README row. Planted:
  `README.md:35` restored verbatim in a scratch copy fails, naming README.md; "Innocent ejections fell from 46 to 21" on
  the README fails; history's "34 of 46" edited fails; the 46 beside "50 of 96 = 0.5208" moved to 47 fails.
- [ ] **21: the owner's voice, confirmed.** Both marker lines leave `docs/lessons.md`, the page in its band, the
  glossary's owner entry unchanged. Mechanism: `git diff <base> -- docs/lessons.md` shows only the two marker lines
  removed; the pin; `check_front_door_budgets`. Planted: a marker restored fails; a word changed shows in the diff.
- [ ] **22: the case study adds the recent ruling.** One section in the page's order (problem and options, evidence,
  judgment, implementation, limits), from the memo and the promotion card's Results only: whether to delete each
  superseded round's candidate recordings once a newer one lands, the earlier proposal, the advice to keep, "Keep the
  comparison records", round 2's 54 files kept identically, limits worded as what those records do not claim. Every
  existing line stays, opening and exhibit included (2b.9; Results notes the opening names one ruling and one drafter).
  Mechanism: `git diff <base> -- docs/ownership-case-study.md` shows additions only; `check_relative_links`;
  the exhibit tests (`test_check_doc_facts.py:5300`, `:5309`); the pin. Planted: a link misspelled; the opening edited.
- [ ] **23: the claim sourced, the latest audit first.** `docs/reading-guide.md:93` reads "Deception: demonstrated in
  earlier recordings", linking the audit that verified it, without "the strongest capability on display"; "Four audits,
  in this order" opens with the audit of 2026-10-10; every entry's link text is plain words (e.g. "the finished-state
  audit of 2026-10-10"), the path in the target only (2b.7); row `:29` reads plainly (the survey's "Learned behaviours
  the ML program set out to show"). Mechanism: the pin and its order case, `check_results_agreement`,
  `check_guide_line_citations`. Planted: the old claim restored; the entry moved second; any filename as link text.
- [ ] **24: two true sentences, topics kept.** `SECURITY.md:5-6` says the one hosted copy is the static demo (recorded
  games; no backend, accounts or API) and the API stays on loopback; `CONTRIBUTING.md:9-11` says CI is the gate and
  separate AI reviewers check each change, the owner deciding what is accepted and published. Mechanism: the pin.
  Planted: each old sentence restored fails by page.
- [ ] **Both ceilings hold; no check weakens.** README at most 1,600 words, the guide at most 1,350, lessons in band,
  `_FRONT_DOOR_BUDGETS` unchanged. The guide's plan: 1,343 after the fixed changes and the `docs/reading-guide.md:69-70`
  drop; the lead entry at most 25 words; the older three, link text now plain words, cut from 100 words to at most 80,
  each keeping its link and "What it proves" claim, old against new in Results; the sentences 2b.8 moves and the twin
  labels add no words in total; so at most 1,348. Further trims fall on the older three first (2b.7), then on a sentence
  listed old against new; the README pays for its GIF and labels from items 16 and 20; if that fails, stop and ask,
  never dropping a checked figure. Planted hunks follow moved text, assertions kept; Results counts them and gives the
  `grep -c 'assert '` totals of both test files at base and head, head not lower. Mechanism: `check_front_door_budgets`,
  `_readme_rebuilt`'s count assertion. Planted: either page one word over; a stale hunk.
- [ ] **Nothing else moves; the live strings and the bundle diff are stated.** `git diff --stat <base>` lists only
  Expected scope's files, no never-written path and no `VIEW_MODEL_VERSION` change; the PR body lists every live string,
  old against new, and the bundle diff built at the merge base and the head in one checkout (expected none; the measured
  diff governs). Perturbed: the caption's tick edited by one in a scratch copy fails.
- [ ] **One bounded mutation pass, and the gate record.** One pass over the listed classes (dropped filter or wrapper,
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

Filled by the implementation.
