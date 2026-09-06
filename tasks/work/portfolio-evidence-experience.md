# Follow a decision from claim to evidence

**Status:** active

## Outcome

A first-time visitor understands who directed AiLibi, what its recorded games
demonstrate, and how to inspect a decision. The standalone demo connects concise
results and three contrasting cases to the exact statement, observation, scene,
and agent knowledge behind a ballot. The README introduces this experience and
links a substantive ownership decision case study.

## Evidence

Roadmap items 26–31 form one reviewer journey. `BallotCard.tsx` displays an
observation ID as an inert span and omits the statement citation. Structured
meeting memory lacks stable observation IDs. `build_demo_bundle.py` deliberately
omits tournament results; its Dashboard therefore explains an absent report.
The tour teaches controls but does not identify the author or link the source.
The README repeats results, history, and workflow detail. Its attribution of all
implementation to Claude and only review to Codex must account for the cleanup
implementation before publication. Root separately owns stale workflow prose
in `docs/lessons.md`.

Three cases verified through the current strict `ReplayLoader` already belong
to the featured games, without new recordings:

| Case | Exact current evidence |
| --- | --- |
| Supported role inference | 9p2i seed 23, meeting 0, tick 10. Opening by p-5 reports p-6 venting at tick 8; p-5's ballot cites `p-5:8:1`, whose memory text confirms that witness event. Other ballots cite opening turn 0; p-6 is ejected. This demonstrates use of certified role evidence, not general social deduction. |
| Persuasive unsupported accusation | 9p2i seed 46, meeting 3, tick 31. Reply turn 1 by p-9 calls p-1's route impossible; three ballots cite that reply and eject crewmate p-1. Replay input ticks 28–30 move p-1 through East Hall, Engineering, then Storage on legal edges. p-9's citation `p-9:29:3` confirms the first move; p-3's `p-3:29:1` instead describes p-4 in Cafeteria. A resolvable citation does not establish its accompanying inference. |
| Appropriately unresolved evidence | 9p2i seed 23, meeting 1, tick 12. All seven ballots voluntarily skip. Two flags concern crewmate p-4's overlapping adjacent-room alibi endpoints and are weak signals, with no role proof. The commentary should describe warranted uncertainty, not claim that skipping was globally optimal. |

Source rows are `replay-seed-23.jsonl:12`, `:15`, and
`replay-seed-46.jsonl:36` under `replays/samples/9p2i/`; filenames, IDs, roles,
and scene facts must be checked against source bytes when published.

## Acceptance

- [x] Statement, observation, and contradiction references navigate by exact
  identity to attributed evidence, the corresponding scene, and the relevant
  meeting-boundary memory. Missing references are explicit. No nearest-ID guess,
  prose parser, or automatic implication that a citation supports the claim.
- [x] Navigation preserves fog and outcome-reveal boundaries, distinguishes
  observation time from replay input/frame time, supports keyboard use, and
  survives reload or shared links. A forged/missing reference and the unrelated
  p-3 citation above exercise the adverse paths.
- [x] A compact static results artifact, at most 50 KiB per set uncompressed,
  recomputes its chosen metrics from current validated recordings. Each metric
  defines its numerator, denominator, scope, and limitation; source fingerprints
  and recording date/model/prompt provenance travel with it. Tampered outcomes
  or drifted source bytes fail publication. Recorded spending stays separate
  from verified outcomes. Every case link resolves within the baked bundle.
- [x] The standalone demo explains purpose, basic movement/task/meeting/win
  rules, recorded playback, source, and Daniel's direction versus agent-written
  code and AI review, including Codex's implementation contributions and
  agent-authored supporting material. It presents the three source-checked cases
  with spoilers withheld until requested; missing or changed evidence cannot
  retain old prose.
- [x] The README is a concise entry point, targeting at most 1,600 words, with
  separate watching, offline mechanics verification, and authorized live-run
  paths. A linked case study traces one actual owner decision through options,
  evidence, tradeoff, implementation/review, and limitations. Preserve explicit
  authorship disclosure and historical experimental verdicts; update displaced
  links rather than duplicating them; coordinate lessons-page corrections with
  root.
