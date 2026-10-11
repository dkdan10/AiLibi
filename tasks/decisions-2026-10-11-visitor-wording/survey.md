# Visitor wording: decisions for Daniel

2026-10-10 · read at `origin/main` fa213381

Visitor-facing wording an agent or the orchestrator chose by default; your header ruling is not repeated. **Bold** is my pick. Rewording moves strings into `copy.ts`. Appendices: every grouped string (A), the drops (B).

**Held already, not re-asked:** dashboard "gate" words and the "vote gate" badge (D8-L; its option (c) also covers process rows on the Results tab); Error-layer words and the ballot "correct / incorrect" badge (D8.1); dashboard skip tiles (D9-L).

<!-- main body starts -->

## Demo: first visit

**1. Project name.** Tab "AiLibi — Replay Viewer", no share text (`frontend/index.html:6`); README "AiLibi — can agents reason from what they actually saw?" (`README.md:1`). By: workers (Task 4.3; portfolio-evidence-experience). Why: neither carries your kept tagline. (a) keep; **(b) tab and share text "AiLibi — Recorded AI social deduction"; tagline under the README question** — one name; (c) tagline as both titles.

**2. Landing.** With no link, the tour opens over a loaded game (`GuidedTour.tsx:49-85, :257-286`). By: workers (Tasks 12.11, 19.9). Why: every first visit. **(a) keep** — quickest way in; (b) open on Replays with a "Take the tour" button; (c) the tour without a game.

**3. Roles from the first frame.** All-roles view, impostors badged, outcomes hidden (`store/replayStore.ts:299, :305`); meeting line "post-hoc: p-4 was impostor" (`MeetingView.tsx:353-357`). By: Phase-12 design (`stage-1-design.md:48`); the brief said one player's view (`frontend/CLAUDE.md:28`). Why: the sources disagree. **(a) keep; the line becomes "p-4 was an impostor"** — the usual spectator view; (b) one player's view; (c) roles hidden until the reveal.

## Demo: replay browser

**4. Tab names.** "Highlights" opens "Browse by moment"; "Results & cases" opens "What the recordings show"; README: "Inspect results and decisions" (`App.tsx:203-204`; `README.md:5`). By: Phase-12 design, workers. Why: the names visitors click. (a) keep; **(b) "Moments", "Results", README "See the results"** — names match pages; (c) page headings as names.

**5. Featured strip.** "Featured — picked by hand" (`ReplayPicker.tsx:312`), though three of five follow a measured rule; count-plus-question blurbs (`:119-150`). By: workers (Task 19.9; spectator-tour-round-2). Why: the only editorial lines before a game. (a) keep; **(b) "Featured", blurbs kept** — wrong for three; (c) "Start here", one setup sentence each.

**6. Game and set names.** "seed 19"; "9p2i — 9 players, 2 impostors" beside a repeat "9p2i" chip. By: workers (Phase 12; Task 20.2). Why: recorder codes are the only names. (a) keep; **(b) "Game 19", seed on hover; sets in words; chip dropped**; (c) words only.

**7. Browser wording.** "Show outcome filters" reveals every outcome (`ReplayFilters.tsx:141-144`); "The replays this build serves…"; "the configured replay directory". By: Phase-19 contract (hidden default); workers' words. Why: developer wording. (a) keep; **(b) "Reveal outcomes", Appendix A's lines**; (c) outcomes shown by default.

## Demo: workspace

**8. Workspace labels.** "3 mtg", "imp 2"; one view, five names ("As-agent", "fog of war · as", "Show what they saw", "perspective", …); "Next beat →"; "† p-4" under a body. By: workers (Phase 12; Task 19.10). Why: undefined words; "† p-4" reads "p-4 is dead". (a) keep; **(b) Appendix A's pass ("3 meetings", "perspective" throughout, "killed by p-4")**; (c) tooltips.

**9. Endings and marks.** One ending, three wordings plus a raw "IMPOSTORS"; recap "✓ named an impostor / ✗ missed"; cards "the vote was right / wrong" (`App.tsx:307-946`; `copy.ts:679-693`). By: workers (Task 19.10; rubric-v2-profile); you adopted the note, not its words. Why: outside the held badge. (a) keep; **(b) one ending wording; facts as marks ("an impostor was voted out")**; (c) endings now, marks with the badge.

## Demo: meetings and panels

