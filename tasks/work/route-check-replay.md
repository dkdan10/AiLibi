# Offline replay of the route checks on the committed recordings

**Status:** ready

## Outcome

Before any round 3 is considered, the owner needs one count the diagnosis of 2026-10-02 could not give: on the
games already recorded, what each candidate route check would have shown each voter, and whether it would have
reached the meetings where the table charged a player with a move the map or the public regroup in fact allows.
Two readings of the existing check disagree today (it reaches 0 or 3 of the 5 ejected kill witnesses, and 12 or 17
of the 22 innocent ejections, in round 2), and the other check has never been counted on these games.

This card builds one offline, count-only lab instrument, `experiments/lab/route_check_replay.py`. It replays
the committed bytes of three 9-player columns, each read alone and never pooled:

- **r2**: `replays/samples/9p2i` at `59bbd1be`, the promoted round 2 (era `stage-b-r2`). Its 50 replays are
  byte-identical to `replays/candidates/stage-b-r2/9p2i` at `d41c9006` (`git ls-tree` of both: every replay
  blob equal; only `experiment-config.json` was added).
- **r1**: `replays/candidates/stage-b-r1/9p2i` at `59bbd1be`, unchanged since `d41c9006`.
- **s9**: the baseline-9 bytes of `replays/samples/9p2i`, which the promotion replaced in place, read from
  history at `d41c9006`. These are the same seeds 0-49 as r1 and r2, and the round-2 record (section 9.7)
  says the s9 column reproduces only there. `replays/ml_corpus/9p2i` is the same era but is **not read**: it
  is a different seed band, so it pairs with no r1 or r2 game, cannot settle a count the diagnosis made on
  seeds 0-49, and its meeting keys would expose a held band.

For every meeting it reports, per column and per meeting kind (report with vent proof, report without, button),
what each check would have shown each voter:

- **(a) the walkable-pair clause** of the corroboration ledger, built exactly as the meeting manager builds it
  (movement records, regroup ticks, trigger kind, living roster), with its one-hop, one-tick bound;
- **(b) the travel-check lines of the recorded field `evidence_reasoning_version = 2`**, as that field renders
  them into each voter's memory, read twice: on the recorded observations as they are, and with each legacy
  start-of-tick sighting labelled a snapshot (an approximation of the observation delivery that field
  requires; Evidence);
- **(c) a reference reading** of the narrow field the diagnosis sketches, computed inside the instrument from
  existing functions (stated placements at the table, several hops, a regroup crossing named). It is no
  mechanism and no arm; its gaps say what such a field would have to read.

Its reading is a **process count**, never role-correctness: impossible-move charges resting on stated pairs that
the map or the public regroup reconciles, and ejections of a player who had such a pair. It writes
`experiments/lab/report-route-check-replay.md` and `experiments/lab/results-route-check-replay.json`, and the
card's Results end with a dated reading the owner can decide round 3 on. It records nothing, changes no game
behaviour, prompt, recorded byte or published file, and authorizes no recording.

## Evidence

Every `path:line` is at `59bbd1be` (labelled as such) and is re-anchored by its symbol at dispatch;
`meetings/`, `agents/` and `engine/` are unchanged between `d41c9006` and `59bbd1be` (`git diff --stat` reads
empty), so the diagnosis's `d41c9006` citations name the same code. Every count below is re-measured by the
instrument at dispatch and the dispatch figure governs.

**The dispute** (diagnosis memo of 2026-10-02, `tasks/diagnosis-2026-10-02/README.md`, Part 2.2 amendment 7
and Part 3 card 2). A transcript-only probe (`walkfire.py`: no movement records, no
regroup ticks) finds a walkable pair for the ejected player in 12 of 22 round-2 innocent ejections, 1 of 44
impostor ejections and 0 of the 5 ejected witnesses; the refuter's version, adding the movement destinations
and regroup ticks the manager passes, finds 17 of 22 and 3 of 5. The memo calls the claim "not established
either way". The hand classification (route misjudged in 11 of 22) is one rater's, with five boundary cases
(9 to 12), and keyword stand-ins are not specific (11 of 17 ejected reporters against 12 of 44 impostor
ejections). The five ejected witnesses are r2 seeds 28, 29, 35 and 43 at their first meeting and seed 30 at
its second (`reporter-ejections.md`, same folder).