- [x] API and static browser journeys exercise all three cases, citation return
  navigation, keyboard/fog/reveal behavior, compact results, and source links.
  Clean-source reproduction passes.
- [x] All private ballot reasoning and mind-inspector tabs require the voter’s or
  inspected agent’s own lens, or omniscient mode. Outcome reveal cannot widen
  the lens; public statements and vote targets remain available. Already cached
  private memory stays hidden after a lens change.
- [ ] The combined full project gate passes.

## Constraints

Implementation starts only after root explicitly starts the next batch. Follow
`docs/architecture.md` Packages, observation firewall, and determinism. Use the
shared strict loader and fingerprint helper. Preserve raw historical reports,
recordings, media, experiment rulings, and additive API compatibility. No live
calls, model/detector/prompt changes, automatic claim-truth scorer, new training,
dependency changes, or deployment. Summary size bounds this publication artifact;
model-call payload delivery and performance work belong to roadmap 32–33.

Do not claim hand-written production code or independent human audits. A useful
case study is the explicit reference-recording override in the baseline-7
decision record §6.1, including its missed criteria and later limitations;
attribute each decision to its recorded author, not a reconstructed narrative.

## Expected scope

The portfolio agent owns all evidence UI (`BallotCard`, `TurnCard`, `MeetingView`,
memory display), store/URL helpers and navigation tests, compact results
producer/view, demo bundle, `GuidedTour`, case curation, shared presentation copy,
README, reading guide, and the new ownership case study.

The code agent remains the sole writer of API/schema/generated types/client
while delivering roadmap 32–33. Coordinate the smallest typed observation-ID
projection and summary DTO handoffs with that owner; do not edit shared API
files or broaden this card into payload/performance implementation. The workflow
agent owns observation temporal semantics in roadmap 12–13, not this UI; keep
navigation faithful to the existing recording's observation/frame clocks and
coordinate any shared semantics. Root owns `docs/lessons.md`, doc-fact gates,
index/roadmap, final integration, and the full gate.

## Record impact

Post-record reader/presentation repair. Future published summaries and curated
annotations bind to unchanged source recordings. No gameplay or adoption change.

## Validation

Read cases with `ReplayLoader.load_replay` and `get_meeting_memory`; assert exact
IDs, observation contents, legal route, voluntary ballots, roles, and outcomes.
Plant missing/foreign references, altered case facts, forged winners, and source
drift in temporary copies. Run focused API/script/frontend tests, generated-type
checks, strict mypy, ruff/format, document facts, and both real API/static browser
journeys. Re-run the README's clean-source offline commands, verify all samples,
and finish with `bash scripts/check.sh`. Record exact commands and source
fingerprints in Results; pre-existing passing installation evidence is a starting
point, not a substitute for checking the changed journey.

## Results

Implemented exact transcript/structured-artifact navigation and bounded observation
references within the architecture's privileged-reader boundary. A citation does
not certify its inference. Scene links use actual delivery frames; memory is
labelled as the meeting-boundary snapshot. Private evidence requires the observer's
lens or omniscient mode. URL state preserves the citation through reload and return
navigation without silently widening fog or revealing an ending.

The neutral `api/public_results.py` helper validates every source recording and
rejects an inventory shortened by the picker's skip-on-error behavior. Completed
outcomes require verification; unfinished records retain reported usage outside
win denominators. Case prose checks exact source hashes and reconstructed facts.
Recording dates come from manifests, not file timestamps. The static bundle
publishes full-set summaries, restricts case links to baked games, and retains
full model text in meeting files while using the lean bulk projection. Full
diagnostics require an explicit live-view disclosure.

The canonical 9-player set yields 50 completed games, 35 crew wins, 151 meetings,
and 95 ejections: 82 impostors and 13 innocents. Ejectee-specific role proof
accompanies 68/68 correct ejections; without it the count is 14/27. These are
co-occurrence counts, not causal attribution, and stay separate from the historical
four-set table. The roughly 1,400-word README links a case study preserving the
failed rule, explicit owner override, later non-adoptions, and Claude/Codex
implementation authorship. Historical media and recording/report bytes remain intact.

Targeted verification:

