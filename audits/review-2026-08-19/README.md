# The 2026-08-19 review: four headline claims it had to retract

Three blind AI review tracks were run over this repository in August 2026 — one on gameplay
behaviour, one on code and architecture, one on it as a portfolio — plus a fourth track that
synthesised them. They produced 171 findings. The interesting part is not the findings.

The interesting part is that the reviews **disproved four of their own headline claims** and
corrected severities in both directions, because each track's flagship conclusions were then
handed to an adversarial verifier whose job was to falsify them. That is what this index is
titled by, and it is why the tree is published at all: an unverified pile of self-criticism is
noise. A pile that audits itself, in public, with each surviving finding linked to the change
that closed it, is a measurement.

The narrative half — what the review taught the author — is [docs/lessons.md](../../docs/lessons.md).

---

## 1. The retractions

Each row is a claim the review published, then re-derived and withdrew. The verdict file that
owns the retraction is linked with the lines that carry it.

| Claim as filed | What the re-derivation measured | Owned by |
|---|---|---|
| **G-1** — agents have no self-location in memory, so ~73.4% of wrongful crew ejections are caused by the victim's own false whereabouts | **44.3% victim-caused, 21.5% witness-caused.** Of 79 crew ejections: 35 where the placement was false, 17 where the *sighting* was false and the victim truthful, and 23 that are real one-tick corridor transits with both accounts true. 35 + 23 = 58 is exactly how the claim reached 73.4%. Two of the claim's own exemplars fall in the opposite bucket | [`A/verdicts.md`](A/verdicts.md) :12-22 |
| **G-6** — 230 of 798 corpses survive a meeting invisible to the crew (`discovered_by=None`), so bodies vanish from the game | **Backwards, and unreproducible.** `engine/visibility.py:93` reads `body.discovered_by is None and body.room in visible_room_set` — `discovered_by=None` is precisely what makes a body visible and reportable. Measured 189/798, not 230/798. Zero real misses corpus-wide: of 172 never-reported bodies only 6 were ever seen by a living crewmate, all 6 on the game's final tick | [`A/verdicts.md`](A/verdicts.md) :111-131 |
| **G-7** — all 963 body reports carry the report tick and never the death tick, and none lands on the kill tick | **A two-clock artefact.** Agent memory stamps run exactly +1 against the engine clock on 18,936 of 18,936 discriminating sightings. Applying the convention: corrected median 3, and **171/963 = 17.8% land exactly on the kill tick**. The mechanism survives — there is still no way to *speak* a witnessed kill — but every quoted figure was inflated by one | [`A/verdicts.md`](A/verdicts.md) :137-147 |
| **G-4** (the vent half) — crewmates fabricate vent sightings and the system renders them as proof | **739 of 748 spoken vent claims = 98.8% grounded** in the speaker's own recorded field of view. All nine exceptions name real impostors; seven of them are witnessed kills filed in the nearest available slot. The claim's own cited example is fully grounded. The sighting half of G-4 survives and is fixed | [`A/verdicts.md`](A/verdicts.md) :222-228 |
| **C-33** — 969 lines forked verbatim across the `agents ↛ training` firewall with **no parity test**, so the learned search may optimise a different action space than ships | **Refuted by experiment.** Five always-on parity gates exist and run both implementations in lockstep; an injected 1e-9 one-sided perturbation produced **446 mismatches** and went loudly red. The duplication is real and stays a maintenance tax; the load-bearing risk does not. Severity corrected down to P2 | [`B/verdicts.md`](B/verdicts.md) :340-375 |

### Severities moved in both directions

The verifier was not a rubber stamp in one direction only.

- **Up.** `C-32` went **P2 → P1** once a planted probe inside the agent package importing the
  orchestrator passed all four import contracts — the firewall's own coverage gap, not a style
  issue ([`B/verdicts.md`](B/verdicts.md) :67). `C-1` and `C-31` moved up the same way.
- **Down.** `C-42` was filed at implied P1 and corrected to **P2**: the mechanism and direction
  were exact, but the measured saving only bites the provider-free paths, so the real-world
  cost was far smaller than the filing implied ([`B/verdicts.md`](B/verdicts.md) :415-441).
  `C-33` above moved down for the same kind of reason.

---

## 2. What each track was, and how it was run

The three review tracks were run **blind to one another** — no track saw another's findings
until the synthesis track collated them. The tree below is **49 markdown files, 16,849 lines,
roughly 249,000 words, 1.7 MB**. Nobody should read it end to end; this index exists so that
nobody has to.

