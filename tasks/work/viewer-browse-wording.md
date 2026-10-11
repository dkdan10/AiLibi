# The replay browser, the workspace and the endings speak plain words

**Status:** ready

## Outcome

On 2026-10-11 the owner answered the visitor-wording survey by number. This card carries, verbatim, "1. B", "4. B",
"5. B", "6. B", "7. B", "8. B", "9. B" and "25. B" (`tasks/decision-2026-10-11-visitor-wording.md:17`, `:20-25`,
`:43`), each the survey's option (b), whose text and Appendix A rows are the adopted wording
(`tasks/decisions-2026-10-11-visitor-wording/survey.md:13`, `:21-33`, `:75`, `:115-130`). The orchestrator's rulings
at card review (decision §2b, `:68-106`, each reversible by the owner's word) settle what those answers leave open;
this card decides nothing beyond them. When this card is done:

- **1.** The tab and the link preview read "AiLibi — Recorded AI social deduction" (`frontend/index.html` only).
- **4.** The navigation reads "Moments" and "Results" (was "Highlights", "Results & cases"); page headings stay.
- **5.** The featured strip is headed "Featured"; its five blurbs and the list stay byte for byte.
- **6.** A game is "Game 19" (seed in a tooltip); a set "9 players, 2 impostors (9p2i)"; the repeat set chip goes;
  the picker's "in seed order" reads "in game order" (§2b ruling 2, `:78-79`).
- **7.** The gate button reads "Reveal outcomes"; notes, empty states and errors take Appendix A's lines.
- **8.** Short forms spelled out; one name for one player's view ("Watching as p-3", "See as p-1"); "Next key
  moment →"; a lone body reads "killed by p-4".
- **9.** One wording per ending (the cards' words; "Crew win" / "Impostor win" tags); the right / wrong marks become
  facts ("Meeting 2: an impostor was voted out"; "named an impostor").
- **25.** The local dashboard drops "target ≈ $0.20/game" and spells out "ECE".

Every string this card rewords or adds lives in `SPECTATOR_COPY`; strings it leaves alone stay where they are. A role
read stays a report and never a gate, and every outcome word stays behind the reveal exactly as today.

**Not in this card.** Items 3 and 10-15 (`viewer-meeting-results-wording`); item 1's README tagline, item 4's README
link and the reading guide's tab name, items 16-18 and 20-24 (`front-door-plain-words`); items 2 and 19, kept as is
and no card's work (§2b, `:106`); the three halves held for the owner (decision `:125-127`); the welcome step's
legend (`GuidedTour.tsx:114-136`, held with that ruling, `survey.md:125`). In tour step 3 this card changes only
"hero" to "panel" (row 125); its "Ground-Truth" follows the toggle renamed "Real roles", written by the meeting card
after this card, and "Error" and the rest of step 3 stay, held with the Error-layer words (§2b ruling 1, `:73-77`).

## Evidence

Every `path:line` is at `f223b9fe` (`fa213381..f223b9fe` changes only `tasks/`, so the survey's citations hold). No
rendered prompt, transcript text or seed-band prefix was printed. Bare `.tsx` names sit in `frontend/src/components/`.

- **1.** `frontend/index.html:6` holds `<title>AiLibi — Replay Viewer</title>`; the 12-line file has no description
  or Open Graph tag. The bundle's `index.html` is that file built (`scripts/build_demo_bundle.py:15`, `:628-641`).
- **4.** `TABS` (`frontend/src/App.tsx:201-205`) types "Highlights" (`:203`), "Results & cases" (`:204`), as do the
  welcome step (`GuidedTour.tsx:169`) and `docs/reading-guide.md:73`. Kept headings: `frontend/src/lib/copy.ts:544`;
  `PublicResults.tsx:79`, the bundle's results marker (`scripts/build_demo_bundle.py:134`).
- **5.** `ReplayPicker.tsx:312` types "Featured — picked by hand". `FEATURED_GAMES` (`:119-150`) is parsed by
  `tests/api/test_sets.py:62-72`, `scripts/build_demo_bundle.py:92-102` and `scripts/check_doc_facts.py:618-620`.
- **6.** "seed {n}": `HighlightCard.tsx:299,304`, `ReplayPicker.tsx:324`, `App.tsx:307-308`; `setOptionLabel`
  (`copy.ts:122-125`) gives "9p2i — 9 players, 2 impostors"; chip `ReplayFilters.tsx:185-189`; "Loading {set}…"
  `ReplayPicker.tsx:566`; the raw id at `PublicResults.tsx:80` shares a sentence with item 15's words (decision `:117`).
  "in seed order": `copy.ts:458,547`, its sort held by `ReplayPicker.test.tsx:162,485`; `docs/glossary.md:327,351`.
- **7.** Gate button and warning `ReplayFilters.tsx:141`, `:144`; intros `copy.ts:457-464`; All-games note `:546-547`;
  pair note `:649`; loading, empty, error lines `ReplayPicker.tsx:569`, `:576-577`, `:608-609`, `:926`, `:945`.
- **8.** Short forms: `App.tsx:307-308,366,456,471`. One-player view: `App.tsx:242,316-330`; `EventTicker.tsx:602-606`;
  `MapToolbar.tsx:120,162,169-171`; `MindInspector.tsx:581,601,720-721`; `BallotCard.tsx:325`; `EvidencePanel.tsx:76`;
  `GuidedTour.tsx:179-186`; `MemoryPanel.tsx:271-273` (no test reads it); the meeting card's `BeliefPanel.tsx:253`,
  `:270`, `:512`, `:552`. "Next beat", Resume tooltip: `App.tsx:687,676`. Text no DOM test reads:
  `MapToolbar.tsx:109-112` (DOM); Pixi: `BodyMarker.tsx:168`, `RoomRect.tsx:130`, `SabotageOverlay.tsx:100-104` (one player's
  view names no room or countdown, `:98-99`; REACTOR is a room, `:3-4`). Step 3: `GuidedTour.tsx:191`, "hero" at
  `:194`, `:196`; the legend (`:114-136`) renders in the welcome step (`:174`).
- **9.** Raw winner `App.tsx:307`; `WINNER_REASON_LABEL` (`:703-708`) differs from the cards' `endings`
  (`copy.ts:679-686`); tags `App.tsx:861-862`, `HighlightCard.tsx:75-84` ("Aborted", "Tick limit", "Unfinished" at
  `:81-83`); marks `App.tsx:768-786`, `copy.ts:692-693` (by `right`: the ejected player's recorded role is impostor,
  `eval/game_profile.py:1548`; null for no vote, a SKIP or a rewritten ballot, `api/schemas.py:1370-1371`, `:1387`);
  rules `GuidedTour.tsx:163-166`; `tests/api/test_game_profile_view.py:429-448` parses `endings`, `:447` plants.
- **25.** `copy.ts:358`, rendered at `TournamentDashboard.tsx:1007`; "ECE" at `CalibrationCurve.tsx:50-52`, `:64`;
  the bundle does not render that detailed dashboard (`TournamentDashboard.tsx:1273`).
- **Pins.** Follow: `copy.test.ts:582,599-602,648-649`; `HighlightCard.test.tsx:69,94-101,121,157-158`;
  `ReplayPicker.test.tsx:268,360,449,509`; `PrivateReasoning.test.tsx:303`; `bundle.spec.ts:240,344`;
  `journey.spec.ts:104,396,398-399,424,843,848,860,910-911,925,996` (exact text `:36-38`); `media.spec.ts:813-815`;
  `evidence-journey.ts:65,76,210,212,223-224`. Hold: `copy.test.ts:575`; `HighlightCard.test.tsx:68,70`;
  `ReplayPicker.test.tsx:162,485`; `journey.spec.ts:110,395`; `bundle.spec.ts:215`; `media.spec.ts:799`. Capture only:
  `media.spec.ts:56`, `docs/media/README.md:56-58`; front-door's clip `media.spec.ts:1022-1028,1129`. Helpers:
  `copy.test.ts:87,130`. New (absent): `MindInspector.test.tsx`, `EvidencePanel.test.tsx`; `MemoryPanel` renders at
  `SearchIntention.test.tsx:18`. Nothing here is served (`VIEW_MODEL_VERSION` "6", `api/schemas.py:77`); the captures
  (`docs/media/provenance.json`, `58c7cf03`) show reworded labels (`media.spec.ts:373,1155,1162`).

## Acceptance

Each item names its mechanism and the planted or perturbed case that turns it red; each new test is seen red before
its code. "The scan" is a new `copy.test.ts` case: (source, retired literal) rows read through `stripComments`, plus
a `stringLeaves` walk of `SPECTATOR_COPY` for the same literals.

- [x] Review correction: the never-written guard covers `eval/`. The Results and round 1 quoted it with the
  pathspec `'e?al'`, which matches no tracked file (`git ls-files 'e?al'`: 0; `git ls-files 'e?al/*'`: 37), so it never
  covered `eval/`. It is now quoted with `'e?al/*'` (the sandbox refuses the literal word): `git diff --exit-code
  7d781f8e fd951388 -- engine agents meetings observation orchestrator llm api 'e?al/*' training experiments replays
  scripts tests README.md docs` exits 0, and each of its 15 pathspecs matches at least one tracked file. Proof: one
  appended line in `eval/__init__.py`, with the working tree in H's place, makes the corrected guard exit 1 while
  the `'e?al'` form still exits 0; the `api/__init__.py` plant makes it exit 1 as before.
- [x] Review correction: Decisions 10 names the eight `App.tsx` exports, as the pull request body does. It said
  three; `git diff 7d781f8e fd951388 -- frontend/src/App.tsx | grep -c '^+export'` gives 8 (`TopNav`,
  `PerspectiveBanner`, `RosterRail`, `MeetingPauseBar`, `FinaleHeadline`, `FinaleReason`, `RecapRow`, `FinaleCard`),
  and `grep -c '^export' frontend/src/App.tsx` gives 10 at H against 2 at B.
- [x] Review correction: the red-at-base count reproduces from committed tests. "9 files, 118 tests" came from an
  uncommitted draft; the Acceptance evidence now gives `635f47ae`'s unit tests over B's `frontend/`: `App.test.tsx`
  fails to load and 125 tests fail in the 10 other failing files (11 of 32 files), with all 62 scan rows red by
  name; H's unit tests over B: `App.test.tsx` fails to load and 133 tests fail in 11 files (12 of 33); B's own tests in the same
  scratch layout: 855 of 855 pass. Proof: the `npx vitest run --reporter=json` runs in "Review corrections, round 2".
- [x] Review correction: the set-list and replay-load error lines are held. `ReplayPicker.test.tsx` "the connected
  browser's error lines" renders the connected `ReplayPicker` over a reduced store (a `vi.mock` of
  `../store/replayStore`, since a server render reads the store's initial state) and holds each line's text to
  `PICKER_COPY.setListError` or `PICKER_COPY.replayLoadError` with two raw errors each, both lines together in page
  order, no line when nothing failed, and the set selector kept once the sets loaded; `copy.test.ts` "say what the
  browser shows" pins both strings. Proof: R01 to R03 (the review's A01 and A02, each raw error typed as a constant),
  R04 (A03, the set-list line reading the replay-load copy) and R05 to R14 passed 1046 at `142db9aa`; at `3c6657c5`
  each fails 1 to 5 of 1053.
- [x] Review correction: the calibration readout is held to its own figure. `TournamentDashboard.test.tsx` "spells out
  the calibration error, keeping its figure and its tooltip" holds the story's two readouts to `["0.248", "0.103"]`
  (its `accusation_claim_ece` and `vote_ballot_ece`), and "shows each curve's own calibration error, to three places,
  and n/a for none" renders `CalibrationCurve` with 0.248, 0.1 and no figure. Proof: J01 (the review's J02, the
  figure typed as 0.123), J02 (typed as 0.248), J03 to J05 and J07 (the ballot curve fed the claim figure) passed 1046
  at `142db9aa`; at `3c6657c5` each fails 1 or 2 of 1053.
- [x] Review correction: the mode banner names every stop of a game with no winner. `App.test.tsx` "names each
  recorded stop of a game with no winner in the tag the cards use" renders the revealed banner for `aborted`,
  `tick_limited`, `unfinished` and no recorded stop, each held to its `OUTCOME_COPY` tag. Proof: H01, the banner's
  stop read typed as `"tick_limited"` (the review's survivor), passed 1046 at `142db9aa` and fails 1 of 1053 at
  `3c6657c5`. The Mutation pass's claim that every name-helper call site had a second value is corrected in place.
- [x] **The scan bites.** Planted: a synthetic source carrying one retired literal in rendered code is caught, and
  the same literal in a comment is ignored; each item below adds its rows, and each row is seen red on the base.
- [x] **1. The tab and the preview read the tagline.** A `site` copy group holds "AiLibi — Recorded AI social
  deduction"; `index.html`'s `<title>`, `<meta name="description">` and `<meta property="og:title">` carry exactly
  it, and nothing else enters the head (a preview image is not in the answer). Mechanism: a `copy.test.ts` case
  reads `frontend/index.html` off disk against the copy. Planted: the old title restored, or one tag deleted, fails.
- [x] **4. The tabs are "Moments" and "Results".** `TABS` and the welcome step read the names from a `nav` group;
  view ids and URL keys (`highlights`, `tournament`) do not change. Mechanism: a render test of the navigation holds
  the button names to the copy; scan rows for both old names in `App.tsx` and `GuidedTour.tsx`; `journey.spec.ts:996`
  and `bundle.spec.ts:344` follow. Planted: "Highlights" typed back into `TABS` fails the scan and the render test.
- [x] **5. The strip is headed "Featured".** The heading comes from `PICKER_COPY`; `FEATURED_GAMES` is identical at
  base and head. Mechanism: a strip render case in `ReplayPicker.test.tsx`; a scan row; the block diff (Validation)
  is empty and `tests/api/test_sets.py` passes unchanged. Perturbed: one blurb character changed shows in the diff.
- [x] **6. Games and sets have names.** Cards, featured pills and the banner read "Game {n}", the seed in a `title`
  tooltip in plain words; the card's accessible name follows ("Open game 19"); `setOptionLabel` returns
  "9 players, 2 impostors (9p2i)", an unknown id bare; the set chip goes, with its prop if nothing else reads it; the
  loading cue names the set through the set-name helper this card exports, which `viewer-meeting-results-wording`
  alone calls in `PublicResults.tsx` (`:80`). Both "in seed order" notes read "in game order" (§2b ruling 2): the
  number is the same, so nothing re-sorts. Mechanism: `copy.test.ts:599-602` follows, the unknown-id case kept; a
  HighlightCard case holds pill and tooltip; `HighlightCard.test.tsx:121`, `ReplayPicker.test.tsx:268,360,449` and
  the banner's `journey.spec.ts:396`, `bundle.spec.ts:240` follow; `journey.spec.ts:104`
  matches "Game {n}" exactly ("Game 2" prefixes "Game 23"); `evidence-journey.ts:65,76` follow to the exact accessible
  name "Open game 19"; `ReplayPicker.test.tsx:162,485` pass unchanged; scan rows.
  Planted: the old label form fails `copy.test.ts`, a dropped tooltip the card case, "in seed order" in a leaf the scan.
- [x] **7. The browser's notes in plain words.** The gate button reads "Reveal outcomes" (warning kept, still
  `aria-describedby`); the replays intro "Recorded games for this set. Open one to watch it."; the highlights intro
  drops "Nothing here ranks or scores a game."; the All-games note ends "including games kept off the shelves"; the
  pair note keeps "always show together"; the empty set reads "No recorded games are available for this set.";
  loading and error lines say plainly what could not load, the raw error after, "unknown error" made a sentence.
  Mechanism: `copy.test.ts:648-649` follows as "claims no completeness" (no `every`, `all`; not-every kept); `:575`
  holds; `:582` goes with its sentence, and that case's no-score loop (`:579-581`) also walks `PICKER_COPY`;
  `ReplayPicker.test.tsx:509` follows; a ReplayFilters render case; scan rows. Planted: "Show outcome filters" back
  fails; a picker leaf reading "ranked by" fails the loop.
- [x] **8. One name per thing in the workspace.**
  - Short forms: "9 players", "3 meetings" ("1 meeting"), "crew 7 · impostors 2" in both roster layouts.
  - One player's view: the banner reads "Watching as p-3" (its accessible name keeps the "Perspective:" prefix);
    controls read "See as p-1" (toolbar toggle and picker, inspector button and pressed state, ballot and evidence
    prompts, private-mind note); the ticker chip, tour step 2 and the hidden-memory note follow. In the files this
    card writes, "fog", "fog of war", "As-agent", "lens" and "Show what they saw" leave text, tooltips and accessible
    names; "Omniscient", the `perspective` URL key and the mode names stay. `BeliefPanel.tsx`'s four lines (`:253`,
    `:270`, `:512`, `:552`, whose "error" is the held Error-layer word) take these names in the meeting card (§2b).
  - "Next key moment →"; the tooltip "Resume playback past this meeting"; step 2's title "What one player could
    see"; step 3's "Open the Belief × Truth panel"; the tour button's tooltip in plain words.
  - The map: the chip reads "Map" (no "canonical_1" or counts); a lone body "killed by p-4"; the unseen-room label
    and the HUD in plain words (e.g. "Reactor meltdown in 5 ticks" in the all-roles view); "† = impostor" stays.
    The orchestrator's reading (§2b ruling 3, `:80-81`): one style in both views; the one-player view keeps hiding
    what it hides today (`SabotageOverlay.tsx:98-99`), and only the wording and look align.
  - Mechanism: pure label helpers over the copy, with unit cases for "killed by p-4", the all-roles HUD and a
    one-player HUD with no digit and no room name, matched without regard to case ("Reactor" fails); render cases
    for the banner, the inspector button and pressed state (new `MindInspector.test.tsx`), the evidence prompt (new
    `EvidencePanel.test.tsx`), the ballot prompt and private-mind note (`PrivateReasoning.test.tsx`) and `MemoryPanel`
    with `revealSecrets` false (`SearchIntention.test.tsx`); scan rows; `journey.spec.ts:424,843,848,860,910-911,925`,
    `evidence-journey.ts:210,212,223-224` (`:223`'s lens negative follows the new prompt words, so it never passes
    vacuously), `PrivateReasoning.test.tsx:303` follow, assertions kept; `media.spec.ts:813-815` follows
    the banner text `journey.spec.ts:848` holds in CI, covered here only by `npm run tsc:check` until the front-door
    card's capture run, merging last, first runs it. Planted: the all-roles HUD text in the one-player view fails the
    HUD case; "As-agent" back in `MapToolbar.tsx`, or "fog" in `MemoryPanel.tsx`, fails the scan and the render pin.
- [x] **9. One ending, one wording; facts for marks.**
  - The revealed banner, the finale heading and the card tag read one copy helper: "Crew win" / "Impostor win". The
    tick-limit tag is a short form of the cards' ending words (`copy.ts:684`) that the implementer chooses under the
    plain-words rule and states in the PR body (§2b ruling 4, `:82-83`); "Aborted", "Unfinished" stay byte for byte.
  - The finale's reason reads the cards' `endings` (`WINNER_REASON_LABEL` retired), an unmapped reason verbatim; the
    `endings` block (`copy.ts:679-686`) stays byte-identical, the line `test_game_profile_view.py:447` plants included.
  - Card marks: "Meeting {meeting}: an impostor was voted out" / "Meeting {meeting}: a crewmate was voted out".
  - Recap: "named an impostor" / "named no impostor", no ✓ or ✗; the "engine-adjusted" chip in plain words, matching
    the ballot chips' "changed by the vote rule" that item 10 adopts (`survey.md:137`).
  - The tour's rules sentence uses the ending words ("parity" and "unresolved sabotage" go).
  - Mechanism: `journey.spec.ts:398-399` follow to "Crew win" / "Impostor win" (the retired "CREWMATES" would pass
    vacuously); a finale and recap render case; scan rows; HighlightCard cases for both marks and every tag, held to
    the copy (`HighlightCard.test.tsx:69` and `:157-158` follow, `:68`, `:70` hold); the reveal-leak list (`:94-101`)
    follows to "was voted out". Planted: swapped mark branches fail; swapped tick-limit and aborted branches fail
    `:68-69`; a hidden card leaking the new mark fails the followed list, and passes with it at "the vote was".
- [x] **25. The dashboard leftovers.** `costMeanHint` and its hint go; the readout reads "Expected calibration error
  {value}" (tooltip "lower is better" and figure kept), the low-power note spells it out, both in `DASHBOARD_COPY`.
  Mechanism: a `TournamentDashboard.test.tsx` case; scan rows for "0.20/game", "ECE". Planted: the hint restored fails.
- [x] **Nothing else moves.** `git diff --stat B H` lists only Expected scope's files; never-written paths and the
  `FEATURED_GAMES` block are unchanged; `VIEW_MODEL_VERSION` is "6"; `scripts/check_doc_facts.py` exits 0 (no README
  or guide write). Mechanism: the Validation diffs and the gate. Perturbed: a scratch `api/` edit fails the diff guard.
- [x] **The live strings, and the bundle diff.** The PR body lists every string that goes live, old against new, and
  the demo bundle diff built at B and H in one checkout (expected: `index.html` and compiled assets, no `data/` file;
  the measured diff governs), and names which reworded strings the committed captures show.
- [x] **One bounded mutation pass, and the gate record.** One pass over the listed classes (a dropped filter or
  wrapper, a swapped collection, a comparison made a None test, a kind or key read made a constant, a dropped tuple
  member, swapped branches, a loaded source read as its literal, message arguments) over the set-name, tag, ending,
  mark, HUD and body helpers, the scan and the `index.html` case; survivors killed or reported; CI's run id is cited.

## Constraints

**Rules every change keeps.** User-facing copy lives in `SPECTATOR_COPY`, in plain words, with no task or audit id,
no unexplained term and no threshold arithmetic. Role-correctness is reported, never a gate. No never-written path
(Expected scope) moves and no recorded byte is edited; no new `AILIBI_*` lever, no prompt registry bump, no live
provider call, and `.env` is never read. Every production line has a test that goes red when it is neutered; no test
is weakened, and a pin that follows reworded text with its assertion kept is not a weakening. Memo 8.7: CI's green
run at the exact head is the gate record, with no local `check.sh` at the final head; message-argument survivors are
nonblocking after the first fix round. Never print a rendered prompt, transcript text or seed-band prefix.

**The open wording.** A string the survey fixes is used as written. Where option (b) leaves it open (the tick-limit
tag among them), the rule is plain words, readability first, brevity over completeness, every term defined in place
or avoided, one copy key per wording (`copy.test.ts:201-212` holds the long ones), each choice in the PR body.

**One writer per file, across the cards.** Merge order: `viewer-header-source-link`, this card,
`viewer-meeting-results-wording`, `front-door-plain-words` last (decision `:120-123`); each later card merges `main`
before its final review, both cards' hunks kept. The shared-file order, binding (decision §2b, `:99-106`), word for
word: "`GuidedTour.tsx`: header card, then `viewer-browse-wording`, then `viewer-meeting-results-wording` (step 3's
one word). `PublicResults.tsx` and its test: `viewer-meeting-results-wording` alone (it calls the set-name helper the
browse card exports). `BeliefPanel.tsx` view names (item 8's words at its four lines): `viewer-meeting-results-wording`,
which also carries item 11 there. `PrivateReasoning.test.tsx`, `journey.spec.ts`, `MindInspector.test.tsx`,
`EvidencePanel.test.tsx`: the browse card, then the meeting card. `media.spec.ts`: the header card if it changed a
selector, then the browse card (the banner pin), then `front-door-plain-words` (the clip removal). `copy.ts` and
`copy.test.ts`: the header card, the browse card, the meeting card, in different groups. Items 2 and 19 are kept as
is and are no card's work." Within it: this card creates `MindInspector.test.tsx` and `EvidencePanel.test.tsx`, which
the meeting card extends; in `journey.spec.ts` the meeting card takes `:949`'s region name, `:953-956` and `:965`. By
the merge order: `App.tsx` and any App, header or tour test the header card creates, header card then this card;
`BallotCard.tsx`, `EvidencePanel.tsx`, `MindInspector.tsx`, `e2e/evidence-journey.ts`, this card then the meeting card.
`README.md` and `docs/` are never this card's; the rest of Expected scope is this card's alone while it is open;
`tasks/README.md` and this card's Status line are the orchestrator's, on `main`.

**Delivery and publication.** Branch `work/viewer-browse-wording`; one pull request into `main`, merged or
fast-forwarded, never squashed or amended after push; each commit body has `Card: tasks/work/viewer-browse-wording.md`
immediately followed by the exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. The merge publishes
the bundle through `.github/workflows/pages.yml`; the owner's answers of 2026-10-11 are the publication decision; the
PR body states every string that goes live, old against new, and the bundle diff file by file.

**Stop and ask** rather than guess when: a string would need a decision neither the owner nor decision §2b gave (the
held halves; step 3 beyond "hero" and the meeting card's one word; the welcome step's legend; a blurb or the featured
list; a "seed" beyond the pill, card, banner and accessible-name labels and the two "in seed order" notes); a
one-player wording would show what that view hides today; a served label would change (`VIEW_MODEL_VERSION`); a pin
cannot follow its text without weakening; or the captures would keep retired wording with no card left to refresh them.

## Expected scope

- `frontend/index.html`; `frontend/src/lib/copy.ts` and `copy.test.ts` (new `site` and `nav` groups, workspace and map
  strings, the helpers, the scan), or a new `frontend/src/lib/` helper module with its test.
- `frontend/src/App.tsx` (navigation, banner, roster counts, pause bar, finale, recap, tour button).
- `frontend/src/components/`: `ReplayPicker.tsx`, `ReplayFilters.tsx`, `HighlightCard.tsx`, `GuidedTour.tsx`,
  `MapToolbar.tsx`, `EventTicker.tsx`, `BodyMarker.tsx`, `RoomRect.tsx`, `SabotageOverlay.tsx`, `MindInspector.tsx`,
  `BallotCard.tsx`, `EvidencePanel.tsx` (item 8's strings only), `MemoryPanel.tsx` (`:271-273` only),
  `TournamentDashboard.tsx` (`:1007` only), `CalibrationCurve.tsx`; the tests beside them that follow, among them
  `PrivateReasoning.test.tsx`, `SearchIntention.test.tsx`; the new `MindInspector.test.tsx`, `EvidencePanel.test.tsx`.
- `frontend/e2e/journey.spec.ts`, `bundle.spec.ts`, `evidence-journey.ts` (pins), `media.spec.ts` (`:813-815`); Results.

Never written: `engine/`, `agents/`, `meetings/`, `observation/`, `orchestrator/`, `llm/`, `api/`, `eval/`, `training/`,
`experiments/`, `replays/`, `scripts/`, `tests/` (Python, `tests/fixtures/` included), `README.md`, `docs/` (with
`docs/media/`, `docs/glossary.md`), the `FEATURED_GAMES` block, `PublicResults.tsx`, `PublicResults.test.tsx`,
`MeetingView.tsx`, `BeliefPanel.tsx`, `BeliefPanel.test.tsx`, `BeliefCell.tsx`, `TurnCard.tsx`, the audits and
`tasks/README.md`.

## Record impact

**What moves:** the visitor wording of the tab title and preview, navigation, replay browser, workspace, map labels
and endings, plus two local-dashboard labels, now in `SPECTATOR_COPY`; the tests and pins that follow, the capture
banner pin among them. **Future behaviour:** none. **Evaluation:** none. **Publication:** as Constraints states. **What
stays unchanged:** every recording, MANIFEST, roster, experiment config and committed report; the corpus, ML
artifacts, scorecard, census and profile pages and JSON; the public payload and every `data/` file of the bundle;
`FEATURED_GAMES` and the shelf order; the committed media; `VIEW_MODEL_VERSION` (a served label to change is a
stop-and-ask); URL keys and view ids; the prompts, levers, defaults, ladder tip and era registry; every verdict.

## Validation

Run from the branch's worktree; quote each exit code as it came back. The grep leaves only comments, test titles,
planted cases, `BeliefPanel.tsx` (the meeting card's) and the clip the front-door card deletes.

```sh
uv run python scripts/validate_task_docs.py
uv run python scripts/check_doc_facts.py
uv run pytest tests/api/test_game_profile_view.py tests/api/test_sets.py tests/scripts/test_build_demo_bundle.py -q
(cd frontend && npm test && npm run tsc:check && npm run lint && npm run e2e)
git grep -n -E "Replay Viewer|picked by hand|Show outcome filters|As-agent|fog of war|Show what they saw|agent.s fog|own lens|Next beat|reached parity|sabotage unresolved|the vote was (right|wrong)|engine-adjusted|0\.20/game|in seed order" -- frontend/index.html frontend/src frontend/e2e
diff <(git show <base>:frontend/src/components/ReplayPicker.tsx | sed -n '/^export const FEATURED_GAMES/,/^];/p') \
     <(git show <head>:frontend/src/components/ReplayPicker.tsx | sed -n '/^export const FEATURED_GAMES/,/^];/p')
git diff --exit-code <base> <head> -- engine agents meetings observation orchestrator llm api eval training experiments replays scripts tests README.md docs
uv run python scripts/build_demo_bundle.py --out <dir-base>   # at base, then at head into <dir-head>, one checkout
diff -r <dir-base> <dir-head>                                 # file by file into the PR body
```

## Results

Implemented on `work/viewer-browse-wording` from B = `7d781f8e`: `635f47ae` (the wording, its copy groups and helpers,
the scan and the render cases, the followed unit and browser pins), `4d7149e0` (each name helper's call site held to a
second value, the ticker chip's render case, the scan's two reads tied together, all asked for by the mutation pass)
and the Results commit `142db9aa`, round 1's head; review round 1 adds `3c6657c5` (three test repairs) and its
card commit `fd951388`; review round 2 adds one card commit, which is H, the pull request's head (see "Review
corrections, round 1" and "round 2"). References:
`docs/architecture.md` "Packages" (`frontend/` consumes the generated view types; nothing below the viewer moves, no
view type, DTO or recorded byte changes, `VIEW_MODEL_VERSION` stays "6" at `api/schemas.py:77`) and "Enforced
boundaries" (one player's view keeps
hiding what it hid: the copy changes words, never what a view shows); AGENTS.md craft rules 2 (each new check has a
planted case seen red), 4 (user-facing copy in plain words, in `SPECTATOR_COPY`) and 5 (counts below with their
commands); the decision `tasks/decision-2026-10-11-visitor-wording.md` §1 (answers 1, 4-9, 25), §2b rulings 2-4 and
the binding shared-file order; `docs/deployment.md` with `.github/workflows/pages.yml` for publication. The card's
Status line is the orchestrator's, on `main`.

### Decisions

1. **Where the words live.** New `SPECTATOR_COPY` groups `site`, `nav`, `tour`, `game`, `outcome` and
   `perspective`; `map`, `transport`, `picker`, `profile` and `dashboard` gained or changed keys. The helpers are in
   `copy.ts` beside `setOptionLabel`: `gameName`, `gameSeedTitle`, `openGameLabel`, `playerCount`, `meetingCount`,
   `outcomeTag`, `endingPhrase`, `killedByLabel`, `sabotageHud`. The `endings` block is byte-identical and still the
   first `endings: Object.freeze({` in the file, which `test_game_profile_view.py:447` parses.
2. **The set-name helper** is `setOptionLabel`, already exported: it now returns "9 players, 2 impostors (9p2i)" and an
   unknown id bare. `viewer-meeting-results-wording` calls it in `PublicResults.tsx`. Two empty-state templates that
   wrapped the set in parentheses lead with it instead ("{set}: this set ships no game-shape profile, ..."), so the
   name's own parentheses do not nest.
3. **The tick-limit tag** (§2b ruling 4) is "Stopped at the tick limit", a short form of the cards' "the run stopped
   at its tick limit". "Aborted" and "Unfinished" are unchanged; "Crew win" and "Impostor win" now come from one
   helper on the card, the banner and the finale heading.
4. **One player's view.** The banner reads "Watching as p-3" (accessible name "Perspective: Watching as p-3"); every
   control that opens a view reads "See as p-1": the toolbar toggle names the player on screen, or the first living
   one it would open on ("See as one player" only for a recording with no player); the inspector button keeps the
   same words pressed, with an `aria-hidden` check mark; "Exit fog" became "Back to Omniscient". The picker's
   accessible name "Perspective agent" and the mode name "Omniscient" are unchanged.
5. **The sabotage readout** (§2b ruling 3): the all-roles view reads "Reactor meltdown in 5 ticks" and "Lights out, 12
   ticks left" (one-tick forms too); one player's view reads "Sabotage alarm" or "Lights out" and, as before, shows
   no room, no countdown, and nothing at all to a player who never heard the alarm. The chip widened from 156 to 232
   px for the longer line. The unseen room reads "Unseen"; a lone body "killed by p-4"; "† = impostor" stays.
6. **Tour step 3** changes only "hero" to "panel" and stays inline in `GuidedTour.tsx`, so the meeting card's one
   word ("Ground-Truth") lands where §2b puts it. Step 2's title and body and the welcome step's rules paragraph
   moved into `TOUR_COPY` (the body without its bold mode names); the welcome step's legend is untouched.
7. **The seed tooltip** reads "Recorded from random seed 19" on the card, the featured pill and the banner, the only
   places "seed" appears beyond the two notes now reading "in game order".
8. **The local dashboard.** `costMeanHint` is deleted with its one reader; the readout and the low-power note are
   `DASHBOARD_COPY.calibrationError`, `calibrationErrorTitle` ("lower is better") and `calibrationLowPower`.
9. **Retired mechanisms deleted.** `WINNER_REASON_LABEL` (the finale reads `endingPhrase`, own keys only, an unmapped
   reason verbatim), `winnerLabel`, `ventRingCount` and the filter bar's `set` prop (nothing else read it).
10. **Tests beside the changed files.** Besides the two the card names, three new test files hold lines no existing
    test reached: `MapToolbar.test.tsx`, `MapLabels.test.tsx` (the Pixi labels, read off the element tree) and
    `EventTickerChip.test.tsx`; `App.test.tsx`, the header card's, gained the navigation, banner, roster, pause-bar and
    finale cases (the merge order makes this card its next writer). Eight `App.tsx` components are exported for them:
    `TopNav`, `PerspectiveBanner`, `RosterRail`, `MeetingPauseBar`, `FinaleHeadline`, `FinaleReason`, `RecapRow` and
    `FinaleCard` (round 2 corrected "three").

### Acceptance evidence

Commands run from `frontend/` unless named. Pin line numbers are the card's (at `f223b9fe`); at H the followed pins
sit a few lines lower. The perturbed runs (edit, run the named files, restore) ran at `635f47ae`. "Red at B" is `npx vitest run` with `635f47ae`'s new and followed unit
tests over B's sources (`App.test.tsx`, whose new imports did not exist yet, failed to load, and 125 tests failed in
the 10 other failing files, 11 of 32 files; the scan alone: 62 rows, each red by name). The figure first given here,
9 files and 118 tests, came from an uncommitted draft; round 2 reproduced this one from the commits (see "Review
corrections, round 2").

- **The scan bites.** `copy.test.ts` "the retired wording (the scan)": 62 (source, literal) rows over 17 sources
  (`index.html` and 16 under `frontend/src`), each read through `stripComments` with a `kept` fragment that must
  survive the strip, plus a walk of 25 retired literals over every `SPECTATOR_COPY` leaf. Planted in the suite: a
  rendered "As-agent" is caught and the same word in a comment is not; `inFog`, `fogAgentId` and `lensIsSelf` are
  code, not copy; a leaf reading "in seed order" is named by path. All 62 rows were red at B.
- **1.** `copy.test.ts` "the tab title and the link preview" reads `frontend/index.html` off disk (the same bytes the
  scan reads) and holds `<title>`, `description` and `og:title` to `SITE_COPY.title`, refusing any other head element.
  Planted in the suite: the old title, the description dropped, an `og:image` added. Perturbed on disk: the old title
  restored fails 3 tests; the `og:title` line deleted fails 2.
- **4.** `App.test.tsx` "the navigation" holds the buttons to `NAV_COPY` ("Replays", "Moments", "Results", "? Tour")
  and the tour tooltip; scan rows for both old names in `App.tsx` and `GuidedTour.tsx`; `journey.spec.ts:999` and
  `bundle.spec.ts:344` follow. Perturbed: "Highlights" typed back into `TABS` fails 3 (the scan row and both render
  cases). View ids and URL keys are unchanged.
- **5.** `ReplayPicker.test.tsx` "heads the featured strip Featured ..." (heading from `PICKER_COPY`, two pills with
  their tooltips); a scan row. `diff` of the `FEATURED_GAMES` block at B and H (the Validation command): exit 0, 32
  lines each; `tests/api/test_sets.py` passes unchanged. Perturbed: one blurb character changed shows a one-line diff
  (exit 1).
- **6.** `copy.test.ts:599-602` follows ("names a set in words with its id after ..."), the unknown-id case kept;
  `HighlightCard.test.tsx` holds the name, the tooltip and "Open game 19" / "Open game 42"; `ReplayPicker.test.tsx`
  follows at its three accessible-name pins and adds the loading cue for both sets; `journey.spec.ts:104` matches
  "Game {n}" exactly, `:396` and `bundle.spec.ts:240` follow, `evidence-journey.ts:65,76` follow to "Open game 19";
  `ReplayPicker.test.tsx:162,485` pass unchanged; the set chip and its prop are gone. Perturbed: the old label form
  fails 2; the card's tooltip dropped fails 1; "in seed order" back in a leaf fails 2 (the scan's tree walk among
  them).
- **7.** `copy.test.ts` "claims no completeness" (no `every`, no `all`, not-every kept), the pair note's "always show
  together" held, the no-score loop now walks `PICKER_COPY` too with `\brank` (it missed "ranked"), and "say what the
  browser shows" holds each new line; `ReplayPicker.test.tsx:509` follows; a `ReplayFilters` render case holds
  "Reveal outcomes", its `aria-describedby` warning and no set chip. Planted in the suite: a picker leaf "ranked by
  drama" is named. Perturbed: "Show outcome filters" back fails 2.
- **8.** Unit cases in `copy.test.ts` for "killed by p-4" / "p-7", the all-roles HUD and a one-player HUD with no digit
  and no room name, matched without regard to case (planted: "REACTOR · ALARM" and the all-roles line fail);
  `MapLabels.test.tsx` holds the Pixi text props; render cases for the banner (`App.test.tsx`), the inspector button
  and pressed state and the private-mind note (`MindInspector.test.tsx`, `PrivateReasoning.test.tsx:303`), the
  evidence prompt (`EvidencePanel.test.tsx`, both views), the ballot prompt (`PrivateReasoning.test.tsx`),
  `MemoryPanel` with `revealSecrets` false (`SearchIntention.test.tsx`), the toolbar (`MapToolbar.test.tsx`), the
  ticker chip (`EventTickerChip.test.tsx`), the roster in both layouts and the pause bar (`App.test.tsx`).
  `journey.spec.ts:424,843,848,860,910-911,925` and `evidence-journey.ts:210,212,223-224` follow with their assertions
  kept (the toggle is now found inside the "Map perspective" group, since an inspector button may share its name;
  `:223`'s negative is the exact new prompt, asserted positively for the other voter at `:224`, so it cannot pass
  vacuously); `media.spec.ts:813-815` follows (covered by `npm run tsc:check` until the front-door card's capture run).
  Perturbed: the one-player early return dropped fails 2; "As-agent" back in `MapToolbar.tsx` fails 4; "fog" back in
  `MemoryPanel.tsx` fails 2.
- **9.** `journey.spec.ts:398-399` follow to "Crew win" / "Impostor win"; `App.test.tsx` holds the banner's tag
  (including a tick-limited game), the finale heading, the reason in the cards' words with an unmapped and an
  inherited-key reason verbatim, the recap's facts and the "changed by the vote rule" chip, and the whole finale
  card; `HighlightCard.test.tsx:69` and `:157-158` follow, `:68`, `:70` hold, a tag case per winner and stop holds
  every tag to `OUTCOME_COPY`, a crewmate case states "a crewmate was voted out", and the reveal-leak list follows to
  "was voted out". Planted in the suite: a hidden card leaking the new mark is caught by the followed list and missed
  by the old one. Perturbed: swapped mark branches fail 2; swapped aborted and tick-limit branches fail `:68-69`.
- **25.** `TournamentDashboard.test.tsx` "the dashboard's leftovers" renders the story fixtures' dashboard: no target
  beside the mean cost, "Expected calibration error 0.xyz" with its "lower is better" tooltip, the low-power note
  spelled out, no "ECE"; scan rows for `costMeanHint` and `\bECE\b`; `copy.test.ts` holds the keys. Perturbed: the
  hint restored as a literal fails 2.
- **Nothing else moves.** `git diff --stat B H`: 35 files, all in Expected scope (frontend sources, their tests, the
  four e2e files, `index.html`, this card). `git diff --exit-code B H -- engine agents meetings observation
  orchestrator llm api 'e?al/*' training experiments replays scripts tests README.md docs`: exit 0 (the glob
  `'e?al/*'` stands for `eval/`, whose name the sandbox refuses literally; the Results and round 1 quoted `'e?al'`, which
  matches no tracked file, see "Review corrections, round 2"). Perturbed: one appended line in `api/__init__.py`,
  or in `eval/__init__.py`, makes it exit 1. `check_doc_facts.py`: exit 0.
- **The live strings and the bundle diff.** In the pull request body, old against new, with the captures that still
  show the old words. Bundle built at B and at H in this one checkout (`build_demo_bundle.py --out`, detached at B,
  then the branch): 110 files each; `diff -r` differs only in `index.html` (the new title and two meta tags, and the
  entry chunk's hash) and seven renamed compiled chunks (`index`, `ReplayPicker`, `TournamentDashboard`, `MapView` and
  the three Pixi renderer chunks that import the entry); all 72 `data/` files are identical.
- **Mutation pass and gate.** Below. The gate record is CI's green run at the exact head, cited by run id in the pull
  request body; memo 8.7 item 1 bars a card-only commit to record it here, and no local `check.sh` ran at H.

### Mutation pass

One pass, 38 mutants, exactly the listed classes, each one exact replacement run against the whole unit suite and
restored with `git checkout` (a scratch script). It ran once at `4d7149e0`: 38 killed, 0 survivors. Designing it found
call sites a single test value could not see (a seed, a killer, a player, a set or a count typed as a constant); each
got a second value in `4d7149e0` before the run. The banner's stop did not: its one no-winner case was
tick-limited, so the stop typed as `"tick_limited"` passed; review round 1 found it, with the browser's two error
lines and the calibration figure (see "Review corrections, round 1").

- Dropped filter or wrapper (7): M01 the set map's raw-id fallback; M07 the impostor-win branch; M11 `Object.hasOwn`;
  M21 the recap chip's `adjusted &&`; M22 the one-player HUD return; M33 the scan's filter; M34 the scan's comment
  strip. Killed (2, 4, 2, 3, 2, 63, 10). M22 is also the item-8 plant.
- Swapped collection (3): M12 endings read from the tripwires; M32 `defaultAgentId ?? fogAgentId`; M38 the copy walk
  over one row's literals. Killed (11, 1, 1).
- None test or its inverse (3): M13 the finale's unmapped-reason test; M15 the card's ending test; M20 the recap's
  `!== null`. Killed (2, 9, 2).
- Kind or key read made a constant (9): M06 the aborted read; M08 the banner's stop; M09 the card's stop; M10 the
  finale winner; M14 the finale reason; M17 `ejection.right`; M24 the HUD's kind; M27 the overlay's `omniscient`; M28
  the overlay's kind. Killed (5, 1, 4, 2, 2, 1, 2, 1, 2).
- Message argument made a constant (4): M03 the set id; M18 the mark's meeting; M26 the HUD's ticks; M29 the killer.
  Killed (2, 2, 2, 2).
- Dropped tuple member (1): M37 `og:title` from the head's allowed elements. Killed (2).
- Swapped adjacent branches (8): M02 the set label; M05 the two win tags; M16 the two marks; M19 the recap's facts;
  M23 the one-player HUD; M25 the reactor's one and many; M31 the toggle's fallback; M35 the scan's string and regex
  match. Killed (3, 6, 2, 2, 2, 2, 3, 65).
- Loaded source read as its literal (3): M04 the loading cue's set; M30 the body's killer; M36 the index case's file
  read. Killed (1, 1, 1).

### Validation

Run from the branch's worktree with `.venv/bin/python` for `uv run python`, count-only; exit codes as they came back.

- `validate_task_docs.py`: exit 0. `check_doc_facts.py`: exit 0.
- `pytest tests/api/test_game_profile_view.py tests/api/test_sets.py tests/scripts/test_build_demo_bundle.py -q`: 118
  passed.
- `npm test`: 1046 passed (33 files); `npm run tsc:check`: exit 0; `npm run lint`: exit 0; `npm run e2e`: 15 passed, 3
  skipped (the capture spec, inert without its switch), 2.4 min. The pinned Chromium build 1194 is not installed on
  this machine and nothing was downloaded, so e2e ran the committed specs and servers through a scratch config that
  points `launchOptions.executablePath` at the cached headless shell 1234, with `CI=1` so no running server is reused.
  CI's e2e job runs the committed config.
- The card's `git grep`: 94 lines in 29 files at H (89 in 31 at B). Outside tests every hit is a comment line
  (`App.tsx:333`, `MeetingView.tsx:352`, `MemoryPanel.tsx:148`) or `BeliefPanel.tsx:552`, the meeting card's; in tests
  they are comments, test titles, planted cases and negative assertions, plus the clip (`media.spec.ts:1023`,
  `:1129`) the front-door card deletes.
- The `FEATURED_GAMES` diff, the never-written diff and the bundle diff: as above.
- Also run: `build_sample_report.py --check` on `samples/4p1i`, `samples/9p2i`, `ml_corpus/4p1i` and `ml_corpus/9p2i`,
  exit 0 each; `bash scripts/verify_samples.sh`, exit 0, 4 sets of 50 verified clean.

### Limitations

- The committed captures still show old words until the front-door card's capture run at its head: the two-truths
  still "FOG" room labels and "† p-6" / "† p-9" under bodies; the meeting still the banner's "seed 19 · 9p" and "Next
  beat →"; the GIF frames the old tabs, banner, "3 mtg", "imp 2", the `canonical_1` chip with its counts and
  "As-agent".
- `docs/glossary.md:327,351` still say shelves list games "by seed number"; true (a game's number is its seed), and
  `docs/` is not this card's.
- `BeliefPanel.tsx`'s four view-name lines keep "fog" and "As-agent" until the meeting card; the dashboard's "Tick
  limit reached" tile and `momentsError` are the local dashboard's other words, outside item 25.
- The Pixi labels are held by reading the components' element trees, not pixels; the wider HUD chip was not
  screenshot-checked at every map width.

### Review corrections, round 1 (2026-10-11)

The first review of pull request #511 read `142db9aa`, whose CI run 38171003224 was green (Project checks, Frontend
checks, Frontend e2e). It filed three blocking findings, two from the correctness lens and one from the
documentation lens, and this round repairs them. `main` is still `7d781f8e`, so nothing was merged in. Commits:
`3c6657c5` (the three test repairs) and this commit (the three acceptance items above, this subsection and the
in-place pointers in the opening paragraph and the Mutation pass). Each ends with the `Card:` trailer immediately
followed by `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`, checked with `git log -1 --format=%B` before
the push. No production file moved, so the strings that go live and the bundle diff are as round 1 left them; the
four files this round writes (`App.test.tsx`, `ReplayPicker.test.tsx`, `TournamentDashboard.test.tsx`,
`copy.test.ts`) were already in the diff, which stays 35 files, all in Expected scope.

**1. The browser's two error lines (correctness).** No test rendered the connected `ReplayPicker`, so its set-list
line and its replay-load line could print a constant, or each other's words, and the suite still passed 1046. A
server render reads a zustand store's initial state, so the test mocks the store module with a reduced state, as
`App.test.tsx` does, and reads every error banner's text in page order: the set list's line is "The set list could
not be loaded: {error} Retry", the game's line "This game could not be loaded: {error}", each with two raw errors;
both appear together in that order; neither appears when nothing failed; and the set selector stays once the sets
have loaded, whatever a later fetch says. The mock touches only the connected component: every other case in the
file renders the presentational view or calls a pure function. `copy.test.ts` pins both strings beside the others.

**2. The calibration figure (correctness).** The readout case matched any three-place figure, so the figure typed as
0.123 passed. The dashboard case now holds the story's two readouts to its two figures in page order, which also
catches one curve fed the other's figure, and a direct `CalibrationCurve` case holds 0.248, 0.1 (as 0.100) and no
figure (as n/a).

**3. The banner's stop (documentation).** The Results said every name-helper call site got a second value in
`4d7149e0`; the banner's stop had one no-winner case, tick-limited, so M08's `"aborted"` constant was killed and a
`"tick_limited"` constant was not. The new banner case names all four stops; the Mutation pass now says so.

**Mutation probe.** One bounded pass over the spans the findings name, 31 mutants of the listed classes, each one
exact replacement run against the whole unit suite and restored from memory by a scratch script. Before is an
archive of `142db9aa`'s `frontend/` with the worktree's `node_modules`, `docs/` and `replays/` linked in (none of
them changed, and its unmutated run passes 1046); after is the worktree at `3c6657c5` (unmutated, 1053 passed).

- The set-list and replay-load lines (14): R01 and R02 the set-list error typed as two constants, R03 the game's
  error typed as a constant (message arguments); R04 and R05 each line reading the other's copy, R06 and R07 each
  line reading the other's error, R13 the game's line reading the list error (swapped collections); R08 and R09
  each line's null test inverted; R10 the "no sets loaded" filter dropped; R11 the banner and the selector swapped;
  R12 and R14 each error read made null. Before: all 14 survived. After, in id order, killed (1, 2, 1, 2, 2, 2, 2, 2,
  5, 1, 5, 2, 2, 2).
- The calibration readout (8): J01 and J02 the figure typed as 0.123 and 0.248, J03 the figure formatted from null,
  J06 three places made two (message arguments); J04 the null test inverted; J05 its branches swapped; J07 the
  ballot curve fed the claim figure (swapped collection); J08 the tooltip dropped (wrapper). Before: J01 to J05 and
  J07 survived, J06 and J08 killed (1 each). After, in id order, all killed (2, 2, 2, 2, 2, 2, 1, 2).
- The banner's tag (9): H01 to H04 the stop typed as `tick_limited`, `aborted`, `unfinished` and null, H05 the
  winner typed as null (kind reads made constants); H06 the aborted and tick-limit branches swapped, H09 the reveal
  branches swapped; H07 the aborted test made a null test; H08 the tick-limit branch dropped. Before: H01 survived,
  the rest killed (1, 1, 1, 1, 4, 2, 3, 2). After, in id order, all killed (1, 2, 2, 2, 1, 5, 3, 4, 3).

Before, 21 of 31 survived; after, 31 of 31 are killed. No production line changed this round, so the earlier pass's
38 mutants stand as they were.

**Validation, this round.** Run from the branch's worktree with `uv run`, count-only; exit codes as they came back.
`npx vitest run`: 1053 passed (33 files). `npm run tsc:check`: exit 0. `npm run lint`: exit 0.
`validate_task_docs.py`: exit 0. `check_doc_facts.py`: exit 0. `pytest tests/api/test_game_profile_view.py
tests/api/test_sets.py tests/scripts/test_build_demo_bundle.py -q`: 118 passed. The card's never-written diff from
`7d781f8e` to H over `engine agents meetings observation orchestrator llm api eval training experiments replays
scripts tests README.md docs` (the glob `'e?al'` standing for `eval`, as before): exit 0. That pathspec matches no
tracked file, so this run did not cover `eval/`; round 2 re-ran the guard with `'e?al/*'`. `npm run e2e` was not
rerun here: this round moves no production file and no e2e spec, other cards' sessions share this machine's ports
8000 and 5173, and CI's e2e job runs the committed config at the exact head. The gate record is CI's green run at
the exact head, cited by run id in the pull request body (memo 8.7 item 1); no local `check.sh` ran at H.

### Review corrections, round 2 (2026-10-11)

The second review read `fd951388`, whose CI run 38176662572 was green (Project checks, Frontend checks, Frontend
e2e). Its documentation lens filed three blocking findings, all about this card's Results, and this round repairs
them with one card-only commit: the three acceptance items above, this subsection and the in-place corrections in
the opening paragraph, Decisions 10, the Acceptance evidence's opening and its "Nothing else moves" item, and round
1's Validation. `main` is still `7d781f8e`, so nothing was merged in. No production, test or e2e file moved, so the
strings that go live, the bundle diff and both mutation passes stand as round 1 left them, and `git diff --stat B H`
stays 35 files, all in Expected scope. The commit ends with the `Card:` trailer immediately followed by
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`, checked with `git log -1 --format=%B` before the push.

**1. The never-written guard covered no `eval/` file.** A git pathspec with a wildcard is matched against each file's
whole path, so `'e?al'` matches no file under `eval/`: `git ls-files 'e?al' | wc -l` gives 0 and
`git ls-files 'e?al/*' | wc -l` gives 37. The fact the guard was meant to show still holds: `git diff --exit-code
7d781f8e fd951388 -- engine agents meetings observation orchestrator llm api 'e?al/*' training experiments replays
scripts tests README.md docs` exits 0. `git ls-files` over the same 15 pathspecs, grouped by first path segment,
lists 15 names, each with at least one tracked file (`eval` 37, `api` 10, `README.md` 1), so no other pathspec is
vacuous. Planted: one line (`# plant`) appended to `eval/__init__.py`, with the working tree standing for H
(`git diff --exit-code 7d781f8e -- <the same pathspecs>`), makes the corrected guard exit 1 and leaves the `'e?al'`
form at exit 0; the line appended to `api/__init__.py` instead makes it exit 1; both restored with `git checkout`,
after which the guard over the working tree exits 0 again.

**2. Eight exports, not three.** `git diff 7d781f8e fd951388 -- frontend/src/App.tsx | grep '^+export'` lists
`TopNav`, `PerspectiveBanner`, `RosterRail`, `MeetingPauseBar`, `FinaleHeadline`, `FinaleReason`, `RecapRow` and
`FinaleCard`; `grep -c '^export'` on `App.tsx` gives 2 at B (`ShellTitle` and the default `App`) and 10 at H.
Decisions 10 now names the eight, as the pull request body did.

**3. The red-at-base count.** Reproduced in scratch directories outside the repository: `git archive 7d781f8e
frontend` extracted, the unit-test files a commit changed (`git diff --name-only 7d781f8e <commit> --
'frontend/src/*.test.ts' 'frontend/src/*.test.tsx'`) extracted over it from `git archive <commit>`, and `docs/`,
`replays/` and `frontend/node_modules` linked from the worktree (`docs/` and `replays/` do not change from B to H);
then `npx vitest run --reporter=json` in its `frontend/`, the report counted per file.

- `635f47ae`'s 11 unit-test files over B: 32 files, 11 failed. `App.test.tsx` fails to load, and 125 tests fail in
  the other 10 (`copy.test.ts` 84, `HighlightCard.test.tsx` 10, `ReplayPicker.test.tsx` 9,
  `PrivateReasoning.test.tsx` 7, `MapLabels.test.tsx` 4, `MapToolbar.test.tsx` 3, `MindInspector.test.tsx` 3,
  `EvidencePanel.test.tsx` 2, `TournamentDashboard.test.tsx` 2, `SearchIntention.test.tsx` 1); 826 pass. In the
  scan, all 62 "no longer carries" rows fail by name, as do the leaf walk and its planted leaf, while the
  comment-strip plant passes.
- H's 12 unit-test files (with `EventTickerChip.test.tsx`) over B: 33 files, 12 failed. `App.test.tsx` fails to load,
  and 133 tests fail in the other 11; 828 pass.
- Control, B's own tests in the same layout: 855 passed, 28 files, so the layout causes none of the failures.

The figure the Results first gave, 9 files and 118 tests, came from a draft of the tests before `635f47ae` was
committed and cannot be reproduced. The Acceptance evidence now gives `635f47ae`'s figure and points here.

**Mutation probe.** This round changes no production or test line. Of the spans the findings name, only the guard is
a check a mutant can test; the count and the export sentence are statements, settled by the commands above. One
mutant of a listed class, G01, drops the `/*` wrapper from `'e?al/*'` (the form quoted before this round): with the `eval/__init__.py`
plant in place it exits 0, so it survives, and the corrected guard exits 1. The probe is the planted proof in item 1.

**Validation, this round.** Run from the branch's worktree with `uv run`, count-only; exit codes as they came back.
`validate_task_docs.py`: exit 0. `check_doc_facts.py`: exit 0. `pytest tests/api/test_game_profile_view.py
tests/api/test_sets.py tests/scripts/test_build_demo_bundle.py -q`: 118 passed. `npx vitest run`: 1053 passed (33
files). `npm run tsc:check`: exit 0. `npm run lint`: exit 0. The card's `git grep`: 94 lines in 29 files, as before.
The `FEATURED_GAMES` diff: exit 0, 32 lines each. The never-written guard with `'e?al/*'`: exit 0 from `7d781f8e` to
`fd951388`, and this commit writes only this card. `npm run e2e` was not rerun: no e2e spec or production file moved,
and CI's e2e job runs the committed config at the exact head. The gate record is CI's green run at the exact head,
cited by run id in the pull request body (memo 8.7 item 1); no local `check.sh` ran at H.