- `.venv/bin/pytest -q tests/api/test_public_results.py tests/scripts/test_build_demo_bundle.py`:
  38 passed. Planted winner/chronology/order corruption fails publication;
  source/projection drift, size bounds and valid partial-spend retention are covered.
- Focused evidence/playback/store/results frontend tests: 95 passed. TypeScript,
  ESLint, Ruff/format and strict mypy passed on owned source/tests.
- Real API/static browser journey: 5 passed in 43.7 seconds, including all cases,
  keyboard use, exact scenes, shared reload, explicit fog switching, unrelated and
  missing citations, and statement/contradiction anchors. Log:
  `/tmp/ailibi-evidence-browser-final.log`.
- Refreshed the previously installed isolated clean source copy, without `.git`
  or `.env`: two README fake seed-42 runs were byte-identical at tick 12 and $0;
  all 100 canonical samples verified; static build contains 7 games, 156 JSON
  files and approximately 4.9 MB total. Full browser suite: 13 passed and 3
  intentional historical-media capture skips, in 1.0 minute. Copy locator:
  `/tmp/ailibi-public-clean-copy-path`; retained log: `clean-browser-evidence.log`
  inside that copy. This preceded the final narrow featured-label correction.
- Final featured-label follow-through: removed the unsupported superlative,
  engine/detector attribution error and no-flags/no-knowledge equivalences.
  All 40 set tests passed, including six derived count/flag checks with planted
  failures. Both affected browser journeys passed in 14.8 seconds; TypeScript,
  ESLint, Ruff and strict mypy passed. Log: `/tmp/ailibi-featured-browser.log`.
  Temporary results/evidence screenshots were visually inspected for layout.
- Independent review of the public-results helper found no blocker. This owner
  independently reviewed the coordinated API/performance changes: all 176 canonical
  cited observations resolved to content and a scene; a genuine lean/full/lean
  cache-and-usage control passed.

Source fingerprints: 4p1i
`sha256:8bbf89bf86072311d45338dd84a98f4fe51c42fe6709bb606926072c4e617d14`;
9p2i `sha256:85fb119eeb09cc9b70fc8e9c7e202d41a3c3a93ff62b8ef824907c4cdec25d10`.
Final combined verification: `bash scripts/check.sh` passed with 6,599 Python
tests, 20 optional skips, three expected failures, and 467 frontend tests, plus
strict typing, lint, formatting, import/document contracts and production build.
`bash scripts/verify_samples.sh` passed all 100 canonical recordings. The final
clean-source journey preceded narrow copy and disclosure corrections; those
corrections passed the combined gate. No deployment, paid call, fresh recording
or experimental adoption occurred. The owner’s final branch review is pending.

Reopened during final integration: ballot rationale hid only a guard-specific
sentinel, leaving model-authored private reasoning visible through another lens.
The inspector also treated private observations and derived beliefs as public.
Root owns this coupled presentation follow-through; existing explicit lens
switching is preserved. Current full-gate evidence above covers the prior batch.


The reopened privacy repair now treats rationale, confidence, citations and
adjustment metadata as private ballot reasoning, regardless of whether a guard
marker exists. Public targets remain visible. Every mind-inspector tab requires
the inspected agent's lens or omniscient mode, and cross-lens snapshots are not
fetched eagerly. Already cached data is withheld by the render gate. Public
speech remains in the meeting transcript, with explicit lens switching retained.
Adjusted ballots use English explanations; a redirected ballot labels its
rationale as the original choice preceding the adjustment.

All 13 focused private-reasoning render controls pass; the isolated previous
commit fails the two unmarked-ballot and three private-memory/belief/flag controls.
Two additional baseline failures only reflect updated redaction copy, not newly
found prompt/response leaks. The real API evidence journey passed in 21.9 seconds,
including p-5 citation visibility before/after explicit lens switching. TypeScript
and ESLint passed. Logs: /tmp/ailibi-fog-tests.log,
/tmp/ailibi-fog-baseline.log, /tmp/ailibi-fog-browser.log.
Independent review approved the cached-memory, rationale, fetch and explicit
lens boundaries after 43 frontend checks and source inspection. This is a
spectator presentation boundary, not a server authorization layer; the API
remains a privileged local reader. Final static journey and the new combined
gate remain pending.