**10. Meeting and ballot wording.** "plurality leader p-4, top ballot {conf} ≥ {thr} threshold → EJECTED" (`MeetingView.tsx:195-217`); "guilt is never coloured in"; "opt-in"; "Cited statement · {meeting id}:turn-3". By: workers (Tasks 12.7, 19.11). Why: the copy rules bar threshold arithmetic and undefined terms. (a) keep; **(b) Appendix A's pass ("Most votes went to p-4, and a voter was sure enough")**; (c) move unchanged.

**11. Inspector and belief panel.** "Thought → Action → Observation" (`MindInspector.tsx:251`); "9×9 suspicion matrix", "Ground-truth", "A badge, never a hue" (`BeliefPanel.tsx:33-552`). By: workers (Tasks 12.6, 12.8). Why: design rules, not meanings. (a) keep; **(b) "Said / Claimed / Voted / Result", "Who suspects whom", "Real roles", a legend of meanings**; (c) swatches only.

**12. Confidence numbers.** "0.73" on ballots, "73" in belief cells, under "Bucketed Low / Med / High" (`BallotCard.tsx:228-238`; `BeliefCell.tsx:105-113`). By: workers (Tasks 12.6-12.8), against the brief. Why: a model's own number reads as measured. (a) keep; **(b) Low / Med / High, number on hover**; (c) colour only.

## Demo: Results tab

**13. Proof box.** "Separate direct proof from uncertain inference", "24/24 (100%)"; 4-player "The 1 ejections" (`PublicResults.tsx:100-109`). By: worker (portfolio-evidence-experience); the baselines memo: "published last, never a headline". Why: role-correct percentages in the boldest box. (a) keep; **(b) a plain row after the cases, headed by what it counts** — your README order; (c) fractions only.

**14. Case cards.** Two editorial cases from one game; "Inspect the meeting" shows roles beside "Reveal case analysis (spoilers)"; "Pinned recording source" opens raw JSON lines (`api/public_results.py:66-84`; `PublicResults.tsx:61-68`). By: card framing, worker words. Why: the page's only story. (a) keep; **(b) links "Inspect the meeting (shows roles)", "Raw recording file"** — keeps the spoiler; (c) your titles, a second game.

**15. Results wording.** "The engine reconstructed each recording…"; "No source-matched editorial cases…"; "impostor ballots cast by strategy"; "Impostor policy: not recorded", meaning the default. By: workers; you adopted the rules, not their words. Why: "not recorded" reads as missing. (a) keep; **(b) Appendix A's pass, naming the default**; (c) a manifest link for the ids.

## GitHub: README and linked pages

**16. Byline and "Who did what".** "implemented by Claude Code and Codex agents · AI-reviewed" (`README.md:3`); "Codex… now also implements cleanup" (`:56`). By: worker (portfolio-evidence-experience); unconfirmed. Why: your ruling sends visitors here; "now" is stale. (a) keep; **(b) keep the byline, linked to an updated "Who did what"**; (c) "by Daniel Keinan · MIT · CI".

**17. Hero picture.** Still embedded; motion only a WebM link; GIF archive-only (`README.md:11`). By: workers (portfolio-evidence-experience; promote-round-3). Why: GitHub plays GIFs inline, not WebM. **(a) keep** — motion needs a fresh capture; (b) GIF under the still; (c) GIF instead.

**18. README jargon.** Caption in ids; "its own era… baseline 9… ML corpus"; "394/397 = 0.9924" beside "56/291 = 19.2%"; "vote correctness 0.783"; a scorecard opening on decision ids. By: workers; doc checks pin tokens. Why: ids before a stranger's first number. (a) keep; **(b) plain words, one number style, ids in manifests, checks updated**; (c) gloss ids once.

**19. "Before" column.** "Each before cell is what that set's previously shown recording read." (`README.md:17`). By: orchestrator default (D12); the 2026-10-10 audit asks you to confirm. Why: it sets every comparison. **(a) keep** — what changed since last time; (b) against baseline 9; (c) drop it.