**Check (a) at `59bbd1be`.**
- The pair rule is `_walkable_transits` (`meetings/corroboration.py:561-600`): a pair qualifies when
  `1 <= hops <= elapsed` within `MAP_ARBITRATION_MAX_HOPS = 1` and `MAP_ARBITRATION_MAX_TICK_GAP = 1`
  (`meetings/constants.py:62-63`), at most `MAX_WALKABLE_TRANSITS_PER_SUBJECT = 2` per subject
  (`meetings/corroboration.py:97`). It reconciles or stays silent; it never charges.
- `build_testimony_ledger` (`:603-721`) builds rows only for players accused at the meeting, over
  `reconstruct_stated_paths` (`meetings/transcript.py:1415-1582`): spoken sightings that pass the relevance
  gate (spawn window, kill-scene rooms and the regroup window dropped, `:1250-1310`), plus each speaker's own
  whereabouts. Alibi routes are not placements.
- The manager builds it only under the ambient corroboration switch (`meetings/manager.py:1703-1716`, resolved
  at `:1363-1367`; the switch, `meetings/corroboration.py:100-124`), off in all three columns. The ballot
  shows each pair to a voter whose candidate list holds the subject
  (`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:256-257`, `:269-270`). Because its only switch is
  ambient, (a) is not itself a round-3 arm; using its rule in a round would need a recorded field, which is
  the narrow field.
- Cross-check: the round-2 record's two committed cells for "ejected with a walkable pair" (section 9.8: 69/411
  over the four baseline-9 sets, 56/321 over three) differ by exactly s9's 90 ejections, so (a) on s9 reads 13
  of 90. s9 has no regroup, so the counterfactual's ledger there is (a) as built.

**Check (b) at `59bbd1be`.**
- `v2_evidence_context_rows` (`agents/memory/evidence_context.py:340-591`) reads one voter's memory: the
  voter's own sightings, each public regroup as a placement (`:379-391`), and reported claims of kind
  whereabouts, alibi or saw_player (`:395-406`). It walks the map with several hops through `assess_travel`
  (`:110-158`) and names an interval that crosses a public regroup undecidable (`:532-544`). The store renders
  these rows only under version 2 (`agents/memory/store.py:729-747`).
- **Timing.** Reported testimony is absorbed after each meeting (`orchestrator/game.py:3602-3625`), and the
  ballot renders the memory held at the meeting's open (`meetings/manager.py:2335-2341`). So at a first
  meeting (b) holds no claim at all, and at any meeting it never holds that meeting's own claims.
- **Phase.** All three columns use legacy observation delivery, so a recorded sighting carries no phase and
  reads "unknown"; under the unknown-phase rule (`agents/memory/evidence_context.py:146-151`) a walk fits only
  with one spare tick. One hop in one tick, or two hops in two, reads "insufficient timing", which is exactly
  the kill witness's walk-in.
- **Prerequisite.** The runner and the game refuse evidence version 2 without temporal observations version 2
  (`orchestrator/game.py:1576-1582`, `:2577-2583`). That is the ambient substrate toggle
  `AILIBI_TEMPORAL_OBSERVATIONS` (`docs/architecture.md`, "Determinism and the substrate ladder"), which the
  wave kept OFF because a temporal-ON set fails the validity gate's bare-shell provenance check and changes
  every prompt (`tasks/decision-2026-09-24-stage-b-wave.md:178-180`). The field is also a package (death
  evidence and account-uncertainty lines), and its one live reading, the archived fifth run, cast 14 EJECT
  and 136 SKIP ballots (`docs/process-scorecard.md:227-236`).
- A legacy snapshot packet is built from the pre-action world state
  (`tests/meetings/test_prompt_byte_golden.py:698-723`), the instant temporal version 2 calls a snapshot; a
  legacy move or action-sourced row is dated at delivery, not at its event. That is why the (b-snapshot)
  reading relabels plain sightings only.

**The walk.** `tests.meetings.test_prompt_byte_golden.walk_replay_meetings` (`:726-888`) is the one committed
reconstruction that drives the real `MeetingManager` and yields each meeting's participants (their sighting
and movement records) and each agent's memory at the meeting's open (`ReconstructedMeeting`, `:337-394`), under
the recording's own settings, with every state hash verified. `scripts/counterfactual_phase21.py:84-92`
records the ruling that lets a non-test module import it. `render_for_prompt` writes to working memory
(`agents/memory/store.py:768-776`), so a render made for counting runs on a deep copy.