| Track | Files | What it did | Adversarial verdicts |
|---|---|---|---|
| [`A/`](A/collated-findings.md) — gameplay | 19 | 13 behavioural reports over the committed corpus — 8 full game walks, 4 evidence-economy slices, 1 spectator UX pass — across 300 replays and 707 meetings, collated into findings `G-1`…`G-41` plus 43 design ideas | **12** ([`A/verdicts.md`](A/verdicts.md)) |
| [`B/`](B/collated-findings.md) — code and architecture | 18 | 16 area reviews (engine, agents, meetings, orchestrator, api, llm, eval, training, frontend ×2, tests/CI, perf, repo health, observation firewall), collated into `C-1`…`C-130`. **No P0** at this track's definition of P0 | **14** ([`B/verdicts.md`](B/verdicts.md)) |
| [`C/`](C/collated-portfolio.md) — the repository as a portfolio | 7 | 6 reads: four hiring personas (backend hiring manager, ML research lead, frontend product engineer, recruiter skimmer) and two cross-cuts (a cold front-door reproduction attempt, a narrative and positioning pass), collated into lettered items with rulings | none — this track issues rulings, not verdicts |
| [`D/`](D/FINAL-synthesis.md) — synthesis | 5 | Three independent syntheses of the same inputs (ambition, pragmatic, credibility), a cross-track map, and one final synthesis that ruled where they disagreed | none — it adjudicates the other three |

The single most useful output of the synthesis is its reconciliation of the two technical
tracks' disagreement about severity: they were using different definitions, and every
gameplay defect was a faithful implementation of correct code
([`D/FINAL-synthesis.md`](D/FINAL-synthesis.md) §0, ruling R11).

---

## 3. What was acted on

One row per finding this phase closed. "Closed by" is the task in
[`tasks/phase-20.md`](../../tasks/phase-20.md) that owns the change; the pull request is the
squash commit on `main` whose subject ends in that number. Findings appear in more than one
contract — instruments, the pre-registration and the recording all cite them — so the row names
the task that made the change, not every task that mentions it.