**20. Missed-bar paragraphs.** "61 of 103 = 0.5922 against 0.60 … FINDING" (`README.md:35, :37`). By: left open for you (D8's second half). Why: threshold arithmetic, verdict words. (a) keep; (b) move to `docs/history.md`; **(c) one plain sentence and a link** — honesty stays, arithmetic moves.

**21. Your voice.** "I directed AiLibi's initial build…", "confirm wording" marker open (`docs/lessons.md:1-4`); glossary "Me — Daniel Keinan" (`docs/glossary.md:21`). By: workers (Tasks 20.40, 20.12). Why: only you can vouch for it. **(a) confirm, if true**; (b) edit yourself; (c) third person.

**22. Ownership case.** "A decision that did not pass its own rule" (`docs/ownership-case-study.md:1`). By: card contract. Why: which of your decisions is shown. (a) keep; (b) a recent ruling instead; **(c) keep, add a recent one** — today's practice.

**23. Reading guide.** "Deception: demonstrated, and the strongest capability on display." (`docs/reading-guide.md:93`), not re-measured; August audit list (`:120`). By: workers (Tasks 19.16, 20.12). Why: the strongest claim, held by no check. (a) keep; **(b) "demonstrated in earlier recordings", sourced; lead with the 2026-10-10 audit; plainer row labels**; (c) cut "strongest" only.

## GitHub: repository page

**24. Policy pages and topics.** "There is no hosted instance…" (`SECURITY.md:5-6`); "CI and a human review as the gates" (`CONTRIBUTING.md:9-11`); topics incl. claude-code, among-us (`docs/deployment.md:194`). By: workers (Tasks 19.7, 20.7). Why: both sentences are now untrue. (a) keep; **(b) fix both, keep topics** — accurate, findable; (c) also drop product-name topics.

## Local checkout

**25. Dashboard leftovers.** "target ≈ $0.20/game" (`copy.ts:358`); "ECE 0.123" (`CalibrationCurve.tsx:50-52`). By: Tasks 5.7, 12.10. Why: stale target, undefined acronym. (a) keep; **(b) drop the target; spell out the acronym**; (c) drop the figure too.

<!-- main body ends -->

## Decisions to answer by number

Answer with the number and a letter; my pick is in brackets.

1. Project name: tab title and share text become "AiLibi — Recorded AI social deduction", README keeps its question with the tagline beneath? [b]
2. First visit: keep the tour opening over a loaded game? [a]
3. Roles from the first frame: keep the all-roles view as the start, with the meeting's role line in plain words? [a]
4. Tab names: "Moments" and "Results", and the README link to match? [b]
5. Featured strip: heading just "Featured", blurbs unchanged? [b]
6. Game and set names: "Game 19" and set names spelled out in words? [b]
7. Replay browser: rename the reveal button "Reveal outcomes" and plain-word the notes and empty states? [b]
8. Workspace labels: spell out the short forms, one name for one player's view, "killed by" on the map? [b]
9. Endings and marks: one set of ending words, and plain facts in place of right/wrong marks? [b]
10. Meeting and ballot cards: plain sentences in place of the threshold readout and the design notes? [b]
11. Inspector and belief panel: plain names, and a legend that says what each mark means? [b]
12. Confidence numbers: show Low / Med / High, with the number on hover? [b]
13. Results proof box: a plain row after the cases instead of a headline box? [b]
14. Case cards: label the links "shows roles" and "raw recording file"? [b]
15. Results wording: plain words, naming the default instead of "not recorded"? [b]
16. README byline: keep it, link it to an updated "Who did what"? [b]
17. README picture: keep the still image? [a]
18. README terms: plain words, one number style, exact identifiers moved to the manifests? [b]
19. README comparison column: keep comparing against the previously shown recording? [a]
20. Missed-target paragraphs: one plain sentence on the README, the figures moved to the history page? [c]
21. Lessons page and glossary entry written in your voice: confirm, edit, or switch to third person? [a, if they read true]
22. Ownership case study: keep it and add a recent decision? [c]
23. Reading guide: soften the deception claim and lead with the latest audit? [b]
24. Security and contributing pages: fix the two outdated sentences, keep the topics? [b]
25. Local dashboard: drop the old cost target and spell out the calibration acronym? [b]

Still waiting, asked elsewhere: the local dashboard's "gate" words and the "vote gate" badge; the belief panel's Error-layer words and the ballot "correct / incorrect" badge; how the local dashboard reads skips.

## Appendix A. Strings behind the grouped items

| Item | Current text | Location | Chosen by | Plain-words suggestion |
|---|---|---|---|---|
| 6 | "seed 19"; banner "seed 19 · 9p · outcome hidden" | `HighlightCard.tsx:304`; `ReplayPicker.tsx:324`; `App.tsx:307-308` | Tasks 12.9, 19.9, 19.10 | "Game 19", seed in a tooltip |
| 6 | "9p2i — 9 players, 2 impostors"; chip "9p2i"; "Loading 9p2i…"; Results intro "…in 9p2i" | `copy.ts:104-125`; `ReplayFilters.tsx:185-189`; `ReplayPicker.tsx:566`; `PublicResults.tsx:80` | Tasks 20.2, 12.9, 12.13; portfolio-evidence-experience | "9 players, 2 impostors (9p2i)"; drop the chip |
| 7 | "Show outcome filters" with "⚠ reveals winners and endings across the whole set" | `ReplayFilters.tsx:141-144` | default: `tasks/phase-19.md:758-779`; words: Task 19.10 | "Reveal outcomes" |
| 7 | "The replays this build serves for the selected set. Click a card to open it." | `copy.ts:457-464` | Task 20.2 | "Recorded games for this set. Open one to watch it." |
| 7 | "…each list in seed order. Nothing here ranks or scores a game." | `copy.ts:457-464` | rubric-v2-profile | drop the second sentence |
| 7 | "…including any a tripwire keeps off the shelves."; "The two halves always show together." | `copy.ts:546-547, :649` | rubric-v2-profile (showing the label before the reveal is your ruling, `:657`) | "including games kept off the shelves" |
| 7 | "No replays found" / "No replays in the configured replay directory."; "Failed to load replays:" plus raw error or "unknown error" | `ReplayPicker.tsx:574-578, :607-609, :926, :945` | Tasks 12.9, 12.13 | "No recorded games are available for this set." |
| 8 | "9p", "3 mtg", "crew 7 · imp 2" | `App.tsx:307-308, :319, :330, :456, :465-471` | Tasks 12.4, 12.13, 19.10 | "9 players", "3 meetings", "crew 7 · impostors 2" |
| 8 | "As p-3 · fog", "Exit fog", "As-agent", "fog of war · as", "Show what they saw", "Switch to p-1's perspective", "View p-1's perspective to inspect it." | `App.tsx:364-366`; `MapToolbar.tsx:162, :171`; `MindInspector.tsx:717-723`; `BallotCard.tsx:325`; `EvidencePanel.tsx:76` | Tasks 12.5, 12.13; portfolio-evidence-experience | "perspective" everywhere: "Watching as p-3", "See as p-1" |
| 8 | "Next beat →"; Resume tooltip "…the pause is edge-triggered, so this advances past the meeting" | `App.tsx:676-687` | Task 19.10 | "Next key moment →"; "Resume playback past this meeting" |
| 8 | Tour "Perspective switcher + the fog firewall", "Open the Belief × Truth hero", "impostor = icon, not a hue"; Tour button "…the two-truth grammar" | `GuidedTour.tsx:118-132, :179, :194-198`; `App.tsx:242` | Tasks 12.11, 12.13 | "What one player could see"; "Open the Belief × Truth panel"; step 3 after the held Error-layer ruling |
| 8 | Map chip "canonical_1 · 10 rooms · 11 corridors · 6-vent ring"; "† = impostor"; "† p-4" under a body | `MapToolbar.tsx:108-129`; `BodyMarker.tsx:164-170` | Tasks 12.5, 12.13 | "Map"; "killed by p-4" |
| 8 | "FOG"; "REACTOR · t-5" in the all-roles view, "SABOTAGE · ALARM" in one player's | `RoomRect.tsx:130`; `SabotageOverlay.tsx:100-104` | Task 12.5 | "Reactor meltdown in 5 ticks"; one wording in both views |
| 9 | Banner raw "CREWMATES" / "IMPOSTORS"; finale "impostors reached parity", "sabotage unresolved"; cards "Ended: the impostors matched the crew in number", "a sabotage ran out"; tag "Tick limit" | `App.tsx:307, :703-708, :862`; `copy.ts:679-686`; `HighlightCard.tsx:79-84` | Tasks 19.10, 12.9; the 2026-09-05 cleanup; rubric-v2-profile | the cards' wording everywhere; "Crew win" / "Impostor win" tags |
| 9 | Recap "What they knew vs the truth", "✓ named an impostor" / "✗ missed", "engine-adjusted" | `App.tsx:773-785, :946` | Task 19.10 | facts without ✓/✗, e.g. "named an impostor" / "named no impostor" |
| 9 | "Meeting 2: the vote was right" / "…wrong" | `copy.ts:692-693` | rubric-v2-profile (the note itself is in the profile you adopted) | "Meeting 2: an impostor was voted out" / "a crewmate was voted out" |
| 10 | "plurality leader {id}, top ballot {conf} ≥ {thr} threshold → EJECTED" | `MeetingView.tsx:195-217` | Task 12.7; kept by `tasks/phase-20.md:544-546`; outside the held badge | "Most votes went to p-4 and a voter was sure enough, so p-4 was ejected" |
| 10 | "outcome is role-neutral · guilt is never coloured in" | `MeetingView.tsx:346` | Task 12.7 | delete |
| 10 | "Accusation edges use distrust orange — direction = who points at whom."; "redirects" on every reply | `MeetingView.tsx:127, :164-166` | Task 12.7 | "Arrows point from accuser to accused"; "accuses" |
| 10 | "Weak signals — the detector stamped these weak (… endpoint tick)"; "Role proof — grounded against the witness's own record…" | `MeetingView.tsx:452-485` | Task 19.11 | plain captions; a glossary entry for any term kept |
| 10 | "t12 · opt-in"; "Source 1 · p-3 (opening)" | `MeetingView.tsx:396-400, :613`; `TurnCard.tsx:47-51` | Tasks 8.10, 12.7; portfolio-evidence-experience | "spoke up", "first statement", "reply" |
| 10 | Panel heading "What the recording shows", near twin of the Results heading | `copy.ts:380-396` | spectator-tour-round-2 | "Where everyone really was" |
| 10 | Eleven vote-adjustment chips, e.g. "Vote redirected by the meeting rule" | `BallotCard.tsx:22-36` | portfolio-evidence-experience | "changed by the vote rule", with a glossary entry |
| 10 | "Cited statement · {meeting id}:turn-3"; "Cited observation · p-1:12:0" | `BallotCard.tsx:262-264`; `EvidencePanel.tsx:63` | portfolio-evidence-experience | "Statement by p-3 (turn 3)"; "What p-1 saw at tick 12" |
| 10 | Finding chip beside "Weighed on this ballot", its label "Basis on the record" only on hover | `BallotCard.tsx:279-294`; `copy.ts:420-452` | grounded-skip-and-guard-labels | a visible "Basis on the record:" prefix |
| 10 | "A resolved citation identifies a source. It does not establish…", also shown when nothing resolved | `EvidencePanel.tsx:64` | portfolio-evidence-experience (review finding retained) | only when resolved: "A citation shows where a claim came from, not that it is right." |
| 11 | "Thought → Action → Observation"; "Meeting ejected — p-4 ejected" | `MindInspector.tsx:57-61, :132, :251` | Phase-12 contract; Task 12.8 | "Said / Claimed / Voted / Result"; "Meeting: p-4 was ejected" |
| 11 | "9×9 suspicion matrix"; "rows = believer · columns = subject"; "Belief · Ground-truth"; "fog · ground-truth hidden" | `BeliefPanel.tsx:33-37, :247-253` | Task 12.6 | "Who suspects whom"; "Real roles" |
| 11 | "A badge, never a hue — and hidden in fog."; "an agent holds no suspicion file on itself"; "0–100 (mono)" | `BeliefPanel.tsx:488-522, :552` | Task 12.6 | "Dagger: a real impostor, all-roles view only" |
| 12 | Inspector "conf 0.73" | `MindInspector.tsx:66, :124, :221` | Task 12.8 | Low / Med / High |
| 13 | Caption "…this group is 100% by construction…", "ejectee" | `PublicResults.tsx:108` | portfolio-evidence-experience (post-review sentence) | "Ejected players who were impostors, with and without a vent sighting" |
| 14 | Titles "A sighting the table can check", "When accounts do not settle the question", both from seed 19 | `api/public_results.py:66-69, :81-84` | framing by the card; words by the worker, re-derived by promote-round-3 | keep, or your own titles |
| 15 | "…The engine reconstructed each recording…" | `PublicResults.tsx:79-81` | portfolio-evidence-experience | "each recording was replayed and checked before counting" |
| 15 | "No source-matched editorial cases are published for this set." | `PublicResults.tsx:113` | portfolio-evidence-experience | "No worked examples for this set yet; the 9-player set has two." |
| 15 | "Rules adopted for the current game: … impostor ballots cast by strategy." | `copy.ts:501, :509-518` | post-promotion-follow-through (adoption yours, words not) | one plain sentence per rule |
| 15 | "Impostor policy: not recorded. Crew policy: not recorded. Rule settings: recorded."; "Observation clock: not recorded." | `copy.ts:492, :535, :538` | experimental-evaluation-integrity; recorded-provenance-gaps; post-promotion-follow-through | name the default ("the built-in scripted policy"), per `orchestrator/replay.py:698` |
| 15 | "Prompt versions: accusation_round.qwen3_6_27b.v6, …"; "a flat-rate adapter can report $0"; "Source fingerprint: sha256:…" | `PublicResults.tsx:114-122` | portfolio-evidence-experience | under "Technical identifiers, for reproduction"; "$0: a flat-rate service, so usage, not a bill" |
| 16 | "Claude Code implemented the initial project; Codex reviewed it and now also implements cleanup… Daniel did not hand-write the production code." | `README.md:56` | portfolio-evidence-experience, replacing a draft marked for your confirmation | later work by Claude workers; some merges by the orchestrator under your written delegation |
| 18 | Hero caption in set and player ids | `README.md:13` | promote-round-3 (a test checks each clause) | a plain caption first, ids after |
| 18 | "in its own era; the 4-player set and the ML corpus stay at baseline 9 … No figure pools the two." | `README.md:17` | promote-round-2 (doc-facts check) | dated plain names |
| 18 | "394/397 = 0.9924", "56/291 = 19.2%", "24 / 46 = 52%"; no row says which way is better | `README.md:23-30` | front-door-process-first | "394 of 397 (99%)" and a direction word per row |
| 18 | "Known evidence leak": "body identifier", "temporal repair", "default-off" | `README.md:49-52` | promote-round-2 | the same disclosure in plain words |
| 18 | "vote correctness 0.783, and ejection accuracy 0.754" | `README.md:110` | Task 20.12 (a check holds it) | say what they count ("ballots naming an impostor") |
| 18 | "`qwen3_6_27b` `v6` prompts with a `v8` ballot … `route_lines_v1`" | `README.md:112` | promote-rounds 2 and 3 (doc-facts check) | plain words; stamps in the set's MANIFEST |
| 18 | Scorecard opens "The owner accepted decision D1 of tasks/direction-…"; rows "argmax-independence: deviating EJECTs"; column "as published at `2eed2e92`" | `docs/process-scorecard.md:3, :108-121` (generated) | process-scorecard; row names from the direction memo you accepted | a generated preface mapping each README label to its row |
| 23 | Row "Pre-registered emergence rulings demonstrated, phase 18" | `docs/reading-guide.md:29` | Task 20.38 | "Learned behaviours the ML program set out to show" |

## Appendix B. Dropped by the refuters

The first column numbers the reviewers' working list; "item N" means this memo's numbering.

| Reviewers' # | What | Why dropped |
|---|---|---|
| 20, 21, 22, 63, 64, 65, 66 | Repeat listings of the three held questions | Held items are listed once (the box at the top) |
| 44, 50 | Results tab opens on win and role tiles, with no process rows | Already held: option (c) of the dashboard-vocabulary question puts process rows on that tab (`tasks/work/front-door-process-first.md:207, :708`); one refuter would have posed it separately, so the box names it |
| 49 (its quote) | Provenance lines quoted as "rule-based impostor" and "v2" | Those words come from a unit-test fixture; both shown sets read "not recorded". Merged with 52 and 58 into item 15 with the real lines |
| 51 | Proof panel | Repeat of 46; its "The 1 ejections" detail is in item 13 |
| 53 | Tab name "Results & cases" | Repeat of 3, now item 4 |
| 54 | Results heading and intro with the raw set id | Repeat of 45, now items 6 and 15 |
| 55 | Case cards | Repeat of 47 and 48; the raw-file link is in item 14 |
| 59 | Results-tab strings typed inline instead of in `copy.ts` | Code organisation a visitor never sees; any rewording above moves its strings |
| 86 | Repository description proposed in `docs/deployment.md` | Operator checklist; the live description was set by hand in other words |
| 88 | `docs/deployment.md` never names the demo address | Operator checklist; the README and the repository homepage already name it |
| 91 | Browser tab title | Repeat of 2, now item 1 |
| 18 (part) | Highlights empty state for the 4-player set | Successor of the no-rubric empty state you already ruled |
| 3 (part) | Screen-reader label "Tournament dashboard" | It belongs to the local dashboard only; the live tab reads "Recorded results and cases" |