**Counts to re-measure**, for s9, r1 and r2 (round-2 record sections 6.4 and 9.6; diagnosis section 1.4):
ejections 90, 54 and 66 (innocent 9, 15 and 22; impostor 81, 39 and 44); meetings 145, 124 and 117 (report
135, 118 and 114; button 10, 6 and 3). A **witness meeting** is a report meeting whose reporter the census's
kill facts record as a witness of a kill since the previous meeting: 3, 3 and 14 (crew-witnessed kills,
census `kills_seen_by_crew`, 3, 4 and 14).

## Acceptance

- [ ] **Columns with exact provenance.** `uv run python -m experiments.lab.route_check_replay --set
  LABEL=COMMIT:PATH ...` resolves each COMMIT to its full commit sha when the run starts (`git rev-parse
  --verify COMMIT^{commit}`), materializes every column with `git archive SHA PATH` into a temporary directory,
  and records each column's full sha beside its path, tree id and recorded experiment config in the JSON.
  - `--check` takes its columns from the JSON, never from the command line or `HEAD`. It re-archives each
    recorded sha, and before it recomputes anything it refuses a column whose recorded tree id differs from the
    tree of `SHA:PATH`, naming the column.
  - The run refuses: a commit or path that does not resolve; a column whose rows' config differs from the one
    its label declares (r2: the era's declared config; r1: the round's config file; s9: none); and any request
    to pool columns.
  - Mechanism: the materializer and `tests/experiments/test_route_check_replay.py`, which resolves the
    checkout's `HEAD` to its sha or builds temporary repositories, and never reads a column through a symbolic
    ref.
  - Planted: r1's tree under the r2 label, and an unknown commit, each exit non-zero naming the cause. A copy of
    the JSON whose recorded tree id for one column differs from its sha's tree makes `--check` exit 1 naming that
    column. In a temporary repository, a file committed into a column's directory after the run (as
    `rubric-extractor-era` will add `replays/samples/9p2i/results-rubric-score.json`) leaves `--check` green,
    because `--check` reads the recorded sha.
- [ ] **A faithful walk, or none.** Every meeting is read through `walk_replay_meetings` with the recording's
  settings. The instrument raises, naming (column, seed, meeting), when a recorded prompt is missed, when a
  state hash differs, and when its meetings per column differ from the census's (`load_census_inputs`). Each
  meeting is counted before the walk resumes, and the live memories are left as they were. Mechanism: the
  integrity checks, and a test comparing each live memory before and after the per-meeting counting. Planted:
  a temporary copy of one r2 game with one byte of a recorded prompt flipped raises; a census fact list with
  one meeting removed raises; a counting step that appends one row to the live store fails the comparison.
- [ ] **(a) as the manager builds it.** The instrument calls `build_testimony_ledger` with the firewalled
  sighting mapping, the movement records, the opener, the living roster, the trigger kind and
  `derive_regroup_ticks(recorded, earlier meeting ticks)` (`orchestrator/replay.py:1498-1514`), and shows a
  row to the voters whose `_candidate_targets` (`meetings/manager.py:5472`) hold the subject. Mechanism: a
  parity test drives one recorded r2 game through the walk with the manager's corroboration resolver patched
  ON (a monkeypatch; no environment write), spies the arguments its ledger call receives at a meeting after
  the first, and requires them equal to the instrument's. Perturbed: dropping `regroup_ticks` or the movement
  records from the instrument's call turns the parity test red. Sourced constants, each patched in
  `meetings.corroboration`'s namespace: the tick bound set to 2 reconciles a planted West Hall at t, Admin at
  t+2; with it, the hop bound set to 2 also reconciles planted case 2; the subject cap set to 1 cuts a planted
  three-pair row to one line. So the instrument reads the live rule and holds no copy of it.