| Finding | What it claimed | Closed by | Pull request |
|---|---|---|---|
| `C-1` | Kill, report and sabotage were legal from inside a vent | 20.11 | [#355](https://github.com/dkdan10/AiLibi/pull/355) |
| `C-2` | Redistributing a dead player's jobs minted "you completed X" memories for work never done | 20.23 | [#375](https://github.com/dkdan10/AiLibi/pull/375) |
| `C-3` | The impostor kill gate re-validated only the top-scored target | 20.32 | [#373](https://github.com/dkdan10/AiLibi/pull/373) |
| `C-4` | Stalking ignored negative evidence and chased sightings already refuted | 20.32 | [#373](https://github.com/dkdan10/AiLibi/pull/373) |
| `C-5` | A truncated replay file returned 500 for the whole listing and the cost endpoint | 20.4 | [#357](https://github.com/dkdan10/AiLibi/pull/357) |
| `C-6` | The episode reader accepted a corrupted replay as a legitimate truncation | 20.10 | [#356](https://github.com/dkdan10/AiLibi/pull/356) |
| `C-7` | The map painted corpses the engine had already consumed, in 66.8% of frames | 20.1 | [#354](https://github.com/dkdan10/AiLibi/pull/354) |
| `C-8` | Two raw fetches bypassed the view-model version guard | 20.16 | [#370](https://github.com/dkdan10/AiLibi/pull/370) |
| `C-9` | Two stacked focus traps locked the keyboard onto one control | 20.3 | [#367](https://github.com/dkdan10/AiLibi/pull/367) |
| `C-11` | Incriminating testimony was never checked against the speaker's own record | 20.26 | [#378](https://github.com/dkdan10/AiLibi/pull/378) |
| `C-31` | The leak scanner validated packet shape and content, never entitlement | 20.8 | [#363](https://github.com/dkdan10/AiLibi/pull/363) |
| `C-32` | The import contracts covered 89 of 383 Python files | 20.9 | [#352](https://github.com/dkdan10/AiLibi/pull/352) |
| `C-34` | The firewall test planted forbidden imports in the live working tree | 20.9 | [#352](https://github.com/dkdan10/AiLibi/pull/352) |
| `C-35` | The suite pinned 1 of 43 environment variables, so ambient settings moved results | 20.17 | [#361](https://github.com/dkdan10/AiLibi/pull/361) |
| `C-42` | A fresh template environment was built per game, recompiling every template | 20.19 | [#362](https://github.com/dkdan10/AiLibi/pull/362) |
| `C-43` | The memory read rescanned the whole log, quadratic in game length | 20.19 | [#362](https://github.com/dkdan10/AiLibi/pull/362) |
| `C-46` | The tournament ran strictly serially over independent games | 20.18 | [#368](https://github.com/dkdan10/AiLibi/pull/368) |
| `C-48` | The default test tier ran serially with no parallel runner | 20.18 | [#368](https://github.com/dkdan10/AiLibi/pull/368) |
| `C-64` | Retired settings left ten no-op resolvers, their constants and their branches behind | 20.37 | [#391](https://github.com/dkdan10/AiLibi/pull/391) |
| `C-67` | Guard activity survived only as marker substrings parsed out of spoken text | 20.28 | [#380](https://github.com/dkdan10/AiLibi/pull/380) |
| `C-73` | Reported testimony was starved out of the memory render in the games it targets | 20.30 | [#382](https://github.com/dkdan10/AiLibi/pull/382) |
| `C-74` | The multi-hour recording script had no coverage of its real worker paths | 20.21 | [#359](https://github.com/dkdan10/AiLibi/pull/359) |
| `C-83` | Import-time side effects in the prompt loader forced a mirrored resolver elsewhere | 20.5 | [#351](https://github.com/dkdan10/AiLibi/pull/351) |
| `C-88` | Fake-provider meetings are degenerate — every fake vote normalises to a skip | 20.12 | [#371](https://github.com/dkdan10/AiLibi/pull/371) |
| `C-96` | The documented evidence restore and the documented gate excluded each other | 20.17 | [#361](https://github.com/dkdan10/AiLibi/pull/361) |
| `C-104` | Tests pinned retired settings, with names and docstrings saying the opposite | 20.37 | [#391](https://github.com/dkdan10/AiLibi/pull/391) |
| `C-113` | Docstring, front door and committed data disagreed about one eval metric | 20.6 | [#353](https://github.com/dkdan10/AiLibi/pull/353) |
| `C-125` | CONTRIBUTING overstated the gate; the README overstated the enforcement | 20.9 | [#352](https://github.com/dkdan10/AiLibi/pull/352) |
| `C-126` | Operator environment knobs were documented nowhere | 20.5 | [#351](https://github.com/dkdan10/AiLibi/pull/351) |
| `C-129` | The live prompt set said "a hidden impostor" in every two-impostor game | 20.31 | [#383](https://github.com/dkdan10/AiLibi/pull/383) |
| `C-130` | Dead prompt-set weight, and a default set no committed replay used | 20.5 | [#351](https://github.com/dkdan10/AiLibi/pull/351) |
| `G-1` | Nothing in memory said where the agent itself had been | 20.24 | [#376](https://github.com/dkdan10/AiLibi/pull/376) |
| `G-2` | The one channel that decides meetings was anti-informative and labelled verified | 20.26 | [#378](https://github.com/dkdan10/AiLibi/pull/378) |
| `G-3` | Redistribution minted false first-hand completion memories | 20.23 | [#375](https://github.com/dkdan10/AiLibi/pull/375) |
| `G-9` | Movement lines were read as sightings in the room the agent had left | 20.25 | [#377](https://github.com/dkdan10/AiLibi/pull/377) |
| `G-12` | The impostor policy stalked ejected players and declined free kills | 20.32 | [#373](https://github.com/dkdan10/AiLibi/pull/373) |
| `G-23` | The prompt mandated re-litigating a vent whose subject was already ejected | 20.31 | [#383](https://github.com/dkdan10/AiLibi/pull/383) |
| `G-25` | Development markers inside quoted dialogue reached other agents' prompts | 20.28 | [#380](https://github.com/dkdan10/AiLibi/pull/380) |
| `G-27` | Every two-impostor meeting was told there was "a hidden impostor", singular | 20.31 | [#383](https://github.com/dkdan10/AiLibi/pull/383) |
| `G-29` | Threshold arithmetic and stock rationales came out of the characters' mouths | 20.31 | [#383](https://github.com/dkdan10/AiLibi/pull/383) |
| `G-34` | The memory render was two-thirds co-presence noise and duplicates | 20.30 | [#382](https://github.com/dkdan10/AiLibi/pull/382) |
| `G-35` | Testimony was absorbed as unverified stubs and meeting outcomes never recorded | 20.29 | [#381](https://github.com/dkdan10/AiLibi/pull/381) |
| `G-37` | Agent tick stamps run +1 against the replay timeline | 20.2 | [#360](https://github.com/dkdan10/AiLibi/pull/360) |
| `G-38` | The spectator misrepresented four action classes and never cleared bodies | 20.16 | [#370](https://github.com/dkdan10/AiLibi/pull/370) |
| `G-41` | Internal jargon and task numbers were on the product surface | 20.2 | [#360](https://github.com/dkdan10/AiLibi/pull/360) |

Two rows want a qualification, and it is better stated than glossed. `G-37` was *labelled*
rather than changed — the clock convention is documented on the spectator surface, because
changing it would move every recorded tick stamp
([`../audit-phase-20-planning.md`](../audit-phase-20-planning.md) §5). `C-88` was *disclosed*:
the front door now explains why a run against the offline provider ejects nobody and reports
null rates, and hands the reader a real report instead. Both are the whole response the
finding was ruled to need. Findings a task only *began* answering are not in this table at
all — they are in §4 below, because a map that calls a first brick a closed wall is the exact
overstatement this index exists to police.

---

## 4. What was not closed, and where that is recorded

Everything the review raised that the map above does not carry: the classes ruled out of this
phase, the ones a task only began, and the ones its own verifier withdrew. None of them is
re-argued here; each points at the ruling or the record that owns it.

- **The balance wave** — post-meeting position and cooldown reset (`G-5`), finished-crew idle
  jobs (`G-15`), the vent peek (`G-13`), a speakable witnessed kill (`G-8`), a symmetric
  roll-call (`G-22`), sabotage as a real clock (`G-40`), and a second act for the small roster.
  Chartered as its own wave with its own recording, because every one of them changes the game
  rather than its honesty ([`../audit-phase-20-planning.md`](../audit-phase-20-planning.md) §7).
- **Begun, not finished.** Four structural findings had one symptom addressed and the finding
  left standing, so none of them is in the map above. `C-79` (the app shell is a God module
  contradicting its own no-edit header) saw its focus-trap and layout defects fixed while the
  shell itself is still roughly 1,200 lines. `C-80` (the frontend derivation layer is
  half-built, which is why `C-7` went unnoticed) had its first derivation extracted and
  tested — the task that did it calls that the first brick and says so. `C-101` (frontend
  coverage an order of magnitude behind Python, by configuration) gained the first
  component-level render test. `C-107` (no test-infrastructure layer) gained the first
  session-scoped fixture, behind a parallel runner. Each remains open at its own scope.
- **Cited as context, not closed** — `C-36` (the tick-and-meeting loop hand-rolled at eight
  sites) is cited for the agent-clock seam it explains rather than for its own decomposition,
  and `C-72` (half the belief model never reaches production) was graded UNDERMINED and needed
  no front-door repair, because the claim it undermined had already been removed. Both stay in
  the tail.
- **The refuted items** — `G-6`, `G-7`'s headline, `G-4`'s vent half and `C-33`'s load-bearing
  risk are in §1 above. Nothing was built for a claim its own verifier withdrew.
- **The decomposition refusals** — the God-module split (`C-62`) and the forked option
  enumerator (`C-33`, answered with a parity paragraph and a mask-parity test instead of a
  merge). Both are backlog, with reasons
  ([`../audit-phase-20-planning.md`](../audit-phase-20-planning.md) §7).
- **The history rewrite** — untracking the regenerable report JSONs and rewriting git history
  to shrink the pack (`C-45`) needs a build step the demo bundle and CI would both have to
  grow; recorded, not done (§5 item 6 and §7 of the same audit).
- **The remaining tail** — roughly 94 P2 code findings, the walker consolidation's flag matrix
  (`C-37`), the text-hygiene remainder (`G-26`, `G-36`, `G-29` beyond the prompt change), and
  the agent-clock convention itself, which was labelled rather than changed (`G-37`, above).
  Triaged and listed in §7; the phase's divergences from the review's own roadmap, with
  reasons, are in §5 of the same audit.

---

## 5. Errata

**2026-08-26.** One of the review's own corrections over-reached, and it is corrected here
rather than in the report that made it. The synthesis's verified re-check of `C-113` recorded
that the README "never mentions the metric", and refuted that leg of the finding on that
ground. The identifier does indeed appear nowhere in `README.md` — but the metric is named in
prose there, in the paragraph explaining why a fake-provider run produces an empty report
(`README.md:199` as of this date). The finding's README leg is still refuted, on the narrower
and true ground that no structural claim about the metric ever reached the front door: the
front page reports the measured value, it never sold it as a guarantee.