- [ ] **The dispute settled.** Beside (a) as built, a perturbed leg drops the movement records and regroup ticks
  (the transcript-only probe). Results reports both on r2's innocent ejections, impostor ejections and ejected
  witnesses, names the input that moves each case between the legs, and explains any difference from 12/22,
  17/22, 0/5 or 3/5 case by case. On s9, (a) as built must read 13 of 90 ejections with a walkable pair; a
  different figure stops the card and goes to the orchestrator, and is never adjusted to fit. Mechanism: the
  two legs and the s9 agreement assertion. Perturbed: the assertion with its expected figure moved by one
  fails; Results also states whether the transcript-only leg would pass it on s9.
- [ ] **(b) as the recorded field renders it.** For each voter, the instrument calls `v2_evidence_context_rows`
  on a version-2 view of the voter's memory at the meeting's open, deriving the voter's own id and teammates
  as the store does (`_latest_self_guard_fields`, `agents/memory/store.py:1162`). It classifies every travel
  row as fits, cannot reconcile, insufficient timing, crosses the regroup or unverifiable, and raises on a
  travel row it cannot classify. It counts rows offered and, separately, rows that a version-2
  `render_for_prompt` on a deep copy keeps, at the budget the recording's runner gives the ballot re-render
  (`orchestrator/game.py:1788`). It checks that at every first meeting the voters hold no reported claim, and
  raises otherwise. Mechanism: the classifier and an equivalence test: one ingestion sequence into a
  version-None and a version-2 memory yields identical travel rows. Planted: a travel line with an altered
  suffix raises; a claim row injected into a first-meeting memory raises.
- [ ] **(b-snapshot), labelled.** The same rows with each plain recorded sighting (built from the pre-action
  state, no action payload) labelled a start-of-tick snapshot; move rows and action-sourced rows stay unknown.
  The report calls it an approximation of temporal delivery, which would also add event rows these bytes lack.
  Mechanism: the relabelling function and its unit test. Planted: relabelling a move row turns that test red.
- [ ] **(c), the reference reading.** Its placements are `reconstruct_stated_paths` with the movement records,
  the regroup ticks and `include_kill_scene=True`, plus the stays of alibi routes about the candidate
  (`maximal_stays`, `meetings/transcript.py:991`) at their first and last tick, for every living candidate. A
  pair in two different rooms is reconciled when `1 <= hops <= elapsed` over the whole canonical map
  (`room_hops` bounded by the room count), and a pair whose interval holds a public regroup tick is reconciled
  by the regroup. No `meetings/` or `agents/` code changes. Mechanism: unit tests over the planted cases.
  Planted: dropping the regroup marking turns case 3 red.
- [ ] **The planted route cases tell the checks apart.** Each runs through the code paths the walk uses (a
  built transcript for (a) and (c); a built memory on the canonical public map for (b)):

  | case | (a) | (b) unknown phase | (b) snapshot phase | (c) |
  | --- | --- | --- | --- | --- |
  | 1. West Hall at t, Admin at t+1 | reconciled | insufficient timing | fits | reconciled |
  | 2. Admin at t, Cafeteria at t+2 | silent | insufficient timing | fits | reconciled |
  | 2'. Admin at t, Cafeteria at t+3 | silent | fits | fits | reconciled |
  | 3. Labs at 10; regroup to Cafeteria at 11 | silent | crosses the regroup | crosses the regroup | by the regroup |

  In case 3 a meeting closes at tick 10, (a) leaves the charge unanswered, and a sighting inside the regroup
  window is dropped. Mechanism: the four tests. Proof: the four rows are pairwise distinct, so a classifier
  that conflated any two checks fails at least one row.
- [ ] **Properties over the map.** Hypothesis, `settings(deadline=None)`, over pairs of distinct canonical rooms
  and ticks away from a regroup: (a) reconciled implies (c) reconciled; (b) fits at unknown phase implies (c)
  reconciled; (b) cannot reconcile at unknown phase implies (c) not reconciled; at snapshot phase, (b) fits
  exactly when (c) reconciles. Mechanism: the properties. Perturbed: (c) with its bound off by one in either
  direction fails at least one of them.
- [ ] **The process count, role-blind.** The **universe** is every typed placement of a player spoken at the
  meeting (sightings naming them as subject or company, movement sightings, their whereabouts, the stays of
  alibi routes about them, vent sightings), ungated. A pair in it is **reconcilable** when its rooms differ
  and `1 <= hops <= elapsed` over the whole map, or its interval holds a public regroup tick. A **charge** is
  an EJECT ballot whose `primary_reason_id` cites a turn carrying a typed placement of the target, or a
  contradiction flag naming the target whose events are such placements. A **misjudged case** is an ejection
  carried by a charge whose placement ends a reconcilable pair. Check X **reaches** a case when it shows a line about the ejected player
  over two different rooms that reconciles, fits or crosses the regroup, to at least one voter who cast EJECT
  against them; it **reaches the charge** when that line's pair holds the charged placement.
  Insufficient-timing lines are counted apart, never as reaching. Each unreached case is attributed to the
  first reason in a fixed order: the placement is outside the check's inputs (by kind), the relevance gate,
  the hop bound, the tick bound, the cap, the claim not yet held at ballot time, the phase rule. The JSON
  carries every count per column and meeting kind; the report sets them out by ejection class (innocent,
  impostor, ejected witness) as description only. The committed judgment net (`IMPOSSIBLE_TRANSIT_PATTERN`,
  `scripts/counterfactual_phase21.py:299`) is an informational column, never the reading. Mechanism:
  role-free signatures, and a property that permuting the role map moves only the class columns. Planted: a
  role read inserted into a line computation fails the property.
- [ ] **Count-only, no model call.** The JSON and the report carry ids, ticks, room ids, kinds, booleans and
  counts, keyed by (column, seed, meeting). They carry no rendered prompt, memory line, rationale, transcript
  text or seed-band prefix. No provider client is built: the walk's recorded-response stub answers from the
  recording's bytes. Mechanism: a scan test over a one-game run's outputs for any recorded turn text,
  rationale or travel line, and a run with socket connection refused. Planted: a rationale written into the
  JSON fails the scan.
- [ ] **The artifacts, pinned.** The instrument writes the report (the decision informed; hypothesis, method,
  result, decision input; the lab's caveat that replayed ballots propagate no game state; each term defined
  where used) and the JSON. `--check` recomputes both from the recorded shas and compares, so it reproduces the
  committed JSON on any later `main`. The `experiments/lab/` row of `docs/artifacts.md` goes from 164 to 167
  files in this card's last commit, after its final merge of `main`: the count `scripts/verify_ml_evidence.py`
  holds against the git index (`_IN_TREE_INVENTORY`, `:2869`). No lab artifact is hash-pinned file by file, so
  nothing else is registered. Mechanism: `--check` and the offline evidence check. Perturbed: one count edited
  in a copy of the JSON makes `--check` exit 1; the row left at 164 fails the inventory leg.
- [ ] **The dated reading, by a rule fixed here.** Results ends with "Reading (YYYY-MM-DD)", which applies this
  rule to r2 verbatim and reports s9 and r1 beside it. Let M be r2's misjudged cases, W the ones at witness
  meetings, and R(X) the cases check X reaches.
  1. M empty: name no route arm.
  2. Else, if (b-snapshot) reaches at least half of M, and of W when W is not empty: name
     `evidence_reasoning_version = 2`, conditional on the owner lifting the temporal exclusion it requires,
     with the package cautions; say whether (b) as recorded also reaches them.
  3. Else, if (c) does: name the narrow new field (versioned, default off, set only from the config file, its
     own stamp, one role-blind line per living candidate that never asserts presence or honesty), shaped by
     (c)'s unreached reasons, as a card to write with planted cases and fake and scripted rehearsals before any
     spend.
  4. Else: name no route arm, and state what the unreached cases share.
  The reading authorizes no recording; a round 3 is the owner's spend decision. Mechanism: the rule's inputs
  are JSON fields, and the report prints the branch taken. Perturbed: the rule on a copy of the JSON with every
  R set to 0 takes branch 4.
- [ ] **The wave's lessons.** Every production line is enforced by a test that goes red when neutered (a neuter
  pass listed in Results); one bounded mutation pass over the instrument with the listed operator classes only
  (F filter, S swap, N comparison, C constant, M message, T tuple member, B branch swap, L loaded source to
  literal), each survivor killed or argued equivalent; no test weakened; every number in Results measured at
  the head that states it, with its command; guarantees stated at delivered strength; no live-tense sentence
  about older behaviour left in a touched file. Mechanism: Results' neuter and mutation tables. Proof: each
  row names its red test.
- [ ] **Every gate, green.** `bash scripts/check.sh` in a clean worktree, run to its end, plus the commands in
  Validation, each with its real exit code in Results. Perturbed: the instrument's tests run against a build
  whose (a) leg ignores regroup ticks exit non-zero.

## Constraints

- **Authorization and spend.** No live provider call, no recorder run, no spend. The instrument builds no
  provider client; the walk's recorded-response stub answers every call from the recording's bytes, and the
  tests run on the fake provider as the suite always does. The untracked `.env` is never read and no
  `AILIBI_*` variable is exported. No rendered prompt, memory line, transcript text or seed-band prefix is
  printed or written.
- **House rules.** The engine stays a pure deterministic tick; no module under `agents/` gains an `engine/`
  import, and `lint-imports` stays green. No module-level mutable state; invalid input raises, with no silent
  fallback. A new invariant check carries a planted or perturbed case. Claims name their enforcing mechanism,
  and every number is reproducible from committed bytes, with its command in Results. One writer per file.
- **No behaviour moves.** No new `AILIBI_*` lever, no environment switch, no new experiment field, no prompt
  registry bump, no template or detector change. Nothing under `engine/`, `agents/`, `meetings/`,
  `observation/`, `orchestrator/`, `llm/`, `training/`, `replays/` or `tests/fixtures/` is written. No recorded
  byte is edited, no history re-scored; the corpus FROZEN line and every ML artifact stay put (offline
  `scripts/verify_ml_evidence.py`, never `--complete`). ML stays held (ruling 12).
- **The owner's direction.** A vote or skip must rest on data the agent holds. Role-correctness is reported and
  never a gate, and nothing here pushes an agent toward the right answer: the instrument is offline and feeds
  nothing back. The meeting layer labels and never rewrites. A check that also reaches impostor ejections is
  reported, not discounted.
- **Why `experiments/lab/` and not `eval/`.** It is a one-off counterfactual on committed bytes for one owner
  decision, which is the lab's charter (`experiments/lab/README.md`: offline labs read committed or history
  bytes and write only reports there). It is not a standing census cell: the census stays a separate report,
  and its new cells are the sibling card's. It imports a test-module walk, which the counterfactual script
  does by recorded ruling but a production `eval/` module should not. Lab modules stay under strict mypy
  (`pyproject.toml`'s exclusion names only listed spikes).
- **History.** The s9 column needs `d41c9006`, and `--check` re-archives every recorded sha, so the full run and
  `--check` run in a full clone. The tests resolve the checkout's `HEAD` to its sha or build temporary
  repositories, so CI's shallow checkout runs them.
- **Sibling cards and merge order.** This card dispatches in parallel with `census-reporter-base-rate` and
  `post-promotion-follow-through` from `main` at the coordination commit that lands the four cards. The three
  merge one at a time: census first, then this card, then the follow-through card (by the owner).
  `rubric-extractor-era` dispatches after the follow-through merge and merges last.
  - It reads `eval/gameplay_census.py` (`load_census_inputs`), `eval/eras.py` and
    `scripts/counterfactual_phase21.py` (`IMPOSSIBLE_TRANSIT_PATTERN`) and writes none of them; they and
    `scripts/publish_gameplay_census.py` are `census-reporter-base-rate`'s. The census card merges first, so this
    card merges `main` after that merge and re-runs its denominator agreement there; Results quotes that run.
  - `docs/artifacts.md`: this card writes only the `experiments/lab/` row (164 to 167), in its last commit after
    merging `main`, then re-runs `scripts/verify_ml_evidence.py` offline. `rubric-extractor-era` is the later
    writer of the same row: it recounts it from 167 to 169 when it merges, after this card. The census and
    follow-through cards write other rows.
  - `tasks/README.md`: the inventory sentence only, re-derived with `scripts/validate_task_docs.py` at this
    card's final merge of `main`, after the census card's.
  - `replays/samples/9p2i/`: `rubric-extractor-era` adds `results-rubric-score.json` there, which gives the
    directory a new tree id. This card reads that directory as its r2 column by the commit sha the JSON records,
    never `HEAD`.
  - `experiments/lab/`: `rubric-extractor-era` adds two `stage-b-r2` JSONs and edits the run line in
    `report-rubric-interestingness.md`; no file is shared with this card.
  - It never writes `tests/scripts/test_refresh_samples.py`.
- **Publication.** Lab artifacts, a lab module, its tests and one registry row: nothing the demo bundle reads
  changes, so the merge publishes nothing new (`pages.yml` rebuilds an identical bundle; the PR shows
  `build_demo_bundle.py --out` at base and head with an empty `diff -rq`). The merge is the orchestrator's.
- **Delivery.** Branch `work/route-check-replay`, one PR into `main` with every section of the PR template,
  merged by merge commit or fast-forward, never squash. Each commit body ends with
  `Card: tasks/work/route-check-replay.md` immediately followed by the exact line
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Scratch work stays outside the repository.

## Expected scope

- `experiments/lab/route_check_replay.py` (new): the instrument and its CLI.
- `experiments/lab/report-route-check-replay.md` (new): written by the instrument.
- `experiments/lab/results-route-check-replay.json` (new): written by the instrument.
- `tests/experiments/test_route_check_replay.py` (new): planted cases, properties, parity, integrity, scan.
- `docs/artifacts.md`: the `experiments/lab/` row's file count only.
- `tasks/work/route-check-replay.md`: this card's Status and Results.
- `tasks/README.md`: the inventory sentence, as the validator derives it.

Test-side reads of committed sets use `tests/_helpers/committed.py` as it stands; it is not written. A file
outside this list needs a line in Results naming it and why; a file another card of the wave owns is not
touched, and the conflict goes to the orchestrator.

## Record impact

None. No recording is made or changed, no future game behaves differently, no prompt or detector byte moves,
and no evaluation cell, scorecard row or census cell changes. The new lab artifacts are class (b) records in
`experiments/lab/`, counted by the registry row. Measurement: the instrument's JSON and report at the
implementing head, reproduced by `--check`.

## Validation

```sh
git fetch origin && git checkout --detach origin/main && uv sync --frozen   # then branch work/route-check-replay
# the dispatch base is the coordination commit that lands the four cards; it moves nothing under replays/,
# so its trees there are 59bbd1be's
# the run: three columns, never pooled (a full clone, for d41c9006); each column names a commit, never HEAD
uv run python -m experiments.lab.route_check_replay \
  --set r2=59bbd1be:replays/samples/9p2i \
  --set r1=59bbd1be:replays/candidates/stage-b-r1/9p2i \
  --set s9=d41c9006:replays/samples/9p2i \
  --out-report experiments/lab/report-route-check-replay.md \
  --out-json experiments/lab/results-route-check-replay.json
uv run python -m experiments.lab.route_check_replay --check   # the JSON's recorded shas; exit 0
git rev-parse 59bbd1be 59bbd1be:replays/samples/9p2i 59bbd1be:replays/candidates/stage-b-r1/9p2i
git rev-parse d41c9006 d41c9006:replays/samples/9p2i   # the shas and tree ids the JSON records
# the denominators, count-only, each column alone (s9's census runs inside the instrument, on its copy)
uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout
uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout
# the instrument's tests, then the gates
uv run pytest tests/experiments/test_route_check_replay.py
uv run lint-imports
uv run python scripts/verify_ml_evidence.py   # offline; never --complete
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/build_demo_bundle.py --out <scratch>/base   # at 59bbd1be
uv run python scripts/build_demo_bundle.py --out <scratch>/head && diff -rq <scratch>/base <scratch>/head
bash scripts/check.sh   # clean worktree, run to its end
```

Run each gate to its end, because `set -e` in `check.sh` hides later gates. On macOS the evolution-strategy hash
pin is Linux-only, so gate in a clean worktree and cite CI for it.

## Results

Not started. On completion this section records the commits, the sections relied on (this card; the diagnosis
memo's Parts 2.2, 3 and 4; the round-2 record's sections 6.4 and 9.6 to 9.8; `docs/architecture.md`,
"Determinism and the substrate ladder" and "Explicit cleanup experiments"; `docs/experiment-arms.md`; the
decision memo's sections 1 and 7), each acceptance item's evidence with its command and exit code, the wall
time of the full run, the per-column tables, the dispute settled case by case, the neuter and mutation tables,
decisions, limitations and deviations. It ends with the dated reading the rule above produces.
